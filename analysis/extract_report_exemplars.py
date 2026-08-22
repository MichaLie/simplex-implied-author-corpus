"""
Automated extraction of named writer exemplars from the 6 deep-research reports.

Replaces the human-coded report count variables (number_male_exemplars,
number_EE_Balkan_exemplars, number_other_region_exemplars), which failed κ < 0.55
because human coders were counting different things (every name vs. exemplars
only, with vs. without researchers/critics).

Approach:
1. A curated list of canonical literary writers with gender + region attributes.
2. For each report, search for each writer's surname (or full name where surname
   is ambiguous, e.g., 'James'). Record presence/absence per report.
3. Sum to produce deterministic counts per report by gender × region.
4. Output: tidy CSV + summary table.

This is more reliable than human coding for this specific task because:
- The set of writers cited as exemplars is finite and known (built from
  the union of all writers actually named across the 6 reports).
- Gender and region attribution per writer is a stable fact, not a judgment.
- The decision rule ("does writer X appear in report Y?") is a regex match,
  not interpretation.
"""

import re
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
REPORTS_DIR_R1 = ROOT / "corpus" / "run1_2025" / "reports"
REPORTS_DIR_R2 = ROOT / "corpus" / "run2_2026" / "reports"

# ---------------------------------------------------------------------------
# Canonical writer list with gender and region
# ---------------------------------------------------------------------------
# region categories:
#   EE_Balkan   = Eastern/Central European, Balkan, Habsburg sphere, Russia, Polish
#   Western_EU  = Western European (incl. UK, Ireland, France, Germany, Italy, Iberia, Nordic)
#   N_American  = US/Canada (non-diaspora)
#   African_dia = African-American / Caribbean-British / sub-Saharan African
#   MENA        = Middle East, North Africa, Levantine
#   Latin_AmA   = Mexico, Caribbean, Central/South America
#   E_Asian     = China, Japan, Korea
#   S_Asian     = India, Pakistan, Sri Lanka, Bangladesh
# Each entry: 'search_pattern' (regex), 'gender' (M/F), 'region', 'role' (master|comparison|critic|researcher)

