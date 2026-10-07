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
from _viz_style import *  # noqa: F401,F403  (palette, ROB_*, helpers; applies the shared style)

SELECTION = "results/tables/one_estimate_per_study_selection_audit.csv"
INPUTS = "results/tables/meta_analysis_input_estimates.csv"
POOLED = "results/tables/meta_analysis_pooled_auc_primary.csv"
QUADAS = "results/tables/quadas2_assessment.csv"
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


def load_rob():
    """EN/PT: QUADAS-2 risk-of-bias judgement per study unit | julgamento QUADAS-2 por unidade de estudo."""
    rows = list(csv.DictReader(open(QUADAS, encoding="utf-8")))
    return {r["study_id"].lower(): r for r in rows}


ROB_COLS = [("rob_patient_selection", "PS"), ("rob_index_test", "IT"),
            ("rob_reference_standard", "RS"), ("rob_flow_timing", "FT")]
BIOFLUID = {"serum": "serum", "plasma": "plasma", "serum_exosome": "serum EV", "serum_neuronal_EV": "serum nEV",
            "plasma_EV": "plasma EV", "plasma_neuronal_EV": "plasma nEV", "blood": "blood", "plasma_sEV": "plasma sEV"}


def plot(data, path, lang):
    rob = load_rob()
    sel = {(s["first_author"], str(int(float(s["year"]))), s["disease"]): s
           for s in csv.DictReader(open(SELECTION, encoding="utf-8"))}
    nA, nP = len(data["AD"][0]), len(data["PD"][0])
    row_h = 0.19
    fig_h = row_h * (nA + nP + 8) + 1.1
    fig = plt.figure(figsize=(7.4, fig_h))
    outer = fig.add_gridspec(2, 1, height_ratios=[nA + 4, nP + 4], hspace=0.12,
                             left=0.015, right=0.985, top=1 - 0.4 / fig_h, bottom=1.0 / fig_h)
    for k, dis in enumerate(["AD", "PD"]):
        studies, prow = data[dis]
        n = len(studies)
        studies = sorted(studies, key=lambda s: -s["y"])
        col = DISEASE[dis]
        soft = AD_SOFT if dis == "AD" else PD_SOFT
        g = outer[k].subgridspec(1, 4, width_ratios=[2.9, 2.6, 1.95, 1.0], wspace=0.015)
        axl, axf, axv, axr = (fig.add_subplot(g[0, i]) for i in range(4))
        ytop = n + 3.2
        for ax in (axl, axf, axv, axr):
            ax.set_ylim(-1.9, ytop)
        for ax in (axl, axv, axr):
            ax.axis("off")
        axl.set_xlim(0, 1); axv.set_xlim(0, 1); axr.set_xlim(0, 4)
        # EN/PT: header row | linha de cabecalho
        yh = n + 1.9
        axl.text(0.0, yh, t(lang, "Study", "Estudo"), fontsize=7.5, fontweight="bold", va="center")
        axl.text(0.5, yh, t(lang, "Selected estimate", "Estimativa selecionada"), fontsize=7.5, fontweight="bold", va="center")
        axv.text(0.0, yh, "AUC [95% CI]", fontsize=7, fontweight="bold", va="center")
        axv.text(0.66, yh, t(lang, "n case/ctrl", "n caso/ctrl"), fontsize=6.0, fontweight="bold", va="center", ha="center")
        axv.text(1.0, yh, t(lang, "Wt %", "Peso %"), fontsize=6.6, fontweight="bold", va="center", ha="right")
        for j, (_c, ab) in enumerate(ROB_COLS):
            axr.text(j + 0.5, yh, ab, fontsize=7.2, fontweight="bold", ha="center", va="center", color=INK2)
        axl.text(0.0, ytop - 0.15, t(lang, "Alzheimer's disease" if dis == "AD" else "Parkinson's disease",
                                     "Doença de Alzheimer" if dis == "AD" else "Doença de Parkinson"),
                 fontsize=10, fontweight="bold", color=col, va="center")
        # EN/PT: prediction band and pooled line behind the studies | faixa de predicao e linha agregada atras dos estudos
        est, lo, hi = float(prow["pooled_auc"]), float(prow["ci_low_hk"]), float(prow["ci_high_hk"])
        pil, pih = float(prow["pi_low"]), float(prow["pi_high"])
        axf.axvspan(pil, pih, ymin=0.0, ymax=1.0, color=soft, alpha=0.55, lw=0, zorder=0)
        axf.axvline(est, color=col, lw=0.9, zorder=1)
        axf.axvline(0.5, color=INK3, lw=0.7, ls=(0, (3, 3)), zorder=1)
        for i, s in enumerate(studies):
            yy = n - i
            lo_i = inv_logit(s["y"] - 1.959964 * math.sqrt(s["v"]))
            hi_i = inv_logit(s["y"] + 1.959964 * math.sqrt(s["v"]))
            auc = inv_logit(s["y"])
            sr = s["se_source"]
            ls = "-" if sr == "reported_95CI" else (0, (1, 1.2)) if "implausibly" in sr else (0, (4, 1.6))
            axf.plot([lo_i, hi_i], [yy, yy], color=col, lw=1.15, ls=ls, solid_capstyle="butt", zorder=2)
            srow = sel[(s["author"], str(s["year"]), dis)]
            panel = srow["selected_marker_type"] == "multi_miRNA_panel"
            axf.scatter([auc], [yy], s=16 + 5.2 * s["wpct"], marker="D" if panel else "s",
                        facecolor=col if panel else PAGE, edgecolor=col, linewidth=1.2, zorder=3)
            if i % 2 == 0:
                for ax in (axl, axv, axr):
                    ax.axhspan(yy - 0.5, yy + 0.5, color=BAND, lw=0, zorder=0)
                axf.axhspan(yy - 0.5, yy + 0.5, color=BAND, alpha=0.5, lw=0, zorder=0.5)
            axl.text(0.0, yy, f"{s['author']} {s['year']}", fontsize=7.2, va="center", color=INK)
            axl.text(0.5, yy, textwrap.shorten(s["marker"], 29, placeholder="…"), fontsize=6.3, va="center", color=INK2, clip_on=True)
            nn = f"{int(float(s['n'][0]))}/{int(float(s['n'][1]))}" if s["n"][0] and s["n"][1] else "n/r"
            star = "*" if "implausibly" in sr else ""
            axv.text(0.0, yy, f"{auc:.2f} [{lo_i:.2f}, {hi_i:.2f}]{star}", fontsize=6.6, va="center")
            axv.text(0.66, yy, nn, fontsize=6.3, va="center", ha="center", color=INK2)
            axv.text(1.0, yy, f"{s['wpct']:.1f}", fontsize=6.6, va="center", ha="right", color=INK2)
            q = rob.get(srow["study_id"].lower())
            for j, (c, _ab) in enumerate(ROB_COLS):
                v = q[c] if q else "unclear"
                rounded(axr, j + 0.1, yy - 0.36, 0.8, 0.72, ROB_FILL[v], r=0.14)
                axr.text(j + 0.5, yy, ROB_LETTER[v], fontsize=5.8, fontweight="bold", ha="center", va="center", color=ROB_TEXT[v])
        # EN/PT: summary row | linha de resumo
        ys = -1.0
        axf.plot([pil, pih], [ys, ys], color=INK, lw=1.0, zorder=3)
        axf.fill([lo, est, hi, est], [ys, ys + 0.5, ys, ys - 0.5], color=col, zorder=4, ec=INK, lw=0.6)
        axf.axhline(0.0, color=RULE, lw=0.7, zorder=1)
        axl.text(0.0, ys, t(lang, f"Pooled, {n} studies", f"Agregado, {n} estudos"), fontsize=7.4, fontweight="bold", va="center")
        axl.text(0.0, ys - 0.85, f"I² = {float(prow['I2_percent']):.1f}%", fontsize=6.6, va="center", color=INK2)
        axv.text(0.0, ys, f"{est:.2f} [{lo:.2f}, {hi:.2f}]", fontsize=7.2, fontweight="bold", va="center")
        axv.text(0.0, ys - 0.85, f"PI [{pil:.2f}, {pih:.2f}]", fontsize=6.6, va="center", color=INK2)
        axf.set_xlim(0.3, 1.0)
        axf.set_yticks([])
        axf.set_xticks([0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0])
        axf.tick_params(axis="x", length=2.5, labelsize=7)
        for sp in ("top", "right", "left"):
            axf.spines[sp].set_visible(False)
        if k == 1:
            axf.set_xlabel("AUC", fontsize=8)
        else:
            axf.set_xlabel("")
    # EN/PT: key | legenda
    items = [
        (t(lang, "Single microRNA", "miRNA isolado"), dict(marker="s", mfc=PAGE, mec=INK2, ls="none", ms=5.5)),
        (t(lang, "Panel", "Painel"), dict(marker="D", mfc=INK2, mec=INK2, ls="none", ms=5.2)),
        (t(lang, "Reported CI", "IC reportado"), dict(marker=None, color=INK2, ls="-", lw=1.2)),
        (t(lang, "CI reconstructed (Hanley-McNeil)", "IC reconstruído (Hanley-McNeil)"), dict(marker=None, color=INK2, ls=(0, (4, 1.6)), lw=1.2)),
        (t(lang, "* reported CI replaced as implausibly narrow", "* IC reportado substituído por implausivelmente estreito"), dict(marker=None, color=INK2, ls=(0, (1, 1.2)), lw=1.2)),
    ]
    handles = [matplotlib.lines.Line2D([], [], **kw) for _lab, kw in items]
    fig.legend(handles, [lab for lab, _ in items], loc="lower left", bbox_to_anchor=(0.0, 0.0), ncol=3,
               frameon=False, fontsize=6.6, handlelength=2.2, columnspacing=1.2)
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
