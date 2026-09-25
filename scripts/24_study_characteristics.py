#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EN | A compact composition figure for the 51 estimates eligible for the primary pool:
     two donuts (disease, marker type) and one ranked bar (biofluid), computed live from
     data/extracted/diagnostic_accuracy_extraction.csv rather than retyped from
     Supplementary Table S1.
PT | Uma figura compacta de composicao para as 51 estimativas elegiveis para o pool
     primario: dois donuts (doenca, tipo de marcador) e uma barra ranqueada (biofluido),
     calculados diretamente de data/extracted/diagnostic_accuracy_extraction.csv em vez
     de redigitados da Tabela Suplementar S1.

EN | Why this exists. Supplementary Table S1 carries this breakdown as four small
     tables, which is the right place for the exhaustive version (it also splits by
     quantification method and cohort stage, which this figure does not). But a reader
     of the main text benefits from seeing, in one glance, that the evidence base is
     PD-heavy, single-marker-heavy, and serum-heavy, before reading the pooled-accuracy
     results that follow - each of those three imbalances matters for how those results
     should be read (section 4.3 discusses the panel-marker and biofluid imbalances
     directly). This is a compositional summary of the same 51 estimates Table S1
     tabulates in full, not a new or competing count.
PT | Por que isto existe. A Tabela Suplementar S1 traz este detalhamento em quatro
     tabelas pequenas, o que e o lugar certo para a versao exaustiva (ela tambem separa
     por metodo de quantificacao e estagio de coorte, o que esta figura nao faz). Mas um
     leitor do texto principal se beneficia de ver, num so olhar, que a base de evidencia
     e mais voltada a DP, a marcador isolado e a soro, antes de ler os resultados de
     acuracia agrupada que vem a seguir - cada um desses tres desequilibrios importa para
     como esses resultados devem ser lidos (a secao 4.3 discute os desequilibrios de
     marcador-painel e de biofluido diretamente). Isto e um resumo composicional das
     mesmas 51 estimativas que a Tabela S1 tabula por completo, nao uma contagem nova ou
     concorrente.

EN | Every count is aggregated at run time from the extraction table filtered to
     eligible_primary_pool == "yes", the same filter and the same 51-row total that
     Supplementary Table S1 and scripts/08_verify_consistency.py both use, so the figure
     cannot silently disagree with the table it summarises.
PT | Toda contagem e agregada em tempo de execucao a partir da tabela de extracao
     filtrada por eligible_primary_pool == "yes", o mesmo filtro e o mesmo total de 51
     linhas que a Tabela Suplementar S1 e o scripts/08_verify_consistency.py usam, entao
     a figura nao pode discordar em silencio da tabela que resume.

    python scripts/24_study_characteristics.py
