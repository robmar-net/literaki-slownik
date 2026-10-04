import gzip
import tempfile
import unittest
from pathlib import Path
from literaki_slownik.sgjp import rows, expand_tag
from literaki_slownik.inputs import GeneratorError


class SgjpTests(unittest.TestCase):
    def test_original_fields_and_expansion(self):
        with tempfile.TemporaryDirectory() as directory:
            p = Path(directory) / 'input.gz'
            with gzip.open(p, 'wt', encoding='utf-8') as stream:
                stream.write('# test\n#</COPYRIGHT>\nRóża\tRóża:S1\tsubst:sg:nom.acc:f\timię\tdaw.|książk.\n')
            result = list(rows(p))
            self.assertEqual(result[0][1][1], 'Róża:S1')
            self.assertEqual(result[0][1][4], 'daw.|książk.')
            self.assertEqual(list(expand_tag('subst:sg:nom.acc:f')), ['subst:sg:nom:f', 'subst:sg:acc:f'])

    def test_invalid_format_and_gzip(self):
        for contents in ['# brak końca\n', '#</COPYRIGHT>\na\tb\n']:
            with tempfile.TemporaryDirectory() as directory:
                p = Path(directory) / 'input.gz'
                with gzip.open(p, 'wt', encoding='utf-8') as stream:
                    stream.write(contents)
                with self.assertRaises(GeneratorError):
                    list(rows(p))
        with tempfile.TemporaryDirectory() as directory:
            p = Path(directory) / 'bad.gz'
            p.write_bytes(b'broken')
            with self.assertRaises(GeneratorError):
                list(rows(p))
