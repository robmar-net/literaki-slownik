import gzip
import tempfile
import unittest
from pathlib import Path
from literaki_slownik.sgjp import rows, expand_tag
from literaki_slownik.inputs import GeneratorError


class SgjpTests(unittest.TestCase):
    def test_pinned_winien_errata_preserve_raw_tag_and_all_gender_alternatives(self):
        from literaki_slownik.sgjp import tag_errata
        digest = '3b2ee079143bc95186370fd528735779c4ba62f4ce14e30cf6622ceb566e9810'
        tag = 'winien:pl:m2.m3.f.n:sec:imperf'
        for lemma,form in [('gotów','gotoweśmy'),('kontent:V','kontenteśmy'),
                           ('niekontent:V','niekontenteśmy'),('nierad:V','nieradeśmy'),
                           ('powinien','powinnyśmy'),('rad:V','radeśmy'),('winien','winnyśmy')]:
            correction, = tag_errata(digest,lemma,form,tag)
            self.assertEqual(correction['raw_tag'],tag)
            self.assertEqual(correction['corrected_tag'],'winien:pl:m2.m3.f.n:pri:imperf')
            self.assertEqual(len(correction['corrected_expanded_tags']),4)

    def test_erratum_never_guesses_suffix_or_applies_to_other_snapshot(self):
        from literaki_slownik.sgjp import tag_errata
        digest = '3b2ee079143bc95186370fd528735779c4ba62f4ce14e30cf6622ceb566e9810'
        tag = 'winien:pl:m2.m3.f.n:sec:imperf'
        for sha,lemma,form,raw in [('other','winien','winnyśmy',tag),
                                  (digest,'winien:other','winnyśmy',tag),
                                  (digest,'winien','inneśmy',tag),
                                  (digest,'winien','winnyśmy','winien:pl:m2.m3.f.n:pri:imperf')]:
            self.assertEqual(tag_errata(sha,lemma,form,raw),[])

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
