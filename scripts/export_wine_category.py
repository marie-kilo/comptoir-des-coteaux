#!/usr/bin/env python3
"""Exporte une catégorie de vins depuis la base DuckDB."""

import sys
from pathlib import Path

import duckdb


def main():
    if len(sys.argv) != 4:
        raise SystemExit(
            "Usage : python scripts/export_wine_category.py "
            "<database> <category> <output>"
        )

    database_path = sys.argv[1]
    category = sys.argv[2].lower()
    output_path = Path(sys.argv[3])

    if category == "premium":
        table_name = "vins_premium"
        expected_count = 30

    elif category == "ordinaire":
        table_name = "vins_ordinaires"
        expected_count = 684

    else:
        raise ValueError("Catégorie invalide. Utiliser 'premium' ou 'ordinaire'.")

    output_path.parent.mkdir(parents=True, exist_ok=True)

    con = duckdb.connect(database_path)

    df = con.execute(
        f"""
        SELECT *
        FROM {table_name}
        ORDER BY z_score DESC
        """
    ).df()

    con.close()

    row_count = len(df)

    if row_count != expected_count:
        raise AssertionError(
            f"Nombre de vins {category} incorrect : "
            f"attendu {expected_count}, obtenu {row_count}"
        )

    df.to_csv(
        output_path,
        index=False,
        encoding="utf-8",
    )

    print(f"Catégorie : {category}")
    print(f"Nombre de vins : {row_count}")
    print(f"Fichier créé : {output_path}")
    print(f"Export {category} : OK")


if __name__ == "__main__":
    main()
