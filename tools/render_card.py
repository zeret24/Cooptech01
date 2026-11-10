# -*- coding: utf-8 -*-
"""Сборка карточки товара «Термокружка» 900x1200 (растр + SVG-исходник)."""
import base64
import io
import os
import sys
from collections import Counter

from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H = 900, 1200
S = 2                      # суперсэмплинг для гладких краёв
BG = (244, 246, 249)       # светлый фон фрейма
NAVY = (23, 37, 84)        # тёмно-синий #172554
BLUE = (59, 130, 246)      # #3B82F6
WHITE = (255, 255, 255)

FONT_BOLD = r"C:\Windows\Fonts\arialbd.ttf"


def remove_plain_background(im, tol=26):
    """Убирает однотонный (светлый) фон заливкой от краёв."""
    im = im.convert("RGB")
    w, h = im.size
    px = im.load()
    edge = [px[x, 0] for x in range(0, w, max(1, w // 40))]
    edge += [px[x, h - 1] for x in range(0, w, max(1, w // 40))]
    edge += [px[0, y] for y in range(0, h, max(1, h // 40))]
    edge += [px[w - 1, y] for y in range(0, h, max(1, h // 40))]
    bg = Counter(edge).most_common(1)[0][0]

    mask = Image.new("L", (w, h), 0)
    mpx = mask.load()
    stack = [(x, y) for x in range(w) for y in (0, h - 1)] + \
            [(x, y) for y in range(h) for x in (0, w - 1)]
    seen = bytearray(w * h)
    while stack:
        x, y = stack.pop()
        if x < 0 or y < 0 or x >= w or y >= h:
            continue
        i = y * w + x
        if seen[i]:
            continue
        r, g, b = px[x, y]
        if abs(r - bg[0]) + abs(g - bg[1]) + abs(b - bg[2]) > tol * 3:
            continue
        seen[i] = 1
        mpx[x, y] = 255
        stack += [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]

    mask = mask.filter(ImageFilter.GaussianBlur(1.2))
    out = im.convert("RGBA")
    out.putalpha(Image.eval(mask, lambda v: 255 - v))
    return out


def autocrop(im, pad=4):
    bbox = im.getchannel("A").point(lambda v: 255 if v > 12 else 0).getbbox()
    if not bbox:
        return im
    x0, y0, x1, y1 = bbox
    return im.crop((max(0, x0 - pad), max(0, y0 - pad),
                    min(im.width, x1 + pad), min(im.height, y1 + pad)))


def adjust(im, brightness=1.03, contrast=1.05, color=1.04):
    from PIL import ImageEnhance
    im = ImageEnhance.Brightness(im).enhance(brightness)
    im = ImageEnhance.Contrast(im).enhance(contrast)
    im = ImageEnhance.Color(im).enhance(color)
    return im


def draw_badge(img, x, y):
    """Плашка 300x60, скругление 20, тёмно-синяя, белый текст по центру."""
    d = ImageDraw.Draw(img)
    shadow = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(shadow).rounded_rectangle(
        [(x + 1) * S, (y + 4) * S, (x + 301) * S, (y + 64) * S], radius=20 * S,
        fill=(23, 37, 84, 45))
    img.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(8 * S)))

    d.rounded_rectangle([x * S, y * S, (x + 300) * S, (y + 60) * S],
                        radius=20 * S, fill=NAVY + (255,))

    text = "Держит тепло 12 часов"
    size = 20
    while size > 10:
        font = ImageFont.truetype(FONT_BOLD, size * S)
        box = d.textbbox((0, 0), text, font=font)
        if (box[2] - box[0]) <= 300 * S - 36 * S:
            break
        size -= 1
    tw, th = box[2] - box[0], box[3] - box[1]
    d.text((x * S + (300 * S - tw) / 2 - box[0],
            y * S + (60 * S - th) / 2 - box[1]), text, font=font, fill=WHITE + (255,))


def draw_thermometer(img, cx, cy, s=60):
    """Иконка термометра из простых фигур (круг + скруглённый прямоугольник + эллипс)."""
    shadow = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(shadow).ellipse(
        [(cx - 30 + 1) * S, (cy - 30 + 4) * S, (cx + 30 + 1) * S, (cy + 30 + 4) * S],
        fill=(23, 37, 84, 45))
    img.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(8 * S)))

    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    k = s / 60.0

    def X(v): return (cx - 30 * k + v * k) * S
    def Y(v): return (cy - 30 * k + v * k) * S
    def B(v): return v * k * S

    d.ellipse([X(0), Y(0), X(60), Y(60)], fill=NAVY + (255,))
    d.rounded_rectangle([X(23), Y(9), X(33), Y(39)], radius=B(5), fill=WHITE + (255,))
    d.ellipse([X(19), Y(33), X(37), Y(51)], fill=WHITE + (255,))
    d.rounded_rectangle([X(26), Y(16), X(30), Y(38)], radius=B(2), fill=BLUE + (255,))
    d.ellipse([X(23.5), Y(37.5), X(32.5), Y(46.5)], fill=BLUE + (255,))
    for yy in (16, 22, 28, 34):
        d.line([X(36), Y(yy), X(40), Y(yy)], fill=WHITE + (255,), width=max(2, int(B(2))))
    img.alpha_composite(layer)


def build(photo_path, outdir, scale=0.78, y_shift=0,
          brightness=1.03, contrast=1.05, color=1.04):
    photo = Image.open(photo_path).convert("RGBA")
    photo = remove_plain_background(photo)
    photo = autocrop(photo)
    photo = adjust(photo, brightness, contrast, color)

    target_h = int(H * scale)
    ratio = target_h / photo.height
    photo = photo.resize((max(1, int(photo.width * ratio)), target_h), Image.LANCZOS)
    photo = photo.resize((photo.width * S, photo.height * S), Image.LANCZOS)

    canvas = Image.new("RGBA", (W * S, H * S), BG + (255,))

    # мягкий светлый ореол по центру
    glow = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    ImageDraw.Draw(glow).ellipse([W * 0.20 * S, H * 0.22 * S, W * 0.80 * S, H * 0.92 * S],
                                 fill=(255, 255, 255, 150))
    canvas.alpha_composite(glow.filter(ImageFilter.GaussianBlur(70 * S)))

    px = (W * S - photo.width) // 2
    py = int((H * S - photo.height) / 2 + y_shift * S)

    # тень под товаром
    shadow = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    ImageDraw.Draw(shadow).ellipse(
        [px + photo.width * 0.16, py + photo.height - 26 * S,
         px + photo.width * 0.84, py + photo.height + 10 * S],
        fill=(23, 37, 84, 55))
    canvas.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(16 * S)))

    canvas.alpha_composite(photo, (px, py))

    draw_thermometer(canvas, 60 + 300 + 16 + 30, 60 + 30)
    draw_badge(canvas, 60, 60)

    card = canvas.resize((W, H), Image.LANCZOS).convert("RGB")
    os.makedirs(outdir, exist_ok=True)
    jpg = os.path.join(outdir, "kartochka_termokruzhka.jpg")
    png = os.path.join(outdir, "kartochka_termokruzhka.png")
    card.save(jpg, quality=90, optimize=True, progressive=True)
    card.save(png, optimize=True)
    return card, jpg, png, photo


if __name__ == "__main__":
    photo_path = sys.argv[1]
    outdir = sys.argv[2] if len(sys.argv) > 2 else os.path.dirname(os.path.abspath(__file__))
    scale = float(sys.argv[3]) if len(sys.argv) > 3 else 0.78
    y_shift = int(sys.argv[4]) if len(sys.argv) > 4 else 0
    card, jpg, png, ph = build(photo_path, outdir, scale=scale, y_shift=y_shift)
    print("JPG", os.path.getsize(jpg), "PNG", os.path.getsize(png))
