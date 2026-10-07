"""Gemeinsame Bausteine für alle SVG-Templates.

Templates importieren von hier, damit Projektion, Zahlenformat und
reduced-motion-Muster in jeder Grafik identisch sind.
"""

import math
import re

# Animations-Muster für alle Templates:
# Die normalen CSS-Werte eines Elements beschreiben immer den ENDZUSTAND.
# Keyframes animieren nur vom Startzustand dorthin (bei Verzögerung mit
# animation-fill-mode: backwards). Schaltet dieser Block alle Animationen ab,
# bleibt automatisch der saubere Endzustand stehen.
REDUCED_MOTION_CSS = (
    "@media (prefers-reduced-motion: reduce) {"
    " *, *::before, *::after { animation: none !important; transition: none !important; }"
    " }"
)

# Token-Gruppen mit je einem Block pro Theme
THEMED = ("color", "shade")

_PLACEHOLDER = re.compile(r"\{\{\s*([\w.-]+)\s*\}\}")


class Tokens:
    """Token-Zugriff für genau ein Theme.

    tok["color.accent"]  -> Farbe des aktuellen Themes
    tok["motion.base"]   -> "1.2s"
    tok["shade.top"]     -> Farbe der Oberseite isometrischer Körper
    tok.theme            -> "dark" | "light"
    tok.raw              -> komplette tokens.json (z. B. für die Skill-Liste)
    """

    def __init__(self, raw, theme):
        self.raw = raw
        self.theme = theme
        flat = {}
        _flatten({k: v for k, v in raw.items() if k not in THEMED}, "", flat)
        _flatten(raw["color"][theme], "color.", flat)
        # shade.* verweist auf Palettennamen -> hier in Farben auflösen
        for face, color_name in raw.get("shade", {}).get(theme, {}).items():
            flat[f"shade.{face}"] = raw["color"][theme][color_name]
        flat["theme"] = theme
        self._flat = flat

    def __getitem__(self, key):
        try:
            return self._flat[key]
        except KeyError:
            raise KeyError(f"Unbekanntes Token: '{key}'") from None

    def colors(self):
        """Alle Farben des aktuellen Themes als {name: hex}."""
        return dict(self.raw["color"][self.theme])

    def fill(self, text, **values):
        """Ersetzt {{ token.pfad }} im Text. Unbekannte Tokens -> Fehler.

        values ergänzt template-eigene Werte (z. B. berechnete Geometrie):
        tok.fill("<path d='{{floor}}'/>", floor="M0 0L10 10")
        """
        def lookup(match):
            key = match.group(1)
            return str(values[key] if key in values else self[key])

        return _PLACEHOLDER.sub(lookup, text)


def _flatten(node, prefix, out):
    for key, value in node.items():
        if isinstance(value, dict):
            _flatten(value, f"{prefix}{key}.", out)
        elif not isinstance(value, list):
            out[prefix + key] = value


def num(value):
    """Kompaktes Zahlenformat: max. 2 Nachkommastellen, ohne Nullen am Ende."""
    text = f"{value:.2f}".rstrip("0").rstrip(".")
    return "0" if text == "-0" else text


class Iso:
    """Isometrische Projektion, in allen Grafiken identisch.

    Koordinaten (x, y, z) sind Rastereinheiten (grid.unit aus tokens.json).
    +x läuft auf dem Bildschirm nach rechts unten, +y nach links unten,
    +z nach oben. origin ist der Bildschirmpunkt von (0, 0, 0).
    """

    def __init__(self, tok, origin):
        self.unit = tok["grid.unit"]
        angle = math.radians(tok["iso.angle"])
        self._cx = math.cos(angle) * self.unit
        self._cy = math.sin(angle) * self.unit
        self.ox, self.oy = origin

    def point(self, x, y, z=0):
        return (
            self.ox + (x - y) * self._cx,
            self.oy + (x + y) * self._cy - z * self.unit,
        )

    def points(self, *pts):
        """Punktliste für das points-Attribut von <polygon>/<polyline>."""
        return " ".join(
            f"{num(sx)},{num(sy)}" for sx, sy in (self.point(*p) for p in pts)
        )

    def box(self, x, y, z, w, d, h):
        """Die drei sichtbaren Flächen eines Quaders als points-Strings."""
        x2, y2, z2 = x + w, y + d, z + h
        return {
            "top": self.points((x, y, z2), (x2, y, z2), (x2, y2, z2), (x, y2, z2)),
            "left": self.points((x, y2, z), (x2, y2, z), (x2, y2, z2), (x, y2, z2)),
            "right": self.points((x2, y, z), (x2, y2, z), (x2, y2, z2), (x2, y, z2)),
        }


def circles(centers, r):
    """Viele gleich große Kreise als EIN Pfad (spart Bytes gegenüber <circle>)."""
    d = num(2 * r)
    return "".join(
        f"M{num(x - r)} {num(y)}a{num(r)} {num(r)} 0 1 0 {d} 0a{num(r)} {num(r)} 0 1 0 -{d} 0"
        for x, y in centers
    )
