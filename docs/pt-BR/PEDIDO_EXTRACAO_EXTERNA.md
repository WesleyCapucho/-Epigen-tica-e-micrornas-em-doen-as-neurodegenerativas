# Pedido de extração externa

**Estado em 23/09/2026.** Você já enviou três PDFs e as três tabelas suplementares do
Wilhelm. O que saiu deles está em `data/extracted/kinetic_parameters.csv` (K043 a K065).
**Nada é obrigatório.** Restou um item opcional, abaixo, com o ganho esperado explicitado.

---

## Ainda faltando

### Tushev 2018 — Tabela S1 (dados processados, meia-vida por isoforma)

Artigo: DOI 10.1016/j.neuron.2018.03.030 · PMID 29656876 · Neuron 98:495-511

**Onde está.** Na mesma página de onde você tirou o `mmc6.pdf`, em *Supplemental
Information*. O artigo diz, na seção **DATA AND SOFTWARE AVAILABILITY**:

> "The accession number for the raw sequencing data reported in this paper is NCBI
> BioProject: PRJNA390472. **Processed data used for analyses in this manuscript are
> included in Table S1.**"

O suplemento tem oito figuras e **cinco tabelas**. O `mmc6.pdf` que você mandou traz as
figuras S1–S8 e a Tabela S5 (primers). As Tabelas S1–S4 são arquivos Excel separados,
provavelmente `mmc2.xlsx` a `mmc5.xlsx`. **A que interessa é a S1.** Se não der para
saber qual arquivo é qual pelo nome, baixe todos os `.xlsx` e me mande — eu identifico.

**O que preciso saber dela:** se existe uma coluna de meia-vida (em horas) por isoforma
de 3'UTR, e se **Bace1**, **Snca** e **App** aparecem, com que valor e com qual isoforma.

**O que isso muda, para você decidir se vale o esforço.** Fecharia a última lacuna
declarada (K030) e transformaria um parâmetro livre do modelo num valor medido. Não
mexe em nenhum dos resultados principais: a razão de Aβ na DA é invariante a parâmetros
livres, e a eliminação do mimético, a saturação da α-sinucleína e a cadeia miR-7 →
elongação não dependem do decaimento de mRNA. O ganho concreto é estreitar a faixa de
19–33% da queda de BACE1 exigida. É melhoria real, mas não é resultado novo.

**Se os genes não estiverem lá, isso também é resposta.** A K030 continua lacuna
declarada, agora com uma segunda fonte conferida em vez de uma.

---

## Regras para a resposta

Para cada item, devolva **uma linha por número**, neste formato:

```
parametro | valor exatamente como impresso | unidade | n | condição experimental | espécie/sistema | frase verbatim | seção/figura/tabela onde está
```

- A **frase verbatim** tem de conter o número. Se o número só existir numa figura sem valor no texto, escreva `apenas em figura, sem valor numérico no texto`.
- Se o artigo não traz o número, escreva `não consta` e diga onde procurou (seções e material suplementar conferidos).
- Não estime, não interpole, não converta unidades e não use resumo nem artigo de revisão. Só o texto completo e o suplementar.

---

## Já resolvido (não precisa refazer)

| Fonte | O que entrou na tabela |
|---|---|
| Tushev 2018, *Neuron* | K043 mediana de meia-vida de mRNA em neurônio, 7,38 h; K044 mediana em glia, 4,89 h |
| Hébert 2008, *PNAS* | K045 miR-29b-1 a 0,60 do controle (p = 0,02751); K046 replicação por qRT-PCR; K047 queda de ~50% da BACE1; K048 queda de ~50–80% em Aβ e sAPPβ; K049 ~30% dos casos de DA esporádica com BACE1 alta |
| Doxakis 2010, *JBC* | K058 miR-7 baixa a SNCA em 30%; K059 miR-153 em 19%; K060 os dois em 46%; K061/K062 mRNA em 15% e 50%; K063 SNCA endógena em neurônios corticais, 43%; K064 réplica em hipocampo, ~30–40%; K065 bloqueio dos miRNAs endógenos eleva o repórter em 44% |
| Wilhelm 2014, *Science* | K050 volume do botão, 0,37 µm³; K052 α+β-sinucleína 6525,67 cópias; K053 razão α:β de 0,98:1; K054 α-sinucleína derivada, 21,6 µM; K055 BACE1 115,84 cópias; K056 APP 6283,6 cópias; K057 volume mitocondrial 0,12 µm³ |

A lacuna do número de cópias da α-sinucleína (K051) foi fechada pela tabela S1 e a
linha saiu da tabela. A ressalva que eu havia levantado estava certa: o número é de
α **mais** β juntas, e a nota de rodapé 1 da tabela dá a razão entre elas (0,98:1),
que é o que permite separar. Sem essa nota, o valor combinado teria superestimado a
α-sinucleína em duas vezes.

Os PDFs dos artigos não são versionados no repositório: só os dados extraídos e as
citações. A tabela S1 é tabela de dados suplementares e está arquivada em
`data/raw/kinetics_2026/wilhelm_2014_table_S1.xlsx`, para que as verificações rodem.
