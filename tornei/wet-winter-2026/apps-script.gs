// Google Apps Script: riceve le iscrizioni dal form e le salva nel Google Sheet collegato.
// Estensioni > Apps Script nel foglio, incolla questo file, poi
// Esegui il deployment > Nuovo deployment > App web (Esegui come: Me, Accesso: Chiunque).
// Copia l'URL /exec in assets/config.js.
var HEADERS = ["Data", "Nome", "Cognome", "Email", "Nick Parabellum", "LSID", "Lingua", "Evento"];

function doPost(e) {
  var lock = LockService.getScriptLock();
  lock.waitLock(10000);
  try {
    var sheet = SpreadsheetApp.getActiveSpreadsheet().getSheets()[0];
    if (sheet.getLastRow() === 0) sheet.appendRow(HEADERS);
    var p = e.parameter;
    sheet.appendRow([new Date(), p.nome, p.cognome, p.email, p.nick_parabellum, p.lsid, p.lingua, p.evento]);
    return ContentService.createTextOutput("ok");
  } finally {
    lock.releaseLock();
  }
}
