"""POP00: zatwierdzona ochrona odmiany i próg form, bez zmiany POP/POP0."""
from collections import Counter, defaultdict
from contextlib import closing
from decimal import Decimal, InvalidOperation
from functools import lru_cache
import csv
import gzip
import hashlib
import os
from pathlib import Path
import shutil
import sqlite3
import tempfile
import unicodedata

from .canonical import dumps, load_json, sha256, write_json
from .export import rename_noreplace
from .inputs import GeneratorError, checked_file
from .quality import sample_strata, review_template
from .run import code_identity
from .sgjp import expand_tag

METHOD = 'pop00-v1'
ADR = 'docs/adr/ADR-009-pop00-v1.md'
SAMPLING = {'version': 'pop00-quality-v1', 'seed': 'literaki-slownik-pop00-v1',
            'size_per_stratum': 30, 'encoding': 'canonical JSON array [seed,stratum,key], UTF-8'}
RULES = frozenset(('by-aglt-nwok-v1', 'documented-spelling-variant-v1',
    'impt-double-particle-v1', 'impt-single-particle-v1', 'mobile-by-host-aglt-v1',
    'mobile-host-by-sequence-v1', 'mobile-source-host-aglt-v1', 'nie-prefix-degree-v2',
    'personal-host-aglt-v1', 'pred-particle-ze-v1', 'preposition-n-source-v1'))
FIELDS = {'N': {'sg', 'pl'}, 'C': {'nom', 'gen', 'dat', 'acc', 'inst', 'loc', 'voc'},
          'G': {'m1', 'm2', 'm3', 'f', 'n'}, 'D': {'pos', 'com', 'sup'},
          'P': {'pri', 'sec', 'ter'}, 'A': {'imperf', 'perf'}, 'Z': {'aff', 'neg'},
          'K': {'col', 'ncol', 'pt'}, 'W': {'wok', 'nwok'}, 'X': {'akc', 'nakc'},
          'R': {'praep', 'npraep'}, 'U': {'congr', 'rec'}, 'B': {'pun', 'npun'},
          'J': {'agl', 'nagl'}}
# Warianty długości pól są jawne. Nieznana cecha nie staje się zwykłą odmianą.
SHAPES = {'subst': ('NCG', 'NCGK'), 'depr': ('NCG',), 'adj': ('NCGD',),
    'adja': ('',), 'adjc': ('',), 'adjp': ('C',), 'adv': ('', 'D'),
    'aglt': ('NPAW',), 'bedzie': ('NPA',), 'brev': ('B',), 'comp': ('',),
    'cond': ('NGPA',), 'conj': ('',), 'fin': ('NPA',), 'frag': ('',),
    'ger': ('NCGAZ',), 'imps': ('A',), 'impt': ('NPA',), 'inf': ('A',),
    'interj': ('',), 'num': ('NCGU', 'NCGUK'), 'numcomp': ('',),
    'pact': ('NCGAZ',), 'pacta': ('',), 'pant': ('A',), 'part': ('', 'W'),
    'pcon': ('A',), 'ppas': ('NCGAZ',), 'ppron12': ('NCGP', 'NCGPX'),
    'ppron3': ('NCGPXR',), 'praet': ('NGA', 'NGPA', 'NGAJ', 'NGPAJ'),
    'pred': ('',), 'prep': ('C', 'CW'), 'siebie': ('C',), 'winien': ('NGA', 'NGPA')}
INPUTS = ('base_pop', 'base_run', 'database', 'standard', 'orth')
DIAGNOSTIC = frozenset('kot kotach kotem czytam czytasz czytaj czytajcie czytając czytany '
    'czytanymi czytanie zrobiłem zrobiłam byłem byłam zrobiliśmy zrobiłbym remontowałoś '
    'przeczytałobym zrobiwszy najmilszy najmilszemu miłemu mili miłymi lepszy lepszemu '
    'nieczytanie nieczytaniami czytajże bym byś byśmy byście'.split())


def load_config(path):
    value = load_json(path)
    expected = {'version': METHOD, 'adr': ADR, 'ipm_min': '0.1', 'sampling': SAMPLING}
    if value != expected:
        raise GeneratorError('Konfiguracja spoza zatwierdzonej metody pop00-v1', 2)
    return value


