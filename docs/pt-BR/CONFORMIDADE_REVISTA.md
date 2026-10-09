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
| Folha de rosto: autor, afiliação como instituição, (departamento), cidade, (estado), país; autor correspondente com e-mail ativo; ORCID de 16 dígitos | **Parcial** | Faltavam cidade e país; agora constam na linha da afiliação, com a cidade do campus como `[VERIFICAR]`. O e-mail do autor correspondente é da USP e a afiliação é UNIFESP: confirme se é intencional. O ORCID consta. |
| Referências: números entre colchetes, numeradas na ordem da primeira citação; só obras publicadas ou aceitas; periódicos abreviados pela lista ISSN de abreviações; DOI como link completo | **Atendido** | 74 referências; todas com `https://doi.org/...`; periódicos abreviados. Uma entrada (Oliveira 2020, número do artigo) segue marcada `verify` em `refs.json`. |
| Tabelas: algarismos arábicos, citadas em ordem, com legenda; notas por letras minúsculas sobrescritas; feitas com a função de tabela | **Corrigido** | A única tabela do texto principal usava asterisco e trazia as notas dentro da legenda. Agora tem legenda curta, letra sobrescrita no cabeçalho e as notas abaixo da tabela. |
| Figuras: algarismos arábicos, citadas em ordem; partes por letras minúsculas; legendas no arquivo de texto, iniciadas por "Fig. n" em negrito | **Corrigido** | Os painéis das Figs 3 e 5 eram A e B; agora são a e b nas imagens e nas legendas. |
| Arquivos de figura nomeados `Fig1`, `Fig2`, ... | **Feito** | `Fig1.eps` a `Fig6.eps` e `Fig1.tif` a `Fig6.tif`, numerados na ordem do manuscrito. |
| Arte vetorial em EPS com fontes embutidas; arte de traço em bitmap a 1200 dpi ou mais | **Corrigido** | O par EPS é gravado junto com cada figura (`scripts/_journal_fit.py`); fontes embutidas. Os TIFF têm 1200 dpi, LZW. |
| Largura de 84 ou 174 mm, altura de no máximo 234 mm | **Corrigido** | Cinco das seis figuras eram mais largas que 174 mm e duas eram mais altas que 234 mm. Os doze arquivos (EN e PT) agora cabem; `results/tables/journal_figure_spec.csv` registra o tamanho e o `scripts/08` confere. |
| Texto em Helvetica ou Arial, consistente, em geral de 8 a 12 pt no tamanho final | **Parcial** | A fonte era DejaVu Sans. Agora é Liberation Sans, clone métrico do Arial (o Arial em si não está instalado aqui e não é redistribuível); reexporte pelo Word ou por um programa gráfico se a editora exigir o Arial propriamente dito. O menor texto tem 6,5 pt; toda figura do texto principal ainda tem rótulos entre 6,5 e 8 pt (de 27 a 458 por figura, ver a tabela de especificações). A faixa de 8 a 12 pt é descrita como usual, não obrigatória, mas as matrizes densas (Figs 3, 4 e 6) não chegam a 8 pt em 174 mm. |
| Toda linha com pelo menos 0,1 mm (0,3 pt) | **Atendido** | A linha mais fina tem 0,55 pt (tabela de especificações). |
| Cor é gratuita online; a informação principal tem de continuar visível em preto e branco | **Atendido** | Conferido em versões em tons de cinza: as células de risco de viés levam as letras L, U e H, a força da evidência também vai na forma do marcador, e o gráfico de desenho é uma rampa ordinal de um só matiz. |
| Notas de rodapé, não notas de fim | **Atendido** | Nenhuma é usada. |
| "Statements and Declarations" depois das Referências, com financiamento (agência e número), conflitos de interesse, aprovação ética e consentimento quando há pessoas ou animais, disponibilidade de dados para pesquisa original; contribuições dos autores recomendadas | **Atendido, com pendências** | Todas presentes. Pendentes: o nome da orientadora e a frase da segunda revisão (abaixo) e o DOI do repositório. |
| Revisões: declaração de quem teve a ideia, quem fez a busca e a análise, quem redigiu e revisou | **Atendido** | A declaração de autoria única está presente; inclua a orientadora só se a segunda revisão for concluída. |
| Informação suplementar citada no texto como figuras e tabelas | **Atendido** | As Tabelas Suplementares S1 a S13 são citadas pela primeira vez em ordem numérica. |
| Modelos de linguagem: não são autores; uso substancial documentado nos Métodos | **Atendido** | Métodos, "Use of a large language model", e a carta de apresentação. |
| Títulos com no máximo três níveis; siglas definidas na primeira menção; numeração de páginas automática | **Corrigido** | Uma varredura achou siglas usadas antes ou sem definição (entre elas AD, PD, AUC, ROC, CI, PET, OSF, NCBI, PRISMA-DTA, QUADAS-2, PROBAST, GRADE, ER e ORCA-Cas). Todas agora são definidas onde aparecem pela primeira vez, e as siglas que só aparecem dentro das figuras são definidas nas legendas. |

## Não encontrado nos resumos da página (confirmar na página atual)

- Limite de palavras e de referências para o tipo de artigo, e qual tipo escolher para uma revisão sistemática com metanálise. A página lista Original Research, Review, Brief Report e Comment, entre outros. O texto tem cerca de 7.500 palavras (da Introdução às Conclusões, sem legendas) e 74 referências.
- Regra de palavras-chave. O manuscrito traz seis, o que cabe na regra de 4 a 6 que a revista irmã *Cellular and Molecular Neurobiology* declara.
- Exigência de numeração de linhas. O arquivo tem linhas numeradas, o que não prejudica.
- Regra da revista sobre diretrizes de relato (segue-se o PRISMA-DTA) ou sobre registro (a revisão foi registrada retrospectivamente no OSF).
- Resumo gráfico, destaques, ou regra de largura de figura além de 84/174 mm.

## Ainda em aberto antes da submissão (não se fecha daqui)

1. `[VERIFICAR]` cidade do campus da UNIFESP (folha de rosto e carta de apresentação).
2. Segunda revisão independente: frase do resultado nos Métodos e nas Limitações, nome da orientadora e a frase de Author contributions. A revista em geral não permite mudar autores depois da submissão, então defina a lista de autores antes.
3. DOI persistente da versão do repositório (Zenodo) em Data availability.
4. Confirmar o domínio do e-mail do autor correspondente (USP) frente à afiliação (UNIFESP).
