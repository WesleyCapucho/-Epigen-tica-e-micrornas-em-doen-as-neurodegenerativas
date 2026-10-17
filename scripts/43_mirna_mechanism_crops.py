#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EN | Crop the four PyMOL renders of scripts/42 to their content and save them as RGB PNG, the
     form in which scripts/44 places them in the mechanism schematic.

     Each render was drawn on the tint of the panel it will sit in (scripts/42), so the margin
     around the molecule is one flat colour, read from the pixel at (2, 2). Anything that differs
     from that colour by more than 10 levels in any channel is content; the crop is the bounding
     box of the content plus 14 px. Nothing else is done to the pixels: no resampling, no
     colour change, so what scripts/44 places is what PyMOL drew. Only the four views used in the
     figure are cropped (the side views of the fibrils are not).

     Needs numpy and Pillow, not PyMOL. The crops are kept in the repository, so scripts/44 can be
     run, and Fig. 7 redrawn, on a machine that has no PyMOL.
PT | Recorta as quatro renders do PyMOL do scripts/42 ao conteudo e as salva em PNG RGB, a forma
     em que o scripts/44 as coloca no esquema de mecanismo.

     Cada render foi desenhado sobre o tom do painel onde vai ficar (scripts/42), entao a margem
     em volta da molecula e de uma cor so, lida no pixel (2, 2). Tudo que difere dessa cor por mais
     de 10 niveis em algum canal e conteudo; o recorte e a caixa do conteudo mais 14 px. Nada mais
     e feito nos pixels: sem reamostragem, sem mudanca de cor, de modo que o que o scripts/44
     coloca e o que o PyMOL desenhou. So as quatro vistas usadas na figura sao recortadas (as
     vistas laterais das fibrilas nao).

     Precisa de numpy e Pillow, nao do PyMOL. Os recortes ficam no repositorio, entao o
     scripts/44 roda, e a Fig. 7 e redesenhada, numa maquina sem PyMOL.

    python scripts/43_mirna_mechanism_crops.py
"""

import os
import sys

import numpy as np
from PIL import Image

SRC = "results/figures/structures/mirna_mechanism/renders"
OUT = "results/figures/structures/mirna_mechanism/crops"
PANELS = ("ago2", "bace1", "abeta42_axis", "asyn_axis")
PAD = 14                       # EN/PT: px kept around the content | px mantidos em volta do conteudo
TOLERANCE = 10                 # EN/PT: levels from the margin colour that count as content | niveis a partir da cor da margem


def main():
    missing = [n for n in PANELS if not os.path.exists(os.path.join(SRC, n + ".png"))]
    if missing:
        sys.exit(f"EN/PT: missing renders {missing} in {SRC}; run scripts/42 first")
    os.makedirs(OUT, exist_ok=True)
    print("=" * 78)
    print("EN | Mechanism schematic: crops of the structure renders | PT | Recortes dos renders de estrutura")
    print("=" * 78)
    for name in PANELS:
        im = Image.open(os.path.join(SRC, name + ".png")).convert("RGB")
        a = np.asarray(im)
        margin = a[2, 2].astype(int)                         # the render was drawn on the colour of its panel
        mask = np.abs(a.astype(int) - margin).max(axis=2) > TOLERANCE
        ys, xs = np.where(mask)
        y0, y1 = max(ys.min() - PAD, 0), min(ys.max() + PAD, a.shape[0] - 1)
        x0, x1 = max(xs.min() - PAD, 0), min(xs.max() + PAD, a.shape[1] - 1)
        c = im.crop((x0, y0, x1 + 1, y1 + 1))
        c.save(os.path.join(OUT, name + ".png"))
        print("%-14s %dx%d -> %dx%d  (aspect w/h %.3f)" % (name, im.width, im.height, c.width, c.height, c.width / c.height))
    print(f"EN/PT -> {OUT}/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
