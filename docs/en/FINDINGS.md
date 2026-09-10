# Findings

*What the pooled evidence says about circulating microRNAs as diagnostic biomarkers in Alzheimer's and Parkinson's disease.*

🇧🇷 Versão em português: [../pt-BR/ACHADOS.md](../pt-BR/ACHADOS.md)

---

## 1. What was synthesised

234 unique records were screened; 189 were primary studies; 95 reported an AUC or a sensitivity–specificity pair; 45 full texts were read; 26 studies yielded 42 extractable estimates, of which 28 met the eligibility rules and 24 (from 15 independent studies) had an estimable standard error and could be weighted.

The attrition is worth stating plainly: **fewer than one in ten screened records ended up contributing a weighted estimate.** Most of that loss is not the reviewer's doing. It comes from studies that report an AUC without the group sizes or confidence interval needed to weight it, from full texts locked behind subscriptions, and from comparisons that sound like "AD versus controls" but are actually something else on reading.

## 2. Single miRNAs do not reach clinical usefulness

Pooled AUC for a single circulating miRNA is **0.745 (95% CI 0.699–0.785)** across 16 estimates from 9 studies.

That number should be read against what it would have to beat. An AUC around 0.80 is the conventional floor for a standalone diagnostic test; established plasma phospho-tau assays for AD sit well above 0.90. A pooled 0.745, with an upper confidence bound of 0.785, does not reach the floor — the entire interval sits below 0.80.

The AD single-miRNA subgroup is the most informative result in the analysis, because it is the one with **I² = 0%**. Six estimates from five different studies, in different biofluids, on different platforms, converge on 0.774 (0.732–0.810) with no detectable between-study heterogeneity. This is not a noisy literature that might contain a strong signal if only it were measured better. It is a consistent, well-replicated, *modest* effect. Consistency at a mediocre value is a more discouraging result than inconsistency, because it removes the hope that better methodology would move the estimate.

PD single miRNAs pool lower still, at 0.716 (0.641–0.781), with moderate heterogeneity (I² = 55%).

## 3. Panels are where the gain is, and the gap is not noise

Multi-miRNA panels pool at **0.888 (0.829–0.928)** — and the confidence intervals of the two marker types do not overlap:

| | Pooled AUC | 95% CI |
|---|---|---|
| Single miRNA | 0.745 | 0.699 – 0.785 |
| Multi-miRNA panel | 0.888 | 0.829 – 0.928 |

Non-overlapping intervals are a conservative test, and this comparison passes it. The practical reading is directional: the productive move is combining markers, not continuing to search for a better individual one. This is consistent with the biology the source monograph argued for — miRNAs act as network modulators, each with modest individual leverage over many targets — but here it arrives as a measured effect rather than an inference from mechanism.

Two cautions attach to the panel estimate. Panel heterogeneity is high (I² = 85%), and panels are precisely the marker type most exposed to overfitting: many derive their weights and their cut-off in the same sample where they report performance. The panel figure is therefore the one most likely to shrink under external validation.

## 4. The field's attention points away from performance

Counting how many corpus articles mention each miRNA and correlating that with its measured AUC gives:

- across all single-miRNA estimates: Spearman ρ = −0.11 (p = 0.62)
- restricted to estimates eligible for the primary pool: **ρ = −0.41 (p = 0.14)**

Neither is statistically significant, and with most miRNAs contributing a single study the test is underpowered — a null result here is not evidence of no association, and the negative coefficient is a signal to investigate, not a conclusion.

But the pattern in the individual values is hard to ignore:

| miRNA | Articles mentioning it | Reported AUC |
|---|---|---|
| miR-125b | 13 | 0.753 |
| miR-146a | 11 | 0.680 |
| miR-34a | 10 | 0.738 |
| … | | |
| miR-128 | 2 | 0.831 |
| let-7i | 1 | 0.835 |
| miR-501 | 1 | 0.820 |

The two most-discussed miRNAs in the corpus sit at the *bottom* of the performance distribution, and three of the best performers are barely discussed at all. miR-146a in particular — one of the anchor molecules of the amyloid-inflammation narrative, and one of the two axes modelled in the source monograph — returns the lowest AUC in the eligible set.

This is the quantitative answer to the circularity problem the monograph raised about itself. Bibliometric frequency and catalogued experimental validation both track prior research attention, so their agreement proves little. Pooled diagnostic accuracy is an external criterion, and by that criterion the correlation with attention is absent or inverse. A miRNA becomes prominent by being mechanistically interesting and easy to assay, not by discriminating patients well.

## 5. The pooled values are upper bounds, not neutral estimates

Egger's test is significant in several subgroups, including the overall pool and the PD subgroup. Combined with two structural features of this literature — cut-offs derived in the same sample where they are evaluated, and small cohorts (many under 50 per arm) — the direction of bias is predictable and one-way.

