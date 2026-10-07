"""whoami-Karte: Name, Rolle, Kurztext und Bereiche links, Server-Rack rechts.

Daten: tokens.json -> profile (Name, Person, Rolle, about) und skills.
Die unteren Rack-Einschübe gehören zu den Bereichen: jeder ist genau so
hoch wie seine Textzeilen, seine Status-LED steht exakt auf der Höhe der
LED in der Liste.
Darüber sitzen allgemeine Einheiten (Patchpanel, Switch, Server).

Boot-Sequenz (einmalig, ca. 4 s), gestaffelt:
  1. Rack steigt auf, LEDs der oberen Einheiten gehen an
  2. Name leuchtet Zeile für Zeile auf, danach Rolle und Kurztext
  3. Bereiche gehen nacheinander an: Listen-LED und Einschub-LED gleichzeitig
  4. "system online"
Danach nur ruhige Ambient-Loops: zwei Switch-Ports und zwei Einschübe blinken.

Alle Normalwerte im CSS sind der Endzustand. prefers-reduced-motion
schaltet die Animationen ab -> statisches Bild wie nach dem Boot.
"""

import html

import dotmatrix
from _scene import Face, anim, boot_schedule, box, circles, document, secs, style, word_wrap, wrap_items
from svglib import Iso, num

PAD = 40             # Innenabstand links/oben
PITCH, DOT_R = 8.4, 3.2
LINE = 30            # Zeilenabstand Kopftext
LIST_LINE = 28       # Zeilenabstand Bereiche
GROUP_GAP = 4
FRONT, DEPTH = 10, 3  # Rack: Frontbreite (x) und Tiefe (y) in Rastereinheiten
LED_U = FRONT - 1.9    # Status-LEDs rechts auf der Front; auf ihrer Höhe liegt die Listen-LED
RACK_RIGHT = 48      # Abstand rechte Rack-Kante zum Kartenrand
GAP = 24             # Mindestabstand Text <-> Rack

# Obere Einheiten von oben nach unten: (Art, Höhe in Rastereinheiten);
# die letzte füllt den Rest bis zu den Bereichs-Einschüben.
UNITS = [("patch", 2), ("switch", 2.4), ("server", 3), ("server", 3), ("blank", 0)]
# Switch-Ports, die im Ambient-Loop blinken: Portindex -> Dauer-Token
PORT_BLINK = {2: "motion.ambient-min", 7: "motion.ambient"}
ACTIVITY_BLINK = (1, 4)  # Einschübe mit blinkender Aktivitäts-LED


def port_u(i):
    return 1.1 + i * 0.6


def unit_face(face, kind, v0, h, led_style):
    """Eine Rack-Einheit auf der Front (Face) zwischen v0 und v0 + h."""
    out = [face.rect(0.5, v0 + 0.08, FRONT - 1, h - 0.16, "p")]
    mid = v0 + h / 2
    if kind == "patch":
        ports = int((FRONT - 1.8) / 0.6)
        for row in (mid + 0.35, mid - 0.35):
            out += [face.rect(0.9 + i * 0.6, row - 0.18, 0.38, 0.36, "s") for i in range(ports)]
    elif kind == "switch":
        ports = int((FRONT - 3) / 0.6)
        out += [face.rect(port_u(i) - 0.21, mid - 0.55, 0.42, 0.5, "s") for i in range(ports)]
        steady = [(port_u(i), mid + 0.35) for i in range(ports) if i not in PORT_BLINK]
        out.append(face.dots(steady, 1.4, "ok", led_style))
        out.append(face.dots([(LED_U, mid)], 2.2, "acc", led_style))
    elif kind == "server":
        out.append(face.lines([((0.9, v), (LED_U - 0.8, v)) for v in (mid + 0.6, mid, mid - 0.6)]))
        out.append(face.dots([(LED_U, mid + 0.6)], 2.2, "ok", led_style))
    else:
        v, vents = v0 + 0.6, []
        while v <= v0 + h - 0.5:
            vents.append(((1, v), (FRONT - 1, v)))
            v += 0.6
        out.append(face.lines(vents))
    return "".join(out)


