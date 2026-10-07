"""Odbiór przebiegu K1–K10 z drugim build i przeglądem związanym hashami.

Verify niczego nie buduje ani nie poprawia. Zapisuje wyłącznie nową próbę
w `verification/attempt-NNNN/` (plan pakietu, kandydat, raport). Manifest
przebiegu zmienia się tylko przy pełnym powodzeniu: readiness=VERIFIED
oraz pieczęć hashy, którą export sprawdza przed zamrożeniem pakietu.
"""
import hashlib
from pathlib import Path
import shutil
import sqlite3
import unicodedata
from .canonical import dumps, load_json, sha256, write_json
from .database import connect
from .inputs import GeneratorError, checked_file, inspect_sources
from .run import STAGES, code_identity, now

KS = tuple(f'K{number}' for number in range(1, 11))
VARIANTS = ('broad', 'standard')
LIST_FILES = {'broad': 'LL-PL-BROAD.txt', 'standard': 'LL-PL-STANDARD.txt'}
EXPLAIN_CATEGORIES = ('accept', 'reject', 'unresolved', 'absent', 'reconstruction',
                      'homonyms', 'profile_reject', 'no_kwjp')
ASSESSMENTS = ('correct', 'incorrect', 'unknown')
CONDITION_SCOPES = ('code', 'documentation', 'lists', 'reports')
SEAL_EXCLUDED = ('readiness', 'verification', 'export')


def manifest_core_sha256(manifest):
    """Hash manifestu bez pól, które zmienia sam odbiór i export."""
    core = {key: value for key, value in manifest.items() if key not in SEAL_EXCLUDED}
    return hashlib.sha256(dumps(core).encode('utf-8')).hexdigest()


def game_key(value):
    return unicodedata.normalize('NFC', unicodedata.normalize('NFC', value).lower())


def pending_flags(data, name):
    """Jawne znaczniki niekompletności raportu; brak raportu to też blokada."""
    if not isinstance(data, dict):
        return [f'Raport {name} nie jest obiektem JSON']
    found = [f'Raport {name}: {key}=true' for key, value in sorted(data.items())
             if key.endswith('_pending') and value is True]
    if data.get('status') == 'INCOMPLETE':
        found.append(f'Raport {name}: status INCOMPLETE')
    return found


class Checks:
    def __init__(self):
        self.reasons = {k: [] for k in KS}
        self.evidence = {k: [] for k in KS}

    def fail(self, k, message, **details):
        self.reasons[k].append({'message': message, **details})

    def note(self, k, message):
        self.evidence[k].append(message)

    def report(self):
        return {k: {'status': 'fail' if self.reasons[k] else 'pass',
                    'reasons': self.reasons[k], 'evidence': self.evidence[k]} for k in KS}


def _load(path):
    try:
        return load_json(path)
    except (OSError, ValueError) as error:
        return error


def _report(run, name, checks, k):
    data = _load(run / 'reports' / name)
    if isinstance(data, Exception):
        checks.fail(k, f'Brak lub niepoprawny raport reports/{name}: {data}')
        return None
    for message in pending_flags(data, name):
        checks.fail(k, message)
    return data


