#!/usr/bin/env python3
"""Release-Validator Mathe Tricks Trainer.
Jede Regel, die einmal wichtig war, steht hier als Pruefung. Aufruf: python3 tools/validate_release.py
Exit-Code 0 = PASS, 1 = FAIL."""
from pathlib import Path
import json, os, plistlib, re, shutil, subprocess, sys, tempfile

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / 'MatheTricksTrainer'
HTML = APP / 'MatheTricksTrainer.html'
PBX = ROOT / 'MatheTricksTrainer.xcodeproj' / 'project.pbxproj'
PRIV = APP / 'PrivacyInfo.xcprivacy'
SWIFT = [APP / x for x in ['MatheTricksTrainerApp.swift', 'GameContainerView.swift', 'LocalGameWebView.swift']]
BUILD = 1
MARKETING = '1.0'
BUNDLE = 'com.larajade.mathetrickstrainer'
LANGS = ['de', 'en', 'fr', 'es', 'it', 'tr', 'pt', 'nl', 'pl', 'ja', 'zh', 'ar']

errors, passed = [], 0
def check(cond, label):
    global passed
    if cond: passed += 1
    else: errors.append(label)

s = HTML.read_text(encoding='utf-8')
p = PBX.read_text(encoding='utf-8')
swift = '\n'.join(x.read_text(encoding='utf-8') for x in SWIFT if x.exists())
cm = (ROOT / 'codemagic.yaml').read_text(encoding='utf-8')
all_code = s + '\n' + swift

# ---------- Xcode-Projekt / Release-Einstellungen
check(all(x.exists() for x in SWIFT), 'Swift-Dateien fehlen')
check(p.count(f'CURRENT_PROJECT_VERSION = {BUILD};') == 2, f'Buildnummer muss {BUILD} sein (Debug + Release)')
check(p.count(f'MARKETING_VERSION = {MARKETING};') == 2, f'Marketing-Version muss {MARKETING} sein')
check(p.count(f'PRODUCT_BUNDLE_IDENTIFIER = "{BUNDLE}";') == 2, 'Bundle-ID stimmt nicht')
check(p.count('TARGETED_DEVICE_FAMILY = 1;') == 2, 'Nur iPhone (TARGETED_DEVICE_FAMILY = 1)')
check(p.count('INFOPLIST_KEY_UISupportedInterfaceOrientations = UIInterfaceOrientationPortrait;') == 2, 'Nur Hochformat')
check(p.count('INFOPLIST_KEY_ITSAppUsesNonExemptEncryption = NO;') == 2, 'Export-Compliance-Flag muss NO sein')
check(p.count('INFOPLIST_KEY_CFBundleDisplayName = "Mathe Tricks";') == 2, 'Anzeigename "Mathe Tricks" fehlt')
check('rechenpyramide' not in p.lower(), 'Xcode-Projekt enthaelt noch Rechenpyramide-Reste')
check((ROOT / f'DEPLOY_BUILD{BUILD}.md').exists(), f'DEPLOY_BUILD{BUILD}.md fehlt')

# ---------- Codemagic
check(f'bundle_identifier: {BUNDLE}' in cm, 'codemagic.yaml: Bundle-ID')
check('XCODE_PROJECT: "MatheTricksTrainer.xcodeproj"' in cm and 'XCODE_SCHEME: "MatheTricksTrainer"' in cm, 'codemagic.yaml: Projekt/Scheme')
check('pattern: main' in cm and 'submit_to_testflight: true' in cm, 'codemagic.yaml: Push auf main -> TestFlight')
check('python3 tools/validate_release.py' in cm, 'codemagic.yaml: Validator laeuft nicht im Build')

# ---------- Icon, Datenschutz, Sprachen der Huelle
icon = APP / 'Assets.xcassets' / 'AppIcon.appiconset' / 'AppIcon.png'
check(icon.exists(), 'App-Icon fehlt')
if icon.exists():
    try:
        from PIL import Image
        im = Image.open(icon)
        check(im.size == (1024, 1024), 'App-Icon muss 1024x1024 sein')
        check(im.mode == 'RGB', 'App-Icon darf keinen Alphakanal haben')
    except ImportError:
        b = icon.read_bytes()
        check(b[16:24] == (1024).to_bytes(4, 'big') * 2, 'App-Icon muss 1024x1024 sein')
        check(b[25] == 2, 'App-Icon darf keinen Alphakanal haben (Farbtyp RGB)')
