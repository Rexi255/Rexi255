"""Hero, Variante B: Netzwerktopologie (Router -> Switch -> Server), Name im Zentrum."""

import dotmatrix
from _scene import document, floor_grid, link, matrix_flat, packet, router, server, switch
from svglib import Iso

HEIGHT = 480


def render(tok):
    width = tok["canvas.width"]
    name, role = tok["profile.name"], tok["profile.role"]
    iso = Iso(tok, origin=(width / 2, 330))
    body = [floor_grid(iso, -12, -12, 12, 12, 2)]

    # Verbindungen (zuerst, damit Knoten darüber liegen)
    body.append(link(iso, (-9.5, -8), (-9.5, 0), (-3.5, 0)))   # Router -> Switch
    body.append(link(iso, (3.5, 0), (8, 0), (8, -6)))           # Switch -> Server hinten rechts
    body.append(link(iso, (3.5, 1), (9, 1), (9, 5)))            # Switch -> Server vorne rechts
    body.append(link(iso, (0, 1.5), (0, 9)))                    # Switch -> Server vorne
    body.append(link(iso, (-2, 1.5), (-2, 6), (-7, 6)))         # Switch -> Server vorne links
    for x, y in ((-9.5, -4), (5.8, 0), (0, 5.5), (-4.5, 6)):
        body.append(packet(iso, x, y))

    # Knoten von hinten nach vorne
    body.append(router(iso, -11, -10.5))
    body.append(server(iso, 7, -9))
    body.append(switch(iso, -3.5, -1.5))
    body.append(server(iso, -9, 5))
    body.append(server(iso, 8, 5))
    body.append(server(iso, -1, 9))

    # Name flach als Dot-Matrix, darunter die Rolle
    pitch, r = 11, 4.2
    x0 = (width - dotmatrix.width(name) * pitch) / 2
    body.append(matrix_flat(name, x0, 20, pitch, r))
    body.append(f'<text class="mut" x="{width / 2}" y="132" text-anchor="middle">{role}</text>')

    label = (f"{name} in leuchtender Punktschrift über einer isometrischen Netzwerktopologie: "
             f"Router, Switch und vier Server, verbunden durch Leitungen mit Datenpaketen. "
             f"Darunter: {role}.")
    return document(tok, HEIGHT, label, "\n".join(body))
