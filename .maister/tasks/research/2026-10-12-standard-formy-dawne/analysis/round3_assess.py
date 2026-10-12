"""Symulowana, ręcznie uzasadniona paczka; bez zmian polityki i bazy."""
import collections
import hashlib
import json
import re
import sqlite3
from pathlib import Path

TASK=Path(__file__).resolve().parents[1]
ROOT=TASK.parents[3]
OUT=TASK/'analysis/findings/round3'
TMP=ROOT/'tmp/research-issue4'
AGE=re.compile(r'\b(?:daw|przest|arch)\.')

def read(p): return json.loads(p.read_text())
def save(name,o): (OUT/name).write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n')

def main():
    families={r['lemma_id']:r for r in read(OUT/'family-decisions.json')}
    tables=read(TMP/'round3-full-tables.json')
    relations=set(read(OUT/'full-tables-manifest.json')['relations'])
    source={}; blocked={}; traversal={}
    for lid,r in families.items():
        if r['status']=='hold':continue
        todo=[(a,[]) for a in r['article_ids']]; seen=set(); forms=collections.defaultdict(list);excluded=collections.defaultdict(list)
        while todo:
            aid,path=todo.pop();aid=str(aid)
            if aid in seen:continue
            seen.add(aid); t=tables[aid]
            child_age=bool(path and AGE.search(' '.join(t['headers'])))
            for f in t['forms']:
                word=re.sub(r'\s+(?:\(z D\.\)|z D\.)$','',f['word'])
                meta={'article_id':int(aid),'path':path,'row':f['row'],'qualifiers':f['qualifiers'],'reader_text':f['word']}
                old=child_age or bool(AGE.search(' '.join(f['qualifiers'])))
                (excluded if old else forms)[word].append(meta)
            if not child_age:
                todo.extend((v['id'],path+[v['relation']]) for v in t['links'] if v['relation'] in relations)
        source[lid]=forms;blocked[lid]=excluded;traversal[lid]=sorted(map(int,seen))

    def supported(word,lid,tag):
        if lid not in source:return None
        rule=families[lid]
        if tag.split(':')[0] in rule.get('exclude_pos',[]):return None
        if isinstance(rule['scope'],list) and word not in rule['scope']:return None
        if word in source[lid]: return {'method':'reader_exact','word':word,'source':source[lid][word]}
        if word in blocked[lid]:return None
        # To nie generator nowych słów: badamy tylko istniejącą analizę z przypiętego eksportu.
        # Czytnik prezentuje dodatnią postać imiesłowu/odsłownika i stopień wyższy.
        base=word; steps=[]
        if ':neg' in tag and tag.split(':')[0] in ('pact','ppas','ger') and base.startswith('nie'):
            base=base[3:];steps.append('negative_in_pinned_analysis')
        if ':sup' in tag and tag.split(':')[0] in ('adj','adv') and base.startswith('naj'):
            base=base[3:];steps.append('superlative_in_pinned_analysis')
        if steps and base in source[lid]:
            return {'method':'+'.join(steps),'word':base,'source':source[lid][base]}
        return None

    standard=set((ROOT/'data/work/lists-v30-20261010-165826-a/lists/standard.txt').read_text().splitlines())
    raw=read(TMP/'candidates.json')
    examined=[r for r in raw if r[1] in source and r[0] not in standard]
    db=sqlite3.connect(f'file:{ROOT}/data/work/lists-v30-20261010-165826-a/build.sqlite?mode=ro',uri=True)
    db.execute('pragma query_only=on')
    payloads={}
    for word in sorted({r[0] for r in examined if r[5]}):
        payloads[word]=[json.loads(row[0]) for row in db.execute('select payload from derivation_candidate indexed by derivation_game_key where game_key=?',(word,))]
    proof=collections.defaultdict(list);unmatched=collections.defaultdict(set)
    for word,lid,base,tag,labels,derived in examined:
        evidence=None
        if 'arch.' not in labels:
            if not derived:evidence=supported(word,lid,tag)
            else:
                for candidate in payloads[word]:
                    if candidate['lemma_id']!=lid or candidate['expanded_tag']!=tag:continue
                    parts=[c['interpretation'] for c in candidate['components'] if c['kind']=='source_interpretation']
                    supports=[supported(p['original'],p['lemma_id'],p['raw_tag']) for p in parts]
                    if supports and all(supports) and all('arch.' not in p['qualifiers'] for p in parts):
                        evidence={'method':'existing_qualified_construction','rule_id':candidate['rule_id'],'components':supports};break
        if evidence: proof[word].append({'lemma_id':lid,'tag':tag,'labels':labels,'derived':bool(derived),'proof':evidence})
        else:unmatched[lid].add(word)
    new=set(proof)
    census=[r for r in read(OUT.parent/'round2/census-1580.json') if r['new_noarch']]
    original={w for r in census for w in r['new_noarch']}
    assert len(census)==404 and len(original)==3364
    oldreview=read(OUT.parent/'round2/live-review.json')['cases']
    details=read(TMP/'candidate-details.json')
    old_by_lid=collections.defaultdict(list)
    for r in oldreview:
        for lid in {v[0] for v in details.get(r['word'],[])}:old_by_lid[lid].append(r['word'])
    current=read(OUT/'context-review.json')['cases']
    current_by_lid=collections.defaultdict(list)
    for r in current:
        for lid in {a[0] for a in r['accepted_analyses']}:current_by_lid[lid].append(r['word'])
    searches={r['word']:r for r in read(OUT/'sgjp-manifest.json')['cases']}
    matrices=[]
    # Nierozstrzygnięcie oznacza brak wystarczającego dowodu tej rodziny, nie zakaz słowa.
    for r in census:
        lid=r['lemma_id'];words=set(r['new_noarch']);own={w for w in words if any(v['lemma_id']==lid for v in proof.get(w,[]))}
        family=families.get(lid)
        if own:status='proposed_scope';reason=family['meaning_note']
        elif family and family['status']=='hold':status='conflict_or_insufficient';reason=family['meaning_note']
        elif family:status='outside_confirmed_scope';reason='Żywe znaczenie potwierdzone, lecz te formy nie mieszczą się w sprawdzonej odmianie/konstrukcji.'
        else:
            status='insufficient_scope_evidence'
            reason='Odczytano identyfikację i kwalifikatory SGJP oraz zestawiono dostępne konkordancje. Nie ustalono dostatecznego kontrdowodu dla znaczenia i dokładnej odmiany tych kandydatów.'
            controls=[x for x in current if x['word'] in current_by_lid[lid]]
            limited=[x for x in controls if x['status']=='limited_construction']
            disputed=[x for x in controls if x['status'] in ('scope_or_register_unresolved','mixed_scoped_evidence','accepted_analysis_not_supported')]
            tags=[t for x in r['forms'] if x['word'] in words for t in x['tags']]
            if limited:
                reason='Poświadczona ograniczona konstrukcja nie uzasadnia tych form całego paradygmatu. '+limited[0]['note']
            elif disputed:reason='Dostępne użycia nie rozstrzygają zakresu kandydackich analiz. '+disputed[0]['note']
            elif tags and all(':com' in t or ':sup' in t for t in tags):
                reason='Kandydaci dotyczą stopniowania. Żywy stopień równy nie podważa dodatkowej dawności wariantu stopnia wyższego; brak odrębnego kontrdowodu dla wskazanych form.'
            specific={
              'wywrzeć:Vp~rę~zę':'Dawne wygotować się, z odmianą wywre/wywrzał. Użycie wywrzeć wpływ dotyczy innego leksemu i odmiany.',
              'dokument':'Kandydat dokumenta ma odrębne oznaczenie dawnej formy. Dowód współczesnego dokument nie znosi dawnej końcówki.',
              'klasztor':'Kandydat klasztora ma odrębne oznaczenie dawnej formy. Dowód współczesnego klasztor nie znosi dawnej końcówki.',
              'zasłonić':'Kandydaci dotyczą wariantów zasłoniony/zasłonienie. Współczesne zasłonięty/zasłonięcie nie uzasadniają tego wariantu odmiany.',
              'łupież:Sf':'Badany żeński leksem oznacza rabunek lub łup, a nie współczesną męską nazwę choroby skóry.',
              'cześć:S':'Kontrola cześci wykazała literówki części i dawny tytuł. Nie uzasadnia całej tej odmiany.',
            }
            reason=specific.get(lid,reason)
        matrices.append({'lemma_id':lid,'lemma_base':r['lemma_base'],'status':status,'reason':reason,
          'source_search':searches[r['lemma_base']]['url'],'source_article_ids':[a['id'] for a in searches[r['lemma_base']]['articles']],
          'round2_review_words':sorted(set(old_by_lid[lid])),'round3_review_words':sorted(set(current_by_lid[lid])),
          'forms':[{'word':w,'decision':'proposed_for_this_analysis' if w in own else 'accepted_via_other_reviewed_analysis' if w in new else 'not_proposed',
                    'tags':next(x['tags'] for x in r['forms'] if x['word']==w)} for w in sorted(words)]})
    save('candidate-matrix.json',{'groups':404,'unique_words':3364,'status_counts':dict(collections.Counter(r['status'] for r in matrices)),'cases':matrices})
    save('proposal-proof.json',{'words':len(new),'cases':[{'word':w,'analyses':proof[w]} for w in sorted(new)]})
    summary={'research_only':True,'implementation_approved':False,'method':'Potwierdzone znaczenie + zakres czytnika, przecięcie z przypiętymi analizami odrzucanymi wyłącznie za dawność. Istniejące konstrukcje wymagają potwierdzonych składników; bez własnego generowania napisów.',
      'new_words':sorted(new),'removed_words':[],
      'counts':{'new':len(new),'from_previous_3364':len(new&original),'outside_previous_3364':len(new-original),
                'previous_3364_not_proposed':len(original-new),'families_with_additions':len({v['lemma_id'] for w in proof for v in proof[w]}),
                'family_records':len(families),'source_tables':len(tables)},
      'family_results':[{'lemma_id':lid,'status':r['status'],'new_words':sorted(w for w in new if any(v['lemma_id']==lid for v in proof[w])),
                        'not_proposed_words':sorted(unmatched[lid]-new),'reader_articles_traversed':traversal.get(lid,[])} for lid,r in sorted(families.items())],
      'input_sha256':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [TMP/'candidates.json',OUT/'family-decisions.json',OUT/'full-tables-manifest.json']}}
    save('proposal.json',summary)
    print(json.dumps(summary['counts'],ensure_ascii=False));print('matrix',collections.Counter(r['status'] for r in matrices))
    for r in summary['family_results']:
        if r['status']!='hold':print(r['lemma_id'],len(r['new_words']),'unmatched',len(r['not_proposed_words']),r['not_proposed_words'][:12])

if __name__=='__main__': main()
