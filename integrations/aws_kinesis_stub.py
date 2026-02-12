import json
import os


def put_record(payload: dict) -> None:
    try:
        import boto3
    except ImportError as exc:
        raise SystemExit("boto3 not installed. Run: pip install boto3") from exc

    stream = os.getenv("KINESIS_STREAM", "risk-transactions")
    client = boto3.client("kinesis", region_name=os.getenv("AWS_REGION", "us-east-1"))
    client.put_record(
        StreamName=stream,
        Data=json.dumps(payload).encode("utf-8"),
        PartitionKey=str(payload.get("customer_id", "0")),
    )


if __name__ == "__main__":
    put_record({"customer_id": 100045, "event": "stress_spike"})
