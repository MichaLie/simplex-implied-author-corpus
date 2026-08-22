# Pre-registration Level 2 — Addendum

*Locked: 2026-05-24. Author: Michaela Liegertová. Drafting partner: Claude.*

This addendum documents deviations from `docs/PREREGISTRATION_LEVEL2.md` (locked 2026-05-24 morning) discovered during the v2 AI peer consultation (Codex + Gemini auditors, afternoon of the same day). The original pre-registration is preserved unedited; this addendum sits beside it. No methodological aspect of the LLM-jury sub-study has changed — only the file-organization deviation, an analytical-frame clarification on self-preference, and a κ-implementation correction are documented here.

## 1. Actual completion date and sequence

- Pre-registration locked: 2026-05-24 (morning).
- Data collection (120 evaluation sessions across 5 LLMs × 8 stories × 3 reps): completed 2026-05-24 (same day).
- First numerical aggregation produced by `analysis/level2_extract.py` (not the pre-registered `analysis/level2_aggregate.py`, which was a planned-name placeholder that ended up implemented under the `_extract` filename).
- The compressed timeline (pre-registration lock → data collection → top-3 identification → Level 3 pre-registration on the same calendar day) is honest. No external Git/OSF timestamp trail existed at the time. Initialising the repository under version control is in the action queue (see `docs/ANALYSIS_PLAN.md`).

## 2. Response-file organisation deviation

The pre-registration (§"Reproducibility" line 114) specifies:

> *Per-session responses to be saved at `level2_jury/responses/{LLM}_{S_XX}_rep{N}.md`.*

This implied 120 individual response files. Actual data collection produced **8 per-story aggregated files** (`level2_jury/responses/SCORING STORY S_*.md`), each containing all 15 evaluations for one story (5 LLMs × 3 reps each), in the structured markdown format defined by the juror prompt.

**Reason for the change:** vendor web-interface UI made per-story batching substantially faster to operate than per-session file management. The change was made by the lead author during data collection.

**Methodological impact: none.** Each of the 120 evaluations was produced in a fresh chat session as pre-registered. Each session received the verbatim juror prompt (`level2_jury/PROMPT_juror.md`) plus the anonymised story (`level2_jury/eval_bundles/S_XX.md`). The aggregated-file format is purely a post-session storage convention. The extractor `analysis/level2_extract.py` parses the aggregated files into the same per-evaluation structure the pre-registered statistical plan operates on; it produced 120/120 clean evaluations with 0 flags.

**Action required of the consultant:** none beyond noting the deviation. The 120 evaluations contained in the 8 aggregated files are the pre-registered dataset.

## 3. Self-preference estimand — clarification

