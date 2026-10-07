"""Gemeinsame Bausteine für isometrische Szenen (Hero, Stack, ...).

Alle Farben kommen über CSS-Klassen aus den Tokens (base_css), die
Geometrie über svglib.Iso. Koordinaten sind Rastereinheiten.
"""

import dotmatrix
from svglib import circles, num


def base_css(tok):
    """CSS-Klassen für alle Szenen-Bausteine eines Themes."""
    return tok.fill("""
text { font-family: {{font.family}}; font-size: {{font.size.min}}px; }
.t { fill: {{shade.top}}; }
.l { fill: {{shade.left}}; }
.r { fill: {{shade.right}}; }
.t, .l, .r, .p, .s { stroke: {{shade.edge}}; stroke-width: 1; stroke-linejoin: round; }
.p { fill: {{color.surface}}; }
.s { fill: {{shade.screen}}; }
.ln { fill: none; stroke: {{shade.edge}}; stroke-width: 1; stroke-linecap: round; }
.on { fill: {{color.accent}}; }
.off { fill: {{color.grid}}; }
.ok { fill: {{color.ok}}; }
.warn { fill: {{color.warn}}; }
.acc { fill: {{color.accent}}; }
.glow { fill: {{color.accent-glow}}; }
.edge-glow { fill: none; stroke: {{color.accent}}; stroke-width: 2; stroke-linecap: round; }
.link { fill: none; stroke: {{color.accent}}; stroke-opacity: 0.45; stroke-width: 2; stroke-linejoin: round; }
.floor { fill: none; stroke: {{color.grid}}; stroke-width: 1; }
.txt { fill: {{color.text}}; }
.mut { fill: {{color.muted}}; }
""").strip()


def poly(points, cls):
    return f'<polygon class="{cls}" points="{points}"/>'


def box(iso, x, y, z, w, d, h, cls=""):
    """Schattierter Quader: links, rechts, oben."""
    f = iso.box(x, y, z, w, d, h)
    attr = f' class="{cls}"' if cls else ""
    return (
        f"<g{attr}>" + poly(f["left"], "l") + poly(f["right"], "r") + poly(f["top"], "t") + "</g>"
    )


class Face:
    """Zeichnen auf einer senkrechten Quaderfläche mit 2D-Koordinaten (u, v).

    u läuft waagerecht entlang der Fläche, v nach oben (Rastereinheiten).
    side="left": Fläche bei y=const, u entlang +x.
    side="right": Fläche bei x=const, u entlang +y.
    """

    def __init__(self, iso, side, x, y, z):
        self.iso, self.side, self.x, self.y, self.z = iso, side, x, y, z

    def point(self, u, v):
        if self.side == "left":
            return self.iso.point(self.x + u, self.y, self.z + v)
        return self.iso.point(self.x, self.y + u, self.z + v)

    def rect(self, u, v, w, h, cls):
        pts = [self.point(u, v), self.point(u + w, v), self.point(u + w, v + h), self.point(u, v + h)]
        return poly(" ".join(f"{num(a)},{num(b)}" for a, b in pts), cls)

    def lines(self, segments, cls="ln"):
        d = ""
        for (u1, v1), (u2, v2) in segments:
            (x1, y1), (x2, y2) = self.point(u1, v1), self.point(u2, v2)
            d += f"M{num(x1)} {num(y1)}L{num(x2)} {num(y2)}"
        return f'<path class="{cls}" d="{d}"/>'

    def dots(self, centers_uv, r, cls):
        return f'<path class="{cls}" d="{circles([self.point(u, v) for u, v in centers_uv], r)}"/>'


def matrix_uv(text, u0, v_top, pitch):
    """Dot-Matrix-Punkte auf einer Fläche: (an-Liste, aus-Liste) als (u, v)."""
    on, off = [], []
    for col, row, lit in dotmatrix.cells(text):
        (on if lit else off).append((u0 + (col + 0.5) * pitch, v_top - (row + 0.5) * pitch))
    return on, off


