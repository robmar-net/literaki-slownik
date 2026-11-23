"""Import porcjowany, metryki i jawne statusy niepełnego przebiegu."""
from collections import Counter
import errno
import os
from pathlib import Path
import resource
import shutil
import sqlite3
import time
from .canonical import dumps, write_json, write_bytes, load_json, sha256
from . import database
from .database import connect
from .inputs import GeneratorError, inspect_sources, checked_file
from . import sgjp, kwjp
from .run import (create_run, set_stage, close_attempt, code_identity, check_identity, begin_resume,
                  STAGES)
from . import volume, workfs
from .reports import qualifier_coverage, logical_content_report, unresolved_report, persisted_filter_impact, canonical_index, coverage_report
from .constructions import materialize_confirmed_candidates
from .links import (create_links, link_report, load_pos_map, verify_link_completeness,
                    link_stage_gate, SHARED_POS, DEFAULT_POS_MAP_VERSION)
from .decisions import materialize_assessments, USE_REVIEW_ID
from . import standard_age_exceptions
from . import standard_exclusions


def flush(db, sql, batch):
    if batch:
        db.executemany(sql, batch)
        db.commit()
        batch.clear()


def stage_durable(db):
    """Granica etapu (R8): commit danych etapu, a w trybie `stage_boundaries` też F_FULLFSYNC bazy.

    Wołana przed plikami etapu i manifestem: kolejność zawsze dane trwale → pliki etapu → manifest.
    W trybie `build` commit przy fullfsync=ON sam opróżnia pamięć dysku."""
    db.commit()
    if database.FULLFSYNC_MODE == 'stage_boundaries':
        database.full_sync(db)


def import_sgjp(db, artifact, batch_size):
    sid = artifact['source_id']
    batch = []
    for number, fields in sgjp.rows(artifact['resolved_path']):
        batch.append((sid, number, *fields))
        if len(batch) >= batch_size:
            flush(db, 'INSERT INTO sgjp_record VALUES (?,?,?,?,?,?,?)', batch)
    flush(db, 'INSERT INTO sgjp_record VALUES (?,?,?,?,?,?,?)', batch)
    db.execute('''INSERT INTO lexeme(source_id,lemma_id,lemma_base)
                  SELECT source_id,lemma,CASE WHEN instr(lemma,':')>0
                  THEN substr(lemma,1,instr(lemma,':')-1) ELSE lemma END
                  FROM sgjp_record WHERE source_id=? GROUP BY lemma''', (sid,))
    db.execute('''INSERT OR IGNORE INTO surface_form(original,nfc,game_key,length)
                  SELECT form,nfc(form),game_key(form),length(game_key(form))
                  FROM sgjp_record WHERE source_id=? GROUP BY form''', (sid,))
    db.execute('''INSERT INTO interpretation(source_id,first_row,form_id,lexeme_id,tag,names,qualifiers)
                  SELECT r.source_id,min(r.row_number),f.id,l.id,r.tag,r.names,r.qualifiers
                  FROM sgjp_record r JOIN surface_form f ON f.original=r.form
                  JOIN lexeme l ON l.source_id=r.source_id AND l.lemma_id=r.lemma
                  WHERE r.source_id=? GROUP BY f.id,l.id,r.tag,r.names,r.qualifiers''', (sid,))
    db.commit()
    return sgjp_counts(db, sid)


def import_kwjp(db, artifact, batch_size):
    sid = artifact['source_id']
    batch = []
    for number, raw, typed in kwjp.rows(artifact['resolved_path'], artifact['kind']):
        if typed['total_freq'] < artifact.get('publication_threshold', 0):
            raise GeneratorError('KWJP poniżej deklarowanego progu publikacji', 4, sid, number)
        unit = raw.get('lemma', raw.get('form', raw.get('unit_1')))
        metrics = {k: raw[k] for k in typed}
        batch.append((sid, number, unit, raw.get('unit_2'), raw.get('pos'), dumps(metrics), dumps(typed), typed['freq']))
        if len(batch) >= batch_size:
            flush(db, 'INSERT INTO corpus_evidence(source_id,row_number,unit_1,unit_2,pos,raw_metrics,typed_metrics,freq) VALUES (?,?,?,?,?,?,?,?)', batch)
    flush(db, 'INSERT INTO corpus_evidence(source_id,row_number,unit_1,unit_2,pos,raw_metrics,typed_metrics,freq) VALUES (?,?,?,?,?,?,?,?)', batch)
    return kwjp_counts(db, sid)


