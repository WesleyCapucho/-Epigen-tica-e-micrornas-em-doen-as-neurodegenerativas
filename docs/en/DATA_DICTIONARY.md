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

## `results/tables/meta_analysis_pooled_auc.csv`

| Column | Description |
|---|---|
| `subgroup` | Which subset was pooled |
| `k_estimates` | Number of estimates pooled |
| `n_studies` | Number of independent studies contributing them |
| `pooled_auc`, `ci_low`, `ci_high` | Random-effects pooled AUC, back-transformed from logit |
| `tau2_logit` | Between-study variance on the logit scale |
| `I2_percent`, `Q`, `df`, `p_heterogeneity` | Heterogeneity statistics |
| `egger_intercept`, `egger_p` | Egger test for small-study effects |

## `results/tables/meta_analysis_input_estimates.csv`

The 24 poolable estimates with the standard error used for each and, critically, `se_source` — `reported_95CI` when derived from a published interval, `Hanley-McNeil` when computed from group sizes.

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

One row per assessed study, seven domains, each as a verdict plus the reason that produced it (`..._reason`). Verdicts are `low`, `high`, `unclear` or `unrated`. `unclear` means the question was asked and the source does not answer it; `unrated` means it was not asked. No domain is currently `unrated`, and `scripts/08` fails if one becomes so again. Also carries `n_estimates` and `n_estimates_eligible` per study.

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

## `results/figures/`

Every figure exists twice, `<name>.en.png` and `<name>.pt-BR.png`. Both are drawn by the same code from the same arrays in the same run; only the label text differs.

## Conventions

- Proportions are stored as proportions (0.82), not percentages (82%).
- Empty cells mean **not stated in the source**, never zero and never imputed.
- Every enum value that appears in the data is listed above; unlisted values indicate a data error.
