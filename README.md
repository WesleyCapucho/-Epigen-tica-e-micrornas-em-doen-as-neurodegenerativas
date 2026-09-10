# Epigenetics and microRNAs in neurodegenerative disease

**Do the microRNAs the field talks about most actually work as diagnostic biomarkers?**

A systematic review and random-effects meta-analysis of the diagnostic accuracy of circulating microRNAs in Alzheimer's disease (AD) and Parkinson's disease (PD), with a fully reproducible pipeline from literature search to pooled estimate.

> 🇧🇷 **Versão em português: [README.pt-BR.md](README.pt-BR.md)**

**Author:** Wesley Felipe Capucho · **Supervisor:** Prof. Dr. Roberta Sessa Stilhano Yamaguchi
Universidade Federal de São Paulo (UNIFESP) — Specialisation in Human Physiology and Pathophysiology applied to Health Sciences.

---

## What this repository contains

This repository began as the computational appendix of a monograph combining an integrative review, bibliometric analysis and ODE modelling of miRNA pathways in AD and PD. It is being extended into a manuscript with primary quantitative synthesis. Two distinct bodies of work live here:

| Layer | What it is | Status |
|---|---|---|
| **Bibliometric layer** | PubMed corpus mining, miRNA extraction, PCA, clustering, miRNA–disease network, exploratory ODE models of the miR-29/BACE1/Aβ and miR-7/SNCA/α-synuclein axes | From the original monograph (`scripts/01`, `scripts/02`) |
| **Meta-analytic layer** | PICO-driven systematic search, PRISMA screening, full-text data extraction, random-effects meta-analysis of AUC, clinical-translation landscape | New (`scripts/03`–`scripts/07`) |

The meta-analytic layer exists to answer a question the monograph raised about itself: bibliometric frequency and experimental validation are not independent sources of evidence, because the most-studied miRNAs accumulate both. Measuring pooled diagnostic accuracy breaks that circularity.

## Headline findings

All values are pooled from published estimates using DerSimonian–Laird random effects on the logit(AUC) scale. Every input value is traceable to a verbatim sentence in its source article (`data/extracted/diagnostic_accuracy_extraction.csv`).

| Subgroup | Pooled AUC (95% CI) | Estimates | Studies | I² |
|---|---|---|---|---|
| Overall | 0.807 (0.745–0.857) | 25 | 16 | 93% |
| Alzheimer's disease | 0.842 (0.788–0.884) | 13 | 10 | 77% |
| Parkinson's disease | 0.753 (0.621–0.850) | 12 | 6 | 94% |
| **Single miRNA** | **0.758 (0.706–0.804)** | 17 | 10 | 66% |
| **Multi-miRNA panel** | **0.888 (0.829–0.928)** | 8 | 7 | 85% |
| AD, single miRNA | 0.802 (0.741–0.851) | 7 | 6 | 63% |
| PD, single miRNA | 0.716 (0.640–0.781) | 10 | 4 | 55% |

Five results carry the argument:

1. **Single circulating miRNAs sit at the boundary of clinical usefulness.** At AUC 0.758 (CI 0.706–0.804), the pooled estimate falls below the ~0.80 commonly treated as a minimum for a standalone diagnostic test, with the interval's upper bound just reaching it — and nowhere near established plasma p-tau assays.

2. **Panels do substantially better, and the difference is not noise.** The confidence intervals of single miRNAs (0.706–0.804) and panels (0.829–0.928) do not overlap. Combining markers, not finding a better single marker, is where the gain is. This agrees with at least three prior meta-analyses — convergent evidence rather than a new discovery.

3. **Literature attention runs inversely to measured performance.** Across miRNAs with extractable accuracy data, the correlation between how many corpus articles mention a miRNA and its reported AUC is **ρ = −0.61 (p = 0.012)** among estimates that passed eligibility (ρ = −0.27, p = 0.16 across all). The two most-discussed miRNAs in the corpus, miR-125b (13 articles) and miR-146a (11 articles), returned AUCs of 0.75 and 0.68 — the lower end of the distribution. Sixteen miRNAs contribute, so this stays exploratory, but it points the opposite way from the field's emphasis. It is the one finding here with no clear precedent.

4. **Nothing has reached the clinic.** ClinicalTrials.gov (10 Sep 2026) lists 16 registered trials of miRNA-directed therapeutics worldwide — in hepatitis C, oncology and dermatology — and **zero** in Alzheimer's or Parkinson's disease. Notably, a miR-29 mimic (MRG-201/remlarsen) did reach Phase 2, for keloid scarring by intradermal injection. miR-29 is exactly the axis the source monograph simulated as a brain therapy: the molecule class exists, the route to the brain does not.

5. **Adding one database overturned two conclusions.** A first version of this review searched PubMed alone and found the AD single-miRNA subgroup homogeneous (I² = 0%), which we read as evidence that the ceiling was real rather than methodological. The Scopus AD arm then added 248 records PubMed had not returned; one of them took that subgroup to I² = 63%. The homogeneity was an artefact of an incomplete search. `docs/en/FINDINGS.md` §8 records what changed and why.

Egger's test indicates small-study effects in several subgroups, so these pooled values should be read as **upper bounds**, not neutral estimates. Six prior meta-analyses report SROC areas of 0.87–0.90 for the same question; that is a different estimand from the average of reported AUCs used here, and `docs/en/FINDINGS.md` §7 explains the comparison.

## Repository layout

