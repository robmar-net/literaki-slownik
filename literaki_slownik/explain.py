"""Diagnostyczne explain pełnego importu; nie nadaje końcowej kwalifikacji."""
from pathlib import Path
import json
import hashlib
import sqlite3
from .canonical import load_json, dumps
from .database import connect
from .decisions import assess_analysis, aggregate, VARIANTS
from .inputs import GeneratorError
from .links import availability
from .policy import assess_profile, approved_qualifier_checks, orthography_checks, release_scope_checks, construction_orthography_checks, VERSION
from .sgjp import expand_tag, tag_errata
from .constructions import impt_particle_candidates, by_aglt_candidates, preposition_n_candidates, mobile_by_aglt_candidates, mobile_aglt_candidates, mobile_by_sequence_candidates, BY_AGLT_ENDINGS


def _pending(rule_id, message):
    return [{'rule_id': rule_id, 'status': 'unresolved', 'message': message, 'evidence': []}]


def _assess(original, qualifiers, additional_checks=(), source_analyses=(), candidate=None):
    pending = _pending('linguistic-policy-not-active-v1', 'Pełna polityka językowa G3/G4 nie jest jeszcze aktywna.')
    return assess_analysis(original,
                           language={v: pending + approved_qualifier_checks(qualifiers, v) + list(additional_checks) +
                           [check for source in source_analyses for check in orthography_checks(source,v)] + construction_orthography_checks(candidate,v) for v in VARIANTS},
                           scope_checks=release_scope_checks(candidate),
                           game_checks=_pending('game-metadata-not-complete-v1',
                                                'Pozostałe udokumentowane warunki growe wymagają domknięcia.'))


def _construction_sources(db, key):
    rows = db.execute('''select i.source_id,i.first_row,f.original,l.lemma_id,
        i.tag,i.names,i.qualifiers from interpretation i
        join surface_form f on f.id=i.form_id join lexeme l on l.id=i.lexeme_id
        where f.game_key=? order by f.original,i.source_id,l.lemma_id,i.tag,i.names,i.qualifiers''', (key,))
    fields = ('source_id','first_source_row','original','lemma_id','raw_tag','names','qualifiers')
    return [dict(zip(fields,row)) for row in rows]


def _derivations(db, key):
    """Odtwórz tylko potwierdzone klasy z rzeczywistych składników importu."""
    candidates = []
    suffix = 'że' if key.endswith('że') else 'ż' if key.endswith('ż') else None
    if suffix and len(key) > len(suffix):
        for source in _construction_sources(db, key[:-len(suffix)]):
            candidates.extend(impt_particle_candidates(source))
    for ending in list(BY_AGLT_ENDINGS.values()) + ['e'+x for x in BY_AGLT_ENDINGS.values()]:
        if not key.endswith(ending) or len(key) <= len(ending):
            continue
        operators = _construction_sources(db, key[:-len(ending)])
        endings = [s for s in _construction_sources(db, ending)
                   if s['raw_tag'].split(':',1)[0] == 'aglt']
        for operator in operators:
            for aglt in endings:
                if aglt['raw_tag'].endswith(':nwok'):
                    candidates.extend(by_aglt_candidates(operator, aglt))
                    candidates.extend(mobile_by_aglt_candidates(operator, aglt))
                candidates.extend(mobile_aglt_candidates(operator, aglt))
    for ending in [None]+list(BY_AGLT_ENDINGS.values()):
        suffix='by'+(ending or '')
        if not key.endswith(suffix) or len(key)<=len(suffix):
            continue
        hosts=_construction_sources(db,key[:-len(suffix)])
        operators=_construction_sources(db,'by')
        endings=[None] if ending is None else _construction_sources(db,ending)
        for host in hosts:
            for operator in operators:
                for aglt in endings:
                    candidates.extend(mobile_by_sequence_candidates(host,operator,aglt))
    if key.endswith('ń') and len(key) > 1:
        for preposition in _construction_sources(db, key[:-1]):
            for pronoun in _construction_sources(db, 'ń'):
                candidates.extend(preposition_n_candidates(preposition, pronoun))
    result = []
    stored = bool(db.execute("select 1 from sqlite_master where name='derivation_candidate'").fetchone())
    for candidate in candidates:
        proof = candidate.get('linguistic_evidence')
        assessed = _assess(candidate['original'], candidate['qualifiers'], [proof] if proof else [],
                           [c['interpretation'] for c in candidate['components'] if c['kind']=='source_interpretation'],candidate=candidate)
        if assessed['game_key'] == key:
            candidate_key = hashlib.sha256(dumps(candidate).encode('utf-8')).hexdigest()
            present = stored and db.execute(
                'select 1 from derivation_candidate where candidate_key=?', (candidate_key,)).fetchone()
            result.append({**candidate, 'persisted_candidate_key': candidate_key if present else None,
                           'assessment': assessed})
    return result


