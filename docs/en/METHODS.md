# Methods

*Systematic review and meta-analysis of the diagnostic accuracy of circulating microRNAs in Alzheimer's and Parkinson's disease.*

🇧🇷 Versão em português: [../pt-BR/METODOS.md](../pt-BR/METODOS.md)

---

## 1. Review question

Two questions are addressed, one confirmatory and one that the source monograph raised about its own method:

1. **How well do circulating microRNAs actually discriminate patients with Alzheimer's disease (AD) or Parkinson's disease (PD) from controls**, when the published estimates are pooled rather than listed?
2. **Is the frequency with which a miRNA is discussed in the literature related to how well it performs?** The monograph on which this repository is based acknowledged that bibliometric frequency and catalogued experimental validation share a common cause — prior research attention — and are therefore not independent evidence. Pooled diagnostic accuracy is an external criterion that breaks that dependency.

PICO framing: **P** adults with clinically diagnosed AD or PD; **I** measurement of one or more microRNAs in an accessible biofluid; **C** healthy or cognitively normal controls; **O** diagnostic discrimination (AUC, sensitivity, specificity).

## 2. Information sources and search

PubMed/MEDLINE was searched through the NCBI E-utilities API on **10 September 2026**, with no language restriction and a publication-date filter of 1 January 2015 onwards.

Two search arms were run, differing only in the disease term. Each combines a microRNA block, a biofluid block and a diagnostic-accuracy block, all restricted to Title/Abstract:

```
(microRNA OR miRNA OR microRNAs OR miRNAs)
AND (Alzheimer | Parkinson)
AND (plasma OR serum OR "cerebrospinal fluid" OR CSF OR blood
     OR exosome OR exosomal OR "extracellular vesicle")
AND (ROC OR "area under the curve" OR AUC OR sensitivity
     OR specificity OR "diagnostic accuracy" OR "diagnostic value")
```

Returns: the initial query reported 168 matching records for the AD arm, but only **167** could actually be fetched and archived (one PMID was lost to a transient E-utilities fetch gap and is excluded from every downstream count); **97 records** (PD arm); **234 unique records** after deduplication, of which **30** were retrieved by both arms. The exact submitted strings, the PubMed query translations and the retrieved PMIDs are stored in `data/raw/systematic_review_2026/search_strategy.json`; `scripts/03_systematic_search.py` re-runs the searches.

Because PubMed grows daily, a later re-run will return more records than the frozen counts above. That is expected behaviour, not an inconsistency: the archived strategy file is what the reported numbers refer to.

**Scopus.** Scopus was searched with the same two-arm strategy on 10 September 2026 and the result sets exported under institutional authentication, because Scopus cannot be queried by API from this environment. The exports are archived in `data/raw/systematic_review_2026/exports/` and ingested by `scripts/09_ingest_scopus_wos.py`, which normalises them and deduplicates against the PubMed corpus and against every previously ingested arm, by DOI, PubMed ID and normalised title.

Returns: **408 records** (AD arm), of which 248 were new to the review, and **255 records** (PD arm), of which 98 were already in the PubMed corpus and 79 had already arrived with the Scopus AD arm — a paper naming both diseases is returned by both searches and must be counted once. The PD arm therefore contributed **78** new records, and the corpus totals **560 unique records**.

That cross-arm step is not incidental. Without it the PD arm appeared to add 157 records rather than 78, because the same paper was being counted in two arms.

**Web of Science.** Web of Science Core Collection was searched on 23 September 2026 with the same two-arm topic (`TS=`) strategy, timespan 2015–2026, and exported in full-record tab-delimited form under institutional authentication, because it cannot be queried by API from this project. The AD arm returned 187 records and the PD arm 108; after deduplication against PubMed, Scopus and each other, **27 were new**. The search date is thirteen days later than the other two databases and is reported as its own date rather than folded into theirs. The exports are archived in `data/raw/systematic_review_2026/exports/`.

**What the third database changed, which was nothing in the synthesis.** Of the 27 new records, 15 are primary studies and 3 report an accuracy measure in the abstract. All three were adjudicated against the PICO and none entered the primary pool: one measures the long non-coding RNA BACE1-AS rather than a microRNA, one measures post-mortem prefrontal cortex rather than a circulating biofluid (and its own authors conclude that testing in peripheral biofluids is still warranted), and the third — the only record matching the PICO on population, biofluid and index test — reports its AUC only as the inequality "AUC>0.90", carries no DOI and no PubMed ID, and its journal stopped depositing in PubMed Central in 2015, so no full text could be reached to confirm a value. A number that cannot be checked against a source sentence is not extracted. All three are recorded in the extraction table as rows E077–E079 with their exclusion reasons, so the arm can be audited rather than taken on trust. The pooled estimates, the bivariate operating point, the QUADAS-2 table and the GRADE rating are byte-identical before and after the Web of Science arm.

**Databases not searched.** All three databases planned for this review have been searched, symmetrically across the two diseases. Embase, which many diagnostic-accuracy reviews add, was not searched, and no citation chasing, forward citation search, grey literature or preprint server supplemented the three databases. These are reported as limitations in the manuscript.

**Reproducibility of the corpus.** Titles and abstracts for all 560 records are archived in `data/raw/systematic_review_2026/screening_corpus.json` and rebuilt by `scripts/10_build_screening_corpus.py`. They were not committed in earlier versions, which meant the mention counts in Section 6 could not be regenerated from the repository alone. They can now.

## 3. Screening

Screening is rule-based and reproducible (`scripts/04_screening.py`). Each record was classified on two axes:

