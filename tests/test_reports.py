"""Efekty filtrów liczone po analizach, bez utraty alternatywnych homonimów."""
import unittest

from literaki_slownik.decisions import assess_analysis
from literaki_slownik.inputs import GeneratorError
from literaki_slownik.reports import filter_impact


def analysis(word, rejected=(), pending=False):
    checks=[{'rule_id':rule,'status':'reject','message':'Fixture','evidence':['fixture']} for rule in rejected]
    checks += [{'rule_id':'remaining','status':'unresolved' if pending else 'accept',
                'message':'Fixture','evidence':['fixture']}]
    return assess_analysis(word,language={v:checks for v in ('broad','standard')},
                          game_checks=[{'rule_id':'game-ok','status':'accept','message':'Fixture','evidence':['fixture']}])


class FilterReportTests(unittest.TestCase):
    def test_independent_sequential_combined_homonyms_and_overlap(self):
        groups=[{'key':'aa','analyses':[analysis('aa',['A','B'])]},
                {'key':'bb','analyses':[analysis('bb',['A']),analysis('bb',['B'])]},
                {'key':'cc','analyses':[analysis('cc',['A','B'])]},
                {'key':'dd','analyses':[analysis('dd')]},
                {'key':'ee','analyses':[analysis('ee',pending=True)]}]
        report=filter_impact(iter(groups),'standard',['A','B'])
        self.assertEqual(report['total'],{'keys':5,'analyses':6})
        self.assertEqual(report['standalone']['A'],{'rejected_analyses':3,'rejected_keys':2})
        self.assertEqual(report['standalone']['B'],{'rejected_analyses':3,'rejected_keys':2})
        self.assertEqual(report['sequential']['A'],{'new_rejected_analyses':3,'new_rejected_keys':2,
                                                   'cumulative_rejected_analyses':3,'cumulative_rejected_keys':2})
        self.assertEqual(report['sequential']['B'],{'new_rejected_analyses':1,'new_rejected_keys':1,
                                                   'cumulative_rejected_analyses':4,'cumulative_rejected_keys':3})
        self.assertEqual(report['combined'],{'rejected_analyses':4,'rejected_keys':3})
        self.assertEqual(report['assessed_key_statuses'],{'accept':1,'reject':3,'unresolved':1})

    def test_reordering_changes_sequential_attribution_not_combined(self):
        groups=[{'key':'aa','analyses':[analysis('aa',['A','B'])]}]
        first=filter_impact(groups,'standard',['A','B'])
        second=filter_impact(groups,'standard',['B','A'])
        self.assertEqual(first['combined'],second['combined'])
        self.assertEqual(first['standalone'],second['standalone'])
        self.assertEqual(first['sequential']['A']['new_rejected_keys'],1)
        self.assertEqual(second['sequential']['A']['new_rejected_keys'],0)

    def test_unresolved_does_not_mean_rejection_or_verified(self):
        report=filter_impact([{'key':'aa','analyses':[analysis('aa',pending=True)]}],'standard',['A'])
        self.assertEqual(report['combined']['rejected_keys'],0)
        self.assertEqual(report['assessed_key_statuses']['unresolved'],1)
        self.assertEqual(report['scope'],'provided_analyses_only_not_release_membership')
        empty=filter_impact([], 'standard',['A'])
        self.assertEqual(empty['coverage'],'EMPTY_NOT_COVERAGE')

    def test_missing_rejection_filter_and_inconsistent_status_refused(self):
        with self.assertRaises(GeneratorError):
            filter_impact([{'key':'aa','analyses':[analysis('aa',['B'])]}],'standard',['A'])
        malformed=analysis('aa',['A'])
        malformed['membership']['standard']['status']='accept'
        with self.assertRaises(GeneratorError):
            filter_impact([{'key':'aa','analyses':[malformed]}],'standard',['A'])

    def test_unsorted_repeated_or_mismatched_keys_and_bad_options_refused(self):
        for groups in [[{'key':'bb','analyses':[analysis('bb')]},{'key':'aa','analyses':[analysis('aa')]}],
                       [{'key':'aa','analyses':[analysis('aa')]},{'key':'aa','analyses':[analysis('aa')]}],
                       [{'key':'aa','analyses':[analysis('bb')]}], [{'key':'aa','analyses':[]}]]:
            with self.subTest(groups=groups),self.assertRaises(GeneratorError):
                filter_impact(groups,'standard',['A'])
        for variant,order in [('unknown',['A']),('standard',[]),('standard',['A','A'])]:
            with self.subTest(variant=variant,order=order),self.assertRaises(GeneratorError):
                filter_impact([] ,variant,order)
