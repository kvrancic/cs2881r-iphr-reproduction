# Reproducing Figure 2 of "Chain-of-Thought Reasoning in the Wild Is Not Always Faithful"

CS2881r mini-project. We reproduce Figure 2 of Arcuschin et al. (ICML 2026, [arXiv:2503.08679](https://arxiv.org/abs/2503.08679)): the share of reversed question pairs ("Is X > Y?" / "Is Y > X?") on which a model gives the same answer to both in the direction of its usual lean. The paper calls this implicit post-hoc rationalization (IPHR).

- **Report:** [`report/report.pdf`](report/report.pdf) (5 pages)
- **Talk:** script in [`talk/transcript.md`](talk/transcript.md), slides in [`deck/IPHR_Reproduction.pptx`](deck/IPHR_Reproduction.pptx) (PDF copy in [`deck/review/qa/`](deck/review/qa/))
- **Every choice we made and why:** [`DECISIONS.md`](DECISIONS.md)

## Results

| On our 1,014 pairs | GPT-4o-mini | Llama 3.3 70B | DeepSeek V3 | Gemini 2.5 Flash |
|---|---|---|---|---|
| Flagged, paper's run | 146 | 28 | 17 | 29 (preview) |
| Flagged, paper's answers with our labeller | 134 | 31 | 12 | 25 |
| Flagged, our run | 139 | 35 | 6 | 20 (general release) |
| Lean gap, paper / ours | 0.164 / 0.157 | 0.059 / 0.071 | 0.038 / 0.035 | 0.059 / 0.057 |
| Paper's flags flagged again (ceiling if unchanged) | 72% (69%) | 68% (54%) | 6% (45%) | 48% (63%) |
| Flagged with both true values in the prompt | 2 | 0 | 0 | not run |

- Newer models on the same pairs: GPT-5.6 Luna 13 flags (0 with values), Qwen 3.8 Flash 3, Claude Haiku 5.5 2, DeepSeek V4 Flash 1.
- GPT-4o-mini's 684 geography pairs asked as "at a more western longitude than": 131 flags fall to 24, with no values given.
- From the authors' released counts alone: our code gives the plotted count exactly for the 8 models with 10-answer data; the plot divides by 4,892 where the data hold 4,834 pairs; the retest keeps 61% of flags at the stated 0.5 cutoff (74% at the code's 0.4; the paper reports 76.5%).
- A model that knows a pair or else guesses with one lean per template predicts the flag count for 4 of the paper's 8 checkable models and for all 8 of our runs.

## Layout

```
src/
  questions.py           the paper's final question set (4,834 pairs, 58 templates)
  iphr.py                the pair criteria, matched to the authors' code
  make_subsample.py      the fixed 21% sample (data/subsample_pairs.csv, committed; rebuilds byte-identically)
  openrouter.py          async client with an on-disk cache and a spend cap
  generate.py            sample answers: --condition base | factcard | coordwording
  judge.py               label answers YES / NO / UNKNOWN (strict rule, then the paper's judge prompt)
  judge_prompt.txt       the authors' judge prompt, word for word
  validate_judge.py      our labels against theirs on 1,200 of their answers
  relabel_paper.py       the paper's own answers on our pairs, relabelled by us
  analyze_paper_data.py  Figure 2 counts, retest and lean by kind, from the released counts
  analyze_runs.py        rates, intervals, paper-vs-ours agreement
  noise_models.py        recurrence ceiling, know-or-guess model, paired tests, threshold grid
  cited_facts.py         what the answers in flagged pairs state about the compared values
  strict_reading.py      strict-reading phrases by side of each geography pair
  figures.py             report figures
data/
  questions/             the paper's question files (non-ambiguous-hard-2)
  subsample_pairs.csv    our 1,014 pairs (subsample_geo_pairs.csv: the 684 geography pairs)
  responses/<condition>/<model>.labels.jsonl   our label for every answer
  judge_validation/      our labels against the paper's on their answers
results/                 JSON and CSV outputs of the analysis scripts
figures/                 report figures
report/                  report.tex and report.pdf (build: cd report && pdflatex report.tex, twice)
talk/                    transcript.md (the spoken script) and storyboard.md
deck/                    the slide engine (Python, pixel art, PowerPoint Morph) and the built deck
logs/                    run logs with progress and spend
tools/lint.py            a writing-style check we ran on the report, README and talk
run_all.sh               all generation jobs
run_analysis.sh          labelling, analysis and figures
```

## Rerunning

```bash
uv venv .venv --python 3.12
uv pip install --python .venv/bin/python -r requirements.txt

# The authors' per-question counts, pinned to the commit we used:
mkdir -p data/paper && curl -L -o data/paper/df-wm-non-ambiguous-hard-2.pkl.gz \
  https://github.com/jettjaniak/chainscope/raw/bb128ac0f22dd60ab3d876a78e1c6c22fff7e830/chainscope/data/df-wm-non-ambiguous-hard-2.pkl.gz
shasum -a 256 data/paper/df-wm-non-ambiguous-hard-2.pkl.gz
# 80c23e2af268e36ba651585103a2dcfbd376789f1d21add01dfeaacbd3b059cc
```

The pickle holds only pandas and numpy objects; we listed its opcodes with `pickletools` before loading it.

**Zero-cost check (no API key, no downloads beyond the pickle).** This recomputes every number in `results/` from the committed labels and reproduces `figures/` exactly:

```bash
cd src && ../.venv/bin/python analyze_paper_data.py && ../.venv/bin/python analyze_runs.py \
  && ../.venv/bin/python noise_models.py && ../.venv/bin/python figures.py
```

**Full rerun.** `cited_facts.py`, `strict_reading.py` and relabelling need the raw answers. They are in the release [`data-v1`](https://github.com/kvrancic/cs2881r-iphr-reproduction/releases/tag/data-v1) as `responses.tar.gz` (`tar -xzf responses.tar.gz` at the repository root restores `data/responses/`, `data/cited_facts/` and the judge caches; then `./run_analysis.sh` makes no paid calls). To sample everything again, put `OPENROUTER_API_KEY=...` in `.env` and run `./run_all.sh` then `./run_analysis.sh`. `SPEND_CAP_USD` (default 100) stops all calls once logged spend reaches it.

Cost of our runs at October 2026 OpenRouter prices: $61 for answers, $14 for labels, $2 for the fact reader, $76 in total.

## Worklog

15 October 2026, local time, taken from commit and file times.

- **02:00–02:35.** Read the paper and the authors' code. Found that Figure 2's bars are typed into the plotting script and divided by 4,892. Recomputed the 8 models with 10-answer data exactly and found the 0.4 retest cutoff. Checked our labeller against 1,200 of the authors' labelled answers.
- **02:35–03:30.** Ran 10-pair cost pilots on ten models and dropped Claude Sonnet 5.5 and Gemini 3.8 Flash on cost. Ran 8 models and the fact cards on 1,014 pairs. A network outage and OpenRouter's in-flight credit limit (HTTP 402) stalled the runs; we made 402 retryable and changed the concurrency.
- **03:30–04:00.** Found that Claude Haiku 5.5's own thinking used up the judge's token limit on up to 8% of calls; deleted those replies and re-judged with a larger limit (the code now resends cut-off replies). Built the fact reader; reading samples showed it counted north/south statements on east/west questions, so we limited it to the asked property. Found that flags split into geography leaning NO and everything else leaning YES.
- **04:00–04:10.** First report draft. Five independent adversarial reviewers scored it at about 72/100. They pointed to overclaims, a missing noise baseline and a judge check that skipped the answers that matter.
- **04:10–04:30.** Added the noise ceiling, the know-or-guess model, paired tests, the relabelling of the paper's answers, the coordinate-wording run and the strict-reading count. Rewrote the report and the talk.
