import csv
import os
import json
from datetime import datetime, timedelta
from collections import defaultdict

def detect_transactions(transactions_path="data/transactions.csv", flagged_path="data/flagged_transactions.csv", metrics_path="results/metrics.json"):
    # Ensure directories exist
    os.makedirs(os.path.dirname(flagged_path), exist_ok=True)
    os.makedirs(os.path.dirname(metrics_path), exist_ok=True)

    # Load transactions
    transactions = []
    with open(transactions_path, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            row["timestamp"] = datetime.fromisoformat(row["timestamp"])
            row["amount"] = float(row["amount"])
            row["is_fraud"] = int(row["is_fraud"])
            transactions.append(row)

    # Sort
    transactions.sort(key=lambda r: (r["card_id"], r["timestamp"]))

    flagged_ids = set()
    by_card = defaultdict(list)
    for txn in transactions:
        by_card[txn["card_id"]].append(txn)

    # Detection rule
    for card_id, txns in by_card.items():
        small = [t for t in txns if t["amount"] <= 3.0 and t["merchant_category"] == "online"]
        times = [t["timestamp"] for t in small]
        ids = [t["txn_id"] for t in small]
        start = 0
        for end in range(len(times)):
            while times[end] - times[start] > timedelta(minutes=10):
                start += 1
            if end - start + 1 >= 5:
                flagged_ids.update(ids[start:end + 1])

    # Add flagged column
    for txn in transactions:
        txn["flagged"] = 1 if txn["txn_id"] in flagged_ids else 0

    # Transaction‑level metrics
    tp = sum(1 for t in transactions if t["flagged"] == 1 and t["is_fraud"] == 1)
    fp = sum(1 for t in transactions if t["flagged"] == 1 and t["is_fraud"] == 0)
    fn = sum(1 for t in transactions if t["flagged"] == 0 and t["is_fraud"] == 1)
    precision = tp / (tp + fp) if (tp + fp) else 0
    recall = tp / (tp + fn) if (tp + fn) else 0

    # Card‑level metrics
    fraud_cards = {c for c, txns in by_card.items() if any(t["is_fraud"] == 1 for t in txns)}
    detected_cards = {c for c, txns in by_card.items() if any(t["flagged"] == 1 for t in txns)}
    tp_card = len(fraud_cards & detected_cards)
    fn_card = len(fraud_cards - detected_cards)
    precision_card = tp_card / len(detected_cards) if detected_cards else 0
    recall_card = tp_card / len(fraud_cards) if fraud_cards else 0

    # Missed bursts analysis (simple heuristic)
    missed_bursts = []
    for card_id, txns in by_card.items():
        fraud_txns = [t for t in txns if t["is_fraud"] == 1]
        if fraud_txns and not any(t["flagged"] == 1 for t in fraud_txns):
            # If fewer than 5 fraud transactions, rule cannot trigger
            if len(fraud_txns) < 5:
                reason = "fewer than 5 fraud transactions"
            else:
                reason = "pattern not captured"
            missed_bursts.append({"card_id": card_id, "count": len(fraud_txns), "reason": reason})

    # Write flagged CSV
    with open(flagged_path, "w", newline="") as f:
        fieldnames = ["txn_id","card_id","timestamp","amount","merchant_category","is_fraud","pattern","flagged"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for txn in transactions:
            if txn["flagged"] == 1:
                txn_copy = txn.copy()
                txn_copy["timestamp"] = txn_copy["timestamp"].isoformat()
                writer.writerow(txn_copy)

    # Write metrics JSON
    metrics = {
        "transaction": {"precision": precision, "recall": recall, "tp": tp, "fp": fp, "fn": fn},
        "card": {"precision": precision_card, "recall": recall_card, "tp": tp_card, "fn": fn_card, "detected_cards": len(detected_cards), "fraud_cards": len(fraud_cards)},
        "missed_bursts": missed_bursts,
    }
    with open(metrics_path, "w") as f:
        json.dump(metrics, f, indent=2)

    print(f"Flagged: {len(flagged_ids)} | TP: {tp} FP: {fp} FN: {fn}")
    print(f"Precision: {precision:.3f}  Recall: {recall:.3f}")
    print(f"Card‑level precision: {precision_card:.3f}, recall: {recall_card:.3f}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Detect fraud in transaction CSV")
    parser.add_argument("--transactions", type=str, default="data/transactions.csv")
    parser.add_argument("--flagged", type=str, default="data/flagged_transactions.csv")
    parser.add_argument("--metrics", type=str, default="results/metrics.json")
    args = parser.parse_args()
    detect_transactions(transactions_path=args.transactions, flagged_path=args.flagged, metrics_path=args.metrics)
