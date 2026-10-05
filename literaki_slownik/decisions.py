"""Wszystkie warunki przy jednej analizie; agregacja dopiero po kwalifikacji."""
from .inputs import GeneratorError
from .policy import (assess_profile, spelling_checks, release_scope_checks,
                     approved_qualifier_checks, orthography_checks, construction_orthography_checks,
                     source_game_checks, resident_use_checks, RESIDENT_RELATION_CONDITIONS, VERSION as POLICY_VERSION)

STATUSES = frozenset({'accept', 'reject', 'unresolved'})
VARIANTS = ('broad', 'standard')
DOCUMENTARY_RULE_EVIDENCE = {
    'game-documented-resident-capital-v1':'87daaddd86911370d4df3c1e5769028e8fa9087e052c8954b70ec173ada2d72e',
    'orthography-documented-resident-capital-2026-v1':'87daaddd86911370d4df3c1e5769028e8fa9087e052c8954b70ec173ada2d72e',
    'game-documented-surname-component-v1':'3e3d104b1a210e0097c511b36f1440de539413ec64079fba505c47c3bf7684ca',
    'game-mandatory-capital-2026-v1':'87daaddd86911370d4df3c1e5769028e8fa9087e052c8954b70ec173ada2d72e',
    'orthography-2026-resident-capital-v1':'87daaddd86911370d4df3c1e5769028e8fa9087e052c8954b70ec173ada2d72e',
}


def assess_diagnostic(original, qualifiers, additional_checks=(), source_analyses=(), candidate=None,
                      *, documented_condition_ids=None, lexical_use_review=None):
    """Wspólna ocena explain i zapisu; nie aktywuje nierozstrzygniętej polityki."""
    pending=[{'rule_id':'linguistic-policy-not-active-v1','status':'unresolved',
              'message':'Pełna polityka językowa G3/G4 nie jest jeszcze aktywna.','evidence':[]}]
    game=[{'rule_id':'game-metadata-not-complete-v1','status':'unresolved',
           'message':'Pozostałe udokumentowane warunki growe wymagają domknięcia.','evidence':[]}]
    if candidate is not None:
        game+=source_game_checks(dict(raw_tag=candidate['expanded_tag'],names=candidate['names'],qualifiers=qualifiers),candidate=candidate)
    else:
        game+=[check for source in source_analyses for check in source_game_checks(source)]
    def in_scope(check):
        return (documented_condition_ids is None or check['rule_id'] not in DOCUMENTARY_RULE_EVIDENCE
                or check['rule_id'] in documented_condition_ids)
    game=[check for check in game if in_scope(check)]
    game+=resident_use_checks(lexical_use_review)
    return assess_analysis(original,
        language={v:pending+approved_qualifier_checks(qualifiers,v)+list(additional_checks)
                  +[check for source in source_analyses for check in orthography_checks(source,v) if in_scope(check)]
                  +construction_orthography_checks(candidate,v)
                  +lexical_use_checks(lexical_use_review,v)+resident_use_checks(lexical_use_review,v) for v in VARIANTS},
        scope_checks=release_scope_checks(candidate),game_checks=game)


DOCUMENTED_LEXICAL_USE_SOURCES = {
    'sgjp-authors-phrase-wznak-v1': (6770165,'wznak','wznak',''),
    'sgjp-authors-phrase-dwojnasob-v1': (1647764,'dwójnasób','dwójnasób',''),
    'sgjp-authors-phrase-krocset-v1': (2244647,'kroćset','kroćset','daw.'),
    'sgjp-authors-phrase-rosciez-v1': (5520636,'roścież','roścież:F',''),
    'sgjp-authors-phrase-trojnasob-v1': (6044918,'trójnasób','trójnasób',''),
    'sgjp-authors-phrase-ziem-v1': (7186612,'ziem','ziem','gwar.'),
}
DOCUMENTED_LEXICAL_RULE = 'linguistic-documented-use-lexical-proof-v1'


def lexical_use_checks(review, variant):
    """Wyłącznie sprawdzony przegląd własny; nie domyka innych warunków."""
    if not review or 'lexical_proof' not in review:return []
    return [{'rule_id':review['lexical_proof'],'status':'accept' if variant=='broad' else 'unresolved',
        'message':('Dodatni dowód leksykalny BROAD dokładnie udokumentowanego użycia; inne warunki osobno.'
                   if variant=='broad' else 'Dowód BROAD nie rozstrzyga aktualnej kwalifikacji STANDARD.'),
        'scope':'documented_use_lexical_condition_only','evidence':review['evidence']}]


