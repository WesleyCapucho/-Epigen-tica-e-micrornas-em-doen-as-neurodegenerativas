# Atenção sem acurácia: microRNAs circulantes como biomarcadores diagnósticos na doença de Alzheimer e na de Parkinson — revisão sistemática e meta-análise

*Rascunho de manuscrito. Toda afirmação quantitativa remete a `data/extracted/diagnostic_accuracy_extraction.csv`, onde cada valor está guardado junto da frase verbatim de sua fonte.*

🇬🇧 English version: [../en/MANUSCRIPT_DRAFT.md](../en/MANUSCRIPT_DRAFT.md)

**Wesley Felipe Capucho¹, Roberta Sessa Stilhano Yamaguchi¹**
¹ Universidade Federal de São Paulo (UNIFESP), Instituto de Saúde e Sociedade, Santos, SP, Brasil.

---

## Resumo

**Contexto.** Há mais de uma década os microRNAs circulantes vêm sendo propostos como biomarcadores minimamente invasivos para a doença de Alzheimer (AD) e a doença de Parkinson (PD). A literatura é vasta e entusiasmada, mas suas estimativas individuais raramente foram agregadas, e os miRNAs que dominam essa literatura nunca foram confrontados com o quanto de fato discriminam pacientes.

**Métodos.** Buscamos no PubMed/MEDLINE (2015 a 10 de setembro de 2026) estudos que reportassem acurácia diagnóstica de miRNAs dosados em biofluido na AD ou na PD. A triagem seguiu o PRISMA 2020. Os valores de acurácia foram extraídos de textos completos de acesso aberto, cada um registrado junto da frase verbatim que o sustenta. As áreas sob a curva ROC foram agregadas na escala logito por efeitos aleatórios de DerSimonian–Laird, com erros-padrão vindos dos intervalos de confiança publicados ou de Hanley–McNeil quando havia tamanhos de grupo. Em seguida, testamos se a frequência com que um miRNA é mencionado no corpus prediz sua acurácia medida, e consultamos o ClinicalTrials.gov quanto a terapias dirigidas a miRNA.

**Resultados.** Dos 234 registros únicos triados, 189 eram estudos primários e 95 reportaram AUC ou par sensibilidade–especificidade; 26 estudos renderam 42 estimativas extraíveis, das quais 24 (15 estudos independentes) puderam ser ponderadas. miRNAs circulantes isolados agregaram em AUC de 0,745 (IC 95% 0,699–0,785). Painéis multi-miRNA agregaram em 0,888 (0,829–0,928), com intervalos de confiança que não se sobrepõem aos dos marcadores isolados. O subgrupo de miRNA isolado em AD não mostrou heterogeneidade detectável (I² = 0%; agregado 0,773; 0,732–0,810). A atenção da literatura não predisse a acurácia medida (ρ de Spearman = −0,11; p = 0,61 no geral; ρ = −0,41; p = 0,14 entre as estimativas elegíveis): os dois miRNAs mais discutidos no corpus, miR-125b e miR-146a, devolveram AUCs de 0,75 e 0,68. O teste de Egger indicou efeitos de estudos pequenos em vários subgrupos. Nenhum mimético de miRNA ou antagomiR entrou em ensaio clínico registrado para AD ou PD.

**Conclusões.** Agregado ao longo da literatura publicada, um miRNA circulante isolado não alcança a acurácia esperada de um teste diagnóstico autônomo, e a consistência desse achado na AD (I² = 0%) sugere que a limitação é real, e não metodológica. Painéis têm desempenho materialmente melhor e é para eles que o esforço da área deveria convergir. A proeminência de miRNAs individuais nessa literatura reflete atenção de pesquisa, e não desempenho diagnóstico.

**Palavras-chave:** microRNA; doença de Alzheimer; doença de Parkinson; acurácia diagnóstica; meta-análise; biomarcadores; viés de publicação.

---

## 1. Introdução

O argumento a favor dos microRNAs circulantes como biomarcadores de neurodegeneração sempre foi fácil de fazer. Eles são estáveis em plasma, soro e líquor; podem ser dosados por qPCR em qualquer laboratório razoavelmente equipado; e, como um único miRNA regula muitos transcritos, cada um carrega informação sobre vias inteiras, e não sobre uma proteína só. Diante de uma doença hoje diagnosticada por critérios clínicos somados a neuroimagem cara ou a uma punção lombar invasiva, um exame de sangue construído sobre essas moléculas é uma perspectiva atraente.

