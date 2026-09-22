# CLAUDE.md — logistika

Memoria del proyecto para Claude Code. Léelo antes de tocar el sitio.
Última actualización: 2026-09-21.

## Qué es

Sitio de **logistika**, empresa de comercio exterior y logística de **Adriana Culebro
Jiménez** (Querétaro). Sitio estático bilingüe (inglés por defecto, español completo).
Marca visible en texto: **"Logistika"** con mayúscula (decisión del cliente, sep 2026).
Repo: github.com/agarduno87/logistika. Deploy de pruebas: logistika-beta.vercel.app.
Producción: **www.logistika.mx** (Neubox, aún por migrar; hoy muestra un mock).

## Cómo está hecho

- **Estático:** `index.html`, `styles.css`, `app.js`, más `about/`, `legal/`, `cotizacion/`.
- **i18n:** el inglés vive en el HTML con `data-i18n="clave"`; el español en `i18n/*.es.js`
  bajo la misma clave. **La clave es OPACA** (el hash NO se re-deriva en runtime): para
  cambiar un texto, edita el inglés en el HTML **y** el español en el diccionario por su
  clave. Común: `i18n/es.js`. Por página: `about.es.js`, `legal-*.es.js`.
- **Generadores (editar la FUENTE, no el output):**
  - `tools/build_about.py` → `about/index.html` + `i18n/about.es.js`
  - `tools/build_matrix.py` → matriz de servicios en `index.html` + sección MATRIX de `es.js`
  - `tools/build_legal.py` → páginas legales
  - `tools/build_pages.py` → `docs/` para GitHub Pages (base `/logistika`)
- **Backend (dev):** `api/main.py` (FastAPI + SQLite). NO va a producción (Neubox no corre
  Python). En producción los leads llegan por **correo** vía `contact.php`.
- **Pruebas:**
  - Backend + sitio: `source .venv/bin/activate && python3 api/test_api.py` (38)
  - Navegador (jsdom): `node tests/frontend.check.js` (30)
  - Correr la app local: `./run.sh` → http://127.0.0.1:8000

## Trampas críticas (NO repetir)

1. **CSP: nada inline.** El sitio sirve `Content-Security-Policy: ... style-src 'self';
   script-src 'self'` desde `_headers`. Eso **bloquea `<style>` y `<script>` inline** (y
   `style=` en HTML). En local sin CSP todo se ve bien; en Vercel/Neubox se rompe.
   → **Toda página nueva usa CSS y JS EXTERNOS.** Probar bajo la CSP real antes de subir
   (levantar un server local que mande esa cabecera). SVG inline y `data:` en img SÍ se permiten.
2. **flex-column estira imágenes.** Un `<img>` en un contenedor `display:flex;
   flex-direction:column` (align-items:stretch por defecto) se estira al ancho del
   contenedor y deforma el aspecto. → `align-items:flex-start` en el contenedor y
   `flex:none; align-self:flex-start` en la imagen.
3. **Inputs que recortan texto.** Un input con `width:100%` dentro de una grid `auto`
   colapsa a su ancho intrínseco y corta valores largos. Darle ancho explícito.
4. **`.sheet > *{position:relative}` pisaba el watermark** (mismo specificity, gana el de
   abajo) y lo dejaba en flujo. Cuidado con reglas `*` que sobreescriben posiciones.
5. **El logo es raster (PNG).** Wordmark color `img/logistika-logo@2x.png` (2.35:1),
   blanco `img/logistika-logo-white.png` (1.87:1). No estirarlo; respetar su aspecto.

## Fronteras legales (NO cruzar)

- **logistika NO es agencia aduanal, ni forwarder, ni transportista.** El despacho aduanero
  está reservado por ley al agente aduanal con patente. El sitio coordina, supervisa y
  audita; no despacha. Está en la FAQ, en términos y en la cotización — no quitarlo.
- **Bosch, Benteler, Tenneco, Geodis, UTI** fueron clientes/empleadores de Adriana, **NO de
  logistika.** Hay una prueba que falla si esos nombres aparecen en el sitio.
- **Precios:** no publicar cifras de ejemplo (hay prueba que falla). El modelo de precios
  no está confirmado por Adriana; la matriz muestra "On request".