def load_sources(path):
    source = load_json(path)
    if (not isinstance(source, dict) or set(source) != {'schema_version', 'version', 'inputs'}
            or type(source['schema_version']) is not int or source['schema_version'] != 1
            or source['version'] != 'pop00-sources-v1' or not isinstance(source['inputs'], dict)
            or set(source['inputs']) != set(INPUTS)
            or any(not isinstance(ref, dict) or set(ref) != {'path', 'sha256'}
                   or not isinstance(ref['path'], str) for ref in source['inputs'].values())):
        raise GeneratorError('Nieprawidłowy manifest wejść POP00', 2)
    return source


@lru_cache(maxsize=8192)
def classify_analysis(tag, rule=None):
    if rule is not None and rule not in RULES:
        raise GeneratorError('Nieznana reguła konstrukcji POP00: ' + str(rule), 4)
    groups = set()
    for expanded in expand_tag(tag):
        pos, *fields = expanded.split(':')
        if pos not in SHAPES or not any(len(shape) == len(fields) and
                all(value in FIELDS[kind] for value, kind in zip(fields, shape))
                for shape in SHAPES.get(pos, ())):
            raise GeneratorError('Nieobsługiwany tag POP00: ' + expanded, 4)
        if ((rule == 'by-aglt-nwok-v1' and pos != 'aglt') or
                (rule == 'nie-prefix-degree-v2' and pos not in ('adj', 'adv'))):
            raise GeneratorError('Tag niezgodny z regułą POP00: ' + expanded, 4)
        if 'n' in fields and ({'pri', 'sec'} & set(fields)):
            group = 'neuter-person-1-2'
        elif rule == 'by-aglt-nwok-v1':
            group = 'ordinary'
        elif rule and rule != 'nie-prefix-degree-v2':
            group = 'construction'
        elif pos in ('pact', 'ppas', 'pant', 'pacta', 'adja', 'adjp'):
            group = pos
        elif pos == 'ger' and 'neg' in fields:
            group = 'negative-gerund'
        elif pos in ('adj', 'adv') and {'com', 'sup'} & set(fields):
            group = 'degree-com-sup'
        else:
            group = 'ordinary'
        groups.add(group)
    return tuple(sorted(groups))


def read_words(path):
    data = gzip.decompress(Path(path).read_bytes()) if str(path).endswith('.gz') else Path(path).read_bytes()
    text = data.decode('utf-8')
    words = text.splitlines()
    if (not words or not text.endswith('\n') or '\r' in text or words != sorted(set(words))
            or any(not w or w != w.lower() or w != unicodedata.normalize('NFC', w)
                   or not w.isalpha() or not 2 <= len(w) <= 15 for w in words)):
        raise GeneratorError('Niekanoniczna lista wejściowa POP00', 4, str(path))
    return set(words)


def read_orth(path):
    result = {}
    with gzip.open(path, 'rt', encoding='utf-8', newline='') as stream:
        reader = csv.DictReader(stream)
        if not reader.fieldnames or not {'', 'ipm', 'freq'} <= set(reader.fieldnames):
            raise GeneratorError('Brak kolumn KWJP orth/all', 4)
        for row in reader:
            word = row['']
            try:
                ipm, freq = Decimal(row['ipm']), Decimal(row['freq'])
            except (InvalidOperation, TypeError) as error:
                raise GeneratorError('Nieprawidłowa miara KWJP', 4) from error
            if (not word or word in result or not ipm.is_finite() or ipm < 0
                    or not freq.is_finite() or freq < 0 or freq != freq.to_integral_value()):
                raise GeneratorError('Nieprawidłowy lub powtórzony wiersz KWJP', 4)
            result[word] = {'ipm': str(ipm), 'freq': int(freq)}
    return result


def package_file(root, manifest, name):
    meta = manifest.get('files', {}).get(name, {})
    path = root / name
    if path.is_symlink() or not path.is_file() or sha256(path) != meta.get('sha256'):
        raise GeneratorError('Niezgodny plik pakietu: ' + name, 3)
    return path


