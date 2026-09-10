# Findings

*What the pooled evidence says about circulating microRNAs as diagnostic biomarkers in Alzheimer's and Parkinson's disease.*

🇧🇷 Versão em português: [../pt-BR/ACHADOS.md](../pt-BR/ACHADOS.md)

> **Revised 2026-09-10 after adding Scopus.** Two conclusions in the previous version did not survive the wider search, and one became stronger. Section 8 records exactly what changed and why, because a reader deserves to see that rather than a silently updated document.

---

## 1. What was synthesised

Searches: PubMed/MEDLINE returned 234 unique records across the AD and PD arms; the Scopus AD arm returned 408, of which 248 were new — **more records than the entire PubMed AD arm had found**. Total unique records: 482. The Scopus PD arm has not been run yet.

Screening left 188 primary studies from PubMed and 101 from the Scopus additions. Of those, 95 and 20 respectively reported an AUC or a sensitivity–specificity pair. Forty-five full texts were read. **34 studies** yielded **50 extractable estimates**, of which 31 met eligibility and **25 (from 16 independent studies)** had an estimable standard error and could be weighted.

Only one Scopus-derived estimate could be weighted. The rest report an AUC with no group sizes and no confidence interval — the same reporting gap that dominates the attrition throughout this review.

## 2. Single miRNAs sit at the boundary of clinical usefulness

Pooled AUC for a single circulating miRNA: **0.758 (95% CI 0.706–0.804)**, 17 estimates from 10 studies, I² = 66%.

An AUC near 0.80 is the conventional floor for a standalone diagnostic test; plasma phospho-tau assays for AD operate well above 0.90. The pooled point estimate falls below that floor and the interval's upper bound just reaches it. The honest reading is that single circulating miRNAs perform at or under the threshold, not comfortably above it — and nowhere near the established protein assays they would have to displace.

By disease: AD single miRNAs pool at 0.802 (0.741–0.851), PD at 0.716 (0.640–0.781).

## 3. Panels outperform single markers, and the intervals still do not overlap

| | Pooled AUC | 95% CI |
|---|---|---|
| Single miRNA | 0.758 | 0.706 – 0.804 |
| Multi-miRNA panel | 0.888 | 0.829 – 0.928 |

The intervals remain disjoint after the Scopus additions. This is the most robust quantitative result here, and it survived a search that overturned other conclusions.

It is also **not novel**. At least three prior meta-analyses reached the same conclusion: the Neurologia AD meta-analysis found "microRNA clusters of plasma type performed a better diagnostic accuracy"; the Neurologia PD meta-analysis found "miRNA cluster showed a better diagnostic accuracy than miRNA simple"; and Guévremont et al. pooled combinations and single markers separately for exactly this reason. What this analysis adds is the gap quantified on a common AUC scale with non-overlapping intervals — convergent evidence, not a discovery.

Two cautions stand. Panel heterogeneity is high (I² = 85%), and panels are the marker type most exposed to overfitting, since many derive their weights and cut-off in the sample where performance is reported. The panel figure is the one most likely to shrink under external validation.

## 4. Literature attention is inversely related to measured performance

This is the finding the wider search **strengthened**, and it is the one with no clear precedent in this literature.

Correlating how many corpus articles mention each miRNA with its mean reported AUC:

- across all single-miRNA estimates: Spearman ρ = −0.27 (p = 0.16)
- restricted to estimates eligible for the primary pool: **ρ = −0.61 (p = 0.012)**

With the Scopus records added, the restricted analysis crosses conventional significance (it was ρ = −0.41, p = 0.14 on PubMed alone). Sixteen miRNAs contribute, most from a single study each, so this remains exploratory and cannot support a causal reading. But the direction is now hard to dismiss as noise.

The individual values show why:

| miRNA | Articles mentioning it | Reported AUC |
|---|---|---|
| miR-125b | 13 | 0.753 |
| miR-146a | 11 | 0.680 |
| miR-34a | 10 | 0.738 |
| … | | |
| miR-128 | 2 | 0.831 |
| let-7i | 1 | 0.835 |
| miR-501 | 1 | 0.820 |

The two most-discussed miRNAs in the corpus sit at the bottom of the performance distribution. miR-146a — an anchor of the neuroinflammatory account of AD, and one of the two axes modelled in the source monograph — returns the lowest AUC among eligible estimates.

This is the quantitative answer to the circularity the monograph raised about itself. Bibliometric frequency and catalogued experimental validation both track prior research attention, so their agreement proves little. Pooled accuracy is external to that loop, and by that criterion attention and performance move in opposite directions.

## 5. The pooled values are upper bounds

Egger's test is significant in the overall pool, the PD subgroup, the single-miRNA pool and the serum subgroup. Combined with cut-offs derived in the same sample where they are evaluated, and cohorts frequently under 50 per arm, the bias runs one way. Every pooled figure here is the optimistic end of its plausible range.

