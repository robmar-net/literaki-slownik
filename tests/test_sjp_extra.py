import sqlite3
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from benchmark_sjp import KWJP_FORMS  # noqa: E402
from render_sjp_extra import shown, source, table_row  # noqa: E402
from sjp_missing_top import kwjp_freq  # noqa: E402


class SjpExtraTest(unittest.TestCase):
    def test_source_sgjp_and_construction(self):
        self.assertEqual(source({'sources': ['nie-prefix-degree-v1', 'sgjp']}), 'nie- + słowo z SGJP, SGJP')

    def test_source_unknown_rule_stays_visible(self):
        self.assertEqual(source({'sources': ['new-rule-v9']}), '`new-rule-v9`')

    def test_broad_row_marks_standard(self):
        row = {'word': 'paweł', 'kwjp': 10450, 'sgjp_lemmas': ['paweł'], 'sources': ['sgjp'], 'in_standard': True}
        self.assertEqual(table_row(1, row, 'broad'), '| 1 | paweł | 10 450 | paweł | SGJP | tak |')
        self.assertEqual(table_row(1, row, 'standard'), '| 1 | paweł | 10 450 | paweł | SGJP |')

    def test_other_game_name_is_hidden(self):
        word = bytes.fromhex('736372616262' '6c65').decode()
        self.assertNotEqual(shown(word), word)
        self.assertEqual(shown('paweł'), 'paweł')

    def test_kwjp_freq_sums_one_source_only(self):
        db = sqlite3.connect(':memory:')
        db.execute('create table corpus_evidence (source_id, unit_1, freq)')
        db.executemany('insert into corpus_evidence values (?,?,?)',
                       [(KWJP_FORMS, 'ewa', 3), (KWJP_FORMS, 'ewa', 2), (KWJP_FORMS, None, 9), ('other', 'ewa', 7)])
        self.assertEqual(kwjp_freq(db), {'ewa': 5})


if __name__ == '__main__':
    unittest.main()