def check_inputs(path):
    path = Path(path).resolve()
    source = load_sources(path)
    paths = {k: checked_file(path.parent, source['inputs'][k]) for k in INPUTS}
    run, pop = load_json(paths['base_run']), load_json(paths['base_pop'])
    if run.get('readiness') != 'FROZEN':
        raise GeneratorError('Przebieg POP00 nie jest FROZEN', 5)
    pins = {k: source['inputs'][k]['sha256'] for k in INPUTS}
    if (pop.get('kind') != 'literaki-pop-manifest' or pop.get('method') != 'pop-v3'
            or pop.get('package_id') != 'POP' or pop.get('status') != 'BUILT'
            or pop.get('inputs', {}).get('database_sha256') != pins['database']
            or pop.get('inputs', {}).get('standard_sha256') != pins['standard']
            or run.get('verification', {}).get('database_sha256') != pins['database']
            or run.get('export', {}).get('release_manifest_sha256') !=
               pop.get('inputs', {}).get('release_manifest_sha256')):
        raise GeneratorError('Niezgodna podstawa POP0/LL-PL', 3)
    root = paths['base_pop'].parent
    pop0_path = package_file(root, pop, 'POP0.txt.gz')
    units_path = package_file(root, pop, 'reports/units.json')
    attribution = package_file(root, pop, 'ATTRIBUTIONS.md')
    units = load_json(units_path)
    members = {m for row in units['units'] for m in row['members_in'].get('POP0', [])}
    if not members or any(not isinstance(m, str) or m.count('@') != 1 for m in members):
        raise GeneratorError('Nieprawidłowi właściciele POP0', 4)
    pop0, standard = read_words(pop0_path), read_words(paths['standard'])
    if not pop0 <= standard:
        raise GeneratorError('POP0 nie jest podzbiorem STANDARD', 4)
    # Orth musi być właśnie listą all tego samego zamrożonego przebiegu.
    artifacts = run.get('inputs', {}).get('artifacts', [])
    if sum(a.get('kind') == 'kwjp_orth' and a.get('genre') == 'all'
           and a.get('sha256') == pins['orth'] for a in artifacts) != 1:
        raise GeneratorError('Orth/all spoza przypiętego przebiegu', 3)
    return {'paths': paths, 'pins': pins, 'source_sha256': sha256(path),
            'pop0': pop0, 'standard': standard, 'members': members,
            'orth': read_orth(paths['orth']), 'attribution': attribution.read_text(encoding='utf-8'),
            'base_files': {root/name: pop['files'][name]['sha256'] for name in
                           ('POP0.txt.gz', 'reports/units.json', 'ATTRIBUTIONS.md')}}


def read_analyses(database, pop0, members):
    with closing(sqlite3.connect(Path(database).as_uri() + '?mode=ro', uri=True)) as db:
        ids = {i: lemma + '@' + source for i, source, lemma in
               db.execute('select id,source_id,lemma_id from lexeme') if lemma + '@' + source in members}
        if set(ids.values()) != members:
            raise GeneratorError('Brak wybranych leksemów w bazie POP00', 4)
        ordered = sorted(ids)
        for offset in range(0, len(ordered), 400):
            chunk = ordered[offset:offset + 400]
            query = ('select i.lexeme_id,s.game_key,s.original,i.tag,i.names,i.qualifiers,i.first_row '
                     'from interpretation i join surface_form s on s.id=i.form_id '
                     'where i.lexeme_id in (' + ','.join('?' * len(chunk)) + ')')
            for ident, word, original, tag, names, qualifiers, first in db.execute(query, chunk):
                if word in pop0:
                    member = ids[ident]
                    stable = hashlib.sha256(dumps([member, first, original, tag, names, qualifiers]).encode()).hexdigest()
                    yield word, {'id': 'source:' + stable, 'member': member, 'tag': tag, 'rule': None}
        query = ("select c.game_key,c.lemma_id,c.expanded_tag,p.source_id,c.rule_id,c.candidate_key "
                 "from derivation_candidate c join derivation_component p on p.candidate_key=c.candidate_key "
                 "where p.kind='source_interpretation'")
        for word, lemma, tag, source, rule, key in db.execute(query):
            member = lemma + '@' + source
            if member in members and word in pop0:
                yield word, {'id': 'construction:' + key, 'member': member, 'tag': tag, 'rule': rule}


