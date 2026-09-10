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

**Bases não consultadas.** Scopus e Web of Science não foram consultadas. Ambas exigem autenticação institucional que o ambiente de análise não conseguia alcançar. Trata-se de uma limitação real de completude, declarada em vez de aproximada — nenhuma contagem estimada de registros é reportada para bases que não foram efetivamente consultadas.

## 3. Triagem

A triagem é baseada em regras e reprodutível (`scripts/04_screening.py`). Cada registro foi classificado em dois eixos:

- **Literatura secundária**, se o tipo de publicação no PubMed fosse Review, Systematic Review, Meta-Analysis, Editorial, Comment, Letter, Erratum ou Retraction, ou se o título/resumo se anunciasse como revisão.
- **Porta dados quantitativos de acurácia**, se o resumo declarasse uma AUC, ou declarasse sensibilidade e especificidade juntas.

Resultados: dos 234 registros triados, **45** eram literatura secundária e **189** eram estudos primários; **95** estudos primários reportaram AUC ou par sensibilidade–especificidade; **55** desses tinham texto completo de acesso aberto no PubMed Central. As decisões por registro estão em `data/raw/systematic_review_2026/screening_decisions.csv`; as contagens são recalculadas para `data/processed/prisma_flow.json`, e não transcritas.

## 4. Extração de dados do texto completo

Os textos completos foram recuperados do PubMed Central para **45 estudos**. A extração seguiu três regras:

**A mineração automatizada localiza candidatos; quem registra os valores é uma pessoa.** Expressões regulares trouxeram à tona cada frase contendo uma métrica de acurácia junto de seu contexto. Essas frases foram então lidas, e os valores transcritos manualmente. Essa divisão de trabalho não é cerimonial: os padrões comprovadamente atribuem sensibilidade ao campo de especificidade quando a frase inverte a ordem, capturam valores de p num campo de especificidade e tratam uma *redução* de AUC em teste de permutação como se fosse uma AUC. Nenhum desses erros sobrevive à leitura da frase, e todos sobreviveriam à captura automática.

**Todo valor guarda a frase que o sustenta.** Cada linha de `data/extracted/diagnostic_accuracy_extraction.csv` carrega a coluna `verbatim_quote`, com o trecho exato da fonte, além de PMID e DOI.

**Valores atribuídos a outros estudos não são extraídos.** Seções de discussão rotineiramente citam AUCs de outros trabalhos ("Han et al. encontraram…", "Wen et al. reportaram…"). Tais frases foram identificadas e excluídas; apenas os resultados próprios de cada estudo foram registrados.

Para cada estimativa foram capturados, quando declarados: miRNA (ou composição do painel), doença, comparação e classe da comparação, biofluido, etapa da coorte (descoberta / treinamento / validação / única), número de casos e de controles, AUC com intervalo de confiança, sensibilidade, especificidade e método de mensuração.

### Elegibilidade para o pool primário

Uma estimativa entra no pool primário apenas se for um **contraste caso-versus-controle em população definida de AD ou PD**. Das 42 estimativas extraídas, **28** qualificaram. As 14 restantes permanecem na tabela com um `exclusion_reason` explícito:

| Motivo | Exemplo |
|---|---|
| Comparador composto | AD discriminada conjuntamente contra FTD *e* controles |
| Contraste intradoença | PD com vs sem comprometimento cognitivo |
| População prodrômica | transtorno comportamental do sono REM isolado, e não PD estabelecida |
| Estratificação por genótipo | portadores de LRRK2, e não PD esporádica |
| População mista | "patologia neurodegenerativa" sem detalhamento por doença |
| Estimativa instável | AUC = 1,000 por separação perfeita em subgrupo de 6 pacientes |
| Coorte não atribuível | AUC reportada sem coorte ou tamanho de grupo resolvível |
| Modelo composto | miRNA combinado com variáveis clínicas não-miRNA |

**Publicação duplicada.** Os PMIDs 40661348 e 41836608 reportam a mesma coorte, os mesmos marcadores e as mesmas AUCs (versão preprint e versão de periódico de um mesmo estudo). O par foi detectado por frases de resultado verbatim idênticas e contado uma única vez.

## 5. Síntese estatística

