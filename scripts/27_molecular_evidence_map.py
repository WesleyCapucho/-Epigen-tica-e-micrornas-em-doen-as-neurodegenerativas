#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EN | Molecular evidence map for the studies in the primary, circulating pools: for
     every pooled study, what kind of evidence the study itself offers that its marker
     sits on a disease pathway, from an experiment done in the paper down to nothing at
     all. Read from data/extracted/molecular_evidence_map.csv, which stores one row per
     claim with the verbatim sentence it was read from.
PT | Mapa de evidencia molecular para os estudos dos pools primarios circulantes:
     para cada estudo agregado, que tipo de evidencia o proprio estudo oferece de que seu
     marcador esta numa via da doenca, de um experimento feito no artigo ate nenhuma.
     Lido de data/extracted/molecular_evidence_map.csv, que guarda uma linha por
     afirmacao com a frase literal de onde foi lida.

EN | Why this exists. A pooled AUC says a marker separates patients from controls; it
     says nothing about whether the marker is part of the disease. The two questions are
     easy to blur in prose, so this figure keeps them apart by sorting each claim by the
     strength of its support: an experiment in the included study, an experiment the
     authors cite from their own earlier work, a claim cited from other literature,
     a target prediction, or a correlation with a clinical or biomarker measure. None of
     these is evidence of diagnostic value, and a high AUC is not evidence of mechanism.
PT | Por que isto existe. Uma AUC agregada diz que um marcador separa pacientes de
     controles; nao diz se o marcador faz parte da doenca. As duas perguntas se confundem
     facilmente no texto, entao esta figura as mantem separadas ordenando cada afirmacao
     pela forca do seu apoio: um experimento no estudo incluido, um experimento que os
     autores citam de trabalho proprio anterior, uma afirmacao citada de outra literatura,
     uma predicao de alvo, ou uma correlacao com uma medida clinica ou de biomarcador.
     Nada disso e evidencia de valor diagnostico, e uma AUC alta nao e evidencia de
     mecanismo.

EN | The script fails if the map and the primary pool disagree on which studies were
     pooled, so the figure cannot silently omit a pooled study or show one that was not.
PT | O script falha se o mapa e o pool primario discordarem sobre quais estudos foram
     agregados, entao a figura nao pode omitir em silencio um estudo agregado nem mostrar
     um que nao foi.

    python scripts/27_molecular_evidence_map.py
