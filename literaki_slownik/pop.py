"""Słowniki POP i POP0: manifest źródeł, piny podstawy LL-PL i wspólne ładowanie danych.

Krok tylko do odczytu. Wejścia to KWJP (z zamrożonej bazy) i NKJP 1grams (ADR-006).
"""
from collections import defaultdict
import gzip
import json
from pathlib import Path
import re
import unicodedata
from .canonical import load_json, sha256
from .inputs import GeneratorError, checked_file
from .kwjp import METRICS

VERSION = 'pop-sources-v1'
TOP_KEYS = {'schema_version', 'project', 'version', 'base', 'inputs'}
BASE_KEYS = {'package_id', 'run_dir', 'release_dir', 'database_sha256', 'release_manifest_sha256',
             'standard_sha256'}
INPUT_KEYS = {'kwjp': {'source_id', 'kind', 'origin', 'lemma_sources', 'used_for'},
              'nkjp_1gram': {'source_id', 'kind', 'path', 'sha256', 'title', 'creator', 'url', 'license',
                             'used_for'}}
GENRES = {'all', 'fakt', 'fikcja', 'publicystyka'}
SHA = re.compile('[0-9a-f]{64}')


def _text(value):
    return isinstance(value, str) and bool(value)


def _exact(value, keys, what):
    if not isinstance(value, dict) or set(value) != keys:
        raise GeneratorError(f'Nieznane lub brakujące klucze: {what}', 2)


def _validate(manifest):
    _exact(manifest, TOP_KEYS, 'manifest POP')
    if (type(manifest['schema_version']) is not int or manifest['schema_version'] != 1
            or manifest['project'] != 'literaki-slownik' or manifest['version'] != VERSION):
        raise GeneratorError('Nieobsługiwany schemat manifestu POP', 2)
    base = manifest['base']
    _exact(base, BASE_KEYS, 'base')
    if not all(_text(base[k]) for k in ('package_id', 'run_dir', 'release_dir')):
        raise GeneratorError('Nieprawidłowe ścieżki podstawy', 2)
    if not all(isinstance(base[k], str) and SHA.fullmatch(base[k]) for k in BASE_KEYS if k.endswith('_sha256')):
        raise GeneratorError('Nieprawidłowy SHA256 podstawy', 2)
    inputs = manifest['inputs']
    if not isinstance(inputs, list):
        raise GeneratorError('inputs musi być listą', 2)
    kinds = []
    for item in inputs:
        kind = item.get('kind') if isinstance(item, dict) else None
        if kind not in INPUT_KEYS:
            raise GeneratorError(f'Niedozwolone wejście POP: {kind}', 2)
        _exact(item, INPUT_KEYS[kind], kind)
        if not all(_text(v) for k, v in item.items() if k != 'lemma_sources'):
            raise GeneratorError(f'Puste pole wejścia {kind}', 2)
        if kind == 'kwjp':
            lemma = item['lemma_sources']
            if (item['origin'] != 'database' or not isinstance(lemma, dict) or 'all' not in lemma
                    or set(lemma) - GENRES or not all(_text(v) for v in lemma.values())):
                raise GeneratorError('KWJP: tylko z bazy, lemma_sources z gatunkami all/fakt/fikcja/publicystyka', 2)
        elif not SHA.fullmatch(item['sha256']):
            raise GeneratorError('Nieprawidłowy SHA256 NKJP', 2)
        kinds.append(kind)
    if sorted(kinds) != ['kwjp', 'nkjp_1gram'] or len({i['source_id'] for i in inputs}) != 2:
        raise GeneratorError('Manifest POP wymaga dokładnie jednego KWJP i jednego NKJP', 2)


def load_sources(path):
    """Wczytaj i ściśle sprawdź `pop-sources.json`; błąd schematu = kod 2."""
    path = Path(path).resolve()
    try:
        manifest = load_json(path)
    except (OSError, ValueError) as error:
        raise GeneratorError(f'Nie można wczytać manifestu POP: {error}', 2, str(path)) from error
    _validate(manifest)
    return {**manifest, 'manifest_path': str(path), 'manifest_sha256': sha256(path)}


def database_sha256(path):
    """SHA256 bazy strumieniem po 1 MB (`canonical.sha256`)."""
    return sha256(path)


def _input(sources, kind):
    return next(i for i in sources['inputs'] if i['kind'] == kind)


def check_inputs(sources, run_dir=None, release_dir=None):
    """Sprawdź podstawę LL-PL i NKJP wobec pinów. FROZEN → inaczej kod 5; niezgodność → kod 3.

    Hash bazy liczony na końcu (największy plik). Zwraca ścieżki i zmierzony hash bazy.
    """
    base_dir = Path(sources['manifest_path']).parent
    base = sources['base']
    run = Path(run_dir or base_dir / base['run_dir']).resolve()
    release = Path(release_dir or base_dir / base['release_dir']).resolve()
    run_manifest_path = run / 'manifest.json'
    if not run_manifest_path.is_file():
        raise GeneratorError('Brak manifest.json przebiegu', 3, str(run_manifest_path))
    try:
        run_manifest = load_json(run_manifest_path)
    except (OSError, ValueError) as error:
        raise GeneratorError(f'Nieczytelny manifest.json przebiegu: {error}', 3, str(run_manifest_path)) from error
    if not isinstance(run_manifest, dict) or run_manifest.get('readiness') != 'FROZEN':
        raise GeneratorError('Przebieg nie jest FROZEN', 5, str(run))
    exported = (run_manifest.get('export') or {}).get('release_manifest_sha256')
    if exported != base['release_manifest_sha256']:
        raise GeneratorError('export.release_manifest_sha256 przebiegu ≠ pin', 3, str(run_manifest_path))
    verified = (run_manifest.get('verification') or {}).get('database_sha256')
    if verified != base['database_sha256']:
        raise GeneratorError('verification.database_sha256 przebiegu ≠ pin', 3, str(run_manifest_path))
    known = {a.get('source_id'): a for a in (run_manifest.get('inputs') or {}).get('artifacts', [])}
    for genre, source_id in _input(sources, 'kwjp')['lemma_sources'].items():
        artifact = known.get(source_id)
        if not artifact or artifact.get('kind') != 'kwjp_lemma' or artifact.get('genre') != genre:
            raise GeneratorError(f'Brak listy lemma KWJP w przebiegu: {source_id}', 3, str(run_manifest_path))
    release_manifest = checked_file(release, {'path': 'release-manifest.json',
                                              'sha256': base['release_manifest_sha256']})
    standard = checked_file(run, {'path': 'lists/standard.txt', 'sha256': base['standard_sha256']})
    nkjp_input = _input(sources, 'nkjp_1gram')
    nkjp = checked_file(base_dir, {'path': nkjp_input['path'], 'sha256': nkjp_input['sha256']})
    database = run / 'build.sqlite'
    if not database.is_file():
        raise GeneratorError('Brak bazy przebiegu', 3, str(database))
    measured = database_sha256(database)
    if measured != base['database_sha256']:
        raise GeneratorError('Niezgodny SHA256 bazy', 3, str(database))
    return {'run_dir': str(run), 'release_dir': str(release), 'release_manifest': str(release_manifest),
            'release_manifest_sha256': base['release_manifest_sha256'], 'standard': str(standard),
            'standard_sha256': base['standard_sha256'], 'nkjp': str(nkjp), 'nkjp_sha256': nkjp_input['sha256'],
            'database': str(database), 'database_sha256': measured}


def read_standard(path):
    """Klucze gry z `lists/standard.txt` (jeden na wiersz, `\\n`)."""
    with Path(path).open('r', encoding='utf-8', newline='\n') as stream:
        return frozenset(line.rstrip('\n') for line in stream if line != '\n')


# --- Dane z bazy tylko do odczytu (A6, A8, A9) ---
# Połączenie otwiera wywołujący: `database.connect(path, readonly=True)`.
# Zapytania bez sortowania i bez złączeń zewnętrznych; łączenie i agregacja w Pythonie.

STATUSES = ('EXACT_CANDIDATE', 'AMBIGUOUS', 'UNMATCHED')
COLLOQUIAL = 'pot.'
COMMON_NAME = 'nazwa_pospolita'


def _tokens(text, separator):
    return frozenset(t.strip() for t in text.split(separator) if t.strip())


def load_lexemes(db):
    """`lexeme.id` → klucz `(source_id, lemma_id)`, lemat, POS, kwalifikatory, nazwy.

    Potoczny = `pot.` w dowolnej interpretacji. Nazwa własna = etykieta nazwy inna niż pospolita.
    """
    found = {lexeme_id: [source_id, lemma_id, lemma, set(), set(), set()]
             for lexeme_id, source_id, lemma_id, lemma in db.execute(
                 'select id,source_id,lemma_id,lemma_base from lexeme')}
    parsed = {}  # te same (tag, names, qualifiers) powtarzają się milionami
    for lexeme_id, tag, names, qualifiers in db.execute('select lexeme_id,tag,names,qualifiers from interpretation'):
        item = parsed.get((tag, names, qualifiers))
        if item is None:
            item = parsed[tag, names, qualifiers] = (tag.split(':', 1)[0], _tokens(names, '|'),
                                                     _tokens(qualifiers, ','))
        entry = found[lexeme_id]
        entry[3].add(item[0])
        entry[4] |= item[1]
        entry[5] |= item[2]
    return {lexeme_id: {'key': (source_id, lemma_id), 'source_id': source_id, 'lemma': lemma,
                        'pos': tuple(sorted(pos)), 'names': tuple(sorted(names)),
                        'qualifiers': tuple(sorted(qualifiers)), 'colloquial': COLLOQUIAL in qualifiers,
                        'proper': bool(names - {COMMON_NAME})}
            for lexeme_id, (source_id, lemma_id, lemma, pos, names, qualifiers) in found.items()}


def _keys(db, lexemes):
    if lexemes is not None:
        return {lexeme_id: item['key'] for lexeme_id, item in lexemes.items()}
    return {i: (s, lemma) for i, s, lemma in db.execute('select id,source_id,lemma_id from lexeme')}


