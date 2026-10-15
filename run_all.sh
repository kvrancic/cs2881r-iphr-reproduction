#!/bin/bash
# Run every generation job; five at a time to stay under OpenRouter's in-flight credit limit.
cd "$(dirname "$0")/src"
P=../data/subsample_pairs.csv
jobs=(
 "--model openai/gpt-4o-mini --pairs $P"
 "--model meta-llama/llama-3.3-70b-instruct --pairs $P --no-top-p"
 "--model deepseek/deepseek-chat --pairs $P --no-top-p"
 "--model google/gemini-2.5-flash --pairs $P --no-top-p"
 "--model openai/gpt-4o-mini --pairs $P --condition factcard"
 "--model meta-llama/llama-3.3-70b-instruct --pairs $P --condition factcard --no-top-p"
 "--model deepseek/deepseek-chat --pairs $P --condition factcard --no-top-p"
 "--model openai/gpt-5.6-luna --pairs $P --condition factcard --max-tokens 8000"
 "--model openai/gpt-4o-mini --pairs ../data/subsample_geo_pairs.csv --condition coordwording"
 "--model openai/gpt-4o-mini --pairs ../data/subsample_geo_pairs.csv --condition paraphrase"
 "--model openai/gpt-4o-mini --pairs ../data/subsample_geo_pairs.csv --condition clarified"
 "--model openai/gpt-4o-mini --pairs ../data/subsample_geo_pairs.csv --condition fullcard"
 "--model openai/gpt-4o-mini --pairs ../data/subsample_geo_pairs.csv --condition strict"
 "--model openai/gpt-4o-mini --pairs ../data/subsample_other_pairs.csv --condition tiecard"
 "--model meta-llama/llama-3.3-70b-instruct --pairs ../data/subsample_other_pairs.csv --condition tiecard --no-top-p"
 "--model openai/gpt-4o-mini --pairs ../data/subsample_other_pairs.csv --condition tieforced"
 "--model meta-llama/llama-3.3-70b-instruct --pairs ../data/subsample_other_pairs.csv --condition tieforced --no-top-p"
 "--model anthropic/claude-haiku-5.5 --pairs $P --max-tokens 8000"
 "--model openai/gpt-5.6-luna --pairs $P --max-tokens 8000"
 "--model deepseek/deepseek-v4-flash --pairs $P --max-tokens 8000"
 "--model qwen/qwen3.8-flash --pairs $P --max-tokens 8000"
)
printf '%s\n' "${jobs[@]}" | xargs -P 5 -I{} sh -c '../.venv/bin/python generate.py {} --concurrency 250'
