# Reproducing Figure 2 of "Chain-of-Thought Reasoning in the Wild Is Not Always Faithful"

CS2881r mini-project by [Name 1], [Name 2] and [Name 3]. We reproduce Figure 2 of Arcuschin et al. (ICML 2026, [arXiv:2503.08679](https://arxiv.org/abs/2503.08679)): the share of reversed question pairs ("Is X > Y?" / "Is Y > X?") on which a model gives the same answer to both in the direction of its usual lean. The paper calls this implicit post-hoc rationalization (IPHR).

- **Report:** [`report/report.pdf`](report/report.pdf) (5 pages)
- **Talk:** script in [`talk/transcript.md`](talk/transcript.md), slides in [`deck/IPHR_Reproduction.pptx`](deck/IPHR_Reproduction.pptx) with a PDF copy in [`deck/IPHR_Reproduction.pdf`](deck/IPHR_Reproduction.pdf)
- **Every choice we made and why:** [`DECISIONS.md`](DECISIONS.md)

## Results

| On our 1,014 pairs | GPT-4o-mini | Llama 3.3 70B | DeepSeek V3 | Gemini 2.5 Flash |
|---|---|---|---|---|
| Flagged, paper's run | 146 | 28 | 17 | 29 (preview) |
| Flagged, paper's answers with our labeller | 134 | 31 | 12 | 25 |
| Flagged, our run | 139 | 35 | 6 | 20 (general release) |
| Lean gap, paper / ours | 0.164 / 0.157 | 0.059 / 0.071 | 0.038 / 0.035 | 0.059 / 0.057 |
| Pair asymmetry correlation across runs (template-only null, 97.5%) | 0.69 (0.18) | 0.47 (0.16) | 0.41 (0.23) | 0.33 (0.20) |
| Flagged with both true values in the prompt | 2 | 0 | 0 | not run |

- **Newer models on the same pairs:** GPT-5.6 Luna 13 flags (0 with values), Qwen 3.8 Flash 3, Claude Haiku 5.5 2, DeepSeek V4 Flash 1.
- **GPT-4o-mini's 684 geography pairs:** 131 flags with the paper's wording, 140 with a paraphrase, 31 with one sentence saying what "west of" means, 24 with "a more western longitude", 0 with both coordinates of both places, 2 with the asked coordinate.
- **From the authors' released counts alone:**
  - our code gives the plotted count exactly for the 8 models with 10-answer data;
  - the plot divides by 4,892 where the data hold 4,834 pairs;
  - the retest keeps 61% of flags at the stated 0.5 cutoff (74% at the code's 0.4; the paper reports 76.5%);
  - the model ranking changes in 8 of 11 alternative cutoff settings;
  - by kind of question the ranking nearly reverses: GPT-4o-mini is flagged on 19.6% of geography pairs and 1.4% of the rest, QwQ on 0.2% and 13.6%.

## Layout

```
src/
  questions.py           the paper's final question set (4,834 pairs, 58 templates)
  iphr.py                the pair criteria, matched to the authors' code
  make_subsample.py      the fixed 21% sample and its geography pairs (both committed; rebuild byte-identically)
  openrouter.py          async client with an on-disk cache and a spend cap
  generate.py            sample answers: --condition base | factcard | coordwording | paraphrase | clarified | fullcard
  judge.py               label answers YES / NO / UNKNOWN (strict rule, then the paper's judge prompt)
  judge_prompt.txt       the authors' judge prompt, word for word
  validate_judge.py      our labels against theirs on 1,200 of their answers
  relabel_paper.py       the paper's own answers on our pairs, relabelled by us
  analyze_paper_data.py  Figure 2 counts, retest and lean by kind, from the released counts
  analyze_runs.py        rates, intervals, paper-vs-ours agreement, fact cards by kind
  noise_models.py        expected recurrence, residual test, paired tests, cutoff grid, Figure 2 by kind
  geo_analysis.py        the six geography wordings and the other-axis offset check
  cited_facts.py         what the answers in flagged pairs state about the compared values
  strict_reading.py      strict-reading phrases by side of each geography pair
  figures.py             report figures
data/
  questions/, properties/   the paper's question files and the geography coordinates
  subsample_pairs.csv       our 1,014 pairs (subsample_geo_pairs.csv: the 684 geography pairs)
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

**Full rerun with new sampling.** Put `OPENROUTER_API_KEY=...` in `.env`, then run `./run_all.sh` and `./run_analysis.sh`. `SPEND_CAP_USD` (default 100) stops all calls once logged spend reaches it. The 10-pair cost pilots used `generate.py --limit-pairs 10`.

Cost of our runs at October 2026 OpenRouter prices: $66 for answers, $16 for labels, $2 for the fact reader, $84 in total.

## Use of AI tools

Claude (Anthropic) wrote most of the code, ran the experiments and drafted the report, the talk script and the slides under our direction. Two rounds of AI reviewers (Claude agents asked to grade, fact-check, edit and attack the work) critiqued drafts; we changed the analysis and the text in response. We checked the reported numbers against the result files.

## Worklog

15 October 2026, local time, from commit and file times.

- **02:00–02:35.** Read the paper and the authors' code. Found that Figure 2's bars are typed into the plotting script and divided by 4,892. Recomputed the 8 models with 10-answer data exactly and found the 0.4 retest cutoff. Checked our labeller against 1,200 of the authors' labelled answers.
- **02:35–03:30.** Ran 10-pair cost pilots on ten models and left out Claude Sonnet 5.5 and Gemini 3.8 Flash on cost. Ran 8 models and the fact cards on 1,014 pairs. A network outage and OpenRouter's in-flight credit limit (HTTP 402) stalled the runs. We made 402 retryable and ran five jobs at a time with up to 250 open requests each.
- **03:30–04:00.** Claude Haiku 5.5's own thinking used up the judge's 600-token limit on up to 8% of calls. We deleted those replies and re-judged with 2,000 tokens. Built the fact reader; reading samples showed it counted north/south statements on east/west questions, so we limited it to the asked property. Found that flags split into geography leaning NO and everything else leaning YES.
- **04:00–04:30.** First report. The first AI review found overclaims, no noise baseline and a judge check limited to easy answers. Added the expected recurrence, relabelling of the paper's own answers and the "more western longitude" run.
- **04:30–05:15.** The second AI review found that comparing flag counts had little power and that the coordinate wording mixed a clearer reading with coordinate recall. Added the residual test, Figure 2 by kind and three geography controls (paraphrase, a plain-language sentence on what "west of" means, both coordinates). The residual test reversed our earlier reading: pair-specific order effects exist and repeat. Rewrote the report and the talk.
