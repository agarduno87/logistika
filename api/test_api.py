#!/usr/bin/env python3
"""
Pruebas del backend y del sitio de logistika.

    cd api
    python3 -m pytest test_api.py -q
o simplemente:
    python3 api/test_api.py

Muchas de estas pruebas existen porque el error YA PASÓ una vez, en este
proyecto o en el anterior. Cada una tiene una nota que dice cuál era.
"""

from __future__ import annotations

import importlib
import json
import os
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))

os.environ.setdefault("DB_PATH", str(Path(tempfile.gettempdir()) / "logistika_test.db"))
os.environ.setdefault("ALLOWED_ORIGIN", "http://127.0.0.1:8000")
os.environ.setdefault("RATE_LIMIT_MAX", "500")
os.environ.setdefault("NOTIFY_CHANNEL", "none")
os.environ.pop("SMTP_HOST", None)

for path in (Path(os.environ["DB_PATH"]),):
    if path.exists():
        path.unlink()

import main  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

importlib.reload(main)
client = TestClient(main.app)

PAGES = ["/", "/about/", "/legal/privacy/", "/legal/terms/"]


def brief(**over):
    data = {
        "company": "Planta Industrial SA",
        "email": "compras@planta.mx",
        "stage": "Already importing",
        "message": "We import components from Germany, roughly 12 shipments a month.",
        "website": "",
        "rendered_at": 0,
        "locale": "en",
    }
    data.update(over)
    return data


# --------------------------------------------------------------------------
# Formulario
# --------------------------------------------------------------------------
def test_valid_submission():
    assert client.post("/api/contact", json=brief()).status_code == 201


def test_unknown_stage_rejected():
    """El value del <option> viaja en inglés siempre. Si alguien traduce el
    value en vez de la etiqueta, una visita en español dejaría de poder
    enviar el formulario y nadie se enteraría."""
    assert client.post("/api/contact", json=brief(stage="Ya importo")).status_code == 422


def test_all_option_values_are_accepted():
    body = (ROOT / "index.html").read_text(encoding="utf-8")
    import re
    values = re.findall(r'<option value="([^"]+)"', body)
    assert values, "no se encontraron opciones en el formulario"
    for value in values:
        assert value in main.ALLOWED_STAGES, f"el HTML ofrece '{value}' y el backend lo rechaza"


def test_honeypot_is_silently_accepted():
    r = client.post("/api/contact", json=brief(website="http://spam.example"))
    assert r.status_code == 201


def test_bad_email_rejected():
    assert client.post("/api/contact", json=brief(email="no-arroba")).status_code == 422


def test_empty_message_rejected():
    assert client.post("/api/contact", json=brief(message="   ")).status_code == 422


def test_oversized_message_rejected():
    assert client.post("/api/contact", json=brief(message="x" * 5000)).status_code == 422


def test_lead_is_stored_with_stage():
    client.post("/api/contact", json=brief(company="Almacenes Bajio"))
    import sqlite3
    con = sqlite3.connect(os.environ["DB_PATH"])
    row = con.execute("SELECT company, stage FROM leads WHERE company='Almacenes Bajio'").fetchone()
    con.close()
    assert row and row[1] == "Already importing"


def test_ip_is_truncated_not_stored_whole():
    """El aviso de privacidad promete que la IP se guarda truncada.
    Si esto cambia, el aviso se vuelve mentira."""
    client.post("/api/contact", json=brief(company="IP Check"))
    import sqlite3
    con = sqlite3.connect(os.environ["DB_PATH"])
    row = con.execute("SELECT ip_prefix FROM leads WHERE company='IP Check'").fetchone()
    con.close()
    # En TestClient no hay IP de cliente real, así que se acepta "unknown";
    # lo que nunca debe aparecer es una IPv4 completa.
    assert row is not None
    stored = row[0]
    assert stored == "unknown" or stored.endswith(".0"), stored
    import re
    assert not re.fullmatch(r"\d+\.\d+\.\d+\.[1-9]\d*", stored), f"IP completa guardada: {stored}"


# --------------------------------------------------------------------------
# Avisos
# --------------------------------------------------------------------------
def test_notifications_off_by_default_and_never_block():
    """El envío va en BackgroundTasks: quien manda el formulario no espera a
    Telegram ni al SMTP. Antes esto corría dentro del endpoint async con un
    smtplib bloqueante de 15 s y congelaba el sitio entero."""
    assert main.NOTIFY_CHANNEL in ("none", "")
    import inspect
    assert "background.add_task" in inspect.getsource(main.contact)


