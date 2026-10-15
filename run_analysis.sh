#!/bin/bash
# Label every run, then recompute all results and figures. Cached calls are not repeated.
set -e
cd "$(dirname "$0")/src"
PY=../.venv/bin/python
for f in ../data/responses/base/*.jsonl ../data/responses/factcard/*.jsonl; do
  case "$f" in *.labels.jsonl|*.judge.jsonl) continue;; esac
  case "$f" in *sonnet-5.5*|*gemini-3.8*) continue;; esac   # 10-pair cost pilots only
  $PY judge.py "$f" | tail -1
done
$PY validate_judge.py | grep -v "^\s*\["
$PY analyze_paper_data.py > /dev/null
$PY analyze_runs.py 2>&1 | grep -v Warning
$PY cited_facts.py openai/gpt-4o-mini meta-llama/llama-3.3-70b-instruct | grep -v "^\s*\["
$PY figures.py 2>&1 | grep -v findfont