def _release_config(inputs, checks):
    """K10: jawne warunki pakietu; bez domyślnej licencji i bez uzupełniania braków."""
    reference = inputs['manifest'].get('configurations', {}).get('release')
    if reference is None:
        checks.fail('K10', 'Brak konfiguracji warunków pakietu (configurations.release)')
        return None, None
    base = Path(inputs['manifest_path']).parent
    try:
        path = checked_file(base, reference)
        config = load_json(path)
    except (GeneratorError, OSError, ValueError) as error:
        checks.fail('K10', f'Nie można odczytać warunków pakietu: {error}')
        return None, None
    directory = path.parent
    if not isinstance(config, dict) or config.get('kind') != 'literaki-release-conditions' \
            or config.get('schema_version') != 1 or not isinstance(config.get('package_id'), str):
        checks.fail('K10', 'Nieobsługiwany format warunków pakietu')
        return None, None
    conditions = config.get('conditions')
    if not isinstance(conditions, dict):
        checks.fail('K10', 'Warunki pakietu nie zawierają sekcji conditions')
        return config, directory
    for scope in CONDITION_SCOPES:
        item = conditions.get(scope)
        if not isinstance(item, dict):
            checks.fail('K10', f'Brak warunków {scope}')
            continue
        if item.get('status') != 'DECLARED':
            checks.fail('K10', f'Warunki {scope}: status {item.get("status")} — czeka na decyzję właściciela')
            continue
        if not isinstance(item.get('terms'), str) or not item['terms'].strip():
            checks.fail('K10', f'Warunki {scope} nie mają treści')
        files = item.get('files')
        if not isinstance(files, list) or not files:
            checks.fail('K10', f'Warunki {scope} nie wskazują przypiętych plików')
            continue
        for reference in files:
            try:
                checked_file(directory, reference)
            except GeneratorError as error:
                checks.fail('K10', f'Warunki {scope}: {error} ({error.source})')
    database = conditions.get('database')
    if not isinstance(database, dict) or type(database.get('distributed')) is not bool:
        checks.fail('K10', 'Brak jawnej decyzji o dystrybucji bazy')
    elif database['distributed'] and database.get('status') != 'DECLARED':
        checks.fail('K10', 'Baza ma być dystrybuowana bez zadeklarowanych warunków — czeka na decyzję właściciela')
    elif not database['distributed'] and database.get('status') != 'NOT_DISTRIBUTED':
        checks.fail('K10', 'Niespójny status warunków bazy')
    try:
        checked_file(directory, config.get('attributions'))
    except GeneratorError as error:
        checks.fail('K10', f'Atrybucje projektu: {error}')
    if not isinstance(config.get('limitations'), list) or not all(isinstance(x, str) for x in config['limitations']):
        checks.fail('K10', 'Ograniczenia pakietu muszą być listą tekstów')
    if not isinstance(config.get('known_limitations', []), list):
        checks.fail('K10', 'known_limitations musi być listą')
    return config, directory


def _check_inputs(run_manifest, checks, allow_test_fixture):
    inputs = run_manifest['inputs']
    if inputs.get('mode') == 'test':
        if not allow_test_fixture:
            checks.fail('K1', 'Przebieg z fikstury testowej (mode=test) nie może uzyskać VERIFIED przez publiczne CLI')
        else:
            checks.note('K1', 'Tryb fikstury testowej: wynik dotyczy wyłącznie mechaniki')
    try:
        current = inspect_sources(inputs['manifest_path'])
    except GeneratorError as error:
        checks.fail('K1', f'Kontrola wejść nieudana: {error} ({error.source})')
        return
    if current['manifest_sha256'] != inputs['manifest_sha256']:
        checks.fail('K1', 'Manifest wejść ma inny SHA256 niż podczas build')
    if current['manifest'] != inputs['manifest']:
        checks.fail('K1', 'Zapisane w przebiegu wejścia różnią się od manifestu źródeł')
    checks.note('K1', f'Wejścia: {len(current["artifacts"])} artefaktów, manifest {current["manifest_sha256"]}')


def _check_imports(run, inputs, checks):
    counts = _report(run, 'import-counts.json', checks, 'K2')
    if counts is None:
        return
    expected = {a['source_id']: a for a in inputs['artifacts']}
    if not isinstance(counts, dict) or set(counts) != set(expected):
        checks.fail('K2', 'Raport importu nie rozlicza dokładnie wszystkich aktywnych źródeł')
        return
    for sid, artifact in sorted(expected.items()):
        metrics = counts[sid]
        if not isinstance(metrics, dict) or type(metrics.get('records')) is not int:
            checks.fail('K2', f'Brak liczby rekordów importu {sid}')
            continue
        for key, value in artifact.get('expected_counts', {}).items():
            if metrics.get(key) != value:
                checks.fail('K2', f'Import {sid}: {key}={metrics.get(key)} zamiast {value}')
    checks.note('K2', f'Rozliczone źródła: {len(expected)}')


