# Atenção sem acurácia: microRNAs circulantes como biomarcadores diagnósticos na doença de Alzheimer e na de Parkinson — revisão sistemática e meta-análise

*Rascunho de manuscrito. Toda afirmação quantitativa remete a `data/extracted/diagnostic_accuracy_extraction.csv`, onde cada valor está guardado junto da frase verbatim de sua fonte.*

🇬🇧 English version: [../en/MANUSCRIPT_DRAFT.md](../en/MANUSCRIPT_DRAFT.md)

**Wesley Felipe Capucho¹, Roberta Sessa Stilhano Yamaguchi¹**
¹ Universidade Federal de São Paulo (UNIFESP), Instituto de Saúde e Sociedade, Santos, SP, Brasil.

---

## Resumo

**Contexto.** Há mais de uma década os microRNAs circulantes vêm sendo propostos como biomarcadores minimamente invasivos para a doença de Alzheimer (AD) e a doença de Parkinson (PD). Diversas meta-análises já agregaram sua acurácia diagnóstica, reportando áreas ROC-resumo de 0,87 a 0,90. O que não foi perguntado é se os miRNAs que dominam essa literatura são os que de fato discriminam pacientes, e até onde as ambições terapêuticas da área chegaram na clínica.

**Métodos.** Buscamos no PubMed/MEDLINE e no Scopus (2015 a 10 de setembro de 2026) estudos que reportassem acurácia diagnóstica de miRNAs dosados em biofluido na AD ou na PD. A triagem seguiu o PRISMA 2020. Os valores de acurácia foram extraídos de textos completos de acesso aberto, cada um registrado junto da frase verbatim que o sustenta. As áreas sob a curva ROC foram agregadas na escala logito por efeitos aleatórios de DerSimonian–Laird, com erros-padrão vindos dos intervalos de confiança publicados ou de Hanley–McNeil quando havia tamanhos de grupo. Em seguida, testamos se a frequência com que um miRNA é mencionado no corpus prediz sua acurácia medida, e consultamos o ClinicalTrials.gov quanto a terapias dirigidas a miRNA.

**Resultados.** Dos 482 registros únicos triados, 34 estudos renderam 50 estimativas extraíveis, das quais 25 (16 estudos independentes) puderam ser ponderadas. miRNAs circulantes isolados agregaram em AUC de 0,758 (IC 95% 0,706–0,804). Painéis multi-miRNA agregaram em 0,888 (0,829–0,928), com intervalos de confiança que não se sobrepõem aos dos marcadores isolados — distância coerente com meta-análises anteriores que também acharam combinações superiores a marcadores isolados. A atenção da literatura mostrou relação inversa com a acurácia medida (ρ de Spearman = −0,61; p = 0,012 entre as estimativas elegíveis): os dois miRNAs mais discutidos no corpus, miR-125b e miR-146a, devolveram AUCs de 0,75 e 0,68. O teste de Egger indicou efeitos de estudos pequenos em vários subgrupos. Nenhum mimético de miRNA ou antagomiR entrou em ensaio clínico registrado para AD ou PD.

**Conclusões.** Agregado ao longo da literatura publicada, um miRNA circulante isolado desempenha no limiar ou abaixo do que se espera de um teste diagnóstico autônomo. Painéis têm desempenho materialmente melhor e é para eles que o esforço da área deveria convergir. A proeminência de miRNAs individuais nessa literatura reflete atenção de pesquisa, e não desempenho diagnóstico — se alguma coisa, de forma inversa. Um achado metodológico acompanha o clínico: acrescentar uma segunda base a uma revisão de base única já concluída derrubou duas de suas conclusões.

**Palavras-chave:** microRNA; doença de Alzheimer; doença de Parkinson; acurácia diagnóstica; meta-análise; biomarcadores; viés de publicação.

---

## 1. Introdução

