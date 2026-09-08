#!/usr/bin/env python3
"""
Genera los iconos del sitio a partir del icono real de la marca
(assets/logo-icon.png: la "L" trazada como ruta con dos waypoints ambar).

Uso:
    pip install Pillow
    python3 tools/build_favicon.py

Salida, en la raiz:
    favicon.svg           el que usan los navegadores modernos
    favicon.ico           16/32/48 px, el que el navegador pide solo
    apple-touch-icon.png  180x180, "Anadir a inicio" en iOS
    icon-192.png, icon-512.png   Android / PWA
    site.webmanifest

A 16 px el trazo del icono se convierte en una mancha, asi que por debajo de
32 px se dibuja un fondo azul solido con el icono en blanco recortado: la marca
sigue siendo reconocible en la pestana, que es lo unico que importa a ese tamano.
"""
from __future__ import annotations
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "assets" / "logo-icon.png"
BLUE = (56, 93, 171)
AMBER = (246, 179, 52)
PAPER = (255, 255, 255)

SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" role="img" aria-label="logistika">
  <title>logistika</title>
  <rect width="64" height="64" rx="12" fill="#385DAB"/>
  <path d="M22 14 v26 a4 4 0 0 0 4 4 h20" fill="none" stroke="#FFFFFF"
        stroke-width="7" stroke-linecap="round" stroke-linejoin="round"/>
  <circle cx="17" cy="47" r="4" fill="#F6B334"/>
  <circle cx="34" cy="51" r="4" fill="#F6B334"/>
</svg>
"""

MANIFEST = """{
  "name": "logistika",
  "short_name": "logistika",
  "icons": [
    { "src": "/icon-192.png", "sizes": "192x192", "type": "image/png" },
    { "src": "/icon-512.png", "sizes": "512x512", "type": "image/png" }
  ],
  "theme_color": "#385DAB",
  "background_color": "#FFFFFF",
  "display": "browser"
}
"""


def draw(size: int):
    """Dibuja a 4x y reduce: a tamanos chicos el antialiasing es lo que
    separa una marca legible de una mancha azul."""
    from PIL import Image, ImageOps

    scale = 4
    s = size * scale
    icon = Image.open(SRC).convert("RGBA")
    bbox = icon.split()[-1].getbbox()
    if bbox:
        icon = icon.crop(bbox)

    canvas = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    radius = int(s * (0.19 if size >= 32 else 0.10))

    from PIL import ImageDraw
    d = ImageDraw.Draw(canvas)
    d.rounded_rectangle([0, 0, s - 1, s - 1], radius=radius, fill=BLUE)

    pad = int(s * (0.20 if size >= 32 else 0.14))
    box = s - pad * 2
    w, h = icon.size
    ratio = min(box / w, box / h)
    icon = icon.resize((max(1, int(w * ratio)), max(1, int(h * ratio))), Image.LANCZOS)

    # El icono viene azul sobre blanco: se recolorea a blanco para que contraste
    # sobre el cuadro azul, conservando los puntos ambar.
    px = icon.load()
    for y in range(icon.size[1]):
        for x in range(icon.size[0]):
            r, g, b, a = px[x, y]
            if a < 30:
                continue
            if abs(r - AMBER[0]) < 60 and abs(g - AMBER[1]) < 60 and b < 130:
                px[x, y] = AMBER + (a,)
            else:
                px[x, y] = PAPER + (a,)

    canvas.alpha_composite(icon, ((s - icon.size[0]) // 2, (s - icon.size[1]) // 2))
    return canvas.resize((size, size), Image.LANCZOS)


def main() -> None:
    (ROOT / "favicon.svg").write_text(SVG, encoding="utf-8")
    (ROOT / "site.webmanifest").write_text(MANIFEST, encoding="utf-8")
    print("  favicon.svg")
    print("  site.webmanifest")

    try:
        from PIL import Image  # noqa: F401
    except ImportError:
        print("\n  Pillow no esta instalado: se omitieron los PNG/ICO.")
        print("  pip install Pillow  y vuelve a correr esto.")
        sys.exit(0)

    if not SRC.exists():
        print(f"\n  Falta {SRC}. Copia ahi el icono de la marca.")
        sys.exit(1)

    # De mayor a menor: Pillow toma la primera como base y si es la chica
    # escala hacia arriba y las grandes salen borrosas.
    sizes = [48, 32, 16]
    frames = [draw(n) for n in sizes]
    frames[0].save(ROOT / "favicon.ico", format="ICO",
                   sizes=[(n, n) for n in sizes], append_images=frames[1:])
    print("  favicon.ico (48, 32, 16)")

    for name, size in (("apple-touch-icon.png", 180), ("icon-192.png", 192), ("icon-512.png", 512)):
        draw(size).save(ROOT / name, format="PNG", optimize=True)
        print(f"  {name}")
    print("\nIconos generados.")


if __name__ == "__main__":
    main()