USE_REVIEW_ID = 'own-semantic-use-review-v1'


def checked_use_reviews(db, reviews):
    """Własne obserwacje przypięte do pięciu pól; nie import glos czytnika.

    Pierwszy format dokumentuje pojedyncze użycia. Nie daje prawa do zamknięcia
    całej macierzy warunków ani do wstrzyknięcia wyników accept/reject.
    """
    import json
    import re
    from .canonical import dumps
    if not isinstance(reviews, (list, tuple)):
        raise GeneratorError('Przegląd użyć wymaga listy własnych adnotacji',4)
    result, seen = {}, set()
    try:
        for review in reviews:
            if (set(review) - {'documented_conditions','lexical_proof'} != {'use_id','source','description','coverage','evidence'}
                    or not isinstance(review['use_id'],str)
                    or not re.fullmatch('[a-z0-9][a-z0-9_-]{0,127}',review['use_id'])
                    or review['use_id'] in seen
                    or not isinstance(review['description'],str) or not review['description'].strip()
                    or review['coverage'] != 'documented_use_only'):
                raise GeneratorError('Nieprawidłowe, powtórzone lub nadmiernie kompletne użycie',4)
            seen.add(review['use_id'])
            source=review['source']
            fields=('source_id','source_sha256','first_source_row','original','lemma_id','raw_tag','names','qualifiers')
            if (set(source) != set(fields) or type(source['first_source_row']) is not int
                    or source['first_source_row']<1
                    or any(not isinstance(source[k],str) for k in fields if k!='first_source_row')):
                raise GeneratorError('Niepełna tożsamość źródłowa użycia',4)
            row=db.execute('''select i.id,f.original,l.lemma_id,i.tag,i.names,i.qualifiers,s.metadata
                from interpretation i join surface_form f on f.id=i.form_id
                join lexeme l on l.id=i.lexeme_id join source_artifact s on s.source_id=i.source_id
                where i.source_id=? and i.first_row=? and f.original=? and l.lemma_id=?''',
                (source['source_id'],source['first_source_row'],source['original'],source['lemma_id'])).fetchone()
            if (row is None or tuple(source[k] for k in fields[3:]) != row[1:6]
                    or json.loads(row[6]).get('sha256') != source['source_sha256']
                    or not re.fullmatch('[a-f0-9]{64}',source['source_sha256'])):
                raise GeneratorError('Użycie nie odpowiada dokładnemu rekordowi i snapshotowi',4)
            evidence=review['evidence']
            if not isinstance(evidence,list) or not evidence:
                raise GeneratorError('Użycie wymaga dopuszczonego dowodu',4)
            for proof in evidence:
                if (set(proof)!={'artifact_id','sha256','locator','status','role'}
                        or proof['status']!='ALLOWED' or proof['role']!='own_documentary_review'
                        or any(not isinstance(proof[k],str) or not proof[k] for k in proof)
                        or not re.fullmatch('[a-f0-9]{64}',proof['sha256'])):
                    raise GeneratorError('Niedopuszczony lub nieprzypięty dowód użycia',4)
            conditions=review.get('documented_conditions',[])
            if (not isinstance(conditions,list) or any(not isinstance(rule,str) for rule in conditions)
                    or len(set(conditions))!=len(conditions)
                    or set(conditions)-set(DOCUMENTARY_RULE_EVIDENCE)):
                raise GeneratorError('Nieznany lub powtórzony warunek dokumentacyjny użycia',4)
            resident=resident_use_checks(review)
            resident+=resident_use_checks(review,'standard')
            if (set(conditions)&RESIDENT_RELATION_CONDITIONS or review['use_id'].startswith('sgjp-relation-warszawianka-')) and not resident:
                raise GeneratorError('Nieprzypięty dowód relacji nazwy mieszkańca',4)
            available={c['rule_id'] for c in source_game_checks(source)}
            available.update(c['rule_id'] for c in resident)
            available.update(c['rule_id'] for v in VARIANTS for c in orthography_checks(source,v))
            if (set(conditions)-available or any(not any(p['sha256']==DOCUMENTARY_RULE_EVIDENCE[rule] for p in evidence)
                                                   for rule in conditions)):
                raise GeneratorError('Warunek nie ma dokładnego mapowania i zgodnego dowodu użycia',4)
            if 'lexical_proof' in review:
                identity=DOCUMENTED_LEXICAL_USE_SOURCES.get(review['use_id'])
                expected_source=(dict(source_id='sgjp-20260823',
                    source_sha256='3b2ee079143bc95186370fd528735779c4ba62f4ce14e30cf6622ceb566e9810',
                    first_source_row=identity[0],original=identity[1],lemma_id=identity[2],raw_tag='frag',names='',qualifiers=identity[3])
                    if identity else None)
                if (review['lexical_proof']!=DOCUMENTED_LEXICAL_RULE or source!=expected_source
                        or not any(p['artifact_id']=='sgjp-theory-own-review' and
                            p['sha256']==DOCUMENTARY_RULE_EVIDENCE['game-documented-surname-component-v1']
                            for p in evidence)):
                    raise GeneratorError('Nieudokumentowane mapowanie dodatniego dowodu leksykalnego',4)
            # Kopia kanoniczna odcina późniejsze mutacje obiektu caller.
            result.setdefault(row[0],[]).append(json.loads(dumps(review)))
        for items in result.values():items.sort(key=lambda item:item['use_id'])
        return result
    except GeneratorError:raise
    except (KeyError,TypeError,ValueError,AttributeError) as error:
        raise GeneratorError('Nieprawidłowa adnotacja użycia',4) from error


