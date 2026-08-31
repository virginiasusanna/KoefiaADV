"""MCP server per TikTok Ads. Entry point.

Avvio: python server.py  (richiede .env compilato, vedi .env.example)
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))  # per importare shared/

from dotenv import load_dotenv
load_dotenv()

from mcp.server.fastmcp import FastMCP

from tiktok_client import TikTokClient
from shared.config import Settings

from tools.list_campaigns import list_campaigns as _list_campaigns
from tools.get_insights import get_insights as _get_insights
from tools.check_pixel import check_pixel_status as _check_pixel_status, get_pixel_events as _get_pixel_events
from tools.create_campaign import create_campaign as _create_campaign
from tools.pause_resume import pause_campaign as _pause_campaign, resume_campaign as _resume_campaign

mcp = FastMCP("tiktok-ads")
settings = Settings(prefix="TIKTOK")
_client = None


def get_client() -> TikTokClient:
    global _client
    if _client is None:
        _client = TikTokClient()
    return _client


@mcp.tool()
def list_campaigns(page_size: int = 50) -> list:
    """Elenca le campagne TikTok Ads esistenti. Sola lettura, basso rischio."""
    return _list_campaigns(get_client(), page_size)


@mcp.tool()
def get_insights(start_date: str, end_date: str, campaign_ids: list = None) -> list:
    """Metriche di performance (spesa, CPC, conversioni) tra due date (YYYY-MM-DD).
    Sola lettura, basso rischio."""
    return _get_insights(get_client(), start_date, end_date, campaign_ids)


@mcp.tool()
def check_pixel_status(pixel_code: str = None) -> list:
    """Elenca i pixel TikTok configurati sull'advertiser e il loro stato.
    Utile per diagnosticare problemi di tracciamento/visibilita'."""
    return _check_pixel_status(get_client(), pixel_code)


@mcp.tool()
def get_pixel_events(pixel_code: str, start_date: str, end_date: str) -> dict:
    """Statistiche eventi ricevuti da un pixel tra due date (YYYY-MM-DD)."""
    return _get_pixel_events(get_client(), pixel_code, start_date, end_date)


@mcp.tool()
def create_campaign(name: str, objective: str, daily_budget_eur: float, confirm: bool = False) -> dict:
    """Crea una campagna TikTok (disabilitata di default). Senza confirm=True: solo anteprima.
    Il budget e' validato contro TIKTOK_MAX_DAILY_BUDGET_EUR."""
    return _create_campaign(get_client(), settings, name, objective, daily_budget_eur, confirm)


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
