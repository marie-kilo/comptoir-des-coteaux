#!/usr/bin/env python3
"""Contrôle un fichier CSV d'une catégorie de vins."""

import sys
from pathlib import Path

import pandas as pd


def main():
    if len(sys.argv) != 3:
        raise SystemExit(
            "Usage : python scripts/check_wine_category_export.py "
            "<fichier.csv> <nombre_attendu>"
        )

    file_path = Path(sys.argv[1])
    expected_count = int(sys.argv[2])

    if not file_path.exists():
        raise FileNotFoundError(f"Fichier introuvable : {file_path}")

    df = pd.read_csv(file_path)
    actual_count = len(df)

    print(f"Fichier contrôlé : {file_path}")
    print(f"Nombre de lignes : {actual_count}")
    print(f"Nombre attendu : {expected_count}")

    if actual_count != expected_count:
        raise AssertionError(
            f"Nombre de lignes incorrect : "
            f"attendu {expected_count}, obtenu {actual_count}"
        )

    print("Test export catégorie : OK")


if __name__ == "__main__":
    main()
