"""Testy przepięcia ocen morza (#12 W9) na syntetycznym pakiecie.

Uruchomienie: python3 -m unittest discover -s <T>/analysis -p 'test_przepnij_morze.py'
"""
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import przepnij_morze as pm  # noqa: E402

ck = pm.checker
WARSTWY = {'a1': 'T1', 'a2': 'T1', 'b1': 'T2', 'b2': 'T2', 'c1': 'T3'}
STRATA_OP = {'T2': ['b1', 'b2'], 'T3': ['c1']}


def pakiet(root):
    (root/'reports').mkdir(parents=True)
    (root/'SHA256SUMS').write_text('abc  plik\n', encoding='utf-8')
    strata = {}
    for k, w in WARSTWY.items():
        strata.setdefault(w, {'selected': []})['selected'].append({'key': k})
    files = {'release-manifest.json': {'method': 'tematy-v2'},
             'reports/sample.json': {'strata': strata, 'operator': {'per_stratum': 2, 'strata': STRATA_OP}},
             'reports/review-template.json': {'sample_sha256': 'n' * 64, 'canonical_index_sha256': 'c' * 64,
                                              'evidence_sha256': {'summary.json': 'e' * 64},
                                              'version': 'tematy-quality-v1'}}
    for name, data in files.items():
        (root/name).write_text(json.dumps(data), encoding='utf-8')


def stary():
    agent = [{'key': k, 'warstwa': w, 'ocena': 'tak', 'powod': 'p'} for k, w in sorted(WARSTWY.items())]
    sha = ck.ratings_sha256(agent)
    return {'schema_version': 1, 'kind': ck.REVIEW_KIND, 'method': 'tematy-v1', 'temat': 'morze',
            'version': 'stara', 'sha256sums_sha256': 's' * 64, 'sample_sha256': 'o' * 64,
            'canonical_index_sha256': 'x' * 64, 'evidence_sha256': {'summary.json': 'f' * 64},
            'agent': {'reviewer': 'agent', 'reviewed_at': 't0', 'items': agent}, 'agent_sha256': sha,
            'operator': {'reviewer': 'operator', 'reviewed_at': 't1', 'agent_sha256': sha,
                         'items': [{'key': k, 'warstwa': w, 'ocena': 'nie' if k == 'b2' else 'tak'}
                                   for k, w in sorted(WARSTWY.items())]}}


class Przepiecie(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        pakiet(self.root)
        self.old = stary()
        self.new = pm.przepnij(json.loads(json.dumps(self.old)), self.root)

    def tearDown(self):
        self.tmp.cleanup()

    def test_wiazanie_z_szablonu_i_sha256sums(self):
        template = json.loads((self.root/'reports/review-template.json').read_text())
        for pole in ('sample_sha256', 'canonical_index_sha256', 'evidence_sha256', 'version'):
            self.assertEqual(self.new[pole], template[pole])
        self.assertEqual(self.new['sha256sums_sha256'],
                         hashlib.sha256((self.root/'SHA256SUMS').read_bytes()).hexdigest())
        self.assertEqual(self.new['method'], 'tematy-v2')

    def test_agent_bez_zmian_operator_tylko_t2_t3(self):
        self.assertEqual(self.new['agent'], self.old['agent'])
        self.assertEqual(self.new['agent_sha256'], self.old['agent_sha256'])
        op = self.new['operator']
        self.assertEqual(op['agent_sha256'], self.new['agent_sha256'])
        self.assertEqual([i['key'] for i in op['items']], ['b1', 'b2', 'c1'])
        self.assertEqual({i['key']: (i['warstwa'], i['ocena']) for i in op['items']},
                         {'b1': ('T2', 'tak'), 'b2': ('T2', 'nie'), 'c1': ('T3', 'tak')})
        self.assertEqual((op['reviewer'], op['reviewed_at']), ('operator', 't1'))


if __name__ == '__main__':
    unittest.main()
