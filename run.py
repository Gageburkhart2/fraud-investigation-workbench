"""Orchestrate the fraud investigation pipeline.

Steps (default): generate → detect → summarize → evaluate

Additional options: --seed for data generation, --model and --temperature for LLM summarization.
"""

import argparse
import subprocess
import sys
import os

def run_step(script_path, args=None):
    cmd = [sys.executable, script_path]
    if args:
        cmd.extend(args)
    result = subprocess.run(cmd, check=True)
    return result.returncode

def main():
    parser = argparse.ArgumentParser(description="Run the fraud investigation pipeline")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for data generation")
    parser.add_argument("--model", type=str, help="Ollama model name (overrides OLLAMA_MODEL env)")
    parser.add_argument("--temperature", type=float, default=0.0, help="LLM temperature")
    args = parser.parse_args()

    # Generate
    print("Running generate_transactions")
    run_step(os.path.join("src", "generate_transactions.py"), ["--seed", str(args.seed)])

    # Detect
    print("Running detect_rules")
    run_step(os.path.join("src", "detect_rules.py"))

    # Summarize
    print("Running summarize_cases")
    summarize_args = []
    if args.model:
        summarize_args.extend(["--model", args.model])
    summarize_args.extend(["--temperature", str(args.temperature)])
    run_step(os.path.join("src", "summarize_cases.py"), summarize_args)

    # Evaluate
    print("Running evaluate_summaries")
    run_step(os.path.join("src", "evaluate_summaries.py"))

if __name__ == "__main__":
    main()
