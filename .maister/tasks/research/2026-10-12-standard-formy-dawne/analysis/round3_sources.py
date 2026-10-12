"""Czytnik SGJP do researchu; surowe odpowiedzi wyłącznie w ignorowanym cache."""
import concurrent.futures
import hashlib
import json
import re
import sqlite3
import sys
import time
import urllib.parse
import urllib.request
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]
TASK = Path(__file__).resolve().parents[1]
TMP = ROOT / 'tmp/research-issue4'
OUT = TASK / 'analysis/findings/round3'

class Node:
    def __init__(self, tag='', attrs=(), parent=None):
        self.tag, self.attrs, self.parent, self.children = tag, dict(attrs), parent, []
    def text(self):
        return re.sub(r'\s+', ' ', ''.join(c if isinstance(c, str) else c.text() for c in self.children)).strip()
    def find(self, cls):
        found = [self] if cls in self.attrs.get('class', '').split() else []
        for c in self.children:
            if isinstance(c, Node): found.extend(c.find(cls))
        return found

class Tree(HTMLParser):
    def __init__(self, source):
        super().__init__(convert_charrefs=True)
        self.root = self.current = Node()
        self.feed(source)
    def handle_starttag(self, tag, attrs):
        child = Node(tag, attrs, self.current); self.current.children.append(child)
        if tag not in ('br', 'img', 'meta', 'input', 'hr', 'link', 'wbr'): self.current = child
    def handle_endtag(self, tag):
        p = self.current
        while p.parent and p.tag != tag: p = p.parent
        if p.parent: self.current = p.parent
    def handle_data(self, data): self.current.children.append(data)

def extract(source):
    root = Tree(source).root
    forms = []
    for form in root.find('form'):
        p = form
        while p.parent and p.tag != 'li': p = p.parent
        row = p
        while row.parent and row.tag != 'tr': row = row.parent
        forms.append({'word': form.text(), 'qualifiers': [n.text() for n in p.find('qualifiers') if n.text()],
                      'row': [n.text() for n in row.find('header-label')]})
    links=[]
    for link in root.find('cr-link'):
        row=link
        while row.parent and row.tag!='tr': row=row.parent
        links.append({'id':int(link.attrs['id'].removeprefix('cr')),'word':link.text(),
                      'relation':' '.join(n.text() for n in row.find('cr-type'))})
    return {'headers': [n.text() for n in root.find('article-header')], 'forms': forms,'links':links,
            'notes': [n.text() for cls in ('lexeme-notes','notes','lexeme-note','comment') for n in root.find(cls)],
            'text': root.text()}

def get(url, path):
    if path.exists(): return json.loads(path.read_text())
    req = urllib.request.Request(url, headers={'User-Agent':'Literaki-research/1.0 (read-only)'})
    with urllib.request.urlopen(req, timeout=35) as response: data = response.read()
    obj = json.loads(data)
    path.write_bytes(data)
    time.sleep(.12)
    return obj

def search_url(word):
    params = {'sort_rules':['a_fronte'],'filter':{},'visible_vocabs':['SGJP','miejscowości','nazwiska'],'reader':True}
    return 'https://sgjp.pl/edycja/ajax/search-by-form/?'+urllib.parse.urlencode({'exponent':word,'query_params':json.dumps(params,ensure_ascii=False,separators=(',',':')),'columns':json.dumps(['entry','abbr_pos','genders'],separators=(',',':'))})

def fetch(word):
    path=TMP/f'sgjp-{word}-search.json';url=search_url(word)
    obj=get(url,path);articles=[];details=[]
    for row in obj['rows']:
        if row.get('hidden'): continue
        aid=row['id'];aurl=f'https://sgjp.pl/edycja/ajax/inflection-tables/?lexeme_id={aid}&variant=0'
        apath=TMP/f'sgjp-{aid}-tables.json';a=get(aurl,apath)
        articles.append({'id':aid,'entry':row['entry'],'pos':row['abbr_pos'],'genders':row['genders'],
                         'url':aurl,'sha256':hashlib.sha256(apath.read_bytes()).hexdigest()})
        details.append({'id':aid,**extract(a['html'])})
    return {'word':word,'url':url,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'articles':articles},details

