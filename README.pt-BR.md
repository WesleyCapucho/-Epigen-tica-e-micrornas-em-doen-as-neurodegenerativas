# Epigenética e microRNAs em doenças neurodegenerativas

**Os microRNAs de que a área mais fala funcionam mesmo como biomarcadores diagnósticos?**

Revisão sistemática e meta-análise de efeitos aleatórios da acurácia diagnóstica de microRNAs circulantes na doença de Alzheimer (AD) e na doença de Parkinson (PD), com pipeline totalmente reprodutível da busca na literatura até a estimativa agregada.

> 🇬🇧 **English version: [README.md](README.md)**

**Autor:** Wesley Felipe Capucho · **Orientadora:** Profa. Dra. Roberta Sessa Stilhano Yamaguchi
Universidade Federal de São Paulo (UNIFESP) — Especialização em Fisiologia e Fisiopatologia Humana aplicada às Ciências da Saúde.

---

## O que há neste repositório

Este repositório nasceu como apêndice computacional de uma monografia que combinava revisão integrativa, análise bibliométrica e modelagem por equações diferenciais de vias de miRNA em AD e PD. Ele está sendo estendido para um manuscrito com síntese quantitativa primária. Dois corpos de trabalho distintos convivem aqui:

| Camada | O que é | Situação |
|---|---|---|
| **Camada bibliométrica** | Mineração de corpus do PubMed, extração de miRNAs, PCA, agrupamento, rede miRNA–doença, modelos exploratórios por EDO dos eixos miR-29/BACE1/Aβ e miR-7/SNCA/α-sinucleína | Da monografia original (`scripts/01`, `scripts/02`) |
| **Camada meta-analítica** | Busca sistemática orientada por PICO, triagem PRISMA, extração de dados de texto completo, meta-análise de efeitos aleatórios da AUC, panorama de translação clínica | Nova (`scripts/03`–`scripts/07`) |

A camada meta-analítica existe para responder a uma questão que a própria monografia levantou sobre si mesma: frequência bibliométrica e validação experimental não são fontes de evidência independentes, porque os miRNAs mais estudados acumulam as duas coisas. Medir a acurácia diagnóstica agregada rompe essa circularidade.

## Principais achados

Todos os valores são agregados a partir de estimativas publicadas, por efeitos aleatórios de DerSimonian–Laird na escala logito(AUC). Cada valor de entrada é rastreável até uma frase verbatim do artigo-fonte (`data/extracted/diagnostic_accuracy_extraction.csv`).

| Subgrupo | AUC agregada (IC 95%) | Estimativas | Estudos | I² |
|---|---|---|---|---|
| Global | 0,807 (0,745–0,857) | 25 | 16 | 93% |
| Doença de Alzheimer | 0,842 (0,788–0,884) | 13 | 10 | 77% |
| Doença de Parkinson | 0,753 (0,621–0,850) | 12 | 6 | 94% |
| **miRNA isolado** | **0,758 (0,706–0,804)** | 17 | 10 | 66% |
| **Painel multi-miRNA** | **0,888 (0,829–0,928)** | 8 | 7 | 85% |
| AD, miRNA isolado | 0,802 (0,741–0,851) | 7 | 6 | 63% |
| PD, miRNA isolado | 0,716 (0,640–0,781) | 10 | 4 | 55% |

Cinco resultados sustentam o argumento:

1. **miRNAs circulantes isolados ficam na fronteira da utilidade clínica.** Com AUC de 0,758 (IC 0,706–0,804), a estimativa agregada fica abaixo do patamar de ~0,80 usualmente tratado como mínimo para um teste diagnóstico autônomo, com o limite superior apenas o alcançando — e em nada próxima dos ensaios plasmáticos consolidados de p-tau.

2. **Painéis vão substancialmente melhor, e a diferença não é ruído.** Os intervalos de confiança de miRNAs isolados (0,706–0,804) e de painéis (0,829–0,928) não se sobrepõem. O ganho está em combinar marcadores, e não em achar um marcador isolado melhor. Isso concorda com ao menos três meta-análises anteriores — evidência convergente, e não descoberta nova.