- **Secondary literature**, if the PubMed publication type was Review, Systematic Review, Meta-Analysis, Editorial, Comment, Letter, Erratum or Retraction, or if the title/abstract announced a review.
- **Carries quantitative accuracy data**, if the abstract stated an AUC, or stated both a sensitivity and a specificity.

Results, by source:

| Source | Screened | Secondary | Primary | Reporting accuracy |
|---|---|---|---|---|
| PubMed | 234 | 46 | 188 | 95 |
| Scopus AD (new) | 248 | 147 | 101 | 20 |
| Scopus PD (new) | 78 | 30 | 48 | 12 |

Fifty-five of the PubMed primary studies had an open-access full text in PubMed Central. Per-record decisions are in `data/raw/systematic_review_2026/screening_decisions.csv`; the counts are recomputed into `data/processed/prisma_flow.json` rather than transcribed.

**A defect worth declaring.** An earlier version of the secondary-literature rule closed its alternation with a word boundary after `meta-analys`. Because "meta-analysis" continues with "is", there is no boundary at that point and the alternative never fired, so self-declared meta-analyses passed screening as primary studies. It reclassified one PubMed record and affected no extracted estimate, but it is why the prior meta-analyses that this work must be positioned against went unnoticed until the Scopus records were screened.

## 4. Full-text data extraction

Full texts were retrieved from PubMed Central for **47 studies**. Extraction followed three rules, and was then checked by a second full-text pass (below):

**Automated mining locates candidates; a human records values.** Regular expressions surfaced every sentence containing an accuracy metric together with its surrounding context. Those sentences were then read, and the values transcribed by hand. This division of labour is not ceremonial: the patterns demonstrably mis-assign sensitivity to specificity when a sentence reverses their order, capture p-values in a specificity slot, and treat a *decrease* in AUC during permutation testing as an AUC. None of those errors survives reading the sentence, and all of them would survive automated capture.

**Every value stores the sentence that supports it.** Each row of `data/extracted/diagnostic_accuracy_extraction.csv` carries a `verbatim_quote` column with the exact wording from the source, plus PMID and DOI.

**Values attributed to other studies are not extracted.** Discussion sections routinely quote AUCs from other papers ("Han et al. found…", "Wen et al. reported…"). Such sentences were identified and excluded; only each study's own results were recorded.

For every estimate the following were captured where stated: miRNA (or panel composition), disease, comparison and comparison class, biofluid, cohort stage (discovery / training / validation / single), number of cases and controls, AUC with its confidence interval, sensitivity, specificity, and measurement method.

### Second full-text pass (28 September 2026)

The first extraction pass read the sentence that carried each accuracy value. That was not enough. A second pass read each of the 22 PubMed Central full texts from beginning to end and checked every extracted number against the paper as a whole: which cohort the AUC came from, how large that cohort was, what was measured in which fluid, and how the markers were chosen. It found errors that no sentence-level reading could have caught:

- **A missed validation cohort.** Li Y et al. 2024 report their classifier in a training set and in a held-out validation set; the first pass stopped reading the sentence before the validation values.
- **AUCs attributed to the wrong cohort.** Hara et al. 2017 discovered their marker in an autopsy-confirmed set but report the AUC for a separate, clinically diagnosed set (36 AD / 22 controls). The first pass recorded the autopsy set's group sizes and credited the estimate with neuropathological confirmation.
- **Wrong biofluid.** Sandau et al. 2020 measured cerebrospinal fluid, not plasma. Jain et al. 2019 measured cerebrospinal-fluid exosomes, not blood, with a signature of three miRNAs and three piRNAs tested against controls that included psychiatric and neurological patients; it is now ineligible under the rules that already excluded mixed small-RNA panels. Hojati et al. 2020 measured serum by RT-qPCR, not whole blood by microarray. Grossi et al. 2020 report their AUC for purified plasma small extracellular vesicles, not whole plasma.
- **Test-split AUCs paired with whole-cohort group sizes.** Aguilar et al. 2023 and Dos Santos et al. 2018 report AUCs on a random test split whose per-group size is not given. Under the no-imputation rule these estimates are not SE-estimable and leave the pool.
- **Group sizes that were in the paper but not in the table.** Zhang M et al. 2021 (miR-128, 106 controls), Rai et al. 2023 (16/16), Omura et al. 2025 (8/6), Grossi et al. 2020 (15/14) and Marques et al. 2016 (28/28).
- **Ten estimates not extracted at all** (E080 to E089), including the only differential-diagnosis AUCs the eligible studies report (AD against vascular cognitive impairment and against dementia with Lewy bodies in Qin et al. 2026; PD against multiple system atrophy in cerebrospinal fluid in Marques et al. 2016).

Every change, with the old value, the new value and the sentence that justifies it, is in `data/extracted/extraction_audit_log.csv`, and `scripts/08` replays that log against the extraction table so the two cannot drift apart. The same pass recorded, for each of the 27 eligible studies, the reference standard, disease stage, medication status, haemolysis handling, normalisation strategy, how candidate markers were selected and how the model was validated, each with a quoted source, in `data/extracted/study_design_preanalytics.csv`. Six studies have no retrievable full text, and those fields are marked not assessable rather than guessed.

This pass was performed by the same single reviewer (with LLM assistance under the author's supervision; see the manuscript's declaration), not by an independent second reviewer. It reduces transcription and attribution error; it does not replace dual independent extraction.

### Eligibility for the primary pool

An estimate enters the primary pool only if it is a **case-versus-healthy-control contrast in a defined AD or PD population**, measuring **one or more miRNAs and nothing else** in the stated biofluid. Of 89 extracted estimates, **58** qualified, from **27 independent studies** (13 AD, 14 PD). The 31 that did not are retained in the table with an explicit `exclusion_reason`:

