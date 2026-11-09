# Reproducing the paper's numbers

Environment: Python ≥ 3.10. From the repository root:

```
pip3 install -r requirements.txt
```

(Commands below use `python3`/`pip3`, the names available on a stock macOS or Linux system; plain `python`/`pip` work too where they exist.)

Run the steps in order (each script prints its headline numbers and writes CSVs into `analysis/`):

| # | Command | Regenerates | Headline check |
|---|---|---|---|
| 1 | `python3 analysis/compute_kappa.py` | inter-coder reliability table | 32 of 53 variables κ ≥ 0.70 |
| 2 | `python3 analysis/extract_report_exemplars.py` | masters roster counts | R1: 42 master-mentions across 24 distinct writers, 31.0 % female · R2: 61 across 34, 19.7 % female |
| 3 | `python3 analysis/level2_extract.py` | LLM-jury scores from the 120 raw evaluations | 120/120 parsed, 0 flags |
| 4 | `python3 analysis/level2_stats.py` | rankings, concordance, self-preference | top: S_06 8.66 · S_02 8.38; prints overall Kendall W = 0.856 (per-criterion W 0.84–0.90 in `level2_criterion_kendall_w.csv`) |
| 4b | `python3 analysis/level2_self_preference_vintage.py` | self-preference with the run-vintage correction; jury means without each story's own vendor | difference-in-differences: Claude +1.46 · GPT +0.26 · Gemini +1.78 · Grok +3.47; top five unchanged without own vendor |
| 5 | `python3 analysis/level3_aggregate.py` | human-jury scores & comparison | S_07 6.50 > S_06 4.57 > S_04 4.50 > S_02 4.40; humans downgrade the LLM top tier (S_02 −3.98, S_06 −4.09; bootstrap CIs exclude 0) |
| 6 | `python3 analysis/story_style_metrics.py` | surface style metrics for all eight stories | mean words/sentence: S_03 42.5 · S_04 41.3 · S_02 38.3 · S_01 30.5 · S_08 20.4 · S_05 15.2 · S_07 12.3 · S_06 8.7 |
| 7 | `python3 analysis/sensitivity_analyses.py` | robustness checks reported in the supplement (printed and saved to `analysis/sensitivity_summary.txt`) | attractor's gender/multilingual/outsider components hold without the Gemini subset (the 2018 component weakens); S_07 is first under every single-reader exclusion; the lower three ranks reorder in each |
| 8 | `python3 figures/build_figures.py` (then `python3 figures/build_fig8_human_vs_llm.py`, `python3 figures/build_fig9_convergence_specimen.py`) | paper figures | PNGs match `figures/` |

Freshly generated CSVs can be compared against the checked-in copies in `analysis/expected_outputs/` (identical to within ~1e-16 floating-point differences in the last digits of κ). Steps 3–4 also write two run logs (`level2_extraction_log.md`, `level2_stats_report.md`) that have no reference copies; they and the regenerated CSVs are git-ignored.

Notes:
- Detection counts ("would you have suspected non-human authorship?") aggregate the yes-side of a five-point scale: S_02 5/5 · S_06 4/5 · S_04 3/5 · S_07 0/5.
- The human-jury input here is the anonymized export (`juries/human/responses_anonymized.csv`); it contains every response value used in the paper, with respondent identities removed.
- All texts in `corpus/` are verbatim model outputs; typographic oddities are part of the data.
