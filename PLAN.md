# PLAN.md – Umsetzungsplan GitHub-Profil

Reihenfolge ist bewusst gewählt: erst Fundament, dann der Eyecatcher, dann Inhalt, zuletzt die Automatisierung.
Jede Phase endet mit einem sichtbaren Ergebnis, das ich prüfe, bevor es weitergeht.

Unter jeder Phase steht ein **Prompt**, den ich in Claude Code einfügen kann.

---

## Phase 0 – Fundament

**Ziel:** Repo-Struktur, Designsystem und Vorschau stehen. Noch keine echte Grafik.

- [ ] Profil-Repo angelegt (Name = Username, public), lokal geklont
- [ ] `CLAUDE.md` und `PLAN.md` liegen im Repo, `<GITHUB_USERNAME>` ersetzt
- [ ] Ordnerstruktur laut `CLAUDE.md` angelegt
- [ ] `src/design/tokens.json` mit Farben, Timings, Raster und Skill-Liste
- [ ] Generator-Grundgerüst: ein Befehl, der alle Templates in `assets/` rendert
- [ ] Prüfskript: XML-Validität, Größenbudget, verbotene Elemente
- [ ] Vorschauseite in `preview/`: alle Assets in Dark und Light, bei 900 px und 400 px
- [ ] Headless-Screenshot-Prüfung funktioniert (oder dokumentiert, warum nicht)

**Ergebnis:** Ein Test-SVG (einfaches isometrisches Rechteck in Akzentfarbe) läuft durch Generator, Prüfung und Vorschau.

> **Prompt:** „Lies CLAUDE.md und PLAN.md. Setze Phase 0 um. Erkläre mir jeden Befehl Zeile für Zeile. Am Ende zeig mir einen Screenshot des Test-SVGs in Dark und Light.“

---

## Phase 1 – Design-Exploration Hero

**Ziel:** Richtung festlegen, bevor Zeit in Animation fließt.

- [ ] 3 statische Hero-Varianten (keine Animation), alle im Designsystem:
  - A: Isometrisches Server-Rack, Name auf einem Display-Einschub
  - B: Netzwerktopologie (Router → Switch → Server-Knoten), Name im Zentrum
  - C: Mischung – Rack links, Topologie rechts, Pakete fließen dazwischen
- [ ] Screenshots aller drei nebeneinander
- [ ] Ich entscheide mich für eine Variante (oder Kombination) und notiere sie hier: `Gewählt: ___`

> **Prompt:** „Phase 1: Erstelle drei statische Hero-Varianten A, B, C wie in PLAN.md beschrieben. Keine Animation. Zeig mir alle drei als Screenshots nebeneinander, Dark und Light.“

---

## Phase 2 – Hero animieren

**Ziel:** Der Eyecatcher. Hier steckt die meiste Arbeit.

- [ ] Boot-Sequenz (einmalig, ca. 3–4 s):
  1. Raster blendet ein
  2. Rack/Knoten bauen sich gestaffelt auf
  3. Status-LEDs gehen nacheinander auf `ok`
  4. Name erscheint Zeile für Zeile, kurz `System online`
- [ ] Ambient-Loop danach: Pakete fließen ruhig zwischen Knoten, einzelne LEDs blinken versetzt
- [ ] `prefers-reduced-motion`: statischer Endzustand
- [ ] Light-Variante
- [ ] Größe ≤ 300 KB, lesbar bei 400 px
- [ ] Mit echtem Browser geprüft: Chrome, Firefox, Safari (falls verfügbar), GitHub-Mobile-App

> **Prompt:** „Phase 2: Animiere die gewählte Hero-Variante nach PLAN.md. Erst die Boot-Sequenz, zeig mir Screenshots zu 3–4 Zeitpunkten. Dann den Ambient-Loop. Halte dich strikt an die Animationsregeln in CLAUDE.md.“

---

## Phase 3 – Stack-Rack

**Ziel:** Tech-Stack als Teil der Szene statt Icon-Reihe.

- [ ] Rack mit Einschüben, gruppiert: Netzwerk · Security · Server · Auth · Deployment · Privat
- [ ] Jeder Einschub: Label in Monospace, Status-LED, dezente Lüfter-/Port-Details
- [ ] Animation: LEDs gehen gestaffelt an, danach sehr ruhiges Ambient-Blinken
- [ ] Daten kommen aus `tokens.json` (Skill-Liste), neue Skills = nur JSON ändern
- [ ] Gleiche Breite und Perspektive wie Hero, damit beides optisch verschmilzt
- [ ] Dark/Light, reduced motion, Budget ≤ 150 KB

> **Prompt:** „Phase 3: Baue das Stack-Rack nach PLAN.md. Die Skills kommen aus tokens.json. Es muss direkt unter dem Hero wie eine Fortsetzung derselben Szene wirken. Zeig mir Hero und Stack untereinander als Screenshot.“

---

## Phase 4 – README-Gerüst

**Ziel:** Die eigentliche Seite zusammensetzen.

