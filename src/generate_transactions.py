import os
import random
import argparse
from datetime import datetime, timedelta
import csv

def generate_transactions(output_path="data/transactions.csv", seed=42):
    # Ensure the data directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    random.seed(seed)
    start = datetime(2026, 9, 1)
    rows = []

    # Normal activity: 200 cards, ~5000 transactions over 30 days
    for _ in range(5000):
        rows.append({
            "txn_id": f"T{len(rows):06d}",
            "card_id": f"C{random.randint(1, 200):04d}",
            "timestamp": (start + timedelta(minutes=random.randint(0, 30 * 24 * 60))).isoformat(),
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
                "timestamp": (legit_start + timedelta(seconds=random.randint(0, 900))).isoformat(),
                "amount": round(random.uniform(0.99, 2.99), 2),
                "merchant_category": "online",
                "is_fraud": 0,
                "pattern": "legit_small_online",
            })

    # Fraud pattern: card testing (bursts of tiny online charges)
    for card in random.sample(range(1, 201), 15):
        burst_start = start + timedelta(minutes=random.randint(0, 29 * 24 * 60))
        for i in range(random.randint(4, 25)):
            rows.append({
                "txn_id": f"T{len(rows):06d}",
                "card_id": f"C{card:04d}",
                "timestamp": (burst_start + timedelta(seconds=random.randint(0, 1200))).isoformat(),
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
                "timestamp": (legit_start + timedelta(seconds=random.randint(0, 900))).isoformat(),
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
                "timestamp": (fraud_start + timedelta(seconds=random.randint(0, 1200))).isoformat(),
                "amount": round(random.uniform(0.5, 2.99), 2),
                "merchant_category": "online",
                "is_fraud": 1,
                "pattern": "card_testing",
            })

    # Write to CSV
    with open(output_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["txn_id","card_id","timestamp","amount","merchant_category","is_fraud","pattern"])
        writer.writeheader()
        writer.writerows(rows)
    print(f"Generated {len(rows)} transactions, {sum(r['is_fraud'] for r in rows)} fraud rows with seed {seed}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate synthetic transaction data")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for reproducibility")
    parser.add_argument("--output", type=str, default="data/transactions.csv", help="Path to write transactions CSV")
    args = parser.parse_args()
    generate_transactions(output_path=args.output, seed=args.seed)
