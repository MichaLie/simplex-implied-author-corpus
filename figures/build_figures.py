"""
Generate manuscript figures for the SIMPLEX / CFS 2026 paper.

Outputs PNG files at 300 DPI to figures/.

Figures:
    Fig 1 — SIMPLEX pipeline diagram
    Fig 2 — Report-to-persona asymmetry (gender + region by run)
    Fig 3 — Implied-author trait frequencies (R2 personas, n=20)
    Fig 4 — Level 2 LLM-jury scoring of the 8-story corpus
    Fig 5 — Per-LLM aesthetic profile (leniency × discrimination)
    Fig 6 — Self-preference: within-juror vs between-juror Δ per vendor
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "figures"
OUT.mkdir(parents=True, exist_ok=True)

# Publication settings.
plt.rcParams.update({
    "font.family": "sans-serif",
    "font.size": 10,
    "axes.titlesize": 11,
    "axes.labelsize": 10,
    "xtick.labelsize": 9,
    "ytick.labelsize": 9,
    "legend.fontsize": 9,
    "savefig.dpi": 300,
    "savefig.bbox": "tight",
    "axes.spines.top": False,
    "axes.spines.right": False,
})

# Consistent vendor colours across figures.
VENDOR_COLOURS = {
    "Claude-Opus-47": "#D97757",   # warm orange
    "GPT-55":         "#7AAE7A",   # sage
    "Gemini-31-Pro":  "#5B8FB9",   # slate blue
    "Grok-43":        "#9C7AB5",   # muted purple
    "Kimi-26":        "#7E7E7E",   # neutral grey (outsider)
}
VENDOR_LABELS = {
    "Claude-Opus-47": "Claude Opus 4.7",
    "GPT-55":         "GPT-5.5",
    "Gemini-31-Pro":  "Gemini 3.1 Pro",
    "Grok-43":        "Grok 4.3",
    "Kimi-26":        "Kimi 2.6 (outsider)",
}


# ============================================================
# FIGURE 1 — SIMPLEX pipeline diagram
# ============================================================

def fig1_pipeline():
    fig, ax = plt.subplots(figsize=(8.5, 6.0))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axis("off")

    # Phase boxes — vertical flow.
    phases = [
        (5, 9.0, "Phase 1 — LLMs as literary critics",
         "Distill what makes prose writers exceptional\n→ 6 deep-research reports (4 vendors × 2 timepoints)"),
        (5, 7.0, "Phase 2 — LLMs as biographers",
         "Instantiate criteria as Nobel-laureate personas\n→ 24 HIGH personas + 24 control personas"),
        (5, 5.0, "Phase 3 — LLMs as writers",
         "Embody persona voice in literary short fiction\n→ 8 stories (4 R1 + 4 R2)"),
        (5, 3.0, "Level 2 — LLMs as jurors",
         "Score stories on 5-criterion rubric\n→ 120 evaluations (5 LLMs × 8 stories × 3 reps)"),
        (5, 1.0, "Level 3 — Human expert jury",
         "Evaluate LLM-jury top-3 + polarising anchor\n→ n=5 evaluators × 4 stories"),
    ]

    box_w, box_h = 6.6, 1.4

    for cx, cy, title, body in phases:
        box = FancyBboxPatch(
            (cx - box_w / 2, cy - box_h / 2), box_w, box_h,
            boxstyle="round,pad=0.05,rounding_size=0.15",
            linewidth=1.2, edgecolor="#333333", facecolor="#F4F1EC",
        )
        ax.add_patch(box)
        ax.text(cx, cy + 0.3, title, ha="center", va="center",
                fontsize=10.5, fontweight="bold", color="#222")
        ax.text(cx, cy - 0.3, body, ha="center", va="center",
                fontsize=9, color="#333")

    # Arrows between phases.
    for i in range(len(phases) - 1):
        y_top = phases[i][1] - box_h / 2
        y_bot = phases[i + 1][1] + box_h / 2
        ax.add_patch(FancyArrowPatch(
            (5, y_top), (5, y_bot),
            arrowstyle="-|>", mutation_scale=14,
            linewidth=1.0, color="#555"
        ))

    # Side annotation: cross-vendor parallelism.
    ax.text(0.3, 5, "Cross-vendor\nparallelism\nat every stage",
            ha="left", va="center", fontsize=9, style="italic", color="#666")
    ax.annotate("",
                xy=(1.5, 7), xytext=(1.5, 3),
                arrowprops=dict(arrowstyle="-", linewidth=0.6, color="#999",
                                linestyle="--"))

    ax.set_title("Figure 1. The SIMPLEX pipeline. LLMs are commissioned in distinct\nauthorial roles across staged phases; outputs at each stage are independently evaluated.",
                 fontsize=11, pad=12)
    plt.savefig(OUT / "fig1_pipeline.png")
    plt.close()
    print("Wrote fig1_pipeline.png")


# ============================================================
# FIGURE 2 — Report-to-persona asymmetry
# ============================================================

def fig2_asymmetry():
    fig, (axL, axR) = plt.subplots(1, 2, figsize=(10, 4.5))

    # LEFT PANEL: gender asymmetry.
    runs = ["Run 1\n(July 2025)", "Run 2\n(May 2026)"]
    report_pct_female = [31.0, 19.7]    # from report_writer_counts_by_run.csv
    persona_pct_female = [100.0, 90.0]  # R1: n=4, all female; R2: 18/20

    x = np.arange(len(runs))
    width = 0.35

    b1 = axL.bar(x - width/2, report_pct_female, width,
                 label="Reports (named master exemplars)",
                 color="#9CB4A5", edgecolor="#444", linewidth=0.7)
    b2 = axL.bar(x + width/2, persona_pct_female, width,
                 label="Personas (generated implied authors)",
                 color="#D97757", edgecolor="#444", linewidth=0.7)

    # Gap annotations.
    for i, (r, p) in enumerate(zip(report_pct_female, persona_pct_female)):
        gap = p - r
        axL.annotate(f"+{gap:.0f} pp",
                     xy=(x[i], (r + p) / 2),
                     xytext=(x[i] + 0.05, (r + p) / 2),
                     fontsize=10, fontweight="bold", color="#444",
                     ha="left", va="center")

    axL.set_xticks(x)
    axL.set_xticklabels(runs)
    axL.set_ylabel("% Female")
    axL.set_ylim(0, 118)  # extra headroom so 100% bar label clears the legend
    axL.set_title("Gender asymmetry between reports and personas")
    axL.legend(loc="upper center", bbox_to_anchor=(0.5, -0.14),
               frameon=False, ncol=1)  # below the chart, stacked vertically
    axL.bar_label(b1, fmt="%.1f%%", padding=3, fontsize=9)
    axL.bar_label(b2, fmt="%.0f%%", padding=3, fontsize=9)

    # RIGHT PANEL: regional asymmetry (R2 only; persona counts from C1 coding).
    regions = ["MENA /\nLevantine", "East Asian", "African /\ndiaspora"]
    # Report % from analysis/report_writer_counts_by_run.csv (R2 master exemplars, n=61).
    report_r2_pct = [0.0, 0.0, 9.8]
    # Persona % from lead-author (C1) region coding on R2 HIGH (n=20):
    #   MENA = 3/20 = 15.0; African diaspora = 5/20 = 25.0; East Asian = 0/20 = 0.
    persona_r2_pct = [15.0, 0.0, 25.0]

    x = np.arange(len(regions))
    b1 = axR.bar(x - width/2, report_r2_pct, width,
                 label="R2 reports (% of master exemplars)",
                 color="#9CB4A5", edgecolor="#444", linewidth=0.7)
    b2 = axR.bar(x + width/2, persona_r2_pct, width,
                 label="R2 personas (% of n=20)",
                 color="#D97757", edgecolor="#444", linewidth=0.7)

    axR.set_xticks(x)
    axR.set_xticklabels(regions)
    axR.set_ylabel("%")
    axR.set_ylim(0, 32)
    axR.set_title("Regional asymmetry (Run 2 only)")
    axR.legend(loc="upper center", bbox_to_anchor=(0.5, -0.14),
               frameon=False, ncol=1)  # match left panel placement
    axR.bar_label(b1, fmt="%.1f%%", padding=3, fontsize=9)
    axR.bar_label(b2, fmt="%.0f%%", padding=3, fontsize=9)

    fig.suptitle(
        "Figure 2. The reports-to-personas asymmetry. The reports name a mostly-male canon\n"
        "with no MENA or East Asian master exemplars; the personas LLMs generate from those reports\n"
        "instantiate the implied author as predominantly female with MENA representation emerging from zero priming.",
        fontsize=10.5, y=1.02,
    )
    plt.tight_layout(rect=[0, 0.10, 1, 0.96])  # leave space for stacked below-chart legend + suptitle
    plt.savefig(OUT / "fig2_asymmetry.png")
    plt.close()
    print("Wrote fig2_asymmetry.png")


# ============================================================
# FIGURE 3 — Implied-author trait frequencies (R2 personas)
# ============================================================

def fig3_traits():
    # From the paper Finding 1 table. Values where ranges given use the midpoint.
    traits = [
        ("Female",                                 90, 0.96),
        ("Multilingual childhood",                100, 0.92),
        ("Outsider relation to writing language", 100, 0.96),
        ("Trauma transformed to innovation",      100, 1.00),
        ("Sentence-level revision obsession",     100, 1.00),
        ("Nobel Prize awarded in text",           100, 1.00),
        ("Gueuloir / auditory revision",          100, 0.92),
        ("Late-blooming (first major work > 40)",  95, 0.71),
        ("Specific historical event in backstory", 87, 0.81),
        ("Hand-transcription apprenticeship",      90, 0.75),
        ("Saturated narrow re-reading",            90, 0.71),
        ("Nobel year in 2018–2019 window",         80, 1.00),
        ("Synesthesia (explicit or implicit)",     77, 0.96),
        ("Depression or mood disorder",            72, 0.77),
        ("Nobel year = 2018 specifically",         60, 1.00),
        ("Index-card composition",                 55, 0.81),
        ("Childhood illness or confinement",       45, 0.83),
        ("Hidden or banned library in childhood",  15, 0.78),
    ]
    traits = sorted(traits, key=lambda r: r[1])  # ascending so largest is at top

    fig, ax = plt.subplots(figsize=(9, 7.5))
    labels = [t[0] for t in traits]
    pcts = [t[1] for t in traits]
    kappas = [t[2] for t in traits]
    y = np.arange(len(labels))

    # Colour by κ tier.
    def colour(k):
        if k >= 0.90:
            return "#5C8AA8"  # high reliability
        elif k >= 0.80:
            return "#88AAC6"
        else:
            return "#BBCAD9"  # lower

    bars = ax.barh(y, pcts, color=[colour(k) for k in kappas],
                    edgecolor="#333", linewidth=0.6)
    ax.set_yticks(y)
    ax.set_yticklabels(labels)
    ax.set_xlabel("Prevalence in 2026 personas (n = 20)")
    ax.set_xlim(0, 105)
    ax.set_title("Figure 3. Implied-author trait prevalence in the 2026 HIGH-prestige persona corpus (n=20).\n"
                 "Bar shade indicates inter-rater reliability tier (darker = higher κ).",
                 pad=12)

    # Annotate with % and κ.
    for bar, p, k in zip(bars, pcts, kappas):
        ax.text(bar.get_width() + 1.5, bar.get_y() + bar.get_height()/2,
                f"{p}% (κ={k:.2f})", va="center", ha="left", fontsize=8.5, color="#333")

    # Legend swatches for κ tiers.
    legend_handles = [
        mpatches.Patch(color="#5C8AA8", label="κ ≥ 0.90"),
        mpatches.Patch(color="#88AAC6", label="0.80 ≤ κ < 0.90"),
        mpatches.Patch(color="#BBCAD9", label="0.70 ≤ κ < 0.80"),
    ]
    ax.legend(handles=legend_handles, loc="lower right", frameon=False)

    plt.tight_layout()
    plt.savefig(OUT / "fig3_traits.png")
    plt.close()
    print("Wrote fig3_traits.png")


# ============================================================
# FIGURE 4 — Level 2 LLM-jury scoring of the 8-story corpus
# ============================================================

def fig4_jury_scoring():
    df = pd.read_csv(ROOT / "analysis" / "level2_scores_wide.csv")
    summary = pd.read_csv(ROOT / "analysis" / "level2_summary.csv")

    story_means = (summary[summary["llm"] == "*ALL*"]
                   .set_index("story_id")["mean_weighted"]
                   .sort_values(ascending=False))
    story_order = list(story_means.index)

    fig, ax = plt.subplots(figsize=(10, 5.5))

    x_positions = {sid: i for i, sid in enumerate(story_order)}
    jitter_amp = 0.08

    # Track legend entries per LLM (only add once).
    seen = set()
    for _, row in df.iterrows():
        sid = row["story_id"]
        llm = row["llm"]
        score = row["weighted_total"]
        x = x_positions[sid] + np.random.uniform(-jitter_amp, jitter_amp)
        label = VENDOR_LABELS[llm] if llm not in seen else None
        seen.add(llm)
        ax.scatter(x, score,
                   color=VENDOR_COLOURS[llm], alpha=0.75, s=42,
                   edgecolor="#333", linewidth=0.4,
                   label=label, zorder=3)

    # Story-mean markers (black horizontal bars).
    for sid in story_order:
        m = story_means[sid]
        ax.hlines(m, x_positions[sid] - 0.25, x_positions[sid] + 0.25,
                  colors="#111", linewidth=2.2, zorder=4)

    # Background shading for consensus typology.
    # High-consensus top (S_06, S_02) = green; polarising (S_07, S_04) = amber; bottom (S_05) = grey.
    typology = {
        "S_06": ("Top-tier consensus", "#D8E8D6"),
        "S_02": ("Top-tier consensus", "#D8E8D6"),
        "S_07": ("Polarising", "#F2E0C0"),
        "S_01": ("Mid (consensus)",   "#E8E8E8"),
        "S_03": ("Mid",               "#E8E8E8"),
        "S_08": ("Bottom",            "#E8E8E8"),
        "S_04": ("Polarising", "#F2E0C0"),
        "S_05": ("Bottom consensus",  "#DDDDDD"),
    }

    ax.set_xticks(list(range(len(story_order))))
    ax.set_xticklabels(story_order)
    ax.set_ylabel("Weighted total score (1–10)")
    ax.set_ylim(2, 10)
    ax.set_xlabel("Story (anonymised ID; ordered by grand mean across 15 evaluations)")
    ax.set_title("Figure 4. Level 2 LLM-jury scoring of the 8-story corpus. Each point is one of 15 evaluations\n"
                 "per story (5 LLM jurors × 3 reps). Black bars = per-story grand mean. Spread captures consensus vs polarisation.",
                 pad=12)
    ax.legend(loc="lower left", frameon=False, ncol=2)

    plt.tight_layout()
    plt.savefig(OUT / "fig4_jury_scoring.png")
    plt.close()
    print("Wrote fig4_jury_scoring.png")


# ============================================================
# FIGURE 5 — Per-LLM aesthetic profile (leniency × discrimination)
# ============================================================

def fig5_llm_profile():
    summary = pd.read_csv(ROOT / "analysis" / "level2_summary.csv")
    per_llm = summary[summary["llm"] != "*ALL*"].copy()

    # Compute per-LLM leniency (mean across stories) and discrimination (range of per-story means).
    profile = (per_llm.groupby("llm")
               .agg(leniency_mean=("mean_weighted", "mean"),
                    max_story=("mean_weighted", "max"),
                    min_story=("mean_weighted", "min"))
               .reset_index())
    profile["discrimination_range"] = profile["max_story"] - profile["min_story"]

    fig, ax = plt.subplots(figsize=(9, 6.5))

    # Set explicit axis padding so point-name labels and quadrant labels have room.
    xmin = profile["leniency_mean"].min() - 0.6
    xmax = profile["leniency_mean"].max() + 0.9   # extra room for Grok label on right
    ymin = profile["discrimination_range"].min() - 0.4
    ymax = profile["discrimination_range"].max() + 0.5
    ax.set_xlim(xmin, xmax)
    ax.set_ylim(ymin, ymax)

    # Quadrant divider lines, plotted BEFORE points so points sit on top.
    xmid = (profile["leniency_mean"].min() + profile["leniency_mean"].max()) / 2
    ymid = (profile["discrimination_range"].min() + profile["discrimination_range"].max()) / 2
    ax.axvline(xmid, color="#CCC", linewidth=0.6, linestyle="--", zorder=1)
    ax.axhline(ymid, color="#CCC", linewidth=0.6, linestyle="--", zorder=1)

    # Quadrant labels — placed in axes-coordinate corners so they cannot clip.
    ax.text(0.02, 0.97, "demanding + discriminating", transform=ax.transAxes,
            fontsize=8.5, style="italic", color="#888",
            ha="left", va="top")
    ax.text(0.98, 0.03, "lenient + flat", transform=ax.transAxes,
            fontsize=8.5, style="italic", color="#888",
            ha="right", va="bottom")

    # Per-LLM points + bold labels offset to the right.
    for _, row in profile.iterrows():
        llm = row["llm"]
        ax.scatter(row["leniency_mean"], row["discrimination_range"],
                   color=VENDOR_COLOURS[llm], s=240, alpha=0.85,
                   edgecolor="#222", linewidth=0.8, zorder=3,
                   label=VENDOR_LABELS[llm])
        ax.annotate(VENDOR_LABELS[llm],
                    xy=(row["leniency_mean"], row["discrimination_range"]),
                    xytext=(10, 4), textcoords="offset points",
                    fontsize=9.5, color="#222", fontweight="bold")

    ax.set_xlabel("Leniency (mean weighted score across all 8 stories; higher = more lenient)")
    ax.set_ylabel("Discrimination (range of per-story means; higher = more discriminating)")
    ax.set_title("Figure 5. Per-LLM aesthetic profile. The 5 LLM jurors occupy distinct positions\n"
                 "in the leniency × discrimination plane — they are not interchangeable aesthetic agents.",
                 pad=14)

    plt.tight_layout()
    plt.savefig(OUT / "fig5_llm_profile.png")
    plt.close()
    print("Wrote fig5_llm_profile.png")


# ============================================================
# FIGURE 6 — Self-preference: within-juror vs between-juror Δ per vendor
# ============================================================

def fig6_self_preference():
    long_df = pd.read_csv(ROOT / "analysis" / "level2_scores_long.csv")
    # Use weighted total per evaluation cell.
    wide = pd.read_csv(ROOT / "analysis" / "level2_scores_wide.csv")

    # vendor → own-story mapping (which R2 story each 2026 vendor generated).
    own_story = {
        "Claude-Opus-47": "S_02",
        "GPT-55":         "S_06",
        "Gemini-31-Pro":  "S_03",
        "Grok-43":        "S_04",
    }

    deltas = []
    for vendor, own_sid in own_story.items():
        # Within-juror Δ: vendor's mean on own story − vendor's mean on other 7 stories.
        own_scores  = wide[(wide["llm"] == vendor) & (wide["story_id"] == own_sid)]["weighted_total"]
        other_scores = wide[(wide["llm"] == vendor) & (wide["story_id"] != own_sid)]["weighted_total"]
        within = own_scores.mean() - other_scores.mean()
        # Between-juror Δ: vendor's mean on own story − mean of other jurors on same story.
        other_jurors_on_own = wide[(wide["llm"] != vendor) & (wide["story_id"] == own_sid)]["weighted_total"]
        between = own_scores.mean() - other_jurors_on_own.mean()
        deltas.append({
            "vendor": vendor,
            "within": within,
            "between": between,
        })

    df = pd.DataFrame(deltas)

    fig, ax = plt.subplots(figsize=(9.5, 5.5))

    x = np.arange(len(df))
    width = 0.38

    # Within-juror bars (preregistered primary).
    b1 = ax.bar(x - width/2, df["within"], width,
                color="#5C8AA8", edgecolor="#333", linewidth=0.7,
                label="Within-juror Δ (preregistered primary)")
    # Between-juror bars (exploratory).
    b2 = ax.bar(x + width/2, df["between"], width,
                color="#D97757", edgecolor="#333", linewidth=0.7,
                label="Between-juror Δ (exploratory)")

    ax.axhline(0, color="#222", linewidth=0.8)
    ax.bar_label(b1, fmt="%+.2f", padding=3, fontsize=9, color="#222")
    ax.bar_label(b2, fmt="%+.2f", padding=3, fontsize=9, color="#222")

    labels = [f"{VENDOR_LABELS[v]}\n(own: {own_story[v]})" for v in df["vendor"]]
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_ylabel("Δ (weighted score; positive = vendor scored its own story higher)")
    ax.set_title("Figure 6. Self-preference is heterogeneous between LLM vendors and uniform within.\n"
                 "Within-juror Δ (against each vendor's own baseline on 7 other stories) is positive for all 4 vendors;\n"
                 "between-juror Δ (against the consensus of other jurors on the same story) ranges from −0.85 (GPT) to +4.30 (Grok).",
                 pad=12)
    ax.legend(loc="upper left", frameon=False)

    plt.tight_layout()
    plt.savefig(OUT / "fig6_self_preference.png")
    plt.close()
    print("Wrote fig6_self_preference.png")


# ============================================================
# FIGURE 7 — Prompt-to-output affordance heatmap
# ============================================================
#
# For each implied-author trait, code its presence/intensity at each pipeline
# stage on an integer 0–3 scale:
#     0 = absent / not relevant
#     1 = weakly present / lightly afforded
#     2 = explicitly present / strongly afforded
#     3 = dominant — the trait is forced or ubiquitous at this stage
#
# Coding is the lead author's qualitative judgement against the prompt files,
# the deterministic regex extraction outputs (reports), the κ-screened persona
# trait codings, and a close read of the 8 stories. The encoding is conservative
# (favouring lower scores under uncertainty). Cells are annotated with their
# integer score.

TRAIT_MATRIX = [
    # (trait label, prompt, reports, persona, story)
    ("Female protagonist",                              0, 1, 3, 3),
    ("Eastern European / Mitteleuropan geography",      0, 1, 3, 2),
    ("MENA / Levantine geography",                      0, 0, 2, 1),
    ("Fictional Nobel year clustered on 2018",          1, 0, 3, 1),
    ("Late-blooming (first major work after 40)",       0, 1, 3, 0),
    ("Multilingual childhood",                          1, 2, 3, 2),
    ("Outsider relation to writing language",           2, 2, 3, 2),
    ("Specific historical event in family backstory",   1, 2, 3, 2),
    ("Trauma transformed to innovation",                2, 2, 3, 2),
    ("Synesthesia (explicit or implicit)",              1, 2, 2, 2),
    ("Hand-transcription apprenticeship",               1, 2, 3, 1),
    ("Gueuloir / auditory revision",                    1, 2, 3, 1),
    ("Index-card composition",                          1, 2, 2, 0),
    ("Sentence-level revision obsession",               1, 3, 3, 1),
    ("Childhood illness or extended confinement",       0, 1, 2, 1),
]

STAGE_LABELS = [
    "Phase 1\nprompt",
    "Phase 1\nreports",
    "Phase 2\npersonas",
    "Phase 3\nstories",
]
STAGE_SUBLABELS = [
    "(what the\nprompt asks for)",
    "(what the\nLLM-as-critic names)",
    "(what the LLM-as-\nbiographer specifies)",
    "(what the LLM-as-\nwriter recapitulates)",
]


def fig7_affordance_heatmap():
    # Sort rows by largest gap between "prompt+reports" and "persona+story"
    # (i.e. traits the LLM added beyond what the scaffold named).
    # r = (label, prompt, reports, persona, story); sort by completion minus scaffold.
    rows = sorted(
        TRAIT_MATRIX,
        key=lambda r: (r[3] + r[4]) - (r[1] + r[2]),
        reverse=True,
    )
    labels = [r[0] for r in rows]
    data = np.array([[r[1], r[2], r[3], r[4]] for r in rows], dtype=float)

    fig, ax = plt.subplots(figsize=(12.5, 9.0))

    # Custom colormap: white → light blue → mid blue → dark blue.
    from matplotlib.colors import LinearSegmentedColormap
    cmap = LinearSegmentedColormap.from_list(
        "intensity",
        ["#FFFFFF", "#D6E5F0", "#7FB0D1", "#2E6FA0"],
        N=256,
    )

    im = ax.imshow(data, cmap=cmap, vmin=0, vmax=3, aspect="auto")

    # Annotate each cell with its score.
    for i in range(data.shape[0]):
        for j in range(data.shape[1]):
            v = int(data[i, j])
            text_colour = "white" if v >= 2 else "#222"
            ax.text(j, i, str(v), ha="center", va="center",
                    fontsize=11, fontweight="bold", color=text_colour)

    ax.set_xticks(np.arange(len(STAGE_LABELS)))
    ax.set_xticklabels(STAGE_LABELS, fontsize=10.5, fontweight="bold")
    ax.xaxis.set_ticks_position("top")
    ax.xaxis.set_label_position("top")
    # Sublabels below each column.
    for j, sub in enumerate(STAGE_SUBLABELS):
        ax.text(j, len(labels) - 0.45 + 0.7, sub, ha="center", va="top",
                fontsize=8.5, color="#666", style="italic",
                transform=ax.transData)
    ax.set_yticks(np.arange(len(labels)))
    ax.set_yticklabels(labels, fontsize=9.5)
    ax.set_xlabel("")
    ax.set_ylabel("")

    # Highlight the asymmetry: thick frame around the "Persona / Story" half
    # for rows where the scaffold (prompt + reports) names the trait at ≤ 1
    # but the LLM completion specifies it at ≥ 2.
    for i, row in enumerate(rows):
        # row = (label, prompt, reports, persona, story)
        scaffold_max = max(row[1], row[2])      # max of prompt + report intensity
        completion_min = min(row[3], row[4])    # min of persona + story intensity
        if scaffold_max <= 1 and completion_min >= 2:
            # Highlight the persona + story cells (cols 2 + 3).
            for j in (2, 3):
                rect = mpatches.Rectangle(
                    (j - 0.5, i - 0.5), 1, 1,
                    fill=False, edgecolor="#C04A2F", linewidth=2.2,
                )
                ax.add_patch(rect)

    ax.tick_params(top=False, bottom=False, left=False, right=False)
    ax.spines[:].set_visible(False)

    # Colourbar.
    cbar = plt.colorbar(im, ax=ax, fraction=0.025, pad=0.04,
                        ticks=[0, 1, 2, 3])
    cbar.ax.set_yticklabels([
        "0: absent",
        "1: weakly\npresent",
        "2: explicitly\npresent",
        "3: dominant",
    ], fontsize=8.5)
    cbar.outline.set_visible(False)

    # Title placed BELOW the figure as a caption so it doesn't collide with the
    # top column labels.
    fig.suptitle(
        "Figure 7. Prompt-to-output affordance map. Rows = implied-author traits; columns = pipeline stages.\n"
        "Cells = qualitative intensity (0–3). Red-outlined cells mark traits the LLM completion (persona / story)\n"
        "specifies at intensity ≥ 2 where the upstream scaffold (prompt + reports) names the trait at intensity ≤ 1.\n"
        "These cells make visible the asymmetry between what the theoretical scaffold names and what the LLM adds.",
        fontsize=10.5, y=0.02, va="bottom",
    )

    plt.tight_layout(rect=[0, 0.08, 1, 1])  # leave room at bottom for caption
    plt.savefig(OUT / "fig7_affordance_heatmap.png")
    plt.close()
    print("Wrote fig7_affordance_heatmap.png")


# ============================================================
# Main
# ============================================================

def main():
    np.random.seed(42)  # for stable jitter in fig 4
    fig1_pipeline()
    fig2_asymmetry()
    fig3_traits()
    fig4_jury_scoring()
    fig5_llm_profile()
    fig6_self_preference()
    fig7_affordance_heatmap()
    print(f"\nAll figures written to {OUT.relative_to(ROOT)}/")


if __name__ == "__main__":
    main()
