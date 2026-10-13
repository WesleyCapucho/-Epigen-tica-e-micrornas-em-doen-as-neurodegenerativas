#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EN | Robustness of the pooled AUCs as a specification chart. Every analysis that
     scripts/05 and scripts/26 ran on the same studies is one row: the dot is the pooled
     AUC and the whisker its interval, so the reader sees at once how little the headline
     number moves with the analytic choice. Panel B shows the panel-versus-single contrast
     under the primary and the marker-type-neutral selection rule.

     All values are read from the result tables (nothing is typed): meta_analysis_pooled_
     auc_primary.csv, meta_analysis_pooled_auc_sensitivity_every_estimate.csv,
     meta_analysis_variance_source_comparison.csv, robustness_alternative_analyses.csv,
     robustness_leave_one_out_by_disease.csv, robustness_random_selection.csv and
     post_search_sensitivity.csv.

     python scripts/33_robustness_specification_figure.py

PT | Robustez dos AUC agregados como grafico de especificacoes. Cada analise que o
     scripts/05 e o scripts/26 rodaram sobre os mesmos estudos e uma linha: o ponto e o
     AUC agregado e a haste, seu intervalo, de modo que o leitor ve de uma vez quanto o
     numero principal se move com a escolha analitica. O painel B mostra o contraste
     painel versus isolado sob a regra primaria e a regra neutra quanto ao tipo de marcador.

     Todos os valores sao lidos das tabelas de resultado (nada e digitado).
