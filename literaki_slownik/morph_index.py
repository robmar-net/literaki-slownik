"""Indeks morfologii SGJP dla form BROAD (#1862), format v1.

Forma → lista reguł; reguła = (obetnij `cut` bajtów UTF-8 formy, dopisz końcówkę lematu,
tag, kwalifikatory). Układ sekcji jak w próbie #1857 (`index-spike`). Różnice:
- lista reguł zachowuje kolejność wierszy eksportu dla formy (bez sortowania, bez powtórzeń);
- numery list: od najczęstszej, remis rozstrzyga pierwsze wystąpienie w eksporcie;
- `cut` liczony do granicy znaku, więc każda końcówka jest poprawnym UTF-8.
Wynik jest deterministyczny: te same wejścia dają identyczny plik.
"""
import gzip
import hashlib
import os
import re
import struct
from pathlib import Path
from .inputs import GeneratorError
from .run import code_identity
from .sgjp import rows

MAGIC = b'LLMI'
VERSION = 1
BLOCK = 32
HEX64 = re.compile(r'[0-9a-f]{64}')


def uvarint(value):
    out = bytearray()
    while value >= 0x80:
        out.append(value & 0x7F | 0x80)
        value >>= 7
    out.append(value)
    return bytes(out)


def _strtab(items):
    offsets, data = [], bytearray()
    for item in items:
        offsets.append(len(data))
        data += item
    offsets.append(len(data))
    return struct.pack(f'<I{len(offsets)}I', len(items), *offsets) + bytes(data)


def _intern(table, index, value):
    found = index.get(value)
    if found is None:
        found = index[value] = len(table)
        table.append(value)
    return found


def _rule_parts(form, lemma):
    """(cut w bajtach UTF-8, końcówka lematu w bajtach) przy wspólnym prefiksie znaków."""
    p = 0
    while p < len(form) and p < len(lemma) and form[p] == lemma[p]:
        p += 1
    cut = len(form[p:].encode('utf-8'))
    if cut > 255:
        raise GeneratorError(f'Za długa reszta formy: {form}', 4)
    return cut, lemma[p:].encode('utf-8')


def _builder():
    identity = code_identity()
    commit = (identity['git_commit'] or 'unknown')[:7]
    return f"literaki-slownik {commit}{'-dirty' if identity['git_dirty'] is not False else ''}"


