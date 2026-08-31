"""Client minimale per l'API pubblica HubSpot (Private App Token), usato dallo
status_report per leggere i lead senza dipendere dalla sessione Claude."""
import os

import requests

BASE_URL = "https://api.hubapi.com"


class HubSpotClient:
    def __init__(self):
        self.token = os.environ["HUBSPOT_PRIVATE_APP_TOKEN"]
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        })

    def search_contacts(self, filters: list, properties: list, limit: int = 100,
                         sorts: list = None) -> dict:
        payload = {"filterGroups": [{"filters": filters}], "properties": properties, "limit": limit}
        if sorts:
            payload["sorts"] = sorts
        resp = self.session.post(f"{BASE_URL}/crm/v3/objects/contacts/search", json=payload, timeout=30)
        resp.raise_for_status()
        return resp.json()
