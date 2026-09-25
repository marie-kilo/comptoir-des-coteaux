#!/usr/bin/env python3
"""Analyse et charge une nouvelle source de données dans DuckDB."""

import sys
from pathlib import Path

import duckdb
import pandas as pd

DATABASE_PATH = "work/comptoir.duckdb"
TABLE_NAME = "extra_source_raw"


def load_source(file_path):
    """Charge une source Excel ou CSV dans un DataFrame pandas."""
    suffix = file_path.suffix.lower()

    if suffix in {".xlsx", ".xls"}:
        return pd.read_excel(file_path)

    if suffix == ".csv":
        return pd.read_csv(file_path)

    # Cas d'un fichier fourni par Kestra sans extension locale.
    try:
        return pd.read_excel(file_path)
    except Exception:  # noqa: BLE001
        try:
            return pd.read_csv(file_path)
        except Exception as error:
            raise ValueError(
                "Impossible d'identifier le format du fichier. "
                "Formats acceptés : Excel ou CSV."
            ) from error


def find_candidate_keys(df):
    """Recherche les colonnes pouvant servir de clé unique."""
    candidates = []

    for column in df.columns:
        missing = df[column].isna().sum()
        unique = df[column].nunique(dropna=False)

        if missing == 0 and unique == len(df):
            candidates.append(column)

    return candidates


def main():
    if len(sys.argv) != 2:
        raise SystemExit("Usage : python scripts/inspect_extra_source.py <fichier>")

    file_path = Path(sys.argv[1])

    if not file_path.exists():
        raise FileNotFoundError(f"Fichier introuvable : {file_path}")

    df = load_source(file_path)

    row_count = len(df)
    column_count = len(df.columns)
    duplicate_count = df.duplicated().sum()
    missing_by_column = df.isna().sum()
    candidate_keys = find_candidate_keys(df)

    print(f"Source analysée : {file_path.name}")
    print(f"Nombre de lignes : {row_count}")
    print(f"Nombre de colonnes : {column_count}")

    print("\nColonnes :")
    for column in df.columns:
        print(f"- {column}")

    print("\nValeurs manquantes :")
    for column, missing in missing_by_column.items():
        print(f"- {column} : {missing}")

    print(f"\nLignes entièrement dupliquées : {duplicate_count}")

    print("\nClés candidates :")
    if candidate_keys:
        for column in candidate_keys:
            print(f"- {column}")
    else:
        print("- aucune clé unique détectée automatiquement")

    Path("work").mkdir(exist_ok=True)

    con = duckdb.connect(DATABASE_PATH)
    con.register("extra_df", df)

    con.execute(
        f"""
        CREATE OR REPLACE TABLE {TABLE_NAME} AS
        SELECT *
        FROM extra_df
        """
    )

    loaded_count = con.execute(f"SELECT COUNT(*) FROM {TABLE_NAME}").fetchone()[0]

    con.unregister("extra_df")
    con.close()

    if loaded_count != row_count:
        raise AssertionError(
            "Le nombre de lignes chargées dans DuckDB "
            f"est incorrect : attendu {row_count}, obtenu {loaded_count}"
        )

    print(f"\nChargement DuckDB : {TABLE_NAME} ({loaded_count} lignes)")
    print("Analyse de la nouvelle source : OK")


if __name__ == "__main__":
    main()
