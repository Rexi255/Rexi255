"""Hero, Variante A: isometrisches Server-Rack, Name auf einem Display-Einschub."""

import dotmatrix
from _scene import Face, box, document, matrix_uv, poly
from svglib import Iso, num

HEIGHT = 480
RACK_W, RACK_D, RACK_H = 30, 9, 18


def render(tok):
    iso = Iso(tok, origin=(134, 231))
    name, role = tok["profile.name"], tok["profile.role"]
    body = [box(iso, 0, 0, 0, RACK_W, RACK_D, RACK_H)]

    front = Face(iso, "left", 0, RACK_D, 0)
    side = Face(iso, "right", RACK_W, 0, 0)

    # Montageschienen
    body.append(front.lines([((1, 0.5), (1, RACK_H - 0.5)), ((RACK_W - 1, 0.5), (RACK_W - 1, RACK_H - 0.5))]))

    # Patchpanel oben: Port-Reihe + LEDs
    body.append(front.rect(1.4, 15.6, RACK_W - 2.8, 1.8, "p"))
    body.append("".join(front.rect(2.2 + i * 1.3, 16.0, 0.8, 0.8, "s") for i in range(19)))
    body.append(front.dots([(2.6 + i * 1.3, 17.05) for i in range(19) if i % 3 != 1], 1.6, "ok"))

    # Display-Einschub mit dem Namen
    body.append(front.rect(1.4, 7.6, RACK_W - 2.8, 7.6, "p"))
    body.append(front.rect(2.0, 8.2, RACK_W - 4.0, 6.4, "s"))
    pitch = 0.62
    cols = dotmatrix.width(name)
    u0 = 2.0 + (RACK_W - 4.0 - cols * pitch) / 2
    v_top = 8.2 + (6.4 + 7 * pitch) / 2
    on, off = matrix_uv(name, u0, v_top, pitch)
    body.append(front.dots(off, 1.2, "off"))
    body.append(front.dots(on, 2.6, "on"))

    # Server-Einschübe: Laufwerksschächte + Status-LEDs
    for v, h in ((4.4, 2.8), (1.0, 3.0)):
        body.append(front.rect(1.4, v, RACK_W - 2.8, h, "p"))
        body.append(front.lines([((2.6 + i * 1.2, v + 0.5), (2.6 + i * 1.2, v + h - 0.5)) for i in range(19)]))
        body.append(front.dots([(RACK_W - 3.2, v + h - 0.7), (RACK_W - 2.4, v + h - 0.7)], 2.4, "ok"))
    body.append(front.dots([(RACK_W - 2.4, 1.7)], 2.4, "warn"))

    # Seitenwand: Lüftungsschlitze
    body.append(side.lines([((1.5, v), (RACK_D - 1.5, v)) for v in (3, 3.6, 4.2, 13.8, 14.4, 15)]))

    # Akzentkante oben vorne
    (a, b), (c, d) = iso.point(0, RACK_D, RACK_H), iso.point(RACK_W, RACK_D, RACK_H)
    body.append(f'<path class="edge-glow" d="M{num(a)} {num(b)}L{num(c)} {num(d)}"/>')

    # Rolle rechts als Terminal-Ausgabe
    words = role.split(" ")
    lines = [words[0], " ".join(words[1:3]), " ".join(words[3:])]
    x, y = 520, 190
    body.append(f'<text class="mut" x="{x}" y="{y}">&gt; whoami</text>')
    for i, line in enumerate(lines):
        body.append(f'<text class="txt" x="{x}" y="{y + 44 + i * 36}">{line}</text>')

    label = f"Isometrisches Server-Rack, auf dem Display-Einschub leuchtet {name} in Punktschrift. Daneben: {role}."
    return document(tok, HEIGHT, label, "\n".join(body))
