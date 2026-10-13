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
import _viz_style  # noqa: F401  (applies the shared figure style)

QUADAS = "results/tables/quadas2_assessment.csv"
POOLED_PRIMARY = "results/tables/meta_analysis_pooled_auc_primary.csv"
POOLED_SENS = "results/tables/meta_analysis_pooled_auc_sensitivity_every_estimate.csv"
BIVARIATE = "results/tables/bivariate_summary.csv"
SELECTION_AUDIT = "results/tables/one_estimate_per_study_selection_audit.csv"
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
    ("publication_bias_min_studies_for_test", 10),
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

         This is not the same fact as risk_of_bias's patient-selection downgrade, even
         though both trace back to the case-versus-healthy-control design, and rating
         both is not double-counting one reason twice. Risk of bias asks whether the
         design threatens the INTERNAL VALIDITY of the accuracy estimate the studies
         report for their own case-versus-control comparison (selection effects that
         inflate apparent separation between groups); indirectness asks whether that
         comparison, however validly estimated, answers the EXTERNAL question this
         review poses (discriminating diagnostically uncertain patients, not healthy
         volunteers). A single design choice can be a genuine, independent threat to
         both, and GRADE guidance for diagnostic test accuracy treats a case-control
         design exactly this way (Schunemann et al. 2020, part 1).
    PT | Dominio 2 do GRADE. A metade de aplicabilidade do QUADAS-2 responde direto: a
         evidencia trata da pergunta que a revisao faz? Aqui nao trata, porque todo
         contraste agrupado e paciente contra pessoa saudavel e nao contra as condicoes
         que o clinico precisa descartar.

         Isso nao e o mesmo fato do rebaixamento de selecao de pacientes do risk_of_bias,
         mesmo que ambos remontem ao desenho caso-versus-controle-saudavel, e avaliar os
         dois nao e contar o mesmo motivo duas vezes. Risco de vies pergunta se o desenho
         ameaca a VALIDADE INTERNA da estimativa de acuracia que os estudos reportam para
         sua propria comparacao caso-versus-controle (efeitos de selecao que inflam a
         separacao aparente entre os grupos); indiretividade pergunta se essa comparacao,
         por mais validamente estimada que seja, responde a pergunta EXTERNA que esta
         revisao coloca (discriminar pacientes com incerteza diagnostica, nao voluntarios
         saudaveis). Uma unica escolha de desenho pode ser uma ameaca genuina e
         independente a ambas, e a orientacao do GRADE para acuracia de teste diagnostico
         trata exatamente assim um desenho caso-controle (Schunemann et al. 2020, parte 1).
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


def rate_imprecision(primary_row):
    """
    EN | GRADE domain 4, judged on the width of the modified Hartung-Knapp (mHK) 95%
         confidence interval around the disease's primary pooled AUC (one estimate per
         study), because that is the quantity a reader would act on. The 0.20/0.40
         AUC-width thresholds in THRESHOLDS are not a validated, literature-derived
         minimal clinically important difference for a microRNA test; they are this
         review's own stated cutoff for "a difference in AUC wide enough that two
         readers could reasonably disagree about whether the test is useful", applied
         identically to both diseases so the judgement is reproducible rather than
         calibrated after seeing the result. The number of contributing studies and the
         95% prediction interval - the wider range a new study's true AUC would be
         expected to fall in - are reported alongside the CI width for the same
         judgement, since a narrow confidence interval built from few studies with an
         even wider prediction interval is a different, weaker kind of precision than a
         narrow interval built from many consistent studies.
    PT | Dominio 4 do GRADE, julgado pela largura do intervalo de confianca de
         Hartung-Knapp modificado (mHK) a 95% em torno da AUC agrupada primaria da doenca
         (uma estimativa por estudo), porque e essa a grandeza sobre a qual se agiria. Os
         limiares de largura de AUC 0,20/0,40 em THRESHOLDS nao sao uma diferenca minima
         clinicamente importante validada e derivada da literatura para um teste de
         microRNA; sao o limiar proprio e declarado desta revisao para "uma diferenca de
         AUC larga o bastante para que dois leitores pudessem razoavelmente discordar se
         o teste e util", aplicado identicamente as duas doencas para que o julgamento
         seja reproduzivel e nao calibrado apos ver o resultado. O numero de estudos
         contribuintes e o intervalo de predicao a 95% - a faixa mais larga em que a AUC
         verdadeira de um novo estudo cairia - sao reportados junto a largura do IC para
         o mesmo julgamento, ja que um IC estreito construido de poucos estudos com um
         intervalo de predicao ainda mais largo e um tipo de precisao diferente, mais
         fraco, do que um IC estreito construido de muitos estudos consistentes.
    """
    lo, hi = primary_row["ci_low_hk"], primary_row["ci_high_hk"]
    width = (float(hi) - float(lo)) if (lo not in ("", None) and hi not in ("", None)) else float("nan")
    if width != width:  # NaN
        return 0, "confidence interval not estimable at this k; imprecision not rated from it"
    if width >= THRESHOLDS["imprecision_very_serious_ci_width"]:
        steps = 2
    elif width >= THRESHOLDS["imprecision_serious_ci_width"]:
        steps = 1
    else:
        steps = 0
    pi_lo, pi_hi = primary_row.get("pi_low"), primary_row.get("pi_high")
    pi_txt = (f"; 95% prediction interval {float(pi_lo):.3f}-{float(pi_hi):.3f}"
              if pi_lo not in ("", None) and pi_hi not in ("", None) else "")
    return steps, (f"95% modified Hartung-Knapp (mHK) interval around the primary pooled AUC "
                   f"({int(primary_row['n_studies'])} studies) spans "
                   f"{width:.3f} ({float(lo):.3f}-{float(hi):.3f}){pi_txt}")


