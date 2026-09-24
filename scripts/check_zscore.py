#!/usr/bin/env python3

"""Vérifie le calcul du z-score et la classification des vins."""

import duckdb

DATABASE_PATH = "work/comptoir.duckdb"


def main():
    """Contrôle les résultats du classement premium / ordinaire."""
    con = duckdb.connect(DATABASE_PATH)

    total_count = con.execute("SELECT COUNT(*) FROM vins_classes").fetchone()[0]

    premium_count = con.execute("SELECT COUNT(*) FROM vins_premium").fetchone()[0]

    ordinary_count = con.execute("SELECT COUNT(*) FROM vins_ordinaires").fetchone()[0]

    null_zscore = con.execute(
        """
        SELECT COUNT(*)
        FROM vins_classes
        WHERE z_score IS NULL
        """
    ).fetchone()[0]

    invalid_premium = con.execute(
        """
        SELECT COUNT(*)
        FROM vins_premium
        WHERE z_score <= 2
        """
    ).fetchone()[0]

    invalid_ordinary = con.execute(
        """
        SELECT COUNT(*)
        FROM vins_ordinaires
        WHERE z_score > 2
        """
    ).fetchone()[0]

    con.close()

    print(f"Nombre total de vins : {total_count}")
    print(f"Vins premium : {premium_count}")
    print(f"Vins ordinaires : {ordinary_count}")
    print(f"z-score manquants : {null_zscore}")
    print(f"Premium invalides : {invalid_premium}")
    print(f"Ordinaires invalides : {invalid_ordinary}")


if __name__ == "__main__":
    main()
