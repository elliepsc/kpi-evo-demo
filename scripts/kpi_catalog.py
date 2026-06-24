"""Catalogue des calculs KPI disponibles."""


def _safe_ratio(numerator, denominator, multiplier=1, decimals=2):
    if denominator == 0:
        return None
    return round(multiplier * numerator / denominator, decimals)


def _throughput(df, params, exclude_long_maintenance=False):
    d = df.copy()
    if not params.get("include_test_runs", True):
        d = d[~d.is_test_run]
    if exclude_long_maintenance:
        threshold = params.get("maintenance_threshold_h", 2)
        d = d[~((d.planned_maintenance_min > 0) & (d.maintenance_event_h >= threshold))]
    op = d[d.active_min > 0]
    return _safe_ratio(op.items_success.sum(), len(op), decimals=2)


# Throughput = items reussis / robot-heures operationnelles
def calc_kpi1_v1(df, params):
    return _throughput(df, params)


# Throughput v2 = v1, hors longues maintenances programmees
def calc_kpi1_v2(df, params):
    return _throughput(df, params, exclude_long_maintenance=True)


# Disponibilite v1 = maintenance programmee comptee au denominateur.
def calc_kpi2_v1(df, params):
    active = df.active_min.sum()
    total = active + df.downtime_min.sum() + df.planned_maintenance_min.sum()
    return _safe_ratio(active, total, multiplier=100, decimals=1)


# Disponibilite v2 = maintenance programmee exclue du denominateur.
def calc_kpi2_v2(df, params):
    active = df.active_min.sum()
    total = active + df.downtime_min.sum()
    return _safe_ratio(active, total, multiplier=100, decimals=1)


# Exactitude commande v1 = lignes correctes / lignes totales, avec un filtre sur le nombre de lignes.
def calc_kpi3_v1(df, params):
    d = df[df.lines_total >= params.get("min_lines", 1)]
    return _safe_ratio(d.lines_correct.sum(), d.lines_total.sum(), multiplier=100, decimals=2)

# Mapping des sources de donnees pour chaque KPI
KPI_SOURCES = {
    "kpi1_throughput": "robot_activity",
    "kpi2_availability": "robot_activity",
    "kpi3_order_accuracy": "order_fulfillment",
}

# Mapping des fonctions de calcul pour chaque KPI et version
CALCULATIONS = {
    ("kpi1_throughput", "v1"): calc_kpi1_v1,
    ("kpi1_throughput", "v2"): calc_kpi1_v2,
    ("kpi2_availability", "v1"): calc_kpi2_v1,
    ("kpi2_availability", "v2"): calc_kpi2_v2,
    ("kpi3_order_accuracy", "v1"): calc_kpi3_v1,
}

# Liste des KPI disponibles
KPI_IDS = list(KPI_SOURCES)
