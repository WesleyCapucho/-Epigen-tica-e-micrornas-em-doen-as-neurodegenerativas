# Registro de mudanças

🇧🇷 English version: [CHANGELOG.md](CHANGELOG.md)

Cada versão é arquivada no Zenodo e tem DOI próprio.

## 1.2.0 (2026-10-14)

### Corrigido

- **Fator de mimético e queda de BACE1 exigida (`scripts/12`).** O fator de mimético que leva o pool de monômero da DA de volta ao do controle era achado por busca em grade com passo de 0,247, e o primeiro ponto da grade além da meta, 1,494, era reportado. Ele ultrapassa, e a queda de BACE1 calculada nesse ponto parecia uma faixa de 30–33% ao longo da força de repressão. As duas grandezas têm forma fechada. A queda exigida é 1 − 1/R = 29,2%, com R = 1,4126 a razão DA sobre controle de produção sobre depuração, e é a mesma em todo valor dos parâmetros livres. O fator de mimético que a entrega é 1,424 no ponto médio da força de repressão e 1,415 a 1,475 em sua faixa declarada (0,1 a 3). Ambas são agora calculadas em forma fechada e conferidas integrando a EDO (erro relativo 3 × 10⁻¹⁰). As chaves de `ode_calibrated_results.json` mudaram junto (`required_BACE1_knockdown`, `mimic_fold_to_offset_clearance`, `required_over_measured_knockdown`); `scripts/08`, `scripts/18` e o texto dos métodos acompanham.
- **Varredura de parâmetros livres (`scripts/12`).** Duas das 18 execuções eram reportadas como não avaliáveis porque o bloco ilustrativo de agregação divergia nos cantos k_repress = 0,1 e k_translate = 5. A varredura pergunta pelo pool de monômero, que esse bloco não pode mudar, então agora integra só a cascata do monômero. As 18 execuções são avaliáveis e devolvem a razão DA sobre controle 1,4126 até 10⁻⁹.
- **Ordens de reação do Aβ42 (`scripts/12`).** As duas ordens eram lidas ao contrário: a ordem da nucleação primária pegava a linha da secundária (K012) e vice-versa. As duas linhas valem 2, então nenhuma saída mudou, mas o `scripts/08` agora confere que K013 é a ordem primária e K012 a secundária, e que o código as lê assim.
- `scripts/18`: a concentração de meia-saturação da elongação da α-sinucleína é rotulada m½ no resumo gráfico. Estava rotulada M*, o símbolo que a concentração crítica de fibrila do Aβ42 carrega em todo o resto.

### Alterado

- O rótulo da queda K058 foi corrigido nos `scripts/12`, `36`, `37` e `08` e no texto de métodos: a linha K058 é a queda da proteína SNCA a partir de um construto que carrega a região codificante e a 3′UTR em células HEK-293 (western blot), e não um repórter de 3′UTR. Mudou só o rótulo; nenhum valor mudou.
- Documentos e texto dos scripts não chamam mais de pré-especificados a regra de seleção, os subgrupos nem a regra de plausibilidade dos intervalos, porque o registro é retrospectivo.
- A limitação sobre a extração restrita a acesso aberto agora diz que 40 dos 95 registros do PubMed com medida de acurácia no resumo não tinham texto completo aberto e não foram extraídos, e que outros 44 registros desse braço não contribuíram com valor sem motivo registrado um a um (README, métodos, dicionário de dados, checklist PRISMA-DTA, notas de conformidade com o periódico).

### Adicionado

- `scripts/36_mimic_target_response.py`, `results/tables/mimic_target_response.csv` (330 cenários) e `mimic_target_response.json`: o que um mimético dosado repetidamente faz com a proteína que ele mira, com a meia-vida medida de cada etapa (miRNA, mRNA, proteína e, no braço da DA, o monômero de Aβ42). A força de repressão entra por um número só, ρ, o decaimento que o miRNA soma ao do mRNA no basal, em unidades do decaimento intrínseco do mRNA. A única observação de perda de função da tabela de parâmetros (K065) põe um piso nela para miR-7 e miR-153 juntos (ρ no mínimo 0,44), abaixo da varredura declarada, e nada diz do miR-7 sozinho; uma varredura sobre ρ de 0,01 a 10⁴ (`mimic_target_rho_sweep.csv`) dá, para cada cenário, o menor pico diário sobre todo ρ. A proteína média no ciclo é resolvida exatamente no estado estacionário periódico, e a dose que alcança a queda exigida é reportada com o pico de que precisa, a dose que a forma fechada do estado estacionário pediria e a oscilação da proteína. O escalonamento da taxa de nucleação do Aβ42 a partir das ordens de reação medidas está no mesmo arquivo. Seis checagens independentes de verificação precisam passar antes de a tabela ser escrita; o `scripts/08` acrescenta 45 checagens sobre as saídas e sobre o texto dos métodos que as cita.
- `scripts/37_manuscript2_numbers.py` e `results/tables/manuscript2_numbers.json`: todo número que o manuscrito do Artigo 2 cita, lido das tabelas dos `scripts/12`, `17` e `36` e da tabela de parâmetros, com asserts por trás de cada frase que depende de um padrão nos dados. Também afirma, com assert, que o menor pico diário da grade de ρ limita a dose para qualquer ρ: em cada série o pico sobe quando ρ cai abaixo do mínimo e já convergiu no topo da grade (muda no máximo 0,1% na última década). Só números; o texto do manuscrito não faz parte deste repositório.
- `scripts/38_mechanistic_figures.py` e `results/figures/mech_*.{en,pt-BR}.{png,pdf,eps}`: as cinco figuras do texto principal do estudo mecanístico (estrutura dos dois modelos, braço de Alzheimer, braço de Parkinson, rotatividade do microRNA administrado, resposta no alvo), no estilo compartilhado e ajustadas aos limites de arte do periódico. Todo número nelas é lido, na hora de desenhar, das tabelas dos `scripts/12`, `17` e `36` e da tabela de parâmetros; o `scripts/08` acrescenta as verificações de arte para os cinco nomes.
- `scripts/35_manuscript_numbers.py` ganha as contagens que uma revisão externa do manuscrito do Artigo 1 exigiu (contabilidade do braço por resumo, estimativas que não puderam ser ponderadas, estudos cujo delineamento pôde ser avaliado, AUCs perto de 0,90, contagens de estudos de revisões anteriores, a faixa das análises alternativas), cada uma com um assert. Nenhum valor existente mudou.

