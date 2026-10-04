"""Baza na przebieg; jawny schemat i integralność relacji."""
from contextlib import contextmanager
from pathlib import Path
import sqlite3
import unicodedata


@contextmanager
def connect(path, create=False, readonly=False):
    path = Path(path).resolve()
    mode = 'rwc' if create else ('ro' if readonly else 'rw')
    db = sqlite3.connect(path.as_uri() + '?mode=' + mode, uri=True)
    try:
        db.execute('PRAGMA foreign_keys=ON')
        db.execute('PRAGMA cache_size=-65536')
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
