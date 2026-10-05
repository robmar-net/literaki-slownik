"""Norma poświadcza konkretny wariant; lower nie zastępuje dowodu."""
import copy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from literaki_slownik.canonical import dumps
from literaki_slownik.database import connect
from literaki_slownik.inputs import GeneratorError
from literaki_slownik.decisions import materialize_assessments,persisted_assessments
from literaki_slownik.reports import logical_content_report

SHA='3b2ee079143bc95186370fd528735779c4ba62f4ce14e30cf6622ceb566e9810'
RULE='documented-spelling-variant-v1'

def source(word='Angol'):
    return dict(source_id='sgjp-20260823',source_sha256=SHA,first_source_row=9040 if word=='Angol' else 358226,
        original=word,lemma_id=word,raw_tag='subst:sg:nom:m1',names='nazwa_pospolita',
        qualifiers='pot.,etn.' if word=='Angol' else '')

class SpellingVariantsTests(unittest.TestCase):
    def fixture(self,root):
        manager=connect(root/'build.sqlite',create=True);db=manager.__enter__()
        self.addCleanup(manager.__exit__,None,None,None)
        db.execute('insert into source_artifact values (?,?,?)',('sgjp-20260823','sgjp_tab',dumps({'sha256':SHA,'origin':'synthetic_test_only'})))
        records=[source(),source('Jugol'),dict(source(),first_source_row=9053,lemma_id='Angola',raw_tag='subst:pl:gen:f',names='nazwa_geograficzna',qualifiers='char.')]
        for i,s in enumerate(records,1):
            db.execute('insert into sgjp_record values (?,?,?,?,?,?,?)',tuple(s[k] for k in ('source_id','first_source_row','original','lemma_id','raw_tag','names','qualifiers')))
            db.execute('insert or ignore into surface_form values (?,?,?,?,?)',(1 if i==3 else i,s['original'],s['original'],s['original'].lower(),len(s['original'])))
            db.execute('insert into lexeme values (?,?,?,?)',(i,s['source_id'],s['lemma_id'],s['lemma_id']))
            db.execute('insert into interpretation values (?,?,?,?,?,?,?,?)',(i,s['source_id'],s['first_source_row'],1 if i==3 else i,i,s['raw_tag'],s['names'],s['qualifiers']))
        db.commit();return db

    def test_only_exact_attested_base_forms_with_full_source_and_use_trace(self):
        from literaki_slownik.constructions import spelling_variant_candidates
        for word in ('Angol','Jugol'):
            c,=spelling_variant_candidates(source(word))
            self.assertEqual(c['original'],word.lower());self.assertEqual(c['rule_id'],RULE)
            self.assertEqual(c['components'],[{'kind':'source_interpretation','interpretation':source(word)}])
            self.assertEqual(c['orthographic_variant']['source_original'],word)
            self.assertEqual(c['orthographic_variant']['coverage'],'documented_use_only')
            self.assertEqual(c['linguistic_evidence']['status'],'accept')
            self.assertEqual(c['qualifiers'],source(word)['qualifiers'])

    def test_no_other_source_snapshot_fields_homonym_or_inflection_is_generated(self):
        from literaki_slownik.constructions import spelling_variant_candidates
        for field,value in dict(source_id='fixture',source_sha256='0'*64,first_source_row=9053,
            original='Angola',lemma_id='Angola',raw_tag='subst:pl:gen:f',names='nazwa_geograficzna',qualifiers='').items():
            self.assertEqual(spelling_variant_candidates(dict(source(),**{field:value})),[],field)
        self.assertEqual(spelling_variant_candidates(dict(source(),original='Angola',raw_tag='subst:sg:gen:m1')),[])
        self.assertEqual(spelling_variant_candidates(dict(source(),original='PCV',lemma_id='PCV')),[])
        missing=source();missing.pop('source_sha256')
        self.assertEqual(spelling_variant_candidates(missing),[])

    def test_materialization_preserves_originals_homonyms_and_unknowns(self):
        from literaki_slownik.constructions import materialize_confirmed_candidates
        with tempfile.TemporaryDirectory() as folder:
            db=self.fixture(Path(folder));raw=db.execute('select * from sgjp_record').fetchall()
            counts=materialize_confirmed_candidates(db)
            self.assertEqual(counts['by_rule'][RULE],2)
            materialize_assessments(db)
            for v in ('broad','standard'):
                rows=persisted_assessments(db,'angol',v)
                self.assertEqual(len(rows),3)
                variant=next(r for r in rows if r['candidate_key'])
                self.assertEqual(variant['assessment']['membership']['status'],'unresolved')
                self.assertFalse(any(c['rule_id']=='game-uppercase-v1' and c['status']=='reject' for c in variant['assessment']['game']['checks']))
                self.assertTrue(all(r['assessment']['game']['status']=='reject' for r in rows if r['interpretation_id']))
            before=logical_content_report(db)
            self.assertEqual(materialize_confirmed_candidates(db)['new_candidates'],0)
            self.assertEqual(materialize_assessments(db)['new_analyses'],0)
            self.assertEqual(before,logical_content_report(db));self.assertEqual(raw,db.execute('select * from sgjp_record').fetchall())
            self.assertEqual(db.execute('select count(*) from lexeme').fetchone()[0],3)
            self.assertEqual(db.execute('pragma foreign_key_check').fetchall(),[])

    def test_live_and_stored_explain_show_orthography_not_particle(self):
        from literaki_slownik.constructions import materialize_confirmed_candidates
        from literaki_slownik.explain import explain,format_explanation
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);db=self.fixture(root);materialize_confirmed_candidates(db);materialize_assessments(db)
            (root/'manifest.json').write_text(dumps({'schema_version':1,'readiness':'INCOMPLETE','stages':{'import_sgjp':{'status':'complete'}},'inputs':{'manifest':{'unavailable':[]}}}))
            for word in ('angol','jugol'):
                for v in ('broad','standard'):
                    result=explain(root,word,v);c,=result['derivations']
                    self.assertTrue(c['persisted_candidate_key'])
                    self.assertEqual(c['orthographic_variant']['target_original'],word)
                    text=format_explanation(result);self.assertIn('Wariant pisowni:',text);self.assertNotIn('Partykuła:',text)

    def test_forged_document_source_or_component_refused_before_assessment_write(self):
        from literaki_slownik.constructions import materialize_confirmed_candidates
        for change in ('document','source','component'):
            with tempfile.TemporaryDirectory() as folder:
                db=self.fixture(Path(folder));materialize_confirmed_candidates(db)
                key,payload=db.execute('select candidate_key,payload from derivation_candidate order by candidate_key limit 1').fetchone()
                value=json.loads(payload)
                if change=='component':
                    db.execute('update derivation_component set source_row=9053 where candidate_key=?',(key,))
                else:
                    if change=='document':value['orthographic_variant']['document_sha256']='2'*64
                    else:value['components'][0]['interpretation']['source_sha256']='0'*64
                    db.execute('update derivation_candidate set payload=? where candidate_key=?',(dumps(value),key))
                db.commit();before=db.total_changes
                with self.assertRaises(GeneratorError):materialize_assessments(db)
                self.assertEqual(db.total_changes,before)
