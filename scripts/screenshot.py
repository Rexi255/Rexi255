"""Visuelle Prüfung: Screenshots aller Assets per Headless-Chromium.

Aufruf:
    python3 scripts/screenshot.py                    # Zustand nach 6 s (Boot fertig)
    python3 scripts/screenshot.py --at 800           # Zustand nach 800 ms (Boot-Frames)
    python3 scripts/screenshot.py --reduced-motion   # mit prefers-reduced-motion
    python3 scripts/screenshot.py --only hero        # nur eine Komponente

Erzeugt in preview/shots/ (nicht im Git):
    <name>-<theme>-<breite>[-suffix].png  je Komponente, Theme und Breite (900/400 px)
    overview.png                          die komplette Vorschauseite (statischer Endzustand)

Zwei Methoden ("Engines"), automatisch gewählt (--engine zum Erzwingen):

  playwright  Echtzeit: Seite laden, wirklich --at ms warten, Screenshot.
              Verlässlich für alle Animationen. Braucht Node + Playwright
              (npm i -g playwright). Bevorzugt, wenn vorhanden.
  cli         Ohne Abhängigkeiten: Chromium-Headless-Shell per Kommandozeile
              mit --virtual-time-budget. Bekannte Grenze: Animationen, die
              etwas nur vorübergehend einblenden (z. B. "system online"),
              treibt die virtuelle Uhr nicht korrekt an. Endzustände und
              reduced-motion stimmen.
              Headless-Shell lokal: npx @puppeteer/browsers install chrome-headless-shell@stable

Das SVG wird für den Screenshot inline in eine HTML-Seite eingebettet und
per CSS auf die Zielbreite skaliert (in <img> treibt die virtuelle Uhr
SVG-Animationen gar nicht an). Die Übersichtsseite nutzt <img> wie GitHub
und wird immer mit prefers-reduced-motion aufgenommen.
"""

import argparse
import glob
import json
import os
import shutil
import struct
import subprocess
import sys
import xml.etree.ElementTree as ET
import zlib
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


# --- Engine: Playwright (Echtzeit) -------------------------------------------

def node_env():
    """Umgebung, in der Node global installierte Pakete findet."""
    env = dict(os.environ)
    npm = shutil.which("npm")
    if npm:
        root = subprocess.run([npm, "root", "-g"], capture_output=True, text=True).stdout.strip()
        env["NODE_PATH"] = os.pathsep.join(p for p in (env.get("NODE_PATH"), root) if p)
    return env


def has_playwright():
    node = shutil.which("node")
    if not node:
        return False
    probe = subprocess.run([node, "-e", "require.resolve('playwright')"],
                           capture_output=True, env=node_env(), cwd=ROOT)
    return probe.returncode == 0


def run_playwright(jobs):
    job_file = SHOTS / "_jobs.json"
    config = {"jobs": jobs}
    if os.environ.get("CHROME_PATH"):
        config["executablePath"] = os.environ["CHROME_PATH"]
    job_file.write_text(json.dumps(config), encoding="utf-8")
    try:
        result = subprocess.run(
            [shutil.which("node"), str(ROOT / "scripts" / "shoot.mjs"), str(job_file)],
            capture_output=True, text=True, env=node_env(), timeout=600,
        )
    finally:
        job_file.unlink()
    if result.returncode != 0:
        raise RuntimeError(f"Playwright-Screenshots fehlgeschlagen:\n{result.stderr[-1500:]}")


# --- Engine: Kommandozeile (virtuelle Zeit) ----------------------------------

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


