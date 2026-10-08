"""Runda 4 (2026-10-08): poprawki z benchmarku SJP.pl, decyzje właściciela i agenta."""
import gzip
import hashlib
import json
import sqlite3
import tempfile
import unittest
from pathlib import Path
from literaki_slownik.build import build
from literaki_slownik.canonical import load_json
from literaki_slownik.decisions import assess_diagnostic, assessment
from literaki_slownik.policy import (CLASS_MATRIX, CONTEMPORARY_USE_MIN_NONFICTION, resident_screen_checks,
                                     source_game_checks)
from literaki_slownik import sgjp
from tests.helpers import rewrite
from tests.release_helpers import SGJP, fixture_inputs

ROOT = Path(__file__).resolve().parent.parent


def source(tag, original, lemma_id=None, names='nazwa_pospolita', qualifiers=''):
    return {'original': original, 'lemma_id': lemma_id or original, 'raw_tag': tag, 'names': names,
            'qualifiers': qualifiers, 'source_id': 'x', 'first_source_row': 1}


def game(s):
    return assessment(source_game_checks(s))['status']


class Round4Tests(unittest.TestCase):
    def test_supplement_adds_reflexive_pronoun_in_sgjp_format(self):
        rows = [fields[:3] for _, fields in sgjp.rows(ROOT / 'config/generator/sgjp-supplement.tab')]
        self.assertEqual(rows, [['się', 'się', 'part'], ['siebie', 'siebie', 'siebie:gen.acc'],
                                ['sobie', 'siebie', 'siebie:dat.loc'], ['sobą', 'siebie', 'siebie:inst']])
        self.assertEqual(CLASS_MATRIX['siebie'], 'word')
        manifest = load_json(ROOT / 'config/generator/sources.json')
        supplement = [a for a in manifest['artifacts'] if a['kind'] == 'lexical_supplement']
        self.assertEqual([a['path'] for a in supplement], ['../../config/generator/sgjp-supplement.tab'])
        for original, tag in (('się', 'part'), ('siebie', 'siebie:gen'), ('sobą', 'siebie:inst')):
            a = assess_diagnostic(original, '', source_analyses=[source(tag, original, names='')])
            self.assertEqual(a['membership']['standard']['status'], 'accept', original)

    def test_agl_stem_is_not_a_standalone_word(self):
        self.assertEqual(game(source('praet:sg:m1:imperf:agl', 'mogł', 'móc', names='')), 'reject')
        self.assertEqual(game(source('praet:sg:m1:imperf:nagl', 'mógł', 'móc', names='')), 'accept')
        self.assertEqual(game(source('praet:pl:m1:imperf', 'mogli', 'móc', names='')), 'accept')

    def test_abbreviation_nouns_rejected_ordinary_homographs_kept(self):
        for lemma, tag in (('nr', 'subst:sg:nom:m3'), ('dr', 'subst:sg:nom:m1'), ('sms', 'subst:sg:nom:m3'),
                           ('bmw', 'subst:sg:nom:m3'), ('abp', 'subst:sg:gen:m1'), ('ha:S', 'subst:sg:nom:n')):
            self.assertEqual(game(source(tag, lemma.split(':')[0], lemma)), 'reject', lemma)
        for lemma, tag in (('dom', 'subst:sg:nom:m3'), ('ul', 'subst:sg:nom:m3'), ('gen', 'subst:sg:nom:m3'),
                           ('ha', 'interj')):
            self.assertEqual(game(source(tag, lemma, lemma, names='' if tag == 'interj' else 'nazwa_pospolita')),
                             'accept', lemma)

    def test_round4_resident_exceptions(self):
        for lemma, tag in (('sielanka', 'subst:sg:nom:f'), ('przytulanka', 'subst:sg:nom:f'),
                           ('kijanka', 'subst:sg:nom:f'), ('markietanka', 'subst:sg:nom:f'),
                           ('powodzianin', 'subst:sg:nom:m1'), ('powodzianka', 'subst:sg:nom:f'),
                           ('targowiczanin', 'subst:sg:nom:m1')):
            self.assertEqual(resident_screen_checks(source(tag, lemma)), [], lemma)
        # Mieszkańcy spoza wyjątków nadal odpadają.
        for lemma, tag in (('chorzowianin', 'subst:sg:nom:m1'), ('chorzowianka', 'subst:sg:nom:f')):
            self.assertEqual([c['rule_id'] for c in resident_screen_checks(source(tag, lemma))],
                             ['game-resident-screen-capital-2026-v1'], lemma)

    def test_contemporary_use_lifts_only_the_age_rejection_in_standard(self):
        wraz = [source('adv', 'wraz', 'wraz:D', names='', qualifiers='daw.')]
        at = assess_diagnostic('wraz', 'daw.', source_analyses=wraz, contemporary_frequency=CONTEMPORARY_USE_MIN_NONFICTION)
        below = assess_diagnostic('wraz', 'daw.', source_analyses=wraz,
                                  contemporary_frequency=CONTEMPORARY_USE_MIN_NONFICTION - 1)
        self.assertEqual(at['membership']['standard']['status'], 'accept')
        self.assertIn('linguistic-contemporary-use-kwjp-v1', [c['rule_id'] for c in at['language']['standard']['checks']])
        self.assertEqual(below['membership']['standard']['status'], 'reject')
        self.assertEqual(at['membership']['broad']['status'], 'accept')
        # Inne odmowy (np. wielka litera) zostają.
        upper = assess_diagnostic('Wraz', 'daw.', source_analyses=[source('adv', 'Wraz', 'Wraz', names='', qualifiers='daw.')],
                                  contemporary_frequency=10**6)
        self.assertEqual(upper['membership']['standard']['status'], 'reject')

    def test_build_uses_supplement_and_nonfiction_frequency(self):
        with tempfile.TemporaryDirectory() as directory:
            directory = Path(directory)
            data = SGJP + 'wraz\twraz:D\tadv\t\tdaw.\nniewiasta\tniewiasta\tsubst:sg:nom:f\tnazwa_pospolita\tdaw.\n'
            manifest_path = fixture_inputs(directory, sgjp=data)
            manifest = load_json(manifest_path)
            corpus = directory / 'lc-publicystyka.csv.gz'
            with gzip.open(corpus, 'wt', encoding='utf-8') as stream:
                stream.write(',freq,ipm,ARF,DP,DP_norm,1-DP,total_freq\n'
                             f'wraz,{CONTEMPORARY_USE_MIN_NONFICTION},1,1,0,0,1,30\nniewiasta,5,1,1,0,0,1,5\n')
            base = manifest['artifacts'][1]
            manifest['artifacts'].append(dict(base, source_id='lc-publicystyka', kind='kwjp_orth_lc',
                                              path=corpus.name, genre='publicystyka',
                                              sha256=hashlib.sha256(corpus.read_bytes()).hexdigest()))
            supplement = directory / 'supplement.tab'
            supplement.write_bytes((ROOT / 'config/generator/sgjp-supplement.tab').read_bytes())
            manifest['artifacts'].append(dict(manifest['artifacts'][0], source_id='supplement',
                                              kind='lexical_supplement', path=supplement.name,
                                              sha256=hashlib.sha256(supplement.read_bytes()).hexdigest()))
            rewrite(manifest_path, manifest)
            run = directory / 'run'
            build(manifest_path, run)
            lists = {v: (run / 'lists' / f'{v}.txt').read_text(encoding='utf-8').split()
                     for v in ('broad', 'standard')}
            for word in ('się', 'siebie', 'sobie', 'sobą', 'wraz'):
                self.assertIn(word, lists['standard'], word)
            self.assertIn('niewiasta', lists['broad'])
            self.assertNotIn('niewiasta', lists['standard'])


if __name__ == '__main__':
    unittest.main()
