# Migración de logistika a Neubox — guía paso a paso

Guía para publicar el sitio en `https://www.logistika.mx` (hoy muestra un mock) y dejar
los leads llegando por correo. Escrita para hacerse **sin conocer cPanel de antes**.

- **Hosting:** Neubox, plan compartido con **cPanel**. Corre **PHP 7.4** (confirmado), MySQL. **No corre Python.**
- **Dominio:** `logistika.mx` ya apunta a Neubox (por eso el mock ya se ve). No hay que tocar DNS para publicar.
- **Qué se sube:** el sitio estático + `contact.php` + `.htaccess`. **No** se sube `api/` (Python), ni `.venv/`, ni `tests/`, ni `node_modules/`.

---

## Resumen en una línea

Subir el sitio a `public_html`, editar 3 datos en `contact.php`, revisar que el correo
salga, y probar el formulario en vivo. 30–45 min la primera vez.

---

## Paso 0 — Antes de empezar, ten a la mano

- [ ] Usuario y contraseña del **panel de Neubox** (y desde ahí, el botón **cPanel**).
- [ ] Confirmado el **correo destino de los leads** y que ese buzón **exista** (ej. `hola@logistika.mx`). Ver Paso 4.
- [ ] Opcional: credenciales **FTP** (las da cPanel) si prefieres subir con FileZilla.

---

## Paso 1 — Preparar el paquete a subir (en tu Mac)

En la carpeta del proyecto, genera un zip **solo con lo que va a producción**:

```bash
cd ~/Documents/logistika
zip -r ../logistika-neubox.zip . \
  -x ".git/*" ".venv/*" "node_modules/*" "api/*" "tests/*" \
     "*.pyc" "__pycache__/*" "*.db" ".env" "package*.json" \
     "history*.md" "auditoria-*.md" "MIGRACION-NEUBOX.md" "PRUEBAS.md" "INSTALAR.md" "GITHUB-PAGES.md"
```

Eso deja dentro del zip: `index.html`, `styles.css`, `app.js`, `i18n.js`, `i18n/`,
`about/`, `legal/`, `img/`, `assets/`, `og/`, iconos, `favicon.*`, `robots.txt`,
`sitemap.xml`, `llms.txt`, `site.webmanifest`, **`contact.php`** y **`.htaccess`**.

> Verifica que el zip trae el `.htaccess` (archivo oculto):
> ```bash
> unzip -l ../logistika-neubox.zip | grep -E "htaccess|contact.php"
> ```

---

## Paso 2 — Subir a cPanel

1. Entra al panel de Neubox → **cPanel**.
2. Abre **"File Manager" (Administrador de archivos)**.
3. Entra a la carpeta **`public_html`** — es la raíz web de `www.logistika.mx`.
4. **Borra o respalda el mock** que está ahí (el `index.html` de "Home de www.logistika.mx"). Para respaldar: selecciónalo → "Compress" a un zip, o muévelo a una carpeta `_backup/`.
5. Botón **"Upload"** → sube `logistika-neubox.zip`.
6. De vuelta en File Manager, clic derecho en el zip → **"Extract"** dentro de `public_html`.
7. ⚠️ **Muestra los archivos ocultos** para confirmar que subió el `.htaccess`:
   **Settings (arriba a la derecha) → "Show Hidden Files (dotfiles)" → Save.**
   Debes ver `.htaccess` en `public_html`.

Al terminar, `public_html/` debe tener `index.html`, `contact.php`, `.htaccess`, y las carpetas del sitio.

---

## Paso 3 — Configurar `contact.php`

Abre `public_html/contact.php` en File Manager (clic derecho → **"Edit"**) y ajusta el
bloque de **CONFIG** de arriba:

```php
$LEAD_TO   = getenv('LEAD_TO')   ?: 'hola@logistika.mx';       // correo destino (confirmado)
$LEAD_FROM = getenv('LEAD_FROM') ?: 'no-reply@logistika.mx';   // <-- un buzón/alias del dominio
$ALLOWED_ORIGIN = getenv('ALLOWED_ORIGIN') ?: 'https://www.logistika.mx';
```

- **`LEAD_TO`**: a dónde llegan los leads. Confirmado: `hola@logistika.mx`.
- **`LEAD_FROM`**: el remitente. Debe ser un buzón que **exista en el mismo dominio** (ver Paso 4), o el correo cae en spam.
- Guarda (**"Save Changes"**).

No hace falta tocar el rate limit ni la trampa de tiempo: vienen con valores sanos.

---

## Paso 4 — Correo: que el lead llegue y no caiga en spam

