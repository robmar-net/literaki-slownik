"""Wspólne pomocniki plików dysku roboczego (#22): blokady, kasowanie drzew, rozmiar, „ścieżka wewnątrz”.

Blokady (flock, zwalniane przez jądro razem z procesem):
  logs/<nazwa>.lock           nadzorca (`scripts/build_supervised.py`), przez cały czas pracy;
  logs/<nazwa>.promote.lock   promocja (`scripts/promote_run.py`);
  <katalog symlinku>/.<nazwa>.build.lock  build i `build --resume` (zwykle `data/work/`).
Blokada buildu leży obok symlinku przebiegu, a nie w `logs/`, bo build działa też poza repo (fikstury testów).

Kasowanie drzewa jest wznawialne: najpierw zmiana nazwy na `.<nazwa>.deleting` w tym samym katalogu (atomowa,
ten sam wolumen), potem `rmtree`. Przerwane kasowanie zostawia tylko `.<nazwa>.deleting`, które dokańcza
`finish_deleting` przy następnym uruchomieniu (promocja, `clean_work.py --apply`).
"""
from contextlib import contextmanager
import fcntl
import os
from pathlib import Path
import shutil
import stat

from .inputs import GeneratorError

DELETING = '.deleting'
BUILD_LOCK = '.build.lock'


def supervisor_lock(logs, name):
    return Path(logs) / f'{name}.lock'


def promote_lock(logs, name):
    return Path(logs) / f'{name}.promote.lock'


def build_lock(run_dir):
    """Blokada buildu przebiegu: `.<nazwa>.build.lock` obok symlinku (albo katalogu) przebiegu."""
    run = Path(run_dir).absolute()
    return run.parent / f'.{run.name}{BUILD_LOCK}'


def is_build_lock(name):
    return name.startswith('.') and name.endswith(BUILD_LOCK)


def is_deleting(name):
    return name.startswith('.') and name.endswith(DELETING) and len(name) > len(DELETING) + 1


def lock_held(path):
    """Czy ktoś trzyma flock na pliku blokady (pliku nie tworzy)."""
    try:
        stream = open(path, 'rb')
    except OSError:
        return False
    with stream:
        try:
            fcntl.flock(stream, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError:
            return True
        fcntl.flock(stream, fcntl.LOCK_UN)
        return False


@contextmanager
def hold_lock(path, message):
    """flock na pliku blokady przez czas bloku; zajęta → GeneratorError 4 (nic nie zmieniono)."""
    stream = open(path, 'a+b')
    try:
        try:
            fcntl.flock(stream, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError as error:
            raise GeneratorError(message, 4, str(path)) from error
        yield
    finally:
        stream.close()


def is_within(path, root, *, strict=False):
    """Czy path (po realpath) leży w root (po realpath); strict=True wyklucza sam root."""
    path, root = os.path.realpath(path), os.path.realpath(root)
    if path == root:
        return not strict
    return path.startswith(root.rstrip(os.sep) + os.sep)


def tree_size(path):
    """Suma st_size drzewa bez podążania za symlinkami; nieczytelne wpisy pomija."""
    total = 0
    try:
        total = os.lstat(path).st_size
        if stat.S_ISDIR(os.lstat(path).st_mode):
            for current, names, files in os.walk(path, followlinks=False):
                for name in names + files:
                    try:
                        total += os.lstat(Path(current) / name).st_size
                    except OSError:
                        pass
    except OSError:
        pass
    return total


def remove_tree(path):
    """`rmtree` drzewa z plikami tylko do odczytu (`chmod u+rw`, symlinków nie zmienia); znikający wpis pomija."""
    def writable(function, target, info):
        error = info[1] if isinstance(info, tuple) else info
        if isinstance(error, FileNotFoundError):
            return  # Wpis skasował już równoległy albo przerwany przebieg.
        os.chmod(os.path.dirname(target), stat.S_IRWXU)
        if not os.path.islink(target):
            os.chmod(target, stat.S_IMODE(os.lstat(target).st_mode) | stat.S_IWUSR | stat.S_IRUSR)
        function(target)
    try:
        if not os.path.islink(path):
            os.chmod(path, stat.S_IMODE(os.lstat(path).st_mode) | stat.S_IRWXU)
    except FileNotFoundError:
        return
    shutil.rmtree(path, onexc=writable)


def deleting_name(path):
    path = Path(path)
    return path.parent / f'.{path.name}{DELETING}'


def delete_tree(path):
    """Wznawialne kasowanie: rename na `.<nazwa>.deleting` (ten sam katalog), sync katalogu, rmtree.

    Symlink albo zwykły plik znika od razu (`unlink`)."""
    from .canonical import sync_directory
    path = Path(path)
    if path.is_symlink() or not path.is_dir():
        os.unlink(path)
        return
    target = deleting_name(path)
    if os.path.lexists(target):
        remove_tree(target)  # Resztka wcześniejszego przerwania pod tą samą nazwą.
    os.rename(path, target)
    sync_directory(path.parent)
    remove_tree(target)


def finish_deleting(directory):
    """Dokańcza przerwane kasowania `.*.deleting` w katalogu; zwraca listę dokończonych nazw."""
    finished = []
    try:
        entries = sorted(Path(directory).iterdir())
    except FileNotFoundError:
        return finished
    for entry in entries:
        if is_deleting(entry.name):
            if entry.is_symlink() or not entry.is_dir():
                try:
                    os.unlink(entry)
                except FileNotFoundError:
                    pass
            else:
                remove_tree(entry)
            finished.append(entry.name)
    return finished

