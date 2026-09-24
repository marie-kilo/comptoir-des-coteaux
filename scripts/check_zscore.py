#!/usr/bin/env python3
"""Contrôle le calcul du z-score et la classification des vins."""

import duckdb

DATABASE_PATH = "work/comptoir.duckdb"
TOLERANCE = 1e-9


def check_equal(actual, expected, message):
    """Lève une erreur si la valeur obtenue est différente de la valeur attendue."""
    if actual != expected:
        raise AssertionError(f"{message} - attendu : {expected}, obtenu : {actual}")


def main():
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

    inconsistent_zscore = con.execute(
        f"""
        WITH stats AS (
            SELECT
                AVG(price) AS mean_price,
                STDDEV_POP(price) AS std_price
            FROM vins_classes
        )
        SELECT COUNT(*)
        FROM vins_classes, stats
        WHERE ABS(
            z_score - ((price - mean_price) / std_price)
        ) > {TOLERANCE}
        """
    ).fetchone()[0]

    con.close()

    print(f"Total vins : {total_count}")
    print(f"Vins premium : {premium_count}")
    print(f"Vins ordinaires : {ordinary_count}")
    print(f"Z-score manquants : {null_zscore}")
    print(f"Premium invalides : {invalid_premium}")
    print(f"Ordinaires invalides : {invalid_ordinary}")
    print(f"Z-scores incohérents : {inconsistent_zscore}")

    check_equal(
        total_count,
        714,
        "Nombre total de vins incorrect",
    )

    check_equal(
        premium_count,
        30,
        "Nombre de vins premium incorrect",
    )

    check_equal(
        ordinary_count,
        684,
        "Nombre de vins ordinaires incorrect",
    )

    check_equal(
        null_zscore,
        0,
        "Z-scores manquants",
    )

    check_equal(
        invalid_premium,
        0,
        "Vins premium avec z-score <= 2",
    )

    check_equal(
        invalid_ordinary,
        0,
        "Vins ordinaires avec z-score > 2",
    )

    check_equal(
        inconsistent_zscore,
        0,
        "Z-scores incohérents avec la formule attendue",
    )

    print("Test z-score et classification : OK")


if __name__ == "__main__":
    main()
