"""Tool di SCRITTURA: crea un annuncio in un ad set esistente (richiede una
creative gia' esistente: creative_id)."""
from facebook_business.adobjects.ad import Ad

from shared.audit_log import log_action


def create_ad(client, settings, adset_id: str, name: str, creative_id: str,
               confirm: bool = False) -> dict:
    params = {
        Ad.Field.name: name,
        Ad.Field.adset_id: adset_id,
        Ad.Field.creative: {"creative_id": creative_id},
        Ad.Field.status: "PAUSED",
    }

    if settings.dry_run or not confirm:
        result = {
            "preview": True,
            "would_create": params,
            "note": "Dry-run o conferma mancante: nessuna chiamata reale effettuata.",
        }
        log_action("meta", "create_ad", params, result, dry_run=True)
        return result

    ad = client.account.create_ad(params=params)
    result = dict(ad)
    log_action("meta", "create_ad", params, result, dry_run=False)
    return result
