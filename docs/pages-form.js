/* GitHub Pages no tiene backend: el formulario se envia por correo.
   Esto lo inyecta tools/build_pages.py y NO existe en la version de servidor. */
(function () {
  var f = document.getElementById("form");
  if (!f) { return; }
  var st = document.getElementById("st");
  var MAIL = "hola@logistika.mx";

  f.addEventListener("submit", function (e) {
    e.preventDefault();
    e.stopImmediatePropagation();

    var trap = f.elements.website;
    if (trap && trap.value !== "") { return; }
    if (!f.checkValidity()) { f.reportValidity(); return; }

    var get = function (n) { return f.elements[n] ? f.elements[n].value.trim() : ""; };
    var lines = [];
    ["company", "email", "stage", "practice", "message"].forEach(function (n) {
      var v = get(n);
      if (v) { lines.push(n.toUpperCase() + ": " + v); }
    });

    var subject = encodeURIComponent("Website enquiry - " + (get("company") || "new contact"));
    var body = encodeURIComponent(lines.join("\n\n"));
    window.location.href = "mailto:" + MAIL + "?subject=" + subject + "&body=" + body;

    if (st) {
      st.textContent = st.getAttribute("data-mail-note") ||
        "Opening your email app. If nothing happens, write to " + MAIL;
    }
  }, true);
})();
