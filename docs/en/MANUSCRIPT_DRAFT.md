# Attention without accuracy: circulating microRNAs as diagnostic biomarkers in Alzheimer's and Parkinson's disease — a systematic review and meta-analysis

*Draft manuscript. All quantitative statements trace to `data/extracted/diagnostic_accuracy_extraction.csv`, where each value is stored with the verbatim sentence of its source.*

🇧🇷 Versão em português: [../pt-BR/MANUSCRITO_RASCUNHO.md](../pt-BR/MANUSCRITO_RASCUNHO.md)

**Wesley Felipe Capucho¹, Roberta Sessa Stilhano Yamaguchi¹**
¹ Universidade Federal de São Paulo (UNIFESP), Instituto de Saúde e Sociedade, Santos, SP, Brazil.

---

## Abstract

**Background.** Circulating microRNAs have been proposed as minimally invasive biomarkers for Alzheimer's disease (AD) and Parkinson's disease (PD) for more than a decade. The literature is large and enthusiastic, but its individual estimates have rarely been pooled, and the miRNAs that dominate that literature have never been checked against how well they actually discriminate patients.

**Methods.** We searched PubMed/MEDLINE (2015 to 10 September 2026) for studies reporting the diagnostic accuracy of miRNAs measured in a biofluid in AD or PD. Screening followed PRISMA 2020. Accuracy values were extracted from open-access full texts, each recorded together with the verbatim sentence supporting it. Areas under the ROC curve were pooled on the logit scale using DerSimonian–Laird random effects, with standard errors from reported confidence intervals or from Hanley–McNeil where group sizes were available. We then tested whether how often a miRNA is mentioned in the corpus predicts its measured accuracy, and queried ClinicalTrials.gov for miRNA-directed therapeutics.

**Results.** Of 234 unique records screened, 189 were primary studies and 95 reported an AUC or a sensitivity–specificity pair; 26 studies yielded 42 extractable estimates, 24 of which (15 independent studies) could be weighted. Single circulating miRNAs pooled at AUC 0.745 (95% CI 0.699–0.785). Multi-miRNA panels pooled at 0.888 (0.829–0.928), with confidence intervals that do not overlap those of single markers. The AD single-miRNA subgroup showed no detectable heterogeneity (I² = 0%, pooled 0.773, 0.732–0.810). Literature attention did not predict measured accuracy (Spearman ρ = −0.11, p = 0.61 overall; ρ = −0.41, p = 0.14 among eligible estimates): the two most-discussed miRNAs in the corpus, miR-125b and miR-146a, returned AUCs of 0.75 and 0.68. Egger's test indicated small-study effects in several subgroups. No miRNA mimic or antagomiR has entered a registered clinical trial for AD or PD.

**Conclusions.** Pooled across the published literature, a single circulating miRNA does not reach the accuracy expected of a standalone diagnostic test, and the consistency of that finding in AD (I² = 0%) suggests the limitation is real rather than methodological. Panels perform materially better and are where the field's effort belongs. The prominence of individual miRNAs in this literature reflects research attention rather than diagnostic performance.

**Keywords:** microRNA; Alzheimer's disease; Parkinson's disease; diagnostic accuracy; meta-analysis; biomarkers; publication bias.

---

## 1. Introduction

The case for circulating microRNAs as biomarkers of neurodegeneration has always been easy to make. They are stable in plasma, serum and cerebrospinal fluid; they can be measured by qPCR in any reasonably equipped laboratory; and because a single miRNA regulates many transcripts, each one carries information about whole pathways rather than a single protein. Against a disease that is currently diagnosed by clinical criteria plus expensive imaging or an invasive lumbar puncture, a blood test built on these molecules is an attractive prospect.

More than a decade of work has followed from that premise. Individual studies report that miR-29 family members track BACE1 expression and amyloid processing in AD, that miR-7 and miR-153 repress SNCA and modulate α-synuclein accumulation in PD, and that miR-146a sits at the centre of the neuroinflammatory response through IRAK1 and TRAF6. Reviews of this literature have listed dysregulated miRNAs, mapped them onto pathways, and concluded that they hold promise.

