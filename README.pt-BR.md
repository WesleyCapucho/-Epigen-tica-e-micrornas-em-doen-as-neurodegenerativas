# Epigenética e microRNAs em doenças neurodegenerativas

**Pacote de reprodutibilidade de uma revisão sistemática e meta-análise de efeitos aleatórios da acurácia diagnóstica de microRNAs circulantes na doença de Alzheimer (AD) e na de Parkinson (PD).**

> 🇬🇧 **English version: [README.md](README.md)**

**Autor:** Wesley Felipe Capucho · **Orientadora:** Profa. Dra. Roberta Sessa Stilhano Yamaguchi
Universidade Federal de São Paulo (UNIFESP) — Especialização em Fisiologia e Fisiopatologia Humana aplicada às Ciências da Saúde.

---

## O que é este repositório

Este repositório guarda **dados brutos, scripts, tabelas e figuras**, e nada além disso. Sua finalidade é que todo número do manuscrito associado possa ser regerado a partir dos arquivos daqui, rodando o pipeline. O manuscrito em si é escrito e mantido fora deste repositório.

Dois corpos de trabalho convivem aqui:

| Camada | O que é | Scripts |
|---|---|---|
| **Bibliométrica** | Mineração do corpus PubMed, extração de miRNAs, PCA, clusterização, rede miRNA–doença, modelos EDO exploratórios dos eixos miR-29/BACE1/Aβ e miR-7/SNCA/α-sinucleína | `01`, `02` |
| **Meta-analítica** | Busca sistemática PICO, triagem PRISMA, extração de texto completo, meta-análise de efeitos aleatórios de AUC, panorama de translação clínica | `03`–`11` |

A camada meta-analítica existe para responder a uma pergunta que a monografia de origem levantou sobre si mesma: frequência bibliométrica e validação experimental não são fontes independentes de evidência, porque os miRNAs mais estudados acumulam as duas. A acurácia diagnóstica agregada é externa a esse laço.

## Estado atual da base de evidência

| | |
|---|---|
| Bases consultadas | PubMed/MEDLINE, Scopus (os dois braços de doença) |
| Registros únicos | 560 |
| Textos completos lidos | 47 |
| Estudos que contribuem com estimativas | 42 |
| Estimativas extraídas | 76 (51 elegíveis, 41 agregáveis) |
| Estudos independentes agregados | 20 |
| Data da busca | 10 de setembro de 2026 |

As estimativas agregadas estão em `results/tables/meta_analysis_pooled_auc.csv`, as entradas por estimativa em `results/tables/meta_analysis_input_estimates.csv`, e as análises de sensibilidade a agrupamento em `results/tables/sensitivity_single_mirna.csv`. Todo valor extraído é rastreável até a frase verbatim de sua fonte em `data/extracted/diagnostic_accuracy_extraction.csv`.

A interpretação pertence ao manuscrito, não a este repositório. Duas coisas, porém, pertencem aqui, porque são propriedades dos dados e não do argumento:

- **Estimativas de um mesmo estudo são correlacionadas.** Um estudo contribui com oito estimativas e outro com seis, e o modelo de efeitos aleatórios trata cada uma como independente. Por isso o `scripts/05` também reagrega uma-estimativa-por-estudo e deixando-um-estudo-de-fora, e a distância entre elas faz parte do resultado.
- **Três defeitos foram encontrados e corrigidos neste pipeline, e cada um mudou um número.** Estão registrados em `data/processed/prisma_flow.json` e nos comentários de cabeçalho dos scripts que carregam a correção. Ver *Correções* abaixo.

## Estrutura do repositório

```
.
├── data/
│   ├── raw/
│   │   ├── pubmed/                    # Amostra bibliométrica, direto do NCBI (proveniência em manifest.json)
│   │   ├── systematic_review_2026/    # Estratégia de busca, corpus e decisões de triagem,
│   │   │                              #   exportações do Scopus, contagens de menção, meta-análises prévias
│   │   └── clinical_trials_2026/      # Panorama do ClinicalTrials.gov de terapêuticos dirigidos a miRNA
│   ├── extracted/                     # Tabela de extração de acurácia + citações verbatim das fontes
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
│   └── 11_attention_finding_audit.py              # Decompõe o que deslocou a correlação de atenção
├── docs/
│   ├── en/                            # Methods, data dictionary, how to export Scopus/WoS
│   └── pt-BR/                         # Métodos, dicionário de dados, como exportar Scopus/WoS
├── results/
│   ├── figures/                       # Forest plot, funnel plot, gráfico atenção-vs-acurácia
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
python scripts/08_verify_consistency.py           # precisa passar antes de versionar
```

Os `scripts/05`, `06`, `08`, `10` e `11` rodam inteiramente offline a partir dos dados versionados. O `scripts/03` chama a API ao vivo do PubMed e vai legitimamente retornar mais registros do que as contagens congeladas de 10/09/2026, porque a literatura continua crescendo; o `data/raw/systematic_review_2026/search_strategy.json` preserva as contagens por trás dos números reportados.

O Scopus não pode ser consultado por API a partir de um script — exige autenticação institucional. Rode a busca na interface web do Scopus, exporte o conjunto de resultados e entregue o arquivo ao `scripts/09`. As queries prontas para colar estão em `docs/pt-BR/COMO_EXPORTAR_SCOPUS_WOS.md`.

Para a camada bibliométrica, rode o `scripts/01` primeiro: ele produz a entrada do `scripts/02`.

## Proveniência e integridade dos dados

