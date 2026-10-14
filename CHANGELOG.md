# Changelog

🇧🇷 Versão em português: [CHANGELOG.pt-BR.md](CHANGELOG.pt-BR.md)

Each release is archived on Zenodo and carries its own DOI.

## Unreleased

### Corrected

- **Mimic factor and required BACE1 knockdown (`scripts/12`).** The mimic factor that brings the AD monomer pool back to the control pool was found by a grid search with a step of 0.247, and the first grid point past the target, 1.494, was reported. It overshoots, and the BACE1 knockdown computed at that point looked like a range of 30–33% across the repression strength. Both quantities are closed-form. The required knockdown is 1 − 1/R = 29.2%, with R = 1.4126 the AD over control ratio of production over clearance, and it is the same at every value of the free parameters. The mimic factor that delivers it is 1.424 at the midpoint of the repression strength and 1.415 to 1.475 over its declared range (0.1 to 3). Both are now computed in closed form and checked by integrating the ODE (relative error 3 × 10⁻¹⁰). The keys of `ode_calibrated_results.json` changed with them (`required_BACE1_knockdown`, `mimic_fold_to_offset_clearance`, `required_over_measured_knockdown`); `scripts/08`, `scripts/18` and the methods text follow.
- **Free-parameter scan (`scripts/12`).** Two of the 18 runs had been reported as not evaluable because the illustrative aggregation block diverged at the corners k_repress = 0.1 and k_translate = 5. The scan asks about the monomer pool, which that block cannot change, so it now integrates the monomer cascade only. All 18 runs are evaluable and return the AD over control ratio 1.4126 to within 10⁻⁹.
- **Aβ42 reaction orders (`scripts/12`).** The two orders were read the wrong way round: the primary-nucleation order took the secondary-nucleation row (K012) and vice versa. Both rows are 2, so no output changed, but `scripts/08` now checks that K013 is the primary and K012 the secondary order, and that the code reads them that way.
- `scripts/18`: the half-saturation concentration of α-synuclein elongation is labelled m½ on the graphical abstract. It had been labelled M*, the symbol the Aβ42 critical fibril concentration carries everywhere else.

### Changed

- Documents and script text no longer call the selection rule, the subgroups or the interval-plausibility rule pre-specified, because the registration is retrospective.
- The limitation about open-access extraction now says that 40 of the 95 PubMed records with an accuracy statement in the abstract had no open full text and were not extracted, and that 44 further records of that arm contributed no value with no reason logged one by one (README, methods, data dictionary, PRISMA-DTA checklist, journal-compliance notes).

### Added

- `scripts/36_mimic_target_response.py`, `results/tables/mimic_target_response.csv` (330 scenarios) and `mimic_target_response.json`: what a mimic dosed repeatedly does to the protein it targets, with the measured half-life of every step (miRNA, mRNA, protein, and the Aβ42 monomer in the AD arm). The repression strength enters through one number, ρ, the share of the mRNA's decay that the miRNA holds at baseline; the only loss-of-function observation in the parameter table (K065) puts ρ at 0.44 for PD, below the declared scan. The cycle-averaged protein is solved exactly at the periodic steady state, and the dose that reaches the required knockdown is reported with the peak it needs, the dose the steady-state closed form would have asked for, and the swing of the protein. Aβ42 nucleation-rate scaling from the measured reaction orders is in the same file. Six independent verification checks must pass before the table is written; `scripts/08` adds 45 checks on the outputs and on the methods text that quotes them.
- `scripts/35_manuscript_numbers.py` gains the counts an external review of the Article 1 manuscript required (abstract-arm accounting, estimates that could not be weighted, studies whose design could be assessed, AUCs near 0.90, earlier-review study counts, the range of alternative analyses), each with an assert. No existing value changed.

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
