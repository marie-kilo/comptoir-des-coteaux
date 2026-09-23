#!/usr/bin/env python3

"""Vérifie les tables créées après le nettoyage initial avec DuckDB."""

import duckdb

DATABASE_PATH = "work/comptoir.duckdb"


def main():
    """Affiche les tables disponibles et vérifie leur nombre de lignes."""
    con = duckdb.connect(DATABASE_PATH)

    tables = con.execute("SHOW TABLES").fetchall()

    print("Tables disponibles dans DuckDB :")
    for table in tables:
        print(f"- {table[0]}")

    print()

    erp_count = con.execute("SELECT COUNT(*) FROM erp_clean").fetchone()[0]

    liaison_count = con.execute("SELECT COUNT(*) FROM liaison_clean").fetchone()[0]

    web_count = con.execute("SELECT COUNT(*) FROM web_clean").fetchone()[0]

    con.close()

    print(f"ERP après nettoyage : {erp_count}")
    print(f"Liaison après nettoyage : {liaison_count}")
    print(f"Web après nettoyage : {web_count}")


if __name__ == "__main__":
    main()
