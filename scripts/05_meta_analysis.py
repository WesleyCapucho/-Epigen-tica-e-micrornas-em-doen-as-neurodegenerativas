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

EN | Unit of analysis. Twenty of the studies contributing to the primary pool
     supply more than one qualifying estimate each. Pooling all 41 estimates as
     if they were 41 independent observations understates the true uncertainty
     and lets a single well-instrumented cohort outweigh a study that
     contributes only one estimate. The PRIMARY analysis therefore collapses
     each study to one estimate per subgroup first, by fixed-effect
     (inverse-variance) combination of that study's own qualifying rows on the
     logit scale, and only then pools across studies with the between-study
     random-effects model. The estimate that treats every row as independent is
     kept and reported as a labelled sensitivity analysis, never as the headline
     number.
PT | Unidade de analise. Vinte dos estudos que contribuem ao pool primario
     fornecem mais de uma estimativa qualificada cada. Agregar as 41 estimativas
     como se fossem 41 observacoes independentes subestima a incerteza real e
     deixa uma coorte bem instrumentada pesar mais que um estudo que contribui
     so uma estimativa. A analise PRIMARIA portanto colapsa cada estudo a uma
     estimativa por subgrupo primeiro, por combinacao de efeito fixo
     (inverso-variancia) das proprias linhas qualificadas do estudo na escala
     logito, e so entao agrega entre estudos com o modelo de efeitos aleatorios
     entre-estudos. A estimativa que trata cada linha como independente e
     mantida e reportada como analise de sensibilidade rotulada, nunca como o
     numero principal.

EN | Heterogeneity estimator. DerSimonian & Laird (1986) tau-squared is known to
     be biased downward at the small-to-moderate k seen in every subgroup here.
     Paule & Mandel (1982) is reported as the primary tau-squared estimator
     (an iterative, unbiased-equation estimator very close to REML in practice,
     and exactly solvable here without a general-purpose optimizer), with
     Hartung-Knapp-Sidik-Jonkman (2001) confidence intervals and a prediction
     interval for every pooled estimate with k >= 3. DerSimonian-Laird is kept
     as a labelled sensitivity check, not the primary tau-squared.
PT | Estimador de heterogeneidade. O tau-quadrado de DerSimonian & Laird (1986)
     e sabidamente enviesado para baixo no k pequeno a moderado visto em todo
     subgrupo aqui. Paule & Mandel (1982) e reportado como estimador primario de
     tau-quadrado (um estimador iterativo, de equacao nao-enviesada, muito
     proximo do REML na pratica, e resolvivel aqui exatamente sem otimizador de
     proposito geral), com intervalos de confianca de Hartung-Knapp-Sidik-Jonkman
     (2001) e um intervalo de predicao para toda estimativa agregada com k >= 3.
     DerSimonian-Laird e mantido como checagem de sensibilidade rotulada, nao
     como o tau-quadrado primario.

EN | No value is simulated: every AUC, sample size and confidence interval comes
     from the extraction table, which stores the verbatim sentence of the source.
PT | Nenhum valor e simulado: toda AUC, tamanho amostral e intervalo de confianca
     vem da tabela de extracao, que guarda a frase verbatim da fonte.
