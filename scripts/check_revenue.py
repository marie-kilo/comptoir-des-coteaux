#!/usr/bin/env python3
"""Contrôle la cohérence du chiffre d'affaires."""

from decimal import Decimal

import duckdb

DATABASE_PATH = "work/comptoir.duckdb"


def check_equal(actual, expected, message):
    """Lève une erreur si la valeur obtenue est différente de la valeur attendue."""
    if actual != expected:
        raise AssertionError(f"{message} - attendu : {expected}, obtenu : {actual}")


def main():
    con = duckdb.connect(DATABASE_PATH)

    product_count = con.execute("SELECT COUNT(*) FROM ca_par_produit").fetchone()[0]

    total_revenue = con.execute(
        """
        SELECT chiffre_affaires_total
        FROM ca_total
        """
    ).fetchone()[0]

    missing_revenue = con.execute(
        """
        SELECT COUNT(*)
        FROM ca_par_produit
        WHERE chiffre_affaires IS NULL
        """
    ).fetchone()[0]

    inconsistent_revenue = con.execute(
        """
        SELECT COUNT(*)
        FROM ca_par_produit
        WHERE chiffre_affaires <> price * total_sales
        """
    ).fetchone()[0]

    missing_inputs = con.execute(
        """
        SELECT COUNT(*)
        FROM ca_par_produit
        WHERE price IS NULL
           OR total_sales IS NULL
        """
    ).fetchone()[0]

    con.close()

    print(f"Nombre de produits avec CA : {product_count}")
    print(f"CA total : {total_revenue}")
    print(f"CA manquants : {missing_revenue}")
    print(f"CA incohérents : {inconsistent_revenue}")
    print(f"Prix ou ventes manquants : {missing_inputs}")

    check_equal(
        product_count,
        714,
        "Nombre de produits avec CA incorrect",
    )

    check_equal(
        total_revenue,
        Decimal("70568.60"),
        "Chiffre d'affaires total incorrect",
    )

    check_equal(
        missing_revenue,
        0,
        "Chiffres d'affaires manquants",
    )

    check_equal(
        inconsistent_revenue,
        0,
        "Calculs de chiffre d'affaires incohérents",
    )

    check_equal(
        missing_inputs,
        0,
        "Prix ou volumes de ventes manquants",
    )

    print("Test cohérence du chiffre d'affaires : OK")


if __name__ == "__main__":
    main()
