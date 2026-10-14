"""Zatwierdzone wyjątki dawności STANDARD (#4): dokładne analizy, nie napisy.

Plik `config/generator/standard-age-exceptions.json` jest zwykłym wejściem pipeline,
przypiętym w `sources.json`. Każda pozycja wskazuje jeden rekord importu (źródło,
wiersz, oryginał, lemat, tag, nazwy, kwalifikatory) albo jeden zapisany kandydat
konstrukcji. Walidator odmawia całego pliku przy pierwszej niezgodności; nie ma
częściowego dopuszczenia.

Klucz analizy jest ten sam co w `decisions.materialize_assessments()`:
- źródło: sha256(dumps(['source', rekord, rozwinięty_tag])),
- konstrukcja: sha256(dumps(['construction', candidate_key])).
"""
import hashlib
import json
import re
import unicodedata
from pathlib import Path

from .canonical import dumps, load_json
from .inputs import GeneratorError, checked_file, inspect_sources
from .sgjp import expand_tag

CONFIG_KEY = 'standard-age-exceptions'
SCHEMA_VERSION = 1
OVERRIDDEN_RULE = 'linguistic-historical-form-v1'
SHA = re.compile('[0-9a-f]{64}')
TOP = ('schema_version', 'decision_version', 'description', 'overrides_rule', 'source_snapshot',
       'sources', 'provenance', 'expected_counts', 'families', 'cases')
SNAPSHOT = ('run', 'database_sha256', 'policy_version', 'matches_per_analysis')
# Klucze kandydatów wyliczone kodem nowszej reguły; w bazie migawki ich nie ma.
SNAPSHOT_OPTIONAL = ('recomputed_constructions',)
RECOMPUTED = ('replaces', 'analyses', 'note')
PROVENANCE = ('research_task', 'approval', 'inputs')
COUNTS = ('words', 'analyses', 'source_analyses', 'construction_analyses', 'families')
FAMILY = ('family', 'lemma_id', 'status', 'scope', 'meaning_note', 'confidence',
          'reader_article_ids', 'kwjp_documents', 'evidence')
FAMILY_OPTIONAL = ('forms', 'exclude_pos')
EVIDENCE_KINDS = {'kwjp_review': {'kind', 'word', 'url'}, 'primary_dictionary_or_author': {'kind', 'url'},
                  'dictionary_review': {'kind', 'path'}}
RECORD = ('source_id', 'first_source_row', 'original', 'lemma_id', 'raw_tag', 'names', 'qualifiers')
SOURCE = ('kind', 'family', 'proof', 'reader_word', *RECORD, 'tag')
CONSTRUCTION = ('kind', 'family', 'proof', 'candidate_key', 'rule_id', 'original', 'lemma_id', 'tag',
                'names', 'qualifiers', 'components')
COMPONENT = ('source_id', 'first_source_row', 'original', 'raw_tag')
SOURCE_PROOFS = {'reader_exact', 'negative_in_pinned_analysis', 'superlative_in_pinned_analysis'}
CONSTRUCTION_PROOFS = {'existing_qualified_construction'}


def refuse(message, where=None):
    raise GeneratorError(f'Wyjątki dawności STANDARD: {message}', 4, CONFIG_KEY, where)


def game_key(text):
    return unicodedata.normalize('NFC', unicodedata.normalize('NFC', text).lower())


def keys(value, required, optional=(), where=None):
    if not isinstance(value, dict) or not set(required) <= set(value) or set(value) - set(required) - set(optional):
        refuse('nieznane lub brakujące pola', where)


def text(value, where, empty=False):
    if not isinstance(value, str) or (not empty and not value.strip()):
        refuse('wymagany napis', where)
    return value


def texts(value, where):
    if not isinstance(value, list) or not value or len(set(value)) != len(value):
        refuse('wymagana niepusta lista bez powtórzeń', where)
    for item in value:
        text(item, where)
    return value


def sha(value, where):
    if not isinstance(value, str) or not SHA.fullmatch(value):
        refuse('nieprawidłowy SHA256', where)
    return value


