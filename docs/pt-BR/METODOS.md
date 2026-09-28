# Métodos

*Revisão sistemática e meta-análise da acurácia diagnóstica de microRNAs circulantes na doença de Alzheimer e na doença de Parkinson.*

🇬🇧 English version: [../en/METHODS.md](../en/METHODS.md)

---

## 1. Pergunta da revisão

Duas perguntas são endereçadas, uma confirmatória e outra que a monografia de origem levantou sobre o próprio método:

1. **Quão bem os microRNAs circulantes de fato discriminam pacientes com doença de Alzheimer (AD) ou de Parkinson (PD) de controles**, quando as estimativas publicadas são agregadas em vez de apenas listadas?
2. **A frequência com que um miRNA é discutido na literatura tem relação com o quanto ele funciona?** A monografia que originou este repositório reconheceu que frequência bibliométrica e validação experimental catalogada compartilham uma causa comum — a atenção prévia da pesquisa — e, portanto, não são evidências independentes. A acurácia diagnóstica agregada é um critério externo que rompe essa dependência.

Enquadramento PICO: **P** adultos com diagnóstico clínico de AD ou PD; **I** dosagem de um ou mais microRNAs em biofluido acessível; **C** controles saudáveis ou cognitivamente normais; **O** discriminação diagnóstica (AUC, sensibilidade, especificidade).

## 2. Fontes de informação e busca

O PubMed/MEDLINE foi consultado pela API E-utilities do NCBI em **10 de setembro de 2026**, sem restrição de idioma e com filtro de data de publicação a partir de 1º de janeiro de 2015.

Foram executados dois braços de busca, que diferem apenas no termo da doença. Cada um combina um bloco de microRNA, um bloco de biofluido e um bloco de acurácia diagnóstica, todos restritos a Título/Resumo:

```
(microRNA OR miRNA OR microRNAs OR miRNAs)
AND (Alzheimer | Parkinson)
AND (plasma OR serum OR "cerebrospinal fluid" OR CSF OR blood
     OR exosome OR exosomal OR "extracellular vesicle")
AND (ROC OR "area under the curve" OR AUC OR sensitivity
     OR specificity OR "diagnostic accuracy" OR "diagnostic value")
```

Retornos: a busca inicial reportou 168 registros correspondentes para o braço AD, mas apenas **167** puderam de fato ser obtidos e arquivados (um PMID se perdeu por uma falha transitória de busca na API E-utilities e fica excluído de toda contagem posterior); **97 registros** (braço PD); **234 registros únicos** após deduplicação, dos quais **30** foram recuperados pelos dois braços. As strings exatas submetidas, as traduções da query pelo PubMed e os PMIDs recuperados estão em `data/raw/systematic_review_2026/search_strategy.json`; o `scripts/03_systematic_search.py` reexecuta as buscas.

Como o PubMed cresce diariamente, uma reexecução posterior retornará mais registros do que as contagens congeladas acima. Isso é comportamento esperado, não inconsistência: o arquivo de estratégia arquivado é a referência dos números reportados.

**Scopus.** O Scopus foi consultado com a mesma estratégia de dois braços em 10 de setembro de 2026 e os conjuntos de resultados exportados sob autenticação institucional, já que o Scopus não pode ser consultado por API a partir deste ambiente. As exportações estão arquivadas em `data/raw/systematic_review_2026/exports/` e são ingeridas pelo `scripts/09_ingest_scopus_wos.py`, que as normaliza e deduplica contra o corpus do PubMed e contra todo braço já ingerido, por DOI, PubMed ID e título normalizado.

Retornos: **408 registros** (braço AD), dos quais 248 eram novos para a revisão, e **255 registros** (braço PD), dos quais 98 já estavam no corpus do PubMed e 79 já haviam chegado com o braço AD do Scopus — um artigo que nomeia as duas doenças volta nas duas buscas e precisa ser contado uma vez só. O braço PD contribuiu, portanto, com **78** registros novos, e o corpus totaliza **560 registros únicos**.

Esse passo entre braços não é acessório. Sem ele, o braço PD parecia acrescentar 157 registros em vez de 78, porque o mesmo artigo estava sendo contado em dois braços.

**Web of Science.** A Web of Science Core Collection foi consultada em 23 de setembro de 2026 com a mesma estratégia de tópico (`TS=`) nos dois braços, timespan 2015–2026, e exportada em registro completo delimitado por tabulação sob autenticação institucional, porque não pode ser consultada por API a partir deste projeto. O braço DA retornou 187 registros e o braço DP 108; após desduplicação contra PubMed, Scopus e entre si, **27 eram novos**. A data da busca é treze dias posterior à das outras duas bases e é reportada como data própria, não fundida à delas. As exportações estão arquivadas em `data/raw/systematic_review_2026/exports/`.

**O que a terceira base mudou, que na síntese foi nada.** Dos 27 registros novos, 15 são estudos primários e 3 reportam alguma medida de acurácia no resumo. Os três foram julgados contra o PICO e nenhum entrou no pool primário: um mede o RNA longo não codificante BACE1-AS e não um microRNA, um mede córtex pré-frontal post-mortem e não um biofluido circulante (e os próprios autores concluem que ainda é preciso testar em biofluidos periféricos), e o terceiro — o único registro que casa com o PICO em população, biofluido e teste índice — reporta a AUC apenas como a desigualdade "AUC>0,90", não tem DOI nem PubMed ID, e sua revista parou de depositar no PubMed Central em 2015, de modo que nenhum texto completo pôde ser alcançado para confirmar um valor. Um número que não pode ser conferido contra uma frase-fonte não é extraído. Os três ficam registrados na tabela de extração como as linhas E077–E079 com suas razões de exclusão, para que o braço possa ser auditado em vez de aceito por confiança. As estimativas agregadas, o ponto de operação bivariado, a tabela QUADAS-2 e a classificação GRADE são idênticos byte a byte antes e depois do braço da Web of Science.

**Bases não consultadas.** As três bases previstas para esta revisão foram consultadas, de forma simétrica entre as duas doenças. A Embase, que muitas revisões de acurácia diagnóstica acrescentam, não foi consultada, e nenhuma busca de citações para trás ou para frente, literatura cinzenta ou servidor de preprints complementou as três bases. Isso é reportado como limitação no manuscrito.

**Reprodutibilidade do corpus.** Títulos e resumos dos 560 registros estão arquivados em `data/raw/systematic_review_2026/screening_corpus.json` e são reconstruídos pelo `scripts/10_build_screening_corpus.py`. Eles não eram versionados nas versões anteriores, o que impedia regerar as contagens de menção da Seção 6 apenas a partir do repositório. Agora é possível.

## 3. Triagem

A triagem é baseada em regras e reprodutível (`scripts/04_screening.py`). Cada registro foi classificado em dois eixos:

- **Literatura secundária**, se o tipo de publicação no PubMed fosse Review, Systematic Review, Meta-Analysis, Editorial, Comment, Letter, Erratum ou Retraction, ou se o título/resumo se anunciasse como revisão.
- **Porta dados quantitativos de acurácia**, se o resumo declarasse uma AUC, ou declarasse sensibilidade e especificidade juntas.

Resultados, por fonte:

| Fonte | Triados | Secundários | Primários | Reportam acurácia |
|---|---|---|---|---|
| PubMed | 234 | 46 | 188 | 95 |
| Scopus AD (novos) | 248 | 147 | 101 | 20 |
| Scopus PD (novos) | 78 | 30 | 48 | 12 |