def checked_persisted_use_coverage(db):
    """Nie pozwól zgubić pozostałości ani sfałszować użycia poprawnym hashem JSON."""
    from .constructions import checked_spelling_variants
    checked_spelling_variants(db)
    import hashlib
    import json
    from .canonical import dumps
    from .sgjp import expand_tag
    if not db.execute("select 1 from sqlite_master where name='source_artifact'").fetchone():return
    marker=db.execute('select kind,metadata from source_artifact where source_id=?',(USE_REVIEW_ID,)).fetchone()
    if marker is None:return
    try:
        kind,encoded=marker;metadata=json.loads(encoded)
        if (kind!='own_documentary_review' or set(metadata)!={'sha256','reviews','scope'}
                or metadata['scope']!='documented_use_only_not_complete_semantics'):
            raise GeneratorError('Niezgodna metryka przeglądu użyć',4)
        reviewed=checked_use_reviews(db,metadata['reviews'])
        ordered=sorted((r for values in reviewed.values() for r in values),key=lambda item:item['use_id'])
        if not reviewed or hashlib.sha256(dumps(ordered).encode()).hexdigest()!=metadata['sha256']:
            raise GeneratorError('Niezgodny hash lub pusty zapis przeglądu użyć',4)
        for iid,reviews in reviewed.items():
            source={k:v for k,v in reviews[0]['source'].items() if k!='source_sha256'}
            remainder={'kind':'unresolved_remainder','coverage':'incomplete','source':reviews[0]['source'],
                'documented_use_ids':[r['use_id'] for r in reviews],
                'message':'Nierozpoznane możliwości; dowody użyć nie zamykają pełnej kwalifikacji.'}
            expected={}
            for tag in expand_tag(source['raw_tag']):
                key=hashlib.sha256(dumps(['source',source,tag]).encode()).hexdigest()
                expected[key]=(tag,remainder)
                for review in reviews:
                    key=hashlib.sha256(dumps(['documented_use',source,tag,review]).encode()).hexdigest()
                    expected[key]=(tag,{'kind':'documented_use',**review})
            actual=dict(db.execute('select analysis_key,expanded_tag from analysis where interpretation_id=?',(iid,)))
            if actual!={k:v[0] for k,v in expected.items()}:
                raise GeneratorError('Niepełne lub zmienione pokrycie użyć i nierozpoznanych możliwości',4)
            checked=set()
            for key,variant,payload_key,encoded in db.execute('''select a.analysis_key,d.variant,p.assessment_key,p.assessment
                from analysis a join variant_decision d on d.analysis_key=a.analysis_key
                join decision_payload p on p.assessment_key=d.assessment_key where a.interpretation_id=?''',(iid,)):
                value=json.loads(encoded)
                if (hashlib.sha256(encoded.encode()).hexdigest()!=payload_key
                        or value.get('semantic_trace')!=expected[key][1]):
                    raise GeneratorError('Zapisany ślad użycia różni się od przypiętego przeglądu',4)
                trace=expected[key][1]
                relation=trace if trace['kind']=='documented_use' else None
                game=resident_use_checks(relation)
                language=resident_use_checks(relation,variant)+lexical_use_checks(relation,variant)
                for layer,checks in (('game',game),('language',language),('membership',game+language)):
                    actual=sorted(dumps(c) for c in value[layer]['checks']
                                  if c['rule_id'] in RESIDENT_RELATION_CONDITIONS|{DOCUMENTED_LEXICAL_RULE})
                    if actual!=sorted(dumps(c) for c in checks):
                        raise GeneratorError('Zmieniony zakres lub wynik warunku udokumentowanego użycia',4)
                if (key,variant) in checked or variant not in VARIANTS:
                    raise GeneratorError('Nieprawidłowe pokrycie wariantów użycia',4)
                checked.add((key,variant))
            if checked!={(key,v) for key in expected for v in VARIANTS}:
                raise GeneratorError('Brak zapisanej oceny użycia lub pozostałości',4)
    except GeneratorError:raise
    except (KeyError,ValueError,TypeError,AttributeError) as error:
        raise GeneratorError('Nieprawidłowy utrwalony przegląd użyć',4) from error


