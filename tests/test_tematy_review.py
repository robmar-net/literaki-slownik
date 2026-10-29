"""Strona R2 i zapis ocen operatora (#11, W11, D12, D14)."""
import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from literaki_slownik.canonical import load_json
from tests.tematy_helpers import ROOT, package_fixture
from tests.test_check_tematy_package import AGENT, OPERATOR, SOURCE, checker, review_tool, write_review

SCRIPT = ROOT/'scripts/tematy_review.py'


class TematyReviewTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.f = package_fixture(cls.tmp.name)
        cls.root = Path(cls.f['root'])
        cls.review = write_review(cls.f, cls.root/'review.json', AGENT)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def run_script(self, *args):
        return subprocess.run([sys.executable, str(SCRIPT), *args, '--package-dir', str(self.f['package'])],
                              capture_output=True, text=True, cwd=ROOT)

    def operator_json(self, **changes):
        review = load_json(self.review)
        given = {'kind': review_tool.OPERATOR_KIND, 'schema_version': 1, 'temat': 'morze',
                 'sample_sha256': review['sample_sha256'], 'sha256sums_sha256': review['sha256sums_sha256'],
                 'agent_sha256': review['agent_sha256'], 'oceny': dict(OPERATOR)}
        given.update(changes)
        return given

    def test_page_refuses_without_agent_hash(self):
        review = load_json(self.review)
        del review['agent_sha256']
        unhashed = self.root/'no-hash.json'
        unhashed.write_text(json.dumps(review), encoding='utf-8')
        out = self.root/'no-hash.html'
        result = self.run_script('strona', '--review', str(unhashed), '--output', str(out))
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('hasha ocen agenta', result.stderr)
        self.assertFalse(out.exists())
        review = load_json(self.review)
        review['agent']['items'][0]['ocena'] = 'nie' if review['agent']['items'][0]['ocena'] != 'nie' else 'tak'
        changed = self.root/'changed.json'
        changed.write_text(json.dumps(review), encoding='utf-8')
        with self.assertRaises(checker.Refused):
            review_tool.page(self.f['package'], changed)

    def test_page_has_buttons_copy_textarea_and_no_agent_ratings(self):
        out = self.root/'r2.html'
        result = self.run_script('strona', '--review', str(self.review), '--output', str(out))
        self.assertEqual(result.returncode, 0, result.stderr)
        html = out.read_text(encoding='utf-8')
        self.assertNotIn('powód testowy', html)
        self.assertNotIn('"powod"', html)
        self.assertNotIn('"ocena"', html)
        self.assertNotIn('wieloznaczny', html)
        data = json.loads(re.search(r'<script id="data" type="application/json">(.*?)</script>', html, re.S).group(1))
        strata = load_json(self.f['package']/'reports/sample.json')['operator']['strata']
        # Warstwy strony z `sample.operator.strata` (#12 W7): tylko T2 i T3, T1 ocenia agent.
        self.assertEqual(list(strata), ['T2', 'T3'])
        self.assertEqual([i['key'] for i in data['items']], [key for name in strata for key in strata[name]])
        self.assertEqual({i['warstwa'] for i in data['items']}, {'T2', 'T3'})
        self.assertEqual(data['agent_sha256'], load_json(self.review)['agent_sha256'])
        self.assertEqual(set(data['items'][0]), {'key', 'lemat', 'warstwa', 'zrodla', 'znaczenie', 'formy', 'liczba_form'})
        for needle in ('Kopiuj JSON', '<textarea', "['tak', 'nie', 'niepewne']", 'name="viewport"',
                       'prefers-color-scheme: dark', 'padding: 0 16px'):
            self.assertIn(needle, html)
        self.assertRegex(html, r'<title>Ocena R2: morze</title>')
        uses = [m.start() for m in re.finditer('localStorage', html)]
        self.assertEqual(len(uses), 2)
        for at in uses:
            self.assertIn('try {', html[max(0, at - 60):at])
        self.assertNotRegex(html, r'(src|href)=["\']?https?:')
        self.assertNotIn('<link', html)

    def test_record_refuses_missing_foreign_key_and_wrong_agent_hash(self):
        missing = self.operator_json(oceny={k: v for k, v in OPERATOR.items() if not k.startswith('okręt')})
        foreign = self.operator_json(oceny={**OPERATOR, 'obcy@sgjp': 'tak'})
        layer_t1 = self.operator_json(oceny={**OPERATOR, 'reja@' + SOURCE: 'tak'})  # T1 spoza operator.strata
        wrong = self.operator_json(agent_sha256='0' * 64)
        for given, message in ((missing, 'Brak oceny'), (foreign, 'Obcy klucz'), (layer_t1, 'Obcy klucz'),
                               (wrong, 'hash ocen agenta')):
            with self.assertRaises(checker.Refused) as caught:
                review_tool.record(self.f['package'], self.review, given)
            self.assertIn(message, str(caught.exception))
        target = self.root/'record.json'
        target.write_bytes(self.review.read_bytes())
        path = self.root/'oceny.json'
        path.write_text(json.dumps(wrong), encoding='utf-8')
        before = target.read_bytes()
        result = self.run_script('zapisz', '--review', str(target), '--oceny', str(path))
        self.assertEqual(result.returncode, 4)
        self.assertEqual(target.read_bytes(), before)
        path.write_text(json.dumps(self.operator_json()), encoding='utf-8')
        result = self.run_script('zapisz', '--review', str(target), '--oceny', str(path))
        self.assertEqual(result.returncode, 0, result.stderr)
        saved = load_json(target)
        self.assertEqual([i['warstwa'] for i in saved['operator']['items']].count('T1'), 0)
        self.assertEqual(len(saved['operator']['items']), 5)
        report = checker.check(self.f['package'], self.f['manifest'], self.f['config'], target)
        self.assertEqual(report['przeglad']['zgodnosc']['kappa'], '2/7')
        again = self.run_script('zapisz', '--review', str(target), '--oceny', str(path))
        self.assertEqual(again.returncode, 4)
        self.assertIn('nie nadpisujemy', again.stderr)


if __name__ == '__main__':
    unittest.main()
