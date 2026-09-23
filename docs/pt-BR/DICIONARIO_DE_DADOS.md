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

## `data/raw/systematic_review_2026/exports/`

As exportações das bases de que esta revisão partiu, arquivadas exatamente como baixadas: `scopus_AD_2026-09-10.csv`, `scopus_PD_2026-09-10.csv`, `wos_AD_2026-09-23.txt`, `wos_PD_2026-09-23.txt`. Scopus e Web of Science exigem sessão institucional autenticada e não podem ser consultadas por API a partir deste projeto, então a exportação é o registro primário do que a busca retornou. Os arquivos da Web of Science são registros completos delimitados por tabulação com as etiquetas de campo de duas letras (`TI`, `AB`, `DI`, `PM`, `PY`, `SO`, `AU`, `DT`, `DE`); o `scripts/09` também aceita os nomes longos de coluna.

## `data/raw/systematic_review_2026/additional_records_*.json`

Um arquivo por braço de base ingerido, nomeado pelo rótulo `--arm`: `AD` e `PD` guardam os braços da Scopus, `AD_wos` e `PD_wos` os da Web of Science. Cada registro traz `Title`, `Abstract`, `DOI`, `PMID`, `Year`, `Journal`, `Authors`, `PublicationTypes`, `Keywords` e `database`. A desduplicação acontece na entrada, contra o corpus do PubMed e contra todo braço já ingerido. Cada base precisa do próprio rótulo: o nome do arquivo vem só do rótulo, então reusar um entre bases substituiria o braço anterior, e o `scripts/09` recusa.

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

## `data/extracted/kinetic_parameters.csv`

Constantes de velocidade, meias-vidas e concentrações usadas pelo `scripts/12`, uma linha por parâmetro por fonte. 67 linhas de 15 fontes primárias.

| Coluna | Tipo | Descrição |
|---|---|---|
| `param_id` | string | Identificador (K001…). O `scripts/12` carrega os parâmetros por esse id, nunca pela posição |
| `kind` | enum | `numeric` (número impresso na fonte), `qualitative_constraint` (afirmação sem número utilizável, ex.: "indetectável"), `declared_gap` (procurado e não encontrado), `derived` (calculado por nós a partir de uma tabela primária) |
| `axis` | enum | `miR-29/BACE1/Abeta`, `miR-7/SNCA/alpha-synuclein`, `both` |
| `parameter` / `symbol` | string | O que o valor é, e o símbolo usado no modelo |
| `value_as_written` | string | O valor exatamente como impresso na fonte. Em `numeric` e `qualitative_constraint`, precisa aparecer dentro de `verbatim_quote` |
| `value_si` | float | O mesmo valor convertido para as unidades do modelo. Vazio em restrições qualitativas e lacunas |
| `unit_si` | enum | `1/hour`, `M`, `M^-1 s^-1`, `molecules per cell`, `uM`, `um^3`, `fold`, `fractional change`, `fractional increase`, `fraction of patients`, `dimensionless` |
| `unit_as_written` | string | Unidade como impressa na fonte |
| `population` / `condition` | texto livre | Quem ou o que foi medido, e em que condição experimental. Constante de velocidade sem condição é rejeitada pelo `scripts/08` |
| `n` | string | Tamanho amostral como reportado |
| `method` | texto livre | Técnica de medida |
| `species` | string | Organismo ou sistema (LCR humano, linhagem celular, neurônios de rato ou camundongo, proteína recombinante in vitro…) |
| `pmid` / `doi` / `first_author` / `year` / `journal` | | Citação da fonte primária |
| `verbatim_quote` | texto livre | **A frase de onde o valor foi lido.** Vazia de propósito nas linhas `derived` e `declared_gap` |
| `source` | string | Onde o texto foi lido (texto completo no PMC, PDF ou tabela suplementar fornecidos pelo autor deste repositório, texto completo no Scite) |
| `note` | texto livre | Conversões, ressalvas e, nas linhas `derived` e `declared_gap`, como o valor foi calculado ou como a busca foi feita |

