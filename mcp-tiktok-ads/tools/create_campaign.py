"""Tool di SCRITTURA: crea una campagna TikTok (creata disabilitata di default)."""
from shared.audit_log import log_action
from shared.budget_guard import check_budget


def create_campaign(client, settings, name: str, objective: str, daily_budget_eur: float,
                     confirm: bool = False) -> dict:
    check_budget(daily_budget_eur, settings.max_daily_budget_eur, "budget giornaliero campagna TikTok")

    payload = {
        "advertiser_id": client.advertiser_id,
        "campaign_name": name,
        "objective_type": objective,
        "budget_mode": "BUDGET_MODE_DAY",
        "budget": daily_budget_eur,
        "operation_status": "DISABLE",
    }

    if settings.dry_run or not confirm:
        result = {
            "preview": True,
            "would_create": payload,
            "note": "Dry-run o conferma mancante: nessuna chiamata reale effettuata. "
                    "Richiama con confirm=True (e TIKTOK_DRY_RUN=false nel .env) per eseguire davvero.",
        }
        log_action("tiktok", "create_campaign", payload, result, dry_run=True)
        return result

    data = client.post("/campaign/create/", payload)
    log_action("tiktok", "create_campaign", payload, data, dry_run=False)
    return data
