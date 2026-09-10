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

Returns: **168 records** (AD arm) and **97 records** (PD arm); **234 unique records** after deduplication, of which **30** were retrieved by both arms. The exact submitted strings, the PubMed query translations and the retrieved PMIDs are stored in `data/raw/systematic_review_2026/search_strategy.json`; `scripts/03_systematic_search.py` re-runs the searches.

Because PubMed grows daily, a later re-run will return more records than the frozen counts above. That is expected behaviour, not an inconsistency: the archived strategy file is what the reported numbers refer to.

**Scopus.** Scopus was searched with the same two-arm strategy on 10 September 2026 and the result sets exported under institutional authentication, because Scopus cannot be queried by API from this environment. The exports are archived in `data/raw/systematic_review_2026/exports/` and ingested by `scripts/09_ingest_scopus_wos.py`, which normalises them and deduplicates against the PubMed corpus and against every previously ingested arm, by DOI, PubMed ID and normalised title.

Returns: **408 records** (AD arm), of which 248 were new to the review, and **255 records** (PD arm), of which 98 were already in the PubMed corpus and 79 had already arrived with the Scopus AD arm — a paper naming both diseases is returned by both searches and must be counted once. The PD arm therefore contributed **78** new records, and the corpus totals **560 unique records**.

That cross-arm step is not incidental. Without it the PD arm appeared to add 157 records rather than 78, because the same paper was being counted in two arms.

**Databases not searched.** Web of Science was not searched. This is a real limitation on completeness and is declared rather than approximated — no estimated record counts are reported for a database that was not actually queried.

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

Full texts were retrieved from PubMed Central for **47 studies**. Extraction followed three rules:

**Automated mining locates candidates; a human records values.** Regular expressions surfaced every sentence containing an accuracy metric together with its surrounding context. Those sentences were then read, and the values transcribed by hand. This division of labour is not ceremonial: the patterns demonstrably mis-assign sensitivity to specificity when a sentence reverses their order, capture p-values in a specificity slot, and treat a *decrease* in AUC during permutation testing as an AUC. None of those errors survives reading the sentence, and all of them would survive automated capture.

**Every value stores the sentence that supports it.** Each row of `data/extracted/diagnostic_accuracy_extraction.csv` carries a `verbatim_quote` column with the exact wording from the source, plus PMID and DOI.

**Values attributed to other studies are not extracted.** Discussion sections routinely quote AUCs from other papers ("Han et al. found…", "Wen et al. reported…"). Such sentences were identified and excluded; only each study's own results were recorded.

For every estimate the following were captured where stated: miRNA (or panel composition), disease, comparison and comparison class, biofluid, cohort stage (discovery / training / validation / single), number of cases and controls, AUC with its confidence interval, sensitivity, specificity, and measurement method.

### Eligibility for the primary pool

An estimate enters the primary pool only if it is a **case-versus-control contrast in a defined AD or PD population**, measuring **one or more miRNAs and nothing else**. Of 76 extracted estimates, **51** qualified. The 25 that did not are retained in the table with an explicit `exclusion_reason`:

| Reason | Example |
|---|---|
| Composite comparator | AD discriminated jointly against FTD *and* controls |
| Within-disease contrast | PD with vs without cognitive impairment |
| Prodromal population | isolated REM sleep behaviour disorder rather than established PD |
| Genotype stratification | LRRK2 carriers rather than sporadic PD |
| Mixed population | "neurodegenerative pathology" without disease-specific breakdown |
| Unstable estimate | AUC = 1.000 by perfect separation in a 6-patient subgroup |
| Cohort not attributable | AUC reported without a resolvable cohort or group size |
| Composite model | miRNA combined with non-miRNA clinical variables, with MRI parameters, or with a lncRNA, circRNA or protein |
| Mixed RNA panel | panel containing piRNAs and rRNA pseudogenes alongside miRNAs |
| Index test not a miRNA | a lncRNA, a circRNA, a brain-tissue gene signature or a faecal microbiome genus |

**Duplicate publication.** PMIDs 40661348 and 41836608 report the same cohort, the same markers and the same AUCs (preprint and journal version of one study). The pair was detected by identical verbatim result sentences and counted once.

## 5. Statistical synthesis

Implemented in `scripts/05_meta_analysis.py` using NumPy and SciPy only, so that every step is inspectable rather than delegated to a black-box package.

**Standard errors.** When the source reported a 95% CI, SE = (upper − lower) / (2 × 1.96). Otherwise SE was computed from Hanley & McNeil (1982) using the case and control group sizes. Estimates with neither a CI nor group sizes cannot be weighted and are excluded from pooling — **41 of the 51** eligible estimates, from **20 independent studies**, were poolable.

