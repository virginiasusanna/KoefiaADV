"""Wrapper sottile sull'SDK ufficiale facebook-business.

Le credenziali vengono lette da variabili d'ambiente (vedi .env.example) e
l'inizializzazione avviene solo alla prima chiamata (lazy), cosi' il server
si avvia anche se le credenziali non sono ancora state configurate: fallisce
solo quando viene davvero invocato un tool.
"""
import os

from facebook_business.api import FacebookAdsApi
from facebook_business.adobjects.adaccount import AdAccount


class MetaClient:
    def __init__(self):
        app_id = os.environ["META_APP_ID"]
        app_secret = os.environ["META_APP_SECRET"]
        access_token = os.environ["META_ACCESS_TOKEN"]
        ad_account_id = os.environ["META_AD_ACCOUNT_ID"]  # es. act_1234567890
        if not ad_account_id.startswith("act_"):
            ad_account_id = f"act_{ad_account_id}"

        FacebookAdsApi.init(app_id, app_secret, access_token)
        self.ad_account_id = ad_account_id
        self.account = AdAccount(ad_account_id)