3. **A atenção da literatura corre em sentido inverso ao desempenho medido.** Entre os miRNAs com dados de acurácia extraíveis, a correlação entre quantos artigos do corpus mencionam um miRNA e a AUC reportada é **ρ = −0,61 (p = 0,012)** entre as estimativas elegíveis (ρ = −0,27; p = 0,16 no conjunto). Os dois miRNAs mais discutidos no corpus, miR-125b (13 artigos) e miR-146a (11 artigos), retornaram AUCs de 0,75 e 0,68 — a parte baixa da distribuição. Dezesseis miRNAs contribuem, então segue exploratório, mas aponta na direção contrária à ênfase da área. É o único achado aqui sem precedente claro.

4. **Nada chegou à clínica.** O ClinicalTrials.gov (10/09/2026) lista 16 ensaios registrados de terapias dirigidas a miRNA no mundo — em hepatite C, oncologia e dermatologia — e **zero** em Alzheimer ou Parkinson. Notavelmente, um mimético de miR-29 (MRG-201/remlarsen) chegou à Fase 2, para queloide, por injeção intradérmica. miR-29 é exatamente o eixo que a monografia de origem simulou como terapia cerebral: a classe molecular existe, a via até o cérebro não.

5. **Acrescentar uma base derrubou duas conclusões.** Uma primeira versão desta revisão consultou apenas o PubMed e encontrou o subgrupo de miRNA isolado em AD homogêneo (I² = 0%), o que lemos como evidência de que o teto era real, e não metodológico. O braço AD do Scopus então acrescentou 248 registros que o PubMed não retornara; um deles levou esse subgrupo a I² = 63%. A homogeneidade era artefato de uma busca incompleta. A Seção 8 de `docs/pt-BR/ACHADOS.md` registra o que mudou e por quê.

O teste de Egger indica efeitos de estudos pequenos em vários subgrupos, então esses valores agregados devem ser lidos como **limites superiores**, não como estimativas neutras. Seis meta-análises anteriores reportam áreas SROC de 0,87–0,90 para a mesma pergunta; esse é um estimando diferente da média das AUCs reportadas usada aqui, e a Seção 7 de `docs/pt-BR/ACHADOS.md` explica a comparação.

## Estrutura do repositório

```
.
├── data/
│   ├── raw/
│   │   ├── pubmed/                    # Amostra bibliométrica, obtida ao vivo do NCBI (procedência em manifest.json)
│   │   ├── systematic_review_2026/    # Estratégia de busca, decisões de triagem, contagens de menção a miRNAs
│   │   └── clinical_trials_2026/      # Panorama do ClinicalTrials.gov de terapias dirigidas a miRNA
│   ├── extracted/                     # Tabela de extração de acurácia + citações verbatim das fontes
│   └── processed/                     # Saídas do pipeline (fluxo PRISMA; regeneráveis)
├── scripts/
│   ├── 01_busca_ranqueamento_pubmed.py            # Busca bibliométrica + ranqueamento (monografia original)
│   ├── 02_estatistica_bioinformatica_modelagem.py # Estatística, PCA, redes, modelos EDO (original)
│   ├── 03_systematic_search.py                    # Busca sistemática PICO via NCBI E-utilities
│   ├── 04_screening.py                            # Triagem PRISMA baseada em regras
│   ├── 05_meta_analysis.py                        # Meta-análise de efeitos aleatórios da AUC
│   ├── 06_citation_vs_performance.py              # Atenção da literatura vs acurácia medida
│   ├── 07_clinical_translation_landscape.py       # O que de fato chegou a ensaios clínicos
│   ├── 08_verify_reported_numbers.py              # Confere cada número do texto contra as tabelas
│   └── 09_ingest_scopus_wos.py                    # Funde exportações do Scopus / Web of Science
├── docs/
│   ├── en/                            # Methods, data dictionary, findings (inglês)
│   └── pt-BR/                         # Métodos, dicionário de dados, achados (português)
├── results/
│   ├── figures/                       # Forest plot, gráfico de funil, atenção vs acurácia
│   └── tables/                        # Estimativas agregadas, entradas por estimativa, correlações
└── requirements.txt
```