What has been done far less often is to ask the arithmetic question. If one collects the reported areas under the ROC curve and pools them, what accuracy does a circulating miRNA actually achieve? And a second question follows immediately, one that reviews of this field are structurally unable to answer: are the miRNAs that dominate the literature the ones that perform best?

That second question matters more than it might appear. The usual way of establishing that a miRNA is important is to show that it is frequently reported and that its target interactions are experimentally catalogued. But those two criteria are not independent. A miRNA that attracted early attention accumulates both citations and validated interactions, and its accumulated prominence then attracts further study. Bibliometric frequency and catalogued validation share a common cause, so their agreement is weak evidence of biological or clinical importance. Pooled diagnostic accuracy, measured in patients, is external to that loop.

We therefore did three things. We performed a systematic review and random-effects meta-analysis of the diagnostic accuracy of circulating miRNAs in AD and PD. We tested whether attention in this literature is associated with measured performance. And, because the field's ambitions extend beyond diagnosis to miRNA replacement therapy, we asked the clinical trials registry how far that ambition has actually travelled.

## 2. Methods

Full detail, including every search string, is in the repository's methods document and in `data/raw/systematic_review_2026/search_strategy.json`.

### 2.1 Search

PubMed/MEDLINE was searched through the NCBI E-utilities API on 10 September 2026, restricted to publications from 1 January 2015 onwards, with no language restriction. Two arms were run, identical except for the disease term, each combining a microRNA block, a biofluid block (plasma, serum, CSF, blood, exosome, extracellular vesicle) and a diagnostic-accuracy block (ROC, AUC, sensitivity, specificity, diagnostic accuracy, diagnostic value), all in Title/Abstract.

Scopus and Web of Science were not searched, because the analysis environment had no institutional access to them. We state this rather than estimating what those databases would have returned.

### 2.2 Screening and eligibility

Screening was rule-based and is reproducible from the committed script. Records were set aside as secondary literature by PubMed publication type or by self-description, and were flagged as carrying quantitative data when the abstract reported an AUC or both a sensitivity and a specificity.

Full texts were retrieved from PubMed Central for studies passing that filter. An estimate entered the primary pool only if it represented a case-versus-control contrast in a defined AD or PD population. Estimates from composite comparators, within-disease contrasts, prodromal cohorts, genotype-stratified subgroups, mixed neurodegenerative populations, or with unresolvable cohorts were retained in the extraction table but flagged out, each with a stated reason.

### 2.3 Extraction

Regular expressions were used to locate sentences containing accuracy metrics; the values themselves were read from those sentences and transcribed manually. This separation was necessary rather than decorative. In validation, automated capture reversed sensitivity and specificity whenever a sentence stated them in the opposite order, read p-values into specificity fields, and mistook a permutation-test *decrease* in AUC for an AUC. It also captured values that the discussion section attributed to other papers. Each extracted row stores the sentence that supports it, so any reader can check a value against its source.

Duplicate publication was checked by comparing verbatim result sentences. One pair was found (PMIDs 40661348 and 41836608, a preprint and its journal version) and counted once.

### 2.4 Synthesis

Standard errors came from the reported 95% confidence interval where available, and otherwise from Hanley and McNeil's formula using case and control group sizes. As a check on that step, for one study reporting an AUC of 0.75 in 18 cases and 18 controls, the formula returned SE = 0.0822 against the SE of 0.08 the article itself reported.

AUCs were transformed to the logit scale, pooled with the DerSimonian–Laird random-effects estimator and back-transformed. Random effects were specified in advance: these studies differ in biofluid, platform, population and how their cut-offs were derived, so a single common true accuracy is not a plausible assumption. Heterogeneity is reported as Cochran's Q, τ² and I². Small-study effects were assessed with Egger's regression. Subgroups were disease, marker type and biofluid.

