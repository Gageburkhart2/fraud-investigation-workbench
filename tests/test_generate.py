import os
import csv
from datetime import datetime
import subprocess
import sys

def test_generate_seed_consistency(tmp_path):
    # generate with seed 123
    out_csv = tmp_path / "transactions.csv"
    subprocess.run([sys.executable, "src/generate_transactions.py", "--seed", "123", "--output", str(out_csv)], check=True)
    # generate again with same seed and compare first few rows
    out_csv2 = tmp_path / "transactions2.csv"
    subprocess.run([sys.executable, "src/generate_transactions.py", "--seed", "123", "--output", str(out_csv2)], check=True)
    with open(out_csv) as f1, open(out_csv2) as f2:
        lines1 = [next(f1) for _ in range(5)]
        lines2 = [next(f2) for _ in range(5)]
    assert lines1 == lines2
