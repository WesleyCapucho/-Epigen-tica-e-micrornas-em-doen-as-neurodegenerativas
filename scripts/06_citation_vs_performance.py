#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EN | Does how often a microRNA is talked about predict how well it actually
     performs as a diagnostic biomarker?
PT | A frequencia com que um microRNA e mencionado prediz o quanto ele de fato
     funciona como biomarcador diagnostico?

EN | This script confronts two independent quantities measured on the same
     corpus: (i) how many articles mention each miRNA in title/abstract, and
     (ii) the AUC each miRNA actually achieved in the primary studies that
     measured it. It is the quantitative answer to the circularity problem
     acknowledged in the source monograph: the most-cited miRNAs may simply be
     the most-studied ones, not the best-performing ones.
PT | Este script confronta duas quantidades independentes medidas no mesmo
     corpus: (i) quantos artigos mencionam cada miRNA em titulo/resumo e
     (ii) a AUC que cada miRNA de fato alcancou nos estudos primarios que o
     mediram. E a resposta quantitativa ao problema de circularidade admitido
     na monografia de origem: os miRNAs mais citados podem ser apenas os mais
     estudados, e nao os de melhor desempenho.

EN | Input : data/raw/systematic_review_2026/mirna_mention_counts.csv
             data/extracted/diagnostic_accuracy_extraction.csv
