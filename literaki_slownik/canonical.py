"""Jawny JSON, sumy kontrolne i trwałe, atomowe zapisy plików przebiegu."""
import hashlib
import json
import os
from pathlib import Path
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


def _full_sync(descriptor):
    # Na macOS sam fsync nie opróżnia pamięci podręcznej dysku; F_FULLFSYNC tak.
    command = getattr(fcntl, 'F_FULLFSYNC', None) if fcntl is not None else None
    if command is not None:
        try:
            fcntl.fcntl(descriptor, command)
            return
        except OSError:
            pass
    os.fsync(descriptor)


def _sync_directory(directory):
    descriptor = os.open(directory, os.O_RDONLY)
    try:
        _full_sync(descriptor)
    finally:
        os.close(descriptor)


def write_bytes(path, data):
    """Trwały zapis: tmp w tym samym katalogu, F_FULLFSYNC, hak, os.replace, sync katalogu."""
    path = Path(path)
    descriptor, temporary = tempfile.mkstemp(prefix='.' + path.name + '-', dir=path.parent)
    replaced = False
    try:
        with os.fdopen(descriptor, 'wb') as stream:
            stream.write(data)
            stream.flush()
            _full_sync(stream.fileno())
        if _replace_guard is not None:
            _replace_guard(path)
        os.replace(temporary, path)
        replaced = True
        _sync_directory(path.parent)
    finally:
        if not replaced:
            try:
                os.unlink(temporary)
            except OSError:
                # Błąd sprzątania nie może zasłonić pierwotnego wyjątku.
                pass


def write_json(path, value):
    write_bytes(path, (dumps(value) + '\n').encode('utf-8'))
