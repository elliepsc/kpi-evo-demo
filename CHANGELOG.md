# Changelog des définitions de KPI

Ce fichier trace **qui** a changé **quoi**, **quand**, et surtout **pourquoi**.
Chaque ligne de `config/` (affectation ou paramètre) correspond à une décision documentée ici.

> Objectif : pouvoir répondre en trente secondes à
> « pourquoi ce chiffre, pour ce client, à cette date ? », preuve à l'appui.

Les entrées sont classées de la plus récente à la plus ancienne.

---

## 2024-06-01 — ACME · `kpi1_throughput` : v1 → v2
- **Qui** : ellie.pascaud
- **Quoi** : migration de la version v1 vers v2 (exclut la maintenance programmée ≥ 2h et les runs de test).
- **Pourquoi** : après la revue des écarts du T1, ACME a demandé que le débit reflète la capacité réelle hors fenêtres de maintenance planifiées. Validé avec le référent métier ACME.
- **Historique** : pas de recalcul rétroactif — le passé reste en v1 (politique *as-of*, voir bas de page).

## 2024-01-01 — Segment `enterprise` · `kpi2_availability` : v1 → v2
- **Qui** : ellie.pascaud
- **Quoi** : les clients du segment `enterprise` (ACME, CIRRUS) passent à la disponibilité *opérationnelle* (maintenance programmée exclue du dénominateur).
- **Pourquoi** : aligner la mesure sur l'engagement SLA enterprise, qui ne pénalise pas la maintenance planifiée. Appliqué au niveau du segment pour éviter de dupliquer la règle client par client.

## Depuis l'origine (2023-01-01)
- **CIRRUS · `kpi1_throughput` directement en v2, seuil `maintenance_threshold_h` = 4** (vs 2 par défaut).
  *Qui* : ellie.pascaud — *Pourquoi* : les fenêtres de maintenance contractuelles de CIRRUS vont jusqu'à 4h ; en deçà, l'arrêt est considéré comme normal. Différence **paramétrique** (même version v2, seuil différent), pas une nouvelle version.
- **BOLT · `kpi2_availability` = `not_applicable`.**
  *Qui* : ellie.pascaud — *Pourquoi* : BOLT n'a pas souscrit au suivi de disponibilité. Statut explicite pour distinguer « non suivi » d'un « 0 % ».
- **Définitions de référence v1 pour tous ; `kpi3_order_accuracy` non applicable par défaut** (activé en v1 pour ACME et CIRRUS).
  *Qui* : ellie.pascaud — *Pourquoi* : figer une base commune avant d'autoriser les évolutions par client.

---

### Politique restatement vs as-of
Par défaut sur ce périmètre : **as-of** — le passé reste calculé avec la version en vigueur à l'époque ; on ne recalcule pas l'historique. Toute exception (recalcul rétroactif) doit être notée explicitement dans l'entrée concernée. *À valider avec le métier, KPI par KPI.*
