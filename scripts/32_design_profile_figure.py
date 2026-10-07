#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EN | Design and reporting profile of the pooled studies as a unit chart: one row per
     feature, one square per study, squares ordered from the most to the least rigorous
     practice. The counts that the Results used to give in a long paragraph are read
     from the squares, and each segment carries its own count and label.

     Counts are recomputed here from data/extracted/study_design_preanalytics.csv and
     quadas2_study_level.csv for the studies in the primary pool, and the script stops
     if a count differs from results/tables/study_design_profile.csv, which scripts/26
     wrote from the same files.

     python scripts/32_design_profile_figure.py

PT | Perfil de desenho e de relato dos estudos agregados como grafico de unidades: uma
     linha por caracteristica, um quadrado por estudo, quadrados ordenados da pratica
     mais rigorosa a menos rigorosa. As contagens que os Resultados davam num paragrafo
     longo sao lidas nos quadrados, e cada segmento traz sua contagem e seu rotulo.

     As contagens sao recalculadas aqui a partir de study_design_preanalytics.csv e
     quadas2_study_level.csv para os estudos do pool primario, e o script para se uma
     contagem divergir de results/tables/study_design_profile.csv, gravado pelo
     scripts/26 a partir dos mesmos arquivos.
"""

import csv
import os
import sys
from collections import Counter

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _bilingual import LANGS, t, fig_path
from _viz_style import INK, INK2, INK3, RULE, PAGE, BAND, rounded, panel_letter

DESIGN = "data/extracted/study_design_preanalytics.csv"
QUADAS = "data/extracted/quadas2_study_level.csv"
SELECTION = "results/tables/one_estimate_per_study_selection_audit.csv"
PROFILE = "results/tables/study_design_profile.csv"
FIG_DIR = "results/figures"
STEM = "design_profile"

RAMP = ["#0d366b", "#1c5cab", "#5598e7", "#9ec5f4"]   # strongest practice first (steps of one blue ramp)
GAP = "#cfcdc7"                                       # reported as absent, or not reported
NA = None                                             # abstract only: drawn as an empty outlined square


def load():
    sel = {r["study_id"].lower() for r in csv.DictReader(open(SELECTION, encoding="utf-8"))}
    des = {r["study_id"].lower(): r for r in csv.DictReader(open(DESIGN, encoding="utf-8")) if r["study_id"].lower() in sel}
    qs = {r["study_id"].lower(): r for r in csv.DictReader(open(QUADAS, encoding="utf-8")) if r["study_id"].lower() in sel}
    if len(des) != len(sel) or len(qs) != len(sel):
        sys.exit(f"EN/PT: design rows {len(des)}, quadas rows {len(qs)}, pooled studies {len(sel)}")
    return sel, des, qs


def reference_standard(d, q):
    if d["reference_standard_basis"] == "not_assessable_no_fulltext":
        return "na"
    if d["reference_standard_basis"] in ("neuropathological", "biomarker_supported"):
        return "biological"
    return "named" if q["reference_standard_named"] == "yes" else "none"


FEATURES = [
    # (key, label EN, label PT, getter, [(code, label EN, label PT, colour)])
    ("reference", "Reference standard", "Padrão de referência", reference_standard, [
        ("biological", "biomarker or neuropathology", "biomarcador ou neuropatologia", RAMP[0]),
        ("named", "named clinical criteria", "critérios clínicos nomeados", RAMP[1]),
        ("none", "no criteria named", "nenhum critério nomeado", GAP)]),
    ("candidate_selection", "Candidate markers chosen", "Escolha dos marcadores", lambda d, q: d["candidate_selection"], [
        ("a_priori_literature", "a priori, from literature", "a priori, pela literatura", RAMP[0]),
        ("separate_discovery_sample", "separate discovery sample", "amostra de descoberta separada", RAMP[1]),
        ("training_split_only", "training split", "partição de treino", RAMP[2]),
        ("same_sample_data_driven", "same participants as evaluation", "mesmos participantes da avaliação", GAP)]),
    ("validation_design", "Validation", "Validação", lambda d, q: d["validation_design"], [
        ("independent_cohort_locked_model", "independent cohort", "coorte independente", RAMP[0]),
        ("random_split_holdout", "random split", "partição aleatória", RAMP[1]),
        ("internal_resampling", "resampling", "reamostragem", RAMP[2]),
        ("separate_discovery_then_roc_in_evaluation_sample", "ROC in evaluation sample", "ROC na amostra de avaliação", RAMP[3]),
        ("none_single_sample", "none", "nenhuma", GAP)]),
    ("threshold_prespecified", "Threshold pre-specified", "Limiar pré-especificado", lambda d, q: d["threshold_prespecified"], [
        ("yes", "yes", "sim", RAMP[0]),
        ("no", "no", "não", GAP)]),
    ("haemolysis_handling", "Haemolysis", "Hemólise", lambda d, q: d["haemolysis_handling"], [
        ("measured_and_excluded", "measured, excluded", "medida, excluída", RAMP[0]),
        ("excluded_method_not_stated", "excluded, method not stated", "excluída, método não declarado", RAMP[1]),
        ("procedural_only", "procedures only", "só procedimentos", RAMP[2]),
        ("not_reported", "not reported", "não relatada", GAP)]),
    ("medication_status", "Medication status", "Medicação", lambda d, q: d["medication_status"], [
        ("reported", "reported", "relatada", RAMP[0]),
        ("not_reported", "not reported", "não relatada", GAP)]),
]


def tally(des, qs):
    out = {}
    for key, _en, _pt, getter, cats in FEATURES:
        c = Counter()
        for sid, d in des.items():
            v = getter(d, qs[sid])
            if key == "medication_status" and v in ("treated", "mixed", "drug_naive"):
                v = "reported"
            if v == "not_assessable_no_fulltext":
                v = "na"
            c[v] += 1
        known = {code for code, *_ in cats} | {"na"}
        stray = set(c) - known
        if stray:
            sys.exit(f"EN/PT: unlisted category in {key}: {stray}")
        out[key] = c
    return out


def check_against_profile(counts):
    prof = {(r["field"], r["value"]): int(r["n_studies"]) for r in csv.DictReader(open(PROFILE, encoding="utf-8"))
            if r["scope"] == "pooled circulating studies"}
    for field in ("candidate_selection", "validation_design", "threshold_prespecified", "haemolysis_handling"):
        for code, n in counts[field].items():
            code_p = "not_assessable_no_fulltext" if code == "na" else code
            if prof.get((field, code_p), 0) != n:
                sys.exit(f"EN/PT: {field}={code_p} gives {n} here but {prof.get((field, code_p), 0)} in {PROFILE}")
    med = sum(prof.get(("medication_status", k), 0) for k in ("treated", "mixed", "drug_naive"))
    if counts["medication_status"]["reported"] != med:
        sys.exit("EN/PT: medication count differs from the profile table")


def plot(counts, n, path, lang):
    """EN/PT: squares are true squares (equal aspect); each row is followed by its own key | os quadrados sao quadrados de fato; cada linha e seguida da propria chave."""
    pitch = 4.7
    margin = 11.0
    total_w = margin + n + 1.0
    total_h = len(FEATURES) * pitch + 2.0
    fig = plt.figure(figsize=(7.4, 7.4 * total_h / total_w))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(-margin, n + 1.0)
    ax.set_ylim(total_h, 0)
    ax.set_aspect("equal")
    ax.axis("off")
    for r, (key, en, pt, _g, cats) in enumerate(FEATURES):
        y0 = 0.9 + r * pitch
        ax.text(-margin + 0.3, y0 + 0.5, t(lang, en, pt), ha="left", va="center", fontsize=7.6, fontweight="bold", color=INK)
        x = 0
        items = []
        for code, len_en, len_pt, colour in cats + [("na", "abstract only", "só resumo", None)]:
            k = counts[key].get(code, 0)
            if not k:
                continue
            for i in range(k):
                if colour is None:
                    rounded(ax, x + i + 0.1, y0 + 0.1, 0.8, 0.8, PAGE, ec=RULE, lw=0.8, r=0.12)
                else:
                    rounded(ax, x + i + 0.1, y0 + 0.1, 0.8, 0.8, colour, r=0.12)
            items.append((k, t(lang, len_en, len_pt), colour))
            x += k
        # key under the row, wrapped at the width of the squares
        kx, ky = 0.0, y0 + 1.9
        for k, lab, colour in items:
            text = f"{k}  {lab}"
            w = 0.36 * len(text) + 3.4
            if kx + w > n + 1.0 and kx > 0:
                kx, ky = 0.0, ky + 1.5
            if colour is None:
                rounded(ax, kx, ky - 0.45, 0.9, 0.9, PAGE, ec=RULE, lw=0.8, r=0.12)
            else:
                rounded(ax, kx, ky - 0.45, 0.9, 0.9, colour, r=0.12)
            ax.text(kx + 1.3, ky, text, ha="left", va="center", fontsize=5.8, color=INK2)
            kx += w
        if r < len(FEATURES) - 1:
            ax.plot([-margin + 0.3, n + 0.8], [y0 + pitch - 0.3] * 2, color=BAND, lw=0.8)
    ax.text(-margin + 0.3, total_h - 0.5, t(lang, "One square = one pooled study (n = %d). Darker = more rigorous practice; grey = absent or not reported; outlined = abstract only, not assessable." % n,
                                         "Um quadrado = um estudo agregado (n = %d). Mais escuro = prática mais rigorosa; cinza = ausente ou não relatado; contorno = só resumo, não avaliável." % n),
            fontsize=5.8, color=INK3, ha="left", va="center")
    fig.savefig(path, dpi=600)
    plt.close(fig)


def main():
    for p in (DESIGN, QUADAS, SELECTION, PROFILE):
        if not os.path.exists(p):
            sys.exit(f"EN/PT: missing | ausente: {p}")
    sel, des, qs = load()
    counts = tally(des, qs)
    check_against_profile(counts)
    os.makedirs(FIG_DIR, exist_ok=True)
    for lang in LANGS:
        plot(counts, len(sel), fig_path(FIG_DIR, STEM, lang), lang)
    print("EN/PT | Design profile | Perfil de desenho")
    for key, c in counts.items():
        print(f"  {key}: {dict(c)}")
    for lang in LANGS:
        print(f"EN/PT -> {fig_path(FIG_DIR, STEM, lang)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
