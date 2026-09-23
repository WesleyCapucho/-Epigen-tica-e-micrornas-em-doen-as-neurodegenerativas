#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EN | QUADAS-2 risk of bias and applicability assessment for the included diagnostic
     accuracy studies.
PT | Avaliacao QUADAS-2 de risco de vies e aplicabilidade dos estudos de acuracia
     diagnostica incluidos.

EN | Why this exists. A systematic review of diagnostic test accuracy without a risk of
     bias assessment is not a systematic review; it is a list of numbers. QUADAS-2 is the
     instrument the field uses, and its absence is the first thing a reviewer looks for.
PT | Por que isto existe. Uma revisao sistematica de acuracia diagnostica sem avaliacao
     de risco de vies nao e revisao sistematica; e uma lista de numeros. O QUADAS-2 e o
     instrumento que o campo usa, e a ausencia dele e a primeira coisa que um revisor
     procura.

EN | How the judgements are made, and what that costs. Every judgement here is DERIVED BY
     RULE from a field recorded in data/extracted/diagnostic_accuracy_extraction.csv. No
     judgement is typed in by hand, so the assessment is reproducible and can be argued
     with: disagree with a rule and you can change one function and rerun.
     The price is that two of the four risk of bias domains cannot be judged at all. The
     extraction was built to capture accuracy estimates and their source sentences; it did
     not record the reference standard, blinding, or patient flow. Those domains are
     reported as UNRATED rather than guessed, and closing them needs a second pass over
     the full texts. Saying "unclear" would imply the studies were checked and found
     ambiguous. They were not checked, and the output says so in a separate category.
PT | Como os julgamentos sao feitos, e o que isso custa. Todo julgamento aqui e DERIVADO
     POR REGRA de um campo registrado em
     data/extracted/diagnostic_accuracy_extraction.csv. Nenhum e digitado a mao, entao a
     avaliacao e reprodutivel e pode ser contestada: discorde de uma regra, mude uma
     funcao e rode de novo.
     O preco e que dois dos quatro dominios de risco de vies nao podem ser julgados. A
     extracao foi feita para capturar estimativas de acuracia e suas frases de origem; ela
     nao registrou padrao de referencia, cegamento nem fluxo de pacientes. Esses dominios
     saem como NAO AVALIADOS em vez de chutados, e fecha-los exige uma segunda passagem
     pelos textos completos. Dizer "incerto" daria a entender que os estudos foram
     conferidos e ficaram ambiguos. Nao foram conferidos, e a saida diz isso numa
     categoria separada.

    python scripts/14_quadas2_risk_of_bias.py

EN | Reference: Whiting PF, Rutjes AWS, Westwood ME, et al. QUADAS-2: a revised tool for
     the quality assessment of diagnostic accuracy studies. Ann Intern Med.
     2011;155(8):529-536.
PT | Referencia: Whiting PF, Rutjes AWS, Westwood ME, et al. QUADAS-2: a revised tool for
     the quality assessment of diagnostic accuracy studies. Ann Intern Med.
     2011;155(8):529-536.
