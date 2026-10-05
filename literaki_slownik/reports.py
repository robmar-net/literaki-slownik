"""Raporty podanych analiz; bez domniemania kompletności całego wydania."""
from collections import Counter
import hashlib
import json
import sqlite3

from .decisions import assessment, aggregate, VARIANTS
from .inputs import GeneratorError
from .canonical import dumps


def logical_content_report(db):
    """Hash bieżących relacji z trwałymi kluczami zamiast technicznych ID.

    Zamknięty schemat nie pozwala pominąć nowej tabeli lub kolumny.
    Przyszłe utrwalone decyzje wymagają rozszerzenia tego kontraktu.
    """
    columns = {
        'source_artifact': 'source_id kind metadata',
        'sgjp_record': 'source_id row_number form lemma tag names qualifiers',
        'lexeme': 'id source_id lemma_id lemma_base',
        'surface_form': 'id original nfc game_key length',
        'interpretation': 'id source_id first_row form_id lexeme_id tag names qualifiers',
        'corpus_evidence': 'id source_id row_number unit_1 unit_2 pos raw_metrics typed_metrics freq',
        'derivation_candidate': 'candidate_key rule_id original game_key lemma_id expanded_tag names qualifiers payload',
        'derivation_component': 'candidate_key position kind source_id source_row',
        'evidence_link': 'evidence_id method status sense_identity_confirmed reason',
        'evidence_candidate': 'id evidence_id lexeme_id form_id candidate_key',
    }
    queries = {
        'source_artifact': ('select source_id,kind,metadata from source_artifact order by source_id', (2,)),
        'sgjp_record': ('select source_id,row_number,form,lemma,tag,names,qualifiers from sgjp_record order by source_id,row_number', ()),
        'lexeme': ('select source_id,lemma_id,lemma_base from lexeme order by source_id,lemma_id', ()),
        'surface_form': ('select original,nfc,game_key,length from surface_form order by original', ()),
        'interpretation': ('''select i.source_id,i.first_row,f.original,l.source_id,l.lemma_id,i.tag,i.names,i.qualifiers
            from interpretation i join surface_form f on f.id=i.form_id join lexeme l on l.id=i.lexeme_id
            order by i.source_id,i.first_row,f.original,l.source_id,l.lemma_id,i.tag,i.names,i.qualifiers''', ()),
        'corpus_evidence': ('''select source_id,row_number,unit_1,unit_2,pos,raw_metrics,typed_metrics,freq
            from corpus_evidence order by source_id,row_number''', (5,6)),
        'derivation_candidate': ('''select candidate_key,rule_id,original,game_key,lemma_id,expanded_tag,names,qualifiers,payload
            from derivation_candidate order by candidate_key''', (8,)),
        'derivation_component': ('''select candidate_key,position,kind,source_id,source_row
            from derivation_component order by candidate_key,position''', ()),
        'evidence_link': ('''select e.source_id,e.row_number,l.method,l.status,l.sense_identity_confirmed,l.reason
            from evidence_link l join corpus_evidence e on e.id=l.evidence_id order by e.source_id,e.row_number''', ()),
        'evidence_candidate': ('''select e.source_id,e.row_number,l.source_id,l.lemma_id,f.original,c.candidate_key
            from evidence_candidate c join corpus_evidence e on e.id=c.evidence_id
            left join lexeme l on l.id=c.lexeme_id left join surface_form f on f.id=c.form_id
            order by e.source_id,e.row_number,l.source_id,l.lemma_id,f.original,c.candidate_key''', ()),
    }
    try:
        tables = {row[0] for row in db.execute("select name from sqlite_master where type='table' and name not like 'sqlite_%'")}
        required = set(columns) - {'evidence_link', 'evidence_candidate'}
        if not required <= tables or tables - set(columns):
            raise GeneratorError('Nieznany lub niepełny schemat logical-content', 4)
        if ('evidence_link' in tables) != ('evidence_candidate' in tables):
            raise GeneratorError('Niepełny schemat powiązań logical-content', 4)
        for table in sorted(tables):
            actual = {row[1] for row in db.execute(f'pragma table_info({table})')}
            if actual != set(columns[table].split()):
                raise GeneratorError('Nieznane kolumny logical-content', 4, table)
        if db.execute('pragma foreign_key_check').fetchone() is not None:
            raise GeneratorError('Niespójne relacje logical-content', 4)
        results = {}
        for table in sorted(tables):
            query, json_columns = queries[table]
            digest, count = hashlib.sha256(), 0
            for source_row in db.execute(query):
                row = list(source_row)
                for index in json_columns:
                    row[index] = json.loads(row[index])
                if table == 'source_artifact':
                    # Wyłącznie lokalizatory i czas pozyskania: identyfikują operację,
                    # a nie treść źródła. SHA, URL, wersja, licencja i dowody zostają.
                    row[2] = {k:v for k,v in row[2].items() if k not in ('path','resolved_path','retrieved_at')}
                    row[2]['evidence'] = [{k:v for k,v in evidence.items() if k not in ('path','resolved_path')}
                                         for evidence in row[2].get('evidence', [])]
                digest.update((dumps(row)+'\n').encode('utf-8'))
                count += 1
            results[table] = {'rows':count, 'sha256':digest.hexdigest()}
        return {'schema_version':1, 'encoding':'logical-relations-v1/json-array-utf8-lf',
                'scope':'current_schema_imports_constructions_links_not_full_release',
                'excluded_source_metadata_fields':['path','resolved_path','retrieved_at','evidence[].path','evidence[].resolved_path'],
                'tables':results, 'sha256':hashlib.sha256(dumps(results).encode('utf-8')).hexdigest()}
    except GeneratorError:
        raise
    except (sqlite3.Error, ValueError, TypeError, AttributeError) as error:
        raise GeneratorError(f'Nie można policzyć logical-content: {error}', 4) from error


