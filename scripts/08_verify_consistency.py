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
