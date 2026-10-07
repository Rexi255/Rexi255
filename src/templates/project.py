"""Projektkarten (440 px breit, zwei nebeneinander): eine Karte pro Projekt.

Daten: tokens.json -> projects (name, text, tags, optional url).
Alle Karten bekommen dieselbe Höhe (die der längsten), damit sie bündig
nebeneinander stehen. Karten mit url zeigen einen Link-Pfeil; verlinkt
werden sie in der README (Bilder selbst können nicht klicken).

Animation: Tags blenden nach dem Hero-Boot nacheinander ein, die Status-LED
oben rechts blinkt danach sehr ruhig. reduced motion: alles sichtbar, ruhig.
"""

import html

from _scene import anim, boot_schedule, circles, document, secs, style, word_wrap
from svglib import num

PAD = 28
TITLE_Y = 56
LINE = 30
TAG_H = 36
TAG_GAP = 10


def variants(tok):
    return [str(i + 1) for i in range(len(tok.raw["projects"]))]


def layout(tok, project):
    """-> (Beschreibungszeilen, Tag-Zeilen [[(tag, breite), ...], ...])"""
    width = tok["canvas.card-width"]
    char_w = tok["font.size.min"] * 0.6
    lines = word_wrap(project["text"], int((width - 2 * PAD) / char_w))
    rows, row, used = [], [], 0
    for tag in project["tags"]:
        w = len(tag) * char_w + 28
        if row and used + w > width - 2 * PAD:
            rows.append(row)
            row, used = [], 0
        row.append((tag, w))
        used += w + TAG_GAP
    return lines, rows + [row] if row else rows


def render(tok, key):
    width = tok["canvas.card-width"]
    index = int(key) - 1
    project = tok.raw["projects"][index]

    # gemeinsame Höhe: die der längsten Karte
    layouts = [layout(tok, p) for p in tok.raw["projects"]]
    max_lines = max(len(lines) for lines, _ in layouts)
    max_rows = max(len(rows) for _, rows in layouts)
    tags_y = TITLE_Y + 46 + max_lines * LINE + 6
    height = tags_y + max_rows * (TAG_H + TAG_GAP) - TAG_GAP + PAD
    lines, rows = layouts[index]

    fast, step = secs(tok["motion.fast"]), secs(tok["motion.stagger"])
    t0 = boot_schedule(tok)["projects"] + index * step * 2
    css = [
        "@keyframes fade { from { opacity: 0; } }",
        "@keyframes blink { 0%, 90%, 100% { opacity: 1; } 94% { opacity: 0.15; } }",
        f".hdr {{ fill: {tok['color.accent']}; }}",
        f".title {{ font-weight: 700; fill: {tok['color.text']}; }}",
        f".tag {{ fill: none; stroke: {tok['color.accent']}; stroke-opacity: 0.6; stroke-width: 1.5; }}",
        f".arrow {{ fill: none; stroke: {tok['color.accent']}; stroke-width: 2.5; stroke-linecap: round; stroke-linejoin: round; }}",
    ]
    name = html.escape(project["name"])
    body = [f'<text x="{PAD}" y="{TITLE_Y}"><tspan class="hdr">&gt; </tspan>'
            f'<tspan class="title">{name}</tspan></text>']

    # Nummer + Status-LED oben rechts
    num_x = width - PAD
    body.append(f'<text class="mut" x="{num_x}" y="{TITLE_Y}" text-anchor="end">{int(key):02d}</text>')
    led = style(anim("fade", fast, t0, "steps(2)"),
                anim("blink", secs(tok["motion.ambient-max"]), t0 + 3 + index * 2, "steps(1)", "infinite"))
    body.append(f'<path class="ok" style="{led}" d="{circles([(num_x - 46, TITLE_Y - 8)], 5)}"/>')

    # Link-Pfeil hinter dem Titel, wenn verlinkt
    if project.get("url"):
        ax = PAD + (len(project["name"]) + 2) * tok["font.size.min"] * 0.6 + 8
        ay = TITLE_Y - 8
        body.append(f'<path class="arrow" d="M{num(ax)} {num(ay + 7)}l12 -12M{num(ax + 2)} {num(ay - 5)}h10v10"/>')

    body.append(f'<path class="ln" d="M{PAD} {TITLE_Y + 22}H{width - PAD}"/>')
    for i, line in enumerate(lines):
        body.append(f'<text class="mut" x="{PAD}" y="{TITLE_Y + 62 + i * LINE}">{html.escape(line)}</text>')

    k = 0
    for r, row in enumerate(rows):
        x = PAD
        y = tags_y + r * (TAG_H + TAG_GAP)
        for tag, w in row:
            st = style(anim("fade", fast, t0 + k * step / 2, "steps(2)"))
            body.append(f'<g style="{st}"><rect class="tag" x="{num(x)}" y="{num(y)}" width="{num(w)}" '
                        f'height="{TAG_H}" rx="{TAG_H / 2}"/>'
                        f'<text class="hdr" x="{num(x + w / 2)}" y="{num(y + TAG_H / 2 + 8)}" '
                        f'text-anchor="middle">{html.escape(tag)}</text></g>')
            x += w + TAG_GAP
            k += 1

    label = (f"Projektkarte {int(key):02d}: {project['name']} – {project['text']}. "
             f"Stichworte: {', '.join(project['tags'])}.")
    return document(tok, height, html.escape(label, quote=True), "\n".join(body), "\n".join(css), width=width)
