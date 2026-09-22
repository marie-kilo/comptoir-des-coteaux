# Note de cadrage

Le Comptoir des Coteaux souhaite automatiser le traitement mensuel actuellement réalisé manuellement par Octave à partir des données de l’ERP et de la boutique Web.

L’objectif est de construire un pipeline capable de nettoyer, rapprocher et traiter automatiquement les données afin de produire le rapport de chiffre d’affaires ainsi que les listes de vins premium et ordinaires.

Les données proviennent de trois fichiers Excel : un export ERP, un export Web et une table de liaison entre `product_id` et `id_web`.

Le pipeline sera orchestré avec Kestra. Les traitements de données seront réalisés en SQL avec DuckDB et en Python avec pandas pour la partie statistique et le calcul du z-score.

L’environnement d’exécution sera conteneurisé avec Docker et Docker Compose afin de ne pas installer les dépendances directement sur le poste local.

L’analyse exploratoire montre que le fichier ERP contient 825 produits avec des `product_id` uniques et sans valeur manquante sur cette clé.

La table de liaison contient 825 lignes, mais 91 valeurs de `id_web` sont manquantes.

Le fichier Web contient 1513 lignes, dont 85 sans `sku`. Après suppression de ces lignes, il reste 1428 lignes.

Ces 1428 lignes correspondent à 714 `sku` uniques. Chaque SKU apparaît deux fois, avec une ligne de type `product` et une ligne de type `attachment`.

Une attention particulière devra donc être portée aux règles de nettoyage et de dédoublonnage avant les jointures.

Des tests seront intégrés après les différentes tâches afin de contrôler les doublons, les valeurs manquantes, les jointures, le chiffre d’affaires et le calcul du z-score.

Le workflow devra produire un rapport Excel de chiffre d’affaires, une liste CSV des vins premium et une liste CSV des vins ordinaires.

Le workflow complet devra être planifié automatiquement le 15 de chaque mois à 9 h.

Deux points restent à clarifier : le traitement des 91 `id_web` manquants et la règle exacte de conservation entre les lignes `product` et `attachment` du fichier Web.