"""Tool READ-only: performance (spesa, CPL, conversioni) da Google Ads."""


def get_insights(wrapper, date_range: str = "LAST_7_DAYS", campaign_id: str = None) -> list:
    ga_service = wrapper.client.get_service("GoogleAdsService")
    where = f"WHERE campaign.id = {int(campaign_id)}" if campaign_id else ""
    query = f"""
        SELECT
          campaign.id,
          campaign.name,
          metrics.cost_micros,
          metrics.impressions,
          metrics.clicks,
          metrics.ctr,
          metrics.average_cpc,
          metrics.conversions,
          metrics.cost_per_conversion
        FROM campaign
        {where}
        DURING {date_range}
    """
    response = ga_service.search(customer_id=wrapper.customer_id, query=query)

    results = []
    for row in response:
        results.append({
            "campaign_id": row.campaign.id,
            "campaign_name": row.campaign.name,
            "spend_eur": row.metrics.cost_micros / 1_000_000,
            "impressions": row.metrics.impressions,
            "clicks": row.metrics.clicks,
            "ctr": row.metrics.ctr,
            "avg_cpc_eur": row.metrics.average_cpc / 1_000_000,
            "conversions": row.metrics.conversions,
            "cost_per_conversion_eur": row.metrics.cost_per_conversion / 1_000_000 if row.metrics.conversions else None,
        })
    return results
