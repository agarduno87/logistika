# Publicar logistika en GitHub Pages

## Los comandos

    cd /Users/antoniogarduno/Downloads/logistika
    git init && git add . && git commit -m "Sitio de logistika"
    git branch -M main
    git remote add origin https://github.com/agarduno87/logistika.git
    git push -u origin main

Crea el repositorio antes en github.com, **público** (Pages en repos privados
requiere plan de pago).

Después: **Settings → Pages → Source: Deploy from a branch → Branch `main`,
carpeta `/docs`**. En dos o tres minutos queda en:

    https://agarduno87.github.io/logistika/

## Regenerar docs/ después de cambiar contenido

    python3 tools/build_pages.py --base /logistika --mailto hola@logistika.mx

El `--base` es obligatorio y tiene que coincidir con el nombre del repositorio.
Sin él, todas las rutas apuntan a la raíz del usuario y el sitio sale sin diseño.

Cuando conecten el dominio propio, cambia a:

    python3 tools/build_pages.py --domain www.logistika.mx --mailto hola@logistika.mx

Eso quita el prefijo y escribe el archivo CNAME.

## Lo que NO funciona en GitHub Pages

**El formulario no guarda leads.** Pages solo sirve archivos: no corre Python,
así que `/api/contact` no existe. El envío abre el correo del visitante con los
datos ya escritos. Funciona, pero nadie queda registrado en base de datos.

**No hay Content-Security-Policy.** Viaja por cabecera HTTP y Pages no permite
cabeceras propias. Por eso Pages sirve para pruebas y no como destino final.

**El backend sigue en el repositorio** (`api/`, `tools/`, `tests/`) pero NO se
publica: el generador los excluye de `docs/`. Cuando el sitio se mueva a un
servidor real, `bash run.sh` lo levanta completo con formulario y base de datos.

## Verificado

Servido exactamente como lo hace Pages, bajo el subdirectorio `/logistika/`:
portada, About, aviso de privacidad, términos y la página 404 cargan sin un solo
recurso roto; el cambio de idioma aplica; el riel arma sus siete marcas; y no
desborda a 390 px.
