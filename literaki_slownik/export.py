"""Export zweryfikowanego kandydata do nowego katalogu i zamrożenie przebiegu.

Export niczego nie buduje ani nie ocenia ponownie: sprawdza pieczęć verify,
kopiuje dokładnie zweryfikowane bajty do katalogu staging obok celu, porównuje
hashe i przenosi staging pod nową nazwę bez nadpisania (także przy wyścigu).
"""
import ctypes
import errno
import os
from pathlib import Path
import stat
import sys
import tempfile
from .canonical import dumps, load_json, sha256, write_json
from .inputs import GeneratorError, inspect_sources
from .run import now
from .verify import manifest_core_sha256

RENAME_EXCL = 0x00000004      # macOS renamex_np
RENAME_NOREPLACE = 1          # Linux renameat2
AT_FDCWD = -100
READ_ONLY = stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH


def _fallback_rename(source, target):
    # Bez atomowego rename bez zamiany: mkdir rezerwuje cel wyłącznie dla nas.
    os.mkdir(target)
    for child in os.listdir(source):
        os.rename(os.path.join(source, child), os.path.join(target, child))
    os.rmdir(source)


def rename_noreplace(source, target):
    """Przenosi katalog pod nową nazwę; istniejący cel (nawet pusty) daje FileExistsError."""
    source_b, target_b = os.fsencode(source), os.fsencode(target)
    libc = ctypes.CDLL(None, use_errno=True)
    try:
        if sys.platform == 'darwin':
            result = libc.renamex_np(source_b, target_b, ctypes.c_uint(RENAME_EXCL))
        else:
            result = libc.renameat2(AT_FDCWD, source_b, AT_FDCWD, target_b, ctypes.c_uint(RENAME_NOREPLACE))
    except AttributeError:
        return _fallback_rename(source, target)
    if result == 0:
        return None
    code = ctypes.get_errno()
    if code in (errno.EEXIST, errno.ENOTEMPTY):
        raise FileExistsError(code, os.strerror(code), str(target))
    if code in (errno.EINVAL, errno.ENOTSUP, errno.ENOSYS):
        return _fallback_rename(source, target)
    raise OSError(code, os.strerror(code), str(target))


def write_release_manifest(staging, data):
    write_json(Path(staging) / 'release-manifest.json', data)


def changes_since_verify(run, manifest):
    """Wszystko, co unieważnia zapisany verdict; pusta lista oznacza zgodność."""
    from .reports import canonical_index
    seal = manifest.get('verification') or {}
    changes = []
    if manifest_core_sha256(manifest) != seal.get('manifest_core_sha256'):
        changes.append('manifest przebiegu')
    inputs = manifest.get('inputs', {})
    try:
        current = inspect_sources(inputs['manifest_path'])
        if current['manifest_sha256'] != inputs.get('manifest_sha256'):
            changes.append('manifest wejść')
    except (GeneratorError, KeyError) as error:
        changes.append(f'wejścia ({error})')
    index_path = run / 'reports/canonical-index.json'
    try:
        if sha256(index_path) != seal.get('canonical_index_sha256'):
            changes.append('reports/canonical-index.json')
        stored = load_json(index_path)
        if dumps(canonical_index(run)) != dumps(stored):
            changes.append('pliki kanoniczne przebiegu (listy/raporty)')
    except (GeneratorError, OSError, ValueError) as error:
        changes.append(f'canonical-index ({error})')
    try:
        if sha256(run / 'build.sqlite') != seal.get('database_sha256'):
            changes.append('build.sqlite')
    except OSError as error:
        changes.append(f'build.sqlite ({error})')
    attempt = run / seal.get('attempt', '')
    try:
        if sha256(attempt / 'verification.json') != seal.get('verification_sha256'):
            changes.append('verification.json')
        if sha256(attempt / 'package-plan.json') != seal.get('package_plan_sha256'):
            changes.append('package-plan.json')
        plan = load_json(attempt / 'package-plan.json')
        for relative, meta in plan['files'].items():
            path = attempt / 'candidate' / relative
            if path.is_symlink() or sha256(path) != meta['sha256']:
                changes.append(f'kandydat {relative}')
    except (OSError, ValueError, KeyError) as error:
        changes.append(f'próba verify ({error})')
    return changes


