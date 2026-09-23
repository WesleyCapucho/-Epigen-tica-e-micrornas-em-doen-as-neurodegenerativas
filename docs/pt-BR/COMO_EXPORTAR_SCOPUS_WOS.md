# Como exportar do Scopus e da Web of Science

🇬🇧 English version: [../en/HOW_TO_EXPORT_SCOPUS_WOS.md](../en/HOW_TO_EXPORT_SCOPUS_WOS.md)

---

## Por que esta etapa é manual

Scopus e Web of Science exigem autenticação institucional. Não há API pública para elas neste projeto, e o ambiente que roda estas análises não alcança `scopus.com` nem `webofscience.com`. A rota suportada é a que revisores sistemáticos já usam no dia a dia: rodar a busca na base, exportar o conjunto de resultados e entregar o arquivo ao pipeline.

Isso leva poucos minutos e fecha a única lacuna metodológica declarada da revisão.

---

## Passo 1 — Rodar a busca no Scopus

Entre no Scopus autenticado, vá em **Search → Advanced document search** e cole exatamente a string abaixo.

### Braço Alzheimer

```
TITLE-ABS-KEY (
  ( microrna OR mirna OR micrornas OR mirnas )
  AND alzheimer
  AND ( plasma OR serum OR "cerebrospinal fluid" OR csf OR blood
        OR exosome OR exosomal OR "extracellular vesicle" )
  AND ( roc OR "area under the curve" OR auc OR sensitivity OR specificity
        OR "diagnostic accuracy" OR "diagnostic value" )
)
AND PUBYEAR > 2014
```

### Braço Parkinson

```
TITLE-ABS-KEY (
  ( microrna OR mirna OR micrornas OR mirnas )
  AND parkinson
  AND ( plasma OR serum OR "cerebrospinal fluid" OR csf OR blood
        OR exosome OR exosomal OR "extracellular vesicle" )
  AND ( roc OR "area under the curve" OR auc OR sensitivity OR specificity
        OR "diagnostic accuracy" OR "diagnostic value" )
)
AND PUBYEAR > 2014
```

**Anote o número total de resultados de cada braço.** Ele entra no fluxograma PRISMA e precisa ser o número que a base mostrou, não uma estimativa.

> Uma diferença esperada: o campo `TITLE-ABS-KEY` do Scopus também varre as palavras-chave, enquanto o `[Title/Abstract]` do PubMed não. O Scopus tende, por isso, a retornar mais registros. Isso não é erro — é diferença de escopo entre as bases, e será documentada como tal.

## Passo 2 — Exportar

1. Marque **Select all** (o seletor no topo da lista de resultados).
2. Clique em **Export**.
3. Formato: **CSV** (ou RIS — o pipeline aceita os dois).
4. Em *Customize export*, marque no mínimo estes campos:

| Grupo | Campos |
|---|---|
| Citation information | Author(s), Document title, Year, Source title, Volume/Issue/Pages, **DOI**, **PubMed ID**, Document type |
| Bibliographical information | — |
| Abstract & keywords | **Abstract**, Author keywords, Index keywords |

O **resumo é obrigatório**: a triagem o lê. Sem ele, o registro entra no fluxo, mas não pode ser triado, e o script avisa.

5. Salve os dois arquivos, um por braço. Sugestão de nome: `scopus_AD.csv` e `scopus_PD.csv`.

## Passo 3 — Web of Science (esta é a que ainda falta)

A Scopus já foi buscada e ingerida nos dois braços. A Web of Science **não**, e ela é a última lacuna declarada da busca. O `webofscience.com` foi tentado a partir deste ambiente e está inalcançável pela mesma razão da Scopus: só responde a uma sessão institucional autenticada. Nada mais está travando — o caminho de ingestão, a desduplicação e os reprocessamentos seguintes estão todos prontos e testados.

Em **Advanced Search**, campo `TS=` (Topic):

```
TS=( ( microRNA OR miRNA OR microRNAs OR miRNAs )
     AND Alzheimer
     AND ( plasma OR serum OR "cerebrospinal fluid" OR CSF OR blood
           OR exosome OR exosomal OR "extracellular vesicle" )
     AND ( ROC OR "area under the curve" OR AUC OR sensitivity OR specificity
           OR "diagnostic accuracy" OR "diagnostic value" ) )
```

Com **Timespan 2015–2026**. Troque `Alzheimer` por `Parkinson` no segundo braço.

Exporte como **Tab-delimited file** ou **RIS**, incluindo *Full Record*. Sugestão de nome: `wos_AD.txt` e `wos_PD.txt`. Exporte o conjunto inteiro de resultados, não a primeira página: uma exportação truncada em 500 ou 1000 registros enviesaria o corpus em silêncio, e nada adiante consegue detectar isso.

## Passo 4 — Enviar os arquivos

Envie os arquivos exportados. O pipeline então roda:

```bash
python scripts/09_ingest_scopus_wos.py --wos wos_AD.txt --arm AD
python scripts/09_ingest_scopus_wos.py --wos wos_PD.txt --arm PD
python scripts/04_screening.py
python scripts/10_build_screening_corpus.py
python scripts/05_meta_analysis.py
python scripts/06_citation_vs_performance.py
python scripts/14_quadas2_risk_of_bias.py
python scripts/15_bivariate_srocc.py
python scripts/16_grade_certainty.py
python scripts/08_verify_consistency.py
```

O script `09` deduplica os novos registros contra o corpus do PubMed por DOI, PubMed ID e título normalizado, e reporta quantos registros cada base acrescentou de fato.

## O que muda daí para a frente

Três coisas, todas para melhor:

1. A frase "a Web of Science não foi consultada" sai da seção de Métodos e da lista de limitações, substituída pelas contagens reais. Hoje ela é a única limitação de base que resta.
2. O fluxograma PRISMA passa a ter as três bases, com números rastreáveis.
3. Qualquer estudo novo que reporte AUC e tamanhos de grupo entra na meta-análise, e as estimativas agregadas são recalculadas — inclusive, possivelmente, mudando os valores já publicados. O script `08` garante que a tabela de extração, as contagens PRISMA e as tabelas de resultado não fiquem defasadas entre si.

Uma quarta coisa muda e é fácil de não notar: todo estudo novo entra também no QUADAS-2, no modelo bivariado e na classificação GRADE, então a certeza da evidência é recalculada junto. Se a Web of Science trouxer estudos com confirmação neuropatológica ou cegamento declarado, o rebaixamento por risco de viés pode se mover.

Vale dizer com franqueza: se os novos registros trouxerem estimativas com desempenho sistematicamente diferente, as conclusões podem se deslocar. É esse o ponto de completar a busca — e não haveria sentido em fazê-la se o resultado já estivesse decidido.
