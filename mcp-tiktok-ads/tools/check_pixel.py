"""Tool READ-only: stato del pixel TikTok e conteggio eventi ricevuti di
recente — utile per diagnosticare problemi di tracciamento/visibilita'."""


def check_pixel_status(client, pixel_code: str = None) -> list:
    data = client.get("/pixel/list/", params={"advertiser_id": client.advertiser_id})
    pixels = data.get("data", {}).get("pixels", [])
    if pixel_code:
        pixels = [p for p in pixels if p.get("pixel_code") == pixel_code]
    return pixels


def get_pixel_events(client, pixel_code: str, start_date: str, end_date: str) -> dict:
    """Statistiche eventi per pixel (es. quanti PageView/CompleteRegistration ricevuti)."""
    data = client.get("/pixel/statistics/", params={
        "advertiser_id": client.advertiser_id,
        "pixel_code": pixel_code,
        "start_date": start_date,
        "end_date": end_date,
    })
    return data.get("data", {})
