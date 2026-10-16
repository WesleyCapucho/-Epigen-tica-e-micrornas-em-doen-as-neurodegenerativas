#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EN | The year a study carries in figures and supplementary tables. The extraction table records the
     year of first online publication, and the reference list of the manuscript gives the year of
     the volume, as Springer's style asks. For seven articles the two differ (an article published
     online in one year and assigned to a volume of the next), and a label that disagrees with the
     reference list sends the reader looking for a study that is not there. The volume year of
     those seven is declared, with the evidence for it, in data/extracted/citation_years.csv;
     every other study keeps its year. scripts/08 checks that the declared first-online year still
     matches the extraction table.
PT | O ano que um estudo leva nas figuras e nas tabelas suplementares. A tabela de extracao registra
     o ano da primeira publicacao online, e a lista de referencias do manuscrito da o ano do
     volume, como pede o estilo da Springer. Em sete artigos os dois diferem (artigo publicado online
     num ano e posto num volume do ano seguinte), e um rotulo que discorda da lista de referencias
     manda o leitor procurar um estudo que nao esta la. O ano do volume desses sete esta declarado,
     com a evidencia, em data/extracted/citation_years.csv; todo outro estudo mantem o seu ano. O
     scripts/08 confere que o ano de primeira publicacao declarado ainda bate com a tabela de extracao.
"""

import csv
import os

PATH = "data/extracted/citation_years.csv"
_TABLE = None


def _key(study_id):
    s = str(study_id).strip().lower().split("#")[0]
    return s[:-2] if s.endswith(".0") else s


def table():
    global _TABLE
    if _TABLE is None:
        _TABLE = {}
        if os.path.exists(PATH):
            for r in csv.DictReader(open(PATH, encoding="utf-8")):
                _TABLE[_key(r["study_id"])] = r
                _TABLE[_key(r["doi"])] = r
    return _TABLE


def citation_year(study_id, year):
    """EN/PT: the year of the reference list for this study | o ano da lista de referencias."""
    y = int(float(year))
    r = table().get(_key(study_id))
    if r is None:
        return y
    if y != int(r["year_first_online"]):
        raise ValueError(f"EN/PT: {study_id}: year {y} is not the first-online year {r['year_first_online']} "
                         f"declared in {PATH}")
    return int(r["citation_year"])


def label(first_author, year, study_id):
    """EN/PT: 'Author Year' with the year of the reference list | rotulo com o ano da lista de referencias."""
    return f"{str(first_author).strip()} {citation_year(study_id, year)}"