Mais de uma década de trabalho decorreu dessa premissa. Estudos individuais reportam que membros da família miR-29 acompanham a expressão de BACE1 e o processamento amiloide na AD, que miR-7 e miR-153 reprimem SNCA e modulam o acúmulo de α-sinucleína na PD, e que o miR-146a ocupa o centro da resposta neuroinflamatória via IRAK1 e TRAF6. Revisões dessa literatura listaram miRNAs desregulados, mapearam-nos sobre vias e concluíram que são promissores.

O que se fez muito menos foi a pergunta aritmética. Se reunirmos as áreas sob a curva ROC reportadas e as agregarmos, que acurácia um miRNA circulante de fato alcança? E uma segunda pergunta vem logo atrás, uma que revisões desse campo são estruturalmente incapazes de responder: os miRNAs que dominam a literatura são os que melhor funcionam?

Essa segunda pergunta importa mais do que parece. O modo habitual de estabelecer que um miRNA é importante é mostrar que ele é frequentemente reportado e que suas interações-alvo estão experimentalmente catalogadas. Mas esses dois critérios não são independentes. Um miRNA que atraiu atenção cedo acumula tanto citações quanto interações validadas, e a proeminência acumulada atrai mais estudos. Frequência bibliométrica e validação catalogada compartilham uma causa comum, de modo que a concordância entre elas é evidência fraca de importância biológica ou clínica. A acurácia diagnóstica agregada, medida em pacientes, é externa a esse laço.

Fizemos, portanto, três coisas. Conduzimos uma revisão sistemática e meta-análise de efeitos aleatórios da acurácia diagnóstica de miRNAs circulantes na AD e na PD. Testamos se a atenção nessa literatura se associa ao desempenho medido. E, porque as ambições da área vão além do diagnóstico e alcançam a terapia de reposição de miRNA, perguntamos ao registro de ensaios clínicos até onde essa ambição de fato chegou.

## 2. Métodos

O detalhamento completo, incluindo cada string de busca, está no documento de métodos do repositório e em `data/raw/systematic_review_2026/search_strategy.json`.

### 2.1 Busca

O PubMed/MEDLINE foi consultado pela API E-utilities do NCBI em 10 de setembro de 2026, restrito a publicações a partir de 1º de janeiro de 2015, sem restrição de idioma. Foram executados dois braços, idênticos exceto pelo termo da doença, cada um combinando um bloco de microRNA, um bloco de biofluido (plasma, soro, líquor, sangue, exossomo, vesícula extracelular) e um bloco de acurácia diagnóstica (ROC, AUC, sensibilidade, especificidade, acurácia diagnóstica, valor diagnóstico), todos em Título/Resumo.

Scopus e Web of Science não foram consultadas, porque o ambiente de análise não tinha acesso institucional a elas. Declaramos isso, em vez de estimar o que essas bases teriam retornado.

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

Os dois braços retornaram 168 (AD) e 97 (PD) registros, 234 únicos após deduplicação, com 30 recuperados por ambos. A triagem separou 45 registros como literatura secundária, restando 189 estudos primários, dos quais 95 reportaram AUC ou par sensibilidade–especificidade e 55 destes tinham texto completo de acesso aberto. Foram lidos 45 textos completos, gerando 42 estimativas extraíveis de 26 estudos. Vinte e oito atenderam à elegibilidade e 24 — de 15 estudos independentes — tinham erro-padrão estimável e puderam ser ponderadas.

A perda merece comentário. Menos de um registro triado em cada dez contribuiu com uma estimativa ponderada, e a maior causa isolada foram estudos que publicaram AUC sem os tamanhos de grupo ou o intervalo de confiança necessários para ponderá-la.

### 3.2 Acurácia diagnóstica agregada

| Subgrupo | k | Estudos | AUC agregada (IC 95%) | I² |
|---|---|---|---|---|
| Global | 24 | 15 | 0,802 (0,735–0,856) | 93% |
| Doença de Alzheimer | 12 | 9 | 0,836 (0,778–0,882) | 76% |
| Doença de Parkinson | 12 | 6 | 0,753 (0,621–0,850) | 94% |
| miRNA isolado | 16 | 9 | 0,745 (0,699–0,785) | 46% |
| Painel multi-miRNA | 8 | 7 | 0,888 (0,829–0,928) | 85% |
| AD, miRNA isolado | 6 | 5 | 0,773 (0,732–0,810) | 0% |
| PD, miRNA isolado | 10 | 4 | 0,716 (0,640–0,781) | 55% |
| Plasma | 5 | 4 | 0,762 (0,642–0,851) | 76% |
| Soro | 10 | 3 | 0,798 (0,693–0,874) | 82% |

