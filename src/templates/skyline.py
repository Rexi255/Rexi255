"""Live-Skyline: Contributions der letzten 52 Wochen als isometrische Säulen.

Daten: tok.data (src/data/github.json, täglich von der Action aktualisiert).
Eine Säule pro Woche als Häuserblock: 4 Reihen à 13 Wochen (Quartale),
hinten links die älteste, vorne rechts die aktuelle Woche. Höhe proportional zur Wochensumme,
Oberseiten in accent mit Deckkraft nach Wochenwert, die stärkste Woche
zusätzlich mit Leuchtkante.

Animation: einmal als Welle wachsen (nach Hero und Stack), danach Ruhe.
Ohne Daten: flache Säulen und Hinweis "noch keine Daten".
"""

from datetime import date

from _scene import SKYLINE_WAVE, SKYLINE_WEEKS, anim, boot_schedule, box, document, secs, style
from svglib import Iso, num

WEEKS = SKYLINE_WEEKS
COLS, ROWS = 13, 4  # Häuserblock: 13 Wochen je Reihe, 4 Reihen (Quartale)
CELL = 1.7        # Rasterabstand der Säulen (Rastereinheiten)
SIZE = 1.2        # Säulen-Grundfläche (Rastereinheiten)
MAX_H = 7         # Höhe der stärksten Woche (Rastereinheiten)
MIN_H = 0.12      # Wochen ohne Beiträge: flache Platte
MARGIN = 32


def render(tok):
    unit = tok["grid.unit"]
    weeks = (tok.data or {}).get("weeks", [])[-WEEKS:]
    counts = [w["count"] for w in weeks] or [0] * WEEKS
    peak = max(counts)
    peak_i = counts.index(peak) if peak else None

    # Ursprung so, dass die höchste mögliche Säule (ganz rechts) und die
    # vorderste Säule (ganz links) hineinpassen
    iso_probe = Iso(tok, origin=(0, 0))
    span_x, span_y = COLS * CELL, ROWS * CELL
    right_x, _ = iso_probe.point(span_x, -0.4)
    left_x, _ = iso_probe.point(-0.4, span_y)
    _, top_y = iso_probe.point(-0.4, -0.4, MAX_H)
    _, bottom_y = iso_probe.point(span_x, span_y)
    oy = MARGIN - top_y
    ox = (tok["canvas.width"] - right_x - left_x) / 2
    iso = Iso(tok, origin=(ox, oy))
    height = round(oy + bottom_y + MARGIN)

    ease = tok["motion.ease"]
    fast = secs(tok["motion.fast"])
    t0 = boot_schedule(tok)["skyline"]

    css = [
        "@keyframes grow { from { transform: scaleY(0.02); } }",
        ".col { transform-box: fill-box; transform-origin: 50% 100%; }",
        f".hdr {{ fill: {tok['color.accent']}; }}",
    ]
    n = len(counts)
    floor = iso.points((-0.4, -0.4), (span_x, -0.4), (span_x, span_y), (-0.4, span_y))
    body = [f'<polygon class="floor" points="{floor}"/>']

    # Woche i -> Reihe i // COLS (Quartal), Spalte i % COLS.
    # Zeichnen von hinten nach vorne (kleines x + y zuerst).
    cells = sorted(range(n), key=lambda i: (i % COLS + i // COLS, i // COLS))
    for i in cells:
        h = max(MIN_H, counts[i] / peak * MAX_H) if peak else MIN_H
        x, y = (i % COLS) * CELL, (i // COLS) * CELL
        col = box(iso, x, y, 0, SIZE, SIZE, h)
        if peak and counts[i]:
            # Oberseite in accent, Deckkraft nach Wochenwert (stärkste Woche = 1)
            top = iso.box(x, y, 0, SIZE, SIZE, h)["top"]
            col += f'<polygon class="acc" fill-opacity="{num(0.2 + 0.8 * counts[i] / peak)}" points="{top}"/>'
            if i == peak_i:
                col += f'<polygon class="edge-glow" points="{top}"/>'
        st = style(anim("grow", fast, t0 + i * SKYLINE_WAVE, ease))
        body.append(f'<g class="col" style="{st}">{col}</g>')

    # Beschriftung wie ein Panel: links Titel + Summe, rechts die stärkste Woche
    total = tok.data.get("total", sum(counts)) if tok.data else 0
    lx, rx = MARGIN + 8, tok["canvas.width"] - MARGIN - 8
    arrow = '<tspan class="hdr">&gt; </tspan>'
    back = '<tspan class="hdr"> &lt;</tspan>'
    body.append(f'<text class="mut" x="{lx}" y="{MARGIN + 40}">{arrow}contributions</text>')
    body.append(f'<text class="mut" x="{lx}" y="{MARGIN + 74}">{arrow}{WEEKS} Wochen</text>')
    total_text = f"{total} im Jahr" if tok.data else "noch keine Daten"
    body.append(f'<text class="txt" x="{lx}" y="{MARGIN + 124}">{total_text}</text>')
    if peak_i is not None:
        start = date.fromisoformat(weeks[peak_i]["start"]).strftime("%d.%m.%Y")
        body.append(f'<text class="mut" x="{rx}" y="{height - MARGIN - 84}" text-anchor="end">stärkste Woche{back}</text>')
        body.append(f'<text class="txt" x="{rx}" y="{height - MARGIN - 50}" text-anchor="end">{peak} ab {start}</text>')

    if tok.data:
        label = (f"Isometrische Skyline aus {n} Säulen, eine pro Woche: {total} Contributions im "
                 f"letzten Jahr, die stärkste Woche ({peak}) ist hervorgehoben.")
    else:
        label = "Isometrische Skyline der Contributions der letzten 52 Wochen – noch keine Daten vorhanden."
    return document(tok, height, label, "\n".join(body), "\n".join(css))
