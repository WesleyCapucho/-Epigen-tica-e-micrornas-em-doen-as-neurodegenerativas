#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EN | The mechanism schematic of the meta-analysis manuscript (its Fig. 7): how microRNAs regulate
     the Alzheimer's (BACE1, Abeta42) and Parkinson's (SNCA, alpha-synuclein) axes and how they
     reach a blood test. It is a schematic, not a result: no number in it comes from the data.

     Built at final size, 174 x 156 mm, in millimetres: Arial, lettering 8 to 12 pt, lines of at
     least 0.5 pt, flat colours, no transparency, no title or caption inside the artwork. The
     lettering is at least 4.5:1 against what it sits on (scripts/45 measures it on the PDF). The
     molecules are the PyMOL renders of deposited structures made by scripts/42 and cropped by
     scripts/43, each drawn on the tint of the panel it sits in and placed at 600 dpi or more.
     Icons, curves and text are drawn here with matplotlib.

     Written once, for one journal figure, so it is English only (the other figures come in
     English and Brazilian Portuguese) and it does not import scripts/_viz_style.py or
     scripts/_bilingual.py: the first would restyle matplotlib and the second would write a PDF
     beside every PNG, and the figure has to come out exactly as it was drawn for the submission.
     The palette is spelled out below; its disease blue and orange are AD_TEXT and PD_TEXT of
     _viz_style.py, and its grey panel tint and rule grey are BAND and RULE of the same file.

     Outputs, in results/figures/: mirna_mechanism_schematic.en.png (RGB), .tif (RGB, LZW,
     600 dpi, the file for the journal) and .pdf. The page is opaque, so dropping the alpha channel
     that matplotlib writes changes no pixel. The TIFF delivered to the journal is redrawn pixel
     for pixel by this script run with Python 3.12.10, matplotlib 3.10.8, NumPy 1.26.4,
     Pillow 12.3.0 and Arial (Windows); `--compare REFERENCE` checks a file against it. Fig. 7
     has its own environment, not the pinned one of the analysis scripts (README).

PT | O esquema de mecanismo do manuscrito da meta-analise (sua Fig. 7): como os microRNAs
     regulam os eixos de Alzheimer (BACE1, Abeta42) e de Parkinson (SNCA, alfa-sinucleina) e como
     chegam a um exame de sangue. E um esquema, nao um resultado: nenhum numero dele vem dos dados.

     Feito no tamanho final, 174 x 156 mm, em milimetros: Arial, texto de 8 a 12 pt, linhas de ao
     menos 0,5 pt, cores chapadas, sem transparencia, sem titulo nem legenda dentro da arte. O
     texto tem ao menos 4,5:1 contra o fundo (o scripts/45 mede no PDF). As moleculas sao os
     renders do PyMOL de estruturas depositadas feitos pelo scripts/42 e recortados pelo
     scripts/43, cada um desenhado sobre o tom do painel onde fica e colocado a 600 dpi ou mais.
     Icones, curvas e texto sao desenhados aqui com o matplotlib.

     Escrito uma vez, para uma figura de periodico, entao so em ingles (as outras figuras saem em
     ingles e portugues do Brasil) e nao importa scripts/_viz_style.py nem scripts/_bilingual.py: o
     primeiro mudaria o estilo do matplotlib e o segundo gravaria um PDF ao lado de cada PNG, e a
     figura tem de sair exatamente como foi desenhada para a submissao. A paleta esta escrita
     abaixo; o azul e o laranja de doenca sao AD_TEXT e PD_TEXT de _viz_style.py, e o tom cinza de
     painel e o cinza de filete sao BAND e RULE do mesmo arquivo.

     Saidas, em results/figures/: mirna_mechanism_schematic.en.png (RGB), .tif (RGB, LZW, 600 dpi,
     o arquivo para a revista) e .pdf. A pagina e opaca, entao tirar o canal alfa que o matplotlib
     grava nao muda nenhum pixel. O TIFF entregue a revista e redesenhado pixel a pixel por este
     script rodado com Python 3.12.10, matplotlib 3.10.8, NumPy 1.26.4, Pillow 12.3.0 e Arial
     (Windows); `--compare REFERENCIA` confere um arquivo contra ele. A Fig. 7 tem ambiente proprio,
     nao o fixado dos scripts de analise (README).

    python scripts/44_mirna_mechanism_figure.py [--compare reference.tif]