def is_sgjp(artifact):
    return artifact['kind'] in {'sgjp_tab', 'lexical_supplement'}


def is_kwjp(artifact):
    return artifact['kind'].startswith('kwjp_')


def sgjp_counts(db, sid):
    """Metryki importu SGJP z bazy (nie z pamięci): wznowienie po import_sgjp daje te same liczby."""
    one = lambda sql: db.execute(sql, (sid,)).fetchone()[0]
    records = one('SELECT count(*) FROM sgjp_record WHERE source_id=?')
    compact = one('SELECT count(*) FROM interpretation WHERE source_id=?')
    expanded = sum(n * sgjp.tag_size(tag) for tag, n in db.execute(
        'SELECT tag,count(*) FROM interpretation WHERE source_id=? GROUP BY tag', (sid,)))
    return {'records': records, 'interpretations': compact, 'duplicates': records - compact,
            'expanded_alternatives': expanded,
            'lexemes': one('SELECT count(*) FROM lexeme WHERE source_id=?'),
            'original_forms': one('SELECT count(DISTINCT form_id) FROM interpretation WHERE source_id=?')}


def kwjp_counts(db, sid):
    records, sum_freq = db.execute('SELECT count(*),coalesce(sum(freq),0) FROM corpus_evidence WHERE source_id=?',
                                   (sid,)).fetchone()
    return {'records': records, 'sum_freq': sum_freq}


def import_counts(db, artifacts):
    """Treść import-counts.json: każde importowane źródło, liczone z bazy (poprawka 2)."""
    return {a['source_id']: sgjp_counts(db, a['source_id']) if is_sgjp(a) else kwjp_counts(db, a['source_id'])
            for a in artifacts if is_sgjp(a) or is_kwjp(a)}


def write_lists(db, run):
    """Listy wydania: posortowane klucze z zaakceptowanym członkostwem (ta sama kwerenda co verify K3)."""
    (run / 'lists').mkdir(exist_ok=True)
    sizes = {}
    for variant in ('broad', 'standard'):
        keys = [row[0] for row in db.execute('''select distinct a.game_key from analysis a
            join variant_decision d on d.analysis_key=a.analysis_key
            where d.variant=? and d.membership_status='accept' order by a.game_key''', (variant,))]
        sizes[variant] = keys
        write_bytes(run / 'lists' / f'{variant}.txt', ''.join(k + '\n' for k in keys).encode('utf-8'))
    outside = set(sizes['standard']) - set(sizes['broad'])
    if outside:
        raise GeneratorError(f'STANDARD nie jest podzbiorem BROAD: {len(outside)} słów', 4)
    return {variant: len(keys) for variant, keys in sizes.items()}


SQLITE_SPACE = {sqlite3.SQLITE_FULL}
SQLITE_DAMAGE = {sqlite3.SQLITE_CORRUPT, sqlite3.SQLITE_NOTADB}
ERRNO_SPACE = {errno.ENOSPC, errno.EDQUOT}
# Błędy, którymi macOS kończy operacje na odłączonym albo ponownie podłączonym wolumenie USB.
SQLITE_DEVICE = {sqlite3.SQLITE_IOERR, sqlite3.SQLITE_CANTOPEN}
ERRNO_DEVICE = {errno.EIO, errno.ENXIO, errno.ENODEV, errno.ENOENT, errno.EROFS}