def rate_publication_bias(sens_row, primary_row):
    """
    EN | GRADE domain 5. A significant Egger intercept is evidence of
         small-study effects (funnel-plot asymmetry), which is necessary but
         not sufficient for publication/dissemination bias specifically:
         heterogeneity, true differences correlated with study size, and
         chance can all produce the same asymmetry. Funnel-plot tests are
         also underpowered and unstable below about ten independent studies,
         and the every-estimate pool treats correlated rows from one study as
         independent. So the test result no longer triggers a downgrade by
         itself. The rule, revised after the 2026-09-28 audit showed the
         every-estimate Egger verdict flipping between diseases when one
         study's implausible CI was corrected: with fewer than
         publication_bias_min_studies_for_test independent studies in the
         primary pool the domain is judged "not assessable by statistical
         test" and not downgraded on the test; with at least that many, one
         step is taken only when the Egger test is significant on BOTH the
         one-estimate-per-study pool and the every-estimate pool. Both
         p-values are always reported so a reader can apply a stricter rule.
    PT | Dominio 5 do GRADE. Um intercepto de Egger significativo e evidencia
         de efeitos de estudos pequenos (assimetria do funil), necessario mas
         nao suficiente para vies de publicacao/disseminacao: heterogeneidade,
         diferencas reais correlacionadas com o tamanho do estudo e o acaso
         produzem a mesma assimetria. Testes de funil tambem tem pouco poder e
         sao instaveis abaixo de cerca de dez estudos independentes, e o pool
         de toda-estimativa trata linhas correlacionadas de um estudo como
         independentes. Por isso o resultado do teste nao dispara mais um
         rebaixamento sozinho. A regra, revista depois que a auditoria de
         2026-09-28 mostrou o veredito de Egger (toda-estimativa) trocando de
         doenca quando o IC implausivel de um estudo foi corrigido: com menos
         de publication_bias_min_studies_for_test estudos independentes no pool
         primario, o dominio e julgado "nao avaliavel por teste estatistico" e
         nao rebaixado pelo teste; com pelo menos esse numero, um passo so e
         dado quando o Egger e significativo TANTO no pool uma-por-estudo
         QUANTO no pool toda-estimativa. Os dois valores de p sao sempre
         reportados para que o leitor aplique uma regra mais estrita.
    """
    k = int(primary_row["n_studies"])
    p_every = sens_row.get("egger_p", "")
    p_one = primary_row.get("egger_p_one_per_study", "")
    fmt = lambda v: f"{float(v):.3g}" if v not in ("", None) else "not estimable"
    ps = f"Egger p = {fmt(p_one)} (one estimate per study) and {fmt(p_every)} (every estimate)"
    if k < THRESHOLDS["publication_bias_min_studies_for_test"]:
        return 0, (f"{ps}; with {k} independent studies the test is underpowered and not used to "
                   f"downgrade, so publication bias is not assessable by test and cannot be excluded")
    both = (p_one not in ("", None) and p_every not in ("", None)
            and float(p_one) < THRESHOLDS["publication_bias_egger_p"]
            and float(p_every) < THRESHOLDS["publication_bias_egger_p"])
    verdict = ("small-study effects on both pools (not itself proof of publication bias)"
               if both else "no consistent small-study effect across the two pools")
    return (1 if both else 0), f"{ps}; {verdict}"


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


