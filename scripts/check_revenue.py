#!/usr/bin/env python3

"""Vérifie le calcul du chiffre d'affaires dans DuckDB."""

import duckdb

DATABASE_PATH = "work/comptoir.duckdb"


def main():
    """Contrôle le CA par produit et le CA total."""
    con = duckdb.connect(DATABASE_PATH)

    product_count = con.execute("SELECT COUNT(*) FROM ca_par_produit").fetchone()[0]

    total_revenue = con.execute(
        "SELECT chiffre_affaires_total FROM ca_total"
    ).fetchone()[0]

    null_revenue = con.execute(
        """
        SELECT COUNT(*)
        FROM ca_par_produit
        WHERE chiffre_affaires IS NULL
        """
    ).fetchone()[0]

    con.close()

    print(f"Nombre de produits avec CA : {product_count}")
    print(f"CA total : {total_revenue}")
    print(f"CA manquants : {null_revenue}")


if __name__ == "__main__":
    main()
