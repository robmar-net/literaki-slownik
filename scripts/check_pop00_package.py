#!/usr/bin/env python3
"""Niezależny odbiór POP00: pliki, źródłowe analizy, reguły oraz przegląd.

Bez importu literaki_slownik. Wymaga jawnego manifestu i konfiguracji wejść.
Nie ufa powodom w pakiecie ani samym sumom, odtwarza je z zamrożonej bazy.
"""
import argparse
from collections import Counter, defaultdict
from contextlib import closing
from decimal import Decimal
import csv
import gzip
import hashlib
from itertools import product
import json
from pathlib import Path
import sqlite3
import stat
import sys
import unicodedata


class Refused(Exception):
    def __init__(self, message, code=4):
        super().__init__(message)
        self.code = code


def require(condition, message, code=4):
    if not condition:
        raise Refused(message, code)


def digest(path):
    with open(path, 'rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def encoded(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()


def read(path):
    def unique(pairs):
        out = {}
        for k, v in pairs:
            require(k not in out, 'Powtórzony klucz JSON')
            out[k] = v
        return out
    return json.loads(Path(path).read_text(encoding='utf-8'), object_pairs_hook=unique,
                      parse_constant=lambda v: (_ for _ in ()).throw(Refused('Nieskończona liczba JSON')))


def words(path):
    path = Path(path)
    if path.suffix == '.gz':
        data = gzip.decompress(path.read_bytes())
    else:
        data = path.read_bytes()
    text = data.decode('utf-8')
    rows = text.splitlines()
    require(bool(rows) and text.endswith('\n') and '\r' not in text and rows == sorted(set(rows)),
            'Niekanoniczna lista słów')
    require(all(w == w.lower() == unicodedata.normalize('NFC', w) and w.isalpha() and
                2 <= len(w) <= 15 for w in rows), 'Zły zapis słowa')
    return set(rows)


def files(root, manifest):
    required = {'POP00.txt.gz', 'method.json', 'reports/decisions.json', 'reports/summary.json',
        'reports/sample.json', 'reports/review-template.json', 'ATTRIBUTIONS.md', 'TERMS.md',
        'LIMITATIONS.md', 'release-manifest.json', 'SHA256SUMS'}
    actual = set()
    for p in root.rglob('*'):
        require(not p.is_symlink() and (p.is_file() or p.is_dir()), 'Niedozwolony wpis pakietu')
        if p.is_file():
            actual.add(p.relative_to(root).as_posix())
            require(stat.S_IMODE(p.stat().st_mode) == 0o444, 'Pakiet nie jest tylko do odczytu')
    require(actual == required, 'Zestaw plików pakietu POP00 różny od kontraktu')
    meta = manifest['files']
    require(set(meta) == required - {'SHA256SUMS', 'release-manifest.json'}, 'Niepełny zakres manifestu')
    for name in meta:
        require(meta[name] == {'sha256': digest(root/name), 'bytes': (root/name).stat().st_size},
                'Niezgodny manifest pliku ' + name)
    expected = ''.join(f'{digest(root/name)}  {name}\n' for name in sorted(required - {'SHA256SUMS'}))
    require((root/'SHA256SUMS').read_text() == expected, 'Niezgodne SHA256SUMS')
    head = (root/'POP00.txt.gz').read_bytes()[:10]
    require(len(head) == 10 and head[:2] == b'\x1f\x8b' and head[3] == 0 and head[4:8] == b'\0'*4,
            'Gzip z nazwą, czasem lub dodatkowymi flagami')


def groups(tag, rule):
    known_rules = {'by-aglt-nwok-v1', 'documented-spelling-variant-v1', 'impt-double-particle-v1',
        'impt-single-particle-v1', 'mobile-by-host-aglt-v1', 'mobile-host-by-sequence-v1',
        'mobile-source-host-aglt-v1', 'nie-prefix-degree-v2', 'personal-host-aglt-v1',
        'pred-particle-ze-v1', 'preposition-n-source-v1'}
    require(rule is None or rule in known_rules, 'Nieznana reguła konstrukcji')
    known_pos = set('adj adja adjc adjp adv aglt bedzie brev comp cond conj depr fin frag ger imps '
        'impt inf interj num numcomp pact pacta pant part pcon ppas ppron12 ppron3 praet pred '
        'prep siebie subst winien'.split())
    found = set()
    fields = [f.split('.') for f in tag.split(':')]
    require(all(all(x for x in f) for f in fields), 'Puste pole tagu')
    for atoms in product(*fields):
        pos, *features = atoms
        require(pos in known_pos, 'Nieznany POS')
        if 'n' in features and any(p in features for p in ('pri','sec')):
            found.add('neuter-person-1-2')
        elif rule == 'by-aglt-nwok-v1':
            require(pos == 'aglt', 'By+aglt bez aglt')
            found.add('ordinary')
        elif rule and rule != 'nie-prefix-degree-v2':
            found.add('construction')
        elif pos in {'pact', 'ppas', 'pant', 'pacta', 'adja', 'adjp'}:
            found.add(pos)
        elif pos == 'ger' and 'neg' in features:
            found.add('negative-gerund')
        elif pos in {'adj','adv'} and any(d in features for d in ('com','sup')):
            found.add('degree-com-sup')
        else:
            found.add('ordinary')
    return sorted(found)


def source_rows(database, selected, base):
    with closing(sqlite3.connect(database.as_uri()+'?mode=ro', uri=True)) as db:
        identifiers = {i: lemma+'@'+sid for i,sid,lemma in db.execute('select id,source_id,lemma_id from lexeme')
                       if lemma+'@'+sid in selected}
        require(set(identifiers.values()) == selected, 'Brak leksemów w bazie')
        ordered = sorted(identifiers)
        for start in range(0,len(ordered),400):
            chunk = ordered[start:start+400]
            q = ('select i.lexeme_id,s.game_key,s.original,i.tag,i.names,i.qualifiers,i.first_row '
                 'from interpretation i join surface_form s on s.id=i.form_id where i.lexeme_id in ('+
                 ','.join('?'*len(chunk))+')')
            for i,word,original,tag,names,qualifiers,row in db.execute(q,chunk):
                if word in base:
                    member = identifiers[i]
                    key = hashlib.sha256(encoded([member,row,original,tag,names,qualifiers])).hexdigest()
                    yield word, 'source:'+key, member, tag, None
        for word,lemma,tag,sid,rule,key in db.execute(
            "select c.game_key,c.lemma_id,c.expanded_tag,p.source_id,c.rule_id,c.candidate_key "
            "from derivation_candidate c join derivation_component p on p.candidate_key=c.candidate_key "
            "where p.kind='source_interpretation'"):
            if word in base and lemma+'@'+sid in selected:
                yield word, 'construction:'+key, lemma+'@'+sid, tag, rule


def semantics(paths, root, manifest, config):
    pop_manifest = read(paths['base_pop'])
    pop_root = paths['base_pop'].parent
    for name in ('POP0.txt.gz','reports/units.json','ATTRIBUTIONS.md'):
        require(digest(pop_root/name) == pop_manifest['files'][name]['sha256'], 'Zmieniony plik POP0',3)
    base, standard, actual_words = words(pop_root/'POP0.txt.gz'), words(paths['standard']), words(root/'POP00.txt.gz')
    require(actual_words <= base <= standard, 'Naruszona relacja POP00 ⊆ POP0 ⊆ STANDARD')
    selected = {m for r in read(pop_root/'reports/units.json')['units'] for m in r['members_in'].get('POP0',[])}
    orth = {}
    with gzip.open(paths['orth'],'rt',encoding='utf-8',newline='') as f:
        for r in csv.DictReader(f):
            word = r[''];ipm = Decimal(r['ipm']);freq = Decimal(r['freq'])
            require(word not in orth and ipm.is_finite() and ipm >= 0 and freq.is_finite()
                    and freq >= 0 and freq == int(freq), 'Uszkodzony KWJP')
            orth[word] = (str(ipm),int(freq))
    rows = read(root/'reports/decisions.json')
    require(set(rows) == base, 'Niepełny raport decyzji')
    actual = {}
    for word,row in rows.items():
        require(set(row) == {'kept','evidence','analyses'} and type(row['kept']) is bool, 'Zły kształt decyzji')
        items = {(a['member'],a['id']):a for a in row['analyses']}
        require(len(items) == len(row['analyses']) and bool(items), 'Duplikaty lub puste analizy')
        actual[word] = items
    seen, kept_by_owner, accepted = defaultdict(set), set(), set()
    for word,key,member,tag,rule in source_rows(paths['database'],selected,base):
        categories = groups(tag,rule)
        observed = word in orth and Decimal(orth[word][0]) >= Decimal('0.1')
        survives = 'ordinary' in categories or (observed and categories != ['neuter-person-1-2'])
        expected = {'id':key,'member':member,'tag':tag,'rule':rule,'groups':categories,'kept':survives}
        require(actual[word].get((member,key)) == expected, 'Fałszywa analiza lub powód: '+word)
        seen[word].add((member,key))
        if survives:
            kept_by_owner.add(member);accepted.add(word)
    require(kept_by_owner == selected, 'Utracony leksem POP0')
    require(accepted == actual_words, 'Lista różni się od źródłowego wyniku polityki')
    groups_count = Counter()
    for word,row in rows.items():
        require(set(actual[word]) == seen[word], 'Brak lub nadmiar analiz: '+word)
        expected_evidence = {'status':'OBSERVED' if word in orth else 'NO_PUBLISHED_EVIDENCE',
                             'ipm':orth[word][0] if word in orth else None}
        require(row['evidence'] == expected_evidence and row['kept'] == (word in accepted),
                'Fałszywy dowód lub wynik: '+word)
        groups_count.update({g for a in row['analyses'] for g in a['groups']})
    counts = {'forms':len(accepted),'base_forms':len(base),'removed_forms':len(base-accepted),
              'selected_lexemes':len(selected),'lost_lexemes':0}
    require(manifest['counts'] == counts, 'Niezgodne liczniki manifestu')
    report = read(root/'reports/summary.json')
    require(all(report[k] == v for k,v in counts.items()), 'Niezgodne liczniki podsumowania')
    require(report['lengths'] == {str(k):v for k,v in sorted(Counter(map(len,accepted)).items())}
            and report['groups_overlapping'] == dict(groups_count), 'Niezgodne grupy lub długości')
    denominator = sum(orth.get(w,('0',0))[1] for w in base)
    retained = sum(orth.get(w,('0',0))[1] for w in accepted)
    total = sum(f for w,(_,f) in orth.items() if w == w.lower())
    coverage=report['coverage']
    require((coverage['observed_pop0_tokens'],coverage['retained_tokens'],coverage['published_lowercase_tokens'])
            == (denominator,retained,total), 'Niezgodna masa pokrycia')
    require(coverage['observed_pop0_pct'] == (100*retained/denominator if denominator else None)
            and coverage['published_lowercase_pct'] == (100*retained/total if total else None),
            'Niezgodny procent pokrycia')
    return rows


def check_sample(root, rows, config, review_path=None):
    diagnostic=set(('kot kotach kotem czytam czytasz czytaj czytajcie czytając czytany czytanymi '
        'czytanie zrobiłem zrobiłam byłem byłam zrobiliśmy zrobiłbym remontowałoś przeczytałobym '
        'zrobiwszy najmilszy najmilszemu miłemu mili miłymi lepszy lepszemu nieczytanie '
        'nieczytaniami czytajże bym byś byśmy byście').split())
    populations=defaultdict(set)
    names=('ordinary neuter-person-1-2 construction pact ppas pant pacta adja adjp negative-gerund '
           'degree-com-sup no-published-evidence threshold short long alternative-analyses').split()
    for n in names:
        for suffix in ('kept','removed'):populations[n+'-'+suffix]=set()
    for word,r in rows.items():
        if word in diagnostic:continue
        suffix='kept' if r['kept'] else 'removed'
        for g in {g for a in r['analyses'] for g in a['groups']}:populations[g+'-'+suffix].add(word)
        ipm=r['evidence']['ipm']
        if ipm is None:populations['no-published-evidence-'+suffix].add(word)
        elif Decimal('0.08') <= Decimal(ipm) <= Decimal('0.12'):populations['threshold-'+suffix].add(word)
        if len(word)<=3:populations['short-'+suffix].add(word)
        if len(word)>=12:populations['long-'+suffix].add(word)
        if len(r['analyses'])>1:populations['alternative-analyses-'+suffix].add(word)
    sample=read(root/'reports/sample.json')
    require(sample['status']=='UNREVIEWED' and sample['schema_version']==1
            and all(sample[k]==v for k,v in config['sampling'].items()), 'Zły stan lub metoda próbki')
    require(set(sample['strata'])==set(populations),'Niepełne warstwy próbki')
    membership=defaultdict(list)
    for name,pop in sorted(populations.items()):
        ranked=sorted((hashlib.sha256(encoded([config['sampling']['seed'],name,w])).hexdigest(),w) for w in pop)[:30]
        expected=[{'key':w,'sha256':d} for d,w in ranked]
        require(sample['strata'][name]=={'population':len(pop),'sample_size':len(expected),
            'coverage':'SAMPLED_NOT_VERIFIED' if pop else 'EMPTY_NOT_COVERAGE','selected':expected},'Zmieniona próbka '+name)
        for item in expected:membership[item['key']].append(name)
    require(sample['unique_selected_units']==len(membership),'Zły licznik próbki')
    require(sample['overlaps']==[{'key':w,'strata':n} for w,n in sorted(membership.items()) if len(n)>1],'Złe przecięcia próbki')
    template=read(root/'reports/review-template.json')
    require(template['status']=='UNREVIEWED' and template['schema_version']==1
            and template['version']==sample['version']
            and template['sample_sha256']==hashlib.sha256(encoded(sample)).hexdigest()
            and template['canonical_index_sha256']==digest(root/'reports/decisions.json')
            and template['evidence_sha256']=={n:digest(root/n) for n in ('POP00.txt.gz','reports/summary.json')},
            'Niepowiązany szablon przeglądu')
    require(template['items']==[{'key':w,'strata':n,'assessment':None,'reviewer':None,'source_justification':None}
                              for w,n in sorted(membership.items())], 'Zmieniony szablon przeglądu')
    if review_path:
        review=read(review_path)
        for field in ('sample_sha256','canonical_index_sha256','evidence_sha256','version','schema_version'):
            require(review[field]==template[field],'Niepowiązany przegląd')
        require(review['status']=='REVIEWED' and review['sha256sums_sha256']==digest(root/'SHA256SUMS'), 'Przegląd innego pakietu')
        require(len(review['items'])==len(membership),'Niepełny przegląd')
        require({i['key'] for i in review['items']}==set(membership),'Złe pozycje przeglądu')
        for item in review['items']:
            require(item['strata']==membership[item['key']] and item['assessment']=='correct'
                and isinstance(item.get('reviewer'),str) and item['reviewer'].strip()
                and isinstance(item.get('source_justification'),str) and item['source_justification'].strip()
                and item.get('affects_lists_or_links') is False,'Nierozstrzygnięta pozycja przeglądu')


def check(root, source_path, config_path, review_path=None):
    root,source_path,config_path=Path(root),Path(source_path).resolve(),Path(config_path).resolve()
    manifest=read(root/'release-manifest.json');source=read(source_path);config=read(config_path)
    require(manifest.get('kind')=='literaki-pop00-manifest' and manifest.get('package_id')=='POP00'
            and manifest.get('status')=='BUILT' and manifest.get('method')=='pop00-v1','Zły format POP00')
    require(config=={'version':'pop00-v1','adr':'docs/adr/ADR-009-pop00-v1.md','ipm_min':'0.1',
        'sampling':{'version':'pop00-quality-v1','seed':'literaki-slownik-pop00-v1','size_per_stratum':30,
        'encoding':'canonical JSON array [seed,stratum,key], UTF-8'}},'Zła polityka')
    require(manifest['config_sha256']==digest(config_path) and manifest['source_manifest_sha256']==digest(source_path),
            'Piny konfiguracji',3)
    require(source['version']=='pop00-sources-v1' and source['schema_version']==1,'Zły manifest wejść')
    require(set(source['inputs'])=={'base_pop','base_run','database','standard','orth'},'Złe wejścia')
    paths={k:(source_path.parent/v['path']).resolve() for k,v in source['inputs'].items()}
    pins={k:v['sha256'] for k,v in source['inputs'].items()}
    require(manifest['inputs']==pins and all(p.is_file() and digest(p)==pins[k] for k,p in paths.items()),'Piny wejść',3)
    run,pop=read(paths['base_run']),read(paths['base_pop'])
    require(run['readiness']=='FROZEN' and run['verification']['database_sha256']==pins['database']
        and pop['inputs']['database_sha256']==pins['database'] and pop['inputs']['standard_sha256']==pins['standard']
        and run['export']['release_manifest_sha256']==pop['inputs']['release_manifest_sha256'],'Niespójna podstawa',3)
    require(sum(a.get('kind')=='kwjp_orth' and a.get('genre')=='all' and a.get('sha256')==pins['orth']
                for a in run['inputs']['artifacts'])==1,'Obca lista orth/all',3)
    files(root,manifest)
    require(read(root/'method.json')==config,'Zła metoda pakietu')
    rows=semantics(paths,root,manifest,config)
    check_sample(root,rows,config,review_path)
    require(all(digest(p)==pins[k] for k,p in paths.items()) and digest(source_path)==manifest['source_manifest_sha256']
            and digest(config_path)==manifest['config_sha256'],'Wejścia zmieniły się podczas kontroli')
    require(all(digest(paths['base_pop'].parent/name)==pop['files'][name]['sha256']
                for name in ('POP0.txt.gz','reports/units.json','ATTRIBUTIONS.md')),
            'Pliki bazowego POP0 zmieniły się podczas kontroli')
    files(root,manifest)
    return {'status':'pass',**manifest['counts'],'review_checked':review_path is not None}


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--pop00-dir',required=True)
    parser.add_argument('--manifest',required=True)
    parser.add_argument('--config',required=True)
    parser.add_argument('--review')
    args=parser.parse_args(argv)
    try:
        report=check(args.pop00_dir,args.manifest,args.config,args.review)
        print(json.dumps(report,ensure_ascii=False,sort_keys=True))
        return 0
    except Refused as error:
        print(str(error),file=sys.stderr);return error.code
    except (OSError,ValueError,KeyError,TypeError,sqlite3.Error,EOFError) as error:
        print('Nieprawidłowy pakiet POP00: '+str(error),file=sys.stderr);return 4


if __name__=='__main__':
    sys.exit(main())
