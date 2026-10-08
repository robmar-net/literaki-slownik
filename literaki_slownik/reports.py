"""Raporty podanych analiz; bez domniemania kompletności całego wydania."""
from collections import Counter
from functools import lru_cache
import hashlib
import json
import sqlite3

from .decisions import assessment, aggregate, VARIANTS
from .inputs import GeneratorError
from .canonical import dumps


def coverage_report(db):
    """Rozliczenie obserwowanych klas i ocen; inwentaryzacja nie jest odbiorem."""
    from .sgjp import tag_size
    from .policy import CONFIRMED_CONSTRUCTOR_RULES, CLASS_MATRIX
    source={}
    for tag,n in db.execute('select tag,count(*) from interpretation group by tag order by tag'):
        cls=tag.split(':',1)[0]
        item=source.setdefault(cls,{'compact_interpretations':0,
            'expanded_interpretations':0,'raw_tags':0,
            'semantic_qualification':'CLOSED' if cls in CLASS_MATRIX else 'UNKNOWN_CLASS',
            'matrix_behavior':CLASS_MATRIX.get(cls)})
        item['compact_interpretations']+=n
        item['expanded_interpretations']+=n*tag_size(tag)
        item['raw_tags']+=1
    tables={r[0] for r in db.execute("select name from sqlite_master where type='table'")}
    constructor_tables={'derivation_candidate','derivation_component'}
    assessment_tables={'analysis','variant_decision','decision_payload'}
    if tables&constructor_tables and not constructor_tables<=tables:
        raise GeneratorError('Niepełny schemat konstrukcji w raporcie pokrycia',4)
    if tables&assessment_tables and not assessment_tables<=tables:
        raise GeneratorError('Niepełny schemat ocen w raporcie pokrycia',4)
    actual=(dict(db.execute('select rule_id,count(*) from derivation_candidate group by rule_id'))
            if constructor_tables<=tables else {})
    constructors={rule:{'candidate_analyses':actual.get(rule,0),
        'coverage':'OBSERVED_NOT_VERIFIED' if actual.get(rule,0) else 'EMPTY_NOT_COVERAGE',
        'registered':rule in CONFIRMED_CONSTRUCTOR_RULES}
        for rule in sorted(set(actual)|CONFIRMED_CONSTRUCTOR_RULES)}
    stored=assessment_tables<=tables
    assessed=(unresolved_report(db) if stored else
              {'variants':{v:{'analyses':0,'semantic_analysis_kinds':{}} for v in VARIANTS}})
    expanded_total=sum(x['expanded_interpretations'] for x in source.values())
    source_assessment_coverage={}
    for variant,counts in assessed['variants'].items():
        kinds=counts['semantic_analysis_kinds']
        covered=kinds.get('source_expansion',0)+kinds.get('unresolved_remainder',0)
        if covered>expanded_total:
            raise GeneratorError('Więcej ocen źródła niż rozwinięć interpretacji',4,variant)
        source_assessment_coverage[variant]={
            'assessed_source_expansions':covered,
            'unassessed_source_expansions':expanded_total-covered,
            'coverage':'COMPLETE_TECHNICAL_NOT_QUALIFICATION' if covered==expanded_total
                       else 'PARTIAL_MISSING_ASSESSMENTS'}
    # Runda 3: zamknięta macierz klas; odbiór nadal wymaga verify (K1–K10).
    population_complete=(stored and bool(source) and all(x['semantic_qualification']=='CLOSED' for x in source.values())
        and all(x['coverage']=='COMPLETE_TECHNICAL_NOT_QUALIFICATION' for x in source_assessment_coverage.values())
        and not set(actual)-CONFIRMED_CONSTRUCTOR_RULES)
    unresolved=any(c[s]['unresolved'] for c in assessed['variants'].values() for s in ('analysis_membership','word_membership')) if stored else True
    complete=population_complete and not unresolved
    return {'schema_version':1,'status':'COMPLETE' if complete else 'INCOMPLETE',
        'scope':'closed_class_matrix_and_assessments' if complete else 'observed_class_inventory_not_semantic_closure',
        'full_qualification_pending':not complete,
        'assessment_storage':'PERSISTED_DIAGNOSTIC' if stored else 'LEGACY_IMPORT_NO_ASSESSMENTS',
        'source_rows':db.execute('select count(*) from sgjp_record').fetchone()[0],
        'source_compact_interpretations':sum(x['compact_interpretations'] for x in source.values()),
        'source_expanded_interpretations':sum(x['expanded_interpretations'] for x in source.values()),
        'source_classes':source,'constructor_classes':constructors,
        'unregistered_constructor_classes':sorted(set(actual)-CONFIRMED_CONSTRUCTOR_RULES),
        'assessments':assessed['variants'],
        'source_assessment_coverage':source_assessment_coverage,
        'source_semantic_population_complete':population_complete,
        'notice':'Dokumentowane użycia/pozostałość nie mnożą źródłowych rekordów. Liczebność klasy i dobór próby nie dowodzą jej pełnej kwalifikacji.'}


