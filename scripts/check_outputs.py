#!/usr/bin/env python3

"""Vérifie les fichiers de sortie générés."""

from pathlib import Path

import pandas as pd

OUTPUT_DIR = Path("outputs")


def main():
    """Contrôle l'existence et le contenu des exports."""
    report_path = OUTPUT_DIR / "rapport_CA.xlsx"
    premium_path = OUTPUT_DIR / "premium.csv"
    ordinary_path = OUTPUT_DIR / "ordinaires.csv"

    # Vérifier que les fichiers existent.
    print(f"rapport_CA.xlsx existe : {report_path.exists()}")
    print(f"premium.csv existe : {premium_path.exists()}")
    print(f"ordinaires.csv existe : {ordinary_path.exists()}")

    # Lire les deux feuilles Excel.
    ca_produit = pd.read_excel(
        report_path,
        sheet_name="CA_par_produit",
    )

    ca_total = pd.read_excel(
        report_path,
        sheet_name="CA_total",
    )

    # Lire les deux fichiers CSV.
    premium = pd.read_csv(premium_path)
    ordinaires = pd.read_csv(ordinary_path)

    print()
    print(f"Lignes CA par produit : {len(ca_produit)}")
    print(f"CA total dans Excel : {ca_total['chiffre_affaires_total'].iloc[0]:.2f}")

    print(f"Lignes premium.csv : {len(premium)}")
    print(f"Lignes ordinaires.csv : {len(ordinaires)}")


if __name__ == "__main__":
    main()
