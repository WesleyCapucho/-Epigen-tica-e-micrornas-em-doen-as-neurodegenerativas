#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EN | Single, shared, pre-specified, AUC-blind priority rule for picking one
     estimate per study, used identically by every analysis in this review
     that needs a one-estimate-per-study reduction: the primary AUC
     meta-analysis (05_meta_analysis.py) and the bivariate sensitivity/
     specificity synthesis (15_bivariate_srocc.py). Both import this module
     rather than keeping their own selection logic, so the two syntheses are
     guaranteed to describe the same representative estimate per study by
     construction, not by two independently maintained rules that could
     silently drift apart (as they had before this module existed: 05 used a
     fixed-effect within-study combination and 15 picked the estimate closest
     to each study's median AUC, an AUC-dependent choice).
PT | Regra de prioridade unica, compartilhada, pre-especificada e cega a AUC
     para escolher uma estimativa por estudo, usada identicamente por toda
     analise desta revisao que precisa de uma reducao uma-estimativa-por-
     estudo: a meta-analise primaria de AUC (05_meta_analysis.py) e a sintese
     bivariada de sensibilidade/especificidade (15_bivariate_srocc.py). As
     duas importam este modulo em vez de manter sua propria logica de
     selecao, entao as duas sinteses descrevem garantidamente a mesma
     estimativa representativa por estudo por construcao, e nao por duas
     regras mantidas independentemente que poderiam divergir em silencio
     (como antes deste modulo existir: 05 usava uma combinacao de efeito fixo
     dentro do estudo e 15 escolhia a estimativa mais proxima da mediana de
     AUC de cada estudo, uma escolha dependente da AUC).

EN | The rule, applied within each study's own candidate rows, in order,
     stopping as soon as one candidate remains: (1) prefer a row evaluated in
     an independent validation cohort (cohort_stage == "validation") over one
     derived and evaluated in the same sample; (2) prefer the study's own
     multi-microRNA panel over its component single markers; (3) prefer the
     row with the larger combined case+control sample size; (4) take the
     alphabetically first marker name, a purely nominal, content-free
     tiebreak. No step ever looks at the accuracy value itself.
PT | A regra, aplicada dentro das proprias linhas candidatas de cada estudo,
     em ordem, parando assim que resta um candidato: (1) preferir uma linha
     avaliada numa coorte de validacao independente (cohort_stage ==
     "validation") sobre uma derivada e avaliada na mesma amostra; (2)
     preferir o painel multi-miRNA do proprio estudo sobre seus marcadores
     isolados componentes; (3) preferir a linha com maior tamanho amostral
     combinado (casos+controles); (4) tomar o nome do marcador
     alfabeticamente primeiro, um desempate puramente nominal, sem conteudo.
     Nenhuma etapa olha para o proprio valor de acuracia.
"""

STAGE_RANK = {"validation": 0, "cross-validated": 1, "training": 2,
              "discovery": 2, "single": 3, "unclear": 3}

# EN | Cerebrospinal-fluid biofluid codes, shared by every analysis that must
#      hold CSF out of the "circulating" primary pool - see the "Scope of the
#      primary pool" docstring in 05_meta_analysis.py.
# PT | Codigos de biofluido de liquido cefalorraquidiano, compartilhados por
#      toda analise que precisa manter o LCR fora do pool primario
#      "circulante" - ver a docstring "Scope of the primary pool" em
#      05_meta_analysis.py.
CSF_BIOFLUIDS = {"CSF", "CSF_exosome"}


def _num(x, default=0.0):
    try:
        if x is None or x == "":
            return default
        return float(x)
    except (TypeError, ValueError):
        return default


def select_one_per_study(candidates, panel_preference=True):
    """
    EN | candidates: list of dict-like rows, all belonging to ONE study, each
         with 'cohort_stage', 'marker_type', 'n_cases', 'n_controls', 'marker'
         keys. Returns (selected_row, reason_string, n_candidates). Raises if
         candidates is empty. panel_preference=False drops step (2), giving
         the alternative, marker-type-neutral rule used only as a sensitivity
         analysis (scripts/26_robustness_analyses.py).
    PT | candidates: lista de linhas tipo-dict, todas de UM estudo, cada uma
         com as chaves 'cohort_stage', 'marker_type', 'n_cases', 'n_controls',
         'marker'. Retorna (linha_selecionada, motivo, n_candidatos). Lanca
         excecao se candidates estiver vazia. panel_preference=False remove a
         etapa (2), dando a regra alternativa neutra quanto ao tipo de marcador,
         usada apenas como analise de sensibilidade
         (scripts/26_robustness_analyses.py).
    """
    rows = list(candidates)
    if not rows:
        raise ValueError("select_one_per_study: no candidate rows")
    if len(rows) == 1:
        return rows[0], "only qualifying estimate | unica estimativa qualificada", 1

    n0 = len(rows)
    reason_parts = []

    best_stage = min(STAGE_RANK.get(r.get("cohort_stage"), 3) for r in rows)
    rows = [r for r in rows if STAGE_RANK.get(r.get("cohort_stage"), 3) == best_stage]
    if best_stage == 0:
        reason_parts.append("evaluated in a separate validation sample | avaliada em amostra de validacao separada")

    if len(rows) > 1 and panel_preference:
        panel_ranks = [0 if r.get("marker_type") == "multi_miRNA_panel" else 1 for r in rows]
        best_panel = min(panel_ranks)
        if best_panel == 0 and any(p == 1 for p in panel_ranks):
            reason_parts.append("own multi-miRNA panel preferred over component markers | "
                                 "painel multi-miRNA proprio preferido sobre marcadores componentes")
        rows = [r for r, p in zip(rows, panel_ranks) if p == best_panel]

    if len(rows) > 1:
        totals = [_num(r.get("n_cases")) + _num(r.get("n_controls")) for r in rows]
        best_n = max(totals)
        if len(set(totals)) > 1:
            reason_parts.append("larger combined case+control sample size | "
                                 "maior tamanho amostral combinado casos+controles")
        rows = [r for r, tot in zip(rows, totals) if tot == best_n]

    if len(rows) > 1:
        rows = sorted(rows, key=lambda r: str(r.get("marker", "")))
        reason_parts.append("alphabetically first marker name (nominal tiebreak) | "
                             "nome do marcador alfabeticamente primeiro (desempate nominal)")

    reason = "; ".join(reason_parts) if reason_parts else \
        "alphabetically first marker name (nominal tiebreak) | " \
        "nome do marcador alfabeticamente primeiro (desempate nominal)"
    return rows[0], reason, n0


def select_one_per_study_grouped(rows, study_id_fn, panel_preference=True):
    """EN/PT: groups `rows` (dict-likes) by study_id_fn(row) and applies
    select_one_per_study to each group. Returns an OrderedDict-like list of
    (study_id, selected_row, reason, n_candidates)."""
    from collections import OrderedDict
    groups = OrderedDict()
    for r in rows:
        groups.setdefault(study_id_fn(r), []).append(r)
    out = []
    for sid, g in groups.items():
        sel, reason, n = select_one_per_study(g, panel_preference=panel_preference)
        out.append((sid, sel, reason, n))
    return out