def build(broad_path, sgjp_path, lexicon_id, dawg_sha256, builder=None):
    """Zwraca (bajty indeksu, statystyki). Nic nie zapisuje."""
    if not HEX64.fullmatch(dawg_sha256 or ''):
        raise GeneratorError('--broad-dawg-sha256 musi mieć 64 małe znaki hex', 2)
    if not lexicon_id or lexicon_id != lexicon_id.strip():
        raise GeneratorError('--broad-lexicon-id nie może być pusty', 2)
    try:
        raw_broad = gzip.decompress(Path(broad_path).read_bytes())
        sgjp_sha256 = hashlib.sha256(Path(sgjp_path).read_bytes()).hexdigest()
        broad = set(raw_broad.decode('utf-8').split('\n')) - {''}
    except (OSError, EOFError, gzip.BadGzipFile, UnicodeError) as error:
        raise GeneratorError(f'Błąd odczytu wejścia: {error}', 4) from error
    header = [lexicon_id, dawg_sha256, hashlib.sha256(raw_broad).hexdigest(),
              Path(sgjp_path).name, sgjp_sha256, builder or _builder()]

    ends, end_ix, tags, tag_ix, rules, rule_ix = [], {}, [], {}, [], {}
    quals, qual_ix = [b''], {b'': 0}
    per_form = {}  # kolejność kluczy = pierwsze wystąpienie formy w eksporcie
    kept = 0
    for _, (form, lemma, tag, _name, qualifiers) in rows(sgjp_path):
        if form not in broad:
            continue
        kept += 1
        cut, end = _rule_parts(form, lemma)
        rule = (cut, _intern(ends, end_ix, end), _intern(tags, tag_ix, tag.encode('utf-8')),
                _intern(quals, qual_ix, qualifiers.encode('utf-8')))
        rule_id = _intern(rules, rule_ix, rule)
        per_form.setdefault(form, {})[rule_id] = None  # dict: bez powtórzeń, kolejność eksportu
    if len(tags) > 0xFFFF or len(quals) > 0xFFFF:
        raise GeneratorError('Za dużo tagów lub kwalifikatorów dla u16', 4)

    lists, list_ix, form_list = [], {}, {}
    for form, ruleset in per_form.items():
        form_list[form] = _intern(lists, list_ix, tuple(ruleset))
    freq = [0] * len(lists)
    for list_id in form_list.values():
        freq[list_id] += 1
    order = sorted(range(len(lists)), key=lambda i: (-freq[i], i))
    remap = {old: new for new, old in enumerate(order)}

    list_offsets, list_data = [], bytearray()
    for old in order:
        list_offsets.append(len(list_data))
        list_data += uvarint(len(lists[old]))
        for rule_id in lists[old]:
            list_data += uvarint(rule_id)
    rule_bytes = b''.join(struct.pack('<BIHH', *rule) for rule in rules)

    forms = sorted((form.encode('utf-8'), remap[list_id]) for form, list_id in form_list.items())
    block_offsets, block_data, previous = [], bytearray(), b''
    for i, (form, list_id) in enumerate(forms):
        if i % BLOCK == 0:
            block_offsets.append(len(block_data))
            block_data += uvarint(len(form)) + form
        else:
            p = 0
            while p < len(form) and p < len(previous) and form[p] == previous[p]:
                p += 1
            block_data += uvarint(p) + uvarint(len(form) - p) + form[p:]
        block_data += uvarint(list_id)
        previous = form

    sections = [
        _strtab(ends), _strtab(tags), _strtab(quals), rule_bytes,
        struct.pack(f'<I{len(order)}I', len(order), *list_offsets) + bytes(list_data),
        struct.pack(f'<II{len(block_offsets)}I', len(forms), len(block_offsets), *block_offsets) + bytes(block_data),
    ]
    out = bytearray(MAGIC + struct.pack('<I', VERSION))
    for field in header:
        encoded = field.encode('utf-8')
        out += uvarint(len(encoded)) + encoded
    out += struct.pack('<6I', *map(len, sections))
    for section in sections:
        out += section
    blob = bytes(out)
    stats = {'broad_forms': len(broad), 'sgjp_rows_kept': kept, 'forms_with_analysis': len(forms),
             'rules': len(rules), 'rule_lists': len(lists), 'lemma_endings': len(ends),
             'tags': len(tags), 'qualifier_sets': len(quals),
             'section_bytes': dict(zip(('endings', 'tags', 'qualifiers', 'rules', 'lists', 'forms'),
                                       map(len, sections))),
             'header': dict(zip(('broadLexiconId', 'broadDawgSha256', 'broadListSha256', 'sgjpExport',
                                 'sgjpSha256', 'builder'), header))}
    return blob, stats


def write_index(broad_path, sgjp_path, lexicon_id, dawg_sha256, out_path):
    """Buduje i zapisuje indeks; odmawia nadpisania istniejącego pliku."""
    out_path = Path(out_path)
    if out_path.exists():
        raise GeneratorError('Plik wyjściowy już istnieje; wybierz nową ścieżkę', 4, str(out_path))
    blob, stats = build(broad_path, sgjp_path, lexicon_id, dawg_sha256)
    partial = out_path.with_name(out_path.name + '.part')
    partial.write_bytes(blob)
    os.replace(partial, out_path)
    stats.update(out=str(out_path), bytes=len(blob),
                 gzip_bytes=len(gzip.compress(blob, compresslevel=9, mtime=0)),
                 sha256=hashlib.sha256(blob).hexdigest())
    return stats
