"""TEMATY: listy tematyczne z etykiet SGJP, Słowosieci i IATE (#11, ADR-010)."""
from collections import Counter, deque
from contextlib import closing
from fractions import Fraction
from pathlib import Path
from urllib.parse import quote
from xml.etree import ElementTree
import os
import re
import shutil
import sqlite3
import tempfile
import unicodedata
import zipfile

from .canonical import dumps, load_json, sha256, write_json
from .export import rename_noreplace
from .inputs import GeneratorError, checked_file
from .pop import _label, load_constructions, write_gzip
from .pop00 import package_file, read_words
from .quality import _config, review_template, sample_strata
from .run import code_identity

METHOD = 'tematy-v1'
ADR = 'docs/adr/ADR-010-tematy-v1.md'
# Przypięte kody części mowy Słowosieci → klasy tagów SGJP; kody 5–8 (angielskie) pomijamy.
CZESCI_MOWY = {'1': ['inf'], '2': ['subst', 'depr'], '3': ['adv'], '4': ['adj']}
T3_KLASY = ['subst', 'depr']
PROGI = ('slowa_oczywiste', 't1_tak', 't2_tak', 't2_nie', 't3_tak', 'zgodnosc')
TEKSTY = ('ATTRIBUTIONS-tematy.md', 'LIMITATIONS.md', 'TERMS.md')
RELACJE = frozenset((11, 25, 27))
# Wejścia z plikiem do hashowania; zip Słowosieci ma tylko pochodzenie (budowa sprawdza `meta` pochodnej).
INPUTS = ('base_run', 'database', 'release_manifest', 'standard', 'broad',
          'base_pop', 'base_pop00', 'plwordnet_db', 'iate')
ZIP_FIELDS = {'url', 'retrieved_at', 'bytes', 'sha256'}
IATE_FIELDS = {'path', 'sha256', 'url', 'retrieved_at', 'last_modified', 'member', 'bytes'}
PLWN_SCRIPT = 'plwn-tematy-v1'
POP_FILES = ('POP.txt.gz', 'reports/units.json', 'ATTRIBUTIONS.md')
POP00_FILES = ('POP00.txt.gz',)
HEX = re.compile('[0-9a-f]{64}')
FRACTION = re.compile(r'0\.[0-9]+|1\.0+|[0-9]+/[1-9][0-9]*')


def _bad(what):
    return GeneratorError('Nieprawidłowa konfiguracja TEMATY: ' + what, 2)


def _int(value):
    return type(value) is int


def _texts(values, *, lower=False):
    return (isinstance(values, list) and len(values) == len(set(map(str, values)))
            and all(isinstance(v, str) and v and v == v.strip() and (not lower or v == v.lower())
                    for v in values))


def _share(text):
    if not isinstance(text, str) or not FRACTION.fullmatch(text):
        raise _bad('próg ' + repr(text))
    value = Fraction(text)
    if not 0 <= value <= 1:
        raise _bad('próg ' + text)
    return value


def load_method(path):
    """Konfiguracja metody (W4); zwraca ją z progami jako ułamkami i ścieżkami tekstów."""
    path = Path(path).resolve()
    value = load_json(path)
    if (not isinstance(value, dict) or set(value) != {'version', 'adr', 'sampling', 'operator_per_stratum',
                                                      'progi', 'czesci_mowy', 't3_klasy', 'teksty'}
            or value['version'] != METHOD or value['adr'] != ADR):
        raise _bad('pola metody')
    _config(value['sampling'])
    operator = value['operator_per_stratum']
    if not _int(operator) or not 0 < operator <= value['sampling']['size_per_stratum']:
        raise _bad('operator_per_stratum')
    if not isinstance(value['progi'], dict) or set(value['progi']) != set(PROGI):
        raise _bad('progi')
    progi = {k: _share(value['progi'][k]) for k in PROGI}
    if value['czesci_mowy'] != CZESCI_MOWY:
        raise _bad('czesci_mowy')
    if value['t3_klasy'] != T3_KLASY:
        raise _bad('t3_klasy')
    teksty = value['teksty']
    if (not isinstance(teksty, dict) or set(teksty) != set(TEKSTY)
            or any(not isinstance(r, dict) or set(r) != {'path', 'sha256'} for r in teksty.values())):
        raise _bad('teksty')
    return {'config': value, 'sha256': sha256(path), 'progi': progi,
            'teksty': {name: checked_file(path.parent, teksty[name]) for name in TEKSTY}}


def _named(items, keys):
    return isinstance(items, list) and all(
        isinstance(i, dict) and set(i) == set(keys) and all(
            _int(i[k]) and i[k] > 0 if k == 'synset' else isinstance(i[k], str) and i[k] for k in keys)
        for i in items)


def load_topic(path):
    """Plik tematu (W5): zbiór kluczy, typy i zamknięte wartości v1."""
    path = Path(path).resolve()
    v = load_json(path)
    if (not isinstance(v, dict) or set(v) != {'id', 'nazwa', 'wersja', 't1', 't2', 't3',
                                              'wykluczenia', 'diagnostyka', 'uwagi'}
            or v['id'] != path.stem or not re.fullmatch('[a-z]+', v['id'])
            or v['wersja'] != v['id'] + '-v1' or not isinstance(v['nazwa'], str) or not v['nazwa']
            or not isinstance(v['uwagi'], str)):
        raise _bad('pola tematu')
    t1, t2, t3, diag = v['t1'], v['t2'], v['t3'], v['diagnostyka']
    if not isinstance(t1, dict) or set(t1) != {'atomy_sgjp'} or not _texts(t1['atomy_sgjp']) or not t1['atomy_sgjp']:
        raise _bad('t1')
    if (not isinstance(t2, dict) or set(t2) != {'korzenie', 'relacje', 'tryb', 'wykluczenia_poddrzew'}
            or not t2['korzenie'] or not _named(t2['korzenie'], ('synset', 'nazwa'))
            or len({k['synset'] for k in t2['korzenie']}) != len(t2['korzenie'])
            or not _named(t2['wykluczenia_poddrzew'], ('synset', 'nazwa', 'powód'))):
        raise _bad('t2')
    relacje = t2['relacje']
    if (not isinstance(relacje, list) or not relacje or not all(_int(r) for r in relacje)
            or len(set(relacje)) != len(relacje) or not set(relacje) <= RELACJE):
        raise _bad('t2.relacje (dozwolone 11, 25, 27)')
    if t2['tryb'] != 'pelne':
        raise _bad('t2.tryb (v1: pelne)')
    iate = t3.get('iate') if isinstance(t3, dict) else None
    if (not isinstance(t3, dict) or set(t3) != {'iate', 'dodatki'} or not isinstance(iate, dict)
            or set(iate) != {'kody_dziedzin', 'typ', 'jedno_slowo', 'niezawodnosc_min', 'odrzuc_status'}
            or not _texts(iate['kody_dziedzin']) or not iate['kody_dziedzin']
            or not all(k.isdigit() for k in iate['kody_dziedzin'])
            or iate['typ'] != 'fullForm' or iate['jedno_slowo'] is not True
            or not _int(iate['niezawodnosc_min']) or not 1 <= iate['niezawodnosc_min'] <= 4
            or not _texts(iate['odrzuc_status'])
            or not _named(t3['dodatki'], ('lemat', 'czesc_mowy', 'powód'))):
        raise _bad('t3')
    if not _named(v['wykluczenia'], ('lemat', 'czesc_mowy', 'powód')):
        raise _bad('wykluczenia')
    marks = diag.get('znaczniki_srodladowe') if isinstance(diag, dict) else None
    if (not isinstance(diag, dict) or set(diag) != {'slowa_oczywiste', 'znaczniki_srodladowe'}
            or not _texts(diag['slowa_oczywiste'], lower=True) or not diag['slowa_oczywiste']
            or not isinstance(marks, dict) or set(marks) != {'pl', 'en'}
            or not all(_texts(m, lower=True) and m for m in marks.values())):
        raise _bad('diagnostyka')
    return v


