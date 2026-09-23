-- ============================================================
-- Dédoublonnage des trois sources
-- Comptoir des Coteaux
-- ============================================================


-- ERP
-- Une seule ligne est conservée par product_id.
CREATE OR REPLACE TABLE erp_dedup AS
SELECT * EXCLUDE (row_num)
FROM (
    SELECT
        *,
        ROW_NUMBER() OVER (
            PARTITION BY product_id
            ORDER BY product_id
        ) AS row_num
    FROM erp_clean
)
WHERE row_num = 1;


-- LIAISON
-- Une seule ligne est conservée par product_id.
-- Les id_web NULL sont toujours conservés.
CREATE OR REPLACE TABLE liaison_dedup AS
SELECT * EXCLUDE (row_num)
FROM (
    SELECT
        *,
        ROW_NUMBER() OVER (
            PARTITION BY product_id
            ORDER BY product_id
        ) AS row_num
    FROM liaison_clean
)
WHERE row_num = 1;


-- WEB
-- On conserve uniquement les lignes métier de type "product".
-- Puis on garantit une seule ligne par sku.
CREATE OR REPLACE TABLE web_dedup AS
SELECT * EXCLUDE (row_num)
FROM (
    SELECT
        *,
        ROW_NUMBER() OVER (
            PARTITION BY sku
            ORDER BY sku
        ) AS row_num
    FROM web_clean
    WHERE LOWER(TRIM(post_type)) = 'product'
)
WHERE row_num = 1;