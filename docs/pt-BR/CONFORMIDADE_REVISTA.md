# Artigo 1 frente às instruções para autores da Molecular Neurobiology

Conferido em 9 de outubro de 2026. Periódico-alvo: *Molecular Neurobiology* (Springer, periódico 12035).

## Como as instruções foram lidas, e o que isso limita

O site da Springer está bloqueado pela política de rede deste ambiente (`link.springer.com` e `www.springer.com` devolvem erro de conexão ou HTTP 403), de modo que a página
<https://link.springer.com/journal/12035/submission-guidelines> não pôde ser aberta diretamente. O conteúdo foi lido por uma ferramenta de busca que devolve um resumo da página. Cada exigência abaixo marcada como **lida** vem desses resumos, em várias consultas independentes que concordaram entre si. Um resumo não é a página: antes da submissão, abra a página atual e confirme os itens marcados como **não encontrado**. Nada foi preenchido de memória.

## Exigências lidas e situação do manuscrito

| Exigência (como lida) | Situação | Observação |
|---|---|---|
| Resumo de 150 a 250 palavras, sem siglas indefinidas nem referências não especificadas | **Corrigido** | O resumo usava PRISMA-DTA e QUADAS-2 sem definição. Agora nomeia a ferramenta por extenso e não cita mais a diretriz de relato por sigla. 243 palavras (contagem por espaços, como o Word conta). |
| Arquivos-fonte editáveis a cada submissão; texto em .docx | **Atendido** | `Manuscript1_*.docx` é um arquivo nativo do Word; as figuras são arquivos separados. |
| Folha de rosto: autor, afiliação como instituição, (departamento), cidade, (estado), país; autor correspondente com e-mail ativo; ORCID de 16 dígitos | **Parcial** | Faltavam cidade e país; a cidade do campus é Santos, SP, Brasil (informada pela autora em 13 de outubro) e a linha da afiliação agora termina com ela; a capa do TCC dá a unidade como Instituto de Saúde e Sociedade, Campus Baixada Santista. O e-mail do autor correspondente é da USP e a afiliação é UNIFESP; o autor confirmou em 14 de outubro que é intencional. O ORCID consta. |
| Referências: números entre colchetes, numeradas na ordem da primeira citação; só obras publicadas ou aceitas; periódicos abreviados pela lista ISSN de abreviações; DOI como link completo | **Atendido** | 74 referências, todas citadas no texto; todas, menos o livro, com `https://doi.org/...`; periódicos abreviados. O número do artigo fica de fora de três entradas da MDPI (Citterio 2023, Karaglani 2020, Oliveira 2020) porque o PubMed não o traz; acrescente-o pela página da editora antes da submissão. |
| Tabelas: algarismos arábicos, citadas em ordem, com legenda; notas por letras minúsculas sobrescritas; feitas com a função de tabela | **Corrigido** | A única tabela do texto principal usava asterisco e trazia as notas dentro da legenda. Agora tem legenda curta, letra sobrescrita no cabeçalho e as notas abaixo da tabela. |
| Figuras: algarismos arábicos, citadas em ordem; partes denotadas por letras minúsculas; legendas no arquivo de texto, iniciadas por "Fig. n" em negrito | **Atendido** | Os painéis das Figs 3 e 5 são a e b. O resumo das instruções diz letras minúsculas e o artigo Research publicado, enviado como modelo, as imprime assim, como "(a–c)" na legenda; o Brief Report publicado, enviado antes, usa maiúsculas, então a revista aceita as duas. |
| Arquivos de figura nomeados `Fig1`, `Fig2`, ... | **Feito** | `Fig1.eps` a `Fig6.eps` e `Fig1.tif` a `Fig6.tif`, numerados na ordem do manuscrito. |
| Arte vetorial em EPS com fontes embutidas; arte de traço em bitmap a 1200 dpi ou mais | **Corrigido** | O par EPS é gravado junto com cada figura (`scripts/_journal_fit.py`); fontes embutidas. Os TIFF têm 1200 dpi, LZW. |
| Largura de 84 ou 174 mm, altura de no máximo 234 mm | **Corrigido** | Cinco das seis figuras eram mais largas que 174 mm e duas eram mais altas que 234 mm. Os doze arquivos (EN e PT) agora cabem; `results/tables/journal_figure_spec.csv` registra o tamanho e o `scripts/08` confere. |
| Texto em Helvetica ou Arial, consistente, em geral de 8 a 12 pt no tamanho final | **Parcial** | A fonte era DejaVu Sans. Agora é Liberation Sans, clone métrico do Arial (o Arial em si não está instalado aqui e não é redistribuível); reexporte pelo Word ou por um programa gráfico se a editora exigir o Arial propriamente dito. O menor texto tem 6,5 pt; toda figura do texto principal ainda tem rótulos entre 6,5 e 8 pt (de 27 a 458 por figura, ver a tabela de especificações). A faixa de 8 a 12 pt é descrita como usual, não obrigatória, mas as matrizes densas (Figs 3, 4 e 6) não chegam a 8 pt em 174 mm. |
| Toda linha com pelo menos 0,1 mm (0,3 pt) | **Atendido** | A linha mais fina tem 0,55 pt (tabela de especificações). |
| Cor é gratuita online; a informação principal tem de continuar visível em preto e branco | **Atendido** | Conferido em versões em tons de cinza: as células de risco de viés levam as letras L, U e H, a força da evidência também vai na forma do marcador, e o gráfico de desenho é uma rampa ordinal de um só matiz. |
| Notas de rodapé, não notas de fim | **Atendido** | Nenhuma é usada. |
| "Statements and Declarations" depois das Referências, com financiamento (agência e número), conflitos de interesse, aprovação ética e consentimento quando há pessoas ou animais, disponibilidade de dados para pesquisa original; contribuições dos autores recomendadas | **Atendido, com pendências** | Todas presentes. Financiamento: nenhum, conforme confirmado pelo autor em 14 de outubro. Author contributions nomeia os dois autores. Pendente: o DOI do repositório precisa ser atualizado depois do próximo release (abaixo). |
| Revisões: declaração de quem teve a ideia, quem fez a busca e a análise, quem redigiu e revisou | **Atendido** | Declaração de dois autores: o primeiro autor teve a ideia, fez as buscas, extraiu e analisou os dados e redigiu o manuscrito; a orientadora supervisionou e revisou criticamente. |
| Informação suplementar citada no texto como figuras e tabelas | **Atendido** | As Tabelas Suplementares S1 a S13 são citadas pela primeira vez em ordem numérica. |
| Modelos de linguagem: não são autores; uso substancial documentado nos Métodos | **Atendido** | Métodos, "Use of a large language model", e a carta de apresentação. |
| Títulos com no máximo três níveis; siglas definidas na primeira menção; numeração de páginas automática | **Corrigido** | Uma varredura achou siglas usadas antes ou sem definição (entre elas AD, PD, AUC, ROC, CI, PET, OSF, NCBI, PRISMA-DTA, QUADAS-2, PROBAST, GRADE, ER e ORCA-Cas). Todas agora são definidas onde aparecem pela primeira vez, e as siglas que só aparecem dentro das figuras são definidas nas legendas. |