with open(PRIV, 'rb') as f:
    d = plistlib.load(f)
check(d.get('NSPrivacyTracking') is False, 'Privacy Manifest: Tracking muss false sein')
check(d.get('NSPrivacyCollectedDataTypes') == [] and d.get('NSPrivacyTrackingDomains') == [], 'Privacy Manifest: keine Daten, keine Domains')
for lp in ['de', 'en', 'fr', 'es', 'it', 'tr', 'pt', 'nl', 'pl', 'ja', 'zh-Hans', 'ar']:
    f = APP / f'{lp}.lproj' / 'InfoPlist.strings'
    check(f.exists() and 'CFBundleDisplayName' in f.read_text(encoding='utf-8'), f'InfoPlist.strings fehlt: {lp}')

# ---------- Swift-Huelle: nur lokale Datei, Pause im Hintergrund
check('decisionHandler(.cancel)' in swift and 'url.isFileURL' in swift, 'WebView muss externe Navigation blockieren')
check('willResignActiveNotification' in swift and 'didEnterBackgroundNotification' in swift and 'window.appPause' in swift, 'Swift muss das Spiel im Hintergrund pausieren')
check('LocalGameWebView(resourceName: "MatheTricksTrainer", resourceExtension: "html")' in swift, 'Swift laedt nicht MatheTricksTrainer.html')

# ---------- App-Store-Regeln (4.3, 5.6, Kinder-Kategorie)
for term in ['fetch(', 'XMLHttpRequest', 'WebSocket', 'http://', 'https://', 'eval(', 'new Function', 'sendBeacon', 'TestFlight', 'reviewer', '__debug']:
    check(term.lower() not in all_code.lower(), f'Verbotener Netz-/Debug-/Review-Begriff: {term}')
for term in ['🔒', 'unlock', 'locked:', 'purchase', 'coins', 'joker', 'lives', 'hearts']:
    check(term.lower() not in s.lower(), f'Sperren/Waehrung/Joker/Leben duerfen nicht vorkommen: {term}')
check(re.search(r'(?i)pyramid|irâmid|iramid|irámid|iramit|ピラミッド|金字塔|هرم|Rechenpyramide|Flinki|Pandi|sprite_', s) is None, 'Keine Begriffe/Figuren der Rechenpyramide (Regel 4.3)')
check('data:image' not in s, 'Keine Base64-Bilder im HTML')
check('<input' not in s and '<textarea' not in s, 'Keine iOS-Tastatur: nur eigenes Tastenfeld')
check('user-scalable=no' in s and 'viewport-fit=cover' in s, 'Viewport: kein Zoom, Safe Area')
check('<a ' not in s and 'window.open' not in s, 'Keine externen Links (sonst Elternhuerde noetig)')

# ---------- Spielregeln (Kickoff Abschnitt 4)
check("const TIME_PER_TASK={1:15,2:15,3:20,4:20};" in s, 'Zeit je Aufgabe: Klasse 1-2 15 s, Klasse 3-4 20 s')
check("const SHOW_HELP_UNTIL=3;" in s and 'ch.revealed=ch.score<SHOW_HELP_UNTIL' in s, 'Bild+Schritte bei den ersten 3 Aufgaben, danach auf Knopfdruck')
check('ALERT_SECONDS=3;' in s and "bar.classList.toggle('alert'" in s, 'Zeitbalken wird ab 3 Sekunden rot')
check('ch.remaining=ch.total' in s and 'total:TIME_PER_TASK[g]' in s, 'Zeitbalken springt bei jeder Aufgabe auf voll und wird nie kuerzer')
check('ch.score++' in s and 'ch.score--' not in s and 'ch.score-=' not in s, 'Score: +1, nie Abzug')
check("ch.wrong=true" in s and "const show=ch.revealed||ch.wrong" in s, 'Nach falscher Antwort erscheinen Bild und Schritte')
check("if(ch.remaining<=0){ch.remaining=0;renderTime();endChallenge(false)" in s, 'Balken leer -> Challenge vorbei')
check('data.best[key]=ch.score' in s and 'const key=bestKey(ch.mode),prev=bestOf(ch.mode),record=ch.score>prev;' in s, 'Best Score nur bei hoeherem Score ueberschrieben')
check("const STORAGE='mathetrickstrainer_v1'" in s, 'Speicherschluessel')
check(s.count('localStorage') == 2, 'localStorage nur ueber safeGet/safeSet (try/catch)')
check('window.appPause=pauseChallenge' in s and "addEventListener('visibilitychange'" in s, 'Timer pausiert im Hintergrund')
check("function resumeChallenge(){if(!ch||ch.phase!=='paused')return;$('pauseOverlay').classList.remove('open');startCountdown()}" in s, 'Nach Pause: 3-2-1, dann weiter')
check("$('keypad').classList.add('locked')" in s, 'Tastenfeld gesperrt waehrend 3-2-1')

