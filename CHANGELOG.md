# Changelog

🇧🇷 Versão em português: [CHANGELOG.pt-BR.md](CHANGELOG.pt-BR.md)

Each release is archived on Zenodo and carries its own DOI.

## 1.1.0 (2026-10-14)

Archived on Zenodo as [10.5281/zenodo.23368166](https://doi.org/10.5281/zenodo.23368166) (git tag `v1.1.0`).

### Changed

- **Panel-versus-single subgroup test.** The between-subgroup Q test took no account of between-study variance and, with I² of 60% to 80% in the pools, gave p values that were too small. `subgroup_difference_test` (`scripts/05_meta_analysis.py`) now also returns a random-effects contrast: the difference of the two subgroups' pooled logit AUCs, each with its own Paule-Mandel τ² and Hartung-Knapp standard error, referred to a t distribution with Welch-Satterthwaite degrees of freedom (`diff_logit_RE`, `se_RE`, `df_RE`, `p_value_RE`). The Q-based p value stays in the tables. For PD the two give p < 0.0001 and p = 0.041, for the combined set p = 0.0004 and p = 0.073, for AD p = 0.65 and p = 0.69.
- The contrast is carried into `robustness_alternative_analyses.csv`, `robustness_random_selection.csv` and `robustness_validation_split_exploratory.csv` (`scripts/26`) and into Fig. 5b (`robustness_specification.*`, `scripts/33`). Across the 2,000 random selections the random-effects p is below 0.05 in 9% of selections for PD, against 95% for the Q-based p.
- `scripts/08_verify_consistency.py` checks the contrast against the stored pooled estimates (9 new checks, 4309 in all).

### Added

- `scripts/35_manuscript_numbers.py` and `results/tables/manuscript_numbers.json`: every number the Article 1 manuscript quotes, read from the result tables, with the source file of each value. Numbers only; the manuscript text is not part of this repository.
- `CHANGELOG.md` and `CHANGELOG.pt-BR.md`.

### Documentation

- README, methods, data dictionary, PRISMA-DTA checklist and journal-compliance notes brought in line with the current results: retrospective registration on OSF, Paule-Mandel pooling with modified Hartung-Knapp intervals, GRADE steps, I², Egger results, excluded contrasts, bivariate operating point, range of the interval-plausibility ratios.
- The Corrections table has a fourteenth entry (the Q-based subgroup test).
- The supervisor and the unit are recorded from the thesis cover; the decisions on co-authorship, funding and the corresponding e-mail are recorded in the compliance notes.

### Unchanged

- Every pooled estimate, the QUADAS-2 judgements, the GRADE ratings and the bivariate summary are as in 1.0.0.

## 1.0.0 (2026-10-13)

Archived on Zenodo as [10.5281/zenodo.23353780](https://doi.org/10.5281/zenodo.23353780) (git tag `v1.0.0`).

- First archived version: search records (PubMed, Scopus, Web of Science), screening decisions and the recall check; extraction tables with the source sentence for every value and the audit log; QUADAS-2, GRADE and robustness analyses (47 eligible studies, 37 in the primary pools); analysis and figure scripts (`scripts/01` to `33`) and the consistency script (4300 checks); result tables and figures in English and Portuguese.
- Scripts under MIT, data, tables, figures and documentation under CC BY 4.0. The Scopus and Web of Science export files are not distributed; `exports_manifest.csv` lists their record counts and SHA-256 hashes.
