"""Deterministyczny dobór próbek; bez kwalifikacji słów i automatycznego odbioru."""
import hashlib
import heapq
import re
import json

from .canonical import dumps
from .inputs import GeneratorError

ENCODING = 'canonical JSON array [seed,stratum,key], UTF-8'


def _config(config):
    if (not isinstance(config, dict)
            or set(config) != {'version', 'seed', 'size_per_stratum', 'encoding'}
            or config['version'] != 'quality-v1'
            or config['seed'] != 'literaki-slownik-g1-v1'
            or type(config['size_per_stratum']) is not int
            or config['size_per_stratum'] != 30
            or config['encoding'] != ENCODING):
        raise GeneratorError('Nieobsługiwana konfiguracja quality-v1', 2)


def sampling_digest(seed, stratum, key):
    return hashlib.sha256(dumps([seed, stratum, key]).encode('utf-8')).hexdigest()


class _WorstFirst:
    def __init__(self, digest, key):
        self.rank = (digest, key)

    def __lt__(self, other):
        return self.rank > other.rank


def sample_strata(strata, config):
    """Każda warstwa dostarcza uporządkowane klucze, np. SQL ORDER BY key.

    Powtórzenia klucza są liczone raz. Wejście jest strumieniowane, pamięć
    ograniczona do 30 wybranych jednostek na warstwę; niesortowane odrzucamy.
    Nazwy warstw i klucze nadaje osobny etap raportów, nie ten moduł.
    """
    _config(config)
    if (not isinstance(strata, dict)
            or any(not isinstance(name, str) or not name for name in strata)):
        raise GeneratorError('Warstwy wymagają niepustych identyfikatorów', 2)
    selected_by_key, report = {}, {}
    for name in sorted(strata):
        heap, previous, population = [], None, 0
        for key in strata[name]:
            if not isinstance(key, str) or not key:
                raise GeneratorError('Nieprawidłowy stabilny klucz próbki', 4, name)
            if previous is not None and key < previous:
                raise GeneratorError('Klucze próbki nie są uporządkowane', 4, name)
            if key == previous:
                continue
            previous = key
            population += 1
            entry = _WorstFirst(sampling_digest(config['seed'], name, key), key)
            if len(heap) < config['size_per_stratum']:
                heapq.heappush(heap, entry)
            elif entry.rank < heap[0].rank:
                heapq.heapreplace(heap, entry)
        selected = [{'key': item.rank[1], 'sha256': item.rank[0]}
                    for item in sorted(heap, key=lambda item: item.rank)]
        report[name] = {'population': population, 'sample_size': len(selected),
                        'coverage': 'SAMPLED_NOT_VERIFIED' if population else 'EMPTY_NOT_COVERAGE',
                        'selected': selected}
        for item in selected:
            selected_by_key.setdefault(item['key'], []).append(name)
    return {
        'schema_version': 1, **config, 'status': 'UNREVIEWED',
        'strata': report, 'unique_selected_units': len(selected_by_key),
        'overlaps': [{'key': key, 'strata': names}
                     for key, names in sorted(selected_by_key.items()) if len(names) > 1],
    }


def review_template(sample, *, canonical_index_sha256, evidence_sha256):
    """Szablon nie zatwierdza próbki; hash wiąże go z konkretnym wynikiem."""
    def valid_hash(value):
        return isinstance(value, str) and re.fullmatch('[0-9a-f]{64}', value)
    if (not valid_hash(canonical_index_sha256)
            or not isinstance(evidence_sha256, dict) or not evidence_sha256
            or any(not isinstance(key, str) or not key or not valid_hash(value)
                   for key, value in evidence_sha256.items())):
        raise GeneratorError('Przegląd wymaga hashy indeksu i dowodów', 2)
    memberships = {}
    for name, stratum in sorted(sample['strata'].items()):
        for item in stratum['selected']:
            memberships.setdefault(item['key'], []).append(name)
    payloads={}
    if 'items' in sample:
        for item in sample['items']:
            key=item.get('key') if isinstance(item,dict) else None
            if key not in memberships or key in payloads:
                raise GeneratorError('Niespójne jednostki próbki do przeglądu',4)
            payloads[key]=item
        if set(payloads)!=set(memberships):
            raise GeneratorError('Niepełne jednostki próbki do przeglądu',4)
    return {
        'schema_version': 1, 'version': sample['version'], 'status': 'UNREVIEWED',
        'canonical_index_sha256': canonical_index_sha256,
        'sample_sha256': hashlib.sha256(dumps(sample).encode('utf-8')).hexdigest(),
        'evidence_sha256': dict(sorted(evidence_sha256.items())),
        'items': [{'key': key, 'strata': names, 'assessment': None,
                   'reviewer': None, 'source_justification': None,
                   **({'selected_unit':payloads[key]} if payloads else {})}
                  for key, names in sorted(memberships.items())],
    }


