#!/usr/bin/env python3
"""
Genera las páginas legales.

Uso:
    python3 tools/build_legal.py

Salida:
    legal/privacy/index.html   +  i18n/legal-privacy.es.js
    legal/terms/index.html     +  i18n/legal-terms.es.js

ADVERTENCIA
-----------
Estos textos describen con exactitud lo que el sitio hace hoy: no usa cookies,
no carga terceros, no rastrea, y el formulario guarda cinco campos. Eso los hace
honestos, que es la mitad del trabajo. La otra mitad es legal y no la cubre este
archivo: si vas a vender en la Unión Europea, o a manejar datos personales de
clientes mexicanos a escala, un abogado tiene que revisarlos y probablemente
añadir el aviso de privacidad integral que pide la LFPDPPP.

Marcadores a sustituir antes de publicar: tu-dominio.com, el nombre legal y el
correo de contacto para ejercicio de derechos.
"""

from __future__ import annotations

import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOMAIN = "https://www.logistika.mx"
E = html.escape

PAGES = [
    {
        "slug": "privacy",
        "path": "legal/privacy",
        "prefix": "pv",
        "title_en": "Privacy Notice",
        "title_es": "Aviso de privacidad",
        "desc_en": "What this site collects, what it does not, and how to have your data deleted. No cookies, no trackers, no third-party scripts.",
        "desc_es": "Qué recoge este sitio, qué no, y cómo pedir que se borren tus datos. Sin cookies, sin rastreadores, sin scripts de terceros.",
        "h1_en": "Privacy notice",
        "h1_es": "Aviso de privacidad",
        "deck_en": "Short, because there is little to describe. This site sets no cookies, loads nothing from third parties, and collects data in exactly one place: the contact form.",
        "deck_es": "Corto, porque hay poco que describir. Este sitio no pone cookies, no carga nada de terceros y recoge datos en exactamente un lugar: el formulario de contacto.",
        "sections": [
            ("What we collect", "Qué recogemos",
             [("When you send the contact form, we store the company name, your work email address, the stage you selected, your message, the language the site was in, and a truncated version of your IP address. Nothing else.",
               "Cuando envías el formulario de contacto guardamos el nombre de la empresa, tu correo de trabajo, el momento que elegiste, tu mensaje, el idioma en que estaba el sitio y una versión truncada de tu dirección IP. Nada más."),
              ("The IP address is truncated on purpose — the last octet is removed before it is stored. That is enough to detect abuse of the form and not enough to identify a person.",
               "La dirección IP se trunca a propósito: se le quita el último octeto antes de guardarla. Eso alcanza para detectar abuso del formulario y no alcanza para identificar a una persona.")]),
            ("What we do not collect", "Qué no recogemos",
             [("No cookies of any kind, including our own. No analytics. No tracking pixels, no advertising tags, no social media widgets, no embedded fonts from a third party. The site loads nothing from any domain other than its own, which you can verify in your browser's network panel in about ten seconds.",
               "Ninguna cookie de ningún tipo, ni siquiera propias. Sin analítica. Sin píxeles de rastreo, sin etiquetas publicitarias, sin widgets de redes sociales, sin tipografías cargadas de terceros. El sitio no carga nada desde ningún dominio que no sea el suyo, y puedes verificarlo en el panel de red de tu navegador en unos diez segundos."),
              ("The language you choose is kept in the page address, not in a cookie or in your browser's storage. That is why there is no cookie banner: there is nothing to consent to.",
               "El idioma que eliges se guarda en la dirección de la página, no en una cookie ni en el almacenamiento de tu navegador. Por eso no hay banner de cookies: no hay nada que consentir.")]),
            ("What we use it for", "Para qué lo usamos",
             [("To reply to you, and to keep a record of the enquiry. Your message is not added to any mailing list, is not used for marketing, and is not shared with, sold to or processed by any third party.",
               "Para responderte y para llevar registro de la solicitud. Tu mensaje no se agrega a ninguna lista de correo, no se usa para marketing y no se comparte, vende ni procesa con ningún tercero."),
              ("If we later add an email delivery provider or a CRM, this notice will be updated to name it before it is switched on.",
               "Si más adelante añadimos un proveedor de envío de correo o un CRM, este aviso se actualizará para nombrarlo antes de encenderlo.")]),
            ("How long we keep it", "Cuánto tiempo lo conservamos",
             [("Enquiries that do not turn into an engagement are deleted within twelve months. Records tied to a signed engagement are kept for as long as the commercial and tax obligations of that engagement require.",
               "Las solicitudes que no derivan en un proyecto se borran antes de doce meses. Los registros ligados a un proyecto firmado se conservan mientras lo exijan las obligaciones comerciales y fiscales de ese proyecto.")]),
            ("Your rights", "Tus derechos",
             [("You can ask us what we hold about you, ask for it to be corrected, or ask for it to be deleted. Write to the contact address below and we will confirm in writing when it is done.",
               "Puedes pedirnos qué tenemos sobre ti, pedir que se corrija o pedir que se borre. Escribe a la dirección de contacto de abajo y te confirmamos por escrito cuando esté hecho."),
              ("Deletion means deletion — the record is removed from the database, not flagged as hidden.",
               "Borrar significa borrar: el registro se elimina de la base de datos, no se marca como oculto.")]),
            ("Security", "Seguridad",
             [("The site is served over HTTPS with a strict content security policy. The contact form is rate limited and validated on the server. Credentials are held in environment variables, never in the code or in anything your browser downloads.",
               "El sitio se sirve por HTTPS con una política de seguridad de contenido estricta. El formulario tiene límite de envíos y validación en el servidor. Las credenciales viven en variables de entorno, nunca en el código ni en nada que descargue tu navegador.")]),
            ("Contact", "Contacto",
             [("logistika, Santiago de Querétaro, Querétaro, México. For any request about your data, use the contact form or the address published on the site.",
               "logistika, Santiago de Querétaro, Querétaro, México. Para cualquier solicitud sobre tus datos, usa el formulario de contacto o la dirección publicada en el sitio.")]),
        ],
    },
    {
        "slug": "terms",
        "path": "legal/terms",
        "prefix": "tm",
        "title_en": "Terms of Use",
        "title_es": "Términos de uso",
        "desc_en": "The terms that apply to this website: what the published information means, what it does not commit us to, and where the actual agreement lives.",
        "desc_es": "Los términos que aplican a este sitio: qué significa la información publicada, a qué no nos compromete y dónde vive el acuerdo real.",
        "h1_en": "Terms of use",
        "h1_es": "Términos de uso",
        "deck_en": "These terms cover the website. They are not the engagement contract — that is a separate, signed document, and where the two differ, the signed one wins.",
        "deck_es": "Estos términos cubren el sitio web. No son el contrato del proyecto: ese es un documento aparte y firmado, y donde ambos difieran, gana el firmado.",
        "sections": [
            ("What this site is", "Qué es este sitio",
             [("A description of services offered by logistika, based in Santiago de Querétaro, Querétaro, México. The content is informational and does not by itself create a client relationship or an obligation to provide any service.",
               "Una descripción de los servicios que ofrece logistika, con base en Santiago de Querétaro, Querétaro, México. El contenido es informativo y por sí mismo no crea una relación de cliente ni obligación de prestar ningún servicio.")]),
            ("Prices and timelines", "Precios y plazos",
             [("Any figure published here is an indicative band for designing an engagement, not a quote. Durations are typical, not guaranteed. The binding numbers are the ones in a written proposal signed by both sides.",
               "Cualquier cifra publicada aquí es una banda indicativa para diseñar un proyecto, no una cotización. Las duraciones son típicas, no garantizadas. Los números que obligan son los de una propuesta escrita y firmada por ambas partes.")]),
            ("Results and figures", "Resultados y cifras",
             [("Any savings, lead times or indicators described on this site come from operations we measured or that the client reported. Experience gained while working for a previous employer is described as experience — never as a client relationship of logistika. Past results describe what happened in that context; they are not a prediction of what will happen in yours.",
               "Cualquier ahorro, lead time o indicador descrito en este sitio proviene de operaciones que medimos o que el cliente reportó. La experiencia adquirida trabajando para un empleador anterior se describe como experiencia, nunca como una relación comercial de logistika. Los resultados pasados describen lo que ocurrió en ese contexto; no son una predicción de lo que ocurrirá en el tuyo.")]),
            ("Customs and regulated activity", "Aduanas y actividad regulada",
             [("logistika is not a customs broker, a freight forwarder or a carrier. In Mexico customs clearance is legally reserved to a licensed customs broker. We coordinate, supervise and audit the broker, the forwarder and the carriers on your behalf, and we answer for the coordination — but we do not perform clearance, we do not sign entries, and we do not charge for those acts.",
               "logistika no es agencia aduanal, ni forwarder, ni transportista. En México el despacho aduanero está legalmente reservado a un agente aduanal con patente. Coordinamos, supervisamos y auditamos al agente, al forwarder y a los transportistas en tu nombre, y respondemos por la coordinación — pero no realizamos el despacho, no firmamos pedimentos y no cobramos por esos actos."),
              ("Nothing published here constitutes customs, tax or legal advice for a specific operation. Bring us the operation and we will tell you, in writing, what applies to it and who has to sign it.",
               "Nada de lo publicado aquí constituye asesoría aduanera, fiscal o legal para una operación específica. Tráenos la operación y te decimos, por escrito, qué le aplica y quién tiene que firmarlo.")]),
            ("Intellectual property", "Propiedad intelectual",
             [("The text, structure and images of this site belong to the studio. The deliverables of an engagement — source code, documentation, data — belong to the client, from the first commit, as stated in the engagement contract.",
               "El texto, la estructura y las imágenes de este sitio son del estudio. Los entregables de un proyecto — código fuente, documentación, datos — son del cliente, desde el primer commit, según lo establece el contrato del proyecto.")]),
            ("Limitation", "Limitación",
             [("The site is provided as is. We make no warranty that it will be uninterrupted or error free, and we are not liable for decisions taken solely on the basis of information published here. Bring your situation to us and we will tell you what applies to it.",
               "El sitio se ofrece tal cual. No garantizamos que esté libre de interrupciones o errores, y no somos responsables de decisiones tomadas únicamente con base en la información publicada aquí. Tráenos tu situación y te decimos qué aplica en tu caso.")]),
            ("Governing law", "Ley aplicable",
             [("These terms are governed by the laws of the United Mexican States. Any dispute is subject to the courts of Santiago de Querétaro, Querétaro, unless a signed engagement contract states otherwise.",
               "Estos términos se rigen por las leyes de los Estados Unidos Mexicanos. Cualquier controversia se somete a los tribunales de Santiago de Querétaro, Querétaro, salvo que un contrato de proyecto firmado indique otra cosa.")]),
        ],
    },
]