def analysis_key(entry):
    """Klucz zapisanej analizy, zgodny z `materialize_assessments()`."""
    if entry['kind'] == 'source':
        return hashlib.sha256(dumps(['source', {k: entry[k] for k in RECORD}, entry['tag']]).encode()).hexdigest()
    return hashlib.sha256(dumps(['construction', entry['candidate_key']]).encode()).hexdigest()


def order(entry):
    return (entry['kind'], entry['lemma_id'], entry['tag'], entry.get('source_id', ''),
            entry.get('first_source_row', 0), entry.get('candidate_key', ''))


def checked_family(family):
    where = family.get('family') if isinstance(family, dict) else None
    keys(family, FAMILY, FAMILY_OPTIONAL, where)
    text(family['family'], where)
    if family['lemma_id'] != family['family']:
        refuse('rodzina jest identyfikowana swoim lematem', where)
    if family['status'] not in {'propose', 'limited'} or (family['status'] == 'limited') != ('forms' in family):
        refuse('rodzina limited wymaga listy form, propose jej nie ma', where)
    for field in ('scope', 'meaning_note', 'confidence'):
        text(family[field], where)
    if 'forms' in family:
        texts(family['forms'], where)
        if any(game_key(form) != form for form in family['forms']):
            refuse('formy rodziny wymagają normalizacji gry', where)
    if 'exclude_pos' in family:
        texts(family['exclude_pos'], where)
    ids = family['reader_article_ids']
    if (not isinstance(ids, list) or not ids or any(type(i) is not int or i <= 0 for i in ids)
            or ids != sorted(set(ids))):
        refuse('wymagane rosnące ID artykułów czytnika', where)
    if texts(family['kwjp_documents'], where) != sorted(family['kwjp_documents']) or len(family['kwjp_documents']) < 2:
        refuse('wymagane co najmniej dwa uporządkowane dokumenty KWJP', where)
    if not isinstance(family['evidence'], list) or not family['evidence']:
        refuse('brak dowodu rodziny', where)
    for item in family['evidence']:
        if not isinstance(item, dict) or set(item) != EVIDENCE_KINDS.get(item.get('kind'), {None}):
            refuse('nieznany rodzaj dowodu rodziny', where)
        for field in item.values():
            text(field, where)


def checked_entry(entry, word, families, hashes):
    kind = entry.get('kind') if isinstance(entry, dict) else None
    if kind == 'source':
        keys(entry, SOURCE, where=word)
        if entry['proof'] not in SOURCE_PROOFS:
            refuse('nieznany dowód analizy źródłowej', word)
        text(entry['reader_word'], word)
        if type(entry['first_source_row']) is not int or entry['first_source_row'] <= 0:
            refuse('nieprawidłowy wiersz źródła', word)
        for field in ('source_id', 'original', 'lemma_id', 'raw_tag', 'tag'):
            text(entry[field], word)
        for field in ('names', 'qualifiers'):
            text(entry[field], word, empty=True)
        try:
            expanded = set(expand_tag(entry['raw_tag']))
        except GeneratorError:
            expanded = set()
        if entry['tag'] not in expanded:
            refuse('tag spoza rozwinięcia rekordu', word)
        sources = {entry['source_id']}
    elif kind == 'construction':
        keys(entry, CONSTRUCTION, where=word)
        if entry['proof'] not in CONSTRUCTION_PROOFS:
            refuse('nieznany dowód konstrukcji', word)
        sha(entry['candidate_key'], word)
        for field in ('rule_id', 'original', 'lemma_id', 'tag'):
            text(entry[field], word)
        for field in ('names', 'qualifiers'):
            text(entry[field], word, empty=True)
        if '.' in entry['tag']:
            refuse('konstrukcja wymaga rozwiniętego tagu', word)
        components = entry['components']
        if not isinstance(components, list) or not components:
            refuse('konstrukcja bez składników', word)
        for component in components:
            keys(component, COMPONENT, where=word)
            if type(component['first_source_row']) is not int or component['first_source_row'] <= 0:
                refuse('nieprawidłowy wiersz składnika', word)
            for field in ('source_id', 'original', 'raw_tag'):
                text(component[field], word)
        sources = {c['source_id'] for c in components}
    else:
        refuse('nieznany rodzaj analizy', word)
    text(entry['family'], word)
    if game_key(entry['original']) != word:
        refuse('forma analizy poza napisem przypadku', word)
    family = families.get(entry['family'])
    if family is None:
        refuse('analiza bez zatwierdzonej rodziny', word)
    if entry['lemma_id'] != family['lemma_id']:
        refuse('obcy lemat względem rodziny', word)
    if 'forms' in family and word not in family['forms']:
        refuse('forma poza zakresem rodziny', word)
    if entry['tag'].split(':')[0] in family.get('exclude_pos', ()):
        refuse('część mowy wyłączona z rodziny', word)
    for sid in sources:
        if sid not in hashes:
            refuse('źródło bez przypiętego hasha', word)
    return sources


