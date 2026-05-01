#!/bin/bash
set -e
echo "=== DATATHON 2026 - Reproduce Pipeline ==="

echo "[1/4] Installing dependencies..."
pip install -r requirements.txt -q

echo "[2/4] Training models..."
python scripts/train.py

echo "[3/4] Generating submission..."
python scripts/predict.py

echo "[4/4] Done! Submission saved to outputs/submissions/submission_final.csv"