## 6. Nothing has reached the clinic

ClinicalTrials.gov (10 September 2026) lists 16 registered trials of miRNA-directed agents worldwide, from five molecules: miravirsen (anti-miR-122, hepatitis C, Phase 2), cobomarsen (anti-miR-155, oncology, Phase 2, terminated), MRX34 (miR-34a mimic, terminated), TargomiRs (miR-16 mimic, Phase 1) and MRG-201/remlarsen (miR-29 mimic, dermatology, Phase 2).

**In Alzheimer's or Parkinson's disease: zero.** Thirteen registered trials mention miRNAs in AD or PD; eight are observational, two measure miRNAs as an exercise or rehabilitation outcome, and the three interventional drug trials administer gemfibrozil, a tau antisense oligonucleotide and a TLR9-agonist adjuvant — none of them miRNA-directed.

MRG-201/remlarsen is a **miR-29 mimic that reached Phase 2** — precisely the axis the source monograph simulated as a brain therapy — developed for keloid scarring and given by intradermal injection. The molecule class exists clinically; the route to the brain does not.

*Caveat:* registry searches match on names and free text, so an agent under unfamiliar nomenclature would be missed. One false positive was found and excluded (a trial matching "Parkinson" through Wolff–Parkinson–White syndrome).

## 7. This question has been asked before

Six prior meta-analyses pooled diagnostic accuracy for miRNAs in AD or PD, reporting **SROC AUCs of 0.87–0.90** (`data/raw/systematic_review_2026/prior_meta_analyses.json`).

Those numbers are not directly comparable to the 0.758 here, and the difference is mostly a difference of estimand rather than of evidence:

- **They report a summary ROC area**, fitted through study-level sensitivity–specificity pairs in a bivariate/HSROC model. That describes a fitted summary curve.
- **This analysis averages the AUCs the studies themselves reported.** That describes what a typical study observed.

The two can differ substantially on identical data. Neither is wrong; they answer different questions. A reader who wants "how good is the summary ROC curve of this literature" should use the published SROC estimates. A reader who wants "what AUC does a typical single miRNA achieve in a typical study" is closer to the number here.

Two further differences matter. Prior meta-analyses pooled single markers and combinations together in their headline figure (Guévremont et al. being the exception), which places their ~0.87 between the single-marker and panel estimates found here. And they were not restricted to open-access full texts, as this extraction was.

**What remains genuinely new in this work:** the attention-versus-performance test, the clinical-trial registry check, and an extraction table in which every value carries the verbatim sentence of its source.

## 8. What the Scopus search changed

Adding one database to a completed review altered two of four headline conclusions. That is worth stating plainly, because it is a result about method as much as about miRNAs.

| Subgroup | PubMed only | + Scopus | Verdict |
|---|---|---|---|
| Single miRNA | 0.745 (0.699–0.785), I² 46% | 0.758 (0.706–0.804), I² 66% | interval now reaches 0.80 |
| **AD single miRNA** | 0.773 (0.732–0.810), **I² 0%** | 0.802 (0.741–0.851), **I² 63%** | **homogeneity claim retracted** |
| Panel | 0.888 (0.829–0.928) | unchanged | holds |
| Attention vs AUC (eligible) | ρ = −0.41, p = 0.14 | **ρ = −0.61, p = 0.012** | **strengthened** |

Two claims from the earlier version are **withdrawn**:

1. *"The AD single-miRNA subgroup shows I² = 0%, so the limitation is a property of the measurement rather than of how it has been performed."* One additional study (miR-202, AUC 0.892, 121 cases vs 86 controls) raised heterogeneity to 63%. The homogeneity was an artefact of an incomplete search.
2. *"The entire confidence interval sits below 0.80."* It no longer does.

A third correction is independent of Scopus: a defect in the screening rule — a word boundary after `meta-analys` that stopped it ever matching "meta-analysis" — let self-declared meta-analyses through. It reclassified one PubMed record and affected no extracted study, but it is why the prior meta-analyses in Section 7 went unnoticed until the Scopus records were screened.

The general lesson is uncomfortable and worth carrying into the manuscript: a single-database systematic review can produce a clean, confident, homogeneous result that a second database dissolves.

## 9. Honest limitations

- The Scopus PD arm has not been run. Coverage is asymmetric between diseases, and the PD estimates rest on PubMed alone.
- Web of Science has not been searched.
- Extraction is restricted to open-access full texts and abstracts; 20 of the 25 weighted standard errors are reconstructed by Hanley–McNeil rather than taken from a published interval.
- Twenty-five weighted estimates from 16 studies is a modest base, and some subgroup cells are very small (PD panels, k = 2).
- Heterogeneity reaches I² = 94%.
- The attention-versus-performance analysis is exploratory; significance at n = 16 with mostly single-study miRNAs is fragile.
- Reported accuracy is not prospective clinical accuracy, and the difference is not neutral.