## Como reproduzir a análise

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Camada 2 — revisão sistemática e meta-análise
python scripts/03_systematic_search.py --email voce@exemplo.org   # exige acesso ao NCBI
python scripts/04_screening.py
python scripts/05_meta_analysis.py
python scripts/06_citation_vs_performance.py
python scripts/07_clinical_translation_landscape.py
```

Os scripts `05` e `06` rodam offline, a partir dos arquivos de dados versionados. O `03` chama a API do PubMed ao vivo e retornará, legitimamente, mais registros do que as contagens congeladas de 10/09/2026, porque a literatura continua crescendo; o arquivo `data/raw/systematic_review_2026/search_strategy.json` preserva as contagens por trás dos números aqui reportados.

Para a camada bibliométrica original, veja `scripts/01` e `scripts/02` (rode o `01` primeiro — ele produz a entrada do `02`).

## Procedência dos dados e integridade

- **Todo número veio de uma fonte real.** Os registros do PubMed foram obtidos pela API E-utilities do NCBI; os valores de acurácia foram lidos em textos completos de acesso aberto no PubMed Central. Nada foi simulado, estimado para preencher lacuna, nem herdado de citação secundária.
- **Todo valor extraído guarda a frase que o sustenta.** O arquivo `diagnostic_accuracy_extraction.csv` tem a coluna `verbatim_quote` com o trecho exato que embasa cada AUC, sensibilidade e especificidade, além de PMID e DOI.
- **Valores que não puderam ser resolvidos sem ambiguidade foram mantidos e sinalizados, não descartados em silêncio.** 14 das 42 linhas extraídas estão marcadas com `eligible_primary_pool = no` e um `exclusion_reason` explícito (comparador composto, contraste intradoença, população prodrômica, separação perfeita instável, coorte não atribuível).
- **A mineração automatizada serviu para *encontrar* candidatos, nunca para registrá-los.** Expressões regulares trouxeram as frases à tona; os valores foram então lidos e transcritos manualmente, porque os padrões comprovadamente trocam sensibilidade por especificidade e confundem valores de p com métricas de acurácia.
- **Publicação duplicada foi verificada.** Os PMIDs 40661348 e 41836608 reportam a mesma coorte e as mesmas AUCs (versão preprint e versão de periódico); contam uma vez só.
- **O método de erro-padrão foi validado contra uma fonte.** Para o PMID 33129241, a fórmula de Hanley–McNeil devolve EP = 0,0822 para AUC 0,75 com 18 vs 18 sujeitos; o artigo reporta, de forma independente, EP = 0,08.

Os textos completos **não** são redistribuídos aqui — apenas os dados extraídos e suas citações. Acesse as fontes pelos DOIs.

## Limitações conhecidas

- A cobertura é assimétrica: PubMed para as duas doenças, mais um braço AD do Scopus. O braço PD do Scopus e a Web of Science não foram consultados, então as estimativas de PD repousam apenas no PubMed e devem ser tratadas como provisórias. O `docs/pt-BR/COMO_EXPORTAR_SCOPUS_WOS.md` traz as queries prontas; o `scripts/09_ingest_scopus_wos.py` funde novas exportações e as deduplica.
- A extração de dados se restringe a textos completos de acesso aberto no PubMed Central (55 dos 95 estudos primários elegíveis), o que pode, por si só, selecionar um subconjunto não aleatório da literatura.
- A heterogeneidade é alta (I² até 94%) e o teste de Egger é significativo em vários subgrupos; as estimativas agregadas são mais bem lidas como limites otimistas.
- A maioria dos miRNAs contribui com um único estudo, então a análise de atenção versus desempenho é exploratória e não sustenta leitura causal.
- Os modelos EDO do `scripts/02` usam parâmetros ilustrativos, não calibrados. São qualitativos e geradores de hipóteses; não são predições quantitativas e não devem ser reportados como tal.

## Integridade científica e uso de IA

Este trabalho segue os princípios de transparência e reprodutibilidade do Guia de Boas Práticas Científicas da USP (2025). Ferramentas de IA auxiliaram na organização, no código, na recuperação de literatura e na redação; não substituíram a curadoria dos dados, a conferência contra as fontes, nem o julgamento científico do autor. Nenhum dado foi fabricado. Quando um valor não pôde ser verificado contra sua fonte, foi excluído e a exclusão foi registrada.

## Como citar

Capucho, W. *Epigenética e microRNAs em doenças neurodegenerativas: revisão sistemática e meta-análise da acurácia diagnóstica de miRNAs circulantes.* GitHub, 2026. https://github.com/WesleyCapucho/-Epigen-tica-e-micrornas-em-doen-as-neurodegenerativas

Os dados de literatura vêm do PubMed/PubMed Central (National Library of Medicine, NCBI). Os estudos individuais estão citados por DOI em `data/extracted/diagnostic_accuracy_extraction.csv`.