## Marca

- En **texto**: "Logistika" con mayúscula (copy, `<title>`, JSON-LD, `llms.txt`).
- En **minúscula** siempre: dominio `logistika.mx`, correo `hola@logistika.mx`, el archivo
  del logo, las claves `data-i18n`, los `@id` del JSON-LD. El logo (wordmark) es minúsculo
  por diseño.

## Hosting y despliegue

- **Producción: Neubox, cPanel, PHP 7.4** (sin Python), dominio `www.logistika.mx` ya
  apunta ahí. Guía completa en `MIGRACION-NEUBOX.md`.
- Formulario en producción: `contact.php` (correo a **hola@logistika.mx**), con la misma
  defensa en profundidad que el backend (honeypot, trampa de tiempo, rate limit, validación,
  logging anonimizado). El `.htaccess` reescribe `/api/contact` → `contact.php`.
- Correo destino confirmado: **hola@logistika.mx**. WhatsApp: **+52 442 608 4290**.
- Vercel es solo entorno de pruebas. GitHub Pages sirve `docs/` (base `/logistika`).

## Cotización

- `cotizacion/` (index.html + cotizacion.css + cotizacion.js). Factura editable estilo
  membrete: franja azul + logo blanco, catálogo de servicios, MXN/USD, IVA 16%, imprimir/PDF,
  guardado en localStorage. `noindex`, no va en nav/sitemap (link para compartir).
  Montos en 0/"a cotizar" hasta que Adriana confirme precios.

## Lo que se hizo (sep 2026)

- Seguridad: se sacó `.env`/`leads.db` de git (repo público), token rotado, `.gitignore`.
- WhatsApp flotante; menú hamburguesa centrado; metadatos SEO acortados; `sitemap` con lastmod.
- GEO: `llms.txt`, `robots.txt` pro-IA, nodo `WebSite` en JSON-LD. Auditoría en `auditoria-logistika.md`.
- Contenido: **Recorrido de 7→6 etapas** (fusión de Documentación en Transporte Internacional;
  solo se renombraron títulos, los cuerpos se conservan), ficha "La ruta en corto" a 6 ítems,
  lista "Qué revisamos" en píldoras, marca a "Logistika", filas de credenciales Dirección/Idiomas
  quitadas. (Aplicado desde las hojas `contenido-*.md` que llenó el cliente.)
- Logo del footer reemplazado por el blanco hi-res.
- Cotización creada y pulida (CSP externa, membrete, logo proporcionado, meta sin recorte).

## Pendientes

- [ ] **Copies del hero** — el cliente los enviará; aplicarlos en `index.html` (EN) + `i18n/es.js`
      (ES) por clave. Claves del hero: `foreign-trade-logistics-supply-chain.2367`,
      `follow-your-cargo.5700`, `watch-where-the-money-goes.c0fe`, `seven-stages-sit-between-your.6cbc`,
      `walk-the-seven-stages.1ee1`, `see-the-three-levels.e9c4`, `years-in-foreign-trade.344f`,
      `continents-of-suppliers.ef26`, `point-of-contact-for-all.50c8` (los números "3" y "1"
      están hardcodeados en el HTML, sin clave).
- [ ] **Migración a Neubox** — seguir `MIGRACION-NEUBOX.md` cuando haya acceso a cPanel:
      subir estático + `contact.php` + `.htaccess`, validar SPF/DKIM y el envío de correo.
      Ojo si Neubox resulta ser nginx puro: el `.htaccess` no aplicaría y habría que apuntar
      el formulario directo a `/contact.php` en `app.js`.
- [ ] **Cuerpos de las etapas 1 y 2 del Recorrido** — hoy el título no coincide con el cuerpo
      (decisión del cliente: solo renombrar). Reescribir si el cliente lo pide (2ª pasada).
- [ ] **Precios del catálogo** de la cotización — precargar cuando Adriana confirme las bandas.
- [ ] **Validar el modelo de precios** con Adriana (el hallazgo de capacidad sigue sin confirmar).
- [ ] Search Console + Bing Webmaster + analítica (cuentas del cliente).
- [ ] Editor de contenido para que Adriana edite sin tocar código (opción CMS git).
