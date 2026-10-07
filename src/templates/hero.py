"""Hero (kompakt): links Name als Dot-Matrix + Rolle, rechts kleine Netzwerktopologie.

Boot-Sequenz (einmalig, ca. 4 s), gestaffelt:
  1. Bodenraster und unbeleuchtete Display-Punkte blenden ein
  2. Knoten bauen sich nacheinander auf, ihre LEDs gehen danach an
  3. Leitungen zeichnen sich
  4. Name leuchtet Zeile für Zeile auf, danach Rolle und "system online"
Danach Ambient-Loop: Pakete fahren versetzt über die Leitungen,
einzelne LEDs blinken mit verschiedenen Ambient-Dauern.

Alle Normalwerte im CSS sind der Endzustand. prefers-reduced-motion
schaltet die Animationen ab -> statisches Bild wie nach dem Boot.
"""

import dotmatrix
from _scene import (anim, boot_schedule, circles, document, floor_grid, link, packet_shape,
                    path_keyframes, router, secs, server, style, switch)
from svglib import Iso, num

HEIGHT = 300
PAD = 40           # Innenabstand links
TOPO_CENTER = (668, 168)

# Knoten in Zeichenreihenfolge (hinten nach vorne): (Funktion, x, y, Extras)
NODES = [
    (router, -6.5, -6, {}),
    (server, 5, -6.5, {}),
    (switch, -2.5, -1, {"w": 4, "d": 2.5}),
    (server, -7, 2.5, {}),
    (server, 6, 0.5, {}),
]

# Leitungen als Iso-Punkte (x, y) und Ruheposition des Pakets darauf
LINKS = [
    ([(-5, -3), (-5, 0), (-2.5, 0)], (-5, -1.5)),       # Router -> Switch
    ([(0, -1), (0, -5.5), (5, -5.5)], (2.5, -5.5)),      # Switch -> Server hinten rechts
    ([(1.5, 1), (6, 1)], (4, 1)),                         # Switch -> Server vorne rechts
    ([(-1, 1.5), (-1, 3.5), (-5, 3.5)], (-3, 3.5)),      # Switch -> Server vorne links
]

# LEDs, die im Ambient-Loop blinken: Knotenindex -> Dauer-Token
BLINKERS = {1: "motion.ambient-min", 3: "motion.ambient", 4: "motion.ambient-max"}


def render(tok):
    name, role = tok["profile.name"], tok["profile.role"]
    iso = Iso(tok, origin=TOPO_CENTER)
    ox, oy = iso.point(0, 0)

    ease = tok["motion.ease"]
    fast = secs(tok["motion.fast"])
    step = secs(tok["motion.stagger"])
    rise = tok["grid.unit"]
    ambient = secs(tok["motion.ambient"])

    t = boot_schedule(tok, len(NODES))

    css = [
        "@keyframes fade { from { opacity: 0; } }",
        f"@keyframes rise {{ from {{ opacity: 0; transform: translateY({rise}px); }} }}",
        "@keyframes draw { from { stroke-dashoffset: 100; } }",
        "@keyframes blink { 0%, 90%, 100% { opacity: 1; } 93% { opacity: 0.15; } }",
        ".link { stroke-dasharray: 100; }",
        f".arrow {{ fill: {tok['color.accent']}; }}",
    ]
    body = [f'<g style="{style(anim("fade", fast, 0, ease))}">{floor_grid(iso, -8, -8, 8, 8, 2)}</g>']

    for i, (pts, _) in enumerate(LINKS):
        body.append(link(iso, *pts, style=style(anim("draw", fast * 1.5, t["links"] + i * step / 2, ease))))

    # Pakete: Ruheposition = Endzustand (reduced motion). Mit Animation sind sie
    # während des Boots ausgeblendet und fahren danach versetzt über ihre Leitung.
    shape = packet_shape(iso)
    for i, (pts, rest) in enumerate(LINKS):
        screen = [(x - ox, y - oy) for x, y in (iso.point(px, py) for px, py in pts)]
        css.append(path_keyframes(f"pk{i}", screen, 0, 30))
        rx, ry = iso.point(*rest)
        delay = t["end"] + i * ambient / len(LINKS)
        st = (f"transform: translate({num(rx - ox)}px, {num(ry - oy)}px); "
              + style(anim(f"pk{i}", ambient, delay, ease, "backwards infinite")))
        body.append(f'<g transform="translate({num(ox)} {num(oy)})"><g style="{st}">{shape}</g></g>')

    # Knoten: aufbauen, danach LEDs an (+ einzelne blinken im Loop)
    for i, (fn, x, y, extra) in enumerate(NODES):
        led = [anim("fade", fast, t["nodes"][i] + fast, "steps(2)")]
        if i in BLINKERS:
            led.append(anim("blink", secs(tok[BLINKERS[i]]), t["end"] + i * 0.7, "steps(1)", "infinite"))
        node_svg = fn(iso, x, y, led_style=style(*led), **extra)
        body.append(f'<g style="{style(anim("rise", fast, t["nodes"][i], ease))}">{node_svg}</g>')

    # Name: Dot-Matrix, Aus-Punkte mit dem Raster, An-Punkte Zeile für Zeile
    pitch, r = 8.4, 3.2
    x0, y0 = PAD, 44
    rows = [[] for _ in range(dotmatrix.ROWS)]
    off = []
    for col, row, lit in dotmatrix.cells(name):
        center = (x0 + (col + 0.5) * pitch, y0 + (row + 0.5) * pitch)
        (rows[row] if lit else off).append(center)
    body.append(f'<path class="off" style="{style(anim("fade", fast, 0, ease))}" d="{circles(off, r * 0.45)}"/>')
    for i, centers in enumerate(rows):
        st = style(anim("fade", fast / 2, t["name"] + i * t["row_step"], "steps(2)"))
        body.append(f'<path class="on" style="{st}" d="{circles(centers, r)}"/>')

    # Rolle (zweizeilig) und Status, nacheinander nach dem Namen
    words = role.split(" ")
    role_lines = [" ".join(words[:2]), " ".join(words[2:])]
    t_role = t["name"] + dotmatrix.ROWS * t["row_step"] + fast
    y = 156
    for i, line in enumerate(role_lines):
        prefix = '<tspan class="arrow">&gt; </tspan>' if i == 0 else '<tspan xml:space="preserve">  </tspan>'
        st = style(anim("fade", fast, t_role + i * step, ease))
        body.append(f'<text class="txt" x="{PAD}" y="{y + i * 34}" style="{st}">{prefix}{line}</text>')
    st = style(anim("fade", fast, t_role + 2 * step + fast, "steps(2)"))
    body.append(f'<g style="{st}"><circle class="ok" cx="{PAD + 7}" cy="{y + 2 * 34 + 26}" r="5"/>'
                f'<text class="mut" x="{PAD + 22}" y="{y + 2 * 34 + 34}">system online</text></g>')

    label = (f"{name} in leuchtender Punktschrift, darunter: {role}, system online. "
             f"Rechts eine isometrische Netzwerktopologie aus Router, Switch und drei Servern, "
             f"über deren Leitungen Datenpakete fließen.")
    return document(tok, HEIGHT, label, "\n".join(body), "\n".join(css))
