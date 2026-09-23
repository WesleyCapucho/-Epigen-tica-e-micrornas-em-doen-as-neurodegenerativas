# Pedido de extração externa

**Estado em 23/09/2026.** Você enviou quatro PDFs e sete tabelas suplementares. O que
saiu deles está em `data/extracted/kinetic_parameters.csv` (K043 a K069). **A lista está
fechada.**

---

## Nada faltando

Todas as fontes externas pedidas foram entregues e extraídas. A última lacuna declarada
(K030, meias-vidas dos mRNAs de BACE1 e SNCA) foi fechada pela Tabela S1 do Tushev.

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
| Tushev 2018, *Neuron* | K043 mediana em neurônio, 7,38 h; K044 mediana em glia, 4,89 h (não reproduz da tabela — ver ressalva); K066 meia-vida do mRNA de SNCA, 6,53 h; K067 isoforma dominante de BACE1, 17,39 h de cinco; K068 constante agrupada derivada da BACE1; K069 APP, 51,39 h, extrapolação marcada como não usável |
| Hébert 2008, *PNAS* | K045 miR-29b-1 a 0,60 do controle (p = 0,02751); K046 replicação por qRT-PCR; K047 queda de ~50% da BACE1; K048 queda de ~50–80% em Aβ e sAPPβ; K049 ~30% dos casos de DA esporádica com BACE1 alta |
| Doxakis 2010, *JBC* | K058 miR-7 baixa a SNCA em 30%; K059 miR-153 em 19%; K060 os dois em 46%; K061/K062 mRNA em 15% e 50%; K063 SNCA endógena em neurônios corticais, 43%; K064 réplica em hipocampo, ~30–40%; K065 bloqueio dos miRNAs endógenos eleva o repórter em 44% |
| Wilhelm 2014, *Science* | K050 volume do botão, 0,37 µm³; K052 α+β-sinucleína 6525,67 cópias; K053 razão α:β de 0,98:1; K054 α-sinucleína derivada, 21,6 µM; K055 BACE1 115,84 cópias; K056 APP 6283,6 cópias; K057 volume mitocondrial 0,12 µm³ |

A lacuna do número de cópias da α-sinucleína (K051) foi fechada pela tabela S1 e a
linha saiu da tabela. A ressalva que eu havia levantado estava certa: o número é de
α **mais** β juntas, e a nota de rodapé 1 da tabela dá a razão entre elas (0,98:1),
que é o que permite separar. Sem essa nota, o valor combinado teria superestimado a
α-sinucleína em duas vezes.

Duas ressalvas saíram da leitura da Tabela S1 do Tushev, e as duas ficaram registradas:

1. O decaimento foi observado por 16 h. Um quarto das 24.435 isoformas tem meia-vida
   além dessa janela, e as maiores chegam a 18.858 h. A meia-vida de 51,39 h do APP está
   nessa faixa, então é extrapolação, não medida, e a linha diz isso.
2. A mediana publicada para neurônio (7,38 h) se reproduz da tabela quando se excluem
   meias-vidas acima de cerca de 25 h — dá 7,394 h. A da glia (4,89 h) não se reproduz
   com nenhum filtro que testei; o mais próximo foi 6,70 h. A linha K044 passou a avisar
   que deve ser citada como impressa e nunca recalculada.

Os PDFs dos artigos não são versionados no repositório: só os dados extraídos e as
citações. As tabelas de dados suplementares ficam em `data/raw/kinetics_2026/`, para que
as verificações rodem.
