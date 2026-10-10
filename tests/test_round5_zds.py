"""Runda 5 (2026-10-08): ZDS §1/§5 jako zasady gry."""
import gzip
import hashlib
import tempfile
import unittest
from pathlib import Path
from literaki_slownik.build import build
from literaki_slownik.canonical import load_json
from literaki_slownik.constructions import (mobile_aglt_candidates, nie_degree_candidates,
                                            pred_particle_candidates)
from literaki_slownik.decisions import assess_diagnostic, assessment
from literaki_slownik.explain import explain
from literaki_slownik.policy import source_game_checks
from tests.helpers import rewrite
from tests.release_helpers import SGJP, fixture_inputs


def source(original, tag, lemma=None, names='', qualifiers=''):
    return {'source_id': 'S', 'first_source_row': 1, 'original': original, 'lemma_id': lemma or original,
            'raw_tag': tag, 'names': names, 'qualifiers': qualifiers}


def membership(candidate, variant='standard'):
    components = [c['interpretation'] for c in candidate['components'] if c['kind'] == 'source_interpretation']
    return assess_diagnostic(candidate['original'], candidate['qualifiers'], [], components,
                             candidate)['membership'][variant]['status']


class Round5Tests(unittest.TestCase):
    def test_zds_named_exclusions_and_abc(self):
        for original, tag in (('desa', 'subst:sg:nom:f'), ('abc', 'subst:sg:nom:n')):
            s = source(original, tag, names='nazwa_pospolita')
            self.assertEqual(assessment(source_game_checks(s))['status'], 'reject', original)
        self.assertEqual(assessment(source_game_checks(source('desant', 'subst:sg:nom:m3',
                                                              names='nazwa_pospolita')))['status'], 'accept')

    def test_brand_names_rejected_mixed_meaning_lemmas_kept(self):
        for lemma in ('toyota', 'ford', 'warszawa', 'facebook', 'volkswagen'):
            s = source(lemma, 'subst:sg:nom:f', names='nazwa_pospolita')
            self.assertEqual(assessment(source_game_checks(s))['status'], 'reject', lemma)
        for lemma in ('polonez', 'syrena', 'jaguar', 'tesla', 'maluch'):
            s = source(lemma, 'subst:sg:nom:m3', names='nazwa_pospolita')
            self.assertEqual(assessment(source_game_checks(s))['status'], 'accept', lemma)

    def test_bodaj_takes_verbal_endings_other_hosts_still_rejected(self):
        em = source('em', 'aglt:sg:pri:imperf:wok', 'być')
        bodajem = mobile_aglt_candidates(source('bodaj', 'part'), em)
        self.assertEqual([c['original'] for c in bodajem], ['bodajem'])
        self.assertEqual(membership(bodajem[0]), 'accept')
        m = source('m', 'aglt:sg:pri:imperf:nwok', 'być')
        albom = mobile_aglt_candidates(source('albo', 'part'), m)
        self.assertEqual(membership(albom[0]), 'reject')

    def test_trzeba_mozna_take_ze(self):
        self.assertEqual([c['original'] for c in pred_particle_candidates(source('trzeba', 'pred'))], ['trzebaż'])
        self.assertEqual(membership(pred_particle_candidates(source('można', 'pred'))[0]), 'accept')
        self.assertEqual(pred_particle_candidates(source('warto', 'pred')), [])

    def test_nie_with_every_degree(self):
        exists = {'niedrogi'}.__contains__
        com = nie_degree_candidates(source('droższy', 'adj:sg:nom:m1:com', 'drogi'), exists)
        self.assertEqual([c['original'] for c in com], ['niedroższy'])
        self.assertEqual(membership(com[0]), 'accept')
        sup = nie_degree_candidates(source('najdrożej', 'adv:sup', 'drogo'), exists)
        self.assertEqual([c['original'] for c in sup], ['nienajdrożej'])
        # Stopień równy: tylko bez źródłowego napisu; lematy na nie- pomijamy.
        self.assertEqual(nie_degree_candidates(source('drogi', 'adj:sg:nom:m1:pos', 'drogi'), exists), [])
        self.assertEqual([c['original'] for c in nie_degree_candidates(source('tani', 'adj:sg:nom:m1:pos', 'tani'), exists)],
                         ['nietani'])
        self.assertEqual(nie_degree_candidates(source('niemiły', 'adj:sg:nom:m1:pos', 'niemiły'), exists), [])
        self.assertEqual(nie_degree_candidates(source('jutro', 'adv', 'jutro'), exists), [])

    def test_explain_matches_build_for_contemporary_use(self):
        with tempfile.TemporaryDirectory() as directory:
            directory = Path(directory)
            manifest_path = fixture_inputs(directory, sgjp=SGJP + 'wraz\twraz:D\tadv\t\tdaw.\n'
                                       'trzeba\ttrzeba\tpred\t\t\ndroższy\tdrogi\tadj:sg:nom:m1:com\t\t\n')
            manifest = load_json(manifest_path)
            corpus = directory / 'lc-fakt.csv.gz'
            with gzip.open(corpus, 'wt', encoding='utf-8') as stream:
                stream.write(',freq,ipm,ARF,DP,DP_norm,1-DP,total_freq\nwraz,40,1,1,0,0,1,40\n')
            manifest['artifacts'].append(dict(manifest['artifacts'][1], source_id='lc-fakt', kind='kwjp_orth',
                                              path=corpus.name, genre='fakt',
                                              sha256=hashlib.sha256(corpus.read_bytes()).hexdigest()))
            rewrite(manifest_path, manifest)
            run = directory / 'run'
            build(manifest_path, run)
            standard = (run / 'lists/standard.txt').read_text(encoding='utf-8').split()
            for word in ('wraz', 'trzebaż', 'niedroższy'):
                self.assertIn(word, standard, word)
            for word in ('trzebaż', 'niedroższy'):
                self.assertEqual([d['rule_id'] for d in explain(run, word, 'standard')['derivations']],
                                 ['pred-particle-ze-v1' if word == 'trzebaż' else 'nie-prefix-degree-v1'], word)
            value = explain(run, 'wraz', 'standard')
            self.assertEqual([a['assessment']['membership']['standard']['status'] for a in value['analyses']],
                             ['accept'])


if __name__ == '__main__':
    unittest.main()
