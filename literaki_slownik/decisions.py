"""Wszystkie warunki przy jednej analizie; agregacja dopiero po kwalifikacji."""
from .inputs import GeneratorError
from .policy import (assess_profile, spelling_checks, release_scope_checks,
                     approved_qualifier_checks, orthography_checks, construction_orthography_checks,
                     source_game_checks, VERSION as POLICY_VERSION)

STATUSES = frozenset({'accept', 'reject', 'unresolved'})
VARIANTS = ('broad', 'standard')


def assess_diagnostic(original, qualifiers, additional_checks=(), source_analyses=(), candidate=None):
    """Wspólna ocena explain i zapisu; nie aktywuje nierozstrzygniętej polityki."""
    pending=[{'rule_id':'linguistic-policy-not-active-v1','status':'unresolved',
              'message':'Pełna polityka językowa G3/G4 nie jest jeszcze aktywna.','evidence':[]}]
    game=[{'rule_id':'game-metadata-not-complete-v1','status':'unresolved',
           'message':'Pozostałe udokumentowane warunki growe wymagają domknięcia.','evidence':[]}]
    if candidate is not None:
        game+=source_game_checks(dict(raw_tag=candidate['expanded_tag'],names=candidate['names'],qualifiers=qualifiers),candidate=candidate)
    else:
        game+=[check for source in source_analyses for check in source_game_checks(source)]
    return assess_analysis(original,
        language={v:pending+approved_qualifier_checks(qualifiers,v)+list(additional_checks)
                  +[check for source in source_analyses for check in orthography_checks(source,v)]
                  +construction_orthography_checks(candidate,v) for v in VARIANTS},
        scope_checks=release_scope_checks(candidate),game_checks=game)


def materialize_assessments(db, batch_size=10000):
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
    for key,payload in db.execute('select assessment_key,assessment from decision_payload'):
        if hashlib.sha256(payload.encode()).hexdigest()!=key:
            raise GeneratorError('Zmieniona treść powodów oceny; wymagany nowy build',4)
    new_analyses=new_decisions=source_count=candidate_count=0
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
            encoded=dumps(payload);assessment_key=hashlib.sha256(encoded.encode()).hexdigest()
            payload_batch[assessment_key]=encoded
            values=(key,variant,*[payload[k]['status'] for k in ('language','game','profile','release_scope','membership')],assessment_key)
            old=db.execute('select * from variant_decision where analysis_key=? and variant=?',(key,variant)).fetchone() if existing else None
            if old is not None and old!=values:
                raise GeneratorError('Istniejąca ocena ma inną treść; wymagany nowy build',4)
            decision_batch.append(values)
        if len(analysis_batch)>=batch_size:flush()
    fields=('source_id','first_source_row','original','lemma_id','raw_tag','names','qualifiers')
    query='''select i.id,i.source_id,i.first_row,f.original,l.lemma_id,i.tag,i.names,i.qualifiers
        from interpretation i join surface_form f on f.id=i.form_id join lexeme l on l.id=i.lexeme_id
        order by i.source_id,i.first_row'''
    for row in db.execute(query):
        source=dict(zip(fields,row[1:]))
        # Każde źródłowe rozwinięcie pozostaje osobną spójną analizą.
        for tag in expand_tag(source['raw_tag']):
            key=hashlib.sha256(dumps(['source',source,tag]).encode()).hexdigest()
            assessed=assess_diagnostic(source['original'],source['qualifiers'],source_analyses=[dict(source,raw_tag=tag)])
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
            'analyses':actual_analyses,'variant_decisions':actual_decisions,
            'new_analyses':new_analyses,'new_decisions':new_decisions,'full_qualification_pending':True}


def persisted_assessments(db, key, variant):
    """Odczyt dokładnych zapisanych powodów; zgodne ze starszymi bazami bez ocen."""
    import json
    import hashlib
    if variant not in VARIANTS:raise GeneratorError('Nieznany wariant słownika',2)
    if not db.execute("select 1 from sqlite_master where name='analysis'").fetchone():return []
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
                       'variant':variant,'assessment':assessed})
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
