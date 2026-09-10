# Epigenetics and microRNAs in neurodegenerative disease

**Reproducibility package for a systematic review and random-effects meta-analysis of the diagnostic accuracy of circulating microRNAs in Alzheimer's disease (AD) and Parkinson's disease (PD).**

> 🇧🇷 **Versão em português: [README.pt-BR.md](README.pt-BR.md)**

**Author:** Wesley Felipe Capucho · **Supervisor:** Prof. Dr. Roberta Sessa Stilhano Yamaguchi
Universidade Federal de São Paulo (UNIFESP) — Specialisation in Human Physiology and Pathophysiology applied to Health Sciences.

---

## What this repository is

This repository holds **raw data, scripts, tables and figures**, and nothing else. Its purpose is that every number in the associated manuscript can be regenerated from the files here by running the pipeline. The manuscript itself is written and kept outside this repository.

Two bodies of work live here:

| Layer | What it is | Scripts |
|---|---|---|
| **Bibliometric** | PubMed corpus mining, miRNA extraction, PCA, clustering, miRNA–disease network, exploratory ODE models of the miR-29/BACE1/Aβ and miR-7/SNCA/α-synuclein axes | `01`, `02` |
| **Meta-analytic** | PICO systematic search, PRISMA screening, full-text extraction, random-effects meta-analysis of AUC, clinical-translation landscape | `03`–`11` |

The meta-analytic layer exists to answer a question the source monograph raised about itself: bibliometric frequency and experimental validation are not independent sources of evidence, because the most-studied miRNAs accumulate both. Pooled diagnostic accuracy is external to that loop.

## Current state of the evidence base

| | |
|---|---|
| Databases searched | PubMed/MEDLINE, Scopus (both disease arms) |
| Unique records | 560 |
| Full texts read | 47 |
| Studies contributing estimates | 42 |
| Extracted estimates | 76 (51 eligible, 41 poolable) |
| Independent studies pooled | 20 |
| Search date | 10 September 2026 |

Pooled estimates live in `results/tables/meta_analysis_pooled_auc.csv`, the per-estimate inputs in `results/tables/meta_analysis_input_estimates.csv`, and the clustering sensitivity analyses in `results/tables/sensitivity_single_mirna.csv`. Every extracted value is traceable to a verbatim sentence from its source in `data/extracted/diagnostic_accuracy_extraction.csv`.

Interpretation belongs in the manuscript, not here. Two things do belong here, because they are properties of the data rather than of the argument:

- **Estimates within a study are correlated.** One study contributes eight estimates and another six, and the random-effects model treats each as independent. `scripts/05` therefore also re-pools one-estimate-per-study and leave-one-study-out, and the spread between them is part of the result.
- **Three defects were found and corrected in this pipeline, and each changed a number.** They are recorded in `data/processed/prisma_flow.json` and in the header comments of the scripts that carry the fix. See *Corrections* below.

## Repository layout

```
.
├── data/
│   ├── raw/
│   │   ├── pubmed/                    # Bibliometric sample, live from NCBI (provenance in manifest.json)
│   │   ├── systematic_review_2026/    # Search strategy, screening corpus and decisions,
│   │   │                              #   Scopus exports, mention counts, prior meta-analyses
│   │   └── clinical_trials_2026/      # ClinicalTrials.gov landscape of miRNA-directed therapeutics
│   ├── extracted/                     # Diagnostic-accuracy extraction table + verbatim source quotes
│   └── processed/                     # PRISMA flow counts (regenerable)
├── scripts/
│   ├── 01_busca_ranqueamento_pubmed.py            # Bibliometric search + ranking (original monograph)
│   ├── 02_estatistica_bioinformatica_modelagem.py # Statistics, PCA, networks, ODE models (original)
│   ├── 03_systematic_search.py                    # PICO systematic search via NCBI E-utilities
│   ├── 04_screening.py                            # Rule-based PRISMA screening
│   ├── 05_meta_analysis.py                        # Random-effects meta-analysis + sensitivity analyses
│   ├── 06_citation_vs_performance.py              # Literature attention vs measured accuracy
│   ├── 07_clinical_translation_landscape.py       # What actually reached clinical trials
│   ├── 08_verify_consistency.py                   # Cross-checks data, PRISMA counts and result tables
│   ├── 09_ingest_scopus_wos.py                    # Merges and deduplicates Scopus / WoS exports
│   ├── 10_build_screening_corpus.py               # Assembles the corpus, rebuilds mention counts
│   └── 11_attention_finding_audit.py              # Decomposes what moved the attention correlation
├── docs/
│   ├── en/                            # Methods, data dictionary, how to export Scopus/WoS
│   └── pt-BR/                         # Métodos, dicionário de dados, como exportar Scopus/WoS
├── results/
│   ├── figures/                       # Forest plot, funnel plot, attention-vs-accuracy plot
│   └── tables/                        # Pooled estimates, inputs, sensitivity, correlations, audit
└── requirements.txt
```

## Reproducing the analysis

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

export NCBI_EMAIL=you@example.org     # required by scripts that call NCBI