def matrix_flat(text, x0, y0, pitch, r, r_off=None):
    """Dot-Matrix flach auf dem Bildschirm (Pixel): <path> für an und aus.

    Aus-Punkte sind kleiner (r_off), damit die Buchstaben klar hervortreten.
    """
    r_off = r * 0.45 if r_off is None else r_off
    on, off = [], []
    for col, row, lit in dotmatrix.cells(text):
        (on if lit else off).append((x0 + (col + 0.5) * pitch, y0 + (row + 0.5) * pitch))
    return f'<path class="off" d="{circles(off, r_off)}"/><path class="on" d="{circles(on, r)}"/>'


def floor_grid(iso, x0, y0, x1, y1, step):
    d = ""
    for i in range(x0, x1 + 1, step):
        (a, b), (c, e) = iso.point(i, y0), iso.point(i, y1)
        d += f"M{num(a)} {num(b)}L{num(c)} {num(e)}"
    for j in range(y0, y1 + 1, step):
        (a, b), (c, e) = iso.point(x0, j), iso.point(x1, j)
        d += f"M{num(a)} {num(b)}L{num(c)} {num(e)}"
    return f'<path class="floor" d="{d}"/>'


def link(iso, *pts, z=0):
    """Verbindung entlang der Iso-Achsen durch die gegebenen (x, y)-Punkte."""
    d = "M" + "L".join(f"{num(sx)} {num(sy)}" for sx, sy in (iso.point(x, y, z) for x, y in pts))
    return f'<path class="link" d="{d}"/>'


def packet(iso, x, y, z=0, size=0.7):
    """Datenpaket: kleine leuchtende Raute auf dem Boden."""
    s = size / 2
    return poly(iso.points((x - s, y - s, z), (x + s, y - s, z), (x + s, y + s, z), (x - s, y + s, z)), "acc")


# --- Netzwerk-Knoten -------------------------------------------------------

def server(iso, x, y, w=2, d=2, h=4):
    """Kleiner Tower-Server mit Laufwerksschlitzen und LEDs auf der Front."""
    out = box(iso, x, y, 0, w, d, h)
    f = Face(iso, "left", x, y + d, 0)
    out += f.lines([((0.4, v), (w - 0.4, v)) for v in (h - 1.2, h - 1.8, h - 2.4)])
    out += f.dots([(0.6, h - 0.6)], 2.4, "ok")
    return out


def switch(iso, x, y, w=7, d=3, h=1.2):
    """Flacher Switch mit Port-Reihe und Status-LEDs."""
    out = box(iso, x, y, 0, w, d, h)
    f = Face(iso, "left", x, y + d, 0)
    ports = int((w - 1.6) / 0.8)
    out += "".join(f.rect(0.8 + i * 0.8, 0.3, 0.55, 0.5, "s") for i in range(ports))
    out += f.dots([(0.8 + i * 0.8 + 0.27, 0.95) for i in range(ports)], 1.4, "ok")
    return out


def router(iso, x, y, w=3, d=3, h=1.2):
    """Router: flacher Kasten mit zwei Antennen."""
    out = box(iso, x, y, 0, w, d, h)
    ant = []
    for ax, ay in ((x + 0.5, y + 0.5), (x + w - 0.5, y + 0.5)):
        (a, b), (c, e) = iso.point(ax, ay, h), iso.point(ax, ay, h + 2.2)
        ant.append(f"M{num(a)} {num(b)}L{num(c)} {num(e)}")
    out += f'<path class="ln" d="{"".join(ant)}"/>'
    f = Face(iso, "left", x, y + d, 0)
    out += f.dots([(0.6 + i * 0.6, 0.6) for i in range(3)], 1.6, "ok")
    return out


def document(tok, height, label, body, css=""):
    """Komplettes SVG mit Hintergrund, Basis-CSS und reduced-motion-Block."""
    from svglib import REDUCED_MOTION_CSS

    width = tok["canvas.width"]
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" '
        f'width="{width}" height="{height}" role="img" aria-label="{label}">\n'
        f"<style>\n{base_css(tok)}\n{css}\n{REDUCED_MOTION_CSS}\n</style>\n"
        f'<rect width="{width}" height="{height}" fill="{tok["color.bg"]}"/>\n'
        f"{body}\n</svg>"
    )