def _evidence_range(db, source_id):
    first, last, count = db.execute('select min(id),max(id),count(*) from corpus_evidence where source_id=?',
                                    (source_id,)).fetchone()
    if not count:
        raise GeneratorError(f'Brak listy KWJP w bazie: {source_id}', 3)
    if last - first + 1 != count:
        raise GeneratorError(f'Zakres evidence_id listy KWJP nie jest ciągły: {source_id}', 4)
    return first, last


def load_kwjp(db, source_id, lexemes=None):
    """Wiersze jednej listy lemma KWJP z powiązaniami do leksemów.

    Zakres `evidence_id` per `source_id`, potem `evidence_link` i `evidence_candidate` w tym zakresie.
    Wiersz: numer, jednostka, POS, F, miary z `kwjp.METRICS`, status, klucze leksemów (posortowane).
    """
    keys = _keys(db, lexemes)
    first, last = _evidence_range(db, source_id)
    statuses = dict(db.execute('select evidence_id,status from evidence_link where evidence_id between ? and ?',
                               (first, last)))
    linked = defaultdict(set)
    for evidence_id, lexeme_id in db.execute(
            'select evidence_id,lexeme_id from evidence_candidate '
            'where evidence_id between ? and ? and lexeme_id is not null', (first, last)):
        linked[evidence_id].add(keys[lexeme_id])
    rows = []
    for evidence_id, source, number, unit, unit_2, pos, typed, freq in db.execute(
            'select id,source_id,row_number,unit_1,unit_2,pos,typed_metrics,freq from corpus_evidence '
            'where id between ? and ?', (first, last)):
        status, members = statuses.get(evidence_id), tuple(sorted(linked.get(evidence_id, ())))
        if source != source_id or status not in STATUSES:
            raise GeneratorError(f'Wiersz KWJP bez powiązania lemma: {source_id}', 4, None, number)
        expected = {'EXACT_CANDIDATE': 1, 'UNMATCHED': 0}.get(status, max(len(members), 2))
        if len(members) != expected:
            raise GeneratorError(f'Status KWJP niezgodny z liczbą leksemów: {status}', 4, source_id, number)
        typed = json.loads(typed)
        rows.append({'source_id': source, 'row': number, 'evidence_id': evidence_id, 'unit': unit,
                     'unit_2': unit_2, 'pos': pos, 'freq': freq,
                     'metrics': {m: typed[m] for m in METRICS if m in typed}, 'status': status,
                     'lexemes': members})
    rows.sort(key=lambda r: r['row'])
    return rows


def load_kwjp_lists(db, lemma_sources, lexemes=None):
    """Lista `all` i listy gatunków z `lemma_sources` (gatunek → source_id)."""
    if lexemes is None:
        lexemes = {i: {'key': k} for i, k in _keys(db, None).items()}
    genres = {genre: load_kwjp(db, source_id, lexemes) for genre, source_id in sorted(lemma_sources.items())
              if genre != 'all'}
    return load_kwjp(db, lemma_sources['all'], lexemes), genres


def kwjp_measures(rows, genres=None):
    """Miary KWJP jednostek z listy `all` (§8.1).

    Leksem (EXACT): F sumowane po wierszach; ARF, 1-DP i gatunki z wiersza o największym F
    (remis: klucz wiersza). Wiersz AMBIGUOUS = grupa homonimów (krotka kluczy); F zostaje przy grupie,
    członkowie nie dostają własnego F. Nigdy suma ARF/1-DP ani korpusu z podkorpusami.
    """
    if len({r['source_id'] for r in rows}) > 1:
        raise ValueError('Miary KWJP tylko z jednej listy (all); bez sumy z podkorpusami')
    present = {genre: {(r['unit'], r['unit_2'], r['pos']) for r in items}
               for genre, items in (genres or {}).items()}
    mass = {'total': 0, **{status: 0 for status in STATUSES}}
    units = defaultdict(list)
    for row in rows:
        mass['total'] += row['freq']
        mass[row['status']] += row['freq']
        if row['status'] == 'EXACT_CANDIDATE':
            units['lexemes', row['lexemes'][0]].append(row)
        elif row['status'] == 'AMBIGUOUS':
            units['groups', row['lexemes']].append(row)
    result = {'lexemes': {}, 'groups': {}}
    for (kind, key), items in units.items():
        best = min(items, key=lambda r: (-r['freq'], r['source_id'], r['row']))
        unit = (best['unit'], best['unit_2'], best['pos'])
        result[kind][key] = {'F': sum(r['freq'] for r in items), 'ARF': best['metrics']['ARF'],
                             '1-DP': best['metrics']['1-DP'], 'row': best['row'], 'row_F': best['freq'],
                             'rows': len(items),
                             'genres': tuple(sorted(g for g, seen in present.items() if unit in seen)),
                             'status': best['status']}
    return {'lexemes': dict(sorted(result['lexemes'].items())),
            'groups': dict(sorted(result['groups'].items())), 'mass': mass}


def _standard_surface(db, standard):
    return {form_id: key for form_id, key in db.execute('select id,game_key from surface_form') if key in standard}


def _frozen(forms):
    return {key: frozenset(values) for key, values in sorted(forms.items())}


def load_forms(db, standard, lexemes=None):
    """Reguła (i): forma ∈ STANDARD i jest formą leksemu (`interpretation` → `surface_form`)."""
    keys, surface = _keys(db, lexemes), _standard_surface(db, standard)
    forms = defaultdict(set)
    for lexeme_id, form_id in db.execute('select lexeme_id,form_id from interpretation'):
        key = surface.get(form_id)
        if key is not None:
            forms[keys[lexeme_id]].add(key)
    return _frozen(forms)


def load_forms_accepted(db, standard, lexemes=None):
    """Reguła (ii): analiza tego leksemu przyjęta w STANDARD (`analysis` + `variant_decision`).

    Osobna funkcja, żeby zmierzyć jej czas (A9). Konstrukcje (bez `interpretation_id`) tu nie wchodzą.
    """
    keys = _keys(db, lexemes)
    forms = defaultdict(set)
    for lexeme_id, key in db.execute(
            'select i.lexeme_id,a.game_key from variant_decision d '
            'join analysis a on a.analysis_key=d.analysis_key '
            'join interpretation i on i.id=a.interpretation_id '
            "where d.variant='standard' and d.membership_status='accept'"):
        if key in standard:
            forms[keys[lexeme_id]].add(key)
    return _frozen(forms)


def load_constructions(db, standard, lexemes=None, surface_keys=None):
    """Formy konstrukcji (`derivation_candidate`) ∈ STANDARD → leksem składnika.

    Klucz leksemu: `derivation_candidate.lemma_id` + `source_id` składnika źródłowego.
    Liczniki A9 (jeden / żaden / kilka leksemów) tylko dla form STANDARD spoza `surface_form`.
    """
    known = set(_keys(db, lexemes).values())
    if surface_keys is None:
        surface_keys = set(_standard_surface(db, standard).values())
    owners = {}
    for key, lemma_id, source_id in db.execute(
            'select c.game_key,c.lemma_id,p.source_id from derivation_candidate c '
            'join derivation_component p on p.candidate_key=c.candidate_key '
            "where p.kind='source_interpretation'"):
        if key in standard:
            found = owners.setdefault(key, set())
            if (source_id, lemma_id) in known:
                found.add((source_id, lemma_id))
    forms = defaultdict(set)
    for key, lexeme_keys in owners.items():
        for lexeme_key in lexeme_keys:
            forms[lexeme_key].add(key)
    only = sorted(key for key in owners if key not in surface_keys)
    classes = {'one': [k for k in only if len(owners[k]) == 1], 'none': [k for k in only if not owners[k]],
               'several': [k for k in only if len(owners[k]) > 1]}
    return {'forms': _frozen(forms), 'only_constructions': len(only),
            'counts': {name: len(keys) for name, keys in classes.items()},
            'examples': {name: keys[:10] for name, keys in classes.items() if name != 'one'}}


# --- NKJP 1grams: ranga leksemu bez kopiowania F (A10, C7, C8, C14, D4) ---

CLEANING_RULES = {'full-nfc': 'nkjp-clean-full-nfc-v1', 'strip-edges': 'nkjp-clean-strip-edges-v1',
                  'strip-edges-keep-dot': 'nkjp-clean-strip-edges-keep-dot-v1'}
NKJP_LINE = re.compile(r' *([0-9]+) (.+)\n')


def _game_key(text):
    """Ta sama normalizacja co `game_key` w bazie: NFC, małe litery, NFC."""
    return unicodedata.normalize('NFC', unicodedata.normalize('NFC', text).lower())


def _strip(key, keep_dot):
    """Zdejmij znaki interpunkcji (kategoria P*) z obu brzegów; `keep_dot` zatrzymuje się na kropce."""
    strip = lambda ch: unicodedata.category(ch)[0] == 'P' and not (keep_dot and ch == '.')
    start, end = 0, len(key)
    while start < end and strip(key[start]):
        start += 1
    while end > start and strip(key[end - 1]):
        end -= 1
    return key[start:end]


def read_nkjp(path, rule, keys):
    """Strumień 1grams.gz (` *liczba napis\\n`) → masa po kluczu gry wg reguły czyszczenia D4.

    Suma całości liczona ze wszystkich wierszy. W pamięci zostają tylko klucze z `keys`
    (formy SGJP) oraz, dla reguł zdejmujących interpunkcję, napisy scalone z takim kluczem.
    Zły wiersz → kod 4; nieznana reguła → kod 2.
    """
    if rule not in CLEANING_RULES:
        raise GeneratorError(f'Nieznana reguła czyszczenia NKJP: {rule}', 2)
    strip, keep_dot = rule != 'full-nfc', rule == 'strip-edges-keep-dot'
    forms, merged = defaultdict(int), defaultdict(lambda: defaultdict(int))
    total = lines = 0
    with gzip.open(path, 'rt', encoding='utf-8', newline='') as stream:
        for lines, line in enumerate(stream, 1):
            match = NKJP_LINE.fullmatch(line)
            if not match:
                raise GeneratorError('Wiersz NKJP poza formatem ` *liczba napis`', 4, str(path), lines)
            count, raw = int(match[1]), _game_key(match[2])
            total += count
            key = raw
            if strip and not (raw[0].isalnum() and raw[-1].isalnum()):
                key = _strip(raw, keep_dot)
            if key in keys:
                forms[key] += count
                if key != raw:
                    merged[key][raw] += count
    return {'rule': rule, 'rule_id': CLEANING_RULES[rule], 'path': str(path), 'lines': lines, 'total': total,
            'matched': sum(forms.values()), 'forms': dict(forms),
            'merged': {key: dict(sources) for key, sources in merged.items()}}


