# Definitions KPI

## kpi1_throughput

Debit des robots.

Source : `raw_robot_activity`.

Formule generale :

```text
items_success / nombre de robot-heures operationnelles
```

Versions :
- `v1` : calcul simple.
- `v2` : exclut certaines heures de maintenance programmee selon un seuil.

Parametres :

- `include_test_runs`
- `maintenance_threshold_h`

## kpi2_availability

Disponibilite des robots.

Source : `raw_robot_activity`.

Versions :
- `v1` : `active / (active + panne + maintenance_programmee)`
- `v2` : `active / (active + panne)`

Ici, la difference est structurelle : le denominateur change.

## kpi3_order_accuracy

Exactitude des commandes.

Source : `raw_order_fulfillment`.

Formule :

```text
lignes_correctes / lignes_totales
```

Parametre :

- `min_lines`

Dans le jeu de demo, BOLT herite d'un statut `not_applicable` pour ce KPI.