```
.
├── data/
│   ├── raw/
│   │   ├── pubmed/                    # Bibliometric sample, live from NCBI (provenance in manifest.json)
│   │   ├── systematic_review_2026/    # Search strategy, screening decisions, miRNA mention counts
│   │   └── clinical_trials_2026/      # ClinicalTrials.gov landscape of miRNA-directed therapeutics
│   ├── extracted/                     # Diagnostic-accuracy extraction table + verbatim source quotes
│   └── processed/                     # Pipeline outputs (PRISMA flow; regenerable)
├── scripts/
│   ├── 01_busca_ranqueamento_pubmed.py            # Bibliometric search + ranking (original monograph)
│   ├── 02_estatistica_bioinformatica_modelagem.py # Statistics, PCA, networks, ODE models (original)
│   ├── 03_systematic_search.py                    # PICO systematic search via NCBI E-utilities
│   ├── 04_screening.py                            # Rule-based PRISMA screening
│   ├── 05_meta_analysis.py                        # Random-effects meta-analysis of AUC
│   ├── 06_citation_vs_performance.py              # Literature attention vs measured accuracy
│   ├── 07_clinical_translation_landscape.py       # What actually reached clinical trials
│   ├── 08_verify_reported_numbers.py              # Checks every figure in the prose against the tables
│   └── 09_ingest_scopus_wos.py                    # Merges Scopus / Web of Science exports
├── docs/
│   ├── en/                            # Methods, data dictionary, findings (English)
│   └── pt-BR/                         # Métodos, dicionário de dados, achados (Portuguese)
├── results/
│   ├── figures/                       # Forest plot, funnel plot, attention-vs-accuracy plot
│   └── tables/                        # Pooled estimates, per-estimate inputs, correlations
└── requirements.txt
```

## Reproducing the analysis

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Layer 2 — systematic review and meta-analysis
python scripts/03_systematic_search.py --email you@example.org   # needs NCBI access
python scripts/04_screening.py
python scripts/05_meta_analysis.py
python scripts/06_citation_vs_performance.py
python scripts/07_clinical_translation_landscape.py
```

`scripts/05` and `scripts/06` run offline from the committed data files. `scripts/03` calls the live PubMed API and will legitimately return more records than the frozen 2026-09-10 counts, because the literature keeps growing; `data/raw/systematic_review_2026/search_strategy.json` preserves the counts behind the numbers reported here.

For the original bibliometric layer, see `scripts/01` and `scripts/02` (run `01` first — it produces the input of `02`).

## Data provenance and integrity

- **Every number came from a real source.** PubMed records were pulled from the NCBI E-utilities API; accuracy values were read from open-access full texts in PubMed Central. Nothing was simulated, estimated to fill a gap, or carried over from a secondary citation.
- **Every extracted value stores its source sentence.** `diagnostic_accuracy_extraction.csv` has a `verbatim_quote` column holding the exact wording that supports each AUC, sensitivity and specificity, plus the PMID and DOI.
- **Values that could not be resolved unambiguously were kept and flagged, not quietly dropped.** 14 of 42 extracted rows are marked `eligible_primary_pool = no` with an explicit `exclusion_reason` (composite comparator, within-disease contrast, prodromal population, unstable perfect separation, cohort not attributable).
- **Automated text mining was used to *find* candidate values, never to record them.** Regular expressions surfaced sentences; the values were then read and transcribed by hand, because the patterns demonstrably mis-pair sensitivity with specificity and mistake p-values for accuracy metrics.
- **Duplicate publication was checked.** PMIDs 40661348 and 41836608 report the same cohort and the same AUCs (preprint and journal version); they are counted once.
- **The standard-error method was validated against a source.** For PMID 33129241 the Hanley–McNeil formula returns SE = 0.0822 for AUC 0.75 with 18 vs 18 subjects; the article independently reports SE = 0.08.

Full texts themselves are **not** redistributed here — only the extracted data points and their citations. Fetch the sources through their DOIs.

## Known limitations

- Coverage is asymmetric: PubMed for both diseases, plus a Scopus AD arm. The Scopus PD arm and Web of Science have not been searched, so PD estimates rest on PubMed alone and should be treated as provisional. `docs/en/HOW_TO_EXPORT_SCOPUS_WOS.md` gives the ready-to-paste queries; `scripts/09_ingest_scopus_wos.py` merges new exports and deduplicates them.
- Data extraction is restricted to PubMed Central open-access full texts (55 of the 95 eligible primary studies), which may itself select for a non-random subset of the literature.
- Heterogeneity is high (I² up to 95%) and Egger's test is significant in several subgroups; pooled estimates are best read as optimistic bounds.
- Most miRNAs contribute a single study, so the attention-vs-performance analysis is exploratory and cannot support a causal reading.
- The ODE models in `scripts/02` use illustrative, non-calibrated parameters. They are qualitative and generate hypotheses; they are not quantitative predictions and should not be reported as such.

## Scientific integrity and use of AI

This work follows the transparency and reproducibility principles of the USP Guide to Good Scientific Practice (2025). AI tools assisted with organisation, code, retrieval and drafting; they did not replace data curation, verification against sources, or the author's scientific judgement. No data were fabricated. Where a value could not be verified against its source, it was excluded and the exclusion recorded.

## Citation

Capucho, W. *Epigenetics and microRNAs in neurodegenerative disease: systematic review and meta-analysis of circulating miRNA diagnostic accuracy.* GitHub, 2026. https://github.com/WesleyCapucho/-Epigen-tica-e-micrornas-em-doen-as-neurodegenerativas

Literature data are from PubMed/PubMed Central (National Library of Medicine, NCBI). Individual studies are cited by DOI in `data/extracted/diagnostic_accuracy_extraction.csv`.
