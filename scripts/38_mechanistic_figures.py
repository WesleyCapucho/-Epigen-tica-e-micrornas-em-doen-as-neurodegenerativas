#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EN | The five main-text figures of the mechanistic study (Article 2), drawn in the shared
     style of scripts/_viz_style.py and fitted to the journal's artwork limits by
     scripts/_journal_fit.py. Every number on a figure is read from the result tables of
     scripts/12, 17 and 36 and from the kinetic parameter table at draw time, or follows
     from a closed form written next to the line it draws; nothing is typed in as a
     result. The one simulation, the time course of Fig. 5a, re-runs the cascade of
     scripts/36 at the dose that the scenario table of that script reports.

         mech_model_schematic   Fig. 1  the two cascades and the constants they use
         mech_alzheimer         Fig. 2  clearance, required knockdown, nucleation scaling
         mech_parkinson         Fig. 3  saturation, transmission, mimic factor against rho
         mech_turnover          Fig. 4  washout, peak to average, stabilisation needed
         mech_target_response   Fig. 5  what a repeated dose does at the protein

PT | As cinco figuras do texto principal do estudo mecanistico (Artigo 2), no estilo
     compartilhado do scripts/_viz_style.py e ajustadas aos limites de arte do periodico
     pelo scripts/_journal_fit.py. Todo numero numa figura e lido, na hora de desenhar, das
     tabelas de resultado dos scripts 12, 17 e 36 e da tabela de parametros cineticos, ou
     decorre de uma forma fechada escrita ao lado da linha que desenha; nada e digitado
     como resultado. A unica simulacao, a curva no tempo da Fig. 5a, roda de novo a cascata
     do scripts/36 na dose que a tabela de cenarios daquele script reporta.

    python scripts/38_mechanistic_figures.py
