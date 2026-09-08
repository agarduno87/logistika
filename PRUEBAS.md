# Cómo probar logistika, paso a paso

Todo esto se corre desde la carpeta del proyecto:

    cd /Users/antoniogarduno/Downloads/logistika

---

## Resumen de qué necesitas

| Para... | Necesitas | Se instala con |
|---|---|---|
| Ver el sitio y usar el formulario | Python 3.9+ | ya viene en macOS |
| Correr las pruebas del backend | Python + httpx | `pip install -r api/requirements-dev.txt` |
| Correr las pruebas del navegador | Node.js + jsdom | `brew install node` y `npm install jsdom` |
| Regenerar iconos, retrato o tarjetas | Pillow | va en `requirements-dev.txt` |
| Regenerar el Excel de precios | openpyxl | va en `requirements-dev.txt` |

Nada de esto hace falta para publicar el sitio. En producción solo corren las
tres dependencias de `api/requirements.txt`.

---

## PASO 1 — Levantar el sitio (lo único indispensable)

    bash run.sh

Eso es todo. El script se encarga solo de:

1. verificar que tengas Python 3.9 o superior
2. comprobar que el puerto 8000 esté libre
3. crear el entorno virtual en `.venv`
4. instalar FastAPI, uvicorn y pydantic
5. crear `api/.env` desde la plantilla
6. arrancar el servidor

Abre **http://127.0.0.1:8000**

Otras direcciones útiles:

    http://127.0.0.1:8000/?lang=es      el sitio en español
    http://127.0.0.1:8000/about/        quién hace el trabajo
    http://127.0.0.1:8000/api/health    responde {"status":"ok"}

Para detenerlo: `Ctrl + C`. Si el puerto está ocupado: `bash run.sh 8001`.

**Por qué `bash run.sh` y no `./run.sh`:** macOS le quita el permiso de ejecución
a los archivos que salen de un zip. Si prefieres el `./`, corre una vez
`chmod +x run.sh`.

### Qué revisar a ojo

- El diseño se ve (colores, tipografía). Si aparece en texto plano, el CSS no cargó.
- El punto ámbar viaja por el riel lateral al hacer scroll.
- El selector de idioma cambia la página completa, incluida la matriz.
- El formulario de abajo acepta un mensaje y responde "Message sent".

---

## PASO 2 — Pruebas del backend (38 pruebas)

Primero instala las dependencias de prueba, una sola vez:

    source .venv/bin/activate
    pip install -r api/requirements-dev.txt

Después, cada vez que quieras:

    python3 api/test_api.py

Debe terminar con `38 pasaron, 0 fallaron`. Si algo falla, el mensaje dice
exactamente qué prueba y por qué.

**Ojo:** sin `requirements-dev.txt` esto truena con
`RuntimeError: The starlette.testclient module requires the httpx package`.
No es un error del proyecto: el TestClient de FastAPI necesita httpx y FastAPI
no lo trae de fábrica.

Si prefieres pytest, también funciona:

    cd api && python3 -m pytest test_api.py -q

Usa `python3 -m pytest` y no `pytest` a secas: así corre el pytest del entorno
virtual y no uno que tengas suelto en el sistema.

### Qué comprueban esas pruebas

- que el formulario acepte lo válido y rechace lo inválido
- que el código fuente no se pueda descargar desde el navegador
- que no haya CSP en `<meta>` ni estilos inline
- que cada página tenga un solo `<h1>`, canonical, iconos y tarjeta social
- que todo el texto marcado tenga traducción al español
- que no aparezcan nombres de clientes de sus empleadores anteriores
- que el CSS sea CSS de verdad y no HTML disfrazado
- que no se publique un precio de ejemplo en la matriz

---

## PASO 3 — Pruebas del navegador (30 pruebas)

Necesitas Node.js. Si no lo tienes:

    brew install node

Luego, una sola vez:

    npm install jsdom

Y cada vez:

    node tests/frontend.check.js

Debe decir `=== PASAN (30) ===`.

Esto levanta un navegador simulado y comprueba lo que el backend no puede ver:
que el riel se arme con sus siete marcas, que el menú abra y cierre con Escape,
que el cambio de idioma traduzca de verdad, y que el formulario valide antes de
mandar nada.

---

## PASO 4 — Regenerar cosas (solo si cambias contenido)

Requiere las dependencias del paso 2.

    python3 tools/build_favicon.py     # iconos, desde el icono de marca
    python3 tools/build_portraits.py   # retrato de Adriana
    python3 tools/build_about.py       # página About + su diccionario
    python3 tools/build_legal.py       # privacidad y términos
    python3 tools/build_og.py          # 6 tarjetas para redes
    python3 tools/build_pricing.py     # modelo de precios en Excel
    python3 tools/build_matrix.py      # matriz de servicios en el sitio

Las páginas de `about/` y `legal/` **se generan**: edita el texto dentro del
script y vuelve a correrlo. Si editas el HTML a mano, el siguiente build lo pisa.

Para cambiar el retrato:

    cp ~/Downloads/nueva-foto.jpg assets/portraits/adriana.jpg
    python3 tools/build_portraits.py
    python3 tools/build_about.py

Si el encuadre no queda, ajusta `FOCUS` en `tools/build_portraits.py`.

---

## PASO 5 — El Excel de precios

`logistika-precios.xlsx` se abre en Excel, Numbers o Google Sheets sin instalar
nada: ya trae todos los valores calculados.

Solo se editan las **celdas amarillas**. Todo lo demás son fórmulas y se
recalcula solo. Empieza por la hoja "Léeme".

Si lo regeneras con `build_pricing.py`, las fórmulas quedan sin valor guardado
hasta que lo abras una vez en Excel y lo guardes.

---

## Problemas comunes

**"No encontré python3"** → `brew install python@3.12`

**"El puerto 8000 ya está ocupado"** → `bash run.sh 8001`, o busca qué lo usa
con `lsof -nP -iTCP:8000 -sTCP:LISTEN`

**"externally-managed-environment" al instalar** → estás fuera del entorno
virtual. Corre `source .venv/bin/activate` primero.

**El sitio se ve sin diseño** → lo abriste con doble clic. Tiene que ser
`bash run.sh` y `http://127.0.0.1:8000`.

**El formulario no envía** → mismo motivo. Con `file://` el navegador bloquea
la petición; el propio sitio te lo avisa en pantalla.

**Errores raros en la consola del navegador** mencionando `g2.styles.css`,
`designSystem.styles.css` o el color `#027E6F` → son de la extensión Grammarly,
no del sitio. Pruébalo en una ventana de incógnito.
