#!/usr/bin/env python3
"""Voice lint for the report, README and talk script: python3 tools/lint.py <files>.
Flags ', and', em dashes, stock phrases and binary contrasts. Warnings only."""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

BANNED = [
    "delve", "tapestry", "testament to", "navigate the", "navigating the", "leverage", "unlock", "game-changer",
    "game changer", "seamless", "robust", "journey", "in today's", "at the end of the day", "it's worth noting",
    "it is worth noting", "let's dive", "here's the thing", "the reality is", "the truth is", "simply put",
    "in a nutshell", "deep dive", "supercharge", "elevate", "empower", "harness", "unleash", "revolutioniz",
    "cutting-edge", "state-of-the-art", "i'm thrilled", "i'm excited", "excited to share", "humbled", "🧵",
    "a thread", "but here's the catch", "buckle up", "in this thread", "hot take", "unpopular opinion",
]
CONTRAST = [
    r"\bnot (?:just|only|merely|simply|about)\b[^.\n]{0,80}?\bbut\b",
    r"\bisn'?t (?:about|just|only)\b[^.\n]{0,80}",
    r"\bit'?s not [^.\n]{0,60}\.\s*it'?s\b",
    r"\bnot because [^.\n]{0,60}\bbut because\b",
    r"\b(?:this|that), not (?:this|that)\b",
    r"\bless [^.\n]{0,30}, more [^.\n]{0,30}\b",
]
EMDASH = "—"
ENDASH_SPACED = " – "


def check(path: Path):
    text = path.read_text(errors="ignore")
    body = re.sub(r"^---\n.*?\n---\n?", "", text, count=1, flags=re.S)
    low = body.lower()
    warns = []
    n_ca = len(re.findall(r",\s+and\b", body))
    if n_ca:
        warns.append(f"\", and\" x{n_ca} (forbidden)")
    if EMDASH in body:
        warns.append(f"em-dash x{body.count(EMDASH)}")
    if ENDASH_SPACED in body:
        warns.append(f"spaced en-dash x{body.count(ENDASH_SPACED)}")
    for w in BANNED:
        if w in low:
            warns.append(f"banned: '{w}'")
    for pat in CONTRAST:
        for m in re.finditer(pat, body, re.I):
            warns.append(f"binary contrast: '{m.group(0)[:70]}'")
    if re.search(r"^\s*\d+/\s", body, re.M):
        warns.append("thread numbering '1/' present")
    if re.search(r"[\U0001F300-\U0001FAFF☀-➿]", body):
        warns.append("emoji present")
    if path.name.startswith("linkedin") and len(re.findall(r"(?<!\w)#\w+", body)) > 2:
        warns.append("more than two hashtags")
    if re.search(r"^\s*(why|what|how|is|are|do|does|can)\b[^\n]{0,80}\?\s*$", body.split("\n\n")[0].strip(), re.I | re.M):
        warns.append("opens with a rhetorical question")
    one_word_paras = [p for p in body.split("\n\n") if 0 < len(p.split()) <= 2 and not p.startswith("#") and not p.startswith("|")]
    if len(one_word_paras) >= 2:
        warns.append(f"{len(one_word_paras)} one-or-two-word paragraphs (staccato)")
    for m in re.finditer(r"\brather than\b|\binstead of\b", body, re.I):
        warns.append(f"possible contrast: '{body[max(0,m.start()-40):m.end()+30]}'")
    return warns


def main():
    for t in [Path(p) for p in sys.argv[1:]]:
        warns = check(t)
        print(f"lint {t.name}: " + ("clean" if not warns else ""))
        for w in warns:
            print(f"  - {w}")


if __name__ == "__main__":
    main()
