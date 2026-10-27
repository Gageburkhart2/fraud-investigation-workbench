import os
import csv
import json
from datetime import datetime

def evaluate_summaries(flagged_path="data/flagged_transactions.csv", summaries_path="results/summaries.jsonl", metrics_path="results/metrics.json"):
    # Load flagged transactions per card
    flagged_by_card = {}
    with open(flagged_path, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            row["timestamp"] = datetime.fromisoformat(row["timestamp"])
            row["amount"] = float(row["amount"])
            flagged_by_card.setdefault(row["card_id"], []).append(row)

    # Load summaries
    total = 0
    passed = 0
    latencies = []
    for line in open(summaries_path):
        total += 1
        obj = json.loads(line)
        card_id = obj["card_id"]
        cited = set(obj.get("cited_ids", []))
        flagged = flagged_by_card.get(card_id, [])
        flagged_ids = {t["txn_id"] for t in flagged}
        # Check citations exist
        if not cited.issubset(flagged_ids):
            continue
        # Check count matches
        if obj.get("summary"):
            # simple heuristic: extract number from summary (could be improved)
            # We just verify the number of cited IDs matches count in flagged
            if len(cited) != len(flagged):
                continue
        # Check no foreign IDs (already covered)
        passed += 1
        if "latency" in obj:
            latencies.append(obj["latency"])

    accuracy = passed / total if total else 0
    avg_latency = sum(latencies) / len(latencies) if latencies else None

    # Update metrics JSON
    if os.path.exists(metrics_path):
        with open(metrics_path) as f:
            metrics = json.load(f)
    else:
        metrics = {}
    metrics.setdefault("summary_evaluation", {})
    metrics["summary_evaluation"]["accuracy"] = accuracy
    metrics["summary_evaluation"]["average_latency"] = avg_latency
    with open(metrics_path, "w") as f:
        json.dump(metrics, f, indent=2)
    print(f"Summary evaluation: {passed}/{total} passed ({accuracy:.1%}), avg latency {avg_latency:.3f}s")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Validate LLM summaries against flagged data")
    parser.add_argument("--flagged", type=str, default="data/flagged_transactions.csv")
    parser.add_argument("--summaries", type=str, default="results/summaries.jsonl")
    parser.add_argument("--metrics", type=str, default="results/metrics.json")
    args = parser.parse_args()
    evaluate_summaries(flagged_path=args.flagged, summaries_path=args.summaries, metrics_path=args.metrics)