def _read_list(path):
    data = path.read_bytes()
    if data.startswith(b'\xef\xbb\xbf'):
        raise ValueError('BOM')
    text = data.decode('utf-8')
    if '\r' in text or (text and not text.endswith('\n')):
        raise ValueError('wymagane LF i końcowy LF')
    keys = text.split('\n')[:-1] if text else []
    for key in keys:
        if not key or key != game_key(key):
            raise ValueError(f'niepoprawny klucz {key!r}')
    if any(left >= right for left, right in zip(keys, keys[1:])):
        raise ValueError('klucze nie są unikalne i posortowane rosnąco')
    return keys


def _check_lists(run, checks):
    lists = {}
    for variant in VARIANTS:
        relative = f'lists/{variant}.txt'
        try:
            lists[variant] = _read_list(run / relative)
        except FileNotFoundError:
            checks.fail('K3', f'Brak {relative}')
        except (OSError, UnicodeDecodeError, ValueError) as error:
            checks.fail('K3', f'Niepoprawny format {relative}: {error}')
    try:
        with connect(run / 'build.sqlite', readonly=True) as db:
            for variant, keys in lists.items():
                stored = [row[0] for row in db.execute('''select distinct a.game_key from analysis a
                    join variant_decision d on d.analysis_key=a.analysis_key
                    where d.variant=? and d.membership_status='accept' order by a.game_key''', (variant,))]
                if stored != keys:
                    extra, missing = sorted(set(keys) - set(stored)), sorted(set(stored) - set(keys))
                    checks.fail('K3', f'lists/{variant}.txt różni się od decyzji bazy ({variant}): '
                                      f'nadmiar {len(extra)}, brak {len(missing)}',
                                extra=extra[:20], missing=missing[:20])
    except (sqlite3.Error, OSError) as error:
        checks.fail('K3', f'Nie można odczytać decyzji z bazy: {error}')
    if len(lists) == 2:
        outside = sorted(set(lists['standard']) - set(lists['broad']))
        if outside:
            checks.fail('K3', f'STANDARD nie jest podzbiorem BROAD: {len(outside)} słów', words=outside[:20])
        checks.note('K3', f'BROAD {len(lists["broad"])}, STANDARD {len(lists["standard"])}')
    return lists


def _check_coverage(run, checks):
    for name in ('construction-candidates.json', 'decisions.json'):
        _report(run, name, checks, 'K4')
    coverage = _report(run, 'coverage.json', checks, 'K4')
    if coverage is None:
        return
    if coverage.get('source_semantic_population_complete') is not True:
        checks.fail('K4', 'Populacja semantyczna źródła nie jest zamknięta')
    for name, item in sorted(coverage.get('source_classes', {}).items()):
        if item.get('semantic_qualification') != 'CLOSED':
            checks.fail('K4', f'Klasa {name}: {item.get("semantic_qualification")}')
    if coverage.get('unregistered_constructor_classes'):
        checks.fail('K4', 'Niezarejestrowane klasy konstrukcji: '
                    + ', '.join(coverage['unregistered_constructor_classes']))
    for variant, item in sorted(coverage.get('source_assessment_coverage', {}).items()):
        if item.get('coverage') == 'PARTIAL_MISSING_ASSESSMENTS':
            checks.fail('K4', f'{variant}: brak ocen części rozwinięć źródła')


def _known_limitations(config, directory, checks):
    known = {}
    for item in (config or {}).get('known_limitations', []) or []:
        key = (item.get('variant'), item.get('layer'), item.get('rule_id')) if isinstance(item, dict) else None
        if not key or not all(isinstance(x, str) for x in key) or not isinstance(item.get('description'), str):
            checks.fail('K5', 'Niepełny opis znanego ograniczenia')
            continue
        try:
            checked_file(directory, item.get('no_impact_evidence'))
        except GeneratorError as error:
            checks.fail('K5', f'Ograniczenie {"/".join(key)}: dowód braku wpływu {error}')
            continue
        known[key] = item
    return known


