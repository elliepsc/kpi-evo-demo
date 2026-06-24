# Changelog des definitions KPI

Ce fichier illustre comment on trace un changement de definition : qui, quand, quoi, et pourquoi.

> C'est un prototype construit comme demonstration. Les raisons ci-dessous sont des
> exemples : elles montrent le type de justification qu'on garderait en conditions reelles,
> pas un historique vecu. L'objectif du mecanisme : pouvoir repondre a
> "pourquoi ce chiffre, pour ce client, a cette date ?".

Auteur des entrees : ellie.pascaud. Les dates, versions et seuils correspondent a `config/`.

| Date d'effet | KPI | Perimetre | Changement | Pourquoi (exemple) |
|---|---|---|---|---|
| 2024-06-01 | kpi1_throughput | ACME | v1 -> v2 | Le debit ne doit plus penaliser les longues maintenances planifiees. Le passe reste en v1 (pas de recalcul). |
| 2024-01-01 | kpi2_availability | segment enterprise | v1 -> v2 | Disponibilite alignee sur une mesure qui exclut la maintenance planifiee. Regle posee au niveau segment, pas client par client. |
| 2023-01-01 | kpi1_throughput | CIRRUS | v2, seuil 4h | Fenetres de maintenance plus longues chez ce client. Difference parametrique (meme version), pas une nouvelle version. |
| 2023-01-01 | kpi2_availability | BOLT | not_applicable | Ce client ne suit pas ce KPI. Statut explicite plutot qu'un null. |
| 2023-01-01 | tous | global | definitions v1 | Base de reference commune avant toute evolution par client. |

## Restatement vs as-of
Choix par defaut sur ce prototype : **as-of** (on ne recalcule pas le passe quand une regle change).
A trancher par KPI avec le metier en conditions reelles.