def _corpus(db, key, unavailable):
    built = bool(db.execute("select 1 from sqlite_master where name='evidence_link'").fetchone())
    observations = []
    if built:
        derived_links = ('candidate_key' in {r[1] for r in db.execute('pragma table_info(evidence_candidate)')}
                         and bool(db.execute("select 1 from sqlite_master where name='derivation_candidate'").fetchone()))
        derived_union = '''union select c.evidence_id from evidence_candidate c
            join derivation_candidate d on d.candidate_key=c.candidate_key where d.game_key=?''' if derived_links else ''
        # UNION usuwa powtórzenia dowodu wskazywanego przez kilka homonimów.
        rows = db.execute('''with matched(evidence_id) as (
            select c.evidence_id from evidence_candidate c
            where c.form_id in (select id from surface_form where game_key=?)
            union
            select c.evidence_id from evidence_candidate c
            where c.lexeme_id in (select i.lexeme_id from interpretation i
                join surface_form f on f.id=i.form_id where f.game_key=?)
        ''' + derived_union + ''') select e.id,e.source_id,e.row_number,e.unit_1,e.unit_2,e.pos,
            e.raw_metrics,e.typed_metrics,l.method,l.status,l.sense_identity_confirmed,l.reason
            from matched m join corpus_evidence e on e.id=m.evidence_id
            join evidence_link l on l.evidence_id=e.id order by e.source_id,e.row_number''',
            (key,key,key) if derived_links else (key,key))
        for eid, sid, row, first, second, pos, raw, typed, method, status, sense, reason in rows:
            candidates = []
            candidate_columns = 'coalesce(f.original,d.original),c.candidate_key' if derived_links else 'f.original,null'
            candidate_join = 'left join derivation_candidate d on d.candidate_key=c.candidate_key' if derived_links else ''
            for lid, fid, lemma, original, candidate_key in db.execute('''select c.lexeme_id,c.form_id,l.lemma_id,''' + candidate_columns + '''
                from evidence_candidate c left join lexeme l on l.id=c.lexeme_id
                left join surface_form f on f.id=c.form_id ''' + candidate_join + ''' where c.evidence_id=?
                order by l.lemma_id,4,5''', (eid,)):
                candidates.append({'lexeme_id': lid, 'form_id': fid, 'lemma_id': lemma,
                                   'original': original, 'candidate_key': candidate_key})
            metrics = json.loads(typed)
            observations.append({'evidence_id': eid, 'source_id': sid, 'row_number': row,
                                 'unit_1': first, 'unit_2': second, 'pos': pos,
                                 'raw_metrics': json.loads(raw), 'typed_metrics': metrics,
                                 'method': method, 'link_status': status,
                                 'sense_identity_confirmed': bool(sense), 'reason': reason,
                                 'availability': availability(observed=metrics), 'candidates': candidates})
    return {'links_available': built, 'observations': observations,
            'absence_is_not_zero': True,
            'reason': 'Powiązania strukturalne nie rozstrzygają sensu ani dopuszczalności.' if built else
                      'Powiązania nie są jeszcze zbudowane; brak obserwacji nie oznacza braku w korpusie.',
            'unavailable': [{'source_id': item['source_id'], **availability(unavailable_reason=item['reason'])}
                            for item in unavailable]}


