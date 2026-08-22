# Pre-registration: Prestige-gradient control experiment

**Project**: Persona convergence in LLM-generated biographies — CFS 2026 submission
**Date locked**: May 23, 2026
**Author**: Michaela Liegertová
**Status**: Locked before any control generations are produced. Any deviation from this protocol must be documented in the manuscript.

---

## Background and motivation

In an exploratory cross-model case series (4 LLM families × 2 timepoints, 2025 and 2026, plus n=3–5 replicates per Run 2 cell), we observed that **biographical personas generated in response to the prompt "exceptional prose writer" converge tightly on a specific cultural-political-demographic archetype**: female (18/20 in Run 2, 90%), multilingual childhood (20/20, 100%), Eastern/Central European, Balkan, MENA, or post-colonial origin (19/20, 95%), dissident or politically-persecuted family (~95%), late-blooming Nobel laureate (~95%, mostly 2018). The upstream priming corpus (deep-research reports by the same models) cites a ~75% male canonical exemplar set — implying the gender flip and demographic concentration emerge at *generation time*, not from priming.

We hypothesize that this convergence is driven, at least in part, by the **prestige framing** of the prompt ("exceptional"). Lower-prestige framing should produce a different demographic distribution — closer to the model's underlying writer-baseline rather than the prestige-archetype attractor.

This pre-registration locks the prediction *before* any control generations are produced.

## Primary hypothesis

Demographic convergence (on female / displaced / multilingual / Eastern-European-or-MENA / Nobel-laureate archetype) is a function of prompt prestige. Specifically:

> **H1**: Female fraction, multilingual-childhood rate, and exile/displacement trope frequency will be **highest** in the high-prestige condition ("exceptional prose writer"), **lowest** in the explicit low-prestige condition ("average writer persona"), and **intermediate** in the neutral condition ("random writer persona"). The relationship will be monotonic across the three conditions.

## Conditions

Three persona-generation conditions, all run on the same four LLM families (GPT-5.5, Claude Opus 4.7, Gemini 3.1, Grok 4.3) via vendor web interfaces:

| Condition | Prompt | Status (May 23, 2026) |
|---|---|---|
| **HIGH prestige** | Full original Phase 1 + Phase 2 prompt: "exceptional prose writer" with deep-research priming, named exemplars, biographical pattern guidance | **Already collected**: n=20 (n=5 per model) |
| **NEUTRAL prestige** | "Create a random writer persona." | **To be collected**: n=12 (n=3 per model) |
| **LOW prestige** | "Create an average writer persona." | **To be collected**: n=12 (n=3 per model) |

All conditions use:
- Vendor web interface (no API)
- Fresh chat session per generation (no cross-contamination)
- Default vendor settings (no system prompt modifications)
- Vendor share URLs preserved for verification
- Same coding rubric applied blind

## Primary outcome variables (locked)

The following variables will be coded by two independent coders, blind to condition. Cohen's κ reported per variable.

1. **Gender** (binary: female / male; "other" if explicit)
2. **Multilingual childhood** (binary: 2+ languages spoken in family of origin)
3. **Region of origin** (categorical, collapsed for analysis to: Mitteleuropa/Balkan, MENA/Levantine, African diaspora, Latin American, Western European, North American, East Asian, South Asian, Other)
4. **Family persecuted by state or political violence** (binary)
5. **Exile or displacement from country of origin** (binary)
6. **Late-blooming (first major work after age 40)** (binary; coded NA if no career timeline given)
7. **Nobel Prize or other major literary prize** (binary; if Nobel, year recorded)
8. **Synesthesia or cross-modal perception** (binary, explicit or implicit)

Secondary descriptive variables (no FDR correction applied): length of generated text, number of named foreign-language words, number of named real writers cited as influence.

## Statistical analysis (locked)

### Primary test: monotonic trend across prestige levels

For each binary outcome (variables 1, 2, 4, 5, 6, 7, 8 above), the **Cochran-Armitage trend test** will be applied across the three conditions, with prestige level coded ordinally (low=1, neutral=2, high=3). One-sided test in the direction of the prediction. Benjamini-Hochberg FDR correction at q=0.05 applied across the seven binary outcomes.

