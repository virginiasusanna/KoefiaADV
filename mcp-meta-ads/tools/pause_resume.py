"""Tool di SCRITTURA: pausa/riattiva una campagna. Richiede SEMPRE confirm=True
esplicito, indipendentemente da DRY_RUN — mai un'azione distruttiva automatica."""
from facebook_business.adobjects.campaign import Campaign

from shared.audit_log import log_action


def _set_status(client, campaign_id: str, status: str, confirm: bool) -> dict:
    params = {"campaign_id": campaign_id, "status": status}

    if not confirm:
        result = {
            "preview": True,
            "would_update": params,
            "note": "Serve confirm=True esplicito per mettere in pausa/riattivare una campagna.",
        }
        log_action("meta", f"set_status:{status}", params, result, dry_run=True)
        return result

    campaign = Campaign(campaign_id)
    campaign.api_update(params={Campaign.Field.status: status})
    result = {"campaign_id": campaign_id, "status": status}
    log_action("meta", f"set_status:{status}", params, result, dry_run=False)
    return result


def pause_campaign(client, campaign_id: str, confirm: bool = False) -> dict:
    return _set_status(client, campaign_id, "PAUSED", confirm)


def resume_campaign(client, campaign_id: str, confirm: bool = False) -> dict:
    return _set_status(client, campaign_id, "ACTIVE", confirm)
