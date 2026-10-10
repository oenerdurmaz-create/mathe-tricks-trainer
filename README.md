# Mathe Tricks Trainer

iOS-Lernspiel für Klasse 1–4: Rechentricks als Challenge gegen die Zeit – Trick, Aufgabe, Bild, Schritte, Score, Best Score und Zeitbalken auf **einem** Bildschirm.

- Bundle-ID: `com.larajade.mathetrickstrainer` · Version 1.0 · nur iPhone, Hochformat, iOS 17+
- 12 Sprachen: de, en, fr, es, it, tr, pt, nl, pl, ja, zh, ar (Arabisch = RTL)
- Keine Werbung, kein Tracking, kein Server, keine Konten. Spielstand in `localStorage` (`mathetrickstrainer_v1`).

## Aufbau
| Datei | Inhalt |
|---|---|
| `MatheTricksTrainer/MatheTricksTrainer.html` | **gesamte Spiellogik** (HTML/CSS/JS, eine Datei) |
| `MatheTricksTrainer/*.swift` | SwiftUI-Hülle + lokale WKWebView, pausiert das Spiel im Hintergrund |
| `MatheTricksTrainer/Assets.xcassets` | App-Icon 1024×1024, Akzentfarbe |
| `tools/validate_release.py` | Release-Validator (läuft auch in Codemagic) |
| `tools/logic_test.js` | Logiktest aller 43 Trick-Pools |
| `tools/check_layout.py` | prüft alle Tricks in 12 Sprachen auf Platz (Playwright) |
| `tools/render_screens.py` | Screenshots 402×850 und 375×667 (Playwright) |
| `tools/make_icon.py` | zeichnet das vorläufige App-Icon |
| `docs/privacy.html`, `docs/support.html` | Datenschutz- und Support-Seite für App Store Connect |
| `DEPLOY_BUILDxx.md` | was je Build geändert und geprüft wurde |
| `PROJEKT.md` | Projektregeln und Entscheidungen |

## Ablauf
1. Neue Features auf einem eigenen Branch.
2. `python3 tools/validate_release.py` → PASS, `python3 tools/render_screens.py` → Bilder ansehen.
3. Nach Freigabe auf `main` pushen → Codemagic `ios-testflight` → TestFlight.
