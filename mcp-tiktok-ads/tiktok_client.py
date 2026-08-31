"""Client REST diretto per la TikTok Business API (piu' trasparente/semplice
da debuggare rispetto all'SDK non ufficiale, per un progetto di queste dimensioni)."""
import os

import requests

BASE_URL = "https://business-api.tiktok.com/open_api/v1.3"


class TikTokClient:
    def __init__(self):
        self.access_token = os.environ["TIKTOK_ACCESS_TOKEN"]
        self.advertiser_id = os.environ["TIKTOK_ADVERTISER_ID"]
        self.session = requests.Session()
        self.session.headers.update({
            "Access-Token": self.access_token,
            "Content-Type": "application/json",
        })

    def get(self, path: str, params: dict = None) -> dict:
        resp = self.session.get(f"{BASE_URL}{path}", params=params, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        if data.get("code") != 0:
            raise RuntimeError(f"TikTok API error: {data.get('message')} (code {data.get('code')})")
        return data

    def post(self, path: str, payload: dict) -> dict:
        resp = self.session.post(f"{BASE_URL}{path}", json=payload, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        if data.get("code") != 0:
            raise RuntimeError(f"TikTok API error: {data.get('message')} (code {data.get('code')})")
        return data
