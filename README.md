# KPI evo demo

Prototype pour tester une methode de gestion de KPI multi-clients :

- la logique de calcul est versionnee dans le code ;
- l'affectation client/segment/global est pilotee par configuration ;
- les seuils et options sont aussi pilotes par configuration ;
- le tout est historise par dates d'effet.

## Lancer

```bash
python3 -m venv .venv
source .venv/bin/activate

python -m pip install --upgrade pip
python -m pip install pandas pyarrow

python scripts/engine.py
```

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

data/raw/                     # donnees brutes generees
results/                      # resultats calcules
docs/                         # notes courtes sur la methode
```

## Modifier la configuration

`config/kpi_assignment.csv`
A modifier quand on change quelle version d'un KPI s'applique a un client, un segment ou tout le monde.
Impact : le moteur peut basculer vers une autre logique de calcul a partir d'une date donnee.
Exemple : ACME passe de `kpi1_throughput/v1` a `kpi1_throughput/v2` au `2024-06-24`.

`config/kpi_parameters.csv`
A modifier quand la version reste la meme, mais qu'un seuil ou une option change.
Impact : le moteur garde la meme logique de calcul, mais avec un reglage different.
Exemple : ACME et CIRRUS utilisent tous les deux `kpi1_throughput/v2`, mais pas le meme `maintenance_threshold_h`.

## A tester

- Changer une affectation dans `config/kpi_assignment.csv`.
- Changer un seuil dans `config/kpi_parameters.csv`.
- Relancer `source .venv/bin/activate && python scripts/engine.py`.
- Comparer `results/kpi_results.csv`.

Exemples testes dans cette demo :

- ACME passe de `kpi1_throughput/v1` a `kpi1_throughput/v2` le `2024-06-24`.
- CIRRUS herite de `kpi2_availability/v2` via le segment `enterprise`.
- ACME et CIRRUS utilisent la meme version de `kpi1_throughput`, mais avec des seuils differents.
- BOLT a certains KPI en `not_applicable`.
