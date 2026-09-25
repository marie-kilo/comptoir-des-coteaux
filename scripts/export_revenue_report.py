#!/usr/bin/env python3
"""Génère le rapport Excel du chiffre d'affaires."""

from pathlib import Path

import duckdb
import pandas as pd

DATABASE_PATH = "work/comptoir.duckdb"
OUTPUT_DIR = Path("outputs")


def main():
    OUTPUT_DIR.mkdir(exist_ok=True)

    con = duckdb.connect(DATABASE_PATH)

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

    ca_total = con.execute(
        """
        SELECT chiffre_affaires_total
        FROM ca_total
        """
    ).df()

    con.close()

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

    if len(ca_produit) != 714:
        raise AssertionError(f"Nombre de produits incorrect : {len(ca_produit)}")

    total = ca_total.iloc[0]["chiffre_affaires_total"]

    if float(total) != 70568.60:
        raise AssertionError(f"CA total incorrect : {total}")

    print(f"Rapport Excel créé : {report_path}")
    print(f"Produits : {len(ca_produit)}")
    print(f"CA total : {total}")
    print("Export rapport CA : OK")


if __name__ == "__main__":
    main()
