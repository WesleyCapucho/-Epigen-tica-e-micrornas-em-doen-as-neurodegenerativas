#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EN | How far have microRNA-directed therapeutics actually travelled towards the
     clinic - and how far in Alzheimer's and Parkinson's disease specifically?
PT | Ate onde as terapias dirigidas a microRNA de fato chegaram na clinica - e
     ate onde, especificamente, na doenca de Alzheimer e na de Parkinson?

EN | The preclinical literature on miRNA mimics and antagomiRs in
     neurodegeneration is large; the source monograph itself simulated a
     miR-29c/miR-107 mimic therapy. This script asks the registry what actually
     reached human testing, which is the check that preclinical enthusiasm
     rarely gets subjected to.
PT | A literatura pre-clinica sobre mimeticos de miRNA e antagomiRs em
     neurodegeneracao e vasta; a propria monografia de origem simulou uma
     terapia com mimetico de miR-29c/miR-107. Este script pergunta ao registro
     o que de fato chegou a teste em humanos, checagem a que o entusiasmo
     pre-clinico raramente e submetido.

EN | Data source: ClinicalTrials.gov (U.S. National Library of Medicine),
     queried 2026-09-10. Results are stored in
     data/raw/clinical_trials_2026/mirna_therapeutics_trials.json
PT | Fonte de dados: ClinicalTrials.gov (U.S. National Library of Medicine),
     consultado em 10/09/2026. Resultados em
     data/raw/clinical_trials_2026/mirna_therapeutics_trials.json

EN | Caveat, stated rather than hidden: registry searches match on intervention
     names and free text. A trial that describes a miRNA-directed agent under a
     nomenclature none of the query terms covers would be missed. The queries
     used are recorded verbatim in the JSON so the search can be criticised and
     repeated.
PT | Ressalva, declarada e nao escondida: buscas no registro casam por nomes de
     intervencao e texto livre. Um ensaio que descreva um agente dirigido a
     miRNA sob nomenclatura que nenhum termo da query cobre passaria
     despercebido. As queries usadas estao registradas verbatim no JSON, para
     que a busca possa ser criticada e repetida.
"""

import json
import os
import pandas as pd

IN_JSON = "data/raw/clinical_trials_2026/mirna_therapeutics_trials.json"
TAB_DIR = "results/tables"


def main():
    os.makedirs(TAB_DIR, exist_ok=True)
    data = json.load(open(IN_JSON))

    trials = pd.DataFrame(data["therapeutic_trials_all_indications"])
    trials.to_csv(f"{TAB_DIR}/mirna_therapeutic_trials.csv", index=False)

    print("=" * 78)
    print("EN | miRNA-directed therapeutics in registered clinical trials")
    print("PT | Terapias dirigidas a miRNA em ensaios clinicos registrados")
    print("=" * 78)
    print(f"Trials matching the therapeutic query / ensaios encontrados: {len(trials)}")
    print(f"Distinct agents / agentes distintos: {trials['agent'].nunique()}")
    print()
    by_area = (trials.groupby("therapeutic_area")
                     .agg(trials=("nct_id", "count"),
                          agents=("agent", lambda s: ", ".join(sorted(set(s)))))
                     .sort_values("trials", ascending=False))
    print(by_area.to_string())

    print("\nEN | Furthest phase reached, by agent | PT | Fase maxima, por agente")
    order = {"PHASE1": 1, "PHASE1/PHASE2": 1.5, "PHASE2": 2, "PHASE3": 3, "NA": 0}
    ag = (trials.assign(rank=trials["phase"].map(lambda p: order.get(p, 0)))
                .groupby("agent")
                .agg(target=("mirna_target", "first"),
                     max_phase=("phase", lambda s: max(s, key=lambda p: order.get(p, 0))),
                     n_trials=("nct_id", "count"),
                     any_terminated=("status", lambda s: any(x in ("TERMINATED", "WITHDRAWN") for x in s)))
                .sort_values("n_trials", ascending=False))
    print(ag.to_string())

    nd = data["neurodegeneration_specific"]
    print("\n" + "=" * 78)
    print("EN | In Alzheimer's / Parkinson's disease specifically")
    print("PT | Especificamente em Alzheimer / Parkinson")
    print("=" * 78)
    print(f"Trials mentioning miRNA in AD/PD / ensaios mencionando miRNA em AD/PD: "
          f"{nd['trials_mentioning_mirna_in_AD_or_PD']}")
    print(f"  of which observational-biomarker / dos quais observacionais-biomarcador: "
          f"{nd['of_which_observational_or_biomarker']}")
    print(f"  miRNA-DIRECTED THERAPEUTIC trials / ensaios TERAPEUTICOS dirigidos a miRNA: "
          f"{nd['mirna_directed_therapeutic_trials']}")
    print()
    for line in nd["interventional_non_mirna_agents"]:
        print(f"  - {line}")
    print(f"\nEN | {nd['conclusion_en']}")
    print(f"PT | {nd['conclusion_pt']}")
    print(f"\nEN/PT -> {TAB_DIR}/mirna_therapeutic_trials.csv")


if __name__ == "__main__":
    main()
