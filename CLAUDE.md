# logistika

Empresa de comercio exterior y logística de Adriana Culebro Jiménez. Marca en
minúsculas, sin acento: **logistika**. Base en Querétaro.

## Estado

- Sitio estático completo, inglés con español completo (219 claves de traducción)
- Backend FastAPI con SQLite para el formulario
- 38 pruebas de backend, 30 de navegador
- Página About con la semblanza y el retrato de Adriana
- Aviso de privacidad y términos
- `logistika-precios.xlsx`: modelo de precios con 8 hojas

## Hosting y dominio

**Neubox, plan "SELL IT", MXN 1,099 al año, vence 17/10/2026.**
Es hosting **compartido con cPanel**: Apache, PHP y MySQL. **No corre Python.**

El dominio `logistika.mx` está registrado desde 2022 y vence el 05/06/2027, en
la misma cuenta de Neubox junto con amoragranel.com, granelco.com y
granelco.com.mx.

Consecuencia directa: **el backend de FastAPI no puede correr ahí.** El sitio se
publica estático y el formulario necesita otra solución — un script PHP en el
mismo cPanel, un servicio externo de formularios, o mover el backend a un VPS.

Hubo un intento en Vercel que falló con `FUNCTION_INVOCATION_FAILED`: `init_db()`
corría al importar el módulo y el disco de Vercel es de solo lectura. Ya está
corregido — la app degrada en vez de morir — pero el formulario sigue sin
guardar leads en cualquier entorno sin disco escribible.

## Marca

Azul `#385DAB`, ámbar `#F6B334`, periwinkle `#8292CA`. El ícono es una "L"
trazada como ruta con dos puntos ámbar tipo waypoint.

**El ámbar y el periwinkle no sirven para texto pequeño.** El ámbar sobre blanco
da 3.85:1 y el periwinkle 1.6:1. Se usan en fondos, filetes y titulares. Para
texto enlazado hay una versión oscurecida.

## Fronteras que el sitio declara y no se pueden cruzar

**logistika no es agencia aduanal.** En México el despacho aduanero está
reservado por ley a un agente aduanal con patente. El sitio coordina, supervisa
y audita al agente, pero no despacha ni firma pedimentos. Está escrito en los
términos y es argumento de venta, no letra chica.

**Bosch, Benteler, Tenneco, Geodis y UTI fueron clientes o empleadores de
Adriana, no de logistika.** Publicarlos como referencia propia sería engañoso.
Hay una prueba automatizada que falla si esos nombres aparecen en el sitio.

## Trampas de este proyecto

**Rutas absolutas y subdirectorios.** Igual que en techStudio. Para GitHub Pages
se usa `tools/build_pages.py --base /logistika`, que reescribe rutas —incluidas
las de `srcset`, que van aparte— y deja todo en `docs/`.

**El diccionario de i18n.** `i18n.js` arma la ruta del diccionario en tiempo de
ejecución, así que la reescritura de atributos no la alcanza: hay que parchear
el literal. Sin eso, el selector de idioma cambia y no pasa nada, porque el
diccionario da 404 en silencio.

**Las claves de traducción se derivan del texto en inglés.** Si se cambia una
frase, la clave cambia y esa línea deja de traducirse. Hay una prueba que lo
detecta en vez de dejar la página medio traducida.

**Los `value` de los `<option>` van siempre en inglés.** El idioma cambia la
etiqueta visible, nunca el valor enviado. Si se traduce el `value`, una visita
en español deja de poder enviar el formulario.

**El formulario tiene un campo trampa.** Se accede con `f.elements.website`, no
con `f.website`: el acceso por nombre directo no está garantizado y donde
devuelve undefined la trampa deja de existir sin que nadie lo note.

## Dependencias

`api/requirements.txt` tiene lo de producción. Las **pruebas** necesitan
`api/requirements-dev.txt`, que agrega httpx —el TestClient de FastAPI lo pide y
FastAPI no lo trae—, Pillow y openpyxl.

## Base de leads

`api/leads.db`. Columnas: id, created_at, company, email, **stage**, message,
locale, ip_prefix. `stage` guarda siempre el valor en inglés. `ip_prefix` va
truncado terminando en `.0` porque el aviso de privacidad lo promete.

## Pendientes

- Decidir si se lanza el nivel PARTNER. El modelo de precios dice que no cabe:
  con 12 h/semana no entra ni un cliente MANAGE a 12 embarques al mes
- Definir bandas de precio y aportar casos con números
- Cambios de redacción que Adriana iba a mandar en un Word
- Resolver el formulario en hosting compartido
- Editor de contenido para que Adriana edite sin tocar código
