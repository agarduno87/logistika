/*
  logistika — i18n.js

  Motor de idiomas. Dos decisiones que evitan errores al ejecutar en local:

  1) Los diccionarios se cargan como <script src="i18n/<code>.js">, NO por fetch de
     JSON. Un fetch de archivo local se bloquea al abrir la página con file://
     (origen 'null'), y ese es exactamente el escenario en el que uno prueba primero.
     Con script tags funciona igual por http:// y por file://.
  2) Cada idioma declara su moneda. La calculadora de costo se recalcula en la moneda
     del idioma activo: inglés en USD, español en pesos mexicanos.

  Sobre la moneda: NO se convierte con un tipo de cambio. Cada moneda trae su propio
  rango de costo por hora, porque el dato que el visitante conoce es lo que le cuesta
  una hora de su gente en SU moneda. Un tipo de cambio fijo se vuelve mentira en un
  mes, y uno en vivo exigiría llamar a una API de terceros, que rompería la CSP.

  Agregar un idioma:
    1. cp i18n/_template.js i18n/<code>.js  y traduce los valores.
    2. Agrega una entrada a LOCALES aquí abajo (con su moneda).
    3. Agrega el <link rel="alternate" hreflang> en index.html.
  Ningún otro archivo se toca.
*/
(function () {
  "use strict";

  var LOCALES = [
    {
      code: "en", label: "English", dir: "ltr",
      currency: { code: "USD", intl: "en-US", min: 5, max: 120, step: 1, value: 25 }
    },
    {
      code: "es", label: "Español", dir: "ltr",
      currency: { code: "MXN", intl: "es-MX", min: 100, max: 2000, step: 25, value: 400 }
    }
    /* Ejemplo para el siguiente:
       { code:"pt-BR", label:"Português (BR)", dir:"ltr",
         currency:{ code:"BRL", intl:"pt-BR", min:30, max:600, step:5, value:120 } }
       Y para RTL basta con dir:"rtl": el CSS ya está escrito. */
  ];

  var SOURCE = "en";
  var dictionaries = {};   // code -> objeto de traducción (común + página, ya fusionados)
  var loaded = {};         // code -> true cuando ya se cargaron todos sus archivos
  var source = null;       // textos originales tomados del HTML
  var current = SOURCE;
  var select = document.getElementById("langSelect");

  /* Las páginas de servicio viven en /services/<slug>/, así que las rutas relativas
     no sirven: los diccionarios se piden con ruta absoluta. La excepción es file://,
     donde no hay raíz de sitio y hay que volver a relativo. */
  var BASE = window.location.protocol === "file:" ? "i18n/" : "/i18n/";

  /* Cada página declara su diccionario propio con data-i18n-page en <html>.
     La portada no lo declara: le basta el común. */
  var PAGE = document.documentElement.getAttribute("data-i18n-page") || "";

  function meta(code) {
    for (var i = 0; i < LOCALES.length; i++) {
      if (LOCALES[i].code === code) { return LOCALES[i]; }
    }
    return LOCALES[0];
  }

  /* Los archivos i18n/<code>.js y i18n/<page>.<code>.js llaman a esta función.
     Se FUSIONA en vez de reemplazar: primero entra el diccionario común y luego
     el de la página, que puede sobrescribir claves si hace falta. */
  window.ttsRegisterDictionary = function (code, dict) {
    if (typeof code !== "string" || !dict || typeof dict !== "object") { return; }
    var target = dictionaries[code] || (dictionaries[code] = {});
    for (var key in dict) {
      if (Object.prototype.hasOwnProperty.call(dict, key)) { target[key] = dict[key]; }
    }
    /* Si el diccionario ya está en memoria no hay que ir a buscarlo otra vez.
       Sin esto, un diccionario precargado se volvía a pedir por red y, cuando
       esa petición fallaba, el idioma no se aplicaba aunque estuviera cargado. */
    loaded[code] = true;
  };

  /* ------------------------------------------------------------------
     Inglés: se toma del propio HTML, no necesita archivo
     ------------------------------------------------------------------ */
  function snapshot() {
    var dict = {};
    var i, nodes;

    nodes = document.querySelectorAll("[data-i18n]");
    for (i = 0; i < nodes.length; i++) {
      dict[nodes[i].getAttribute("data-i18n")] = nodes[i].textContent;
    }
    nodes = document.querySelectorAll("[data-i18n-ph]");
    for (i = 0; i < nodes.length; i++) {
      dict[nodes[i].getAttribute("data-i18n-ph")] = nodes[i].placeholder;
    }
    nodes = document.querySelectorAll("[data-i18n-alt]");
    for (i = 0; i < nodes.length; i++) {
      dict[nodes[i].getAttribute("data-i18n-alt")] = nodes[i].alt;
    }

    /* Cadenas que no viven en el DOM (mensajes en tiempo de ejecución). */
    dict["menu.open"] = "Open menu";
    dict["menu.close"] = "Close menu";
    dict["form.sending"] = "Sending…";
    dict["msg.sending"] = "Sending your message…";
    dict["msg.sent"] = "Message sent. You will get a written reply within one business day.";
    dict["msg.thanks"] = "Thanks — we will be in touch.";
    dict["msg.tooFast"] = "Take a moment to describe your operation, then send.";
    dict["msg.company"] = "Add your company name.";
    dict["msg.email"] = "Add a valid work email address.";
    dict["msg.message"] = "Describe your operation in a line or two.";
    dict["msg.rate"] = "Too many messages from this connection. Try again in an hour.";
    dict["msg.invalid"] = "Check the company, email and description fields.";
    dict["msg.error"] = "The message could not be sent right now. Please try again in a few minutes.";
    dict["msg.connection"] = "Connection problem — the message was not sent. Please try again.";
    dict["msg.fileProtocol"] = "Open the site over http:// to send the form. Run ./run.sh and use http://127.0.0.1:8000";
    return dict;
  }

  function t(key, fallback) {
    var dict = dictionaries[current];
    if (dict && typeof dict[key] === "string" && dict[key] !== "") { return dict[key]; }
    if (source && typeof source[key] === "string") { return source[key]; }
    return typeof fallback === "string" ? fallback : key;
  }

  window.ttsI18n = {
    t: t,
    locales: LOCALES,
    get current() { return current; },
    get currency() { return meta(current).currency; }
  };

  /* ------------------------------------------------------------------
     Aplicar
     ------------------------------------------------------------------ */
  function apply(code) {
    var dict = code === SOURCE ? source : dictionaries[code];
    if (!dict) { return; }

    var i, nodes, value;

    nodes = document.querySelectorAll("[data-i18n]");
    for (i = 0; i < nodes.length; i++) {
      value = dict[nodes[i].getAttribute("data-i18n")];
      /* Siempre textContent: ninguna cadena traducida puede inyectar marcado. */
      if (typeof value === "string" && value !== "") { nodes[i].textContent = value; }
    }
    nodes = document.querySelectorAll("[data-i18n-ph]");
    for (i = 0; i < nodes.length; i++) {
      value = dict[nodes[i].getAttribute("data-i18n-ph")];
      if (typeof value === "string" && value !== "") { nodes[i].placeholder = value; }
    }
    /* El texto alternativo también se traduce: es lo que oye quien usa lector
       de pantalla, y lo que lee un buscador cuando la imagen no carga. */
    nodes = document.querySelectorAll("[data-i18n-alt]");
    for (i = 0; i < nodes.length; i++) {
      value = dict[nodes[i].getAttribute("data-i18n-alt")];
      if (typeof value === "string" && value !== "") { nodes[i].alt = value; }
    }

    var info = meta(code);
    document.documentElement.lang = code;
    document.documentElement.dir = info.dir === "rtl" ? "rtl" : "ltr";
    current = code;

    /* Re-etiquetar el botón del menú según su estado actual. */
    var burger = document.getElementById("burger");
    if (burger) {
      var open = burger.getAttribute("aria-expanded") === "true";
      burger.setAttribute("aria-label", t(open ? "menu.close" : "menu.open", "Menu"));
    }

    /* Reflejar el idioma en la URL: compartible y marcable, sin cookies. */
    try {
      var url = new URL(window.location.href);
      if (code === SOURCE) { url.searchParams.delete("lang"); }
      else { url.searchParams.set("lang", code); }
      window.history.replaceState(null, "", url.toString());
    } catch (e) { /* file:// no siempre lo permite; no es crítico */ }

    /* Por si alguna parte del sitio necesita reaccionar al cambio de idioma. */
    document.dispatchEvent(new CustomEvent("logistika:locale", { detail: { code: code } }));
  }

  /* ------------------------------------------------------------------
     Carga del diccionario por <script>
     ------------------------------------------------------------------ */
  function loadScript(src, done) {
    var script = document.createElement("script");
    script.src = src;
    script.async = false;                 // preserva el orden: común antes que página
    script.onload = function () { done(true); };
    script.onerror = function () { done(false); };
    document.head.appendChild(script);
  }

  function load(code) {
    if (code === SOURCE || loaded[code]) {
      apply(code);
      return;
    }
    var files = [BASE + encodeURIComponent(code) + ".js"];
    if (PAGE) {
      files.push(BASE + encodeURIComponent(PAGE) + "." + encodeURIComponent(code) + ".js");
    }

    var pending = files.length;
    var anyFailed = false;

    files.forEach(function (src) {
      loadScript(src, function (ok) {
        if (!ok) { anyFailed = true; }
        pending -= 1;
        if (pending > 0) { return; }
        if (dictionaries[code]) {
          loaded[code] = true;
          apply(code);
          if (anyFailed) { revert("partial dictionary for " + code + " — missing page file"); }
        } else {
          revert("dictionary not found: " + code);
        }
      });
    });
  }

  function revert(reason) {
    /* Si un idioma (o parte de él) falla, el sitio se queda legible en el idioma
       actual en vez de romperse o mostrar claves crudas. Las claves que sí
       cargaron se aplican; las que no, caen al inglés del HTML. */
    if (window.console && console.warn) { console.warn("[i18n] " + reason); }
    if (select) { select.value = current; }
  }

  /* ------------------------------------------------------------------
     Arranque
     ------------------------------------------------------------------ */
  source = snapshot();

  if (select) {
    for (var i = 0; i < LOCALES.length; i++) {
      var option = document.createElement("option");
      option.value = LOCALES[i].code;
      option.textContent = LOCALES[i].label;
      select.appendChild(option);
    }
    select.hidden = false;
    select.addEventListener("change", function (event) { load(event.target.value); });
  }

  /* Idioma inicial: ?lang= → idioma del navegador → inglés. */
  var requested = "";
  try {
    requested = new URL(window.location.href).searchParams.get("lang") || "";
  } catch (e) { requested = ""; }

  var supported = LOCALES.map(function (l) { return l.code; });
  var initial = SOURCE;

  if (supported.indexOf(requested) !== -1) {
    initial = requested;
  } else if (navigator.language) {
    if (supported.indexOf(navigator.language) !== -1) {
      initial = navigator.language;
    } else {
      var base = navigator.language.split("-")[0];
      for (var j = 0; j < supported.length; j++) {
        if (supported[j].split("-")[0] === base) { initial = supported[j]; break; }
      }
    }
  }

  if (select) { select.value = initial; }
  if (initial !== SOURCE) { load(initial); }
  else {
    /* Aun en inglés, avisar a app.js cuál es la moneda inicial. */
    document.dispatchEvent(new CustomEvent("tts:locale", {
      detail: { code: SOURCE, currency: meta(SOURCE).currency }
    }));
  }
})();
