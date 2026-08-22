# Follow-up: earlier correction notes closed — 2026-08-20

Two of the earlier correction notes recorded an action that was still open when they were written. Both are now closed. The original notes are preserved verbatim as dated records; this note supersedes them on these two points.

## 1 · Run 1 date — confirmed (closes the action in `PREREGISTRATION_CORRECTIONS_2026-07-02.md`)

The 2026-07-02 note re-dated Run 1 from May 2025 to **July 2025** on forensic grounds: vendor conversation identifiers decoding to 24–25 July 2025, and the public release date of one of the Run 1 models (Grok 4, 9 July 2025), which makes a May 2025 run with that model impossible. The note asked the lead author to confirm the dating against her own vendor chat histories.

**Confirmed by the lead author on 2026-08-20: Run 1 was conducted in July 2025.** The dating in the methods and manuscript therefore rests on author testimony as well as on the forensic reconstruction, and the action is closed. The locked pre-registration files retain "May 2025" unedited, per the project's policy of never altering frozen documents; this note and the 2026-07-02 note together are the correction record. The interval between runs is approximately ten months (July 2025 → May 2026).

## 2 · Story word counts — canonical basis designated, second basis disclosed (closes the action in `PREREGISTRATION_CORRECTIONS_2026-06-21.md`)

The 2026-06-21 note observed that story word counts differed slightly between files depending on the counting method, and asked that they be reconciled to a single basis before public release. **Resolved, with one basis-dependence disclosed.** `analysis/story_style_metrics.csv` is the canonical word count for style analysis, computed by a single documented method (whitespace tokens in the story body, title line excluded) in `analysis/story_style_metrics.py`; this is stated in `analysis/README.md`. One other count remains in the repository by design: `analysis/level2_stats.py` computes its own word count (a different tokenizer, title line included) for the pre-registered length-confound outcome, and ships it as the `word_count` column of `level2_story_rankings.csv`. The two differ by 2–17 words per story.

That difference is not cosmetic and should be stated plainly: the length-versus-score rank correlation reported in the Level 2 statistics log is **ρ = 0.43 on the pipeline's own basis and ρ = 0.55 on the canonical basis**. The pre-registered analysis is the pipeline's, and it is reported unchanged; the alternative basis is recorded here so that a reader recomputing it from `story_style_metrics.csv` finds the discrepancy explained rather than surprising. No claim in the paper rests on either value.

## 3 · Collection labels normalized in this public tree (2026-08-22)

At collection time the one-line archival labels at the top of the corpus files varied in format, and several files carried none; `EXTRACTION_CORRECTIONS_2026-08-20.md` describes that earlier state (including one relabelled Grok header, reasoned there). On 2026-08-22, for this public tree, every model-output file's label was normalized to equal its filename — labels are packaging, added or replaced at build time; the model text below each label is untouched, and the authors' archive preserves the files exactly as collected. This note supersedes the label descriptions in the earlier dated documents, which refer to the archive state.
