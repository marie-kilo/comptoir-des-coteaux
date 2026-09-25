#!/usr/bin/env python3
"""Intègre une nouvelle source aux ventes fusionnées."""

import duckdb

DATABASE_PATH = "work/comptoir.duckdb"
BASE_TABLE = "ventes_fusionnees"
EXTRA_TABLE = "extra_source_raw"
ENRICHED_TABLE = "ventes_fusionnees_extra"

JOIN_KEYS = ("product_id", "sku", "id_web")


def quote_identifier(name):
    """Protège un nom de colonne utilisé dans une requête SQL."""
    return '"' + name.replace('"', '""') + '"'


def get_columns(con, table_name):
    """Retourne les colonnes d'une table DuckDB."""
    rows = con.execute(f"PRAGMA table_info('{table_name}')").fetchall()

    return [row[1] for row in rows]


def find_join_key(con, base_columns, extra_columns):
    """Recherche une clé commune unique et non nulle."""
    for key in JOIN_KEYS:
        if key not in base_columns or key not in extra_columns:
            continue

        key_sql = quote_identifier(key)

        missing_count = con.execute(
            f"""
            SELECT COUNT(*)
            FROM {EXTRA_TABLE}
            WHERE {key_sql} IS NULL
            """
        ).fetchone()[0]

        duplicate_count = con.execute(
            f"""
            SELECT COUNT(*) - COUNT(DISTINCT {key_sql})
            FROM {EXTRA_TABLE}
            WHERE {key_sql} IS NOT NULL
            """
        ).fetchone()[0]

        if missing_count == 0 and duplicate_count == 0:
            return key

    return None


def main():
    """Joint la quatrième source aux données de ventes."""
    con = duckdb.connect(DATABASE_PATH)

    base_columns = get_columns(con, BASE_TABLE)
    extra_columns = get_columns(con, EXTRA_TABLE)

    join_key = find_join_key(
        con,
        base_columns,
        extra_columns,
    )

    if join_key is None:
        con.close()
        raise ValueError(
            "Aucune clé de jointure exploitable détectée. "
            "Clés supportées : product_id, sku ou id_web."
        )

    print(f"Clé de jointure détectée : {join_key}")

    base_count = con.execute(f"SELECT COUNT(*) FROM {BASE_TABLE}").fetchone()[0]

    extra_count = con.execute(f"SELECT COUNT(*) FROM {EXTRA_TABLE}").fetchone()[0]

    join_key_sql = quote_identifier(join_key)

    matched_count = con.execute(
        f"""
        SELECT COUNT(*)
        FROM {BASE_TABLE} AS base
        INNER JOIN {EXTRA_TABLE} AS extra
            ON TRIM(CAST(base.{join_key_sql} AS VARCHAR))
             = TRIM(CAST(extra.{join_key_sql} AS VARCHAR))
        """
    ).fetchone()[0]

    if matched_count == 0:
        con.close()
        raise AssertionError(
            "La quatrième source ne correspond à aucune ligne des ventes fusionnées."
        )

    extra_columns_to_add = [column for column in extra_columns if column != join_key]

    extra_select = ""

    if extra_columns_to_add:
        selections = []

        for column in extra_columns_to_add:
            source = quote_identifier(column)
            alias = quote_identifier(f"extra_{column}")

            selections.append(f"extra.{source} AS {alias}")

        extra_select = ",\n    " + ",\n    ".join(selections)

    con.execute(
        f"""
        CREATE OR REPLACE TABLE {ENRICHED_TABLE} AS
        SELECT
            base.*
            {extra_select}
        FROM {BASE_TABLE} AS base
        LEFT JOIN {EXTRA_TABLE} AS extra
            ON TRIM(CAST(base.{join_key_sql} AS VARCHAR))
             = TRIM(CAST(extra.{join_key_sql} AS VARCHAR))
        """
    )

    enriched_count = con.execute(f"SELECT COUNT(*) FROM {ENRICHED_TABLE}").fetchone()[0]

    if enriched_count != base_count:
        con.close()
        raise AssertionError(
            "La jointure a modifié le nombre de ventes : "
            f"avant {base_count}, après {enriched_count}."
        )

    con.execute(
        f"""
        CREATE OR REPLACE TABLE {BASE_TABLE} AS
        SELECT *
        FROM {ENRICHED_TABLE}
        """
    )

    con.close()

    coverage = matched_count / base_count * 100

    print(f"Lignes ventes initiales : {base_count}")
    print(f"Lignes quatrième source : {extra_count}")
    print(f"Lignes correspondantes : {matched_count}")
    print(f"Couverture de jointure : {coverage:.2f} %")
    print(f"Lignes après jointure : {enriched_count}")
    print("Intégration de la quatrième source : OK")


if __name__ == "__main__":
    main()
