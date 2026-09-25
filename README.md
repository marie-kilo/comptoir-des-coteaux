# Comptoir des Coteaux — Pipeline Data Engineering

## Contexte

Le Comptoir des Coteaux souhaite automatiser un traitement mensuel réalisé à partir de données provenant d'un ERP et d'une boutique Web.

L'objectif du projet est de mettre en place un pipeline Data Engineering permettant de :

- nettoyer les données sources ;
- supprimer les doublons ;
- rapprocher les données ERP et Web ;
- calculer le chiffre d'affaires par produit et le chiffre d'affaires global ;
- identifier les vins premium à l'aide d'un z-score ;
- générer les livrables métiers ;
- contrôler automatiquement la qualité des résultats ;
- orchestrer et planifier l'ensemble du pipeline avec Kestra.

Le workflow principal est exécuté automatiquement le **15 de chaque mois à 9h**, heure de Paris.

---

## Sources de données

Les données sont fournies dans trois fichiers Excel situés dans `data/` :

```text
data/
├── Fichier_erp.xlsx
├── Fichier_web.xlsx
└── fichier_liaison.xlsx
```

La table de liaison permet de rapprocher les identifiants ERP et Web :

```text
ERP.product_id
       |
       v
liaison.product_id
       |
       v
liaison.id_web
       |
       v
WEB.sku
```

### Analyse initiale

#### ERP

- 825 lignes
- 5 colonnes
- 825 `product_id` uniques
- aucun `product_id` manquant
- aucun doublon sur `product_id`

#### Liaison

- 825 lignes
- 825 `product_id` uniques
- 734 `id_web` renseignés
- 91 `id_web` manquants

Les lignes dont `id_web` est manquant sont conservées dans la table de liaison. Elles ne participent simplement pas à la jointure finale avec les données Web.

#### Web

- 1513 lignes initiales
- 85 `sku` manquants
- 1428 lignes après nettoyage
- 714 `sku` uniques
- chaque `sku` apparaît initialement deux fois :
  - une ligne `product`
  - une ligne `attachment`

Pour le dédoublonnage, les lignes `post_type = 'product'` sont conservées.

---

## Architecture technique

Le projet utilise :

- Docker
- Docker Compose
- Kestra
- Python 3.12
- pandas
- DuckDB
- SQL
- OpenPyXL
- Git
- GitHub
- OpenProject
- Draw.io

Les traitements sont exécutés dans des conteneurs Docker afin d'éviter l'installation directe des dépendances Python sur le poste local.

Kestra est utilisé comme **orchestrateur**.

La logique métier reste dans les scripts SQL et Python.

---

## Prérequis

Avant de lancer le projet, les éléments suivants doivent être disponibles :

- Git
- Docker Desktop ou Docker Engine
- Docker Compose
- un navigateur Web
- le port `8080` disponible pour Kestra

Aucune installation locale de Python, pandas ou DuckDB n'est nécessaire.

Les dépendances Python sont intégrées dans l'image Docker :

```text
comptoir-python:latest
```

---

# Pipeline principal

Le workflow Kestra principal est :

```text
flows/pipeline_comptoir.yml
```

Il orchestre la totalité du pipeline mensuel.

## Fonctionnement du pipeline

```text
Clone du dépôt GitHub
        |
        v
Vérification des fichiers
        |
        v
Nettoyage des sources
        |
        v
Test nettoyage
        |
        v
Dédoublonnage
        |
        v
Test dédoublonnage
        |
        v
Fusion ERP / Liaison / Web
        |
        v
Test jointure
        |
        v
Calcul du chiffre d'affaires
        |
        v
Test chiffre d'affaires
        |
        v
Calcul du z-score
        |
        v
Test z-score
        |
        v
Génération du rapport CA
        |
        v
     Parallel Kestra
       /          \
      /            \
Premium            Ordinaire
   |                   |
   v                   v
premium.csv      ordinaires.csv
   |                   |
   v                   v
Test export        Test export
```

---

# Traitements SQL

Les traitements DuckDB sont disponibles dans :

```text
scripts/sql/
```

## 1. Nettoyage

Script :

```text
scripts/sql/01_clean_sources.sql
```

Ce traitement :