O argumento a favor dos microRNAs circulantes como biomarcadores de neurodegeneração sempre foi fácil de fazer. Eles são estáveis em plasma, soro e líquor; podem ser dosados por qPCR em qualquer laboratório razoavelmente equipado; e, como um único miRNA regula muitos transcritos, cada um carrega informação sobre vias inteiras, e não sobre uma proteína só. Diante de uma doença hoje diagnosticada por critérios clínicos somados a neuroimagem cara ou a uma punção lombar invasiva, um exame de sangue construído sobre essas moléculas é uma perspectiva atraente.

Mais de uma década de trabalho decorreu dessa premissa. Estudos individuais reportam que membros da família miR-29 acompanham a expressão de BACE1 e o processamento amiloide na AD, que miR-7 e miR-153 reprimem SNCA e modulam o acúmulo de α-sinucleína na PD, e que o miR-146a ocupa o centro da resposta neuroinflamatória via IRAK1 e TRAF6. Revisões dessa literatura listaram miRNAs desregulados, mapearam-nos sobre vias e concluíram que são promissores.

A pergunta aritmética já foi feita. Ao menos seis meta-análises agregaram acurácia diagnóstica de miRNAs nessas doenças, reportando áreas ROC-resumo entre 0,87 e 0,90, e três delas reportam que combinações de miRNAs superam marcadores isolados. Não reivindicamos primazia aqui e, onde nossos resultados concordam com os delas, dizemos isso.

Uma segunda pergunta, porém, não foi feita, e revisões desse campo são estruturalmente incapazes de respondê-la: os miRNAs que dominam a literatura são os que melhor funcionam?

Essa segunda pergunta importa mais do que parece. O modo habitual de estabelecer que um miRNA é importante é mostrar que ele é frequentemente reportado e que suas interações-alvo estão experimentalmente catalogadas. Mas esses dois critérios não são independentes. Um miRNA que atraiu atenção cedo acumula tanto citações quanto interações validadas, e a proeminência acumulada atrai mais estudos. Frequência bibliométrica e validação catalogada compartilham uma causa comum, de modo que a concordância entre elas é evidência fraca de importância biológica ou clínica. A acurácia diagnóstica agregada, medida em pacientes, é externa a esse laço.

Fizemos, portanto, três coisas. Conduzimos uma revisão sistemática e meta-análise de efeitos aleatórios da acurácia diagnóstica de miRNAs circulantes na AD e na PD, agregando as AUCs que os estudos reportaram em vez de ajustar uma curva ROC-resumo, o que responde à pergunta mais estreita do que um estudo típico observa. Testamos se a atenção nessa literatura se associa ao desempenho medido. E, porque as ambições da área vão além do diagnóstico e alcançam a terapia de reposição de miRNA, perguntamos ao registro de ensaios clínicos até onde essa ambição de fato chegou.

## 2. Métodos

O detalhamento completo, incluindo cada string de busca, está no documento de métodos do repositório e em `data/raw/systematic_review_2026/search_strategy.json`.

### 2.1 Busca

O PubMed/MEDLINE foi consultado pela API E-utilities do NCBI em 10 de setembro de 2026, restrito a publicações a partir de 1º de janeiro de 2015, sem restrição de idioma. Foram executados dois braços, idênticos exceto pelo termo da doença, cada um combinando um bloco de microRNA, um bloco de biofluido (plasma, soro, líquor, sangue, exossomo, vesícula extracelular) e um bloco de acurácia diagnóstica (ROC, AUC, sensibilidade, especificidade, acurácia diagnóstica, valor diagnóstico), todos em Título/Resumo. Os braços retornaram 168 (AD) e 97 (PD) registros, 234 únicos após deduplicação.

O Scopus foi então consultado com a expressão `TITLE-ABS-KEY` equivalente para o braço AD, exportado e fundido. Retornou 408 registros, dos quais 159 já constavam do PubMed e um era duplicata interna, restando **248 registros novos** — mais do que todo o braço AD do PubMed havia recuperado. A deduplicação foi por DOI, PubMed ID e título normalizado. O braço PD do Scopus e a Web of Science seguem não consultados; a cobertura é, portanto, assimétrica entre as duas doenças, e dizemos isso em vez de sugerir uma busca uniforme.

### 2.2 Triagem e elegibilidade

