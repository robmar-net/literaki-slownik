"""Oceny agenta R2 dla pakietów v2 (#13): przeniesienie z #12 i scalenie z nowymi.

Próba to ranking hashem klucza (`tematy-quality-v1`), więc v2 losuje głównie te same klucze co v1.
Ocena z #12 przechodzi tylko wtedy, gdy klucz i cały `selected_unit` są identyczne. Resztę ocenia agent.

  python3 przenies_oceny.py przygotuj   → analysis/do-oceny-<id>.json (pozycje do oceny) i podsumowanie
  python3 przenies_oceny.py scal        → analysis/agent-ratings-<id>.json (przeniesione + nowe-oceny-<id>.json)

Zła liczba lub nieznany klucz w nowych ocenach: odmowa, nic nie jest zapisane.
"""
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

TASK = Path(__file__).resolve().parents[1]
REPO = TASK.parents[3]
STARE = REPO/'.maister/tasks/development/2026-10-29-12-tematy-fala-1/analysis'
TEMATY = ('grzyby', 'pogoda', 'matematyka', 'muzyka', 'sport', 'kuchnia', 'medycyna')
OCENY = {'tak', 'nie', 'niepewne'}


def czytaj(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def pisz(path, value):
    Path(path).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def szablon(temat, wersja):
    return {i['key']: i for i in czytaj(REPO/f'data/work/tematy-{temat}-{wersja}-20261029-a/reports/review-template.json')['items']}


def podziel(temat):
    """Zwraca (przeniesione oceny, pozycje do oceny) dla tematu."""
    nowe, stare = szablon(temat, 'v2'), szablon(temat, 'v1')
    oceny = czytaj(STARE/f'agent-ratings-{temat}.json')['oceny']
    przeniesione, do_oceny = {}, []
    for key, item in nowe.items():
        if key in stare and stare[key]['selected_unit'] == item['selected_unit'] and key in oceny:
            przeniesione[key] = oceny[key]
        else:
            do_oceny.append({'key': key, 'selected_unit': item['selected_unit'], 'strata': item['strata']})
    return przeniesione, do_oceny


def przygotuj():
    podsumowanie = {}
    for temat in TEMATY:
        przeniesione, do_oceny = podziel(temat)
        pisz(TASK/f'analysis/do-oceny-{temat}.json', {'temat': temat, 'items': do_oceny})
        podsumowanie[temat] = {'przeniesione': len(przeniesione), 'do_oceny': len(do_oceny)}
        print(temat, podsumowanie[temat], flush=True)
    pisz(TASK/'verification/przeniesienie-ocen.json', podsumowanie)


def scal():
    kod = 0
    for temat in TEMATY:
        przeniesione, do_oceny = podziel(temat)
        path = TASK/f'analysis/nowe-oceny-{temat}.json'
        nowe = czytaj(path)['oceny'] if do_oceny else {}
        klucze = {i['key'] for i in do_oceny}
        zle = [k for k, v in nowe.items() if k not in klucze or not isinstance(v, dict)
               or set(v) != {'ocena', 'powod'} or v['ocena'] not in OCENY or not str(v['powod']).strip()]
        if set(nowe) != klucze or zle:
            print(temat, 'ODMOWA: brak', sorted(klucze - set(nowe)), 'złe', zle, file=sys.stderr)
            kod = 1
            continue
        pisz(TASK/f'analysis/agent-ratings-{temat}.json', {
            'reviewer': 'agent (Claude)',
            'reviewed_at': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
            'oceny': dict(sorted({**przeniesione, **nowe}.items()))})
        print(temat, 'scalono', len(przeniesione), '+', len(nowe), flush=True)
    return kod


if __name__ == '__main__':
    tryb = sys.argv[1:] or ['?']
    if tryb == ['przygotuj']:
        przygotuj()
    elif tryb == ['scal']:
        sys.exit(scal())
    else:
        sys.exit(__doc__)
