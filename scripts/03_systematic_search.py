#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EN | Reproduce the PICO-driven systematic searches for the diagnostic-accuracy
     review of circulating microRNAs in Alzheimer's and Parkinson's disease.
PT | Reproduz as buscas sistematicas orientadas por PICO para a revisao de
     acuracia diagnostica de microRNAs circulantes em Alzheimer e Parkinson.

EN | Runs both search arms against the NCBI E-utilities API, downloads every
     record's metadata, and writes the search strategy plus the raw corpus to
     data/raw/systematic_review_2026/. Requires outbound access to NCBI.
PT | Executa os dois bracos de busca na API E-utilities do NCBI, baixa os
     metadados de cada registro e grava a estrategia de busca e o corpus bruto
     em data/raw/systematic_review_2026/. Exige acesso de rede ao NCBI.

    python scripts/03_systematic_search.py --email you@example.org

EN | The counts reported in the manuscript were obtained on 2026-09-10. PubMed
     grows daily, so re-running this later will legitimately return more
     records; the stored search_strategy.json preserves the frozen counts.
PT | As contagens do manuscrito foram obtidas em 2026-09-10. O PubMed cresce
     diariamente, entao reexecutar depois retornara, legitimamente, mais
     registros; o search_strategy.json guardado preserva as contagens congeladas.
"""

import argparse
import json
import os
import time
import datetime

OUT_DIR = "data/raw/systematic_review_2026"

# EN | The two search arms, verbatim as submitted to PubMed.
# PT | Os dois bracos de busca, textualmente como submetidos ao PubMed.
MIRNA_BLOCK = ('(microRNA[Title/Abstract] OR miRNA[Title/Abstract] OR '
               'microRNAs[Title/Abstract] OR miRNAs[Title/Abstract])')
FLUID_BLOCK = ('(plasma[Title/Abstract] OR serum[Title/Abstract] OR '
               '"cerebrospinal fluid"[Title/Abstract] OR CSF[Title/Abstract] OR '
               'blood[Title/Abstract] OR exosome[Title/Abstract] OR '
               'exosomal[Title/Abstract] OR "extracellular vesicle"[Title/Abstract])')
ACCURACY_BLOCK = ('(ROC[Title/Abstract] OR "area under the curve"[Title/Abstract] OR '
                  'AUC[Title/Abstract] OR sensitivity[Title/Abstract] OR '
                  'specificity[Title/Abstract] OR "diagnostic accuracy"[Title/Abstract] OR '
                  '"diagnostic value"[Title/Abstract])')

ARMS = {
    "AD_diagnostic_accuracy": f'{MIRNA_BLOCK} AND (Alzheimer[Title/Abstract]) AND {FLUID_BLOCK} AND {ACCURACY_BLOCK}',
    "PD_diagnostic_accuracy": f'{MIRNA_BLOCK} AND (Parkinson[Title/Abstract]) AND {FLUID_BLOCK} AND {ACCURACY_BLOCK}',
}

DATE_FROM = "2015/01/01"


def run_arm(Entrez, Medline, name, query, date_to):
    term = f'{query} AND ("{DATE_FROM}"[PDAT] : "{date_to}"[PDAT])'
    handle = Entrez.esearch(db="pubmed", term=term, retmax=10000, usehistory="y")
    res = Entrez.read(handle)
    handle.close()
    pmids = list(res["IdList"])
    print(f"[{name}] total in PubMed / total no PubMed: {res['Count']}  "
          f"retrieved / recuperados: {len(pmids)}")
    return dict(query=query, term_submitted=term, date_from=DATE_FROM,
                date_to=date_to, total_count=int(res["Count"]),
                retrieved=len(pmids), pmids=pmids)


def fetch_records(Entrez, Medline, pmids, batch=200):
    out = []
    for i in range(0, len(pmids), batch):
        chunk = pmids[i:i + batch]
        h = Entrez.efetch(db="pubmed", id=",".join(chunk), rettype="medline", retmode="text")
        for rec in Medline.parse(h):
            out.append({
                "PMID": rec.get("PMID", ""),
                "DOI": next((x.split()[0] for x in rec.get("AID", []) if "doi" in x.lower()), ""),
                "Title": rec.get("TI", ""),
                "Abstract": rec.get("AB", ""),
                "Journal": rec.get("JT", ""),
                "Year": rec.get("DP", "").split()[0] if rec.get("DP") else "",
                "Authors": "; ".join(rec.get("AU", [])),
                "PublicationTypes": "; ".join(rec.get("PT", [])),
                "MeSH": "; ".join(rec.get("MH", [])),
                "PMC": rec.get("PMC", ""),
            })
        h.close()
        time.sleep(0.4)  # EN/PT: courtesy to NCBI | cortesia ao NCBI
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--email", required=True,
                    help="EN: e-mail required by NCBI | PT: e-mail exigido pelo NCBI")
    ap.add_argument("--api-key", default=None)
    ap.add_argument("--date-to", default=datetime.date.today().strftime("%Y/%m/%d"))
    args = ap.parse_args()

    from Bio import Entrez, Medline
    Entrez.email = args.email
    if args.api_key:
        Entrez.api_key = args.api_key

    os.makedirs(OUT_DIR, exist_ok=True)
    strategy = {"search_date": args.date_to,
                "source": "PubMed/MEDLINE via NCBI E-utilities",
                "searches": {}}
    all_records = {}

    for name, query in ARMS.items():
        arm = run_arm(Entrez, Medline, name, query, args.date_to)
        strategy["searches"][name] = arm
        for rec in fetch_records(Entrez, Medline, arm["pmids"]):
            all_records[rec["PMID"]] = rec

    strategy["deduplicated_records"] = len(all_records)
    json.dump(strategy, open(f"{OUT_DIR}/search_strategy_rerun.json", "w"),
              indent=1, ensure_ascii=False)
    json.dump(all_records, open(f"{OUT_DIR}/screening_corpus.json", "w"),
              indent=1, ensure_ascii=False)

    print(f"\nEN | unique records after deduplication : {len(all_records)}")
    print(f"PT | registros unicos apos deduplicacao  : {len(all_records)}")
    print(f"EN/PT -> {OUT_DIR}/search_strategy_rerun.json, {OUT_DIR}/screening_corpus.json")


if __name__ == "__main__":
    main()
