"""R11: sprzątanie `scripts/clean_work.py` — lista domyślnie, kasowanie tylko klas T7 i wydań za zgodą."""
from contextlib import redirect_stderr, redirect_stdout
import fcntl
import hashlib
import importlib.util
import io
import json
import os
import stat
import subprocess
import time
from pathlib import Path
from unittest import mock

from literaki_slownik.canonical import write_json
from literaki_slownik.run import STAGES
from tests.layout_helpers import LayoutCase

ROOT = Path(__file__).resolve().parent.parent
SPEC = importlib.util.spec_from_file_location('clean_work', ROOT / 'scripts/clean_work.py')
clean_work = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(clean_work)

OLD = time.time() - 3 * 86400

# Kształt jak w prawdziwym NOTICE serwera: hashe w osobnych, wciętych liniach, czasem z nawiasem.
NOTICE = """NOTICE
======

The independent Polish lists of the literaki-slownik subproject
--------------------------------------------------------------
Source:       literaki-slownik, release v29, readiness VERIFIED
Playing lists:
              LL-PL-STANDARD.txt, 3 entries, sha256
              {list_hash}
              (released as LL-PL-STANDARD.txt.gz, sha256
              {gz_hash})
              -> lexicons/pl-standard-20261011.dawg
Retired lists still shipped:
              release v28, release-manifest sha256
              {manifest_hash}.
              -> lexicons/pl-broad-20261009.dawg
"""


def age(path, when=OLD):
    """Stary wiek całego drzewa (od liści, na końcu sam katalog)."""
    path = Path(path)
    if path.is_dir() and not path.is_symlink():
        for current, names, files in os.walk(path, topdown=False):
            for name in names + files:
                os.utime(Path(current) / name, (when, when), follow_symlinks=False)
    os.utime(path, (when, when), follow_symlinks=False)


def run(path, readiness='INCOMPLETE', *, pending=False, sqlite=True, old=True, failed=False):
    """Przebieg-fikstura; failed=True: przerwany w etapie links (dalsze etapy pending)."""
    path = Path(path)
    path.mkdir(parents=True)
    stages = {name: {'status': 'pending' if pending else 'complete'} for name in STAGES}
    if failed:
        stages.update(links={'status': 'failed'}, reports={'status': 'pending'})
    write_json(path / 'manifest.json', {'schema_version': 1, 'readiness': readiness, 'stages': stages})
    if sqlite:
        (path / 'build.sqlite').write_bytes(b'db')
    if old:
        age(path)
    return path


def release(work, name, *, package='LL-PL', frozen_at='2026-10-01T00:00:00+00:00', run_name=None,
            text='kot\n'):
    path = Path(work) / name
    path.mkdir(parents=True)
    listing = path / 'LL-PL-STANDARD.txt'
    listing.write_text(text, encoding='utf-8')
    digest = hashlib.sha256(listing.read_bytes()).hexdigest()
    manifest = {'schema_version': 1, 'kind': 'literaki-release-manifest', 'package_id': package,
                'status': 'FROZEN', 'frozen_at': frozen_at,
                'files': {listing.name: {'bytes': listing.stat().st_size, 'sha256': digest}}}
    if run_name is not None:
        manifest['source_run'] = {'run_name': run_name}
    write_json(path / 'release-manifest.json', manifest)
    age(path)
    return path, digest


def git(repo, *args):
    env = {key: value for key, value in os.environ.items() if not key.startswith('GIT_')}
    env.update(GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM='1')
    subprocess.run(['git', '-C', str(repo), '-c', 'user.name=t', '-c', 'user.email=t@example.invalid',
                    '-c', 'commit.gpgsign=false', *args], check=True, capture_output=True, env=env)


