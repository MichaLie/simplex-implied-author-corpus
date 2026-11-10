#!/usr/bin/env python3
"""
level3_aggregate.py — Level 3 human-expert jury aggregation + comparison to the
Level 2 LLM jury.

Reads the anonymized form export (juries/human/responses_anonymized.csv),
de-blinds Story A/B/C/D -> canonical S_XX via the internal story key, computes per-story human
weighted means (using the same 5-criterion weights as Level 2), and lines them up against the
LLM jury means in analysis/level2_summary.csv.

Two stories get a closer look:
  - Story D = S_04 (Grok 4.3): LLM-jury self-preference probe. Does the human panel side with
    the 4-juror LLM consensus (low) or with Grok's own 8.33 (high)?
  - Story C = S_07 (Opus 4): LLM jury was lukewarm/divided. Do humans rank it higher?

Outputs (analysis/):
  level3_scores_long.csv   one row per respondent x story x criterion
  level3_summary.csv       per-story human mean/SD/range/weighted + LLM weighted + delta + CI
  level3_alignment.csv     human-rater x LLM-juror rank correlations
  level3_criterion_comparison.csv
  level3_editorial_detection.csv
  (also prints a full report to stdout)

stdlib only.
"""

import csv
import random
import statistics as stats
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RESP = ROOT / "juries" / "human" / "responses_anonymized.csv"
L2 = ROOT / "analysis" / "level2_summary.csv"
L2_LONG = ROOT / "analysis" / "level2_scores_long.csv"
OUT_LONG = ROOT / "analysis" / "level3_scores_long.csv"
OUT_SUMMARY = ROOT / "analysis" / "level3_summary.csv"
OUT_ALIGNMENT = ROOT / "analysis" / "level3_alignment.csv"
OUT_CRITERION = ROOT / "analysis" / "level3_criterion_comparison.csv"
OUT_ED_DETECT = ROOT / "analysis" / "level3_editorial_detection.csv"

# --- rubric (identical to Level 2) -----------------------------------------
CRITERIA = ["Literary Merit", "Originality", "Emotional Impact",
            "Thematic Depth", "Structural Craft"]
WEIGHTS = {"Literary Merit": 0.30, "Originality": 0.25, "Emotional Impact": 0.20,
           "Thematic Depth": 0.15, "Structural Craft": 0.10}

# --- de-blinding (the internal story key, seed 100) -----------------------------
LABELS = ["A", "B", "C", "D"]
KEY = {
    "A": {"sid": "S_02", "gen": "Opus 4.7", "run": "R2"},
    "B": {"sid": "S_06", "gen": "GPT-5.5",  "run": "R2"},
    "C": {"sid": "S_07", "gen": "Opus 4",   "run": "R1"},
    "D": {"sid": "S_04", "gen": "Grok 4.3", "run": "R2"},
}

# --- CSV column layout (0-indexed, verified against header) -----------------
COL_META = {"category": 1, "language": 2}
# per label: 5 criteria cols, then journal-decision, ai-detection, reflection
COL = {
    "A": {"crit": [3, 4, 5, 6, 7],      "journal": 8,  "detect": 9,  "reflect": 10},
    "B": {"crit": [11, 12, 13, 14, 15], "journal": 16, "detect": 17, "reflect": 18},
    "C": {"crit": [19, 20, 21, 22, 23], "journal": 24, "detect": 25, "reflect": 26},
    "D": {"crit": [27, 28, 29, 30, 31], "journal": 32, "detect": 33, "reflect": 34},
}

EXPECTED_HEADER_STARTS = {
    0: "Timestamp",
    1: "You are:",
    2: "Your primary working language",
    3: "Story A — Literary Merit",
    4: "Story A — Originality",
    5: "Story A — Emotional Impact",
    6: "Story A — Thematic Depth",
    7: "Story A — Structural Craft",
    11: "Story B — Literary Merit",
    19: "Story C — Literary Merit",
    27: "Story D — Literary Merit",
}


def validate_header(header):
    if len(header) < 35:
        raise ValueError(f"Expected at least 35 columns in form export; found {len(header)}")
    for idx, expected in EXPECTED_HEADER_STARTS.items():
        if not header[idx].startswith(expected):
            raise ValueError(
                f"Unexpected column {idx}: {header[idx]!r}; expected prefix {expected!r}"
            )


def parse_score(value, respondent_id, label, criterion):
    stripped = value.strip()
    if stripped == "":
        return None
    as_float = float(stripped)
    if not as_float.is_integer():
        raise ValueError(
            f"Non-integer score for respondent {respondent_id}, Story {label}, "
            f"{criterion}: {value!r}"
        )
    score = int(as_float)
    if not (1 <= score <= 10):
        raise ValueError(
            f"Out-of-range score for respondent {respondent_id}, Story {label}, "
            f"{criterion}: {score}"
        )
    return score


