"""Indeks morfologii SGJP (#1862): format v1 czytany niezależnym czytnikiem z testu."""
import gzip
import hashlib
import json
import struct
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from literaki_slownik.inputs import GeneratorError
from literaki_slownik.morph_index import build

DAWG = 'ab' * 32


def uvarint(data, pos):
    value = shift = 0
    while True:
        byte = data[pos]
        pos += 1
        value |= (byte & 0x7F) << shift
        if byte < 0x80:
            return value, pos
        shift += 7


def strtab(section):
    count, = struct.unpack_from('<I', section)
    offsets = struct.unpack_from(f'<{count + 1}I', section, 4)
    data = section[4 + 4 * (count + 1):]
    return [data[offsets[i]:offsets[i + 1]] for i in range(count)]


def read(blob):
    """Czytnik formatu v1 napisany od zera: nagłówek, sekcje, wszystkie formy."""
    assert blob[:4] == b'LLMI' and struct.unpack_from('<I', blob, 4) == (1,)
    pos, header = 8, []
    for _ in range(6):
        size, pos = uvarint(blob, pos)
        header.append(blob[pos:pos + size].decode('utf-8'))
        pos += size
    sizes = struct.unpack_from('<6I', blob, pos)
    pos += 24
    sections = []
    for size in sizes:
        sections.append(blob[pos:pos + size])
        pos += size
    assert pos == len(blob)
    ends, tags, quals = strtab(sections[0]), strtab(sections[1]), strtab(sections[2])
    assert quals[0] == b''
    rules = [struct.unpack_from('<BIHH', sections[3], i) for i in range(0, len(sections[3]), 9)]
    count, = struct.unpack_from('<I', sections[4])
    offsets = struct.unpack_from(f'<{count}I', sections[4], 4)
    data = sections[4][4 + 4 * count:]
    lists = []
    for offset in offsets:
        size, p = uvarint(data, offset)
        items = []
        for _ in range(size):
            item, p = uvarint(data, p)
            items.append(item)
        lists.append(items)
    forms_sec = sections[5]
    n_forms, n_blocks = struct.unpack_from('<II', forms_sec)
    block_offsets = struct.unpack_from(f'<{n_blocks}I', forms_sec, 8)
    blocks = forms_sec[8 + 4 * n_blocks:]
    forms = {}
    for b, offset in enumerate(block_offsets):
        p, previous = offset, b''
        for i in range(min(32, n_forms - 32 * b)):
            if i == 0:
                size, p = uvarint(blocks, p)
                current = blocks[p:p + size]
                p += size
            else:
                shared, p = uvarint(blocks, p)
                size, p = uvarint(blocks, p)
                current = previous[:shared] + blocks[p:p + size]
                p += size
            list_id, p = uvarint(blocks, p)
            forms[current] = list_id
            previous = current
    assert list(forms) == sorted(forms) and len(forms) == n_forms
    analyses = {}
    for form, list_id in forms.items():
        out = []
        for rule_id in lists[list_id]:
            cut, add, tag, qual = rules[rule_id]
            lemma = form[:len(form) - cut] + ends[add]
            out.append((lemma.decode('utf-8'), tags[tag].decode('utf-8'), quals[qual].decode('utf-8')))
        analyses[form.decode('utf-8')] = out
    return header, analyses, lists, forms, rules


class MorphIndexTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def files(self, words, rows):
        broad, sgjp = self.dir / 'LL-PL-BROAD.txt.gz', self.dir / 'sgjp-test.tab.gz'
        with gzip.open(broad, 'wt', encoding='utf-8') as stream:
            stream.write(''.join(w + '\n' for w in words))
        with gzip.open(sgjp, 'wt', encoding='utf-8') as stream:
            stream.write('# test\n#</COPYRIGHT>\n')
            stream.write(''.join('\t'.join(r) + '\n' for r in rows))
        return broad, sgjp

    def index(self, words, rows, **kw):
        broad, sgjp = self.files(words, rows)
        return build(broad, sgjp, 'pl-test', DAWG, builder='literaki-slownik test', **kw)

    def test_round_trip_keeps_export_order_per_form(self):
        rows = [('mam', 'mieć', 'fin:sg:pri:imperf', '', ''),
                ('kot', 'kot:Sm1', 'subst:sg:nom:m1', '', 'pot.'),
                ('mam', 'mama', 'subst:pl:gen:f', '', ''),
                ('mam', 'mieć', 'fin:sg:pri:imperf', '', ''),
                ('kot', 'kot:Sm2', 'subst:sg:nom.acc:m2', '', '')]
        blob, stats = self.index(['kot', 'mam'], rows)
        _, analyses, *_ = read(blob)
        self.assertEqual(analyses, {
            'kot': [('kot:Sm1', 'subst:sg:nom:m1', 'pot.'), ('kot:Sm2', 'subst:sg:nom.acc:m2', '')],
            'mam': [('mieć', 'fin:sg:pri:imperf', ''), ('mama', 'subst:pl:gen:f', '')]})
        self.assertEqual(stats['forms_with_analysis'], 2)

    def test_header_has_six_fields_in_order(self):
        broad, sgjp = self.files(['kot'], [('kot', 'kot', 'subst:sg:nom:m2', '', '')])
        blob, _ = build(broad, sgjp, 'pl-test', DAWG, builder='literaki-slownik abc1234')
        header, *_ = read(blob)
        self.assertEqual(header, [
            'pl-test', DAWG,
            hashlib.sha256(gzip.decompress(broad.read_bytes())).hexdigest(),
            'sgjp-test.tab.gz', hashlib.sha256(sgjp.read_bytes()).hexdigest(),
            'literaki-slownik abc1234'])

    def test_deterministic_and_frequency_ties_by_first_appearance(self):
        # Lista B (zz) pojawia się przed listą A (aa) w eksporcie; obie mają częstość 1.
        # Lista C (dwie formy) jest najczęstsza i dostaje 0.
        rows = [('zz', 'zz', 'adv', '', ''),
                ('aa', 'aa', 'subst:sg:nom:f', '', ''),
                ('ab', 'ab', 'interj', '', ''),
                ('ac', 'ac', 'interj', '', '')]
        words = ['aa', 'ab', 'ac', 'zz']
        blob, _ = self.index(words, rows)
        again, _ = self.index(words, rows)
        self.assertEqual(blob, again)
        _, _, lists, forms, _ = read(blob)
        self.assertEqual(forms[b'ab'], 0)
        self.assertEqual(forms[b'ac'], 0)
        self.assertEqual(forms[b'zz'], 1)
        self.assertEqual(forms[b'aa'], 2)

    def test_cut_counts_utf8_bytes_for_polish_ending(self):
        rows = [('gęsią', 'gęś', 'subst:sg:inst:f', '', ''),
                ('mąk', 'męka', 'subst:pl:gen:f', '', '')]
        blob, _ = self.index(['gęsią', 'mąk'], rows)
        _, analyses, _, forms, rules = read(blob)
        self.assertEqual(analyses['gęsią'], [('gęś', 'subst:sg:inst:f', '')])
        self.assertEqual(analyses['mąk'], [('męka', 'subst:pl:gen:f', '')])
        # 'gęsią' i 'gęś' dzielą 'gę' (3 bajty); reszta formy 'sią' to 4 bajty UTF-8, nie 3 znaki.
        cuts = sorted(rule[0] for rule in rules)
        self.assertEqual(cuts, [3, 4])

    def test_form_missing_from_sgjp_is_absent(self):
        blob, stats = self.index(['abym', 'kot'], [('kot', 'kot', 'subst:sg:nom:m2', '', ''),
                                                  ('pies', 'pies', 'subst:sg:nom:m2', '', '')])
        _, analyses, *_ = read(blob)
        self.assertEqual(list(analyses), ['kot'])
        self.assertEqual(stats['broad_forms'], 2)
        self.assertEqual(stats['forms_with_analysis'], 1)

    def test_bad_dawg_sha256_is_refused(self):
        broad, sgjp = self.files(['kot'], [('kot', 'kot', 'subst:sg:nom:m2', '', '')])
        for bad in ('ab' * 31, 'AB' * 32, 'zz' * 32, 'ab' * 32 + ' '):
            with self.assertRaises(GeneratorError) as caught:
                build(broad, sgjp, 'pl-test', bad, builder='x')
            self.assertEqual(caught.exception.code, 2)
        out = self.dir / 'out.bin'
        result = subprocess.run([sys.executable, '-m', 'literaki_slownik', 'morph-index', '--broad', str(broad),
                                 '--sgjp', str(sgjp), '--broad-lexicon-id', 'pl-test',
                                 '--broad-dawg-sha256', 'ab' * 31, '--out', str(out), '--json'],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertEqual(json.loads(result.stdout)['status'], 'error')
        self.assertFalse(out.exists())


if __name__ == '__main__':
    unittest.main()
