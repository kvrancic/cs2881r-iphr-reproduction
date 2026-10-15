"""Draw a fixed 21% sample of each template's pairs (seed 0).

On the authors' saved counts this sample moves the Figure 2 rates by -0.4 to
+1.0 points, so every comparison with the paper is made on this same sample.
Also writes the geography pairs of the sample, used by the wording runs.
"""

from pathlib import Path

from questions import load_questions, pairs

ROOT = Path(__file__).resolve().parents[1]

if __name__ == "__main__":
    pr = pairs(load_questions())
    sub = pr.groupby(["prop_id", "comparison"]).sample(frac=0.21, random_state=0)
    sub = sub.sample(frac=1, random_state=0)  # shuffle so --limit-pairs pilots are mixed
    sub.to_csv(ROOT / "data" / "subsample_pairs.csv", index=False)
    geo = sub[sub.prop_id.str.contains(r"-(?:lat|long)$")]
    geo.to_csv(ROOT / "data" / "subsample_geo_pairs.csv", index=False)
    print(len(sub), "pairs from", sub.groupby(["prop_id", "comparison"]).ngroups, "templates")
