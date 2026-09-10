#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EN | Ingest Scopus and Web of Science exports and merge them into the review.
PT | Ingere exportacoes do Scopus e da Web of Science e as funde a revisao.

EN | Those two databases require institutional authentication, so their records
     cannot be pulled by an API from this project. The supported path is the one
     systematic reviewers already use: run the search in the database, export
     the result set, and hand the file to this script. It normalises the export,
     deduplicates it against the PubMed corpus by DOI, PubMed ID and normalised
     title, and reports exactly how many records each database contributed that
     PubMed did not already have.
PT | Essas duas bases exigem autenticacao institucional, entao seus registros nao
     podem ser puxados por API a partir deste projeto. O caminho suportado e o que
     revisores sistematicos ja usam: rodar a busca na base, exportar o conjunto de
     resultados e entregar o arquivo a este script. Ele normaliza a exportacao,
     deduplica contra o corpus do PubMed por DOI, PubMed ID e titulo normalizado,
     e reporta exatamente quantos registros cada base acrescentou.

    python scripts/09_ingest_scopus_wos.py \
        --scopus data/raw/systematic_review_2026/scopus_export.csv \
        --wos    data/raw/systematic_review_2026/wos_export.txt \
        --arm    AD

EN | Accepted formats: Scopus CSV export, Scopus/Generic RIS, Web of Science
     tab-delimited or plain-text export. The export MUST include the abstract,
     because screening reads it; a warning is printed if abstracts are missing.
PT | Formatos aceitos: exportacao CSV do Scopus, RIS do Scopus/generico,
     exportacao da Web of Science em texto delimitado por tabulacao ou texto
     puro. A exportacao PRECISA incluir o resumo, porque a triagem o le; um aviso
     e impresso se os resumos estiverem faltando.
