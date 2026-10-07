"""Erzeugt README.md aus src/readme.md.

Platzhalter:
    {{picture:NAME}}  -> <picture> mit assets/NAME-dark.svg / -light.svg,
                         Fallback-<img> ist die Dark-Variante (CLAUDE.md, Regel 5).
                         Der Alt-Text kommt aus dem aria-label der Grafik, damit
                         er immer zum Inhalt passt (z. B. nach Skill-Änderungen).
    {{projects}}      -> alle Projektkarten (project-1, project-2, ...) nebeneinander,
                         Karten mit url aus tokens.json sind verlinkt.

Wird von build.py aufgerufen. Einzeln: python3 scripts/readme.py
"""

import html
import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "src" / "readme.md"
OUT = ROOT / "README.md"

PICTURE = """<picture>
    <source media="(prefers-color-scheme: dark)" srcset="assets/{name}-dark.svg">
    <source media="(prefers-color-scheme: light)" srcset="assets/{name}-light.svg">
    <img src="assets/{name}-dark.svg" width="{width}" alt="{alt}">
  </picture>"""


def picture(name, width=None):
    dark = ROOT / "assets" / f"{name}-dark.svg"
    if not dark.exists() or not (ROOT / "assets" / f"{name}-light.svg").exists():
        raise SystemExit(f"README: Grafik '{name}' fehlt in assets/ (dark und light nötig)")
    root = ET.parse(dark).getroot()
    alt = root.get("aria-label")
    if not alt:
        raise SystemExit(f"README: {dark.name} hat kein aria-label für den Alt-Text")
    width = width or root.get("viewBox").split()[2]
    return PICTURE.format(name=name, width=width, alt=html.escape(alt, quote=True))


def centered(inner):
    return f'<p align="center">\n  {inner}\n</p>'


def projects():
    """Projektkarten nebeneinander (je knapp halbe Breite), mit Link falls vorhanden."""
    tokens = json.loads((ROOT / "src" / "design" / "tokens.json").read_text(encoding="utf-8"))
    cards = []
    for i, project in enumerate(tokens["projects"], 1):
        card = picture(f"project-{i}", width="49%")
        if project.get("url"):
            # ohne Zeilenumbrüche: Leerraum im Link würde unterstrichen angezeigt
            card = " ".join(card.split()).replace("> <", "><")
            card = f'<a href="{html.escape(project["url"], quote=True)}">{card}</a>'
        cards.append(card)
    return centered("\n  ".join(cards))


def build():
    text = SOURCE.read_text(encoding="utf-8")
    text = re.sub(r"\{\{picture:([\w-]+)\}\}", lambda m: centered(picture(m.group(1))), text)
    text = text.replace("{{projects}}", projects())
    OUT.write_text(text, encoding="utf-8", newline="\n")
    print(f"  gebaut   {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    build()