## O que os artigos publicados mostram (conferido em 13 de outubro de 2026)

Foram enviados dois artigos publicados da revista como modelo: Xu et al., *Mol Neurobiol* 2026;63:408, um artigo Research, [10.1007/s12035-026-05704-3](https://doi.org/10.1007/s12035-026-05704-3), e Huang et al., *Mol Neurobiol* 2026;63:409, um Brief Report, [10.1007/s12035-026-05684-4](https://doi.org/10.1007/s12035-026-05684-4). Dois resumos sistemáticos publicados também foram lidos pelo PubMed e pelo PubMed Central: Przywara et al. 2026, [10.1007/s12035-026-06247-3](https://doi.org/10.1007/s12035-026-06247-3), e Khan et al. 2026, [10.1007/s12035-026-06143-w](https://doi.org/10.1007/s12035-026-06143-w). Uma busca por título no PubMed encontra 116 registros da *Molecular Neurobiology* com "systematic review" ou "meta-analysis" no título, então esse tipo de artigo cabe na revista.

| Característica dos artigos publicados | O manuscrito |
|---|---|
| Resumo não estruturado em um parágrafo, depois "Keywords" separadas por " · " | Igual. |
| Lista de siglas em duas colunas logo depois das palavras-chave, nos dois artigos | **Incluída** depois das palavras-chave; toda sigla dela é definida no primeiro uso no texto. |
| Introdução, Métodos, Resultados, Discussão, Conclusão nessa ordem (artigo Research e revisões sistemáticas) | Mesma ordem. |
| Citações numeradas entre colchetes com intervalos (`[1–4]`), figuras citadas como `(Fig. 1a and b)` | Igual. |
| Legendas: "Fig. n" em negrito, uma frase de título, depois "(a) ... (b–d) ..." com letras em negrito | Feito: as seis legendas seguem esse formato. |
| Lista de referências: sobrenomes com iniciais, ano entre parênteses, título, periódico abreviado, `volume(número):primeira–última`, DOI como link quando existe | Igual, exceto que o manuscrito não traz o número do fascículo e usa hífen nas páginas. O exemplo da própria página de instruções também omite o fascículo, então é cosmético. |
| Declaração própria, "Declaration of Generative AI in Scientific Writing", entre as declarações do artigo Research | **Incluída** em Statements and Declarations; diz que o Claude foi usado e remete aos Métodos. |
| Contribuições dos autores escritas com papéis por pessoa (termos no estilo CRediT) no artigo Research | A nossa é uma frase; a revista aceita as duas. |
| Nos artigos compostos, as declarações vêm antes das referências | O manuscrito mantém as declarações depois das Referências, como a página de instruções diz; a editora reorganiza. |

## Não encontrado nos resumos da página (confirmar na página atual)

- Limite de palavras e de referências para o tipo de artigo, e qual tipo escolher para uma revisão sistemática com metanálise. A página lista Original Research, Review, Brief Report e Comment, entre outros. O texto tem cerca de 6.100 palavras (da Introdução às Conclusões, sem legendas) e 74 referências.
- Regra de palavras-chave. O manuscrito traz seis, o que cabe na regra de 4 a 6 que a revista irmã *Cellular and Molecular Neurobiology* declara.
- Exigência de numeração de linhas. O arquivo tem linhas numeradas, o que não prejudica.
- Regra da revista sobre diretrizes de relato (segue-se o PRISMA-DTA) ou sobre registro (a revisão foi registrada retrospectivamente no OSF).
- Resumo gráfico, destaques, ou regra de largura de figura além de 84/174 mm.

## Ainda em aberto antes da submissão (não se fecha daqui)

1. O arquivo do manuscrito se perdeu quando a sessão na nuvem foi reiniciada e foi reconstruído em 14 de outubro de 2026 a partir do repositório, com todo número lido de `results/tables/manuscript_numbers.json`. A versão reconstruída tem a afiliação com "Santos, SP, Brazil", a lista de siglas, as legendas reescritas, as imagens novas das figuras e a declaração "Declaration of Generative AI in Scientific Writing". Pode diferir na redação da versão enviada antes.
2. Coautora: a orientadora, Profa. Dra. Roberta Sessa Stilhano Yamaguchi, é coautora (decisão do autor em 14 de outubro) e consta como segunda autora. Em aberto: o ORCID dela, a ser tomado do próprio registro dela no ORCID; a(s) afiliação(ões) que ela quer listar (a capa do TCC dá o Instituto de Saúde e Sociedade, UNIFESP, Campus Baixada Santista; o PubMed mostra as publicações dela de 2026 no Departamento de Ciências Fisiológicas da Faculdade de Ciências Médicas da Santa Casa de São Paulo); a forma do nome (os trabalhos anteriores estão indexados como Stilhano RS); e a aprovação dela da versão final. A revista em geral não permite mudar autores depois da submissão. Uma segunda revisão independente não consta no artigo, por decisão do autor; o desenho de revisor único continua declarado nos Métodos e nas limitações porque o item 9 do PRISMA-DTA pede o número de revisores.
3. DOI do repositório: feito em 13 de outubro de 2026. A versão 1.0.0 está arquivada no Zenodo como [10.5281/zenodo.23353780](https://doi.org/10.5281/zenodo.23353780) (MIT para os scripts, CC BY 4.0 para os dados; os arquivos de exportação do Scopus e da Web of Science não estão no arquivo). A declaração de disponibilidade de dados do manuscrito diz isso. O arquivo ainda não traz os commits posteriores (o contraste de efeitos aleatórios dos subgrupos, o `scripts/35` e os documentos atualizados), então é preciso publicar um *release* novo depois de mesclar o ramo e confirmar o DOI no manuscrito.
4. Fechado em 14 de outubro: o domínio do e-mail do autor correspondente (USP) frente à afiliação (UNIFESP) é intencional.
