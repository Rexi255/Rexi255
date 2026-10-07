# PLAN.md – Umsetzungsplan GitHub-Profil

Reihenfolge ist bewusst gewählt: erst Fundament, dann der Eyecatcher, dann Inhalt, zuletzt die Automatisierung.
Jede Phase endet mit einem sichtbaren Ergebnis, das ich prüfe, bevor es weitergeht.

Unter jeder Phase steht ein **Prompt**, den ich in Claude Code einfügen kann.

---

## Phase 0 – Fundament

**Ziel:** Repo-Struktur, Designsystem und Vorschau stehen. Noch keine echte Grafik.

- [x] Profil-Repo angelegt (Name = Username, public), lokal geklont *(public bestätigt; lokalen Klon auf deinem Rechner kann ich nicht prüfen)*
- [x] `CLAUDE.md` und `PLAN.md` liegen im Repo, `<GITHUB_USERNAME>` ersetzt
- [x] Ordnerstruktur laut `CLAUDE.md` angelegt
- [x] `src/design/tokens.json` mit Farben, Timings, Raster und Skill-Liste
- [x] Generator-Grundgerüst: ein Befehl, der alle Templates in `assets/` rendert
- [x] Prüfskript: XML-Validität, Größenbudget, verbotene Elemente
- [x] Vorschauseite in `preview/`: alle Assets in Dark und Light, bei 900 px und 400 px
- [x] Headless-Screenshot-Prüfung funktioniert (oder dokumentiert, warum nicht)

**Ergebnis:** Ein Test-SVG (einfaches isometrisches Rechteck in Akzentfarbe) läuft durch Generator, Prüfung und Vorschau. ✅ (`phase0-test`)

**Befehle:**
- `python3 scripts/build.py` – Templates → `assets/`, Vorschau neu erzeugen, Prüfung (Exit ≠ 0 bei Verstoß)
- `python3 scripts/check.py` – nur Prüfung
- `python3 scripts/screenshot.py [--at MS] [--reduced-motion] [--only NAME]` – Screenshots nach `preview/shots/` (Echtzeit per Playwright, falls installiert, sonst Headless-Shell mit virtueller Zeit)

**Hinweis Headless:** Screenshots laufen über `chrome-headless-shell` (klassischer Headless-Modus). Normales Chrome im neuen Headless-Modus schneidet ca. 88 px ab und lässt Animationen nicht vorlaufen. SMIL-Animationen sind gesperrt, weil `prefers-reduced-motion` sie nicht stoppen kann – nur CSS-Animationen.

> **Prompt:** „Lies CLAUDE.md und PLAN.md. Setze Phase 0 um. Erkläre mir jeden Befehl Zeile für Zeile. Am Ende zeig mir einen Screenshot des Test-SVGs in Dark und Light.“

---

## Phase 1 – Design-Exploration Hero

**Ziel:** Richtung festlegen, bevor Zeit in Animation fließt.

- [x] 3 statische Hero-Varianten (keine Animation), alle im Designsystem:
  - A: Isometrisches Server-Rack, Name auf einem Display-Einschub
  - B: Netzwerktopologie (Router → Switch → Server-Knoten), Name im Zentrum
  - C: Mischung – Rack links, Topologie rechts, Pakete fließen dazwischen
- [x] Screenshots aller drei nebeneinander
- [x] Ich entscheide mich für eine Variante (oder Kombination) und notiere sie hier: `Gewählt: B – Netzwerktopologie, Name als Dot-Matrix „Rexi255“ oben`

> **Prompt:** „Phase 1: Erstelle drei statische Hero-Varianten A, B, C wie in PLAN.md beschrieben. Keine Animation. Zeig mir alle drei als Screenshots nebeneinander, Dark und Light.“

---

## Phase 2 – Hero animieren

**Ziel:** Der Eyecatcher. Hier steckt die meiste Arbeit.

- [x] Boot-Sequenz (einmalig, ca. 3–4 s):
  1. Raster blendet ein
  2. Rack/Knoten bauen sich gestaffelt auf
  3. Status-LEDs gehen nacheinander auf `ok`
  4. Name erscheint Zeile für Zeile, kurz `System online`
- [x] Ambient-Loop danach: Pakete fließen ruhig zwischen Knoten, einzelne LEDs blinken versetzt
- [x] `prefers-reduced-motion`: statischer Endzustand
- [x] Light-Variante
- [x] Größe ≤ 300 KB, lesbar bei 400 px
- [ ] Mit echtem Browser geprüft: Chrome, Firefox, Safari (falls verfügbar), GitHub-Mobile-App
  - Chromium (Headless, Echtzeit) ✅ – Firefox, Safari und GitHub-App bitte selbst prüfen, in der Cloud-Umgebung nicht verfügbar