Cinquenta e cinco dos estudos primários do PubMed tinham texto completo de acesso aberto no PubMed Central. As decisões por registro estão em `data/raw/systematic_review_2026/screening_decisions.csv`; as contagens são recalculadas para `data/processed/prisma_flow.json`, e não transcritas.

**Um defeito que merece ser declarado.** Uma versão anterior da regra de literatura secundária fechava a alternância com fronteira de palavra após `meta-analys`. Como "meta-analysis" segue com "is", não há fronteira ali e a alternativa nunca disparava, de modo que meta-análises autodeclaradas passavam na triagem como estudos primários. Isso reclassificou um registro do PubMed e não afetou nenhuma estimativa extraída, mas é a razão de as meta-análises prévias diante das quais este trabalho precisa se posicionar terem passado despercebidas até a triagem dos registros do Scopus.

## 4. Extração de dados do texto completo

Os textos completos foram recuperados do PubMed Central para **48 estudos** no braço de acurácia no resumo e para outros 34 estudos na verificação de recall (abaixo). A extração seguiu três regras e depois foi conferida por uma segunda passagem pelo texto completo (abaixo):

**A mineração automatizada localiza candidatos; quem registra os valores é uma pessoa.** Expressões regulares trouxeram à tona cada frase contendo uma métrica de acurácia junto de seu contexto. Essas frases foram então lidas, e os valores transcritos manualmente. Essa divisão de trabalho não é cerimonial: os padrões comprovadamente atribuem sensibilidade ao campo de especificidade quando a frase inverte a ordem, capturam valores de p num campo de especificidade e tratam uma *redução* de AUC em teste de permutação como se fosse uma AUC. Nenhum desses erros sobrevive à leitura da frase, e todos sobreviveriam à captura automática.

**Todo valor guarda a frase que o sustenta.** Cada linha de `data/extracted/diagnostic_accuracy_extraction.csv` carrega a coluna `verbatim_quote`, com o trecho exato da fonte, além de PMID e DOI.

**Valores atribuídos a outros estudos não são extraídos.** Seções de discussão rotineiramente citam AUCs de outros trabalhos ("Han et al. encontraram…", "Wen et al. reportaram…"). Tais frases foram identificadas e excluídas; apenas os resultados próprios de cada estudo foram registrados.

Para cada estimativa foram capturados, quando declarados: miRNA (ou composição do painel), doença, comparação e classe da comparação, biofluido, etapa da coorte (descoberta / treinamento / validação / única), número de casos e de controles, AUC com intervalo de confiança, sensibilidade, especificidade e método de mensuração.

### Segunda passagem pelo texto completo (28 de setembro de 2026)

A primeira extração leu a frase que trazia cada valor de acurácia. Isso não bastou. Uma segunda passagem leu cada um dos 22 textos completos do PubMed Central do início ao fim e conferiu todo número extraído contra o artigo inteiro: de qual coorte vinha a AUC, qual o tamanho dessa coorte, o que foi medido em qual fluido e como os marcadores foram escolhidos. Ela encontrou erros que nenhuma leitura frase a frase poderia ter pegado:

- **Uma coorte de validação perdida.** Li Y et al. 2024 reportam o classificador num conjunto de treino e num conjunto de validação retido; a primeira passagem parou de ler a frase antes dos valores de validação.
- **AUCs atribuídas à coorte errada.** Hara et al. 2017 descobriram o marcador num conjunto confirmado por autópsia, mas reportam a AUC para um conjunto separado, de diagnóstico clínico (36 DA / 22 controles). A primeira passagem registrou os tamanhos de grupo do conjunto de autópsia e atribuiu à estimativa uma confirmação neuropatológica.
- **Biofluido errado.** Sandau et al. 2020 mediram líquido cefalorraquidiano, não plasma. Jain et al. 2019 mediram exossomos de líquido cefalorraquidiano, não sangue, com uma assinatura de três miRNAs e três piRNAs testada contra controles que incluíam pacientes psiquiátricos e neurológicos; o estudo passa a ser inelegível pelas mesmas regras que já excluíam painéis mistos de pequenos RNAs. Hojati et al. 2020 mediram soro por RT-qPCR, não sangue total por microarranjo. Grossi et al. 2020 reportam a AUC para pequenas vesículas extracelulares purificadas do plasma, não para o plasma total.
- **AUCs de partição de teste pareadas com tamanhos de grupo da coorte inteira.** Aguilar et al. 2023 e Dos Santos et al. 2018 reportam AUCs numa partição de teste aleatória cujo tamanho por grupo não é informado. Pela regra de não imputação, essas estimativas não têm EP estimável e saem do pool.
- **Tamanhos de grupo que estavam no artigo mas não na tabela.** Zhang M et al. 2021 (miR-128, 106 controles), Rai et al. 2023 (16/16), Omura et al. 2025 (8/6), Grossi et al. 2020 (15/14) e Marques et al. 2016 (28/28).
- **Dez estimativas que não tinham sido extraídas** (E080 a E089), incluindo as únicas AUCs de diagnóstico diferencial que os estudos elegíveis reportam (DA contra comprometimento cognitivo vascular e contra demência com corpos de Lewy em Qin et al. 2026; DP contra atrofia de múltiplos sistemas em líquido cefalorraquidiano em Marques et al. 2016).

Toda mudança, com o valor antigo, o novo e a frase que a justifica, está em `data/extracted/extraction_audit_log.csv`, e o `scripts/08` reexecuta esse log contra a tabela de extração para que os dois não se afastem. A mesma passagem registrou, para cada estudo elegível (27 na época dessa passagem, 47 após a verificação de recall), padrão de referência, estágio da doença, status de medicação, controle de hemólise, estratégia de normalização, como os marcadores candidatos foram escolhidos e como o modelo foi validado, cada item com a citação da fonte, em `data/extracted/study_design_preanalytics.csv`. Cinco estudos não têm texto completo recuperável, e esses campos ficam marcados como não avaliáveis em vez de adivinhados.

Esta passagem foi feita pelo mesmo revisor único (com assistência de LLM sob supervisão do autor; ver a declaração do manuscrito), não por um segundo revisor independente. Ela reduz erros de transcrição e de atribuição; não substitui a extração dupla independente.

### Verificação de recall (28 de setembro de 2026)

A primeira regra de triagem enviava à leitura de texto completo apenas os estudos primários cujo resumo citava AUC, sensibilidade ou especificidade. A comparação com a lista de estudos de uma meta-análise anterior sobre doença de Parkinson (Zhang et al. 2024) mostrou que esse filtro perdeu estudos cuja análise ROC aparece só no texto completo. Dos 356 estudos primários, 227 não tinham afirmação de acurácia no resumo. O `scripts/30_recall_check.py` rederiva quais deles parecem, pelo título e resumo, estudos caso-controle de microRNAs circulantes na DA ou na DP (90 registros). Trinta e sete dos 90 tinham texto completo no PubMed Central; três não puderam ser recuperados, de modo que 34 foram lidos por inteiro. Dezenove relatos atenderam aos critérios de elegibilidade e forneceram 59 das 162 estimativas extraídas; 11 relatos traziam estatísticas de acurácia que não podiam entrar no pool primário e 4 não traziam nenhuma. Os outros 53 candidatos não têm texto completo aberto e não puderam ser avaliados, o que continua sendo uma fonte de estudos perdidos. As decisões, com a frase em que cada uma se apoia, estão em `data/extracted/recall_check_decisions.csv`.

