# Data dictionary

🇧🇷 Versão em português: [../pt-BR/DICIONARIO_DE_DADOS.md](../pt-BR/DICIONARIO_DE_DADOS.md)

---

## `data/extracted/diagnostic_accuracy_extraction.csv`

The core dataset of the meta-analysis: one row per reported diagnostic-accuracy estimate. Also available as `.json`.

| Column | Type | Description |
|---|---|---|
| `record_id` | string | Internal identifier of the extraction row (E001…) |
| `pmid` | string | PubMed identifier of the source study |
| `doi` | string | DOI of the source study |
| `first_author` | string | Surname and initials of the first author |
| `year` | integer | Publication year |
| `journal` | string | Journal title |
| `disease` | enum | `AD`, `PD`, `mixed_neurodegenerative` |
| `comparison` | free text | Contrast as described by the source article |
| `comparison_class` | enum | `case_vs_healthy_control`, `differential_diagnosis`, `prodromal_vs_control`, `within_disease` |
| `biofluid` | enum | `serum`, `plasma`, `CSF`, `whole_blood`, `blood`, `serum_exosome`, `CSF_exosome`, `plasma_EV`, `plasma_sEV`, `plasma_neuronal_EV`, `extracellular_miRNA`, `gastric_juice` |
| `marker_type` | enum | `single_miRNA` or `multi_miRNA_panel` |
| `marker` | string | miRNA name, or a description of the panel |
| `cohort_stage` | enum | `discovery`, `training`, `validation`, `single`, `cross-validated`, `unclear` |
| `n_cases` | integer | Number of patients in the contrast (blank if not stated) |
| `n_controls` | integer | Number of controls in the contrast (blank if not stated) |
| `auc` | float | Area under the ROC curve, as published |
| `auc_ci_low` / `auc_ci_high` | float | 95% CI bounds, only when the source reports them |
| `sensitivity` / `specificity` | float | Proportions (not percentages), only when unambiguous in the source |
| `method` | string | Measurement platform (RT-qPCR, small RNA-seq, microarray, ddPCR…) |
| `eligible_primary_pool` | enum | `yes` / `no` — whether the row enters the primary meta-analysis |
| `exclusion_reason` | free text | Why an ineligible row was excluded (blank when eligible) |
| `note` | free text | Caveats: truncated CI, missing group size, duplicate publication… |
| `verbatim_quote` | free text | **The exact sentence from the source article that supports the values in this row** |
| `source` | string | Where the full text came from (PubMed Central open access) |

**Reading rule.** No numeric cell in this file should be trusted without its `verbatim_quote`. If a quote does not support a value, the value is an error and should be reported as such.

## `data/extracted/extraction_audit_log.csv`

Every change the 28 September 2026 full-text second pass made to `diagnostic_accuracy_extraction.csv` and `quadas2_study_level.csv`, one row per field changed. `scripts/08` replays the log against the current tables and fails if a logged new value is no longer what the table holds.