def explain(run_dir, word, variant='standard'):
    if variant not in VARIANTS or not isinstance(word, str) or not word:
        raise GeneratorError('Wymagane niepuste słowo i wariant broad/standard', 2)
    run = Path(run_dir)
    try:
        manifest = load_json(run / 'manifest.json')
        if manifest.get('schema_version') != 1 or manifest.get('readiness') not in {'INCOMPLETE', 'VERIFIED', 'FROZEN'}:
            raise GeneratorError('Nieobsługiwany manifest przebiegu', 4, str(run))
        stages = manifest['stages']
        imported = stages['import_sgjp']['status'] == 'complete'
        query = assess_profile(word)
        analyses, sources = [], {}
        with connect(run / 'build.sqlite', readonly=True) as db:
            rows = db.execute('''select i.id,i.source_id,i.first_row,f.original,l.lemma_id,
                i.tag,i.names,i.qualifiers from interpretation i
                join surface_form f on f.id=i.form_id join lexeme l on l.id=i.lexeme_id
                where f.game_key=? order by f.original,i.source_id,l.lemma_id,i.tag,i.names,i.qualifiers''',
                (query['game_key'],))
            for iid, sid, row, original, lemma, tag, names, qualifiers in rows:
                if sid not in sources:
                    metadata = db.execute('select metadata from source_artifact where source_id=?', (sid,)).fetchone()[0]
                    sources[sid] = json.loads(metadata)
                assessed = _assess(original, qualifiers, source_analyses=[dict(original=original,lemma_id=lemma,raw_tag=tag)])
                analyses.append({'interpretation_id': iid, 'source_id': sid, 'first_source_row': row,
                                 'original': original, 'lemma_id': lemma, 'raw_tag': tag,
                                 'expanded_tags': list(expand_tag(tag)), 'names': names,
                                 'qualifiers': qualifiers, 'assessment': assessed,
                                 'tag_errata': tag_errata(sources[sid].get('sha256'),lemma,original,tag)})
            derivations = _derivations(db, query['game_key'])
            for candidate in derivations:
                for component in candidate['components']:
                    if component['kind'] != 'source_interpretation':
                        continue
                    sid = component['interpretation']['source_id']
                    if sid not in sources:
                        metadata = db.execute('select metadata from source_artifact where source_id=?', (sid,)).fetchone()[0]
                        sources[sid] = json.loads(metadata)
            unavailable = manifest['inputs']['manifest'].get('unavailable', [])
            corpus = _corpus(db, query['game_key'], unavailable)
        presence = 'present' if analyses else 'absent' if imported else 'not_observed_in_incomplete_import'
        diagnostics = [] if imported else [{'code': 'INCOMPLETE_SGJP_IMPORT',
                                            'message': 'Import SGJP nieukończony; odczytana część nie rozstrzyga braku w źródle.'}]
        source_aggregation = aggregate([a['assessment'] for a in analyses], variant)
        if not analyses and not imported:
            source_aggregation['status'] = 'unresolved'
        return {'query': {'word': word, 'nfc': query['nfc'], 'game_key': query['game_key']},
                'variant': variant, 'readiness': manifest['readiness'], 'policy_version': VERSION,
                'scope': 'diagnostic_import_and_confirmed_derivation_candidates', 'source_presence': presence,
                'import_complete': imported, 'stages': stages, 'sources': sources,
                'analyses': analyses, 'source_aggregation': source_aggregation, 'derivations': derivations,
                'list_membership': {'status': 'unresolved',
                                    'reason': 'Diagnostyka importu; pełna polityka i konstrukcje nie są jeszcze zaimplementowane.'},
                'corpus': corpus, 'diagnostics': diagnostics}
    except GeneratorError:
        raise
    except (OSError, sqlite3.Error, ValueError, KeyError, TypeError, AttributeError) as error:
        raise GeneratorError(f'Nie można odczytać explain: {error}', 4, str(run)) from error