def load_sources(path):
    """Manifest wejść (W3), wzór `pop00.load_sources`; hashe sprawdza budowa."""
    source = load_json(path)
    inputs = source.get('inputs') if isinstance(source, dict) else None
    if (not isinstance(source, dict) or set(source) != {'schema_version', 'version', 'inputs'}
            or not _int(source['schema_version']) or source['schema_version'] != 1
            or source['version'] != 'tematy-sources-v1' or not isinstance(inputs, dict)
            or set(inputs) != set(INPUTS) | {'plwordnet_zip'}
            or any(not isinstance(inputs[k], dict) or not isinstance(inputs[k].get('path'), str)
                   or set(inputs[k]) != (IATE_FIELDS if k == 'iate' else {'path', 'sha256'})
                   for k in INPUTS)):
        raise GeneratorError('Nieprawidłowy manifest wejść TEMATY', 2)
    for key, fields in (('plwordnet_zip', ZIP_FIELDS), ('iate', IATE_FIELDS)):
        ref = inputs[key]
        if (not isinstance(ref, dict) or set(ref) != fields or not isinstance(ref['sha256'], str)
                or not HEX.fullmatch(ref['sha256']) or not _int(ref['bytes']) or ref['bytes'] <= 0
                or any(not isinstance(ref[k], str) or not ref[k] for k in fields - {'bytes'})):
            raise GeneratorError('Nieprawidłowe pochodzenie wejścia TEMATY: ' + key, 2)
    return source


def register(data, path, expected_sha):
    """Wpis rejestru czytanych plików; hash sprawdził wołający (`checked_file`, `package_file`).

    Zwraca ścieżkę, którą wolno czytać. `confirm_unchanged` re-hashuje cały rejestr.
    """
    path = Path(path).resolve()
    if data['registry'].setdefault(path, expected_sha) != expected_sha:
        raise GeneratorError('Wejście TEMATY zmieniło się podczas operacji', 5, str(path))
    return path


def confirm_unchanged(data):
    """Re-hash każdego pliku z rejestru (naprawa klasy błędu f33fe05)."""
    for path, expected in sorted(data['registry'].items()):
        try:
            same = path.is_file() and not path.is_symlink() and sha256(path) == expected
        except OSError:
            same = False
        if not same:
            raise GeneratorError('Wejście TEMATY zmieniło się podczas operacji', 5, str(path))


def _unpinned(data, path):
    """Plik bez pinu (manifest, temat): rejestrujemy hash z chwili pierwszego odczytu."""
    return register(data, path, sha256(path))


def _readonly(path):
    """SQLite tylko do odczytu, domyślny cache (pełny skan nie potrzebuje 4 GB stron)."""
    return closing(sqlite3.connect('file:' + quote(str(path)) + '?mode=ro', uri=True))


def _plwordnet_meta(path, zip_sha):
    try:
        with _readonly(path) as db:
            meta = dict(db.execute('SELECT key, value FROM meta'))
    except sqlite3.Error as error:
        raise GeneratorError('Nieczytelna pochodna Słowosieci: ' + str(error), 4, str(path)) from error
    if meta.get('script_version') != PLWN_SCRIPT or meta.get('zip_sha256') != zip_sha:
        raise GeneratorError('Pochodna Słowosieci nie pochodzi z przypiętego zipa', 3, str(path))
    return meta


def _members(units, name):
    members = {m for row in units['units'] for m in row['members_in'].get(name, [])}
    if not members or any(not isinstance(m, str) or m.count('@') != 1 for m in members):
        raise GeneratorError('Nieprawidłowi członkowie ' + name, 4)
    return members


def check_inputs(manifest, config, topic):
    """Wejścia budowy (W3, W6), wzór `pop00.check_inputs`; każdy czytany plik idzie przez rejestr.

    Kody: 2 konfiguracja, 3 niezgodny hash lub powiązanie, 4 dane, 5 przebieg nie FROZEN.
    """
    data = {'registry': {}}
    manifest = _unpinned(data, manifest)
    source = load_sources(manifest)
    config = _unpinned(data, config)
    method = load_method(config)
    if method['sha256'] != data['registry'][config]:
        raise GeneratorError('Konfiguracja TEMATY zmieniła się podczas odczytu', 5, str(config))
    texts = {name: register(data, path, method['config']['teksty'][name]['sha256'])
             for name, path in method['teksty'].items()}
    topic_path = _unpinned(data, topic)
    topic = load_topic(topic_path)
    refs = source['inputs']
    pins = {k: refs[k]['sha256'] for k in INPUTS}
    paths = {k: register(data, checked_file(manifest.parent, refs[k]), pins[k]) for k in INPUTS}
    run, release = load_json(paths['base_run']), load_json(paths['release_manifest'])
    pop, pop00 = load_json(paths['base_pop']), load_json(paths['base_pop00'])
    if run.get('readiness') != 'FROZEN':
        raise GeneratorError('Przebieg TEMATY nie jest FROZEN', 5)
    files = release.get('files', {}) if isinstance(release.get('files'), dict) else {}
    if (run.get('verification', {}).get('database_sha256') != pins['database']
            or run.get('export', {}).get('release_manifest_sha256') != pins['release_manifest']
            or release.get('kind') != 'literaki-release-manifest' or release.get('package_id') != 'LL-PL'
            or release.get('status') != 'FROZEN'
            or files.get('LL-PL-BROAD.txt', {}).get('sha256') != pins['broad']
            or files.get('LL-PL-STANDARD.txt', {}).get('sha256') != pins['standard']):
        raise GeneratorError('Niezgodny przebieg, manifest wydania albo BROAD/STANDARD', 3)
    base = pop.get('inputs', {})
    if (pop.get('kind') != 'literaki-pop-manifest' or pop.get('method') != 'pop-v3'
            or pop.get('package_id') != 'POP' or pop.get('status') != 'BUILT'
            or base.get('database_sha256') != pins['database']
            or base.get('standard_sha256') != pins['standard']
            or base.get('release_manifest_sha256') != pins['release_manifest']):
        raise GeneratorError('Niezgodna podstawa POP', 3)
    base = pop00.get('inputs', {})
    if (pop00.get('kind') != 'literaki-pop00-manifest' or pop00.get('method') != 'pop00-v1'
            or pop00.get('package_id') != 'POP00' or pop00.get('status') != 'BUILT'
            or base.get('base_pop') != pins['base_pop'] or base.get('base_run') != pins['base_run']
            or base.get('database') != pins['database'] or base.get('standard') != pins['standard']):
        raise GeneratorError('Niezgodna podstawa POP00', 3)
    package = {}
    for manifest_path, value, names in ((paths['base_pop'], pop, POP_FILES),
                                        (paths['base_pop00'], pop00, POP00_FILES)):
        for name in names:
            package[name] = register(data, package_file(manifest_path.parent, value, name),
                                     value['files'][name]['sha256'])
    units = load_json(package['reports/units.json'])
    if not isinstance(units, dict) or not isinstance(units.get('units'), list):
        raise GeneratorError('Nieprawidłowy reports/units.json POP', 4)
    members = {name: _members(units, name) for name in ('POP', 'POP0')}
    words = {k: read_words(paths[k]) for k in ('broad', 'standard')}
    words['pop'], words['pop00'] = read_words(package['POP.txt.gz']), read_words(package['POP00.txt.gz'])
    if not words['standard'] <= words['broad']:
        raise GeneratorError('STANDARD nie jest podzbiorem BROAD', 4)
    if not words['pop'] <= words['standard'] or not words['pop00'] <= words['standard']:
        raise GeneratorError('POP albo POP00 nie jest podzbiorem STANDARD', 4)
    plwordnet_meta = _plwordnet_meta(paths['plwordnet_db'], refs['plwordnet_zip']['sha256'])
    return {**data, 'source': source, 'method': method, 'topic': topic, 'texts': texts,
            'paths': paths, 'pins': pins, 'package': package, 'members': members, **words,
            'attribution': package['ATTRIBUTIONS.md'].read_text(encoding='utf-8'),
            'plwordnet_meta': plwordnet_meta}


