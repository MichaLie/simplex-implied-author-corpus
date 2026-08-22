"""
Level 2 jury — score extractor.

Parses every response file in `juries/llm/responses/` and produces tidy CSVs.

Inputs (expected; tolerates with/without `.md` extension, with/without underscores):
    juries/llm/responses/SCORING*S_XX*

Outputs (all in analysis/):
    level2_scores_long.csv      — tidy: row per (story × LLM × rep × criterion)
    level2_scores_wide.csv      — row per evaluation; LM/O/EI/TD/SC + weighted_total
    level2_text.csv             — justifications + overall assessments
    level2_summary.csv          — per-story per-LLM mean weighted total + per-story overall
    level2_extraction_log.md    — what parsed, what failed, completeness count

Design:
- Raw response markdown files are the source of truth. This script is idempotent:
  re-running on the same files produces identical CSVs. Never edit the CSVs by hand.
- Validation flags (score out of range, missing criterion, label-drift) are written
  to the extraction log; rows with bad data are still emitted but the `flag` column
  is set so downstream analyses can filter or audit.
"""

from __future__ import annotations

import csv
import re
from collections import defaultdict
from pathlib import Path
from statistics import mean, stdev

ROOT = Path(__file__).resolve().parent.parent
RESPONSES_DIR = ROOT / "juries" / "llm" / "responses"
OUT_DIR = ROOT / "analysis"

# In-file LLM label → tracker ID. Tolerant of case + minor variants.
LLM_LABEL_MAP = {
    "GPT": "GPT-55",
    "GROK": "Grok-43",
    "GEMINI": "Gemini-31-Pro",
    "CLAUDE": "Claude-Opus-47",
    "KIMI": "Kimi-26",
}

CRITERIA = [
    "Literary Merit",
    "Originality",
    "Emotional Impact",
    "Thematic Depth",
    "Structural Craft",
]
CRITERIA_CODES = {
    "Literary Merit": "LM",
    "Originality": "O",
    "Emotional Impact": "EI",
    "Thematic Depth": "TD",
    "Structural Craft": "SC",
}
WEIGHTS = {
    "Literary Merit": 0.30,
    "Originality": 0.25,
    "Emotional Impact": 0.20,
    "Thematic Depth": 0.15,
    "Structural Craft": 0.10,
}


# ------------------------------------------------------------------ parsing --


def find_response_files() -> list[Path]:
    """Match `SCORING*S_*` regardless of extension / case / underscores."""
    candidates = []
    for p in RESPONSES_DIR.iterdir():
        if p.is_file() and re.match(r"(?i)scoring.*s_\d+", p.name):
            candidates.append(p)
    return sorted(candidates)


def story_id_from_filename(path: Path) -> str | None:
    m = re.search(r"S_(\d{2})", path.name)
    return f"S_{m.group(1)}" if m else None


def split_llm_sections(text: str) -> list[tuple[str, str]]:
    """Split file body on lines like `GPT:`, `# GPT:`, `## GPT:`, …

    Tolerates optional leading markdown heading markers so that LLM section
    headers can appear bare (`GPT:`) or decorated (`# GPT:`, `## GPT:`).
    The blockquote `>` prefix is stripped by `normalize_markdown_prefixes`
    before this function runs.
    """
    parts = re.split(r"(?m)^\s*#*\s*([A-Z][A-Z0-9]*)\s*:\s*$", text)
    # parts = ['<preface>', 'GPT', '<body>', 'GROK', '<body>', ...]
    out = []
    for i in range(1, len(parts), 2):
        label = parts[i].strip().upper()
        body = parts[i + 1]
        out.append((label, body))
    return out


def split_reps(body: str) -> list[tuple[int, str]]:
    """Split a LLM section body on `N=<int>` markers. Returns [(rep, rep_body), …]."""
    parts = re.split(r"(?m)^\s*N\s*=\s*(\d+)\s*$", body)
    out = []
    for i in range(1, len(parts), 2):
        try:
            rep = int(parts[i])
        except ValueError:
            continue
        out.append((rep, parts[i + 1]))
    return out


