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

EN | Unit of analysis. Eight of the 20 studies with an estimable variance
     supply more than one qualifying estimate each, and those estimates
     typically come from the same participants (e.g. a single microRNA and a
     panel that contains it, measured in one cohort), so they are correlated.
     A within-study fixed-effect (inverse-variance) combination assumes they
     are independent and therefore understates the true uncertainty of the
     combined estimate; it does not resolve the dependence, only relabels it.
     The PRIMARY analysis instead selects exactly ONE estimate per study by a
     rule fixed in advance and blind to the estimate's own AUC: (1) prefer a
     row evaluated in an independent validation cohort (cohort_stage ==
     "validation") over one derived and evaluated in the same sample; (2)
     within the surviving tier, prefer the study's own multi-microRNA panel
     over its component single markers, since the panel is the study's
     integrative, composite result rather than one candidate among several;
     (3) if still tied, prefer the row with the larger combined case+control
     sample size; (4) if still tied, take the alphabetically first marker
     name, a purely nominal, content-free tiebreak. Every selection is written
     to results/tables/one_estimate_per_study_selection_audit.csv with the
     reason it won, so the choice is auditable and was never made by picking
     the largest AUC. Only after this one-row-per-study reduction are studies
     pooled across with the between-study random-effects model. The estimate
     that treats every row as independent is kept and reported as a labelled
     sensitivity analysis, never as the headline number.
PT | Unidade de analise. Oito dos 20 estudos com variancia estimavel fornecem
     mais de uma estimativa qualificada cada, e essas estimativas tipicamente
     vem dos mesmos participantes (ex.: um microRNA isolado e um painel que o
     contem, medidos numa mesma coorte), portanto sao correlacionadas. Uma
     combinacao de efeito fixo (inverso-variancia) dentro do estudo assume que
     sao independentes e por isso subestima a incerteza real da estimativa
     combinada; isso nao resolve a dependencia, apenas a rotula de outro jeito.
     A analise PRIMARIA em vez disso seleciona exatamente UMA estimativa por
     estudo por uma regra fixada de antemao e cega ao valor da propria AUC:
     (1) preferir uma linha avaliada numa coorte de validacao independente
     (cohort_stage == "validation") sobre uma derivada e avaliada na mesma
     amostra; (2) dentro do nivel remanescente, preferir o painel
     multi-miRNA do proprio estudo sobre seus marcadores isolados
     componentes, pois o painel e o resultado integrativo e composto do
     estudo, nao um candidato entre varios; (3) se ainda empatado, preferir a
     linha com maior tamanho amostral combinado (casos+controles); (4) se
     ainda empatado, tomar o nome do marcador alfabeticamente primeiro, um
     desempate puramente nominal, sem conteudo. Toda selecao e escrita em
     results/tables/one_estimate_per_study_selection_audit.csv com o motivo da
     escolha, para que ela seja auditavel e nunca tenha sido feita escolhendo
     a maior AUC. So apos essa reducao a uma-linha-por-estudo os estudos sao
     agregados entre si com o modelo de efeitos aleatorios entre-estudos. A
     estimativa que trata cada linha como independente e mantida e reportada
     como analise de sensibilidade rotulada, nunca como o numero principal.

EN | Scope of the primary pool: circulating (blood-derived) versus CSF. The
     eligibility criteria admit a small number of cerebrospinal-fluid (CSF)
     studies alongside the blood-derived biofluids the title and research
     question concern, because they were captured by the same search and
     screened, risk-of-bias-rated and GRADE-rated alongside the rest of the
     corpus. CSF is not a peripheral, minimally invasive circulating biofluid
     in the sense plasma, serum or whole blood are, so the PRIMARY pooled AUC
     never mixes a CSF row with a blood-derived one: CSF studies are held out
     of every pooled estimate and reported narratively, on their own, as a
     secondary, non-pooled observation (k=1 per disease, so there is nothing
     to pool).
