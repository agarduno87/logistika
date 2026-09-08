#!/usr/bin/env python3
"""
Genera la página About (/about/) de logistika.

Uso:
    python3 tools/build_about.py

Salida:
    about/index.html
    i18n/about.es.js

SOBRE EL RETRATO
----------------
Si existe img/adriana-culebro-320.jpg (lo produce tools/build_portraits.py a
partir de la foto original en assets/portraits/), la página lo usa. Si no
existe, se dibuja un marcador con la marca en lugar de dejar una imagen rota,
y una prueba avisa de que el retrato sigue pendiente. La página nunca se ve mal
por una foto que todavía no llegó.

SOBRE LO QUE SE PUEDE Y NO SE PUEDE DECIR
-----------------------------------------
La biografía describe la trayectoria de Adriana sin presentar como clientes de
logistika a empresas que fueron clientes de sus EMPLEADORES. La cuenta de la
automotriz alemana se coordinó siendo empleada de un operador logístico global;
eso es experiencia, no una referencia comercial de logistika, y así está escrito.
Si algún día hay autorización por escrito para nombrarlas, se cambia aquí.
"""

from __future__ import annotations

import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOMAIN = "https://www.logistika.mx"
E = html.escape

PORTRAIT_SLUG = "adriana-culebro"

BIO_EN = [
    "logistika is led by Adriana Culebro Jiménez, a specialist in international logistics and foreign trade with more than fifteen years inside the operation — not around it. She holds a degree in Foreign Trade and Customs from Universidad Iberoamericana Puebla and a master's in Logistics and International Trade from Universidad Anáhuac in Mexico City, both licensed.",
    "Her track record is operational before it is advisory. She ran the in-house logistics account for a German automotive manufacturer at a global freight forwarder, coordinating air, ocean and ground shipments into plants in San Luis Potosí, Aguascalientes and Toluca, and reporting the indicators the account renewal depended on. Before that she analysed operations with suppliers across Europe, Asia and India — which is where you learn that a lead time quoted in a spreadsheet and a lead time that survives a customs inspection are two different numbers.",
    "Today she directs administration, logistics and foreign trade for a consultancy operating out of three offices, and has led complex industrial projects including the transfer and installation of metal structures — the kind of work where the schedule, the permits and the crane all have to agree with each other.",
    "That is the background logistika sells. Supply chain savings are not theoretical: they live in knowing which charge is negotiable, which document always jams, and which week of the month is the wrong one to ship.",
]

BIO_ES = [
    "logistika la dirige Adriana Culebro Jiménez, especialista en logística internacional y comercio exterior con más de quince años dentro de la operación, no alrededor de ella. Es licenciada en Comercio Exterior y Aduanas por la Universidad Iberoamericana Puebla y maestra en Logística y Comercio Internacional por la Universidad Anáhuac en la Ciudad de México, ambas con cédula profesional.",
    "Su trayectoria es operativa antes que consultiva. Llevó in-house la cuenta logística de una armadora automotriz alemana dentro de un operador logístico global, coordinando embarques aéreos, marítimos y terrestres hacia plantas en San Luis Potosí, Aguascalientes y Toluca, y reportando los indicadores de los que dependía la renovación de la cuenta. Antes de eso analizó operaciones con proveedores de Europa, Asia e India, que es donde se aprende que un lead time cotizado en una hoja de cálculo y un lead time que sobrevive a un reconocimiento aduanero son dos números distintos.",
    "Hoy dirige la administración, la logística y el comercio exterior de una consultoría que opera desde tres oficinas, y ha liderado proyectos industriales complejos, incluido el traslado e instalación de estructura metálica: ese tipo de trabajo donde el cronograma, los permisos y la grúa tienen que ponerse de acuerdo.",
    "Ese es el respaldo que vende logistika. Los ahorros de una cadena de suministro no están en la teoría: están en saber qué cargo es negociable, qué documento siempre se atora y en qué semana del mes no conviene embarcar.",
]

