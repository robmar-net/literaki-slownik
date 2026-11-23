"""R5: `build --resume` — kolejność kontroli, krok 12, restart preflight, reset etapów i CLI."""
import contextlib
import io
import json
import os
import shutil
import sqlite3
import subprocess
import sys
import tempfile
import types
import unittest
from pathlib import Path
from unittest import mock

from literaki_slownik import build as build_module
from literaki_slownik import cli
from literaki_slownik import run as run_module
from literaki_slownik import volume
from literaki_slownik.build import build, reset_stage, resume
from literaki_slownik.canonical import load_json, write_json
from literaki_slownik.database import connect
from literaki_slownik.decisions import USE_REVIEW_ID
from literaki_slownik.inputs import GeneratorError
from literaki_slownik.run import STAGES, code_identity
from tests.layout_helpers import GB, LayoutCase
from tests.release_helpers import fixture_inputs

ROOT = Path(__file__).resolve().parents[1]
CLEAN = dict(code_identity(), git_dirty=False)
# Proces potomny: twarde przerwanie (os._exit) w środku import_kwjp, po zapisie wierszy.
CRASH = '''
import os, sys
from unittest import mock
from literaki_slownik import build as b
real = b.import_kwjp
def crash(*args, **kwargs):
    real(*args, **kwargs)
    os._exit(9)
with mock.patch.object(b, 'import_kwjp', crash):
    b.build(sys.argv[1], sys.argv[2])
'''
DERIVED = ('variant_decision', 'decision_payload', 'analysis', 'derivation_component', 'derivation_candidate')
SGJP_TABLES = ('interpretation', 'lexeme', 'surface_form', 'sgjp_record')


def clean_identity():
    """Kod bez niezatwierdzonych zmian: drzewo robocze implementera bywa dirty."""
    stack = contextlib.ExitStack()
    for module in (run_module, build_module):
        stack.enter_context(mock.patch.object(module, 'code_identity', lambda: dict(CLEAN)))
    return stack


def outputs(run):
    run = Path(run)
    found = {name: (run / 'reports' / name).read_bytes() for name in ('canonical-index.json', 'logical-content.json')}
    found.update({p.name: p.read_bytes() for p in sorted((run / 'lists').glob('*.txt'))})
    return found


def boom(*args, **kwargs):
    raise sqlite3.OperationalError('disk I/O error')