Finally, distinct-article mention counts were computed for each miRNA across the screened corpus and correlated with mean reported AUC, and ClinicalTrials.gov was queried for miRNA-directed therapeutic agents.

## 3. Results

### 3.1 Study flow

The two arms returned 168 (AD) and 97 (PD) records, 234 unique after deduplication, with 30 records retrieved by both. Screening set aside 45 records as secondary literature, leaving 189 primary studies, of which 95 reported an AUC or a sensitivity–specificity pair and 55 of those had open-access full text. Forty-five full texts were read, yielding 42 extractable estimates from 26 studies. Twenty-eight met eligibility, and 24 — from 15 independent studies — had an estimable standard error and could be weighted.

The attrition deserves comment. Fewer than one screened record in ten contributed a weighted estimate, and the largest single cause was studies publishing an AUC without the group sizes or confidence interval needed to weight it.

### 3.2 Pooled diagnostic accuracy

| Subgroup | k | Studies | Pooled AUC (95% CI) | I² |
|---|---|---|---|---|
| Overall | 24 | 15 | 0.802 (0.735–0.856) | 93% |
| Alzheimer's disease | 12 | 9 | 0.836 (0.778–0.882) | 76% |
| Parkinson's disease | 12 | 6 | 0.753 (0.621–0.850) | 94% |
| Single miRNA | 16 | 9 | 0.745 (0.699–0.785) | 46% |
| Multi-miRNA panel | 8 | 7 | 0.888 (0.829–0.928) | 85% |
| AD, single miRNA | 6 | 5 | 0.773 (0.732–0.810) | 0% |
| PD, single miRNA | 10 | 4 | 0.716 (0.640–0.781) | 55% |
| Plasma | 5 | 4 | 0.762 (0.642–0.851) | 76% |
| Serum | 10 | 3 | 0.798 (0.693–0.874) | 82% |

A single circulating miRNA pools at 0.745, with the whole confidence interval below 0.80. Panels pool at 0.888, and the two intervals do not overlap.

The AD single-miRNA subgroup is the most informative cell in the table because its heterogeneity is zero. Six estimates from five studies, across serum, serum exosomes, whole blood and neuron-derived extracellular vesicles, and across qPCR and sequencing platforms, converge on 0.773 with no detectable between-study variance. A consistent modest value is a harder result to argue with than an inconsistent one, because it removes the hope that better methods would move the estimate upward.

### 3.3 Attention does not predict performance

Mention counts across the 234-record corpus correlated with mean reported AUC at ρ = −0.11 (p = 0.61) over all single-miRNA estimates, and at ρ = −0.41 (p = 0.14) when restricted to eligible estimates. Neither reaches significance, and with most miRNAs contributing a single study the analysis is underpowered; we report it as exploratory.

The pattern behind the coefficient is nonetheless worth stating. miR-125b was mentioned in 13 corpus articles and returned an AUC of 0.753; miR-146a was mentioned in 11 and returned 0.680, the lowest value among eligible estimates. Meanwhile let-7i, miR-501-3p and miR-128 — mentioned in one, one and two articles respectively — returned 0.835, 0.820 and 0.831.

### 3.4 Small-study effects

Egger's regression was significant in the overall pool, in the PD subgroup, and in the panel subgroup. Together with two structural features of this literature — cut-offs derived in the same sample where they are evaluated, and cohorts frequently under 50 per arm — this points in one direction. Every pooled value here should be read as the optimistic end of its plausible range.

### 3.5 Clinical translation

ClinicalTrials.gov lists 16 registered trials of miRNA-directed therapeutic agents, from five molecules: miravirsen (anti-miR-122, hepatitis C, eight trials, Phase 2); cobomarsen (anti-miR-155, oncology, Phase 2, terminated); MRX34 (miR-34a mimic, oncology, terminated); TargomiRs (miR-16 mimic, Phase 1); and MRG-201/remlarsen (miR-29 mimic, dermatology, Phase 2).

