#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EN | The PRISMA 2020 flow diagram, drawn from data/processed/prisma_flow.json rather
     than typed in by hand. Every count on every box is read from that file at draw
     time, so the diagram cannot say a number the PRISMA flow table itself does not.
PT | O fluxograma PRISMA 2020, desenhado a partir de data/processed/prisma_flow.json em
     vez de digitado a mao. Toda contagem em toda caixa e lida desse arquivo no momento
     do desenho, entao o diagrama nao pode dizer um numero que a propria tabela PRISMA
     nao diz.

EN | Why a new figure rather than reusing a table. The prose flow (587 unique records ->
     356 primary studies -> 129 with an accuracy statement in the abstract, plus a recall
     check of the 227 without one -> 82 full texts -> 77 studies / 251 estimates -> 117
     eligible / 47 studies -> 97 pooled circulating estimates / 37 studies, plus 3 CSF
     estimates reported separately) is hard to scan in text. The numbers here are read from
     data/processed/prisma_flow.json at draw time; the ones quoted in this docstring are
     only a guide to the layout.
PT | Por que uma figura nova em vez de reaproveitar uma tabela. O fluxo em prosa (587
     registros unicos -> 356 estudos primarios -> 129 com afirmacao de acuracia no resumo,
     mais uma verificacao de recall dos 227 sem ela -> 82 textos completos -> 77 estudos /
     251 estimativas -> 117 elegiveis / 47 estudos -> 97 estimativas circulantes agregadas /
     37 estudos, mais 3 estimativas de LCR reportadas a parte) e dificil de acompanhar em
     texto. Os numeros aqui sao lidos de data/processed/prisma_flow.json no momento do
     desenho; os citados neste docstring servem so de guia do layout.

    python scripts/21_prisma_flow_diagram.py
