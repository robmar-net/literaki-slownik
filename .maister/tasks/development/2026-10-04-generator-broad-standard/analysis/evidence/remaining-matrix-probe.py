"""Przegląd pełnych przypiętych wejść; bez aktywacji kryteriów i modyfikacji baz."""
import argparse,json,re
from collections import Counter
from pathlib import Path
from literaki_slownik.canonical import sha256,write_json,dumps
from literaki_slownik.database import connect
from literaki_slownik.constructions import (SOURCE_FIELDS,MOBILE_BY_HOSTS,MOBILE_AGLT_HOSTS,MOBILE_BY_SEQUENCE_HOSTS,
    by_aglt_candidates,mobile_by_aglt_candidates,mobile_aglt_candidates,mobile_by_sequence_candidates)
from literaki_slownik.decisions import assess_diagnostic
from literaki_slownik.policy import KNOWN_NAME_LABELS
from literaki_slownik.sgjp import tag_size

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--source-run',required=True);parser.add_argument('--output',required=True)
    args=parser.parse_args();root=Path(args.source_run);database=root/'build.sqlite';before=sha256(database)
    segments=Path('cache/sgjp-docs/Morfeusz/input/segmenty.dat');segment_hash=sha256(segments)
    assert segment_hash=='73fca7c4cd5a1cd0db5cd6367b098ec96a6fb01481a0eb441f3b24aa9ca4521c'
    definitions={}
    for n,line in enumerate(segments.read_text().splitlines(),1):
        fields=line.split()
        if len(fields)==3 and fields[0] in {'z_aglt','z_aglt_by','z_aglt_nwok','z_aglt_nwok2'}:
            definitions.setdefault(tuple(fields),[]).append(n)
    assert len(definitions)==70
    others={(lemma,tag) for cls,lemma,tag in definitions if cls!='z_aglt_by'}
    by={(lemma,tag) for cls,lemma,tag in definitions if cls=='z_aglt_by' and lemma!='by'}
    sequence={(lemma,tag) for cls,lemma,tag in definitions if cls in {'z_aglt','z_aglt_nwok'}}
    assert others==set(MOBILE_AGLT_HOSTS) and by==set(MOBILE_BY_HOSTS.items()) and sequence==MOBILE_BY_SEQUENCE_HOSTS
    query='''select i.source_id,i.first_row,f.original,l.lemma_id,i.tag,i.names,i.qualifiers
        from interpretation i join surface_form f on f.id=i.form_id join lexeme l on l.id=i.lexeme_id'''
    hosts=[];cases=[]
    with connect(database,readonly=True) as db:
        endings=[dict(zip(SOURCE_FIELDS,r)) for r in db.execute(query+" where i.tag like 'aglt:%' order by i.first_row")]
        operators=[dict(zip(SOURCE_FIELDS,r)) for r in db.execute(query+" where f.original='by' and i.tag in ('comp','part') order by i.first_row")]
        for (cls,lemma,pattern),lines in sorted(definitions.items()):
            rows=[dict(zip(SOURCE_FIELDS,r)) for r in db.execute(query+" where l.lemma_base=? and i.tag like ? order by i.first_row",(lemma,pattern))]
            assert rows
            seen=set();counts=Counter();variants=Counter()
            for host in rows:
                generated=[]
                for ending in endings:
                    if cls=='z_aglt_by' and not ending['raw_tag'].endswith(':nwok'):continue
                    generated+=(by_aglt_candidates(host,ending) if lemma=='by' else mobile_by_aglt_candidates(host,ending)) if cls=='z_aglt_by' else mobile_aglt_candidates(host,ending)
                if cls in {'z_aglt','z_aglt_nwok'}:
                    for op in operators:
                        for ending in [None]+[a for a in endings if a['raw_tag'].endswith(':nwok')]:generated+=mobile_by_sequence_candidates(host,op,ending)
                for candidate in generated:
                    key=dumps(candidate);assert key not in seen;seen.add(key);counts[candidate['rule_id']]+=1
                    sources=[c['interpretation'] for c in candidate['components'] if c['kind']=='source_interpretation']
                    assert all(s['source_id']==host['source_id'] for s in sources)
                    for field in ('names','qualifiers'):
                        expected='|'.join(sorted({label for s in sources for label in s[field].split('|') if label}))
                        assert candidate[field]==expected
                    if 'host_variant_evidence' in candidate:variants[candidate['host_variant_evidence']['source_class_variant']+'→'+candidate['host_variant_evidence']['form_variant']]+=1
            assert seen
            hosts.append({'source_class':cls,'lemma_base':lemma,'tag_pattern':pattern,'definition_lines':lines,
                'source_compact_records':len(rows),'by_rule':dict(sorted(counts.items())),
                'variant_annotation_candidates':dict(variants),'coverage':'COMPLETE_CLOSED_SOURCE_HOST_DEFINITION_NOT_FINAL_QUALIFICATION'})
        mixed=[]
        for row in db.execute(query+" where instr(i.names,'nazwa_pospolita')>0 order by i.first_row"):
            source=dict(zip(SOURCE_FIELDS,row));labels=set(source['names'].split('|'))
            if labels & (KNOWN_NAME_LABELS-{'nazwa_pospolita'}):
                value=assess_diagnostic(source['original'],source['qualifiers'],source_analyses=[source])
                assert value['game']['status']=='reject'
                assert any(c['rule_id']=='game-required-uppercase-v1' and c['status']=='reject' for c in value['game']['checks'])
                mixed.append({'source':source,'expanded':tag_size(source['raw_tag']),'known_rejection':'game-required-uppercase-v1'})
        assert len(mixed)==295
        for row in db.execute(query+" where i.tag='frag' or instr(i.qualifiers,'pisane_łącznie_z_przyimkiem')>0 order by i.first_row"):
            source=dict(zip(SOURCE_FIELDS,row));value=assess_diagnostic(source['original'],source['qualifiers'],source_analyses=[source])
            cases.append({'source':source,'expanded':tag_size(source['raw_tag']),
                'conditions':{variant:{'membership':value['membership'][variant]['status'],
                    'known_reject_rules':sorted({c['rule_id'] for c in value['membership'][variant]['checks'] if c['status']=='reject'})}
                    for variant in ('broad','standard')},
                'scope':'existing_rules_only_not_semantic_completion'})
        assert len(cases)==149 and db.total_changes==0
    assert before==sha256(database)
    summary={v:{'frag_compact':147,'frag_with_independent_rejection':sum(x['source']['raw_tag']=='frag' and bool(x['conditions'][v]['known_reject_rules']) for x in cases),
               'frag_without_independent_rejection':sum(x['source']['raw_tag']=='frag' and not x['conditions'][v]['known_reject_rules'] for x in cases)} for v in ('broad','standard')}
    write_json(Path(args.output),{'schema_version':1,'scope':'full_closed_host_definitions_and_known_semantic_gap_cases_not_full_release',
        'database_sha256':before,'segments_sha256':segment_hash,'source_unchanged':True,'host_definitions':hosts,
        'host_matrix':{'definitions':70,'by_hosts_excluding_by':16,'other_hosts':53,'sequence_hosts':47,'missing':[],
            'meaning':'Complete registration and source exercise; no permissive generation; not complete lexical/game qualification.'},
        'mixed_name_compact':295,'mixed_name_expanded':sum(x['expanded'] for x in mixed),
        'mixed_names_independently_rejected':True,'mixed_name_cases':mixed,
        'frag_summary':summary,'semantic_cases':cases,'full_qualification_pending':True})
    print(json.dumps({'hosts':70,'mixed':len(mixed),'frag':summary}))
if __name__=='__main__':main()