- charge les fichiers Excel avec DuckDB ;
- supprime les lignes dont les clés principales sont manquantes ;
- prépare les données pour la suite du pipeline.

Tables créées :

```text
erp_clean
liaison_clean
web_clean
```

---

## 2. Dédoublonnage

Script :

```text
scripts/sql/02_deduplicate_sources.sql
```

Ce traitement :

- dédoublonne ERP sur `product_id` ;
- dédoublonne Liaison sur `product_id` ;
- conserve les lignes Web de type `product` ;
- dédoublonne les données Web sur `sku`.

Tables créées :

```text
erp_dedup
liaison_dedup
web_dedup
```

---

## 3. Jointure

Script :

```text
scripts/sql/03_join_sources.sql
```

La jointure est réalisée selon :

```text
ERP.product_id = Liaison.product_id
Liaison.id_web = Web.sku
```

La table finale de rapprochement est :

```text
ventes_fusionnees
```

Résultat attendu :

```text
714 lignes
```

---

## 4. Chiffre d'affaires

Script :

```text
scripts/sql/04_calculate_revenue.sql
```

Le chiffre d'affaires est calculé avec :

```text
chiffre_affaires = price * total_sales
```

Les résultats sont stockés dans :

```text
ca_par_produit
ca_total
```

Résultat de référence :

```text
70 568,60 €
```

---

# Classification des vins avec le z-score

Le script :

```text
scripts/classify_wines.py
```

calcule le z-score du prix de chaque vin.

Formule :

```text
z = (prix - moyenne des prix) / écart-type des prix
```

L'écart-type utilisé correspond à la population complète :

```python
df["price"].std(ddof=0)
```

Règle métier :

```text
z > 2  -> Premium
z <= 2 -> Ordinaire
```

Résultats obtenus :

```text
Premium   : 30 vins
Ordinaire : 684 vins
Total     : 714 vins
```

Les données sont stockées dans deux tables DuckDB :

```text
vins_premium
vins_ordinaires
```

---

# Branches Kestra Premium et Ordinaire

Après le calcul et le contrôle du z-score, Kestra sépare les deux extractions métiers dans deux branches distinctes exécutées en parallèle.

```text
                category_exports
                     Parallel
                    /        \
                   /          \
        premium_branch     ordinary_branch
              |                  |
              v                  v
       export_premium      export_ordinaire
              |                  |
              v                  v
        test_premium        test_ordinaire
              |                  |
              v                  v
         premium.csv       ordinaires.csv
             30                684
```

Le script utilisé par les deux branches est :

```text
scripts/export_wine_category.py
```

Il reçoit :

```text
base DuckDB
catégorie
fichier CSV de sortie
```

Exemple Premium :

```bash
python export_wine_category.py comptoir.duckdb premium premium.csv
```

Exemple Ordinaire :

```bash
python export_wine_category.py comptoir.duckdb ordinaire ordinaires.csv
```

Les exports sont ensuite contrôlés avec :

```text
scripts/check_wine_category_export.py
```

Valeurs attendues :

```text
premium.csv    -> 30 lignes
ordinaires.csv -> 684 lignes
```

Cette architecture permet à Kestra d'orchestrer indépendamment les deux extractions métiers.

---

# Tests automatiques

Les tests du pipeline sont bloquants.

Si une valeur attendue n'est pas respectée, le script retourne une erreur et Kestra arrête le pipeline avec un statut `Failed`.

## 1. Nettoyage et valeurs manquantes

Script :

```text
scripts/check_cleaning.py
```

Contrôles principaux :

- volumes après nettoyage ;
- absence de `product_id` manquant dans ERP ;
- absence de `product_id` manquant dans Liaison ;
- absence de `sku` manquant dans Web.

---

## 2. Absence de doublons

Script :

```text
scripts/check_deduplication.py
```

Contrôles :

- doublons ERP sur `product_id` ;
- doublons Liaison sur `product_id` ;
- doublons Web sur `sku`.

---

## 3. Cohérence de la jointure

Script :

```text
scripts/check_join.py
```

Contrôles :

- nombre de lignes fusionnées ;
- unicité des clés ;
- absence de clés manquantes ;
- cohérence entre `id_web` et `sku`.

---

