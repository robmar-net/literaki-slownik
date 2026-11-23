"""R6: harness „wznowiony = świeży” — każdy punkt przerwania, podwójne przerwanie i para pod verify."""
import sqlite3
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from literaki_slownik import build as build_module
from literaki_slownik.build import MARKED_REPORTS, build, resume
from literaki_slownik.canonical import load_json
from literaki_slownik.inputs import GeneratorError
from literaki_slownik.run import STAGES
from literaki_slownik.verify import verify
from tests.release_helpers import complete_run, fixture_inputs, make_review
from tests.test_resume import clean_identity, outputs


def boom(*args, **kwargs):
    raise sqlite3.OperationalError('disk I/O error')


def after(name):
    """Podstawiona funkcja: prawdziwa praca (z commitem), potem błąd I/O w środku etapu."""
    real = getattr(build_module, name)

    def wrapper(*args, **kwargs):
        real(*args, **kwargs)
        boom()
    return mock.patch.object(build_module, name, wrapper)


def nth_report(k):
    """Błąd przy k-tym raporcie: raporty 1..k-1 mają już znaczniki .done."""
    real, calls = build_module.marked_report, []

    def wrapper(ctx, name, compute):
        calls.append(name)
        if len(calls) == k:
            boom()
        return real(ctx, name, compute)
    return mock.patch.object(build_module, 'marked_report', wrapper)


# Jedna fikstura, punkty przez subTest: granice etapów, środek etapów, między raportami, po reports.
POINTS = (
    *((f'przed {stage}', lambda stage=stage: mock.patch.dict(build_module.STAGE_RUNNERS, {stage: boom}))
      for stage in STAGES),
    ('w import_sgjp', lambda: after('import_sgjp')),
    ('w import_kwjp', lambda: after('import_kwjp')),
    ('w constructions', lambda: after('materialize_confirmed_candidates')),
    ('w links', lambda: after('link_report')),
    *((f'raport {k}', lambda k=k: nth_report(k)) for k in range(1, len(MARKED_REPORTS) + 1)),
    ('po reports', lambda: mock.patch.object(build_module, 'canonical_index', boom)),
)


class ResumeEquivalenceTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.directory = Path(self.tmp.name)
        (self.directory / 'inputs').mkdir()
        # Ten sam katalog wejść dla świeżego i wznowionego: mtime gzip zmienia source_sha256.
        self.manifest = fixture_inputs(self.directory / 'inputs')
        self.enterContext(clean_identity())
        self.fresh = self.directory / 'swiezy'
        build(self.manifest, self.fresh)

    def interrupted(self, run, point):
        with point(), self.assertRaises(GeneratorError):
            build(self.manifest, run)

    def test_every_interruption_point_resumes_to_fresh_bytes(self):
        self.assertEqual(len(POINTS), len(STAGES) + 4 + len(MARKED_REPORTS) + 1)
        expected = outputs(self.fresh)
        for number, (label, point) in enumerate(POINTS):
            with self.subTest(label):
                run = self.directory / f'punkt-{number}'
                self.interrupted(run, point)
                resume(self.manifest, run)
                self.assertEqual(outputs(run), expected)
                manifest = load_json(run / 'manifest.json')
                self.assertEqual([a['outcome'] for a in manifest['build_attempts']], ['failed', 'complete'])
                self.assertEqual(manifest['resume'], {'resumed': True, 'count': 1})
                self.assertEqual({s['status'] for s in manifest['stages'].values()}, {'complete'})

    def test_double_interruption_and_second_resume_give_fresh_bytes(self):
        run = self.directory / 'podwojny'
        self.interrupted(run, lambda: after('materialize_confirmed_candidates'))
        with nth_report(3), self.assertRaises(GeneratorError):
            resume(self.manifest, run)
        result = resume(self.manifest, run)
        self.assertEqual(result['resumed_from'], 'reports')
        self.assertEqual(outputs(run), outputs(self.fresh))
        manifest = load_json(run / 'manifest.json')
        self.assertEqual([(a['first_stage'], a['outcome']) for a in manifest['build_attempts']],
                         [('preflight', 'failed'), ('constructions', 'failed'), ('reports', 'complete')])
        self.assertEqual(manifest['resume'], {'resumed': True, 'count': 2})

    def test_resumed_and_fresh_pair_passes_verify(self):
        run = self.directory / 'wznowiony'
        self.interrupted(run, lambda: after('link_report'))
        resume(self.manifest, run)
        complete_run(run)
        complete_run(self.fresh)
        review = make_review(run, self.directory / 'review.json')
        report = verify(run, self.fresh, review, allow_test_fixture=True)
        self.assertEqual(report['verdict'], 'VERIFIED', report['checks'])


if __name__ == '__main__':
    unittest.main()
