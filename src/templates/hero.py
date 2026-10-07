"""Hero: Netzwerktopologie (Router -> Switch -> Server), Name als Dot-Matrix.

Boot-Sequenz (einmalig, ca. 4 s), gestaffelt:
  1. Bodenraster und unbeleuchtete Display-Punkte blenden ein
  2. Knoten bauen sich nacheinander auf, ihre LEDs gehen danach an
  3. Leitungen zeichnen sich
  4. Name leuchtet Zeile für Zeile auf
  5. kurz "system online", danach die Rollenzeile
Danach Ambient-Loop: Pakete fahren versetzt über die Leitungen,
einzelne LEDs blinken mit verschiedenen Ambient-Dauern.

Alle Normalwerte im CSS sind der Endzustand. prefers-reduced-motion
schaltet die Animationen ab -> statisches Bild wie nach dem Boot.
"""

import dotmatrix
from _scene import (anim, boot_schedule, circles, document, floor_grid, link, packet_shape, path_keyframes,
                    router, secs, server, style, switch)
from svglib import Iso, num

HEIGHT = 480

# Knoten in Zeichenreihenfolge (hinten nach vorne): (Funktion, x, y)
NODES = [(router, -11, -10.5), (server, 7, -9), (switch, -3.5, -1.5),
         (server, -9, 5), (server, 8, 5), (server, -1, 9)]

# Leitungen als Iso-Punkte (x, y) und Ruheposition des Pakets darauf
LINKS = [
    ([(-9.5, -8), (-9.5, 0), (-3.5, 0)], (-9.5, -4)),     # Router -> Switch
    ([(3.5, 0), (8, 0), (8, -6)], (5.8, 0)),               # Switch -> Server hinten rechts
    ([(3.5, 1), (9, 1), (9, 5)], (9, 2.5)),                # Switch -> Server vorne rechts
    ([(0, 1.5), (0, 9)], (0, 5.5)),                        # Switch -> Server vorne
    ([(-2, 1.5), (-2, 6), (-7, 6)], (-4.5, 6)),            # Switch -> Server vorne links
]

# LEDs, die im Ambient-Loop blinken: Knotenindex -> Dauer-Token
BLINKERS = {1: "motion.ambient-min", 4: "motion.ambient-max", 2: "motion.ambient"}


def render(tok):
    width = tok["canvas.width"]
    name, role = tok["profile.name"], tok["profile.role"]
    iso = Iso(tok, origin=(width / 2, 330))
    ox, oy = iso.point(0, 0)

    ease = tok["motion.ease"]
    fast, base = secs(tok["motion.fast"]), secs(tok["motion.base"])
    step = secs(tok["motion.stagger"])
    rise = tok["grid.unit"]

    # --- Zeitplan der Boot-Sequenz (Sekunden), gemeinsam mit anderen Grafiken ---
    t = boot_schedule(tok, len(NODES))
    node_delay, t_links, t_name = t["nodes"], t["links"], t["name"]
    row_step, t_sys, t_role, t_ambient = t["row_step"], t["sys"], t["role"], t["end"]

    css = [
        f"@keyframes fade {{ from {{ opacity: 0; }} }}",
        f"@keyframes rise {{ from {{ opacity: 0; transform: translateY({rise}px); }} }}",
        "@keyframes draw { from { stroke-dashoffset: 100; } }",
        "@keyframes sys { 0%, 100% { opacity: 0; } 20%, 80% { opacity: 1; } }",
        "@keyframes blink { 0%, 90%, 100% { opacity: 1; } 93% { opacity: 0.15; } }",
        ".link { stroke-dasharray: 100; }",
        ".sys { opacity: 0; }",
    ]
    body = [f'<g style="{style(anim("fade", fast, 0, ease))}">{floor_grid(iso, -12, -12, 12, 12, 2)}</g>']

    # Leitungen (unter den Knoten)
    for i, (pts, _) in enumerate(LINKS):
        body.append(link(iso, *pts, style=style(anim("draw", fast * 1.5, t_links + i * step / 2, ease))))

    # Pakete: Ruheposition = Endzustand (reduced motion). Mit Animation sind sie
    # während des Boots ausgeblendet (backwards-Fill der Schleife) und fahren
    # danach versetzt über ihre Leitung (Richtung: erster -> letzter Punkt).
    ambient = secs(tok["motion.ambient"])
    shape = packet_shape(iso)
    for i, (pts, rest) in enumerate(LINKS):
        screen = [iso.point(x, y) for x, y in pts]
        screen = [(x - ox, y - oy) for x, y in screen]
        css.append(path_keyframes(f"pk{i}", screen, 0, 30))
        rx, ry = iso.point(*rest)
        delay = t_ambient + i * ambient / len(LINKS)
        st = (f"transform: translate({num(rx - ox)}px, {num(ry - oy)}px); "
              + style(anim(f"pk{i}", ambient, delay, ease, "backwards infinite")))
        body.append(f'<g transform="translate({num(ox)} {num(oy)})"><g style="{st}">{shape}</g></g>')

    # Knoten: aufbauen, danach LEDs an (+ einzelne blinken im Loop)
    for i, (fn, x, y) in enumerate(NODES):
        led = [anim("fade", fast, node_delay[i] + fast, "steps(2)")]
        if i in BLINKERS:
            dur = secs(tok[BLINKERS[i]])
            led.append(anim("blink", dur, t_ambient + i * 0.7, "steps(1)", "infinite"))
        node_svg = fn(iso, x, y, led_style=style(*led))
        body.append(f'<g style="{style(anim("rise", fast, node_delay[i], ease))}">{node_svg}</g>')

    # Name: Dot-Matrix, Aus-Punkte mit dem Raster, An-Punkte Zeile für Zeile
    pitch, r = 11, 4.2
    x0, y0 = (width - dotmatrix.width(name) * pitch) / 2, 20
    rows = [[] for _ in range(dotmatrix.ROWS)]
    off = []
    for col, row, lit in dotmatrix.cells(name):
        center = (x0 + (col + 0.5) * pitch, y0 + (row + 0.5) * pitch)
        (rows[row] if lit else off).append(center)
    body.append(f'<path class="off" style="{style(anim("fade", fast, 0, ease))}" d="{circles(off, r * 0.45)}"/>')
    for i, centers in enumerate(rows):
        st = style(anim("fade", fast / 2, t_name + i * row_step, "steps(2)"))
        body.append(f'<path class="on" style="{st}" d="{circles(centers, r)}"/>')

    # "system online" kurz, danach die Rolle an derselben Stelle
    cx, ty = width / 2, 132
    sys_text = "system online"
    sys_w = len(sys_text) * 14.4  # ca. 0,6 em je Zeichen bei 24 px
    body.append(
        f'<g class="sys" style="{style(anim("sys", base, t_sys, ease))}">'
        f'<circle class="ok" cx="{num(cx - sys_w / 2 - 14)}" cy="{ty - 8}" r="5"/>'
        f'<text class="mut" x="{num(cx + 7)}" y="{ty}" text-anchor="middle">{sys_text}</text></g>'
    )
    body.append(f'<text class="mut" style="{style(anim("fade", fast, t_role, ease))}" '
                f'x="{num(cx)}" y="{ty}" text-anchor="middle">{role}</text>')

    label = (f"{name} in leuchtender Punktschrift über einer isometrischen Netzwerktopologie: "
             f"ein Router, ein Switch und vier Server, verbunden durch Leitungen, über die "
             f"Datenpakete fließen. Darunter: {role}.")
    return document(tok, HEIGHT, label, "\n".join(body), "\n".join(css))
