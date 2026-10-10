"""Konstrukcja liczy się w powiązaniu raz, bez względu na liczbę tagów (przegląd K9, 2026-10-10)."""
import gzip
import hashlib
import sqlite3
import tempfile
import unittest
from pathlib import Path
from literaki_slownik.build import build
from literaki_slownik.canonical import load_json
from literaki_slownik.links import candidates
from tests.helpers import rewrite
from tests.release_helpers import SGJP, fixture_inputs


def database(rows, forms=()):
    db = sqlite3.connect(':memory:')
    db.execute('create table surface_form (id integer primary key, original text, nfc text, game_key text, length int)')
    db.execute('create table derivation_candidate (candidate_key text primary key, rule_id text, original text,'
               ' game_key text, lemma_id text, expanded_tag text, names text, qualifiers text, payload text)')
    db.executemany('insert into surface_form(original,nfc,game_key,length) values (?,?,?,?)',
                   [(f, f, f.lower(), len(f)) for f in forms])
    db.executemany('insert into derivation_candidate values (?,?,?,?,?,?,?,?,?)',
                   [(f'k{i}', rule, original, original.lower(), lemma, tag, '', '', '{}')
                    for i, (rule, original, lemma, tag) in enumerate(rows)])
    return db


class LinkStructureTests(unittest.TestCase):
    def test_one_construction_many_tags_is_exact(self):
        db = database([('nie-prefix-degree-v1', 'nienajlepszy', 'dobry:A', t)
                       for t in ('adj:sg:nom:m1:sup', 'adj:sg:nom:m2:sup', 'adj:sg:acc:m3:sup')])
        result = candidates(db, 'kwjp_orth', 'nienajlepszy')
        self.assertEqual(result['status'], 'EXACT_CANDIDATE')
        self.assertEqual(len(result['candidates']), 3)  # krawędzie do każdego kandydata zostają

    def test_different_structures_stay_ambiguous(self):
        db = database([('mobile-source-host-aglt-v1', 'coś', 'co:S', 'aglt'),
                       ('mobile-source-host-aglt-v1', 'coś', 'co:M', 'aglt')])
        self.assertEqual(candidates(db, 'kwjp_orth', 'coś')['status'], 'AMBIGUOUS')
        db = database([('nie-prefix-degree-v1', 'niebezpieczniejszy', 'bezpieczny', 'adj:com')],
                      forms=('niebezpieczniejszy',))
        self.assertEqual(candidates(db, 'kwjp_orth', 'niebezpieczniejszy')['status'], 'AMBIGUOUS')

    def test_build_link_gate_counts_structures(self):
        with tempfile.TemporaryDirectory() as directory:
            directory = Path(directory)
            path = fixture_inputs(directory, sgjp=SGJP + 'droższy\tdrogi\tadj:sg:nom.voc:m1.m2.m3:com\t\t\n')
            manifest = load_json(path)
            corpus = directory / 'orth.csv.gz'
            with gzip.open(corpus, 'wt', encoding='utf-8') as stream:
                stream.write(',freq,ipm,ARF,DP,DP_norm,1-DP,total_freq\nniedroższy,9,1,1,0,0,1,9\n')
            manifest['artifacts'].append(dict(manifest['artifacts'][1], source_id='orth', kind='kwjp_orth',
                                              path=corpus.name, sha256=hashlib.sha256(corpus.read_bytes()).hexdigest()))
            rewrite(path, manifest)
            run = directory / 'run'
            build(path, run)
            self.assertTrue(load_json(run / 'reports/links.json')['stage_completion']['complete'])
            db = sqlite3.connect(run / 'build.sqlite')
            try:
                rows = db.execute("""select l.status,count(c.candidate_key) from corpus_evidence e
                    join evidence_link l on l.evidence_id=e.id join evidence_candidate c on c.evidence_id=e.id
                    where e.unit_1='niedroższy' group by l.status""").fetchall()
            finally:
                db.close()
            self.assertEqual(rows, [('EXACT_CANDIDATE', 6)])  # nom.voc × m1.m2.m3


if __name__ == '__main__':
    unittest.main()