**Regras de leitura.**
- Uma linha `declared_gap` não traz valor, citação nem frase. Ela registra que um número foi procurado e não encontrado, e onde. O código das EDOs se recusa a carregá-la.
- Uma linha `derived` **não** é número impresso pela fonte. A derivação está em `note`, e o `scripts/08` a recalcula a partir da tabela arquivada em `data/raw/kinetics_2026/`.
- K038 e K039 registram valores de um modelo que o próprio artigo rejeita. Ficam como aviso e não são usados.
- Um valor impresso numa figura ou na tabela de uma figura é registrado com aquela linha ou rótulo como citação, e o `note` diz de que figura foi lido. Um valor que só existe como posição numa curva não é registrado.
- K052 e K054 são a razão de existir o tipo `derived`. Wilhelm et al. reportam α- e β-sinucleína juntas (K052) e, numa nota de rodapé, a razão entre as duas (K053); nenhuma das duas é, sozinha, uma concentração de α-sinucleína. O K054 combina as duas e diz isso, e o `scripts/08` o recalcula. Citar K052 como α-sinucleína superestimaria o valor em duas vezes.

## `data/raw/kinetics_2026/tushev_2018_table_S1.xls`

Tabela Suplementar S1 de Tushev et al. 2018 (Neuron, DOI 10.1016/j.neuron.2018.03.030): 24.435 isoformas de 3'UTR com símbolo do gene, enriquecimento por tipo celular, localização por compartimento e uma coluna `half.life[hours]`, que são os dados processados para os quais a própria declaração de disponibilidade do artigo aponta. O `scripts/08` procura de novo as linhas de SNCA, BACE1 e APP neste arquivo e recalcula a constante de decaimento agrupada da BACE1. Leia com duas ressalvas, ambas registradas nas linhas que o usam: o decaimento foi observado por 16 h, então um quarto das isoformas traz meias-vidas além da janela e as maiores chegam a 18.858 h; e o resumo do artigo para transcrições de neurônio só se reproduz quando se excluem valores acima de cerca de 25 h, enquanto o da glia não se reproduz de forma alguma.

## `data/raw/kinetics_2026/wilhelm_2014_table_S1.xlsx`

Additional Data Table S1 de Wilhelm et al. 2014 (Science, DOI 10.1126/science.1252884): medidas de immunoblot quantitativo de 64 proteínas presinápticas, com porcentagem da proteína total, número de cópias por sinapse (média ± EPM de quatro preparações), concentração molar e notas de rodapé. A legenda está embutida na planilha como imagem. As concentrações foram calculadas pelos autores sobre o volume sináptico menos o volume mitocondrial; o `scripts/08` confirma isso recalculando o volume implicado por cada par de cópias e concentração e comparando com K050 menos K057, lidos da Figura 1C do mesmo artigo.

## `data/raw/kinetics_2026/schwanhausser_2011_supplementary_table.xls`

Tabela suplementar de Schwanhäusser et al. 2011 (Nature, DOI 10.1038/nature10098): meias-vidas de mRNA e proteína, números de cópias e taxas de síntese em escala genômica em fibroblastos NIH3T3 de camundongo, 5028 linhas. Arquivada sem alteração. Os metadados do arquivo indicam última modificação em novembro de 2012; a errata do artigo (DOI 10.1038/nature11848) saiu em fevereiro de 2013, e não foi confirmado se esta é a versão corrigida. Usada só para as medianas genômicas (K040, K041) e para confirmar a ausência de BACE1 e SNCA (K030).

## `data/raw/structures_2026/`

Coordenadas depositadas, sem alteração: `6N4O.pdb` (Argonauta2 humana com miR-122 e alvo, raio X 2,9 Å), `4D8C.cif` (BACE1 com inibidor sulfona cíclica, raio X 2,07 Å), `6CU7.cif` (fibrila de α-sinucleína completa, polimorfo rod, crio-EM), `5OQV.cif` (fibrila de Aβ(1-42), crio-EM 4,0 Å).

## `results/tables/ode_calibrated_results.json`

Saída do `scripts/12`: os parâmetros livres, suas faixas e o valor central de cada um (medido quando existe medida comparável); as constantes ilustrativas de agregação e por que nenhuma fonte as dá; a comparação entre a dose de mimético exigida e a queda de BACE1 medida; o experimento depuração-versus-produção na DA; o tempo para um mimético de miRNA ser eliminado em cada meia-vida medida; o experimento da comporta de pH da α-sinucleína; as cargas de agregado de Aβ42 humanas expressas em múltiplos de M\*; e um resumo da varredura dos parâmetros livres.