A triagem foi baseada em regras e é reprodutível a partir do script versionado. Registros foram separados como literatura secundária pelo tipo de publicação do PubMed ou por autodescrição, e foram sinalizados como portadores de dados quantitativos quando o resumo reportava AUC ou sensibilidade e especificidade juntas.

Os textos completos foram recuperados do PubMed Central para os estudos que passaram nesse filtro. Uma estimativa entrou no pool primário apenas se representasse contraste caso-versus-controle em população definida de AD ou PD. Estimativas com comparadores compostos, contrastes intradoença, coortes prodrômicas, subgrupos estratificados por genótipo, populações neurodegenerativas mistas ou coortes não resolvíveis foram mantidas na tabela de extração, porém sinalizadas fora, cada uma com o motivo declarado.

### 2.3 Extração

Expressões regulares foram usadas para localizar frases contendo métricas de acurácia; os valores em si foram lidos nessas frases e transcritos manualmente. Essa separação foi necessária, não decorativa. Na validação, a captura automática inverteu sensibilidade e especificidade sempre que a frase as declarava em ordem oposta, leu valores de p em campos de especificidade e confundiu uma *redução* de AUC em teste de permutação com uma AUC. Também capturou valores que a seção de discussão atribuía a outros artigos. Cada linha extraída guarda a frase que a sustenta, de modo que qualquer leitor pode conferir um valor contra sua fonte.

Publicação duplicada foi verificada comparando frases de resultado verbatim. Um par foi encontrado (PMIDs 40661348 e 41836608, um preprint e sua versão de periódico) e contado uma única vez.

### 2.4 Síntese

Os erros-padrão vieram do IC 95% publicado quando disponível e, caso contrário, da fórmula de Hanley e McNeil a partir dos tamanhos dos grupos caso e controle. Como checagem dessa etapa, para um estudo que reportou AUC de 0,75 em 18 casos e 18 controles, a fórmula devolveu EP = 0,0822, contra EP de 0,08 reportado pelo próprio artigo.

As AUCs foram transformadas para a escala logito, agregadas pelo estimador de efeitos aleatórios de DerSimonian–Laird e retrotransformadas. Efeitos aleatórios foram especificados de antemão: esses estudos diferem em biofluido, plataforma, população e no modo como derivaram seus pontos de corte, então uma acurácia verdadeira comum não é hipótese plausível. A heterogeneidade é reportada como Q de Cochran, τ² e I². Efeitos de estudos pequenos foram avaliados pela regressão de Egger. Os subgrupos foram doença, tipo de marcador e biofluido.

Por fim, contagens de artigos distintos que mencionam cada miRNA foram calculadas no corpus triado e correlacionadas com a AUC média reportada, e o ClinicalTrials.gov foi consultado quanto a agentes terapêuticos dirigidos a miRNA.

## 3. Resultados

### 3.1 Fluxo dos estudos

O PubMed retornou 234 registros únicos; o braço AD do Scopus acrescentou outros 248, totalizando 482 registros únicos. A triagem separou 46 registros do PubMed e 147 do Scopus como literatura secundária, restando 188 e 101 estudos primários respectivamente; 95 e 20 destes reportaram AUC ou par sensibilidade–especificidade. Foram lidos 45 textos completos. No total, **34 estudos** renderam **50 estimativas extraíveis**; 31 atenderam à elegibilidade e **25 — de 16 estudos independentes** — tinham erro-padrão estimável e puderam ser ponderadas.

A perda merece comentário. Cerca de um registro triado em cada vinte contribuiu com uma estimativa ponderada, e a maior causa isolada foram estudos que publicaram AUC sem os tamanhos de grupo ou o intervalo de confiança necessários para ponderá-la. Das oito estimativas que a busca no Scopus acrescentou, apenas uma pôde ser ponderada exatamente por esse motivo.

### 3.2 Acurácia diagnóstica agregada

