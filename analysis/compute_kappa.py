#!/usr/bin/env python3
"""Inter-coder reliability (Cohen's kappa) per variable.

Reads the tidy coded data in coding/ (one row per document x variable,
both coders side by side) and writes analysis/kappa_per_variable.csv.

A pair enters the computation when both coders coded the variable —
blank cells and explicit NA markers ("NA", "nan", "none") are treated
as not-coded and skipped, and free-text variables (notes,
named_exemplars_list) are excluded. kappa is undefined when expected
agreement is 1.0 (a single category used by both coders); such
variables are reported with an empty kappa and counted separately.
"""
from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCES = {
    "coding_personas": ROOT / "coding" / "personas.csv",
    "coding_stories": ROOT / "coding" / "stories.csv",
    "coding_reports": ROOT / "coding" / "reports.csv",
}
OUT = ROOT / "analysis" / "kappa_per_variable.csv"
THRESHOLD = 0.70


FREE_TEXT = {"notes", "named_exemplars_list"}

# Tolerate common manual-Excel-entry variants so that 'Yes', 'TRUE', 'y', 1
# all map to one token — otherwise textually-different but semantically
# identical codes would count as disagreements and depress kappa.
BOOL_SYNONYMS = {"yes": "yes", "y": "yes", "true": "yes", "1": "yes",
                 "no": "no", "n": "no", "false": "no", "0": "no"}


def norm(v: str) -> str:
    v = (v or "").strip()
    if v.endswith(".0"):
        v = v[:-2]
    return BOOL_SYNONYMS.get(v.lower(), v)


def is_missing(v: str) -> bool:
    return v.strip().lower() in ("", "na", "nan", "none")


def main() -> None:
    rows_out = []
    n_pub = n_total = n_undef = 0
    for sheet, path in SOURCES.items():
        by_var: dict[str, list[tuple[str, str, str]]] = {}
        with path.open(encoding="utf-8") as f:
            for r in csv.DictReader(f):
                if r["variable"] in FREE_TEXT:
                    continue
                by_var.setdefault(r["variable"], [])  # keep column order even if early docs are NA
                c1, c2 = norm(r["coder1"]), norm(r["coder2"])
                if is_missing(c1) or is_missing(c2):
                    continue
                by_var[r["variable"]].append((r["doc_id"], c1, c2))
        for var, pairs in by_var.items():
            if not pairs:
                continue
            n = len(pairs)
            agree = sum(1 for _, a, b in pairs if a == b)
            po = agree / n
            m1, m2 = Counter(a for _, a, _ in pairs), Counter(b for _, _, b in pairs)
            cats = set(m1) | set(m2)
            pe = sum((m1[c] / n) * (m2[c] / n) for c in cats)
            disagreements = [f"{d}({a} vs {b})" for d, a, b in pairs if a != b]
            if pe >= 1.0:
                kappa, publishable = "", "False"
                n_undef += 1
            else:
                k = (po - pe) / (1 - pe)
                kappa = f"{k}"
                publishable = str(k >= THRESHOLD)
                n_total += 1
                if k >= THRESHOLD:
                    n_pub += 1
            rows_out.append({
                "sheet": sheet, "variable": var, "kappa": kappa,
                "observed_agreement": po, "expected_agreement": pe,
                "n_pairs": n, "n_disagreements": len(disagreements),
                "publishable": publishable,
                "disagreement_docs": "; ".join(disagreements),
            })
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows_out[0].keys()))
        w.writeheader()
        w.writerows(rows_out)
    print(f"{n_pub} of {n_total + n_undef} variables at kappa >= {THRESHOLD} "
          f"({n_undef} kappa-undefined)")
    print(f"wrote {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