PT | Escopo do pool primario: circulante (derivado de sangue) versus LCR. Os
     criterios de elegibilidade admitem um pequeno numero de estudos de
     liquido cefalorraquidiano (LCR) ao lado dos biofluidos derivados de
     sangue que o titulo e a pergunta de pesquisa tratam, porque foram
     capturados pela mesma busca e triados, avaliados quanto a risco de vies e
     GRADE junto ao resto do corpus. O LCR nao e um biofluido circulante
     periferico e minimamente invasivo no sentido em que plasma, soro ou
     sangue total sao, entao a AUC agregada PRIMARIA nunca mistura uma linha
     de LCR com uma derivada de sangue: estudos de LCR ficam fora de toda
     estimativa agregada e sao reportados narrativamente, isoladamente, como
     uma observacao secundaria, nao agregada (k=1 por doenca, entao nao ha o
     que agregar).

EN | Heterogeneity estimator. DerSimonian & Laird (1986) tau-squared is known to
     be biased downward at the small-to-moderate k seen in every subgroup here.
     Paule & Mandel (1982) is reported as the primary tau-squared estimator
     (an iterative, unbiased-equation estimator very close to REML in practice,
     and exactly solvable here without a general-purpose optimizer), with
     modified Hartung-Knapp (mHK) confidence intervals, Paule-Mandel tau-squared and a prediction
     interval for every pooled estimate with k >= 3. DerSimonian-Laird is kept
     as a labelled sensitivity check, not the primary tau-squared.
PT | Estimador de heterogeneidade. O tau-quadrado de DerSimonian & Laird (1986)
     e sabidamente enviesado para baixo no k pequeno a moderado visto em todo
     subgrupo aqui. Paule & Mandel (1982) e reportado como estimador primario de
     tau-quadrado (um estimador iterativo, de equacao nao-enviesada, muito
     proximo do REML na pratica, e resolvivel aqui exatamente sem otimizador de
     proposito geral), com intervalos de confianca de Hartung-Knapp modificado (mHK), tau-quadrado de Paule-Mandel
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
import _study_selection as _sel

