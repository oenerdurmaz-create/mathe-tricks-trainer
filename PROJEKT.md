# Projektregeln Mathe Tricks Trainer

## Entscheidungen (10.10.2026)
| Thema | Entscheidung |
|---|---|
| Name | „Mathe Tricks Trainer“ (EN „Math Tricks Trainer“); Homescreen „Mathe Tricks“ |
| Bundle-ID / Repo | `com.larajade.mathetrickstrainer` / `oenerdurmaz-create/mathe-tricks-trainer` |
| Spielmodus | nur Challenge, keine Modi „Lernen“/„Training“ |
| Score | +1 je richtige Antwort, kein Abzug, Best Score je Trick und je „Alle Tricks gemischt“ pro Klasse, keine Währung |
| Zeit | Balken pro Aufgabe, Klasse 1–2 15 s, Klasse 3–4 20 s, wird nie kürzer |
| Erklärung | ab der 4. richtigen Antwort nur auf Knopfdruck, nach Fehler automatisch |
| Herzen, Münzen, Joker | weggelassen |
| Figur / Begleiter | keine – auch später nicht |
| Rechenpyramide | bleibt unverändert, kein Hinweis auf diese App; zwei getrennte Apps |
| Build 1 (erste TestFlight-Version) | alle 43 Tricks, „Alle Tricks gemischt“ je Klasse (ohne Profi-Tricks), Klassen-Reiter |
| Score/Best-Anzeige | Symbole 🎯 (Score) und 🏆 (Best) statt Wörter; keine Sterne |
| App-Icon | vorläufig eigenes Icon (Zeit-Ring + Blitz) |

## App-Store-Vorgaben
- Regel 4.3: keine Kopie der Rechenpyramide – eigenes Spielprinzip, eigenes Aussehen, keine Begriffe/Figuren der Rechenpyramide (Validator prüft).
- Kinder-Kategorie: keine Tracker, keine Werbung, kein Server, keine Konten, keine externen Links.
- Alle Tricks sofort spielbar, keine Schloss-Symbole, keine Server-Schalter.

## Arbeitsregeln
1. Validator `tools/validate_release.py` muss PASS melden; jede wichtige Regel wird dort eine Prüfung.
2. Logiktest: jede Aufgabe jedes Pools, jede Schritt-Gleichung mit eingesetzter Lösung rechnerisch korrekt (0 Fehler).
3. Sichtbare Änderungen rendern und ansehen (402×850 und 375×667, auch Arabisch); `tools/check_layout.py` muss PASS melden.
4. Bei Score/Zeit/Fortschritt vorher in einem Satz festlegen: abgezogen oder gezählt? einmalig oder wiederholbar?
5. Batch-Ersetzungen pro Sprache: Treffer vorher zählen, bei Abweichung abbrechen.
6. „Fertig“ heißt: Logik + UI + 12 Sprachen + Hilfe-Text + Prüfregel + Screenshot geprüft.
7. Je Build eine `DEPLOY_BUILDxx.md`; Buildnummer im Projekt und im Validator hochzählen.
8. Neue Features zuerst auf Branch; `main` erst nach Freigabe (jeder Push auf `main` startet TestFlight).
9. Türkisch: nicht „hile“, sondern „püf noktası“. Texte in ja/zh/ar/tr muttersprachlich prüfen lassen.
10. Zeitbalken pausiert im Hintergrund; Zahlen, Zeit und Rechnungen immer `dir="ltr"`.