"""

import os
import sys
import numpy as np
import pandas as pd
from scipy import stats, optimize
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

IN_CSV = "data/extracted/diagnostic_accuracy_extraction.csv"
TAB_DIR = "results/tables"
FIG_DIR = "results/figures"

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _bilingual import LANGS, t, fig_path


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
# EN | Heterogeneity (tau-squared) estimators
# PT | Estimadores de heterogeneidade (tau-quadrado)
# --------------------------------------------------------------------------
def dl_tau2(y, v):
    """EN/PT: DerSimonian & Laird (1986) moment estimator of tau-squared."""
    y, v = np.asarray(y, float), np.asarray(v, float)
    k = len(y)
    w = 1.0 / v
    y_fixed = np.sum(w * y) / np.sum(w)
    Q = float(np.sum(w * (y - y_fixed) ** 2))
    df = k - 1
    if df <= 0:
        return 0.0, Q, df
    c = np.sum(w) - np.sum(w ** 2) / np.sum(w)
    tau2 = max(0.0, (Q - df) / c) if c > 0 else 0.0
    return tau2, Q, df


def paule_mandel_tau2(y, v):
    """
    EN | Paule & Mandel (1982) estimator: the tau-squared root of
         Q(tau2) = sum_i w_i(tau2) * (y_i - theta_hat(tau2))^2 = k - 1,
         where w_i(tau2) = 1/(v_i + tau2). Q(tau2) is monotonically
         non-increasing in tau2 (from Q(0) = the fixed-effect Q down to 0 as
         tau2 -> infinity), so the root is found by bisection, which cannot
         diverge or overshoot the way a Newton step can.
    PT | Estimador de Paule & Mandel (1982): a raiz em tau-quadrado de
         Q(tau2) = soma_i w_i(tau2) * (y_i - theta_hat(tau2))^2 = k - 1,
         onde w_i(tau2) = 1/(v_i + tau2). Q(tau2) e monotonicamente
         nao-crescente em tau2 (de Q(0) = o Q de efeito fixo ate 0 quando
         tau2 -> infinito), entao a raiz e achada por bissecao, que nao pode
         divergir nem ultrapassar como um passo de Newton pode.
    """
    y, v = np.asarray(y, float), np.asarray(v, float)
    k = len(y)
    if k < 2:
        return 0.0

    def q_minus_target(tau2):
        w = 1.0 / (v + tau2)
        theta = np.sum(w * y) / np.sum(w)
        return float(np.sum(w * (y - theta) ** 2)) - (k - 1)

    q0 = q_minus_target(0.0)
    if q0 <= 0:
        return 0.0
    hi = max(np.var(y, ddof=1), np.max(v)) * 4 + 1.0
    tries = 0
    while q_minus_target(hi) > 0 and tries < 60:
        hi *= 2
        tries += 1
    try:
        tau2 = optimize.brentq(q_minus_target, 0.0, hi, xtol=1e-10, maxiter=200)
    except ValueError:
        tau2, _, _ = dl_tau2(y, v)
    return max(0.0, float(tau2))


# --------------------------------------------------------------------------
# EN | Unified random-effects pooling: DL Q/I2 always reported for
#      heterogeneity description; tau2_method selects which tau-squared
#      feeds the pooled estimate, its Wald CI, its Hartung-Knapp-Sidik-Jonkman
#      CI, and its prediction interval.
# PT | Agregacao unificada de efeitos aleatorios: Q/I2 de DL sempre reportados
#      para descrever heterogeneidade; tau2_method escolhe qual tau-quadrado
#      alimenta a estimativa agregada, seu IC de Wald, seu IC de
#      Hartung-Knapp-Sidik-Jonkman e seu intervalo de predicao.
# --------------------------------------------------------------------------
def pool_re(y, v, tau2_method="PM"):
    y, v = np.asarray(y, float), np.asarray(v, float)
    k = len(y)
    if k == 0:
        return None

    tau2_dl, Q, df = dl_tau2(y, v)
    I2 = max(0.0, (Q - df) / Q * 100) if (df > 0 and Q > 0) else 0.0
    p_Q = 1 - stats.chi2.cdf(Q, df) if df > 0 else np.nan

    if tau2_method == "PM" and k >= 2:
        tau2 = paule_mandel_tau2(y, v)
    else:
        tau2 = tau2_dl

    w = 1.0 / (v + tau2)
    theta = float(np.sum(w * y) / np.sum(w))
    se_wald = float(np.sqrt(1.0 / np.sum(w)))
    ci_low_wald = theta - 1.959964 * se_wald
    ci_high_wald = theta + 1.959964 * se_wald

    if k >= 2:
        q_stat = float(np.sum(w * (y - theta) ** 2) / (k - 1))
        se_hk = float(np.sqrt(q_stat / np.sum(w)))
        tcrit = stats.t.ppf(0.975, k - 1)
        ci_low_hk = theta - tcrit * se_hk
        ci_high_hk = theta + tcrit * se_hk
    else:
        se_hk = np.nan
        ci_low_hk = ci_high_hk = np.nan

    if k >= 3:
        tcrit_pi = stats.t.ppf(0.975, k - 2)
        pi_low = theta - tcrit_pi * np.sqrt(tau2 + se_wald ** 2)
        pi_high = theta + tcrit_pi * np.sqrt(tau2 + se_wald ** 2)
    else:
        pi_low = pi_high = np.nan

    return dict(k=k, estimate=theta, se=se_wald,
                ci_low=ci_low_wald, ci_high=ci_high_wald,
                se_hk=se_hk, ci_low_hk=ci_low_hk, ci_high_hk=ci_high_hk,
                pi_low=pi_low, pi_high=pi_high,
                Q=Q, df=df, p_Q=p_Q, tau2=tau2, tau2_dl=tau2_dl, I2=I2,
                tau2_method=tau2_method)


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


# --------------------------------------------------------------------------
# EN | Collapse multiple qualifying estimates from the same study, within a
#      subgroup, to a single logit-AUC and variance by fixed-effect
#      (inverse-variance) combination. A study with one qualifying estimate
#      passes through unchanged.
# PT | Colapsa multiplas estimativas qualificadas do mesmo estudo, dentro de
#      um subgrupo, a um unico logito-AUC e variancia por combinacao de
#      efeito fixo (inverso-variancia). Um estudo com uma estimativa
#      qualificada passa sem alteracao.
# --------------------------------------------------------------------------
def collapse_one_per_study(sub):
    sub = sub.dropna(subset=["auc", "se_auc"]).copy()
    if len(sub) == 0:
        return sub.assign(y=[], v=[])
    sub["y"] = logit(sub["auc"].values)
    sub["se_y"] = sub["se_auc"].values / (sub["auc"].values * (1 - sub["auc"].values))
    sub["v"] = sub["se_y"] ** 2

    rows = []
    for sid, g in sub.groupby("study_id"):
        if len(g) == 1:
            rows.append(dict(study_id=sid, y=g["y"].iloc[0], v=g["v"].iloc[0],
                             n_rows_collapsed=1))
        else:
            w = 1.0 / g["v"].values
            y_fe = float(np.sum(w * g["y"].values) / np.sum(w))
            v_fe = float(1.0 / np.sum(w))
            rows.append(dict(study_id=sid, y=y_fe, v=v_fe,
                             n_rows_collapsed=len(g)))
    return pd.DataFrame(rows)


def summarise_primary(label, sub):
    """
    EN/PT: primary analysis for one subgroup - collapse to one estimate per
    study (fixed-effect within study), then pool between studies with
    Paule-Mandel tau2, reporting the Wald, Hartung-Knapp and prediction
    intervals side by side.
    """
    coll = collapse_one_per_study(sub)
    if len(coll) == 0:
        return None
    r = pool_re(coll["y"].values, coll["v"].values, tau2_method="PM")
    if r is None:
        return None
    n_multi = int((coll["n_rows_collapsed"] > 1).sum())
    return {
        "subgroup": label,
        "n_studies": r["k"],
        "n_estimates_collapsed": int(sub.dropna(subset=["auc", "se_auc"]).shape[0]),
        "n_studies_with_multiple_estimates": n_multi,
        "pooled_auc": round(inv_logit(r["estimate"]), 4),
        "ci_low_wald": round(inv_logit(r["ci_low"]), 4),
        "ci_high_wald": round(inv_logit(r["ci_high"]), 4),
        "ci_low_hk": round(inv_logit(r["ci_low_hk"]), 4) if not np.isnan(r["ci_low_hk"]) else "",
        "ci_high_hk": round(inv_logit(r["ci_high_hk"]), 4) if not np.isnan(r["ci_high_hk"]) else "",
        "pi_low": round(inv_logit(r["pi_low"]), 4) if not np.isnan(r["pi_low"]) else "",
        "pi_high": round(inv_logit(r["pi_high"]), 4) if not np.isnan(r["pi_high"]) else "",
        "tau2_PM": round(r["tau2"], 4),
        "I2_percent": round(r["I2"], 1),
        "Q": round(r["Q"], 2),
        "df": r["df"],
        "p_heterogeneity": round(r["p_Q"], 4) if not np.isnan(r["p_Q"]) else "",
    }


def summarise_sensitivity_every_estimate(label, sub):
    """EN/PT: the every-row-independent DerSimonian-Laird pool, kept as a
    labelled sensitivity analysis (this was the primary analysis before the
    unit-of-analysis correction)."""
    sub = sub.dropna(subset=["auc", "se_auc"])
    if len(sub) == 0:
        return None
    y = logit(sub["auc"].values)
    se_y = sub["se_auc"].values / (sub["auc"].values * (1 - sub["auc"].values))
    r = pool_re(y, se_y ** 2, tau2_method="DL")
    if r is None:
        return None
    eg = egger_test(y, se_y)
    return {
        "subgroup": label,
        "k_estimates": r["k"],
        "n_studies": sub["study_id"].nunique(),
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


def subgroup_difference_test(sub_a, sub_b, label):
    """
    EN | Test for subgroup differences (Borenstein et al., 2009, ch.19): pool
         all rows of both subgroups combined to get Q_all, pool each subgroup
         separately to get Q_a and Q_b, then Q_between = Q_all - Q_a - Q_b
         with 1 df. Computed on the one-per-study collapsed rows, matching the
         primary analysis.
    PT | Teste para diferenca entre subgrupos (Borenstein et al., 2009, cap.19):
         agrega todas as linhas dos dois subgrupos juntas para obter Q_all,
         agrega cada subgrupo separadamente para obter Q_a e Q_b, entao
         Q_between = Q_all - Q_a - Q_b com 1 gl. Calculado sobre as linhas
         colapsadas uma-por-estudo, igual a analise primaria.
    """
    coll_a = collapse_one_per_study(sub_a)
    coll_b = collapse_one_per_study(sub_b)
    if len(coll_a) < 2 or len(coll_b) < 2:
        return None
    y_all = np.concatenate([coll_a["y"].values, coll_b["y"].values])
    v_all = np.concatenate([coll_a["v"].values, coll_b["v"].values])
    _, Q_all, _ = dl_tau2(y_all, v_all)
    _, Q_a, _ = dl_tau2(coll_a["y"].values, coll_a["v"].values)
    _, Q_b, _ = dl_tau2(coll_b["y"].values, coll_b["v"].values)
    q_between = Q_all - Q_a - Q_b
    p_value = 1 - stats.chi2.cdf(q_between, 1) if q_between >= 0 else np.nan
    return dict(comparison=label, n_studies_a=len(coll_a), n_studies_b=len(coll_b),
                Q_between=round(q_between, 3), df=1,
                p_value=round(p_value, 4) if not np.isnan(p_value) else "")


def variance_source_comparison(label, sub):
    """
    EN/PT: compares the pooled AUC using only estimates with a directly
    reported CI/SE against the full pool that also includes Hanley-McNeil
    reconstructed variances, both on the one-per-study primary basis.
    """
    reported = sub[sub["se_source"] == "reported_95CI"]
    out = []
    for tag, s in [("reported_only | somente_reportado", reported),
                   ("full (reported + reconstructed) | completo (reportado + reconstruido)", sub)]:
        r = summarise_primary(f"{label} - {tag}", s)
        if r:
            out.append(r)
    return out


def main():
    os.makedirs(TAB_DIR, exist_ok=True)
    os.makedirs(FIG_DIR, exist_ok=True)
    df = pd.read_csv(IN_CSV)

    for c in ["auc", "auc_ci_low", "auc_ci_high", "n_cases", "n_controls",
              "sensitivity", "specificity"]:
        df[c] = pd.to_numeric(df[c], errors="coerce")

    se_ci = df.apply(lambda r: se_from_ci(r["auc_ci_low"], r["auc_ci_high"]), axis=1)
    se_hm = df.apply(lambda r: se_hanley_mcneil(r["auc"], r["n_cases"], r["n_controls"]), axis=1)
    df["se_auc"] = se_ci.where(se_ci.notna(), se_hm)
    df["se_source"] = np.where(se_ci.notna(), "reported_95CI",
                               np.where(se_hm.notna(), "Hanley-McNeil", "not_estimable"))

    pmid_txt = (df["pmid"].astype(str).str.strip()
                .str.replace(r"\.0$", "", regex=True)
                .replace({"": np.nan, "nan": np.nan, "None": np.nan}))
    df["study_id"] = pmid_txt.fillna(df["doi"].astype(str).str.strip().str.lower())

    pool = df[(df["eligible_primary_pool"] == "yes") & df["se_auc"].notna()].copy()

    print("=" * 78)
    print("EN | Meta-analysis input | PT | Entrada da meta-analise")
    print("=" * 78)
    print(f"Extracted rows / linhas extraidas          : {len(df)}")
    print(f"Eligible rows / linhas elegiveis           : {(df['eligible_primary_pool']=='yes').sum()}")
    print(f"Poolable (SE estimable) / com EP estimavel : {len(pool)}")
    print(f"Independent studies / estudos independentes: {pool['study_id'].nunique()}")
    print(f"SE source / origem do EP                   : "
          f"{dict(pool['se_source'].value_counts())}")

    # EN | PRIMARY analysis: AD and PD are separate primary subgroups; the
    #      pooled AD+PD figure is reported as a secondary, exploratory summary.
    # PT | Analise PRIMARIA: AD e PD sao subgrupos primarios separados; a
    #      cifra agregada AD+PD e reportada como resumo secundario, exploratorio.
    primary_rows = []
    primary_rows.append(summarise_primary("AD - all markers | todos marcadores (PRIMARY 1)",
                                          pool[pool["disease"] == "AD"]))
    primary_rows.append(summarise_primary("PD - all markers | todos marcadores (PRIMARY 2)",
                                          pool[pool["disease"] == "PD"]))
    primary_rows.append(summarise_primary("Overall AD+PD (all eligible) | Global (SECONDARY)",
                                          pool))
    for mt, lab in [("single_miRNA", "single miRNA | miRNA isolado"),
                    ("multi_miRNA_panel", "multi-miRNA panel | painel multi-miRNA")]:
        primary_rows.append(summarise_primary(f"All - {lab}", pool[pool["marker_type"] == mt]))
        for d in ["AD", "PD"]:
            primary_rows.append(summarise_primary(
                f"{d} - {lab}", pool[(pool["disease"] == d) & (pool["marker_type"] == mt)]))
    for bf, sub in pool.groupby("biofluid"):
        if len(sub) >= 3 and sub["study_id"].nunique() >= 3:
            primary_rows.append(summarise_primary(f"Biofluid | Biofluido - {bf}", sub))

    primary_res = pd.DataFrame([r for r in primary_rows if r])
    primary_res.to_csv(f"{TAB_DIR}/meta_analysis_pooled_auc_primary.csv", index=False)

    print("\n" + "=" * 78)
    print("EN | PRIMARY: one estimate per study, Paule-Mandel tau2, HKSJ CI")
    print("PT | PRIMARIA: uma estimativa por estudo, tau2 de Paule-Mandel, IC HKSJ")
    print("=" * 78)
    print(primary_res.to_string(index=False))

    # EN | SENSITIVITY: every row treated as independent, DerSimonian-Laird -
    #      this was the review's previous primary analysis.
    # PT | SENSIBILIDADE: cada linha tratada como independente, DerSimonian-Laird
    #      - esta era a analise primaria anterior da revisao.
    sens_rows = []
    sens_rows.append(summarise_sensitivity_every_estimate("Overall (all eligible) | Global", pool))
    for d in ["AD", "PD"]:
        sens_rows.append(summarise_sensitivity_every_estimate(
            f"{d} - all markers | todos marcadores", pool[pool["disease"] == d]))
    for mt, lab in [("single_miRNA", "single miRNA | miRNA isolado"),
                    ("multi_miRNA_panel", "multi-miRNA panel | painel multi-miRNA")]:
        sens_rows.append(summarise_sensitivity_every_estimate(
            f"All - {lab}", pool[pool["marker_type"] == mt]))
        for d in ["AD", "PD"]:
            sens_rows.append(summarise_sensitivity_every_estimate(
                f"{d} - {lab}", pool[(pool["disease"] == d) & (pool["marker_type"] == mt)]))
    for bf, sub in pool.groupby("biofluid"):
        if len(sub) >= 3 and sub["study_id"].nunique() >= 3:
            sens_rows.append(summarise_sensitivity_every_estimate(f"Biofluid | Biofluido - {bf}", sub))
    sens_res = pd.DataFrame([r for r in sens_rows if r])
    sens_res.to_csv(f"{TAB_DIR}/meta_analysis_pooled_auc_sensitivity_every_estimate.csv", index=False)

    # EN | Variance-source comparison for the two primary outcomes.
    # PT | Comparacao de origem de variancia para os dois desfechos primarios.
    varsrc_rows = []
    varsrc_rows += variance_source_comparison("AD - all markers", pool[pool["disease"] == "AD"])
    varsrc_rows += variance_source_comparison("PD - all markers", pool[pool["disease"] == "PD"])
    varsrc_res = pd.DataFrame([r for r in varsrc_rows if r])
    varsrc_res.to_csv(f"{TAB_DIR}/meta_analysis_variance_source_comparison.csv", index=False)
    print("\n" + "=" * 78)
    print("EN | Variance source: reported-only vs full (+ reconstructed)")
    print("PT | Origem da variancia: so-reportado vs completo (+ reconstruido)")
    print("=" * 78)
    print(varsrc_res.to_string(index=False))

    # EN | Formal test for subgroup differences: panel vs single, within each
    #      disease and combined, on the one-per-study primary basis.
    # PT | Teste formal para diferenca entre subgrupos: painel vs isolado,
    #      dentro de cada doenca e combinado, na base primaria uma-por-estudo.
    diff_rows = []
    for d in ["AD", "PD", None]:
        base = pool if d is None else pool[pool["disease"] == d]
        single = base[base["marker_type"] == "single_miRNA"]
        panel = base[base["marker_type"] == "multi_miRNA_panel"]
        label = "panel vs single | painel vs isolado" + (f" - {d}" if d else " - combined | combinado")
        r = subgroup_difference_test(single, panel, label)
        if r:
            diff_rows.append(r)
    diff_res = pd.DataFrame(diff_rows)
    diff_res.to_csv(f"{TAB_DIR}/subgroup_difference_test.csv", index=False)
    print("\n" + "=" * 78)
    print("EN | Test for subgroup differences (Borenstein et al. 2009, ch.19)")
    print("PT | Teste para diferenca entre subgrupos (Borenstein et al. 2009, cap.19)")
    print("=" * 78)
    print(diff_res.to_string(index=False))

    pool_out = pool[["record_id", "pmid", "doi", "first_author", "year", "disease",
                     "biofluid", "marker_type", "marker", "cohort_stage", "n_cases",
                     "n_controls", "auc", "auc_ci_low", "auc_ci_high", "se_auc",
                     "se_source"]].copy()
    pool_out.to_csv(f"{TAB_DIR}/meta_analysis_input_estimates.csv", index=False)

    sensitivity_analyses(pool)

    for lang in LANGS:
        forest_plot(pool, lang)
        funnel_plot(pool, lang)
    print(f"\nEN: tables -> {TAB_DIR} | figures -> {FIG_DIR}")
    print(f"PT: tabelas -> {TAB_DIR} | figuras -> {FIG_DIR}")


def sensitivity_analyses(pool):
    """
    EN | Test whether the single-miRNA estimate depends on any one study,
         beyond the one-per-study collapse already applied in the primary
         analysis: leave-one-study-out on the collapsed rows.
    PT | Testa se a estimativa de miRNA isolado depende de um unico estudo,
         alem do colapso uma-por-estudo ja aplicado na analise primaria:
         deixar-um-estudo-de-fora sobre as linhas colapsadas.
    """
    single = pool[pool["marker_type"] == "single_miRNA"].dropna(subset=["auc", "se_auc"])
    if single["study_id"].nunique() < 3:
        return

    coll = collapse_one_per_study(single)
    out = []
    base = pool_re(coll["y"].values, coll["v"].values, tau2_method="PM")
    out.append(dict(analysis="primary (one per study) | primaria (uma por estudo)",
                    k_estimates=base["k"], n_studies=base["k"],
                    pooled_auc=round(inv_logit(base["estimate"]), 4),
                    ci_low=round(inv_logit(base["ci_low_hk"]), 4) if not np.isnan(base["ci_low_hk"]) else "",
                    ci_high=round(inv_logit(base["ci_high_hk"]), 4) if not np.isnan(base["ci_high_hk"]) else "",
                    I2_percent=round(base["I2"], 1)))

    for sid in sorted(coll["study_id"].unique()):
        sub = coll[coll["study_id"] != sid]
        if len(sub) < 2:
            continue
        r = pool_re(sub["y"].values, sub["v"].values, tau2_method="PM")
        who = single[single["study_id"] == sid].iloc[0]
        out.append(dict(analysis=f"leave out | sem {who['first_author']} {who['year']} ({sid})",
                        k_estimates=r["k"], n_studies=r["k"],
                        pooled_auc=round(inv_logit(r["estimate"]), 4),
                        ci_low=round(inv_logit(r["ci_low_hk"]), 4) if not np.isnan(r["ci_low_hk"]) else "",
                        ci_high=round(inv_logit(r["ci_high_hk"]), 4) if not np.isnan(r["ci_high_hk"]) else "",
                        I2_percent=round(r["I2"], 1)))

    sens = pd.DataFrame(out)
    sens.to_csv(f"{TAB_DIR}/sensitivity_single_mirna.csv", index=False)
    print("\n" + "=" * 78)
    print("EN | Leave-one-study-out, single-miRNA (one-per-study basis)")
    print("PT | Deixar-um-estudo-de-fora, miRNA isolado (base uma-por-estudo)")
    print("=" * 78)
    print(sens.to_string(index=False))


def _pooled_auc(sub):
    """EN/PT: pooled AUC and CI (DL, every-row) for the forest/funnel plots,
    which display every individual estimate and therefore keep the
    every-row summary diamond for visual continuity with the raw data shown."""
    sub = sub.dropna(subset=["auc", "se_auc"])
    if len(sub) == 0:
        return None
    y = logit(sub["auc"].values)
    se_y = sub["se_auc"].values / (sub["auc"].values * (1 - sub["auc"].values))
    r = pool_re(y, se_y ** 2, tau2_method="DL")
    if not r:
        return None
    return (inv_logit(r["estimate"]), inv_logit(r["ci_low"]),
            inv_logit(r["ci_high"]), r["k"], r["I2"])


def forest_plot(pool, lang):
    """EN | Forest plot of every estimate, grouped by disease and marker type,
           with a DerSimonian-Laird summary diamond for each block (the
           every-row view; the primary, one-per-study pooled figures are in
           Table 1 and results/tables/meta_analysis_pooled_auc_primary.csv).
       PT | Forest plot de cada estimativa, agrupada por doenca e tipo de
           marcador, com losango-resumo de DerSimonian-Laird por bloco (a
           visao por linha; as cifras primarias, uma-por-estudo, estao na
           Tabela 1 e em results/tables/meta_analysis_pooled_auc_primary.csv)."""
    colors = {"AD": "#3B6EA5", "PD": "#B3541E", "mixed_neurodegenerative": "#777777"}
    blocks = []
    for dis in ["AD", "PD"]:
        for mt, lab in [("single_miRNA", t(lang, "single miRNA", "miRNA isolado")),
                        ("multi_miRNA_panel", t(lang, "panel", "painel"))]:
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
            ytick_lab.append(f"Pooled (every row) | Agregado (por linha)  (k={k}, I²={i2:.0f}%)")

    ax.axvline(0.5, color="#999999", ls="--", lw=1, zorder=1)
    ax.axvline(0.8, color="#cccccc", ls=":", lw=1, zorder=1)
    ax.set_xlim(0.35, 1.03)
    ax.set_ylim(-0.8, n_rows + 0.5)
    ax.set_yticks(ytick_pos)
    ax.set_yticklabels(ytick_lab, fontsize=7.4)
    ax.tick_params(axis="y", length=0)
    ax.set_xlabel(t(lang,
                    "AUC (95% CI).  Square = single miRNA;  diamond = panel;  "
                    "black diamond = random-effects summary, every row",
                    "AUC (IC 95%).  Quadrado = miRNA isolado;  losango = painel;  "
                    "losango preto = resumo de efeitos aleatórios, por linha"), fontsize=8.4)
    ax.set_title(t(lang, "Diagnostic accuracy of circulating miRNAs in AD and PD",
                   "Acurácia diagnóstica de miRNAs circulantes na DA e na DP"),
                 fontsize=11.5)
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    fig.tight_layout()
    fig.savefig(fig_path(FIG_DIR, "forest_plot_auc", lang), dpi=600, bbox_inches="tight")
    plt.close(fig)


def funnel_plot(pool, lang):
    """EN/PT: funnel plot on the logit(AUC) scale to inspect small-study effects."""
    y = logit(pool["auc"].values)
    se = pool["se_auc"].values / (pool["auc"].values * (1 - pool["auc"].values))
    r = pool_re(y, se ** 2, tau2_method="DL")

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
    ax.set_ylabel(t(lang, "Standard error", "Erro-padrão"))
    ax.set_title(t(lang, "Funnel plot: small-study effects",
                   "Gráfico de funil: efeitos de estudos pequenos"), fontsize=10.5)
    ax.legend(fontsize=8, frameon=False)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    fig.tight_layout()
    fig.savefig(fig_path(FIG_DIR, "funnel_plot_auc", lang), dpi=600, bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    main()
