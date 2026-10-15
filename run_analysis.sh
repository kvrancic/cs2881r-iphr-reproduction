#!/bin/bash
# Label every run, then recompute all results and figures.
# Calls already in the caches are not repeated, so with the release tarball
# unpacked (see README) this makes no paid API calls.
set -euo pipefail
cd "$(dirname "$0")/src"
PY=../.venv/bin/python
for f in ../data/responses/*/*.jsonl; do
  case "$f" in *.labels.jsonl|*.judge.jsonl) continue;; esac
  case "$f" in *sonnet-5.5*|*gemini-3.8*) continue;; esac   # 10-pair cost pilots only
  $PY judge.py "$f"
done
$PY validate_judge.py
$PY relabel_paper.py
$PY analyze_paper_data.py
$PY analyze_runs.py
$PY noise_models.py
$PY cited_facts.py openai/gpt-4o-mini meta-llama/llama-3.3-70b-instruct
$PY strict_reading.py
$PY geo_analysis.py
$PY figures.py
