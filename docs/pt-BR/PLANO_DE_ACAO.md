# Plano de ação: elevação do TCC a artigo científico de alto impacto

**Autor:** Wesley Felipe Capucho · **Orientadora:** Profa. Dra. Roberta Sessa Stilhano Yamaguchi
**Documento preparado em:** 10 de setembro de 2026
**Base analisada:** "Epigenética e microRNAs em doenças neurodegenerativas: revisão integrativa, análise bioinformática e modelagem computacional de vias associadas à Doença de Alzheimer e à Doença de Parkinson" (versão revisada e finalizada do TCC).

---

## 1. Ponto de partida: o que o TCC já faz bem

Antes de listar lacunas, vale registrar o que já está consolidado, porque o plano de ação parte desse patamar e não do zero:

- Delineamento com PRISMA 2020, escore de relevância explícito e documentado, e critérios de corte justificados.
- Validação bioinformática cruzada com miRTarBase para os miRNAs mais frequentes, com discussão honesta da circularidade entre frequência bibliométrica e validação funcional (Seção 6.2).
- Análise de sensibilidade paramétrica das simulações (±20/40/60%), com critério de robustez qualitativa explícito.
- Seção de limitações já bastante autocrítica: reconhece que os parâmetros das EDOs não são calibrados experimentalmente, que a precisão decimal reportada reflete resolução numérica (não medição), e que parte da amplificação não linear do modelo integrado é propriedade estrutural do acoplamento, não necessariamente sinergia biológica.
- Declaração de uso de IA e aderência ao Guia de Boas Práticas Científicas da USP.

Esse nível de rigor autocrítico é incomum e é um ativo para a publicação — jornais de maior fator de impacto valorizam exatamente esse tipo de transparência sobre limitações. O trabalho de elevação, portanto, não é "consertar" o TCC, é **substituir elementos ilustrativos por elementos empíricos** nos pontos onde isso é hoje o principal fator limitante, mantendo a mesma postura crítica.

## 2. Diagnóstico das lacunas reais (por ordem de prioridade para "alto impacto")

### 2.1 [CRÍTICO] Números da Tabela 1 (PRISMA) para Scopus e Web of Science parecem ser estimativas, não contagens reais
A Tabela 1 do TCC apresenta "~320*" (Scopus) e "~210*" (Web of Science) como "registros adicionais não duplicados identificados", com nota de rodapé que remete a uma "busca exploratória complementar". Isso precisa ser resolvido antes de qualquer submissão: revisores de periódicos de alto impacto exigem números exatos e reprodutíveis em qualquer fluxograma PRISMA. Duas rotas, sem fabricar números:
- **Rota A (recomendada):** executar de fato as buscas em Scopus e Web of Science com a mesma string adaptada (`TITLE-ABS-KEY` e `TS`, respectivamente), documentar contagem real, data de acesso e exportar os registros. Isso requer acesso institucional (login CAFe/UNIFESP ou Elsevier/Clarivate) —ends via navegador logado, que **esta sessão remota do Claude Code não consegue acessar** (não há controle do Chrome local aqui; ver Seção 5).
- **Rota B:** se o acesso a Scopus/WoS não for viável a tempo, reportar honestamente no manuscrito que a busca aprofundada foi conduzida apenas no PubMed/MEDLINE, e remover ou reclassificar a linha de Scopus/WoS da Tabela 1 como "não quantificada nesta versão", eliminando o asterisco-estimativa. Isso é cientificamente mais defensável do que manter um número aproximado sem rastreabilidade.

