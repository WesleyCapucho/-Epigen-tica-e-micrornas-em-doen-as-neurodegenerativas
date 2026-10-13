#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EN | Assemble the full screening corpus (PubMed + imported database arms) and rebuild the
     miRNA mention counts from it.
PT | Monta o corpus completo de triagem (PubMed + bracos de bases importadas) e reconstroi
     as contagens de mencao de miRNA a partir dele.

EN | Why this script exists. The mention counts feed the attention-versus-
     performance analysis, and they must be counted over the SAME corpus the
     accuracy estimates come from. For a while they were not: the counts had
     been built over the 234 PubMed records and then left frozen while the
     Scopus arms added 326 more records and a dozen new markers. Every miRNA
     that entered through Scopus was therefore credited with zero mentions by
     construction, which pushes any correlation with performance toward zero.
     That is an artefact of mismatched inputs, not a result.
PT | Por que este script existe. As contagens de mencao alimentam a analise de
     atencao versus desempenho e precisam ser contadas sobre o MESMO corpus de
     onde vem as estimativas de acuracia. Por um tempo nao foram: as contagens
     tinham sido construidas sobre os 234 registros do PubMed e ficaram
     congeladas enquanto os bracos do Scopus somavam 326 registros e uma duzia
     de marcadores novos. Todo miRNA que entrou pelo Scopus era, por
     construcao, creditado com zero mencoes, o que empurra qualquer correlacao
     com desempenho para zero. Isso e artefato de entradas incompativeis, e
     nao resultado.

EN | The second reason is reproducibility. The corpus used to live only in the
     analysis environment; titles and abstracts were never committed, so the
     mention counts could not be regenerated from the repository alone. They
     can now.
PT | A segunda razao e reprodutibilidade. O corpus vivia so no ambiente de
     analise; titulos e resumos nunca foram versionados, entao as contagens nao
     podiam ser regeradas so a partir do repositorio. Agora podem.

    python scripts/10_build_screening_corpus.py

EN | Requires NCBI_EMAIL when the PubMed half has to be re-fetched. When
     data/raw/systematic_review_2026/screening_corpus.json already exists, the
     PubMed half is read from it and no network access is needed.
PT | Requer NCBI_EMAIL quando a metade do PubMed precisa ser rebuscada. Se
     data/raw/systematic_review_2026/screening_corpus.json ja existe, essa
     metade e lida dele e nenhum acesso de rede e necessario.