def sample_persisted_analyses(db, config):
    """Diagnostyczne warstwy ocen; pełne źródło i obie oceny wybranej analizy.

    Przegląd pozostaje UNREVIEWED. Te warstwy uzupełniają, a nie zastępują
    wymagane warstwy słowne i linków pełnego quality-v1.
    """
    from .reports import unresolved_report
    coverage=unresolved_report(db)
    join='''from analysis a join variant_decision d on d.analysis_key=a.analysis_key
        join decision_payload p on p.assessment_key=d.assessment_key'''
    kind="coalesce(json_extract(p.assessment,'$.semantic_trace.kind'),case when a.candidate_key is null then 'source_expansion' else 'construction' end)"
    strata={}
    for name in ('source_expansion','construction','documented_use','unresolved_remainder'):
        strata['analysis:'+name]=(row[0] for row in db.execute(
            'select distinct a.analysis_key '+join+' where '+kind+'=? order by a.analysis_key',(name,)))
    for variant in ('broad','standard'):
        for status in ('accept','reject','unresolved'):
            strata[variant+':'+status]=(row[0] for row in db.execute(
                'select a.analysis_key '+join+' where d.variant=? and d.membership_status=? order by a.analysis_key',
                (variant,status)))
    sample=sample_strata(strata,config)
    selected=sorted({value['key'] for stratum in sample['strata'].values() for value in stratum['selected']})
    items=[_analysis_item(db,key) for key in selected]
    return {**sample,'scope':'persisted_analysis_strata_not_full_quality_matrix',
            'full_quality_matrix_pending':True,'coverage':coverage['variants'],'items':items}


