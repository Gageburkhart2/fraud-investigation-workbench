import os
import json
import subprocess
import sys
from unittest import mock

def test_summarize_fallback(tmp_path):
    # Prepare a minimal flagged CSV with one card
    flagged_path = tmp_path / "flagged.csv"
    fieldnames = ["txn_id","card_id","timestamp","amount","merchant_category","is_fraud","pattern","flagged"]
    rows = [{
        "txn_id": "T000001",
        "card_id": "C0001",
        "timestamp": "2026-09-01T12:00:00",
        "amount": "1.00",
        "merchant_category": "online",
        "is_fraud": "1",
        "pattern": "card_testing",
        "flagged": "1",
    }]
    with open(flagged_path, "w", newline="") as f:
        writer = __import__("csv").DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    # Mock requests.post to raise ConnectionError
    with mock.patch("requests.post", side_effect=Exception("Ollama not reachable")):
        out_path = tmp_path / "summaries.jsonl"
        subprocess.run([
            sys.executable,
            "src/summarize_cases.py",
            "--flagged",
            str(flagged_path),
            "--output",
            str(out_path),
        ], check=True)
    # Verify fallback summary was written
    with open(out_path) as f:
        lines = f.readlines()
    assert len(lines) == 1
    obj = json.loads(lines[0])
    assert "summary" in obj
    assert "Card C0001" in obj["summary"]
