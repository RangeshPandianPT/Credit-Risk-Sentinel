from datetime import timedelta

try:
    from feast import Entity, FeatureView, Field
    from feast.infra.offline_stores.file_source import FileSource
    from feast.types import Float32, Int64
except ImportError as exc:
    raise SystemExit("Feast is not installed. Run: pip install feast") from exc

customer = Entity(name="customer_id", join_keys=["SK_ID_CURR"])

behavioral_source = FileSource(
    path="phase1_behavioral_features.csv",
    timestamp_field=None,
)

behavioral_view = FeatureView(
    name="behavioral_features",
    entities=[customer],
    ttl=timedelta(days=365),
    schema=[
        Field(name="avg_days_past_due", dtype=Float32),
        Field(name="payment_consistency_score", dtype=Float32),
        Field(name="late_payment_trend", dtype=Float32),
        Field(name="SK_ID_CURR", dtype=Int64),
    ],
    online=True,
    source=behavioral_source,
)
