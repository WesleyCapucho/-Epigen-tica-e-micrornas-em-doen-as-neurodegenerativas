# Article 1 against the author instructions of Molecular Neurobiology

Checked on 9 October 2026. Target journal: *Molecular Neurobiology* (Springer, journal 12035).

## How the instructions were read, and what that limits

The Springer site is blocked by this environment's network policy (`link.springer.com` and `www.springer.com` return a connection error or HTTP 403), so the page
<https://link.springer.com/journal/12035/submission-guidelines> could not be opened directly. Its content was read through a search tool that returns a summary of the page. Every requirement below that is marked **read** comes from those summaries, in several independent queries that agreed with each other. A summary is not the page: before submission, open the live page and confirm the items marked **not found**. Nothing here was filled in from memory.

## Requirements that were read, and the state of the manuscript

| Requirement (as read) | State | Note |
|---|---|---|
| Abstract of 150 to 250 words, no undefined abbreviations, no unspecified references | **Fixed** | The abstract used PRISMA-DTA and QUADAS-2 without definition. It now names the tool in full and no longer cites the reporting guideline by acronym. 243 words (whitespace count, as Word counts them). |
| Editable source files at every submission; text as .docx | **Met** | `Manuscript1_*.docx` is a native Word file; figures are separate files. |
| Title page: author name, affiliation as institution, (department), city, (state), country; corresponding author with an active e-mail; 16-digit ORCID | **Partly met** | City and country were missing and are now in the affiliation line, with the city of the campus left as `[VERIFICAR]`. The corresponding e-mail is a USP address while the affiliation is UNIFESP: confirm that this is intended. ORCID is present. |
| References: numbers in square brackets, numbered consecutively in order of first citation; only published or accepted works; journal names abbreviated per the ISSN List of Title Word Abbreviations; DOI as a full link | **Met** | 74 references; every entry carries `https://doi.org/...`; journal names are abbreviated. One entry (Oliveira 2020, article number) stays flagged `verify` in `refs.json`. |
| Tables: Arabic numerals, cited in order, with a caption; footnotes by superscript lower-case letters; built with the table function | **Fixed** | The only main-text table used an asterisk and carried its notes inside the caption. It now has a short caption, a superscript letter in the header and the notes below the table. |
| Figures: Arabic numerals, cited in order; parts denoted by lower-case letters; captions in the text file, starting with bold "Fig. n" | **Fixed** | Panels of Fig. 3 and Fig. 5 were A and B; they are now a and b in the images and the captions. |
| Figure files named `Fig1`, `Fig2`, ... | **Done** | `Fig1.eps` to `Fig6.eps` and `Fig1.tif` to `Fig6.tif`, made from `results/figures/<name>.en.*` and numbered in manuscript order. They are delivered with the manuscript and not stored in the repository (the TIFF files are 2.6 to 9.8 MB each). |
| Vector art as EPS with fonts embedded; bitmap line art at 1200 dpi or more | **Fixed** | EPS twins are written with each figure (`scripts/_journal_fit.py`); fonts are embedded. TIFF files are 1200 dpi, LZW. |
| Width 84 or 174 mm, height at most 234 mm | **Fixed** | Five of the six figures were wider than 174 mm and two were taller than 234 mm. All twelve files (EN and PT) now fit; `results/tables/journal_figure_spec.csv` records the size and `scripts/08` checks it. |
| Lettering in Helvetica or Arial, consistent, usually 8 to 12 pt at final size | **Partly met** | The font was DejaVu Sans. It is now Liberation Sans, the metric-compatible clone of Arial (Arial itself is not installed here and is not redistributable); re-export from Word or a graphics program if the editorial office insists on Arial proper. Smallest lettering is 6.5 pt; every main-text figure still carries some lettering between 6.5 and 8 pt (27 to 458 labels per figure, see the spec table). The 8 to 12 pt range is described as usual, not mandatory, but the dense matrices (Figs 3, 4, 6) cannot reach 8 pt at 174 mm. |
| Every line at least 0.1 mm (0.3 pt) | **Met** | Thinnest line is 0.55 pt (checked in the spec table). |
| Colour is free online; the main information must still be visible in black and white | **Met** | Checked on grey-scale renderings: the risk-of-bias cells carry the letters L, U and H, evidence strength is also carried by marker shape, and the design chart is an ordinal one-hue ramp. |
| Footnotes, not endnotes | **Met** | None are used. |
| "Statements and Declarations" after the References, with funding (agency and grant number), competing interests, ethics approval and consent where people or animals are involved, data availability for original research; author contributions encouraged | **Met, with open items** | All present. Open: the supervisor's name and the second-review sentence (see below), and the repository DOI. |
| Reviews: statement of who had the idea, who did the search and analysis, who drafted and revised | **Met** | Single-author statement is present; add the supervisor only if the second review is completed. |
| Supplementary information cited in the text like figures and tables | **Met** | Supplementary Tables S1 to S13 are first cited in numerical order. |
| Large language models: not an author; substantive use documented in the Methods | **Met** | Methods, "Use of a large language model", and the cover letter. |
| Headings no deeper than three levels; abbreviations defined at first mention; footnote and page numbering automatic | **Fixed** | A scan found abbreviations used before or without a definition (among them AD, PD, AUC, ROC, CI, PET, OSF, NCBI, PRISMA-DTA, QUADAS-2, PROBAST, GRADE, ER and ORCA-Cas). All are now defined where they first appear, and the abbreviations that only appear inside figures are defined in the captions. |

## Not found in the page summaries (confirm on the live page)

- Word limit and reference limit for the article type, and which type to choose for a systematic review and meta-analysis. The page lists Original Research, Review, Brief Report and Comment, among others. The body text is about 7,500 words (Introduction to Conclusions, captions excluded) with 74 references.
- A keyword rule. The manuscript gives six keywords, which fits the 4 to 6 rule that the sister journal *Cellular and Molecular Neurobiology* states.
- Any line-numbering requirement. The file is line-numbered, which does no harm.
- A journal rule on reporting guidelines (PRISMA-DTA is followed) or on registration (the review was registered retrospectively on OSF).
- A graphical abstract, highlights, or a specific figure-width rule beyond 84/174 mm.

## Still open before submission (cannot be closed from here)

1. `[VERIFICAR]` city of the UNIFESP campus (title page and cover letter).
2. Independent second review: outcome sentence in Methods and Limitations, the supervisor's name and the Author contributions sentence. The journal generally does not allow author changes after submission, so decide the author list first.
3. Persistent DOI for the repository release (Zenodo) in Data availability.
4. Confirm the corresponding author's e-mail domain (USP) against the affiliation (UNIFESP).
