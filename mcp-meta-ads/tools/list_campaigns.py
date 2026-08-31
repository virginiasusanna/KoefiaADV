"""Tool READ-only: elenca le campagne Meta Ads esistenti."""
from facebook_business.adobjects.campaign import Campaign


def list_campaigns(client, status_filter: str = None, limit: int = 50) -> list:
    fields = [
        Campaign.Field.id,
        Campaign.Field.name,
        Campaign.Field.status,
        Campaign.Field.effective_status,
        Campaign.Field.objective,
        Campaign.Field.daily_budget,
        Campaign.Field.lifetime_budget,
        Campaign.Field.start_time,
        Campaign.Field.stop_time,
    ]
    params = {"limit": limit}
    if status_filter:
        # es. ["ACTIVE"], ["PAUSED"]
        params["effective_status"] = [status_filter]

    campaigns = client.account.get_campaigns(fields=fields, params=params)
    return [dict(c) for c in campaigns]
