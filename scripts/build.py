"""Baut alles: Templates -> assets/, danach Vorschau und Prüfung.

Aufruf (aus dem Repo-Wurzelverzeichnis):
    python3 scripts/build.py

Ablauf:
  1. src/design/tokens.json laden.
  2. Jedes Template src/templates/<name>.py (ohne führendes "_") laden.
     Es muss eine Funktion render(tok) -> str enthalten.
  3. Für jedes Theme (dark, light) rendern und nach
     assets/<name>-<theme>.svg schreiben.
  4. Generierte SVGs ohne zugehöriges Template entfernen.
  5. preview/index.html neu erzeugen.
  6. Prüfskript laufen lassen. Exit-Code != 0, wenn etwas verletzt ist.

Nur Python-Standardbibliothek.
"""

import importlib.util
import json
import sys
from pathlib import Path

import check
import preview
from svglib import Tokens

ROOT = Path(__file__).resolve().parent.parent
TOKENS = ROOT / "src" / "design" / "tokens.json"
TEMPLATES = ROOT / "src" / "templates"
ASSETS = ROOT / "assets"
THEMES = ("dark", "light")


def load_template(path):
    spec = importlib.util.spec_from_file_location(f"template_{path.stem}", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    if not callable(getattr(module, "render", None)):
        raise SystemExit(f"{path.name}: keine Funktion render(tok) gefunden")
    return module


def build_assets():
    raw = json.loads(TOKENS.read_text(encoding="utf-8"))
    ASSETS.mkdir(exist_ok=True)
    written = set()

    for path in sorted(TEMPLATES.glob("*.py")):
        if path.name.startswith("_"):
            continue
        template = load_template(path)
        for theme in THEMES:
            svg = template.render(Tokens(raw, theme)).strip() + "\n"
            out = ASSETS / f"{path.stem}-{theme}.svg"
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
    print("Prüfung:")
    return check.main([])


if __name__ == "__main__":
    sys.exit(main())