"""

import argparse
import csv
import glob
import json
import os
import re
import sys

# EN/PT: Scopus abstracts routinely exceed the default CSV field limit
csv.field_size_limit(10 ** 7)

CORPUS = "data/raw/systematic_review_2026/screening_corpus.json"
DECISIONS = "data/raw/systematic_review_2026/screening_decisions.csv"
OUT_DIR = "data/raw/systematic_review_2026"


def norm_title(t):
    """EN/PT: lowercase, strip punctuation and whitespace, for fuzzy matching."""
    return re.sub(r'[^a-z0-9]+', '', (t or "").lower())


def norm_doi(d):
    d = (d or "").strip().lower()
    d = re.sub(r'^https?://(dx\.)?doi\.org/', '', d)
    return d


# --------------------------------------------------------------------------
# Parsers | Analisadores
# --------------------------------------------------------------------------
def parse_scopus_csv(path):
    """EN/PT: Scopus 'Export > CSV' file. Column names vary slightly by year."""
    out = []
    with open(path, encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        cols = {c.lower().strip(): c for c in (reader.fieldnames or [])}

        def pick(*names):
            for n in names:
                if n in cols:
                    return cols[n]
            return None

        c_title = pick("title", "document title")
        c_abs = pick("abstract")
        c_doi = pick("doi")
        c_pmid = pick("pubmed id", "pubmed_id")
        c_year = pick("year", "publication year")
        c_src = pick("source title", "source")
        c_auth = pick("authors", "author full names")
        c_type = pick("document type")
        c_kw = pick("author keywords", "index keywords")

        for row in reader:
            abstract = (row.get(c_abs) or "").strip() if c_abs else ""
            # EN/PT: Scopus writes this placeholder when it holds no abstract
            if abstract.lower().startswith("[no abstract available"):
                abstract = ""
            out.append({
                "Title": (row.get(c_title) or "").strip() if c_title else "",
                "Abstract": abstract,
                "DOI": norm_doi(row.get(c_doi)) if c_doi else "",
                "PMID": (row.get(c_pmid) or "").strip() if c_pmid else "",
                "Year": (row.get(c_year) or "").strip() if c_year else "",
                "Journal": (row.get(c_src) or "").strip() if c_src else "",
                "Authors": (row.get(c_auth) or "").strip() if c_auth else "",
                "PublicationTypes": (row.get(c_type) or "").strip() if c_type else "",
                "Keywords": (row.get(c_kw) or "").strip() if c_kw else "",
                "database": "Scopus",
            })
    return out


def parse_ris(path):
    """EN/PT: RIS export (Scopus, WoS or reference manager)."""
    out, rec = [], {}
    tag_map = {"TI": "Title", "T1": "Title", "AB": "Abstract", "N2": "Abstract",
               "DO": "DOI", "PY": "Year", "Y1": "Year", "JO": "Journal",
               "JF": "Journal", "T2": "Journal", "TY": "PublicationTypes",
               "KW": "Keywords"}
    with open(path, encoding="utf-8-sig", errors="replace") as f:
        for raw in f:
            line = raw.rstrip("\n")
            m = re.match(r'^([A-Z][A-Z0-9])\s+-\s?(.*)$', line)
            if not m:
                continue
            tag, val = m.group(1), m.group(2).strip()
            if tag == "ER":
                if rec:
                    rec.setdefault("database", "RIS")
                    rec["DOI"] = norm_doi(rec.get("DOI"))
                    out.append(rec)
                rec = {}
            elif tag == "AU":
                rec["Authors"] = (rec.get("Authors", "") + "; " + val).strip("; ")
            elif tag in tag_map:
                key = tag_map[tag]
                rec[key] = (rec.get(key, "") + " " + val).strip() if key == "Abstract" else val
    if rec:
        rec.setdefault("database", "RIS")
        out.append(rec)
    return out


def parse_wos_tab(path):
    """EN/PT: Web of Science tab-delimited export (field-tag columns)."""
    out = []
    with open(path, encoding="utf-8-sig", errors="replace", newline="") as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row in reader:
            out.append({
                "Title": (row.get("TI") or row.get("Article Title") or "").strip(),
                "Abstract": (row.get("AB") or row.get("Abstract") or "").strip(),
                "DOI": norm_doi(row.get("DI") or row.get("DOI")),
                "PMID": (row.get("PM") or row.get("Pubmed Id") or "").strip(),
                "Year": (row.get("PY") or row.get("Publication Year") or "").strip(),
                "Journal": (row.get("SO") or row.get("Source Title") or "").strip(),
                "Authors": (row.get("AU") or row.get("Authors") or "").strip(),
                "PublicationTypes": (row.get("DT") or row.get("Document Type") or "").strip(),
                "Keywords": (row.get("DE") or row.get("Author Keywords") or "").strip(),
                "database": "Web of Science",
            })
    return out


def load_any(path, label):
    ext = os.path.splitext(path)[1].lower()
    if ext == ".ris":
        recs = parse_ris(path)
    elif ext == ".csv":
        recs = parse_scopus_csv(path)
    else:
        recs = parse_wos_tab(path)
    for r in recs:
        r["database"] = label
    return recs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scopus", help="Scopus export (.csv or .ris)")
    ap.add_argument("--wos", help="Web of Science export (.txt, .tsv or .ris)")
    ap.add_argument("--arm", default="", help="Search arm label, e.g. AD or PD")
    args = ap.parse_args()

    if not args.scopus and not args.wos:
        ap.error("EN: give at least one export | PT: informe ao menos uma exportacao")

    # EN | Resolve the output path before anything else. This file is rewritten
    #      on every run, so it must never be read back as a "previously ingested
    #      arm" - a re-run would then deduplicate the arm against its own output
    #      and report zero new records while silently emptying the file.
    # PT | Resolve o caminho de saida antes de tudo. Este arquivo e reescrito a
    #      cada execucao, entao nunca pode ser relido como "braco ja ingerido" -
    #      uma reexecucao deduplicaria o braco contra a propria saida e reportaria
    #      zero registros novos, esvaziando o arquivo em silencio.
    os.makedirs(OUT_DIR, exist_ok=True)
    suffix = f"_{args.arm}" if args.arm else ""
    out_json = f"{OUT_DIR}/additional_records{suffix}.json"

    # --- existing PubMed corpus, for deduplication -------------------------
    # EN | Prefer the full corpus when present; otherwise fall back to the
    #      committed screening decisions, which carry pmid, doi and title -
    #      everything deduplication needs.
    # PT | Usa o corpus completo quando existe; caso contrario, recorre as
    #      decisoes de triagem versionadas, que trazem pmid, doi e titulo -
    #      tudo de que a deduplicacao precisa.
    pm_dois, pm_pmids, pm_titles = set(), set(), set()
    n_loaded, source = 0, None
    if os.path.exists(CORPUS):
        corpus = json.load(open(CORPUS))
        for pmid, art in corpus.items():
            ids = art.get("identifiers", {}) if isinstance(art.get("identifiers"), dict) else {}
            pm_pmids.add(str(pmid))
            pm_dois.add(norm_doi(art.get("DOI") or ids.get("doi")))
            pm_titles.add(norm_title(art.get("Title") or art.get("title")))
        n_loaded, source = len(corpus), CORPUS
    elif os.path.exists(DECISIONS):
        with open(DECISIONS, encoding="utf-8", newline="") as f:
            for row in csv.DictReader(f):
                pm_pmids.add(str(row.get("pmid", "")).strip())
                pm_dois.add(norm_doi(row.get("doi")))
                pm_titles.add(norm_title(row.get("title")))
                n_loaded += 1
        source = DECISIONS
    # EN | Also deduplicate against previously ingested arms. A record that
    #      mentions both diseases is returned by both the AD and the PD search,
    #      and counting it twice would inflate the corpus. Missing this once
    #      turned 78 genuinely new PD records into an apparent 157.
    # PT | Deduplicar tambem contra bracos ja ingeridos. Um registro que menciona
    #      as duas doencas volta nas buscas de AD e de PD, e conta-lo duas vezes
    #      inflaria o corpus. Deixar isso passar uma vez transformou 78 registros
    #      novos de PD em aparentes 157.
    prior_files = [f for f in sorted(glob.glob(os.path.join(OUT_DIR, "additional_records_*.json")))
                   if os.path.abspath(f) != os.path.abspath(out_json)]
    n_prior = 0
    for fp in prior_files:
        try:
            for r in json.load(open(fp)):
                pm_dois.add(norm_doi(r.get("DOI")))
                pm_titles.add(norm_title(r.get("Title")))
                if r.get("PMID"):
                    pm_pmids.add(str(r["PMID"]).strip())
                n_prior += 1
        except Exception:
            continue
    if n_prior:
        print(f"EN | Also deduplicating against {n_prior} records from previously "
              f"ingested arms ({len(prior_files)} file(s))")
        print(f"PT | Deduplicando tambem contra {n_prior} registros de bracos ja "
              f"ingeridos ({len(prior_files)} arquivo(s))")

    pm_dois.discard("")
    pm_titles.discard("")
    pm_pmids.discard("")
    if source:
        print(f"EN | PubMed corpus loaded from {source}: {n_loaded} records")
        print(f"PT | Corpus PubMed carregado de {source}: {n_loaded} registros")
    else:
        print("WARNING: no PubMed corpus found - nothing to deduplicate against.")

    incoming = []
    if args.scopus:
        incoming += load_any(args.scopus, "Scopus")
    if args.wos:
        incoming += load_any(args.wos, "Web of Science")

    # --- deduplicate -------------------------------------------------------
    seen_doi, seen_title = set(), set()
    new_records, dup_pubmed, dup_internal, no_abstract = [], 0, 0, 0
    for r in incoming:
        doi, title = r.get("DOI", ""), norm_title(r.get("Title"))
        pmid = str(r.get("PMID", "")).strip()
        if (doi and doi in pm_dois) or (pmid and pmid in pm_pmids) or (title and title in pm_titles):
            dup_pubmed += 1
            continue
        if (doi and doi in seen_doi) or (title and title in seen_title):
            dup_internal += 1
            continue
        if doi:
            seen_doi.add(doi)
        if title:
            seen_title.add(title)
        if not r.get("Abstract"):
            no_abstract += 1
        new_records.append(r)

    json.dump(new_records, open(out_json, "w"), ensure_ascii=False, indent=1)

    by_db = {}
    for r in new_records:
        by_db[r["database"]] = by_db.get(r["database"], 0) + 1

    print("\n" + "=" * 70)
    print("EN | Ingestion summary | PT | Resumo da ingestao")
    print("=" * 70)
    print(f"Records in the exports / registros nas exportacoes : {len(incoming)}")
    print(f"Already in PubMed corpus / ja no corpus PubMed     : {dup_pubmed}")
    print(f"Duplicated inside the exports / duplicados internos: {dup_internal}")
    print(f"NEW records / registros NOVOS                      : {len(new_records)}")
    for db, n in sorted(by_db.items()):
        print(f"    {db:<18} {n}")
    if no_abstract:
        print(f"\nWARNING / AVISO: {no_abstract} new records have no abstract.")
        print("EN | Screening reads the abstract; re-export including it.")
        print("PT | A triagem le o resumo; reexporte incluindo-o.")
    print(f"\nEN/PT -> {out_json}")
    print("\nEN | Next: run scripts/04_screening.py to screen the merged corpus,")
    print("     then scripts/05 and 08 to refresh the pooled estimates and checks.")
    print("PT | Depois: rode scripts/04_screening.py para triar o corpus unido,")
    print("     e entao scripts/05 e 08 para atualizar as estimativas e checagens.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
