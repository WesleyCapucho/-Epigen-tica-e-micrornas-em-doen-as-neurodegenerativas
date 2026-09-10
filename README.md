# Epigenética e microRNAs em doenças neurodegenerativas

Revisão integrativa, análise bioinformática e modelagem computacional de vias associadas à Doença de Alzheimer e à Doença de Parkinson.

Trabalho de Conclusão de Curso — Universidade Federal de São Paulo (UNIFESP), Especialização em Fisiologia e Fisiopatologia Humana aplicada às Ciências da Saúde. Autor: Wesley Felipe Capucho. Orientadora: Profa. Dra. Roberta Sessa Stilhano Yamaguchi.

Este repositório está em processo de expansão para elevar o trabalho a um manuscrito de maior rigor e impacto científico. Esta reorganização separa dados brutos, scripts e resultados para garantir reprodutibilidade total do pipeline.

## Estrutura do repositório

```
.
├── data/
│   ├── raw/              # Dados brutos, tal como obtidos das fontes originais (não editar)
│   │   └── pubmed/        # Metadados reais de artigos PubMed (API NCBI E-utilities)
│   └── processed/         # Saídas geradas pelos scripts (ranqueamento, anotações) — não versionadas, reprodutíveis via scripts/
├── scripts/
│   ├── 01_busca_ranqueamento_pubmed.py       # Busca PubMed, ranqueamento e anotação automática
│   └── 02_estatistica_bioinformatica_modelagem.py  # Estatística, PCA, clustering, redes, EDOs, heatmaps
├── docs/
│   └── PLANO_DE_ACAO_ARTIGO_ALTO_IMPACTO.md  # Diagnóstico de lacunas e plano faseado de elevação do TCC a artigo
├── results/
│   ├── figures/           # Figuras geradas pelos scripts (não versionadas)
│   └── tables/            # Tabelas geradas pelos scripts (não versionadas)
├── requirements.txt
└── README.md
```

## Reprodutibilidade

### 1. Ambiente

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Coleta de dados reais (PubMed/MEDLINE)

Edite `Entrez.email` no início de `scripts/01_busca_ranqueamento_pubmed.py` para o seu e-mail (exigência da NCBI para uso da API) e execute a partir da raiz do repositório:

```bash
python scripts/01_busca_ranqueamento_pubmed.py
```

Isso reproduz a busca descrita no TCC (mesma string de busca, campos Title/Abstract, filtro 2015–presente) diretamente na API pública do NCBI, gera `data/processed/pubmed_results_2015_2025.csv`, aplica o algoritmo de ranqueamento e anotação automática, e produz `data/processed/top100_miRNA_AD_PD_annotated.csv` mais os gráficos descritivos em `results/figures/`.

**Nota sobre o tamanho do corpus:** o parâmetro `MAX_RESULTS` do script (originalmente 1.000) define quantos registros são efetivamente baixados nesta execução; o número total de registros existentes no PubMed para essa query cresce continuamente (era de 2.777 registros em 2026-09-10, ver `data/raw/pubmed/manifest.json`). Isso é esperado — literatura nova é publicada todos os meses — e não representa inconsistência dos dados.

### 3. Estatística, bioinformática e modelagem

Após a etapa anterior:

```bash
python scripts/02_estatistica_bioinformatica_modelagem.py
```

Gera o teste qui-quadrado, extração/ranking de miRNAs, matrizes miRNA×doença e artigo×miRNA, PCA, clustering K-means, rede miRNA–doença, as simulações por equações diferenciais ordinárias (vias AD, PD e modelo integrado) e os três heatmaps quantitativos, salvando as figuras em `results/figures/`.

### 4. Dados brutos incluídos no repositório

`data/raw/pubmed/` contém uma **amostra real de validação** (100 artigos, obtidos diretamente da API do NCBI/PubMed em 2026-09-10, sem nenhuma edição, estimativa ou geração sintética) que comprova a reprodutibilidade da etapa de coleta sem exigir nova chamada à API. Ver `data/raw/pubmed/manifest.json` para a proveniência completa (query exata, data de acesso, contagem total real na fonte, ferramenta usada). Para o corpus completo utilizado nas análises do TCC, execute o Script 01.

## Limitações conhecidas e próximos passos

Consulte `docs/PLANO_DE_ACAO_ARTIGO_ALTO_IMPACTO.md` para o diagnóstico completo de lacunas metodológicas e o plano faseado de elevação deste trabalho a um manuscrito submetido a periódico de alto impacto, incluindo: ampliação real da cobertura Scopus/Web of Science, meta-análise quantitativa de acurácia diagnóstica, reanálise de dados públicos de expressão gênica/miRNA (GEO), validação cruzada de alvos (TargetScan/miRDB/DIANA-TarBase) e enriquecimento funcional de vias (KEGG/Reactome).

## Boas práticas científicas e uso de IA

Este projeto segue os princípios de integridade, transparência e reprodutibilidade do Guia de Boas Práticas Científicas da USP (2025). Ferramentas de inteligência artificial foram utilizadas como apoio à organização, análise e redação, nunca como substituto da curadoria de dados e da interpretação científica do autor. Nenhum dado experimental, bibliográfico ou numérico apresentado neste repositório foi fabricado, estimado sem indicação explícita, ou apresentado como resultado real sem procedência rastreável.

## Citação

CAPUCHO, W. Epigenética e microRNAs em doenças neurodegenerativas. GitHub, 2026. Disponível em: <https://github.com/WesleyCapucho/-Epigen-tica-e-micrornas-em-doen-as-neurodegenerativas>.
