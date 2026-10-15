# The Ludic-Milan W.E.T. – Winter Edition (05/12/2026)

Sito statico che sostituisce le pagine MailerLite della Summer Edition.

- `index.html` – pagina di ingresso con scelta lingua
- `it/` – landing italiana (copiata dalla landing da 1 giorno della Summer)
- `en/` – landing inglese (stessa struttura, tradotta)
- `assets/` – immagini, stile, script del form

## Iscrizioni
Il form invia i dati a una Web App Google Apps Script che li scrive in un Google Sheet:
1. Crea un Google Sheet "Iscrizioni WET Winter 2026".
2. Estensioni > Apps Script, incolla `apps-script.gs`, salva.
3. Esegui il deployment > Nuovo deployment > App web (Esegui come: Me, Chi ha accesso: Chiunque).
4. Incolla l'URL `.../exec` in `assets/config.js` (`WET_FORM_ENDPOINT`).

Dopo l'invio il form mostra il pulsante PayPal (paypal.me/conquestludic), come su MailerLite.

## Pubblicazione
Qualsiasi hosting statico (GitHub Pages, Netlify, ecc.): basta caricare questa cartella.

## Da completare
- `assets/hero.jpg` è ancora l'immagine della Summer: sostituirla con quella invernale.
- Link Longshanks: punta alla home di longshanks.org finché non c'è l'evento.
