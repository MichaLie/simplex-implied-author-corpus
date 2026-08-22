# Pre-registration v1 — Addendum

**Document type**: post-data addendum to a locked pre-registration
**Date of original lock**: May 23, 2026 (`PREREGISTRATION_v1.md`)
**Date of addendum**: May 23, 2026 (same day, immediately after control data returned and analysis completed)
**Author**: Michaela Liegertová

This addendum records, *honestly and contemporaneously*, what the pre-registered analysis predicted, what the data actually showed, and how the paper's framing was revised in response. It is intended to make the audit trail visible. The original `PREREGISTRATION_v1.md` is preserved unedited; this addendum sits beside it.

---

## What was pre-registered

`PREREGISTRATION_v1.md` (May 23, 2026, locked before NEUTRAL and LOW prestige generations were produced) recorded the following primary hypothesis:

> **H1**: Female fraction, multilingual-childhood rate, and exile/displacement trope frequency will be **highest** under high-prestige framing ('exceptional prose writer'), **lowest** under explicit low-prestige framing ('average writer'), and **intermediate** under neutral framing ('random writer'). The relationship will be monotonic across the three conditions.

Three pre-registered controls:
- HIGH: full Phase 1 + Phase 2 scaffolded prompt
- NEUTRAL: "Create a random writer persona."
- LOW: "Create an average writer persona."

Pre-registered primary statistical test: Cochran-Armitage trend across the three conditions with BH-FDR correction at q=0.05.

## What the data showed

Generated n=12 per control condition (4 model families × n=3 per cell). Coding pass yielded the following gender distributions:

| Condition | n | Female | Male | NB/unspecified | % female |
|---|---|---|---|---|---|
| HIGH | 20 | 18 | 2 (both Gemini) | 0 | 90% |
| NEUTRAL ("random") | 12 | 4 | 6 | 2 | 33% |
| LOW ("average") | 12 | 6 | 0 | 6 | 50% |

**The prediction of monotonicity is NOT supported.** Female fraction is higher in LOW (50%) than in NEUTRAL (33%). The relationship is non-monotonic (V-shaped, with NEUTRAL the trough).

Similarly, the other pre-registered outcome variables (multilingual childhood, exile/displacement) do not follow the predicted monotonic gradient. They drop sharply from HIGH to either control, but the controls produce *different* archetypes from each other rather than a smooth gradient.

## What was learned beyond the prediction

The data revealed an unanticipated three-attractor structure: each prompt condition retrieves a *culturally specific* default, not a quantitative gradient of the same archetype.

| Condition | Resulting archetype |
|---|---|
| HIGH | Female Eastern-European or post-colonial multilingual displaced writer, dissident family, 2018 Nobel |
| NEUTRAL | Literary-eccentric, age ~42, often male, gothic/magical-realism, lighthouse motif, recurring name "Elias" |
| LOW | American suburban Columbus-Ohio area, female-or-NB, content-marketing day job, NaNoWriMo + Scrivener + Substack, imposter syndrome universal |

This is descriptively more interesting than the monotonic prediction would have been, but it requires a different analytical apparatus (descriptive heat maps + qualitative archetype identification) rather than the pre-registered trend test.

## Acknowledged methodological confound

In addition to the substantive non-monotonicity, two AI-reviewer feedbacks (GPT and Gemini, independently, May 23, 2026) identified a control-design confound that compromises the pre-registered test even if the data had been monotonic:

The HIGH-prestige prompt also imposes dramatic structural scaffolding (sections, length, biographical-template) that the NEUTRAL and LOW prompts lack. Output median length differs ~7-10× across conditions (HIGH ~2,500 words; NEUTRAL ~250 words; LOW ~340 words). Many of the pre-registered outcome variables (e.g., "multilingual childhood") cannot appear in the controls because the controls never request childhood content. The pre-registered trend test would therefore have detected an *artifact of prompt-richness*, not an isolated effect of prestige.

A cleanly prestige-isolated test would require structurally-matched controls (same length, same sections, only the prestige word changed). This was not done.

## Framing revision

In light of (a) the partial refutation, (b) the structural-scaffolding confound, and (c) a deeper reread of the original research design's intent (the study was originally about LLM aesthetic synthesis of literary-excellence theory, not about LLM demographic-bias auditing), the paper's central framing was revised on May 23, 2026 from:

> *"Prestige-gradient demographic bias in LLM persona generation"*

to:

> *"LLM aesthetic synthesis: when models are asked to instantiate abstract criteria for literary excellence into a concrete Nobel-laureate biography, what do they retrieve, and what do they implicitly add beyond the criteria?"*

This reframe redirects the central analytical comparison from HIGH-vs-NEUTRAL-vs-LOW to **reports-vs-personas-vs-real-laureate-baseline**, specifically the report-to-persona embodiment-and-addition matrix. See `docs/FINDINGS_v1.md` for the full analytical state.

## What changes, and what stays

### Stays in the paper
- The HIGH-prestige n=20 corpus and its findings (90% female, 95% post-imperial-exile, vendor-specific patterns, two Gemini male outliers, 2018-Nobel anchor)
- The cross-temporal 2025 → 2026 comparison
- The reports-vs-personas asymmetry (the central evidence for the implied-author claim)
- The NEUTRAL and LOW controls, repurposed as **supporting evidence**: "without research scaffolding, models do not produce the displaced-multilingual archetype; the archetype is specific to theory-synthesis tasks, not a universal default"
- The cross-vendor design (Claude, GPT, Gemini, Grok)
- The 8 short stories (now framed as persona-bio embodiment, not autonomous fiction)

### Removed or downgraded
- The pre-registered monotonic prediction is reported as **partially refuted** in the manuscript's results section
- The Cochran-Armitage trend test as the primary statistical instrument
- The claim that "prestige isolates the active ingredient" — replaced by "the archetype is condition-specific; minimal prompts produce different defaults"

### Added in the reframe
- Arielli's "implied author" framework as the conceptual spine
- D'Isa's "semantic attractors" as naming vocabulary (the "Tokarczuk attractor" terminology comes from this)
- Casanova's *World Republic of Letters* as the human-side explanation for the prestige-economy shape of the retrieved archetype
- The embodiment-and-addition matrix as the central analytical instrument
- The report-to-persona comparison as central descriptive evidence

## Why this addendum is being made visible

In the spirit of the open-science norms the pre-registration was meant to embody, this addendum is timestamped and dated alongside the original pre-registration document. It records the partial refutation honestly. We report it openly rather than reframing the paper as if it had been the planned analysis all along.

The pre-registration *worked*: it committed us to a falsifiable prediction in advance, and the data refuted part of it. That refutation produced a more interesting finding than the prediction would have yielded. We report both the original prediction and what the data showed.

## Pending pre-registration update

Before any further controls are run (e.g., the structurally-matched prestige controls discussed as future work), a v2 pre-registration will be locked on OSF that records the revised framing and any new predictions. This is on the task list (`task #10`).

## Document chain

- `docs/PREREGISTRATION_v1.md` — original pre-registration, locked May 23, 2026, preserved unedited
- `docs/PREREGISTRATION_v1_ADDENDUM.md` — this file
- `docs/FINDINGS_v1.md` — canonical analytical state under the reframe
- Future: `docs/PREREGISTRATION_v2.md` — to be locked on OSF before further controls

## Signatures

**Lead author**: Michaela Liegertová (date: _______)

**Witness** (any independent observer who can vouch for the date): _______