Every pooled figure in this analysis should therefore be read as **the optimistic end** of the plausible range. That matters most for the headline: if 0.745 is already the optimistic estimate for a single miRNA, the realistic figure is lower.

## 6. Nothing has reached the clinic

The preclinical literature on miRNA mimics and antagomiRs in neurodegeneration is substantial, and the source monograph itself simulated a miR-29c/miR-107 mimic therapy. ClinicalTrials.gov, queried on 10 September 2026, gives the state of actual human testing (`scripts/07_clinical_translation_landscape.py`).

**Across all indications, 16 registered trials of miRNA-directed agents, from 5 distinct molecules:**

| Agent | Target | Area | Furthest phase | Trials |
|---|---|---|---|---|
| Miravirsen (SPC3649) | anti-miR-122 | Hepatitis C | Phase 2 | 8 |
| Cobomarsen (MRG-106) | anti-miR-155 | Oncology | Phase 2 (terminated) | 3 |
| MRG-201 / remlarsen | miR-29 mimic | Dermatology / fibrosis | Phase 2 | 2 |
| MRX34 | miR-34a mimic | Oncology | Phase 1/2 (terminated) | 2 |
| TargomiRs | miR-16 mimic | Oncology | Phase 1 | 1 |

**In Alzheimer's or Parkinson's disease: zero.** Thirteen registered trials mention miRNAs in AD or PD; eight are observational biomarker studies, two measure miRNAs as an outcome of exercise or rehabilitation, and the three interventional trials with a drug are testing something else — gemfibrozil (a fibrate), NIO752 (an antisense oligonucleotide against tau mRNA) and CpG1018 (a TLR9-agonist adjuvant). None administers a miRNA mimic or an anti-miR.

Two details sharpen this. First, the modality's track record where it *has* been tried is uneven: MRX34 was terminated, cobomarsen's Phase 2 and its extension were both terminated, and miravirsen did not advance past Phase 2. Second — and this is the detail that matters most for the source monograph — **MRG-201/remlarsen is a miR-29 mimic that reached Phase 2**, which is precisely the axis the monograph modelled as a therapy (miR-29c/miR-107 → BACE1 → Aβ). It was developed for keloid scarring and delivered by intradermal injection. The molecule class exists clinically. What does not exist is a route to the brain.

That reframes the simulated "miRNA mimic therapy" honestly: the barrier is not whether such a molecule can be made, but delivery across the blood–brain barrier and a therapeutic window narrow enough that the monograph's own simulations produced over-suppression below physiological baseline.

*Caveat, stated rather than hidden:* registry searches match on intervention names and free text, so an agent described under nomenclature none of the query terms covers would be missed. The exact queries are stored in `data/raw/clinical_trials_2026/mirna_therapeutics_trials.json` so the search can be criticised and repeated. One false positive was found and excluded: a trial matching "Parkinson" through Wolff–Parkinson–White syndrome, a cardiac conduction disorder.

## 7. What follows from this

**For biomarker development.** Single-miRNA papers reporting an AUC near 0.75 are reporting the field's central value, not a discovery. The evidence supports investing in panels, in head-to-head comparison against p-tau217 rather than against no comparator, and in external validation cohorts where the cut-off is fixed in advance.

**For how this literature is read.** Frequency of mention is not evidence of performance, and in this corpus may be mildly anti-correlated with it. Reviews that rank miRNA candidates by how often they appear are ranking by attention.

**For reporting practice.** The single largest cause of data loss here was studies publishing an AUC without the group sizes or confidence interval needed to weight it. That omission removes a study from every future meta-analysis. Reporting n per arm alongside every ROC result costs nothing and would materially improve the field's cumulative evidence.

**For the modelling layer of the source monograph.** The ODE models built on the miR-29/BACE1/Aβ and miR-7/SNCA/α-synuclein axes remain useful as qualitative, hypothesis-generating structures. What this analysis adds is a boundary condition: the miRNAs at the centre of those models are not, on current evidence, strong individual discriminators of disease. That does not invalidate them as mechanistic regulators — regulatory importance and diagnostic discrimination are different claims — but it does mean the diagnostic case for them has to be made on panels, not on single markers.

## 8. Honest limitations

- PubMed/MEDLINE only; Scopus and Web of Science were not searched.
- Extraction limited to PubMed Central open-access full texts (55 of 95 eligible primary studies), a potentially non-random slice.
- 24 weighted estimates from 15 studies is a modest evidence base; subgroup cells are smaller still (PD panels: k = 2).
- Heterogeneity up to I² = 95% in some subgroups.
- The attention-versus-performance analysis is exploratory and underpowered.
- Reported accuracy is not prospective clinical accuracy.