As estimativas foram lidas dos textos completos em sessões paralelas com o modelo de linguagem, e cada frase citada, valor, tamanho de grupo e classificação foi depois reconferido contra o texto completo por sessões separadas. Essa conferência corrigiu, entre outras coisas, intervalos de confiança impressos como porcentagens (He et al. 2021), intervalos que não contêm a própria AUC (Tong et al. 2022), tamanhos de grupo conflitantes em quatro artigos e rótulos de evidência que a frase citada não sustentava. Shigemizu et al. 2019 fornece os participantes reanalisados como conjunto de dados 2 por Karaglani et al. 2020 (GSE120584); suas estimativas são registradas, mas ficam fora do pool para que os mesmos participantes não sejam contados duas vezes. Dois relatos analisam as duas doenças e contam uma vez por doença (ver o dicionário de dados). Um estudo publicado após a data da busca foi encontrado por uma atualização da busca no PubMed e é analisado apenas como análise de sensibilidade (`scripts/31_post_search_sensitivity.py`).

### Elegibilidade para o pool primário

Uma estimativa entra no pool primário apenas se for um **contraste caso-versus-controle saudável numa população definida de DA ou DP**, medindo **um ou mais miRNAs e nada além disso** no biofluido declarado. Das 251 estimativas extraídas, **117** se qualificaram, de **47 estudos** (23 DA, 24 DP; dois relatos cobrem as duas doenças e contam uma vez por doença). As 134 que não se qualificaram ficam na tabela com um `exclusion_reason` explícito:

| Razão | Exemplo |
|---|---|
| Comparador composto ou diferencial | DA contra DFT *e* controles; DA contra comprometimento cognitivo vascular; DP contra AMS |
| Contraste intradoença | DP com vs sem comprometimento cognitivo |
| População prodrômica | transtorno comportamental do sono REM isolado em vez de DP estabelecida |
| Estratificação por genótipo | portadores de LRRK2 em vez de DP esporádica |
| População mista | "patologia neurodegenerativa" sem desagregação por doença |
| Estimativa instável | AUC = 1,000 por separação perfeita num subgrupo de 6 pacientes |
| Modelo composto | miRNA combinado com variáveis clínicas não-miRNA, com parâmetros de RM ou com um lncRNA, circRNA ou proteína |
| Painel de RNA misto | painel com piRNAs ou pseudogenes de rRNA ao lado de miRNAs |
| Teste índice não é miRNA | um lncRNA, um circRNA, uma assinatura gênica de tecido cerebral ou um gênero do microbioma fecal |

**Publicação duplicada.** Os PMIDs 40661348 e 41836608 reportam a mesma coorte, os mesmos marcadores e as mesmas AUCs (versão preprint e versão de periódico de um mesmo estudo). O par foi detectado por frases de resultado verbatim idênticas e contado uma vez. A segunda passagem também encontrou provável sobreposição de participantes que não é publicação duplicada: Karaglani et al. 2020 reanalisam um conjunto público de sangue total do mesmo grupo cujas coortes anteriores entram em Ludwig et al. 2019. Ludwig et al. não tem estimativa com EP estimável, então a sobreposição não atinge nenhum número agregado, mas fica registrada.

## 5. Síntese estatística

Implementada em `scripts/05_meta_analysis.py` (a agregação), `scripts/_study_selection.py` (a regra de seleção de uma estimativa por estudo, compartilhada com a síntese bivariada da Seção 7) e `scripts/26_robustness_analyses.py` (Seção 5b), usando apenas NumPy e SciPy, para que cada etapa possa ser inspecionada em vez de delegada a um pacote caixa-preta.

**Erros-padrão.** Quando a fonte reportou IC de 95%, EP = (superior − inferior) / (2 × 1,96). Caso contrário, o EP foi calculado por Hanley & McNeil (1982) a partir dos tamanhos dos grupos de casos e controles. Estimativas sem IC e sem tamanhos de grupo não podem ser ponderadas e saem da agregação. **100 das 117** estimativas elegíveis, de **40 estudos independentes**, eram agregáveis.

**Plausibilidade de um intervalo reportado.** Um intervalo reportado tem preferência sobre um reconstruído apenas se puder descrever a incerteza amostral nos tamanhos de grupo declarados. Quando o EP implícito num IC reportado é menor que metade do EP de Hanley-McNeil para a mesma AUC e os mesmos grupos, o intervalo é tratado como descrição de outra coisa (por exemplo, a dispersão de uma estimativa de validação cruzada) e usa-se o EP de Hanley-McNeil. Esta regra foi adicionada depois da segunda passagem, não pré-especificada. Ela muda um estudo: Li Y et al. 2024 reportam 0,916 (IC 95% 0,911 a 0,921) para 21 casos e 25 controles, um intervalo cerca de 18 vezes mais estreito do que a amostragem nesse tamanho permite (razão de EPs 0,056; o intervalo do treino dá 0,049). Toda outra linha com IC e tamanhos de grupo tem razão entre 0,80 e 1,38 (`results/tables/ci_plausibility_check.csv`), então qualquer ponto de corte entre cerca de 0,06 e 0,79 dá a mesma classificação. A Seção 5b reporta toda análise com os intervalos como publicados.

**Escopo: circulante versus líquido cefalorraquidiano.** Quatro estudos elegíveis mediram líquido cefalorraquidiano (Lusardi et al. 2017 e Sandau et al. 2020 na DA; Marques et al. 2016 e Dos Santos et al. 2018 na DP), três deles com estimativa de EP estimável. O LCR é triado, extraído e avaliado por QUADAS-2 junto ao resto do corpus (Seção 6), porque a mesma busca o capturou, mas nunca é agregado com estimativas derivadas de sangue: os critérios de elegibilidade, o título do manuscrito e a pergunta de pesquisa tratam de microRNAs *circulantes*. As estimativas de LCR são reportadas narrativamente em `results/tables/csf_secondary_estimates.csv`. Isso deixa **97 estimativas de 37 estudos circulantes independentes** (18 DA, 19 DP) como a meta-análise primária.

**Identidade do estudo.** Um estudo é identificado pelo PubMed ID quando o tem e pelo DOI caso contrário. Usar só o PMID fundia os estudos publicados fora do MEDLINE num único grupo de PMID vazio, e duas coortes independentes que reportam miR-124 no soro de DP eram contadas como uma. A origem do EP fica registrada por estimativa em `results/tables/meta_analysis_input_estimates.csv`.

*Validação desta etapa:* para o PMID 33129241 (AUC 0,75, 18 casos vs 18 controles), a fórmula de Hanley–McNeil devolve EP = 0,0822, contra EP = 0,08 reportado de forma independente pelo próprio artigo.

**Unidade de análise: uma estimativa por estudo, pré-especificada e cega à AUC.** Vinte e um dos 37 estudos circulantes fornecem mais de uma estimativa qualificada (um fornece onze), e essas estimativas em geral vêm dos mesmos participantes (um microRNA isolado e um painel que o contém, medidos numa coorte), portanto são correlacionadas. Uma versão anterior deste pipeline combinava essas linhas por efeito fixo dentro do estudo; isso ainda supõe independência ao calcular a variância combinada. O pipeline atual seleciona exatamente **uma** estimativa por estudo por uma regra fixada de antemão e cega à própria AUC, implementada uma vez em `scripts/_study_selection.py` e compartilhada pelo pool de AUC e pela síntese bivariada:

