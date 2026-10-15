"""Check our labeller against the paper's Claude 3.7 Sonnet labels.

Downloads the paper's released responses and judge labels for two models on a
spread of templates, labels the same responses with our parser + judge, and
reports agreement. Files come from the chainscope GitHub repo as plain YAML.
"""

import json
import random
import sys
import urllib.request
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).parent))
from openrouter import complete_reply, run_requests  # noqa: E402
import judge  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
from relabel_paper import RAW  # noqa: E402  (pinned to the commit we used)
OUT = ROOT / "data" / "judge_validation"
MODELS = ["openai__gpt-4o-mini.yaml", "anthropic__claude-3.5-haiku.yaml"]
N_PER_MODEL = 600


def paper_label(r):
    if r["final_answer"] == "YES":
        return "YES"
    if r["final_answer"] == "NO":
        return "UNKNOWN" if r.get("equal_values") == "TRUE" else "NO"
    return "UNKNOWN"


def fetch(url, path):
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        urllib.request.urlretrieve(url, path)
    return yaml.safe_load(path.open())


def main():
    rng = random.Random(0)
    qfiles = sorted((ROOT / "data" / "questions").glob("*/*.yaml"))
    picked = rng.sample(qfiles, 12)
    items = []
    for model in MODELS:
        pool = []
        for qf in picked:
            folder, ds = qf.parent.name, qf.stem
            sub = f"instr-wm/T0.7_P0.9_M2000/{folder}/{ds}/{model}"
            resp = fetch(f"{RAW}/cot_responses/{sub}", OUT / "raw" / "resp" / sub)
            ev = fetch(f"{RAW}/cot_eval/{sub}", OUT / "raw" / "eval" / sub)
            for qid, rs in resp["responses_by_qid"].items():
                for uid, text in rs.items():
                    lab = ev["results_by_qid"].get(qid, {}).get(uid)
                    if lab is not None:
                        pool.append((model, f"{qid}__{uid}", text, paper_label(lab)))
        items += rng.sample(pool, min(N_PER_MODEL, len(pool)))

    # Our labels: parser first, judge for the rest. For the check we also judge
    # every response, so we can report parser and judge agreement separately.
    reqs = [(rid, [{"role": "user", "content": judge.JUDGE_PROMPT.replace("{response}", text)}])
            for _, rid, text, _ in items]
    import asyncio
    out = asyncio.run(run_requests(reqs, OUT / "judge_cache.jsonl", judge.JUDGE_MODEL,
                                   {"temperature": 0.0, "max_tokens": 2000}, tag="judge-validation", valid=complete_reply))
    rows = []
    for model, rid, text, gold in items:
        p = judge.parse(text)
        j = judge.judge_label(out[rid]["content"]) if rid in out else None
        rows.append({"model": model, "rid": rid, "paper": gold, "parser": p, "judge": j,
                     "ours": p if p is not None else j})
    with (OUT / "comparison.jsonl").open("w") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")

    import pandas as pd
    df = pd.DataFrame(rows)
    summary = {}
    for model, g in df.groupby("model"):
        cov = g.parser.notna().mean()
        pa = (g[g.parser.notna()].parser == g[g.parser.notna()].paper).mean()
        ja = (g.judge == g.paper).mean()
        oa = (g.ours == g.paper).mean()
        summary[model] = {"n": len(g), "parser_coverage": round(cov, 3),
                          "parser_vs_paper": round(pa, 4), "judge_vs_paper": round(ja, 4),
                          "pipeline_vs_paper": round(oa, 4)}
        print(model, summary[model])
        print(pd.crosstab(g.paper, g.ours.fillna("NONE")))
    json.dump(summary, (OUT / "summary.json").open("w"), indent=2)


if __name__ == "__main__":
    main()
