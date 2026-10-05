"""Potwierdzone konstrukcje źródłowe; kandydat nie jest dopuszczeniem do gry."""
import unicodedata

from .inputs import GeneratorError
from .sgjp import expand_tag

VOWELS = frozenset('aąeęioóuy')
IMPT_PARTICLE_RULE = 'impt-single-particle-v1'
SOURCE_FIELDS = ('source_id', 'first_source_row', 'original', 'lemma_id', 'raw_tag', 'names', 'qualifiers')
BY_AGLT_ENDINGS = {('sg', 'pri'): 'm', ('sg', 'sec'): 'ś', ('pl', 'pri'): 'śmy', ('pl', 'sec'): 'ście'}


def _validate_source(source):
    if (not isinstance(source, dict) or any(field not in source for field in SOURCE_FIELDS)
            or any(not isinstance(source[field], str) for field in SOURCE_FIELDS if field != 'first_source_row')
            or any(not source[field] for field in ('source_id', 'original', 'lemma_id', 'raw_tag'))
            or type(source['first_source_row']) is not int or source['first_source_row'] < 1):
        raise GeneratorError('Konstrukcja wymaga pełnej interpretacji źródłowej', 4)


def impt_particle_candidates(source):
    """Dodaj jedną partykułę do udokumentowanego rozkaźnika.

    Każdy wynik zachowuje konkretną źródłową analizę i odziedziczone etykiety.
    Kwalifikacja całej analizy i profilu następuje w osobnym etapie.
    Niezgodność klasy lub zakończenia jest luką pokrycia, nie cichym pominięciem.
    """
    _validate_source(source)
    if source['raw_tag'].split(':', 1)[0] != 'impt':
        return []
    original = source['original']
    ending = unicodedata.normalize('NFC', original)[-1].lower()
    results = []
    for tag in expand_tag(source['raw_tag']):
        fields = tag.split(':')
        if (len(fields) != 4 or fields[3] not in {'perf', 'imperf'}
                or (fields[1], fields[2]) not in {('sg', 'sec'), ('pl', 'pri'), ('pl', 'sec')}):
            raise GeneratorError('Niepokryta klasa rozkaźnika', 4, source['source_id'], source['first_source_row'])
        singular = fields[1] == 'sg'
        if singular == (ending in VOWELS) or not ending.isalpha():
            raise GeneratorError('Zakończenie rozkaźnika niezgodne z potwierdzoną macierzą', 4,
                                 source['source_id'], source['first_source_row'])
        particle = 'że' if singular else 'ż'
        results.append({
            'rule_id': IMPT_PARTICLE_RULE, 'status': 'candidate_not_qualified',
            'original': original + particle, 'lemma_id': source['lemma_id'], 'expanded_tag': tag,
            'names': source['names'], 'qualifiers': source['qualifiers'],
            'components': [
                {'kind': 'source_interpretation', 'interpretation': dict(source)},
                {'kind': 'grammatical_particle', 'original': particle, 'rule_id': IMPT_PARTICLE_RULE},
            ],
            'evidence': ['docs/generator/konstrukcje.md', 'config/generator/constructions.json'],
        })
    return results


def by_aglt_candidates(operator, aglt):
    """Wyłącznie źródłowe by + cztery niewokaliczne aglutynanty."""
    _validate_source(operator)
    _validate_source(aglt)
    if operator['original'] != 'by' or operator['raw_tag'] not in {'comp', 'part'}:
        return []
    if aglt['raw_tag'].split(':', 1)[0] != 'aglt':
        return []
    results = []
    for tag in expand_tag(aglt['raw_tag']):
        fields = tag.split(':')
        if (len(fields) != 5 or fields[3:] != ['imperf', 'nwok']
                or BY_AGLT_ENDINGS.get((fields[1], fields[2])) != aglt['original']):
            raise GeneratorError('Niepokryta forma by + aglt; wymagany wariant nwok', 4,
                                 aglt['source_id'], aglt['first_source_row'])
        inherited = {field: '|'.join(sorted({label for item in (operator, aglt)
                                            for label in item[field].split('|') if label}))
                     for field in ('names', 'qualifiers')}
        results.append({
            'rule_id': 'by-aglt-nwok-v1', 'status': 'candidate_not_qualified',
            'original': operator['original'] + aglt['original'], 'lemma_id': operator['lemma_id'],
            'expanded_tag': tag, **inherited,
            'components': [{'kind': 'source_interpretation', 'interpretation': dict(item)}
                           for item in (operator, aglt)],
            'evidence': ['docs/generator/konstrukcje.md', 'config/generator/constructions.json'],
        })
    return results