# EN | Cerebrospinal-fluid biofluid codes (shared with 15_bivariate_srocc.py
#      via _study_selection.py), held out of every pooled ("primary" or
#      sensitivity) AUC and reported only as a narrative, non-pooled
#      secondary observation - see the "Scope of the primary pool" docstring
#      further down.
# PT | Codigos de biofluido de liquido cefalorraquidiano (compartilhados com
#      15_bivariate_srocc.py via _study_selection.py), fora de toda AUC
#      agregada (analise "primaria" ou de sensibilidade) e reportados apenas
#      como uma observacao narrativa secundaria, nao agregada - ver a
#      docstring "Scope of the primary pool" mais abaixo.
CSF_BIOFLUIDS = _sel.CSF_BIOFLUIDS


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
#      feeds the pooled estimate, its Wald CI, its Hartung-Knapp CI, and its
#      prediction interval.
#
#      Naming. What is computed below is the Hartung & Knapp (2001) t-based
#      confidence interval - a refined variance estimator (q_stat/sum(w))
#      combined with a t(k-1) reference distribution - paired with
#      Paule-Mandel (1982) as the tau-squared estimator that sets the
#      weights. This is NOT "Hartung-Knapp-Sidik-Jonkman (HKSJ)": Sidik and
#      Jonkman (2002) is a distinct tau-squared ESTIMATOR (unrelated to the
#      Paule-Mandel one used here), and pairing the HK interval with it is a
#      different, specific combination this review does not use. Calling
#      every HK-type interval "HKSJ" regardless of which tau-squared feeds it
#      is a common but imprecise habit; this review names the method it
#      actually ran. The modification of IntHout et al. (2014) - flooring the
#      HK standard error at the conventional (Wald) one, se_hk = max(se_hk,
#      se_wald) - is applied, because the un-floored HK interval is known to
#      sometimes come out narrower than the standard random-effects interval
#      when between-study heterogeneity is small, which is anti-conservative;
#      flooring it never happens the other way round. The method reported
#      throughout is therefore the "modified Hartung-Knapp (mHK) interval,
#      Paule-Mandel tau-squared".
# PT | Agregacao unificada de efeitos aleatorios: Q/I2 de DL sempre reportados
#      para descrever heterogeneidade; tau2_method escolhe qual tau-quadrado
#      alimenta a estimativa agregada, seu IC de Wald, seu IC de
#      Hartung-Knapp e seu intervalo de predicao.
#
#      Nomenclatura. O que e calculado abaixo e o intervalo de confianca-t de
#      Hartung & Knapp (2001) - um estimador de variancia refinado
#      (q_stat/soma(w)) combinado com uma distribuicao de referencia t(k-1) -
#      pareado com Paule-Mandel (1982) como o estimador de tau-quadrado que
#      define os pesos. Isso NAO e "Hartung-Knapp-Sidik-Jonkman (HKSJ)": Sidik
#      e Jonkman (2002) e um ESTIMADOR de tau-quadrado distinto (nao
#      relacionado ao de Paule-Mandel usado aqui), e parear o intervalo HK com
#      ele e uma combinacao diferente e especifica que esta revisao nao usa.
#      Chamar todo intervalo tipo-HK de "HKSJ" independente de qual
#      tau-quadrado o alimenta e um habito comum mas impreciso; esta revisao
#      nomeia o metodo que de fato rodou. A modificacao de IntHout et al.
#      (2014) - colocar um piso no erro-padrao HK no erro-padrao convencional
#      (de Wald), se_hk = max(se_hk, se_wald) - e aplicada, porque o intervalo
#      HK sem piso e sabidamente as vezes mais estreito que o intervalo
#      convencional de efeitos aleatorios quando a heterogeneidade
#      entre-estudos e pequena, o que e anticonservador; colocar o piso nunca
#      acontece ao contrario. O metodo reportado ao longo do texto e portanto
#      o "intervalo de Hartung-Knapp modificado (mHK), tau-quadrado de
#      Paule-Mandel".
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
        se_hk = max(se_hk, se_wald)  # EN/PT: IntHout et al. (2014) floor - see docstring above
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
# EN | Select exactly one estimate per study, within a subgroup, by the fixed,
#      AUC-blind priority rule in scripts/_study_selection.py (imported below
#      as _sel), the single implementation this rule has anywhere in the
#      review - scripts/15_bivariate_srocc.py calls the same function, so the
#      AUC-based and the sensitivity/specificity-based syntheses can never
#      silently pick a different representative estimate for the same study.
#      Replaces the earlier fixed-effect within-study combination, which
#      assumed independence between same-study estimates that are typically
#      measured in the same participants and therefore correlated.
# PT | Seleciona exatamente uma estimativa por estudo, dentro de um subgrupo,
#      pela regra de prioridade fixa e cega a AUC em
#      scripts/_study_selection.py (importada abaixo como _sel), a unica
#      implementacao dessa regra em toda a revisao - scripts/15_bivariate_srocc.py
#      chama a mesma funcao, entao as sinteses baseadas em AUC e em
#      sensibilidade/especificidade nunca podem escolher em silencio uma
#      estimativa representativa diferente para o mesmo estudo. Substitui a
#      combinacao anterior de efeito fixo dentro do estudo, que assumia
#      independencia entre estimativas do mesmo estudo tipicamente medidas
#      nos mesmos participantes e portanto correlacionadas.
# --------------------------------------------------------------------------
def select_one_per_study(sub):
    sub = sub.dropna(subset=["auc", "se_auc"]).copy()
    if len(sub) == 0:
        return sub.assign(y=[], v=[])
    sub["y"] = logit(sub["auc"].values)
    sub["se_y"] = sub["se_auc"].values / (sub["auc"].values * (1 - sub["auc"].values))
    sub["v"] = sub["se_y"] ** 2

    rows = []
    for sid, g in sub.groupby("study_id"):
        candidates = g.to_dict("records")
        picked, reason, n_candidates = _sel.select_one_per_study(candidates)
        rows.append(dict(study_id=sid, y=picked["y"], v=picked["v"],
                         n_candidate_estimates=n_candidates,
                         disease=picked["disease"], biofluid=picked["biofluid"],
                         selected_marker=picked["marker"], selected_marker_type=picked["marker_type"],
                         selected_cohort_stage=picked["cohort_stage"], selected_auc=picked["auc"],
                         first_author=picked["first_author"], year=picked["year"],
                         selection_reason=reason))
    return pd.DataFrame(rows)