| Reason | Example |
|---|---|
| Composite or differential comparator | AD against FTD *and* controls; AD against vascular cognitive impairment; PD against MSA |
| Within-disease contrast | PD with vs without cognitive impairment |
| Prodromal population | isolated REM sleep behaviour disorder rather than established PD |
| Genotype stratification | LRRK2 carriers rather than sporadic PD |
| Mixed population | "neurodegenerative pathology" without disease-specific breakdown |
| Unstable estimate | AUC = 1.000 by perfect separation in a 6-patient subgroup |
| Composite model | miRNA combined with non-miRNA clinical variables, with MRI parameters, or with a lncRNA, circRNA or protein |
| Mixed RNA panel | panel containing piRNAs or rRNA pseudogenes alongside miRNAs |
| Index test not a miRNA | a lncRNA, a circRNA, a brain-tissue gene signature or a faecal microbiome genus |

**Duplicate publication.** PMIDs 40661348 and 41836608 report the same cohort, the same markers and the same AUCs (preprint and journal version of one study). The pair was detected by identical verbatim result sentences and counted once. The second pass also found likely participant overlap that is not duplicate publication: Karaglani et al. 2020 re-analyse a public whole-blood dataset from the same group whose earlier cohorts contribute to Ludwig et al. 2019. Ludwig et al. has no SE-estimable estimate, so the overlap does not reach any pooled number, but it is recorded.

## 5. Statistical synthesis

Implemented in `scripts/05_meta_analysis.py` (the pooling itself), `scripts/_study_selection.py` (the one-estimate-per-study selection rule, shared with the bivariate synthesis in Section 7) and `scripts/26_robustness_analyses.py` (Section 5b), using NumPy and SciPy only, so that every step is inspectable rather than delegated to a black-box package.

**Standard errors.** When the source reported a 95% CI, SE = (upper − lower) / (2 × 1.96). Otherwise SE was computed from Hanley & McNeil (1982) using the case and control group sizes. Estimates with neither a CI nor group sizes cannot be weighted and are excluded from pooling. **42 of the 58** eligible estimates, from **21 independent studies**, were poolable.

**Plausibility of a reported interval.** A reported interval is preferred to a reconstructed one only if it can describe sampling uncertainty at the stated group sizes. When the SE implied by a reported CI is less than half the Hanley-McNeil SE for the same AUC and group sizes, the interval is treated as describing something else (for example, the spread of a cross-validation estimate) and the Hanley-McNeil SE is used instead. This rule was added after the second full-text pass, not pre-specified. It changes one study: Li Y et al. 2024 report 0.916 (95% CI 0.911 to 0.921) for 21 cases and 25 controls, an interval about 18 times narrower than sampling at that size allows (ratio of SEs 0.056; the training-set interval gives 0.049). Every other row with both a CI and group sizes has a ratio between 0.80 and 1.38 (`results/tables/ci_plausibility_check.csv`), so any cut-off between about 0.06 and 0.79 gives the same classification. Section 5b reports every analysis with the intervals as published.

**Scope: circulating versus cerebrospinal fluid.** Four eligible studies measured cerebrospinal fluid (Lusardi et al. 2017 and Sandau et al. 2020 in AD; Marques et al. 2016 and Dos Santos et al. 2018 in PD), three of them with an SE-estimable estimate. CSF is screened, extracted and QUADAS-2-rated with the rest of the corpus (Section 6), because the same search captured it, but it is never pooled with blood-derived estimates: the eligibility criteria, the manuscript's title and its research question all concern *circulating* microRNAs. The CSF estimates are reported narratively in `results/tables/csf_secondary_estimates.csv`. This leaves **39 estimates from 18 independent circulating studies** (9 AD, 9 PD) as the primary meta-analysis.

**Study identity.** A study is keyed on its PubMed ID when it has one and on its DOI otherwise. Keying on PMID alone collapsed the studies published outside MEDLINE into a single blank-PMID group, so two independent cohorts that both report miR-124 in PD serum were being counted as one. The SE source is recorded per estimate in `results/tables/meta_analysis_input_estimates.csv`.

*Validation of this step:* for PMID 33129241 (AUC 0.75, 18 cases vs 18 controls) the Hanley–McNeil formula returns SE = 0.0822, against SE = 0.08 reported independently by the article itself.

**Unit of analysis: one pre-specified, AUC-blind estimate per study.** Nine of the 18 circulating studies supply more than one qualifying estimate (one supplies eight), and those estimates typically come from the same participants (a single microRNA and a panel that contains it, measured in one cohort), so they are correlated. An earlier version of this pipeline collapsed such rows with a within-study fixed-effect combination; that still assumes the correlated rows are independent when it computes their combined variance. The current pipeline instead selects exactly **one** estimate per study by a rule fixed in advance and blind to the estimate's own AUC, implemented once in `scripts/_study_selection.py` and shared by the AUC pool and the bivariate synthesis:

1. Prefer a row evaluated in a separate validation sample (`cohort_stage == "validation"`: a held-out split or a second cohort) over one derived and evaluated in the same sample.
2. Within the surviving tier, prefer the study's own multi-microRNA panel over its component single markers.
3. If still tied, prefer the row with the larger combined case-plus-control sample size.
4. If still tied, take the alphabetically first marker name, a purely nominal tiebreak.

Step 2 favours panels by construction whenever panels and single markers are compared, so Section 5b re-runs everything without it. Every selection and the reason it won are written to `results/tables/one_estimate_per_study_selection_audit.csv`. Pooling every row as if independent is retained only as a labelled sensitivity check (`results/tables/meta_analysis_pooled_auc_sensitivity_every_estimate.csv`).

