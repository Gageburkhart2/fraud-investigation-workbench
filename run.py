"""Orchestrate the fraud investigation pipeline.

Steps (default): generate → detect → summarize

You can also run individual steps via command‑line flags:
  --steps generate,detect,summary
"""

import argparse
import subprocess
import sys
import os

def run_step(script_path: str):
    # Execute the script using the same Python interpreter
    result = subprocess.run([sys.executable, script_path], check=True)
    return result.returncode

def main():
    parser = argparse.ArgumentParser(description="Run the fraud investigation workflow")
    parser.add_argument(
        "--steps",
        type=str,
        default="generate,detect,summary",
        help="Comma‑separated list of steps to run: generate,detect,summary",
    )
    args = parser.parse_args()
    steps = [s.strip() for s in args.steps.split(",") if s.strip()]

    step_map = {
        "generate": "src/generate_transactions.py",
        "detect": "src/detect_rules.py",
        "summary": "src/summarize_cases.py",
    }

    for step in steps:
        script = step_map.get(step)
        if not script:
            print(f"Unknown step: {step}", file=sys.stderr)
            sys.exit(1)
        print(f"Running step: {step} ({script})")
        run_step(script)

if __name__ == "__main__":
    main()
