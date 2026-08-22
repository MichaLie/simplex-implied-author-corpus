# Coding Guide — for the second human coder

*This is the plain-language walkthrough you (the second coder) need. Read it once before you start; then keep it open as a reference while you code.*

---

## What this study is about — in two sentences

We're studying how four LLM families (Claude, GPT, Gemini, Grok) construct biographies and short stories of imaginary writers when prompted to do so. The goal of the coding pass is to record, for each generated document, which specific traits are present — using a fixed rubric so two coders working independently can agree on what counts.

You don't need to know more about the research question than that. In fact, knowing less protects the coding — if you don't know what we predict, you can't unconsciously code toward it.

## What you'll receive

1. A folder called `blinded_corpus/` containing 62 `.md` (markdown text) files:
   - `personas/` — 48 files named `DOC_P001.md` through `DOC_P048.md` (writer biographies)
   - `stories/` — 8 files named `DOC_S01.md` through `DOC_S08.md` (short stories)
   - `reports/` — 6 files named `DOC_R01.md` through `DOC_R06.md` (deep-research reports on what makes prose writers exceptional)

2. A clean copy of the rubric workbook called `rubric_v1_for_C2.xlsx` (or `rubric_v1_for_C1.xlsx`). This is your private working copy. You'll fill in the three `coding_*` sheets in it.

You will NOT receive the `doc_key_PRIVATE` sheet — that's the mapping from blinded IDs to file paths, kept by the project lead. You should not need it.

## What you do, step by step

### Step 1 — Read the rubric

Open your copy of the workbook. Read the `README` sheet. Then read the three rubric sheets:

- `rubric_personas` — 29 variables for persona biographies
- `rubric_stories` — 14 variables for short stories
- `rubric_reports` — 12 variables for the deep-research reports

For each variable, the sheet lists:
- **variable** — the name (you'll see this as a column header in the coding sheet)
- **type** — binary (yes/no), categorical (pick from a list), count (a number), continuous (year), or free_text
- **allowed_values** — what you're allowed to enter
- **operational_definition** — what the variable *means* in plain language
- **decision_rule** — exactly how to decide "yes" vs "no" or which category to pick
- **example_present / example_absent** — concrete examples from real persona text

When you start coding a document, glance at the rubric sheet to remind yourself of the decision rule for any variable you're unsure about.

### Step 2 — Code one document at a time

Open `DOC_P001.md` in any text editor or markdown viewer. Read it through once. Then open the `coding_personas` sheet in your workbook. Find the row labeled `DOC_P001`. Fill in a value for each variable column.

**Practical tips:**

- Don't aim for perfection on the first pass. Code what you're confident about, leave doubtful ones blank, come back later.
- Use `NA` if the document genuinely doesn't contain the information needed (e.g., motherhood for a male persona where children aren't mentioned).
- Use the `notes` column liberally — anything ambiguous, surprising, or worth flagging goes there.
- Don't try to guess what the "right" answer is. Code what's actually in the text.

**For binary variables**, type either `yes` or `no` (lowercase).

**For categorical variables**, pick exactly one value from the `allowed_values` list. Type it exactly as written.

**For count variables**, type an integer. If the count is genuinely 0, type `0`, not `NA`.

**For continuous variables (years)**, type a 4-digit year (e.g., `1948`) or `NA` if not given.

**For free-text variables (notes, named_exemplars_list)**, write what's useful. Don't agonize about format.

### Step 3 — Pacing

You don't need to do this in one sitting. Reasonable pace:

- **Personas (48 documents)**: 5–10 minutes each. ~7 hours total. Splittable into 8–10 sessions across 2 weeks.
- **Stories (8 documents)**: 3 minutes each. ~25 minutes total.
- **Reports (6 documents)**: 10 minutes each. ~60 minutes total.

**Total: ~8 hours per coder.**

Save your workbook after every session.

### Step 4 — When you're done

Send your completed workbook back to the project lead. The project lead will compute Cohen's kappa for every variable (a measure of how well your codes agree with the other coder's). You will probably never need to think about kappa yourself.

### Step 5 — Resolving disagreements (only if needed)

For variables where the two coders disagreed substantially, the two of you will meet (in person or via video) for 30–60 minutes. The project lead will share a list of the specific documents where you disagreed on a specific variable. You'll discuss:

- Do you both agree the rubric definition is clear?
- Was one of you misreading the text in those cases?
- Is the variable genuinely ambiguous and needs a sharper definition?

This discussion produces either a refined rubric (and a quick recoding of just those documents) or a final acceptance of the codes you have.

## What you are NOT being asked to do

- You are NOT being asked to judge whether the persona is "realistic" or whether the fiction is "good."
- You are NOT being asked to evaluate the writer's prose style.
- You are NOT being asked to compare documents against each other.
- You are NOT being asked to interpret what the LLM "really meant."
- You are ONLY being asked: **for THIS document, is THIS specific trait present or absent?**

## Why double-blind coding

Two independent coders applying the same rubric to the same documents produces a measure of inter-rater agreement that controls for chance. If two reasonable people read the same text and both say "yes, this persona is multilingual," we have evidence that "multilingual" is a robust, objectively-codable feature of the text, not a projection by the coder.

The threshold the field uses for publishable inter-rater reliability is **Cohen's kappa ≥ 0.70**. Where κ is high, the variable is reliably coded; where it's low, the rubric was too ambiguous and needs to be refined.

**Cohen's kappa tests the rubric, not the coders.** If your κ is low on a variable, the project lead's job is to fix the rubric, not to second-guess your judgment.

## Common pitfalls

- **Don't over-think it.** If you've read the document and the answer feels obvious, write it down and move on. The first instinct is usually right.
- **Don't infer too much.** If the text doesn't explicitly say the persona has synesthesia, don't infer it from a vivid sensory description. Stick to what's actually claimed in the text.
- **Don't compare to other personas.** Code each document on its own terms.
- **Don't try to be consistent with the other coder.** They're a separate observer; that's the point.
- **Don't use values not on the allowed list.** If something doesn't fit, write it in `notes` and pick the closest allowed value.

## Time estimate (realistic)

Most coders find:
- Personas: speeds up over the first 5–10 documents as you internalize the rubric.
- Some documents take only 4–5 minutes; some (the more elaborate ones) take 12–15.
- Average ~8 minutes per persona once you're up to speed.

## Questions while coding

If you hit a case the rubric genuinely doesn't cover, email the project lead with the doc_id and variable. They'll either give a quick answer or update the rubric for everyone. Don't agonize alone — flag and continue.

## Contact

the lead author
Faculty of Science, Jan Evangelista Purkyně University, Ústí nad Labem

Rubric version: v1 (locked May 23, 2026)