## 1.1.0 (2026-10-14)

Arquivada no Zenodo como [10.5281/zenodo.23368166](https://doi.org/10.5281/zenodo.23368166) (tag git `v1.1.0`).

### Alterado

- **Teste de subgrupos painel versus isolado.** O teste Q entre subgrupos não levava em conta a variância entre estudos e, com I² de 60% a 80% nos pools, dava valores de p pequenos demais. `subgroup_difference_test` (`scripts/05_meta_analysis.py`) agora também devolve um contraste de efeitos aleatórios: a diferença das AUCs logit agregadas dos dois subgrupos, cada uma com seu próprio τ² de Paule-Mandel e seu erro-padrão de Hartung-Knapp, referida a uma distribuição t com graus de liberdade de Welch-Satterthwaite (`diff_logit_RE`, `se_RE`, `df_RE`, `p_value_RE`). O p baseado em Q fica nas tabelas. Para a DP os dois dão p < 0,0001 e p = 0,041, para o conjunto combinado p = 0,0004 e p = 0,073, para a DA p = 0,65 e p = 0,69.
- O contraste foi levado para `robustness_alternative_analyses.csv`, `robustness_random_selection.csv` e `robustness_validation_split_exploratory.csv` (`scripts/26`) e para a Fig. 5b (`robustness_specification.*`, `scripts/33`). Nas 2.000 seleções aleatórias, o p de efeitos aleatórios fica abaixo de 0,05 em 9% das seleções na DP, contra 95% para o p baseado em Q.
- O `scripts/08_verify_consistency.py` confere o contraste contra as estimativas agregadas guardadas (9 conferências novas, 4309 no total).

### Acrescentado

- `scripts/35_manuscript_numbers.py` e `results/tables/manuscript_numbers.json`: todo número que o manuscrito do Artigo 1 cita, lido das tabelas de resultado, com o arquivo de origem de cada valor. Só números; o texto do manuscrito não faz parte deste repositório.
- `CHANGELOG.md` e `CHANGELOG.pt-BR.md`.

### Documentação

- README, métodos, dicionário de dados, lista de conferência PRISMA-DTA e notas de conformidade com a revista alinhados aos resultados atuais: registro retrospectivo no OSF, agregação de Paule-Mandel com intervalos de Hartung-Knapp modificados, passos GRADE, I², resultados de Egger, contrastes excluídos, ponto de operação bivariado, faixa das razões de plausibilidade dos intervalos.
- A tabela de Correções tem uma décima quarta entrada (o teste de subgrupos baseado em Q).
- A orientadora e a unidade foram registradas a partir da capa do TCC; as decisões sobre coautoria, financiamento e e-mail do autor correspondente estão nas notas de conformidade.

### Sem mudança

- Toda estimativa agregada, os julgamentos do QUADAS-2, as classificações GRADE e o resumo bivariado são os da 1.0.0.

## 1.0.0 (2026-10-13)

Arquivada no Zenodo como [10.5281/zenodo.23353780](https://doi.org/10.5281/zenodo.23353780) (tag git `v1.0.0`).

- Primeira versão arquivada: registros de busca (PubMed, Scopus, Web of Science), decisões de triagem e verificação de recall; tabelas de extração com a frase-fonte de cada valor e o registro de auditoria; análises de QUADAS-2, GRADE e robustez (47 estudos elegíveis, 37 nos pools primários); scripts de análise e de figuras (`scripts/01` a `33`) e o script de consistência (4300 conferências); tabelas de resultado e figuras em inglês e português.
- Scripts sob MIT, dados, tabelas, figuras e documentação sob CC BY 4.0. Os arquivos de exportação da Scopus e da Web of Science não são distribuídos; `exports_manifest.csv` lista a contagem de registros e o SHA-256 de cada um.