def plot(sof, subtitle, path, lang):
    """
    EN | What the test does to 1000 people at each pre-test probability, drawn as an icon
         array: one dot is one person, so false alarms and missed cases are counted by eye.
         Counts are the per-1000 values of the summary of findings, rounded so that the dots
         add to 1000.
    PT | O que o teste faz a 1000 pessoas em cada probabilidade pre-teste, desenhado como
         matriz de icones: um ponto e uma pessoa, de modo que alarmes falsos e casos
         perdidos sao contados a olho. As contagens sao os valores por 1000 do resumo de
         achados, arredondados para que os pontos somem 1000.
    """
    from _viz_style import INK, INK2, INK3, PAGE, PD, TIER_RAMP, RULE
    keys = [("true_positives_per_1000", TIER_RAMP[0], "o", True,
             t(lang, "diseased, test positive", "doentes, teste positivo")),
            ("false_negatives_per_1000", TIER_RAMP[0], "o", False,
             t(lang, "diseased, test negative (missed)", "doentes, teste negativo (perdidos)")),
            ("false_positives_per_1000", PD, "o", True,
             t(lang, "healthy, test positive (false alarm)", "saudáveis, teste positivo (alarme falso)")),
            ("true_negatives_per_1000", "#d6d4ce", "o", True,
             t(lang, "healthy, test negative", "saudáveis, teste negativo"))]
    ncol, nrow = 40, 25
    fig, axes = plt.subplots(1, len(sof), figsize=(7.4, 3.6))
    if len(sof) == 1:
        axes = [axes]
    for ax, row in zip(axes, sof):
        raw = [row[k] for k, *_ in keys]
        counts = [int(x) for x in raw]
        rem = sorted(range(4), key=lambda i: -(raw[i] - counts[i]))
        for i in rem[:1000 - sum(counts)]:
            counts[i] += 1
        seq = []
        for (k, colour, mk, filled, _lab), c in zip(keys, counts):
            seq += [(colour, filled)] * c
        xs, ys, fc, ec = [], [], [], []
        for j, (colour, filled) in enumerate(seq):
            col, rw = divmod(j, nrow)
            xs.append(col); ys.append(rw)
            fc.append(colour if filled else PAGE); ec.append(colour)
        ax.scatter(xs, ys, s=5.0, facecolor=fc, edgecolor=ec, linewidths=0.8)
        ax.set_xlim(-1, ncol); ax.set_ylim(nrow, -1.5)
        ax.set_aspect("equal"); ax.axis("off")
        ax.set_title(t(lang, f"Pre-test probability {row['pre_test_probability']:.0%}",
                       f"Probabilidade pré-teste {row['pre_test_probability']:.0%}"), fontsize=8.6, fontweight="bold", color=INK, pad=2)
        ax.text(ncol / 2 - 0.5, nrow + 2.2,
                t(lang, f"{counts[2]} false alarms, {counts[1]} missed", f"{counts[2]} alarmes falsos, {counts[1]} perdidos"),
                ha="center", va="top", fontsize=7.2, color=INK)
        ax.text(ncol / 2 - 0.5, nrow + 4.6,
                t(lang, f"PPV {row['positive_predictive_value']:.2f} · NPV {row['negative_predictive_value']:.2f}",
                  f"VPP {row['positive_predictive_value']:.2f} · VPN {row['negative_predictive_value']:.2f}"),
                ha="center", va="top", fontsize=7.0, color=INK2)
    handles = [plt.Line2D([], [], marker="o", ls="none", ms=5.5, mfc=(c if f else PAGE), mec=c, mew=0.9) for _, c, _, f, _ in keys]
    fig.legend(handles, [lab for *_, lab in keys], loc="lower center", ncol=2, fontsize=7, frameon=False,
               bbox_to_anchor=(0.5, 0.12), handletextpad=0.3, columnspacing=1.6)
    # Title omitted: the caption in the manuscript names the figure.
    fig.savefig(path, dpi=600, bbox_inches="tight")
    plt.close(fig)


