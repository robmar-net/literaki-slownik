"""Próbka jakości jest odtwarzalna i nie stanowi werdyktu językowego."""
import unittest
from unittest.mock import patch

from literaki_slownik.canonical import load_json
from literaki_slownik.inputs import GeneratorError
from literaki_slownik.quality import sample_strata, sampling_digest, review_template


class QualityTests(unittest.TestCase):
    def setUp(self):
        self.config = load_json('config/generator/quality.json')

    def test_utf8_canonical_encoding_known_digest(self):
        self.assertEqual(sampling_digest(self.config['seed'], 'krótkie', 'ąę'),
                         '1df9886d041a162a42789bde80cd56c662d3948408f6429c5d4f4217d20f2be3')

    def test_stable_mapping_order_duplicates_and_limit(self):
        keys = [f'word:{n:04}' for n in range(1000)]
        first = sample_strata({'b': iter(keys), 'a': iter(['a', 'a', 'b'])}, self.config)
        second = sample_strata({'a': iter(['a', 'b']), 'b': iter(keys)}, self.config)
        self.assertEqual(first, second)
        self.assertEqual(first['strata']['a']['population'], 2)
        self.assertEqual(first['strata']['b']['population'], 1000)
        self.assertEqual(first['strata']['b']['sample_size'], 30)
        selected = first['strata']['b']['selected']
        self.assertEqual(selected, sorted(selected, key=lambda item: (item['sha256'], item['key'])))
        remaining = set(keys) - {item['key'] for item in selected}
        self.assertTrue(all(sampling_digest(self.config['seed'], 'b', key) >= selected[-1]['sha256']
                            for key in remaining))

    def test_empty_and_small_strata_and_overlap(self):
        result = sample_strata({'empty': [], 'one': ['a'], 'two': ['a', 'b']}, self.config)
        self.assertEqual(result['strata']['empty']['coverage'], 'EMPTY_NOT_COVERAGE')
        self.assertEqual(result['strata']['empty']['sample_size'], 0)
        self.assertEqual(result['strata']['two']['sample_size'], 2)
        self.assertEqual(result['unique_selected_units'], 2)
        self.assertEqual(result['overlaps'], [{'key': 'a', 'strata': ['one', 'two']}])
        self.assertEqual(result['status'], 'UNREVIEWED')

    def test_unsorted_or_invalid_keys_refused(self):
        for keys in [['b', 'a'], ['a', None], ['']]:
            with self.subTest(keys=keys), self.assertRaises(GeneratorError):
                sample_strata({'x': keys}, self.config)

    def test_hash_tie_uses_stable_key(self):
        with patch('literaki_slownik.quality.sampling_digest', return_value='0' * 64):
            result = sample_strata({'x': [f'{n:03}' for n in range(40)]}, self.config)
        self.assertEqual([item['key'] for item in result['strata']['x']['selected']],
                         [f'{n:03}' for n in range(30)])

    def test_unapproved_config_changes_refused(self):
        for field, value in [('version', 'v2'), ('size_per_stratum', 31),
                             ('size_per_stratum', True), ('seed', ''),
                             ('encoding', 'concatenation'), ('extra', 1)]:
            config = {**self.config, field: value}
            with self.subTest(field=field, value=value), self.assertRaises(GeneratorError):
                sample_strata({'x': ['a']}, config)

    def test_review_template_bound_to_inputs_without_default_approval(self):
        sample = sample_strata({'one': ['a'], 'two': ['a', 'b']}, self.config)
        review = review_template(sample, canonical_index_sha256='a' * 64,
                                 evidence_sha256={'rules': 'b' * 64})
        self.assertEqual(review['canonical_index_sha256'], 'a' * 64)
        self.assertEqual(review['evidence_sha256'], {'rules': 'b' * 64})
        self.assertEqual(review['status'], 'UNREVIEWED')
        self.assertEqual(len(review['items']), 2)
        self.assertEqual(review['items'][0]['strata'], ['one', 'two'])
        for item in review['items']:
            self.assertIsNone(item['assessment'])
            self.assertIsNone(item['reviewer'])
            self.assertIsNone(item['source_justification'])
        for index, evidence in [('x', {'rules': 'b' * 64}), ('a' * 64, {}),
                                ('a' * 64, {'rules': 'x'})]:
            with self.assertRaises(GeneratorError):
                review_template(sample, canonical_index_sha256=index, evidence_sha256=evidence)

    def test_review_keeps_complete_selected_payload_and_refuses_missing_or_duplicate_units(self):
        sample=sample_strata({'word': ['a','b']}, self.config)
        sample['items']=[{'key':'a','analyses':[{'source_record':{'lemma_id':'a'},
                          'assessments':{'broad':{'membership':{'status':'unresolved'}},
                                         'standard':{'membership':{'status':'reject'}}}}]},
                         {'key':'b','evidence_unit':{'freq':7},'candidates':[{'lemma_id':'b'}]}]
        review=review_template(sample,canonical_index_sha256='a'*64,evidence_sha256={'rules':'b'*64})
        self.assertEqual(review['items'][0]['selected_unit'], sample['items'][0])
        self.assertEqual(review['items'][1]['selected_unit'], sample['items'][1])
        self.assertIsNone(review['items'][0]['assessment'])
        for items in (sample['items'][:1],sample['items']+sample['items'][:1]):
            with self.assertRaises(GeneratorError):
                review_template({**sample,'items':items},canonical_index_sha256='a'*64,
                                evidence_sha256={'rules':'b'*64})


