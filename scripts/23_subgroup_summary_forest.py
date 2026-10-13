#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EN | A compact point-range ("summary forest") chart of the core pooled-AUC subgroups
     reported in Table 1, read live from
     results/tables/meta_analysis_pooled_auc_primary.csv rather than retyped.
PT | Um grafico compacto de ponto-e-intervalo ("forest de resumo") dos subgrupos
     centrais de AUC agrupada reportados na Tabela 1, lido diretamente de
     results/tables/meta_analysis_pooled_auc_primary.csv em vez de redigitado.

EN | Why this exists. Table 1 already carries these numbers, but a table asks the
     reader to compare several digits across rows by eye. A point-range plot puts the
     same estimates on one shared AUC axis with their 95% Hartung-Knapp interval, so
     the AD-versus-PD gap and the panel-versus-single gap are visible in one glance.
     AD and PD are each other's own primary outcome here (section 2.2), so they are
     drawn first and separately; the combined AD+PD figure is drawn as a labelled
     secondary summary, never averaged into the same row as either disease. This is
     deliberately not a second forest plot of all individual circulating estimates - that plot
     exists at the study level in Supplementary Figure S1.
PT | Por que isto existe. A Tabela 1 ja traz estes numeros, mas uma tabela pede ao
     leitor para comparar varios digitos em linhas a olho. Um grafico de ponto-e-
     intervalo poe as mesmas estimativas num eixo de AUC compartilhado com seu
     intervalo de Hartung-Knapp a 95%, entao a diferenca DA-versus-DP e a diferenca
     painel-versus-isolado ficam visiveis num so olhar. DA e DP sao cada uma seu
     proprio desfecho primario aqui (secao 2.2), entao sao desenhadas primeiro e
     separadamente; a cifra combinada DA+DP e desenhada como resumo secundario
     rotulado, nunca fundida na mesma linha que qualquer doenca. Deliberadamente nao
     e um segundo forest plot das estimativas circulantes individuais - esse existe no nivel
     de estudo na Figura Suplementar S1.

EN | Every number drawn is read from meta_analysis_pooled_auc_primary.csv at run
     time, the same file scripts/08_verify_consistency.py checks against Table 1's
     own numbers, so this figure cannot silently disagree with the table it
     illustrates.
PT | Todo numero desenhado e lido de meta_analysis_pooled_auc_primary.csv em tempo
     de execucao, o mesmo arquivo que scripts/08_verify_consistency.py confere
     contra os numeros da propria Tabela 1, entao esta figura nao pode discordar em
     silencio da tabela que ilustra.

    python scripts/23_subgroup_summary_forest.py