def nkjp_collisions(nkjp, top=None):
    """Klucze, z którymi reguła scaliła inne napisy (`ul.`→`ul`), wg masy scalonej; remis: klucz.

    `kept` = masa napisu bez zmian, `merged` = masa napisów scalonych, `sources` = te napisy z masą.
    """
    found = []
    for key, sources in nkjp['merged'].items():
        mass = sum(sources.values())
        found.append({'key': key, 'kept': nkjp['forms'][key] - mass, 'merged': mass,
                      'sources': sorted(sources.items(), key=lambda item: (-item[1], item[0]))})
    found.sort(key=lambda item: (-item['merged'], item['key']))
    return found if top is None else found[:top]


def form_owners(db, lexemes=None):
    """`game_key` → posortowana krotka kluczy leksemów, do których forma należy.

    Wszystkie leksemy w bazie (SGJP i uzupełnienie), z nazwami własnymi i analizami odrzuconymi
    w LL-PL: liczy się każda interpretacja. Jeden przebieg `interpretation` ⋈ `surface_form`.
    """
    single = {lexeme_id: (key,) for lexeme_id, key in _keys(db, lexemes).items()}
    owners = {}
    for lexeme_id, key in db.execute('select i.lexeme_id,s.game_key from interpretation i '
                                     'join surface_form s on s.id=i.form_id'):
        mine, current = single[lexeme_id], owners.get(key)
        if current is None:
            owners[key] = mine
        elif current is not mine and mine[0] not in current:
            owners[key] = tuple(sorted(current + mine))
    return owners


def nkjp_form_status(nkjp, key):
    """Status formy w NKJP; brak wiersza to `NOT_IN_PUBLISHED_LIST`, nigdy 0."""
    return 'OBSERVED' if key in nkjp['forms'] else 'NOT_IN_PUBLISHED_LIST'


def _percentile(rank, count):
    return round(100 * (count - rank + 1) / count, 4)


def nkjp_lexeme_ranks(nkjp, owners):
    """Ranga i percentyl NKJP leksemu; F tylko z form jednoznacznych wobec wszystkich leksemów SGJP.

    Ranga: pozycja wg `(-F, klucz leksemu)`; percentyl 100 dla pierwszego. Wyjście bez F (C14).
    Status: `OBSERVED`; `UNMATCHED` (formy w NKJP są, ale każda wspólna z innym leksemem);
    `NOT_IN_PUBLISHED_LIST` (żadnej formy w liście). Masa: całość, dopasowana, przypisana, wspólna.
    """
    mass, shared = defaultdict(int), set()
    universe = set()
    for key, members in owners.items():
        universe.update(members)
        count = nkjp['forms'].get(key)
        if count is None:
            continue
        if len(members) == 1:
            mass[members[0]] += count
        else:
            shared.update(members)
    ranked = sorted(mass, key=lambda key: (-mass[key], key))
    position = {key: number for number, key in enumerate(ranked, 1)}
    lexemes = {}
    for key in sorted(universe):
        if key in position:
            lexemes[key] = {'status': 'OBSERVED', 'rank': position[key],
                            'percentile': _percentile(position[key], len(ranked))}
        else:
            lexemes[key] = {'status': 'UNMATCHED' if key in shared else 'NOT_IN_PUBLISHED_LIST',
                            'rank': None, 'percentile': None}
    attributed = sum(mass.values())
    return {'rule_id': nkjp['rule_id'], 'lexemes': lexemes,
            'mass': {'total': nkjp['total'], 'matched': nkjp['matched'], 'attributed': attributed,
                     'shared': nkjp['matched'] - attributed}}


# --- Jednostki, miary, rangi, pokrycie, progi i formy: opcje D1–D8 (C5–C10, C14) ---
# Identyfikatory opcji są wartościami parametrów; spoza listy → kod 2. Brak danych to `None` ze statusem,
# nigdy 0. Rangi: `(-miara, klucz jednostki)`, sortowanie w Pythonie.

D1_OPTIONS = ('kwjp-all', 'kwjp-exact', 'kwjp-standard')
D2_CLASSES = ('voc', 'impt', 'participle', 'person-1-2')
D2_CONSTRUCTIONS = ('yes', 'no')
D2_MEMBERSHIP = ('i', 'ii')
D3_SOURCES = ('kwjp', 'kwjp+nkjp')
D3_FIELDS = ('F', 'ARF', '1-DP', 'genres')
D5_OPTIONS = ('a', 'b', 'c', 'd', 'e')
D6_BY = ('count', 'coverage')
D8_PARTIAL = ('available-only', 'lower-bound', 'exclude')
PARTICIPLES = frozenset({'pact', 'ppas', 'pcon', 'pant'})
KWJP_ABSENT = 'ABSENT_OR_BELOW_PUBLICATION_THRESHOLD'
NKJP_ABSENT = 'NOT_IN_PUBLISHED_LIST'


def _option(value, allowed, what):
    if not isinstance(value, str) or value not in allowed:
        raise GeneratorError(f'Nieznana opcja {what}: {value!r}', 2)
    return value


def _number(value, low, high, what, *, integer=False, low_open=False):
    kinds = (int,) if integer else (int, float)
    if (type(value) not in kinds or value != value or value > high
            or (value <= low if low_open else value < low)):
        raise GeneratorError(f'Liczba spoza zakresu: {what} = {value!r}', 2)
    return value


class _Groups:
    """Union-find na kluczach leksemów; klucz grupy = posortowana krotka członków."""

    def __init__(self):
        self.parent = {}

    def find(self, key):
        parent = self.parent.setdefault(key, key)
        while parent != key:
            grand = self.parent[parent]
            self.parent[key] = grand
            key, parent = parent, grand
        return key

    def union(self, keys):
        first = self.find(keys[0])
        for key in keys[1:]:
            other = self.find(key)
            if other != first:
                self.parent[other] = first


def _kwjp_entry(entries):
    """F jednostki = suma F jej wpisów KWJP (każdy wiersz raz); reszta z wiersza o największym F."""
    if not entries:
        return None
    best = min(entries, key=lambda e: (-e['row_F'], e['row']))
    return {'F': sum(e['F'] for e in entries), 'ARF': best['ARF'], '1-DP': best['1-DP'],
            'genres': best['genres'], 'row': best['row']}


def _kwjp_missing(status):
    return {'status': status, 'F': None, 'ARF': None, '1-DP': None, 'genres': None, 'row': None,
            'ambiguous': False}


