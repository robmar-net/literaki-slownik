#!/usr/bin/env python3
"""Audyt własnych obserwacji czytnika; bez importu glos i aktywacji polityki."""
import argparse
import hashlib
import json
import re
from collections import Counter
from pathlib import Path

MAPPINGS=frozenset({'unique_spelling_class_candidate_not_snapshot_identity',
    'multiple_articles_not_snapshot_identity','embedded_use_in_parent_article_not_snapshot_identity'})
CLASSES=frozenset({'phrase_component','proper_name_component','surname_component','article','noun_parent_with_phrase_note'})

def audit(cases,review):
    if (review.get('schema_version')!=1 or review.get('scope')!='public_reader_reference_observations'
            or review.get('automatic_eligibility_decisions') is not False
            or review.get('raw_articles_committed') is not False
            or type(review.get('active_build_inputs_added')) is not int
            or review['active_build_inputs_added']!=0):
        raise ValueError('Odczyt referencyjny nie może aktywować wejść lub kwalifikacji')
    by_id={c['case_id']:c for c in cases['cases']};seen=set();counts=Counter();classes=Counter();articles=0
    if len(by_id)!=len(cases['cases']):raise ValueError('Powtórzony przypadek źródłowy')
    for r in review['records']:
        cid=r['case_id'];mapping=r['mapping_status'];notes=r['articles']
        if cid not in by_id or cid in seen or r['pinned_source']!=by_id[cid]['source']:
            raise ValueError('Niezgodna lub powtórzona tożsamość źródłowa')
        if r['eligibility_status']!='unresolved' or mapping not in MAPPINGS:
            raise ValueError('Odczyt nie dowodzi zgodności snapshotu ani pełnego znaczenia')
        if (not isinstance(notes,list) or not notes or
                (mapping!='multiple_articles_not_snapshot_identity' and len(notes)!=1) or
                (mapping=='multiple_articles_not_snapshot_identity' and len(notes)<2)):
            raise ValueError('Niezgodna liczba kandydatów artykułu')
        ids=set()
        for a in notes:
            wid=a['web_lexeme_id'];cls=a['own_class_observation']
            if (type(wid) is not int or wid<=0 or wid in ids or cls not in CLASSES
                    or not re.fullmatch('[0-9a-f]{64}',a['response_sha256'])
                    or not re.fullmatch(r'https://sgjp\.pl/leksemy/#'+str(wid)+r'(?:/[^#]*)?',a['url'])):
                raise ValueError('Nieprawidłowa obserwacja lub odsyłacz')
            ids.add(wid);classes[cls]+=1;articles+=1
        if (mapping=='embedded_use_in_parent_article_not_snapshot_identity') != any(a['own_class_observation']=='noun_parent_with_phrase_note' for a in notes):
            raise ValueError('Użycie w artykule nadrzędnym wymaga jawnego rozróżnienia')
        seen.add(cid);counts[mapping]+=1
    if seen!=set(by_id):raise ValueError('Brak odczytu któregoś przypadku źródłowego')
    return {'schema_version':1,'scope':'reader_observation_coverage_not_qualification',
        'source_cases':len(seen),'article_observations':articles,
        'mapping_statuses':dict(sorted(counts.items())), 'own_class_observations':dict(sorted(classes.items())),
        'source_snapshot_alignment_confirmed':False,'full_semantics_complete':False,
        'automatic_eligibility_decisions':False,'active_build_inputs_added':0}

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--cases',required=True);p.add_argument('--review',required=True);p.add_argument('--output',required=True);a=p.parse_args()
    try:
        raw=Path(a.cases).read_bytes();cases=json.loads(raw);review=json.loads(Path(a.review).read_text())
        if hashlib.sha256(raw).hexdigest()!=review['cases_sha256']:raise ValueError('Inny snapshot przypadków')
        result=audit(cases,review)
        with Path(a.output).open('x',encoding='utf-8') as f:json.dump(result,f,ensure_ascii=False,sort_keys=True,indent=2);f.write('\n')
    except (ValueError,KeyError,TypeError,OSError) as e:p.exit(4,str(e)+'\n')
if __name__=='__main__':main()