PT | Entrada: os mesmos arquivos acima.
"""

import os
import re
import json
import numpy as np
import pandas as pd
from scipy import stats
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

COUNTS = "data/raw/systematic_review_2026/mirna_mention_counts.csv"
EXTRACTION = "data/extracted/diagnostic_accuracy_extraction.csv"
TAB_DIR = "results/tables"
FIG_DIR = "results/figures"

MIRNA_RE = re.compile(
    r'\b(?:hsa[-‐‑])?(?:miR|let|mir)[-‐‑]\s?[0-9][0-9a-zA-Z]*'
    r'(?:[-‐‑][0-9a-z]+)*(?:[-‐‑][35]p)?\b')


def normalise(name):
    """EN/PT: canonical miRNA label (drop hsa- prefix, unify dashes and case)."""
    n = name.replace("‐", "-").replace("‑", "-").replace(" ", "")
    n = re.sub(r'^hsa-', '', n, flags=re.I)
    if n.lower().startswith("mir-"):
        n = "miR-" + n[4:]
    elif n.lower().startswith("let-"):
        n = "let-" + n[4:]
    return n


def build_counts_from_corpus(corpus_path, out_path):
    """EN | Count how many ARTICLES mention each miRNA (and each miRNA family) in
           title/abstract across the screened corpus. Counting distinct articles
           - not raw occurrences - keeps an article that writes both 'miR-125b'
           and 'miR-125b-5p' from being counted twice for that family.
       PT | Conta quantos ARTIGOS mencionam cada miRNA (e cada familia) em
           titulo/resumo no corpus triado. Contar artigos distintos, e nao
           ocorrencias, evita que um artigo que escreva 'miR-125b' e
           'miR-125b-5p' seja contado duas vezes para a mesma familia."""
    corpus = json.load(open(corpus_path))
    exact, fam = {}, {}
    for pmid, art in corpus.items():
        text = f"{art.get('title','')} {art.get('abstract','')}"
        found = {normalise(m) for m in MIRNA_RE.findall(text)}
        for m in found:
            exact.setdefault(m, set()).add(pmid)
        for f in {family(m) for m in found}:
            fam.setdefault(f, set()).add(pmid)

    rows = [{"mirna": m, "family": family(m),
             "n_articles_mentioning": len(pmids),
             "n_articles_mentioning_family": len(fam[family(m)])}
            for m, pmids in exact.items()]
    df = pd.DataFrame(rows).sort_values("n_articles_mentioning", ascending=False)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    df.to_csv(out_path, index=False)
    return df


def family(name):
    """EN | Collapse a miRNA to its family (miR-146a-5p -> miR-146a), so that a
           mention of 'miR-146a' can be matched to the arm 'miR-146a-5p'.
       PT | Reduz o miRNA a sua familia, para casar 'miR-146a' com 'miR-146a-5p'."""
    n = normalise(name)
    n = re.sub(r'-[35]p$', '', n)
    return n


def main():
    os.makedirs(TAB_DIR, exist_ok=True)
    os.makedirs(FIG_DIR, exist_ok=True)

    counts = pd.read_csv(COUNTS)
    # EN/PT: distinct-article count per family (already de-duplicated upstream)
    fam_counts = (counts.groupby("family", as_index=False)["n_articles_mentioning_family"]
                        .max()
                        .rename(columns={"n_articles_mentioning_family": "n_articles_mentioning"}))

    ext = pd.read_csv(EXTRACTION)
    ext = ext[(ext["marker_type"] == "single_miRNA")].copy()
    ext["auc"] = pd.to_numeric(ext["auc"], errors="coerce")
    ext = ext.dropna(subset=["auc"])
    ext["family"] = ext["marker"].map(family)

    # EN | Identify a study by its PMID when it has one and by its DOI
    #      otherwise. Grouping on PMID alone merged every study published
    #      outside MEDLINE into one blank-PMID bucket, so two independent
    #      cohorts reporting miR-124 collapsed into a single observation.
    # PT | Identifica o estudo pelo PMID quando existe e pelo DOI caso
    #      contrario. Agrupar so pelo PMID fundia todo estudo publicado fora do
    #      MEDLINE num unico balde de PMID vazio, e duas coortes independentes
    #      que reportam miR-124 viravam uma observacao so.
    pmid_txt = (ext["pmid"].astype(str).str.strip()
                .str.replace(r"\.0$", "", regex=True)
                .replace({"": np.nan, "nan": np.nan, "None": np.nan}))
    ext["study_id"] = pmid_txt.fillna(ext["doi"].astype(str).str.strip().str.lower())

    # EN: one estimate per miRNA per study (mean if a study reports several stages)
    # PT: uma estimativa por miRNA por estudo (media se o estudo reporta varias etapas)
    per_study = (ext.groupby(["family", "study_id"], as_index=False)
                    .agg(auc=("auc", "mean"),
                         eligible=("eligible_primary_pool", "first")))
    per_mirna = (per_study.groupby("family", as_index=False)
                          .agg(mean_auc=("auc", "mean"),
                               n_studies=("study_id", "nunique"),
                               max_auc=("auc", "max"),
                               min_auc=("auc", "min")))

    merged = per_mirna.merge(fam_counts, on="family", how="left")
    merged["n_articles_mentioning"] = merged["n_articles_mentioning"].fillna(0).astype(int)
    merged = merged.sort_values("n_articles_mentioning", ascending=False)
    merged.to_csv(f"{TAB_DIR}/citation_frequency_vs_auc.csv", index=False)

    print("=" * 78)
    print("EN | Literature attention vs measured diagnostic accuracy")
    print("PT | Atencao da literatura vs acuracia diagnostica medida")
    print("=" * 78)
    print(merged.to_string(index=False))

    def correlate(sub, label):
        if len(sub) < 4:
            return None
        xs = sub["n_articles_mentioning"].values.astype(float)
        ys = sub["mean_auc"].values.astype(float)
        rho, p_rho = stats.spearmanr(xs, ys)
        r, p_r = stats.pearsonr(xs, ys)
        print(f"\n[{label}]  n = {len(sub)} miRNAs")
        print(f"   Spearman rho = {rho:.3f} (p = {p_rho:.3f})    "
              f"Pearson r = {r:.3f} (p = {p_r:.3f})")
        return dict(analysis=label, n_mirnas=int(len(sub)),
                    spearman_rho=float(rho), spearman_p=float(p_rho),
                    pearson_r=float(r), pearson_p=float(p_r))

    # EN | Main analysis, then a sensitivity analysis restricted to the estimates
    #      that survived the primary-pool eligibility rules.
    # PT | Analise principal e, depois, analise de sensibilidade restrita as
    #      estimativas que passaram nos criterios de elegibilidade do pool.
    eligible_fams = set(per_study.loc[per_study["eligible"] == "yes", "family"])
    results = [correlate(merged, "all single-miRNA estimates | todas as estimativas"),
               correlate(merged[merged["family"].isin(eligible_fams)],
                         "eligible estimates only | apenas elegiveis")]
    results = [r for r in results if r]
    print("\nEN | Exploratory: most miRNAs contribute a single study, so the test is")
    print("     underpowered and a null result is not evidence of no association.")
    print("PT | Exploratorio: a maioria dos miRNAs contribui com um unico estudo,")
    print("     logo o teste tem baixo poder e um resultado nulo nao prova ausencia.")
    json.dump(results, open(f"{TAB_DIR}/citation_vs_auc_correlation.json", "w"), indent=1)

    x = merged["n_articles_mentioning"].values.astype(float)
    y = merged["mean_auc"].values.astype(float)

    # ---------------- figure | figura ----------------
    # EN | Filled = estimate eligible for the primary pool; open = flagged out
    #      (unstable, wrong comparator, population mismatch). Showing both, with
    #      the distinction visible, is more honest than hiding the flagged ones.
    # PT | Preenchido = estimativa elegivel para o pool primario; vazado =
    #      sinalizada fora (instavel, comparador errado, populacao divergente).
    #      Mostrar as duas, com a distincao visivel, e mais honesto que ocultar.
    fig, ax = plt.subplots(figsize=(8.6, 6.0))
    is_elig = merged["family"].isin(eligible_fams).values
    ax.scatter(x[is_elig], y[is_elig], s=68, color="#3B6EA5", alpha=0.9,
               edgecolor="white", zorder=3, label="eligible | elegivel")
    ax.scatter(x[~is_elig], y[~is_elig], s=68, facecolor="none",
               edgecolor="#3B6EA5", linewidth=1.4, zorder=3,
               label="flagged out | sinalizada fora")
    for i, (_, r_) in enumerate(merged.iterrows()):
        # EN/PT: alternate label side to reduce overlap in the dense region
        dx, ha = (7, "left") if i % 2 == 0 else (-7, "right")
        ax.annotate(r_["family"],
                    (r_["n_articles_mentioning"], r_["mean_auc"]),
                    textcoords="offset points", xytext=(dx, 4),
                    ha=ha, fontsize=7.4)
    ax.axhline(0.80, color="#B3541E", ls="--", lw=1.2, zorder=2)
    ax.text(ax.get_xlim()[1], 0.803, "AUC = 0.80", ha="right", fontsize=8, color="#B3541E")
    ax.set_xlabel("Articles mentioning the miRNA in the screened corpus\n"
                  "Artigos que mencionam o miRNA no corpus triado", fontsize=9)
    ax.set_ylabel("Mean reported AUC | AUC media reportada", fontsize=9)
    ax.set_title("Literature attention does not track diagnostic performance\n"
                 "Atencao da literatura nao acompanha o desempenho diagnostico",
                 fontsize=11)
    ax.legend(fontsize=8, frameon=False, loc="lower left")
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    fig.tight_layout()
    fig.savefig(f"{FIG_DIR}/citation_frequency_vs_auc.png", dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(f"\nEN: table -> {TAB_DIR}/citation_frequency_vs_auc.csv | figure -> {FIG_DIR}")
    print(f"PT: tabela -> {TAB_DIR}/citation_frequency_vs_auc.csv | figura -> {FIG_DIR}")


if __name__ == "__main__":
    main()