def canonical_index(run_dir):
    """Indeks I2 dla diagnostycznego przebiegu; nie zastępuje verify.

    Jawna lista plików zapobiega związaniu czasów, ścieżek i fizycznej bazy.
    Brakujące części pełnego pakietu pozostają widoczne, bez pustych list.
    """
    from pathlib import Path
    from .canonical import load_json, sha256
    root=Path(run_dir).resolve()
    manifest=load_json(root/'manifest.json')
    inputs=manifest['inputs']
    required=('lists/broad.txt','lists/standard.txt','reports/import-counts.json',
              'reports/inventory.json','reports/qualifier-conditions.json',
              'reports/construction-candidates.json','reports/decisions.json',
              'reports/unresolved.json','reports/links.json','reports/filter-impact.json',
              'reports/logical-content.json','reports/coverage.json')
    paths=list(required)
    if 'quality' in inputs['manifest']['configurations']:
        paths.extend(('reports/quality-analyses.json','reports/quality-links.json'))
    if 'quality-words' in inputs['manifest']['configurations']:
        paths.append('reports/quality-words.json')
    files,missing={},[]
    for relative in sorted(paths):
        target=root/relative
        if target.is_symlink() or not target.resolve().is_relative_to(root):
            raise GeneratorError('Plik indeksu poza przebiegiem lub dowiązanie',4,relative)
        if not target.exists():
            missing.append(relative)
        elif not target.is_file():
            raise GeneratorError('Pozycja indeksu nie jest plikiem',4,relative)
        else:
            files[relative]={'sha256':sha256(target),'bytes':target.stat().st_size}
    provenance={
        'mode':inputs['mode'],
        'sources':sorted([{'source_id':a['source_id'],'kind':a['kind'],'sha256':a['sha256'],
                           'evidence_sha256':sorted(e['sha256'] for e in a['evidence'])}
                          for a in inputs['artifacts']],key=lambda a:a['source_id']),
        'configurations':{name:value['sha256'] for name,value in sorted(
            inputs['manifest']['configurations'].items())},
    }
    return {'schema_version':1,'scope':'diagnostic_content_index_not_release_verification',
            'status':'INCOMPLETE' if missing else 'COMPLETE','files':files,'missing':missing,'provenance':provenance,
            'excluded':['manifest.json','reports/performance.json','build.sqlite',
                        'review','verification','logs','local_paths','timestamps']}


