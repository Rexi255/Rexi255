# CLAUDE.md – GitHub-Profil-README

Dieses Repo ist das Profil-Repository von **<GITHUB_USERNAME>**. Die `README.md` wird als Startseite des GitHub-Profils angezeigt.
Ziel: Ein Profil, das beim ersten Blick hängen bleibt. Kein Widget-Sammelsurium, sondern eine durchgestaltete Szene aus eigenen, animierten SVGs.

Der vollständige Umsetzungsplan steht in `PLAN.md`. Arbeite Phase für Phase und hake dort ab, was erledigt ist.

---

## Über mich (Inhalt fürs Profil)

> Platzhalter in `<…>` vor dem Veröffentlichen ersetzen oder entfernen. Nichts davon erfinden oder ausschmücken.

- **Name:** Jan
- **Rolle:** Auszubildender Fachinformatiker für Systemintegration, 2. Lehrjahr
- **Schwerpunkte (nur allgemeine Bereiche):**
  - Netzwerk
  - IT-Sicherheit
  - Server-Administration
  - Authentifizierung & Verzeichnisdienste
  - Client-Deployment & Geräteverwaltung
  - IT-Support
  - Linux

**Wichtig:** Keine Produkt- oder Markennamen und keine konkreten Details aus meinem Arbeitsumfeld verwenden (kein Arbeitgeber, keine Kunden, keine eingesetzten Systeme). Weder in der README noch in Grafiken, Alt-Texten oder Commit-Messages. Nur die allgemeinen Bereiche oben.
- **Projekte zum Hervorheben:**
  - [LF7-Projekt_GAS](https://github.com/BBZ-AIFS51/LF7-Projekt_GAS) – Schul-Teamprojekt: kleine Alarmanlage auf Mikrocontroller-Basis mit PIN-Feld, RFID und Bewegungsmelder, 3D-gedrucktem Gehäuse und interaktivem 3D-Modell im Browser
  - `<z. B. Berichtspilot – portable Electron-App für Ausbildungsnachweise>`
  - `<weitere>`
- **Kontakt/Links:** keine. Keine Kontakt-, Social- oder Mail-Links ins Profil einbauen.

---

## Kommunikation mit mir

- Antworte auf **Deutsch**.
- Commit-Messages auf Englisch im Conventional-Commits-Stil (`feat:`, `fix:`, `chore:`, `docs:`).
- Kleine, nachvollziehbare Commits. Ein Commit pro abgeschlossenem Schritt.
- Bevor du etwas Größeres baust: kurz den Ansatz in 3–5 Sätzen nennen, dann umsetzen.

---

## Konzept: „Datacenter / Network Ops“

Das ganze Profil ist **eine Szene**: ein Rechenzentrum bzw. Netzwerk, das gerade hochfährt und lebt.
Dunkel, präzise, technisch. Eine Akzentfarbe, Monospace-Typo, isometrische Perspektive (30°).

Aufbau der README von oben nach unten:

1. **Hero** – isometrisches Server-Rack / Netzwerktopologie, Datenpakete fließen zwischen Knoten, Name erscheint per Boot-Sequenz.
2. **Stack-Rack** – Skills als Rack-Einschübe mit Status-LEDs, gruppiert nach Bereich.
3. **Kurzer Text-Block** – 2–4 Sätze über mich, echtes Markdown (lesbar, durchsuchbar).
4. **Featured Projects** – über GitHubs gepinnte Repos, plus optional kurze Liste.
5. **Live-Skyline** – Contribution-Daten als isometrische 3D-Skyline, täglich generiert.
6. **Terminal-Footer** – kleines Terminalfenster mit Live-Werten (z. B. Last update, Commits diese Woche, Uptime-Gag).

---

## Designsystem

**Single Source of Truth:** `src/design/tokens.json`. Alle Farben, Abstände und Timings kommen von dort. Keine hartcodierten Werte in Templates.

### Farben

| Token | Dark | Light | Verwendung |
|---|---|---|---|
| `bg` | `#0C0915` | `#FAF8FF` | Hintergrund |
| `surface` | `#150F24` | `#FFFFFF` | Rack-Körper, Fenster |
| `surface-2` | `#1E1633` | `#F0EAFB` | Seitenflächen (isometrisch) |
| `grid` | `#2B2145` | `#DDD2F2` | Raster, Linien |
| `accent` | `#A855F7` | `#7C3AED` | Die Hauptfarbe: Pakete, Highlights, Name |
| `accent-glow` | `#D8B4FE` | `#A78BFA` | Heller Kern / Glow der Akzentfarbe, nur für Leuchteffekte |
| `ok` | `#4ADE80` | `#15803D` | Status-LEDs „online“ |
| `warn` | `#FBBF24` | `#A16207` | Sparsam, max. 1–2 Stellen |
| `text` | `#EDE9FE` | `#1E1533` | Primärtext |
| `muted` | `#8B81A8` | `#6B6385` | Sekundärtext, Labels |

Regel: **Lila dominiert.** `accent-glow` nur als Leuchtkern von Akzent-Elementen. `ok`/`warn` sind kleine Signalpunkte, keine Flächen. Hintergründe und Flächen sind leicht violett getönt, nicht neutral grau.

### Typografie

- Ausschließlich Monospace-Systemschriften (Stack: `ui-monospace, SFMono-Regular, Menlo, Consolas, "Liberation Mono", monospace`).
- Keine Webfonts laden. Für den Namen im Hero darf der Text in Pfade umgewandelt werden, damit er überall identisch aussieht.
- Mindestgröße im SVG so wählen, dass Text bei 400 px Anzeigebreite noch lesbar ist.

### Geometrie

- Isometrisch, 30°-Projektion, durchgehend gleich in allen SVGs.
- Einheitliches Raster (Basiseinheit in `tokens.json`).
- Feste Breite im `viewBox`: **900 px** für alle Haupt-Grafiken, damit sie bündig untereinander stehen.

### Animation

- Timings als Tokens: `fast` 0,4 s · `base` 1,2 s · `slow` 4 s · `ambient` 8–12 s.
- **Gestaffelt**, nie alles gleichzeitig. Maximal 2–3 Dinge gleichzeitig in Bewegung im sichtbaren Bereich.
- Hero: Boot-Sequenz läuft einmal (ca. 3–4 s), danach nur ruhige Ambient-Loops (LED-Blinken, fließende Pakete).
- Easing weich (`ease-in-out` oder eigene cubic-bezier), keine harten Sprünge außer bewusst beim „Glitch“/Boot.
- Jedes SVG enthält einen `prefers-reduced-motion`-Block, der Animationen stoppt und den **Endzustand** statisch zeigt.

---

## Harte technische Regeln

Diese Regeln sind nicht verhandelbar, weil GitHub sonst Inhalte entfernt oder Bilder kaputt anzeigt:

1. **Kein JavaScript** – weder in der README noch in den SVGs.
2. **Keine externen Ressourcen** in SVGs: keine Fonts, Bilder, Stylesheets per URL. Alles inline.
3. **Kein `<foreignObject>`.** 3D-Wirkung ausschließlich über isometrische Zeichnung, Flächen-Schattierung und CSS-/SMIL-Animationen innerhalb des SVG.
4. **Keine Drittanbieter-Widgets** (readme-stats, Typing-SVG-Dienste o. Ä.). Alles wird in diesem Repo erzeugt.
5. **Jede Grafik in Dark und Light**, eingebunden per `<picture>` mit `prefers-color-scheme`. Fallback-`<img>` ist die Dark-Variante.
6. **Relative Pfade** zu `assets/` in der README.
7. **Größenbudget:** Hero ≤ 300 KB, alle anderen SVGs ≤ 150 KB. Gesamte Asset-Größe ≤ 1 MB.
8. **Alt-Texte** für jedes Bild, die beschreiben, was zu sehen ist.
9. **Keine Secrets** im Repo. Tokens nur als GitHub Actions Secrets.
10. Generierte Dateien in `assets/` **nie von Hand bearbeiten** – Template oder Token ändern und neu generieren.

---

## Repo-Struktur

```
.
├── README.md                 # Profilseite – nur Layout, Text und <picture>-Einbindungen
├── CLAUDE.md                 # diese Datei
├── PLAN.md                   # Umsetzungsplan mit Phasen und Checklisten
├── assets/                   # GENERIERT – fertige SVGs (*-dark.svg / *-light.svg)
├── src/
│   ├── design/tokens.json    # Farben, Abstände, Timings, Skill-Liste
│   ├── templates/            # SVG-Templates je Komponente
│   └── data/                 # zwischengespeicherte Live-Daten (JSON)
├── scripts/                  # Generator- und Fetch-Skripte
├── preview/                  # lokale Vorschauseite (alle SVGs, Dark + Light, Desktop + Mobilbreite)
└── .github/workflows/        # Action für tägliche Live-Daten
```

**Generator:** Python 3, nur Standardbibliothek (keine pip-Abhängigkeiten), damit die Action ohne Installationsschritt läuft.
Ein Befehl baut alles: statische Komponenten aus Templates + Tokens, dynamische zusätzlich aus `src/data/`.

---

## Arbeitsablauf bei jeder Änderung an einer Grafik

1. Template oder Token ändern.
2. Generator laufen lassen.
3. **Prüfen:**
   - SVG ist gültiges XML.
   - Dateigröße innerhalb des Budgets.
   - Keine verbotenen Elemente (`<script>`, `<foreignObject>`, externe `href`/`url()`).
4. **Visuell kontrollieren:** SVG in einem Headless-Browser rendern, Screenshots in Dark und Light, bei 900 px und 400 px Breite. Screenshot selbst anschauen und Auffälligkeiten melden. Falls kein Headless-Browser verfügbar ist, das sagen und mich bitten, `preview/` lokal zu öffnen.
5. Erst dann committen.

---

## Live-Daten (GitHub Action)

- Läuft täglich per Cron und manuell per `workflow_dispatch`.
- Holt Daten über die GitHub-API mit dem eingebauten `GITHUB_TOKEN`. Ein eigenes Token (fine-grained, read-only) nur, wenn private Contributions mitzählen sollen – dann als Secret.
- Workflow-Rechte minimal: nur `contents: write`.
- Committet nur, wenn sich die generierten Dateien tatsächlich geändert haben.
- Bei API-Fehlern: letzten Stand aus `src/data/` verwenden, Workflow nicht mit kaputten SVGs committen.

---

## Definition of Done (je Komponente)

- [ ] Dark- und Light-Variante vorhanden
- [ ] `prefers-reduced-motion` zeigt sauberen statischen Endzustand
- [ ] Innerhalb Größenbudget
- [ ] Keine verbotenen Elemente
- [ ] Lesbar bei 400 px Breite
- [ ] Screenshots geprüft
- [ ] In `README.md` eingebunden mit Alt-Text
- [ ] In `PLAN.md` abgehakt
