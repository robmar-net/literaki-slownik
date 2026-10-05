"""Dodatni dowód relacji dotyczy tylko sprawdzonego użycia i paradygmatu."""
import copy
import json
import tempfile
import unittest
from pathlib import Path
from literaki_slownik.database import connect
from literaki_slownik.decisions import materialize_assessments,persisted_assessments
from literaki_slownik.canonical import dumps
from literaki_slownik.inputs import GeneratorError
from literaki_slownik.reports import logical_content_report,unresolved_report

GAME='game-documented-resident-capital-v1'
ORTH='orthography-documented-resident-capital-2026-v1'

class ResidentUsesTests(unittest.TestCase):
    def fixture(self,root):
        reviews=[r for r in json.loads(Path('config/generator/semantic-uses.json').read_text())['reviews']
                 if r['use_id'].startswith('sgjp-relation-warszawianka-')]
        self.assertEqual(len(reviews),11)
        manager=connect(root/'build.sqlite',create=True);db=manager.__enter__()
        self.addCleanup(manager.__exit__,None,None,None)
        sid=reviews[0]['source']['source_id']
        db.execute('insert into source_artifact values (?,?,?)',(sid,'sgjp_tab',dumps({
            'sha256':reviews[0]['source']['source_sha256'],'origin':'synthetic_test_only'})))
        db.execute('insert into lexeme values (1,?,?,?)',(sid,'warszawianka','warszawianka'))
        forms={}
        for iid,review in enumerate(reviews,1):
            s=review['source'];word=s['original']
            if word not in forms:
                fid=len(forms)+1;forms[word]=fid
                db.execute('insert into surface_form values (?,?,?,?,?)',(fid,word,word,word,len(word)))
            db.execute('insert into sgjp_record values (?,?,?,?,?,?,?)',(sid,s['first_source_row'],word,
                s['lemma_id'],s['raw_tag'],s['names'],s['qualifiers']))
            db.execute('insert into interpretation values (?,?,?,?,?,?,?,?)',(iid,sid,s['first_source_row'],
                forms[word],1,s['raw_tag'],s['names'],s['qualifiers']))
        # Niezależna analiza tej samej pisowni nie przejmuje klasy mieszkańca.
        db.execute('insert into lexeme values (2,?,?,?)',(sid,'fixture-independent','fixture-independent'))
        db.execute('insert into sgjp_record values (?,?,?,?,?,?,?)',(sid,1,'warszawianka','fixture-independent','subst:sg:nom:f','',''))
        db.execute('insert into interpretation values (12,?,?,?,2,?,?,?)',(sid,1,forms['warszawianka'],'subst:sg:nom:f','',''))
        db.commit()
        (root/'manifest.json').write_text(dumps({'schema_version':1,'readiness':'INCOMPLETE','stages':{'import_sgjp':{'status':'complete'}},
            'inputs':{'manifest':{'unavailable':[]}}}))
        return db,reviews

    def test_all_source_forms_own_uses_remainder_and_independent_analysis(self):
        with tempfile.TemporaryDirectory() as folder:
            db,reviews=self.fixture(Path(folder));before=db.execute('select * from sgjp_record order by row_number').fetchall()
            counts=materialize_assessments(db,use_reviews=reviews)
            self.assertEqual(counts['source_tag_expansions'],15)
            self.assertEqual(counts['documented_use_analyses'],14)
            self.assertEqual(counts['remainder_analyses'],14)
            self.assertEqual(counts['analyses'],29)
            self.assertEqual(counts['variant_decisions'],58)
            for v in ('broad','standard'):
                rows=persisted_assessments(db,'warszawianka',v)
                use=next(r for r in rows if r.get('semantic_trace',{}).get('kind')=='documented_use')
                rest=next(r for r in rows if r.get('semantic_trace',{}).get('kind')=='unresolved_remainder')
                self.assertEqual(use['assessment']['game']['status'],'reject')
                self.assertEqual(use['assessment']['membership']['status'],'reject')
                self.assertEqual(use['assessment']['language']['status'],'unresolved' if v=='broad' else 'reject')
                self.assertEqual(rest['assessment']['membership']['status'],'unresolved')
                self.assertFalse(any(c['rule_id']==GAME for c in rest['assessment']['game']['checks']))
                self.assertTrue(any(r['interpretation_id']==12 and
                                    r['assessment']['membership']['status']=='unresolved' for r in rows))
            self.assertEqual(before,db.execute('select * from sgjp_record order by row_number').fetchall())
            first=logical_content_report(db)
            self.assertEqual(materialize_assessments(db,use_reviews=list(reversed(reviews)))['new_analyses'],0)
            self.assertEqual(first,logical_content_report(db))
            self.assertEqual(db.execute('pragma foreign_key_check').fetchall(),[])

    def test_mismatched_source_relation_norm_or_unscoped_rule_refused_before_writes(self):
        changes=[lambda r:r['source'].update(lemma_id='fixture-independent'),
                 lambda r:r['source'].update(original='bawarka'),
                 lambda r:r['source'].update(source_sha256='0'*64),
                 lambda r:r['evidence'][0].update(sha256='0'*64),
                 lambda r:r['evidence'][0].update(artifact_id='different-review'),
                 lambda r:r['evidence'][1].update(sha256='0'*64),
                 lambda r:r.update(use_id='sgjp-relation-bawarka-6309663-v1'),
                 lambda r:r.update(documented_conditions=[GAME]),
                 lambda r:r.update(documented_conditions=[])]
        with tempfile.TemporaryDirectory() as folder:
            db,reviews=self.fixture(Path(folder))
            for change in changes:
                bad=copy.deepcopy(reviews);change(bad[0]);before=db.total_changes
                with self.assertRaises(GeneratorError):materialize_assessments(db,use_reviews=bad)
                self.assertEqual(before,db.total_changes)

    def test_explain_and_quality_have_full_relation_trace_without_propagation(self):
        from literaki_slownik.explain import explain,format_explanation
        from literaki_slownik.quality import sample_persisted_analyses
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);db,reviews=self.fixture(root);materialize_assessments(db,use_reviews=reviews)
            result=explain(root,'warszawiance',variant='standard')
            self.assertEqual(result['source_aggregation']['status'],'unresolved')
            text=format_explanation(result)
            self.assertIn(GAME,text);self.assertIn('sgjp-relation-warszawianka-',text)
            sample=sample_persisted_analyses(db,json.loads(Path('config/generator/quality.json').read_text()))
            self.assertEqual(sample['strata']['analysis:documented_use']['population'],14)
            self.assertEqual(sample['strata']['analysis:unresolved_remainder']['population'],14)
            self.assertEqual(sample,sample_persisted_analyses(db,json.loads(Path('config/generator/quality.json').read_text())))
            self.assertEqual(unresolved_report(db)['variants']['standard']['semantic_analysis_kinds']['documented_use'],14)

    def test_reader_refuses_removed_resident_rule_even_with_coherent_rehashed_payload(self):
        import hashlib
        from literaki_slownik.decisions import assessment
        with tempfile.TemporaryDirectory() as folder:
            db,reviews=self.fixture(Path(folder));materialize_assessments(db,use_reviews=reviews)
            row=next(r for r in persisted_assessments(db,'warszawianka','broad')
                     if r.get('semantic_trace',{}).get('kind')=='documented_use')
            key,encoded=db.execute('''select p.assessment_key,p.assessment from decision_payload p
                join variant_decision d on d.assessment_key=p.assessment_key
                where d.analysis_key=? and d.variant='broad' ''',(row['analysis_key'],)).fetchone()
            value=json.loads(encoded)
            value['game']=assessment(c for c in value['game']['checks'] if c['rule_id']!=GAME)
            value['membership']=assessment(c for layer in ('language','game','profile','release_scope')
                for c in value[layer]['checks'])
            text=dumps(value);new=hashlib.sha256(text.encode()).hexdigest()
            db.execute('insert into decision_payload values (?,?)',(new,text))
            db.execute('update variant_decision set assessment_key=? where analysis_key=? and variant=?',
                       (new,row['analysis_key'],'broad'));db.commit()
            with self.assertRaises(GeneratorError):persisted_assessments(db,'warszawianka','broad')