def exit_code(error, run, work_volume):
    """Kod wyjścia błędu buildu (tabela „Kody wyjścia”): strażnik 75/76, miejsce 78, uszkodzenie 77, reszta 4.

    Przebieg na wolumenie roboczym: błąd urządzenia (SQLITE_IOERR/CANTOPEN, EIO/ENXIO/ENODEV/ENOENT/EROFS) daje 75
    także przy zdrowym strażniku. T7 mógł zniknąć i wrócić, zanim klasyfikator go sprawdził; G3 tego nie widzi,
    gdy macOS nada wolumenowi to samo st_dev, a st_ino nie pomaga, bo APFS zapisuje numery i-węzłów na dysku.
    Wznowienie jest idempotentne i ograniczone limitem nadzorcy, więc fałszywe 75 kosztuje jeden etap."""
    if isinstance(error, KeyboardInterrupt):
        return 130
    if isinstance(error, GeneratorError):
        return error.code
    if isinstance(error, (OSError, sqlite3.Error)):
        try:
            volume.check_active()
            volume.check_mounted(run)
            volume.check_marker(run, work_volume['marker_id'] if work_volume else None)
        except GeneratorError as guard:
            return guard.code
        except OSError:
            return 75
        primary = getattr(error, 'sqlite_errorcode', None)
        if primary is not None and primary & 0xff in SQLITE_SPACE or getattr(error, 'errno', None) in ERRNO_SPACE:
            return 78
        if primary is not None and primary & 0xff in SQLITE_DAMAGE:
            return 77
        device = (primary is not None and primary & 0xff in SQLITE_DEVICE) \
            or getattr(error, 'errno', None) in ERRNO_DEVICE
        if work_volume is not None and device:
            return 75
        return 4
    if isinstance(error, ValueError):
        return 4
    return 1


# Liczniki „wstawione w tej próbie” zależą od historii przebiegu; raporty kanoniczne ich nie mają (poprawka 1).
INSERTED_COUNTERS = ('new_candidates', 'new_analyses', 'new_decisions')
# Raporty etapu reports ze znacznikami .done (R7), w kolejności liczenia.
MARKED_REPORTS = ('unresolved.json', 'filter-impact.json', 'quality-analyses.json', 'quality-links.json',
                  'quality-words.json', 'logical-content.json', 'coverage.json')


def canonical_report(report):
    return {key: value for key, value in report.items() if key not in INSERTED_COUNTERS}


def stage_context(manifest_path, run, inputs, batch_size=10000):
    """Stan wspólny etapów jednego wywołania buildu."""
    return {'manifest_path': manifest_path, 'base': Path(manifest_path).resolve().parent, 'run': Path(run),
            'inputs': inputs, 'configurations': inputs['manifest']['configurations'],
            'batch_size': batch_size, 'performance': {}, 'stage': STAGES[0]}


def stage_preflight(db, ctx):
    run = ctx['run']
    set_stage(run, 'preflight', 'running')
    for artifact in ctx['inputs']['artifacts']:
        db.execute('INSERT INTO source_artifact VALUES (?,?,?)',
                   (artifact['source_id'], artifact['kind'], dumps(artifact)))
    stage_durable(db)
    # complete dopiero po commicie source_artifact: wznowienie ufa tylko istniejącej bazie.
    set_stage(run, 'preflight', 'complete')


def run_import(db, ctx, stage, predicate, importer):
    run = ctx['run']
    start = time.monotonic()
    set_stage(run, stage, 'running')
    for artifact in filter(predicate, ctx['inputs']['artifacts']):
        sid = artifact['source_id']
        metrics = importer(db, artifact, ctx['batch_size'])
        for key, expected in artifact.get('expected_counts', {}).items():
            if metrics.get(key) != expected:
                raise GeneratorError(f'Niezgodne rozliczenie {key}: {metrics.get(key)} != {expected}', 4, sid)
    stage_durable(db)
    ctx['performance'][stage] = {'seconds': time.monotonic() - start}


def stage_import_sgjp(db, ctx):
    run_import(db, ctx, 'import_sgjp', is_sgjp, import_sgjp)
    set_stage(ctx['run'], 'import_sgjp', 'complete')


def stage_import_kwjp(db, ctx):
    run = ctx['run']
    run_import(db, ctx, 'import_kwjp', is_kwjp, import_kwjp)
    # Poprawki 2 i 3: trzy raporty importu z bazy, zapisane przed complete.
    inventory = {name: dict(db.execute(f'SELECT {name},count(*) FROM interpretation GROUP BY {name}'))
                 for name in ('tag', 'names', 'qualifiers')}
    write_json(run / 'reports/import-counts.json', import_counts(db, ctx['inputs']['artifacts']))
    write_json(run / 'reports/inventory.json', inventory)
    write_json(run / 'reports/qualifier-conditions.json', qualifier_coverage(inventory['qualifiers'].items()))
    set_stage(run, 'import_kwjp', 'complete')


