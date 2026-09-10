# Auditoría SEO + GEO — logistika

- **Fecha:** 2026-09-09 (2ª pasada, tras aplicar fixes)
- **URL auditada:** https://logistika-beta.vercel.app (deploy de pruebas)
- **Dominio de producción (aún no en vivo):** https://www.logistika.mx
- **Plataforma:** sitio estático (HTML/CSS/JS) + backend FastAPI (dev) → producción PHP en Neubox
- **Salud SEO:** 80/100 🟢 (metadatos y lastmod ya corregidos; solo falta publicar el dominio)
- **Salud GEO:** 60/100 🟡 (structured data + llms.txt + robots pro-IA listos; falta dominio indexable en vivo)
- **Pruebas:** 38 backend + 30 navegador en verde; `contact.php` validado con PHP 8.5.

### Cambios aplicados desde la 1ª pasada
- ✅ title 73→**59** car.; description 208→**143** car.
- ✅ sitemap con **lastmod** real por página (4/4).
- ✅ GEO: `llms.txt`, `robots.txt` pro-IA y nodo `WebSite` en el JSON-LD (vivos).
- ✅ `contact.php` endurecido (honeypot + trampa de tiempo + rate limit + validación +
  CORS cerrado + secretos por env + logging anonimizado) y probado funcionalmente.

---

## 1. Resumen ejecutivo

Lo bueno: la base técnica es **sólida** — JSON-LD rico (ProfessionalService + 6 Service
+ FAQPage + WebSite), hreflang ES/EN, canonical, Open Graph, y ~1,840 palabras en la
portada. Con esta auditoría se agregó lo que faltaba de GEO: `llms.txt`, `robots.txt`
pro-IA y el nodo `WebSite`.

Los tres problemas de fondo:

1. **El sitio no vive en su dominio.** Sirve desde `logistika-beta.vercel.app`, pero
   `canonical`, `sitemap` y `JSON-LD` apuntan a `www.logistika.mx`, que aún no responde.
   Hasta resolverlo, ni Google ni las IA pueden indexar/citar el dominio real.
2. **Los leads no persisten en el deploy actual** (disco efímero de Vercel). El plan de
   producción es PHP + correo en Neubox (`contact.php` ya está listo y endurecido).
3. **Metadatos un poco largos** (description 208 car., title 73 car.) → se truncan en el
   buscador.

---

## 2. Tabla de hallazgos

| # | Sev | Hallazgo | Evidencia |
|---|-----|----------|-----------|
| 1 | 🔴 | Sitio servido desde `vercel.app`, no desde `logistika.mx` | canonical y sitemap apuntan a `www.logistika.mx`; ese host aún no sirve |
| 2 | 🔴 | Leads no persisten en Vercel (SQLite en disco efímero) | prueba: lead guardado desaparece en cold start; ver errores propios #8 |
| 3 | ✅ | ~~Meta description 208 caracteres~~ → **143** (resuelto) | live → 143 |
| 4 | ✅ | ~~`<title>` 73 caracteres~~ → **59** (resuelto) | live → 59 |
| 5 | ✅ | ~~Sitemap sin `lastmod`~~ → **4/4 con fecha real** (resuelto) | `grep -c lastmod` → 4 |
| 6 | 🟡 | Sin Search Console / Bing Webmaster / analítica | requieren cuentas del cliente |
| 7 | 🟡 | Presencia en Bing sin confirmar (ChatGPT usa Bing) | depende de que el dominio esté vivo |
| 8 | 🟡 | Correo de leads `.mx` vs `.com.mx` sin confirmar | sitio usa `logistika.mx`; correo dado fue `hola@logistika.com.mx` |

---

## 3. Diagnóstico GEO (para que las IA citen el sitio)

- ✅ **JSON-LD** rico y válido — las IA entienden qué es logistika, servicios y FAQ.
- ✅ **llms.txt** publicado con datos verificados (qué es/qué no es, servicios, niveles,
  fundadora, la frontera de agente aduanal). Solo espeja el sitio; no inventa nada.
- ✅ **robots.txt pro-IA** — permite GPTBot, OAI-SearchBot, ChatGPT-User, PerplexityBot,
  ClaudeBot, Claude-Web, Google-Extended; bloquea los de solo-entrenamiento.