Um miRNA circulante isolado agrega em 0,745, com todo o intervalo de confiança abaixo de 0,80. Painéis agregam em 0,888, e os dois intervalos não se sobrepõem.

O subgrupo de miRNA isolado em AD é a célula mais informativa da tabela porque sua heterogeneidade é zero. Seis estimativas de cinco estudos, em soro, exossomos séricos, sangue total e vesículas extracelulares de origem neuronal, e em plataformas de qPCR e sequenciamento, convergem para 0,773 sem variância detectável entre estudos. Um valor modesto e consistente é um resultado mais difícil de contestar do que um inconsistente, porque retira a esperança de que métodos melhores elevariam a estimativa.

### 3.3 Atenção não prediz desempenho

As contagens de menção no corpus de 234 registros correlacionaram-se com a AUC média reportada em ρ = −0,11 (p = 0,61) considerando todas as estimativas de miRNA isolado, e em ρ = −0,41 (p = 0,14) quando restritas às elegíveis. Nenhum alcança significância e, com a maioria dos miRNAs contribuindo com um único estudo, a análise tem baixo poder; reportamo-la como exploratória.

O padrão por trás do coeficiente, ainda assim, merece ser dito. O miR-125b foi mencionado em 13 artigos do corpus e devolveu AUC de 0,753; o miR-146a foi mencionado em 11 e devolveu 0,680, o menor valor entre as estimativas elegíveis. Enquanto isso, let-7i, miR-501-3p e miR-128 — mencionados em um, um e dois artigos, respectivamente — devolveram 0,835, 0,820 e 0,831.

### 3.4 Efeitos de estudos pequenos

A regressão de Egger foi significativa no pool global, no subgrupo de PD e no subgrupo de painéis. Somado a duas características estruturais desta literatura — pontos de corte derivados na mesma amostra em que são avaliados e coortes frequentemente com menos de 50 por braço —, isso aponta em uma única direção. Todo valor agregado aqui deve ser lido como a ponta otimista de sua faixa plausível.

### 3.5 Translação clínica

O ClinicalTrials.gov lista 16 ensaios registrados de agentes terapêuticos dirigidos a miRNA, de cinco moléculas: miravirsen (anti-miR-122, hepatite C, oito ensaios, Fase 2); cobomarsen (anti-miR-155, oncologia, Fase 2, encerrado); MRX34 (mimético de miR-34a, oncologia, encerrado); TargomiRs (mimético de miR-16, Fase 1); e MRG-201/remlarsen (mimético de miR-29, dermatologia, Fase 2).

Nenhum é em doença de Alzheimer ou de Parkinson. Treze ensaios registrados mencionam miRNAs em AD ou PD, mas oito são estudos observacionais de biomarcador, dois medem miRNAs como desfecho de exercício ou reabilitação, e os três ensaios intervencionais com fármaco administram genfibrozila, um oligonucleotídeo antissenso contra o mRNA da tau e um adjuvante agonista de TLR9 — nenhum deles agente dirigido a miRNA.

## 4. Discussão

O número central desta análise é 0,745. É o que um miRNA circulante isolado alcança quando as estimativas publicadas são ponderadas e combinadas, e fica abaixo do limiar usualmente tratado como mínimo para um teste diagnóstico autônomo. Para comparação, os ensaios plasmáticos de fosfo-tau hoje em uso clínico para AD operam bem acima de 0,90. Um exame de sangue cujo intervalo de confiança inteiro fica sob 0,80 não está competindo na mesma categoria.

Queremos ser cuidadosos com o que isso mostra e o que não mostra. Não mostra que miRNAs sejam irrelevantes na biologia da neurodegeneração; importância regulatória e discriminação diagnóstica são afirmações distintas, e evidência para a primeira não é evidência para a segunda. O que mostra é mais estreito e mais prático: como medidas individuais em biofluidos acessíveis, essas moléculas não separam pacientes de controles bem o bastante para funcionarem sozinhas.

