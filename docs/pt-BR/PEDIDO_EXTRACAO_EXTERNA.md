# Pedido de extração externa (4 artigos)

Use este texto no Claude do Chrome, com as sessões institucionais abertas. Um artigo por vez.

## Regras para a resposta

Para cada item, devolva **uma linha por número**, neste formato:

```
parametro | valor exatamente como impresso | unidade | n | condição experimental | espécie/sistema | frase verbatim | seção/figura/tabela onde está
```

- A **frase verbatim** tem de conter o número. Se o número só existir numa figura sem valor no texto, escreva `apenas em figura, sem valor numérico no texto`.
- Se o artigo não traz o número, escreva `não consta` e diga onde procurou (seções e material suplementar conferidos).
- Não estime, não interpole, não converta unidades e não use resumo nem artigo de revisão. Só o texto completo e o suplementar.

## 1. Tushev et al. 2018, *Neuron* — meias-vidas de mRNA em compartimentos neuronais

PMID 29656876 · DOI 10.1016/j.neuron.2018.03.030

Preciso de:
- meia-vida (ou taxa de decaimento) de mRNA nos compartimentos **soma** e **neuropil**, com a mediana de cada um;
- o método de medida da estabilidade e a duração do experimento;
- se aparecerem, os valores para **Bace1**, **Snca**, **App** (qualquer isoforma de 3' UTR);
- tabelas suplementares que tragam meia-vida por gene: diga o nome do arquivo e da coluna.

## 2. Hébert et al. 2008, *PNAS* — miR-29a/b-1 e BACE1

PMID 18434550 · DOI 10.1073/pnas.0710263105

Preciso dos números, não da direção do efeito:
- quanto o cluster miR-29a/b-1 está reduzido nos pacientes (valor, unidade, n de pacientes e de controles, teste e p);
- quanto a proteína BACE1 está aumentada nos mesmos cérebros;
- o efeito de miR-29a, miR-29b-1 e miR-9 sobre BACE1 in vitro (percentual ou fold, com n e p);
- o efeito sobre Aβ no modelo em cultura (percentual ou fold, com n e p).

## 3. Doxakis 2010, *J Biol Chem* — miR-7/miR-153 e α-sinucleína

PMID 20106983 · DOI 10.1074/jbc.M109.086827

Preciso de:
- a queda de proteína de α-sinucleína com superexpressão de miR-7, e de miR-153, **em percentual ou fold**, com n e p;
- a queda de mRNA nas mesmas condições;
- o efeito dos dois juntos (o artigo diz que é aditivo — preciso do número);
- o aumento de luciferase com inibição de miR-7/miR-153 em neurônios primários;
- o sistema celular e o tempo após transfecção de cada medida.

## 4. Wilhelm et al. 2014, *Science* — cópias de α-sinucleína no botão sináptico

PMID 24876496 · DOI 10.1126/science.1252884

Preciso de:
- número de cópias de **α-sinucleína (SNCA)** por botão sináptico, com desvio e método;
- o volume ou a referência de normalização usada para o botão médio, para eu poder converter cópias em concentração;
- a tabela suplementar com contagem por proteína: nome do arquivo, coluna e a linha da α-sinucleína;
- se a α-sinucleína não estiver na lista quantificada, diga isso explicitamente.

## Como me enviar

Cole as linhas aqui na conversa, ou anexe o PDF e o suplementar. Eu registro na
`data/extracted/kinetic_parameters.csv` e o `scripts/08` confere se cada número
aparece na frase que você trouxe.
