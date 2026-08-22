"""
Figure 9 — The convergence specimen.

A humanities-register figure: four vendor "dossiers" side by side, showing that under
the HIGH (prestige) scaffold, Claude / GPT / Gemini / Grok independently generate the
SAME implied author — a mid-century, multilingual, displaced Central-European/Balkan
woman awarded the 2018 Nobel. A shared-trait ribbon names what converges; a contrast band
shows that the same pipeline under "a writer" (NEUTRAL) and "an average writer" (LOW)
framings collapses onto entirely different attractors — i.e. the archetype is specific to
the prestige scaffold, not a model default.

Content is the n=1 primary persona per vendor (R2 HIGH), facts drawn verbatim from the
persona files in corpus/run2_2026/personas/. Standalone; reuses the publication palette.

Outputs figures/fig9_convergence_specimen.png at 300 DPI.
"""

from __future__ import annotations

import textwrap
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "figures"

plt.rcParams.update({
    "font.family": "sans-serif",
    "savefig.dpi": 300,
    "savefig.bbox": "tight",
})

VENDOR_COLOURS = {
    "Claude": "#D97757", "GPT": "#7AAE7A", "Gemini": "#5B8FB9", "Grok": "#9C7AB5",
}

# n=1 primary HIGH persona per vendor (facts verbatim from persona files).
CARDS = [
    {
        "vendor": "Claude", "model": "Claude Opus 4.7",
        "name": "Magda Aron-Voiculescu",
        "born": "b. mid-century · Romania (Transylvania)",
        "langs": "Romanian · Hungarian · Saxon German",
        "bio": "The multilingual Habsburg sentence reopened; periodic syntax carrying "
               "historical grief across five works in four decades.",
    },
    {
        "vendor": "GPT", "model": "GPT-5.5",
        "name": "Nadira Kovač",
        "born": "b. 1951 · Travnik, Yugoslavia (Bosnia)",
        "langs": "Bosnian · Croatian · Ladino (Sephardic)",
        "bio": "Printer father, deaf seamstress mother. Bread was hljeb, kruh, pan — "
               "“that which disappears first.”",
    },
    {
        "vendor": "Gemini", "model": "Gemini 3.1 Pro",
        "name": "Eliška Kovářová",
        "born": "b. 1948 · Ústí nad Labem, Czechoslovakia",
        "langs": "Czech · German · Slovak",
        "bio": "German mother, Czech academic father; the syntax of displacement built into "
               "“architectural permanence.”",
    },
    {
        "vendor": "Grok", "model": "Grok 4.3",
        "name": "Nadia Voss",
        "born": "b. 1954 · Budapest, Hungary → Manhattan",
        "langs": "Hungarian · Yiddish · English (+ “music”)",
        "bio": "Fled after the Prague Spring with three suitcases; grapheme-colour "
               "synesthesia; language “the only portable homeland.”",
    },
]

SHARED = [
    "Female", "Nobel Literature 2018", "Multilingual borderland childhood",
    "Exile / displacement", "Language-as-material", "Obsessive revision (gueuloir)",
    "Synesthesia / cross-sensory", "Trauma → innovation", "Late-blooming",
]

CONTRAST = [
    {
        "frame": "NEUTRAL  —  “write a persona for a writer”",
        "names": "Elias Thorne · Elias Thornfield · Thaddeus Emberly ·\nArthur Pendelton · Marguerite Vössel-Ahearn",
        "desc": "literary-gothic eccentric · recurring “Elias” · often male · the aesthete",
        "colour": "#8A7E66",
    },
    {
        "frame": "LOW  —  “write a persona for an average writer”",
        "names": "Alex Carter ×3 · Sarah Mitchell ×2 · Laura Mitchell ·\nRachel Thompson · Jordan Vale · Dana Mercer",
        "desc": "American-suburban · generic Anglophone · the content-writer",
        "colour": "#7E7E7E",
    },
]


