#!/usr/bin/env python3
"""
Procesa el retrato de Adriana para la pagina About.

Uso, cuando tengas la foto:
    cp <tu-foto.jpg> assets/portraits/adriana.jpg
    python3 tools/build_portraits.py
    python3 tools/build_about.py     # vuelve a generar la pagina con la foto

Salida (en img/):
    adriana-culebro-640.jpg / .webp
    adriana-culebro-320.jpg / .webp

Se exporta WebP y JPEG: el navegador toma el WebP, que pesa la mitad, y el JPEG
queda de respaldo. Dos anchos para no servir 640 px a una tarjeta de 320.

Si el encuadre no queda, ajusta FOCUS: son centro X, centro Y y lado del
recorte, en proporcion del original. Para un retrato de cuerpo entero baja el
lado a 0.5 y sube el centro Y a 0.3 para acercarte a la cara.
"""
from __future__ import annotations
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "img"
SLUG = "adriana-culebro"
WIDTHS = (640, 320)
FOCUS = (0.52, 0.26, 0.85)   # centro X, centro Y, lado del recorte


def process(src: Path) -> None:
    from PIL import Image

    im = Image.open(src)
    if im.mode in ("RGBA", "LA", "P"):
        bg = Image.new("RGB", im.size, (255, 255, 255))
        im = im.convert("RGBA")
        bg.paste(im, mask=im.split()[-1])
        im = bg
    else:
        im = im.convert("RGB")

    cx, cy, ratio = FOCUS
    w, h = im.size
    side = int(min(w, h) * ratio)
    left = int(max(0, min(w - side, cx * w - side / 2)))
    top = int(max(0, min(h - side, cy * h - side / 2)))
    im = im.crop((left, top, left + side, top + side))

    OUT.mkdir(exist_ok=True)
    for width in WIDTHS:
        r = im.resize((width, width), Image.LANCZOS)
        r.save(OUT / f"{SLUG}-{width}.jpg", "JPEG", quality=84, optimize=True, progressive=True)
        r.save(OUT / f"{SLUG}-{width}.webp", "WEBP", quality=82, method=6)
        print(f"  img/{SLUG}-{width}.jpg  +  .webp")


def main() -> None:
    args = sys.argv[1:]
    if args:
        src = Path(args[0])
    else:
        folder = ROOT / "assets" / "portraits"
        candidates = sorted(p for p in folder.glob("*") if p.suffix.lower() in
                            (".jpg", ".jpeg", ".png", ".webp")) if folder.exists() else []
        if not candidates:
            print("No encontre ninguna foto.")
            print("Copia el retrato a assets/portraits/ y vuelve a correr esto,")
            print("o pasa la ruta:  python3 tools/build_portraits.py ruta/foto.jpg")
            sys.exit(1)
        src = candidates[0]

    if not src.exists():
        print(f"No encontre {src}")
        sys.exit(1)
    process(src)
    print("\nListo. Ahora corre:  python3 tools/build_about.py")


if __name__ == "__main__":
    main()
