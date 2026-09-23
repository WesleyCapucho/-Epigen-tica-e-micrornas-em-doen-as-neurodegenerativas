# PRISMA-DTA checklist

🇧🇷 Versão em português: [../pt-BR/CHECKLIST_PRISMA_DTA.md](../pt-BR/CHECKLIST_PRISMA_DTA.md)

---

Reporting checklist for systematic reviews of diagnostic test accuracy (McInnes MDF, Moher D, Thombs BD, et al. Preferred Reporting Items for a Systematic Review and Meta-analysis of Diagnostic Test Accuracy Studies: the PRISMA-DTA statement. *JAMA.* 2018;319(4):388-396).

Each item says where it is met in this repository, or says plainly that it is not. Three items are not met, and they are listed first so they are not buried: the review was **not registered and has no prospective protocol** (item 5), **certainty of evidence was not graded** (item 15), and two QUADAS-2 domains are **unrated** rather than judged (items 11 and 18). A fourth is partial: screening had **no independent second reviewer** (item 9).

| # | Section | Item | Status | Where |
|---|---|---|---|---|
| 1 | Title | Identify the report as a systematic review of diagnostic test accuracy. | In the manuscript | In the manuscript, which is kept outside this repository. |
| 2 | Abstract | Structured abstract following PRISMA-DTA for Abstracts. | In the manuscript | In the manuscript. |
| 3 | Introduction | Describe the rationale in the context of what is already known. | In the manuscript | In the manuscript; the quantitative background is in docs/en/METHODS.md. |
| 4 | Introduction | State the question with reference to participants, index test and target condition. | Met | docs/en/METHODS.md section 1; the PICO is frozen in data/raw/systematic_review_2026/search_strategy.json. |
| 5 | Methods | Indicate whether a protocol exists, and give the registration number. | **Not met** | No prospective protocol was written and the review was NOT registered in PROSPERO or elsewhere. The search strategy, eligibility rules and screening decisions were frozen in the repository as they were applied, which makes the process auditable but not pre-specified. Any reader should treat the eligibility rules as capable of having been shaped by the data. This is disclosed rather than repaired: registering now would be retrospective and presenting it as a protocol would be false. |
| 6 | Methods | Specify the eligibility criteria and how studies were grouped. | Met | docs/en/METHODS.md section 3; every decision is in data/raw/systematic_review_2026/screening_decisions.csv, and every excluded estimate carries an exclusion_reason in the extraction table. |
| 7 | Methods | Specify all information sources and the date last searched. | Partly met | PubMed/MEDLINE and Scopus, both arms, last searched 10 September 2026 (docs/en/METHODS.md section 2). Web of Science was NOT searched; this is a coverage limitation, not an omission from the report. |
| 8 | Methods | Present the full search strategy for at least one database. | Met | data/raw/systematic_review_2026/search_strategy.json holds the executed queries and the counts they returned; docs/en/HOW_TO_EXPORT_SCOPUS_WOS.md holds the Scopus queries verbatim. |
| 9 | Methods | State the selection process, including how many reviewers screened. | Partly met | Screening was rule-based and is fully reproducible (scripts/04), then checked against full texts by one person. There was NO independent second screener and no inter-rater agreement statistic. Single-reviewer screening is a recognised source of error and is disclosed here. |
| 10 | Methods | State the data collection process and the data items sought. | Met | docs/en/DATA_DICTIONARY.md documents every column; each numeric cell carries the verbatim sentence it was read from. |
| 11 | Methods | Describe the methods for assessing risk of bias and applicability. | Partly met | QUADAS-2 (scripts/14), with every judgement derived by a stated rule from a recorded field. Two of the four risk of bias domains - reference standard, and flow and timing - are reported as UNRATED because the extraction did not capture the diagnostic criteria, blinding or patient flow. Rating them needs a second pass over the full texts. |
| 12 | Methods | State the measures of test accuracy used. | Met | AUC as the primary measure, because it is what most source studies report; sensitivity and specificity in the bivariate model where a complete 2x2 could be reconstructed. |
| 13 | Methods | Describe the synthesis methods and how heterogeneity was handled. | Met | DerSimonian-Laird random effects on logit AUC (scripts/05) and the Reitsma bivariate model on logit sensitivity and specificity (scripts/15). Heterogeneity is reported as tau squared, Q and I squared, and is high. |
| 14 | Methods | Describe methods for assessing reporting bias. | Met | Egger regression on each subgroup, reported with the pooled estimate; funnel plot in results/figures/funnel_plot_auc.png. |
| 15 | Methods | Describe methods for assessing certainty of evidence. | **Not met** | GRADE for diagnostic test accuracy was not applied. The elements that would feed it are present - risk of bias, inconsistency, indirectness through the case-control designs, imprecision, and publication bias - but they were not combined into a GRADE rating. |
| 16 | Results | Give the numbers of studies screened, assessed and included, with a flow diagram. | Met | data/processed/prisma_flow.json, recomputed and cross-checked by scripts/08. |
| 17 | Results | Cite each included study and present its characteristics. | Met | data/extracted/diagnostic_accuracy_extraction.csv, one row per estimate with cohort, biofluid, platform and group sizes. |
| 18 | Results | Present the risk of bias assessment for each study. | Partly met | results/tables/quadas2_assessment.csv, one row per study with the reason for every judgement; summary figure in results/figures/quadas2_summary.png. Two domains unrated, as in item 11. |
| 19 | Results | Report accuracy results for each study, ideally as 2x2 tables. | Partly met | results/tables/bivariate_input_estimates.csv gives the reconstructed 2x2 for every estimate that supports one. The source articles report proportions rather than counts, so the tables are reconstructed by multiplying and rounding, and the file says so. |
| 20 | Results | Present the syntheses, with confidence intervals and heterogeneity. | Met | results/tables/meta_analysis_pooled_auc.csv and results/tables/bivariate_summary.csv; forest plot and summary ROC in results/figures/. |
| 21 | Results | Present the results of any reporting bias assessment. | Met | Egger intercept and p value per subgroup in the pooled table; both are significant in the overall and Parkinson analyses. |
| 22 | Results | Present the results of any sensitivity analyses. | Met | results/tables/sensitivity_single_mirna.csv: one estimate per study and leave-one-study-out; results/tables/attention_correlation_audit.csv decomposes a corrected defect. |
| 23 | Discussion | Summarise the main findings and their certainty. | In the manuscript | In the manuscript. The repository supplies the numbers and the caveats attached to each. |
| 24 | Discussion | Discuss limitations of the evidence and of the review process. | Met | README 'Known limitations' and README 'Corrections', which records three defects found after results had been produced and what each changed. |
| 25 | Discussion | Discuss implications for practice and research. | In the manuscript | In the manuscript. |
| 26 | Other | Declare sources of funding and the role of funders. | In the manuscript | In the manuscript. |
| 27 | Other | Declare competing interests and state data availability. | Met | This repository is the data availability statement: raw data, scripts, tables and figures, with every extracted value traceable to a verbatim source sentence. |
