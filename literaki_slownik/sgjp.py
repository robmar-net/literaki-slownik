"""Odczyt eksportu z zachowaniem pięciu surowych pól."""
import gzip
from itertools import product
from math import prod
from .inputs import GeneratorError


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
        with gzip.open(path, 'rt', encoding='utf-8', errors='strict', newline='') as stream:
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
