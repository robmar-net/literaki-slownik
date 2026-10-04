"""Potwierdzone warunki i profil; pełna polityka językowa nadal nieukończona."""
import unicodedata
from .inputs import GeneratorError

ALPHABET = 'aąbcćdeęfghijklłmnńoóprsśtuwyzźż'
VERSION = 'diagnostic-approved-conditions-v3'
DISRECOMMENDED_LABELS = frozenset({
    'niezal.', 'daw.,niezal.', 'niezal.,przest.', 'niezal.,rzad.', 'niezal.,pot.',
})


HISTORICAL_LABELS = frozenset({
    "arch.,char.",
    "arch.,char.,biol.",
    "arch.,char.,bot.",
    "arch.,char.,bud.",
    "arch.,char.,chem.",
    "arch.,char.,chem.,fiz.",
    "arch.,char.,chor.",
    "arch.,char.,edyt.",
    "arch.,char.,ekon.",
    "arch.,char.,fiz.",
    "arch.,char.,geol.",
    "arch.,char.,hist.",
    "arch.,char.,hydrol.",
    "arch.,char.,jęz.",
    "arch.,char.,komp.",
    "arch.,char.,kulin.",
    "arch.,char.,lit.",
    "arch.,char.,mat.",
    "arch.,char.,med.",
    "arch.,char.,meteor.",
    "arch.,char.,mit.",
    "arch.,char.,mors.",
    "arch.,char.,mot.",
    "arch.,char.,muz.",
    "arch.,char.,paleont.",
    "arch.,char.,praw.",
    "arch.,char.,psych.",
    "arch.,char.,rel.",
    "arch.,char.,sport.",
    "arch.,char.,techn.",
    "arch.,char.,term.",
    "arch.,char.,wojsk.",
    "arch.,char.,zool.",
    "arch.,char.,żegl.",
    "arch._(tylko_po_\"ku\")",
    "daw.",
    "daw.,anat.",
    "daw.,arch.,char.",
    "daw.,arch.,char.,rel.",
    "daw.,bot.",
    "daw.,bud.",
    "daw.,char.",
    "daw.,char.,karc.",
    "daw.,chem.,fiz.",
    "daw.,daw._dziś_gwar.",
    "daw.,daw._dziś_gwar.,rzad.",
    "daw.,etn.",
    "daw.,flis.",
    "daw.,gry",
    "daw.,gwar.",
    "daw.,górn.",
    "daw.,hist.",
    "daw.,hom.",
    "daw.,hom.,karc.",
    "daw.,hom.,rel.",
    "daw.,indyw.",
    "daw.,iron.",
    "daw.,jęz.",
    "daw.,karc.",
    "daw.,kulin.",
    "daw.,mat.",
    "daw.,meteor.",
    "daw.,mikol.",
    "daw.,monet.",
    "daw.,niepopr.",
    "daw.,niezal.",
    "daw.,num.",
    "daw.,pogard.",
    "daw.,pot.",
    "daw.,praw.",
    "daw.,przest.",
    "daw.,przest.,rzad.",
    "daw.,pszcz.",
    "daw.,reg.",
    "daw.,reg.,char.",
    "daw.,reg.,hom.",
    "daw.,rel.",
    "daw.,rzad.",
    "daw.,rzad.,akcent",
    "daw.,rzad.,anat.",
    "daw.,rzad.,char.",
    "daw.,rzad.,hist.",
    "daw.,rzad.,hom.",
    "daw.,rzad.,jęz.",
    "daw.,rzad.,term.",
    "daw.,rzad.,zool.",
    "daw.,sport.",
    "daw.,techn.",
    "daw.,wojsk.",
    "daw.,wulg.",
    "daw.,z_D.",
    "daw.,zool.",
    "daw.,łow.",
    "daw.,środ.",
    "daw.,żart.",
    "daw.,żegl.",
    "gwar.,przest.",
    "gwar.,rzad.,arch.,char.",
    "indyw.,arch.,char.",
    "iron.,przest.",
    "iron.,żart.,arch.,char.",
    "książk.,arch.,char.",
    "książk.,przest.",
    "książk.,żart.,arch.,char.",
    "niepopr.,przest.",
    "niepopr.,rzad.,arch.,char.",
    "niezal.,przest.",
    "pogard.,pot.,arch.,char.",
    "pogard.,przest.",
    "pot.,arch.,char.",
    "pot.,przest.",
    "pot.,przest.,char.",
    "pot.,przest.,hom.",
    "przen.,arch.,char.",
    "przest.",
    "przest.,anat.",
    "przest.,arch.,char.",
    "przest.,arch.,char.,lit.",
    "przest.,char.",
    "przest.,druk.",
    "przest.,fiz.",
    "przest.,gry",
    "przest.,hip.",
    "przest.,hist.",
    "przest.,hom.",
    "przest.,hom.,lit.",
    "przest.,jęz.",
    "przest.,karc.",
    "przest.,leśn.",
    "przest.,lit.",
    "przest.,mat.",
    "przest.,med.",
    "przest.,monet.",
    "przest.,muz.",
    "przest.,paleont.",
    "przest.,podniosłe",
    "przest.,przest._dziś_książk.",
    "przest.,reg.",
    "przest.,roln.",
    "przest.,rzad.",
    "przest.,rzad.,hom.",
    "przest.,rzad.,techn.",
    "przest.,rzad.,żart.",
    "przest.,sport.",
    "przest.,szkol.",
    "przest.,szt.",
    "przest.,teatr.",
    "przest.,techn.",
    "przest.,wojsk.",
    "przest.,wulg.",
    "przest.,z_D.",
    "przest.,zool.",
    "przest.,łow.",
    "przest.,środ.",
    "przest.,żart.",
    "przest.,żegl.",
    "przest._dziś_książk.,arch.,char.",
    "rzad.,arch.,char.",
    "rzad.,arch.,char.,term.",
    "żart.,arch.,char.",
})
CURRENT_USAGE_LABELS = frozenset({
    "daw.,daw._dziś_gwar.",
    "daw.,daw._dziś_gwar.,rzad.",
    "daw._dziś_fraz.",
    "daw._dziś_gwar.",
    "daw._dziś_gwar.,rzad.",
    "daw._dziś_gwar.,z_D.",
    "daw._dziś_rzad.",
    "daw._dziś_środ.",
    "pogard.,przest._dziś_książk.",
    "przest.,przest._dziś_książk.",
    "przest._dziś_gwar.",
    "przest._dziś_książk.",
    "przest._dziś_książk.,arch.,char.",
    "przest._dziś_książk.,hom.",
    "przest._dziś_książk.,rzad.",
    "przest._dziś_książk.,żart.",
})