# Meta-analytic layer, in order
python scripts/03_systematic_search.py            # live PubMed search
python scripts/04_screening.py
python scripts/09_ingest_scopus_wos.py --scopus <export.csv> --arm AD
python scripts/10_build_screening_corpus.py       # corpus + mention counts
python scripts/05_meta_analysis.py
python scripts/06_citation_vs_performance.py
python scripts/07_clinical_translation_landscape.py
python scripts/11_attention_finding_audit.py
python scripts/08_verify_consistency.py           # must pass before committing
```

`scripts/05`, `06`, `08`, `10` and `11` run entirely offline from the committed data. `scripts/03` calls the live PubMed API and will legitimately return more records than the frozen 2026-09-10 counts, because the literature keeps growing; `data/raw/systematic_review_2026/search_strategy.json` preserves the counts behind the reported numbers.

Scopus cannot be queried by API from a script — it requires institutional authentication. Run the search in the Scopus web interface, export the result set, and hand the file to `scripts/09`. The ready-to-paste queries are in `docs/en/HOW_TO_EXPORT_SCOPUS_WOS.md`.

For the bibliometric layer, run `scripts/01` first: it produces the input of `scripts/02`.

## Data provenance and integrity

- **Every number came from a real source.** PubMed records were pulled from the NCBI E-utilities API; accuracy values were read from open-access full texts in PubMed Central or from the abstract when no full text was reachable. Nothing was simulated, estimated to fill a gap, or carried over from a secondary citation.
- **Every extracted value stores its source sentence.** `diagnostic_accuracy_extraction.csv` carries a `verbatim_quote` column with the exact wording supporting each AUC, sensitivity and specificity, plus PMID and DOI.
- **Values that could not be resolved unambiguously were kept and flagged, not quietly dropped.** 25 of the 76 extracted rows are marked `eligible_primary_pool = no` with an explicit `exclusion_reason`.
- **Automated text mining was used to *find* candidate values, never to record them.** Regular expressions surfaced sentences; values were then read and transcribed by hand, because the patterns demonstrably mis-pair sensitivity with specificity and mistake p-values for accuracy metrics.
- **Duplicate publication was checked.** PMIDs 40661348 and 41836608 report the same cohort and the same AUCs (preprint and journal version); they are counted once.
- **The standard-error method was validated against a source.** For PMID 33129241 the Hanley–McNeil formula returns SE = 0.0822 for AUC 0.75 with 18 vs 18 subjects; the article independently reports SE = 0.08.
- **`scripts/08` enforces all of this.** It recomputes each derived number from its source and fails if the extraction table, the PRISMA counts and the result tables disagree. 429 checks currently pass.

Full texts are **not** redistributed here — only extracted data points and their citations. Fetch sources through their DOIs.

## Corrections

Three defects in this pipeline were found after results had already been produced. Each is fixed, and each changed a reported number. They are listed here rather than quietly patched, because a reproducibility package that hides its own corrections is not one.

| Defect | Effect | Fixed in |
|---|---|---|
| Screening regex closed with `\b` after `meta-analys`, so it never matched "meta-analysis" | Self-declared meta-analyses passed as primary studies; one record reclassified; it is why prior meta-analyses went unnoticed | `scripts/04` |
| miRNA mention counts computed over 234 PubMed records while AUCs came from the 560-record corpus | Markers entering via Scopus were credited zero mentions by construction, inflating the attention–performance correlation | `scripts/10` |
| Studies keyed on PMID alone | The four studies published outside MEDLINE collapsed into one blank-PMID group; two independent miR-124 cohorts counted as one; study totals understated | `scripts/05`, `scripts/06` |
| Biofluid subgroups required three *estimates*, not three *studies* | Produced a subgroup of eight estimates from a single cohort — within-study spread reported as between-study evidence | `scripts/05` |
| `scripts/09` deduplicated only against PubMed | The Scopus PD arm appeared to add 157 new records instead of 78 | `scripts/09` |

`scripts/11_attention_finding_audit.py` quantifies the second of these: it recomputes the attention–performance correlation under each combination of inputs and separates the contribution of the bug from that of the new data.

## Known limitations

- Web of Science has not been searched. Coverage is symmetric across diseases but two databases deep.
- Extraction is restricted to open-access full texts and abstracts, which may select a non-random subset of the literature; four Parkinson-arm studies were access-restricted such that only a combined-model AUC could be read.
- 34 of the 41 weighted standard errors are reconstructed by Hanley–McNeil rather than taken from a published interval.
- Heterogeneity is high (I² up to 97%) and estimates within studies are correlated, which also makes Egger's test unreliable here.
- Most miRNAs contribute a single study, so the attention-vs-performance analysis is underpowered in both directions.
- The ODE models in `scripts/02` use illustrative, non-calibrated parameters. They are qualitative and hypothesis-generating; they are not quantitative predictions and should not be reported as such.

## Scientific integrity and use of AI

This work follows the transparency and reproducibility principles of the USP Guide to Good Scientific Practice (2025). AI tools assisted with organisation, code, retrieval and drafting; they did not replace data curation, verification against sources, or the author's scientific judgement. No data were fabricated. Where a value could not be verified against its source, it was excluded and the exclusion recorded.

## Citation

Capucho, W. *Epigenetics and microRNAs in neurodegenerative disease: systematic review and meta-analysis of circulating miRNA diagnostic accuracy.* GitHub, 2026. https://github.com/WesleyCapucho/-Epigen-tica-e-micrornas-em-doen-as-neurodegenerativas

Literature data are from PubMed/PubMed Central (National Library of Medicine, NCBI) and Scopus (Elsevier). Individual studies are cited by DOI in `data/extracted/diagnostic_accuracy_extraction.csv`.