def _check_unresolved(run, config, directory, checks):
    data = _report(run, 'unresolved.json', checks, 'K5')
    known = _known_limitations(config, directory, checks)
    if data is None:
        return
    for variant, counts in sorted(data.get('variants', {}).items()):
        for scope in ('analysis_membership', 'word_membership'):
            if counts.get(scope, {}).get('unresolved', 0):
                checks.fail('K5', f'{variant}: {counts[scope]["unresolved"]} nierozstrzygniętych ({scope}) zmienia listy')
    for rule in data.get('rules', []):
        key = (rule.get('variant'), rule.get('layer'), rule.get('rule_id'))
        label = '/'.join(map(str, key))
        affected = rule.get('word_keys_by_membership', {}).get('unresolved', 0)
        if affected:
            checks.fail('K5', f'Nierozstrzygnięcie {label} zmienia listy: {affected} słów bez rozstrzygnięcia')
        elif key not in known:
            checks.fail('K5', f'Nieznane nierozstrzygnięcie {label} bez udokumentowanego braku wpływu')
        else:
            checks.note('K5', f'Udokumentowane ograniczenie bez wpływu: {label}')


def _check_links(run, checks):
    links = _report(run, 'links.json', checks, 'K6')
    if links is None:
        return
    gate = links.get('stage_completion') or {}
    if gate.get('complete') is not True or gate.get('blocking'):
        checks.fail('K6', 'Etap links nieukończony: ' + ', '.join(map(str, gate.get('blocking') or ['brak bramki'])))


def _review_samples(run, review, index_sha, index, checks):
    samples = review.get('samples') if isinstance(review.get('samples'), dict) else {}
    required = sorted(p for p in index.get('files', {}) if p.startswith('reports/quality-'))
    if not required:
        checks.fail('K9', 'Przebieg nie zawiera próbek quality-v1 do przeglądu')
    from .quality import review_template
    for relative in required:
        entry = samples.get(relative)
        if not isinstance(entry, dict):
            checks.fail('K9', f'Brak przeglądu próbki {relative}')
            continue
        try:
            template = review_template(load_json(run / relative), canonical_index_sha256=index_sha,
                                       evidence_sha256={relative: sha256(run / relative)})
        except (GeneratorError, OSError, ValueError, KeyError) as error:
            checks.fail('K9', f'Nie można odtworzyć szablonu przeglądu {relative}: {error}')
            continue
        for field in ('sample_sha256', 'evidence_sha256', 'canonical_index_sha256', 'version'):
            if entry.get(field) != template[field]:
                checks.fail('K9', f'Przegląd {relative}: niezgodny hash lub wersja ({field})')
        if entry.get('status') != 'REVIEWED':
            checks.fail('K9', f'Przegląd {relative}: status {entry.get("status")}')
        expected = {item['key']: item['strata'] for item in template['items']}
        items = {item.get('key'): item for item in entry.get('items', []) if isinstance(item, dict)}
        missing, extra = sorted(set(expected) - set(items)), sorted(set(items) - set(expected), key=str)
        if missing:
            checks.fail('K9', f'Brak {len(missing)} pozycji przeglądu w {relative}', keys=missing[:20])
        if extra:
            checks.fail('K9', f'Nadmiarowe pozycje przeglądu w {relative}', keys=[str(x) for x in extra[:20]])
        for key, item in sorted(items.items(), key=lambda pair: str(pair[0])):
            if key not in expected:
                continue
            if item.get('strata') != expected[key]:
                checks.fail('K9', f'{relative}: pozycja {key} ma inne warstwy próby')
            if item.get('assessment') not in ASSESSMENTS:
                checks.fail('K9', f'{relative}: pozycja {key} bez oceny')
            if not all(isinstance(item.get(f), str) and item[f].strip()
                       for f in ('reviewer', 'source_justification')):
                checks.fail('K9', f'{relative}: pozycja {key} bez przeglądającego lub uzasadnienia źródłowego')
            if type(item.get('affects_lists_or_links')) is not bool:
                checks.fail('K9', f'{relative}: pozycja {key} bez oceny wpływu na listy/linki')
            elif item['affects_lists_or_links']:
                checks.fail('K9', f'{relative}: pozycja {key} to błąd blokujący werdykt')
        checks.note('K9', f'{relative}: {len(items)} pozycji')


