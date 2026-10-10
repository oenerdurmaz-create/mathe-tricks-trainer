#!/usr/bin/env python3
"""Rendert die wichtigsten Bildschirme (402x850 und 375x667) als PNG nach build/screens.
Aufruf: python3 tools/render_screens.py [ausgabeordner]"""
import sys, pathlib
from playwright.sync_api import sync_playwright

ROOT = pathlib.Path(__file__).resolve().parents[1]
HTML = (ROOT / 'MatheTricksTrainer' / 'MatheTricksTrainer.html').as_uri()
OUT = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else ROOT / 'build' / 'screens')
OUT.mkdir(parents=True, exist_ok=True)

def page_for(b, lang, w=402, h=850):
    ctx = b.new_context(viewport={'width': w, 'height': h}, device_scale_factor=2, locale=lang)
    p = ctx.new_page()
    errors = []
    p.on('pageerror', lambda e: errors.append(str(e)))
    p.add_init_script(f"try{{localStorage.setItem('mathetrickstrainer_language','{lang}')}}catch(e){{}}")
    p.goto(HTML)
    return ctx, p, errors

def run(b, lang, w, h, tag):
    ctx, p, errors = page_for(b, lang, w, h)
    p.screenshot(path=str(OUT / f'{tag}_{lang}_1_home.png'))
    p.click('#helpBtn'); p.screenshot(path=str(OUT / f'{tag}_{lang}_8_help.png')); p.click('[data-close="helpOverlay"]')
    p.click('#settingsBtn'); p.screenshot(path=str(OUT / f'{tag}_{lang}_9_settings.png')); p.click('[data-close="settingsOverlay"]')
    p.click('[data-trick="vz"]')
    p.wait_for_timeout(300)
    p.screenshot(path=str(OUT / f'{tag}_{lang}_2_countdown.png'))
    p.wait_for_timeout(2900)
    ans = p.evaluate('trickAnswer(ch.task)')
    [p.click('[data-key="%s"]' % d) for d in str(ans)]
    p.screenshot(path=str(OUT / f'{tag}_{lang}_3_input.png'))
    # 3 richtige, dann Aufgabe 4 ohne Hilfe
    for i in range(3):
        if i: 
            a = p.evaluate('trickAnswer(ch.task)'); [p.click('[data-key="%s"]' % d) for d in str(a)]
        p.click('[data-key="ok"]'); p.wait_for_timeout(800)
    p.screenshot(path=str(OUT / f'{tag}_{lang}_4_hidden.png'))
    wrong = (p.evaluate('trickAnswer(ch.task)') % 9) + 1
    p.click('[data-key="%d"]' % wrong); p.click('[data-key="ok"]'); p.wait_for_timeout(450)
    p.screenshot(path=str(OUT / f'{tag}_{lang}_5_wrong.png'))
    p.evaluate('ch.remaining=2.5')
    p.wait_for_timeout(600)
    p.screenshot(path=str(OUT / f'{tag}_{lang}_6_alert.png'))
    p.wait_for_timeout(2600)
    p.screenshot(path=str(OUT / f'{tag}_{lang}_7_result.png'))
    # Klasse 4 auf der Startseite und "Alle Tricks gemischt" (Klasse 2)
    p.click('[data-act="home"]'); p.click('[data-grade="4"]'); p.wait_for_timeout(150)
    p.screenshot(path=str(OUT / f'{tag}_{lang}_10_home4.png'))
    p.click('[data-grade="2"]'); p.click('[data-trick="all:2"]'); p.wait_for_timeout(3300)
    p.screenshot(path=str(OUT / f'{tag}_{lang}_11_mix.png'))
    a = p.evaluate('trickAnswer(ch.task)'); [p.click('[data-key="%s"]' % d) for d in str(a)]; p.click('[data-key="ok"]'); p.wait_for_timeout(800)
    p.screenshot(path=str(OUT / f'{tag}_{lang}_12_mix2.png'))
    ctx.close()
    return errors

with sync_playwright() as pw:
    b = pw.chromium.launch()
    all_err = {}
    for lang in (sys.argv[2].split(',') if len(sys.argv) > 2 else ['de', 'ar']):
        all_err[lang] = run(b, lang, 402, 850, 'L')
    all_err['se_de'] = run(b, 'de', 375, 667, 'S')
    b.close()
print('JS-Fehler:', {k: v for k, v in all_err.items() if v} or 'keine')
