#!/usr/bin/env python3

"""Vérifie la cohérence de la jointure ERP + liaison + Web."""

import duckdb

DATABASE_PATH = "work/comptoir.duckdb"


def main():
    """Contrôle le volume et l'unicité des clés après jointure."""
    con = duckdb.connect(DATABASE_PATH)

    row_count = con.execute("SELECT COUNT(*) FROM ventes_fusionnees").fetchone()[0]

    product_count = con.execute(
        "SELECT COUNT(DISTINCT product_id) FROM ventes_fusionnees"
    ).fetchone()[0]

    sku_count = con.execute(
        "SELECT COUNT(DISTINCT sku) FROM ventes_fusionnees"
    ).fetchone()[0]

    duplicate_product = con.execute(
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

    null_keys = con.execute(
        """
        SELECT COUNT(*)
        FROM ventes_fusionnees
        WHERE product_id IS NULL
           OR id_web IS NULL
           OR sku IS NULL
        """
    ).fetchone()[0]

    con.close()

    print(f"Lignes après jointure : {row_count}")
    print(f"product_id uniques : {product_count}")
    print(f"sku uniques : {sku_count}")
    print(f"Doublons product_id : {duplicate_product}")
    print(f"Doublons sku : {duplicate_sku}")
    print(f"Clés manquantes après jointure : {null_keys}")


if __name__ == "__main__":
    main()
