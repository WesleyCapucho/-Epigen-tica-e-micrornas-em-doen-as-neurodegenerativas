# Epigenética e microRNAs em doenças neurodegenerativas

**Pacote de reprodutibilidade de uma revisão sistemática e meta-análise de efeitos aleatórios da acurácia diagnóstica de microRNAs circulantes na doença de Alzheimer (AD) e na de Parkinson (PD).**

> 🇬🇧 **English version: [README.md](README.md)**

**Autor:** Wesley Felipe Capucho
Universidade Federal de São Paulo (UNIFESP) — Especialização em Fisiologia e Fisiopatologia Humana aplicada às Ciências da Saúde.

**Registro:** Esta revisão sistemática tem registro retrospectivo no OSF Registries: [https://doi.org/10.17605/OSF.IO/NJ8A5](https://doi.org/10.17605/OSF.IO/NJ8A5).

---

## O que é este repositório

Este repositório guarda **dados brutos, scripts, tabelas e figuras**, e nada além disso. Sua finalidade é que todo número do manuscrito associado possa ser regerado a partir dos arquivos daqui, rodando o pipeline. O manuscrito em si é escrito e mantido fora deste repositório.

Dois corpos de trabalho convivem aqui:

| Camada | O que é | Scripts |
|---|---|---|
| **Bibliométrica** | Mineração do corpus PubMed, extração de miRNAs, PCA, clusterização, rede miRNA–doença, modelos EDO exploratórios dos eixos miR-29/BACE1/Aβ e miR-7/SNCA/α-sinucleína | `01`, `02` |
| **Meta-analítica** | Busca sistemática PICO, triagem PRISMA, extração de texto completo, meta-análise de efeitos aleatórios de AUC, panorama de translação clínica | `03`–`11` |
| **Mecanística** | Modelos EDO dos dois eixos construídos sobre medidas cinéticas publicadas; figuras estruturais renderizadas a partir de coordenadas depositadas; viabilidade de dosagem a partir de constantes de decaimento medidas; um graphical abstract dos dois eixos; GIFs animados das mesmas simulações; um painel composto dos renders estruturais | `12`, `13`, `17`, `18`, `19`, `20` |
| **Apreciação crítica** | Risco de viés QUADAS-2, síntese bivariada de sensibilidade e especificidade, certeza da evidência GRADE | `14`–`16` |

A camada meta-analítica existe para responder a uma pergunta que a monografia de origem levantou sobre si mesma: frequência bibliométrica e validação experimental não são fontes independentes de evidência, porque os miRNAs mais estudados acumulam as duas. A acurácia diagnóstica agregada é externa a esse laço.

## Estado atual da base de evidência

| | |
|---|---|
| Bases consultadas | PubMed/MEDLINE, Scopus, Web of Science (os dois braços de doença) |
| Registros únicos | 587 |
| Textos completos lidos | 47 |
| Estudos que contribuem com estimativas | 45 |
| Estimativas extraídas | 79 (51 elegíveis, 41 agregáveis) |
| Estudos independentes agregados | 20 |
| Data da busca | 10 de setembro de 2026 (PubMed, Scopus); 23 de setembro de 2026 (Web of Science) |
| Estudos avaliados com QUADAS-2 | 28 |
| Certeza da evidência (GRADE) | Muito baixa |

As estimativas agregadas estão em `results/tables/meta_analysis_pooled_auc.csv`, as entradas por estimativa em `results/tables/meta_analysis_input_estimates.csv`, e as análises de sensibilidade a agrupamento em `results/tables/sensitivity_single_mirna.csv`. Todo valor extraído é rastreável até a frase verbatim de sua fonte em `data/extracted/diagnostic_accuracy_extraction.csv`.

A interpretação pertence ao manuscrito, não a este repositório. Duas coisas, porém, pertencem aqui, porque são propriedades dos dados e não do argumento:

- **Estimativas de um mesmo estudo são correlacionadas.** Um estudo contribui com oito estimativas e outro com seis, e o modelo de efeitos aleatórios trata cada uma como independente. Por isso o `scripts/05` também reagrega uma-estimativa-por-estudo e deixando-um-estudo-de-fora, e a distância entre elas faz parte do resultado.
- **Onze defeitos foram encontrados e corrigidos neste pipeline.** Estão registrados em `data/processed/prisma_flow.json` e nos comentários de cabeçalho dos scripts que carregam a correção. Ver *Correções* abaixo.

## Estrutura do repositório

```
.
├── data/
│   ├── raw/
│   │   ├── pubmed/                    # Amostra bibliométrica, direto do NCBI (proveniência em manifest.json)
│   │   ├── systematic_review_2026/    # Estratégia de busca, corpus e decisões de triagem,
│   │   │                              #   exportações do Scopus, contagens de menção, meta-análises prévias
│   │   ├── clinical_trials_2026/      # Panorama do ClinicalTrials.gov de terapêuticos dirigidos a miRNA
│   │   ├── kinetics_2026/             # Tabelas suplementares: meias-vidas genômicas (Schwanhäusser 2011),
│   │   │                              #   cópias de proteína presináptica (Wilhelm 2014, tabela S1),
│   │   │                              #   meias-vidas de isoformas de 3'UTR neuronais (Tushev 2018, tabela S1)
│   │   └── structures_2026/           # Coordenadas depositadas: 6N4O, 4D8C, 6CU7, 5OQV
│   ├── extracted/                     # Tabela de extração de acurácia e tabela de parâmetros cinéticos,
│   │                                  #   ambas com citações verbatim das fontes
│   └── processed/                     # Contagens do fluxo PRISMA (regeráveis)
├── scripts/
│   ├── 01_busca_ranqueamento_pubmed.py            # Busca e ranqueamento bibliométrico (monografia original)
│   ├── 02_estatistica_bioinformatica_modelagem.py # Estatística, PCA, redes, modelos EDO (original)
│   ├── 03_systematic_search.py                    # Busca sistemática PICO via NCBI E-utilities
│   ├── 04_screening.py                            # Triagem PRISMA baseada em regras
│   ├── 05_meta_analysis.py                        # Meta-análise de efeitos aleatórios + sensibilidade
│   ├── 06_citation_vs_performance.py              # Atenção da literatura vs acurácia medida
│   ├── 07_clinical_translation_landscape.py       # O que de fato chegou a ensaios clínicos
│   ├── 08_verify_consistency.py                   # Cruza dados, contagens PRISMA e tabelas de resultado
│   ├── 09_ingest_scopus_wos.py                    # Funde e deduplica exportações Scopus / WoS
│   ├── 10_build_screening_corpus.py               # Monta o corpus, reconstrói as contagens de menção
│   ├── 11_attention_finding_audit.py              # Decompõe o que deslocou a correlação de atenção
│   ├── 12_ode_models_calibrated.py                # Modelos EDO sobre constantes cinéticas publicadas
│   ├── 13_structure_figures.py                    # Figuras PyMOL a partir de estruturas depositadas
│   ├── 14_quadas2_risk_of_bias.py                 # QUADAS-2, julgamentos derivados por regra
│   ├── 15_bivariate_srocc.py                      # Modelo bivariado de Reitsma + ROC sumária
│   ├── 16_grade_certainty.py                      # Certeza GRADE + resumo de achados por 1000
│   ├── 17_mimic_dosing_feasibility.py             # O que a dosagem repetida custa a um mimético instável
│   ├── 18_graphical_abstract.py                   # Figura esquemática: os dois eixos, números calculados
│   ├── 19_mechanism_animations.py                 # GIFs animados de mecanismos já simulados
│   ├── 20_structure_story_panel.py                # Compõe os renders do scripts/13 numa figura só
│   ├── _bilingual.py                              # Auxiliar comum: toda figura emitida em EN e pt-BR
│   └── tools/mirror_extraction_json.py            # Regenera o espelho JSON da tabela de extração
├── docs/
│   ├── en/                            # Methods, data dictionary, PRISMA-DTA checklist, Scopus/WoS export
│   └── pt-BR/                         # Métodos, dicionário de dados, checklist PRISMA-DTA, exportação
├── results/
│   ├── figures/                       # Forest plot, funnel plot, atenção-vs-acurácia, SROC, QUADAS-2, GRADE,
│   │                                  #   dosagem e visão geral das EDOs — cada uma duas vezes, .en.png e
│   │                                  #   .pt-BR.png; structures/ (renderizações PyMOL)
│   └── tables/                        # Estimativas agregadas, entradas, sensibilidade, correlações, auditoria
└── requirements.txt
```

## Reproduzindo a análise

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

export NCBI_EMAIL=voce@exemplo.org    # exigido pelos scripts que chamam o NCBI

# Camada meta-analítica, na ordem
python scripts/03_systematic_search.py            # busca ao vivo no PubMed
python scripts/04_screening.py
python scripts/09_ingest_scopus_wos.py --scopus <exportacao.csv> --arm AD
python scripts/10_build_screening_corpus.py       # corpus + contagens de menção
python scripts/05_meta_analysis.py
python scripts/06_citation_vs_performance.py
python scripts/07_clinical_translation_landscape.py
python scripts/11_attention_finding_audit.py
python scripts/14_quadas2_risk_of_bias.py
python scripts/15_bivariate_srocc.py
python scripts/16_grade_certainty.py               # exige que o 14 e o 15 já tenham rodado
python scripts/08_verify_consistency.py           # precisa passar antes de versionar

# Camada mecanística, offline
python scripts/12_ode_models_calibrated.py
python scripts/17_mimic_dosing_feasibility.py
python scripts/19_mechanism_animations.py
pip install pymol-open-source                     # só é necessário para o scripts/13
python scripts/13_structure_figures.py
python scripts/18_graphical_abstract.py     # needs 12, 17 and 13 to have run
python scripts/20_structure_story_panel.py
```

Os `scripts/05`, `06`, `08`, `10` e `11` rodam inteiramente offline a partir dos dados versionados. O `scripts/03` chama a API ao vivo do PubMed e vai legitimamente retornar mais registros do que as contagens congeladas de 10/09/2026, porque a literatura continua crescendo; o `data/raw/systematic_review_2026/search_strategy.json` preserva as contagens por trás dos números reportados.

O Scopus não pode ser consultado por API a partir de um script — exige autenticação institucional. Rode a busca na interface web do Scopus, exporte o conjunto de resultados e entregue o arquivo ao `scripts/09`. As queries prontas para colar estão em `docs/pt-BR/COMO_EXPORTAR_SCOPUS_WOS.md`.

Para a camada bibliométrica, rode o `scripts/01` primeiro: ele produz a entrada do `scripts/02`.

## Proveniência e integridade dos dados

- **Todo número veio de uma fonte real.** Os registros do PubMed foram puxados da API E-utilities do NCBI; os valores de acurácia foram lidos em textos completos de acesso aberto no PubMed Central ou no resumo quando nenhum texto completo estava acessível. Nada foi simulado, estimado para preencher lacuna ou herdado de citação secundária.
- **Todo valor extraído guarda a frase que o sustenta.** O `diagnostic_accuracy_extraction.csv` traz a coluna `verbatim_quote` com a redação exata que sustenta cada AUC, sensibilidade e especificidade, além de PMID e DOI.
- **Valores que não puderam ser resolvidos sem ambiguidade foram mantidos e sinalizados, não descartados em silêncio.** 28 das 79 linhas extraídas estão marcadas com `eligible_primary_pool = no` e um `exclusion_reason` explícito.
- **A mineração automática de texto serviu para *encontrar* valores candidatos, nunca para registrá-los.** Expressões regulares trouxeram as frases à superfície; os valores foram então lidos e transcritos à mão, porque os padrões comprovadamente trocam sensibilidade por especificidade e confundem valores de p com métricas de acurácia.
- **Publicação duplicada foi checada.** Os PMIDs 40661348 e 41836608 reportam a mesma coorte e as mesmas AUCs (versão preprint e versão de revista); são contados uma vez só.
- **O método de erro-padrão foi validado contra uma fonte.** Para o PMID 33129241, a fórmula de Hanley–McNeil devolve EP = 0,0822 para AUC 0,75 com 18 vs 18 sujeitos; o artigo reporta independentemente EP = 0,08.
- **O `scripts/08` faz cumprir tudo isso.** Ele recalcula cada número derivado a partir da fonte e falha se a tabela de extração, as contagens PRISMA e as tabelas de resultado discordarem. Atualmente 1656 verificações passam.

- **Os parâmetros cinéticos seguem a mesma regra.** `data/extracted/kinetic_parameters.csv` tem 67 linhas de 15 fontes primárias. Todo valor medido traz a frase de onde foi lido, e o `scripts/08` confere se o número de fato aparece nessa frase. Um parâmetro procurado e não encontrado fica registrado como `declared_gap`, sem valor e sem citação emprestada, e o código das EDOs se recusa a carregá-lo. Duas linhas são `derived` (medianas genômicas calculadas a partir da tabela arquivada de Schwanhäusser); o `scripts/08` as recalcula a partir do arquivo.
- **As figuras estruturais citam o próprio depósito.** O `scripts/13` lê título, método, resolução e citação primária de cada arquivo de coordenadas e para se o título não bater com a molécula que a figura diz mostrar. O leitor de citação ignora o DOI de depósito do próprio PDB, que é fácil de confundir com o DOI do artigo.

Os textos completos **não** são redistribuídos aqui — apenas os pontos de dado extraídos e suas citações. Busque as fontes pelos DOIs.

## Correções

Onze defeitos deste pipeline foram encontrados depois que resultados já haviam sido produzidos. Cada um está corrigido, e cada um mudou um número reportado. Estão listados aqui em vez de silenciosamente remendados, porque um pacote de reprodutibilidade que esconde as próprias correções não é um.

| Defeito | Efeito | Corrigido em |
|---|---|---|
| Regex de triagem fechava com `\b` após `meta-analys`, e assim nunca casava com "meta-analysis" | Meta-análises autodeclaradas passavam como estudos primários; um registro reclassificado; é a razão de meta-análises prévias passarem despercebidas | `scripts/04` |
| Contagens de menção calculadas sobre 234 registros do PubMed enquanto as AUCs vinham do corpus de 560 | Marcadores que entraram pelo Scopus recebiam zero menções por construção, inflando a correlação atenção–desempenho | `scripts/10` |
| Estudos identificados só por PMID | Os quatro estudos publicados fora do MEDLINE colapsavam num único grupo de PMID vazio; duas coortes independentes de miR-124 contadas como uma; totais de estudo subestimados | `scripts/05`, `scripts/06` |
| Subgrupos de biofluido exigiam três *estimativas*, e não três *estudos* | Produziam um subgrupo de oito estimativas vindas de uma só coorte — dispersão intraestudo reportada como evidência entre estudos | `scripts/05` |
| O `scripts/09` deduplicava apenas contra o PubMed | O braço PD do Scopus parecia acrescentar 157 registros novos em vez de 78 | `scripts/09` |
| O `scripts/09` lia o DOI do PubMed só como `DOI`, mas o corpus o guarda como `doi` | A desduplicação por DOI contra toda a metade do PubMed ficou inerte; um artigo entrou duas vezes sob duas composições do próprio título | `scripts/09` |
| O `scripts/09` deduplicava um braço contra um corpus que já o continha | Reingerir um braço devolvia zero registros novos e esvaziava o arquivo dele; o pipeline documentado destruía dados se rodado duas vezes | `scripts/09` |
| O `scripts/09` nomeava a saída só pelo `--arm` e a excluía da desduplicação | Reusar um rótulo entre bases substituía em silêncio o braço anterior; ingerir a Web of Science como `--arm AD` teria apagado 248 registros da Scopus | `scripts/09` |
| O `scripts/04` lia o corpus como se fosse só do PubMed, e sobrescrevia o `prisma_flow.json` inteiro | Quebrava no primeiro registro importado, e se não quebrasse teria substituído o registro PRISMA curado por cinco chaves | `scripts/04` |
| O `scripts/10` contava todo registro importado como Scopus | Com a Web of Science ingerida, isso poria uma contagem por base falsa nos métodos | `scripts/10` |
| A busca do braço AD no PubMed reportou 168 registros, mas só 167 foram de fato obtidos e arquivados; todo documento citava o 168 não arquivado | A contagem do braço AD, e o texto de métodos que a citava, discordavam dos PMIDs de fato arquivados; achado ao auditar o texto do registro OSF contra o repositório | saída do `scripts/03`, `data/processed/prisma_flow.json` |

O `scripts/11_attention_finding_audit.py` quantifica o segundo destes: recalcula a correlação atenção–desempenho sob cada combinação de entradas e separa a contribuição do defeito da contribuição dos dados novos.

## Limitações conhecidas

- **A Web of Science já foi consultada**, em 23 de setembro de 2026, sob autenticação institucional e treze dias depois das outras duas bases — o que é reportado como data própria de busca, e não fundido às delas. Ela retornou 295 registros nos dois braços, dos quais **27 eram novos**, e **nenhum deles entrou no pool primário**: um mede um RNA longo não codificante e não um microRNA, um mede córtex post-mortem e não um biofluido circulante, e o único registro que casa com o PICO reporta a AUC apenas como a desigualdade "AUC>0,90" e não tem DOI, nem PubMed ID, nem texto completo alcançável para confirmar um valor. Os três ficam registrados na tabela de extração com suas razões de exclusão (E077–E079), em vez de descartados. As estimativas agregadas, o ponto de operação bivariado, a tabela QUADAS-2 e a classificação GRADE são idênticos byte a byte antes e depois.
- A extração se restringe a textos completos de acesso aberto e a resumos, o que pode selecionar um subconjunto não aleatório da literatura; quatro estudos do braço PD estavam com acesso restrito de modo que só uma AUC de modelo combinado pôde ser lida.
- 34 dos 41 erros-padrão ponderados são reconstruídos por Hanley–McNeil, e não retirados de intervalo publicado.
- A heterogeneidade é alta (I² até 97%) e as estimativas dentro dos estudos são correlacionadas, o que também torna o teste de Egger pouco confiável aqui.
- A maioria dos miRNAs contribui com um único estudo, então a análise de atenção versus desempenho tem pouco poder nos dois sentidos.
- **A revisão não foi registrada e não tem protocolo prospectivo.** A busca, as regras de elegibilidade e as decisões de triagem estão congeladas no repositório conforme aplicadas, o que as torna auditáveis mas não pré-especificadas. Ver `docs/pt-BR/CHECKLIST_PRISMA_DTA.md`, item 5.
- **A triagem não teve segundo revisor independente**, e não existe estatística de concordância.
- **Os quatro domínios de risco de viés do QUADAS-2 estão agora avaliados**, os dois últimos por uma segunda passagem pelos textos completos (`data/extracted/quadas2_study_level.csv`). O que essa passagem encontrou é, em si, uma limitação desta literatura: dos 22 estudos com texto completo recuperável, **um** tem confirmação neuropatológica do diagnóstico, **um** declara que o diagnóstico foi cego ao teste índice e **nenhum** traz fluxograma STARD. Seis estudos não têm texto completo recuperável e ficam incertos por essa razão declarada.
- **Toda estimativa do pool primário é um contraste caso-versus-controle-saudável**, o desenho que o QUADAS-2 aponta como inflador de acurácia. Isso é em parte por construção, já que a regra de elegibilidade exigia esse contraste; 13 estimativas de 9 estudos com contraste de diagnóstico diferencial, prodrômico ou intradoença foram excluídas por não casarem com o PICO.
- **A certeza da evidência é muito baixa** (GRADE para acurácia diagnóstica): seis passos de rebaixamento a partir de *alta*, por risco de viés (−2), inconsistência (−2, I² = 95,7%), evidência indireta (−1) e viés de publicação (−1). Com probabilidade pré-teste de 5%, o ponto de operação sumário chama cerca de 301 pessoas de positivas a cada 1000, e 261 delas estão erradas (VPP 0,13). Todo limiar por trás desses julgamentos é uma constante nomeada no `scripts/16`, que pode ser movida e rodada de novo.
- No ponto de operação sumário bivariado (9 estudos, sensibilidade 0,80, especificidade 0,72), as razões de verossimilhança são 2,9 positiva e 0,28 negativa. Uma AUC agrupada perto de 0,78 soa melhor que o ponto de operação de onde vem. As tabelas 2×2 por trás dele são reconstruídas a partir de proporções e tamanhos de grupo publicados, porque os artigos-fonte não reportam contagens.
- Os modelos EDO do `scripts/02` usam parâmetros ilustrativos e não calibrados e ficam aqui só como parte da monografia original. Foram substituídos pelo `scripts/12`.
- O `scripts/12` usa constantes medidas onde elas existem, mas elas vêm de sistemas diferentes (LCR humano, células HEK, neurônios de rato e camundongo, SH-SY5Y, fibroblastos). Dois parâmetros nunca foram medidos para esses genes e ficam livres, declarados e varridos numa faixa, sem ajuste. O decaimento de mRNA era o terceiro até a tabela suplementar do Tushev ser lida; agora é medido por gene. As constantes de agregação do Aβ42 não podem ser separadas umas das outras com os dados publicados (linha K037), e a nucleação da α-sinucleína em pH ácido só é relatada de forma qualitativa (K042). Essas constantes ficam fixadas em valores ilustrativos declarados. Por isso, o tamanho da chave de pH da α-sinucleína não é resultado: na varredura do `scripts/12` ele vai de cerca de 500 a cerca de 14.000 vezes. Só a direção é.
- O número mais nítido do modelo, um nível de monômero de Aβ 1,41 vez maior na DA, é fixado analiticamente pelas taxas de produção e depuração de Mawuenyega et al. 2010 e não depende de nenhum parâmetro livre. Ele reescreve essa medida em forma de modelo; não é uma predição independente.
- A comparação entre a dose de miR-29 que o modelo pede e a queda que Hébert et al. mediram atravessa sistemas: um estado estacionário num modelo de cérebro humano contra uma transfecção transitória de linhagem de neuroblastoma. Ela responde se a intervenção exigida é maior ou menor que uma já alcançada em células, e nada além disso.
- As figuras estruturais são ilustração. Não testam nada. As resoluções vêm de critérios diferentes (6CU7 FSC 0,5; 5OQV FSC 0,143) e não são diretamente comparáveis.
- O `scripts/17` supõe que um mimético entregue seja eliminado na mesma taxa de primeira ordem da espécie endógena. Um mimético quimicamente estabilizado não seria, e é exatamente por isso que a saída dele é um fator de estabilização **necessário** (20× para o miR-7 tolerar dose diária) e não um veredito de viabilidade. O cálculo não tem parâmetro livre — a dose se cancela na razão entre pico e média — mas é uma afirmação sobre farmacocinética em abstrato, não sobre um veículo de entrega ou tecido em particular.
- O `scripts/19` anima três dos mecanismos acima (Aβ42 alcançando o novo estado estacionário, a eliminação de dose única, o dente de serra da dosagem repetida) reaproveitando exatamente as funções do `scripts/12` e do `scripts/17`, sem rederivá-las — o último quadro de cada GIF é conferido contra o mesmo JSON com que as figuras estáticas são conferidas. Ele deliberadamente **não** anima o crescimento de fibrila da comporta de pH da α-sinucleína, porque a constante de velocidade em pH ácido dessa curva é declarada ilustrativa (K042, só qualitativa): pôr uma velocidade específica na tela para uma grandeza que este projeto reporta só como direção, não magnitude, seria mais enganoso em movimento do que já é parado. Esses GIFs são ilustração de simulações que já estão neste repositório, não um experimento novo.

## Integridade científica e uso de IA

Este trabalho segue os princípios de transparência e reprodutibilidade do Guia de Boas Práticas Científicas da USP (2025). Ferramentas de IA auxiliaram na organização, no código, na recuperação de informação e na redação; não substituíram a curadoria dos dados, a verificação contra as fontes nem o julgamento científico do autor. Nenhum dado foi fabricado. Onde um valor não pôde ser verificado contra sua fonte, ele foi excluído e a exclusão registrada.

## Citação

Capucho, W. *Epigenética e microRNAs em doenças neurodegenerativas: revisão sistemática e meta-análise da acurácia diagnóstica de miRNAs circulantes.* GitHub, 2026. https://github.com/WesleyCapucho/-Epigen-tica-e-micrornas-em-doen-as-neurodegenerativas

Os dados de literatura vêm do PubMed/PubMed Central (National Library of Medicine, NCBI) e do Scopus (Elsevier). Os estudos individuais são citados por DOI em `data/extracted/diagnostic_accuracy_extraction.csv`.