def summarise_from_selection(label, coll):
    """
    EN | Pool an already one-row-per-study selection (see
         select_one_per_study) with Paule-Mandel tau2, reporting the Wald,
         Hartung-Knapp and prediction intervals side by side. Marker-type and
         biofluid subgroups MUST be built by filtering the output of one
         selection made over the whole disjoint candidate set first, never by
         pre-filtering raw rows by marker_type/biofluid and selecting again
         within each filter - the latter lets a study with both a single-miRNA
         and a panel candidate contribute to both subgroups, double-counting
         it and invalidating the independence the subgroup-difference test
         (Borenstein et al., ch.19) assumes.
    PT | Agrega uma selecao ja uma-linha-por-estudo (ver select_one_per_study)
         com tau2 de Paule-Mandel, reportando os intervalos de Wald,
         Hartung-Knapp e predicao lado a lado. Subgrupos de tipo de marcador e
         biofluido DEVEM ser construidos filtrando a saida de uma selecao
         feita sobre todo o conjunto de candidatos disjunto primeiro, nunca
         pre-filtrando linhas brutas por marker_type/biofluido e selecionando
         de novo dentro de cada filtro - isso deixaria um estudo com um
         candidato single-miRNA E um candidato painel contribuir para os dois
         subgrupos, contando-o em dobro e invalidando a independencia que o
         teste de diferenca entre subgrupos (Borenstein et al., cap.19) supoe.
    """
    if len(coll) == 0:
        return None
    r = pool_re(coll["y"].values, coll["v"].values, tau2_method="PM")
    if r is None:
        return None
    n_multi = int((coll["n_candidate_estimates"] > 1).sum())
    eg = egger_test(coll["y"].values, np.sqrt(coll["v"].values)) if len(coll) >= 3 else None
    return {
        "subgroup": label,
        "n_studies": r["k"],
        "n_estimates_collapsed": int(coll["n_candidate_estimates"].sum()),
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
        "egger_intercept_one_per_study": round(eg["intercept"], 3) if eg else "",
        "egger_p_one_per_study": round(eg["p_value"], 4) if eg else "",
    }


def summarise_primary(label, sub):
    """EN/PT: convenience wrapper - selects one estimate per study from raw
    rows, then pools. Safe to use only when `sub` was filtered by a variable
    that partitions studies (disease, se_source), never by marker_type or
    biofluid (see summarise_from_selection)."""
    return summarise_from_selection(label, select_one_per_study(sub))


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


def subgroup_difference_test(coll_a, coll_b, label):
    """
    EN | Test for subgroup differences (Borenstein et al., 2009, ch.19): pool
         all rows of both subgroups combined to get Q_all, pool each subgroup
         separately to get Q_a and Q_b, then Q_between = Q_all - Q_a - Q_b
         with 1 df. Takes two already one-row-per-study selections that must
         be disjoint in study_id (produced by filtering a single global
         select_one_per_study() call, never by independently re-selecting
         within two overlapping marker-type/biofluid filters - see
         summarise_from_selection). With disjoint sets this is a standard,
         valid test of independent subgroups; it is not otherwise.
    PT | Teste para diferenca entre subgrupos (Borenstein et al., 2009, cap.19):
         agrega todas as linhas dos dois subgrupos juntas para obter Q_all,
         agrega cada subgrupo separadamente para obter Q_a e Q_b, entao
         Q_between = Q_all - Q_a - Q_b com 1 gl. Recebe duas selecoes ja
         uma-linha-por-estudo que devem ser disjuntas em study_id (produzidas
         filtrando uma unica chamada global de select_one_per_study(), nunca
         selecionando de novo, independentemente, dentro de dois filtros de
         tipo-de-marcador/biofluido que se sobrepoem - ver
         summarise_from_selection). Com conjuntos disjuntos este e um teste
         valido e padrao de subgrupos independentes; do contrario, nao e.
    """
    if len(coll_a) < 2 or len(coll_b) < 2:
        return None
    overlap = set(coll_a["study_id"]) & set(coll_b["study_id"])
    if overlap:
        raise ValueError(f"subgroup_difference_test: {label} - non-disjoint study_id {overlap}, "
                          f"the two subgroups must be built by filtering one shared selection")
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