def materialize_assessments(db, batch_size=10000, *, use_reviews=()):
    """Utrwal wszystkie rozwinięcia i warianty, zachowując unknown i wcześniejsze dane.

    To zapis diagnostyczny. Dopiero domknięcie macierzy pozwoli na pełną
    kwalifikację. Wersja lub wynik różniące się od istniejących wymagają nowego build.
    """
    import hashlib
    import json
    from .canonical import dumps
    from .sgjp import expand_tag
    if type(batch_size) is not int or not 1<=batch_size<=10000:
        raise GeneratorError('Porcja ocen musi mieć od 1 do 10 000 analiz',2)
    if db.execute('select 1 from analysis where policy_version!=? limit 1',(POLICY_VERSION,)).fetchone():
        raise GeneratorError('Inna wersja ocen; wymagany nowy build bez nadpisania poprzednich danych',4)
    from .constructions import checked_spelling_variants
    checked_spelling_variants(db)
    reviewed=checked_use_reviews(db,use_reviews)
    review_payload=dumps(sorted((item for items in reviewed.values() for item in items),key=lambda item:item['use_id']))
    marker=db.execute('select kind,metadata from source_artifact where source_id=?',(USE_REVIEW_ID,)).fetchone()
    expected_marker=('own_documentary_review',dumps({'sha256':hashlib.sha256(review_payload.encode()).hexdigest(),
        'reviews':json.loads(review_payload),'scope':'documented_use_only_not_complete_semantics'})) if reviewed else None
    if marker!=expected_marker and (marker is not None or db.execute('select 1 from analysis limit 1').fetchone()):
        raise GeneratorError('Inny przegląd użyć; wymagany nowy build bez zmiany wcześniejszych ocen',4)
    for key,payload in db.execute('select assessment_key,assessment from decision_payload'):
        if hashlib.sha256(payload.encode()).hexdigest()!=key:
            raise GeneratorError('Zmieniona treść powodów oceny; wymagany nowy build',4)
    new_analyses=new_decisions=source_count=candidate_count=0
    tag_count=use_count=remainder_count=compact_count=0
    analysis_batch=[];decision_batch=[];payload_batch={}
    existing=bool(db.execute('select 1 from analysis limit 1').fetchone())
    def flush():
        nonlocal new_analyses,new_decisions
        if not analysis_batch:return
        db.executemany('insert or ignore into decision_payload values (?,?)',payload_batch.items())
        new_analyses+=db.executemany('insert or ignore into analysis values (?,?,?,?,?,?,?,?,?)',analysis_batch).rowcount
        new_decisions+=db.executemany('insert or ignore into variant_decision values (?,?,?,?,?,?,?,?)',decision_batch).rowcount
        db.commit();analysis_batch.clear();decision_batch.clear();payload_batch.clear()
    def save(key,iid,ckey,tag,assessed):
        profile=assessed['profile']
        row=(key,iid,ckey,tag,assessed['original'],profile['nfc'],assessed['game_key'],profile['length'],POLICY_VERSION)
        old=db.execute('select * from analysis where analysis_key=?',(key,)).fetchone() if existing else None
        if old is not None and old!=row:
            raise GeneratorError('Istniejąca analiza ma inną treść; wymagany nowy build',4)
        analysis_batch.append(row)
        for variant in VARIANTS:
            payload={'language':assessed['language'][variant],
                     **{k:assessed[k] for k in ('game','release_scope')},
                     'profile':{k:v for k,v in profile.items() if k not in ('original','nfc','game_key','length')},
                     'membership':assessed['membership'][variant]}
            if 'semantic_trace' in assessed:payload['semantic_trace']=assessed['semantic_trace']
            encoded=dumps(payload);assessment_key=hashlib.sha256(encoded.encode()).hexdigest()
            payload_batch[assessment_key]=encoded
            values=(key,variant,*[payload[k]['status'] for k in ('language','game','profile','release_scope','membership')],assessment_key)
            old=db.execute('select * from variant_decision where analysis_key=? and variant=?',(key,variant)).fetchone() if existing else None
            if old is not None and old!=values:
                raise GeneratorError('Istniejąca ocena ma inną treść; wymagany nowy build',4)
            decision_batch.append(values)
        if len(analysis_batch)>=batch_size:flush()
    fields=('source_id','first_source_row','original','lemma_id','raw_tag','names','qualifiers')
    source_hashes={sid:json.loads(metadata).get('sha256')
                   for sid,metadata in db.execute('select source_id,metadata from source_artifact')}
    if expected_marker and marker is None:
        db.execute('insert into source_artifact values (?,?,?)',(USE_REVIEW_ID,*expected_marker))
    query='''select i.id,i.source_id,i.first_row,f.original,l.lemma_id,i.tag,i.names,i.qualifiers
        from interpretation i join surface_form f on f.id=i.form_id join lexeme l on l.id=i.lexeme_id
        order by i.source_id,i.first_row'''
    for row in db.execute(query):
        compact_count+=1
        source=dict(zip(fields,row[1:]))
        # Każde źródłowe rozwinięcie pozostaje osobną spójną analizą.
        for tag in expand_tag(source['raw_tag']):
            tag_count+=1
            key=hashlib.sha256(dumps(['source',source,tag]).encode()).hexdigest()
            assessed=assess_diagnostic(source['original'],source['qualifiers'],source_analyses=[dict(source,raw_tag=tag,source_sha256=source_hashes[source['source_id']])])
            if row[0] in reviewed:
                assessed=assess_diagnostic(source['original'],source['qualifiers'],
                    source_analyses=[dict(source,raw_tag=tag,source_sha256=source_hashes[source['source_id']])],
                    documented_condition_ids=[])
                assessed['semantic_trace']={'kind':'unresolved_remainder','coverage':'incomplete',
                    'source':reviewed[row[0]][0]['source'],'documented_use_ids':[r['use_id'] for r in reviewed[row[0]]],
                    'message':'Nierozpoznane możliwości; dowody użyć nie zamykają pełnej kwalifikacji.'}
                remainder_count+=1
                for review in reviewed[row[0]]:
                    use_key=hashlib.sha256(dumps(['documented_use',source,tag,review]).encode()).hexdigest()
                    use=assess_diagnostic(source['original'],source['qualifiers'],
                        additional_checks=[{'rule_id':'semantic-use-qualification-pending-v1','status':'unresolved',
                        'message':'Udokumentowane użycie wymaga osobnego domknięcia warunków.',
                        'evidence':review['evidence']}],
                        source_analyses=[dict(source,raw_tag=tag,source_sha256=source_hashes[source['source_id']])],
                        documented_condition_ids=review.get('documented_conditions',[]),lexical_use_review=review)
                    use['semantic_trace']={'kind':'documented_use',**review}
                    save(use_key,row[0],None,tag,use);use_count+=1;source_count+=1
            save(key,row[0],None,tag,assessed);source_count+=1
    for ckey,payload in db.execute('select candidate_key,payload from derivation_candidate order by candidate_key'):
        candidate=json.loads(payload);proof=candidate.get('linguistic_evidence')
        components=[c['interpretation'] for c in candidate['components'] if c['kind']=='source_interpretation']
        assessed=assess_diagnostic(candidate['original'],candidate['qualifiers'],[proof] if proof else [],components,candidate)
        key=hashlib.sha256(dumps(['construction',ckey]).encode()).hexdigest()
        save(key,None,ckey,candidate['expanded_tag'],assessed);candidate_count+=1
    flush()
    actual_analyses=db.execute('select count(*) from analysis').fetchone()[0]
    actual_decisions=db.execute('select count(*) from variant_decision').fetchone()[0]
    if actual_analyses!=source_count+candidate_count or actual_decisions!=2*actual_analyses:
        raise GeneratorError('Niezgodne pokrycie zapisanych analiz i wariantów; wymagany nowy build',4)
    return {'schema_version':1,'scope':'persisted_diagnostic_analyses_not_full_qualification',
            'policy_version':POLICY_VERSION,'source_analyses':source_count,'construction_analyses':candidate_count,
            'source_tag_expansions':tag_count,'documented_use_analyses':use_count,'remainder_analyses':remainder_count,
            'source_compact_interpretations':compact_count,
            'source_rows':db.execute('select count(*) from sgjp_record').fetchone()[0],
            'analyses':actual_analyses,'variant_decisions':actual_decisions,
            'new_analyses':new_analyses,'new_decisions':new_decisions,'full_qualification_pending':True}