def weighted(score_by_crit):
    return round(sum(score_by_crit[c] * WEIGHTS[c] for c in CRITERIA), 4)


def sample_sd(values):
    return round(stats.stdev(values), 4) if len(values) > 1 else 0.0


def bootstrap_ci(values, seed, draws=10000):
    rng = random.Random(seed)
    boot = []
    for _ in range(draws):
        sample = [rng.choice(values) for _ in values]
        boot.append(stats.mean(sample))
    boot.sort()
    lo = boot[int(0.025 * (draws - 1))]
    hi = boot[int(0.975 * (draws - 1))]
    return round(lo, 4), round(hi, 4)


def rank_desc(values):
    indexed = sorted(enumerate(values), key=lambda item: (-item[1], item[0]))
    ranks = [0.0] * len(values)
    i = 0
    while i < len(indexed):
        j = i + 1
        while j < len(indexed) and indexed[j][1] == indexed[i][1]:
            j += 1
        avg_rank = (i + 1 + j) / 2
        for original_idx, _value in indexed[i:j]:
            ranks[original_idx] = avg_rank
        i = j
    return ranks


def pearson(a, b):
    ma, mb = stats.mean(a), stats.mean(b)
    num = sum((x - ma) * (y - mb) for x, y in zip(a, b))
    da = sum((x - ma) ** 2 for x in a) ** 0.5
    db = sum((y - mb) ** 2 for y in b) ** 0.5
    return num / (da * db) if da and db else 0.0


def load_human():
    rows = []
    with open(RESP, newline="", encoding="utf-8-sig") as f:
        r = csv.reader(f)
        header = next(r)
        validate_header(header)
        for i, raw in enumerate(r):
            if not any(raw):
                continue
            rid = i + 1
            resp = {"rid": i + 1, "timestamp": raw[0],
                    "category": raw[COL_META["category"]],
                    "language": raw[COL_META["language"]],
                    "stories": {}}
            for lab in LABELS:
                c = COL[lab]
                sbc = {}
                ok = True
                for crit, idx in zip(CRITERIA, c["crit"]):
                    score = parse_score(raw[idx], rid, lab, crit)
                    if score is None:
                        ok = False
                        break
                    sbc[crit] = score
                resp["stories"][lab] = {
                    "ok": ok,
                    "by_crit": sbc,
                    "weighted": weighted(sbc) if ok else None,
                    "journal": raw[c["journal"]].strip(),
                    "detect": raw[c["detect"]].strip(),
                    "reflect": raw[c["reflect"]].strip(),
                }
            rows.append(resp)
    return header, rows


def load_llm():
    """Per-story LLM weighted means: {sid: {'ALL': x, 'jurors': {juror: x}}}."""
    out = {}
    with open(L2, newline="") as f:
        for row in csv.DictReader(f):
            sid = row["story_id"]
            out.setdefault(sid, {"jurors": {}})
            mw = float(row["mean_weighted"])
            if row["llm"] == "*ALL*":
                out[sid]["ALL"] = mw
            else:
                out[sid]["jurors"][row["llm"]] = mw
    return out


def load_llm_criteria():
    """Per-story LLM criterion means: {sid: {criterion: mean_score}}."""
    buckets = {}
    with open(L2_LONG, newline="") as f:
        for row in csv.DictReader(f):
            sid = row["story_id"]
            criterion = row["criterion"]
            buckets.setdefault(sid, {}).setdefault(criterion, []).append(float(row["score"]))
    return {
        sid: {criterion: round(stats.mean(vals), 4) for criterion, vals in criteria.items()}
        for sid, criteria in buckets.items()
    }


def spearman(a, b):
    """Spearman rho using average ranks, robust to ties."""
    return round(pearson(rank_desc(a), rank_desc(b)), 4)


def kendall_tau(a, b):
    n = len(a)
    conc = disc = 0
    for i in range(n):
        for j in range(i + 1, n):
            s = (a[i] - a[j]) * (b[i] - b[j])
            if s > 0:
                conc += 1
            elif s < 0:
                disc += 1
    return round((conc - disc) / (conc + disc), 4) if (conc + disc) else 0.0


def fmt(x, nd=2):
    return "—" if x is None else f"{x:.{nd}f}"


