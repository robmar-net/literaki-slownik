"""R1: dopasowanie lematów -anin do nazw geograficznych SGJP (pomoc do ręcznego przeglądu, tylko odczyt).

Użycie: python3 scripts/probe_resident_toponyms.py  (z katalogu repo; wynik tmp/r1/match.json).
Dopasowanie nie dowodzi klasy; słabe dopasowanie wskazuje kandydatów do przeglądu.
"""
import sqlite3, sys, json, unicodedata, bisect
db=sqlite3.connect('file:data/work/import-20261004-1302/build.sqlite?mode=ro',uri=True)
TR=str.maketrans({'ó':'o','ę':'e','ą':'a','ł':'l','ś':'s','ć':'c','ń':'n','ź':'z','ż':'z'})
def norm(w): return w.lower().translate(TR)
anin=sorted({r[0] for r in db.execute("select distinct lemma_base from lexeme where lemma_base like '%anin'") if r[0].islower()})
topo=sorted({norm(r[0].split(':')[0]) for r in db.execute("select distinct lemma from sgjp_record where names like '%nazwa_geograficzna%'")})
def best(stem):
    # najdłuższy wspólny prefiks z dowolnym toponimem (bisect po posortowanej liście)
    b=0; best_t=None
    for k in range(len(stem),2,-1):
        p=stem[:k]; i=bisect.bisect_left(topo,p)
        if i<len(topo) and topo[i].startswith(p): return k, topo[i]
    return 0, None
out=[]
for l in anin:
    stem=norm(l[:-4]).rstrip('i')
    k,t=best(stem)
    out.append({'lemma':l,'stem':stem,'prefix':k,'toponym':t,'ratio':round(k/max(len(stem),1),2)})
json.dump(out,open('tmp/r1/match.json','w'),ensure_ascii=False,indent=0)
import collections
weak=[o for o in out if o['prefix']<max(4,len(o['stem'])-2)]
print(len(out), 'słabe dopasowanie:', len(weak))
