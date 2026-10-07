"""Prüft alle generierten SVGs in assets/ gegen die harten Regeln aus CLAUDE.md.

Aufruf:
    python3 scripts/check.py            # prüft assets/
    python3 scripts/check.py a.svg ...  # prüft nur diese Dateien

Bricht mit Exit-Code 1 ab, sobald irgendeine Regel verletzt ist.

Geprüft wird:
  - gültiges XML, kein DOCTYPE/ENTITY
  - Wurzel ist <svg> mit viewBox-Breite canvas.width (900)
  - keine verbotenen Elemente (script, foreignObject, iframe, ...)
  - kein JavaScript (on*-Attribute, "javascript:")
  - keine externen Ressourcen (href/url() nur auf #id, kein @import/@font-face)
  - Farben nur aus der Palette des passenden Themes in tokens.json
  - wer animiert, braucht einen prefers-reduced-motion-Block;
    SMIL-Animationen sind verboten, weil CSS sie dort nicht stoppen kann
  - zu jeder -dark.svg gibt es eine -light.svg und umgekehrt
  - Größenbudget je Datei und gesamt

Nur Python-Standardbibliothek.
"""

import argparse
import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"
README = ROOT / "README.md"
TOKENS = ROOT / "src" / "design" / "tokens.json"

KB = 1024
BUDGET_HERO = 300 * KB
BUDGET_DEFAULT = 150 * KB
BUDGET_TOTAL = 1024 * KB

SVG_NS = "http://www.w3.org/2000/svg"
FORBIDDEN_ELEMENTS = {
    "script", "foreignObject", "iframe", "object", "embed", "audio", "video",
    "image", "feImage", "a", "handler", "listener",
}
SMIL_ELEMENTS = {"animate", "animateMotion", "animateTransform", "set", "animateColor"}
COLOR_PROPS = ("fill", "stroke", "stop-color", "flood-color", "lighting-color", "color")
COLOR_KEYWORDS = {"none", "currentcolor", "transparent", "inherit"}

CSS_COLOR = re.compile(
    r"(?<![\w-])(" + "|".join(COLOR_PROPS) + r")\s*:\s*([^;}!]+)", re.IGNORECASE
)
URL = re.compile(r"url\(\s*['\"]?([^'\")\s]*)", re.IGNORECASE)


def local(name):
    """'{namespace}tag' -> 'tag'"""
    return name.rsplit("}", 1)[-1]


def theme_of(path):
    for theme in ("dark", "light"):
        if path.stem.endswith(f"-{theme}"):
            return theme
    return None


def budget_for(path):
    return BUDGET_HERO if path.name.startswith("hero-") else BUDGET_DEFAULT


def check_color(value, palette, where, errors):
    value = value.strip()
    if value.lower() in COLOR_KEYWORDS or value.startswith("url(#"):
        return
    if value.upper() not in palette:
        errors.append(f"{where}: Farbe '{value}' ist nicht in tokens.json (Theme-Palette)")


def check_css(text, palette, where, errors):
    lowered = text.lower()
    for rule in ("@import", "@font-face"):
        if rule in lowered:
            errors.append(f"{where}: '{rule}' ist verboten (externe Ressource)")
    for target in URL.findall(text):
        if not target.startswith("#"):
            errors.append(f"{where}: url({target}) zeigt nicht auf eine interne #id")
    for _prop, value in CSS_COLOR.findall(text):
        check_color(value, palette, where, errors)


