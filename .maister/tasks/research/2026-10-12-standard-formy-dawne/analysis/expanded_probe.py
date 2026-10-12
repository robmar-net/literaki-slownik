"""Szerszy research #4: pełny spis i próby; żadnych wejść produkcyjnych."""
import csv,gzip,hashlib,json,re,sqlite3,subprocess,tarfile,sys
from decimal import Decimal
from collections import Counter,defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parents[5]
TASK=Path(__file__).resolve().parents[1]
TMP=ROOT/'tmp/research-issue4'
OUT=TASK/'analysis/findings/round2'
OUT.mkdir(exist_ok=True)
def save(path,x):path.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def digest(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(8<<20),b''):h.update(b)
 return h.hexdigest()
def arch(q):return any('arch.' in x.split(',') for x in q.split('|'))
def sample(seq,n,seed):return sorted(seq,key=lambda x:hashlib.sha256((seed+str(x)).encode()).hexdigest())[:n]
data=json.loads((TMP/'candidate-details.json').read_text())
raw=json.loads((TMP/'candidates.json').read_text())
standard=set((ROOT/'data/work/lists-v30-20261010-165826-a/lists/standard.txt').read_text().splitlines())
controls={x[0] for x in raw}&standard
allwords=set(data)|controls
forms=defaultdict(dict);lemmas=defaultdict(dict);hashes={}
for kind in ('orth','lemma'):
 for genre in ('all','fakt','publicystyka','fikcja'):
  path=ROOT/f'cache/kwjp/kwjp100-slowa-{kind}-{genre}.csv.gz';hashes[str(path.relative_to(ROOT))]=digest(path)
  with gzip.open(path,'rt') as f:
   r=csv.reader(f);header=next(r);off=2 if kind=='lemma' else 1
   for row in r:
    if kind=='orth' and row[0] not in allwords:continue
    d=dict(zip(header[off:],row[off:]));x=Decimal(d['freq']);assert x==int(x);d['freq']=int(x)
    if kind=='lemma':lemmas[(row[0],row[1])][genre]=d
    else:forms[row[0]][genre]=d
print('lists ready',flush=True)
def f(w,g):return forms.get(w,{}).get(g,{}).get('freq',0)
def nf(w):return f(w,'fakt')+f(w,'publicystyka')
def lf(b,p,g):return lemmas.get((b,p),{}).get(g,{}).get('freq',0)
def lnf(v):return lf(v[1],v[2],'fakt')+lf(v[1],v[2],'publicystyka')
def stratum(w):
 if not f(w,'all'):return 'A_no_published_form'
 if not nf(w):return 'B_fiction_only'
 if nf(w)<5:return 'C_nf_1_4'
 return 'D_nf_5_29'
qualified=defaultdict(set);good=defaultdict(set);meta=defaultdict(set);wordgood={}
for w,vals in data.items():
 matches=[v for v in vals if lnf(v)>=30]
 for v in matches:
  qualified[v[0]].add(w);meta[v[0]].add(tuple(v))
  if not arch(v[3]):good[v[0]].add(w)
 clean=[v for v in matches if not arch(v[3])]
 if clean:wordgood[w]=clean
assert len(qualified)==1580 and len(good)==404 and len(wordgood)==3364
full=set().union(*qualified.values());assert len(full)==4559
strata=defaultdict(list)
for w in sorted(wordgood):strata[stratum(w)].append(w)
selected=[w for k in sorted(strata) for w in sample(strata[k],50,'issue4-round2-form-v1:')]
features={w:{'word':w,'stratum':stratum(w),'orth':forms.get(w,{}),'eligible_analyses':wordgood[w],
 'all_historical_candidate_analyses':data[w]} for w in selected}
# Pełne paradygmaty oznaczonych kandydatów, bez tekstów korpusowych.
tagmap=defaultdict(set)
for w,lid,b,tag,q,d in raw:
 if lid in qualified and w in qualified[lid]:tagmap[(w,lid)].add(tag)
census=[]
for lid in sorted(qualified):
 ws=sorted(qualified[lid]);clean=sorted(good.get(lid,set()))
 vals=sorted(meta[lid]);census.append({'lemma_id':lid,'lemma_base':vals[0][1],
 'new_forms':ws,'new_noarch':clean,'labels':sorted({v[3] for v in vals}),
 'lemma_metrics':{v[2]:lemmas.get((v[1],v[2]),{}) for v in vals},
 'forms':[{'word':w,'nf':nf(w),'all':f(w,'all'),'tags':sorted(tagmap[(w,lid)])} for w in ws]})
save(OUT/'census-1580.json',census)
save(OUT/'sample-forms.json',{'seed':'issue4-round2-form-v1:','strata':{k:{'population':len(v),'sample':sum(w in v for w in selected)} for k,v in strata.items()},'cases':list(features.values())})
# Rozpoznawalne bez interpretacji semantycznej cechy całej populacji.
struct={'qualified_lemma_ids':len(qualified),'noarch_lemma_ids':len(good),'all_forms':len(full),'noarch_forms':len(wordgood),
 'only_arch_lemma_ids':sum(not good.get(x) for x in qualified),
 'labels_noarch':dict(Counter(v[3] for w,vals in wordgood.items() for v in vals)),
 'strata':{k:len(v) for k,v in strata.items()},
 'derived_only_forms':sum(all(v[4] for v in vals) for vals in wordgood.values()),
 'forms_with_multiple_eligible_lids':sum(len({v[0] for v in vals})>1 for vals in wordgood.values()),
 'source_hashes':hashes,'candidate_details_sha256':digest(TMP/'candidate-details.json')}
