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

Retornos: **168 registros** (braço AD) e **97 registros** (braço PD); **234 registros únicos** após deduplicação, dos quais **30** foram recuperados pelos dois braços. As strings exatas submetidas, as traduções da query pelo PubMed e os PMIDs recuperados estão em `data/raw/systematic_review_2026/search_strategy.json`; o `scripts/03_systematic_search.py` reexecuta as buscas.

Como o PubMed cresce diariamente, uma reexecução posterior retornará mais registros do que as contagens congeladas acima. Isso é comportamento esperado, não inconsistência: o arquivo de estratégia arquivado é a referência dos números reportados.

**Scopus.** O Scopus foi consultado com a mesma estratégia de dois braços em 10 de setembro de 2026 e os conjuntos de resultados exportados sob autenticação institucional, já que o Scopus não pode ser consultado por API a partir deste ambiente. As exportações estão arquivadas em `data/raw/systematic_review_2026/exports/` e são ingeridas pelo `scripts/09_ingest_scopus_wos.py`, que as normaliza e deduplica contra o corpus do PubMed e contra todo braço já ingerido, por DOI, PubMed ID e título normalizado.

Retornos: **408 registros** (braço AD), dos quais 248 eram novos para a revisão, e **255 registros** (braço PD), dos quais 98 já estavam no corpus do PubMed e 79 já haviam chegado com o braço AD do Scopus — um artigo que nomeia as duas doenças volta nas duas buscas e precisa ser contado uma vez só. O braço PD contribuiu, portanto, com **78** registros novos, e o corpus totaliza **560 registros únicos**.

Esse passo entre braços não é acessório. Sem ele, o braço PD parecia acrescentar 157 registros em vez de 78, porque o mesmo artigo estava sendo contado em dois braços.

**Web of Science.** A Web of Science Core Collection foi consultada em 23 de setembro de 2026 com a mesma estratégia de tópico (`TS=`) nos dois braços, timespan 2015–2026, e exportada em registro completo delimitado por tabulação sob autenticação institucional, porque não pode ser consultada por API a partir deste projeto. O braço DA retornou 187 registros e o braço DP 108; após desduplicação contra PubMed, Scopus e entre si, **27 eram novos**. A data da busca é treze dias posterior à das outras duas bases e é reportada como data própria, não fundida à delas. As exportações estão arquivadas em `data/raw/systematic_review_2026/exports/`.

**O que a terceira base mudou, que na síntese foi nada.** Dos 27 registros novos, 15 são estudos primários e 3 reportam alguma medida de acurácia no resumo. Os três foram julgados contra o PICO e nenhum entrou no pool primário: um mede o RNA longo não codificante BACE1-AS e não um microRNA, um mede córtex pré-frontal post-mortem e não um biofluido circulante (e os próprios autores concluem que ainda é preciso testar em biofluidos periféricos), e o terceiro — o único registro que casa com o PICO em população, biofluido e teste índice — reporta a AUC apenas como a desigualdade "AUC>0,90", não tem DOI nem PubMed ID, e sua revista parou de depositar no PubMed Central em 2015, de modo que nenhum texto completo pôde ser alcançado para confirmar um valor. Um número que não pode ser conferido contra uma frase-fonte não é extraído. Os três ficam registrados na tabela de extração como as linhas E077–E079 com suas razões de exclusão, para que o braço possa ser auditado em vez de aceito por confiança. As estimativas agregadas, o ponto de operação bivariado, a tabela QUADAS-2 e a classificação GRADE são idênticos byte a byte antes e depois do braço da Web of Science.

**Bases não consultadas.** Nenhuma. As três bases previstas para esta revisão já foram consultadas. A cobertura segue simétrica entre as duas doenças.

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

Os textos completos foram recuperados do PubMed Central para **47 estudos**. A extração seguiu três regras:

**A mineração automatizada localiza candidatos; quem registra os valores é uma pessoa.** Expressões regulares trouxeram à tona cada frase contendo uma métrica de acurácia junto de seu contexto. Essas frases foram então lidas, e os valores transcritos manualmente. Essa divisão de trabalho não é cerimonial: os padrões comprovadamente atribuem sensibilidade ao campo de especificidade quando a frase inverte a ordem, capturam valores de p num campo de especificidade e tratam uma *redução* de AUC em teste de permutação como se fosse uma AUC. Nenhum desses erros sobrevive à leitura da frase, e todos sobreviveriam à captura automática.

