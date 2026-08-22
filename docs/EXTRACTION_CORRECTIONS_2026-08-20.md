# Masters-roster corrections — 2026-08-20

Following two independent pre-release reviews of the dataset (2026-08-20), three region codings of real writers in the fixed exemplar roster (`analysis/extract_report_exemplars.py`) were corrected:

| Writer | Old region | Corrected region | Reason |
|---|---|---|---|
| Saul Bellow | EE_Balkan | N_American | Born Lachine, Quebec; raised Chicago; canonical North American novelist. The old code reflected parental heritage only. |
| Thomas Bernhard | EE_Balkan | Western_EU | Austrian, German-language postwar prose. |
| Henry James | Western_EU | N_American | Born New York; naturalized British only in 1915. |

**Effect on published numbers.** Gender counts are unchanged (R1: 42 named, 31.0 % female; R2: 61 named, 19.7 % female — the "roughly 70–80 % male" claim is unaffected). Region tallies shift: R2 EE/Balkan exemplars 9 → 7 (pct 14.8 → 11.5), R2 N_American 21 → 23, R2 Western_EU 18 (net unchanged); R1 N_American 12 → 13, Western_EU 11 → 10. The corrected values supersede earlier tallies wherever report-side regional composition is cited. The corrections *sharpen* the personas-vs-reports asymmetry (report-side Central/Eastern European share falls; persona-side remains 11/20).

**A note on the coding rubric.** One decision-rule example in the coding rubric (`number_EE_Balkan_exemplars`: "Count Sebald (German), Bernhard (Austrian)…") predates these corrections; the rubric is preserved as the instrument the coders received, and the corrected roster together with this note governs.

## Collection-label normalization (same date)

Seven researcher-added first-line collection labels in the corpus files were corrected for typos and formatting slips (`avarage_writer` → `average_writer`; a doubled `# #` in three files; a stray leading word; `Opu47` → `Opus47`). Labels are packaging added at collection time, not model output; no model-generated text was altered. Most Run 1 files carry no label and open directly with model output; one (`R1_report_Opus4.md`) retains its original filing label, left as collected.

One correction needs its reasoning recorded. The label on the Run 2 Grok primary persona read `Nadia_Voss_Grok_42`, which — since both Grok 4.20 (released February–March 2026) and Grok 4.3 (released early May 2026) were available on the collection date of 23 May 2026 — could have denoted a different model version rather than a typo. The vendor interface does not display model versions for past conversations, so the question was settled from the collection records: the contemporaneous share-URL log lists this exact conversation under "Grok-4.3 Persona"; the file name, the corpus index, the methods table, the pre-registration, and the five other Grok files from the same run all record Grok 4.3; and the anomalous label also lacked the replicate suffix its siblings carry. The label was normalized to `Nadia_Voss_Grok43_n1`. All Run 2 Grok generations are therefore recorded as Grok 4.3.

**What was deliberately left unchanged.**
- Bare "White" in R1_GPTo3's masters list remains unmatched: the roster matches unambiguous name forms only, and "White" alone is ambiguous between E. B. White and Patrick White (Nobel 1973). Recorded here as the instrument's disambiguation rule rather than silently resolved.
- Writers named in reports but outside the fixed roster (Thomas Hardy, John Updike, Benjamin Franklin, Sir Thomas Browne, Shakespeare, Eva Hoffman) remain outside it. The roster is a **fixed 88-name checklist designed in advance**, including writers deliberately listed as *expected absences* (Tokarczuk, Müller, Alexievich, Han Kang, Lispector, and others resembling the persona archetype) to test whether the critic reports would cite them — an absence probe, not an open-ended extraction. Sensitivity analysis in the audit showed that adding all defensibly missed writers moves the gender split by at most about two points and preserves direction (R1 67.5–71.1 % male; R2 79.4–80.6 %).

Locked pre-registration files are unaffected. Derived CSVs (`report_writer_extraction.csv`, `report_writer_counts*.csv`) regenerated from the corrected script on 2026-08-20.
