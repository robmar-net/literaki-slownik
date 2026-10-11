import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from render_sjp_missing import lemmas, reason  # noqa: E402


class SjpMissingRenderTest(unittest.TestCase):
    def test_reason_absent_from_sgjp(self):
        self.assertEqual(reason({'reject_rules': None}), 'brak w SGJP')

    def test_reason_proper_name_hides_uppercase_and_helper_rule(self):
        row = {'reject_rules': ['game-proper-name-class-v1', 'game-required-uppercase-v1',
                                'semantic-remainder-exhausted-v1']}
        self.assertEqual(reason(row), 'nazwa własna')

    def test_reason_unknown_rule_stays_visible(self):
        self.assertEqual(reason({'reject_rules': ['new-rule-v9']}), '`new-rule-v9`')

    def test_lemmas_drop_inflection_marks_and_duplicates(self):
        row = {'sgjp_lemmas': ['Janusz:Sf', 'Janusz:Sm1', 'List_do_Koryntian', 'a', 'b']}
        self.assertEqual(lemmas(row), 'Janusz, List do Koryntian, a')


if __name__ == '__main__':
    unittest.main()