# --- Kandydaci T1, T2, T3 (W7) ---
POLSKIE_LITERY = re.compile('[a-ząćęłńóśźż]+')
XML_LANG = '{http://www.w3.org/XML/1998/namespace}lang'
HEADER_BYTES = 1 << 16
# Kolejność powodów odrzucenia terminu T3: pierwszy pasujący wygrywa.
T3_POWODY = ('TYP', 'STATUS', 'NIEZAWODNOSC', 'NIE_JEDNO_SLOWO', 'WIELKA_LITERA')


def jedno_slowo(text):
    """W7: po NFC i małych literach wyłącznie litery alfabetu polskiego."""
    return bool(POLSKIE_LITERY.fullmatch(unicodedata.normalize('NFC', text).lower()))


def qualifier_atoms(qualifiers):
    """Kwalifikatory SGJP: podział po `|`, potem po `,`; atomy całe, bez spacji wokół."""
    return frozenset(a.strip() for part in qualifiers.split('|') for a in part.split(',') if a.strip())


def scan_sgjp(data):
    """Jedyny pełny skan `interpretation` (T1 i klasy leksemów).

    Zwraca `t1`: `lexeme.id` → posortowane atomy tematu z jego interpretacji,
    oraz `klasy`: `lexeme.id` → posortowane klasy tagów (pierwszy segment) każdego leksemu.
    """
    atoms = frozenset(data['topic']['t1']['atomy_sgjp'])
    parsed, t1, classes, interned = {}, {}, {}, {}
    with _readonly(data['paths']['database']) as db:
        # Te same (tag, qualifiers) powtarzają się milionami; `names` T1 nie potrzebuje.
        for lexeme_id, tag, qualifiers in db.execute('select lexeme_id,tag,qualifiers from interpretation'):
            item = parsed.get((tag, qualifiers))
            if item is None:
                item = parsed[tag, qualifiers] = (tag.split(':', 1)[0], atoms & qualifier_atoms(qualifiers))
            found = classes.get(lexeme_id)
            if found is None:
                classes[lexeme_id] = {item[0]}
            else:
                found.add(item[0])
            if item[1]:
                t1.setdefault(lexeme_id, set()).update(item[1])
    for lexeme_id, found in classes.items():
        key = frozenset(found)
        classes[lexeme_id] = interned.get(key) or interned.setdefault(key, tuple(sorted(key)))
    return {'t1': {i: tuple(sorted(a)) for i, a in sorted(t1.items())}, 'klasy': classes}


def _root_name(db, synset):
    row = db.execute('SELECT l.lemma, l.variant FROM unitandsynset u JOIN lexicalunit l ON l.ID = u.LEX_ID '
                     'WHERE u.SYN_ID = ? ORDER BY u.unitindex LIMIT 1', (synset,)).fetchone()
    return None if row is None else f'{row[0]} {row[1]}'


def _check_names(db, items, what):
    for item in items:
        if _root_name(db, item['synset']) != item['nazwa']:
            raise _bad(f'{what} {item["synset"]}: nazwa {item["nazwa"]!r} niezgodna ze Słowosiecią '
                       f'({_root_name(db, item["synset"])!r})')


def t2_candidates(data):
    """T2 (W7, D3, D4): pełne domknięcie od korzeni po relacjach tematu, PARENT_ID → CHILD_ID.

    Synsety sztuczne przechodzimy bez lematów; jednostki z kodem spoza `czesci_mowy` pomijamy.
    Zwraca `synsety` (osiągnięte, posortowane), `sztuczne`, `jednostki` (przyjęte),
    `lematy`: lemat → {`klasy`, `kody`, `znaczenia`} oraz `odrzucone`: powód → posortowane znaczenia.
    """
    t2, mapping = data['topic']['t2'], data['method']['config']['czesci_mowy']
    relations = sorted(t2['relacje'])
    marks = ','.join('?' * len(relations))
    with _readonly(data['paths']['plwordnet_db']) as db:
        _check_names(db, t2['korzenie'], 'korzeń')
        _check_names(db, t2['wykluczenia_poddrzew'], 'wykluczenie')
        excluded = {item['synset'] for item in t2['wykluczenia_poddrzew']}
        reached = {k['synset'] for k in t2['korzenie']} - excluded
        queue = deque(sorted(reached))
        while queue:
            for (child,) in db.execute(f'SELECT CHILD_ID FROM synsetrelation WHERE PARENT_ID = ? '
                                       f'AND REL_ID IN ({marks}) ORDER BY CHILD_ID', (queue.popleft(), *relations)):
                if child not in reached and child not in excluded:
                    reached.add(child)
                    queue.append(child)
        synsets = sorted(reached)
        abstract, units = set(), []
        for start in range(0, len(synsets), 500):
            chunk = synsets[start:start + 500]
            marks_chunk = ','.join('?' * len(chunk))
            abstract.update(i for (i,) in db.execute(
                f'SELECT ID FROM synset WHERE isabstract = 1 AND ID IN ({marks_chunk})', chunk))
            units.extend(db.execute(
                'SELECT u.SYN_ID, l.lemma, l.pos, l.variant FROM unitandsynset u '
                f'JOIN lexicalunit l ON l.ID = u.LEX_ID WHERE u.SYN_ID IN ({marks_chunk})', chunk))
    rejected = {'KOD_POZA_MAPA': [], 'NIE_JEDNO_SLOWO': []}
    accepted, lemmas = [], {}
    for synset, lemma, pos, variant in sorted(units, key=lambda u: (u[1], u[3], u[2], u[0])):
        if synset in abstract:
            continue
        lemma, code = unicodedata.normalize('NFC', lemma), str(pos)
        meaning = f'{lemma} {variant}'
        if code not in mapping:
            rejected['KOD_POZA_MAPA'].append(meaning)
        elif not jedno_slowo(lemma):
            rejected['NIE_JEDNO_SLOWO'].append(meaning)
        else:
            accepted.append({'lemat': lemma, 'kod': code, 'wariant': variant, 'synset': synset, 'znaczenie': meaning})
            entry = lemmas.setdefault(lemma, ({'klasy': set(), 'kody': set(), 'znaczenia': set()}))
            entry['klasy'].update(mapping[code])
            entry['kody'].add(code)
            entry['znaczenia'].add(meaning)
    return {'synsety': synsets, 'sztuczne': sorted(abstract), 'jednostki': accepted,
            'lematy': {lemma: {k: tuple(sorted(v)) for k, v in entry.items()} for lemma, entry in sorted(lemmas.items())},
            'odrzucone': {k: sorted(v) for k, v in rejected.items()}}


def _check_header(head):
    """DOCTYPE dozwolone; `<!ENTITY` albo podzbiór wewnętrzny DTD = błąd danych (kod 4)."""
    text = head.decode('utf-8', 'replace')
    first = re.search(r'<(?![?!])', text)
    if first is None:
        raise GeneratorError('TBX IATE: brak elementu głównego w nagłówku', 4)
    prolog = text[:first.start()]
    doctype = re.search(r'<!DOCTYPE\b([^>]*)>', prolog)
    if '<!ENTITY' in prolog or ('<!DOCTYPE' in prolog and (doctype is None or '[' in doctype.group(1))):
        raise GeneratorError('TBX IATE: deklaracje encji albo podzbiór wewnętrzny DTD są niedozwolone', 4)


def _local(tag):
    return tag.rsplit('}', 1)[-1]


