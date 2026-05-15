#!/usr/bin/env python3
import urllib.request
import urllib.error
import json
import os
from datetime import datetime, UTC

API_FI = "https://trafi2.stat.fi/PXWeb/api/v1/fi/TraFi/TraFi__Kaytettyna_maahantuodut/040_yksmaah_tau_104.px"
API_EN = "https://trafi2.stat.fi/PXWeb/api/v1/en/TraFi/TraFi__Kaytettyna_maahantuodut/040_yksmaah_tau_104.px"

def get_metadata(url):
    req = urllib.request.Request(url, headers={"Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        print(f"  GET {url} -> {e.code}: {body[:200]}")
        return None

def px_post(url, query):
    body = json.dumps({"query": query, "response": {"format": "json"}}, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(url, data=body, headers={
        "Content-Type": "application/json; charset=utf-8",
        "Accept": "application/json",
    })
    try:
        with urllib.request.urlopen(req, timeout=90) as r:
            data = r.read().decode("utf-8")
            print(f"  OK {r.status}, {len(data)} merkkia")
            return json.loads(data)
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        print(f"  VIRHE {e.code}: {body[:300]}")
        raise

def main():
    # Step 1: Get metadata from both endpoints to find exact variable codes
    print("=== METADATA FI ===")
    meta_fi = get_metadata(API_FI)
    if meta_fi:
        for v in meta_fi.get("variables", []):
            print(f'code="{v["code"]}"  text="{v["text"]}"')
            print(f'  values[0..3]: {v["values"][:4]}')
            print(f'  texts[0..3]:  {v["valueTexts"][:4]}')
    else:
        print("FI metadata ei onnistu GET:lla")

    print("\n=== METADATA EN ===")
    meta_en = get_metadata(API_EN)
    if meta_en:
        for v in meta_en.get("variables", []):
            print(f'code="{v["code"]}"  text="{v["text"]}"')
            print(f'  values[0..3]: {v["values"][:4]}')
            print(f'  texts[0..3]:  {v["valueTexts"][:4]}')
    else:
        print("EN metadata ei onnistu GET:lla")

    # Step 2: Try posting with codes found from metadata
    if meta_fi:
        vars_fi = {v["code"]: v for v in meta_fi["variables"]}
        print("\n=== FI POST TESTI ===")
        query = []
        for code, v in vars_fi.items():
            query.append({
                "code": code,
                "selection": {"filter": "item", "values": [v["values"][0]]}
            })
        print(f"Query: {json.dumps(query, ensure_ascii=False)}")
        try:
            result = px_post(API_FI, query)
            print(f"Arvo[0]: {result['value'][0]}")
        except:
            pass

    if meta_en:
        vars_en = {v["code"]: v for v in meta_en["variables"]}
        print("\n=== EN POST TESTI ===")
        query = []
        for code, v in vars_en.items():
            query.append({
                "code": code,
                "selection": {"filter": "item", "values": [v["values"][0]]}
            })
        print(f"Query: {json.dumps(query, ensure_ascii=False)}")
        try:
            result = px_post(API_EN, query)
            print(f"Arvo[0]: {result['value'][0]}")
        except:
            pass

    print("\nValmis.")

if __name__ == "__main__":
    main()
