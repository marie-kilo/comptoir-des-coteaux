-- ============================================================
-- Fusion ERP + Liaison + Web
-- Comptoir des Coteaux
-- ============================================================

CREATE OR REPLACE TABLE ventes_fusionnees AS
SELECT
    erp.product_id,
    liaison.id_web,
    web.sku,
    erp.onsale_web,
    erp.price,
    erp.stock_quantity,
    erp.stock_status,
    web.post_title,
    web.total_sales,
    web.post_type
FROM erp_dedup AS erp

INNER JOIN liaison_dedup AS liaison
    ON erp.product_id = liaison.product_id

INNER JOIN web_dedup AS web
    ON TRIM(liaison.id_web) = TRIM(web.sku);