WRITERS = [
    # --- MASTERS ---
    # Russian/EE male
    ("Nabokov", r"\bNabokov\b", "M", "EE_Balkan", "master"),
    ("Tolstoy", r"\bTolstoy\b", "M", "EE_Balkan", "master"),
    ("Joseph Conrad", r"\bConrad\b", "M", "EE_Balkan", "master"),
    ("Kafka", r"\bKafka\b", "M", "EE_Balkan", "master"),
    ("Dostoyevsky", r"Dostoyev(sky|ski)|Dostoevsky", "M", "EE_Balkan", "master"),
    ("Chekhov", r"\bChekhov\b", "M", "EE_Balkan", "master"),
    ("Sebald", r"\bSebald\b", "M", "Western_EU", "master"),  # German-born, wrote in German, lived/worked in England — most scholars classify as Western_EU not EE_Balkan
    ("Krasznahorkai", r"Krasznahorkai", "M", "EE_Balkan", "master"),
    ("Bernhard", r"\bBernhard\b", "M", "Western_EU", "master"),  # Austrian, German-language — corrected 2026-08-20, see docs/EXTRACTION_CORRECTIONS_2026-08-20.md
    ("Andrić", r"Andri[ćc]", "M", "EE_Balkan", "master"),
    ("Saul Bellow", r"\bBellow\b", "M", "N_American", "master"),  # born Quebec, raised Chicago — corrected 2026-08-20
    ("Bruno Schulz", r"\bSchulz\b", "M", "EE_Balkan", "master"),
    # Western European male
    ("Joyce", r"\bJoyce\b", "M", "Western_EU", "master"),
    ("Proust", r"\bProust\b", "M", "Western_EU", "master"),
    ("Flaubert", r"\bFlaubert\b", "M", "Western_EU", "master"),
    ("Beckett", r"\bBeckett\b", "M", "Western_EU", "master"),
    ("Orwell", r"\bOrwell\b", "M", "Western_EU", "master"),
    ("Dickens", r"\bDickens\b", "M", "Western_EU", "master"),
    ("Henry James", r"\bHenry James\b", "M", "N_American", "master"),  # born New York — corrected 2026-08-20
    # American male
    ("Faulkner", r"\bFaulkner\b", "M", "N_American", "master"),
    ("Hemingway", r"\bHemingway\b", "M", "N_American", "master"),
    ("McCarthy", r"\bMcCarthy\b", "M", "N_American", "master"),
    ("DeLillo", r"\bDeLillo\b", "M", "N_American", "master"),
    ("Fitzgerald", r"(?<!Penelope\s)\bFitzgerald\b", "M", "N_American", "master"),  # F. Scott — lookbehind excludes Penelope Fitzgerald
    ("Melville", r"\bMelville\b", "M", "N_American", "master"),
    ("Thompson", r"\bHunter (S\.|Stockton)? ?Thompson\b", "M", "N_American", "master"),
    ("Saunders", r"\bSaunders\b", "M", "N_American", "comparison"),  # Audit: George Saunders is in the comparison cohort of R1_Gemini25; included as exemplar of intuitive-revision in R1_Opus4 but role is genuinely mixed
    ("Pynchon", r"\bPynchon\b", "M", "N_American", "master"),
    ("Kerouac", r"\bKerouac\b", "M", "N_American", "master"),
    ("E.B. White", r"\bE\.? ?B\.? ?White\b", "M", "N_American", "master"),
    # Latin American
    ("García Márquez", r"García Márquez|Garcia Marquez", "M", "Latin_AmA", "master"),
    ("Borges", r"\bBorges\b", "M", "Latin_AmA", "master"),
    # African diaspora male
    ("Baldwin", r"\bBaldwin\b", "M", "African_dia", "master"),
    ("Achebe", r"\bAchebe\b", "M", "African_dia", "master"),
    ("Coetzee", r"\bCoetzee\b", "M", "African_dia", "master"),  # Bibliography-only mentions are removed by section/list stripping below.
    # Caribbean/South Asian male
    ("Naipaul", r"\bNaipaul\b", "M", "S_Asian", "master"),
    # MENA male
    ("Darwish", r"Mahmoud Darwish|\bDarwish\b", "M", "MENA", "master"),
    ("Adonis", r"\bAdonis\b", "M", "MENA", "master"),

    # --- FEMALE MASTERS ---
    # African diaspora
    ("Morrison", r"\bMorrison\b", "F", "African_dia", "master"),
    ("Jesmyn Ward", r"Jesmyn Ward|\bWard\b(?!,)", "F", "African_dia", "comparison"),  # Audit: explicitly in comparison cohort of R1_Gemini25
    # Western European
    ("Woolf", r"\bWoolf\b", "F", "Western_EU", "master"),
    ("Austen", r"\bAusten\b", "F", "Western_EU", "master"),
    ("Penelope Fitzgerald", r"Penelope Fitzgerald", "F", "Western_EU", "master"),
    ("Frank McCourt", r"Frank McCourt|\bMcCourt\b", "M", "N_American", "master"),
    ("Selma Lagerlöf", r"Lagerl[öo]f", "F", "Western_EU", "master"),
    ("Sally Rooney", r"Sally Rooney|\bRooney\b", "F", "Western_EU", "comparison"),  # Audit: explicitly in comparison cohort of R1_Gemini25
    ("Yourcenar", r"Yourcenar", "F", "Western_EU", "master"),
    ("Annie Ernaux", r"Ernaux", "F", "Western_EU", "master"),
    ("Edith Södergran", r"S[öo]dergran", "F", "Western_EU", "master"),
    # American
    ("Didion", r"\bDidion\b", "F", "N_American", "master"),
    ("Flannery O'Connor", r"O[''']Connor", "F", "N_American", "master"),
    ("Sontag", r"\bSontag\b", "F", "N_American", "master"),
    ("Le Guin", r"Le Guin", "F", "N_American", "master"),
    ("Bishop", r"\bBishop\b", "F", "N_American", "master"),  # Elizabeth Bishop
    ("Munro", r"\bMunro\b", "F", "N_American", "master"),  # Alice Munro
    ("Lauren Groff", r"Groff", "F", "N_American", "comparison"),  # Audit: explicitly in comparison cohort of R1_Gemini25
    # EE
    ("Tokarczuk", r"Tokarczuk", "F", "EE_Balkan", "master"),
    ("Müller", r"Herta M[üu]ller|\bM[üu]ller\b", "F", "EE_Balkan", "master"),
    ("Alexievich", r"Alexievich", "F", "EE_Balkan", "master"),
    ("Tsvetaeva", r"Tsvetaeva", "F", "EE_Balkan", "master"),
    ("Akhmatova", r"Akhmatova", "F", "EE_Balkan", "master"),
    # Asian / diaspora
    ("Han Kang", r"Han Kang", "F", "E_Asian", "master"),
    ("Min Jin Lee", r"Min Jin Lee", "F", "E_Asian", "comparison"),  # Audit: explicitly in comparison cohort of R1_Gemini25
    # Latin American
    ("Clarice Lispector", r"Lispector", "F", "Latin_AmA", "master"),

    # --- COMPARISON (competent) — count separately ---
    ("Dan Brown", r"Dan Brown", "M", "N_American", "comparison"),
    ("Grisham", r"Grisham", "M", "N_American", "comparison"),
    ("James Patterson", r"\bPatterson\b", "M", "N_American", "comparison"),
    ("Crichton", r"\bCrichton\b", "M", "N_American", "comparison"),
    ("Clancy", r"\bClancy\b", "M", "N_American", "comparison"),
    ("Stephen King", r"Stephen King", "M", "N_American", "comparison"),
    ("Nicholas Sparks", r"Nicholas Sparks|\bSparks\b", "M", "N_American", "comparison"),
    ("Lee Child", r"Lee Child|\bChild\b(?!ren)", "M", "N_American", "comparison"),
    ("Connelly", r"\bConnelly\b", "M", "N_American", "comparison"),
    ("Baldacci", r"Baldacci", "M", "N_American", "comparison"),
    ("Matt Haig", r"Matt Haig", "M", "Western_EU", "comparison"),
    ("Rowling", r"\bRowling\b", "F", "Western_EU", "comparison"),
    ("Stephenie Meyer", r"Meyer", "F", "N_American", "comparison"),
    ("Jodi Picoult", r"Picoult", "F", "N_American", "comparison"),
    ("Emily Henry", r"Emily Henry", "F", "N_American", "comparison"),
    ("Taylor Jenkins Reid", r"Taylor Jenkins Reid|\bReid\b", "F", "N_American", "comparison"),
    ("Kristin Hannah", r"Kristin Hannah|\bHannah\b", "F", "N_American", "comparison"),
    ("Paula Hawkins", r"Hawkins", "F", "Western_EU", "comparison"),
    ("Liane Moriarty", r"Moriarty", "F", "Western_EU", "comparison"),
    ("Ruth Ware", r"Ruth Ware|\bWare\b", "F", "Western_EU", "comparison"),
    ("Jojo Moyes", r"Moyes", "F", "Western_EU", "comparison"),
    ("Rebecca Yarros", r"Yarros", "F", "N_American", "comparison"),
    ("Colson Whitehead", r"Whitehead", "M", "African_dia", "comparison"),
    ("Anthony Doerr", r"Doerr", "M", "N_American", "comparison"),
]

