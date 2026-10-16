# EN | Checks the estimators of scripts/05, 15 and the Egger test against the R package metafor
#      (Viechtbauer 2010, J Stat Softw 36(3):1-48), on the very rows the result tables were
#      pooled from. Paule-Mandel tau2, pooled logit AUC and the modified Hartung-Knapp interval
#      (metafor's test = "adhoc", which floors the Hartung-Knapp variance at the Wald one), the
#      DerSimonian-Laird I2, the classical Egger test (regtest, model = "lm") and the bivariate
#      model fitted by maximum likelihood (rma.mv, unstructured between-study covariance). The
#      prediction interval is not compared, because metafor uses t with k - 1 degrees of freedom
#      and this review uses k - 2. Writes results/tables/external_validation_metafor.csv; scripts/08
#      checks it against the current tables. Optional: needs R and metafor.
# PT | Confere os estimadores dos scripts/05 e 15 e o teste de Egger com o pacote R metafor, sobre
#      as mesmas linhas de que as tabelas foram agregadas. Opcional: precisa de R e do metafor.
#
#   Rscript scripts/41_validate_against_metafor.R

suppressMessages(library(metafor))
T <- "results/tables"
sel <- read.csv(file.path(T, "one_estimate_per_study_selection_audit.csv"), stringsAsFactors = FALSE)
inp <- read.csv(file.path(T, "meta_analysis_input_estimates.csv"), stringsAsFactors = FALSE)
prim <- read.csv(file.path(T, "meta_analysis_pooled_auc_primary.csv"), stringsAsFactors = FALSE)
every <- read.csv(file.path(T, "meta_analysis_pooled_auc_sensitivity_every_estimate.csv"), stringsAsFactors = FALSE)
biv <- read.csv(file.path(T, "bivariate_input_estimates.csv"), stringsAsFactors = FALSE)
bsum <- read.csv(file.path(T, "bivariate_summary.csv"), stringsAsFactors = FALSE)
bmod <- jsonlite::fromJSON(file.path(T, "bivariate_model.json"))

filt <- function(d, label, typecol) {
  if (startsWith(label, "AD -")) d <- d[d$disease == "AD", ]
  if (startsWith(label, "PD -")) d <- d[d$disease == "PD", ]
  if (grepl("single miRNA", label)) d <- d[d[[typecol]] == "single_miRNA", ]
  if (grepl("multi-miRNA panel", label)) d <- d[d[[typecol]] == "multi_miRNA_panel", ]
  if (startsWith(label, "Biofluid")) d <- d[d$biofluid == sub(".*- ", "", label), ]
  d
}
logit <- function(p) log(p / (1 - p))
short <- function(s) if (startsWith(s, "Biofluid")) paste0("Biofluid - ", sub(".*- ", "", s)) else sub(" \\|.*", "", s)
out <- list()
add <- function(q, ours, theirs, tol) out[[length(out) + 1]] <<- data.frame(quantity = q, this_review = ours,
  metafor = round(theirs, 6), abs_difference = round(abs(ours - theirs), 6), tolerance = tol)

for (i in seq_len(nrow(prim))) {
  r <- prim[i, ]; d <- filt(sel, r$subgroup, "selected_marker_type")
  if (nrow(d) < 3) next
  pm <- rma(yi = d$y, vi = d$v, method = "PM", test = "adhoc")
  dl <- rma(yi = d$y, vi = d$v, method = "DL")
  eg <- regtest(rma(yi = d$y, vi = d$v, method = "FE"), model = "lm", predictor = "sei")
  lab <- short(r$subgroup)
  add(paste0(lab, ": tau2 (Paule-Mandel)"), r$tau2_PM, pm$tau2, 1e-4)
  add(paste0(lab, ": pooled logit AUC"), logit(r$pooled_auc), as.numeric(pm$b), 1e-3)
  add(paste0(lab, ": mHK lower limit, logit"), logit(r$ci_low_hk), pm$ci.lb, 1e-3)
  add(paste0(lab, ": mHK upper limit, logit"), logit(r$ci_high_hk), pm$ci.ub, 1e-3)
  add(paste0(lab, ": I2 (DerSimonian-Laird), %"), r$I2_percent, dl$I2, 0.05)
  add(paste0(lab, ": Egger p, one estimate per study"), r$egger_p_one_per_study, eg$pval, 1e-4)
}
for (i in seq_len(nrow(every))) {
  r <- every[i, ]; d <- filt(inp, r$subgroup, "marker_type")
  y <- logit(d$auc); se <- d$se_auc / (d$auc * (1 - d$auc))
  eg <- regtest(rma(yi = y, sei = se, method = "FE"), model = "lm", predictor = "sei")
  add(paste0(short(r$subgroup), ": Egger p, every estimate"), r$egger_p, eg$pval, 1e-4)
}
b <- biv[biv$in_primary_analysis %in% c(TRUE, "True"), ]
long <- data.frame(study = rep(b$record_id, 2), outcome = rep(c("sens", "spec"), each = nrow(b)),
                   yi = c(log(b$tp / b$fn), log(b$tn / b$fp)), vi = c(1 / b$tp + 1 / b$fn, 1 / b$tn + 1 / b$fp))
fit <- rma.mv(yi, vi, mods = ~ outcome - 1, random = ~ outcome | study, struct = "UN", data = long, method = "ML")
fp <- bmod$fitted_parameters_primary
add("bivariate: mean logit sensitivity", fp$mu_sens, as.numeric(coef(fit)["outcomesens"]), 1e-3)
add("bivariate: mean logit specificity", fp$mu_spec, as.numeric(coef(fit)["outcomespec"]), 1e-3)
add("bivariate: tau, logit sensitivity", fp$tau_sens, sqrt(fit$tau2[1]), 2e-3)
add("bivariate: tau, logit specificity", fp$tau_spec, sqrt(fit$tau2[2]), 2e-3)
add("bivariate: between-study correlation", fp$rho, fit$rho, 5e-3)
res <- do.call(rbind, out)
res$agrees <- res$abs_difference <= res$tolerance
res$metafor_version <- as.character(packageVersion("metafor"))
res$r_version <- paste(R.version$major, R.version$minor, sep = ".")
write.csv(res, file.path(T, "external_validation_metafor.csv"), row.names = FALSE)
cat(sprintf("%d comparisons, %d agree; largest difference %.2g\n", nrow(res), sum(res$agrees), max(res$abs_difference)))
if (!all(res$agrees)) { print(res[!res$agrees, ]); quit(status = 1) }