def _check_review(run, review_path, index, checks):
    _report(run, 'filter-impact.json', checks, 'K9')
    review = _load(review_path)
    if isinstance(review, Exception) or not isinstance(review, dict) \
            or review.get('kind') != 'literaki-quality-review' or review.get('schema_version') != 1:
        message = f'Brak lub niepoprawny plik przeglądu ({review_path})'
        checks.fail('K9', message)
        checks.fail('K7', message + '; brak runtime explain')
        return
    try:
        index_sha = sha256(run / 'reports/canonical-index.json')
        logical = load_json(run / 'reports/logical-content.json')['sha256']
    except (OSError, ValueError, KeyError) as error:
        checks.fail('K9', f'Brak hashy przebiegu do związania przeglądu: {error}')
        return
    if review.get('canonical_index_sha256') != index_sha:
        checks.fail('K9', 'Przegląd dotyczy innego hash canonical-index')
    if review.get('logical_content_sha256') != logical:
        checks.fail('K9', 'Przegląd dotyczy innego hash logical-content')
    _review_samples(run, review, index_sha, index, checks)
    from .explain import explain
    cases = review.get('explain_runtime') if isinstance(review.get('explain_runtime'), list) else []
    present = {case.get('category') for case in cases if isinstance(case, dict)}
    for category in EXPLAIN_CATEGORIES:
        if category not in present:
            checks.fail('K7', f'Brak runtime explain dla kategorii: {category}')
    for case in cases:
        if not isinstance(case, dict) or case.get('category') not in EXPLAIN_CATEGORIES:
            checks.fail('K7', 'Nieznana pozycja runtime explain')
            continue
        try:
            result = explain(run, case.get('word'), case.get('variant', 'standard'))
        except GeneratorError as error:
            checks.fail('K7', f'explain {case["category"]} ({case.get("word")}) nieudane: {error}')
            continue
        if hashlib.sha256(dumps(result).encode('utf-8')).hexdigest() != case.get('result_sha256'):
            checks.fail('K7', f'Wynik explain dla {case["category"]} ({case.get("word")}) różni się od przeglądu')
    checks.note('K7', f'Sprawdzono {len(cases)} wyników explain')


def _integrity(run, label, checks):
    from .reports import logical_content_report
    try:
        with connect(run / 'build.sqlite', readonly=True) as db:
            if db.execute('pragma integrity_check').fetchone()[0] != 'ok':
                checks.fail('K8', f'{label}: integrity_check bazy nieudany')
            if db.execute('pragma foreign_key_check').fetchone() is not None:
                checks.fail('K8', f'{label}: naruszone klucze obce')
            logical = logical_content_report(db)
    except (GeneratorError, sqlite3.Error, OSError) as error:
        checks.fail('K8', f'{label}: nie można policzyć logical-content: {error}')
        return None
    stored = _load(run / 'reports/logical-content.json')
    if isinstance(stored, Exception) or stored.get('sha256') != logical['sha256']:
        checks.fail('K8', f'{label}: logical-content bazy różni się od raportu')
    return logical['sha256']


def _index(run, label, checks):
    from .reports import canonical_index
    stored = _load(run / 'reports/canonical-index.json')
    try:
        current = canonical_index(run)
    except (GeneratorError, OSError, ValueError, KeyError) as error:
        checks.fail('K8', f'{label}: nie można odtworzyć canonical-index: {error}')
        return None
    if isinstance(stored, Exception):
        checks.fail('K8', f'{label}: brak reports/canonical-index.json')
        return current
    changed = sorted(path for path in set(stored.get('files', {})) | set(current['files'])
                     if stored.get('files', {}).get(path) != current['files'].get(path))
    if changed:
        checks.fail('K8', f'{label}: pliki zmienione względem canonical-index: ' + ', '.join(changed))
    for field in ('missing', 'provenance'):
        if stored.get(field) != current[field]:
            checks.fail('K8', f'{label}: canonical-index ma nieaktualne pole {field}')
    return stored


