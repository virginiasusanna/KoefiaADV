#!/usr/bin/env python3
"""Status report aggregato: "funziona tutto?" in un colpo d'occhio.

Per ogni piattaforma configurata (Meta / Google / TikTok) mostra spesa reale
vs spesa attesa secondo il piano (scripts/plan.py), impression/click/CTR e
conversioni. Da HubSpot mostra i lead arrivati dall'inizio campagna e quali
non sono ancora stati lavorati (nessuna nota/attivita').

Uso:
    python scripts/status_report.py [--days N]

Richiede il .env compilato per le piattaforme che si vogliono controllare;
una piattaforma senza credenziali viene semplicemente segnalata come "non
configurata" e saltata, non blocca il resto del report.
"""
import argparse
import importlib.util
import os
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from dotenv import load_dotenv
load_dotenv(ROOT / ".env")

from shared.config import Settings  # noqa: E402
from scripts import plan  # noqa: E402


def _load_module(unique_name: str, file_path: Path):
    spec = importlib.util.spec_from_file_location(unique_name, file_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[unique_name] = module
    spec.loader.exec_module(module)
    return module


def _load_platform(platform: str, client_module_name: str, client_class_name: str):
    """Carica in isolamento client.py + tools/list_campaigns.py + tools/get_insights.py
    di una piattaforma, senza inquinare sys.modules per le altre (i tre server hanno
    tutti un package locale 'tools', quindi vanno caricati con nomi univoci)."""
    base = ROOT / f"mcp-{platform}-ads"
    sys.path.insert(0, str(base))  # necessario perche' i moduli si importano tra loro con nomi relativi
    try:
        client_mod = _load_module(f"{platform}_client_mod", base / f"{client_module_name}.py")
        list_campaigns_mod = _load_module(f"{platform}_list_campaigns", base / "tools" / "list_campaigns.py")
        get_insights_mod = _load_module(f"{platform}_get_insights", base / "tools" / "get_insights.py")
        client_class = getattr(client_mod, client_class_name)
        return client_class, list_campaigns_mod.list_campaigns, get_insights_mod.get_insights
    finally:
        sys.path.remove(str(base))


def _platform_configured(required_env_vars: list) -> bool:
    return all(os.getenv(v) for v in required_env_vars)


def report_meta(days: int) -> dict:
    required = ["META_APP_ID", "META_APP_SECRET", "META_ACCESS_TOKEN", "META_AD_ACCOUNT_ID"]
    if not _platform_configured(required):
        return {"configured": False}

    ClientClass, list_campaigns, get_insights = _load_platform("meta", "meta_client", "MetaClient")
    client = ClientClass()
    date_preset = {3: "last_3d", 7: "last_7d", 14: "last_14d", 30: "last_30d"}.get(days, "last_7d")
    insights = get_insights(client, level="account", date_preset=date_preset)
    campaigns = list_campaigns(client)

    spend = sum(float(i.get("spend", 0)) for i in insights)
    impressions = sum(int(i.get("impressions", 0)) for i in insights)
    clicks = sum(int(i.get("clicks", 0)) for i in insights)
    return {
        "configured": True,
        "spend_eur": round(spend, 2),
        "impressions": impressions,
        "clicks": clicks,
        "ctr_pct": round(100 * clicks / impressions, 2) if impressions else None,
        "campaigns_count": len(campaigns),
        "active_campaigns": [c["name"] for c in campaigns if c.get("effective_status") == "ACTIVE"],
    }


def report_google(days: int) -> dict:
    required = ["GOOGLE_ADS_DEVELOPER_TOKEN", "GOOGLE_ADS_CLIENT_ID", "GOOGLE_ADS_CLIENT_SECRET",
                "GOOGLE_ADS_REFRESH_TOKEN", "GOOGLE_ADS_CUSTOMER_ID"]
    if not _platform_configured(required):
        return {"configured": False}

    ClientClass, list_campaigns, get_insights = _load_platform(
        "google", "google_ads_client", "GoogleAdsClientWrapper")
    wrapper = ClientClass()
    date_range = {3: "LAST_3_DAYS", 7: "LAST_7_DAYS", 14: "LAST_14_DAYS", 30: "LAST_30_DAYS"}.get(
        days, "LAST_7_DAYS")
    insights = get_insights(wrapper, date_range=date_range)
    campaigns = list_campaigns(wrapper)

    spend = sum(i["spend_eur"] for i in insights)
    impressions = sum(i["impressions"] for i in insights)
    clicks = sum(i["clicks"] for i in insights)
    return {
        "configured": True,
        "spend_eur": round(spend, 2),
        "impressions": impressions,
        "clicks": clicks,
        "ctr_pct": round(100 * clicks / impressions, 2) if impressions else None,
        "campaigns_count": len(campaigns),
        "active_campaigns": [c["name"] for c in campaigns if c.get("status") == "ENABLED"],
    }


def report_tiktok(days: int) -> dict:
    required = ["TIKTOK_ACCESS_TOKEN", "TIKTOK_ADVERTISER_ID"]
    if not _platform_configured(required):
        return {"configured": False}

    ClientClass, list_campaigns, get_insights = _load_platform("tiktok", "tiktok_client", "TikTokClient")
    client = ClientClass()
    end_date = date.today()
    start_date = end_date - timedelta(days=days)
    insights = get_insights(client, start_date.isoformat(), end_date.isoformat())
    campaigns = list_campaigns(client)

    spend = sum(float(row.get("metrics", {}).get("spend", 0)) for row in insights)
    impressions = sum(int(row.get("metrics", {}).get("impressions", 0)) for row in insights)
    clicks = sum(int(row.get("metrics", {}).get("clicks", 0)) for row in insights)
    return {
        "configured": True,
        "spend_eur": round(spend, 2),
        "impressions": impressions,
        "clicks": clicks,
        "ctr_pct": round(100 * clicks / impressions, 2) if impressions else None,
        "campaigns_count": len(campaigns),
        "active_campaigns": [c.get("campaign_name") for c in campaigns
                              if c.get("operation_status") == "ENABLE"],
    }


def report_hubspot_leads(since: date) -> dict:
    if not os.getenv("HUBSPOT_PRIVATE_APP_TOKEN"):
        return {"configured": False}

    from shared.hubspot_client import HubSpotClient
    client = HubSpotClient()
    since_millis = int(datetime.combine(since, datetime.min.time(), tzinfo=timezone.utc).timestamp() * 1000)

    data = client.search_contacts(
        filters=[{"propertyName": "createdate", "operator": "GTE", "value": str(since_millis)}],
        properties=["email", "firstname", "lastname", "createdate", "hs_is_unworked",
                    "hs_analytics_source", "hs_latest_source"],
        sorts=[{"propertyName": "createdate", "direction": "DESCENDING"}],
    )
    contacts = data.get("results", [])
    now = datetime.now(timezone.utc)
    unworked = []
    for c in contacts:
        props = c["properties"]
        if props.get("hs_is_unworked") == "true":
            created = datetime.fromisoformat(props["createdate"].replace("Z", "+00:00"))
            age_hours = round((now - created).total_seconds() / 3600, 1)
            unworked.append({
                "name": f"{props.get('firstname', '')} {props.get('lastname', '')}".strip(),
                "email": props.get("email"),
                "source": props.get("hs_latest_source"),
                "age_hours": age_hours,
            })
    return {"configured": True, "total_leads": len(contacts), "unworked": unworked}


def print_report(days: int):
    today = date.today()
    phase = plan.current_phase(today)
    print(f"\n=== Status report campagna Open Day Koefia — {today.isoformat()} ===")
    print(f"Fase corrente: {phase['name'] if phase else 'nessuna (fuori dalle date pianificate)'}\n")

    for platform, fn in (("meta", report_meta), ("google", report_google), ("tiktok", report_tiktok)):
        print(f"--- {platform.upper()} (ultimi {days} giorni) ---")
        try:
            r = fn(days)
        except Exception as e:
            print(f"  ERRORE nel leggere i dati: {e}\n")
            continue

        if not r["configured"]:
            print("  Non configurato (credenziali mancanti nel .env)\n")
            continue

        expected = plan.expected_spend_to_date(platform, today)
        pacing_pct = round(100 * r["spend_eur"] / expected, 1) if expected else None
        print(f"  Spesa: {r['spend_eur']}EUR  |  Attesa a oggi (da piano): {expected}EUR"
              + (f"  -> pacing {pacing_pct}%" if pacing_pct is not None else ""))
        if pacing_pct is not None and (pacing_pct < 50 or pacing_pct > 150):
            print("  ANOMALIA: pacing fuori dal range 50-150% dell'atteso — da controllare.")
        print(f"  Impression: {r['impressions']}  |  Click: {r['clicks']}  |  CTR: {r['ctr_pct']}%")
        print(f"  Campagne attive: {r['active_campaigns']}\n")

    print("--- HUBSPOT: lead e follow-up ---")
    campaign_start = plan.PHASES[0]["start"]
    hs = report_hubspot_leads(campaign_start)
    if not hs["configured"]:
        print("  Non configurato (HUBSPOT_PRIVATE_APP_TOKEN mancante nel .env)\n")
    else:
        print(f"  Lead totali dal {campaign_start.isoformat()}: {hs['total_leads']}")
        if hs["unworked"]:
            print(f"  NON LAVORATI ({len(hs['unworked'])}):")
            for u in hs["unworked"]:
                print(f"    - {u['name']} <{u['email']}> fonte={u['source']} da {u['age_hours']}h")
        else:
            print("  Tutti i lead risultano lavorati.")
        print()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--days", type=int, default=7, help="Finestra giorni per spend/insights")
    args = parser.parse_args()
    print_report(args.days)