| Column | Description |
|---|---|
| `audit_pass` | Which pass made the change |
| `record_id` | Extraction row (E###) or `study <id> (quadas2_study_level)` |
| `first_author`, `year` | For reading |
| `action` | `corrected`, `added` (a new row), `removed` (a study-level row) or `flagged` (kept as published, marked for a sensitivity analysis) |
| `field`, `old_value`, `new_value` | The change itself |
| `reason` | Why |
| `source_quote` | The sentence from the full text that justifies the change |

## `data/extracted/study_design_preanalytics.csv`

One row per eligible study (27), recorded in the second full-text pass with short quotes from the source. Studies without a retrievable full text are `not_assessable_no_fulltext` in every design field rather than guessed. `scripts/08` checks every value against the closed vocabularies below.

| Column | Values |
|---|---|
| `reference_standard_basis` | `clinical_criteria`, `biomarker_supported`, `neuropathological`, `not_reported` |
| `sample_source` | free text (single-centre clinic, biobank, commercial biorepository, public dataset re-analysis, ...) |
| `disease_stage` | `early`, `mixed`, `established`, `not_reported` |
| `medication_status` | `drug_naive`, `treated`, `mixed`, `not_reported` |
| `haemolysis_handling` | `measured_and_excluded`, `excluded_method_not_stated`, `procedural_only`, `not_reported`, `not_applicable_whole_blood` |
| `normalization` | endogenous small RNA, endogenous miRNA, spike-in, combinations, sequencing library size, positive-control miRNAs, `none_raw_ct` |
| `candidate_selection` | `a_priori_literature`, `separate_discovery_sample`, `training_split_only`, `same_sample_data_driven` |
| `validation_design` | `none_single_sample`, `separate_discovery_then_roc_in_evaluation_sample`, `internal_resampling`, `random_split_holdout`, `independent_cohort_locked_model` |
| `threshold_prespecified` | `no` for every study with a full text |
| `key_quotes`, `note` | Supporting sentences, pipe-separated; free-text note |

## `data/extracted/molecular_evidence_map.csv`

One row per mechanistic claim made by a study in the primary pools (37 studies, 65 rows), read from the full text or, for two studies, marked as abstract only. Written by hand from the full texts on 2026-09-28 and read by `scripts/27_molecular_evidence_map.py` (figure) and `scripts/08` (coverage check).

| Column | Values |
|---|---|
| `study_id`, `first_author`, `year`, `disease` | Study identifiers, keyed like the selection audit |
| `pooled_marker` | The marker selected for the primary pool |
| `mirna`, `target_or_pathway` | The microRNA(s) the claim concerns and the proposed target or pathway |
| `biological_axis` | The disease axis the claim belongs to; `none` when no claim is made |
| `evidence_type` | `experimental_in_included_study`, `experimental_cited_from_authors_prior_work`, `literature_cited`, `in_silico_prediction`, `clinical_correlation`, `paired_brain_tissue`, `none_reported`, `none_reported_abstract_only` |
| `model_system` | Cell line, assay or data source behind the claim |
| `source_quote` | Verbatim sentence from the full text (empty only for `none_*`) |
| `source`, `note` | PMC identifier or abstract source; free-text note |

## `data/extracted/recall_check_decisions.csv`

One row for each of the 227 primary studies whose abstract gave no accuracy statement, written for the recall check of 28 September 2026 (`scripts/30_recall_check.py`). `triage` is `candidate` for the 90 that look like case-control studies of circulating microRNAs in AD or PD on title and abstract (the rule is in the script and is re-derived on every run) and `not_candidate` for the rest. For candidates: `pmcid` (empty when there is no PubMed Central full text), `fulltext_read` (`yes`, or `no` when the full text could not be retrieved or does not exist), `decision` (`eligible`, `reports_accuracy_but_not_primary`, `not_eligible`, `fulltext_unavailable` or `not_assessed_no_open_fulltext`), `decision_reason` and `decision_quote`, the sentence the decision rests on. The estimates read from the eligible and accuracy-reporting papers are in `diagnostic_accuracy_extraction.csv` from record E090 onwards, each with its own source sentence, and were checked against the full text by a second reader before being accepted.

## `results/tables/recall_check_summary.json`

The counts of the recall check recomputed by `scripts/30_recall_check.py` from the file above; `scripts/08` requires them to equal the `recall_check` block of `data/processed/prisma_flow.json`.

## `data/extracted/post_search_candidates.csv` and `results/tables/post_search_sensitivity.csv`

A study that entered PubMed between the search date and 28 September 2026 and meets the eligibility criteria, available as an abstract only (Jeong et al. 2026, two assay variants of one panel). It is not in the primary analysis. `scripts/31_post_search_sensitivity.py` adds it to the primary AD selection, once with each variant, and writes the pooled AUC with and without it.

## Two-disease reports

Two reports (Mancuso et al. 2019 and Sandau et al. 2026) analyse both diseases. Their AD rows carry the real PMID; their PD rows carry an empty `pmid` and the DOI with the suffix `#PD`, so that `study_id` (PMID when present, DOI otherwise) treats each disease as its own study and each disease pool receives at most one estimate from the report.

## `data/second_reviewer/second_reviewer_packet.xlsx`

The workbook for the independent second reviewer, written by `python scripts/29_second_reviewer_packet.py build`: a seeded random sample of 120 screened records (decisions hidden), the QUADAS-2 sheet with the first reviewer's judgements hidden, and every pooled estimate with its stored value and source sentence for verification. `python scripts/29_second_reviewer_packet.py agree <returned file>` writes `results/tables/second_reviewer_agreement.csv` (percent agreement and Cohen's kappa).

## `results/tables/ci_plausibility_check.csv`