## 4. Cohérence du chiffre d'affaires

Script :

```text
scripts/check_revenue.py
```

Contrôles :

- nombre de produits ;
- chiffre d'affaires global ;
- absence de CA manquant ;
- cohérence de la formule :

```text
price * total_sales
```

---

## 5. Cohérence du z-score

Script :

```text
scripts/check_zscore.py
```

Contrôles :

- nombre total de vins ;
- nombre de vins premium ;
- nombre de vins ordinaires ;
- absence de z-score manquant ;
- `premium -> z > 2` ;
- `ordinaire -> z <= 2` ;
- cohérence entre le z-score Python et un recalcul DuckDB.

---

## 6. Contrôle des exports Premium / Ordinaire

Script :

```text
scripts/check_wine_category_export.py
```

Contrôles :

```text
Premium   -> 30 lignes
Ordinaire -> 684 lignes
```

---

# Valeurs de référence

| Contrôle | Valeur attendue |
|---|---:|
| ERP après dédoublonnage | 825 |
| Liaison après dédoublonnage | 825 |
| Web après nettoyage | 1428 |
| Web après dédoublonnage | 714 |
| Lignes après jointure | 714 |
| Chiffre d'affaires total | 70 568,60 € |
| Vins premium | 30 |
| Vins ordinaires | 684 |

---

# Gestion des erreurs

Une stratégie de retry est configurée dans Kestra sur les tâches de traitement susceptibles d'échouer temporairement.

Configuration :

```yaml
retry:
  type: constant
  interval: PT5S
  maxAttempts: 3
  maxDuration: PT30S
  warningOnRetry: true
```

Principe :

```text
Tentative
    |
    v
Erreur
    |
    v
Attente 5 secondes
    |
    v
Nouvelle tentative
```

Après les tentatives autorisées, Kestra marque la tâche en :

```text
Failed
```

Les tâches de test ne disposent volontairement pas de retry.

Une anomalie de qualité des données doit interrompre immédiatement le pipeline plutôt que relancer le même contrôle.

Un workflow de démonstration est disponible :

```text
flows/test_retry.yml
```

Il simule volontairement une erreur avec :

```bash
exit 1
```

afin de vérifier le mécanisme de retry de Kestra.

---

# Évolutivité : intégration d'une quatrième source

Le projet contient un second workflow Kestra permettant d'anticiper l'arrivée d'une nouvelle source de données :

```text
flows/onboard_extra_source.yml
```

La nouvelle source est fournie au workflow avec un input Kestra de type :

```text
FILE
```

Le workflow est indépendant du cron mensuel du pipeline nominal.

## Fonctionnement

```text
Upload du nouveau fichier
        |
        v
Clone du dépôt GitHub
        |
        v
Nettoyage des sources de référence
        |
        v
Dédoublonnage
        |
        v
Jointure ERP / Liaison / Web
        |
        v
Analyse de la nouvelle source
        |
        v
Chargement extra_source_raw
        |
        v
Recherche d'une clé commune
product_id / sku / id_web
        |
        v
Intégration à ventes_fusionnees
        |
        v
Test de l'intégration
        |
        v
Calcul du chiffre d'affaires
        |
        v
Test CA
        |
        v
Classification z-score
        |
        v
Test z-score
        |
        v
Rapport CA
        |
        v
Parallel Kestra
   /                 \
Premium             Ordinaire
   |                    |
   v                    v
CSV + test          CSV + test
```

---

## Analyse de la nouvelle source

Script :

```text
scripts/inspect_extra_source.py
```

Il analyse notamment :

- le nombre de lignes ;
- le nombre de colonnes ;
- les noms de colonnes ;
- les valeurs manquantes ;
- les doublons complets ;
- les clés candidates.

La source est ensuite chargée dans DuckDB dans :

```text
extra_source_raw
```

Le script accepte notamment :

```text
.xlsx
.xls
.csv
```

---

## Intégration de la nouvelle source

Script :

```text
scripts/integrate_extra_source.py
```

Le script recherche une clé commune exploitable parmi :

```text
product_id
sku
id_web
```

La clé doit notamment être compatible avec les données existantes et ne pas générer de duplication des ventes.

Les nouvelles colonnes sont ajoutées avec le préfixe :

