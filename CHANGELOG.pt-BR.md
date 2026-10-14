# Registro de mudanças

🇧🇷 English version: [CHANGELOG.md](CHANGELOG.md)

Cada versão é arquivada no Zenodo e tem DOI próprio.

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
