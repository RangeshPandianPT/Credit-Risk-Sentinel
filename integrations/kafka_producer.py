import json
import os
from typing import Dict


def publish_event(event: Dict[str, object]) -> None:
    try:
        from kafka import KafkaProducer
    except ImportError as exc:
        raise SystemExit("kafka-python is not installed. Run: pip install kafka-python") from exc

    brokers = os.getenv("KAFKA_BROKERS", "localhost:9092")
    topic = os.getenv("KAFKA_TOPIC", "risk-events")

    producer = KafkaProducer(
        bootstrap_servers=brokers.split(","),
        value_serializer=lambda v: json.dumps(v).encode("utf-8"),
    )
    producer.send(topic, event)
    producer.flush()


if __name__ == "__main__":
    publish_event({"event": "risk_score", "customer_id": 100045, "score": 82})
