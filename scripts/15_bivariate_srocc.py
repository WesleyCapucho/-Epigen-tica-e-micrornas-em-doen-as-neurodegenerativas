#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EN | Bivariate random-effects meta-analysis of sensitivity and specificity (Reitsma
     model), with a summary ROC curve derived from it.
PT | Meta-analise bivariada de efeitos aleatorios de sensibilidade e especificidade
     (modelo de Reitsma), com curva ROC sumaria derivada dela.

EN | Why this exists, and why pooled AUC was not enough. scripts/05 pools AUC, which is
     what most of the source studies report and therefore what most estimates support.
     But AUC discards the operating point: two tests with the same AUC can be useless and
     excellent at the threshold a clinic would actually use. The instrument the field
     expects for diagnostic accuracy is the bivariate model of Reitsma et al., which keeps
     sensitivity and specificity together, models the negative correlation between them
     that a shifting threshold induces, and yields a summary ROC curve. Its absence is a
     standard reviewer objection, and an AUC-only synthesis cannot answer it.
PT | Por que isto existe, e por que a AUC agrupada nao bastava. O scripts/05 agrupa AUC,
     que e o que a maioria dos estudos-fonte reporta e portanto o que a maioria das
     estimativas sustenta. Mas a AUC descarta o ponto de operacao: dois testes com a mesma
     AUC podem ser inuteis e excelentes no limiar que a clinica de fato usaria. O
     instrumento que o campo espera para acuracia diagnostica e o modelo bivariado de
     Reitsma et al., que mantem sensibilidade e especificidade juntas, modela a correlacao
     negativa entre elas que um limiar deslizante induz, e produz uma curva ROC sumaria. A
     ausencia dele e objecao padrao de revisor, e uma sintese so de AUC nao a responde.

EN | The model. For study i with a complete 2x2 table, the observed logit sensitivity and
     logit specificity are taken as bivariate normal around study-specific true values,
     which are themselves bivariate normal around the summary point:

         (logit se_i, logit sp_i)' ~ N( mu , Sigma_between + S_i )

     S_i is the within-study covariance, diagonal, with 1/TP + 1/FN and 1/TN + 1/FP on
     the diagonal. Sigma_between carries tau_se, tau_sp and their correlation rho. The
     five parameters are fitted by maximum likelihood and their standard errors come from
     a numerical Hessian of the negative log-likelihood.
PT | O modelo. Para o estudo i com tabela 2x2 completa, o logito da sensibilidade e o da
     especificidade observados sao normais bivariados em torno dos valores verdadeiros do
     estudo, que por sua vez sao normais bivariados em torno do ponto sumario:

         (logit se_i, logit sp_i)' ~ N( mu , Sigma_entre + S_i )

     S_i e a covariancia intra-estudo, diagonal, com 1/TP + 1/FN e 1/TN + 1/FP na
     diagonal. Sigma_entre carrega tau_se, tau_sp e a correlacao rho entre eles. Os cinco
     parametros sao ajustados por maxima verossimilhanca e os erros-padrao vem de uma
     hessiana numerica da log-verossimilhanca negativa.

EN | What this synthesis can and cannot carry. Nine studies for five parameters is at the
     lower end of what the bivariate model tolerates, so the between-study terms are
     poorly determined and the summary point is the part to read. The script therefore
     validates its own estimator against simulated data with known parameters before
     touching the real table, and refuses to report if the recovery test fails.
PT | O que esta sintese aguenta e o que nao aguenta. Nove estudos para cinco parametros
     esta no limite inferior do que o modelo bivariado tolera, entao os termos entre
     estudos ficam mal determinados e o ponto sumario e a parte a ser lida. Por isso o
     script valida o proprio estimador contra dados simulados de parametros conhecidos
     antes de tocar na tabela real, e se recusa a reportar se o teste de recuperacao
     falhar.

    python scripts/15_bivariate_srocc.py

