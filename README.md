# Reproducing Figure 2 of "Chain-of-Thought Reasoning in the Wild Is Not Always Faithful"

CS2881r mini-project by [Name 1], [Name 2] and [Name 3]. We reproduce Figure 2 of Arcuschin et al. (ICML 2026, [arXiv:2503.08679](https://arxiv.org/abs/2503.08679)): the share of reversed question pairs ("Is X > Y?" / "Is Y > X?") on which a model gives the same answer to both in the direction of its usual lean. The paper calls this implicit post-hoc rationalization (IPHR).

- **Report:** [`report/report.pdf`](report/report.pdf) (5 pages)
- **Talk:** script in [`talk/transcript.md`](talk/transcript.md), slides in [`deck/IPHR_Reproduction.pptx`](deck/IPHR_Reproduction.pptx) with a PDF copy in [`deck/IPHR_Reproduction.pdf`](deck/IPHR_Reproduction.pdf)
- **Decision log:** [`DECISIONS.md`](DECISIONS.md)

## Results

| On our 1,014 pairs | GPT-4o-mini | Llama 3.3 70B | DeepSeek V3 | Gemini 2.5 Flash |
|---|---|---|---|---|
| Flagged, paper's run | 146 | 28 | 17 | 29 (preview) |
| Flagged, paper's answers with our labeller | 134 | 31 | 12 | 25 |
| Flagged, our run | 139 | 35 | 6 | 20 (general release) |
| Lean gap, paper / ours | 0.164 / 0.157 | 0.059 / 0.071 | 0.038 / 0.035 | 0.059 / 0.057 |
| Pair asymmetry correlation across runs (template-only null, 97.5%) | 0.69 (0.18) | 0.47 (0.17) | 0.41 (0.22) | 0.33 (0.19) |
| Excess asymmetry that returns in our run, lean side / other side (nulls about 0.04–0.05) | 0.19 / 0.24 | 0.05 / 0.07 | 0.07 / 0.10 | 0.05 / 0.09 |
| Flagged with both true values in the prompt | 2 | 0 | 0 | not run |

- **Newer models on the same pairs:** GPT-5.6 Luna 13 flags (0 with values), Qwen 3.8 Flash 3, Claude Haiku 5.5 2, DeepSeek V4 Flash 1.
- **Tie cards** (one rounded value printed for both entities, 330 non-geography pairs): GPT-4o-mini and Llama 3.3 answer UNKNOWN 98% and 89% of the time, as the card invites; too few answers remain to measure a lean.
- **Closed-book recall:** asked for each value alone, Llama 3.3 orders 72% of its 32 flagged non-geography pairs correctly (85% of unflagged pairs; chance is 50%).
- **GPT-4o-mini's 684 geography pairs:** 131 flags with the paper's wording, 140 with a paraphrase, 31 with one sentence saying that anywhere further west counts, 667 with one sentence saying only directly west counts, 24 with "a more western longitude", 0 with both coordinates of both places, 2 with the asked coordinate.
- **From the authors' released counts alone:**
  - our code gives the plotted count exactly for the 8 models with 10-answer data, as well as their 64 values in the paper's Table 10;
  - the plot divides by 4,892 where the data hold 4,834 pairs;
  - averaged over models, the retest keeps 61% of flags at the stated 0.5 cutoff (74% at the code's 0.4; the paper reports 76.5%, also averaged over models);
  - the model ranking changes in 16 of 19 alternative cutoff settings, as the paper's own Table 10 also shows;
  - by kind of question the two model rankings are negatively correlated (Kendall τ = −0.57): GPT-4o-mini is first on geography (19.6%) and seventh on the rest (1.4%), QwQ last on geography (0.2%) and first on the rest (13.6%).

## Layout

```
src/
  questions.py           the paper's final question set (4,834 pairs, 58 templates)
  iphr.py                the pair criteria, matched to the authors' code
  make_subsample.py      the fixed 21% sample and its geography pairs (both committed; rebuild byte-identically)
  openrouter.py          async client with an on-disk cache and a spend cap
  generate.py            sample answers: --condition base | factcard | tiecard | coordwording | paraphrase | clarified | strict | fullcard
  judge.py               label answers YES / NO / UNKNOWN (strict rule, then the paper's judge prompt)
  judge_prompt.txt       the authors' judge prompt, word for word
  validate_judge.py      our labels against theirs on 1,200 of their answers
  relabel_paper.py       the paper's own answers on our pairs, relabelled by us
  analyze_paper_data.py  Figure 2 counts, retest and lean by kind, from the released counts
  analyze_runs.py        rates, intervals, paper-vs-ours agreement, fact cards by kind
  noise_models.py        expected recurrence, residual test, paired tests, cutoff grid, Figure 2 by kind
  geo_analysis.py        the seven geography wordings and flag rates by distance
  tie_analysis.py        tie cards: does the lean act when the prompt leaves the order open
  recall_probe.py        closed-book recall of each entity's value, flagged vs unflagged pairs
  report_tables.py       writes report/table_agree.tex (Table 1) from the result files
  cited_facts.py         what the answers in flagged pairs state about the compared values
  strict_reading.py      strict-reading phrases by side of each geography pair
  figures.py             report figures
data/
  questions/, properties/   the paper's question files and the geography coordinates
  subsample_pairs.csv       our 1,014 pairs (subsample_geo_pairs.csv and subsample_other_pairs.csv split them)
  responses/<condition>/<model>.labels.jsonl   our label for every answer
  paper_answers/            our judge's replies on the paper's answers
  judge_validation/         our labels against the paper's on their answers
results/                    JSON and CSV outputs of the analysis scripts
figures/                    report figures
report/                     report.tex and report.pdf (build: cd report && pdflatex report.tex, twice)
talk/                       transcript.md, the spoken script
deck/                       the slides and the Python engine that draws them (deck/README.md)
logs/                       run logs with progress and spend
tools/lint.py               a writing-style check we ran on the report, README and talk
run_all.sh                  all generation jobs
run_analysis.sh             labelling, analysis and figures
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

**Zero-cost check (no API key, only the pickle).** From `src/`:

```bash
../.venv/bin/python analyze_paper_data.py   # results/paper_data_checks.json
../.venv/bin/python analyze_runs.py         # results/runs.json, pairs_base.csv, pairs_factcard.csv
../.venv/bin/python noise_models.py         # results/noise_models.json (also reads paper_answers_our_labels.csv)
../.venv/bin/python figures.py              # figures/ (needs relabel_paper.json and geo_analysis.json, committed)
```

**Full rerun without new sampling.** The raw answers are in the release [`data-v2`](https://github.com/kvrancic/cs2881r-iphr-reproduction/releases/tag/data-v2) as `responses.tar.gz` (97518561 bytes, sha256 `e49759ddcc08d92e510376517383d26a76b50202fa0d3ee40df87a6b4ff9333d`). Run `tar -xzf responses.tar.gz` at the repository root. Then `./run_analysis.sh` regenerates every file in `results/` and `figures/` with no paid calls. It needs internet access: `validate_judge.py` and `relabel_paper.py` download the authors' answer files from GitHub (cached under `data/*/raw/`).

**Full rerun with new sampling.** Put `OPENROUTER_API_KEY=...` in `.env`, then run `./run_all.sh` and `./run_analysis.sh`. `SPEND_CAP_USD` (default 100) stops each job once logged spend reaches it. Each job checks only its own running total, so with five jobs in parallel our total passed the cap by $2.91. The 10-pair cost pilots used `generate.py --limit-pairs 10`.

Cost of our runs at October 2026 OpenRouter prices: $103 in total (answers, labels, the fact reader and the recall probe; `data/spend.jsonl.gz` logs the cost of every call).

## Use of AI tools

Claude (Anthropic) wrote most of the code, ran the experiments and drafted the report, the talk script and the slides under our direction. AI reviewers (Claude agents asked to grade, fact-check, edit and attack the work) critiqued the drafts. We checked the reported numbers against the result files.

## Worklog

15 October 2026, local time, from commit and file times.

- **02:00–02:35.** Read the paper and the authors' code. Found that Figure 2's bars are typed into the plotting script and divided by 4,892. Recomputed the 8 models with 10-answer data exactly and found the 0.4 retest cutoff. Checked our labeller against 1,200 of the authors' labelled answers.
- **02:35–03:30.** Ran 10-pair cost pilots on ten models and left out Claude Sonnet 5.5 and Gemini 3.8 Flash on cost. Ran 8 models and the fact cards on 1,014 pairs. A network outage and OpenRouter's in-flight credit limit (HTTP 402) stalled the runs. We made 402 retryable and ran five jobs at a time with up to 250 open requests each.
- **03:30–04:00.** Claude Haiku 5.5's own thinking used up the judge's 600-token limit on up to 8% of calls. We deleted those replies and re-judged with 2,000 tokens. Built the fact reader; reading samples showed it counted north/south statements on east/west questions, so we limited it to the asked property. Found that flags split into geography leaning NO and everything else leaning YES.
- **04:00–04:30.** Wrote the report. Added the expected recurrence, relabelling of the paper's own answers and the "more western longitude" run.
- **04:30–05:15.** Added the residual test, Figure 2 by kind and three geography controls (paraphrase, a plain-language sentence on what "west of" means, both coordinates).
- **05:15–06:10.** Added a one-sided residual test, a closed-book recall probe, tie cards, a strict-reading control and distance tables for geography. Generated Table 1 from the result files.
- **06:30–07:30.** Added a mirror control to the residual test (the lean side and the other side return by similar amounts, so the repeated asymmetry is not specific to the lean), a forced-choice tie card, template-cluster intervals for Figure 1 and the full 20-setting cutoff grid. Built the deck.
- **07:30–09:45.** Revised the report, talk and deck. Computed the expected recurrence from our labels and recorded the sample's effect on the paper's rates. Regenerated the figures and Table 1.