1. Preferir uma linha avaliada numa amostra de validação separada (`cohort_stage == "validation"`: partição retida ou segunda coorte) a uma derivada e avaliada na mesma amostra.
2. Dentro do nível remanescente, preferir o painel multi-miRNA do próprio estudo aos seus marcadores isolados componentes.
3. Se ainda empatado, preferir a linha com maior tamanho amostral combinado (casos mais controles).
4. Se ainda empatado, tomar o nome de marcador alfabeticamente primeiro, um desempate puramente nominal.

A etapa 2 favorece painéis por construção sempre que painéis e marcadores isolados são comparados, então a Seção 5b roda tudo de novo sem ela. Toda seleção e o motivo que a decidiu vão para `results/tables/one_estimate_per_study_selection_audit.csv`. Agregar todas as linhas como se independentes fica só como checagem de sensibilidade rotulada (`results/tables/meta_analysis_pooled_auc_sensitivity_every_estimate.csv`).

**Agregação.** As AUCs foram transformadas para a escala logit, com o EP propagado pelo método delta (EP_logit = EP_AUC / [AUC(1 − AUC)]). As linhas uma-por-estudo foram combinadas com o estimador de τ² de Paule & Mandel (1982), que evita o viés para baixo que o de DerSimonian & Laird (1986) tem no *k* pequeno visto aqui, e retransformadas para o relato. Os intervalos de confiança usam o ajuste de Hartung & Knapp (2001) baseado na distribuição *t*, com a modificação de IntHout et al. (2014): o erro-padrão de Hartung-Knapp tem como piso o de Wald, porque o intervalo sem piso pode sair mais estreito que o intervalo padrão de efeitos aleatórios quando a heterogeneidade é pequena. Esse intervalo de Hartung-Knapp modificado (mHK) é o reportado em todo o trabalho. Ele não é chamado de "Hartung-Knapp-Sidik-Jonkman": Sidik & Jonkman (2002) é um estimador de τ² distinto, que esta revisão não usa. Um intervalo de predição de 95% é reportado para toda estimativa agregada com *k* ≥ 3. Efeitos aleatórios foram escolhidos a priori: os estudos diferem em biofluido, plataforma, população e derivação do ponto de corte.

**Doença de Alzheimer e doença de Parkinson são desfechos primários separados**, agregados e avaliados por GRADE cada um por si; a estimativa combinada DA+DP (37 estudos) é um resumo secundário, exploratório.

**Heterogeneidade** é reportada como Q de Cochran com seu valor de p, τ² na escala logit e I² do cálculo de DerSimonian-Laird, para que as estatísticas de heterogeneidade continuem comparáveis entre as análises primária e de sensibilidade.

**Efeitos de estudos pequenos** foram avaliados pela regressão de Egger no pool uma-por-estudo e no pool de toda-estimativa. Com 18 e 19 estudos independentes por doença, heterogeneidade alta e estimativas correlacionadas, o teste é lido como descrição da assimetria do funil, não como teste de viés de publicação; ele reduz a certeza apenas quando é significativo nos dois pools (Seção 8).

**Subgrupos**, pré-especificados: por doença, por tipo de marcador (miRNA isolado vs painel multi-miRNA) e por biofluido quando havia pelo menos três estudos independentes. Os subgrupos de tipo de marcador e de biofluido são construídos filtrando a seleção única uma-por-estudo, nunca reselecionando dentro de um conjunto pré-filtrado de linhas brutas, então os grupos de miRNA isolado e de painel são disjuntos por construção. Isso importa para o teste formal painel versus isolado (Borenstein et al. 2009, cap. 19: Q_entre = Q_todos − Q_isolado − Q_painel, com 1 gl), que pressupõe subgrupos independentes; uma versão anterior deste pipeline deixava um estudo contribuir para os dois grupos e exagerava a diferença na DA (p = 0,005 então, contra p = 0,067 com os grupos disjuntos, sobre o corpus como extraído naquele momento).

### 5b. Análises de robustez

`scripts/26_robustness_analyses.py`, adicionado depois da segunda passagem. Nenhuma substitui a análise primária; cada uma pergunta quanto uma escolha analítica a move.

- **Regra de seleção neutra quanto ao tipo de marcador** (sem a etapa 2 acima): `results/tables/robustness_alternative_analyses.csv`.
- **2.000 seleções aleatórias cegas à AUC**, uma estimativa qualificada por estudo sorteada uniformemente, com semente fixa: a dispersão da AUC agregada e do valor de p painel versus isolado entre seleções que ignoram a AUC (`robustness_random_selection.csv`).
- **Deixar-um-estudo-de-fora por doença** na seleção primária (`robustness_leave_one_out_by_disease.csv`).
- **Intervalos reportados como publicados**, sem a regra de plausibilidade (em `robustness_alternative_analyses.csv`).
- **Auditoria do subgrupo de painéis**: cada estudo do subgrupo de painéis de cada doença, com AUC, intervalo, tamanhos de grupo, origem do EP, peso e a fonte de onde o valor foi lido (`panel_subgroup_audit.csv`).
- **Checagem de rótulos de sensibilidade/especificidade**: se cada sensibilidade publicada é consistente com um inteiro sobre o grupo de casos e cada especificidade sobre o grupo controle, ou só quando trocadas (`sens_spec_label_check.csv`). Wu L et al. 2022 é consistente só com os rótulos trocados, nos dois marcadores; os valores ficam como publicados e o modelo bivariado é reajustado sem esse estudo (`robustness_bivariate_label_check.csv`).
- **Perfil de desenho** dos estudos agregados a partir de `study_design_preanalytics.csv` (`study_design_profile.csv`), e uma divisão exploratória da AUC agregada pelo fato de a estimativa selecionada vir de participantes separados daqueles em que os marcadores foram escolhidos (`robustness_validation_split_exploratory.csv`). Com três a dezesseis estudos por célula, essa divisão é apenas descritiva.

## 6. Risco de viés e aplicabilidade (QUADAS-2)

`scripts/14_quadas2_risk_of_bias.py`. Os 47 estudos elegíveis (Seção 4) foram avaliados com o QUADAS-2 (Whiting et al. 2011): quatro domínios de risco de viés e três de aplicabilidade, incluindo os quatro estudos de líquido cefalorraquidiano que a Seção 5 exclui da AUC agregada. A certeza GRADE da Seção 8, por outro lado, tira os domínios de risco de viés e de evidência indireta apenas dos 37 estudos do pool primário circulante.

**Os julgamentos são derivados por regra, não digitados.** Todo veredito é produzido por uma função que lê um campo registrado e devolve o julgamento com a razão, para que quem discordar possa mudar uma função e rodar de novo a avaliação sobre todos os estudos.

