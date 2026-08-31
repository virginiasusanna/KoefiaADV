# Koefia ADV — gestione campagne Meta / Google / TikTok

Sistema per monitorare e (in futuro) gestire via codice le campagne Ads
dell'Open Day Koefia (12 settembre 2026), invece di passare dalle interfacce
web. Basato su [brief_integrazione_ads.md] originale.

## Stato attuale (aggiornato 31/08/2026)

- Landing page live: accademiakoefia.com/open-day
- Campagne Meta e Google create manualmente e live dal 29/08
- Campagna TikTok live (problema iniziale di visibilita' pixel risolto dall'utente)
- **Priorita' attuale: monitoraggio, non creazione** — le campagne esistono gia',
  i tool di scrittura (`create_campaign` ecc.) sono pronti ma non servono ora.

**Ultimo check HubSpot (31/08, via MCP in sessione Claude):** 3 lead reali
arrivati dal 29/08 (2 da Meta Paid Social, 1 da bio Instagram organica),
**nessuno ancora lavorato** (0 note/attivita' su tutti e 3). Non risulta
nessun lead attribuito a Google o TikTok in questa finestra — da tenere
d'occhio quando avremo i numeri di spesa reali.

**Limite noto:** il modulo Marketing Campaigns / Attribution reporting di
HubSpot non e' accessibile con i permessi correnti dell'integrazione in
questo portale (`get_campaign_attribution_reports` -> Not Authorized,
oggetto `CAMPAIGN` -> `REQUIRES_ACCOUNT_MODIFICATION`). Va verificato/abilitato
lato HubSpot se si vuole quel livello di dati.

## Architettura

```
/mcp-meta-ads/       server MCP Meta Ads (facebook-business SDK)
/mcp-google-ads/      server MCP Google Ads (google-ads SDK)
/mcp-tiktok-ads/      server MCP TikTok Ads (REST diretto)
/shared/              config, budget guard, audit log, client HubSpot condivisi
/scripts/status_report.py   report aggregato spesa/pacing/CTR + lead HubSpot
/logs/                 audit log JSONL di ogni azione di scrittura (per piattaforma)
```

Un server per piattaforma (non monolitico), come da brief originale — piu'
semplice da testare/debuggare/versionare singolarmente. Il modulo `shared/`
contiene solo utility comuni (config, guardrail, log), non logica business.

## Modello di sicurezza

Per ogni piattaforma, ogni tool di **scrittura** (create_campaign,
create_ad_set, create_ad, pause_campaign, resume_campaign):

1. **Dry-run di default** (`*_DRY_RUN=true`): calcola il payload che
   verrebbe inviato ma non chiama mai l'API reale.
2. **Conferma esplicita richiesta** (`confirm=True`): senza, ritorna solo
   un'anteprima, anche se `DRY_RUN=false`. `pause_campaign`/`resume_campaign`
   la richiedono **sempre**, a prescindere da `DRY_RUN`.
3. **Tetto di budget hard-coded** (`*_MAX_DAILY_BUDGET_EUR`, default 50€):
   qualunque budget superiore fa fallire la chiamata con `BudgetExceeded`.
4. **Log di audit** append-only in `logs/<piattaforma>_audit.jsonl`: ogni
   azione (anche in dry-run) viene registrata con timestamp e parametri.

I tool di **lettura** (list_campaigns, get_insights, check_pixel_status)
non hanno questi vincoli: sono a basso rischio.

## Cosa serve fare TU (non posso farlo io)

Queste azioni richiedono login/identita' del titolare dell'account — non
posso completarle al posto tuo. Appena hai i valori, compilali in `.env`
(copia `.env.example`) e i tool iniziano a funzionare.

### Meta
1. Crea un'app Business su developers.facebook.com
2. Ottieni App ID + App Secret
3. Genera un System User Access Token con permesso `ads_management`
4. Sottometti l'app ad **App Review** per lo scope `ads_management`
   (piu' lento — giorni, non bypassabile)

### Google Ads
1. Attiva Google Ads API su console.cloud.google.com, crea OAuth Client ID + Secret
2. Richiedi il Developer Token (Google Ads → Strumenti → Centro API — livello
   "Test" e' immediato, "Standard/Basic" richiede approvazione)
3. Genera un refresh token (flow OAuth una tantum — chiedimi aiuto quando
   sei a questo punto, ti preparo lo script)

### TikTok
1. Accesso Developer su business-api.tiktok.com/portal
2. Access Token con permessi campaign management (Advertiser ID gia' noto)

### HubSpot (per lo status report automatico)
1. Impostazioni → Integrazioni → App private → crea un'app con scope
   `crm.objects.contacts.read`
2. Copia il token in `HUBSPOT_PRIVATE_APP_TOKEN`

## Uso

```bash
pip install -r requirements.txt
cp .env.example .env   # poi compila i valori che hai

# Report aggregato (salta le piattaforme senza credenziali)
python scripts/status_report.py --days 7

# Avvio di un singolo server MCP (per collegarlo a Claude Desktop/altro client MCP)
cd mcp-meta-ads && pip install -r requirements.txt && python server.py
```

## Limiti noti

- `mcp-google-ads/tools/create_campaign.py` copre solo campagne Search
  generiche; Performance Max richiede asset group con requisiti aggiuntivi
  non ancora implementati.
- Il codice non e' stato testato contro API reali (nessuna credenziale
  disponibile al momento della scrittura) — testare prima su un account/budget
  minimo, come raccomandato nel brief originale.