def rate_disease(disease, quadas_all, primary_rows, sens_rows):
    """
    EN | Full GRADE rating for one disease's primary outcome (the one-per-study
         pooled AUC), so that AD and PD - two biologically and diagnostically
         distinct primary outcomes - each get their own certainty rating rather
         than sharing one verdict built from the combined AD+PD pool.
    PT | Classificacao GRADE completa para o desfecho primario de uma doenca (a
         AUC agrupada uma-por-estudo), para que AD e PD - dois desfechos
         diagnosticos e biologicamente distintos - recebam cada um sua propria
         classificacao de certeza, em vez de compartilhar um veredito construido
         a partir do pool combinado AD+PD.
    """
    # EN | quadas_all is already restricted, by the caller, to the studies in
    #      the circulating PRIMARY pool - the same studies the pooled AUC
    #      being GRADEd here is built from. Rating risk of bias/indirectness
    #      from the full 14-study QUADAS-2 set per disease (which includes
    #      one CSF study per disease never entering this pooled estimate)
    #      would rate a body of evidence one domain-step wider than the
    #      number this GRADE table actually certifies.
    # PT | quadas_all ja vem restrito, por quem chama, aos estudos do pool
    #      PRIMARIO circulante - os mesmos estudos de que a AUC agrupada aqui
    #      classificada e construida. Avaliar risco de vies/indiretividade a
    #      partir do conjunto QUADAS-2 completo de 14 estudos por doenca
    #      (que inclui um estudo de LCR por doenca que nunca entra nesta
    #      estimativa agregada) avaliaria um corpo de evidencia um passo mais
    #      largo do que o que esta tabela GRADE de fato certifica.
    quadas = [r for r in quadas_all if r["disease"] == disease]
    primary_row = next(r for r in primary_rows
                       if r["subgroup"].startswith(f"{disease} - all markers"))
    sens_row = next(r for r in sens_rows
                    if r["subgroup"] == f"{disease} - all markers | todos marcadores")

    domains = OrderedDict()
    for name, (steps, why) in [
        ("risk_of_bias", rate_risk_of_bias(quadas)),
        ("indirectness", rate_indirectness(quadas)),
        ("inconsistency", rate_inconsistency(primary_row)),
        ("imprecision", rate_imprecision(primary_row)),
        ("publication_bias", rate_publication_bias(sens_row, primary_row)),
    ]:
        en, pt = downgrade(steps)
        if name == "publication_bias" and steps == 0 and "not assessable" in why:
            en, pt = "not assessable by test (not downgraded)", "nao avaliavel por teste (sem rebaixamento)"
        domains[name] = OrderedDict([("downgrade_steps", steps), ("judgement_en", en),
                                     ("judgement_pt", pt), ("reason", why)])
    total = sum(d["downgrade_steps"] for d in domains.values())
    idx = max(0, len(LEVELS) - 1 - total)
    certainty = LEVELS[idx]
    return domains, total, certainty, primary_row