A heterogeneidade zero no subgrupo de miRNA isolado em AD é, para nós, o detalhe mais instrutivo. Literaturas heterogêneas alimentam a esperança de que um sinal mais forte esteja soterrado sob ruído metodológico. Aqui, cinco estudos independentes, usando fluidos e plataformas diferentes, concordam estreitamente em um valor modesto. A limitação parece ser propriedade da medida, e não do modo como ela vem sendo feita.

Os painéis são o achado construtivo. Em 0,888, com intervalos que não se sobrepõem aos dos marcadores isolados, combinar miRNAs produz ganho real e quantificável. Isso se alinha ao que a biologia prevê — miRNAs atuam como moduladores de rede, com alavancagem individual modesta —, mas aqui chega como efeito medido, e não como inferência. Duas ressalvas se aplicam: a heterogeneidade dos painéis é alta e painéis são o tipo de marcador mais vulnerável a sobreajuste, já que muitos derivam pesos e ponto de corte na mesma amostra em que reportam desempenho. O número dos painéis é o mais provável de cair sob validação externa.

A análise de atenção é exploratória e não queremos superdimensioná-la. Mas é difícil olhar para o miR-146a — mencionado em onze artigos do corpus, central no relato neuroinflamatório da AD e devolvendo a menor AUC entre as estimativas elegíveis — sem concluir que a proeminência nesta literatura é conquistada por interesse mecanístico e conveniência de dosagem, e não por desempenho discriminativo. Revisões que ranqueiam candidatos a miRNA pela frequência com que aparecem estão ranqueando por atenção. Se um leitor quer saber qual miRNA medir, esse ranqueamento é quase não informativo.

Os achados do registro completam o quadro. Após mais de uma década de trabalho pré-clínico com miméticos e antagomiRs em neurodegeneração, nenhum entrou em ensaio registrado em AD ou PD. A lacuna não é que a classe molecular seja não testada em humanos: o miravirsen chegou à Fase 2 em hepatite C, e o MRG-201/remlarsen — um mimético de miR-29, exatamente o eixo mais frequentemente modelado como terapia para AD — chegou à Fase 2 para queloide, por injeção intradérmica. As moléculas podem ser feitas e administradas. O que falta é uma via até o cérebro. Qualquer modelo computacional que simule um mimético de miRNA como terapia para AD ou PD deveria declarar essa restrição explicitamente, ao lado da janela terapêutica estreita que esses próprios modelos geram quando a supersupressão leva os alvos abaixo do nível fisiológico basal.

Duas recomendações decorrem para a prática. Primeiro, reporte o número de casos e de controles junto de todo resultado de ROC. A maior causa isolada de perda de dados nesta revisão foram estudos que publicaram uma AUC sem a informação necessária para ponderá-la, o que os remove de toda síntese futura sem benefício para ninguém. Segundo, avalie painéis candidatos em coortes nas quais o ponto de corte seja fixado de antemão, e compare-os com p-tau217, e não com nenhum comparador. Sem isso, a literatura seguirá produzindo estimativas perto de 0,75 e descrevendo-as como promissoras.

## 5. Limitações

A cobertura restringe-se ao PubMed/MEDLINE. A extração restringe-se a textos completos de acesso aberto no PubMed Central, 55 dos 95 estudos primários elegíveis, o que pode selecionar uma fatia não aleatória do campo. Vinte e quatro estimativas ponderadas de 15 estudos é uma base de evidência modesta, e algumas células de subgrupo são muito pequenas (painéis em PD, k = 2). A heterogeneidade chega a I² = 94%. A análise de atenção tem baixo poder e não sustenta interpretação causal. Não havia dados individuais de participantes, então não foi feita modelagem bivariada de sensibilidade–especificidade. Por fim, acurácia reportada não é acurácia clínica prospectiva, e a direção dessa diferença não é neutra.

## 6. Conclusão

Agregados ao longo dos estudos publicados, microRNAs circulantes isolados discriminam pacientes com AD e PD de controles com acurácia em torno de 0,75 — de forma consistente, no caso da AD, e abaixo do que um teste diagnóstico autônomo requer. Painéis multi-miRNA alcançam cerca de 0,89 e é neles que a evidência sustenta investir. Os miRNAs individuais que dominam esta literatura devem sua proeminência à atenção de pesquisa, e não ao desempenho medido, e nenhuma terapia dirigida a miRNA entrou até hoje em ensaio clínico para qualquer uma das duas doenças. As moléculas seguem biologicamente interessantes; o argumento diagnóstico em favor delas, como vem sendo feito, é mais fraco do que o volume de publicação sugere.

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
