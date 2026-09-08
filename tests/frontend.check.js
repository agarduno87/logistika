/*
  Pruebas del front en un DOM real (jsdom).

      npm install jsdom
      node tests/frontend.check.js

  Comprueba lo que el backend no puede ver: que el riel del recorrido se arma,
  que el selector de idioma traduce la página entera, que el formulario valida
  antes de mandar nada y que el menú responde al teclado.
*/
const fs = require("fs");
const path = require("path");
let JSDOM;
try { ({ JSDOM } = require("jsdom")); }
catch (e) { console.error("Falta jsdom.  npm install jsdom"); process.exit(1); }

const ROOT = path.resolve(__dirname, "..");
const ok = [], bad = [];
const check = (name, cond, extra = "") => (cond ? ok : bad).push(name + (extra ? " -> " + extra : ""));

function load(file, page) {
  let html = fs.readFileSync(path.join(ROOT, file), "utf8");
  // jsdom no resuelve /rutas absolutas desde el disco: se cargan a mano
  html = html.replace(/<script src="\/(i18n|app)\.js" defer><\/script>/g, "");
  const dom = new JSDOM(html, { runScripts: "dangerously", pretendToBeVisual: true, url: "http://localhost/" });
  const { window } = dom;
  window.eval(fs.readFileSync(path.join(ROOT, "i18n.js"), "utf8"));
  window.eval(fs.readFileSync(path.join(ROOT, "i18n", "es.js"), "utf8"));
  if (page) window.eval(fs.readFileSync(path.join(ROOT, "i18n", page), "utf8"));
  window.eval(fs.readFileSync(path.join(ROOT, "app.js"), "utf8"));
  return dom;
}

// ---------- portada ----------
{
  const { window } = load("index.html");
  const d = window.document;

  check("no-js se retira al correr JS", !d.body.classList.contains("no-js"));
  check("año pintado en el pie", /^\d{4}$/.test(d.getElementById("yr").textContent));
  check("siete etapas del recorrido", d.querySelectorAll("[data-stage]").length === 7,
        String(d.querySelectorAll("[data-stage]").length));
  check("marcas del riel generadas", d.querySelectorAll(".railstop").length === 7,
        String(d.querySelectorAll(".railstop").length));
  check("panel del diagnóstico es el ámbar", d.querySelectorAll(".split .a").length === 1);
  check("logo enlazado como archivo", /logistika-logo\.png/.test(d.querySelector("header img").getAttribute("src")));

  // menú
  const burger = d.getElementById("burger"), nav = d.getElementById("nav");
  burger.dispatchEvent(new window.MouseEvent("click"));
  check("menú abre", burger.getAttribute("aria-expanded") === "true");
  d.dispatchEvent(new window.KeyboardEvent("keydown", { key: "Escape" }));
  check("Escape cierra el menú", burger.getAttribute("aria-expanded") === "false");

  // idioma
  const sel = d.getElementById("langSelect");
  check("selector de idioma poblado", sel && sel.options.length === 2,
        sel ? String(sel.options.length) : "ausente");
  sel.value = "es";
  sel.dispatchEvent(new window.Event("change"));
  check("html lang cambia a es", d.documentElement.lang === "es", d.documentElement.lang);
  const h1 = d.querySelector("h1").textContent;
  check("h1 traducido", /Sigue tu carga/.test(h1), h1.slice(0, 40));
  check("etapa traducida", /Etapa 01/.test(d.querySelector(".stagenum").textContent));
  check("placeholder traducido", /Tu empresa/.test(d.querySelector('[name="company"]').placeholder));
  const untranslated = [...d.querySelectorAll("[data-i18n]")]
    .filter(el => /^(Supplier and purchase|Three levels|Who does the work|Questions)$/.test(el.textContent.trim()));
  check("no quedan cadenas en inglés", untranslated.length === 0,
        untranslated.map(e => e.textContent.trim()).join(" | "));

  // formulario
  const form = d.getElementById("form"), st = d.getElementById("st"), ts = d.getElementById("ts");
  ts.value = String(Date.now());
  form.dispatchEvent(new window.Event("submit", { cancelable: true, bubbles: true }));
  check("trampa de tiempo activa", /Tómate un momento/.test(st.textContent), st.textContent);

  ts.value = String(Date.now() - 10000);
  form.elements.company.value = "";
  form.dispatchEvent(new window.Event("submit", { cancelable: true, bubbles: true }));
  check("valida campos vacíos", /Revisa la empresa/.test(st.textContent), st.textContent);

  form.elements.website.value = "spam";
  form.elements.company.value = "ACME";
  form.dispatchEvent(new window.Event("submit", { cancelable: true, bubbles: true }));
  check("honeypot acepta en silencio", /Gracias/.test(st.textContent), st.textContent);

  const values = [...d.querySelectorAll("option")].map(o => o.value);
  check("values del select en inglés", values.every(v => /^[A-Za-z ]+$/.test(v)), values.join(","));
}

// ---------- about ----------
{
  const { window } = load("about/index.html", "about.es.js");
  const d = window.document;
  check("[about] un solo h1", d.querySelectorAll("h1").length === 1);
  check("[about] perfil de Adriana", /Adriana Culebro/.test(d.body.textContent));
  check("[about] retrato o marcador", d.querySelectorAll(".person-photo img, .portrait-pending").length === 1);
  check("[about] credenciales listadas", d.querySelectorAll(".creds li").length >= 8,
        String(d.querySelectorAll(".creds li").length));
  const sel = d.getElementById("langSelect");
  sel.value = "es"; sel.dispatchEvent(new window.Event("change"));
  check("[about] biografía traducida", /especialista en logística internacional/.test(d.body.textContent));
  check("[about] migas traducidas", d.querySelector('[data-i18n="ab.crumbHome"]').textContent === "Inicio");
}

// ---------- legales ----------
for (const [file, dict, label] of [
  ["legal/privacy/index.html", "legal-privacy.es.js", "privacidad"],
  ["legal/terms/index.html", "legal-terms.es.js", "términos"]]) {
  const { window } = load(file, dict);
  const d = window.document;
  check(`[${label}] un solo h1`, d.querySelectorAll("h1").length === 1);
  check(`[${label}] tiene secciones`, d.querySelectorAll(".legal-block").length >= 5,
        String(d.querySelectorAll(".legal-block").length));
  const sel = d.getElementById("langSelect");
  sel.value = "es"; sel.dispatchEvent(new window.Event("change"));
  check(`[${label}] traducido`, /[áéíóúñ]/.test(d.querySelector(".legal-block p").textContent));
}

console.log(`=== PASAN (${ok.length}) ===`);
if (bad.length) {
  console.log(`\n=== FALLAN (${bad.length}) ===`);
  bad.forEach(b => console.log("  " + b));
  process.exit(1);
}
