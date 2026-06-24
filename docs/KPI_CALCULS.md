# Calculs KPI

Resume des formules implementees dans `scripts/kpi_catalog.py`.

| KPI | Version | Calcul | Difference |
|---|---|---|---|
| `kpi1_throughput` | `v1` | `items_success / nb_robot_heures_operationnelles` | Calcul de debit de base. |
| `kpi1_throughput` | `v2` | Meme calcul que `v1`, apres exclusion des longues maintenances programmees. | Le seuil d'exclusion vient de `maintenance_threshold_h`. |
| `kpi2_availability` | `v1` | `active / (active + panne + maintenance_programmee)` | La maintenance programmee penalise la disponibilite. |
| `kpi2_availability` | `v2` | `active / (active + panne)` | La maintenance programmee est sortie du denominateur. |
| `kpi3_order_accuracy` | `v1` | `lignes_correctes / lignes_totales` | Les commandes peuvent etre filtrees avec `min_lines`. |

## Lecture rapide

- `kpi1` montre une version ajustee par parametre : meme famille de calcul, seuil configurable.
- `kpi2` montre une vraie difference structurelle : le denominateur change.
- `kpi3` sert d'exemple simple avec une seule version active.