def units(kwjp, d5, relevant, nkjp=None, owners=None, eligible=None):
    """Jednostki rankingu wg D5 z miarami KWJP i rangą NKJP (C5, C7, C8, C14).

    `relevant` = leksemy z formą w STANDARD; jednostka ma co najmniej jednego takiego członka.
    D5: `a` — leksem z udziałem w niejednoznaczności (grupa KWJP, wspólna forma NKJP) nie dostaje F;
    `b` — F wspólne liczone każdemu kandydatowi, z flagą `ambiguous` (kopiowanie; tylko do porównania);
    `c` — tylko F jednoznaczne (wiersz EXACT, forma NKJP jednego leksemu);
    `d` — grupa homonimów: union-find po grupach AMBIGUOUS KWJP i zbiorach właścicieli form NKJP
    obserwowanych w liście; F wspólne trafia do grupy złożonej z całego zbioru właścicieli;
    `e` — jak `d`, ale łączy tylko zbiory, w których każdy właściciel należy do `eligible`
    (domyślnie `relevant`); zbiór z innym leksemem (nazwa własna, skrót) nie tworzy grupy,
    a jego F zostaje nieprzypisane jak w `c`.
    NKJP na wyjściu tylko jako status, ranga i percentyl wśród jednostek (bez F).
    """
    _option(d5, D5_OPTIONS, 'D5')
    if nkjp is not None and owners is None:
        raise ValueError('NKJP wymaga właścicieli form (form_owners)')
    relevant = frozenset(relevant)
    lexemes, groups = kwjp['lexemes'], kwjp['groups']
    in_group = defaultdict(list)
    for group in groups:
        for key in group:
            in_group[key].append(group)
    observed = []  # (właściciele, liczba) form NKJP obserwowanych w liście
    if nkjp is not None:
        observed = [(owners[key], count) for key, count in sorted(nkjp['forms'].items())]
    if eligible is not None and d5 != 'e':
        raise ValueError('eligible tylko dla D5e')
    eligible = relevant if eligible is None else relevant.intersection(eligible)
    joined = (lambda members: True) if d5 == 'd' else (lambda members: eligible.issuperset(members))
    grouped = d5 in ('d', 'e')
    if grouped:
        found = _Groups()
        for key in relevant:
            found.find(key)
        for group in groups:
            if joined(group):
                found.union(group)
        for members, _ in observed:
            if len(members) > 1 and joined(members):
                found.union(members)
        components = defaultdict(list)
        for key in list(found.parent):
            components[found.find(key)].append(key)
        unit_of = {}
        for members in components.values():
            if relevant.intersection(members):
                unit = tuple(sorted(members))
                unit_of.update((key, unit) for key in unit)
    else:
        unit_of = {key: (key,) for key in relevant}
    members_of = defaultdict(list)
    for key, unit in unit_of.items():
        members_of[unit].append(key)
    # KWJP
    kwjp_unit, copied = {}, 0
    attributed_rows = set()
    for unit, members in members_of.items():
        if grouped:
            entries = [lexemes[k] for k in members if k in lexemes]
            unit_groups = sorted({g for k in members for g in in_group.get(k, ()) if joined(g)})
            entries += [groups[g] for g in unit_groups]
            item = _kwjp_entry(entries)
            ambiguous = bool(unit_groups)
            attributed_rows.update(('lexeme', k) for k in members if k in lexemes)
            attributed_rows.update(('group', g) for g in unit_groups)
        else:
            key, = members
            mine = in_group.get(key, ())
            own = [lexemes[key]] if key in lexemes and not (d5 == 'a' and mine) else []
            extra = sorted(mine) if d5 == 'b' else []
            item = _kwjp_entry(own + [groups[g] for g in extra])
            ambiguous = bool(extra)
            attributed_rows.update(('lexeme', key) for _ in own)
            for group in extra:
                copied += groups[group]['F'] if ('group', group) in attributed_rows else 0
                attributed_rows.add(('group', group))
        if item is not None:
            kwjp_unit[unit] = {'status': 'OBSERVED', **item, 'ambiguous': ambiguous}
        else:
            known = any(k in lexemes or k in in_group for k in members)
            kwjp_unit[unit] = _kwjp_missing('UNMATCHED' if known else KWJP_ABSENT)
    kwjp_attributed = sum((lexemes if kind == 'lexeme' else groups)[key]['F'] for kind, key in attributed_rows)
    # NKJP: F jednostki tylko wewnętrznie, na wyjściu ranga i percentyl.
    nkjp_mass, shared_seen, nkjp_copied, nkjp_attributed = defaultdict(int), set(), 0, 0
    ambiguous_nkjp = set()
    if not grouped:
        if d5 == 'a':
            for members, _ in observed:
                if len(members) > 1:
                    shared_seen.update(members)
        for members, count in observed:
            if len(members) == 1:
                key = members[0]
                if key in unit_of and not (d5 == 'a' and key in shared_seen):
                    nkjp_mass[unit_of[key]] += count
                    nkjp_attributed += count
            else:
                shared_seen.update(members)
                if d5 == 'b':
                    reached = [unit_of[k] for k in members if k in unit_of]
                    for unit in reached:
                        nkjp_mass[unit] += count
                        ambiguous_nkjp.add(unit)
                    if reached:
                        nkjp_attributed += count
                        nkjp_copied += count * (len(reached) - 1)
    else:
        for members, count in observed:
            if len(members) > 1 and not joined(members):
                shared_seen.update(members)
                continue
            unit = unit_of.get(members[0])
            if unit is not None:
                nkjp_mass[unit] += count
                nkjp_attributed += count
                if len(members) > 1:
                    ambiguous_nkjp.add(unit)
    ranked = sorted(nkjp_mass, key=lambda unit: (-nkjp_mass[unit], unit))
    position = {unit: number for number, unit in enumerate(ranked, 1)}
    result = {}
    for unit in sorted(members_of):
        members = unit if grouped else tuple(sorted(members_of[unit]))
        if nkjp is None:
            nkjp_unit = {'status': 'NOT_APPLICABLE', 'rank': None, 'percentile': None, 'ambiguous': False}
        elif unit in position:
            nkjp_unit = {'status': 'OBSERVED', 'rank': position[unit],
                         'percentile': _percentile(position[unit], len(ranked)),
                         'ambiguous': unit in ambiguous_nkjp}
        else:
            nkjp_unit = {'status': 'UNMATCHED' if shared_seen.intersection(members) else NKJP_ABSENT,
                         'rank': None, 'percentile': None, 'ambiguous': False}
        k = kwjp_unit[unit]
        confidence = (('AMBIGUOUS' if k['ambiguous'] else 'EXACT') if k['status'] == 'OBSERVED'
                      else 'NKJP_ONLY' if nkjp_unit['status'] == 'OBSERVED' else None)
        result[unit] = {'members': members, 'size': len(relevant.intersection(members)), 'kwjp': k,
                        'nkjp': nkjp_unit, 'confidence': confidence}
    sizes = sorted((len(u['members']) for u in result.values()), reverse=True)
    mass = {'kwjp': {'total': kwjp['mass']['total'], 'attributed': kwjp_attributed, 'copied': copied,
                     'unattributed': kwjp['mass']['total'] - kwjp_attributed}}
    if nkjp is not None:
        mass['nkjp'] = {'total': nkjp['total'], 'matched': nkjp['matched'], 'attributed': nkjp_attributed,
                        'copied': nkjp_copied, 'unattributed': nkjp['matched'] - nkjp_attributed}
    return {'option': d5, 'units': result, 'mass': mass,
            'groups': {'count': sum(1 for size in sizes if size > 1), 'largest': sizes[0] if sizes else None}}


def _kwjp_value(item, field):
    if item['status'] != 'OBSERVED':
        return None
    if field == 'genres':
        return len(item['genres'])
    return item['F'] if field == 'F' else float(item[field])


def _missing(found, result, partial):
    pairs = defaultdict(int)
    for unit in result['units'].values():
        pairs[f"{unit['kwjp']['status']}/{unit['nkjp']['status']}"] += 1
    return {'full': sum(1 for v in found.values() if v['status'] == 'NO_DATA'), 'partial': partial,
            'statuses': dict(sorted(pairs.items()))}


def measure(result, d3, d8='available-only'):
    """Miara jednostki wg D3; brak częściowy wg D8b. Wynik: wartość, status, flagi (C5, C6).

    `kwjp`: sama KWJP, pole F / ARF / 1-DP / liczba gatunków z obecnością.
    `kwjp+nkjp`: tylko z percentyli, `weight × KWJP + (1 − weight) × NKJP`. Brak częściowy:
    `available-only` — percentyl dostępnego źródła; `lower-bound` — brakujące źródło tuż pod ostatnią
    obserwowaną rangą, z flagą; `exclude` — jednostka bez wartości. Brak pełny = `NO_DATA`.
    """
    _exact(d3, {'source', 'field'} | ({'weight'} if d3.get('source') == 'kwjp+nkjp' else set())
           if isinstance(d3, dict) else set(), 'D3')
    source = _option(d3['source'], D3_SOURCES, 'D3 source')
    field = _option(d3['field'], D3_FIELDS, 'D3 field')
    _option(d8, D8_PARTIAL, 'D8b')
    found = {}
    if source == 'kwjp':
        for key, unit in result['units'].items():
            value = _kwjp_value(unit['kwjp'], field)
            found[key] = ({'value': value, 'status': 'MEASURED',
                           'flags': ('ambiguous',) if unit['kwjp']['ambiguous'] else ()}
                          if value is not None else {'value': None, 'status': 'NO_DATA', 'flags': ()})
        return {'units': found, 'missing': _missing(found, result, None)}
    weight = _number(d3['weight'], 0, 1, 'D3 weight')
    kwjp_pct = percentiles(rank_units({k: {'value': _kwjp_value(u['kwjp'], field)}
                                       for k, u in result['units'].items()}))
    nkjp_count = sum(1 for u in result['units'].values() if u['nkjp']['status'] == 'OBSERVED')
    floors = {'kwjp': _percentile(len(kwjp_pct) + 1, len(kwjp_pct) + 1),
              'nkjp': _percentile(nkjp_count + 1, nkjp_count + 1)}
    partial = 0
    for key, unit in result['units'].items():
        values = {'kwjp': kwjp_pct.get(key), 'nkjp': unit['nkjp']['percentile']}
        missing = [name for name, value in values.items() if value is None]
        if len(missing) == 2:
            found[key] = {'value': None, 'status': 'NO_DATA', 'flags': ()}
            continue
        if missing:
            partial += 1
            gone, = missing
            if d8 == 'exclude':
                found[key] = {'value': None, 'status': 'EXCLUDED_PARTIAL', 'flags': ()}
                continue
            if d8 == 'available-only':
                kept = 'nkjp' if gone == 'kwjp' else 'kwjp'
                found[key] = {'value': values[kept], 'status': 'MEASURED', 'flags': (f'single_source:{kept}',)}
                continue
            values[gone] = floors[gone]
        value = round(weight * values['kwjp'] + (1 - weight) * values['nkjp'], 6)
        found[key] = {'value': value, 'status': 'MEASURED', 'flags': (f'lower_bound:{missing[0]}',) if missing else ()}
    return {'units': found, 'missing': _missing(found, result, partial)}


def rank_units(measured):
    """Ranga od 1 wg `(-wartość, klucz jednostki)`; jednostki bez wartości nie mają rangi (nie 0)."""
    ranked = sorted((key for key, item in measured.items() if item['value'] is not None),
                    key=lambda key: (-measured[key]['value'], key))
    return {key: number for number, key in enumerate(ranked, 1)}


def percentiles(ranks):
    """Percentyl rangi: 100 dla pierwszej, `100 / n` dla ostatniej."""
    return {key: _percentile(rank, len(ranks)) for key, rank in ranks.items()}


def member_ranks(ranks, result):
    """Ranga każdego leksemu = ranga jego jednostki (grupa dzieli rangę, nie F)."""
    return {member: rank for key, rank in ranks.items() for member in result['units'][key]['members']}


def _coverage_parts(kwjp, d1, relevant):
    """Mianownik D1 i masy wpisów KWJP, które może pokryć wybór leksemów."""
    _option(d1, D1_OPTIONS, 'D1')
    lexemes, groups = kwjp['lexemes'], kwjp['groups']
    if d1 == 'kwjp-standard':
        if relevant is None:
            raise ValueError('D1 kwjp-standard wymaga leksemów z formą w STANDARD')
        lexeme_mass = {k: v['F'] for k, v in lexemes.items() if k in relevant}
        group_mass = {g: v['F'] for g, v in groups.items() if relevant.intersection(g)}
        total = sum(lexeme_mass.values()) + sum(group_mass.values())
    else:
        lexeme_mass = {k: v['F'] for k, v in lexemes.items()}
        group_mass = {} if d1 == 'kwjp-exact' else {g: v['F'] for g, v in groups.items()}
        total = kwjp['mass']['total' if d1 == 'kwjp-all' else 'EXACT_CANDIDATE']
    return total, lexeme_mass, group_mass


