"""TEMATY: listy tematyczne z etykiet SGJP, Słowosieci i IATE (#11, ADR-010)."""
from contextlib import closing
from fractions import Fraction
from pathlib import Path
from urllib.parse import quote
import re
import sqlite3

from .canonical import load_json, sha256
from .inputs import GeneratorError, checked_file
from .pop00 import package_file, read_words
from .quality import _config

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


def _plwordnet_meta(path, zip_sha):
    try:
        with closing(sqlite3.connect('file:' + quote(str(path)) + '?mode=ro', uri=True)) as db:
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