# --------------------------------------------------------------------------
# EN | Plausibility of a reported confidence interval.
#      A reported 95% CI is normally preferred to the Hanley-McNeil
#      reconstruction. But an interval can only describe sampling uncertainty
#      if it is at least roughly as wide as sampling at the stated group sizes
#      allows. When the SE implied by a reported CI is less than
#      CI_PLAUSIBILITY_RATIO times the Hanley-McNeil SE for the same AUC and
#      group sizes, the interval is treated as not describing sampling
#      uncertainty (for example, the spread of a cross-validation estimate),
#      and the Hanley-McNeil SE is used instead. This rule was added after the
#      2026-09-28 full-text audit, not pre-specified; it changes exactly one
#      study (Li Y 2024, SE ratio about 0.07), and every analysis is also
#      re-run with the reported intervals as published
#      (scripts/26_robustness_analyses.py). The ratio of every row that has
#      both a CI and group sizes is written to
#      results/tables/ci_plausibility_check.csv so the choice of cut-off can
#      be judged against the whole distribution.
# PT | Plausibilidade de um intervalo de confianca reportado.
#      Um IC de 95% reportado normalmente tem preferencia sobre a
#      reconstrucao de Hanley-McNeil. Mas um intervalo so descreve incerteza
#      amostral se for pelo menos aproximadamente tao largo quanto a
#      amostragem nos tamanhos de grupo declarados permite. Quando o EP
#      implicito num IC reportado e menor que CI_PLAUSIBILITY_RATIO vezes o EP
#      de Hanley-McNeil para a mesma AUC e os mesmos grupos, o intervalo e
#      tratado como nao descrevendo incerteza amostral (por exemplo, a
#      dispersao de uma estimativa de validacao cruzada), e usa-se o EP de
#      Hanley-McNeil. Esta regra foi adicionada depois da auditoria de texto
#      completo de 2026-09-28, nao pre-especificada; ela muda exatamente um
#      estudo (Li Y 2024, razao de EP ~0,07), e toda analise tambem e rodada
#      com os intervalos como publicados (scripts/26_robustness_analyses.py).
#      A razao de toda linha com IC e tamanhos de grupo vai para
#      results/tables/ci_plausibility_check.csv, para que o ponto de corte
#      possa ser julgado contra a distribuicao inteira.
# --------------------------------------------------------------------------
CI_PLAUSIBILITY_RATIO = 0.5
SE_SOURCE_IMPLAUSIBLE = "Hanley-McNeil (reported CI implausibly narrow)"


def load_estimates(ci_plausibility=True):
    """
    EN | Read the extraction table and attach se_auc / se_source / study_id.
         Returns (df, elig, poolable, pool_csf, pool). With
         ci_plausibility=False every reported CI is used as published (the
         sensitivity analysis in 26_robustness_analyses.py).
    PT | Le a tabela de extracao e anexa se_auc / se_source / study_id.
         Retorna (df, elig, poolable, pool_csf, pool). Com
         ci_plausibility=False todo IC reportado e usado como publicado (a
         analise de sensibilidade em 26_robustness_analyses.py).
    """
    df = pd.read_csv(IN_CSV)
    for c in ["auc", "auc_ci_low", "auc_ci_high", "n_cases", "n_controls",
              "sensitivity", "specificity"]:
        df[c] = pd.to_numeric(df[c], errors="coerce")

    se_ci = df.apply(lambda r: se_from_ci(r["auc_ci_low"], r["auc_ci_high"]), axis=1)
    se_hm = df.apply(lambda r: se_hanley_mcneil(r["auc"], r["n_cases"], r["n_controls"]), axis=1)
    df["se_ci_reported"] = se_ci
    df["se_hanley_mcneil"] = se_hm
    df["se_ratio_ci_over_hm"] = se_ci / se_hm
    implausible = (df["se_ratio_ci_over_hm"] < CI_PLAUSIBILITY_RATIO) if ci_plausibility \
        else pd.Series(False, index=df.index)
    use_ci = se_ci.notna() & ~implausible
    df["se_auc"] = se_ci.where(use_ci, se_hm)
    df["se_source"] = np.where(use_ci, "reported_95CI",
                               np.where(implausible & se_hm.notna(), SE_SOURCE_IMPLAUSIBLE,
                                        np.where(se_hm.notna(), "Hanley-McNeil", "not_estimable")))

    pmid_txt = (df["pmid"].astype(str).str.strip()
                .str.replace(r"\.0$", "", regex=True)
                .replace({"": np.nan, "nan": np.nan, "None": np.nan}))
    df["study_id"] = pmid_txt.fillna(df["doi"].astype(str).str.strip().str.lower())

    elig = df[df["eligible_primary_pool"] == "yes"].copy()
    poolable = elig[elig["se_auc"].notna()].copy()
    is_csf = poolable["biofluid"].isin(CSF_BIOFLUIDS)
    pool_csf = poolable[is_csf].copy()
    pool = poolable[~is_csf].copy()
    return df, elig, poolable, pool_csf, pool


