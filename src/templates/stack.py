"""Bereiche (kompakt): schmales Rack, je Einschub eine Zeile "Gruppe  Einträge".

Daten: tokens.json -> skills (Gruppe + Einträge). Neue Skills = nur JSON ändern.
Gruppenname (accent) und Einträge stehen in einer Zeile; nur zu lange
Einträge brechen um. Jeder Einschub ist so hoch wie seine Zeilen, dadurch
laufen alle Führungslinien waagerecht. Die Einschub-Front ist die rechte
Quaderseite und zeigt zu den Beschriftungen.

Animation: startet nach dem Hero-Boot (gemeinsamer Zeitplan). LEDs gehen
von oben nach unten an, danach blinken zwei Aktivitäts-LEDs sehr ruhig.
"""

import html

from _scene import Face, anim, boot_schedule, box, circles, document, secs, style
from svglib import Iso, num

LINE = 28            # Zeilenabstand (px)
PAD = 3              # Luft über/unter jeder Zeilengruppe (px)
DEPTH, FRONT = 3, 5  # Rack-Tiefe (x) und Front-Breite (y) in Rastereinheiten
MARGIN = 24
GROUP_X = 150        # Spalte Gruppenname (px)


def wrap(items, max_chars):
    """Einträge mit " · " verbinden; umbrechen bevorzugt zwischen Einträgen,
    nur ein einzelner zu langer Eintrag wird an Wortgrenzen geteilt."""
    lines, current = [], ""
    for item in items:
        candidate = f"{current} · {item}" if current else item
        if len(candidate) <= max_chars:
            current = candidate
            continue
        if current:
            lines.append(current)
        current = ""
        for word in item.split():
            candidate = f"{current} {word}" if current else word
            if current and len(candidate) > max_chars:
                lines.append(current)
                current = word
            else:
                current = candidate
    return lines + [current] if current else lines


def render(tok):
    width, unit = tok["canvas.width"], tok["grid.unit"]
    char_w = tok["font.size.min"] * 0.6  # Monospace: ca. 0,6 em je Zeichen
    longest_group = max(len(g["group"]) for g in tok.raw["skills"])
    items_x = GROUP_X + (longest_group + 1) * char_w
    max_chars = int((width - MARGIN - items_x) / char_w)

    groups, alt = [], []
    for g in tok.raw["skills"]:
        own = g["items"] != [g["group"]]
        groups.append((g["group"], wrap(g["items"], max_chars) if own else []))
        alt.append(g["group"] + (": " + ", ".join(g["items"]) if own else ""))
    heights = [(max(1, len(lines)) * LINE + 2 * PAD) / unit for _, lines in groups]
    rack_h = sum(heights) + 0.6

    oy = MARGIN + rack_h * unit
    iso = Iso(tok, origin=(MARGIN + FRONT * unit * 0.866 + 6, oy))
    height = round(oy + (DEPTH + FRONT) * unit / 2 + MARGIN)

    fast, step = secs(tok["motion.fast"]), secs(tok["motion.stagger"])
    t0 = boot_schedule(tok)["stack"]
    calm = secs(tok["motion.ambient-max"])

    body = [box(iso, 0, 0, 0, DEPTH, FRONT, rack_h)]
    front = Face(iso, "right", DEPTH, 0, 0)
    edge_x, _ = iso.point(DEPTH, 0)
    css = [
        "@keyframes fade { from { opacity: 0; } }",
        "@keyframes blink { 0%, 88%, 100% { opacity: 1; } 91% { opacity: 0.15; } }",
        f".hdr {{ fill: {tok['color.accent']}; }}",
    ]
    labels = []

    z_top = rack_h - 0.3
    for i, ((group, lines), h) in enumerate(zip(groups, heights)):
        z_bot = z_top - h
        body.append(front.rect(0.4, z_bot + 0.1, FRONT - 0.8, h - 0.2, "p"))
        vents = []
        v = z_bot + 0.7
        while v <= z_top - 0.6:
            vents.append(((2.4, v), (FRONT - 0.7, v)))
            v += 0.7
        body.append(front.lines(vents))

        # Status-LED (ok) + Aktivitäts-LED (accent) auf Höhe der ersten Zeile
        z_line = z_top - (PAD + LINE / 2) / unit
        status, activity = (0.9, z_line), (1.6, z_line)
        body.append(front.dots([status, activity], 2.4, "off"))
        body.append(front.dots([status], 2.4, "ok", style(anim("fade", fast, t0 + i * step, "steps(2)"))))
        act = [anim("fade", fast, t0 + i * step + step / 2, "steps(2)")]
        if i in (1, 4):
            act.append(anim("blink", calm, t0 + 2 + i, "steps(1)", "infinite"))
        body.append(front.dots([activity], 2.4, "acc", style(*act)))

        # Führungslinie vom Einschub zur Zeile, dann Gruppe + Einträge
        _, ay = iso.point(DEPTH, 0, z_line)
        body.append(f'<path class="link" d="M{num(edge_x + 8)} {num(ay)}H{GROUP_X - 14}"/>')
        body.append(f'<path class="acc" d="{circles([(GROUP_X - 14, ay)], 3)}"/>')
        y = ay + LINE * 0.22
        labels.append(f'<text class="hdr" x="{GROUP_X}" y="{num(y)}">{html.escape(group)}</text>')
        for j, line in enumerate(lines):
            labels.append(f'<text class="txt" x="{num(items_x)}" y="{num(y + j * LINE)}">{html.escape(line)}</text>')
        z_top = z_bot

    # Akzentkante oben an der Front
    (a, b), (c, d) = iso.point(DEPTH, 0, rack_h), iso.point(DEPTH, FRONT, rack_h)
    body.append(f'<path class="edge-glow" d="M{num(a)} {num(b)}L{num(c)} {num(d)}"/>')

    label = (f"Schmales isometrisches Server-Rack mit {len(groups)} Einschüben und grünen Status-LEDs, "
             "jeder Einschub ist beschriftet: " + "; ".join(alt) + ".")
    return document(tok, height, html.escape(label, quote=True), "\n".join(body + labels), "\n".join(css))
