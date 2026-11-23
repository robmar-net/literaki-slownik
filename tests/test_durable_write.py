import os
import sqlite3
import stat
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from literaki_slownik import canonical
from literaki_slownik.build import write_lists


class Fcntl:
    """Podstawiony moduł fcntl, który zapisuje wywołania w dzienniku."""
    def __init__(self, log, path=None, has_command=True, fails=False):
        self.log, self.path, self.fails = log, path, fails
        if has_command:
            self.F_FULLFSYNC = 51

    def fcntl(self, descriptor, command):
        if stat.S_ISDIR(os.fstat(descriptor).st_mode):
            self.log.append(('fullfsync_dir',))
        else:
            # Treść musi być już zapisana w pliku tymczasowym.
            self.log.append(('fullfsync', os.pread(descriptor, 1024, 0)))
        if self.fails:
            raise OSError('ENOTSUP')


class DurableWriteTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.root = Path(self.directory.name)
        self.target = self.root / 'plik.json'
        self.log = []
        real_replace, real_fsync, real_mkstemp = os.replace, os.fsync, tempfile.mkstemp

        def replace(source, destination):
            self.log.append(('replace', Path(source).parent, Path(destination)))
            real_replace(source, destination)

        def fsync(descriptor):
            kind = 'fsync_dir' if stat.S_ISDIR(os.fstat(descriptor).st_mode) else 'fsync'
            self.log.append((kind,))
            real_fsync(descriptor)

        def mkstemp(*args, **kwargs):
            self.log.append(('mkstemp', Path(kwargs['dir'])))
            return real_mkstemp(*args, **kwargs)

        self.replace, self.fsync, self.mkstemp = replace, fsync, mkstemp
        self.addCleanup(self.directory.cleanup)
        self.addCleanup(canonical.set_replace_guard, None)

    def patched(self, fake_fcntl):
        return [mock.patch.object(canonical, 'fcntl', fake_fcntl),
                mock.patch.object(canonical.os, 'replace', self.replace),
                mock.patch.object(canonical.os, 'fsync', self.fsync),
                mock.patch.object(canonical.tempfile, 'mkstemp', self.mkstemp)]

    def run_patched(self, fake_fcntl, function, *args):
        patches = self.patched(fake_fcntl)
        for patch in patches:
            patch.start()
        try:
            return function(*args)
        finally:
            for patch in reversed(patches):
                patch.stop()

    def test_order_tmp_write_fullfsync_hook_replace_dirsync(self):
        canonical.set_replace_guard(lambda path: self.log.append(('guard', Path(path))))
        self.run_patched(Fcntl(self.log), canonical.write_json, self.target, {'b': 1, 'a': 'ż'})
        data = (canonical.dumps({'b': 1, 'a': 'ż'}) + '\n').encode('utf-8')
        self.assertEqual(self.log, [
            ('mkstemp', self.root), ('fullfsync', data), ('guard', self.target),
            ('replace', self.root, self.target), ('fullfsync_dir',)])
        self.assertEqual(self.target.read_bytes(), data)
        self.assertEqual(sorted(p.name for p in self.root.iterdir()), ['plik.json'])

    def test_fallback_to_fsync_without_command_or_on_error(self):
        for fake in (Fcntl(self.log, has_command=False), Fcntl(self.log, fails=True)):
            with self.subTest(has_command=hasattr(fake, 'F_FULLFSYNC')):
                self.log.clear()
                self.run_patched(fake, canonical.write_bytes, self.target, b'abc\n')
                kinds = [entry[0] for entry in self.log]
                expected = (['mkstemp', 'fsync', 'replace', 'fsync_dir'] if not hasattr(fake, 'F_FULLFSYNC')
                            else ['mkstemp', 'fullfsync', 'fsync', 'replace', 'fullfsync_dir', 'fsync_dir'])
                self.assertEqual(kinds, expected)
                self.assertEqual(self.target.read_bytes(), b'abc\n')

    def test_interrupt_before_replace_keeps_old_file_and_no_tmp(self):
        self.target.write_bytes(b'stary\n')

        def guard(path):
            raise KeyboardInterrupt
        canonical.set_replace_guard(guard)
        with self.assertRaises(KeyboardInterrupt):
            canonical.write_bytes(self.target, b'nowy\n')
        self.assertEqual(self.target.read_bytes(), b'stary\n')
        self.assertEqual([p.name for p in self.root.iterdir()], ['plik.json'])

    def test_unlink_error_does_not_mask_original_exception(self):
        class Original(Exception):
            pass

        def guard(path):
            raise Original('błąd zapisu')
        canonical.set_replace_guard(guard)
        with mock.patch.object(canonical.os, 'unlink', side_effect=OSError('EIO')):
            with self.assertRaises(Original):
                canonical.write_bytes(self.target, b'x')

    def test_write_json_bytes_unchanged(self):
        value = {'z': [1, 2.5, None], 'ą': {'k': True}, 'a': 'tekst'}
        canonical.write_json(self.target, value)
        expected = b'{"a":"tekst","z":[1,2.5,null],"\xc4\x85":{"k":true}}\n'
        self.assertEqual(self.target.read_bytes(), expected)

    def test_write_lists_uses_write_bytes_with_same_bytes(self):
        db = sqlite3.connect(':memory:')
        self.addCleanup(db.close)
        db.executescript('''create table analysis(analysis_key, game_key);
            create table variant_decision(analysis_key, variant, membership_status);
            insert into analysis values (1,'kot'),(2,'ala'),(3,'żuk');
            insert into variant_decision values (1,'broad','accept'),(2,'broad','accept'),
              (3,'broad','accept'),(1,'standard','accept'),(3,'standard','reject');''')
        written = []
        real = canonical.write_bytes
        with mock.patch('literaki_slownik.build.write_bytes',
                        side_effect=lambda path, data: (written.append(Path(path).name), real(path, data))):
            sizes = write_lists(db, self.root)
        self.assertEqual(sizes, {'broad': 3, 'standard': 1})
        self.assertEqual(written, ['broad.txt', 'standard.txt'])
        self.assertEqual((self.root / 'lists' / 'broad.txt').read_bytes(), 'ala\nkot\nżuk\n'.encode('utf-8'))
        self.assertEqual((self.root / 'lists' / 'standard.txt').read_bytes(), b'kot\n')


if __name__ == '__main__':
    unittest.main()
