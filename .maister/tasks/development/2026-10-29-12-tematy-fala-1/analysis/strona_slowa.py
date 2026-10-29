"""Strona przeglądu słów oczywistych (#12, W10.3).

Czyta `szkic` z `slowa-oczywiste.json` i pisze jedną samodzielną stronę HTML
(iPhone, bez zewnętrznych plików). Operator skreśla słowa, dopisuje nowe
i kopiuje JSON:
  {"kind": "literaki-tematy-slowa-oczywiste", "schema_version": 1,
   "szkic_sha256": ..., "wynik": {<id>: [słowa]}}

`szkic_sha256` = sha256 kanonicznego JSON samego `szkic`:
  json.dumps(szkic, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode('utf-8')
Hash nie zależy od pola `wynik`, więc zapis wyniku (2.6) go nie zmienia.

Uruchomienie (z korzenia repozytorium):
  python3 <T>/analysis/strona_slowa.py <T>/analysis/slowa-oczywiste.json <T>/verification/slowa-oczywiste.html
"""
import argparse
import hashlib
import html
import json
from pathlib import Path

KIND = 'literaki-tematy-slowa-oczywiste'
TEMATY = [
    ('zwierzeta', 'Zwierzęta'), ('rosliny', 'Rośliny'), ('medycyna', 'Medycyna i ciało'),
    ('muzyka', 'Muzyka'), ('kuchnia', 'Kuchnia'), ('sport', 'Sport'),
    ('matematyka', 'Matematyka'), ('pogoda', 'Pogoda'), ('grzyby', 'Grzyby'),
]
# Granice z clarifications.md (operator, 2026-10-29).
GRANICE = [
    'Słowo pasujące do kilku tematów zostaje w każdym.',
    'Taniec należy do muzyki.',
    'Gry, szachy i karty należą do sportu.',
    'Napoje, też alkoholowe, należą do kuchni.',
    'Zwierzęta obejmują dinozaury, ale bez gwary łowieckiej.',
    'Grzybica należy do medycyny, nie do grzybów.',
]


def szkic_sha256(szkic):
    text = json.dumps(szkic, ensure_ascii=False, sort_keys=True, separators=(',', ':'))
    return hashlib.sha256(text.encode('utf-8')).hexdigest()


def page(szkic):
    ids = [i for i, _ in TEMATY]
    if sorted(szkic) != sorted(ids):
        raise SystemExit(f'Zły zestaw tematów w szkicu: {sorted(szkic)}')
    data = {'kind': KIND, 'schema_version': 1, 'szkic_sha256': szkic_sha256(szkic),
            'tematy': [{'id': i, 'nazwa': n, 'slowa': sorted(set(szkic[i]))} for i, n in TEMATY]}
    blob = json.dumps(data, ensure_ascii=False, sort_keys=True).replace('</', '<\\/')
    total = sum(len(t['slowa']) for t in data['tematy'])
    granice = ''.join(f'<li>{html.escape(g)}</li>' for g in GRANICE)
    return (TEMPLATE.replace('@@DATA@@', blob).replace('@@GRANICE@@', granice)
            .replace('@@TOTAL@@', str(total)))


