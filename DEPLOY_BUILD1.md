# Build 1 – Mathe Tricks Trainer: Challenge mit allen 43 Tricks

Marketing-Version 1.0, Buildnummer 1 (Codemagic setzt beim Bauen seine eigene, fortlaufende `BUILD_NUMBER`; bei der neuen App beginnt sie bei 1).
Ein Push nach `main` → ein Codemagic-Lauf → TestFlight.

## Regeln (je ein Satz)
- **Score:** jede richtige Antwort +1, eine falsche Antwort zieht nichts ab und zeigt Bild und Schritte; nur gezählt, keine Währung.
- **Best Score:** je Trick (`trick:<id>`) und je „Alle Tricks gemischt“ pro Klasse (`all:<klasse>`) lokal gespeichert, wird nur überschrieben, wenn der neue Score höher ist.
- **Zeit:** jede Aufgabe hat ihren eigenen Balken (Klasse 1–2: 15 s, Klasse 3–4: 20 s), er springt bei jeder neuen Aufgabe auf voll und wird nie kürzer; Balken leer → Challenge vorbei.
- **Farben des Balkens:** türkis, ab der Hälfte orange, ab 3 Sekunden rot und pulsierend; Restzeit als „0:08“ im Balken.
- **Erklärung:** Bild und Schritte bei den ersten 3 Aufgaben; ab der 4. richtigen Antwort (Score ≥ 3) nur über „💡 Trick zeigen“ oder automatisch nach einem Fehler. „Trick zeigen“ kostet keine Punkte, die Zeit läuft weiter.
- **Start:** kein eigener Startbildschirm – der Challenge-Bildschirm öffnet sofort, „3 – 2 – 1 – Los!“ im Zeitbalken, erst dann läuft die Zeit (Tastenfeld solange gesperrt).
- **Pause:** App im Hintergrund, Bildschirm aus oder Zurück-Taste → Pause-Karte („Weiter“ mit neuem 3-2-1 oder „Challenge beenden“); die Restzeit bleibt erhalten.
- **Ende:** Ergebnis-Karte mit Score, Best Score, „Neuer Rekord!“ und der richtigen Lösung der letzten Aufgabe; „Nochmal“ / „Alle Tricks“.
- Keine Herzen, keine Münzen, keine Joker, keine Figur, keine Sperren.
- **Alle 43 Tricks** sind sofort spielbar; Startseite mit Reitern Klasse 1–4, die gewählte Klasse wird gemerkt.
- **Profi-Tricks** (Abstand zur 100, Verliebte Einer beim Mal) stehen in Klasse 4 mit Kennzeichnung „Profi“ am Ende der Liste und sind nur einzeln spielbar.
- **🎲 Alle Tricks gemischt** (je Klasse, ohne Profi-Tricks): jede Aufgabe wählt zuerst zufällig einen Trick, nie zweimal derselbe hintereinander; die Trick-Leiste zeigt immer den Trick der aktuellen Aufgabe; eigener Best Score `all:<klasse>`.
- **Symbole:** Kacheln zeigen 🎯 (Score) und 🏆 (Best) statt der Wörter – auch auf Ergebnis-Karte und Trick-Karten; für VoiceOver bleibt das Wort als Beschriftung. Keine Sterne (Unterscheidung zur Rechenpyramide).
- **Falsche Antwort:** Meldung „Noch nicht. Schau dir die Schritte an!“ (Schritte gibt es bei jedem Trick, ein Bild nicht immer).
- **Platz:** Lange Rechnungen und Trick-Namen werden kleiner; ein zu großes Bild wird bis auf 60 % verkleinert; reicht das auf kleinen iPhones nicht, bleiben nur die Schritte stehen (betrifft im Fehlerfall nur Abstand zur 100, Muster der 8er-Reihe, Zahlen von 11 bis 19 auf 375×667). Kompaktes Layout unter 720 px Höhe.

## Inhalt
- Trick-Engine aus der Rechenpyramide (Build 28, Commit b0ad652) übernommen: 43 Tricks, Erkennung, Rechenweg, Bilder, Aufgaben-Pools, Trick-Texte in 12 Sprachen (187 Schlüssel je Sprache, ohne die pyramidenbezogenen Tipp- und Erklärtexte).
- Neu: Oberfläche, eigene Farbwelt (Nachtblau, Türkis, Koralle), 41 UI-Texte × 12 Sprachen, Einstellungen (Sprache, Töne), Hilfe, vorläufiges App-Icon (`tools/make_icon.py`).
- Anzeigename auf dem Homescreen: „Mathe Tricks“ (lokalisiert), App-Store-Name „Mathe Tricks Trainer“.

## Geprüft
- `python3 tools/validate_release.py` → PASS (inkl. `node --check` und Logiktest).
- `node tools/logic_test.js` → 43 Tricks, 2027 Aufgaben, 5305 Schritt-Gleichungen, 0 Fehler; jeder letzte Schritt endet mit „?“.
- `python3 tools/check_layout.py` → 12 Sprachen × 375×667 und 402×850 × 43 Tricks im engsten Zustand: nichts läuft über, keine Karte muss scrollen.
- `python3 tools/render_screens.py` → Start Klasse 1/4, 3-2-1, Eingabe, ausgeblendete Schritte, falsche Antwort, rote Restzeit, Gemischt-Challenge, Ergebnis-Karte, Hilfe, Einstellungen in 12 Sprachen angesehen.

## Nicht geprüft (braucht echtes Gerät)
- Pause beim Wechsel in den Hintergrund in der echten WKWebView, Töne, Safe-Area-Ränder mit Notch/Dynamic Island, CSS-`zoom` in WKWebView.
- Muttersprachliche Prüfung der neuen Texte (ja, zh, ar, tr).