def validate(config, *, source_hashes):
    """Pełna kontrola pliku; zwraca mapę klucz analizy → pozycja albo odmawia całości."""
    keys(config, TOP)
    if type(config['schema_version']) is not int or config['schema_version'] != SCHEMA_VERSION:
        refuse('nieobsługiwana wersja schematu')
    text(config['decision_version'], None)
    text(config['description'], None)
    if config['overrides_rule'] != OVERRIDDEN_RULE:
        refuse('wyjątek uchyla tylko odmowę dawności')
    snapshot = config['source_snapshot']
    keys(snapshot, SNAPSHOT, SNAPSHOT_OPTIONAL, where='source_snapshot')
    recomputed = snapshot.get('recomputed_constructions', {})
    if not isinstance(recomputed, dict):
        refuse('nieprawidłowy opis przeliczonych konstrukcji', 'source_snapshot')
    for rule, item in recomputed.items():
        keys(item, RECOMPUTED, where=rule)
        text(item['replaces'], rule)
        text(item['note'], rule)
        if type(item['analyses']) is not int or item['analyses'] <= 0 or item['replaces'] == rule:
            refuse('nieprawidłowy opis przeliczonych konstrukcji', rule)
    text(snapshot['run'], 'source_snapshot')
    text(snapshot['policy_version'], 'source_snapshot')
    sha(snapshot['database_sha256'], 'source_snapshot')
    if not isinstance(snapshot['matches_per_analysis'], dict):
        refuse('wymagany rozkład dopasowań audytu', 'source_snapshot')
    provenance = config['provenance']
    keys(provenance, PROVENANCE, where='provenance')
    text(provenance['research_task'], 'provenance')
    text(provenance['approval'], 'provenance')
    if not isinstance(provenance['inputs'], dict) or not provenance['inputs']:
        refuse('brak hashy wejść badania', 'provenance')
    for name, value in provenance['inputs'].items():
        text(name, 'provenance')
        sha(value, name)
    hashes = config['sources']
    if not isinstance(hashes, dict) or not hashes:
        refuse('brak hashy źródeł')
    for sid, value in hashes.items():
        if source_hashes.get(sid) != sha(value, sid):
            refuse('hash źródła niezgodny z przypiętym importem', sid)
    families = config['families']
    if not isinstance(families, list) or not families:
        refuse('brak rodzin')
    for family in families:
        checked_family(family)
    names = [f['family'] for f in families]
    if names != sorted(set(names)):
        refuse('rodziny wymagają rosnącej kolejności bez powtórzeń')
    families = {f['family']: f for f in families}
    cases = config['cases']
    if not isinstance(cases, list) or not cases:
        refuse('brak przypadków')
    words = [c.get('word') if isinstance(c, dict) else None for c in cases]
    if any(not isinstance(w, str) for w in words) or words != sorted(set(words)):
        refuse('przypadki wymagają rosnącej kolejności bez powtórzeń')
    analyses, used_families, used_sources = {}, set(), set()
    for case in cases:
        word = case['word']
        keys(case, ('word', 'analyses'), where=word)
        if not word or game_key(word) != word:
            refuse('napis przypadku wymaga normalizacji gry', word)
        entries = case['analyses']
        if not isinstance(entries, list) or not entries:
            refuse('przypadek bez analiz', word)
        for entry in entries:
            used_sources |= checked_entry(entry, word, families, hashes)
            used_families.add(entry['family'])
        ordered = [order(e) for e in entries]
        if ordered != sorted(set(ordered)):
            refuse('analizy przypadku wymagają rosnącej kolejności bez powtórzeń', word)
        for entry in entries:
            key = analysis_key(entry)
            if key in analyses:
                refuse('powtórzona analiza', word)
            analyses[key] = {'word': word, **entry}
    if used_families != set(families):
        refuse('rodzina bez przypadków', ', '.join(sorted(set(families) - used_families)))
    if used_sources != set(hashes):
        refuse('nieużywany hash źródła')
    counts = {'words': len(cases), 'analyses': len(analyses),
              'source_analyses': sum(e['kind'] == 'source' for e in analyses.values()),
              'construction_analyses': sum(e['kind'] == 'construction' for e in analyses.values()),
              'families': len(families)}
    expected = config['expected_counts']
    keys(expected, COUNTS, where='expected_counts')
    if expected != counts:
        refuse(f'liczby niezgodne z expected_counts: {counts}', 'expected_counts')
    for rule, item in recomputed.items():
        used = [e for e in analyses.values() if e['kind'] == 'construction' and e['rule_id'] in (rule, item['replaces'])]
        if len(used) != item['analyses'] or any(e['rule_id'] != rule for e in used):
            refuse('liczba przeliczonych konstrukcji niezgodna z opisem', rule)
    return {'decision_version': config['decision_version'], 'counts': counts,
            'sources': dict(hashes), 'families': families, 'recomputed_rules': sorted(recomputed),
            'analyses': analyses}


