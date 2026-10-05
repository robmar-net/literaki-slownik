"""Raporty podanych analiz; bez domniemania kompletności całego wydania."""
from collections import Counter

from .decisions import assessment, aggregate, VARIANTS
from .inputs import GeneratorError


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
    from .policy import approved_qualifier_checks, VERSION

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
        label_rows.append({'label': label, 'compact_interpretations': count,
                           'has_known_condition': has_condition, 'condition_assessment': conditions})
    field_rows = []
    totals = {'compact_interpretations': sum(inventory.values()), 'fields': len(inventory),
              'literal_labels': len(counts), 'records_with_any_condition': 0,
              'records_with_unmapped_label': 0, 'records_without_qualifiers': 0}
    for field, count in sorted(inventory.items()):
        labels = sorted(set(field.split('|')) - {''})
        unknown = sorted(set(labels) - mapped)
        totals['records_with_any_condition'] += count if set(labels) & mapped else 0
        totals['records_with_unmapped_label'] += count if unknown else 0
        totals['records_without_qualifiers'] += count if not labels else 0
        field_rows.append({'qualifiers': field, 'compact_interpretations': count, 'labels': labels,
                           'unmapped_labels': unknown,
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
            'unmapped_labels': sorted(set(counts) - mapped)}
