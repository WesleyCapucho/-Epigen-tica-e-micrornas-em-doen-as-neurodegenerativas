#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EN | Gathers every number that the Article 1 manuscript quotes into one flat file,
     results/tables/manuscript_numbers.json, read from the result tables and processed
     data of this repository and from nothing else. The manuscript text is kept outside
     the repository; it carries placeholders such as {{pool.AD.auc}} and a renderer
     replaces each one with the value stored here, and refuses to build if a placeholder
     has no value. A number in the manuscript therefore cannot differ from the table it
     came from, and a rerun of the pipeline followed by this script moves both together.

     This script computes nothing new about the studies. It selects, rounds and counts
     (half-up rounding, as Word and most readers expect) from files already written by
     scripts 03 to 33. Each value is stored as a string, already formatted for the
     manuscript, together with the file it was read from (key "_sources").

PT | Reune num arquivo plano, results/tables/manuscript_numbers.json, todo numero que o
     manuscrito do Artigo 1 cita, lido das tabelas de resultado e dos dados processados
     deste repositorio e de mais nada. O texto do manuscrito fica fora do repositorio; ele
     traz marcadores como {{pool.AD.auc}} e um montador troca cada um pelo valor guardado
     aqui, e se recusa a montar se algum marcador nao tiver valor. Assim um numero do
     manuscrito nao pode diferir da tabela de onde veio, e uma nova execucao do pipeline
     seguida deste script move os dois juntos.

     Este script nao calcula nada novo sobre os estudos. Ele seleciona, arredonda e conta
     (arredondamento meio-para-cima, como o Word e a maioria dos leitores esperam) a
     partir de arquivos ja gravados pelos scripts 03 a 33. Cada valor e guardado como
     texto, ja formatado para o manuscrito, junto com o arquivo de onde foi lido
     (chave "_sources").
