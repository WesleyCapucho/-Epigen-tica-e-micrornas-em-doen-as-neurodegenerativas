#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EN | GRADE certainty of evidence for the pooled diagnostic accuracy, with a summary of
     findings table expressed as consequences per 1000 people tested.
PT | Certeza da evidencia pelo GRADE para a acuracia diagnostica agrupada, com tabela de
     resumo de achados expressa em consequencias por 1000 pessoas testadas.

EN | Why this exists. A pooled sensitivity and specificity say what the studies found.
     They do not say how much to believe it. GRADE is the instrument that answers the
     second question, and a review that reports the first without the second invites the
     reader to take a number at face value that its own risk-of-bias table undercuts.
PT | Por que isto existe. Sensibilidade e especificidade agrupadas dizem o que os estudos
     acharam. Nao dizem o quanto acreditar. O GRADE e o instrumento que responde a segunda
     pergunta, e uma revisao que reporta a primeira sem a segunda convida o leitor a levar
     ao pe da letra um numero que a propria tabela de risco de vies derruba.

EN | How the rating is made. Accuracy studies start at HIGH certainty and are downgraded
     across five domains. Every downgrade here is DERIVED BY A STATED RULE from a number
     already in the repository - the QUADAS-2 table, the heterogeneity statistics, the
     Egger test, the width of the bivariate confidence interval - so the rating can be
     argued with by changing a threshold rather than by disputing a judgement call.
     Where GRADE asks for judgement the thresholds are written down in THRESHOLDS below.
PT | Como a classificacao e feita. Estudos de acuracia comecam em certeza ALTA e sao
     rebaixados em cinco dominios. Todo rebaixamento aqui e DERIVADO DE UMA REGRA
     DECLARADA sobre um numero que ja esta no repositorio - a tabela QUADAS-2, as
     estatisticas de heterogeneidade, o teste de Egger, a largura do intervalo de
     confianca bivariado - de modo que a classificacao pode ser contestada mudando um
     limiar, e nao discutindo um juizo. Onde o GRADE pede julgamento, os limiares estao
     escritos em THRESHOLDS abaixo.

EN | The summary of findings table follows GRADE practice for diagnostic tests: the
     summary sensitivity and specificity are applied to a hypothetical cohort of 1000
     people at a stated pre-test probability, and the table reports true and false
     positives and negatives. A test is judged by the mistakes it makes at the prevalence
     where it would be used, not by its area under a curve.
PT | A tabela de resumo de achados segue a pratica GRADE para testes diagnosticos: a
     sensibilidade e a especificidade sumarias sao aplicadas a uma coorte hipotetica de
     1000 pessoas numa probabilidade pre-teste declarada, e a tabela reporta verdadeiros e
     falsos positivos e negativos. Um teste se julga pelos erros que comete na prevalencia
     em que seria usado, nao pela area sob uma curva.

    python scripts/16_grade_certainty.py

EN | References:
     Schunemann HJ, Mustafa RA, Brozek J, et al. GRADE guidelines: 21 part 1 and part 2.
     Test accuracy: rating the certainty of evidence. J Clin Epidemiol. 2020;122:129-141
     and 142-152.
PT | Referencias:
     Schunemann HJ, Mustafa RA, Brozek J, et al. GRADE guidelines: 21 parte 1 e parte 2.
     Test accuracy: rating the certainty of evidence. J Clin Epidemiol. 2020;122:129-141
     e 142-152.