### 2.2 [CRÍTICO] Corpus real do PubMed cresceu de 1.000 (script `MAX_RESULTS`) para 2.777 registros
Reexecutei agora mesmo a query exata do TCC via API oficial do NCBI (não uma estimativa): em 10/09/2026 ela retorna **2.777 registros totais**, contra os 1.000 baixados na coleta original (limitados pelo parâmetro `MAX_RESULTS=1000`, não pelo total então disponível). Isso não invalida o trabalho original, mas significa que:
- o manuscrito final deve declarar a data exata de corte da busca e, idealmente, recuperar o corpus completo (ou uma amostra probabilística dele, não apenas os 1.000 primeiros por relevância) para reforçar a robustez estatística;
- o algoritmo de ranqueamento (escore por título/resumo/palavras-chave) deve ser reaplicado sobre o corpus atualizado antes da submissão, para que o "Top 100" reflita o estado da arte até a data de submissão.
- Já iniciei essa correção nesta sessão: o repositório agora contém uma amostra real de 100 artigos recém-coletados via API (ver `data/raw/pubmed/`), como prova de conceito da reprodutibilidade; a extração completa do corpus atual (2.777 registros) deve ser rodada antes da redação final (ver Fase 1).

### 2.3 [ALTO IMPACTO NA PUBLICABILIDADE] Ausência de meta-análise quantitativa real
O trabalho atual é bibliométrico e descritivo (contagens, qui-quadrado, PCA sobre presença/ausência de menções a miRNAs no título/resumo). Isso tem teto editorial baixo. O upgrade de maior retorno por esforço é transformar uma fração do corpus em uma **meta-análise de acurácia diagnóstica real**: extrair de artigos primários (não de resumos) valores publicados de sensibilidade, especificidade, AUC ou fold-change para os miRNAs mais citados (ex.: miR-29c-3p, miR-146a-5p, miR-125b-5p em AD; miR-7-5p, miR-153-3p em PD) em biofluidos (plasma, soro, LCR, exossomos), e agrupá-los estatisticamente (modelo de efeitos aleatórios, `metafor` em R ou `PythonMeta`/`statsmodels`). Esse tipo de síntese quantitativa é o que costuma justificar publicação em periódicos de fator de impacto mais alto na área (ex.: *Ageing Research Reviews*, *Progress in Neurobiology*), porque gera uma estimativa de efeito agregada, com intervalo de confiança, que hoje simplesmente não existe no TCC.

### 2.4 [ALTO IMPACTO CIENTÍFICO] Nenhuma reanálise de dados públicos de expressão
O TCC é inteiramente baseado em mineração textual de metadados (título/resumo). Não há reanálise de nenhum dado de expressão gênica ou de miRNA depositado publicamente. Isso é hoje viável sem gerar ou forjar dado algum: bases como **NCBI GEO** e **ArrayExpress/BioStudies** hospedam séries de expressão de miRNA e mRNA em tecido cerebral, plasma, soro e LCR de pacientes com AD e PD, disponíveis para reanálise (ex.: estudos de perfil de miRNA em córtex/hipocampo de AD, substância negra em PD, plasma/exossomos em ambas). Uma reanálise (diferencial de expressão com `limma`/`DESeq2`, ou re-clusterização/PCA sobre dados reais de amostras humanas) daria ao manuscrito um resultado computacional genuíno, não apenas contagem de citações — e permitiria testar diretamente hipóteses do próprio modelo teórico do TCC (ex.: miR-29c/BACE1 co-variam nos dados reais de AD?). Essa é provavelmente a alavanca isolada mais forte para "alto impacto e relevância científica" pedida pela orientadora.

### 2.5 [MÉDIO-ALTO] Validação de alvos limitada a uma única base (miRTarBase)
Reforçar a validação com bases complementares e de natureza diferente — **TargetScan** e **miRDB** (predição computacional por complementaridade de sequência) e **DIANA-TarBase** ou **miRWalk** (validação experimental adicional) — e então rodar enriquecimento funcional (KEGG/Reactome/GO) sobre a lista consolidada de alvos. Isso movimenta a discussão de "estes miRNAs aparecem juntos na literatura" para "estes miRNAs convergem estatisticamente sobre as mesmas vias biológicas", que é um argumento mais forte e menos circular do que o atual (already reconhecido como limitação pelo próprio autor na Seção 6.2).