**Evidência por estudo.** Os domínios de padrão de referência e de fluxo precisam de evidência que a extração de acurácia não contém; ela é registrada estudo a estudo em `data/extracted/quadas2_study_level.csv`, com a frase de onde cada resposta saiu. 42 dos 47 estudos têm texto completo recuperável; **30** nomeiam os critérios diagnósticos aplicados; **um** (Yang et al. 2026) define os grupos de DA e controle por neuropatologia; **dois** confirmam a DA com biomarcadores (Qin et al. 2026 por PET amiloide ou razão Aβ42/40 baixa no LCR; Cha et al. 2019 por perfil de Aβ42 e tau no LCR). Cinco estudos declaram que a equipe de laboratório era cega ao diagnóstico, o que diz respeito ao teste índice e não ao padrão de referência. A segunda passagem corrigiu esse registro em três pontos: Hara et al. 2017 tinham recebido uma confirmação neuropatológica que vale só para o conjunto de descoberta, Yang et al. 2026 constavam como não nomeando critério, e Zhang M et al. 2021 (miR-128) nomeiam o NINCDS-ADRDA.

**Por que nomear critérios aceitos não basta para risco baixo.** Na DA e na DP, o padrão de referência prático é o critério clínico, que classifica erroneamente uma fração conhecida dos casos. Um estudo que nomeia critérios aceitos é classificado como *incerto*; só a confirmação neuropatológica ou por biomarcadores limpa o domínio. O resultado é 3 baixo, 32 incerto e 12 alto.

**Teste índice.** Um estudo está em risco alto quando o limiar, os marcadores ou o modelo foram derivados na mesma amostra em que a acurácia foi depois avaliada. A partir da segunda passagem vale uma regra adicional: um estudo cuja AUC vem de uma partição retida continua em risco alto se os marcadores foram escolhidos comparando casos e controles no conjunto inteiro antes da partição (`candidate_selection = same_sample_data_driven` na tabela de desenho), porque os participantes de avaliação informaram a escolha do teste. Isso move Aguilar et al. 2023 e Dos Santos et al. 2018. O resultado é 43 alto e 4 incerto (Hara et al. 2017, Duan et al. 2024 e as duas unidades específicas por doença de Sandau et al. 2026, cujos marcadores foram escolhidos numa amostra de descoberta separada ou por validação cruzada). Nenhum estudo incluído pré-especificou um limiar numérico. A coluna `threshold_source` registra de onde veio a estimativa reportada: 41 estudos derivaram e avaliaram numa mesma amostra, 2 usaram validação cruzada dentro de uma amostra, 4 avaliaram numa amostra separada da de derivação. O rótulo foi renomeado de "externally_validated", que exagerava o que esses quatro estudos fizeram: toda amostra assim veio do mesmo centro ou recrutamento da amostra de derivação.

**Fluxo e tempo é incerto para os 47 estudos.** Nenhum dos textos completos recuperáveis contém fluxograma STARD ou contabilidade equivalente de todo participante recrutado.

**O veredito uniforme de seleção de pacientes é em parte circular, e a saída diz isso.** Todo estudo está em risco alto e preocupação alta para seleção de pacientes porque toda estimativa elegível é um contraste caso-versus-controle saudável, que a regra de elegibilidade exigiu. 68 estimativas de 31 estudos com contraste de diagnóstico diferencial, intradoença ou prodrômico foram excluídas por não casarem com o PICO. O `quadas2_summary.json` traz essa afirmação ao lado das contagens.

## 7. Síntese bivariada de sensibilidade e especificidade

`scripts/15_bivariate_srocc.py`. Os estudos que reportam sensibilidade e especificidade num limiar declarado foram sintetizados com o modelo bivariado de efeitos aleatórios de Reitsma et al. (2005): logit da sensibilidade e logit da especificidade como um par normal bivariado correlacionado, com a covariância intraestudo a partir da tabela 2×2 reconstruída e a covariância entre estudos por máxima verossimilhança. Estudos de LCR ficam de fora.

**O estimador é testado antes de ser usado.** O script primeiro ajusta 400 estudos simulados de parâmetros conhecidos e exige que os cinco sejam recuperados dentro de uma tolerância declarada, ou sai sem gravar resultados.

**As tabelas 2×2 são reconstruídas.** Os artigos-fonte reportam proporções e não contagens, então as células são obtidas multiplicando sensibilidade e especificidade publicadas pelos tamanhos de grupo publicados e arredondando, com correção de continuidade de 0,5 quando uma célula fica vazia. A análise primária usa a mesma seleção uma-por-estudo da Seção 5; uma análise secundária usa toda estimativa elegível.

Análise primária, 19 estudos circulantes (19 estimativas; 8 DA, 11 DP): sensibilidade sumária **0,754** (IC 95% 0,677–0,818), especificidade **0,814** (0,779–0,845), razão de chances diagnóstica 13,4, RV+ 4,06, RV− 0,30. A análise secundária (43 estimativas, os mesmos 19 estudos) dá sensibilidade 0,745 e especificidade 0,796. Excluir Wu L et al. 2022, cujos rótulos parecem trocados (Seção 5b), dá sensibilidade 0,765 e especificidade 0,821 com 18 estudos. Com 19 estudos e cinco parâmetros, os termos entre estudos (τ_sensibilidade 0,762, τ_especificidade 0,246, ρ 0,040) são fracamente identificados e não são interpretados isoladamente. O ponto de operação é o que esta análise sustenta, e ele soa bem pior do que uma AUC agregada perto de 0,8 sugere.

## 8. Certeza da evidência (GRADE)

`scripts/16_grade_certainty.py`. A certeza foi avaliada com o GRADE para acurácia de teste diagnóstico (Schünemann et al. 2020), partindo de *alta* e rebaixando em cinco domínios. Todo limiar que decide um rebaixamento é uma constante nomeada no topo do script e vai para `grade_certainty.json`.

**DA e DP são avaliadas separadamente**, cada uma sobre seu próprio pool primário circulante. Risco de viés e evidência indireta são calculados a partir da tabela QUADAS-2 restrita aos 37 estudos desse pool (18 DA, 19 DP).

| Domínio | Passos DA | Base DA | Passos DP | Base DP |
|---|---|---|---|---|
| Risco de viés | −2 | 18 de 18 estudos em risco alto em pelo menos um domínio QUADAS-2 | −2 | 19 de 19 estudos em risco alto em pelo menos um domínio QUADAS-2 |
| Evidência indireta | −1 | 18 de 18 com preocupação alta de aplicabilidade: caso versus controle saudável, não o diagnóstico diferencial que o clínico enfrenta | −1 | igual à DA |
| Inconsistência | −1 | I² = 78,5% | −1 | I² = 81,1% |
| Imprecisão | 0 | intervalo mHK de 95% com largura 0,08 (0,772–0,852); IP 95% 0,620–0,923 | 0 | intervalo mHK de 95% com largura 0,11 (0,741–0,848), abaixo do limiar de 0,20; IP 95% 0,524–0,936 |
| Viés de publicação | −1 | efeitos de estudos pequenos nos dois pools: Egger p = 0,030 (uma por estudo) e 0,004 (toda estimativa), com 18 estudos | 0 | significativo em um pool apenas: Egger p = 0,55 (uma por estudo) e 0,017 (toda estimativa), com 19 estudos |
| **Total** | **5** | → **muito baixa** | **4** | → **muito baixa** |