def check_file(path, tokens):
    errors = []
    data = path.read_bytes()
    text = data.decode("utf-8", errors="replace")
    theme = theme_of(path)
    if theme is None:
        return ["Dateiname muss auf -dark.svg oder -light.svg enden"]
    palette = {c.upper() for c in tokens["color"][theme].values()}

    if len(data) > budget_for(path):
        errors.append(
            f"Größenbudget überschritten: {len(data) / KB:.1f} KB > {budget_for(path) // KB} KB"
        )
    if "<!DOCTYPE" in text or "<!ENTITY" in text:
        errors.append("DOCTYPE/ENTITY-Deklarationen sind verboten")
        return errors
    if "javascript:" in text.lower():
        errors.append("'javascript:' gefunden")

    try:
        root = ET.fromstring(data)
    except ET.ParseError as exc:
        return errors + [f"kein gültiges XML: {exc}"]

    if root.tag != f"{{{SVG_NS}}}svg":
        errors.append(f"Wurzelelement ist {root.tag}, erwartet <svg> im SVG-Namespace")
    viewbox = (root.get("viewBox") or "").replace(",", " ").split()
    width = tokens["canvas"]["width"]
    if len(viewbox) != 4 or float(viewbox[2]) != width:
        errors.append(f"viewBox muss {width} breit sein (ist: '{root.get('viewBox')}')")

    style_text = []
    for el in root.iter():
        tag = local(el.tag)
        where = f"<{tag}>"
        if tag in FORBIDDEN_ELEMENTS:
            errors.append(f"{where} ist verboten")
        if tag in SMIL_ELEMENTS:
            errors.append(
                f"{where}: SMIL-Animation lässt sich per prefers-reduced-motion "
                "nicht stoppen, bitte CSS-Animation verwenden"
            )
        if tag == "style":
            style_text.append(el.text or "")
            check_css(el.text or "", palette, where, errors)
        for attr, value in el.attrib.items():
            name = local(attr)
            at = f"{where} @{name}"
            if name.lower().startswith("on"):
                errors.append(f"{at}: Event-Handler (JavaScript) ist verboten")
            elif name == "href" and not value.startswith("#"):
                errors.append(f"{at}: externer Verweis '{value}' ist verboten")
            elif name == "style":
                check_css(value, palette, at, errors)
            elif name in COLOR_PROPS:
                check_color(value, palette, at, errors)
            elif "url(" in value:
                check_css(value, palette, at, errors)

    css = "\n".join(style_text)
    animated = "@keyframes" in css or "animation" in css
    if animated and "prefers-reduced-motion" not in css:
        errors.append("animiert, aber ohne prefers-reduced-motion-Block")
    return errors


def check_readme():
    """README: Bilder vorhanden, relative Pfade, Alt-Texte, kein Skript."""
    errors = []
    text = README.read_text(encoding="utf-8")
    if re.search(r"<script|javascript:|on\w+\s*=", text, re.IGNORECASE):
        errors.append("Skript/Event-Handler gefunden")
    for ref in re.findall(r'(?:src|srcset)="([^"]+)"', text):
        if re.match(r"[a-z]+:", ref) or ref.startswith("/"):
            errors.append(f"Bildpfad nicht relativ: {ref}")
        elif not (ROOT / ref).exists():
            errors.append(f"Bild fehlt: {ref}")
    for img in re.findall(r"<img\b[^>]*>", text):
        alt = re.search(r'alt="([^"]*)"', img)
        if not alt or len(alt.group(1).strip()) < 10:
            errors.append(f"Alt-Text fehlt/zu kurz: {img[:60]}…")
    for picture in re.findall(r"<picture>.*?</picture>", text, re.DOTALL):
        if 'prefers-color-scheme: dark' not in picture or 'prefers-color-scheme: light' not in picture:
            errors.append("<picture> ohne Dark- und Light-Quelle")
        fallback = re.search(r'<img[^>]*src="([^"]+)"', picture)
        if fallback and not fallback.group(1).endswith("-dark.svg"):
            errors.append(f"Fallback-<img> ist nicht die Dark-Variante: {fallback.group(1)}")
    return errors


def main(argv):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("files", nargs="*", type=Path)
    args = parser.parse_args(argv)

    tokens = json.loads(TOKENS.read_text(encoding="utf-8"))
    files = args.files or sorted(ASSETS.glob("*.svg"))
    failed = False

    for path in files:
        errors = check_file(path, tokens)
        size = path.stat().st_size / KB
        status = "FEHLER" if errors else "ok    "
        print(f"  {status} {path.name:<32} {size:7.1f} KB / {budget_for(path) // KB} KB")
        for err in errors:
            print(f"           - {err}")
        failed |= bool(errors)

    if not args.files:
        names = {p.name for p in files}
        for path in files:
            for a, b in (("-dark.svg", "-light.svg"), ("-light.svg", "-dark.svg")):
                if path.name.endswith(a) and path.name[: -len(a)] + b not in names:
                    print(f"  FEHLER {path.name}: Gegenstück {path.name[: -len(a)] + b} fehlt")
                    failed = True
        total = sum(p.stat().st_size for p in ASSETS.iterdir() if p.is_file())
        over = total > BUDGET_TOTAL
        print(
            f"  {'FEHLER' if over else 'ok    '} Gesamtgröße assets/"
            f"{'':<19} {total / KB:7.1f} KB / {BUDGET_TOTAL // KB} KB"
        )
        failed |= over

        if README.exists():
            readme_errors = check_readme()
            print(f"  {'FEHLER' if readme_errors else 'ok    '} README.md")
            for err in readme_errors:
                print(f"           - {err}")
            failed |= bool(readme_errors)

    if not files:
        print("  (keine SVGs in assets/)")
    print("Prüfung fehlgeschlagen." if failed else "Alle Prüfungen bestanden.")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
