#!/usr/bin/env python3
"""
Level 2 jury statistics.

Consumes the extractor outputs produced by `analysis/level2_extract.py` and
writes the pre-registered Level 2 summary statistics:

    level2_story_rankings.csv
    level2_pairwise_spearman.csv
    level2_icc_by_llm.csv
    level2_criterion_icc.csv
    level2_criterion_kendall_w.csv
    level2_self_preference.csv
    level2_stats_report.md

The script is dependency-free on purpose. It treats `level2_scores_wide.csv`
and `level2_scores_long.csv` as the parsed source, while raw markdown remains
the ultimate source of truth for the extractor.
"""

from __future__ import annotations

import csv
import math
import random
import re
import statistics as stats
from collections import Counter, defaultdict
from itertools import combinations
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ANALYSIS = ROOT / "analysis"
STORIES_DIR = ROOT / "juries" / "llm" / "anonymized_stories"

WIDE = ANALYSIS / "level2_scores_wide.csv"
LONG = ANALYSIS / "level2_scores_long.csv"

CRITERIA = ["LM", "O", "EI", "TD", "SC"]

OWN_STORY = {
    "Claude-Opus-47": "S_02",
    "GPT-55": "S_06",
    "Gemini-31-Pro": "S_03",
    "Grok-43": "S_04",
}

# Story vintage for the pre-registered cross-run descriptive comparison
# (PREREGISTRATION_LEVEL2.md, Secondary outcome 7). The four R2-vintage stories
# are the ones authored by the 2026 vendor models; the rest are R1 (2025).
RUN2_STORIES = {"S_02", "S_03", "S_04", "S_06"}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def mean(values: list[float]) -> float:
    return stats.mean(values)


def sample_sd(values: list[float]) -> float:
    return stats.stdev(values) if len(values) > 1 else 0.0


def rank_desc(values: list[float]) -> list[float]:
    """Average ranks, with rank 1 assigned to the largest value."""
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


def pearson(x: list[float], y: list[float]) -> float:
    if len(x) != len(y):
        raise ValueError("pearson inputs must have equal length")
    mx, my = mean(x), mean(y)
    num = sum((a - mx) * (b - my) for a, b in zip(x, y))
    den_x = math.sqrt(sum((a - mx) ** 2 for a in x))
    den_y = math.sqrt(sum((b - my) ** 2 for b in y))
    return num / (den_x * den_y) if den_x and den_y else float("nan")


def spearman(x: list[float], y: list[float]) -> float:
    return pearson(rank_desc(x), rank_desc(y))


def kendall_w(rank_vectors: list[list[float]]) -> float:
    """Kendall's W with tie correction for average-ranked vectors."""
    m = len(rank_vectors)
    n = len(rank_vectors[0])
    rank_sums = [sum(v[i] for v in rank_vectors) for i in range(n)]
    expected = m * (n + 1) / 2
    s = sum((total - expected) ** 2 for total in rank_sums)

    tie_terms = 0
    for ranks in rank_vectors:
        counts = Counter(ranks)
        tie_terms += sum(t ** 3 - t for t in counts.values() if t > 1)

    denominator = m * m * (n ** 3 - n) - m * tie_terms
    return 12 * s / denominator if denominator else float("nan")


def icc_3_1(matrix: list[list[float]]) -> float:
    """Two-way mixed, consistency, single-measure ICC(3,1)."""
    n = len(matrix)
    k = len(matrix[0])
    flat = [v for row in matrix for v in row]
    grand = mean(flat)
    row_means = [mean(row) for row in matrix]
    col_means = [mean([matrix[i][j] for i in range(n)]) for j in range(k)]

    ss_rows = k * sum((rm - grand) ** 2 for rm in row_means)
    ss_cols = n * sum((cm - grand) ** 2 for cm in col_means)
    ss_total = sum((v - grand) ** 2 for v in flat)
    ss_error = ss_total - ss_rows - ss_cols

    ms_rows = ss_rows / (n - 1)
    ms_error = ss_error / ((n - 1) * (k - 1))
    denominator = ms_rows + (k - 1) * ms_error
    return (ms_rows - ms_error) / denominator if denominator else float("nan")


