import argparse
import json
import os
import sys
from pathlib import Path
from typing import Dict, List

import redis
import requests


TEMPLATES = {
    "salary_delay": {
        "title": "Offer a payment holiday",
        "message": (
            "Hi {name}, we noticed a change in your salary timing. "
            "If it helps, we can offer a short payment holiday or a revised due date. "
            "Reply YES to explore options."
        ),
    },
    "utilization_spike": {
        "title": "Spending support plan",
        "message": (
            "Hi {name}, it looks like your card usage has risen recently. "
            "We can help with a flexible payment plan or budgeting tips. "
            "Reply YES for support."
        ),
    },
}


def load_feature_list(path: Path) -> List[str]:
    data = path.read_text(encoding="utf-8").splitlines()
    if not data:
        raise ValueError("feature list file is empty")
    header = data[0].split(",")
    if header[0].strip().lower() == "feature":
        return [line.split(",")[0].strip() for line in data[1:] if line.strip()]
    return [line.split(",")[0].strip() for line in data if line.strip()]


def set_if_present(payload: Dict[str, float], name: str, value: float) -> None:
    if name in payload:
        payload[name] = float(value)


def build_baseline(features: List[str]) -> Dict[str, float]:
    payload = {name: 0.0 for name in features}
    set_if_present(payload, "avg_days_past_due", 0.5)
    set_if_present(payload, "payment_consistency_score", 0.1)
    set_if_present(payload, "late_payment_trend", 0.01)
    set_if_present(payload, "AMT_INCOME_TOTAL", 60000)
    set_if_present(payload, "AMT_CREDIT", 50000)
    set_if_present(payload, "AMT_ANNUITY", 2500)
    return payload


def build_stressed(
    baseline: Dict[str, float], stress_factor: str
) -> Dict[str, float]:
    payload = dict(baseline)

    if stress_factor == "salary_delay":
        set_if_present(payload, "avg_days_past_due", 12)
        set_if_present(payload, "payment_consistency_score", 1.4)
        set_if_present(payload, "late_payment_trend", 0.25)
    elif stress_factor == "utilization_spike":
        set_if_present(payload, "AMT_CREDIT", 90000)
        set_if_present(payload, "AMT_GOODS_PRICE", 95000)
        set_if_present(payload, "AMT_ANNUITY", 4200)
        set_if_present(payload, "AMT_BALANCE", 18000)
        set_if_present(payload, "AMT_PAYMENT", 1500)
        set_if_present(payload, "payment_consistency_score", 0.4)
    else:
        raise ValueError(f"Unsupported stress factor: {stress_factor}")

    return payload


def write_features(redis_client: redis.Redis, customer_id: int, payload: Dict[str, float]) -> None:
    key = f"features:{customer_id}"
    redis_client.set(key, json.dumps(payload))


def request_score(api_url: str, customer_id: int) -> Dict[str, object]:
    response = requests.post(
        f"{api_url}/score",
        json={"customer_id": customer_id},
        timeout=30,
    )
    response.raise_for_status()
    return response.json()


def request_notify(api_url: str, payload: Dict[str, object]) -> Dict[str, object]:
    response = requests.post(
        f"{api_url}/api/notify",
        json=payload,
        timeout=30,
    )
    response.raise_for_status()
    return response.json()


def main() -> int:
    parser = argparse.ArgumentParser(description="Phase 5 scenario runner")
    parser.add_argument("--api-url", default=os.getenv("RISK_API_URL", "http://localhost:8000"))
    parser.add_argument("--redis-url", default=os.getenv("REDIS_URL", "redis://localhost:6379/0"))
    parser.add_argument("--feature-path", default=os.getenv("FEATURE_PATH", "artifacts/feature_list.csv"))
    parser.add_argument("--customer-id", type=int, default=900001)
    parser.add_argument(
        "--stress-factor",
        choices=sorted(TEMPLATES.keys()),
        default="salary_delay",
    )
    parser.add_argument("--customer-name", default="Test Customer")
    parser.add_argument("--skip-notify", action="store_true")
    args = parser.parse_args()

    feature_path = Path(args.feature_path)
    if not feature_path.exists():
        print(f"Feature list not found: {feature_path}")
        return 2

    features = load_feature_list(feature_path)
    baseline = build_baseline(features)
    stressed = build_stressed(baseline, args.stress_factor)

    redis_client = redis.Redis.from_url(args.redis_url)

    write_features(redis_client, args.customer_id, baseline)
    baseline_score = request_score(args.api_url, args.customer_id)

    write_features(redis_client, args.customer_id, stressed)
    stressed_score = request_score(args.api_url, args.customer_id)

    base_value = float(baseline_score.get("risk_score", 0))
    stressed_value = float(stressed_score.get("risk_score", 0))

    print("Baseline score:", base_value)
    print("Stressed score:", stressed_value)

    if stressed_value <= base_value:
        print("Warning: stressed score did not increase. Review feature injection or model.")
    else:
        print("OK: stressed score increased.")

    template = TEMPLATES[args.stress_factor]
    notify_payload = {
        "customerId": args.customer_id,
        "channel": "sms_email",
        "templateTitle": template["title"],
        "message": template["message"].replace("{name}", args.customer_name),
        "stressFactor": args.stress_factor,
        "riskScore": stressed_value,
        "reasons": [item["feature"] for item in stressed_score.get("reasons", [])],
    }

    if args.skip_notify:
        print("Notify skipped. Payload:")
        print(json.dumps(notify_payload, indent=2))
        return 0

    notify_result = request_notify(args.api_url, notify_payload)
    print("Notify status:", notify_result.get("status", "unknown"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
