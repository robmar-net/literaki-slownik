import json
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from literaki_slownik.build import build
from literaki_slownik.canonical import load_json, write_json
from literaki_slownik.inputs import GeneratorError
from literaki_slownik.verify import verify, KS
from tests.release_helpers import (complete_pair, complete_run, fixture_inputs, make_review,
                                   repin_release, tree_hashes)


def reasons(report, k):
    return ' | '.join(r['message'] for r in report['checks'][k]['reasons'])


class VerifyTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.directory = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def test_complete_fixture_pair_verified_with_candidate_prepared_before_verdict(self):
        _, run, peer, review = complete_pair(self.directory)
        report = verify(run, peer, review, allow_test_fixture=True)
        self.assertEqual(report['verdict'], 'VERIFIED', json.dumps(report['checks'], ensure_ascii=False))
        self.assertEqual(set(report['checks']), set(KS))
        manifest = load_json(run / 'manifest.json')
        self.assertEqual(manifest['readiness'], 'VERIFIED')
        self.assertTrue(manifest['verification']['fixture'])
        attempt = run / manifest['verification']['attempt']
        plan = load_json(attempt / 'package-plan.json')
        # I1: plan pakietu ma oznaczenie INCOMPLETE i powstaje przed werdyktem.
        self.assertEqual(plan['status'], 'INCOMPLETE')
        self.assertIn('LL-PL-BROAD.txt', plan['files'])
        self.assertIn('ATTRIBUTIONS.md', plan['files'])
        self.assertIn('LIMITATIONS.md', plan['files'])
        self.assertIn('TERMS.md', plan['files'])
        self.assertEqual((attempt / 'candidate/LL-PL-STANDARD.txt').read_bytes(), b'kot\nzamek\n')
        self.assertEqual(load_json(attempt / 'verification.json')['verdict'], 'VERIFIED')

    def test_incomplete_build_refused_with_reason_per_k_and_files_preserved(self):
        manifest = fixture_inputs(self.directory)
        run, peer = self.directory / 'a', self.directory / 'b'
        build(manifest, run)
        build(manifest, peer)
        before = tree_hashes(run)
        report = verify(run, peer, self.directory / 'brak-review.json', allow_test_fixture=True)
        self.assertEqual(report['verdict'], 'REFUSED')
        for k in KS:
            self.assertEqual(report['checks'][k]['status'], 'fail', k)
            self.assertTrue(report['checks'][k]['reasons'], k)
        self.assertIn('constructions', reasons(report, 'K4'))
        self.assertIn('pending', reasons(report, 'K4'))
        self.assertIn('links', reasons(report, 'K6'))
        self.assertIn('lists/broad.txt', reasons(report, 'K3'))
        self.assertIn('przegląd', reasons(report, 'K9'))
        self.assertEqual(load_json(run / 'manifest.json')['readiness'], 'INCOMPLETE')
        self.assertEqual(before, tree_hashes(run, skip=('verification',)))
        attempt = run / report['attempt']
        self.assertEqual(load_json(attempt / 'package-plan.json')['status'], 'INCOMPLETE')

    def test_public_cli_refuses_fixture_even_when_complete(self):
        _, run, peer, review = complete_pair(self.directory)
        cmd = [sys.executable, '-m', 'literaki_slownik', 'verify', '--run-dir', str(run),
               '--peer-run', str(peer), '--review', str(review), '--json']
        result = subprocess.run(cmd, capture_output=True, text=True)
        self.assertEqual(result.returncode, 5, result.stdout + result.stderr)
        output = json.loads(result.stdout)
        self.assertEqual(output['status'], 'refused')
        self.assertIn('fikstur', reasons(output['result'], 'K1'))
        self.assertTrue(result.stderr)
        self.assertEqual(load_json(run / 'manifest.json')['readiness'], 'INCOMPLETE')

    def test_changed_inputs_and_tampered_files_refused(self):
        manifest, run, peer, review = complete_pair(self.directory)
        (manifest.parent / 'lemma.csv.gz').write_bytes(b'zmienione')
        (run / 'reports/decisions.json').write_text('{"schema_version":1}\n', encoding='utf-8')
        report = verify(run, peer, review, allow_test_fixture=True)
        self.assertEqual(report['verdict'], 'REFUSED')
        self.assertIn('SHA256', reasons(report, 'K1'))
        self.assertIn('reports/decisions.json', reasons(report, 'K8'))

    def test_changed_or_dirty_code_refused(self):
        _, run, peer, review = complete_pair(self.directory)
        manifest = load_json(run / 'manifest.json')
        manifest['code']['tree_sha256'] = '0' * 64
        write_json(run / 'manifest.json', manifest)
        report = verify(run, peer, review, allow_test_fixture=True)
        self.assertIn('kod', reasons(report, 'K8'))
        manifest['code'] = dict(load_json(peer / 'manifest.json')['code'], git_dirty=True)
        write_json(run / 'manifest.json', manifest)
        report = verify(run, peer, review, allow_test_fixture=True)
        self.assertIn('dirty', reasons(report, 'K8'))
        self.assertEqual(load_json(run / 'manifest.json')['readiness'], 'INCOMPLETE')

    def test_inconsistent_database_refused(self):
        _, run, peer, review = complete_pair(self.directory)
        db = sqlite3.connect(run / 'build.sqlite')
        db.execute("update variant_decision set membership_status='reject' where variant='broad'")
        db.commit()
        db.close()
        report = verify(run, peer, review, allow_test_fixture=True)
        self.assertEqual(report['verdict'], 'REFUSED')
        self.assertIn('broad', reasons(report, 'K3'))
        self.assertIn('logical-content', reasons(report, 'K8'))

    def test_peer_differing_only_in_time_and_log_accepted_but_content_refused(self):
        _, run, peer, review = complete_pair(self.directory)
        manifest = load_json(peer / 'manifest.json')
        manifest['created'] = '1999-01-01T00:00:00+00:00'
        write_json(peer / 'manifest.json', manifest)
        write_json(peer / 'reports/performance.json', {'peak_rss': {'value': 1}})
        (peer / 'events.log').write_text('inny log\n', encoding='utf-8')
        self.assertEqual(verify(run, peer, review, allow_test_fixture=True)['verdict'], 'VERIFIED')
        (self.directory / 'x').mkdir()
        _, run2, peer2, review2 = complete_pair(self.directory / 'x')
        (peer2 / 'lists/standard.txt').write_bytes(b'kot\n')
        from literaki_slownik.reports import canonical_index
        write_json(peer2 / 'reports/canonical-index.json', canonical_index(peer2))
        report = verify(run2, peer2, review2, allow_test_fixture=True)
        self.assertEqual(report['verdict'], 'REFUSED')
        self.assertIn('lists/standard.txt', reasons(report, 'K8'))

    def test_peer_must_be_independent_run(self):
        _, run, _, review = complete_pair(self.directory)
        from literaki_slownik import reports
        walked = []
        original = reports.logical_content_report
        with patch.object(reports, 'logical_content_report', lambda db: walked.append(1) or original(db)):
            report = verify(run, run, review, allow_test_fixture=True)
        self.assertIn('niezależn', report['checks']['K8']['reasons'][0]['message'])
        # Ten sam katalog to jedno przejście bazy, nie dwa.
        self.assertEqual(walked, [1])

    def test_incomplete_run_refused_without_walking_database(self):
        manifest = fixture_inputs(self.directory)
        run, peer = self.directory / 'a', self.directory / 'b'
        build(manifest, run)
        build(manifest, peer)
        from literaki_slownik import reports

        def no_walk(db):
            raise AssertionError('przejście bazy nieukończonego przebiegu')

        with patch.object(reports, 'logical_content_report', no_walk):
            report = verify(run, run, self.directory / 'brak.json', allow_test_fixture=True)
        self.assertEqual(report['verdict'], 'REFUSED')
        self.assertIn('niezależn', reasons(report, 'K8'))
        self.assertIn('Pominięto integrity_check', ' '.join(report['checks']['K8']['evidence']))

    def test_review_must_be_bound_by_hashes_and_complete(self):
        _, run, peer, review = complete_pair(self.directory)
        data = load_json(review)
        data['canonical_index_sha256'] = 'f' * 64
        review.write_text(json.dumps(data), encoding='utf-8')
        self.assertIn('hash', reasons(verify(run, peer, review, allow_test_fixture=True), 'K9'))
        make_review(run, review, drop_item=True)
        self.assertIn('pozycj', reasons(verify(run, peer, review, allow_test_fixture=True), 'K9'))
        make_review(run, review, assessment='incorrect', blocking=True)
        report = verify(run, peer, review, allow_test_fixture=True)
        self.assertIn('blokuj', reasons(report, 'K9'))
        data = load_json(make_review(run, review))
        data['explain_runtime'] = data['explain_runtime'][1:]
        data['explain_runtime'][0]['result_sha256'] = '0' * 64
        review.write_text(json.dumps(data), encoding='utf-8')
        text = reasons(verify(run, peer, review, allow_test_fixture=True), 'K7')
        self.assertIn('kategorii: accept', text)
        # Osobno od braku kategorii: zmieniony wynik explain dla obecnej pozycji.
        self.assertIn('explain dla reject (kotek) różni się', text)

    def test_unknown_unresolved_refused_documented_no_impact_accepted(self):
        _, run, peer, review = complete_pair(self.directory)
        rule = {'variant': 'standard', 'layer': 'language', 'rule_id': 'nieznana-v1', 'analyses': 1,
                'word_keys': 1, 'analyses_with_rejected_membership': 1,
                'word_keys_by_membership': {'accept': 0, 'reject': 1, 'unresolved': 0}}
        for target in (run, peer):
            data = load_json(target / 'reports/unresolved.json')
            data['rules'] = [rule]
            write_json(target / 'reports/unresolved.json', data)
            from literaki_slownik.reports import canonical_index
            write_json(target / 'reports/canonical-index.json', canonical_index(target))
        make_review(run, review)
        report = verify(run, peer, review, allow_test_fixture=True)
        self.assertIn('nieznana-v1', reasons(report, 'K5'))
        affecting = dict(rule, word_keys_by_membership={'accept': 0, 'reject': 0, 'unresolved': 1})
        data = load_json(run / 'reports/unresolved.json')
        data['rules'] = [affecting]
        write_json(run / 'reports/unresolved.json', data)
        self.assertIn('zmienia', reasons(verify(run, peer, review, allow_test_fixture=True), 'K5'))

    def test_documented_known_limitation_accepted(self):
        (self.directory / 'inputs').mkdir()
        evidence = self.directory / 'inputs' / 'dowod.md'
        evidence.write_text('Brak wpływu: wszystkie analizy odrzucone innym warunkiem.\n', encoding='utf-8')
        import hashlib
        known = [{'variant': 'standard', 'layer': 'language', 'rule_id': 'znana-v1',
                  'description': 'opisane ograniczenie',
                  'no_impact_evidence': {'path': 'dowod.md',
                                         'sha256': hashlib.sha256(evidence.read_bytes()).hexdigest()}}]
        manifest = fixture_inputs(self.directory / 'inputs', known=known)
        run, peer = self.directory / 'a', self.directory / 'b'
        rule = {'variant': 'standard', 'layer': 'language', 'rule_id': 'znana-v1', 'analyses': 1,
                'word_keys': 1, 'analyses_with_rejected_membership': 1,
                'word_keys_by_membership': {'accept': 0, 'reject': 1, 'unresolved': 0}}
        from literaki_slownik.reports import canonical_index
        for target in (run, peer):
            build(manifest, target)
            complete_run(target)
            data = load_json(target / 'reports/unresolved.json')
            data['rules'] = [rule]
            write_json(target / 'reports/unresolved.json', data)
            write_json(target / 'reports/canonical-index.json', canonical_index(target))
        review = make_review(run, self.directory / 'review.json')
        report = verify(run, peer, review, allow_test_fixture=True)
        self.assertEqual(report['checks']['K5']['status'], 'pass', reasons(report, 'K5'))
        self.assertIn('znana-v1', (run / report['attempt'] / 'candidate/LIMITATIONS.md').read_text(encoding='utf-8'))

    def test_release_conditions_pending_owner_decision_refused(self):
        (self.directory / 'inputs').mkdir()
        manifest = fixture_inputs(self.directory / 'inputs', lists_status='PENDING_OWNER_DECISION')
        run, peer = self.directory / 'a', self.directory / 'b'
        for target in (run, peer):
            build(manifest, target)
            complete_run(target)
        review = make_review(run, self.directory / 'review.json')
        report = verify(run, peer, review, allow_test_fixture=True)
        self.assertEqual(report['verdict'], 'REFUSED')
        self.assertIn('lists', reasons(report, 'K10'))
        self.assertIn('właściciel', reasons(report, 'K10'))
        self.assertEqual([k for k in KS if report['checks'][k]['status'] == 'fail'], ['K10'])

    def test_missing_release_conditions_refused(self):
        _, run, peer, review = complete_pair(self.directory)
        manifest = load_json(run / 'manifest.json')
        del manifest['inputs']['manifest']['configurations']['release']
        write_json(run / 'manifest.json', manifest)
        self.assertIn('warunk', reasons(verify(run, peer, review, allow_test_fixture=True), 'K10'))

    def test_each_k_has_independent_refusal(self):
        breakers = {
            'K1': lambda run: self.edit_manifest(run, lambda m: m['stages'].update(preflight={'status': 'failed'})),
            'K2': lambda run: write_json(run / 'reports/import-counts.json', {}),
            'K3': lambda run: (run / 'lists/standard.txt').write_bytes(b'kot\nkotek\nzamek\nzzz\n'),
            'K4': lambda run: self.edit_report(run, 'coverage.json', full_qualification_pending=True),
            'K5': lambda run: self.edit_report(run, 'unresolved.json', full_qualification_pending=True),
            'K6': lambda run: self.edit_report(run, 'links.json', stage_completion={'complete': False, 'blocking': ['x']}),
            'K7': lambda run: None,
            'K8': lambda run: self.edit_manifest(run, lambda m: m.pop('code')),
            'K9': lambda run: self.edit_report(run, 'filter-impact.json', full_qualification_pending=True),
            'K10': lambda run: self.edit_manifest(run, lambda m: m['inputs']['manifest']['configurations'].pop('release')),
        }
        for index, (k, breaker) in enumerate(breakers.items()):
            with self.subTest(k=k):
                directory = self.directory / str(index)
                directory.mkdir()
                _, run, peer, review = complete_pair(directory)
                breaker(run)
                if k == 'K7':
                    data = load_json(review)
                    data['explain_runtime'] = []
                    review.write_text(json.dumps(data), encoding='utf-8')
                report = verify(run, peer, review, allow_test_fixture=True)
                self.assertEqual(report['verdict'], 'REFUSED')
                self.assertEqual(report['checks'][k]['status'], 'fail', k)

    def test_directory_without_run_manifest_refused_without_writes(self):
        target = self.directory / 'tylko-baza'
        target.mkdir()
        (target / 'build.sqlite').write_bytes(b'')
        with self.assertRaises(GeneratorError) as raised:
            verify(target, target, self.directory / 'review.json')
        self.assertEqual(raised.exception.code, 5)
        self.assertEqual(sorted(p.name for p in target.iterdir()), ['build.sqlite'])

    def test_verified_run_not_verified_again(self):
        _, run, peer, review = complete_pair(self.directory)
        self.assertEqual(verify(run, peer, review, allow_test_fixture=True)['verdict'], 'VERIFIED')
        with self.assertRaises(GeneratorError) as raised:
            verify(run, peer, review, allow_test_fixture=True)
        self.assertEqual(raised.exception.code, 5)

    def edit_manifest(self, run, change):
        manifest = load_json(run / 'manifest.json')
        change(manifest)
        write_json(run / 'manifest.json', manifest)

    def edit_report(self, run, name, **values):
        from literaki_slownik.reports import canonical_index
        data = load_json(run / 'reports' / name)
        data.update(values)
        write_json(run / 'reports' / name, data)
        write_json(run / 'reports/canonical-index.json', canonical_index(run))


if __name__ == '__main__':
    unittest.main()