"""

import csv
import glob
import json
import os
import re
import sys
import time

RAW = "data/raw/systematic_review_2026"
CORPUS = f"{RAW}/screening_corpus.json"
DECISIONS = f"{RAW}/screening_decisions.csv"
COUNTS = f"{RAW}/mirna_mention_counts.csv"

MIRNA_RE = re.compile(
    r'\b(?:hsa[-‐‑])?(?:miR|let|mir)[-‐‑]\s?[0-9][0-9a-zA-Z]*'
    r'(?:[-‐‑][0-9a-z]+)*(?:[-‐‑][35]p)?\b')


def normalise(name):
    """EN/PT: canonical miRNA label (drop hsa- prefix, unify dashes and case)."""
    n = name.replace("‐", "-").replace("‑", "-").replace(" ", "")
    n = re.sub(r'^hsa-', '', n, flags=re.I)
    if n.lower().startswith("mir-"):
        n = "miR-" + n[4:]
    elif n.lower().startswith("let-"):
        n = "let-" + n[4:]
    return n


def family(name):
    """EN/PT: collapse a miRNA to its family (miR-146a-5p -> miR-146a)."""
    return re.sub(r'-[35]p$', '', normalise(name))


def fetch_pubmed_half(pmids):
    """
    EN | Fetch title and abstract for the archived PMIDs from NCBI E-utilities.
    PT | Busca titulo e resumo dos PMIDs arquivados nas E-utilities do NCBI.
    """
    try:
        from Bio import Entrez
    except ImportError:
        sys.exit("EN: pip install biopython | PT: instale biopython")
    Entrez.email = os.environ.get("NCBI_EMAIL")
    if not Entrez.email:
        sys.exit("EN: set NCBI_EMAIL before running.\n"
                 "PT: defina NCBI_EMAIL antes de executar.")
    out = {}
    for i in range(0, len(pmids), 100):
        batch = pmids[i:i + 100]
        h = Entrez.efetch(db="pubmed", id=",".join(batch), retmode="xml")
        recs = Entrez.read(h)
        h.close()
        for art in recs.get("PubmedArticle", []):
            cit = art["MedlineCitation"]
            pmid = str(cit["PMID"])
            a = cit["Article"]
            abstract = " ".join(str(p) for p in
                                a.get("Abstract", {}).get("AbstractText", []))
            out[pmid] = {
                "title": str(a.get("ArticleTitle", "")),
                "abstract": abstract,
                "journal": str(a.get("Journal", {}).get("Title", "")),
                "article_types": [str(t) for t in a.get("PublicationTypeList", [])],
                "database": "PubMed",
            }
        time.sleep(0.4)
    return out


def main():
    if not os.path.exists(DECISIONS):
        sys.exit(f"EN/PT: missing {DECISIONS}")
    # EN | Only the PubMed-keyed rows. The decisions file used to hold the PubMed half
    #      alone; it now covers the whole merged corpus, so taking every key here made
    #      this script treat 353 imported records as missing PubMed articles and try to
    #      fetch them by ID from NCBI. A row is PubMed's when its database says so, with
    #      an all-digits key as the fallback for a file written before that column.
    # PT | Apenas as linhas com chave do PubMed. O arquivo de decisoes guardava so a
    #      metade do PubMed; agora cobre o corpus unido inteiro, entao pegar toda chave
    #      aqui fazia este script tratar 353 registros importados como artigos do PubMed
    #      faltantes e tentar busca-los por ID no NCBI. Uma linha e do PubMed quando a
    #      coluna database diz isso, com a chave toda numerica como reserva para um
    #      arquivo escrito antes dessa coluna.
    archived = []
    for r in csv.DictReader(open(DECISIONS, encoding="utf-8")):
        key = (r.get("pmid") or "").strip()
        if not key:
            continue
        db = (r.get("database") or "").strip()
        if db == "PubMed" or (not db and key.isdigit()):
            archived.append(key)

    # --- PubMed half -------------------------------------------------------
    corpus = {}
    if os.path.exists(CORPUS):
        stored = json.load(open(CORPUS, encoding="utf-8"))
        corpus = {k: v for k, v in stored.items() if v.get("database") == "PubMed"}
        print(f"EN | PubMed half read from {CORPUS}: {len(corpus)} records")
        print(f"PT | Metade PubMed lida de {CORPUS}: {len(corpus)} registros")
    missing = [p for p in archived if p not in corpus]
    if missing:
        print(f"EN | Fetching {len(missing)} PubMed records | PT | Buscando {len(missing)}")
        corpus.update(fetch_pubmed_half(missing))

    # EN | Keep exactly the archived record set. A re-fetch must not quietly
    #      widen the corpus, or the denominator of every count would drift.
    # PT | Manter exatamente o conjunto arquivado. Uma rebusca nao pode alargar
    #      o corpus em silencio, ou o denominador de toda contagem mudaria.
    corpus = {p: corpus[p] for p in archived if p in corpus}
    still = [p for p in archived if p not in corpus]
    if still:
        sys.exit(f"EN/PT: could not recover {len(still)} archived records: {still[:10]}")

    # --- imported database arms --------------------------------------------
    # EN | Each arm file carries its own database name per record. Counting them
    #      all as "Scopus" was harmless while Scopus was the only import; with Web
    #      of Science ingested it would put a false number in the methods, so the
    #      tally is per database and the key prefix no longer names one.
    # PT | Cada arquivo de braco traz o nome da base por registro. Conta-los todos
    #      como "Scopus" era inofensivo enquanto a Scopus era a unica importacao;
    #      com a Web of Science ingerida isso poria um numero falso nos metodos,
    #      entao a contagem e por base e o prefixo da chave nao nomeia mais uma.
    from collections import Counter
    imported = Counter()
    for fp in sorted(glob.glob(f"{RAW}/additional_records_*.json")):
        arm = os.path.basename(fp).replace("additional_records_", "").replace(".json", "")
        for j, r in enumerate(json.load(open(fp, encoding="utf-8"))):
            key = f"import_{arm}_{r.get('DOI') or j}"
            corpus[key] = {
                "title": r.get("Title", ""),
                "abstract": r.get("Abstract", ""),
                "journal": r.get("Journal", ""),
                "year": r.get("Year", ""),
                "doi": r.get("DOI", ""),
                "article_types": [t for t in (r.get("PublicationTypes") or "").split(";") if t.strip()],
                "database": r.get("database", "Scopus"),
                "search_arm": arm,
            }
            imported[corpus[key]["database"]] += 1
    n_imported = sum(imported.values())
    print("EN | Imported database records merged | PT | Registros importados somados: "
          f"{n_imported} " + ", ".join(f"{k} {v}" for k, v in sorted(imported.items())))

    os.makedirs(RAW, exist_ok=True)
    json.dump(corpus, open(CORPUS, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

    # --- mention counts ----------------------------------------------------
    # EN/PT: distinct ARTICLES per miRNA and per family, never raw occurrences
    exact, fam = {}, {}
    n_no_abstract = 0
    for key, art in corpus.items():
        if not (art.get("abstract") or "").strip():
            n_no_abstract += 1
        text = f"{art.get('title','')} {art.get('abstract','')}"
        found = {normalise(m) for m in MIRNA_RE.findall(text)}
        for m in found:
            exact.setdefault(m, set()).add(key)
        for f in {family(m) for m in found}:
            fam.setdefault(f, set()).add(key)

    rows = [{"mirna": m, "family": family(m),
             "n_articles_mentioning": len(keys),
             "n_articles_mentioning_family": len(fam[family(m)])}
            for m, keys in exact.items()]
    rows.sort(key=lambda r: (-r["n_articles_mentioning"], r["mirna"]))
    with open(COUNTS, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["mirna", "family",
                                          "n_articles_mentioning",
                                          "n_articles_mentioning_family"])
        w.writeheader()
        w.writerows(rows)

    print("\n" + "=" * 70)
    print("EN | Corpus and mention counts | PT | Corpus e contagens de mencao")
    print("=" * 70)
    print(f"Records in corpus / registros no corpus  : {len(corpus)}")
    print(f"   PubMed                                : {sum(1 for v in corpus.values() if v['database']=='PubMed')}")
    for db, n in sorted(imported.items()):
        print(f"   {db:38s}: {n}")
    print(f"Records without abstract / sem resumo    : {n_no_abstract}")
    print(f"Distinct miRNA labels / rotulos distintos: {len(rows)}")
    print(f"Distinct families / familias distintas   : {len(fam)}")
    print(f"\nEN/PT -> {CORPUS}\nEN/PT -> {COUNTS}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
