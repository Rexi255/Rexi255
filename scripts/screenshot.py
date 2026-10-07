"""Visuelle Prüfung: Screenshots aller Assets per Headless-Chromium.

Aufruf:
    python3 scripts/screenshot.py                    # Zustand nach 6 s (Boot fertig)
    python3 scripts/screenshot.py --at 800           # Zustand nach 800 ms (Boot-Frames)
    python3 scripts/screenshot.py --reduced-motion   # mit prefers-reduced-motion
    python3 scripts/screenshot.py --only phase0-test # nur eine Komponente

Erzeugt in preview/shots/ (nicht im Git):
    <name>-<theme>-<breite>[-suffix].png  je Komponente, Theme und Breite (900/400 px)
    overview.png                          die komplette Vorschauseite (statischer Endzustand)

Technik:
  - Der Browser wird direkt per Kommandozeile gesteuert (kein Playwright,
    keine pip-Pakete). Gesucht wird in CHROME_PATH, dann an üblichen Orten.
  - --virtual-time-budget lässt die Seite eine feste Zeit "virtuell" laufen,
    damit Animationen reproduzierbar an derselben Stelle stehen.
  - Das SVG wird für den Screenshot inline in eine HTML-Seite eingebettet und
    per CSS auf die Zielbreite skaliert. Grund: In <img> eingebettet treibt
    die virtuelle Uhr die SVG-Animationen nicht an (Bild bliebe im
    Startzustand). Im echten Browser laufen sie auch in <img>.
  - Die Übersichtsseite nutzt <img> wie GitHub und wird deshalb immer mit
    prefers-reduced-motion aufgenommen, also im statischen Endzustand.
  - Bevorzugt wird chrome-headless-shell (klassischer Headless-Modus).
    Normales Chrome im neuen Headless-Modus schneidet unten ca. 88 px ab
    und lässt Animationen nicht vorlaufen. Es dient nur als Notlösung.
    Headless-Shell lokal installieren:
        npx @puppeteer/browsers install chrome-headless-shell@stable
"""

import argparse
import glob
import os
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

import preview

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"
SHOTS = ROOT / "preview" / "shots"
DEFAULT_AT_MS = 6000

HEADLESS_SHELLS = [
    *sorted(glob.glob("/opt/pw-browsers/chromium_headless_shell-*/chrome-linux/headless_shell")),
    "chrome-headless-shell",
    "headless_shell",
]
FULL_BROWSERS = [
    "/opt/pw-browsers/chromium",
    "chromium",
    "chromium-browser",
    "google-chrome",
    "google-chrome-stable",
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
]

WRAPPER = """<!doctype html><meta charset="utf-8">
<style>html,body{{margin:0;background:{bg};overflow:hidden}}
body>svg{{display:block;width:{width}px;height:auto}}</style>
{svg}
"""


def find_browser():
    for candidate in [os.environ.get("CHROME_PATH")] + HEADLESS_SHELLS + FULL_BROWSERS:
        if not candidate:
            continue
        path = shutil.which(candidate) or (candidate if Path(candidate).is_file() else None)
        if path:
            return path
    return None


def is_headless_shell(browser):
    name = Path(browser).name.lower()
    return "headless_shell" in name or "headless-shell" in name


def aspect(svg_path):
    """Höhe/Breite aus der viewBox."""
    vb = ET.parse(svg_path).getroot().get("viewBox").replace(",", " ").split()
    return float(vb[3]) / float(vb[2])


def shoot(browser, url, out, width, height, at_ms, reduced):
    cmd = [browser]
    if not is_headless_shell(browser):
        cmd.append("--headless=new")
    cmd += [
        "--disable-gpu",
        "--hide-scrollbars",
        "--force-device-scale-factor=1",
        f"--window-size={width},{height}",
        f"--virtual-time-budget={at_ms}",
        f"--screenshot={out}",
    ]
    if reduced:
        cmd.append("--force-prefers-reduced-motion")
    if hasattr(os, "geteuid") and os.geteuid() == 0:
        cmd.append("--no-sandbox")  # nur nötig, wenn als root (z. B. Container)
    cmd.append(url)
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    if result.returncode != 0 or not out.exists():
        raise RuntimeError(f"Screenshot fehlgeschlagen: {out.name}\n{result.stderr[-800:]}")


def main(argv):
    parser = argparse.ArgumentParser(description="Screenshots aller Assets")
    parser.add_argument("--at", type=int, default=DEFAULT_AT_MS, metavar="MS",
                        help=f"Zeitpunkt in ms nach dem Laden (Standard: {DEFAULT_AT_MS})")
    parser.add_argument("--reduced-motion", action="store_true")
    parser.add_argument("--only", metavar="NAME", help="nur diese Komponente")
    args = parser.parse_args(argv)

    browser = find_browser()
    if not browser:
        print("Kein Headless-Browser gefunden (Chrome/Chromium/Edge).")
        print("Bitte preview/index.html lokal im Browser öffnen oder CHROME_PATH setzen.")
        return 2
    print(f"Browser: {browser}")
    if not is_headless_shell(browser):
        print("WARNUNG: kein chrome-headless-shell gefunden. Screenshots können unten")
        print("         abgeschnitten sein und Animationen im Startzustand zeigen.")

    SHOTS.mkdir(parents=True, exist_ok=True)
    # Aufwärmen: Der allererste Start baut u. a. den Font-Cache auf. In dieser
    # Zeit kann das virtuelle Zeitbudget ablaufen, bevor gerendert wurde
    # (einmal beobachtet: leerer erster Screenshot).
    warmup = SHOTS / "_warmup.png"
    shoot(browser, "about:blank", warmup, 100, 100, 1000, False)
    warmup.unlink()
    if args.reduced_motion:
        suffix = "-reduced"
    elif args.at != DEFAULT_AT_MS:
        suffix = f"-t{args.at}"
    else:
        suffix = ""

    names = preview.components()
    if args.only:
        names = [n for n in names if n == args.only]

    for name in names:
        for theme in ("dark", "light"):
            svg = ASSETS / f"{name}-{theme}.svg"
            ratio = aspect(svg)
            for width in preview.WIDTHS:
                height = round(width * ratio)
                page = SHOTS / f"_{name}-{theme}-{width}.html"
                page.write_text(WRAPPER.format(
                    bg=preview.GITHUB_BG[theme], width=width,
                    svg=svg.read_text(encoding="utf-8"),
                ), encoding="utf-8")
                out = SHOTS / f"{name}-{theme}-{width}{suffix}.png"
                try:
                    shoot(browser, page.resolve().as_uri(), out, width, height,
                          args.at, args.reduced_motion)
                finally:
                    page.unlink()
                print(f"  {out.relative_to(ROOT)}  ({width}x{height})")

    if not args.only:
        # 3 Zeilen (dark, light, auto) je Komponente, plus Überschriften/Abstände
        height = 80 + sum(
            3 * (round(900 * aspect(ASSETS / f"{n}-dark.svg")) + 66) + 60 for n in names
        )
        out = SHOTS / "overview.png"
        shoot(browser, (ROOT / "preview" / "index.html").resolve().as_uri(), out,
              1440, height, 1000, reduced=True)
        print(f"  {out.relative_to(ROOT)}  (1440x{height}, statischer Endzustand)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
