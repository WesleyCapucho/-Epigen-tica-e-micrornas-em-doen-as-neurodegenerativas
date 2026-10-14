#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EN | Gathers every number that the Article 2 manuscript (the mechanistic study) quotes
     into one flat file, results/tables/manuscript2_numbers.json, read from the result
     tables of scripts 12, 17 and 36 and from the kinetic parameter table, and from
     nothing else. The manuscript text is kept outside the repository; it carries
     placeholders such as {{ad.kappa}} and a renderer replaces each one with the value
     stored here, and refuses to build if a placeholder has no value. A number in the
     manuscript therefore cannot differ from the table it came from.

     Like scripts/35 for Article 1, this script computes nothing new about the models.
     It selects, rounds and counts (half-up rounding) from files already written, and a
     few values that are plain arithmetic on two table entries (a ratio, a percentage,
     a time to 90%) are computed here and labelled as such in "_sources". Each value is
     stored as a string, already formatted for the manuscript. Every sentence of the
     manuscript that relies on a pattern in the data (all 18 scans evaluable, the
     floor that the only loss-of-function observation sets on the repression strength lying below the scan,
     a regimen out of reach at every repression strength) has an assert here, so the
     sentence fails loudly if a rerun stops supporting it.

PT | Reune num arquivo plano, results/tables/manuscript2_numbers.json, todo numero que o
     manuscrito do Artigo 2 (o estudo mecanistico) cita, lido das tabelas de resultado
     dos scripts 12, 17 e 36 e da tabela de parametros cineticos, e de mais nada. O texto
     do manuscrito fica fora do repositorio; ele traz marcadores como {{ad.kappa}} e um
     montador troca cada um pelo valor guardado aqui, e se recusa a montar se algum
     marcador nao tiver valor. Um numero do manuscrito nao pode diferir da tabela de onde
     veio.

     Como o scripts/35 para o Artigo 1, este script nao calcula nada novo sobre os
     modelos. Ele seleciona, arredonda e conta (meio-para-cima) a partir de arquivos ja
     gravados, e uns poucos valores que sao aritmetica simples sobre duas entradas da
     tabela (uma razao, uma porcentagem, um tempo ate 90%) sao calculados aqui e
     rotulados assim em "_sources". Cada valor e guardado como texto, ja formatado para o
     manuscrito. Toda frase do manuscrito que depende de um padrao nos dados (as 18
     varreduras avaliaveis, a piso que a unica observacao de perda de funcao poe na forca de repressao
     abaixo da varredura, um regime fora de alcance em toda forca de repressao) tem um
     assert aqui, e a frase falha de forma explicita se uma nova execucao deixar de
     sustenta-la.

    python scripts/37_manuscript2_numbers.py