Every extracted row with both a reported CI and group sizes: the SE implied by the CI, the Hanley-McNeil SE for the same AUC and group sizes, their ratio, and whether the row falls below `CI_PLAUSIBILITY_RATIO` (0.5, `scripts/05`). Only the two Li Y 2024 rows are flagged (ratios 0.049 and 0.056); every other ratio lies between 0.80 and 1.38.

## `results/tables/robustness_*.csv`, `panel_subgroup_audit.csv`, `sens_spec_label_check.csv`, `study_design_profile.csv`

Written by `scripts/26_robustness_analyses.py`. `robustness_alternative_analyses.csv`: AD, PD, combined and panel/single pools under the primary rule, the marker-type-neutral rule and the reported intervals as published, with the panel-versus-single Q and p. `robustness_random_selection.csv`: median and 2.5th/97.5th percentiles of the pooled AUC and of the panel-versus-single p over 2,000 AUC-blind random selections (seed 20260928), with the fraction of draws below p = 0.05. `robustness_leave_one_out_by_disease.csv`: per-disease leave-one-study-out. `panel_subgroup_audit.csv`: each panel study's AUC, interval, n, SE source, weight and source. `sens_spec_label_check.csv`: whether published sensitivity and specificity are integer-consistent with the group sizes as labelled or only swapped. `robustness_bivariate_label_check.csv`: the bivariate model with and without studies flagged there. `study_design_profile.csv`: counts of each design value among pooled and among all eligible studies. `robustness_validation_split_exploratory.csv`: pooled AUC by whether the selected estimate came from a separate validation sample (descriptive only). `robustness_summary.json`: seed, number of draws, plausibility ratio, flagged studies.

## `data/raw/systematic_review_2026/search_strategy.json`

Frozen record of the searches: for each arm, the query as submitted, PubMed's own query translation, the date filter, the total number of matching records on the search date, and the full list of retrieved PMIDs.

## `data/raw/systematic_review_2026/screening_decisions.csv`

One row per screened record (234 rows).

| Column | Description |
|---|---|
| `pmid`, `doi`, `pmcid`, `year`, `journal`, `title` | Record identification |
| `search_arm` | `AD`, `PD` or `AD+PD` (retrieved by both arms) |
| `article_types` | PubMed publication types |
| `is_review_or_secondary` | Classified as secondary literature |
| `abstract_reports_auc` / `_sensitivity` / `_specificity` | Whether the abstract states each metric |
| `pmc_fulltext_available` | Open-access full text available in PubMed Central |

## `data/raw/systematic_review_2026/mirna_mention_counts.csv`

| Column | Description |
|---|---|
| `mirna` | miRNA label as written (normalised: `hsa-` dropped, dashes unified) |
| `family` | Family after collapsing the arm suffix (`miR-146a-5p` → `miR-146a`) |
| `n_articles_mentioning` | Distinct corpus articles mentioning that exact label |
| `n_articles_mentioning_family` | Distinct corpus articles mentioning any member of the family |

Counts are of **distinct articles**, never of raw occurrences.

## `data/raw/systematic_review_2026/exports/`

The database exports this review was built from, archived exactly as downloaded: `scopus_AD_2026-09-10.csv`, `scopus_PD_2026-09-10.csv`, `wos_AD_2026-09-23.txt`, `wos_PD_2026-09-23.txt`. Scopus and Web of Science require an authenticated institutional session and cannot be queried by API from this project, so the export is the primary record of what the search returned. Web of Science files are tab-delimited full records carrying the two-letter field tags (`TI`, `AB`, `DI`, `PM`, `PY`, `SO`, `AU`, `DT`, `DE`); `scripts/09` also accepts the long column names.

## `data/raw/systematic_review_2026/additional_records_*.json`

One file per ingested database arm, named from the `--arm` label: `AD` and `PD` hold the Scopus arms, `AD_wos` and `PD_wos` the Web of Science arms. Each record carries `Title`, `Abstract`, `DOI`, `PMID`, `Year`, `Journal`, `Authors`, `PublicationTypes`, `Keywords` and `database`. Deduplication happens on the way in, against the PubMed corpus and against every arm already ingested. Each database needs its own label: the file name comes from the label alone, so reusing one across databases would replace the earlier arm, and `scripts/09` refuses it.

## `data/raw/pubmed/`