def stage_constructions(db, ctx):
    # Runda 3: zarejestrowany zbiór konstruktorów jest zamkniętym zakresem wydania.
    run = ctx['run']
    start = time.monotonic()
    set_stage(run, 'constructions', 'running')
    construction_counts = materialize_confirmed_candidates(db, ctx['batch_size'])
    stage_durable(db)
    ctx['performance']['diagnostic_constructions'] = {'seconds': time.monotonic() - start}
    write_json(run / 'reports/construction-candidates.json', canonical_report(construction_counts))
    if construction_counts['full_constructions_pending']:
        set_stage(run, 'constructions', 'pending', {'reason': 'niepełny zbiór kandydatów konstrukcji'})
    else:
        set_stage(run, 'constructions', 'complete')


def stage_decisions(db, ctx):
    run, base, configurations = ctx['run'], ctx['base'], ctx['configurations']
    start = time.monotonic()
    set_stage(run, 'decisions', 'running')
    use_reviews = []
    use_reference = configurations.get('semantic-uses')
    if use_reference:
        use_data = load_json(checked_file(base, use_reference))
        if (not isinstance(use_data, dict) or set(use_data) != {'schema_version', 'reviews'}
                or type(use_data['schema_version']) is not int or use_data['schema_version'] != 1):
            raise GeneratorError('Nieobsługiwany format przeglądu użyć', 4)
        use_reviews = use_data['reviews']
    source_hashes = {a['source_id']: a['sha256'] for a in ctx['inputs']['artifacts']}
    # #4: przypięte wyjątki dawności STANDARD; rekordy sprawdzone przed oceną.
    age_exceptions = None
    age_reference = configurations.get(standard_age_exceptions.CONFIG_KEY)
    if age_reference:
        age_exceptions = standard_age_exceptions.load(checked_file(base, age_reference), source_hashes=source_hashes)
        standard_age_exceptions.check_database(db, age_exceptions, analyses=False)
    # #15: przypięte wykluczenia STANDARD; rekordy sprawdzone przed oceną.
    exclusions = None
    exclusion_reference = configurations.get(standard_exclusions.CONFIG_KEY)
    if exclusion_reference:
        exclusions = standard_exclusions.load(checked_file(base, exclusion_reference), source_hashes=source_hashes)
        standard_exclusions.check_database(db, exclusions, analyses=False)
    decision_counts = materialize_assessments(db, ctx['batch_size'], use_reviews=use_reviews,
                                              age_exceptions=age_exceptions, standard_exclusions=exclusions)
    stage_durable(db)
    if age_exceptions:
        decision_counts['standard_age_exceptions']['sha256'] = age_reference['sha256']
    if exclusions:
        decision_counts['standard_exclusions']['sha256'] = exclusion_reference['sha256']
    ctx['performance']['diagnostic_decisions'] = {'seconds': time.monotonic() - start}
    write_json(run / 'reports/decisions.json', canonical_report(decision_counts))
    if decision_counts['full_qualification_pending']:
        set_stage(run, 'decisions', 'pending', {'reason': 'nierozstrzygnięte członkostwo analiz'})
    else:
        write_lists(db, run)
        set_stage(run, 'decisions', 'complete')


def stage_links(db, ctx):
    # Powiązania bezpośrednie są niezależne od kwalifikacji językowej.
    # Pełny etap wymaga kompletnego zbioru konstrukcji i niezależnej kontroli krawędzi.
    run, manifest = ctx['run'], ctx['inputs']['manifest']
    start = time.monotonic()
    set_stage(run, 'links', 'running')
    allowed_pos, pos_map_version = SHARED_POS, DEFAULT_POS_MAP_VERSION
    pos_reference = ctx['configurations'].get('pos-map')
    if pos_reference:
        pos_map = load_pos_map(checked_file(ctx['base'], pos_reference))
        allowed_pos, pos_map_version = pos_map['pairs'], pos_map['version']
    create_links(db, allowed_pos)
    stage_durable(db)
    links = link_report(db, manifest.get('unavailable', []), details=True, pos_map_version=pos_map_version)
    constructions_status = load_json(run / 'manifest.json')['stages']['constructions']['status']
    links['stage_completion'] = link_stage_gate(verify_link_completeness(db, allowed_pos), constructions_status)
    write_json(run / 'reports/links.json', links)
    ctx['performance']['diagnostic_links'] = {'seconds': time.monotonic() - start}
    if links['stage_completion']['complete']:
        set_stage(run, 'links', 'complete')
    else:
        set_stage(run, 'links', 'pending',
                  {'reason': 'niepełne powiązania: ' + '; '.join(links['stage_completion']['blocking'])})


