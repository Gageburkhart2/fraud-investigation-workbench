import random
from datetime import datetime, timedelta
import pandas as pd

random.seed(42)
start = datetime(2026, 9, 1)
rows = []

# Normal activity: 200 cards, ~5000 transactions over 30 days
for _ in range(5000):
    rows.append({
        "txn_id": f"T{len(rows):06d}",
        "card_id": f"C{random.randint(1, 200):04d}",
        "timestamp": start + timedelta(minutes=random.randint(0, 30 * 24 * 60)),
        "amount": round(random.lognormvariate(3.2, 0.9), 2),
        "merchant_category": random.choice(["grocery", "fuel", "dining", "retail", "online"]),
        "is_fraud": 0,
        "pattern": "none",
    })

# Fraud pattern: card testing (bursts of tiny online charges)
for card in random.sample(range(1, 201), 8):
    burst_start = start + timedelta(minutes=random.randint(0, 29 * 24 * 60))
    for i in range(random.randint(12, 25)):
        rows.append({
            "txn_id": f"T{len(rows):06d}",
            "card_id": f"C{card:04d}",
            "timestamp": burst_start + timedelta(seconds=random.randint(0, 600)),
            "amount": round(random.uniform(0.5, 2.0), 2),
            "merchant_category": "online",
            "is_fraud": 1,
            "pattern": "card_testing",
        })

df = pd.DataFrame(rows).sort_values("timestamp")
df.to_csv("data/transactions.csv", index=False)
print(df.shape, df["is_fraud"].sum(), "fraud rows")