CREDS = [
    ("Degree", "Licenciatura",
     "BA in Foreign Trade &amp; Customs — Universidad Iberoamericana Puebla · licensed",
     "Licenciatura en Comercio Exterior y Aduanas — Universidad Iberoamericana Puebla · con cédula"),
    ("Master's", "Maestría",
     "MSc in Logistics &amp; International Trade — Universidad Anáhuac CDMX · licensed",
     "Maestría en Logística y Comercio Internacional — Universidad Anáhuac CDMX · con cédula"),
    ("Experience", "Experiencia",
     "15+ years in multimodal operations and complex logistics projects",
     "15+ años en operaciones multimodales y proyectos logísticos complejos"),
    ("Operations", "Operación",
     "Air, ocean and ground freight; automotive corporate accounts",
     "Carga aérea, marítima y terrestre; cuentas corporativas del sector automotriz"),
    ("Suppliers", "Proveedores",
     "Coordination with global suppliers across Europe, Asia and India",
     "Coordinación con proveedores globales en Europa, Asia e India"),
    ("Leadership", "Dirección",
     "Administration, logistics and foreign trade across three offices",
     "Administración, logística y comercio exterior en tres oficinas"),
    ("Projects", "Proyectos",
     "Transfer and installation of metal structures; industrial project supply",
     "Traslado e instalación de estructura metálica; suministro para proyectos industriales"),
    ("Systems", "Sistemas",
     "SAP · advanced spreadsheets · KPI reporting",
     "SAP · hojas de cálculo avanzadas · reporte de indicadores"),
    ("Languages", "Idiomas",
     "Spanish native · English · valid US visa",
     "Español nativo · inglés · visa estadounidense vigente"),
]

FOCUS = [
    ("Foreign trade", "Comercio exterior"),
    ("Import management", "Gestión de importaciones"),
    ("Supply chain", "Cadena de suministro"),
    ("Project logistics", "Logística de proyectos"),
    ("Vendor management", "Gestión de proveedores"),
]

PRINCIPLES = [
    ("Scope in writing, before the work", "Alcance por escrito, antes del trabajo",
     "Every engagement states what is included, what is excluded and what you receive. The exclusions are published so the first call is about your operation instead of about ours.",
     "Cada proyecto declara qué incluye, qué excluye y qué recibes. Las exclusiones están publicadas para que la primera llamada sea sobre tu operación y no sobre la nuestra."),
    ("We coordinate, we do not replace", "Coordinamos, no sustituimos",
     "logistika is not a customs broker, a forwarder or a carrier. That independence is what lets us select, compare and audit yours on your behalf instead of defending our own yard.",
     "logistika no es agencia aduanal, ni forwarder, ni transportista. Esa independencia es lo que nos permite elegir, comparar y auditar a los tuyos en tu nombre, en vez de defender nuestro propio patio."),
    ("You keep the report", "El reporte es tuyo",
     "Findings, roadmaps and procedures are written so another provider could execute them. A supplier who makes you dependent has solved their problem, not yours.",
     "Los hallazgos, las hojas de ruta y los procedimientos se escriben para que otro proveedor pueda ejecutarlos. Un proveedor que te vuelve dependiente resolvió su problema, no el tuyo."),
]


def nav_html(cta="#contact"):
    return f"""  <div class="wrap">
    <a class="brand" href="/"><img src="/img/logistika-logo.png" srcset="/img/logistika-logo.png 420w, /img/logistika-logo@2x.png 840w" sizes="180px" alt="logistika" width="420" height="179" decoding="async"></a>
    <button class="burger" id="burger" aria-expanded="false" aria-controls="nav" aria-label="Open menu">☰</button>
    <nav id="nav">
      <a href="/#journey" data-i18n="nav.journey">The journey</a>
      <a href="/#levels" data-i18n="nav.levels">Levels</a>
      <a href="/#check" data-i18n="nav.check">Health check</a>
      <a href="/#services" data-i18n="nav.services">Services</a>
      <a href="/about/" data-i18n="nav.about">Who we are</a>
      <label class="skip" for="langSelect" data-i18n="lang.label">Language</label>
      <select class="langpick" id="langSelect" hidden></select>
      <a class="cta" href="{cta}" data-i18n="nav.cta">Request an assessment</a>
    </nav>
  </div>"""


