"""Własne użycia nie zastępują źródła ani nie zamykają brakujących możliwości."""
import copy
import json
import tempfile
import unittest
from pathlib import Path

from literaki_slownik.database import connect
from literaki_slownik.decisions import materialize_assessments, persisted_assessments
from literaki_slownik.inputs import GeneratorError
from literaki_slownik.reports import logical_content_report, unresolved_report, persisted_filter_impact


class SemanticUsesTests(unittest.TestCase):
    def test_documentary_name_proof_applies_only_to_bound_use_not_remainder(self):
        from literaki_slownik.decisions import assess_diagnostic
        from tests.test_documented_names import source,RULE
        record=source('de','de:F',1463128)
        use=assess_diagnostic('de','',source_analyses=[record],documented_condition_ids=[RULE])
        remainder=assess_diagnostic('de','',source_analyses=[record],documented_condition_ids=[])
        self.assertEqual(use['game']['status'],'reject')
        self.assertEqual(remainder['game']['status'],'unresolved')
        self.assertFalse(any(c['rule_id']==RULE for c in remainder['game']['checks']))

    def test_build_reads_only_manifest_pinned_use_review_configuration(self):
        from tests.test_build import BuildTests
        from literaki_slownik.build import build
        import hashlib
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder)
            manifest=BuildTests().manifest(root,'#</COPYRIGHT>\ndon\tdon:F\tfrag\t\t\n')
            value=json.loads(manifest.read_text());artifact=value['artifacts'][0]
            review=dict(use_id='own-fixture-don',description='Własne użycie testowe',coverage='documented_use_only',
                source=dict(source_id=artifact['source_id'],source_sha256=artifact['sha256'],first_source_row=1,
                    original='don',lemma_id='don:F',raw_tag='frag',names='',qualifiers=''),
                evidence=[dict(artifact_id='fixture-proof',sha256='2'*64,locator='sekcja 1',
                    status='ALLOWED',role='own_documentary_review')])
            data=root/'own-uses.json';data.write_text(json.dumps({'schema_version':1,'reviews':[review]}))
            value['configurations']['semantic-uses']={'path':data.name,'sha256':hashlib.sha256(data.read_bytes()).hexdigest()}
            quality=root/'quality.json';quality.write_bytes(Path('config/generator/quality.json').read_bytes())
            value['configurations']['quality']={'path':quality.name,'sha256':hashlib.sha256(quality.read_bytes()).hexdigest()}
            manifest.write_text(json.dumps(value))
            run=root/'run';build(manifest,run)
            counts=json.loads((run/'reports/decisions.json').read_text())
            self.assertEqual(counts['documented_use_analyses'],1)
            self.assertEqual(counts['remainder_analyses'],1)
            self.assertEqual(counts['analyses'],2)
            sample=json.loads((run/'reports/quality-analyses.json').read_text())
            self.assertEqual(sample['strata']['analysis:documented_use']['population'],1)
            self.assertEqual(len(sample['items']),2)

    def fixture(self, root):
        db = connect(root/'build.sqlite', create=True)
        connection = db.__enter__()
        self.addCleanup(db.__exit__, None, None, None)
        connection.execute('insert into source_artifact values (?,?,?)',
            ('fixture', 'sgjp_tab', json.dumps({'sha256':'1'*64, 'origin':'synthetic_test_only'})))
        for i, tag in ((1, 'frag'), (2, 'subst:sg:nom.acc:m3')):
            lemma = 'don:F' if i == 1 else 'don:S'
            connection.execute('insert into sgjp_record values (?,?,?,?,?,?,?)', ('fixture',i,'don',lemma,tag,'',''))
            if i == 1:
                connection.execute('insert into surface_form values (1,?,?,?,3)', ('don','don','don'))
            connection.execute('insert into lexeme values (?,?,?,?)', (i,'fixture',lemma,'don'))
            connection.execute('insert into interpretation values (?,?,?,?,?,?,?,?)', (i,'fixture',i,1,i,tag,'',''))
        source = dict(source_id='fixture',source_sha256='1'*64,first_source_row=1,
            original='don',lemma_id='don:F',raw_tag='frag',names='',qualifiers='')
        reviews = [dict(use_id='own-use-'+str(i), source=source, description='Własna fikstura użycia '+str(i),
            coverage='documented_use_only', evidence=[dict(artifact_id='own-fixture-proof',sha256='2'*64,
            locator='sekcja '+str(i),status='ALLOWED',role='own_documentary_review')]) for i in (1,2)]
        connection.commit()
        return connection, reviews

    def test_two_uses_remainder_and_homonym_are_persisted_idempotently(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);db,reviews=self.fixture(root)
            counts=materialize_assessments(db,use_reviews=reviews,batch_size=2)
            self.assertEqual(counts['source_tag_expansions'],3)
            self.assertEqual(counts['documented_use_analyses'],2)
            self.assertEqual(counts['remainder_analyses'],1)
            self.assertEqual(counts['analyses'],5)
            rows=persisted_assessments(db,'don','standard')
            self.assertEqual(sum(r.get('semantic_trace',{}).get('kind')=='documented_use' for r in rows),2)
            remainder=[r for r in rows if r.get('semantic_trace',{}).get('kind')=='unresolved_remainder']
            self.assertEqual(len(remainder),1)
            self.assertEqual(remainder[0]['assessment']['membership']['status'],'reject')
            self.assertTrue(any(c['rule_id']=='semantic-remainder-exhausted-v1' for c in remainder[0]['assessment']['language']['checks']))
            self.assertEqual(db.execute('select count(*) from sgjp_record').fetchone()[0],2)
            before=logical_content_report(db)
            self.assertEqual(materialize_assessments(db,use_reviews=list(reversed(reviews)))['new_analyses'],0)
            self.assertEqual(logical_content_report(db),before)
            self.assertEqual(db.execute('pragma foreign_key_check').fetchall(),[])
            unknown=unresolved_report(db)
            impact=persisted_filter_impact(db)
            for v in ('broad','standard'):
                self.assertEqual(unknown['variants'][v]['semantic_analysis_kinds'],
                    {'documented_use':2,'unresolved_remainder':1,'source_expansion':2})
                self.assertEqual(impact['variants'][v]['semantic_analysis_kinds'],
                    unknown['variants'][v]['semantic_analysis_kinds'])
            (root/'manifest.json').write_text(json.dumps({'schema_version':1,'readiness':'INCOMPLETE',
                'stages':{'import_sgjp':{'status':'complete'}},'inputs':{'manifest':{'unavailable':[]}}}))
            from literaki_slownik.explain import explain,format_explanation
            live=explain(root,'don')
            self.assertEqual(len(live['semantic_analyses']),3)
            self.assertIn('own-use-1',format_explanation(live))
            self.assertIn('Nierozpoznane możliwości',format_explanation(live))

    def test_invalid_evidence_identity_duplicates_and_claimed_completeness_refused_before_writes(self):
        with tempfile.TemporaryDirectory() as folder:
            db,reviews=self.fixture(Path(folder))
            mutations=[lambda r:r[0]['source'].update(lemma_id='don:S'),
                lambda r:r[0]['source'].update(source_sha256='0'*64),
                lambda r:r[0]['source'].update(first_source_row=2),
                lambda r:r[0]['source'].update(names='nazwa_pospolita'),
                lambda r:r[0]['evidence'][0].update(status='BLOCKED'),
                lambda r:r[0]['evidence'][0].update(role='online_metadata'),
                lambda r:r[0].update(coverage='complete'),
                lambda r:r[1].update(use_id=r[0]['use_id']),
                lambda r:r[0].update(game_status='accept')]
            mutations+=[lambda r:r[0].update(documented_conditions=['made-up-accept-v1']),
                lambda r:r[0].update(documented_conditions=['game-documented-surname-component-v1'])]
            for change in mutations:
                bad=copy.deepcopy(reviews);change(bad)
                before=db.total_changes
                with self.assertRaises(GeneratorError):materialize_assessments(db,use_reviews=bad)
                self.assertEqual(db.total_changes,before)

    def test_changed_or_omitted_review_requires_new_build_without_mutation(self):
        with tempfile.TemporaryDirectory() as folder:
            db,reviews=self.fixture(Path(folder));materialize_assessments(db,use_reviews=reviews)
            for bad in ([],reviews[:1]):
                before=db.total_changes
                with self.assertRaises(GeneratorError):materialize_assessments(db,use_reviews=bad)
                self.assertEqual(db.total_changes,before)

    def test_quality_sample_keeps_source_and_all_use_layers(self):
        from literaki_slownik.quality import sample_persisted_analyses
        with tempfile.TemporaryDirectory() as folder:
            db,reviews=self.fixture(Path(folder));materialize_assessments(db,use_reviews=reviews)
            config=json.loads(Path('config/generator/quality.json').read_text())
            sample=sample_persisted_analyses(db,config)
            self.assertEqual(sample['strata']['analysis:documented_use']['population'],2)
            self.assertEqual(sample['strata']['analysis:unresolved_remainder']['population'],1)
            self.assertEqual(len(sample['items']),5)
            for item in sample['items']:
                self.assertTrue(item['source_record'])
                self.assertEqual(set(item['assessments']),{'broad','standard'})
                for value in item['assessments'].values():
                    self.assertTrue(set(('language','game','profile','release_scope','membership'))<=set(value))
            self.assertEqual(sample,sample_persisted_analyses(db,config))

    def test_readers_refuse_missing_remainder_or_forged_trace_even_with_valid_payload_hash(self):
        import hashlib
        from literaki_slownik.canonical import dumps
        for corruption in ('missing_remainder','forged_trace'):
            with self.subTest(corruption=corruption), tempfile.TemporaryDirectory() as folder:
                db,reviews=self.fixture(Path(folder));materialize_assessments(db,use_reviews=reviews)
                if corruption=='missing_remainder':
                    key=next(r['analysis_key'] for r in persisted_assessments(db,'don','standard')
                        if r.get('semantic_trace',{}).get('kind')=='unresolved_remainder')
                    db.execute('delete from variant_decision where analysis_key=?',(key,))
                    db.execute('delete from analysis where analysis_key=?',(key,))
                else:
                    old,encoded=db.execute("select assessment_key,assessment from decision_payload where assessment like '%own-use-1%' limit 1").fetchone()
                    payload=json.loads(encoded);payload['semantic_trace']['source']['lemma_id']='don:S'
                    text=dumps(payload);new=hashlib.sha256(text.encode()).hexdigest()
                    db.execute('insert into decision_payload values (?,?)',(new,text))
                    db.execute('update variant_decision set assessment_key=? where assessment_key=?',(new,old))
                db.commit()
                for reader in (unresolved_report,persisted_filter_impact):
                    with self.assertRaises(GeneratorError):reader(db)
                with self.assertRaises(GeneratorError):persisted_assessments(db,'don','standard')