class ResumeChecksTests(LayoutCase):
    def setUp(self):
        super().setUp()
        self.enterContext(clean_identity())
        build(self.manifest, self.work / 'wzor', work_root=self.data)

    def copy(self, name):
        shutil.copytree(self.data / 'wzor', self.data / name)
        os.symlink(self.data / name, self.work / name)
        return self.work / name

    def edit(self, run, **fields):
        manifest = load_json(run / 'manifest.json')
        manifest.update(fields)
        write_json(run / 'manifest.json', manifest)

    def test_resume_through_the_t7_path_is_refused_before_the_lock(self):
        # N4: blokada leży obok podanej ścieżki; wznowienie przez ścieżkę T7 omija blokadę nadzorcy z data/work.
        self.copy('przez-t7')
        with self.assertRaises(GeneratorError) as caught:
            resume(self.manifest, self.data / 'przez-t7')
        self.assertEqual(caught.exception.code, 4)
        self.assertIn('data/work', str(caught.exception))
        self.assertFalse(os.path.lexists(self.data / '.przez-t7.build.lock'))
        self.assertEqual(len(load_json(self.data / 'przez-t7' / 'manifest.json')['build_attempts']), 1)

    def test_each_check_refuses_with_its_code_in_spec_order(self):
        other = load_json(self.manifest)
        other['unavailable'][0]['reason'] = 'INNY'
        changed = self.manifest.parent / 'sources-inny.json'
        changed.write_text(json.dumps(other), encoding='utf-8')
        marker = self.data / volume.MARKER
        small = lambda path: types.SimpleNamespace(f_bavail=10 * GB, f_frsize=1)

        def dangling(run):
            os.rename(self.data / run.name, self.data / (run.name + '-gdzie-indziej'))

        def corrupt_db(run):
            with open(run / 'build.sqlite', 'r+b') as stream:
                stream.write(b'to nie jest baza' * 8)

        cases = (
            ('brak przebiegu', None, lambda run: None, contextlib.nullcontext, self.manifest, 4),
            ('wiszący symlink', 'wiszacy', dangling, contextlib.nullcontext, self.manifest, 75),
            ('G1', 'g1', lambda run: self.mounts.discard(str(self.data)), contextlib.nullcontext, self.manifest, 75),
            ('nieczytelny manifest', 'manifest', lambda run: (run / 'manifest.json').write_text('{', encoding='utf-8'),
             contextlib.nullcontext, self.manifest, 4),
            ('VERIFIED', 'verified', lambda run: self.edit(run, readiness='VERIFIED'), contextlib.nullcontext,
             self.manifest, 5),
            ('G2', 'g2', lambda run: write_json(marker, {'schema_version': 1, 'marker_id': 'inny', 'volume_uuid': 'X'}),
             contextlib.nullcontext, self.manifest, 76),
            ('miejsce', 'miejsce', lambda run: None, lambda: mock.patch('os.statvfs', small), self.manifest, 78),
            ('kod', 'kod', lambda run: None,
             lambda: mock.patch.object(run_module, 'code_identity', lambda: dict(CLEAN, tree_sha256='0' * 64)),
             self.manifest, 4),
            ('wejścia', 'wejscia', lambda run: None, contextlib.nullcontext, changed, 3),
            ('quick_check', 'quick', corrupt_db, contextlib.nullcontext, self.manifest, 77),
        )
        original_marker = marker.read_bytes()
        for label, name, damage, context, manifest, code in cases:
            with self.subTest(label):
                run = self.copy(name) if name else self.work / 'brak'
                damage(run)
                try:
                    with context(), self.assertRaises(GeneratorError) as caught:
                        resume(manifest, run)
                finally:
                    self.mounts.add(str(self.data))
                    marker.write_bytes(original_marker)
                self.assertEqual(caught.exception.code, code, str(caught.exception))
                if name and code not in (4, 75):
                    # Odmowa przed krokiem 12 nie dopisuje próby.
                    self.assertEqual(len(load_json(run / 'manifest.json')['build_attempts']), 1)
        # Po zdrowych kontrolach wznowienie na wolumenie zostawia symlink i marker_id.
        run = self.copy('wznowiony')
        manifest = load_json(run / 'manifest.json')
        manifest['stages']['links'] = {'status': 'running', 'updated': 'awaria'}
        manifest['build_attempts'][0].update(ended=None, outcome=None, exit_code=None)
        write_json(run / 'manifest.json', manifest)
        result = resume(self.manifest, run)
        self.assertEqual(result['resumed_from'], 'links')
        self.assertTrue(os.path.islink(run))
        manifest = load_json(run / 'manifest.json')
        self.assertEqual(manifest['work_volume'], {'marker_id': 'm-data'})
        self.assertEqual(manifest['resume'], {'resumed': True, 'count': 1})


class ResumeFlowTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.directory = Path(self.tmp.name)
        (self.directory / 'inputs').mkdir()
        self.manifest = fixture_inputs(self.directory / 'inputs')
        self.enterContext(clean_identity())

    def test_hard_crash_in_child_leaves_running_and_resume_marks_failed_and_interrupted(self):
        fresh = self.directory / 'swiezy'
        build(self.manifest, fresh)
        run = self.directory / 'awaria'
        child = subprocess.run([sys.executable, '-c', CRASH, str(self.manifest), str(run)], cwd=ROOT,
                               capture_output=True, text=True)
        self.assertEqual(child.returncode, 9, child.stderr)
        before = load_json(run / 'manifest.json')
        self.assertEqual(before['stages']['import_kwjp']['status'], 'running')
        self.assertIsNone(before['build_attempts'][0]['ended'])
        seen = {}
        real = build_module.run_build

        def spying(ctx, first):
            seen['stages'] = load_json(ctx['run'] / 'manifest.json')['stages']
            return real(ctx, first)

        with mock.patch.object(build_module, 'run_build', spying):
            result = resume(self.manifest, run)
        self.assertEqual(seen['stages']['import_kwjp']['status'], 'failed')
        self.assertEqual(result['resumed_from'], 'import_kwjp')
        manifest = load_json(run / 'manifest.json')
        first, second = manifest['build_attempts']
        self.assertEqual((first['outcome'], first['last_stage'], first['exit_code']),
                         ('interrupted', 'import_kwjp', None))
        self.assertEqual((second['attempt'], second['first_stage'], second['outcome'], second['exit_code']),
                         (2, 'import_kwjp', 'complete', 0))
        self.assertEqual(manifest['resume'], {'resumed': True, 'count': 1})
        self.assertEqual(outputs(run), outputs(fresh))

    def test_unfinished_preflight_restarts_the_run_in_place(self):
        fresh = self.directory / 'swiezy'
        build(self.manifest, fresh)

        def missing_source(run):
            with connect(run / 'build.sqlite') as db:
                db.execute("delete from source_artifact where source_id='corpus'")

        for label, damage in (('preflight przerwany', None), ('niepełny source_artifact', missing_source)):
            with self.subTest(label):
                run = self.directory / label.replace(' ', '-')
                if damage is None:
                    with mock.patch.dict(build_module.STAGE_RUNNERS, {'preflight': boom}):
                        with self.assertRaises(GeneratorError):
                            build(self.manifest, run)
                else:
                    with mock.patch.dict(build_module.STAGE_RUNNERS, {'import_sgjp': boom}):
                        with self.assertRaises(GeneratorError):
                            build(self.manifest, run)
                    damage(run)
                (run / 'reports/resztka.json').write_text('{}', encoding='utf-8')
                (run / 'lists').mkdir(exist_ok=True)
                (run / 'lists/resztka.txt').write_text('x\n', encoding='utf-8')
                result = resume(self.manifest, run)
                self.assertEqual(result['resumed_from'], 'preflight')
                self.assertFalse((run / 'reports/resztka.json').exists())
                self.assertFalse((run / 'lists/resztka.txt').exists())
                self.assertEqual(outputs(run), outputs(fresh))

    def test_reset_follows_the_table_per_first_stage(self):
        run = self.directory / 'pelny'
        build(self.manifest, run)
        tables = (*DERIVED, *SGJP_TABLES, 'corpus_evidence')
        expected_empty = {'import_sgjp': set(tables), 'import_kwjp': {*DERIVED, 'corpus_evidence'}}
        with connect(run / 'build.sqlite', readonly=True) as db:
            baseline = {t for t in tables if db.execute(f'select count(*) from {t}').fetchone()[0] == 0}
        self.assertFalse(baseline & {*SGJP_TABLES, 'corpus_evidence', 'analysis', 'variant_decision'})
        for first in STAGES:
            with self.subTest(first):
                copy = self.directory / f'baza-{first}.sqlite'
                shutil.copy(run / 'build.sqlite', copy)
                with connect(copy) as db:
                    db.execute("insert into source_artifact values (?,'own_documentary_review','{}')",
                               (USE_REVIEW_ID,))
                    db.commit()
                    reset_stage(db, first)
                    self.assertFalse(db.in_transaction)
                with connect(copy, readonly=True) as db:
                    names = {r[0] for r in db.execute("select name from sqlite_master where type='table'")}
                    counts = {t: db.execute(f'select count(*) from {t}').fetchone()[0] for t in tables}
                    review = db.execute('select count(*) from source_artifact where source_id=?',
                                        (USE_REVIEW_ID,)).fetchone()[0]
                    sources = db.execute('select count(*) from source_artifact where source_id!=?',
                                         (USE_REVIEW_ID,)).fetchone()[0]
                empty = expected_empty.get(first, set()) | baseline
                self.assertEqual({t for t, n in counts.items() if n == 0}, empty)
                self.assertEqual(sources, 2)
                self.assertEqual(review, 0 if first in expected_empty else 1)
                dropped = first not in ('preflight', 'reports')
                self.assertEqual({'evidence_link', 'evidence_candidate'} & names,
                                 set() if dropped else {'evidence_link', 'evidence_candidate'})
        # reports/.done znika, gdy w tej próbie wykonał się etap przed reports.
        for first, kept in (('links', False), ('reports', True)):
            with self.subTest(first):
                run = self.directory / ('done-' + first)
                with mock.patch.dict(build_module.STAGE_RUNNERS, {first: boom}):
                    with self.assertRaises(GeneratorError):
                        build(self.manifest, run)
                (run / 'reports/.done').mkdir(exist_ok=True)
                (run / 'reports/.done/obcy.json').write_text('{}', encoding='utf-8')
                resume(self.manifest, run)
                self.assertEqual((run / 'reports/.done/obcy.json').exists(), kept)

    def test_cli_build_resume_returns_json_and_codes(self):
        run = self.directory / 'cli'
        with mock.patch.dict(build_module.STAGE_RUNNERS, {'decisions': boom}):
            with self.assertRaises(GeneratorError):
                build(self.manifest, run)

        def call(*argv):
            out, err = io.StringIO(), io.StringIO()
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                code = cli.main(list(argv))
            return code, out.getvalue()

        code, out = call('build', '--resume', '--manifest', str(self.manifest), '--run-dir', str(run), '--json')
        self.assertEqual(code, 0, out)
        found = json.loads(out)['result']
        self.assertEqual((found['resumed_from'], found['pending']), ('decisions', []))
        code, _ = call('build', '--resume', '--manifest', str(self.manifest), '--run-dir',
                       str(self.directory / 'nie-ma'), '--json')
        self.assertEqual(code, 4)
        code, _ = call('build', '--resume', '--manifest', str(self.manifest), '--run-dir', str(run),
                       '--work-root', str(self.directory), '--json')
        self.assertEqual(code, 2)


