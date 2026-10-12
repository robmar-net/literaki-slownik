"""Publiczne KWJP: konteksty całej próby; cache tekstów poza repozytorium."""
import ast
import concurrent.futures
import hashlib
import html
import json
import re
import subprocess
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

ROOT=Path(__file__).resolve().parents[5]
TASK=Path(__file__).resolve().parents[1]
OUT=TASK/'analysis/findings/round5'
TMP=ROOT/'tmp/research-issue4/round5/contexts'
TMP.mkdir(parents=True,exist_ok=True)
tree=ast.parse((TASK/'analysis/kwjp_live_probe.py').read_text())
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ('plain','parse')],type_ignores=[]),'<existing KWJP parser>','exec'))


def fetch(case):
    lemma=case['lemma']
    query='[lemma="'+re.escape(lemma)+'"]'
    url='https://kwjp.pl/query_corpus/21/?'+urllib.parse.urlencode({'query':query,'per_page':'10','chosen_corpora':'balanced'})
    path=TMP/(case['id']+'.html')
    result={'id':case['id'],'lemma':lemma,'url':url,'query':query}
    try:
        if not path.exists():
            with urllib.request.urlopen(url,timeout=45) as response:body=response.read()
            total,rows=parse(body.decode())
            if total is None:raise ValueError('Nierozpoznany format KWJP')
            path.write_bytes(body)
            time.sleep(.2)
        body=path.read_bytes();total,rows=parse(body.decode())
        if total is None:raise ValueError('Nierozpoznany zapisany format KWJP')
        result.update(total=total,rows=rows,response_sha256=hashlib.sha256(body).hexdigest(),status='read')
    except Exception as e:
        result.update(status='error',error=str(e))
    return result


def main():
    cases=json.loads((OUT/'sample-blind.json').read_text())['cases']
    if sys.argv[1:]==['probe']:cases=cases[:1]
    results=[]
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
        for r in pool.map(fetch,cases):
            results.append(r)
            if len(results)%25==0:print('KWJP',len(results),'/',len(cases),flush=True)
    raw=TMP.parent/('context-probe.json' if len(cases)==1 else 'contexts-raw.json')
    raw.write_text(json.dumps(results,ensure_ascii=False,indent=2)+'\n')
    if len(cases)>1:
        public=[]
        for r in results:
            public.append({**{k:v for k,v in r.items() if k!='rows'},'rows':[
                {k:v for k,v in row.items() if k not in ('left','right')} for row in r.get('rows',[])]})
        (OUT/'context-manifest.json').write_text(json.dumps({'accessed_at':subprocess.check_output(['date','-u','+%Y-%m-%dT%H:%M:%SZ'],text=True).strip(),
            'method':'Exact lemma query, first page 10; targeted contexts, not random; live corpus differs from frozen lists. Raw texts local only.',
            'cases':public},ensure_ascii=False,indent=2)+'\n')
        for label in ('a','b'):
            ids={r['id'] for r in json.loads((OUT/f'sample-blind-{label}.json').read_text())['cases']}
            (TMP.parent/f'contexts-{label}-raw.json').write_text(json.dumps([r for r in results if r['id'] in ids],ensure_ascii=False,indent=2)+'\n')
    print({'queries':len(cases),'read':sum(r['status']=='read' for r in results),'contexts':sum(len(r.get('rows',[])) for r in results),
           'errors':[{k:v for k,v in r.items() if k!='rows'} for r in results if r['status']=='error']},flush=True)
    if any(r['status']=='error' for r in results):sys.exit(1)


if __name__=='__main__':main()
