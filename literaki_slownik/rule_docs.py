"""Katalog reguł słowników (#21): jedna strona z opisem każdej reguły z kodu.

Źródło prawdy o tym, JAKIE reguły istnieją, to kod (`rule_id` w pakiecie) i
`config/generator/policy.json`. Opisy są w `config/generator/rule-docs.json`.
Plik opisów nie jest wejściem builda i nie zmienia list.
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / 'config/generator/rule-docs.json'
PAGE = ROOT / 'docs/generator/reguly.md'
REPO = 'https://github.com/robmar-net/literaki-slownik/blob/main/'
LAYERS = ['konstrukcja', 'język', 'pisownia', 'gra', 'profil', 'zakres', 'ocena']
EFFECTS = {'odrzuca', 'dopuszcza', 'nie wyklucza', 'nierozstrzyga', 'tworzy kandydatów', 'poprawia źródło', '—'}
FIELDS = ['rule_id', 'warstwa', 'broad', 'standard', 'opis', 'przyklad', 'decyzja', 'od']

_RULE_KEY = re.compile(r"""['"]rule_id['"]\s*:\s*['"]([a-z0-9-]+)['"]""")
_RULE_CONST = re.compile(r"""^[A-Z0-9_]*RULE[A-Z0-9_]*\s*=\s*['"]([a-z0-9-]+)['"]""", re.M)


def code_rule_ids(root=ROOT):
    ids = set()
    for path in sorted((root / 'literaki_slownik').glob('*.py')):
        text = path.read_text(encoding='utf-8')
        ids |= set(_RULE_KEY.findall(text)) | set(_RULE_CONST.findall(text))
    policy = json.loads((root / 'config/generator/policy.json').read_text(encoding='utf-8'))
    ids |= {rule['rule_id'] for rule in policy['rules']}
    return ids


def load(path=DOCS):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def problems(docs, ids, root=ROOT):
    """Lista błędów; pusta = katalog zgodny z kodem."""
    out = []
    rules = docs['rules']
    seen = [r.get('rule_id') for r in rules]
    if seen != sorted(seen):
        out.append('reguły nie są posortowane po rule_id')
    if len(seen) != len(set(seen)):
        out.append('powtórzony rule_id')
    for missing in sorted(ids - set(seen)):
        out.append(f'brak opisu reguły z kodu: {missing}')
    for extra in sorted(set(seen) - ids):
        out.append(f'opis reguły, której nie ma w kodzie: {extra}')
    for r in rules:
        rid = r.get('rule_id')
        if sorted(r) != sorted(FIELDS):
            out.append(f'{rid}: pola {sorted(r)} zamiast {sorted(FIELDS)}')
            continue
        if r['warstwa'] not in LAYERS:
            out.append(f'{rid}: nieznana warstwa {r["warstwa"]}')
        for v in ('broad', 'standard'):
            if r[v] not in EFFECTS:
                out.append(f'{rid}: nieznany skutek {v}={r[v]}')
        if not r['opis'].strip():
            out.append(f'{rid}: pusty opis')
        if r['decyzja'] and not r['decyzja'].startswith('http') and not (root / r['decyzja'].split('#')[0]).exists():
            out.append(f'{rid}: decyzja wskazuje nieistniejący plik {r["decyzja"]}')
    return out


def _link(target, base):
    if not target:
        return '—'
    if target.startswith('http'):
        return f'[link]({target})'
    name = Path(target.split('#')[0]).name.removesuffix('.md')
    return f'[{name}]({base}{target})'


def _cell(text):
    return text.replace('|', '\\|').replace('\n', ' ')


def render(docs, base=REPO):
    """Strona Markdown; `base` to prefiks linków do plików repo."""
    rules = docs['rules']
    lines = [
        '# Reguły słowników',
        '',
        '<!-- Wygenerowane: python3 scripts/render_rules.py. Nie edytuj ręcznie; zmieniaj config/generator/rule-docs.json. -->',
        '',
        f'Wszystkie reguły, które oceniają słowa w BROAD i STANDARD: {len(rules)}. Wersja polityki w kodzie: `{docs["policy_version"]}`.',
        'Zasada: słowo jest na liście, gdy choć jedna jego analiza przechodzi wszystkie warstwy. Reguła współczesnego użycia i wyjątki #4 znoszą odrzucenie za dawność. Dla konkretnego słowa: `python3 -m literaki_slownik explain --run-dir <przebieg> --word <słowo>`.',
        '',
        '**Skutek:** „odrzuca” — reguła może usunąć słowo; „nie wyklucza” — sama etykieta nie usuwa; „dopuszcza” — warunek spełniony, słowo wchodzi, jeśli nic innego go nie odrzuca; „nierozstrzyga” — brak oceny, słowo nie wchodzi; „poprawia źródło” — naprawia błąd w SGJP; „tworzy kandydatów” — reguła składa nowe formy, ocenia je reszta; „—” — nie dotyczy.',
        '**Od:** wersja polityki i data commitu, który wprowadził regułę.',
        '',
    ]
    for layer in LAYERS:
        group = [r for r in rules if r['warstwa'] == layer]
        if not group:
            continue
        lines += [f'## {layer.capitalize()} ({len(group)})', '',
                  '| reguła | BROAD | STANDARD | co robi | przykład | decyzja | od |',
                  '|---|---|---|---|---|---|---|']
        for r in group:
            lines.append('| `{}` | {} | {} | {} | {} | {} | {} |'.format(
                r['rule_id'], r['broad'], r['standard'], _cell(r['opis']),
                _cell(r['przyklad']) or '—', _link(r['decyzja'], base), _cell(r['od'])))
        lines.append('')
    return '\n'.join(lines)
