import tempfile
import unittest
from pathlib import Path
import sqlite3
from literaki_slownik.database import connect


class DatabaseTests(unittest.TestCase):
    def test_foreign_keys_and_version(self):
        with tempfile.TemporaryDirectory() as directory:
            with connect(Path(directory) / 'db.sqlite', create=True) as db:
                self.assertEqual(db.execute('pragma foreign_keys').fetchone()[0], 1)
                self.assertEqual(db.execute('pragma user_version').fetchone()[0], 2)
                with self.assertRaises(sqlite3.IntegrityError):
                    db.execute('insert into sgjp_record values (?, ?, ?, ?, ?, ?, ?)', ('missing', 1, 'kot', 'kot', 'subst', '', ''))

    def test_large_page_cache(self):
        # Pełny build to głównie losowe odczyty bazy ~22 GB; mały cache czekał na dysk.
        with tempfile.TemporaryDirectory() as directory:
            with connect(Path(directory) / 'db.sqlite', create=True) as db:
                self.assertEqual(db.execute('pragma cache_size').fetchone()[0], -4 * 1024 * 1024)
                self.assertEqual(db.execute('pragma temp_store').fetchone()[0], 2)
