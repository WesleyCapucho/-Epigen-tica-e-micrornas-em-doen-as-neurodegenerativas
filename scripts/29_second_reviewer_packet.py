#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EN | Builds the workbook for the independent second reviewer and, once it has been filled
     in, computes agreement with the first reviewer.

     python scripts/29_second_reviewer_packet.py build
     python scripts/29_second_reviewer_packet.py agree <filled_workbook.xlsx>

     build  writes data/second_reviewer/second_reviewer_packet.xlsx with four sheets:
            instructions; A_screening (a seeded random sample of screened records, decisions
            hidden); B_quadas2 (every pooled study, first reviewer's judgements hidden);
            C_extraction (every pooled estimate with its stored value and source sentence,
            for verification against the article).
     agree  reads the filled workbook and writes results/tables/second_reviewer_agreement.csv
            with percent agreement and Cohen's kappa for screening and for each QUADAS-2
            domain, and the share of extracted fields the second reviewer corrected.

PT | Monta a planilha do segundo revisor independente e, depois de preenchida, calcula a
     concordancia com o primeiro revisor.
     build  grava data/second_reviewer/second_reviewer_packet.xlsx com quatro abas:
            instrucoes; A_screening (amostra aleatoria com semente, decisoes ocultas);
            B_quadas2 (todos os estudos agregados, julgamentos do primeiro revisor ocultos);
            C_extraction (toda estimativa agregada com o valor guardado e a frase de origem,
            para conferencia contra o artigo).
     agree  le a planilha preenchida e grava results/tables/second_reviewer_agreement.csv
            com concordancia percentual e kappa de Cohen para a triagem e para cada dominio
            do QUADAS-2, e a fracao dos campos extraidos que o segundo revisor corrigiu.
"""

import csv
import json
import os
import random
import sys

from openpyxl import Workbook, load_workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter

SEED = 20260928
N_SCREEN = 120
DECISIONS = "data/raw/systematic_review_2026/screening_decisions.csv"
CORPUS = "data/raw/systematic_review_2026/screening_corpus.json"
EXTRACTION = "data/extracted/diagnostic_accuracy_extraction.csv"
SELECTION = "results/tables/one_estimate_per_study_selection_audit.csv"
QUADAS = "results/tables/quadas2_assessment.csv"
OUT_DIR = "data/second_reviewer"
PACKET = os.path.join(OUT_DIR, "second_reviewer_packet.xlsx")
AGREE = "results/tables/second_reviewer_agreement.csv"

QDOMAINS = ["rob_patient_selection", "rob_index_test", "rob_reference_standard", "rob_flow_timing"]
QLABEL = {"rob_patient_selection": "Patient selection", "rob_index_test": "Index test",
          "rob_reference_standard": "Reference standard", "rob_flow_timing": "Flow and timing"}
EXTRACT_FIELDS = ["n_cases", "n_controls", "auc", "auc_ci_low", "auc_ci_high", "sensitivity",
                  "specificity", "biofluid", "cohort_stage"]

INSTRUCTIONS = [
    "Second reviewer packet: circulating microRNAs in Alzheimer's and Parkinson's disease",
    "",
    "Work independently. Do not open the first reviewer's files while filling sheets A and B.",
    "",
    "Sheet A_screening. For each record read the title and abstract only and fill the yellow",
    "columns: (1) is the record a primary study, or a review/meta-analysis/editorial/other",
    "secondary item; (2) does the abstract report an AUC, a sensitivity or a specificity.",
    "Use the values 'primary' or 'secondary' in column (1) and 'yes' or 'no' in column (2).",
    "",
    "Sheet B_quadas2. For each study read the full text and rate the four QUADAS-2 risk-of-bias",
    "domains as 'low', 'unclear' or 'high' using the published QUADAS-2 signalling questions",
    "(Whiting et al. 2011). Add a short reason. Ratings made without the first reviewer's",
    "judgements are what the agreement statistic needs.",
    "",
    "Sheet C_extraction. Each row is one stored estimate with the sentence it was read from.",
    "Check every stored value against the article. In the yellow column 'correction' write the",
    "correct value for any field that is wrong (field=value, separated by semicolons), and leave",
    "it empty when everything agrees. Add a comment in 'reviewer_note' if the sentence does not",
    "support a value.",
    "",
    "Return the workbook unchanged in structure. The first reviewer then runs:",
    "    python scripts/29_second_reviewer_packet.py agree <returned_file.xlsx>",
]


def read_csv(path):
    with open(path, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def style_sheet(ws, widths, yellow_cols):
    head = PatternFill("solid", fgColor="DDDDDD")
    yellow = PatternFill("solid", fgColor="FFF2B3")
    for c in ws[1]:
        c.font = Font(bold=True)
        c.fill = head
    for i, w in enumerate(widths, 1):
        ws.column_dimensions[get_column_letter(i)].width = w
    for row in ws.iter_rows(min_row=2):
        for c in row:
            c.alignment = Alignment(wrap_text=True, vertical="top")
        for idx in yellow_cols:
            row[idx].fill = yellow
    ws.freeze_panes = "A2"


def build():
    os.makedirs(OUT_DIR, exist_ok=True)
    decisions = read_csv(DECISIONS)
    corpus = json.load(open(CORPUS, encoding="utf-8"))
    rng = random.Random(SEED)
    sample = rng.sample(decisions, min(N_SCREEN, len(decisions)))

    wb = Workbook()
    ws = wb.active
    ws.title = "Instructions"
    for i, line in enumerate(INSTRUCTIONS, 1):
        ws.cell(row=i, column=1, value=line)
    ws.column_dimensions["A"].width = 110

    ws = wb.create_sheet("A_screening")
    ws.append(["record_key", "year", "title", "abstract", "record_type (primary/secondary)",
               "abstract_reports_accuracy (yes/no)", "reviewer_note"])
    for r in sample:
        key = r["pmid"] or r["doi"]
        rec = corpus.get(key) or {}
        ws.append([key, r["year"], r["title"], rec.get("abstract", "") if isinstance(rec, dict) else "",
                   "", "", ""])
    style_sheet(ws, [22, 7, 60, 100, 18, 18, 30], [4, 5, 6])

    ws = wb.create_sheet("B_quadas2")
    ws.append(["study_id", "first_author", "year", "disease"]
              + [f"{QLABEL[d]} (low/unclear/high)" for d in QDOMAINS]
              + ["reasons and reviewer_note"])
    for r in read_csv(QUADAS):
        ws.append([r["study_id"], r["first_author"], r["year"], r["disease"]] + [""] * (len(QDOMAINS) + 1))
    style_sheet(ws, [26, 18, 7, 8, 18, 18, 18, 18, 60], [4, 5, 6, 7, 8])

    ws = wb.create_sheet("C_extraction")
    ws.append(["record_id", "study_id", "first_author", "year", "marker"] + EXTRACT_FIELDS
              + ["verbatim_quote", "correction (field=value; ...)", "reviewer_note"])
    sel = {(r["first_author"], r["year"], r["selected_marker"]) for r in read_csv(SELECTION)}
    for r in read_csv(EXTRACTION):
        if r["eligible_primary_pool"] != "yes":
            continue
        sid = r["pmid"] or r["doi"]
        ws.append([r["record_id"], sid, r["first_author"], r["year"], r["marker"]]
                  + [r[f] for f in EXTRACT_FIELDS] + [r["verbatim_quote"], "", ""])
    style_sheet(ws, [9, 24, 16, 6, 24] + [10] * len(EXTRACT_FIELDS) + [70, 30, 30],
                [len(EXTRACT_FIELDS) + 6, len(EXTRACT_FIELDS) + 7])
    wb.save(PACKET)
    print(f"wrote {PACKET}: {len(sample)} screening records, "
          f"{len(read_csv(QUADAS))} studies for QUADAS-2, "
          f"{ws.max_row - 1} estimates for extraction")


def kappa(a, b):
    labels = sorted(set(a) | set(b))
    n = len(a)
    if n == 0:
        return float("nan")
    po = sum(x == y for x, y in zip(a, b)) / n
    pe = sum((a.count(l) / n) * (b.count(l) / n) for l in labels)
    return float("nan") if pe == 1 else (po - pe) / (1 - pe)


def agree(path):
    wb = load_workbook(path, data_only=True)
    rows = []

    # screening
    dec = {(r["pmid"] or r["doi"]): r for r in read_csv(DECISIONS)}
    a1, a2, b1, b2 = [], [], [], []
    for r in wb["A_screening"].iter_rows(min_row=2, values_only=True):
        key, rt, acc = r[0], (r[4] or "").strip().lower(), (r[5] or "").strip().lower()
        if not rt or not acc or key not in dec:
            continue
        first = dec[key]
        a1.append("secondary" if first["is_review_or_secondary"] == "yes" else "primary")
        a2.append(rt)
        b1.append("yes" if first["carries_quantitative_accuracy"] == "yes" else "no")
        b2.append(acc)
    for name, x, y in (("screening: record type", a1, a2), ("screening: accuracy in abstract", b1, b2)):
        if x:
            rows.append([name, len(x), round(sum(i == j for i, j in zip(x, y)) / len(x), 3),
                         round(kappa(x, y), 3)])

    # QUADAS-2
    first_q = {r["study_id"]: r for r in read_csv(QUADAS)}
    for i, d in enumerate(QDOMAINS):
        x, y = [], []
        for r in wb["B_quadas2"].iter_rows(min_row=2, values_only=True):
            sid, v = r[0], (r[4 + i] or "").strip().lower()
            if v and sid in first_q:
                x.append(first_q[sid][d])
                y.append(v)
        if x:
            rows.append([f"QUADAS-2: {QLABEL[d]}", len(x),
                         round(sum(p == q for p, q in zip(x, y)) / len(x), 3), round(kappa(x, y), 3)])

    # extraction
    ws = wb["C_extraction"]
    n_rows = n_corr = n_fields = 0
    for r in ws.iter_rows(min_row=2, values_only=True):
        if r[0] is None:
            continue
        n_rows += 1
        corr = (r[len(EXTRACT_FIELDS) + 6] or "").strip()
        if corr:
            n_corr += 1
            n_fields += len([p for p in corr.split(";") if p.strip()])
    if n_rows:
        rows.append(["extraction: estimates with at least one correction", n_rows,
                     round(1 - n_corr / n_rows, 3), ""])
        rows.append(["extraction: individual fields corrected", n_rows * len(EXTRACT_FIELDS),
                     round(1 - n_fields / (n_rows * len(EXTRACT_FIELDS)), 3), ""])

    os.makedirs(os.path.dirname(AGREE), exist_ok=True)
    with open(AGREE, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["item", "n", "proportion_agreement", "cohens_kappa"])
        w.writerows(rows)
    for r in rows:
        print(r)
    print(f"wrote {AGREE}")


if __name__ == "__main__":
    if len(sys.argv) >= 2 and sys.argv[1] == "build":
        build()
    elif len(sys.argv) >= 3 and sys.argv[1] == "agree":
        agree(sys.argv[2])
    else:
        sys.exit(__doc__)
