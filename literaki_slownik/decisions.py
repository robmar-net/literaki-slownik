"""Wszystkie warunki przy jednej analizie; agregacja dopiero po kwalifikacji."""
from .inputs import GeneratorError
from .policy import assess_profile, spelling_checks

STATUSES = frozenset({'accept', 'reject', 'unresolved'})
VARIANTS = ('broad', 'standard')


def assessment(checks):
    checks = list(checks)
    for check in checks:
        if (not isinstance(check, dict) or check.get('status') not in STATUSES
                or not check.get('rule_id') or not check.get('message')
                or not isinstance(check.get('evidence'), list)):
            raise GeneratorError('Nieprawidłowy wynik warunku kwalifikacji', 4)
    if not checks:
        checks = [{'rule_id': 'assessment-not-evaluated-v1', 'status': 'unresolved',
                   'message': 'Brak oceny wymaganych warunków.', 'evidence': []}]
    states = {c['status'] for c in checks}
    status = 'reject' if 'reject' in states else 'unresolved' if 'unresolved' in states else 'accept'
    return {'status': status, 'checks': checks}


def assess_analysis(original, *, language, game_checks):
    if set(language) != set(VARIANTS):
        raise GeneratorError('Wymagane odrębne oceny BROAD i STANDARD', 4)
    languages = {variant: assessment(language[variant]) for variant in VARIANTS}
    if languages['standard']['status'] == 'accept' and languages['broad']['status'] != 'accept':
        raise GeneratorError('STANDARD nie jest podzbiorem BROAD dla tej analizy', 4)
    # Pusta ocena growa jest unknown, nawet gdy sprawdzenie samej wielkości liter przechodzi.
    game = assessment(assessment(game_checks)['checks'] + spelling_checks(original))
    profile = assess_profile(original)
    membership = {variant: assessment(languages[variant]['checks'] + game['checks'] + profile['checks'])
                  for variant in VARIANTS}
    return {'original': original, 'game_key': profile['game_key'],
            'language': languages, 'game': game, 'profile': profile, 'membership': membership}


def aggregate(analyses, variant):
    if variant not in VARIANTS:
        raise GeneratorError('Nieznany wariant słownika', 2)
    if len({analysis['game_key'] for analysis in analyses}) > 1:
        raise GeneratorError('Nie można agregować analiz różnych kluczy słów', 4)
    statuses = {analysis['membership'][variant]['status'] for analysis in analyses}
    if statuses - STATUSES:
        raise GeneratorError('Nieprawidłowy status analizy', 4)
    status = ('absent' if not statuses else 'accept' if 'accept' in statuses else
              'unresolved' if 'unresolved' in statuses else 'reject')
    return {'status': status, 'variant': variant, 'analyses_count': len(analyses)}
