# Definitions KPI

Une fiche par KPI : ce qu'il mesure, son grain, sa source, son proprietaire,
et la modalite de calcul exacte de chaque version.

La version active par client est dans `config/kpi_assignment.csv`.
Les seuils et options sont dans `config/kpi_parameters.csv`.
L'historique des decisions (qui / quand / pourquoi) est dans `CHANGELOG.md`.
Le calcul est implemente dans `scripts/kpi_catalog.py` : cette fiche le decrit, le code l'applique.

---

## kpi1_throughput  --  Debit

- Question metier : combien d'items un robot traite-t-il avec succes par heure ?
- Grain : 1 ligne = 1 robot x 1 heure.
- Source : `raw_robot_activity`.
- Proprietaire metier : [a designer]   |   Referent data : ellie.pascaud
- Robot-heure operationnelle = ligne ou `active_min > 0`.

| Version | Statut | Modalite de calcul |
|---|---|---|
| v1 | deprecated | `somme(items_success) / nombre de robot-heures operationnelles`. Les runs de test sont inclus ou exclus selon le parametre `include_test_runs`. |
| v2 | active | Idem v1, mais on exclut **en dur** les robot-heures sous maintenance programmee appartenant a une fenetre `>= maintenance_threshold_h` (ecart structurel). Les runs de test sont exclus **via le parametre** `include_test_runs = false`, pas en dur. |

- Arrondi : 2 decimales.
- Parametres : `include_test_runs` (v1 = true, v2 = false)  |  `maintenance_threshold_h` (defaut 2 ; CIRRUS = 4).
- Nature des ecarts : exclusion de la longue maintenance = **structurel** (porte par la version v2) ; `include_test_runs` et seuil 2h vs 4h = **parametriques** (memes pour une version, ajustables par scope).

---

## kpi2_availability  --  Disponibilite (%)

- Question metier : quelle part du temps le robot est-il actif ?
- Grain : 1 ligne = 1 robot x 1 heure.
- Source : `raw_robot_activity`.
- Proprietaire metier : [a designer]   |   Referent data : ellie.pascaud

| Version | Statut | Modalite de calcul |
|---|---|---|
| v1 | active (defaut global) | `100 * active / (active + panne + maintenance_programmee)`. La maintenance est **comptee** au denominateur (disponibilite brute). |
| v2 | active (segment enterprise) | `100 * active / (active + panne)`. La maintenance programmee est **exclue** du denominateur (disponibilite operationnelle). |

- Arrondi : 1 decimale.
- Parametres : aucun.
- Nature de l'ecart : purement **structurel** (le perimetre du denominateur change, pas un seuil).
- Non applicable : BOLT (statut explicite `not_applicable`, pas un 0%).

---

## kpi3_order_accuracy  --  Exactitude commande (%)

- Question metier : quelle part des lignes de commande est correcte ?
- Grain : 1 ligne = 1 commande.
- Source : `raw_order_fulfillment`.
- Proprietaire metier : [a designer]   |   Referent data : ellie.pascaud

| Version | Statut | Modalite de calcul |
|---|---|---|
| v1 | active | `100 * somme(lignes_correctes) / somme(lignes_totales)`, sur les commandes ayant `lines_total >= min_lines`. |

- Arrondi : 2 decimales.
- Parametres : `min_lines` (defaut 1).
- Applicable : ACME, CIRRUS. Non applicable par defaut (dont BOLT) -- gere par statut, pas par `null`.
