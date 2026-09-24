-- ============================================================
-- Calcul du chiffre d'affaires
-- Comptoir des Coteaux
-- ============================================================


-- Chiffre d'affaires par produit
CREATE OR REPLACE TABLE ca_par_produit AS
SELECT
    product_id,
    id_web,
    sku,
    post_title,

    CAST(price AS DECIMAL(10, 2)) AS price,
    CAST(total_sales AS INTEGER) AS total_sales,

    CAST(price AS DECIMAL(10, 2))
        * CAST(total_sales AS INTEGER) AS chiffre_affaires

FROM ventes_fusionnees;


-- Chiffre d'affaires total
CREATE OR REPLACE TABLE ca_total AS
SELECT
    SUM(chiffre_affaires) AS chiffre_affaires_total
FROM ca_par_produit;