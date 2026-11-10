# -*- coding: utf-8 -*-
"""Создаёт kartochka.svg — исходник карточки 900x1200 со слоями как в Figma."""
import base64
import io
import os
import sys

from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from render_card import remove_plain_background, autocrop, adjust  # noqa: E402

W, H = 900, 1200
BG = "#F4F6F9"
NAVY = "#172554"
BLUE = "#3B82F6"


def photo_png_b64(path, target_h=936):
    im = Image.open(path).convert("RGBA")
    im = remove_plain_background(im)
    im = autocrop(im)
    im = adjust(im)
    r = target_h / im.height
    im = im.resize((max(1, int(im.width * r)), target_h), Image.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, "PNG", optimize=True)
    return base64.b64encode(buf.getvalue()).decode(), im.size


def build_svg(photo_path, out_path, y_off=20):
    b64, (pw, ph) = photo_png_b64(photo_path)
    px = (W - pw) / 2
    py = (H - ph) / 2 + y_off

    svg = f'''<svg width="{W}" height="{H}" viewBox="0 0 {W} {H}" fill="none" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink">
  <title>Карточка товара «Термокружка» 900×1200</title>
  <desc>Урок 21. Компьютерная графика. Figma: растровое фото + векторная плашка и иконка.</desc>
  <defs>
    <filter id="softShadow" x="-30%" y="-60%" width="160%" height="260%">
      <feGaussianBlur stdDeviation="14"/>
    </filter>
    <filter id="softGlow" x="-40%" y="-40%" width="180%" height="180%">
      <feGaussianBlur stdDeviation="60"/>
    </filter>
  </defs>

  <!-- ===== Фрейм 900 x 1200 ===== -->
  <g id="Frame_900x1200">
    <rect id="Background" width="{W}" height="{H}" fill="{BG}"/>

    <!-- мягкий светлый ореол на фоне -->
    <ellipse id="Glow" cx="{W/2}" cy="660" rx="270" ry="400" fill="#FFFFFF" opacity="0.75" filter="url(#softGlow)"/>

    <!-- тень под товаром -->
    <ellipse id="Product_Shadow" cx="{W/2}" cy="{py + ph - 8:.1f}" rx="{pw * 0.34:.1f}" ry="14"
             fill="{NAVY}" opacity="0.22" filter="url(#softShadow)"/>

    <!-- ===== Растровое изображение (фотография) ===== -->
    <image id="Photo" x="{px:.1f}" y="{py:.1f}" width="{pw}" height="{ph}"
           xlink:href="data:image/png;base64,{b64}"/>

    <!-- ===== Векторные элементы ===== -->
    <g id="Badge_Group">
      <!-- Плашка 300 x 60, скругление 20 -->
      <rect id="Badge" x="60" y="60" width="300" height="60" rx="20" fill="{NAVY}"/>
      <text id="Badge_Text" x="210" y="98" fill="#FFFFFF" font-family="Arial, Helvetica, sans-serif"
            font-size="20" font-weight="bold" text-anchor="middle">Держит тепло 12 часов</text>
    </g>

    <!-- Иконка термометра: круг + скруглённый прямоугольник + эллипс -->
    <g id="Thermometer_Icon" transform="translate(376, 60)">
      <circle cx="30" cy="30" r="30" fill="{NAVY}"/>
      <rect x="23" y="9" width="10" height="30" rx="5" fill="#FFFFFF"/>
      <circle cx="28" cy="42" r="9" fill="#FFFFFF"/>
      <rect x="26" y="16" width="4" height="22" rx="2" fill="{BLUE}"/>
      <circle cx="28" cy="42" r="4.5" fill="{BLUE}"/>
      <line x1="36" y1="16" x2="40" y2="16" stroke="#FFFFFF" stroke-width="2" stroke-linecap="round"/>
      <line x1="36" y1="22" x2="40" y2="22" stroke="#FFFFFF" stroke-width="2" stroke-linecap="round"/>
      <line x1="36" y1="28" x2="40" y2="28" stroke="#FFFFFF" stroke-width="2" stroke-linecap="round"/>
      <line x1="36" y1="34" x2="40" y2="34" stroke="#FFFFFF" stroke-width="2" stroke-linecap="round"/>
    </g>
  </g>
</svg>
'''
    open(out_path, "w", encoding="utf-8").write(svg)
    return out_path, os.path.getsize(out_path)


if __name__ == "__main__":
    photo_path = sys.argv[1]
    out = sys.argv[2] if len(sys.argv) > 2 else "kartochka.svg"
    print(build_svg(photo_path, out))
