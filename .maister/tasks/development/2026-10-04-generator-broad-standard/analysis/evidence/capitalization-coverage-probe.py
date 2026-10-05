#!/usr/bin/env python3
"""Odczyt przypiętej bazy: etn. i zamknięte przykłady normy, bez filtrów.
Uruchomienie z katalogu repo: python3 PATH DB > NEW_REPORT.json.
Własny raport badawczy; żadne dane nie są wejściem kwalifikacji.
"""
import hashlib
import json
from pathlib import Path
import sqlite3
import sys

path=Path(sys.argv[1]).resolve()
def digest():
    h=hashlib.sha256()
    with path.open('rb') as stream:
        for data in iter(lambda:stream.read(1024*1024),b''):h.update(data)
    return h.hexdigest()
before=digest();db=sqlite3.connect(path.as_uri()+'?mode=ro',uri=True)
sid='sgjp-20260823';source=json.loads(db.execute('select metadata from source_artifact where source_id=?',(sid,)).fetchone()[0])
assert source['sha256']=='3b2ee079143bc95186370fd528735779c4ba62f4ce14e30cf6622ceb566e9810'
labels=db.execute("select l.lemma_id,i.names,i.qualifiers,count(*) from interpretation i join lexeme l on l.id=i.lexeme_id where i.source_id=? and i.qualifiers like '%etn.%' group by l.lemma_id,i.names,i.qualifiers order by l.lemma_id,i.names,i.qualifiers",(sid,)).fetchall()
examples={}
for word in ('angol','jugol','kitajec','makaroniarz','szkop','żabojad','warszawianka','krakowianka','bawarka','krakus','sądeczanin','chochołowianin'):
    rows=db.execute('''select i.source_id,i.first_row,f.original,l.lemma_id,i.tag,i.names,i.qualifiers
        from interpretation i join lexeme l on l.id=i.lexeme_id join surface_form f on f.id=i.form_id
        where i.source_id=? and f.game_key=? order by i.first_row''',(sid,word)).fetchall()
    examples[word]=[dict(zip(('source_id','first_source_row','original','lemma_id','raw_tag','names','qualifiers'),row)) for row in rows]
assert db.total_changes==0;db.close();assert before==digest()
print(json.dumps({'schema_version':1,'scope':'etn_label_inventory_and_closed_documentary_lookup_not_complete_resident_class',
    'source_sha256':source['sha256'],'source_db_sha256':before,'readonly':True,'source_unchanged':True,
    'active_policy_inputs_added':0,'etn_lemma_count':len({r[0] for r in labels}),
    'etn_label_combination_count':len(labels),'etn_compact_interpretations':sum(r[3] for r in labels),
    'etn_inventory':[dict(lemma_id=r[0],names=r[1],qualifiers=r[2],compact_interpretations=r[3]) for r in labels],
    'examples':examples,'full_resident_inventory_complete':False},ensure_ascii=False,indent=2))
