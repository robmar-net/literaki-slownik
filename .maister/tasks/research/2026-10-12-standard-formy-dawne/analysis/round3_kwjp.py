"""Celowa kontrola wszystkich bieżących przyjęć i brakujących przykładów. Bez importu."""
import ast,concurrent.futures,hashlib,html,json,re,subprocess,time,urllib.parse,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[5];TASK=Path(__file__).resolve().parents[1]
TMP=ROOT/'tmp/research-issue4';OUT=TASK/'analysis/findings/round3'
# Te same jawne funkcje parsujące, bez uruchamiania efektów ubocznych skryptu rundy 2.
tree=ast.parse((TASK/'analysis/kwjp_live_probe.py').read_text())
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ('plain','parse')],type_ignores=[]),'<kwjp parser>','exec'))
words=set(json.loads((OUT.parent/'round2/current-override.json').read_text())['necessary_words'])
words.update('sołtyska sołtyską sztaluga sztalugę szuwar szuwarem przytulisko przytuliska przechwałka przechwałkę powijak ukradka szczętu szczętem podorędziu negocjator pryncypium pryncypiami gawiedzią jagnięcina'.split())
def fetch(w):
    url='https://kwjp.pl/query_corpus/21/?'+urllib.parse.urlencode({'query':'[orth="'+w+'"]','per_page':'10','chosen_corpora':'balanced'})
    p=TMP/'kwjp-live'/f'{w}.html'
    if not p.exists():
        with urllib.request.urlopen(url,timeout=40) as response:body=response.read()
        count,rows=parse(body.decode())
        if count is None:raise ValueError('Nierozpoznana odpowiedź: '+w)
        p.write_bytes(body);time.sleep(.15)
    body=p.read_bytes();count,rows=parse(body.decode());assert count is not None,w
    return {'word':w,'url':url,'total':count,'sha256':hashlib.sha256(body).hexdigest(),'rows':rows}
result=[]
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
    for x in pool.map(fetch,sorted(words)):
        result.append(x)
        if len(result)%50==0:print('KWJP',len(result),'of',len(words),flush=True)
(TMP/'round3-kwjp-raw.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
public=[{**{k:v for k,v in x.items() if k!='rows'},'rows':[{k:v for k,v in row.items() if k not in ('left','right')} for row in x['rows']]} for x in result]
(OUT/'kwjp-manifest.json').write_text(json.dumps({'queries':len(result),'accessed_at':subprocess.check_output(['date','-u','+%Y-%m-%dT%H:%M:%SZ'],text=True).strip(),'cases':public},ensure_ascii=False,indent=2)+'\n')
print('Done',len(result),flush=True)
