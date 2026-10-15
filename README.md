# Reproducing Figure 2 of "Chain-of-Thought Reasoning in the Wild Is Not Always Faithful"

CS2881r mini-project. We reproduce the headline figure of Arcuschin et al. (ICML 2026, [arXiv:2503.08679](https://arxiv.org/abs/2503.08679)): the share of reversed question pairs ("Is X > Y?" / "Is Y > X?") on which a model gives the same answer to both in the direction of its usual lean. The paper calls this implicit post-hoc rationalization (IPHR).

- **Report:** [`report/report.pdf`](report/report.pdf) (4 pages)
- **Talk script:** [`talk/transcript.md`](talk/transcript.md); slides in [`deck/`](deck/)
- **Every choice we made and why:** [`DECISIONS.md`](DECISIONS.md)

## Results in one table

| | GPT-4o-mini | Llama 3.3 70B | DeepSeek V3 | Gemini 2.5 Flash |
|---|---|---|---|---|
| Paper's run, our 1,014 pairs | 14.4% | 2.8% | 1.7% | 2.9% (preview) |
| Our run, same pairs | 13.7% | 3.5% | 0.6% | 2.0% (general release) |
| Paper's flags that recur in our run | 105 of 146 | 19 of 28 | 1 of 17 | 14 of 29 |
| Our run with both true values in the prompt | 0.2% | 0.0% | 0.0% | not run |

Newer models on the same pairs: GPT-5.6 Luna 1.3% (0.0% with values), Qwen 3.8 Flash 0.3%, Claude Haiku 5.5 0.2%, DeepSeek V4 Flash 0.1%.

From the authors' released counts alone (no API calls): our code reproduces the flagged-pair count of all 16 models in Figure 2; the plotting script divides by 4,892 where the dataset has 4,834 pairs; at the paper's 0.5 cutoff, 103 of 193 flags survive the authors' 100-sample retest (they report 76% using a 0.4 cutoff).

## Layout

```
src/
  questions.py           load the paper's final question set (4,834 pairs, 58 templates)
  iphr.py                the paper's pair criteria, matched to their code
  make_subsample.py      the fixed 21% sample of pairs (data/subsample_pairs.csv)
  openrouter.py          async client with an on-disk cache and a spend cap
  generate.py            sample answers (paper prompt; --condition factcard adds the true values)
  judge.py               label answers YES / NO / UNKNOWN (strict rule, then the paper's judge prompt)
  validate_judge.py      compare our labels with the paper's on 1,200 of their answers
  analyze_paper_data.py  Figure 2 counts, retest and lean-by-kind from the released counts
  analyze_runs.py        rates, CIs, paper-vs-ours agreement on the same pairs
  cited_facts.py         what the answers in flagged pairs state about the compared values
  figures.py             report figures
data/
  questions/             the paper's question files (non-ambiguous-hard-2)
  subsample_pairs.csv    the 1,014 pairs we sampled
  responses/<condition>/<model>.labels.jsonl   our YES/NO/UNKNOWN labels for every answer
  judge_validation/      our labels against the paper's on their answers
results/                 JSON and CSV outputs of the analysis scripts
figures/                 report figures
run_all.sh               all generation jobs
run_analysis.sh          labelling, analysis and figures (cached calls are free)
```

Raw model answers (about 370 MB) are not in git; they are attached to the repository's release as `responses.tar.gz`. Unpack it into `data/responses/` to rerun the labelling without API calls.

## Rerunning

```bash
uv venv .venv --python 3.12
uv pip install --python .venv/bin/python httpx pandas numpy scipy matplotlib pyyaml python-dotenv
echo "OPENROUTER_API_KEY=..." > .env

# The paper's per-question counts (needed for the zero-cost checks), from the authors' repo:
mkdir -p data/paper && curl -L -o data/paper/df-wm-non-ambiguous-hard-2.pkl.gz \
  https://github.com/jettjaniak/chainscope/raw/main/chainscope/data/df-wm-non-ambiguous-hard-2.pkl.gz

./run_all.sh        # generation, about $65 at October 2026 OpenRouter prices
./run_analysis.sh   # labels, analysis, figures; a few dollars for the judge
```

`SPEND_CAP_USD` (default 100) stops all calls once the logged spend reaches it. The released pickle contains only pandas and numpy objects; we checked its opcodes before loading it.

## Worklog

- **Day 1, morning.** Read the paper and the authors' code. Recomputed Figure 2 from the released counts and found the denominator and retest-threshold details. Checked our labeller against 1,200 of the authors' labelled answers.
- **Day 1, midday.** Ran 8 models and the fact-card condition on 1,014 pairs. Found that the judge model's own thinking used up the token limit on up to 8% of calls; purged those replies and re-judged with a larger limit.
- **Day 1, afternoon.** Built the cited-facts reader; restricted it to the asked property after reading samples showed it was counting north/south statements on east/west questions. Wrote the report and the talk.
