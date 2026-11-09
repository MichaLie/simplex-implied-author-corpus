# Pre-registration corrections — 2026-07-02

Per project policy, the locked pre-registration files are preserved unedited; corrections are recorded in dated notes. This note supplements `PREREGISTRATION_CORRECTIONS_2026-06-21.md`.

## 1 · Run 1 date: "May 2025" → **July 2025**

**Affected locked file:** `PREREGISTRATION_LEVEL2.md` (§Stories evaluated: "4 from Run 1 / May 2025").

**What is wrong:** Run 1 was dated to May 2025 throughout the project's documentation (also in `METHODS.md`, `README.md`, `ANALYSIS_QUESTIONS_v1.md`, `CONSULTATION_BRIEF.md`, and the manuscript drafts — all corrected on 2026-07-02; the locked file is left as-is).

**Evidence for the correction (2026-07-02 submission audit):**
1. The Run 1 ChatGPT conversation and share IDs in `data/chat_share_urls.md` embed Unix-timestamp prefixes that decode to **July 24–25, 2025** (persona chat `6881bfce…`, story chat `68823a57…`, deep-research share `dr_68838f03…`). The decoding method was validated against Run 2, whose conversation IDs (`6a11…`) decode to **May 23, 2026** — matching both the Run 2 raw-file creation timestamps and the documented Run 2 date exactly.
2. Run 1 used **Grok 4**, which xAI first released on **July 9, 2025**; a May 2025 Grok 4 generation is not possible.

**What does not change:** No statistic, coding, or analysis depends on the Run 1 date or on the inter-run interval. The cross-temporal comparison (R1 vs R2) is unaffected; the interval is ~10 months rather than ~12. The submitted abstract's phrase "repeated a year apart" is retained as prose approximation; the manuscript's Methods now carry the exact months (July 2025, May 2026).

**Author action:** M.L. to confirm the July 2025 dating against her own vendor chat histories (the Claude/Gemini/Grok Run 1 URLs do not embed decodable timestamps; the GPT legs and the Grok-4 release constraint are the hard evidence).

---

**Postscript (20 August 2026).** The lead author confirmed the July 2025 dating of Run 1 against her own vendor chat histories; the records throughout the repository carry July 2025.
