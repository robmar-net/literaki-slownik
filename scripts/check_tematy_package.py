#!/usr/bin/env python3
"""Niezależny odbiór pakietu TEMATY (#11 W12, #12 W7; ADR-010, ADR-012) i przeglądu R2 (`--review`).

Bez importu literaki_slownik. Wymaga jawnego manifestu wejść i konfiguracji metody.
Formy wpisów i przecięcia z POP/POP00 liczy od nowa z przypiętych wejść.
Pakiety `tematy-v1` sprawdza checker z `a633136` (ADR-012).
"""
import argparse
from collections import Counter
from contextlib import closing
from fractions import Fraction
import gzip
import hashlib
import json
from pathlib import Path
from urllib.parse import quote
import re
import sqlite3
import stat
import sys
import unicodedata

METHOD = 'tematy-v2'
ADR = 'docs/adr/ADR-012-tematy-fala-1.md'
KIND = 'literaki-tematy-manifest'
REVIEW_KIND = 'literaki-tematy-review'
# D: ręczne dodatki z pliku tematu; po T3, poza próbą R2 (ADR-010, poprawka 2026-10-29).
WARSTWY = ('T1', 'T2', 'T3', 'D')
PROBA = ('T1', 'T2', 'T3')
GRUPY = (*WARSTWY, 'razem')
OCENY = ('tak', 'nie', 'niepewne')
WIELOZNACZNY = ('tak', 'nie', 'brak_danych')
# Kopia `tematy.TSV_KOLUMNY` (bez importu).
TSV_KOLUMNY = ('klucz', 'lemat', 'czesci_mowy', 'warstwa', 'zrodla', 'znaczenie', 'wieloznaczny', 'formy')
INPUTS = ('base_run', 'database', 'release_manifest', 'standard', 'broad',
          'base_pop', 'base_pop00', 'plwordnet_db', 'iate')
PROGI = ('slowa_oczywiste', 't1_tak', 't2_tak', 't2_nie', 't3_tak', 'zgodnosc')
# Próg z ocen R2 → jego warstwa (#12 W6). Kopia `tematy.PROG_WARSTWA` (bez importu).
PROG_WARSTWA = {'t1_tak': 'T1', 't2_tak': 'T2', 't2_nie': 'T2', 't3_tak': 'T3'}
NIE_DOTYCZY = 'nie_dotyczy'
# Kolumny danych redaktorów, których nie wolno mieć przypiętej pochodnej Słowosieci.
ZAKAZANE_KOLUMNY = {'owner', 'comment', 'error_comment'}
FRACTION = re.compile(r'0\.[0-9]+|1\.0+|[0-9]+/[1-9][0-9]*')
HEX = re.compile('[0-9a-f]{64}')
CHUNK = 400


class Refused(Exception):
    def __init__(self, message, code=4):
        super().__init__(message)
        self.code = code


def require(condition, message, code=4):
    if not condition:
        raise Refused(message, code)