def main():
    db=sqlite3.connect(f'file:{ROOT}/data/work/lists-v30-20261010-165826-a/build.sqlite?mode=ro',uri=True)
    db.execute('pragma query_only=on')
    ws=json.loads((OUT.parent/'round2/current-override.json').read_text())['necessary_words']
    q='''select distinct a.game_key,coalesce(l.lemma_id,c.lemma_id),a.expanded_tag,
    coalesce(i.qualifiers,c.qualifiers),a.candidate_key is not null,d.assessment_key
    from analysis a indexed by analysis_game_key join variant_decision d on d.analysis_key=a.analysis_key
    left join interpretation i on i.id=a.interpretation_id left join lexeme l on l.id=i.lexeme_id
    left join derivation_candidate c on c.candidate_key=a.candidate_key
    where a.game_key=? and +d.variant='standard' and d.membership_status='accept' '''
    rows=[list(x) for w in ws for x in db.execute(q,(w,))]
    (OUT/'current-analyses.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n')
    census=json.loads((OUT.parent/'round2/census-1580.json').read_text())
    words={x['lemma_base'] for x in census if x['new_noarch']}
    words|={x[1].split(':')[0] for x in rows}
    data=json.loads((TMP/'candidate-details.json').read_text())
    review=json.loads((OUT.parent/'round2/live-review.json').read_text())
    words|={v[1] for x in review['cases'] for v in data.get(x['word'],[])}
    manifest=[];details={};errors=[]
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
        jobs={pool.submit(fetch,w):w for w in sorted(words)}
        for future in concurrent.futures.as_completed(jobs):
            word=jobs[future]
            try:
                m,d=future.result();manifest.append(m);details[word]=d
            except Exception as error:
                errors.append({'word':word,'error':str(error)})
                print('ERROR',word,str(error),flush=True)
            if (len(manifest)+len(errors))%50==0: print('SGJP',len(manifest),len(errors),'of',len(words),flush=True)
    manifest.sort(key=lambda x:x['word'])
    (OUT/'sgjp-manifest.json').write_text(json.dumps({'queries':len(words),'successful':len(manifest),'errors':errors,'cases':manifest},ensure_ascii=False,indent=2)+'\n')
    (TMP/'round3-sgjp-details.json').write_text(json.dumps(details,ensure_ascii=False)+'\n')
    print('Done',len(manifest),len(errors),flush=True)

def full():
    roots=json.loads((OUT/'family-decisions.json').read_text())
    relations={'odsłownik','imiesłów przymiotnikowy czynny','imiesłów przymiotnikowy bierny',
      'przymiotnik „zanegowany”','przysłówek „zanegowany”','przymiotnik stopnia wyższego',
      'przymiotnik stopnia najwyższego','przysłówek stopnia wyższego','przysłówek stopnia najwyższego',
      'przysłówek stopnia równego'}
    fetched={};manifest=[]
    todo={a for r in roots if r['status'] in ('propose','limited') for a in r['article_ids']}
    depth=0
    while todo:
        depth+=1;assert depth<=6,'Nieoczekiwany łańcuch derywacji'
        def one(aid):
            url=f'https://sgjp.pl/edycja/ajax/inflection-tables/?lexeme_id={aid}&variant=1'
            p=TMP/f'sgjp-{aid}-variant1.json';obj=get(url,p)
            return aid,extract(obj['html']),{'id':aid,'url':url,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
            for aid,details,meta in pool.map(one,sorted(todo)):
                fetched[aid]=details;manifest.append(meta)
        todo={link['id'] for aid in todo for link in fetched[aid]['links'] if link['relation'] in relations and link['id'] not in fetched}
        print('full tables',len(fetched),'next',len(todo),flush=True)
    save=lambda p,o:p.write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n')
    save(TMP/'round3-full-tables.json',fetched)
    save(OUT/'full-tables-manifest.json',{'relations':sorted(relations),'articles':sorted(manifest,key=lambda x:x['id'])})

if __name__=='__main__':
    full() if len(sys.argv)>1 and sys.argv[1]=='full' else main()
