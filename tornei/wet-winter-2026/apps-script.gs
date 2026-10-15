// The Ludic-Milan W.E.T. Winter Edition – iscrizioni ed email.
// Installazione: nel Google Sheet delle iscrizioni, Estensioni > Apps Script, incolla questo file,
// salva, poi Esegui il deployment > Nuovo deployment > App web
// (Esegui come: Me, Chi ha accesso: Chiunque) e copia l'URL /exec in assets/config.js.
// Le email partono dall'account Google di chi fa il deployment (es. nicolo.olivieri9@gmail.com):
// il deployment va fatto da quell'account. Limite Gmail gratuito: 100 destinatari al giorno.

var EVENTO = "The Ludic-Milan W.E.T. Winter Edition";
var MITTENTE = "Ludic Milan";
var PAYPAL = "https://paypal.me/conquestludic";
// Chi riceve la notifica di ogni nuova iscrizione, oltre all'account che invia (separa con virgole).
var ALTRE_NOTIFICHE = "";
var HEADERS = ["Data", "Nome", "Cognome", "Email", "Nick Parabellum", "LSID", "Lingua", "Pagato", "Note"];
var COL = { nome: 2, email: 4, lingua: 7, pagato: 8 };

var TESTI = {
  it: {
    oggetto: "Iscrizione ricevuta – " + EVENTO,
    corpo: function (nome) {
      return "Ciao " + nome + ",\n\n" +
        "abbiamo ricevuto la tua iscrizione a " + EVENTO + ", sabato 5 dicembre 2026 alla Casa dei Giochi " +
        "(Via Sant'Uguzzone 8, Milano).\n\n" +
        "L'iscrizione è valida solo dopo il pagamento: 20€ entro il 15 novembre, 25€ entro il 25 novembre.\n" +
        "Paga qui: " + PAYPAL + "\n\n" +
        "Ricorda di caricare la lista su Longshanks entro il 28 novembre.\n\n" +
        "A presto!\n" + MITTENTE;
    }
  },
  en: {
    oggetto: "Registration received – " + EVENTO,
    corpo: function (nome) {
      return "Hi " + nome + ",\n\n" +
        "we have received your registration for " + EVENTO + ", Saturday 5 December 2026 at Casa dei Giochi " +
        "(Via Sant'Uguzzone 8, Milan).\n\n" +
        "Your registration is confirmed only after payment: €20 by November 15th, €25 by November 25th.\n" +
        "Pay here: " + PAYPAL + "\n\n" +
        "Remember to upload your army list to Longshanks by November 28th.\n\n" +
        "See you soon!\n" + MITTENTE;
    }
  }
};

function foglio_() {
  var sheet = SpreadsheetApp.getActiveSpreadsheet().getSheets()[0];
  if (sheet.getLastRow() === 0) {
    sheet.appendRow(HEADERS);
    sheet.setFrozenRows(1);
    sheet.getRange(1, 1, 1, HEADERS.length).setFontWeight("bold");
  }
  return sheet;
}

function doPost(e) {
  var p = e.parameter;
  var lingua = p.lingua === "en" ? "en" : "it";
  var lock = LockService.getScriptLock();
  lock.waitLock(10000);
  try {
    var sheet = foglio_();
    var emails = sheet.getLastRow() > 1
      ? sheet.getRange(2, COL.email, sheet.getLastRow() - 1, 1).getValues().map(function (r) { return String(r[0]).toLowerCase(); })
      : [];
    var nota = emails.indexOf(String(p.email).toLowerCase()) >= 0 ? "Email già presente" : "";
    sheet.appendRow([new Date(), p.nome, p.cognome, p.email, p.nick_parabellum, p.lsid, lingua, false, nota]);
    sheet.getRange(sheet.getLastRow(), COL.pagato).insertCheckboxes();
  } finally {
    lock.releaseLock();
  }

  var t = TESTI[lingua];
  MailApp.sendEmail({ to: p.email, subject: t.oggetto, body: t.corpo(p.nome), name: MITTENTE });
  MailApp.sendEmail({
    to: [Session.getEffectiveUser().getEmail(), ALTRE_NOTIFICHE].filter(String).join(","),
    subject: "Nuova iscrizione W.E.T. Winter: " + p.nome + " " + p.cognome,
    body: "Nome: " + p.nome + " " + p.cognome + "\nEmail: " + p.email + "\nNick Parabellum: " + p.nick_parabellum +
      "\nLSID: " + p.lsid + "\nLingua: " + lingua + "\n\nIscritti totali: " + (foglio_().getLastRow() - 1) +
      "\n" + SpreadsheetApp.getActiveSpreadsheet().getUrl(),
    name: MITTENTE
  });
  return ContentService.createTextOutput("ok");
}

// Menu nel foglio per gli invii di massa.
function onOpen() {
  SpreadsheetApp.getUi().createMenu("W.E.T.")
    .addItem("Promemoria pagamento (chi non ha pagato)", "promemoriaPagamento")
    .addItem("Email a tutti gli iscritti…", "emailATutti")
    .addToUi();
}

function iscritti_(soloNonPagati) {
  var sheet = foglio_();
  if (sheet.getLastRow() < 2) return [];
  return sheet.getRange(2, 1, sheet.getLastRow() - 1, HEADERS.length).getValues()
    .filter(function (r) { return r[COL.email - 1] && !(soloNonPagati && r[COL.pagato - 1] === true); })
    .map(function (r) { return { nome: r[COL.nome - 1], email: r[COL.email - 1], lingua: r[COL.lingua - 1] }; });
}

function promemoriaPagamento() {
  var lista = iscritti_(true);
  lista.forEach(function (i) {
    var en = i.lingua === "en";
    MailApp.sendEmail({
      to: i.email,
      name: MITTENTE,
      subject: (en ? "Payment reminder – " : "Promemoria pagamento – ") + EVENTO,
      body: en
        ? "Hi " + i.nome + ",\n\nwe haven't received your payment yet. Only paid players are registered (deadline November 25th).\nPay here: " + PAYPAL + "\n\n" + MITTENTE
        : "Ciao " + i.nome + ",\n\nnon ci risulta ancora il tuo pagamento. Sono considerati iscritti solo i giocatori che hanno pagato (scadenza 25 novembre).\nPaga qui: " + PAYPAL + "\n\n" + MITTENTE
    });
  });
  SpreadsheetApp.getUi().alert("Promemoria inviati: " + lista.length);
}

function emailATutti() {
  var ui = SpreadsheetApp.getUi();
  var oggetto = ui.prompt("Oggetto dell'email").getResponseText();
  if (!oggetto) return;
  var testo = ui.prompt("Testo dell'email ({nome} viene sostituito col nome)").getResponseText();
  if (!testo) return;
  var lista = iscritti_(false);
  if (ui.alert("Inviare a " + lista.length + " iscritti?", ui.ButtonSet.YES_NO) !== ui.Button.YES) return;
  lista.forEach(function (i) {
    MailApp.sendEmail({ to: i.email, name: MITTENTE, subject: oggetto, body: testo.replace(/\{nome\}/g, i.nome) });
  });
  ui.alert("Email inviate: " + lista.length);
}
