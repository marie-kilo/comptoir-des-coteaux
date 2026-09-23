-- ============================================================
-- Nettoyage initial des trois sources
-- Comptoir des Coteaux
-- ============================================================

-- ERP
-- La clé product_id doit être renseignée.
CREATE OR REPLACE TABLE erp_clean AS
SELECT *
FROM read_xlsx(
    'data/Fichier_erp.xlsx',
    all_varchar = true
)
WHERE NULLIF(TRIM(product_id), '') IS NOT NULL;


-- LIAISON
-- product_id est obligatoire.
-- Les id_web NULL sont volontairement conservés.
CREATE OR REPLACE TABLE liaison_clean AS
SELECT *
FROM read_xlsx(
    'data/fichier_liaison.xlsx',
    all_varchar = true
)
WHERE NULLIF(TRIM(product_id), '') IS NOT NULL;


-- WEB
-- Les lignes sans sku ne peuvent pas être rapprochées
-- avec les données ERP : elles sont supprimées.
CREATE OR REPLACE TABLE web_clean AS
SELECT *
FROM read_xlsx(
    'data/Fichier_web.xlsx',
    all_varchar = true
)
WHERE NULLIF(TRIM(sku), '') IS NOT NULL;