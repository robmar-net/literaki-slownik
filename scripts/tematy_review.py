#!/usr/bin/env python3
"""Przegląd R2 TEMATY (#11, W11, ADR-010): strona operatora i zapis jego ocen.

`strona`: samodzielny HTML z pozycjami operatora, bez ocen agenta. Odmawia, gdy plik przeglądu
nie ma hasha ocen agenta albo hash nie zgadza się z ocenami.
`zapisz`: dopisuje JSON operatora do pliku przeglądu; sprawdza klucze, hashe pakietu i próby
oraz hash ocen agenta.
Oceny agenta zapisuje skrypt w folderze zadania przez `agent_review` i `write_review`.
"""
import argparse
from datetime import datetime, timezone
import importlib.util
import json
import os
from pathlib import Path
import sys
import tempfile

_spec = importlib.util.spec_from_file_location('check_tematy_package',
                                               Path(__file__).resolve().with_name('check_tematy_package.py'))
checker = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(checker)
Refused, require, read, digest = checker.Refused, checker.require, checker.read, checker.digest

OPERATOR_KIND = 'literaki-tematy-ocena-operatora'


def _package(root):
    """Pakiet: pliki i SHA256SUMS zgodne z manifestem; zwraca próbę i szablon."""
    root = Path(root)
    manifest = read(root/'release-manifest.json')
    require(manifest.get('kind') == checker.KIND and manifest.get('status') == 'BUILT', 'To nie jest pakiet TEMATY')
    checker.files(root, manifest)
    return manifest, read(root/'reports/sample.json'), read(root/'reports/review-template.json')


def _membership(sample):
    return {i['key']: name for name, s in sample['strata'].items() for i in s['selected']}


def agent_review(root, ratings, reviewer, reviewed_at):
    """Nowy plik przeglądu z ocenami agenta i ich hashem (D12).

    `ratings`: klucz → {'ocena': tak|nie|niepewne, 'powod': tekst}; musi objąć całą próbę.
    """
    root = Path(root)
    manifest, sample, template = _package(root)
    membership = _membership(sample)
    require(set(ratings) == set(membership), 'Oceny agenta: brak albo obce pozycje')
    items = [{'key': k, 'warstwa': membership[k], 'ocena': ratings[k]['ocena'], 'powod': ratings[k]['powod']}
             for k in sorted(ratings)]
    review = {'schema_version': 1, 'kind': checker.REVIEW_KIND, 'method': manifest['method'],
              'temat': manifest['topic']['id'], 'version': template['version'],
              'sha256sums_sha256': digest(root/'SHA256SUMS'), 'sample_sha256': template['sample_sha256'],
              'canonical_index_sha256': template['canonical_index_sha256'],
              'evidence_sha256': template['evidence_sha256'],
              'agent': {'reviewer': reviewer, 'reviewed_at': reviewed_at, 'items': items},
              'agent_sha256': checker.ratings_sha256(items), 'operator': None}
    checker.agent_items(review, membership)
    return review


def write_review(path, review):
    """Zapis atomowy, czytelny JSON (plik leży w folderze zadania)."""
    path = Path(path)
    fd, tmp = tempfile.mkstemp(prefix='.' + path.name + '-', dir=path.parent)
    try:
        with os.fdopen(fd, 'w', encoding='utf-8', newline='\n') as stream:
            stream.write(json.dumps(review, ensure_ascii=False, sort_keys=True, indent=2) + '\n')
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def _bound_review(root, review_path):
    """Plik przeglądu powiązany z pakietem i z hashem ocen agenta; zwraca (przegląd, próba)."""
    _, sample, _ = _package(root)
    review = read(review_path)
    require(isinstance(review, dict), 'Zły plik przeglądu')
    require(review.get('agent_sha256'), 'Brak hasha ocen agenta; najpierw zapisz i zacommituj oceny agenta')
    checker.binding(review, Path(root))
    checker.agent_items(review, _membership(sample))
    return review, sample


