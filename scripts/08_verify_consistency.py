#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EN | Check that the extraction table, the PRISMA counts and every results table
     still agree with one another.
PT | Verifica se a tabela de extracao, as contagens PRISMA e todas as tabelas de
     resultado continuam concordando entre si.

EN | This repository is a reproducibility package: raw data, scripts, tables and
     figures. Nothing here is narrated in prose, so the failure mode to guard
     against is not a mistyped sentence but a silent drift between artefacts -
     an extraction row edited by hand, a PRISMA count left behind after a new
     search arm, a results table regenerated from a stale input. This script
     recomputes each derived number from its source and fails loudly on any
     disagreement. Run it after every pipeline change, before committing.
PT | Este repositorio e um pacote de reprodutibilidade: dados brutos, scripts,
     tabelas e figuras. Nada aqui e narrado em prosa, entao o modo de falha a
     evitar nao e uma frase mal digitada, e sim um descolamento silencioso entre
     artefatos - uma linha de extracao editada a mao, uma contagem PRISMA
     esquecida apos um novo braco de busca, uma tabela de resultado regerada a
     partir de entrada velha. Este script recalcula cada numero derivado a
     partir da fonte e falha ruidosamente em qualquer divergencia. Rode apos
     toda mudanca no pipeline, antes de versionar.

    python scripts/08_verify_consistency.py
