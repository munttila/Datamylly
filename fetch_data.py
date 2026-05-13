#!/usr/bin/env python3
"""
Datamylly - Traficom datahaku
Ajetaan GitHub Actionsissa kerran kuussa.
Tallentaa tuloksen data/latest.json tiedostoon.
"""

import urllib.request
import urllib.error
import json
import os
from datetime import datetime

API = "https://trafi2.stat.fi/PXWeb/api/v1/fi/TraFi/TraFi__Kaytettyna_maahantuodut/040_yksmaah_tau_104.px"

BRANDS = [
    "Volkswagen","Volvo","Mercedes-Benz","BMW","Polestar","Tesla Motors",
    "Audi","Toyota","Skoda","Ford","Hyundai","Kia","Renault","Nissan",
    "Mazda","Opel","Cupra","Dacia","Mitsubishi","Land Rover"
]

PT_CODES = [
    "S\u00e4hk\u00f6",
    "Bensiini/S\u00e4hk\u00f6 (ladattava hybridi)",
    "Diesel/S\u00e4hk\u00f6 (ladattava hybridi)",
    "Bensiini",
    "Diesel",
]
PT_LABELS = ["Sahko","PHEV_bens","PHEV_diesel","Bensiini","Diesel"]

N_MONTHS = 30

def latest_month():
    now = datetime.utcnow()
    m = now.month - 1 or 12
    y = now.year if now.month > 1 else now.year - 1
    return y, m

def build_months(ly, lm):
    months = []
    y, m = ly, lm
    for _ in range(N_MONTHS):
        months.insert(0, {"year": y, "month": m, "code": f"{y}M{m:02d}"})
        m -= 1
        if m == 0:
            m = 12; y -= 1
    return months

def young_years(mon):
    return [str(y) for y in range(mon["year"] - 2, mon["year"] + 1)]

def all_years(months):
    s = set()
    for m in months:
        s.update(young_years(m))
    return sorted(s)

def px_post(query):
    body = json.dumps({"query": query, "response": {"format": "json"}}).encode("utf-8")
    req = urllib.request.Request(
        API, data=body,
        headers={"Content-Type": "application/json; charset=utf-8"}
    )
    with urllib.request.urlopen(req, timeout=90) as r:
        return json.loads(r.read().decode("utf-8"))

def main():
    ly, lm = latest_month()
    print(f"Haetaan: {ly}/{lm:02d}")

    months = build_months(ly, lm)
    yrs = all_years(months)
    nB, nY, nM, nP = len(BRANDS), len(yrs), len(months), len(PT_CODES)
    yi = {y: i for i, y in enumerate(yrs)}

    print("Merkki-data...")
    bd = px_post([
        {"code": "Merkki",                "selection": {"filter": "item", "values": BRANDS}},
        {"code": "K\u00e4ytt\u00f6\u00f6nottovuosi", "selection": {"filter": "item", "values": yrs}},
        {"code": "K\u00e4ytt\u00f6voima",           "selection": {"filter": "item", "values": ["Yhteens\u00e4"]}},
        {"code": "Kuukausi",              "selection": {"filter": "item", "values": [m["code"] for m in months]}},
    ])

    print("Kayttovoima-data...")
    pd_ = px_post([
        {"code": "Merkki",                "selection": {"filter": "item", "values": ["Henkilöautot yhteensä"]}},
        {"code": "K\u00e4ytt\u00f6\u00f6nottovuosi", "selection": {"filter": "item", "values": yrs}},
        {"code": "K\u00e4ytt\u00f6voima",           "selection": {"filter": "item", "values": PT_CODES}},
        {"code": "Kuukausi",              "selection": {"filter": "item", "values": [m["code"] for m in months]}},
    ])

    bv, pv = bd["value"], pd_["value"]
    monthly_brands, monthly_pt, brand_totals = [], [], [0]*nB

    for mi, mon in enumerate(months):
        vy = [y for y in young_years(mon) if y in yi]
        rb = []
        for bi in range(nB):
            s = sum(bv[bi*nY*nM + yi[y]*nM + mi] or 0 for y in vy)
            rb.append(s); brand_totals[bi] += s
        monthly_brands.append(rb)
        monthly_pt.append([
            sum(pv[pi*nY*nM + yi[y]*nM + mi] or 0 for y in vy)
            for pi in range(nP)
        ])

    out = {
        "updated": datetime.utcnow().isoformat(),
        "latest_month": f"{ly}M{lm:02d}",
        "months": [m["code"] for m in months],
        "brands": BRANDS,
        "pt_labels": PT_LABELS,
        "monthly_brands": monthly_brands,
        "monthly_pt": monthly_pt,
        "brand_totals": brand_totals,
    }

    os.makedirs("data", exist_ok=True)
    with open("data/latest.json", "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, separators=(",", ":"))

    total = sum(sum(r) for r in monthly_pt)
    print(f"Valmis. {total:,} autoa 30 kk. data/latest.json tallennettu.")

if __name__ == "__main__":
    main()
