#!/usr/bin/env bash
#
# logistika — arranque local.
#
#   ./run.sh          levanta sitio + API en http://127.0.0.1:8000
#   ./run.sh 8080     usa otro puerto
#
# Un solo proceso sirve el sitio y la API desde el mismo origen: sin CORS,
# sin editar constantes, sin dos terminales.

set -euo pipefail

PORT="${1:-8000}"
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
API_DIR="$ROOT/api"
VENV="$ROOT/.venv"

say()  { printf '\033[1;36m==>\033[0m %s\n' "$1"; }
warn() { printf '\033[1;33m!! \033[0m %s\n' "$1"; }
die()  { printf '\033[1;31mXX \033[0m %s\n' "$1" >&2; exit 1; }

# --- 1. Python ---------------------------------------------------------------
command -v python3 >/dev/null 2>&1 || die "No encontré python3. En macOS: brew install python@3.12"

PY_OK=$(python3 -c 'import sys; print(1 if sys.version_info >= (3, 9) else 0)')
[ "$PY_OK" = "1" ] || die "Se necesita Python 3.9 o superior. Tienes: $(python3 -V)"
say "Python $(python3 -V 2>&1 | cut -d" " -f2)"

# --- 2. Puerto libre ---------------------------------------------------------
if command -v lsof >/dev/null 2>&1 && lsof -nP -iTCP:"$PORT" -sTCP:LISTEN >/dev/null 2>&1; then
  die "El puerto $PORT ya está ocupado. Prueba: ./run.sh 8001"
fi

# --- 3. Entorno virtual ------------------------------------------------------
# macOS marca su Python como 'externally managed': sin venv, pip se niega a instalar.
# Si el venv no se puede crear (disco de red, permisos, sin python3-venv), seguimos
# sin él en vez de abortar.
PY=python3
USE_VENV=0

if [ ! -d "$VENV" ]; then
  say "Creando entorno virtual en .venv"
  if python3 -m venv "$VENV" 2>/dev/null; then
    USE_VENV=1
  elif python3 -m venv --copies "$VENV" 2>/dev/null; then
    # --copies evita symlinks: sirve en volúmenes que no los soportan.
    USE_VENV=1
  else
    rm -rf "$VENV"
    warn "No pude crear el entorno virtual; seguiré con el Python del sistema."
  fi
else
  USE_VENV=1
fi

if [ "$USE_VENV" = "1" ]; then
  # shellcheck disable=SC1091
  source "$VENV/bin/activate"
  PY=python
fi

# --- 4. Dependencias ---------------------------------------------------------
if ! "$PY" -c "import fastapi, uvicorn, pydantic, email_validator" >/dev/null 2>&1; then
  say "Instalando dependencias (la primera vez tarda un minuto)"
  "$PY" -m pip install --quiet --upgrade pip >/dev/null 2>&1 || true
  if ! "$PY" -m pip install --quiet -r "$API_DIR/requirements.txt"; then
    warn "Reintentando la instalación para el usuario actual"
    "$PY" -m pip install --quiet --user --break-system-packages -r "$API_DIR/requirements.txt" \
      || die "Falló la instalación de dependencias. Revisa tu conexión y reintenta."
  fi
fi
"$PY" -c "import fastapi, uvicorn, pydantic, email_validator" >/dev/null 2>&1 \
  || die "Las dependencias no quedaron disponibles. Corre: $PY -m pip install -r api/requirements.txt"
say "Dependencias listas"

# --- 5. Configuración --------------------------------------------------------
if [ ! -f "$API_DIR/.env" ]; then
  cp "$API_DIR/.env.example" "$API_DIR/.env"
  warn "Creé api/.env desde la plantilla. Sin SMTP los mensajes se guardan pero no se envían por correo."
fi

set -a
# shellcheck disable=SC1091
source "$API_DIR/.env"
set +a
export ALLOWED_ORIGIN="${ALLOWED_ORIGIN:-http://127.0.0.1:$PORT}"

# --- 6. Arranque -------------------------------------------------------------
echo
say "Sitio y API en  ->  http://127.0.0.1:$PORT"
say "Español         ->  http://127.0.0.1:$PORT/?lang=es"
say "Salud de la API ->  http://127.0.0.1:$PORT/api/health"
echo "    (Ctrl+C para detener)"
echo

cd "$API_DIR"
exec "$PY" -m uvicorn main:app --host 127.0.0.1 --port "$PORT" --reload