None is in Alzheimer's or Parkinson's disease. Thirteen registered trials mention miRNAs in AD or PD, but eight are observational biomarker studies, two measure miRNAs as an outcome of exercise or rehabilitation, and the three interventional drug trials administer gemfibrozil, an antisense oligonucleotide against tau mRNA, and a TLR9-agonist adjuvant — none of which is a miRNA-directed agent.

## 4. Discussion

The central number of this analysis is 0.745. That is what a single circulating miRNA achieves when the published estimates are weighted and combined, and it sits below the threshold usually treated as a minimum for a standalone diagnostic test. For comparison, plasma phospho-tau assays now in clinical use for AD operate well above 0.90. A blood test whose entire confidence interval falls under 0.80 is not competing in the same category.

We want to be careful about what this does and does not show. It does not show that miRNAs are unimportant in the biology of neurodegeneration; regulatory importance and diagnostic discrimination are separate claims, and evidence for the first is not evidence for the second. What it shows is narrower and more practical: as individual measurements in accessible biofluids, these molecules do not currently separate patients from controls well enough to stand alone.

The zero heterogeneity in the AD single-miRNA subgroup is, to us, the most instructive detail. Heterogeneous literatures invite the hope that a stronger signal is buried under methodological noise. Here, five independent studies using different fluids and different platforms agree closely on a modest value. The limitation looks like a property of the measurement rather than of how it has been performed.

Panels are the constructive finding. At 0.888, with non-overlapping intervals against single markers, combining miRNAs produces a real and quantifiable gain. This aligns with what the biology would predict — miRNAs act as network modulators with individually modest leverage — but it arrives here as a measured effect rather than an inference. Two cautions apply: panel heterogeneity is high, and panels are the marker type most vulnerable to overfitting, since many derive their weights and cut-off in the sample where performance is reported. The panel figure is the one most likely to fall under external validation.

The attention analysis is exploratory and we do not want to overstate it. But it is difficult to look at miR-146a — mentioned in eleven corpus articles, central to the neuroinflammatory account of AD, and returning the lowest AUC among eligible estimates — without concluding that prominence in this literature is earned by mechanistic interest and assay convenience rather than by discriminative performance. Reviews that rank miRNA candidates by how frequently they appear are ranking them by attention. If a reader wants to know which miRNA to measure, that ranking is close to uninformative.

The registry findings complete the picture. After more than a decade of preclinical work on mimics and antagomiRs in neurodegeneration, not one has entered a registered trial in AD or PD. The gap is not that the molecular class is untested in humans: miravirsen reached Phase 2 in hepatitis C, and MRG-201/remlarsen — a miR-29 mimic, precisely the axis most often modelled as an AD therapy — reached Phase 2 for keloid scarring, delivered by intradermal injection. The molecules can be made and dosed. What is missing is a route to the brain. Any computational model that simulates a miRNA mimic as an AD or PD therapy should state that constraint explicitly, alongside the narrow therapeutic window that such models themselves generate when over-suppression drives targets below physiological baseline.

Two recommendations follow for how this work should be done. First, report the number of cases and controls alongside every ROC result. The single largest cause of data loss in this review was studies that published an AUC without the information needed to weight it, which removes them from every future synthesis at no benefit to anyone. Second, evaluate candidate panels in cohorts where the cut-off is fixed in advance, and benchmark them against p-tau217 rather than against no comparator. Absent that, the literature will keep producing estimates near 0.75 and describing them as promising.

## 5. Limitations

Coverage is restricted to PubMed/MEDLINE. Extraction is restricted to PubMed Central open-access full texts, 55 of the 95 eligible primary studies, which may itself select a non-random slice of the field. Twenty-four weighted estimates from 15 studies is a modest evidence base, and some subgroup cells are very small (PD panels, k = 2). Heterogeneity reaches I² = 94%. The attention analysis is underpowered and cannot support causal interpretation. Individual participant data were not available, so bivariate sensitivity–specificity modelling was not performed. Finally, reported accuracy is not prospective clinical accuracy, and the direction of that difference is not neutral.