### 2.6 [MÉDIO] Modelos por equações diferenciais: parâmetros ilustrativos, não calibrados
O TCC já é extremamente honesto sobre isso (Seções 4.16, 6.3, 7) — o risco aqui não é de má conduta, é de **percepção editorial**: revisores de periódicos de maior impacto tendem a exigir que pelo menos alguns parâmetros sejam ancorados em valores da literatura (meias-vidas de miRNA, taxas de degradação de proteína, constantes de Hill de repressão traducional), mesmo que o modelo continue qualitativo. Duas ações de baixo risco e alto retorno:
- Substituir 2–3 parâmetros-chave (ex.: meia-vida de miR-29/miR-107, taxa de degradação de BACE1) por valores com citação direta de estudo cinético real, mantendo os demais como exploratórios e sinalizados como tal.
- Reclassificar explicitamente essa seção do manuscrito como "modelo teórico/conceitual" em vez de misturá-la com "Resultados" experimentais — algo que o próprio texto já sinaliza no conteúdo, mas que a estrutura do artigo (se seguir o formato atual do TCC) ainda não deixa claro apenas pelo sumário.

### 2.7 [MÉDIO] 59% dos artigos classificados como "método indefinido"
O TCC já testa a sensibilidade dessa classificação (Tabela 8) e já reconhece a causa (dependência de menção explícita do método no resumo). Para o artigo, a correção completa é fazer mineração no **texto completo** (não apenas resumo) de uma subamostra maior — hoje isso é possível com leitura de texto integral via PubMed Central (artigos de acesso aberto) e por upload dos PDFs que a orientadora/o autor considerarem essenciais.

### 2.8 [BAIXO, MAS NECESSÁRIO] Padronização para o formato do periódico-alvo
Após decidido o periódico (Seção 4), reformatar seções, tabelas, limites de palavras, estilo de citação (Vancouver numérico é comum nas revistas biomédicas listadas abaixo, diferente do sistema autor-data ABNT usado no TCC) e figuras em resolução de publicação (300+ dpi, formato vetorial quando possível).

## 3. O que NÃO será feito (fora do escopo realista desta colaboração)

Para gerenciar expectativas com a orientadora: nenhum destes é factível dentro do protocolo "sem fabricar dados" e do escopo de um TCC/artigo derivado, a menos que envolvam colaboração externa:
- Geração de dados experimentais novos (wet-lab: qPCR, Western blot, ensaio de luciferase) — mencionado no próprio TCC como "prioridade imediata" de validação in vitro, mas exige laboratório, reagentes e tempo que este projeto de reanálise computacional não supre.
- Acesso a bases pagas sem credenciais ativas nesta sessão (ver Seção 5).

## 4. Periódicos-alvo realistas (compatíveis com o escopo de revisão integrativa + reanálise computacional)

Nenhum destes está garantido — a escolha final depende da extensão da reanálise de dados (Seção 2.4) e deve ser validada com a orientadora, mas todos têm escopo temático compatível e já publicam revisões/meta-análises com componente computacional sobre miRNAs em neurodegeneração:
- *Ageing Research Reviews* (Elsevier)
- *Progress in Neurobiology* (Elsevier)
- *Molecular Neurodegeneration* (BMC/Springer Nature)
- *npj Parkinson's Disease* (Nature Portfolio)
- *Neurobiology of Disease* (Elsevier)
- *Journal of Neuroinflammation* (BMC/Springer Nature)
- *Frontiers in Aging Neuroscience* / *Frontiers in Molecular Neuroscience*
- *International Journal of Molecular Sciences* (MDPI) — patamar de entrada mais acessível, ainda indexado e com bom alcance

## 5. Limitação importante desta sessão: acesso ao Scopus/ScienceDirect

