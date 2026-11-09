"""Figure 1 of the article: the SIMPLEX workflow as a plain typographic plate.
No title, no explanation inside the image; everything else goes to the caption.
Black and grey only. 180 mm wide at 300 dpi."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.patches import FancyArrowPatch

def pick(*names):
    avail = {f.name for f in font_manager.fontManager.ttflist}
    for n in names:
        if n in avail: return n
    return "DejaVu Sans"
SANS = pick("Helvetica Neue", "Helvetica", "Arial", "DejaVu Sans")
INK, GREY, RULE = "#141414", "#6B6B6B", "#B8B8B8"

W_MM, H_MM = 180, 54
fig = plt.figure(figsize=(W_MM / 25.4, H_MM / 25.4), dpi=300)
ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, 180); ax.set_ylim(0, 54); ax.axis("off")

stages = [
    ("CRITICS",      "6 reports"),
    ("BIOGRAPHERS",  "24 personas"),
    ("WRITERS",      "8 stories"),
    ("MACHINE JURY", "5 models · 120 scorings"),
    ("HUMAN PANEL",  "5 readers · 4 stories"),
]
xs = [18, 54, 90, 126, 162]
y_label, y_count, y_rule = 41, 35.5, 45.5
for (lab, cnt), x in zip(stages, xs):
    ax.text(x, y_label, lab, ha="center", va="center", fontsize=8.6, fontfamily=SANS, color=INK, fontweight="medium")
    ax.text(x, y_count, cnt, ha="center", va="center", fontsize=7.4, fontfamily=SANS, color=GREY)
    ax.plot([x - 14, x + 14], [y_rule, y_rule], color=INK, lw=0.8, solid_capstyle="butt")
# arrows between stages
for x0, x1 in zip(xs[:-1], xs[1:]):
    ax.add_patch(FancyArrowPatch((x0 + 15.5, y_label), (x1 - 15.5, y_label), arrowstyle="-|>", mutation_scale=7, lw=0.7, color=GREY, shrinkA=0, shrinkB=0))
# role glosses (one short line each, grey, small)
gloss = ["what makes a prose writer\nexceptional?", "one fictional Nobel laureate\nembodying those patterns", "a short story in that\nnovelist's voice", "blinded identifiers,\nthree repetitions", "same rubric, machine\norigin disclosed"]
for g, x in zip(gloss, xs):
    ax.text(x, 27.5, g, ha="center", va="top", fontsize=7.0, fontfamily=SANS, color=GREY, linespacing=1.25)
# controls branch under BIOGRAPHERS
ax.plot([54, 54], [20.5, 15], color=RULE, lw=0.7, linestyle=(0, (1.2, 1.6)))
ax.text(54, 13, "CONTROLS", ha="center", va="top", fontsize=7.2, fontfamily=SANS, color=INK, fontweight="medium")
ax.text(54, 9, "“a random writer” · “an average writer”\n24 personas, no reports, no brief", ha="center", va="top", fontsize=7.0, fontfamily=SANS, color=GREY, linespacing=1.25)

import matplotlib as mpl
mpl.rcParams["pdf.fonttype"] = 42
out = __file__.replace("build_fig1_workflow.py", "fig1_workflow.png")
fig.savefig(out, dpi=600, facecolor="white"); fig.savefig(out.replace(".png", ".pdf"), facecolor="white")
print("wrote", out, "+ pdf | font:", SANS)