def _typed(element, name, kind):
    for child in element:
        if _local(child.tag) == name and child.get('type') == kind:
            return (child.text or '').strip()
    return None


def _terms(entry):
    """(język, termin, termType, administrativeStatus, reliabilityCode) każdego `tig` hasła."""
    for lang_set in entry:
        if _local(lang_set.tag) != 'langSet':
            continue
        lang = (lang_set.get(XML_LANG) or '').lower()
        for tig in lang_set:
            if _local(tig.tag) != 'tig':
                continue
            term = next((unicodedata.normalize('NFC', (c.text or '').strip()) for c in tig if _local(c.tag) == 'term'), '')
            reliability = _typed(tig, 'descrip', 'reliabilityCode')
            yield (lang, term, _typed(tig, 'termNote', 'termType'), _typed(tig, 'termNote', 'administrativeStatus'),
                   int(reliability) if reliability and reliability.isdigit() else 0)


def _reason(term, kind, status, reliability, iate):
    if kind != iate['typ']:
        return 'TYP'
    if status in iate['odrzuc_status']:
        return 'STATUS'
    if reliability < iate['niezawodnosc_min']:
        return 'NIEZAWODNOSC'
    if not jedno_slowo(term):
        return 'NIE_JEDNO_SLOWO'
    if term != term.lower():
        return 'WIELKA_LITERA'
    return None


def t3_candidates(data):
    """T3 (W7, K1, W1, W2): hasła IATE z całym kodem dziedziny, terminy PL po filtrach.

    Strumień `iterparse` z członka zipa; zewnętrznego DTD nie ładujemy. Zwraca `terminy`:
    termin → posortowane id haseł; `hasla` (kandydaci): id → {`pl`, `en`, `przyjete`, `kody` (pasujące)};
    `odrzucone`: powód → posortowane terminy; `liczniki` haseł i terminów PL.
    """
    iate = data['topic']['t3']['iate']
    codes = frozenset(iate['kody_dziedzin'])
    member = data['source']['inputs']['iate']['member']
    terms, entries, rejected = {}, {}, {r: [] for r in T3_POWODY}
    counts = {'hasla': 0, 'hasla_pl': 0, 'termType': Counter(), 'status': Counter()}
    try:
        with zipfile.ZipFile(data['paths']['iate']) as archive:
            with archive.open(member) as stream:
                _check_header(stream.read(HEADER_BYTES))
            with archive.open(member) as stream:
                stack = []
                for event, element in ElementTree.iterparse(stream, events=('start', 'end')):
                    if event == 'start':
                        stack.append(element)
                        continue
                    stack.pop()
                    if _local(element.tag) != 'termEntry':
                        continue
                    group = next((c for c in element if _local(c.tag) == 'descripGrp'), None)
                    field = _typed(group, 'descrip', 'subjectField') if group is not None else None
                    matched = codes & {c.strip() for c in field.split(',')} if field else None
                    if matched:
                        _entry(element, iate, terms, entries, rejected, counts, matched)
                    element.clear()
                    if stack:
                        stack[-1].remove(element)
    except (zipfile.BadZipFile, KeyError, ElementTree.ParseError) as error:
        raise GeneratorError('Nieczytelny TBX IATE: ' + str(error), 4, str(data['paths']['iate'])) from error
    accepted = sum(len(v) for v in terms.values())
    return {'terminy': {t: tuple(sorted(ids)) for t, ids in sorted(terms.items())},
            'hasla': dict(sorted(entries.items())),
            'odrzucone': {r: sorted(v) for r, v in rejected.items() if v},
            'liczniki': {'hasla': counts['hasla'], 'hasla_pl': counts['hasla_pl'],
                         'termType': dict(sorted(counts['termType'].items())),
                         'status': dict(sorted(counts['status'].items())),
                         'przyjete': accepted, 'przyjete_rozne': len(terms)}}


def _entry(element, iate, terms, entries, rejected, counts, matched):
    entry_id = element.get('id') or ''
    counts['hasla'] += 1
    pl, en, taken = [], [], []
    for lang, term, kind, status, reliability in _terms(element):
        if lang == 'en':
            en.append(term)
        if lang != 'pl':
            continue
        pl.append(term)
        counts['termType'][kind or 'BRAK'] += 1
        counts['status'][status or 'BRAK'] += 1
        reason = _reason(term, kind, status, reliability, iate)
        if reason:
            rejected[reason].append(term)
        else:
            taken.append(term)
            terms.setdefault(term, []).append(entry_id)
    counts['hasla_pl'] += bool(pl)
    if taken:
        entries[entry_id] = {'pl': tuple(sorted(pl)), 'en': tuple(sorted(en)), 'przyjete': tuple(sorted(taken)),
                             'kody': tuple(sorted(matched))}


def candidates(data):
    """Kandydaci trzech źródeł; każdy plik z `data['paths']` (rejestr z `check_inputs`)."""
    return {'sgjp': scan_sgjp(data), 't2': t2_candidates(data), 't3': t3_candidates(data)}


# --- Leksemy, warstwy i formy (W7, W8, D15) ---
WARSTWY = ('T1', 'T2', 'T3')
POWODY = ('BRAK_LEKSEMU', 'NIE_JEDNO_SLOWO', 'POZA_BROAD', 'POZA_STANDARD')
CHUNK = 400  # jak `pop00.read_analyses`


def _chunks(values, size=CHUNK):
    values = sorted(values)
    for start in range(0, len(values), size):
        chunk = values[start:start + size]
        yield chunk, ','.join('?' * len(chunk))


def _lexeme_rows(db, column, values):
    """`lexeme` po indeksie (`id` albo `lemma_base`) → id → (source_id, lemma_id, lemma_base)."""
    rows = {}
    for chunk, marks in _chunks(values):
        rows.update((i, (s, l, b)) for i, s, l, b in db.execute(
            f'SELECT id, source_id, lemma_id, lemma_base FROM lexeme WHERE {column} IN ({marks})', chunk))
    return rows


def map_lemmas(db, wanted, klasy):
    """Lemat → leksemy z równym `lemma_base` i klasą z dozwolonych (W7).

    `wanted`: lemat → dozwolone klasy tagów; `klasy`: `scan_sgjp(...)['klasy']`.
    Zwraca `leksemy` (lemat → posortowane id), `brak` (lematy bez leksemu, `BRAK_LEKSEMU`),
    `ger` (te z `brak`, które są formą o tagu `ger`; indeksy surface_form → interpretation)
    i `wiersze` (id → (source_id, lemma_id, lemma_base)).
    """
    rows = _lexeme_rows(db, 'lemma_base', wanted)
    by_base = {}
    for ident, (_, _, base) in rows.items():
        by_base.setdefault(base, []).append(ident)
    found, missing = {}, []
    for lemma, allowed in sorted(wanted.items()):
        ids = sorted(i for i in by_base.get(lemma, ()) if set(klasy.get(i, ())) & set(allowed))
        if ids:
            found[lemma] = ids
        else:
            missing.append(lemma)
    ger = set()
    for chunk, marks in _chunks(missing):
        ger.update(form for form, tag in db.execute(
            'SELECT s.original, i.tag FROM surface_form s JOIN interpretation i ON i.form_id = s.id '
            f'WHERE s.original IN ({marks})', chunk) if tag.split(':', 1)[0] == 'ger')
    return {'leksemy': found, 'brak': missing, 'ger': sorted(ger), 'wiersze': rows}


def _plwn_units(data, lemmas):
    """Synsety jednostek Słowosieci o kodach z mapy (1–4) dla lematów; kody 5–8 pomijamy."""
    codes = sorted(int(c) for c in data['method']['config']['czesci_mowy'])
    units = {}
    with _readonly(data['paths']['plwordnet_db']) as db:
        for chunk, marks in _chunks(lemmas):
            for lemma, synset in db.execute(
                    'SELECT l.lemma, u.SYN_ID FROM lexicalunit l JOIN unitandsynset u ON u.LEX_ID = l.ID '
                    f'WHERE l.lemma IN ({marks}) AND l.pos IN ({",".join("?" * len(codes))})', (*chunk, *codes)):
                units.setdefault(unicodedata.normalize('NFC', lemma), set()).add(synset)
    return units


