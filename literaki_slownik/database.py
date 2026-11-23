"""Baza na przebieg; jawny schemat i integralność relacji."""
from contextlib import contextmanager
import os
from pathlib import Path
import sqlite3
import unicodedata
from .canonical import _full_sync

# Tryb `fullfsync` buildu (ADR-020): `build` (4B) = ON przez cały build, `stage_boundaries` (4C) = OFF w etapie
# i F_FULLFSYNC na granicy etapu. Wybrany pomiarem `scripts/measure_fullfsync.py` na T7 (narzut 0,09%).
FULLFSYNC_MODES = ('build', 'stage_boundaries')
FULLFSYNC_MODE = 'build'


def full_sync(db):
    """F_FULLFSYNC na pliku głównej bazy połączenia (granica etapu w trybie `stage_boundaries`)."""
    path = next(row[2] for row in db.execute('PRAGMA database_list') if row[1] == 'main')
    descriptor = os.open(path, os.O_RDONLY)
    try:
        _full_sync(descriptor)
    finally:
        os.close(descriptor)


@contextmanager
def connect(path, create=False, readonly=False, build=False):
    """build=True: tryb FULLFSYNC_MODE (ON przez cały build albo OFF w etapie, R8)."""
    path = Path(path).resolve()
    mode = 'rwc' if create else ('ro' if readonly else 'rw')
    db = sqlite3.connect(path.as_uri() + '?mode=' + mode, uri=True)
    try:
        db.execute('PRAGMA foreign_keys=ON')
        if not readonly:
            # R8: jawnie, nigdy WAL ani synchronous<FULL. Czytelnik (ro) nic nie ustawia.
            db.execute('PRAGMA journal_mode=DELETE')
            db.execute('PRAGMA synchronous=FULL')
            if build and FULLFSYNC_MODE == 'build':
                db.execute('PRAGMA fullfsync=ON')
                db.execute('PRAGMA checkpoint_fullfsync=ON')
        # 4 GB cache stron i tabele tymczasowe w RAM: build i raporty czytają losowo
        # bazę ~22 GB; przy 64 MB proces głównie czekał na dysk (pomiar 2026-10-13: 7× szybciej).
        db.execute('PRAGMA cache_size=-4194304')
        db.execute('PRAGMA temp_store=MEMORY')
        db.create_function('nfc', 1, lambda value: unicodedata.normalize('NFC', value), deterministic=True)
        db.create_function('game_key', 1, lambda value: unicodedata.normalize('NFC', unicodedata.normalize('NFC', value).lower()), deterministic=True)
        if create:
            db.executescript(Path(__file__).with_name('schema.sql').read_text(encoding='utf-8'))
        yield db
        db.commit()
    except BaseException:
        # Po błędzie dysku rollback i close też mogą rzucić; ich błąd nie zasłania pierwotnego (R4).
        try:
            db.rollback()
        except sqlite3.Error:
            pass
        raise
    finally:
        try:
            db.close()
        except sqlite3.Error:
            pass
