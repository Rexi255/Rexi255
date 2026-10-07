"""Stack-Rack: Skills als Rack-Einschübe mit Status-LEDs, beschriftet per Callout.

Daten: tokens.json -> skills (Gruppe + Einträge). Neue Skills = nur JSON ändern.
Jeder Einschub ist so hoch wie sein Beschriftungsblock, dadurch laufen alle
Führungslinien waagerecht. Die Einschub-Front ist die rechte Quaderseite
und zeigt zu den Beschriftungen.

Animation: startet erst nach dem Hero-Boot (gemeinsamer Zeitplan). LEDs
gehen von oben nach unten an, danach blinken zwei Aktivitäts-LEDs sehr ruhig.
"""

import html

from _scene import Face, anim, boot_schedule, box, circles, document, secs, style
from svglib import Iso, num

LINE = 30          # Zeilenabstand im Callout (px)
PAD = 12           # Luft über/unter jedem Block (px)
DEPTH, FRONT = 6, 8  # Rack-Tiefe (x) und Front-Breite (y) in Rastereinheiten
LABEL_X = 250      # Beginn der Beschriftungsspalte (px)
MARGIN = 20


def wrap(items, max_chars):
    """Einträge mit " · " verbinden, bei Bedarf auf mehrere Zeilen."""
    lines, current = [], ""
    for item in items:
        candidate = f"{current} · {item}" if current else item
        if current and len(candidate) > max_chars:
            lines.append(current)
            current = item
        else:
            current = candidate
    return lines + [current] if current else lines


def render(tok):
    width, unit = tok["canvas.width"], tok["grid.unit"]
    char_w = tok["font.size.min"] * 0.6  # Monospace: ca. 0,6 em je Zeichen
    max_chars = int((width - MARGIN - LABEL_X) / char_w)

    groups = []
    for g in tok.raw["skills"]:
        lines = [] if g["items"] == [g["group"]] else wrap(g["items"], max_chars)
        groups.append((g["group"], lines))
    heights = [((1 + len(lines)) * LINE + 2 * PAD) / unit for _, lines in groups]
    rack_h = sum(heights) + 1.0

    oy = MARGIN + rack_h * unit
    iso = Iso(tok, origin=(130, oy))
    height = round(oy + (DEPTH + FRONT) * unit / 2 + MARGIN)

    ease = tok["motion.ease"]
    fast, step = secs(tok["motion.fast"]), secs(tok["motion.stagger"])
    t0 = boot_schedule(tok)["end"]
    calm = secs(tok["motion.ambient-max"])

    body = [box(iso, 0, 0, 0, DEPTH, FRONT, rack_h)]
    front = Face(iso, "right", DEPTH, 0, 0)
    edge_x, _ = iso.point(DEPTH, 0)
    css = [
        "@keyframes fade { from { opacity: 0; } }",
        "@keyframes blink { 0%, 88%, 100% { opacity: 1; } 91% { opacity: 0.15; } }",
        f".hdr {{ fill: {tok['color.accent']}; }}",
    ]
    labels, alt = [], []

    z_top = rack_h - 0.5
    for i, ((group, lines), h) in enumerate(zip(groups, heights)):
        z_bot = z_top - h
        body.append(front.rect(0.5, z_bot + 0.15, FRONT - 1, h - 0.3, "p"))
        vents = []
        v = z_bot + 0.8
        while v <= z_top - 0.7:
            vents.append(((3.2, v), (FRONT - 1.0, v)))
            v += 0.8
        body.append(front.lines(vents))

        # Status-LED (ok) + Aktivitäts-LED (accent): erst "aus", dann an
        z_mid = (z_bot + z_top) / 2
        status, activity = (1.1, z_mid), (1.8, z_mid)
        body.append(front.dots([status, activity], 2.6, "off"))
        body.append(front.dots([status], 2.6, "ok", style(anim("fade", fast, t0 + i * step, "steps(2)"))))
        act = [anim("fade", fast, t0 + i * step + step / 2, "steps(2)")]
        if i in (1, 4):
            act.append(anim("blink", calm, t0 + 2 + i, "steps(1)", "infinite"))
        body.append(front.dots([activity], 2.6, "acc", style(*act)))

        # Callout: Führungslinie vom Einschub zur Beschriftung
        _, ay = iso.point(DEPTH, 0, z_mid)
        body.append(f'<path class="link" d="M{num(edge_x + 8)} {num(ay)}H{LABEL_X - 14}"/>')
        body.append(f'<path class="acc" d="{circles([(LABEL_X - 14, ay)], 3)}"/>')
        block = (1 + len(lines)) * LINE
        y = ay - block / 2 + LINE * 0.72
        labels.append(f'<text class="hdr" x="{LABEL_X}" y="{num(y)}">{html.escape(group)}</text>')
        for j, line in enumerate(lines, 1):
            labels.append(f'<text class="txt" x="{LABEL_X}" y="{num(y + j * LINE)}">{html.escape(line)}</text>')
        alt.append(group + (": " + ", ".join(lines) if lines else ""))
        z_top = z_bot

    # Akzentkante oben an der Front
    (a, b), (c, d) = iso.point(DEPTH, 0, rack_h), iso.point(DEPTH, FRONT, rack_h)
    body.append(f'<path class="edge-glow" d="M{num(a)} {num(b)}L{num(c)} {num(d)}"/>')

    label = ("Isometrisches Server-Rack mit sechs Einschüben und grünen Status-LEDs, "
             "jeder Einschub ist beschriftet: " + "; ".join(alt) + ".")
    return document(tok, height, html.escape(label, quote=True), "\n".join(body + labels), "\n".join(css))
