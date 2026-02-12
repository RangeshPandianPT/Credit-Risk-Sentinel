import os


def consume_events() -> None:
    try:
        from kafka import KafkaConsumer
    except ImportError as exc:
        raise SystemExit("kafka-python is not installed. Run: pip install kafka-python") from exc

    brokers = os.getenv("KAFKA_BROKERS", "localhost:9092")
    topic = os.getenv("KAFKA_TOPIC", "risk-events")

    consumer = KafkaConsumer(
        topic,
        bootstrap_servers=brokers.split(","),
        auto_offset_reset="latest",
        enable_auto_commit=True,
    )

    for message in consumer:
        print(message.value)


if __name__ == "__main__":
    consume_events()