"""

import csv
import json
import os
import sys
from collections import OrderedDict

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _bilingual import LANGS, t, fig_path

QUADAS = "results/tables/quadas2_assessment.csv"
POOLED = "results/tables/meta_analysis_pooled_auc.csv"
BIVARIATE = "results/tables/bivariate_summary.csv"
TAB_DIR = "results/tables"
FIG_DIR = "results/figures"

LEVELS = ["very low", "low", "moderate", "high"]

# EN | Where GRADE asks for a judgement, the number that triggers it is written here
#      rather than decided case by case. Disagree with a threshold and you can move it.
# PT | Onde o GRADE pede julgamento, o numero que o dispara esta aqui e nao e decidido
#      caso a caso. Discorde de um limiar e voce pode move-lo.
THRESHOLDS = OrderedDict([
    ("risk_of_bias_serious_fraction", 0.50),
    ("risk_of_bias_very_serious_fraction", 0.75),
    ("inconsistency_serious_i2", 50.0),
    ("inconsistency_very_serious_i2", 90.0),
    ("imprecision_serious_ci_width", 0.20),
    ("imprecision_very_serious_ci_width", 0.40),
    ("publication_bias_egger_p", 0.05),
    ("indirectness_serious_fraction_high_applicability", 0.50),
])

# EN/PT: pre-test probabilities the summary of findings table is computed at
PREVALENCES = [0.05, 0.20, 0.50]


def downgrade(n):
    return {0: ("not serious", "nao serio"), 1: ("serious", "serio"),
            2: ("very serious", "muito serio")}[n]


def rate_risk_of_bias(quadas):
    """
    EN | GRADE domain 1. Driven by the QUADAS-2 table: the fraction of studies at high
         risk in any risk-of-bias domain.
    PT | Dominio 1 do GRADE. Guiado pela tabela QUADAS-2: a fracao de estudos em alto
         risco em qualquer dominio de risco de vies.
    """
    dom = ["rob_patient_selection", "rob_index_test",
           "rob_reference_standard", "rob_flow_timing"]
    n = len(quadas)
    high = sum(1 for r in quadas if any(r[d] == "high" for d in dom))
    frac = high / n if n else 0.0
    if frac >= THRESHOLDS["risk_of_bias_very_serious_fraction"]:
        steps = 2
    elif frac >= THRESHOLDS["risk_of_bias_serious_fraction"]:
        steps = 1
    else:
        steps = 0
    return steps, (f"{high} of {n} studies are at high risk of bias in at least one "
                   f"QUADAS-2 domain ({100 * frac:.0f}%)")


def rate_indirectness(quadas):
    """
    EN | GRADE domain 2. The applicability half of QUADAS-2 answers this directly: does
         the evidence address the question the review asks? Here it does not, because
         every pooled contrast is patients against healthy people rather than against the
         conditions a clinician must rule out.
    PT | Dominio 2 do GRADE. A metade de aplicabilidade do QUADAS-2 responde direto: a
         evidencia trata da pergunta que a revisao faz? Aqui nao trata, porque todo
         contraste agrupado e paciente contra pessoa saudavel e nao contra as condicoes
         que o clinico precisa descartar.
    """
    n = len(quadas)
    high = sum(1 for r in quadas if r["app_patient_selection"] == "high")
    frac = high / n if n else 0.0
    steps = 1 if frac >= THRESHOLDS["indirectness_serious_fraction_high_applicability"] else 0
    return steps, (f"{high} of {n} studies raise high applicability concern for patient "
                   f"selection ({100 * frac:.0f}%): the pooled contrast is case versus "
                   "healthy control, not the differential diagnosis a clinician faces")


def rate_inconsistency(pooled_row):
    i2 = float(pooled_row["I2_percent"])
    if i2 >= THRESHOLDS["inconsistency_very_serious_i2"]:
        steps = 2
    elif i2 >= THRESHOLDS["inconsistency_serious_i2"]:
        steps = 1
    else:
        steps = 0
    return steps, f"I2 = {i2:.1f}% across the pooled estimates"


def rate_imprecision(biv_row):
    """
    EN | GRADE domain 4, judged on the width of the confidence interval around the summary
         operating point, because that is the quantity a reader would act on.
    PT | Dominio 4 do GRADE, julgado pela largura do intervalo de confianca em torno do
         ponto sumario de operacao, porque e essa a grandeza sobre a qual se agiria.
    """
    widths = {
        "sensitivity": float(biv_row["sensitivity_ci_high"]) - float(biv_row["sensitivity_ci_low"]),
        "specificity": float(biv_row["specificity_ci_high"]) - float(biv_row["specificity_ci_low"]),
    }
    worst = max(widths.values())
    if worst >= THRESHOLDS["imprecision_very_serious_ci_width"]:
        steps = 2
    elif worst >= THRESHOLDS["imprecision_serious_ci_width"]:
        steps = 1
    else:
        steps = 0
    return steps, (f"widest 95% interval around the summary point is "
                   f"{worst:.3f} (sensitivity {widths['sensitivity']:.3f}, "
                   f"specificity {widths['specificity']:.3f})")


def rate_publication_bias(pooled_row):
    p = float(pooled_row["egger_p"])
    steps = 1 if p < THRESHOLDS["publication_bias_egger_p"] else 0
    verdict = "strongly suspected" if steps else "not detected"
    return steps, f"Egger test p = {p:.4g} on the pooled estimates, {verdict}"


def summary_of_findings(sens, spec, prevalence):
    """EN/PT: consequences per 1000 people tested at a stated pre-test probability."""
    diseased = 1000.0 * prevalence
    healthy = 1000.0 - diseased
    tp = sens * diseased
    fn = diseased - tp
    tn = spec * healthy
    fp = healthy - tn
    ppv = tp / (tp + fp) if (tp + fp) else float("nan")
    npv = tn / (tn + fn) if (tn + fn) else float("nan")
    return OrderedDict([
        ("pre_test_probability", prevalence),
        ("true_positives_per_1000", round(tp, 1)),
        ("false_negatives_per_1000", round(fn, 1)),
        ("true_negatives_per_1000", round(tn, 1)),
        ("false_positives_per_1000", round(fp, 1)),
        ("positive_predictive_value", round(ppv, 4)),
        ("negative_predictive_value", round(npv, 4)),
    ])


def plot(sof, certainty, path, lang):
    """EN/PT: what the test does to 1000 people, at each pre-test probability."""
    fig, axes = plt.subplots(1, len(sof), figsize=(3.5 * len(sof), 4.4), sharey=True)
    if len(sof) == 1:
        axes = [axes]
    keys = [("true_positives_per_1000", "#2e8b57",
             t(lang, "correctly identified as diseased", "identificados corretamente como doentes")),
            ("false_negatives_per_1000", "#c0392b",
             t(lang, "missed cases", "casos perdidos")),
            ("true_negatives_per_1000", "#7fb3d5",
             t(lang, "correctly cleared", "corretamente liberados")),
            ("false_positives_per_1000", "#e59866",
             t(lang, "false alarms", "alarmes falsos"))]
    for ax, row in zip(axes, sof):
        bottom = 0.0
        for key, colour, _lab in keys:
            v = row[key]
            ax.bar(0, v, bottom=bottom, color=colour, width=0.62, edgecolor="white")
            if v >= 45:
                ax.text(0, bottom + v / 2, f"{v:.0f}", ha="center", va="center",
                        fontsize=9, color="white" if colour != "#7fb3d5" else "#123")
            bottom += v
        ax.set_xticks([])
        ax.set_title(t(lang, f"pre-test probability {row['pre_test_probability']:.0%}",
                       f"probabilidade pré-teste {row['pre_test_probability']:.0%}"),
                     fontsize=9.5)
        ax.set_xlabel(t(lang,
                        f"PPV {row['positive_predictive_value']:.2f}  ·  "
                        f"NPV {row['negative_predictive_value']:.2f}",
                        f"VPP {row['positive_predictive_value']:.2f}  ·  "
                        f"VPN {row['negative_predictive_value']:.2f}"), fontsize=8.5)
        ax.spines[["top", "right"]].set_visible(False)
    axes[0].set_ylabel(t(lang, "people per 1000 tested", "pessoas por 1000 testadas"))
    handles = [plt.Rectangle((0, 0), 1, 1, color=c) for _, c, _ in keys]
    fig.legend(handles, [lab for _, _, lab in keys], loc="lower center",
               ncol=2, fontsize=8.5, frameon=False, bbox_to_anchor=(0.5, -0.08))
    cert = {"high": t(lang, "high", "alta"), "moderate": t(lang, "moderate", "moderada"),
            "low": t(lang, "low", "baixa"), "very low": t(lang, "very low", "muito baixa")}[certainty]
    fig.suptitle(t(lang,
                   "What the pooled test does to 1000 people\n"
                   f"GRADE certainty of evidence: {cert}",
                   "O que o teste agrupado faz com 1000 pessoas\n"
                   f"Certeza da evidência pelo GRADE: {cert}"), fontsize=11)
    fig.tight_layout()
    fig.savefig(path, dpi=600, bbox_inches="tight")
    plt.close(fig)


def main():
    os.makedirs(TAB_DIR, exist_ok=True)
    os.makedirs(FIG_DIR, exist_ok=True)
    for f in (QUADAS, POOLED, BIVARIATE):
        if not os.path.exists(f):
            sys.exit(f"EN/PT: missing {f}; run scripts/05, 14 and 15 first")

    quadas = list(csv.DictReader(open(QUADAS, encoding="utf-8")))
    pooled = list(csv.DictReader(open(POOLED, encoding="utf-8")))
    biv = list(csv.DictReader(open(BIVARIATE, encoding="utf-8")))
    overall = next(r for r in pooled if r["subgroup"].startswith("Overall"))
    primary = next(r for r in biv if r["analysis"].startswith("one estimate per study"))

    domains = OrderedDict()
    for name, (steps, why) in [
        ("risk_of_bias", rate_risk_of_bias(quadas)),
        ("indirectness", rate_indirectness(quadas)),
        ("inconsistency", rate_inconsistency(overall)),
        ("imprecision", rate_imprecision(primary)),
        ("publication_bias", rate_publication_bias(overall)),
    ]:
        en, pt = downgrade(steps)
        domains[name] = OrderedDict([("downgrade_steps", steps), ("judgement_en", en),
                                     ("judgement_pt", pt), ("reason", why)])

    total = sum(d["downgrade_steps"] for d in domains.values())
    idx = max(0, len(LEVELS) - 1 - total)
    certainty = LEVELS[idx]

    sof = [summary_of_findings(float(primary["summary_sensitivity"]),
                               float(primary["summary_specificity"]), p)
           for p in PREVALENCES]

    print("=" * 78)
    print("EN | GRADE certainty of evidence | PT | Certeza da evidencia pelo GRADE")
    print("=" * 78)
    print(f"  starting certainty for accuracy studies : high")
    for name, d in domains.items():
        print(f"  {name:18s} -{d['downgrade_steps']}  {d['judgement_en']:13s} {d['reason']}")
    print(f"  total downgrade steps                   : {total}")
    print(f"  CERTAINTY OF EVIDENCE                   : {certainty.upper()}")
    print("\n  Summary of findings, per 1000 people tested:")
    for row in sof:
        print(f"    pre-test {row['pre_test_probability']:.0%}: "
              f"TP {row['true_positives_per_1000']:6.1f}  FN {row['false_negatives_per_1000']:6.1f}  "
              f"TN {row['true_negatives_per_1000']:6.1f}  FP {row['false_positives_per_1000']:6.1f}  "
              f"PPV {row['positive_predictive_value']:.2f}  NPV {row['negative_predictive_value']:.2f}")

    with open(f"{TAB_DIR}/grade_summary_of_findings.csv", "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(sof[0].keys()))
        w.writeheader()
        w.writerows(sof)

    payload = OrderedDict([
        ("instrument", "GRADE for diagnostic test accuracy (Schunemann et al., "
                       "J Clin Epidemiol 2020;122:129-141 and 142-152)"),
        ("starting_certainty", "high"),
        ("thresholds", THRESHOLDS),
        ("domains", domains),
        ("total_downgrade_steps", total),
        ("certainty_of_evidence", certainty),
        ("summary_sensitivity", float(primary["summary_sensitivity"])),
        ("summary_specificity", float(primary["summary_specificity"])),
        ("summary_of_findings", sof),
        ("reading_en",
         "Certainty is very low, and the five domains that put it there are not "
         "independent afflictions of a few weak studies: every pooled estimate comes from "
         "a case-versus-healthy-control design with a threshold chosen in the same sample, "
         "heterogeneity is near total, and the funnel is asymmetric. The summary of "
         "findings is the part to quote. At a pre-test probability of 5%, the order of a "
         "screening setting, the pooled test returns 301 positives per 1000 people tested, "
         "of which 261 are false: 40 real cases found at the cost of 261 people sent for "
         "unnecessary further work-up, a positive predictive value of 0.13. The test is "
         "better at ruling out than ruling in, with a negative predictive value of 0.99 at "
         "that prevalence, and that asymmetry is the honest way to describe it."),
        ("reading_pt",
         "A certeza e muito baixa, e os cinco dominios que a levaram ate la nao sao males "
         "independentes de alguns estudos fracos: toda estimativa agrupada vem de um "
         "desenho caso-versus-controle-saudavel com limiar escolhido na mesma amostra, a "
         "heterogeneidade e quase total e o funil e assimetrico. A tabela de resumo de "
         "achados e a parte a citar. Numa probabilidade pre-teste de 5%, a ordem de um "
         "cenario de rastreio, o teste agrupado devolve 301 positivos por 1000 pessoas "
         "testadas, dos quais 261 sao falsos: 40 casos reais encontrados ao custo de 261 "
         "pessoas encaminhadas para investigacao desnecessaria, um valor preditivo positivo "
         "de 0,13. O teste e melhor para descartar que para confirmar, com valor preditivo "
         "negativo de 0,99 nessa prevalencia, e essa assimetria e o jeito honesto de "
         "descreve-lo."),
    ])
    with open(f"{TAB_DIR}/grade_certainty.json", "w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=1)

    for lang in LANGS:
        plot(sof, certainty, fig_path(FIG_DIR, "grade_summary_of_findings", lang), lang)

    print(f"\nEN/PT -> {TAB_DIR}/grade_summary_of_findings.csv")
    print(f"EN/PT -> {TAB_DIR}/grade_certainty.json")
    for lang in LANGS:
        print(f"EN/PT -> {fig_path(FIG_DIR, 'grade_summary_of_findings', lang)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
