#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EN | Sensitivity of the primary AD pool to a study that entered PubMed after the search date.

     An update of the PubMed search on 28 September 2026 (entry dates 10 to 28 September)
     found one further eligible AD study, available as an abstract only
     (data/extracted/post_search_candidates.csv). The primary analysis keeps the search
     dates stated in the Methods. This script adds the new study to the primary AD selection,
     once with each of its two assay variants (they are measurements of the same participants,
     so at most one enters a pool), and reports how far the pooled AUC moves.

     python scripts/31_post_search_sensitivity.py

PT | Sensibilidade do pool primario de DA a um estudo que entrou no PubMed apos a data da busca.

     Uma atualizacao da busca no PubMed em 28 de setembro de 2026 (datas de entrada de 10 a 28
     de setembro) encontrou mais um estudo elegivel de DA, disponivel so como resumo
     (data/extracted/post_search_candidates.csv). A analise primaria mantem as datas de busca
     dos Metodos. Este script acrescenta o novo estudo a selecao primaria de DA, uma vez com
     cada uma de suas duas variantes de ensaio (sao medidas dos mesmos participantes, entao
     no maximo uma entra num pool), e reporta quanto a AUC agregada se move.
"""

import csv
import importlib.util
import os
import sys

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("meta05", os.path.join(HERE, "05_meta_analysis.py"))
m05 = importlib.util.module_from_spec(spec)
sys.modules["meta05"] = m05
spec.loader.exec_module(m05)

POST = "data/extracted/post_search_candidates.csv"
OUT = "results/tables/post_search_sensitivity.csv"


def main():
    _, _, _, _, pool = m05.load_estimates(ci_plausibility=True)
    ad = pool[pool["disease"] == "AD"].copy()
    post = pd.read_csv(POST)
    rows = []
    base = m05.summarise_primary("AD primary pool", ad)
    rows.append(dict(analysis="AD primary pool (search dates in the Methods)", **{k: base[k] for k in
                     ("n_studies", "pooled_auc", "ci_low_hk", "ci_high_hk", "I2_percent")}))
    for _, p in post.iterrows():
        add = ad.iloc[[0]].copy()
        for c in add.columns:
            add[c] = None
        add["study_id"] = str(p["pmid"])
        add["disease"] = p["disease"]
        add["biofluid"] = p["biofluid"]
        add["marker_type"] = p["marker_type"]
        add["marker"] = p["marker"]
        add["cohort_stage"] = p["cohort_stage"]
        add["auc"] = float(p["auc"])
        add["se_auc"] = m05.se_hanley_mcneil(float(p["auc"]), float(p["n_cases"]), float(p["n_controls"]))
        add["first_author"] = p["first_author"]
        add["year"] = p["year"]
        add["n_cases"] = p["n_cases"]
        add["n_controls"] = p["n_controls"]
        add["eligible_primary_pool"] = "yes"
        s = m05.summarise_primary("AD primary pool plus post-search study", pd.concat([ad, add], ignore_index=True))
        rows.append(dict(analysis=f"AD primary pool plus Jeong 2026, {p['marker']}",
                         **{k: s[k] for k in ("n_studies", "pooled_auc", "ci_low_hk", "ci_high_hk", "I2_percent")}))
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    for r in rows:
        print(r)


if __name__ == "__main__":
    main()
