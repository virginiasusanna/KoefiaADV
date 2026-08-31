"""Configurazione condivisa (safety settings) per i server MCP di gestione Ads.

Ogni server la istanzia con il proprio prefisso (META / GOOGLE / TIKTOK) cosi'
i tetti di sicurezza sono indipendenti per piattaforma.
"""
import os


def _bool_env(name: str, default: bool) -> bool:
    val = os.getenv(name)
    if val is None:
        return default
    return val.strip().lower() in ("1", "true", "yes", "on")


class Settings:
    def __init__(self, prefix: str):
        self.prefix = prefix
        # Di default in dry-run: le tool di scrittura calcolano il payload
        # ma non chiamano mai l'API reale finche' non viene impostato esplicitamente
        # <PREFIX>_DRY_RUN=false nel .env.
        self.dry_run = _bool_env(f"{prefix}_DRY_RUN", True)
        self.max_daily_budget_eur = float(os.getenv(f"{prefix}_MAX_DAILY_BUDGET_EUR", "50"))
        self.max_lifetime_budget_eur = float(os.getenv(f"{prefix}_MAX_LIFETIME_BUDGET_EUR", "500"))