O ambiente em que este trabalho está sendo conduzido é uma sessão remota do Claude Code, executada em contêiner na nuvem — **não há navegador Chrome local nem controle de sessão de navegador nesta sessão**, portanto não é possível usar o login do Scopus/ScienceDirect mantido no seu Chrome pessoal a partir daqui. As ferramentas disponíveis para literatura nesta sessão são: PubMed/MEDLINE (API oficial NCBI), PubMed Central (texto completo apenas para artigos de acesso aberto), e Scite.ai (busca e leitura de texto integral quando disponível, com relatório de citações). Para preencher a lacuna da Seção 2.1, há três caminhos práticos:
1. Você roda a busca Scopus/WoS localmente (no seu Chrome logado) e me envia os resultados exportados (RIS/CSV) para eu processar, desduplicar e integrar às análises.
2. Você usa uma sessão local do Claude Code (no seu computador, com esse Chrome logado) para essa etapa específica, e eu continuo daqui com o restante do pipeline.
3. Seguimos com a Rota B da Seção 2.1 (reportar honestamente a cobertura restrita ao PubMed nesta fase).

## 6. Plano faseado

| Fase | Entregável | Fonte de dados | Depende de |
|---|---|---|---|
| **0 — concluída nesta sessão** | Reestruturação do repositório (`data/raw`, `scripts/`, `docs/`, `results/`), correção de caminhos absolutos do Colab, correção de bug de execução (`col_mirna` indefinido), amostra real de 100 artigos PubMed com proveniência documentada | PubMed (API NCBI, real) | — |
| **1** | Recoleta completa do corpus PubMed atualizado (2.777+ registros), reaplicação do ranqueamento, decisão sobre Scopus/WoS (Seção 5) | PubMed + Scopus/WoS (se viabilizado) | Decisão do usuário sobre Seção 5 |
| **2** | Meta-análise quantitativa de acurácia diagnóstica/expressão para os 8–12 miRNAs mais consolidados | Artigos primários de texto completo (PMC OA + upload do usuário) | Leitura de texto completo |
| **3** | Reanálise de dado público de expressão (GEO/ArrayExpress) para pelo menos 1 eixo (ex.: miR-29/BACE1 em AD) | GEO/ArrayExpress (dados humanos reais depositados) | Escolha do(s) dataset(s) junto à orientadora |
| **4** | Validação cruzada de alvos (TargetScan + miRDB + DIANA-TarBase) e enriquecimento funcional (KEGG/Reactome) | Bases de alvos e vias, todas públicas | Fase 1 concluída |
| **5** | Revisão dos modelos EDO: ancoragem de 2–3 parâmetros em literatura cinética real; reclassificação editorial da seção como modelo teórico | Literatura cinética específica | Fase 2/4 |
| **6** | Redação do manuscrito no formato do periódico-alvo escolhido, com revisão de linguagem natural (sem marcas de escrita robotizada) | — | Fases 1–5 |
| **7** | Triple-check final: verificação cruzada de todos os números, DOIs, tabelas e figuras antes do envio à orientadora/submissão | — | Fase 6 |

## 7. Decisões que dependem de você e da orientadora

1. Como resolver o acesso Scopus/Web of Science (Seção 5, opções 1–3)?
2. Até que ponto investir na reanálise de dados públicos de expressão (Fase 3) — isso é o que mais eleva o "impacto científico real", mas também é a etapa mais demorada.
3. Prioridade do periódico-alvo (Seção 4), já que isso define formato, extensão e estilo de citação a adotar desde já.
4. Prazo desejado para a primeira versão do manuscrito revisado.

---
*Documento gerado como parte do processo de revisão colaborativa do TCC. Nenhum dado, contagem ou citação apresentado aqui foi fabricado; números do PubMed foram obtidos em tempo real via API oficial do NCBI em 10/09/2026 (ver `data/raw/pubmed/manifest.json`).*
