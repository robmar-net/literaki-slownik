"""Kontrola śladów dowodowych, bez oceny dopuszczalności."""
import importlib.util
import json
import sqlite3
import tarfile
import tempfile
import io
import unittest
from contextlib import closing
from unittest.mock import patch
from pathlib import Path


class PanProbeTest(unittest.TestCase):
    def test_alternative_meanings_and_context_are_not_decisions(self):
        path = Path(__file__).resolve().parents[1] / 'scripts/probe_pan_semantics.py'
        spec = importlib.util.spec_from_file_location('pan_probe', path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            db = root / 'input.sqlite'
            with closing(sqlite3.connect(db)) as conn, conn:
                conn.executescript('CREATE TABLE sgjp_record(source_id,row_number,form,lemma,tag,names,qualifiers);')
                conn.executemany('INSERT INTO sgjp_record VALUES(?,?,?,?,?,?,?)', [
                    ('sgjp-test', 1, 'oścież', 'oścież:F', 'frag', '', ''),
                    ('sgjp-test', 2, 'oścież', 'oścież:S', 'subst:sg:nom:f', 'nazwa_pospolita', ''),
                    ('sgjp-test', 3, 'oścież', 'oścież:F', 'frag', '', ''),
                    ('sgjp-test', 4, 'Bin', 'Bin:F', 'frag', '', ''),
                    ('sgjp-test', 5, 'bin', 'bin:V', 'impt:sg:sec:imperf', '', ''),
                    ('sgjp-test', 6, 'pro', 'pro:F', 'frag', '', ''),
                ])
            samples = root / 'samples.tar.gz'
            obj = {'meta': {'id': 'test', 'meta_author': 'Autor testowy'}, 'samples': [
                {'text': 'Drzwi na oścież. Bin i bin. ościeżnica. pro-Test.'},
                {'text': 'Bez dopasowania.'},
            ]}
            raw = json.dumps(obj).encode()
            with tarfile.open(samples, 'w:gz') as archive:
                info = tarfile.TarInfo('samples/test.json'); info.size = len(raw)
                archive.addfile(info, io.BytesIO(raw))
            connection=sqlite3.connect(db.resolve().as_uri()+'?mode=ro',uri=True)
            with patch.object(module.sqlite3,'connect',return_value=connection):
                result = module.probe(db, samples, [])
            with self.assertRaises(sqlite3.ProgrammingError):
                connection.execute('select 1')
            self.assertEqual(len(result['cases']), 3)
            by_form = {c['source']['original']: c for c in result['cases']}
            case = by_form['oścież']
            self.assertEqual(case['source']['row_numbers'], [1, 3])
            self.assertEqual(case['other_source_analyses'][0]['lemma_id'], 'oścież:S')
            self.assertEqual(case['sample_matches'][0]['matched_forms'], ['oścież'])
            self.assertNotIn('text', case['sample_matches'][0])
            self.assertEqual(len(by_form['Bin']['other_source_analyses']), 1)
            self.assertEqual(by_form['Bin']['sample_matches'][0]['matched_forms'], ['Bin', 'bin'])
            self.assertEqual(case['semantic_status'], 'unresolved')
            self.assertEqual(by_form['pro']['sample_matches'], [])
            self.assertFalse(result['automatic_eligibility_decisions'])


if __name__ == '__main__':
    unittest.main()
