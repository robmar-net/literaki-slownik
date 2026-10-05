"""Potwierdzone warunki i profil; pełna polityka językowa nadal nieukończona."""
import unicodedata
from .inputs import GeneratorError

ALPHABET = 'aąbcćdeęfghijklłmnńoóprsśtuwyzźż'
VERSION = 'diagnostic-approved-conditions-v9'
FIRST_RELEASE_CONTRACTIONS = frozenset('bezeń dlań doń nadeń nań odeń oń podeń poń przedeń przezeń spodeń spozań sprzedeń weń zań zeń znadeń'.split())
DEFERRED_CONTRACTIONS = frozenset('kołoń pozań zzań ponadeń popodeń poprzezeń sponadeń spopodeń'.split())


def release_scope_checks(candidate=None):
    """Zakres wydania dotyczy śladu konstrukcji; nie błędności ani całego napisu."""
    status, message = 'accept', 'Analiza nie jest wyłączona przez ograniczenie zakresu kontrakcji; inne warunki osobno.'
    if candidate is not None and candidate['rule_id']=='preposition-n-source-v1':
        original = candidate['original']
        if original in DEFERRED_CONTRACTIONS:
            status, message = 'reject', 'Kandydat poza zakresem pierwszego wydania; zachowany diagnostycznie, bez uznania formy za błędną.'
        elif original not in FIRST_RELEASE_CONTRACTIONS:
            status, message = 'unresolved', 'Nieznany zakres kontrakcji: wymagana ocena, bez automatycznego wyłączenia.'
    return [{'rule_id':'first-release-contraction-scope-v1', 'status':status,
             'message':message, 'evidence':['config/generator/constructions.json',
             '.maister/tasks/development/2026-10-04-generator-broad-standard/analysis/evidence/remaining-contractions-scope-decision.md']}]


# Dosłowne leksemy potwierdzone pełnym odczytem SGJP i poradą UŁ/RJP2026.
ORTHOGRAPHY_2026_CONJUNCTIONS = frozenset({'jeśliby','jeżeliby'})


def orthography_checks(source, variant):
    """Ocena konkretnej źródłowej analizy; nie ogólna reguła końcowych liter."""
    if variant not in {'broad','standard'}:
        raise GeneratorError('Wariant musi być broad lub standard', 2)
    lemma = source['lemma_id']
    if (lemma not in ORTHOGRAPHY_2026_CONJUNCTIONS or source['raw_tag'] != 'comp'
            or source['original'] != lemma):
        return []
    return [{'rule_id':'orthography-2026-conjunction-by-v1',
             'status':'reject' if variant == 'standard' else 'accept',
             'source_lemma_id':lemma, 'norm_effective_from':'2026-01-01',
             'message':'Norma 2026 wymaga pisowni rozdzielnej; ta analiza odpada ze STANDARD.'
                       if variant == 'standard' else
                       'Udokumentowany dawny zapis nie wyklucza sam w BROAD; reguły gry i inne warunki osobno.',
             'evidence':['config/generator/orthography.json',
                         '.maister/tasks/development/2026-10-04-generator-broad-standard/analysis/evidence/orthography-2026-decision.md',
                         'https://www.poradnia-jezykowa.uni.lodz.pl/szczegoly/pisownia-spojnikow-jesli-jezeli-z-czastka-by']}]


CONTEXT_REQUIREMENTS = {
    'daw.,z_D.': 'adjective_genitive',
    'daw._dziś_gwar.,z_D.': 'adjective_genitive',
    'fraz.': 'phraseological_usage',
    'fraz.,rzad.': 'phraseological_usage',
    'gwar.,z_D.': 'adjective_genitive',
    'książk.,z_D.': 'adjective_genitive',
    'po_liczebniku': 'after_numeral',
    'pot.,po_liczebniku': 'after_numeral',
    'pot.,z_D.': 'adjective_genitive',
    'przest.,z_D.': 'adjective_genitive',
    'z_D.': 'adjective_genitive',
}