### Secondary test: pairwise condition differences

For each binary outcome, pairwise **Fisher's exact tests** comparing:
- HIGH vs NEUTRAL
- HIGH vs LOW
- NEUTRAL vs LOW

Pairwise comparisons treated as secondary; reported with effect sizes (odds ratios + Wilson 95% CIs) without additional FDR correction beyond the primary trend test.

### Categorical region variable

Distribution of region categories across conditions compared with **chi-square goodness-of-fit** (or Fisher-Freeman-Halton exact test if cell counts < 5). Cramér's V reported as effect size.

### Per-model breakdown

Because we have observed vendor-specific differences in the HIGH condition (Gemini 3.1 produced 2/5 male; other three vendors 0/5), all primary analyses will be repeated **separately per vendor**. We pre-register the prediction that the monotonic prestige effect will be observed *in all four vendors*, with effect sizes possibly differing.

## Possible outcomes and interpretation

The pre-registered hypothesis predicts a monotonic gradient. Three meaningful outcomes are possible:

| Outcome | Pattern | Interpretation |
|---|---|---|
| **A. Monotonic confirmation** | HIGH > NEUTRAL > LOW for all outcome variables | Prestige framing drives the convergence. The Tokarczuk-shape attractor is a prestige-coded archetype. Consistent with Chen et al. 2025. |
| **B. Flat** | All three conditions converge similarly | The bias is in the model's writer-baseline prior, not the prestige cue. Stronger finding for the "RLHF-deep-default" interpretation. |
| **C. Reverse** | LOW > NEUTRAL > HIGH or non-monotonic | The model has a stronger "average woman writer" archetype than "exceptional woman writer" archetype. Unlikely but would be a striking inversion of expected priors. |

Each outcome is publishable. The pre-registration commits to reporting whichever outcome obtains, without post-hoc reframing.

## Sample size justification

n=3 per (condition × model) = n=12 per condition. Total new generations: 24.

This is small by NLP-bias-audit standards (e.g., Pikuliak et al. 2025 *GenderBench* recommends n≥10 per cell) but appropriate for the case-series framing of the present study. We pre-register the limitation explicitly: with n=12 per condition, Wilson 95% CIs on proportions will be approximately ±15 percentage points, and the Cochran-Armitage trend test has moderate power for detection of monotonic effects. We do not claim within-condition distributional generalization; we claim only sufficient power to detect a strong monotonic gradient if present.

## What this pre-registration does NOT cover

The following analyses are explicitly *not* pre-registered and will be reported as exploratory:

- Stylometric features (sentence length, type-token ratio, function-word distribution) of the generated outputs
- Sentence-embedding pairwise cosine distances within and between conditions
- Named-entity extraction and frequency analysis of locations/languages mentioned
- Cross-comparison between Run 2 outputs and the n=4 Run 1 (2025) outputs
- Story-level analysis of any Phase 3 outputs from these new conditions (none planned)

These exploratory analyses will be clearly labeled as such in the manuscript.

## Deviations protocol

If at any point we deviate from this pre-registered protocol — e.g., adjusting the prompt wording, changing condition assignment, modifying the statistical test — the deviation will be documented in the manuscript with date and justification. We will report results both with and without the deviation, where possible.

## Data availability

All generated personas (including conditions HIGH, NEUTRAL, and LOW), vendor share URLs, coding spreadsheets, statistical analysis code, and pre-registration document will be made publicly available at paper acceptance via GitHub (target: `github.com/[author]/cfs-persona-convergence-2026`) under CC-BY-4.0.

## Timestamp

This document is locked at **May 23, 2026** (date of writing this version), before any NEUTRAL or LOW prestige generations have been collected.

A SHA-256 hash of this file, plus the rendered version on OSF, will serve as the timestamp anchor.

---

## Signatures

**Lead author**: Michaela Liegertová (date locked: _______)

**Witness** (any independent observer who can vouch for the date of locking): _______
