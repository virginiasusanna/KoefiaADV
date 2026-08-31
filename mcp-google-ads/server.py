"""MCP server per Google Ads. Entry point.

Avvio: python server.py  (richiede .env compilato, vedi .env.example)
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))  # per importare shared/

from dotenv import load_dotenv
load_dotenv()

from mcp.server.fastmcp import FastMCP

from google_ads_client import GoogleAdsClientWrapper
from shared.config import Settings

from tools.list_campaigns import list_campaigns as _list_campaigns
from tools.get_insights import get_insights as _get_insights
from tools.create_campaign import create_campaign as _create_campaign
from tools.pause_resume import pause_campaign as _pause_campaign, resume_campaign as _resume_campaign

mcp = FastMCP("google-ads")
settings = Settings(prefix="GOOGLE")
_wrapper = None


def get_wrapper() -> GoogleAdsClientWrapper:
    global _wrapper
    if _wrapper is None:
        _wrapper = GoogleAdsClientWrapper()
    return _wrapper


@mcp.tool()
def list_campaigns(limit: int = 50) -> list:
    """Elenca le campagne Google Ads esistenti. Sola lettura, basso rischio."""
    return _list_campaigns(get_wrapper(), limit)


@mcp.tool()
def get_insights(date_range: str = "LAST_7_DAYS", campaign_id: str = None) -> list:
    """Metriche di performance (spesa, CPC, conversioni). Sola lettura, basso rischio.

    date_range: es. TODAY, YESTERDAY, LAST_7_DAYS, LAST_14_DAYS, LAST_30_DAYS, THIS_MONTH.
    """
    return _get_insights(get_wrapper(), date_range, campaign_id)


@mcp.tool()
def create_campaign(name: str, daily_budget_eur: float, channel_type: str = "SEARCH",
                     confirm: bool = False) -> dict:
    """Crea budget + campagna Google Ads (PAUSED). Senza confirm=True: solo anteprima.
    Il budget e' validato contro GOOGLE_MAX_DAILY_BUDGET_EUR."""
    return _create_campaign(get_wrapper(), settings, name, daily_budget_eur, channel_type, confirm)


@mcp.tool()
def pause_campaign(campaign_id: str, confirm: bool = False) -> dict:
    """Mette in pausa una campagna. Azione distruttiva: richiede SEMPRE confirm=True esplicito."""
    return _pause_campaign(get_wrapper(), campaign_id, confirm)


@mcp.tool()
def resume_campaign(campaign_id: str, confirm: bool = False) -> dict:
    """Riattiva (ENABLED) una campagna in pausa. Richiede SEMPRE confirm=True esplicito."""
    return _resume_campaign(get_wrapper(), campaign_id, confirm)


if __name__ == "__main__":
    mcp.run()
