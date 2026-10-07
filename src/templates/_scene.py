"""Gemeinsame Bausteine für isometrische Szenen (Hero, Tools, Skyline, ...).

Alle Farben kommen über CSS-Klassen aus den Tokens (base_css), die
Geometrie über svglib.Iso. Koordinaten sind Rastereinheiten.
"""

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

    def dots(self, centers_uv, r, cls, style=""):
        st = f' style="{style}"' if style else ""
        return f'<path class="{cls}"{st} d="{circles([self.point(u, v) for u, v in centers_uv], r)}"/>'


def word_wrap(text, max_chars):
    """Text an Wortgrenzen auf Zeilen mit höchstens max_chars Zeichen verteilen."""
    lines, current = [], ""
    for word in text.split():
        candidate = f"{current} {word}" if current else word
        if current and len(candidate) > max_chars:
            lines.append(current)
            current = word
        else:
            current = candidate
    return lines + [current] if current else lines


def wrap_items(items, max_chars):
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
        *full, current = word_wrap(item, max_chars)
        lines += full
    return lines + [current] if current else lines


def document(tok, height, label, body, css="", width=None):
    """Komplettes SVG als Karte: abgerundeter Rahmen, Basis-CSS, reduced motion.

    Alle Grafiken teilen denselben Kartenrahmen, damit das Profil als
    Einheit wirkt. Außerhalb der runden Ecken ist das SVG transparent.
    """
    from svglib import REDUCED_MOTION_CSS

    width = width or tok["canvas.width"]
    radius = tok["canvas.radius"]
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" '
        f'width="{width}" height="{height}" role="img" aria-label="{label}">\n'
        f"<style>\n{base_css(tok)}\n{css}\n{REDUCED_MOTION_CSS}\n</style>\n"
        f'<rect x="1" y="1" width="{width - 2}" height="{height - 2}" rx="{radius}" '
        f'fill="{tok["color.bg"]}" stroke="{tok["color.grid"]}" stroke-width="1.5"/>\n'
        f"{body}\n</svg>"
    )


# --- Animation --------------------------------------------------------------

TOOLS = 9
SKYLINE_WEEKS = 52
SKYLINE_WAVE = 0.03  # Versatz je Skyline-Säule (s): die Welle läuft in ca. 1,5 s durch


def boot_schedule(tok):
    """Zeitplan der Boot-Sequenz in Sekunden.

    Liegt hier, damit alle Grafiken einen gemeinsamen Ablauf haben: erst
    die whoami-Karte (Rack, Name, Text, Bereiche), danach die übrigen
    Karten – nie mehrere gleichzeitig "hochfahren".
    """
    fast, base = secs(tok["motion.fast"]), secs(tok["motion.base"])
    step = secs(tok["motion.stagger"])
    groups = len(tok.raw["skills"])
    t = {"rack": fast / 2, "units": fast * 1.5, "name": fast * 1.5, "row_step": step * 0.4}
    t["role"] = t["name"] + 7 * t["row_step"] + fast / 2
    t["about"] = t["role"] + 2 * step
    t["list"] = [t["about"] + 2 * step + fast / 2 + i * step for i in range(groups)]
    t["sys"] = t["list"][-1] + step + fast / 2
    t["end"] = t["sys"] + fast
    # Darunter: Tools sind beim Laden oft noch sichtbar und folgen direkt.
    t["tools"] = t["end"]
    t["tools_end"] = t["tools"] + TOOLS * step + fast
    # Weiter unten (beim Laden meist außer Sicht): starten direkt nach der
    # whoami-Karte, damit beim Scrollen nichts mehr leer ist.
    t["projects"] = t["end"] + fast
    t["skyline"] = t["end"] + base
    t["skyline_end"] = t["skyline"] + SKYLINE_WEEKS * SKYLINE_WAVE + fast
    return t


def secs(value):
    """Token-Zeit wie "0.4s" -> 0.4"""
    return float(str(value).rstrip("s"))


def anim(name, duration, delay=0, ease="", extra="backwards"):
    """Ein Eintrag für die CSS-Eigenschaft animation (Zeiten in Sekunden)."""
    parts = [name, f"{num(duration)}s", ease, f"{num(delay)}s", extra]
    return " ".join(p for p in parts if p)


def style(*animations):
    return "animation: " + ", ".join(animations)
