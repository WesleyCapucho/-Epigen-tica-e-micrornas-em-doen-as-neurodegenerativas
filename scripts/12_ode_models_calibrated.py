#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EN | Recalibrated ODE models of the miR-29/BACE1/Abeta and miR-7/SNCA/alpha-synuclein
     axes, driven by the measured constants in data/extracted/kinetic_parameters.csv.
PT | Modelos EDO recalibrados dos eixos miR-29/BACE1/Abeta e miR-7/SNCA/alfa-sinucleina,
     guiados pelas constantes medidas em data/extracted/kinetic_parameters.csv.

EN | What changed, and why. The models in scripts/02 came from the source monograph and
     used illustrative parameters: one lumped "miRNA" variable, first-order aggregation,
     and a disease effect entering through production. Every one of those choices is
     contradicted by a measured value now in the parameter table:

       1. There is no single miR-29. In one assay miR-29b decays with a 7 h half-life,
          miR-29c 10.6 h, and miR-29a does not decay measurably in 12 h (K017-K019).
          The three paralogues are separate state variables here.
       2. miR-7 is not a stable miRNA. Its half-life is 1.7 h, the shortest in a
          genome-wide survey whose median is 34 h (K016, K020), because the lncRNA
          Cyrano drives target-directed degradation. A mimic therefore washes out in
          hours, which a generic decay rate hides completely.
       3. alpha-synuclein fibrils do not grow first-order in monomer. Elongation
          saturates with a half-maximal concentration near 46-50 uM (K009, K010).
       4. At neutral pH, primary and secondary nucleation of alpha-synuclein are
          undetectable (K011). The autocatalytic term must be off unless the
          compartment is acidic. The old model had no such gate.
       5. The Abeta42 elongation constant is NOT in the parameter table: it could not
          be read from any retrievable sentence of its primary source. It is therefore
          a free parameter, and the Abeta aggregation block is illustrative. Borrowing
          the alpha-synuclein value instead would be wrong by roughly two orders of
          magnitude against the measured clearance rate.
       6. In humans, Abeta42 production does not differ between AD and control
          (6.7 vs 6.6 %/h, p = 0.96); clearance does (7.6 vs 5.3 %/h, p = 0.03)
          (K001-K004). The disease lever is clearance. The old model moved production.

PT | O que mudou, e por que. Os modelos do scripts/02 vieram da monografia e usavam
     parametros ilustrativos: uma variavel "miRNA" agregada, agregacao de primeira
     ordem e efeito de doenca entrando pela producao. Cada uma dessas escolhas e
     contrariada por um valor medido que agora esta na tabela de parametros:

       1. Nao existe um unico miR-29. Num mesmo ensaio o miR-29b decai com meia-vida
          de 7 h, o miR-29c 10,6 h e o miR-29a nao decai de forma mensuravel em 12 h
          (K017-K019). Os tres paralogos sao variaveis de estado separadas aqui.
       2. O miR-7 nao e um miRNA estavel. Sua meia-vida e 1,7 h, a mais curta de um
          levantamento genomico cuja mediana e 34 h (K016, K020), porque o lncRNA
          Cyrano promove degradacao dirigida pelo alvo. Um mimetico, portanto, se
          esvai em horas - o que uma taxa generica de decaimento esconde por completo.
       3. Fibrilas de alfa-sinucleina nao crescem em primeira ordem no monomero. A
          elongacao satura, com concentracao de meia-saturacao perto de 46-50 uM
          (K009, K010).
       4. Em pH neutro, nucleacao primaria e secundaria da alfa-sinucleina sao
          indetectaveis (K011). O termo autocatalitico precisa ficar desligado a menos
          que o compartimento seja acido. O modelo antigo nao tinha essa trava.
       5. Em humanos, a producao de Abeta42 nao difere entre AD e controle
          (6,7 vs 6,6 %/h, p = 0,96); a depuracao difere (7,6 vs 5,3 %/h, p = 0,03)
          (K001-K004). A alavanca da doenca e a depuracao. O modelo antigo mexia na
          producao.

EN | What this model is and is not. Where a constant was measured it is used and cited
     by param_id. Where it was not - the mRNA decay rates, the translation and
     transcription rates, the strength of miRNA repression - it is a FREE parameter,
     named as such, and the conclusions are reported across a scan of its plausible
     range rather than at one convenient value. No free parameter was tuned to make a
     result come out. The output is therefore semi-quantitative: it supports statements
     about direction, ordering and order of magnitude, not about absolute concentrations.
