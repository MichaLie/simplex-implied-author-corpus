# Pre-registration corrections & executed-vs-registered deviations

**Date:** 2026-06-21
**Author:** Michaela Liegertová (with AI audit support)

The locked pre-registration files (`PREREGISTRATION_v1.md`, `PREREGISTRATION_LEVEL2.md`, `PREREGISTRATION_LEVEL3.md` and their addenda) are **preserved unedited** as the time-stamped design lock. This document is the vehicle for (A) factual corrections to text inside those locked files, and (B) disclosure of deviations between the registered analysis plan and what was actually executed. It supersedes the cited locked passages where they conflict. Full audit trail: `analysis/RESEARCH_AUDIT_2026-06-21.md`.

---

## A. Factual corrections to locked pre-registration text

### A1. `PREREGISTRATION_LEVEL2_ADDENDUM.md:79` — S_06 session-robustness overstated
The addendum's top-3 fragility note states "S_06 = 8.66 (top in 15/15 reconstructed sessions)." Recomputing per-session ranks independently from the raw response files (15 sessions = 5 LLMs × 3 reps), **S_06 is the sole rank-1 story in only 11 of 15 sessions** (sole-or-tied rank-1 in 13/15; strictly outranked in 2 — by S_02 in Gemini rep 3, by S_07 in Grok rep 1). "Top in 15/15" is incorrect for sole rank-1; S_06 *is* top-3 in 15/15.
- **Impact:** none on the top-3 *selection* — S_06 correctly ranks first by mean weighted total (8.6633), and the Level 3 story set is unchanged. Only the parenthetical robustness claim is wrong. The manuscript's wording ("top-tier by every juror in every replicate," i.e. top-3 in 15/15; `results_draft.md`) is correct and needs no change.
- **Corrected reading:** "S_06 — highest mean (8.66); sole or tied rank-1 in 13/15 reconstructed sessions; strictly outranked in 2."

### A2. `PREREGISTRATION_LEVEL3_ADDENDUM.md` — internal contradiction on the L3-5 longitudinal-stability analysis
The addendum both (a) drops L3-5 ("L3-5 is therefore removed from the pre-specified analysis plan," lines 54–63) and (b) lists, under "What this addendum does NOT modify" (line 68), "Inclusion of SOLIT reviewers (n=3) for longitudinal stability check on S_07."
- **Operative decision (what was executed):** L3-5 is **dropped**. The SOLIT-prior identification question was removed from the Level 3 form, and `analysis/level3_aggregate.py` implements no L3-5 analysis. SOLIT reviewers are retained only as *motivating pilot context* (Results Finding 5c), not as a longitudinal-stability analysis.
- The line-68 clause is therefore superseded: read it as "Inclusion of SOLIT reviewers as motivating pilot context — the L3-5 longitudinal-stability analysis itself is dropped per the section above."

### A3. `PREREGISTRATION_LEVEL2.md` — numbering typos (cosmetic, no effect on any analysis)
- Limitations list (lines 104–105): two consecutive items are both numbered "5." Read as items 5 ("Self-preference n=4") and 6 ("Persona names visible").
- Cross-references to the length-confound analysis as "Secondary outcome 5" (lines 87, 106) should read **"Secondary outcome 6"**; in the pre-specified plan #5 is the outsider-juror (Kimi) baseline and #6 is the length confound.

---

## B. Executed-vs-registered deviations (disclosure)

### B1. Self-preference non-parametric test: sign test in place of Wilcoxon/permutation
`PREREGISTRATION_LEVEL2_ADDENDUM.md:41` specifies, as the replacement for the dropped mixed model, "bootstrap 95% CIs … and a paired non-parametric test (Wilcoxon signed-rank or permutation) on the four-vendor within-juror Δ vector." Executed: bootstrap 95% CIs (retained) **plus an exact one-sided sign test** (all four within-juror Δ positive → p = 0.5⁴ = 0.0625). With n = 4 all-positive deltas, Wilcoxon signed-rank / permutation are degenerate; the exact sign test is the defensible non-parametric choice. Disclosed; manuscript methods updated to match.

### B2. Bootstrap resamples: 10,000 executed vs 1,000 registered
`PREREGISTRATION_LEVEL2.md:102`, its addendum, and the manuscript methods stated "1000 resamples." Both executed scripts (`level2_stats.py`, `level3_aggregate.py`) use **10,000**. This increases precision and does not bias the percentile CIs. `manuscript/methods_draft.md` corrected to "10,000."

### B3. Per-criterion ICC(3,1): registered, initially not emitted, now computed
`PREREGISTRATION_LEVEL2.md:83` registers "ICC(3,1) … computed per criterion **and** on the weighted total." The first stats run emitted only the weighted-total ICC. As of 2026-06-21, per-criterion ICC(3,1) is computed and written to **`analysis/level2_criterion_icc.csv`** (5 criteria × 5 jurors; all in 0.74–1.00), closing the gap. Manuscript methods now point to both ICC outputs.

### B4. Cross-run (R1 vs R2) descriptive comparison: registered, now emitted as a labeled output
`PREREGISTRATION_LEVEL2.md:88` (Secondary outcome 7, "Cross-run effect," descriptive only) is now produced by `level2_stats.py` and reported in `level2_stats_report.md`: mean weighted total R2-vintage stories (S_02/S_03/S_04/S_06) = 7.17 vs R1-vintage (S_01/S_05/S_07/S_08) = 5.84 (descriptive only; the R2 stories dominate the top tier).

### B5. Extractor script rename (already disclosed)
The planned `analysis/level2_aggregate.py` was implemented as `analysis/level2_extract.py` (parser) + `analysis/level2_stats.py` (statistics). Disclosed in `PREREGISTRATION_LEVEL2_ADDENDUM.md` §1.

### B6. Word-count discrepancy between the two private story keys (non-load-bearing)
`human_jury_handoff/STORY_KEY_PRIVATE.md` and the Level 2 pipeline report slightly different word counts for the same stories (e.g. S_07 1066 vs 1077; ~1–2%), because the Level 2 bundles (seed 42) and the Level 3 handoff (seed 100) were tokenised/anonymised through different scripts. No reported statistic depends on these counts. Reconcile to a single counting basis (or annotate each key with its basis) before public release.

---

## What is NOT changed
The locked pre-registration bodies themselves remain byte-for-byte as locked on 2026-05-23/24. The top-3 Level 3 story selection rule, the four-story Level 3 design (top-3 + S_04 anchor), the n≥5 minimum, and all primary estimands are executed exactly as registered (verified independently in `analysis/RESEARCH_AUDIT_2026-06-21.md`).
