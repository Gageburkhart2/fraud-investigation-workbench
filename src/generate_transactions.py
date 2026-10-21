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

# Legitimate small online purchases (noise) drawn from same card pool
for card in random.sample(range(1, 201), 25):
    legit_start = start + timedelta(minutes=random.randint(0, 29 * 24 * 60))
    for _ in range(random.randint(3, 7)):
        rows.append({
            "txn_id": f"T{len(rows):06d}",
            "card_id": f"C{card:04d}",
            "timestamp": legit_start + timedelta(seconds=random.randint(0, 900)),
            "amount": round(random.uniform(0.99, 2.99), 2),
            "merchant_category": "online",
            "is_fraud": 0,
            "pattern": "legit_small_online",
        })

# Fraud pattern: card testing (bursts of tiny online charges)
# More cards, burst sizes 4-25, spread up to 20 minutes
for card in random.sample(range(1, 201), 15):
    burst_start = start + timedelta(minutes=random.randint(0, 29 * 24 * 60))
    for i in range(random.randint(4, 25)):
        rows.append({
            "txn_id": f"T{len(rows):06d}",
            "card_id": f"C{card:04d}",
            "timestamp": burst_start + timedelta(seconds=random.randint(0, 1200)),
            "amount": round(random.uniform(0.5, 2.99), 2),
            "merchant_category": "online",
            "is_fraud": 1,
            "pattern": "card_testing",
        })

# Some cards have both legit small online bursts and fraud testing bursts
combined_cards = random.sample(range(1, 201), random.randint(3, 5))
for card in combined_cards:
    # legit small online burst
    legit_start = start + timedelta(minutes=random.randint(0, 29 * 24 * 60))
    for _ in range(random.randint(3, 7)):
        rows.append({
            "txn_id": f"T{len(rows):06d}",
            "card_id": f"C{card:04d}",
            "timestamp": legit_start + timedelta(seconds=random.randint(0, 900)),
            "amount": round(random.uniform(0.99, 2.99), 2),
            "merchant_category": "online",
            "is_fraud": 0,
            "pattern": "legit_small_online",
        })
    # fraud testing burst (different time)
    fraud_start = start + timedelta(minutes=random.randint(0, 29 * 24 * 60))
    for i in range(random.randint(4, 25)):
        rows.append({
            "txn_id": f"T{len(rows):06d}",
            "card_id": f"C{card:04d}",
            "timestamp": fraud_start + timedelta(seconds=random.randint(0, 1200)),
            "amount": round(random.uniform(0.5, 2.99), 2),
            "merchant_category": "online",
            "is_fraud": 1,
            "pattern": "card_testing",
        })

df = pd.DataFrame(rows).sort_values("timestamp")
df.to_csv("data/transactions.csv", index=False)
print(df.shape, df["is_fraud"].sum(), "fraud rows")