> **Prompt:** „Phase 2: Animiere die gewählte Hero-Variante nach PLAN.md. Erst die Boot-Sequenz, zeig mir Screenshots zu 3–4 Zeitpunkten. Dann den Ambient-Loop. Halte dich strikt an die Animationsregeln in CLAUDE.md.“

---

## Phase 3 – Stack-Rack

**Ziel:** Tech-Stack als Teil der Szene statt Icon-Reihe.

- [x] Rack mit Einschüben, gruppiert: Netzwerk · Security · Server · Auth · Deployment · Privat
- [x] Jeder Einschub: Label in Monospace, Status-LED, dezente Lüfter-/Port-Details
- [x] Animation: LEDs gehen gestaffelt an, danach sehr ruhiges Ambient-Blinken
- [x] Daten kommen aus `tokens.json` (Skill-Liste), neue Skills = nur JSON ändern
- [x] Gleiche Breite und Perspektive wie Hero, damit beides optisch verschmilzt
- [x] Dark/Light, reduced motion, Budget ≤ 150 KB

> **Prompt:** „Phase 3: Baue das Stack-Rack nach PLAN.md. Die Skills kommen aus tokens.json. Es muss direkt unter dem Hero wie eine Fortsetzung derselben Szene wirken. Zeig mir Hero und Stack untereinander als Screenshot.“

---

## Phase 4 – README-Gerüst

**Ziel:** Die eigentliche Seite zusammensetzen.

- [x] Layout: Hero → Stack → Text → Projekte → (Platzhalter Skyline) → (Platzhalter Footer)
- [x] Alle Grafiken per `<picture>` mit Dark/Light, zentriert, mit Alt-Text
- [x] Text-Block: 2–4 Sätze über mich, echtes Markdown, kein Bild
- [x] Featured Projects: kurze Liste mit Einzeiler pro Projekt
- [x] ~~Links/Kontakt dezent, im Stil der Seite~~ – entfällt, laut CLAUDE.md keine Kontakt-Links
- [ ] Auf GitHub gepusht und echtes Profil in Dark **und** Light Mode angeschaut
  - Gepusht ✅, GitHub rendert beide `<picture>` mit Alt-Texten ✅ (per HTML geprüft). Optik nur lokal nachgestellt – echtes Profil bitte selbst in Dark und Light ansehen.

> **Prompt:** „Phase 4: Setze die README.md nach PLAN.md zusammen. Text-Entwürfe für ‚Über mich‘ und die Projekte schlägst du mir vor, ich entscheide. Keine Inhalte erfinden.“

---

## Phase 5 – Live-Daten

**Ziel:** Das Profil lebt und aktualisiert sich selbst.

### 5a – Daten holen
- [x] Fetch-Skript: Contribution-Kalender der letzten 52 Wochen, Commits diese Woche, Anzahl öffentlicher Repos
- [x] Ergebnis als JSON in `src/data/`
- [x] Fehlerfall: alter Stand bleibt erhalten

### 5b – Skyline
- [x] Isometrische Skyline: eine Säule pro Woche, Höhe = Contributions
- [x] Animation: Säulen wachsen einmal gestaffelt von links nach rechts, danach ruhig
- [x] Höchste Woche dezent mit `accent` markiert
- [x] Dark/Light, reduced motion, Budget

### 5c – Terminal-Footer
- [x] Kleines Terminalfenster, Zeilen erscheinen nacheinander
- [x] Inhalte z. B.: `last_update`, `commits_this_week`, `repos`, ein kleiner Gag wie `uptime: since 2025`
- [x] Blinkender Cursor am Ende

### 5d – GitHub Action
- [x] Workflow: täglich + manuell auslösbar
- [x] Ablauf: Daten holen → generieren → prüfen → nur bei Änderung committen
- [x] Minimale Rechte (`contents: write`)
- [x] Einmal manuell ausgelöst und Ergebnis auf dem Profil geprüft
  - Lauf #1 erfolgreich, Bot-Commit `chore: update live data` mit echten Daten (eingebautes Token). Optik auf dem echten Profil bitte selbst ansehen.

> **Prompt:** „Phase 5: Setze 5a bis 5d nacheinander um. Nach jedem Teilschritt kurz zeigen, was funktioniert. Erkläre mir den Workflow (YAML) Zeile für Zeile.“

---

## Phase 6 – Qualitätssicherung