## `results/tables/ode_free_parameter_sensitivity.csv`

Uma linha por ponto da varredura dos parâmetros livres: `free_parameter`, `value`, `abeta_AD_over_control`, `verdict` (`AD_above_control`, `AD_at_or_below_control`, `not_evaluable`). Uma execução que falha numericamente é reportada como `not_evaluable`, nunca contada como inversão.

## `results/tables/structure_figure_provenance.json`

Uma entrada por estrutura, lida do arquivo de coordenadas pelo `scripts/13`: título depositado, método, resolução e critério de resolução, DOI e PMID da citação primária, o papel da figura, e verificações calculadas a partir das coordenadas: para 4D8C, os aspartatos catalíticos encontrados tanto pelo motivo de sequência (DTGS, DSGT) quanto pela distância ao inibidor; para as fibrilas, as cadeias de cada protofilamento, o espaçamento entre camadas e a distância entre protofilamentos. Os números de resíduo são os do depósito.

## `data/extracted/quadas2_study_level.csv`

A evidência por trás dos dois domínios QUADAS-2 que a extração de acurácia não responde. Uma linha por estudo agrupado, lida à mão do texto completo no PubMed Central.

| Coluna | Significado |
|---|---|
| `study_id` | PubMed ID, ou DOI para estudos fora do MEDLINE; a mesma chave que o `scripts/05` usa |
| `first_author`, `year`, `disease` | identidade do estudo, para ler a tabela sem consulta externa |
| `fulltext_availability` | `yes`, `no_fulltext_in_pmc`, `no_pmc_record` — qual das três razões se aplica |
| `reference_standard_named` | `yes` / `no`; vazio quando o texto completo não pôde ser lido |
| `reference_standard_quote` | a frase que nomeia os critérios diagnósticos, literal |
| `autopsy_confirmed` | `yes` / `no`; `yes` exige que a citação mencione confirmação neuropatológica |
| `blinding_stated` | `yes` / `not_stated` |
| `blinding_quote` | a frase que declara cegamento ao teste índice, literal |
| `source` | de onde o texto completo foi lido |

Um sinalizador e sua citação precisam concordar: o `scripts/08` falha se um `yes` não traz citação, ou se há citação registrada para um estudo cujo texto completo não era recuperável.

## `results/tables/quadas2_assessment.csv`

Uma linha por estudo avaliado, sete domínios, cada um como veredito mais a razão que o produziu (`..._reason`). Os vereditos são `low`, `high`, `unclear` ou `unrated`. `unclear` significa que a pergunta foi feita e a fonte não responde; `unrated` significa que ela não foi feita. Nenhum domínio está hoje como `unrated`, e o `scripts/08` falha se algum voltar a ficar. Traz também `n_estimates` e `n_estimates_eligible` por estudo.

## `results/tables/quadas2_summary.json`

Contagens por domínio, os estudos avaliados e dois campos narrativos calculados a partir do registro em vez de digitados: `full_text_pass_*` (quantos textos completos eram recuperáveis, quantos nomeiam critérios, quantos confirmam por autópsia, quantos declaram cegamento) e `eligibility_circularity_*` (quanto do veredito uniforme de seleção de pacientes decorre da própria regra de elegibilidade desta revisão, com os contrastes excluídos contados). O `scripts/08` confere os números da prosa contra o registro, para que o texto não sobreviva aos dados.

## `results/tables/bivariate_input_estimates.csv`

As tabelas 2×2 que entram no modelo bivariado, reconstruídas a partir de proporções publicadas: `sensitivity`, `specificity`, `n_cases`, `n_controls`, `continuity_corrected` (se a correção de 0,5 foi aplicada a uma célula vazia) e `in_primary_analysis` (se esta estimativa é a mantida para o estudo).

## `results/tables/bivariate_summary.csv`

Uma linha por análise (primária, uma estimativa por estudo; secundária, toda estimativa elegível): sensibilidade e especificidade sumárias com intervalos de 95%, os desvios-padrão entre estudos `tau_*` e sua correlação `rho_between`, a razão de chances diagnóstica, as duas razões de verossimilhança e `converged`.

## `results/tables/bivariate_model.json`

