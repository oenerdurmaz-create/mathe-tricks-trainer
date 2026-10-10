#!/usr/bin/env python3
"""Layout-Pruefung fuer alle Tricks (Playwright/Chromium).
Fuer jeden Trick werden bis zu 30 Aufgaben (inkl. der laengsten) im schwierigsten Zustand
(Bild + Schritte + Fehlermeldung) auf dem kleinsten Bildschirm gerendert. Geprueft wird:
nichts ragt aus der Aufgabenkarte, die Rechnung passt in eine Zeile, die Trick-Leiste laeuft nicht ueber,
und das Bild wird hoechstens auf 60 % verkleinert.
Aufruf: python3 tools/check_layout.py [ausgabeordner] [sprachen]   Exit-Code 1 bei Fehlern."""
import sys, pathlib, json
from playwright.sync_api import sync_playwright

ROOT = pathlib.Path(__file__).resolve().parents[1]
HTML = (ROOT / 'MatheTricksTrainer' / 'MatheTricksTrainer.html').as_uri()
OUT = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else ROOT / 'build' / 'layout')
LANGS = sys.argv[2].split(',') if len(sys.argv) > 2 else ['de', 'fr', 'ar']
SIZES = [(375, 667), (402, 850)]
MIN_ZOOM = 0.6
OUT.mkdir(parents=True, exist_ok=True)

JS = r"""([id, n]) => {
  startChallenge(id); stopTimers(); ch.phase = 'running';
  const pool = ch.pools[id].slice();
  const len = m => trickTaskLine(m).length + trickPlan(m).steps.reduce((a, s) => a + s[1].length, 0) + trickPlan(m).steps.length * 8;
  pool.sort((a, b) => len(b) - len(a));
  const pickIdx = new Set([0, 1, 2]); for (let i = 0; i < n; i++) pickIdx.add(Math.floor(i * pool.length / n));
  const res = [];
  for (const i of pickIdx) { if (i >= pool.length) continue; const m = pool[i];
    ch.task = m; ch.revealed = true; ch.wrong = true; ch.feedback = 'wrong'; ch.input = String(trickAnswer(m)).slice(0, 1);
    renderChallenge();
    const card = $('taskCard'), eq = $('taskEq'), bar = $('trickBar'), vis = card.querySelector('.tk-visual');
    res.push({ i, task: trickTaskLine(m), over: card.scrollHeight - card.clientHeight, eqOver: eq.scrollWidth - eq.clientWidth,
      barOver: bar.scrollWidth - bar.clientWidth, zoom: vis ? Number(vis.style.zoom || 1) : 1, eqPx: parseFloat(eq.style.fontSize || 0),
      hid: !!(vis && vis.classList.contains('hidden')), scroll: card.classList.contains('scroll') });
  }
  return res; }"""

errors, worst, hidden = [], {}, {}
with sync_playwright() as pw:
    b = pw.chromium.launch()
    for lang in LANGS:
        for (w, h) in SIZES:
            ctx = b.new_context(viewport={'width': w, 'height': h}, device_scale_factor=1)
            p = ctx.new_page(); jserr = []
            p.on('pageerror', lambda e: jserr.append(str(e)))
            p.add_init_script(f"try{{localStorage.setItem('mathetrickstrainer_language','{lang}')}}catch(e){{}}")
            p.goto(HTML)
            ids = p.evaluate('AVAILABLE_TRICKS')
            for tid in ids:
                for r in p.evaluate(JS, [tid, 30]):
                    key = (lang, w, tid)
                    score = max(r['over'], 0) * 10 + (1 - r['zoom']) * 100
                    if key not in worst or score > worst[key][0]: worst[key] = (score, r)
                    tag = f'{lang} {w}x{h} {tid} "{r["task"]}"'
                    if r['over'] > 1: errors.append(f'{tag}: Karte laeuft {r["over"]}px ueber')
                    if r['eqOver'] > 1: errors.append(f'{tag}: Rechnung zu breit')
                    if r['barOver'] > 1: errors.append(f'{tag}: Trick-Leiste zu breit')
                    if r['zoom'] < MIN_ZOOM - 1e-6: errors.append(f'{tag}: Bild auf {r["zoom"]:.2f} verkleinert')
                    if r['scroll']: errors.append(f'{tag}: Karte muss scrollen')
                    if r['hid']:
                        hidden.setdefault((lang, w, tid), 0); hidden[(lang, w, tid)] += 1
                        if (w, h) != SIZES[0]: errors.append(f'{tag}: Bild ausgeblendet auf grossem Bildschirm')
            # Bildschirmfoto des schlimmsten Falls je Trick (nur kleinster Bildschirm)
            if (w, h) == SIZES[0]:
                for tid in ids:
                    r = worst[(lang, w, tid)][1]
                    p.evaluate("([id,i])=>{startChallenge(id);stopTimers();ch.phase='running';const pool=ch.pools[id].slice();"
                               "const len=m=>trickTaskLine(m).length+trickPlan(m).steps.reduce((a,s)=>a+s[1].length,0)+trickPlan(m).steps.length*8;"
                               "pool.sort((a,b)=>len(b)-len(a));const m=pool[i];ch.task=m;ch.revealed=true;ch.wrong=true;ch.feedback='wrong';ch.input='';renderChallenge()}", [tid, r['i']])
                    p.screenshot(path=str(OUT / f'{lang}_{tid}.png'))
            if jserr: errors.append(f'{lang} {w}: JS-Fehler {jserr[:2]}')
            ctx.close()
    b.close()

print('Bild ausgeblendet (nur kleiner Bildschirm):', ', '.join(f'{k[2]}({k[0]}): {n}x' for k, n in sorted(hidden.items())) or 'nie')
zooms = sorted(((v[1]['zoom'], k) for k, v in worst.items()))[:8]
print('Kleinste Bild-Zooms:', ', '.join(f'{k[2]}({k[0]},{k[1]}): {z:.2f}' for z, k in zooms))
if errors:
    from collections import Counter
    c = Counter(' '.join(e.split(' ')[:3]) + ' | ' + e.rsplit('": ', 1)[1] for e in errors)
    print(f'LAYOUT FAIL ({len(errors)}):'); print('\n'.join(f'{n:3d}x {k}' for k, n in sorted(c.items())))
    print('Beispiele:'); print('\n'.join(errors[:8])); sys.exit(1)
print(f'LAYOUT PASS – {len(LANGS)} Sprachen x {len(SIZES)} Groessen x {len(set(k[2] for k in worst))} Tricks')