def _wieloznaczny(ident, row, homonyms, klasy, units, closure):
    """ADR-007 badania: `tak` (jednostka poza domknięciem albo kilka leksemów lematu i klasy),
    `nie` (wszystkie znaczenia w temacie), `brak_danych` (lematu nie ma w Słowosieci)."""
    mine = set(klasy.get(ident, ()))
    if any(other != ident and mine & set(klasy.get(other, ())) for other in homonyms.get(row[2], ())):
        return 'tak'
    synsets = units.get(row[2])
    if not synsets:
        return 'brak_danych'
    return 'nie' if synsets <= closure else 'tak'


def _read_forms(db, data, ids):
    """Formy leksemów kandydatów porcjami po `lexeme_id` plus konstrukcje ∈ BROAD (D15).

    Bez `pop.load_forms`: `interpretation` czytamy przez indeks `lexeme_id`, nie w całości.
    """
    forms = {i: set() for i in ids}
    for chunk, marks in _chunks(ids):
        for ident, word in db.execute('SELECT i.lexeme_id, s.game_key FROM interpretation i '
                                      f'JOIN surface_form s ON s.id = i.form_id WHERE i.lexeme_id IN ({marks})', chunk):
            forms[ident].add(word)
    keys = {i: (row[0], row[1]) for i, row in ids.items()}
    built = load_constructions(db, data['broad'], {i: {'key': k} for i, k in keys.items()}, surface_keys=frozenset())
    for ident, key in keys.items():
        forms[ident] |= built['forms'].get(key, frozenset())
    return forms


def build_entries(data, cands):
    """Kandydaci (`candidates`) → leksemy z warstwą, źródłami, flagą i formami; diagnostyka BROAD/STANDARD.

    Zwraca:
    - `kandydaci`: klucz `lemma_id@source_id` → {`klucz`, `lemat`, `czesci_mowy`, `warstwa`, `zrodla`,
      `znaczenie` (warstwa → napisy), `iate` (id haseł T3), `wieloznaczny`, `formy` (wszystkie, posortowane),
      `powod` (None, `POZA_BROAD` albo `POZA_STANDARD`)};
    - `wpisy`: kandydaci z formą w STANDARD; `formy` = formy ∩ STANDARD;
    - `warstwy`: warstwa → posortowane klucze wpisów (rozłączne); `formy`: posortowane formy tematu ∩ STANDARD;
    - `diagnostyka`: warstwa i `razem` → {`leksemy`, `formy`} → {`kandydaci`, `broad`, `standard`};
    - `odrzucone`: warstwa i `razem` → powód → posortowane lematy (BRAK_LEKSEMU, NIE_JEDNO_SLOWO) albo klucze;
    - `ger`: warstwa i `razem` → lematy `BRAK_LEKSEMU`, które są formą `ger`.
    """
    klasy, t1, t2, t3 = cands['sgjp']['klasy'], cands['sgjp']['t1'], cands['t2'], cands['t3']
    mapping = data['method']['config']['czesci_mowy']
    wanted2 = {}
    for unit in t2['jednostki']:
        wanted2.setdefault(unit['lemat'], set()).update(mapping[unit['kod']])
    with _readonly(data['paths']['database']) as db:
        m2 = map_lemmas(db, {k: tuple(sorted(v)) for k, v in wanted2.items()}, klasy)
        m3 = map_lemmas(db, {t: tuple(T3_KLASY) for t in t3['terminy']}, klasy)
        rows = {**_lexeme_rows(db, 'id', t1), **m2['wiersze'], **m3['wiersze']}
        sources = {}
        for ident in t1:
            sources.setdefault(ident, {})['T1'] = tuple(t1[ident])
        for unit in t2['jednostki']:
            for ident in m2['leksemy'].get(unit['lemat'], ()):
                if set(klasy.get(ident, ())) & set(mapping[unit['kod']]):
                    sources.setdefault(ident, {}).setdefault('T2', set()).add(f'{unit["synset"]} {unit["znaczenie"]}')
        iate = {}
        for term, entry_ids in t3['terminy'].items():
            for ident in m3['leksemy'].get(term, ()):
                iate.setdefault(ident, set()).update(entry_ids)
                sources.setdefault(ident, {}).setdefault('T3', set()).update(
                    f'{e} {",".join(t3["hasla"][e]["kody"])}' for e in entry_ids)
        candidates_rows = {i: rows[i] for i in sources}
        homonyms = {}
        for ident, row in _lexeme_rows(db, 'lemma_base', {r[2] for r in candidates_rows.values()}).items():
            homonyms.setdefault(row[2], []).append(ident)
        forms = _read_forms(db, data, candidates_rows)
    units = _plwn_units(data, {r[2] for r in candidates_rows.values()})
    closure = set(t2['synsety'])
    broad, standard = data['broad'], data['standard']
    kandydaci = {}
    for ident, found in sources.items():
        row = candidates_rows[ident]
        all_forms = forms[ident]
        reason = (None if all_forms & standard else 'POZA_STANDARD' if all_forms & broad else 'POZA_BROAD')
        key = _label(row[:2])
        kandydaci[key] = {
            'klucz': key, 'lemat': row[2], 'czesci_mowy': tuple(klasy.get(ident, ())),
            'warstwa': min(found), 'zrodla': tuple(sorted(found)),
            'znaczenie': {w: tuple(sorted(v)) for w, v in sorted(found.items())},
            'iate': tuple(sorted(iate.get(ident, ()))),
            'wieloznaczny': _wieloznaczny(ident, row, homonyms, klasy, units, closure),
            'formy': tuple(sorted(all_forms)), 'powod': reason}
    kandydaci = dict(sorted(kandydaci.items()))
    wpisy = {k: {**{f: v for f, v in e.items() if f != 'powod'},
                 'formy': tuple(sorted(set(e['formy']) & standard))}
             for k, e in kandydaci.items() if e['powod'] is None}
    groups = {w: [e for e in kandydaci.values() if e['warstwa'] == w] for w in WARSTWY}
    groups['razem'] = list(kandydaci.values())

    diag = {}
    for name, items in groups.items():
        lex = {'kandydaci': len(items), 'broad': sum(e['powod'] != 'POZA_BROAD' for e in items),
               'standard': sum(e['powod'] is None for e in items)}
        words = {f for e in items for f in e['formy']}
        diag[name] = {'leksemy': lex, 'formy': {'kandydaci': len(words), 'broad': len(words & broad),
                                                 'standard': len(words & standard)}}
    one_word = {'T2': {m.rsplit(' ', 1)[0] for m in t2['odrzucone']['NIE_JEDNO_SLOWO']},
                'T3': set(t3['odrzucone'].get('NIE_JEDNO_SLOWO', ()))}
    missing = {'T2': set(m2['brak']), 'T3': set(m3['brak'])}
    gerunds = {'T2': set(m2['ger']), 'T3': set(m3['ger'])}
    odrzucone, ger = {}, {}
    for name, items in groups.items():
        layers = WARSTWY if name == 'razem' else (name,)
        odrzucone[name] = {
            'BRAK_LEKSEMU': sorted(set().union(*(missing.get(w, ()) for w in layers))),
            'NIE_JEDNO_SLOWO': sorted(set().union(*(one_word.get(w, ()) for w in layers))),
            'POZA_BROAD': [e['klucz'] for e in items if e['powod'] == 'POZA_BROAD'],
            'POZA_STANDARD': [e['klucz'] for e in items if e['powod'] == 'POZA_STANDARD']}
        ger[name] = sorted(set().union(*(gerunds.get(w, ()) for w in layers)))
    return {'kandydaci': kandydaci, 'wpisy': wpisy,
            'warstwy': {w: tuple(k for k, e in wpisy.items() if e['warstwa'] == w) for w in WARSTWY},
            'formy': tuple(sorted({f for e in wpisy.values() for f in e['formy']})),
            'diagnostyka': diag, 'odrzucone': odrzucone, 'ger': ger}


