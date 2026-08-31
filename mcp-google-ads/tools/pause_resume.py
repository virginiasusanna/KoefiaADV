"""Tool di SCRITTURA: pausa/riattiva una campagna. Richiede SEMPRE confirm=True
esplicito, indipendentemente da DRY_RUN — mai un'azione distruttiva automatica."""
from shared.audit_log import log_action


def _set_status(wrapper, campaign_id: str, status: str, confirm: bool) -> dict:
    params = {"campaign_id": campaign_id, "status": status}

    if not confirm:
        result = {
            "preview": True,
            "would_update": params,
            "note": "Serve confirm=True esplicito per mettere in pausa/riattivare una campagna.",
        }
        log_action("google", f"set_status:{status}", params, result, dry_run=True)
        return result

    client = wrapper.client
    campaign_service = client.get_service("CampaignService")
    campaign_op = client.get_type("CampaignOperation")
    campaign = campaign_op.update
    campaign.resource_name = campaign_service.campaign_path(wrapper.customer_id, campaign_id)
    campaign.status = getattr(client.enums.CampaignStatusEnum, status)
    client.copy_from(campaign_op.update_mask, client.get_type("FieldMask")(paths=["status"]))

    campaign_service.mutate_campaigns(customer_id=wrapper.customer_id, operations=[campaign_op])
    result = {"campaign_id": campaign_id, "status": status}
    log_action("google", f"set_status:{status}", params, result, dry_run=False)
    return result


def pause_campaign(wrapper, campaign_id: str, confirm: bool = False) -> dict:
    return _set_status(wrapper, campaign_id, "PAUSED", confirm)


def resume_campaign(wrapper, campaign_id: str, confirm: bool = False) -> dict:
    return _set_status(wrapper, campaign_id, "ENABLED", confirm)
