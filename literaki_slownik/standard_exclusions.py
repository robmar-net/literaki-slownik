"""Zatwierdzone wykluczenia STANDARD (#15): dokładne analizy, nie napisy.

Plik `config/generator/standard-exclusions.json` jest zwykłym wejściem pipeline,
przypiętym w `sources.json`. Każda pozycja wskazuje jeden rekord importu (źródło,
wiersz, oryginał, lemat, tag, nazwy, kwalifikatory) i jedno rozwinięcie tagu.
Wykluczenie tylko odrzuca w STANDARD; BROAD bez zmian. Walidator odmawia całego
pliku przy pierwszej niezgodności.

Kształt i klucz analizy jak w `standard_age_exceptions` (#4); tam wyjątek uchyla
odmowę, tu wpis dodaje odmowę. Dlatego osobny plik i osobna reguła.
"""
import json
import re
from pathlib import Path

from .canonical import load_json
from .inputs import GeneratorError, checked_file, inspect_sources
from .sgjp import expand_tag
from .standard_age_exceptions import RECORD, analysis_key, game_key, render  # noqa: F401 (render: zapis pliku)

CONFIG_KEY = 'standard-exclusions'
SCHEMA_VERSION = 1
RULE = 'linguistic-standard-no-polish-meaning-v1'
SHA = re.compile('[0-9a-f]{64}')
TOP = ('schema_version', 'decision_version', 'description', 'rule_id', 'source_snapshot',
       'sources', 'provenance', 'expected_counts', 'cases')
SNAPSHOT = ('run', 'policy_version')
PROVENANCE = ('issue', 'research_task', 'approval', 'inputs')
COUNTS = ('words', 'analyses')
SOURCE = ('kind', 'reason', *RECORD, 'tag')


def refuse(message, where=None):
    raise GeneratorError(f'Wykluczenia STANDARD: {message}', 4, CONFIG_KEY, where)


def keys(value, required, where=None):
    if not isinstance(value, dict) or set(value) != set(required):
        refuse('nieznane lub brakujące pola', where)


def text(value, where, empty=False):
    if not isinstance(value, str) or (not empty and not value.strip()):
        refuse('wymagany napis', where)
    return value


def sha(value, where):
    if not isinstance(value, str) or not SHA.fullmatch(value):
        refuse('nieprawidłowy SHA256', where)
    return value


def order(entry):
    return (entry['lemma_id'], entry['tag'], entry['source_id'], entry['first_source_row'])


def checked_entry(entry, word, hashes):
    if not isinstance(entry, dict) or entry.get('kind') != 'source':
        refuse('nieznany rodzaj analizy; dozwolona tylko analiza źródłowa', word)
    keys(entry, SOURCE, word)
    if type(entry['first_source_row']) is not int or entry['first_source_row'] <= 0:
        refuse('nieprawidłowy wiersz źródła', word)
    for field in ('reason', 'source_id', 'original', 'lemma_id', 'raw_tag', 'tag'):
        text(entry[field], word)
    for field in ('names', 'qualifiers'):
        text(entry[field], word, empty=True)
    try:
        expanded = set(expand_tag(entry['raw_tag']))
    except GeneratorError:
        expanded = set()
    if entry['tag'] not in expanded:
        refuse('tag spoza rozwinięcia rekordu', word)
    if game_key(entry['original']) != word:
        refuse('forma analizy poza napisem przypadku', word)
    if entry['source_id'] not in hashes:
        refuse('źródło bez przypiętego hasha', word)
    return entry['source_id']