def select_forms(pop0, members, analyses, orth, config):
    rows = defaultdict(dict)
    owners = defaultdict(set)
    minimum = Decimal(config['ipm_min'])
    for word, item in analyses:
        if word not in pop0 or item['member'] not in members:
            raise GeneratorError('Analiza spoza podstawy POP0', 4)
        groups = classify_analysis(item['tag'], item['rule'])
        evidence = orth.get(word)
        observed = evidence is not None and Decimal(evidence['ipm']) >= minimum
        kept = ('ordinary' in groups or (bool(set(groups) - {'neuter-person-1-2'}) and observed))
        record = {**item, 'groups': list(groups), 'kept': kept}
        key = item['member'], item['id']
        if key in rows[word] and rows[word][key] != record:
            raise GeneratorError('Sprzeczny identyfikator analizy POP00', 4)
        rows[word][key] = record
        if kept:
            owners[item['member']].add(word)
    if set(rows) != pop0:
        raise GeneratorError('Niepełne pokrycie form POP0 analizami', 4)
    lost = sorted(m for m in members if not owners[m])
    if lost:
        raise GeneratorError('POP00 usuwa całe leksemy: ' + ', '.join(lost[:20]), 4)
    decisions, result = {}, set()
    for word in sorted(rows):
        items = [rows[word][key] for key in sorted(rows[word])]
        kept = any(a['kept'] for a in items)
        if kept:
            result.add(word)
        decisions[word] = {'kept': kept, 'evidence':
            {'status': 'OBSERVED' if word in orth else 'NO_PUBLISHED_EVIDENCE',
             'ipm': orth[word]['ipm'] if word in orth else None}, 'analyses': items}
    return result, decisions


def summary(pop0, result, members, decisions, orth):
    observed = sum(orth.get(w, {}).get('freq', 0) for w in pop0)
    retained = sum(orth.get(w, {}).get('freq', 0) for w in result)
    published = sum(v['freq'] for w, v in orth.items() if w == w.lower())
    groups = Counter()
    for row in decisions.values():
        groups.update({g for a in row['analyses'] for g in a['groups']})
    return {'method': METHOD, 'ipm_min': '0.1', 'forms': len(result), 'base_forms': len(pop0),
            'removed_forms': len(pop0 - result), 'selected_lexemes': len(members), 'lost_lexemes': 0,
            'lengths': dict(sorted(Counter(map(len, result)).items())), 'groups_overlapping': dict(sorted(groups.items())),
            'coverage': {'observed_pop0_tokens': observed, 'retained_tokens': retained,
                         'published_lowercase_tokens': published,
                         'observed_pop0_pct': 100 * retained / observed if observed else None,
                         'published_lowercase_pct': 100 * retained / published if published else None,
                         'scope': 'opublikowane małoliterowe tokeny orth/all; nie znajomość ani grywalność'}}


def _strata(decisions):
    strata = defaultdict(list)
    for word, row in decisions.items():
        if word in DIAGNOSTIC:
            continue
        outcome = 'kept' if row['kept'] else 'removed'
        groups = {g for a in row['analyses'] for g in a['groups']}
        for g in sorted(groups):
            strata[g + '-' + outcome].append(word)
        if row['evidence']['ipm'] is None:
            strata['no-published-evidence-' + outcome].append(word)
        elif Decimal('0.08') <= Decimal(row['evidence']['ipm']) <= Decimal('0.12'):
            strata['threshold-' + outcome].append(word)
        if len(word) <= 3 or len(word) >= 12:
            strata[('short-' if len(word) <= 3 else 'long-') + outcome].append(word)
        if len(row['analyses']) > 1:
            strata['alternative-analyses-' + outcome].append(word)
    # Puste warstwy pozostają jawne, a nie są dowodem pokrycia.
    for name in ('ordinary', 'neuter-person-1-2', 'construction', 'pact', 'ppas', 'pant', 'pacta',
                 'adja', 'adjp', 'negative-gerund', 'degree-com-sup', 'no-published-evidence',
                 'threshold', 'short', 'long', 'alternative-analyses'):
        for outcome in ('kept', 'removed'):
            strata.setdefault(name + '-' + outcome, [])
    return dict(strata)