- ❌ **Bloqueo real:** las IA necesitan una URL viva e indexable. Mientras el dominio no
  responda, no hay nada que citar. Es el paso 1 del wizard.

---

## 4. SERP y competencia

Análisis pleno pendiente hasta que el dominio esté en vivo (antes no hay nada que
posicionar). Criterio de la metodología: **no pelear términos genéricos gigantes**
("comercio exterior" a secas). El ángulo ganable de logistika:

- Nicho + localidad: *departamento de comercio exterior externo* / *health check de
  importación* + **Querétaro / Bajío**.
- Diferenciador claro y honesto: **coordina y audita al agente aduanal, no lo reemplaza**
  — copy que además evita competir donde no debe.

---

## 5. Wizard de ejecución

### Pasos de NUESTRO lado (ejecutables)

**PASO 1 — Publicar el sitio en `www.logistika.mx`.** 🔴
- Problema: el sitio vive en `vercel.app`; el dominio real no sirve.
- Cómo: subir el estático a Neubox (o apuntar DNS), con `www` → apex resuelto y HTTPS.
- Verificar: `curl -sI https://www.logistika.mx/ | head -1` → `200`.

**PASO 2 — Formulario de leads en Neubox (PHP + correo).** 🟠 CÓDIGO LISTO Y PROBADO
- `contact.php` ya está escrito, endurecido y **validado con PHP 8.5** (honeypot, trampa de
  tiempo, rate limit, validación y logging anonimizado dan los códigos correctos).
- Falta solo: **subirlo a Neubox**, apuntar el formulario a él y **confirmar el correo
  destino** (C3) y el modo de envío de Neubox (C4).
- Verificar en vivo: `curl -s -X POST https://www.logistika.mx/contact.php -H "Content-Type: application/json" -d '{"company":"Prueba","email":"t@t.com","stage":"Want to start","message":"hola","locale":"es","rendered_at":0}'` → `{"status":"ok"}` y el correo llega.

**PASO 3 — Acortar metadatos.** ✅ HECHO
- title 59 car., description 143 car. (verificado en vivo).

**PASO 4 — `lastmod` estable en el sitemap.** ✅ HECHO
- 4/4 URLs con fecha real (`grep -c lastmod sitemap.xml` → 4).

### Pasos del CLIENTE (pendientes, requieren cuentas/datos)

- **C1** — Alta en Google Search Console + Bing Webmaster (verificar dominio, mandar sitemap).
- **C2** — Analítica (Plausible/GA4) — decisión de privacidad del cliente.
- **C3** — Confirmar correo destino de leads (`.mx` vs `.com.mx`) y que el buzón exista.
- **C4** — Cómo envía correo Neubox: ¿`mail()` o SMTP autenticado? SPF/DKIM del dominio.
- **C5** — Textos que Adriana iba a mandar (nunca llegaron).
- **C6** — Validar el modelo de precios con horas reales (ver nota de viabilidad).

---

## 6. Roadmap

- **0–30 días (fuego):** PASO 1 (dominio vivo) + PASO 2 (leads por correo) + C1 (Search
  Console/Bing) + PASOS 3–4 (metadatos, lastmod).
- **30–90 días:** C2 analítica; primeras 2–3 páginas/artículos de contenido local
  (health check, importar a México, errores comunes) enlazando al formulario.
- **90–180 días:** monitoreo GEO (¿citan `logistika.mx`?), afinar según qué queries traen
  tráfico, decidir blog sostenido.

---

## 7. Queries objetivo (sembrado) y no objetivo

**Sí:** "departamento de comercio exterior externo Querétaro", "auditoría de importación
Bajío", "health check cadena de suministro México", "cómo saber si pago de más en
importaciones".
**No (genéricas gigantes):** "comercio exterior", "logística", "aduanas" a secas.

---

## 8. Lo que YA está bien (no tocar)

- JSON-LD rico y válido (ProfessionalService + 6 Service + FAQPage + WebSite).
- hreflang ES/EN, canonical, Open Graph completos.
- Portada con ~1,840 palabras (contenido profundo).
- Defensa en profundidad del formulario (honeypot + trampa de tiempo + rate limit +
  validación + CORS cerrado + secretos por env + logging anonimizado), ahora también en PHP.
- `llms.txt` + `robots.txt` pro-IA (agregados en esta auditoría).