def history_checks(qualifiers, variant):
    """Tylko wiek formy według zamkniętego rejestru dosłownych etykiet.

    Nie rozbijamy przecinków na sensy i nie stosujemy substring na nowych
    etykietach. Dodatkowe daw./przest. nie znika przez obecność dziś.
    Pozytywna ocena tego warunku nie zatwierdza całej analizy.
    """
    if variant not in {'broad', 'standard'}:
        raise GeneratorError('Nieznany wariant słownika', 2)
    result = []
    for label in sorted(set(qualifiers.split('|'))):
        if label in CURRENT_USAGE_LABELS:
            result.append({'rule_id': 'linguistic-current-usage-non-excluding-v1',
                           'status': 'accept', 'source_label': label,
                           'message': 'Wskazane współczesne użycie nie wyklucza; dodatkowe ograniczenia oceniane osobno.',
                           'evidence': ['config/generator/policy.json', 'docs/generator/etykiety.md']})
        if label in HISTORICAL_LABELS:
            result.append({'rule_id': 'linguistic-historical-form-v1',
                           'status': 'reject' if variant == 'standard' else 'accept',
                           'source_label': label,
                           'message': 'Oznaczenie dawności wyklucza tę analizę ze STANDARD, także przy dziś.'
                                      if variant == 'standard' else 'Sama dawność nie wyklucza z BROAD.',
                           'evidence': ['config/generator/policy.json',
                                        '.maister/tasks/development/2026-10-04-generator-broad-standard/analysis/evidence/mixed-history-decision.md']})
    return result


def disrecommended_checks(qualifiers):
    """Tylko warunek niezalecania, nie ocena całego kwalifikatora/analizy.

    Zamknięta lista dosłownych etykiet z audytu. Przecinka nie traktujemy
    jako separatora sensów; pozostałe składniki etykiety oceniamy osobno.
    Nieznane etykiety nadal wymagają oceny w pełnej polityce.
    """
    return [{'rule_id': 'linguistic-disrecommended-non-excluding-v1',
             'status': 'accept', 'source_label': label,
             'message': 'Samo niezalecanie nie wyklucza w BROAD ani STANDARD; pozostałe warunki oceniane osobno.',
             'evidence': ['config/generator/policy.json',
                          '.maister/tasks/development/2026-10-04-generator-broad-standard/analysis/evidence/disrecommended-decision.md']}
            for label in sorted(set(qualifiers.split('|')) & DISRECOMMENDED_LABELS)]


def spelling_checks(original):
    """Ocena źródłowego zapisu, zanim powstanie małoliterowy klucz."""
    uppercase = any(character.isupper() for character in unicodedata.normalize('NFC', original))
    return [{'rule_id': 'game-required-uppercase-v1',
             'status': 'reject' if uppercase else 'accept',
             'message': 'Źródłowy zapis wymaga wielkich liter.' if uppercase else
                        'Źródłowy zapis nie zawiera wielkich liter; pozostałe reguły oceniane osobno.',
             'evidence': ['docs/generator/ortografia.md']}]


def assess_profile(original):
    nfc = unicodedata.normalize('NFC', original)
    key = unicodedata.normalize('NFC', nfc.lower())
    invalid = sorted(set(key) - set(ALPHABET))
    checks = [
        {'rule_id': 'profile-pl-alphabet-v1', 'status': 'reject' if invalid else 'accept',
         'message': 'Znaki poza alfabetem płytek.' if invalid else 'Alfabet płytek zgodny.',
         'evidence': ['config/generator/profile.json']},
        {'rule_id': 'profile-pl-length-v1', 'status': 'accept' if 2 <= len(key) <= 15 else 'reject',
         'message': 'Wymagana długość 2–15 znaków po NFC/lower.',
         'evidence': ['config/generator/profile.json']},
    ]
    return {'status': 'reject' if any(c['status'] == 'reject' for c in checks) else 'accept',
            'version': 'pl-v1', 'original': original, 'nfc': nfc, 'game_key': key,
            'length': len(key), 'invalid_characters': invalid, 'checks': checks}