def context_checks(qualifiers):
    """Zachowaj wymaganie użycia; samo w sobie nie odrzuca poprawnej formy."""
    descriptions = {
        'adjective_genitive': 'Określenie przymiotnikowe w dopełniaczu.',
        'phraseological_usage': 'Użycie frazeologiczne.',
        'after_numeral': 'Użycie po liczebniku.',
    }
    return [{'rule_id': 'linguistic-context-non-excluding-v1',
             'status': 'accept', 'source_label': label,
             'required_context': CONTEXT_REQUIREMENTS[label],
             'message': descriptions[CONTEXT_REQUIREMENTS[label]] +
                        ' Samo wymaganie kontekstu nie wyklucza; inne ograniczenia oceniane osobno.',
             'evidence': ['config/generator/policy.json',
                          '.maister/tasks/development/2026-10-04-generator-broad-standard/analysis/evidence/context-restrictions-decision.md']}
            for label in sorted(set(qualifiers.split('|')) & CONTEXT_REQUIREMENTS.keys())]


def approved_qualifier_checks(qualifiers, variant):
    """Zatwierdzone warunki kwalifikatorów; inne warstwy nadal osobno."""
    return (history_checks(qualifiers, variant) + disrecommended_checks(qualifiers)
            + usage_checks(qualifiers) + incorrect_checks(qualifiers)
            + descriptive_checks(qualifiers) + context_checks(qualifiers))