def unresolved_report(db):
    """Pełne liczniki zapisanych niewiadomych, także pod znanym odrzuceniem.

    Słowo agregujemy po spójnych analizach. Nie liczymy wspólnego payloadu
    jako pojedynczej analizy ani nie powielamy powodów z membership.
    Pamięć: ograniczony cache powodów i zbiór reguł jednego słowa.
    """
    from .decisions import checked_persisted_use_coverage
    checked_persisted_use_coverage(db)
    layers = ('language', 'game', 'profile', 'release_scope')
    statuses = ('accept', 'reject', 'unresolved')

    @lru_cache(maxsize=256)
    def checked_payload(key, text):
        if not isinstance(text, str):
            raise GeneratorError('Nieprawidłowy zapis powodów oceny', 4)
        if hashlib.sha256(text.encode()).hexdigest() != key:
            raise GeneratorError('Niezgodny hash powodów w raporcie niewiadomych', 4)
        value = json.loads(text)
        for layer in (*layers, 'membership'):
            if not isinstance(value[layer]['checks'], list) or not value[layer]['checks']:
                raise GeneratorError('Brak powodów wymaganej warstwy oceny', 4)
            if assessment(value[layer]['checks'])['status'] != value[layer]['status']:
                raise GeneratorError('Niespójne powody i status oceny', 4)
        combined = assessment(check for layer in layers for check in value[layer]['checks'])
        if combined['status'] != value['membership']['status']:
            raise GeneratorError('Niespójna kwalifikacja całej analizy', 4)
        return value

    variants = {v: {'analyses': 0, 'analysis_membership': dict.fromkeys(statuses, 0),
                    'word_keys': 0, 'word_membership': dict.fromkeys(statuses, 0),
                    'analyses_with_unresolved_checks': 0,
                    'rejected_analyses_with_unresolved_checks': 0,
                    'semantic_analysis_kinds':{}} for v in VARIANTS}
    rules = {}
    group = None
    group_states, group_rules = set(), set()

    def finish_group():
        if group is None:
            return
        variant = group[1]
        word_status = ('accept' if 'accept' in group_states else
                       'unresolved' if 'unresolved' in group_states else 'reject')
        variants[variant]['word_keys'] += 1
        variants[variant]['word_membership'][word_status] += 1
        for rule in group_rules:
            rules[rule]['word_keys'] += 1
            rules[rule]['word_keys_by_membership'][word_status] += 1

    try:
        expected = db.execute('select count(*) from analysis').fetchone()[0]
        decisions = db.execute('select count(*) from variant_decision').fetchone()[0]
        if decisions != expected * len(VARIANTS):
            raise GeneratorError('Niepełne pokrycie wariantów w raporcie niewiadomych', 4)
        has_candidate='candidate_key' in {r[1] for r in db.execute('pragma table_info(analysis)')}
        query = '''select a.game_key,d.variant,d.language_status,d.game_status,
            d.profile_status,d.scope_status,d.membership_status,p.assessment_key,p.assessment
            ,'''+('a.candidate_key' if has_candidate else 'null')+'''
            from analysis a join variant_decision d on d.analysis_key=a.analysis_key
            join decision_payload p on p.assessment_key=d.assessment_key
            order by a.game_key,d.variant,a.analysis_key'''
        processed = 0
        for key, variant, language, game, profile, scope, membership, payload_key, text, candidate_key in db.execute(query):
            if variant not in variants or membership not in statuses:
                raise GeneratorError('Nieznany wariant lub status zapisanej oceny', 4)
            value = checked_payload(payload_key, text)
            stored = (language, game, profile, scope, membership)
            if stored != tuple(value[layer]['status'] for layer in (*layers, 'membership')):
                raise GeneratorError('Statusy bazy różnią się od zapisanych powodów', 4)
            if group != (key, variant):
                finish_group()
                group = (key, variant)
                group_states, group_rules = set(), set()
            group_states.add(membership)
            total = variants[variant]
            total['analyses'] += 1
            kind=value.get('semantic_trace',{}).get('kind','construction' if candidate_key else 'source_expansion')
            if kind not in {'source_expansion','construction','documented_use','unresolved_remainder'}:
                raise GeneratorError('Nieznany rodzaj analizy semantycznej',4)
            total['semantic_analysis_kinds'][kind]=total['semantic_analysis_kinds'].get(kind,0)+1
            total['analysis_membership'][membership] += 1
            unknowns = {(variant, layer, check['rule_id']) for layer in layers
                        for check in value[layer]['checks'] if check['status'] == 'unresolved'}
            total['analyses_with_unresolved_checks'] += bool(unknowns)
            total['rejected_analyses_with_unresolved_checks'] += bool(unknowns) and membership == 'reject'
            for rule in unknowns:
                counts = rules.setdefault(rule, {'analyses': 0, 'word_keys': 0,
                                                'analyses_with_rejected_membership': 0,
                                                'word_keys_by_membership':dict.fromkeys(statuses,0)})
                counts['analyses'] += 1
                counts['analyses_with_rejected_membership'] += membership == 'reject'
            group_rules.update(unknowns)
            processed += 1
        finish_group()
        if processed != decisions or any(v['analyses'] != expected for v in variants.values()):
            raise GeneratorError('Brak analiz, powodów lub wariantów w raporcie niewiadomych', 4)
        return {'schema_version': 1, 'scope': 'all_persisted_assessments_not_full_release',
                'full_qualification_pending': any(c[s]['unresolved'] for c in variants.values() for s in ('analysis_membership','word_membership')), 'variants': variants,
                'rules': [{'variant': v, 'layer': layer, 'rule_id': rule, **counts}
                          for (v, layer, rule), counts in sorted(rules.items())]}
    except GeneratorError:
        raise
    except (sqlite3.Error, KeyError, TypeError, ValueError) as error:
        raise GeneratorError('Nie można odczytać pełnych ocen dla raportu niewiadomych', 4) from error


