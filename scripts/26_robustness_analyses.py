#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EN | Robustness analyses for the primary AUC pools, added after the 2026-09-28
     full-text audit. None of them replaces the primary analysis in
     scripts/05_meta_analysis.py; each asks how much a specific analytic choice
     moves the answer.
PT | Analises de robustez dos pools primarios de AUC, adicionadas depois da
     auditoria de texto completo de 2026-09-28. Nenhuma substitui a analise
     primaria de scripts/05_meta_analysis.py; cada uma pergunta quanto uma
     escolha analitica especifica move a resposta.

EN | What is run, and why.
     1. Marker-type-neutral selection rule. The primary rule prefers a study's
        own panel over its component markers, which favours panels by
        construction in any panel-versus-single comparison. The alternative
        drops that step (validation sample > larger N > alphabetical).
     2. Random AUC-blind selection. 2,000 draws, each picking one qualifying
        estimate per study uniformly at random, report how far the pooled AUC
        and the panel-versus-single test can move under any selection that
        ignores the AUC itself.
     3. Leave-one-study-out, per disease, on the primary selection.
     4. Reported confidence intervals as published (no plausibility rule;
        see CI_PLAUSIBILITY_RATIO in 05).
     5. Panel-subgroup audit: every study in each disease's panel subgroup,
        with its AUC, interval, group sizes, SE source and weight.
     6. Sensitivity/specificity label check: whether each published
        sensitivity is integer-consistent with the case group size and each
        specificity with the control group size, or only with the swapped
        sizes. Rows consistent only with swapped labels are flagged, and the
        bivariate model is refitted without them.
     7. Study design and pre-analytical profile of the pooled studies, from
        data/extracted/study_design_preanalytics.csv, and an exploratory split
        of the pooled AUC by whether the selected estimate came from
        participants separate from those the markers were chosen in.
PT | O que roda, e por que.
     1. Regra de selecao neutra quanto ao tipo de marcador. A regra primaria
        prefere o painel proprio do estudo a seus marcadores componentes, o
        que favorece paineis por construcao em qualquer comparacao painel
        versus isolado. A alternativa remove essa etapa (amostra de validacao >
        maior N > alfabetica).
     2. Selecao aleatoria cega a AUC. 2.000 sorteios, cada um escolhendo uma
        estimativa qualificada por estudo ao acaso, mostram quanto a AUC
        agregada e o teste painel versus isolado podem se mover sob qualquer
        selecao que ignore a propria AUC.
     3. Deixar-um-estudo-de-fora, por doenca, na selecao primaria.
     4. Intervalos de confianca como publicados (sem a regra de
        plausibilidade; ver CI_PLAUSIBILITY_RATIO em 05).
     5. Auditoria do subgrupo de paineis: cada estudo do subgrupo de paineis
        de cada doenca, com AUC, intervalo, tamanhos de grupo, origem do EP e
        peso.
     6. Checagem de rotulos de sensibilidade/especificidade: se cada
        sensibilidade publicada e consistente com um inteiro sobre o grupo de
        casos e cada especificidade sobre o grupo controle, ou so com os
        tamanhos trocados. Linhas consistentes so com rotulos trocados sao
        sinalizadas, e o modelo bivariado e reajustado sem elas.
     7. Perfil de desenho e pre-analitico dos estudos agregados, a partir de
        data/extracted/study_design_preanalytics.csv, e uma divisao
        exploratoria da AUC agregada pelo fato de a estimativa selecionada vir
        de participantes separados daqueles em que os marcadores foram
        escolhidos.

    python scripts/26_robustness_analyses.py
