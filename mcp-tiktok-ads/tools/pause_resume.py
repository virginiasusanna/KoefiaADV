"""Tool di SCRITTURA: pausa/riattiva una campagna. Richiede SEMPRE confirm=True
esplicito, indipendentemente da DRY_RUN — mai un'azione distruttiva automatica."""
from shared.audit_log import log_action


def _set_status(client, campaign_id: str, status: str, confirm: bool) -> dict:
    payload = {
        "advertiser_id": client.advertiser_id,
        "campaign_ids": [campaign_id],
        "operation_status": status,
    }

    if not confirm:
        result = {
            "preview": True,
            "would_update": payload,
            "note": "Serve confirm=True esplicito per mettere in pausa/riattivare una campagna.",
        }
        log_action("tiktok", f"set_status:{status}", payload, result, dry_run=True)
        return result

    data = client.post("/campaign/status/update/", payload)
    log_action("tiktok", f"set_status:{status}", payload, data, dry_run=False)
    return data


def pause_campaign(client, campaign_id: str, confirm: bool = False) -> dict:
    return _set_status(client, campaign_id, "DISABLE", confirm)


def resume_campaign(client, campaign_id: str, confirm: bool = False) -> dict:
    return _set_status(client, campaign_id, "ENABLE", confirm)