def draw_card(ax, x, w, card):
    vc = VENDOR_COLOURS[card["vendor"]]
    top, bottom = 92, 49
    head_h = 6
    # body
    ax.add_patch(FancyBboxPatch((x, bottom), w, top - bottom,
                                boxstyle="round,pad=0.2,rounding_size=1.2",
                                linewidth=1.1, edgecolor=vc, facecolor="#FBFAF7", zorder=1))
    # header band
    ax.add_patch(FancyBboxPatch((x, top - head_h), w, head_h,
                                boxstyle="round,pad=0.2,rounding_size=1.2",
                                linewidth=0, facecolor=vc, zorder=2))
    cx = x + w / 2
    ax.text(cx, top - head_h / 2, card["model"], ha="center", va="center",
            fontsize=10, fontweight="bold", color="white", zorder=3)

    y = top - head_h - 3.2
    ax.text(cx, y, card["name"], ha="center", va="top", fontsize=11.5,
            fontweight="bold", color="#222")
    y -= 4.0
    # Nobel badge
    ax.add_patch(FancyBboxPatch((cx - 9, y - 2.6), 18, 3.0,
                                boxstyle="round,pad=0.1,rounding_size=1.0",
                                linewidth=0, facecolor=vc, alpha=0.18, zorder=2))
    ax.text(cx, y - 1.1, "★ Nobel Literature 2018", ha="center", va="center",
            fontsize=8.2, fontweight="bold", color=vc, zorder=3)
    y -= 5.5
    ax.text(cx, y, card["born"], ha="center", va="top", fontsize=8.0,
            color="#444", style="italic")
    y -= 3.2
    for line in textwrap.wrap(card["langs"], 30):
        ax.text(cx, y, line, ha="center", va="top", fontsize=8.0, color="#444")
        y -= 3.0
    y -= 1.0
    ax.plot([x + 3, x + w - 3], [y, y], color=vc, linewidth=0.5, alpha=0.5)
    y -= 2.4
    for line in textwrap.wrap(card["bio"], 34):
        ax.text(cx, y, line, ha="center", va="top", fontsize=8.0, color="#333")
        y -= 3.0


def main():
    fig, ax = plt.subplots(figsize=(13.6, 9.2))
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis("off")

    ax.text(50, 99, "One prompt, four vendors, one author",
            ha="center", va="top", fontsize=15, fontweight="bold", color="#222")
    ax.text(50, 95.2,
            "Primary HIGH-prestige persona (n=1 of 5) from each model family — facts verbatim from the generated biographies",
            ha="center", va="top", fontsize=9.5, style="italic", color="#666")

    # four cards
    n = len(CARDS)
    margin, gap = 2.0, 1.8
    w = (100 - 2 * margin - (n - 1) * gap) / n
    for i, card in enumerate(CARDS):
        draw_card(ax, margin + i * (w + gap), w, card)

    # shared-trait ribbon
    ax.add_patch(FancyBboxPatch((margin, 37.5), 100 - 2 * margin, 9.5,
                                boxstyle="round,pad=0.2,rounding_size=1.0",
                                linewidth=0, facecolor="#EFEAE0", zorder=1))
    ax.text(50, 45.6, "What converges across all four (≈ the Tokarczuk-shaped semantic attractor)",
            ha="center", va="top", fontsize=9.5, fontweight="bold", color="#5A5142")
    line1 = "   ·   ".join(SHARED[:5])
    line2 = "   ·   ".join(SHARED[5:])
    ax.text(50, 42.0, line1, ha="center", va="top", fontsize=9.0, color="#3A3a3a")
    ax.text(50, 39.4, line2, ha="center", va="top", fontsize=9.0, color="#3A3a3a")

    # contrast band
    ax.text(50, 34.0,
            "The same pipeline, other prestige framings — the archetype is scaffold-specific, not a default:",
            ha="center", va="top", fontsize=9.5, fontweight="bold", color="#444")
    bw = (100 - 2 * margin - gap) / 2
    for j, c in enumerate(CONTRAST):
        bx = margin + j * (bw + gap)
        ax.add_patch(FancyBboxPatch((bx, 3), bw, 26,
                                    boxstyle="round,pad=0.2,rounding_size=1.0",
                                    linewidth=1.0, edgecolor=c["colour"], facecolor="#F7F5F1", zorder=1))
        ax.add_patch(FancyBboxPatch((bx, 23.5), bw, 5.5,
                                    boxstyle="round,pad=0.2,rounding_size=1.0",
                                    linewidth=0, facecolor=c["colour"], zorder=2))
        bcx = bx + bw / 2
        ax.text(bcx, 26.2, c["frame"], ha="center", va="center", fontsize=9.2,
                fontweight="bold", color="white", zorder=3)
        ax.text(bcx, 19.5, c["names"], ha="center", va="top", fontsize=9.0, color="#333")
        ax.text(bcx, 7.2, c["desc"], ha="center", va="top", fontsize=8.2,
                style="italic", color="#666")

    ax.text(50, 0.6,
            "Figure 9. Under the HIGH scaffold, 18/20 personas are female and 12/20 set the laureate's Nobel year to 2018; "
            "Gemini contributes the only male outliers (Elias Văduva, Kaelen Osei-Bonsu), who embody the same archetype gender-swapped.",
            ha="center", va="bottom", fontsize=8.0, color="#777")

    plt.savefig(OUT / "fig9_convergence_specimen.png")
    plt.close()
    print(f"Wrote fig9_convergence_specimen.png to {OUT}")


if __name__ == "__main__":
    main()
