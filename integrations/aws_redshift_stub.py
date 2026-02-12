import os


def load_scores() -> None:
    try:
        import psycopg2
    except ImportError as exc:
        raise SystemExit("psycopg2 not installed. Run: pip install psycopg2-binary") from exc

    conn = psycopg2.connect(
        host=os.getenv("REDSHIFT_HOST"),
        port=int(os.getenv("REDSHIFT_PORT", "5439")),
        dbname=os.getenv("REDSHIFT_DB"),
        user=os.getenv("REDSHIFT_USER"),
        password=os.getenv("REDSHIFT_PASSWORD"),
    )
    print("Stub: bulk load risk scores into Redshift")
    conn.close()


if __name__ == "__main__":
    load_scores()
