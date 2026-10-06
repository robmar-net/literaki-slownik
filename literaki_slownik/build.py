"""Import porcjowany, metryki i jawne statusy niepełnego przebiegu."""
from collections import Counter
from pathlib import Path
import resource
import sqlite3
import time
from .canonical import dumps, write_json, load_json
from .database import connect
from .inputs import GeneratorError, inspect_sources
from . import sgjp, kwjp
from .run import create_run, set_stage, STAGES
from .reports import qualifier_coverage, logical_content_report, unresolved_report, persisted_filter_impact, canonical_index, coverage_report
from .constructions import materialize_confirmed_candidates
from .links import (create_links, link_report, load_pos_map, verify_link_completeness,
                    link_stage_gate, SHARED_POS, DEFAULT_POS_MAP_VERSION)
from .decisions import materialize_assessments


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
            stage='decisions'
            start=time.monotonic()
            use_reviews=[]
            use_reference=inputs['manifest']['configurations'].get('semantic-uses')
            if use_reference:
                from .inputs import checked_file
                use_data=load_json(checked_file(Path(manifest_path).resolve().parent,use_reference))
                if (not isinstance(use_data,dict) or set(use_data)!={'schema_version','reviews'}
                        or type(use_data['schema_version']) is not int or use_data['schema_version']!=1):
                    raise GeneratorError('Nieobsługiwany format przeglądu użyć',4)
                use_reviews=use_data['reviews']
            decision_counts=materialize_assessments(db,batch_size,use_reviews=use_reviews)
            performance['diagnostic_decisions']={'seconds':time.monotonic()-start}
            write_json(run/'reports/decisions.json',decision_counts)
            # Powiązania bezpośrednie są niezależne od kwalifikacji językowej.
            # Pełny etap wymaga kompletnego zbioru konstrukcji i niezależnej kontroli krawędzi.
            stage = 'links'
            start = time.monotonic()
            allowed_pos, pos_map_version = SHARED_POS, DEFAULT_POS_MAP_VERSION
            pos_reference = inputs['manifest']['configurations'].get('pos-map')
            if pos_reference:
                from .inputs import checked_file
                pos_map = load_pos_map(checked_file(Path(manifest_path).resolve().parent, pos_reference))
                allowed_pos, pos_map_version = pos_map['pairs'], pos_map['version']
            create_links(db, allowed_pos)
            db.commit()
            links = link_report(db, inputs['manifest'].get('unavailable', []),
                                details=True, pos_map_version=pos_map_version)
            constructions_status = load_json(run / 'manifest.json')['stages']['constructions']['status']
            links['stage_completion'] = link_stage_gate(
                verify_link_completeness(db, allowed_pos), constructions_status)
            write_json(run / 'reports/links.json', links)
            if links['stage_completion']['complete']:
                set_stage(run, 'links', 'complete')
            performance['diagnostic_links'] = {'seconds': time.monotonic() - start}
            stage = 'reports'
            start = time.monotonic()
            write_json(run / 'reports/unresolved.json', unresolved_report(db))
            performance['diagnostic_unresolved'] = {'seconds': time.monotonic() - start}
            start = time.monotonic()
            write_json(run / 'reports/filter-impact.json', persisted_filter_impact(db))
            performance['diagnostic_filter_impact'] = {'seconds': time.monotonic() - start}
            quality_reference=inputs['manifest']['configurations'].get('quality')
            if quality_reference:
                from .inputs import checked_file
                from .quality import sample_persisted_analyses, sample_corpus_links
                start=time.monotonic()
                config=load_json(checked_file(Path(manifest_path).resolve().parent,quality_reference))
                write_json(run/'reports/quality-analyses.json',sample_persisted_analyses(db,config))
                performance['diagnostic_quality_analyses']={'seconds':time.monotonic()-start}
                start=time.monotonic()
                write_json(run/'reports/quality-links.json',sample_corpus_links(db,config))
                performance['diagnostic_quality_links']={'seconds':time.monotonic()-start}
                words_reference=inputs['manifest']['configurations'].get('quality-words')
                if words_reference:
                    from .quality import sample_word_analyses
                    definitions=load_json(checked_file(Path(manifest_path).resolve().parent,words_reference))
                    start=time.monotonic()
                    write_json(run/'reports/quality-words.json',sample_word_analyses(db,config,definitions))
                    performance['diagnostic_quality_words']={'seconds':time.monotonic()-start}
            start = time.monotonic()
            write_json(run / 'reports/logical-content.json', logical_content_report(db))
            performance['diagnostic_logical_content'] = {'seconds': time.monotonic() - start}
            start = time.monotonic()
            write_json(run / 'reports/coverage.json', coverage_report(db))
            performance['diagnostic_coverage'] = {'seconds': time.monotonic() - start}
            # Potwierdzenie niezmienności całego kompletu wejść po odczycie.
            checked = inspect_sources(manifest_path)
            if checked['manifest_sha256'] != inputs['manifest_sha256']:
                raise GeneratorError('Manifest zmienił się w trakcie build', 3)
        performance['peak_rss'] = {'value': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                                   'unit': 'bytes on macOS, KiB on Linux'}
        performance['database_bytes'] = (run / 'build.sqlite').stat().st_size
        write_json(run / 'reports/performance.json', performance)
        write_json(run / 'reports/canonical-index.json', canonical_index(run))
        stages = load_json(run / 'manifest.json')['stages']
        return {'run_dir': str(run.resolve()), 'readiness': 'INCOMPLETE', 'counts': counts,
                'completed': [name for name in STAGES if stages[name]['status'] == 'complete'],
                'pending': [name for name in STAGES if stages[name]['status'] == 'pending']}
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