"""

import csv
import json
import math
import os
import sys
from decimal import ROUND_HALF_UP, Decimal

T = "results/tables"
KIN = "data/extracted/kinetic_parameters.csv"
ODE = f"{T}/ode_calibrated_results.json"
SENS = f"{T}/ode_free_parameter_sensitivity.csv"
DOS_J = f"{T}/mimic_dosing_feasibility.json"
DOS_C = f"{T}/mimic_dosing_feasibility.csv"
TGT_J = f"{T}/mimic_target_response.json"
TGT_C = f"{T}/mimic_target_response.csv"
OUT = f"{T}/manuscript2_numbers.json"

N, SRC = {}, {}
LN2 = math.log(2.0)


def rnd(x, nd):
    q = Decimal(1).scaleb(-nd)
    return str(Decimal(repr(round(float(x), 10))).quantize(q, rounding=ROUND_HALF_UP))


def hl_fmt(x):
    """EN/PT: a half-life without a trailing zero: 7 h, 34 h, but 1.7 h and 10.6 h."""
    x = float(x)
    return str(int(round(x))) if abs(x - round(x)) < 1e-3 else rnd(x, 1)


def put(key, value, src):
    if key in N:
        raise KeyError(f"duplicate key {key}")
    N[key] = value if isinstance(value, str) else str(value)
    SRC[key] = src


def num(key, x, nd, src):
    put(key, rnd(x, nd), src)


def integer(key, x, src):
    put(key, f"{int(round(float(x))):,}", src)


def pct(key, x, nd, src):
    put(key, rnd(float(x) * 100.0, nd), src)


def peak(x):
    """EN/PT: one decimal below 10, whole numbers from 10 up, thousands separated."""
    x = float(x)
    if x < 10.0:
        return rnd(x, 1)
    return f"{int(Decimal(repr(round(x, 8))).quantize(Decimal(1), rounding=ROUND_HALF_UP)):,}"


def lower_bound(x):
    """EN/PT: round DOWN, to one decimal below 10 and to a whole number from 10 up, so that "at least X" stays true."""
    x = float(x)
    if x < 10.0:
        return f"{int(Decimal(repr(round(x, 8))) * 10) / 10:.1f}"
    return f"{int(Decimal(repr(round(x, 8)))):,}"


def must(cond, msg):
    if not cond:
        sys.exit(f"EN/PT: manuscript2 numbers: {msg}")


# ----------------------------------------------------------------------------- inputs
kin = {r["param_id"]: r for r in csv.DictReader(open(KIN, encoding="utf-8"))}
ode = json.load(open(ODE, encoding="utf-8"))
dos = json.load(open(DOS_J, encoding="utf-8"))
dos_rows = list(csv.DictReader(open(DOS_C, encoding="utf-8")))
sens = list(csv.DictReader(open(SENS, encoding="utf-8")))
tgt = json.load(open(TGT_J, encoding="utf-8"))
rows = list(csv.DictReader(open(TGT_C, encoding="utf-8")))


def v(pid):
    r = kin[pid]
    must(r["kind"] in ("numeric", "derived"), f"{pid} is {r['kind']}, not a number")
    return float(r["value_si"])


def written(pid):
    return kin[pid]["value_as_written"]


# ----------------------------------------------------------------------------- the parameter table
kinds = {}
for r in kin.values():
    kinds[r["kind"]] = kinds.get(r["kind"], 0) + 1
integer("kin.rows", len(kin), KIN)
integer("kin.sources", len({(r["pmid"], r["doi"]) for r in kin.values() if r["pmid"] or r["doi"]}), KIN)
integer("kin.numeric", kinds["numeric"], KIN)
integer("kin.derived", kinds["derived"], KIN)
integer("kin.qualitative", kinds["qualitative_constraint"], KIN)
integer("kin.gap", kinds["declared_gap"], KIN)
must(len(kin) == 67 and kinds["declared_gap"] == 1, "the parameter table no longer has 67 rows with one declared gap")

# ----------------------------------------------------------------------------- Alzheimer's arm (scripts/12)
clr = ode["ad_clearance_vs_production"]
dose = ode["mimic_dose_vs_measured_knockdown"]
src12 = ODE
for k, pid in dict(prod_ctrl="K001", prod_ad="K002", clear_ctrl="K003", clear_ad="K004").items():
    put(f"ad.{k}", written(pid), KIN)
num("ad.clear_deficit", clr["clearance_deficit_percent"], 1, src12)
num("ad.prod_diff", clr["production_difference_percent"], 1, src12)
num("ad.ratio", clr["abeta_ratio_AD_over_control"], 2, src12)
num("ad.ratio4", clr["abeta_ratio_AD_over_control"], 4, src12)
# EN/PT: the two factors of the pool ratio, written out so the text can show that clearance carries it
f_prod = v("K002") / v("K001")
f_clear = v("K003") / v("K004")
must(abs(f_prod * f_clear - clr["abeta_ratio_AD_over_control"]) < 1e-7, "production and clearance factors do not multiply to the ratio")
num("ad.factor_prod", f_prod, 3, "arithmetic on K001, K002")
num("ad.factor_clear", f_clear, 3, "arithmetic on K003, K004")
pct("ad.kappa", dose["required_BACE1_knockdown"], 1, src12)
pct("ad.measured_kd", dose["measured_BACE1_knockdown_K047"], 0, src12)
pct("ad.kappa_over_measured", dose["required_over_measured_knockdown"], 0, src12)
lo, hi = dose["mimic_fold_to_offset_clearance"]
num("ad.fold_lo", lo, 2, src12)
num("ad.fold_hi", hi, 2, src12)
num("ad.fold_mid", clr["mimic_fold_needed"], 2, src12)
num("ad.fold_proportional", 1.0 / (1.0 - dose["required_BACE1_knockdown"]), 2, "arithmetic on the required knockdown")
lo, hi = dose["mimic_fold_to_reproduce_measured_knockdown"]
num("ad.fold_measured_lo", lo, 1, src12)
num("ad.fold_measured_hi", hi, 1, src12)
_sup = str.maketrans("-0123456789", "\u207b\u2070\u00b9\u00b2\u00b3\u2074\u2075\u2076\u2077\u2078\u2079")


def sci(x):
    """EN/PT: one significant figure, written 3 x 10-10 with a superscript exponent."""
    e = int(math.floor(math.log10(abs(x))))
    m = int(round(x / 10 ** e))
    if m == 10:
        m, e = 1, e + 1
    return f"{m} \u00d7 10{str(e).translate(_sup)}"


put("ad.ode_check", sci(clr["mimic_fold_ode_check_max_relative_error"]), src12)
rs = tgt["repression_strength"]
num("ad.rho_lo", rs["AD"]["rho_scan_low"], 1, TGT_J)
num("ad.rho_mid", rs["AD"]["rho_scan_mid"], 0, TGT_J)
integer("ad.rho_hi", rs["AD"]["rho_scan_high"], TGT_J)
st = ode["enzyme_substrate_stoichiometry"]
integer("ad.bace1_copies", st["BACE1_copies_per_bouton"], src12)
integer("ad.app_copies", st["APP_copies_per_bouton"], src12)
integer("ad.stoich", st["APP_per_BACE1"], src12)
nuc = tgt["nucleation_scaling"]
must(nuc["order_primary_nucleation"] == nuc["order_secondary_nucleation"] == 2.0,
     "the two Abeta42 nucleation orders are no longer both 2; the sentence that quotes one number for both must change")
num("ad.nuc_order", nuc["order_primary_nucleation"], 0, TGT_J)
num("ad.nuc_ratio", nuc["primary_nucleation_rate_ratio_AD_over_control"], 3, TGT_J)
num("ad.nuc_ratio1", nuc["primary_nucleation_rate_ratio_AD_over_control"], 1, TGT_J)
pct("ad.nuc_cut", nuc["primary_nucleation_rate_reduction_after_offset"], 1, TGT_J)
loads = ode["human_abeta_aggregate_load"]
num("ad.mstar_nM", loads["M_star_nM [K014]"], 0, src12)
num("ad.load_ctrl_x", loads["control median [K032]"]["multiples_of_M_star"], 0, src12)
num("ad.load_ad_x", loads["AD median [K035]"]["multiples_of_M_star"], 0, src12)
num("ad.load_fold", loads["AD_over_control_median_fold"], 0, src12)
# scans
ok = [r for r in sens if r["verdict"] == "AD_above_control"]
must(len(sens) == 18 and len(ok) == 18, "the free-parameter scan no longer has 18 evaluable runs")
ratios = [float(r["abeta_AD_over_control"]) for r in ok]
must(max(ratios) - min(ratios) < 1e-6, "the scanned AD/control ratio is no longer constant")
integer("ad.scan_n", len(sens), SENS)
num("ad.scan_ratio", sum(ratios) / len(ratios), 4, SENS)
for lab, rho_ in (("rho1", 1.0), ("rho01", 0.1)):
    num(f"ad.fold_{lab}", 1.0 + dose["required_BACE1_knockdown"] / (1.0 - dose["required_BACE1_knockdown"]) * (1.0 + rho_) / rho_, 1,
        "closed form on the required knockdown at the stated rho")
pct("ad.bace1_subset", v("K049"), 0, KIN)
put("ad.k_repress_range", "0.1 to 3", ODE)
put("ad.k_translate_range", "0.2 to 5", ODE)
num("ad.d_bace1_mrna", v("K068"), 4, KIN)
num("ad.hl_bace1_mrna", LN2 / v("K068"), 1, "arithmetic on K068")
num("ad.hl_bace1_cell", LN2 / v("K025"), 0, "arithmetic on K025")
put("ad.bace1_hek_hl", written("K024"), KIN)

# ----------------------------------------------------------------------------- Parkinson's arm (scripts/12)
sat = ode["alpha_synuclein_saturation"]
chain = ode["mir7_knockdown_to_elongation"]
num("pd.conc", sat["alpha_synuclein_uM_in_bouton"], 1, src12)
num("pd.mhalf_lo", min(p["m_half_uM"] for p in sat["points"]), 0, src12)
num("pd.mhalf_hi", max(p["m_half_uM"] for p in sat["points"]), 0, src12)
pct("pd.frac_lo", sat["fraction_of_maximal_range"][0], 0, src12)
pct("pd.frac_hi", sat["fraction_of_maximal_range"][1], 0, src12)
num("pd.elast_lo", sat["elasticity_range"][0], 2, src12)
num("pd.elast_hi", sat["elasticity_range"][1], 2, src12)
must(sat["below_half_saturation"], "alpha-synuclein no longer sits below half-saturation")
for lab, pid in (("a", "K058"), ("b", "K063")):
    kd = v(pid)
    cases = [c for c in chain["cases"] if abs(c["knockdown"] - kd) < 1e-12]
    must(len(cases) == 2, f"expected two m_half cases for {pid}")
    slows = [c["elongation_rate_reduction"] for c in cases]
    pct(f"pd.kd_{lab}", kd, 0, KIN)
    pct(f"pd.slow_{lab}_lo", min(slows), 1, src12)
    pct(f"pd.slow_{lab}_hi", max(slows), 1, src12)
    pct(f"pd.transmit_{lab}_lo", min(slows) / kd, 0, src12)
    pct(f"pd.transmit_{lab}_hi", max(slows) / kd, 0, src12)
must(chain["less_than_proportional_everywhere"], "the elongation slowdown is no longer less than proportional")
ad_ = chain["additivity"]
pct("pd.pair_measured", ad_["pair_measured"], 0, src12)
pct("pd.pair_independent", ad_["pair_if_independent"], 0, src12)
pct("pd.mir7_alone_kd", ad_["miR7_alone"], 0, src12)
pct("pd.mir153_alone_kd", ad_["miR153_alone"], 0, src12)
pct("pd.mir7_mrna_kd", v("K061"), 0, KIN)
pct("pd.pair_mrna_kd", v("K062"), 0, KIN)
pct("pd.age_protein", v("K027"), 0, KIN)
pct("pd.age_mrna", abs(v("K028")), 0, KIN)
put("pd.mir7_copies", written("K022"), KIN)
put("pd.cyrano_fold", written("K023"), KIN)
put("pd.mrna_hl", written("K066"), KIN)
put("pd.mrna_hl_1", rnd(float(written("K066")), 1), KIN)
put("pd.mhalf_hi_1", written("K009"), KIN)
put("pd.asyn_hl", written("K026"), KIN)
put("pd.proteome_hl_d", written("K029"), KIN)
num("pd.d_snca_mrna", v("K066"), 3, KIN)
num("pd.rho_lo", rs["PD"]["rho_scan_low"], 2, TGT_J)
num("pd.rho_mid", rs["PD"]["rho_scan_mid"], 1, TGT_J)
integer("pd.rho_hi", rs["PD"]["rho_scan_high"], TGT_J)
num("pd.rho_floor", rs["PD"]["rho_floor_K065"], 2, TGT_J)
must(rs["PD"]["floor_below_scan"], "the K065 floor on the repression strength no longer lies below the declared scan")
pct("pd.k065_increase", v("K065"), 0, KIN)
for lab, key in (("a", "miR-7 alone, SNCA construct with 3'UTR [K058]"), ("b", "miR-7 + miR-153, cortical neurons [K063]")):
    t = rs["PD"]["targets"][key]
    num(f"pd.fold_{lab}_prop", t["proportional_limit_fold"], 2, TGT_J)
    num(f"pd.fold_{lab}_lo", t["fold_at_scan_high"], 2, TGT_J)
    num(f"pd.fold_{lab}_hi", t["fold_at_scan_low"], 2, TGT_J)
    num(f"pd.fold_{lab}_floor", t["fold_at_floor"], 2, TGT_J)
# gene-dosage arithmetic: a duplication carries three copies and a triplication four, against two
num("pd.dup_cancel", (1.0 - 2.0 / 3.0) * 100.0, 0, "arithmetic: three gene copies against two")
num("pd.trip_cancel", (1.0 - 2.0 / 4.0) * 100.0, 0, "arithmetic: four gene copies against two")

# ----------------------------------------------------------------------------- turnover (scripts/12 and 17)
wash = ode["mimic_washout"]
labels = {"miR-7 (1.7 h, K020)": "m7", "miR-7 upper bound (5 h, K021)": "m7ub", "miR-29b (7 h, K017)": "b",
          "miR-29c (10.6 h, K018)": "c", "median miRNA (34 h, K016)": "med"}
for lab, tag in labels.items():
    w = wash[lab]
    put(f"turn.{tag}.hl", hl_fmt(w["half_life_hours"]), src12)
    num(f"turn.{tag}.washout_h", w["hours_to_return_to_baseline"], 1, src12)
    num(f"turn.{tag}.washout_d", w["days_to_return_to_baseline"], 1, src12)
dd = dos["daily_dosing_comparison"]
dkeys = {"miR-7": "m7", "miR-7 upper bound": "m7ub", "miR-29b": "b", "miR-29c": "c"}
for name, tag in dkeys.items():
    d_ = dd[name]
    num(f"turn.{tag}.ptm", d_["peak_over_average_daily"], 2, DOS_J)
    num(f"turn.{tag}.penalty", d_["penalty_versus_reference"], 1, DOS_J)
    num(f"turn.{tag}.interval_h", d_["interval_matching_reference_penalty_hours"], 1, DOS_J)
    num(f"turn.{tag}.stab", d_["fold_stabilisation_required"], 1, DOS_J)
    num(f"turn.{tag}.hl_req", d_["half_life_required_for_daily_dosing_hours"], 0, DOS_J)
num("turn.med.ptm", dd["miR-7"]["reference_peak_over_average_daily"], 2, DOS_J)
for r in dos_rows:
    if float(r["dosing_interval_hours"]) == 24.0:
        tag = {"miR-7": "m7", "miR-7 upper bound": "m7ub", "miR-29b": "b", "miR-29c": "c", "median miRNA": "med"}[r["species"]]
        pct(f"turn.{tag}.above_half", r["fraction_of_interval_above_half_peak"], 1, DOS_C)
num("turn.ratio_hl_m7_med", float(wash["median miRNA (34 h, K016)"]["half_life_hours"]) / float(wash["miR-7 (1.7 h, K020)"]["half_life_hours"]), 0,
    "arithmetic on K016, K020")
put("turn.avg_hl", written("K015"), KIN)
put("turn.med_hl", written("K016"), KIN)

# ----------------------------------------------------------------------------- the dose at the target (scripts/36)
must(tgt["scenarios"] == len(rows) == 330, "the scenario table no longer has 330 rows")
integer("dose.scenarios", len(rows), TGT_C)
integer("dose.unreachable", tgt["scenarios_unreachable"], TGT_J)
integer("dose.cap", tgt["dose_cap_in_baseline_pools"], TGT_J)
for k_, c_ in tgt["verification"].items():
    must(c_["passed"], f"verification {k_} did not pass")
integer("dose.verifications", len(tgt["verification"]), TGT_J)
num("dose.verif_worst", max(c_["max_abs_error"] / c_["tolerance"] for c_ in tgt["verification"].values()), 3,
    "worst error over tolerance in " + TGT_J)

PRIMARY = ("BACE1 in", "alpha-syn")
SP_TAG = {"miR-7": "m7", "miR-7 upper bound": "m7ub", "miR-29b": "b", "miR-29c": "c", "median miRNA": "med"}


def pick(axis, rho_case, species, interval, kappa=None, protein=PRIMARY):
    out = [r for r in rows if r["axis"] == axis and r["rho_case"] == rho_case and r["species"] == species
           and float(r["interval_h"]) == interval and r["protein_case"].startswith(protein)
           and (kappa is None or abs(float(r["target_knockdown"]) - kappa) < 1e-9)]
    must(len(out) == 1, f"expected one row for {axis}/{rho_case}/{species}/{interval}/{kappa}, found {len(out)}")
    return out[0]


def cases(axis, species, interval, kappa=None, only=None, protein=PRIMARY):
    names = [c for c in dict.fromkeys(r["rho_case"] for r in rows if r["axis"] == axis)
             if only is None or c in only]
    return [pick(axis, c, species, interval, kappa, protein) for c in names]


def span(key, items, field, f, src=TGT_C):
    xs = [float(i[field]) for i in items if i[field] != ""]
    must(xs, f"no values for {key}")
    put(f"{key}_lo", f(min(xs)), src)
    put(f"{key}_hi", f(max(xs)), src)


kap_ad = dose["required_BACE1_knockdown"]
kap_a, kap_b = v("K058"), v("K063")
SCAN = ("scan low", "scan midpoint", "scan high")
INTERVALS = (8.0, 12.0, 24.0, 48.0, 168.0)

# AD: pool-level mimic, three species, four intervals, over the three scan strengths
for sp in ("miR-29b", "miR-29c", "median miRNA"):
    tag = SP_TAG[sp]
    for T_ in INTERVALS:
        its = cases("AD", sp, T_, kap_ad)
        must(all(i["reachable"] == "True" for i in its), f"AD {sp} {T_} h unreachable")
        span(f"dose.AD.{tag}.T{int(T_)}.peak", its, "peak_pool_over_baseline", peak)
        span(f"dose.AD.{tag}.T{int(T_)}.eff", its, "efficiency", lambda x: rnd(x, 2))
        span(f"dose.AD.{tag}.T{int(T_)}.swing", its, "protein_ripple", lambda x: rnd(100 * x, 0))
        span(f"dose.AD.{tag}.T{int(T_)}.abswing", its, "abeta_ripple", lambda x: rnd(100 * x, 0))
        span(f"dose.AD.{tag}.T{int(T_)}.trough", its, "trough_pool_over_baseline", lambda x: rnd(x, 2))

# PD: the K065 floor and the scan, two targets, five intervals
for sp in ("miR-7", "miR-7 upper bound", "median miRNA"):
    tag = SP_TAG[sp]
    for lab, kap in (("a", kap_a), ("b", kap_b)):
        for T_ in INTERVALS:
            k065 = pick("PD", "K065 lower bound", sp, T_, kap)
            sc = cases("PD", sp, T_, kap, only=SCAN)
            base = f"dose.PD.{tag}.{lab}.T{int(T_)}"
            put(f"{base}.reach_floor", "yes" if k065["reachable"] == "True" else "no", TGT_C)
            put(f"{base}.reach_scan", "yes" if all(i["reachable"] == "True" for i in sc) else
                ("no" if all(i["reachable"] != "True" for i in sc) else "some"), TGT_C)
            if k065["reachable"] == "True":
                put(f"{base}.peak_floor", peak(k065["peak_pool_over_baseline"]), TGT_C)
                put(f"{base}.eff_floor", rnd(k065["efficiency"], 2), TGT_C)
                put(f"{base}.swing_floor", rnd(100 * float(k065["protein_ripple"]), 0), TGT_C)
            else:
                put(f"{base}.reached_floor", rnd(100 * float(k065["knockdown_reached"]), 0), TGT_C)
            reach = [i for i in sc if i["reachable"] == "True"]
            if reach:
                span(f"{base}.peak_scan", reach, "peak_pool_over_baseline", peak)
                span(f"{base}.eff_scan", reach, "efficiency", lambda x: rnd(x, 2))
                span(f"{base}.swing_scan", reach, "protein_ripple", lambda x: rnd(100 * x, 0))
            if len(reach) < len(sc):
                un = [i for i in sc if i["reachable"] != "True"]
                span(f"{base}.reached_scan", un, "knockdown_reached", lambda x: rnd(100 * x, 0))

# the sentences about weekly miR-7 dosing rest on this pattern
for lab in ("a", "b"):
    b = f"dose.PD.m7.{lab}.T168"
    must(N[f"{b}.reach_floor"] == "no" and N[f"{b}.reach_scan"] == "no",
         f"weekly miR-7 dosing is no longer out of reach at every repression strength (target {lab})")
# daily dosing of a median-stability miRNA is the linear case: the closed form suffices
for ax_, sp_, kap_list in (("AD", "median miRNA", [kap_ad]), ("PD", "median miRNA", [kap_a, kap_b])):
    for kap in kap_list:
        for r in cases(ax_, sp_, 24.0, kap):
            must(float(r["efficiency"]) > 0.99, f"daily dosing of a median-stability miRNA is no longer in the linear regime ({ax_} {r['rho_case']})")
# the dose does not depend on the protein half-life
by = {}
for r in rows:
    by.setdefault((r["axis"], r["rho_case"], r["species"], r["interval_h"], r["target"]), []).append(r)
for k_, g_ in by.items():
    d_ = [float(x["dose"]) for x in g_ if x["dose"] != ""]
    must(len(d_) in (0, len(g_)) and (not d_ or max(d_) - min(d_) <= 1e-7 * max(d_)),
         f"the dose depends on the protein half-life in {k_}")
put("dose.protein_independent", "yes", TGT_C)

# protein half-life sensitivity: swing at the cell value and at the in vivo brain median
for tag, axis, sp, rho_case, kap in (("ad_b", "AD", "miR-29b", "scan midpoint", kap_ad),
                                     ("pd_m7", "PD", "miR-7", "K065 lower bound", kap_a)):
    cell_ = pick(axis, rho_case, sp, 24.0, kap)
    vivo = pick(axis, rho_case, sp, 24.0, kap, protein=("brain proteome",))
    pct(f"dose.swing_cell.{tag}", cell_["protein_ripple"], 1, TGT_C)
    pct(f"dose.swing_vivo.{tag}", vivo["protein_ripple"], 1, TGT_C)
    num(f"dose.hl_cell.{tag}", cell_["protein_half_life_h"], 0, TGT_C)
    num(f"dose.hl_vivo.{tag}", float(vivo["protein_half_life_h"]) / 24.0, 1, TGT_C)
# time for the protein to approach 90% of its new mean: ln(10) / d_p
num("onset.bace1_cell_d", math.log(10.0) / v("K025") / 24.0, 1, "arithmetic on K025: ln(10) / d_p")
num("onset.asyn_cell_d", math.log(10.0) / v("K026") / 24.0, 1, "arithmetic on K026: ln(10) / d_p")
num("onset.vivo_d", math.log(10.0) / v("K029") / 24.0, 0, "arithmetic on K029: ln(10) / d_p")

# elongation in the periodic regimen against the steady-state chain
r = pick("PD", "K065 lower bound", "median miRNA", 24.0, kap_a)
pct("dose.elong_periodic_a", r["elongation_reduction_m49_8"], 1, TGT_C)
ss = [c for c in chain["cases"] if abs(c["knockdown"] - kap_a) < 1e-12 and abs(c["m_half_uM"] - 49.8) < 1e-9][0]
must(abs(float(r["elongation_reduction_m49_8"]) - ss["elongation_rate_reduction"]) < 1e-4,
     "the periodic elongation reduction no longer matches the steady-state chain")

# the rho sweep: the smallest daily peak over all rho, a bound that holds whatever rho is
sweep = tgt["rho_sweep"]
for e in sweep["summary"]:
    lab = "ad" if e["axis"] == "AD" else ("a" if abs(e["target_knockdown"] - kap_a) < 1e-12 else "b")
    base = f"sweep.{e['axis']}.{SP_TAG[e['species']]}.{lab}"
    put(f"{base}.min", peak(e["min_peak_pool_over_baseline"]), TGT_J)
    put(f"{base}.min_lb", lower_bound(e["min_peak_pool_over_baseline"]), TGT_J)
    r_ = e["rho_at_min"]
    put(f"{base}.rho_at_min", (f"10{str(int(round(math.log10(r_)))).translate(_sup)}" if r_ >= 1000 else f"{r_:.2g}"), TGT_J)
    put(f"{base}.low", peak(e["peak_at_lowest_rho"]), TGT_J)
    put(f"{base}.high", peak(e["peak_at_highest_rho"]), TGT_J)
    must(e["unreachable_points"] == 0, f"the sweep has unreachable points for {base}")
num("sweep.rho_min", sweep["rho_min"], 2, TGT_J)
integer("sweep.rho_max", sweep["rho_max"], TGT_J)
# the sentences that quote one bound for the miR-29 mimics rest on the bound being the strong-repression limit
for sp_ in ("b", "c", "med"):
    must(abs(float(N[f"sweep.AD.{sp_}.ad.min"]) - float(N[f"sweep.AD.{sp_}.ad.high"])) < 0.051,
         f"the smallest AD peak for {sp_} is no longer the strong-repression limit")
must(float(N["sweep.PD.m7.a.min"]) > 5 * float(N["sweep.PD.med.a.min"]),
     "the miR-7 bound is no longer more than five times the median-stability bound")
_m7 = [e for e in sweep["summary"] if e["axis"] == "PD" and e["species"] == "miR-7" and abs(e["target_knockdown"] - kap_a) < 1e-12][0]
_md = [e for e in sweep["summary"] if e["axis"] == "PD" and e["species"] == "median miRNA" and abs(e["target_knockdown"] - kap_a) < 1e-12][0]
num("sweep.PD.ratio_m7_med_a", _m7["min_peak_pool_over_baseline"] / _md["min_peak_pool_over_baseline"], 0, "arithmetic on two bounds of " + TGT_J)

# absolute scale for miR-7: the model's baseline pool taken as the 40 copies per neuron of K022
c40 = v("K022")
for lab, kap in (("a", kap_a), ("b", kap_b)):
    pks = [float(i["peak_pool_over_baseline"]) for i in cases("PD", "miR-7", 24.0, kap)]
    integer(f"abs.peak_copies_{lab}_lo", min(pks) * c40, TGT_C)
    integer(f"abs.peak_copies_{lab}_hi", max(pks) * c40, TGT_C)
integer("abs.baseline_copies", c40, KIN)
integer("abs.cyrano_copies", c40 * v("K023"), "arithmetic on K022, K023")
must(min(float(i["peak_pool_over_baseline"]) for i in cases("PD", "miR-7", 24.0, kap_b)) > v("K023"),
     "the daily peak for the 43% target no longer exceeds the Cyrano-knockout fold")

# ----------------------------------------------------------------------------- write
payload = dict(N)
payload["_sources"] = SRC
json.dump(payload, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"EN/PT -> {OUT}  ({len(N)} values)")
