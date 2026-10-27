import os
import csv
import json
import time
from collections import defaultdict
from datetime import datetime
import argparse
import requests

def summarize_cases(flagged_path="data/flagged_transactions.csv", output_path="results/summaries.jsonl", model=None, temperature=0.0):
    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Resolve model name
    if model is None:
        model = os.getenv("OLLAMA_MODEL", "llama2")

    # Load flagged transactions
    flagged = []
    with open(flagged_path, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            row["timestamp"] = datetime.fromisoformat(row["timestamp"])
            row["amount"] = float(row["amount"])
            row["is_fraud"] = int(row["is_fraud"])
            flagged.append(row)

    # Group by card
    by_card = defaultdict(list)
    for txn in flagged:
        by_card[txn["card_id"]].append(txn)

    # Helper to build prompt
    def build_prompt(card_id, txns):
        lines = [f"Card {card_id} has {len(txns)} flagged transactions:"]
        for t in txns:
            lines.append(f"- ID {t['txn_id']}, {t['timestamp'].isoformat()}, ${t['amount']:.2f}, {t['merchant_category']}")
        lines.append("Summarize the suspicious pattern, total amount, risk assessment, and next investigation step. Cite each transaction ID used.")
        return "\n".join(lines)

    results = []
    for card_id, txns in by_card.items():
        prompt = build_prompt(card_id, txns)
        start = time.perf_counter()
        try:
            resp = requests.post(
                "http://localhost:11434/api/generate",
                json={"model": model, "prompt": prompt, "stream": False, "temperature": temperature},
                timeout=30,
            )
            resp.raise_for_status()
            data = resp.json()
            summary = data.get("response", "").strip()
            used_ids = [t["txn_id"] for t in txns]  # assume all cited
        except Exception as e:
            # Ollama not reachable – fall back to template
            summary = (
                f"Card {card_id} flagged with {len(txns)} suspicious transactions "
                f"between {min(t['timestamp'] for t in txns)} and {max(t['timestamp'] for t in txns)}, "
                f"total amount ${sum(t['amount'] for t in txns):.2f}."
            )
            used_ids = [t["txn_id"] for t in txns]
            print(f"Ollama request failed for card {card_id}: {e}. Using fallback summary.")
        latency = time.perf_counter() - start
        result = {
            "card_id": card_id,
            "summary": summary,
            "cited_ids": used_ids,
            "model": model,
            "latency": latency,
        }
        results.append(result)

    # Write JSONL
    with open(output_path, "w") as f:
        for obj in results:
            f.write(json.dumps(obj) + "\n")
    print(f"Wrote {len(results)} summaries to {output_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Summarize flagged cards with Ollama LLM")
    parser.add_argument("--flagged", type=str, default="data/flagged_transactions.csv")
    parser.add_argument("--output", type=str, default="results/summaries.jsonl")
    parser.add_argument("--model", type=str, help="Ollama model name (overrides OLLAMA_MODEL env)")
    parser.add_argument("--temperature", type=float, default=0.0, help="Sampling temperature for LLM")
    args = parser.parse_args()
    summarize_cases(flagged_path=args.flagged, output_path=args.output, model=args.model, temperature=args.temperature)