DESCRIPTIVE_LABELS = frozenset({
    'anat.',
    'anat.,muz.,techn.',
    'anat.,techn.',
    'anat.,zool.',
    'antr.',
    'archeol.',
    'archit.',
    'archit.,bud.',
    'archit.,hist.',
    'archit.,rel.',
    'archit.,techn.',
    'bank.',
    'bibl.',
    'biochem.',
    'biochem.,farm.',
    'biol.',
    'biol.,chem.',
    'biol.,fiz.,miner.,techn.',
    'biol.,kulin.',
    'biol.,med.',
    'biol.,zool.',
    'bot.',
    'bot.,chem.',
    'bot.,geol.',
    'bot.,hist.',
    'bot.,kulin.',
    'bot.,med.',
    'bot.,miner.',
    'bot.,ogr.',
    'bot.,włók.',
    'bot.,zool.',
    'bud.',
    'bud.,hist.',
    'bud.,techn.',
    'char.',
    'char.,anat.',
    'char.,archit.',
    'char.,biol.',
    'char.,bot.',
    'char.,bot.,kulin.',
    'char.,bud.',
    'char.,chor.',
    'char.,hist.',
    'char.,kulin.',
    'char.,lit.',
    'char.,meteor.',
    'char.,mit.',
    'char.,mors.,żegl.',
    'char.,muz.',
    'char.,muz.,teatr.',
    'char.,praw.',
    'char.,techn.',
    'char.,zool.',
    'char.,łow.',
    'char.,żegl.',
    'chem.',
    'chem.,farm.',
    'chem.,fiz.',
    'chem.,fiz.,muz.',
    'chem.,ogr.',
    'chem.,wojsk.',
    'chor.',
    'chor.,lit.',
    'chor.,muz.',
    'druk.',
    'druk.,hist.',
    'edyt.',
    'ekon.',
    'ekon.,praw.',
    'elektr.',
    'elektr.,komp.',
    'erud.',
    'etnolog.',
    'euf.',
    'euf.,rzad.',
    'farm.',
    'film.',
    'filoz.',
    'filoz.,rel.',
    'fiz.',
    'fiz.,mat.',
    'fiz.,techn.',
    'form.',
    'genet.',
    'geogr.',
    'geogr.,geol.',
    'geol.',
    'geol.,komp.',
    'geol.,med.',
    'gwar.,archit.',
    'gwar.,char.',
    'gwar.,hom.',
    'gwar.,pot.,żart.',
    'gwar.,rzad.,archit.',
    'gwar.,rzad.,hom.',
    'gwar.,łow.',
    'gwar.,środ.',
    'górn.',
    'górn.,rzem.',
    'górn.,techn.',
    'handl.',
    'hip.',
    'hist.',
    'hist.,lit.',
    'hist.,mit.',
    'hist.,monet.',
    'hist.,mors.',
    'hist.,poligr.',
    'hist.,polit.',
    'hist.,roln.',
    'hist.,sport.',
    'hist.,techn.',
    'hist.,wojsk.',
    'hom.',
    'hom.,anat.',
    'hom.,archit.',
    'hom.,biol.',
    'hom.,bot.',
    'hom.,bot.,kulin.',
    'hom.,bud.',
    'hom.,chem.',
    'hom.,chem.,fiz.',
    'hom.,chor.',
    'hom.,edyt.',
    'hom.,ekon.',
    'hom.,fiz.',
    'hom.,geol.',
    'hom.,hist.',
    'hom.,hydrol.',
    'hom.,jęz.',
    'hom.,komp.',
    'hom.,kulin.',
    'hom.,lit.',
    'hom.,mat.',
    'hom.,med.',
    'hom.,meteor.',
    'hom.,mit.',
    'hom.,mors.',
    'hom.,mors.,żegl.',
    'hom.,mot.',
    'hom.,muz.',
    'hom.,muz.,teatr.',
    'hom.,paleont.',
    'hom.,praw.',
    'hom.,psych.',
    'hom.,rel.',
    'hom.,sport.',
    'hom.,techn.',
    'hom.,term.',
    'hom.,wojsk.',
    'hom.,zool.',
    'hom.,łow.',
    'hom.,żegl.',
    'hydrol.',
    'indyw.',
    'indyw.,char.',
    'indyw.,hom.',
    'indyw.,rzad.',
    'indyw.,rzad.,hom.',
    'indyw.,żart.',
    'iron.',
    'iron.,char.',
    'iron.,książk.',
    'iron.,pogard.',
    'iron.,pot.',
    'iron.,pot.,żart.',
    'iron.,rzad.',
    'iron.,rzad.,hom.',
    'iron.,żart.',
    'iron.,żart.,hom.',
    'jęz.',
    'jęz.,komp.',
    'jęz.,lit.',
    'jęz.,mat.',
    'karc.',
    'komp.',
    'komp.,lit.',
    'komp.,mat.,techn.',
    'komp.,muz.',
    'komp.,psych.',
    'książk.',
    'książk.,hom.',
    'książk.,poet.',
    'książk.,pogard.',
    'książk.,rzad.',
    'książk.,żart.',
    'książk.,żart.,hom.',
    'kulin.',
    'kulin.,mikol.',
    'kulin.,sport.',
    'kulin.,zool.',
    'lekcew.',
    'lekcew.,pot.',
    'lekcew.,pot.,rzad.',
    'lekcew.,wulg.',
    'leśn.',
    'leśn.,ogr.',
    'lit.',
    'lit.,muz.',
    'lotn.',
    'mat.',
    'mat.,muz.',
    'med.',
    'med.,praw.',
    'med.,psych.',
    'med.,wet.',
    'med.,zool.',
    'meteor.',
    'mikol.',
    'mikol.,zool.',
    'miner.',
    'mit.',
    'monet.',
    'mors.',
    'mors.,wojsk.',
    'mors.,żegl.',
    'mot.',
    'muz.',
    'muz.,teatr.',
    'muz.,techn.',
    'num.',
    'ogr.',
    'paleont.',
    'plast.',
    'poet.',
    'poet.,rzad.',
    'pogard.',
    'pogard.,pot.',
    'pogard.,pot.,char.',
    'pogard.,pot.,hom.',
    'pogard.,pot.,rzad.',
    'pogard.,rzad.',
    'pogard.,wulg.',
    'pogard.,żart.',
    'poligr.',
    'polit.',
    'pot.,anat.',
    'pot.,bot.',
    'pot.,bot.,geol.',
    'pot.,bot.,kulin.',
    'pot.,char.',
    'pot.,hist.',
    'pot.,hom.',
    'pot.,karc.',
    'pot.,komp.',
    'pot.,kulin.',
    'pot.,monet.',
    'pot.,mors.',
    'pot.,mors.,wojsk.',
    'pot.,muz.',
    'pot.,num.',
    'pot.,rub.',
    'pot.,rzad.,karc.',
    'pot.,sport.',
    'pot.,szkol.',
    'pot.,wojsk.',
    'pot.,zool.',
    'pot.,środ.',
    'pot.,środ.,char.',
    'pot.,środ.,hom.',
    'pot.,żart.',
    'pot.,żart.,char.',
    'pot.,żart.,hom.',
    'pot.,żegl.',
    'praw.',
    'przen.',
    'przen.,hom.',
    'przen.,rzad.,wulg.',
    'psych.',
    'pszcz.',
    'reg.,bud.',
    'reg.,char.',
    'reg.,hist.',
    'reg.,hom.',
    'reg.,kulin.',
    'reg.,rzad.,zool.',
    'reg.,zool.',
    'reg.,łow.',
    'rel.',
    'roln.',
    'roln.,techn.',
    'rub.',
    'rub.,rzad.',
    'rub.,żart.',
    'ryb.',
    'ryb.,techn.',
    'rzad.,anat.',
    'rzad.,biol.',
    'rzad.,bot.',
    'rzad.,char.',
    'rzad.,chem.',
    'rzad.,elektr.',
    'rzad.,etnolog.',
    'rzad.,geogr.',
    'rzad.,hist.',
    'rzad.,hom.',
    'rzad.,hom.,term.',
    'rzad.,kulin.',
    'rzad.,kulin.,sport.',
    'rzad.,lit.',
    'rzad.,lotn.',
    'rzad.,mat.',
    'rzad.,med.',
    'rzad.,med.,wet.',
    'rzad.,meteor.',
    'rzad.,mikol.',
    'rzad.,muz.',
    'rzad.,num.',
    'rzad.,ogr.',
    'rzad.,rel.',
    'rzad.,roln.',
    'rzad.,ryb.,techn.',
    'rzad.,rzem.',
    'rzad.,sport.',
    'rzad.,szt.,włók.',
    'rzad.,techn.',
    'rzad.,term.',
    'rzad.,wojsk.',
    'rzad.,zool.',
    'rzad.,łow.',
    'rzad.,łow.,zool.',
    'rzad.,łow.,zootechn.',
    'rzad.,środ.',
    'rzad.,środ.,łow.',
    'rzad.,żart.',
    'rzad.,żegl.',
    'rzem.',
    'sport.',
    'sport.,zool.',
    'sport.,żegl.',
    'szach.',
    'szkol.',
    'szt.',
    'teatr.',
    'techn.',
    'term.',
    'wet.',
    'wet.,zool.',
    'wojsk.',
    'wulg.,char.',
    'wulg.,hom.',
    'włók.',
    'włók.,zool.',
    'zool.',
    'zootechn.',
    'łow.',
    'łow.,zool.',
    'łow.,zootechn.',
    'łow.,żegl.',
    'środ.',
    'środ.,char.',
    'środ.,hom.',
    'środ.,sport.',
    'środ.,łow.',
    'żart.',
    'żart.,hom.',
    'żegl.',
})


