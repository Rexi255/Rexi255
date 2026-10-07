"""Tools: Logos einfarbig in accent auf isometrischen Sockeln.

Daten: tokens.json -> tools (Name + Icon-Schlüssel oder Dot-Matrix-Kürzel),
Logo-Pfade aus src/design/icons.json (Simple Icons, CC0-Pfaddaten).

Animation:
  Boot (nach dem Stack): Tools gehen nacheinander an (Logo hell, Sockel-LED an).
  Ambient: reihum hebt sich immer genau ein Logo kurz an und leuchtet in
  accent-glow auf (ein Durchlauf ca. 11 s), sonst Ruhe.
reduced motion: alle Logos ruhig und hell.
"""

import html
import json
from pathlib import Path

import dotmatrix
from _scene import Face, anim, boot_schedule, box, circles, document, secs, style
from svglib import Iso, num

ICONS = json.loads((Path(__file__).resolve().parent.parent / "design" / "icons.json").read_text())
PER_ROW = 5
SLOT_W = 168
LOGO = 40          # Logo-Kantenlänge (px)
ROW_H = 130
TOP = 50           # Mitte der Logos in Zeile 1 (px)
HEIGHT = 300
LIFT = 8           # Anheben im Ambient-Loop (px)


def logo(tool, size):
    """Logo (oder Dot-Matrix-Kürzel) zentriert um (0, 0), Kantenlänge size."""
    if "icon" in tool:
        s = size / 24
        return (f'<path class="logo" transform="translate({num(-size / 2)} {num(-size / 2)}) '
                f'scale({num(s)})" d="{ICONS[tool["icon"]]}"/>')
    text = tool["monogram"]
    pitch = size / dotmatrix.ROWS
    w = dotmatrix.width(text) * pitch
    centers = [(-w / 2 + (c + 0.5) * pitch, -size / 2 + (r + 0.5) * pitch)
               for c, r, lit in dotmatrix.cells(text) if lit]
    return f'<path class="logo" d="{circles(centers, pitch * 0.42)}"/>'


def render(tok):
    width = tok["canvas.width"]
    tools = tok.raw["tools"]
    ease = tok["motion.ease"]
    fast, step = secs(tok["motion.fast"]), secs(tok["motion.stagger"])
    t = boot_schedule(tok)
    beat = secs(tok["motion.base"])            # Abstand zwischen zwei "aktiven" Tools
    cycle = beat * len(tools)                  # ca. 11 s: liegt im Ambient-Bereich
    peak = 100 * beat / cycle                  # Anteil eines Tools am Zyklus (%)

    css = [
        "@keyframes fade { from { opacity: 0.15; } }",
        f"@keyframes lift {{ 0%, {num(peak)}%, 100% {{ transform: translateY(0); }} "
        f"{num(peak * 0.3)}%, {num(peak * 0.7)}% {{ transform: translateY(-{LIFT}px); "
        f"fill: {tok['color.accent-glow']}; }} }}",
        f".logo {{ fill: {tok['color.accent']}; }}",
    ]
    body = []
    for i, tool in enumerate(tools):
        row, col = divmod(i, PER_ROW)
        in_row = min(PER_ROW, len(tools) - row * PER_ROW)
        cx = width / 2 + (col - (in_row - 1) / 2) * SLOT_W
        logo_y = TOP + row * ROW_H
        plate_top = logo_y + LOGO / 2 + 16

        # Sockel: flache isometrische Platte, Oberseitenmitte unter dem Logo
        iso = Iso(tok, origin=(cx, plate_top + 0.6 * tok["grid.unit"]))
        plate = box(iso, -1.5, -1.5, 0, 3, 3, 0.6)
        led = Face(iso, "left", -1.5, 1.5, 0).dots(
            [(0.6, 0.3)], 2.2, "ok", style(anim("fade", fast, t["tools"] + i * step, "steps(2)")))
        body.append(plate + led)

        on = anim("fade", fast, t["tools"] + i * step, ease)
        loop = anim("lift", cycle, t["tools_end"] + i * beat, ease, "infinite")
        body.append(f'<g transform="translate({num(cx)} {num(logo_y)})">'
                    f'<g style="{style(on)}"><g style="{style(loop)}">{logo(tool, LOGO)}</g></g></g>')
        body.append(f'<text class="txt" x="{num(cx)}" y="{num(plate_top + 52)}" '
                    f'text-anchor="middle">{html.escape(tool["name"])}</text>')

    names = ", ".join(tool["name"] for tool in tools)
    label = f"Tools als leuchtende Logos auf isometrischen Sockeln: {names}."
    return document(tok, HEIGHT, html.escape(label, quote=True), "\n".join(body), "\n".join(css))
