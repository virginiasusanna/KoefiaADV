"""Piano della campagna Open Day Koefia (12 settembre 2026), cosi' come
riepilogato dall'utente. Usato dallo status_report per calcolare il pacing
(spesa attesa vs spesa reale) per fase e per canale.

Se il piano cambia, aggiornare qui: e' l'unica fonte di verita' per i calcoli
di pacing.
"""
from datetime import date

EVENT_DATE = date(2026, 9, 12)

PHASES = [
    {"name": "Pre-lancio", "start": date(2026, 8, 27), "end": date(2026, 8, 28)},
    {"name": "Fase 1-2 Lead Gen", "start": date(2026, 8, 29), "end": date(2026, 9, 9)},
    {"name": "Fase 3 Retargeting", "start": date(2026, 9, 10), "end": date(2026, 9, 12)},
]

# Budget totale per canale nell'intera campagna (in EUR), e come si ripartisce
# tra le fasi in cui il canale e' effettivamente attivo.
CHANNEL_PLAN = {
    "meta": {
        "total_eur": 1000,
        "phases": {
            "Fase 1-2 Lead Gen": 650,
            "Fase 3 Retargeting": 350,
        },
    },
    "google": {
        "total_eur": 700,
        "phases": {
            "Fase 1-2 Lead Gen": 550,
            "Fase 3 Retargeting": 150,
        },
    },
    "tiktok": {
        "total_eur": 300,
        "phases": {
            "Fase 1-2 Lead Gen": 300,
            # Nessuna fase di retargeting per TikTok: budget/tempo insufficienti.
        },
    },
}


def current_phase(today: date = None):
    today = today or date.today()
    for phase in PHASES:
        if phase["start"] <= today <= phase["end"]:
            return phase
    return None


def expected_spend_to_date(channel: str, today: date = None) -> float:
    """Spesa attesa cumulata fino a oggi per un canale, assumendo delivery
    lineare all'interno di ogni fase attiva. E' una stima, non un vincolo."""
    today = today or date.today()
    plan = CHANNEL_PLAN[channel]["phases"]
    expected = 0.0
    for phase in PHASES:
        phase_budget = plan.get(phase["name"])
        if phase_budget is None:
            continue
        if today < phase["start"]:
            continue
        phase_days = (phase["end"] - phase["start"]).days + 1
        elapsed_days = min((today - phase["start"]).days + 1, phase_days)
        expected += phase_budget * (elapsed_days / phase_days)
    return round(expected, 2)
