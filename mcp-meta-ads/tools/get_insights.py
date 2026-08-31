"""Tool READ-only: performance (spesa, CPL, conversioni) da Meta Ads."""
from facebook_business.adobjects.campaign import Campaign

FIELDS = [
    "campaign_name",
    "spend",
    "impressions",
    "clicks",
    "cpc",
    "ctr",
    "actions",
    "cost_per_action_type",
]


def get_insights(client, level: str = "campaign", date_preset: str = "last_7d",
                  campaign_id: str = None) -> list:
    params = {"level": level, "date_preset": date_preset}
    if campaign_id:
        insights = Campaign(campaign_id).get_insights(fields=FIELDS, params=params)
    else:
        insights = client.account.get_insights(fields=FIELDS, params=params)
    return [dict(i) for i in insights]
