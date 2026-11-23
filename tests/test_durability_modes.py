"""R8: PRAGMA zapisywalnej bazy i tryb `fullfsync` buildu (ADR-020)."""
import os
import re
import sqlite3
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from literaki_slownik import build as build_module
from literaki_slownik import canonical
from literaki_slownik import database
from literaki_slownik.build import build, reset_stage
from literaki_slownik.database import connect
from literaki_slownik.run import STAGES, set_stage as real_set_stage
from tests.release_helpers import fixture_inputs


def pragma(db, name):
    return db.execute(f'PRAGMA {name}').fetchone()[0]


class DurabilityModeTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.directory = Path(self.tmp.name)
        (self.directory / 'inputs').mkdir()
        self.manifest = fixture_inputs(self.directory / 'inputs')
        self.run = self.directory / 'run'

    def tearDown(self):
        self.tmp.cleanup()

    def observed_build(self, mode):
        """Build w trybie mode; zapis PRAGMA w etapie i na granicy oraz kolejności zdarzeń."""
        seen, events = {}, []
        real_runners, real_sync = dict(build_module.STAGE_RUNNERS), database.full_sync
        real_durable = build_module.stage_durable
        real_write_json, real_write_bytes = build_module.write_json, build_module.write_bytes

        def runner(stage):
            def observed(db, ctx):
                seen[(stage, 'stage')] = (pragma(db, 'fullfsync'), pragma(db, 'checkpoint_fullfsync'))
                return real_runners[stage](db, ctx)
            return observed

        def durable(db):
            real_durable(db)
            seen[(build_module_stage[0], 'boundary')] = (pragma(db, 'fullfsync'), pragma(db, 'synchronous'),
                                                         pragma(db, 'journal_mode'))

        build_module_stage = [None]

        def recording_set_stage(path, stage, status, details=None):
            build_module_stage[0] = stage
            events.append(('stage', stage, status))
            return real_set_stage(path, stage, status, details)

        def sync(db):
            events.append(('sync', build_module_stage[0]))
            return real_sync(db)

        def write_json(path, value):
            events.append(('file', build_module_stage[0], Path(path).name))
            return real_write_json(path, value)

        def write_bytes(path, data):
            events.append(('file', build_module_stage[0], Path(path).name))
            return real_write_bytes(path, data)

        with patch.object(database, 'FULLFSYNC_MODE', mode), \
                patch.dict(build_module.STAGE_RUNNERS, {stage: runner(stage) for stage in STAGES}), \
                patch.object(build_module, 'stage_durable', durable), \
                patch.object(build_module, 'set_stage', recording_set_stage), \
                patch.object(database, 'full_sync', sync), \
                patch.object(build_module, 'write_json', write_json), \
                patch.object(build_module, 'write_bytes', write_bytes):
            build(self.manifest, self.run)
        return seen, events

    def test_writable_connect_sets_delete_journal_and_full_sync_readonly_untouched(self):
        path = self.directory / 'b.sqlite'
        statements = []
        real_connect = sqlite3.connect

        def traced(*args, **kwargs):
            db = real_connect(*args, **kwargs)
            db.set_trace_callback(statements.append)
            return db

        setting = re.compile(r'(journal_mode|synchronous|fullfsync)\s*=', re.I)
        with patch.object(database.sqlite3, 'connect', traced):
            with connect(path, create=True) as db:
                self.assertEqual((pragma(db, 'journal_mode'), pragma(db, 'synchronous')), ('delete', 2))
                self.assertEqual(pragma(db, 'fullfsync'), 0)  # tylko build włącza fullfsync
            self.assertEqual([sql for sql in statements if setting.search(sql)],
                             ['PRAGMA journal_mode=DELETE', 'PRAGMA synchronous=FULL'])
            statements.clear()
            with connect(path, readonly=True) as db:
                self.assertEqual(pragma(db, 'fullfsync'), 0)
        self.assertTrue(statements)
        self.assertFalse([sql for sql in statements if setting.search(sql)])  # czytelnik bez zmian

    def test_build_mode_keeps_fullfsync_on_in_stage_and_at_boundary(self):
        seen, events = self.observed_build('build')
        for stage in STAGES:
            self.assertEqual(seen[(stage, 'stage')], (1, 1), stage)
            self.assertEqual(seen[(stage, 'boundary')], (1, 2, 'delete'), stage)
        self.assertFalse([event for event in events if event[0] == 'sync'])  # commit sam robi F_FULLFSYNC

    def test_stage_boundaries_mode_syncs_database_before_stage_files_and_manifest(self):
        seen, events = self.observed_build('stage_boundaries')
        for stage in STAGES:
            self.assertEqual(seen[(stage, 'stage')], (0, 0), stage)
            self.assertEqual(seen[(stage, 'boundary')], (0, 2, 'delete'), stage)
            segment = [event for event in events if event[1] == stage]
            segment = segment[:max(i for i, event in enumerate(segment) if event[0] == 'stage') + 1]
            self.assertEqual(segment[0], ('stage', stage, 'running'))
            self.assertIn(segment[-1][2], ('complete', 'pending'), stage)
            kinds = [event[0] for event in segment]
            self.assertIn('sync', kinds, stage)
            files = [index for index, kind in enumerate(kinds) if kind == 'file']
            self.assertTrue(all(index > kinds.index('sync') for index in files), (stage, segment))

    def test_full_sync_issues_f_fullfsync_on_database_and_reset_stage_uses_it_per_mode(self):
        path = self.directory / 'b.sqlite'
        calls = []

        def fcntl_call(descriptor, command, *args):
            calls.append((os.fstat(descriptor).st_ino, command))
            return 0

        with connect(path, create=True) as db:
            with patch.object(canonical.fcntl, 'fcntl', fcntl_call):
                database.full_sync(db)
            self.assertEqual(calls, [(path.stat().st_ino, getattr(canonical.fcntl, 'F_FULLFSYNC', None))]
                             if hasattr(canonical.fcntl, 'F_FULLFSYNC') else [])
            for mode, expected in (('build', 0), ('stage_boundaries', 1)):
                synced = []
                with patch.object(database, 'FULLFSYNC_MODE', mode), \
                        patch.object(database, 'full_sync', lambda db: synced.append(db.in_transaction)):
                    reset_stage(db, 'decisions')
                self.assertEqual(synced, [False] * expected, mode)  # po commicie resetu


if __name__ == '__main__':
    unittest.main()
