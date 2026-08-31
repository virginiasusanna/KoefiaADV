"""Tool di SCRITTURA: crea un budget + una campagna Google Ads (in stato PAUSED).

Nota: copre il caso Search generico. Le campagne Performance Max richiedono
asset group con requisiti aggiuntivi (asset di testo/immagine minimi) non
coperti da questa versione minimale — vedi README per i limiti noti.
"""
from shared.audit_log import log_action
from shared.budget_guard import check_budget


def create_campaign(wrapper, settings, name: str, daily_budget_eur: float,
                     channel_type: str = "SEARCH", confirm: bool = False) -> dict:
    check_budget(daily_budget_eur, settings.max_daily_budget_eur, "budget giornaliero campagna Google")

    preview = {
        "name": name,
        "daily_budget_eur": daily_budget_eur,
        "channel_type": channel_type,
        "status": "PAUSED",
    }

    if settings.dry_run or not confirm:
        result = {
            "preview": True,
            "would_create": preview,
            "note": "Dry-run o conferma mancante: nessuna chiamata reale effettuata. "
                    "Richiama con confirm=True (e GOOGLE_DRY_RUN=false nel .env) per eseguire davvero.",
        }
        log_action("google", "create_campaign", preview, result, dry_run=True)
        return result

    client = wrapper.client
    customer_id = wrapper.customer_id

    budget_service = client.get_service("CampaignBudgetService")
    budget_op = client.get_type("CampaignBudgetOperation")
    budget = budget_op.create
    budget.name = f"{name} - budget"
    budget.delivery_method = client.enums.BudgetDeliveryMethodEnum.STANDARD
    budget.amount_micros = int(round(daily_budget_eur * 1_000_000))
    budget_response = budget_service.mutate_campaign_budgets(customer_id=customer_id, operations=[budget_op])
    budget_resource_name = budget_response.results[0].resource_name

    campaign_service = client.get_service("CampaignService")
    campaign_op = client.get_type("CampaignOperation")
    campaign = campaign_op.create
    campaign.name = name
    campaign.advertising_channel_type = getattr(client.enums.AdvertisingChannelTypeEnum, channel_type)
    campaign.status = client.enums.CampaignStatusEnum.PAUSED
    campaign.campaign_budget = budget_resource_name
    campaign.network_settings.target_google_search = True
    campaign.network_settings.target_search_network = True
    campaign.network_settings.target_partner_search_network = False

    campaign_response = campaign_service.mutate_campaigns(customer_id=customer_id, operations=[campaign_op])
    result = {"resource_name": campaign_response.results[0].resource_name}
    log_action("google", "create_campaign", preview, result, dry_run=False)
    return result
