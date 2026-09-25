# Epigenetics and microRNAs in neurodegenerative disease

**Reproducibility package for a systematic review and random-effects meta-analysis of the diagnostic accuracy of circulating microRNAs in Alzheimer's disease (AD) and Parkinson's disease (PD).**

> 🇧🇷 **Versão em português: [README.pt-BR.md](README.pt-BR.md)**

**Author:** Wesley Felipe Capucho
Universidade Federal de São Paulo (UNIFESP) — Specialisation in Human Physiology and Pathophysiology applied to Health Sciences.

**Registration:** This systematic review is retrospectively registered on OSF Registries: [https://doi.org/10.17605/OSF.IO/NJ8A5](https://doi.org/10.17605/OSF.IO/NJ8A5).

---

## What this repository is

This repository holds **raw data, scripts, tables and figures**, and nothing else. Its purpose is that every number in the associated manuscript can be regenerated from the files here by running the pipeline. The manuscript itself is written and kept outside this repository.

Two bodies of work live here:

| Layer | What it is | Scripts |
|---|---|---|
| **Bibliometric** | PubMed corpus mining, miRNA extraction, PCA, clustering, miRNA–disease network, exploratory ODE models of the miR-29/BACE1/Aβ and miR-7/SNCA/α-synuclein axes | `01`, `02` |
| **Meta-analytic** | PICO systematic search, PRISMA screening, full-text extraction, random-effects meta-analysis of AUC, clinical-translation landscape | `03`–`11` |
| **Mechanistic** | ODE models of both axes built on published kinetic measurements; structural figures rendered from deposited coordinates; dosing feasibility from measured decay constants; a graphical abstract of both axes; animated GIFs of the same simulations; a composite panel of the structural renders | `12`, `13`, `17`, `18`, `19`, `20` |
| **Appraisal** | QUADAS-2 risk of bias, bivariate sensitivity–specificity synthesis, GRADE certainty of evidence | `14`–`16` |

The meta-analytic layer exists to answer a question the source monograph raised about itself: bibliometric frequency and experimental validation are not independent sources of evidence, because the most-studied miRNAs accumulate both. Pooled diagnostic accuracy is external to that loop.

## Current state of the evidence base

| | |
|---|---|
| Databases searched | PubMed/MEDLINE, Scopus, Web of Science (both disease arms) |
| Unique records | 587 |
| Full texts read | 47 |
| Studies contributing estimates | 45 |
| Extracted estimates | 79 (51 eligible, 41 poolable) |
| Independent studies pooled | 20 |
| Search date | 10 September 2026 (PubMed, Scopus); 23 September 2026 (Web of Science) |
| Studies appraised with QUADAS-2 | 28 |
| Certainty of evidence (GRADE) | Very low |

Pooled estimates live in `results/tables/meta_analysis_pooled_auc.csv`, the per-estimate inputs in `results/tables/meta_analysis_input_estimates.csv`, and the clustering sensitivity analyses in `results/tables/sensitivity_single_mirna.csv`. Every extracted value is traceable to a verbatim sentence from its source in `data/extracted/diagnostic_accuracy_extraction.csv`.

Interpretation belongs in the manuscript, not here. Two things do belong here, because they are properties of the data rather than of the argument:

- **Estimates within a study are correlated.** One study contributes eight estimates and another six, and the random-effects model treats each as independent. `scripts/05` therefore also re-pools one-estimate-per-study and leave-one-study-out, and the spread between them is part of the result.
- **Twelve defects were found and corrected in this pipeline.** They are recorded in `data/processed/prisma_flow.json` and in the header comments of the scripts that carry the fix. See *Corrections* below.

## Repository layout

```
.
├── data/
│   ├── raw/
│   │   ├── pubmed/                    # Bibliometric sample, live from NCBI (provenance in manifest.json)
│   │   ├── systematic_review_2026/    # Search strategy, screening corpus and decisions,
│   │   │                              #   Scopus exports, mention counts, prior meta-analyses
│   │   ├── clinical_trials_2026/      # ClinicalTrials.gov landscape of miRNA-directed therapeutics
│   │   ├── kinetics_2026/             # Supplementary data tables: genome-wide half-lives (Schwanhäusser 2011),
│   │   │                              #   presynaptic protein copy numbers (Wilhelm 2014, table S1),
│   │   │                              #   neuronal 3'UTR isoform half-lives (Tushev 2018, table S1)
│   │   └── structures_2026/           # Deposited coordinates: 6N4O, 4D8C, 6CU7, 5OQV
│   ├── extracted/                     # Diagnostic-accuracy extraction table, kinetic-parameter table,
│   │                                  #   both with verbatim source quotes
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
│   ├── 11_attention_finding_audit.py              # Decomposes what moved the attention correlation
│   ├── 12_ode_models_calibrated.py                # ODE models on published kinetic constants
│   ├── 13_structure_figures.py                    # PyMOL figures from deposited structures
│   ├── 14_quadas2_risk_of_bias.py                 # QUADAS-2, judgements derived by rule
│   ├── 15_bivariate_srocc.py                      # Reitsma bivariate model + summary ROC
│   ├── 16_grade_certainty.py                      # GRADE certainty + summary of findings per 1000
│   ├── 17_mimic_dosing_feasibility.py             # What repeated dosing costs a fast-decaying mimic
│   ├── 18_graphical_abstract.py                   # Schematic figure: both axes, computed numbers
│   ├── 19_mechanism_animations.py                 # Animated GIFs of already-simulated mechanisms
│   ├── 20_structure_story_panel.py                # Composites scripts/13's renders into one figure
│   ├── _bilingual.py                              # Shared helper: every figure emitted in EN and pt-BR
│   └── tools/mirror_extraction_json.py            # Regenerates the JSON mirror of the extraction table
├── docs/
│   ├── en/                            # Methods, data dictionary, PRISMA-DTA checklist, Scopus/WoS export
│   └── pt-BR/                         # Métodos, dicionário de dados, checklist PRISMA-DTA, exportação
├── results/
│   ├── figures/                       # Forest, funnel, attention-vs-accuracy, SROC, QUADAS-2, GRADE,
│   │                                  #   dosing and ODE overview — each twice, .en.png and .pt-BR.png;
│   │                                  #   structures/ (PyMOL renders)
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
python scripts/14_quadas2_risk_of_bias.py
python scripts/15_bivariate_srocc.py
python scripts/16_grade_certainty.py               # needs 14 and 15 to have run
python scripts/08_verify_consistency.py           # must pass before committing

# Mechanistic layer, offline
python scripts/12_ode_models_calibrated.py
python scripts/17_mimic_dosing_feasibility.py
python scripts/19_mechanism_animations.py
pip install pymol-open-source                     # only needed for scripts/13
python scripts/13_structure_figures.py
python scripts/18_graphical_abstract.py     # needs 12, 17 and 13 to have run
python scripts/20_structure_story_panel.py
```

`scripts/05`, `06`, `08`, `10` and `11` run entirely offline from the committed data. `scripts/03` calls the live PubMed API and will legitimately return more records than the frozen 2026-09-10 counts, because the literature keeps growing; `data/raw/systematic_review_2026/search_strategy.json` preserves the counts behind the reported numbers.

Scopus cannot be queried by API from a script — it requires institutional authentication. Run the search in the Scopus web interface, export the result set, and hand the file to `scripts/09`. The ready-to-paste queries are in `docs/en/HOW_TO_EXPORT_SCOPUS_WOS.md`.

For the bibliometric layer, run `scripts/01` first: it produces the input of `scripts/02`.

## Data provenance and integrity

- **Every number came from a real source.** PubMed records were pulled from the NCBI E-utilities API; accuracy values were read from open-access full texts in PubMed Central or from the abstract when no full text was reachable. Nothing was simulated, estimated to fill a gap, or carried over from a secondary citation.
- **Every extracted value stores its source sentence.** `diagnostic_accuracy_extraction.csv` carries a `verbatim_quote` column with the exact wording supporting each AUC, sensitivity and specificity, plus PMID and DOI.
- **Values that could not be resolved unambiguously were kept and flagged, not quietly dropped.** 28 of the 79 extracted rows are marked `eligible_primary_pool = no` with an explicit `exclusion_reason`.
- **Automated text mining was used to *find* candidate values, never to record them.** Regular expressions surfaced sentences; values were then read and transcribed by hand, because the patterns demonstrably mis-pair sensitivity with specificity and mistake p-values for accuracy metrics.
- **Duplicate publication was checked.** PMIDs 40661348 and 41836608 report the same cohort and the same AUCs (preprint and journal version); they are counted once.
- **The standard-error method was validated against a source.** For PMID 33129241 the Hanley–McNeil formula returns SE = 0.0822 for AUC 0.75 with 18 vs 18 subjects; the article independently reports SE = 0.08.
- **`scripts/08` enforces all of this.** It recomputes each derived number from its source and fails if the extraction table, the PRISMA counts and the result tables disagree. 1737 checks currently pass.

- **The kinetic parameters follow the same rule.** `data/extracted/kinetic_parameters.csv` holds 67 rows from 15 primary sources. Every measured value carries the sentence it was read from, and `scripts/08` checks that the number actually appears in that sentence. A parameter that was looked for and not found is recorded as a `declared_gap` with no value and no borrowed citation, and the ODE code refuses to load it. Two rows are `derived` (genome-wide medians computed from the archived Schwanhäusser table); `scripts/08` recomputes them from the file.
- **Structure figures quote their deposition.** `scripts/13` reads title, method, resolution and primary citation from each coordinate file and stops if the title does not match the molecule the figure claims to show. The citation parser skips the PDB's own deposition DOI, which is easy to mistake for the article's.

Full texts are **not** redistributed here — only extracted data points and their citations. Fetch sources through their DOIs.

## Corrections

Twelve defects in this pipeline were found after results had already been produced. Each is fixed, and each changed a reported number. They are listed here rather than quietly patched, because a reproducibility package that hides its own corrections is not one.

| Defect | Effect | Fixed in |
|---|---|---|
| Screening regex closed with `\b` after `meta-analys`, so it never matched "meta-analysis" | Self-declared meta-analyses passed as primary studies; one record reclassified; it is why prior meta-analyses went unnoticed | `scripts/04` |
| miRNA mention counts computed over 234 PubMed records while AUCs came from the 560-record corpus | Markers entering via Scopus were credited zero mentions by construction, inflating the attention–performance correlation | `scripts/10` |
| Studies keyed on PMID alone | The four studies published outside MEDLINE collapsed into one blank-PMID group; two independent miR-124 cohorts counted as one; study totals understated | `scripts/05`, `scripts/06` |
| Biofluid subgroups required three *estimates*, not three *studies* | Produced a subgroup of eight estimates from a single cohort — within-study spread reported as between-study evidence | `scripts/05` |
| `scripts/09` deduplicated only against PubMed | The Scopus PD arm appeared to add 157 new records instead of 78 | `scripts/09` |
| `scripts/09` read the PubMed DOI only as `DOI`, while the corpus stores it as `doi` | DOI deduplication against the whole PubMed half was inert; one article entered twice under two typesettings of its own title | `scripts/09` |
| `scripts/09` deduplicated an arm against a corpus that already contained it | Re-ingesting an arm returned zero new records and emptied its file; the documented pipeline destroyed data when run twice | `scripts/09` |
| `scripts/09` named its output from `--arm` alone and excluded it from deduplication | Reusing a label across databases silently replaced the earlier arm; ingesting Web of Science as `--arm AD` would have deleted 248 Scopus records | `scripts/09` |
| `scripts/04` read the corpus as PubMed-shaped only, and overwrote `prisma_flow.json` wholesale | It crashed on the first imported record, and had it not crashed it would have replaced the curated PRISMA record with five keys | `scripts/04` |
| `scripts/10` counted every imported record as Scopus | With Web of Science ingested this would have put a false per-database count in the methods | `scripts/10` |
| The AD-arm PubMed search reported 168 records, but only 167 were ever fetched and archived; every document quoted the unarchived 168 | The AD-arm count, and the methods text quoting it, disagreed with the actual archived PMIDs; found while auditing the OSF registration text against the repository | `scripts/03` output, `data/processed/prisma_flow.json` |
| `first_author` held a placeholder string (`(Turk J Biochem)`, `(APMIS)`) instead of a name, for two rows added from Scopus only | Went unnoticed by every existing check, since none read `first_author`, until building a per-study citation table for the manuscript surfaced it | `data/extracted/diagnostic_accuracy_extraction.csv`, `scripts/08` |

`scripts/11_attention_finding_audit.py` quantifies the second of these: it recomputes the attention–performance correlation under each combination of inputs and separates the contribution of the bug from that of the new data.

## Known limitations

- **Web of Science has now been searched**, on 23 September 2026, under institutional authentication and thirteen days later than the other two databases — which is reported as its own search date rather than folded into theirs. It returned 295 records across the two arms, of which **27 were new**, and **none of them entered the primary pool**: one measures a long non-coding RNA rather than a microRNA, one measures post-mortem cortex rather than a circulating biofluid, and the one record that does match the PICO reports its AUC only as the inequality "AUC>0.90" and has no DOI, no PubMed ID and no reachable full text to confirm a value. All three are recorded in the extraction table with their exclusion reasons (E077–E079) rather than dropped. The pooled estimates, the bivariate operating point, the QUADAS-2 table and the GRADE rating are byte-identical before and after.
- Extraction is restricted to open-access full texts and abstracts, which may select a non-random subset of the literature; four Parkinson-arm studies were access-restricted such that only a combined-model AUC could be read.
- 34 of the 41 weighted standard errors are reconstructed by Hanley–McNeil rather than taken from a published interval.
- Heterogeneity is high (I² up to 97%) and estimates within studies are correlated, which also makes Egger's test unreliable here.
- Most miRNAs contribute a single study, so the attention-vs-performance analysis is underpowered in both directions.
- **The review was not registered and has no prospective protocol.** The search, eligibility rules and screening decisions are frozen in the repository as applied, which makes them auditable but not pre-specified. See `docs/en/PRISMA_DTA_CHECKLIST.md`, item 5.
- **Screening had no independent second reviewer**, and no inter-rater agreement statistic exists.
- **All four QUADAS-2 risk-of-bias domains are now rated**, the last two from a second pass over the full texts (`data/extracted/quadas2_study_level.csv`). What that pass found is itself a limitation of this literature: of the 22 studies with a retrievable full text, **one** has neuropathological confirmation of the diagnosis, **one** states that diagnosis was blind to the index test, and **none** reports a STARD flow diagram. Six studies have no retrievable full text and are unclear for that stated reason.
- **Every estimate in the primary pool is a case-versus-healthy-control contrast**, the design QUADAS-2 flags as inflating accuracy. This is partly by construction, since the eligibility rule required that contrast; 13 estimates from 9 studies using a differential-diagnosis, prodromal or within-disease contrast were excluded for not matching the PICO.
- **Certainty of evidence is very low** (GRADE for diagnostic accuracy): six downgrade steps from *high*, for risk of bias (−2), inconsistency (−2, I² = 95.7%), indirectness (−1) and publication bias (−1). At a 5% pre-test probability the summary operating point calls about 301 people positive per 1000 and 261 of them are wrong (PPV 0.13). Every threshold behind those judgements is a named constant in `scripts/16`, movable and rerunnable.
- At the bivariate summary operating point (9 studies, sensitivity 0.80, specificity 0.72) the likelihood ratios are 2.9 positive and 0.28 negative. A pooled AUC near 0.78 reads better than the operating point it comes from. The 2×2 tables behind it are reconstructed from published proportions and group sizes, because the source articles report no counts.
- The ODE models in `scripts/02` use illustrative, non-calibrated parameters and are kept only as part of the original monograph. They are superseded by `scripts/12`.
- `scripts/12` uses measured constants where they exist, but they come from different systems (human CSF, HEK cells, rat and mouse neurons, SH-SY5Y, fibroblasts). Two parameters were never measured for these genes and are left free, declared, and scanned over a range rather than tuned. mRNA decay was the third until the Tushev supplementary table was read; it is now measured per gene. The Aβ42 aggregation rate constants cannot be separated from one another with the published data (row K037), and α-synuclein nucleation at acidic pH is reported only qualitatively (K042). These are fixed at declared illustrative values. As a result, the size of the α-synuclein pH switch is not a result: across the sweep in `scripts/12` it ranges from about 500-fold to about 14,000-fold. Only its direction is.
- The model's clearest number, a 1.41-fold higher Aβ monomer level in AD, is fixed analytically by the production and clearance rates of Mawuenyega et al. 2010 and does not depend on any free parameter. It restates that measurement in model form; it is not an independent prediction.
- The comparison between the miR-29 dose the model asks for and the knockdown Hébert et al. measured crosses systems: a steady state in a model of human brain against a transient transfection of a neuroblastoma line. It answers whether the required intervention is larger or smaller than one already achieved in cells, and nothing more.
- The structure figures are illustration. They test nothing. Resolutions come from different criteria (6CU7 FSC 0.5, 5OQV FSC 0.143) and are not directly comparable.
- `scripts/17` assumes a delivered mimic is cleared at the same first-order rate as the endogenous species. A chemically stabilised mimic would not be, which is exactly why its output is a **required** fold stabilisation (20× for miR-7 to tolerate daily dosing) rather than a verdict on feasibility. The calculation has no free parameter — the dose cancels out of the peak-to-average ratio — but it is a statement about pharmacokinetics in the abstract, not about any particular delivery vehicle or tissue.
- `scripts/19` animates three of the mechanisms above (Aβ42 reaching its new steady state, a single-dose washout, the repeated-dosing sawtooth) by reusing the exact functions from `scripts/12` and `scripts/17`, not by re-deriving them — each GIF's final frame is checked against the same JSON the static figures are checked against. It deliberately does **not** animate the α-synuclein pH-gate fibril growth, because that curve's acidic-pH rate constant is declared illustrative (K042, qualitative only): putting a specific speed on screen for a quantity this project reports only as a direction, not a magnitude, would be more misleading in motion than it already is standing still. These GIFs are illustration of simulations already in this repository, not a new experiment.

## Scientific integrity and use of AI

This work follows the transparency and reproducibility principles of the USP Guide to Good Scientific Practice (2025). AI tools assisted with organisation, code, retrieval and drafting; they did not replace data curation, verification against sources, or the author's scientific judgement. No data were fabricated. Where a value could not be verified against its source, it was excluded and the exclusion recorded.

## Citation

Capucho, W. *Epigenetics and microRNAs in neurodegenerative disease: systematic review and meta-analysis of circulating miRNA diagnostic accuracy.* GitHub, 2026. https://github.com/WesleyCapucho/-Epigen-tica-e-micrornas-em-doen-as-neurodegenerativas

Literature data are from PubMed/PubMed Central (National Library of Medicine, NCBI) and Scopus (Elsevier). Individual studies are cited by DOI in `data/extracted/diagnostic_accuracy_extraction.csv`.
