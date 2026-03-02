import json
import os
from typing import List, Dict

import redis


DEFAULT_CUSTOMERS: List[Dict[str, object]] = [
    {
        "id": 100045,
        "name": "Alicia W.",
        "riskScore": 82,
        "stressFactor": "salary_delay",
        "reasons": ["Salary drift", "Late payment trend", "Rising DPD"],
        "trend": [
            {"month": "Sep", "stress": 38},
            {"month": "Oct", "stress": 42},
            {"month": "Nov", "stress": 50},
            {"month": "Dec", "stress": 58},
            {"month": "Jan", "stress": 64},
            {"month": "Feb", "stress": 72},
        ],
    },
    {
        "id": 100112,
        "name": "Jordan K.",
        "riskScore": 76,
        "stressFactor": "utilization_spike",
        "reasons": ["Utilization spike", "High balance variance", "Cash advance uptick"],
        "trend": [
            {"month": "Sep", "stress": 30},
            {"month": "Oct", "stress": 36},
            {"month": "Nov", "stress": 44},
            {"month": "Dec", "stress": 53},
            {"month": "Jan", "stress": 57},
            {"month": "Feb", "stress": 61},
        ],
    },
    {
        "id": 100231,
        "name": "Priya S.",
        "riskScore": 69,
        "stressFactor": "payment_irregularity",
        "reasons": ["Payment inconsistency", "Recent DPD", "Short-term volatility"],
        "trend": [
            {"month": "Sep", "stress": 22},
            {"month": "Oct", "stress": 24},
            {"month": "Nov", "stress": 31},
            {"month": "Dec", "stress": 40},
            {"month": "Jan", "stress": 46},
            {"month": "Feb", "stress": 52},
        ],
    },
]


def main() -> None:
    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    key = os.getenv("HIGH_RISK_CUSTOMERS_KEY", "high_risk_customers")

    client = redis.Redis.from_url(redis_url)
    client.set(key, json.dumps(DEFAULT_CUSTOMERS))
    print(f"Seeded {len(DEFAULT_CUSTOMERS)} customers into Redis key '{key}'.")


if __name__ == "__main__":
    main()
