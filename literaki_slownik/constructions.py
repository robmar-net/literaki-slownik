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