- [ ] Layout: Hero → Stack → Text → Projekte → (Platzhalter Skyline) → (Platzhalter Footer)
- [ ] Alle Grafiken per `<picture>` mit Dark/Light, zentriert, mit Alt-Text
- [ ] Text-Block: 2–4 Sätze über mich, echtes Markdown, kein Bild
- [ ] Featured Projects: kurze Liste mit Einzeiler pro Projekt
- [ ] Links/Kontakt dezent, im Stil der Seite
- [ ] Auf GitHub gepusht und echtes Profil in Dark **und** Light Mode angeschaut

> **Prompt:** „Phase 4: Setze die README.md nach PLAN.md zusammen. Text-Entwürfe für ‚Über mich‘ und die Projekte schlägst du mir vor, ich entscheide. Keine Inhalte erfinden.“

---

## Phase 5 – Live-Daten

**Ziel:** Das Profil lebt und aktualisiert sich selbst.

### 5a – Daten holen
- [ ] Fetch-Skript: Contribution-Kalender der letzten 52 Wochen, Commits diese Woche, Anzahl öffentlicher Repos
- [ ] Ergebnis als JSON in `src/data/`
- [ ] Fehlerfall: alter Stand bleibt erhalten

### 5b – Skyline
- [ ] Isometrische Skyline: eine Säule pro Woche, Höhe = Contributions
- [ ] Animation: Säulen wachsen einmal gestaffelt von links nach rechts, danach ruhig
- [ ] Höchste Woche dezent mit `accent` markiert
- [ ] Dark/Light, reduced motion, Budget

### 5c – Terminal-Footer
- [ ] Kleines Terminalfenster, Zeilen erscheinen nacheinander
- [ ] Inhalte z. B.: `last_update`, `commits_this_week`, `repos`, ein kleiner Gag wie `uptime: since 2025`
- [ ] Blinkender Cursor am Ende

### 5d – GitHub Action
- [ ] Workflow: täglich + manuell auslösbar
- [ ] Ablauf: Daten holen → generieren → prüfen → nur bei Änderung committen
- [ ] Minimale Rechte (`contents: write`)
- [ ] Einmal manuell ausgelöst und Ergebnis auf dem Profil geprüft

> **Prompt:** „Phase 5: Setze 5a bis 5d nacheinander um. Nach jedem Teilschritt kurz zeigen, was funktioniert. Erkläre mir den Workflow (YAML) Zeile für Zeile.“

---

## Phase 6 – Qualitätssicherung

- [ ] Alle Komponenten erfüllen die Definition of Done aus `CLAUDE.md`
- [ ] Gesamtgröße aller Assets ≤ 1 MB
- [ ] Getestet: Chrome, Firefox, Safari, GitHub-Mobile-App, Light und Dark Mode
- [ ] Mit reduzierter Bewegung (Systemeinstellung) angeschaut
- [ ] Ladezeit des Profils subjektiv okay, nichts „springt“
- [ ] Rechtschreibung in allen sichtbaren Texten geprüft
- [ ] Keine persönlichen Daten, die ich nicht freigegeben habe

> **Prompt:** „Phase 6: Führe die komplette QA-Checkliste aus PLAN.md durch und gib mir einen Bericht mit allem, was noch nicht passt.“

---

## Phase 7 – Launch & Feinschliff

- [ ] Beste Repos auf dem Profil pinnen
- [ ] Profilbild und Bio passend zum Look (Bio kurz, gleiche Tonalität)
- [ ] Social-Preview-Bild für das Profil-Repo (statischer Screenshot vom Hero)
- [ ] Vorher/Nachher-Screenshot für mich archivieren

---

## Wartung

- Neue Skills: nur `tokens.json` ändern, Generator laufen lassen.
- Monatlich kurz prüfen, ob die Action grün läuft (GitHub schickt bei Fehlern eine Mail).
- Hinweis: GitHub deaktiviert geplante Workflows in Repos ohne Aktivität nach 60 Tagen. Die täglichen Commits der Action halten das Repo aktiv, solange sich Daten ändern. Wenn die Action pausiert wurde, im Actions-Tab wieder aktivieren.

---

## Risiken und Gegenmaßnahmen

| Risiko | Gegenmaßnahme |
|---|---|
| Animation sieht in Safari/App anders aus | Nur CSS-Keyframes und einfache SMIL, kein `foreignObject`, früh auf allen Plattformen testen |
| Profil wirkt überladen | Max. 2–3 Bewegungen gleichzeitig, Boot nur einmal, danach Ruhe |
| Text auf dem Handy unlesbar | Lesbarkeitsprüfung bei 400 px in jeder Phase |
| Light Mode sieht kaputt aus | Jede Komponente von Anfang an in beiden Varianten |
| Action scheitert still | Fehlerbehandlung mit altem Datenstand, GitHub-Mail bei Fehlschlag |
| Dateien zu groß | Prüfskript bricht bei Budgetüberschreitung ab |
