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
import os
import json
import math
import re
import sys

EXTRACTION = "data/extracted/diagnostic_accuracy_extraction.csv"
KINETICS = "data/extracted/kinetic_parameters.csv"
SCHWANHAUSSER = "data/raw/kinetics_2026/schwanhausser_2011_supplementary_table.xls"
TUSHEV = "data/raw/kinetics_2026/tushev_2018_table_S1.xls"
ODE_RESULTS = "results/tables/ode_calibrated_results.json"
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
QUADAS = "results/tables/quadas2_assessment.csv"
QUADAS_STUDY_LEVEL = "data/extracted/quadas2_study_level.csv"
QUADAS_SUMMARY = "results/tables/quadas2_summary.json"
BIVARIATE = "results/tables/bivariate_summary.csv"
BIVARIATE_JSON = "results/tables/bivariate_model.json"
GRADE_JSON = "results/tables/grade_certainty.json"
DOSING_JSON = "results/tables/mimic_dosing_feasibility.json"
DOSING_CSV = "results/tables/mimic_dosing_feasibility.csv"
ANIM_JSON = "results/tables/mechanism_animations.json"


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

    # EN | A claim about the run itself - "N checks pass" in the README - cannot be a
    #      check, because counting it changes the number it asserts. claim() records a
    #      failure the same way but leaves the counter alone, so the number the README
    #      quotes stays the number of checks over data and results.
    # PT | Uma afirmacao sobre a propria execucao - "N verificacoes passam" no README -
    #      nao pode ser uma verificacao, porque conta-la muda o numero que ela afirma. O
    #      claim() registra falha do mesmo jeito mas nao mexe no contador, entao o numero
    #      citado no README continua sendo o de verificacoes sobre dados e resultados.
    def claim(ok, msg):
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
    # EN | non_miRNA_marker exists so that a record excluded BECAUSE its index test is
    #      not a microRNA can still be recorded with what it actually measured. Calling a
    #      long non-coding RNA a single_miRNA to fit the vocabulary would make the
    #      exclusion reason contradict the row it sits on.
    # PT | O non_miRNA_marker existe para que um registro excluido PORQUE seu teste indice
    #      nao e um microRNA ainda possa ser registrado com o que de fato mediu. Chamar um
    #      RNA longo nao codificante de single_miRNA para caber no vocabulario faria a
    #      razao de exclusao contradizer a propria linha em que esta.
    check(all(r["marker_type"] in ("single_miRNA", "multi_miRNA_panel", "non_miRNA_marker")
              for r in ext),
          "extraction: unexpected marker_type")
    check(all(r["eligible_primary_pool"] == "no" for r in ext
              if r["marker_type"] == "non_miRNA_marker"),
          "extraction: a non-miRNA marker reached the primary pool")
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
            if r["kind"] == "declared_gap":
                # EN | A parameter that was searched for and not found. It must say how it
                #      was searched and must not borrow a source, a quote or a number -
                #      attaching the DOI of a paper that was rejected would make a gap look
                #      like evidence.
                # PT | Um parametro procurado e nao encontrado. Precisa dizer como foi
                #      buscado e nao pode emprestar fonte, citacao nem numero - anexar o DOI
                #      de um artigo rejeitado faria uma lacuna parecer evidencia.
                check(not r["value_si"].strip() and not r["verbatim_quote"].strip()
                      and not r["pmid"].strip() and not r["doi"].strip(),
                      f"kinetics {pid}: a declared gap must not carry a value, quote or source")
                check(len(r["note"].strip()) > 80,
                      f"kinetics {pid}: a declared gap must record how it was searched")
                continue
            if r["kind"] == "derived":
                # EN | A value this project COMPUTED from a source table rather than read
                #      in a sentence. It must name its source and document the derivation,
                #      and it must not claim a verbatim quote it does not have: quoting a
                #      sentence that never contained the number is how a computed figure
                #      starts looking like a measured one.
                # PT | Valor que este projeto CALCULOU de uma tabela-fonte em vez de ler
                #      numa frase. Precisa nomear a fonte e documentar a derivacao, e nao
                #      pode alegar citacao verbatim que nao tem: citar uma frase que nunca
                #      continha o numero e como uma cifra calculada passa a parecer medida.
                check(not r["verbatim_quote"].strip(),
                      f"kinetics {pid}: a derived value must not carry a verbatim quote")
                check(bool(r["source"].strip()) and bool(r["value_si"].strip()),
                      f"kinetics {pid}: a derived value needs a source and an SI value")
                check("DERIVED" in r["note"] or "derived" in r["note"],
                      f"kinetics {pid}: a derived value must document its derivation")
                continue
            check(bool(r["verbatim_quote"].strip()), f"kinetics {pid}: no verbatim quote")
            check(bool(r["pmid"].strip() or r["doi"].strip()), f"kinetics {pid}: no PMID or DOI")
            check(r["kind"] in ("numeric", "qualitative_constraint", "declared_gap", "derived"),
                  f"kinetics {pid}: unknown kind {r['kind']!r}")
            check(bool(r["species"].strip()), f"kinetics {pid}: species not recorded")
            if r["kind"] != "numeric":
                # EN | A measured absence ("undetectable") is a real constraint on the
                #      model but is not a number, and must not be stored as a fitted
                #      zero. Only the wording is checked against the source.
                # PT | Uma ausencia medida ("undetectable") e uma restricao real ao
                #      modelo, mas nao e um numero, e nao pode ser guardada como zero
                #      ajustado. So a redacao e conferida contra a fonte.
                check(r["value_as_written"].strip() in r["verbatim_quote"],
                      f"kinetics {pid}: qualitative value does not appear in its quote")
                check(not r["value_si"].strip(),
                      f"kinetics {pid}: a qualitative constraint must not carry an SI value")
                continue
            check(bool(r["unit_si"].strip()), f"kinetics {pid}: no SI unit")
            check(bool(r["condition"].strip()),
                  f"kinetics {pid}: no experimental condition - a rate constant without "
                  "its pH, temperature and buffer is not a usable parameter")
            try:
                float(r["value_si"])
            except ValueError:
                check(False, f"kinetics {pid}: value_si {r['value_si']!r} is not numeric")
                continue
            # EN | The number as printed in the source must appear in the source's own
            #      sentence. value_si may differ from it (unit conversion, percent to
            #      rate constant, scientific notation), so the two are checked apart:
            #      value_as_written is the audit trail, value_si is what the model runs.
            # PT | O numero como impresso na fonte precisa aparecer na frase da propria
            #      fonte. value_si pode diferir dele (conversao de unidade, porcentagem
            #      para constante, notacao cientifica), entao os dois sao checados em
            #      separado: value_as_written e a trilha de auditoria, value_si e o que
            #      o modelo roda.
            quote = r["verbatim_quote"]
            written = r["value_as_written"].strip()
            trimmed = written.rstrip("0").rstrip(".") if "." in written else written
            check(written in quote or trimmed in quote,
                  f"kinetics {pid}: value_as_written {written!r} does not appear in its "
                  "verbatim quote")

    # EN | The two derived rows and the K030 gap rest on one archived spreadsheet
    #      (Schwanhausser et al. 2011, supplementary table). They were first worked
    #      out by hand; here they are recomputed from the file, so that anyone can see
    #      the medians and the absence of BACE1/SNCA come from the data and not from
    #      a note.
    # PT | As duas linhas derivadas e a lacuna K030 dependem de uma planilha arquivada
    #      (Schwanhausser et al. 2011, tabela suplementar). Foram calculadas a mao
    #      primeiro; aqui sao recalculadas a partir do arquivo, para que qualquer um
    #      veja que as medianas e a ausencia de BACE1/SNCA vem dos dados e nao de uma
    #      nota.
    kin_by_id = {r["param_id"]: r for r in kin}
    if {"K030", "K040", "K041"} <= set(kin_by_id):
        try:
            import pandas as pd
            sch = pd.read_excel(SCHWANHAUSSER)
        except Exception as e:  # EN/PT: missing xlrd or missing file is a failure
            sch = None
            check(False, f"kinetics: cannot read {SCHWANHAUSSER}: {e}")
        if sch is not None:
            for pid, col in (("K040", "mRNA half-life average [h]"),
                             ("K041", "Protein half-life average [h]")):
                vals = pd.to_numeric(sch[col], errors="coerce").dropna()
                r = kin_by_id[pid]
                check(int(r["n"]) == len(vals),
                      f"kinetics {pid}: n={r['n']} but the table has {len(vals)} values")
                check(abs(float(r["value_as_written"]) - float(vals.median())) < 1e-9,
                      f"kinetics {pid}: median {vals.median()} != {r['value_as_written']}")
                check(abs(float(r["value_si"]) - math.log(2) / float(vals.median())) < 1e-6,
                      f"kinetics {pid}: value_si is not ln2 / median half-life")
            genes = {g.strip().lower() for cell in sch["Gene Names"].dropna()
                     for g in str(cell).split(";")}
            for g in ("bace1", "snca", "sncb", "sncg", "app"):
                check(g not in genes,
                      f"kinetics K030: {g} IS in the table - the declared gap is wrong")

    # EN | Mimic washout: the reported time must be the time for a 10-fold bolus
    #      (excess 9x) to decay within 10% of baseline, t = ln(90) * t_half / ln 2.
    #      This once used ln(9) and halved every washout time.
    # PT | Eliminacao do mimetico: o tempo reportado deve ser o de um bolus de 10x
    #      (excesso 9x) decair a menos de 10% do basal, t = ln(90) * t_meia / ln 2.
    #      Isto ja usou ln(9) e cortou pela metade todos os tempos de eliminacao.
    try:
        ode = json.load(open(ODE_RESULTS, encoding="utf-8"))
    except FileNotFoundError:
        ode = None
    if ode is not None:
        for lab, w in ode["mimic_washout"].items():
            expect = math.log(90.0) * w["half_life_hours"] / math.log(2.0)
            check(abs(w["hours_to_return_to_baseline"] - expect) < 1e-6 * expect,
                  f"ode washout {lab}: {w['hours_to_return_to_baseline']:.3f} h, "
                  f"expected {expect:.3f} h")

    # EN | The dose comparison is analytic, so it can be checked in closed form rather
    #      than trusted: a mimic factor m gives a fractional BACE1 knockdown of
    #      1 - (d + 3k)/(d + 3k m), and the inverse must return the measured knockdown.
    #      Both ends of each reported range must also be consistent with the free
    #      parameter ranges the same file declares.
    # PT | A comparacao de doses e analitica, entao pode ser checada em forma fechada em
    #      vez de aceita: um fator de mimetico m da uma queda fracional de BACE1 de
    #      1 - (d + 3k)/(d + 3k m), e a inversa tem de devolver a queda medida. As duas
    #      pontas de cada faixa reportada tambem precisam ser coerentes com as faixas de
    #      parametro livre que o mesmo arquivo declara.
    if ode is not None and "mimic_dose_vs_measured_knockdown" in ode:
        dose = ode["mimic_dose_vs_measured_knockdown"]
        fr = ode["free_parameters"]
        target = dose["measured_BACE1_knockdown_K047"]
        kin_by_pid = {r["param_id"]: r for r in kin}
        check(abs(target - float(kin_by_pid["K047"]["value_si"])) < 1e-12,
              "ode dose: measured knockdown does not match K047")

        def kd(d, k, m):
            return 1.0 - (d + 3.0 * k) / (d + 3.0 * k * m)

        # EN/PT: d_mRNA is measured now (K068), so the corners span k_repress only
        d_meas = dose["d_mRNA_BACE1_measured"]
        check(abs(d_meas - float(kin_by_id["K068"]["value_si"])) < 1e-12,
              "ode dose: the BACE1 mRNA decay used is not K068")
        corners = [(d_meas, k)
                   for k in (fr["k_repress"]["low"], fr["k_repress"]["high"])]
        m = dose["mimic_fold_needed_to_offset_clearance"]
        lo, hi = dose["BACE1_knockdown_at_required_mimic"]
        vals = [kd(d, k, m) for d, k in corners]
        check(abs(min(vals) - lo) < 1e-9 and abs(max(vals) - hi) < 1e-9,
              f"ode dose: knockdown range {lo:.4f}-{hi:.4f} != corners "
              f"{min(vals):.4f}-{max(vals):.4f}")
        for m_end in dose["mimic_fold_to_reproduce_measured_knockdown"]:
            got = [kd(d, k, m_end) for d, k in corners]
            check(min(abs(g - target) for g in got) < 1e-9,
                  f"ode dose: mimic fold {m_end:.4f} does not give the measured knockdown")
        check(dose["required_knockdown_below_measured_everywhere"] == (hi < target),
              "ode dose: the below-measured verdict disagrees with the reported range")

    # EN | Wilhelm et al. print copy numbers and concentrations in the same table and
    #      state in the legend that the concentrations were computed over the synaptic
    #      volume MINUS the mitochondrial volume. Both halves of that statement are
    #      recomputed here: the alpha-synuclein split that K054 derives, and the volume
    #      implied by each copy number / concentration pair, which must agree with the
    #      two geometric rows read from a different figure of the same paper.
    # PT | Wilhelm et al. imprimem numero de copias e concentracao na mesma tabela e
    #      dizem na legenda que as concentracoes foram calculadas sobre o volume
    #      sinaptico MENOS o volume mitocondrial. As duas metades disso sao recalculadas
    #      aqui: a separacao da alfa-sinucleina que o K054 deriva, e o volume implicado
    #      por cada par copias / concentracao, que tem de bater com as duas linhas
    #      geometricas lidas de outra figura do mesmo artigo.
    if {"K050", "K052", "K053", "K054", "K057"} <= set(kin_by_id):
        AVOGADRO = 6.02214076e23
        ratio = float(kin_by_id["K053"]["value_si"])
        share = ratio / (1.0 + ratio)
        total_uM = 43.57                      # printed beside K052 in the same row
        check(f"{total_uM}" in kin_by_id["K052"]["verbatim_quote"],
              "kinetics K052: the quoted row no longer carries the 43.57 uM used by K054")
        check(abs(float(kin_by_id["K054"]["value_si"]) - total_uM * share) < 1e-3,
              f"kinetics K054: {kin_by_id['K054']['value_si']} != "
              f"{total_uM} x {share:.6f} = {total_uM * share:.4f}")
        v_cyto = float(kin_by_id["K050"]["value_si"]) - float(kin_by_id["K057"]["value_si"])
        for pid, conc_uM in (("K052", 43.57), ("K055", 0.77), ("K056", 41.96)):
            copies = float(kin_by_id[pid]["value_si"])
            implied = copies / (conc_uM * 1e-6 * AVOGADRO) * 1e15     # litres -> um^3
            check(abs(implied - v_cyto) / v_cyto < 0.02,
                  f"kinetics {pid}: copies and concentration imply {implied:.4f} um^3, "
                  f"but the bouton minus its mitochondria is {v_cyto:.4f} um^3")

    # EN | The saturation and stoichiometry blocks are pure arithmetic on measured rows,
    #      so they are recomputed here from the parameter table rather than trusted.
    # PT | Os blocos de saturacao e estequiometria sao aritmetica pura sobre linhas
    #      medidas, entao sao recalculados aqui a partir da tabela em vez de aceitos.
    if ode is not None and "alpha_synuclein_saturation" in ode:
        sat = ode["alpha_synuclein_saturation"]
        C = float(kin_by_id["K054"]["value_si"])
        check(abs(sat["alpha_synuclein_uM_in_bouton"] - C) < 1e-9,
              "ode saturation: concentration does not match K054")
        for pt in sat["points"]:
            mh = pt["m_half_uM"]
            check(abs(pt["fraction_of_maximal_elongation_rate"] - C / (mh + C)) < 1e-9,
                  f"ode saturation: fraction at m_half {mh} is not C/(m_half+C)")
            check(abs(pt["percent_rate_change_per_percent_concentration_change"]
                      - mh / (mh + C)) < 1e-9,
                  f"ode saturation: elasticity at m_half {mh} is not m_half/(m_half+C)")
            check(abs(pt["m_half_uM"] - float(kin_by_id["K009"]["value_si"]) * 1e6) < 1e-6
                  or abs(pt["m_half_uM"] - float(kin_by_id["K010"]["value_si"]) * 1e6) < 1e-6,
                  f"ode saturation: m_half {mh} is neither K009 nor K010")
        check(sat["below_half_saturation"] == (max(
            p["fraction_of_maximal_elongation_rate"] for p in sat["points"]) < 0.5),
            "ode saturation: the below-half-saturation verdict disagrees with its own numbers")
    if ode is not None and "enzyme_substrate_stoichiometry" in ode:
        st = ode["enzyme_substrate_stoichiometry"]
        nb, na = float(kin_by_id["K055"]["value_si"]), float(kin_by_id["K056"]["value_si"])
        check(abs(st["BACE1_copies_per_bouton"] - nb) < 1e-9
              and abs(st["APP_copies_per_bouton"] - na) < 1e-9,
              "ode stoichiometry: copy numbers do not match K055 and K056")
        check(abs(st["APP_per_BACE1"] - na / nb) < 1e-9,
              "ode stoichiometry: the ratio is not APP over BACE1")

    # EN | The three-source chain is arithmetic on measured rows, so every step is
    #      recomputed from the parameter table: the knockdown against its row, the
    #      concentration against K054, the saturation form against K009 and K010, and
    #      the additivity comparison against K058, K059 and K060.
    # PT | A cadeia de tres fontes e aritmetica sobre linhas medidas, entao cada passo e
    #      recalculado a partir da tabela: a queda contra a linha dela, a concentracao
    #      contra o K054, a forma de saturacao contra K009 e K010, e a comparacao de
    #      aditividade contra K058, K059 e K060.
    if ode is not None and "mir7_knockdown_to_elongation" in ode:
        ch = ode["mir7_knockdown_to_elongation"]
        C0 = float(kin_by_id["K054"]["value_si"])
        check(abs(ch["alpha_synuclein_uM_in_bouton"] - C0) < 1e-9,
              "ode chain: concentration does not match K054")
        known_kd = {float(kin_by_id[pid]["value_si"]) for pid in ("K058", "K063")}
        known_mh = {float(kin_by_id[pid]["value_si"]) * 1e6 for pid in ("K009", "K010")}
        for c in ch["cases"]:
            kd, mh = c["knockdown"], c["m_half_uM"]
            check(any(abs(kd - k) < 1e-12 for k in known_kd),
                  f"ode chain: knockdown {kd} is not a row of the parameter table")
            check(any(abs(mh - m) < 1e-6 for m in known_mh),
                  f"ode chain: m_half {mh} is neither K009 nor K010")
            C1 = C0 * (1.0 - kd)
            check(abs(c["alpha_synuclein_after_uM"] - C1) < 1e-9,
                  "ode chain: post-knockdown concentration is not C0 x (1 - knockdown)")
            expect = 1.0 - (C1 / (mh + C1)) / (C0 / (mh + C0))
            check(abs(c["elongation_rate_reduction"] - expect) < 1e-9,
                  f"ode chain: elongation reduction {c['elongation_rate_reduction']:.6f} "
                  f"!= {expect:.6f} from the saturation form")
            check(c["elongation_rate_reduction"] < kd,
                  "ode chain: a saturating curve cannot give a more than proportional "
                  "slowdown; this one did")
        check(ch["less_than_proportional_everywhere"] ==
              all(c["elongation_rate_reduction"] < c["knockdown"] for c in ch["cases"]),
              "ode chain: the less-than-proportional verdict disagrees with its own cases")
        ad = ch["additivity"]
        a_, b_ = float(kin_by_id["K058"]["value_si"]), float(kin_by_id["K059"]["value_si"])
        check(abs(ad["pair_measured"] - float(kin_by_id["K060"]["value_si"])) < 1e-12,
              "ode chain: the measured pair does not match K060")
        check(abs(ad["pair_if_independent"] - (1.0 - (1.0 - a_) * (1.0 - b_))) < 1e-12,
              "ode chain: the independent-action prediction is not 1 - (1-a)(1-b)")

    # EN | The Tushev rows are read straight out of a 24,435-row table, so each one is
    #      looked up again here by gene symbol and compared field by field, and the
    #      derived pooled decay constant is recomputed from all five BACE1 isoforms.
    #      The pooling is the part worth guarding: the abundance-weighted mean of the
    #      RATE constants is the right quantity, and the mean of the half-lives is not.
    # PT | As linhas do Tushev sao lidas de uma tabela de 24.435 linhas, entao cada uma e
    #      procurada de novo aqui pelo simbolo do gene e comparada campo a campo, e a
    #      constante de decaimento derivada e recalculada a partir das cinco isoformas de
    #      BACE1. O pooling e a parte que vale guardar: a media ponderada das CONSTANTES
    #      DE VELOCIDADE e a grandeza certa, e a media das meias-vidas nao e.
    if {"K066", "K067", "K068", "K069"} <= set(kin_by_id):
        try:
            import pandas as pd
            tu = pd.read_excel(TUSHEV, sheet_name="PASSData", header=0)
            tu.columns = [str(c) for c in tu.columns]
        except Exception as e:
            tu = None
            check(False, f"kinetics: cannot read {TUSHEV}: {e}")
        if tu is not None:
            sym = tu["gene.symbol"].astype(str).str.lower()
            hl = pd.to_numeric(tu["half.life[hours]"], errors="coerce")
            rpm = pd.to_numeric(tu["rpm.neuron.culture"], errors="coerce")
            for pid, gene, single in (("K066", "snca", True), ("K069", "app", True)):
                rowsg = tu[sym == gene]
                check(len(rowsg) == 1,
                      f"kinetics {pid}: {gene} has {len(rowsg)} isoforms, the row assumes one")
                if len(rowsg) == 1:
                    t_printed = float(hl[rowsg.index[0]])
                    check(abs(float(kin_by_id[pid]["value_as_written"]) - t_printed) < 1e-4,
                          f"kinetics {pid}: half-life {kin_by_id[pid]['value_as_written']} "
                          f"!= {t_printed} in the table")
                    check(abs(float(kin_by_id[pid]["value_si"]) - math.log(2) / t_printed) < 1e-7,
                          f"kinetics {pid}: value_si is not ln2 over the printed half-life")
            b = tu[sym == "bace1"]
            check(len(b) == 5, f"kinetics K067: bace1 has {len(b)} isoforms, the note says five")
            if len(b):
                dom = rpm[b.index].idxmax()
                check(abs(float(kin_by_id["K067"]["value_as_written"]) - float(hl[dom])) < 1e-4,
                      "kinetics K067: this is not the most abundant BACE1 isoform's half-life")
                k_eff = float((rpm[b.index] * (math.log(2) / hl[b.index])).sum()
                              / rpm[b.index].sum())
                check(abs(float(kin_by_id["K068"]["value_si"]) - k_eff) < 1e-7,
                      f"kinetics K068: pooled constant {kin_by_id['K068']['value_si']} != {k_eff:.8f}")
                # EN/PT: and it must NOT be ln2 over the mean of the half-lives
                wrong = math.log(2) / float((rpm[b.index] * hl[b.index]).sum() / rpm[b.index].sum())
                check(abs(float(kin_by_id["K068"]["value_si"]) - wrong) > 1e-4,
                      "kinetics K068: the pooled constant equals the mean-of-half-lives form, "
                      "which is the wrong average for a decaying pool")

    # --- 8b. QUADAS-2 -------------------------------------------------------
    # EN | The assessment is generated by rule, so the check is that it still covers every
    #      study it claims to and that its own summary counts match its own rows. A stale
    #      risk-of-bias table is worse than none: it looks authoritative.
    # PT | A avaliacao e gerada por regra, entao a checagem e que ela ainda cobre todos os
    #      estudos que diz cobrir e que as contagens do resumo batem com as proprias
    #      linhas. Uma tabela de risco de vies velha e pior que nenhuma: parece confiavel.
    try:
        quadas = list(csv.DictReader(open(QUADAS, encoding="utf-8")))
        qsum = json.load(open(QUADAS_SUMMARY, encoding="utf-8"))
    except FileNotFoundError:
        quadas, qsum = None, None
    if quadas is not None:
        eligible_studies = {study_id(r) for r in ext if r["eligible_primary_pool"] == "yes"}
        check({r["study_id"] for r in quadas} == eligible_studies,
              f"QUADAS-2: assesses {len(quadas)} studies but {len(eligible_studies)} "
              "contribute to the primary pool")
        check(qsum["studies_assessed"] == len(quadas),
              "QUADAS-2: summary study count disagrees with the assessment table")
        allowed = {"high", "low", "unclear", "unrated"}
        for domain, counts in qsum["domain_summary"].items():
            observed = {}
            for r in quadas:
                check(r[domain] in allowed, f"QUADAS-2 {domain}: unexpected verdict {r[domain]!r}")
                observed[r[domain]] = observed.get(r[domain], 0) + 1
                check(bool(r[domain + "_reason"].strip()),
                      f"QUADAS-2 {domain}: a verdict without a stated reason ({r['study_id']})")
            for verdict, n in counts.items():
                check(observed.get(verdict, 0) == n,
                      f"QUADAS-2 {domain}: summary says {n} {verdict}, table has "
                      f"{observed.get(verdict, 0)}")
        # EN/PT: the circularity note must match what the extraction actually excluded
        excluded = {}
        for r in ext:
            if r["eligible_primary_pool"] != "yes" and r["comparison_class"] != "case_vs_healthy_control":
                excluded[r["comparison_class"]] = excluded.get(r["comparison_class"], 0) + 1
        check(qsum["excluded_non_case_control_estimates"] == excluded,
              f"QUADAS-2: the recorded eligibility circularity {qsum['excluded_non_case_control_estimates']} "
              f"disagrees with the extraction {excluded}")

    # EN | The study-level record behind the reference-standard and flow domains. A
    #      verdict of LOW or HIGH there rests on a quoted sentence, so the quote has to be
    #      present, and the flags derived from it have to agree with it.
    # PT | O registro por estudo que sustenta os dominios de padrao de referencia e fluxo.
    #      Um veredito LOW ou HIGH ali repousa numa frase citada, entao a citacao precisa
    #      existir, e os sinalizadores derivados dela precisam concordar com ela.
    try:
        sl = list(csv.DictReader(open(QUADAS_STUDY_LEVEL, encoding="utf-8")))
    except FileNotFoundError:
        sl = None
    if sl is not None and quadas is not None:
        eligible_studies = {study_id(r) for r in ext if r["eligible_primary_pool"] == "yes"}
        check({r["study_id"] for r in sl} == eligible_studies,
              "QUADAS-2 study level: the studies covered are not the studies pooled")
        for r in sl:
            avail = r["fulltext_availability"]
            check(avail in ("yes", "no_fulltext_in_pmc", "no_pmc_record"),
                  f"QUADAS-2 study level {r['study_id']}: unexpected availability {avail!r}")
            if avail != "yes":
                check(not r["reference_standard_quote"] and not r["blinding_quote"],
                      f"QUADAS-2 study level {r['study_id']}: quotes recorded although the "
                      "full text was not retrievable")
                continue
            check(r["reference_standard_named"] in ("yes", "no"),
                  f"QUADAS-2 study level {r['study_id']}: reference_standard_named must be yes or no")
            check((r["reference_standard_named"] == "yes") == bool(r["reference_standard_quote"]),
                  f"QUADAS-2 study level {r['study_id']}: the named flag and the quote disagree")
            check((r["blinding_stated"] == "yes") == bool(r["blinding_quote"]),
                  f"QUADAS-2 study level {r['study_id']}: the blinding flag and the quote disagree")
            if r["autopsy_confirmed"] == "yes":
                check(bool(re.search(r"autops|neuropatholog|Braak|Brain Bank Network",
                                     r["reference_standard_quote"], re.I)),
                      f"QUADAS-2 study level {r['study_id']}: autopsy claimed but the quote "
                      "does not mention neuropathological confirmation")
        # EN/PT: every reference-standard verdict must follow from the study-level record
        by_sl = {r["study_id"]: r for r in sl}
        for row in quadas:
            rec = by_sl.get(row["study_id"])
            if not rec:
                continue
            v = row["rob_reference_standard"]
            if rec["autopsy_confirmed"] == "yes" or rec["blinding_stated"] == "yes":
                check(v == "low", f"QUADAS-2 {row['study_id']}: expected low reference-standard risk")
            elif rec["fulltext_availability"] != "yes":
                check(v == "unclear",
                      f"QUADAS-2 {row['study_id']}: unretrievable full text must be unclear")
            elif rec["reference_standard_named"] == "yes":
                check(v == "unclear", f"QUADAS-2 {row['study_id']}: named criteria must be unclear")
            else:
                check(v == "high", f"QUADAS-2 {row['study_id']}: unnamed criteria must be high")
        check(all(r["rob_flow_timing"] == "unclear" for r in quadas),
              "QUADAS-2: flow and timing is no longer uniformly unclear; the reason text "
              "in scripts/14 claims it is, so one of the two is now wrong")
        check(all(r[d] != "unrated" for r in quadas
                  for d in ("rob_patient_selection", "rob_index_test",
                            "rob_reference_standard", "rob_flow_timing")),
              "QUADAS-2: a risk-of-bias domain is unrated again")

        # EN | A narrative string is the part of an output that silently goes stale: the
        #      counts get recomputed on every run, the prose does not. Require that no
        #      text in the summary announces unrated domains while the counts say none
        #      are unrated, and that the counts in the narrative match the record.
        # PT | Uma string narrativa e a parte da saida que envelhece em silencio: as
        #      contagens sao recalculadas a cada execucao, a prosa nao. Exige que nenhum
        #      texto do resumo anuncie dominios nao avaliados enquanto as contagens dizem
        #      que nao ha, e que os numeros da narrativa batam com o registro.
        qsum = json.load(open(QUADAS_SUMMARY, encoding="utf-8"))
        n_unrated = sum(d.get("unrated", 0) for d in qsum["domain_summary"].values())
        prose = " ".join(v for v in qsum.values() if isinstance(v, str))
        if n_unrated == 0:
            check("UNRATED" not in prose and "NAO AVALIADOS" not in prose,
                  "QUADAS-2: the summary still announces unrated domains, but no domain "
                  "is unrated; the prose outlived the numbers")
        sl_assessed = [by_sl[r["study_id"]] for r in quadas if r["study_id"] in by_sl]
        counted = {
            "fulltext": sum(1 for r in sl_assessed if r["fulltext_availability"] == "yes"),
            "named": sum(1 for r in sl_assessed if r["reference_standard_named"] == "yes"),
            "autopsy": sum(1 for r in sl_assessed if r["autopsy_confirmed"] == "yes"),
            "blinded": sum(1 for r in sl_assessed if r["blinding_stated"] == "yes"),
        }
        check(counted["fulltext"] == 22 and counted["named"] == 13
              and counted["autopsy"] == 1 and counted["blinded"] == 1,
              f"QUADAS-2 full-text pass: the study-level record changed {counted}; the "
              "documentation quotes 22 full texts, 13 naming criteria, 1 autopsy-confirmed "
              "and 1 stating blinding")
        n_assessed = qsum["studies_assessed"]
        for phrase in (f"{counted['fulltext']} of {n_assessed} studies",
                       f"{counted['named']} name the diagnostic criteria",
                       f"{counted['autopsy']} has neuropathological confirmation",
                       f"None of the {counted['fulltext']} reports a STARD flow diagram"):
            check(phrase in qsum["full_text_pass_en"],
                  f"QUADAS-2 narrative (en) no longer says {phrase!r}")
        for phrase in (f"{counted['fulltext']} dos {n_assessed} estudos",
                       f"{counted['named']} nomeiam os criterios",
                       f"{counted['autopsy']} tem confirmacao neuropatologica",
                       f"Nenhum dos {counted['fulltext']} traz fluxograma"):
            check(phrase in qsum["full_text_pass_pt"],
                  f"QUADAS-2 narrative (pt) no longer says {phrase!r}")

    # --- 8c. Bivariate model ------------------------------------------------
    # EN | Recompute the derived diagnostic measures from the summary point, and require
    #      that the estimator passed its own recovery test on simulated data.
    # PT | Recalcula as medidas diagnosticas derivadas do ponto sumario, e exige que o
    #      estimador tenha passado no proprio teste de recuperacao em dados simulados.
    try:
        biv = list(csv.DictReader(open(BIVARIATE, encoding="utf-8")))
        bjson = json.load(open(BIVARIATE_JSON, encoding="utf-8"))
    except FileNotFoundError:
        biv, bjson = None, None
    if biv is not None:
        for key, rep in bjson["estimator_self_test"].items():
            check(rep["pass_"], f"bivariate: the estimator failed to recover {key} in its self-test")
        for row in biv:
            se_, sp_ = float(row["summary_sensitivity"]), float(row["summary_specificity"])
            check(0.0 < se_ < 1.0 and 0.0 < sp_ < 1.0,
                  f"bivariate {row['analysis']}: summary point out of range")
            check(float(row["sensitivity_ci_low"]) <= se_ <= float(row["sensitivity_ci_high"]),
                  f"bivariate {row['analysis']}: sensitivity outside its own interval")
            check(float(row["specificity_ci_low"]) <= sp_ <= float(row["specificity_ci_high"]),
                  f"bivariate {row['analysis']}: specificity outside its own interval")
            dor = (se_ / (1 - se_)) * (sp_ / (1 - sp_))
            check(abs(float(row["diagnostic_odds_ratio"]) - dor) < 0.01,
                  f"bivariate {row['analysis']}: DOR is not sens/(1-sens) x spec/(1-spec)")
            check(abs(float(row["positive_likelihood_ratio"]) - se_ / (1 - sp_)) < 0.01,
                  f"bivariate {row['analysis']}: LR+ is not sens/(1-spec)")
            check(abs(float(row["negative_likelihood_ratio"]) - (1 - se_) / sp_) < 0.01,
                  f"bivariate {row['analysis']}: LR- is not (1-sens)/spec")
            check(row["converged"] == "True", f"bivariate {row['analysis']}: fit did not converge")
        primary = [r for r in biv if r["analysis"].startswith("one estimate per study")]
        check(len(primary) == 1, "bivariate: the one-estimate-per-study analysis is missing")
        if primary:
            check(primary[0]["k_estimates"] == primary[0]["n_studies"],
                  "bivariate: the one-estimate-per-study analysis has more estimates than studies")

    # --- 8d. GRADE ----------------------------------------------------------
    # EN | The certainty rating is arithmetic on the other tables, so it is recomputed
    #      here: the downgrade steps must follow from the thresholds the file itself
    #      declares, the total must give the stated level, and the summary of findings
    #      must follow from the summary sensitivity and specificity at each prevalence.
    # PT | A classificacao de certeza e aritmetica sobre as outras tabelas, entao e
    #      recalculada aqui: os passos de rebaixamento tem de decorrer dos limiares que o
    #      proprio arquivo declara, o total tem de dar o nivel declarado, e o resumo de
    #      achados tem de decorrer da sensibilidade e da especificidade sumarias em cada
    #      prevalencia.
    try:
        gr = json.load(open(GRADE_JSON, encoding="utf-8"))
    except FileNotFoundError:
        gr = None
    if gr is not None and quadas is not None and biv is not None:
        th = gr["thresholds"]
        dom = ["rob_patient_selection", "rob_index_test",
               "rob_reference_standard", "rob_flow_timing"]
        n = len(quadas)
        high_rob = sum(1 for r in quadas if any(r[d] == "high" for d in dom))
        expect = 2 if high_rob / n >= th["risk_of_bias_very_serious_fraction"] else (
                 1 if high_rob / n >= th["risk_of_bias_serious_fraction"] else 0)
        check(gr["domains"]["risk_of_bias"]["downgrade_steps"] == expect,
              f"GRADE risk of bias: {gr['domains']['risk_of_bias']['downgrade_steps']} steps "
              f"but {high_rob}/{n} high-risk studies imply {expect}")
        i2 = float(next(r for r in pooled if r["subgroup"].startswith("Overall"))["I2_percent"])
        expect = 2 if i2 >= th["inconsistency_very_serious_i2"] else (
                 1 if i2 >= th["inconsistency_serious_i2"] else 0)
        check(gr["domains"]["inconsistency"]["downgrade_steps"] == expect,
              f"GRADE inconsistency: I2 {i2} implies {expect} steps")
        total = sum(d["downgrade_steps"] for d in gr["domains"].values())
        check(total == gr["total_downgrade_steps"], "GRADE: the downgrade steps do not sum")
        levels = ["very low", "low", "moderate", "high"]
        check(gr["certainty_of_evidence"] == levels[max(0, len(levels) - 1 - total)],
              f"GRADE: {total} steps from high does not give {gr['certainty_of_evidence']!r}")
        se_, sp_ = gr["summary_sensitivity"], gr["summary_specificity"]
        primary_biv = next(r for r in biv if r["analysis"].startswith("one estimate per study"))
        check(abs(se_ - float(primary_biv["summary_sensitivity"])) < 1e-9
              and abs(sp_ - float(primary_biv["summary_specificity"])) < 1e-9,
              "GRADE: the operating point does not match the bivariate primary analysis")
        for row in gr["summary_of_findings"]:
            p_ = row["pre_test_probability"]
            d_, h_ = 1000.0 * p_, 1000.0 * (1 - p_)
            for key, want in (("true_positives_per_1000", se_ * d_),
                              ("false_negatives_per_1000", d_ - se_ * d_),
                              ("true_negatives_per_1000", sp_ * h_),
                              ("false_positives_per_1000", h_ - sp_ * h_)):
                check(abs(row[key] - round(want, 1)) < 0.05,
                      f"GRADE summary of findings at {p_}: {key} is {row[key]}, not {want:.1f}")
            tp, fp = row["true_positives_per_1000"], row["false_positives_per_1000"]
            check(abs(row["positive_predictive_value"] - tp / (tp + fp)) < 1e-3,
                  f"GRADE summary of findings at {p_}: PPV is not TP/(TP+FP)")

    # --- 8e. Mimic dosing feasibility ---------------------------------------
    # EN | Closed form throughout, so every published number is recomputed from the decay
    #      constants in the parameter table. Two properties are asserted as properties of
    #      the function rather than of this run: the peak-to-average ratio never drops
    #      below one, and a species that decays faster always pays a larger penalty at the
    #      same interval. A version that violated either would be wrong regardless of what
    #      the data said.
    # PT | Tudo em forma fechada, entao cada numero publicado e recalculado a partir das
    #      constantes de decaimento da tabela de parametros. Duas propriedades sao exigidas
    #      como propriedades da funcao e nao desta execucao: a razao pico sobre media nunca
    #      cai abaixo de um, e uma especie que decai mais rapido sempre paga penalidade
    #      maior no mesmo intervalo. Uma versao que violasse qualquer uma estaria errada
    #      independentemente do que os dados dissessem.
    try:
        dos = json.load(open(DOSING_JSON, encoding="utf-8"))
        dos_rows = list(csv.DictReader(open(DOSING_CSV, encoding="utf-8")))
    except FileNotFoundError:
        dos, dos_rows = None, None
    if dos is not None:
        ln2 = math.log(2.0)

        def p2a(d, T):
            x = d * T
            return 1.0 if x < 1e-9 else x / (1.0 - math.exp(-x))

        for name, rec in dos["decay_constants"].items():
            row = kin_by_id.get(rec["param_id"])
            check(row is not None and abs(float(row["value_si"]) - rec["decay_per_hour"]) < 1e-12,
                  f"dosing: {name} decay does not match {rec['param_id']}")
            check(abs(rec["half_life_hours"] - ln2 / rec["decay_per_hour"]) < 1e-9,
                  f"dosing: {name} half-life is not ln2 over its decay constant")
        for r in dos_rows:
            d = ln2 / float(r["half_life_hours"])
            T = float(r["dosing_interval_hours"])
            check(abs(float(r["peak_over_average"]) - p2a(d, T)) < 1e-3,
                  f"dosing {r['species']} at {T} h: peak/average is not dT/(1-exp(-dT))")
            check(abs(float(r["fraction_of_interval_above_half_peak"])
                      - min(1.0, (ln2 / d) / T)) < 1e-3,
                  f"dosing {r['species']} at {T} h: time above half peak is not one half-life")
            check(float(r["peak_over_average"]) >= 1.0,
                  f"dosing {r['species']}: a peak below the average is impossible")
        ref = dos["decay_constants"][dos["reference_species"]]["decay_per_hour"]
        for name, p in dos["daily_dosing_comparison"].items():
            d = ln2 / p["half_life_hours"]
            check(abs(p["peak_over_average_daily"] - p2a(d, 24.0)) < 1e-3,
                  f"dosing {name}: daily peak/average disagrees")
            check(abs(p["penalty_versus_reference"]
                      - p2a(d, 24.0) / p2a(ref, 24.0)) < 1e-3,
                  f"dosing {name}: the penalty is not its ratio to the reference")
            check(d > ref and p["penalty_versus_reference"] > 1.0,
                  f"dosing {name}: a species decaying faster than the reference must pay "
                  "a penalty above one")
            check(abs(p["fold_stabilisation_required"] - d / ref) < 1e-2,
                  f"dosing {name}: matching the reference at a fixed interval means "
                  "matching its decay constant, so the stabilisation is d/d_ref")

    # --- 8g. Mechanism animations recompute the same simulation ------------
    # EN | An animation is a movie of a simulation, and the only thing worth checking
    #      about it automatically is whether it is a movie of THIS simulation: its final
    #      frame has to land on the same numbers ode_calibrated_results.json and
    #      mimic_dosing_feasibility.json already carry. This does not open the GIF files
    #      - matplotlib figures are not meaningfully diffable - it recomputes the
    #      manifest scripts/19 wrote its numbers from and compares that manifest to the
    #      already-verified tables, the same one step removed from the pixels that every
    #      other figure check in this file uses.
    # PT | Uma animacao e o filme de uma simulacao, e a unica coisa que vale a pena
    #      conferir automaticamente nela e se e o filme DESTA simulacao: seu ultimo
    #      quadro tem de cair nos mesmos numeros que o ode_calibrated_results.json e o
    #      mimic_dosing_feasibility.json ja guardam. Isto nao abre os arquivos GIF -
    #      figuras do matplotlib nao sao comparaveis de forma significativa - recalcula
    #      o manifesto do qual o scripts/19 tirou seus numeros e compara esse manifesto
    #      as tabelas ja verificadas, o mesmo passo removido dos pixels que toda outra
    #      checagem de figura deste arquivo usa.
    try:
        anim = json.load(open(ANIM_JSON, encoding="utf-8"))
    except FileNotFoundError:
        anim = None
    if anim is not None and ode is not None:
        clr = ode["ad_clearance_vs_production"]
        check(abs(anim["ad_monomer_accumulation"]["ratio_AD_over_control"]
                  - clr["abeta_ratio_AD_over_control"]) < 1e-3,
              "animation manifest: AD/control ratio disagrees with ode_calibrated_results.json")

        wo = ode["mimic_washout"]
        m = anim["mimic_washout"]
        check(m["fast_species"] in wo and m["slow_species"] in wo,
              "animation manifest: washout species are not in ode_calibrated_results.json")
        if m["fast_species"] in wo and m["slow_species"] in wo:
            check(abs(m["fast_hours_to_baseline"]
                      - wo[m["fast_species"]]["hours_to_return_to_baseline"]) < 1e-3,
                  "animation manifest: fast-species washout time disagrees with the ODE table")
            check(abs(m["slow_hours_to_baseline"]
                      - wo[m["slow_species"]]["hours_to_return_to_baseline"]) < 1e-3,
                  "animation manifest: slow-species washout time disagrees with the ODE table")

    if anim is not None and dos is not None:
        d = anim["dosing_sawtooth"]
        mir7 = dos["daily_dosing_comparison"]["miR-7"]
        check(abs(d["peak_over_average_fast"] - mir7["peak_over_average_daily"]) < 1e-3,
              "animation manifest: fast-species peak/average disagrees with mimic_dosing_feasibility.json")
        check(abs(d["peak_over_average_slow"] - mir7["reference_peak_over_average_daily"]) < 1e-3,
              "animation manifest: reference peak/average disagrees with mimic_dosing_feasibility.json")
        check(abs(d["penalty_ratio"] - mir7["penalty_versus_reference"]) < 1e-3,
              "animation manifest: penalty ratio disagrees with mimic_dosing_feasibility.json")

    anim_stems = ("anim_ad_monomer", "anim_mimic_washout", "anim_dosing_sawtooth")
    for stem in anim_stems:
        for lang in ("en", "pt-BR"):
            fp = f"results/figures/{stem}.{lang}.gif"
            claim(os.path.isfile(fp), f"animation: {fp} is missing")

    # EN | The structure story panel composites scripts/13's own renders and fails loudly
    #      at generation time (missing provenance, missing PNG) rather than at check time,
    #      matching scripts/13's own stance that these figures are illustration, not a
    #      result, and so carry a lighter checking bar than a quantitative table. All
    #      scripts/08 confirms is that the composite was actually produced.
    # PT | O painel estrutural composto reaproveita os renders do proprio scripts/13 e
    #      falha alto na geracao (proveniencia ou PNG faltando), nao na checagem, no mesmo
    #      espirito do proprio scripts/13 de que essas figuras sao ilustracao, nao
    #      resultado, e por isso carregam uma barra de checagem mais leve que uma tabela
    #      quantitativa. Tudo que o scripts/08 confirma e que o composto foi de fato
    #      produzido.
    for lang in ("en", "pt-BR"):
        fp = f"results/figures/structure_story_panel.{lang}.png"
        claim(os.path.isfile(fp), f"structure story panel: {fp} is missing")

    # --- 8f. The corpus holds each article once ----------------------------
    # EN | Deduplication happens in scripts/09 and is easy to break silently: reading the
    #      DOI under one spelling while the corpus stores it under another leaves the
    #      DOI check inert, and the corpus grows a second copy of an article whose title
    #      two databases typeset differently. That is exactly what happened, and nothing
    #      noticed until a record count moved for an unrelated reason. The corpus is the
    #      denominator of every screening count, so its uniqueness is checked here rather
    #      than trusted to the code that builds it.
    # PT | A deduplicacao acontece no scripts/09 e quebra em silencio com facilidade: ler
    #      o DOI numa grafia enquanto o corpus o guarda em outra deixa a checagem de DOI
    #      inerte, e o corpus ganha uma segunda copia de um artigo cujo titulo duas bases
    #      compoem de forma diferente. Foi exatamente o que ocorreu, e nada percebeu ate
    #      uma contagem se mexer por outro motivo. O corpus e o denominador de toda
    #      contagem de triagem, entao sua unicidade e conferida aqui, e nao confiada ao
    #      codigo que o monta.
    try:
        corpus = json.load(open(CORPUS, encoding="utf-8"))
    except FileNotFoundError:
        corpus = None
    if corpus:
        by_doi, by_title = {}, {}
        for key, art in corpus.items():
            doi = str(art.get("DOI") or art.get("doi") or "").strip().lower()
            doi = re.sub(r"^https?://(dx\.)?doi\.org/", "", doi)
            if doi:
                by_doi.setdefault(doi, []).append(key)
            t = re.sub(r"[^a-z0-9]+", "", str(art.get("title") or art.get("Title") or "").lower())
            if t:
                by_title.setdefault(t, []).append(key)
        dup_doi = {d: k for d, k in by_doi.items() if len(k) > 1}
        dup_title = {t: k for t, k in by_title.items() if len(k) > 1}
        check(not dup_doi,
              f"corpus: {len(dup_doi)} DOI(s) appear on more than one record, so the same "
              f"article is counted twice: {list(dup_doi.items())[:3]}")
        check(not dup_title,
              f"corpus: {len(dup_title)} normalised title(s) appear on more than one "
              f"record: {list(dup_title.items())[:3]}")

    # --- 9. Clinical trial landscape --------------------------------------
    nd = trials["neurodegeneration_specific"]
    check(nd["mirna_directed_therapeutic_trials"] == 0,
          "trials: the zero-in-AD/PD claim no longer matches the data")
    check(len(trials["therapeutic_trials_all_indications"]) > 0,
          "trials: therapeutic trial list is empty")

    # --- 9b. A prose claim about a scanned range must match the scan -------
    # EN | The methods prose once said the required BACE1 knockdown was "19-33%",
    #      copied from before d_mRNA was measured (K068) and the free-parameter grid
    #      narrowed. Nothing recomputed it when the grid changed, and it sat wrong in
    #      both language files. It is corrected here and pinned to the JSON, exactly as
    #      the README's own numbers were pinned in section 10 below: the whole point of
    #      writing the range into ode_calibrated_results.json was so a sentence quoting
    #      it could be checked instead of trusted.
    # PT | A prosa dos metodos dizia "19-33%" para a queda de BACE1 necessaria, copiada
    #      de antes de o d_mRNA ser medido (K068) e a grade de parametros livres se
    #      estreitar. Nada recalculou quando a grade mudou, e o texto ficou errado nos
    #      dois idiomas. E corrigido aqui e preso ao JSON, exatamente como os numeros do
    #      README sao presos na secao 10 abaixo: o motivo de escrever a faixa em
    #      ode_calibrated_results.json era justamente poder conferir uma frase que a cita,
    #      em vez de confiar nela.
    if ode is not None and "mimic_dose_vs_measured_knockdown" in ode:
        lo, hi = ode["mimic_dose_vs_measured_knockdown"]["BACE1_knockdown_at_required_mimic"]
        expect = f"{math.floor(lo * 100):.0f}\u2013{round(hi * 100):.0f}%"
        anchor = {"docs/en/METHODS.md": "knockdown needed to offset",
                  "docs/pt-BR/METODOS.md": "queda de BACE1 necess\u00e1ria"}
        for name, needle in anchor.items():
            try:
                text = open(name, encoding="utf-8").read()
            except FileNotFoundError:
                continue
            claim(needle in text, f"{name}: the sentence this check anchors to is gone; "
                                  "update the anchor before trusting its pass")
            claim(expect in text,
                  f"{name}: does not quote the current BACE1-knockdown range {expect} "
                  f"computed from {ODE_RESULTS}")

    # --- 10. The README has to describe the repository it ships with ------
    # EN | Two numbers in the README are claims about this file and about the corrections
    #      table below them, and both were found stale once: the check count said 1374
    #      while 1627 checks ran, and the prose said three defects above a table of five.
    #      A count that is asserted in prose and computed nowhere is a count that drifts,
    #      so both are recomputed here and the README is required to agree.
    # PT | Dois numeros do README sao afirmacoes sobre este arquivo e sobre a tabela de
    #      correcoes logo abaixo deles, e os dois ja foram encontrados desatualizados: a
    #      contagem de verificacoes dizia 1374 enquanto 1627 rodavam, e o texto dizia tres
    #      defeitos acima de uma tabela de cinco. Um numero afirmado em prosa e calculado
    #      em lugar nenhum e um numero que deriva, entao ambos sao recalculados aqui e o
    #      README tem de concordar.
    readmes = [("README.md", "| Defect | Effect | Fixed in |",
                "{n} checks currently pass.",
                ("Five", "defects in this pipeline were found")),
               ("README.pt-BR.md", "| Defeito | Efeito | Corrigido em |",
                "Atualmente {n} verificacoes passam.",
                ("Cinco", "defeitos deste pipeline foram encontrados"))]
    spelled = {1: ("One", "Um"), 2: ("Two", "Dois"), 3: ("Three", "Tres"),
               4: ("Four", "Quatro"), 5: ("Five", "Cinco"), 6: ("Six", "Seis"),
               7: ("Seven", "Sete"), 8: ("Eight", "Oito"), 9: ("Nine", "Nove"),
               10: ("Ten", "Dez"), 11: ("Eleven", "Onze"), 12: ("Twelve", "Doze"),
               13: ("Thirteen", "Treze"), 14: ("Fourteen", "Catorze"),
               15: ("Fifteen", "Quinze"), 16: ("Sixteen", "Dezesseis"),
               17: ("Seventeen", "Dezessete"), 18: ("Eighteen", "Dezoito"),
               19: ("Nineteen", "Dezenove"), 20: ("Twenty", "Vinte")}
    for idx, (name, header, count_claim, _) in enumerate(readmes):
        try:
            text = open(name, encoding="utf-8").read()
        except FileNotFoundError:
            continue
        # EN/PT: the corrections table runs from its header to the first blank line
        body = text.split(header, 1)[1].split("\n\n", 1)[0] if header in text else ""
        rows = [ln for ln in body.splitlines()
                if ln.startswith("| ") and not ln.startswith("|---")]
        claim(len(rows) > 0, f"{name}: the corrections table was not found")
        # EN/PT: past the table, say so rather than silently passing an unchecked claim
        if len(rows) not in spelled:
            claim(False, f"{name}: the corrections table has {len(rows)} rows, which is "
                         "past the range this check can spell; extend `spelled`")
            continue
        word = spelled[len(rows)][idx]
        claim(word.lower() in text.lower(),
              f"{name}: the corrections table has {len(rows)} rows, so the prose above it "
              f"should say {word.lower()}, and it does not")
        # EN/PT: the asserted check count is a claim about this very run
        stated = count_claim.format(n=checks)
        stated_alt = stated.replace("verificacoes", "verificações")
        claim(stated in text or stated_alt in text,
              f"{name}: the README claims a different number of checks than the "
              f"{checks} that just ran")

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