```text
extra_
```

Exemple :

```text
stock_quantity
```

devient :

```text
extra_stock_quantity
```

Cela permet de conserver les colonnes métier existantes sans les écraser.

---

## Test de l'intégration

Script :

```text
scripts/check_extra_source_integration.py
```

Le contrôle vérifie notamment :

```text
714 lignes après intégration
0 doublon product_id
0 doublon sku
présence de colonnes extra_
```

Lors du test de démonstration avec `Fichier_erp.xlsx` utilisé comme quatrième source :

```text
Clé détectée          : product_id
Ventes initiales      : 714
Lignes source         : 825
Correspondances       : 714
Couverture jointure   : 100 %
Lignes après jointure : 714
```

Colonnes supplémentaires obtenues :

```text
extra_onsale_web
extra_price
extra_stock_quantity
extra_stock_status
```

Le workflow complet d'onboarding a été exécuté avec succès dans Kestra, jusqu'au calcul du CA, au z-score et aux branches Premium / Ordinaire.

### Limite volontaire

Le workflow générique enrichit les données existantes mais ne remplace pas automatiquement les colonnes métier telles que `price` ou `total_sales`.

La règle métier exacte d'une future quatrième source dépend de son contenu réel.

Cette approche évite de modifier le calcul du chiffre d'affaires sans règle métier validée.

---

# Fichiers de sortie

Le pipeline produit trois livrables métiers.

## Rapport Excel

Script :

```text
scripts/export_revenue_report.py
```

Fichier :

```text
outputs/rapport_CA.xlsx
```

Le classeur contient deux feuilles :

```text
CA_par_produit
CA_total
```

Valeurs de référence :

```text
714 produits
CA total : 70 568,60 €
```

---

## Vins premium

La branche :

```text
premium_branch
```

produit :

```text
outputs/premium.csv
```

Nombre de vins :

```text
30
```

---

## Vins ordinaires

La branche :

```text
ordinary_branch
```

produit :

```text
outputs/ordinaires.csv
```

Nombre de vins :

```text
684
```

---

# Planification Kestra

Le workflow principal est exécuté automatiquement le **15 de chaque mois à 9h**, heure de Paris.

Configuration :

```yaml
triggers:
  - id: monthly_schedule
    type: io.kestra.plugin.core.trigger.Schedule
    cron: "0 9 15 * *"
    timezone: Europe/Paris
```

Expression cron :

```text
0 9 15 * *
```

Le workflow concerné est :

```text
pipeline_comptoir
```

Le workflow :

```text
onboard_extra_source
```

n'est pas planifié automatiquement.

Il est déclenché manuellement lorsqu'une nouvelle source doit être analysée et intégrée.

---

# Installation

## 1. Cloner le dépôt

```bash
git clone https://github.com/marie-kilo/comptoir-des-coteaux.git
cd comptoir-des-coteaux
```

---

## 2. Construire l'image Python

Depuis la racine du projet :

```bash
docker compose build
```

L'image créée est :

```text
comptoir-python:latest
```

---

## 3. Vérifier les dépendances

```bash
docker compose run --rm python python -c "import pandas; import duckdb; import openpyxl; print('Environnement OK')"
```

---

# Démarrer Kestra

## 1. Configuration

Le modèle de configuration est disponible dans :

```text
kestra/.env.example
```

Créer un fichier `.env` à partir de ce modèle.

### Windows PowerShell

```powershell
cd kestra
Copy-Item .env.example .env
```

### Linux / macOS

```bash
cd kestra
cp .env.example .env
```

Le fichier `.env.example` contient uniquement des valeurs d'exemple :

```env
POSTGRES_PASSWORD=change_me
KESTRA_USERNAME=admin
KESTRA_PASSWORD=change_me
```

Modifier les valeurs dans `.env` si nécessaire.

Le fichier `.env` peut contenir des informations sensibles et n'est pas versionné dans Git.

Seul :

```text
.env.example
```

est conservé dans le dépôt.

---

## 2. Lancer Kestra

Depuis le dossier :

```text
kestra/
```

lancer :

```bash
docker compose up -d
```

Vérifier les conteneurs :

```bash
docker compose ps
```

L'interface Kestra est accessible sur :

