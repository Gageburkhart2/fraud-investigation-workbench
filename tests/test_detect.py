import os
import csv
import subprocess
import sys
from datetime import datetime

def _load_flagged(flagged_path):
    with open(flagged_path, newline="") as f:
        reader = csv.DictReader(f)
        return [row for row in reader]

def test_detection_simple_burst(tmp_path):
    # Create a tiny CSV with a known burst of 5 small online transactions for one card
    transactions_path = tmp_path / "transactions.csv"
    fieldnames = ["txn_id","card_id","timestamp","amount","merchant_category","is_fraud","pattern"]
    rows = []
    base_time = datetime(2026, 9, 1, 12, 0, 0)
    for i in range(5):
        rows.append({
            "txn_id": f"T{i:06d}",
            "card_id": "C0001",
            "timestamp": (base_time.replace(minute=base_time.minute + i)).isoformat(),
            "amount": 1.0,
            "merchant_category": "online",
            "is_fraud": 1,
            "pattern": "card_testing",
        })
    with open(transactions_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    # Run detection
    flagged_path = tmp_path / "flagged.csv"
    subprocess.run([sys.executable, "src/detect_rules.py", "--transactions", str(transactions_path), "--flagged", str(flagged_path)], check=True)
    flagged = _load_flagged(flagged_path)
    assert len(flagged) == 5

def test_detection_no_burst(tmp_path):
    # Same as above but only 4 transactions (should not flag)
    transactions_path = tmp_path / "transactions.csv"
    fieldnames = ["txn_id","card_id","timestamp","amount","merchant_category","is_fraud","pattern"]
    rows = []
    base_time = datetime(2026, 9, 1, 12, 0, 0)
    for i in range(4):
        rows.append({
            "txn_id": f"T{i:06d}",
            "card_id": "C0002",
            "timestamp": (base_time.replace(minute=base_time.minute + i)).isoformat(),
            "amount": 1.0,
            "merchant_category": "online",
            "is_fraud": 1,
            "pattern": "card_testing",
        })
    with open(transactions_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    flagged_path = tmp_path / "flagged.csv"
    subprocess.run([sys.executable, "src/detect_rules.py", "--transactions", str(transactions_path), "--flagged", str(flagged_path)], check=True)
    flagged = _load_flagged(flagged_path)
    assert len(flagged) == 0
