"""Ten sam zatwierdzony próg dowodu, bez domykania innych warunków."""
import copy
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from literaki_slownik.database import connect
from literaki_slownik.decisions import materialize_assessments,persisted_assessments
from literaki_slownik.inputs import GeneratorError
from literaki_slownik.canonical import dumps

WORDS={'dwójnasób','trójnasób','kroćset','roścież','ziem'}
RULE='linguistic-documented-use-lexical-proof-v1'

class AdditionalPhraseUsesTests(unittest.TestCase):
    def fixture(self,root):
        path=Path('config/generator/semantic-uses.json')
        reviews=[r for r in json.loads(path.read_text())['reviews'] if r['source']['original'] in WORDS]
        self.assertEqual(len(reviews),5)
        context=connect(root/'build.sqlite',create=True);db=context.__enter__()
        self.addCleanup(context.__exit__,None,None,None)
        sid=reviews[0]['source']['source_id'];db.execute('insert into source_artifact values (?,?,?)',
            (sid,'sgjp_tab',dumps({'sha256':reviews[0]['source']['source_sha256']})))
        for i,r in enumerate(reviews,1):
            s=r['source'];word=s['original'];lemma=s['lemma_id'];row=s['first_source_row']
            db.execute('insert into sgjp_record values (?,?,?,?,?,?,?)',(sid,row,word,lemma,s['raw_tag'],s['names'],s['qualifiers']))
            db.execute('insert into surface_form values (?,?,?,?,?)',(i,word,word,word,len(word)))
            db.execute('insert into lexeme values (?,?,?,?)',(i,sid,lemma,lemma.split(':')[0]))
            db.execute('insert into interpretation values (?,?,?,?,?,?,?,?)',(i,sid,row,i,i,s['raw_tag'],s['names'],s['qualifiers']))
        db.commit();return db,reviews

    def test_five_explicit_uses_shared_lexical_condition_and_remainders(self):
        directory=self.enterContext(tempfile.TemporaryDirectory())
        db,reviews=self.fixture(Path(directory));counts=materialize_assessments(db,use_reviews=reviews)
        self.assertEqual(counts['documented_use_analyses'],5)
        self.assertEqual(counts['remainder_analyses'],5)
        for word in WORDS:
            for variant in ('broad','standard'):
                rows=persisted_assessments(db,word,variant)
                use=next(r for r in rows if r['semantic_trace']['kind']=='documented_use')
                rest=next(r for r in rows if r['semantic_trace']['kind']=='unresolved_remainder')
                c=next(c for c in use['assessment']['language']['checks'] if c['rule_id']==RULE)
                self.assertEqual(c['status'],'accept')
                self.assertFalse(any(c['rule_id']==RULE for c in rest['assessment']['language']['checks']))
                self.assertEqual(rest['assessment']['membership']['status'],
                    'reject' if word=='kroćset' and variant=='standard' else 'unresolved')
        self.assertEqual(materialize_assessments(db,use_reviews=list(reversed(reviews)))['new_analyses'],0)
        self.assertFalse(db.execute('pragma foreign_key_check').fetchall())

    def test_shared_lexical_proof_keeps_history_and_remainder_independent(self):
        directory=self.enterContext(tempfile.TemporaryDirectory())
        db,reviews=self.fixture(Path(directory));materialize_assessments(db,use_reviews=reviews)
        for variant in ('broad','standard'):
            rows=persisted_assessments(db,'kroćset',variant)
            use=next(r for r in rows if r['semantic_trace']['kind']=='documented_use')
            checks=use['assessment']['language']['checks']
            self.assertEqual(next(c['status'] for c in checks if c['rule_id']==RULE),'accept')
            if variant=='standard':
                self.assertTrue(any(c['status']=='reject' and c['rule_id']=='linguistic-historical-form-v1' for c in checks))
                self.assertEqual(use['assessment']['membership']['status'],'reject')
        from literaki_slownik.decisions import lexical_use_checks
        with self.assertRaises(GeneratorError):lexical_use_checks(reviews[0],'unknown')

    def test_wrong_document_hash_or_source_mapping_refuses_before_writes(self):
        directory=self.enterContext(tempfile.TemporaryDirectory())
        db,reviews=self.fixture(Path(directory))
        for field in ('document','use'):
            changed=copy.deepcopy(reviews)
            if field=='document':changed[0]['evidence'][0]['sha256']='0'*64
            else:changed[0]['use_id']='other-use'
            with self.assertRaises(GeneratorError):materialize_assessments(db,use_reviews=changed)
            self.assertEqual(db.execute('select count(*) from analysis').fetchone()[0],0)

    def test_rehashed_loss_of_positive_lexical_reason_refuses_read(self):
        directory=self.enterContext(tempfile.TemporaryDirectory())
        db,reviews=self.fixture(Path(directory));materialize_assessments(db,use_reviews=reviews)
        key,encoded=db.execute("select assessment_key,assessment from decision_payload where assessment like '%documented_use%' and assessment like '%lexical_proof%' limit 1").fetchone()
        value=json.loads(encoded)
        for layer in ('language','membership'):
            value[layer]['checks']=[c for c in value[layer]['checks'] if c['rule_id']!=RULE]
        encoded=dumps(value);new=hashlib.sha256(encoded.encode()).hexdigest()
        db.execute('insert into decision_payload values (?,?)',(new,encoded))
        db.execute('update variant_decision set assessment_key=? where assessment_key=?',(new,key))
        with self.assertRaises(GeneratorError):persisted_assessments(db,reviews[0]['source']['original'],'broad')