# --------------------------------------------------------------------------
# Servidor de archivos
# --------------------------------------------------------------------------
def test_pages_are_served():
    for path in PAGES:
        r = client.get(path)
        assert r.status_code == 200, path
        assert "<h1" in r.text, path


def test_root_is_not_treated_as_a_hidden_file():
    """Starlette entrega la raíz como '.', y la regla de archivos ocultos la
    confundía con un dotfile: la portada devolvía 404."""
    assert client.get("/").status_code == 200


def test_source_and_assets_are_not_downloadable():
    for path in (
        "/api/main.py",
        "/api/.env.example",
        "/tools/build_about.py",
        "/tests/frontend.check.js",
        "/assets/logo.png",
        "/run.sh",
        "/.gitignore",
    ):
        assert client.get(path).status_code == 404, f"{path} se está sirviendo"


def test_static_files_exist():
    for path in ("/styles.css", "/app.js", "/i18n.js", "/i18n/es.js",
                 "/favicon.ico", "/favicon.svg", "/apple-touch-icon.png",
                 "/site.webmanifest", "/robots.txt", "/sitemap.xml",
                 "/img/logistika-logo.png", "/img/logistika-logo-white.png"):
        assert client.get(path).status_code == 200, path


def test_admin_endpoint_is_closed_without_token():
    """Sin ADMIN_TOKEN configurado devuelve 404, no 401: así el endpoint ni
    siquiera admite que existe, que es lo correcto para algo que expone leads."""
    assert client.get("/api/leads").status_code in (401, 403, 404)


def test_admin_endpoint_rejects_a_wrong_token():
    original = main.ADMIN_TOKEN
    main.ADMIN_TOKEN = "correcto"
    try:
        wrong = client.get("/api/leads", headers={"x-admin-token": "incorrecto"})
        right = client.get("/api/leads", headers={"x-admin-token": "correcto"})
        assert wrong.status_code in (401, 403, 404), wrong.status_code
        assert right.status_code in (200, 401, 403, 404), right.status_code
        assert wrong.status_code != 200
    finally:
        main.ADMIN_TOKEN = original


# --------------------------------------------------------------------------
# Marca, SEO y contenido
# --------------------------------------------------------------------------
def test_no_csp_meta_anywhere():
    """LA regresión de este proyecto: una CSP en <meta> con style-src 'self'
    bloquea el CSS y la página se ve en texto plano. La CSP va por cabecera."""
    for path in PAGES:
        body = client.get(path).text
        assert "http-equiv=\"Content-Security-Policy\"" not in body, path


def test_csp_is_served_as_a_header():
    assert "Content-Security-Policy" in (ROOT / "_headers").read_text(encoding="utf-8")


def test_no_inline_styles_anywhere():
    """Un style="" inline es invisible bajo la CSP de producción: no se aplica
    y nadie entiende por qué el elemento se ve distinto."""
    for path in PAGES:
        assert " style=\"" not in client.get(path).text, path


def test_every_page_has_one_h1():
    for path in PAGES:
        assert client.get(path).text.count("<h1") == 1, path


def test_every_page_links_the_legal_pages():
    for path in PAGES:
        body = client.get(path).text
        assert 'href="/legal/privacy/"' in body, path
        assert 'href="/legal/terms/"' in body, path


def test_every_page_has_icons_and_canonical():
    for path in PAGES:
        body = client.get(path).text
        assert 'rel="icon"' in body, path
        assert 'rel="canonical"' in body, path
        assert 'name="theme-color"' in body, path


def test_every_page_has_a_reachable_og_image():
    for path in PAGES:
        body = client.get(path).text
        assert 'property="og:image"' in body, path
        og = body.split('property="og:image" content="')[1].split('"')[0]
        local = og.replace("https://www.logistika.mx", "")
        assert client.get(local).status_code == 200, f"{path} apunta a {local}"


def test_structured_data_is_valid_json():
    import re
    for path in PAGES:
        for block in re.findall(r'<script type="application/ld\+json">(.*?)</script>',
                                client.get(path).text, re.S):
            json.loads(block)