Bibliometric sample from the original monograph layer, pulled live from the NCBI API on 2026-09-10. `manifest.json` records the exact query, access date, the real total number of matching records in PubMed, and an explicit no-fabrication statement.

## `results/tables/meta_analysis_pooled_auc_primary.csv`

The PRIMARY analysis, circulating (blood-derived) studies only: every study reduced to one estimate per subgroup first, by a fixed, AUC-blind priority rule (see `scripts/_study_selection.py`: prefer a row evaluated in a separate validation sample, then the study's own multi-miRNA panel over its component markers, then the larger combined sample size, then an alphabetical tiebreak), pooled between studies with Paule-Mandel tau-squared. AD and PD are separate primary rows; the combined AD+PD row is labelled SECONDARY. Cerebrospinal-fluid studies are never in this table; see `results/tables/csf_secondary_estimates.csv`.

| Column | Description |
|---|---|
| `subgroup` | Which subset was pooled (PRIMARY 1 = AD, PRIMARY 2 = PD, SECONDARY = AD+PD combined) |
| `n_studies` | Independent studies contributing (equals k after one-per-study selection) |
| `n_estimates_collapsed` | Sum of each contributing study's own candidate-row count (see `one_estimate_per_study_selection_audit.csv`) |
| `n_studies_with_multiple_estimates` | How many of those studies had more than one qualifying row to choose from |
| `pooled_auc` | Random-effects pooled AUC, back-transformed from logit |
| `ci_low_wald`, `ci_high_wald` | Standard Wald 95% CI |
| `ci_low_hk`, `ci_high_hk` | modified Hartung-Knapp (mHK) 95% CI (the one reported in text and figures) |
| `pi_low`, `pi_high` | 95% prediction interval (k >= 3 only) |
| `tau2_PM` | Paule-Mandel between-study variance on the logit scale |
| `I2_percent`, `Q`, `df`, `p_heterogeneity` | Heterogeneity statistics (Q from DerSimonian-Laird, reported regardless of which tau-squared feeds the pooled estimate) |
| `egger_intercept_one_per_study`, `egger_p_one_per_study` | Egger's test on the one-per-study rows (k >= 3); exploratory, underpowered below ten studies |

## `results/tables/one_estimate_per_study_selection_audit.csv`

One row per circulating study in the primary pool: which estimate the pre-specified, AUC-blind priority rule selected, and the exact reason it won (`selection_reason`), so the choice can be checked against the raw extraction table and was never made by picking the highest AUC.

## `results/tables/csf_secondary_estimates.csv`

The SE-estimable cerebrospinal-fluid estimates (Lusardi 2017 and Sandau 2020 in AD, Marques 2016 in PD) held out of every pooled AUC because CSF is not a peripheral circulating biofluid. A fourth CSF study (Dos Santos 2018) reports its AUC on a test split of unreported size and has no estimable SE. They are reported narratively, not meta-analysed.

## `results/tables/meta_analysis_pooled_auc_sensitivity_every_estimate.csv`

The analysis that was previously reported as primary: every qualifying circulating row treated as an independent observation, pooled with DerSimonian-Laird tau-squared. Kept as a labelled sensitivity check on the unit-of-analysis choice above. Same column schema as the pre-existing table (`subgroup`, `k_estimates`, `n_studies`, `pooled_auc`, `ci_low`, `ci_high`, `tau2_logit`, `I2_percent`, `Q`, `df`, `p_heterogeneity`, `egger_intercept`, `egger_p`).

## `results/tables/meta_analysis_variance_source_comparison.csv`

For each primary disease outcome, the pooled AUC restricted to studies with a directly reported CI/SE (`reported_only`) against the full primary pool that also includes Hanley-McNeil reconstructed variances (`full`), so a reader can see how much the reconstruction (30 of 39 circulating estimates) actually changes the answer versus how few studies (2 for AD, 3 for PD) reported a usable interval of their own.

## `results/tables/subgroup_difference_test.csv`

Formal test for a panel-versus-single difference (Borenstein et al., 2009, ch. 19: `Q_between = Q_all - Q_single - Q_panel`, 1 df), computed on the one-per-study primary rows, within AD, within PD, and combined. Valid only because the one-estimate-per-study selection assigns every study to exactly one marker type, so the two groups compared are disjoint by construction; see the docstring of `subgroup_difference_test` in `scripts/05_meta_analysis.py`.

## `results/tables/meta_analysis_input_estimates.csv`

The 39 poolable circulating estimates with the standard error used for each and, critically, `se_source`: `reported_95CI` when derived from a published interval, `Hanley-McNeil` when computed from group sizes, and `Hanley-McNeil (reported CI implausibly narrow)` when a published interval was set aside by the plausibility rule (see `ci_plausibility_check.csv`).

## `results/tables/arithmetic_audit.csv`

Every core sample-size and study count used anywhere in the manuscript's Methods, Results or Discussion (from the 587 identified records down to the 11 circulating studies in the bivariate synthesis), reconciled in one table by `scripts/25_arithmetic_audit.py`, which reads each figure live from the same tables and JSON the rest of the pipeline already produces and asserts that every subtotal named in `reconciles_as` actually sums to the row it names before writing the file. `scripts/08_verify_consistency.py` additionally recomputes a subset of these same figures independently, straight from the extraction table, and fails if they disagree. Reproduced as Supplementary Table S4, read live from this file rather than transcribed.

| Column | Description |
|---|---|
| `label` | The count being reported; a leading double space marks it as a sub-count of the row immediately above it at the next level up |
| `value` | The count itself |
| `reconciles_as` | The arithmetic relationship to nearby rows this value is checked against, where one applies |
| `source` | The file this value was read from |

## `results/tables/citation_frequency_vs_auc.csv`

Per miRNA family: mean reported AUC, number of contributing studies, min/max AUC, and number of corpus articles mentioning it.

## `data/extracted/kinetic_parameters.csv`

Rate constants, half-lives and concentrations used by `scripts/12`, one row per parameter per source. 67 rows from 15 primary sources.

| Column | Type | Description |
|---|---|---|
| `param_id` | string | Identifier (K001…). `scripts/12` loads parameters by this id, never by position |
| `kind` | enum | `numeric` (a number printed in the source), `qualitative_constraint` (a statement with no usable number, e.g. "undetectable"), `declared_gap` (searched for and not found), `derived` (computed by us from a primary table) |
| `axis` | enum | `miR-29/BACE1/Abeta`, `miR-7/SNCA/alpha-synuclein`, `both` |
| `parameter` / `symbol` | string | What the value is, and the symbol the model uses |
| `value_as_written` | string | The value exactly as printed in the source. For `numeric` and `qualitative_constraint` it must appear inside `verbatim_quote` |
| `value_si` | float | The same value converted to the model's units. Blank for qualitative constraints and gaps |
| `unit_si` | enum | `1/hour`, `M`, `M^-1 s^-1`, `molecules per cell`, `uM`, `um^3`, `fold`, `fractional change`, `fractional increase`, `fraction of patients`, `dimensionless` |
| `unit_as_written` | string | Unit as printed in the source |
| `population` / `condition` | free text | Who or what was measured, and under which experimental condition. A rate constant without its condition is rejected by `scripts/08` |
| `n` | string | Sample size as reported |
| `method` | free text | Measurement technique |
| `species` | string | Organism or system (human CSF, cell line, rat or mouse neurons, recombinant protein in vitro…) |
| `pmid` / `doi` / `first_author` / `year` / `journal` | | Citation of the primary source |
| `verbatim_quote` | free text | **The sentence the value was read from.** Empty for `derived` and `declared_gap` rows, on purpose |
| `source` | string | Where the text was read (PMC full text, supplementary PDF or table supplied by the author of this repository, Scite full text) |
| `note` | free text | Conversions, caveats, and for `derived` and `declared_gap` rows, how the value was computed or how the search was done |

**Reading rules.**
- A `declared_gap` row carries no value, no quote and no citation. It records that a number was looked for and not found, and where. The ODE code refuses to load it.
- A `derived` row is **not** a number printed by its source. Its derivation is in `note`, and `scripts/08` recomputes it from the archived table in `data/raw/kinetics_2026/`.
- K038 and K039 record values from a model that the source paper itself rejects. They are kept as warnings and not used.
- A value printed in a figure or in a figure's table is recorded with that row or label as its quote, and `note` says which figure it was read from. A value that exists only as a position on a plotted curve is not recorded at all.
- K052 and K054 are the reason the `derived` kind exists. Wilhelm et al. report α- and β-synuclein together (K052) and, in a footnote, the ratio between them (K053); neither is an α-synuclein concentration on its own. K054 combines the two and says so, and `scripts/08` recomputes it. Quoting K052 as α-synuclein would overstate it twofold.

## `data/raw/kinetics_2026/tushev_2018_table_S1.xls`

Supplementary Table S1 of Tushev et al. 2018 (Neuron, DOI 10.1016/j.neuron.2018.03.030): 24,435 3'UTR isoforms with gene symbol, cell-type enrichment, compartment localisation and a `half.life[hours]` column, the processed data the paper's own availability statement points to. `scripts/08` looks up the SNCA, BACE1 and APP rows again from this file and recomputes the pooled BACE1 decay constant. Read it with two cautions, both recorded in the rows that use it: the decay was observed over 16 h, so a quarter of the isoforms carry half-lives beyond the window and the largest reach 18,858 h; and the paper's neuron-enriched summary reproduces only when values above about 25 h are excluded, while the glia summary does not reproduce at all.

## `data/raw/kinetics_2026/wilhelm_2014_table_S1.xlsx`

Additional Data Table S1 of Wilhelm et al. 2014 (Science, DOI 10.1126/science.1252884): quantitative immunoblot measurements of 64 presynaptic proteins, with percentage of total protein, copy number per synapse (mean ± SEM of four preparations), molar concentration and footnotes. The legend is embedded in the sheet as an image. Concentrations were computed by the authors over the synaptic volume minus the mitochondrial volume; `scripts/08` confirms this by recomputing the implied volume from each copy number and concentration pair and comparing it against K050 minus K057, read from Figure 1C of the same paper.

## `data/raw/kinetics_2026/schwanhausser_2011_supplementary_table.xls`

Supplementary table of Schwanhäusser et al. 2011 (Nature, DOI 10.1038/nature10098): genome-wide mRNA and protein half-lives, copy numbers and synthesis rates in mouse NIH3T3 fibroblasts, 5028 rows. Archived unchanged. The file metadata show it was last modified in November 2012; the paper's corrigendum (DOI 10.1038/nature11848) came out in February 2013, and it has not been confirmed whether this is the corrected version. Used only for the genome-wide medians (K040, K041) and to confirm that BACE1 and SNCA are absent (K030).

## `data/raw/structures_2026/`

Deposited coordinates, unchanged: `6N4O.pdb` (human Argonaute2 with miR-122 and target, X-ray 2.9 Å), `4D8C.cif` (BACE1 with a cyclic sulfone inhibitor, X-ray 2.07 Å), `6CU7.cif` (full-length α-synuclein fibril, rod polymorph, cryo-EM), `5OQV.cif` (Aβ(1-42) fibril, cryo-EM 4.0 Å).

## `results/tables/ode_calibrated_results.json`

Output of `scripts/12`: the free parameters, their ranges and the central value of each (measured where a comparable measurement exists); the illustrative aggregation constants and why no source gives them; the comparison between the required mimic dose and the measured BACE1 knockdown; the AD clearance-versus-production experiment; time for a miRNA mimic to wash out at each measured half-life; the α-synuclein pH-gate experiment; human Aβ42 aggregate loads expressed as multiples of M\*; and a summary of the free-parameter scan.

## `results/tables/ode_free_parameter_sensitivity.csv`

One row per point of the free-parameter scan: `free_parameter`, `value`, `abeta_AD_over_control`, `verdict` (`AD_above_control`, `AD_at_or_below_control`, `not_evaluable`). A run that fails numerically is reported as `not_evaluable`, never counted as a reversal.

## `results/tables/structure_figure_provenance.json`

One entry per structure, read from the coordinate file by `scripts/13`: deposited title, method, resolution and resolution criterion, primary-citation DOI and PMID, the figure's role, and checks computed from the coordinates: for 4D8C the catalytic aspartates found both by sequence motif (DTGS, DSGT) and by distance to the inhibitor; for the fibrils, the chains in each protofilament, the layer spacing and the distance between protofilaments. Residue numbers are those of the deposition.

## `data/extracted/quadas2_study_level.csv`

The evidence behind the two QUADAS-2 domains that the accuracy extraction cannot answer. One row per pooled study, read from the PubMed Central full text by hand.

| Column | Meaning |
|---|---|
| `study_id` | PubMed ID, or DOI for studies outside MEDLINE; the same key `scripts/05` uses |
| `first_author`, `year`, `disease` | study identity, for reading the table without a lookup |
| `fulltext_availability` | `yes`, `no_fulltext_in_pmc`, `no_pmc_record` — which of the three reasons applies |
| `reference_standard_named` | `yes` / `no`; empty when the full text could not be read |
| `reference_standard_quote` | the sentence naming the diagnostic criteria, verbatim |
| `autopsy_confirmed` | `yes` / `no`; `yes` requires the quote to mention neuropathological confirmation |
| `blinding_stated` | `yes` / `not_stated` |
| `blinding_quote` | the sentence stating blinding to the index test, verbatim |
| `source` | where the full text was read from |

A flag and its quote must agree: `scripts/08` fails if a `yes` carries no quote, or a quote is recorded for a study whose full text was not retrievable.

## `results/tables/quadas2_assessment.csv`

One row per assessed study, seven domains, each as a verdict plus the reason that produced it (`..._reason`). Verdicts are `low`, `high`, `unclear` or `unrated`. `unclear` means the question was asked and the source does not answer it; `unrated` means it was not asked. No domain is currently `unrated`, and `scripts/08` fails if one becomes so again. Also carries `n_estimates` and `n_estimates_eligible` per study, plus two finer, rule-derived classifications that do not change any of the seven verdicts: `reference_standard_type` (`neuropathological`, `biomarker_confirmed`, `clinical_criteria_named`, `unclear_not_named` or `unclear_fulltext_unavailable`, read from the same `reference_standard_quote` field `rob_reference_standard` uses) and `threshold_source` (`derived_and_evaluated_same_sample`, `cross_validated_within_sample`, `evaluated_in_separate_sample` or `not_determinable`, the same `cohort_stage` set `rob_index_test` uses, relabelled; `evaluated_in_separate_sample` means the estimate comes from participants other than the derivation sample, not that a threshold was pre-specified or externally validated). `rob_index_test` is also set to `high` when `study_design_preanalytics.csv` records that the markers were chosen using the evaluation participants (`candidate_selection = same_sample_data_driven`); the reason text then names that file.

## `results/tables/quadas2_summary.json`

Domain counts, the studies assessed, and two narrative fields computed from the record rather than typed: `full_text_pass_*` (how many full texts were retrievable, how many name criteria, how many confirm by autopsy, how many state blinding) and `eligibility_circularity_*` (how much of the uniform patient-selection verdict follows from this review's own eligibility rule, with the excluded contrasts counted). `scripts/08` checks the numbers in the prose against the record, so the text cannot outlive the data.

## `results/tables/bivariate_input_estimates.csv`

The 2×2 tables entering the bivariate model, reconstructed from published proportions: `sensitivity`, `specificity`, `n_cases`, `n_controls`, `continuity_corrected` (whether the 0.5 correction was applied to an empty cell) and `in_primary_analysis` (whether this estimate is the one kept for its study).

## `results/tables/bivariate_summary.csv`

One row per analysis (primary, one estimate per study; secondary, every eligible estimate): summary sensitivity and specificity with 95% intervals, the between-study standard deviations `tau_*` and their correlation `rho_between`, the diagnostic odds ratio, the two likelihood ratios, and `converged`.

## `results/tables/bivariate_model.json`

The fitted parameters, the estimator's self-test on 400 simulated studies (true value, fitted value, absolute error, tolerance, pass flag for each of the five parameters), and the reconstruction caveat in both languages. `scripts/08` fails if any self-test component reports a failure.

## `results/tables/grade_certainty.json`

The GRADE assessment: the declared thresholds that decide each downgrade, one entry per domain with its steps, judgement and stated reason, the total steps, the resulting certainty, and the summary of findings. Changing a threshold and rerunning changes the verdict — that is the point of storing them.

## `results/tables/grade_summary_of_findings.csv`

One row per pre-test probability: expected true and false positives and negatives per 1000 people tested, plus the resulting predictive values. Counts are not rounded to integers, because rounding three probabilities to whole people hides that they are expectations.

## `results/tables/mimic_dosing_feasibility.csv`

One row per species and dosing interval: `species`, `param_id` (the kinetic-table row the decay constant came from), `half_life_hours`, `dosing_interval_hours`, `peak_over_average` and `fraction_of_interval_above_half_peak`. No free parameter and no assumed dose enter: the dose cancels out of the peak-to-average ratio.

## `results/tables/mimic_dosing_feasibility.json`

The same calculation with the comparisons that use it: each species' decay constant and its `param_id`, the daily-dosing comparison against the median-stability reference (penalty, equivalent interval, fold stabilisation required), and the stated assumption that the delivered mimic is cleared at the endogenous rate — which is why the output is a required fold stabilisation rather than a verdict on feasibility.

## `results/tables/graphical_abstract_values.json`

Every number drawn on `results/figures/graphical_abstract.*.png`, loaded from `ode_calibrated_results.json`, `mimic_dosing_feasibility.json` and `kinetic_parameters.csv` at draw time rather than typed as a separate string, plus the `param_id`s each figure grounds a claim in. Nothing here is a new computation; it is a record of which already-verified number went where.

## `results/tables/mechanism_animations.json`

The numbers each animation in `results/figures/anim_*.gif` draws: the final AD/control Aβ42 ratio, the two species' washout times, and the two species' peak-to-average ratios and the penalty between them. Every field is recomputed by `scripts/08` from `ode_calibrated_results.json` and `mimic_dosing_feasibility.json` and required to match, so the manifest cannot drift from the tables its own numbers came from.

## `results/figures/anim_*.gif`

Three animated GIFs, each in both languages: `anim_ad_monomer` (Aβ42 accumulating to steady state, no free parameter), `anim_mimic_washout` (a single mimic bolus decaying at its measured half-life), `anim_dosing_sawtooth` (the repeated-dosing peak-to-average penalty as a moving cycle). Each is produced by `scripts/19_mechanism_animations.py`, which imports its equations from `scripts/12` and `scripts/17` rather than re-deriving them. The α-synuclein pH-gate trajectory is not among them, because its acidic-pH rate constant is illustrative rather than measured (K042).

## `results/figures/`

Every figure exists twice, `<name>.en.png` and `<name>.pt-BR.png`. Both are drawn by the same code from the same arrays in the same run; only the label text differs.

## `results/figures/structure_story_panel.*.png`

The four `scripts/13` renders composited into one figure, with the accompanying facts (PDB id, method, resolution, catalytic dyad residues, protofilament count and spacing) pulled from `structure_figure_provenance.json` rather than retyped. No new render, no new claim - only the layout and the grouping are new.

## `results/figures/prisma_flow_diagram.*.png`

The PRISMA 2020 flow diagram, drawn by `scripts/21_prisma_flow_diagram.py` from `data/processed/prisma_flow.json` and, for the one count not stored there (studies contributing an eligible estimate), recomputed directly from `diagnostic_accuracy_extraction.csv` at draw time.

## `results/figures/key_equations.*.png`

A six-panel figure typesetting the equations `scripts/05_meta_analysis.py` and `scripts/15_bivariate_srocc.py` actually evaluate (logit transform, Hanley-McNeil standard error, DerSimonian-Laird pooling, Egger's regression, the bivariate model, and the CI-to-SE conversion), each captioned with the function and citation it comes from. Produced by `scripts/22_key_equations_figure.py`.

## `results/figures/subgroup_summary_forest.*.png`

A point-range ("summary forest") chart of the core pooled-AUC subgroups reported in Table 1 (AD primary, PD primary, AD+PD combined secondary, single microRNA, multi-microRNA panel), each point and its 95% modified Hartung-Knapp (mHK) CI read live from `results/tables/meta_analysis_pooled_auc_primary.csv`. Produced by `scripts/23_subgroup_summary_forest.py`; not a substitute for the individual-study forest plot (`forest_plot_auc.*.png`, Supplementary Figure S1), which plots every individual circulating estimate rather than five subgroup summaries.

## `results/figures/study_characteristics.*.png`

Two donuts (by disease, by marker type) and one ranked bar (by biofluid) summarising the composition of the 58 estimates eligible for the primary pool, aggregated at draw time from `data/extracted/diagnostic_accuracy_extraction.csv` filtered to `eligible_primary_pool == "yes"`. Produced by `scripts/24_study_characteristics.py`; the same 58-estimate counts are tabulated in full, with two further breakdowns (quantification method, cohort stage), in Supplementary Table S1.

## Conventions

- Proportions are stored as proportions (0.82), not percentages (82%).
- Empty cells mean **not stated in the source**, never zero and never imputed.
- Every enum value that appears in the data is listed above; unlisted values indicate a data error.
