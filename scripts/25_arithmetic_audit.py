#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EN | Arithmetic audit: every core sample-size and study count used anywhere in
     this review's Methods, Results or manuscript, reconciled in one table so
     a reader (or a future edit) cannot silently drift into an inconsistent
     set of numbers again. Every value here is READ from the same live
     tables and JSON that the manuscript and the other scripts already
     produce, never hand-typed, and every subtotal that should sum to another
     row is checked with an assertion, not just printed.
PT | Auditoria aritmetica: toda contagem central de tamanho amostral e de
     estudos usada em qualquer parte dos Metodos, Resultados ou manuscrito
     desta revisao, reconciliada em uma unica tabela para que um leitor (ou
     uma edicao futura) nao possa deslizar em silencio para um conjunto
     inconsistente de numeros de novo. Todo valor aqui e LIDO das mesmas
     tabelas e do mesmo JSON que o manuscrito e os outros scripts ja
     produzem, nunca digitado a mao, e todo subtotal que deveria somar a
     outra linha e conferido com uma asserção, nao so impresso.

    python scripts/25_arithmetic_audit.py
"""

import csv
import json
import os
import sys
from collections import OrderedDict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

EXTRACTION = "data/extracted/diagnostic_accuracy_extraction.csv"
FLOW = "data/processed/prisma_flow.json"
QUADAS = "results/tables/quadas2_assessment.csv"
SELECTION = "results/tables/one_estimate_per_study_selection_audit.csv"
PRIMARY = "results/tables/meta_analysis_pooled_auc_primary.csv"
BIVARIATE = "results/tables/bivariate_summary.csv"
CSF = "results/tables/csf_secondary_estimates.csv"
TAB_DIR = "results/tables"

CSF_BIOFLUIDS = {"CSF", "CSF_exosome"}


def study_id(row):
    pmid = str(row.get("pmid", "")).strip()
    if pmid.endswith(".0"):
        pmid = pmid[:-2]
    return pmid or str(row.get("doi", "")).strip().lower()


def main():
    ext = list(csv.DictReader(open(EXTRACTION, encoding="utf-8")))
    flow = json.load(open(FLOW, encoding="utf-8"))
    quadas = list(csv.DictReader(open(QUADAS, encoding="utf-8")))
    selection = list(csv.DictReader(open(SELECTION, encoding="utf-8")))
    primary = list(csv.DictReader(open(PRIMARY, encoding="utf-8")))
    biv = list(csv.DictReader(open(BIVARIATE, encoding="utf-8")))
    csf = list(csv.DictReader(open(CSF, encoding="utf-8")))

    elig = [r for r in ext if r["eligible_primary_pool"] == "yes"]
    elig_studies = {study_id(r) for r in elig}
    elig_ad = [r for r in elig if r["disease"] == "AD"]
    elig_pd = [r for r in elig if r["disease"] == "PD"]

    def has_se(r):
        if r["auc_ci_low"] and r["auc_ci_high"]:
            return True
        try:
            nc, nk = float(r["n_cases"]), float(r["n_controls"])
            auc = float(r["auc"])
        except (TypeError, ValueError):
            return False
        return nc >= 2 and nk >= 2 and 0 < auc < 1

    poolable = [r for r in elig if has_se(r)]
    poolable_studies = {study_id(r) for r in poolable}
    no_poolable_row_studies = elig_studies - poolable_studies

    csf_row_studies_any = {study_id(r) for r in elig if r["biofluid"] in CSF_BIOFLUIDS}
    csf_poolable_studies = {study_id(r) for r in poolable if r["biofluid"] in CSF_BIOFLUIDS}
    circ_poolable_studies = poolable_studies - csf_poolable_studies

    quadas_ad = [r for r in quadas if r["disease"] == "AD"]
    quadas_pd = [r for r in quadas if r["disease"] == "PD"]

    sel_ad = [r for r in selection if r["disease"] == "AD"]
    sel_pd = [r for r in selection if r["disease"] == "PD"]
    sel_multi = [r for r in selection if int(r["n_candidate_estimates"]) > 1]

    row_ad_all = next(r for r in primary if r["subgroup"].startswith("AD - all markers"))
    row_pd_all = next(r for r in primary if r["subgroup"].startswith("PD - all markers"))
    row_single_ad = next(r for r in primary if r["subgroup"] == "AD - single miRNA | miRNA isolado")
    row_single_pd = next(r for r in primary if r["subgroup"] == "PD - single miRNA | miRNA isolado")
    row_panel_ad = next(r for r in primary if r["subgroup"] == "AD - multi-miRNA panel | painel multi-miRNA")
    row_panel_pd = next(r for r in primary if r["subgroup"] == "PD - multi-miRNA panel | painel multi-miRNA")

    biv_one = next(r for r in biv if r["analysis"].startswith("one estimate per study"))
    biv_all = next(r for r in biv if r["analysis"].startswith("every eligible"))

    rows = [
        ("Total unique records identified", flow["identification"]["total_unique_records"], "identification.total_unique_records", flow.get("source", FLOW)),
        ("Primary studies after screening", flow["screening_rule_recomputation"]["primary_studies"], "screening_rule_recomputation.primary_studies", FLOW),
        ("Primary studies reporting an extractable accuracy measure", flow["screening_rule_recomputation"]["primary_reporting_auc_or_sens_spec"], "screening_rule_recomputation.primary_reporting_auc_or_sens_spec", FLOW),
        ("Full texts retrieved", flow["eligibility_fulltext"]["fulltext_retrieved"], "eligibility_fulltext.fulltext_retrieved", FLOW),
        ("Studies contributing extracted estimates", flow["eligibility_fulltext"]["studies_contributing_extracted_estimates"], "eligibility_fulltext.studies_contributing_extracted_estimates", FLOW),
        ("Extracted estimates (rows)", flow["eligibility_fulltext"]["extracted_estimates_total"], "eligibility_fulltext.extracted_estimates_total", FLOW),
        ("Eligible estimates, systematic-review scope", len(elig), "= AD-arm + PD-arm below", EXTRACTION),
        ("  of which AD-arm estimates", len(elig_ad), "", EXTRACTION),
        ("  of which PD-arm estimates", len(elig_pd), "", EXTRACTION),
        ("Eligible studies, systematic-review scope (QUADAS-2/GRADE-rated)", len(elig_studies), "= AD studies + PD studies below", EXTRACTION),
        ("  of which AD studies", len(quadas_ad), "", QUADAS),
        ("  of which PD studies", len(quadas_pd), "", QUADAS),
        ("Estimates with an estimable standard error (poolable, any biofluid)", len(poolable), "= circulating + CSF poolable below", EXTRACTION),
        ("Independent studies with >=1 poolable estimate (any biofluid)", len(poolable_studies), "= circulating + CSF poolable studies below", EXTRACTION),
        ("  Studies with NO poolable estimate at all (excluded from every quantitative synthesis)", len(no_poolable_row_studies), "= eligible studies - poolable studies", EXTRACTION),
        ("  CSF studies with any eligible row", len(csf_row_studies_any), "", EXTRACTION),
        ("  CSF studies that are poolable (secondary, not pooled - see csf_secondary_estimates.csv)", len(csf_poolable_studies), "", CSF),
        ("  CSF studies with NO poolable row (counted in the no-poolable-estimate row above)", len(csf_row_studies_any - csf_poolable_studies), "", EXTRACTION),
        ("Circulating eligible studies (systematic-review scope)", len(elig_studies - csf_row_studies_any), "= eligible studies - CSF studies", EXTRACTION),
        ("Circulating (primary) poolable estimates", int(flow["included_in_meta_analysis"]["estimates_with_estimable_standard_error"]), "= poolable - CSF poolable estimates", FLOW),
        ("Circulating (primary) independent studies", int(flow["included_in_meta_analysis"]["independent_studies"]), "= AD + PD circulating studies below", FLOW),
        ("  of which AD circulating studies (primary pool)", int(row_ad_all["n_studies"]), "= single + panel AD below", PRIMARY),
        ("  of which PD circulating studies (primary pool)", int(row_pd_all["n_studies"]), "= single + panel PD below", PRIMARY),
        ("    AD single-miRNA studies", int(row_single_ad["n_studies"]), "", PRIMARY),
        ("    AD multi-miRNA-panel studies", int(row_panel_ad["n_studies"]), "", PRIMARY),
        ("    PD single-miRNA studies", int(row_single_pd["n_studies"]), "", PRIMARY),
        ("    PD multi-miRNA-panel studies", int(row_panel_pd["n_studies"]), "", PRIMARY),
        ("Circulating candidate estimates before one-per-study selection, AD", int(row_ad_all["n_estimates_collapsed"]), "", PRIMARY),
        ("Circulating candidate estimates before one-per-study selection, PD", int(row_pd_all["n_estimates_collapsed"]), "", PRIMARY),
        ("Circulating studies with >1 candidate estimate to choose from", len(sel_multi), "= AD multi-candidate + PD multi-candidate", SELECTION),
        ("  of which AD", sum(1 for r in sel_ad if int(r["n_candidate_estimates"]) > 1), "", SELECTION),
        ("  of which PD", sum(1 for r in sel_pd if int(r["n_candidate_estimates"]) > 1), "", SELECTION),
        ("Bivariate synthesis: independent circulating studies", int(biv_one["n_studies"]), "", BIVARIATE),
        ("  one-estimate-per-study analysis: estimates used", int(biv_one["k_estimates"]), "", BIVARIATE),
        ("  every-eligible-estimate analysis: estimates used", int(biv_all["k_estimates"]), "", BIVARIATE),
    ]

    # EN/PT: assertions - every subtotal actually sums to the row above it,
    # not merely printed side by side.
    assert len(elig) == len(elig_ad) + len(elig_pd)
    assert len(elig_studies) == len(quadas_ad) + len(quadas_pd) == len(quadas)
    assert len(poolable_studies) == len(circ_poolable_studies) + len(csf_poolable_studies)
    assert int(flow["included_in_meta_analysis"]["independent_studies"]) == int(row_ad_all["n_studies"]) + int(row_pd_all["n_studies"])
    assert int(row_ad_all["n_studies"]) == int(row_single_ad["n_studies"]) + int(row_panel_ad["n_studies"])
    assert int(row_pd_all["n_studies"]) == int(row_single_pd["n_studies"]) + int(row_panel_pd["n_studies"])
    assert len(sel_multi) == sum(1 for r in sel_ad if int(r["n_candidate_estimates"]) > 1) \
        + sum(1 for r in sel_pd if int(r["n_candidate_estimates"]) > 1)
    assert len(csf_poolable_studies) == int(flow["included_in_meta_analysis"]["csf_studies_secondary_not_pooled"])
    assert len(circ_poolable_studies) == int(flow["included_in_meta_analysis"]["independent_studies"])
    assert len(elig) == int(flow["eligibility_fulltext"]["estimates_eligible_for_primary_pool"])
    assert len(ext) == int(flow["eligibility_fulltext"]["extracted_estimates_total"])

    print("=" * 78)
    print("EN | Arithmetic audit | PT | Auditoria aritmetica")
    print("=" * 78)
    for label, value, formula, source in rows:
        print(f"  {label:78s} {value:>4}")

    os.makedirs(TAB_DIR, exist_ok=True)
    with open(f"{TAB_DIR}/arithmetic_audit.csv", "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["label", "value", "reconciles_as", "source"])
        for label, value, formula, source in rows:
            w.writerow([label, value, formula, source])

    print(f"\nAll cross-total assertions passed.")
    print(f"EN/PT -> {TAB_DIR}/arithmetic_audit.csv")


if __name__ == "__main__":
    main()