**4a. Crea/confirma los buzones** — cPanel → **"Email Accounts"**:
- [ ] Existe el buzón destino (`hola@…`).
- [ ] Existe (o crea) el remitente `no-reply@logistika.mx` (puede ser un alias).

**4b. SPF y DKIM** — cPanel → **"Email Deliverability"**:
- Busca `logistika.mx` en la lista. Si SPF o DKIM salen en rojo/"Problems", pulsa **"Repair"** — Neubox arregla los registros DNS solo.
- Objetivo: SPF y DKIM en **verde**.

**4c. ¿`mail()` o SMTP?** — no lo decides por adelantado, lo pruebas (Paso 6):
- Si el correo **llega a bandeja** con la config actual → `mail()` funciona, listo.
- Si **no llega o cae en spam** → me avisas y cambio `contact.php` a **SMTP** (usa PHPMailer + usuario/contraseña de un buzón). Es un cambio de ~10 min.

---

## Paso 5 — Conectar el formulario (el `.htaccess`)

El formulario del sitio manda a `/api/contact`. El `.htaccess` que ya va incluido
reescribe esa ruta a `contact.php`, así **no se toca el JavaScript**.

- Si Neubox es Apache (o nginx delante de Apache, lo normal en cPanel), **funciona solo**.
- **Si el formulario diera 404** al probar (Paso 6), es señal de que el `.htaccess` no se
  está aplicando (nginx puro). Solución de respaldo: me dices y cambio una línea en
  `app.js` para que mande directo a `/contact.php`. (No lo hago antes porque rompería la
  prueba en Vercel; se hace justo al migrar.)

---

## Paso 6 — Verificar en vivo (checklist)

Desde tu Mac, con el sitio ya subido:

```bash
# 1) El sitio responde en el dominio
curl -sI https://www.logistika.mx/ | head -1          # -> HTTP/... 200

# 2) Es el sitio nuevo, no el mock
curl -s https://www.logistika.mx/ | grep -o "<title>[^<]*</title>"
#    -> debe decir "Foreign Trade & Supply Chain, Managed — logistika Querétaro"

# 3) GEO vivo
curl -sI https://www.logistika.mx/llms.txt | head -1  # -> 200
curl -s  https://www.logistika.mx/robots.txt | grep -c GPTBot   # -> >=1

# 4) El receptor de leads responde
curl -s -X POST https://www.logistika.mx/api/contact \
  -H "Content-Type: application/json" \
  -d '{"company":"Prueba","email":"TUCORREO@gmail.com","stage":"Want to start","message":"prueba de migracion","locale":"es","rendered_at":0}'
#    -> {"status":"ok"}
```

- [ ] El paso 4 devolvió `{"status":"ok"}`.
- [ ] **Llegó el correo** a `LEAD_TO` (revisa bandeja **y** spam).
- [ ] Abre el sitio en el navegador: el botón de WhatsApp aparece, el menú se centra, ES/EN funciona.
- [ ] Manda el formulario **desde el navegador** una vez y confirma que llega.

Si el paso 4 da **404** → aplica el respaldo del Paso 5. Si da **422** → el `stage` no era
válido (usa uno de: `Already importing`, `Want to start`, `Specific problem`, `Outsource`).
Si da **502** → `mail()` falló, pasar a SMTP (Paso 4c).

---

## Paso 7 — Cierre

- [ ] Borra el zip subido y el `_backup/` del mock si ya no lo necesitas.
- [ ] Da de alta el dominio en **Google Search Console** y **Bing Webmaster** y manda el `sitemap.xml` (esto activa el SEO/GEO real; ver `auditoria-logistika.md`, pasos C1).
- [ ] Anota en `history_es.md` / `history.en.md` que logistika ya está en producción en Neubox.

---

## Qué NO hacer

- ❌ No subas `api/`, `.env`, `.venv/`, `*.db`, `tests/`, `node_modules/`. (El `.htaccess`
  bloquea `.env`/`.db`/`.py` por si acaso, pero mejor ni subirlos.)
- ❌ No borres el plan de correo de Neubox: el buzón `@logistika.mx` vive ahí; cancelarlo mata el correo.
- ❌ No pongas `ADMIN_TOKEN` ni contraseñas dentro de archivos servidos por web sin que el `.htaccess` los bloquee.

---

## Si algo sale mal (rollback)

Como el sitio es estático, volver atrás es instantáneo: restaura el mock (o el zip previo)
en `public_html`. Nada se pierde: el repo en GitHub tiene todo, y los leads viejos no
existían en producción todavía.
