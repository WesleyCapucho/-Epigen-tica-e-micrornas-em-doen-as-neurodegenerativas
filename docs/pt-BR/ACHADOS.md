# Achados

*O que a evidência agregada diz sobre microRNAs circulantes como biomarcadores diagnósticos na doença de Alzheimer e na de Parkinson.*

🇬🇧 English version: [../en/FINDINGS.md](../en/FINDINGS.md)

---

## 1. O que foi sintetizado

Foram triados 234 registros únicos; 189 eram estudos primários; 95 reportaram AUC ou par sensibilidade–especificidade; 45 textos completos foram lidos; 26 estudos renderam 42 estimativas extraíveis, das quais 28 atenderam às regras de elegibilidade e 24 (de 15 estudos independentes) tinham erro-padrão estimável e puderam ser ponderadas.

Vale dizer a perda com todas as letras: **menos de um em cada dez registros triados terminou contribuindo com uma estimativa ponderada.** A maior parte dessa perda não é obra do revisor. Vem de estudos que reportam AUC sem os tamanhos de grupo ou o intervalo de confiança necessários para ponderá-la, de textos completos trancados atrás de assinaturas, e de comparações que soam como "AD versus controles" mas, na leitura, são outra coisa.

## 2. miRNAs isolados não alcançam utilidade clínica

A AUC agregada de um miRNA circulante isolado é **0,745 (IC 95% 0,699–0,785)**, em 16 estimativas de 9 estudos.

Esse número precisa ser lido contra o que ele teria de superar. Uma AUC em torno de 0,80 é o piso convencional para um teste diagnóstico autônomo; os ensaios plasmáticos consolidados de fosfo-tau para AD ficam bem acima de 0,90. Um valor agregado de 0,745, com limite superior de 0,785, não alcança o piso — o intervalo inteiro fica abaixo de 0,80.

O subgrupo de miRNA isolado em AD é o resultado mais informativo da análise, porque é o que tem **I² = 0%**. Seis estimativas de cinco estudos diferentes, em biofluidos diferentes, em plataformas diferentes, convergem para 0,774 (0,732–0,810) sem heterogeneidade detectável entre estudos. Não se trata de uma literatura ruidosa que talvez contenha um sinal forte, se apenas fosse mais bem medida. Trata-se de um efeito consistente, bem replicado e *modesto*. Consistência em um valor mediano é um resultado mais desanimador do que inconsistência, porque retira a esperança de que melhor metodologia moveria a estimativa.

Os miRNAs isolados em PD agregam ainda mais baixo, em 0,716 (0,641–0,781), com heterogeneidade moderada (I² = 55%).

## 3. O ganho está nos painéis, e a diferença não é ruído

Painéis multi-miRNA agregam em **0,888 (0,829–0,928)** — e os intervalos de confiança dos dois tipos de marcador não se sobrepõem:

| | AUC agregada | IC 95% |
|---|---|---|
| miRNA isolado | 0,745 | 0,699 – 0,785 |
| Painel multi-miRNA | 0,888 | 0,829 – 0,928 |

Intervalos que não se sobrepõem constituem um teste conservador, e esta comparação passa nele. A leitura prática é direcional: o movimento produtivo é combinar marcadores, e não seguir procurando um marcador individual melhor. Isso é coerente com a biologia que a monografia de origem defendeu — miRNAs atuam como moduladores de rede, cada um com alavancagem individual modesta sobre muitos alvos — mas aqui o argumento chega como efeito medido, e não como inferência a partir do mecanismo.

Duas ressalvas acompanham a estimativa dos painéis. A heterogeneidade é alta (I² = 85%), e painéis são justamente o tipo de marcador mais exposto a sobreajuste: muitos derivam seus pesos e seu ponto de corte na mesma amostra em que reportam desempenho. O número dos painéis é, portanto, o que tem maior probabilidade de encolher sob validação externa.

## 4. A atenção da área aponta para longe do desempenho

Contar quantos artigos do corpus mencionam cada miRNA e correlacionar isso com sua AUC medida resulta em:

- em todas as estimativas de miRNA isolado: ρ de Spearman = −0,11 (p = 0,62)
- restrito às estimativas elegíveis para o pool primário: **ρ = −0,41 (p = 0,14)**