def main():
    os.makedirs(TAB_DIR, exist_ok=True)
    os.makedirs(FIG_DIR, exist_ok=True)
    df, elig, poolable, pool_csf, pool = load_estimates(ci_plausibility=True)

    chk = df[df["se_ci_reported"].notna() & df["se_hanley_mcneil"].notna()][
        ["record_id", "first_author", "year", "disease", "marker", "n_cases", "n_controls", "auc",
         "auc_ci_low", "auc_ci_high", "se_ci_reported", "se_hanley_mcneil", "se_ratio_ci_over_hm",
         "se_source"]].copy()
    chk["flagged_implausible"] = chk["se_ratio_ci_over_hm"] < CI_PLAUSIBILITY_RATIO
    chk.round(4).sort_values("se_ratio_ci_over_hm").to_csv(
        f"{TAB_DIR}/ci_plausibility_check.csv", index=False)

    print("=" * 78)
    print("EN | Meta-analysis input | PT | Entrada da meta-analise")
    print("=" * 78)
    print(f"Extracted rows / linhas extraidas               : {len(df)}")
    print(f"Eligible rows (systematic review) / elegiveis    : {len(elig)}")
    print(f"Poolable (SE estimable) / com EP estimavel       : {len(poolable)}")
    print(f"  of which CSF (secondary, not pooled) / das quais LCR (secundario, nao agregado): {len(pool_csf)}")
    print(f"  of which circulating (PRIMARY) / das quais circulante (PRIMARIA)              : {len(pool)}")
    print(f"Independent studies, circulating pool / estudos independentes, pool circulante: {pool['study_id'].nunique()}")
    print(f"SE source / origem do EP                        : "
          f"{dict(pool['se_source'].value_counts())}")

    # EN | CSF secondary/exploratory note: k=1 study per disease, so nothing
    #      is pooled - report each study's own estimate narratively.
    # PT | Nota secundaria/exploratoria de LCR: k=1 estudo por doenca, entao
    #      nada e agregado - reporta a estimativa do proprio estudo, narrativamente.
    csf_out = pool_csf[["record_id", "pmid", "doi", "first_author", "year", "disease",
                        "marker_type", "marker", "n_cases", "n_controls", "auc",
                        "auc_ci_low", "auc_ci_high"]].copy()
    csf_out.to_csv(f"{TAB_DIR}/csf_secondary_estimates.csv", index=False)
    print("\n" + "=" * 78)
    print("EN | CSF - secondary/exploratory, held out of every pooled estimate")
    print("PT | LCR - secundario/exploratorio, fora de toda estimativa agregada")
    print("=" * 78)
    print(csf_out.to_string(index=False))

    # EN | One global, disease-agnostic selection of one estimate per study
    #      (see select_one_per_study docstring at top of file). AD and PD
    #      subgroups, and marker-type/biofluid subgroups, are all built by
    #      FILTERING this single selection, never by re-selecting within a
    #      pre-filtered set of raw rows - the latter would let a study with
    #      both a single-miRNA and a panel candidate contribute to both
    #      marker-type subgroups (see summarise_from_selection docstring).
    # PT | Uma unica selecao global, cega a doenca, de uma estimativa por
    #      estudo (ver docstring de select_one_per_study no topo do arquivo).
    #      Subgrupos de AD e PD, e de tipo-de-marcador/biofluido, sao todos
    #      construidos FILTRANDO essa selecao unica, nunca reselecionando
    #      dentro de um conjunto de linhas brutas pre-filtrado - isso deixaria
    #      um estudo com um candidato single-miRNA E um candidato painel
    #      contribuir para os dois subgrupos de tipo-de-marcador (ver
    #      docstring de summarise_from_selection).
    sel_all = select_one_per_study(pool)
    sel_all.to_csv(f"{TAB_DIR}/one_estimate_per_study_selection_audit.csv", index=False)

    # EN | PRIMARY analysis: AD and PD are separate primary subgroups; the
    #      pooled AD+PD figure is reported as a secondary, exploratory summary.
    # PT | Analise PRIMARIA: AD e PD sao subgrupos primarios separados; a
    #      cifra agregada AD+PD e reportada como resumo secundario, exploratorio.
    primary_rows = []
    primary_rows.append(summarise_from_selection(
        "AD - all markers | todos marcadores (PRIMARY 1)", sel_all[sel_all["disease"] == "AD"]))
    primary_rows.append(summarise_from_selection(
        "PD - all markers | todos marcadores (PRIMARY 2)", sel_all[sel_all["disease"] == "PD"]))
    primary_rows.append(summarise_from_selection(
        "Overall AD+PD (all eligible) | Global (SECONDARY)", sel_all))
    for mt, lab in [("single_miRNA", "single miRNA | miRNA isolado"),
                    ("multi_miRNA_panel", "multi-miRNA panel | painel multi-miRNA")]:
        primary_rows.append(summarise_from_selection(
            f"All - {lab}", sel_all[sel_all["selected_marker_type"] == mt]))
        for d in ["AD", "PD"]:
            primary_rows.append(summarise_from_selection(
                f"{d} - {lab}",
                sel_all[(sel_all["disease"] == d) & (sel_all["selected_marker_type"] == mt)]))
    for bf, sub in sel_all.groupby("biofluid"):
        if len(sub) >= 3:
            primary_rows.append(summarise_from_selection(f"Biofluid | Biofluido - {bf}", sub))

    primary_res = pd.DataFrame([r for r in primary_rows if r])
    primary_res.to_csv(f"{TAB_DIR}/meta_analysis_pooled_auc_primary.csv", index=False)

    print("\n" + "=" * 78)
    print("EN | PRIMARY: one pre-specified, AUC-blind estimate per study, Paule-Mandel tau2, modified HK (mHK) CI")
    print("PT | PRIMARIA: uma estimativa pre-especificada e cega a AUC por estudo, tau2 de Paule-Mandel, IC mHK")
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
        base = sel_all if d is None else sel_all[sel_all["disease"] == d]
        single = base[base["selected_marker_type"] == "single_miRNA"]
        panel = base[base["selected_marker_type"] == "multi_miRNA_panel"]
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

    sensitivity_analyses(sel_all)

    for lang in LANGS:
        forest_plot(pool, lang)
        funnel_plot(pool, lang, sel_all)
    print(f"\nEN: tables -> {TAB_DIR} | figures -> {FIG_DIR}")
    print(f"PT: tabelas -> {TAB_DIR} | figuras -> {FIG_DIR}")