**Todo valor guarda a frase que o sustenta.** Cada linha de `data/extracted/diagnostic_accuracy_extraction.csv` carrega a coluna `verbatim_quote`, com o trecho exato da fonte, além de PMID e DOI.

**Valores atribuídos a outros estudos não são extraídos.** Seções de discussão rotineiramente citam AUCs de outros trabalhos ("Han et al. encontraram…", "Wen et al. reportaram…"). Tais frases foram identificadas e excluídas; apenas os resultados próprios de cada estudo foram registrados.

Para cada estimativa foram capturados, quando declarados: miRNA (ou composição do painel), doença, comparação e classe da comparação, biofluido, etapa da coorte (descoberta / treinamento / validação / única), número de casos e de controles, AUC com intervalo de confiança, sensibilidade, especificidade e método de mensuração.

### Elegibilidade para o pool primário

Uma estimativa entra no pool primário apenas se for um **contraste caso-versus-controle em população definida de AD ou PD**, medindo **um ou mais miRNAs e nada além disso**. Das 76 estimativas extraídas, **51** qualificaram. As 25 restantes permanecem na tabela com um `exclusion_reason` explícito:

| Motivo | Exemplo |
|---|---|
| Comparador composto | AD discriminada conjuntamente contra FTD *e* controles |
| Contraste intradoença | PD com vs sem comprometimento cognitivo |
| População prodrômica | transtorno comportamental do sono REM isolado, e não PD estabelecida |
| Estratificação por genótipo | portadores de LRRK2, e não PD esporádica |
| População mista | "patologia neurodegenerativa" sem detalhamento por doença |
| Estimativa instável | AUC = 1,000 por separação perfeita em subgrupo de 6 pacientes |
| Coorte não atribuível | AUC reportada sem coorte ou tamanho de grupo resolvível |
| Modelo composto | miRNA combinado com variáveis clínicas não-miRNA, com parâmetros de RM, ou com lncRNA, circRNA ou proteína |
| Painel de RNAs mistos | painel com piRNAs e pseudogenes de rRNA ao lado de miRNAs |
| Teste índice não é miRNA | um lncRNA, um circRNA, assinatura gênica de tecido cerebral ou gênero do microbioma fecal |

**Publicação duplicada.** Os PMIDs 40661348 e 41836608 reportam a mesma coorte, os mesmos marcadores e as mesmas AUCs (versão preprint e versão de periódico de um mesmo estudo). O par foi detectado por frases de resultado verbatim idênticas e contado uma única vez.

## 5. Síntese estatística

Implementada em `scripts/05_meta_analysis.py` usando apenas NumPy e SciPy, para que cada etapa seja inspecionável em vez de delegada a um pacote caixa-preta.

**Erros-padrão.** Quando a fonte reportou IC 95%, EP = (superior − inferior) / (2 × 1,96). Caso contrário, o EP foi calculado por Hanley & McNeil (1982) a partir dos tamanhos dos grupos caso e controle. Estimativas sem IC e sem tamanhos de grupo não podem ser ponderadas e ficam fora da agregação — **41 das 51** estimativas elegíveis, de **20 estudos independentes**, eram agregáveis.

**Identidade do estudo.** Um estudo é identificado pelo PubMed ID quando existe e pelo DOI caso contrário. Identificar só pelo PMID colapsava os estudos publicados fora do MEDLINE num único grupo de PMID vazio, de modo que duas coortes independentes que reportam miR-124 em soro de PD estavam sendo contadas como uma. A origem do EP é registrada por estimativa em `results/tables/meta_analysis_input_estimates.csv`.

*Validação desta etapa:* para o PMID 33129241 (AUC 0,75; 18 casos vs 18 controles) a fórmula de Hanley–McNeil devolve EP = 0,0822, contra EP = 0,08 reportado de forma independente pelo próprio artigo.