"""

import io
import os
import sys

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager, rcParams
from matplotlib.patches import FancyBboxPatch, Circle, Ellipse, Polygon, FancyArrowPatch, Rectangle
from PIL import Image

CROPS = "results/figures/structures/mirna_mechanism/crops"        # scripts/43
OUT_STEM = "results/figures/mirna_mechanism_schematic.en"
DPI = 600


rcParams.update({"font.family": "sans-serif", "font.sans-serif": ["Arial", "Liberation Sans", "DejaVu Sans"],
                 "pdf.fonttype": 42, "ps.fonttype": 42, "svg.fonttype": "none", "mathtext.default": "regular",
                 "image.composite_image": False})        # keep every PyMOL render as its own image, at its own resolution

# ---- palette (lettering colours checked >= 4.5:1 on white and on the panel tints) ------------------------------------
INK, INK2, NOTE = "#1b1b1a", "#3f3e3b", "#55544f"
AD, AD_TINT, AD_LINE = "#1f63b8", "#e8f0fa", "#9fc0ea"
PD, PD_TINT, PD_LINE = "#b8400f", "#fbece4", "#f0b79b"
MIR = "#6a3d9a"
SEED = "#c2185b"
GREY_TINT, GREY_LINE, GREY_FILL = "#f4f3f0", "#cfcdc7", "#dcdbd7"
BLOOD, PLASMA = "#a61c1c", "#f0dc9f"
LW = 0.8                                                   # pt, lines

W, H = 174.0, 156.0                                        # mm, final size
fig = ax = None                                            # set by build()


def T(x, y, s, size=8, color=INK, weight="normal", ha="left", va="center", z=6, ls=1.15):
    return ax.text(x, y, s, fontsize=size, color=color, fontweight=weight, ha=ha, va=va, zorder=z, linespacing=ls)


def panel(x, y, w, h, fc, ec, r=2.5, lw=0.6):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0,rounding_size=%s" % r, fc=fc, ec=ec, lw=lw, zorder=1))


def letter(x, y, s):
    T(x, y, s, size=11, weight="bold", color=INK)


def arrow(x0, y0, x1, y1, color=INK2, lw=0.9, ms=7, z=4):
    ax.add_patch(FancyArrowPatch((x0, y0), (x1, y1), arrowstyle="-|>", mutation_scale=ms, lw=lw, color=color, zorder=z,
                                 shrinkA=0, shrinkB=0))


def tbar(x0, y0, x1, y1, color=MIR, lw=1.0, half=1.7, z=4):
    """Repression symbol: a line that ends in a perpendicular bar."""
    ax.plot([x0, x1], [y0, y1], color=color, lw=lw, solid_capstyle="butt", zorder=z)
    dx, dy = x1 - x0, y1 - y0
    n = np.hypot(dx, dy)
    px, py = -dy / n, dx / n
    ax.plot([x1 - px * half, x1 + px * half], [y1 - py * half, y1 + py * half], color=color, lw=lw + 0.3, solid_capstyle="butt", zorder=z)


def wave(x0, x1, y, amp=0.9, n=3.0, color=MIR, lw=1.2, z=5):
    xs = np.linspace(x0, x1, 120)
    ax.plot(xs, y + amp * np.sin(2 * np.pi * n * (xs - x0) / (x1 - x0)), color=color, lw=lw, solid_capstyle="round", zorder=z)


def img(name, x, y, w, z=3):
    im = np.asarray(Image.open(os.path.join(CROPS, name + ".png")).convert("RGB"))
    h = w * im.shape[0] / im.shape[1]
    ax.imshow(im, extent=(x, x + w, y, y + h), zorder=z, interpolation="lanczos")
    return h


def mrna(x0, x1, y, name):
    """mRNA as a line; the 3' UTR is the open box at its end."""
    L = x1 - x0
    ax.plot([x0, x1], [y, y], color=INK2, lw=1.6, solid_capstyle="round", zorder=4)
    ax.add_patch(Rectangle((x0 + 0.62 * L, y - 1.15), 0.38 * L, 2.3, fc="white", ec=INK2, lw=LW, zorder=5))
    T(x0, y + 3.2, name, size=8, color=INK)
    ax.plot([x0 + 0.81 * L, x0 + 0.81 * L], [y - 1.15, y - 2.9], color=NOTE, lw=0.6, zorder=4)
    T(x0 + 0.81 * L, y - 4.6, "3′ UTR", size=8, color=NOTE, ha="center")
    return x0 + 0.81 * L                                   # centre of the UTR box


