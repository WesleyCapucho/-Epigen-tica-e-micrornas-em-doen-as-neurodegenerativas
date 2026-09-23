# How to export from Scopus and Web of Science

🇧🇷 Versão em português: [../pt-BR/COMO_EXPORTAR_SCOPUS_WOS.md](../pt-BR/COMO_EXPORTAR_SCOPUS_WOS.md)

---

## Why this step is manual

Scopus and Web of Science require institutional authentication. There is no public API for them in this project, and the environment that runs these analyses cannot reach `scopus.com` or `webofscience.com`. The supported route is the one systematic reviewers already use every day: run the search in the database, export the result set, and hand the file to the pipeline.

It takes a few minutes and closes the only declared methodological gap in the review.

---

## Step 1 — Run the search in Scopus

Sign in to Scopus, go to **Search → Advanced document search**, and paste exactly the string below.

### Alzheimer arm

```
TITLE-ABS-KEY (
  ( microrna OR mirna OR micrornas OR mirnas )
  AND alzheimer
  AND ( plasma OR serum OR "cerebrospinal fluid" OR csf OR blood
        OR exosome OR exosomal OR "extracellular vesicle" )
  AND ( roc OR "area under the curve" OR auc OR sensitivity OR specificity
        OR "diagnostic accuracy" OR "diagnostic value" )
)
AND PUBYEAR > 2014
```

### Parkinson arm

```
TITLE-ABS-KEY (
  ( microrna OR mirna OR micrornas OR mirnas )
  AND parkinson
  AND ( plasma OR serum OR "cerebrospinal fluid" OR csf OR blood
        OR exosome OR exosomal OR "extracellular vesicle" )
  AND ( roc OR "area under the curve" OR auc OR sensitivity OR specificity
        OR "diagnostic accuracy" OR "diagnostic value" )
)
AND PUBYEAR > 2014
```

**Write down the total number of results for each arm.** It goes into the PRISMA flow diagram and has to be the number the database displayed, not an estimate.

> One expected difference: Scopus's `TITLE-ABS-KEY` also searches keywords, whereas PubMed's `[Title/Abstract]` does not. Scopus will therefore tend to return more records. That is not an error — it is a scope difference between the databases, and it will be documented as such.

## Step 2 — Export

1. Tick **Select all** (the selector at the top of the results list).
2. Click **Export**.
3. Format: **CSV** (or RIS — the pipeline accepts both).
4. Under *Customize export*, tick at least these fields:

| Group | Fields |
|---|---|
| Citation information | Author(s), Document title, Year, Source title, Volume/Issue/Pages, **DOI**, **PubMed ID**, Document type |
| Bibliographical information | — |
| Abstract & keywords | **Abstract**, Author keywords, Index keywords |

The **abstract is mandatory**: screening reads it. Without it a record still enters the flow but cannot be screened, and the script says so.

5. Save one file per arm. Suggested names: `scopus_AD.csv` and `scopus_PD.csv`.

## Step 3 — Web of Science (done, 23 September 2026)

Both arms have been run and ingested: 187 records for the AD arm, 108 for the PD arm, 27 of them new after deduplication. The exports are archived in `data/raw/systematic_review_2026/exports/` as `wos_AD_2026-09-23.txt` and `wos_PD_2026-09-23.txt`. The instructions stay here because the search has to be repeatable, and because an update of this review will run it again.

In **Advanced Search**, using the `TS=` (Topic) field:

```
TS=( ( microRNA OR miRNA OR microRNAs OR miRNAs )
     AND Alzheimer
     AND ( plasma OR serum OR "cerebrospinal fluid" OR CSF OR blood
           OR exosome OR exosomal OR "extracellular vesicle" )
     AND ( ROC OR "area under the curve" OR AUC OR sensitivity OR specificity
           OR "diagnostic accuracy" OR "diagnostic value" ) )
```

With **Timespan 2015–2026**. Swap `Alzheimer` for `Parkinson` in the second arm.

Export as a **Tab-delimited file** or **RIS**, including *Full Record*. Suggested names: `wos_AD.txt` and `wos_PD.txt`. Export the whole result set, not the first page: an export truncated at 500 or 1000 records would silently bias the corpus, and nothing downstream can detect that.

## Step 4 — Send the files

Send the exported files. The pipeline then runs:

```bash
python scripts/09_ingest_scopus_wos.py --wos wos_AD.txt --arm AD_wos
python scripts/09_ingest_scopus_wos.py --wos wos_PD.txt --arm PD_wos
python scripts/04_screening.py
python scripts/10_build_screening_corpus.py
python scripts/05_meta_analysis.py
python scripts/06_citation_vs_performance.py
python scripts/14_quadas2_risk_of_bias.py
python scripts/15_bivariate_srocc.py
python scripts/16_grade_certainty.py
python scripts/08_verify_consistency.py
```

Script `09` deduplicates the incoming records against the PubMed corpus and against every previously ingested arm, by DOI, PubMed ID and normalised title, and reports how many records each database actually added.

**Give each database its own `--arm` label.** The output file is named from `--arm` alone, so `--arm AD` for a Web of Science export would overwrite the Scopus AD arm. `scripts/09` now refuses that and says so, but the habit to keep is `AD`/`PD` for Scopus and `AD_wos`/`PD_wos` for Web of Science. Every `additional_records_*.json` file is picked up downstream, so a new label costs nothing.

## What changes downstream

Three things, all of them improvements:

1. The sentence "Web of Science was not searched" leaves the Methods section and the limitations list, replaced by real counts. It is currently the only database limitation left.
2. The PRISMA flow diagram covers three databases, with traceable numbers.
3. Any new study reporting an AUC with group sizes enters the meta-analysis, and the pooled estimates are recomputed — possibly changing the published values. Script `08` makes sure the extraction table, the PRISMA counts and the result tables do not fall out of step with one another.

A fourth thing changes that is easy to miss: any new study enters QUADAS-2, the bivariate model and the GRADE rating as well, so the certainty of evidence is recomputed too. If Web of Science surfaces studies with neuropathological confirmation or a stated blinding, the risk-of-bias downgrade can move.

Worth saying plainly: if the new records bring estimates that perform systematically differently, the conclusions may shift. That is the point of completing the search — there would be no reason to run it if the answer were already settled.