def _check_reproduction(run, peer, run_manifest, checks, *, walk_databases=True):
    same_peer = run.resolve() == peer.resolve()
    if same_peer:
        # Przed przejściami bazy: ten błąd nie zależy od jej treści.
        checks.fail('K8', 'Peer-run musi być niezależnym drugim przebiegiem, nie tym samym katalogiem')
    code = run_manifest.get('code')
    current = code_identity()['tree_sha256']
    if not isinstance(code, dict):
        checks.fail('K8', 'Brak tożsamości kodu w manifeście przebiegu')
    else:
        if code.get('tree_sha256') != current:
            checks.fail('K8', 'Zmieniony kod generatora od build (tree_sha256)')
        if code.get('git_dirty') is not False:
            checks.fail('K8', 'Build z kodu dirty lub bez stanu git')
        if not code.get('git_commit'):
            checks.fail('K8', 'Build bez commitu kodu')
    run_index = _index(run, 'run', checks)
    if walk_databases:
        _integrity(run, 'run', checks)
    else:
        # Odczyt całej bazy (godziny na pełnym buildzie) nie zmieni werdyktu REFUSED.
        checks.note('K8', 'Pominięto integrity_check i logical-content bazy: przebieg nieukończony')
    if same_peer:
        return
    peer_manifest = _load(peer / 'manifest.json')
    if isinstance(peer_manifest, Exception):
        checks.fail('K8', f'Brak manifestu niezależnego peer-run: {peer_manifest}')
        return
    for stage in STAGES:
        status = peer_manifest.get('stages', {}).get(stage, {}).get('status')
        if status != 'complete':
            checks.fail('K8', f'Peer-run: etap {stage} ma status {status}')
    peer_code = peer_manifest.get('code') or {}
    if isinstance(code, dict) and peer_code.get('tree_sha256') != code.get('tree_sha256'):
        checks.fail('K8', 'Peer-run zbudowano innym kodem')
    if peer_manifest.get('inputs', {}).get('manifest_sha256') != run_manifest['inputs']['manifest_sha256']:
        checks.fail('K8', 'Peer-run zbudowano z innego manifestu wejść')
    peer_index = _index(peer, 'peer-run', checks)
    if walk_databases:
        _integrity(peer, 'peer-run', checks)
    if run_index is None or peer_index is None:
        return
    differing = sorted(path for path in set(run_index.get('files', {})) | set(peer_index.get('files', {}))
                       if (run_index['files'].get(path) or {}).get('sha256')
                       != (peer_index['files'].get(path) or {}).get('sha256'))
    if differing:
        checks.fail('K8', 'Peer-run różni się treścią kanoniczną: ' + ', '.join(differing))
    if run_index.get('provenance') != peer_index.get('provenance'):
        checks.fail('K8', 'Peer-run ma inne pochodzenie wejść')
    checks.note('K8', f'Porównano {len(run_index.get("files", {}))} plików kanonicznych z peer-run')


def _markdown_attributions(inputs, config, directory):
    lines = ['# Atrybucje pakietu', '',
             'Źródła faktycznie użyte w przebiegu. Pakiet nie przypisuje projektowi praw do materiałów zewnętrznych.', '']
    for artifact in sorted(inputs['artifacts'], key=lambda a: a['source_id']):
        lines += [f'## {artifact["source_id"]}', '',
                  f'- pochodzenie: {artifact.get("origin")}',
                  f'- wersja: {artifact["version"]}', f'- adres: {artifact["url"]}',
                  f'- autorzy: {artifact["authors"]}', f'- licencja: {artifact["license"]} ({artifact["license_scope"]})',
                  f'- użycie: {artifact["used_for"]}', f'- atrybucja: {artifact["attribution"]}',
                  f'- SHA256: {artifact["sha256"]}', '']
    if config:
        try:
            project = checked_file(directory, config['attributions']).read_text(encoding='utf-8')
            lines += ['## Atrybucje projektu', '', project.rstrip('\n'), '']
        except (GeneratorError, OSError, KeyError):
            lines += ['## Atrybucje projektu', '', 'BRAK: atrybucje projektu nie przeszły kontroli K10.', '']
    return '\n'.join(lines).rstrip('\n') + '\n'


