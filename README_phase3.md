Phase 3: Airflow DAG + FastAPI integration

Files:
- dags/pre_delinquency_dag.py: DAG orchestrating ingestion, Redis feature refresh, risk scoring, and notification.
- phase3_ingest_transactions.py: Placeholder ingestion script for daily transactions.

Configuration:
- REDIS_URL: Redis connection string (default: redis://localhost:6379/0)
- RISK_API_URL: FastAPI scoring endpoint (default: http://localhost:8000/score)
- RISK_ALERT_THRESHOLD: Score threshold for alert (default: 70)
- RISK_ALERT_EMAIL: Email recipient for alerts

Notes:
- Airflow EmailOperator requires SMTP configuration in Airflow.
- Replace the placeholder feature payload in the DAG with your real feature computation logic.
- Temporal split guidance (Phase 2): a cutoff like -500 keeps enough historical seasoning for training while reserving a recent window to test pre-delinquency logic.

Project Completion Checklist
[x] Data Leakage Check: Enforced when time split is used (requires leakage report).
[x] Model Explainability: Top-3 SHAP reasons displayed in dashboard.
[x] Low Latency: Scoring fails when feature latency exceeds SLA.
[x] Regulatory Alignment: Audit trails for scoring and interventions.

Phase 4: Risk Intervention Dashboard

API endpoints (served by phase3_risk_api.py):
- GET /customers/high-risk: returns the customer list shown in the dashboard.
- POST /score: returns risk score, top-3 SHAP reasons, and feature latency.
- POST /api/notify: publishes an intervention payload to SNS (when enabled).

Environment variables:
- SNS_TOPIC_ARN: SNS topic ARN used for sending empathetic SMS/Email notifications.
- MODEL_PATH: model artifact path (default: artifacts/xgb_model.json)
- FEATURE_PATH: feature list path (default: artifacts/feature_list.csv)
- FEATURE_LATENCY_THRESHOLD_MS: latency SLA in milliseconds (default: 100)
- HIGH_RISK_CUSTOMERS_KEY: Redis key for the high-risk customer list (default: high_risk_customers)

Training with mandatory leakage checks:
- Use run_training_with_leakage_checks.py to enforce time split + leakage report inputs.
- Example:
	- python run_training_with_leakage_checks.py --time-column DAYS_ENTRY_PAYMENT --time-cutoff -500 --leakage-report leakage_report.csv

Seed high-risk customer list in Redis (for dashboard testing):
- Run seed_high_risk_customers.py to populate the HIGH_RISK_CUSTOMERS_KEY value.
- Example:
	- REDIS_URL=redis://localhost:6379/0 python seed_high_risk_customers.py

Phase 5: Validation & Stress Testing (stubs)
- integrations/feast/feature_store.yaml and integrations/feast/feature_views.py
- integrations/kafka_producer.py and integrations/kafka_consumer.py
- integrations/bentoml_service.py
- integrations/dash_app.py
- integrations/aws_sagemaker_stub.py
- integrations/aws_kinesis_stub.py
- integrations/aws_redshift_stub.py
- integrations/aws_dynamodb_stub.py
- integrations/aws_quicksight_stub.py