"""

import csv
import json
import math
import sys

EXTRACTION = "data/extracted/diagnostic_accuracy_extraction.csv"
KINETICS = "data/extracted/kinetic_parameters.csv"
EXTRACTION_JSON = "data/extracted/diagnostic_accuracy_extraction.json"
FLOW = "data/processed/prisma_flow.json"
POOLED = "results/tables/meta_analysis_pooled_auc.csv"
INPUTS = "results/tables/meta_analysis_input_estimates.csv"
SENS = "results/tables/sensitivity_single_mirna.csv"
CITED = "results/tables/citation_frequency_vs_auc.csv"
CORR = "results/tables/citation_vs_auc_correlation.json"
COUNTS = "data/raw/systematic_review_2026/mirna_mention_counts.csv"
CORPUS = "data/raw/systematic_review_2026/screening_corpus.json"
TRIALS = "data/raw/clinical_trials_2026/mirna_therapeutics_trials.json"


def study_id(row):
    """EN/PT: PMID when the study has one, DOI otherwise."""
    pmid = str(row.get("pmid", "")).strip()
    if pmid.endswith(".0"):
        pmid = pmid[:-2]
    return pmid or str(row.get("doi", "")).strip().lower()


def main():
    fails, checks = [], 0

    def check(ok, msg):
        nonlocal checks
        checks += 1
        if not ok:
            fails.append(msg)

    ext = list(csv.DictReader(open(EXTRACTION, encoding="utf-8")))
    flow = json.load(open(FLOW, encoding="utf-8"))
    pooled = list(csv.DictReader(open(POOLED, encoding="utf-8")))
    inputs = list(csv.DictReader(open(INPUTS, encoding="utf-8")))
    sens = list(csv.DictReader(open(SENS, encoding="utf-8")))
    cited = list(csv.DictReader(open(CITED, encoding="utf-8")))
    corr = json.load(open(CORR, encoding="utf-8"))
    counts = list(csv.DictReader(open(COUNTS, encoding="utf-8")))
    corpus = json.load(open(CORPUS, encoding="utf-8"))
    trials = json.load(open(TRIALS, encoding="utf-8"))

    print("EN | Verifying internal consistency of data, counts and result tables")
    print("PT | Verificando consistencia interna de dados, contagens e tabelas")
    print("=" * 76)

    # --- 1. Extraction table is well formed --------------------------------
    ids = [r["record_id"] for r in ext]
    check(len(set(ids)) == len(ids), "extraction: duplicate record_id")
    check(all(not r["verbatim_quote"].strip() == "" for r in ext),
          "extraction: rows without a verbatim quote -> "
          f"{[r['record_id'] for r in ext if not r['verbatim_quote'].strip()]}")
    check(all(r["exclusion_reason"].strip() for r in ext
              if r["eligible_primary_pool"] == "no"),
          "extraction: excluded rows without a reason -> "
          f"{[r['record_id'] for r in ext if r['eligible_primary_pool']=='no' and not r['exclusion_reason'].strip()]}")
    check(all(r["eligible_primary_pool"] in ("yes", "no") for r in ext),
          "extraction: eligible_primary_pool must be yes or no")
    check(all(r["marker_type"] in ("single_miRNA", "multi_miRNA_panel") for r in ext),
          "extraction: unexpected marker_type")
    for r in ext:
        if r["auc"]:
            check(0.0 < float(r["auc"]) <= 1.0, f"extraction {r['record_id']}: AUC out of range")
        if r["auc_ci_low"] and r["auc_ci_high"]:
            check(float(r["auc_ci_low"]) <= float(r["auc"]) <= float(r["auc_ci_high"]),
                  f"extraction {r['record_id']}: AUC outside its own confidence interval")
        for f in ("sensitivity", "specificity"):
            if r[f]:
                check(0.0 < float(r[f]) <= 1.0,
                      f"extraction {r['record_id']}: {f} should be a proportion, not a percentage")

    # --- 2. The JSON mirror matches the CSV --------------------------------
    try:
        mirror = json.load(open(EXTRACTION_JSON, encoding="utf-8"))
        check(len(mirror) == len(ext),
              f"extraction: JSON mirror has {len(mirror)} rows, CSV has {len(ext)}")
    except FileNotFoundError:
        check(False, f"missing {EXTRACTION_JSON}")

    # --- 3. PRISMA counts are what the tables actually contain -------------
    elig = flow["eligibility_fulltext"]
    incl = flow["included_in_meta_analysis"]
    ident = flow["identification"]
    check(elig["extracted_estimates_total"] == len(ext),
          f"PRISMA extracted_estimates_total={elig['extracted_estimates_total']} but table has {len(ext)}")
    check(elig["studies_contributing_extracted_estimates"] == len({study_id(r) for r in ext}),
          "PRISMA studies_contributing_extracted_estimates disagrees with the table")
    check(elig["estimates_eligible_for_primary_pool"] ==
          sum(1 for r in ext if r["eligible_primary_pool"] == "yes"),
          "PRISMA estimates_eligible_for_primary_pool disagrees with the table")
    check(incl["estimates_with_estimable_standard_error"] == len(inputs),
          f"PRISMA poolable={incl['estimates_with_estimable_standard_error']} but inputs table has {len(inputs)}")
    check(incl["independent_studies"] == len({study_id(r) for r in inputs}),
          "PRISMA independent_studies disagrees with the inputs table")
    check(ident["total_unique_records"] == len(corpus),
          f"PRISMA total_unique_records={ident['total_unique_records']} but corpus has {len(corpus)}")
    check(ident["scopus_records_new"] ==
          ident["scopus_records_AD_arm"] - ident["scopus_records_already_in_pubmed_corpus"]
          - ident["scopus_duplicates_within_export"] + ident["scopus_PD_records_new"],
          "PRISMA Scopus arithmetic does not add up")
    check(ident["scopus_records_PD_arm"] == (ident["scopus_PD_already_in_pubmed_corpus"]
                                             + ident["scopus_PD_overlapping_scopus_AD_arm"]
                                             + ident["scopus_PD_records_new"]),
          "PRISMA Scopus PD arm arithmetic does not add up")

    # --- 4. Every poolable estimate is an eligible extracted estimate ------
    ext_by_id = {r["record_id"]: r for r in ext}
    for r in inputs:
        e = ext_by_id.get(r["record_id"])
        check(e is not None, f"inputs: {r['record_id']} is not in the extraction table")
        if e:
            check(e["eligible_primary_pool"] == "yes",
                  f"inputs: {r['record_id']} is pooled but flagged ineligible")
            check(abs(float(e["auc"]) - float(r["auc"])) < 1e-9,
                  f"inputs: {r['record_id']} AUC differs from the extraction table")
            check(float(r["se_auc"]) > 0, f"inputs: {r['record_id']} has a non-positive SE")

    # --- 5. Pooled table is internally coherent ----------------------------
    by_sub = {r["subgroup"]: r for r in pooled}
    for r in pooled:
        lo, est, hi = float(r["ci_low"]), float(r["pooled_auc"]), float(r["ci_high"])
        check(lo < est < hi, f"pooled [{r['subgroup']}]: estimate outside its interval")
        check(0.0 < lo and hi < 1.0, f"pooled [{r['subgroup']}]: interval leaves the AUC scale")
        check(int(r["k_estimates"]) >= int(r["n_studies"]),
              f"pooled [{r['subgroup']}]: more studies than estimates")
        check(0.0 <= float(r["I2_percent"]) <= 100.0,
              f"pooled [{r['subgroup']}]: I2 out of range")
        check(int(r["df"]) == int(r["k_estimates"]) - 1,
              f"pooled [{r['subgroup']}]: df should be k-1")

    overall = by_sub.get("Overall (all eligible) | Global")
    check(overall is not None, "pooled: overall row missing")
    if overall:
        check(int(overall["k_estimates"]) == len(inputs),
              "pooled: overall k does not match the inputs table")

    # EN/PT: disease and marker subgroups must partition the overall pool
    for parts, whole in [
        (["AD - all markers | todos marcadores", "PD - all markers | todos marcadores"],
         "Overall (all eligible) | Global"),
        (["All - single miRNA | miRNA isolado", "All - multi-miRNA panel | painel multi-miRNA"],
         "Overall (all eligible) | Global"),
        (["AD - single miRNA | miRNA isolado", "PD - single miRNA | miRNA isolado"],
         "All - single miRNA | miRNA isolado"),
        (["AD - multi-miRNA panel | painel multi-miRNA", "PD - multi-miRNA panel | painel multi-miRNA"],
         "All - multi-miRNA panel | painel multi-miRNA"),
    ]:
        if whole in by_sub and all(p in by_sub for p in parts):
            got = sum(int(by_sub[p]["k_estimates"]) for p in parts)
            want = int(by_sub[whole]["k_estimates"])
            check(got == want,
                  f"pooled: {' + '.join(parts)} = {got} estimates, but {whole} has {want}")

    # EN/PT: a biofluid subgroup must rest on at least three independent studies
    for r in pooled:
        if r["subgroup"].startswith("Biofluid"):
            check(int(r["n_studies"]) >= 3,
                  f"pooled [{r['subgroup']}]: biofluid subgroup with fewer than 3 studies")

    # --- 6. Sensitivity analysis agrees with the primary pool --------------
    primary = [r for r in sens if r["analysis"].startswith("primary")]
    check(len(primary) == 1, "sensitivity: primary row missing")
    if primary and "All - single miRNA | miRNA isolado" in by_sub:
        p, m = primary[0], by_sub["All - single miRNA | miRNA isolado"]
        check(abs(float(p["pooled_auc"]) - float(m["pooled_auc"])) < 5e-4,
              "sensitivity: primary row disagrees with the pooled single-miRNA estimate")
        check(int(p["k_estimates"]) == int(m["k_estimates"]),
              "sensitivity: primary k disagrees with the pooled table")
    one_per = [r for r in sens if r["analysis"].startswith("one estimate per study")]
    if one_per:
        check(int(one_per[0]["k_estimates"]) == int(one_per[0]["n_studies"]),
              "sensitivity: one-per-study row must have k equal to the study count")

    # --- 7. Mention counts cover the corpus the AUCs came from -------------
    fam_counts = {r["family"]: int(r["n_articles_mentioning_family"]) for r in counts}
    for r in cited:
        check(r["family"] in fam_counts or int(r["n_articles_mentioning"]) == 0,
              f"citation: {r['family']} has a count with no entry in the mention table")
    zero_but_extracted = [r["family"] for r in cited
                          if int(r["n_articles_mentioning"]) == 0]
    # EN | A marker with an eligible estimate must be mentioned by at least the
    #      article that reported it, unless that article carries no abstract.
    # PT | Um marcador com estimativa elegivel deve ser mencionado ao menos pelo
    #      artigo que o reportou, salvo se esse artigo nao tiver resumo.
    no_abstract = sum(1 for v in corpus.values() if not (v.get("abstract") or "").strip())
    check(len(zero_but_extracted) <= no_abstract,
          f"citation: {len(zero_but_extracted)} markers show zero mentions "
          f"({zero_but_extracted}) but only {no_abstract} corpus records lack an abstract - "
          "the mention counts are probably built over a smaller corpus than the estimates")

    for entry in corr:
        check(-1.0 <= entry["spearman_rho"] <= 1.0, "correlation: rho out of range")
        check(0.0 <= entry["spearman_p"] <= 1.0, "correlation: p out of range")
        check(entry["n_mirnas"] > 2, "correlation: fewer than three points")

    # --- 8. Kinetic parameters carry their own provenance ------------------
    # EN | Same discipline as the accuracy table: a parameter is only usable if
    #      the sentence that supports it is stored with it, and if the number
    #      recorded is the number that sentence actually states. The second
    #      condition is the one that catches a transcription slip, so it is
    #      checked mechanically rather than trusted.
    # PT | Mesma disciplina da tabela de acuracia: um parametro so serve se a
    #      frase que o sustenta estiver guardada junto, e se o numero registrado
    #      for o numero que essa frase de fato declara. A segunda condicao e a
    #      que pega erro de transcricao, entao e checada mecanicamente e nao
    #      confiada.
    try:
        kin = list(csv.DictReader(open(KINETICS, encoding="utf-8")))
    except FileNotFoundError:
        kin = []
    if kin:
        kids = [r["param_id"] for r in kin]
        check(len(set(kids)) == len(kids), "kinetics: duplicate param_id")
        for r in kin:
            pid = r["param_id"]
            check(bool(r["verbatim_quote"].strip()), f"kinetics {pid}: no verbatim quote")
            check(bool(r["pmid"].strip() or r["doi"].strip()), f"kinetics {pid}: no PMID or DOI")
            check(bool(r["unit"].strip()), f"kinetics {pid}: no unit")
            check(bool(r["species"].strip()), f"kinetics {pid}: species not recorded")
            try:
                float(r["value"])
            except ValueError:
                check(False, f"kinetics {pid}: value {r['value']!r} is not numeric")
                continue
            # EN/PT: the recorded number must appear verbatim in its own quote
            quote = r["verbatim_quote"]
            val = r["value"].strip()
            trimmed = val.rstrip("0").rstrip(".") if "." in val else val
            check(val in quote or trimmed in quote,
                  f"kinetics {pid}: value {val} does not appear in its verbatim quote")

    # --- 9. Clinical trial landscape --------------------------------------
    nd = trials["neurodegeneration_specific"]
    check(nd["mirna_directed_therapeutic_trials"] == 0,
          "trials: the zero-in-AD/PD claim no longer matches the data")
    check(len(trials["therapeutic_trials_all_indications"]) > 0,
          "trials: therapeutic trial list is empty")

    print(f"Checks run / verificacoes: {checks}")
    if fails:
        print(f"\nFAILURES / FALHAS: {len(fails)}")
        for f in fails:
            print(f"  - {f}")
        return 1
    print("\nEN | Data, PRISMA counts and result tables are mutually consistent.")
    print("PT | Dados, contagens PRISMA e tabelas de resultado sao consistentes entre si.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
