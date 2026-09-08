#!/usr/bin/env python3
"""
Inyecta la matriz de servicios por nivel en index.html y sus traducciones en
i18n/es.js.

Uso:
    python3 tools/build_matrix.py

La matriz sale de la MISMA lista que usa tools/build_pricing.py para la hoja
"Matriz" del Excel. Si se define en los dos lados por separado, tarde o
temprano el sitio dice una cosa y la propuesta que se manda al cliente dice
otra, y esa contradicción se descubre siempre delante del cliente.

PRECIOS
-------
Los precios NO se publican hasta que Adriana los confirme. Mientras tanto cada
nivel muestra "On request". Cuando estén decididos, se ponen en PRICES abajo y
se vuelve a correr este script. Hay una prueba que falla si se publica un
precio de ejemplo.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

from build_pricing import SERVICES  # noqa: E402  — una sola fuente de verdad

# Nombre en inglés de cada servicio, en el mismo orden que SERVICES.
EN_NAMES = [
    ("Supply chain health check", "Ten to fifteen day diagnostic"),
    ("Import plan", "Product, origin, tariff code, landed cost"),
    ("Import management", "Every shipment coordinated end to end"),
    ("Pre-shipment document review", "Before your supplier ships"),
    ("Forwarder and broker coordination", "Selection, comparison and audit"),
    ("File closure and KPIs", "Real cost per shipment, OTIF, incidents"),
    ("Supply chain optimization", "Finding where the cost leaks"),
    ("Logistics control tower", "Monitoring, ETA, delays, incidents"),
    ("Exports", "As well as imports"),
    ("Procurement logistics", "Supplier and purchasing management"),
    ("Compliance and document audit", "Filings and files that survive an audit"),
    ("Reporting to leadership", "Cost control and KPIs for the board"),
    ("Project logistics", "Builds, plant start-ups, specialized transport"),
    ("Interim logistics management", "Three to twelve months covering the role"),
]

MARK_EN = {"Incluido": "Included", "Proyecto aparte": "Separate project", "—": "—"}

# Precio publicado por nivel. None = "On request".
# Cuando Adriana confirme, poner aquí la cifra tal como debe leerse.
PRICES = {
    "START": {"en": None, "es": None},
    "MANAGE": {"en": None, "es": None},
    "PARTNER": {"en": None, "es": None},
}

LEVELS = [
    ("START", "Fixed-price project", "Proyecto de precio fijo"),
    ("MANAGE", "Retainer + fee per shipment", "Iguala + fee por embarque"),
    ("PARTNER", "Monthly retainer, annual", "Iguala mensual, anual"),
]


def build_html():
    rows = []
    es = {}

    for i, ((name_es, desc_es, s, m, p), (name_en, desc_en)) in enumerate(zip(SERVICES, EN_NAMES)):
        k = f"mx.s{i+1}"
        es[k] = name_es
        es[f"{k}d"] = desc_es
        cells = []
        for lvl, val in (("start", s), ("manage", m), ("partner", p)):
            if val == "Incluido":
                cells.append(f'<td class="yes"><span class="tick" aria-hidden="true"></span>'
                             f'<span class="mxlabel" data-i18n="mx.included">Included</span></td>')
            elif val == "Proyecto aparte":
                cells.append('<td class="apart"><span class="mxlabel" '
                             'data-i18n="mx.apart">Separate project</span></td>')
            else:
                cells.append('<td class="no"><span class="mxlabel" '
                             'data-i18n="mx.no">Not included</span></td>')
        rows.append(
            f'        <tr>\n'
            f'          <th scope="row"><b data-i18n="{k}">{name_en}</b>'
            f'<span data-i18n="{k}d">{desc_en}</span></th>\n'
            f'          ' + "".join(cells) + '\n        </tr>')

    es.update({
        "mx.included": "Incluido",
        "mx.apart": "Proyecto aparte",
        "mx.no": "No incluido",
        "mx.kick": "Qué incluye cada nivel",
        "mx.h": "La matriz completa, sin letras chicas.",
        "mx.lead": "Un servicio o está dentro del nivel, o se cotiza como proyecto aparte, o no aplica. "
                   "No hay una cuarta categoría, y esta tabla es la misma que va en la propuesta.",
        "mx.service": "Servicio",
        "mx.price": "Precio",
        "mx.onrequest": "A cotizar",
        "mx.note": "Los precios se acuerdan por escrito antes de arrancar y no cambian a mitad del "
                   "proyecto salvo que cambie el alcance, también por escrito.",
    })
    for lvl, en_how, es_how in LEVELS:
        es[f"mx.{lvl.lower()}how"] = es_how

    price_cells = []
    for lvl, en_how, es_how in LEVELS:
        val = PRICES[lvl]["en"]
        shown = val if val else '<span data-i18n="mx.onrequest">On request</span>'
        price_cells.append(
            f'<td class="mxprice">{shown}'
            f'<span class="mxhow" data-i18n="mx.{lvl.lower()}how">{en_how}</span></td>')

    heads = "".join(f'<th scope="col">{lvl}</th>' for lvl, _, _ in LEVELS)

    html = f'''<!-- MATRIX:START — generado por tools/build_matrix.py, no editar a mano -->
<section class="plain tinted" id="matrix">
  <div class="wrap">
    <div class="head">
      <p class="kick" data-i18n="mx.kick">What each level includes</p>
      <h2 class="t" data-i18n="mx.h">The full matrix, no small print.</h2>
      <p data-i18n="mx.lead">A service is either inside the level, quoted as a separate project, or not part of it. There is no fourth category, and this is the same table that goes in the proposal.</p>
    </div>
    <div class="mxwrap">
      <table class="mx">
        <caption class="skip" data-i18n="mx.h">The full matrix, no small print.</caption>
        <thead>
          <tr><th scope="col" data-i18n="mx.service">Service</th>{heads}</tr>
        </thead>
        <tbody>
{chr(10).join(rows)}
        </tbody>
        <tfoot>
          <tr><th scope="row" data-i18n="mx.price">Price</th>{"".join(price_cells)}</tr>
        </tfoot>
      </table>
    </div>
    <p class="mxnote" data-i18n="mx.note">Prices are agreed in writing before the work starts and do not change mid-project unless the scope changes, also in writing.</p>
  </div>
</section>
<!-- MATRIX:END -->'''
    return html, es


def inject_html(html: str) -> None:
    p = ROOT / "index.html"
    src = p.read_text(encoding="utf-8")
    if "<!-- MATRIX:START" in src:
        src = re.sub(r"<!-- MATRIX:START.*?<!-- MATRIX:END -->", html, src, flags=re.S)
    else:
        anchor = '<section class="plain" id="services">'
        if anchor not in anchor and anchor not in src:
            raise SystemExit("no encontré dónde insertar la matriz")
        src = src.replace(anchor, html + "\n\n" + anchor, 1)
    p.write_text(src, encoding="utf-8")


def inject_dict(es: dict) -> None:
    p = ROOT / "i18n" / "es.js"
    src = p.read_text(encoding="utf-8")
    block = ",\n".join(f'  {json.dumps(k, ensure_ascii=False)}: {json.dumps(v, ensure_ascii=False)}'
                       for k, v in es.items())
    block = ("  /* MATRIX:START — generado por tools/build_matrix.py */\n"
             + block + ",\n  /* MATRIX:END */")
    if "/* MATRIX:START" in src:
        src = re.sub(r"  /\* MATRIX:START.*?/\* MATRIX:END \*/", block, src, flags=re.S)
    else:
        src = src.replace('window.ttsRegisterDictionary("es", {\n',
                          'window.ttsRegisterDictionary("es", {\n' + block + "\n", 1)
    p.write_text(src, encoding="utf-8")


def main() -> None:
    html, es = build_html()
    inject_html(html)
    inject_dict(es)
    published = [k for k, v in PRICES.items() if v["en"]]
    print(f"  index.html  ->  matriz de {len(SERVICES)} servicios")
    print(f"  i18n/es.js  ->  {len(es)} claves")
    print("  precios publicados:", ", ".join(published) if published else "ninguno (todos 'A cotizar')")


if __name__ == "__main__":
    main()