**Agregação.** As AUCs foram transformadas para a escala logito, na qual são ilimitadas e se aproximam melhor da normalidade, com o EP propagado pelo método delta (EP_logito = EP_AUC / [AUC(1 − AUC)]). As estimativas foram combinadas pelo estimador de efeitos aleatórios de DerSimonian & Laird (1986) e retrotransformadas para reporte. Efeitos aleatórios foram escolhidos a priori: os estudos diferem em biofluido, plataforma, população e derivação do ponto de corte, de modo que uma AUC verdadeira comum não é hipótese plausível.

**Heterogeneidade** é reportada como Q de Cochran com seu valor de p, τ² na escala logito e I².

**Efeitos de estudos pequenos** foram avaliados pela regressão de Egger do desvio normal padronizado sobre a precisão.

**Subgrupos**, pré-especificados: por doença (AD, PD), por tipo de marcador (miRNA isolado vs painel multi-miRNA) e por biofluido quando havia ao menos três estimativas vindas de **ao menos três estudos independentes**. A condição de estudos foi acrescentada depois que a regra baseada só em estimativas produziu um subgrupo de biofluido com oito estimativas tiradas de uma única coorte, o que reporta dispersão intraestudo como se fosse evidência entre estudos.

**Sensibilidade ao agrupamento.** Vários estudos contribuem com mais de uma estimativa — um deles com oito — e o modelo de efeitos aleatórios trata cada uma como independente. Em vez de supor que isso não importa, o `scripts/05_meta_analysis.py` reagrega a estimativa de miRNA isolado de duas outras formas: uma estimativa por estudo (mediana da AUC e mediana do EP do estudo) e deixando-um-estudo-de-fora. Ambas estão em `results/tables/sensitivity_single_mirna.csv`, e a distância entre elas é tratada como parte do resultado, e não como nota de rodapé.

## 6. Risco de viés e aplicabilidade (QUADAS-2)

`scripts/14_quadas2_risk_of_bias.py`. Os 28 estudos que contribuem com ao menos uma estimativa para o pool primário foram avaliados com o QUADAS-2 (Whiting et al. 2011): quatro domínios de risco de viés e três de aplicabilidade.

**Os julgamentos são derivados por regra, não digitados.** Cada veredito sai de uma função que lê um campo registrado e devolve o julgamento junto com a razão dele. Nada é preenchido à mão. O objetivo é que quem discorde de um julgamento encontre a regra que o produziu, mude uma função e rode a avaliação de novo sobre os 28 estudos de uma vez — o que uma tabela preenchida à mão não permite.

**Dois domínios exigiam evidência que a extração de acurácia não guarda.** A extração foi feita para capturar estimativas e suas frases de origem; ela não registra padrão de referência, cegamento nem fluxo de pacientes. Esses dois domínios foram fechados por uma segunda passagem pelos textos completos, registrada estudo a estudo em `data/extracted/quadas2_study_level.csv` com a frase de onde cada resposta saiu. 22 dos 28 estudos têm texto completo recuperável pelo PubMed Central; **13** nomeiam os critérios diagnósticos que aplicaram, **um** tem confirmação neuropatológica da condição alvo e **um** declara que o diagnóstico foi cego ao teste índice. Os seis estudos cujo texto completo não pôde ser recuperado ficam incertos por essa razão declarada, e o registro diz qual razão vale para qual estudo.

**Por que nomear critérios aceitos não basta para um veredito de baixo risco.** Na DA e na DP o padrão de referência prático é critério clínico, e critério clínico classifica errado uma fração conhecida dos casos; as estimativas de acurácia herdam esse erro. Um estudo que nomeia critérios aceitos fez o que o campo espera e é classificado como *incerto*, não *baixo*. Só a confirmação neuropatológica, ou critérios nomeados mais cegamento declarado, limpa o domínio. O resultado é 2 baixo, 17 incerto e 9 alto.

**Fluxo e tempo é incerto nos 28 estudos, e isso é um achado.** Nenhum dos 22 textos completos recuperáveis traz fluxograma STARD ou prestação de contas equivalente de cada participante incluído, e só um declara o intervalo entre coleta e diagnóstico. A pergunta foi feita aos relatos primários e eles não respondem.

