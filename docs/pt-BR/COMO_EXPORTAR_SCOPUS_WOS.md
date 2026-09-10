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

## Passo 3 — Web of Science (se tiver acesso)

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

Exporte como **Tab-delimited file** ou **RIS**, incluindo *Full Record*.

## Passo 4 — Enviar os arquivos

Envie os arquivos exportados. O pipeline então roda:

```bash
python scripts/09_ingest_scopus_wos.py --scopus scopus_AD.csv --arm AD
python scripts/09_ingest_scopus_wos.py --scopus scopus_PD.csv --arm PD
python scripts/04_screening.py
python scripts/05_meta_analysis.py
python scripts/06_citation_vs_performance.py
python scripts/08_verify_reported_numbers.py
```

O script `09` deduplica os novos registros contra o corpus do PubMed por DOI, PubMed ID e título normalizado, e reporta quantos registros cada base acrescentou de fato.

## O que muda no manuscrito depois disso

Três coisas, todas para melhor:

1. A frase "Scopus e Web of Science não foram consultadas" sai da seção de Métodos e da lista de limitações, substituída pelas contagens reais.
2. O fluxograma PRISMA passa a ter as três bases, com números rastreáveis.
3. Qualquer estudo novo que reporte AUC e tamanhos de grupo entra na meta-análise, e as estimativas agregadas são recalculadas — inclusive, possivelmente, mudando os valores que hoje estão no manuscrito. O script `08` garante que o texto não fique defasado em relação às novas tabelas.

Vale dizer com franqueza: se os novos registros trouxerem estimativas com desempenho sistematicamente diferente, as conclusões podem se deslocar. É esse o ponto de completar a busca — e não haveria sentido em fazê-la se o resultado já estivesse decidido.
