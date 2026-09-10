#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EN | Random-effects meta-analysis of the diagnostic accuracy (AUC) of circulating
     microRNAs in Alzheimer's disease (AD) and Parkinson's disease (PD).

PT | Meta-analise de efeitos aleatorios da acuracia diagnostica (AUC) de
     microRNAs circulantes na doenca de Alzheimer (AD) e de Parkinson (PD).

EN | Input : data/extracted/diagnostic_accuracy_extraction.csv
     Output: results/tables/*.csv, results/figures/*.png
PT | Entrada: data/extracted/diagnostic_accuracy_extraction.csv
     Saida  : results/tables/*.csv, results/figures/*.png

EN | Method. Standard errors come from the reported 95% CI when the source
     article published one, otherwise from Hanley & McNeil (1982) using the
     case and control group sizes. AUCs are pooled on the logit scale with the
     DerSimonian & Laird (1986) random-effects estimator and back-transformed.
     Heterogeneity is reported as Cochran's Q, tau-squared and I-squared;
     small-study effects are assessed with Egger's regression test.
PT | Metodo. Os erros-padrao vem do IC 95% publicado quando o artigo-fonte o
     reporta; caso contrario, sao calculados por Hanley & McNeil (1982) a partir
     dos tamanhos dos grupos caso e controle. As AUCs sao agregadas na escala
     logito pelo estimador de efeitos aleatorios de DerSimonian & Laird (1986) e
     retrotransformadas. A heterogeneidade e reportada como Q de Cochran, tau^2
     e I^2; efeitos de estudos pequenos sao avaliados pelo teste de Egger.

EN | No value is simulated: every AUC, sample size and confidence interval comes
     from the extraction table, which stores the verbatim sentence of the source.
PT | Nenhum valor e simulado: toda AUC, tamanho amostral e intervalo de confianca
     vem da tabela de extracao, que guarda a frase verbatim da fonte.
"""

import os
import numpy as np
import pandas as pd
from scipy import stats
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

IN_CSV = "data/extracted/diagnostic_accuracy_extraction.csv"
TAB_DIR = "results/tables"
FIG_DIR = "results/figures"


# --------------------------------------------------------------------------
# EN | Standard error of an AUC | PT | Erro-padrao de uma AUC
# --------------------------------------------------------------------------
def se_from_ci(low, high):
    """EN: SE from a symmetric 95% CI. | PT: EP a partir de IC 95% simetrico."""
    if pd.isna(low) or pd.isna(high):
        return np.nan
    return (high - low) / (2 * 1.959964)


def se_hanley_mcneil(auc, n_cases, n_controls):
    """EN/PT: Hanley & McNeil (1982), Radiology 143:29-36."""
    if pd.isna(auc) or pd.isna(n_cases) or pd.isna(n_controls):
        return np.nan
    if n_cases < 2 or n_controls < 2:
        return np.nan
    a = float(auc)
    q1 = a / (2.0 - a)
    q2 = 2.0 * a ** 2 / (1.0 + a)
    var = (a * (1 - a) + (n_cases - 1) * (q1 - a ** 2)
           + (n_controls - 1) * (q2 - a ** 2)) / (n_cases * n_controls)
    return float(np.sqrt(var)) if var > 0 else np.nan


def logit(p):
    return np.log(p / (1 - p))


def inv_logit(x):
    return 1 / (1 + np.exp(-x))


# --------------------------------------------------------------------------
# EN | DerSimonian-Laird random-effects pooling
# PT | Agregacao por efeitos aleatorios de DerSimonian-Laird
# --------------------------------------------------------------------------
def dersimonian_laird(y, v):
    y, v = np.asarray(y, float), np.asarray(v, float)
    k = len(y)
    if k == 0:
        return None
    w = 1.0 / v
    y_fixed = np.sum(w * y) / np.sum(w)
    Q = float(np.sum(w * (y - y_fixed) ** 2))
    df = k - 1
    if df > 0:
        c = np.sum(w) - np.sum(w ** 2) / np.sum(w)
        tau2 = max(0.0, (Q - df) / c) if c > 0 else 0.0
        I2 = max(0.0, (Q - df) / Q * 100) if Q > 0 else 0.0
        p_Q = 1 - stats.chi2.cdf(Q, df)
    else:
        tau2, I2, p_Q = 0.0, 0.0, np.nan

    w_star = 1.0 / (v + tau2)
    est = float(np.sum(w_star * y) / np.sum(w_star))
    se = float(np.sqrt(1.0 / np.sum(w_star)))
    return dict(k=k, estimate=est, se=se,
                ci_low=est - 1.959964 * se, ci_high=est + 1.959964 * se,
                Q=Q, df=df, p_Q=p_Q, tau2=tau2, I2=I2,
                z=est / se, p=2 * (1 - stats.norm.cdf(abs(est / se))))


def egger_test(y, se):
    """EN/PT: Egger regression of the standard normal deviate on precision."""
    y, se = np.asarray(y, float), np.asarray(se, float)
    if len(y) < 3:
        return None
    snd = y / se
    precision = 1.0 / se
    res = stats.linregress(precision, snd)
    return dict(intercept=res.intercept, p_value=res.pvalue,
                slope=res.slope, n=len(y))


def summarise(label, sub):
    """EN/PT: pool one subset and return a tidy row."""
    sub = sub.dropna(subset=["auc", "se_auc"])
    if len(sub) == 0:
        return None
    y = logit(sub["auc"].values)
    # EN: delta method for the SE on the logit scale | PT: metodo delta
    se_y = sub["se_auc"].values / (sub["auc"].values * (1 - sub["auc"].values))
    r = dersimonian_laird(y, se_y ** 2)
    if r is None:
        return None
    eg = egger_test(y, se_y)
    return {
        "subgroup": label,
        "k_estimates": r["k"],
        "n_studies": sub["pmid"].nunique(),
        "pooled_auc": round(inv_logit(r["estimate"]), 4),
        "ci_low": round(inv_logit(r["ci_low"]), 4),
        "ci_high": round(inv_logit(r["ci_high"]), 4),
        "tau2_logit": round(r["tau2"], 4),
        "I2_percent": round(r["I2"], 1),
        "Q": round(r["Q"], 2),
        "df": r["df"],
        "p_heterogeneity": round(r["p_Q"], 4) if not np.isnan(r["p_Q"]) else "",
        "egger_intercept": round(eg["intercept"], 3) if eg else "",
        "egger_p": round(eg["p_value"], 4) if eg else "",
    }


def main():
    os.makedirs(TAB_DIR, exist_ok=True)
    os.makedirs(FIG_DIR, exist_ok=True)
    df = pd.read_csv(IN_CSV)

    for c in ["auc", "auc_ci_low", "auc_ci_high", "n_cases", "n_controls",
              "sensitivity", "specificity"]:
        df[c] = pd.to_numeric(df[c], errors="coerce")

    # EN: CI-derived SE first, Hanley-McNeil as fallback, and record which
    # PT: EP do IC primeiro, Hanley-McNeil como alternativa, registrando a fonte
    se_ci = df.apply(lambda r: se_from_ci(r["auc_ci_low"], r["auc_ci_high"]), axis=1)
    se_hm = df.apply(lambda r: se_hanley_mcneil(r["auc"], r["n_cases"], r["n_controls"]), axis=1)
    df["se_auc"] = se_ci.where(se_ci.notna(), se_hm)
    df["se_source"] = np.where(se_ci.notna(), "reported_95CI",
                               np.where(se_hm.notna(), "Hanley-McNeil", "not_estimable"))

    pool = df[(df["eligible_primary_pool"] == "yes") & df["se_auc"].notna()].copy()

    print("=" * 78)
    print("EN | Meta-analysis input | PT | Entrada da meta-analise")
    print("=" * 78)
    print(f"Extracted rows / linhas extraidas          : {len(df)}")
    print(f"Eligible rows / linhas elegiveis           : {(df['eligible_primary_pool']=='yes').sum()}")
    print(f"Poolable (SE estimable) / com EP estimavel : {len(pool)}")
    print(f"Independent studies / estudos independentes: {pool['pmid'].nunique()}")
    print(f"SE source / origem do EP                   : "
          f"{dict(pool['se_source'].value_counts())}")

    rows = []
    rows.append(summarise("Overall (all eligible) | Global", pool))
    for d in ["AD", "PD"]:
        rows.append(summarise(f"{d} - all markers | todos marcadores",
                              pool[pool["disease"] == d]))
    for mt, lab in [("single_miRNA", "single miRNA | miRNA isolado"),
                    ("multi_miRNA_panel", "multi-miRNA panel | painel multi-miRNA")]:
        rows.append(summarise(f"All - {lab}", pool[pool["marker_type"] == mt]))
        for d in ["AD", "PD"]:
            rows.append(summarise(f"{d} - {lab}",
                                  pool[(pool["disease"] == d) & (pool["marker_type"] == mt)]))
    # EN/PT: biofluid subgroups with at least 3 estimates
    for bf, sub in pool.groupby("biofluid"):
        if len(sub) >= 3:
            rows.append(summarise(f"Biofluid | Biofluido - {bf}", sub))

    res = pd.DataFrame([r for r in rows if r])
    res.to_csv(f"{TAB_DIR}/meta_analysis_pooled_auc.csv", index=False)

    print("\n" + "=" * 78)
    print("EN | Pooled AUC (random effects) | PT | AUC agregada (efeitos aleatorios)")
    print("=" * 78)
    print(res.to_string(index=False))

    pool_out = pool[["record_id", "pmid", "doi", "first_author", "year", "disease",
                     "biofluid", "marker_type", "marker", "cohort_stage", "n_cases",
                     "n_controls", "auc", "auc_ci_low", "auc_ci_high", "se_auc",
                     "se_source"]].copy()
    pool_out.to_csv(f"{TAB_DIR}/meta_analysis_input_estimates.csv", index=False)

    forest_plot(pool)
    funnel_plot(pool)
    print(f"\nEN: tables -> {TAB_DIR} | figures -> {FIG_DIR}")
    print(f"PT: tabelas -> {TAB_DIR} | figuras -> {FIG_DIR}")


def _pooled_auc(sub):
    """EN/PT: pooled AUC and CI for a subset, on the back-transformed scale."""
    sub = sub.dropna(subset=["auc", "se_auc"])
    if len(sub) == 0:
        return None
    y = logit(sub["auc"].values)
    se_y = sub["se_auc"].values / (sub["auc"].values * (1 - sub["auc"].values))
    r = dersimonian_laird(y, se_y ** 2)
    if not r:
        return None
    return (inv_logit(r["estimate"]), inv_logit(r["ci_low"]),
            inv_logit(r["ci_high"]), r["k"], r["I2"])


def forest_plot(pool):
    """EN | Forest plot of every estimate, grouped by disease and marker type,
           with a DerSimonian-Laird summary diamond for each block.
       PT | Forest plot de cada estimativa, agrupada por doenca e tipo de
           marcador, com losango-resumo de DerSimonian-Laird por bloco."""
    colors = {"AD": "#3B6EA5", "PD": "#B3541E", "mixed_neurodegenerative": "#777777"}
    blocks = []
    for dis in ["AD", "PD"]:
        for mt, lab in [("single_miRNA", "single miRNA | miRNA isolado"),
                        ("multi_miRNA_panel", "panel | painel")]:
            sub = pool[(pool["disease"] == dis) & (pool["marker_type"] == mt)]
            sub = sub.sort_values("auc")
            if len(sub):
                blocks.append((f"{dis} - {lab}", dis, sub))

    n_rows = sum(len(s) for _, _, s in blocks) + 2 * len(blocks)
    fig, ax = plt.subplots(figsize=(10.2, 0.33 * n_rows + 2.4))
    y = n_rows
    ytick_pos, ytick_lab = [], []

    for header, dis, sub in blocks:
        y -= 1
        ax.text(0.352, y, header, ha="left", va="center",
                fontsize=8.6, fontweight="bold", color=colors.get(dis, "#333"))
        for _, r in sub.iterrows():
            y -= 1
            lo = max(r["auc"] - 1.959964 * r["se_auc"], 0.0)
            hi = min(r["auc"] + 1.959964 * r["se_auc"], 1.0)
            c = colors.get(dis, "#555555")
            ax.plot([lo, hi], [y, y], color=c, lw=1.3, zorder=2)
            ax.scatter([r["auc"]], [y], s=38, color=c,
                       marker="s" if r["marker_type"] == "single_miRNA" else "D", zorder=3)
            stage = "" if r["cohort_stage"] in ("single", "unclear") else f", {r['cohort_stage']}"
            n_txt = ""
            if not pd.isna(r["n_cases"]) and not pd.isna(r["n_controls"]):
                n_txt = f"  n={int(r['n_cases'])}/{int(r['n_controls'])}"
            label = (f"{r['first_author']} {int(r['year'])} | {r['marker']} "
                     f"({r['biofluid']}{stage}){n_txt}")
            ytick_pos.append(y)
            ytick_lab.append(label[:72])

        p = _pooled_auc(sub)
        if p:
            est, lo, hi, k, i2 = p
            y -= 1
            ax.plot([lo, hi], [y, y], color="#222222", lw=2.0, zorder=4)
            ax.scatter([est], [y], marker="D", s=80, color="#222222", zorder=5)
            ytick_pos.append(y)
            ytick_lab.append(f"Pooled | Agregado  (k={k}, I²={i2:.0f}%)")

    ax.axvline(0.5, color="#999999", ls="--", lw=1, zorder=1)
    ax.axvline(0.8, color="#cccccc", ls=":", lw=1, zorder=1)
    ax.set_xlim(0.35, 1.03)
    ax.set_ylim(-0.8, n_rows + 0.5)
    ax.set_yticks(ytick_pos)
    ax.set_yticklabels(ytick_lab, fontsize=7.4)
    ax.tick_params(axis="y", length=0)
    ax.set_xlabel("AUC (95% CI)   |   square/quadrado = single miRNA;  "
                  "diamond/losango = panel;  black diamond = random-effects summary",
                  fontsize=8.4)
    ax.set_title("Diagnostic accuracy of circulating miRNAs in AD and PD\n"
                 "Acuracia diagnostica de miRNAs circulantes em AD e PD", fontsize=11.5)
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    fig.tight_layout()
    fig.savefig(f"{FIG_DIR}/forest_plot_auc.png", dpi=300, bbox_inches="tight")
    plt.close(fig)


def funnel_plot(pool):
    """EN/PT: funnel plot on the logit(AUC) scale to inspect small-study effects."""
    y = logit(pool["auc"].values)
    se = pool["se_auc"].values / (pool["auc"].values * (1 - pool["auc"].values))
    r = dersimonian_laird(y, se ** 2)

    fig, ax = plt.subplots(figsize=(6.4, 5.4))
    colors = {"AD": "#3B6EA5", "PD": "#B3541E", "mixed_neurodegenerative": "#777777"}
    for dis, sub_idx in pool.groupby("disease").groups.items():
        idx = pool.index.get_indexer(sub_idx)
        ax.scatter(y[idx], se[idx], s=38, alpha=0.85,
                   color=colors.get(dis, "#555555"), label=dis)

    if r:
        se_max = float(np.nanmax(se)) * 1.05
        se_line = np.linspace(0.001, se_max, 60)
        for z, ls in [(1.959964, "--"), (1.644854, ":")]:
            ax.plot(r["estimate"] - z * se_line, se_line, color="#888888", ls=ls, lw=1)
            ax.plot(r["estimate"] + z * se_line, se_line, color="#888888", ls=ls, lw=1)
        ax.axvline(r["estimate"], color="#444444", lw=1.2)

    ax.invert_yaxis()
    ax.set_xlabel("logit(AUC)")
    ax.set_ylabel("Standard error | Erro-padrao")
    ax.set_title("Funnel plot: small-study effects\nGrafico de funil: efeitos de estudos pequenos",
                 fontsize=10.5)
    ax.legend(fontsize=8, frameon=False)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    fig.tight_layout()
    fig.savefig(f"{FIG_DIR}/funnel_plot_auc.png", dpi=300, bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    main()
