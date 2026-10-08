"""Odczyt eksportu z zachowaniem pięciu surowych pól."""
import gzip
from itertools import product
from math import prod
from .inputs import GeneratorError

WINIEN_ERRATA_FORMS = {'gotów':'gotoweśmy', 'kontent:V':'kontenteśmy',
                      'niekontent:V':'niekontenteśmy', 'nierad:V':'nieradeśmy',
                      'powinien':'powinnyśmy', 'rad:V':'radeśmy', 'winien':'winnyśmy'}


def tag_errata(source_sha256, lemma_id, original, raw_tag):
    """Jawna adnotacja siedmiu sprawdzonych rekordów; nie modyfikuje importu."""
    if (source_sha256 != '3b2ee079143bc95186370fd528735779c4ba62f4ce14e30cf6622ceb566e9810'
            or WINIEN_ERRATA_FORMS.get(lemma_id) != original
            or raw_tag != 'winien:pl:m2.m3.f.n:sec:imperf'):
        return []
    corrected = 'winien:pl:m2.m3.f.n:pri:imperf'
    return [{'rule_id':'sgjp-20260823-winien-person-erratum-v1',
             'raw_tag':raw_tag, 'corrected_tag':corrected,
             'corrected_expanded_tags':list(expand_tag(corrected)),
             'effect_on_word_strings':'none',
             'message':'Sprawdzona forma pierwszej osoby mnogiej; surowy tag źródłowy zachowany.',
             'evidence':['docs/generator/konstrukcje.md',
                         'https://sgjp.pl/static/pdf/Podstawy_teoretyczne_SGJP.pdf']}]


def tag_size(tag):
    parts = [part.split('.') for part in tag.split(':')]
    if any(not item for part in parts for item in part) or prod(map(len, parts)) > 1024:
        raise GeneratorError('Nieprawidłowy lub zbyt szeroki tag SGJP', 4)
    return prod(map(len, parts))


def expand_tag(tag):
    tag_size(tag)
    for alternative in product(*(part.split('.') for part in tag.split(':'))):
        yield ':'.join(alternative)


def rows(path):
    number = 0
    try:
        opener = gzip.open if str(path).endswith('.gz') else open
        with opener(path, 'rt', encoding='utf-8', errors='strict', newline='') as stream:
            for line in stream:
                if line.rstrip('\r\n') == '#</COPYRIGHT>':
                    break
            else:
                raise GeneratorError('Brak końca nagłówka SGJP', 4, str(path))
            for number, line in enumerate(stream, 1):
                fields = line.rstrip('\r\n').split('\t')
                if len(fields) != 5 or not all(fields[:3]):
                    raise GeneratorError('SGJP wymaga pięciu pól i niepustej formy/lematu/tagu', 4, str(path), number)
                tag_size(fields[2])
                yield number, fields
    except GeneratorError:
        raise
    except (OSError, EOFError, UnicodeError) as error:
        raise GeneratorError(f'Błąd odczytu SGJP: {error}', 4, str(path), number) from error
