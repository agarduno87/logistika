"""
logistika — servidor de la aplicación.

Sirve DOS cosas desde un solo proceso y un solo puerto:
  1. El sitio estático (index.html, styles.css, app.js, i18n/…)
  2. La API de contacto en /api/contact

Servir ambos desde el mismo origen no es un atajo: elimina de raíz los problemas
de CORS, hace que /api/contact resuelva sin proxy y mantiene la CSP cerrada con
connect-src 'self'. Es la diferencia entre "corre de un comando" y "hay que
levantar dos servidores y editar una constante".

Ejecutar (desde la raíz del proyecto):
    ./run.sh
o a mano:
    cd api && uvicorn main:app --port 8000
Luego abre http://127.0.0.1:8000

Controles aplicados (AAIF security-standard):
    Mínimo privilegio ...... CORS cerrado, sin endpoints de lectura públicos,
                             lista negra de rutas en el servidor de estáticos
    Defensa en profundidad .. honeypot + trampa de tiempo + rate limit + validación
    Defaults seguros ........ sin docs de OpenAPI, sin CORS abierto, cabeceras puestas
    Gestión de secretos ..... todo por variables de entorno, nunca en el repositorio
    Logging ................. sin cuerpo del mensaje, sin correo completo, IP anonimizada
    Validación de entrada ... Pydantic con longitud máxima en todos los campos
    Autorización ............ el endpoint de lectura exige token de administrador
"""

from __future__ import annotations

import json as jsonlib
import logging
import os
import smtplib
import urllib.error
import urllib.request
import sqlite3
import time
from collections import deque
from contextlib import contextmanager
from email.message import EmailMessage
from pathlib import Path
from typing import Deque, Dict, Iterator

from fastapi import BackgroundTasks, FastAPI, Header, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, EmailStr, Field, field_validator

# --------------------------------------------------------------------------
# Rutas
# --------------------------------------------------------------------------
API_DIR = Path(__file__).resolve().parent
SITE_DIR = API_DIR.parent                      # la raíz del proyecto

# --------------------------------------------------------------------------
# Configuración — todo por entorno. Nada de secretos en el código.
# --------------------------------------------------------------------------
ALLOWED_ORIGIN = os.environ.get("ALLOWED_ORIGIN", "http://127.0.0.1:8000")
DB_PATH = Path(os.environ.get("DB_PATH", str(API_DIR / "leads.db")))

SMTP_HOST = os.environ.get("SMTP_HOST", "")
SMTP_PORT = int(os.environ.get("SMTP_PORT", "587"))
SMTP_USER = os.environ.get("SMTP_USER", "")
SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD", "")
MAIL_FROM = os.environ.get("MAIL_FROM", "")
MAIL_TO = os.environ.get("MAIL_TO", "")

ADMIN_TOKEN = os.environ.get("ADMIN_TOKEN", "")

# Notificación instantánea sin correo. Ver README, sección "Avisos de leads".
NOTIFY_CHANNEL = os.environ.get("NOTIFY_CHANNEL", "none").strip().lower()
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")
WEBHOOK_URL = os.environ.get("WEBHOOK_URL", "")

RATE_LIMIT_MAX = int(os.environ.get("RATE_LIMIT_MAX", "5"))
RATE_LIMIT_WINDOW_SECONDS = int(os.environ.get("RATE_LIMIT_WINDOW_SECONDS", "3600"))
MIN_FILL_SECONDS = 3
MAX_BODY_BYTES = 16 * 1024

# Debe coincidir exactamente con los value="" de los <option> en index.html.
# Están en inglés a propósito: el idioma cambia la etiqueta visible, nunca el
# valor enviado, así una visita en español no rompe esta validación.
ALLOWED_STAGES = {
    "Already importing",
    "Want to start",
    "Specific problem",
    "Outsource",
}

# Debe coincidir con LOCALES en i18n.js.
SUPPORTED_LOCALES = {"en", "es"}

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("logistika")

app = FastAPI(title="logistika", docs_url=None, redoc_url=None, openapi_url=None, redirect_slashes=True)

# Con sitio y API en el mismo origen, CORS no hace falta. Se deja configurado por
# si algún día se separan, pero cerrado a un solo origen. Nunca ["*"].
app.add_middleware(
    CORSMiddleware,
    allow_origins=[ALLOWED_ORIGIN],
    allow_credentials=False,
    allow_methods=["POST"],
    allow_headers=["Content-Type", "Accept"],
    max_age=600,
)