def materialize_confirmed_candidates(db, batch_size=10000):
    """Zapisz potwierdzony podzbiór bez dopuszczenia lub pełnego statusu etapu.

    Kandydat i jego składniki zapisują się razem; porcje mogą pozostać po awarii.
    Klucz treści zachowuje alternatywne ślady, także dla istniejącego napisu.
    """
    import hashlib
    from .canonical import dumps

    if type(batch_size) is not int or not 1 <= batch_size <= 10000:
        raise GeneratorError('Porcja konstrukcji musi mieć od 1 do 10 000 kandydatów', 2)
    select = '''select i.source_id,i.first_row,f.original,l.lemma_id,i.tag,i.names,i.qualifiers
        from interpretation i join surface_form f on f.id=i.form_id join lexeme l on l.id=i.lexeme_id'''
    new_count, pending, source_count = 0, 0, 0

    def save(candidate):
        nonlocal new_count, pending
        payload = dumps(candidate)
        key = hashlib.sha256(payload.encode('utf-8')).hexdigest()
        nfc = unicodedata.normalize('NFC', candidate['original'])
        game_key = unicodedata.normalize('NFC', nfc.lower())
        inserted = db.execute('''insert or ignore into derivation_candidate
            (candidate_key,rule_id,original,game_key,lemma_id,expanded_tag,names,qualifiers,payload)
            values (?,?,?,?,?,?,?,?,?)''',
            (key, candidate['rule_id'], candidate['original'], game_key, candidate['lemma_id'],
             candidate['expanded_tag'], candidate['names'], candidate['qualifiers'], payload)).rowcount
        new_count += inserted
        for position, component in enumerate(candidate['components']):
            source = component.get('interpretation')
            db.execute('''insert or ignore into derivation_component
                (candidate_key,position,kind,source_id,source_row) values (?,?,?,?,?)''',
                (key, position, component['kind'], source['source_id'] if source else None,
                 source['first_source_row'] if source else None))
        pending += 1
        if pending >= batch_size:
            db.commit()
            pending = 0

    for row in db.execute(select + " where i.tag like 'impt:%' order by i.source_id,i.first_row"):
        source_count += 1
        for candidate in impt_particle_candidates(dict(zip(SOURCE_FIELDS,row))):
            save(candidate)
    operators = [dict(zip(SOURCE_FIELDS,row)) for row in db.execute(
        select + " where f.original='by' and i.tag in ('part','comp') order by i.source_id,i.first_row")]
    endings = [dict(zip(SOURCE_FIELDS,row)) for row in db.execute(
        select + " where i.tag like 'aglt:%:nwok' order by i.source_id,i.first_row")]
    for operator in operators:
        for ending in endings:
            if operator['source_id'] == ending['source_id']:
                for candidate in by_aglt_candidates(operator, ending):
                    save(candidate)
    db.commit()
    by_rule = dict(db.execute('select rule_id,count(*) from derivation_candidate group by rule_id order by rule_id'))
    return {'schema_version': 1, 'scope': 'confirmed_subset_candidates_not_full_constructions',
            'full_constructions_pending': True, 'impt_source_interpretations': source_count,
            'operator_source_interpretations': len(operators), 'aglt_source_interpretations': len(endings),
            'new_candidates': new_count, 'candidates': sum(by_rule.values()), 'by_rule': by_rule,
            'components': db.execute('select count(*) from derivation_component').fetchone()[0],
            'notice': 'Kandydaci zachowują ślady; nie są decyzjami językowymi ani dopuszczeniem do gry. '
                      'Brak pełnej macierzy nadal blokuje ukończenie etapu konstrukcji.'}
