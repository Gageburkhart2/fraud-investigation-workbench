import os
import csv
from collections import defaultdict
from datetime import datetime

def main():
    # Ensure required directories exist
    os.makedirs("results", exist_ok=True)

    transactions_path = "data/transactions.csv"
    flagged_path = "data/flagged_transactions.csv"
    if not os.path.exists(transactions_path) or not os.path.exists(flagged_path):
        raise FileNotFoundError("Required CSV files not found. Run generate_transactions.py and detect_rules.py first.")

    # Load full transactions
    transactions = {}
    with open(transactions_path, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            row["timestamp"] = datetime.fromisoformat(row["timestamp"])
            row["amount"] = float(row["amount"])
            row["is_fraud"] = int(row["is_fraud"])
            transactions[row["txn_id"]] = row

    # Load flagged transactions
    flagged = []
    with open(flagged_path, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            row["timestamp"] = datetime.fromisoformat(row["timestamp"])
            row["amount"] = float(row["amount"])
            row["is_fraud"] = int(row["is_fraud"])
            flagged.append(row)

    # Group flagged rows by card
    by_card = defaultdict(list)
    for txn in flagged:
        by_card[txn["card_id"]].append(txn)

    summaries = []
    for card_id, txns in by_card.items():
        count = len(txns)
        first = min(t["timestamp"] for t in txns)
        last = max(t["timestamp"] for t in txns)
        total_amount = sum(t["amount"] for t in txns)
        summary = (
            f"Card {card_id} flagged with {count} suspicious transactions "
            f"between {first} and {last}, total amount ${total_amount:.2f}."
        )
        summaries.append(summary)

    out_path = os.path.join("results", "summaries.txt")
    with open(out_path, "w") as f:
        for s in summaries:
            f.write(s + "\n")
    print(f"Wrote {len(summaries)} summaries to {out_path}")

if __name__ == "__main__":
    main()
