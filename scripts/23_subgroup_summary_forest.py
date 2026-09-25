#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EN | A compact point-range ("summary forest") chart of the five core pooled-AUC
     subgroups already reported in Table 1, read live from
     results/tables/meta_analysis_pooled_auc.csv rather than retyped.
PT | Um grafico compacto de ponto-e-intervalo ("forest de resumo") dos cinco
     subgrupos centrais de AUC agrupada ja reportados na Tabela 1, lido diretamente
     de results/tables/meta_analysis_pooled_auc.csv em vez de redigitado.

EN | Why this exists. Table 1 already carries these five numbers, but a table asks the
     reader to compare six digits across five rows by eye. A point-range plot puts the
     same five estimates on one shared AUC axis with their 95% CI, so the panel-versus-
     single gap and the AD-versus-PD gap are visible in one glance rather than computed
     by the reader. It is deliberately not a second forest plot of all 41 individual
     estimates - that plot already exists at the study level in Supplementary Figure S1
     and was moved there because it does not read at manuscript width. This one has five
     rows and stays in the main text for exactly that reason.
PT | Por que isto existe. A Tabela 1 ja traz estes cinco numeros, mas uma tabela pede ao
     leitor para comparar seis digitos em cinco linhas a olho. Um grafico de ponto-e-
     intervalo poe as mesmas cinco estimativas num eixo de AUC compartilhado com seu IC
     95%, entao a diferenca painel-versus-isolado e a diferenca DA-versus-DP ficam
     visiveis num so olhar em vez de calculadas pelo leitor. Deliberadamente nao e um
     segundo forest plot das 41 estimativas individuais - esse ja existe no nivel de
     estudo na Figura Suplementar S1 e foi movido para la porque nao se le na largura do
     manuscrito. Este tem cinco linhas e fica no texto principal exatamente por isso.

EN | Every number drawn is read from meta_analysis_pooled_auc.csv at run time, the same
     file scripts/08_verify_consistency.py checks against Table 1's own numbers, so this
     figure cannot silently disagree with the table it illustrates.
PT | Todo numero desenhado e lido de meta_analysis_pooled_auc.csv em tempo de execucao, o
     mesmo arquivo que scripts/08_verify_consistency.py confere contra os numeros da
     propria Tabela 1, entao esta figura nao pode discordar em silencio da tabela que
     ilustra.

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

POOLED = "results/tables/meta_analysis_pooled_auc.csv"
FIG_DIR = "results/figures"

# EN | The five rows of Table 1, in the same top-to-bottom reading order, keyed by the
#      exact "subgroup" string meta_analysis_pooled_auc.csv uses.
# PT | As cinco linhas da Tabela 1, na mesma ordem de leitura de cima para baixo,
#      indexadas pela string exata "subgroup" que meta_analysis_pooled_auc.csv usa.
ROWS = [
    ("Overall (all eligible) | Global", "group",
     ("Overall (all eligible estimates)", "Global (todas as estimativas elegíveis)")),
    ("AD - all markers | todos marcadores", "disease",
     ("Alzheimer's disease – all markers", "Doença de Alzheimer – todos os marcadores")),
    ("PD - all markers | todos marcadores", "disease",
     ("Parkinson's disease – all markers", "Doença de Parkinson – todos os marcadores")),
    ("All - single miRNA | miRNA isolado", "marker",
     ("Single microRNA – all", "MicroRNA isolado – todos")),
    ("All - multi-miRNA panel | painel multi-miRNA", "marker",
     ("Multi-microRNA panel – all", "Painel multi-microRNA – todos")),
]

COLOUR = {"group": "#2c3e50", "disease": "#2c3e50", "marker": "#2c3e50"}
SECTION_AFTER = {0: t}  # placeholder, real section breaks handled in plot()


def load_pooled():
    with open(POOLED, encoding="utf-8") as fh:
        rows = {r["subgroup"]: r for r in csv.DictReader(fh)}
    return rows


def plot(pooled, path, lang):
    fig, ax = plt.subplots(figsize=(7.4, 3.6))
    n = len(ROWS)
    y_positions = []
    y = n
    section_breaks = []
    prev_kind = None
    for key, kind, label in ROWS:
        if prev_kind is not None and kind != prev_kind and prev_kind != "group":
            y -= 0.55
            section_breaks.append(y + 0.275)
        y_positions.append(y)
        y -= 1
        prev_kind = kind

    for (key, kind, label), ypos in zip(ROWS, y_positions):
        r = pooled[key]
        est = float(r["pooled_auc"])
        lo = float(r["ci_low"])
        hi = float(r["ci_high"])
        k = int(r["k_estimates"])
        nstud = int(r["n_studies"])
        ax.plot([lo, hi], [ypos, ypos], color=COLOUR[kind], lw=1.6, zorder=2)
        ax.plot([lo, lo], [ypos - 0.09, ypos + 0.09], color=COLOUR[kind], lw=1.6, zorder=2)
        ax.plot([hi, hi], [ypos - 0.09, ypos + 0.09], color=COLOUR[kind], lw=1.6, zorder=2)
        ax.scatter([est], [ypos], s=70, color=COLOUR[kind], zorder=3,
                   edgecolor="white", linewidth=0.8)
        ax.text(hi + 0.012, ypos,
                t(lang, f"{est:.2f} ({lo:.2f}–{hi:.2f})  k={k}, n={nstud}",
                  f"{est:.2f} ({lo:.2f}–{hi:.2f})  k={k}, n={nstud}"),
                va="center", ha="left", fontsize=7.6, color="#333333")

    ymin = min(y_positions) - 0.75
    ymax = max(y_positions) + 0.55
    ax.axvline(0.5, color="#aaaaaa", ls="--", lw=1, zorder=1)
    ax.text(0.5, ymin + 0.12, t(lang, "no discrimination", "sem discriminação"),
            ha="center", va="bottom", fontsize=7, color="#888888")

    ax.set_yticks(y_positions)
    ax.set_yticklabels([t(lang, *label) for _, _, label in ROWS], fontsize=8.6)
    ax.set_ylim(ymin, ymax)
    ax.set_xlim(0.45, 1.05)
    ax.set_xlabel(t(lang, "Pooled AUC (95% CI)", "AUC agrupada (IC 95%)"), fontsize=9)
    ax.set_title(t(lang, "Pooled diagnostic accuracy, core subgroups (Table 1)",
                   "Acurácia diagnóstica agrupada, subgrupos centrais (Tabela 1)"),
                 fontsize=10.5)
    for yb in section_breaks:
        ax.axhline(yb, color="#e3e3e0", lw=0.8, zorder=0)
    ax.spines[["top", "right", "left"]].set_visible(False)
    ax.tick_params(left=False)
    fig.tight_layout()
    fig.savefig(path, dpi=200, bbox_inches="tight")
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
        print(f"  {key:45s} AUC {r['pooled_auc']} ({r['ci_low']}-{r['ci_high']})")
    for lang in LANGS:
        print(f"EN/PT -> {fig_path(FIG_DIR, 'subgroup_summary_forest', lang)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
