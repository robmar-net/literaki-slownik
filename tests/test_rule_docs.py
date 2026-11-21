import unittest

from literaki_slownik import rule_docs


class RuleDocsTests(unittest.TestCase):
    def test_every_code_rule_has_a_description_and_no_extra(self):
        self.assertEqual(rule_docs.problems(rule_docs.load(), rule_docs.code_rule_ids()), [])

    def test_page_is_regenerated(self):
        page = rule_docs.render(rule_docs.load(), base='../../')
        self.assertEqual(rule_docs.PAGE.read_text(encoding='utf-8'), page,
                         'docs/generator/reguly.md nieaktualne: python3 scripts/render_rules.py')

    def test_scan_sees_rules_from_constants_keys_and_policy_json(self):
        ids = rule_docs.code_rule_ids()
        self.assertIn('nie-prefix-degree-v2', ids)          # stała *_RULE
        self.assertIn('linguistic-historical-form-v1', ids)  # klucz 'rule_id'
        self.assertIn('game-documented-resident-capital-v1', ids)  # tylko policy.json

    def test_new_rule_without_description_is_reported(self):
        docs = rule_docs.load()
        found = rule_docs.problems(docs, rule_docs.code_rule_ids() | {'linguistic-new-rule-v1'})
        self.assertEqual(found, ['brak opisu reguły z kodu: linguistic-new-rule-v1'])

    def test_description_of_removed_rule_is_reported(self):
        docs = rule_docs.load()
        ids = rule_docs.code_rule_ids() - {'profile-pl-length-v1'}
        self.assertEqual(rule_docs.problems(docs, ids), ['opis reguły, której nie ma w kodzie: profile-pl-length-v1'])

    def test_policy_version_matches_code(self):
        from literaki_slownik.policy import VERSION
        self.assertEqual(rule_docs.load()['policy_version'], VERSION)


if __name__ == '__main__':
    unittest.main()
