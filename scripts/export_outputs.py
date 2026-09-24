#!/usr/bin/env python3

"""Génère les fichiers de sortie métier du projet."""

from pathlib import Path

import duckdb
import pandas as pd

DATABASE_PATH = "work/comptoir.duckdb"
OUTPUT_DIR = Path("outputs")


def main():
    """Exporte le rapport CA et les listes premium / ordinaires."""
    OUTPUT_DIR.mkdir(exist_ok=True)

    con = duckdb.connect(DATABASE_PATH)

    # Données du chiffre d'affaires par produit.
    ca_produit = con.execute(
        """
        SELECT
            product_id,
            sku,
            post_title,
            price,
            total_sales,
            chiffre_affaires
        FROM ca_par_produit
        ORDER BY product_id
        """
    ).df()

    # Chiffre d'affaires total.
    ca_total = con.execute(
        """
        SELECT chiffre_affaires_total
        FROM ca_total
        """
    ).df()

    # Vins premium.
    premium = con.execute(
        """
        SELECT *
        FROM vins_premium
        ORDER BY z_score DESC
        """
    ).df()

    # Vins ordinaires.
    ordinaires = con.execute(
        """
        SELECT *
        FROM vins_ordinaires
        ORDER BY z_score DESC
        """
    ).df()

    con.close()

    # Rapport Excel avec deux feuilles.
    report_path = OUTPUT_DIR / "rapport_CA.xlsx"

    with pd.ExcelWriter(report_path, engine="openpyxl") as writer:
        ca_produit.to_excel(
            writer,
            sheet_name="CA_par_produit",
            index=False,
        )

        ca_total.to_excel(
            writer,
            sheet_name="CA_total",
            index=False,
        )

    # Exports CSV.
    premium.to_csv(
        OUTPUT_DIR / "premium.csv",
        index=False,
        encoding="utf-8",
    )

    ordinaires.to_csv(
        OUTPUT_DIR / "ordinaires.csv",
        index=False,
        encoding="utf-8",
    )

    print(f"Rapport Excel créé : {report_path}")
    print(f"Vins premium exportés : {len(premium)}")
    print(f"Vins ordinaires exportés : {len(ordinaires)}")


if __name__ == "__main__":
    main()
