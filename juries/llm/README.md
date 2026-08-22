# juries/llm — the LLM jury (Level 2)

Five LLM jurors — Claude Opus 4.7, GPT-5.5, Gemini 3.1 Pro, Grok 4.3, and Kimi 2.6 — blind-scored all eight stories, three repetitions each, inside a fictitious literary-prize frame ("Meridian Prize"). The first four each generated one story in the corpus, which makes them self-interested jurors; Kimi generated none and serves as the outsider comparator.

- `PROMPT_juror.md` — the juror commissioning prompt; each juror received it with one story appended (see `eval_bundles/`).
- `anonymized_stories/` — the stories exactly as jurors received them: identifying headers stripped, IDs only. Persona names occurring *inside* story text were retained by design (a documented limitation — e.g. S_07's narrator is addressed by her persona's name). A juror could in principle match such a name to a vendor if it already knew the project's persona-to-vendor mapping, which was not public at the time; the pre-registration records this as a residual blinding limitation rather than a guarantee.
- `eval_bundles/` — the complete evaluation bundles sent to each juror (prompt + story, verbatim).
- `responses/` — the 120 raw juror evaluations in eight per-story files (five jurors × three repetitions per file), labelled by juror and `N=`. The written justifications are worth reading in their own right: they are machine literary criticism.

Scores are parsed from the responses by `analysis/level2_extract.py` and analyzed by `analysis/level2_stats.py`; reference copies of all derived CSVs live in `analysis/expected_outputs/`. The scripts expect the shipped response filenames verbatim.
