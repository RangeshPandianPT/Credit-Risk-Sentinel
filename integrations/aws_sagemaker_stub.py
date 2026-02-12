import os


def start_training_job() -> None:
    try:
        import boto3
    except ImportError as exc:
        raise SystemExit("boto3 not installed. Run: pip install boto3") from exc

    client = boto3.client("sagemaker", region_name=os.getenv("AWS_REGION", "us-east-1"))
    print("Stub: call client.create_training_job with your config")
    print(client)


def create_endpoint() -> None:
    try:
        import boto3
    except ImportError as exc:
        raise SystemExit("boto3 not installed. Run: pip install boto3") from exc

    client = boto3.client("sagemaker", region_name=os.getenv("AWS_REGION", "us-east-1"))
    print("Stub: call client.create_endpoint with your config")
    print(client)


if __name__ == "__main__":
    start_training_job()