"""

import csv
import importlib.util
import json
import math
import os
import sys
from collections import OrderedDict

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch
from scipy.integrate import solve_ivp

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _viz_style as vs
from _bilingual import LANGS, t as tr, fig_path

HERE = os.path.dirname(os.path.abspath(__file__))
FIG = "results/figures"
TAB = "results/tables"
KIN = "data/extracted/kinetic_parameters.csv"
LN2 = math.log(2.0)
MM = 1.0 / 25.4

SP_COLOUR = {   # EN/PT: species -> (colour, line style, label EN, label PT)
    "miR-7": (vs.PD, "-", "miR-7 (1.7 h)", "miR-7 (1,7 h)"),
    "miR-7 upper bound": (vs.PD, "--", "miR-7, upper bound (5 h)", "miR-7, limite superior (5 h)"),
    "miR-29b": (vs.AD, "-", "miR-29b (7 h)", "miR-29b (7 h)"),
    "miR-29c": (vs.AD, "--", "miR-29c (10.6 h)", "miR-29c (10,6 h)"),
    "median miRNA": (vs.INK2, "-", "median miRNA (34 h)", "miRNA mediano (34 h)"),
}


def load_module(name, filename):
    path = os.path.join(HERE, filename)
    if not os.path.exists(path):
        sys.exit(f"EN/PT: missing {path}")
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def read_inputs():
    for f in (f"{TAB}/ode_calibrated_results.json", f"{TAB}/mimic_dosing_feasibility.json",
              f"{TAB}/mimic_target_response.json", f"{TAB}/mimic_target_response.csv",
              f"{TAB}/mimic_target_rho_sweep.csv", KIN):
        if not os.path.exists(f):
            sys.exit(f"EN/PT: missing {f}; run scripts/12, 17 and 36 first")
    d = OrderedDict()
    d["kin"] = {r["param_id"]: r for r in csv.DictReader(open(KIN, encoding="utf-8"))}
    d["ode"] = json.load(open(f"{TAB}/ode_calibrated_results.json", encoding="utf-8"))
    d["dos"] = json.load(open(f"{TAB}/mimic_dosing_feasibility.json", encoding="utf-8"))
    d["tgt"] = json.load(open(f"{TAB}/mimic_target_response.json", encoding="utf-8"))
    d["rows"] = list(csv.DictReader(open(f"{TAB}/mimic_target_response.csv", encoding="utf-8")))
    d["sweep"] = list(csv.DictReader(open(f"{TAB}/mimic_target_rho_sweep.csv", encoding="utf-8")))
    return d


def kv(d, pid):
    return float(d["kin"][pid]["value_si"])


def label_panel(ax, letter, x=-0.15, y=1.08):
    """EN/PT: bold panel letter above and left of the axes, clear of the title | letra do painel fora do titulo."""
    vs.panel_letter(ax, letter, x=x, y=y, size=10)


def style_axes(ax, grid=True):
    ax.spines[["top", "right"]].set_visible(False)
    if grid:
        ax.grid(True, color=vs.GRID, lw=0.5)
        ax.set_axisbelow(True)


def fold_for(kappa, rho):
    """EN/PT: mimic factor that a knockdown kappa requires at strength rho | fator de mimetico."""
    return 1.0 + kappa / (1.0 - kappa) * (1.0 + rho) / rho


def knockdown_at(f, rho):
    """EN/PT: knockdown produced by a mimic factor f at strength rho | queda produzida."""
    return 1.0 - (1.0 + rho) / (1.0 + rho * f)


# ----------------------------------------------------------------------------- Fig. 2
def fig_alzheimer(d, lang):
    ode, tgt = d["ode"], d["tgt"]
    clr = ode["ad_clearance_vs_production"]
    dose = ode["mimic_dose_vs_measured_knockdown"]
    kappa = dose["required_BACE1_knockdown"]
    measured = dose["measured_BACE1_knockdown_K047"]
    rs = tgt["repression_strength"]["AD"]
    nuc = tgt["nucleation_scaling"]

    fig = plt.figure(figsize=(174 * MM, 62 * MM))
    gs = fig.add_gridspec(1, 3, width_ratios=[1.15, 1.2, 1.25], wspace=0.55, left=0.065, right=0.99,
                          top=0.87, bottom=0.2)

    # (a) factors of the pool ratio, logarithmic
    ax = fig.add_subplot(gs[0])
    f_prod = kv(d, "K002") / kv(d, "K001")
    f_clear = kv(d, "K003") / kv(d, "K004")
    ratio = clr["abeta_ratio_AD_over_control"]
    names = [tr(lang, "Production", "Produção"), tr(lang, "Clearance", "Depuração"),
             tr(lang, "Pool", "Pool")]
    vals = [f_prod, f_clear, ratio]
    cols = [vs.INK3, vs.AD, vs.TIER_RAMP[1]]
    ax.bar(range(3), [v - 1 for v in vals], bottom=1.0, color=cols, width=0.62)
    ax.axhline(1.0, color=vs.INK2, lw=0.8)
    for i, v in enumerate(vals):
        ax.text(i, v + (0.03 if v >= 1 else -0.03), f"{v:.3f}", ha="center",
                va="bottom" if v >= 1 else "top", fontsize=7.5, color=vs.INK)
    ax.set_yscale("log")
    ax.set_ylim(0.85, 1.9)
    ax.set_yticks([0.9, 1.0, 1.2, 1.5])
    ax.set_yticklabels(["0.9", "1.0", "1.2", "1.5"])
    ax.set_xticks(range(3))
    ax.set_xticklabels(names, fontsize=6.6)
    ax.set_ylabel(tr(lang, "AD relative to control", "DA em relação ao controle"))
    ax.set_title(tr(lang, "Aβ42 pool", "Pool de Aβ42"), fontsize=8, loc="left")
    style_axes(ax)
    label_panel(ax, "a")

    # (b) knockdown against mimic factor
    ax = fig.add_subplot(gs[1])
    f = np.linspace(1.0, 3.2, 300)
    for rho, lw, ls, lab in ((rs["rho_scan_high"], 1.6, "-", tr(lang, "ρ = {:.0f} (scan, strong)", "ρ = {:.0f} (varredura, forte)")),
                             (rs["rho_scan_mid"], 1.2, "-", tr(lang, "ρ = {:.0f} (midpoint)", "ρ = {:.0f} (ponto médio)")),
                             (rs["rho_scan_low"], 1.2, "--", tr(lang, "ρ = {:.1f} (scan, weak)", "ρ = {:.1f} (varredura, fraca)")),
                             (1.0, 1.2, ":", tr(lang, "ρ = {:.0f}", "ρ = {:.0f}"))):
        ax.plot(f, 100 * knockdown_at(f, rho), color=vs.AD, lw=lw, ls=ls, label=lab.format(rho))
    ax.axhline(100 * kappa, color=vs.TIER_RAMP[1], lw=1.0)
    ax.axhline(100 * measured, color=vs.INK2, lw=1.0, ls="--")
    ax.text(3.17, 100 * kappa + 1.5, tr(lang, f"required {100 * kappa:.1f}%", f"exigida {100 * kappa:.1f}%"),
            ha="right", va="bottom", fontsize=7.2, color=vs.TIER_RAMP[1])
    ax.text(1.04, 100 * measured + 1.5, tr(lang, f"measured in\ncells ≈{100 * measured:.0f}%", f"medida em\ncélulas ≈{100 * measured:.0f}%"),
            ha="left", va="bottom", fontsize=7.2, color=vs.INK2, linespacing=1.1)
    ax.set_xlim(1.0, 3.2)
    ax.set_ylim(0, 70)
    ax.set_xlabel(tr(lang, "miR-29 pool, multiple of baseline", "Pool de miR-29, múltiplo do basal"))
    ax.set_ylabel(tr(lang, "BACE1 knockdown (%)", "Queda de BACE1 (%)"))
    ax.set_title(tr(lang, "Mimic needed for the required fall", "Mimético para a queda exigida"), fontsize=8, loc="left")
    ax.legend(frameon=False, fontsize=6.8, loc="lower right", handlelength=1.8, borderaxespad=0.2)
    style_axes(ax)
    label_panel(ax, "b")

    # (c) rate ratios, from the measured reaction orders
    ax = fig.add_subplot(gs[2])
    n_ = nuc["order_secondary_nucleation"]
    items = [(tr(lang, "Monomer\npool", "Pool de\nmonômero"), ratio, "1"),
             (tr(lang, "Elongation", "Alongamento"), nuc["elongation_rate_ratio_AD_over_control"], "1"),
             (tr(lang, "Nucleation", "Nucleação"), nuc["secondary_nucleation_rate_ratio_AD_over_control"], f"{n_:.0f}")]
    ax.bar(range(3), [v - 1 for _, v, _ in items], bottom=1.0, color=[vs.TIER_RAMP[1], vs.AD, vs.AD], width=0.62)
    ax.axhline(1.0, color=vs.INK2, lw=0.8)
    for i, (_, v, order) in enumerate(items):
        ax.text(i, v + 0.04, f"{v:.2f}", ha="center", va="bottom", fontsize=7.5, color=vs.INK)
        ax.text(i, 1.0 - 0.06, tr(lang, f"order {order}", f"ordem {order}") if i else "", ha="center", va="top",
                fontsize=6.8, color=vs.INK2)
    ax.set_xticks(range(3))
    ax.set_xticklabels([x[0] for x in items], fontsize=6.6)
    ax.set_ylim(0.8, 2.3)
    ax.set_ylabel(tr(lang, "AD relative to control", "DA em relação ao controle"))
    ax.set_title(tr(lang, "Rates at the same pool", "Taxas no mesmo pool"), fontsize=8, loc="left")
    style_axes(ax)
    label_panel(ax, "c")

    fig.savefig(fig_path(FIG, "mech_alzheimer", lang), dpi=300, bbox_inches="tight")
    plt.close(fig)


# ----------------------------------------------------------------------------- Fig. 3
def fig_parkinson(d, lang):
    ode, tgt = d["ode"], d["tgt"]
    sat = ode["alpha_synuclein_saturation"]
    chain = ode["mir7_knockdown_to_elongation"]
    rs = tgt["repression_strength"]
    C0 = sat["alpha_synuclein_uM_in_bouton"]
    mhs = sorted(p["m_half_uM"] for p in sat["points"])
    kd_a, kd_b = kv(d, "K058"), kv(d, "K063")

    fig = plt.figure(figsize=(174 * MM, 66 * MM))
    gs = fig.add_gridspec(1, 3, width_ratios=[1.15, 1.0, 1.25], wspace=0.5, left=0.06, right=0.99,
                          top=0.88, bottom=0.2)

    # (a) saturation curve
    ax = fig.add_subplot(gs[0])
    S = np.linspace(0, 120, 400)
    cols = (vs.PD, "#c04a1c")
    for mh, c in zip(mhs, cols):
        ax.plot(S, S / (mh + S), color=c, lw=1.4, label=f"m½ {mh:.1f} µM")
        for kd, mk in ((kd_a, "o"), (kd_b, "s")):
            s1 = C0 * (1 - kd)
            ax.plot([s1], [s1 / (mh + s1)], mk, ms=4.2, color=c, mec="white", mew=0.5, zorder=4)
    ax.axvline(C0, color=vs.INK2, lw=0.9, ls="--")
    ax.text(C0 + 2, 0.76, tr(lang, f"{C0:.1f} µM in a bouton", f"{C0:.1f} µM em um botão"), fontsize=7, color=vs.INK2,
            va="top", ha="left")
    for kd, y_txt in ((kd_a, 0.20), (kd_b, 0.115)):
        s1 = C0 * (1 - kd)
        ax.annotate(f"−{100 * kd:.0f}%", (s1, s1 / (mhs[-1] + s1)), xytext=(27, y_txt), fontsize=6.6, color=vs.INK2,
                    ha="left", va="center",
                    arrowprops=dict(arrowstyle="-", color=vs.INK3, lw=0.6, shrinkA=1, shrinkB=2))
    ax.set_xlim(0, 120)
    ax.set_ylim(0, 0.8)
    ax.set_xlabel(tr(lang, "α-synuclein monomer (µM)", "Monômero de α-sinucleína (µM)"))
    ax.set_ylabel(tr(lang, "Elongation rate, fraction of maximum", "Taxa de alongamento, fração do máximo"))
    ax.legend(frameon=False, fontsize=6.8, loc="lower right", handlelength=1.6)
    ax.set_title(tr(lang, "Where the protein sits", "Onde a proteína está"), fontsize=8, loc="left")
    style_axes(ax)
    label_panel(ax, "a")

    # (b) transmission
    ax = fig.add_subplot(gs[1])
    x = np.linspace(0, 0.6, 200)
    ax.plot(100 * x, 100 * x, color=vs.INK3, lw=0.9, ls="--")
    ax.text(57, 59, tr(lang, "proportional", "proporcional"), ha="right", va="bottom", fontsize=7, color=vs.INK3, rotation=0)
    lo_curve = [1 - ((C0 * (1 - k)) / (mhs[0] + C0 * (1 - k))) / (C0 / (mhs[0] + C0)) for k in x]
    hi_curve = [1 - ((C0 * (1 - k)) / (mhs[-1] + C0 * (1 - k))) / (C0 / (mhs[-1] + C0)) for k in x]
    ax.fill_between(100 * x, 100 * np.array(lo_curve), 100 * np.array(hi_curve), color=vs.PD, alpha=0.35, lw=0)
    ax.plot(100 * x, 100 * np.array(hi_curve), color=vs.PD, lw=1.3)
    for lab, kd in (("a", kd_a), ("b", kd_b)):
        cs = [c["elongation_rate_reduction"] for c in chain["cases"] if abs(c["knockdown"] - kd) < 1e-12]
        ax.plot([100 * kd] * 2, [100 * min(cs)] * 2, "o", color=vs.PD, ms=4, mec="white", mew=0.5, zorder=4)
        ax.annotate(f"{100 * min(cs):.1f}–{100 * max(cs):.1f}%", (100 * kd, 100 * min(cs)),
                    xytext=(100 * kd + 3, 100 * min(cs) - 7), fontsize=7, color=vs.INK,
                    arrowprops=dict(arrowstyle="-", color=vs.INK3, lw=0.6))
    ax.set_xlim(0, 60)
    ax.set_ylim(0, 62)
    ax.set_xlabel(tr(lang, "Fall in α-synuclein (%)", "Queda de α-sinucleína (%)"))
    ax.set_ylabel(tr(lang, "Fall in elongation rate (%)", "Queda da taxa de alongamento (%)"))
    ax.set_title(tr(lang, "Less than proportional", "Menos que proporcional"), fontsize=8, loc="left")
    style_axes(ax)
    label_panel(ax, "b")

    # (c) mimic factor against rho, both axes
    ax = fig.add_subplot(gs[2])
    rho = np.geomspace(0.01, 1000, 400)
    pd_ = rs["PD"]
    ad_ = rs["AD"]
    kappa_ad = d["ode"]["mimic_dose_vs_measured_knockdown"]["required_BACE1_knockdown"]
    ax.axvspan(pd_["rho_scan_low"], pd_["rho_scan_high"], color=vs.PD_SOFT, alpha=0.7, lw=0)
    ax.axvspan(ad_["rho_scan_low"], ad_["rho_scan_high"], color=vs.AD_SOFT, alpha=0.7, lw=0)
    ax.plot(rho, fold_for(kd_a, rho), color=vs.PD, lw=1.4, label=tr(lang, f"PD, {100 * kd_a:.0f}%", f"DP, {100 * kd_a:.0f}%"))
    ax.plot(rho, fold_for(kd_b, rho), color=vs.PD, lw=1.4, ls="--", label=tr(lang, f"PD, {100 * kd_b:.0f}%", f"DP, {100 * kd_b:.0f}%"))
    ax.plot(rho, fold_for(kappa_ad, rho), color=vs.AD, lw=1.4, label=tr(lang, f"AD, {100 * kappa_ad:.1f}%", f"DA, {100 * kappa_ad:.1f}%"))
    for kap, c in ((kd_a, vs.PD), (kd_b, vs.PD), (kappa_ad, vs.AD)):
        ax.axhline(1.0 / (1.0 - kap), color=c, lw=0.6, ls=":")
    ax.axvline(pd_["rho_floor_K065"], color=vs.INK2, lw=0.9, ls=":")
    ax.text(pd_["rho_floor_K065"] * 0.9, 70, tr(lang, "floor from K065", "piso do K065"), ha="right", va="top", fontsize=6.8, color=vs.INK2, rotation=90)
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlim(0.01, 1000)
    ax.set_ylim(1.0, 100)
    ax.set_yticks([1, 2, 5, 10, 20, 50, 100])
    ax.set_yticklabels(["1", "2", "5", "10", "20", "50", "100"])
    ax.set_xlabel(tr(lang, "ρ, share of mRNA decay held by the microRNA", "ρ, parcela do decaimento do mRNA com o microRNA"))
    ax.set_ylabel(tr(lang, "Mimic factor required", "Fator de mimético exigido"))
    ax.legend(frameon=False, fontsize=6.8, loc="upper right", handlelength=1.8, ncol=1, borderaxespad=0.3)
    ax.set_title(tr(lang, "How much mimic, by repression strength", "Quanto mimético, por força de repressão"), fontsize=8, loc="left")
    style_axes(ax)
    label_panel(ax, "c")

    fig.savefig(fig_path(FIG, "mech_parkinson", lang), dpi=300, bbox_inches="tight")
    plt.close(fig)


# ----------------------------------------------------------------------------- Fig. 4
def fig_turnover(d, lang):
    dos = d["dos"]
    dec = dos["decay_constants"]
    dd = dos["daily_dosing_comparison"]
    order = ["miR-7", "miR-7 upper bound", "miR-29b", "miR-29c", "median miRNA"]

    fig = plt.figure(figsize=(174 * MM, 62 * MM))
    gs = fig.add_gridspec(1, 3, width_ratios=[1.1, 1.1, 0.8], wspace=0.46, left=0.065, right=0.985, top=0.87, bottom=0.2)

    ax = fig.add_subplot(gs[0])
    t = np.linspace(0, 120, 400)
    for sp in order:
        c, ls, en, pt = SP_COLOUR[sp]
        ax.plot(t, 1 + 9 * np.exp(-dec[sp]["decay_per_hour"] * t), color=c, ls=ls, lw=1.3, label=tr(lang, en, pt))
    ax.axhline(1.1, color=vs.INK3, lw=0.8, ls="--")
    ax.set_yscale("log")
    ax.set_ylim(1.0, 11)
    ax.set_yticks([1, 2, 5, 10])
    ax.set_yticklabels(["1", "2", "5", "10"])
    ax.set_xlim(0, 120)
    ax.set_xlabel(tr(lang, "Time after a 10-fold bolus (h)", "Tempo após um bolus de 10x (h)"))
    ax.set_ylabel(tr(lang, "Level, multiple of baseline", "Nível, múltiplo do basal"))
    ax.set_title(tr(lang, "Washout", "Eliminação"), fontsize=8, loc="left")
    style_axes(ax)
    label_panel(ax, "a")

    ax = fig.add_subplot(gs[1])
    T = np.geomspace(0.5, 72, 300)
    for sp in order:
        c, ls, en, pt = SP_COLOUR[sp]
        x = dec[sp]["decay_per_hour"] * T
        ax.plot(T, x / (1 - np.exp(-x)), color=c, ls=ls, lw=1.3, label=tr(lang, en, pt))
    ax.axvline(24, color=vs.INK3, lw=0.8, ls="--")
    ax.legend(frameon=False, fontsize=6.2, loc="upper left", handlelength=1.4, borderaxespad=0.12, labelspacing=0.3)
    ax.annotate(tr(lang, "daily", "diário"), xy=(24, 1.0), xycoords=("data", "axes fraction"), xytext=(0, 1.5),
                textcoords="offset points", ha="center", va="bottom", fontsize=7, color=vs.INK3)
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlim(0.5, 72)
    ax.set_ylim(1, 40)
    ax.set_xticks([1, 2, 4, 8, 24, 48])
    ax.set_xticklabels(["1", "2", "4", "8", "24", "48"])
    ax.set_yticks([1, 2, 5, 10, 20])
    ax.set_yticklabels(["1", "2", "5", "10", "20"])
    ax.set_xlabel(tr(lang, "Dosing interval (h)", "Intervalo entre doses (h)"))
    ax.set_ylabel(tr(lang, "Peak / average", "Pico / média"))
    ax.set_title(tr(lang, "Cost of instability", "Custo da instabilidade"), fontsize=8, loc="left")
    style_axes(ax)
    label_panel(ax, "b")

    ax = fig.add_subplot(gs[2])
    sps = ["miR-7", "miR-7 upper bound", "miR-29b", "miR-29c"]
    vals = [dd[s]["fold_stabilisation_required"] for s in sps]
    cols = [SP_COLOUR[s][0] for s in sps]
    y = np.arange(len(sps))
    bars = ax.barh(y, vals, color=cols, height=0.6)
    for b, s in zip(bars, sps):
        if SP_COLOUR[s][1] == "--":
            b.set_alpha(0.6)
    for yi, v in zip(y, vals):
        ax.text(v + 0.4, yi, f"{v:.1f}×", va="center", fontsize=7.5, color=vs.INK)
    ax.set_yticks(y)
    short = {"miR-7": "miR-7", "miR-7 upper bound": tr(lang, "miR-7 (5 h)", "miR-7 (5 h)"),
             "miR-29b": "miR-29b", "miR-29c": "miR-29c"}
    ax.set_yticklabels([short[s_] for s_ in sps], fontsize=7)
    ax.invert_yaxis()
    ax.set_xlim(0, 24)
    ax.set_xlabel(tr(lang, "Fold increase in half-life", "Aumento da meia-vida (vezes)"))
    ax.set_title(tr(lang, "Stabilisation for daily dosing", "Estabilização para dose diária"), fontsize=8, loc="left")
    style_axes(ax, grid=False)
    label_panel(ax, "c")

    fig.savefig(fig_path(FIG, "mech_turnover", lang), dpi=300, bbox_inches="tight")
    plt.close(fig)


# ----------------------------------------------------------------------------- Fig. 5
def trajectory(cas, dose, T, dx, cycles=2, per=240):
    """EN/PT: E, mu, pi over `cycles` periodic cycles of repeated dosing | E, mu, pi ao longo de ciclos periodicos."""
    e_peak = dose / (1.0 - math.exp(-dx * T))
    x0 = list(cas.periodic_state(e_peak, T))
    ts, ys = [], []
    for c in range(cycles):
        sol = solve_ivp(cas.rhs, (0.0, T), [e_peak] + x0 + [0.0] * cas.n_int, method="LSODA",
                        rtol=1e-10, atol=1e-13, t_eval=np.linspace(0.0, T, per))
        ts.append(sol.t + c * T)
        ys.append(sol.y[:3 + cas.L])
        x0 = list(sol.y[1:1 + cas.n_lin, -1])
    return np.concatenate(ts), np.concatenate(ys, axis=1)


def fig_target(d, lang, t36):
    rows, sweep = d["rows"], d["sweep"]
    meas, table = t36.load_module("ode12", "12_ode_models_calibrated.py").load_measured()
    tgt = d["tgt"]
    kap_a = kv(d, "K058")
    T24 = 24.0
    mid = tgt["repression_strength"]["PD"]["rho_scan_mid"]

    def row(axis, rho_case, sp, T, kap, prot=("BACE1 in", "alpha-syn")):
        out = [r for r in rows if r["axis"] == axis and r["rho_case"] == rho_case and r["species"] == sp
               and float(r["interval_h"]) == T and abs(float(r["target_knockdown"]) - kap) < 1e-9
               and r["protein_case"].startswith(prot)]
        if len(out) != 1:
            sys.exit(f"EN/PT: expected one scenario for {axis}/{rho_case}/{sp}/{T}, found {len(out)}")
        return out[0]

    fig = plt.figure(figsize=(174 * MM, 140 * MM))
    outer = fig.add_gridspec(2, 2, wspace=0.34, hspace=0.42, left=0.075, right=0.985, top=0.95, bottom=0.075)

    # (a) time courses: three stacked rows in the top-left cell
    inner = outer[0, 0].subgridspec(3, 1, hspace=0.18)
    dp = meas["d_aSyn"]
    d_mrna = meas["d_mRNA_SNCA"]
    series = []
    for sp in ("miR-7", "median miRNA"):
        r = row("PD", "scan midpoint", sp, T24, kap_a)
        dx = LN2 / float(r["half_life_h"])
        cas = t36.Cascade(d_mrna, mid, dp, dx)
        tt, yy = trajectory(cas, float(r["dose"]), T24, dx)
        series.append((sp, tt, yy))
    names = [tr(lang, "Repressor pool\n(× baseline)", "Pool do repressor\n(× basal)"),
             tr(lang, "mRNA\n(× baseline)", "mRNA\n(× basal)"), tr(lang, "Protein\n(× baseline)", "Proteína\n(× basal)")]
    axs = []
    for k in range(3):
        ax = fig.add_subplot(inner[k])
        for sp, tt, yy in series:
            c, ls, en, pt = SP_COLOUR[sp]
            y = 1 + yy[0] if k == 0 else yy[k]
            ax.plot(tt, y, color=c, ls="-", lw=1.2, label=tr(lang, en, pt))
        if k == 0:
            ax.set_yscale("log")
            ax.set_ylim(1, 30)
            ax.set_yticks([1, 3, 10, 30])
            ax.set_yticklabels(["1", "3", "10", "30"])
        elif k == 1:
            ax.set_ylim(0, 1.15)
        else:
            ax.set_ylim(0.6, 1.05)
        ax.set_ylabel(names[k], fontsize=6.8)
        style_axes(ax)
        if k < 2:
            ax.set_xticklabels([])
        axs.append(ax)
    axs[2].set_xlabel(tr(lang, "Time (h), daily dosing", "Tempo (h), dose diária"))
    axs[0].legend(frameon=False, fontsize=6.5, loc="upper right", handlelength=1.6, borderaxespad=0.1)
    axs[0].set_title(tr(lang, f"PD, {100 * kap_a:.0f}% target, ρ = {mid:.1f}", f"DP, meta de {100 * kap_a:.0f}%, ρ = {mid:.1f}"),
                     fontsize=8, loc="left")
    label_panel(axs[0], "a")

    # (b) peak against rho at 24 h, from the sweep
    ax = fig.add_subplot(outer[0, 1])
    kap_ad = d["ode"]["mimic_dose_vs_measured_knockdown"]["required_BACE1_knockdown"]
    kap_b = kv(d, "K063")
    plot = [("PD", "miR-7", kap_a, vs.PD, "-", 1.4), ("PD", "miR-7", kap_b, vs.PD, "--", 1.4),
            ("PD", "miR-7 upper bound", kap_a, vs.PD, "-.", 1.2), ("PD", "median miRNA", kap_a, vs.INK2, "-", 1.1),
            ("AD", "miR-29b", kap_ad, vs.AD, "-", 1.4), ("AD", "miR-29c", kap_ad, vs.AD, "-.", 1.2),
            ("AD", "median miRNA", kap_ad, vs.TIER_RAMP[0], "-", 1.1)]
    for axis, sp, kap, c, ls, lw in plot:
        pts = sorted([r for r in sweep if r["axis"] == axis and r["species"] == sp
                      and abs(float(r["target_knockdown"]) - kap) < 1e-9 and r["reachable"] == "True"],
                     key=lambda r: float(r["rho"]))
        ax.plot([float(r["rho"]) for r in pts], [float(r["peak_pool_over_baseline"]) for r in pts], color=c, ls=ls, lw=lw)
    pd_ = tgt["repression_strength"]["PD"]
    ad_ = tgt["repression_strength"]["AD"]
    ax.axvspan(pd_["rho_scan_low"], pd_["rho_scan_high"], color=vs.PD_SOFT, alpha=0.6, lw=0)
    ax.axvline(pd_["rho_floor_K065"], color=vs.INK2, lw=0.9, ls=":")
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlim(0.01, 1e4)
    ax.set_ylim(1, 2000)
    ax.set_yticks([1, 3, 10, 30, 100, 300, 1000])
    ax.set_yticklabels(["1", "3", "10", "30", "100", "300", "1000"])
    ax.set_xlabel(tr(lang, "ρ, share of mRNA decay held by the microRNA", "ρ, parcela do decaimento do mRNA com o microRNA"))
    ax.set_ylabel(tr(lang, "Peak of the repressor pool (× baseline)", "Pico do pool do repressor (× basal)"))
    ax.set_title(tr(lang, "Daily dosing, by repression strength", "Dose diária, por força de repressão"), fontsize=8, loc="left")
    style_axes(ax)
    ax.axvspan(ad_["rho_scan_low"], ad_["rho_scan_high"], color=vs.AD_SOFT, alpha=0.45, lw=0)
    handles = [plt.Line2D([], [], color=c, ls=ls, lw=lw) for _, _, _, c, ls, lw in plot]
    names_ = [tr(lang, f"PD miR-7, {100 * kap_a:.0f}%", f"DP miR-7, {100 * kap_a:.0f}%"),
              tr(lang, f"PD miR-7, {100 * kap_b:.0f}%", f"DP miR-7, {100 * kap_b:.0f}%"),
              tr(lang, "PD miR-7 (5 h)", "DP miR-7 (5 h)"), tr(lang, "PD median", "DP mediano"),
              tr(lang, "AD miR-29b", "DA miR-29b"), tr(lang, "AD miR-29c", "DA miR-29c"), tr(lang, "AD median", "DA mediano")]
    ax.legend(handles, names_, frameon=False, fontsize=6.3, loc="upper right", ncol=2, handlelength=1.8,
              columnspacing=0.8, borderaxespad=0.2)
    label_panel(ax, "b")

    # (c) peak against interval, at the scan midpoint
    ax_c = fig.add_subplot(outer[1, 0])
    ax_d = fig.add_subplot(outer[1, 1])
    intervals = [8.0, 12.0, 24.0, 48.0, 168.0]
    cap = tgt["dose_cap_in_baseline_pools"]
    for axis, sp, kap in (("PD", "miR-7", kap_a), ("PD", "miR-7 upper bound", kap_a), ("PD", "median miRNA", kap_a),
                          ("AD", "miR-29b", kap_ad), ("AD", "miR-29c", kap_ad), ("AD", "median miRNA", kap_ad)):
        rr = [row(axis, "scan midpoint", sp, T, kap) for T in intervals]
        c = SP_COLOUR[sp][0] if sp != "median miRNA" else (vs.INK2 if axis == "PD" else vs.TIER_RAMP[0])
        ls = SP_COLOUR[sp][1]
        ok = [(T, r) for T, r in zip(intervals, rr) if r["reachable"] == "True"]
        ax_c.plot([T for T, _ in ok], [float(r["peak_pool_over_baseline"]) for _, r in ok], color=c, ls=ls, lw=1.3,
                  marker="o", ms=3.4, mec="white", mew=0.4)
        ax_d.plot([T for T, _ in ok], [float(r["efficiency"]) for _, r in ok], color=c, ls=ls, lw=1.3,
                  marker="o", ms=3.4, mec="white", mew=0.4)
        for T, r in zip(intervals, rr):
            if r["reachable"] != "True":
                ax_c.plot([T], [cap], marker="o", ms=4.2, mfc="white", mec=c, mew=0.9, ls="none")
                ax_d.plot([T], [0.0], marker="o", ms=4.2, mfc="white", mec=c, mew=0.9, ls="none")
    ax_c.set_yscale("log")
    ax_c.set_xscale("log")
    ax_c.set_xticks(intervals)
    ax_c.set_xticklabels(["8", "12", "24", "48", "168"])
    ax_c.set_ylim(1, cap * 2)
    ax_c.set_yticks([1, 10, 100, 1000, 10000])
    ax_c.set_yticklabels(["1", "10", "100", "1000", "10⁴"])
    ax_c.set_xlabel(tr(lang, "Dosing interval (h)", "Intervalo entre doses (h)"))
    ax_c.set_ylabel(tr(lang, "Peak of the repressor pool (× baseline)", "Pico do pool do repressor (× basal)"))
    ax_c.set_title(tr(lang, f"Dosing interval, ρ = {mid:.1f} (PD) and {tgt['repression_strength']['AD']['rho_scan_mid']:.0f} (AD)",
                      f"Intervalo, ρ = {mid:.1f} (DP) e {tgt['repression_strength']['AD']['rho_scan_mid']:.0f} (DA)"),
                   fontsize=8, loc="left")
    ax_c.text(165, cap * 1.25, tr(lang, "not reached", "não alcançada"), fontsize=6.8, color=vs.INK2, ha="right", va="bottom")
    handles = [plt.Line2D([], [], color=SP_COLOUR["miR-7"][0], ls="-", lw=1.3), plt.Line2D([], [], color=SP_COLOUR["miR-7"][0], ls="--", lw=1.3),
               plt.Line2D([], [], color=vs.INK2, ls="-", lw=1.3), plt.Line2D([], [], color=vs.AD, ls="-", lw=1.3),
               plt.Line2D([], [], color=vs.AD, ls="--", lw=1.3), plt.Line2D([], [], color=vs.TIER_RAMP[0], ls="-", lw=1.3)]
    ax_c.legend(handles, [tr(lang, "PD miR-7", "DP miR-7"), tr(lang, "PD miR-7 (5 h)", "DP miR-7 (5 h)"), tr(lang, "PD median", "DP mediano"),
                          tr(lang, "AD miR-29b", "DA miR-29b"), tr(lang, "AD miR-29c", "DA miR-29c"), tr(lang, "AD median", "DA mediano")],
                frameon=False, fontsize=6.3, loc="upper left", ncol=2, handlelength=1.8, columnspacing=0.8, borderaxespad=0.2)
    style_axes(ax_c)
    label_panel(ax_c, "c")
    ax_d.set_xscale("log")
    ax_d.set_xticks(intervals)
    ax_d.set_xticklabels(["8", "12", "24", "48", "168"])
    ax_d.set_ylim(-0.04, 1.04)
    ax_d.set_xlabel(tr(lang, "Dosing interval (h)", "Intervalo entre doses (h)"))
    ax_d.set_ylabel(tr(lang, "Efficiency", "Eficiência"))
    ax_d.set_title(tr(lang, "Closed form against the cycle", "Forma fechada contra o ciclo"), fontsize=8, loc="left")
    style_axes(ax_d)
    label_panel(ax_d, "d")

    fig.savefig(fig_path(FIG, "mech_target_response", lang), dpi=300, bbox_inches="tight")
    plt.close(fig)


# ----------------------------------------------------------------------------- Fig. 1
def box(ax, x, y, w, h, title, sub, colour, soft, dashed=False, tsize=7.4, ssize=6.1):
    """EN/PT: rounded box with a bold title and a block of small lines | caixa com titulo e linhas pequenas.
    Returns the two text artists so that the caller can check that they fit | devolve os textos."""
    p = vs.rounded(ax, x, y, w, h, fc=soft, ec=colour, r=1.2, lw=1.1 if not dashed else 0.9, z=2)
    if dashed:
        p.set_linestyle((0, (3, 2)))
    t1 = ax.text(x + w / 2, y + h - 2.1, title, ha="center", va="center", fontsize=tsize, color=vs.INK,
                 fontweight="bold", zorder=3)
    t2 = ax.text(x + w / 2, y + h - 4.2, sub, ha="center", va="top", fontsize=ssize, color=vs.INK2,
                 zorder=3, linespacing=1.2)
    return p, t1, t2


def arrow(ax, p0, p1, colour, style="-|>", lw=1.1, ls="-", rad=0.0, mutation=9):
    a = FancyArrowPatch(p0, p1, arrowstyle=style, mutation_scale=mutation, lw=lw, color=colour, ls=ls,
                        connectionstyle=f"arc3,rad={rad}", zorder=4, shrinkA=0, shrinkB=0)
    ax.add_patch(a)


def tbar(ax, p0, p1, colour, lw=1.1, half=1.5):
    """EN/PT: dashed line ending in a bar, the sign for repression | linha tracejada que termina em barra."""
    ax.plot([p0[0], p1[0]], [p0[1], p1[1]], color=colour, lw=lw, ls=(0, (3, 2)), zorder=4, solid_capstyle="butt")
    ax.plot([p1[0], p1[0]], [p1[1] - half, p1[1] + half], color=colour, lw=lw + 0.4, zorder=4, solid_capstyle="butt")


def fig_schematic(d, lang):
    fig = plt.figure(figsize=(174 * MM, 100 * MM))
    ax = fig.add_axes([0.0, 0.0, 1.0, 1.0])
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 57.5)
    ax.axis("off")
    dd = d["dos"]["decay_constants"]
    hl = lambda k: LN2 / dd[k]["decay_per_hour"]
    kin = d["kin"]
    ode = d["ode"]
    W, H, GAP, X0 = 14.6, 13.6, 2.6, 13.4

    def xs(i):
        return X0 + i * (W + GAP)

    def f1(x):
        return f"{x:.1f}"

    yA, yP = 42.6, 12.4
    n_ord = d["tgt"]["nucleation_scaling"]["order_primary_nucleation"]
    m_star = ode["human_abeta_aggregate_load"]["M_star_nM [K014]"]
    apq = ode["enzyme_substrate_stoichiometry"]["APP_per_BACE1"]
    t_b, t_c = f1(hl("miR-29b")), f1(hl("miR-29c"))
    t_b = t_b[:-2] if t_b.endswith((".0", ",0")) else t_b
    drawn = []
    # ---- lane titles and a rule between the lanes
    ax.text(0.5, 56.2, tr(lang, "ALZHEIMER'S DISEASE", "DOENÇA DE ALZHEIMER"), fontsize=8.2, fontweight="bold", color=vs.AD, va="center")
    ax.text(0.5, 26.0, tr(lang, "PARKINSON'S DISEASE", "DOENÇA DE PARKINSON"), fontsize=8.2, fontweight="bold", color=vs.PD, va="center")
    ax.plot([0.5, 99.5], [28.9, 28.9], color=vs.RULE, lw=0.6)
    # ---- Alzheimer lane
    items = [
        ("miR-29a, b, c", tr(lang, f"b {t_b} h, c {t_c} h\na: no decay in 12 h\nK017–K019", f"b {t_b} h, c {t_c} h\na: sem queda em 12 h\nK017–K019")),
        ("BACE1 mRNA", tr(lang, f"half-life {f1(LN2 / float(kin['K068']['value_si']))} h\n5 isoforms pooled\nK067, K068", f"meia-vida {f1(LN2 / float(kin['K068']['value_si']))} h\n5 isoformas juntas\nK067, K068")),
        (tr(lang, "BACE1 protein", "Proteína BACE1"), tr(lang, f"half-life ≈{LN2 / float(kin['K025']['value_si']):.0f} h\nBACE1:APP = 1:{apq:.0f}\nK025, K055, K056", f"meia-vida ≈{LN2 / float(kin['K025']['value_si']):.0f} h\nBACE1:APP = 1:{apq:.0f}\nK025, K055, K056")),
        (tr(lang, "Aβ42 monomers", "Aβ42 monômero"), tr(lang, f"production {kin['K002']['value_as_written']} %/h\nclearance {kin['K004']['value_as_written']} %/h\nin AD; K001–K004", f"produção {kin['K002']['value_as_written']} %/h\ndepuração {kin['K004']['value_as_written']} %/h\nna DA; K001–K004")),
        (tr(lang, "Aβ42 nucleation", "Nucleação Aβ42"), tr(lang, f"orders {n_ord:.0f} and {n_ord:.0f}\nM* {m_star:.0f} nM\nrate constants: gap\nK012–K014, K037", f"ordens {n_ord:.0f} e {n_ord:.0f}\nM* {m_star:.0f} nM\nconstantes: lacuna\nK012–K014, K037")),
    ]
    for i, (t_, s_) in enumerate(items):
        drawn.append(box(ax, xs(i), yA - H / 2, W, H, t_, s_, vs.AD, vs.AD_SOFT, dashed=(i == 4)))
    # ---- Parkinson lane
    items = [
        ("miR-7", tr(lang, f"half-life {f1(hl('miR-7'))} h\nupper bound {hl('miR-7 upper bound'):.0f} h\nCyrano degrades it\nK020–K023", f"meia-vida {f1(hl('miR-7'))} h\nlimite superior {hl('miR-7 upper bound'):.0f} h\nCyrano a degrada\nK020–K023")),
        ("SNCA mRNA", tr(lang, f"half-life {f1(LN2 / float(kin['K066']['value_si']))} h\nrat neurons\nK066", f"meia-vida {f1(LN2 / float(kin['K066']['value_si']))} h\nneurônios de rato\nK066")),
        (tr(lang, "α-synuclein", "α-sinucleína"), tr(lang, f"{f1(float(kin['K054']['value_si']))} µM in a bouton\nhalf-life ≥ {LN2 / float(kin['K026']['value_si']):.0f} h\nK026, K054", f"{f1(float(kin['K054']['value_si']))} µM num botão\nmeia-vida ≥ {LN2 / float(kin['K026']['value_si']):.0f} h\nK026, K054")),
        (tr(lang, "Elongation", "Alongamento"), tr(lang, f"saturating\nm½ {float(kin['K010']['value_si']) * 1e6:.0f}–{float(kin['K009']['value_si']) * 1e6:.0f} µM\nK009, K010", f"saturante\nm½ {float(kin['K010']['value_si']) * 1e6:.0f}–{float(kin['K009']['value_si']) * 1e6:.0f} µM\nK009, K010")),
        (tr(lang, "Nucleation", "Nucleação"), tr(lang, "gated by pH:\nnone at neutral pH\nK011, K042", "controlada por pH:\nnenhuma em pH 7\nK011, K042")),
    ]
    for i, (t_, s_) in enumerate(items):
        drawn.append(box(ax, xs(i), yP - H / 2, W, H, t_, s_, vs.PD, vs.PD_SOFT, dashed=(i == 4)))
    # ---- arrows inside the lanes: repression (dashed bar), then production steps
    for yy, c in ((yA, vs.AD), (yP, vs.PD)):
        tbar(ax, (xs(0) + W + 0.2, yy), (xs(1) - 0.3, yy), vs.INK3)
        for i in range(1, 4):
            arrow(ax, (xs(i) + W + 0.2, yy), (xs(i + 1) - 0.3, yy), c, lw=1.2)
    # ---- what has been measured at the repression step
    ax.text(xs(0) + W + GAP / 2, yA + H / 2 + 1.0, tr(lang, "repression strength not measured\nBACE1 about 50% in cells (K047)", "força da repressão não medida\nBACE1 cerca de 50% em células (K047)"),
            ha="center", va="bottom", fontsize=6.0, color=vs.INK2, linespacing=1.15)
    ax.text(xs(0) + W + GAP / 2, yP + H / 2 + 1.0, tr(lang, f"repression strength not measured\nSNCA {100 * float(kin['K058']['value_si']):.0f}% and {100 * float(kin['K063']['value_si']):.0f}% in cells (K058, K063)", f"força da repressão não medida\nSNCA {100 * float(kin['K058']['value_si']):.0f}% e {100 * float(kin['K063']['value_si']):.0f}% em células (K058, K063)"),
            ha="center", va="bottom", fontsize=6.0, color=vs.INK2, linespacing=1.15)
    # ---- the mimic bolus feeds the repressor pool
    for yy, c, soft in ((yA, vs.AD, vs.AD_SOFT), (yP, vs.PD, vs.PD_SOFT)):
        bx = 0.6
        bw = 9.0
        p = vs.rounded(ax, bx, yy - 4.6, bw, 9.2, fc="white", ec=c, r=1.2, lw=1.1, z=2)
        ax.text(bx + bw / 2, yy + 2.3, tr(lang, "Mimic", "Mimético"), ha="center", va="center", fontsize=7.0, fontweight="bold", color=vs.INK, zorder=3)
        ax.text(bx + bw / 2, yy + 0.5, tr(lang, "bolus D\nevery T h", "bolus D\na cada T h"), ha="center", va="top", fontsize=6.1, color=vs.INK2, linespacing=1.2, zorder=3)
        arrow(ax, (bx + bw + 0.2, yy), (xs(0) - 0.3, yy), c, lw=1.3)
    ax.text(99.5, 0.6, tr(lang, "dashed outline: no measured rate constants      dashed bar: repression", "contorno tracejado: sem constantes medidas      barra tracejada: repressão"),
            ha="right", va="bottom", fontsize=6.0, color=vs.INK3)
    # ---- guard: every text must lie inside its box
    fig.canvas.draw()
    rend = fig.canvas.get_renderer()
    bad = []
    for p, t1, t2 in drawn:
        bb = p.get_window_extent(rend)
        for t in (t1, t2):
            tb = t.get_window_extent(rend)
            if tb.x0 < bb.x0 + 2 or tb.x1 > bb.x1 - 2 or tb.y0 < bb.y0 + 2 or tb.y1 > bb.y1 - 2:
                bad.append(f"{t.get_text()!r}: text {tb.width:.0f} x {tb.height:.0f} px, box {bb.width:.0f} x {bb.height:.0f} px")
    if bad:
        sys.exit(f"EN/PT: text overflows its box on the schematic ({lang}):\n  " + "\n  ".join(bad))
    fig.savefig(fig_path(FIG, "mech_model_schematic", lang), dpi=300, bbox_inches="tight")
    plt.close(fig)


def main():
    os.makedirs(FIG, exist_ok=True)
    d = read_inputs()
    t36 = load_module("t36", "36_mimic_target_response.py")
    for lang in LANGS:
        fig_schematic(d, lang)
        fig_alzheimer(d, lang)
        fig_parkinson(d, lang)
        fig_turnover(d, lang)
        fig_target(d, lang, t36)
    print("=" * 78)
    print("EN | Mechanistic figures | PT | Figuras mecanisticas")
    print("=" * 78)
    for stem in ("mech_model_schematic", "mech_alzheimer", "mech_parkinson", "mech_turnover", "mech_target_response"):
        for lang in LANGS:
            print(f"EN/PT -> {fig_path(FIG, stem, lang)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