def page_items(sample):
    """Pozycje operatora w kolejności rangi, warstwa po warstwie; bez ocen agenta i flag budowy."""
    by_key = {i['key']: i for i in sample['items']}
    out = []
    for name in checker.PROBA:
        for key in sample['operator']['strata'][name]:
            item = by_key[key]
            out.append({'key': key, 'lemat': item['lemat'], 'warstwa': name, 'zrodla': item['zrodla'],
                         'znaczenie': item['znaczenie'], 'formy': item['formy'], 'liczba_form': item['liczba_form']})
    return out


def _script_json(value):
    """JSON bezpieczny w <script>: bez `<`, `>`, `&` i separatorów wierszy U+2028/U+2029."""
    text = json.dumps(value, ensure_ascii=False, sort_keys=True)
    for char, escape in (('<', '\\u003c'), ('>', '\\u003e'), ('&', '\\u0026'),
                         (' ', '\\u2028'), (' ', '\\u2029')):
        text = text.replace(char, escape)
    return text


def page(root, review_path):
    """HTML strony R2. Odmawia bez hasha ocen agenta (D12)."""
    review, sample = _bound_review(root, review_path)
    data = {'kind': OPERATOR_KIND, 'schema_version': 1, 'temat': review['temat'],
            'sample_sha256': review['sample_sha256'], 'sha256sums_sha256': review['sha256sums_sha256'],
            'agent_sha256': review['agent_sha256'], 'items': page_items(sample)}
    return PAGE.replace('@@TEMAT@@', review['temat']).replace('@@DATA@@', _script_json(data))


def record(root, review_path, operator_json, reviewer='operator', reviewed_at=None):
    """Dopisuje oceny operatora do przeglądu; zwraca nowy przegląd (bez zapisu)."""
    review, sample = _bound_review(root, review_path)
    require(review.get('operator') is None, 'Plik przeglądu ma już oceny operatora; nie nadpisujemy')
    given = operator_json
    require(isinstance(given, dict) and given.get('kind') == OPERATOR_KIND and given.get('schema_version') == 1,
            'To nie jest JSON ocen operatora')
    require(given.get('agent_sha256') == review['agent_sha256'], 'Zły hash ocen agenta w JSON operatora')
    for field in ('sample_sha256', 'sha256sums_sha256', 'temat'):
        require(given.get(field) == review[field], 'JSON operatora z innej próby albo pakietu: ' + field)
    ratings = given.get('oceny')
    require(isinstance(ratings, dict), 'Brak ocen w JSON operatora')
    expected = {k: name for name, keys in sample['operator']['strata'].items() for k in keys}
    foreign = sorted(set(ratings) - set(expected))
    missing = sorted(set(expected) - set(ratings))
    require(not foreign, 'Obcy klucz w ocenach operatora: ' + ', '.join(foreign))
    require(not missing, f'Brak oceny operatora ({len(missing)}): ' + ', '.join(missing[:10]))
    bad = sorted(k for k, v in ratings.items() if v not in checker.OCENY)
    require(not bad, 'Ocena spoza tak/nie/niepewne: ' + ', '.join(bad))
    when = reviewed_at or datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    review['operator'] = {'reviewer': reviewer, 'reviewed_at': when, 'agent_sha256': review['agent_sha256'],
                          'items': [{'key': k, 'warstwa': expected[k], 'ocena': ratings[k]} for k in sorted(ratings)]}
    checker.operator_items(review, sample['operator']['strata'])
    return review