def logical_content_report(db):
    """Hash bieżących relacji z trwałymi kluczami zamiast technicznych ID.

    Zamknięty schemat nie pozwala pominąć nowej tabeli lub kolumny.
    Przyszłe utrwalone decyzje wymagają rozszerzenia tego kontraktu.
    """
    columns = {
        'source_artifact': 'source_id kind metadata',
        'sgjp_record': 'source_id row_number form lemma tag names qualifiers',
        'lexeme': 'id source_id lemma_id lemma_base',
        'surface_form': 'id original nfc game_key length',
        'interpretation': 'id source_id first_row form_id lexeme_id tag names qualifiers',
        'corpus_evidence': 'id source_id row_number unit_1 unit_2 pos raw_metrics typed_metrics freq',
        'derivation_candidate': 'candidate_key rule_id original game_key lemma_id expanded_tag names qualifiers payload',
        'derivation_component': 'candidate_key position kind source_id source_row',
        'evidence_link': 'evidence_id method status sense_identity_confirmed reason',
        'evidence_candidate': 'id evidence_id lexeme_id form_id candidate_key',
        'analysis': 'analysis_key interpretation_id candidate_key expanded_tag original nfc game_key length policy_version',
        'decision_payload': 'assessment_key assessment',
        'variant_decision': 'analysis_key variant language_status game_status profile_status scope_status membership_status assessment_key',
    }
    queries = {
        'source_artifact': ('select source_id,kind,metadata from source_artifact order by source_id', (2,)),
        'sgjp_record': ('select source_id,row_number,form,lemma,tag,names,qualifiers from sgjp_record order by source_id,row_number', ()),
        'lexeme': ('select source_id,lemma_id,lemma_base from lexeme order by source_id,lemma_id', ()),
        'surface_form': ('select original,nfc,game_key,length from surface_form order by original', ()),
        'interpretation': ('''select i.source_id,i.first_row,f.original,l.source_id,l.lemma_id,i.tag,i.names,i.qualifiers
            from interpretation i join surface_form f on f.id=i.form_id join lexeme l on l.id=i.lexeme_id
            order by i.source_id,i.first_row,f.original,l.source_id,l.lemma_id,i.tag,i.names,i.qualifiers''', ()),
        'corpus_evidence': ('''select source_id,row_number,unit_1,unit_2,pos,raw_metrics,typed_metrics,freq
            from corpus_evidence order by source_id,row_number''', (5,6)),
        'derivation_candidate': ('''select candidate_key,rule_id,original,game_key,lemma_id,expanded_tag,names,qualifiers,payload
            from derivation_candidate order by candidate_key''', (8,)),
        'derivation_component': ('''select candidate_key,position,kind,source_id,source_row
            from derivation_component order by candidate_key,position''', ()),
        'evidence_link': ('''select e.source_id,e.row_number,l.method,l.status,l.sense_identity_confirmed,l.reason
            from evidence_link l join corpus_evidence e on e.id=l.evidence_id order by e.source_id,e.row_number''', ()),
        'evidence_candidate': ('''select e.source_id,e.row_number,l.source_id,l.lemma_id,f.original,c.candidate_key
            from evidence_candidate c join corpus_evidence e on e.id=c.evidence_id
            left join lexeme l on l.id=c.lexeme_id left join surface_form f on f.id=c.form_id
            order by e.source_id,e.row_number,l.source_id,l.lemma_id,f.original,c.candidate_key''', ()),
        'analysis': ('''select a.analysis_key,i.source_id,i.first_row,a.candidate_key,a.expanded_tag,a.original,a.nfc,a.game_key,a.length,a.policy_version
            from analysis a left join interpretation i on i.id=a.interpretation_id order by a.analysis_key''',()),
        'decision_payload': ('select assessment_key,assessment from decision_payload order by assessment_key',(1,)),
        'variant_decision': ('''select analysis_key,variant,language_status,game_status,profile_status,scope_status,membership_status,assessment_key
            from variant_decision order by analysis_key,variant''',()),
    }
    try:
        tables = {row[0] for row in db.execute("select name from sqlite_master where type='table' and name not like 'sqlite_%'")}
        assessment_tables={'analysis','variant_decision','decision_payload'}
        required = set(columns) - {'evidence_link', 'evidence_candidate'} - assessment_tables
        if not required <= tables or tables - set(columns):
            raise GeneratorError('Nieznany lub niepełny schemat logical-content', 4)
        if ('evidence_link' in tables) != ('evidence_candidate' in tables):
            raise GeneratorError('Niepełny schemat powiązań logical-content', 4)
        if tables & assessment_tables and not assessment_tables<=tables:
            raise GeneratorError('Niepełny schemat ocen logical-content',4)
        for table in sorted(tables):
            actual = {row[1] for row in db.execute(f'pragma table_info({table})')}
            if actual != set(columns[table].split()):
                raise GeneratorError('Nieznane kolumny logical-content', 4, table)
        if db.execute('pragma foreign_key_check').fetchone() is not None:
            raise GeneratorError('Niespójne relacje logical-content', 4)
        results = {}
        for table in sorted(tables):
            query, json_columns = queries[table]
            digest, count = hashlib.sha256(), 0
            for source_row in db.execute(query):
                row = list(source_row)
                for index in json_columns:
                    row[index] = json.loads(row[index])
                if table == 'source_artifact':
                    # Wyłącznie lokalizatory i czas pozyskania: identyfikują operację,
                    # a nie treść źródła. SHA, URL, wersja, licencja i dowody zostają.
                    row[2] = {k:v for k,v in row[2].items() if k not in ('path','resolved_path','retrieved_at')}
                    row[2]['evidence'] = [{k:v for k,v in evidence.items() if k not in ('path','resolved_path')}
                                         for evidence in row[2].get('evidence', [])]
                digest.update((dumps(row)+'\n').encode('utf-8'))
                count += 1
            results[table] = {'rows':count, 'sha256':digest.hexdigest()}
        return {'schema_version':1, 'encoding':'logical-relations-v1/json-array-utf8-lf',
                'scope':'current_schema_imports_constructions_links_not_full_release',
                'excluded_source_metadata_fields':['path','resolved_path','retrieved_at','evidence[].path','evidence[].resolved_path'],
                'tables':results, 'sha256':hashlib.sha256(dumps(results).encode('utf-8')).hexdigest()}
    except GeneratorError:
        raise
    except (sqlite3.Error, ValueError, TypeError, AttributeError) as error:
        raise GeneratorError(f'Nie można policzyć logical-content: {error}', 4) from error