def sensitivity_analyses(sel_all):
    """
    EN | Test whether the single-miRNA estimate depends on any one study,
         beyond the one-per-study selection already applied in the primary
         analysis: leave-one-study-out on the selected rows. Takes the single
         global selection (see select_one_per_study), filtered to the studies
         whose selected estimate is a single microRNA - never a fresh
         selection over marker_type-pre-filtered raw rows (see
         summarise_from_selection).
    PT | Testa se a estimativa de miRNA isolado depende de um unico estudo,
         alem da selecao uma-por-estudo ja aplicada na analise primaria:
         deixar-um-estudo-de-fora sobre as linhas selecionadas. Recebe a
         selecao global unica (ver select_one_per_study), filtrada aos
         estudos cuja estimativa selecionada e um microRNA isolado - nunca
         uma nova selecao sobre linhas brutas pre-filtradas por marker_type
         (ver summarise_from_selection).
    """
    coll = sel_all[sel_all["selected_marker_type"] == "single_miRNA"]
    if coll["study_id"].nunique() < 3:
        return

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
        who = coll[coll["study_id"] == sid].iloc[0]
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
    # Title omitted: the caption in the manuscript names the figure.
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    fig.tight_layout()
    fig.savefig(fig_path(FIG_DIR, "forest_plot_auc", lang), dpi=600, bbox_inches="tight")
    plt.close(fig)


