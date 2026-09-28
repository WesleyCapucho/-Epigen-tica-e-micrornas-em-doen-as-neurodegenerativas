#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EN | Recall check for the abstract-based accuracy filter.

     The first screening kept, for full-text reading, only primary studies whose abstract
     mentioned an AUC, a sensitivity or a specificity. A study can report a ROC analysis in
     its full text without saying so in the abstract, and a comparison with the study list
     of an earlier Parkinson's disease meta-analysis showed that the filter had missed
     such studies. This script re-derives, from the screening decisions and the archived
     abstracts, the set of primary studies without an accuracy statement in the abstract
     that look like case-control studies of circulating microRNAs in AD or PD (the triage
     rule below), checks that set against data/extracted/recall_check_decisions.csv, which
     holds the full-text decision for each candidate, and writes the counts used in the PRISMA
     flow to results/tables/recall_check_summary.json.

     python scripts/30_recall_check.py

     The full-text decisions themselves were made by reading the PubMed Central full text of
     each candidate; they cannot be recomputed offline and are stored in the CSV with the
     sentence each one rests on. Candidates without an open full text could not be assessed
     and are listed as such.

PT | Verificacao de recall do filtro de acuracia no resumo.

     A primeira triagem levou a leitura de texto completo so os estudos primarios cujo
     resumo citava AUC, sensibilidade ou especificidade. Um estudo pode reportar uma
     analise ROC no texto completo sem dizer isso no resumo, e a comparacao com a lista de
     estudos de uma meta-analise anterior sobre doenca de Parkinson mostrou que o filtro
     tinha perdido estudos assim. Este script rederiva, das decisoes de triagem e dos
     resumos arquivados, o conjunto de estudos primarios sem afirmacao de acuracia no
     resumo que parecem estudos caso-controle de microRNAs circulantes na DA ou na DP
     (a regra de triagem abaixo), confere esse conjunto com
     data/extracted/recall_check_decisions.csv, que guarda a decisao de texto completo de
     cada candidato, e grava as contagens usadas no fluxo PRISMA em
     results/tables/recall_check_summary.json.
"""

import csv
import json
import re
import sys
from collections import Counter

DECISIONS = "data/raw/systematic_review_2026/screening_decisions.csv"
CORPUS = "data/raw/systematic_review_2026/screening_corpus.json"
RECALL = "data/extracted/recall_check_decisions.csv"
FLOW = "data/processed/prisma_flow.json"
OUT = "results/tables/recall_check_summary.json"

HUMAN = re.compile(r"patients|subjects|participants|cohort|individuals|healthy controls|case-control")
FLUID = re.compile(r"serum|plasma|blood|exosom|vesicle|peripheral")
MIRNA = re.compile(r"mirna|microrna|mir-|mir\d")
# EN/PT: titles that mark records outside the review question | titulos que marcam registros fora da pergunta
EXCLUDE = re.compile(
    r"cardiomyopathy|breast|multiple sclerosis|Creutzfeldt|bipolar|COVID|Nanotech|Database|Omic-Based|eQTL|"
    r"transfer learning|Drosophila|polymorphism|salivary|nasal|swab|tear fluid|cerebrospinal fluid|Picalm|"
    r"hazmat|circ_|circular|lncRNA|GAS5|LINC|bioinformatic|GEO Database|RBAD|Mitochondrial|CXCL8|"
    r"Neuroprotective|cell viability|Protective Role|inhibits|ameliorates|Microglial exosomes|leukocytes|"
    r"Protein binding|Role and Dysregulation|Circulating microRNAs as Promising|PBMC|Telomere|Multiomics|"
    r"Inflammation-related|repetitive transcranial|Identification of key|Integrative|prefrontal|GENFI|FTD|"
    r"Lewy bodies using|youth|Gene Signatures|Integrated", re.I)


def triage(decisions, corpus):
    cands = set()
    for r in decisions:
        if r["is_review_or_secondary"] != "no" or r["carries_quantitative_accuracy"] != "no":
            continue
        rec = corpus.get(r["pmid"]) or {}
        abstract = rec.get("abstract", "") if isinstance(rec, dict) else ""
        text = (r["title"] + " " + abstract).lower()
        if not (HUMAN.search(text) and FLUID.search(text) and MIRNA.search(text)):
            continue
        if EXCLUDE.search(r["title"]):
            continue
        cands.add(r["pmid"])
    return cands


def main():
    with open(DECISIONS, newline="", encoding="utf-8") as fh:
        decisions = list(csv.DictReader(fh))
    corpus = json.load(open(CORPUS, encoding="utf-8"))
    with open(RECALL, newline="", encoding="utf-8") as fh:
        recall = list(csv.DictReader(fh))

    derived = triage(decisions, corpus)
    stored = {r["record_key"] for r in recall if r["triage"] == "candidate"}
    n_no_acc = sum(1 for r in decisions
                   if r["is_review_or_secondary"] == "no" and r["carries_quantitative_accuracy"] == "no")
    problems = []
    if derived != stored:
        problems.append(f"triage rule gives {len(derived)} candidates, the stored file has {len(stored)}; "
                        f"difference {sorted(derived ^ stored)[:5]}")
    if len(recall) != n_no_acc:
        problems.append(f"recall file has {len(recall)} rows but {n_no_acc} primary studies lack an accuracy statement")

    cand = [r for r in recall if r["triage"] == "candidate"]
    dec = Counter(r["decision"] for r in cand)
    read = [r for r in cand if r["fulltext_read"] == "yes"]
    summary = {
        "records_without_accuracy_statement_in_abstract": len(recall),
        "judged_plausible_by_title_and_abstract": len(cand),
        "no_open_fulltext": dec["not_assessed_no_open_fulltext"],
        "fulltext_requested": len(cand) - dec["not_assessed_no_open_fulltext"],
        "fulltext_not_retrievable": dec["fulltext_unavailable"],
        "fulltext_read": len(read),
        "reports_with_eligible_estimates": dec["eligible"],
        "reports_with_accuracy_but_no_primary_estimate": dec["reports_accuracy_but_not_primary"],
        "reports_not_eligible": dec["not_eligible"],
    }
    flow = json.load(open(FLOW, encoding="utf-8"))["eligibility_fulltext"]["recall_check"]
    for k, v in summary.items():
        if flow.get(k) != v:
            problems.append(f"prisma_flow.json recall_check.{k}={flow.get(k)} but the decisions file gives {v}")
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(summary, fh, indent=1)
    print(json.dumps(summary, indent=1))
    if problems:
        for p in problems:
            print("PROBLEM:", p)
        sys.exit(1)


if __name__ == "__main__":
    main()
