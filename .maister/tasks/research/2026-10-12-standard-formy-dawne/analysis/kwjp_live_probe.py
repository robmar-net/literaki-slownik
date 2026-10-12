"""Odczyt publicznej wyszukiwarki KWJP: 10 pierwszych konkordancji, bez importu."""
import concurrent.futures,hashlib,html,json,re,subprocess,sys,time,urllib.parse
from pathlib import Path
ROOT=Path(__file__).resolve().parents[5];TASK=Path(__file__).resolve().parents[1]
TMP=ROOT/'tmp/research-issue4/kwjp-live';TMP.mkdir(exist_ok=True)
OUT=TASK/'analysis/findings/round2'
def plain(s):
 s=re.sub(r'<!--.*?-->','',s,flags=re.S);s=re.sub(r'<u>.*?</u>','',s,flags=re.S)
 return re.sub(r'\s+',' ',html.unescape(re.sub('<[^>]+>','',s))).strip()
def parse(s):
 m=re.search(r'<span><b>([\d ,]+)</b> results found',s)
 if not m:
  if 'No results found' in s or 'Nothing found' in s or '<strong>No results.' in s:return 0,[]
  return None,[]
 total=int(re.sub(r'\D','',m[1]));rows=[]
 for r in re.findall(r'<tr class="orth".*?</tr>',s,re.S):
  cells=re.findall(r'<td[^>]*>(.*?)</td>',r,re.S)
  if len(cells)<6:continue
  match=re.search('title="([^"]*)"',cells[4]);meta=plain(html.unescape(match[1])) if match else ''
  did=re.search('data-text-id="([^"]+)"',r);sent=re.search('data-sentence="([^"]+)"',r)
  rows.append({'left':plain(cells[1]),'word':plain(cells[2]),'right':plain(cells[3]),'date':plain(cells[4]),
   'metadata':meta,'document_id':did[1] if did else None,'sentence':sent[1] if sent else None,
   'annotation':html.unescape(re.search('title="([^"]*)"',cells[2])[1])})
 return total,rows
sample=json.loads((OUT/'sample-forms.json').read_text())['cases']
words={x['word'] for x in sample}
words.update('desperacja niezbędnik familia odzienie surdut aliści jakoż iże nazad trzykroć desperacyj metrowie kursorzy kalkulatorzy powijak umorach rozpukowi dżdżu industrialny generyczny wolontariacki dinozaur wywre sztorcem podorędziem'.split())
controls=json.loads((OUT/'current-override.json').read_text())
words.update(controls['sample'])
words.update(x['word'] for x in json.loads((OUT/'controls.json').read_text())['rejected_outside_lemma30_with_nf_evidence'])
def fetch(w):
 url='https://kwjp.pl/query_corpus/21/?'+urllib.parse.urlencode({'query':'[orth="'+w+'"]','per_page':'10','chosen_corpora':'balanced'})
 path=TMP/(w+'.html')
 if not path.exists():
  r=subprocess.run(['curl','-fL','--max-time','45','--retry','1',url,'-o',str(path)],capture_output=True,text=True)
  if r.returncode:return {'word':w,'url':url,'error':r.stderr[-300:]}
  time.sleep(.25)
 s=path.read_text();count,rows=parse(s)
 return {'word':w,'url':url,'total':count,'rows':rows,'response_sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
results=[]
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as ex:
 for r in ex.map(fetch,sorted(words)):
  results.append(r)
  if len(results)%20==0:print('fetched',len(results),'/',len(words),flush=True)
(Path(ROOT/'tmp/research-issue4/kwjp-live-raw.json')).write_text(json.dumps(results,ensure_ascii=False,indent=2)+'\n')
public=[]
for x in results:
 y={k:v for k,v in x.items() if k!='rows'};y['rows']=[{k:v for k,v in r.items() if k not in ('left','right')} for r in x.get('rows',[])];public.append(y)
(OUT/'kwjp-live-inventory.json').write_text(json.dumps({'accessed':subprocess.check_output(['date','-u','+%Y-%m-%dT%H:%M:%SZ'],text=True).strip(),
 'method':'exact lower orth; first 10 web results; not random contexts, not pinned snapshot; raw texts local only','cases':public},ensure_ascii=False,indent=2)+'\n')
print('done',len(results),'unknown',sum(x.get('total') is None for x in results),flush=True)