Nenhum é estatisticamente significativo e, com a maioria dos miRNAs contribuindo com um único estudo, o teste tem baixo poder — um resultado nulo aqui não é evidência de ausência de associação, e o coeficiente negativo é um sinal para investigar, não uma conclusão.

Mas o padrão nos valores individuais é difícil de ignorar:

| miRNA | Artigos que o mencionam | AUC reportada |
|---|---|---|
| miR-125b | 13 | 0,753 |
| miR-146a | 11 | 0,680 |
| miR-34a | 10 | 0,738 |
| … | | |
| miR-128 | 2 | 0,831 |
| let-7i | 1 | 0,835 |
| miR-501 | 1 | 0,820 |

Os dois miRNAs mais discutidos do corpus ficam na *base* da distribuição de desempenho, e três dos melhores desempenhos são quase não discutidos. O miR-146a em particular — uma das moléculas-âncora da narrativa amiloide-inflamatória, e um dos dois eixos modelados na monografia de origem — devolve a menor AUC do conjunto elegível.

Esta é a resposta quantitativa ao problema de circularidade que a monografia levantou sobre si mesma. Frequência bibliométrica e validação experimental catalogada seguem ambas a atenção prévia da pesquisa, então a concordância entre elas prova pouco. A acurácia diagnóstica agregada é um critério externo e, por esse critério, a correlação com a atenção é ausente ou inversa. Um miRNA se torna proeminente por ser mecanisticamente interessante e fácil de dosar, não por discriminar bem os pacientes.

## 5. Os valores agregados são limites superiores, não estimativas neutras

O teste de Egger é significativo em vários subgrupos, incluindo o pool global e o subgrupo de PD. Somado a duas características estruturais desta literatura — pontos de corte derivados na mesma amostra em que são avaliados, e coortes pequenas (muitas com menos de 50 por braço) —, a direção do viés é previsível e de mão única.

Toda cifra agregada nesta análise deve, portanto, ser lida como **a ponta otimista** da faixa plausível. Isso importa sobretudo para o resultado principal: se 0,745 já é a estimativa otimista para um miRNA isolado, a cifra realista é menor.

## 6. O que decorre disso

**Para o desenvolvimento de biomarcadores.** Artigos de miRNA isolado reportando AUC perto de 0,75 estão reportando o valor central da área, não uma descoberta. A evidência sustenta investir em painéis, em comparação direta com p-tau217 em vez de comparação contra nenhum comparador, e em coortes de validação externa nas quais o ponto de corte seja fixado de antemão.

**Para como esta literatura é lida.** Frequência de menção não é evidência de desempenho e, neste corpus, pode estar levemente anticorrelacionada com ele. Revisões que ranqueiam candidatos a miRNA pela frequência com que aparecem estão ranqueando por atenção.

**Para as práticas de reporte.** A maior causa isolada de perda de dados aqui foram estudos que publicaram uma AUC sem os tamanhos de grupo ou o intervalo de confiança necessários para ponderá-la. Essa omissão remove o estudo de toda meta-análise futura. Reportar o n por braço junto de cada resultado de ROC não custa nada e melhoraria materialmente a evidência cumulativa da área.

**Para a camada de modelagem da monografia de origem.** Os modelos por EDO construídos sobre os eixos miR-29/BACE1/Aβ e miR-7/SNCA/α-sinucleína seguem úteis como estruturas qualitativas e geradoras de hipóteses. O que esta análise acrescenta é uma condição de contorno: os miRNAs no centro desses modelos não são, pela evidência atual, discriminadores individuais fortes da doença. Isso não os invalida como reguladores mecanísticos — importância regulatória e discriminação diagnóstica são afirmações distintas — mas significa que o argumento diagnóstico em favor deles precisa ser feito com painéis, e não com marcadores isolados.

## 7. Limitações honestas

- Apenas PubMed/MEDLINE; Scopus e Web of Science não foram consultadas.
- Extração limitada a textos completos de acesso aberto no PubMed Central (55 de 95 estudos primários elegíveis), uma fatia potencialmente não aleatória.
- 24 estimativas ponderadas de 15 estudos é uma base de evidência modesta; as células de subgrupo são ainda menores (painéis em PD: k = 2).
- Heterogeneidade de até I² = 95% em alguns subgrupos.
- A análise de atenção versus desempenho é exploratória e com baixo poder.
- Acurácia reportada não é acurácia clínica prospectiva.