**O veredito uniforme de seleção de pacientes é em parte circular, e a saída diz isso.** Todo estudo é de alto risco e alta preocupação em seleção de pacientes porque toda estimativa elegível é um contraste caso-versus-controle-saudável — que a própria regra de elegibilidade da revisão exigiu. 13 estimativas de 9 estudos com contraste de diagnóstico diferencial, intradoença ou prodrômico foram excluídas por não casarem com o PICO. As comparações clinicamente relevantes existem nesta literatura e foram postas de lado pela pergunta da revisão, não faltam no campo. O `quadas2_summary.json` carrega essa afirmação ao lado das contagens para que as duas não sejam lidas separadamente.

## 7. Síntese bivariada de sensibilidade e especificidade

`scripts/15_bivariate_srocc.py`. Agrupar só a AUC esconde o ponto de operação, então os estudos que reportam sensibilidade e especificidade num limiar declarado também foram sintetizados com o modelo bivariado de efeitos aleatórios de Reitsma et al. (2005): logito da sensibilidade e logito da especificidade são tratados como um par correlacionado vindo de uma normal bivariada, com a covariância intraestudo derivada da tabela 2×2 reconstruída e a covariância entre estudos estimada por máxima verossimilhança. A curva ROC sumária é traçada como a esperança condicional do logito da sensibilidade dado o logito da especificidade.

**O estimador é testado antes de ser usado.** O script primeiro ajusta 400 estudos simulados a partir de parâmetros conhecidos e exige que os cinco sejam recuperados dentro de uma tolerância declarada; se a recuperação falhar, o script sai sem escrever resultado. O relatório de recuperação fica em `bivariate_model.json` e o `scripts/08` se recusa a passar se algum componente dele falhou.

**As tabelas 2×2 são reconstruídas, e isso é uma limitação.** Os artigos-fonte reportam proporções e não contagens, então as células são obtidas multiplicando sensibilidade e especificidade publicadas pelos tamanhos de grupo publicados e arredondando, com correção de continuidade de 0,5 onde uma célula fica vazia. A análise primária usa uma estimativa por estudo — a mais próxima da AUC mediana daquele estudo — e uma análise secundária usa toda estimativa elegível.

Análise primária, 9 estudos: sensibilidade sumária **0,796** (IC 95% 0,686–0,875), especificidade **0,725** (0,614–0,813), razão de chances diagnóstica 10,3, RV+ 2,89, RV− 0,28. Com nove estudos e cinco parâmetros, os termos entre estudos são fracamente identificados e não são interpretados sozinhos. O ponto de operação é o que esta análise sustenta, e ele é bem pior do que uma AUC agrupada perto de 0,78 sugere.

## 8. Certeza da evidência (GRADE)

`scripts/16_grade_certainty.py`. A certeza foi avaliada com o GRADE adaptado para acurácia diagnóstica (Schünemann et al. 2020), partindo de *alta* para um corpo de estudos transversais de acurácia e rebaixando em cinco domínios. Todo limiar que decide um rebaixamento é declarado como constante nomeada no topo do script e escrito em `grade_certainty.json`, de modo que quem colocaria o limiar em outro lugar possa movê-lo e rodar de novo em vez de discutir com um veredito.

| Domínio | Passos | Por quê |
|---|---|---|
| Risco de viés | −2 | 28 de 28 estudos são de alto risco em ao menos um domínio QUADAS-2 |
| Evidência indireta | −1 | 28 de 28 levantam alta preocupação de aplicabilidade: o contraste agrupado é caso versus controle saudável, não o diagnóstico diferencial que o clínico enfrenta |
| Inconsistência | −2 | I² = 95,7% nas estimativas agrupadas |
| Imprecisão | 0 | o intervalo de 95% mais largo em torno do ponto sumário é 0,199 |
| Viés de publicação | −1 | o teste de Egger no pool global devolve p < 0,0001 (arredonda para 0,0000 na tabela), fortemente suspeito |

Seis passos de rebaixamento a partir de *alta* dão certeza **muito baixa**.

**O resumo de achados é a parte a citar.** Aplicando o ponto sumário bivariado a 1000 pessoas testadas, em três probabilidades pré-teste:

| Probabilidade pré-teste | Verdadeiros positivos | Falsos positivos | Falsos negativos | VPP | VPN |
|---|---|---|---|---|---|
| 5% | 40 | 261 | 10 | 0,13 | 0,99 |
| 20% | 159 | 220 | 41 | 0,42 | 0,93 |
| 50% | 398 | 138 | 102 | 0,74 | 0,78 |