EN | Reference: Reitsma JB, Glas AS, Rutjes AWS, Scholten RJPM, Bossuyt PM, Zwinderman
     AH. Bivariate analysis of sensitivity and specificity produces informative summary
     measures in diagnostic reviews. J Clin Epidemiol. 2005;58(10):982-990.
PT | Referencia: Reitsma JB, Glas AS, Rutjes AWS, Scholten RJPM, Bossuyt PM, Zwinderman
     AH. Bivariate analysis of sensitivity and specificity produces informative summary
     measures in diagnostic reviews. J Clin Epidemiol. 2005;58(10):982-990.
"""

import csv
import json
import math
import os
import sys

import numpy as np
from scipy.optimize import minimize
from scipy.stats import norm
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _bilingual import LANGS, t, fig_path

EXTRACTION = "data/extracted/diagnostic_accuracy_extraction.csv"
TAB_DIR = "results/tables"
FIG_DIR = "results/figures"


def logit(p):
    return math.log(p / (1.0 - p))


def expit(x):
    return 1.0 / (1.0 + math.exp(-x))


def study_id(row):
    """EN/PT: PMID when the study has one, DOI otherwise."""
    pmid = str(row.get("pmid", "")).strip()
    if pmid.endswith(".0"):
        pmid = pmid[:-2]
    return pmid or str(row.get("doi", "")).strip().lower()


# --------------------------------------------------------------------------
# Estimator | Estimador
# --------------------------------------------------------------------------
def unpack(theta):
    """EN/PT: mu1, mu2, log tau1, log tau2, atanh rho -> the natural parameters."""
    mu1, mu2, lt1, lt2, zr = theta
    return mu1, mu2, math.exp(lt1), math.exp(lt2), math.tanh(zr)


def neg_loglik(theta, y, v):
    """
    EN | Negative log-likelihood of the bivariate random-effects model. Parameterised so
         the optimiser is unconstrained: the two between-study standard deviations enter
         as logs and the correlation through atanh, which keeps tau > 0 and |rho| < 1
         without bounds.
    PT | Log-verossimilhanca negativa do modelo bivariado de efeitos aleatorios.
         Parametrizada para que o otimizador seja irrestrito: os dois desvios entre
         estudos entram como logaritmos e a correlacao por atanh, o que mantem tau > 0 e
         |rho| < 1 sem limites explicitos.
    """
    mu1, mu2, t1, t2, rho = unpack(theta)
    between = np.array([[t1 * t1, rho * t1 * t2],
                        [rho * t1 * t2, t2 * t2]])
    total = 0.0
    for yi, vi in zip(y, v):
        S = between + np.diag(vi)
        det = S[0, 0] * S[1, 1] - S[0, 1] * S[1, 0]
        if det <= 0 or not np.isfinite(det):
            return 1e12
        d = yi - np.array([mu1, mu2])
        inv = np.array([[S[1, 1], -S[0, 1]], [-S[1, 0], S[0, 0]]]) / det
        total += math.log(det) + float(d @ inv @ d)
    return 0.5 * total


def numerical_hessian(fun, theta, eps=1e-4):
    """EN/PT: central-difference Hessian, used for the standard errors."""
    n = len(theta)
    H = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            tpp, tpm, tmp, tmm = (np.array(theta, float) for _ in range(4))
            tpp[i] += eps; tpp[j] += eps
            tpm[i] += eps; tpm[j] -= eps
            tmp[i] -= eps; tmp[j] += eps
            tmm[i] -= eps; tmm[j] -= eps
            H[i, j] = (fun(tpp) - fun(tpm) - fun(tmp) + fun(tmm)) / (4 * eps * eps)
    return (H + H.T) / 2.0


def fit_bivariate(y, v):
    """EN/PT: maximum likelihood fit, from several starts so a local optimum is visible."""
    y = [np.asarray(a, float) for a in y]
    v = [np.asarray(a, float) for a in v]
    best = None
    starts = [
        [np.mean([a[0] for a in y]), np.mean([a[1] for a in y]), math.log(0.5), math.log(0.5), 0.0],
        [0.0, 0.0, math.log(0.2), math.log(0.2), 0.5],
        [1.0, 1.0, math.log(1.0), math.log(1.0), -0.5],
    ]
    for s in starts:
        r = minimize(neg_loglik, s, args=(y, v), method="Nelder-Mead",
                     options=dict(maxiter=20000, maxfev=20000, xatol=1e-8, fatol=1e-10))
        if best is None or r.fun < best.fun:
            best = r
    mu1, mu2, t1, t2, rho = unpack(best.x)
    H = numerical_hessian(lambda th: neg_loglik(th, y, v), best.x)
    try:
        cov = np.linalg.inv(H)
        se = np.sqrt(np.clip(np.diag(cov), 0.0, None))
    except np.linalg.LinAlgError:
        cov, se = None, np.full(5, np.nan)
    return dict(mu_sens=mu1, mu_spec=mu2, tau_sens=t1, tau_spec=t2, rho=rho,
                se_mu_sens=float(se[0]), se_mu_spec=float(se[1]),
                neg_loglik=float(best.fun), converged=bool(best.success), theta=list(best.x))


def self_test(seed=20260923, n_studies=400):
    """
    EN | Recover known parameters from simulated data. An estimator written once and never
         checked is a guess with a confidence interval attached. Many studies are used
         here so the check is about the estimator, not about small-sample behaviour.
    PT | Recupera parametros conhecidos de dados simulados. Um estimador escrito uma vez e
         nunca conferido e um chute com intervalo de confianca em volta. Usa-se muitos
         estudos aqui para que o teste seja sobre o estimador, nao sobre amostra pequena.
    """
    rng = np.random.default_rng(seed)
    true = dict(mu_sens=logit(0.82), mu_spec=logit(0.74), tau_sens=0.45,
                tau_spec=0.55, rho=-0.40)
    B = np.array([[true["tau_sens"] ** 2, true["rho"] * true["tau_sens"] * true["tau_spec"]],
                  [true["rho"] * true["tau_sens"] * true["tau_spec"], true["tau_spec"] ** 2]])
    y, v = [], []
    for _ in range(n_studies):
        theta_i = rng.multivariate_normal([true["mu_sens"], true["mu_spec"]], B)
        nd, nh = 120, 120
        tp = max(1, min(nd - 1, rng.binomial(nd, expit(theta_i[0]))))
        tn = max(1, min(nh - 1, rng.binomial(nh, expit(theta_i[1]))))
        fn, fp = nd - tp, nh - tn
        y.append([logit(tp / nd), logit(tn / nh)])
        v.append([1.0 / tp + 1.0 / fn, 1.0 / tn + 1.0 / fp])
    got = fit_bivariate(y, v)
    ok, report = True, {}
    for key, tol in (("mu_sens", 0.15), ("mu_spec", 0.15),
                     ("tau_sens", 0.15), ("tau_spec", 0.15), ("rho", 0.25)):
        err = abs(got[key] - true[key])
        report[key] = dict(true=round(true[key], 4), fitted=round(got[key], 4),
                           abs_error=round(err, 4), tolerance=tol, pass_=bool(err <= tol))
        ok = ok and err <= tol
    return ok, report


# --------------------------------------------------------------------------
# Data | Dados
# --------------------------------------------------------------------------
def two_by_two(row):
    """
    EN | Reconstruct the 2x2 table from sensitivity, specificity and the group sizes, with
         the usual 0.5 continuity correction when a cell would be empty. The counts are
         rounded, so they are a reconstruction and not the published table; the note in
         the output says so.
    PT | Reconstroi a tabela 2x2 a partir de sensibilidade, especificidade e tamanhos de
         grupo, com a correcao de continuidade usual de 0,5 quando uma celula ficaria
         vazia. As contagens sao arredondadas, entao sao reconstrucao e nao a tabela
         publicada; a nota na saida diz isso.
    """
    nd, nh = int(float(row["n_cases"])), int(float(row["n_controls"]))
    se, sp = float(row["sensitivity"]), float(row["specificity"])
    tp = round(se * nd); fn = nd - tp
    tn = round(sp * nh); fp = nh - tn
    cells = [tp, fn, tn, fp]
    corrected = any(c == 0 for c in cells)
    if corrected:
        tp, fn, tn, fp = (c + 0.5 for c in cells)
    return tp, fn, tn, fp, corrected


def load_pairs():
    rows = list(csv.DictReader(open(EXTRACTION, encoding="utf-8")))
    usable = [r for r in rows
              if r["eligible_primary_pool"] == "yes"
              and r["sensitivity"] and r["specificity"]
              and r["n_cases"] and r["n_controls"]]
    by_study = {}
    for r in usable:
        by_study.setdefault(study_id(r), []).append(r)

    # EN | One estimate per study, chosen as the one whose AUC is closest to that study's
    #      median AUC. This matches the convention scripts/05 already uses for its
    #      one-estimate-per-study sensitivity analysis, so the two syntheses describe the
    #      same representative estimates rather than two different subsets.
    # PT | Uma estimativa por estudo, a de AUC mais proxima da mediana daquele estudo. E a
    #      mesma convencao que o scripts/05 ja usa na analise de sensibilidade de uma
    #      estimativa por estudo, entao as duas sinteses descrevem as mesmas estimativas
    #      representativas e nao dois subconjuntos diferentes.
    chosen = []
    for sid, rs in sorted(by_study.items()):
        with_auc = [r for r in rs if r["auc"]]
        pick = rs[0]
        if with_auc:
            med = float(np.median([float(r["auc"]) for r in with_auc]))
            pick = min(with_auc, key=lambda r: abs(float(r["auc"]) - med))
        chosen.append(pick)
    return usable, chosen


def prepare(rows):
    y, v, meta = [], [], []
    for r in rows:
        tp, fn, tn, fp, corrected = two_by_two(r)
        y.append([logit(tp / (tp + fn)), logit(tn / (tn + fp))])
        v.append([1.0 / tp + 1.0 / fn, 1.0 / tn + 1.0 / fp])
        meta.append(dict(record_id=r["record_id"], study_id=study_id(r),
                         first_author=r["first_author"], year=r["year"],
                         disease=r["disease"], marker=r["marker"],
                         sensitivity=float(r["sensitivity"]),
                         specificity=float(r["specificity"]),
                         n_cases=int(float(r["n_cases"])),
                         n_controls=int(float(r["n_controls"])),
                         continuity_corrected=corrected))
    return y, v, meta


def summarise(fit, label, k, n_studies):
    se_ = expit(fit["mu_sens"]); sp_ = expit(fit["mu_spec"])
    out = dict(
        analysis=label, k_estimates=k, n_studies=n_studies,
        summary_sensitivity=round(se_, 4),
        sensitivity_ci_low=round(expit(fit["mu_sens"] - 1.96 * fit["se_mu_sens"]), 4),
        sensitivity_ci_high=round(expit(fit["mu_sens"] + 1.96 * fit["se_mu_sens"]), 4),
        summary_specificity=round(sp_, 4),
        specificity_ci_low=round(expit(fit["mu_spec"] - 1.96 * fit["se_mu_spec"]), 4),
        specificity_ci_high=round(expit(fit["mu_spec"] + 1.96 * fit["se_mu_spec"]), 4),
        tau_sensitivity=round(fit["tau_sens"], 4),
        tau_specificity=round(fit["tau_spec"], 4),
        rho_between=round(fit["rho"], 4),
        diagnostic_odds_ratio=round((se_ / (1 - se_)) * (sp_ / (1 - sp_)), 3),
        positive_likelihood_ratio=round(se_ / (1 - sp_), 3),
        negative_likelihood_ratio=round((1 - se_) / sp_, 3),
        converged=fit["converged"],
    )
    return out


def sroc_points(fit, n=200):
    """
    EN | The summary ROC line is the conditional expectation of logit sensitivity given
         logit specificity under the fitted bivariate normal. That is exactly what the
         model implies and nothing more; it is not an extra curve fitted to the data.
    PT | A linha ROC sumaria e a esperanca condicional do logito da sensibilidade dado o
         logito da especificidade sob a normal bivariada ajustada. E exatamente o que o
         modelo implica e nada alem; nao e uma curva extra ajustada aos dados.
    """
    if fit["tau_spec"] <= 0:
        return [], []
    slope = fit["rho"] * fit["tau_sens"] / fit["tau_spec"]
    xs, ys = [], []
    for sp_ in np.linspace(0.02, 0.98, n):
        ls = fit["mu_sens"] + slope * (logit(sp_) - fit["mu_spec"])
        xs.append(1.0 - sp_)
        ys.append(expit(ls))
    return xs, ys


def plot(fit, meta, primary, path, lang):
    fig, ax = plt.subplots(figsize=(6.4, 6.0))
    sizes = [30 + 2.2 * (m["n_cases"] + m["n_controls"]) ** 0.5 * 3 for m in meta]
    colours = {"AD": "#1f77b4", "PD": "#d62728"}
    for m, s in zip(meta, sizes):
        ax.scatter(1 - m["specificity"], m["sensitivity"], s=s, alpha=0.45,
                   color=colours.get(m["disease"], "#7f7f7f"),
                   edgecolor="white", linewidth=0.8, zorder=3)
    xs, ys = sroc_points(fit)
    if xs:
        ax.plot(xs, ys, color="black", lw=1.6, zorder=4,
                label=t(lang, "SROC (bivariate)", "ROC sumária (bivariada)"))
    ax.scatter([1 - primary["summary_specificity"]], [primary["summary_sensitivity"]],
               marker="D", s=95, color="black", zorder=5,
               label=(t(lang, "summary  ", "sumário  ") +
                      f"{primary['summary_sensitivity']:.2f} / "
                      f"{primary['summary_specificity']:.2f}"))
    ax.plot([1 - primary["specificity_ci_low"], 1 - primary["specificity_ci_high"]],
            [primary["summary_sensitivity"]] * 2, color="black", lw=1.2, zorder=5)
    ax.plot([1 - primary["summary_specificity"]] * 2,
            [primary["sensitivity_ci_low"], primary["sensitivity_ci_high"]],
            color="black", lw=1.2, zorder=5)
    ax.plot([0, 1], [0, 1], ls=":", color="grey", lw=1)
    for d, c in colours.items():
        ax.scatter([], [], color=c, alpha=0.6, s=60,
                   label=t(lang, f"{d} study", f"estudo de {d}"))
    ax.set_xlim(0, 1); ax.set_ylim(0, 1)
    ax.set_xlabel(t(lang, "1 - specificity", "1 - especificidade"))
    ax.set_ylabel(t(lang, "sensitivity", "sensibilidade"))
    ax.set_title(t(lang,
                   "Bivariate summary ROC\n"
                   f"{primary['n_studies']} studies, one estimate each",
                   "ROC sumária bivariada\n"
                   f"{primary['n_studies']} estudos, uma estimativa cada"), fontsize=10)
    ax.legend(loc="lower right", fontsize=8, frameon=False)
    ax.grid(alpha=0.25)
    fig.tight_layout()
    fig.savefig(path, dpi=600)
    plt.close(fig)


def main():
    os.makedirs(TAB_DIR, exist_ok=True)
    os.makedirs(FIG_DIR, exist_ok=True)

    print("=" * 78)
    print("EN | Bivariate meta-analysis | PT | Meta-analise bivariada")
    print("=" * 78)
    ok, report = self_test()
    print("  estimator self-test on simulated data | autoteste do estimador:")
    for k, r in report.items():
        print(f"    {k:10s} true {r['true']:8.4f}  fitted {r['fitted']:8.4f}  "
              f"|err| {r['abs_error']:.4f} <= {r['tolerance']}  "
              f"{'ok' if r['pass_'] else 'FAIL'}")
    if not ok:
        sys.exit("EN/PT: estimator failed to recover known parameters; refusing to report")

    all_rows, chosen = load_pairs()
    y_all, v_all, meta_all = prepare(all_rows)
    y_one, v_one, meta_one = prepare(chosen)

    fit_one = fit_bivariate(y_one, v_one)
    primary = summarise(fit_one, "one estimate per study | uma estimativa por estudo",
                        len(chosen), len({m["study_id"] for m in meta_one}))
    fit_all = fit_bivariate(y_all, v_all)
    secondary = summarise(fit_all, "every eligible estimate | toda estimativa elegivel",
                          len(all_rows), len({m["study_id"] for m in meta_all}))

    for res in (primary, secondary):
        print(f"\n  {res['analysis']}")
        print(f"    estimates {res['k_estimates']} from {res['n_studies']} studies")
        print(f"    sensitivity {res['summary_sensitivity']:.3f} "
              f"({res['sensitivity_ci_low']:.3f}-{res['sensitivity_ci_high']:.3f})")
        print(f"    specificity {res['summary_specificity']:.3f} "
              f"({res['specificity_ci_low']:.3f}-{res['specificity_ci_high']:.3f})")
        print(f"    DOR {res['diagnostic_odds_ratio']:.2f}   "
              f"LR+ {res['positive_likelihood_ratio']:.2f}   "
              f"LR- {res['negative_likelihood_ratio']:.2f}")
        print(f"    tau_se {res['tau_sensitivity']:.3f}  tau_sp {res['tau_specificity']:.3f}  "
              f"rho {res['rho_between']:.3f}")

    with open(f"{TAB_DIR}/bivariate_summary.csv", "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(primary.keys()))
        w.writeheader(); w.writerows([primary, secondary])

    with open(f"{TAB_DIR}/bivariate_input_estimates.csv", "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(meta_all[0].keys()) + ["in_primary_analysis"])
        w.writeheader()
        primary_ids = {m["record_id"] for m in meta_one}
        for m in meta_all:
            w.writerow({**m, "in_primary_analysis": m["record_id"] in primary_ids})

    for lang in LANGS:
        plot(fit_one, meta_one, primary, fig_path(FIG_DIR, "bivariate_sroc", lang), lang)

    payload = dict(
        model="bivariate random effects (Reitsma et al., J Clin Epidemiol 2005;58:982-990)",
        estimator_self_test=report,
        primary=primary, secondary=secondary,
        fitted_parameters_primary={k: fit_one[k] for k in
                                   ("mu_sens", "mu_spec", "tau_sens", "tau_spec", "rho")},
        note_en=("The 2x2 tables are reconstructed by multiplying published sensitivity and "
                 "specificity by the published group sizes and rounding, because the source "
                 "articles report proportions rather than counts. With nine studies and five "
                 "parameters the between-study terms (tau, rho) are weakly identified and "
                 "should not be interpreted on their own; the summary operating point is what "
                 "this analysis supports. Every included contrast is case versus healthy "
                 "control, so these are upper bounds in the same sense as the pooled AUC."),
        note_pt=("As tabelas 2x2 sao reconstruidas multiplicando sensibilidade e "
                 "especificidade publicadas pelos tamanhos de grupo publicados e "
                 "arredondando, porque os artigos-fonte reportam proporcoes e nao contagens. "
                 "Com nove estudos e cinco parametros, os termos entre estudos (tau, rho) sao "
                 "fracamente identificados e nao devem ser interpretados sozinhos; o ponto "
                 "sumario de operacao e o que esta analise sustenta. Todo contraste incluido e "
                 "caso versus controle saudavel, entao sao limites superiores no mesmo sentido "
                 "que a AUC agrupada."),
    )
    with open(f"{TAB_DIR}/bivariate_model.json", "w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=1)

    print(f"\nEN/PT -> {TAB_DIR}/bivariate_summary.csv")
    print(f"EN/PT -> {TAB_DIR}/bivariate_input_estimates.csv")
    print(f"EN/PT -> {TAB_DIR}/bivariate_model.json")
    for lang in LANGS:
        print(f"EN/PT -> {fig_path(FIG_DIR, 'bivariate_sroc', lang)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