def _markdown_limitations(inputs, config):
    lines = ['# Ograniczenia pakietu', '']
    for item in inputs['manifest'].get('unavailable', []):
        lines.append(f'- Źródło {item.get("source_id")} niedostępne ({item.get("reason")}); '
                     'przewidziane ograniczenie N1, bez imputacji brakujących danych.')
    for text in (config or {}).get('limitations', []) or []:
        lines.append(f'- {text}')
    for item in (config or {}).get('known_limitations', []) or []:
        if isinstance(item, dict):
            lines.append(f'- {item.get("variant")}/{item.get("layer")}/{item.get("rule_id")}: '
                         f'{item.get("description")} (dowód braku wpływu: '
                         f'{(item.get("no_impact_evidence") or {}).get("sha256")})')
    lines += ['- Próba jakościowa quality-v1 nie jest statystycznym zapewnieniem bezbłędności całego zbioru.',
              '- Pakiet nie jest wdrożony do gry; nie zmienia reguł gry.']
    return '\n'.join(lines) + '\n'


def _markdown_terms(config):
    lines = ['# Warunki udostępnienia', '']
    if not config:
        return '\n'.join(lines + ['BRAK: warunki nie przeszły kontroli K10.']) + '\n'
    for scope in (*CONDITION_SCOPES, 'database'):
        item = config.get('conditions', {}).get(scope) or {}
        lines.append(f'## {scope}')
        lines.append('')
        lines.append(f'- status: {item.get("status")}')
        for field in ('terms', 'basis', 'note'):
            if item.get(field):
                lines.append(f'- {field}: {item[field]}')
        for reference in item.get('files', []) or []:
            lines.append(f'- plik: {reference.get("path")} (SHA256 {reference.get("sha256")})')
        lines.append('')
    return '\n'.join(lines).rstrip('\n') + '\n'


def _prepare_candidate(run, attempt, inputs, config, directory):
    """I1: kandydat i plan pakietu powstają przed werdyktem i mają status INCOMPLETE."""
    candidate = attempt / 'candidate'
    (candidate / 'reports').mkdir(parents=True)
    files, missing = {}, []

    def add(relative, source=None, text=None):
        target = candidate / relative
        if text is not None:
            target.write_bytes(text.encode('utf-8'))
        else:
            shutil.copyfile(source, target)
            if sha256(target) != sha256(source):
                raise GeneratorError('Kopia kandydata różni się od źródła', 4, relative)
        files[relative] = {'sha256': sha256(target), 'bytes': target.stat().st_size}

    for variant, name in LIST_FILES.items():
        source = run / 'lists' / f'{variant}.txt'
        if source.is_file() and not source.is_symlink():
            add(name, source)
        else:
            missing.append(name)
    index = _load(run / 'reports/canonical-index.json')
    reports = sorted(p for p in (index.get('files', {}) if isinstance(index, dict) else {})
                     if p.startswith('reports/'))
    for relative in [*reports, 'reports/canonical-index.json']:
        source = run / relative
        if source.is_file() and not source.is_symlink():
            add(relative, source)
        else:
            missing.append(relative)
    add('ATTRIBUTIONS.md', text=_markdown_attributions(inputs, config, directory))
    add('LIMITATIONS.md', text=_markdown_limitations(inputs, config))
    add('TERMS.md', text=_markdown_terms(config))
    plan = {'schema_version': 1, 'kind': 'literaki-package-plan', 'status': 'INCOMPLETE',
            'package_id': (config or {}).get('package_id'),
            'database': ((config or {}).get('conditions') or {}).get('database'),
            'notice': 'Plan kandydata przed werdyktem; nie jest wydaniem.',
            'files': dict(sorted(files.items())), 'missing': sorted(missing)}
    write_json(attempt / 'package-plan.json', plan)
    return plan


