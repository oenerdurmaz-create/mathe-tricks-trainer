#!/usr/bin/env node
// Logiktest fuer alle Tricks: jede Aufgabe aus jedem Pool -> Aufgabe und jede Schritt-Gleichung
// mit eingesetzter Loesung muessen rechnerisch stimmen. Zusaetzlich: der letzte Schritt enthaelt "?".
// Aufruf: node tools/logic_test.js   (Exit-Code 1 bei Fehlern)
'use strict';
const fs = require('fs'), path = require('path'), vm = require('vm');
const html = fs.readFileSync(path.join(__dirname, '..', 'MatheTricksTrainer', 'MatheTricksTrainer.html'), 'utf8');
const start = html.indexOf('// ===== Trick-Engine');
const end = html.indexOf('// ---------- Spielregeln');
if (start < 0 || end < 0 || end < start) { console.error('Engine-Marker nicht gefunden'); process.exit(1); }
const ctx = { t: k => k };
vm.createContext(ctx);
vm.runInContext(html.slice(start, end) + '\n;this.API={TRICKS,TRICK_EXAMPLES,trickTaskPool,trickPlan,trickAnswer,trickTaskLine,trickMatches};', ctx);
const { TRICKS, TRICK_EXAMPLES, trickTaskPool, trickPlan, trickAnswer, trickTaskLine } = ctx.API;
const avail = html.includes('const AVAILABLE_TRICKS=TRICKS.map(x=>x.id);') ? TRICKS.map(x => x.id)
  : (html.match(/const AVAILABLE_TRICKS=\[([^\]]*)\]/) || [, ''])[1].split(',').map(s => s.trim().replace(/'/g, '')).filter(Boolean);

function evalSide(expr) {
  const e = expr.replace(/×/g, '*').replace(/−/g, '-').replace(/:/g, '/').replace(/\s+/g, '');
  if (!/^[0-9+\-*/().]+$/.test(e)) return NaN;
  return Function('"use strict";return (' + e + ')')();
}
function checkEq(line, ans) {
  const filled = line.replace('?', String(ans));
  if (filled.includes('≈') || !filled.includes('=')) return true; // Runden/Muster: keine Gleichung
  const sides = filled.split('=').map(evalSide);
  if (sides.some(Number.isNaN)) return false;
  return sides.every(v => Math.abs(v - sides[0]) < 1e-9);
}

let tasks = 0, steps = 0, errors = [], report = [];
for (const tr of TRICKS) {
  const pool = trickTaskPool(tr.id);
  if (!pool.length) { errors.push(tr.id + ': leerer Aufgaben-Pool'); continue; }
  let noSteps = 0, noQ = 0;
  for (const m of pool) {
    tasks++;
    const pl = trickPlan(m), ans = trickAnswer(m);
    if (!checkEq(trickTaskLine(m), ans)) errors.push(tr.id + ': Aufgabe falsch ' + trickTaskLine(m) + ' -> ' + ans);
    if (!pl.steps.length) { noSteps++; continue; }
    pl.steps.forEach(([lab, eq]) => { steps++; if (!checkEq(eq, ans)) errors.push(tr.id + ': Schritt falsch "' + eq + '" mit ' + ans + ' (' + trickTaskLine(m) + ')'); });
    if (!pl.steps[pl.steps.length - 1][1].includes('?')) noQ++;
  }
  const ex = Object.assign({ id: tr.id }, TRICK_EXAMPLES[tr.id] || {});
  if (!TRICK_EXAMPLES[tr.id] || !checkEq(trickTaskLine(ex), trickAnswer(ex))) errors.push(tr.id + ': Beispiel fehlt oder falsch');
  const live = avail.includes(tr.id);
  if (live && noSteps) errors.push(tr.id + ': ' + noSteps + ' Aufgaben ohne Schritte (Challenge braucht Schritte)');
  if (live && noQ) errors.push(tr.id + ': ' + noQ + ' Aufgaben, deren letzter Schritt kein ? hat');
  report.push(tr.id + ':' + pool.length + (noSteps ? ' ohneSchritte=' + noSteps : '') + (noQ ? ' ohne?=' + noQ : '') + (live ? ' [aktiv]' : ''));
}
console.log('Tricks:', TRICKS.length, '| aktiv:', avail.join(',') || '-', '| Aufgaben:', tasks, '| Schritt-Gleichungen:', steps);
console.log(report.join('  '));
if (errors.length) { console.log('FEHLER (' + errors.length + '):\n' + errors.slice(0, 40).join('\n')); process.exit(1); }
console.log('LOGIKTEST PASS (0 Fehler)');
