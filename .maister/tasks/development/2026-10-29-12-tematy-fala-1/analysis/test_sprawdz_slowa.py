"""Testy kontroli słów oczywistych (#12, W10.2) na małej bazie SQLite.

Uruchomienie: python3 -m unittest discover -s <T>/analysis -p 'test_sprawdz_slowa.py'
"""
from pathlib import Path
import sqlite3
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import sprawdz_slowa  # noqa: E402

# (lemma_base, [(forma, tag)])
LEKSEMY = [
    ('kot', [('kot', 'subst:sg:nom:m2'), ('kota', 'subst:sg:gen:m2'), ('koty', 'subst:pl:nom:m2')]),
    ('nuta', [('nuta', 'subst:sg:nom:f'), ('nuty', 'subst:pl:nom:f')]),
    ('pod', [('pod', 'prep:inst')]),
    ('zyzol', [('zyzol', 'subst:sg:nom:m1'), ('zyzola', 'subst:sg:gen:m1')]),
]
STANDARD = {'kot', 'kota', 'koty', 'nuta', 'nuty', 'pod'}


def baza(path):
    with sqlite3.connect(path) as db:
        db.executescript(
            'CREATE TABLE lexeme (id INTEGER PRIMARY KEY, source_id TEXT, lemma_id TEXT, lemma_base TEXT);'
            'CREATE TABLE surface_form (id INTEGER PRIMARY KEY, original TEXT UNIQUE, nfc TEXT, game_key TEXT,'
            ' length INTEGER);'
            'CREATE TABLE interpretation (id INTEGER PRIMARY KEY, source_id TEXT, first_row INTEGER,'
            ' form_id INTEGER, lexeme_id INTEGER, tag TEXT, names TEXT, qualifiers TEXT);'
            'CREATE TABLE derivation_candidate (candidate_key TEXT, game_key TEXT, lemma_id TEXT);'
            'CREATE TABLE derivation_component (candidate_key TEXT, source_id TEXT, kind TEXT);')
        forms = {}
        for ident, (lemma, rows) in enumerate(LEKSEMY, 1):
            db.execute('INSERT INTO lexeme VALUES (?,?,?,?)', (ident, 'sgjp', f'{lemma}:1', lemma))
            for form, tag in rows:
                fid = forms.setdefault(form, len(forms) + 1)
                db.execute('INSERT OR IGNORE INTO surface_form VALUES (?,?,?,?,?)', (fid, form, form, form, len(form)))
                db.execute('INSERT INTO interpretation (source_id,first_row,form_id,lexeme_id,tag,names,qualifiers)'
                           " VALUES ('sgjp',1,?,?,?,'','')", (fid, ident, tag))


class SprawdzSlowa(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.db = Path(self.tmp.name) / 'build.sqlite'
        baza(self.db)

    def tearDown(self):
        self.tmp.cleanup()

    def sprawdz(self, words):
        return sprawdz_slowa.sprawdz(self.db, STANDARD, STANDARD, {'t': words})['t']

    def test_lemat_z_klasa_i_forma_w_standard_przechodzi(self):
        self.assertEqual(self.sprawdz(['kot', 'nuta']), {'kot': None, 'nuta': None})

    def test_forma_ktora_nie_jest_lematem_odpada(self):
        # Wzór `nuty`, `zawody`: forma jest w STANDARD, ale nie jest `lemma_base`.
        self.assertEqual(self.sprawdz(['nuty', 'koty']), {'nuty': 'FORMA_NIE_LEMAT', 'koty': 'FORMA_NIE_LEMAT'})

    def test_klasa_spoza_czesci_mowy_albo_brak_formy_w_standard_odpada(self):
        self.assertEqual(self.sprawdz(['pod', 'zyzol', 'brak']),
                         {'pod': 'KLASA_SPOZA', 'zyzol': 'POZA_STANDARD', 'brak': 'BRAK_LEKSEMU'})


if __name__ == '__main__':
    unittest.main()