**Regra de viés de publicação, revista.** Até a segunda passagem, um teste de Egger significativo no pool de toda-estimativa disparava um rebaixamento automaticamente. Corrigir o intervalo implausível de um estudo levou esse teste de p < 0,0001 na DP e p = 0,15 na DA para p = 0,16 na DP e p = 0,025 na DA: um veredito que troca de doença quando um intervalo é corrigido não é base estável para um julgamento GRADE. A regra dá um passo apenas com pelo menos dez estudos independentes e teste significativo nos dois pools; abaixo de dez estudos, o domínio é "não avaliável por teste". Após a verificação de recall os dois pools têm mais de dez estudos. Os testes da DA são significativos nos dois pools (uma por estudo p = 0,030, toda estimativa p = 0,004) e a DA perde um passo; o teste da DP é significativo apenas no pool de toda estimativa e a DP não perde. Um passo por efeitos de estudos pequenos não é, por si, prova de viés de publicação. Nenhuma classificação mudaria com ou sem ele, já que as duas já são muito baixas.

Risco de viés e evidência indireta remontam ambos ao desenho caso-versus-controle saudável, mas avaliar os dois não é contar duas vezes: risco de viés pergunta se o desenho ameaça a validade interna da estimativa de cada estudo para a própria comparação; evidência indireta pergunta se essa comparação responde à pergunta que o clínico enfrenta. A orientação GRADE para acurácia diagnóstica trata o desenho caso-controle como ameaça às duas coisas (Schünemann et al. 2020, parte 1).

**O resumo de achados é exploratório, combina as doenças e não é a base de nenhuma das classificações.** Aplicando o ponto de operação bivariado da Seção 7 (sensibilidade 0,754, especificidade 0,814) a 1000 pessoas testadas:

| Probabilidade pré-teste | Verdadeiros positivos | Falsos positivos | Falsos negativos | VPP | VPN |
|---|---|---|---|---|---|
| 5% | 38 | 176 | 12 | 0,18 | 0,98 |
| 20% | 151 | 149 | 49 | 0,50 | 0,93 |
| 50% | 377 | 93 | 123 | 0,80 | 0,77 |

Com probabilidade pré-teste de 5%, o teste chama cerca de 214 pessoas de positivas a cada 1000, e 176 delas estão erradas.

## 9. Atenção da literatura versus desempenho medido

`scripts/06_citation_vs_performance.py`. Para cada miRNA, contou-se o número de **artigos distintos** do corpus que o mencionam no título ou resumo, correlacionado (Spearman e Pearson) com a AUC média reportada por miRNA, sobre todas as estimativas de miRNA isolado e restrito às elegíveis para o pool primário.

**Uma correção que mudou a resposta.** Durante duas revisões essas contagens foram calculadas sobre os 234 registros do PubMed enquanto as estimativas de acurácia já vinham do corpus PubMed mais Scopus, então todo marcador que entrou pelo Scopus recebia zero menções por construção. O `scripts/11_attention_finding_audit.py` recalcula a correlação sob cada combinação de entradas (`results/tables/attention_correlation_audit.csv`). O ρ = −0,61 (p = 0,012) reportado antes não sobrevive; na extração atual a correlação é ρ = 0,00 (p = 0,97) entre 84 miRNAs e ρ = −0,16 (p = 0,23) entre os 59 com estimativa elegível. O achado está retirado. Sufixos de braço (-3p/-5p) são colapsados no nível da família, e um artigo que cita "miR-125b" e "miR-125b-5p" conta uma vez.

Esta análise é **exploratória**: a maioria dos miRNAs contribui com um único estudo, e um resultado não significativo não é evidência de ausência de associação.

## 10. O que este desenho não é capaz de entregar

- Ele mede acurácia **reportada**, não acurácia em uso clínico prospectivo. Nenhum estudo incluído pré-especificou o limiar, então sensibilidade e especificidade reportadas são otimistas. A AUC independe do limiar, então a escolha do limiar sozinha não infla a AUC; o que pode inflá-la é a escolha de quais marcadores foram testados e reportados, qual combinação foi mantida e se os participantes de avaliação informaram essas escolhas. Só um estudo agregado (Qin et al. 2026) avaliou um modelo travado de antemão numa coorte independente, e mesmo essa coorte veio do mesmo centro.
- A restrição a textos completos de acesso aberto no PubMed Central e a resumos pode selecionar um subconjunto não aleatório da literatura. Cinco estudos elegíveis (dois deles no subgrupo de painéis da DP) são conhecidos só pelo resumo, e seus campos de desenho e pré-analítica não podem ser avaliados.
- O relato pré-analítico é escasso: entre os 37 estudos agregados, 4 mediram hemólise e excluíram amostras afetadas, 5 excluíram amostras hemolisadas sem declarar o método, 7 descrevem manejo voltado a evitá-la e 19 não a mencionam (2 não avaliáveis); o status de medicação não é reportado por 22. A tabela de desenho registra essas lacunas; não pode preenchê-las.
- Estimativas de um mesmo estudo são correlacionadas. A seleção uma-por-estudo remove as linhas correlacionadas antes de agregar, em vez de fazer a média delas; não modela a correlação residual com estrutura multinível ou de variância robusta. A Seção 5b mostra quanto a resposta se move sob outras seleções.
- O teste de Egger tem pouco poder com heterogeneidade deste tamanho e é lido como descrição de assimetria, não como teste de viés de publicação.
- Não havia dados individuais de participantes. A síntese bivariada repousa sobre tabelas 2×2 reconstruídas a partir de proporções e tamanhos de grupo publicados e cobre os 19 estudos circulantes que declaram um limiar, e não os 37 agregados por AUC.
- Triagem, extração e avaliação de risco de viés foram feitas por um único revisor com assistência de modelo de linguagem e reconferidas por uma segunda sessão de leitura do mesmo modelo, não por dois revisores humanos independentes; uma segunda revisão humana independente está planejada (`scripts/29_second_reviewer_packet.py`).
- A verificação de recall só pôde ler candidatos com texto completo aberto; 53 candidatos não puderam ser avaliados, e Embase, busca em citações e uma busca final sincronizada no Scopus e na Web of Science não foram feitas.

## 11. Camada mecanística: modelos EDO e figuras estruturais

Esta camada pergunta algo mais estreito que a meta-análise, e deve ser lida assim. Ela não testa se um miRNA funciona como biomarcador. Pergunta o que a cinética medida de cada eixo permite, e onde uma afirmação sobre eles vai além dos números que existem.

**De onde vêm os parâmetros.** Toda taxa, meia-vida e concentração usada pelo `scripts/12_ode_models_calibrated.py` é carregada por identificador de `data/extracted/kinetic_parameters.csv` (67 linhas, 15 fontes primárias). Os valores foram lidos em textos completos ou arquivos suplementares, nunca em resumos ou citações secundárias, e cada linha numérica guarda a frase de onde veio. A tabela separa quatro tipos de linha: números medidos, restrições qualitativas (resultado afirmado sem número utilizável, como nucleação indetectável em pH neutro), lacunas declaradas e valores derivados por nós de uma tabela primária. O carregador recusa tudo que não seja número medido, então uma lacuna não pode ser preenchida em silêncio.