def descriptive_checks(qualifiers):
    """Sama dziedzina, styl lub oznaczenie wariantu nie wyklucza.

    Zamknięta mapa całych etykiet. Nie przenosi efektu na nieznaną
    mieszaną etykietę i nie zastępuje oceny składni lub całej analizy.
    """
    return [{'rule_id': 'linguistic-descriptive-non-excluding-v1',
             'status': 'accept', 'source_label': label,
             'message': 'Sama dziedzina, stylistyka lub opis wariantu formy nie wyklucza; pozostałe warunki oceniane osobno.',
             'evidence': ['config/generator/policy.json', 'docs/generator/etykiety.md',
                          'https://sgjp.pl/oznaczenia/', 'https://sgjp.pl/instrukcja/']}
            for label in sorted(set(qualifiers.split('|')) & DESCRIPTIVE_LABELS)]


INCORRECT_LABELS = frozenset({
    'daw.,niepopr.',
    'indyw.,niepopr.',
    'książk.,niepopr.',
    'książk.,niepopr.,pogard.',
    'niepopr.',
    'niepopr.,astron.',
    'niepopr.,biol.',
    'niepopr.,biol.,zool.',
    'niepopr.,filoz.',
    'niepopr.,fiz.',
    'niepopr.,genet.',
    'niepopr.,jęz.',
    'niepopr.,jęz.,lit.',
    'niepopr.,lit.',
    'niepopr.,med.',
    'niepopr.,muz.',
    'niepopr.,polit.',
    'niepopr.,pot.',
    'niepopr.,pot.,żart.',
    'niepopr.,przest.',
    'niepopr.,rel.',
    'niepopr.,rzad.',
    'niepopr.,rzad.,arch.,char.',
    'niepopr.,rzad.,hom.',
    'niepopr.,sport.',
    'niepopr.,szt.',
    'niepopr.,wulg.',
})