- **Todo número veio de uma fonte real.** Os registros do PubMed foram puxados da API E-utilities do NCBI; os valores de acurácia foram lidos em textos completos de acesso aberto no PubMed Central ou no resumo quando nenhum texto completo estava acessível. Nada foi simulado, estimado para preencher lacuna ou herdado de citação secundária.
- **Todo valor extraído guarda a frase que o sustenta.** O `diagnostic_accuracy_extraction.csv` traz a coluna `verbatim_quote` com a redação exata que sustenta cada AUC, sensibilidade e especificidade, além de PMID e DOI.
- **Valores que não puderam ser resolvidos sem ambiguidade foram mantidos e sinalizados, não descartados em silêncio.** 25 das 76 linhas extraídas estão marcadas com `eligible_primary_pool = no` e um `exclusion_reason` explícito.
- **A mineração automática de texto serviu para *encontrar* valores candidatos, nunca para registrá-los.** Expressões regulares trouxeram as frases à superfície; os valores foram então lidos e transcritos à mão, porque os padrões comprovadamente trocam sensibilidade por especificidade e confundem valores de p com métricas de acurácia.
- **Publicação duplicada foi checada.** Os PMIDs 40661348 e 41836608 reportam a mesma coorte e as mesmas AUCs (versão preprint e versão de revista); são contados uma vez só.
- **O método de erro-padrão foi validado contra uma fonte.** Para o PMID 33129241, a fórmula de Hanley–McNeil devolve EP = 0,0822 para AUC 0,75 com 18 vs 18 sujeitos; o artigo reporta independentemente EP = 0,08.
- **O `scripts/08` faz cumprir tudo isso.** Ele recalcula cada número derivado a partir da fonte e falha se a tabela de extração, as contagens PRISMA e as tabelas de resultado discordarem. Atualmente 429 verificações passam.

Os textos completos **não** são redistribuídos aqui — apenas os pontos de dado extraídos e suas citações. Busque as fontes pelos DOIs.

## Correções

Três defeitos deste pipeline foram encontrados depois que resultados já haviam sido produzidos. Cada um está corrigido, e cada um mudou um número reportado. Estão listados aqui em vez de silenciosamente remendados, porque um pacote de reprodutibilidade que esconde as próprias correções não é um.

| Defeito | Efeito | Corrigido em |
|---|---|---|
| Regex de triagem fechava com `\b` após `meta-analys`, e assim nunca casava com "meta-analysis" | Meta-análises autodeclaradas passavam como estudos primários; um registro reclassificado; é a razão de meta-análises prévias passarem despercebidas | `scripts/04` |
| Contagens de menção calculadas sobre 234 registros do PubMed enquanto as AUCs vinham do corpus de 560 | Marcadores que entraram pelo Scopus recebiam zero menções por construção, inflando a correlação atenção–desempenho | `scripts/10` |
| Estudos identificados só por PMID | Os quatro estudos publicados fora do MEDLINE colapsavam num único grupo de PMID vazio; duas coortes independentes de miR-124 contadas como uma; totais de estudo subestimados | `scripts/05`, `scripts/06` |
| Subgrupos de biofluido exigiam três *estimativas*, e não três *estudos* | Produziam um subgrupo de oito estimativas vindas de uma só coorte — dispersão intraestudo reportada como evidência entre estudos | `scripts/05` |
| O `scripts/09` deduplicava apenas contra o PubMed | O braço PD do Scopus parecia acrescentar 157 registros novos em vez de 78 | `scripts/09` |

O `scripts/11_attention_finding_audit.py` quantifica o segundo destes: recalcula a correlação atenção–desempenho sob cada combinação de entradas e separa a contribuição do defeito da contribuição dos dados novos.

## Limitações conhecidas

- A Web of Science não foi consultada. A cobertura é simétrica entre as doenças, mas tem profundidade de duas bases.
- A extração se restringe a textos completos de acesso aberto e a resumos, o que pode selecionar um subconjunto não aleatório da literatura; quatro estudos do braço PD estavam com acesso restrito de modo que só uma AUC de modelo combinado pôde ser lida.
- 34 dos 41 erros-padrão ponderados são reconstruídos por Hanley–McNeil, e não retirados de intervalo publicado.
- A heterogeneidade é alta (I² até 97%) e as estimativas dentro dos estudos são correlacionadas, o que também torna o teste de Egger pouco confiável aqui.
- A maioria dos miRNAs contribui com um único estudo, então a análise de atenção versus desempenho tem pouco poder nos dois sentidos.
- Os modelos EDO do `scripts/02` usam parâmetros ilustrativos e não calibrados. São qualitativos e geradores de hipótese; não são predições quantitativas e não devem ser reportados como tal.

## Integridade científica e uso de IA

Este trabalho segue os princípios de transparência e reprodutibilidade do Guia de Boas Práticas Científicas da USP (2025). Ferramentas de IA auxiliaram na organização, no código, na recuperação de informação e na redação; não substituíram a curadoria dos dados, a verificação contra as fontes nem o julgamento científico do autor. Nenhum dado foi fabricado. Onde um valor não pôde ser verificado contra sua fonte, ele foi excluído e a exclusão registrada.

## Citação

Capucho, W. *Epigenética e microRNAs em doenças neurodegenerativas: revisão sistemática e meta-análise da acurácia diagnóstica de miRNAs circulantes.* GitHub, 2026. https://github.com/WesleyCapucho/-Epigen-tica-e-micrornas-em-doen-as-neurodegenerativas

Os dados de literatura vêm do PubMed/PubMed Central (National Library of Medicine, NCBI) e do Scopus (Elsevier). Os estudos individuais são citados por DOI em `data/extracted/diagnostic_accuracy_extraction.csv`.
