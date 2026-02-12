import os


def upsert_risk_score(customer_id: int, risk_score: float) -> None:
    try:
        import boto3
    except ImportError as exc:
        raise SystemExit("boto3 not installed. Run: pip install boto3") from exc

    table_name = os.getenv("DYNAMODB_TABLE", "risk_scores")
    client = boto3.resource("dynamodb", region_name=os.getenv("AWS_REGION", "us-east-1"))
    table = client.Table(table_name)
    table.put_item(Item={"customer_id": customer_id, "risk_score": risk_score})


if __name__ == "__main__":
    upsert_risk_score(100045, 82.0)
