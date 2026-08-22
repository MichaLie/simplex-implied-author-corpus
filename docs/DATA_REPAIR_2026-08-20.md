# Level 2 data repair — recovered juror response (2026-08-20)

## What was wrong

A pre-release integrity audit of the 120 LLM-jury evaluations found one duplicated response: in `juries/llm/responses/SCORING STORY S_05.md`, the block recorded as **Grok, repetition 2** was byte-identical to the **GPT, repetition 2** block in the same file — a copy-paste error made while transcribing the jury sessions into the response files on 2026-05-24. Formatting fingerprints (table padding and bullet style, which differ consistently between the two jurors' outputs) confirmed the duplicated text was GPT's. Grok's genuine second S_05 evaluation was therefore missing from the dataset, and GPT's was counted twice. A similarity sweep across all 120 blocks found no other duplication.

## Recovery

The original Grok session was located in the lead author's vendor chat history (the Level 2 sessions were run one chat per story, with the three repetitions captured as three regenerated responses in the same chat). The S_05 chat contains exactly three Grok evaluations:

| Scores (LM / O / EI / TD / SC) | Where recorded | Status |
|---|---|---|
| 7, 5, 6, 6, 7 | recorded in the dataset (rep 3) | present |
| 7, 5, 7, 6, 7 | recorded in the dataset (rep 1) | present |
| **7, 5, 7, 6, 8** | **absent from the dataset** | **recovered** |

The recovered evaluation — scores, justifications, and overall assessment — was restored to the repetition-2 slot on 2026-08-20 by the lead author, working from the original conversation in her vendor account. Repetition labels are exchangeable (the three are independent regenerations of the same prompt in the same session), so the restored set is now complete and correctly attributed.

**What was and was not preserved, precisely.** The wording is verbatim: nothing was regenerated, rewritten, or paraphrased, and no fresh model call was made — a 2026 call to the current model would not be the May 2026 session and would not have been a recovery. The *markdown formatting* was not preserved: the block was re-typed into the file's table-and-bullet conventions during restoration. This matters more than it might seem, because it interacts with the diagnostic above. Table padding and bullet style are near-perfectly juror-consistent across the other 119 blocks, and the restored block now carries the padded-table, asterisk-bullet style characteristic of GPT rather than Grok's compact style. **The fingerprint therefore identifies the defect but cannot authenticate the repair**, and readers should not treat it as doing so. What does support the attribution is the content: the block's nearest neighbours by lexical overlap are the two other Grok S_05 evaluations rather than any GPT block, and it uses straight quotation marks, which appear in Grok's output in this corpus and never in GPT's.

**Limits of verification.** A reader can independently reconstruct and check the *pre-repair* state — the defective block was a copy of the GPT repetition-2 block, which remains in the file, so every "before" figure in the table below can be recomputed from the shipped data. A reader cannot independently verify the *provenance of the replacement text*, which rests on a private vendor conversation and on author testimony. That asymmetry is the residual limitation of this correction. The superseded file is retained in the authors' archive and can be supplied on request.

## Effect on results

Confined to S_05 and to Grok's non-self baseline. **No number changes for the four stories the human jury evaluated (S_02, S_04, S_06, S_07), and no Level 3 result changes.**

| Quantity | Before | After |
|---|---|---|
| S_05 mean weighted score | 4.45 (SD 0.92) | **4.56 (SD 1.06)** |
| S_05 rank / top-3 count / Borda | last of eight, 0, 27.0 | unchanged |
| Overall Kendall's W | 0.8558 | 0.8558 |
| Per-criterion W: Emotional Impact | 0.8983 | 0.9005 |
| Per-criterion W: Structural Craft | 0.8902 | 0.8952 |
| Grok within-juror self-preference Δ | 0.4048 (CI −0.11 … 0.96) | **0.3238 (CI −0.13 … 0.79)** |
| All Level 3 values, all other stories | — | unchanged |

Substantive conclusions are unaffected: S_05 remains the lowest-scored story in the corpus and the low-dispersion bottom of the U-shaped agreement pattern, and Grok's within-juror self-preference remains small with a confidence interval spanning zero.

Derived CSVs and figures were regenerated from the corrected response file on 2026-08-20.
