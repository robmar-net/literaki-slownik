"""Niewiadome pozostają widoczne mimo odmowy i dopuszczonego homonimu."""
import hashlib
import json
import sqlite3
import unittest

from literaki_slownik.canonical import dumps
from literaki_slownik.decisions import assess_analysis
from literaki_slownik.inputs import GeneratorError
from literaki_slownik.reports import unresolved_report


class UnknownReportTest(unittest.TestCase):
    def database(self):
        db = sqlite3.connect(':memory:')
        self.addCleanup(db.close)
        db.executescript('''
            create table analysis(analysis_key primary key, game_key);
            create table decision_payload(assessment_key primary key, assessment);
            create table variant_decision(analysis_key, variant, language_status, game_status,
                profile_status, scope_status, membership_status, assessment_key,
                primary key(analysis_key,variant));
        ''')
        check = lambda status, rule: dict(status=status, rule_id=rule, message='Fixture', evidence=[])
        for akey, word, pending, rejected in [('a1', 'aa', True, True),
                                              ('a2', 'aa', False, False),
                                              ('b1', 'bb', True, False)]:
            lang = [check('unresolved' if pending else 'accept', 'language-gap')]
            if pending:
                lang += lang  # Jeden powód liczony raz dla tej analizy.
            assessed = assess_analysis(word, language={v: lang for v in ('broad', 'standard')},
                game_checks=[check('reject' if rejected else 'accept', 'game')])
            db.execute('insert into analysis values (?,?)', (akey, word))
            for variant in ('broad', 'standard'):
                payload = {'language': assessed['language'][variant],
                    **{k: assessed[k] for k in ('game', 'profile', 'release_scope')},
                    'membership': assessed['membership'][variant]}
                text = dumps(payload)
                digest = hashlib.sha256(text.encode()).hexdigest()
                db.execute('insert or ignore into decision_payload values (?,?)', (digest, text))
                db.execute('insert into variant_decision values (?,?,?,?,?,?,?,?)',
                    (akey, variant, *[payload[k]['status'] for k in
                        ('language', 'game', 'profile', 'release_scope', 'membership')], digest))
        db.commit()
        return db

    def test_shared_payloads_and_rejected_unknowns_preserve_word_aggregation(self):
        db = self.database()
        before = db.total_changes
        result = unresolved_report(db)
        for variant in ('broad', 'standard'):
            total = result['variants'][variant]
            self.assertEqual(total['analyses'], 3)
            self.assertEqual(total['analysis_membership'], {'accept': 1, 'reject': 1, 'unresolved': 1})
            self.assertEqual(total['word_membership'], {'accept': 1, 'reject': 0, 'unresolved': 1})
            self.assertEqual(total['analyses_with_unresolved_checks'], 2)
            self.assertEqual(total['rejected_analyses_with_unresolved_checks'], 1)
            rule = next(x for x in result['rules'] if x['variant'] == variant)
            self.assertEqual(rule['analyses'], 2)
            self.assertEqual(rule['word_keys'], 2)
            self.assertEqual(rule['analyses_with_rejected_membership'], 1)
        self.assertEqual(db.total_changes, before)
        self.assertTrue(result['full_qualification_pending'])

    def test_rule_relevance_separates_accepted_rejected_and_unresolved_words(self):
        db=self.database()
        db.execute("insert into analysis values ('c1','cc')")
        db.execute("insert into variant_decision select 'c1',variant,language_status,game_status,profile_status,scope_status,membership_status,assessment_key from variant_decision where analysis_key='a1'")
        before=db.total_changes
        report=unresolved_report(db)
        for rule in report['rules']:
            self.assertEqual(rule['word_keys_by_membership'],{'accept':1,'reject':1,'unresolved':1})
            self.assertEqual(rule['word_keys'],sum(rule['word_keys_by_membership'].values()))
        self.assertEqual(db.total_changes,before)
        self.assertEqual(report,unresolved_report(db))

    def test_missing_variant_or_payload_cannot_be_reported_as_complete(self):
        for table in ('variant_decision', 'decision_payload'):
            db = self.database()
            db.execute('delete from ' + table + ' where rowid=(select min(rowid) from ' + table + ')')
            with self.subTest(table=table), self.assertRaises(GeneratorError):
                unresolved_report(db)

    def test_corrupted_reason_hash_or_status_is_refused(self):
        for change in ('hash', 'status'):
            db = self.database()
            if change == 'hash':
                db.execute("update decision_payload set assessment='{}'")
            else:
                db.execute("update variant_decision set membership_status='accept' where analysis_key='b1'")
            with self.subTest(change=change), self.assertRaises(GeneratorError):
                unresolved_report(db)

    def test_build_writes_report_without_promoting_readiness(self):
        import tempfile
        from pathlib import Path
        from tests.test_build import BuildTests
        from literaki_slownik.build import build
        from literaki_slownik.canonical import load_json
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            manifest = BuildTests().manifest(root,
                '#</COPYRIGHT>\naa\taa\tsubst:sg:nom:m2\tnazwa_pospolita\t\n')
            first = root / 'first'
            second = root / 'second'
            build(manifest, first)
            build(manifest, second)
            report = load_json(first / 'reports/unresolved.json')
            self.assertEqual(report, load_json(second / 'reports/unresolved.json'))
            self.assertEqual(report['variants']['standard']['analyses'], 1)
            self.assertEqual(report['variants']['standard']['analyses_with_unresolved_checks'], 1)
            self.assertEqual(load_json(first / 'manifest.json')['readiness'], 'INCOMPLETE')