def filter_impact(groups, variant, rule_order):
    """Strumień uporządkowanych, unikalnych grup {key, analyses}.

    Reguła usuwa klucz dopiero, gdy odrzuca wszystkie jego analizy.
    Kolejne efekty nie dublują analiz/kluczy odrzuconych wcześniej.
    Reguły unresolved pozostają niewiadomymi, nie odrzuceniami.
    """
    if (variant not in VARIANTS or not isinstance(rule_order, list) or not rule_order
            or any(not isinstance(rule, str) or not rule for rule in rule_order)
            or len(set(rule_order)) != len(rule_order)):
        raise GeneratorError('Raport wymaga wariantu i jawnej unikalnej kolejności filtrów', 2)
    standalone = {rule: {'rejected_analyses': 0, 'rejected_keys': 0} for rule in rule_order}
    sequential = {rule: {'new_rejected_analyses': 0, 'new_rejected_keys': 0,
                         'cumulative_rejected_analyses': 0, 'cumulative_rejected_keys': 0}
                  for rule in rule_order}
    total = {'keys': 0, 'analyses': 0}
    combined = {'rejected_analyses': 0, 'rejected_keys': 0}
    statuses = Counter()
    previous = None
    try:
        for group in groups:
            key, analyses = group['key'], group['analyses']
            if (not isinstance(key, str) or not key or not isinstance(analyses, list) or not analyses
                    or previous is not None and key <= previous):
                raise GeneratorError('Raport wymaga uporządkowanych niepustych grup bez powtórzeń', 4)
            previous = key
            if any(item['game_key'] != key for item in analyses):
                raise GeneratorError('Analiza nie należy do klucza grupy', 4)
            rejected_by_rule = {rule: set() for rule in rule_order}
            for index, item in enumerate(analyses):
                decision = item['membership'][variant]
                checked = assessment(decision['checks'])
                if decision['status'] != checked['status']:
                    raise GeneratorError('Status analizy nie zgadza się z jej warunkami', 4)
                for check in checked['checks']:
                    if check['status'] != 'reject':
                        continue
                    rule = check['rule_id']
                    if rule not in rejected_by_rule:
                        raise GeneratorError('Lista filtrów pomija regułę odrzucającą', 4, rule)
                    rejected_by_rule[rule].add(index)
            total['keys'] += 1
            total['analyses'] += len(analyses)
            statuses[aggregate(analyses, variant)['status']] += 1
            cumulative = set()
            for rule in rule_order:
                rejected = rejected_by_rule[rule]
                standalone[rule]['rejected_analyses'] += len(rejected)
                standalone[rule]['rejected_keys'] += len(rejected) == len(analyses)
                before = len(cumulative)
                cumulative.update(rejected)
                sequential[rule]['new_rejected_analyses'] += len(cumulative) - before
                sequential[rule]['new_rejected_keys'] += before < len(analyses) and len(cumulative) == len(analyses)
                sequential[rule]['cumulative_rejected_analyses'] += len(cumulative)
                sequential[rule]['cumulative_rejected_keys'] += len(cumulative) == len(analyses)
            combined['rejected_analyses'] += len(cumulative)
            combined['rejected_keys'] += len(cumulative) == len(analyses)
    except GeneratorError:
        raise
    except (KeyError, TypeError, AttributeError) as error:
        raise GeneratorError(f'Nieprawidłowe analizy raportu: {error}', 4) from error
    return {
        'schema_version': 1, 'scope': 'provided_analyses_only_not_release_membership',
        'variant': variant, 'rule_order': list(rule_order),
        'coverage': 'ASSESSED_PROVIDED_ANALYSES_ONLY' if total['keys'] else 'EMPTY_NOT_COVERAGE',
        'total': total, 'standalone': dict(sorted(standalone.items())),
        'sequential': sequential, 'combined': combined, 'assessed_key_statuses': dict(sorted(statuses.items())),
    }