def persisted_assessments(db, key, variant):
    """Odczyt dokładnych zapisanych powodów; zgodne ze starszymi bazami bez ocen."""
    import json
    import hashlib
    if variant not in VARIANTS:raise GeneratorError('Nieznany wariant słownika',2)
    if not db.execute("select 1 from sqlite_master where name='analysis'").fetchone():return []
    checked_persisted_use_coverage(db)
    rows=db.execute('''select a.analysis_key,a.interpretation_id,a.candidate_key,a.expanded_tag,
        a.original,a.nfc,a.game_key,a.length,a.policy_version,p.assessment_key,p.assessment
        from analysis a join variant_decision d on d.analysis_key=a.analysis_key
        join decision_payload p on p.assessment_key=d.assessment_key
        where a.game_key=? and d.variant=? order by a.analysis_key''',(key,variant))
    result=[]
    for akey,iid,ckey,tag,original,nfc,game_key,length,version,payload_key,payload in rows:
        if hashlib.sha256(payload.encode()).hexdigest()!=payload_key:
            raise GeneratorError('Zmieniona treść zapisanych powodów oceny',4)
        assessed=json.loads(payload)
        assessed['profile'].update(original=original,nfc=nfc,game_key=game_key,length=length)
        result.append({'analysis_key':akey,'interpretation_id':iid,'candidate_key':ckey,
                       'expanded_tag':tag,'original':original,'policy_version':version,
                       'variant':variant,'assessment':assessed,
                       **({'semantic_trace':assessed['semantic_trace']} if 'semantic_trace' in assessed else {})})
    return result