def disease_row(y0, name, color, label_color, mirs, mrna_name, protein_img, protein_label, protein_sub, arrow2_text, fib_img, fib_label, note, letter_char, monomer=False):
    """y0 = bottom of the panel (height 46.5)."""
    top = y0 + 46.5
    letter(55, top - 3.9, letter_char)
    T(60.5, top - 3.7, name, size=9, weight="bold", color=label_color)
    ymr = y0 + 19.2                                             # mRNA line height
    cx = mrna(56, 84, ymr, mrna_name)
    # microRNA names sit right next to their wave (right-aligned against it)
    n = len(mirs)
    for k, m in enumerate(mirs):
        T(cx - 6.5, ymr + 9.0 + (n - 1) * 1.9 - k * 3.8, m, size=8, color=MIR, weight="bold", ha="right")
    wave(cx - 5.2, cx + 5.2, ymr + 9.0, amp=0.7, n=2.5, lw=1.1)
    tbar(cx, ymr + 8.0, cx, ymr + 2.0)
    arrow(86.2, ymr, 102.8, ymr)
    T(94.5, ymr + 3.1, "translation", size=8, color=INK, ha="center")
    yc = ymr + 0.2                                              # protein stage centre
    if protein_img:
        h = img(protein_img, 104.8, y0 + 11.8, 18.6)
    arrow(125.5, yc, 141.0, yc)
    for k, line in enumerate(arrow2_text):
        T(133.2, yc + 3.1 + (len(arrow2_text) - 1 - k) * 3.5, line, size=8, color=INK, ha="center")
    fh = img(fib_img, 143.0, y0 + 11.0, 28.2)
    T(113.8, y0 + 8.6, protein_label, size=8, color=INK, weight="bold", ha="center")
    if protein_sub:
        T(113.8, y0 + 5.2, protein_sub, size=8, color=INK, ha="center")
    T(157.1, y0 + 8.0, fib_label, size=8, color=INK, weight="bold", ha="center")
    if note:
        T(170.6, top - 3.7, note, size=8, color=NOTE, ha="right")
    return ymr