Com probabilidade pré-teste de 5% — cenário de rastreamento — o teste chama cerca de 301 pessoas de positivas a cada 1000, e 261 delas estão erradas. Os cinco domínios que colocam a certeza em muito baixa não são males separados de alguns estudos fracos: são propriedades da mesma escolha de desenho repetida pela literatura.

## 9. Atenção da literatura versus desempenho medido

`scripts/06_citation_vs_performance.py`. Para cada miRNA, contou-se o número de **artigos distintos** do corpus de **560 registros** que o mencionam em título ou resumo.

**Uma correção que mudou a resposta.** Por duas revisões, essas contagens foram calculadas sobre os 234 registros do PubMed enquanto as estimativas de acurácia já vinham do corpus completo PubMed-mais-Scopus. Todo marcador que entrou pelo Scopus era, por construção, creditado com zero menções, o que inflava a associação entre atenção e desempenho. O `scripts/11_attention_finding_audit.py` recalcula a correlação sob cada combinação de entradas e separa a contribuição do defeito da contribuição dos dados novos; o resultado está em `results/tables/attention_correlation_audit.csv`. O ρ = −0,61 (p = 0,012) antes reportado não sobrevive, e o achado está retirado. Contar artigos distintos, e não ocorrências brutas, importa: um artigo que escreve tanto "miR-125b" quanto "miR-125b-5p" não pode contar duas vezes para a família miR-125b. Os sufixos de braço (-3p/-5p) foram colapsados ao nível de família, para que uma menção a "miR-146a" possa ser casada com uma estimativa reportada para "miR-146a-5p".

As contagens de menção foram então correlacionadas (Spearman e Pearson) com a AUC média reportada por miRNA. A análise foi rodada duas vezes: sobre todas as estimativas de miRNA isolado e restrita às elegíveis para o pool primário.

Esta análise é **exploratória**. A maioria dos miRNAs contribui com um único estudo, o teste tem baixo poder, e um resultado não significativo não pode ser lido como evidência de ausência de associação.

## 10. O que este desenho não é capaz de entregar

- Ele mede acurácia **reportada**, não acurácia sob uso clínico prospectivo. A maior parte das estimativas incluídas deriva o ponto de corte na mesma amostra em que o avalia, o que infla a AUC.
- A restrição a textos completos de acesso aberto no PubMed Central pode selecionar um subconjunto não aleatório da literatura.
- Com testes de Egger significativos em vários subgrupos, os valores agregados devem ser lidos como **limites superiores**.
- Não havia dados individuais de participantes. A síntese bivariada da Seção 7 se apoia, por isso, em tabelas 2×2 reconstruídas a partir de proporções e tamanhos de grupo publicados, não em contagens reportadas, e cobre os 9 estudos que declaram limiar, e não os 20 agrupados por AUC.

## 11. Camada mecanística: modelos EDO e figuras estruturais

Esta camada pergunta algo mais estreito que a meta-análise, e deve ser lida assim. Ela não testa se um miRNA funciona como biomarcador. Pergunta o que a cinética medida de cada eixo permite, e onde uma afirmação sobre eles vai além dos números que existem.

**De onde vêm os parâmetros.** Toda taxa, meia-vida e concentração usada pelo `scripts/12_ode_models_calibrated.py` é carregada por identificador de `data/extracted/kinetic_parameters.csv` (67 linhas, 15 fontes primárias). Os valores foram lidos em textos completos ou arquivos suplementares, nunca em resumos ou citações secundárias, e cada linha numérica guarda a frase de onde veio. A tabela separa quatro tipos de linha: números medidos, restrições qualitativas (resultado afirmado sem número utilizável, como nucleação indetectável em pH neutro), lacunas declaradas e valores derivados por nós de uma tabela primária. O carregador recusa tudo que não seja número medido, então uma lacuna não pode ser preenchida em silêncio.