def test_matrix_is_present_and_complete():
    """La matriz del sitio y la hoja "Matriz" del Excel salen de la misma lista.
    Si alguien edita una y no la otra, el sitio y la propuesta que se manda al
    cliente dicen cosas distintas."""
    import re
    body = client.get("/").text
    assert 'id="matrix"' in body
    rows = re.findall(r"<tr>\s*<th scope=\"row\">", body)
    assert len(rows) >= 14, f"la matriz tiene {len(rows)} filas de servicio"
    for level in ("START", "MANAGE", "PARTNER"):
        assert f">{level}</th>" in body, f"falta la columna {level}"


def test_no_example_price_is_published():
    """Los precios del modelo son supuestos míos, no cifras que Adriana haya
    confirmado. Hasta que las confirme, el sitio dice "On request"; esta prueba
    impide que una cifra de ejemplo se publique por descuido."""
    import re
    body = client.get("/").text
    section = body.split('id="matrix"')[1].split("</section>")[0]
    assert "On request" in section or "mx.onrequest" in section
    money = re.findall(r"[$€]\s?\d[\d,\.]{2,}", section)
    assert not money, f"hay precios publicados en la matriz: {money}"


def test_customs_broker_boundary_is_stated():
    """La frontera legal es lo más importante de la página: logistika no es
    agencia aduanal y no puede dar a entender que despacha."""
    home = client.get("/").text.lower()
    terms = client.get("/legal/terms/").text.lower()
    assert "not a customs broker" in home
    assert "customs broker" in terms


def test_no_employer_client_is_claimed_as_our_own():
    """Bosch, Benteler y Tenneco fueron clientes de sus EMPLEADORES, no de
    logistika. Publicarlos como referencia propia sería engañoso."""
    for path in PAGES:
        body = client.get(path).text.lower()
        for name in ("bosch", "benteler", "tenneco", "geodis", "uti logistics"):
            assert name not in body, f"{name} aparece en {path}"


def test_privacy_notice_matches_what_the_site_does():
    privacy = client.get("/legal/privacy/").text.lower()
    assert "no cookies" in privacy
    for path in PAGES:
        body = client.get(path).text.lower()
        for tracker in ("document.cookie", "localstorage", "googletagmanager", "google-analytics"):
            assert tracker not in body, f"{tracker} en {path}"


def test_no_third_party_origins():
    import re
    for path in PAGES:
        for url in re.findall(r'(?:src|href)="(https?://[^"]+)"', client.get(path).text):
            assert "logistika.mx" in url, f"{path} carga {url}"


# --------------------------------------------------------------------------
# Traducción
# --------------------------------------------------------------------------
def test_every_marked_string_has_a_spanish_translation():
    """Las claves se derivan del texto en inglés: si alguien cambia una frase
    y no actualiza el diccionario, la clave deja de existir y esa línea se
    quedaría en inglés sin avisar. Esta prueba avisa."""
    import re
    common = set(re.findall(r'^\s*"([^"]+)":', (ROOT / "i18n" / "es.js").read_text(encoding="utf-8"), re.M))
    runtime = set(re.findall(r'dict\["([^"]+)"\]\s*=', (ROOT / "i18n.js").read_text(encoding="utf-8")))

    page_dicts = {"/about/": "about.es.js",
                  "/legal/privacy/": "legal-privacy.es.js",
                  "/legal/terms/": "legal-terms.es.js"}
    for path in PAGES:
        body = client.get(path).text
        keys = set(re.findall(r'data-i18n(?:-ph|-alt)?="([^"]+)"', body))
        have = set(common) | runtime
        extra = page_dicts.get(path)
        if extra:
            have |= set(re.findall(r'^\s*"([^"]+)":',
                                   (ROOT / "i18n" / extra).read_text(encoding="utf-8"), re.M))
        missing = sorted(keys - have)
        assert not missing, f"{path} sin traducir: {missing[:6]}"


def test_dictionaries_load_as_plain_scripts():
    """Se cargan con <script src>, no con fetch de JSON: abrir el sitio con
    file:// rompía el fetch y el selector de idioma no hacía nada."""
    engine = (ROOT / "i18n.js").read_text(encoding="utf-8")
    assert "script.src" in engine
    assert "fetch(" not in engine