def build():
    """EN/PT: draw the whole figure and return it | desenha a figura inteira e a devolve."""
    global fig, ax
    fig = plt.figure(figsize=(W / 25.4, H / 25.4), dpi=DPI)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, W); ax.set_ylim(0, H); ax.set_aspect("equal"); ax.axis("off")

    # =========================================================================================================== panels
    panel(1.5, 60.0, 49, 94.5, GREY_TINT, GREY_LINE)
    panel(53, 108.0, 119.5, 46.5, AD_TINT, AD_LINE)
    panel(53, 60.0, 119.5, 46.5, PD_TINT, PD_LINE)
    panel(1.5, 1.5, 171, 56.5, "white", GREY_LINE)

    # ------------------------------------------------------------------------------------------------------- a: AGO2
    letter(3.5, 150.7, "a")
    T(9.5, 151.8, "How a microRNA", size=9, weight="bold")
    T(9.5, 147.7, "represses a target", size=9, weight="bold")
    h = img("ago2", 3.4, 110.2, 45.2)
    for k, (col, txt, kind) in enumerate([(GREY_FILL, "AGO2 protein", "box"), (MIR, "guide miRNA", "line"),
                                          (SEED, "seed, nucleotides 2–8", "line"), ("#4a4a48", "target RNA", "line")]):
        yy = 103.6 - k * 4.5
        if kind == "box":
            ax.add_patch(Rectangle((4.6, yy - 1.3), 5.4, 2.6, fc=col, ec=NOTE, lw=0.5, zorder=4))
        else:
            ax.plot([4.6, 10.0], [yy, yy], color=col, lw=2.2, solid_capstyle="butt", zorder=4)
        T(12.0, yy, txt, size=8, color=INK2)
    # symbol key
    tbar(4.6, 82.6, 9.6, 82.6, lw=1.0, half=1.5)
    T(12.0, 82.6, "represses", size=8, color=INK2)
    arrow(4.6, 78.2, 9.8, 78.2)
    T(12.0, 78.2, "leads to", size=8, color=INK2)
    T(4.4, 71.4, "Seed pairing lowers", size=8, color=INK)
    T(4.4, 67.8, "translation and", size=8, color=INK)
    T(4.4, 64.2, "destabilises the mRNA", size=8, color=INK)

    # ------------------------------------------------------------------------------------------------------- b: AD
    disease_row(108.0, "Alzheimer’s disease", AD, AD, ["miR-29a/b-1", "miR-9"], "BACE1 mRNA", "bace1", "BACE1", "cleaves APP",
                ["Aβ42 forms", "fibrils"], "abeta42_axis", "Aβ42 fibril",
                "", "b")
    # ------------------------------------------------------------------------------------------------------- c: PD
    ymr = disease_row(60.0, "Parkinson’s disease", PD, PD, ["miR-7"], "SNCA mRNA", None, "α-synuclein", "monomer",
                      ["misfolds and", "aggregates"], "asyn_axis", "α-synuclein fibril",
                      "", "c")
    # unfolded alpha-synuclein chain icon (stage 2 of panel c)
    t = np.linspace(0, 1, 400)
    xs = 105.4 + 17.4 * t
    env = np.sin(np.pi * t) ** 0.6
    ys = ymr + 0.2 + env * (3.4 * np.sin(2 * np.pi * 2.1 * t + 0.5) + 1.7 * np.sin(2 * np.pi * 4.7 * t + 1.1) + 1.0 * np.sin(2 * np.pi * 8.3 * t))
    ax.plot(xs, ys, color=PD, lw=1.7, solid_capstyle="round", zorder=5)

    # ------------------------------------------------------------------------------------------------------- d: brain -> blood -> test
    letter(3.5, 54.4, "d")
    T(9.5, 54.6, "From cells to a blood test", size=9, weight="bold")
    cy = 33.0
    # neuron
    cx0 = 11.5
    for ang, ln in ((20, 7), (75, 6), (130, 7), (200, 6), (250, 6), (310, 6)):
        a = np.deg2rad(ang)
        ax.plot([cx0, cx0 + ln * np.cos(a)], [cy, cy + ln * np.sin(a)], color=INK2, lw=LW, zorder=4)
    ax.add_patch(Circle((cx0, cy), 3.3, fc="#dce6f0", ec=INK2, lw=LW, zorder=5))
    ax.add_patch(Circle((cx0, cy), 1.1, fc=INK2, ec="none", zorder=6))
    T(cx0, 21.5, "Neurons", size=8, ha="center")
    T(cx0, 18.0, "and glia", size=8, ha="center")
    ax.add_patch(FancyArrowPatch((20.5, cy), (32.5, cy), arrowstyle="-|>", mutation_scale=7, lw=0.9, color=INK2, zorder=4, shrinkA=0, shrinkB=0, linestyle=(0, (3, 2))))
    T(26.5, cy + 3.3, "proposed", size=8, color=NOTE, ha="center")
    # extracellular miRNA: vesicle / AGO2 / free
    T(56.0, 49.6, "miRNA outside the cell", size=8, ha="center")
    ex = 38.5
    ax.add_patch(Circle((ex + 4.5, 41.0), 4.3, fc="white", ec=INK2, lw=LW + 0.1, zorder=4))
    for (px, py) in ((ex + 3.0, 41.6), (ex + 5.4, 40.2), (ex + 4.4, 42.6)):
        ax.plot([px - 1.0, px + 1.0], [py, py + 0.3], color=MIR, lw=1.1, zorder=5)
    T(ex + 10.2, 41.0, "in vesicles", size=8)
    ax.add_patch(Ellipse((ex + 4.5, 32.2), 8.6, 5.4, fc=GREY_FILL, ec=NOTE, lw=0.6, zorder=4))
    wave(ex + 1.4, ex + 7.6, 32.2, amp=0.55, n=1.6, lw=1.1)
    T(ex + 10.2, 32.2, "bound to AGO2", size=8)
    wave(ex + 0.3, ex + 8.7, 23.8, amp=0.7, n=2.2, lw=1.3)
    T(ex + 10.2, 23.8, "free", size=8)
    arrow(75.5, cy, 83.0, cy)
    # blood tube
    tx, ty, tw, th = 85.5, 15.5, 7.6, 29.5
    ax.add_patch(FancyBboxPatch((tx, ty), tw, th, boxstyle="round,pad=0,rounding_size=3.0", fc="white", ec="none", zorder=3))
    ax.add_patch(Rectangle((tx + 0.5, ty + 11.2), tw - 1.0, 14.6, fc=PLASMA, ec="none", zorder=3.5))
    ax.add_patch(Rectangle((tx + 0.5, ty + 10.0), tw - 1.0, 1.2, fc="#f7f6f2", ec="none", zorder=3.6))
    ax.add_patch(FancyBboxPatch((tx + 0.5, ty + 0.5), tw - 1.0, 9.6, boxstyle="round,pad=0,rounding_size=2.4", fc=BLOOD, ec="none", zorder=3.5))
    ax.add_patch(FancyBboxPatch((tx, ty), tw, th, boxstyle="round,pad=0,rounding_size=3.0", fc="none", ec=INK2, lw=LW + 0.1, zorder=5))
    ax.add_patch(Rectangle((tx - 0.8, ty + th - 1.2), tw + 1.6, 2.4, fc=INK2, ec="none", zorder=5.5))
    T(tx + tw + 2.4, 36.6, "plasma or serum,", size=8)
    T(tx + tw + 2.4, 33.2, "EV fraction", size=8)
    T(tx + tw + 2.4, 21.6, "blood cells", size=8)
    ax.add_patch(Polygon([(tx + tw + 1.8, 9.6), (tx + tw + 7.0, 9.6), (tx + tw + 4.4, 14.6)], closed=True, fc="#fbbd2a", ec=INK2, lw=0.6, zorder=5))
    T(tx + tw + 4.4, 10.9, "!", size=8, weight="bold", ha="center", color=INK, z=7)
    T(tx + tw + 9.0, 12.4, "cells and haemolysis", size=8)
    T(tx + tw + 9.0, 9.0, "add or alter miRNA", size=8)
    arrow(125.0, cy, 131.0, cy)
    # assay: amplification curves
    qx, qy, qw, qh = 132.5, 25.5, 15, 15
    ax.add_patch(Rectangle((qx, qy), qw, qh, fc="white", ec=INK2, lw=LW, zorder=4))
    xs = np.linspace(0, 1, 100)
    for shift, col in ((0.42, MIR), (0.55, INK2), (0.68, NOTE)):
        ax.plot(qx + 1 + xs * (qw - 2), qy + 1.3 + 11.5 / (1 + np.exp(-14 * (xs - shift))), color=col, lw=1.0, zorder=5)
    ax.plot([qx + 1, qx + qw - 1], [qy + 6, qy + 6], color=INK2, lw=0.6, ls=(0, (2, 1.5)), zorder=5)
    T(qx + qw / 2, 21.0, "RT-qPCR or", size=8, ha="center")
    T(qx + qw / 2, 17.6, "sequencing", size=8, ha="center")
    arrow(149.5, cy, 154.5, cy)
    # ROC
    rx, ry, rw = 156.0, 27.0, 11.0
    ax.add_patch(Rectangle((rx, ry), rw, rw, fc="white", ec=INK2, lw=LW, zorder=4))
    ax.plot([rx, rx + rw], [ry, ry + rw], color=NOTE, lw=0.6, ls=(0, (2, 1.5)), zorder=5)
    tt = np.linspace(0, 1, 60)
    ax.plot(rx + tt * rw, ry + rw * (1 - (1 - tt) ** 2.6), color=AD, lw=1.1, zorder=5)
    ax.plot(rx + tt * rw, ry + rw * (1 - (1 - tt) ** 2.3), color=PD, lw=1.1, zorder=5)
    T(rx + rw / 2, 21.0, "Diagnostic", size=8, ha="center")
    T(rx + rw / 2, 17.6, "accuracy (AUC)", size=8, ha="center")

    return fig


