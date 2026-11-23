"""Jawny JSON, sumy kontrolne i trwałe, atomowe zapisy plików przebiegu."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import stat
import tempfile

try:
    import fcntl
except ImportError:  # poza POSIX
    fcntl = None


def dumps(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False)


def load_json(path):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError(f'Powtórzony klucz JSON: {key}')
            result[key] = value
        return result
    return json.loads(Path(path).read_text(encoding='utf-8'), object_pairs_hook=unique,
                      parse_constant=lambda value: (_ for _ in ()).throw(ValueError(value)))


def sha256(path):
    digest = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


# Wywoływany z docelową ścieżką tuż przed os.replace; strażnik wolumenu (G3) może przerwać zapis.
_replace_guard = None


def set_replace_guard(guard):
    """Ustawia hak przed os.replace (None wyłącza) i zwraca poprzedni."""
    global _replace_guard
    previous, _replace_guard = _replace_guard, guard
    return previous


def full_sync(descriptor):
    """F_FULLFSYNC deskryptora (macOS), a gdy go nie ma albo zawiedzie: fsync."""
    # Na macOS sam fsync nie opróżnia pamięci podręcznej dysku; F_FULLFSYNC tak.
    command = getattr(fcntl, 'F_FULLFSYNC', None) if fcntl is not None else None
    if command is not None:
        try:
            fcntl.fcntl(descriptor, command)
            return
        except OSError:
            pass
    os.fsync(descriptor)


def sync_directory(directory):
    """Trwały wpis katalogu po utworzeniu, zamianie albo skasowaniu pliku."""
    descriptor = os.open(directory, os.O_RDONLY)
    try:
        full_sync(descriptor)
    finally:
        os.close(descriptor)


def _durable(path, fill, before_replace=None):
    """tmp w katalogu celu, fill(stream), F_FULLFSYNC, before_replace(tmp), hak, os.replace, sync katalogu."""
    path = Path(path)
    descriptor, temporary = tempfile.mkstemp(prefix='.' + path.name + '-', dir=path.parent)
    replaced = False
    try:
        with os.fdopen(descriptor, 'wb') as stream:
            fill(stream)
            stream.flush()
            full_sync(stream.fileno())
        if before_replace is not None:
            before_replace(temporary)
        if _replace_guard is not None:
            _replace_guard(path)
        os.replace(temporary, path)
        replaced = True
        sync_directory(path.parent)
    finally:
        if not replaced:
            try:
                os.unlink(temporary)
            except OSError:
                # Błąd sprzątania nie może zasłonić pierwotnego wyjątku.
                pass


def write_bytes(path, data):
    """Trwały zapis: tmp w tym samym katalogu, F_FULLFSYNC, hak, os.replace, sync katalogu."""
    _durable(path, lambda stream: stream.write(data))


def copy_durable(source, target):
    """Trwała kopia pliku jak write_bytes, z trybem i czasami (atime, mtime) źródła."""
    info = os.lstat(source)

    def fill(stream):
        with open(source, 'rb') as reader:
            shutil.copyfileobj(reader, stream, 1024 * 1024)

    def keep_metadata(temporary):
        os.chmod(temporary, stat.S_IMODE(info.st_mode))
        os.utime(temporary, ns=(info.st_atime_ns, info.st_mtime_ns))
    _durable(target, fill, keep_metadata)


def write_json(path, value):
    write_bytes(path, (dumps(value) + '\n').encode('utf-8'))
