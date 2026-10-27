#!/usr/bin/env bash
set -e

REPO_ROOT=$(dirname "$(realpath "$0")")
cd "$REPO_ROOT"

# Clean previous artifacts
rm -rf data results

# Run the pipeline
python3 run.py

# Verify files exist
if [[ ! -f data/transactions.csv ]]; then echo "Missing transactions.csv"; exit 1; fi
if [[ ! -f data/flagged_transactions.csv ]]; then echo "Missing flagged_transactions.csv"; exit 1; fi
if [[ ! -f results/summaries.txt ]]; then echo "Missing summaries.txt"; exit 1; fi

# Basic content checks
FLAGGED_COUNT=$(wc -l < data/flagged_transactions.csv)
if [[ $FLAGGED_COUNT -le 1 ]]; then echo "No flagged rows"; exit 1; fi

# Summaries count should match unique cards in flagged file
UNIQUE_CARDS=$(cut -d, -f2 data/flagged_transactions.csv | tail -n +2 | sort -u | wc -l)
SUMMARY_COUNT=$(wc -l < results/summaries.txt)
if [[ $UNIQUE_CARDS -ne $SUMMARY_COUNT ]]; then echo "Summaries count ($SUMMARY_COUNT) != unique cards ($UNIQUE_CARDS)"; exit 1; fi

echo "All checks passed."