def shoot(browser, url, out, width, height, at_ms, reduced, check_blank=True):
    cmd = [browser]
    if not is_headless_shell(browser):
        cmd.append("--headless=new")
    cmd += [
        "--disable-gpu",
        "--hide-scrollbars",
        # Ohne diesen Schalter liefert die Headless-Shell mit virtueller Zeit
        # sporadisch (ca. jedes 3. Mal) ein leeres Bild.
        "--run-all-compositor-stages-before-draw",
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
    for _attempt in range(3):
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        if result.returncode != 0 or not Path(out).exists():
            raise RuntimeError(f"Screenshot fehlgeschlagen: {Path(out).name}\n{result.stderr[-800:]}")
        if not check_blank or not looks_blank(Path(out)):
            return


def run_cli(browser, jobs):
    # Aufwärmen: Der allererste Start baut u. a. den Font-Cache auf.
    warmup = SHOTS / "_warmup.png"
    shoot(browser, "about:blank", warmup, 100, 100, 1000, False, check_blank=False)
    warmup.unlink()
    for job in jobs:
        shoot(browser, job["url"], job["out"], job["width"], job["height"], job["at"], job["reduced"])


# --- gemeinsam -----------------------------------------------------------------

def looks_blank(png):
    """Grober Leer-Test ohne Bildbibliothek: einfarbige Bilder enthalten nach
    dem Entpacken nur eine Handvoll verschiedener Bytewerte, echte Grafiken
    deutlich über 50."""
    data, pos, idat = png.read_bytes(), 8, b""
    while pos < len(data):
        length, kind = struct.unpack(">I4s", data[pos:pos + 8])
        if kind == b"IDAT":
            idat += data[pos + 8:pos + 8 + length]
        pos += 12 + length
    return len(set(zlib.decompress(idat))) < 16


def aspect(svg_path):
    """Höhe/Breite aus der viewBox."""
    vb = ET.parse(svg_path).getroot().get("viewBox").replace(",", " ").split()
    return float(vb[3]) / float(vb[2])


def pick_engine(requested):
    """-> (engine, browser) oder (None, None), wenn nichts verfügbar ist."""
    if requested in ("auto", "playwright") and has_playwright():
        return "playwright", None
    if requested == "playwright":
        print("Playwright nicht gefunden (npm i -g playwright).")
        return None, None
    browser = find_browser()
    return ("cli", browser) if browser else (None, None)


def main(argv):
    parser = argparse.ArgumentParser(description="Screenshots aller Assets")
    parser.add_argument("--at", type=int, default=DEFAULT_AT_MS, metavar="MS",
                        help=f"Zeitpunkt in ms nach dem Laden (Standard: {DEFAULT_AT_MS})")
    parser.add_argument("--reduced-motion", action="store_true")
    parser.add_argument("--only", metavar="NAME", help="nur diese Komponente")
    parser.add_argument("--engine", choices=("auto", "playwright", "cli"), default="auto")
    args = parser.parse_args(argv)

    engine, browser = pick_engine(args.engine)
    if engine is None:
        print("Kein Headless-Browser gefunden (Chrome/Chromium/Edge) und kein Playwright.")
        print("Bitte preview/index.html lokal im Browser öffnen oder CHROME_PATH setzen.")
        return 2
    if engine == "playwright":
        print("Engine: playwright (Echtzeit)")
    else:
        print(f"Engine: cli ({browser})")
        print("Hinweis: virtuelle Zeit – vorübergehende Einblendungen können fehlen.")
        if not is_headless_shell(browser):
            print("WARNUNG: kein chrome-headless-shell gefunden. Screenshots können unten")
            print("         abgeschnitten sein und Animationen im Startzustand zeigen.")

    SHOTS.mkdir(parents=True, exist_ok=True)
    if args.reduced_motion:
        suffix = "-reduced"
    elif args.at != DEFAULT_AT_MS:
        suffix = f"-t{args.at}"
    else:
        suffix = ""

    names = preview.components()
    if args.only:
        names = [n for n in names if n == args.only]

    jobs, pages = [], []
    for name in names:
        for theme in ("dark", "light"):
            svg = ASSETS / f"{name}-{theme}.svg"
            ratio = aspect(svg)
            for width in preview.WIDTHS:
                page = SHOTS / f"_{name}-{theme}-{width}.html"
                page.write_text(WRAPPER.format(bg=preview.GITHUB_BG[theme], width=width,
                                               svg=svg.read_text(encoding="utf-8")), encoding="utf-8")
                pages.append(page)
                jobs.append({"url": page.resolve().as_uri(), "width": width,
                             "height": round(width * ratio), "at": args.at,
                             "reduced": args.reduced_motion,
                             "out": str(SHOTS / f"{name}-{theme}-{width}{suffix}.png")})
    if not args.only:
        # 3 Zeilen (dark, light, auto) je Komponente, plus Überschriften/Abstände
        height = 80 + sum(
            3 * (round(900 * aspect(ASSETS / f"{n}-dark.svg")) + 66) + 60 for n in names
        )
        # 1000 ms: Ladezeit für die Bilder. (Ein Budget von 0 lässt die
        # Headless-Shell hängen.)
        jobs.append({"url": (ROOT / "preview" / "index.html").resolve().as_uri(), "width": 1440,
                     "height": height, "at": 1000, "reduced": True,
                     "out": str(SHOTS / "overview.png")})

    try:
        if engine == "playwright":
            run_playwright(jobs)
        else:
            run_cli(browser, jobs)
    finally:
        for page in pages:
            page.unlink(missing_ok=True)

    for job in jobs:
        out = Path(job["out"])
        note = "  WARNUNG: wirkt leer (nur Hintergrund)" if looks_blank(out) else ""
        print(f"  {out.relative_to(ROOT)}  ({job['width']}x{job['height']}){note}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