def _coverage(d1, covered, total):
    return {'denominator': d1, 'covered': covered, 'total': total,
            'coverage': round(covered / total, 6) if total else None}


def coverage(members, kwjp, d1, relevant=None):
    """Pokrycie masy KWJP wybranymi leksemami w mianowniku D1.

    Wiersz EXACT pokryty, gdy jego leksem jest wybrany; wiersz AMBIGUOUS — gdy wybrani są wszyscy
    kandydaci (dolna granica). `kwjp-all`: wszystkie tokeny listy; `kwjp-exact`: masa EXACT;
    `kwjp-standard`: masa leksemów z formą w STANDARD (wiersze EXACT i grupy z takim leksemem).
    """
    total, lexeme_mass, group_mass = _coverage_parts(kwjp, d1, None if relevant is None else frozenset(relevant))
    members = set(members)
    covered = (sum(m for k, m in lexeme_mass.items() if k in members)
               + sum(m for g, m in group_mass.items() if members.issuperset(g)))
    return _coverage(d1, covered, total)


def threshold(ranks, result, d6, kwjp=None, relevant=None):
    """Próg D6 jako prefiks rang: jednostka wchodzi w całości albo wcale.

    `count`: jednostki po kolei, dopóki suma leksemów (członków z formą w STANDARD) ≤ wartość.
    `coverage`: do pierwszej jednostki, po której pokrycie w mianowniku D1 ≥ wartość.
    """
    if not isinstance(d6, dict):
        raise GeneratorError('D6 musi być obiektem', 2)
    by = _option(d6.get('by'), D6_BY, 'D6')
    _exact(d6, {'by', 'value'} | ({'denominator'} if by == 'coverage' else set()), 'D6')
    if by == 'count':
        limit = _number(d6['value'], 0, 10 ** 7, 'D6 count', integer=True, low_open=True)
    else:
        limit = _number(d6['value'], 0, 1, 'D6 coverage', low_open=True)
        if kwjp is None:
            raise ValueError('Próg pokrycia wymaga miar KWJP')
        total, lexeme_mass, group_mass = _coverage_parts(
            kwjp, d6['denominator'], None if relevant is None else frozenset(relevant))
        remaining = {g: len(g) for g in group_mass}
        groups_of = defaultdict(list)
        for group in group_mass:
            for key in group:
                groups_of[key].append(group)
    chosen, members, size, covered, reached = [], set(), 0, 0, False
    for key in sorted(ranks, key=lambda k: ranks[k]):
        unit = result['units'][key]
        if by == 'count':
            if size + unit['size'] > limit:
                reached = True
                break
        chosen.append(key)
        size += unit['size']
        for member in unit['members']:
            if member in members:
                continue
            members.add(member)
            if by == 'coverage':
                covered += lexeme_mass.get(member, 0)
                for group in groups_of.get(member, ()):
                    remaining[group] -= 1
                    if not remaining[group]:
                        covered += group_mass[group]
        if by == 'count' and size == limit:
            reached = True
            break
        if by == 'coverage' and total and covered / total >= limit:
            reached = True
            break
    found = {'units': tuple(chosen), 'members': frozenset(members), 'lexemes': size,
             'rank': ranks[chosen[-1]] if chosen else None, 'reached': reached}
    if by == 'coverage':
        found['coverage'] = _coverage(d6['denominator'], covered, total)
    return found


def tag_classes(tag):
    """Klasy D2a etykiety: wołacz (sam `voc`), rozkaźnik, imiesłowy, os. 1/2; pusta = poza klasami."""
    fields = tag.split(':')
    found = set()
    if fields[0] == 'impt':
        found.add('impt')
    if fields[0] in PARTICIPLES:
        found.add('participle')
    if 'voc' in fields[1:]:
        found.add('voc')
    if 'pri' in fields[1:] or 'sec' in fields[1:]:
        found.add('person-1-2')
    return frozenset(found)


def load_form_classes(db, standard, lexemes=None):
    """Leksem → forma STANDARD → zbiór klas jej analiz, tylko gdy każda analiza ma klasę D2a.

    Forma z choć jedną analizą poza klasami zawsze zostaje, więc nie trafia do mapy.
    Dwa przebiegi `interpretation`, żeby nie trzymać wszystkich par (leksem, forma).
    """
    keys, surface = _keys(db, lexemes), _standard_surface(db, standard)
    cache = {}
    classed = defaultdict(lambda: defaultdict(set))
    for lexeme_id, form_id, tag in db.execute('select lexeme_id,form_id,tag from interpretation'):
        key = surface.get(form_id)
        if key is None:
            continue
        found = cache.get(tag)
        if found is None:
            found = cache[tag] = tag_classes(tag)
        if found:
            classed[keys[lexeme_id]][key].add(found)
    for lexeme_id, form_id, tag in db.execute('select lexeme_id,form_id,tag from interpretation'):
        key = surface.get(form_id)
        if key is not None and not cache[tag]:
            forms = classed.get(keys[lexeme_id])
            if forms is not None:
                forms.pop(key, None)
    return {lexeme: {form: frozenset(sets) for form, sets in sorted(forms.items())}
            for lexeme, forms in sorted(classed.items()) if forms}


def forms_for(members, d2, forms, constructions=None, classes=None):
    """Formy jednostki wg D2: reguła przynależności (i)/(ii), klasy znaczników, konstrukcje tak/nie.

    `forms` = reguła → wynik `load_forms` / `load_forms_accepted`. Forma odpada, gdy każda jej analiza
    w danym leksemie ma klasę wykluczoną; zostaje, gdy inny członek ją zachowuje. Forma konstrukcji
    wchodzi z leksemem składnika (C9) i nie ma etykiety, więc klasy jej nie dotyczą.
    """
    if not isinstance(d2, dict):
        raise GeneratorError('D2 musi być obiektem', 2)
    _exact(d2, {'classes', 'constructions', 'membership'}, 'D2')
    excluded = d2['classes']
    if not isinstance(excluded, (tuple, list)) or len(set(excluded)) != len(excluded):
        raise GeneratorError('D2 classes musi być listą bez powtórzeń', 2)
    for name in excluded:
        _option(name, D2_CLASSES, 'D2 class')
    _option(d2['constructions'], D2_CONSTRUCTIONS, 'D2 constructions')
    rule = _option(d2['membership'], D2_MEMBERSHIP, 'D2 membership')
    if rule not in forms:
        raise ValueError(f'Brak form reguły {rule}')
    if excluded and classes is None:
        raise ValueError('Wykluczenie klas wymaga load_form_classes')
    if d2['constructions'] == 'yes' and constructions is None:
        raise ValueError('Konstrukcje wymagają load_constructions')
    excluded = frozenset(excluded)
    kept, dropped = set(), defaultdict(set)
    for member in members:
        mine = (classes or {}).get(member, {})
        for form in forms[rule].get(member, ()):
            sets = mine.get(form) if excluded else None
            if sets and all(found & excluded for found in sets):
                for name in frozenset().union(*sets) & excluded:
                    dropped[name].add(form)
            else:
                kept.add(form)
    added = set()
    if d2['constructions'] == 'yes':
        for member in members:
            added.update(constructions['forms'].get(member, ()))
    result = frozenset(kept | added)
    return {'forms': result, 'constructions': len(added - kept),
            'removed': {name: len(found - result) for name, found in sorted(dropped.items())
                        if found - result}}


def spearman(ranks_a, ranks_b):
    """Spearman na wspólnych jednostkach (rangi przeliczone w części wspólnej); n < 2 → `None`."""
    common = set(ranks_a) & set(ranks_b)
    n = len(common)
    if n < 2:
        return {'n': n, 'rho': None}
    order = lambda ranks: {k: i for i, k in enumerate(sorted(common, key=lambda k: (ranks[k], k)), 1)}
    first, second = order(ranks_a), order(ranks_b)
    squared = sum((first[k] - second[k]) ** 2 for k in common)
    return {'n': n, 'rho': round(1 - 6 * squared / (n * (n * n - 1)), 6)}


def top_overlap(ranks_a, ranks_b, n):
    """Część wspólna top-N obu rankingów."""
    _number(n, 0, 10 ** 7, 'top-N', integer=True, low_open=True)
    top = lambda ranks: {k for k, r in ranks.items() if r <= n}
    overlap = len(top(ranks_a) & top(ranks_b))
    return {'n': n, 'overlap': overlap, 'share': round(overlap / n, 6)}


# --- Konfiguracja metody `pop-v1` (B3, C3, ADR-007) ---
# `config/generator/pop.json` zapisuje decyzje D1–D9. Każde naruszenie schematu = kod 2.
# Schemat zna wszystkie opcje pomiaru; `load_config` przyjmuje tylko wartości ADR-007 (C3).
# Jedyny wyjątek: wycofanie NKJP (ADR-006) = `d3 = {source: kwjp, field: F}` i `d4 = null`.
# `must_include_pop0`: słowa, których brak w POP0 zatrzymuje polecenie `pop` (kod 4).

METHODS = {'pop-v1': 'docs/adr/ADR-007-metoda-pop-v1.md'}
CONFIG_KEYS = {'version', 'adr', 'd1', 'd2', 'd3', 'd4', 'd5', 'd6', 'd7', 'd8', 'proper_names_in_ranking',
               'must_include_pop0', 'sampling'}
# D5 w konfiguracji: opcje `units` plus `e-common` = `e` z `eligible` = leksemy bez nazw własnych.
D5_CONFIG = D5_OPTIONS + ('e-common',)
D7_OPTIONS = ('accepted',)
SAMPLING_VERSION = 'pop-quality-v1'
D6_MAX = 10 ** 7
# Wartości ADR-007 (C3). D3 i D4 idą parami: KWJP+NKJP z regułą D4 albo sama KWJP bez D4.
ADR_007 = {'d1': 'kwjp-standard', 'd2': {'classes': [], 'constructions': 'yes', 'membership': 'i'},
           'd5': 'e-common', 'd7': 'accepted', 'd8': 'available-only', 'proper_names_in_ranking': False}
