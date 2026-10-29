"""Kontrola słów oczywistych (#12, W10.2): słowo liczy się tak, jak w teście słów budowy.

Słowo przechodzi, gdy jest `lemma_base` leksemu SGJP z klasą tagu z `czesci_mowy`
(`inf`, `subst`, `depr`, `adv`, `adj`), a ten leksem ma formę w STANDARD v31.
Formy jak w budowie: `tematy._read_forms` (interpretacje plus konstrukcje ∈ BROAD).
Sama forma w STANDARD nie wystarcza (`nuty`, `zawody`).

Powody odpadnięcia: NIE_JEDNO_SLOWO, FORMA_NIE_LEMAT, BRAK_LEKSEMU, KLASA_SPOZA, POZA_STANDARD.

Uruchomienie (z korzenia repozytorium):
  python3 <T>/analysis/sprawdz_slowa.py <T>/analysis/slowa-oczywiste.json <T>/verification/slowa-oczywiste-check.json
Każde uruchomienie dopisuje rundę do pliku wyniku. Kod 1, gdy jakieś słowo odpadło.
"""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import sys

TASK = Path(__file__).resolve().parents[1]
REPO = TASK.parents[3]
sys.path.insert(0, str(REPO))
from literaki_slownik.canonical import load_json, sha256  # noqa: E402
from literaki_slownik.pop00 import read_words  # noqa: E402
from literaki_slownik.tematy import CZESCI_MOWY, _chunks, _lexeme_rows, _read_forms, _readonly  # noqa: E402

SOURCES = REPO / 'config/generator/tematy-sources.json'
KLASY = frozenset(k for v in CZESCI_MOWY.values() for k in v)
SLOWO = re.compile(r'[a-ząćęłńóśźż]+')


def _klasy(db, ids):
    """Leksem → klasy tagów (pierwszy segment), przez indeks `lexeme_id`, jak `scan_sgjp` dla całości."""
    found = {i: set() for i in ids}
    for chunk, marks in _chunks(ids):
        for ident, tag in db.execute(f'SELECT lexeme_id, tag FROM interpretation WHERE lexeme_id IN ({marks})', chunk):
            found[ident].add(tag.split(':', 1)[0])
    return found


def sprawdz(db_path, standard, broad, tematy):
    """`tematy`: id → słowa. Zwraca id → słowo → powód (None = przechodzi)."""
    words = {w for ws in tematy.values() for w in ws}
    ok_format = {w for w in words if SLOWO.fullmatch(w)}
    reasons = {w: 'NIE_JEDNO_SLOWO' for w in words - ok_format}
    with _readonly(db_path) as db:
        rows = _lexeme_rows(db, 'lemma_base', ok_format)
        klasy = _klasy(db, rows)
        allowed = {i: r for i, r in rows.items() if klasy[i] & KLASY}
        forms = _read_forms(db, {'broad': broad}, allowed)
        surface = set()
        for chunk, marks in _chunks(ok_format):
            surface.update(f for (f,) in db.execute(
                f'SELECT original FROM surface_form WHERE original IN ({marks})', chunk))
    by_base = {}
    for ident, row in rows.items():
        by_base.setdefault(row[2], []).append(ident)
    for word in ok_format:
        ids = by_base.get(word, [])
        if not ids:
            reasons[word] = 'FORMA_NIE_LEMAT' if word in surface else 'BRAK_LEKSEMU'
        elif not any(i in allowed for i in ids):
            reasons[word] = 'KLASA_SPOZA'
        elif not any(forms[i] & standard for i in ids if i in allowed):
            reasons[word] = 'POZA_STANDARD'
        else:
            reasons[word] = None
    return {t: {w: reasons[w] for w in ws} for t, ws in tematy.items()}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split('\n', 1)[0])
    parser.add_argument('slowa', type=Path, help='slowa-oczywiste.json ({szkic: {id: [...]}, wynik})')
    parser.add_argument('wynik', type=Path, help='plik kontroli; runda jest dopisywana')
    args = parser.parse_args(argv)
    pins = load_json(SOURCES)['inputs']
    paths = {k: (SOURCES.parent / pins[k]['path']).resolve() for k in ('database', 'standard', 'broad')}
    wejscia = {}
    for key, path in paths.items():
        digest = sha256(path)
        if digest != pins[key]['sha256']:
            raise SystemExit(f'{key}: hash {digest} różny od pinu {pins[key]["sha256"]}')
        wejscia[key] = {'path': path.relative_to(REPO).as_posix(), 'sha256': digest}
    standard, broad = read_words(paths['standard']), read_words(paths['broad'])
    tematy = load_json(args.slowa)['szkic']
    result = sprawdz(paths['database'], standard, broad, tematy)
    runda = {
        'czas': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
        'slowa_sha256': sha256(args.slowa),
        'tematy': {t: {'slowa': len(r), 'przeszlo': sum(v is None for v in r.values()),
                       'odpadlo': {w: v for w, v in sorted(r.items()) if v}} for t, r in result.items()},
    }
    runda['wszystkie_przeszly'] = not any(v['odpadlo'] for v in runda['tematy'].values())
    out = load_json(args.wynik) if args.wynik.exists() else {}
    out.update({'regula': 'W10.2: lemma_base leksemu SGJP, klasa z czesci_mowy, forma leksemu w STANDARD v31',
                'klasy': sorted(KLASY), 'wejscia': wejscia})
    out.setdefault('rundy', []).append(runda)
    args.wynik.write_text(json.dumps(out, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    for t, v in runda['tematy'].items():
        print(f'{t}: {v["przeszlo"]}/{v["slowa"]}', *(f'{w}={p}' for w, p in v['odpadlo'].items()))
    return 0 if runda['wszystkie_przeszly'] else 1


if __name__ == '__main__':
    sys.exit(main())
