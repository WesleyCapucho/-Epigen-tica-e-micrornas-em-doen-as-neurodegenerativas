# Pedido de extração externa

**Estado em 23/09/2026.** Você já enviou três PDFs e as três tabelas suplementares do
Wilhelm. O que saiu deles está em `data/extracted/kinetic_parameters.csv` (K043 a K057).
**Falta um único item: o Doxakis 2010 inteiro.**

---

## Ainda faltando

### A. Doxakis 2010, *J Biol Chem* — miR-7/miR-153 e α-sinucleína

PMID 20106983 · DOI 10.1074/jbc.M109.086827 · **artigo inteiro ainda não enviado**

Preciso de:
- a queda de proteína de α-sinucleína com superexpressão de miR-7, e de miR-153,
  **em percentual ou fold**, com n e p;
- a queda de mRNA nas mesmas condições;
- o efeito dos dois juntos (o artigo diz que é aditivo — preciso do número);
- o aumento de luciferase com inibição de miR-7/miR-153 em neurônios primários;
- o sistema celular e o tempo após transfecção de cada medida.

### B. Tushev 2018 — tabela suplementar com meia-vida por gene (opcional)

O PDF enviado traz a mediana (7,38 h), mas não os genes individuais. Se houver uma
tabela suplementar com meia-vida por isoforma de 3'UTR, preciso saber se **Bace1**,
**Snca** e **App** aparecem, e com que valor. Se não aparecerem, isso também é
resposta: a lacuna K030 continua registrada como lacuna.

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
| Wilhelm 2014, *Science* | K050 volume do botão, 0,37 µm³; K052 α+β-sinucleína 6525,67 cópias; K053 razão α:β de 0,98:1; K054 α-sinucleína derivada, 21,6 µM; K055 BACE1 115,84 cópias; K056 APP 6283,6 cópias; K057 volume mitocondrial 0,12 µm³ |

A lacuna do número de cópias da α-sinucleína (K051) foi fechada pela tabela S1 e a
linha saiu da tabela. A ressalva que eu havia levantado estava certa: o número é de
α **mais** β juntas, e a nota de rodapé 1 da tabela dá a razão entre elas (0,98:1),
que é o que permite separar. Sem essa nota, o valor combinado teria superestimado a
α-sinucleína em duas vezes.

Os PDFs dos artigos não são versionados no repositório: só os dados extraídos e as
citações. A tabela S1 é tabela de dados suplementares e está arquivada em
`data/raw/kinetics_2026/wilhelm_2014_table_S1.xlsx`, para que as verificações rodem.