PAGE = '''<!doctype html>
<html lang="pl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>Ocena R2: @@TEMAT@@</title>
<style>
:root {
  --bg: #f7f6f2; --card: #ffffff; --text: #1d1d1b; --muted: #5d5d58; --line: #dddcd5;
  --accent: #1f5f8b; --tak: #1e7a3c; --nie: #b3261e; --niepewne: #8a6100; --on: #ffffff;
  color-scheme: light;
}
@media (prefers-color-scheme: dark) {
  :root:not([data-theme="light"]) {
    --bg: #141413; --card: #1f1f1d; --text: #ecebe6; --muted: #a8a7a0; --line: #3a3a36;
    --accent: #7fb6dd; --tak: #5cc27c; --nie: #f2827a; --niepewne: #e0b44a; --on: #141413;
    color-scheme: dark;
  }
}
:root[data-theme="dark"] {
  --bg: #141413; --card: #1f1f1d; --text: #ecebe6; --muted: #a8a7a0; --line: #3a3a36;
  --accent: #7fb6dd; --tak: #5cc27c; --nie: #f2827a; --niepewne: #e0b44a; --on: #141413;
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
h2 { font-size: 18px; margin: 24px 0 8px; }
.card { background: var(--card); border: 1px solid var(--line); border-radius: 12px; padding: 14px; margin: 10px 0;
  overflow-wrap: anywhere; }
.card.done { border-color: var(--accent); }
.lemat { font-size: 22px; font-weight: 700; margin: 0; }
.meta { color: var(--muted); font-size: 14px; margin: 2px 0 8px; }
.zn { margin: 4px 0; font-size: 15px; }
.zn b { font-weight: 600; }
.forms { color: var(--muted); font-size: 14px; margin: 6px 0 10px; }
.btns { display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px; }
button { font: inherit; font-weight: 600; min-height: 52px; border-radius: 10px; border: 2px solid var(--line);
  background: var(--card); color: var(--text); cursor: pointer; touch-action: manipulation; }
button[data-v="tak"][aria-pressed="true"] { background: var(--tak); border-color: var(--tak); color: var(--on); }
button[data-v="nie"][aria-pressed="true"] { background: var(--nie); border-color: var(--nie); color: var(--on); }
button[data-v="niepewne"][aria-pressed="true"] { background: var(--niepewne); border-color: var(--niepewne); color: var(--on); }
.out { margin-top: 28px; }
#copy { width: 100%; background: var(--accent); border-color: var(--accent); color: var(--on); }
#status { color: var(--muted); font-size: 15px; min-height: 1.4em; margin: 8px 0; }
textarea { width: 100%; min-height: 160px; font: 13px/1.4 ui-monospace, Menlo, monospace; color: var(--text);
  background: var(--card); border: 1px solid var(--line); border-radius: 10px; padding: 10px; }
</style>
</head>
<body>
<header><h1>Ocena R2: @@TEMAT@@</h1><p id="progress"></p></header>
<main>
<p class="intro">Czy słowo należy do tematu „@@TEMAT@@”? Wybierz tak, nie albo niepewne.
Na końcu naciśnij „Kopiuj JSON” i wklej wynik w rozmowę. Szkic zostaje w tej przeglądarce.</p>
<div id="list"></div>
<section class="out">
<button id="copy" type="button">Kopiuj JSON</button>
<p id="status" role="status"></p>
<textarea id="json" readonly aria-label="JSON z ocenami"></textarea>
</section>
</main>
<script id="data" type="application/json">@@DATA@@</script>
<script>
(function () {
  var data = JSON.parse(document.getElementById('data').textContent);
  var store = 'tematy-r2-' + data.sample_sha256.slice(0, 16);
  var oceny = {};
  try {
    var saved = JSON.parse(window.localStorage.getItem(store) || '{}');
    data.items.forEach(function (it) {
      var v = saved[it.key];
      if (v === 'tak' || v === 'nie' || v === 'niepewne') { oceny[it.key] = v; }
    });
  } catch (e) { oceny = {}; }

  function save() {
    try { window.localStorage.setItem(store, JSON.stringify(oceny)); } catch (e) { /* szkic tylko w pamięci */ }
  }
  function result() {
    var picked = {};
    data.items.forEach(function (it) { if (oceny[it.key]) { picked[it.key] = oceny[it.key]; } });
    return JSON.stringify({kind: data.kind, schema_version: data.schema_version, temat: data.temat,
      sample_sha256: data.sample_sha256, sha256sums_sha256: data.sha256sums_sha256,
      agent_sha256: data.agent_sha256, oceny: picked});
  }
  function refresh() {
    var done = data.items.filter(function (it) { return oceny[it.key]; }).length;
    document.getElementById('progress').textContent = 'Ocenione: ' + done + ' z ' + data.items.length;
    document.getElementById('json').value = result();
  }
  function el(tag, cls, text) {
    var node = document.createElement(tag);
    if (cls) { node.className = cls; }
    if (text !== undefined) { node.textContent = text; }
    return node;
  }

  var list = document.getElementById('list');
  var layer = null;
  data.items.forEach(function (it) {
    if (it.warstwa !== layer) {
      layer = it.warstwa;
      list.appendChild(el('h2', '', 'Warstwa ' + layer));
    }
    var card = el('article', 'card');
    card.appendChild(el('p', 'lemat', it.lemat));
    card.appendChild(el('p', 'meta', 'Warstwa ' + it.warstwa + ' · źródła: ' + it.zrodla.join(', ')));
    Object.keys(it.znaczenie).sort().forEach(function (w) {
      var p = el('p', 'zn');
      p.appendChild(el('b', '', w + ': '));
      p.appendChild(document.createTextNode(it.znaczenie[w].join('; ')));
      card.appendChild(p);
    });
    var more = it.liczba_form > it.formy.length ? ' … (razem ' + it.liczba_form + ')' : '';
    card.appendChild(el('p', 'forms', 'Formy: ' + it.formy.join(', ') + more));
    var row = el('div', 'btns');
    ['tak', 'nie', 'niepewne'].forEach(function (v) {
      var b = el('button', '', v);
      b.type = 'button';
      b.setAttribute('data-v', v);
      b.setAttribute('aria-pressed', oceny[it.key] === v ? 'true' : 'false');
      b.addEventListener('click', function () {
        oceny[it.key] = v;
        row.querySelectorAll('button').forEach(function (x) {
          x.setAttribute('aria-pressed', x === b ? 'true' : 'false');
        });
        card.classList.add('done');
        save();
        refresh();
      });
      row.appendChild(b);
    });
    if (oceny[it.key]) { card.classList.add('done'); }
    card.appendChild(row);
    list.appendChild(card);
  });

  document.getElementById('copy').addEventListener('click', function () {
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


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest='command', required=True)
    strona = sub.add_parser('strona', help='strona HTML dla operatora')
    zapisz = sub.add_parser('zapisz', help='dopisz oceny operatora do pliku przeglądu')
    for p in (strona, zapisz):
        p.add_argument('--package-dir', required=True)
        p.add_argument('--review', required=True)
    strona.add_argument('--output', required=True)
    zapisz.add_argument('--oceny', required=True, help="plik z JSON operatora albo '-' (stdin)")
    zapisz.add_argument('--reviewer', default='operator')
    args = parser.parse_args(argv)
    try:
        if args.command == 'strona':
            html = page(args.package_dir, args.review)
            Path(args.output).write_text(html, encoding='utf-8')
            print('Strona R2: ' + str(Path(args.output).resolve()))
        else:
            given = json.load(sys.stdin) if args.oceny == '-' else read(args.oceny)
            review = record(args.package_dir, args.review, given, args.reviewer)
            write_review(args.review, review)
            print(f'Zapisano oceny operatora: {len(review["operator"]["items"])} pozycji')
        return 0
    except Refused as error:
        print(str(error), file=sys.stderr)
        return error.code
    except (OSError, ValueError, KeyError, TypeError) as error:
        print('Nieprawidłowy przegląd TEMATY: ' + str(error), file=sys.stderr)
        return 4


if __name__ == '__main__':
    sys.exit(main())
