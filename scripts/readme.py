"""Erzeugt README.md aus src/readme.md.

Platzhalter:
    {{picture:NAME}}  -> <picture> mit assets/NAME-dark.svg / -light.svg,
                         Fallback-<img> ist die Dark-Variante (CLAUDE.md, Regel 5).
                         Der Alt-Text kommt aus dem aria-label der Grafik, damit
                         er immer zum Inhalt passt (z. B. nach Skill-Änderungen).

Wird von build.py aufgerufen. Einzeln: python3 scripts/readme.py
"""

import html
import re
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "src" / "readme.md"
OUT = ROOT / "README.md"

PICTURE = """<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="assets/{name}-dark.svg">
    <source media="(prefers-color-scheme: light)" srcset="assets/{name}-light.svg">
    <img src="assets/{name}-dark.svg" width="{width}" alt="{alt}">
  </picture>
</p>"""


def picture(name):
    dark = ROOT / "assets" / f"{name}-dark.svg"
    if not dark.exists() or not (ROOT / "assets" / f"{name}-light.svg").exists():
        raise SystemExit(f"README: Grafik '{name}' fehlt in assets/ (dark und light nötig)")
    root = ET.parse(dark).getroot()
    alt = root.get("aria-label")
    if not alt:
        raise SystemExit(f"README: {dark.name} hat kein aria-label für den Alt-Text")
    width = root.get("viewBox").split()[2]
    return PICTURE.format(name=name, width=width, alt=html.escape(alt, quote=True))


def build():
    text = SOURCE.read_text(encoding="utf-8")
    text = re.sub(r"\{\{picture:([\w-]+)\}\}", lambda m: picture(m.group(1)), text)
    OUT.write_text(text, encoding="utf-8", newline="\n")
    print(f"  gebaut   {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    build()
