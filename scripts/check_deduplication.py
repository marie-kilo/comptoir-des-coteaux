#!/usr/bin/env python3
"""Contrôle le dédoublonnage des trois sources."""

import duckdb

DATABASE_PATH = "work/comptoir.duckdb"


def check_equal(actual, expected, message):
    """Lève une erreur si la valeur obtenue est différente de la valeur attendue."""
    if actual != expected:
        raise AssertionError(f"{message} - attendu : {expected}, obtenu : {actual}")


def main():
    con = duckdb.connect(DATABASE_PATH)

    erp_count = con.execute("SELECT COUNT(*) FROM erp_dedup").fetchone()[0]

    liaison_count = con.execute("SELECT COUNT(*) FROM liaison_dedup").fetchone()[0]

    web_count = con.execute("SELECT COUNT(*) FROM web_dedup").fetchone()[0]

    erp_duplicates = con.execute(
        """
        SELECT COUNT(*)
        FROM (
            SELECT product_id
            FROM erp_dedup
            GROUP BY product_id
            HAVING COUNT(*) > 1
        )
        """
    ).fetchone()[0]

    liaison_duplicates = con.execute(
        """
        SELECT COUNT(*)
        FROM (
            SELECT product_id
            FROM liaison_dedup
            GROUP BY product_id
            HAVING COUNT(*) > 1
        )
        """
    ).fetchone()[0]

    web_duplicates = con.execute(
        """
        SELECT COUNT(*)
        FROM (
            SELECT sku
            FROM web_dedup
            GROUP BY sku
            HAVING COUNT(*) > 1
        )
        """
    ).fetchone()[0]

    con.close()

    print(f"ERP après dédoublonnage : {erp_count}")
    print(f"Doublons ERP sur product_id : {erp_duplicates}")

    print(f"Liaison après dédoublonnage : {liaison_count}")
    print(f"Doublons Liaison sur product_id : {liaison_duplicates}")

    print(f"Web après dédoublonnage : {web_count}")
    print(f"Doublons Web sur sku : {web_duplicates}")

    check_equal(
        erp_count,
        825,
        "Nombre de lignes ERP après dédoublonnage incorrect",
    )

    check_equal(
        liaison_count,
        825,
        "Nombre de lignes Liaison après dédoublonnage incorrect",
    )

    check_equal(
        web_count,
        714,
        "Nombre de lignes Web après dédoublonnage incorrect",
    )

    check_equal(
        erp_duplicates,
        0,
        "Doublons détectés dans ERP",
    )

    check_equal(
        liaison_duplicates,
        0,
        "Doublons détectés dans Liaison",
    )

    check_equal(
        web_duplicates,
        0,
        "Doublons détectés dans Web",
    )

    print("Test absence de doublons : OK")


if __name__ == "__main__":
    main()