class CleanWorkCase(LayoutCase):
    def setUp(self):
        super().setUp()
        self.logs = self.repo / 'logs'
        self.logs.mkdir()
        (self.repo / 'config/generator').mkdir(parents=True)
        self.server = self.internal / 'server-fixture'

    def server_repo(self, notice=None, *, origin=True):
        self.server.mkdir()
        git(self.server, 'init', '-q')
        if notice is not None:
            (self.server / 'NOTICE').write_text(notice, encoding='utf-8')
        else:
            (self.server / 'README').write_text('x\n', encoding='utf-8')
        git(self.server, 'add', '-A')
        git(self.server, 'commit', '-q', '-m', 'fikstura')
        if origin:
            git(self.server, 'update-ref', 'refs/remotes/origin/main', 'HEAD')

    def clean(self, *args, server=None):
        stdout, stderr = io.StringIO(), io.StringIO()
        argv = ['--work-root', str(self.data), '--server-repo', str(server or self.server), *args]
        with redirect_stdout(stdout), redirect_stderr(stderr):
            code = clean_work.main(argv)
        self.stderr = stderr.getvalue()
        return code, (json.loads(stdout.getvalue()) if stdout.getvalue() else None)

    @staticmethod
    def classes(result, where=None):
        return {item['entry']: item['class'] for item in result['entries']
                if where is None or item['where'] == where}

    def hold(self, path):
        lock = open(path, 'a')
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        self.addCleanup(lock.close)

    def every_class(self):
        """T7 z każdą klasą 1–6 oraz wpisy dysku wewnętrznego (7, 8)."""
        run(self.data / 'verified', 'VERIFIED')
        frozen = run(self.data / 'frozen', 'FROZEN')
        os.symlink(frozen, self.work / 'frozen')
        promoting = run(self.data / 'promoting')
        record = self.work / 'prom'
        record.mkdir()
        write_json(record / 'promotion.json', {'t7_path': str(promoting), 'peer_path': None,
                                               'peer_link': None, 'completed': None})
        run(self.data / 'staged')
        (self.work / '.staged.promote').mkdir()
        run(self.data / 'locked')
        self.hold(self.logs / 'locked.lock')
        run(self.data / 'fresh', old=False)
        unknown = self.data / 'unknown'
        unknown.mkdir()
        (unknown / 'x.bin').write_bytes(b'x')
        age(unknown)
        run(self.data / 'orphan', failed=True)
        run(self.data / 'leftover', pending=True, sqlite=False)
        unfinished = run(self.data / 'unfinished', failed=True)
        os.symlink(unfinished, self.work / 'unfinished')
        # Wszystkie etapy complete, ≥ 24 h przed verify: para czeka na przegląd i nie znika (decyzja właściciela).
        complete = run(self.data / 'complete')
        os.symlink(complete, self.work / 'complete')
        run(self.data / 'complete-bez-linku')
        run(self.data / 'building')
        self.hold(self.work / '.building.build.lock')
        release(self.work, 'release-LL-PL-v30')
        (self.work / 'stary.log').write_text('log\n', encoding='utf-8')

    def snapshot(self):
        state = []
        for current, names, files in os.walk(self.internal):
            for name in sorted(names + files):
                path = Path(current) / name
                info = os.lstat(path)
                state.append((str(path), info.st_mode, info.st_size, info.st_mtime_ns))
        return sorted(state)


