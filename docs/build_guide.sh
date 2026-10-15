#!/bin/bash
# Render GUIDE.md as a classic LaTeX article: Computer Modern, wide margins, table of contents.
set -euo pipefail
cd "$(dirname "$0")/.."
tail -n +4 GUIDE.md > docs/guide_body.md
pandoc docs/guide_body.md -o docs/GUIDE.pdf \
  --pdf-engine=xelatex --toc --toc-depth=1 \
  -V documentclass=article -V fontsize=11pt -V papersize=letter \
  -V geometry:"top=1.3in,bottom=1.4in,left=1.6in,right=1.6in" \
  -V linestretch=1.08 -V colorlinks=true -V linkcolor=black -V urlcolor=black -V toccolor=black \
  -V title="The IPHR reproduction: a complete guide" \
  -V author="Shlok Dholakia, Nadia Sumin, Karlo Vrancic, Marc Walden" \
  -V date="CS2881r mini-project, October 2026" \
  -H docs/guide_header.tex
rm docs/guide_body.md
