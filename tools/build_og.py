#!/usr/bin/env python3
"""
Genera las imágenes Open Graph: la tarjeta que se ve cuando alguien comparte una
liga del sitio por WhatsApp, LinkedIn, Slack o Twitter.

Uso:
    python3 tools/build_og.py

Salida:
    og/<slug>.png   1200×630, una por página

Sin estas imágenes, compartir cualquier liga muestra una tarjeta gris con texto
chico. Con ellas, muestra el título de la página sobre la marca del estudio.
Cuesta un archivo por página y cambia por completo cómo se ve tu sitio cuando
alguien lo reenvía — que es exactamente el momento en que un prospecto decide si
te abre o no.

Los títulos se leen de los generadores, así que una página nueva hereda su
tarjeta sin tocar este archivo.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

W, H = 1200, 630
BLUE = (56, 93, 171)
AMBER = (246, 179, 52)
PAPER = (255, 255, 255)
MUTED = (195, 209, 238)

FONT_SERIF = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
    "/System/Library/Fonts/Supplemental/Georgia.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf",
]
FONT_MONO = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
    "/System/Library/Fonts/Menlo.ttc",
    "/usr/share/fonts/truetype/liberation/LiberationMono-Regular.ttf",
]


def font(paths, size):
    from PIL import ImageFont
    for p in paths:
        if Path(p).exists():
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


def wrap(draw, text, f, max_width):
    words, lines, line = text.split(), [], ""
    for w in words:
        probe = f"{line} {w}".strip()
        if draw.textlength(probe, font=f) <= max_width:
            line = probe
        else:
            if line:
                lines.append(line)
            line = w
    if line:
        lines.append(line)
    return lines


def card(slug: str, kicker: str, title: str) -> None:
    from PIL import Image, ImageDraw

    img = Image.new("RGB", (W, H), BLUE)
    d = ImageDraw.Draw(img)

    pad = 80
    d.rectangle([pad, pad, W - pad, H - pad], outline=AMBER, width=2)

    # Se pega el logotipo real en blanco, no una reconstrucción: la tarjeta
    # social es lo primero que ve un prospecto y la marca tiene que ser la suya.
    mark = ROOT / "img" / "logistika-logo-white.png"
    if mark.exists():
        logo = Image.open(mark).convert("RGBA")
        target_h = 62
        logo = logo.resize((round(logo.width * target_h / logo.height), target_h), Image.LANCZOS)
        img.paste(logo, (pad + 44, pad + 40), logo)
        text_x = pad + 44 + logo.width + 26
    else:
        text_x = pad + 44

    f_kick = font(FONT_MONO, 20)
    d.text((text_x, pad + 58), kicker.upper()[:44], font=f_kick, fill=AMBER)

    # Título: se ajusta el cuerpo hasta que quepa en cuatro líneas
    max_w = W - 2 * pad - 88
    for size in (66, 58, 50, 44, 38):
        f_title = font(FONT_SERIF, size)
        lines = wrap(d, title, f_title, max_w)
        if len(lines) <= 4:
            break
    lh = int(size * 1.22)
    y = pad + 190
    for line in lines[:4]:
        d.text((pad + 44, y), line, font=f_title, fill=PAPER)
        y += lh

    f_foot = font(FONT_MONO, 20)
    d.text((pad + 44, H - pad - 56), "LOGISTIKA · FOREIGN TRADE & SUPPLY CHAIN · QUERÉTARO, MX",
           font=f_foot, fill=MUTED)

    out = ROOT / "og"
    out.mkdir(exist_ok=True)
    img.save(out / f"{slug}.png", "PNG", optimize=True)
    print(f"  og/{slug}.png")


def main() -> None:
    try:
        from PIL import Image  # noqa: F401
    except ImportError:
        print("Falta Pillow.  pip install Pillow")
        sys.exit(1)

    cards = [
        ("home", "Foreign trade · Supply chain",
         "Seven vendors. One point of control."),
        ("about", "Who does the work",
         "Fifteen years inside the operation."),
        ("check", "Entry product",
         "Ten days to find where your money is going."),
        ("levels", "Three levels",
         "Start, manage or outsource the whole function."),
        ("privacy", "Legal", "Privacy notice"),
        ("terms", "Legal", "Terms of use"),
    ]


    for slug, kicker, title in cards:
        card(slug, kicker, title)

    print(f"\n{len(cards)} tarjetas generadas.")


if __name__ == "__main__":
    main()
