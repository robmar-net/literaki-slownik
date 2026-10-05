import unittest


class PersistedDecisionTests(unittest.TestCase):
    def test_shared_reasons_keep_each_original_profile_and_complete_decision(self):
        import tempfile
        from pathlib import Path
        from tests.test_build import BuildTests
        from literaki_slownik.build import build
        from literaki_slownik.database import connect
        from literaki_slownik.decisions import persisted_assessments,assess_diagnostic
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);p=BuildTests().manifest(root,'#</COPYRIGHT>\nkot\tkot\tsubst:sg:nom:m2\t\t\npies\tpies\tsubst:sg:nom:m2\t\t\n')
            run=root/'run';build(p,run)
            with connect(run/'build.sqlite',readonly=True) as db:
                self.assertEqual(db.execute('select count(*) from decision_payload').fetchone()[0],2)
                for variant in ('broad','standard'):
                    self.assertEqual(db.execute('select count(distinct assessment_key) from variant_decision where variant=?',(variant,)).fetchone()[0],1)
                for word in ('kot','pies'):
                    row,=persisted_assessments(db,word,'standard')
                    live=assess_diagnostic(word,'',source_analyses=[dict(original=word,lemma_id=word,raw_tag='subst:sg:nom:m2',names='',qualifiers='')])
                    self.assertEqual(row['assessment']['profile'],live['profile'])
                    self.assertEqual(row['assessment']['membership'],live['membership']['standard'])
                self.assertEqual(db.total_changes,0)

    def test_all_expansions_and_homonyms_preserved_with_stable_content_keys(self):
        import tempfile
        from pathlib import Path
        from tests.test_build import BuildTests
        from literaki_slownik.build import build
        from literaki_slownik.database import connect
        from literaki_slownik.decisions import materialize_assessments,persisted_assessments
        from literaki_slownik.reports import logical_content_report
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            p=BuildTests().manifest(root,'#</COPYRIGHT>\nbiało\tbiały\tadja\t\t\nbiało\tbiało\tadv:pos\t\t\njam\tjama\tsubst:pl:gen:f\t\t\nkot\tkot\tsubst:sg:nom.acc:m2\t\t\nja\tja\tppron12:sg:nom:m1:pri\t\t\nm\tbyć:A\taglt:sg:pri:imperf:nwok\t\t\n')
            run=root/'run';build(p,run)
            with connect(run/'build.sqlite') as db:
                first=materialize_assessments(db,batch_size=2)
                self.assertEqual(first['source_analyses'],7)
                self.assertEqual(first['construction_analyses'],1)
                self.assertEqual(first['variant_decisions'],16)
                self.assertEqual(db.execute("select count(*) from analysis where expanded_tag in ('subst:sg:nom:m2','subst:sg:acc:m2')").fetchone()[0],2)
                statuses=db.execute("select a.original,a.expanded_tag,d.game_status from analysis a join variant_decision d using(analysis_key) where d.variant='standard' and a.original in ('biało','jam') order by a.original,a.expanded_tag").fetchall()
                self.assertEqual(statuses,[('biało','adja','reject'),('biało','adv:pos','unresolved'),('jam','aglt:sg:pri:imperf:nwok','reject'),('jam','subst:pl:gen:f','unresolved')])
                before=logical_content_report(db)
                second=materialize_assessments(db,batch_size=3)
                self.assertEqual(second['new_analyses'],0)
                self.assertEqual(second['new_decisions'],0)
                self.assertEqual(logical_content_report(db),before)
                self.assertEqual(db.execute('pragma foreign_key_check').fetchall(),[])

    def test_policy_change_refuses_overwriting_previous_snapshot(self):
        import tempfile
        from pathlib import Path
        from unittest.mock import patch
        from tests.test_build import BuildTests
        from literaki_slownik.build import build
        from literaki_slownik.database import connect
        from literaki_slownik.decisions import materialize_assessments,persisted_assessments
        from literaki_slownik.inputs import GeneratorError
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);p=BuildTests().manifest(root,'#</COPYRIGHT>\nkot\tkot\tsubst:sg:nom:m2\t\t\n')
            run=root/'run';build(p,run)
            with connect(run/'build.sqlite') as db:
                materialize_assessments(db)
                with patch('literaki_slownik.decisions.POLICY_VERSION','future'):
                    with self.assertRaises(GeneratorError):materialize_assessments(db)
                db.execute("update decision_payload set assessment='{}'")
                with self.assertRaises(GeneratorError):materialize_assessments(db)
                with self.assertRaises(GeneratorError):persisted_assessments(db,'kot','standard')