**Pooling.** AUCs were transformed to the logit scale, with the SE propagated by the delta method (SE_logit = SE_AUC / [AUC(1 − AUC)]). The one-estimate-per-study rows were combined with the Paule & Mandel (1982) τ² estimator, which avoids the downward bias DerSimonian & Laird (1986) carries at the small *k* seen here, and back-transformed for reporting. Confidence intervals use the Hartung & Knapp (2001) *t*-based adjustment with the modification of IntHout et al. (2014): the Hartung-Knapp standard error is floored at the Wald one, because the unfloored interval can come out narrower than the standard random-effects interval when heterogeneity is small. This modified Hartung-Knapp (mHK) interval is reported throughout. It is not called "Hartung-Knapp-Sidik-Jonkman": Sidik & Jonkman (2002) is a distinct τ² estimator this review does not use. A 95% prediction interval is reported for every pooled estimate with *k* ≥ 3. Random effects were chosen a priori: the studies differ in biofluid, platform, population and cut-off derivation.

**Alzheimer's and Parkinson's disease are separate primary outcomes**, pooled and GRADE-rated on their own; the combined AD+PD estimate (18 studies) is a secondary, exploratory summary.

**Heterogeneity** is reported as Cochran's Q with its p-value, τ² on the logit scale, and I² from the DerSimonian-Laird calculation, so heterogeneity statistics stay comparable across the primary and sensitivity analyses.

**Small-study effects** were assessed with Egger's regression on both the one-estimate-per-study pool and the every-row pool. With fewer than ten independent studies per disease the test is underpowered and unstable, and it is read as exploratory evidence of funnel-plot asymmetry, not as a test for publication bias (Section 8).

**Subgroups**, pre-specified: by disease, by marker type (single miRNA vs multi-miRNA panel), and by biofluid where at least three independent studies were available. Marker-type and biofluid subgroups are built by filtering the single one-estimate-per-study selection, never by re-selecting within a pre-filtered set of raw rows, so the single-miRNA and panel groups are disjoint by construction. That matters for the formal panel-versus-single test (Borenstein et al. 2009, ch. 19: Q_between = Q_all − Q_single − Q_panel on 1 df), which presupposes independent subgroups; an earlier version of this pipeline let one study contribute to both groups and overstated the AD difference (p = 0.005 then, against p = 0.067 once the groups were disjoint, on the corpus as extracted at that time).

### 5b. Robustness analyses

`scripts/26_robustness_analyses.py`, added after the second full-text pass. None replaces the primary analysis; each asks how much one analytic choice moves it.

- **Marker-type-neutral selection rule** (drops step 2 above): `results/tables/robustness_alternative_analyses.csv`.
- **2,000 random AUC-blind selections**, one qualifying estimate per study drawn uniformly at random, seed fixed: the spread of the pooled AUC and of the panel-versus-single p-value across selections that ignore the AUC (`robustness_random_selection.csv`).
- **Leave-one-study-out per disease** on the primary selection (`robustness_leave_one_out_by_disease.csv`).
- **Reported intervals as published**, without the plausibility rule (in `robustness_alternative_analyses.csv`).
- **Panel-subgroup audit**: every study in each disease's panel subgroup, with AUC, interval, group sizes, SE source, weight and the source the value was read from (`panel_subgroup_audit.csv`).
- **Sensitivity/specificity label check**: whether each published sensitivity is integer-consistent with the case group size and each specificity with the control group size, or only when swapped (`sens_spec_label_check.csv`). Wu L et al. 2022 is consistent only with swapped labels for both markers; values are kept as published and the bivariate model is refitted without that study (`robustness_bivariate_label_check.csv`).
- **Design profile** of the pooled studies from `study_design_preanalytics.csv` (`study_design_profile.csv`), and an exploratory split of the pooled AUC by whether the selected estimate came from participants separate from those the markers were chosen in (`robustness_validation_split_exploratory.csv`). With two to seven studies per cell this split is descriptive only.

## 6. Risk of bias and applicability (QUADAS-2)

`scripts/14_quadas2_risk_of_bias.py`. All 27 eligible studies (Section 4) were assessed with QUADAS-2 (Whiting et al. 2011): four risk-of-bias domains and three applicability domains, including the four cerebrospinal-fluid studies that Section 5 excludes from the pooled AUC. Section 8's GRADE rating, by contrast, draws its risk-of-bias and indirectness domains only from the 17 studies in the circulating primary pool.

**Judgements are derived by rule, not typed in.** Every verdict is produced by a function that reads a recorded field and returns a judgement with its reason, so a reader who disagrees can change one function and rerun the assessment over every study.

**Study-level evidence.** The reference-standard and flow domains need evidence the accuracy extraction does not hold; it is recorded study by study in `data/extracted/quadas2_study_level.csv` with the sentence each answer was read from. 22 of the 27 studies have a retrievable full text; **15** name the diagnostic criteria they applied; **one** (Yang et al. 2026) defines its AD and control groups by neuropathology; **one** (Qin et al. 2026) confirms AD by amyloid PET or a low CSF Aβ42/40 ratio and states that laboratory staff were blind to diagnosis. The second pass corrected this record in three places: Hara et al. 2017 had been credited with neuropathological confirmation that applies only to its discovery set, Yang et al. 2026 had been recorded as naming no criteria, and Zhang M et al. 2021 (miR-128) names NINCDS-ADRDA.

**Why naming accepted criteria is not enough for a low-risk verdict.** In AD and PD the practical reference standard is clinical criteria, which misclassify a known fraction of cases. A study that names accepted criteria is rated *unclear*; only neuropathological confirmation, or named criteria with stated blinding, clears the domain. The result is 2 low, 18 unclear and 7 high.

