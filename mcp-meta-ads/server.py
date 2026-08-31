"""MCP server per Meta Ads. Entry point.

Avvio: python server.py  (richiede .env compilato, vedi .env.example)
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))  # per importare shared/

from dotenv import load_dotenv
load_dotenv()

from mcp.server.fastmcp import FastMCP

from meta_client import MetaClient
from shared.config import Settings

from tools.list_campaigns import list_campaigns as _list_campaigns
from tools.get_insights import get_insights as _get_insights
from tools.create_campaign import create_campaign as _create_campaign
from tools.create_ad_set import create_ad_set as _create_ad_set
from tools.create_ad import create_ad as _create_ad
from tools.pause_resume import pause_campaign as _pause_campaign, resume_campaign as _resume_campaign

mcp = FastMCP("meta-ads")
settings = Settings(prefix="META")
_client = None


def get_client() -> MetaClient:
    global _client
    if _client is None:
        _client = MetaClient()
    return _client


@mcp.tool()
def list_campaigns(status_filter: str = None, limit: int = 50) -> list:
    """Elenca le campagne Meta Ads esistenti. Sola lettura, basso rischio."""
    return _list_campaigns(get_client(), status_filter, limit)


@mcp.tool()
def get_insights(level: str = "campaign", date_preset: str = "last_7d", campaign_id: str = None) -> list:
    """Metriche di performance (spesa, CPC, CTR, conversioni). Sola lettura, basso rischio.

    date_preset: es. today, yesterday, last_3d, last_7d, last_14d, last_30d.
    """
    return _get_insights(get_client(), level, date_preset, campaign_id)


@mcp.tool()
def create_campaign(name: str, objective: str, daily_budget_eur: float,
                     status: str = "PAUSED", confirm: bool = False) -> dict:
    """Crea una nuova campagna Meta. Senza confirm=True esegue solo un'anteprima (dry-run).
    Il budget e' validato contro META_MAX_DAILY_BUDGET_EUR."""
    return _create_campaign(get_client(), settings, name, objective, daily_budget_eur, status, confirm)


@mcp.tool()
def create_ad_set(campaign_id: str, name: str, daily_budget_eur: float, targeting: dict,
                   optimization_goal: str = "OFFSITE_CONVERSIONS", confirm: bool = False) -> dict:
    """Crea un ad set (pubblico, budget, evento di conversione). Senza confirm=True: solo anteprima."""
    return _create_ad_set(get_client(), settings, campaign_id, name, daily_budget_eur, targeting,
                           optimization_goal, confirm)


@mcp.tool()
def create_ad(adset_id: str, name: str, creative_id: str, confirm: bool = False) -> dict:
    """Crea un annuncio in un ad set esistente, a partire da una creative gia' esistente.
    Senza confirm=True: solo anteprima."""
    return _create_ad(get_client(), settings, adset_id, name, creative_id, confirm)


@mcp.tool()
def pause_campaign(campaign_id: str, confirm: bool = False) -> dict:
    """Mette in pausa una campagna. Azione distruttiva: richiede SEMPRE confirm=True esplicito."""
    return _pause_campaign(get_client(), campaign_id, confirm)


@mcp.tool()
def resume_campaign(campaign_id: str, confirm: bool = False) -> dict:
    """Riattiva una campagna in pausa. Richiede SEMPRE confirm=True esplicito."""
    return _resume_campaign(get_client(), campaign_id, confirm)


if __name__ == "__main__":
    mcp.run()