class BuildLockTests(LayoutCase):
    """Blokada przebiegu `data/work/.<nazwa>.build.lock`: drugi build albo --resume → 4, zanim coś zmieni."""

    def setUp(self):
        super().setUp()
        self.enterContext(clean_identity())

    def hold(self, name):
        import fcntl
        lock = open(self.work / f'.{name}.build.lock', 'a')
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        self.addCleanup(lock.close)
        return lock

    def code(self, function, *args, **kwargs):
        with self.assertRaises(GeneratorError) as caught:
            function(*args, **kwargs)
        return caught.exception.code

    def test_held_lock_refuses_fresh_build_and_resume_before_any_change(self):
        lock = self.hold('nowy')
        self.assertEqual(self.code(build, self.manifest, self.work / 'nowy', work_root=self.data), 4)
        self.assertFalse(os.path.lexists(self.work / 'nowy'))
        self.assertFalse(os.path.lexists(self.data / 'nowy'))
        lock.close()
        build(self.manifest, self.work / 'nowy', work_root=self.data)
        manifest = load_json(self.work / 'nowy' / 'manifest.json')
        manifest['stages']['reports'] = {'status': 'running'}
        write_json(self.work / 'nowy' / 'manifest.json', manifest)
        before = {path.name: path.read_bytes() for path in (self.data / 'nowy').iterdir() if path.is_file()}
        self.hold('nowy')
        self.assertEqual(self.code(resume, self.manifest, self.work / 'nowy'), 4)
        after = {path.name: path.read_bytes() for path in (self.data / 'nowy').iterdir() if path.is_file()}
        self.assertEqual(after, before)

    def test_lock_is_held_during_the_build_and_released_after(self):
        from literaki_slownik import workfs
        seen = []
        real = build_module.STAGE_RUNNERS['links']

        def links(db, ctx):
            seen.append(workfs.lock_held(self.work / '.trwa.build.lock'))
            return real(db, ctx)
        with mock.patch.dict(build_module.STAGE_RUNNERS, {'links': links}):
            build(self.manifest, self.work / 'trwa', work_root=self.data)
        self.assertEqual(seen, [True])
        self.assertFalse(workfs.lock_held(self.work / '.trwa.build.lock'))


if __name__ == '__main__':
    unittest.main()