def report_marker(ctx, path):
    """Znacznik R7: bajty raportu oraz kod i wejścia, z którymi powstał."""
    if 'tree_sha256' not in ctx:
        ctx['tree_sha256'] = code_identity()['tree_sha256']
    return {'sha256': sha256(path), 'bytes': path.stat().st_size,
            'tree_sha256': ctx['tree_sha256'], 'manifest_sha256': ctx['inputs']['manifest_sha256']}


def marked_report(ctx, name, compute):
    """Raport z reports/.done: pominięty tylko przy pełnej zgodności znacznika, wtedy czytany z pliku."""
    path = ctx['run'] / 'reports' / name
    marker = ctx['run'] / 'reports/.done' / name
    try:
        if load_json(marker) == report_marker(ctx, path):
            return load_json(path)
    except (FileNotFoundError, ValueError):
        pass  # Brak albo nieczytelny znacznik lub raport: raport liczony od nowa.
    start = time.monotonic()
    value = compute()
    write_json(path, value)
    marker.parent.mkdir(exist_ok=True)
    write_json(marker, report_marker(ctx, path))
    ctx['performance']['diagnostic_' + name.removesuffix('.json').replace('-', '_')] = {
        'seconds': time.monotonic() - start}
    return value


def stage_reports(db, ctx):
    run, base, configurations = ctx['run'], ctx['base'], ctx['configurations']
    set_stage(run, 'reports', 'running')
    stage_durable(db)  # Raporty tylko czytają bazę (tabele temp w RAM); granica przed pierwszym plikiem.
    unresolved = marked_report(ctx, 'unresolved.json', lambda: unresolved_report(db))
    marked_report(ctx, 'filter-impact.json', lambda: persisted_filter_impact(db, unresolved))
    quality_reference = configurations.get('quality')
    if quality_reference:
        from .quality import sample_persisted_analyses, sample_corpus_links, sample_word_analyses
        config = load_json(checked_file(base, quality_reference))
        marked_report(ctx, 'quality-analyses.json', lambda: sample_persisted_analyses(db, config, unresolved))
        marked_report(ctx, 'quality-links.json', lambda: sample_corpus_links(db, config))
        words_reference = configurations.get('quality-words')
        if words_reference:
            definitions = load_json(checked_file(base, words_reference))
            marked_report(ctx, 'quality-words.json',
                          lambda: sample_word_analyses(db, config, definitions, unresolved))
    marked_report(ctx, 'logical-content.json', lambda: logical_content_report(db))
    coverage = marked_report(ctx, 'coverage.json', lambda: coverage_report(db, unresolved))
    set_stage(run, 'reports', 'complete' if coverage['status'] == 'COMPLETE' else 'pending')


# Reset przed wznowieniem (tabela „Reset”): DELETE w kolejności kluczy obcych, dziecko przed rodzicem.
DERIVED_TABLES = ('variant_decision', 'decision_payload', 'analysis', 'derivation_component', 'derivation_candidate')
SGJP_TABLES = ('interpretation', 'lexeme', 'surface_form', 'sgjp_record')


def reset_stage(db, first):
    """Tabele etapu first i dalszych do stanu sprzed etapu; jedna transakcja zakończona commitem."""
    if first in ('preflight', 'reports'):
        return  # preflight: nowa baza (krok 10); reports: znaczniki .done (R7).
    if not db.in_transaction:
        db.execute('BEGIN')
    # DROP przed DELETE i osobno: przy foreign_keys=ON DROP rodzica sprawdza odwołania dziecka.
    db.execute('DROP TABLE IF EXISTS evidence_candidate')
    db.execute('DROP TABLE IF EXISTS evidence_link')
    if first in ('import_sgjp', 'import_kwjp'):
        for table in (*DERIVED_TABLES, *(SGJP_TABLES if first == 'import_sgjp' else ()), 'corpus_evidence'):
            db.execute(f'DELETE FROM {table}')
        db.execute('DELETE FROM source_artifact WHERE source_id=?', (USE_REVIEW_ID,))
    # Commit przed set_stage(running) pierwszego etapu; w trybie `stage_boundaries` też F_FULLFSYNC (R8).
    stage_durable(db)


STAGE_RUNNERS = {'preflight': stage_preflight, 'import_sgjp': stage_import_sgjp, 'import_kwjp': stage_import_kwjp,
                 'constructions': stage_constructions, 'decisions': stage_decisions, 'links': stage_links,
                 'reports': stage_reports}