**Index test.** A study is at high risk when its threshold, markers or model were derived in the same sample where accuracy was then evaluated. From the second pass a further rule applies: a study whose AUC comes from a held-out split is still high risk if its markers were chosen by comparing cases and controls across the whole dataset before the split (`candidate_selection = same_sample_data_driven` in the design table), because the evaluation participants informed the choice of test. This moves Aguilar et al. 2023 and Dos Santos et al. 2018. The result is 25 high and 2 unclear (Hara et al. 2017 and Duan et al. 2024, whose markers were chosen in a separate discovery sample; the cut-off was still derived in the evaluation sample). No included study pre-specified a numeric threshold. The `threshold_source` column records where the reported estimate came from: 23 studies derived and evaluated in one sample, 4 evaluated in a sample separate from the derivation sample. The label was renamed from "externally_validated", which overstated what those four studies did: every such sample came from the same centre or recruitment as its derivation sample.

**Flow and timing is unclear for all 27 studies.** None of the retrievable full texts contains a STARD flow diagram or an equivalent accounting of every enrolled participant.

**The uniform patient-selection verdict is partly circular, and the output says so.** Every study is high risk and high concern for patient selection because every eligible estimate is a case-versus-healthy-control contrast, which the eligibility rule required. 18 estimates from 13 studies using a differential-diagnosis, within-disease or prodromal contrast were excluded for not matching the PICO. `quadas2_summary.json` carries this statement next to the counts.

## 7. Bivariate sensitivity–specificity synthesis

`scripts/15_bivariate_srocc.py`. The studies reporting sensitivity and specificity at a stated threshold were synthesised with the bivariate random-effects model of Reitsma et al. (2005): logit sensitivity and logit specificity as a correlated bivariate normal pair, with the within-study covariance from the reconstructed 2×2 table and the between-study covariance by maximum likelihood. CSF studies are excluded.

**The estimator is tested before it is used.** The script first fits 400 simulated studies drawn from known parameters and requires all five to be recovered within a declared tolerance, or it exits without writing results.

**2×2 tables are reconstructed.** The source articles report proportions rather than counts, so cells are obtained by multiplying published sensitivity and specificity by published group sizes and rounding, with a 0.5 continuity correction where a cell is empty. The primary analysis uses the same one-estimate-per-study selection as Section 5; a secondary analysis uses every eligible estimate.

Primary analysis, 12 circulating studies (12 estimates): summary sensitivity **0.755** (95% CI 0.659–0.831), specificity **0.791** (0.751–0.825), diagnostic odds ratio 11.7, LR+ 3.61, LR− 0.31. The secondary analysis (21 estimates, the same 12 studies) gives sensitivity 0.765 and specificity 0.783. Excluding Wu L et al. 2022, whose labels appear swapped (Section 5b), gives sensitivity 0.773 and specificity 0.797 from 11 studies. With 12 studies and five parameters the between-study terms (τ_sensitivity 0.734, τ_specificity 0.180, ρ 0.589) are weakly identified and not interpreted on their own. The operating point is what this analysis supports, and it reads considerably worse than a pooled AUC near 0.8 suggests.

## 8. Certainty of evidence (GRADE)

`scripts/16_grade_certainty.py`. Certainty was rated with GRADE for diagnostic test accuracy (Schünemann et al. 2020), starting at *high* and downgrading across five domains. Every threshold that decides a downgrade is a named constant at the top of the script and is written into `grade_certainty.json`.

**AD and PD are rated separately**, each on its own primary circulating pool. Risk of bias and indirectness are computed from the QUADAS-2 table restricted to the 18 studies in that pool (9 AD, 9 PD).

| Domain | AD steps | AD basis | PD steps | PD basis |
|---|---|---|---|---|
| Risk of bias | −2 | 9 of 9 studies at high risk in at least one QUADAS-2 domain | −2 | 9 of 9 studies at high risk in at least one QUADAS-2 domain |
| Indirectness | −1 | 9 of 9 raise high applicability concern: case versus healthy control, not the differential diagnosis a clinician faces | −1 | same as AD |
| Inconsistency | −1 | I² = 68.9% | −1 | I² = 85.8% |
| Imprecision | 0 | 95% mHK interval spans 0.10 (0.782–0.883); 95% PI 0.652–0.935 | −1 | 95% mHK interval spans 0.21 (0.665–0.873), crossing the serious-imprecision threshold; 95% PI 0.386–0.956 |
| Publication bias | 0 | not assessable by test: Egger p = 0.026 (one per study) and 0.025 (every estimate), with 9 studies | 0 | not assessable by test: Egger p = 0.66 and 0.16, with 9 studies |
| **Total** | **4** | → **very low** | **5** | → **very low** |

**Publication bias rule, revised.** Until the second pass, a significant every-row Egger test triggered a downgrade automatically. Correcting one study's implausible interval moved that test from p < 0.0001 in PD and p = 0.15 in AD to p = 0.16 in PD and p = 0.025 in AD: a verdict that swaps diseases when one interval is corrected is not a stable basis for a GRADE judgement. The rule now takes a step only with at least ten independent studies and a significant test on both pools; below ten studies the domain is "not assessable by test" and small-study effects cannot be excluded. Under the old rule AD would have lost one more step and PD one fewer; neither rating would change, since both are already very low.

Risk of bias and indirectness both trace back to the case-versus-healthy-control design, but rating both is not double-counting: risk of bias asks whether the design threatens the internal validity of each study's estimate for its own comparison; indirectness asks whether that comparison answers the question a clinician faces. GRADE guidance for diagnostic test accuracy treats a case-control design as a threat to both (Schünemann et al. 2020, part 1).

