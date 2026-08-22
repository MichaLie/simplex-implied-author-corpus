"""
Figure 8 — Level 3 human-expert jury vs Level 2 LLM jury.

Standalone (does not modify build_figures.py); reuses the same publication style and
vendor palette. Reads:
    analysis/level2_summary.csv      (LLM per-juror + *ALL* weighted means)
    analysis/level3_scores_long.csv  (one row per human respondent x story; written by
                                       analysis/level3_aggregate.py)

Outputs figures/fig8_human_vs_llm.png at 300 DPI.

Four panels:
    A  per-story weighted means: human panel vs LLM jury (dumbbell, shows the divergence)
    B  full distribution overlay: 5 human scores + 5 LLM-juror means per story
    C  per-criterion human profile (the human favourite S_07 leads on every criterion)
    D  AI-detection: could the experts tell each story was machine-written?
"""

from __future__ import annotations

import csv
import statistics as stats
from collections import Counter, defaultdict
from pathlib import Path

import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "figures"

plt.rcParams.update({
    "font.family": "sans-serif",
    "font.size": 10,
    "axes.titlesize": 11,
    "axes.labelsize": 10,
    "xtick.labelsize": 9,
    "ytick.labelsize": 9,
    "legend.fontsize": 8.5,
    "savefig.dpi": 300,
    "savefig.bbox": "tight",
    "axes.spines.top": False,
    "axes.spines.right": False,
})

VENDOR_COLOURS = {
    "Claude-Opus-47": "#D97757",
    "GPT-55":         "#7AAE7A",
    "Gemini-31-Pro":  "#5B8FB9",
    "Grok-43":        "#9C7AB5",
    "Kimi-26":        "#7E7E7E",
}
VENDOR_LABELS = {
    "Claude-Opus-47": "Claude Opus 4.7",
    "GPT-55":         "GPT-5.5",
    "Gemini-31-Pro":  "Gemini 3.1 Pro",
    "Grok-43":        "Grok 4.3",
    "Kimi-26":        "Kimi 2.6 (outsider)",
}

HUMAN_COLOUR = "#C04A2F"   # deep red-orange — the human panel
LLM_COLOUR = "#2E6FA0"     # deep blue — the LLM jury (aggregate)

CRITERIA = ["Literary Merit", "Originality", "Emotional Impact",
            "Thematic Depth", "Structural Craft"]
CRIT_ABBR = ["Literary\nMerit", "Originality", "Emotional\nImpact",
             "Thematic\nDepth", "Structural\nCraft"]

# The 4 Level-3 stories, ordered by LLM-jury rank (best first) so the human
# divergence reads left-to-right / top-to-bottom.
STORIES = [
    ("S_06", "Story B", "The Drawer for Returned Names", "GPT-5.5", "2026"),
    ("S_02", "Story A", "Birthälm, in November",        "Opus 4.7", "2026"),
    ("S_07", "Story C", "The Translator's Hands",        "Opus 4",   "2025"),
    ("S_04", "Story D", "The Verb That Refused to Conjugate", "Grok 4.3", "2026"),
]
SID_ORDER = [s[0] for s in STORIES]

DETECT_ORDER = ["No", "Probably no", "Uncertain", "Probably yes", "Yes"]
DETECT_COLOURS = {
    "No":           "#4C9A6B",   # green = evaded detection (read as human)
    "Probably no":  "#A6CFA0",
    "Uncertain":    "#DCD6C8",   # neutral
    "Probably yes": "#E0A06A",
    "Yes":          "#C04A2F",   # red = caught as machine
}


def load_llm():
    """{sid: {'ALL': x, 'jurors': {juror: x}}}."""
    out = {}
    with open(ROOT / "analysis" / "level2_summary.csv", newline="") as f:
        for row in csv.DictReader(f):
            sid = row["story_id"]
            out.setdefault(sid, {"jurors": {}})
            mw = float(row["mean_weighted"])
            if row["llm"] == "*ALL*":
                out[sid]["ALL"] = mw
            else:
                out[sid]["jurors"][row["llm"]] = mw
    return out


def load_human():
    """Returns per-sid lists of weighted scores, per-criterion lists, detect lists."""
    weighted = defaultdict(list)
    per_crit = defaultdict(lambda: defaultdict(list))
    detect = defaultdict(list)
    with open(ROOT / "analysis" / "level3_scores_long.csv", newline="") as f:
        for row in csv.DictReader(f):
            sid = row["story_id"]
            weighted[sid].append(float(row["weighted"]))
            for c in CRITERIA:
                per_crit[sid][c].append(int(float(row[c])))
            detect[sid].append(row["detect"].strip())
    return weighted, per_crit, detect


