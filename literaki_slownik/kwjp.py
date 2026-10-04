"""Parser list, niezależny od nazwy pliku; liczby bez utraty oryginału."""
import csv
from decimal import Decimal, InvalidOperation
import gzip
from .inputs import GeneratorError

METRICS = ['freq', 'ipm', 'ARF', 'DP', 'DP_norm', '1-DP', 'total_freq']
COLUMNS = {'kwjp_lemma': ['lemma', 'pos'] + METRICS,
           'kwjp_orth': ['form'] + METRICS,
           'kwjp_orth_lc': ['form'] + METRICS,
           'kwjp_bigram': ['unit_1', 'unit_2'] + METRICS[:-1] + ['Dice', 'total_freq']}


def rows(path, kind):
    if kind not in COLUMNS:
        raise GeneratorError('Nieznany typ listy KWJP', 4, str(path))
    columns = COLUMNS[kind]
    metric_names = [c for c in columns if c in METRICS or c == 'Dice']
    unit_count = len(columns) - len(metric_names)
    number = 0
    try:
        with gzip.open(path, 'rt', encoding='utf-8', errors='strict', newline='') as stream:
            reader = csv.reader(stream, strict=True)
            header = next(reader, None)
            if header != [''] * unit_count + metric_names:
                raise GeneratorError('Niezgodny nagłówek listy KWJP', 4, str(path))
            for number, row in enumerate(reader, 1):
                if len(row) != len(columns) or any(not value for value in row):
                    raise GeneratorError('Nieprawidłowa szerokość lub puste pole KWJP', 4, str(path), number)
                raw = dict(zip(columns, row))
                typed = {}
                for name in metric_names:
                    value = Decimal(raw[name])
                    if not value.is_finite() or value < 0:
                        raise GeneratorError('Niefinitywna lub ujemna miara KWJP', 4, str(path), number)
                    if name in {'freq', 'total_freq'}:
                        if value != value.to_integral_value():
                            raise GeneratorError('Częstość KWJP nie jest całkowita', 4, str(path), number)
                        typed[name] = int(value)
                    else:
                        typed[name] = str(value)
                if typed['freq'] > typed['total_freq']:
                    raise GeneratorError('F przekracza total_freq', 4, str(path), number)
                yield number, raw, typed
    except GeneratorError:
        raise
    except (OSError, EOFError, UnicodeError, csv.Error, InvalidOperation) as error:
        raise GeneratorError(f'Błąd odczytu KWJP: {error}', 4, str(path), number) from error
