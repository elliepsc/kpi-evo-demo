#!/usr/bin/env python3
"""Garde-fou de configuration KPI. Verifie la coherence de config/ avant tout calcul."""
import csv
import os
import sys
from collections import defaultdict
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
CONFIG = os.path.join(ROOT, "config")
sys.path.insert(0, HERE)
import kpi_catalog  # noqa: E402

ALLOWED_STATUS = {"active", "not_applicable", "pending_migration", "deprecated"}
errors, warnings = [], []


def read_csv(name):
    with open(os.path.join(CONFIG, name), newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def parse_date(s, where):
    try:
        return datetime.strptime(s.strip(), "%Y-%m-%d").date()
    except ValueError:
        errors.append(f"{where}: date invalide '{s}'.")
        return None


registry = read_csv("kpi_version_registry.csv")
assignment = read_csv("kpi_assignment.csv")
parameters = read_csv("kpi_parameters.csv")

reg_versions = {(r["kpi_id"], r["version"]) for r in registry}
reg_kpis = {r["kpi_id"] for r in registry}
calc_keys = set(kpi_catalog.CALCULATIONS.keys())

for r in registry:
    key = (r["kpi_id"], r["version"])
    if r["status"].strip() == "active" and key not in calc_keys:
        errors.append(f"Registre {key}: 'active' mais aucune fonction de calcul dans kpi_catalog.")

for r in assignment:
    where = f"Affectation[{r['scope_type']}/{r['scope_id']}/{r['kpi_id']}]"
    status, version = r["status"].strip(), r["version"].strip()
    if status not in ALLOWED_STATUS:
        errors.append(f"{where}: statut inconnu '{status}'.")
    if r["kpi_id"] not in reg_kpis:
        errors.append(f"{where}: KPI absent du registre.")
    if status == "active":
        if not version:
            errors.append(f"{where}: statut 'active' sans version.")
        else:
            if (r["kpi_id"], version) not in reg_versions:
                errors.append(f"{where}: version '{version}' absente du registre.")
            if (r["kpi_id"], version) not in calc_keys:
                errors.append(f"{where}: aucune fonction de calcul pour ('{r['kpi_id']}','{version}').")
    elif status == "not_applicable" and version:
        warnings.append(f"{where}: 'not_applicable' mais une version est renseignee ('{version}').")
    d_from = parse_date(r["effective_from"], where)
    d_to = parse_date(r["effective_to"], where)
    if d_from and d_to and d_from > d_to:
        errors.append(f"{where}: effective_from ({d_from}) posterieure a effective_to ({d_to}).")

groups = defaultdict(list)
for r in assignment:
    d_from = parse_date(r["effective_from"], "chevauchement")
    d_to = parse_date(r["effective_to"], "chevauchement")
    if d_from and d_to:
        groups[(r["scope_type"], r["scope_id"], r["kpi_id"])].append((d_from, d_to, r["version"] or r["status"]))
for (st, sid, kpi), intervals in groups.items():
    intervals.sort()
    for i in range(len(intervals)):
        for j in range(i + 1, len(intervals)):
            af, at, al = intervals[i]
            bf, bt, bl = intervals[j]
            if af <= bt and bf <= at:
                errors.append(f"Chevauchement {st}/{sid}/{kpi}: '{al}' [{af}->{at}] et '{bl}' [{bf}->{bt}] se recouvrent.")

for r in parameters:
    where = f"Parametre[{r['scope_type']}/{r['scope_id']}/{r['kpi_id']}/{r['version']}/{r['param_name']}]"
    if (r["kpi_id"], r["version"]) not in reg_versions:
        errors.append(f"{where}: ('{r['kpi_id']}','{r['version']}') absent du registre.")
    parse_date(r["effective_from"], where)
    parse_date(r["effective_to"], where)

with_global = {r["kpi_id"] for r in assignment if r["scope_type"] == "global"}
for kpi in sorted(reg_kpis):
    if kpi not in with_global:
        warnings.append(f"KPI '{kpi}': pas d'affectation 'global' (aucune valeur par defaut).")

print("=== Validation de la configuration KPI ===")
print(f"Registre    : {len(registry)} versions")
print(f"Affectations: {len(assignment)} lignes")
print(f"Parametres  : {len(parameters)} lignes\n")
for w in warnings:
    print(f"  [warn]   {w}")
for e in errors:
    print(f"  [ERREUR] {e}")
if not errors and not warnings:
    print("  (rien a signaler)")
print()
if errors:
    print(f"ECHEC : {len(errors)} erreur(s), {len(warnings)} avertissement(s).")
    sys.exit(1)
print(f"OK : configuration coherente ({len(warnings)} avertissement(s)).")
sys.exit(0)