# --- Raporty, próba i pakiet (W8–W11, W15) ---
KIND = 'literaki-tematy-manifest'
PACKAGE_ID = 'TEMATY'
PRZYKLADY = 10
PRZYKLADY_SRODLADOWE = 20
ZNACZNIK = '@@SRODLADOWE@@'
TSV_KOLUMNY = ('klucz', 'lemat', 'czesci_mowy', 'warstwa', 'zrodla', 'znaczenie', 'wieloznaczny', 'formy')
# Progi z ocen R2; automat ich nie rozstrzyga („czeka na ocenę”).
CZEKA = ('t1_tak', 't2_tak', 't2_nie', 't3_tak', 'zgodnosc')
GRUPY = (*WARSTWY, 'razem')
WIELOZNACZNY = ('tak', 'nie', 'brak_danych')
POP00_LEKSEMY = 'POP00 na poziomie leksemów = członkowie POP0 z reports/units.json POP (pop-v3)'


def _pct(part, whole):
    """Procent z jednym miejscem (kropka), z dokładnego ułamka; None przy pustym mianowniku."""
    return None if not whole else f'{float(Fraction(100 * part, whole)):.1f}'


def _part(part, whole):
    return {'liczba': part, 'procent': _pct(part, whole)}


def _examples(values, limit=PRZYKLADY):
    values = list(values)
    return {'liczba': len(values), 'przyklady': values[:limit]}


def _groups(built):
    groups = {w: [built['wpisy'][k] for k in built['warstwy'][w]] for w in WARSTWY}
    groups['razem'] = list(built['wpisy'].values())
    return groups


def _overlap(data, built):
    """Przecięcia z POP i POP00 (W8): leksemy (liczba główna) i formy, razem i na warstwę."""
    lex, forms = {}, {}
    for name, items in _groups(built).items():
        keys = {e['klucz'] for e in items}
        words = {f for e in items for f in e['formy']}
        lex[name] = {'temat': len(keys), 'pop': _part(len(keys & data['members']['POP']), len(keys)),
                     'pop00': _part(len(keys & data['members']['POP0']), len(keys))}
        forms[name] = {'temat': len(words), 'pop': _part(len(words & data['pop']), len(words)),
                       'pop00': _part(len(words & data['pop00']), len(words))}
    return {'leksemy': lex, 'formy': forms, 'uwaga': POP00_LEKSEMY + '; formy z POP.txt.gz i POP00.txt.gz'}


def _diagnostics(built):
    return {name: {kind: {**row, 'procent_broad': _pct(row['broad'], row['kandydaci']),
                          'procent_standard': _pct(row['standard'], row['kandydaci'])}
                   for kind, row in item.items()}
            for name, item in built['diagnostyka'].items()}


def _rejected(built):
    """Odrzuceni na warstwę i powód: liczba i pierwsze 10 z posortowanej listy (W8)."""
    result = {}
    for name in GRUPY:
        rows = {reason: _examples(built['odrzucone'][name][reason]) for reason in POWODY}
        rows['BRAK_LEKSEMU']['ger'] = _examples(built['ger'][name])
        result[name] = rows
    return result


def slowa_oczywiste(words, wpisy, prog):
    """Test 37 słów (W9): słowo pokryte, gdy ma je lemat wpisu. Do progu idzie wynik całości."""
    lemmas = {w: set() for w in WARSTWY}
    for entry in wpisy.values():
        lemmas[entry['warstwa']].add(entry['lemat'])

    def score(layers):
        covered = set().union(*(lemmas[w] for w in layers))
        missing = [w for w in words if w not in covered]
        return {'pokryte': len(words) - len(missing), 'procent': _pct(len(words) - len(missing), len(words)),
                'brakujace': missing}
    total = score(WARSTWY)
    return {'lista': len(words), 'razem': total, 'T1': score(('T1',)), 'T1_T2': score(('T1', 'T2')),
            'spelniony': Fraction(total['pokryte'], len(words)) >= prog}


def _patterns(markers):
    return [re.compile(r'(?<!\w)' + re.escape(m)) for m in markers]


def srodladowe_hasla(hasla, znaczniki):
    """W10: id haseł, w których termin PL lub EN ma znacznik jako początek słowa."""
    pl, en = _patterns(znaczniki['pl']), _patterns(znaczniki['en'])

    def hit(terms, patterns):
        return any(p.search(t.lower()) for t in terms for p in patterns)
    return sorted(i for i, e in hasla.items() if hit(e['pl'], pl) or hit(e['en'], en))


def _inland(topic, t3, built):
    marks = topic['diagnostyka']['znaczniki_srodladowe']
    hasla = t3['hasla']
    found = srodladowe_hasla(hasla, marks)
    entries = [built['wpisy'][k] for k in built['warstwy']['T3']]
    inland = [e['klucz'] for e in entries if set(found) & set(e['iate'])]
    return {'znaczniki': marks,
            'kandydaci_t3': {'hasla': len(hasla), 'srodladowe': len(found), 'procent': _pct(len(found), len(hasla)),
                             'przyklady': [f'{i} ({", ".join(hasla[i]["przyjete"])})'
                                           for i in found[:PRZYKLADY_SRODLADOWE]]},
            'wpisy_t3': {'wpisy': len(entries), 'srodladowe': len(inland), 'procent': _pct(len(inland), len(entries)),
                         'przyklady': inland[:PRZYKLADY_SRODLADOWE]}}


def summary(data, cands, built):
    """`reports/summary.json` (W8–W10); `raport.md` powstaje z tych samych liczb."""
    topic, config, t2, t3 = data['topic'], data['method']['config'], cands['t2'], cands['t3']
    wpisy = built['wpisy']
    words = slowa_oczywiste(topic['diagnostyka']['slowa_oczywiste'], wpisy, data['method']['progi']['slowa_oczywiste'])
    words['prog'] = config['progi']['slowa_oczywiste']
    failed = [] if words['spelniony'] else ['slowa_oczywiste']
    flags = {v: [k for k, e in wpisy.items() if e['wieloznaczny'] == v] for v in WIELOZNACZNY}
    return {
        'method': METHOD, 'temat': topic['id'], 'wersja_tematu': topic['wersja'],
        'liczby': {'kandydaci': len(built['kandydaci']), 'wpisy': len(wpisy), 'formy': len(built['formy']),
                   'warstwy': {w: len(built['warstwy'][w]) for w in WARSTWY}},
        'przeciecia': _overlap(data, built),
        'diagnostyka': _diagnostics(built),
        'odrzucone': _rejected(built),
        't1': {'atomy': topic['t1']['atomy_sgjp'], 'leksemy': len(cands['sgjp']['t1'])},
        't2': {'synsety': len(t2['synsety']), 'sztuczne': len(t2['sztuczne']), 'jednostki': len(t2['jednostki']),
               'lematy': len(t2['lematy']), 'odrzucone': {k: _examples(v) for k, v in t2['odrzucone'].items()}},
        't3': {**t3['liczniki'], 'hasla_kandydaci': len(t3['hasla']),
               'odrzucone': {r: _examples(t3['odrzucone'].get(r, ())) for r in T3_POWODY}},
        'wieloznaczny': {v: {**_part(len(keys), len(wpisy)), 'przyklady': keys[:PRZYKLADY]} for v, keys in flags.items()},
        'slowa_oczywiste': words,
        'srodladowe': _inland(topic, t3, built),
        'werdykt': {'automatyczny': 'popraw' if failed else 'dalej', 'niespelnione': failed,
                    'czeka_na_ocene': list(CZEKA), 'uwaga': '„stop” wybiera tylko operator na bramce'},
    }


