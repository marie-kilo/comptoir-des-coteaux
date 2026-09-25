#!/usr/bin/env python3
"""Contrôle l'intégration d'une quatrième source."""

import duckdb

DATABASE_PATH = "work/comptoir.duckdb"
TABLE_NAME = "ventes_fusionnees"
EXPECTED_ROWS = 714


def main():
    con = duckdb.connect(DATABASE_PATH)

    row_count = con.execute(
        f"""
        SELECT COUNT(*)
        FROM {TABLE_NAME}
        """
    ).fetchone()[0]

    duplicate_product_id = con.execute(
        f"""
        SELECT COUNT(*) - COUNT(DISTINCT product_id)
        FROM {TABLE_NAME}
        """
    ).fetchone()[0]

    duplicate_sku = con.execute(
        f"""
        SELECT COUNT(*) - COUNT(DISTINCT sku)
        FROM {TABLE_NAME}
        """
    ).fetchone()[0]

    columns = [
        row[1] for row in con.execute(f"PRAGMA table_info('{TABLE_NAME}')").fetchall()
    ]

    con.close()

    extra_columns = [column for column in columns if column.startswith("extra_")]

    print(f"Lignes après intégration : {row_count}")
    print(f"Doublons product_id : {duplicate_product_id}")
    print(f"Doublons sku : {duplicate_sku}")
    print(f"Colonnes ajoutées : {len(extra_columns)}")

    for column in extra_columns:
        print(f"- {column}")

    if row_count != EXPECTED_ROWS:
        raise AssertionError(
            f"Nombre de lignes incorrect : attendu {EXPECTED_ROWS}, obtenu {row_count}"
        )

    if duplicate_product_id != 0:
        raise AssertionError(f"Doublons product_id détectés : {duplicate_product_id}")

    if duplicate_sku != 0:
        raise AssertionError(f"Doublons sku détectés : {duplicate_sku}")

    if not extra_columns:
        raise AssertionError("Aucune colonne de la quatrième source n'a été ajoutée.")

    print("Test intégration quatrième source : OK")


if __name__ == "__main__":
    main()