```text
http://localhost:8080
```

---

# Workflows Kestra

Les workflows sont disponibles dans :

```text
flows/
```

## Pipeline nominal

```text
flows/pipeline_comptoir.yml
```

Flow Kestra :

```text
pipeline_comptoir
```

Fonction :

- traitements mensuels ;
- contrôles qualité ;
- calcul du CA ;
- classification ;
- rapport Excel ;
- branches Premium / Ordinaire ;
- exports CSV ;
- cron mensuel.

---

## Onboarding quatrième source

```text
flows/onboard_extra_source.yml
```

Flow Kestra :

```text
onboard_extra_source
```

Fonction :

- upload d'une nouvelle source ;
- analyse automatique ;
- détection d'une clé ;
- jointure contrôlée ;
- tests ;
- recalcul du pipeline ;
- CA ;
- z-score ;
- Premium / Ordinaire ;
- exports.

---

## Test des retries

```text
flows/test_retry.yml
```

Ce flow simule une tâche en erreur afin de tester la stratégie de retry.

---

# Exécution manuelle des traitements

Les traitements peuvent également être testés manuellement avec Docker.

## Nettoyage

```bash
docker compose run --rm python python scripts/run_sql.py scripts/sql/01_clean_sources.sql
```

## Test nettoyage

```bash
docker compose run --rm python python scripts/check_cleaning.py
```

## Dédoublonnage

```bash
docker compose run --rm python python scripts/run_sql.py scripts/sql/02_deduplicate_sources.sql
```

## Test dédoublonnage

```bash
docker compose run --rm python python scripts/check_deduplication.py
```

## Jointure

```bash
docker compose run --rm python python scripts/run_sql.py scripts/sql/03_join_sources.sql
```

## Test jointure

```bash
docker compose run --rm python python scripts/check_join.py
```

## Calcul du chiffre d'affaires

```bash
docker compose run --rm python python scripts/run_sql.py scripts/sql/04_calculate_revenue.sql
```

## Test du chiffre d'affaires

```bash
docker compose run --rm python python scripts/check_revenue.py
```

## Classification z-score

```bash
docker compose run --rm python python scripts/classify_wines.py
```

## Test z-score

```bash
docker compose run --rm python python scripts/check_zscore.py
```

## Rapport Excel

```bash
docker compose run --rm python python scripts/export_revenue_report.py
```

## Export Premium

```bash
docker compose run --rm python python scripts/export_wine_category.py work/comptoir.duckdb premium outputs/premium.csv
```

## Test Premium

```bash
docker compose run --rm python python scripts/check_wine_category_export.py outputs/premium.csv 30
```

## Export Ordinaire

```bash
docker compose run --rm python python scripts/export_wine_category.py work/comptoir.duckdb ordinaire outputs/ordinaires.csv
```

## Test Ordinaire

```bash
docker compose run --rm python python scripts/check_wine_category_export.py outputs/ordinaires.csv 684
```

---

# Test manuel d'une quatrième source

Exemple avec `Fichier_erp.xlsx` utilisé comme source supplémentaire de démonstration :

## Analyse

```bash
docker compose run --rm python python scripts/inspect_extra_source.py data/Fichier_erp.xlsx
```

## Intégration

```bash
docker compose run --rm python python scripts/integrate_extra_source.py
```

## Contrôle

```bash
docker compose run --rm python python scripts/check_extra_source_integration.py
```

Résultat validé :

```text
714 lignes
0 doublon product_id
0 doublon sku
4 colonnes supplémentaires
```

---

# Structure du projet