def nav_html():
    return """  <div class="wrap">
    <a class="brand" href="/"><img src="/img/logistika-logo.png" srcset="/img/logistika-logo.png 420w, /img/logistika-logo@2x.png 840w" sizes="180px" alt="logistika" width="420" height="179" decoding="async"></a>
    <button class="burger" id="burger" aria-expanded="false" aria-controls="nav" aria-label="Open menu">&#9776;</button>
    <nav id="nav">
      <a href="/#journey" data-i18n="nav.journey">The journey</a>
      <a href="/#levels" data-i18n="nav.levels">Levels</a>
      <a href="/#check" data-i18n="nav.check">Health check</a>
      <a href="/#services" data-i18n="nav.services">Services</a>
      <a href="/about/" data-i18n="nav.about">Who we are</a>
      <label class="skip" for="langSelect" data-i18n="lang.label">Language</label>
      <select class="langpick" id="langSelect" hidden></select>
      <a class="cta" href="/#contact" data-i18n="nav.cta">Request an assessment</a>
    </nav>
  </div>"""


def build(p: dict) -> str:
    pre = p["prefix"]
    url = f"{DOMAIN}/{p['path']}/"
    blocks = []
    for i, (h_en, h_es, paras) in enumerate(p["sections"]):
        ps = "\n".join(
            f'        <p data-i18n="{pre}.s{i+1}p{j+1}">{E(t_en)}</p>'
            for j, (t_en, t_es) in enumerate(paras)
        )
        blocks.append(f"""      <section class="legal-block">
        <h2 data-i18n="{pre}.s{i+1}h">{E(h_en)}</h2>
{ps}
      </section>""")

    ld = {
        "@context": "https://schema.org",
        "@graph": [
            {"@type": "WebPage", "@id": url, "url": url, "name": p["title_en"],
             "description": p["desc_en"], "isPartOf": {"@id": DOMAIN + "/#studio"}},
            {"@type": "BreadcrumbList", "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "Home", "item": DOMAIN + "/"},
                {"@type": "ListItem", "position": 2, "name": p["title_en"], "item": url}]},
        ],
    }

    return f"""<!doctype html>
<html lang="en" dir="ltr" data-i18n-page="legal-{p['slug']}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{E(p["title_en"])} | logistika</title>
<meta name="description" content="{E(p["desc_en"])}">

<!-- No CSP meta here: the authoritative policy is an HTTP header. See _headers. -->
<meta name="referrer" content="strict-origin-when-cross-origin">
<meta name="robots" content="index,follow">
<meta name="color-scheme" content="light">
<meta name="theme-color" content="#0E2439">

<link rel="icon" href="/favicon.ico" sizes="32x32">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<link rel="manifest" href="/site.webmanifest">

<link rel="canonical" href="{url}">
<link rel="alternate" hreflang="en" href="{url}">
<link rel="alternate" hreflang="x-default" href="{url}">
<meta property="og:type" content="website">
<meta property="og:title" content="{E(p["title_en"])}">
<meta property="og:description" content="{E(p["desc_en"])}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{DOMAIN}/og/{p['slug']}.png">
<meta name="twitter:card" content="summary_large_image">

<link rel="stylesheet" href="/styles.css">
</head>
<body class="no-js">
<a class="skip" href="#main" data-i18n="skip">Skip to content</a>

<header>
{nav_html()}
</header>

<main id="main">
<section class="plain legal">
  <div class="wrap">
    <nav class="crumbs" aria-label="Breadcrumb">
      <a href="/" data-i18n="{pre}.crumbHome">Home</a>
      <span aria-hidden="true">/</span>
      <span data-i18n="{pre}.crumbSelf">{E(p["title_en"])}</span>
    </nav>
    <div class="band-head">
      <p class="kicker" data-i18n="{pre}.kicker">Legal</p>
      <h1 data-i18n="{pre}.h1">{E(p["h1_en"])}</h1>
      <p data-i18n="{pre}.deck">{E(p["deck_en"])}</p>
    </div>
    <div class="legal-body">
{chr(10).join(blocks)}
      <p class="legal-updated" data-i18n="{pre}.updated">Last updated: 15 August 2026.</p>
    </div>
  </div>
</section>
</main>

<footer>
  <div class="wrap">
    <div>logistika · Querétaro, México</div>
    <span>
      <a href="/legal/privacy/" data-i18n="footer.privacy">Privacy</a> ·
      <a href="/legal/terms/" data-i18n="footer.terms">Terms</a> ·
      Querétaro, México · <span id="yr"></span>
    </span>
  </div>
</footer>

<script type="application/ld+json">
{json.dumps(ld, ensure_ascii=False, separators=(",", ":"))}
</script>

<script src="/i18n.js" defer></script>
<script src="/app.js" defer></script>
</body>
</html>
"""


