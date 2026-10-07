"""Phase-0-Testgrafik: isometrischer Quader in Akzentfarbe auf Bodenraster.

Dient nur dazu, Generator, Prüfung und Vorschau einmal komplett zu
durchlaufen. Wird entfernt, sobald echte Komponenten existieren.
"""

from svglib import REDUCED_MOTION_CSS, Iso, num

HEIGHT = 360

SVG = """
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {{canvas.width}} {{height}}" width="{{canvas.width}}" height="{{height}}" role="img" aria-label="Testgrafik: isometrischer Quader in Akzentfarbe auf einem Bodenraster">
<style>
text { font-family: {{font.family}}; font-size: {{font.size.min}}px; fill: {{color.muted}}; }
.floor { animation: fade {{motion.fast}} {{motion.ease}} backwards; }
.box { animation: rise {{motion.base}} {{motion.ease}} {{motion.fast}} backwards; }
.edge { animation: pulse {{motion.ambient}} {{motion.ease}} {{motion.slow}} infinite; }
.led { animation: blink {{motion.ambient-min}} steps(1) {{motion.slow}} infinite; }
@keyframes fade { from { opacity: 0; } }
@keyframes rise { from { opacity: 0; transform: translateY({{rise}}px); } }
@keyframes pulse { 50% { opacity: 0.35; } }
@keyframes blink { 92% { opacity: 0.2; } 96% { opacity: 1; } }
{{reduced_motion}}
</style>
<rect width="{{canvas.width}}" height="{{height}}" fill="{{color.bg}}"/>
<path class="floor" d="{{floor}}" fill="none" stroke="{{color.grid}}" stroke-width="1"/>
<g class="box">
<polygon points="{{box_left}}" fill="{{color.accent}}" fill-opacity="0.6"/>
<polygon points="{{box_right}}" fill="{{color.accent}}" fill-opacity="0.35"/>
<polygon points="{{box_top}}" fill="{{color.accent}}"/>
<polygon class="edge" points="{{box_top}}" fill="none" stroke="{{color.accent-glow}}" stroke-width="2"/>
<circle class="led" cx="{{led_x}}" cy="{{led_y}}" r="{{led_r}}" fill="{{color.ok}}"/>
</g>
<text x="{{text_x}}" y="{{text_y}}">phase-0 render test · {{theme}}</text>
</svg>
"""


def render(tok):
    unit = tok["grid.unit"]
    iso = Iso(tok, origin=(tok["canvas.width"] / 2, 200))

    floor = []
    for i in range(-8, 9, 2):
        for a, b in (((i, -8), (i, 8)), ((-8, i), (8, i))):
            (x1, y1), (x2, y2) = iso.point(*a), iso.point(*b)
            floor.append(f"M{num(x1)} {num(y1)}L{num(x2)} {num(y2)}")

    box = iso.box(-4, -4, 0, 8, 8, 4)
    led_x, led_y = iso.point(4, -2.5, 2)

    return tok.fill(
        SVG,
        height=HEIGHT,
        reduced_motion=REDUCED_MOTION_CSS,
        rise=2 * unit,
        floor="".join(floor),
        box_left=box["left"],
        box_right=box["right"],
        box_top=box["top"],
        led_x=num(led_x),
        led_y=num(led_y),
        led_r=num(unit / 3),
        text_x=2 * unit,
        text_y=4 * unit,
    )
