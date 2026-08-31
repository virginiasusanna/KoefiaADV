"""Guardia di sicurezza sul budget: nessuna chiamata di scrittura puo' impostare
un budget superiore al tetto configurato, indipendentemente da cosa viene
richiesto nel prompt."""


class BudgetExceeded(Exception):
    pass


def check_budget(amount_eur: float, cap_eur: float, label: str = "budget") -> None:
    if amount_eur > cap_eur:
        raise BudgetExceeded(
            f"{label} di {amount_eur:.2f}EUR supera il tetto di sicurezza di "
            f"{cap_eur:.2f}EUR configurato nel .env. Se e' voluto, alza la variabile "
            f"*_MAX_DAILY_BUDGET_EUR corrispondente."
        )
