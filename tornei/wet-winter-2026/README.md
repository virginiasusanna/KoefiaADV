# The Ludic-Milan W.E.T. – Winter Edition (05/12/2026)

Sito statico che sostituisce le pagine MailerLite della Summer Edition.

- `index.html` – pagina di ingresso con scelta lingua
- `it/` – landing italiana (copiata dalla landing da 1 giorno della Summer)
- `en/` – landing inglese (stessa struttura, tradotta)
- `assets/` – immagini, stile, script del form

## Iscrizioni ed email
Le iscrizioni finiscono nel Google Sheet "Iscrizioni W.E.T. Winter Edition 2026"
(https://docs.google.com/spreadsheets/d/1zoPuFj_xHtQ3mVBvl8brGDfVTLcUud-ML_SHXWgx7uM/edit).
Lo script `apps-script.gs`, collegato al foglio:
- salva ogni iscrizione (segnala le email doppie nella colonna Note);
- manda al giocatore l'email di conferma in italiano o inglese, con il link PayPal e le scadenze;
- manda all'organizzazione una notifica con i dati e il numero di iscritti;
- aggiunge al foglio il menu "W.E.T." con "Promemoria pagamento" (a chi non ha la spunta Pagato)
  ed "Email a tutti gli iscritti…".

Installazione (una volta sola):
1. Apri il foglio > Estensioni > Apps Script, cancella il contenuto e incolla `apps-script.gs`, salva.
2. Esegui il deployment > Nuovo deployment > tipo "App web"; Esegui come: Me; Chi ha accesso: Chiunque.
   Autorizza le richieste di Google (foglio + invio email).
3. Copia l'URL `.../exec` in `assets/config.js` (`WET_FORM_ENDPOINT`).

Dopo l'invio il form mostra il pulsante PayPal (paypal.me/conquestludic), come su MailerLite.

## Pubblicazione (GitHub Pages)
Repository > Settings > Pages > Source "Deploy from a branch" > branch `claude/loving-euler-t0hagy`, cartella `/ (root)`.
Indirizzo: https://virginiasusanna.github.io/KoefiaADV/tornei/wet-winter-2026/

## Da completare
- `assets/hero.jpg` è ancora l'immagine della Summer: sostituirla con quella invernale.
- Link Longshanks: punta alla home di longshanks.org finché non c'è l'evento.