# ---------- Ein Bildschirm: Pflicht-Elemente
for el in ['id="scoreTile"', 'id="bestTile"', 'id="timeBar"', 'id="timeText"', 'id="trickBar"', 'id="taskEq"', 'id="taskHelp"', 'id="keypad"', 'data-key="back"', 'data-key="ok"', 'id="showTrickBtn"', 'id="resultOverlay"', 'id="pauseOverlay"', 'id="countdown"']:
    check(el in s, f'Pflicht-Element fehlt: {el}')
check(re.search(r'<div id="timeBar"[^>]*dir="ltr"', s) is not None and re.search(r'<span id="timeText"[^>]*dir="ltr"', s) is not None, 'Zeitbalken und Restzeit dir="ltr"')
check(re.search(r'<div id="keypad"[^>]*dir="ltr"', s) is not None and re.search(r'<div id="taskEq"[^>]*dir="ltr"', s) is not None, 'Tastenfeld und Aufgabe dir="ltr"')
check('class="tb-ex num" dir="ltr"' in s and 'class="tc-ex num" dir="ltr"' in s, 'Beispiele in Trick-Leiste und Karte dir="ltr"')

# ---------- Texte: 12 Sprachen vollstaendig
def catalog(name):
    m = re.search(r'const %s=\{\n(.*?)\n\};' % name, s, re.S)
    out = {}
    if not m: return out
    for ln in m.group(1).split(',\n'):
        lang, js = ln.strip().split(':', 1)
        out[lang] = json.loads(js)
    return out
ui, tk = catalog('UI_I18N'), catalog('TRICK_I18N')
check(list(ui) == LANGS, 'UI_I18N: 12 Sprachen in fester Reihenfolge')
check(list(tk) == LANGS, 'TRICK_I18N: 12 Sprachen in fester Reihenfolge')
for lang in LANGS:
    check(set(ui.get(lang, {})) == set(ui.get('de', {})), f'UI-Texte unvollstaendig: {lang}')
    check(set(tk.get(lang, {})) == set(tk.get('de', {})), f'Trick-Texte unvollstaendig: {lang}')
    check(all(str(v).strip() for v in ui.get(lang, {}).values()), f'Leerer UI-Text: {lang}')
check(len(ui.get('de', {})) == 41, 'UI-Texte: Schluesselanzahl (41) stimmt nicht')
ids = re.findall(r"\{id:'([a-z0-9]+)',icon:", s)
check(len(ids) == 43, f'43 Tricks im Katalog (gefunden {len(ids)})')
for i in ids:
    for pre in ['trickName_', 'trickAsk_']:
        check(all(pre + i in tk.get(l, {}) for l in LANGS), f'{pre}{i} fehlt in einer Sprache')
