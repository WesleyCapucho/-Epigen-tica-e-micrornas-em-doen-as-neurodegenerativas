#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EN | Forest plot of the PRIMARY analysis: one pre-specified, AUC-blind estimate per
     study, AD and PD in separate panels, each closed by its random-effects summary
     (Paule-Mandel tau-squared, modified Hartung-Knapp 95% CI) and its 95% prediction
     interval. Everything is read from files scripts/05_meta_analysis.py already wrote:
     the per-study selection (one_estimate_per_study_selection_audit.csv), the input
     estimates with their standard-error source (meta_analysis_input_estimates.csv) and
     the pooled rows (meta_analysis_pooled_auc_primary.csv).
PT | Forest plot da analise PRIMARIA: uma estimativa pre-especificada e cega a AUC por
     estudo, AD e PD em paineis separados, cada um fechado pelo seu resumo de efeitos
     aleatorios (tau-quadrado de Paule-Mandel, IC 95% de Hartung-Knapp modificado) e
     pelo seu intervalo de predicao de 95%. Tudo e lido de arquivos que
     scripts/05_meta_analysis.py ja gravou.

EN | Why this exists. forest_plot_auc shows every eligible row, which is the right
     picture for the every-row sensitivity analysis but not for the headline numbers,
     which come from one estimate per study. A reader comparing the main-text forest
     plot with Table 1 should see the same studies, the same weights and the same
     summary. The script stops if the summary it draws differs from the pooled CSV.
PT | Por que isto existe. forest_plot_auc mostra toda linha elegivel, o retrato certo
     para a analise de sensibilidade por linha, mas nao para os numeros principais, que
     vem de uma estimativa por estudo. O script para se o resumo desenhado divergir do
     CSV agregado.

    python scripts/28_primary_forest_plot.py