| Subgrupo | k | Estudos | AUC agregada (IC 95%) | I² |
|---|---|---|---|---|
| Global | 25 | 16 | 0,807 (0,745–0,857) | 93% |
| Doença de Alzheimer | 13 | 10 | 0,842 (0,788–0,884) | 77% |
| Doença de Parkinson | 12 | 6 | 0,753 (0,621–0,850) | 94% |
| miRNA isolado | 17 | 10 | 0,758 (0,706–0,804) | 66% |
| Painel multi-miRNA | 8 | 7 | 0,888 (0,829–0,928) | 85% |
| AD, miRNA isolado | 7 | 6 | 0,802 (0,741–0,851) | 63% |
| PD, miRNA isolado | 10 | 4 | 0,716 (0,640–0,781) | 55% |
| Plasma | 5 | 4 | 0,762 (0,642–0,851) | 76% |
| Soro | 11 | 4 | 0,810 (0,721–0,876) | 82% |

Um miRNA circulante isolado agrega em 0,758, com a estimativa pontual abaixo do piso convencional de 0,80 para um teste autônomo e o limite superior do intervalo apenas o alcançando. Painéis agregam em 0,888, e os dois intervalos não se sobrepõem.

Uma versão anterior desta análise, restrita ao PubMed, não encontrou heterogeneidade detectável no subgrupo de miRNA isolado em AD (I² = 0%; agregado 0,773) e tiramos uma conclusão dessa consistência. A busca no Scopus a dissolveu: um único estudo adicional — miR-202, AUC 0,892 em 121 casos e 86 controles — elevou o subgrupo a 0,802 com I² = 63%. Reportamos isso em vez de apresentar silenciosamente a cifra revisada, porque é a evidência mais clara neste artigo de que uma revisão de base única pode fabricar um consenso aparente.

### 3.3 Atenção não prediz desempenho

As contagens de menção no corpus triado correlacionaram-se com a AUC média reportada em ρ = −0,27 (p = 0,16) considerando todas as estimativas de miRNA isolado, e em **ρ = −0,61 (p = 0,012)** quando restritas às elegíveis. Só com o PubMed, o coeficiente restrito era ρ = −0,41 (p = 0,14); a busca ampliada o levou além da significância convencional. Dezesseis miRNAs contribuem, a maioria com um único estudo cada, então a análise segue exploratória e não sustenta leitura causal.

O padrão por trás do coeficiente, ainda assim, merece ser dito. O miR-125b foi mencionado em 13 artigos do corpus e devolveu AUC de 0,753; o miR-146a foi mencionado em 11 e devolveu 0,680, o menor valor entre as estimativas elegíveis. Enquanto isso, let-7i, miR-501-3p e miR-128 — mencionados em um, um e dois artigos, respectivamente — devolveram 0,835, 0,820 e 0,831.

### 3.4 Efeitos de estudos pequenos

A regressão de Egger foi significativa no pool global, no subgrupo de PD, no pool de miRNAs isolados, no subgrupo de painéis e no subgrupo de soro. Somado a duas características estruturais desta literatura — pontos de corte derivados na mesma amostra em que são avaliados e coortes frequentemente com menos de 50 por braço —, isso aponta em uma única direção. Todo valor agregado aqui deve ser lido como a ponta otimista de sua faixa plausível.

### 3.5 Translação clínica

O ClinicalTrials.gov lista 16 ensaios registrados de agentes terapêuticos dirigidos a miRNA, de cinco moléculas: miravirsen (anti-miR-122, hepatite C, oito ensaios, Fase 2); cobomarsen (anti-miR-155, oncologia, Fase 2, encerrado); MRX34 (mimético de miR-34a, oncologia, encerrado); TargomiRs (mimético de miR-16, Fase 1); e MRG-201/remlarsen (mimético de miR-29, dermatologia, Fase 2).

Nenhum é em doença de Alzheimer ou de Parkinson. Treze ensaios registrados mencionam miRNAs em AD ou PD, mas oito são estudos observacionais de biomarcador, dois medem miRNAs como desfecho de exercício ou reabilitação, e os três ensaios intervencionais com fármaco administram genfibrozila, um oligonucleotídeo antissenso contra o mRNA da tau e um adjuvante agonista de TLR9 — nenhum deles agente dirigido a miRNA.

## 4. Discussão

