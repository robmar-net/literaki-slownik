"""Import porcjowany, metryki i jawne statusy niepełnego przebiegu."""
from collections import Counter
from pathlib import Path
import resource
import sqlite3
import time
from .canonical import dumps, write_json
from .database import connect
from .inputs import GeneratorError, inspect_sources
from . import sgjp, kwjp
from .run import create_run, set_stage
from .reports import qualifier_coverage, logical_content_report
from .constructions import materialize_confirmed_candidates
from .links import create_links, link_report


def flush(db, sql, batch):
    if batch:
        db.executemany(sql, batch)
        db.commit()
        batch.clear()


def import_sgjp(db, artifact, batch_size):
    sid = artifact['source_id']
    batch, count = [], 0
    for number, fields in sgjp.rows(artifact['resolved_path']):
        batch.append((sid, number, *fields))
        count += 1
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
    compact = db.execute('SELECT count(*) FROM interpretation WHERE source_id=?', (sid,)).fetchone()[0]
    expanded = sum(n * sgjp.tag_size(tag) for tag, n in db.execute(
        'SELECT tag,count(*) FROM interpretation WHERE source_id=? GROUP BY tag', (sid,)))
    return {'records': count, 'interpretations': compact, 'duplicates': count - compact,
            'expanded_alternatives': expanded,
            'lexemes': db.execute('SELECT count(*) FROM lexeme WHERE source_id=?', (sid,)).fetchone()[0],
            'original_forms': db.execute('SELECT count(DISTINCT form_id) FROM interpretation WHERE source_id=?', (sid,)).fetchone()[0]}


def import_kwjp(db, artifact, batch_size):
    sid = artifact['source_id']
    batch, count, sum_freq = [], 0, 0
    for number, raw, typed in kwjp.rows(artifact['resolved_path'], artifact['kind']):
        if typed['total_freq'] < artifact.get('publication_threshold', 0):
            raise GeneratorError('KWJP poniżej deklarowanego progu publikacji', 4, sid, number)
        unit = raw.get('lemma', raw.get('form', raw.get('unit_1')))
        metrics = {k: raw[k] for k in typed}
        batch.append((sid, number, unit, raw.get('unit_2'), raw.get('pos'), dumps(metrics), dumps(typed), typed['freq']))
        count += 1
        sum_freq += typed['freq']
        if len(batch) >= batch_size:
            flush(db, 'INSERT INTO corpus_evidence(source_id,row_number,unit_1,unit_2,pos,raw_metrics,typed_metrics,freq) VALUES (?,?,?,?,?,?,?,?)', batch)
    flush(db, 'INSERT INTO corpus_evidence(source_id,row_number,unit_1,unit_2,pos,raw_metrics,typed_metrics,freq) VALUES (?,?,?,?,?,?,?,?)', batch)
    return {'records': count, 'sum_freq': sum_freq}


def build(manifest_path, run_dir, batch_size=10000):
    if type(batch_size) is not int or batch_size < 1 or batch_size > 10000:
        raise GeneratorError('Porcja musi mieć od 1 do 10 000 rekordów', 2)
    inputs = inspect_sources(manifest_path)
    run = Path(run_dir)
    create_run(run, inputs)
    stage = 'preflight'
    counts, performance = {}, {}
    try:
        set_stage(run, stage, 'complete')
        with connect(run / 'build.sqlite', create=True) as db:
            for artifact in inputs['artifacts']:
                db.execute('INSERT INTO source_artifact VALUES (?,?,?)',
                           (artifact['source_id'], artifact['kind'], dumps(artifact)))
            db.commit()
            for stage, predicate, importer in [
                ('import_sgjp', lambda a: a['kind'] == 'sgjp_tab', import_sgjp),
                ('import_kwjp', lambda a: a['kind'].startswith('kwjp_'), import_kwjp),
            ]:
                start = time.monotonic()
                set_stage(run, stage, 'running')
                for artifact in filter(predicate, inputs['artifacts']):
                    sid = artifact['source_id']
                    metrics = importer(db, artifact, batch_size)
                    counts[sid] = metrics
                    for key, expected in artifact.get('expected_counts', {}).items():
                        if metrics.get(key) != expected:
                            raise GeneratorError(f'Niezgodne rozliczenie {key}: {metrics.get(key)} != {expected}', 4, sid)
                performance[stage] = {'seconds': time.monotonic() - start}
                set_stage(run, stage, 'complete')
            inventory = {name: dict(db.execute(f'SELECT {name},count(*) FROM interpretation GROUP BY {name}'))
                         for name in ('tag', 'names', 'qualifiers')}
            write_json(run / 'reports/import-counts.json', counts)
            write_json(run / 'reports/inventory.json', inventory)
            write_json(run / 'reports/qualifier-conditions.json',
                       qualifier_coverage(inventory['qualifiers'].items()))
            # Potwierdzony podzbiór pozostaje diagnostyczny; status etapu nadal pending.
            stage = 'constructions'
            start = time.monotonic()
            construction_counts = materialize_confirmed_candidates(db, batch_size)
            performance['diagnostic_constructions'] = {'seconds': time.monotonic() - start}
            write_json(run / 'reports/construction-candidates.json', construction_counts)
            # Powiązania bezpośrednie są niezależne od kwalifikacji językowej.
            # Pełny etap czeka także na powiązania wszystkich klas konstrukcji.
            stage = 'links'
            start = time.monotonic()
            create_links(db)
            db.commit()
            write_json(run / 'reports/links.json',
                       link_report(db, inputs['manifest'].get('unavailable', [])))
            performance['diagnostic_links'] = {'seconds': time.monotonic() - start}
            stage = 'reports'
            start = time.monotonic()
            write_json(run / 'reports/logical-content.json', logical_content_report(db))
            performance['diagnostic_logical_content'] = {'seconds': time.monotonic() - start}
            # Potwierdzenie niezmienności całego kompletu wejść po odczycie.
            checked = inspect_sources(manifest_path)
            if checked['manifest_sha256'] != inputs['manifest_sha256']:
                raise GeneratorError('Manifest zmienił się w trakcie build', 3)
        performance['peak_rss'] = {'value': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                                   'unit': 'bytes on macOS, KiB on Linux'}
        performance['database_bytes'] = (run / 'build.sqlite').stat().st_size
        write_json(run / 'reports/performance.json', performance)
        return {'run_dir': str(run.resolve()), 'readiness': 'INCOMPLETE', 'counts': counts,
                'completed': ['preflight', 'import_sgjp', 'import_kwjp'],
                'pending': ['constructions', 'decisions', 'links', 'reports']}
    except BaseException as error:
        try:
            set_stage(run, stage, 'failed', {'reason': str(error)})
        except OSError:
            pass  # Pełny dysk może uniemożliwić nawet zapis statusu; running blokuje odbiór.
        if isinstance(error, (KeyboardInterrupt, GeneratorError)):
            raise
        if isinstance(error, (OSError, sqlite3.Error, ValueError)):
            raise GeneratorError(f'Build nieukończony: {error}', 4, str(run)) from error
        raise
