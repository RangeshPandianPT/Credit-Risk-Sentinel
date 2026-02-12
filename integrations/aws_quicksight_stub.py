import os


def create_dataset() -> None:
    try:
        import boto3
    except ImportError as exc:
        raise SystemExit("boto3 not installed. Run: pip install boto3") from exc

    account_id = os.getenv("AWS_ACCOUNT_ID", "")
    region = os.getenv("AWS_REGION", "us-east-1")
    client = boto3.client("quicksight", region_name=region)
    print("Stub: call create_data_source/create_data_set for QuickSight")
    print(f"Account: {account_id}")
    print(client)


if __name__ == "__main__":
    create_dataset()