"""

import json
import os
import re
from decimal import ROUND_HALF_UP, Decimal

import numpy as np
import pandas as pd

T = "results/tables"
OUT = f"{T}/manuscript_numbers.json"

N, SRC = {}, {}


def rnd(x, nd):
    q = Decimal(1).scaleb(-nd)
    return str(Decimal(repr(round(float(x), 8))).quantize(q, rounding=ROUND_HALF_UP))


def put(key, value, src):
    if key in N:
        raise KeyError(f"duplicate key {key}")
    N[key] = value if isinstance(value, str) else str(value)
    SRC[key] = src


def num(key, x, nd, src):
    put(key, rnd(x, nd), src)


def integer(key, x, src):
    put(key, str(int(round(float(x)))), src)


def pctval(key, x, nd, src):
    put(key, rnd(float(x) * 100, nd), src)


def p_text(p):
    p = float(p)
    if p < 0.0001:
        return "< 0.0001"
    if p < 0.001:
        return rnd(p, 4)
    return rnd(p, 3) if p < 0.1 else rnd(p, 2)


def norm_sid(df):
    s = df["pmid"].astype(str).str.replace(r"\.0$", "", regex=True)
    s = s.where(~s.isin(["nan", "", "None"]), df["doi"].astype(str).str.lower())
    return s


# ----------------------------------------------------------------------------- flow
flow = json.load(open("data/processed/prisma_flow.json"))
ident, scr, elig = flow["identification"], flow["screening"], flow["eligibility_fulltext"]
rc = elig["recall_check"]
incl = flow["included_in_meta_analysis"]
rule = flow["screening_rule_recomputation"]
FL = "data/processed/prisma_flow.json"
for k, v in dict(pubmed_ad=ident["pubmed_records_AD_arm"], pubmed_pd=ident["pubmed_records_PD_arm"],
                 pubmed_dedup=ident["pubmed_records_after_deduplication"],
                 pubmed_both=ident["pubmed_records_in_both_arms"],
                 scopus_ad=ident["scopus_records_AD_arm"], scopus_pd=ident["scopus_records_PD_arm"],
                 scopus_new=ident["scopus_records_new"], scopus_new_ad=ident["scopus_records_new"] - ident["scopus_PD_records_new"],
                 scopus_new_pd=ident["scopus_PD_records_new"],
                 wos_ad=ident["wos_records_AD_arm"], wos_pd=ident["wos_records_PD_arm"],
                 wos_new=ident["wos_records_new_total"], total=ident["total_unique_records"],
                 secondary=rule["excluded_review_or_secondary"], primary=rule["primary_studies"],
                 acc_abstract=rule["primary_reporting_auc_or_sens_spec"],
                 ft_read=elig["fulltext_retrieved"], studies_extracted=elig["studies_contributing_extracted_estimates"],
                 est_total=elig["extracted_estimates_total"], est_eligible=elig["estimates_eligible_for_primary_pool"],
                 recall_noacc=rc["records_without_accuracy_statement_in_abstract"],
                 recall_plausible=rc["judged_plausible_by_title_and_abstract"],
                 recall_noft=rc["no_open_fulltext"], recall_requested=rc["fulltext_requested"],
                 recall_notretr=rc["fulltext_not_retrievable"], recall_read=rc["fulltext_read"],
                 recall_reports_eligible=rc["reports_with_eligible_estimates"],
                 recall_reports_acc_only=rc["reports_with_accuracy_but_no_primary_estimate"],
                 recall_reports_none=rc["reports_not_eligible"],
                 recall_est=rc["estimates_extracted"], recall_est_eligible=rc["estimates_eligible_for_primary_pool"],
                 pooled_est=incl["estimates_with_estimable_standard_error"], pooled_k=incl["independent_studies"],
                 csf_est=incl["csf_estimates_secondary_not_pooled"], wos_candidates=elig["wos_candidates_adjudicated"]).items():
    integer(f"flow.{k}", v, FL)
integer("flow.ft_abstract_arm", elig["fulltext_retrieved"] - rc["fulltext_read"], FL)
integer("flow.est_set_aside", elig["extracted_estimates_total"] - elig["estimates_eligible_for_primary_pool"], FL)
integer("flow.not_pooled", elig["estimates_eligible_for_primary_pool"] - incl["estimates_with_estimable_standard_error"], FL)
integer("flow.no_se", elig["estimates_eligible_for_primary_pool"] - incl["estimates_with_estimable_standard_error"]
        - incl["csf_estimates_secondary_not_pooled"], FL)

# ----------------------------------------------------------------------------- eligible studies (QUADAS-2 units)
q2 = json.load(open(f"{T}/quadas2_summary.json"))
qa = pd.read_csv(f"{T}/quadas2_assessment.csv")
QA = f"{T}/quadas2_summary.json"
integer("elig.units", q2["studies_assessed"], QA)
integer("elig.not_pooled", q2["studies_assessed"] - incl["independent_studies"], f"{QA} and {FL}")
integer("elig.no_se_units", q2["studies_assessed"] - incl["independent_studies"] - 4, f"{QA} and {FL} (four CSF studies, see docs/en/METHODS.md)")
integer("elig.units_ad", (qa.disease == "AD").sum(), f"{T}/quadas2_assessment.csv")
integer("elig.units_pd", (qa.disease == "PD").sum(), f"{T}/quadas2_assessment.csv")
# a report that covers both diseases is keyed twice (its PMID or DOI for AD, the DOI plus "#pd" for PD)
integer("elig.reports_both", qa.study_id.str.endswith("#pd").sum(), f"{T}/quadas2_assessment.csv")
integer("elig.reports", len(qa) - qa.study_id.str.endswith("#pd").sum(), f"{T}/quadas2_assessment.csv")
ds = q2["domain_summary"]
for dom, nm in [("rob_patient_selection", "rob_ps"), ("rob_index_test", "rob_it"),
                ("rob_reference_standard", "rob_rs"), ("rob_flow_timing", "rob_ft"),
                ("app_patient_selection", "app_ps"), ("app_index_test", "app_it"),
                ("app_reference_standard", "app_rs")]:
    for lvl in ("high", "unclear", "low"):
        integer(f"q2.{nm}.{lvl}", ds[dom][lvl], QA)
exc = q2["excluded_non_case_control_estimates"]
integer("q2.excl_diff", exc["differential_diagnosis"], QA)
integer("q2.excl_within", exc["within_disease"], QA)
integer("q2.excl_prodromal", exc["prodromal_vs_control"], QA)
integer("q2.excl_total", sum(exc.values()), QA)
ext = pd.read_csv("data/extracted/diagnostic_accuracy_extraction.csv")
EX = "data/extracted/diagnostic_accuracy_extraction.csv"
non_cc = ext[ext.comparison_class != "case_vs_healthy_control"]
# the pipeline's own count of studies behind the excluded contrasts (it keys a two-disease report once per disease)
integer("q2.excl_studies", re.search(r"from (\d+) studies", q2["eligibility_circularity_en"]).group(1), QA)

ql = pd.read_csv("data/extracted/quadas2_study_level.csv", dtype=str)
QL = "data/extracted/quadas2_study_level.csv"
integer("q2.ft_available", (ql.fulltext_availability == "yes").sum(), QL)
integer("q2.named_criteria", (ql.reference_standard_named == "yes").sum(), QL)
integer("q2.autopsy", (ql.autopsy_confirmed == "yes").sum(), QL)
integer("q2.blinding", (ql.blinding_stated == "yes").sum(), QL)
integer("q2.ft_missing", (ql.fulltext_availability != "yes").sum(), QL)

# ----------------------------------------------------------------------------- primary pools
pp = pd.read_csv(f"{T}/meta_analysis_pooled_auc_primary.csv")
PP = f"{T}/meta_analysis_pooled_auc_primary.csv"


def pool_row(prefix):
    r = pp[pp.subgroup.str.startswith(prefix)]
    if len(r) != 1:
        raise KeyError(prefix)
    return r.iloc[0]


def put_pool(tag, row, src):
    integer(f"pool.{tag}.k", row.n_studies, src)
    integer(f"pool.{tag}.k_est", row.n_estimates_collapsed, src)
    num(f"pool.{tag}.auc", row.pooled_auc, 2, src)
    num(f"pool.{tag}.auc3", row.pooled_auc, 3, src)
    num(f"pool.{tag}.lo", row.ci_low_hk, 2, src)
    num(f"pool.{tag}.hi", row.ci_high_hk, 2, src)
    num(f"pool.{tag}.lo3", row.ci_low_hk, 3, src)
    num(f"pool.{tag}.hi3", row.ci_high_hk, 3, src)
    num(f"pool.{tag}.wald_lo", row.ci_low_wald, 2, src)
    num(f"pool.{tag}.wald_hi", row.ci_high_wald, 2, src)
    num(f"pool.{tag}.pi_lo", row.pi_low, 2, src)
    num(f"pool.{tag}.pi_hi", row.pi_high, 2, src)
    num(f"pool.{tag}.i2", row.I2_percent, 1, src)
    num(f"pool.{tag}.tau2", row.tau2_PM, 2, src)
    num(f"pool.{tag}.q", row.Q, 1, src)
    integer(f"pool.{tag}.df", row.df, src)
    num(f"pool.{tag}.ci_width", row.ci_high_hk - row.ci_low_hk, 2, src)
    num(f"pool.{tag}.egger_int", row.egger_intercept_one_per_study, 2, src)
    put(f"pool.{tag}.egger_p", p_text(row.egger_p_one_per_study), src)


put_pool("AD", pool_row("AD - all markers"), PP)
put_pool("PD", pool_row("PD - all markers"), PP)
put_pool("ALL", pool_row("Overall AD+PD"), PP)
put_pool("single", pool_row("All - single"), PP)
put_pool("panel", pool_row("All - multi"), PP)
put_pool("AD_single", pool_row("AD - single"), PP)
put_pool("PD_single", pool_row("PD - single"), PP)
put_pool("AD_panel", pool_row("AD - multi"), PP)
put_pool("PD_panel", pool_row("PD - multi"), PP)
put_pool("plasma", pool_row("Biofluid | Biofluido - plasma"), PP)
put_pool("serum", pool_row("Biofluid | Biofluido - serum"), PP)
put("pool.PD_panel.p_het", p_text(pool_row("PD - multi").p_heterogeneity), PP)

sd = pd.read_csv(f"{T}/subgroup_difference_test.csv")
SD = f"{T}/subgroup_difference_test.csv"
for tag, key in [("AD", "AD"), ("PD", "PD"), ("ALL", "combined")]:
    r = sd[sd.comparison.str.contains(key)].iloc[0]
    num(f"subtest.{tag}.q", r.Q_between, 1, SD)
    put(f"subtest.{tag}.p", p_text(r.p_value), SD)
    put(f"subtest.{tag}.p_re", p_text(r.p_value_RE), SD)
    num(f"subtest.{tag}.diff_logit", r.diff_logit_RE, 2, SD)
    num(f"subtest.{tag}.se_re", r.se_RE, 2, SD)
    num(f"subtest.{tag}.df_re", r.df_RE, 1, SD)
    sg_tag, pn_tag = {"AD": ("AD_single", "AD_panel"), "PD": ("PD_single", "PD_panel"), "ALL": ("single", "panel")}[tag]
    num(f"subtest.{tag}.auc_diff", float(N[f"pool.{pn_tag}.auc3"]) - float(N[f"pool.{sg_tag}.auc3"]), 2, SD)

ev = pd.read_csv(f"{T}/meta_analysis_pooled_auc_sensitivity_every_estimate.csv")
EV = f"{T}/meta_analysis_pooled_auc_sensitivity_every_estimate.csv"
for tag, pre in [("ALL", "Overall"), ("AD", "AD - all"), ("PD", "PD - all")]:
    r = ev[ev.subgroup.str.startswith(pre)].iloc[0]
    integer(f"every.{tag}.k_est", r.k_estimates, EV)
    num(f"every.{tag}.auc", r.pooled_auc, 2, EV)
    num(f"every.{tag}.lo", r.ci_low, 2, EV)
    num(f"every.{tag}.hi", r.ci_high, 2, EV)
    num(f"every.{tag}.i2", r.I2_percent, 1, EV)
    put(f"every.{tag}.egger_p", p_text(r.egger_p), EV)

vs = pd.read_csv(f"{T}/meta_analysis_variance_source_comparison.csv")
VS = f"{T}/meta_analysis_variance_source_comparison.csv"
for tag in ("AD", "PD"):
    r = vs[vs.subgroup.str.startswith(f"{tag} - all markers - reported_only")].iloc[0]
    integer(f"repo.{tag}.k", r.n_studies, VS)
    num(f"repo.{tag}.auc", r.pooled_auc, 2, VS)
    num(f"repo.{tag}.lo", r.ci_low_hk, 2, VS)
    num(f"repo.{tag}.hi", r.ci_high_hk, 2, VS)

# ----------------------------------------------------------------------------- robustness
ra = pd.read_csv(f"{T}/robustness_alternative_analyses.csv")
RA = f"{T}/robustness_alternative_analyses.csv"
for rule_key, rule_name in [("neutral", "marker-type-neutral"), ("asis", "reported CIs as published")]:
    for tag, out in [("AD", "AD - all markers"), ("PD", "PD - all markers"), ("ALL", "AD+PD combined")]:
        r = ra[ra.analysis.str.contains(rule_name, regex=False) & ra.outcome.str.startswith(out)].iloc[0]
        integer(f"rob.{rule_key}.{tag}.k", r.n_studies, RA)
        num(f"rob.{rule_key}.{tag}.auc", r.pooled_auc, 2, RA)
        num(f"rob.{rule_key}.{tag}.lo", r.ci_low_hk, 2, RA)
        num(f"rob.{rule_key}.{tag}.hi", r.ci_high_hk, 2, RA)
        num(f"rob.{rule_key}.{tag}.i2", r.I2_percent, 1, RA)
        put(f"rob.{rule_key}.{tag}.p", p_text(r.panel_vs_single_p), RA)
        put(f"rob.{rule_key}.{tag}.p_re", p_text(r.panel_vs_single_p_RE), RA)
for tag, out in [("AD_panel", "AD - panels"), ("AD_single", "AD - single markers"),
                 ("PD_panel", "PD - panels"), ("PD_single", "PD - single markers")]:
    r = ra[ra.analysis.str.contains("marker-type-neutral", regex=False) & ra.outcome.str.startswith(out)].iloc[0]
    integer(f"rob.neutral.{tag}.k", r.n_studies, RA)
    num(f"rob.neutral.{tag}.auc", r.pooled_auc, 2, RA)

rs = pd.read_csv(f"{T}/robustness_random_selection.csv").set_index("quantity")
RS = f"{T}/robustness_random_selection.csv"
integer("rob.random.draws", rs.loc["AD_auc", "draws_used"], RS)
for tag in ("AD", "PD"):
    num(f"rob.random.{tag}.med", rs.loc[f"{tag}_auc", "median"], 2, RS)
    num(f"rob.random.{tag}.lo", rs.loc[f"{tag}_auc", "p2_5"], 2, RS)
    num(f"rob.random.{tag}.hi", rs.loc[f"{tag}_auc", "p97_5"], 2, RS)
    pctval(f"rob.random.{tag}.frac_sig", rs.loc[f"p_{tag}", "fraction_below_0_05"], 0, RS)
    put(f"rob.random.{tag}.p_med", p_text(rs.loc[f"p_{tag}", "median"]), RS)
    put(f"rob.random.{tag}.p_re_med", p_text(rs.loc[f"p_{tag}_RE", "median"]), RS)
    pctval(f"rob.random.{tag}.frac_sig_re", rs.loc[f"p_{tag}_RE", "fraction_below_0_05"], 0, RS)
pctval("rob.random.ALL.frac_sig", rs.loc["p_combined", "fraction_below_0_05"], 0, RS)
put("rob.random.ALL.p_re_med", p_text(rs.loc["p_combined_RE", "median"]), RS)
pctval("rob.random.ALL.frac_sig_re", rs.loc["p_combined_RE", "fraction_below_0_05"], 0, RS)
put("rob.seed", json.load(open(f"{T}/robustness_summary.json"))["seed"], f"{T}/robustness_summary.json")

lo = pd.read_csv(f"{T}/robustness_leave_one_out_by_disease.csv")
LO = f"{T}/robustness_leave_one_out_by_disease.csv"
for tag in ("AD", "PD"):
    s = lo[(lo.disease == tag) & (~lo.left_out.str.startswith("none"))]
    num(f"rob.loo.{tag}.min", s.pooled_auc.min(), 2, LO)
    num(f"rob.loo.{tag}.max", s.pooled_auc.max(), 2, LO)
    num(f"rob.loo.{tag}.ci_lo_min", s.ci_low_hk.min(), 2, LO)
    num(f"rob.loo.{tag}.ci_hi_max", s.ci_high_hk.max(), 2, LO)
    integer(f"rob.loo.{tag}.n", len(s), LO)

vsp = pd.read_csv(f"{T}/robustness_validation_split_exploratory.csv")
VSP = f"{T}/robustness_validation_split_exploratory.csv"
for tag in ("AD", "PD"):
    a = vsp[(vsp.disease == tag) & (vsp.group.str.contains("separate"))].iloc[0]
    b = vsp[(vsp.disease == tag) & (vsp.group.str.contains("derivation"))].iloc[0]
    t_ = vsp[(vsp.disease == tag) & (vsp.group == "difference test")].iloc[0]
    integer(f"valsplit.{tag}.k_sep", a.n_studies, VSP)
    num(f"valsplit.{tag}.auc_sep", a.pooled_auc, 2, VSP)
    integer(f"valsplit.{tag}.k_der", b.n_studies, VSP)
    num(f"valsplit.{tag}.auc_der", b.pooled_auc, 2, VSP)
    put(f"valsplit.{tag}.p", p_text(t_.p_value), VSP)
    put(f"valsplit.{tag}.p_re", p_text(t_.p_value_RE), VSP)
a = vsp[(vsp.disease == "AD+PD") & (vsp.group.str.contains("separate"))].iloc[0]
integer("valsplit.ALL.k_sep", a.n_studies, VSP)
num("valsplit.ALL.auc_sep", a.pooled_auc, 2, VSP)

ps = pd.read_csv(f"{T}/post_search_sensitivity.csv")
PS = f"{T}/post_search_sensitivity.csv"
for i, tag in enumerate(("base", "rtqpcr", "orca")):
    r = ps.iloc[i]
    integer(f"post.{tag}.k", r.n_studies, PS)
    num(f"post.{tag}.auc", r.pooled_auc, 2, PS)
    num(f"post.{tag}.lo", r.ci_low_hk, 2, PS)
    num(f"post.{tag}.hi", r.ci_high_hk, 2, PS)

cp = pd.read_csv(f"{T}/ci_plausibility_check.csv")
CP = f"{T}/ci_plausibility_check.csv"
fl = cp[cp.flagged_implausible]
oth = cp[~cp.flagged_implausible & cp.se_ratio_ci_over_hm.notna()]
integer("ci.flagged_rows", len(fl), CP)
integer("ci.flagged_studies", fl.first_author.nunique(), CP)
num("ci.flag_ratio_max", fl.se_ratio_ci_over_hm.max(), 3, CP)
num("ci.other_ratio_min", oth.se_ratio_ci_over_hm.min(), 2, CP)
num("ci.other_ratio_max", oth.se_ratio_ci_over_hm.max(), 2, CP)
integer("ci.other_rows", len(oth), CP)

# ----------------------------------------------------------------------------- bivariate
bv = pd.read_csv(f"{T}/bivariate_summary.csv")
BV = f"{T}/bivariate_summary.csv"
p1, p2 = bv.iloc[0], bv.iloc[1]
integer("biv.k", p1.n_studies, BV)
num("biv.sens", p1.summary_sensitivity, 2, BV)
num("biv.sens_lo", p1.sensitivity_ci_low, 2, BV)
num("biv.sens_hi", p1.sensitivity_ci_high, 2, BV)
num("biv.spec", p1.summary_specificity, 2, BV)
num("biv.spec_lo", p1.specificity_ci_low, 2, BV)
num("biv.spec_hi", p1.specificity_ci_high, 2, BV)
num("biv.sens3", p1.summary_sensitivity, 3, BV)
num("biv.spec3", p1.summary_specificity, 3, BV)
num("biv.dor", p1.diagnostic_odds_ratio, 1, BV)
num("biv.lrp", p1.positive_likelihood_ratio, 1, BV)
num("biv.lrn", p1.negative_likelihood_ratio, 2, BV)
num("biv.tau_sens", p1.tau_sensitivity, 2, BV)
num("biv.tau_spec", p1.tau_specificity, 2, BV)
num("biv.rho", p1.rho_between, 2, BV)
integer("biv.all_k_est", p2.k_estimates, BV)
num("biv.all_sens", p2.summary_sensitivity, 2, BV)
num("biv.all_spec", p2.summary_specificity, 2, BV)
bi = pd.read_csv(f"{T}/bivariate_input_estimates.csv")
BI = f"{T}/bivariate_input_estimates.csv"
prim = bi[bi.in_primary_analysis]
integer("biv.k_ad", (prim.disease == "AD").sum(), BI)
integer("biv.k_pd", (prim.disease == "PD").sum(), BI)
bl = pd.read_csv(f"{T}/robustness_bivariate_label_check.csv")
BL = f"{T}/robustness_bivariate_label_check.csv"
integer("biv.nolabel_k", bl.iloc[1].n_studies, BL)
num("biv.nolabel_sens", bl.iloc[1].summary_sensitivity, 2, BL)
num("biv.nolabel_spec", bl.iloc[1].summary_specificity, 2, BL)

# ----------------------------------------------------------------------------- GRADE and summary of findings
gr = json.load(open(f"{T}/grade_certainty.json"))
GR = f"{T}/grade_certainty.json"
for d in ("AD", "PD"):
    g = gr["by_disease"][d]
    put(f"grade.{d}.certainty", g["certainty_of_evidence"], GR)
    integer(f"grade.{d}.steps", g["total_downgrade_steps"], GR)
    for dom in ("risk_of_bias", "indirectness", "inconsistency", "imprecision", "publication_bias"):
        integer(f"grade.{d}.{dom}", g["domains"][dom]["downgrade_steps"], GR)
        put(f"grade.{d}.{dom}_j", g["domains"][dom]["judgement_en"], GR)
th = gr["thresholds"]
num("grade.th.i2", th["inconsistency_serious_i2"], 0, GR)
num("grade.th.ci_width", th["imprecision_serious_ci_width"], 2, GR)
integer("grade.th.min_studies", th["publication_bias_min_studies_for_test"], GR)
for sf in gr["summary_of_findings"]:
    t_ = int(round(sf["pre_test_probability"] * 100))
    integer(f"sof.{t_}.tp", sf["true_positives_per_1000"], GR)
    integer(f"sof.{t_}.fp", sf["false_positives_per_1000"], GR)
    integer(f"sof.{t_}.fn", sf["false_negatives_per_1000"], GR)
    integer(f"sof.{t_}.tn", sf["true_negatives_per_1000"], GR)
    num(f"sof.{t_}.ppv", sf["positive_predictive_value"], 2, GR)
    num(f"sof.{t_}.npv", sf["negative_predictive_value"], 2, GR)
    integer(f"sof.{t_}.pos", sf["true_positives_per_1000"] + sf["false_positives_per_1000"], GR)

# ----------------------------------------------------------------------------- the pooled studies themselves
au = pd.read_csv(f"{T}/one_estimate_per_study_selection_audit.csv")
AU = f"{T}/one_estimate_per_study_selection_audit.csv"
es = pd.read_csv(f"{T}/meta_analysis_input_estimates.csv")
ES = f"{T}/meta_analysis_input_estimates.csv"
es["sid"] = norm_sid(es) + "|" + es.disease
au["sid_key"] = au.study_id.astype(str).str.replace(r"\.0$", "", regex=True)
sel = []
for _, r in au.iterrows():
    cand = es[(es.marker == r.selected_marker) & (es.disease == r.disease)
              & (es.first_author.str.strip() == str(r.first_author).strip()) & (es.year == r.year)]
    if len(cand) != 1:
        cand = cand[cand.cohort_stage == r.selected_cohort_stage]
    if len(cand) != 1:
        raise RuntimeError(f"cannot match selected estimate for {r.first_author} {r.year}")
    sel.append(cand.iloc[0])
sel = pd.DataFrame(sel).reset_index(drop=True)
sel["n_total"] = sel.n_cases + sel.n_controls
integer("n.k", len(sel), AU)
for d in ("AD", "PD"):
    s = sel[sel.disease == d]
    integer(f"n.{d}.k", len(s), AU)
    integer(f"n.{d}.cases", s.n_cases.sum(), ES)
    integer(f"n.{d}.controls", s.n_controls.sum(), ES)
    integer(f"n.{d}.total", s.n_total.sum(), ES)
    integer(f"n.{d}.n_med", s.n_total.median(), ES)
    integer(f"n.{d}.n_min", s.n_total.min(), ES)
    integer(f"n.{d}.n_max", s.n_total.max(), ES)
    num(f"n.{d}.auc_min", s.auc.min(), 2, ES)
    num(f"n.{d}.auc_max", s.auc.max(), 2, ES)
    num(f"n.{d}.auc_med", s.auc.median(), 2, ES)
integer("n.cases", sel.n_cases.sum(), ES)
integer("n.controls", sel.n_controls.sum(), ES)
integer("n.total", sel.n_total.sum(), ES)
integer("n.small", (sel.n_total < 100).sum(), ES)
integer("n.small_cut", 100, ES)
integer("n.year_min", sel.year.min(), AU)
integer("n.year_max", sel.year.max(), AU)
integer("n.since2020", (sel.year >= 2020).sum(), AU)
for key, cond in [("serum", sel.biofluid == "serum"), ("plasma", sel.biofluid == "plasma"),
                  ("ev", sel.biofluid.str.contains("EV|exosome", regex=True))]:
    integer(f"n.bio.{key}", cond.sum(), ES)
integer("n.bio.ev_neuronal", (sel.biofluid.str.contains("neuronal")).sum(), ES)
integer("n.bio.exosome", (sel.biofluid == "serum_exosome").sum(), ES)
integer("n.bio.plasma_ev", (sel.biofluid == "plasma_EV").sum(), ES)
integer("n.stage.single", (sel.cohort_stage == "single").sum(), ES)
integer("n.stage.validation", (sel.cohort_stage == "validation").sum(), ES)
integer("n.stage.cv", (sel.cohort_stage == "cross-validated").sum(), ES)
integer("n.panel_validation", ((sel.marker_type == "multi_miRNA_panel") & (sel.cohort_stage == "validation")).sum(), ES)
integer("n.single_validation", ((sel.marker_type == "single_miRNA") & (sel.cohort_stage == "validation")).sum(), ES)
integer("n.type.single", (sel.marker_type == "single_miRNA").sum(), ES)
integer("n.type.panel", (sel.marker_type == "multi_miRNA_panel").sum(), ES)
integer("n.units_multi", (au.n_candidate_estimates > 1).sum(), AU)
integer("n.est_max_per_study", au.n_candidate_estimates.max(), AU)
num("n.auc_min", sel.auc.min(), 2, ES)
num("n.auc_max", sel.auc.max(), 2, ES)
num("n.auc_med", sel.auc.median(), 2, ES)
integer("n.auc_below70", (sel.auc < 0.70).sum(), ES)
integer("n.auc_above90", (sel.auc >= 0.90).sum(), ES)
meth = ext[ext.eligible_primary_pool == "yes"].copy()
rt = meth.method.str.contains("RT-qPCR|qPCR|ddPCR", regex=True)
seq = meth.method.str.contains("small RNA-seq|microarray|chip|transcriptomics", regex=True, case=False)
integer("n.est_pcr", rt.sum(), EX)
integer("n.est_seq", (seq & ~rt).sum(), EX)
integer("n.est_all_eligible", len(meth), EX)

# replication of single microRNAs across independent units
est_ = es.copy()


def family(n):
    n = str(n).replace("‐", "-").replace("‑", "-").replace(" ", "")
    n = re.sub(r"^hsa-", "", n, flags=re.I)
    if n.lower().startswith("mir-"):
        n = "miR-" + n[4:]
    elif n.lower().startswith("let-"):
        n = "let-" + n[4:]
    return re.sub(r"-[35]p$", "", n)


sg = est_[est_.marker_type == "single_miRNA"].copy()
sg["fam"] = sg.marker.map(family)
rep = sg.groupby("fam").sid.nunique()
integer("repl.families", len(rep), ES)
integer("repl.max_units", rep.max(), ES)
integer("repl.ge3", (rep >= 3).sum(), ES)
integer("repl.ge2", (rep >= 2).sum(), ES)
integer("repl.once", (rep == 1).sum(), ES)
top = sorted(rep[rep == rep.max()].index, key=lambda f: (re.sub(r"\D", "", f).zfill(6), f))
put("repl.names_max", ", ".join(top[:-1]) + " and " + top[-1] if len(top) > 1 else top[0], ES)

# ----------------------------------------------------------------------------- design profile (pooled circulating scope)
dp = pd.read_csv(f"{T}/study_design_profile.csv")
DP = f"{T}/study_design_profile.csv"
pooled_scope = dp[dp.scope == "pooled circulating studies"]


def dpv(field, value):
    r = pooled_scope[(pooled_scope.field == field) & (pooled_scope.value == value)]
    return int(r.n_studies.iloc[0]) if len(r) else 0


integer("des.ref.clinical", dpv("reference_standard_basis", "clinical_criteria"), DP)
integer("des.ref.none", dpv("reference_standard_basis", "not_reported"), DP)
integer("des.ref.biomarker", dpv("reference_standard_basis", "biomarker_supported"), DP)
integer("des.ref.neuropath", dpv("reference_standard_basis", "neuropathological"), DP)
integer("des.ref.abstract", dpv("reference_standard_basis", "not_assessable_no_fulltext"), DP)
integer("des.ref.bio_or_path", dpv("reference_standard_basis", "biomarker_supported")
        + dpv("reference_standard_basis", "neuropathological"), DP)
pooled_ids = set(norm_sid(sel).tolist()) if False else None
ql2 = ql.copy()
ql2["study_id"] = ql2.study_id.astype(str)
pooled_study_ids = set(au.study_id.astype(str))
qp = ql2[ql2.study_id.isin(pooled_study_ids)]
integer("des.ref.named_pooled", (qp.reference_standard_named == "yes").sum(), QL)
dz = pd.read_csv("data/extracted/study_design_preanalytics.csv", dtype=str)
dz["study_id"] = dz.study_id.astype(str)
qd = qp.merge(dz[["study_id", "reference_standard_basis"]], on="study_id", how="left")
clin = qd[qd.reference_standard_basis == "clinical_criteria"]
integer("des.ref.clinical_named", (clin.reference_standard_named == "yes").sum(), QL)
integer("des.ref.clinical_unnamed", (clin.reference_standard_named != "yes").sum(), QL)
integer("des.ref.not_named_total", (clin.reference_standard_named != "yes").sum() + dpv("reference_standard_basis", "not_reported"), QL)
integer("des.stage.mixed", dpv("disease_stage", "mixed"), DP)
integer("des.stage.not_reported", dpv("disease_stage", "not_reported"), DP)
integer("des.stage.established", dpv("disease_stage", "established"), DP)
integer("des.stage.early", dpv("disease_stage", "early"), DP)
integer("des.med.not_reported", dpv("medication_status", "not_reported"), DP)
integer("des.med.reported", sum(dpv("medication_status", v) for v in ("treated", "mixed", "drug_naive")), DP)
integer("des.med.naive", dpv("medication_status", "drug_naive"), DP)
integer("des.hem.not_reported", dpv("haemolysis_handling", "not_reported"), DP)
integer("des.hem.procedural", dpv("haemolysis_handling", "procedural_only"), DP)
integer("des.hem.excluded_ns", dpv("haemolysis_handling", "excluded_method_not_stated"), DP)
integer("des.hem.measured", dpv("haemolysis_handling", "measured_and_excluded"), DP)
integer("des.hem.abstract", dpv("haemolysis_handling", "not_assessable_no_fulltext"), DP)
integer("des.cand.a_priori", dpv("candidate_selection", "a_priori_literature"), DP)
integer("des.cand.discovery", dpv("candidate_selection", "separate_discovery_sample"), DP)
integer("des.cand.same", dpv("candidate_selection", "same_sample_data_driven"), DP)
integer("des.cand.training", dpv("candidate_selection", "training_split_only"), DP)
integer("des.val.none", dpv("validation_design", "none_single_sample"), DP)
integer("des.val.roc_eval", dpv("validation_design", "separate_discovery_then_roc_in_evaluation_sample"), DP)
integer("des.val.resampling", dpv("validation_design", "internal_resampling"), DP)
integer("des.val.split", dpv("validation_design", "random_split_holdout"), DP)
integer("des.val.independent", dpv("validation_design", "independent_cohort_locked_model"), DP)
integer("des.thr.no", dpv("threshold_prespecified", "no"), DP)
integer("des.norm.u6", dpv("normalization", "snRNA_U6"), DP)
integer("des.norm.endog", dpv("normalization", "endogenous_miRNA") + dpv("normalization", "spike_in_plus_endogenous_miRNA"), DP)
integer("des.norm.spike", dpv("normalization", "spike_in") + dpv("normalization", "spike_in_plus_endogenous_miRNA"), DP)
integer("des.norm.not_reported", dpv("normalization", "not_reported") + dpv("normalization", "none_raw_ct"), DP)

# ----------------------------------------------------------------------------- molecular evidence map
mm = pd.read_csv("data/extracted/molecular_evidence_map.csv")
MM = "data/extracted/molecular_evidence_map.csv"
integer("mol.rows", len(mm), MM)
integer("mol.studies", mm.study_id.astype(str).nunique(), MM)
vc = mm.groupby("axis_group").study_id.nunique()
for key, grp in [("inflam", "Neuroinflammation and innate immunity"), ("tau", "Tau, synaptic and neuronal signalling"),
                 ("clinical", "Correlation with clinical or biomarker measures"), ("amyloid", "Amyloid and APP processing"),
                 ("synuclein", "Alpha-synuclein biology"), ("survival", "Cell survival, apoptosis and proteostasis"),
                 ("none", "none")]:
    integer(f"mol.axis.{key}", vc.get(grp, 0), MM)
et = mm[mm.axis_group != "none"].groupby("study_id").evidence_type.apply(set)
order = ["experimental_in_included_study", "paired_brain_tissue", "experimental_cited_from_authors_prior_work",
         "literature_cited", "in_silico_prediction", "clinical_correlation"]
integer("mol.studies_experiment", sum(1 for s in et if "experimental_in_included_study" in s), MM)
integer("mol.studies_literature_only", sum(1 for s in et if s <= {"literature_cited"}), MM)
integer("mol.studies_with_axis", len(et), MM)
integer("mol.studies_none", mm.study_id.astype(str).nunique() - len(et), MM)
integer("mol.rows_experiment", (mm.evidence_type == "experimental_in_included_study").sum(), MM)
integer("mol.rows_literature", (mm.evidence_type == "literature_cited").sum(), MM)
integer("mol.rows_insilico", (mm.evidence_type == "in_silico_prediction").sum(), MM)
integer("mol.rows_clinical", (mm.evidence_type == "clinical_correlation").sum(), MM)
integer("mol.axes", mm[mm.axis_group != "none"].axis_group.nunique(), MM)

# ----------------------------------------------------------------------------- attention versus accuracy (exploratory)
ca = json.load(open(f"{T}/citation_vs_auc_correlation.json"))
CA = f"{T}/citation_vs_auc_correlation.json"
integer("att.all.n", ca[0]["n_mirnas"], CA)
num("att.all.rho", ca[0]["spearman_rho"], 2, CA)
put("att.all.p", p_text(ca[0]["spearman_p"]), CA)
integer("att.elig.n", ca[1]["n_mirnas"], CA)
num("att.elig.rho", ca[1]["spearman_rho"], 2, CA)
put("att.elig.p", p_text(ca[1]["spearman_p"]), CA)
aa = pd.read_csv(f"{T}/attention_correlation_audit.csv")
AA = f"{T}/attention_correlation_audit.csv"
num("att.strict.rho", aa.iloc[3].rho_eligible, 2, AA)
put("att.strict.p", p_text(aa.iloc[3].p_eligible), AA)
num("att.old.rho", aa.iloc[0].rho_eligible, 2, AA)
put("att.old.p", p_text(aa.iloc[0].p_eligible), AA)

# ----------------------------------------------------------------------------- CSF
cs = pd.read_csv(f"{T}/csf_secondary_estimates.csv")
CS = f"{T}/csf_secondary_estimates.csv"
integer("csf.k", len(cs), CS)
num("csf.auc_min", cs.auc.min(), 2, CS)
num("csf.auc_max", cs.auc.max(), 2, CS)
integer("csf.eligible_studies", 4, "docs/en/METHODS.md (four eligible CSF studies; three have an estimable SE)")

# ----------------------------------------------------------------------------- prior meta-analyses
pm = json.load(open("data/raw/systematic_review_2026/prior_meta_analyses.json"))["studies"]
PM = "data/raw/systematic_review_2026/prior_meta_analyses.json"
byp = {s["pmid"]: s for s in pm}
for pmid, tag in [("38460993", "zhang_ad"), ("39232595", "zhang_pd"), ("37770507", "guev"), ("40783152", "liu"),
                  ("26903857", "hu")]:
    s = byp[pmid]
    num(f"prior.{tag}.auc", s["pooled_auc_sroc"], 2, PM)
    num(f"prior.{tag}.auc_lo", s["auc_ci"][0], 2, PM) if "auc_ci" in s else None
    num(f"prior.{tag}.auc_hi", s["auc_ci"][1], 2, PM) if "auc_ci" in s else None

# ----------------------------------------------------------------------------- search window
sj = json.load(open("data/raw/systematic_review_2026/search_strategy.json"))
put("search.year_from", "2015", "data/raw/systematic_review_2026/search_strategy.json (date_filter)")
mf = pd.read_csv("data/raw/systematic_review_2026/exports_manifest.csv")
MF = "data/raw/systematic_review_2026/exports_manifest.csv"


def long_date(iso):
    y, m, d = iso.split("-")
    months = ["January", "February", "March", "April", "May", "June", "July", "August", "September",
              "October", "November", "December"]
    return f"{int(d)} {months[int(m) - 1]} {y}"


put("search.date_pubmed", long_date(sj["search_date"]), "data/raw/systematic_review_2026/search_strategy.json")
put("search.date_scopus", long_date(mf[mf.database == "Scopus"].search_date.iloc[0]), MF)
put("search.date_wos", long_date(mf[mf.database == "Web of Science"].search_date.iloc[0]), MF)
from datetime import date as _date
put("search.gap_days", (_date.fromisoformat(mf[mf.database == "Web of Science"].search_date.iloc[0])
                        - _date.fromisoformat(mf[mf.database == "Scopus"].search_date.iloc[0])).days, MF)
put("search.date_recall", "28 September 2026", "data/processed/prisma_flow.json (recall_check note) and docs/en/METHODS.md")
put("search.date_update", "24 September 2026", "data/extracted/post_search_candidates.csv (PubMed entry date of the update study)")

put("_sources", json.dumps(SRC, indent=1), "this script")
os.makedirs(T, exist_ok=True)
out = dict(N)
out["_sources"] = SRC
with open(OUT, "w", encoding="utf-8") as fh:
    json.dump(out, fh, indent=1, ensure_ascii=False, sort_keys=True)
print(f"EN | wrote {len(N) - 1} values to {OUT}")
print(f"PT | gravou {len(N) - 1} valores em {OUT}")