O número central desta análise é 0,758. É o que um miRNA circulante isolado alcança quando as estimativas publicadas são ponderadas e combinadas: abaixo do limiar usualmente tratado como mínimo para um teste diagnóstico autônomo, com o limite superior do intervalo apenas o alcançando. Para comparação, os ensaios plasmáticos de fosfo-tau hoje em uso clínico para AD operam bem acima de 0,90. Um exame de sangue nesse patamar não está competindo na mesma categoria.

### Relação com meta-análises anteriores

Seis meta-análises anteriores agregaram acurácia diagnóstica de miRNAs nessas doenças e reportaram áreas ROC-resumo de 0,87 a 0,90 — visivelmente acima da cifra daqui. A diferença é sobretudo de estimando, e não de evidência, e não deve ser lida como contradição.

Aquelas análises ajustam um modelo bivariado ou HSROC aos pares sensibilidade–especificidade de cada estudo e reportam a área sob a curva-resumo resultante. Nós fizemos a média das AUCs que os próprios estudos reportaram. A primeira descreve uma curva-resumo ajustada ao conjunto da literatura; a segunda descreve o que um estudo típico observou. Sobre dados idênticos as duas podem divergir bastante, e cada uma responde a uma pergunta legítima. Quem pergunta quão bem funciona a curva ROC-resumo da literatura deve usar os valores SROC publicados; quem pergunta o que um miRNA isolado alcança numa coorte típica está mais perto do nosso.

Outras duas diferenças empurram na mesma direção. Com a exceção de Guévremont e colegas, as cifras principais anteriores agregam marcadores isolados e combinações juntos — o que coloca o ~0,87 delas entre nossas estimativas de marcador isolado (0,758) e de painel (0,888), aproximadamente onde uma mistura das duas cairia. E nossa extração se restringiu a textos completos de acesso aberto e a resumos, fatia mais estreita do que a usada por aquelas revisões.

Também não reivindicamos como novo o resultado de isolado versus painel. Três meta-análises anteriores reportam que combinações superam marcadores isolados; nossa contribuição é quantificar a distância numa escala de AUC comum, com intervalos que não se sobrepõem. Onde nossos achados concordam com o trabalho existente, devem ser lidos como replicação convergente.

Queremos ser cuidadosos com o que isso mostra e o que não mostra. Não mostra que miRNAs sejam irrelevantes na biologia da neurodegeneração; importância regulatória e discriminação diagnóstica são afirmações distintas, e evidência para a primeira não é evidência para a segunda. O que mostra é mais estreito e mais prático: como medidas individuais em biofluidos acessíveis, essas moléculas não separam pacientes de controles bem o bastante para funcionarem sozinhas.

### Um achado sobre método

Uma primeira versão desta análise consultou apenas o PubMed. Nela, o subgrupo de miRNA isolado em AD mostrava I² = 0% — seis estimativas de cinco estudos, biofluidos e plataformas diferentes, convergindo para 0,773 — e interpretamos essa consistência como evidência de que o teto era propriedade da medida, e não do modo como vinha sendo feita. Era um argumento atraente, e estava errado.

Acrescentar o braço do Scopus trouxe 248 registros que a busca no PubMed não retornara, e um deles (miR-202, AUC 0,892 em 121 casos e 86 controles) levou o subgrupo a 0,802 com I² = 63%. A homogeneidade era artefato de uma busca incompleta, e não propriedade da biologia.

Reportamos isso porque a alternativa — apresentar os números revisados como se sempre tivessem sido os números — ocultaria o resultado mais transferível deste artigo. Uma revisão sistemática de base única pode render uma estimativa limpa, de baixa heterogeneidade e confiantemente interpretável que uma segunda base dissolve. Revisões desta literatura apoiadas em um só índice merecem ser lidas com essa possibilidade em mente, inclusive revisões que chegam a conclusões que gostaríamos que fossem verdadeiras.