Implementada em `scripts/05_meta_analysis.py` usando apenas NumPy e SciPy, para que cada etapa seja inspecionável em vez de delegada a um pacote caixa-preta.

**Erros-padrão.** Quando a fonte reportou IC 95%, EP = (superior − inferior) / (2 × 1,96). Caso contrário, o EP foi calculado por Hanley & McNeil (1982) a partir dos tamanhos dos grupos caso e controle. Estimativas sem IC e sem tamanhos de grupo não podem ser ponderadas e ficam fora da agregação — 24 das 28 estimativas elegíveis, de 15 estudos independentes, eram agregáveis. A origem do EP é registrada por estimativa em `results/tables/meta_analysis_input_estimates.csv`.

*Validação desta etapa:* para o PMID 33129241 (AUC 0,75; 18 casos vs 18 controles) a fórmula de Hanley–McNeil devolve EP = 0,0822, contra EP = 0,08 reportado de forma independente pelo próprio artigo.

**Agregação.** As AUCs foram transformadas para a escala logito, na qual são ilimitadas e se aproximam melhor da normalidade, com o EP propagado pelo método delta (EP_logito = EP_AUC / [AUC(1 − AUC)]). As estimativas foram combinadas pelo estimador de efeitos aleatórios de DerSimonian & Laird (1986) e retrotransformadas para reporte. Efeitos aleatórios foram escolhidos a priori: os estudos diferem em biofluido, plataforma, população e derivação do ponto de corte, de modo que uma AUC verdadeira comum não é hipótese plausível.

**Heterogeneidade** é reportada como Q de Cochran com seu valor de p, τ² na escala logito e I².

**Efeitos de estudos pequenos** foram avaliados pela regressão de Egger do desvio normal padronizado sobre a precisão.

**Subgrupos**, pré-especificados: por doença (AD, PD), por tipo de marcador (miRNA isolado vs painel multi-miRNA) e por biofluido quando havia ao menos três estimativas.

## 6. Atenção da literatura versus desempenho medido

`scripts/06_citation_vs_performance.py`. Para cada miRNA, contou-se o número de **artigos distintos** do corpus de 234 registros que o mencionam em título ou resumo. Contar artigos distintos, e não ocorrências brutas, importa: um artigo que escreve tanto "miR-125b" quanto "miR-125b-5p" não pode contar duas vezes para a família miR-125b. Os sufixos de braço (-3p/-5p) foram colapsados ao nível de família, para que uma menção a "miR-146a" possa ser casada com uma estimativa reportada para "miR-146a-5p".

As contagens de menção foram então correlacionadas (Spearman e Pearson) com a AUC média reportada por miRNA. A análise foi rodada duas vezes: sobre todas as estimativas de miRNA isolado e restrita às elegíveis para o pool primário.

Esta análise é **exploratória**. A maioria dos miRNAs contribui com um único estudo, o teste tem baixo poder, e um resultado não significativo não pode ser lido como evidência de ausência de associação.

## 7. O que este desenho não é capaz de entregar

- Ele mede acurácia **reportada**, não acurácia sob uso clínico prospectivo. A maior parte das estimativas incluídas deriva o ponto de corte na mesma amostra em que o avalia, o que infla a AUC.
- A restrição a textos completos de acesso aberto no PubMed Central pode selecionar um subconjunto não aleatório da literatura.
- Com testes de Egger significativos em vários subgrupos, os valores agregados devem ser lidos como **limites superiores**.
- Não havia dados individuais de participantes, então não foi feita modelagem bivariada de sensibilidade–especificidade (HSROC); a síntese é sobre AUC.

## Referências dos métodos

- DerSimonian R, Laird N. Meta-analysis in clinical trials. *Control Clin Trials.* 1986;7(3):177–188.
- Hanley JA, McNeil BJ. The meaning and use of the area under a receiver operating characteristic (ROC) curve. *Radiology.* 1982;143(1):29–36.
- Egger M, Davey Smith G, Schneider M, Minder C. Bias in meta-analysis detected by a simple, graphical test. *BMJ.* 1997;315(7109):629–634.
- Page MJ, McKenzie JE, Bossuyt PM, et al. The PRISMA 2020 statement: an updated guideline for reporting systematic reviews. *BMJ.* 2021;372:n71.
