#!/usr/bin/env python3

"""Exécute un script SQL DuckDB dans la base locale du projet."""

import sys
from pathlib import Path

import duckdb

DATABASE_PATH = "work/comptoir.duckdb"


def main():
    """Exécute le fichier SQL fourni en argument."""
    if len(sys.argv) != 2:
        raise SystemExit("Usage : python scripts/run_sql.py <fichier.sql>")

    sql_path = Path(sys.argv[1])

    if not sql_path.exists():
        raise FileNotFoundError(f"Fichier SQL introuvable : {sql_path}")

    sql = sql_path.read_text(encoding="utf-8")

    con = duckdb.connect(DATABASE_PATH)

    con.execute("INSTALL excel")
    con.execute("LOAD excel")

    con.execute(sql)

    con.close()

    print(f"Script exécuté avec succès : {sql_path}")


if __name__ == "__main__":
    main()