def main():
    os.makedirs(TAB_DIR, exist_ok=True)
    os.makedirs(FIG_DIR, exist_ok=True)
    for f in (QUADAS, POOLED_PRIMARY, POOLED_SENS, BIVARIATE, SELECTION_AUDIT):
        if not os.path.exists(f):
            sys.exit(f"EN/PT: missing {f}; run scripts/05, 14 and 15 first")

    quadas_all = list(csv.DictReader(open(QUADAS, encoding="utf-8")))
    primary_rows = list(csv.DictReader(open(POOLED_PRIMARY, encoding="utf-8")))
    sens_rows = list(csv.DictReader(open(POOLED_SENS, encoding="utf-8")))
    biv = list(csv.DictReader(open(BIVARIATE, encoding="utf-8")))
    biv_primary = next(r for r in biv if r["analysis"].startswith("one estimate per study"))

    # EN | Restrict the QUADAS-2 table to the studies that are actually in the
    #      circulating primary pool (drops the one CSF study per disease that
    #      is screened/QUADAS-2/GRADE-rated alongside the corpus but never
    #      pooled - see the "Scope of the primary pool" docstring in
    #      scripts/05_meta_analysis.py), so risk-of-bias and indirectness are
    #      rated over the same studies inconsistency/imprecision already are.
    # PT | Restringe a tabela QUADAS-2 aos estudos que de fato estao no pool
    #      primario circulante (descarta o estudo de LCR por doenca que e
    #      triado/avaliado por QUADAS-2/GRADE junto ao corpus mas nunca
    #      agregado - ver a docstring "Scope of the primary pool" em
    #      scripts/05_meta_analysis.py), para que risco de vies e
    #      indiretividade sejam avaliados sobre os mesmos estudos que
    #      inconsistencia/imprecisao ja sao.
    primary_pool_study_ids = {r["study_id"] for r in
                              csv.DictReader(open(SELECTION_AUDIT, encoding="utf-8"))}
    quadas = [r for r in quadas_all if r["study_id"] in primary_pool_study_ids]

    results = OrderedDict()
    for disease in ["AD", "PD"]:
        domains, total, certainty, primary_row = rate_disease(
            disease, quadas, primary_rows, sens_rows)
        results[disease] = OrderedDict([
            ("domains", domains), ("total_downgrade_steps", total),
            ("certainty_of_evidence", certainty),
            ("primary_pooled_auc", float(primary_row["pooled_auc"])),
            ("primary_auc_ci_hk", [primary_row["ci_low_hk"], primary_row["ci_high_hk"]]),
            ("primary_row_n_studies", int(primary_row["n_studies"])),
        ])

    # EN | The bivariate sensitivity/specificity summary-of-findings table stays
    #      a single, combined AD+PD exploratory analysis: only 9 independent
    #      studies contribute a paired sensitivity and specificity, splitting
    #      that by disease would leave too few studies per disease to fit or
    #      interpret the bivariate model. It is reported as an exploratory
    #      complement to the two disease-specific AUC-based GRADE ratings
    #      above, not as their source.
    # PT | A tabela de resumo de achados de sensibilidade/especificidade
    #      bivariada permanece uma unica analise exploratoria combinada AD+PD:
    #      so 9 estudos independentes contribuem um par de sensibilidade e
    #      especificidade, separar por doenca deixaria poucos estudos por
    #      doenca para ajustar ou interpretar o modelo bivariado. E reportada
    #      como complemento exploratorio as duas classificacoes GRADE
    #      especificas por doenca acima, nao como fonte delas.
    sof = [summary_of_findings(float(biv_primary["summary_sensitivity"]),
                               float(biv_primary["summary_specificity"]), p)
           for p in PREVALENCES]

    print("=" * 78)
    print("EN | GRADE certainty of evidence, by disease | PT | Certeza GRADE, por doenca")
    print("=" * 78)
    for disease, r in results.items():
        print(f"\n  {disease} (primary pooled AUC {r['primary_pooled_auc']:.3f}, "
              f"HK 95% CI {r['primary_auc_ci_hk'][0]}-{r['primary_auc_ci_hk'][1]}):")
        for name, d in r["domains"].items():
            print(f"    {name:18s} -{d['downgrade_steps']}  {d['judgement_en']:13s} {d['reason']}")
        print(f"    total downgrade steps : {r['total_downgrade_steps']}")
        print(f"    CERTAINTY OF EVIDENCE : {r['certainty_of_evidence'].upper()}")

    print("\n  Exploratory combined AD+PD summary of findings, per 1000 people tested:")
    for row in sof:
        print(f"    pre-test {row['pre_test_probability']:.0%}: "
              f"TP {row['true_positives_per_1000']:6.1f}  FN {row['false_negatives_per_1000']:6.1f}  "
              f"TN {row['true_negatives_per_1000']:6.1f}  FP {row['false_positives_per_1000']:6.1f}  "
              f"PPV {row['positive_predictive_value']:.2f}  NPV {row['negative_predictive_value']:.2f}")

    with open(f"{TAB_DIR}/grade_summary_of_findings.csv", "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(sof[0].keys()))
        w.writeheader()
        w.writerows(sof)

    n_ad = results["AD"]["primary_row_n_studies"]
    n_pd = results["PD"]["primary_row_n_studies"]
    i2_ad = results["AD"]["domains"]["inconsistency"]["reason"].split("= ")[1].split("%")[0]
    i2_pd = results["PD"]["domains"]["inconsistency"]["reason"].split("= ")[1].split("%")[0]

    payload = OrderedDict([
        ("instrument", "GRADE for diagnostic test accuracy (Schunemann et al., "
                       "J Clin Epidemiol 2020;122:129-141 and 142-152)"),
        ("starting_certainty", "high"),
        ("thresholds", THRESHOLDS),
        ("by_disease", results),
        ("bivariate_summary_of_findings_scope",
         f"exploratory, AD and PD combined, {biv_primary['n_studies']} independent "
         "studies with a paired sensitivity and specificity; not disease-specific "
         "and not the basis for either disease's GRADE rating above"),
        ("bivariate_summary_sensitivity", float(biv_primary["summary_sensitivity"])),
        ("bivariate_summary_specificity", float(biv_primary["summary_specificity"])),
        ("summary_of_findings", sof),
        ("reading_en",
         "AD and PD are rated separately because they are different diagnostic "
         f"questions with different evidence bases ({n_ad} AD and {n_pd} PD studies "
         "in the primary, circulating AUC pool), and a single combined verdict "
         f"would obscure that PD's evidence is more heterogeneous (I2 {i2_pd}% "
         f"versus AD's {i2_ad}%). Both ratings are very low, "
         "driven by the same structural facts: every study is a case-versus-healthy-control design, "
         "no study pre-specified its positivity threshold, and "
         "heterogeneity is high to extreme. The combined bivariate summary of "
         "findings below is a secondary, exploratory illustration of what a "
         f"pooled operating point would imply clinically, drawn from only {biv_primary['n_studies']} "
         "studies, and should not be read as a validated clinical accuracy for "
         "either disease individually."),
        ("reading_pt",
         "AD e PD sao classificadas separadamente porque sao perguntas "
         "diagnosticas diferentes com bases de evidencia diferentes "
         f"({n_ad} estudos de AD e {n_pd} de PD no pool "
         "primario circulante de AUC), e um veredito unico combinado "
         f"esconderia que a evidencia de PD e mais heterogenea (I2 "
         f"{i2_pd}% contra {i2_ad}% de AD). As duas classificacoes "
         "sao muito baixas, guiadas pelos mesmos fatos estruturais: todo "
         "estudo e um desenho caso-versus-controle-saudavel, o limiar de positividade nao foi "
         "pre-especificado por nenhum estudo, e a heterogeneidade e "
         "alta a extrema. A tabela de resumo de achados bivariada combinada "
         "abaixo e uma ilustracao secundaria e exploratoria do que um ponto de "
         f"operacao agrupado implicaria clinicamente, tirada de apenas {biv_primary['n_studies']} "
         "estudos, e nao deve ser lida como uma acuracia clinica validada para "
         "nenhuma das duas doencas isoladamente."),
    ])
    with open(f"{TAB_DIR}/grade_certainty.json", "w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=1)

    ad_cert = results["AD"]["certainty_of_evidence"]
    pd_cert = results["PD"]["certainty_of_evidence"]
    for lang in LANGS:
        subtitle = t(lang,
                     f"exploratory, AD+PD combined (9 studies) · AD AUC certainty: {ad_cert} · "
                     f"PD AUC certainty: {pd_cert}",
                     f"exploratório, DA+DP combinado (9 estudos) · certeza AUC DA: {ad_cert} · "
                     f"certeza AUC DP: {pd_cert}")
        plot(sof, subtitle, fig_path(FIG_DIR, "grade_summary_of_findings", lang), lang)

    print(f"\nEN/PT -> {TAB_DIR}/grade_summary_of_findings.csv")
    print(f"EN/PT -> {TAB_DIR}/grade_certainty.json")
    for lang in LANGS:
        print(f"EN/PT -> {fig_path(FIG_DIR, 'grade_summary_of_findings', lang)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
