#!/usr/bin/env python3
"""Contrôle la cohérence de la jointure ERP / Liaison / Web."""

import duckdb

DATABASE_PATH = "work/comptoir.duckdb"


def check_equal(actual, expected, message):
    """Lève une erreur si la valeur obtenue est différente de la valeur attendue."""
    if actual != expected:
        raise AssertionError(f"{message} - attendu : {expected}, obtenu : {actual}")


def main():
    con = duckdb.connect(DATABASE_PATH)

    row_count = con.execute("SELECT COUNT(*) FROM ventes_fusionnees").fetchone()[0]

    unique_product_id = con.execute(
        """
        SELECT COUNT(DISTINCT product_id)
        FROM ventes_fusionnees
        """
    ).fetchone()[0]

    unique_sku = con.execute(
        """
        SELECT COUNT(DISTINCT sku)
        FROM ventes_fusionnees
        """
    ).fetchone()[0]

    duplicate_product_id = con.execute(
        """
        SELECT COUNT(*)
        FROM (
            SELECT product_id
            FROM ventes_fusionnees
            GROUP BY product_id
            HAVING COUNT(*) > 1
        )
        """
    ).fetchone()[0]

    duplicate_sku = con.execute(
        """
        SELECT COUNT(*)
        FROM (
            SELECT sku
            FROM ventes_fusionnees
            GROUP BY sku
            HAVING COUNT(*) > 1
        )
        """
    ).fetchone()[0]

    missing_keys = con.execute(
        """
        SELECT COUNT(*)
        FROM ventes_fusionnees
        WHERE product_id IS NULL
           OR id_web IS NULL
           OR sku IS NULL
           OR TRIM(product_id) = ''
           OR TRIM(id_web) = ''
           OR TRIM(sku) = ''
        """
    ).fetchone()[0]

    inconsistent_links = con.execute(
        """
        SELECT COUNT(*)
        FROM ventes_fusionnees
        WHERE TRIM(id_web) <> TRIM(sku)
        """
    ).fetchone()[0]

    con.close()

    print(f"Lignes après jointure : {row_count}")
    print(f"product_id uniques : {unique_product_id}")
    print(f"sku uniques : {unique_sku}")
    print(f"Doublons product_id : {duplicate_product_id}")
    print(f"Doublons sku : {duplicate_sku}")
    print(f"Clés manquantes après jointure : {missing_keys}")
    print(f"Correspondances id_web / sku incohérentes : {inconsistent_links}")

    check_equal(
        row_count,
        714,
        "Nombre de lignes après jointure incorrect",
    )

    check_equal(
        unique_product_id,
        714,
        "Nombre de product_id uniques incorrect",
    )

    check_equal(
        unique_sku,
        714,
        "Nombre de sku uniques incorrect",
    )

    check_equal(
        duplicate_product_id,
        0,
        "Doublons product_id après jointure",
    )

    check_equal(
        duplicate_sku,
        0,
        "Doublons sku après jointure",
    )

    check_equal(
        missing_keys,
        0,
        "Clés manquantes après jointure",
    )

    check_equal(
        inconsistent_links,
        0,
        "Correspondances id_web / sku incohérentes",
    )

    print("Test cohérence des jointures : OK")


if __name__ == "__main__":
    main()
