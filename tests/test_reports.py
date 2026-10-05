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


class QualifierCoverageTests(unittest.TestCase):
    def report(self, fields):
        from literaki_slownik.reports import qualifier_coverage
        return qualifier_coverage(iter(fields))

    def test_literal_labels_and_mixed_fields_without_double_counting(self):
        report = self.report([('rzad.|nieznane|rzad.', 3), ('nieznane', 2), ('', 5), ('pot.,nieznane', 1)])
        self.assertEqual(report['totals'], {'compact_interpretations': 11, 'fields': 4, 'literal_labels': 3,
                                          'records_with_any_condition': 3,
                                          'records_with_unmapped_label': 6,
                                          'records_without_qualifiers': 5})
        self.assertEqual(report['unmapped_labels'], ['nieznane', 'pot.,nieznane'])
        labels = {row['label']: row for row in report['labels']}
        self.assertEqual(labels['rzad.']['compact_interpretations'], 3)
        self.assertEqual(labels['nieznane']['compact_interpretations'], 5)
        fields = {row['qualifiers']: row for row in report['fields']}
        self.assertEqual(fields['rzad.|nieznane|rzad.']['unmapped_labels'], ['nieznane'])
        self.assertEqual(fields['']['labels'], [])
        self.assertTrue(report['full_qualification_pending'])

    def test_known_conditions_are_partial_and_variant_specific(self):
        report = self.report([('daw.,z_D.', 2), ('niepopr.', 1), ('techn.', 4)])
        fields = {row['qualifiers']: row for row in report['fields']}
        self.assertEqual(fields['daw.,z_D.']['condition_assessment']['standard']['status'], 'reject')
        self.assertEqual(fields['daw.,z_D.']['condition_assessment']['broad']['status'], 'accept')
        rules = fields['daw.,z_D.']['condition_assessment']['standard']['checks']
        self.assertTrue(any(c.get('required_context') == 'adjective_genitive' for c in rules))
        self.assertEqual(fields['niepopr.']['condition_assessment']['broad']['status'], 'reject')
        self.assertEqual(report['scope'], 'qualifier_conditions_only_not_full_qualification')
        self.assertNotIn('list_membership', report)

    def test_unknown_or_empty_is_not_condition_acceptance(self):
        report = self.report([('', 2), ('nieznane', 1)])
        for row in report['fields']:
            for variant in ('broad', 'standard'):
                self.assertEqual(row['condition_assessment'][variant]['status'], 'unresolved')
        empty = self.report([])
        self.assertEqual(empty['coverage'], 'EMPTY_NOT_COVERAGE')
        self.assertEqual(empty['totals']['compact_interpretations'], 0)

    def test_deterministic_regardless_of_inventory_order(self):
        fields = [('z_D.|rzad.', 2), ('med.', 1), ('', 3)]
        self.assertEqual(self.report(fields), self.report(reversed(fields)))

    def test_invalid_inventory_refused(self):
        for fields in [[('med.', 1), ('med.', 2)], [('med.', True)], [('med.', 0)],
                       [('med.', -1)], [(None, 1)], [('med.', '1')], [('med.', 1, 2)]]:
            with self.subTest(fields=fields), self.assertRaises(GeneratorError):
                self.report(fields)

    def test_probe_command_reads_database_and_is_repeatable(self):
        import json
        import sqlite3
        import subprocess
        import sys
        import tempfile
        from pathlib import Path
        from literaki_slownik.canonical import sha256
        script = Path('scripts/probe_generator_evidence.py').resolve()
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'db.sqlite'
            with sqlite3.connect(path) as db:
                db.execute('create table interpretation (qualifiers TEXT)')
                db.executemany('insert into interpretation values (?)', [('rzad.',), ('z_D.',), ('nieznane',)])
            before = sha256(path)
            args = [sys.executable, str(script), '--mode', 'qualifier-conditions', '--database', str(path)]
            first = subprocess.run(args, cwd=directory, capture_output=True, text=True)
            self.assertEqual(first.returncode, 0, first.stderr)
            second = subprocess.run(args, cwd=directory, capture_output=True, text=True)
            self.assertEqual(second.returncode, 0, second.stderr)
            self.assertEqual(first.stdout, second.stdout)
            self.assertEqual(json.loads(first.stdout)['unmapped_labels'], ['nieznane'])
            self.assertEqual(sha256(path), before)
