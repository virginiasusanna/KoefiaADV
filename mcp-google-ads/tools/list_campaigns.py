"""Tool READ-only: elenca le campagne Google Ads esistenti."""


def list_campaigns(wrapper, limit: int = 50) -> list:
    ga_service = wrapper.client.get_service("GoogleAdsService")
    query = f"""
        SELECT
          campaign.id,
          campaign.name,
          campaign.status,
          campaign.advertising_channel_type,
          campaign_budget.amount_micros,
          campaign.start_date,
          campaign.end_date
        FROM campaign
        ORDER BY campaign.id
        LIMIT {int(limit)}
    """
    response = ga_service.search(customer_id=wrapper.customer_id, query=query)

    results = []
    for row in response:
        results.append({
            "id": row.campaign.id,
            "name": row.campaign.name,
            "status": row.campaign.status.name,
            "channel_type": row.campaign.advertising_channel_type.name,
            "daily_budget_eur": row.campaign_budget.amount_micros / 1_000_000,
            "start_date": row.campaign.start_date,
            "end_date": row.campaign.end_date,
        })
    return results