Os painéis são o achado construtivo. Em 0,888, com intervalos que não se sobrepõem aos dos marcadores isolados, combinar miRNAs produz ganho real e quantificável. Isso se alinha ao que a biologia prevê — miRNAs atuam como moduladores de rede, com alavancagem individual modesta —, mas aqui chega como efeito medido, e não como inferência. Duas ressalvas se aplicam: a heterogeneidade dos painéis é alta e painéis são o tipo de marcador mais vulnerável a sobreajuste, já que muitos derivam pesos e ponto de corte na mesma amostra em que reportam desempenho. O número dos painéis é o mais provável de cair sob validação externa.

A análise de atenção só cruzou a significância convencional depois da busca ampliada (ρ = −0,61; p = 0,012, vindo de ρ = −0,41), e com dezesseis miRNAs segue exploratória; não queremos superdimensioná-la. Mas é difícil olhar para o miR-146a — mencionado em onze artigos do corpus, central no relato neuroinflamatório da AD e devolvendo a menor AUC entre as estimativas elegíveis — sem concluir que a proeminência nesta literatura é conquistada por interesse mecanístico e conveniência de dosagem, e não por desempenho discriminativo. Revisões que ranqueiam candidatos a miRNA pela frequência com que aparecem estão ranqueando por atenção. Se um leitor quer saber qual miRNA medir, esse ranqueamento é quase não informativo.

Os achados do registro completam o quadro. Após mais de uma década de trabalho pré-clínico com miméticos e antagomiRs em neurodegeneração, nenhum entrou em ensaio registrado em AD ou PD. A lacuna não é que a classe molecular seja não testada em humanos: o miravirsen chegou à Fase 2 em hepatite C, e o MRG-201/remlarsen — um mimético de miR-29, exatamente o eixo mais frequentemente modelado como terapia para AD — chegou à Fase 2 para queloide, por injeção intradérmica. As moléculas podem ser feitas e administradas. O que falta é uma via até o cérebro. Qualquer modelo computacional que simule um mimético de miRNA como terapia para AD ou PD deveria declarar essa restrição explicitamente, ao lado da janela terapêutica estreita que esses próprios modelos geram quando a supersupressão leva os alvos abaixo do nível fisiológico basal.

Duas recomendações decorrem para a prática. Primeiro, reporte o número de casos e de controles junto de todo resultado de ROC. A maior causa isolada de perda de dados nesta revisão foram estudos que publicaram uma AUC sem a informação necessária para ponderá-la, o que os remove de toda síntese futura sem benefício para ninguém. Segundo, avalie painéis candidatos em coortes nas quais o ponto de corte seja fixado de antemão, e compare-os com p-tau217, e não com nenhum comparador. Sem isso, a literatura seguirá produzindo estimativas perto de 0,75 e descrevendo-as como promissoras.

## 5. Limitações

A cobertura é assimétrica: o braço AD do Scopus foi consultado, mas o braço PD não, e a Web of Science não foi consultada, então as estimativas de PD repousam apenas no PubMed. Dado que só o braço AD do Scopus dobrou a contagem de registros e mudou duas conclusões, as cifras de PD aqui devem ser tratadas como provisórias. A extração restringe-se a textos completos de acesso aberto e a resumos, e 20 dos 25 erros-padrão ponderados são reconstruídos a partir de tamanhos de grupo, e não retirados de intervalo publicado. Vinte e cinco estimativas ponderadas de 16 estudos é base de evidência modesta, e algumas células de subgrupo são muito pequenas (painéis em PD, k = 2). A heterogeneidade chega a I² = 94%. A análise de atenção tem baixo poder e não sustenta interpretação causal. Não havia dados individuais de participantes, então não foi feita modelagem bivariada de sensibilidade–especificidade. Por fim, acurácia reportada não é acurácia clínica prospectiva, e a direção dessa diferença não é neutra.

## 6. Conclusão

Agregados ao longo dos estudos publicados, microRNAs circulantes isolados discriminam pacientes com AD e PD de controles com acurácia em torno de 0,76, no limiar ou abaixo do que um teste diagnóstico autônomo requer. Painéis multi-miRNA alcançam cerca de 0,89 e é neles que a evidência sustenta investir — conclusão que este trabalho compartilha com várias meta-análises anteriores, em vez de estabelecer sozinho. Os miRNAs individuais que dominam esta literatura devem sua proeminência à atenção de pesquisa, e não ao desempenho medido, e a associação corre de forma inversa. Nenhuma terapia dirigida a miRNA entrou até hoje em ensaio clínico para qualquer uma das duas doenças.