"""

import csv
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _bilingual import LANGS, t, fig_path

POOLED = "results/tables/meta_analysis_pooled_auc_primary.csv"
FIG_DIR = "results/figures"

# EN | Reading order: the two primary disease outcomes first, then the secondary
#      combined figure, then the marker-type comparison across both diseases.
# PT | Ordem de leitura: os dois desfechos primarios de doenca primeiro, depois a
#      cifra secundaria combinada, depois a comparacao por tipo de marcador nas
#      duas doencas.
ROWS = [
    ("AD - all markers | todos marcadores (PRIMARY 1)", "disease",
     ("Alzheimer's disease – primary outcome", "Doença de Alzheimer – desfecho primário")),
    ("PD - all markers | todos marcadores (PRIMARY 2)", "disease",
     ("Parkinson's disease – primary outcome", "Doença de Parkinson – desfecho primário")),
    ("Overall AD+PD (all eligible) | Global (SECONDARY)", "secondary",
     ("AD+PD combined – secondary", "DA+DP combinado – secundário")),
    ("All - single miRNA | miRNA isolado", "marker",
     ("Single microRNA – both diseases", "MicroRNA isolado – ambas as doenças")),
    ("All - multi-miRNA panel | painel multi-miRNA", "marker",
     ("Multi-microRNA panel – both diseases", "Painel multi-microRNA – ambas as doenças")),
]

COLOUR = {"disease": "#2a78d6", "secondary": "#9aa0a6", "marker": "#1baf7a"}


def load_pooled():
    with open(POOLED, encoding="utf-8") as fh:
        rows = {r["subgroup"]: r for r in csv.DictReader(fh)}
    return rows


def plot(pooled, path, lang):
    fig, ax = plt.subplots(figsize=(7.8, 3.8))
    n = len(ROWS)
    y_positions = []
    y = n
    section_breaks = []
    prev_kind = None
    for key, kind, label in ROWS:
        if prev_kind is not None and kind != prev_kind:
            y -= 0.55
            section_breaks.append(y + 0.275)
        y_positions.append(y)
        y -= 1
        prev_kind = kind

    for (key, kind, label), ypos in zip(ROWS, y_positions):
        r = pooled[key]
        est = float(r["pooled_auc"])
        lo = float(r["ci_low_hk"])
        hi = float(r["ci_high_hk"])
        nstud = int(r["n_studies"])
        ax.plot([lo, hi], [ypos, ypos], color=COLOUR[kind], lw=1.6, zorder=2)
        ax.plot([lo, lo], [ypos - 0.09, ypos + 0.09], color=COLOUR[kind], lw=1.6, zorder=2)
        ax.plot([hi, hi], [ypos - 0.09, ypos + 0.09], color=COLOUR[kind], lw=1.6, zorder=2)
        ax.scatter([est], [ypos], s=70, color=COLOUR[kind], zorder=3,
                   edgecolor="white", linewidth=0.8)
        ax.text(hi + 0.012, ypos,
                t(lang, f"{est:.2f} ({lo:.2f}–{hi:.2f})  n={nstud} studies",
                  f"{est:.2f} ({lo:.2f}–{hi:.2f})  n={nstud} estudos"),
                va="center", ha="left", fontsize=7.6, color="#333333")

    ymin = min(y_positions) - 0.75
    ymax = max(y_positions) + 0.55
    ax.axvline(0.5, color="#aaaaaa", ls="--", lw=1, zorder=1)
    ax.text(0.5, ymin + 0.12, t(lang, "no discrimination", "sem discriminação"),
            ha="center", va="bottom", fontsize=7, color="#888888")

    ax.set_yticks(y_positions)
    ax.set_yticklabels([t(lang, *label) for _, _, label in ROWS], fontsize=8.6)
    ax.set_ylim(ymin, ymax)
    ax.set_xlim(0.35, 1.08)
    ax.set_xlabel(t(lang, "Primary pooled AUC (95% Hartung-Knapp CI)",
                   "AUC agrupada primária (IC 95% de Hartung-Knapp)"), fontsize=9)
    # Title omitted: the caption in the manuscript names the figure.
    for yb in section_breaks:
        ax.axhline(yb, color="#e3e3e0", lw=0.8, zorder=0)
    ax.spines[["top", "right", "left"]].set_visible(False)
    ax.tick_params(left=False)
    fig.tight_layout()
    fig.savefig(path, dpi=600, bbox_inches="tight")
    plt.close(fig)


def main():
    if not os.path.exists(POOLED):
        sys.exit(f"EN/PT: missing {POOLED}")
    pooled = load_pooled()
    missing = [key for key, _, _ in ROWS if key not in pooled]
    if missing:
        sys.exit(f"EN/PT: subgroup(s) not found in {POOLED}: {missing}")
    os.makedirs(FIG_DIR, exist_ok=True)
    for lang in LANGS:
        plot(pooled, fig_path(FIG_DIR, "subgroup_summary_forest", lang), lang)
    print("EN/PT | Subgroup summary forest plot | Grafico de resumo dos subgrupos")
    for key, _, _ in ROWS:
        r = pooled[key]
        print(f"  {key:55s} AUC {r['pooled_auc']} ({r['ci_low_hk']}-{r['ci_high_hk']})")
    for lang in LANGS:
        print(f"EN/PT -> {fig_path(FIG_DIR, 'subgroup_summary_forest', lang)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