def render(tok):
    width, unit = tok["canvas.width"], tok["grid.unit"]
    char_w = tok["font.size.min"] * 0.6  # Monospace: ca. 0,6 em je Zeichen
    ease = tok["motion.ease"]
    fast, step = secs(tok["motion.fast"]), secs(tok["motion.stagger"])
    t = boot_schedule(tok)

    # --- Textspalte: Positionen ---------------------------------------------
    probe = Iso(tok, origin=(0, 0))
    rack_w = probe.point(FRONT, 0)[0] - probe.point(0, DEPTH)[0]
    text_right = width - RACK_RIGHT - rack_w - GAP

    role_lines = word_wrap(f"{tok['profile.person']} · {tok['profile.role']}", 28)
    about_lines = word_wrap(tok["profile.about"], int((text_right - PAD) / char_w))
    role_y = PAD + dotmatrix.ROWS * PITCH + 42
    about_y = role_y + len(role_lines) * LINE + 12
    rule_y = about_y + (len(about_lines) - 1) * LINE + 30
    list_y = rule_y + 44

    led_x, group_x = PAD + 6, PAD + 22
    items_x = group_x + (max(len(g["group"]) for g in tok.raw["skills"]) + 1) * char_w
    max_chars = int((text_right - items_x) / char_w)
    groups, y = [], list_y
    for g in tok.raw["skills"]:
        own = g["items"] != [g["group"]]
        lines = wrap_items(g["items"], max_chars) if own else []
        n = max(1, len(lines))
        top = y - LIST_LINE * 0.75 - GROUP_GAP / 2
        bottom = y + (n - 1) * LIST_LINE + LIST_LINE * 0.25 + GROUP_GAP / 2
        groups.append({"name": g["group"], "lines": lines, "y": y, "top": top, "bottom": bottom,
                       "alt": g["group"] + (": " + ", ".join(g["items"]) if own else "")})
        y += n * LIST_LINE + GROUP_GAP
    last_y = groups[-1]["y"] + (max(1, len(groups[-1]["lines"])) - 1) * LIST_LINE

    # --- Rack: so tief, dass der unterste Einschub (LED-Spalte) unter der
    # letzten Zeile endet; oben bündig mit dem Namen --------------------------
    mid_dy = probe.point(LED_U, DEPTH)[1]               # LED-Spalte unten relativ zum Ursprung
    oy = groups[-1]["bottom"] + 0.5 * unit - mid_dy      # 0,5 Einheiten Sockel
    ox = width - RACK_RIGHT - probe.point(FRONT, 0)[0]
    iso = Iso(tok, origin=(ox, oy))
    rack_h = (oy - (PAD - 4)) / unit
    height = round(max(oy + probe.point(FRONT, DEPTH)[1], last_y) + 28)

    def v_at(y):
        """Bildschirm-y (in der LED-Spalte) -> Höhe v auf der Rack-Front."""
        return (oy + mid_dy - y) / unit

    css = [
        "@keyframes fade { from { opacity: 0; } }",
        f"@keyframes rise {{ from {{ opacity: 0; transform: translateY({unit}px); }} }}",
        "@keyframes blink { 0%, 90%, 100% { opacity: 1; } 93% { opacity: 0.15; } }",
        f".hdr {{ fill: {tok['color.accent']}; }}",
    ]
    face = Face(iso, "left", 0, DEPTH, 0)
    rack = [box(iso, 0, 0, 0, FRONT, DEPTH, rack_h)]
    rails = [((0.25, 0.3), (0.25, rack_h - 0.25)), ((FRONT - 0.25, 0.3), (FRONT - 0.25, rack_h - 0.25))]
    rack.append(face.lines(rails))

    # obere Einheiten
    v_top, v_floor = rack_h - 0.3, v_at(groups[0]["top"])
    for k, (kind, h) in enumerate(UNITS):
        h = h or v_top - v_floor
        led = style(anim("fade", fast, t["units"] + k * step / 2, "steps(2)"))
        rack.append(unit_face(face, kind, v_top - h, h, led))
        if kind == "switch":
            mid = v_top - h / 2
            for port, token in PORT_BLINK.items():
                st = style(anim("fade", fast, t["units"] + k * step / 2, "steps(2)"),
                           anim("blink", secs(tok[token]), t["end"] + port * 0.4, "steps(1)", "infinite"))
                rack.append(face.dots([(port_u(port), mid + 0.35)], 1.4, "ok", st))
        v_top -= h

    # Bereichs-Einschübe
    calm = secs(tok["motion.ambient-max"])
    for i, g in enumerate(groups):
        v0, v1 = v_at(g["bottom"]), v_at(g["top"])
        rack.append(face.rect(0.5, v0 + 0.08, FRONT - 1, v1 - v0 - 0.16, "p"))
        vents, v = [], v0 + 0.6
        while v <= v1 - 0.5:
            vents.append(((0.9, v), (LED_U - 1.4, v)))
            v += 0.6
        rack.append(face.lines(vents))
        led_v = v_at(g["y"] - 8)
        on = t["list"][i]
        act_u = LED_U - 0.7
        rack.append(face.dots([(LED_U, led_v), (act_u, led_v)], 2.4, "off"))
        rack.append(face.dots([(LED_U, led_v)], 2.4, "ok", style(anim("fade", fast, on, "steps(2)"))))
        act = [anim("fade", fast, on + step / 2, "steps(2)")]
        if i in ACTIVITY_BLINK:
            act.append(anim("blink", calm, t["end"] + 2 + i, "steps(1)", "infinite"))
        rack.append(face.dots([(act_u, led_v)], 2.4, "acc", style(*act)))

    # Akzentkante oben an der Front
    (a, b), (c, d) = iso.point(0, DEPTH, rack_h), iso.point(FRONT, DEPTH, rack_h)
    rack.append(f'<path class="edge-glow" d="M{num(a)} {num(b)}L{num(c)} {num(d)}"/>')
    body = [f'<g style="{style(anim("rise", fast, t["rack"], ease))}">{"".join(rack)}</g>']

    # --- Name: Dot-Matrix, Aus-Punkte zuerst, An-Punkte Zeile für Zeile ---
    rows = [[] for _ in range(dotmatrix.ROWS)]
    off = []
    for col, row, lit in dotmatrix.cells(tok["profile.name"]):
        center = (PAD + (col + 0.5) * PITCH, PAD + (row + 0.5) * PITCH)
        (rows[row] if lit else off).append(center)
    body.append(f'<path class="off" style="{style(anim("fade", fast, 0, ease))}" d="{circles(off, DOT_R * 0.45)}"/>')
    for i, centers in enumerate(rows):
        st = style(anim("fade", fast / 2, t["name"] + i * t["row_step"], "steps(2)"))
        body.append(f'<path class="on" style="{st}" d="{circles(centers, DOT_R)}"/>')

    # --- Rolle und Kurztext ---
    for i, line in enumerate(role_lines):
        prefix = '<tspan class="hdr">&gt; </tspan>' if i == 0 else '<tspan xml:space="preserve">  </tspan>'
        st = style(anim("fade", fast, t["role"] + i * step, ease))
        body.append(f'<text class="txt" x="{PAD}" y="{role_y + i * LINE}" style="{st}">{prefix}{html.escape(line)}</text>')
    for i, line in enumerate(about_lines):
        st = style(anim("fade", fast, t["about"] + i * step, ease))
        body.append(f'<text class="mut" x="{PAD}" y="{about_y + i * LINE}" style="{st}">{html.escape(line)}</text>')

    # --- Trennlinie mit Status rechts ---
    status = "system online"
    status_x = text_right - len(status) * char_w
    st = style(anim("fade", fast, t["sys"], "steps(2)"))
    body.append(f'<path class="ln" d="M{PAD} {rule_y}H{num(status_x - 40)}"/>')
    body.append(f'<g style="{st}"><circle class="ok" cx="{num(status_x - 18)}" cy="{rule_y}" r="5"/>'
                f'<text class="mut" x="{num(status_x)}" y="{rule_y + 8}">{status}</text></g>')

    # --- Bereiche ---
    for i, g in enumerate(groups):
        on = t["list"][i]
        led = style(anim("fade", fast, on, "steps(2)"))
        txt = style(anim("fade", fast, on, ease))
        body.append(f'<circle class="off" cx="{led_x}" cy="{g["y"] - 8}" r="4"/>'
                    f'<circle class="ok" cx="{led_x}" cy="{g["y"] - 8}" r="4" style="{led}"/>')
        parts = [f'<text class="hdr" x="{group_x}" y="{g["y"]}">{html.escape(g["name"])}</text>']
        parts += [f'<text class="txt" x="{num(items_x)}" y="{g["y"] + j * LIST_LINE}">{html.escape(line)}</text>'
                  for j, line in enumerate(g["lines"])]
        body.append(f'<g style="{txt}">{"".join(parts)}</g>')

    label = (f"{tok['profile.name']} in leuchtender Punktschrift. {tok['profile.person']}, "
             f"{tok['profile.role']}. {tok['profile.about']} Bereiche: "
             + "; ".join(g["alt"] for g in groups)
             + ". Rechts ein isometrisches Server-Rack, dessen untere Einschübe mit grünen LEDs "
               "zu den Bereichen gehören; system online.")
    return document(tok, height, html.escape(label, quote=True), "\n".join(body), "\n".join(css))