ADR_007_D3_D4 = (({'source': 'kwjp+nkjp', 'field': 'F', 'weight': 0.5}, 'strip-edges-keep-dot'),
                 ({'source': 'kwjp', 'field': 'F'}, None))


def _config_d2(d2):
    _exact(d2, {'classes', 'constructions', 'membership'}, 'D2')
    classes = d2['classes']
    if not isinstance(classes, list) or len(set(map(str, classes))) != len(classes):
        raise GeneratorError('D2 classes musi być listą bez powtórzeń', 2)
    for name in classes:
        _option(name, D2_CLASSES, 'D2 class')
    _option(d2['constructions'], D2_CONSTRUCTIONS, 'D2 constructions')
    _option(d2['membership'], D2_MEMBERSHIP, 'D2 membership')


def _config_d3_d4(d3, d4):
    source = d3.get('source') if isinstance(d3, dict) else None
    _exact(d3, {'source', 'field'} | ({'weight'} if source == 'kwjp+nkjp' else set()), 'D3')
    _option(source, D3_SOURCES, 'D3 source')
    _option(d3['field'], D3_FIELDS, 'D3 field')
    if source == 'kwjp+nkjp':
        _number(d3['weight'], 0, 1, 'D3 weight', low_open=True)
    if d4 is not None or source == 'kwjp+nkjp':
        _option(d4, CLEANING_RULES, 'D4')


def _config_d6(d6):
    _exact(d6, {'pop', 'pop0'}, 'D6')
    limits = {}
    for name in ('pop', 'pop0'):
        item = d6[name]
        by = _option(item.get('by') if isinstance(item, dict) else None, D6_BY, f'D6 {name}')
        _exact(item, {'by', 'value'} | ({'denominator'} if by == 'coverage' else set()), f'D6 {name}')
        if by == 'count':
            limits[name] = _number(item['value'], 0, D6_MAX, f'D6 {name}', integer=True, low_open=True)
        else:
            _option(item['denominator'], D1_OPTIONS, f'D6 {name} denominator')
            limits[name] = _number(item['value'], 0, 1, f'D6 {name}', low_open=True)
    if (d6['pop']['by'] != d6['pop0']['by'] or d6['pop'].get('denominator') != d6['pop0'].get('denominator')
            or not limits['pop0'] < limits['pop']):
        raise GeneratorError('D6: POP0 musi być mniejsze od POP w tej samej mierze', 2)


def _validate_config(config):
    from .quality import _config as sampling_config
    _exact(config, CONFIG_KEYS, 'pop.json')
    version = _option(config['version'], METHODS, 'wersja metody')
    if config['adr'] != METHODS[version]:
        raise GeneratorError(f'pop.json: adr musi wskazywać {METHODS[version]}', 2)
    _option(config['d1'], D1_OPTIONS, 'D1')
    _config_d2(config['d2'])
    _config_d3_d4(config['d3'], config['d4'])
    _option(config['d5'], D5_CONFIG, 'D5')
    _config_d6(config['d6'])
    _option(config['d7'], D7_OPTIONS, 'D7')
    _option(config['d8'], D8_PARTIAL, 'D8b')
    if type(config['proper_names_in_ranking']) is not bool:
        raise GeneratorError('D9: proper_names_in_ranking musi być true albo false', 2)
    words = config['must_include_pop0']
    if (not isinstance(words, list) or not words or not all(_text(w) for w in words)
            or len(set(words)) != len(words)):
        raise GeneratorError('must_include_pop0: niepusta lista słów bez powtórzeń', 2)
    sampling = config['sampling']
    if not isinstance(sampling, dict) or sampling.get('version') != SAMPLING_VERSION:
        raise GeneratorError(f'pop.json: sampling musi być {SAMPLING_VERSION}', 2)
    sampling_config(sampling)
    _adr_007(config)


def _adr_007(config):
    """Zawężenie do metody `pop-v1` (C3): inna wartość niż w ADR-007 = kod 2."""
    for key, value in ADR_007.items():
        if config[key] != value or type(config[key]) is not type(value):
            raise GeneratorError(f'pop.json: {key} spoza ADR-007 (oczekiwane {value!r})', 2)
    if not any(config['d3'] == d3 and config['d4'] == d4 for d3, d4 in ADR_007_D3_D4):
        raise GeneratorError('pop.json: d3/d4 spoza ADR-007 (KWJP+NKJP F 0,5 z D4 albo sama KWJP F bez D4)', 2)
    if any(config['d6'][name]['by'] != 'count' for name in ('pop', 'pop0')):
        raise GeneratorError('pop.json: d6 tylko jako liczba leksemów (ADR-007)', 2)


def load_config(path):
    """Wczytaj i ściśle sprawdź `pop.json` (metoda `pop-v1`, ADR-007); błąd schematu = kod 2."""
    path = Path(path).resolve()
    try:
        config = load_json(path)
    except (OSError, ValueError) as error:
        raise GeneratorError(f'Nie można wczytać pop.json: {error}', 2, str(path)) from error
    _validate_config(config)
    return {**config, 'config_path': str(path), 'config_sha256': sha256(path)}


# --- Polecenie `pop`: listy POP i POP0 w pamięci (C1–C10, C14, C19) ---
# Złożenie jak w `scripts/measure_pop.py` (D5 `e-common`); funkcje rankingu wyżej bez zmian (D-6).
# Ranking tylko z jednostek, w których jest zwykły leksem (D9). Zapis pakietu: grupa 12.

LISTS = ('pop0', 'pop')
REPORT_DENOMINATORS = ('kwjp-standard', 'kwjp-all')
POS_CLASSES = (('subst', {'subst', 'depr'}),
               ('verb', {'fin', 'praet', 'inf', 'impt', 'imps', 'pcon', 'pant', 'pact', 'ppas', 'ger', 'bedzie',
                         'winien'}),
               ('adj', {'adj', 'adja', 'adjp', 'adjc'}),
               ('adv', {'adv'}))


def _lexicon(paths, sources, with_nkjp):
    """Dane z bazy tylko do odczytu: KWJP, formy reguły (i), konstrukcje, nazwy własne, właściciele form."""
    from .database import connect
    standard = read_standard(paths['standard'])
    with connect(paths['database'], readonly=True) as db:
        lexemes = load_lexemes(db)
        rows, genres = load_kwjp_lists(db, _input(sources, 'kwjp')['lemma_sources'], lexemes)
        owners = form_owners(db, lexemes) if with_nkjp else None
        forms = load_forms(db, standard, lexemes)
        constructions = load_constructions(db, standard, lexemes)
    proper = frozenset(item['key'] for item in lexemes.values() if item['proper'])
    pos = {item['key']: _pos_class(item['pos']) for item in lexemes.values()}
    return {'standard': standard, 'kwjp': kwjp_measures(rows, genres), 'owners': owners, 'forms': forms,
            'constructions': constructions, 'proper': proper, 'relevant': frozenset(forms), 'pos': pos}


def _pos_class(tags):
    """Klasa części mowy leksemu do warstw próbek (wzór `scripts/measure_pop.py`)."""
    tags = set(tags)
    return next((name for name, group in POS_CLASSES if tags & group), 'other')


def _base_attributions(paths):
    """`ATTRIBUTIONS.md` pakietu LL-PL sprawdzone hashem z jego release-manifestu, bez sekcji NKJP."""
    release = Path(paths['release_dir'])
    files = load_json(paths['release_manifest']).get('files') or {}
    pinned = (files.get('ATTRIBUTIONS.md') or {}).get('sha256')
    if not pinned:
        raise GeneratorError('Pakiet LL-PL bez ATTRIBUTIONS.md w release-manifest', 3, str(release))
    text = checked_file(release, {'path': 'ATTRIBUTIONS.md', 'sha256': pinned}).read_text(encoding='utf-8')
    return _demote_without_nkjp(text)


def _demote_without_nkjp(text):
    """Nagłówki o dwa poziomy niżej; sekcje z NKJP w nagłówku pomijane (NKJP opisuje własna sekcja, C19)."""
    lines, fence, skip = [], False, None
    for line in text.splitlines():
        heading = 0
        if line.startswith('```'):
            fence = not fence
        elif not fence and line.startswith('#') and line.lstrip('#').startswith(' '):
            heading = len(line) - len(line.lstrip('#'))
            if skip is not None and heading <= skip:
                skip = None
            if skip is None and 'nkjp' in line.lower():
                skip = heading
        if skip is None:
            lines.append('##' + line if heading else line)
    return '\n'.join(lines).strip('\n')


def _unit_row(key, unit, found, rank, kwjp_pct, place):
    row = {'unit': key, 'size': unit['size'], 'rank': rank, 'value': found['value'], 'status': found['status'],
           'flags': list(found['flags']), 'confidence': unit['confidence'], 'list': place,
           'kwjp': {'status': unit['kwjp']['status'], 'percentile': kwjp_pct.get(key),
                    'ambiguous': unit['kwjp']['ambiguous']}}
    if unit['nkjp']['status'] != 'NOT_APPLICABLE':
        row['nkjp'] = {k: unit['nkjp'][k] for k in ('status', 'rank', 'percentile', 'ambiguous')}
    return row


