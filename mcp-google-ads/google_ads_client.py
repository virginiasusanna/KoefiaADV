"""Wrapper sottile sull'SDK ufficiale google-ads.

Richiede: developer token, OAuth client id/secret, refresh token (ottenuto una
tantum con un flow OAuth interattivo, vedi README), customer id dell'account
Ads di Koefia. login_customer_id serve solo se si accede tramite un MCC.
"""
import os

from google.ads.googleads.client import GoogleAdsClient


class GoogleAdsClientWrapper:
    def __init__(self):
        self.customer_id = os.environ["GOOGLE_ADS_CUSTOMER_ID"].replace("-", "")
        login_customer_id = os.environ.get("GOOGLE_ADS_LOGIN_CUSTOMER_ID", "").replace("-", "")

        config = {
            "developer_token": os.environ["GOOGLE_ADS_DEVELOPER_TOKEN"],
            "client_id": os.environ["GOOGLE_ADS_CLIENT_ID"],
            "client_secret": os.environ["GOOGLE_ADS_CLIENT_SECRET"],
            "refresh_token": os.environ["GOOGLE_ADS_REFRESH_TOKEN"],
            "use_proto_plus": True,
        }
        if login_customer_id:
            config["login_customer_id"] = login_customer_id

        self.client = GoogleAdsClient.load_from_dict(config)
