#!/usr/bin/env python3

"""Vérifie les résultats du dédoublonnage dans DuckDB."""

import duckdb

DATABASE_PATH = "work/comptoir.duckdb"


def main():
    """Contrôle les volumes et les doublons des tables dédoublonnées."""
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
    print()

    print(f"Liaison après dédoublonnage : {liaison_count}")
    print(f"Doublons liaison sur product_id : {liaison_duplicates}")
    print()

    print(f"Web après dédoublonnage : {web_count}")
    print(f"Doublons Web sur sku : {web_duplicates}")


if __name__ == "__main__":
    main()
