# Pre-registration — Level 2 (LLM jury evaluation of the 8-story corpus)

*Locked: May 24, 2026. This document succeeds and complements `PREREGISTRATION_v1.md` and `PREREGISTRATION_v1_ADDENDUM.md`. It pre-specifies the Level 2 LLM-jury sub-study before any evaluation sessions are run.*

## Aim

Test whether independent LLM jurors — each given the same neutral evaluator prompt — converge on the same top-ranked stories from the 8-story SIMPLEX/CFS corpus, and identify the top 3 stories for follow-up human-expert evaluation. Secondary aim: estimate within-LLM scoring reliability and between-LLM agreement, and characterize the LLMs' implicit aesthetic priors for literary short fiction.

## Pre-specified design

**Mode**: per-story independent evaluation. Each story is evaluated in a fresh chat session containing one story only. No cross-story comparison is requested. Rankings across the 8 stories are derived post-hoc from independent numerical scores.

**Rationale for per-story over all-at-once**: an all-at-once design (8 stories in one chat) introduces anchoring, position, and fatigue effects that confound the per-story aesthetic judgment we want to measure. Per-story independence removes those effects at the cost of losing forced comparative ranking; rankings are reconstructed numerically.

**Juror prompt**: single neutral evaluator persona ("an experienced reader of contemporary literary fiction, known for thoughtful, careful, and discriminating judgment"). Same prompt across all sessions. See `level2_jury/eval_bundles/` for the verbatim prompt; the prompt is also embedded at the head of every eval bundle.

**Rationale for neutral juror vs. v1 5-persona Meridian panel**: the v1 5-persona roleplay panel produced narrative deliberation, not comparable scores. A single neutral juror persona — same prompt across LLMs — exposes each LLM's own aesthetic prior cleanly and yields directly comparable structured output.

**Anti-ceiling protection**: ceiling effects are countered through (a) juror-persona framing ("demanding but specific"), (b) descriptive scale anchors at every score point, and (c) per-criterion requirement of 2–3 sentences of justification grounded in textual evidence. **No distributional instruction** is given (i.e., the prompt does NOT tell the model what the expected distribution of scores looks like).

## Sample

- **Stories evaluated**: 8 stories from the SIMPLEX/CFS corpus (4 from Run 1 / May 2025, 4 from Run 2 / May 2026). Blinded IDs `S_01`–`S_08`, mapping fixed by `random.Random(42).shuffle` in `level2_jury/build_eval_bundles.py`. Private key in `level2_jury/story_key_PRIVATE.md`.
- **Anonymization**: filename headers and LLM-generated preambles stripped; character names inside the story bodies retained (literary content). See `level2_jury/anonymized_stories/`.
- **LLM jurors**: 5 model families, accessed via vendor web interfaces at default settings:
  - **Claude Opus 4.7** (Anthropic)
  - **GPT-5.5** (OpenAI)
  - **Gemini 3.1 Pro** (Google)
  - **Grok 4.3** (xAI)
  - **Kimi 2.6** (Moonshot AI) — outsider juror; did **not** participate in any prior phase of the SIMPLEX/CFS study and generated none of the 8 stories
- **Note on Run 1 models**: the 2025 models (GPT-o3, Claude Opus 4, Gemini 2.5 Pro, Grok 4) are no longer publicly accessible and are therefore not used as jurors. The 4 Run-2 vendors used as jurors did each generate one of the four Run 2 stories under evaluation; this is addressed analytically through the self-preference and outsider-juror analyses (see "Pre-specified analysis plan").
- **Reps per juror per story**: n=3 (fresh chat session per rep).
- **Total sessions**: 5 × 8 × 3 = **120 evaluation sessions**.
- **Stopping rule**: 120 sessions complete. No extension without an addendum.

## Rubric

Five criteria, identical to the v1 Meridian Prize rubric for continuity:

| Criterion | Aggregation weight | Scale |
|---|---|---|
| Literary Merit | 30% | integer 1–10 |
| Originality | 25% | integer 1–10 |
| Emotional Impact | 20% | integer 1–10 |
| Thematic Depth | 15% | integer 1–10 |
| Structural Craft | 10% | integer 1–10 |

**Weighted total** = 0.30·LM + 0.25·O + 0.20·EI + 0.15·TD + 0.10·SC (range 1–10).

**Important separation**: criterion weights are **applied only at aggregation, by the analysis script**. The juror prompt does NOT show the weights to the LLM and does NOT ask the LLM to compute the weighted total. This prevents (a) arithmetic errors from the LLM and (b) implicit balancing of scores against an internally-tracked target total. The LLM produces five independent criterion scores; aggregation is downstream.

**Scale anchors** (in prompt, descriptive only — no distributional instruction):

- 10: Exceptional. Once-in-a-decade work.
- 8–9: Strong. Award-quality writing.
- 6–7: Competent. Publishable but not memorable.
- 4–5: Flawed. Significant problems.
- 1–3: Substantially below the literary threshold.

## Output format

Each session must produce, in markdown, three sections:

1. **`### Scores`** — a 5-row table, one row per criterion, with a single integer (1–10) in the score cell. No text in the score cells; no decimals, no half-points, no ranges.
2. **`### Justifications`** — a bulleted list, one bullet per criterion, each with 2–3 sentences of textual evidence supporting the score.
3. **`### Overall Assessment`** — a single paragraph (4–6 sentences) grounded in specific textual passages.

The juror prompt **explicitly forbids** the LLM from computing a weighted total, producing a ranking, or providing commentary outside the three required sections. Score and justification are kept in separate sections to permit clean numeric parsing downstream.

Sessions failing to produce this structure are re-prompted once; failures after re-prompting are flagged in `session_tracker.csv` and excluded from analysis with explicit documentation.

