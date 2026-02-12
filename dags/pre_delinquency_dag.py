from __future__ import annotations

from datetime import datetime, timedelta
import json
import os
from pathlib import Path
import time
from typing import Any, Dict

import requests
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator, ShortCircuitOperator
from airflow.operators.email import EmailOperator
from airflow.utils.trigger_rule import TriggerRule


def log_audit_event(event_type: str, payload: Dict[str, Any]) -> None:
    audit_dir = Path("d:/SpaceBar/logs")
    audit_dir.mkdir(parents=True, exist_ok=True)
    audit_path = audit_dir / "audit_trail.jsonl"
    record = {
        "event_type": event_type,
        "timestamp_utc": datetime.utcnow().isoformat(),
        "payload": payload,
    }
    with audit_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record) + "\n")


def update_redis_features(**context: Dict[str, Any]) -> None:
    import redis

    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    redis_client = redis.Redis.from_url(redis_url)

    # Example feature payload. Replace with real computed features.
    features = {
        "customer_id": 100001,
        "avg_days_past_due": 2.3,
        "payment_consistency_score": 0.42,
        "late_payment_trend": 0.08,
    }

    key = f"features:{features['customer_id']}"
    redis_client.set(key, json.dumps(features))

    log_audit_event("feature_update", {"key": key, "features": features})


def check_feature_latency(**context: Dict[str, Any]) -> None:
    import redis

    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    redis_client = redis.Redis.from_url(redis_url)
    key = os.getenv("LATENCY_CHECK_KEY", "features:100001")
    threshold_ms = float(os.getenv("FEATURE_LATENCY_THRESHOLD_MS", "100"))

    start = time.perf_counter()
    _ = redis_client.get(key)
    elapsed_ms = (time.perf_counter() - start) * 1000

    log_audit_event(
        "feature_latency",
        {"key": key, "latency_ms": round(elapsed_ms, 2), "threshold_ms": threshold_ms},
    )

    if elapsed_ms > threshold_ms:
        raise ValueError(f"Feature store latency {elapsed_ms:.2f}ms exceeds {threshold_ms}ms")


def call_risk_api(**context: Dict[str, Any]) -> float:
    api_url = os.getenv("RISK_API_URL", "http://localhost:8000/score")
    payload = {"customer_id": 100001}

    response = requests.post(api_url, json=payload, timeout=30)
    response.raise_for_status()

    data = response.json()
    risk_score = float(data.get("risk_score", 0))
    context["ti"].xcom_push(key="risk_score", value=risk_score)

    log_audit_event("risk_score", data)
    return risk_score


def should_notify(**context: Dict[str, Any]) -> bool:
    threshold = float(os.getenv("RISK_ALERT_THRESHOLD", "70"))
    risk_score = float(context["ti"].xcom_pull(key="risk_score"))
    return risk_score >= threshold


DEFAULT_ARGS = {
    "owner": "airflow",
    "depends_on_past": False,
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
}


with DAG(
    dag_id="pre_delinquency_intervention",
    default_args=DEFAULT_ARGS,
    description="Daily ingestion, feature refresh, and risk scoring",
    schedule="0 2 * * *",
    start_date=datetime(2025, 1, 1),
    catchup=False,
    tags=["risk", "home_credit"],
) as dag:
    ingest_transactions = BashOperator(
        task_id="ingest_transactions",
        bash_command="python d:/SpaceBar/phase3_ingest_transactions.py",
    )

    update_features = PythonOperator(
        task_id="update_feature_store",
        python_callable=update_redis_features,
    )

    check_latency = PythonOperator(
        task_id="check_feature_latency",
        python_callable=check_feature_latency,
    )

    score_risk = PythonOperator(
        task_id="score_risk",
        python_callable=call_risk_api,
    )

    latency_alert = EmailOperator(
        task_id="send_latency_alert",
        to=os.getenv("RISK_ALERT_EMAIL", "risk-alerts@example.com"),
        subject="Feature Store Latency SLA Breach",
        html_content="Feature retrieval exceeded the 100ms SLA. Investigate Redis and network.",
        trigger_rule=TriggerRule.ONE_FAILED,
    )

    notify_gate = ShortCircuitOperator(
        task_id="notify_if_high_risk",
        python_callable=should_notify,
    )

    send_email = EmailOperator(
        task_id="send_high_risk_email",
        to=os.getenv("RISK_ALERT_EMAIL", "risk-alerts@example.com"),
        subject="High Risk Account Detected",
        html_content="A high risk score was detected. Check the dashboard for details.",
    )

    ingest_transactions >> update_features >> check_latency
    check_latency >> latency_alert
    check_latency >> score_risk >> notify_gate >> send_email