def sample_corpus_links(db, config):
    """Wszystkie metody/statusy linków; F raz przy jednostce, nie krawędzi.

    To próbka do przeglądu powiązań, nie dowód poprawności językowej.
    Warstwy słowne i odbiór całej macierzy pozostają osobnymi zadaniami.
    """
    from .links import link_report
    _config(config)
    methods={'kwjp_lemma':'NFC_LEMMA_POS','kwjp_orth':'NFC_FORM',
             'kwjp_orth_lc':'NFC_LOWER_FORM','kwjp_bigram':'BIGRAM_SEGMENTS'}
    statuses=('EXACT_CANDIDATE','AMBIGUOUS','UNMATCHED','NOT_APPLICABLE')
    tables={r[0] for r in db.execute("select name from sqlite_master where type='table'")}
    if not {'evidence_link','evidence_candidate'}<=tables:
        raise GeneratorError('Próbka wymaga utrwalonych powiązań KWJP',4)
    from .constructions import checked_spelling_variants
    checked_spelling_variants(db)
    coverage=link_report(db)
    counts={}
    for kind,method,status,n in db.execute('''select s.kind,l.method,l.status,count(*) from evidence_link l
        join corpus_evidence e on e.id=l.evidence_id join source_artifact s on s.source_id=e.source_id
        group by s.kind,l.method,l.status'''):
        if kind not in methods or methods[kind]!=method or status not in statuses:
            raise GeneratorError('Nieznana metoda lub kategoria powiązań próbki',4)
        if (method=='BIGRAM_SEGMENTS')!=(status=='NOT_APPLICABLE'):
            raise GeneratorError('Niespójna stosowalność powiązania próbki',4)
        counts[method,status]=counts.get((method,status),0)+n
    # Zachowanie historycznej bazy linków bez candidate_key, bez migracji.
    derived='candidate_key' in {r[1] for r in db.execute('pragma table_info(evidence_candidate)')}
    # Dwa uporządkowane strumienie zamiast pięciu milionów skanów krawędzi.
    count_rows=iter(db.execute('select evidence_id,count(*) from evidence_candidate group by evidence_id order by evidence_id'))
    current=next(count_rows,None)
    for evidence_id,status in db.execute('select evidence_id,status from evidence_link order by evidence_id'):
        if current and current[0]<evidence_id:
            raise GeneratorError('Krawędź próbki bez jednostki powiązania',4)
        n=current[1] if current and current[0]==evidence_id else 0
        if n:current=next(count_rows,None)
        expected='EXACT_CANDIDATE' if n==1 else 'AMBIGUOUS' if n>1 else None
        if (expected and status!=expected) or (not expected and status not in ('UNMATCHED','NOT_APPLICABLE')):
            raise GeneratorError('Kategoria linku nie odpowiada liczbie kandydatów',4)
    if current:raise GeneratorError('Krawędź próbki bez jednostki powiązania',4)
    key_sql="json_array('corpus',e.source_id,e.row_number)"
    strata={}
    for method in sorted(methods.values()):
        for status in statuses:
            strata['link:'+method+':'+status]=(row[0] for row in db.execute(
                'select '+key_sql+' as key from corpus_evidence e join evidence_link l on l.evidence_id=e.id '
                'where l.method=? and l.status=? order by key',(method,status))) if counts.get((method,status)) else []
    sample=sample_strata(strata,config)
    selected=sorted({x['key'] for stratum in sample['strata'].values() for x in stratum['selected']})
    items=[]
    for key in selected:
        _,sid,row=json.loads(key)
        raw=db.execute('''select e.id,e.unit_1,e.unit_2,e.pos,e.raw_metrics,e.typed_metrics,e.freq,s.kind,s.metadata,
            l.method,l.status,l.sense_identity_confirmed,l.reason from corpus_evidence e
            join source_artifact s on s.source_id=e.source_id join evidence_link l on l.evidence_id=e.id
            where e.source_id=? and e.row_number=?''',(sid,row)).fetchone()
        ident,first,second,pos,raw_metrics,typed,freq,kind,metadata,method,status,sense,reason=raw
        if sense!=0:raise GeneratorError('Próbka nie może poświadczać tożsamości sensu z linku strukturalnego',4)
        meta=json.loads(metadata);candidates=[]
        select='select lexeme_id,form_id,'+('candidate_key' if derived else 'null')+' from evidence_candidate where evidence_id=? and '
        columns=['lexeme_id','form_id']+(['candidate_key'] if derived else [])
        sql=' union all '.join(select+column+' is not null' for column in columns)
        for lid,fid,ckey in db.execute(sql,tuple(ident for _ in columns)):
            if lid is not None:
                source,lemma,base=db.execute('select source_id,lemma_id,lemma_base from lexeme where id=?',(lid,)).fetchone()
                candidate={'kind':'lexeme','source_id':source,'lemma_id':lemma,'lemma_base':base}
            elif fid is not None:
                original,nfc,game_key=db.execute('select original,nfc,game_key from surface_form where id=?',(fid,)).fetchone()
                candidate={'kind':'source_form','original':original,'nfc':nfc,'game_key':game_key}
            else:
                encoded=db.execute('select payload from derivation_candidate where candidate_key=?',(ckey,)).fetchone()[0]
                candidate={'kind':'derived_form','candidate_key':ckey,'trace':json.loads(encoded)}
            candidates.append(candidate)
        items.append({'key':key,'evidence':{'source_id':sid,'row_number':row,'source_sha256':meta.get('sha256'),
            'kind':kind,'genre':meta.get('genre'),'publication_threshold':meta.get('publication_threshold'),
            'unit_1':first,'unit_2':second,'pos':pos,'raw_metrics':json.loads(raw_metrics),
            'typed_metrics':json.loads(typed),'freq':freq},'method':method,'status':status,
            'sense_identity_confirmed':False,'reason':reason,'candidates':sorted(candidates,key=dumps)})
    return {**sample,'scope':'full_corpus_units_and_structural_candidates_not_lexical_quality',
        'full_quality_matrix_pending':True,'coverage':coverage,'items':items}


