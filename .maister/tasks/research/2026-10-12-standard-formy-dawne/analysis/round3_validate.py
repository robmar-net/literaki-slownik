"""Niezależny od generatora propozycji odczyt utrwalonych decyzji STANDARD."""
import collections
import hashlib
import json
import sqlite3
import subprocess
from pathlib import Path

TASK=Path(__file__).resolve().parents[1]
ROOT=TASK.parents[3]
OUT=TASK/'analysis/findings/round3'
def read(n):return json.loads((OUT/n).read_text())

def main():
    proposal=read('proposal.json'); proof=read('proposal-proof.json')
    words=set(proposal['new_words'])
    assert len(words)==proposal['counts']['new']==proof['words']
    assert words=={r['word'] for r in proof['cases']}
    families={r['lemma_id']:r for r in read('family-decisions.json')}
    for r in families.values():
        if r['status']!='hold':assert len(set(r['documents']))>=2,(r['lemma_id'],r['documents'])
    db=sqlite3.connect(f'file:{ROOT}/data/work/lists-v30-20261010-165826-a/build.sqlite?mode=ro',uri=True)
    db.execute('pragma query_only=on')
    payload={k:json.loads(v) for k,v in db.execute('select assessment_key,assessment from decision_payload')}
    safe=set()
    for key,p in payload.items():
        checks=[c for layer in ('language','game','profile','release_scope') for c in p[layer]['checks']]
        if any(c['rule_id']=='linguistic-historical-form-v1' and c['status']=='reject' for c in checks) and all(c['status']=='accept' or (c['rule_id']=='linguistic-historical-form-v1' and c['status']=='reject') for c in checks):safe.add(key)
    query='''select coalesce(l.lemma_id,c.lemma_id),a.expanded_tag,a.candidate_key is not null,d.membership_status,d.assessment_key
      from analysis a indexed by analysis_game_key join variant_decision d on d.analysis_key=a.analysis_key
      left join interpretation i on i.id=a.interpretation_id left join lexeme l on l.id=i.lexeme_id
      left join derivation_candidate c on c.candidate_key=a.candidate_key
      where a.game_key=? and +d.variant='standard' '''
    checked=0
    for r in proof['cases']:
        rows=list(db.execute(query,(r['word'],)))
        assert not any(v[3]=='accept' for v in rows),r['word']
        for a in r['analyses']:
            assert families[a['lemma_id']]['status']!='hold'
            assert any((v[0],v[1],bool(v[2]))==(a['lemma_id'],a['tag'],a['derived']) and v[4] in safe for v in rows),(r['word'],a)
            checked+=1
    matrix=read('candidate-matrix.json')['cases'];original={v['word'] for r in matrix for v in r['forms']}
    assert len(matrix)==404 and len(original)==3364
    assert len(original&words)==proposal['counts']['from_previous_3364']
    current=read('current-review.json'); assert len(current['cases'])==current['words']==290
    assert sum(current['status_counts'].values())==290
    assert len(current['unsupported_evidence_words'])==12
    negatives=['desperacyj','atencyj','dokumenta','klasztora','wywre','umorach','premiów','zasłonionemu','mielszy','spękany','konkludowany']
    assert not words.intersection(negatives)
    positives=['desperacja','ekscytacją','niezbędnik','sołtyska','sztaluga','szuwar','przechwałka','pryncypium','naście','aktuariusz','moderowana']
    assert set(positives)<=words,set(positives)-words
    baseline=read('pop-baseline.json');impact=read('pop-impact.json')
    assert baseline['baseline_matches_published_lists']
    assert impact['proposal_sha256']==hashlib.sha256((OUT/'proposal.json').read_bytes()).hexdigest()
    assert impact['standard_delta']=={'added':len(words),'removed':0}
    for name in ('pop','pop0'):
        d=impact['deltas'][name]
        assert set(d['added']).isdisjoint(d['removed'])
        assert d['net']==len(d['added'])-len(d['removed'])
        assert baseline['lists'][name]['forms']+d['net']==impact['lists'][name]['forms']
        assert impact['frequent_guard'][name]['missing']==0
    result={'status':'passed','checked_proposed_words':len(words),'checked_proposed_analyses':checked,
      'all_proposed_analyses_reject_only_history':True,'matrix_groups':404,'matrix_unique_words':3364,'current_words':290,
      'negative_controls':negatives,'positive_controls':positives,'database_sha256_after_simulation':impact['database_unchanged_sha256'],
      'review_limit':'Ocena semantyki przez jednego badacza; SQL nie dowodzi trafności tej oceny.',
      'checked_at':subprocess.check_output(['date','-u','+%Y-%m-%dT%H:%M:%SZ'],text=True).strip()}
    (OUT/'validation.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(result,ensure_ascii=False))

if __name__=='__main__':main()