def main():
    llm = load_llm()
    h_weighted, h_crit, h_detect = load_human()
    n_human = len(next(iter(h_weighted.values())))

    fig, axes = plt.subplots(2, 2, figsize=(13.2, 10.4))
    axA, axB, axC, axD = axes[0, 0], axes[0, 1], axes[1, 0], axes[1, 1]

    ylabels = [f"{lab} · {sid}\n{gen} ({yr})" for sid, lab, _, gen, yr in STORIES]

    # ---------------------------------------------------------------
    # PANEL A — dumbbell: human mean vs LLM mean per story
    # ---------------------------------------------------------------
    y = np.arange(len(STORIES))[::-1]   # first story at top
    for yi, (sid, *_rest) in zip(y, STORIES):
        h = stats.mean(h_weighted[sid])
        l = llm[sid]["ALL"]
        axA.plot([l, h], [yi, yi], color="#BBB", linewidth=2.2, zorder=1)
        axA.scatter(l, yi, color=LLM_COLOUR, s=130, zorder=3,
                    edgecolor="#222", linewidth=0.6)
        axA.scatter(h, yi, color=HUMAN_COLOUR, s=130, zorder=3,
                    edgecolor="#222", linewidth=0.6)
        gap = h - l
        midx = (h + l) / 2
        axA.annotate(f"{gap:+.1f}", xy=(midx, yi + 0.16), ha="center",
                     fontsize=9, fontweight="bold", color="#555")
        axA.annotate(f"{l:.1f}", xy=(l, yi - 0.24), ha="center", fontsize=8, color=LLM_COLOUR)
        axA.annotate(f"{h:.1f}", xy=(h, yi - 0.24), ha="center", fontsize=8, color=HUMAN_COLOUR)

    axA.set_yticks(y)
    axA.set_yticklabels(ylabels)
    axA.set_xlim(1, 10)
    axA.set_xlabel("Weighted score (1–10)")
    axA.set_title("A. Per-story consensus: human panel vs LLM jury", loc="left", fontweight="bold")
    axA.legend(handles=[
        mpatches.Patch(color=LLM_COLOUR, label="LLM jury (5 jurors × 3 reps)"),
        mpatches.Patch(color=HUMAN_COLOUR, label=f"Human experts (n={n_human})"),
    ], loc="lower right", frameon=False)
    axA.text(0.01, 0.02,
             "Spearman ρ(human, LLM) = 0.0 across the 4 stories",
             transform=axA.transAxes, fontsize=8, style="italic", color="#777")

    # ---------------------------------------------------------------
    # PANEL B — full distribution overlay
    # ---------------------------------------------------------------
    x = np.arange(len(STORIES))
    rng = np.random.default_rng(42)
    for xi, (sid, *_rest) in zip(x, STORIES):
        # human cloud (left sub-slot)
        hx = xi - 0.20 + rng.uniform(-0.05, 0.05, n_human)
        hy = h_weighted[sid]
        axB.scatter(hx, hy, color=HUMAN_COLOUR, s=46, alpha=0.85,
                    edgecolor="#222", linewidth=0.4, zorder=3)
        axB.hlines(stats.mean(hy), xi - 0.32, xi - 0.08, color=HUMAN_COLOUR,
                   linewidth=2.4, zorder=4)
        # LLM-juror cloud (right sub-slot), coloured by vendor
        for k, (juror, val) in enumerate(llm[sid]["jurors"].items()):
            jx = xi + 0.20 + (k - 2) * 0.035
            axB.scatter(jx, val, color=VENDOR_COLOURS[juror], s=58, alpha=0.9,
                        edgecolor="#222", linewidth=0.4, zorder=3,
                        marker="D")
        axB.hlines(llm[sid]["ALL"], xi + 0.08, xi + 0.32, color="#222",
                   linewidth=2.4, zorder=4)

    # annotate Grok's self-preference outlier on S_04
    s04_i = SID_ORDER.index("S_04")
    grok_s04 = llm["S_04"]["jurors"]["Grok-43"]
    axB.annotate("Grok rates\nits own story", xy=(s04_i + 0.27, grok_s04),
                 xytext=(s04_i - 0.15, 9.2), fontsize=7.5, color=VENDOR_COLOURS["Grok-43"],
                 ha="center", arrowprops=dict(arrowstyle="->", color=VENDOR_COLOURS["Grok-43"], lw=0.8))

    axB.set_xticks(x)
    axB.set_xticklabels([f"{lab}\n{sid}" for sid, lab, *_ in STORIES])
    axB.set_ylim(0, 10)
    axB.set_ylabel("Weighted score (1–10)")
    axB.set_title("B. Full distribution: every human and every LLM juror", loc="left", fontweight="bold")
    handles = [mpatches.Patch(color=HUMAN_COLOUR, label=f"Human experts (n={n_human})")]
    handles += [plt.Line2D([], [], marker="D", linestyle="", markersize=7,
                           markerfacecolor=VENDOR_COLOURS[j], markeredgecolor="#222",
                           label=VENDOR_LABELS[j]) for j in VENDOR_COLOURS]
    axB.legend(handles=handles, loc="lower left", frameon=False, ncol=2, fontsize=7.5)

    # ---------------------------------------------------------------
    # PANEL C — per-criterion human profile (line per story)
    # ---------------------------------------------------------------
    xc = np.arange(len(CRITERIA))
    story_line_colour = {
        "S_06": "#7AAE7A", "S_02": "#D97757", "S_07": "#2E6FA0", "S_04": "#9C7AB5",
    }
    for sid, lab, _t, gen, yr in STORIES:
        means = [stats.mean(h_crit[sid][c]) for c in CRITERIA]
        lw = 3.0 if sid == "S_07" else 1.6
        axC.plot(xc, means, marker="o", markersize=6, linewidth=lw,
                 color=story_line_colour[sid],
                 label=f"{lab} · {sid} ({gen})", zorder=3 if sid == "S_07" else 2)
    axC.set_xticks(xc)
    axC.set_xticklabels(CRIT_ABBR)
    axC.set_ylim(1, 9)
    axC.set_ylabel("Mean human score (1–10)")
    axC.set_title("C. Human per-criterion profile (S_07 leads on every criterion)", loc="left", fontweight="bold")
    axC.legend(loc="upper right", frameon=False, fontsize=8)
    axC.grid(axis="y", linewidth=0.4, color="#EEE")

    # ---------------------------------------------------------------
    # PANEL D — AI-detection (stacked horizontal bars)
    # ---------------------------------------------------------------
    yd = np.arange(len(STORIES))[::-1]
    for yi, (sid, lab, *_rest) in zip(yd, STORIES):
        counts = Counter(h_detect[sid])
        left = 0
        for cat in DETECT_ORDER:
            c = counts.get(cat, 0)
            if c == 0:
                continue
            axD.barh(yi, c, left=left, color=DETECT_COLOURS[cat],
                     edgecolor="white", linewidth=1.0)
            axD.text(left + c / 2, yi, str(c), ha="center", va="center",
                     fontsize=9, fontweight="bold",
                     color="white" if cat in ("No", "Yes") else "#333")
            left += c
    axD.set_yticks(yd)
    axD.set_yticklabels([f"{lab} · {sid}" for sid, lab, *_ in STORIES])
    axD.set_xlim(0, n_human)
    axD.set_xlabel(f"Experts (n={n_human})")
    axD.set_title('D. "Would you have suspected non-human authorship?"', loc="left", fontweight="bold")
    axD.spines["left"].set_visible(False)
    axD.legend(handles=[mpatches.Patch(color=DETECT_COLOURS[c], label=c) for c in DETECT_ORDER],
               loc="upper center", bbox_to_anchor=(0.5, -0.18), frameon=False, ncol=5, fontsize=7.8)
    axD.text(0.5, 1.02, "← read as human            caught as machine →",
             transform=axD.transAxes, ha="center", fontsize=7.5, style="italic", color="#888")

    fig.suptitle(
        "Figure 8. Human expert jury (n=5) vs LLM jury, on the same four stories and rubric. "
        "The LLM jury's two top-rated stories (S_06, S_02) collapse by ~4 points\n"
        "with human experts, who instead rank S_07 first on every criterion — the one story they cannot reliably flag as "
        "machine-written, and the only one from a 2025-era model.\n"
        "Story S_04 (Grok): humans match the 4-juror LLM consensus, not Grok's own 8.3 self-rating. n=5 — directional, within-subject.",
        fontsize=10, y=1.005,
    )
    plt.tight_layout(rect=[0, 0.0, 1, 0.97])
    plt.savefig(OUT / "fig8_human_vs_llm.png")
    plt.close()
    print(f"Wrote fig8_human_vs_llm.png to {OUT}")


if __name__ == "__main__":
    main()