class CleanWorkTests(CleanWorkCase):
    def test_lista_domyslnie_nic_nie_zmienia_i_zna_kazda_klase(self):
        self.every_class()
        self.server_repo(NOTICE.format(list_hash='a' * 64, gz_hash='b' * 64, manifest_hash='c' * 64))
        before = self.snapshot()
        code, result = self.clean()
        self.assertEqual(code, 0, self.stderr)
        self.assertEqual(self.snapshot(), before)
        self.assertFalse(result['apply'])
        self.assertEqual(result['deleted'], [])
        self.assertEqual(self.classes(result, 't7'), {
            'verified': 1, 'frozen': 1, 'promoting': 2, 'staged': 2, 'locked': 3, 'fresh': 3,
            'unknown': 4, 'orphan': 5, 'leftover': 5, 'unfinished': 6, 'complete': 3, 'complete-bez-linku': 3,
            'building': 3})
        reasons = {item['entry']: item['reason'] for item in result['entries']}
        self.assertEqual(reasons['complete'], 'kompletny, czeka na verify')
        # Kompletny przebieg czeka bez limitu i zajmuje ~22 GB: lista pokazuje jego wiek w dniach.
        ages = {item['entry']: item.get('age_days') for item in result['entries']}
        self.assertEqual(ages['complete'], 3)
        self.assertEqual(ages['complete-bez-linku'], 3)
        self.assertIsNone(ages['building'])
        self.assertEqual(reasons['building'], 'trzymana blokada buildu')
        self.assertNotIn('.building.build.lock', self.classes(result))
        internal = self.classes(result, 'internal')
        self.assertEqual(internal['release-LL-PL-v30'], 7)  # ostatnie w rodzinie
        self.assertEqual(internal['stary.log'], 7)
        self.assertEqual(internal['prom'], 7)
        for item in result['entries']:
            self.assertIn('size', item)
            self.assertTrue(item['reason'])

    def test_apply_kasuje_tylko_klasy_5_i_6(self):
        self.every_class()
        self.server_repo(NOTICE.format(list_hash='a' * 64, gz_hash='b' * 64, manifest_hash='c' * 64))
        code, result = self.clean('--apply')
        self.assertEqual(code, 0, self.stderr)
        self.assertEqual(sorted(item['entry'] for item in result['deleted']),
                         ['leftover', 'orphan', 'unfinished'])
        for name in ('orphan', 'leftover', 'unfinished'):
            self.assertFalse(os.path.lexists(self.data / name), name)
        self.assertFalse(os.path.lexists(self.work / 'unfinished'))
        for name in ('verified', 'frozen', 'promoting', 'staged', 'locked', 'fresh', 'unknown', 'complete',
                     'complete-bez-linku', 'building'):
            self.assertTrue((self.data / name).is_dir(), name)
        for name in ('frozen', 'prom', '.staged.promote', 'release-LL-PL-v30', 'stary.log'):
            self.assertTrue(os.path.lexists(self.work / name), name)

    def test_verified_frozen_i_promocja_w_toku_nigdy_nie_znikaja(self):
        run(self.data / 'verified-bez-linku', 'VERIFIED')
        run(self.data / 'frozen-bez-linku', 'FROZEN')
        dangling = self.data / 'verified-zly-link'
        run(dangling, 'VERIFIED')
        os.symlink(self.data / 'nie-ma', self.work / 'verified-zly-link')
        peer = run(self.data / 'peer-promocji')
        record = self.work / '.cel.promote'
        record.mkdir()
        write_json(record / 'promotion.json', {'t7_path': str(self.data / 'cel'), 'peer_path': str(peer),
                                               'peer_link': None, 'completed': None})
        run(self.data / 'z-blokada')
        self.hold(self.logs / 'z-blokada.promote.lock')
        code, result = self.clean('--apply')
        self.assertEqual(code, 0, self.stderr)
        self.assertEqual(result['deleted'], [])
        self.assertEqual(self.classes(result, 't7'), {
            'verified-bez-linku': 1, 'frozen-bez-linku': 1, 'verified-zly-link': 1,
            'peer-promocji': 2, 'z-blokada': 2})
        for name in ('verified-bez-linku', 'frozen-bez-linku', 'verified-zly-link', 'peer-promocji', 'z-blokada'):
            self.assertTrue((self.data / name / 'manifest.json').exists(), name)

    def test_wydanie_przypiete_biezace_i_ostatnie_nigdy_nie_jest_kandydatem(self):
        self.assertEqual(clean_work.parse_version('pop-v1r2-20261011-172408-a'), ('pop', (1, 2)))
        self.assertEqual(clean_work.parse_version('release-LL-PL-v30'), ('release-LL-PL', (30,)))
        self.assertIsNone(clean_work.parse_version('wydanie-bez-wersji'))
        self.server_repo(NOTICE.format(list_hash='a' * 64, gz_hash='b' * 64, manifest_hash='c' * 64))
        release(self.work, 'pop-v1-20261011-a', package='POP', text='a\n')
        release(self.work, 'pop-v1r2-20261011-a', package='POP', text='b\n')
        release(self.work, 'pop-v2-20261011-a', package='POP', text='c\n')
        release(self.work, 'tematy-wydanie-x/tematy-morze-v1-20261029-a', package='TEMATY', text='d\n')
        release(self.work, 'tematy-morze-v2-20261029-a', package='TEMATY', text='e\n')
        release(self.work, 'release-LL-PL-v28', text='f\n')
        release(self.work, 'release-LL-PL-v29', text='g\n')
        release(self.work, 'release-LL-PL-v30', text='h\n')
        release(self.work, 'wydanie-bez-wersji', text='i\n')
        write_json(self.repo / 'config/generator/pop-sources.json', {'inputs': [
            {'path': '../../data/work/pop-v1r2-20261011-a/release-manifest.json', 'sha256': 'x'}]})
        code, result = self.clean('--server-current', 'release-LL-PL-v29')
        self.assertEqual(code, 0, self.stderr)
        self.assertEqual(result['server_notice']['status'], 'available')
        self.assertEqual(sorted(result['candidates']),
                         ['pop-v1-20261011-a', 'release-LL-PL-v28', 'tematy-wydanie-x/tematy-morze-v1-20261029-a'])
        internal = self.classes(result, 'internal')
        for name in ('pop-v1r2-20261011-a', 'pop-v2-20261011-a', 'tematy-morze-v2-20261029-a',
                     'release-LL-PL-v29', 'release-LL-PL-v30', 'wydanie-bez-wersji', 'tematy-wydanie-x'):
            self.assertEqual(internal[name], 7, name)
        reasons = {item['entry']: item['reason'] for item in result['entries']}
        self.assertIn('config/generator', reasons['pop-v1r2-20261011-a'])
        self.assertIn('--server-current', reasons['release-LL-PL-v29'])
        self.assertIn('ostatnie w rodzinie', reasons['release-LL-PL-v30'])

    def test_notice_w_prawdziwym_ksztalcie_chroni_wydania_z_serwera(self):
        _, list_hash = release(self.work, 'release-LL-PL-v29', text='lista v29\n')
        old, _ = release(self.work, 'release-LL-PL-v28', text='lista v28\n')
        release(self.work, 'release-LL-PL-v27', text='lista v27\n')
        release(self.work, 'release-LL-PL-v31', text='lista v31\n')
        manifest_hash = hashlib.sha256((old / 'release-manifest.json').read_bytes()).hexdigest()
        self.server_repo(NOTICE.format(list_hash=list_hash, gz_hash='b' * 64, manifest_hash=manifest_hash))
        code, result = self.clean()
        self.assertEqual(code, 0, self.stderr)
        notice = result['server_notice']
        self.assertEqual(notice['status'], 'available')
        self.assertEqual(notice['hashes'], 3)
        self.assertEqual(notice['lexicons'], ['lexicons/pl-broad-20261009.dawg', 'lexicons/pl-standard-20261011.dawg'])
        self.assertEqual(result['candidates'], ['release-LL-PL-v27'])
        reasons = {item['entry']: item['reason'] for item in result['entries']}
        self.assertIn('NOTICE', reasons['release-LL-PL-v29'])
        self.assertIn('NOTICE', reasons['release-LL-PL-v28'])

    def test_brak_repo_lub_notice_to_zero_kandydatow_i_komunikat(self):
        release(self.work, 'release-LL-PL-v29', text='a\n')
        release(self.work, 'release-LL-PL-v30', text='b\n')
        cases = (('brak-repo', None, True), ('bez-notice', None, True), ('bez-origin', 'x ' + 'a' * 64, False),
                 ('bez-hashy', 'NOTICE\nbez hashy\n', True))
        for label, notice, origin in cases:
            with self.subTest(label):
                if self.server.exists():
                    import shutil
                    shutil.rmtree(self.server)
                if label != 'brak-repo':
                    self.server_repo(notice, origin=origin)
                code, result = self.clean()
                self.assertEqual(code, 0, self.stderr)
                self.assertEqual(result['server_notice']['status'], 'unavailable')
                self.assertTrue(result['server_notice']['reason'])
                self.assertEqual(result['candidates'], [])
                self.assertEqual(self.classes(result, 'internal')['release-LL-PL-v29'], 7)

    def test_delete_releases_z_nazwa_potrzebna_odmawia_calosci(self):
        self.server_repo(NOTICE.format(list_hash='a' * 64, gz_hash='b' * 64, manifest_hash='c' * 64))
        release(self.work, 'release-LL-PL-v28', text='a\n')
        release(self.work, 'release-LL-PL-v30', text='b\n')
        run(self.data / 'orphan', failed=True)
        approved = self.internal / 'zgoda.txt'
        approved.write_text('release-LL-PL-v28\nrelease-LL-PL-v30\n', encoding='utf-8')
        before = self.snapshot()
        code, result = self.clean('--apply', '--delete-releases', str(approved))
        self.assertEqual(code, 4)
        self.assertIsNone(result)
        self.assertIn('release-LL-PL-v30', self.stderr)
        self.assertEqual(self.snapshot(), before)
        code, _ = self.clean('--delete-releases', str(approved))
        self.assertEqual(code, 2)
        self.assertEqual(self.snapshot(), before)

    def test_delete_releases_kasuje_kandydata_tylko_do_odczytu_z_jego_przebiegiem(self):
        self.server_repo(NOTICE.format(list_hash='a' * 64, gz_hash='b' * 64, manifest_hash='c' * 64))
        run(self.work / 'run-27', 'FROZEN')
        run(self.work / 'run-shared', 'FROZEN')
        v27, _ = release(self.work, 'release-LL-PL-v27', text='a\n', run_name='run-27')
        release(self.work, 'release-LL-PL-v26', text='b\n', run_name='run-shared')
        release(self.work, 'release-LL-PL-v30', text='c\n', run_name='run-shared')
        release(self.work, 'release-LL-PL-v25', text='d\n')
        for path in (v27, self.work / 'run-27'):
            for current, _, files in os.walk(path):
                for name in files:
                    os.chmod(Path(current) / name, stat.S_IRUSR)
            os.chmod(path, stat.S_IRUSR | stat.S_IXUSR)
        approved = self.internal / 'zgoda.txt'
        approved.write_text('release-LL-PL-v27\nrelease-LL-PL-v26\n', encoding='utf-8')
        code, result = self.clean('--apply', '--delete-releases', str(approved))
        self.assertEqual(code, 0, self.stderr)
        for name in ('release-LL-PL-v27', 'run-27', 'release-LL-PL-v26'):
            self.assertFalse(os.path.lexists(self.work / name), name)
        for name in ('release-LL-PL-v30', 'run-shared', 'release-LL-PL-v25'):
            self.assertTrue((self.work / name).is_dir(), name)
        deleted = {item['entry'] for item in result['deleted']}
        self.assertEqual(deleted, {'release-LL-PL-v27', 'run-27', 'release-LL-PL-v26'})

    def test_przerwane_kasowanie_konczy_nastepne_apply(self):
        import shutil
        self.server_repo(NOTICE.format(list_hash='a' * 64, gz_hash='b' * 64, manifest_hash='c' * 64))
        orphan = run(self.data / 'orphan', failed=True)
        (orphan / 'reports').mkdir()
        (orphan / 'reports' / 'r.json').write_text('{}', encoding='utf-8')
        age(orphan)
        release(self.work, 'release-LL-PL-v27', text='a\n')
        release(self.work, 'release-LL-PL-v30', text='b\n')
        approved = self.internal / 'zgoda.txt'
        approved.write_text('release-LL-PL-v27\n', encoding='utf-8')
        real_rmtree, seen = shutil.rmtree, set()

        def partial(path, *args, **kwargs):
            # Pierwsze kasowanie każdego drzewa przerwane w środku: manifest już zniknął, reszta została.
            if str(path) in seen:
                return real_rmtree(path, *args, **kwargs)
            seen.add(str(path))
            for name in ('manifest.json', 'release-manifest.json'):
                if (Path(path) / name).exists():
                    (Path(path) / name).unlink()
            raise KeyboardInterrupt
        for _ in range(2):
            with mock.patch('shutil.rmtree', partial), self.assertRaises(KeyboardInterrupt):
                clean_work.clean(str(self.data), apply=True, server_repo=str(self.server),
                                 delete_file=str(approved) if _ else None)
        self.assertEqual(len(seen), 2)  # T7 w pierwszym, wydanie w drugim przebiegu
        code, result = self.clean('--apply')
        self.assertEqual(code, 0, self.stderr)
        self.assertFalse(any(name.endswith('.deleting') for name in os.listdir(self.data)), os.listdir(self.data))
        self.assertFalse(any(name.endswith('.deleting') for name in os.listdir(self.work)), os.listdir(self.work))
        self.assertFalse(os.path.lexists(self.data / 'orphan'))
        self.assertFalse(os.path.lexists(self.work / 'release-LL-PL-v27'))
        self.assertTrue((self.work / 'release-LL-PL-v30').is_dir())

    def test_blad_dysku_przy_kasowaniu_to_kod_a_nie_traceback(self):
        import errno
        self.server_repo(NOTICE.format(list_hash='a' * 64, gz_hash='b' * 64, manifest_hash='c' * 64))
        run(self.data / 'orphan', failed=True)
        with mock.patch('shutil.rmtree', side_effect=OSError(errno.EIO, 'Input/output error')):
            code, result = self.clean('--apply')
        self.assertEqual((code, result['exit_code'], result['deleted']), (4, 4, []))
        self.assertIn('Input/output error', result['error'])
        self.assertIn('Input/output error', self.stderr)

    def test_blad_w_polowie_apply_podaje_liste_juz_skasowanych(self):
        import errno
        import shutil
        self.server_repo(NOTICE.format(list_hash='a' * 64, gz_hash='b' * 64, manifest_hash='c' * 64))
        run(self.data / 'orphan-a', failed=True)
        run(self.data / 'orphan-b', failed=True)
        real_rmtree, calls = shutil.rmtree, []

        def second_fails(path, *args, **kwargs):
            calls.append(path)
            if len(calls) == 2:
                raise OSError(errno.EIO, 'Input/output error')
            return real_rmtree(path, *args, **kwargs)
        with mock.patch('shutil.rmtree', second_fails):
            code, result = self.clean('--apply')
        self.assertEqual(code, 4, self.stderr)
        self.assertEqual([(item['entry'], item['where']) for item in result['deleted']], [('orphan-a', 't7')])
        self.assertFalse(os.path.lexists(self.data / 'orphan-a'))

    def test_przerwane_kasowanie_wydania_nie_jest_wydaniem(self):
        self.server_repo(NOTICE.format(list_hash='a' * 64, gz_hash='b' * 64, manifest_hash='c' * 64))
        release(self.work, 'release-LL-PL-v30', text='b\n')
        # Przerwane kasowanie zostawiło release-manifest.json w drzewie `.<nazwa>.deleting`.
        release(self.work, '.release-LL-PL-v27.deleting', text='a\n')
        release(self.work / 'wydania', 'release-LL-PL-v25', text='c\n')
        release(self.work / 'wydania', '.release-LL-PL-v24.deleting', text='d\n')
        code, result = self.clean()
        self.assertEqual(code, 0, self.stderr)
        entries = {item['entry']: item for item in result['entries']}
        self.assertNotIn('wydania/.release-LL-PL-v24.deleting', entries)
        self.assertEqual(entries['.release-LL-PL-v27.deleting']['reason'],
                         'przerwane kasowanie wydania (.deleting); dokończy --apply')
        self.assertFalse(any('.deleting' in name for name in result['candidates']), result['candidates'])
        code, result = self.clean('--apply')
        self.assertEqual(code, 0, self.stderr)
        self.assertFalse(os.path.lexists(self.work / '.release-LL-PL-v27.deleting'))
        self.assertFalse(os.path.lexists(self.work / 'wydania' / '.release-LL-PL-v24.deleting'))
        self.assertTrue((self.work / 'wydania' / 'release-LL-PL-v25').is_dir())