def decision_for(loaded, entry):
    """Ślad decyzji do `decision_payload`: wersja, rodzina, rodzaj dowodu i dowód rodziny."""
    family = loaded['families'][entry['family']]
    return {'decision_version': loaded['decision_version'], 'word': entry['word'], 'family': entry['family'],
            'proof': entry['proof'], 'confidence': family['confidence'],
            'reader_article_ids': family['reader_article_ids'], 'kwjp_documents': family['kwjp_documents'],
            'family_evidence': family['evidence']}


def load(path, *, source_hashes):
    try:
        config = load_json(path)
    except (OSError, ValueError) as error:
        raise GeneratorError(f'Nie można odczytać wyjątków dawności STANDARD: {error}', 4, str(path)) from error
    return validate(config, source_hashes=source_hashes)


def from_manifest(manifest_path):
    """Wczytaj plik przez `configurations` manifestu; zmiana bez nowego hasha przerywa."""
    inputs = inspect_sources(manifest_path)
    reference = inputs['manifest']['configurations'].get(CONFIG_KEY)
    if reference is None:
        raise GeneratorError('Manifest nie przypina wyjątków dawności STANDARD', 4, CONFIG_KEY)
    path = checked_file(Path(inputs['manifest_path']).parent, reference)
    return load(path, source_hashes={a['source_id']: a['sha256'] for a in inputs['artifacts']})


