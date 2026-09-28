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


LINE = 0.2       # EN/PT: row height per text line, in axis units | altura de linha de texto, em unidades do eixo
MAX_LINES = 7    # EN/PT: lines shown per cell before "+N" | linhas por celula antes de "+N"
WRAP = 23        # EN/PT: characters per line inside a cell | caracteres por linha dentro da celula


def cell_text(cs):
    """EN/PT: one paragraph per claim, wrapped whole; never cut in the middle of a claim |
    um paragrafo por afirmacao, quebrado inteiro; nunca cortado no meio de uma afirmacao."""
    if cs[0]["evidence_type"] in ("none_reported", "none_reported_abstract_only"):
        return ["-"]
    lines, shown = [], 0
    for c in cs:
        # EN/PT: a claim with no named target falls back on its biological axis | afirmacao sem alvo nomeado usa o eixo biologico
        target = c["target_or_pathway"].strip() or c["biological_axis"].strip()
        claim = textwrap.shorten(f"{c['mirna']} -> {target}", 75, placeholder="...")
        wrapped = textwrap.wrap(claim, WRAP)
        if lines and len(lines) + len(wrapped) > MAX_LINES:
            lines.append(f"+{len(cs) - shown} more")
            return lines
        lines += wrapped
        shown += 1
    return lines


def plot(rows, pooled, path, lang):
    order = sorted(pooled.values(), key=lambda r: (r["disease"], -float(r["selected_auc"])))
    keys = [study_key(r) for r in order]
    n = len(keys)
    cells, heights = [], []
    for k in keys:
        by_tier = {}
        for c in rows:
            if study_key(c) == k:
                by_tier.setdefault(TIER_INDEX[c["evidence_type"]], []).append(c)
        row_cells = {j: cell_text(cs) for j, cs in by_tier.items()}
        cells.append(row_cells)
        heights.append(max(0.55, LINE * max(len(v) for v in row_cells.values()) + 0.25))
    tops = [sum(heights[:i]) for i in range(n)]
    total = sum(heights)
    x0 = -4.6
    fig, ax = plt.subplots(figsize=(19, 0.6 * total + 1.8))
    ax.set_xlim(x0, len(TIERS) - 0.5)
    ax.set_ylim(total, -1.3)
    ax.axis("off")

    for j, (_k, en, pt, col) in enumerate(TIERS):
        ax.text(j, -0.8, t(lang, en, pt), ha="center", va="center", fontsize=8.5,
                fontweight="bold", color=col)
    ax.text(x0 + 0.05, -0.8, t(lang, "Pooled study, selected marker (AUC)",
                               "Estudo agregado, marcador selecionado (AUC)"),
            ha="left", va="center", fontsize=9, fontweight="bold")

    prev = None
    for i, r in enumerate(order):
        y0, h = tops[i], heights[i]
        yc = y0 + h / 2
        if r["disease"] != prev:
            if prev is not None:
                ax.axhline(y0, color="black", lw=0.8)
            prev = r["disease"]
        if i % 2 == 0:
            ax.axhspan(y0, y0 + h, color="#f4f4f4", zorder=0)
        label = f"{r['disease']}  {r['first_author']} {int(float(r['year']))}: " \
                f"{textwrap.shorten(r['selected_marker'], 30, placeholder='...')} ({float(r['selected_auc']):.2f})"
        ax.text(x0 + 0.05, yc, "\n".join(textwrap.wrap(label, 46)), ha="left", va="center", fontsize=8.5)
        for j, lines in cells[i].items():
            ax.scatter([j - 0.42], [yc], s=38, color=TIERS[j][3], zorder=3)
            ax.text(j - 0.34, yc, "\n".join(lines), ha="left", va="center", fontsize=6.6,
                    color="black", linespacing=1.15)
    # EN/PT: no in-figure title; the caption lives in the manuscript text (journal rule)
    # sem titulo na figura; a legenda fica no texto do manuscrito (regra da revista)
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