def funnel_plot(pool, lang, sel=None):
    """
    EN | Contour-enhanced funnel plot on the logit(AUC) scale. The shading marks the
         significance of a two-sided test of AUC = 0.5 (logit 0) for a point at that place:
         white p > 0.10, then progressively darker for 0.05-0.10, 0.01-0.05 and < 0.01. An
         asymmetry that sits inside the white and pale zones points to selective reporting;
         one that sits in the dark zones does not. Faint dots are every eligible estimate;
         solid dots are the one estimate per study that enters the primary analysis, and the
         vertical line is that selection's pooled estimate for each disease.
    PT | Funil com contornos na escala logit(AUC). O sombreado marca a significancia de um
         teste bilateral de AUC = 0,5 (logit 0) para um ponto naquele lugar: branco p > 0,10,
         depois cada vez mais escuro para 0,05-0,10, 0,01-0,05 e < 0,01. Uma assimetria
         dentro das zonas branca e clara aponta para relato seletivo; nas zonas escuras, nao.
         Pontos claros sao toda estimativa elegivel; pontos solidos sao a unica estimativa
         por estudo da analise primaria, e a linha vertical e o agregado dessa selecao.
    """
    import _viz_style as vs
    from matplotlib.patches import Patch
    y = logit(pool["auc"].values)
    se = pool["se_auc"].values / (pool["auc"].values * (1 - pool["auc"].values))
    se_max = float(np.nanmax(se)) * 1.08
    ymax = float(np.nanmax(np.abs(y))) * 1.12
    fig, ax = plt.subplots(figsize=(6.2, 4.9))
    grid = np.linspace(0.0, se_max, 80)
    ax.set_facecolor("#d3d2cc")                                   # p < 0.01
    for z, colr in [(2.575829, "#e4e3de"), (1.959964, "#efeeea"), (1.644854, "#ffffff")]:
        ax.fill_betweenx(grid, -z * grid, z * grid, color=colr, zorder=0.5, lw=0)
    ax.axvline(0.0, color=vs.INK3, lw=0.9, ls=(0, (3, 3)), zorder=1)
    for dis in ("AD", "PD"):
        idx = np.where(pool["disease"].values == dis)[0]
        ax.scatter(y[idx], se[idx], s=11, color=vs.DISEASE[dis], alpha=0.30, linewidths=0, zorder=2)
        if sel is not None:
            ss = sel[sel["disease"] == dis]
            ys_, ses_ = ss["y"].values.astype(float), np.sqrt(ss["v"].values.astype(float))
            ax.scatter(ys_, ses_, s=30, color=vs.DISEASE[dis], edgecolor="white", linewidths=0.7, zorder=4,
                       label=t(lang, "Alzheimer's disease" if dis == "AD" else "Parkinson's disease",
                               "Doença de Alzheimer" if dis == "AD" else "Doença de Parkinson"))
            r = pool_re(ys_, ses_ ** 2, tau2_method="PM")
            if r:
                ax.plot([r["estimate"], r["estimate"]], [0, se_max], color=vs.DISEASE[dis], lw=1.0, zorder=3)
    ax.set_xlim(-0.35, ymax)
    ax.set_ylim(se_max, 0)
    ax.set_xlabel("logit(AUC)")
    ax.set_ylabel(t(lang, "Standard error", "Erro-padrão"))
    handles, labels = ax.get_legend_handles_labels()
    for fc, lab in (("#ffffff", "p ≥ 0.10"), ("#efeeea", "0.05 ≤ p < 0.10"), ("#e4e3de", "0.01 ≤ p < 0.05"), ("#d3d2cc", "p < 0.01")):
        handles.append(Patch(fc=fc, ec=vs.RULE, lw=0.6)); labels.append(lab)
    ax.legend(handles, labels, fontsize=7, frameon=True, framealpha=0.9, facecolor="white", edgecolor=vs.RULE, loc="lower right",
              title=t(lang, "Test of AUC = 0.5", "Teste de AUC = 0,5"), title_fontsize=7)
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)
    # Title omitted: the caption in the manuscript names the figure.
    fig.tight_layout()
    fig.savefig(fig_path(FIG_DIR, "funnel_plot_auc", lang), dpi=600, bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    main()
