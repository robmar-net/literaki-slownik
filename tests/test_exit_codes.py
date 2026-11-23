"""R4: klasyfikator błędów buildu (75/76/77/78/4), tolerancja sprzątania i kody CLI."""
import contextlib
import errno
import io
import json
import sqlite3
from unittest import mock

from literaki_slownik import cli, database
from literaki_slownik.build import build
from literaki_slownik.canonical import load_json
from literaki_slownik.inputs import GeneratorError
from tests.layout_helpers import LayoutCase


def sqlite_error(message, code, kind=sqlite3.OperationalError):
    error = kind(message)
    error.sqlite_errorcode = code
    return error


class ExitCodeTests(LayoutCase):
    def build_code(self, error, name, work_root='T7', **kwargs):
        work_root = self.data if work_root == 'T7' else work_root
        with mock.patch('literaki_slownik.build.create_links', side_effect=error):
            with self.assertRaises(GeneratorError) as caught:
                build(self.manifest, self.work / name, work_root=work_root, **kwargs)
        return caught.exception.code

    def test_disk_io_error_is_75_when_guard_fails(self):
        def unmount(*args):
            self.mounts.discard(str(self.data))
            raise sqlite3.OperationalError('disk I/O error')

        self.assertEqual(self.build_code(unmount, 'upadly'), 75)

    def test_io_error_with_healthy_guard_is_75_on_work_volume_and_4_on_internal_disk(self):
        # T7 wrócił, zanim klasyfikator sprawdził strażnika: G1–G3 przechodzą, a błąd I/O dalej znaczy „dysk”.
        cases = (('ioerr', sqlite_error('disk I/O error', sqlite3.SQLITE_IOERR)),
                 ('ioerr-ext', sqlite_error('disk I/O error', sqlite3.SQLITE_IOERR | (13 << 8))),
                 ('cantopen', sqlite_error('unable to open database file', sqlite3.SQLITE_CANTOPEN)),
                 ('eio', OSError(errno.EIO, 'Input/output error')),
                 ('enxio', OSError(errno.ENXIO, 'Device not configured')),
                 ('enodev', OSError(errno.ENODEV, 'Operation not supported by device')),
                 ('enoent', OSError(errno.ENOENT, 'No such file or directory')),
                 ('erofs', OSError(errno.EROFS, 'Read-only file system')))
        for name, error in cases:
            with self.subTest(name):
                self.assertEqual(self.build_code(error, 't7-' + name), 75)
                self.assertEqual(self.build_code(error, 'wew-' + name, work_root=None), 4)
        attempt = load_json(self.work / 'wew-ioerr' / 'manifest.json')['build_attempts'][0]
        self.assertEqual((attempt['outcome'], attempt['exit_code'], attempt['last_stage']), ('failed', 4, 'links'))
        attempt = load_json(self.data / 't7-ioerr' / 'manifest.json')['build_attempts'][0]
        self.assertEqual((attempt['outcome'], attempt['exit_code']), ('failed', 75))
        # Inny błąd systemu plików na T7 nie jest zniknięciem dysku.
        self.assertEqual(self.build_code(OSError(errno.EACCES, 'Permission denied'), 't7-eacces'), 4)

    def test_full_disk_is_78_and_corruption_is_77(self):
        cases = (('full', sqlite_error('database or disk is full', sqlite3.SQLITE_FULL), 78),
                 ('enospc', OSError(errno.ENOSPC, 'No space left on device'), 78),
                 ('edquot', OSError(errno.EDQUOT, 'Disc quota exceeded'), 78),
                 ('corrupt', sqlite_error('database disk image is malformed', sqlite3.SQLITE_CORRUPT,
                                          sqlite3.DatabaseError), 77),
                 ('notadb', sqlite_error('file is not a database', sqlite3.SQLITE_NOTADB,
                                         sqlite3.DatabaseError), 77))
        for name, error, code in cases:
            with self.subTest(name):
                self.assertEqual(self.build_code(error, name), code)

    def test_failing_rollback_and_failed_status_write_keep_the_code(self):
        class Connection:
            def __init__(self, real):
                self.real = real

            def __getattr__(self, name):
                return getattr(self.real, name)

            def rollback(self):
                raise sqlite3.OperationalError('disk I/O error przy rollback')

            def close(self):
                self.real.close()
                raise sqlite3.OperationalError('disk I/O error przy close')

        real_connect = sqlite3.connect
        with mock.patch.object(database.sqlite3, 'connect', lambda *a, **k: Connection(real_connect(*a, **k))):
            with self.assertRaises(ValueError):
                with database.connect(self.internal / 'x.sqlite', create=True):
                    raise ValueError('pierwotny')
        real_set_stage = __import__('literaki_slownik.run', fromlist=['set_stage']).set_stage

        def set_stage(path, stage, status, details=None):
            if status == 'failed':
                raise OSError(errno.EIO, 'zapis failed niemożliwy')
            return real_set_stage(path, stage, status, details)

        with mock.patch('literaki_slownik.build.set_stage', side_effect=set_stage), \
                mock.patch('literaki_slownik.build.close_attempt', side_effect=OSError(errno.EIO, 'zamknięcie')):
            code = self.build_code(OSError(errno.ENOSPC, 'No space left on device'), 'tolerancja')
        self.assertEqual(code, 78)

    def test_cli_returns_classified_codes_and_catches_bare_sqlite_error(self):
        def run(argv):
            stdout, stderr = io.StringIO(), io.StringIO()
            with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                code = cli.main(argv)
            return code, json.loads(stdout.getvalue()), stderr.getvalue()

        with mock.patch('literaki_slownik.build.create_links',
                        side_effect=sqlite_error('database or disk is full', sqlite3.SQLITE_FULL)):
            code, result, stderr = run(['build', '--manifest', str(self.manifest), '--run-dir',
                                        str(self.work / 'cli'), '--work-root', str(self.data), '--json'])
        self.assertEqual(code, 78)
        self.assertEqual(result['diagnostics'][0]['code'], 78)
        self.assertTrue((self.work / 'cli').is_symlink())
        with mock.patch.object(cli, 'inspect_sources', side_effect=sqlite3.DatabaseError('goły błąd')):
            code, result, stderr = run(['inspect-sources', '--manifest', str(self.manifest), '--json'])
        self.assertEqual(code, 4)
        self.assertEqual(result['status'], 'error')
        self.assertIn('goły błąd', stderr)
        self.assertNotIn('Traceback', stderr)