## 6. Conclusion

Pooled across published studies, single circulating microRNAs discriminate AD and PD patients from controls at an accuracy of about 0.75 — consistently, in the case of AD, and below what a standalone diagnostic test requires. Multi-miRNA panels reach about 0.89 and are where the evidence supports investing. The individual miRNAs that dominate this literature owe their prominence to research attention rather than to measured performance, and no miRNA-directed therapeutic has yet entered a clinical trial for either disease. The molecules remain biologically interesting; the diagnostic case for them, as currently made, is weaker than the volume of publication suggests.

## Data availability

All data, extraction tables with verbatim source quotations, analysis scripts and outputs are available at https://github.com/WesleyCapucho/-Epigen-tica-e-micrornas-em-doen-as-neurodegenerativas

## References

1. Marques TM, Kuiperij HB, Bruinsma IB, et al. MicroRNAs in cerebrospinal fluid as potential biomarkers for Parkinson's disease and multiple system atrophy. *Mol Neurobiol.* 2016. doi:10.1007/s12035-016-0253-0
2. Lusardi TA, Phillips JI, Wiedrick JT, et al. MicroRNAs in human cerebrospinal fluid as biomarkers for Alzheimer's disease. *J Alzheimers Dis.* 2017. doi:10.3233/JAD-160835
3. Hara N, Kikuchi M, Miyashita A, et al. Serum microRNA miR-501-3p as a potential biomarker related to the progression of Alzheimer's disease. *Acta Neuropathol Commun.* 2017. doi:10.1186/s40478-017-0414-z
4. Dos Santos MCT, Barreto-Sanz MA, Correia BRS, et al. miRNA-based signatures in cerebrospinal fluid as potential diagnostic tools for early stage Parkinson's disease. *Oncotarget.* 2018. doi:10.18632/oncotarget.24736
5. Jain G, Stuendl A, Rao P, et al. A combined miRNA-piRNA signature to detect Alzheimer's disease. *Transl Psychiatry.* 2019. doi:10.1038/s41398-019-0579-2
6. Ludwig N, Fehlmann T, Kern F, et al. Machine learning to detect Alzheimer's disease from circulating non-coding RNAs. *Genomics Proteomics Bioinformatics.* 2019. doi:10.1016/j.gpb.2019.09.004
7. Grossi I, Radeghieri A, Paolini L, et al. MicroRNA-34a-5p expression in the plasma and in its extracellular vesicle fractions in subjects with Parkinson's disease. *Int J Mol Med.* 2020. doi:10.3892/ijmm.2020.4806
8. Han L, Tang Y, Bai X, et al. Association of the serum microRNA-29 family with cognitive impairment in Parkinson's disease. *Aging.* 2020. doi:10.18632/aging.103458
9. Hojati Z, Omidi F, Dehbashi M, et al. The highlighted roles of metabolic and cellular response to stress pathways engaged in circulating hsa-miR-494-3p and hsa-miR-661 in Alzheimer's disease. *Iran Biomed J.* 2020. doi:10.29252/ibj.25.1.62
10. Karaglani M, Gourlia K, Tsamardinos I, et al. Accurate blood-based diagnostic biosignatures for Alzheimer's disease via automated machine learning. *J Clin Med.* 2020. doi:10.3390/jcm9093016
11. Oliveira SR, Dionísio PA, Correia Guedes L, et al. Circulating inflammatory miRNAs associated with Parkinson's disease pathophysiology. *Biomolecules.* 2020. doi:10.3390/biom10060945
12. Sandau US, Wiedrick JT, Smith SJ, et al. Performance of validated microRNA biomarkers for Alzheimer's disease in mild cognitive impairment. *J Alzheimers Dis.* 2020. doi:10.3233/JAD-200396
13. Tan YJ, Wong BYX, Vaidyanathan R, et al. Altered cerebrospinal fluid exosomal microRNA levels in young-onset Alzheimer's disease and frontotemporal dementia. *J Alzheimers Dis Rep.* 2021. doi:10.3233/ADR-210311
14. Zhang M, Han W, Xu Y, et al. Serum miR-128 serves as a potential diagnostic biomarker for Alzheimer's disease. *Neuropsychiatr Dis Treat.* 2021. doi:10.2147/NDT.S290925
15. Soto M, Iranzo A, Lahoz S, et al. Serum microRNAs predict isolated rapid eye movement sleep behavior disorder and Lewy body diseases. *Mov Disord.* 2022. doi:10.1002/mds.29171
16. Wu L, Xu Q, Zhou M, et al. Plasma miR-153 and miR-223 levels as potential biomarkers in Parkinson's disease. *Front Neurosci.* 2022. doi:10.3389/fnins.2022.865139
17. Kumar A, Su Y, Sharma M, et al. MicroRNA expression in extracellular vesicles as a novel blood-based biomarker for Alzheimer's disease. *Alzheimers Dement.* 2023. doi:10.1002/alz.13055
18. Rai S, Bharti PS, Singh R, et al. Circulating plasma miR-23b-3p as a biomarker target for idiopathic Parkinson's disease. *Front Neurosci.* 2023. doi:10.3389/fnins.2023.1174951
19. Braunger LJ, Knab F, Gasser T. Using extracellular miRNA signatures to identify patients with LRRK2-related Parkinson's disease. *J Parkinsons Dis.* 2024. doi:10.3233/JPD-230408
20. Duan X, Zheng Q, Liang L, et al. Serum exosomal miRNA-125b and miRNA-451a are potential diagnostic biomarkers for Alzheimer's disease. *Degener Neurol Neuromuscul Dis.* 2024. doi:10.2147/DNND.S444567
21. Li Y, Cao Y, Liu W, et al. Candidate biomarkers of EV-microRNA in detecting REM sleep behavior disorder and Parkinson's disease. *NPJ Parkinsons Dis.* 2024. doi:10.1038/s41531-023-00628-4
22. Omura T, Nishiguchi H, Kaneda H, et al. Plasma expression levels of microRNA-101 are downregulated in patients with Parkinson's disease. *BMC Res Notes.* 2025. doi:10.1186/s13104-025-07604-6
23. Birsan S, Roman-Filip I, Rusu M, et al. Gastric juice miR-106a-5p as a non-invasive biomarker of neuroinflammation and neurodegeneration. *Diseases.* 2026. doi:10.3390/diseases14060187
24. Chen Z, Liu Y, Wang H, et al. Literature-derived serum miRNA signatures associated with cognitive decline in Alzheimer's disease. *Alzheimers Res Ther.* 2026. doi:10.1186/s13195-026-02048-x
25. Qin Q, Xia X, Zhang X, et al. Development of a serum-based microRNA panel for Alzheimer's disease diagnosis. *J Transl Int Med.* 2026. doi:10.1515/jtim-2026-0038
26. Yang SJ, Lin AA, Shen H, et al. Microfluidic nanomagnetically isolated neuron- and astrocyte-derived extracellular vesicles to differentiate Lewy body and Alzheimer's disease. *NPJ Biosens.* 2026. doi:10.1038/s44328-026-00086-x

**Methodological references**

27. DerSimonian R, Laird N. Meta-analysis in clinical trials. *Control Clin Trials.* 1986;7(3):177–188.
28. Hanley JA, McNeil BJ. The meaning and use of the area under a receiver operating characteristic (ROC) curve. *Radiology.* 1982;143(1):29–36.
29. Egger M, Davey Smith G, Schneider M, Minder C. Bias in meta-analysis detected by a simple, graphical test. *BMJ.* 1997;315(7109):629–634.
30. Page MJ, McKenzie JE, Bossuyt PM, et al. The PRISMA 2020 statement. *BMJ.* 2021;372:n71.

*Literature data retrieved from PubMed and PubMed Central (National Library of Medicine, NCBI); trial data from ClinicalTrials.gov (NLM).*