def main():
    header, humans = load_human()
    llm = load_llm()
    llm_criteria = load_llm_criteria()
    n = len(humans)

    # ---- per-story human aggregation -------------------------------------
    summary = {}
    for lab in LABELS:
        sid = KEY[lab]["sid"]
        weights = [h["stories"][lab]["weighted"] for h in humans
                   if h["stories"][lab]["ok"]]
        per_crit = {c: [h["stories"][lab]["by_crit"][c] for h in humans
                        if h["stories"][lab]["ok"]] for c in CRITERIA}
        journals = [h["stories"][lab]["journal"] for h in humans]
        detects = [h["stories"][lab]["detect"] for h in humans]
        ci_low, ci_high = bootstrap_ci(weights, seed=20260621 + ord(lab))
        summary[lab] = {
            "sid": sid, "gen": KEY[lab]["gen"], "run": KEY[lab]["run"],
            "n": len(weights),
            "h_mean": round(stats.mean(weights), 4),
            "h_sd": sample_sd(weights),
            "h_ci_low": ci_low, "h_ci_high": ci_high,
            "h_min": min(weights), "h_max": max(weights),
            "per_crit_mean": {c: round(stats.mean(per_crit[c]), 2) for c in CRITERIA},
            "journals": journals, "detects": detects,
            "weights": weights,
            "llm_all": llm[sid]["ALL"],
            "llm_jurors": llm[sid]["jurors"],
        }

    # ---- write long + summary CSVs ---------------------------------------
    with open(OUT_LONG, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["rid", "category", "language", "label", "story_id",
                    "generator"] + CRITERIA + ["weighted", "journal", "detect"])
        for h in humans:
            for lab in LABELS:
                s = h["stories"][lab]
                if not s["ok"]:
                    continue
                w.writerow([h["rid"], h["category"], h["language"], lab,
                            KEY[lab]["sid"], KEY[lab]["gen"]] +
                           [s["by_crit"][c] for c in CRITERIA] +
                           [s["weighted"], s["journal"], s["detect"]])

    with open(OUT_SUMMARY, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["label", "story_id", "generator", "run", "n",
                    "human_mean_weighted", "human_sd", "human_min", "human_max",
                    "human_bootstrap_ci95_low", "human_bootstrap_ci95_high",
                    "llm_mean_weighted", "human_minus_llm",
                    "human_minus_llm_ci95_low", "human_minus_llm_ci95_high"])
        for lab in LABELS:
            s = summary[lab]
            w.writerow([lab, s["sid"], s["gen"], s["run"], s["n"],
                        s["h_mean"], s["h_sd"], s["h_min"], s["h_max"],
                        s["h_ci_low"], s["h_ci_high"],
                        s["llm_all"], round(s["h_mean"] - s["llm_all"], 4),
                        round(s["h_ci_low"] - s["llm_all"], 4),
                        round(s["h_ci_high"] - s["llm_all"], 4)])

    with open(OUT_ALIGNMENT, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["rid", "category", "language", "llm_juror", "spearman_rho_4_stories"])
        for h in humans:
            human_scores = [h["stories"][lab]["weighted"] for lab in LABELS]
            for juror in sorted(next(iter(llm.values()))["jurors"]):
                llm_scores = [summary[lab]["llm_jurors"][juror] for lab in LABELS]
                w.writerow([
                    h["rid"], h["category"], h["language"], juror,
                    spearman(human_scores, llm_scores),
                ])

    with open(OUT_CRITERION, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["label", "story_id", "criterion", "human_mean", "llm_mean", "human_minus_llm"])
        for lab in LABELS:
            sid = summary[lab]["sid"]
            for criterion in CRITERIA:
                h_mean = summary[lab]["per_crit_mean"][criterion]
                l_mean = llm_criteria[sid][criterion]
                w.writerow([lab, sid, criterion, h_mean, l_mean, round(h_mean - l_mean, 4)])

    with open(OUT_ED_DETECT, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["label", "story_id", "field", "response", "count", "proportion"])
        for lab in LABELS:
            s = summary[lab]
            for field, values in [("journal", s["journals"]), ("detect", s["detects"])]:
                counts = Counter(values)
                for response, count in sorted(counts.items()):
                    w.writerow([lab, s["sid"], field, response, count, round(count / len(values), 4)])

    # ---- report ----------------------------------------------------------
    print(f"\nLEVEL 3 HUMAN-EXPERT JURY  (n = {n} respondents)\n" + "=" * 78)
    print("Respondents:")
    for h in humans:
        print(f"  R{h['rid']}: {h['category'][:45]:45s} | {h['language']:8s}")

    print("\nPER-STORY: human weighted mean vs LLM jury weighted mean")
    print("-" * 78)
    print(f"{'Lab':3} {'StoryID':7} {'Generator':9} {'n':>2} "
          f"{'HUMAN':>6} {'SD':>5} {'95% CI':>13} {'LLM':>6} {'H–LLM':>7}")
    for lab in LABELS:
        s = summary[lab]
        ci = f"{fmt(s['h_ci_low'])}-{fmt(s['h_ci_high'])}"
        print(f"{lab:3} {s['sid']:7} {s['gen']:9} {s['n']:>2} "
              f"{fmt(s['h_mean']):>6} {fmt(s['h_sd']):>5} {ci:>13} "
              f"{fmt(s['llm_all']):>6} {s['h_mean']-s['llm_all']:>+7.2f}")

    # rankings (restricted to the 4 L3 stories)
    h_rank = sorted(LABELS, key=lambda l: summary[l]["h_mean"], reverse=True)
    l_rank = sorted(LABELS, key=lambda l: summary[l]["llm_all"], reverse=True)
    print("\nRANKING of the 4 stories (best -> worst):")
    print("  HUMAN: " + " > ".join(f"{l}/{summary[l]['sid']}({fmt(summary[l]['h_mean'])})" for l in h_rank))
    print("  LLM  : " + " > ".join(f"{l}/{summary[l]['sid']}({fmt(summary[l]['llm_all'])})" for l in l_rank))

    h_vals = [summary[l]["h_mean"] for l in LABELS]
    l_vals = [summary[l]["llm_all"] for l in LABELS]
    print(f"\n  Spearman rho (human vs LLM, n=4) = {spearman(h_vals, l_vals)}"
          f"   Kendall tau = {kendall_tau(h_vals, l_vals)}   [n=4: directional only]")
    top3_labels = ["A", "B", "C"]
    h_top3 = [summary[l]["h_mean"] for l in top3_labels]
    l_top3 = [summary[l]["llm_all"] for l in top3_labels]
    print(f"  Top-3-only Kendall tau (A/B/C) = {kendall_tau(h_top3, l_top3)}"
          "   [pre-addendum L3-1; n=3 directional only]")

    # ---- per-criterion table ---------------------------------------------
    print("\nPER-CRITERION human means")
    print("-" * 78)
    print(f"{'Lab/Story':14} " + " ".join(f"{c[:9]:>9}" for c in CRITERIA))
    for lab in LABELS:
        s = summary[lab]
        print(f"{lab+'/'+s['sid']:14} " +
              " ".join(f"{fmt(s['per_crit_mean'][c]):>9}" for c in CRITERIA))

    # ---- editorial verdict + AI-detection ---------------------------------
    print("\nEDITORIAL VERDICT (journal accept/revise/reject) & AI-DETECTION")
    print("-" * 78)
    for lab in LABELS:
        s = summary[lab]
        print(f"{lab}/{s['sid']}:")
        print(f"    journal : {s['journals']}")
        print(f"    detect  : {s['detects']}")

    # ---- the two diagnostics ---------------------------------------------
    print("\n" + "=" * 78)
    print("DIAGNOSTIC 1 — Story D = S_04 (Grok 4.3): self-preference probe")
    print("-" * 78)
    d = summary["D"]
    jur = d["llm_jurors"]
    consensus = [v for k, v in jur.items() if k != "Grok-43"]
    print(f"  Human panel (n={d['n']}):          mean {fmt(d['h_mean'])}  "
          f"(bootstrap 95% CI {fmt(d['h_ci_low'])}-{fmt(d['h_ci_high'])})")
    print(f"  Grok-43 (the generator):     {fmt(jur.get('Grok-43'))}")
    print(f"  LLM consensus excl. Grok:    {fmt(stats.mean(consensus))}  ({', '.join(f'{k}={fmt(v)}' for k,v in jur.items() if k!='Grok-43')})")
    print(f"  Full LLM jury (incl Grok):   {fmt(d['llm_all'])}")
    verdict = ("side with the 4-juror CONSENSUS (low) -> Grok's 8.33 reads as SELF-PREFERENCE"
               if abs(d["h_mean"] - stats.mean(consensus)) < abs(d["h_mean"] - jur.get("Grok-43", 99))
               else "side with GROK (high) -> the LLM consensus, not Grok, was the outlier")
    print(f"  => Humans {verdict}")

    print("\nDIAGNOSTIC 2 — Story C = S_07 (Opus 4): LLM-jury underdog / divergence")
    print("-" * 78)
    c = summary["C"]
    print(f"  Human panel (n={c['n']}):          mean {fmt(c['h_mean'])}  "
          f"(bootstrap 95% CI {fmt(c['h_ci_low'])}-{fmt(c['h_ci_high'])})")
    print(f"  LLM jury:                    {fmt(c['llm_all'])}  (internally split: {', '.join(f'{k}={fmt(v)}' for k,v in c['llm_jurors'].items())})")
    print(f"  Human rank of S_07: #{h_rank.index('C')+1} of 4    LLM rank of S_07: #{l_rank.index('C')+1} of 4")
    print(f"  H–LLM delta: {c['h_mean']-c['llm_all']:+.2f}")

    print(f"\nwrote {OUT_LONG.name}, {OUT_SUMMARY.name}, "
          f"{OUT_ALIGNMENT.name}, {OUT_CRITERION.name}, {OUT_ED_DETECT.name}")


if __name__ == "__main__":
    main()
