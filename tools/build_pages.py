#!/usr/bin/env python3
"""
Genera la version estatica del sitio para GitHub Pages, en docs/.

    python3 tools/build_pages.py                 # dominio propio (rutas /)
    python3 tools/build_pages.py --base /mi-repo # project page de GitHub
    python3 tools/build_pages.py --domain ejemplo.com   # escribe CNAME

QUE HACE Y POR QUE
------------------
GitHub Pages solo sirve archivos. No corre Python, no ejecuta el backend y no
deja poner cabeceras HTTP. Eso rompe tres cosas del proyecto, y este script
resuelve las tres de la unica forma posible en un sitio estatico:

1. EL FORMULARIO. No hay /api/contact al que llamar. Se inyecta un script que
   intercepta el envio y abre el correo del visitante con los datos ya escritos.
   Funciona sin backend y sin servicios de terceros, pero NO guarda leads en
   base de datos: eso solo vuelve cuando el sitio corra en un servidor real.

2. LAS RUTAS ABSOLUTAS. Si el sitio vive en usuario.github.io/repo/, entonces
   /styles.css apunta a usuario.github.io/styles.css, que no existe, y la
   pagina sale sin diseno. Con --base se reescriben todas.

3. EL CODIGO FUENTE. En el servidor real, SafeStaticFiles bloquea api/, tools/
   y tests/. Aqui no hay servidor: se excluyen del build directamente.

LO QUE NO SE PUEDE ARREGLAR
---------------------------
La Content-Security-Policy viaja por cabecera HTTP y GitHub Pages no permite
cabeceras propias. NO se pone en un <meta> como sustituto: esa es exactamente
la regresion que dejo el sitio sin CSS una vez, y ademas frame-ancestors se
ignora en meta. En Pages el sitio queda sin CSP. Es una razon de peso para
tratar Pages como entorno de PRUEBAS y no como produccion final.
"""

from __future__ import annotations

import argparse
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "docs"

# Nada de esto se publica: es codigo, originales de marca o secretos.
BLOCKED_DIRS = {"api", "tools", "tests", "assets", "docs", ".git", ".venv",
                "venv", "__pycache__", ".pytest_cache", "node_modules"}
BLOCKED_SUFFIX = {".py", ".sh", ".db", ".sqlite3", ".pyc", ".env", ".zip", ".xlsx"}
BLOCKED_NAMES = {".env", ".env.example", ".gitignore", ".DS_Store", "_headers",
                 "README.md", "INSTALAR.md", "PRUEBAS.md", "vercel.json", ".vercelignore"}

FORM_SHIM = """/* GitHub Pages no tiene backend: el formulario se envia por correo.
   Esto lo inyecta tools/build_pages.py y NO existe en la version de servidor. */
(function () {
  var f = document.getElementById("form");
  if (!f) { return; }
  var st = document.getElementById("st");
  var MAIL = "__MAILTO__";

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
    var body = encodeURIComponent(lines.join("\\n\\n"));
    window.location.href = "mailto:" + MAIL + "?subject=" + subject + "&body=" + body;

    if (st) {
      st.textContent = st.getAttribute("data-mail-note") ||
        "Opening your email app. If nothing happens, write to " + MAIL;
    }
  }, true);
})();
"""

NOT_FOUND = """<!doctype html>
<html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Page not found</title>
<link rel="icon" href="__BASE__/favicon.ico" sizes="32x32">
<link rel="stylesheet" href="__BASE__/styles.css">
</head><body>
<main id="main"><section class="plain"><div class="wrap">
<div class="head">
  <p class="kick">404</p>
  <h1 class="t">That page does not exist.</h1>
  <p>The link may be old, or the address may have a typo.</p>
</div>
<p><a class="btn btn-p" href="__BASE__/">Back to the home page</a></p>
</div></section></main>
</body></html>
"""


def is_blocked(path: Path) -> bool:
    rel = path.relative_to(ROOT)
    if any(part in BLOCKED_DIRS for part in rel.parts):
        return True
    if path.name in BLOCKED_NAMES or path.suffix in BLOCKED_SUFFIX:
        return True
    if path.name.startswith(".") and path.name != ".nojekyll":
        return True
    return False