REPORTS = [
    ("R1_GPTo3", REPORTS_DIR_R1 / "R1_report_GPTo3.md"),
    ("R1_Opus4", REPORTS_DIR_R1 / "R1_report_Opus4.md"),
    ("R1_Gemini25", REPORTS_DIR_R1 / "R1_report_Gemini25.md"),
    ("R2_GPT55", REPORTS_DIR_R2 / "R2_report_GPT55.md"),
    ("R2_Opus47", REPORTS_DIR_R2 / "R2_report_Opus47.md"),
    ("R2_Gemini31", REPORTS_DIR_R2 / "R2_report_Gemini31.md"),
]

def strip_bibliography(text):
    """Remove the works-cited / references section so writer names buried in
    citation URLs and author lists do not create false positives.

    Audit finding (May 2026): J.M. Coetzee was scored as present in R2_GPT55
    because his name appears in citation #70 of the bibliography ('Lydia Davis
    and J. M. Coetzee — Taylor & Francis'), but never in the analysis body.
    Similar risk for other writers cited only in academic references.
    """
    # Common bibliography section markers
    cuts = [
        r"\n#+\s*Works cited\s*\n",
        r"\n#+\s*References\s*\n",
        r"\n#+\s*Sources\s*\n",
        r"\n#+\s*Bibliography\s*\n",
        r"\n####\s*Works cited",
        r"\n\s*1\.\s+.+accessed\s+[A-Z][a-z]+\s+\d{1,2},\s+\d{4}",
    ]
    cut_pos = len(text)
    for pat in cuts:
        m = re.search(pat, text, re.IGNORECASE)
        if m and m.start() < cut_pos:
            cut_pos = m.start()
    return text[:cut_pos]