# --------------------------------------------------------------------------
# Accesibilidad
# --------------------------------------------------------------------------
def test_stylesheet_is_actually_css():
    """El extractor que separó el CSS del HTML original se guió por la primera
    aparición del texto "<style>", y encontró primero una MENCIÓN de esa
    etiqueta dentro de un comentario del head: styles.css salió con un pedazo
    de HTML pegado al inicio. Pesaba lo correcto y hasta parseaba, así que
    ninguna comprobación por tamaño lo habría detectado."""
    import re
    css = (ROOT / "styles.css").read_text(encoding="utf-8")
    assert css.lstrip().startswith(":root"), css[:60]
    assert not re.search(r"<(html|head|meta|title|link|body|div|style)\b", css), "hay HTML dentro del CSS"
    assert css.count("{") == css.count("}"), "llaves desbalanceadas"
    served = client.get("/styles.css")
    assert served.status_code == 200
    assert served.text.lstrip().startswith(":root")
    assert "--paper:" in served.text


def test_every_class_used_by_generated_pages_exists():
    """Las páginas generadas usan clases que no están en la propuesta original.
    Si alguien regenera el CSS desde el HTML ganador y olvida el bloque extra,
    About y las legales se ven sin estilo."""
    css = (ROOT / "styles.css").read_text(encoding="utf-8")
    for cls in (".person", ".creds", ".legal-block", ".langpick",
                ".portrait-pending", ".crumbs", ".split"):
        assert cls in css, f"falta {cls} en styles.css"


def test_brand_colours_meet_wcag_aa_for_small_text():
    """El ámbar y el periwinkle de la marca NO tienen contraste suficiente para
    texto pequeño sobre blanco. Se usan en fondos, puntos y trazos. Esta prueba
    fija los tonos que sí se usan como texto."""
    css = (ROOT / "styles.css").read_text(encoding="utf-8")

    def value(name):
        return css.split(f"--{name}:")[1].split(";")[0].strip()

    def luminance(hex_colour):
        hex_colour = hex_colour.lstrip("#")
        ch = [int(hex_colour[i:i + 2], 16) / 255 for i in (0, 2, 4)]
        adj = [c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4 for c in ch]
        return 0.2126 * adj[0] + 0.7152 * adj[1] + 0.0722 * adj[2]

    def ratio(a, b):
        la, lb = luminance(a), luminance(b)
        hi, lo = max(la, lb), min(la, lb)
        return (hi + 0.05) / (lo + 0.05)

    paper = value("paper")
    for token in ("blue", "muted", "ink"):
        assert ratio(value(token), paper) >= 4.5, f"--{token} sobre --paper no llega a 4.5:1"


def test_matrix_labels_are_readable():
    """El periwinkle de la marca da 1.6:1 sobre blanco. Sirve para trazos y
    fondos, nunca para texto que carga significado como "Not included"."""
    css = (ROOT / "styles.css").read_text(encoding="utf-8")
    block = css.split(".mx .no .mxlabel{")[1].split("}")[0]
    assert "--peri-soft" not in block, "la etiqueta usa un tono sin contraste"
    assert "--muted" in block


def test_images_declare_dimensions():
    """Sin width/height la página salta al cargar la imagen."""
    import re
    for path in PAGES:
        for tag in re.findall(r"<img[^>]*>", client.get(path).text):
            assert 'width="' in tag and 'height="' in tag, f"{path}: {tag[:70]}"
            assert 'alt="' in tag, f"{path}: img sin alt"


def test_portrait_is_present_or_explicitly_pending():
    """Mientras no llegue la foto de Adriana la página muestra un marcador con
    la marca, nunca una imagen rota."""
    body = client.get("/about/").text
    has_photo = "adriana-culebro-320.jpg" in body
    has_placeholder = "portrait-pending" in body
    assert has_photo or has_placeholder
    if has_photo:
        assert client.get("/img/adriana-culebro-320.jpg").status_code == 200


def run() -> int:
    tests = [(n, o) for n, o in sorted(globals().items())
             if n.startswith("test_") and callable(o)]
    failed = 0
    for name, fn in tests:
        try:
            fn()
            print(f"  ok    {name}")
        except AssertionError as exc:
            failed += 1
            print(f"  FALLA {name}: {exc}")
        except Exception as exc:                      # noqa: BLE001
            failed += 1
            print(f"  ERROR {name}: {type(exc).__name__}: {exc}")
    print(f"\n{len(tests) - failed} pasaron, {failed} fallaron")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(run())
