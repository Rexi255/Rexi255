"""Live-Skyline: Contributions der letzten 52 Wochen als isometrische Säulen.

Daten: tok.data (src/data/github.json, täglich von der Action aktualisiert).
Eine Säule pro Woche, entlang der Iso-Achse von links unten (älteste Woche)
nach rechts oben (aktuelle Woche). Höhe proportional zur Wochensumme,
Oberseiten in accent mit Deckkraft nach Wochenwert, die stärkste Woche
zusätzlich mit Leuchtkante.

Animation: einmal als Welle wachsen (nach Hero und Stack), danach Ruhe.
Ohne Daten: flache Säulen und Hinweis "noch keine Daten".
"""

from datetime import date

from _scene import anim, boot_schedule, box, document, secs, style
from svglib import Iso, num

WEEKS = 52
SIZE = 0.8        # Säulen-Grundfläche (Rastereinheiten)
MAX_H = 14        # Höhe der stärksten Woche (Rastereinheiten)
MIN_H = 0.15      # Wochen ohne Beiträge: flache Platte
MARGIN = 20


def render(tok):
    unit = tok["grid.unit"]
    weeks = (tok.data or {}).get("weeks", [])[-WEEKS:]
    counts = [w["count"] for w in weeks] or [0] * WEEKS
    peak = max(counts)
    peak_i = counts.index(peak) if peak else None

    # Ursprung so, dass die höchste mögliche Säule (ganz rechts) und die
    # vorderste Säule (ganz links) hineinpassen
    iso_probe = Iso(tok, origin=(0, 0))
    right_x, top_y = iso_probe.point(SIZE, -(len(counts) - 1), MAX_H)
    oy = MARGIN - top_y
    ox = (tok["canvas.width"] - right_x) / 2
    iso = Iso(tok, origin=(ox, oy))
    height = round(oy + 2 * SIZE * unit / 2 + MARGIN + 6)

    ease = tok["motion.ease"]
    fast = secs(tok["motion.fast"])
    t0 = boot_schedule(tok)["end"] + secs(tok["motion.base"]) + fast
    wave = 0.03  # Versatz je Säule (s): die Welle läuft in ca. 1,5 s durch

    css = [
        "@keyframes grow { from { transform: scaleY(0.02); } }",
        ".col { transform-box: fill-box; transform-origin: 50% 100%; }",
    ]
    n = len(counts)
    floor = iso.points((-0.3, 1.1), (SIZE + 0.3, 1.1), (SIZE + 0.3, -(n - 1) - 0.3), (-0.3, -(n - 1) - 0.3))
    body = [f'<polygon class="floor" points="{floor}"/>']

    # hinten (rechts oben) nach vorne (links unten) zeichnen
    for i in reversed(range(n)):
        h = max(MIN_H, counts[i] / peak * MAX_H) if peak else MIN_H
        y = -i
        col = box(iso, 0, y, 0, SIZE, SIZE, h)
        if peak and counts[i]:
            # Oberseite in accent, Deckkraft nach Wochenwert (stärkste Woche = 1)
            top = iso.box(0, y, 0, SIZE, SIZE, h)["top"]
            col += f'<polygon class="acc" fill-opacity="{num(0.2 + 0.8 * counts[i] / peak)}" points="{top}"/>'
            if i == peak_i:
                col += f'<polygon class="edge-glow" points="{top}"/>'
        st = style(anim("grow", fast, t0 + i * wave, ease))
        body.append(f'<g class="col" style="{st}">{col}</g>')

    # Beschriftung: Titel oben links, Spitzenwoche unten rechts
    body.append(f'<text class="mut" x="{MARGIN + 4}" y="{MARGIN + 28}">contributions · letzte {WEEKS} Wochen</text>')
    if tok.data:
        total = tok.data.get("total", sum(counts))
        body.append(f'<text class="txt" x="{MARGIN + 4}" y="{MARGIN + 62}">{total} im letzten Jahr</text>')
    else:
        body.append(f'<text class="txt" x="{MARGIN + 4}" y="{MARGIN + 62}">noch keine Daten</text>')
    if peak_i is not None:
        start = date.fromisoformat(weeks[peak_i]["start"]).strftime("%d.%m.%Y")
        x = tok["canvas.width"] - MARGIN - 4
        body.append(f'<text class="mut" x="{x}" y="{height - MARGIN - 34}" text-anchor="end">stärkste Woche</text>')
        body.append(f'<text class="txt" x="{x}" y="{height - MARGIN}" text-anchor="end">{peak} ab {start}</text>')

    if tok.data:
        label = (f"Isometrische Skyline aus {n} Säulen, eine pro Woche: {total} Contributions im "
                 f"letzten Jahr, die stärkste Woche ({peak}) ist hervorgehoben.")
    else:
        label = "Isometrische Skyline der Contributions der letzten 52 Wochen – noch keine Daten vorhanden."
    return document(tok, height, label, "\n".join(body), "\n".join(css))
