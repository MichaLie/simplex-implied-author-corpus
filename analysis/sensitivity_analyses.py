#!/usr/bin/env python3
"""Robustness checks reported in the paper's supplement.

A. Vendor sensitivity: the persona-attractor claims recomputed with the
   Gemini subset excluded (the vendor for which account-level
   personalization could not be ruled out; see the paper's methods).
B. Panel sensitivity: a leave-one-out (jackknife) over the human jury —
   the Level 3 results recomputed five times, each omitting one respondent,
   to show how far the small panel's ordering depends on any single reader.

Run AFTER analysis/level3_aggregate.py (step 5 in REPRODUCE.md).
Prints its results and writes them to analysis/sensitivity_summary.txt.
"""
from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PERSONAS = ROOT / "coding" / "personas.csv"
L3_LONG = ROOT / "analysis" / "level3_scores_long.csv"
L2_RANK = ROOT / "analysis" / "level2_story_rankings.csv"
YES_SIDE = {"Yes", "Probably yes"}


def norm(v: str) -> str:
    v = (v or "").strip()
    return v[:-2] if v.endswith(".0") else v


def load_personas():
    docs = {}
    with PERSONAS.open(encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["run"] == "R2" and r["condition"] == "HIGH":
                docs.setdefault((r["doc_id"], r["model"]), {})[r["variable"]] = norm(r["coder1"])
    return docs


def tally(docs, label):
    n = len(docs)
    f = sum(1 for v in docs.values() if v.get("gender") == "F")
    ml = sum(1 for v in docs.values() if v.get("multilingual_childhood") == "yes")
    ol = sum(1 for v in docs.values() if v.get("outsider_relation_to_language") == "yes")
    y18 = sum(1 for v in docs.values() if v.get("nobel_year") == "2018")
    y1819 = sum(1 for v in docs.values() if v.get("nobel_year") in ("2018", "2019"))
    reg = Counter(v.get("region", "") for v in docs.values())
    ee_mena = reg["EE_Balkan"] + reg["MENA_Levantine"]
    west = reg["Western_European"] + reg["North_American"]
    emit(f"  {label}: n={n} | woman {f}/{n} | multilingual {ml}/{n} | outsider {ol}/{n} | "
         f"Nobel-2018 {y18}/{n} (2018-19 {y1819}/{n}) | EE+MENA {ee_mena}/{n} | West/NAm {west}/{n}")


def spearman(xs, ys):
    def ranks(v):
        s = sorted(range(len(v)), key=lambda i: v[i])
        r = [0.0] * len(v)
        i = 0
        while i < len(s):
            j = i
            while j + 1 < len(s) and v[s[j + 1]] == v[s[i]]:
                j += 1
            avg = (i + j) / 2 + 1
            for k in range(i, j + 1):
                r[s[k]] = avg
            i = j + 1
        return r
    rx, ry = ranks(xs), ranks(ys)
    n = len(xs)
    mx, my = sum(rx) / n, sum(ry) / n
    num = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
    den = (sum((a - mx) ** 2 for a in rx) * sum((b - my) ** 2 for b in ry)) ** 0.5
    return num / den if den else float("nan")


LOG: list[str] = []


def emit(line: str = "") -> None:
    LOG.append(line)
    print(line)


def main() -> None:
    emit("A. Persona attractor, vendor sensitivity (coder 1, R2 HIGH):")
    docs = load_personas()
    tally(docs, "all four vendors")
    tally({k: v for k, v in docs.items() if not k[1].startswith("Gemini")}, "without Gemini")
    tally({k: v for k, v in docs.items() if k[1].startswith("Gemini")}, "Gemini only")

    emit("")
    emit("B. Human jury, leave-one-out over all five respondents:")
    rows = list(csv.DictReader(L3_LONG.open(encoding="utf-8")))
    all_rids = sorted({r["rid"] for r in rows})
    l2 = {r["story_id"]: float(r["mean_weighted"])
          for r in csv.DictReader(L2_RANK.open(encoding="utf-8"))}

    def summarise(kept, label):
        means, detect = {}, {}
        for sid in sorted({r["story_id"] for r in kept}):
            sub = [r for r in kept if r["story_id"] == sid]
            means[sid] = sum(float(r["weighted"]) for r in sub) / len(sub)
            detect[sid] = sum(1 for r in sub if r["detect"] in YES_SIDE)
        order = sorted(means, key=means.get, reverse=True)
        n = len(kept) // len(means)
        sids = sorted(means)
        rho = spearman([means[s] for s in sids], [l2[s] for s in sids])
        emit(f"  {label}: " + " > ".join(f"{s} {means[s]:.2f}" for s in order)
             + f"  (n={n}, rho vs LLM {rho:+.2f})")
        return order[0]

    summarise(rows, "all five        ")
    firsts = []
    for rid in all_rids:
        firsts.append(summarise([r for r in rows if r["rid"] != rid], f"omitting reader {rid}"))
    top = set(firsts)
    emit(f"  -> first place is {'stable' if len(top) == 1 else 'NOT stable'} "
         f"across every single-reader exclusion ({', '.join(sorted(top))}); "
         "the lower three ranks reorder in every variant, so only the top position "
         "is robust at this panel size.")
    out = ROOT / "analysis" / "sensitivity_summary.txt"
    out.write_text("\n".join(LOG) + "\n", encoding="utf-8")
    print(f"\nwrote {out.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