- [x] Alle Komponenten erfüllen die Definition of Done aus `CLAUDE.md`
  - hero, stack, skyline, footer: Dark/Light, reduced motion, Budget, keine verbotenen Elemente, lesbar bei 400 px, Screenshots geprüft, in README mit Alt-Text ✅
- [x] Gesamtgröße aller Assets ≤ 1 MB
  - aktuell ca. 112 KB
- [ ] Getestet: Chrome, Firefox, Safari, GitHub-Mobile-App, Light und Dark Mode
  - Chromium Dark + Light ✅ (Cloud-Umgebung). **Offen für dich:** Firefox, Safari, GitHub-Mobile-App
- [x] Mit reduzierter Bewegung (Systemeinstellung) angeschaut
  - per Browser-Emulation geprüft; echte Systemeinstellung bitte einmal selbst testen
- [ ] Ladezeit des Profils subjektiv okay, nichts „springt“
  - **Offen für dich** (subjektiv). Technisch: 4 SVGs, zusammen ca. 112 KB, keine externen Ressourcen
- [x] Rechtschreibung in allen sichtbaren Texten geprüft
  - geprüft ✅ – bewusster Sprachmix: Terminal-Elemente englisch (`status.sh`, `contributions`), Inhalte deutsch
- [x] Keine persönlichen Daten, die ich nicht freigegeben habe
  - nur freigegebene Angaben (Name, Rolle, Bereiche, Projekte, since 2025); Dateien und Commit-Messages auf Produkt-/Markennamen durchsucht ✅

> **Prompt:** „Phase 6: Führe die komplette QA-Checkliste aus PLAN.md durch und gib mir einen Bericht mit allem, was noch nicht passt.“

---

## Phase 7 – Launch & Feinschliff

- [ ] Beste Repos auf dem Profil pinnen
  - **Offen für dich:** Profil → „Customize your pins“
- [ ] Profilbild und Bio passend zum Look (Bio kurz, gleiche Tonalität)
  - **Offen für dich**
- [ ] Social-Preview-Bild für das Profil-Repo (statischer Screenshot vom Hero)
  - Bild liegt in `preview/social-preview.png` (1280×640). **Offen für dich:** Repo → Settings → General → Social preview → Upload
- [ ] Vorher/Nachher-Screenshot für mich archivieren
  - **Offen für dich** (aus der Cloud-Umgebung lädt GitHub ohne Styles). Vorher-Stand: Commit `62c76d7`

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

---

## Redesign „kompakt & rund“ (nach Feedback)

Vorbild: Struktur des Profils eines Kollegen (einheitliche Karten, kompakte Höhen, klare Abschnitte) – Farben, Isometrie und Rechenzentrums-Thema bleiben eigen.

- [x] Einheitlicher Kartenrahmen für alle Grafiken (`canvas.radius`), Höhen ca. 230–335 px statt bis zu 640 px
- [x] Hero kompakt (300 px): Name + Rolle links, Topologie rechts
- [x] Bereiche kompakt: schmales Rack, eine Zeile je Gruppe
- [x] Neu: Tools-Sektion, Logos einfarbig lila auf isometrischen Sockeln, reihum leuchtendes Tool (Logos: Simple Icons, CC0-Pfaddaten; Sophos als Dot-Matrix-Kürzel)
- [x] Neu: Projektkarten (je 440 px, nebeneinander, LF7 verlinkt)
- [x] Skyline als isometrischer Häuserblock (13 × 4), Footer als Terminal-Karte in zwei Spalten
- [x] README mit `##`-Abschnitten im Terminal-Stil, aus `src/readme.md` generiert
- [ ] Alten Branch `claude/festive-faraday-sq3pz0` löschen – **offen für dich** (Proxy der Cloud-Umgebung blockiert Branch-Löschungen): Repo → Branches → Mülleimer

## whoami-Karte (nach Feedback)

- [x] Hero, whoami-Text und Bereiche zu **einer** Grafik zusammengefasst (`hero`, ca. 590 px): Text links, Rack rechts
- [x] Netzwerk-Topologie entfernt (Leitungen um den Switch wirkten wie ein Hakenkreuz), stattdessen ein Server-Rack ohne Leitungen
- [x] Einschub-LEDs liegen exakt auf Höhe der Listen-LEDs und gehen synchron an
- [x] Kurztext jetzt im Bild; vollständig im Alt-Text enthalten (dadurch nicht mehr als Markdown durchsuchbar)
- [ ] Social-Preview-Bild neu aufnehmen (Hero hat sich geändert) – **offen für dich**

