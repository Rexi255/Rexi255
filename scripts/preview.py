"""Erzeugt preview/index.html: alle Assets in Dark und Light, bei 900 und 400 px.

Wird von build.py automatisch aufgerufen. Einzeln:
    python3 scripts/preview.py

Die Seite einfach lokal im Browser öffnen. Kein JavaScript, die SVGs werden
wie auf GitHub per <img> eingebunden (dort laufen CSS-Animationen, aber
keine Skripte). Die Zeile "auto" nutzt <picture> + prefers-color-scheme
genau wie später die README.
"""

import html
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"
OUT = ROOT / "preview" / "index.html"

WIDTHS = (900, 400)

# Seitenhintergründe von GitHub selbst (nicht aus tokens.json): Die Vorschau
# soll zeigen, wie die Grafik auf der echten Profilseite sitzt.
GITHUB_BG = {"dark": "#0d1117", "light": "#ffffff"}

PAGE = """<!doctype html>
<html lang="de">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Vorschau – Profil-Assets</title>
<style>
  body {{ margin: 0; padding: 24px; font: 14px ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
         background: #6e7681; color: #fff; }}
  h1 {{ font-size: 18px; margin: 0 0 24px; }}
  h2 {{ font-size: 16px; margin: 40px 0 12px; }}
  .row {{ display: flex; flex-wrap: wrap; gap: 24px; align-items: flex-start; padding: 16px; margin-bottom: 12px; }}
  .dark {{ background: {dark}; color: #e6edf3; }}
  .light {{ background: {light}; color: #1f2328; }}
  .auto {{ background: {light}; color: #1f2328; }}
  @media (prefers-color-scheme: dark) {{ .auto {{ background: {dark}; color: #e6edf3; }} }}
  figure {{ margin: 0; }}
  figcaption {{ margin-bottom: 6px; opacity: .7; }}
  img {{ display: block; max-width: 100%; height: auto; }}
</style>
</head>
<body>
<h1>Profil-Assets – Vorschau</h1>
{sections}
</body>
</html>
"""


def components():
    """Komponentennamen, für die es -dark.svg oder -light.svg gibt."""
    names = set()
    for path in ASSETS.glob("*.svg"):
        for theme in ("dark", "light"):
            if path.stem.endswith(f"-{theme}"):
                names.add(path.stem[: -len(theme) - 1])
    return sorted(names)


def figure(caption, width, img):
    return (
        f'<figure style="width:{width}px"><figcaption>{caption}</figcaption>'
        f"{img}</figure>"
    )


def section(name):
    esc = html.escape(name)
    rows = []
    for theme in ("dark", "light"):
        src = f"../assets/{esc}-{theme}.svg"
        figs = "".join(
            figure(f"{theme} · {w}px", w, f'<img src="{src}" width="{w}" alt="{esc} ({theme})">')
            for w in WIDTHS
        )
        rows.append(f'<div class="row {theme}">{figs}</div>')

    picture = (
        "<picture>"
        f'<source media="(prefers-color-scheme: dark)" srcset="../assets/{esc}-dark.svg">'
        f'<source media="(prefers-color-scheme: light)" srcset="../assets/{esc}-light.svg">'
        f'<img src="../assets/{esc}-dark.svg" width="{{w}}" alt="{esc} (auto)">'
        "</picture>"
    )
    figs = "".join(
        figure(f"auto (System-Theme) · {w}px", w, picture.replace("{w}", str(w)))
        for w in WIDTHS
    )
    rows.append(f'<div class="row auto">{figs}</div>')
    return f"<h2>{esc}</h2>\n" + "\n".join(rows)


def build():
    OUT.parent.mkdir(exist_ok=True)
    sections = "\n".join(section(n) for n in components()) or "<p>Keine Assets gefunden.</p>"
    page = PAGE.format(sections=sections, dark=GITHUB_BG["dark"], light=GITHUB_BG["light"])
    OUT.write_text(page, encoding="utf-8", newline="\n")
    print(f"  gebaut   {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    build()