**The summary of findings is exploratory, combined-disease, and not the basis for either rating.** Applying the bivariate operating point of Section 7 (sensitivity 0.755, specificity 0.791) to 1000 tested people:

| Pre-test probability | True positives | False positives | False negatives | PPV | NPV |
|---|---|---|---|---|---|
| 5% | 38 | 199 | 12 | 0.16 | 0.98 |
| 20% | 151 | 167 | 49 | 0.47 | 0.93 |
| 50% | 378 | 105 | 122 | 0.78 | 0.76 |

At 5% pre-test probability the test calls about 236 people positive per 1000, and 199 of those are wrong.

## 9. Literature attention versus measured performance

`scripts/06_citation_vs_performance.py`. For each miRNA, the number of **distinct articles** in the corpus mentioning it in title or abstract was counted and correlated (Spearman and Pearson) with the mean reported AUC per miRNA, over all single-miRNA estimates and restricted to those eligible for the primary pool.

**A correction that changed the answer.** These counts were, for two revisions, computed over the 234 PubMed records while the accuracy estimates already came from the PubMed-plus-Scopus corpus, so every marker that entered through Scopus was credited with zero mentions by construction. `scripts/11_attention_finding_audit.py` recomputes the correlation under each combination of inputs (`results/tables/attention_correlation_audit.csv`). The previously reported ρ = −0.61 (p = 0.012) does not survive; on the current extraction the correlation is ρ = −0.01 (p = 0.95) across 44 miRNAs and ρ = −0.09 (p = 0.64) across the 33 with an eligible estimate. The finding is withdrawn. Arm suffixes (-3p/-5p) are collapsed to the family level, and an article mentioning both "miR-125b" and "miR-125b-5p" counts once.

This analysis is **exploratory**: most miRNAs contribute a single study, and a non-significant result is not evidence of no association.

## 10. What this design cannot deliver

- It measures **reported** accuracy, not accuracy under prospective clinical use. No included study pre-specified its threshold, so reported sensitivity and specificity are optimistic. AUC is threshold-independent, so threshold choice does not by itself inflate AUC; what can inflate AUC is the choice of which markers were tried and reported, which combination was kept, and whether the evaluation participants informed those choices. Only one pooled study (Qin et al. 2026) evaluated a model locked in advance in an independent cohort, and even that cohort came from the same centre.
- Restriction to PubMed Central open-access full texts and to abstracts may select a non-random subset of the literature. Five eligible studies (two of them in the PD panel subgroup) are known only from abstracts, and their design and pre-analytical fields cannot be assessed.
- Pre-analytical reporting is sparse: among the 18 pooled studies, 2 measured haemolysis and excluded affected samples, 1 excluded haemolysed samples without stating the method, 2 describe handling intended to avoid it, and 11 do not mention it; medication status is not reported by 9. The design table records these gaps; it cannot fill them.
- Estimates within a study are correlated. The one-estimate-per-study selection removes the correlated rows before pooling rather than averaging over them; it does not model residual correlation with a multilevel or robust-variance structure. Section 5b shows how far the answer moves under other selections.
- Egger's test is underpowered at fewer than ten studies per disease and is reported as exploratory only.
- No individual participant data were available. The bivariate synthesis rests on 2×2 tables reconstructed from published proportions and group sizes, and it covers the 12 circulating studies that state a threshold rather than the 18 pooled on AUC.
- Extraction, second-pass verification and risk-of-bias assessment were performed by a single reviewer, not by two independent reviewers.

## 11. Mechanistic layer: ODE models and structural figures

This layer asks something narrower than the meta-analysis, and it should be read that way. It does not test whether a miRNA works as a biomarker. It asks what the measured kinetics of each axis allow, and where a claim about them outruns the numbers that exist.

**Where the parameters come from.** Every rate, half-life and concentration used by `scripts/12_ode_models_calibrated.py` is loaded by identifier from `data/extracted/kinetic_parameters.csv` (67 rows, 15 primary sources). Values were read from full texts or from supplementary files, never from abstracts or from secondary citations, and each numeric row stores the sentence it came from. The table separates four kinds of row: measured numbers, qualitative constraints (a result stated without a usable number, such as nucleation being undetectable at neutral pH), declared gaps, and values derived by us from a primary table. The loader refuses anything that is not a measured number, so a gap cannot be filled silently.

**What is measured and what is not.** Aβ42 production and clearance come from stable-isotope labelling kinetics in human CSF (Mawuenyega et al. 2010, DOI 10.1126/science.1197623). Aggregation exponents and the critical fibril concentration come from Cohen et al. 2013 (DOI 10.1073/pnas.1218402110), and human brain Aβ42 loads from its Table S2. α-synuclein elongation and its pH dependence come from Buell et al. 2014 (DOI 10.1073/pnas.1315346111). miRNA half-lives come from Zhang et al. 2011, Gantier et al. 2011, Kingston and Bartel 2019 and Kleaveland et al. 2018, and protein turnover from Li et al. 2004, Liu et al. 2019 and Fornasiero et al. 2018. Aggregation rate constants that no source gives as a number (Aβ42 nucleation and elongation, α-synuclein nucleation at acidic pH) are fixed at declared **illustrative** values, listed with their reasons in the output; no reported finding depends on them. Two further quantities were never measured for these genes and are left **free**: the strength of miRNA repression and the translation rate. Each is scanned over a declared range on a geometric grid; neither is tuned to reach a result.

