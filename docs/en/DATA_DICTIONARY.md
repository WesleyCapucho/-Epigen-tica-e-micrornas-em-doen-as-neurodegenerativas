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

## Conventions

- Proportions are stored as proportions (0.82), not percentages (82%).
- Empty cells mean **not stated in the source**, never zero and never imputed.
- Every enum value that appears in the data is listed above; unlisted values indicate a data error.