## Pre-specified analysis plan

**Primary outcome: top-3 selection for human-expert evaluation.**

- For each story, compute the mean weighted total across the 15 cell-replicates (5 LLMs × 3 reps).
- Top 3 = the 3 stories with the highest mean weighted totals.
- Ties broken by Borda count on per-session derived ranks (1–8 within each session, computed post-hoc from that session's weighted totals).

**Secondary outcomes (all pre-specified):**

1. **Inter-LLM rank agreement**: Kendall's W on the rank vectors of the 5 LLMs (after averaging within-LLM reps to a single rank vector per LLM). Pairwise Spearman ρ between LLM pairs reported as supporting detail.
2. **Within-LLM reliability**: ICC(3,1) on the 3 within-LLM reps per story per LLM, computed per criterion and on the weighted total.
3. **Per-criterion agreement**: Kendall's W per criterion across LLMs. Hypothesis-generating only: we expect higher agreement on Structural Craft and Literary Merit than on Originality and Emotional Impact, but this is exploratory.
4. **Self-preference effect (vendor-jurors only)**: for each of the 4 R2-vendor jurors (Claude Opus 4.7, GPT-5.5, Gemini 3.1 Pro, Grok 4.3), compare its mean weighted total on the single R2 story it generated versus its mean weighted total on the 7 stories it did not generate. Mixed model across the 4 vendor-jurors: `score ~ story_factor + own_vs_other + (1|juror) + (1|rep)`. One-sided test: own > other.
5. **Outsider-juror baseline (Kimi 2.6)**: Kimi 2.6 generated none of the 8 stories and serves as the outsider juror. Compare Kimi's per-story mean weighted total to the average of the 4 vendor-jurors' per-story means. Spearman ρ on rank vectors (Kimi vs. average-of-4-vendor-jurors). Identifies whether the outsider juror ranks the corpus the same as the vendor jurors do; provides a null-comparison anchor for the self-preference analysis.
6. **Length confound**: Spearman ρ between story word-count and mean weighted total across all 15 evaluation cells.
7. **Cross-run effect**: mean weighted total for R1 stories (4) vs. R2 stories (4). Descriptive only — n=4 per cell is too small for inferential claims.

**Multiple comparisons**: secondary analyses are exploratory. No FDR correction applied within Level 2; results reported with Wilson CIs (proportions) or 95% CIs (means).

## What this study does NOT pre-register

- Any claim about whether the LLM jury agrees with human jurors. That comparison is the subject of the follow-up human-evaluation sub-study, which is pre-registered separately when its participant pool is finalized.
- Any claim about whether LLM judgments reflect "real" literary quality. The Level 2 study measures LLM-internal aesthetic judgment, not ground-truth literary value.
- Any claim that the LLM-jury rank order is causally driven by any specific feature of the stories (style, length, persona-origin, etc.). Self-preference and length-confound analyses are descriptive.

## Acknowledged limitations (pre-specified)

1. **Web-interface variability**: vendor-default system prompts and safety layers cannot be fully controlled. Matches the rest of the study's ecological-validity choice.
2. **n=3 reps per cell** is the minimum for within-LLM variance estimation. ICC estimates will have wide CIs.
3. **n=5 LLM jurors** is still a small panel. Kendall's W with k=5 has limited statistical power; results are reported descriptively with bootstrap CIs (1000 resamples).
4. **n=4 vs. n=4 cross-run comparison** (R1 vs R2) is descriptive only; no inferential claim.
5. **Self-preference n=4** (one R2 story per vendor-juror) is small for the mixed-model self-preference test. Effect-size estimates with 95% CIs are the primary report; significance testing is supplementary.
5. **Persona names visible in story text**: characters' first names (Elara, Magda, Lejla, Hana, Rosa, Leo, …) remain in the story body because they are part of the literary content. A juror sufficiently familiar with the SIMPLEX/CFS project could in principle recognize the source. Considered tolerable because (a) the LLM jurors have no project-specific prior, (b) the persona names are inside the story's voice, and (c) removing them would damage the literary text the experiment is meant to evaluate.
6. **Length not normalized**: stories vary in length. Addressed analytically via the length-confound check (Secondary outcome 5), not by trimming or padding.
7. **No paraphrase / prompt-variation robustness check** for the juror prompt itself. If time permits before manuscript submission, a paraphrase replication of the juror prompt may be run; if so, it is added as an addendum, not as a substitute.

## Reproducibility

- Random seed: 42, fixed in `level2_jury/build_eval_bundles.py`.
- Anonymized stories: `level2_jury/anonymized_stories/S_01.md`–`S_08.md`.
- Verbatim juror prompt: at the head of each `level2_jury/eval_bundles/S_*.md`.
- Per-session responses to be saved at `level2_jury/responses/{LLM}_{S_XX}_rep{N}.md`.
- Session log: `level2_jury/session_tracker.csv`.
- Aggregation and statistics: `analysis/level2_aggregate.py` (to be written after sessions complete, before any post-hoc inspection of mean scores).
- The aggregation script will be committed before any cell-level numerical inspection beyond the per-session structured output.

## Schedule

- Pre-registration locked: 2026-05-24.
- Sessions: target completion by mid-June 2026 (well before the July 1 CFS abstract deadline; Level 2 results may or may not be ready in time for the abstract — abstract claims are independent of Level 2 outcomes).
- Aggregation + analysis: late June 2026.
- Top-3 stories selected by July 2026; human-expert evaluation begins.

## Authorship and audit

- Sole runner / lead author: Michaela Liegertová.
- Analytical partner (this pre-registration and the analysis code): Claude (Anthropic), used as a drafting and methodological partner.
- No conflicts of interest beyond the disclosed use of LLMs as the system under study and as analytical assistants.

— end —