mRNA decay used to be a third free parameter and is not any more. Tushev et al. 2018 report it per 3'UTR isoform in cultured rat hippocampal neurons: SNCA has one isoform at 6.53 h (K066), while BACE1 has five, with half-lives from 2.8 to 23.9 h (K067). A pool of isoforms does not decay with the mean of their half-lives, so the BACE1 rate is the abundance-weighted mean of the **rate constants**, 0.0456 h⁻¹, an effective half-life of 15.2 h (K068); the mean of the half-lives would give 17.4 h, which is the wrong quantity. Two cautions came out of reading that table. Its decay was observed over 16 h, so the APP half-life of 51.4 h (K069) is an extrapolation and is recorded with a warning rather than used. And the paper's own neuron-enriched summary reproduces from the table only when half-lives above about 25 h are excluded (median 7.394 h against the printed 7.38), while the glia summary does not reproduce under any filter tried — so K044 is quoted as printed and never recomputed.

**Experiments run.** (i) The AD arm compares a 30% clearance deficit with the measured 1.5% production difference, and finds the miR-29 mimic dose that would offset the clearance deficit by lowering BACE1. (ii) Single-dose mimic washout: the time for a 10-fold bolus to decay within 10% of baseline at each measured half-life. (iii) Human brain Aβ42 loads expressed as multiples of the critical concentration above which secondary nucleation dominates. (iv) The α-synuclein arm with nucleation switched off at neutral pH, where Buell et al. found it undetectable (K011), and on below pH 6, where they report that secondary nucleation "increases dramatically" (K042). The source gives the direction of that switch, not its size, so the acidic-pH rate constant is swept over four orders of magnitude; the fold change in fibril number then ranges from about 500 to about 14,000, and only the direction is reported as a result. (v) The miR-29 dose the clearance experiment requires, set beside a measured effect: Hébert et al. 2008 report about 50% BACE1 knockdown on miR-29a/b-1 transfection in SK-N-SH cells (K047). At steady state the BACE1 level is analytic in the mimic factor, so the knockdown the required dose produces, and the dose that would reproduce the measured 50%, are both computed in closed form over the declared ranges of the two free parameters they depend on. (vi) Two calculations that use no free parameter at all, because they combine measured quantities directly. The α-synuclein concentration in a presynaptic bouton, 21.6 µM (derived from the combined synuclein copy number and the measured α:β ratio of 0.98:1, Wilhelm et al. 2014 table S1), is placed on the measured elongation saturation curve, whose half-maximal concentration is 46–50 µM (Buell et al. 2014): the protein sits at 30–32% of maximal elongation rate, below half-saturation, where a 1% fall in concentration buys a 0.68–0.70% fall in elongation rate. The same curve then carries a measured knockdown through to a rate: miR-7 lowers α-synuclein by 30% on a 3'UTR reporter and miR-7 with miR-153 lowers endogenous α-synuclein by 43% in rat cortical neurons (Doxakis 2010), which on the saturation curve become a 23% and a 34% slower elongation — less than proportional, because the curve saturates. Separately, BACE1 and APP are counted in the same preparation, 116 against 6284 copies per bouton. Both cross systems — an in vitro saturation constant against a rat synaptosome — and are reported as statements about regime and stoichiometry, not as rates. (vii) A scan of the free parameters, with every run classed as AD above control, at or below control, or not evaluable. A run that fails numerically is reported as not evaluable, never counted as a reversal. Integration uses LSODA (`scipy.integrate.solve_ivp`, rtol 1e-8, atol 1e-10).

**What the models can and cannot claim.** The AD/control monomer ratio (1.41) equals the ratio of production to clearance measured by Mawuenyega et al. and is independent of every free parameter. The model restates that measurement; it does not predict it. The value of the models is elsewhere: they show that miR-29 paralogues decay at different rates (7 h and 10.6 h, one reported as stable) and cannot be treated as one species, that a single miR-7 mimic dose would be back near baseline within 11 to 32 hours against about 9 days for a typical miRNA, that the BACE1 knockdown needed to offset the measured clearance deficit is 30–33% across the free-parameter grid and therefore smaller than the roughly 50% already achieved in cells, that a measured miR-7 knockdown of α-synuclein translates into a 23–34% slower fibril elongation through three independent measurements and no free parameter, and that the Aβ42 rate constants needed to go further cannot be separated with the published data (row K037).

**What repeated dosing costs a fast-turning-over mimic.** `scripts/17_mimic_dosing_feasibility.py` asks a question the washout calculation raises but does not answer: if a mimic has to be given repeatedly rather than once, what does the measured half-life cost? At steady state under repeated dosing of a species cleared with first-order constant *d* at interval *T*, the ratio of peak to average concentration is *dT* / (1 − e^(−*dT*)). The dose cancels, so the calculation has no free parameter at all; only the measured decay constants enter, loaded by identifier from the kinetic table.

Dosed once a day, a miR-7 mimic that turns over like endogenous miR-7 (half-life 1.7 h, K020) must peak at **9.79×** its average level, against **1.26×** for a miRNA of median stability (34 h, K016) — a **7.7-fold** penalty in the peak needed to hold the same average. It spends **7.1%** of each day above half its own peak. To be dosed daily on the terms an ordinary miRNA enjoys, it would need roughly **20-fold** stabilisation (1.7 h → 34 h); at its measured half-life the equivalent interval is **1.2 h**. Under the upper-bound miR-7 half-life (5 h, K021) the requirement falls to 6.8-fold, and for the miR-29 paralogues to 4.9-fold (miR-29b) and 3.2-fold (miR-29c). The result is stated as a required fold stabilisation rather than as a verdict, because a chemically stabilised mimic is by construction not cleared at the endogenous rate; it is a design target the measurements set, and it is the quantity a delivery chemistry has to beat.