Os parâmetros ajustados, o autoteste do estimador em 400 estudos simulados (valor verdadeiro, valor ajustado, erro absoluto, tolerância e sinalizador de aprovação para cada um dos cinco parâmetros) e a ressalva sobre a reconstrução, nos dois idiomas. O `scripts/08` falha se qualquer componente do autoteste reportar falha.

## `results/tables/grade_certainty.json`

A avaliação GRADE: os limiares declarados que decidem cada rebaixamento, uma entrada por domínio com seus passos, julgamento e razão declarada, o total de passos, a certeza resultante e o resumo de achados. Mudar um limiar e rodar de novo muda o veredito — é para isso que eles ficam armazenados.

## `results/tables/grade_summary_of_findings.csv`

Uma linha por probabilidade pré-teste: verdadeiros e falsos positivos e negativos esperados a cada 1000 pessoas testadas, mais os valores preditivos resultantes. As contagens não são arredondadas para inteiros, porque arredondar três probabilidades para pessoas inteiras esconde que são esperanças.

## `results/tables/mimic_dosing_feasibility.csv`

Uma linha por espécie e intervalo de dose: `species`, `param_id` (a linha da tabela cinética de onde veio a constante de decaimento), `half_life_hours`, `dosing_interval_hours`, `peak_over_average` e `fraction_of_interval_above_half_peak`. Nenhum parâmetro livre e nenhuma dose suposta entram: a dose se cancela na razão entre pico e média.

## `results/tables/mimic_dosing_feasibility.json`

O mesmo cálculo com as comparações que o usam: a constante de decaimento de cada espécie e seu `param_id`, a comparação de dosagem diária contra a referência de estabilidade mediana (penalidade, intervalo equivalente, fator de estabilização necessário) e a suposição declarada de que o mimético entregue é eliminado na taxa endógena — por isso a saída é um fator de estabilização necessário e não um veredito de viabilidade.

## `results/tables/graphical_abstract_values.json`

Todo número desenhado em `results/figures/graphical_abstract.*.png`, carregado do `ode_calibrated_results.json`, do `mimic_dosing_feasibility.json` e do `kinetic_parameters.csv` no momento do desenho, e não digitado como string separada, mais os `param_id`s em que cada afirmação da figura se apoia. Nada aqui é cálculo novo; é o registro de qual número já verificado foi parar onde.

## `results/tables/mechanism_animations.json`

Os números que cada animação em `results/figures/anim_*.gif` desenha: a razão final Aβ42 DA/controle, os tempos de eliminação das duas espécies, e as razões pico sobre média das duas espécies e a penalidade entre elas. Todo campo é recalculado pelo `scripts/08` a partir do `ode_calibrated_results.json` e do `mimic_dosing_feasibility.json` e exigido a bater, para que o manifesto não possa se afastar das tabelas de onde seus próprios números vieram.

## `results/figures/anim_*.gif`

Três GIFs animados, cada um nos dois idiomas: `anim_ad_monomer` (Aβ42 acumulando até o estado estacionário, sem parâmetro livre), `anim_mimic_washout` (um bolus único de mimético decaindo na meia-vida medida), `anim_dosing_sawtooth` (a penalidade de pico sobre média da dosagem repetida como um ciclo em movimento). Cada um é produzido pelo `scripts/19_mechanism_animations.py`, que importa suas equações do `scripts/12` e do `scripts/17` em vez de rederivá-las. A trajetória da comporta de pH da α-sinucleína não está entre eles, porque sua constante de velocidade em pH ácido é ilustrativa e não medida (K042).

## `results/figures/`

Toda figura existe duas vezes, `<nome>.en.png` e `<nome>.pt-BR.png`. As duas são desenhadas pelo mesmo código, a partir dos mesmos vetores, na mesma execução; só o texto dos rótulos muda.

## `results/figures/structure_story_panel.*.png`

Os quatro renders do `scripts/13` compostos numa figura só, com os fatos que acompanham (PDB id, método, resolução, resíduos da díade catalítica, número e espaçamento dos protofilamentos) tirados do `structure_figure_provenance.json`, não redigitados. Nenhum render novo, nenhuma afirmação nova - só o layout e o agrupamento são novos.

## Convenções

- Proporções são armazenadas como proporções (0,82), não como percentuais (82%).
- Células vazias significam **não declarado na fonte**, nunca zero e nunca imputado.
- Todo valor de enum que aparece nos dados está listado acima; valores não listados indicam erro de dados.
