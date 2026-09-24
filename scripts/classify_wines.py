#!/usr/bin/env python3

"""Calcule le z-score des prix et classe les vins."""

import duckdb
import pandas as pd

DATABASE_PATH = "work/comptoir.duckdb"


def main():
    """Classe les vins en premium ou ordinaires selon leur z-score."""
    con = duckdb.connect(DATABASE_PATH)

    # Récupération des données déjà fusionnées et du CA calculé.
    df = con.execute(
        """
        SELECT
            product_id,
            id_web,
            sku,
            post_title,
            price,
            total_sales,
            chiffre_affaires
        FROM ca_par_produit
        """
    ).df()

    # Conversion explicite du prix en numérique pour pandas.
    df["price"] = pd.to_numeric(df["price"])

    # Calcul des statistiques du prix.
    mean_price = df["price"].mean()
    std_price = df["price"].std(ddof=0)

    # Calcul du z-score.
    df["z_score"] = (df["price"] - mean_price) / std_price

    # Par défaut, les vins sont ordinaires.
    df["categorie"] = "ordinaire"

    # Un vin est premium si son z-score est strictement supérieur à 2.
    df.loc[df["z_score"] > 2, "categorie"] = "premium"

    premium = df[df["categorie"] == "premium"].copy()
    ordinaires = df[df["categorie"] == "ordinaire"].copy()

    # Enregistrement des résultats dans DuckDB.
    con.register("df_classes", df)
    con.register("df_premium", premium)
    con.register("df_ordinaires", ordinaires)

    con.execute(
        """
        CREATE OR REPLACE TABLE vins_classes AS
        SELECT * FROM df_classes
        """
    )

    con.execute(
        """
        CREATE OR REPLACE TABLE vins_premium AS
        SELECT * FROM df_premium
        """
    )

    con.execute(
        """
        CREATE OR REPLACE TABLE vins_ordinaires AS
        SELECT * FROM df_ordinaires
        """
    )

    con.close()

    print(f"Nombre total de vins : {len(df)}")
    print(f"Prix moyen : {mean_price:.2f}")
    print(f"Écart-type : {std_price:.2f}")
    print(f"Vins premium : {len(premium)}")
    print(f"Vins ordinaires : {len(ordinaires)}")


if __name__ == "__main__":
    main()