**A graphical abstract from the same numbers.** `scripts/18_graphical_abstract.py` draws one schematic figure spanning both axes, for a reader who wants the mechanism before the results section. Every number placed on it - the AD/control ratio, the BACE1:APP stoichiometry, the required knockdown, the elongation slowdown, the dosing penalty - is loaded at draw time from the same JSON and CSV files `scripts/08` already checks, and a manifest (`results/tables/graphical_abstract_values.json`) records what was drawn. The Argonaute2 inset reuses `scripts/13`'s own render (PDB 6N4O) rather than a second, unverified drawing of the same molecule; because that structure carries human AGO2 loaded with miR-122, not miR-29 or miR-7, the caption says so rather than implying otherwise.

**Animating the same simulations.** `scripts/19_mechanism_animations.py` produces three GIFs, and reuses rather than re-derives: it imports the ODE right-hand sides and measured constants directly from `scripts/12`, and the closed-form dosing formula from `scripts/17`, so an animation cannot compute a different number from the one already checked. (i) Aβ42 monomer accumulating to its new steady state, control versus AD — no free parameter, since production and clearance are both measured. (ii) A single 10-fold mimic bolus washing out at the measured half-life, miR-7 against a median-stability miRNA. (iii) The repeated-dosing sawtooth: concentration relative to its own average, over four daily doses, for the same two species, so the peak height read directly off the axis is the peak-to-average penalty. Each GIF's final frame is written to `results/tables/mechanism_animations.json`, and `scripts/08` checks it against `ode_calibrated_results.json` and `mimic_dosing_feasibility.json` rather than trusting that the animation and the static figure agree. The α-synuclein pH-gate fibril growth is deliberately not animated: its acidic-pH rate constant is illustrative (K042), and animating it would put a specific speed on screen for a quantity this project reports only as a direction.

**Structural figures.** `scripts/13_structure_figures.py` renders four deposited structures with PyMOL: human Argonaute2 with a guide and target (6N4O), BACE1 with a bound inhibitor (4D8C), a full-length α-synuclein fibril (6CU7) and an Aβ(1-42) fibril (5OQV). Title, method, resolution and primary citation are read from each file, and the script stops if the title does not match the molecule the figure claims to show. The BACE1 catalytic aspartates are found twice, by sequence motif and by distance to the inhibitor, and must agree. Fibril protofilaments are assigned from the coordinates as chains stacked at the cross-β spacing. The figures illustrate mechanism; they are not a result.

**One composite panel, not four loose images.** `scripts/20_structure_story_panel.py` arranges four of `scripts/13`'s own PNGs into a single figure, captioned entirely from `results/tables/structure_figure_provenance.json` - no PyMOL session is reopened and no new claim is made. Panels are grouped by which axis they belong to with a coloured accent bar (blue for the Alzheimer's axis, orange for Parkinson's, grey for what both axes share), not chained with arrows: BACE1 does not structurally become the Aβ fibril, and no arrow claims it does.

## 12. Figures in two languages

Every figure in `results/figures/` is emitted twice, once in English and once in Brazilian Portuguese, as `<name>.en.png` and `<name>.pt-BR.png`. The two versions are produced by the same code path in the same run from the same arrays: `scripts/_bilingual.py` exposes the language list, a `t(lang, en, pt)` chooser for label text and a path builder, and each plotting function is called once per language. Only words are translated. Numbers, axis limits, tick positions and the data themselves are identical by construction, because they are computed before the language loop begins and are not passed through the translator — a figure pair cannot disagree about a value without the code that drew it having changed.

## References for the methods

- DerSimonian R, Laird N. Meta-analysis in clinical trials. *Control Clin Trials.* 1986;7(3):177–188.
- Paule RC, Mandel J. Consensus values and weighting factors. *J Res Natl Bur Stand.* 1982;87(5):377–385.
- Hartung J, Knapp G. On tests of the overall treatment effect in meta-analysis with normally distributed responses. *Stat Med.* 2001;20(12):1771–1782.
- IntHout J, Ioannidis JPA, Borm GF. The Hartung-Knapp-Sidik-Jonkman method for random effects meta-analysis is straightforward and considerably outperforms the standard DerSimonian-Laird method. *BMC Med Res Methodol.* 2014;14:25.
- Borenstein M, Hedges LV, Higgins JPT, Rothstein HR. *Introduction to Meta-Analysis.* Chichester: John Wiley & Sons; 2009.
- Hanley JA, McNeil BJ. The meaning and use of the area under a receiver operating characteristic (ROC) curve. *Radiology.* 1982;143(1):29–36.
- Egger M, Davey Smith G, Schneider M, Minder C. Bias in meta-analysis detected by a simple, graphical test. *BMJ.* 1997;315(7109):629–634.
- Page MJ, McKenzie JE, Bossuyt PM, et al. The PRISMA 2020 statement: an updated guideline for reporting systematic reviews. *BMJ.* 2021;372:n71.
- Whiting PF, Rutjes AWS, Westwood ME, et al. QUADAS-2: a revised tool for the quality assessment of diagnostic accuracy studies. *Ann Intern Med.* 2011;155(8):529–536.
- Reitsma JB, Glas AS, Rutjes AWS, Scholten RJPM, Bossuyt PM, Zwinderman AH. Bivariate analysis of sensitivity and specificity produces informative summary measures in diagnostic reviews. *J Clin Epidemiol.* 2005;58(10):982–990.
- Schünemann HJ, Mustafa RA, Brozek J, et al. GRADE guidelines: 21 part 1 and part 2. Test accuracy. *J Clin Epidemiol.* 2020;122:129–141 and 142–152.
- McInnes MDF, Moher D, Thombs BD, et al. Preferred Reporting Items for a Systematic Review and Meta-analysis of Diagnostic Test Accuracy Studies: the PRISMA-DTA statement. *JAMA.* 2018;319(4):388–396.