def _analysis_item(db,key):
    row=db.execute('''select a.interpretation_id,a.candidate_key,a.expanded_tag,a.original,a.nfc,a.game_key,a.length,a.policy_version
        from analysis a where a.analysis_key=?''',(key,)).fetchone()
    iid,ckey,tag,original,nfc,game_key,length,version=row
    source=None
    if iid is not None:
        fields=('source_id','first_source_row','original','lemma_id','raw_tag','names','qualifiers')
        raw=db.execute('''select i.source_id,i.first_row,f.original,l.lemma_id,i.tag,i.names,i.qualifiers,s.metadata
            from interpretation i join surface_form f on f.id=i.form_id join lexeme l on l.id=i.lexeme_id
            join source_artifact s on s.source_id=i.source_id where i.id=?''',(iid,)).fetchone()
        source=dict(zip(fields,raw[:7]),source_sha256=json.loads(raw[7]).get('sha256'))
    assessments={}
    for variant,encoded in db.execute('''select d.variant,p.assessment from variant_decision d
        join decision_payload p on p.assessment_key=d.assessment_key where d.analysis_key=? order by d.variant''',(key,)):
        value=json.loads(encoded)
        value['profile'].update(original=original,nfc=nfc,game_key=game_key,length=length)
        assessments[variant]=value
    candidate=json.loads(db.execute('select payload from derivation_candidate where candidate_key=?',(ckey,)).fetchone()[0]) if ckey else None
    return {'key':key,'source_record':source,'candidate_key':ckey,'candidate':candidate,
        'expanded_tag':tag,'original':original,'game_key':game_key,'policy_version':version,'assessments':assessments}


