"""Raport całej zapisanej populacji zachowuje homonimy i unknown."""
import unittest
from tests import test_unknown_report as fixtures
from literaki_slownik.reports import persisted_filter_impact
from literaki_slownik.inputs import GeneratorError

class PersistedFilterImpactTests(unittest.TestCase):
    def test_rejected_analysis_does_not_remove_accepted_homonym(self):
        helper=fixtures.UnknownReportTest();db=helper.database();self.addCleanup(helper.doCleanups)
        before=db.total_changes
        result=persisted_filter_impact(db)
        for variant in ('broad','standard'):
            report=result['variants'][variant]
            self.assertEqual(report['total'],{'keys':2,'analyses':3})
            self.assertEqual(report['combined'],{'rejected_analyses':1,'rejected_keys':0})
            self.assertEqual(report['standalone']['game']['rejected_analyses'],1)
            self.assertEqual(report['assessed_key_statuses'],{'accept':1,'unresolved':1})
            self.assertEqual(report['rule_order'], sorted(report['rule_order']))
        self.assertEqual(db.total_changes,before)
        self.assertEqual(result,persisted_filter_impact(db))
        self.assertTrue(result['full_qualification_pending'])

    def test_incomplete_or_corrupt_persisted_population_refused(self):
        for sql in ("delete from variant_decision where variant='broad'",
                    "update decision_payload set assessment='{}'",
                    "update variant_decision set membership_status='accept' where analysis_key='b1'"):
            helper=fixtures.UnknownReportTest();db=helper.database();self.addCleanup(helper.doCleanups)
            db.execute(sql)
            with self.subTest(sql=sql),self.assertRaises(GeneratorError):persisted_filter_impact(db)

    def test_build_report_is_deterministic_and_not_release(self):
        import tempfile,json
        from pathlib import Path
        from tests.test_build import BuildTests
        from literaki_slownik.build import build
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);m=BuildTests().manifest(root,'#</COPYRIGHT>\njam\tjama\tsubst:pl:gen:f\t\t\njam\tjam\tfrag\t\t\n')
            runs=[root/'a',root/'b']
            for r in runs:build(m,r)
            a,b=[json.loads((r/'reports/filter-impact.json').read_text()) for r in runs]
            self.assertEqual(a,b)
            self.assertEqual(a['variants']['standard']['total']['analyses'],2)
            self.assertEqual(a['variants']['standard']['combined']['rejected_keys'],0)
            self.assertEqual(json.loads((runs[0]/'manifest.json').read_text())['readiness'],'INCOMPLETE')

    def test_changed_rule_attribution_with_valid_hash_is_refused(self):
        import json,hashlib
        from literaki_slownik.canonical import dumps
        helper=fixtures.UnknownReportTest();db=helper.database();self.addCleanup(helper.doCleanups)
        key,encoded=db.execute("select p.assessment_key,p.assessment from decision_payload p join variant_decision d using(assessment_key) where d.analysis_key='a1' limit 1").fetchone()
        value=json.loads(encoded)
        for check in value['membership']['checks']:
            if check['status']=='reject':check['rule_id']='wrong-attribution'
        new=dumps(value);digest=hashlib.sha256(new.encode()).hexdigest()
        db.execute('insert into decision_payload values (?,?)',(digest,new))
        db.execute('update variant_decision set assessment_key=? where assessment_key=?',(digest,key))
        with self.assertRaises(GeneratorError):persisted_filter_impact(db)