def build_pop(sources, config, run_dir=None, release_dir=None):
    """Listy POP i POP0 wg `pop.json` (ADR-007), bez zapisu. Kody: 2 konfiguracja, 3 piny, 4 kontrola list,
    5 przebieg nie FROZEN albo baza zmieniona w trakcie.

    Wynik: posortowane klucze POP i POP0, wiersze jednostek (ranga, miara, percentyle, statusy, flagi,
    lista), raport progów. NKJP tylko jako status, ranga i percentyl (C14); przy samej KWJP bez NKJP (C19).
    """
    config = load_config(config)
    sources = load_sources(sources)
    paths = check_inputs(sources, run_dir, release_dir)
    with_nkjp = config['d3']['source'] == 'kwjp+nkjp'
    data = _lexicon(paths, sources, with_nkjp)
    kwjp, relevant, proper = data['kwjp'], data['relevant'], data['proper']
    nkjp = read_nkjp(paths['nkjp'], config['d4'], data['owners']) if with_nkjp else None
    result = units(kwjp, 'e', relevant, nkjp, data['owners'], eligible=relevant - proper)
    rule_id = nkjp['rule_id'] if with_nkjp else None
    del nkjp, data['owners']
    # D9: jednostka z samych nazw własnych nie ma rangi i nie liczy się do progu.
    proper_units = sum(1 for unit in result['units'].values() if proper.issuperset(unit['members']))
    result['units'] = {k: u for k, u in result['units'].items() if not proper.issuperset(u['members'])}
    found = measure(result, config['d3'], config['d8'])
    ranks = rank_units(found['units'])
    cuts = {name: threshold(ranks, result, config['d6'][name], kwjp, relevant) for name in LISTS}
    lists = {name: forms_for(cuts[name]['members'], config['d2'], {'i': data['forms']}, data['constructions'])
             for name in LISTS}
    pop, pop0 = lists['pop']['forms'], lists['pop0']['forms']
    included, ranked_members = {}, member_ranks(ranks, result)
    for word in config['must_include_pop0']:
        key = _game_key(word)
        if key not in pop0:
            raise GeneratorError(f'Słowo z must_include_pop0 poza POP0: {word}', 4)
        owners = [m for m in cuts['pop0']['members'] if key in data['forms'].get(m, ())
                  or key in data['constructions']['forms'].get(m, ())]
        included[word] = min(ranked_members[m] for m in owners)
    if not (pop0 <= pop <= data['standard']):
        raise GeneratorError('Naruszone POP0 ⊆ POP ⊆ STANDARD', 4)
    after = database_sha256(paths['database'])
    if after != paths['database_sha256']:
        raise GeneratorError('Baza zmieniła się w trakcie pop', 5, paths['database'])
    place = {}
    for name in ('pop', 'pop0'):
        place.update((unit, name.upper()) for unit in cuts[name]['units'])
    kwjp_pct = percentiles(rank_units({k: {'value': _kwjp_value(u['kwjp'], 'F')} for k, u in result['units'].items()}))
    rows = [_unit_row(key, unit, found['units'][key], ranks.get(key), kwjp_pct, place.get(key))
            for key, unit in result['units'].items()]
    rows.sort(key=lambda r: (r['rank'] is None, r['rank'] or 0, r['unit']))
    thresholds = {name: {'limit': config['d6'][name]['value'], 'rank': cuts[name]['rank'],
                         'units': len(cuts[name]['units']), 'lexemes': cuts[name]['lexemes'],
                         'reached': cuts[name]['reached'], 'forms': len(lists[name]['forms']),
                         'construction_forms': lists[name]['constructions'],
                         'coverage': {d1: coverage(cuts[name]['members'], kwjp, d1, relevant)
                                      for d1 in REPORT_DENOMINATORS}}
                  for name in LISTS}
    missing = found['missing']
    if not with_nkjp:
        statuses = defaultdict(int)
        for unit in result['units'].values():
            statuses[unit['kwjp']['status']] += 1
        missing = {**missing, 'statuses': dict(sorted(statuses.items()))}
    inputs = {'database_sha256': paths['database_sha256'], 'release_manifest_sha256': paths['release_manifest_sha256'],
              'standard_sha256': paths['standard_sha256'], 'sources_sha256': sources['manifest_sha256']}
    answer = {'method': config['version'], 'adr': config['adr'], 'config_sha256': config['config_sha256'],
              'database_sha256': after, 'inputs': inputs, 'pop': sorted(pop), 'pop0': sorted(pop0),
              'units': rows, 'thresholds': thresholds, 'missing': missing, 'mass': result['mass'],
              'groups': result['groups'], 'proper_units': proper_units, 'must_include_pop0': included}
    # Dane tylko do zapisu pakietu (grupa 12): próbki, atrybucje, klasy POS członków POP.
    package = {'sampling': config['sampling'], 'base_package_id': sources['base']['package_id'],
               'base_attributions': _base_attributions(paths),
               'pos': {_label(m): data['pos'][m] for m in sorted(cuts['pop']['members'])}}
    answer['package'] = package
    if with_nkjp:
        inputs['nkjp_sha256'] = paths['nkjp_sha256']
        answer['nkjp_rule_id'] = rule_id
        package['nkjp'] = {k: v for k, v in _input(sources, 'nkjp_1gram').items() if k != 'path'}
    return answer


def pop_summary(result):
    """Podsumowanie wyniku `build_pop` dla CLI: bez list i wierszy jednostek."""
    keep = ('method', 'config_sha256', 'database_sha256', 'nkjp_rule_id', 'thresholds', 'missing', 'groups',
            'proper_units', 'must_include_pop0')
    summary = {key: result[key] for key in keep if key in result}
    summary['units'] = len(result['units'])
    summary['ranked'] = sum(1 for row in result['units'] if row['rank'] is not None)
    return summary


# --- Pakiet POP `BUILT` (C11–C13, C17, C18, C19) ---
# Zapis do stagingu obok celu, potem `export.rename_noreplace`; pliki 0444. Bez czasów i ścieżek
# bezwzględnych, więc dwa przebiegi z tych samych wejść dają te same bajty (D-1).
# NKJP w raportach tylko pod kluczami `NKJP_REPORT_KEYS` (C14); bez NKJP (C19) nie ma ich wcale.

PACKAGE_ID = 'POP'
NKJP_REPORT_KEYS = ('nkjp_rank', 'nkjp_percentile', 'nkjp_status')
SAMPLE_WINDOW = 500  # jednostek po każdej stronie granicy (jak w pomiarze A)
SHORT_FORM, LONG_FORM = 3, 12
DIVERGENCE = 50  # różnica percentyli KWJP i NKJP w warstwie rozbieżności
LIST_FILES = {'pop': 'POP.txt.gz', 'pop0': 'POP0.txt.gz'}
CC_BY_4 = 'https://creativecommons.org/licenses/by/4.0/'


def _label(key):
    """Klucz leksemu jako napis: `lemma_id@source_id` (wzór `scripts/measure_pop.py`)."""
    return f'{key[1]}@{key[0]}'


def _write_gzip(path, keys):
    """Lista `game_key`, po jednym w wierszu; gzip bez nazwy i czasu, poziom 9 (C11)."""
    data = ''.join(key + '\n' for key in keys).encode('utf-8')
    with open(path, 'wb') as raw, gzip.GzipFile(filename='', mode='wb', fileobj=raw, mtime=0,
                                                compresslevel=9) as stream:
        stream.write(data)


def _package_row(row):
    """Wiersz `reports/units.json`: ranga, miara, percentyle, statusy, flagi; NKJP bez F (C14)."""
    out = {'members': [_label(m) for m in row['unit']], 'size': row['size'], 'rank': row['rank'],
           'value': row['value'], 'status': row['status'], 'flags': list(row['flags']),
           'confidence': row['confidence'], 'list': row['list'], 'kwjp_status': row['kwjp']['status'],
           'kwjp_percentile': row['kwjp']['percentile'], 'kwjp_ambiguous': row['kwjp']['ambiguous']}
    if 'nkjp' in row:
        nkjp = row['nkjp']
        out.update(zip(NKJP_REPORT_KEYS, (nkjp['rank'], nkjp['percentile'], nkjp['status'])))
        if nkjp['ambiguous']:
            out['flags'].append('ambiguous:nkjp')
    return out


def _strata(result, rows):
    """Warstwy `pop-quality-v1` (C17); klucze to leksemy (`lemma_id@source_id`) albo formy."""
    ranked = [row for row in rows if row['rank'] is not None]  # wiersze są w kolejności rang

    def members(selected):
        return sorted({m for row in selected for m in row['members']})

    strata = {}
    for name in LISTS:
        position = result['thresholds'][name]['units']
        strata[f'{name}-granica-wewnatrz'] = members(ranked[max(0, position - SAMPLE_WINDOW):position])
        strata[f'{name}-granica-zewnatrz'] = members(ranked[position:position + SAMPLE_WINDOW])
    strata['braki-danych'] = members(row for row in rows if row['status'] != 'MEASURED'
                                     or any(f.startswith('single_source:') for f in row['flags']))
    # Bez NKJP warstwa jest pusta i zostaje jawnie (`EMPTY_NOT_COVERAGE`).
    strata['rozbieznosc-korpusow'] = members(
        row for row in rows if row['kwjp_percentile'] is not None and row.get('nkjp_percentile') is not None
        and abs(row['kwjp_percentile'] - row['nkjp_percentile']) >= DIVERGENCE)
    strata['grupy-homonimow'] = members(row for row in rows if len(row['members']) > 1)
    for member, pos in result['package']['pos'].items():
        strata.setdefault(f'pos-{pos}', []).append(member)
    strata['formy-krotkie'] = [form for form in result['pop'] if len(form) <= SHORT_FORM]
    strata['formy-dlugie'] = [form for form in result['pop'] if len(form) >= LONG_FORM]
    return {name: sorted(keys) for name, keys in strata.items()}


