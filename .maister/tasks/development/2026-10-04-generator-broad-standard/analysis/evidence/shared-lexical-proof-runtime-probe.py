"""Dwie nowe projekcje kolejnych użyć frazeologicznych; oryginalna baza wyłącznie readonly."""
import argparse
import json
from datetime import datetime,timezone
from pathlib import Path
from literaki_slownik.canonical import sha256,write_json,dumps
from literaki_slownik.database import connect
from literaki_slownik.decisions import materialize_assessments,persisted_assessments
from literaki_slownik.constructions import materialize_confirmed_candidates
from literaki_slownik.reports import logical_content_report,unresolved_report,persisted_filter_impact
from literaki_slownik.quality import sample_persisted_analyses
from literaki_slownik.explain import explain,format_explanation
from literaki_slownik.policy import standard_age_baseline_checks
from literaki_slownik.decisions import assessment


def main():
    p=argparse.ArgumentParser();p.add_argument('--source-run',required=True);p.add_argument('--output',required=True)
    args=p.parse_args();source=Path(args.source_run);source_hash=sha256(source/'build.sqlite')
    reviews=[r for r in json.loads(Path('config/generator/semantic-uses.json').read_text())['reviews']
             if 'lexical_proof' in r]
    assert len(reviews)==6
    keys=sorted({r['source']['original'] for r in reviews})
    config=json.loads(Path('config/generator/quality.json').read_text())
    stamp=datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S');outputs=[]
    with connect(source/'build.sqlite',readonly=True) as src:
        rows=src.execute('''select i.* from interpretation i join surface_form f on f.id=i.form_id
            where f.game_key in ('''+','.join('?' for _ in keys)+') order by i.source_id,i.first_row',keys).fetchall()
        for label in ('a','b'):
            root=Path('data/work')/('shared-lexical-use-'+stamp+'-'+label);root.mkdir()
            with connect(root/'build.sqlite',create=True) as db:
                db.execute('insert into source_artifact values (?,?,?)',src.execute(
                    "select * from source_artifact where source_id='sgjp-20260823'").fetchone())
                for row in rows:
                    raw=src.execute('select * from sgjp_record where source_id=? and row_number=?',(row[1],row[2])).fetchone()
                    db.execute('insert into sgjp_record values (?,?,?,?,?,?,?)',raw)
                    for table,ident in [('lexeme',row[4]),('surface_form',row[3])]:
                        values=src.execute('select * from '+table+' where id=?',(ident,)).fetchone()
                        db.execute('insert or ignore into '+table+' values ('+','.join('?' for _ in values)+')',values)
                    db.execute('insert into interpretation values (?,?,?,?,?,?,?,?)',row)
                original=db.execute('select * from sgjp_record').fetchall()
                materialize_confirmed_candidates(db)
                counts=materialize_assessments(db,use_reviews=reviews);logical=logical_content_report(db)
                assert materialize_assessments(db,use_reviews=list(reversed(reviews)))['new_analyses']==0
                assert logical==logical_content_report(db)
                assert original==db.execute('select * from sgjp_record').fetchall()
                assert not db.execute('pragma foreign_key_check').fetchall()
                assert db.execute('pragma integrity_check').fetchone()[0]=='ok'
                sample=sample_persisted_analyses(db,config);assert sample==sample_persisted_analyses(db,config)
                unknown=unresolved_report(db);impact=persisted_filter_impact(db)
                for key in keys:
                    for variant in ('broad','standard'):
                        rs=persisted_assessments(db,key,variant)
                        uses=[r for r in rs if r.get('semantic_trace',{}).get('kind')=='documented_use']
                        rest=[r for r in rs if r.get('semantic_trace',{}).get('kind')=='unresolved_remainder']
                        assert uses and rest
                        for item in uses+rest:
                            expected_age=standard_age_baseline_checks(item['semantic_trace']['source']['qualifiers'],variant)
                            actual_age=[c for c in item['assessment']['language']['checks'] if c['rule_id']=='linguistic-standard-age-baseline-v1']
                            assert actual_age==expected_age
                        assert all(any(c['rule_id']=='linguistic-documented-use-lexical-proof-v1' and c['status']=='accept' for c in r['assessment']['language']['checks']) for r in uses)
                        assert all(not any(c['rule_id']=='linguistic-documented-use-lexical-proof-v1' for c in r['assessment']['language']['checks']) for r in rest)
            manifest=json.loads((source/'manifest.json').read_text());manifest['readiness']='INCOMPLETE'
            manifest['scope']='source_paradigm_and_all_matching_homonyms_diagnostic_projection'
            write_json(root/'manifest.json',manifest)
            before=sha256(root/'build.sqlite');queries=0
            for key in keys:
                for variant in ('broad','standard'):
                    value=explain(root,key,variant);text=format_explanation(value)
                    assert 'linguistic-documented-use-lexical-proof-v1' in text
                    assert value['source_aggregation']['status'] in ('unresolved','reject')
                    queries+=1
            assert before==sha256(root/'build.sqlite')
            outputs.append({'run':str(root),'assessments':counts,'logical_content':logical,
                'unresolved':unknown,'filter_impact':impact,'sample_sha256':__import__('hashlib').sha256(dumps(sample).encode()).hexdigest(),
                'readonly_explain':queries,'fk':'ok','integrity':'ok','repeat_new_analyses':0})
        assert src.total_changes==0
    assert source_hash==sha256(source/'build.sqlite')
    assert outputs[0]['logical_content']==outputs[1]['logical_content']
    assert outputs[0]['sample_sha256']==outputs[1]['sample_sha256']
    result={'schema_version':1,'scope':'six_documented_uses_shared_lexical_proof_all_homonyms_not_full_build',
        'source_db_sha256':source_hash,'source_unchanged':True,'source_compact_records':len(rows),
        'independent_logical_content_equal':True,'independent_samples_equal':True,
        'outputs':outputs,'final_list_delta':'pending_full_qualification'}
    write_json(Path(args.output),result)
    print(json.dumps({'source_records':len(rows),'counts':counts,'queries':queries*2,'equal':True}))

if __name__=='__main__':main()