class CorpusQualityTests(unittest.TestCase):
    def fixture(self):
        from tests.test_links import LinksTests
        from literaki_slownik.links import create_links
        import json
        owner=LinksTests();owner.setUp();self.addCleanup(owner.doCleanups);db=owner.db
        for sid,kind in [('LEMMA','kwjp_lemma'),('ORTH','kwjp_orth'),('LOWER','kwjp_orth_lc'),('BIGRAM','kwjp_bigram')]:
            db.execute('insert into source_artifact values (?,?,?)',(sid,kind,json.dumps({'genre':'fikcja','sha256':'1'*64,'publication_threshold':1})))
        rows=[(1,'LEMMA',1,'zamek',None,'subst',7),(2,'LEMMA',2,'polski',None,'adj',1),
            (3,'LEMMA',3,'brak',None,'subst',5),(4,'ORTH',1,'Róża',None,None,2),
            (5,'LOWER',1,'róża',None,None,3),(6,'BIGRAM',1,'czytał','bym',None,4)]
        for ident,sid,row,first,second,pos,freq in rows:
            metrics=json.dumps({'freq':freq,'DP':'0','DP_norm':'0.2'})
            db.execute('insert into corpus_evidence values (?,?,?,?,?,?,?,?,?)',(ident,sid,row,first,second,pos,metrics,metrics,freq))
        create_links(db);db.commit();return db

    def test_all_method_status_strata_and_full_units_without_spreading_frequency(self):
        from literaki_slownik.quality import sample_corpus_links
        from literaki_slownik.canonical import load_json
        db=self.fixture();before=db.total_changes
        sample=sample_corpus_links(db,load_json('config/generator/quality.json'))
        self.assertEqual(len(sample['strata']),16)
        self.assertEqual(sample['strata']['link:NFC_LEMMA_POS:AMBIGUOUS']['population'],1)
        self.assertEqual(sample['strata']['link:NFC_LEMMA_POS:EXACT_CANDIDATE']['population'],1)
        self.assertEqual(sample['strata']['link:NFC_LEMMA_POS:UNMATCHED']['population'],1)
        self.assertEqual(sample['strata']['link:BIGRAM_SEGMENTS:NOT_APPLICABLE']['population'],1)
        self.assertEqual(sample['strata']['link:NFC_FORM:AMBIGUOUS']['coverage'],'EMPTY_NOT_COVERAGE')
        self.assertEqual(len(sample['items']),6)
        zamek=next(i for i in sample['items'] if i['evidence']['unit_1']=='zamek')
        self.assertEqual(zamek['evidence']['typed_metrics']['freq'],7)
        self.assertEqual(len(zamek['candidates']),2)
        self.assertTrue(all('freq' not in c for c in zamek['candidates']))
        self.assertTrue(all(i['sense_identity_confirmed'] is False for i in sample['items']))
        self.assertTrue(all(i['evidence']['source_sha256']=='1'*64 for i in sample['items']))
        self.assertEqual(sample,sample_corpus_links(db,load_json('config/generator/quality.json')))
        self.assertEqual(db.total_changes,before)
        self.assertEqual(sample['status'],'UNREVIEWED')

    def test_incomplete_or_unknown_mapping_is_not_a_valid_sample(self):
        from literaki_slownik.quality import sample_corpus_links
        from literaki_slownik.canonical import load_json
        for corrupt in ('missing','method','status'):
            db=self.fixture()
            if corrupt=='missing':db.execute('delete from evidence_link where evidence_id=3')
            else:db.execute('update evidence_link set '+corrupt+'=? where evidence_id=3',('unknown',))
            with self.assertRaises(GeneratorError):sample_corpus_links(db,load_json('config/generator/quality.json'))
            db.commit()

    def test_build_writes_manifest_pinned_link_sample_without_approving_it(self):
        from tests.test_build import BuildTests
        from literaki_slownik.build import build
        from literaki_slownik.canonical import load_json
        import tempfile,json,hashlib
        from pathlib import Path
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);manifest=BuildTests().corpus_manifest(root)
            quality=root/'quality.json';quality.write_bytes(Path('config/generator/quality.json').read_bytes())
            value=load_json(manifest);value['configurations']['quality']={'path':quality.name,'sha256':hashlib.sha256(quality.read_bytes()).hexdigest()};manifest.write_text(json.dumps(value))
            run=root/'run';build(manifest,run)
            sample=load_json(run/'reports/quality-links.json')
            self.assertEqual(len(sample['items']),2)
            self.assertEqual(sample['status'],'UNREVIEWED')
            self.assertEqual(load_json(run/'manifest.json')['readiness'],'INCOMPLETE')

    def test_link_sampling_does_not_scan_all_edges_for_each_unit(self):
        from literaki_slownik.quality import sample_corpus_links
        from literaki_slownik.canonical import load_json
        db=self.fixture()
        for n in range(1000):
            ident=100+n;word='fixture'+str(n)
            db.execute('insert into surface_form values (?,?,?,?,?)',(ident,word,word,word,len(word)))
            db.execute('insert into corpus_evidence values (?,?,?,?,?,?,?,?,?)',(ident,'ORTH',ident,word,None,None,'{"freq":"1"}','{"freq":1}',1))
            db.execute('insert into evidence_link values (?,?,?,?,?)',(ident,'NFC_FORM','EXACT_CANDIDATE',0,'synthetic fixture'))
            db.execute('insert into evidence_candidate(evidence_id,form_id) values (?,?)',(ident,ident))
        db.commit();calls=0
        def budget():
            nonlocal calls
            calls+=1
            return int(calls>20000)  # 2 mln instrukcji VM; dawny skan kwadratowy przekracza.
        db.set_progress_handler(budget,100)
        try:
            sample=sample_corpus_links(db,load_json('config/generator/quality.json'))
            self.assertEqual(sample['strata']['link:NFC_FORM:EXACT_CANDIDATE']['population'],1001)
            self.assertEqual(sample['strata']['link:NFC_FORM:EXACT_CANDIDATE']['sample_size'],30)
        finally:db.set_progress_handler(None,0)