def form_html():
    return """    <form id="form" method="post" action="/api/contact" novalidate>
      <label><span data-i18n="form.company">Company</span><input name="company" required maxlength="120" data-i18n-ph="form.ph.company" placeholder="Your company"></label>
      <label><span data-i18n="form.email">Work email</span><input type="email" name="email" required maxlength="254" data-i18n-ph="form.ph.email" placeholder="you@company.com"></label>
      <label><span data-i18n="form.stage">Where you are</span><select name="stage">
        <option value="Already importing" data-i18n="form.o1">Already importing &#8212; I want to know if I am overpaying</option>
        <option value="Want to start" data-i18n="form.o2">I want to start importing</option>
        <option value="Specific problem" data-i18n="form.o3">I have a specific problem to solve</option>
        <option value="Outsource" data-i18n="form.o4">I want to outsource the whole function</option>
      </select></label>
      <label><span data-i18n="form.operation">Your operation</span><textarea name="message" rows="5" required maxlength="4000" data-i18n-ph="form.ph.message" placeholder="Product, country of origin, approximate volume, and what is not working today"></textarea></label>
      <div class="hp" aria-hidden="true"><label>Leave this empty<input name="website" tabindex="-1" autocomplete="off"></label></div>
      <input type="hidden" name="ts" id="ts">
      <button type="submit" data-i18n="form.send">Request an assessment</button>
      <p class="status" id="st" role="status" aria-live="polite"></p>
      <p class="note" data-i18n="form.note">We use your message to reply to you. No lists, no third parties.</p>
    </form>"""


def portrait_html() -> str:
    have = (ROOT / "img" / f"{PORTRAIT_SLUG}-320.jpg").exists()
    if not have:
        return """        <div class="portrait-pending" role="img" aria-label="Portrait pending">
          <span class="pp-mark" aria-hidden="true"></span>
          <span class="pp-note" data-i18n="ab.portraitPending">Portrait pending</span>
        </div>"""
    return f"""        <picture>
          <source type="image/webp" srcset="/img/{PORTRAIT_SLUG}-320.webp 320w, /img/{PORTRAIT_SLUG}-640.webp 640w" sizes="(max-width:640px) 100vw, 320px">
          <img src="/img/{PORTRAIT_SLUG}-320.jpg"
               srcset="/img/{PORTRAIT_SLUG}-320.jpg 320w, /img/{PORTRAIT_SLUG}-640.jpg 640w"
               sizes="(max-width:640px) 100vw, 320px"
               width="320" height="320" loading="lazy" decoding="async"
               alt="Portrait of Adriana Culebro Jimenez" data-i18n-alt="ab.portraitAlt">
        </picture>"""