def export(run_dir, output_dir, *, allow_test_fixture=False):
    run, target = Path(run_dir), Path(output_dir)
    try:
        manifest = load_json(run / 'manifest.json')
    except (OSError, ValueError) as error:
        raise GeneratorError(f'Katalog nie jest przebiegiem generatora: {error}', 5, str(run)) from error
    readiness = manifest.get('readiness')
    if readiness == 'FROZEN':
        raise GeneratorError('Przebieg jest już FROZEN; ponowny export nie jest możliwy', 5, str(run))
    if readiness != 'VERIFIED':
        raise GeneratorError(f'Export wymaga przebiegu VERIFIED (jest {readiness})', 5, str(run))
    seal = manifest['verification']
    if seal.get('fixture') and not allow_test_fixture:
        raise GeneratorError('Przebieg fikstury testowej nie może być eksportowany przez publiczne CLI', 5, str(run))
    if os.path.lexists(target):
        raise GeneratorError('Cel exportu już istnieje; export nigdy nie nadpisuje', 5, str(target))
    if not target.parent.is_dir():
        raise GeneratorError('Katalog nadrzędny celu nie istnieje', 2, str(target.parent))
    changes = changes_since_verify(run, manifest)
    if changes:
        raise GeneratorError('Zmiany po verify unieważniają werdykt: ' + ', '.join(changes), 5, str(run))
    attempt = run / seal['attempt']
    plan = load_json(attempt / 'package-plan.json')
    staging = Path(tempfile.mkdtemp(prefix=f'.{target.name}.staging-', dir=target.parent))
    files = {}
    for relative, meta in plan['files'].items():
        destination = staging / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes((attempt / 'candidate' / relative).read_bytes())
        files[relative] = meta
    verification = staging / 'reports/verification.json'
    verification.write_bytes((attempt / 'verification.json').read_bytes())
    files['reports/verification.json'] = {'sha256': sha256(verification), 'bytes': verification.stat().st_size}
    data = {
        'schema_version': 1, 'kind': 'literaki-release-manifest', 'status': 'FROZEN',
        'package_id': plan.get('package_id'), 'frozen_at': now(),
        'hash_scope': 'wszystkie pliki pakietu poza release-manifest.json (bez rekursji)',
        'files': dict(sorted(files.items())),
        'source_run': {
            'run_name': run.resolve().name,
            'canonical_index_sha256': seal['canonical_index_sha256'],
            'logical_content_sha256': seal['logical_content_sha256'],
            'inputs_manifest_sha256': manifest['inputs']['manifest_sha256'],
            'code': manifest.get('code'),
            # Baza nie jest plikiem pakietu; wiąże ją hash logiczny i hash pliku w archiwum przebiegu.
            'database': {**plan['database'], 'archive': 'build.sqlite w katalogu przebiegu',
                         'file_sha256': seal['database_sha256']}},
        'verification': {'attempt': seal['attempt'], 'verification_sha256': seal['verification_sha256'],
                         'package_plan_sha256': seal['package_plan_sha256'], 'fixture': seal['fixture']},
    }
    write_release_manifest(staging, data)
    for relative, meta in files.items():
        if sha256(staging / relative) != meta['sha256']:
            raise GeneratorError('Bajty w staging różnią się od zweryfikowanych', 4, relative)
    on_disk = {str(p.relative_to(staging)) for p in staging.rglob('*') if p.is_file()}
    if on_disk != set(files) | {'release-manifest.json'}:
        raise GeneratorError('Staging zawiera pliki spoza planu pakietu', 4, str(staging))
    for path in staging.rglob('*'):
        if path.is_file():
            path.chmod(READ_ONLY)
    try:
        rename_noreplace(staging, target)
    except FileExistsError as error:
        raise GeneratorError(f'Cel exportu powstał w trakcie; staging zachowano: {staging.name}', 5,
                             str(target)) from error
    release_sha = sha256(target / 'release-manifest.json')
    manifest['readiness'] = 'FROZEN'
    manifest['export'] = {'output_dir': str(target.resolve()), 'release_manifest_sha256': release_sha,
                          'frozen_at': data['frozen_at']}
    write_json(run / 'manifest.json', manifest)
    (run / 'build.sqlite').chmod(READ_ONLY)
    return {'status': 'FROZEN', 'output_dir': str(target.resolve()),
            'release_manifest_sha256': release_sha, 'files': len(files) + 1}