def _pl(pct):
    return 'brak' if pct is None else pct.replace('.', ',') + '%'


def _share_text(part, whole, pct):
    return f'{part} z {whole} ({_pl(pct)})'


def raport(report):
    """`reports/raport.md`: po polsku, z liczb `summary.json`."""
    n, over, words, inland, verdict = (report[k] for k in ('liczby', 'przeciecia', 'slowa_oczywiste',
                                                           'srodladowe', 'werdykt'))
    lex, forms = over['leksemy'], over['formy']
    warstwy = ', '.join(f'{w} {n["warstwy"][w]}' for w in WARSTWY)
    total = words['razem']
    cand = inland['kandydaci_t3']
    failed = ', '.join(verdict['niespelnione']) or 'brak'
    lines = [
        f'# Raport TEMATY: {report["temat"]} ({report["wersja_tematu"]}, {report["method"]})', '',
        '## TL;DR',
        f'- Wpisy: {n["wpisy"]} ({warstwy}); formy w MORZE: {n["formy"]}.',
        f'- W POP: {_share_text(lex["razem"]["pop"]["liczba"], lex["razem"]["temat"], lex["razem"]["pop"]["procent"])} '
        f'leksemów; w POP00: {_share_text(lex["razem"]["pop00"]["liczba"], lex["razem"]["temat"], lex["razem"]["pop00"]["procent"])}.',
        f'- Test {words["lista"]} słów: {_share_text(total["pokryte"], words["lista"], total["procent"])}, '
        f'próg {words["prog"]}: {"spełniony" if words["spelniony"] else "niespełniony"}.',
        f'- Śródlądowe wśród haseł T3 kandydatów: {_share_text(cand["srodladowe"], cand["hasla"], cand["procent"])}.',
        f'- Werdykt automatyczny: {verdict["automatyczny"]} (niespełnione: {failed}). '
        f'Progi z ocen ({", ".join(verdict["czeka_na_ocene"])}): czeka na ocenę.', '',
        '## Kluczowe decyzje',
        '- Wpis to leksem SGJP z formą w STANDARD. Warstwa to najniższa z T1 < T2 < T3; źródła to wszystkie.',
        f'- {POP00_LEKSEMY}. Formy liczymy z POP.txt.gz i POP00.txt.gz.',
        '- Werdykt automatyczny to tylko „dalej” albo „popraw”. „stop” wybiera operator na bramce.', '',
        '## Otwarte pytania',
        '- Trafność warstw i zgodność ocen: czeka na przegląd R2 (agent i operator).',
        f'- Wpisy T3: {n["warstwy"]["T3"]}. Szum pełnego domknięcia T2 oceni przegląd.', '',
        '## Przecięcia z POP i POP00',
        '| Warstwa | Leksemy | w POP | w POP00 (POP0) | Formy | w POP | w POP00 |',
        '|---|---|---|---|---|---|---|']
    for name in GRUPY:
        a, b = lex[name], forms[name]
        lines.append(f'| {name} | {a["temat"]} | {a["pop"]["liczba"]} ({_pl(a["pop"]["procent"])}) '
                     f'| {a["pop00"]["liczba"]} ({_pl(a["pop00"]["procent"])}) | {b["temat"]} '
                     f'| {b["pop"]["liczba"]} ({_pl(b["pop"]["procent"])}) | {b["pop00"]["liczba"]} ({_pl(b["pop00"]["procent"])}) |')
    lines += ['', '## Diagnostyka przed ∩ STANDARD',
              '| Warstwa | Jednostka | Kandydaci | ∩ BROAD | ∩ STANDARD |', '|---|---|---|---|---|']
    for name in GRUPY:
        for kind in ('leksemy', 'formy'):
            row = report['diagnostyka'][name][kind]
            lines.append(f'| {name} | {kind} | {row["kandydaci"]} | {row["broad"]} ({_pl(row["procent_broad"])}) '
                         f'| {row["standard"]} ({_pl(row["procent_standard"])}) |')
    lines += ['', '## Odrzuceni', 'BRAK_LEKSEMU i NIE_JEDNO_SLOWO to lematy; POZA_BROAD i POZA_STANDARD to leksemy.']
    for name in GRUPY:
        for reason, row in report['odrzucone'][name].items():
            extra = f'; w tym ger: {row["ger"]["liczba"]}' if 'ger' in row else ''
            lines.append(f'- {name} {reason}: {row["liczba"]}{extra}. ' + _list(row['przyklady']))
    t2, t3 = report['t2'], report['t3']
    lines += ['', '## Źródła',
              f'- T1: atomy {", ".join(report["t1"]["atomy"])}; leksemy z etykietą: {report["t1"]["leksemy"]}.',
              f'- T2: synsety {t2["synsety"]} (sztuczne {t2["sztuczne"]}), jednostki {t2["jednostki"]}, '
              f'lematy {t2["lematy"]}. Odrzucone: ' +
              '; '.join(f'{k} {v["liczba"]}' for k, v in t2['odrzucone'].items()) + '.',
              f'- T3: hasła z kodem dziedziny {t3["hasla"]}, z terminem PL {t3["hasla_pl"]}, kandydaci '
              f'{t3["hasla_kandydaci"]}; terminy przyjęte {t3["przyjete"]} ({t3["przyjete_rozne"]} różnych).',
              '- T3 termType: ' + _counts(t3['termType']) + '.',
              '- T3 status: ' + _counts(t3['status']) + '.',
              '- T3 odrzucone: ' + '; '.join(f'{r} {v["liczba"]}' for r, v in t3['odrzucone'].items()) + '.',
              '', '## Flaga wieloznaczny']
    for value, row in report['wieloznaczny'].items():
        lines.append(f'- {value}: {row["liczba"]} ({_pl(row["procent"])}). ' + _list(row['przyklady']))
    lines += ['', f'## Test {words["lista"]} słów',
              f'Do progu idzie wynik całości T1 ∪ T2 ∪ T3. T1 oraz T1 ∪ T2 to diagnostyka.']
    for name, title in (('razem', 'całość'), ('T1', 'T1'), ('T1_T2', 'T1 ∪ T2')):
        row = words[name]
        lines.append(f'- {title}: {_share_text(row["pokryte"], words["lista"], row["procent"])}. '
                     f'Brakuje: {", ".join(row["brakujace"]) or "nic"}.')
    entries = inland['wpisy_t3']
    lines += ['', '## Żegluga śródlądowa (T3)',
              f'- Znaczniki PL: {", ".join(inland["znaczniki"]["pl"])}; EN: {", ".join(inland["znaczniki"]["en"])}.',
              f'- Hasła T3 kandydatów (miara główna): {_share_text(cand["srodladowe"], cand["hasla"], cand["procent"])}. '
              + _list(cand['przyklady']),
              f'- Wpisy T3: {_share_text(entries["srodladowe"], entries["wpisy"], entries["procent"])}. '
              + _list(entries['przyklady']),
              '', '## Werdykt',
              f'- Automatyczny: {verdict["automatyczny"]}. Niespełnione progi: {failed}.',
              f'- Czeka na ocenę: {", ".join(verdict["czeka_na_ocene"])}.', '']
    return '\n'.join(lines)


def _list(values):
    return ('Przykłady: ' + ', '.join(values) + '.') if values else 'Brak przykładów.'


def _counts(values):
    return ', '.join(f'{k} {v}' for k, v in values.items()) or 'brak'