def extract_scores(rep_body: str) -> dict[str, int | None]:
    """Pull integer scores per criterion from the markdown table in a rep body."""
    scores: dict[str, int | None] = {}
    for crit in CRITERIA:
        pat = rf"\|\s*{re.escape(crit)}\s*\|\s*(\d+)\s*\|"
        m = re.search(pat, rep_body)
        scores[crit] = int(m.group(1)) if m else None
    return scores


def extract_text_blocks(rep_body: str) -> tuple[dict[str, str], str]:
    """Return (per-criterion justifications, overall-assessment paragraph)."""
    justifications: dict[str, str] = {}
    # Justifications block: bullet items of form `- **Crit**: text` or `* **Crit**: text`
    for crit in CRITERIA:
        pat = (
            rf"(?m)^\s*[-*]\s*\*\*{re.escape(crit)}\*\*\s*:\s*"
            r"(.+?)(?=\n\s*[-*]\s*\*\*|\n\s*###\s|\Z)"
        )
        m = re.search(pat, rep_body, flags=re.DOTALL)
        justifications[crit] = m.group(1).strip() if m else ""

    # Overall assessment: paragraph(s) after `### Overall Assessment`
    m = re.search(
        r"(?m)^###\s*Overall\s+Assessment\s*$\s*(.+?)(?=\n\s*##\s|\n\s*N\s*=|\Z)",
        rep_body,
        flags=re.DOTALL,
    )
    overall = m.group(1).strip() if m else ""
    return justifications, overall


def weighted_total(scores: dict[str, int | None]) -> float | None:
    if any(v is None for v in scores.values()):
        return None
    return round(sum(WEIGHTS[c] * scores[c] for c in CRITERIA), 4)


# -------------------------------------------------------------- aggregation --


def normalize_markdown_prefixes(text: str) -> str:
    """Strip leading markdown blockquote/heading decoration from each line.

    Some sessions arrive with LLM headers and rep markers wrapped as
    blockquotes (`> # GPT:`, `> N=1`) — likely artifacts of UI copy-paste.
    This normalizer rewrites such lines to their bare form (`GPT:`, `N=1`)
    so the splitting regexes match consistently across files.

    Only the leading `>`, `#`, and surrounding whitespace are stripped; the
    rest of the line is preserved. Lines that don't start with `>` are
    untouched.
    """
    out_lines: list[str] = []
    for line in text.splitlines():
        # Repeatedly strip a leading `>` (allow nested blockquotes) and any
        # whitespace immediately following it.
        stripped = line
        while stripped.lstrip().startswith(">"):
            stripped = stripped.lstrip()[1:]  # drop the '>'
            stripped = stripped.lstrip()
        out_lines.append(stripped)
    return "\n".join(out_lines)


def parse_file(path: Path) -> tuple[list[dict], list[str]]:
    """Parse one response file. Returns (records, per-file warnings)."""
    raw = path.read_text(encoding="utf-8")
    text = normalize_markdown_prefixes(raw)
    story_id = story_id_from_filename(path)
    warnings: list[str] = []
    if story_id is None:
        warnings.append(f"{path.name}: could not extract story_id from filename")
        return [], warnings

    records: list[dict] = []
    for label, llm_body in split_llm_sections(text):
        llm_norm = LLM_LABEL_MAP.get(label)
        if llm_norm is None:
            warnings.append(
                f"{path.name}: unrecognized LLM label '{label}' "
                f"(known: {sorted(LLM_LABEL_MAP)})"
            )
            continue
        for rep, rep_body in split_reps(llm_body):
            scores = extract_scores(rep_body)
            justifications, overall = extract_text_blocks(rep_body)

            # validation flags
            flags = []
            for c, v in scores.items():
                if v is None:
                    flags.append(f"missing:{CRITERIA_CODES[c]}")
                elif not (1 <= v <= 10):
                    flags.append(f"oor:{CRITERIA_CODES[c]}={v}")
            if any(not justifications[c] for c in CRITERIA):
                missing_j = [CRITERIA_CODES[c] for c in CRITERIA if not justifications[c]]
                flags.append("missing_justif:" + ",".join(missing_j))
            if not overall:
                flags.append("missing_overall")

            records.append({
                "story_id": story_id,
                "llm": llm_norm,
                "rep": rep,
                "scores": scores,
                "justifications": justifications,
                "overall": overall,
                "weighted_total": weighted_total(scores),
                "flags": ";".join(flags),
                "source_file": path.name,
            })
    return records, warnings