**O que é medido e o que não é.** Produção e depuração de Aβ42 vêm de cinética com marcação por isótopo estável no LCR humano (Mawuenyega et al. 2010, DOI 10.1126/science.1197623). Expoentes de agregação e a concentração crítica de fibrila vêm de Cohen et al. 2013 (DOI 10.1073/pnas.1218402110), e as cargas de Aβ42 no cérebro humano, da Tabela S2 desse artigo. Alongamento da α-sinucleína e sua dependência de pH vêm de Buell et al. 2014 (DOI 10.1073/pnas.1315346111). Meias-vidas de miRNA vêm de Zhang et al. 2011, Gantier et al. 2011, Kingston e Bartel 2019 e Kleaveland et al. 2018, e a renovação de proteínas, de Li et al. 2004, Liu et al. 2019 e Fornasiero et al. 2018. Constantes de agregação que nenhuma fonte dá como número (nucleação e alongamento do Aβ42, nucleação da α-sinucleína em pH ácido) ficam fixadas em valores **ilustrativos** declarados, listados com seus motivos na saída; nenhum achado reportado depende delas. Outras duas grandezas nunca foram medidas para esses genes e ficam **livres**: a força da repressão pelo miRNA e a taxa de tradução. Cada uma é varrida numa faixa declarada, em grade geométrica; nenhuma é ajustada para chegar a um resultado.

O decaimento de mRNA era um terceiro parâmetro livre e não é mais. Tushev et al. 2018 o reportam por isoforma de 3'UTR em neurônios hipocampais de rato em cultura: o SNCA tem uma isoforma, de 6,53 h (K066), e a BACE1 tem cinco, com meias-vidas de 2,8 a 23,9 h (K067). Um conjunto de isoformas não decai com a média das meias-vidas, então a taxa da BACE1 é a média ponderada das **constantes de velocidade**, 0,0456 h⁻¹, meia-vida efetiva de 15,2 h (K068); a média das meias-vidas daria 17,4 h, que é a grandeza errada. Ler essa tabela trouxe duas ressalvas. O decaimento foi observado por 16 h, então a meia-vida de 51,4 h do APP (K069) é extrapolação e fica registrada com aviso, sem ser usada. E o resumo do próprio artigo para transcrições de neurônio só se reproduz da tabela quando se excluem meias-vidas acima de cerca de 25 h (mediana 7,394 h contra os 7,38 impressos), enquanto o resumo da glia não se reproduz com nenhum filtro testado — por isso K044 é citado como impresso e nunca recalculado.

**Experimentos rodados.** (i) O braço da DA compara um déficit de depuração de 30% com a diferença de produção medida de 1,5%, e acha a dose de mimético de miR-29 que compensaria o déficit de depuração baixando a BACE1. (ii) Eliminação de mimético em dose única: o tempo para um bolus de 10x voltar a menos de 10% do basal em cada meia-vida medida. (iii) Cargas de Aβ42 no cérebro humano expressas em múltiplos da concentração crítica acima da qual a nucleação secundária domina. (iv) O braço da α-sinucleína com nucleação desligada em pH neutro, onde Buell et al. a acharam indetectável (K011), e ligada abaixo de pH 6, onde relatam que a nucleação secundária "aumenta drasticamente" (K042). A fonte dá a direção dessa chave, não o tamanho, então a constante de velocidade em pH ácido é varrida em quatro ordens de grandeza; a razão no número de fibrilas vai então de cerca de 500 a cerca de 14.000, e só a direção é reportada como resultado. (v) A dose de miR-29 que o experimento de depuração exige, posta ao lado de um efeito medido: Hébert et al. 2008 relatam cerca de 50% de queda da BACE1 com transfecção de miR-29a/b-1 em células SK-N-SH (K047). No estado estacionário o nível de BACE1 é analítico no fator do mimético, então tanto a queda produzida pela dose exigida quanto a dose que reproduziria os 50% medidos são calculadas em forma fechada nas faixas declaradas dos dois parâmetros livres de que dependem. (vi) Dois cálculos que não usam nenhum parâmetro livre, porque combinam grandezas medidas diretamente. A concentração de α-sinucleína no botão presináptico, 21,6 µM (derivada do número combinado de sinucleína e da razão medida α:β de 0,98:1, tabela S1 de Wilhelm et al. 2014), é posta sobre a curva medida de saturação da elongação, cuja concentração de meia-saturação é 46–50 µM (Buell et al. 2014): a proteína fica em 30–32% da taxa máxima de elongação, abaixo da meia-saturação, onde uma queda de 1% na concentração compra 0,68–0,70% de queda na taxa. A mesma curva então leva uma queda medida até uma taxa: o miR-7 baixa a α-sinucleína em 30% num repórter de 3'UTR e o miR-7 com o miR-153 baixa a α-sinucleína endógena em 43% em neurônios corticais de rato (Doxakis 2010), o que na curva de saturação vira 23% e 34% de elongação mais lenta — menos que proporcional, porque a curva satura. À parte, BACE1 e APP são contados na mesma preparação, 116 contra 6284 cópias por botão. Os dois atravessam sistemas — constante de saturação in vitro contra sinaptossomo de rato — e são reportados como afirmações de regime e estequiometria, não de taxa. (vii) Uma varredura dos parâmetros livres, com cada execução classificada como DA acima do controle, igual ou abaixo, ou não avaliável. Uma execução que falha numericamente é reportada como não avaliável, nunca contada como inversão. A integração usa LSODA (`scipy.integrate.solve_ivp`, rtol 1e-8, atol 1e-10).

