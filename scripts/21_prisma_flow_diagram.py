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
    ident = flow["identification"]
    scr = flow["screening"]
    elig = flow["eligibility_fulltext"]
    pool = flow["included_in_meta_analysis"]

    fig, ax = plt.subplots(figsize=(10.2, 12.6))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 100)
    ax.axis("off")

    col_l, col_r, w_main, w_side, h = 0.6, 6.2, 5.4, 3.2, 8.4

    # EN/PT: Identification
    box(ax, (col_l, 88), w_main, h, tr(lang,
        f"Records identified through database searching (n = {ident['total_unique_records']})\n"
        f"PubMed/MEDLINE (n = {ident['pubmed_records_after_deduplication']})\n"
        f"Scopus, new (n = {ident['scopus_records_new']}) · "
        f"Web of Science, new (n = {ident['wos_records_new_total']})",
        f"Registros identificados na busca em bases de dados (n = {ident['total_unique_records']})\n"
        f"PubMed/MEDLINE (n = {ident['pubmed_records_after_deduplication']})\n"
        f"Scopus, novos (n = {ident['scopus_records_new']}) · "
        f"Web of Science, novos (n = {ident['wos_records_new_total']})"),
        HUE_ID, fontsize=7.9)

    # EN/PT: Screening
    y_screen = 74
    box(ax, (col_l, y_screen), w_main, h, tr(lang,
        f"Records screened (n = {scr['pubmed_records_screened'] + scr['scopus_new_records_screened_total'] + scr['wos_new_records_screened_total']})",
        f"Registros triados (n = {scr['pubmed_records_screened'] + scr['scopus_new_records_screened_total'] + scr['wos_new_records_screened_total']})"),
        HUE_SCREEN)
    n_secondary = (scr["pubmed_excluded_review_or_secondary"] + scr["scopus_excluded_review_or_secondary_total"]
                   + scr["wos_excluded_review_or_secondary_total"])
    box(ax, (col_r, y_screen + 1.6), w_side, h - 3.2, tr(lang,
        f"Excluded as secondary literature\n(review, meta-analysis, editorial)\n(n = {n_secondary})",
        f"Excluidos como literatura secundaria\n(revisao, meta-analise, editorial)\n(n = {n_secondary})"),
        HUE_EXC, fontsize=7.8)

    # EN/PT: primary studies with extractable measure
    y_primary = 60
    n_primary = scr["pubmed_primary_studies"] + scr["scopus_primary_studies_total"] + scr["wos_primary_studies_total"]
    n_extractable = (scr["pubmed_primary_reporting_auc_or_sens_spec"] + scr["scopus_primary_reporting_auc_or_sens_spec_total"]
                      + scr["wos_primary_reporting_auc_or_sens_spec_total"])
    box(ax, (col_l, y_primary), w_main, h, tr(lang,
        f"Primary studies (n = {n_primary})\nreporting an accuracy measure in title/abstract (n = {n_extractable})",
        f"Estudos primários (n = {n_primary})\nreportando medida de acurácia no título/resumo (n = {n_extractable})"),
        HUE_SCREEN)

    # EN/PT: recall check of the records without an accuracy statement in the abstract
    rc = elig["recall_check"]
    n_abs_arm = elig["fulltext_retrieved"] - rc["fulltext_read"]
    box(ax, (col_r, 55.5), w_side, 13.5, tr(lang,
        f"Recall check of records with no\naccuracy statement in the abstract\n(n = {rc['records_without_accuracy_statement_in_abstract']})\n"
        f"Plausible on title/abstract (n = {rc['judged_plausible_by_title_and_abstract']})\n"
        f"No open full text, not assessed (n = {rc['no_open_fulltext']})\n"
        f"Full text not retrievable (n = {rc['fulltext_not_retrievable']})\n"
        f"Full texts read (n = {rc['fulltext_read']})",
        f"Verificação de recall dos registros sem\nafirmação de acurácia no resumo\n(n = {rc['records_without_accuracy_statement_in_abstract']})\n"
        f"Plausíveis por título/resumo (n = {rc['judged_plausible_by_title_and_abstract']})\n"
        f"Sem texto completo aberto, não avaliados (n = {rc['no_open_fulltext']})\n"
        f"Texto completo não recuperável (n = {rc['fulltext_not_retrievable']})\n"
        f"Textos completos lidos (n = {rc['fulltext_read']})"),
        HUE_SCREEN, fontsize=6.9)
    arrow(ax, (col_l + w_main, y_primary + h / 2), (col_r, y_primary + h / 2))
    ax.add_patch(FancyArrowPatch((col_r, 56.7), (col_l + w_main / 2, 56.7), arrowstyle="-|>",
                                  mutation_scale=11, linewidth=1.2, color="#6b6a66",
                                  shrinkA=0, shrinkB=0))

    # EN/PT: Eligibility
    y_elig = 46
    box(ax, (col_l, y_elig), w_main, h, tr(lang,
        f"Full texts retrieved and assessed for eligibility (n = {elig['fulltext_retrieved']})\n"
        f"{n_abs_arm} from the abstract-based arm, {rc['fulltext_read']} from the recall check\n"
        f"{elig['studies_contributing_extracted_estimates']} studies contributed "
        f"{elig['extracted_estimates_total']} extracted estimates",
        f"Textos completos obtidos e avaliados quanto à elegibilidade (n = {elig['fulltext_retrieved']})\n"
        f"{n_abs_arm} do braço de acurácia no resumo, {rc['fulltext_read']} da verificação de recall\n"
        f"{elig['studies_contributing_extracted_estimates']} estudos contribuíram "
        f"{elig['extracted_estimates_total']} estimativas extraídas"),
        HUE_ELIG, fontsize=8.0)
    n_ineligible = elig["extracted_estimates_total"] - elig["estimates_eligible_for_primary_pool"]
    box(ax, (col_r, y_elig + 1.6), w_side, h - 3.2, tr(lang,
        f"Estimates excluded from\nprimary pool, reason recorded\n(n = {n_ineligible})",
        f"Estimativas excluídas do\npool primário, motivo registrado\n(n = {n_ineligible})"),
        HUE_EXC, fontsize=7.8)

    # EN/PT: Included / eligible
    y_inc = 32
    n_elig_studies = n_studies_eligible()
    box(ax, (col_l, y_inc), w_main, h, tr(lang,
        f"Estimates eligible for the primary pool (n = {elig['estimates_eligible_for_primary_pool']})\n"
        f"case-vs-healthy-control design, {n_elig_studies} independent studies",
        f"Estimativas elegíveis para o pool primário (n = {elig['estimates_eligible_for_primary_pool']})\n"
        f"desenho caso-versus-controle saudável, {n_elig_studies} estudos independentes"),
        HUE_INC)

    # EN/PT: pooled (circulating, primary) vs held out (no computable SE, or CSF)
    y_pool = 18
    n_csf = pool.get("csf_estimates_secondary_not_pooled", 0)
    n_not_estimable = (elig["estimates_eligible_for_primary_pool"]
                        - pool["estimates_with_estimable_standard_error"] - n_csf)
    box(ax, (col_l, y_pool), w_main, h, tr(lang,
        f"Circulating estimates with a computable standard error,\nincluded in the PRIMARY pooled meta-analysis (n = {pool['estimates_with_estimable_standard_error']})\n"
        f"from {pool['independent_studies']} independent studies",
        f"Estimativas circulantes com erro-padrão computável,\nincluidas na meta-análise agregada PRIMÁRIA (n = {pool['estimates_with_estimable_standard_error']})\n"
        f"de {pool['independent_studies']} estudos independentes"),
        HUE_INC)
    box(ax, (col_r, y_pool - 1.5), w_side, h + 3.0, tr(lang,
        f"No computable standard error: no CI and\nno usable group sizes (n = {n_not_estimable})\n\n"
        f"Cerebrospinal fluid, SE computable\nbut not a circulating biofluid:\nreported separately, not pooled (n = {n_csf})",
        f"Sem erro-padrão computável: sem IC e\nsem tamanhos de grupo utilizáveis (n = {n_not_estimable})\n\n"
        f"Líquido cefalorraquidiano, EP computável\nmas não é biofluido circulante:\nreportado à parte, não agregado (n = {n_csf})"),
        HUE_EXC, fontsize=7.2)

    for (y0, y1) in [(88, y_screen + h), (y_screen, y_primary + h), (y_primary, y_elig + h),
                     (y_elig, y_inc + h), (y_inc, y_pool + h)]:
        arrow(ax, (col_l + w_main / 2, y0), (col_l + w_main / 2, y1))
    for y0 in [y_screen, y_elig, y_pool]:
        arrow(ax, (col_l + w_main, y0 + (h - 3.2) / 2 + 1.6), (col_r, y0 + (h - 3.2) / 2 + 1.6))

    stage_labels = [(96.5, "Identification | Identificação"),
                    (79.5, "Screening | Triagem"),
                    (51.5, "Eligibility | Elegibilidade"),
                    (23.5, "Included | Incluídos")]
    for y, lab in stage_labels:
        en, pt = lab.split(" | ")
        ax.text(0.05, y, tr(lang, en, pt), fontsize=9.5, weight="bold", color="#4a4a48",
                rotation=90, va="center", ha="center")

    # Title omitted: the caption in the manuscript names the figure.
    fig.savefig(path, dpi=600, facecolor="white", bbox_inches="tight")
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