def save_all(fig):
    """
    EN | PNG and TIFF as 8-bit RGB (the page is opaque, so the alpha channel carries nothing),
         and the PDF, from the same figure object.
    PT | PNG e TIFF em RGB de 8 bits (a pagina e opaca, entao o canal alfa nao leva nada) e o
         PDF, do mesmo objeto de figura.
    """
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=DPI, facecolor="white")
    buf.seek(0)
    rgba = Image.open(buf)
    if np.asarray(rgba)[..., 3].min() != 255:
        sys.exit("EN/PT: the page is not opaque; flattening to RGB would change pixels")
    rgb = rgba.convert("RGB")
    rgb.save(OUT_STEM + ".png", dpi=(DPI, DPI), optimize=True)
    rgb.save(OUT_STEM + ".tif", dpi=(DPI, DPI), compression="tiff_lzw")
    fig.savefig(OUT_STEM + ".pdf", facecolor="white")
    return rgb


def compare(rgb, reference):
    """EN/PT: pixel-by-pixel comparison with a reference image | comparacao pixel a pixel com uma imagem de referencia."""
    ref = np.asarray(Image.open(reference).convert("RGB"))
    new = np.asarray(rgb)
    if ref.shape != new.shape:
        print(f"EN/PT: {reference}: {ref.shape[1]} x {ref.shape[0]} px, the figure is {new.shape[1]} x {new.shape[0]} px")
        return 1
    n = int((np.abs(ref.astype(int) - new.astype(int)).max(axis=2) > 0).sum())
    print(f"EN/PT: {reference}: " + ("pixel-identical" if n == 0 else f"{n} of {ref.shape[0] * ref.shape[1]} pixels differ"))
    return 0 if n == 0 else 1