class PromotionThenCleanTests(CleanWorkCase):
    """Styk: rekord prawdziwego promote_run.py czyta clean_work.py na tym samym drzewie."""

    def test_przerwana_promocja_chroni_t7_a_ukonczona_zostawia_tylko_kopie_wewnetrzna(self):
        from literaki_slownik.verify import verify
        from tests.release_helpers import complete_pair
        from tests.test_promote_run import Crash, crash_at, promote_run
        _, run_a, run_b, review = complete_pair(self.data)
        link_a, link_b = self.work / 'run-a', self.work / 'run-b'
        os.symlink(run_a, link_a)
        os.symlink(run_b, link_b)
        self.assertEqual(verify(link_a, link_b, review, allow_test_fixture=True)['verdict'], 'VERIFIED')
        with self.assertRaises(Crash):
            promote_run.promote(link_a, link_b, hook=crash_at('unlinked'))
        # B ma rekord promocji (klasa 2), więc przegrywa nawet z „kompletny, czeka na verify” (3).
        age(run_a)
        age(run_b)
        self.server_repo()
        code, result = self.clean('--apply')
        self.assertEqual(code, 0, self.stderr)
        self.assertEqual(result['deleted'], [])
        t7 = self.classes(result, 't7')
        self.assertEqual((t7['run-a'], t7['run-b']), (1, 2))
        self.assertTrue((run_a / 'manifest.json').is_file())
        self.assertTrue((run_b / 'manifest.json').is_file())
        self.assertEqual(self.classes(result, 'internal')['run-a'], 7)

        self.assertEqual(promote_run.promote(link_a, link_b)['status'], 'promoted')
        code, result = self.clean('--apply')
        self.assertEqual(code, 0, self.stderr)
        self.assertEqual(result['deleted'], [])
        t7 = self.classes(result, 't7')
        self.assertNotIn('run-a', t7)
        self.assertNotIn('run-b', t7)
        self.assertEqual(self.classes(result, 'internal')['run-a'], 7)
        self.assertTrue((link_a / 'build.sqlite').is_file())


if __name__ == '__main__':
    import unittest
    unittest.main()
