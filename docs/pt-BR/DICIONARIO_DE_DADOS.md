# Dicionário de dados

🇬🇧 English version: [../en/DATA_DICTIONARY.md](../en/DATA_DICTIONARY.md)

---

## `data/extracted/diagnostic_accuracy_extraction.csv`

O conjunto de dados central da meta-análise: uma linha por estimativa de acurácia diagnóstica reportada. Também disponível em `.json`.

| Coluna | Tipo | Descrição |
|---|---|---|
| `record_id` | texto | Identificador interno da linha de extração (E001…) |
| `pmid` | texto | Identificador PubMed do estudo-fonte |
| `doi` | texto | DOI do estudo-fonte |
| `first_author` | texto | Sobrenome e iniciais do primeiro autor |
| `year` | inteiro | Ano de publicação |
| `journal` | texto | Título do periódico |
| `disease` | enum | `AD`, `PD`, `mixed_neurodegenerative` |
| `comparison` | texto livre | Contraste conforme descrito pelo artigo-fonte |
| `comparison_class` | enum | `case_vs_healthy_control`, `differential_diagnosis`, `prodromal_vs_control`, `within_disease` |
| `biofluid` | enum | `serum`, `plasma`, `CSF`, `whole_blood`, `blood`, `serum_exosome`, `CSF_exosome`, `plasma_EV`, `plasma_sEV`, `plasma_neuronal_EV`, `extracellular_miRNA`, `gastric_juice` |
| `marker_type` | enum | `single_miRNA` ou `multi_miRNA_panel` |
| `marker` | texto | Nome do miRNA, ou descrição do painel |
| `cohort_stage` | enum | `discovery`, `training`, `validation`, `single`, `cross-validated`, `unclear` |
| `n_cases` | inteiro | Número de pacientes no contraste (vazio se não declarado) |
| `n_controls` | inteiro | Número de controles no contraste (vazio se não declarado) |
| `auc` | decimal | Área sob a curva ROC, conforme publicada |
| `auc_ci_low` / `auc_ci_high` | decimal | Limites do IC 95%, apenas quando a fonte os reporta |
| `sensitivity` / `specificity` | decimal | Proporções (não percentuais), apenas quando inequívocas na fonte |
| `method` | texto | Plataforma de mensuração (RT-qPCR, small RNA-seq, microarray, ddPCR…) |
| `eligible_primary_pool` | enum | `yes` / `no` — se a linha entra na meta-análise primária |
| `exclusion_reason` | texto livre | Por que uma linha inelegível foi excluída (vazio quando elegível) |
| `note` | texto livre | Ressalvas: IC truncado, tamanho de grupo ausente, publicação duplicada… |
| `verbatim_quote` | texto livre | **A frase exata do artigo-fonte que sustenta os valores desta linha** |
| `source` | texto | De onde veio o texto completo (acesso aberto no PubMed Central) |

**Regra de leitura.** Nenhuma célula numérica deste arquivo deve ser considerada confiável sem sua `verbatim_quote`. Se a citação não sustenta um valor, o valor é um erro e deve ser reportado como tal.

## `data/raw/systematic_review_2026/search_strategy.json`

Registro congelado das buscas: por braço, a query como submetida, a tradução da query feita pelo próprio PubMed, o filtro de data, o número total de registros correspondentes na data da busca e a lista completa de PMIDs recuperados.

## `data/raw/systematic_review_2026/screening_decisions.csv`

Uma linha por registro triado (234 linhas).

| Coluna | Descrição |
|---|---|
| `pmid`, `doi`, `pmcid`, `year`, `journal`, `title` | Identificação do registro |
| `search_arm` | `AD`, `PD` ou `AD+PD` (recuperado pelos dois braços) |
| `article_types` | Tipos de publicação do PubMed |
| `is_review_or_secondary` | Classificado como literatura secundária |
| `abstract_reports_auc` / `_sensitivity` / `_specificity` | Se o resumo declara cada métrica |
| `pmc_fulltext_available` | Texto completo de acesso aberto disponível no PubMed Central |

## `data/raw/systematic_review_2026/mirna_mention_counts.csv`

| Coluna | Descrição |
|---|---|
| `mirna` | Rótulo do miRNA como escrito (normalizado: `hsa-` removido, hifens unificados) |
| `family` | Família após colapsar o sufixo de braço (`miR-146a-5p` → `miR-146a`) |
| `n_articles_mentioning` | Artigos distintos do corpus que mencionam aquele rótulo exato |
| `n_articles_mentioning_family` | Artigos distintos do corpus que mencionam qualquer membro da família |

As contagens são de **artigos distintos**, nunca de ocorrências brutas.

## `data/raw/pubmed/`

Amostra bibliométrica da camada da monografia original, obtida ao vivo da API do NCBI em 10/09/2026. O `manifest.json` registra a query exata, a data de acesso, o número real total de registros correspondentes no PubMed e uma declaração explícita de não fabricação.

## `results/tables/meta_analysis_pooled_auc.csv`

| Coluna | Descrição |
|---|---|
| `subgroup` | Qual subconjunto foi agregado |
| `k_estimates` | Número de estimativas agregadas |
| `n_studies` | Número de estudos independentes que as forneceram |
| `pooled_auc`, `ci_low`, `ci_high` | AUC agregada por efeitos aleatórios, retrotransformada do logito |
| `tau2_logit` | Variância entre estudos na escala logito |
| `I2_percent`, `Q`, `df`, `p_heterogeneity` | Estatísticas de heterogeneidade |
| `egger_intercept`, `egger_p` | Teste de Egger para efeitos de estudos pequenos |

## `results/tables/meta_analysis_input_estimates.csv`

As 24 estimativas agregáveis com o erro-padrão usado em cada uma e, crucialmente, `se_source` — `reported_95CI` quando derivado de intervalo publicado, `Hanley-McNeil` quando calculado a partir dos tamanhos de grupo.

## `results/tables/citation_frequency_vs_auc.csv`

Por família de miRNA: AUC média reportada, número de estudos contribuintes, AUC mínima/máxima e número de artigos do corpus que a mencionam.

## Convenções

- Proporções são armazenadas como proporções (0,82), não como percentuais (82%).
- Células vazias significam **não declarado na fonte**, nunca zero e nunca imputado.
- Todo valor de enum que aparece nos dados está listado acima; valores não listados indicam erro de dados.
