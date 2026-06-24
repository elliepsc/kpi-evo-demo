"""
Moteur d'execution des KPI.
Il lit la configuration, trouve la version et les parametres applicables pour chaque
client/date, puis appelle le calcul correspondant dans `kpi_catalog.py`.
"""

from __future__ import annotations
import pandas as pd
from pathlib import Path
from kpi_catalog import CALCULATIONS, KPI_IDS, KPI_SOURCES

ROOT = Path(__file__).resolve().parents[1]
CFG = ROOT / "config"
RAW = ROOT / "data" / "raw"
OPEN_DATE = "2200-01-01"  # 9999-12-31 est hors bornes pandas

# chargement
def load():
    clients = pd.read_csv(CFG / "clients.csv")
    reg = pd.read_csv(CFG / "kpi_version_registry.csv")
    asg = pd.read_csv(CFG / "kpi_assignment.csv", dtype=str, keep_default_na=False)
    par = pd.read_csv(CFG / "kpi_parameters.csv", dtype=str, keep_default_na=False)
    for df in (asg, par):
        df["effective_from"] = pd.to_datetime(df["effective_from"])
        df["effective_to"] = pd.to_datetime(df["effective_to"].replace("9999-12-31", OPEN_DATE))
    ra = pd.read_parquet(RAW / "raw_robot_activity.parquet")
    od = pd.read_parquet(RAW / "raw_order_fulfillment.parquet")
    return clients, reg, asg, par, ra, od

# resolution
def _scopes_for(client_id, segment):
    return {
        ("client", client_id): 3,
        ("segment", segment): 2,
        ("global", "*"): 1,
    }


def _active_rows(df, as_of):
    as_of = pd.Timestamp(as_of)
    return df[(df.effective_from <= as_of) & (df.effective_to >= as_of)].copy()


def _best_scoped_row(df, scopes):
    df = df[df.apply(lambda r: (r.scope_type, r.scope_id) in scopes, axis=1)].copy()
    if df.empty:
        return None
    df["rank"] = df.apply(lambda r: scopes[(r.scope_type, r.scope_id)], axis=1)
    return df.sort_values(["rank", "effective_from"], ascending=[False, False]).iloc[0]


# resolution de version: version applicable a (client, kpi) a la date as_of
def resolve_version(asg, client_id, segment, kpi_id, as_of):
    cand = _active_rows(asg[asg.kpi_id == kpi_id], as_of)
    row = _best_scoped_row(cand, _scopes_for(client_id, segment))
    if row is None:
        return None, "undefined"
    return row.version or None, row.status

# resolution des parametres: parametres effectifs : global surcharge par segment surcharge par client
def resolve_params(par, client_id, segment, kpi_id, version, as_of):
    if version is None:
        return {}
    cand = _active_rows(par[(par.kpi_id == kpi_id) & (par.version == version)], as_of)
    scopes = _scopes_for(client_id, segment)
    out = {}
    for _, r in cand.iterrows():
        key = (r.scope_type, r.scope_id)
        if key not in scopes:
            continue
        prev = out.get(r.param_name)
        if prev is None or scopes[key] > prev[1]:
            out[r.param_name] = (_cast(r.param_value), scopes[key])
    return {k: v[0] for k, v in out.items()}

# conversion de types:
def _cast(v):
    s = str(v).strip()
    if s.lower() in ("true", "false"):
        return s.lower() == "true"
    try:
        return int(s)
    except ValueError:
        try:
            return float(s)
        except ValueError:
            return s

# orchestration: pour chaque client, kpi, date, on determine la version et les parametres applicables, puis on appelle le calcul correspondant
def run():
    clients, reg, asg, par, ra, od = load()
    ra["day"] = ra.hour_ts.dt.normalize()
    od["day"] = od.order_ts.dt.normalize()
    seg = dict(zip(clients.client_id, clients.segment))
    sources = {"robot_activity": ra, "order_fulfillment": od}
    out = []
    for c in clients.client_id:
        for kpi in KPI_IDS:
            src = sources[KPI_SOURCES[kpi]]
            for day in sorted(src.day.unique()):
                version, status = resolve_version(asg, c, seg[c], kpi, day)
                row = dict(client_id=c, kpi_id=kpi, day=pd.Timestamp(day).date(),
                           version=version or "", status=status, value=None, params="")
                if status != "active" or version is None:
                    out.append(row)
                    continue
                params = resolve_params(par, c, seg[c], kpi, version, day)
                sub = src[(src.client_id == c) & (src.day == day)]
                calc = CALCULATIONS.get((kpi, version))
                if calc is None:
                    raise ValueError(f"Calcul non implemente pour {kpi}/{version}")
                row["value"] = calc(sub, params) if len(sub) else None
                row["params"] = ";".join(f"{k}={v}" for k, v in params.items())
                out.append(row)
    res = pd.DataFrame(out).sort_values(["client_id", "kpi_id", "day"])
    res.to_csv(ROOT / "results" / "kpi_results.csv", index=False)
    res.to_parquet(ROOT / "results" / "kpi_results.parquet", index=False)
    return res

if __name__ == "__main__":
    res = run()
    pd.set_option("display.width", 200, "display.max_rows", 200)
    print("\n=== Echantillon : KPI1 throughput ACME (bascule v1 -> v2 au 2024-06-01) ===")
    print(res[(res.client_id=="ACME") & (res.kpi_id=="kpi1_throughput")].to_string(index=False))
    print("\n=== KPI2 availability : BOLT (not_applicable) vs CIRRUS (v2 via segment enterprise) ===")
    print(res[(res.kpi_id=="kpi2_availability") & (res.client_id.isin(["BOLT","CIRRUS"]))].groupby(["client_id","version","status"]).size().to_string())
    print("\n=== KPI1 v2 : seuil maintenance ACME(2h) vs CIRRUS(4h) le 2024-06-03 ===")
    print(res[(res.kpi_id=="kpi1_throughput") & (res.day==pd.Timestamp('2024-06-03').date()) & (res.client_id.isin(["ACME","CIRRUS"]))].to_string(index=False))
    print("\n=== KPI3 : ACME/CIRRUS (v1) vs BOLT (not_applicable, herite du global) ===")
    print(res[res.kpi_id=="kpi3_order_accuracy"].groupby(["client_id","version","status"]).size().to_string())
