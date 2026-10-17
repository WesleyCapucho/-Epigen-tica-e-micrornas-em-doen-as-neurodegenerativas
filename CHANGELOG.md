# Changelog

🇧🇷 Versão em português: [CHANGELOG.pt-BR.md](CHANGELOG.pt-BR.md)

Each release is archived on Zenodo and carries its own DOI.

## Unreleased

### Added

- `requirements-lock.txt`: the exact versions of the Python packages of the environment that produced the archived results (Python 3.11.17, NumPy 2.4.6, SciPy 1.17.1, pandas 3.0.6, matplotlib 3.11.2); `requirements.txt` keeps the minimum versions.

## 1.2.0 (2026-10-16)

Archived on Zenodo as [10.5281/zenodo.23421847](https://doi.org/10.5281/zenodo.23421847) (git tag `v1.2.0`).

### Corrected

- **Egger test.** `scripts/05` reported the p value of the regression slope, which tests whether the pooled effect is zero, as the Egger p value; it now reports the t test of the intercept on k − 2 degrees of freedom. Every Egger p value changed (AD one estimate per study 0.030 → 0.69, every estimate 0.004 → 0.020; PD 0.55 → 0.016 and 0.017 → 0.002), and the GRADE publication-bias step moved from AD to PD (AD 5 → 4 steps, PD 4 → 5, both still very low). Found by an external review of the manuscript. `results/tables/egger_test_audit.csv` lists both p values for every pool; `scripts/08` recomputes every Egger p by an independent least-squares fit and checks the GRADE step.
- **History of the publication-bias rule.** The p values quoted for the 28 September revision of the rule came from the slope test and mixed the data before and after the second full-text pass; `docs/en/METHODS.md` now gives the intercept test on the data of that commit.
- **Study labels.** Figures 3, 4 and 6 and the supplementary tables gave the year of first online publication, which for seven articles differs from the year of the volume in the reference list; they now give the volume year (`data/extracted/citation_years.csv`). A clipped marker label in the forest plot (a three-miRNA panel shown as two) now shows its ellipsis.

- **Mimic factor and required BACE1 knockdown (`scripts/12`).** The mimic factor that brings the AD monomer pool back to the control pool was found by a grid search with a step of 0.247, and the first grid point past the target, 1.494, was reported. It overshoots, and the BACE1 knockdown computed at that point looked like a range of 30–33% across the repression strength. Both quantities are closed-form. The required knockdown is 1 − 1/R = 29.2%, with R = 1.4126 the AD over control ratio of production over clearance, and it is the same at every value of the free parameters. The mimic factor that delivers it is 1.424 at the midpoint of the repression strength and 1.415 to 1.475 over its declared range (0.1 to 3). Both are now computed in closed form and checked by integrating the ODE (relative error 3 × 10⁻¹⁰). The keys of `ode_calibrated_results.json` changed with them (`required_BACE1_knockdown`, `mimic_fold_to_offset_clearance`, `required_over_measured_knockdown`); `scripts/08`, `scripts/18` and the methods text follow.
- **Free-parameter scan (`scripts/12`).** Two of the 18 runs had been reported as not evaluable because the illustrative aggregation block diverged at the corners k_repress = 0.1 and k_translate = 5. The scan asks about the monomer pool, which that block cannot change, so it now integrates the monomer cascade only. All 18 runs are evaluable and return the AD over control ratio 1.4126 to within 10⁻⁹.
- **Aβ42 reaction orders (`scripts/12`).** The two orders were read the wrong way round: the primary-nucleation order took the secondary-nucleation row (K012) and vice versa. Both rows are 2, so no output changed, but `scripts/08` now checks that K013 is the primary and K012 the secondary order, and that the code reads them that way.
- `scripts/18`: the half-saturation concentration of α-synuclein elongation is labelled m½ on the graphical abstract. It had been labelled M*, the symbol the Aβ42 critical fibril concentration carries everywhere else.

### Changed

- The label of the K058 knockdown was corrected in `scripts/12`, `36`, `37` and `08` and in the methods text: row K058 is the fall in SNCA protein from a construct that carries the coding region and the 3′UTR in HEK-293 cells (western blot), not a 3′UTR reporter. Only the label changed; no value did.
- Documents and script text no longer call the selection rule, the subgroups or the interval-plausibility rule pre-specified, because the registration is retrospective.
- The limitation about open-access extraction now says that 40 of the 95 PubMed records with an accuracy statement in the abstract had no open full text and were not extracted, and that 44 further records of that arm contributed no value with no reason logged one by one (README, methods, data dictionary, PRISMA-DTA checklist, journal-compliance notes).

### Added

- Deeks' funnel-plot asymmetry test on the reconstructed two-by-two tables (`scripts/15`, `results/tables/deeks_funnel_test.csv`); the reconstructed cell counts are now columns of `results/tables/bivariate_input_estimates.csv`.
- `scripts/41_validate_against_metafor.R` and `results/tables/external_validation_metafor.csv`: Paule-Mandel τ², pooled estimates, modified Hartung-Knapp intervals, I², every Egger test and the bivariate model refitted with metafor 4.4.0; 82 comparisons agree.
- Egger intercept and p value for each alternative analysis in `results/tables/robustness_alternative_analyses.csv`.
- The QUADAS-2 index-test judgement for the estimate selected for the pool alone (`rob_index_test_selected_estimate` in `results/tables/quadas2_assessment.csv`).
- `data/extracted/shared_control_groups.csv`: the two reports that cover both diseases use one control group each, so the 4103 participants of the disease pools are 3981 people.

- `scripts/36_mimic_target_response.py`, `results/tables/mimic_target_response.csv` (330 scenarios) and `mimic_target_response.json`: what a mimic dosed repeatedly does to the protein it targets, with the measured half-life of every step (miRNA, mRNA, protein, and the Aβ42 monomer in the AD arm). The repression strength enters through one number, ρ, the decay that the miRNA adds to the mRNA at baseline in units of the mRNA's intrinsic decay. The only loss-of-function observation in the parameter table (K065) sets a floor on it for miR-7 and miR-153 together (ρ at least 0.44), below the declared scan, and says nothing about miR-7 alone; a sweep over ρ from 0.01 to 10⁴ (`mimic_target_rho_sweep.csv`) gives, for each scenario, the smallest daily peak over all ρ. The cycle-averaged protein is solved exactly at the periodic steady state, and the dose that reaches the required knockdown is reported with the peak it needs, the dose the steady-state closed form would have asked for, and the swing of the protein. Aβ42 nucleation-rate scaling from the measured reaction orders is in the same file. Six independent verification checks must pass before the table is written; `scripts/08` adds 45 checks on the outputs and on the methods text that quotes them.
- `scripts/37_manuscript2_numbers.py` and `results/tables/manuscript2_numbers.json`: every number the Article 2 manuscript quotes, read from the tables of `scripts/12`, `17` and `36` and from the parameter table, with asserts behind each sentence that relies on a pattern in the data. It also asserts that the smallest daily peak on the ρ grid bounds the dose at any ρ: in every series the peak rises as ρ falls below its minimum and has converged at the top of the grid (it changes by at most 0.1% over the last decade). Numbers only; the manuscript text is not part of this repository.
- `scripts/38_mechanistic_figures.py` and `results/figures/mech_*.{en,pt-BR}.{png,pdf,eps}`: the seven main-text figures of the mechanistic study (structure of the two models beside four deposited structures; where each row of the parameter table was measured and what it feeds; Alzheimer's arm drawn as tanks whose arrows and levels follow the measured rates; Parkinson's arm; turnover against the dosing intervals; response at the target; design space), in the shared style and fitted to the journal's artwork limits. Every number on them is read at draw time from the tables of `scripts/12`, `17`, `36` and `40`, from `scripts/_provenance.py` and from the parameter table; `scripts/08` adds the artwork checks for the seven stems. The ordinal ramp of Fig. 2 passes the data-visualisation palette validator.
- `scripts/39_structure_renders_article2.py`, `results/figures/structures/a2_*.png` and `results/tables/structure_renders_article2.json`: PyMOL renders of the four deposited structures (6N4O, 4D8C, 5OQV, 6CU7) in the figure palette, with method and resolution read from the entry. Two constructions are recorded and named in the legends: the translucent layer past the last chain of a fibril (an exact superposition of two deposited chains, with rise, rotation, pair count and rms written to the JSON) and the clipping plane through BACE1. Illustration only; no result is read from an image. Needs `pip install pymol-open-source`.
- `scripts/40_mimic_design_space.py`, `results/tables/mimic_design_space.csv` (8,379 points) and `mimic_design_space.json`: the peak of the repressor pool that a target requires over a grid of 49 values of ρ and 19 dosing intervals for nine series, with the solver of `scripts/36`; the longest interval within a peak of 3, 10 and 30 times baseline; the grid reproduces `scripts/36` at 24 h (relative difference 6 × 10⁻¹⁰), the peak never falls as the interval grows, and 615 grid points (all miR-7-like, PD arm) are not reached by any dose up to 10,000 times baseline.
- `scripts/_provenance.py` and `results/tables/parameter_provenance_classes.csv`: the system in which each of the 67 rows was measured (7 classes) and the block of the models it feeds (6 classes), declared as lists and checked against the species, population, condition and method of every row; `scripts/_viz_mech.py`: drawing helpers for those figures. `scripts/37` gains the tokens for the provenance counts, the design space and the structures; `scripts/08` gains checks that the grid is complete and reproduces `scripts/36`, that every render exists and points at an entry with provenance, and that the saved classes equal the classification.
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
