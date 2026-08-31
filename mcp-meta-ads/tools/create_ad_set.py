"""Tool di SCRITTURA: crea un ad set (pubblico, budget, evento di conversione)."""
from facebook_business.adobjects.adset import AdSet

from shared.audit_log import log_action
from shared.budget_guard import check_budget


def create_ad_set(client, settings, campaign_id: str, name: str, daily_budget_eur: float,
                   targeting: dict, optimization_goal: str = "OFFSITE_CONVERSIONS",
                   confirm: bool = False) -> dict:
    check_budget(daily_budget_eur, settings.max_daily_budget_eur, "budget giornaliero ad set Meta")

    params = {
        AdSet.Field.name: name,
        AdSet.Field.campaign_id: campaign_id,
        AdSet.Field.daily_budget: int(round(daily_budget_eur * 100)),
        AdSet.Field.targeting: targeting,
        AdSet.Field.optimization_goal: optimization_goal,
        AdSet.Field.billing_event: "IMPRESSIONS",
        AdSet.Field.status: "PAUSED",
    }

    if settings.dry_run or not confirm:
        result = {
            "preview": True,
            "would_create": params,
            "note": "Dry-run o conferma mancante: nessuna chiamata reale effettuata.",
        }
        log_action("meta", "create_ad_set", params, result, dry_run=True)
        return result

    adset = client.account.create_ad_set(params=params)
    result = dict(adset)
    log_action("meta", "create_ad_set", params, result, dry_run=False)
    return result