from literaki_slownik.decisions import assessment, assess_analysis, aggregate
from literaki_slownik.inputs import GeneratorError


def checks(status):
    return [{'rule_id': 'synthetic-v1', 'status': status,
             'message': 'Własna fikstura', 'evidence': ['synthetic:own']}]


def analysis(language, game, form='kot'):
    return assess_analysis(form, language={'broad': checks(language), 'standard': checks(language)},
                           game_checks=checks(game))


class DecisionsTests(unittest.TestCase):
    def test_release_scope_excludes_candidate_without_lexical_rejection_or_homonym_loss(self):
        outside = assess_analysis('kołoń', language={v:checks('unresolved') for v in ('broad','standard')},
                                  game_checks=checks('accept'), scope_checks=checks('reject'))
        self.assertEqual(outside['language']['standard']['status'],'unresolved')
        self.assertEqual(outside['game']['status'],'accept')
        self.assertEqual(outside['release_scope']['status'],'reject')
        self.assertEqual(outside['membership']['standard']['status'],'reject')
        direct = analysis('accept','accept','kołoń')
        self.assertEqual(direct['release_scope']['status'],'accept')
        self.assertEqual(aggregate([outside,direct],'standard')['status'],'accept')

    def test_known_reject_retains_unknown_and_empty_is_not_accept(self):
        value = assessment(checks('unresolved') + checks('reject'))
        self.assertEqual(value['status'], 'reject')
        self.assertEqual(len(value['checks']), 2)
        self.assertEqual(assessment([])['status'], 'unresolved')
        with self.assertRaises(GeneratorError):
            assessment(checks('maybe'))

    def test_all_conditions_must_hold_in_same_analysis(self):
        values = [analysis('accept', 'reject'), analysis('reject', 'accept')]
        self.assertEqual(aggregate(values, 'standard')['status'], 'reject')
        values.append(analysis('accept', 'accept'))
        self.assertEqual(aggregate(values, 'standard')['status'], 'accept')
        self.assertEqual(len(values), 3)
        self.assertEqual(aggregate([analysis('unresolved', 'accept')], 'broad')['status'], 'unresolved')
        self.assertEqual(aggregate([], 'broad')['status'], 'absent')

    def test_uppercase_reject_does_not_remove_lexical_assessment(self):
        value = analysis('accept', 'accept', 'PCV')
        self.assertEqual(value['language']['standard']['status'], 'accept')
        self.assertEqual(value['game']['status'], 'reject')
        self.assertEqual(value['profile']['status'], 'reject')
        self.assertEqual(value['membership']['standard']['status'], 'reject')
        self.assertEqual(value['original'], 'PCV')

    def test_standard_cannot_accept_an_analysis_rejected_by_broad(self):
        with self.assertRaises(GeneratorError):
            assess_analysis('kot', language={'broad': checks('reject'), 'standard': checks('accept')},
                            game_checks=checks('accept'))

    def test_empty_game_assessment_and_cross_word_aggregation_are_not_acceptance(self):
        value = assess_analysis('kot', language={'broad': checks('accept'), 'standard': checks('accept')},
                                game_checks=[])
        self.assertEqual(value['game']['status'], 'unresolved')
        self.assertEqual(value['membership']['standard']['status'], 'unresolved')
        with self.assertRaises(GeneratorError):
            aggregate([analysis('accept', 'accept', 'kot'), analysis('accept', 'accept', 'pies')], 'standard')
