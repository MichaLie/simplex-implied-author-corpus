#!/usr/bin/env python3
"""Self-preference of the LLM jurors with the run-vintage correction, and jury means
without each story's own vendor.

Input:  analysis/level2_scores_long.csv as written by level2_extract.py (falls back to the
        reference copy in analysis/expected_outputs/ on a fresh clone).
Output: analysis/level2_self_preference_vintage.csv and analysis/level2_own_vendor_excluded.csv
        (reference copies in analysis/expected_outputs/), plus the headline numbers on the terminal.

Method. Each juror's three repetitions are averaged into one weighted total per story
(weights as in level2_extract.py: literary merit .30, originality .25, emotional impact .20,
thematic depth .15, structural craft .10). For each of the four vendor jurors:
  pre-registered delta   = own story minus the juror's mean over the seven other stories
  vintage-matched delta  = own story minus the juror's mean over the three other second-run stories
  others' delta          = mean, over the four other jurors, of (own story minus that juror's mean
                           over the three other second-run stories)
  difference-in-differences = vintage-matched delta minus others' delta
The own-vendor-excluded mean of a story is the mean over the four jurors not made by the vendor
whose model wrote the story; the outsider (Kimi) is never excluded. A standardized variant
z-scores each juror's eight story means before averaging.

Story-to-vendor mapping follows the table in the repository README (S_01 Gemini 2.5 Pro, run 1;
S_02 Claude Opus 4.7, run 2; S_03 Gemini 3.1 Pro, run 2; S_04 Grok 4.3, run 2; S_05 GPT o3, run 1;
S_06 GPT-5.5, run 2; S_07 Claude Opus 4, run 1; S_08 Grok 4, run 1).
"""
import csv, os, statistics as st
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
_fresh = os.path.join(HERE, "level2_scores_long.csv")
SRC = _fresh if os.path.exists(_fresh) else os.path.join(HERE, "expected_outputs", "level2_scores_long.csv")
OUT1 = os.path.join(HERE, "level2_self_preference_vintage.csv")
OUT2 = os.path.join(HERE, "level2_own_vendor_excluded.csv")

WEIGHTS = {"LM": 0.30, "O": 0.25, "EI": 0.20, "TD": 0.15, "SC": 0.10}
STORY = {  # story id -> (vendor, run, title)
    "S_01": ("Gemini", "R1", "The Palimpsest of Winter"),
    "S_02": ("Claude", "R2", "Birthälm, in November"),
    "S_03": ("Gemini", "R2", "The Diffusion Gradient"),
    "S_04": ("Grok",   "R2", "The Verb That Refused to Conjugate"),
    "S_05": ("GPT",    "R1", "Echoes at Twilight"),
    "S_06": ("GPT",    "R2", "The Drawer for Returned Names"),
    "S_07": ("Claude", "R1", "The Translator's Hands"),
    "S_08": ("Grok",   "R1", "The Weight of Unspoken Tongues"),
}
def vendor_of_juror(label: str) -> str:
    l = label.lower()
    if "gpt" in l: return "GPT"
    if "opus" in l or "claude" in l: return "Claude"
    if "gemini" in l: return "Gemini"
    if "grok" in l: return "Grok"
    return "Kimi"

rows = list(csv.DictReader(open(SRC, encoding="utf8")))
per_eval = defaultdict(dict)
for r in rows:
    per_eval[(r["story_id"], r["llm"], r["rep"])][r["criterion_code"]] = int(r["score"])
totals = defaultdict(list)
for (s, j, rep), d in per_eval.items():
    if len(d) == 5:
        totals[(s, j)].append(sum(WEIGHTS[c] * d[c] for c in WEIGHTS))
mean = {k: st.mean(v) for k, v in totals.items()}
jurors = sorted({j for _, j in mean}); stories = sorted(STORY)
r2 = [s for s in stories if STORY[s][1] == "R2"]

# --- self-preference with vintage correction
sp_rows = []
for j in jurors:
    v = vendor_of_juror(j)
    own = [s for s in r2 if STORY[s][0] == v]
    if not own: continue
    own = own[0]
    pre = mean[(own, j)] - st.mean(mean[(s, j)] for s in stories if s != own)
    vint = mean[(own, j)] - st.mean(mean[(s, j)] for s in r2 if s != own)
    others = st.mean(mean[(own, k)] - st.mean(mean[(s, k)] for s in r2 if s != own) for k in jurors if k != j)
    sp_rows.append({"juror": j, "own_story": own, "own_title": STORY[own][2],
                    "delta_preregistered": round(pre, 2), "delta_vintage_matched": round(vint, 2),
                    "others_delta_on_own_story": round(others, 2), "difference_in_differences": round(vint - others, 2)})
with open(OUT1, "w", newline="", encoding="utf8") as f:
    w = csv.DictWriter(f, fieldnames=list(sp_rows[0].keys())); w.writeheader(); w.writerows(sp_rows)

# --- own-vendor-excluded means, raw and standardized
z = {}
for j in jurors:
    vals = [mean[(s, j)] for s in stories]; mu = st.mean(vals); sd = st.pstdev(vals)
    for s in stories: z[(s, j)] = (mean[(s, j)] - mu) / sd if sd else 0.0
ov_rows = []
for s in stories:
    v = STORY[s][0]
    incl = [j for j in jurors if vendor_of_juror(j) != v]
    ov_rows.append({"story_id": s, "title": STORY[s][2], "vendor": v, "run": STORY[s][1],
                    "mean_all_jurors": round(st.mean(mean[(s, j)] for j in jurors), 2),
                    "mean_without_own_vendor": round(st.mean(mean[(s, j)] for j in incl), 2),
                    "z_mean_without_own_vendor": round(st.mean(z[(s, j)] for j in incl), 2),
                    "outsider_mean": round(next(mean[(s, j)] for j in jurors if vendor_of_juror(j) == "Kimi"), 2)})
ov_rows.sort(key=lambda r: -r["mean_all_jurors"])
with open(OUT2, "w", newline="", encoding="utf8") as f:
    w = csv.DictWriter(f, fieldnames=list(ov_rows[0].keys())); w.writeheader(); w.writerows(ov_rows)

print("Self-preference (weighted totals, mean of 3 repetitions):")
for r in sp_rows:
    print(f"  {r['juror']:16s} own {r['own_story']}  pre-registered {r['delta_preregistered']:+.2f}  vintage-matched {r['delta_vintage_matched']:+.2f}  others {r['others_delta_on_own_story']:+.2f}  DiD {r['difference_in_differences']:+.2f}")
print("Jury means without each story's own vendor (ordered by the full jury):")
for r in ov_rows:
    print(f"  {r['story_id']} {r['title'][:34]:34s} all {r['mean_all_jurors']:.2f}  without own {r['mean_without_own_vendor']:.2f}  z {r['z_mean_without_own_vendor']:+.2f}  outsider {r['outsider_mean']:.2f}")
print(f"wrote {os.path.relpath(OUT1, HERE)} and {os.path.relpath(OUT2, HERE)}")