def persisted_filter_impact(db):
    """Wszystkie utrwalone oceny, jawna diagnostyczna kolejność ID reguł.

    Przed liczeniem wymagamy spójnego pokrycia obu wariantów i powodów.
    Kolejność nie jest pierwszeństwem reguł językowych; unknown nie odrzuca.
    Pamięć ograniczona do jednej grupy słowa i cache 256 powodów.
    """
    coverage = unresolved_report(db)
    @lru_cache(maxsize=256)
    def payload(encoded):
        value = json.loads(encoded)
        expected = Counter(dumps(c) for layer in ('language','game','profile','release_scope')
                           for c in value[layer]['checks'])
        if Counter(dumps(c) for c in value['membership']['checks']) != expected:
            raise GeneratorError('Powody członkostwa nie odpowiadają warstwom zapisanej analizy',4)
        return value
    variants = {}
    for variant in VARIANTS:
        rules = set()
        for encoded, in db.execute('''select distinct p.assessment from decision_payload p
                join variant_decision d on d.assessment_key=p.assessment_key where d.variant=?''', (variant,)):
            rules.update(c['rule_id'] for c in payload(encoded)['membership']['checks'])
        def groups():
            current, items = None, []
            for key, encoded in db.execute('''select a.game_key,p.assessment
                    from analysis a join variant_decision d on d.analysis_key=a.analysis_key
                    join decision_payload p on p.assessment_key=d.assessment_key
                    where d.variant=? order by a.game_key,a.analysis_key''', (variant,)):
                if current is not None and key != current:
                    yield {'key':current,'analyses':items}
                    items = []
                current = key
                items.append({'game_key':key,'membership':{variant:payload(encoded)['membership']}})
            if current is not None:
                yield {'key':current,'analyses':items}
        if rules:
            report = filter_impact(groups(), variant, sorted(rules))
        else:
            # Pusta populacja to brak pokrycia, bez wymyślonej reguły.
            report = {'schema_version':1,'variant':variant,'rule_order':[],
                      'coverage':'EMPTY_NOT_COVERAGE','total':{'keys':0,'analyses':0},
                      'standalone':{},'sequential':{},'combined':{'rejected_analyses':0,'rejected_keys':0},
                      'assessed_key_statuses':{}}
        expected = coverage['variants'][variant]
        if (report['total'] != {'keys':expected['word_keys'],'analyses':expected['analyses']}
                or report['combined']['rejected_analyses'] != expected['analysis_membership']['reject']
                or report['combined']['rejected_keys'] != expected['word_membership']['reject']):
            raise GeneratorError('Niezgodne pokrycie raportów zapisanych ocen',4)
        report['scope'] = 'all_persisted_assessments_not_full_release'
        report['semantic_analysis_kinds']=expected['semantic_analysis_kinds']
        variants[variant] = report
    return {'schema_version':1,'scope':'all_persisted_assessments_not_full_release',
            'full_qualification_pending':any(c[s]['unresolved'] for c in coverage['variants'].values() for s in ('analysis_membership','word_membership')),'order_basis':'lexicographic_rule_id_diagnostic_not_linguistic_priority',
            'variants':variants}


