#!/usr/bin/env python3
"""
Deterministic surface-style metrics for the 8 blinded stories.

Purpose: provide surface style measurements for the manuscript's descriptive
characterisations. On mean sentence length the corpus runs from S_03 (42.5
words) down to S_06 (8.7); S_02 is third at 38.3 but holds the single longest
sentence (200 words) and the most italicised code-switching spans (15). No
single metric orders the corpus by "markedness"; the columns are reported
individually rather than combined into an index.

Metrics per story (from juries/llm/anonymized_stories/S_0x.md — the canonical
Level 2 jury texts, whose S_xx ids match all Level 2/3 result tables):
  words                 whitespace tokens in the body (title line excluded)
  sentences             naive sentence count (split on . ! ? followed by space/EOL)
  mean_words_per_sent   words / sentences
  max_sent_words        longest sentence, in words
  italic_spans          count of *...* emphasis spans in the body
  italic_lexemes        distinct lowercased lexemes inside emphasis spans
                        (proxy for foreign-language interpolation density)

Output: analysis/story_style_metrics.csv  (also printed).
Run from the package/repo root: python3 analysis/story_style_metrics.py
"""

import csv
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STORIES = ROOT / "juries" / "llm" / "anonymized_stories"
OUT = ROOT / "analysis" / "story_style_metrics.csv"

SENT_SPLIT = re.compile(r"[.!?]+(?:[\"'”’)]+)?(?:\s+|$)")
ITALIC = re.compile(r"(?<!\*)\*([^*\n]+?)\*(?!\*)")


def body_of(path: Path) -> str:
    lines = path.read_text(encoding="utf-8").splitlines()
    # drop markdown title/heading lines and horizontal rules
    kept = [l for l in lines if not l.lstrip().startswith("#") and l.strip() != "---"]
    return "\n".join(kept).strip()


def metrics(text: str) -> dict:
    words = text.split()
    sentences = [s for s in SENT_SPLIT.split(text) if s.strip()]
    sent_lens = [len(s.split()) for s in sentences]
    spans = ITALIC.findall(text)
    lexemes = set()
    for span in spans:
        for tok in re.findall(r"[^\W\d_]+(?:[-'’][^\W\d_]+)*", span, re.UNICODE):
            lexemes.add(tok.lower())
    return {
        "words": len(words),
        "sentences": len(sentences),
        "mean_words_per_sent": round(len(words) / max(1, len(sentences)), 1),
        "max_sent_words": max(sent_lens) if sent_lens else 0,
        "italic_spans": len(spans),
        "italic_lexemes": len(lexemes),
    }


def main() -> None:
    rows = []
    for f in sorted(STORIES.glob("S_*.md")):
        story_id = f.stem  # S_02
        m = metrics(body_of(f))
        rows.append({"story_id": story_id, **m})

    with OUT.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    for r in rows:
        print(r)
    print(f"\nWrote {OUT}")


if __name__ == "__main__":
    main()