def digest(path):
    with open(path, 'rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def encoded(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()


def read(path):
    def unique(pairs):
        out = {}
        for k, v in pairs:
            require(k not in out, 'Powtórzony klucz JSON')
            out[k] = v
        return out
    return json.loads(Path(path).read_text(encoding='utf-8'), object_pairs_hook=unique,
                      parse_constant=lambda v: (_ for _ in ()).throw(Refused('Nieskończona liczba JSON')))


def text(path):
    path = Path(path)
    data = path.read_bytes()
    return (gzip.decompress(data) if path.suffix == '.gz' else data).decode('utf-8')


def words(path):
    content = text(path)
    rows = content.splitlines()
    require(bool(rows) and content.endswith('\n') and '\r' not in content and rows == sorted(set(rows)),
            'Niekanoniczna lista słów: ' + Path(path).name)
    require(all(w == w.lower() == unicodedata.normalize('NFC', w) and w.isalpha() and
                2 <= len(w) <= 15 for w in rows), 'Zły zapis słowa: ' + Path(path).name)
    return set(rows)


def share(value):
    require(isinstance(value, str) and FRACTION.fullmatch(value), 'Zły próg: ' + repr(value), 2)
    result = Fraction(value)
    require(0 <= result <= 1, 'Próg poza [0, 1]: ' + value, 2)
    return result


def pct(part, whole):
    """Jak `tematy._pct`: jedno miejsce po kropce z dokładnego ułamka; None przy zerze."""
    return None if not whole else f'{float(Fraction(100 * part, whole)):.1f}'


def required_files(topic_id):
    name = topic_id.upper()
    return {f'{name}.txt.gz', f'{name}.tsv.gz', f'tematy/{topic_id}.json', 'method.json',
            'reports/summary.json', 'reports/raport.md', 'reports/sample.json',
            'reports/review-template.json', 'ATTRIBUTIONS.md', 'LIMITATIONS.md', 'TERMS.md',
            'release-manifest.json', 'SHA256SUMS'}


def files(root, manifest):
    """Zestaw plików, 0444, manifest, SHA256SUMS, gzip bez nazwy i czasu."""
    required = required_files(manifest['topic']['id'])
    actual = set()
    for p in root.rglob('*'):
        require(not p.is_symlink() and (p.is_file() or p.is_dir()), 'Niedozwolony wpis pakietu')
        if p.is_file():
            actual.add(p.relative_to(root).as_posix())
            require(stat.S_IMODE(p.stat().st_mode) == 0o444, 'Pakiet nie jest tylko do odczytu')
    require(actual == required, 'Zestaw plików pakietu TEMATY różny od kontraktu')
    meta = manifest['files']
    require(set(meta) == required - {'SHA256SUMS', 'release-manifest.json'}, 'Niepełny zakres manifestu')
    for name in sorted(meta):
        require(meta[name] == {'sha256': digest(root/name), 'bytes': (root/name).stat().st_size},
                'Niezgodny manifest pliku ' + name)
    expected = ''.join(f'{digest(root/name)}  {name}\n' for name in sorted(required - {'SHA256SUMS'}))
    require((root/'SHA256SUMS').read_text(encoding='utf-8') == expected, 'Niezgodne SHA256SUMS')
    for name in sorted(n for n in required if n.endswith('.gz')):
        head = (root/name).read_bytes()[:10]
        require(len(head) == 10 and head[:2] == b'\x1f\x8b' and head[3] == 0 and head[4:8] == b'\0'*4,
                'Gzip z nazwą, czasem lub dodatkowymi flagami: ' + name)


def tsv(root, topic_id):
    """Wiersze `<TEMAT>.tsv.gz`: klucz → pola; leksem w jednej warstwie."""
    content = text(root/f'{topic_id.upper()}.tsv.gz')
    lines = content.splitlines()
    require(content.endswith('\n') and '\r' not in content, 'Zły koniec wiersza TSV')
    require(lines and tuple(lines[0].split('\t')) == TSV_KOLUMNY, 'Złe kolumny TSV')
    rows, keys = {}, []
    for line in lines[1:]:
        cells = line.split('\t')
        require(len(cells) == len(TSV_KOLUMNY), 'Zły wiersz TSV')
        row = dict(zip(TSV_KOLUMNY, cells))
        key = row['klucz']
        require(key not in rows, 'Leksem w dwóch warstwach albo powtórzony: ' + key)
        zrodla = row['zrodla'].split(',')
        require(key.count('@') == 1 and all(key.split('@')), 'Zły klucz leksemu: ' + key)
        require(set(zrodla) <= set(WARSTWY) and zrodla == sorted(set(zrodla), key=WARSTWY.index)
                and row['warstwa'] == zrodla[0] and ('D' not in zrodla or zrodla == ['D']),
                'Zła warstwa albo źródła: ' + key)
        require(row['wieloznaczny'] in WIELOZNACZNY and row['formy'].isdigit() and int(row['formy']) > 0,
                'Złe pole wiersza TSV: ' + key)
        rows[key] = row
        keys.append(key)
    require(keys == sorted(keys), 'Wiersze TSV nie są posortowane')
    return rows


def _readonly(path):
    return closing(sqlite3.connect('file:' + quote(str(path)) + '?mode=ro', uri=True))


def recount_forms(database, keys, standard):
    """Formy leksemów z bazy przebiegu (interpretacje i konstrukcje) ∩ STANDARD, od nowa."""
    wanted = {tuple(k.split('@')) for k in keys}  # (lemma_id, source_id)
    forms = {k: set() for k in keys}
    with _readonly(database) as db:
        ids = {i: f'{lemma}@{source}' for i, source, lemma in db.execute('SELECT id, source_id, lemma_id FROM lexeme')
               if (lemma, source) in wanted}
        require(set(ids.values()) == set(keys), 'Brak leksemów TSV w bazie przebiegu')
        ordered = sorted(ids)
        for start in range(0, len(ordered), CHUNK):
            chunk = ordered[start:start + CHUNK]
            for ident, word in db.execute('SELECT i.lexeme_id, s.game_key FROM interpretation i JOIN surface_form s '
                                          'ON s.id = i.form_id WHERE i.lexeme_id IN (' + ','.join('?' * len(chunk)) + ')',
                                          chunk):
                forms[ids[ident]].add(word)
        for word, lemma, source in db.execute(
                'SELECT c.game_key, c.lemma_id, p.source_id FROM derivation_candidate c JOIN derivation_component p '
                "ON p.candidate_key = c.candidate_key WHERE p.kind = 'source_interpretation'"):
            key = f'{lemma}@{source}'
            if key in forms:
                forms[key].add(word)
    return {k: v & standard for k, v in forms.items()}


def plwordnet_schema(path):
    """Pochodna Słowosieci bez kolumn redaktorów (D6)."""
    with _readonly(path) as db:
        tables = [r[0] for r in db.execute("SELECT name FROM sqlite_master WHERE type = 'table'")]
        require(tables, 'Pusta pochodna Słowosieci')
        for table in tables:
            columns = {r[1].lower() for r in db.execute('PRAGMA table_info("' + table.replace('"', '""') + '")')}
            require(not columns & ZAKAZANE_KOLUMNY, 'Pochodna Słowosieci ma dane redaktorów: ' + table)


def members(units, name):
    out = {m for row in units['units'] for m in row['members_in'].get(name, [])}
    require(bool(out) and all(isinstance(m, str) and m.count('@') == 1 for m in out), 'Zli członkowie ' + name)
    return out


def overlap(rows, forms, base):
    """Przecięcia z POP i POP00 jak w W8: leksemy (POP, POP0) i formy (POP.txt.gz, POP00.txt.gz)."""
    lex, out_forms = {}, {}
    for name in GRUPY:
        keys = {k for k, r in rows.items() if name == 'razem' or r['warstwa'] == name}
        found = set().union(*(forms[k] for k in keys)) if keys else set()

        def part(n, whole):
            return {'liczba': n, 'procent': pct(n, whole)}
        lex[name] = {'temat': len(keys), 'pop': part(len(keys & base['POP']), len(keys)),
                     'pop00': part(len(keys & base['POP0']), len(keys))}
        out_forms[name] = {'temat': len(found), 'pop': part(len(found & base['pop']), len(found)),
                           'pop00': part(len(found & base['pop00']), len(found))}
    return {'leksemy': lex, 'formy': out_forms}


def addenda(topic, rows):
    """Warstwa D = dodatki tematu (górne `dodatki`, #12 W1): jeden wiersz na dodatek, `znaczenie` `D: <powód>`."""
    expected = sorted((d['lemat'], 'D: ' + d['powód']) for d in topic['dodatki'])
    found = sorted((r['lemat'], r['znaczenie']) for r in rows.values() if r['warstwa'] == 'D')
    require(found == expected, 'Warstwa D różna od dodatków tematu')


def exclusions(topic, rows, report):
    """Wykluczenia lematów (#12 W3): żaden wiersz TSV nie ma lematu (kolumna `lemat` = `lemma_base`) i klasy
    z `wykluczenia` tematu; `summary.json` wymienia te same wykluczenia."""
    pairs = {(w['lemat'], w['czesc_mowy']) for w in topic['wykluczenia']}
    for key, row in rows.items():
        hit = sorted(c for c in row['czesci_mowy'].split(',') if (row['lemat'], c) in pairs)
        require(not hit, f'Wiersz TSV z wykluczonym lematem: {key} ({row["lemat"]}, {", ".join(hit)})')
    require([(w['lemat'], w['czesc_mowy'], w['powód']) for w in report['wykluczenia']]
            == [(w['lemat'], w['czesc_mowy'], w['powód']) for w in topic['wykluczenia']],
            'Wykluczenia raportu różne od tematu')


def obvious_words(topic, rows):
    """Test 37 słów, wynik całości: słowo pokryte, gdy ma je lemat wpisu."""
    lista = topic['diagnostyka']['slowa_oczywiste']
    lemmas = {r['lemat'] for r in rows.values()}
    missing = [w for w in lista if w not in lemmas]
    return {'lista': len(lista), 'pokryte': len(lista) - len(missing), 'brakujace': missing}


def sampling_digest(seed, stratum, key):
    return hashlib.sha256(encoded([seed, stratum, key])).hexdigest()


def check_sample(root, rows, config, list_name):
    """Próba `min(size, N)` na warstwę i operator `min(per, N)`; szablon związany z próbą i TSV."""
    sampling, per = config['sampling'], config['operator_per_stratum']
    sample = read(root/'reports/sample.json')
    require(sample['status'] == 'UNREVIEWED' and sample['schema_version'] == 1
            and all(sample[k] == v for k, v in sampling.items()), 'Zły stan lub metoda próby')
    require(set(sample['strata']) == set(PROBA), 'Próba ma inne warstwy niż T1, T2, T3')
    membership = {}
    for name in PROBA:
        population = sorted(k for k, r in rows.items() if r['warstwa'] == name)
        ranked = sorted((sampling_digest(sampling['seed'], name, k), k) for k in population)[:sampling['size_per_stratum']]
        expected = [{'key': k, 'sha256': d} for d, k in ranked]
        require(sample['strata'][name] == {'population': len(population), 'sample_size': len(expected),
                                           'coverage': 'SAMPLED_NOT_VERIFIED' if population else 'EMPTY_NOT_COVERAGE',
                                           'selected': expected}, 'Zmieniona próba ' + name)
        for item in expected:
            require(item['key'] not in membership, 'Leksem w dwóch warstwach próby: ' + item['key'])
            membership[item['key']] = name
    require(sample['unique_selected_units'] == len(membership) and sample['overlaps'] == [],
            'Zły licznik albo przecięcia próby')
    # Operator: tylko warstwy `operator_warstwy` (#12 W5, W7).
    operator = {name: [i['key'] for i in sample['strata'][name]['selected'][:per]]
                for name in PROBA if name in config['operator_warstwy']}
    require(sample['operator'] == {'per_stratum': per, 'strata': operator}, 'Zła próba operatora')
    items = sample['items']
    require([i.get('key') for i in items] == sorted(membership), 'Złe dane pozycji próby')
    for item in items:
        row = rows[item['key']]
        require(item['lemat'] == row['lemat'] and item['warstwa'] == row['warstwa']
                and item['zrodla'] == row['zrodla'].split(',') and item['liczba_form'] == int(row['formy']),
                'Dane pozycji próby różne od TSV: ' + item['key'])
    template = read(root/'reports/review-template.json')
    require(template['status'] == 'UNREVIEWED' and template['schema_version'] == 1
            and template['version'] == sample['version']
            and template['sample_sha256'] == digest(root/'reports/sample.json')
            and template['canonical_index_sha256'] == digest(root/f'{list_name}.tsv.gz')
            and template['evidence_sha256'] == {n: digest(root/n) for n in (f'{list_name}.txt.gz', 'reports/summary.json')},
            'Niepowiązany szablon przeglądu')
    by_key = {i['key']: i for i in items}
    require(template['items'] == [{'key': k, 'strata': [membership[k]], 'assessment': None, 'reviewer': None,
                                   'source_justification': None, 'selected_unit': by_key[k]}
                                  for k in sorted(membership)], 'Zmieniony szablon przeglądu')
    return {'sample': sample, 'template': template, 'membership': membership, 'operator': operator,
            'populacje': {name: sample['strata'][name]['population'] for name in PROBA}}


def load_config(path):
    config = read(path)
    require(isinstance(config, dict) and config.get('version') == METHOD and config.get('adr') == ADR
            and set(config) == {'version', 'adr', 'sampling', 'operator_per_stratum', 'operator_warstwy', 'progi',
                                'czesci_mowy', 't3_klasy', 'teksty'}
            and isinstance(config['operator_warstwy'], list) and config['operator_warstwy']
            and all(w in PROBA for w in config['operator_warstwy'])
            and len(set(config['operator_warstwy'])) == len(config['operator_warstwy'])
            and isinstance(config['progi'], dict) and set(config['progi']) == set(PROGI)
            and type(config['operator_per_stratum']) is int
            and 0 < config['operator_per_stratum'] <= config['sampling']['size_per_stratum'], 'Zła metoda', 2)
    for key in PROGI:
        share(config['progi'][key])
    return config


def check(root, source_path, config_path, review_path=None):
    """Pakiet (W12); z `review_path` także przegląd R2. Zwraca raport; odmowa to `Refused`."""
    root, source_path, config_path = Path(root), Path(source_path).resolve(), Path(config_path).resolve()
    manifest, source, config = read(root/'release-manifest.json'), read(source_path), load_config(config_path)
    require(manifest.get('kind') == KIND and manifest.get('package_id') == 'TEMATY'
            and manifest.get('status') == 'BUILT' and manifest.get('method') == METHOD
            and manifest.get('adr') == ADR, 'Zły format TEMATY')
    require(manifest['config_sha256'] == digest(config_path) and manifest['source_manifest_sha256'] == digest(source_path),
            'Piny konfiguracji', 3)
    # Manifest wejść nadal przypina IATE (#12 W2, D6); od `t3` zależy tylko porównanie pinów.
    require(source.get('version') == 'tematy-sources-v1' and source.get('schema_version') == 1
            and set(source['inputs']) == set(INPUTS) | {'plwordnet_zip'}, 'Zły manifest wejść')
    require(isinstance(manifest.get('topic', {}).get('id'), str)
            and re.fullmatch('[a-z]+', manifest['topic']['id']), 'Zły identyfikator tematu')
    topic_id = manifest['topic']['id']
    topic_path = root/f'tematy/{topic_id}.json'
    require(digest(topic_path) == manifest['topic']['sha256'], 'Plik tematu różny od pinu', 3)
    topic = read(topic_path)
    require(topic['id'] == topic_id and topic['wersja'] == manifest['topic']['wersja'], 'Zły temat')
    t3 = 't3' in topic
    used = tuple(k for k in INPUTS if k != 'iate' or t3)
    paths = {k: (source_path.parent/source['inputs'][k]['path']).resolve() for k in used}
    pins = {k: source['inputs'][k]['sha256'] for k in used}
    require(manifest['inputs'] == pins and all(p.is_file() and digest(p) == pins[k] for k, p in paths.items()),
            'Piny wejść', 3)
    iate = {k: source['inputs']['iate'][k] for k in ('member', 'last_modified', 'bytes')} if t3 else None
    require(manifest.get('iate') == iate, 'Blok iate manifestu niezgodny z tematem', 3)
    files(root, manifest)
    require(read(root/'method.json') == config, 'Zła metoda pakietu')

    standard = words(paths['standard'])
    listed = words(root/f'{topic_id.upper()}.txt.gz')
    require(listed <= standard, f'Naruszone {topic_id.upper()} ⊆ STANDARD')
    rows = tsv(root, topic_id)
    require(t3 or not any(r['warstwa'] == 'T3' for r in rows.values()), 'Warstwa T3 w temacie bez t3')
    addenda(topic, rows)
    forms = recount_forms(paths['database'], rows, standard)
    for key, row in rows.items():
        require(forms[key] and len(forms[key]) == int(row['formy']), 'Liczba form TSV różna od bazy: ' + key)
    require(set().union(*forms.values()) == listed if forms else not listed, 'TSV niespójny z listą TXT')

    pop, pop00 = read(paths['base_pop']), read(paths['base_pop00'])
    for manifest_path, value, names in ((paths['base_pop'], pop, ('POP.txt.gz', 'reports/units.json')),
                                        (paths['base_pop00'], pop00, ('POP00.txt.gz',))):
        for name in names:
            require(digest(manifest_path.parent/name) == value['files'][name]['sha256'], 'Zmieniony plik ' + name, 3)
    units = read(paths['base_pop'].parent/'reports/units.json')
    base = {'POP': members(units, 'POP'), 'POP0': members(units, 'POP0'),
            'pop': words(paths['base_pop'].parent/'POP.txt.gz'), 'pop00': words(paths['base_pop00'].parent/'POP00.txt.gz')}
    plwordnet_schema(paths['plwordnet_db'])

    report = read(root/'reports/summary.json')
    exclusions(topic, rows, report)
    counted = {'warstwy': {w: sum(r['warstwa'] == w for r in rows.values()) for w in WARSTWY},
               'wpisy': len(rows), 'formy': len(listed)}
    require(all(report['liczby'][k] == v for k, v in counted.items())
            and manifest['counts'] == {topic_id: report['liczby']}, 'Niezgodne liczniki')
    recounted = overlap(rows, forms, base)
    require({k: report['przeciecia'][k] for k in ('leksemy', 'formy')} == recounted
            and manifest['overlap'] == report['przeciecia'], 'Niezgodne przecięcia z POP/POP00')
    obvious = obvious_words(topic, rows)
    total = report['slowa_oczywiste']['razem']
    require(report['slowa_oczywiste']['lista'] == obvious['lista'] and total['pokryte'] == obvious['pokryte']
            and total['brakujace'] == obvious['brakujace'], 'Niezgodny test słów oczywistych')
    drawn = check_sample(root, rows, config, topic_id.upper())

    result = {'status': 'pass', 'temat': topic_id, **counted, 'slowa_oczywiste': obvious,
              'sha256sums_sha256': digest(root/'SHA256SUMS'), 'review_checked': review_path is not None}
    if review_path is not None:
        result['przeglad'] = check_review(read(review_path), root, config, drawn, obvious, t3)
    require(all(digest(p) == pins[k] for k, p in paths.items()) and digest(source_path) == manifest['source_manifest_sha256']
            and digest(config_path) == manifest['config_sha256'], 'Wejścia zmieniły się podczas kontroli', 5)
    files(root, manifest)
    return result


# --- Przegląd R2 (W11, ADR-010 „Przegląd” i „Bramka”) ---

def ratings_sha256(items):
    """Hash ocen: kanoniczny JSON listy pozycji posortowanej po kluczu."""
    return hashlib.sha256(encoded(sorted(items, key=lambda i: i['key']))).hexdigest()


def binding(review, root):
    """Powiązanie pliku przeglądu z pakietem: SHA256SUMS i próba."""
    template = read(root/'reports/review-template.json')
    require(review.get('kind') == REVIEW_KIND and review.get('schema_version') == 1, 'Zły format przeglądu')
    for field in ('sample_sha256', 'canonical_index_sha256', 'evidence_sha256', 'version'):
        require(review.get(field) == template[field], 'Przegląd niepowiązany z próbą: ' + field)
    require(review.get('sha256sums_sha256') == digest(root/'SHA256SUMS'), 'Przegląd innego pakietu (SHA256SUMS)')
    return template


def agent_items(review, membership):
    """Oceny agenta: pełna próba, ocena z trzech, powód; hash zgodny z zapisanym."""
    agent = review.get('agent')
    require(isinstance(agent, dict) and isinstance(agent.get('items'), list), 'Brak ocen agenta')
    items = agent['items']
    require([i.get('key') for i in items] == sorted(membership), 'Oceny agenta: brak albo obce pozycje')
    for item in items:
        require(set(item) == {'key', 'warstwa', 'ocena', 'powod'} and item['warstwa'] == membership[item['key']]
                and item['ocena'] in OCENY and isinstance(item['powod'], str) and item['powod'].strip(),
                'Nierozstrzygnięta ocena agenta: ' + str(item.get('key')))
    require(HEX.fullmatch(str(review.get('agent_sha256'))) and review['agent_sha256'] == ratings_sha256(items),
            'Hash ocen agenta różny od ocen')
    return {i['key']: i['ocena'] for i in items}


def operator_items(review, operator):
    """Oceny operatora: dokładnie jego próba (`sample.operator`), ocena z trzech."""
    part = review.get('operator')
    if part is None:
        return None
    expected = {k: w for w, keys in operator.items() for k in keys}
    require(isinstance(part, dict) and part.get('agent_sha256') == review['agent_sha256'],
            'Oceny operatora bez hasha ocen agenta')
    items = part.get('items')
    require(isinstance(items, list) and [i.get('key') for i in items] == sorted(expected),
            'Oceny operatora: brak albo obce pozycje')
    for item in items:
        require(set(item) == {'key', 'warstwa', 'ocena'} and item['warstwa'] == expected[item['key']]
                and item['ocena'] in OCENY, 'Zła ocena operatora: ' + str(item.get('key')))
    return {i['key']: i['ocena'] for i in items}


def fraction_text(value):
    return None if value is None else str(value)


def accuracy(ratings, layer_of):
    """Trafność na warstwę: „tak”/N i „nie”/N, N = rzeczywista liczba ocen; „niepewne” to ani „tak”, ani „nie”."""
    out = {}
    for name in PROBA:
        values = [r for k, r in ratings.items() if layer_of[k] == name]
        n, count = len(values), Counter(values)
        out[name] = {'N': n, **{o: count[o] for o in OCENY},
                     'tak_udzial': fraction_text(Fraction(count['tak'], n) if n else None),
                     'nie_udzial': fraction_text(Fraction(count['nie'], n) if n else None)}
    return out


def agreement(first, second):
    """Zgodność i kappa Cohena (3 kategorie) na pozycjach ocenionych przez obu."""
    keys = sorted(set(first) & set(second))
    n = len(keys)
    if not n:
        return {'N': 0, 'zgodnosc': None, 'kappa': None}
    observed = Fraction(sum(first[k] == second[k] for k in keys), n)
    a, b = Counter(first[k] for k in keys), Counter(second[k] for k in keys)
    expected = sum(Fraction(a[c] * b[c], n * n) for c in OCENY)
    kappa = None if expected == 1 else (observed - expected) / (1 - expected)
    return {'N': n, 'zgodnosc': str(observed), 'kappa': fraction_text(kappa), 'oczekiwana': str(expected)}


def verdict(progi, miary):
    """Werdykt „dalej” albo „popraw” (ADR-010 „Bramka”). „stop” wybiera tylko operator.

    `miary`: próg → Fraction, None (pusta N: nie spełnia), `czeka` (na ocenę operatora) albo
    `nie_dotyczy` (#12 W6: `t3_tak` tematu bez `t3`; nie blokuje „dalej”). `t2_nie` to górna granica.
    """
    rows, failed, pending, skipped = [], [], [], []
    for key in PROGI:
        value = miary[key]
        limit = share(progi[key])
        if value == 'czeka':
            status = 'czeka'
            pending.append(key)
        elif value == NIE_DOTYCZY:
            status = NIE_DOTYCZY
            skipped.append(key)
        elif value is None:
            status = 'niespelniony'
        else:
            status = 'spelniony' if (value <= limit if key == 't2_nie' else value >= limit) else 'niespelniony'
        if status == 'niespelniony':
            failed.append(key)
        rows.append({'prog': key, 'granica': progi[key], 'kierunek': '<=' if key == 't2_nie' else '>=',
                     'wartosc': value if value in ('czeka', NIE_DOTYCZY, None) else str(value), 'status': status})
    wynik = 'popraw' if failed else None if pending else 'dalej'
    return {'wynik': wynik, 'progi': rows, 'niespelnione': failed, 'czeka_na_ocene': pending,
            'nie_dotyczy': skipped, 'uwaga': '„stop” wybiera tylko operator na bramce'}


def check_review(review, root, config, drawn, obvious, t3=True):
    """Werdykt R2 (#12 W6): próg warstwy z `operator_warstwy` z ocen operatora (bez nich `czeka`),
    pozostałych warstw z ocen agenta, zawsze. Bez `t3`: `t3_tak` nie dotyczy; z `t3` i pustą T3:
    niespełniony. Zgodność i kappa na pozycjach ocenionych przez obu."""
    binding(review, root)
    membership, operator = drawn['membership'], drawn['operator']
    agent = agent_items(review, membership)
    human = operator_items(review, operator)
    own = config['operator_warstwy']
    by_agent = accuracy(agent, membership)
    layers = None if human is None else accuracy(human, membership)
    agreed = None if human is None else agreement(agent, human)
    result = {'agent_sha256': review['agent_sha256'], 'agent': by_agent, 'operator': layers, 'zgodnosc': agreed}
    whole = Fraction(obvious['pokryte'], obvious['lista'])
    field = {'t1_tak': 'tak_udzial', 't2_tak': 'tak_udzial', 't2_nie': 'nie_udzial', 't3_tak': 'tak_udzial'}
    miary = {'slowa_oczywiste': whole}
    for key, name in PROG_WARSTWA.items():
        source = (layers if name in own else by_agent)
        if key == 't3_tak' and not t3:
            miary[key] = NIE_DOTYCZY
        elif not drawn['populacje'][name]:
            miary[key] = None  # pusta warstwa (np. T3 przy `t3`): błąd konfiguracji, nie „czeka”
        elif source is None:
            miary[key] = 'czeka'
        else:
            value = source[name][field[key]]
            miary[key] = None if value is None else Fraction(value)
    miary['zgodnosc'] = ('czeka' if agreed is None else
                         None if agreed['zgodnosc'] is None else Fraction(agreed['zgodnosc']))
    result['slowa_oczywiste'] = {**obvious, 'udzial': str(whole)}
    result['werdykt'] = verdict(config['progi'], miary)
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--package-dir', required=True)
    parser.add_argument('--manifest', required=True)
    parser.add_argument('--config', required=True)
    parser.add_argument('--review')
    args = parser.parse_args(argv)
    try:
        report = check(args.package_dir, args.manifest, args.config, args.review)
        print(json.dumps(report, ensure_ascii=False, sort_keys=True, indent=2))
        return 0
    except Refused as error:
        print(str(error), file=sys.stderr)
        return error.code
    except (OSError, ValueError, KeyError, TypeError, sqlite3.Error, EOFError) as error:
        print('Nieprawidłowy pakiet TEMATY: ' + str(error), file=sys.stderr)
        return 4


if __name__ == '__main__':
    sys.exit(main())
