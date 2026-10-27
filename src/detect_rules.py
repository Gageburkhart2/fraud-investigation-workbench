import csv
import os
from datetime import datetime, timedelta
from collections import defaultdict

# Ensure data directory exists
os.makedirs("data", exist_ok=True)

transactions_path = "data/transactions.csv"
flagged_path = "data/flagged_transactions.csv"

# Load transactions into a list of dicts, parsing timestamp
transactions = []
with open(transactions_path, newline="") as f:
    reader = csv.DictReader(f)
    for row in reader:
        # Parse fields
        row["timestamp"] = datetime.fromisoformat(row["timestamp"])
        row["amount"] = float(row["amount"])
        row["is_fraud"] = int(row["is_fraud"])
        transactions.append(row)

# Sort by card_id then timestamp
transactions.sort(key=lambda r: (r["card_id"], r["timestamp"]))

flagged_ids = set()
# Group by card_id
by_card = defaultdict(list)
for txn in transactions:
    by_card[txn["card_id"]].append(txn)

for card_id, txns in by_card.items():
    # Filter small online transactions
    small = [t for t in txns if t["amount"] <= 3.0 and t["merchant_category"] == "online"]
    times = [t["timestamp"] for t in small]
    ids = [t["txn_id"] for t in small]
    start = 0
    for end in range(len(times)):
        while times[end] - times[start] > timedelta(minutes=10):
            start += 1
        if end - start + 1 >= 5:
            flagged_ids.update(ids[start:end + 1])

# Add flagged column to each transaction dict
for txn in transactions:
    txn["flagged"] = 1 if txn["txn_id"] in flagged_ids else 0

# Compute metrics
tp = sum(1 for t in transactions if t["flagged"] == 1 and t["is_fraud"] == 1)
fp = sum(1 for t in transactions if t["flagged"] == 1 and t["is_fraud"] == 0)
fn = sum(1 for t in transactions if t["flagged"] == 0 and t["is_fraud"] == 1)
precision = tp / (tp + fp) if (tp + fp) else 0
recall = tp / (tp + fn) if (tp + fn) else 0

# Write flagged transactions CSV (only flagged rows)
with open(flagged_path, "w", newline="") as f:
    fieldnames = ["txn_id","card_id","timestamp","amount","merchant_category","is_fraud","pattern","flagged"]
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    for txn in transactions:
        if txn["flagged"] == 1:
            # Convert timestamp back to ISO string for CSV
            txn_copy = txn.copy()
            txn_copy["timestamp"] = txn_copy["timestamp"].isoformat()
            writer.writerow(txn_copy)

print(f"Flagged: {len(flagged_ids)} | TP: {tp} FP: {fp} FN: {fn}")
print(f"Precision: {precision:.3f}  Recall: {recall:.3f}")