def _payload(entry):
    """Dane wpisu do oceny R2 (W11)."""
    return {'key': entry['klucz'], 'lemat': entry['lemat'], 'warstwa': entry['warstwa'],
            'zrodla': list(entry['zrodla']), 'znaczenie': {w: list(v) for w, v in entry['znaczenie'].items()},
            'czesci_mowy': list(entry['czesci_mowy']), 'wieloznaczny': entry['wieloznaczny'],
            'formy': list(entry['formy'][:5]), 'liczba_form': len(entry['formy'])}


def sample(layers, payloads, method):
    """Próba R2 (W11): `min(size, N)` na warstwę przez `quality.sample_strata`.

    Operator: pierwsze `min(operator_per_stratum, N)` wybranych w kolejności rangi (`selected`).
    `items` niesie dane wpisu do `quality.review_template`.
    """
    result = sample_strata({w: list(keys) for w, keys in layers.items()}, method['sampling'])
    per = method['operator_per_stratum']
    result['operator'] = {'per_stratum': per, 'strata': {
        name: [item['key'] for item in stratum['selected'][:per]] for name, stratum in sorted(result['strata'].items())}}
    keys = sorted({item['key'] for stratum in result['strata'].values() for item in stratum['selected']})
    result['items'] = [payloads[k] for k in keys]
    return result


def _tsv_rows(wpisy):
    rows = ['\t'.join(TSV_KOLUMNY)]
    for key, e in wpisy.items():
        cells = (key, e['lemat'], ','.join(e['czesci_mowy']), e['warstwa'], ','.join(e['zrodla']),
                 ' | '.join(f'{w}: {"; ".join(v)}' for w, v in e['znaczenie'].items()),
                 e['wieloznaczny'], str(len(e['formy'])))
        if any('\t' in c or '\n' in c for c in cells):
            raise ValueError('Tabulacja albo nowa linia w wierszu MORZE.tsv: ' + key)
        rows.append('\t'.join(cells))
    return rows


def _write_package(staging, data, sources, cands, built):
    """Pliki pakietu (wzór `pop00._write_package`); zwraca `summary`."""
    topic = data['topic']
    name = topic['id'].upper()
    (staging / 'reports').mkdir()
    (staging / 'tematy').mkdir()
    write_gzip(staging / f'{name}.txt.gz', built['formy'])
    write_gzip(staging / f'{name}.tsv.gz', _tsv_rows(built['wpisy']))
    (staging / 'tematy' / f'{topic["id"]}.json').write_bytes(sources['topic_path'].read_bytes())
    write_json(staging / 'method.json', data['method']['config'])
    report = summary(data, cands, built)
    write_json(staging / 'reports/summary.json', report)
    (staging / 'reports/raport.md').write_text(raport(report), encoding='utf-8')
    payloads = {k: _payload(e) for k, e in built['wpisy'].items()}
    drawn = sample({w: built['warstwy'][w] for w in WARSTWY}, payloads, data['method']['config'])
    # Szablon wiąże hash dokładnych kanonicznych bajtów próbki.
    (staging / 'reports/sample.json').write_text(dumps(drawn), encoding='utf-8')
    evidence = {p: sha256(staging / p) for p in (f'{name}.txt.gz', 'reports/summary.json')}
    review = review_template(drawn, canonical_index_sha256=sha256(staging / f'{name}.tsv.gz'),
                             evidence_sha256=evidence)
    write_json(staging / 'reports/review-template.json', review)
    texts = {k: p.read_text(encoding='utf-8') for k, p in data['texts'].items()}
    (staging / 'ATTRIBUTIONS.md').write_text(data['attribution'].rstrip('\n') + '\n\n' + texts['ATTRIBUTIONS-tematy.md'],
                                             encoding='utf-8')
    if texts['LIMITATIONS.md'].count(ZNACZNIK) != 1:
        raise _bad('LIMITATIONS.md wymaga jednego znacznika ' + ZNACZNIK)
    cand = report['srodladowe']['kandydaci_t3']
    (staging / 'LIMITATIONS.md').write_text(texts['LIMITATIONS.md'].replace(
        ZNACZNIK, _share_text(cand['srodladowe'], cand['hasla'], cand['procent'])), encoding='utf-8')
    (staging / 'TERMS.md').write_text(texts['TERMS.md'], encoding='utf-8')
    files = {p.relative_to(staging).as_posix(): {'sha256': sha256(p), 'bytes': p.stat().st_size}
             for p in sorted(staging.rglob('*')) if p.is_file()}
    refs = data['source']['inputs']
    manifest = {'schema_version': 1, 'kind': KIND, 'package_id': PACKAGE_ID, 'status': 'BUILT',
                'method': METHOD, 'adr': ADR,
                'topic': {'id': topic['id'], 'wersja': topic['wersja'], 'sha256': sources['topic']},
                'config_sha256': sources['config'], 'source_manifest_sha256': sources['manifest'],
                'inputs': data['pins'], 'plwordnet_zip_sha256': refs['plwordnet_zip']['sha256'],
                'iate': {k: refs['iate'][k] for k in ('member', 'last_modified', 'bytes')},
                'code_identity': code_identity(), 'counts': {topic['id']: report['liczby']},
                'overlap': report['przeciecia'], 'files': files}
    write_json(staging / 'release-manifest.json', manifest)
    (staging / 'SHA256SUMS').write_text(''.join(f'{sha256(p)}  {p.relative_to(staging).as_posix()}\n'
                                                for p in sorted(staging.rglob('*')) if p.is_file()), encoding='utf-8')
    return report


def build_package(manifest, config, topic, output_dir):
    """Podkomenda `tematy` (W6), wzór `pop00.build_package`: staging obok celu, rejestr, 0444, bez nadpisania.

    Kody: 2 konfiguracja albo cel w wejściach, 3 piny, 4 dane albo istniejący cel, 5 zmiana wejść.
    """
    target = Path(output_dir).absolute()
    resolved = target.parent.resolve() / target.name
    if os.path.lexists(target):
        raise GeneratorError('Pakiet TEMATY już istnieje; nie nadpisujemy', 4, str(target))
    staging = None
    try:
        source = load_sources(manifest)
        base = Path(manifest).resolve().parent
        protected = [(base / ref['path']).resolve().parent for ref in source['inputs'].values() if 'path' in ref]
        if not target.parent.is_dir() or any(resolved == p or p in resolved.parents for p in protected):
            raise GeneratorError('Cel TEMATY w wejściach albo bez katalogu nadrzędnego', 2, str(target))
        data = check_inputs(manifest, config, topic)
        paths = {k: Path(v).resolve() for k, v in (('manifest', manifest), ('config', config), ('topic', topic))}
        sources = {k: data['registry'][p] for k, p in paths.items()}
        sources['topic_path'] = paths['topic']
        cands = candidates(data)
        built = build_entries(data, cands)
        if not set(built['formy']) <= data['standard']:
            raise GeneratorError('Naruszone MORZE ⊆ STANDARD', 4)
        staging = Path(tempfile.mkdtemp(prefix='.' + target.name + '.staging-', dir=target.parent))
        report = _write_package(staging, data, sources, cands, built)
        confirm_unchanged(data)
        for p in staging.rglob('*'):
            if p.is_file():
                p.chmod(0o444)
        rename_noreplace(staging, target)
        staging = None
        return {**{k: report[k] for k in ('method', 'temat', 'wersja_tematu', 'liczby', 'przeciecia',
                                          'slowa_oczywiste', 'srodladowe', 'werdykt')},
                'output_dir': str(target.resolve()),
                'release_manifest_sha256': sha256(target / 'release-manifest.json')}
    except GeneratorError:
        raise
    except FileExistsError as error:
        raise GeneratorError('Cel TEMATY powstał podczas zapisu; nie nadpisujemy', 4, str(target)) from error
    except (OSError, ValueError, sqlite3.Error, KeyError, TypeError, EOFError) as error:
        raise GeneratorError('Błąd danych TEMATY: ' + str(error), 4) from error
    finally:
        if staging is not None:
            shutil.rmtree(staging)