def assessment(checks):
    checks = list(checks)
    for check in checks:
        if (not isinstance(check, dict) or check.get('status') not in STATUSES
                or not check.get('rule_id') or not check.get('message')
                or not isinstance(check.get('evidence'), list)):
            raise GeneratorError('Nieprawidłowy wynik warunku kwalifikacji', 4)
    if not checks:
        checks = [{'rule_id': 'assessment-not-evaluated-v1', 'status': 'unresolved',
                   'message': 'Brak oceny wymaganych warunków.', 'evidence': []}]
    states = {c['status'] for c in checks}
    status = 'reject' if 'reject' in states else 'unresolved' if 'unresolved' in states else 'accept'
    return {'status': status, 'checks': checks}


def assess_analysis(original, *, language, game_checks, scope_checks=None):
    if set(language) != set(VARIANTS):
        raise GeneratorError('Wymagane odrębne oceny BROAD i STANDARD', 4)
    languages = {variant: assessment(language[variant]) for variant in VARIANTS}
    if languages['standard']['status'] == 'accept' and languages['broad']['status'] != 'accept':
        raise GeneratorError('STANDARD nie jest podzbiorem BROAD dla tej analizy', 4)
    # Pusta ocena growa jest unknown, nawet gdy sprawdzenie samej wielkości liter przechodzi.
    game = assessment(assessment(game_checks)['checks'] + spelling_checks(original))
    profile = assess_profile(original)
    scope = assessment(release_scope_checks() if scope_checks is None else scope_checks)
    membership = {variant: assessment(languages[variant]['checks'] + game['checks'] + profile['checks'] + scope['checks'])
                  for variant in VARIANTS}
    return {'original': original, 'game_key': profile['game_key'],
            'language': languages, 'game': game, 'profile': profile, 'release_scope':scope, 'membership': membership}


def aggregate(analyses, variant):
    if variant not in VARIANTS:
        raise GeneratorError('Nieznany wariant słownika', 2)
    if len({analysis['game_key'] for analysis in analyses}) > 1:
        raise GeneratorError('Nie można agregować analiz różnych kluczy słów', 4)
    statuses = {analysis['membership'][variant]['status'] for analysis in analyses}
    if statuses - STATUSES:
        raise GeneratorError('Nieprawidłowy status analizy', 4)
    status = ('absent' if not statuses else 'accept' if 'accept' in statuses else
              'unresolved' if 'unresolved' in statuses else 'reject')
    return {'status': status, 'variant': variant, 'analyses_count': len(analyses)}