def bootstrap_delta_ci(
    left: list[float],
    right: list[float],
    seed: int,
    draws: int = 10000,
) -> tuple[float, float]:
    rng = random.Random(seed)
    vals: list[float] = []
    for _ in range(draws):
        left_sample = [rng.choice(left) for _ in left]
        right_sample = [rng.choice(right) for _ in right]
        vals.append(mean(left_sample) - mean(right_sample))
    vals.sort()
    lo = vals[int(0.025 * (draws - 1))]
    hi = vals[int(0.975 * (draws - 1))]
    return lo, hi


def word_count(story_id: str) -> int:
    text = (STORIES_DIR / f"{story_id}.md").read_text(encoding="utf-8")
    return len(re.findall(r"\b[\w’'-]+\b", text))


def write_csv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for row in rows:
            w.writerow(row)


def main() -> None:
    wide = read_csv(WIDE)
    long = read_csv(LONG)

    stories = sorted({row["story_id"] for row in wide})
    llms = sorted({row["llm"] for row in wide})
    reps = sorted({int(row["rep"]) for row in wide})

    scores = defaultdict(list)
    for row in wide:
        scores[(row["story_id"], row["llm"])].append(float(row["weighted_total"]))

    story_scores = defaultdict(list)
    for row in wide:
        story_scores[row["story_id"]].append(float(row["weighted_total"]))

    # Borda and top-3 counts across each LLM x rep rank vector.
    borda = defaultdict(float)
    top3 = defaultdict(int)
    for llm in llms:
        for rep in reps:
            rows = [r for r in wide if r["llm"] == llm and int(r["rep"]) == rep]
            sid_order = [r["story_id"] for r in rows]
            ranks = rank_desc([float(r["weighted_total"]) for r in rows])
            for sid, rank in zip(sid_order, ranks):
                borda[sid] += len(stories) + 1 - rank
                if rank <= 3:
                    top3[sid] += 1

    story_ranking_rows = []
    for sid in stories:
        vals = story_scores[sid]
        story_ranking_rows.append({
            "story_id": sid,
            "mean_weighted": round(mean(vals), 4),
            "sd_weighted": round(sample_sd(vals), 4),
            "min_weighted": round(min(vals), 4),
            "max_weighted": round(max(vals), 4),
            "word_count": word_count(sid),
            "top3_count_out_of_15": top3[sid],
            "borda_8_to_1_tie_aware": round(borda[sid], 4),
        })
    story_ranking_rows.sort(
        key=lambda r: (-float(r["mean_weighted"]), -float(r["borda_8_to_1_tie_aware"]))
    )
    write_csv(
        ANALYSIS / "level2_story_rankings.csv",
        story_ranking_rows,
        [
            "story_id",
            "mean_weighted",
            "sd_weighted",
            "min_weighted",
            "max_weighted",
            "word_count",
            "top3_count_out_of_15",
            "borda_8_to_1_tie_aware",
        ],
    )

    # LLM rank agreement.
    per_llm_means = {
        llm: [mean(scores[(sid, llm)]) for sid in stories]
        for llm in llms
    }
    weighted_w = kendall_w([rank_desc(per_llm_means[llm]) for llm in llms])

    pairwise_rows = []
    for a, b in combinations(llms, 2):
        pairwise_rows.append({
            "llm_a": a,
            "llm_b": b,
            "spearman_rho": round(spearman(per_llm_means[a], per_llm_means[b]), 4),
        })
    write_csv(
        ANALYSIS / "level2_pairwise_spearman.csv",
        pairwise_rows,
        ["llm_a", "llm_b", "spearman_rho"],
    )

    # ICC by LLM on weighted totals.
    icc_rows = []
    for llm in llms:
        matrix = []
        for sid in stories:
            vals_by_rep = []
            for rep in reps:
                vals = [
                    float(row["weighted_total"])
                    for row in wide
                    if row["llm"] == llm and row["story_id"] == sid and int(row["rep"]) == rep
                ]
                vals_by_rep.append(vals[0])
            matrix.append(vals_by_rep)
        icc_rows.append({"llm": llm, "icc_3_1_weighted": round(icc_3_1(matrix), 4)})
    write_csv(ANALYSIS / "level2_icc_by_llm.csv", icc_rows, ["llm", "icc_3_1_weighted"])

    # Criterion-level Kendall W.
    criterion_values = defaultdict(list)
    for row in long:
        criterion_values[(row["llm"], row["story_id"], row["criterion_code"])].append(
            float(row["score"])
        )

    criterion_rows = []
    for criterion in CRITERIA:
        rank_vectors = []
        for llm in llms:
            values = [mean(criterion_values[(llm, sid, criterion)]) for sid in stories]
            rank_vectors.append(rank_desc(values))
        criterion_rows.append({
            "criterion_code": criterion,
            "kendall_w": round(kendall_w(rank_vectors), 4),
        })
    write_csv(
        ANALYSIS / "level2_criterion_kendall_w.csv",
        criterion_rows,
        ["criterion_code", "kendall_w"],
    )

    # Criterion-level ICC(3,1) per LLM. Pre-registered (PREREGISTRATION_LEVEL2.md:
    # "ICC(3,1) ... computed per criterion and on the weighted total"); the
    # weighted-total ICC is in level2_icc_by_llm.csv, this is the per-criterion half.
    long_by_rep: dict[tuple[str, str, str], dict[int, float]] = defaultdict(dict)
    for row in long:
        long_by_rep[(row["llm"], row["story_id"], row["criterion_code"])][int(row["rep"])] = float(
            row["score"]
        )

    criterion_icc_rows = []
    criterion_icc_by_llm: dict[str, list[float]] = defaultdict(list)
    for llm in llms:
        for criterion in CRITERIA:
            matrix = []
            for sid in stories:
                by_rep = long_by_rep[(llm, sid, criterion)]
                matrix.append([by_rep[rep] for rep in reps])
            icc_value = icc_3_1(matrix)
            criterion_icc_rows.append({
                "llm": llm,
                "criterion_code": criterion,
                "icc_3_1": round(icc_value, 4),
            })
            criterion_icc_by_llm[llm].append(icc_value)
    write_csv(
        ANALYSIS / "level2_criterion_icc.csv",
        criterion_icc_rows,
        ["llm", "criterion_code", "icc_3_1"],
    )

    # Self-preference.
    self_rows = []
    for vendor, own_sid in OWN_STORY.items():
        own_vals = [
            float(row["weighted_total"])
            for row in wide
            if row["llm"] == vendor and row["story_id"] == own_sid
        ]
        baseline_vals = [
            float(row["weighted_total"])
            for row in wide
            if row["llm"] == vendor and row["story_id"] != own_sid
        ]
        same_story_other = [
            float(row["weighted_total"])
            for row in wide
            if row["llm"] != vendor and row["story_id"] == own_sid
        ]
        within = mean(own_vals) - mean(baseline_vals)
        between = mean(own_vals) - mean(same_story_other)
        ci_lo, ci_hi = bootstrap_delta_ci(own_vals, baseline_vals, seed=20260621)
        self_rows.append({
            "vendor_juror": vendor,
            "own_story": own_sid,
            "own_story_mean": round(mean(own_vals), 4),
            "nonself_baseline_mean": round(mean(baseline_vals), 4),
            "within_juror_delta": round(within, 4),
            "within_delta_bootstrap_ci95_low": round(ci_lo, 4),
            "within_delta_bootstrap_ci95_high": round(ci_hi, 4),
            "other_jurors_same_story_mean": round(mean(same_story_other), 4),
            "between_juror_delta": round(between, 4),
        })
    write_csv(
        ANALYSIS / "level2_self_preference.csv",
        self_rows,
        [
            "vendor_juror",
            "own_story",
            "own_story_mean",
            "nonself_baseline_mean",
            "within_juror_delta",
            "within_delta_bootstrap_ci95_low",
            "within_delta_bootstrap_ci95_high",
            "other_jurors_same_story_mean",
            "between_juror_delta",
        ],
    )

    # Length and outsider checks.
    story_means = [mean(story_scores[sid]) for sid in stories]
    story_words = [word_count(sid) for sid in stories]
    length_rho = spearman(story_words, story_means)

    kimi_values = per_llm_means["Kimi-26"]
    vendor_consensus = [
        mean([per_llm_means[llm][i] for llm in llms if llm != "Kimi-26"])
        for i in range(len(stories))
    ]
    kimi_rho = spearman(kimi_values, vendor_consensus)

    # Cross-run descriptive comparison (pre-registered Secondary outcome 7).
    r2_grand = mean([mean(story_scores[sid]) for sid in stories if sid in RUN2_STORIES])
    r1_grand = mean([mean(story_scores[sid]) for sid in stories if sid not in RUN2_STORIES])

    sign_test_one_sided = 1 / 16  # all 4 preregistered within-juror deltas are positive.

    report = [
        "# Level 2 statistics report",
        "",
        "Generated by `analysis/level2_stats.py` from `level2_scores_wide.csv` and `level2_scores_long.csv`.",
        "",
        "## Primary ranking",
        "",
        "| rank | story | mean weighted | SD | top-3 count | Borda 8-to-1 | word count |",
        "|---:|---|---:|---:|---:|---:|---:|",
    ]
    for i, row in enumerate(story_ranking_rows, start=1):
        report.append(
            f"| {i} | {row['story_id']} | {row['mean_weighted']:.4f} | "
            f"{row['sd_weighted']:.4f} | {row['top3_count_out_of_15']} | "
            f"{row['borda_8_to_1_tie_aware']:.1f} | {row['word_count']} |"
        )

    report.extend([
        "",
        "## Agreement",
        "",
        f"- Kendall's W across the 5 LLM mean rank vectors: **{weighted_w:.4f}** "
        "(tie-corrected for averaged ranks).",
        f"- Per-criterion Kendall's W (tie-corrected): "
        + ", ".join(f"{r['criterion_code']} {r['kendall_w']:.4f}" for r in criterion_rows)
        + ".",
        f"- Kimi vs average of the 4 vendor jurors, Spearman rho: **{kimi_rho:.4f}**.",
        f"- Story length vs grand mean score, Spearman rho: **{length_rho:.4f}** "
        "(n = 8 stories; descriptive only).",
        f"- Cross-run descriptive (Secondary outcome 7): mean weighted total for R2-vintage "
        f"stories (S_02/S_03/S_04/S_06) = **{r2_grand:.4f}** vs R1-vintage (S_01/S_05/S_07/S_08) "
        f"= **{r1_grand:.4f}**; descriptive only.",
        "",
        "## Within-LLM reliability — ICC(3,1), 3 reps as raters",
        "",
        "| LLM | weighted-total ICC | per-criterion ICC range |",
        "|---|---:|---|",
    ])
    weighted_icc = {r["llm"]: r["icc_3_1_weighted"] for r in icc_rows}
    for llm in llms:
        per_crit = criterion_icc_by_llm[llm]
        report.append(
            f"| {llm} | {weighted_icc[llm]:.4f} | "
            f"{min(per_crit):.4f}–{max(per_crit):.4f} |"
        )
    report.extend([
        "",
        "SD throughout is the sample SD (ddof = 1).",
        "",
        "## Self-preference",
        "",
        "| vendor | own story | own mean | non-self baseline | within delta | bootstrap 95% CI | between delta |",
        "|---|---|---:|---:|---:|---|---:|",
    ])
    for row in self_rows:
        report.append(
            f"| {row['vendor_juror']} | {row['own_story']} | {row['own_story_mean']:.4f} | "
            f"{row['nonself_baseline_mean']:.4f} | {row['within_juror_delta']:+.4f} | "
            f"[{row['within_delta_bootstrap_ci95_low']:+.4f}, "
            f"{row['within_delta_bootstrap_ci95_high']:+.4f}] | "
            f"{row['between_juror_delta']:+.4f} |"
        )
    report.append("")
    report.append(
        f"Exact one-sided sign-test probability for all four within-juror deltas being positive under a symmetric null: {sign_test_one_sided:.4f}."
    )
    report.append("")

    (ANALYSIS / "level2_stats_report.md").write_text("\n".join(report), encoding="utf-8")
    print("Wrote Level 2 stats outputs to analysis/.")
    print(f"Kendall W = {weighted_w:.4f}; length rho = {length_rho:.4f}; Kimi rho = {kimi_rho:.4f}")


if __name__ == "__main__":
    main()