"""

import csv
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _bilingual import LANGS, t, fig_path
from _viz_style import DISEASE, AD_SOFT, PD_SOFT, INK, INK2, INK3, RULE, GRID, BAND, PAGE, panel_letter

T = "results/tables/"
FIG_DIR = "results/figures"
STEM = "robustness_specification"


def rd(name):
    return list(csv.DictReader(open(T + name, encoding="utf-8")))


def load():
    pooled = {r["subgroup"].split(" |")[0]: r for r in rd("meta_analysis_pooled_auc_primary.csv")}
    every = {r["subgroup"].split(" |")[0]: r for r in rd("meta_analysis_pooled_auc_sensitivity_every_estimate.csv")}
    var = rd("meta_analysis_variance_source_comparison.csv")
    alt = rd("robustness_alternative_analyses.csv")
    loo = rd("robustness_leave_one_out_by_disease.csv")
    rnd = {r["quantity"]: r for r in rd("robustness_random_selection.csv")}
    post = rd("post_search_sensitivity.csv")
    out = {}
    for dis in ("AD", "PD"):
        key = f"{dis} - all markers"
        p = pooled[key]
        rows = []
        rows.append(("primary", float(p["pooled_auc"]), float(p["ci_low_hk"]), float(p["ci_high_hk"]), p["n_studies"]))
        a = [r for r in alt if r["analysis"].startswith("marker-type-neutral") and r["outcome"] == f"{dis} - all markers"][0]
        rows.append(("neutral", float(a["pooled_auc"]), float(a["ci_low_hk"]), float(a["ci_high_hk"]), a["n_studies"]))
        a = [r for r in alt if r["analysis"].startswith("primary rule, reported CIs") and r["outcome"] == f"{dis} - all markers"][0]
        rows.append(("published", float(a["pooled_auc"]), float(a["ci_low_hk"]), float(a["ci_high_hk"]), a["n_studies"]))
        v = [r for r in var if r["subgroup"].startswith(dis) and "reported_only" in r["subgroup"]][0]
        rows.append(("reported_only", float(v["pooled_auc"]), float(v["ci_low_hk"]), float(v["ci_high_hk"]), v["n_studies"]))
        lo_ = [float(r["pooled_auc"]) for r in loo if r["disease"] == dis and not r["left_out"].startswith("none")]
        rows.append(("loo", None, min(lo_), max(lo_), str(len(lo_))))
        r = rnd[f"{dis}_auc"]
        rows.append(("random", float(r["median"]), float(r["p2_5"]), float(r["p97_5"]), r["draws_used"]))
        e = every[key]
        rows.append(("every", float(e["pooled_auc"]), float(e["ci_low"]), float(e["ci_high"]), e["n_studies"]))
        if dis == "AD":
            rows.append(("post_rt", float(post[1]["pooled_auc"]), float(post[1]["ci_low_hk"]), float(post[1]["ci_high_hk"]), post[1]["n_studies"]))
            rows.append(("post_orca", float(post[2]["pooled_auc"]), float(post[2]["ci_low_hk"]), float(post[2]["ci_high_hk"]), post[2]["n_studies"]))
        out[dis] = dict(rows=rows, loo=lo_, primary=float(p["pooled_auc"]),
                        pi=(float(p["pi_low"]), float(p["pi_high"])))
    # panel versus single
    pv = {}
    for dis in ("AD", "PD"):
        for rule, tag in (("primary rule (panel preferred), CI plausibility rule", "primary"), ("marker-type-neutral rule", "neutral")):
            sg = [r for r in alt if r["analysis"].startswith(rule) and r["outcome"] == f"{dis} - single markers"][0]
            pn = [r for r in alt if r["analysis"].startswith(rule) and r["outcome"] == f"{dis} - panels"][0]
            both = [r for r in alt if r["analysis"].startswith(rule) and r["outcome"] == f"{dis} - all markers"][0]
            pv[(dis, tag)] = dict(single=(float(sg["pooled_auc"]), float(sg["ci_low_hk"]), float(sg["ci_high_hk"]), sg["n_studies"]),
                                  panel=(float(pn["pooled_auc"]), float(pn["ci_low_hk"]), float(pn["ci_high_hk"]), pn["n_studies"]),
                                  p=float(both["panel_vs_single_p"]))
    return out, pv, rnd


LABELS = {
    "primary": ("Primary: one estimate per study", "Primária: uma estimativa por estudo"),
    "neutral": ("Marker-type-neutral selection", "Seleção neutra quanto ao tipo de marcador"),
    "published": ("Confidence intervals as published", "Intervalos de confiança como publicados"),
    "reported_only": ("Only studies with a reported interval", "Só estudos com intervalo reportado"),
    "loo": ("Leave one study out (each dot)", "Excluindo um estudo por vez (cada ponto)"),
    "random": ("2000 random accuracy-blind selections", "2000 seleções aleatórias cegas à acurácia"),
    "every": ("Every eligible estimate (ignores correlation)", "Toda estimativa elegível (ignora correlação)"),
    "post_rt": ("Plus search-update study, RT-qPCR", "Mais o estudo da atualização, RT-qPCR"),
    "post_orca": ("Plus search-update study, ORCA-Cas", "Mais o estudo da atualização, ORCA-Cas"),
}


def p_text(p):
    return "p < 0.0001" if p < 0.0001 else (f"p = {p:.3f}" if p < 0.01 else f"p = {p:.2f}")


def plot(data, pv, rnd, path, lang):
    fig = plt.figure(figsize=(7.4, 6.4))
    gs = fig.add_gridspec(1, 2, wspace=0.08, left=0.3, right=0.985, top=0.95, bottom=0.45)
    gsb = fig.add_gridspec(1, 1, left=0.3, right=0.66, top=0.34, bottom=0.07)
    nrows = {d: len(data[d]["rows"]) for d in data}
    ymax = max(nrows.values())
    for c, dis in enumerate(("AD", "PD")):
        ax = fig.add_subplot(gs[0, c])
        col = DISEASE[dis]
        soft = AD_SOFT if dis == "AD" else PD_SOFT
        d = data[dis]
        ax.axvspan(d["pi"][0], d["pi"][1], color=soft, alpha=0.55, lw=0, zorder=0)
        ax.axvline(d["primary"], color=col, lw=0.9, zorder=1)
        for i, (code, est, lo, hi, nstud) in enumerate(d["rows"]):
            y = ymax - 1 - i
            if i % 2 == 0:
                ax.axhspan(y - 0.5, y + 0.5, color=BAND, lw=0, zorder=0)
            if code == "loo":
                ax.plot([lo, hi], [y, y], color=col, lw=1.0, alpha=0.5, zorder=2)
                ax.scatter(d["loo"], [y] * len(d["loo"]), s=9, color=col, alpha=0.75, zorder=3, linewidths=0)
            elif code == "random":
                ax.plot([lo, hi], [y, y], color=col, lw=4.2, alpha=0.38, solid_capstyle="butt", zorder=2)
                ax.scatter([est], [y], s=24, color=col, zorder=3)
            else:
                ax.plot([lo, hi], [y, y], color=col, lw=1.3, zorder=2)
                ax.scatter([est], [y], s=34 if code == "primary" else 22, marker="D" if code == "primary" else "o",
                           facecolor=col if code != "every" else PAGE, edgecolor=col, linewidth=1.2, zorder=3)
            if c == 0:
                ax.text(-0.04, y, t(lang, *LABELS[code]), transform=ax.get_yaxis_transform(), ha="right", va="center",
                        fontsize=7.2, color=INK, fontweight="bold" if code == "primary" else "normal")
            nlab = f"{nstud} studies" if code not in ("random",) else f"{nstud} draws"
            if code == "loo":
                nlab = f"{est_fmt(lo)}–{est_fmt(hi)}"
            ax.text(1.13, y, f"{est_fmt(est)} [{est_fmt(lo)}–{est_fmt(hi)}]" if est is not None else nlab,
                    ha="right", va="center", fontsize=6.0, color=INK2)
        ax.set_xlim(0.55, 1.13)
        ax.spines['bottom'].set_bounds(0.55, 1.0)
        ax.set_ylim(-0.7, ymax - 0.3)
        ax.set_yticks([])
        ax.set_xticks([0.6, 0.7, 0.8, 0.9, 1.0])
        ax.spines["left"].set_visible(False)
        ax.set_title(t(lang, "Alzheimer's disease" if dis == "AD" else "Parkinson's disease",
                       "Doença de Alzheimer" if dis == "AD" else "Doença de Parkinson"), loc="left", fontsize=9, fontweight="bold", color=col)
        ax.set_xlabel(t(lang, "Pooled AUC", "AUC agregado"), fontsize=7.4)
        if c == 0:
            panel_letter(ax, "a", x=-0.62, y=1.06)
    # ---- B: panel versus single ----
    axb = fig.add_subplot(gsb[0, 0])
    axb.set_ylim(-0.7, 5.0)
    axb.set_xlim(0.5, 1.0)
    ys = {("PD", "primary"): 4.0, ("PD", "neutral"): 2.9, ("AD", "primary"): 1.1, ("AD", "neutral"): 0.0}
    for (dis, tag), y in ys.items():
        col = DISEASE[dis]
        r = pv[(dis, tag)]
        for kind, dy, filled in (("single", 0.2, False), ("panel", -0.2, True)):
            est, lo, hi, ns = r[kind]
            axb.plot([lo, hi], [y + dy, y + dy], color=col, lw=1.3, zorder=2)
            axb.scatter([est], [y + dy], s=30, marker="D" if filled else "s", facecolor=col if filled else PAGE,
                        edgecolor=col, linewidth=1.2, zorder=3)
            axb.annotate(f"{est_fmt(est)} ({ns})", xy=(1.03 if kind == "single" else 1.2, y + dy), xycoords=("axes fraction", "data"), va="center", fontsize=6.3, color=INK2, annotation_clip=False)
        axb.text(-0.005, y, t(lang, "Primary selection" if tag == "primary" else "Neutral selection",
                              "Seleção primária" if tag == "primary" else "Seleção neutra"),
                 transform=axb.get_yaxis_transform(), ha="right", va="center", fontsize=7.2, color=INK)
        axb.annotate(p_text(r["p"]), xy=(1.4, y), xycoords=("axes fraction", "data"), va="center", fontsize=6.8, color=INK2,
                     fontweight="bold" if r["p"] < 0.05 else "normal", annotation_clip=False)
    axb.text(-0.005, 4.75, t(lang, "Parkinson's disease", "Doença de Parkinson"), transform=axb.get_yaxis_transform(), ha="right", va="center", fontsize=7.6, fontweight="bold", color=DISEASE["PD"])
    axb.text(-0.005, 1.85, t(lang, "Alzheimer's disease", "Doença de Alzheimer"), transform=axb.get_yaxis_transform(), ha="right", va="center", fontsize=7.6, fontweight="bold", color=DISEASE["AD"])
    axb.axhline(2.35, color=GRID, lw=0.8)
    for xx, lab in ((1.03, t(lang, "single (n)", "isolado (n)")), (1.2, t(lang, "panel (n)", "painel (n)")), (1.4, t(lang, "panel vs single", "painel vs isolado"))):
        axb.annotate(lab, xy=(xx, 4.75), xycoords=("axes fraction", "data"), va="center", fontsize=6.3, color=INK3, annotation_clip=False)
    axb.set_yticks([])
    axb.spines["left"].set_visible(False)
    axb.set_xticks([0.5, 0.6, 0.7, 0.8, 0.9, 1.0])
    axb.set_xlabel(t(lang, "Pooled AUC (95% CI); square = single microRNA, diamond = panel; n studies in brackets",
                     "AUC agregado (IC 95%); quadrado = miRNA isolado, losango = painel; n de estudos entre parênteses"), fontsize=7.2)
    panel_letter(axb, "b", x=-0.62, y=1.02)
    fig.savefig(path, dpi=600, bbox_inches="tight")
    plt.close(fig)


def est_fmt(x):
    return f"{x:.2f}"


def main():
    for f in ("meta_analysis_pooled_auc_primary.csv", "robustness_random_selection.csv", "post_search_sensitivity.csv"):
        if not os.path.exists(T + f):
            sys.exit(f"EN/PT: missing | ausente: {T + f}")
    data, pv, rnd = load()
    os.makedirs(FIG_DIR, exist_ok=True)
    for lang in LANGS:
        plot(data, pv, rnd, fig_path(FIG_DIR, STEM, lang), lang)
    print("EN/PT | Robustness specification chart | Grafico de especificacoes de robustez")
    for dis, d in data.items():
        print(f"  {dis}: " + "; ".join(f"{c} {e if e is None else round(e, 3)}" for c, e, lo, hi, n in d["rows"]))
    for lang in LANGS:
        print(f"EN/PT -> {fig_path(FIG_DIR, STEM, lang)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