"""

import csv
import math
import os
import sys
import textwrap

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _bilingual import LANGS, t, fig_path

SELECTION = "results/tables/one_estimate_per_study_selection_audit.csv"
INPUTS = "results/tables/meta_analysis_input_estimates.csv"
POOLED = "results/tables/meta_analysis_pooled_auc_primary.csv"
FIG_DIR = "results/figures"
STEM = "forest_plot_primary"
PRIMARY_ROW = {"AD": "AD - all markers", "PD": "PD - all markers"}


def inv_logit(x):
    return 1.0 / (1.0 + math.exp(-x))


def load():
    sel = list(csv.DictReader(open(SELECTION, encoding="utf-8")))
    inp = list(csv.DictReader(open(INPUTS, encoding="utf-8")))
    pooled = list(csv.DictReader(open(POOLED, encoding="utf-8")))
    out = {}
    for dis, prefix in PRIMARY_ROW.items():
        prow = [p for p in pooled if p["subgroup"].startswith(prefix)
                and "reported_only" not in p["subgroup"] and "full (" not in p["subgroup"]]
        if len(prow) != 1:
            sys.exit(f"EN/PT: expected one primary row for {dis}, found {len(prow)}")
        prow = prow[0]
        tau2 = float(prow["tau2_PM"])
        studies = []
        for s in sel:
            if s["disease"] != dis:
                continue
            match = [r for r in inp if r["first_author"] == s["first_author"]
                     and str(int(float(r["year"]))) == str(int(float(s["year"])))
                     and r["marker"] == s["selected_marker"]
                     and abs(float(r["auc"]) - float(s["selected_auc"])) < 1e-9]
            if len(match) != 1:
                sys.exit(f"EN/PT: cannot match input row for {s['first_author']} {s['selected_marker']}")
            m = match[0]
            y, v = float(s["y"]), float(s["v"])
            studies.append(dict(author=s["first_author"], year=int(float(s["year"])),
                                marker=s["selected_marker"], biofluid=s["biofluid"],
                                n=(m["n_cases"], m["n_controls"]), se_source=m["se_source"],
                                y=y, v=v, w=1.0 / (v + tau2)))
        if len(studies) != int(prow["n_studies"]):
            sys.exit(f"EN/PT: {dis} selection has {len(studies)} studies, pooled row says {prow['n_studies']}")
        wsum = sum(s["w"] for s in studies)
        for s in studies:
            s["wpct"] = 100 * s["w"] / wsum
        # EN/PT: cross-check the point estimate against the pooled CSV | confere a estimativa com o CSV
        est = inv_logit(sum(s["w"] * s["y"] for s in studies) / wsum)
        if abs(est - float(prow["pooled_auc"])) > 0.0006:
            sys.exit(f"EN/PT: {dis} recomputed {est:.4f} differs from pooled CSV {prow['pooled_auc']}")
        out[dis] = (sorted(studies, key=lambda s: s["y"]), prow)
    return out


def plot(data, path, lang):
    fig, axes = plt.subplots(2, 1, figsize=(10.5, 9.2),
                             gridspec_kw={"height_ratios": [len(data["AD"][0]) + 3, len(data["PD"][0]) + 3]})
    colors = {"AD": "#3B6EA5", "PD": "#B3541E"}
    for ax, dis in zip(axes, ["AD", "PD"]):
        studies, prow = data[dis]
        n = len(studies)
        labels = []
        for i, s in enumerate(studies):
            yy = n - i + 1
            lo = inv_logit(s["y"] - 1.959964 * math.sqrt(s["v"]))
            hi = inv_logit(s["y"] + 1.959964 * math.sqrt(s["v"]))
            ax.plot([lo, hi], [yy, yy], color=colors[dis], lw=1.3)
            ax.scatter([inv_logit(s["y"])], [yy], s=18 + 6 * s["wpct"], marker="s", color=colors[dis], zorder=3)
            nn = f"{int(float(s['n'][0]))}/{int(float(s['n'][1]))}" if s["n"][0] and s["n"][1] else "n/r"
            src = (t(lang, "reported CI", "IC reportado") if s["se_source"] == "reported_95CI"
                   else "HM*" if "implausibly" in s["se_source"] else "HM")
            labels.append((yy, f"{s['author']} {s['year']}  {textwrap.shorten(s['marker'], 30, placeholder='...')}  ({s['biofluid']}, {nn}, {src})"))
            ax.text(1.005, yy, f"{inv_logit(s['y']):.2f} [{lo:.2f}, {hi:.2f}]  {s['wpct']:.1f}%",
                    va="center", fontsize=7.2, transform=ax.get_yaxis_transform())
        est, lo, hi = float(prow["pooled_auc"]), float(prow["ci_low_hk"]), float(prow["ci_high_hk"])
        pil, pih = float(prow["pi_low"]), float(prow["pi_high"])
        ax.plot([pil, pih], [0.2, 0.2], color="#555555", lw=1.0, ls="-")
        ax.fill([lo, est, hi, est], [0.2, 0.55, 0.2, -0.15], color="#222222", zorder=4)
        labels.append((0.2, t(lang,
                              f"Summary, {n} studies (mHK CI; line = 95% PI)  I² = {float(prow['I2_percent']):.1f}%",
                              f"Resumo, {n} estudos (IC mHK; linha = IP 95%)  I² = {float(prow['I2_percent']):.1f}%")))
        ax.text(1.005, 0.2, f"{est:.2f} [{lo:.2f}, {hi:.2f}]  PI [{pil:.2f}, {pih:.2f}]", va="center",
                fontsize=7.2, fontweight="bold", transform=ax.get_yaxis_transform())
        ax.set_yticks([p for p, _ in labels])
        ax.set_yticklabels([l for _, l in labels], fontsize=7.4)
        ax.tick_params(axis="y", length=0)
        ax.axvline(0.5, color="#999999", ls="--", lw=0.8)
        ax.axvline(est, color="#bbbbbb", ls=":", lw=0.8)
        ax.set_xlim(0.3, 1.0)
        ax.set_ylim(-0.6, n + 1.8)
        ax.set_title(t(lang, "Alzheimer's disease" if dis == "AD" else "Parkinson's disease",
                       "Doença de Alzheimer" if dis == "AD" else "Doença de Parkinson"),
                     loc="left", fontsize=10, color=colors[dis], fontweight="bold")
        for sp in ("top", "right", "left"):
            ax.spines[sp].set_visible(False)
    axes[-1].set_xlabel(t(lang, "AUC (95% CI); marker size proportional to random-effects weight. "
                          "HM = Hanley-McNeil SE; HM* = reported CI replaced as implausibly narrow",
                          "AUC (IC 95%); tamanho do marcador proporcional ao peso de efeitos aleatórios. "
                          "HM = EP de Hanley-McNeil; HM* = IC reportado substituído por ser implausivelmente estreito"),
                        fontsize=8.4)
    fig.tight_layout()
    fig.savefig(path, dpi=600, bbox_inches="tight")
    plt.close(fig)


def main():
    for p in (SELECTION, INPUTS, POOLED):
        if not os.path.exists(p):
            sys.exit(f"EN/PT: missing | ausente: {p}")
    data = load()
    os.makedirs(FIG_DIR, exist_ok=True)
    for lang in LANGS:
        plot(data, fig_path(FIG_DIR, STEM, lang), lang)
    print("EN/PT | Primary forest plot | Forest plot primario")
    for dis, (studies, prow) in data.items():
        print(f"  {dis}: {len(studies)} studies, pooled {float(prow['pooled_auc']):.3f}; "
              + ", ".join(f"{s['author']} {s['wpct']:.1f}%" for s in studies))
    for lang in LANGS:
        print(f"EN/PT -> {fig_path(FIG_DIR, STEM, lang)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
