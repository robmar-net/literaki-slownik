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