**O que é medido e o que não é.** Produção e depuração de Aβ42 vêm de cinética com marcação por isótopo estável no LCR humano (Mawuenyega et al. 2010, DOI 10.1126/science.1197623). Expoentes de agregação e a concentração crítica de fibrila vêm de Cohen et al. 2013 (DOI 10.1073/pnas.1218402110), e as cargas de Aβ42 no cérebro humano, da Tabela S2 desse artigo. Alongamento da α-sinucleína e sua dependência de pH vêm de Buell et al. 2014 (DOI 10.1073/pnas.1315346111). Meias-vidas de miRNA vêm de Zhang et al. 2011, Gantier et al. 2011, Kingston e Bartel 2019 e Kleaveland et al. 2018, e a renovação de proteínas, de Li et al. 2004, Liu et al. 2019 e Fornasiero et al. 2018. Constantes de agregação que nenhuma fonte dá como número (nucleação e alongamento do Aβ42, nucleação da α-sinucleína em pH ácido) ficam fixadas em valores **ilustrativos** declarados, listados com seus motivos na saída; nenhum achado reportado depende delas. Outras duas grandezas nunca foram medidas para esses genes e ficam **livres**: a força da repressão pelo miRNA e a taxa de tradução. Cada uma é varrida numa faixa declarada, em grade geométrica; nenhuma é ajustada para chegar a um resultado.

O decaimento de mRNA era um terceiro parâmetro livre e não é mais. Tushev et al. 2018 o reportam por isoforma de 3'UTR em neurônios hipocampais de rato em cultura: o SNCA tem uma isoforma, de 6,53 h (K066), e a BACE1 tem cinco, com meias-vidas de 2,8 a 23,9 h (K067). Um conjunto de isoformas não decai com a média das meias-vidas, então a taxa da BACE1 é a média ponderada das **constantes de velocidade**, 0,0456 h⁻¹, meia-vida efetiva de 15,2 h (K068); a média das meias-vidas daria 17,4 h, que é a grandeza errada. Ler essa tabela trouxe duas ressalvas. O decaimento foi observado por 16 h, então a meia-vida de 51,4 h do APP (K069) é extrapolação e fica registrada com aviso, sem ser usada. E o resumo do próprio artigo para transcrições de neurônio só se reproduz da tabela quando se excluem meias-vidas acima de cerca de 25 h (mediana 7,394 h contra os 7,38 impressos), enquanto o resumo da glia não se reproduz com nenhum filtro testado — por isso K044 é citado como impresso e nunca recalculado.

**Experimentos rodados.** (i) O braço da DA compara um déficit de depuração de 30% com a diferença de produção medida de 1,5%, e acha a dose de mimético de miR-29 que compensaria o déficit de depuração baixando a BACE1. (ii) Eliminação de mimético em dose única: o tempo para um bolus de 10x voltar a menos de 10% do basal em cada meia-vida medida. (iii) Cargas de Aβ42 no cérebro humano expressas em múltiplos da concentração crítica acima da qual a nucleação secundária domina. (iv) O braço da α-sinucleína com nucleação desligada em pH neutro, onde Buell et al. a acharam indetectável (K011), e ligada abaixo de pH 6, onde relatam que a nucleação secundária "aumenta drasticamente" (K042). A fonte dá a direção dessa chave, não o tamanho, então a constante de velocidade em pH ácido é varrida em quatro ordens de grandeza; a razão no número de fibrilas vai então de cerca de 500 a cerca de 14.000, e só a direção é reportada como resultado. (v) A dose de miR-29 que o experimento de depuração exige, posta ao lado de um efeito medido: Hébert et al. 2008 relatam cerca de 50% de queda da BACE1 com transfecção de miR-29a/b-1 em células SK-N-SH (K047). No estado estacionário o nível de BACE1 é analítico no fator do mimético, então tanto a queda produzida pela dose exigida quanto a dose que reproduziria os 50% medidos são calculadas em forma fechada nas faixas declaradas dos dois parâmetros livres de que dependem. (vi) Dois cálculos que não usam nenhum parâmetro livre, porque combinam grandezas medidas diretamente. A concentração de α-sinucleína no botão presináptico, 21,6 µM (derivada do número combinado de sinucleína e da razão medida α:β de 0,98:1, tabela S1 de Wilhelm et al. 2014), é posta sobre a curva medida de saturação da elongação, cuja concentração de meia-saturação é 46–50 µM (Buell et al. 2014): a proteína fica em 30–32% da taxa máxima de elongação, abaixo da meia-saturação, onde uma queda de 1% na concentração compra 0,68–0,70% de queda na taxa. A mesma curva então leva uma queda medida até uma taxa: o miR-7 baixa a α-sinucleína em 30% num repórter de 3'UTR e o miR-7 com o miR-153 baixa a α-sinucleína endógena em 43% em neurônios corticais de rato (Doxakis 2010), o que na curva de saturação vira 23% e 34% de elongação mais lenta — menos que proporcional, porque a curva satura. À parte, BACE1 e APP são contados na mesma preparação, 116 contra 6284 cópias por botão. Os dois atravessam sistemas — constante de saturação in vitro contra sinaptossomo de rato — e são reportados como afirmações de regime e estequiometria, não de taxa. (vii) Uma varredura dos parâmetros livres, com cada execução classificada como DA acima do controle, igual ou abaixo, ou não avaliável. Uma execução que falha numericamente é reportada como não avaliável, nunca contada como inversão. A integração usa LSODA (`scipy.integrate.solve_ivp`, rtol 1e-8, atol 1e-10).

**O que os modelos podem e não podem afirmar.** A razão de monômero DA/controle (1,41) é igual à razão entre produção e depuração medida por Mawuenyega et al. e não depende de nenhum parâmetro livre. O modelo reescreve essa medida; não a prevê. O valor dos modelos está em outro lugar: mostram que os parálogos de miR-29 decaem em ritmos diferentes (7 h e 10,6 h, e um relatado como estável) e não podem ser tratados como uma espécie só, que uma dose única de mimético de miR-7 voltaria para perto do basal em 11 a 32 horas, contra cerca de 9 dias para um miRNA típico, que a queda de BACE1 necessária para compensar o déficit de depuração medido é de 30–33% em toda a grade de parâmetros livres e portanto menor que os cerca de 50% já alcançados em células, que uma queda medida de α-sinucleína pelo miR-7 se traduz em 23–34% de elongação de fibrila mais lenta, atravessando três medidas independentes e nenhum parâmetro livre, e que as constantes de velocidade do Aβ42 necessárias para ir além não podem ser separadas com os dados publicados (linha K037).

**O que a dosagem repetida custa a um mimético de renovação rápida.** O `scripts/17_mimic_dosing_feasibility.py` faz uma pergunta que o cálculo de washout levanta mas não responde: se um mimético precisa ser dado repetidamente e não uma vez só, quanto custa a meia-vida medida? No estado estacionário sob dosagem repetida de uma espécie eliminada com constante de primeira ordem *d* no intervalo *T*, a razão entre pico e média é *dT* / (1 − e^(−*dT*)). A dose se cancela, então o cálculo não tem nenhum parâmetro livre; só entram as constantes de decaimento medidas, carregadas por identificador da tabela cinética.

