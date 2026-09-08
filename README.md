# logistika

Sitio de logistika — comercio exterior, logística y cadena de suministro.
Querétaro, México. Inglés como idioma principal, español completo.

## Arrancar

    bash run.sh          # http://127.0.0.1:8000
    bash run.sh 8001     # otro puerto

## Qué hay dentro

    index.html              portada: el recorrido de 7 etapas
    about/                  quién hace el trabajo (Adriana)
    legal/privacy/          aviso de privacidad
    legal/terms/            términos de uso
    styles.css              toda la hoja de estilos
    app.js                  riel del recorrido, menú, formulario
    i18n.js                 motor de idiomas
    i18n/es.js              español, 219 claves
    i18n/_template.js       plantilla para un idioma nuevo
    api/main.py             backend: formulario, base de datos, avisos
    api/requirements.txt    lo que necesita el sitio en producción (3 paquetes)
    api/requirements-dev.txt lo que necesitan las pruebas y los generadores
    api/test_api.py         38 pruebas
    tests/frontend.check.js 30 pruebas de navegador
    PRUEBAS.md              cómo probar todo, paso a paso
    tools/                  generadores (about, legales, iconos, OG, matriz, precios)
    logistika-precios.xlsx  modelo de precios y matriz de servicios
    assets/                 originales de marca (no se publican)

## Regenerar lo generado

    python3 tools/build_favicon.py     # iconos desde el icono de marca
    python3 tools/build_portraits.py   # retrato de Adriana
    python3 tools/build_about.py       # página About + su diccionario
    python3 tools/build_legal.py       # privacidad y términos
    python3 tools/build_og.py          # 6 tarjetas para redes
    python3 tools/build_pricing.py     # modelo de precios en Excel
    python3 tools/build_matrix.py      # matriz de servicios en el sitio

Las páginas de `about/` y `legal/` **se generan**: edita el texto en el script
correspondiente y vuelve a correrlo, no toques el HTML a mano.

## Precios y matriz

`logistika-precios.xlsx` calcula las bandas de precio a partir de la capacidad real
de Adriana. Ocho hojas: supuestos, horas por entregable, bandas, capacidad,
sensibilidad, matriz y validación de mercado. Solo se editan las celdas amarillas.

La matriz de servicios sale de una sola lista, en `tools/build_pricing.py`. El Excel
y el sitio la leen de ahí, así que no se pueden despegar. Para cambiarla: edita
`SERVICES` y corre los dos generadores.

**Los precios no están publicados.** El sitio dice "A cotizar" hasta que Adriana
confirme las cifras. Cuando lo haga, se ponen en `PRICES` dentro de
`tools/build_matrix.py` y se vuelve a correr. Hay una prueba que falla si se
publica un precio de ejemplo por descuido.

## Idiomas

El inglés vive en el propio HTML; no hay archivo para él. El español está en
`i18n/es.js` más un diccionario por página generada. Las claves se derivan del
texto en inglés, así que si cambias una frase la clave cambia — hay una prueba
que lo detecta en vez de dejar la página medio traducida.

Para agregar un idioma: copia `i18n/_template.js`, tradúcelo, y añade la entrada
a `LOCALES` en `i18n.js`.

## Antes de publicar

1. Apuntar www.logistika.mx al hosting y activar HTTPS
2. Verificar el dominio en Google Search Console (método TXT en DNS)
3. Configurar avisos de leads en `api/.env` (Telegram es lo más rápido)
4. Borrar los leads de prueba: `rm leads.db`
5. Abrir Google Business Profile de Querétaro
6. Subir la foto de Adriana (ver INSTALAR.md)

## La CSP

La Content-Security-Policy va **por cabecera HTTP**, en `_headers` (Cloudflare
Pages / Netlify) y en `api/main.py` para local. Nunca en un `<meta>`: ahí
`style-src 'self'` bloquea el CSS y la página aparece en texto plano. Hay una
prueba que falla si alguien vuelve a meterla en el HTML.