The pre-registration (§"Pre-specified analysis plan" #4) specifies the self-preference analysis as a comparison of "each juror's mean weighted total on the single R2 story it generated versus its mean weighted total on the 7 stories it did not generate." **This is the within-juror frame.**

Earlier headline self-preference numbers communicated in working notes (and reproduced in `docs/ANALYSIS_QUESTIONS_v1.md` Cluster C examples) used the **between-juror frame** — each vendor-juror's score on its own story compared to the mean of the other four jurors' scores on the same story. The between-juror frame produces the striking Δ values previously circulated (Grok +4.30, Gemini +1.32, Claude +0.09, GPT −0.85).

The two frames answer different questions and should not be conflated:

- **Within-juror (pre-registered, primary):** does this juror inflate its own story above its own scoring baseline? Yes for all 4 vendors (all Δs positive). Headline finding: **all four vendor-jurors show positive within-juror self-elevation** when compared to their own baseline on non-self stories.
- **Between-juror (post-hoc, exploratory):** how does this juror's score on its own story compare to the consensus of other jurors on the same story? Heterogeneous (range from Grok +4.30 to GPT −0.85). Striking but contaminated by juror leniency.

**Decision:** the within-juror analysis is the pre-registered primary analysis and will be reported as such. The between-juror analysis is reported as exploratory and labelled accordingly in the manuscript. Both will appear; neither will be presented as the primary "headline" alone.

The pre-registered mixed-effects model (`score ~ story_factor + own_vs_other + (1|juror) + (1|rep)`) is **dropped** following both reviewers' concurrent recommendation: with n=4 self-cells the random-effects structure cannot be reliably estimated. Replacement: descriptive within-juror Δ values per vendor with bootstrap 95% confidence intervals (1000 resamples) and a paired non-parametric test (Wilcoxon signed-rank or permutation) on the four-vendor within-juror Δ vector. The mixed-effects model results, if estimable, will be reported as a supplementary sensitivity check, not as the headline.

## 4. κ implementation correction (`analysis/compute_kappa.py`)

A bug was identified in the κ computation: when expected agreement `pe = 1.0` (i.e., all coders gave a single category for every document), the script returned κ = 1.0. Mathematically, κ is undefined in this case because the denominator `(1 - pe)` is zero. The bug affected 2 of 53 variables (`exile_or_displacement_central`, `number_MENA_exemplars`); both had 100% observed agreement but no marginal variation.

**Fix applied:** the script now returns `kappa = None` and flags these variables as κ-undefined; the original 100% observed agreement is preserved as a separate output column.

**Headline number change:** 34/53 variables ≥ κ 0.70 → **32/53 variables ≥ κ 0.70 (plus 2 with 100% observed agreement but κ-undefined)**. The two affected variables remain usable descriptively but are excluded from predictive models.

This is the only headline-number change resulting from the v2 audit. All downstream documents have been updated.

A second small fix was applied to `compute_kappa.py`: case/synonym normalization for boolean values entered by coders ("Yes"/"yes"/"y"/"TRUE" all map to the canonical "yes"). This pre-empts artificial κ depression from string-format differences in future coder workbooks; the current workbooks did not contain such variants, so the existing κ values are unchanged.

## 5. Bibliography-extraction regex bug (separate, but found during the same audit)

A separate audit finding: `analysis/extract_report_exemplars.py` was using case-insensitive regex matching on bare-surname patterns. This produced false positives where common English words matched literary surnames in lowercase contexts (e.g., the word "child" in prose matched the `\bChild\b` pattern for Lee Child).

**Fix applied:** the writer-search call now uses case-sensitive matching. Bibliography stripping remains case-insensitive (section headers vary in capitalisation).

**Headline number change: none.** The only material false positive was Lee Child being marked present in `R2_Opus47` (where only the prose word "child" appeared). Lee Child is a "comparison" role writer, not a master exemplar, so the false positive did not enter the headline master-exemplar counts. Verified by direct diff against pre-fix `report_writer_counts.csv` and `report_writer_counts_by_run.csv`: identical.

This fix is documented here for audit-trail completeness, even though no claim or number in the project changed.

## 6. What this addendum does NOT modify

- The pre-registered juror prompt (`level2_jury/PROMPT_juror.md`).
- The pre-registered rubric (5 criteria, weights 30/25/20/15/10, integer 1–10 scale).
- The pre-registered juror panel (Claude Opus 4.7, GPT-5.5, Gemini 3.1 Pro, Grok 4.3, Kimi 2.6).
- The pre-registered sample size (5 LLMs × 8 stories × 3 reps = 120 sessions).
- The pre-registered stopping rule (no extension without further addendum).
- The pre-registered top-3 selection rule (mean weighted total with Borda tiebreak on derived ranks).
- The pre-registered analysis plan beyond the self-preference clarification in §3 above.

## 7. Top-3 fragility note

The pre-registered selection rule (top 3 by mean weighted total) produced:
1. S_06 = 8.66 (top in 15/15 reconstructed sessions)
2. S_02 = 8.38 (top-3 in 15/15)
3. S_07 = 6.97 (top-3 in 7/15) — vs S_01 = 6.90 (top-3 in 6/15)

The deterministic rule is rule-compliant; Borda count also gives S_07 over S_01 (80 vs 75). However the gap is only 0.07 weighted points, and S_07 is a polarising story (cross-LLM SD = 1.40) while S_01 is a mid-tier near-miss. **The third top-3 slot should be reported in the manuscript as "third by preregistered mean, with S_01 as near-miss; see `PREREGISTRATION_LEVEL3_ADDENDUM.md` for the Level 3 design response."** This framing avoids overstating S_07's preference over S_01.

## 8. Auditors

- Codex (OpenAI), with 6 independent explorer sub-agents (methodology / scripts / data integrity / Level 2 pipeline / reproducibility / statistical validity).
- Gemini (Google) with 3 independent sub-agents (script / data / methodology).

Both audit reports filed at `feedback/v2_consultation/`.

— end —