"""

import csv
import importlib.util
import json
import os
import sys
from collections import Counter, OrderedDict

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import _study_selection as _sel

TAB_DIR = "results/tables"
DESIGN = "data/extracted/study_design_preanalytics.csv"
N_RANDOM_DRAWS = 2000
SEED = 20260928


def _load(name, filename):
    spec = importlib.util.spec_from_file_location(name, os.path.join(HERE, filename))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


ma = _load("meta_analysis_05", "05_meta_analysis.py")
bv = _load("bivariate_15", "15_bivariate_srocc.py")


def pooled(coll):
    """EN/PT: Paule-Mandel + mHK pool of a one-row-per-study frame (columns y, v)."""
    r = ma.pool_re(coll["y"].values, coll["v"].values, tau2_method="PM")
    if r is None:
        return None
    f = ma.inv_logit
    return OrderedDict([
        ("n_studies", r["k"]), ("pooled_auc", round(f(r["estimate"]), 4)),
        ("ci_low_hk", round(f(r["ci_low_hk"]), 4) if not np.isnan(r["ci_low_hk"]) else ""),
        ("ci_high_hk", round(f(r["ci_high_hk"]), 4) if not np.isnan(r["ci_high_hk"]) else ""),
        ("I2_percent", round(r["I2"], 1))])


def with_yv(sub):
    sub = sub.dropna(subset=["auc", "se_auc"]).copy()
    sub["y"] = ma.logit(sub["auc"].values)
    sub["v"] = (sub["se_auc"].values / (sub["auc"].values * (1 - sub["auc"].values))) ** 2
    return sub


def select(pool, panel_preference=True):
    sub = with_yv(pool)
    rows = []
    for sid, g in sub.groupby("study_id"):
        picked, _reason, n = _sel.select_one_per_study(g.to_dict("records"),
                                                       panel_preference=panel_preference)
        rows.append(dict(study_id=sid, y=picked["y"], v=picked["v"], disease=picked["disease"],
                         marker=picked["marker"], marker_type=picked["marker_type"],
                         cohort_stage=picked["cohort_stage"], auc=picked["auc"],
                         first_author=picked["first_author"], year=picked["year"],
                         n_candidate_estimates=n))
    return pd.DataFrame(rows)


def panel_test(sel, disease=None):
    base = sel if disease is None else sel[sel["disease"] == disease]
    single = base[base["marker_type"] == "single_miRNA"]
    panel = base[base["marker_type"] == "multi_miRNA_panel"]
    if len(single) < 1 or len(panel) < 1:
        return None
    r = ma.subgroup_difference_test(single, panel, "x")
    return r


def outcome_rows(label, sel):
    out = []
    for d in ["AD", "PD"]:
        p = pooled(sel[sel["disease"] == d])
        t = panel_test(sel, d)
        out.append(OrderedDict([("analysis", label), ("outcome", f"{d} - all markers"), *p.items(),
                                ("panel_vs_single_Q", t["Q_between"] if t else ""),
                                ("panel_vs_single_p", t["p_value"] if t else "")]))
    t = panel_test(sel)
    p = pooled(sel)
    out.append(OrderedDict([("analysis", label), ("outcome", "AD+PD combined (secondary)"), *p.items(),
                            ("panel_vs_single_Q", t["Q_between"] if t else ""),
                            ("panel_vs_single_p", t["p_value"] if t else "")]))
    for d in ["AD", "PD"]:
        for mt, lab in [("multi_miRNA_panel", "panels"), ("single_miRNA", "single markers")]:
            p = pooled(sel[(sel["disease"] == d) & (sel["marker_type"] == mt)])
            if p:
                out.append(OrderedDict([("analysis", label), ("outcome", f"{d} - {lab}"), *p.items(),
                                        ("panel_vs_single_Q", ""), ("panel_vs_single_p", "")]))
    return out


def random_selection(pool, rng):
    """EN/PT: one AUC-blind uniformly random qualifying estimate per study."""
    sub = with_yv(pool)
    picks = []
    for _sid, g in sub.groupby("study_id"):
        picks.append(g.iloc[int(rng.integers(len(g)))])
    s = pd.DataFrame(picks)
    return s.rename(columns={})[["study_id", "y", "v", "disease", "marker_type"]]


def sens_spec_label_check(df):
    """
    EN | For every row with a published sensitivity, specificity and both group
         sizes: is sensitivity x n_cases (and specificity x n_controls) within
         rounding of an integer, given the number of decimals reported? And is
         the swapped assignment? A row consistent only with the swap is flagged.
    PT | Para toda linha com sensibilidade, especificidade e os dois tamanhos de
         grupo publicados: sensibilidade x n_casos (e especificidade x
         n_controles) fica dentro do arredondamento de um inteiro, dado o numero
         de decimais reportado? E a atribuicao trocada? Uma linha consistente so
         com a troca e sinalizada.
    """
    raw = {r["record_id"]: r for r in csv.DictReader(open(ma.IN_CSV, encoding="utf-8"))}

    def decimals_pct(txt):
        pct = float(txt) * 100
        s = f"{pct:.6f}".rstrip("0").rstrip(".")
        return len(s.split(".")[1]) if "." in s else 0

    def consistent(p_txt, n):
        p = float(p_txt)
        tol = n * 0.5 * 10 ** (-decimals_pct(p_txt)) / 100 + 1e-9
        x = p * n
        return abs(x - round(x)) <= tol

    out = []
    for rid, r in raw.items():
        if not (r["sensitivity"] and r["specificity"] and r["n_cases"] and r["n_controls"]):
            continue
        n1, n0 = int(float(r["n_cases"])), int(float(r["n_controls"]))
        if n1 == n0:
            continue
        as_labelled = consistent(r["sensitivity"], n1) and consistent(r["specificity"], n0)
        swapped = consistent(r["sensitivity"], n0) and consistent(r["specificity"], n1)
        verdict = ("consistent" if as_labelled else
                   "consistent_only_if_labels_swapped" if swapped else "not_integer_consistent_either_way")
        out.append(OrderedDict([("record_id", rid), ("first_author", r["first_author"]),
                                ("year", r["year"]), ("marker", r["marker"]),
                                ("eligible_primary_pool", r["eligible_primary_pool"]),
                                ("n_cases", n1), ("n_controls", n0),
                                ("sensitivity", r["sensitivity"]), ("specificity", r["specificity"]),
                                ("verdict", verdict)]))
    return out


def main():
    os.makedirs(TAB_DIR, exist_ok=True)
    _df, _elig, _poolable, _csf, pool = ma.load_estimates(ci_plausibility=True)
    _df_r, _e_r, _p_r, _c_r, pool_as_reported = ma.load_estimates(ci_plausibility=False)

    rows = []
    sel_primary = select(pool, panel_preference=True)
    rows += outcome_rows("primary rule (panel preferred), CI plausibility rule", sel_primary)
    sel_neutral = select(pool, panel_preference=False)
    rows += outcome_rows("marker-type-neutral rule (no panel preference)", sel_neutral)
    sel_reported = select(pool_as_reported, panel_preference=True)
    rows += outcome_rows("primary rule, reported CIs as published (no plausibility rule)", sel_reported)
    pd.DataFrame(rows).to_csv(f"{TAB_DIR}/robustness_alternative_analyses.csv", index=False)

    # 2. random AUC-blind selection
    rng = np.random.default_rng(SEED)
    draws = OrderedDict((k, []) for k in ["AD_auc", "PD_auc", "p_AD", "p_PD", "p_combined"])
    for _ in range(N_RANDOM_DRAWS):
        s = random_selection(pool, rng)
        draws["AD_auc"].append(pooled(s[s["disease"] == "AD"])["pooled_auc"])
        draws["PD_auc"].append(pooled(s[s["disease"] == "PD"])["pooled_auc"])
        for key, d in [("p_AD", "AD"), ("p_PD", "PD"), ("p_combined", None)]:
            t = panel_test(s, d)
            draws[key].append(float(t["p_value"]) if t and t["p_value"] != "" else np.nan)
    rand_rows = []
    for key, vals in draws.items():
        a = np.array(vals, float)
        a = a[~np.isnan(a)]
        row = OrderedDict([("quantity", key), ("draws_used", len(a)),
                           ("median", round(float(np.median(a)), 4)),
                           ("p2_5", round(float(np.percentile(a, 2.5)), 4)),
                           ("p97_5", round(float(np.percentile(a, 97.5)), 4))])
        if key.startswith("p_"):
            row["fraction_below_0_05"] = round(float(np.mean(a < 0.05)), 4)
        rand_rows.append(row)
    pd.DataFrame(rand_rows).to_csv(f"{TAB_DIR}/robustness_random_selection.csv", index=False)

    # 3. leave-one-study-out per disease
    loo = []
    for d in ["AD", "PD"]:
        base = sel_primary[sel_primary["disease"] == d]
        p = pooled(base)
        loo.append(OrderedDict([("disease", d), ("left_out", "none (primary)"), *p.items()]))
        for _, r in base.sort_values(["year", "first_author"]).iterrows():
            p = pooled(base[base["study_id"] != r["study_id"]])
            loo.append(OrderedDict([("disease", d),
                                    ("left_out", f"{r['first_author']} {r['year']} ({r['marker']})"), *p.items()]))
    pd.DataFrame(loo).to_csv(f"{TAB_DIR}/robustness_leave_one_out_by_disease.csv", index=False)

    # 5. panel-subgroup audit
    sub = with_yv(pool)
    audit = []
    for d in ["AD", "PD"]:
        panels = sel_primary[(sel_primary["disease"] == d) &
                             (sel_primary["marker_type"] == "multi_miRNA_panel")]
        if panels.empty:
            continue
        r = ma.pool_re(panels["y"].values, panels["v"].values, tau2_method="PM")
        w = 1.0 / (panels["v"].values + r["tau2"])
        for (_, p), wi in zip(panels.iterrows(), w):
            src = sub[(sub["study_id"] == p["study_id"]) & (sub["marker"] == p["marker"]) &
                      (sub["cohort_stage"] == p["cohort_stage"])].iloc[0]
            audit.append(OrderedDict([
                ("disease", d), ("first_author", p["first_author"]), ("year", p["year"]),
                ("record_id", src["record_id"]), ("marker", p["marker"]),
                ("cohort_stage", p["cohort_stage"]), ("n_cases", src["n_cases"]),
                ("n_controls", src["n_controls"]), ("auc", src["auc"]),
                ("reported_ci", f"{src['auc_ci_low']}-{src['auc_ci_high']}"
                 if pd.notna(src["auc_ci_low"]) else ""),
                ("se_auc_used", round(float(src["se_auc"]), 4)), ("se_source", src["se_source"]),
                ("weight_percent", round(100 * wi / w.sum(), 1)),
                ("source", src["source"])]))
    pd.DataFrame(audit).to_csv(f"{TAB_DIR}/panel_subgroup_audit.csv", index=False)

    # 6. sensitivity/specificity label check + bivariate refit without flagged rows
    chk = sens_spec_label_check(_df)
    pd.DataFrame(chk).to_csv(f"{TAB_DIR}/sens_spec_label_check.csv", index=False)
    flagged = {c["record_id"] for c in chk if c["verdict"] == "consistent_only_if_labels_swapped"}
    usable, chosen = bv.load_pairs()
    flagged_studies = {bv.study_id(r) for r in usable if r["record_id"] in flagged}
    chosen_clean = [r for r in chosen if bv.study_id(r) not in flagged_studies]
    biv_rows = []
    for label, rows_ in [("one estimate per study (primary)", chosen),
                         ("one estimate per study, excluding studies with label-inconsistent sens/spec",
                          chosen_clean)]:
        y, v, meta = bv.prepare(rows_)
        fit = bv.fit_bivariate(y, v)
        s = bv.summarise(fit, label, len(rows_), len({m["study_id"] for m in meta}))
        biv_rows.append(s)
    pd.DataFrame(biv_rows).to_csv(f"{TAB_DIR}/robustness_bivariate_label_check.csv", index=False)

    # 7. design / pre-analytics profile of the pooled studies, and an exploratory split
    design = {r["study_id"]: r for r in csv.DictReader(open(DESIGN, encoding="utf-8"))}
    pooled_ids = set(sel_primary["study_id"])
    fields = ["reference_standard_basis", "disease_stage", "medication_status", "haemolysis_handling",
              "normalization", "candidate_selection", "validation_design", "threshold_prespecified"]
    prof = []
    for f in fields:
        for scope, ids in [("pooled circulating studies", pooled_ids), ("all eligible studies", set(design))]:
            c = Counter(design[i][f] for i in ids if i in design)
            for k, n in sorted(c.items(), key=lambda kv: (-kv[1], kv[0])):
                prof.append(OrderedDict([("field", f), ("scope", scope), ("value", k), ("n_studies", n)]))
    missing = sorted(pooled_ids - set(design))
    if missing:
        sys.exit(f"EN/PT: pooled studies missing from {DESIGN}: {missing}")
    pd.DataFrame(prof).to_csv(f"{TAB_DIR}/study_design_profile.csv", index=False)

    split = []
    sep = sel_primary["cohort_stage"].eq("validation")
    for d in ["AD", "PD", None]:
        base_mask = sel_primary["disease"].eq(d) if d else pd.Series(True, index=sel_primary.index)
        for lab, m in [("selected estimate from separate participants", sep),
                       ("selected estimate from the derivation sample", ~sep)]:
            p = pooled(sel_primary[base_mask & m])
            if p:
                split.append(OrderedDict([("disease", d or "AD+PD"), ("group", lab), *p.items()]))
        t = ma.subgroup_difference_test(sel_primary[base_mask & ~sep], sel_primary[base_mask & sep], "x") \
            if (base_mask & sep).sum() >= 1 and (base_mask & ~sep).sum() >= 1 else None
        if t:
            split.append(OrderedDict([("disease", d or "AD+PD"), ("group", "difference test"),
                                      ("n_studies", ""), ("pooled_auc", ""), ("ci_low_hk", ""),
                                      ("ci_high_hk", ""), ("I2_percent", ""),
                                      ("Q_between", t["Q_between"]), ("p_value", t["p_value"])]))
    pd.DataFrame(split).to_csv(f"{TAB_DIR}/robustness_validation_split_exploratory.csv", index=False)

    summary = OrderedDict([
        ("random_draws", N_RANDOM_DRAWS), ("seed", SEED),
        ("ci_plausibility_ratio", ma.CI_PLAUSIBILITY_RATIO),
        ("studies_flagged_label_swap", sorted(flagged_studies)),
    ])
    json.dump(summary, open(f"{TAB_DIR}/robustness_summary.json", "w", encoding="utf-8"), indent=2)

    for f in ["robustness_alternative_analyses", "robustness_random_selection",
              "robustness_leave_one_out_by_disease", "panel_subgroup_audit", "sens_spec_label_check",
              "robustness_bivariate_label_check", "robustness_validation_split_exploratory"]:
        print("\n" + "=" * 78 + f"\n{f}\n" + "=" * 78)
        print(pd.read_csv(f"{TAB_DIR}/{f}.csv").to_string(index=False))


if __name__ == "__main__":
    main()