def build() -> str:
    bio = "\n".join(f'        <p data-i18n="ab.bio{i+1}">{E(t)}</p>' for i, t in enumerate(BIO_EN))
    focus = "".join(f'<span data-i18n="ab.focus{i+1}">{en}</span>' for i, (en, es) in enumerate(FOCUS))
    creds = "\n".join(
        f'          <li><b data-i18n="ab.credk{i+1}">{k_en}</b><span data-i18n="ab.credv{i+1}">{v_en}</span></li>'
        for i, (k_en, k_es, v_en, v_es) in enumerate(CREDS))
    principles = "\n".join(
        f'      <div class="lvl"><span class="tag" data-i18n="ab.pr{i+1}n">Principle {i+1:02d}</span>'
        f'<h3 data-i18n="ab.pr{i+1}t">{E(t_en)}</h3>'
        f'<p class="sub" data-i18n="ab.pr{i+1}d">{E(d_en)}</p></div>'
        for i, (t_en, t_es, d_en, d_es) in enumerate(PRINCIPLES))

    ld = {
        "@context": "https://schema.org",
        "@graph": [
            {"@type": "AboutPage", "@id": DOMAIN + "/about/", "url": DOMAIN + "/about/",
             "name": "Who we are — logistika"},
            {"@type": "Person", "@id": DOMAIN + "/about/#adriana",
             "name": "Adriana Culebro Jiménez",
             "jobTitle": "Director, Foreign Trade and Logistics",
             "worksFor": {"@id": DOMAIN + "/#logistika"},
             "knowsAbout": ["Foreign trade", "Customs", "Import management",
                            "Supply chain", "Project logistics", "Multimodal transport"],
             "alumniOf": [
                 {"@type": "CollegeOrUniversity", "name": "Universidad Iberoamericana Puebla"},
                 {"@type": "CollegeOrUniversity", "name": "Universidad Anáhuac México"}],
             "address": {"@type": "PostalAddress", "addressLocality": "Santiago de Querétaro",
                         "addressCountry": "MX"}},
            {"@type": "BreadcrumbList", "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "Home", "item": DOMAIN + "/"},
                {"@type": "ListItem", "position": 2, "name": "Who we are", "item": DOMAIN + "/about/"}]},
        ],
    }

    return f"""<!doctype html>
<html lang="en" dir="ltr" data-i18n-page="about">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Who We Are: Adriana Culebro Jim&#233;nez | logistika &#8212; Quer&#233;taro, M&#233;xico</title>
<meta name="description" content="logistika is led by Adriana Culebro Jim&#233;nez, a specialist in international logistics and foreign trade with 15+ years in multimodal operations, automotive accounts and complex industrial projects.">

<!-- No CSP meta here: the authoritative policy is an HTTP header. See _headers. -->
<meta name="referrer" content="strict-origin-when-cross-origin">
<meta name="robots" content="index,follow,max-image-preview:large">
<meta name="color-scheme" content="light">
<meta name="theme-color" content="#385DAB">

<link rel="icon" href="/favicon.ico" sizes="32x32">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<link rel="manifest" href="/site.webmanifest">

<link rel="canonical" href="{DOMAIN}/about/">
<link rel="alternate" hreflang="en" href="{DOMAIN}/about/">
<link rel="alternate" hreflang="es" href="{DOMAIN}/es/nosotros/">
<link rel="alternate" hreflang="x-default" href="{DOMAIN}/about/">
<meta property="og:type" content="profile">
<meta property="og:title" content="Who we are &#8212; logistika">
<meta property="og:description" content="Fifteen years inside the operation, not around it.">
<meta property="og:url" content="{DOMAIN}/about/">
<meta property="og:image" content="{DOMAIN}/og/about.png">
<meta name="twitter:card" content="summary_large_image">

<link rel="stylesheet" href="/styles.css">
</head>
<body class="no-js">
<a class="skip" href="#main" data-i18n="skip">Skip to content</a>

<header>
{nav_html()}
</header>

<main id="main">
<section class="hero" id="top">
  <div class="wrap">
    <div>
      <nav class="crumbs" aria-label="Breadcrumb">
        <a href="/" data-i18n="ab.crumbHome">Home</a>
        <span aria-hidden="true">/</span>
        <span data-i18n="ab.crumbSelf">Who we are</span>
      </nav>
      <p class="kick" data-i18n="ab.kick">Who does the work</p>
      <h1><span data-i18n="ab.h1a">Fifteen years</span> <em data-i18n="ab.h1b">inside the operation.</em></h1>
      <p class="lead" data-i18n="ab.deck">Most consultancies sell you a partner and staff the project with someone else. This page exists so you know exactly who takes your operation: one specialist, named, with the licences and the shipments behind her.</p>
      <div class="btns">
        <a class="btn btn-p" href="#contact" data-i18n="ab.cta1">Request an assessment</a>
        <a class="btn btn-s" href="/#journey" data-i18n="ab.cta2">See the seven stages</a>
      </div>
    </div>
    <div class="preview">
      <h2 data-i18n="ab.cardHead">The studio</h2>
      <div class="pv">
        <div class="pvrow"><b data-i18n="ab.k1">Based in</b><span data-i18n="ab.v1">Quer&#233;taro, M&#233;xico</span></div>
        <div class="pvrow"><b data-i18n="ab.k2">Working languages</b><span>EN / ES</span></div>
        <div class="pvrow hot"><b data-i18n="ab.k3">Entry point</b><span data-i18n="ab.v3">Ten-day health check</span></div>
        <div class="pvrow"><b data-i18n="ab.k4">Delivery</b><span data-i18n="ab.v4">Remote, overlap hours agreed</span></div>
        <div class="pvrow hot"><b data-i18n="ab.k5">What we are not</b><span data-i18n="ab.v5">Not a customs broker, forwarder or carrier</span></div>
      </div>
      <p class="pvfoot" data-i18n="ab.stamp">You work with the person on this page.</p>
    </div>
  </div>
</section>

<section class="plain tinted">
  <div class="wrap">
    <div class="head">
      <p class="kick" data-i18n="ab.profileKick">The profile</p>
      <h2 class="t" data-i18n="ab.profileH">Adriana Culebro Jim&#233;nez</h2>
    </div>
    <article class="person">
      <div class="person-photo">
{portrait_html()}
      </div>
      <div class="person-body">
        <p class="person-role" data-i18n="ab.role">Director &#183; Foreign trade, logistics and supply chain</p>
{bio}
        <div class="pill-row">{focus}</div>
        <h3 class="creds-head" data-i18n="ab.credsHead">Credentials</h3>
        <ul class="creds">
{creds}
        </ul>
      </div>
    </article>
  </div>
</section>

<section class="plain">
  <div class="wrap">
    <div class="head">
      <p class="kick" data-i18n="ab.prKick">How we work</p>
      <h2 class="t" data-i18n="ab.prH">Three commitments, and they are checkable.</h2>
    </div>
    <div class="levels">
{principles}
    </div>
  </div>
</section>

<section class="plain contact" id="contact">
  <div class="wrap">
    <div>
      <p class="kick" data-i18n="ab.conKick">Start here</p>
      <h2 class="t" data-i18n="ab.conH">Tell us what you are importing.</h2>
      <div class="head"><p data-i18n="ab.conLead">The product, the origin and a rough volume is enough for a first written read on your operation. If we do not see anything worth fixing, we will say so.</p></div>
    </div>
{form_html()}
  </div>
</section>
</main>

<footer>
  <div class="wrap">
    <img src="/img/logistika-logo-white.png" alt="logistika" width="360" height="193" loading="lazy" decoding="async">
    <span>
      <a href="/legal/privacy/" data-i18n="footer.privacy">Privacy</a> &#183;
      <a href="/legal/terms/" data-i18n="footer.terms">Terms</a> &#183;
      Quer&#233;taro, M&#233;xico &#183; <span id="yr"></span>
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


def build_dict() -> str:
    d = {
        "ab.crumbHome": "Inicio", "ab.crumbSelf": "Nosotros",
        "ab.kick": "Quién hace el trabajo",
        "ab.h1a": "Quince años", "ab.h1b": "dentro de la operación.",
        "ab.deck": "Casi toda consultoría te vende un socio y luego asigna el proyecto a alguien más. Esta página existe para que sepas exactamente quién toma tu operación: una especialista, con nombre, con las cédulas y los embarques que lo respaldan.",
        "ab.cta1": "Solicitar diagnóstico", "ab.cta2": "Ver las siete etapas",
        "ab.cardHead": "El estudio",
        "ab.k1": "Con base en", "ab.v1": "Querétaro, México",
        "ab.k2": "Idiomas de trabajo",
        "ab.k3": "Punto de entrada", "ab.v3": "Diagnóstico de diez días",
        "ab.k4": "Entrega", "ab.v4": "Remoto, con horas de traslape acordadas",
        "ab.k5": "Lo que no somos", "ab.v5": "Ni agencia aduanal, ni forwarder, ni transportista",
        "ab.stamp": "Trabajas con la persona de esta página.",
        "ab.profileKick": "El perfil", "ab.profileH": "Adriana Culebro Jiménez",
        "ab.role": "Dirección · Comercio exterior, logística y cadena de suministro",
        "ab.credsHead": "Credenciales",
        "ab.portraitAlt": "Retrato de Adriana Culebro Jiménez",
        "ab.portraitPending": "Retrato pendiente",
        "ab.prKick": "Cómo trabajamos",
        "ab.prH": "Tres compromisos, y se pueden verificar.",
        "ab.conKick": "Empecemos", "ab.conH": "Cuéntanos qué estás importando.",
        "ab.conLead": "Con el producto, el origen y un volumen aproximado basta para darte una primera lectura por escrito de tu operación. Si no vemos nada que valga la pena arreglar, te lo decimos.",
        "nav.journey": "El recorrido", "nav.levels": "Niveles", "nav.check": "Diagnóstico",
        "nav.services": "Servicios", "nav.about": "Nosotros", "nav.cta": "Solicitar diagnóstico",
        "lang.label": "Idioma", "skip": "Ir al contenido",
        "footer.privacy": "Privacidad", "footer.terms": "Términos",
        "form.company": "Empresa", "form.email": "Correo de trabajo",
        "form.stage": "En qué momento estás", "form.operation": "Tu operación",
        "form.o1": "Ya importo — quiero saber si estoy pagando de más",
        "form.o2": "Quiero empezar a importar",
        "form.o3": "Tengo un problema puntual que resolver",
        "form.o4": "Quiero externalizar la función completa",
        "form.send": "Solicitar diagnóstico",
        "form.note": "Usamos tu mensaje para responderte. Sin listas, sin terceros.",
        "form.ph.company": "Tu empresa", "form.ph.email": "tu@empresa.com",
        "form.ph.message": "Producto, país de origen, volumen aproximado y qué es lo que hoy no funciona",
        "menu.open": "Abrir menú", "menu.close": "Cerrar menú",
        "msg.thanks": "Gracias, te contactamos pronto.",
        "msg.tooFast": "Tómate un momento para describir tu operación y envía.",
        "msg.invalid": "Revisa la empresa, el correo y la descripción.",
        "msg.sending": "Enviando tu mensaje…",
        "msg.sent": "Mensaje enviado. Recibirás una respuesta escrita en un día hábil.",
        "msg.rate": "Demasiados mensajes desde esta conexión. Inténtalo en una hora.",
        "msg.error": "El mensaje no se pudo enviar ahora. Inténtalo de nuevo en unos minutos.",
        "msg.connection": "Problema de conexión — el mensaje no se envió. Inténtalo de nuevo.",
        "form.sending": "Enviando…",
        "msg.fileProtocol": "Abre el sitio por http:// para enviar el formulario. Corre ./run.sh y usa http://127.0.0.1:8000",
    }
    for i, t in enumerate(BIO_ES):
        d[f"ab.bio{i+1}"] = t
    for i, (en, es) in enumerate(FOCUS):
        d[f"ab.focus{i+1}"] = es
    for i, (k_en, k_es, v_en, v_es) in enumerate(CREDS):
        d[f"ab.credk{i+1}"] = k_es
        d[f"ab.credv{i+1}"] = v_es
    for i, (t_en, t_es, d_en, d_es) in enumerate(PRINCIPLES):
        d[f"ab.pr{i+1}n"] = f"Principio {i+1:02d}"
        d[f"ab.pr{i+1}t"] = t_es
        d[f"ab.pr{i+1}d"] = d_es

    body = ",\n".join(f'  {json.dumps(k, ensure_ascii=False)}: {json.dumps(v, ensure_ascii=False)}'
                      for k, v in d.items())
    return ('/* Español — página About. Generado por tools/build_about.py:\n'
            '   edita las biografías allí y vuelve a generar, no este archivo. */\n'
            f'window.ttsRegisterDictionary("es", {{\n{body}\n}});\n')


def main() -> None:
    (ROOT / "about").mkdir(exist_ok=True)
    (ROOT / "about" / "index.html").write_text(build(), encoding="utf-8")
    (ROOT / "i18n" / "about.es.js").write_text(build_dict(), encoding="utf-8")
    has_photo = (ROOT / "img" / f"{PORTRAIT_SLUG}-320.jpg").exists()
    print("  about/index.html  +  i18n/about.es.js")
    print("  retrato:", "incluido" if has_photo else "PENDIENTE — falta la foto de Adriana")


if __name__ == "__main__":
    main()
