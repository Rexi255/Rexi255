"""Baut alles: Templates -> assets/, danach Vorschau und Prüfung.

Aufruf (aus dem Repo-Wurzelverzeichnis):
    python3 scripts/build.py

Ablauf:
  1. src/design/tokens.json und Live-Daten (src/data/github.json) laden.
  2. Jedes Template src/templates/<name>.py (ohne führendes "_") laden.
     Es muss eine Funktion render(tok) -> str enthalten. Optional liefert
     variants(tok) mehrere Schlüssel -> render(tok, key) je Schlüssel.
  3. Für jedes Theme (dark, light) rendern und nach
     assets/<name>-<theme>.svg schreiben.
  4. Generierte SVGs ohne zugehöriges Template entfernen.
  5. preview/index.html und README.md (aus src/readme.md) neu erzeugen.
  6. Prüfskript laufen lassen. Exit-Code != 0, wenn etwas verletzt ist.

Nur Python-Standardbibliothek.
"""

import importlib.util
import json
import os
import sys
from pathlib import Path

import check
import preview
import readme
from svglib import Tokens

# Templates dürfen gemeinsame Helfer aus src/templates/_*.py importieren
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src" / "templates"))

ROOT = Path(__file__).resolve().parent.parent
TOKENS = ROOT / "src" / "design" / "tokens.json"
TEMPLATES = ROOT / "src" / "templates"
ASSETS = ROOT / "assets"
DATA = ROOT / "src" / "data" / "github.json"
THEMES = ("dark", "light")


def load_template(path):
    spec = importlib.util.spec_from_file_location(f"template_{path.stem}", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    if not callable(getattr(module, "render", None)):
        raise SystemExit(f"{path.name}: keine Funktion render(tok) gefunden")
    return module


def load_data():
    """Live-Daten laden. PROFILE_DATA=pfad.json überschreibt (zum Testen)."""
    path = Path(os.environ.get("PROFILE_DATA") or DATA)
    if not path.exists():
        print(f"  Hinweis: keine Live-Daten ({path.name}) – dynamische Grafiken zeigen Platzhalter")
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def build_assets():
    raw = json.loads(TOKENS.read_text(encoding="utf-8"))
    data = load_data()
    ASSETS.mkdir(exist_ok=True)
    written = set()

    for path in sorted(TEMPLATES.glob("*.py")):
        if path.name.startswith("_"):
            continue
        template = load_template(path)
        # Optional: variants(tok) -> Liste von Schlüsseln, je Schlüssel eine
        # eigene Grafik <name>-<schlüssel> (z. B. eine Karte pro Projekt)
        variants = getattr(template, "variants", None)
        keys = variants(Tokens(raw, "dark", data)) if variants else [None]
        for key in keys:
            name = path.stem if key is None else f"{path.stem}-{key}"
            for theme in THEMES:
                tok = Tokens(raw, theme, data)
                svg = (template.render(tok) if key is None else template.render(tok, key)).strip() + "\n"
                out = ASSETS / f"{name}-{theme}.svg"
                out.write_text(svg, encoding="utf-8", newline="\n")
                written.add(out.name)
                print(f"  gebaut   {out.relative_to(ROOT)}  ({len(svg.encode()):,} B)")

    for theme in THEMES:
        for stale in ASSETS.glob(f"*-{theme}.svg"):
            if stale.name not in written:
                stale.unlink()
                print(f"  entfernt {stale.relative_to(ROOT)} (kein Template mehr)")


def main():
    print("Assets:")
    build_assets()
    print("Vorschau:")
    preview.build()
    print("README:")
    readme.build()
    print("Prüfung:")
    return check.main([])


if __name__ == "__main__":
    sys.exit(main())