Dosado uma vez por dia, um mimético de miR-7 que se renove como o miR-7 endógeno (meia-vida 1,7 h, K020) precisa atingir um pico de **9,79×** o nível médio, contra **1,26×** para um miRNA de estabilidade mediana (34 h, K016) — uma penalidade de **7,7 vezes** no pico necessário para sustentar a mesma média. Ele passa **7,1%** de cada dia acima da metade do próprio pico. Para ser dosado diariamente nos termos de que um miRNA comum desfruta, precisaria de cerca de **20 vezes** de estabilização (1,7 h → 34 h); na meia-vida medida, o intervalo equivalente é de **1,2 h**. Com a meia-vida de miR-7 no limite superior (5 h, K021) a exigência cai para 6,8 vezes, e para os parálogos de miR-29 para 4,9 (miR-29b) e 3,2 (miR-29c). O resultado é enunciado como fator de estabilização necessário e não como veredito, porque um mimético quimicamente estabilizado, por construção, não é eliminado na taxa endógena; é uma meta de projeto fixada pelas medidas, e é a quantidade que uma química de entrega precisa superar.

**Um graphical abstract a partir dos mesmos números.** O `scripts/18_graphical_abstract.py` desenha uma figura esquemática única cobrindo os dois eixos, para quem quer o mecanismo antes da seção de resultados. Todo número nela - a razão DA/controle, a estequiometria BACE1:APP, a queda necessária, a desaceleração da elongação, a penalidade de dosagem - é carregado no momento do desenho dos mesmos arquivos JSON e CSV que o `scripts/08` já confere, e um manifesto (`results/tables/graphical_abstract_values.json`) registra o que foi desenhado. O encarte do Argonauta2 reaproveita o próprio render do `scripts/13` (PDB 6N4O), em vez de um segundo desenho, não verificado, da mesma molécula; como essa estrutura traz o AGO2 humano carregado com miR-122, e não miR-29 ou miR-7, a legenda diz isso em vez de dar a entender outra coisa.

**Animando as mesmas simulações.** O `scripts/19_mechanism_animations.py` produz três GIFs, e reaproveita em vez de rederivar: importa os lados-direitos de EDO e as constantes medidas diretamente do `scripts/12`, e a fórmula fechada de dosagem do `scripts/17`, para que uma animação não possa calcular um número diferente do que já foi conferido. (i) O monômero de Aβ42 acumulando até seu novo estado estacionário, controle versus DA — sem parâmetro livre, já que produção e depuração são medidas. (ii) Um bolus único de mimético de 10× se eliminando na meia-vida medida, miR-7 contra um miRNA de estabilidade mediana. (iii) O dente de serra da dosagem repetida: concentração relativa à própria média, ao longo de quatro doses diárias, para as mesmas duas espécies, de modo que a altura do pico lida direto no eixo é a penalidade de pico sobre média. O último quadro de cada GIF é escrito em `results/tables/mechanism_animations.json`, e o `scripts/08` o confere contra o `ode_calibrated_results.json` e o `mimic_dosing_feasibility.json`, em vez de confiar que a animação e a figura estática concordam. O crescimento de fibrila da comporta de pH da α-sinucleína deliberadamente não é animado: sua constante de velocidade em pH ácido é ilustrativa (K042), e animá-la poria uma velocidade específica na tela para uma grandeza que este projeto reporta só como direção.

**Figuras estruturais.** O `scripts/13_structure_figures.py` renderiza quatro estruturas depositadas com o PyMOL: Argonauta2 humana com guia e alvo (6N4O), BACE1 com inibidor ligado (4D8C), uma fibrila de α-sinucleína completa (6CU7) e uma fibrila de Aβ(1-42) (5OQV). Título, método, resolução e citação primária são lidos de cada arquivo, e o script para se o título não bater com a molécula que a figura diz mostrar. Os aspartatos catalíticos da BACE1 são encontrados duas vezes, pelo motivo de sequência e pela distância ao inibidor, e precisam concordar. Os protofilamentos das fibrilas são atribuídos a partir das coordenadas, como cadeias empilhadas no espaçamento cross-β. As figuras ilustram mecanismo; não são resultado.

**Um painel composto, não quatro imagens soltas.** O `scripts/20_structure_story_panel.py` organiza quatro dos próprios PNGs do `scripts/13` numa figura só, com legendas inteiramente tiradas de `results/tables/structure_figure_provenance.json` - nenhuma sessão do PyMOL é reaberta e nenhuma afirmação nova é feita. Os painéis ficam agrupados pelo eixo a que pertencem, com uma barra de cor (azul para o eixo de Alzheimer, laranja para o de Parkinson, cinza para o que os dois eixos compartilham), e não encadeados por setas: a BACE1 não vira estruturalmente a fibrila de Aβ, e nenhuma seta afirma isso.

## 12. Figuras em dois idiomas

Toda figura em `results/figures/` é emitida duas vezes, uma em inglês e outra em português do Brasil, como `<nome>.en.png` e `<nome>.pt-BR.png`. As duas versões saem do mesmo caminho de código, na mesma execução, dos mesmos vetores: o `scripts/_bilingual.py` expõe a lista de idiomas, um seletor `t(lang, en, pt)` para o texto dos rótulos e um construtor de caminho, e cada função de plotagem é chamada uma vez por idioma. Só as palavras são traduzidas. Números, limites de eixo, posições de marcação e os próprios dados são idênticos por construção, porque são calculados antes de o laço de idioma começar e não passam pelo tradutor — um par de figuras não pode discordar sobre um valor sem que o código que as desenhou tenha mudado.

## Referências dos métodos

- DerSimonian R, Laird N. Meta-analysis in clinical trials. *Control Clin Trials.* 1986;7(3):177–188.
- Paule RC, Mandel J. Consensus values and weighting factors. *J Res Natl Bur Stand.* 1982;87(5):377–385.
- Hartung J, Knapp G. On tests of the overall treatment effect in meta-analysis with normally distributed responses. *Stat Med.* 2001;20(12):1771–1782.
- IntHout J, Ioannidis JPA, Borm GF. The Hartung-Knapp-Sidik-Jonkman method for random effects meta-analysis is straightforward and considerably outperforms the standard DerSimonian-Laird method. *BMC Med Res Methodol.* 2014;14:25.
- Borenstein M, Hedges LV, Higgins JPT, Rothstein HR. *Introduction to Meta-Analysis.* Chichester: John Wiley & Sons; 2009.
- Hanley JA, McNeil BJ. The meaning and use of the area under a receiver operating characteristic (ROC) curve. *Radiology.* 1982;143(1):29–36.
- Egger M, Davey Smith G, Schneider M, Minder C. Bias in meta-analysis detected by a simple, graphical test. *BMJ.* 1997;315(7109):629–634.
- Page MJ, McKenzie JE, Bossuyt PM, et al. The PRISMA 2020 statement: an updated guideline for reporting systematic reviews. *BMJ.* 2021;372:n71.
- Whiting PF, Rutjes AWS, Westwood ME, et al. QUADAS-2: a revised tool for the quality assessment of diagnostic accuracy studies. *Ann Intern Med.* 2011;155(8):529–536.
- Reitsma JB, Glas AS, Rutjes AWS, Scholten RJPM, Bossuyt PM, Zwinderman AH. Bivariate analysis of sensitivity and specificity produces informative summary measures in diagnostic reviews. *J Clin Epidemiol.* 2005;58(10):982–990.
- Schünemann HJ, Mustafa RA, Brozek J, et al. GRADE guidelines: 21 part 1 and part 2. Test accuracy. *J Clin Epidemiol.* 2020;122:129–141 e 142–152.
- McInnes MDF, Moher D, Thombs BD, et al. Preferred Reporting Items for a Systematic Review and Meta-analysis of Diagnostic Test Accuracy Studies: the PRISMA-DTA statement. *JAMA.* 2018;319(4):388–396.
