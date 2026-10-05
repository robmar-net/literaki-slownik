"""Pełny odczyt nie jest pełnym mapowaniem znaczeń ani wejściem build."""
import copy,importlib.util,unittest
from pathlib import Path

class ReaderReviewTests(unittest.TestCase):
    def setUp(self):
        p=Path(__file__).resolve().parents[1]/'scripts/audit_sgjp_reader_review.py'
        spec=importlib.util.spec_from_file_location('reader_review',p);self.module=importlib.util.module_from_spec(spec);spec.loader.exec_module(self.module)
        self.cases={'cases':[{'case_id':'don','source':{'lemma_id':'don','tag':'frag'},'other_source_analyses':[]},
                             {'case_id':'de','source':{'lemma_id':'de:F','tag':'frag'},'other_source_analyses':[{'lemma_id':'de:S'}]}]}
        def article(i,cls):return {'web_lexeme_id':i,'response_sha256':'a'*64,'url':'https://sgjp.pl/leksemy/#'+str(i),'own_class_observation':cls}
        self.review={'schema_version':1,'scope':'public_reader_reference_observations','automatic_eligibility_decisions':False,
            'active_build_inputs_added':0,'raw_articles_committed':False,'records':[
             {'case_id':'don','pinned_source':self.cases['cases'][0]['source'],'mapping_status':'multiple_articles_not_snapshot_identity','eligibility_status':'unresolved','articles':[article(1,'phrase_component'),article(2,'article')]},
             {'case_id':'de','pinned_source':self.cases['cases'][1]['source'],'mapping_status':'unique_spelling_class_candidate_not_snapshot_identity','eligibility_status':'unresolved','articles':[article(3,'surname_component')]}]}
    def test_plural_articles_preserve_compact_source_and_homonyms(self):
        result=self.module.audit(self.cases,self.review)
        self.assertEqual(result['source_cases'],2);self.assertEqual(result['article_observations'],3)
        self.assertEqual(result['mapping_statuses']['multiple_articles_not_snapshot_identity'],1)
        self.assertEqual(self.cases['cases'][1]['other_source_analyses'],[{'lemma_id':'de:S'}])
        self.assertFalse(result['source_snapshot_alignment_confirmed']);self.assertFalse(result['full_semantics_complete'])
    def test_incomplete_duplicate_or_different_source_refused(self):
        for kind in ('missing','duplicate','identity'):
            r=copy.deepcopy(self.review)
            if kind=='missing':r['records'].pop()
            if kind=='duplicate':r['records'].append(r['records'][0])
            if kind=='identity':r['records'][1]['pinned_source']['lemma_id']='de:S'
            with self.subTest(kind=kind),self.assertRaises(ValueError):self.module.audit(self.cases,r)
    def test_reading_cannot_authorize_input_or_qualification(self):
        for field,value in [('active_build_inputs_added',1),('raw_articles_committed',True),('automatic_eligibility_decisions',True)]:
            r=copy.deepcopy(self.review);r[field]=value
            with self.subTest(field=field),self.assertRaises(ValueError):self.module.audit(self.cases,r)
        r=copy.deepcopy(self.review);r['records'][0]['eligibility_status']='accept'
        with self.assertRaises(ValueError):self.module.audit(self.cases,r)

    def test_wrong_article_anchor_or_corrupt_hash_refused(self):
        for field,value in [('url','https://sgjp.pl/leksemy/#12'),('response_sha256','not-a-hash')]:
            r=copy.deepcopy(self.review);r['records'][0]['articles'][0][field]=value
            with self.subTest(field=field),self.assertRaises(ValueError):self.module.audit(self.cases,r)
        r=copy.deepcopy(self.review);r['records'][0]['mapping_status']='snapshot_confirmed'
        with self.assertRaises(ValueError):self.module.audit(self.cases,r)