def sample_word_analyses(db, config, definitions):
    """Warstwy słowne, wszystkie analizy i oba warianty; bez verdictu.

    Przynależność do warstwy służy doborowi przeglądu, nie rozstrzyga znaczeń.
    Specjalistyczność ograniczona do udokumentowanych etykiet tematycznych.
    """
    from functools import lru_cache
    from .reports import unresolved_report
    from .policy import HISTORICAL_LABELS,KNOWN_NAME_LABELS,CONFIRMED_CONSTRUCTOR_RULES
    from .decisions import aggregate
    _config(config)
    if (not isinstance(definitions,dict) or set(definitions)!={'version','specialist_topics','basis','specialist_scope'}
            or definitions['version']!='word-strata-v1'
            or definitions['specialist_scope']!='documented_topics_not_all_specialist_meanings'
            or not isinstance(definitions['basis'],str) or not definitions['basis']
            or not isinstance(definitions['specialist_topics'],list) or not definitions['specialist_topics']
            or any(not isinstance(v,str) or not v for v in definitions['specialist_topics'])
            or len(set(definitions['specialist_topics']))!=len(definitions['specialist_topics'])):
        raise GeneratorError('Nieobsługiwane definicje warstw słownych',2)
    coverage=unresolved_report(db)
    topics=frozenset(definitions['specialist_topics'])
    @lru_cache(maxsize=4096)
    def history(q):return int(bool(set(q.split('|'))&HISTORICAL_LABELS))
    @lru_cache(maxsize=4096)
    def specialist(q):return int(bool({atom for label in q.split('|') for atom in label.split(',')}&topics))
    @lru_cache(maxsize=4096)
    def proper(n):return int(bool(set(n.split('|'))&(KNOWN_NAME_LABELS-{'nazwa_pospolita'})))
    @lru_cache(maxsize=4096)
    def common(n):return int(not n or 'nazwa_pospolita' in n.split('|'))
    for name,fn in [('quality_history',history),('quality_specialist',specialist),('quality_proper',proper),('quality_common',common)]:
        db.create_function(name,1,fn,deterministic=True)
    db.execute('''create temp view if not exists quality_word_features as
        select a.game_key,min(a.length) as length,
        count(distinct json_array(coalesce(i.source_id,json_extract(c.payload,'$.components[0].interpretation.source_id')),coalesce(l.lemma_id,c.lemma_id))) as lexemes,
        max(quality_history(coalesce(i.qualifiers,c.qualifiers))) as historical,
        max(quality_specialist(coalesce(i.qualifiers,c.qualifiers))) as specialist,
        max(quality_proper(coalesce(i.names,c.names))) as proper,
        max(quality_common(coalesce(i.names,c.names))) as common
        from analysis a left join interpretation i on i.id=a.interpretation_id
        left join lexeme l on l.id=i.lexeme_id left join derivation_candidate c on c.candidate_key=a.candidate_key
        group by a.game_key''')
    key="json_array('word',game_key)"
    strata={}
    for name,condition in [('short','length between 2 and 3'),('homonyms','lexemes>1'),
        ('history','historical=1'),('specialist','specialist=1'),('proper_common','proper=1 and common=1')]:
        strata['word:'+name]=(row[0] for row in db.execute('select '+key+' as key from quality_word_features where '+condition+' order by key'))
    source_classes={row[0] for row in db.execute("select distinct case when instr(expanded_tag,':')>0 then substr(expanded_tag,1,instr(expanded_tag,':')-1) else expanded_tag end from analysis where interpretation_id is not null")} | {'praet','winien'}
    for pos in sorted(source_classes):
        strata['word:source_class:'+pos]=(row[0] for row in db.execute("select distinct json_array('word',game_key) as key from analysis where interpretation_id is not null and (expanded_tag=? or expanded_tag like ?) order by key",(pos,pos+':%')))
    known=set(CONFIRMED_CONSTRUCTOR_RULES)
    actual={row[0] for row in db.execute('select distinct rule_id from derivation_candidate')}
    if actual-known:raise GeneratorError('Nieznana klasa konstrukcji w próbce słów',4)
    for rule in sorted(known):
        strata['word:construction:'+rule]=(row[0] for row in db.execute("select distinct json_array('word',game_key) as key from derivation_candidate where rule_id=? order by key",(rule,)))
    for variant in ('broad','standard'):
        join='''from analysis a join variant_decision d on d.analysis_key=a.analysis_key where d.variant=? group by a.game_key'''
        for name,condition in [('unresolved',"max(d.membership_status='accept')=0 and max(d.membership_status='unresolved')=1"),
            ('filter_changed',"min(d.membership_status='reject')=1")]:
            strata['word:'+name+':'+variant]=(row[0] for row in db.execute("select json_array('word',a.game_key) as key "+join+' having '+condition+' order by key',(variant,)))
    sample=sample_strata(strata,config)
    selected=sorted({x['key'] for stratum in sample['strata'].values() for x in stratum['selected']})
    items=[]
    for selected_key in selected:
        _,game_key=json.loads(selected_key)
        analyses=[_analysis_item(db,row[0]) for row in db.execute('select analysis_key from analysis where game_key=? order by analysis_key',(game_key,))]
        membership={variant:aggregate([{'game_key':game_key,'membership':{variant:a['assessments'][variant]['membership']}} for a in analyses],variant) for variant in ('broad','standard')}
        items.append({'key':selected_key,'game_key':game_key,'membership':membership,'analyses':analyses})
    return {**sample,'scope':'persisted_word_strata_all_analyses_both_variants_not_final_review',
        'definitions':definitions,'coverage':coverage['variants'],'items':items,'full_quality_matrix_pending':True,
        'filter_changed_basis':'aggregate_reject_after_known_rejection_checks_counterfactual_without_those_filters',
        'name_common_basis':'source_proper_label_and_common_or_unlabelled_candidate_not_confirmed_senses'}