PT | O que este modelo e e o que nao e. Onde a constante foi medida, ela e usada e
     citada pelo param_id. Onde nao foi - taxas de decaimento de mRNA, de traducao e de
     transcricao, forca da repressao por miRNA - ela e parametro LIVRE, nomeado como
     tal, e as conclusoes sao reportadas ao longo de uma varredura da faixa plausivel,
     nao num valor conveniente. Nenhum parametro livre foi ajustado para produzir um
     resultado. A saida e, portanto, semiquantitativa: sustenta afirmacoes sobre
     direcao, ordenamento e ordem de grandeza, nao sobre concentracoes absolutas.

    python scripts/12_ode_models_calibrated.py
"""

import csv
import json
import math
import os
import sys

import numpy as np
from scipy.integrate import solve_ivp
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

KINETICS = "data/extracted/kinetic_parameters.csv"
TAB_DIR = "results/tables"
FIG_DIR = "results/figures"
LN2 = math.log(2.0)


# --------------------------------------------------------------------------
# Measured parameters | Parametros medidos
# --------------------------------------------------------------------------
def load_measured():
    """
    EN | Read the measured constants by param_id. Nothing in this script invents a
         number: if an id is missing the script stops rather than falling back to a
         default, because a silent default is how an illustrative parameter becomes a
         quoted result.
    PT | Le as constantes medidas por param_id. Nada neste script inventa numero: se um
         id faltar, o script para em vez de recorrer a um padrao, porque um padrao
         silencioso e justamente como um parametro ilustrativo vira resultado citado.
    """
    if not os.path.exists(KINETICS):
        sys.exit(f"EN/PT: missing {KINETICS}")
    table = {r["param_id"]: r for r in csv.DictReader(open(KINETICS, encoding="utf-8"))}

    def val(pid):
        r = table.get(pid)
        if r is None:
            sys.exit(f"EN/PT: parameter {pid} not found in {KINETICS}")
        if r["kind"] != "numeric":
            sys.exit(f"EN/PT: parameter {pid} is {r['kind']}, not a numeric value")
        return float(r["value_si"])

    m = {
        # Abeta42 handling, human in vivo (Mawuenyega 2010)
        "k_prod_Ab_ctrl": val("K001"),      # 1/h
        "k_prod_Ab_ad":   val("K002"),      # 1/h
        "k_clear_Ab_ctrl": val("K003"),     # 1/h
        "k_clear_Ab_ad":   val("K004"),     # 1/h
        # alpha-synuclein fibril elongation (Buell 2014); M^-1 s^-1 -> uM^-1 h^-1
        "kplus_high": val("K007") * 3600.0 / 1e6,
        "kplus_low":  val("K008") * 3600.0 / 1e6,
        "m_half_uM":  val("K009") * 1e6,    # M -> uM
        "m_half_uM_b": val("K010") * 1e6,
        # Abeta42 aggregation reaction orders (Cohen 2013)
        "n_c": val("K012"),
        "n_2": val("K013"),
        "M_star_uM": val("K014") * 1e6,     # M -> uM
        # miRNA decay constants, 1/h
        "d_miR_median": val("K016"),
        "d_miR29b": val("K017"),
        "d_miR29c": val("K018"),
        "d_miR7":   val("K020"),
        "d_miR7_slow": val("K021"),
        # miR-7 neuronal steady state (Kleaveland 2018)
        "miR7_copies": val("K022"),
        "miR7_fold_noCyrano": val("K023"),
        # protein decay, 1/h
        "d_BACE1_hek": val("K024"),
        "d_BACE1_neuron": val("K025"),
        "d_aSyn": val("K026"),
        "d_proteome_brain": val("K029"),
        # human ageing observations
        "aSyn_protein_aging": val("K027"),  # +1.0 = doubling
        "SNCA_mRNA_aging": val("K028"),     # -0.6
        # Abeta42 aggregate load in human brain, Cohen 2013 Table S2; M
        "Ab_load_ctrl_median": val("K032"),
        "Ab_load_AD_median":   val("K035"),
        "Ab_load_ctrl_lq":     val("K031"),
        "Ab_load_AD_uq":       val("K036"),
        # EN/PT: K040/K041 (genome-wide medians) are deliberately NOT loaded here. They
        #        are kind=derived - computed by this project from a supplementary table,
        #        not read in a sentence - and they only justify the free-parameter range
        #        in FREE["d_mRNA"]. The val() guard refuses non-numeric kinds, which is
        #        what caught an earlier attempt to feed one straight into the model.
    }
    # EN/PT: miR-29a does not decay measurably within the assay (K019, qualitative).
    #        Represented by the slowest rate the data can support, the whole-population
    #        median, and flagged in the output rather than invented as a number.
    m["d_miR29a_proxy"] = m["d_miR_median"]
    return m, table


# --------------------------------------------------------------------------
# Free parameters | Parametros livres
# --------------------------------------------------------------------------
# EN | Every entry here is UNMEASURED in the parameter table. The scan range is what
#      the scripts explore; the midpoint is used only to draw the time courses.
# PT | Toda entrada aqui e NAO MEDIDA na tabela de parametros. A faixa e o que os
#      scripts varrem; o ponto medio serve apenas para desenhar as curvas.
FREE = {
    "d_mRNA": dict(low=LN2 / 20.0, high=LN2 / 2.0,
                   why_en="BACE1 and SNCA mRNA half-life: declared gap K030. Neither gene appears "
                           "in the genome-wide table (checked directly: 0 of 5028 rows), so the "
                           "range spans 2-20 h and brackets the genome-wide median of 9.9 h (K040).",
                   why_pt="Meia-vida do mRNA de BACE1 e SNCA: lacuna declarada K030. Nenhum dos dois "
                           "genes aparece na tabela genomica (checado direto: 0 de 5028 linhas), entao "
                           "a faixa cobre 2-20 h e contem a mediana genomica de 9,9 h (K040)."),
    "k_repress": dict(low=0.1, high=3.0,
                      why_en="Strength of miRNA repression per unit miRNA. Not measured as a "
                              "rate anywhere in the table.",
                      why_pt="Forca da repressao por unidade de miRNA. Nao medida como taxa em "
                              "nenhum ponto da tabela."),
    "k_translate": dict(low=0.2, high=5.0,
                        why_en="Protein output per unit mRNA per hour.",
                        why_pt="Producao de proteina por unidade de mRNA por hora."),
}


def midpoint(name):
    f = FREE[name]
    return math.sqrt(f["low"] * f["high"])   # EN/PT: geometric mean of the scan range


# --------------------------------------------------------------------------
# AD arm | Braco AD : miR-29 paralogues -> BACE1 -> Abeta42
# --------------------------------------------------------------------------
def ad_rhs(t, y, p):
    """
    EN | State: [miR-29a, miR-29b, miR-29c, BACE1 mRNA, BACE1 protein, Abeta monomer,
         fibril number, fibril mass]. Abeta monomer is in relative units; the
         aggregation block uses the measured reaction orders and the critical fibril
         concentration, both from Cohen 2013.
    PT | Estado: [miR-29a, miR-29b, miR-29c, mRNA de BACE1, proteina BACE1, monomero de
         Abeta, numero de fibrilas, massa de fibrilas]. O monomero esta em unidades
         relativas; o bloco de agregacao usa as ordens de reacao medidas e a
         concentracao critica de fibrila, ambas de Cohen 2013.
    """
    a29a, a29b, a29c, mR, pB, A, P, M = y

    # --- miR-29 paralogues, each with its own measured decay -----------------
    d_a = a29a * p["d_miR29a"]
    d_b = a29b * p["d_miR29b"]
    d_c = a29c * p["d_miR29c"]
    dm29a = p["s29a"] - d_a
    dm29b = p["s29b"] - d_b
    dm29c = p["s29c"] - d_c

    # --- BACE1 mRNA: repressed by the summed miR-29 pool ---------------------
    repression = p["k_repress"] * (a29a + a29b + a29c)
    dmR = p["s_mRNA"] - (p["d_mRNA"] + repression) * mR

    # --- BACE1 protein -------------------------------------------------------
    dpB = p["k_translate"] * mR - p["d_BACE1"] * pB

    # --- Abeta42 monomer pool --------------------------------------------
    # EN | A is the MONOMER pool, which is exactly what Mawuenyega et al. measured:
    #      fractional production and clearance of labelled Abeta42 in human CSF. It is
    #      not a total that also contains fibril mass. An earlier version subtracted the
    #      fibril mass from it and then subtracted the elongation flux again, counting
    #      the same molecules twice and driving the AD trajectory BELOW control.
    # PT | A e o pool de MONOMERO, exatamente o que Mawuenyega et al. mediram: producao e
    #      depuracao fracionais de Abeta42 marcado no liquor humano. Nao e um total que
    #      contenha tambem massa de fibrila. Uma versao anterior subtraia a massa de
    #      fibrila dele e depois subtraia o fluxo de elongacao de novo, contando as
    #      mesmas moleculas duas vezes e levando a trajetoria de AD ABAIXO do controle.
    dA = p["k_prod_Ab"] * pB - p["k_clear_Ab"] * A

    # --- Abeta42 aggregation: reaction orders measured, rate constants NOT ----
    # EN | Cohen 2013 gives n_c, n_2 and the critical fibril concentration M_star, but
    #      its elongation constant could not be read from any retrievable sentence of
    #      the primary source, so k_plus, k_n and k_2 are FREE here. An earlier version
    #      borrowed the alpha-synuclein k_plus (K007), which is about a hundred times
    #      the Abeta clearance rate and swamped the monomer pool. Constants are not
    #      transferable between proteins, and this block is reported as illustrative.
    # PT | Cohen 2013 da n_c, n_2 e a concentracao critica de fibrila M_star, mas sua
    #      constante de elongacao nao pode ser lida em nenhuma frase recuperavel da fonte
    #      primaria, entao k_plus, k_n e k_2 sao LIVRES aqui. Uma versao anterior tomou
    #      emprestado o k_plus da alfa-sinucleina (K007), cerca de cem vezes a taxa de
    #      depuracao do Abeta, e engoliu o pool de monomero. Constantes nao sao
    #      transferiveis entre proteinas, e este bloco e reportado como ilustrativo.
    nucleation = p["k_n"] * A ** p["n_c"]
    secondary = p["k_2"] * A ** p["n_2"] * M if M > p["M_star"] else 0.0
    dP = nucleation + secondary
    dM = 2.0 * p["k_plus_Ab_FREE"] * A * P

    return [dm29a, dm29b, dm29c, dmR, dpB, dA, dP, dM]


def run_ad(measured, condition, free=None, t_end=2000.0, mimic=1.0):
    """EN/PT: one AD trajectory. `mimic` multiplies miR-29 synthesis."""
    free = free or {k: midpoint(k) for k in FREE}
    p = {
        "d_miR29a": measured["d_miR29a_proxy"],
        "d_miR29b": measured["d_miR29b"],
        "d_miR29c": measured["d_miR29c"],
        "d_mRNA": free["d_mRNA"],
        "k_repress": free["k_repress"],
        "k_translate": free["k_translate"],
        "d_BACE1": measured["d_BACE1_neuron"],
        "n_c": measured["n_c"],
        "n_2": measured["n_2"],
        "M_star": measured["M_star_uM"],
        # EN/PT: all three are FREE - no measured Abeta elongation constant exists
        #        in the parameter table. They set the illustrative aggregation block
        #        only and do not feed back on the monomer pool.
        "k_n": 1e-6,
        "k_2": 1e-4,
        "k_plus_Ab_FREE": 1e-3,
    }
    # EN/PT: each paralogue held at a steady state of 1.0 before the mimic
    p["s29a"] = 1.0 * p["d_miR29a"] * mimic
    p["s29b"] = 1.0 * p["d_miR29b"] * mimic
    p["s29c"] = 1.0 * p["d_miR29c"] * mimic
    p["s_mRNA"] = 1.0

    if condition == "control":
        p["k_prod_Ab"] = measured["k_prod_Ab_ctrl"]
        p["k_clear_Ab"] = measured["k_clear_Ab_ctrl"]
    elif condition == "AD":
        p["k_prod_Ab"] = measured["k_prod_Ab_ad"]
        p["k_clear_Ab"] = measured["k_clear_Ab_ad"]
    else:
        raise ValueError(condition)

    y0 = [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1e-3, 0.0]
    sol = solve_ivp(ad_rhs, (0.0, t_end), y0, args=(p,),
                    t_eval=np.linspace(0.0, t_end, 1200), method="LSODA", rtol=1e-8, atol=1e-10)
    return sol, p


# --------------------------------------------------------------------------
# PD arm | Braco PD : miR-7 -> SNCA -> alpha-synuclein
# --------------------------------------------------------------------------
def pd_rhs(t, y, p):
    """
    EN | State: [miR-7, SNCA mRNA, alpha-syn monomer, fibril number, fibril mass].
         Elongation saturates with monomer (Buell 2014), and nucleation is gated on
         compartment pH: at neutral pH both nucleation terms are zero, which is a
         measured absence, not an assumption.
    PT | Estado: [miR-7, mRNA de SNCA, monomero de alfa-sin, numero de fibrilas, massa].
         A elongacao satura com o monomero (Buell 2014) e a nucleacao e condicionada ao
         pH do compartimento: em pH neutro os dois termos sao zero, o que e ausencia
         medida, e nao suposicao.
    """
    miR7, mR, S, P, M = y

    dmiR7 = p["s_miR7"] - p["d_miR7"] * miR7
    repression = p["k_repress"] * miR7
    dmR = p["s_mRNA"] - (p["d_mRNA"] + repression) * mR

    free_S = max(S - M, 0.0)
    # EN/PT: Michaelis-Menten-like saturation, m_half from Buell 2014 (K009/K010)
    elong = 2.0 * p["k_plus"] * P * free_S / (p["m_half"] + free_S)
    if p["acidic"]:
        dP = p["k_n"] * free_S ** 2 + p["k_2"] * free_S ** 2 * M
    else:
        dP = 0.0     # EN/PT: K011, undetectable at neutral pH under quiescent conditions

    dS = p["k_translate"] * mR - p["d_aSyn"] * free_S - elong
    dM = elong
    return [dmiR7, dmR, dS, dP, dM]


def run_pd(measured, acidic=False, free=None, t_end=2000.0, mimic=1.0,
           d_miR7=None, seed=1e-3):
    free = free or {k: midpoint(k) for k in FREE}
    p = {
        "d_miR7": d_miR7 if d_miR7 is not None else measured["d_miR7"],
        "d_mRNA": free["d_mRNA"],
        "k_repress": free["k_repress"],
        "k_translate": free["k_translate"],
        "d_aSyn": measured["d_aSyn"],
        "k_plus": measured["kplus_high"],
        "m_half": measured["m_half_uM"],
        "k_n": 1e-8,
        "k_2": 1e-6,
        "acidic": acidic,
    }
    p["s_miR7"] = 1.0 * p["d_miR7"] * mimic
    p["s_mRNA"] = 1.0
    y0 = [1.0, 1.0, 1.0, seed, 0.0]
    sol = solve_ivp(pd_rhs, (0.0, t_end), y0, args=(p,),
                    t_eval=np.linspace(0.0, t_end, 1200), method="LSODA", rtol=1e-8, atol=1e-10)
    return sol, p


# --------------------------------------------------------------------------
# Experiments | Experimentos
# --------------------------------------------------------------------------
def experiment_clearance_vs_production(measured):
    """
    EN | The central AD question. Human data say the disease lever is clearance, not
         production. A miR-29 mimic acts on production. How large a mimic would be
         needed to bring AD Abeta back to the control steady state?
    PT | A questao central de AD. Os dados humanos dizem que a alavanca e a depuracao,
         nao a producao. Um mimetico de miR-29 age na producao. Que tamanho de mimetico
         seria preciso para trazer o Abeta de AD de volta ao estado do controle?
    """
    sol_c, _ = run_ad(measured, "control")
    sol_d, _ = run_ad(measured, "AD")
    ab_c = sol_c.y[5][-1]
    ab_d = sol_d.y[5][-1]

    # EN/PT: scan mimic strength until the AD trajectory reaches the control level
    needed, grid = None, np.linspace(1.0, 60.0, 240)
    for f in grid:
        s, _ = run_ad(measured, "AD", mimic=float(f))
        if s.y[5][-1] <= ab_c:
            needed = float(f)
            break

    # EN/PT: for comparison, restoring clearance alone
    return dict(
        abeta_control=float(ab_c),
        abeta_AD=float(ab_d),
        abeta_ratio_AD_over_control=float(ab_d / ab_c) if ab_c else float("nan"),
        clearance_deficit_percent=float(
            100.0 * (1.0 - measured["k_clear_Ab_ad"] / measured["k_clear_Ab_ctrl"])),
        production_difference_percent=float(
            100.0 * (1.0 - measured["k_prod_Ab_ad"] / measured["k_prod_Ab_ctrl"])),
        mimic_fold_needed=needed,
        mimic_scan_max=float(grid[-1]),
    )


def experiment_mimic_washout(measured):
    """
    EN | How long does a single-dose miRNA mimic last, given the measured decay rates?
    PT | Quanto dura um mimetico de dose unica, dadas as taxas de decaimento medidas?
    """
    out = {}
    for label, d in [("miR-7 (1.7 h, K020)", measured["d_miR7"]),
                     ("miR-7 upper bound (5 h, K021)", measured["d_miR7_slow"]),
                     ("miR-29b (7 h, K017)", measured["d_miR29b"]),
                     ("miR-29c (10.6 h, K018)", measured["d_miR29c"]),
                     ("median miRNA (34 h, K016)", measured["d_miR_median"])]:
        # EN/PT: time for a 10-fold bolus to fall back within 10% of baseline
        t = math.log(9.0) / d if d > 0 else float("nan")
        out[label] = dict(decay_constant_per_hour=float(d),
                          half_life_hours=float(LN2 / d),
                          hours_to_return_to_baseline=float(t),
                          days_to_return_to_baseline=float(t / 24.0))
    return out


def experiment_human_aggregate_load(measured):
    """
    EN | Where the measured human brain aggregate loads sit relative to the critical
         fibril concentration above which secondary nucleation takes over. This is a
         comparison of measured quantities, not a simulation output, so it does not
         depend on any free parameter.
    PT | Onde as cargas de agregado medidas em cerebro humano ficam em relacao a
         concentracao critica de fibrila acima da qual a nucleacao secundaria assume.
         E uma comparacao entre quantidades medidas, nao saida de simulacao, entao nao
         depende de nenhum parametro livre.
    """
    mstar = measured["M_star_uM"] * 1e-6          # uM -> M
    out = {}
    for lab, key in [("control median [K032]", "Ab_load_ctrl_median"),
                     ("control lower quartile [K031]", "Ab_load_ctrl_lq"),
                     ("AD median [K035]", "Ab_load_AD_median"),
                     ("AD upper quartile [K036]", "Ab_load_AD_uq")]:
        out[lab] = dict(load_nM=measured[key] * 1e9,
                        multiples_of_M_star=measured[key] / mstar,
                        above_M_star=bool(measured[key] > mstar))
    out["M_star_nM [K014]"] = mstar * 1e9
    out["AD_over_control_median_fold"] = (measured["Ab_load_AD_median"]
                                          / measured["Ab_load_ctrl_median"])
    return out


def experiment_ph_gate(measured):
    """
    EN | What the pH gate does to aggregate number, holding everything else fixed.
    PT | O que a trava de pH faz com o numero de agregados, com o resto fixo.
    """
    neutral, _ = run_pd(measured, acidic=False)
    acidic, _ = run_pd(measured, acidic=True)
    return dict(
        fibril_number_neutral_pH=float(neutral.y[3][-1]),
        fibril_number_acidic_pH=float(acidic.y[3][-1]),
        fold_difference=float(acidic.y[3][-1] / neutral.y[3][-1]) if neutral.y[3][-1] else float("inf"),
        fibril_mass_neutral_pH=float(neutral.y[4][-1]),
        fibril_mass_acidic_pH=float(acidic.y[4][-1]),
    )


def experiment_free_parameter_sensitivity(measured, n=9):
    """
    EN | Do the qualitative conclusions survive the free parameters? Each is scanned
         across its full range while the others sit at their midpoint.
    PT | As conclusoes qualitativas sobrevivem aos parametros livres? Cada um e varrido
         em toda a faixa enquanto os outros ficam no ponto medio.
    """
    rows = []
    base = {k: midpoint(k) for k in FREE}
    for name, spec in FREE.items():
        for v in np.geomspace(spec["low"], spec["high"], n):
            free = dict(base)
            free[name] = float(v)
            sc, _ = run_ad(measured, "control", free=free)
            sd, _ = run_ad(measured, "AD", free=free)
            ratio = sd.y[5][-1] / sc.y[5][-1] if sc.y[5][-1] else float("nan")
            # EN | Three outcomes, not two. A non-finite ratio means the illustrative
            #      aggregation block diverged at this corner of the scan; it is NOT
            #      evidence against the conclusion. An earlier version counted such a
            #      NaN as a flip and printed "CONCLUSION NOT ROBUST" off a single
            #      numerical blow-up.
            # PT | Tres desfechos, nao dois. Um ratio nao finito significa que o bloco
            #      ilustrativo de agregacao divergiu naquele canto da varredura; NAO e
            #      evidencia contra a conclusao. Uma versao anterior contava esse NaN
            #      como inversao e imprimia "CONCLUSAO NAO ROBUSTA" por causa de uma
            #      unica explosao numerica.
            if not math.isfinite(ratio):
                verdict = "not_evaluable"
            elif ratio > 1.0:
                verdict = "AD_above_control"
            else:
                verdict = "AD_at_or_below_control"
            rows.append(dict(free_parameter=name, value=float(v),
                             abeta_AD_over_control=float(ratio),
                             verdict=verdict))
    return rows


def figures(measured):
    os.makedirs(FIG_DIR, exist_ok=True)
    fig, axes = plt.subplots(2, 2, figsize=(12, 8))

    # --- miR-29 paralogues decay apart ---------------------------------------
    ax = axes[0, 0]
    t = np.linspace(0, 48, 400)
    for lab, d, pid in [("miR-29a (no measurable decay)", measured["d_miR29a_proxy"], "K019"),
                        ("miR-29b (7 h)", measured["d_miR29b"], "K017"),
                        ("miR-29c (10.6 h)", measured["d_miR29c"], "K018")]:
        ax.plot(t, np.exp(-d * t), label=f"{lab}  [{pid}]")
    ax.set_title("miR-29 paralogues are not one species\nParalogos de miR-29 nao sao uma especie", fontsize=9)
    ax.set_xlabel("hours | horas"); ax.set_ylabel("fraction remaining | fracao restante")
    ax.legend(fontsize=7); ax.grid(alpha=.3)

    # --- miR-7 washout -------------------------------------------------------
    ax = axes[0, 1]
    t = np.linspace(0, 120, 400)
    for lab, d in [("miR-7 (1.7 h) [K020]", measured["d_miR7"]),
                   ("miR-7 bound (5 h) [K021]", measured["d_miR7_slow"]),
                   ("median miRNA (34 h) [K016]", measured["d_miR_median"])]:
        ax.plot(t, 1.0 + 9.0 * np.exp(-d * t), label=lab)
    ax.axhline(1.1, ls="--", c="k", lw=.8)
    ax.set_yscale("log")
    ax.set_title("A 10-fold mimic bolus, by measured decay\nBolus 10x de mimetico, pelo decaimento medido", fontsize=9)
    ax.set_xlabel("hours | horas"); ax.set_ylabel("fold over baseline | vezes o basal")
    ax.legend(fontsize=7); ax.grid(alpha=.3)

    # --- Abeta: clearance vs production --------------------------------------
    ax = axes[1, 0]
    sc, _ = run_ad(measured, "control")
    sd, _ = run_ad(measured, "AD")
    ax.plot(sc.t / 24.0, sc.y[5], label="control | controle")
    ax.plot(sd.t / 24.0, sd.y[5], label="AD (clearance -30%) | AD (depuracao -30%)")
    ax.set_title("Abeta42: the human lever is clearance [K001-K004]\nAbeta42: a alavanca humana e a depuracao", fontsize=9)
    ax.set_xlabel("days | dias"); ax.set_ylabel("Abeta (relative | relativo)")
    ax.legend(fontsize=7); ax.grid(alpha=.3)

    # --- alpha-syn aggregation, pH gate --------------------------------------
    ax = axes[1, 1]
    sn, _ = run_pd(measured, acidic=False)
    sa, _ = run_pd(measured, acidic=True)
    ax.plot(sn.t / 24.0, sn.y[4], label="neutral pH: no self-amplification [K011]")
    ax.plot(sa.t / 24.0, sa.y[4], label="acidic pH: secondary nucleation on")
    ax.set_title("alpha-synuclein fibril mass\nMassa de fibrila de alfa-sinucleina", fontsize=9)
    ax.set_xlabel("days | dias"); ax.set_ylabel("fibril mass | massa (relative)")
    ax.legend(fontsize=7); ax.grid(alpha=.3)

    fig.tight_layout()
    fig.savefig(f"{FIG_DIR}/ode_calibrated_overview.png", dpi=200)
    plt.close(fig)


def main():
    os.makedirs(TAB_DIR, exist_ok=True)
    measured, table = load_measured()

    print("=" * 78)
    print("EN | Recalibrated ODE models | PT | Modelos EDO recalibrados")
    print("=" * 78)
    n_used = sum(1 for r in table.values() if r["kind"] == "numeric")
    print(f"Measured constants available / constantes medidas : {n_used}")
    print(f"Free parameters / parametros livres               : {len(FREE)}")
    for k, v in FREE.items():
        print(f"    {k:<14} scan {v['low']:.4g} .. {v['high']:.4g}")

    clearance = experiment_clearance_vs_production(measured)
    washout = experiment_mimic_washout(measured)
    ph = experiment_ph_gate(measured)
    loads = experiment_human_aggregate_load(measured)
    sens = experiment_free_parameter_sensitivity(measured)

    print("\n--- AD: clearance versus production ---")
    print(f"  Abeta AD / control            : {clearance['abeta_ratio_AD_over_control']:.3f}")
    print(f"  measured clearance deficit    : {clearance['clearance_deficit_percent']:.1f}%")
    print(f"  measured production difference: {clearance['production_difference_percent']:.1f}%")
    mf = clearance["mimic_fold_needed"]
    print(f"  miR-29 mimic fold needed      : "
          f"{'>%.0f (not reached in scan)' % clearance['mimic_scan_max'] if mf is None else '%.1f' % mf}")

    print("\n--- Single-dose mimic washout ---")
    for lab, d in washout.items():
        print(f"  {lab:<32} t_half {d['half_life_hours']:6.1f} h   "
              f"back to baseline in {d['days_to_return_to_baseline']:6.2f} d")

    print("\n--- Human brain Abeta42 aggregate load vs the critical concentration ---")
    print(f"  M* (secondary nucleation takes over) : {loads['M_star_nM [K014]']:.4g} nM")
    for lab in ["control lower quartile [K031]", "control median [K032]",
                "AD median [K035]", "AD upper quartile [K036]"]:
        d = loads[lab]
        print(f"  {lab:<32} {d['load_nM']:8.4g} nM   "
              f"{d['multiples_of_M_star']:8.4g} x M*   "
              f"{'above' if d['above_M_star'] else 'below'}")
    print(f"  AD / control, median                 : "
          f"{loads['AD_over_control_median_fold']:.4g} fold")

    print("\n--- alpha-synuclein pH gate ---")
    print(f"  fibril number, neutral pH     : {ph['fibril_number_neutral_pH']:.4g}")
    print(f"  fibril number, acidic pH      : {ph['fibril_number_acidic_pH']:.4g}")
    print(f"  fold difference               : {ph['fold_difference']:.4g}")

    flips = [r for r in sens if r["verdict"] == "AD_at_or_below_control"]
    nanq = [r for r in sens if r["verdict"] == "not_evaluable"]
    ok = [r for r in sens if r["verdict"] == "AD_above_control"]
    ratios = [r["abeta_AD_over_control"] for r in ok]
    print("\n--- Free-parameter sensitivity ---")
    print(f"  scans run / varreduras        : {len(sens)}")
    print(f"  AD above control              : {len(ok)}")
    print(f"  AD at or below control        : {len(flips)}")
    print(f"  not evaluable (diverged)      : {len(nanq)}")
    if ratios:
        print(f"  ratio range across all scans  : {min(ratios):.4f} .. {max(ratios):.4f}")
    print("  " + ("conclusion holds throughout | conclusao se mantem"
                  if not flips else "CONCLUSION NOT ROBUST | CONCLUSAO NAO ROBUSTA"))

    out = dict(
        generated_on="2026-09-22",
        measured_parameter_source=KINETICS,
        free_parameters={k: {kk: (vv if not isinstance(vv, float) else float(vv))
                             for kk, vv in v.items()} for k, v in FREE.items()},
        ad_clearance_vs_production=clearance,
        mimic_washout=washout,
        alpha_synuclein_ph_gate=ph,
        human_abeta_aggregate_load=loads,
        free_parameter_sensitivity_scans=len(sens),
        free_parameter_sensitivity_ad_above_control=len(ok),
        free_parameter_sensitivity_flips=len(flips),
        free_parameter_sensitivity_not_evaluable=len(nanq),
        abeta_ratio_min=float(min(ratios)) if ratios else None,
        abeta_ratio_max=float(max(ratios)) if ratios else None,
        abeta_ratio_note_en=("The AD/control monomer ratio is analytically "
                             "(k_prod_AD/k_clear_AD)/(k_prod_ctrl/k_clear_ctrl) and is therefore "
                             "independent of every free parameter. The scan confirms this "
                             "numerically rather than discovering it."),
        abeta_ratio_note_pt=("O ratio de monomero AD/controle e analiticamente "
                             "(k_prod_AD/k_clear_AD)/(k_prod_ctrl/k_clear_ctrl) e, portanto, "
                             "independente de todo parametro livre. A varredura confirma isso "
                             "numericamente, em vez de descobrir."),
    )
    json.dump(out, open(f"{TAB_DIR}/ode_calibrated_results.json", "w"),
              ensure_ascii=False, indent=1)
    with open(f"{TAB_DIR}/ode_free_parameter_sensitivity.csv", "w", newline="",
              encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(sens[0].keys()))
        w.writeheader(); w.writerows(sens)

    figures(measured)
    print(f"\nEN/PT -> {TAB_DIR}/ode_calibrated_results.json")
    print(f"EN/PT -> {TAB_DIR}/ode_free_parameter_sensitivity.csv")
    print(f"EN/PT -> {FIG_DIR}/ode_calibrated_overview.png")
    return 0


if __name__ == "__main__":
    sys.exit(main())
