"""Terminal-Footer: die Karte selbst ist ein Terminalfenster mit Live-Werten.

Daten: tok.data (src/data/github.json), uptime aus tokens.json (profile.since).
Werte stehen in zwei Spalten, damit die Karte flach bleibt.
Animation: Zeilen erscheinen nacheinander, sobald die Skyline-Welle fertig
ist, danach blinkt der Cursor. Ohne Daten stehen dort "n/a".
"""

from _scene import anim, boot_schedule, document, secs, style
from svglib import num

BAR = 44           # Höhe der Titelleiste
LINE = 36          # Zeilenabstand
PAD_X = 32         # Innenabstand links
COL2_X = 540       # Beginn der zweiten Spalte


def render(tok):
    width = tok["canvas.width"]
    radius = tok["canvas.radius"]
    data = tok.data or {}
    char_w = tok["font.size.min"] * 0.6

    fetched = data.get("fetched_at", "")
    cols = [
        [("last_update", fetched[:10] or "n/a"),
         ("commits_this_week", str(data.get("commits_this_week", "n/a")))],
        [("public_repos", str(data.get("public_repos", "n/a"))),
         ("uptime", f"since {tok['profile.since']}")],
    ]
    height = BAR + 26 + LINE * 4 + 14

    fast, step = secs(tok["motion.fast"]), secs(tok["motion.stagger"])
    blink = secs(tok["motion.base"])
    t0 = boot_schedule(tok)["skyline_end"]

    css = [
        "@keyframes fade { from { opacity: 0; } }",
        "@keyframes cursor { 50% { opacity: 0; } }",
        f".bar {{ fill: {tok['color.surface-2']}; }}",
        f".prompt {{ fill: {tok['color.accent']}; }}",
    ]
    # Titelleiste in den oberen, runden Kartenecken
    r = radius - 1
    body = [
        f'<path class="bar" d="M2 {BAR}V{r + 1}a{r} {r} 0 0 1 {r} -{r}H{width - r - 2}'
        f'a{r} {r} 0 0 1 {r} {r}V{BAR}Z"/>',
        f'<path class="ln" d="M1 {BAR}H{width - 1}"/>',
    ]
    for i in range(3):
        body.append(f'<circle class="off" cx="{24 + i * 22}" cy="{BAR / 2 + 1}" r="6"/>')
    body.append(f'<text class="mut" x="{width / 2}" y="{BAR / 2 + 9}" text-anchor="middle">'
                f'{tok["profile.login"].lower()}@profile: ~</text>')

    y0 = BAR + 26 + 10
    lines = [(0, f'<tspan class="prompt">$</tspan><tspan class="txt"> ./status.sh</tspan>', PAD_X)]
    for c, rows in enumerate(cols):
        x = PAD_X if c == 0 else COL2_X
        key_w = (max(len(k) for k, _ in rows) + 2) * char_w
        for r_i, (k, v) in enumerate(rows):
            lines.append((1 + r_i, f'<tspan class="mut">{k}</tspan>'
                                   f'<tspan class="txt" x="{num(x + key_w)}">{v}</tspan>', x))
    for i, (row, content, x) in enumerate(lines):
        st = style(anim("fade", fast / 2, t0 + i * step, "steps(1)"))
        body.append(f'<text x="{x}" y="{num(y0 + row * LINE)}" style="{st}">{content}</text>')

    # letzte Zeile: Prompt mit blinkendem Cursor
    last_y = y0 + 3 * LINE
    t_cursor = t0 + len(lines) * step
    body.append(f'<text x="{PAD_X}" y="{num(last_y)}" style="{style(anim("fade", fast / 2, t_cursor, "steps(1)"))}">'
                f'<tspan class="prompt">$</tspan></text>')
    cur = style(anim("fade", fast / 2, t_cursor, "steps(1)"),
                anim("cursor", blink, t_cursor + fast, "steps(1)", "infinite"))
    body.append(f'<rect class="acc" x="{num(PAD_X + 2 * char_w)}" y="{num(last_y - 20)}" '
                f'width="{num(char_w)}" height="24" style="{cur}"/>')

    values = ", ".join(f"{k} {v}" for rows in cols for k, v in rows)
    label = f"Terminalfenster mit dem Profilstatus: {values}."
    return document(tok, height, label, "\n".join(body), "\n".join(css))