def build_dict(p: dict) -> str:
    pre = p["prefix"]
    d = {
        f"{pre}.crumbHome": "Inicio",
        f"{pre}.crumbSelf": p["title_es"],
        f"{pre}.kicker": "Legal",
        f"{pre}.h1": p["h1_es"],
        f"{pre}.deck": p["deck_es"],
        f"{pre}.updated": "Última actualización: 15 de agosto de 2026.",
    }
    for i, (h_en, h_es, paras) in enumerate(p["sections"]):
        d[f"{pre}.s{i+1}h"] = h_es
        for j, (t_en, t_es) in enumerate(paras):
            d[f"{pre}.s{i+1}p{j+1}"] = t_es

    body = ",\n".join(f'  {json.dumps(k, ensure_ascii=False)}: {json.dumps(v, ensure_ascii=False)}'
                      for k, v in d.items())
    return (f'/* Español — {p["title_es"]}. Generado por tools/build_legal.py. */\n'
            f'window.ttsRegisterDictionary("es", {{\n{body}\n}});\n')


def main() -> None:
    for p in PAGES:
        out = ROOT / p["path"]
        out.mkdir(parents=True, exist_ok=True)
        (out / "index.html").write_text(build(p), encoding="utf-8")
        (ROOT / "i18n" / f"legal-{p['slug']}.es.js").write_text(build_dict(p), encoding="utf-8")
        print(f"  {p['path']}/index.html  +  i18n/legal-{p['slug']}.es.js")


if __name__ == "__main__":
    main()