def validate(config, *, source_hashes):
    """Pełna kontrola pliku; zwraca mapę klucz analizy → pozycja albo odmawia całości."""
    keys(config, TOP)
    if type(config['schema_version']) is not int or config['schema_version'] != SCHEMA_VERSION:
        refuse('nieobsługiwana wersja schematu')
    text(config['decision_version'], None)
    text(config['description'], None)
    if config['rule_id'] != RULE:
        refuse(f'nieobsługiwana reguła; dozwolona {RULE}')
    snapshot = config['source_snapshot']
    keys(snapshot, SNAPSHOT, 'source_snapshot')
    for field in SNAPSHOT:
        text(snapshot[field], 'source_snapshot')
    provenance = config['provenance']
    keys(provenance, PROVENANCE, 'provenance')
    for field in ('issue', 'research_task', 'approval'):
        text(provenance[field], 'provenance')
    if not isinstance(provenance['inputs'], dict) or not provenance['inputs']:
        refuse('brak hashy wejść decyzji', 'provenance')
    for name, value in provenance['inputs'].items():
        text(name, 'provenance')
        sha(value, name)
    hashes = config['sources']
    if not isinstance(hashes, dict) or not hashes:
        refuse('brak hashy źródeł')
    for sid, value in hashes.items():
        if source_hashes.get(sid) != sha(value, sid):
            refuse('hash źródła niezgodny z przypiętym importem', sid)
    cases = config['cases']
    if not isinstance(cases, list) or not cases:
        refuse('brak przypadków')
    words = [c.get('word') if isinstance(c, dict) else None for c in cases]
    if any(not isinstance(w, str) for w in words) or words != sorted(set(words)):
        refuse('przypadki wymagają rosnącej kolejności bez powtórzeń')
    analyses, used_sources = {}, set()
    for case in cases:
        word = case['word']
        keys(case, ('word', 'analyses'), word)
        if not word or game_key(word) != word:
            refuse('napis przypadku wymaga normalizacji gry', word)
        entries = case['analyses']
        if not isinstance(entries, list) or not entries:
            refuse('przypadek bez analiz', word)
        for entry in entries:
            used_sources.add(checked_entry(entry, word, hashes))
        ordered = [order(e) for e in entries]
        if ordered != sorted(set(ordered)):
            refuse('analizy przypadku wymagają rosnącej kolejności bez powtórzeń', word)
        for entry in entries:
            key = analysis_key(entry)
            if key in analyses:
                refuse('powtórzona analiza', word)
            analyses[key] = {'word': word, **entry}
    if used_sources != set(hashes):
        refuse('nieużywany hash źródła')
    counts = {'words': len(cases), 'analyses': len(analyses)}
    expected = config['expected_counts']
    keys(expected, COUNTS, 'expected_counts')
    if expected != counts:
        refuse(f'liczby niezgodne z expected_counts: {counts}', 'expected_counts')
    return {'decision_version': config['decision_version'], 'rule_id': RULE, 'counts': counts,
            'sources': dict(hashes), 'provenance': provenance, 'analyses': analyses}


def decision_for(loaded, entry):
    """Ślad decyzji do `decision_payload`: wersja, forma, powód i odsyłacze."""
    provenance = loaded['provenance']
    return {'decision_version': loaded['decision_version'], 'word': entry['word'], 'reason': entry['reason'],
            'issue': provenance['issue'], 'inputs': sorted(provenance['inputs'])}


def load(path, *, source_hashes):
    try:
        config = load_json(path)
    except (OSError, ValueError) as error:
        raise GeneratorError(f'Nie można odczytać wykluczeń STANDARD: {error}', 4, str(path)) from error
    return validate(config, source_hashes=source_hashes)


def from_manifest(manifest_path):
    """Wczytaj plik przez `configurations` manifestu; zmiana bez nowego hasha przerywa."""
    inputs = inspect_sources(manifest_path)
    reference = inputs['manifest']['configurations'].get(CONFIG_KEY)
    if reference is None:
        raise GeneratorError('Manifest nie przypina wykluczeń STANDARD', 4, CONFIG_KEY)
    path = checked_file(Path(inputs['manifest_path']).parent, reference)
    return load(path, source_hashes={a['source_id']: a['sha256'] for a in inputs['artifacts']})


def check_database(db, loaded, *, analyses=True):
    """Każda pozycja ma dokładnie jeden swój rekord w bazie; `analyses` wymaga też zapisanej analizy."""
    stored = {sid: json.loads(metadata).get('sha256') for sid, metadata in
              db.execute('select source_id,metadata from source_artifact')}
    for sid, value in loaded['sources'].items():
        if stored.get(sid) != value:
            refuse('hash źródła bazy niezgodny z plikiem', sid)
    record = '''select i.id,f.original,l.lemma_id,i.tag,i.names,i.qualifiers
        from surface_form f join interpretation i on i.form_id=f.id join lexeme l on l.id=i.lexeme_id
        where f.original=? and i.source_id=? and i.first_row=?'''
    matched = 0
    for key, entry in loaded['analyses'].items():
        word = entry['word']
        rows = db.execute(record, (entry['original'], entry['source_id'], entry['first_source_row'])).fetchall()
        if len(rows) != 1 or rows[0][1:] != tuple(entry[k] for k in ('original', 'lemma_id', 'raw_tag', 'names', 'qualifiers')):
            refuse('brak dokładnego rekordu importu', word)
        if analyses:
            row = db.execute('select interpretation_id,candidate_key,expanded_tag,game_key from analysis where analysis_key=?',
                             (key,)).fetchone()
            if row != (rows[0][0], None, entry['tag'], word):
                refuse('brak zapisanej analizy o tym kluczu', word)
        matched += 1
    return {'matched_analyses': matched, 'words': loaded['counts']['words']}