def filter_impact(groups, variant, rule_order):
    """Strumień uporządkowanych, unikalnych grup {key, analyses}.

    Reguła usuwa klucz dopiero, gdy odrzuca wszystkie jego analizy.
    Kolejne efekty nie dublują analiz/kluczy odrzuconych wcześniej.
    Reguły unresolved pozostają niewiadomymi, nie odrzuceniami.
    """
    if (variant not in VARIANTS or not isinstance(rule_order, list) or not rule_order
            or any(not isinstance(rule, str) or not rule for rule in rule_order)
            or len(set(rule_order)) != len(rule_order)):
        raise GeneratorError('Raport wymaga wariantu i jawnej unikalnej kolejności filtrów', 2)
    standalone = {rule: {'rejected_analyses': 0, 'rejected_keys': 0} for rule in rule_order}
    sequential = {rule: {'new_rejected_analyses': 0, 'new_rejected_keys': 0,
                         'cumulative_rejected_analyses': 0, 'cumulative_rejected_keys': 0}
                  for rule in rule_order}
    total = {'keys': 0, 'analyses': 0}
    combined = {'rejected_analyses': 0, 'rejected_keys': 0}
    statuses = Counter()
    previous = None
    try:
        for group in groups:
            key, analyses = group['key'], group['analyses']
            if (not isinstance(key, str) or not key or not isinstance(analyses, list) or not analyses
                    or previous is not None and key <= previous):
                raise GeneratorError('Raport wymaga uporządkowanych niepustych grup bez powtórzeń', 4)
            previous = key
            if any(item['game_key'] != key for item in analyses):
                raise GeneratorError('Analiza nie należy do klucza grupy', 4)
            rejected_by_rule = {rule: set() for rule in rule_order}
            for index, item in enumerate(analyses):
                decision = item['membership'][variant]
                checked = assessment(decision['checks'])
                if decision['status'] != checked['status']:
                    raise GeneratorError('Status analizy nie zgadza się z jej warunkami', 4)
                for check in checked['checks']:
                    if check['status'] != 'reject':
                        continue
                    rule = check['rule_id']
                    if rule not in rejected_by_rule:
                        raise GeneratorError('Lista filtrów pomija regułę odrzucającą', 4, rule)
                    rejected_by_rule[rule].add(index)
            total['keys'] += 1
            total['analyses'] += len(analyses)
            statuses[aggregate(analyses, variant)['status']] += 1
            cumulative = set()
            for rule in rule_order:
                rejected = rejected_by_rule[rule]
                standalone[rule]['rejected_analyses'] += len(rejected)
                standalone[rule]['rejected_keys'] += len(rejected) == len(analyses)
                before = len(cumulative)
                cumulative.update(rejected)
                sequential[rule]['new_rejected_analyses'] += len(cumulative) - before
                sequential[rule]['new_rejected_keys'] += before < len(analyses) and len(cumulative) == len(analyses)
                sequential[rule]['cumulative_rejected_analyses'] += len(cumulative)
                sequential[rule]['cumulative_rejected_keys'] += len(cumulative) == len(analyses)
            combined['rejected_analyses'] += len(cumulative)
            combined['rejected_keys'] += len(cumulative) == len(analyses)
    except GeneratorError:
        raise
    except (KeyError, TypeError, AttributeError) as error:
        raise GeneratorError(f'Nieprawidłowe analizy raportu: {error}', 4) from error
    return {
        'schema_version': 1, 'scope': 'provided_analyses_only_not_release_membership',
        'variant': variant, 'rule_order': list(rule_order),
        'coverage': 'ASSESSED_PROVIDED_ANALYSES_ONLY' if total['keys'] else 'EMPTY_NOT_COVERAGE',
        'total': total, 'standalone': dict(sorted(standalone.items())),
        'sequential': sequential, 'combined': combined, 'assessed_key_statuses': dict(sorted(statuses.items())),
    }


