"""Zgoda na próg wieku nie nadaje całej analizie poprawności."""
import unittest
from literaki_slownik.decisions import assess_diagnostic
from literaki_slownik.inputs import GeneratorError

RULE='linguistic-standard-age-baseline-v1'

class AgeBaselineTests(unittest.TestCase):
    def test_missing_age_evidence_is_reported_nonblocking_condition_only(self):
        from literaki_slownik.policy import standard_age_baseline_checks
        for labels in ('','techn.','rzad.','daw._dziś_gwar.'):
            checks=standard_age_baseline_checks(labels,'standard')
            self.assertEqual(len(checks),1)
            self.assertEqual(checks[0]['status'],'accept')
            self.assertEqual(checks[0]['age_basis'],'source_classification')
            self.assertEqual(checks[0]['age_certainty'],'not_independently_established')
            self.assertNotIn('contemporary_confirmed',checks[0].values())
            result=assess_diagnostic('dom',labels)
            self.assertIn(RULE,[c['rule_id'] for c in result['language']['standard']['checks']])
            self.assertEqual(result['membership']['standard']['status'],'accept')
        self.assertEqual(standard_age_baseline_checks('','broad'),[])
        with self.assertRaises(GeneratorError):standard_age_baseline_checks('','other')

    def test_age_defaults_do_not_restore_historical_incorrect_or_name_analysis(self):
        from literaki_slownik.policy import standard_age_baseline_checks
        for labels in ('daw.','daw.|daw._dziś_gwar.','arch.,char.','niezal.,przest.'):
            self.assertEqual(standard_age_baseline_checks(labels,'standard'),[])
            self.assertEqual(assess_diagnostic('dom',labels)['language']['standard']['status'],'reject')
        self.assertEqual(assess_diagnostic('dom','niepopr.')['language']['standard']['status'],'reject')
        source=dict(original='Warszawa',lemma_id='Warszawa',raw_tag='subst:sg:nom:f',names='nazwa_geograficzna',qualifiers='')
        self.assertEqual(assess_diagnostic('Warszawa','',source_analyses=[source])['membership']['standard']['status'],'reject')

    def test_age_default_does_not_explain_unknown_qualifier(self):
        from literaki_slownik.reports import qualifier_coverage
        report=qualifier_coverage([('nowa_nieobjaśniona_etykieta',1),('',2)])
        self.assertEqual(report['unmapped_labels'],['nowa_nieobjaśniona_etykieta'])
        self.assertFalse(report['labels'][0]['has_known_condition'])
