# Architecture

But du prototype : separer ce qui change dans le code de ce qui change dans la configuration.

## Les 3 tables de configuration

`kpi_version_registry.csv`

Liste les versions de KPI implementees dans le code.

Exemple : `kpi2_availability` existe en `v1` et `v2`.

`kpi_assignment.csv`

Dit quelle version s'applique a quel scope, sur quelle periode.

Scopes supportes :

- `client`
- `segment`
- `global`

Un statut explicite permet aussi de dire qu'un KPI n'est pas applicable.

`kpi_parameters.csv`

Contient les reglages internes d'une version : seuils, flags, options.

Exemple : meme version `kpi1_throughput/v2`, mais seuil maintenance different selon le client.

## Resolution

Pour un client, un KPI et une date :

1. Le moteur cherche l'affectation active dans `kpi_assignment.csv`.
2. La ligne la plus specifique gagne : `client` > `segment` > `global`.
3. Si le statut n'est pas `active`, le KPI n'est pas calcule.
4. Le moteur charge les parametres applicables dans `kpi_parameters.csv`.
5. Il applique la fonction de calcul correspondant au couple `(kpi, version)`.

## Regle de decision

Nouvelle version si la formule ou le perimetre change.

Exemple : `kpi2` v1 compte la maintenance dans le denominateur, v2 l'exclut.

Nouveau parametre si seule une valeur de reglage change.

Exemple : seuil de maintenance a 2h pour ACME, 4h pour CIRRUS.

## Idee testee

On evite deux extremes :

- trop de versions pour de simples seuils ;
- une formule unique remplie de flags difficiles a auditer.

La version porte la logique. Les parametres ajustent cette logique.
