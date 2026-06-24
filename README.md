# KPI evo demo

Prototype pour tester une methode de gestion de KPI multi-clients :

- la logique de calcul est versionnee dans le code ;
- l'affectation client/segment/global est pilotee par configuration ;
- les seuils et options sont aussi pilotes par configuration ;
- le tout est historise par dates d'effet ;
- la coherence de la config est verifiee automatiquement (garde-fou d'integrite).

## Lancer

```bash
python3 -m venv .venv
source .venv/bin/activate

python -m pip install --upgrade pip
python -m pip install pandas pyarrow

python scripts/engine.py
```

`pandas` et `pyarrow` ne servent qu'au moteur de calcul (`engine.py`).

## Verifier la configuration

```bash
python scripts/validate_config.py
```

Controle la config **avant** tout calcul :

- chaque version affectee existe dans le registre ;
- chaque couple KPI/version actif a une fonction de calcul ;
- aucune periode d'affectation ne se chevauche pour un meme scope + KPI ;
- les dates sont valides et bien ordonnees ;
- chaque parametre pointe vers une version connue.

Aucune dependance (Python pur). Sort en erreur (code 1) si un probleme est trouve : branchable en CI.

## Structure

```text
config/
  clients.csv                 # client -> segment
  kpi_version_registry.csv    # versions disponibles/catalogue
  kpi_assignment.csv          # version/statut par scope et date d'effet
  kpi_parameters.csv          # seuils/options par scope, version et date d'effet

scripts/
  engine.py                   # resout config + lance les calculs
  kpi_catalog.py              # liste les KPI, versions et fonctions de calcul
  validate_config.py          # garde-fou : verifie la coherence de la config

data/raw/                     # donnees brutes generees
results/                      # resultats calcules
docs/                         # notes courtes sur la methode + changelog
```

## Modifier la configuration

`config/kpi_assignment.csv`
A modifier quand on change quelle version d'un KPI s'applique a un client, un segment ou tout le monde.
Impact : le moteur peut basculer vers une autre logique de calcul a partir d'une date donnee.
Exemple : ACME passe de `kpi1_throughput/v1` a `kpi1_throughput/v2` au `2024-06-01`.

`config/kpi_parameters.csv`
A modifier quand la version reste la meme, mais qu'un seuil ou une option change.
Impact : le moteur garde la meme logique de calcul, mais avec un reglage different.
Exemple : ACME et CIRRUS utilisent tous les deux `kpi1_throughput/v2`, mais pas le meme `maintenance_threshold_h`.

## A tester

- Valider la config avec `python scripts/validate_config.py`.
- Changer une affectation dans `config/kpi_assignment.csv`.
- Changer un seuil dans `config/kpi_parameters.csv`.
- Revalider, puis relancer `source .venv/bin/activate && python scripts/engine.py`.
- Comparer `results/kpi_results.csv`.

Exemples testes dans cette demo :

- ACME passe de `kpi1_throughput/v1` a `kpi1_throughput/v2` le `2024-06-01`.
- CIRRUS herite de `kpi2_availability/v2` via le segment `enterprise`.
- ACME et CIRRUS utilisent la meme version de `kpi1_throughput`, mais avec des seuils differents.
- BOLT a certains KPI en `not_applicable`.