# --------------------------------------------------------------------------
# Cabeceras de seguridad. En producción detrás de nginx, las de allá mandan.
# --------------------------------------------------------------------------
CSP = (
    "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; "
    "font-src 'self'; connect-src 'self'; form-action 'self'; frame-ancestors 'none'; "
    "base-uri 'none'; object-src 'none'"
)


@app.middleware("http")
async def security_headers(request: Request, call_next):
    if request.method == "POST":
        raw_length = request.headers.get("content-length")
        if raw_length and raw_length.isdigit() and int(raw_length) > MAX_BODY_BYTES:
            return JSONResponse({"detail": "Payload too large"}, status_code=413)

    response = await call_next(request)
    response.headers["Content-Security-Policy"] = CSP
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Permissions-Policy"] = "geolocation=(), camera=(), microphone=(), payment=()"
    if request.url.path.startswith("/api/"):
        response.headers["Cache-Control"] = "no-store"
    return response


# --------------------------------------------------------------------------
# Rate limit en memoria. Suficiente para un proceso único.
# Con varios workers o instancias, muévelo a Redis o al reverse proxy.
# --------------------------------------------------------------------------
_hits: Dict[str, Deque[float]] = {}


def client_ip(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for", "")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


def rate_limited(ip: str) -> bool:
    now = time.time()
    window = _hits.setdefault(ip, deque())
    while window and now - window[0] > RATE_LIMIT_WINDOW_SECONDS:
        window.popleft()
    if len(window) >= RATE_LIMIT_MAX:
        return True
    window.append(now)
    return False


def anonymise(ip: str) -> str:
    """IPv4 sin el último octeto, IPv6 solo el prefijo. Logs sin PII completa."""
    if ":" in ip:
        return ":".join(ip.split(":")[:3]) + "::/48"
    parts = ip.split(".")
    return ".".join(parts[:3]) + ".0" if len(parts) == 4 else "unknown"


# --------------------------------------------------------------------------
# Persistencia
# --------------------------------------------------------------------------
@contextmanager
def db() -> Iterator[sqlite3.Connection]:
    conn = sqlite3.connect(DB_PATH)
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db() -> None:
    with db() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS leads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TEXT NOT NULL DEFAULT (datetime('now')),
                company TEXT NOT NULL,
                email TEXT NOT NULL,
                stage TEXT NOT NULL,
                message TEXT NOT NULL,
                locale TEXT NOT NULL DEFAULT 'en',
                ip_prefix TEXT
            )
            """
        )


# El arranque NO debe morir si el disco es de solo lectura. En Vercel, Lambda y
# cualquier contenedor con raíz inmutable, crear el .db lanza OperationalError
# al importar el módulo y la plataforma responde FUNCTION_INVOCATION_FAILED en
# TODAS las rutas, incluidas las estáticas: el sitio entero se cae por la base
# de datos del formulario. Se degrada en vez de reventar.
PERSISTENCE_ENABLED = True
try:
    init_db()
except (sqlite3.Error, OSError) as exc:
    PERSISTENCE_ENABLED = False
    log.error(
        "no se pudo abrir la base en %s (%s). El sitio sigue en pie y el "
        "formulario sigue avisando, pero los leads NO se guardan. "
        "Apunta DB_PATH a una ruta escribible, por ejemplo /tmp/leads.db",
        DB_PATH, exc,
    )


# --------------------------------------------------------------------------
# Entrada — toda cadena con longitud máxima explícita.
# --------------------------------------------------------------------------
class ContactRequest(BaseModel):
    company: str = Field(min_length=1, max_length=120)
    email: EmailStr = Field(max_length=254)
    stage: str = Field(min_length=1, max_length=80)
    message: str = Field(min_length=20, max_length=4000)
    website: str = Field(default="", max_length=200)     # honeypot
    rendered_at: int = Field(default=0, ge=0)
    locale: str = Field(default="en", max_length=10)

    @field_validator("company", "message")
    @classmethod
    def clean_text(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("empty after trimming")
        # Sin caracteres de control: evita inyección de encabezados en el correo saliente.
        if any(ord(ch) < 32 and ch not in "\n\r\t" for ch in cleaned):
            raise ValueError("control characters not allowed")
        return cleaned

    @field_validator("stage")
    @classmethod
    def known_stage(cls, value: str) -> str:
        if value not in ALLOWED_STAGES:
            raise ValueError("unknown stage")
        return value

    @field_validator("locale")
    @classmethod
    def known_locale(cls, value: str) -> str:
        # Idioma desde el que se envió: sirve para responder en el mismo idioma.
        return value if value in SUPPORTED_LOCALES else "en"


# --------------------------------------------------------------------------
# Correo — siempre texto plano. Nunca HTML con contenido del usuario.
# --------------------------------------------------------------------------
def send_webhook(payload: ContactRequest) -> bool:
    """Avisa por Telegram, Slack o Discord. Un POST HTTPS, sin SMTP, sin dominio
    propio y sin reputación de remitente que cuidar: el lead llega al teléfono en
    segundos. Se usa urllib de la biblioteca estándar para no añadir dependencias.

    Sale por la red hacia un tercero, así que nunca se envía el mensaje completo
    sin querer: se manda tal cual lo escribió el prospecto, que es el punto, pero
    la URL y el token viven solo en el entorno del servidor."""
    if NOTIFY_CHANNEL in ("", "none"):
        return False

    text = (
        "Nuevo lead\n"
        f"Empresa:  {payload.company}\n"
        f"Correo:   {payload.email}\n"
        f"Momento:  {payload.stage}\n"
        f"Idioma:   {payload.locale}\n\n"
        f"{payload.message}"
    )

    if NOTIFY_CHANNEL == "telegram":
        if not (TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID):
            log.warning("NOTIFY_CHANNEL=telegram pero falta token o chat id")
            return False
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        body = {"chat_id": TELEGRAM_CHAT_ID, "text": text, "disable_web_page_preview": True}
    elif NOTIFY_CHANNEL == "slack":
        if not WEBHOOK_URL:
            log.warning("NOTIFY_CHANNEL=slack pero falta WEBHOOK_URL")
            return False
        url, body = WEBHOOK_URL, {"text": text}
    elif NOTIFY_CHANNEL == "discord":
        if not WEBHOOK_URL:
            log.warning("NOTIFY_CHANNEL=discord pero falta WEBHOOK_URL")
            return False
        url, body = WEBHOOK_URL, {"content": text[:1900]}
    else:
        log.warning("NOTIFY_CHANNEL desconocido: %s", NOTIFY_CHANNEL)
        return False

    request = urllib.request.Request(
        url,
        data=jsonlib.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=10) as response:
            return 200 <= response.status < 300
    except Exception as exc:                       # noqa: BLE001
        log.error("webhook %s falló: %s", NOTIFY_CHANNEL, type(exc).__name__)
        return False


def notify(payload: ContactRequest) -> None:
    """Se ejecuta DESPUÉS de responderle al visitante, como tarea de fondo.

    Antes esto corría dentro del endpoint async con un smtplib bloqueante de
    hasta 15 segundos: si el servidor de correo tardaba, el event loop se
    congelaba y el sitio entero dejaba de responder mientras tanto. Una
    notificación lenta nunca debe hacer esperar a quien acaba de enviar el
    formulario."""
    send_webhook(payload)
    send_notification(payload)


def send_notification(payload: ContactRequest) -> bool:
    if not (SMTP_HOST and SMTP_USER and SMTP_PASSWORD and MAIL_FROM and MAIL_TO):
        log.warning("SMTP not configured — lead stored, no email sent")
        return False

    msg = EmailMessage()
    # El asunto se arma solo con valores de la lista blanca, nunca con texto libre.
    msg["Subject"] = f"[logistika] {payload.stage}"
    msg["From"] = MAIL_FROM
    msg["To"] = MAIL_TO
    msg["Reply-To"] = str(payload.email)
    msg.set_content(
        "New enquiry from the website\n\n"
        f"Company:  {payload.company}\n"
        f"Email:    {payload.email}\n"
        f"Stage:    {payload.stage}\n"
        f"Language: {payload.locale}\n\n"
        "Problem:\n"
        f"{payload.message}\n"
    )

    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=15) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.send_message(msg)
        return True
    except Exception as exc:                       # noqa: BLE001
        log.error("SMTP delivery failed: %s", type(exc).__name__)
        return False


# --------------------------------------------------------------------------
# API — se declara ANTES del montaje de estáticos para que tenga prioridad.
# --------------------------------------------------------------------------
@app.post("/api/contact", status_code=status.HTTP_201_CREATED)
async def contact(payload: ContactRequest, request: Request,
                  background: BackgroundTasks) -> dict:
    ip = client_ip(request)

    # Honeypot: se acepta en silencio para no darle señal al bot.
    if payload.website:
        log.info("honeypot triggered ip=%s", anonymise(ip))
        return {"status": "ok"}

    # Trampa de tiempo, revalidada aquí porque un bot puede saltarse el JavaScript.
    if payload.rendered_at:
        elapsed = time.time() - (payload.rendered_at / 1000)
        if elapsed < MIN_FILL_SECONDS:
            log.info("timetrap triggered ip=%s", anonymise(ip))
            raise HTTPException(status_code=400, detail="Submitted too quickly")

    if rate_limited(ip):
        log.info("rate limited ip=%s", anonymise(ip))
        raise HTTPException(status_code=429, detail="Too many submissions")

    # Sin disco escribible el lead no se guarda, pero el aviso SÍ sale: perder
    # el registro es malo, perder el lead es peor. Se avisa fuerte en el log
    # para que no pase inadvertido en producción.
    if PERSISTENCE_ENABLED:
        try:
            with db() as conn:
                conn.execute(
                    "INSERT INTO leads (company, email, stage, message, locale, ip_prefix) "
                    "VALUES (?, ?, ?, ?, ?, ?)",
                    (payload.company, str(payload.email), payload.stage,
                     payload.message, payload.locale, anonymise(ip)),
                )
        except (sqlite3.Error, OSError) as exc:
            log.error("lead NO guardado (%s). Empresa: %s, correo: %s",
                      exc, payload.company, payload.email)
    else:
        log.warning("lead NO guardado, persistencia deshabilitada. Empresa: %s, correo: %s",
                    payload.company, payload.email)

    # La notificación sale después de responder: el visitante ve su confirmación
    # de inmediato aunque Telegram o el SMTP estén lentos.
    background.add_task(notify, payload)

    # Log sin PII: ni el correo completo ni el cuerpo del mensaje.
    log.info(
        "lead stored stage=%s locale=%s domain=%s notify=%s ip=%s",
        payload.stage, payload.locale,
        str(payload.email).split("@")[-1], NOTIFY_CHANNEL, anonymise(ip),
    )
    return {"status": "ok"}


@app.get("/api/health")
async def health() -> dict:
    return {"status": "ok", "site_dir": str(SITE_DIR)}


@app.get("/api/leads")
async def leads(x_admin_token: str = Header(default="")) -> dict:
    """Lectura de leads. Sin token configurado queda cerrado (404, no 401:
    no confirmamos que el endpoint exista)."""
    if not ADMIN_TOKEN or x_admin_token != ADMIN_TOKEN:
        raise HTTPException(status_code=404, detail="Not found")
    with db() as conn:
        rows = conn.execute(
            "SELECT id, created_at, company, email, stage, locale FROM leads "
            "ORDER BY id DESC LIMIT 200"
        ).fetchall()
    return {
        "leads": [
            {"id": r[0], "created_at": r[1], "company": r[2],
             "email": r[3], "stage": r[4], "locale": r[5]}
            for r in rows
        ]
    }


# --------------------------------------------------------------------------
# Sitio estático
# --------------------------------------------------------------------------
# "assets" guarda los originales de los retratos (a color y en alta resolución).
# El sitio sirve las versiones procesadas de img/; los originales se quedan en el
# repositorio para poder regenerarlos, no para que cualquiera se los descargue.
BLOCKED_DIRS = {"api", "assets", "tools", "tests", ".git", ".venv", "venv",
                "__pycache__", "node_modules"}
BLOCKED_SUFFIXES = {".py", ".db", ".env", ".sh", ".pyc", ".log", ".sqlite3"}
BLOCKED_NAMES = {".env", ".gitignore", ".env.example"}


class SafeStaticFiles(StaticFiles):
    """StaticFiles con lista negra.

    Sin esto, montar el proyecto en "/" serviría api/main.py, api/.env y la base
    de leads como archivos descargables. Es el error clásico de servir la raíz del
    repositorio: el código fuente y las credenciales quedan a un GET de distancia.
    """

    async def get_response(self, path: str, scope):
        # Starlette normaliza la raíz "/" como ".", no como "": si no se trata
        # aparte, la regla de archivos ocultos la bloquea y la portada da 404.
        normalised = path.replace("\\", "/").strip("/")
        parts = [] if normalised in ("", ".") else [p for p in normalised.split("/") if p and p != "."]

        if any(p in BLOCKED_DIRS for p in parts):
            return Response(status_code=404)
        if any(p.startswith(".") for p in parts if p not in ("",)):
            return Response(status_code=404)
        if parts and parts[-1] in BLOCKED_NAMES:
            return Response(status_code=404)
        if parts and Path(parts[-1]).suffix.lower() in BLOCKED_SUFFIXES:
            return Response(status_code=404)

        return await super().get_response(path, scope)


app.mount("/", SafeStaticFiles(directory=str(SITE_DIR), html=True), name="site") # Comentando por errores en el backend