def check_database(db, loaded, *, analyses=True, allow_missing_recomputed=False):
    """Każda pozycja ma dokładnie swój rekord w bazie przebiegu; `analyses` wymaga też zapisanej analizy.

    `allow_missing_recomputed` służy tylko kontroli starej migawki: kandydat reguły z
    `recomputed_constructions` może nie istnieć, o ile baza nie ma żadnego kandydata tej reguły
    (powstała przed nią). W nowym przebiegu reguła ma kandydatów, więc brak klucza przerywa.
    """
    stored = {sid: json.loads(metadata).get('sha256') for sid, metadata in
              db.execute('select source_id,metadata from source_artifact')}
    for sid, value in loaded['sources'].items():
        if stored.get(sid) != value:
            refuse('hash źródła bazy niezgodny z plikiem', sid)
    record = '''select i.id,f.original,l.lemma_id,i.tag,i.names,i.qualifiers
        from surface_form f join interpretation i on i.form_id=f.id join lexeme l on l.id=i.lexeme_id
        where f.original=? and i.source_id=? and i.first_row=?'''
    matched, missing = 0, {}
    absent_rules = {rule for rule in loaded.get('recomputed_rules', ()) if allow_missing_recomputed and not
                    db.execute('select 1 from derivation_candidate where rule_id=? limit 1', (rule,)).fetchone()}
    for key, entry in loaded['analyses'].items():
        word = entry['word']
        if entry['kind'] == 'source':
            rows = db.execute(record, (entry['original'], entry['source_id'], entry['first_source_row'])).fetchall()
            if len(rows) != 1 or rows[0][1:] != tuple(entry[k] for k in ('original', 'lemma_id', 'raw_tag', 'names', 'qualifiers')):
                refuse('brak dokładnego rekordu importu', word)
            expected = (rows[0][0], None, entry['tag'], word)
        else:
            row = db.execute('''select rule_id,original,game_key,lemma_id,expanded_tag,names,qualifiers,payload
                from derivation_candidate where candidate_key=?''', (entry['candidate_key'],)).fetchone()
            if row is None and entry['rule_id'] in absent_rules:
                missing[entry['rule_id']] = missing.get(entry['rule_id'], 0) + 1
                continue
            if row is None or row[:7] != (entry['rule_id'], entry['original'], word, entry['lemma_id'],
                                          entry['tag'], entry['names'], entry['qualifiers']):
                refuse('brak kandydata konstrukcji o tym kluczu', word)
            parts = [p['interpretation'] for p in json.loads(row[7])['components'] if p['kind'] == 'source_interpretation']
            relations = db.execute('''select source_id,source_row from derivation_component
                where candidate_key=? and kind='source_interpretation' order by position''', (entry['candidate_key'],)).fetchall()
            if ([{k: p[k] for k in COMPONENT} for p in parts] != entry['components']
                    or relations != [(c['source_id'], c['first_source_row']) for c in entry['components']]):
                refuse('składniki konstrukcji niezgodne z plikiem', word)
            expected = (None, entry['candidate_key'], entry['tag'], word)
        if analyses:
            row = db.execute('select interpretation_id,candidate_key,expanded_tag,game_key from analysis where analysis_key=?',
                             (key,)).fetchone()
            if row != expected:
                refuse('brak zapisanej analizy o tym kluczu', word)
        matched += 1
    result = {'matched_analyses': matched, 'words': loaded['counts']['words']}
    if allow_missing_recomputed:
        result['expected_missing_recomputed'] = missing
    return result


def render(config):
    """Deterministyczny zapis do ręcznej edycji: jedna analiza w wierszu."""
    def line(value):
        return json.dumps(value, ensure_ascii=False, allow_nan=False)
    parts = ['{']
    fields = list(config)
    for index, field in enumerate(fields):
        tail = ',' if index < len(fields) - 1 else ''
        value = config[field]
        if field == 'families':
            rows = [f'    {line(f)}' for f in value]
            parts.append(f'  "families": [\n' + ',\n'.join(rows) + f'\n  ]{tail}')
        elif field == 'cases':
            rows = []
            for case in value:
                inner = ',\n'.join(f'      {line(e)}' for e in case['analyses'])
                head = {k: v for k, v in case.items() if k != 'analyses'}
                rows.append('    ' + line(head)[:-1] + ', "analyses": [\n' + inner + '\n    ]}')
            parts.append('  "cases": [\n' + ',\n'.join(rows) + f'\n  ]{tail}')
        else:
            body = json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False).replace('\n', '\n  ')
            parts.append(f'  {line(field)}: {body}{tail}')
    parts.append('}')
    return '\n'.join(parts) + '\n'
