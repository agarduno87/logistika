# Instalar logistika en tu Mac

## 1. Poner la carpeta en su lugar

Descomprime el zip y deja la carpeta aquí:

    /Users/antoniogarduno/Downloads/logistika

## 2. Arrancar

Abre Terminal y pega esto:

    cd /Users/antoniogarduno/Downloads/logistika
    bash run.sh

Se usa `bash run.sh` y no `./run.sh` porque macOS le quita el permiso de
ejecución a los archivos que salen de un zip. Si prefieres el `./`:

    chmod +x run.sh && ./run.sh

El script crea el entorno virtual, instala las dependencias y levanta el sitio.
La primera vez tarda un minuto; después, segundos.

Abre: **http://127.0.0.1:8000**

Si el puerto está ocupado: `bash run.sh 8001`

Para detenerlo: `Ctrl + C`

## 3. Comprobar que todo está bien

Las pruebas necesitan una dependencia extra que el sitio NO usa en producción:

    source .venv/bin/activate
    pip install -r api/requirements-dev.txt
    python3 api/test_api.py

Deben salir 38 pruebas en verde. Si alguna falla, el mensaje dice exactamente qué.

Para las pruebas del navegador hace falta Node:

    brew install node
    npm install jsdom
    node tests/frontend.check.js

Los detalles de cada paso están en PRUEBAS.md.

## 4. Poner la foto de Adriana

Todavía no me llegó. Cuando la tengas:

    cp ~/Downloads/adriana.jpg assets/portraits/adriana.jpg
    python3 tools/build_portraits.py
    python3 tools/build_about.py

Mientras tanto la página About muestra un marcador con la marca, no una imagen
rota. Si el encuadre no queda bien, abre `tools/build_portraits.py` y ajusta la
línea `FOCUS`: son centro horizontal, centro vertical y qué tanto acercar.

## Abrir el HTML directamente NO funciona del todo

Si haces doble clic en `index.html`, el diseño se ve pero el formulario no
envía y el cambio de idioma puede fallar: el navegador bloquea esas cosas bajo
`file://`. Siempre `bash run.sh`.