def main():
    argv = sys.argv[1:]
    reference = None
    if argv[:1] == ["--compare"]:
        if len(argv) != 2:
            sys.exit("EN/PT: usage: python scripts/44_mirna_mechanism_figure.py [--compare reference.tif]")
        reference = argv[1]
    elif argv:
        sys.exit("EN/PT: usage: python scripts/44_mirna_mechanism_figure.py [--compare reference.tif]")
    missing = [n for n in ("ago2", "bace1", "abeta42_axis", "asyn_axis") if not os.path.exists(os.path.join(CROPS, n + ".png"))]
    if missing:
        sys.exit(f"EN/PT: missing crops {missing} in {CROPS}; run scripts/42 and scripts/43 first")
    try:
        font_manager.findfont("Arial", fallback_to_default=False)
    except ValueError:
        print("EN/PT: WARNING Arial is not installed; the lettering falls back to Liberation Sans or DejaVu Sans, "
              "and the journal asks for Arial or Helvetica")
    os.makedirs(os.path.dirname(OUT_STEM), exist_ok=True)
    print("=" * 78)
    print("EN | Mechanism schematic | PT | Esquema de mecanismo")
    print("=" * 78)
    rgb = save_all(build())
    for ext in ("png", "tif", "pdf"):
        print(f"EN/PT -> {OUT_STEM}.{ext}")
    return compare(rgb, reference) if reference else 0


if __name__ == "__main__":
    sys.exit(main())