def incorrect_checks(qualifiers):
    """Jawna niepoprawność konkretnej analizy, bez usunięcia wpisu/homonimów."""
    return [{'rule_id': 'linguistic-incorrect-form-v1',
             'status': 'reject', 'source_label': label,
             'message': 'SGJP oznacza tę interpretację jako niepoprawną; odrzucenie w BROAD i STANDARD.',
             'evidence': ['config/generator/policy.json',
                          '.maister/tasks/development/2026-10-04-generator-broad-standard/analysis/evidence/incorrect-forms-decision.md']}
            for label in sorted(set(qualifiers.split('|')) & INCORRECT_LABELS)]


USAGE_LABELS = frozenset({
    'gwar.', 'gwar.,pot.', 'gwar.,rzad.', 'pot.', 'pot.,reg.',
    'pot.,reg.,rzad.', 'pot.,rzad.', 'pot.,rzad.,wulg.', 'pot.,wulg.',
    'reg.', 'reg.,rzad.', 'reg.,wulg.', 'rzad.', 'rzad.,wulg.', 'wulg.',
})


def usage_checks(qualifiers):
    """Zatwierdzony niewykluczający zakres użycia, bez pełnego werdyktu.

    Zamknięte dosłowne etykiety; nie rozbijamy przecinków w runtime.
    Mieszanki z ograniczeniami spoza tej mapy wymagają osobnej oceny.
    """
    return [{'rule_id': 'linguistic-informal-rare-non-excluding-v1',
             'status': 'accept', 'source_label': label,
             'message': 'Sama potoczność, wulgarność, regionalność, gwarowość lub rzadkość nie wyklucza; inne warunki oceniane osobno.',
             'evidence': ['docs/literaki-niezalezne-slowniki-prompt-v3.md',
                          'config/generator/policy.json', 'https://sgjp.pl/oznaczenia/']}
            for label in sorted(set(qualifiers.split('|')) & USAGE_LABELS)]

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


def construction_orthography_checks(candidate, variant):
    if candidate is None or candidate['rule_id']!='mobile-host-by-sequence-v1':
        return []
    if variant not in {'broad','standard'}:
        raise GeneratorError('Wariant musi być broad lub standard',2)
    return [{'rule_id':'orthography-2026-host-by-sequence-v1',
             'status':'reject' if variant=='standard' else 'accept',
             'norm_effective_from':'2026-01-01',
             'message':'Ta konstrukcja wymaga rozdzielnej pisowni by według normy2026; odrębne źródłowe wyrazy oceniane osobno.'
                       if variant=='standard' else 'Udokumentowana źródłowa konstrukcja historyczna; sama pisownia nie wyklucza w BROAD. Inne warunki osobno.',
             'evidence':['config/generator/orthography.json',
              'https://rjp.pan.pl/app/uploads/2025/11/2-zalacznik-do-komunikatu-11-25-wersja-jednolita.pdf'] }]