class PositiveUseProofTests(unittest.TestCase):
    def fixture(self, root):
        manager=connect(root/'build.sqlite',create=True);db=manager.__enter__()
        self.addCleanup(manager.__exit__,None,None,None)
        review=next(r for r in json.loads(Path('config/generator/semantic-uses.json').read_text())['reviews']
                    if r['use_id']=='sgjp-authors-phrase-wznak-v1')
        # Jawna fikstura reprodukuje tożsamość; nie jest danymi wydania.
        from tests.test_documented_names import source,SHA
        r=source('wznak','wznak',6770165);sid=r['source_id']
        db.execute('insert into source_artifact values (?,?,?)',(sid,'sgjp_tab',json.dumps({'sha256':SHA,'origin':'synthetic_test_only'})))
        db.execute('insert into sgjp_record values (?,?,?,?,?,?,?)',(sid,6770165,'wznak','wznak','frag','',''))
        db.execute('insert into surface_form values (1,?,?,?,5)',('wznak','wznak','wznak'))
        db.execute('insert into lexeme values (1,?,?,?)',(sid,'wznak','wznak'))
        db.execute('insert into interpretation values (1,?,?,1,1,?,?,?)',(sid,6770165,'frag','',''))
        db.commit();return db,review

    def test_positive_shared_condition_does_not_close_other_layers_or_remainder(self):
        with tempfile.TemporaryDirectory() as folder:
            db,review=self.fixture(Path(folder));materialize_assessments(db,use_reviews=[review])
            for variant in ('broad','standard'):
                rows=persisted_assessments(db,'wznak',variant)
                use=next(r for r in rows if r['semantic_trace']['kind']=='documented_use')
                rest=next(r for r in rows if r['semantic_trace']['kind']=='unresolved_remainder')
                checks=use['assessment']['language']['checks']
                proof=next(c for c in checks if c['rule_id']=='linguistic-documented-use-lexical-proof-v1')
                self.assertEqual(proof['status'],'accept')
                self.assertEqual(use['assessment']['membership']['status'],'unresolved')
                self.assertEqual(use['assessment']['game']['status'],'unresolved')
                self.assertFalse(any(c['rule_id']==proof['rule_id'] for c in rest['assessment']['language']['checks']))
            before=logical_content_report(db)
            self.assertEqual(materialize_assessments(db,use_reviews=[review])['new_analyses'],0)
            self.assertEqual(logical_content_report(db),before)

    def test_lexical_proof_cannot_be_reused_for_another_use_or_document(self):
        with tempfile.TemporaryDirectory() as folder:
            db,review=self.fixture(Path(folder))
            for field,value in (('use_id','other-use'),('lexical_proof','unapproved-rule')):
                bad=copy.deepcopy(review);bad[field]=value;before=db.total_changes
                with self.assertRaises(GeneratorError):materialize_assessments(db,use_reviews=[bad])
                self.assertEqual(db.total_changes,before)
            bad=copy.deepcopy(review);bad['evidence'][0]['sha256']='2'*64
            with self.assertRaises(GeneratorError):materialize_assessments(db,use_reviews=[bad])
            self.assertEqual(db.execute('select count(*) from analysis').fetchone()[0],0)

    def test_old_broad_only_payload_is_readable_but_not_accepted_in_current_policy(self):
        import hashlib
        from literaki_slownik.canonical import dumps
        for version in ('diagnostic-approved-conditions-v20','diagnostic-approved-conditions-v21'):
            with self.subTest(version=version),tempfile.TemporaryDirectory() as folder:
                db,review=self.fixture(Path(folder));materialize_assessments(db,use_reviews=[review])
                db.execute('update analysis set policy_version=?',(version,))
                rows=db.execute('select d.analysis_key,d.variant,d.assessment_key,p.assessment from variant_decision d join decision_payload p on p.assessment_key=d.assessment_key').fetchall()
                for akey,variant,old,encoded in rows:
                    value=json.loads(encoded)
                    for layer in ('language','membership'):
                        for c in value[layer]['checks']:
                            if c['rule_id']=='linguistic-documented-use-lexical-proof-v1':
                                c['status']='accept' if variant=='broad' else 'unresolved'
                                c['message']=('Dodatni dowód leksykalny BROAD dokładnie udokumentowanego użycia; inne warunki osobno.' if variant=='broad' else 'Dowód BROAD nie rozstrzyga aktualnej kwalifikacji STANDARD.')
                    encoded=dumps(value);new=hashlib.sha256(encoded.encode()).hexdigest()
                    db.execute('insert or ignore into decision_payload values (?,?)',(new,encoded))
                    db.execute('update variant_decision set assessment_key=? where analysis_key=? and variant=?',(new,akey,variant))
                db.commit();before=db.total_changes
                if version.endswith('v20'):
                    rows=persisted_assessments(db,'wznak','standard')
                    use=next(r for r in rows if r['semantic_trace']['kind']=='documented_use')
                    self.assertEqual(next(c['status'] for c in use['assessment']['language']['checks'] if c['rule_id']=='linguistic-documented-use-lexical-proof-v1'),'unresolved')
                else:
                    with self.assertRaises(GeneratorError):persisted_assessments(db,'wznak','standard')
                self.assertEqual(db.total_changes,before)