def _write_package(staging, data, config, config_sha, result, decisions):
    from .pop import _write_gzip
    (staging / 'reports').mkdir()
    _write_gzip(staging / 'POP00.txt.gz', sorted(result))
    write_json(staging / 'method.json', config)
    write_json(staging / 'reports/decisions.json', decisions)
    report = summary(data['pop0'], result, data['members'], decisions, data['orth'])
    write_json(staging / 'reports/summary.json', report)
    sample = sample_strata(_strata(decisions), config['sampling'])
    # Szablon wiąże hash dokładnych kanonicznych bajtów próbki.
    (staging / 'reports/sample.json').write_text(dumps(sample), encoding='utf-8')
    evidence = {p: sha256(staging / p) for p in ('POP00.txt.gz', 'reports/summary.json')}
    review = review_template(sample, canonical_index_sha256=sha256(staging / 'reports/decisions.json'),
                             evidence_sha256=evidence)
    write_json(staging / 'reports/review-template.json', review)
    (staging / 'ATTRIBUTIONS.md').write_text(data['attribution'] +
        '\n## POP00\nWybór leksemów odziedziczono z POP0 (KWJP i NKJP). '
        'Nałożono ochronę odmiany i próg form KWJP; nie dołączono surowych danych NKJP.\n', encoding='utf-8')
    (staging / 'TERMS.md').write_text('# Warunki POP00\n\nFormy SGJP: BSD-2-Clause z pełnym '
        'zawiadomieniem w ATTRIBUTIONS.md. KWJP: CC BY 4.0. Wybór leksemów dziedziczy warunki '
        'NKJP wskazane w ATTRIBUTIONS.md. Własne raporty: CC BY 4.0; kod: BSD-2-Clause. '
        'Projekt nie deklaruje wyłącznych praw do wyboru słów.\n', encoding='utf-8')
    (staging / 'LIMITATIONS.md').write_text('# Ograniczenia POP00\n\nBUILT nie oznacza odbioru '
        'ani wydania. Nie przeprowadzono badania rozpoznawalności przez graczy ani partii. '
        'Próg 0,1 IPM i grupy fleksji są pierwszą polityką, nie granicą znajomości. '
        'Odziedziczono wybór leksemów i regułę (i) POP0. Korpus jest pisany; brak wiersza '
        'nie jest częstością zero. Usuwane bywają poprawne i zrozumiałe rzadkie odmiany. '
        'Próbka jest niezależna od przykładów diagnostycznych, ale jest przeglądem technicznym, '
        'nie badaniem graczy. Słownik znajomości nie zmienia walidatora stołu.\n', encoding='utf-8')
    files = {p.relative_to(staging).as_posix(): {'sha256': sha256(p), 'bytes': p.stat().st_size}
             for p in sorted(staging.rglob('*')) if p.is_file()}
    manifest = {'schema_version': 1, 'kind': 'literaki-pop00-manifest', 'package_id': 'POP00',
                'status': 'BUILT', 'method': METHOD, 'adr': ADR, 'config_sha256': config_sha,
                'source_manifest_sha256': data['source_sha256'], 'inputs': data['pins'],
                'code_identity': code_identity(), 'counts': {k: report[k] for k in
                    ('forms', 'base_forms', 'removed_forms', 'selected_lexemes', 'lost_lexemes')},
                'files': files}
    write_json(staging / 'release-manifest.json', manifest)
    (staging / 'SHA256SUMS').write_text(''.join(f'{sha256(p)}  {p.relative_to(staging).as_posix()}\n'
        for p in sorted(staging.rglob('*')) if p.is_file()), encoding='utf-8')
    return report


def confirm_unchanged(data):
    if (any(sha256(data['paths'][k]) != data['pins'][k] for k in INPUTS)
            or any(sha256(p) != expected for p,expected in data['base_files'].items())):
        raise GeneratorError('Wejścia POP00 zmieniły się podczas operacji', 5)


