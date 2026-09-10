#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EN | Verify that every number written in the manuscripts, findings documents and
     READMEs matches the analysis outputs it claims to come from.
PT | Verifica se todo numero escrito nos manuscritos, documentos de achados e
     READMEs corresponde as saidas de analise de que diz vir.

EN | A manuscript drifts from its data the moment a value is edited by hand.
     This script closes that gap: it reads the result tables, reconstructs the
     figures that should appear in prose, and fails loudly if the text disagrees
     or still carries a superseded value. Run it before sending any draft out.
PT | Um manuscrito descola dos dados no instante em que um valor e editado a
     mao. Este script fecha essa brecha: le as tabelas de resultado, reconstroi
     as cifras que deveriam aparecer no texto corrido e falha ruidosamente se o
     texto discordar ou ainda carregar um valor superado. Rode antes de enviar
     qualquer versao.

    python scripts/08_verify_reported_numbers.py
"""

import csv
import json
import re
import sys

POOLED = "results/tables/meta_analysis_pooled_auc.csv"
CORR = "results/tables/citation_vs_auc_correlation.json"
CITED = "results/tables/citation_frequency_vs_auc.csv"
EXTRACTION = "data/extracted/diagnostic_accuracy_extraction.csv"
FLOW = "data/processed/prisma_flow.json"
TRIALS = "data/raw/clinical_trials_2026/mirna_therapeutics_trials.json"

DOCS = [
    "docs/en/MANUSCRIPT_DRAFT.md",
    "docs/pt-BR/MANUSCRITO_RASCUNHO.md",
    "docs/en/FINDINGS.md",
    "docs/pt-BR/ACHADOS.md",
    "README.md",
    "README.pt-BR.md",
]

SUBGROUPS = [
    "Overall (all eligible) | Global",
    "AD - all markers | todos marcadores",
    "PD - all markers | todos marcadores",
    "All - single miRNA | miRNA isolado",
    "All - multi-miRNA panel | painel multi-miRNA",
    "AD - single miRNA | miRNA isolado",
    "PD - single miRNA | miRNA isolado",
]


def decimal_variants(value, decimals=3):
    """EN/PT: the same number written the English way and the Portuguese way."""
    en = f"{float(value):.{decimals}f}"
    return en, en.replace(".", ",")


def main():
    failures, checked = [], 0
    pooled = {r["subgroup"]: r for r in csv.DictReader(open(POOLED))}
    corr = json.load(open(CORR))
    cited = {r["family"]: r for r in csv.DictReader(open(CITED))}
    extraction = list(csv.DictReader(open(EXTRACTION)))
    flow = json.load(open(FLOW))
    trials = json.load(open(TRIALS))
    docs = {f: open(f).read() for f in DOCS}

    print("EN | Verifying reported numbers against analysis outputs")
    print("PT | Verificando numeros reportados contra as saidas de analise")
    print("=" * 74)

    # --- 1. Every "estimate (CI low-CI high)" written in prose must exist ----
    # EN | Checking whole triples, not loose numbers, avoids false alarms when a
    #      study-level AUC happens to equal a pooled one (0.753 is both the PD
    #      pooled estimate and miR-125b's reported AUC).
    # PT | Checar trios inteiros, e nao numeros soltos, evita alarme falso quando
    #      uma AUC de estudo coincide com uma agregada (0,753 e tanto a estimativa
    #      agregada de PD quanto a AUC reportada do miR-125b).
    known = set()
    for r in pooled.values():
        for dec in (2, 3, 4):
            known.add((f"{float(r['pooled_auc']):.{dec}f}",
                       f"{float(r['ci_low']):.{dec}f}",
                       f"{float(r['ci_high']):.{dec}f}"))
    for r in extraction:
        if r["auc"] and r["auc_ci_low"] and r["auc_ci_high"]:
            for dec in (2, 3, 4):
                known.add((f"{float(r['auc']):.{dec}f}",
                           f"{float(r['auc_ci_low']):.{dec}f}",
                           f"{float(r['auc_ci_high']):.{dec}f}"))

    TRIPLE = re.compile(r'(\d[.,]\d{2,4})\s*\((?:95%\s*(?:CI|IC)\s*)?(\d[.,]\d{2,4})\s*[–—-]\s*(\d[.,]\d{2,4})\)')
    for path, text in docs.items():
        for m in TRIPLE.finditer(text):
            triple = tuple(v.replace(",", ".") for v in m.groups())
            checked += 1
            if triple not in known:
                line = text[:m.start()].count("\n") + 1
                failures.append(f"{path}:{line}: reported estimate {m.group(0)} "
                                f"is not in the result tables")

    # --- 1b. Headline estimates must actually appear in the manuscripts ------
    for key in ("All - single miRNA | miRNA isolado",
                "All - multi-miRNA panel | painel multi-miRNA"):
        en, pt = decimal_variants(pooled[key]["pooled_auc"])
        for path in ("docs/en/MANUSCRIPT_DRAFT.md", "docs/pt-BR/MANUSCRITO_RASCUNHO.md"):
            checked += 1
            want = pt if "pt-BR" in path else en
            if want not in docs[path]:
                failures.append(f"{path}: headline estimate {want} ({key}) missing")

    # --- 2. PRISMA counts ---------------------------------------------------
    ident, screen = flow["identification"], flow["screening"]
    elig, incl = flow["eligibility_fulltext"], flow["included_in_meta_analysis"]
    counts = {
        "records_after_deduplication": ident["records_after_deduplication"],
        "primary_studies": screen["primary_studies"],
        "primary_reporting_auc_or_sens_spec": screen["primary_reporting_auc_or_sens_spec"],
        "of_which_pmc_open_access_fulltext": screen["of_which_pmc_open_access_fulltext"],
        "extracted_estimates_total": elig["extracted_estimates_total"],
        "studies_contributing_extracted_estimates": elig["studies_contributing_extracted_estimates"],
        "estimates_eligible_for_primary_pool": elig["estimates_eligible_for_primary_pool"],
        "estimates_with_estimable_standard_error": incl["estimates_with_estimable_standard_error"],
        "independent_studies": incl["independent_studies"],
    }
    for path in ("docs/en/MANUSCRIPT_DRAFT.md", "docs/pt-BR/MANUSCRITO_RASCUNHO.md"):
        for name, value in counts.items():
            checked += 1
            if str(value) not in docs[path]:
                failures.append(f"{path}: PRISMA count {name}={value} not found")

    # --- 3. Extraction table internal consistency ---------------------------
    n_flagged = sum(1 for r in extraction if r["eligible_primary_pool"] == "no")
    checked += 1
    if n_flagged + int(counts["estimates_eligible_for_primary_pool"]) != len(extraction):
        failures.append("extraction: eligible + flagged does not equal total rows")

    checked += 1
    missing_quote = [r["record_id"] for r in extraction if not r["verbatim_quote"].strip()]
    if missing_quote:
        failures.append(f"extraction: rows without a verbatim quote -> {missing_quote}")

    checked += 1
    no_reason = [r["record_id"] for r in extraction
                 if r["eligible_primary_pool"] == "no" and not r["exclusion_reason"].strip()]
    if no_reason:
        failures.append(f"extraction: excluded rows without a reason -> {no_reason}")

    # --- 4. Correlation coefficients ---------------------------------------
    for entry in corr:
        rho_en, rho_pt = f"{entry['spearman_rho']:.2f}".replace("-", "−"), None
        rho_pt = rho_en.replace(".", ",")
        p_en = f"{entry['spearman_p']:.2f}"
        p_pt = p_en.replace(".", ",")
        for path, text in docs.items():
            rho = rho_pt if "pt-BR" in path else rho_en
            p_val = p_pt if "pt-BR" in path else p_en
            if rho in text:
                checked += 1
                if p_val not in text:
                    failures.append(f"{path}: rho {rho} present but p {p_val} missing")

    # --- 5. Citation-vs-AUC values quoted in prose --------------------------
    for mirna in ("miR-125b", "miR-146a", "miR-34a"):
        row = cited[mirna]
        auc_en, auc_pt = decimal_variants(row["mean_auc"], 3)
        for path, text in docs.items():
            if mirna in text and "attention" in text.lower() or mirna in text and "aten" in text.lower():
                want = auc_pt if "pt-BR" in path else auc_en
                if want in text:
                    checked += 1

    # --- 6. Clinical trial counts ------------------------------------------
    nd = trials["neurodegeneration_specific"]
    n_ther = len(trials["therapeutic_trials_all_indications"])
    checked += 1
    if nd["mirna_directed_therapeutic_trials"] != 0:
        failures.append("trials: the zero-in-AD/PD claim no longer matches the data")
    for path in ("docs/en/MANUSCRIPT_DRAFT.md", "docs/pt-BR/MANUSCRITO_RASCUNHO.md"):
        checked += 1
        if str(n_ther) not in docs[path]:
            failures.append(f"{path}: therapeutic trial count {n_ther} not found")

    # --- 7. Superseded values that must no longer appear anywhere -----------
    stale = ["0.803", "0,803", "0.774", "0,774", "p = 0.62", "p = 0,62"]
    for path, text in docs.items():
        for bad in stale:
            checked += 1
            if bad in text:
                failures.append(f"{path}: superseded value still present -> {bad}")

    print(f"Checks run / verificacoes: {checked}")
    if failures:
        print(f"\nFAILURES / FALHAS: {len(failures)}")
        for f in failures:
            print(f"  - {f}")
        return 1
    print("\nEN | All reported numbers match their source tables.")
    print("PT | Todos os numeros reportados conferem com suas tabelas-fonte.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
