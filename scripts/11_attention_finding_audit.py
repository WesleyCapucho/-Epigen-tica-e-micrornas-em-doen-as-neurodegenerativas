#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EN | Audit the attention-versus-performance correlation: what made it move.
PT | Auditoria da correlacao atencao-versus-desempenho: o que a deslocou.

EN | An earlier version of this project reported Spearman rho = -0.61
     (p = 0.012) between how often a miRNA is discussed and how well it
     performs, and called it the one finding with no clear precedent. Two
     later corrections dissolved it, and rather than quietly restate the new
     number this script separates their contributions so a reader can see
     exactly which change did what.
PT | Uma versao anterior deste projeto reportou rho de Spearman = -0,61
     (p = 0,012) entre quanto um miRNA e discutido e quao bem ele desempenha, e
     chamou isso do unico achado sem precedente claro. Duas correcoes
     posteriores o dissolveram e, em vez de simplesmente reescrever o numero,
     este script separa as contribuicoes de cada uma para que o leitor veja
     exatamente qual mudanca fez o que.

EN | The two corrections:
     1. Mention counts were being taken over the 234 PubMed records while the
        AUCs already came from the PubMed-plus-Scopus corpus. Every marker that
        entered through Scopus was credited with zero mentions by construction,
        which is an artefact of mismatched denominators.
     2. The Scopus Parkinson arm added 26 extracted estimates, including eight
        low-AUC markers with little literature attention.
PT | As duas correcoes:
     1. As contagens de mencao vinham dos 234 registros do PubMed enquanto as
        AUCs ja vinham do corpus PubMed-mais-Scopus. Todo marcador que entrou
        pelo Scopus recebia zero mencoes por construcao, o que e artefato de
        denominadores incompativeis.
     2. O braco Parkinson do Scopus somou 26 estimativas extraidas, entre elas
        oito marcadores de AUC baixa e pouca atencao na literatura.

    python scripts/11_attention_finding_audit.py
"""

import os
import re
import subprocess
import sys

import numpy as np
import pandas as pd
from scipy import stats

# EN/PT: the commit that carries the superseded inputs, as published
BASELINE_COMMIT = "e46a1ec"
COUNTS = "data/raw/systematic_review_2026/mirna_mention_counts.csv"
EXTRACTION = "data/extracted/diagnostic_accuracy_extraction.csv"
OUT = "results/tables/attention_correlation_audit.csv"
TMP = "results/.audit_baseline"


def normalise(name):
    n = name.replace("‐", "-").replace("‑", "-").replace(" ", "")
    n = re.sub(r'^hsa-', '', n, flags=re.I)
    if n.lower().startswith("mir-"):
        n = "miR-" + n[4:]
    elif n.lower().startswith("let-"):
        n = "let-" + n[4:]
    return n


def family(name):
    return re.sub(r'-[35]p$', '', normalise(name))


def from_git(path, dest):
    """EN/PT: recover a superseded input from the baseline commit."""
    try:
        blob = subprocess.check_output(["git", "show", f"{BASELINE_COMMIT}:{path}"],
                                       stderr=subprocess.DEVNULL)
    except subprocess.CalledProcessError:
        return None
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    open(dest, "wb").write(blob)
    return dest


def correlate(counts_path, ext_path, study_id):
    """
    EN | Recompute the correlation for one combination of inputs.
    PT | Recalcula a correlacao para uma combinacao de entradas.
    """
    counts = pd.read_csv(counts_path)
    fam_counts = (counts.groupby("family", as_index=False)["n_articles_mentioning_family"]
                        .max()
                        .rename(columns={"n_articles_mentioning_family": "n_articles_mentioning"}))
    ext = pd.read_csv(ext_path)
    ext = ext[ext["marker_type"] == "single_miRNA"].copy()
    ext["auc"] = pd.to_numeric(ext["auc"], errors="coerce")
    ext = ext.dropna(subset=["auc"])
    ext["family"] = ext["marker"].map(family)
    if study_id:
        pm = (ext["pmid"].astype(str).str.strip().str.replace(r"\.0$", "", regex=True)
              .replace({"": np.nan, "nan": np.nan, "None": np.nan}))
        ext["gid"] = pm.fillna(ext["doi"].astype(str).str.strip().str.lower())
    else:
        ext["gid"] = ext["pmid"]

    per_study = (ext.groupby(["family", "gid"], as_index=False)
                    .agg(auc=("auc", "mean"), eligible=("eligible_primary_pool", "first")))
    out = {}
    for lab, d in (("all", per_study.groupby("family", as_index=False).agg(mean_auc=("auc", "mean"))),
                   ("eligible", per_study[per_study["eligible"] == "yes"]
                    .groupby("family", as_index=False).agg(mean_auc=("auc", "mean")))):
        m = d.merge(fam_counts, on="family", how="left")
        m["n_articles_mentioning"] = m["n_articles_mentioning"].fillna(0)
        rho, p = stats.spearmanr(m["n_articles_mentioning"], m["mean_auc"])
        out[lab] = (len(m), rho, p)
    return out


def main():
    old_counts = from_git(COUNTS, f"{TMP}/mirna_mention_counts.csv")
    old_ext = from_git(EXTRACTION, f"{TMP}/diagnostic_accuracy_extraction.csv")
    if not old_counts or not old_ext:
        sys.exit(f"EN/PT: cannot read the baseline inputs from commit {BASELINE_COMMIT}")

    scenarios = [
        ("A. as published | como publicado: PubMed-only counts + pre-PD extraction",
         old_counts, old_ext, False),
        ("B. mention-count denominator fixed | denominador corrigido",
         COUNTS, old_ext, False),
        ("C. Scopus PD arm added only | so o braco PD do Scopus",
         old_counts, EXTRACTION, True),
        ("D. current | atual: both corrections | ambas as correcoes",
         COUNTS, EXTRACTION, True),
    ]

    rows = []
    for lab, c, e, sid in scenarios:
        r = correlate(c, e, sid)
        rows.append({
            "scenario": lab,
            "n_mirnas_all": r["all"][0],
            "rho_all": round(r["all"][1], 3),
            "p_all": round(r["all"][2], 3),
            "n_mirnas_eligible": r["eligible"][0],
            "rho_eligible": round(r["eligible"][1], 3),
            "p_eligible": round(r["eligible"][2], 3),
        })

    df = pd.DataFrame(rows)
    os.makedirs("results/tables", exist_ok=True)
    df.to_csv(OUT, index=False)
    print("=" * 78)
    print("EN | What moved the attention-versus-performance correlation")
    print("PT | O que deslocou a correlacao atencao-versus-desempenho")
    print("=" * 78)
    print(df.to_string(index=False))
    print(f"\nEN/PT -> {OUT}")
    print("\nEN | Read: either correction alone weakens the association; together")
    print("     it is gone. The published -0.61 does not survive its own inputs.")
    print("PT | Leitura: cada correcao sozinha enfraquece a associacao; juntas,")
    print("     ela desaparece. O -0,61 publicado nao sobrevive as proprias entradas.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