def build_package(manifest, config, output_dir):
    target = Path(output_dir).absolute()
    resolved = target.parent.resolve() / target.name
    if os.path.lexists(target):
        raise GeneratorError('Pakiet POP00 już istnieje; nie nadpisujemy', 4)
    staging = None
    try:
        source = load_sources(manifest)
        protected = [(Path(manifest).resolve().parent / ref['path']).resolve().parent
                     for ref in source['inputs'].values()]
        if not target.parent.is_dir() or any(resolved == p or p in resolved.parents for p in protected):
            raise GeneratorError('Cel POP00 w wejściach albo bez katalogu nadrzędnego', 2)
        settings = load_config(config)
        config_sha = sha256(config)
        data = check_inputs(manifest)
        result, decisions = select_forms(data['pop0'], data['members'],
            read_analyses(data['paths']['database'], data['pop0'], data['members']), data['orth'], settings)
        if not result <= data['pop0'] <= data['standard']:
            raise GeneratorError('Naruszone POP00 ⊆ POP0 ⊆ STANDARD', 4)
        staging = Path(tempfile.mkdtemp(prefix='.' + target.name + '.staging-', dir=target.parent))
        report = _write_package(staging, data, settings, config_sha, result, decisions)
        confirm_unchanged(data)
        if sha256(config) != config_sha or sha256(manifest) != data['source_sha256']:
            raise GeneratorError('Konfiguracja POP00 zmieniła się podczas operacji', 5)
        for p in staging.rglob('*'):
            if p.is_file():
                p.chmod(0o444)
        rename_noreplace(staging, target)
        staging = None
        return {**report, 'output_dir': str(target.resolve()),
                'release_manifest_sha256': sha256(target / 'release-manifest.json')}
    except GeneratorError:
        raise
    except FileExistsError as error:
        raise GeneratorError('Cel POP00 powstał podczas zapisu; nie nadpisujemy', 4) from error
    except (sqlite3.Error, ValueError, KeyError, TypeError, EOFError) as error:
        raise GeneratorError('Błąd danych POP00: ' + str(error), 4) from error
    finally:
        if staging is not None:
            shutil.rmtree(staging)


def explain_pop00(package, run_dir, word):
    try:
        return _explain_pop00(package, run_dir, word)
    except GeneratorError:
        raise
    except (ValueError, KeyError, TypeError, EOFError) as error:
        raise GeneratorError('Uszkodzona diagnostyka POP00: ' + str(error), 4) from error


def _explain_pop00(package, run_dir, word):
    package, run_dir = Path(package), Path(run_dir)
    manifest = load_json(package / 'release-manifest.json')
    if (manifest.get('kind') != 'literaki-pop00-manifest' or manifest.get('method') != METHOD
            or manifest.get('inputs', {}).get('base_run') != sha256(run_dir / 'manifest.json')):
        raise GeneratorError('Pakiet POP00 nie odpowiada przebiegowi', 3)
    if load_json(run_dir / 'manifest.json').get('readiness') != 'FROZEN':
        raise GeneratorError('Przebieg nie jest FROZEN', 5)
    load_config(package_file(package, manifest, 'method.json'))
    decisions = load_json(package_file(package, manifest, 'reports/decisions.json'))
    selected = read_words(package_file(package, manifest, 'POP00.txt.gz'))
    key = unicodedata.normalize('NFC', word).lower()
    row = decisions.get(key)
    if row is not None and row['kept'] != (key in selected):
        raise GeneratorError('Sprzeczny wynik diagnostyki POP00', 4)
    return {'word': key, 'method': METHOD, 'in_pop0': row is not None, 'in_pop00': key in selected,
            'reason': 'NOT_IN_POP0' if row is None else ('IN_POP00' if row['kept'] else 'FORM_FILTERED'),
            'decision': row}


def format_pop00_explanation(value):
    row = value['decision']
    lines = [f"{value['word']}: {value['reason']} ({METHOD})"]
    if row:
        lines.append('KWJP: ' + row['evidence']['status'] + '; IPM=' + str(row['evidence']['ipm']))
        for analysis in row['analyses']:
            lines.append(analysis['member'] + ' ' + analysis['tag'] + ': ' +
                         ', '.join(analysis['groups']) + (' — zostaje' if analysis['kept'] else ' — odpada'))
    return '\n'.join(lines)
