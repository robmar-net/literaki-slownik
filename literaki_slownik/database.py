"""Baza na przebieg; jawny schemat i integralność relacji."""
from contextlib import contextmanager
from pathlib import Path
import sqlite3
import unicodedata

# Tryb `fullfsync` buildu (ADR-020): `build` (4B) = ON przez cały build, `stage_boundaries` (4C) = OFF w etapie
# i F_FULLFSYNC na granicy etapu. Wybrany pomiarem `scripts/measure_fullfsync.py` na T7. Czyta go grupa 8.
FULLFSYNC_MODES = ('build', 'stage_boundaries')
FULLFSYNC_MODE = 'build'


@contextmanager
def connect(path, create=False, readonly=False):
    path = Path(path).resolve()
    mode = 'rwc' if create else ('ro' if readonly else 'rw')
    db = sqlite3.connect(path.as_uri() + '?mode=' + mode, uri=True)
    try:
        db.execute('PRAGMA foreign_keys=ON')
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
        db.rollback()
        raise
    finally:
        db.close()
