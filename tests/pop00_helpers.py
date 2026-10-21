"""Małe, własne dane POP00: pełne piny, konstrukcje i pułapki częstości."""
import gzip
from contextlib import closing
import json
import os
from pathlib import Path
import sqlite3
from literaki_slownik.canonical import sha256, write_json
from literaki_slownik.pop import _write_gzip

ROOT = Path(__file__).resolve().parents[1]


def fixture(root):
    root = Path(root)
    run, pop, inputs = root/'run', root/'pop', root/'inputs'
    for p in (run/'lists', pop/'reports', inputs):
        p.mkdir(parents=True)
    rows = [('kot','kot','subst:sg:nom:m1'), ('kotach','kot','subst:pl:loc:m1'),
        ('zrobiłem','robić','praet:sg:m1:pri:perf'),
        ('remontowałoś','robić','praet:sg:n:sec:imperf'),
        ('czytanymi','robić','ppas:pl:inst:m1:imperf:aff'),
        ('nieczytanie','robić','ger:sg:nom:n:imperf:neg'),
        ('nieczytaniami','robić','ger:pl:inst:n:imperf:neg'),
        ('miły','miły','adj:sg:nom:m1:pos'), ('najmilszy','miły','adj:sg:nom:m1:sup'),
        ('najmilszemu','miły','adj:sg:dat:m1:sup'), ('by','by','comp'),
        ('my','by','ppron12:pl:nom:m1.f.n:pri')]
    construction = [('czytajże','robić','impt:sg:sec:imperf','impt-single-particle-v1'),
                    ('bym','by','aglt:sg:pri:imperf:nwok','by-aglt-nwok-v1')]
    members = {lemma+'@own' for _,lemma,_ in rows}
    words = {w for w,_,_ in rows} | {w for w,_,_,_ in construction}
    database = run/'build.sqlite'
    with closing(sqlite3.connect(database)) as db:
        db.executescript((ROOT/'literaki_slownik/schema.sql').read_text())
        db.execute("insert into source_artifact values ('own','sgjp_tab','{}')")
        lexemes = {m.split('@')[0]:i for i,m in enumerate(sorted(members),1)}
        for lemma,i in lexemes.items():
            db.execute('insert into lexeme values (?,?,?,?)',(i,'own',lemma,lemma))
        for i,(word,lemma,tag) in enumerate(rows,1):
            db.execute('insert into surface_form values (?,?,?,?,?)',(i,word,word,word,len(word)))
            db.execute('insert into sgjp_record values (?,?,?,?,?,?,?)',('own',i,word,lemma,tag,'',''))
            db.execute('insert into interpretation values (?,?,?,?,?,?,?,?)',
                       (i,'own',i,i,lexemes[lemma],tag,'',''))
        for word,lemma,tag,rule in construction:
            key='own-'+word
            db.execute('insert into derivation_candidate values (?,?,?,?,?,?,?,?,?)',
                       (key,rule,word,word,lemma,tag,'','','{}'))
            db.execute('insert into derivation_component values (?,?,?,?,?)',(key,0,'source_interpretation','own',1))
        db.commit()
    standard = run/'lists/standard.txt'
    standard.write_text(''.join(w+'\n' for w in sorted(words)))
    _write_gzip(pop/'POP0.txt.gz',sorted(words))
    write_json(pop/'reports/units.json',{'units':[{'members_in':{'POP0':sorted(members)}}]})
    (pop/'ATTRIBUTIONS.md').write_text('# Własna fikstura\n')
    orth = inputs/'orth.csv.gz'
    with gzip.open(orth,'wt') as f:
        f.write(',freq,ipm\nkot,100,10\nczytanymi,9,0.09\nnajmilszy,36,0.36\nnieczytanie,15,0.15\n')
    db_sha=sha256(database)
    base=pop/'release-manifest.json'
    write_json(base,{'kind':'literaki-pop-manifest','method':'pop-v3','package_id':'POP','status':'BUILT',
        'inputs':{'database_sha256':db_sha,'standard_sha256':sha256(standard),'release_manifest_sha256':'a'*64},
        'files':{name:{'sha256':sha256(pop/name)} for name in ['POP0.txt.gz','reports/units.json','ATTRIBUTIONS.md']}})
    write_json(run/'manifest.json',{'readiness':'FROZEN','verification':{'database_sha256':db_sha},
        'export':{'release_manifest_sha256':'a'*64},'inputs':{'artifacts':[{'kind':'kwjp_orth','genre':'all','sha256':sha256(orth)}]}})
    refs={'base_pop':base,'base_run':run/'manifest.json','database':database,'standard':standard,'orth':orth}
    manifest=root/'sources.json'
    write_json(manifest,{'schema_version':1,'version':'pop00-sources-v1','inputs':{
        k:{'path':os.path.relpath(p,root),'sha256':sha256(p)} for k,p in refs.items()}})
    config=root/'config.json'
    config.write_bytes((ROOT/'config/generator/pop00.json').read_bytes())
    return {'root':root,'run':run,'pop':pop,'database':database,'manifest':manifest,'config':config,
            'words':words,'members':members,'refs':refs}


def rewrite(path,value):
    path=Path(path)
    if path.exists():
        path.chmod(0o644)
    write_json(path,value)


def cleanup(root):
    for p in Path(root).rglob('*'):
        if p.is_file():
            p.chmod(0o644)