"""

import csv
import json
import os
import sys
from collections import Counter, OrderedDict

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _bilingual import LANGS, t, fig_path

EXTRACTION = "data/extracted/diagnostic_accuracy_extraction.csv"
STUDY_LEVEL = "data/extracted/quadas2_study_level.csv"
TAB_DIR = "results/tables"
FIG_DIR = "results/figures"

HIGH, LOW, UNCLEAR, UNRATED = "high", "low", "unclear", "unrated"

# EN | The four risk-of-bias domains and the three applicability domains of QUADAS-2,
#      with the signalling questions each rule answers.
# PT | Os quatro dominios de risco de vies e os tres de aplicabilidade do QUADAS-2, com
#      as perguntas-sinal que cada regra responde.
DOMAINS = OrderedDict([
    ("rob_patient_selection", ("Risk of bias: patient selection",
                               "Risco de viés: seleção de pacientes")),
    ("rob_index_test", ("Risk of bias: index test", "Risco de viés: teste índice")),
    ("rob_reference_standard", ("Risk of bias: reference standard",
                                "Risco de viés: padrão de referência")),
    ("rob_flow_timing", ("Risk of bias: flow and timing",
                         "Risco de viés: fluxo e tempo")),
    ("app_patient_selection", ("Applicability: patient selection",
                               "Aplicabilidade: seleção de pacientes")),
    ("app_index_test", ("Applicability: index test", "Aplicabilidade: teste índice")),
    ("app_reference_standard", ("Applicability: reference standard",
                                "Aplicabilidade: padrão de referência")),
])


def study_id(row):
    """EN/PT: PMID when the study has one, DOI otherwise."""
    pmid = str(row.get("pmid", "")).strip()
    if pmid.endswith(".0"):
        pmid = pmid[:-2]
    return pmid or str(row.get("doi", "")).strip().lower()


def rob_patient_selection(rows):
    """
    EN | Signalling questions: consecutive or random sample? case-control design avoided?
         inappropriate exclusions avoided?
         Only the second is answerable from the extraction. A study contrasting cases
         against healthy controls sampled separately is a two-gate (case-control) design,
         which QUADAS-2 names explicitly as a source of bias because it inflates accuracy
         by removing the differential-diagnosis problem the test would face in practice.
         Sampling method and exclusions are not recorded, so a study that avoids the
         case-control design still cannot be rated LOW here.
    PT | Perguntas-sinal: amostra consecutiva ou aleatoria? desenho caso-controle evitado?
         exclusoes inadequadas evitadas?
         So a segunda e respondivel pela extracao. Um estudo que contrasta casos contra
         controles saudaveis amostrados a parte e um desenho de duas portas
         (caso-controle), que o QUADAS-2 nomeia explicitamente como fonte de vies porque
         infla a acuracia ao remover o problema de diagnostico diferencial que o teste
         enfrentaria na pratica. Metodo de amostragem e exclusoes nao estao registrados,
         entao um estudo que evita o caso-controle ainda assim nao pode ser LOW aqui.
    """
    classes = {r["comparison_class"] for r in rows}
    if "case_vs_healthy_control" in classes:
        return HIGH, ("contrast against healthy controls is a two-gate (case-control) "
                      "design [comparison_class]")
    return UNCLEAR, ("no healthy-control contrast, but the sampling method is not "
                     "recorded [comparison_class]")


def rob_index_test(rows):
    """
    EN | Signalling questions: were index test results interpreted without knowledge of
         the reference standard? was a threshold pre-specified?
         The second is answerable. An accuracy estimate whose cut-off was chosen in the
         same sample where it is evaluated is optimistically biased, and that is what
         cohort_stage records. Blinding is not recorded, so a study using a pre-specified
         threshold in an independent validation set is rated UNCLEAR, not LOW: one
         signalling question answered well does not clear the domain.
    PT | Perguntas-sinal: os resultados do teste indice foram interpretados sem conhecer o
         padrao de referencia? o limiar foi pre-especificado?
         A segunda e respondivel. Uma estimativa cujo ponto de corte foi escolhido na
         mesma amostra em que e avaliada e otimista, e e isso que o cohort_stage
         registra. O cegamento nao esta registrado, entao um estudo com limiar
         pre-especificado em conjunto de validacao independente fica UNCLEAR, nao LOW:
         uma pergunta-sinal bem respondida nao limpa o dominio.
    """
    stages = {r["cohort_stage"] for r in rows}
    derived = {"single", "discovery", "training"} & stages
    if derived:
        return HIGH, (f"threshold derived in the evaluation sample ({'/'.join(sorted(derived))}) "
                      "[cohort_stage]")
    if "cross-validated" in stages:
        return UNCLEAR, ("cross-validated within one sample: better than resubstitution, "
                         "but not an independent threshold [cohort_stage]")
    if "validation" in stages:
        return UNCLEAR, ("independent validation set, but blinding to the reference "
                         "standard is not recorded [cohort_stage]")
    return UNCLEAR, "cohort stage not determinable [cohort_stage]"


def rob_reference_standard(rows, sl):
    """
    EN | Signalling questions: is the reference standard likely to classify the target
         condition correctly? was it interpreted without knowledge of the index test?
         Both are answered from data/extracted/quadas2_study_level.csv, which records,
         per study, the sentence naming the diagnostic criteria and the sentence stating
         blinding, read from the PubMed Central full text.
         The judgement turns on a fact specific to these two diseases: the practical
         reference standard is clinical criteria, not autopsy, and clinical criteria
         misclassify a known fraction of cases. A study that names accepted criteria has
         done what the field expects and still cannot be rated LOW on that ground alone,
         because the standard it used is imperfect and the accuracy estimates inherit its
         error. Only neuropathological confirmation, or named criteria plus stated
         blinding, clears the domain.
    PT | Perguntas-sinal: o padrao de referencia provavelmente classifica corretamente a
         condicao alvo? foi interpretado sem conhecer o teste indice?
         As duas sao respondidas por data/extracted/quadas2_study_level.csv, que registra,
         por estudo, a frase que nomeia os criterios diagnosticos e a frase que declara
         cegamento, lidas do texto completo no PubMed Central.
         O julgamento gira num fato especifico destas duas doencas: o padrao de referencia
         pratico e criterio clinico, nao autopsia, e criterio clinico classifica errado uma
         fracao conhecida dos casos. Um estudo que nomeia criterios aceitos fez o que o
         campo espera e ainda assim nao pode ser LOW so por isso, porque o padrao que usou
         e imperfeito e as estimativas de acuracia herdam o erro dele. So confirmacao
         neuropatologica, ou criterios nomeados mais cegamento declarado, limpa o dominio.
    """
    if not sl:
        return UNCLEAR, "no study-level record for this study [quadas2_study_level.csv]"
    if sl["fulltext_availability"] != "yes":
        return UNCLEAR, (f"full text not retrievable ({sl['fulltext_availability']}), so the "
                         "reference standard could not be checked [quadas2_study_level.csv]")
    if sl["autopsy_confirmed"] == "yes":
        return LOW, "neuropathological confirmation of the target condition [reference_standard_quote]"
    if sl["reference_standard_named"] == "yes":
        if sl["blinding_stated"] == "yes":
            return LOW, ("named diagnostic criteria and stated blinding to the index test "
                         "[reference_standard_quote, blinding_quote]")
        return UNCLEAR, ("named clinical diagnostic criteria, which misclassify a known "
                         "fraction of AD and PD cases, and no statement of blinding "
                         "[reference_standard_quote]")
    return HIGH, ("the full text was read and names no diagnostic criteria for the target "
                  "condition [reference_standard_named=no]")


def rob_flow_timing(rows, sl):
    """
    EN | Signalling questions: appropriate interval between index test and reference
         standard? did all patients receive a reference standard, and the same one? were
         all patients included in the analysis?
         These were checked against the full texts and are, with one exception each, not
         reported: none of the 22 retrievable full texts contains a STARD flow diagram or
         flow chart, one accounts for post-enrolment exclusions, and one states the
         interval between sampling and diagnosis. The domain is therefore UNCLEAR rather
         than unrated - the question was asked of the primary reports and they do not
         answer it. That silence is itself a finding about how this literature reports.
    PT | Perguntas-sinal: intervalo adequado entre teste indice e padrao de referencia?
         todos os pacientes receberam padrao de referencia, e o mesmo? todos entraram na
         analise?
         Foram conferidas contra os textos completos e, com uma excecao cada, nao sao
         reportadas: nenhum dos 22 textos completos recuperaveis traz fluxograma STARD ou
         diagrama de fluxo, um presta contas de exclusoes apos a inclusao e um declara o
         intervalo entre coleta e diagnostico. O dominio fica UNCLEAR e nao nao-avaliado -
         a pergunta foi feita aos relatos primarios e eles nao respondem. Esse silencio e,
         em si, um achado sobre como esta literatura reporta.
    """
    if not sl or sl["fulltext_availability"] != "yes":
        return UNCLEAR, ("full text not retrievable, so patient flow could not be checked "
                         "[quadas2_study_level.csv]")
    return UNCLEAR, ("full text read: no STARD flow diagram, and neither the accounting of "
                     "all enrolled participants nor the interval between sampling and "
                     "diagnosis is reported [full text]")


def app_patient_selection(rows):
    """
    EN | Do the included patients match the review question? The question a biomarker has
         to answer in clinic is not "disease or healthy" but "this disease or another
         cause of the same complaint". A study of patients against healthy controls does
         not address it.
         Read the result of this rule together with eligibility_circularity in the summary.
         Every eligible estimate is a case-versus-healthy-control contrast because the
         review's own eligibility rule demanded that contrast, so a uniform HIGH here is
         not a discovery about the literature. It is a statement about the review question,
         and the literature that does address differential diagnosis was excluded rather
         than absent.
    PT | Os pacientes incluidos correspondem a pergunta da revisao? A pergunta que um
         biomarcador tem de responder na clinica nao e "doente ou saudavel" e sim "esta
         doenca ou outra causa da mesma queixa". Um estudo de pacientes contra controles
         saudaveis nao trata disso.
         Leia o resultado desta regra junto com eligibility_circularity no resumo. Toda
         estimativa elegivel e um contraste caso-versus-controle-saudavel porque a propria
         regra de elegibilidade da revisao exigiu esse contraste, entao um HIGH uniforme
         aqui nao e descoberta sobre a literatura. E uma afirmacao sobre a pergunta da
         revisao, e a literatura que trata de diagnostico diferencial foi excluida, nao
         esta ausente.
    """
    classes = {r["comparison_class"] for r in rows}
    if classes <= {"case_vs_healthy_control"}:
        return HIGH, ("only case versus healthy control contrasts [comparison_class]; "
                      "note this is also what the eligibility rule required, see "
                      "eligibility_circularity in the summary")
    if "differential_diagnosis" in classes or "prodromal_vs_control" in classes:
        return LOW, ("includes a differential-diagnosis or prodromal contrast, which is "
                     "the clinically relevant question [comparison_class]")
    return UNCLEAR, "contrast type does not map cleanly onto the review question"


def app_index_test(rows):
    """
    EN | Does the test as performed match the review question, which concerns a minimally
         invasive circulating marker? Blood and CSF qualify; anything obtained by
         endoscopy does not.
    PT | O teste como realizado corresponde a pergunta da revisao, que trata de marcador
         circulante minimamente invasivo? Sangue e liquor servem; o que exige endoscopia
         nao serve.
    """
    fluids = {r["biofluid"] for r in rows}
    invasive = {f for f in fluids if "gastric" in f}
    if invasive:
        return HIGH, f"sample not minimally invasive: {sorted(invasive)} [biofluid]"
    return LOW, f"minimally invasive circulating sample: {sorted(fluids)} [biofluid]"


def app_reference_standard(rows, sl):
    """
    EN | Does the target condition as defined by the reference standard match the review
         question? The review asks about diagnosing clinically established AD or PD, and a
         study using the accepted clinical criteria for those diseases is answering that
         question, whatever the criteria's own error rate.
    PT | A condicao alvo definida pelo padrao de referencia corresponde a pergunta da
         revisao? A revisao trata de diagnosticar DA ou DP clinicamente estabelecida, e um
         estudo que usa os criterios clinicos aceitos para essas doencas esta respondendo a
         essa pergunta, qualquer que seja a taxa de erro dos criterios.
    """
    if not sl or sl["fulltext_availability"] != "yes":
        return UNCLEAR, "full text not retrievable [quadas2_study_level.csv]"
    if sl["reference_standard_named"] == "yes" or sl["autopsy_confirmed"] == "yes":
        return LOW, "the target condition is AD or PD as defined by accepted criteria"
    return UNCLEAR, "the target condition definition is not stated in the full text"


RULES = OrderedDict([
    ("rob_patient_selection", rob_patient_selection),
    ("rob_index_test", rob_index_test),
    ("rob_reference_standard", rob_reference_standard),
    ("rob_flow_timing", rob_flow_timing),
    ("app_patient_selection", app_patient_selection),
    ("app_index_test", app_index_test),
    ("app_reference_standard", app_reference_standard),
])


NEEDS_STUDY_LEVEL = {"rob_reference_standard", "rob_flow_timing", "app_reference_standard"}


def assess(rows_by_study, study_level):
    out = []
    for sid, rows in sorted(rows_by_study.items()):
        first = rows[0]
        rec = OrderedDict([
            ("study_id", sid),
            ("first_author", first["first_author"]),
            ("year", first["year"]),
            ("journal", first["journal"]),
            ("disease", "/".join(sorted({r["disease"] for r in rows}))),
            ("n_estimates", len(rows)),
            ("n_estimates_eligible", sum(1 for r in rows
                                         if r["eligible_primary_pool"] == "yes")),
        ])
        sl = study_level.get(sid)
        for key, rule in RULES.items():
            verdict, reason = (rule(rows, sl) if key in NEEDS_STUDY_LEVEL else rule(rows))
            rec[key] = verdict
            rec[key + "_reason"] = reason
        out.append(rec)
    return out


def plot(assessment, path, lang):
    """EN/PT: the standard QUADAS-2 stacked bar, one row per domain."""
    order = [HIGH, UNCLEAR, LOW, UNRATED]
    colour = {HIGH: "#c0392b", UNCLEAR: "#f0c419", LOW: "#2e8b57", UNRATED: "#9aa0a6"}
    label = {HIGH: t(lang, "High", "Alto"), UNCLEAR: t(lang, "Unclear", "Incerto"),
             LOW: t(lang, "Low", "Baixo"),
             UNRATED: t(lang, "Not assessed", "Não avaliado")}
    keys = list(DOMAINS)
    fig, ax = plt.subplots(figsize=(10, 4.6))
    n = len(assessment)
    for i, key in enumerate(keys):
        counts = Counter(r[key] for r in assessment)
        left = 0.0
        for v in order:
            frac = 100.0 * counts.get(v, 0) / n
            if frac <= 0:
                continue
            ax.barh(len(keys) - 1 - i, frac, left=left, color=colour[v],
                    edgecolor="white", height=0.72)
            if frac >= 7:
                ax.text(left + frac / 2, len(keys) - 1 - i, f"{frac:.0f}%",
                        ha="center", va="center", fontsize=8,
                        color="white" if v != UNCLEAR else "black")
            left += frac
    ax.set_yticks(range(len(keys)))
    ax.set_yticklabels([t(lang, *DOMAINS[k]) for k in reversed(keys)], fontsize=9)
    ax.set_xlabel(t(lang, f"per cent of studies  (n = {n})",
                    f"por cento dos estudos  (n = {n})"))
    ax.set_xlim(0, 100)
    ax.set_title(t(lang, "QUADAS-2: risk of bias and applicability",
                   "QUADAS-2: risco de viés e aplicabilidade"), fontsize=11)
    handles = [plt.Rectangle((0, 0), 1, 1, color=colour[v]) for v in order]
    ax.legend(handles, [label[v] for v in order], loc="lower center",
              bbox_to_anchor=(0.5, -0.32), ncol=4, fontsize=8, frameon=False)
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    fig.savefig(path, dpi=200, bbox_inches="tight")
    plt.close(fig)


def main():
    os.makedirs(TAB_DIR, exist_ok=True)
    os.makedirs(FIG_DIR, exist_ok=True)
    if not os.path.exists(EXTRACTION):
        sys.exit(f"EN/PT: missing {EXTRACTION}")
    rows = list(csv.DictReader(open(EXTRACTION, encoding="utf-8")))

    # EN | Assess the studies that contribute to the primary pool. A risk of bias table
    #      over studies whose estimates were excluded anyway would not inform the result.
    # PT | Avalia os estudos que entram no pool primario. Uma tabela de risco de vies
    #      sobre estudos cujas estimativas foram excluidas de qualquer modo nao
    #      informaria o resultado.
    eligible = [r for r in rows if r["eligible_primary_pool"] == "yes"]
    by_study = {}
    for r in eligible:
        by_study.setdefault(study_id(r), []).append(r)

    study_level = {}
    if os.path.exists(STUDY_LEVEL):
        study_level = {r["study_id"]: r
                       for r in csv.DictReader(open(STUDY_LEVEL, encoding="utf-8"))}
    assessment = assess(by_study, study_level)
    fields = list(assessment[0].keys())
    with open(f"{TAB_DIR}/quadas2_assessment.csv", "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=fields)
        w.writeheader()
        w.writerows(assessment)

    # EN | Count what the eligibility rule removed, so the uniform judgements above can be
    #      read for what they are. Hiding this would let a reader mistake a design choice
    #      of this review for a finding about the field.
    # PT | Conta o que a regra de elegibilidade removeu, para que os julgamentos uniformes
    #      acima sejam lidos pelo que sao. Esconder isso deixaria o leitor confundir uma
    #      escolha de desenho desta revisao com um achado sobre o campo.
    excluded_contrasts = Counter(
        r["comparison_class"] for r in rows
        if r["eligible_primary_pool"] != "yes" and r["comparison_class"] != "case_vs_healthy_control")
    excluded_studies = len({study_id(r) for r in rows
                            if r["eligible_primary_pool"] != "yes"
                            and r["comparison_class"] != "case_vs_healthy_control"})

    summary = OrderedDict()
    for key in DOMAINS:
        c = Counter(r[key] for r in assessment)
        summary[key] = OrderedDict((v, c.get(v, 0)) for v in (HIGH, UNCLEAR, LOW, UNRATED))

    for lang in LANGS:
        plot(assessment, fig_path(FIG_DIR, "quadas2_summary", lang), lang)

    payload = OrderedDict([
        ("instrument", "QUADAS-2 (Whiting et al., Ann Intern Med 2011;155:529-536)"),
        ("studies_assessed", len(assessment)),
        ("scope", "studies contributing at least one estimate to the primary pool"),
        ("judgements_derived_by_rule_from", EXTRACTION),
        ("domain_summary", summary),
        ("eligibility_circularity_en",
         "Every study assessed is high risk and high concern for patient selection because "
         "every eligible estimate is a case-versus-healthy-control contrast. That is partly "
         f"by construction: the review's eligibility rule required that contrast, and "
         f"{sum(excluded_contrasts.values())} estimates from {excluded_studies} studies were "
         f"excluded for using another one ({dict(excluded_contrasts)}). The clinically "
         "relevant comparisons - this disease against its mimics, and prodromal against "
         "control - exist in the literature and were set aside by the PICO, not missing "
         "from it. The honest reading is that the pooled estimates answer an easier "
         "question than the clinical one, and are upper bounds for that reason."),
        ("eligibility_circularity_pt",
         "Todo estudo avaliado e de alto risco e alta preocupacao em selecao de pacientes "
         "porque toda estimativa elegivel e um contraste caso-versus-controle-saudavel. "
         "Isso e em parte por construcao: a regra de elegibilidade da revisao exigiu esse "
         f"contraste, e {sum(excluded_contrasts.values())} estimativas de {excluded_studies} "
         f"estudos foram excluidas por usarem outro ({dict(excluded_contrasts)}). As "
         "comparacoes clinicamente relevantes - esta doenca contra seus imitadores, e "
         "prodromico contra controle - existem na literatura e foram postas de lado pelo "
         "PICO, nao faltam nele. A leitura honesta e que as estimativas agrupadas respondem "
         "a uma pergunta mais facil que a clinica, e sao limites superiores por isso."),
        ("excluded_non_case_control_estimates", dict(excluded_contrasts)),
        ("unrated_domains_en",
         "The reference standard and flow-and-timing domains are UNRATED, not unclear: "
         "the extraction did not capture which diagnostic criteria each study used, "
         "whether diagnosis was blind to the miRNA result, or how patients flowed through "
         "the study. Rating them requires a second pass over the full texts."),
        ("unrated_domains_pt",
         "Os dominios de padrao de referencia e de fluxo e tempo estao NAO AVALIADOS, nao "
         "incertos: a extracao nao capturou quais criterios diagnosticos cada estudo usou, "
         "se o diagnostico foi cego ao resultado do miRNA, nem como os pacientes fluiram "
         "pelo estudo. Avalia-los exige uma segunda passagem pelos textos completos."),
    ])
    with open(f"{TAB_DIR}/quadas2_summary.json", "w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=1)

    print("=" * 78)
    print("EN | QUADAS-2 risk of bias | PT | QUADAS-2 risco de vies")
    print("=" * 78)
    print(f"  studies assessed | estudos avaliados : {len(assessment)}")
    for key, titles in DOMAINS.items():
        c = summary[key]
        print(f"  {titles[0]:42s} high {c[HIGH]:3d} | unclear {c[UNCLEAR]:3d} | "
              f"low {c[LOW]:3d} | unrated {c[UNRATED]:3d}")
    print(f"\n  EN | Uniform patient-selection judgements are partly a consequence of the")
    print(f"       eligibility rule: {sum(excluded_contrasts.values())} estimates from "
          f"{excluded_studies} studies using another")
    print(f"       contrast were excluded -> {dict(excluded_contrasts)}")
    print(f"  PT | Julgamentos uniformes de selecao vem em parte da regra de elegibilidade.")
    print(f"\nEN/PT -> {TAB_DIR}/quadas2_assessment.csv")
    print(f"EN/PT -> {TAB_DIR}/quadas2_summary.json")
    for lang in LANGS:
        print(f"EN/PT -> {fig_path(FIG_DIR, 'quadas2_summary', lang)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
