#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EN | Title/abstract screening of the systematic-review corpus, and the PRISMA
     counts that follow from it.
PT | Triagem por titulo/resumo do corpus da revisao sistematica e as contagens
     PRISMA dela decorrentes.

EN | Screening is deliberately rule-based and auditable: a record is set aside
     as secondary literature when its PubMed publication type says so or when
     its own text announces a review, and it is marked as carrying quantitative
     accuracy data only when the abstract states an AUC, or both a sensitivity
     and a specificity. The rules decide nothing on their own - they route
     records to full-text reading, where every extracted value is confirmed
     against the verbatim sentence of the source.
PT | A triagem e deliberadamente baseada em regras e auditavel: um registro e
     separado como literatura secundaria quando o tipo de publicacao do PubMed
     assim indica ou quando o proprio texto se anuncia como revisao, e e
     marcado como portador de dados quantitativos apenas quando o resumo
     declara uma AUC, ou sensibilidade e especificidade juntas. As regras nao
     decidem sozinhas - elas encaminham registros para leitura do texto
     completo, onde cada valor extraido e conferido contra a frase verbatim.

    python scripts/04_screening.py
"""

import csv
import json
import os
import re

IN_CORPUS = "data/raw/systematic_review_2026/screening_corpus.json"
OUT_CSV = "data/raw/systematic_review_2026/screening_decisions.csv"
OUT_FLOW = "data/processed/prisma_flow.json"

AUC_RE = re.compile(r'\b(?:AUC|area under (?:the )?(?:ROC )?curve)\b[^.]{0,80}?'
                    r'(0?\.\d{2,4}|\d{1,3}(?:\.\d+)?\s*%)', re.I)
SENS_RE = re.compile(r'\bsensitivit(?:y|ies)\b[^.]{0,60}?(\d{1,3}(?:\.\d+)?\s*%|0?\.\d{2,4})', re.I)
SPEC_RE = re.compile(r'\bspecificit(?:y|ies)\b[^.]{0,60}?(\d{1,3}(?:\.\d+)?\s*%|0?\.\d{2,4})', re.I)
SECONDARY_TYPES = {"Review", "Systematic Review", "Meta-Analysis", "Editorial",
                   "Comment", "Published Erratum", "Letter",
                   "Retracted Publication", "Retraction of Publication"}
# EN | No trailing \b here, on purpose. An earlier version ended the group with
#      \b, which made the 'meta-analys' alternative never fire: 'meta-analysis'
#      continues with 'is', so there is no boundary at that point. Two prior
#      meta-analyses reached the eligible pool because of it.
# PT | Sem \b no fim, de proposito. Uma versao anterior fechava o grupo com \b,
#      o que impedia a alternativa 'meta-analys' de disparar: 'meta-analysis'
#      segue com 'is', logo nao ha fronteira ali. Duas meta-analises previas
#      chegaram ao conjunto elegivel por causa disso.
SECONDARY_TEXT = re.compile(
    r'(systematic review|meta[-\s]?analy[sz]|narrative review|scoping review|'
    r'umbrella review|pooled analysis|\bthis review\b|\bwe review\b)', re.I)


def screen(record):
    title = record.get("Title") or record.get("title") or ""
    abstract = record.get("Abstract") or record.get("abstract") or ""
    ptypes = record.get("PublicationTypes") or ""
    if isinstance(record.get("article_types"), list):
        ptypes = "; ".join(record["article_types"])
    types = {t.strip() for t in ptypes.split(";") if t.strip()}

    secondary = bool(types & SECONDARY_TYPES) or bool(SECONDARY_TEXT.search(title + " " + abstract))
    has_auc = bool(AUC_RE.search(abstract))
    has_sens = bool(SENS_RE.search(abstract))
    has_spec = bool(SPEC_RE.search(abstract))
    return dict(is_review_or_secondary=secondary,
                abstract_reports_auc=has_auc,
                abstract_reports_sensitivity=has_sens,
                abstract_reports_specificity=has_spec,
                carries_quantitative_accuracy=has_auc or (has_sens and has_spec))


def corpus_field(rec, *names):
    """
    EN | The corpus holds two record shapes: PubMed records, where journal and
         publication date are objects, and imported database records, where they
         are plain strings. Reading one shape as the other crashed this script
         the moment a Web of Science export arrived, so the shapes are flattened
         here in one place instead of at each use.
    PT | O corpus guarda duas formas de registro: os do PubMed, em que revista e
         data sao objetos, e os importados de outras bases, em que sao strings.
         Ler uma forma como a outra quebrava este script no instante em que
         chegou uma exportacao da Web of Science, entao as formas sao achatadas
         aqui, num lugar so, e nao em cada uso.
    """
    for n in names:
        v = rec.get(n)
        if isinstance(v, dict):
            v = v.get("title") or v.get("year") or ""
        if v:
            return str(v).strip()
    return ""


def main():
    corpus = json.load(open(IN_CORPUS))

    # EN | Columns that this script cannot derive are carried forward from the
    #      committed decisions rather than recomputed. pmc_fulltext_available
    #      records whether a full text was actually fetched from PubMed Central;
    #      it is an observation, not a rule output, and overwriting it with a
    #      blank would silently destroy work. Empty means not checked.
    # PT | Colunas que este script nao consegue derivar sao trazidas das decisoes
    #      ja versionadas, em vez de recalculadas. O pmc_fulltext_available
    #      registra se um texto completo foi de fato obtido do PubMed Central; e
    #      observacao, nao saida de regra, e sobrescreve-lo com vazio destruiria
    #      trabalho em silencio. Vazio significa nao conferido.
    carried = {}
    if os.path.exists(OUT_CSV):
        with open(OUT_CSV, encoding="utf-8", newline="") as f:
            for row in csv.DictReader(f):
                carried[row["pmid"]] = row

    rows = []
    for pmid, rec in corpus.items():
        ids = rec.get("identifiers", {}) if isinstance(rec.get("identifiers"), dict) else {}
        prev = carried.get(pmid, {})
        d = screen(rec)
        types = rec.get("article_types")
        types = "; ".join(types) if isinstance(types, list) else (rec.get("PublicationTypes") or "")
        rows.append({
            "pmid": pmid,
            "doi": rec.get("DOI") or rec.get("doi") or ids.get("doi", ""),
            "pmcid": rec.get("PMC") or rec.get("pmcid") or ids.get("pmc", "") or prev.get("pmcid", ""),
            "year": corpus_field(rec, "Year", "year", "publication_date"),
            "journal": corpus_field(rec, "Journal", "journal"),
            "title": rec.get("Title") or rec.get("title", ""),
            "search_arm": rec.get("search_arm") or prev.get("search_arm", ""),
            "article_types": types or prev.get("article_types", ""),
            "is_review_or_secondary": "yes" if d["is_review_or_secondary"] else "no",
            "abstract_reports_auc": "yes" if d["abstract_reports_auc"] else "no",
            "abstract_reports_sensitivity": "yes" if d["abstract_reports_sensitivity"] else "no",
            "abstract_reports_specificity": "yes" if d["abstract_reports_specificity"] else "no",
            "carries_quantitative_accuracy": "yes" if d["carries_quantitative_accuracy"] else "no",
            "database": rec.get("database", ""),
            "pmc_fulltext_available": prev.get("pmc_fulltext_available", ""),
        })
    rows.sort(key=lambda r: r["pmid"])

    os.makedirs(os.path.dirname(OUT_CSV), exist_ok=True)
    with open(OUT_CSV, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    n = len(rows)
    prim = [r for r in rows if r["is_review_or_secondary"] == "no"]
    quant = [r for r in prim if r["carries_quantitative_accuracy"] == "yes"]
    pmc = [r for r in quant if r["pmcid"]]
    flow = {
        "records_screened": n,
        "excluded_review_or_secondary": n - len(prim),
        "primary_studies": len(prim),
        "primary_reporting_auc_or_sens_spec": len(quant),
        "of_which_carry_a_pmcid": len(pmc),
    }

    # EN | Merge, never replace. This script used to dump its five counts over
    #      data/processed/prisma_flow.json, which also holds the identification
    #      counts per database arm, the eligibility and full-text counts, and the
    #      notes recording what each correction changed - none of which this
    #      script can regenerate. One run would have destroyed all of it. The
    #      rule-derived counts now live under their own key, beside the per-arm
    #      record rather than on top of it.
    # PT | Funde, nunca substitui. Este script despejava suas cinco contagens
    #      sobre data/processed/prisma_flow.json, que tambem guarda as contagens
    #      de identificacao por braco, as de elegibilidade e texto completo, e as
    #      notas do que cada correcao mudou - nada disso ele sabe regenerar. Uma
    #      execucao teria destruido tudo. As contagens derivadas por regra passam
    #      a ficar sob chave propria, ao lado do registro por braco e nao em cima
    #      dele.
    os.makedirs(os.path.dirname(OUT_FLOW), exist_ok=True)
    existing = {}
    if os.path.exists(OUT_FLOW):
        try:
            existing = json.load(open(OUT_FLOW, encoding="utf-8"))
        except ValueError:
            existing = {}
    if not isinstance(existing, dict):
        existing = {}
    flow["scope_en"] = ("rule output recomputed over the whole merged corpus; the "
                        "per-database-arm counts are in 'screening'")
    flow["scope_pt"] = ("saida das regras recalculada sobre o corpus unido inteiro; as "
                        "contagens por braco de base estao em 'screening'")
    flow["pmcid_note_en"] = ("only PubMed records carry a PMCID, so this count says nothing "
                             "about full-text availability for records imported from Scopus "
                             "or Web of Science")
    flow["pmcid_note_pt"] = ("so registros do PubMed trazem PMCID, entao esta contagem nao diz "
                             "nada sobre disponibilidade de texto completo para registros "
                             "importados da Scopus ou da Web of Science")
    existing["screening_rule_recomputation"] = flow
    json.dump(existing, open(OUT_FLOW, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)

    print("EN | PRISMA screening counts | PT | Contagens da triagem PRISMA")
    for k, v in flow.items():
        print(f"  {k:42s} {v}")
    print(f"\nEN/PT -> {OUT_CSV}, {OUT_FLOW}")


if __name__ == "__main__":
    main()
