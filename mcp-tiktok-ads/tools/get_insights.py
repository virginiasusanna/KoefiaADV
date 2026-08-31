"""Tool READ-only: performance (spesa, CPL, conversioni) da TikTok Ads."""
import json


def get_insights(client, start_date: str, end_date: str, campaign_ids: list = None) -> list:
    params = {
        "advertiser_id": client.advertiser_id,
        "report_type": "BASIC",
        "dimensions": json.dumps(["campaign_id"]),
        "metrics": json.dumps([
            "spend", "impressions", "clicks", "ctr", "cpc", "conversion", "cost_per_conversion",
        ]),
        "start_date": start_date,
        "end_date": end_date,
        "data_level": "AUCTION_CAMPAIGN",
        "page_size": 50,
    }
    if campaign_ids:
        params["filtering"] = json.dumps([{
            "field_name": "campaign_ids",
            "filter_type": "IN",
            "filter_value": json.dumps(campaign_ids),
        }])

    data = client.get("/report/integrated/get/", params=params)
    return data.get("data", {}).get("list", [])
