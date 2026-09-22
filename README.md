# Comptoir des Coteaux - Pipeline Data Engineering

## Contexte

Le Comptoir des Coteaux souhaite automatiser un traitement mensuel actuellement réalisé manuellement à partir de données provenant d'un ERP et d'une boutique Web.

L'objectif du projet est de construire progressivement un pipeline Data Engineering permettant de nettoyer, rapprocher et traiter ces données.

Le projet sera orchestré avec Kestra et les traitements utiliseront notamment SQL avec DuckDB ainsi que Python avec pandas.

À ce stade, la phase de cadrage et l'analyse exploratoire des fichiers sources ont été réalisées.

## Sources de données

Les données sont fournies dans trois fichiers Excel :

- `Fichier_erp.xlsx`
- `Fichier_web.xlsx`
- `fichier_liaison.xlsx`

La table de liaison permet de faire correspondre :

```text
ERP.product_id
       ↓
liaison.product_id
       ↓
liaison.id_web
       ↓
WEB.sku
```

## Environnement

Le projet utilise Docker et Docker Compose afin de ne pas installer directement les dépendances Python sur le poste local.

Technologies actuellement utilisées :

- Docker
- Docker Compose
- Python 3.12
- pandas
- OpenPyXL

## Installation de l'environnement

Construire l'image Docker :

```bash
docker compose build
```

Vérifier l'environnement Python :

```bash
docker compose run --rm python python -c "import pandas as pd; import openpyxl; print('pandas:', pd.__version__); print('openpyxl:', openpyxl.__version__)"
```

Versions actuellement utilisées :

```text
pandas : 3.0.6
openpyxl : 3.1.5
```

## Analyse exploratoire des données

L'analyse des trois fichiers sources est réalisée avec le script :

```text
scripts/analyse_sources.py
```

Pour l'exécuter :

```bash
docker compose run --rm python python scripts/analyse_sources.py
```

### Résultats obtenus

**ERP**

- 825 lignes
- 5 colonnes
- 825 `product_id` uniques
- aucun `product_id` manquant
- aucun doublon sur `product_id`

**Table de liaison**

- 825 lignes
- 825 `product_id` uniques
- 734 `id_web` renseignés
- 91 `id_web` manquants

**Web**

- 1513 lignes initiales
- 85 `sku` manquants
- 1428 lignes après suppression des `sku` manquants
- 714 `sku` uniques
- chaque `sku` apparaît deux fois : une ligne `product` et une ligne `attachment`

## Points à clarifier

Deux points ont été identifiés pendant l'analyse :

- le traitement des 91 `id_web` manquants dans la table de liaison ;
- la règle de conservation lors du dédoublonnage du fichier Web entre les lignes `product` et `attachment`.

## Structure actuelle du projet

```text
comptoir-des-coteaux/
├── data/
│   ├── Fichier_erp.xlsx
│   ├── Fichier_web.xlsx
│   └── fichier_liaison.xlsx
├── docs/
│   └── note_cadrage.md
├── scripts/
│   └── analyse_sources.py
├── .gitignore
├── Dockerfile
├── docker-compose.yml
├── README.md
└── requirements.txt
```

## Documentation

La note de cadrage est disponible dans :

```text
docs/note_cadrage.md
```

## Suivi du projet

Le suivi des tâches et du backlog est réalisé dans OpenProject.

Lien OpenProject : **https://comptoir-coteaux-marie.openproject.com/projects/comptoir-coteaux-pipeline**