TEMPLATE = r'''<!doctype html>
<html lang="pl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>Słowa oczywiste</title>
<style>
:root {
  --bg: #f7f6f2; --card: #ffffff; --text: #1d1d1b; --muted: #5d5d58; --line: #dddcd5;
  --accent: #1f5f8b; --nie: #b3261e; --add: #1e7a3c; --off: #eeede8; --on: #ffffff;
  color-scheme: light;
}
@media (prefers-color-scheme: dark) {
  :root:not([data-theme="light"]) {
    --bg: #141413; --card: #1f1f1d; --text: #ecebe6; --muted: #a8a7a0; --line: #3a3a36;
    --accent: #7fb6dd; --nie: #f2827a; --add: #5cc27c; --off: #2a2a27; --on: #141413;
    color-scheme: dark;
  }
}
:root[data-theme="dark"] {
  --bg: #141413; --card: #1f1f1d; --text: #ecebe6; --muted: #a8a7a0; --line: #3a3a36;
  --accent: #7fb6dd; --nie: #f2827a; --add: #5cc27c; --off: #2a2a27; --on: #141413;
  color-scheme: dark;
}
* { box-sizing: border-box; }
html { -webkit-text-size-adjust: 100%; }
body { margin: 0; background: var(--bg); color: var(--text); overflow-x: hidden;
  font: 17px/1.45 -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
main { max-width: 640px; margin: 0 auto; padding: 0 16px 48px; }
header { position: sticky; top: 0; z-index: 1; background: var(--bg); padding: 12px 16px 10px;
  border-bottom: 1px solid var(--line); }
header h1 { margin: 0; font-size: 20px; }
header p { margin: 2px 0 0; color: var(--muted); font-size: 15px; }
.intro { color: var(--muted); font-size: 15px; margin: 12px 0; }
.intro p { margin: 0 0 8px; }
.intro ul { margin: 4px 0 0; padding-left: 20px; }
details summary { cursor: pointer; color: var(--text); }
section.temat { background: var(--card); border: 1px solid var(--line); border-radius: 12px;
  padding: 14px; margin: 14px 0; }
section.temat h2 { font-size: 19px; margin: 0; }
.licz { color: var(--muted); font-size: 14px; margin: 2px 0 10px; }
.slowa { display: flex; flex-wrap: wrap; gap: 8px; }
button { font: inherit; border-radius: 10px; border: 2px solid var(--line); background: var(--card);
  color: var(--text); cursor: pointer; touch-action: manipulation; }
.slowo { flex: 1 0 auto; min-width: 84px; max-width: 100%; min-height: 48px; padding: 4px 12px;
  overflow-wrap: break-word; font-weight: 600; }
.slowo[aria-pressed="true"] { text-decoration: line-through; text-decoration-thickness: 2px;
  color: var(--nie); border-color: var(--nie); background: var(--off); font-weight: 400; }
.slowo.nowe { border-color: var(--add); color: var(--add); }
.dopisz { display: flex; gap: 8px; margin-top: 10px; }
.dopisz input { flex: 1; min-width: 0; font: inherit; min-height: 48px; padding: 0 10px; border-radius: 10px;
  border: 2px solid var(--line); background: var(--bg); color: var(--text); }
.dopisz button { min-height: 48px; padding: 0 14px; font-weight: 600; }
.uwaga { color: var(--nie); font-size: 14px; margin: 6px 0 0; min-height: 0; }
.out { margin-top: 28px; }
#copy { width: 100%; min-height: 52px; font-weight: 600; background: var(--accent);
  border-color: var(--accent); color: var(--on); }
#status { color: var(--muted); font-size: 15px; min-height: 1.4em; margin: 8px 0; }
textarea { width: 100%; min-height: 160px; font: 13px/1.4 ui-monospace, Menlo, monospace; color: var(--text);
  background: var(--card); border: 1px solid var(--line); border-radius: 10px; padding: 10px; }
</style>
</head>
<body>
<header><h1>Słowa oczywiste</h1><p id="progress"></p></header>
<main>
<div class="intro">
<p>To test pokrycia: liczymy, ile oczywistych słów zawiera lista tematu. Po budowie te listy się nie zmieniają.</p>
<p>Dotknij słowa, żeby je skreślić (drugi raz przywraca). Brakujące słowa wpisz w „dopisz”, oddzielając przecinkiem lub spacją. Na końcu naciśnij „Kopiuj JSON” i wklej wynik w rozmowę. Szkic zostaje w tej przeglądarce.</p>
<details><summary>Granice tematów</summary><ul>@@GRANICE@@</ul></details>
</div>
<div id="list"></div>
<section class="out">
<button id="copy" type="button">Kopiuj JSON</button>
<p id="status" role="status"></p>
<textarea id="json" readonly aria-label="JSON z wynikiem"></textarea>
</section>
</main>
<script id="data" type="application/json">@@DATA@@</script>
<script>
(function () {
  var data = JSON.parse(document.getElementById('data').textContent);
  var store = 'slowa-oczywiste-' + data.szkic_sha256.slice(0, 16);
  var SLOWO = /^[a-ząćęłńóśźż]+$/;
  var stan = {};
  data.tematy.forEach(function (t) { stan[t.id] = {skreslone: {}, dodane: []}; });
  try {
    var saved = JSON.parse(window.localStorage.getItem(store) || '{}');
    data.tematy.forEach(function (t) {
      var s = saved[t.id] || {};
      (s.skreslone || []).forEach(function (w) { if (t.slowa.indexOf(w) >= 0) { stan[t.id].skreslone[w] = true; } });
      (s.dodane || []).forEach(function (w) {
        if (typeof w === 'string' && SLOWO.test(w) && t.slowa.indexOf(w) < 0 && stan[t.id].dodane.indexOf(w) < 0) {
          stan[t.id].dodane.push(w);
        }
      });
    });
  } catch (e) { /* bez zapisu: szkic tylko w pamięci */ }

  function save() {
    var out = {};
    data.tematy.forEach(function (t) {
      out[t.id] = {skreslone: Object.keys(stan[t.id].skreslone), dodane: stan[t.id].dodane};
    });
    try { window.localStorage.setItem(store, JSON.stringify(out)); } catch (e) { /* szkic tylko w pamięci */ }
  }
  function wynik(t) {
    var s = stan[t.id];
    var w = t.slowa.filter(function (x) { return !s.skreslone[x]; }).concat(s.dodane);
    return w.filter(function (x, i) { return w.indexOf(x) === i; }).sort();
  }
  function result() {
    var out = {};
    data.tematy.forEach(function (t) { out[t.id] = wynik(t); });
    return JSON.stringify({kind: data.kind, schema_version: data.schema_version,
      szkic_sha256: data.szkic_sha256, wynik: out});
  }
  function el(tag, cls, text) {
    var node = document.createElement(tag);
    if (cls) { node.className = cls; }
    if (text !== undefined) { node.textContent = text; }
    return node;
  }

  var views = {};
  function refresh() {
    var all = 0, skr = 0, dop = 0;
    data.tematy.forEach(function (t) {
      var s = stan[t.id], n = Object.keys(s.skreslone).length;
      all += wynik(t).length; skr += n; dop += s.dodane.length;
      views[t.id].licz.textContent = 'Zostaje ' + wynik(t).length + ' · skreślone ' + n + ' · dopisane ' + s.dodane.length;
    });
    document.getElementById('progress').textContent = 'Razem ' + all + ' słów · skreślone ' + skr + ' · dopisane ' + dop;
    document.getElementById('json').value = result();
  }
  function renderNowe(t) {
    var v = views[t.id];
    v.nowe.forEach(function (b) { b.remove(); });
    v.nowe = stan[t.id].dodane.map(function (w) {
      var b = el('button', 'slowo nowe', '+ ' + w);
      b.type = 'button';
      b.title = 'Dotknij, żeby usunąć';
      b.setAttribute('aria-label', 'dopisane: ' + w + ', dotknij, żeby usunąć');
      b.addEventListener('click', function () {
        var d = stan[t.id].dodane;
        d.splice(d.indexOf(w), 1);
        renderNowe(t); save(); refresh();
      });
      v.grid.appendChild(b);
      return b;
    });
  }
  function dopisz(t) {
    var v = views[t.id];
    var raw = v.input.value.toLowerCase().split(/[\s,;]+/).filter(function (x) { return x; });
    var zle = [];
    raw.forEach(function (w) {
      if (!SLOWO.test(w)) { zle.push(w); return; }
      var s = stan[t.id];
      if (t.slowa.indexOf(w) >= 0) {
        if (s.skreslone[w]) {
          delete s.skreslone[w];
          v.btn[w].setAttribute('aria-pressed', 'false');
        }
      } else if (s.dodane.indexOf(w) < 0) { s.dodane.push(w); }
    });
    v.input.value = '';
    v.uwaga.textContent = zle.length ? 'Pominięte (tylko małe polskie litery): ' + zle.join(', ') : '';
    renderNowe(t); save(); refresh();
  }

  var list = document.getElementById('list');
  data.tematy.forEach(function (t) {
    var sec = el('section', 'temat');
    sec.id = 't-' + t.id;
    sec.appendChild(el('h2', '', t.nazwa));
    var licz = el('p', 'licz');
    sec.appendChild(licz);
    var grid = el('div', 'slowa');
    var btn = {};
    t.slowa.forEach(function (w) {
      var b = el('button', 'slowo', w);
      b.type = 'button';
      b.setAttribute('aria-pressed', stan[t.id].skreslone[w] ? 'true' : 'false');
      b.addEventListener('click', function () {
        var s = stan[t.id].skreslone;
        if (s[w]) { delete s[w]; } else { s[w] = true; }
        b.setAttribute('aria-pressed', s[w] ? 'true' : 'false');
        save(); refresh();
      });
      btn[w] = b;
      grid.appendChild(b);
    });
    sec.appendChild(grid);
    var form = el('form', 'dopisz');
    var input = el('input');
    input.type = 'text';
    input.placeholder = 'dopisz';
    input.setAttribute('aria-label', 'Dopisz do: ' + t.nazwa);
    input.autocapitalize = 'none';
    input.setAttribute('autocorrect', 'off');
    input.spellcheck = false;
    var add = el('button', '', 'Dodaj');
    add.type = 'submit';
    form.appendChild(input);
    form.appendChild(add);
    form.addEventListener('submit', function (e) { e.preventDefault(); dopisz(t); });
    sec.appendChild(form);
    var uwaga = el('p', 'uwaga');
    uwaga.setAttribute('role', 'status');
    sec.appendChild(uwaga);
    list.appendChild(sec);
    views[t.id] = {licz: licz, grid: grid, btn: btn, input: input, uwaga: uwaga, nowe: []};
    renderNowe(t);
  });

  document.getElementById('copy').addEventListener('click', function () {
    data.tematy.forEach(function (t) { if (views[t.id].input.value.trim()) { dopisz(t); } });
    var area = document.getElementById('json');
    var status = document.getElementById('status');
    var text = result();
    area.value = text;
    function fallback() {
      area.focus();
      area.select();
      area.setSelectionRange(0, text.length);
      var ok = false;
      try { ok = document.execCommand('copy'); } catch (e) { ok = false; }
      status.textContent = ok ? 'Skopiowano.' : 'Zaznacz tekst poniżej i skopiuj ręcznie.';
    }
    try {
      if (navigator.clipboard && window.isSecureContext) {
        navigator.clipboard.writeText(text).then(function () { status.textContent = 'Skopiowano.'; }, fallback);
      } else { fallback(); }
    } catch (e) { fallback(); }
  });
  refresh();
})();
</script>
</body>
</html>
'''


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('wejscie', type=Path)
    ap.add_argument('wyjscie', type=Path)
    a = ap.parse_args()
    szkic = json.loads(a.wejscie.read_text(encoding='utf-8'))['szkic']
    a.wyjscie.parent.mkdir(parents=True, exist_ok=True)
    a.wyjscie.write_text(page(szkic), encoding='utf-8')
    print(f'{a.wyjscie}: {sum(len(set(v)) for v in szkic.values())} słów, szkic_sha256 {szkic_sha256(szkic)}')


if __name__ == '__main__':
    main()