check('const AVAILABLE_TRICKS=TRICKS.map(x=>x.id);' in s, 'Alle 43 Tricks spielbar')
check(len(re.findall(r"profi:true", s)) == 2, 'Genau 2 Profi-Tricks')
used = set(re.findall(r'data-i18n(?:-aria)?="([A-Za-z0-9_]+)"', s)) | set(re.findall(r"\bt\('([A-Za-z0-9_]+)'\)", s))
known = set(ui.get('de', {})) | set(tk.get('de', {}))
missing = sorted(k for k in used if k not in known)
check(not missing, f'Unbekannte Text-Schluessel: {missing}')
check(re.search(r'(?i)\bhile', json.dumps(ui.get('tr', {}), ensure_ascii=False) + json.dumps(tk.get('tr', {}), ensure_ascii=False)) is None, 'Tuerkisch: nicht "hile", sondern "püf noktası"')
check(LANGS and "ar:{name:'العربية',flag:'🇸🇦',dir:'rtl'}" in s, 'Arabisch als RTL markiert')


# ---------- Alle Tricks, "Alle Tricks gemischt", Symbole, Platz
check("function mixIds(g){return AVAILABLE_TRICKS.filter(id=>trickGrade(id)===g&&!trickProfi(id))}" in s, 'Gemischt: alle Tricks der Klasse ohne Profi-Tricks')
check("function bestKey(mode){return String(mode).startsWith('all:')?mode:'trick:'+mode}" in s, 'Best Score je Trick und je "Alle Tricks" pro Klasse')
check("do{id=pick(ch.ids)}while(id===ch.lastId)" in s, 'Gemischt: nie zweimal derselbe Trick hintereinander')
check("const m=ch.task,id=m.id,pl=trickPlan(m)" in s, 'Trick-Leiste zeigt den Trick der aktuellen Aufgabe')
check('<span class="sym" aria-hidden="true">🎯</span><b id="scoreVal"' in s and '<span class="sym" aria-hidden="true">🏆</span><b id="bestVal"' in s, 'Kacheln: 🎯 Score und 🏆 Best als Symbole')
check('data-i18n-aria="score"' in s and 'data-i18n-aria="best"' in s, 'Kacheln: Wort bleibt fuer VoiceOver')
check('data-i18n="score"' not in s and 'data-i18n="best"' not in s, 'Kacheln: kein sichtbares Wort Score/Best mehr')
check('⭐' not in json.dumps(ui, ensure_ascii=False), 'Keine Sterne (Unterscheidung zur Rechenpyramide)')
check('function fitChallenge(){' in s and 'const MIN_VISUAL_ZOOM=0.6;' in s and "card.classList.add('scroll')" in s, 'Aufgabenkarte passt sich dem Platz an')
check('@media (max-height:720px)' in s, 'Kompaktes Layout fuer kleine iPhones')
check('data-i18n="helpMixTitle"' in s, 'Hilfe erklaert "Alle Tricks gemischt"')
check("data.grade=+b.dataset.grade;saveData()" in s, 'Gewaehlte Klasse wird gemerkt')

# ---------- JavaScript-Syntax und Logiktest (brauchen node)
node = shutil.which('node')
if node:
    m = re.search(r'<script>(.*?)</script>', s, re.S)
    with tempfile.NamedTemporaryFile('w', suffix='.js', delete=False, encoding='utf-8') as tf:
        tf.write(m.group(1)); tmp = tf.name
    r = subprocess.run([node, '--check', tmp], capture_output=True, text=True); os.unlink(tmp)
    check(r.returncode == 0, 'JavaScript-Syntaxfehler: ' + r.stderr[:300])
    r = subprocess.run([node, str(ROOT / 'tools' / 'logic_test.js')], capture_output=True, text=True)
    check(r.returncode == 0 and 'LOGIKTEST PASS' in r.stdout, 'Logiktest fehlgeschlagen:\n' + r.stdout[-800:])
else:
    print('Hinweis: node nicht gefunden – Syntax- und Logiktest uebersprungen')

# ---------- Doku fuer App Store Connect
check((ROOT / 'docs' / 'privacy.html').exists() and (ROOT / 'docs' / 'support.html').exists(), 'docs/privacy.html und docs/support.html fehlen')

if errors:
    print(f'FAIL – {len(errors)} Fehler, {passed} Pruefungen ok')
    for e in errors: print(' -', e)
    sys.exit(1)
print(f'PASS – {passed} Pruefungen')
