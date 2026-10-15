"""Draw a fixed 21% sample of pairs from every template (seed 0).

At this size the paper's own saved counts give rates within about 0.5
percentage points of the full-set rates (checked for five models), and the
comparison with the paper is always made on this same sample.
"""

from pathlib import Path

from questions import load_questions, pairs

ROOT = Path(__file__).resolve().parents[1]

if __name__ == "__main__":
    pr = pairs(load_questions())
    sub = pr.groupby(["prop_id", "comparison"]).sample(frac=0.21, random_state=0)
    sub = sub.sample(frac=1, random_state=0)  # shuffle so --limit-pairs pilots are mixed
    sub.to_csv(ROOT / "data" / "subsample_pairs.csv", index=False)
    print(len(sub), "pairs from", sub.groupby(["prop_id", "comparison"]).ngroups, "templates")