def format_explanation(value):
    labels = {'accept': 'dopuszczone', 'reject': 'odrzucone', 'unresolved': 'niewiadome'}
    presence = {'present': 'wpis istnieje', 'absent': 'brak w kompletnym imporcie SGJP',
                'not_observed_in_incomplete_import': 'brak w odczytanej części; import nieukończony'}
    lines = [f"Słowo: {value['query']['word']} · klucz: {value['query']['game_key']}",
             f"Obecność źródłowa: {presence[value['source_presence']]} · przebieg: {value['readiness']}",
             'Ocena listy: niewiadome — diagnostyka importu, pełna polityka nieaktywna.',
             f"Analizy: {len(value['analyses'])}"]
    for analysis in value['analyses']:
        assessed = analysis['assessment']
        lines.append(f"\n{analysis['original']} · {analysis['lemma_id']} · {analysis['raw_tag']}")
        for erratum in analysis.get('tag_errata', []):
            lines.append(f"  Errata tagu: {erratum['corrected_tag']} — {erratum['message']}")
        lines.append(f"  Źródło: {analysis['source_id']}, pierwszy wiersz: {analysis['first_source_row']}; "
                     f"nazwy: {analysis['names'] or 'brak oznaczenia'}; kwalifikatory: {analysis['qualifiers'] or 'brak oznaczenia'}")
        for layer, result in [('język', assessed['language'][value['variant']]),
                              ('gra', assessed['game']), ('profil', assessed['profile']), ('zakres wydania', assessed['release_scope'])]:
            lines.append(f"  {layer}: {labels[result['status']]}")
            for check in result['checks']:
                lines.append(f"    {check['rule_id']}: {labels[check['status']]} — {check['message']}")
    lines.append(f"\nKandydaci konstrukcji: {len(value['derivations'])}; pełne dopuszczenie nieustalone.")
    for candidate in value['derivations']:
        lines.append(f"  {candidate['original']} · {candidate['rule_id']} · {candidate['expanded_tag']}")
        if candidate['persisted_candidate_key']:
            lines.append(f"    Zapisany ślad: {candidate['persisted_candidate_key']}")
        for component in candidate['components']:
            if component['kind'] == 'source_interpretation':
                source = component['interpretation']
                lines.append(f"    Składnik: {source['original']} · {source['lemma_id']} · {source['raw_tag']} · "
                             f"{source['source_id']}, wiersz {source['first_source_row']}; "
                             f"nazwy: {source['names'] or 'brak oznaczenia'}; "
                             f"kwalifikatory: {source['qualifiers'] or 'brak oznaczenia'}")
            else:
                lines.append(f"    Partykuła: {component['original']} · {component['rule_id']}")
        for check in candidate['assessment']['membership'][value['variant']]['checks']:
            lines.append(f"    {check['rule_id']}: {labels[check['status']]} — {check['message']}")
    lines.append(f"\nObserwacje korpusowe: {len(value['corpus']['observations'])}; nie oznaczają pewnej tożsamości sensu.")
    lines.append(value['corpus']['reason'])
    for item in value['corpus']['observations']:
        lines.append(f"  {item['source_id']} · {item['unit_1']} · {item['link_status']} · "
                     f"F={item['typed_metrics']['freq']} przy jednostce korpusu; kandydaci: {len(item['candidates'])}")
    for item in value['corpus']['unavailable']:
        lines.append(f"  {item['source_id']}: {item['status']} — {item['reason']}")
    for diagnostic in value['diagnostics']:
        lines.append(diagnostic['message'])
    return '\n'.join(lines)
