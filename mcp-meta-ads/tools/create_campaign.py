"""Tool di SCRITTURA: crea una campagna Meta.

Guardrail (vedi brief): senza confirm=True esplicito (o in DRY_RUN, il default)
non viene eseguita nessuna chiamata reale, solo un'anteprima del payload.
Il budget e' sempre validato contro il tetto configurato in .env.
"""
from facebook_business.adobjects.campaign import Campaign

from shared.audit_log import log_action
from shared.budget_guard import check_budget


def create_campaign(client, settings, name: str, objective: str, daily_budget_eur: float,
                     status: str = "PAUSED", confirm: bool = False) -> dict:
    check_budget(daily_budget_eur, settings.max_daily_budget_eur, "budget giornaliero campagna Meta")

    params = {
        Campaign.Field.name: name,
        Campaign.Field.objective: objective,
        Campaign.Field.status: status,
        Campaign.Field.special_ad_categories: [],
        "daily_budget": int(round(daily_budget_eur * 100)),  # centesimi
    }

    if settings.dry_run or not confirm:
        result = {
            "preview": True,
            "would_create": params,
            "note": "Dry-run o conferma mancante: nessuna chiamata reale effettuata. "
                    "Richiama con confirm=True (e META_DRY_RUN=false nel .env) per eseguire davvero.",
        }
        log_action("meta", "create_campaign", params, result, dry_run=True)
        return result

    campaign = client.account.create_campaign(params=params)
    result = dict(campaign)
    log_action("meta", "create_campaign", params, result, dry_run=False)
    return result