"""

import csv
import os
import sys
from collections import Counter, OrderedDict

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _bilingual import LANGS, t, fig_path

EXTRACTION = "data/extracted/diagnostic_accuracy_extraction.csv"
FIG_DIR = "results/figures"

DISEASE_LABEL = {"AD": ("Alzheimer's disease", "Doença de Alzheimer"),
                 "PD": ("Parkinson's disease", "Doença de Parkinson")}
DISEASE_COLOUR = {"AD": "#3B6EA5", "PD": "#B3541E"}

MARKER_LABEL = {"single_miRNA": ("Single microRNA", "MicroRNA isolado"),
                "multi_miRNA_panel": ("Multi-microRNA panel", "Painel multi-microRNA")}
MARKER_COLOUR = {"single_miRNA": "#2a78d6", "multi_miRNA_panel": "#1baf7a"}
BAR_COLOUR = "#2a78d6"

# EN | Merge the extraction table's fine-grained biofluid codes into the same seven
#      categories Supplementary Table S1 reports.
# PT | Funde os codigos finos de biofluido da tabela de extracao nas mesmas sete
#      categorias que a Tabela Suplementar S1 reporta.
BIOFLUID_GROUP = OrderedDict([
    ("serum", ("Serum", "Soro")),
    ("serum_neuronal_EV", ("Serum-derived neuronal EV", "EV neuronal derivada de soro")),
    ("plasma", ("Plasma", "Plasma")),
    ("blood", ("Whole blood / blood", "Sangue total / sangue")),
    ("whole_blood", ("Whole blood / blood", "Sangue total / sangue")),
    ("CSF", ("Cerebrospinal fluid (CSF)", "Líquido cefalorraquidiano (LCR)")),
    ("serum_exosome", ("Serum exosome", "Exossomo de soro")),
    ("plasma_neuronal_EV", ("Plasma-derived EV", "EV derivada de plasma")),
    ("plasma_EV", ("Plasma-derived EV", "EV derivada de plasma")),
])


def donut(ax, counts, colours, labels, lang, title):
    total = sum(counts.values())
    keys = list(counts.keys())
    sizes = [counts[k] for k in keys]
    cols = [colours[k] for k in keys]
    wedges, _ = ax.pie(sizes, colors=cols, startangle=90, counterclock=False,
                        wedgeprops=dict(width=0.42, edgecolor="white", linewidth=1.5))
    ax.set_title(title, fontsize=9.6, pad=2)
    ax.text(0, 0, str(total), ha="center", va="center", fontsize=15, weight="bold",
            color="#333333")
    ax.text(0, -0.22, t(lang, "estimates", "estimativas"), ha="center", va="center",
            fontsize=6.8, color="#777777")
    handles = wedges
    legend_labels = [f"{t(lang, *labels[k])} ({counts[k]}, {100*counts[k]/total:.0f}%)"
                     for k in keys]
    ax.legend(handles, legend_labels, loc="upper center", bbox_to_anchor=(0.5, -0.02),
              fontsize=7.4, frameon=False, ncol=1)


def ranked_bar(ax, counts, lang):
    items = sorted(counts.items(), key=lambda kv: -kv[1])
    labels = [t(lang, *lbl) for lbl, _ in items]
    values = [v for _, v in items]
    total = sum(values)
    y = list(range(len(items) - 1, -1, -1))
    ax.barh(y, values, color=BAR_COLOUR, height=0.62)
    for yi, v in zip(y, values):
        ax.text(v + total * 0.012, yi, f"{v} ({100*v/total:.0f}%)", va="center",
                fontsize=7.6, color="#333333")
    ax.set_yticks(y)
    ax.set_yticklabels(labels, fontsize=8.2)
    ax.set_xlim(0, max(values) * 1.28)
    ax.set_xlabel(t(lang, "estimates (n = 51)", "estimativas (n = 51)"), fontsize=8.4)
    ax.set_title(t(lang, "By biofluid", "Por biofluido"), fontsize=9.6)
    ax.spines[["top", "right", "left"]].set_visible(False)
    ax.tick_params(left=False)


def plot(rows, path, lang):
    disease_counts = Counter(r["disease"] for r in rows)
    marker_counts = Counter(r["marker_type"] for r in rows)
    biofluid_counts = Counter()
    biofluid_label = {}
    for r in rows:
        code = r["biofluid"]
        label = BIOFLUID_GROUP.get(code, (code, code))
        biofluid_counts[label[0]] += 1
        biofluid_label[label[0]] = label

    fig = plt.figure(figsize=(11.6, 4.1))
    gs = fig.add_gridspec(1, 3, width_ratios=[1, 1, 2.05], wspace=0.85)
    ax1 = fig.add_subplot(gs[0, 0])
    ax2 = fig.add_subplot(gs[0, 1])
    ax3 = fig.add_subplot(gs[0, 2])

    donut(ax1, disease_counts, DISEASE_COLOUR, DISEASE_LABEL, lang,
          t(lang, "By disease", "Por doença"))
    donut(ax2, marker_counts, MARKER_COLOUR, MARKER_LABEL, lang,
          t(lang, "By marker type", "Por tipo de marcador"))

    bar_counts = {biofluid_label[lbl_en]: cnt for lbl_en, cnt in biofluid_counts.items()}
    ranked_bar(ax3, bar_counts, lang)

    fig.suptitle(t(lang,
                   "Composition of the 51 estimates eligible for the primary pool",
                   "Composição das 51 estimativas elegíveis para o pool primário"),
                 fontsize=11, y=1.03)
    fig.savefig(path, dpi=600, bbox_inches="tight")
    plt.close(fig)


def main():
    if not os.path.exists(EXTRACTION):
        sys.exit(f"EN/PT: missing {EXTRACTION}")
    rows = [r for r in csv.DictReader(open(EXTRACTION, encoding="utf-8"))
            if r["eligible_primary_pool"] == "yes"]
    if len(rows) != 51:
        sys.exit(f"EN/PT: expected 51 eligible estimates, found {len(rows)}")
    os.makedirs(FIG_DIR, exist_ok=True)
    for lang in LANGS:
        plot(rows, fig_path(FIG_DIR, "study_characteristics", lang), lang)

    print("EN/PT | Study characteristics | Características dos estudos")
    print("  disease:", dict(Counter(r["disease"] for r in rows)))
    print("  marker_type:", dict(Counter(r["marker_type"] for r in rows)))
    for lang in LANGS:
        print(f"EN/PT -> {fig_path(FIG_DIR, 'study_characteristics', lang)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
