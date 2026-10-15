"""Load the paper's final IPHR question set (suffix non-ambiguous-hard-2).

Each template is a (property, comparison) combination, e.g. (wm-book-length, gt).
Within a template, every pair holds one question whose correct answer is YES
("Is X > Y?") and one whose correct answer is NO ("Is Y > X?").
"""

from pathlib import Path

import pandas as pd
import yaml

ROOT = Path(__file__).resolve().parents[1]
QDIR = ROOT / "data" / "questions"
SUFFIX = "non-ambiguous-hard-2"


def load_questions(qdir: Path = QDIR) -> pd.DataFrame:
    rows = []
    for path in sorted(qdir.glob(f"*/*_{SUFFIX}.yaml")):
        d = yaml.safe_load(path.open())
        p = d["params"]
        for qid, q in d["question_by_qid"].items():
            rows.append({
                "qid": qid,
                "prop_id": p["prop_id"],
                "comparison": p["comparison"],
                "answer": p["answer"],
                "q_str": q["q_str"],
                "x_name": q["x_name"],
                "y_name": q["y_name"],
                "x_value": q["x_value"],
                "y_value": q["y_value"],
            })
    df = pd.DataFrame(rows)
    # A pair is the same two entities under the same template, in both orders.
    df["pair_key"] = df.apply(
        lambda r: "|".join([r.prop_id, r.comparison] + sorted([r.x_name, r.y_name])), axis=1)
    return df


def pairs(df: pd.DataFrame) -> pd.DataFrame:
    """One row per pair with the YES-question id and the NO-question id."""
    yes = df[df.answer == "YES"].set_index("pair_key")
    no = df[df.answer == "NO"].set_index("pair_key")
    out = yes[["qid", "prop_id", "comparison"]].rename(columns={"qid": "qid_yes"})
    out["qid_no"] = no["qid"]
    return out.dropna().reset_index()


if __name__ == "__main__":
    df = load_questions()
    pr = pairs(df)
    print(len(df), "questions,", len(pr), "pairs,",
          pr.groupby(["prop_id", "comparison"]).ngroups, "templates")