**O que os modelos podem e não podem afirmar.** A razão de monômero DA/controle (1,41) é igual à razão entre produção e depuração medida por Mawuenyega et al. e não depende de nenhum parâmetro livre. O modelo reescreve essa medida; não a prevê. O valor dos modelos está em outro lugar: mostram que os parálogos de miR-29 decaem em ritmos diferentes (7 h e 10,6 h, e um relatado como estável) e não podem ser tratados como uma espécie só, que uma dose única de mimético de miR-7 voltaria para perto do basal em 11 a 32 horas, contra cerca de 9 dias para um miRNA típico, que a queda de BACE1 necessária para compensar o déficit de depuração medido é de 30–33% em toda a grade de parâmetros livres e portanto menor que os cerca de 50% já alcançados em células, que uma queda medida de α-sinucleína pelo miR-7 se traduz em 23–34% de elongação de fibrila mais lenta, atravessando três medidas independentes e nenhum parâmetro livre, e que as constantes de velocidade do Aβ42 necessárias para ir além não podem ser separadas com os dados publicados (linha K037).

**O que a dosagem repetida custa a um mimético de renovação rápida.** O `scripts/17_mimic_dosing_feasibility.py` faz uma pergunta que o cálculo de washout levanta mas não responde: se um mimético precisa ser dado repetidamente e não uma vez só, quanto custa a meia-vida medida? No estado estacionário sob dosagem repetida de uma espécie eliminada com constante de primeira ordem *d* no intervalo *T*, a razão entre pico e média é *dT* / (1 − e^(−*dT*)). A dose se cancela, então o cálculo não tem nenhum parâmetro livre; só entram as constantes de decaimento medidas, carregadas por identificador da tabela cinética.

Dosado uma vez por dia, um mimético de miR-7 que se renove como o miR-7 endógeno (meia-vida 1,7 h, K020) precisa atingir um pico de **9,79×** o nível médio, contra **1,26×** para um miRNA de estabilidade mediana (34 h, K016) — uma penalidade de **7,7 vezes** no pico necessário para sustentar a mesma média. Ele passa **7,1%** de cada dia acima da metade do próprio pico. Para ser dosado diariamente nos termos de que um miRNA comum desfruta, precisaria de cerca de **20 vezes** de estabilização (1,7 h → 34 h); na meia-vida medida, o intervalo equivalente é de **1,2 h**. Com a meia-vida de miR-7 no limite superior (5 h, K021) a exigência cai para 6,8 vezes, e para os parálogos de miR-29 para 4,9 (miR-29b) e 3,2 (miR-29c). O resultado é enunciado como fator de estabilização necessário e não como veredito, porque um mimético quimicamente estabilizado, por construção, não é eliminado na taxa endógena; é uma meta de projeto fixada pelas medidas, e é a quantidade que uma química de entrega precisa superar.

