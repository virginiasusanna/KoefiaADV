(function () {
  var form = document.querySelector("form.reg");
  if (!form) return;
  var err = document.getElementById("form-err");
  var ok = document.getElementById("form-ok");
  var pay = document.querySelector(".paypal-box");
  form.addEventListener("submit", function (e) {
    e.preventDefault();
    err.style.display = "none";
    if (!form.reportValidity()) return;
    var endpoint = window.WET_FORM_ENDPOINT;
    if (!endpoint) { err.style.display = "block"; return; }
    var btn = form.querySelector("button");
    btn.disabled = true;
    var data = new URLSearchParams(new FormData(form));
    data.append("lingua", document.documentElement.lang);
    data.append("evento", "WET Winter 2026");
    fetch(endpoint, { method: "POST", mode: "no-cors", body: data })
      .then(function () {
        form.style.display = "none";
        ok.style.display = "block";
        pay.classList.add("show");
      })
      .catch(function () { err.style.display = "block"; btn.disabled = false; });
  });
})();