As moléculas seguem biologicamente interessantes; o argumento diagnóstico em favor delas, como vem sendo feito, é mais fraco do que o volume de publicação sugere. E um dos resultados aqui é sobre como esses argumentos são construídos: nossa própria alegação mais confiante, a de que as estimativas de miRNA isolado em AD eram homogêneas, não sobreviveu ao acréscimo de uma segunda base à busca.

## Disponibilidade dos dados

Todos os dados, tabelas de extração com citações verbatim das fontes, scripts de análise e saídas estão disponíveis em https://github.com/WesleyCapucho/-Epigen-tica-e-micrornas-em-doen-as-neurodegenerativas

## Referências

1. Marques TM, Kuiperij HB, Bruinsma IB, et al. MicroRNAs in cerebrospinal fluid as potential biomarkers for Parkinson's disease and multiple system atrophy. *Mol Neurobiol.* 2016. doi:10.1007/s12035-016-0253-0
2. Lusardi TA, Phillips JI, Wiedrick JT, et al. MicroRNAs in human cerebrospinal fluid as biomarkers for Alzheimer's disease. *J Alzheimers Dis.* 2017. doi:10.3233/JAD-160835
3. Hara N, Kikuchi M, Miyashita A, et al. Serum microRNA miR-501-3p as a potential biomarker related to the progression of Alzheimer's disease. *Acta Neuropathol Commun.* 2017. doi:10.1186/s40478-017-0414-z
4. Dos Santos MCT, Barreto-Sanz MA, Correia BRS, et al. miRNA-based signatures in cerebrospinal fluid as potential diagnostic tools for early stage Parkinson's disease. *Oncotarget.* 2018. doi:10.18632/oncotarget.24736
5. Jain G, Stuendl A, Rao P, et al. A combined miRNA-piRNA signature to detect Alzheimer's disease. *Transl Psychiatry.* 2019. doi:10.1038/s41398-019-0579-2
6. Ludwig N, Fehlmann T, Kern F, et al. Machine learning to detect Alzheimer's disease from circulating non-coding RNAs. *Genomics Proteomics Bioinformatics.* 2019. doi:10.1016/j.gpb.2019.09.004
7. Grossi I, Radeghieri A, Paolini L, et al. MicroRNA-34a-5p expression in the plasma and in its extracellular vesicle fractions in subjects with Parkinson's disease. *Int J Mol Med.* 2020. doi:10.3892/ijmm.2020.4806
8. Han L, Tang Y, Bai X, et al. Association of the serum microRNA-29 family with cognitive impairment in Parkinson's disease. *Aging.* 2020. doi:10.18632/aging.103458
9. Hojati Z, Omidi F, Dehbashi M, et al. The highlighted roles of metabolic and cellular response to stress pathways engaged in circulating hsa-miR-494-3p and hsa-miR-661 in Alzheimer's disease. *Iran Biomed J.* 2020. doi:10.29252/ibj.25.1.62
10. Karaglani M, Gourlia K, Tsamardinos I, et al. Accurate blood-based diagnostic biosignatures for Alzheimer's disease via automated machine learning. *J Clin Med.* 2020. doi:10.3390/jcm9093016
11. Oliveira SR, Dionísio PA, Correia Guedes L, et al. Circulating inflammatory miRNAs associated with Parkinson's disease pathophysiology. *Biomolecules.* 2020. doi:10.3390/biom10060945
12. Sandau US, Wiedrick JT, Smith SJ, et al. Performance of validated microRNA biomarkers for Alzheimer's disease in mild cognitive impairment. *J Alzheimers Dis.* 2020. doi:10.3233/JAD-200396
13. Tan YJ, Wong BYX, Vaidyanathan R, et al. Altered cerebrospinal fluid exosomal microRNA levels in young-onset Alzheimer's disease and frontotemporal dementia. *J Alzheimers Dis Rep.* 2021. doi:10.3233/ADR-210311
14. Zhang M, Han W, Xu Y, et al. Serum miR-128 serves as a potential diagnostic biomarker for Alzheimer's disease. *Neuropsychiatr Dis Treat.* 2021. doi:10.2147/NDT.S290925
15. Soto M, Iranzo A, Lahoz S, et al. Serum microRNAs predict isolated rapid eye movement sleep behavior disorder and Lewy body diseases. *Mov Disord.* 2022. doi:10.1002/mds.29171
16. Wu L, Xu Q, Zhou M, et al. Plasma miR-153 and miR-223 levels as potential biomarkers in Parkinson's disease. *Front Neurosci.* 2022. doi:10.3389/fnins.2022.865139
17. Kumar A, Su Y, Sharma M, et al. MicroRNA expression in extracellular vesicles as a novel blood-based biomarker for Alzheimer's disease. *Alzheimers Dement.* 2023. doi:10.1002/alz.13055
18. Rai S, Bharti PS, Singh R, et al. Circulating plasma miR-23b-3p as a biomarker target for idiopathic Parkinson's disease. *Front Neurosci.* 2023. doi:10.3389/fnins.2023.1174951
19. Braunger LJ, Knab F, Gasser T. Using extracellular miRNA signatures to identify patients with LRRK2-related Parkinson's disease. *J Parkinsons Dis.* 2024. doi:10.3233/JPD-230408
20. Duan X, Zheng Q, Liang L, et al. Serum exosomal miRNA-125b and miRNA-451a are potential diagnostic biomarkers for Alzheimer's disease. *Degener Neurol Neuromuscul Dis.* 2024. doi:10.2147/DNND.S444567
21. Li Y, Cao Y, Liu W, et al. Candidate biomarkers of EV-microRNA in detecting REM sleep behavior disorder and Parkinson's disease. *NPJ Parkinsons Dis.* 2024. doi:10.1038/s41531-023-00628-4
22. Omura T, Nishiguchi H, Kaneda H, et al. Plasma expression levels of microRNA-101 are downregulated in patients with Parkinson's disease. *BMC Res Notes.* 2025. doi:10.1186/s13104-025-07604-6
23. Birsan S, Roman-Filip I, Rusu M, et al. Gastric juice miR-106a-5p as a non-invasive biomarker of neuroinflammation and neurodegeneration. *Diseases.* 2026. doi:10.3390/diseases14060187
24. Chen Z, Liu Y, Wang H, et al. Literature-derived serum miRNA signatures associated with cognitive decline in Alzheimer's disease. *Alzheimers Res Ther.* 2026. doi:10.1186/s13195-026-02048-x
25. Qin Q, Xia X, Zhang X, et al. Development of a serum-based microRNA panel for Alzheimer's disease diagnosis. *J Transl Int Med.* 2026. doi:10.1515/jtim-2026-0038
26. Yang SJ, Lin AA, Shen H, et al. Microfluidic nanomagnetically isolated neuron- and astrocyte-derived extracellular vesicles to differentiate Lewy body and Alzheimer's disease. *NPJ Biosens.* 2026. doi:10.1038/s44328-026-00086-x

**Referências metodológicas**

27. DerSimonian R, Laird N. Meta-analysis in clinical trials. *Control Clin Trials.* 1986;7(3):177–188.
28. Hanley JA, McNeil BJ. The meaning and use of the area under a receiver operating characteristic (ROC) curve. *Radiology.* 1982;143(1):29–36.
29. Egger M, Davey Smith G, Schneider M, Minder C. Bias in meta-analysis detected by a simple, graphical test. *BMJ.* 1997;315(7109):629–634.
30. Page MJ, McKenzie JE, Bossuyt PM, et al. The PRISMA 2020 statement. *BMJ.* 2021;372:n71.

*Dados de literatura obtidos do PubMed e do PubMed Central (National Library of Medicine, NCBI); dados de ensaios do ClinicalTrials.gov (NLM).*