**Animando as mesmas simulações.** O `scripts/19_mechanism_animations.py` produz três GIFs, e reaproveita em vez de rederivar: importa os lados-direitos de EDO e as constantes medidas diretamente do `scripts/12`, e a fórmula fechada de dosagem do `scripts/17`, para que uma animação não possa calcular um número diferente do que já foi conferido. (i) O monômero de Aβ42 acumulando até seu novo estado estacionário, controle versus DA — sem parâmetro livre, já que produção e depuração são medidas. (ii) Um bolus único de mimético de 10× se eliminando na meia-vida medida, miR-7 contra um miRNA de estabilidade mediana. (iii) O dente de serra da dosagem repetida: concentração relativa à própria média, ao longo de quatro doses diárias, para as mesmas duas espécies, de modo que a altura do pico lida direto no eixo é a penalidade de pico sobre média. O último quadro de cada GIF é escrito em `results/tables/mechanism_animations.json`, e o `scripts/08` o confere contra o `ode_calibrated_results.json` e o `mimic_dosing_feasibility.json`, em vez de confiar que a animação e a figura estática concordam. O crescimento de fibrila da comporta de pH da α-sinucleína deliberadamente não é animado: sua constante de velocidade em pH ácido é ilustrativa (K042), e animá-la poria uma velocidade específica na tela para uma grandeza que este projeto reporta só como direção.

**Figuras estruturais.** O `scripts/13_structure_figures.py` renderiza quatro estruturas depositadas com o PyMOL: Argonauta2 humana com guia e alvo (6N4O), BACE1 com inibidor ligado (4D8C), uma fibrila de α-sinucleína completa (6CU7) e uma fibrila de Aβ(1-42) (5OQV). Título, método, resolução e citação primária são lidos de cada arquivo, e o script para se o título não bater com a molécula que a figura diz mostrar. Os aspartatos catalíticos da BACE1 são encontrados duas vezes, pelo motivo de sequência e pela distância ao inibidor, e precisam concordar. Os protofilamentos das fibrilas são atribuídos a partir das coordenadas, como cadeias empilhadas no espaçamento cross-β. As figuras ilustram mecanismo; não são resultado.

## 12. Figuras em dois idiomas

Toda figura em `results/figures/` é emitida duas vezes, uma em inglês e outra em português do Brasil, como `<nome>.en.png` e `<nome>.pt-BR.png`. As duas versões saem do mesmo caminho de código, na mesma execução, dos mesmos vetores: o `scripts/_bilingual.py` expõe a lista de idiomas, um seletor `t(lang, en, pt)` para o texto dos rótulos e um construtor de caminho, e cada função de plotagem é chamada uma vez por idioma. Só as palavras são traduzidas. Números, limites de eixo, posições de marcação e os próprios dados são idênticos por construção, porque são calculados antes de o laço de idioma começar e não passam pelo tradutor — um par de figuras não pode discordar sobre um valor sem que o código que as desenhou tenha mudado.

## Referências dos métodos

- DerSimonian R, Laird N. Meta-analysis in clinical trials. *Control Clin Trials.* 1986;7(3):177–188.
- Hanley JA, McNeil BJ. The meaning and use of the area under a receiver operating characteristic (ROC) curve. *Radiology.* 1982;143(1):29–36.
- Egger M, Davey Smith G, Schneider M, Minder C. Bias in meta-analysis detected by a simple, graphical test. *BMJ.* 1997;315(7109):629–634.
- Page MJ, McKenzie JE, Bossuyt PM, et al. The PRISMA 2020 statement: an updated guideline for reporting systematic reviews. *BMJ.* 2021;372:n71.
- Whiting PF, Rutjes AWS, Westwood ME, et al. QUADAS-2: a revised tool for the quality assessment of diagnostic accuracy studies. *Ann Intern Med.* 2011;155(8):529–536.
- Reitsma JB, Glas AS, Rutjes AWS, Scholten RJPM, Bossuyt PM, Zwinderman AH. Bivariate analysis of sensitivity and specificity produces informative summary measures in diagnostic reviews. *J Clin Epidemiol.* 2005;58(10):982–990.
- Schünemann HJ, Mustafa RA, Brozek J, et al. GRADE guidelines: 21 part 1 and part 2. Test accuracy. *J Clin Epidemiol.* 2020;122:129–141 e 142–152.
- McInnes MDF, Moher D, Thombs BD, et al. Preferred Reporting Items for a Systematic Review and Meta-analysis of Diagnostic Test Accuracy Studies: the PRISMA-DTA statement. *JAMA.* 2018;319(4):388–396.
