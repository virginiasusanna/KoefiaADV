"""Tool READ-only: elenca le campagne TikTok Ads esistenti."""


def list_campaigns(client, page_size: int = 50) -> list:
    data = client.get("/campaign/get/", params={
        "advertiser_id": client.advertiser_id,
        "page_size": page_size,
    })
    return data.get("data", {}).get("list", [])