"""

import csv
import os
import sys
import textwrap

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _bilingual import LANGS, t, fig_path

MAP = "data/extracted/molecular_evidence_map.csv"
SELECTION = "results/tables/one_estimate_per_study_selection_audit.csv"
FIG_DIR = "results/figures"
STEM = "molecular_evidence_map"

# EN/PT: column order, strongest support first | ordem das colunas, apoio mais forte primeiro
TIERS = [
    ("experimental_in_included_study", "Experiment in\nthe study", "Experimento\nno estudo", "#1b7837"),
    ("experimental_cited_from_authors_prior_work", "Authors' earlier\nexperiment", "Experimento\nanterior (autores)", "#5aae61"),
    ("literature_cited", "Cited from\nliterature", "Citado da\nliteratura", "#2166ac"),
    ("in_silico_prediction", "Target prediction\nor enrichment", "Predicao de alvo\nou enriquecimento", "#9970ab"),
    ("clinical_correlation", "Clinical\ncorrelation", "Correlacao\nclinica", "#e08214"),
    ("paired_brain_tissue", "Paired brain\ntissue", "Tecido cerebral\npareado", "#b35806"),
    ("none_reported", "None\nreported", "Nenhuma\nrelatada", "#999999"),
    ("none_reported_abstract_only", "None\n(abstract only)", "Nenhuma\n(so resumo)", "#cccccc"),
]
TIER_INDEX = {k: i for i, (k, *_rest) in enumerate(TIERS)}


def study_key(row):
    """EN/PT: study_id is unique per study and disease (a two-disease report has two units) |
    study_id e unico por estudo e doenca (um relato de duas doencas tem duas unidades)."""
    return row["study_id"]


def load():
    rows = list(csv.DictReader(open(MAP, encoding="utf-8")))
    sel = list(csv.DictReader(open(SELECTION, encoding="utf-8")))
    pooled = {study_key(r): r for r in sel}
    mapped = {study_key(r) for r in rows}
    if mapped != set(pooled):
        sys.exit(f"EN/PT: map/pool mismatch | divergencia mapa/pool: "
                 f"only in map {sorted(mapped - set(pooled))}; only in pool {sorted(set(pooled) - mapped)}")
    bad = [r["evidence_type"] for r in rows if r["evidence_type"] not in TIER_INDEX]
    if bad:
        sys.exit(f"EN/PT: unknown evidence_type | evidence_type desconhecido: {bad}")
    return rows, pooled


GROUPS = [
    ("Amyloid and APP processing", "Amiloide e processamento da APP"),
    ("Tau, synaptic and neuronal signalling", "Tau, sinapse e sinalização neuronal"),
    ("Neuroinflammation and innate immunity", "Neuroinflamação e imunidade inata"),
    ("Cell survival, apoptosis and proteostasis", "Sobrevivência celular, apoptose e proteostase"),
    ("Alpha-synuclein biology", "Biologia da alfa-sinucleína"),
    ("Dopaminergic neuron biology and LRRK2", "Neurônio dopaminérgico e LRRK2"),
    ("Vascular and blood-brain barrier", "Vascular e barreira hematoencefálica"),
    ("Extracellular vesicle biology", "Biologia de vesículas extracelulares"),
    ("Brain-periphery relationship", "Relação cérebro-periferia"),
    ("Neuronal development and other", "Neurodesenvolvimento e outros"),
    ("Correlation with clinical or biomarker measures", "Correlação com medida clínica ou de biomarcador"),
]
GROUP_INDEX = {g: i for i, (g, _) in enumerate(GROUPS)}
# EN/PT: shape repeats the ordinal colour so that neighbouring dark steps stay distinguishable | a forma repete a cor ordinal para que passos escuros vizinhos fiquem distinguiveis
TIER_MARKER = {0: "o", 1: "o", 2: "s", 3: "^", 4: "D", 5: "p"}


def plot(rows, pooled, path, lang):
    """
    EN | Study by pathway matrix. One row per pooled study (AD then PD, highest AUC first),
         one column per pathway group; a dot marks a group in which the study offers a claim,
         coloured by the strongest kind of support it offers there (dark = an experiment in
         the study, light = a correlation or paired tissue). Studies with no claim for the
         pooled marker are shown in the last column. The bar on the left is the study's AUC,
         so the reader can look for any relation between mechanism and accuracy, and see none.
    PT | Matriz estudo por via. Uma linha por estudo agregado (DA e depois DP, maior AUC
         primeiro), uma coluna por grupo de via; um ponto marca o grupo em que o estudo faz
         uma afirmacao, colorido pelo tipo mais forte de apoio (escuro = experimento no
         estudo, claro = correlacao ou tecido pareado). Estudos sem afirmacao para o
         marcador agregado aparecem na ultima coluna. A barra a esquerda e a AUC do estudo.
    """
    import matplotlib.gridspec as gridspec
    from _viz_style import (TIER_RAMP, TIER_NONE, DISEASE, INK, INK2, INK3, BAND, RULE, PAGE, GRID, panel_letter)
    order_rows = sorted(pooled.values(), key=lambda r: (r["disease"], -float(r["selected_auc"])))
    n = len(order_rows)
    ng = len(GROUPS)
    cells = {}
    n_claims = {}
    for r in rows:
        sid = r["study_id"]
        if r["evidence_type"].startswith("none"):
            cells.setdefault((sid, "none"), 99)
            continue
        g = r["axis_group"]
        tier = TIER_INDEX[r["evidence_type"]]
        key = (sid, g)
        cells[key] = min(cells.get(key, 99), tier)
        n_claims[key] = n_claims.get(key, 0) + 1
    # a study with claims elsewhere is not "none"
    has_claim = {sid for (sid, g) in cells if g != "none"}
    fig_h = 2.3 + 0.157 * n + 1.05
    fig = plt.figure(figsize=(7.4, fig_h))
    gs = gridspec.GridSpec(2, 3, width_ratios=[1.3, 1.25, 4.9], height_ratios=[2.4, 0.157 * n * 6],
                           left=0.01, right=0.99, top=1 - 0.2 / fig_h, bottom=1.0 / fig_h, wspace=0.03, hspace=0.04)
    axl = fig.add_subplot(gs[1, 0]); axb = fig.add_subplot(gs[1, 1]); axm = fig.add_subplot(gs[1, 2])
    axt = fig.add_subplot(gs[0, 2])
    ncol = ng + 1
    for ax in (axl, axb, axm):
        ax.set_ylim(n - 0.5, -0.5)
    axl.set_xlim(0, 1); axl.axis("off")
    axb.set_xlim(0.5, 1.13)
    axm.set_xlim(-0.6, ncol - 0.4); axm.axis("off")
    prev = None
    counts_by_col = [0] * ncol
    for i, r in enumerate(order_rows):
        sid = r["study_id"]
        dis = r["disease"]
        if i % 2 == 0:
            for ax in (axl, axb, axm):
                ax.axhspan(i - 0.5, i + 0.5, color=BAND, lw=0, zorder=0)
        if dis != prev:
            if prev is not None:
                for ax in (axl, axb, axm):
                    ax.axhline(i - 0.5, color=INK3, lw=0.8, zorder=1)
            prev = dis
        axl.text(0.0, i, dis, fontsize=6.0, va="center", color=DISEASE[dis], fontweight="bold")
        axl.text(0.14, i, f"{r['first_author']} {int(float(r['year']))}", fontsize=6.4, va="center", color=INK)
        auc = float(r["selected_auc"])
        axb.plot([0.5, auc], [i, i], color=DISEASE[dis], lw=1.4, solid_capstyle="butt", zorder=2)
        axb.scatter([auc], [i], s=11, color=DISEASE[dis], zorder=3)
        axb.text(1.13, i, f"{auc:.2f}", fontsize=5.8, va="center", ha="right", color=INK2)
        for g, gi in GROUP_INDEX.items():
            tier = cells.get((sid, g))
            if tier is None:
                continue
            k = n_claims[(sid, g)]
            hollow = tier == 1
            axm.scatter([gi], [i], s=(40 if tier != 3 else 46) + 6 * min(k - 1, 4), marker=TIER_MARKER[tier],
                        facecolor=PAGE if hollow else TIER_RAMP[tier], edgecolor=TIER_RAMP[tier], linewidths=1.6 if hollow else 0, zorder=3)
            counts_by_col[gi] += 1
        if sid not in has_claim:
            axm.scatter([ng], [i], s=30, facecolor=PAGE, edgecolor=TIER_NONE, linewidths=1.3, zorder=3)
            counts_by_col[ng] += 1
    axb.spines['bottom'].set_bounds(0.5, 1.0); axb.set_yticks([]); axb.set_xticks([0.5, 0.75, 1.0]); axb.tick_params(axis="x", labelsize=6.3, length=2)
    axb.spines["left"].set_visible(False)
    axb.set_xlabel("AUC", fontsize=6.8)
    for sp in ("top", "right"):
        axb.spines[sp].set_visible(False)
    # column heads and marginal counts
    axt.set_xlim(-0.6, ncol - 0.4); axt.set_ylim(0, 12); axt.axis("off")
    import textwrap as _tw
    for gi in range(ncol):
        lab = t(lang, *GROUPS[gi]) if gi < ng else t(lang, "No mechanism reported for the pooled marker", "Nenhum mecanismo relatado para o marcador agregado")
        axt.text(gi, 6.6, "\n".join(_tw.wrap(lab, 24)), rotation=90, ha="center", va="bottom", fontsize=6.0, color=INK, linespacing=0.95)
        h = counts_by_col[gi]
        axt.add_patch(plt.Rectangle((gi - 0.2, 0.0), 0.4, 0.3 * h, color=RULE if gi == ng else INK2, lw=0, alpha=0.9))
        if h:
            axt.text(gi, 0.3 * h + 0.15, str(h), ha="center", va="bottom", fontsize=5.8, color=INK2)
    axt.text(-0.75, 0.15, t(lang, "Studies per pathway", "Estudos por via"), fontsize=5.8, color=INK3, va="bottom", ha="right")
    # legend: strength of support
    names = [(t(lang, "Experiment in the study", "Experimento no estudo")), t(lang, "Authors' earlier experiment", "Experimento anterior dos autores"),
             t(lang, "Cited from literature", "Citado da literatura"), t(lang, "Target prediction", "Predição de alvo"),
             t(lang, "Clinical correlation", "Correlação clínica"), t(lang, "Paired brain tissue", "Tecido cerebral pareado")]
    handles = [plt.Line2D([], [], marker=TIER_MARKER[i], ls="none", ms=6, mfc=PAGE if i == 1 else c, mec=c, mew=1.6 if i == 1 else 0) for i, c in enumerate(TIER_RAMP)]
    handles.append(plt.Line2D([], [], marker="o", ls="none", ms=6, mfc=PAGE, mec=TIER_NONE, mew=1.3))
    names.append(t(lang, "None reported", "Nenhuma relatada"))
    fig.legend(handles, names, loc="lower left", bbox_to_anchor=(0.01, 0.0), ncol=4, frameon=False, fontsize=6.3,
               handletextpad=0.2, columnspacing=1.0, title=t(lang, "Strongest support offered (dark to light)", "Apoio mais forte oferecido (escuro a claro)"),
               title_fontsize=6.3, alignment="left")
    fig.savefig(path, dpi=600, bbox_inches="tight")
    plt.close(fig)


def main():
    for p in (MAP, SELECTION):
        if not os.path.exists(p):
            sys.exit(f"EN/PT: missing | ausente: {p}")
    rows, pooled = load()
    os.makedirs(FIG_DIR, exist_ok=True)
    for lang in LANGS:
        plot(rows, pooled, fig_path(FIG_DIR, STEM, lang), lang)
    counts = {}
    for k, *_ in TIERS:
        counts[k] = len({study_key(r) for r in rows if r["evidence_type"] == k})
    print("EN/PT | Molecular evidence map | Mapa de evidencia molecular")
    print(f"  pooled studies mapped | estudos agregados mapeados: {len(pooled)}")
    for k, v in counts.items():
        print(f"  studies with {k}: {v}")
    for lang in LANGS:
        print(f"EN/PT -> {fig_path(FIG_DIR, STEM, lang)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
