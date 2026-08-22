# analysis/ — verification layer

One script per analysis step; run order and expected headline outputs are in the repository root's [`REPRODUCE.md`](../REPRODUCE.md). Freshly generated CSVs land here; the checked-in reference copies are in `expected_outputs/` for comparison (a fresh clone has no CSVs at this level until you run the scripts).

Scripts are dependency-light on purpose (see `../requirements.txt`); each prints its headline numbers when run. Two structural notes: the extraction scripts expect the shipped filenames verbatim (`juries/llm/responses/SCORING STORY S_0X.md`), and `juries/human/responses_anonymized.csv` is read by column position, so its empty `Timestamp` column is load-bearing. Story word counts differ slightly across files by counting method; `story_style_metrics.csv` is the analysis-canonical count.