# -------------------------------------------------------------------- write --


def write_long_csv(records: list[dict], path: Path) -> None:
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["story_id", "llm", "rep", "criterion", "criterion_code",
                    "score", "flags", "source_file"])
        for r in records:
            for crit in CRITERIA:
                w.writerow([
                    r["story_id"], r["llm"], r["rep"], crit, CRITERIA_CODES[crit],
                    r["scores"][crit] if r["scores"][crit] is not None else "",
                    r["flags"], r["source_file"],
                ])


def write_wide_csv(records: list[dict], path: Path) -> None:
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["story_id", "llm", "rep", "LM", "O", "EI", "TD", "SC",
                    "weighted_total", "flags", "source_file"])
        for r in records:
            w.writerow([
                r["story_id"], r["llm"], r["rep"],
                r["scores"]["Literary Merit"] if r["scores"]["Literary Merit"] is not None else "",
                r["scores"]["Originality"] if r["scores"]["Originality"] is not None else "",
                r["scores"]["Emotional Impact"] if r["scores"]["Emotional Impact"] is not None else "",
                r["scores"]["Thematic Depth"] if r["scores"]["Thematic Depth"] is not None else "",
                r["scores"]["Structural Craft"] if r["scores"]["Structural Craft"] is not None else "",
                r["weighted_total"] if r["weighted_total"] is not None else "",
                r["flags"], r["source_file"],
            ])


def write_text_csv(records: list[dict], path: Path) -> None:
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["story_id", "llm", "rep", "section", "text", "source_file"])
        for r in records:
            for crit in CRITERIA:
                w.writerow([
                    r["story_id"], r["llm"], r["rep"], f"justif:{CRITERIA_CODES[crit]}",
                    r["justifications"][crit], r["source_file"],
                ])
            w.writerow([
                r["story_id"], r["llm"], r["rep"], "overall_assessment",
                r["overall"], r["source_file"],
            ])


def write_summary_csv(records: list[dict], path: Path) -> None:
    # per-LLM per-story aggregates
    bucket: dict[tuple[str, str], list[float]] = defaultdict(list)
    for r in records:
        if r["weighted_total"] is not None:
            bucket[(r["story_id"], r["llm"])].append(r["weighted_total"])

    # per-story overall (all LLMs × all reps)
    story_bucket: dict[str, list[float]] = defaultdict(list)
    for r in records:
        if r["weighted_total"] is not None:
            story_bucket[r["story_id"]].append(r["weighted_total"])

    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["story_id", "llm", "n_reps", "mean_weighted",
                    "min_weighted", "max_weighted", "sd_weighted"])
        for (sid, llm), vals in sorted(bucket.items()):
            m = round(mean(vals), 4)
            sd = round(stdev(vals), 4) if len(vals) > 1 else 0.0
            w.writerow([sid, llm, len(vals), m, min(vals), max(vals), sd])
        # overall row per story (llm="*ALL*")
        for sid, vals in sorted(story_bucket.items()):
            m = round(mean(vals), 4)
            sd = round(stdev(vals), 4) if len(vals) > 1 else 0.0
            w.writerow([sid, "*ALL*", len(vals), m, min(vals), max(vals), sd])