```text
comptoir-des-coteaux/
|
|-- data/
|   |-- Fichier_erp.xlsx
|   |-- Fichier_web.xlsx
|   `-- fichier_liaison.xlsx
|
|-- docs/
|   |-- note_cadrage.md
|   |-- pipeline_comptoir.drawio
|   |-- pipeline_comptoir.png
|   `-- screenshots/
|
|-- flows/
|   |-- pipeline_comptoir.yml
|   |-- onboard_extra_source.yml
|   `-- test_retry.yml
|
|-- kestra/
|   |-- docker-compose.yml
|   `-- .env.example
|
|-- outputs/
|   |-- rapport_CA.xlsx
|   |-- premium.csv
|   `-- ordinaires.csv
|
|-- scripts/
|   |
|   |-- sql/
|   |   |-- 01_clean_sources.sql
|   |   |-- 02_deduplicate_sources.sql
|   |   |-- 03_join_sources.sql
|   |   `-- 04_calculate_revenue.sql
|   |
|   |-- analyse_sources.py
|   |-- run_sql.py
|   |
|   |-- classify_wines.py
|   |
|   |-- export_revenue_report.py
|   |-- export_wine_category.py
|   |
|   |-- inspect_extra_source.py
|   |-- integrate_extra_source.py
|   |
|   |-- check_cleaning.py
|   |-- check_deduplication.py
|   |-- check_join.py
|   |-- check_revenue.py
|   |-- check_zscore.py
|   |-- check_wine_category_export.py
|   `-- check_extra_source_integration.py
|
|-- Dockerfile
|-- docker-compose.yml
|-- requirements.txt
|-- .gitignore
`-- README.md
```

---

# Documentation

La note de cadrage est disponible dans :

```text
docs/note_cadrage.md
```

Le logigramme du pipeline est disponible dans :

```text
docs/pipeline_comptoir.drawio
docs/pipeline_comptoir.png
```

Les captures d'écran de validation sont disponibles dans :

```text
docs/screenshots/
```

Elles documentent notamment :

- l'installation de Kestra ;
- une première exécution réussie ;
- le clonage du dépôt GitHub ;
- le nettoyage des données ;
- le dédoublonnage ;
- la jointure ;
- le calcul du chiffre d'affaires ;
- le calcul du z-score ;
- les exports ;
- les tests automatiques ;
- le trigger cron ;
- les retries ;
- la gestion des erreurs ;
- les branches Premium / Ordinaire ;
- l'analyse d'une nouvelle source ;
- l'exécution complète du workflow d'intégration d'une quatrième source.

---

# Principes d'architecture

Le projet suit plusieurs principes.

## Séparation orchestration / traitement

Kestra orchestre :

- l'ordre des tâches ;
- les dépendances ;
- les branches ;
- les retries ;
- le cron ;
- les exécutions.

Les scripts SQL et Python réalisent les traitements métier.

---

## Tests bloquants

Chaque étape critique est suivie d'un contrôle.

Une anomalie de données arrête le pipeline.

---

## Reproductibilité

Docker garantit un environnement reproductible.

Les dépendances sont encapsulées dans une image versionnée par le projet.

---

## Évolutivité

Les traitements sont séparés en scripts indépendants.

Un flow spécifique permet d'intégrer une nouvelle source sans réécrire entièrement le pipeline nominal.

---

# Pourquoi Kestra ?

Kestra est adapté au projet car il permet :

- de décrire les workflows de manière déclarative ;
- de visualiser les tâches et leur état ;
- d'orchestrer des traitements SQL et Python ;
- de gérer les dépendances entre tâches ;
- de gérer les erreurs et retries ;
- de créer des branches parallèles ;
- de planifier les exécutions avec un cron ;
- de conserver un historique des exécutions.

La logique métier reste indépendante de l'orchestrateur.

---

# Pourquoi DuckDB ?

DuckDB est adapté au projet car :

- les volumes sont compatibles avec un moteur analytique local ;
- aucune infrastructure de base de données permanente n'est nécessaire ;
- il permet d'utiliser directement SQL ;
- il s'intègre facilement à Python ;
- il permet de travailler avec des fichiers Excel après chargement via son extension ;
- il est facilement utilisable dans Docker ;
- il convient bien à un pipeline analytique local et reproductible.

---

# Suivi du projet

Le backlog et le suivi Kanban sont réalisés avec OpenProject.

Projet :

https://comptoir-coteaux-marie.openproject.com/projects/comptoir-coteaux-pipeline

---

# Dépôt GitHub

Le dépôt du projet est disponible ici :

https://github.com/marie-kilo/comptoir-des-coteaux

Le dépôt contient :

- le code source ;
- les workflows Kestra ;
- les scripts SQL et Python ;
- le logigramme ;
- la documentation ;
- les captures d'écran ;
- les résultats générés ;
- le README ;
- le support de soutenance une fois finalisé.