def qualifier_coverage(fields):
    """Inwentaryzacja warunków, nie kompletna semantyka etykiet lub analiz.

    Wejście: unikalne pary (surowe pole kwalifikatorów, liczba interpretacji).
    Liczniki etykiet mogą się nakładać; mianownik rekordów liczymy raz po polu.
    """
    from .policy import approved_qualifier_checks, VERSION, UNEXPLAINED_FIRST_RELEASE_LABELS, UNEXPLAINED_ACCENT_LABELS
    waived_labels = UNEXPLAINED_FIRST_RELEASE_LABELS | UNEXPLAINED_ACCENT_LABELS

    inventory, counts = {}, Counter()
    try:
        for field, count in fields:
            if (not isinstance(field, str) or type(count) is not int or count < 1
                    or field in inventory):
                raise GeneratorError('Pokrycie wymaga unikalnych pól i dodatnich liczników całkowitych', 4)
            inventory[field] = count
            for label in set(field.split('|')) - {''}:
                counts[label] += count
    except GeneratorError:
        raise
    except (TypeError, ValueError) as error:
        raise GeneratorError(f'Nieprawidłowa inwentaryzacja kwalifikatorów: {error}', 4) from error

    label_rows, mapped = [], set()
    for label, count in sorted(counts.items()):
        checks = {v: approved_qualifier_checks(label, v) for v in VARIANTS}
        conditions = {v: assessment(value) for v, value in checks.items()}
        has_condition = any(checks.values())
        if has_condition:
            mapped.add(label)
        waived = label in waived_labels
        label_rows.append({'label': label, 'compact_interpretations': count,
                           'gloss_status': 'unestablished' if waived else 'not_assessed_by_this_report',
                           'first_release_gloss_requirement_waived': waived,
                           'has_known_condition': has_condition, 'condition_assessment': conditions})
    field_rows = []
    totals = {'compact_interpretations': sum(inventory.values()), 'fields': len(inventory),
              'literal_labels': len(counts), 'records_with_any_condition': 0,
              'records_with_unmapped_label': 0, 'records_without_qualifiers': 0,
              'records_with_unexplained_first_release_label': 0}
    for field, count in sorted(inventory.items()):
        labels = sorted(set(field.split('|')) - {''})
        unknown = sorted(set(labels) - mapped)
        unexplained = sorted(set(labels) & waived_labels)
        totals['records_with_unexplained_first_release_label'] += count if unexplained else 0
        totals['records_with_any_condition'] += count if set(labels) & mapped else 0
        totals['records_with_unmapped_label'] += count if unknown else 0
        totals['records_without_qualifiers'] += count if not labels else 0
        field_rows.append({'qualifiers': field, 'compact_interpretations': count, 'labels': labels,
                           'unmapped_labels': unknown,
                           'unexplained_first_release_labels': unexplained,
                           'condition_assessment': {v: assessment(approved_qualifier_checks(field, v))
                                                    for v in VARIANTS}})
    return {'schema_version': 1, 'policy_version': VERSION,
            'scope': 'qualifier_conditions_only_not_full_qualification',
            'coverage': 'OBSERVED_FIELDS' if inventory else 'EMPTY_NOT_COVERAGE',
            'full_qualification_pending': True, 'totals': totals,
            'label_counts_overlap': True, 'record_categories_overlap': True,
            'notice': 'Znany warunek nie oznacza pełnej semantyki etykiety ani dopuszczenia analizy. '
                      'Brak etykiety nie dowodzi poprawności; nie sumujemy nakładających się liczników.',
            'labels': label_rows, 'fields': field_rows,
            'unexplained_first_release_labels': sorted(set(counts) & waived_labels),
            'unmapped_labels': sorted(set(counts) - mapped)}


def construction_scope_report(db):
    """Analizy kandydatów poza zakresem nie są licznikiem błędnych słów."""
    from .policy import release_scope_checks
    counts = Counter()
    outside = Counter()
    for rule, original, n in db.execute('select rule_id,original,count(*) from derivation_candidate group by rule_id,original order by rule_id,original'):
        status = assessment(release_scope_checks(dict(rule_id=rule,original=original)))['status']
        counts[status] += n
        if status=='reject':
            outside[original] += n
    return {'schema_version':1,'scope':'candidate_release_scope_not_lexical_correctness_or_final_lists',
            'rule_id':'first-release-contraction-scope-v1',
            'in_scope_candidate_analyses':counts['accept'],
            'outside_scope_candidate_analyses':counts['reject'],
            'unresolved_scope_candidate_analyses':counts['unresolved'],
            'outside_scope_forms':[{'original':w,'candidate_analyses':n} for w,n in sorted(outside.items())]}
