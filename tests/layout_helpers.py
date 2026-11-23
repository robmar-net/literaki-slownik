"""Fikcyjny układ dysków dla testów przebiegu na wolumenie roboczym (bez /Volumes)."""
import gzip
import hashlib
import os
import tempfile
import types
import unittest
from pathlib import Path
from unittest import mock

from literaki_slownik import canonical, volume
from tests.helpers import fixture_manifest, rewrite

GB = 10 ** 9
SOURCE = '#</COPYRIGHT>\nkot\tkot\tsubst:sg:nom:m2\t\t\nkota\tkot\tsubst:sg:gen:m2\t\t\n'


class LayoutCase(unittest.TestCase):
    """Dysk systemowy z repo oraz zamontowany wolumen `Data` ze znacznikiem."""

    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        base = Path(os.path.realpath(self.directory.name))
        self.internal, self.data = base, base / 'Volumes' / 'Data'
        self.repo = self.internal / 'repo'
        self.work = self.repo / 'data' / 'work'
        for path in (self.work, self.data, self.internal / 'inputs'):
            path.mkdir(parents=True)
        self.mounts = {str(self.internal), str(self.data)}
        real_ismount = os.path.ismount
        for patch in (
            mock.patch.object(volume, 'REPO_ROOT', self.repo),
            mock.patch('os.path.ismount', lambda path: os.path.realpath(path) in self.mounts
                       or (os.path.realpath(path) == '/' and real_ismount('/'))),
            mock.patch('os.statvfs', lambda path: types.SimpleNamespace(f_bavail=500 * GB, f_frsize=1)),
        ):
            patch.start()
            self.addCleanup(patch.stop)
        self.addCleanup(volume.deactivate)
        canonical.write_json(self.data / volume.MARKER, {'schema_version': 1, 'marker_id': 'm-data',
                                                         'volume_uuid': 'FAKE'})
        self.manifest = self.sources(self.internal / 'inputs')

    @staticmethod
    def sources(directory):
        path, manifest = fixture_manifest(directory)
        source = Path(directory) / 'source.gz'
        with gzip.open(source, 'wt', encoding='utf-8') as stream:
            stream.write(SOURCE)
        manifest['artifacts'][0]['sha256'] = hashlib.sha256(source.read_bytes()).hexdigest()
        rewrite(path, manifest)
        return path