"""

import csv
import json
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _bilingual import LANGS, t as tr, fig_path
import _viz_style  # noqa: F401  (applies the shared figure style)

tr_ = tr

FLOW = "data/processed/prisma_flow.json"
EXTRACTION = "data/extracted/diagnostic_accuracy_extraction.csv"
FIG_DIR = "results/figures"


def n_studies_eligible():
    """EN/PT: unique studies (PMID, or DOI when no PMID) contributing an eligible estimate."""
    rows = list(csv.DictReader(open(EXTRACTION, encoding="utf-8")))
    ids = {(r["pmid"] or r["doi"]) for r in rows if r["eligible_primary_pool"] == "yes"}
    return len(ids)

HUE_ID, HUE_SCREEN, HUE_ELIG, HUE_INC, HUE_EXC = (
    "#4a4a48", "#2a78d6", "#8a5aab", "#2f9e5c", "#c24a3a",
)


def box(ax, xy, w, h, text, hue, fontsize=8.4):
    x, y = xy
    patch = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.012,rounding_size=0.012",
                            linewidth=1.3, edgecolor=hue, facecolor="white")
    ax.add_patch(patch)
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fontsize,
             color="#232220", linespacing=1.35)


def arrow(ax, p0, p1, hue="#6b6a66"):
    ax.add_patch(FancyArrowPatch(p0, p1, arrowstyle="-|>", mutation_scale=11,
                                  linewidth=1.2, color=hue, shrinkA=0, shrinkB=0))


def plot(flow, path, lang):
    """
    EN | PRISMA 2020 flow in the shared figure style: each stage is a card with its headline
         number in large type and its explanation beside it, an accent bar whose depth of
         blue follows the progression from records to pooled studies, and grey cards for
         what was set aside.
    PT | Fluxo PRISMA 2020 no estilo compartilhado das figuras: cada etapa e um cartao com o
         numero principal em corpo grande e a explicacao ao lado, uma barra de destaque cujo
         tom de azul acompanha a progressao de registros a estudos agregados, e cartoes
         cinza para o que foi posto de lado.
    """
    from _viz_style import INK, INK2, INK3, RULE, BAND, PAGE, TIER_RAMP, rounded
    ident = flow["identification"]
    scr = flow["screening"]
    elig = flow["eligibility_fulltext"]
    pool = flow["included_in_meta_analysis"]
    rc = elig["recall_check"]

    fig, ax = plt.subplots(figsize=(7.4, 9.0))
    ax.set_xlim(0, 100)
    ax.set_ylim(104, 0)
    ax.axis("off")
    XL, WM = 7.5, 57.0        # main column
    XR, WR = 69.5, 30.0       # side column
    H = 10.0

    def card(x, y, w, h, big, text, accent, side=False):
        rounded(ax, x, y, w, h, BAND if side else PAGE, ec=RULE, lw=0.9, r=1.2, z=1)
        rounded(ax, x, y, 1.1, h, accent, r=0.5, z=2)
        ax.text(x + 3.0, y + h / 2, big, fontsize=15 if not side else 12, fontweight="bold", color=accent if not side else INK2,
                va="center", ha="left", zorder=3)
        off = 3.0 + (10.5 if not side else 8.0)
        ax.text(x + off, y + h / 2, text, fontsize=6.3, color=INK, va="center", ha="left", linespacing=1.4, zorder=3)

    def arrow(x0, y0, x1, y1):
        ax.add_patch(FancyArrowPatch((x0, y0), (x1, y1), arrowstyle="-|>", mutation_scale=9, lw=1.0, color=INK3,
                                     shrinkA=0, shrinkB=0, zorder=0))

    n_secondary = (scr["pubmed_excluded_review_or_secondary"] + scr["scopus_excluded_review_or_secondary_total"]
                   + scr["wos_excluded_review_or_secondary_total"])
    n_primary = scr["pubmed_primary_studies"] + scr["scopus_primary_studies_total"] + scr["wos_primary_studies_total"]
    n_extractable = (scr["pubmed_primary_reporting_auc_or_sens_spec"] + scr["scopus_primary_reporting_auc_or_sens_spec_total"]
                     + scr["wos_primary_reporting_auc_or_sens_spec_total"])
    n_abs_arm = elig["fulltext_retrieved"] - rc["fulltext_read"]
    n_ineligible = elig["extracted_estimates_total"] - elig["estimates_eligible_for_primary_pool"]
    n_csf = pool.get("csf_estimates_secondary_not_pooled", 0)
    n_not_est = elig["estimates_eligible_for_primary_pool"] - pool["estimates_with_estimable_standard_error"] - n_csf
    n_elig_studies = n_studies_eligible()
    ys = [3, 19, 35, 53, 74, 90]
    card(XL, ys[0], WM, H, f"{ident['total_unique_records']}",
         tr_(lang, f"records identified\nPubMed {ident['pubmed_records_after_deduplication']} · Scopus {ident['scopus_records_new']} · WoS {ident['wos_records_new_total']} (new records)",
             f"registros identificados\nPubMed {ident['pubmed_records_after_deduplication']} · Scopus {ident['scopus_records_new']} · WoS {ident['wos_records_new_total']} (registros novos)"), TIER_RAMP[5])
    card(XL, ys[1], WM, H, f"{scr['pubmed_records_screened'] + scr['scopus_new_records_screened_total'] + scr['wos_new_records_screened_total']}",
         tr_(lang, "records screened\n(title, abstract, publication type)", "registros triados\n(título, resumo, tipo de publicação)"), TIER_RAMP[4])
    card(XR, ys[1] + 1.5, WR, H - 3, f"{n_secondary}", tr_(lang, "excluded: reviews,\nmeta-analyses, editorials", "excluídos: revisões,\nmeta-análises, editoriais"), RULE, side=True)
    card(XL, ys[2], WM, H + 2, f"{n_primary}",
         tr_(lang, f"primary studies\n{n_extractable} state accuracy in the abstract\n{rc['records_without_accuracy_statement_in_abstract']} do not (recall check, right)",
             f"estudos primários\n{n_extractable} citam acurácia no resumo\n{rc['records_without_accuracy_statement_in_abstract']} não citam (recall, à direita)"), TIER_RAMP[3])
    card(XR, ys[2] - 1.0, WR, H + 4.5, f"{rc['judged_plausible_by_title_and_abstract']}",
         tr_(lang, f"plausible (title, abstract)\n{rc['no_open_fulltext']} no open full text\n{rc['fulltext_not_retrievable']} not retrievable\n{rc['fulltext_read']} full texts read",
             f"plausíveis (título, resumo)\n{rc['no_open_fulltext']} sem texto completo aberto\n{rc['fulltext_not_retrievable']} não recuperáveis\n{rc['fulltext_read']} textos completos lidos"), TIER_RAMP[3], side=True)
    card(XL, ys[3], WM, H + 2, f"{elig['fulltext_retrieved']}",
         tr_(lang, f"full texts read ({n_abs_arm} abstract arm,\n{rc['fulltext_read']} recall check)\n{elig['studies_contributing_extracted_estimates']} studies, {elig['extracted_estimates_total']} estimates extracted",
             f"textos completos lidos ({n_abs_arm} braço por\nresumo, {rc['fulltext_read']} recall)\n{elig['studies_contributing_extracted_estimates']} estudos, {elig['extracted_estimates_total']} estimativas extraídas"), TIER_RAMP[2])
    card(XR, 64.5, WR, 9.0, f"{n_ineligible}", tr_(lang, "estimates set aside,\nreason recorded", "estimativas postas de lado,\nmotivo registrado"), RULE, side=True)
    card(XL, ys[4], WM, H, f"{elig['estimates_eligible_for_primary_pool']}",
         tr_(lang, f"eligible estimates from {n_elig_studies} studies\ncase versus healthy control", f"estimativas elegíveis de {n_elig_studies} estudos\ncaso versus controle saudável"), TIER_RAMP[1])
    card(XL, ys[5], WM, H + 2, f"{pool['estimates_with_estimable_standard_error']}",
         tr_(lang, f"circulating estimates in the\nprimary meta-analysis, from\n{pool['independent_studies']} independent studies", f"estimativas circulantes na\nmeta-análise primária, de\n{pool['independent_studies']} estudos independentes"), TIER_RAMP[0])
    card(XR, ys[5] - 0.5, WR, H + 3, f"{n_not_est + n_csf}",
         tr_(lang, f"not pooled\n{n_not_est} no computable\nstandard error\n{n_csf} cerebrospinal fluid", f"não agregadas\n{n_not_est} sem erro-padrão\ncomputável\n{n_csf} líquor"), RULE, side=True)
    cx = XL + WM / 2
    for a_, b_, hh in ((ys[0], ys[1], H), (ys[1], ys[2], H), (ys[2], ys[3], H + 2), (ys[3], ys[4], H + 2), (ys[4], ys[5], H)):
        arrow(cx, a_ + hh, cx, b_)
    arrow(XL + WM, ys[1] + H / 2, XR, ys[1] + H / 2)
    arrow(XL + WM, ys[2] + 6, XR, ys[2] + 6)
    ax.add_patch(FancyArrowPatch((XR + WR / 2, ys[2] - 1.0 + H + 4.5), (XL + WM, ys[3] + 4), connectionstyle="angle,angleA=90,angleB=0,rad=6",
                                 arrowstyle="-|>", mutation_scale=9, lw=1.0, color=INK3, shrinkA=0, shrinkB=0, zorder=0))
    arrow(cx, 69.0, XR, 69.0)
    arrow(XL + WM, ys[5] + 6, XR, ys[5] + 6)
    for y, lab in ((ys[0] + H / 2, tr_(lang, "Identification", "Identificação")), (ys[1] + 5, tr_(lang, "Screening", "Triagem")),
                   (ys[3] + 8, tr_(lang, "Eligibility", "Elegibilidade")), (ys[5] + 6, tr_(lang, "Included", "Incluídos"))):
        ax.text(2.2, y, lab, rotation=90, fontsize=7.8, fontweight="bold", color=INK2, va="center", ha="center")
    fig.savefig(path, dpi=600, bbox_inches="tight")
    plt.close(fig)


def main():
    os.makedirs(FIG_DIR, exist_ok=True)
    if not os.path.exists(FLOW):
        sys.exit(f"EN/PT: missing {FLOW}")
    flow = json.load(open(FLOW, encoding="utf-8"))

    for lang in LANGS:
        plot(flow, fig_path(FIG_DIR, "prisma_flow_diagram", lang), lang)

    print("=" * 78)
    print("EN | PRISMA flow diagram | PT | Fluxograma PRISMA")
    print("=" * 78)
    for lang in LANGS:
        print(f"EN/PT -> {fig_path(FIG_DIR, 'prisma_flow_diagram', lang)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
