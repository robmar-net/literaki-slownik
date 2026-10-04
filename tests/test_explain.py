"""Explain zachowuje wpisy i niewiadome; odczyt nie zmienia przebiegu."""
import gzip
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from tests.helpers import fixture_manifest, rewrite
from literaki_slownik.build import build
from literaki_slownik.canonical import load_json, sha256, write_json
from literaki_slownik.database import connect
from literaki_slownik.explain import explain
from literaki_slownik.links import create_links


class ExplainTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        root = Path(self.temp.name)
        manifest_path, manifest = fixture_manifest(root)
        lines = ['PCV\tPCV\tsubst:sg:nom:m3\tnazwa_pospolita\t',
                 'DNA\tDNA\tsubst:sg:nom:n\tnazwa_pospolita\t',
                 'dna\tdno\tsubst:pl:nom.acc:n\t\t',
                 'dna\tdna\tsubst:sg:nom:f\t\t',
                 'żaba\tżaba\tsubst:sg:nom:f\t\t']
        lines.append('kakaa\tkakao\tsubst:sg:gen:n\t\tniezal.')
        lines += [f'kot\tkot:S{i}\tsubst:sg:nom:m2\t\t' for i in range(150)]
        source = root / 'source.gz'
        with gzip.open(source, 'wt', encoding='utf-8') as stream:
            stream.write('#</COPYRIGHT>\n' + '\n'.join(lines) + '\n')
        manifest['artifacts'][0]['sha256'] = sha256(source)
        rewrite(manifest_path, manifest)
        self.run = root / 'run'
        build(manifest_path, self.run)

    def test_approved_disrecommended_condition_visible_without_full_acceptance(self):
        value = explain(self.run, 'kakaa')
        analysis = value['analyses'][0]
        self.assertEqual(analysis['qualifiers'], 'niezal.')
        for variant in ('broad', 'standard'):
            language = analysis['assessment']['language'][variant]
            self.assertEqual(language['status'], 'unresolved')
            confirmed = [c for c in language['checks'] if c['rule_id'] == 'linguistic-disrecommended-non-excluding-v1']
            self.assertEqual(len(confirmed), 1)
            self.assertEqual(confirmed[0]['status'], 'accept')
        self.assertEqual(value['list_membership']['status'], 'unresolved')

    def test_readonly_all_originals_homonyms_and_expanded_tags(self):
        before = [sha256(self.run / f) for f in ('manifest.json', 'build.sqlite')]
        value = explain(self.run, 'DNA')
        self.assertEqual(value['source_presence'], 'present')
        self.assertEqual(len(value['analyses']), 3)
        by_lemma = {a['lemma_id']: a for a in value['analyses']}
        self.assertEqual(by_lemma['DNA']['assessment']['game']['status'], 'reject')
        self.assertEqual(by_lemma['dno']['expanded_tags'], ['subst:pl:nom:n', 'subst:pl:acc:n'])
        self.assertEqual(value['list_membership']['status'], 'unresolved')
        self.assertEqual(len(explain(self.run, 'kot')['analyses']), 150)
        self.assertEqual(explain(self.run, 'z\u0307aba')['source_presence'], 'present')
        self.assertEqual(before, [sha256(self.run / f) for f in ('manifest.json', 'build.sqlite')])

    def test_uppercase_and_profile_both_visible_without_lexical_accept(self):
        value = explain(self.run, 'pcv')
        assessed = value['analyses'][0]['assessment']
        self.assertEqual(assessed['language']['standard']['status'], 'unresolved')
        self.assertEqual(assessed['game']['status'], 'reject')
        self.assertEqual(assessed['profile']['invalid_characters'], ['v'])
        self.assertEqual(assessed['membership']['standard']['status'], 'reject')

    def test_absence_in_partial_import_is_not_absence_in_source(self):
        self.assertEqual(explain(self.run, 'nieistniejące')['source_presence'], 'absent')
        path = self.run / 'manifest.json'
        manifest = load_json(path)
        manifest['stages']['import_sgjp']['status'] = 'failed'
        write_json(path, manifest)
        value = explain(self.run, 'nieistniejące')
        self.assertEqual(value['source_presence'], 'not_observed_in_incomplete_import')
        self.assertTrue(value['diagnostics'])
        self.assertEqual(value['list_membership']['status'], 'unresolved')

    def test_corpus_observation_once_with_all_candidates_and_no_sense_claim(self):
        with connect(self.run / 'build.sqlite') as db:
            db.execute('insert into source_artifact values (?,?,?)', ('KWJP', 'kwjp_lemma', json.dumps({'genre': 'all'})))
            db.execute('insert into corpus_evidence values (?,?,?,?,?,?,?,?,?)',
                       (1, 'KWJP', 1, 'kot', None, 'subst', '{"freq":"7"}', '{"freq":7}', 7))
            create_links(db)
        value = explain(self.run, 'kot')
        observations = value['corpus']['observations']
        self.assertEqual(len(observations), 1)
        self.assertEqual(observations[0]['typed_metrics']['freq'], 7)
        self.assertEqual(len(observations[0]['candidates']), 150)
        self.assertFalse(observations[0]['sense_identity_confirmed'])
        self.assertEqual(value['corpus']['unavailable'][0]['source_id'], 'NKJP')

    def test_cli_json_text_and_operational_error(self):
        cmd = [sys.executable, '-m', 'literaki_slownik', 'explain', '--run-dir', str(self.run), '--word', 'pcv']
        result = subprocess.run(cmd + ['--json'], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)['result']['source_presence'], 'present')
        result = subprocess.run(cmd, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('PCV', result.stdout)
        self.assertIn('niewiadome', result.stdout)
        result = subprocess.run(cmd + ['--variant', 'other', '--json'], capture_output=True, text=True)
        self.assertEqual(result.returncode, 2)
        self.assertEqual(json.loads(result.stdout)['status'], 'error')
        cmd[cmd.index(str(self.run))] = str(self.run / 'missing')
        result = subprocess.run(cmd + ['--json'], capture_output=True, text=True)
        self.assertEqual(result.returncode, 4)
        self.assertEqual(json.loads(result.stdout)['status'], 'error')
        self.assertNotIn('Traceback', result.stderr)
