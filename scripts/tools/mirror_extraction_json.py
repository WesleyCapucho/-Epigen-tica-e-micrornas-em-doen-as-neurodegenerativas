#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EN | Regenerate the JSON mirror of the diagnostic-accuracy extraction table.
PT | Regenera o espelho JSON da tabela de extracao de acuracia diagnostica.

EN | The extraction table is curated by hand in CSV, and a JSON copy of it is
     published beside it for readers who would rather not parse a CSV with
     embedded quotes. Two copies of the same data drift: the JSON sat at 76 rows
     while the CSV moved to 79, and only scripts/08 noticed. So the JSON is not a
     second source - it is generated from the CSV by this script, and scripts/08
     still fails if the two disagree, which now means the script was not run.
PT | A tabela de extracao e curada a mao em CSV, e uma copia em JSON e publicada
     ao lado dela para quem preferir nao analisar um CSV com aspas embutidas.
     Duas copias do mesmo dado divergem: o JSON ficou em 76 linhas enquanto o CSV
     foi para 79, e so o scripts/08 percebeu. Entao o JSON nao e uma segunda
     fonte - e gerado do CSV por este script, e o scripts/08 continua falhando se
     os dois discordarem, o que agora significa que o script nao foi rodado.

    python scripts/tools/mirror_extraction_json.py
"""

import csv
import json
import sys

CSV_PATH = "data/extracted/diagnostic_accuracy_extraction.csv"
JSON_PATH = "data/extracted/diagnostic_accuracy_extraction.json"


def main():
    csv.field_size_limit(10 ** 7)
    with open(CSV_PATH, encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    if not rows:
        sys.exit(f"EN/PT: {CSV_PATH} is empty")

    # EN/PT: dict order follows the CSV header, so the mirror reads like the table
    with open(JSON_PATH, "w", encoding="utf-8") as f:
        json.dump([dict(r) for r in rows], f, ensure_ascii=False, indent=1)
        f.write("\n")

    print(f"EN | {len(rows)} rows mirrored | PT | {len(rows)} linhas espelhadas")
    print(f"EN/PT: {CSV_PATH} -> {JSON_PATH}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