def run_stages(db, ctx, first):
    """Jedna pętla dla świeżego buildu i wznowienia: etap first i każdy dalszy liczą się od nowa."""
    order = STAGES[STAGES.index(first):]
    for stage in order:
        volume.check_active()
        ctx['stage'] = stage
        done = ctx['run'] / 'reports/.done'
        if stage == 'reports' and first != 'reports' and done.exists():
            shutil.rmtree(done)  # Znaczniki wiążą się z bazą sprzed ponownych etapów.
        STAGE_RUNNERS[stage](db, ctx)
    # Potwierdzenie niezmienności całego kompletu wejść po odczycie.
    checked = inspect_sources(ctx['manifest_path'])
    if checked['manifest_sha256'] != ctx['inputs']['manifest_sha256']:
        raise GeneratorError('Manifest zmienił się w trakcie build', 3)


def run_build(ctx, first='preflight'):
    """Etapy od first, raporty końcowe i zamknięcie próby; błąd przechodzi do wywołującego."""
    run, performance = ctx['run'], ctx['performance']
    with connect(run / 'build.sqlite', create=first == 'preflight', build=True) as db:
        reset_stage(db, first)
        run_stages(db, ctx, first)
    performance['peak_rss'] = {'value': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                               'unit': 'bytes on macOS, KiB on Linux'}
    performance['database_bytes'] = (run / 'build.sqlite').stat().st_size
    write_json(run / 'reports/performance.json', performance)
    write_json(run / 'reports/canonical-index.json', canonical_index(run))
    stages = load_json(run / 'manifest.json')['stages']
    try:
        close_attempt(run, ctx['stage'], 'incomplete' if any(stages[name]['status'] == 'pending' for name in STAGES)
                      else 'complete', 0)
    except Exception:
        pass  # Niezamknięta próba: --resume ustawi `interrupted`.
    return {'run_dir': str(run.resolve()), 'readiness': 'INCOMPLETE',
            'counts': load_json(run / 'reports/import-counts.json'),
            'completed': [name for name in STAGES if stages[name]['status'] == 'complete'],
            'pending': [name for name in STAGES if stages[name]['status'] == 'pending']}


def record_failure(error, ctx, work_volume):
    """Status failed i zamknięcie próby po błędzie; zwraca kod wyjścia (R4)."""
    # Baza jest już po rollbacku i zamknięciu (connect); teraz strażnik i kod.
    run, stage = ctx['run'], ctx['stage']
    code = exit_code(error, run, work_volume)
    try:
        set_stage(run, stage, 'failed', {'reason': str(error)})
    except Exception:
        pass  # Pełny albo odłączony dysk może uniemożliwić zapis statusu; running blokuje odbiór.
    try:
        close_attempt(run, stage, 'interrupted' if isinstance(error, KeyboardInterrupt) else 'failed', code)
    except Exception:
        pass
    return code


def build(manifest_path, run_dir, batch_size=10000, work_root=None):
    if type(batch_size) is not int or batch_size < 1 or batch_size > 10000:
        raise GeneratorError('Porcja musi mieć od 1 do 10 000 rekordów', 2)
    inputs = inspect_sources(manifest_path)
    run = Path(run_dir)
    # Strażnik przed create_run: bez wolumenu roboczego nic nie powstaje na dysku systemowym (R1).
    work_volume = volume.check_fresh(run, work_root)
    with run_lock(run):
        create_run(run, inputs, work_root=work_root, work_volume=work_volume)
        return guarded_build(stage_context(manifest_path, run, inputs, batch_size), 'preflight', work_volume)


def run_lock(run):
    """Blokada przebiegu na cały build albo --resume (`.<nazwa>.build.lock` obok symlinku); zajęta → 4."""
    lock = workfs.build_lock(run)
    if not lock.parent.is_dir():
        raise GeneratorError('Brak katalogu nadrzędnego przebiegu', 4, str(lock.parent))
    return workfs.hold_lock(lock, 'Inny build albo --resume tego przebiegu trwa (blokada)')