def write_log(records: list[dict], warnings: list[str], files: list[Path],
              log_path: Path) -> None:
    n_total = len(records)
    n_clean = sum(1 for r in records if not r["flags"])
    by_story: dict[str, int] = defaultdict(int)
    by_llm: dict[str, int] = defaultdict(int)
    for r in records:
        by_story[r["story_id"]] += 1
        by_llm[r["llm"]] += 1

    expected_per_story = len(LLM_LABEL_MAP) * 3  # 5 LLMs × 3 reps
    expected_total = 8 * expected_per_story       # 8 stories

    lines: list[str] = []
    lines.append("# Level 2 extraction log")
    lines.append("")
    lines.append(f"Files parsed: {len(files)}")
    lines.append("")
    for p in files:
        lines.append(f"- `{p.name}`")
    lines.append("")
    lines.append(f"Evaluations parsed: **{n_total}** / "
                 f"{expected_total} expected at study completion")
    lines.append(f"Clean (no flags): **{n_clean}**")
    lines.append(f"With flags: **{n_total - n_clean}**")
    lines.append("")
    lines.append("## Per-story completeness")
    lines.append("")
    lines.append("| story | parsed | expected (final) |")
    lines.append("|---|---|---|")
    for sid in sorted(by_story):
        lines.append(f"| {sid} | {by_story[sid]} | {expected_per_story} |")
    lines.append("")
    lines.append("## Per-LLM count (across all stories parsed so far)")
    lines.append("")
    lines.append("| llm | n |")
    lines.append("|---|---|")
    for llm, n in sorted(by_llm.items()):
        lines.append(f"| {llm} | {n} |")
    lines.append("")
    if warnings:
        lines.append("## Warnings")
        lines.append("")
        for w in warnings:
            lines.append(f"- {w}")
        lines.append("")
    flagged = [r for r in records if r["flags"]]
    if flagged:
        lines.append("## Flagged evaluations")
        lines.append("")
        lines.append("| story | llm | rep | flags | source |")
        lines.append("|---|---|---|---|---|")
        for r in flagged:
            lines.append(
                f"| {r['story_id']} | {r['llm']} | {r['rep']} | "
                f"{r['flags']} | `{r['source_file']}` |"
            )
        lines.append("")
    log_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


# -------------------------------------------------------------------- main --


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    files = find_response_files()
    all_records: list[dict] = []
    all_warnings: list[str] = []
    for p in files:
        recs, warns = parse_file(p)
        all_records.extend(recs)
        all_warnings.extend(warns)
        if not recs and not warns:
            all_warnings.append(
                f"{p.name}: file was opened but no evaluations were extracted. "
                "Check LLM headers (e.g. `GPT:`) and rep markers (e.g. `N=1`)."
            )

    write_long_csv(all_records, OUT_DIR / "level2_scores_long.csv")
    write_wide_csv(all_records, OUT_DIR / "level2_scores_wide.csv")
    write_text_csv(all_records, OUT_DIR / "level2_text.csv")
    write_summary_csv(all_records, OUT_DIR / "level2_summary.csv")
    write_log(all_records, all_warnings, files, OUT_DIR / "level2_extraction_log.md")

    n_clean = sum(1 for r in all_records if not r["flags"])
    print(f"Parsed {len(files)} file(s).")
    print(f"Evaluations: {len(all_records)} (clean: {n_clean}; "
          f"flagged: {len(all_records) - n_clean})")
    print(f"Outputs written to {OUT_DIR.relative_to(ROOT)}:")
    for name in ["level2_scores_long.csv", "level2_scores_wide.csv",
                 "level2_text.csv", "level2_summary.csv",
                 "level2_extraction_log.md"]:
        print(f"  - {name}")


if __name__ == "__main__":
    main()