**Study identity.** A study is keyed on its PubMed ID when it has one and on its DOI otherwise. Keying on PMID alone collapsed the studies published outside MEDLINE into a single blank-PMID group, so two independent cohorts that both report miR-124 in PD serum were being counted as one. The SE source is recorded per estimate in `results/tables/meta_analysis_input_estimates.csv`.

*Validation of this step:* for PMID 33129241 (AUC 0.75, 18 cases vs 18 controls) the Hanley–McNeil formula returns SE = 0.0822, against SE = 0.08 reported independently by the article itself.

**Pooling.** AUCs were transformed to the logit scale, where they are unbounded and better approximate normality, with the SE propagated by the delta method (SE_logit = SE_AUC / [AUC(1 − AUC)]). Estimates were combined with the DerSimonian & Laird (1986) random-effects estimator and back-transformed for reporting. Random effects were chosen a priori: the studies differ in biofluid, platform, population and cut-off derivation, so a common true AUC is not a plausible assumption.

**Heterogeneity** is reported as Cochran's Q with its p-value, τ² on the logit scale, and I².

**Small-study effects** were assessed with Egger's regression of the standard normal deviate on precision.

**Subgroups**, prespecified: by disease (AD, PD), by marker type (single miRNA vs multi-miRNA panel), and by biofluid where at least three estimates from **at least three independent studies** were available. The study condition was added after the estimate-only rule produced a biofluid subgroup of eight estimates drawn from one cohort, which reports within-study spread as though it were between-study evidence.

**Sensitivity to clustering.** Several studies contribute more than one estimate — one contributes eight — and the random-effects model treats each as independent. Rather than assume this away, `scripts/05_meta_analysis.py` re-pools the single-miRNA estimate two further ways: one estimate per study (the study's median AUC and median SE), and leave-one-study-out. Both are reported in `results/tables/sensitivity_single_mirna.csv`, and the spread between them is treated as part of the result rather than as a footnote.

## 6. Literature attention versus measured performance

`scripts/06_citation_vs_performance.py`. For each miRNA, the number of **distinct articles** in the **560-record** corpus mentioning it in title or abstract was counted.

**A correction that changed the answer.** These counts were, for two revisions, computed over the 234 PubMed records while the accuracy estimates already came from the full PubMed-plus-Scopus corpus. Every marker that entered through Scopus was therefore credited with zero mentions by construction, which inflated the association between attention and performance. `scripts/11_attention_finding_audit.py` recomputes the correlation under each combination of inputs and separates the contribution of the bug from that of the new data; the result is in `results/tables/attention_correlation_audit.csv`. The previously reported ρ = −0.61 (p = 0.012) does not survive, and the finding is withdrawn. Counting distinct articles rather than raw occurrences matters: an article writing both "miR-125b" and "miR-125b-5p" must not count twice for the miR-125b family. Arm suffixes (-3p/-5p) were collapsed to the family level so that a mention of "miR-146a" can be matched to an estimate reported for "miR-146a-5p".

Mention counts were then correlated (Spearman and Pearson) with the mean reported AUC per miRNA. The analysis was run twice: over all single-miRNA estimates, and restricted to those eligible for the primary pool.

This analysis is **exploratory**. Most miRNAs contribute a single study, the test is underpowered, and a non-significant result cannot be read as evidence of no association.

## 7. What this design cannot deliver

- It measures **reported** accuracy, not accuracy under prospective clinical use. Most included estimates derive their cut-off in the same sample where they evaluate it, which inflates AUC.
- Restriction to PubMed Central open-access full texts and to abstracts may select a non-random subset of the literature.
- Estimates within a study are correlated, and the model does not account for it. The sensitivity analyses in Section 5 measure the consequence instead.
- With significant Egger tests in several subgroups, pooled values should be read as **upper bounds**.
- No individual participant data were available, so bivariate sensitivity–specificity (HSROC) modelling was not performed; the synthesis is on AUC.

## References for the methods

- DerSimonian R, Laird N. Meta-analysis in clinical trials. *Control Clin Trials.* 1986;7(3):177–188.
- Hanley JA, McNeil BJ. The meaning and use of the area under a receiver operating characteristic (ROC) curve. *Radiology.* 1982;143(1):29–36.
- Egger M, Davey Smith G, Schneider M, Minder C. Bias in meta-analysis detected by a simple, graphical test. *BMJ.* 1997;315(7109):629–634.
- Page MJ, McKenzie JE, Bossuyt PM, et al. The PRISMA 2020 statement: an updated guideline for reporting systematic reviews. *BMJ.* 2021;372:n71.
