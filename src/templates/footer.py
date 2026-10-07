"""Terminal-Footer: kleines Terminalfenster mit Live-Werten.

Daten: tok.data (src/data/github.json), uptime aus tokens.json (profile.since).
Animation: Zeilen erscheinen nacheinander, sobald die Skyline-Welle fertig
ist, danach blinkt der Cursor. Ohne Daten stehen dort "n/a".
"""

from _scene import anim, boot_schedule, document, secs, style
from svglib import num

MARGIN = 20
BAR = 44           # Höhe der Titelleiste
LINE = 34          # Zeilenabstand
PAD_X = 28         # Innenabstand links


def render(tok):
    width = tok["canvas.width"]
    data = tok.data or {}
    char_w = tok["font.size.min"] * 0.6

    fetched = data.get("fetched_at", "")
    rows = [
        ("last_update", fetched[:10] or "n/a"),
        ("commits_this_week", str(data.get("commits_this_week", "n/a"))),
        ("public_repos", str(data.get("public_repos", "n/a"))),
        ("uptime", f"since {tok['profile.since']}"),
    ]
    key_w = (max(len(k) for k, _ in rows) + 2) * char_w

    height = MARGIN * 2 + BAR + 30 + LINE * (len(rows) + 2)
    win_w, win_h = width - 2 * MARGIN, height - 2 * MARGIN

    ease = tok["motion.ease"]
    fast, step = secs(tok["motion.fast"]), secs(tok["motion.stagger"])
    blink = secs(tok["motion.base"])
    t0 = boot_schedule(tok)["skyline_end"]

    css = [
        "@keyframes fade { from { opacity: 0; } }",
        "@keyframes cursor { 50% { opacity: 0; } }",
        f".win {{ fill: {tok['color.surface']}; stroke: {tok['color.grid']}; stroke-width: 1; }}",
        f".bar {{ fill: {tok['color.surface-2']}; }}",
        f".prompt {{ fill: {tok['color.accent']}; }}",
    ]
    x0, y0 = MARGIN, MARGIN
    body = [
        f'<rect class="win" x="{x0}" y="{y0}" width="{win_w}" height="{win_h}" rx="10"/>',
        f'<path class="bar" d="M{x0 + 1} {y0 + BAR}V{y0 + 10}a9 9 0 0 1 9-9H{x0 + win_w - 10}'
        f'a9 9 0 0 1 9 9V{y0 + BAR}Z"/>',
        f'<path class="ln" d="M{x0} {y0 + BAR}H{x0 + win_w}"/>',
    ]
    for i in range(3):
        body.append(f'<circle class="off" cx="{x0 + 24 + i * 22}" cy="{y0 + BAR / 2}" r="6"/>')
    login = tok["profile.login"].lower()
    body.append(f'<text class="mut" x="{width / 2}" y="{y0 + BAR / 2 + 8}" text-anchor="middle">'
                f'{login}@profile: ~</text>')

    tx = x0 + PAD_X
    y = y0 + BAR + 30 + 10
    lines = [f'<tspan class="prompt">$</tspan><tspan class="txt"> ./status.sh</tspan>']
    lines += [f'<tspan class="mut">{k}</tspan><tspan class="txt" x="{num(tx + key_w)}">{v}</tspan>'
              for k, v in rows]
    for i, content in enumerate(lines):
        st = style(anim("fade", fast / 2, t0 + i * step, "steps(1)"))
        body.append(f'<text x="{tx}" y="{num(y + i * LINE)}" style="{st}">{content}</text>')

    # letzte Zeile: Prompt mit blinkendem Cursor
    last_y = y + len(lines) * LINE
    t_cursor = t0 + len(lines) * step
    body.append(f'<text x="{tx}" y="{num(last_y)}" style="{style(anim("fade", fast / 2, t_cursor, "steps(1)"))}">'
                f'<tspan class="prompt">$</tspan></text>')
    cur = style(anim("fade", fast / 2, t_cursor, "steps(1)"),
                anim("cursor", blink, t_cursor + fast, "steps(1)", "infinite"))
    body.append(f'<rect class="acc" x="{num(tx + 2 * char_w)}" y="{num(last_y - 20)}" '
                f'width="{num(char_w)}" height="24" style="{cur}"/>')

    values = ", ".join(f"{k} {v}" for k, v in rows)
    label = f"Terminalfenster mit dem Profilstatus: {values}."
    return document(tok, height, label, "\n".join(body), "\n".join(css))