class WordQualityTests(unittest.TestCase):
    def fixture(self,root):
        import gzip
        from literaki_slownik.database import connect
        from literaki_slownik.build import import_sgjp
        from literaki_slownik.constructions import materialize_confirmed_candidates
        from literaki_slownik.decisions import materialize_assessments
        raw='#</COPYRIGHT>\nco\tco\tsubst:sg:nom.acc:n\t\t\ndar\tdar\tsubst:sg:nom:m3\t\tdaw.\nlek\tlek\tsubst:sg:nom:m3\tnazwa_pospolita\tmed.\nLek\tLek\tsubst:sg:nom:m1\tnazwisko\t\ndon\tdon:F\tfrag\t\t\ndon\tdon:S\tsubst:sg:nom:m3\t\t\ndaj\tdać\timpt:sg:sec:perf\t\t\n'
        path=root/'source.gz'
        with gzip.open(path,'wt',encoding='utf-8') as stream:stream.write(raw)
        manager=connect(root/'build.sqlite',create=True);db=manager.__enter__();self.addCleanup(manager.__exit__,None,None,None)
        db.execute('insert into source_artifact values (?,?,?)',('fixture','sgjp_tab','{"sha256":"'+('1'*64)+'","origin":"synthetic_test_only"}'))
        import_sgjp(db,{'source_id':'fixture','resolved_path':str(path)},10000);materialize_confirmed_candidates(db);materialize_assessments(db)
        return db

    def test_word_strata_equal_original_queries(self):
        """Szybkie tabele tymczasowe muszą dać te same warstwy co pierwotne pełne zapytania."""
        from literaki_slownik.quality import sample_word_analyses
        from literaki_slownik.canonical import load_json
        from pathlib import Path
        import tempfile
        with tempfile.TemporaryDirectory() as folder:
            db=self.fixture(Path(folder))
            sample=sample_word_analyses(db,load_json('config/generator/quality.json'),load_json('config/generator/quality-words.json'))
            count=lambda sql,args=(): db.execute('select count(*) from ('+sql+')',args).fetchone()[0]
            classes={r[0] for r in db.execute("select distinct case when instr(expanded_tag,':')>0 then substr(expanded_tag,1,instr(expanded_tag,':')-1) else expanded_tag end from analysis where interpretation_id is not null")}|{'praet','winien'}
            expected={'word:source_class:'+pos:count("select distinct game_key from analysis where interpretation_id is not null and (expanded_tag=? or expanded_tag like ?)",(pos,pos+':%')) for pos in classes}
            for variant in ('broad','standard'):
                join="select a.game_key from analysis a join variant_decision d on d.analysis_key=a.analysis_key where d.variant=? group by a.game_key having "
                expected['word:unresolved:'+variant]=count(join+"max(d.membership_status='accept')=0 and max(d.membership_status='unresolved')=1",(variant,))
                expected['word:filter_changed:'+variant]=count(join+"min(d.membership_status='reject')=1",(variant,))
            self.assertGreater(expected['word:filter_changed:standard'],0)
            for name,population in expected.items():
                self.assertEqual(sample['strata'][name]['population'],population,name)

    def test_required_word_strata_complete_analyses_and_both_variants(self):
        from literaki_slownik.quality import sample_word_analyses
        from literaki_slownik.canonical import load_json
        from pathlib import Path
        import tempfile
        with tempfile.TemporaryDirectory() as folder:
            db=self.fixture(Path(folder));before=db.total_changes
            sample=sample_word_analyses(db,load_json('config/generator/quality.json'),load_json('config/generator/quality-words.json'))
            self.assertEqual(sample['strata']['word:homonyms']['population'],2)
            self.assertEqual(sample['strata']['word:source_class:subst']['population'],4)
            self.assertEqual(sample['strata']['word:source_class:winien']['coverage'],'EMPTY_NOT_COVERAGE')
            self.assertEqual(sample['strata']['word:history']['population'],1)
            self.assertEqual(sample['strata']['word:specialist']['population'],1)
            self.assertEqual(sample['strata']['word:proper_common']['population'],1)
            self.assertEqual(sample['strata']['word:construction:impt-single-particle-v1']['population'],1)
            self.assertEqual(sample['strata']['word:construction:impt-double-particle-v1']['population'],1)
            co=next(x for x in sample['items'] if x['game_key']=='co')
            self.assertEqual(len(co['analyses']),2)  # Rozwinięcia jednego ID nie są homonimami.
            self.assertEqual(set(co['membership']),{'broad','standard'})
            dar=next(x for x in sample['items'] if x['game_key']=='dar')
            self.assertEqual(dar['membership']['broad']['status'],'accept')
            self.assertEqual(dar['membership']['standard']['status'],'reject')
            derived=next(x for x in sample['items'] if x['game_key']=='dajże')
            self.assertTrue(derived['analyses'][0]['candidate']['components'])
            self.assertEqual(set(derived['analyses'][0]['assessments']),{'broad','standard'})
            self.assertTrue(all(x['source_record'] for x in co['analyses']))
            self.assertEqual(sample,sample_word_analyses(db,load_json('config/generator/quality.json'),load_json('config/generator/quality-words.json')))
            self.assertEqual(before,db.total_changes);self.assertEqual(sample['status'],'UNREVIEWED')

    def test_build_uses_pinned_word_definitions_and_writes_sample(self):
        from tests.test_build import BuildTests
        from literaki_slownik.build import build
        from literaki_slownik.canonical import load_json
        from pathlib import Path
        import tempfile,json,hashlib
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);manifest=BuildTests().corpus_manifest(root);value=load_json(manifest)
            for name,file in [('quality','quality.json'),('quality-words','quality-words.json')]:
                target=root/file;target.write_bytes(Path('config/generator',file).read_bytes())
                value['configurations'][name]={'path':file,'sha256':hashlib.sha256(target.read_bytes()).hexdigest()}
            manifest.write_text(json.dumps(value));run=root/'run';build(manifest,run)
            self.assertEqual(load_json(run/'reports/quality-words.json')['strata']['word:homonyms']['population'],1)
            self.assertEqual(load_json(run/'reports/quality-words.json')['status'],'UNREVIEWED')
            self.assertEqual(load_json(run/'manifest.json')['readiness'],'INCOMPLETE')
