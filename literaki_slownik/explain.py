"""Diagnostyczne explain pełnego importu; nie nadaje końcowej kwalifikacji."""
from pathlib import Path
import json
import sqlite3
from .canonical import load_json
from .database import connect
from .decisions import assess_analysis, aggregate, VARIANTS
from .inputs import GeneratorError
from .links import availability
from .policy import assess_profile, disrecommended_checks, history_checks, usage_checks, incorrect_checks, VERSION
from .sgjp import expand_tag


def _pending(rule_id, message):
    return [{'rule_id': rule_id, 'status': 'unresolved', 'message': message, 'evidence': []}]


def _corpus(db, key, unavailable):
    built = bool(db.execute("select 1 from sqlite_master where name='evidence_link'").fetchone())
    observations = []
    if built:
        # UNION usuwa powtórzenia dowodu wskazywanego przez kilka homonimów.
        rows = db.execute('''with matched(evidence_id) as (
            select c.evidence_id from evidence_candidate c
            where c.form_id in (select id from surface_form where game_key=?)
            union
            select c.evidence_id from evidence_candidate c
            where c.lexeme_id in (select i.lexeme_id from interpretation i
                join surface_form f on f.id=i.form_id where f.game_key=?)
        ) select e.id,e.source_id,e.row_number,e.unit_1,e.unit_2,e.pos,
            e.raw_metrics,e.typed_metrics,l.method,l.status,l.sense_identity_confirmed,l.reason
            from matched m join corpus_evidence e on e.id=m.evidence_id
            join evidence_link l on l.evidence_id=e.id order by e.source_id,e.row_number''', (key, key))
        for eid, sid, row, first, second, pos, raw, typed, method, status, sense, reason in rows:
            candidates = []
            for lid, fid, lemma, original in db.execute('''select c.lexeme_id,c.form_id,l.lemma_id,f.original
                from evidence_candidate c left join lexeme l on l.id=c.lexeme_id
                left join surface_form f on f.id=c.form_id where c.evidence_id=?
                order by l.lemma_id,f.original''', (eid,)):
                candidates.append({'lexeme_id': lid, 'form_id': fid, 'lemma_id': lemma, 'original': original})
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
                pending = _pending('linguistic-policy-not-active-v1', 'Pełna polityka językowa G3/G4 nie jest jeszcze aktywna.')
                assessed = assess_analysis(original,
                                           language={v: pending + disrecommended_checks(qualifiers) + history_checks(qualifiers, v) + usage_checks(qualifiers) + incorrect_checks(qualifiers)
                                                     for v in VARIANTS},
                                           game_checks=_pending('game-metadata-not-complete-v1',
                                                                'Pozostałe udokumentowane warunki growe wymagają domknięcia.'))
                analyses.append({'interpretation_id': iid, 'source_id': sid, 'first_source_row': row,
                                 'original': original, 'lemma_id': lemma, 'raw_tag': tag,
                                 'expanded_tags': list(expand_tag(tag)), 'names': names,
                                 'qualifiers': qualifiers, 'assessment': assessed})
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
                'scope': 'diagnostic_imported_interpretations_only', 'source_presence': presence,
                'import_complete': imported, 'stages': stages, 'sources': sources,
                'analyses': analyses, 'source_aggregation': source_aggregation,
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
        lines.append(f"  Źródło: {analysis['source_id']}, pierwszy wiersz: {analysis['first_source_row']}; "
                     f"nazwy: {analysis['names'] or 'brak oznaczenia'}; kwalifikatory: {analysis['qualifiers'] or 'brak oznaczenia'}")
        for layer, result in [('język', assessed['language'][value['variant']]),
                              ('gra', assessed['game']), ('profil', assessed['profile'])]:
            lines.append(f"  {layer}: {labels[result['status']]}")
            for check in result['checks']:
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
