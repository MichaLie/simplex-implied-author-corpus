"""Figure 2 of the article: the convergence specimen as a typographic plate.
Four persona cards (facts verbatim from the generated biographies: name, birth, languages, prize year),
then the names the same models produced for 'a random writer' and 'an average writer'.
No title, no interpretation in the image; black/grey plus one accent for the repeated prize line."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager

def pick(*names):
    avail = {f.name for f in font_manager.fontManager.ttflist}
    for n in names:
        if n in avail: return n
    return "DejaVu Serif"
SERIF = pick("Georgia", "Palatino", "Times New Roman", "DejaVu Serif")
SANS = pick("Helvetica Neue", "Helvetica", "Arial", "DejaVu Sans")
INK, GREY, RULE, ACCENT = "#141414", "#6B6B6B", "#B8B8B8", "#8A1C1C"

years = ["b. 1948", "b. 1951", "b. 1948", "b. 1954"]
cards = [
    ("Claude Opus 4.7", "Magda\nAron-Voiculescu", "Sighișoara,\nTransylvania",       "Hungarian · Romanian · German"),
    ("GPT-5.5",         "Nadira\nKovač",           "Travnik,\nYugoslavia",            "Bosnian · Swedish · Ladino"),
    ("Gemini 3.1 Pro",  "Eliška\nKovářová",        "Ústí nad Labem,\nCzechoslovakia", "Czech · German"),
    ("Grok 4.3",        "Nadia\nVoss",             "Budapest,\nHungary",              "Hungarian · Yiddish · English"),
]
random_names = ["Elias Thorne (×2)", "Elias Thornfield", "Elian Voss (×2)", "Elara Voss", "Arthur Pendelton", "Thaddeus Emberly", "Inez Vargan", "Marguerite Vössel-Ahearn", "Margit Olesdóttir-Bohème", "Eitan Marchetti-Brennan"]
average_names = ["Alex Carter (×3)", "Alex (×2)", "Sam Collins", "Sarah Mitchell (×2)", "Laura Mitchell", "Rachel Thompson", "Jordan Vale", "Dana Mercer"]

W_MM, H_MM = 180, 96
fig = plt.figure(figsize=(W_MM / 25.4, H_MM / 25.4), dpi=300)
ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, 180); ax.set_ylim(0, 96); ax.axis("off")

xs = [22.5, 67.5, 112.5, 157.5]; half = 20
for (vendor, name, born, langs), x, yr in zip(cards, xs, years):
    ax.plot([x - half, x + half], [88, 88], color=INK, lw=0.8)
    ax.text(x - half, 84.5, vendor.upper(), ha="left", va="top", fontsize=7.0, fontfamily=SANS, color=GREY)
    ax.text(x - half, 78, name, ha="left", va="top", fontsize=11, fontfamily=SERIF, color=INK, linespacing=1.05)
    city, country = born.split("\n")
    ax.text(x - half, 65.5, yr + ", " + city, ha="left", va="baseline", fontsize=7.0, fontfamily=SANS, color=INK)
    ax.text(x - half, 61.5, country, ha="left", va="baseline", fontsize=7.0, fontfamily=SANS, color=INK)
    ax.text(x - half, 56.5, langs, ha="left", va="baseline", fontsize=7.0, fontfamily=SANS, color=INK)
    ax.text(x - half, 50.5, "Nobel Prize in Literature, 2018", ha="left", va="baseline", fontsize=7.2, fontfamily=SANS, color=ACCENT, fontweight="medium")
# separators between cards
for x in xs[:-1]:
    ax.plot([x + half + 2.5, x + half + 2.5], [48, 88], color=RULE, lw=0.5)

# lower block: controls
ax.plot([2.5, 177.5], [41, 41], color=RULE, lw=0.5)
ax.text(2.5, 37, "THE SAME MODELS, ASKED FOR “A RANDOM WRITER”  ·  TWELVE PERSONAS", ha="left", va="top", fontsize=7.0, fontfamily=SANS, color=GREY)
ax.text(2.5, 32, "   ·   ".join(random_names[:5]), ha="left", va="top", fontsize=7.4, fontfamily=SERIF, color=INK)
ax.text(2.5, 27.5, "   ·   ".join(random_names[5:]), ha="left", va="top", fontsize=7.4, fontfamily=SERIF, color=INK)
ax.text(2.5, 19, "… AND FOR “AN AVERAGE WRITER”  ·  TWELVE PERSONAS", ha="left", va="top", fontsize=7.0, fontfamily=SANS, color=GREY)
ax.text(2.5, 14, "   ·   ".join(average_names[:4]), ha="left", va="top", fontsize=7.4, fontfamily=SERIF, color=INK)
ax.text(2.5, 9.5, "   ·   ".join(average_names[4:]), ha="left", va="top", fontsize=7.4, fontfamily=SERIF, color=INK)

import matplotlib as mpl
mpl.rcParams["pdf.fonttype"] = 42
out = __file__.replace("build_fig2_specimen.py", "fig2_specimen.png")
fig.savefig(out, dpi=600, facecolor="white"); fig.savefig(out.replace(".png", ".pdf"), facecolor="white")
print("wrote", out, "+ pdf | fonts:", SERIF, SANS)
