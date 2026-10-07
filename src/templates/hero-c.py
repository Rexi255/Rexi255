"""Hero, Variante C: Rack links, Topologie rechts, Pakete fließen dazwischen."""

import dotmatrix
from _scene import Face, box, document, floor_grid, link, matrix_flat, packet, server, switch
from svglib import Iso, num

HEIGHT = 480
RACK = (0, 0, 8, 8, 19)  # x, y, Breite, Tiefe, Höhe


def rack(iso):
    x, y, w, d, h = RACK
    out = [box(iso, x, y, 0, w, d, h)]
    front = Face(iso, "left", x, y + d, 0)
    out.append(front.lines([((0.8, 0.5), (0.8, h - 0.5)), ((w - 0.8, 0.5), (w - 0.8, h - 0.5))]))
    # Einschübe von unten nach oben: (Höhe, Anzahl LEDs)
    v = 1.0
    for units, leds in ((3, 2), (2, 2), (1.2, 3), (2, 1), (1.2, 3), (3, 2), (2, 2)):
        out.append(front.rect(1.1, v, w - 2.2, units - 0.3, "p"))
        out.append(front.dots([(w - 1.7 - i * 0.6, v + units - 0.75) for i in range(leds)], 2.2, "ok"))
        out.append(front.lines([((1.6, v + 0.4), (w - 3.4, v + 0.4))]))
        v += units + 0.2
    side = Face(iso, "right", x + w, y, 0)
    out.append(side.lines([((1.2, vv), (d - 1.2, vv)) for vv in (2.5, 3.1, 3.7, 15.5, 16.1, 16.7)]))
    (a, b), (c, e) = iso.point(x, y + d, h), iso.point(x + w, y + d, h)
    out.append(f'<path class="edge-glow" d="M{num(a)} {num(b)}L{num(c)} {num(e)}"/>')
    return "".join(out)


def render(tok):
    name, role = tok["profile.name"], tok["profile.role"]
    iso = Iso(tok, origin=(170, 250))
    body = [floor_grid(iso, 6, -24, 36, 2, 2)]

    # Leitungen
    body.append(link(iso, (8, 1), (22, 1), (22, -9)))        # Rack -> Switch
    body.append(link(iso, (27, -11), (31, -11), (31, -20)))  # Switch -> Server hinten
    body.append(link(iso, (27, -10), (35, -10), (35, -12)))  # Switch -> Server rechts
    body.append(link(iso, (24, -9), (24, -3), (29, -3)))     # Switch -> Server vorne
    for x, y in ((13, 1), (22, -4), (31, -15), (26.5, -3)):
        body.append(packet(iso, x, y))

    # Knoten von hinten nach vorne
    body.append(server(iso, 30, -22))
    body.append(switch(iso, 20, -12))
    body.append(server(iso, 34, -14))
    body.append(server(iso, 29, -4))
    body.append(rack(iso))

    # Name + Rolle oben rechts
    pitch, r = 9, 3.5
    x0 = 860 - dotmatrix.width(name) * pitch
    body.append(matrix_flat(name, x0, 36, pitch, r))
    words = role.split(" ")
    lines = [" ".join(words[:2]), " ".join(words[2:])]
    for i, line in enumerate(lines):
        body.append(f'<text class="mut" x="860" y="{136 + i * 34}" text-anchor="end">{line}</text>')

    label = (f"Isometrisches Server-Rack links, rechts ein Netzwerk aus Switch und drei Servern, "
             f"dazwischen Leitungen mit Datenpaketen. Oben rechts {name} in leuchtender Punktschrift, "
             f"darunter: {role}.")
    return document(tok, HEIGHT, label, "\n".join(body))