def _new_attempt(run):
    root = run / 'verification'
    root.mkdir(exist_ok=True)
    number = 1 + max((int(p.name.split('-')[1]) for p in root.glob('attempt-*')
                      if p.name.split('-')[1].isdigit()), default=0)
    while True:
        attempt = root / f'attempt-{number:04d}'
        try:
            attempt.mkdir()
            return attempt
        except FileExistsError:
            number += 1


def verify(run_dir, peer_dir, review_path, *, allow_test_fixture=False):
    """Kontrola K1–K10. Fikstura testowa przechodzi tylko przez API testów."""
    run, peer = Path(run_dir), Path(peer_dir)
    manifest = _load(run / 'manifest.json')
    if isinstance(manifest, Exception) or not isinstance(manifest, dict) \
            or manifest.get('schema_version') != 1 or 'inputs' not in manifest:
        raise GeneratorError('Katalog nie jest przebiegiem generatora (brak manifest.json)', 5, str(run))
    if manifest.get('readiness') != 'INCOMPLETE':
        raise GeneratorError(f'Przebieg ma już status {manifest.get("readiness")}; verify wymaga nowego przebiegu', 5, str(run))
    inputs = manifest['inputs']
    checks = Checks()
    stages = manifest.get('stages', {})
    blocked = [f'etap {stage} ma status {stages.get(stage, {}).get("status")}'
               for stage in STAGES if stages.get(stage, {}).get('status') != 'complete']
    if blocked:
        # §9: odbiór wymaga wszystkich etapów complete; dotyczy każdego K.
        for k in KS:
            checks.fail(k, 'Przebieg nieukończony: ' + '; '.join(blocked))
    _check_inputs(manifest, checks, allow_test_fixture)
    config, directory = _release_config(inputs, checks)
    _check_imports(run, inputs, checks)
    _check_lists(run, checks)
    _check_coverage(run, checks)
    _check_unresolved(run, config, directory, checks)
    _check_links(run, checks)
    index = _load(run / 'reports/canonical-index.json')
    _check_review(run, Path(review_path), index if isinstance(index, dict) else {}, checks)
    _check_reproduction(run, peer, manifest, checks, walk_databases=not blocked)
    attempt = _new_attempt(run)
    plan = _prepare_candidate(run, attempt, inputs, config, directory)
    results = checks.report()
    verdict = 'VERIFIED' if all(item['status'] == 'pass' for item in results.values()) else 'REFUSED'
    relative = str(attempt.relative_to(run))
    report = {'schema_version': 1, 'kind': 'literaki-verification', 'verdict': verdict,
              'attempt': relative, 'fixture': inputs.get('mode') == 'test', 'checks': results,
              'package_plan_sha256': sha256(attempt / 'package-plan.json'),
              'package_files': sorted(plan['files']),
              'review_sha256': sha256(review_path) if Path(review_path).is_file() else None}
    write_json(attempt / 'verification.json', report)
    if verdict == 'VERIFIED':
        with_db = sha256(run / 'build.sqlite')
        manifest = load_json(run / 'manifest.json')
        manifest['readiness'] = 'VERIFIED'
        manifest['verification'] = {
            'attempt': relative, 'fixture': report['fixture'], 'verified_at': now(),
            'verification_sha256': sha256(attempt / 'verification.json'),
            'package_plan_sha256': report['package_plan_sha256'],
            'canonical_index_sha256': sha256(run / 'reports/canonical-index.json'),
            'logical_content_sha256': load_json(run / 'reports/logical-content.json')['sha256'],
            'database_sha256': with_db, 'manifest_core_sha256': manifest_core_sha256(manifest)}
        write_json(run / 'manifest.json', manifest)
    return report


def format_verification(report):
    lines = [f'Werdykt: {report["verdict"]} (próba {report["attempt"]})']
    for k, item in report['checks'].items():
        lines.append(f'{k}: {"OK" if item["status"] == "pass" else "BLOKADA"}')
        lines.extend(f'  - {reason["message"]}' for reason in item['reasons'])
    return '\n'.join(lines)