def patch_runtime_paths(text: str, base: str) -> str:
    """i18n.js construye la ruta del diccionario en JS, no en un atributo, asi
    que la reescritura de href/src no la ve. Bajo subdirectorio esto hacia que
    el selector de idioma no aplicara nada: el diccionario devolvia 404 en
    silencio y la pagina se quedaba en ingles."""
    if not base:
        return text
    return text.replace('var BASE = window.location.protocol === "file:" ? "i18n/" : "/i18n/";',
                        f'var BASE = window.location.protocol === "file:" ? "i18n/" : "{base}/i18n/";')


def rewrite(text: str, base: str) -> str:
    """Reescribe rutas absolutas para que funcionen bajo un subdirectorio.
    Solo toca href/src/content que empiecen con una sola barra: las que
    empiezan con // son protocolo-relativas y no deben tocarse."""
    if not base:
        return text
    text = re.sub(r'(href|src)="/(?!/)', rf'\1="{base}/', text)
    text = re.sub(r'url\(/(?!/)', f'url({base}/', text)

    # srcset lleva VARIAS rutas separadas por coma, cada una con su descriptor
    # ("/img/a.png 420w, /img/a@2x.png 840w"). La regex de href/src no las ve, y
    # bajo subdirectorio esas imagenes daban 404 sin romper nada visible: el
    # navegador caia al src de respaldo y el fallo solo aparecia en consola.
    def _srcset(m):
        partes = []
        for parte in m.group(2).split(","):
            parte = parte.strip()
            if parte.startswith("/") and not parte.startswith("//"):
                parte = base + parte
            partes.append(parte)
        return f'{m.group(1)}="' + ", ".join(partes) + '"'

    text = re.sub(r'(srcset)="([^"]*)"', _srcset, text)
    return text


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default="",
                    help="Subdirectorio, p.ej. /mi-repo, para project pages de GitHub")
    ap.add_argument("--domain", default="",
                    help="Dominio propio; escribe el archivo CNAME")
    ap.add_argument("--mailto", default="",
                    help="Correo al que va el formulario en la version estatica")
    args = ap.parse_args()

    base = args.base.rstrip("/")
    if base and not base.startswith("/"):
        base = "/" + base

    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir()

    copied = rewritten = 0
    for src in sorted(ROOT.rglob("*")):
        if not src.is_file() or is_blocked(src):
            continue
        dst = OUT / src.relative_to(ROOT)
        dst.parent.mkdir(parents=True, exist_ok=True)
        if src.suffix in {".html", ".css", ".js", ".json", ".webmanifest", ".xml", ".txt"}:
            text = src.read_text(encoding="utf-8")
            new = rewrite(text, base)
            if src.name == "i18n.js":
                new = patch_runtime_paths(new, base)
            if new != text:
                rewritten += 1
            dst.write_text(new, encoding="utf-8")
        else:
            shutil.copy2(src, dst)
        copied += 1

    # Sin .nojekyll, GitHub Pages pasa todo por Jekyll y descarta los archivos
    # y carpetas que empiezan con guion bajo.
    (OUT / ".nojekyll").write_text("", encoding="utf-8")

    (OUT / "404.html").write_text(NOT_FOUND.replace("__BASE__", base), encoding="utf-8")

    if args.domain:
        (OUT / "CNAME").write_text(args.domain.strip() + "\n", encoding="utf-8")

    mail = args.mailto or "hello@example.com"
    (OUT / "pages-form.js").write_text(FORM_SHIM.replace("__MAILTO__", mail), encoding="utf-8")
    tag = f'<script src="{base}/pages-form.js" defer></script>'
    for page in OUT.rglob("*.html"):
        text = page.read_text(encoding="utf-8")
        if 'id="form"' in text and "pages-form.js" not in text:
            text = text.replace("</body>", f"{tag}\n</body>")
            page.write_text(text, encoding="utf-8")

    print(f"  docs/  ->  {copied} archivos publicados, {rewritten} con rutas reescritas")
    print(f"  base: {base or '/ (dominio propio)'}")
    print(f"  formulario: correo a {mail}" + ("" if args.mailto else "  <-- CAMBIA ESTO con --mailto"))
    if args.domain:
        print(f"  CNAME: {args.domain}")
    print("\n  Recuerda: en Pages NO hay backend ni CSP. Es entorno de pruebas.")


if __name__ == "__main__":
    main()
