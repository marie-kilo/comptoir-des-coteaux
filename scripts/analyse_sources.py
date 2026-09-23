#!/usr/bin/env python3

"""Analyse exploratoire des trois sources du Comptoir des Coteaux."""

from pathlib import Path

import pandas as pd

DATA_DIR = Path("data")


def analyse_erp():
    """Analyse le fichier ERP."""
    erp = pd.read_excel(DATA_DIR / "Fichier_erp.xlsx")

    print("\n========== ERP ==========")
    print(f"Nombre de lignes : {len(erp)}")
    print(f"Nombre de colonnes : {len(erp.columns)}")
    print(f"Colonnes : {erp.columns.tolist()}")

    print("\nTypes :")
    print(erp.dtypes)

    print("\nValeurs manquantes :")
    print(erp.isna().sum())

    print(f"\nproduct_id uniques : {erp['product_id'].nunique()}")
    print(f"product_id manquants : {erp['product_id'].isna().sum()}")
    print(f"Doublons product_id : {erp['product_id'].duplicated().sum()}")


def analyse_liaison():
    """Analyse le fichier de liaison."""
    liaison = pd.read_excel(DATA_DIR / "fichier_liaison.xlsx")

    print("\n========== LIAISON ==========")
    print(f"Nombre de lignes : {len(liaison)}")
    print(f"Nombre de colonnes : {len(liaison.columns)}")
    print(f"Colonnes : {liaison.columns.tolist()}")

    print("\nTypes :")
    print(liaison.dtypes)

    print("\nValeurs manquantes :")
    print(liaison.isna().sum())

    print(f"\nproduct_id uniques : {liaison['product_id'].nunique()}")
    print(f"id_web renseignés : {liaison['id_web'].notna().sum()}")
    print(f"id_web manquants : {liaison['id_web'].isna().sum()}")


def analyse_web():
    """Analyse le fichier Web."""
    web = pd.read_excel(DATA_DIR / "Fichier_web.xlsx")

    print("\n========== WEB ==========")
    print(f"Nombre de lignes : {len(web)}")
    print(f"Nombre de colonnes : {len(web.columns)}")
    print(f"Colonnes : {web.columns.tolist()}")

    print("\nValeurs manquantes :")
    print(web.isna().sum())

    print(f"\nsku manquants : {web['sku'].isna().sum()}")

    web_clean = web.dropna(subset=["sku"])

    print(f"Lignes après suppression des sku manquants : {len(web_clean)}")
    print(f"sku uniques : {web_clean['sku'].nunique()}")

    counts = web_clean["sku"].value_counts()

    print(f"Tous les sku apparaissent exactement 2 fois : {(counts == 2).all()}")

    print("\nRépartition post_type :")
    print(web_clean["post_type"].value_counts())


if __name__ == "__main__":
    analyse_erp()
    analyse_liaison()
    analyse_web()
