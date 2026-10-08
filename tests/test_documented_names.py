"""Dokumentacyjna odmowa growa nie usuwa wpisu ani homonimu."""
import unittest
from literaki_slownik.policy import source_game_checks
from literaki_slownik.decisions import assess_diagnostic, aggregate

SHA = '3b2ee079143bc95186370fd528735779c4ba62f4ce14e30cf6622ceb566e9810'
RULE = 'game-documented-surname-component-v1'

def source(form, lemma, row):
    return dict(source_id='sgjp-20260823', source_sha256=SHA,
                first_source_row=row, original=form, lemma_id=lemma,
                raw_tag='frag', names='', qualifiers='')

class DocumentedNamesTests(unittest.TestCase):
    def test_exact_cases_rejected_in_both_variants_with_unknowns_retained(self):
        for s in (source('de','de:F',1463128), source('ibn','ibn',1960055)):
            a=assess_diagnostic(s['original'],'',source_analyses=[s])
            self.assertEqual(a['game']['status'],'reject')
            self.assertTrue(any(c['rule_id']==RULE for c in a['game']['checks']))
            # Runda 3: brak zastępczych niewiadomych; odmowa nadal ma własną regułę.
            self.assertFalse(any(c['status']=='unresolved' for c in a['game']['checks']))
            for v in ('broad','standard'):
                self.assertEqual(a['membership'][v]['status'],'reject')
                self.assertEqual(a['language'][v]['status'],'accept')

    def test_no_propagation_to_changed_source_or_homonym(self):
        s=source('de','de:F',1463128)
        for field,value in dict(source_id='other',source_sha256='0'*64,
                first_source_row=1463129,original='DE',lemma_id='de:S',raw_tag='subst',
                names='nazwa_pospolita',qualifiers='książk.').items():
            changed=dict(s,**{field:value})
            self.assertFalse(any(c['rule_id']==RULE for c in source_game_checks(changed)),field)
            missing=dict(s);missing.pop(field)
            if field not in {'raw_tag','names','qualifiers'}:
                self.assertFalse(any(c['rule_id']==RULE for c in source_game_checks(missing)),field)
        noun=dict(s,first_source_row=1463129,lemma_id='de:S',
                  raw_tag='subst:sg:nom:n:ncol',names='nazwa_pospolita')
        a=assess_diagnostic('de','',source_analyses=[noun])
        self.assertEqual(a['game']['status'],'accept')
        frag=assess_diagnostic('de','',source_analyses=[s])
        self.assertEqual(aggregate([frag,a],'standard')['status'],'accept')

    def test_complete_construction_does_not_inherit_fragment_class(self):
        s=source('de','de:F',1463128)
        checks=source_game_checks(s,candidate={'rule_id':'impt-single-particle-v1'})
        self.assertFalse(any(c['rule_id']==RULE for c in checks))

    def test_persisted_and_live_explain_agree_on_exact_source_identity(self):
        import tempfile,json
        from pathlib import Path
        from literaki_slownik.database import connect
        from literaki_slownik.decisions import materialize_assessments
        from literaki_slownik.explain import explain
        with tempfile.TemporaryDirectory() as folder:
            r=Path(folder)
            with connect(r/'build.sqlite',create=True) as db:
                sid='sgjp-20260823'
                db.execute('insert into source_artifact values (?,?,?)',(sid,'sgjp_tab',json.dumps({'sha256':SHA,'origin':'synthetic_test_only'})))
                for i,s in enumerate((source('de','de:F',1463128),source('ibn','ibn',1960055)),1):
                    row=s['first_source_row'];word=s['original'];lemma=s['lemma_id']
                    db.execute('insert into sgjp_record values (?,?,?,?,?,?,?)',(sid,row,word,lemma,'frag','',''))
                    db.execute('insert into surface_form values (?,?,?,?,?)',(i,word,word,word,len(word)))
                    db.execute('insert into lexeme values (?,?,?,?)',(i,sid,lemma,word))
                    db.execute('insert into interpretation values (?,?,?,?,?,?,?,?)',(i,sid,row,i,i,'frag','',''))
                materialize_assessments(db)
                self.assertEqual(materialize_assessments(db)['new_analyses'],0)
            (r/'manifest.json').write_text(json.dumps({'schema_version':1,'readiness':'INCOMPLETE',
                'stages':{'import_sgjp':{'status':'complete'}},'inputs':{'manifest':{'unavailable':[]}}}))
            for word in ('de','ibn'):
                result=explain(r,word)
                self.assertEqual(result['analyses'][0]['assessment']['game']['status'],'reject')
                # Odczyt nie gubi przypiętej tożsamości ani powodów po zapisie.
                self.assertEqual(result['persisted_analyses'][0]['assessment']['game']['status'],'reject')