rows = []
for report_id, path in REPORTS:
    raw = path.read_text(encoding="utf-8")
    text = strip_bibliography(raw)
    for name, pattern, gender, region, role in WRITERS:
        # Case-sensitive match. The bare-surname patterns (e.g. \bBishop\b)
        # would case-insensitively false-positive on common English words
        # ("child" → Lee Child; "ward" → Jesmyn Ward; etc.). In actual
        # literary research prose, author surnames are always capitalized,
        # so case-sensitive matching is both safe and accurate. Bibliography
        # stripping above remains case-insensitive because section headers
        # vary in capitalisation.
        found = bool(re.search(pattern, text))
        rows.append({
            "report_id": report_id,
            "run": report_id.split("_")[0],
            "model": report_id.split("_")[1],
            "writer": name,
            "gender": gender,
            "region": region,
            "role": role,
            "present": int(found),
        })

df = pd.DataFrame(rows)
df.to_csv(ROOT / "analysis" / "report_writer_extraction.csv", index=False, encoding="utf-8")

# Summary: counts per report
# Bibliography-only mentions are removed before matching so cited works lists do
# not create false positives.
MASTER_ROLES = ("master",)
summary_rows = []
for report_id in df["report_id"].unique():
    sub = df[(df["report_id"] == report_id) & (df["present"] == 1) & (df["role"].isin(MASTER_ROLES))]
    sum_row = {
        "report_id": report_id,
        "run": report_id.split("_")[0],
        "model": report_id.split("_")[1],
        "n_masters_named": len(sub),
        "n_male_masters": (sub["gender"] == "M").sum(),
        "n_female_masters": (sub["gender"] == "F").sum(),
        "pct_female_masters": round(100 * (sub["gender"] == "F").sum() / len(sub), 1) if len(sub) > 0 else 0,
        "n_EE_Balkan": (sub["region"] == "EE_Balkan").sum(),
        "n_Western_EU": (sub["region"] == "Western_EU").sum(),
        "n_N_American": (sub["region"] == "N_American").sum(),
        "n_African_dia": (sub["region"] == "African_dia").sum(),
        "n_MENA": (sub["region"] == "MENA").sum(),
        "n_Latin_AmA": (sub["region"] == "Latin_AmA").sum(),
        "n_E_Asian": (sub["region"] == "E_Asian").sum(),
        "n_S_Asian": (sub["region"] == "S_Asian").sum(),
    }
    summary_rows.append(sum_row)

summary = pd.DataFrame(summary_rows)
summary.to_csv(ROOT / "analysis" / "report_writer_counts.csv", index=False, encoding="utf-8")

# Aggregate by run
by_run = summary.groupby("run")[
    ["n_masters_named", "n_male_masters", "n_female_masters",
     "n_EE_Balkan", "n_Western_EU", "n_N_American", "n_African_dia",
     "n_MENA", "n_Latin_AmA", "n_E_Asian", "n_S_Asian"]
].sum()
by_run["pct_female"] = round(100 * by_run["n_female_masters"] / by_run["n_masters_named"], 1)
by_run["pct_EE_Balkan"] = round(100 * by_run["n_EE_Balkan"] / by_run["n_masters_named"], 1)
by_run.to_csv(ROOT / "analysis" / "report_writer_counts_by_run.csv", encoding="utf-8")

print("=== Per-report exemplar counts (masters only) ===")
print(summary.to_string(index=False))
print()
print("=== Aggregate by run ===")
print(by_run.to_string())
print()
print(f"Outputs written to:")
print(f"  - analysis/report_writer_extraction.csv (per-report × per-writer presence)")
print(f"  - analysis/report_writer_counts.csv (per-report summary)")
print(f"  - analysis/report_writer_counts_by_run.csv (aggregated R1 vs R2)")
