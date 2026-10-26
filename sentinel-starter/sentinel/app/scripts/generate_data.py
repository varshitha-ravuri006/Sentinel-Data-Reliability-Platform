"""Generate a CSV with a known number of corrupted rows, for testing/demo."""
import csv
import os
import random
import sys

from faker import Faker

fake = Faker()


def generate(path: str, n: int = 200, corrupt_ratio: float = 0.2) -> int:
    rows = []
    for i in range(n):
        rows.append({
            "order_id": str(i + 1),
            "customer_id": f"C{random.randint(1, 60)}",
            "amount": str(random.randint(1, 500)),
            "status": random.choice(["pending", "paid", "shipped", "cancelled"]),
            "order_date": fake.date(),
        })

    # corrupt exactly n_bad distinct rows, one field each
    n_bad = int(n * corrupt_ratio)
    for row in random.sample(rows, n_bad):
        field = random.choice(["customer_id", "amount", "status"])
        if field == "customer_id":
            row["customer_id"] = ""
        elif field == "amount":
            row["amount"] = str(-random.randint(1, 50))
        else:
            row["status"] = "unknown"

    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    print(f"Wrote {n} rows to {path} ({n_bad} corrupted)")
    return n_bad


if __name__ == "__main__":
    default = os.path.join(os.path.dirname(__file__), "sample.csv")
    generate(sys.argv[1] if len(sys.argv) > 1 else default)