def _attributions(result):
    package = result['package']
    lines = ['# Atrybucje pakietu POP', '',
             f'Listy POP i POP0 (metoda {result["method"]}, {result["adr"]}) to podzbiory listy STANDARD pakietu '
             f'{package["base_package_id"]} (release-manifest SHA256 `{result["inputs"]["release_manifest_sha256"]}`). '
             'Formy pochodzą z SGJP, wybór miarą z KWJP' + (' i NKJP.' if 'nkjp' in package else '.'),
             'Pakiet nie przypisuje projektowi praw do materiałów zewnętrznych.', '']
    nkjp = package.get('nkjp')
    if nkjp:
        lines += [f'## NKJP — {nkjp["title"]}', '',
                  f'- zasób: {nkjp["title"]}, plik 1-gramów (SHA256 `{nkjp["sha256"]}`)',
                  f'- adres: {nkjp["url"]}',
                  f'- twórca i udostępniający: {nkjp["creator"]}',
                  f'- licencja: {nkjp["license"]}. Spełniamy wymagania wszystkich wersji CC BY 1.0–4.0; '
                  f'tekst wersji 4.0: {CC_BY_4}',
                  '- prawa i gwarancja: udostępniający nie podał informacji o prawach autorskich '
                  'ani wyłączenia gwarancji.',
                  '- zmiany: z formy zdejmujemy interpunkcję tylko z brzegów tokenu i zostawiamy kropkę, '
                  'więc skróty (np. `ul.`) nie łączą się ze słowami (`ul`); '
                  f'reguła `{result["nkjp_rule_id"]}`. '
                  'Zliczenia łączymy z formami SGJP i przeliczamy na rangi i percentyle. '
                  'Pakiet nie zawiera surowego pliku ani zliczeń NKJP.',
                  f'- użycie: {nkjp["used_for"]}',
                  '- Autorzy NKJP i IPI PAN nie popierają tego projektu ani jego wyników. '
                  'Decyzja: ADR-006 (`docs/adr/ADR-006-nkjp-cc-by-bez-wersji.md`).', '']
    lines += [f'## Podstawa: atrybucje pakietu {package["base_package_id"]}', '', package['base_attributions'], '']
    return '\n'.join(lines).rstrip('\n') + '\n'


def _limitations(result):
    with_nkjp = 'nkjp_rule_id' in result
    corpora = 'KWJP i NKJP' if with_nkjp else 'KWJP'
    lines = ['# Ograniczenia pakietu POP', '',
             '- Status `BUILT`: pakiet nie jest wydaniem. Wydanie wymaga przeglądu próbek `pop-quality-v1` '
             '(`reports/sample.json`) ze statusem `REVIEWED`.',
             f'- POP0 ⊆ POP ⊆ STANDARD pakietu {result["package"]["base_package_id"]}, nie ⊆ SJP.pl. '
             'Serwer gry gra dziś na SJP.pl: bot z POP przy stole SJP może zagrać słowo, którego SJP.pl nie ma. '
             'Integracja z grą to osobna praca.',
             f'- Miara to częstość w tekstach ({corpora}), nie znajomość słowa przez ludzi. '
             'Ludzie oceniają tylko próbki, nie całą listę.',
             '- Pełna odmiana: leksem z POP wnosi każdą swoją formę ze STANDARD, także rzadkie '
             '(wołacz, imiesłowy).',
             '- Grupy homonimów `e-common` łączą też zwykłe homonimy (np. `nie`, `on`, `jeść`). '
             'Grupa wchodzi w całości albo wcale; jej F nie jest dzielone ani kopiowane.',
             f'- Luka potoczna (D7): miara pochodzi z tekstów pisanych ({corpora}). '
             'Nie ma listy mowy potocznej ani slangu internetowego.',
             '- Nazwy własne poza rankingiem (D9): ich formy wchodzą tylko przez zwykły leksem o tej samej formie.',
             '- KWJP dzieli formy przeszłe (`zrobił`+`em`). Brak w źródle to brak danych, nie zero: '
             'status per źródło, nigdy ranga 0. Brak pełny = poza listami; częściowy = flaga `single_source`.']
    if with_nkjp:
        lines += [f'- NKJP: zrównoważony podkorpus, starszy od KWJP; reguła czyszczenia `{result["nkjp_rule_id"]}`. '
                  'Pakiet podaje NKJP tylko jako rangę, percentyl i status.']
    else:
        lines += ['- Miara tylko z KWJP F (wycofanie NKJP, ADR-006).']
    lines += ['- Wycofanie NKJP (sama KWJP) nadal wymaga pliku NKJP przypiętego w `pop-sources.json`: '
              'kontrola wejść sprawdza jego SHA256.']
    return '\n'.join(lines) + '\n'


def _terms(result):
    with_nkjp = 'nkjp_rule_id' in result
    measure = ('KWJP (CC BY 4.0) i NKJP (CC BY, wersja nieokreślona; ADR-006)' if with_nkjp
               else 'KWJP (CC BY 4.0)')
    lines = ['# Warunki udostępnienia pakietu POP', '',
             '## Listy (`POP.txt.gz`, `POP0.txt.gz`)', '',
             f'- Wybór i układ list: CC BY 4.0 ({CC_BY_4}).',
             '- Formy pochodzą z eksportu SGJP i zachowują jego warunki BSD-2-Clause z pełną atrybucją '
             '(`ATTRIBUTIONS.md`).',
             f'- Wybór miarą z {measure}.', '',
             '## Raporty (`reports/`)', '',
             f'- Własne raporty: CC BY 4.0 ({CC_BY_4}); miary źródeł z atrybucją w `ATTRIBUTIONS.md`.', '',
             '## Kod', '',
             '- Kod generatora (`literaki_slownik`): BSD-2-Clause; tożsamość kodu w `release-manifest.json`.', '']
    return '\n'.join(lines).rstrip('\n') + '\n'


def _write_text(path, text):
    Path(path).write_bytes(text.encode('utf-8'))


def write_package(result, staging):
    """Zapisz pakiet wyniku `build_pop` w pustym katalogu `staging` (C11, C12, C17, C18)."""
    from .canonical import dumps, write_json
    from .quality import review_template, sample_strata
    from .run import code_identity
    staging = Path(staging)
    (staging / 'reports').mkdir()
    for name in LISTS:
        _write_gzip(staging / LIST_FILES[name], result[name])
    rows = [_package_row(row) for row in result['units']]
    write_json(staging / 'reports/units.json', {'schema_version': 1, 'method': result['method'], 'units': rows})
    write_json(staging / 'reports/thresholds.json', {
        'schema_version': 1, 'method': result['method'], 'adr': result['adr'], 'thresholds': result['thresholds'],
        'must_include_pop0': result['must_include_pop0'], 'missing': result['missing'], 'groups': result['groups'],
        'proper_units': result['proper_units'], 'kwjp_mass': result['mass']['kwjp'],
        'units': len(rows), 'ranked': sum(1 for row in rows if row['rank'] is not None)})
    sample = sample_strata(_strata(result, rows), result['package']['sampling'])
    # Bez końcowego `\n`: SHA256 pliku = `sample_sha256` szablonu przeglądu (D-5).
    _write_text(staging / 'reports/sample.json', dumps(sample))
    evidence = {name: sha256(staging / name) for name in (*LIST_FILES.values(), 'reports/thresholds.json')}
    write_json(staging / 'reports/review-template.json', review_template(
        sample, canonical_index_sha256=sha256(staging / 'reports/units.json'), evidence_sha256=evidence))
    _write_text(staging / 'ATTRIBUTIONS.md', _attributions(result))
    _write_text(staging / 'LIMITATIONS.md', _limitations(result))
    _write_text(staging / 'TERMS.md', _terms(result))
    files = {str(p.relative_to(staging)): {'sha256': sha256(p), 'bytes': p.stat().st_size}
             for p in sorted(staging.rglob('*')) if p.is_file()}
    manifest = {
        'schema_version': 1, 'kind': 'literaki-pop-manifest', 'status': 'BUILT', 'package_id': PACKAGE_ID,
        'method': result['method'], 'adr': result['adr'], 'config_sha256': result['config_sha256'],
        'inputs': result['inputs'], 'base_package_id': result['package']['base_package_id'],
        'code_identity': code_identity(), 'must_include_pop0': sorted(result['must_include_pop0']),
        'sampling': result['package']['sampling']['version'],
        'counts': {name: {k: result['thresholds'][name][k] for k in ('units', 'lexemes', 'forms')} for name in LISTS},
        'hash_scope': 'wszystkie pliki pakietu poza release-manifest.json i SHA256SUMS',
        'files': dict(sorted(files.items()))}
    if 'nkjp_rule_id' in result:
        manifest['nkjp_rule_id'] = result['nkjp_rule_id']
    write_json(staging / 'release-manifest.json', manifest)
    sums = sorted(str(p.relative_to(staging)) for p in staging.rglob('*') if p.is_file())
    _write_text(staging / 'SHA256SUMS', ''.join(f'{sha256(staging / r)}  {r}\n' for r in sums))
    return manifest


def build_package(sources, config, output_dir, run_dir=None, release_dir=None):
    """Polecenie `pop`: listy (`build_pop`) i pakiet `BUILT` w nowym katalogu (C13).

    Cel istnieje → kod 4 (przed liczeniem i przy przeniesieniu). Błąd w trakcie: staging usunięty,
    celu brak. Wynik: podsumowanie list, ścieżka pakietu, liczby form i SHA256 manifestu.
    """
    import os
    import shutil
    import tempfile
    from .export import READ_ONLY, rename_noreplace
    target = Path(output_dir).absolute()
    if os.path.lexists(target):
        raise GeneratorError('Katalog pakietu POP już istnieje; pop nigdy nie nadpisuje', 4, str(target))
    if not target.parent.is_dir():
        raise GeneratorError('Katalog nadrzędny pakietu POP nie istnieje', 2, str(target.parent))
    result = build_pop(sources, config, run_dir, release_dir)
    staging = Path(tempfile.mkdtemp(prefix=f'.{target.name}.staging-', dir=target.parent))
    try:
        write_package(result, staging)
        for path in staging.rglob('*'):
            if path.is_file():
                path.chmod(READ_ONLY)
        rename_noreplace(staging, target)
    except FileExistsError as error:
        shutil.rmtree(staging, ignore_errors=True)
        raise GeneratorError('Katalog pakietu POP powstał w trakcie; pop nigdy nie nadpisuje', 4,
                             str(target)) from error
    except BaseException:
        shutil.rmtree(staging, ignore_errors=True)
        raise
    summary = pop_summary(result)
    summary.update(output_dir=str(target.resolve()), release_manifest_sha256=sha256(target / 'release-manifest.json'),
                   files=sum(1 for p in target.rglob('*') if p.is_file()),
                   forms={name: len(result[name]) for name in LISTS})
    return summary