# Siatka progów: każda para działa wewnątrz tej samej uprawnionej analizy.
grid=[]
for lt in (10,20,30,50,100,300):
 eligible={w:[v for v in vals if lnf(v)>=lt and not arch(v[3])] for w,vals in data.items()}
 eligible={w:v for w,v in eligible.items() if v}
 for ft in (0,1,5,10,20):
  ws={w for w in eligible if nf(w)>=ft}
  grid.append({'lemma_nf':lt,'form_nf':ft,'new_forms':len(ws),'no_published_orth_all':sum(not f(w,'all') for w in ws),
   'forms_arch':sum(all(arch(v[3]) for v in data[w]) for w in ws)})
extra=[]
for threshold in (1,5,10,20,30):
 ws={w for w,vals in wordgood.items() if any(lf(v[1],v[2],'fakt')>=threshold and lf(v[1],v[2],'publicystyka')>=threshold for v in vals)}
 extra.append({'both_nf_genres_at_least':threshold,'new_forms':len(ws),'no_published_form':sum(not f(w,'all') for w in ws)})
for maxdp in (.5,.7,.8,.9,.95):
 ws={w for w,vals in wordgood.items() if any(any(d['freq']>=30 and float(d['DP_norm'])<=maxdp for g,d in lemmas.get((v[1],v[2]),{}).items() if g in ('fakt','publicystyka')) for v in vals)}
 extra.append({'one_nf_genre_f30_max_dp':maxdp,'new_forms':len(ws),'no_published_form':sum(not f(w,'all') for w in ws)})
save(OUT/'metrics.json',dict(struct,grid=grid,extra=extra))
# Kontrole są strukturą analityczną, nie gold standard.
low={w for w,vals in data.items() if w not in full and 0<nf(w)<30}
controlsets={'rejected_outside_lemma30_with_nf_evidence':sample(low,40,'issue4-outside-v1:')}
save(OUT/'controls.json',{k:[{'word':w,'nf':nf(w),'all':f(w,'all'),'standard':w in standard,'analyses':data.get(w,[])} for w in ws] for k,ws in controlsets.items()})
# Pełne skanowanie publicznych kontekstów dla wszystkich możliwych dodatków.
archive=ROOT/'tmp/kwjp-halfm-samples.tar.gz'
assert digest(archive)=='aedad77022508fe10d0d537e6a082884b8e7a97d4836a184ff744a5261db55b1'
hits=[];files=units=0;candidate_words=set(data)
with tarfile.open(archive) as tf:
 for member in tf:
  if not member.isfile():continue
  obj=json.load(tf.extractfile(member));files+=1
  for i,s in enumerate(obj['samples']):
   units+=1;tokens=re.findall(r'(?<![\w-])[^\W\d_]+(?![\w-])',s['text'])
   matches=sorted({t.lower() for t in tokens}&candidate_words)
   if matches:
    hits.append({'id':f"{obj['meta']['id']}:{i}",'file':member.name,'sample_index':i,
      'words':matches,'noarch_words':[w for w in matches if w in wordgood],
      'originals':sorted({t for t in tokens if t.lower() in matches}),
      'bibliography':obj['meta'],'text':s['text']})
save(TMP/'round2-all-contexts-raw.json',hits)
# Wszystkie konteksty 4559 dodatków; podzbiór 3364 oznaczamy osobno.
focus=[x for x in hits if x['noarch_words']]
qualified_hits=[x for x in hits if set(x['words'])&full]
chosen=qualified_hits if len(qualified_hits)<=250 else sample(qualified_hits,200,'issue4-round2-context-v1:')
save(OUT/'context-inventory.json',{'files':files,'units':units,'all_hits':len(hits),
 'all_hits_scope':'389160 history-only candidates; not just lemma30',
 'lemma30_hits':len(qualified_hits),'focus_hits':len(focus),'selected_hits':len(chosen),'unique_noarch_words_in_contexts':len({w for x in focus for w in x['noarch_words']}),
 'source_sha256':digest(archive),'records':[{k:v for k,v in x.items() if k!='text'} for x in chosen]})
(TMP/'round2-contexts-review.txt').write_text('\n\n'.join(f"{x['id']} | {','.join(x['noarch_words'])} | {x['bibliography']['meta_kwjp_type']} | {x['bibliography'].get('meta_published')}\n{x['text']}" for x in chosen))
(TMP/'round2-groups-404.txt').write_text('\n'.join(f"{x['lemma_id']}: {', '.join(x['new_noarch'])}" for x in census if x['new_noarch']))
print(json.dumps(dict(struct,context_files=files,context_units=units,all_context_hits=len(hits),focus_hits=len(focus),selected_hits=len(chosen),form_sample=len(selected)),ensure_ascii=False,indent=2),flush=True)
