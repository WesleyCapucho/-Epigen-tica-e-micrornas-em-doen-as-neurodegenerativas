#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EN | One figure collecting the equations this review's synthesis actually runs, typeset
     exactly as scripts/05_meta_analysis.py and scripts/15_bivariate_srocc.py implement
     them - not a textbook's generic version. Each panel names the script and function
     it comes from, so a reader can go straight to the code that evaluates it.
PT | Uma figura reunindo as equacoes que a sintese desta revisao de fato executa,
     tipografadas exatamente como scripts/05_meta_analysis.py e
     scripts/15_bivariate_srocc.py as implementam - nao a versao generica de livro-texto.
     Cada painel nomeia o script e a funcao de onde vem, para que o leitor va direto ao
     codigo que a avalia.

    python scripts/22_key_equations_figure.py
"""

import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _bilingual import LANGS, t as tr, fig_path

FIG_DIR = "results/figures"


def panel(ax, title, eq_lines, source, title_color="#1F3864"):
    ax.axis("off")
    ax.text(0.02, 0.93, title, transform=ax.transAxes, fontsize=12.5, weight="bold",
             color=title_color, va="top")
    y = 0.66
    for line in eq_lines:
        ax.text(0.06, y, line, transform=ax.transAxes, fontsize=13.5, va="top")
        y -= 0.28
    ax.text(0.02, 0.04, source, transform=ax.transAxes, fontsize=8.2, color="#6b6a66",
             style="italic", va="bottom")
    for spine in ("top", "right", "bottom", "left"):
        pass
    ax.add_patch(plt.Rectangle((0, 0), 1, 1, transform=ax.transAxes, fill=False,
                                edgecolor="#d8d7d3", linewidth=1.1))


def plot(path, lang):
    fig, axes = plt.subplots(3, 2, figsize=(12.5, 11.5))
    fig.suptitle(tr(lang, "Key equations used in the synthesis",
                     "Equações-chave usadas na síntese"),
                 fontsize=16, weight="bold", y=0.99)

    panel(axes[0, 0],
          tr(lang, "1. Logit transform", "1. Transformação logito"),
          [r"$\mathrm{logit}(AUC) = \ln\dfrac{AUC}{1-AUC}$",
           r"$SE_{\mathrm{logit}} = \dfrac{SE_{AUC}}{AUC\,(1-AUC)}$"],
          tr(lang, "scripts/05_meta_analysis.py — logit(), delta method",
             "scripts/05_meta_analysis.py — logit(), método delta"))

    panel(axes[0, 1],
          tr(lang, "2. Hanley–McNeil standard error", "2. Erro-padrão de Hanley–McNeil"),
          [r"$Q_1=\dfrac{AUC}{2-AUC},\ \ Q_2=\dfrac{2\,AUC^2}{1+AUC}$",
           r"$SE(AUC)=\sqrt{\dfrac{AUC(1{-}AUC)+(n_1{-}1)(Q_1{-}AUC^2)+(n_2{-}1)(Q_2{-}AUC^2)}{n_1 n_2}}$"],
          tr(lang, "scripts/05_meta_analysis.py — se_hanley_mcneil(); Hanley & McNeil, 1982",
             "scripts/05_meta_analysis.py — se_hanley_mcneil(); Hanley & McNeil, 1982"))

    panel(axes[1, 0],
          tr(lang, "3. DerSimonian–Laird random effects", "3. Efeitos aleatórios de DerSimonian–Laird"),
          [r"$\hat\tau^2=\max\!\left(0,\ \dfrac{Q-(k-1)}{\sum w_i-\sum w_i^2/\sum w_i}\right)$",
           r"$\hat\theta=\dfrac{\sum w_i^{*}y_i}{\sum w_i^{*}},\ \ w_i^{*}=\dfrac{1}{v_i+\hat\tau^2}$"],
          tr(lang, "scripts/05_meta_analysis.py — dersimonian_laird(); DerSimonian & Laird, 1986",
             "scripts/05_meta_analysis.py — dersimonian_laird(); DerSimonian & Laird, 1986"))

    panel(axes[1, 1],
          tr(lang, "4. Egger's regression test", "4. Teste de regressão de Egger"),
          [r"$\dfrac{y_i}{SE_i} = a + b\left(\dfrac{1}{SE_i}\right)$",
           tr(lang, "$a \\neq 0$ read as small-study asymmetry",
              "$a \\neq 0$ lido como assimetria de estudo pequeno")],
          tr(lang, "scripts/05_meta_analysis.py — egger_test(); Egger et al., 1997",
             "scripts/05_meta_analysis.py — egger_test(); Egger et al., 1997"))

    panel(axes[2, 0],
          tr(lang, "5. Bivariate model (Reitsma)", "5. Modelo bivariado (Reitsma)"),
          [r"$\mathrm{logit}(Se_i),\ \mathrm{logit}(Sp_i)\ \sim\ \mathrm{BVN}(\mu_{Se},\,\mu_{Sp},\,\tau_{Se}^2,\,\tau_{Sp}^2,\,\rho)$",
           tr(lang, "joint normal in $Se$ and $Sp$, correlated by $\\rho$ across studies",
              "normal conjunta em $Se$ e $Sp$, correlacionada por $\\rho$ entre estudos")],
          tr(lang, "scripts/15_bivariate_srocc.py; Reitsma et al., 2005",
             "scripts/15_bivariate_srocc.py; Reitsma et al., 2005"))

    panel(axes[2, 1],
          tr(lang, "6. Standard error from a reported 95% CI", "6. Erro-padrão a partir de um IC 95% reportado"),
          [r"$SE = \dfrac{\mathrm{upper} - \mathrm{lower}}{2 \times 1.959964}$"],
          tr(lang, "scripts/05_meta_analysis.py — se_from_ci()",
             "scripts/05_meta_analysis.py — se_from_ci()"))

    plt.tight_layout(rect=[0, 0, 1, 0.965])
    fig.savefig(path, dpi=600, facecolor="white")
    plt.close(fig)


def main():
    os.makedirs(FIG_DIR, exist_ok=True)
    for lang in LANGS:
        plot(fig_path(FIG_DIR, "key_equations", lang), lang)
    print("=" * 78)
    print("EN | Key equations | PT | Equacoes-chave")
    print("=" * 78)
    for lang in LANGS:
        print(f"EN/PT -> {fig_path(FIG_DIR, 'key_equations', lang)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