def guarded_build(ctx, first, work_volume):
    """Etapy od first pod strażnikiem G3; błąd zamyka próbę i dostaje kod z klasyfikatora (R4)."""
    run = ctx['run']
    ctx['stage'] = first
    volume.activate(run)
    try:
        return run_build(ctx, first)
    except BaseException as error:
        code = record_failure(error, ctx, work_volume)
        if isinstance(error, (KeyboardInterrupt, GeneratorError)):
            raise
        if isinstance(error, (OSError, sqlite3.Error, ValueError)):
            raise GeneratorError(f'Build nieukończony: {error}', code, str(run)) from error
        raise
    finally:
        volume.deactivate()


def read_run_manifest(run):
    """Krok 4: manifest przebiegu; brak albo nieczytelny → ponowny G1 (75), inaczej 4."""
    try:
        manifest = load_json(run / 'manifest.json')
        if not all(isinstance(manifest[key], dict) for key in ('stages', 'code', 'inputs')):
            raise ValueError('pola manifestu')
        # Brak pola daje KeyError/TypeError, czyli ten sam kod 4 co nieczytelny plik.
        [manifest['stages'][name]['status'] for name in STAGES]
        [manifest['code']['tree_sha256'], manifest['inputs']['manifest_sha256'], manifest['readiness']]
    except (OSError, ValueError, KeyError, TypeError) as error:
        volume.check_mounted(run)
        raise GeneratorError('Brak albo nieczytelny manifest przebiegu', 4, str(run)) from error
    return manifest


def database_resumable(run, manifest, work_volume):
    """Kroki 10–11: False, gdy preflight niegotowy albo baza bez kompletu source_artifact; quick_check ≠ ok → 77."""
    if manifest['stages']['preflight']['status'] != 'complete' or not (run / 'build.sqlite').is_file():
        return False
    try:
        with connect(run / 'build.sqlite') as db:
            if db.execute('PRAGMA quick_check').fetchall() != [('ok',)]:
                raise GeneratorError('PRAGMA quick_check bazy przebiegu ≠ ok', 77, str(run))
            present = {row[0] for row in db.execute('SELECT source_id FROM source_artifact')}
    except sqlite3.Error as error:
        raise GeneratorError(f'Baza przebiegu nie otwiera się: {error}', exit_code(error, run, work_volume),
                             str(run)) from error
    return {artifact['source_id'] for artifact in manifest['inputs']['artifacts']} <= present


def restart_in_place(run):
    """Krok 10: przebieg od preflight w tym samym katalogu (baza, journal, reports/ i lists/ od zera)."""
    for name in ('build.sqlite', 'build.sqlite-journal', 'build.sqlite-wal', 'build.sqlite-shm'):
        (run / name).unlink(missing_ok=True)
    for folder in ('reports', 'lists'):
        if (run / folder).is_dir():
            for entry in (run / folder).iterdir():
                if entry.is_dir() and not entry.is_symlink():
                    shutil.rmtree(entry)
                else:
                    entry.unlink()
    (run / 'reports').mkdir(exist_ok=True)


def resume(manifest_path, run_dir, batch_size=10000):
    """`build --resume`: kontrole 1–12 ze spec (kolejność H1), potem etapy od pierwszego niegotowego."""
    if type(batch_size) is not int or batch_size < 1 or batch_size > 10000:
        raise GeneratorError('Porcja musi mieć od 1 do 10 000 rekordów', 2)
    run = Path(run_dir)
    if not os.path.lexists(run):
        raise GeneratorError('Brak przebiegu do wznowienia', 4, str(run))
    with run_lock(run):  # Przed pierwszą zmianą: żywy build albo drugie --resume → 4.
        volume.check_mounted(run)  # 2–3: wiszący symlink, G1 → 75 (dysk przed manifestem, który leży na T7).
        manifest = read_run_manifest(run)
        if manifest['readiness'] in {'VERIFIED', 'FROZEN'}:
            raise GeneratorError(f'Przebieg ma status {manifest["readiness"]}; wznowienie po verify jest '
                                 'niedozwolone', 5, str(run))
        work_volume = manifest.get('work_volume')
        volume.check_resume(run, work_volume['marker_id'] if work_volume else None)  # G1, G2 → 76, miejsce → 78
        inputs = check_identity(manifest, manifest_path)  # kod 4, wejścia 3
        restart = not database_resumable(run, manifest, work_volume)
        if restart:
            restart_in_place(run)
        first = begin_resume(run, 'preflight' if restart else None)
        result = guarded_build(stage_context(manifest_path, run, inputs, batch_size), first, work_volume)
        return {**result, 'resumed_from': first}
