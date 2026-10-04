import gzip
import hashlib
import tempfile
import unittest
from pathlib import Path
from tests.helpers import fixture_manifest, rewrite
from literaki_slownik.build import build
from literaki_slownik.database import connect
from literaki_slownik.canonical import load_json
from literaki_slownik.inputs import GeneratorError


class BuildTests(unittest.TestCase):
    def manifest(self, directory, contents):
        p, manifest = fixture_manifest(directory)
        source = Path(directory) / 'source.gz'
        with gzip.open(source, 'wt', encoding='utf-8') as stream:
            stream.write(contents)
        manifest['artifacts'][0]['sha256'] = hashlib.sha256(source.read_bytes()).hexdigest()
        rewrite(p, manifest)
        return p

    def test_duplicates_homonyms_and_outside_profile_preserved(self):
        with tempfile.TemporaryDirectory() as directory:
            p = self.manifest(directory, '#</COPYRIGHT>\nkot\tkot:S1\tsubst:sg:nom.acc:m2\t\t\nkot\tkot:S1\tsubst:sg:nom.acc:m2\t\t\nRóża\tRóża:S2\tsubst:sg:nom:f\timię\t\npol-ski\tpolski\tadj:sg:nom:m1:pos\t\t\n')
            run = Path(directory) / 'run'
            result = build(p, run, batch_size=1)
            counts = result['counts']['synthetic']
            self.assertEqual(counts['records'], 4)
            self.assertEqual(counts['interpretations'], 3)
            self.assertEqual(counts['expanded_alternatives'], 4)
            with connect(run / 'build.sqlite') as db:
                self.assertEqual(db.execute('select count(*) from sgjp_record').fetchone()[0], 4)
                self.assertEqual(db.execute('select lemma_id from lexeme where lemma_id like ?', ('kot%',)).fetchone()[0], 'kot:S1')
                self.assertEqual(db.execute('select original from surface_form where original=?', ('pol-ski',)).fetchone()[0], 'pol-ski')
            self.assertEqual(load_json(run / 'manifest.json')['readiness'], 'INCOMPLETE')

    def test_failure_after_committed_batch_not_complete(self):
        with tempfile.TemporaryDirectory() as directory:
            p = self.manifest(directory, '#</COPYRIGHT>\nkot\tkot\tsubst\t\t\nbad\trow\n')
            run = Path(directory) / 'run'
            with self.assertRaises(GeneratorError):
                build(p, run, batch_size=1)
            stage = load_json(run / 'manifest.json')['stages']['import_sgjp']
            self.assertEqual(stage['status'], 'failed')
            with connect(run / 'build.sqlite') as db:
                self.assertEqual(db.execute('select count(*) from sgjp_record').fetchone()[0], 1)

    def test_count_mismatch_is_not_success(self):
        with tempfile.TemporaryDirectory() as directory:
            p = self.manifest(directory, '#</COPYRIGHT>\nkot\tkot\tsubst\t\t\n')
            manifest = load_json(p)
            manifest['artifacts'][0]['expected_counts'] = {'records': 2}
            rewrite(p, manifest)
            with self.assertRaises(GeneratorError):
                build(p, Path(directory) / 'run')
