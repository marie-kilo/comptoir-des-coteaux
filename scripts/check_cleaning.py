#!/usr/bin/env python3
"""Contrôle les résultats du nettoyage des sources."""

import duckdb

DATABASE_PATH = "work/comptoir.duckdb"


def check_equal(actual, expected, message):
    """Lève une erreur si la valeur obtenue est différente de la valeur attendue."""
    if actual != expected:
        raise AssertionError(f"{message} - attendu : {expected}, obtenu : {actual}")


def main():
    con = duckdb.connect(DATABASE_PATH)

    erp_count = con.execute("SELECT COUNT(*) FROM erp_clean").fetchone()[0]

    liaison_count = con.execute("SELECT COUNT(*) FROM liaison_clean").fetchone()[0]

    web_count = con.execute("SELECT COUNT(*) FROM web_clean").fetchone()[0]

    erp_null_product_id = con.execute(
        """
        SELECT COUNT(*)
        FROM erp_clean
        WHERE product_id IS NULL OR TRIM(product_id) = ''
        """
    ).fetchone()[0]

    liaison_null_product_id = con.execute(
        """
        SELECT COUNT(*)
        FROM liaison_clean
        WHERE product_id IS NULL OR TRIM(product_id) = ''
        """
    ).fetchone()[0]

    web_null_sku = con.execute(
        """
        SELECT COUNT(*)
        FROM web_clean
        WHERE sku IS NULL OR TRIM(sku) = ''
        """
    ).fetchone()[0]

    con.close()

    print(f"ERP après nettoyage : {erp_count}")
    print(f"Liaison après nettoyage : {liaison_count}")
    print(f"Web après nettoyage : {web_count}")

    print(f"product_id manquants ERP : {erp_null_product_id}")
    print(f"product_id manquants liaison : {liaison_null_product_id}")
    print(f"sku manquants Web : {web_null_sku}")

    check_equal(
        erp_count,
        825,
        "Nombre de lignes ERP incorrect",
    )

    check_equal(
        liaison_count,
        825,
        "Nombre de lignes Liaison incorrect",
    )

    check_equal(
        web_count,
        1428,
        "Nombre de lignes Web incorrect",
    )

    check_equal(
        erp_null_product_id,
        0,
        "Valeurs product_id manquantes dans ERP",
    )

    check_equal(
        liaison_null_product_id,
        0,
        "Valeurs product_id manquantes dans Liaison",
    )

    check_equal(
        web_null_sku,
        0,
        "Valeurs sku manquantes dans Web",
    )

    print("Test nettoyage / valeurs manquantes : OK")


if __name__ == "__main__":
    main()
