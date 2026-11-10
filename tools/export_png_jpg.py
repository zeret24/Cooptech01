# -*- coding: utf-8 -*-
"""Экспорт kartochka.svg в PNG (Chrome headless) и JPG (Pillow)."""
import os
import subprocess
import sys
import tempfile

from PIL import Image

CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"


def export(svg_path, outdir):
    svg_path = os.path.abspath(svg_path)
    png = os.path.abspath(os.path.join(outdir, "kartochka_termokruzhka.png"))
    jpg = os.path.abspath(os.path.join(outdir, "kartochka_termokruzhka.jpg"))

    profile = tempfile.mkdtemp(prefix="chr_")
    cmd = [CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars",
           "--force-device-scale-factor=1", "--window-size=900,1200",
           "--default-background-color=00000000",
           "--user-data-dir=" + profile,
           "--screenshot=" + png,
           "file:///" + svg_path.replace("\\", "/")]
    subprocess.run(cmd, check=True, capture_output=True, timeout=120)

    im = Image.open(png)
    if im.size != (900, 1200):
        im = im.resize((900, 1200), Image.LANCZOS)
        im.save(png, optimize=True)
    im.convert("RGB").save(jpg, quality=90, optimize=True, progressive=True)
    return png, jpg


if __name__ == "__main__":
    svg = sys.argv[1]
    outdir = sys.argv[2] if len(sys.argv) > 2 else "."
    os.makedirs(outdir, exist_ok=True)
    png, jpg = export(svg, outdir)
    print("PNG", os.path.getsize(png), "JPG", os.path.getsize(jpg))