def qualifier_coverage(fields):
    """Inwentaryzacja warunków, nie kompletna semantyka etykiet lub analiz.

    Wejście: unikalne pary (surowe pole kwalifikatorów, liczba interpretacji).
    Liczniki etykiet mogą się nakładać; mianownik rekordów liczymy raz po polu.
    """
    from .policy import approved_qualifier_checks, VERSION, UNEXPLAINED_FIRST_RELEASE_LABELS, UNEXPLAINED_ACCENT_LABELS, _label_has_condition
    waived_labels = UNEXPLAINED_FIRST_RELEASE_LABELS | UNEXPLAINED_ACCENT_LABELS

    inventory, counts = {}, Counter()
    try:
        for field, count in fields:
            if (not isinstance(field, str) or type(count) is not int or count < 1
                    or field in inventory):
                raise GeneratorError('Pokrycie wymaga unikalnych pól i dodatnich liczników całkowitych', 4)
            inventory[field] = count
            for label in set(field.split('|')) - {''}:
                counts[label] += count
    except GeneratorError:
        raise
    except (TypeError, ValueError) as error:
        raise GeneratorError(f'Nieprawidłowa inwentaryzacja kwalifikatorów: {error}', 4) from error

    label_rows, mapped = [], set()
    for label, count in sorted(counts.items()):
        checks = {v: approved_qualifier_checks(label, v) for v in VARIANTS}
        conditions = {v: assessment(value) for v, value in checks.items()}
        has_condition = _label_has_condition(label)
        if has_condition:
            mapped.add(label)
        waived = label in waived_labels
        label_rows.append({'label': label, 'compact_interpretations': count,
                           'gloss_status': 'unestablished' if waived else 'not_assessed_by_this_report',
                           'first_release_gloss_requirement_waived': waived,
                           'has_known_condition': has_condition, 'condition_assessment': conditions})
    field_rows = []
    totals = {'compact_interpretations': sum(inventory.values()), 'fields': len(inventory),
              'literal_labels': len(counts), 'records_with_any_condition': 0,
              'records_with_unmapped_label': 0, 'records_without_qualifiers': 0,
              'records_with_unexplained_first_release_label': 0}
    for field, count in sorted(inventory.items()):
        labels = sorted(set(field.split('|')) - {''})
        unknown = sorted(set(labels) - mapped)
        unexplained = sorted(set(labels) & waived_labels)
        totals['records_with_unexplained_first_release_label'] += count if unexplained else 0
        totals['records_with_any_condition'] += count if set(labels) & mapped else 0
        totals['records_with_unmapped_label'] += count if unknown else 0
        totals['records_without_qualifiers'] += count if not labels else 0
        field_rows.append({'qualifiers': field, 'compact_interpretations': count, 'labels': labels,
                           'unmapped_labels': unknown,
                           'unexplained_first_release_labels': unexplained,
                           'condition_assessment': {v: assessment(approved_qualifier_checks(field, v))
                                                    for v in VARIANTS}})
    return {'schema_version': 1, 'policy_version': VERSION,
            'scope': 'qualifier_conditions_only_not_full_qualification',
            'coverage': 'OBSERVED_FIELDS' if inventory else 'EMPTY_NOT_COVERAGE',
            'full_qualification_pending': True, 'totals': totals,
            'label_counts_overlap': True, 'record_categories_overlap': True,
            'notice': 'Znany warunek nie oznacza pełnej semantyki etykiety ani dopuszczenia analizy. '
                      'Brak etykiety nie dowodzi poprawności; nie sumujemy nakładających się liczników.',
            'labels': label_rows, 'fields': field_rows,
            'unexplained_first_release_labels': sorted(set(counts) & waived_labels),
            'unmapped_labels': sorted(set(counts) - mapped)}


def construction_scope_report(db):
    """Analizy kandydatów poza zakresem nie są licznikiem błędnych słów."""
    from .policy import release_scope_checks
    counts = Counter()
    outside = Counter()
    for rule, original, n in db.execute('select rule_id,original,count(*) from derivation_candidate group by rule_id,original order by rule_id,original'):
        status = assessment(release_scope_checks(dict(rule_id=rule,original=original)))['status']
        counts[status] += n
        if status=='reject':
            outside[original] += n
    return {'schema_version':1,'scope':'candidate_release_scope_not_lexical_correctness_or_final_lists',
            'rule_id':'first-release-contraction-scope-v1',
            'in_scope_candidate_analyses':counts['accept'],
            'outside_scope_candidate_analyses':counts['reject'],
            'unresolved_scope_candidate_analyses':counts['unresolved'],
            'outside_scope_forms':[{'original':w,'candidate_analyses':n} for w,n in sorted(outside.items())]}
