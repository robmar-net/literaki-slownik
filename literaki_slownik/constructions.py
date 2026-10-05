"""Potwierdzone konstrukcje źródłowe; kandydat nie jest dopuszczeniem do gry."""
import unicodedata

from .inputs import GeneratorError
from .sgjp import expand_tag

VOWELS = frozenset('aąeęioóuy')
IMPT_PARTICLE_RULE = 'impt-single-particle-v1'
IMPT_DOUBLE_PARTICLE_RULE = 'impt-double-particle-v1'
SOURCE_FIELDS = ('source_id', 'first_source_row', 'original', 'lemma_id', 'raw_tag', 'names', 'qualifiers')
BY_AGLT_ENDINGS = {('sg', 'pri'): 'm', ('sg', 'sec'): 'ś', ('pl', 'pri'): 'śmy', ('pl', 'sec'): 'ście'}
PREPOSITION_N_UNVARIED = frozenset('na do dla koło o po poza spoza za zza'.split())
PREPOSITION_N_WOK = frozenset('beze nade ode pode ponade popode poprzeze przede przeze spode sponade spopode sprzede we ze znade'.split())
# Dosłowna enumeracja §9.1 SGJP, zatwierdzona jako dowód językowy (A).
PREPOSITION_N_DOCUMENTED = frozenset('bezeń dlań doń nadeń nań odeń oń podeń poń przedeń przezeń spodeń spozań sprzedeń weń zań zeń znadeń'.split())
MOBILE_BY_HOSTS = {**dict.fromkeys('aby choćby chociażby iżby gdyby jakby jakoby żeby ażeby jeżeliby jeśliby byleby kieby'.split(), 'comp'),
                   **dict.fromkeys('oby bodajby czyżby'.split(), 'part')}

# Zamknięte definicje z_aglt/z_aglt_nwok/z_aglt_nwok2; nie reguła sufiksu.
MOBILE_AGLT_HOSTS = {('albo', 'part'): 'nwok',
 ('alboż', 'part'): 'wok',
 ('ale', 'conj'): 'nwok',
 ('ale', 'part'): 'nwok',
 ('ależ', 'part'): 'wok',
 ('aniżeli', 'conj'): 'nwok',
 ('azali', 'part'): 'nwok',
 ('azaliż', 'part'): 'wok',
 ('bo', 'comp'): 'nwok',
 ('bowiem', 'comp'): 'wok',
 ('byle', 'comp'): 'nwok',
 ('chyba', 'part'): 'nwok',
 ('co', 'comp'): 'nwok',
 ('co', 'subst:%'): 'nwok',
 ('czemu', 'adv'): 'nwok',
 ('czy', 'part'): 'nwok',
 ('czyli', 'part'): 'nwok',
 ('czyliż', 'part'): 'wok',
 ('czyż', 'part'): 'wok',
 ('cóż', 'subst:%'): 'wok',
 ('dlaczego', 'adv'): 'nwok',
 ('dopóki', 'comp'): 'nwok',
 ('dopóty', 'conj'): 'nwok',
 ('gdy', 'adv'): 'nwok',
 ('gdzie', 'adv'): 'nwok',
 ('gdzie', 'part'): 'nwok',
 ('gdzież', 'adv'): 'wok',
 ('iż', 'comp'): 'wok',
 ('jakżeż', 'part'): 'wok',
 ('jeszcze', 'part'): 'nwok',
 ('jeśli', 'comp'): 'nwok',
 ('jeżeli', 'comp'): 'nwok',
 ('już', 'part'): 'wok',
 ('kiedy', 'adv'): 'nwok',
 ('kiedy', 'comp'): 'nwok',
 ('kto', 'subst:%'): 'nwok',
 ('któż', 'subst:%'): 'wok',
 ('ledwie', 'comp'): 'nwok',
 ('niźli', 'conj'): 'nwok',
 ('niż', 'conj'): 'wok',
 ('niżeli', 'conj'): 'nwok',
 ('póki', 'comp'): 'nwok',
 ('skoro', 'comp'): 'nwok',
 ('skąd', 'adv'): 'wok',
 ('tak', 'adv:%'): 'wok',
 ('to', 'comp'): 'nwok',
 ('tylko', 'part'): 'nwok',
 ('wcale', 'adv'): 'nwok',
 ('zaledwie', 'comp'): 'nwok',
 ('zali', 'part'): 'nwok',
 ('zaliż', 'part'): 'wok',
 ('że', 'comp'): 'nwok',
 ('że', 'part'): 'nwok'}

MOBILE_BY_SEQUENCE_HOSTS = frozenset([('albo', 'part'),
 ('alboż', 'part'),
 ('ale', 'conj'),
 ('ale', 'part'),
 ('ależ', 'part'),
 ('aniżeli', 'conj'),
 ('azali', 'part'),
 ('azaliż', 'part'),
 ('bo', 'comp'),
 ('bowiem', 'comp'),
 ('byle', 'comp'),
 ('chyba', 'part'),
 ('co', 'comp'),
 ('czemu', 'adv'),
 ('czy', 'part'),
 ('czyli', 'part'),
 ('czyliż', 'part'),
 ('czyż', 'part'),
 ('cóż', 'subst:%'),
 ('dlaczego', 'adv'),
 ('dopóki', 'comp'),
 ('dopóty', 'conj'),
 ('gdzie', 'adv'),
 ('gdzie', 'part'),
 ('gdzież', 'adv'),
 ('iż', 'comp'),
 ('jakżeż', 'part'),
 ('jeszcze', 'part'),
 ('jeśli', 'comp'),
 ('jeżeli', 'comp'),
 ('już', 'part'),
 ('kiedy', 'adv'),
 ('kiedy', 'comp'),
 ('któż', 'subst:%'),
 ('ledwie', 'comp'),
 ('niźli', 'conj'),
 ('niż', 'conj'),
 ('niżeli', 'conj'),
 ('póki', 'comp'),
 ('skoro', 'comp'),
 ('skąd', 'adv'),
 ('tak', 'adv:%'),
 ('to', 'comp'),
 ('tylko', 'part'),
 ('zaledwie', 'comp'),
 ('zali', 'part'),
 ('zaliż', 'part')])


def _validate_source(source):
    if (not isinstance(source, dict) or any(field not in source for field in SOURCE_FIELDS)
            or any(not isinstance(source[field], str) for field in SOURCE_FIELDS if field != 'first_source_row')
            or any(not source[field] for field in ('source_id', 'original', 'lemma_id', 'raw_tag'))
            or type(source['first_source_row']) is not int or source['first_source_row'] < 1):
        raise GeneratorError('Konstrukcja wymaga pełnej interpretacji źródłowej', 4)


def impt_particle_candidates(source):
    """Dodaj jedną partykułę do udokumentowanego rozkaźnika.

    Każdy wynik zachowuje konkretną źródłową analizę i odziedziczone etykiety.
    Kwalifikacja całej analizy i profilu następuje w osobnym etapie.
    Niezgodność klasy lub zakończenia jest luką pokrycia, nie cichym pominięciem.
    """
    _validate_source(source)
    if source['raw_tag'].split(':', 1)[0] != 'impt':
        return []
    original = source['original']
    ending = unicodedata.normalize('NFC', original)[-1].lower()
    results = []
    for tag in expand_tag(source['raw_tag']):
        fields = tag.split(':')
        if (len(fields) != 4 or fields[3] not in {'perf', 'imperf'}
                or (fields[1], fields[2]) not in {('sg', 'sec'), ('pl', 'pri'), ('pl', 'sec')}):
            raise GeneratorError('Niepokryta klasa rozkaźnika', 4, source['source_id'], source['first_source_row'])
        singular = fields[1] == 'sg'
        if singular == (ending in VOWELS) or not ending.isalpha():
            raise GeneratorError('Zakończenie rozkaźnika niezgodne z potwierdzoną macierzą', 4,
                                 source['source_id'], source['first_source_row'])
        particle = 'że' if singular else 'ż'
        results.append({
            'rule_id': IMPT_PARTICLE_RULE, 'status': 'candidate_not_qualified',
            'original': original + particle, 'lemma_id': source['lemma_id'], 'expanded_tag': tag,
            'names': source['names'], 'qualifiers': source['qualifiers'],
            'components': [
                {'kind': 'source_interpretation', 'interpretation': dict(source)},
                {'kind': 'grammatical_particle', 'original': particle, 'rule_id': IMPT_PARTICLE_RULE},
            ],
            'evidence': ['docs/generator/konstrukcje.md', 'config/generator/constructions.json'],
        })
    return results


def impt_double_particle_candidates(source):
    """Źródłowa reguła sg + że + ż; bez rekursywnego mnożenia partykuł."""
    results=[]
    for single in impt_particle_candidates(source):
        if not single['expanded_tag'].startswith('impt:sg:sec:'):
            continue
        results.append({**single,'rule_id':IMPT_DOUBLE_PARTICLE_RULE,
                        'original':single['original']+'ż',
                        'components':[single['components'][0]]+[
                            {'kind':'grammatical_particle','original':particle,'rule_id':IMPT_DOUBLE_PARTICLE_RULE}
                            for particle in ('że','ż')],
                        'linguistic_evidence':{
                            'rule_id':'impt-double-particle-source-proof-v1','status':'accept',
                            'message':'Zamknięta źródłowa reguła impt_sg ze z? potwierdza całość; growe wyłączenie oceniane osobno.',
                            'evidence':['config/generator/constructions.json','morfeusz_segments:334-340']}})
    return results


def by_aglt_candidates(operator, aglt):
    """Wyłącznie źródłowe by + cztery niewokaliczne aglutynanty."""
    _validate_source(operator)
    _validate_source(aglt)
    if operator['original'] != 'by' or operator['raw_tag'] not in {'comp', 'part'}:
        return []
    return _attach_aglt(operator, aglt, 'by-aglt-nwok-v1')


def mobile_by_aglt_candidates(host, aglt):
    """Źródłowa klasa z_aglt_by; bez odczytywania końcowych liter hosta."""
    _validate_source(host)
    _validate_source(aglt)
    lemma = host['lemma_id'].split(':', 1)[0]
    if (host['source_id'] != aglt['source_id'] or lemma not in MOBILE_BY_HOSTS
            or host['original'] != lemma or host['raw_tag'] != MOBILE_BY_HOSTS[lemma]):
        return []
    return _attach_aglt(host, aglt, 'mobile-by-host-aglt-v1')


def mobile_aglt_candidates(host, aglt):
    """Źródłowy host i właściwa wokaliczność, bez permissive ani swobodnego by."""
    _validate_source(host)
    _validate_source(aglt)
    if host['source_id'] != aglt['source_id']:
        return []
    lemma = host['lemma_id'].split(':',1)[0]
    variant = MOBILE_AGLT_HOSTS.get((lemma,host['raw_tag']))
    if variant is None:
        for pattern in ('subst:%','adv:%'):
            if host['raw_tag'].startswith(pattern[:-1]):
                variant = MOBILE_AGLT_HOSTS.get((lemma,pattern))
    if variant is None or (not host['raw_tag'].startswith('subst:') and host['original'] != lemma):
        return []
    vowel = unicodedata.normalize('NFC',host['original'])[-1].lower() in VOWELS
    form_variant = 'nwok' if vowel else 'wok'
    # Odmienny host ma źródłowe uprawnienie przez subst:%; wariant dla
    # konkretnej formy określa teoria SGJP §6.4.1, nie gruboziarnista klasa.
    inflected = (lemma,'subst:%') in MOBILE_AGLT_HOSTS and host['raw_tag'].startswith('subst:')
    actual_variant = form_variant if inflected else variant
    if form_variant != actual_variant or not aglt['raw_tag'].endswith(':'+actual_variant):
        return []
    results = _attach_aglt(host,aglt,'mobile-source-host-aglt-v1',actual_variant)
    if actual_variant != variant:
        for candidate in results:
            candidate['host_variant_evidence'] = {
                'source_class_variant':variant,'form_variant':actual_variant,
                'rule_id':'mobile-inflected-host-vocality-v1',
                'evidence':['https://sgjp.pl/static/pdf/Podstawy_teoretyczne_SGJP.pdf#page=93'],
                'message':'Źródłowy zamknięty host odmienny; wariant końcówki według zakończenia rzeczywistej formy (SGJP §6.4.1).'}
    return results


def mobile_by_sequence_candidates(host, operator, aglt=None):
    """Zamknięte z_aglt/z_aglt_nwok + źródłowe partykułowe by, opcjonalnie nwok."""
    for item in (host,operator) if aglt is None else (host,operator,aglt):
        _validate_source(item)
        if item['source_id'] != host['source_id']:
            return []
    lemma=host['lemma_id'].split(':',1)[0]
    matched = ((lemma,host['raw_tag']) in MOBILE_BY_SEQUENCE_HOSTS
               or any((lemma,p) in MOBILE_BY_SEQUENCE_HOSTS and host['raw_tag'].startswith(p[:-1])
                      for p in ('subst:%','adv:%')))
    if (not matched or (not host['raw_tag'].startswith('subst:') and host['original']!=lemma)
            or operator['original']!='by' or operator['raw_tag']!='part'):
        return []
    tags=[operator['raw_tag']]
    if aglt is not None:
        if not aglt['raw_tag'].startswith('aglt:'):
            return []
        tags=[]
        for tag in expand_tag(aglt['raw_tag']):
            fields=tag.split(':')
            if (len(fields)!=5 or fields[3:]!=['imperf','nwok']
                    or (fields[1],fields[2]) not in BY_AGLT_ENDINGS
                    or BY_AGLT_ENDINGS[(fields[1],fields[2])]!=aglt['original']):
                continue
            tags.append(tag)
    items=(host,operator) if aglt is None else (host,operator,aglt)
    inherited={field:'|'.join(sorted({label for item in items for label in item[field].split('|') if label}))
               for field in ('names','qualifiers')}
    return [{'rule_id':'mobile-host-by-sequence-v1','status':'candidate_not_qualified',
             'original':host['original']+'by'+(aglt['original'] if aglt is not None else ''),
             'lemma_id':host['lemma_id'],'expanded_tag':tag,**inherited,
             'components':[{'kind':'source_interpretation','interpretation':dict(item)} for item in items],
             'evidence':['docs/generator/konstrukcje.md','config/generator/constructions.json']}
            for tag in tags]


def personal_aglt_candidates(host, aglt):
    """Zamknięte klasy ja/ty/my/wy/wszyscy z segmenty.dat, bez permissive."""
    _validate_source(host)
    _validate_source(aglt)
    if host['source_id'] != aglt['source_id']:
        return []
    lemma = host['lemma_id'].split(':',1)[0]
    personal = {'ja':('sg','pri'), 'ty':('sg','sec'), 'my':('pl','pri'), 'wy':('pl','sec')}
    allowed = set()
    if lemma in personal and host['original']==lemma:
        number,person = personal[lemma]
        if host['raw_tag'].startswith(f'ppron12:{number}:nom:'):
            allowed.add((number,person))
    # Komentarz mówi o rzeczowniku PT, ale definicja klasy wskazuje
    # wszystek/adj:%. Zachowujemy formalną definicję, nie rozszerzamy subst.
    elif lemma=='wszystek' and host['original']=='wszyscy' and host['raw_tag'].startswith('adj:'):
        allowed = {('pl','pri'),('pl','sec')}
    tags = expand_tag(aglt['raw_tag'])
    if not allowed or not all(len(t.split(':'))==5 and t.split(':')[0]=='aglt'
            and tuple(t.split(':')[1:3]) in allowed and t.split(':')[3:]==['imperf','nwok'] for t in tags):
        return []
    return _attach_aglt(host,aglt,'personal-host-aglt-v1')


def _attach_aglt(operator, aglt, rule_id, variant="nwok"):
    if aglt['raw_tag'].split(':', 1)[0] != 'aglt':
        return []
    results = []
    for tag in expand_tag(aglt['raw_tag']):
        fields = tag.split(':')
        if (len(fields) != 5 or (fields[1],fields[2]) not in BY_AGLT_ENDINGS
                or fields[3:] != ['imperf', variant]
                or (('e' if variant=='wok' else '') + BY_AGLT_ENDINGS.get((fields[1], fields[2]),'')) != aglt['original']):
            raise GeneratorError('Niepokryta forma aglt; wymagany wariant źródłowej klasy', 4,
                                 aglt['source_id'], aglt['first_source_row'])
        inherited = {field: '|'.join(sorted({label for item in (operator, aglt)
                                            for label in item[field].split('|') if label}))
                     for field in ('names', 'qualifiers')}
        results.append({
            'rule_id': rule_id, 'status': 'candidate_not_qualified',
            'original': operator['original'] + aglt['original'], 'lemma_id': operator['lemma_id'],
            'expanded_tag': tag, **inherited,
            'components': [{'kind': 'source_interpretation', 'interpretation': dict(item)}
                           for item in (operator, aglt)],
            'evidence': ['docs/generator/konstrukcje.md', 'config/generator/constructions.json'],
        })
    return results


def preposition_n_candidates(preposition, pronoun):
    """Kontrolowana kontrakcja; dowód całego napisu oceniany oddzielnie.

    Nie ma ogólnej reguły doklejania ń ani zgadywania wariantu wokalicznego.
    Osiem niewymienionych napisów zachowuje nierozstrzygnięty dowód językowy.
    """
    _validate_source(preposition)
    _validate_source(pronoun)
    if (preposition['source_id'] != pronoun['source_id'] or pronoun['original'] != 'ń'
            or pronoun['lemma_id'].split(':', 1)[0] != 'on'):
        return []
    form = preposition['original']
    results = []
    for prep_tag in expand_tag(preposition['raw_tag']):
        prep = prep_tag.split(':')
        if (len(prep) not in {2, 3} or prep[0] != 'prep' or prep[1] not in {'gen', 'acc'}
                or not ((len(prep) == 2 and form in PREPOSITION_N_UNVARIED)
                        or (len(prep) == 3 and prep[2] == 'wok' and form in PREPOSITION_N_WOK))):
            continue
        for tag in expand_tag(pronoun['raw_tag']):
            fields = tag.split(':')
            if (len(fields) != 7 or fields[:3] != ['ppron3', 'sg', prep[1]]
                    or fields[3] not in {'m1', 'm2', 'm3'} or fields[4:] != ['ter', 'nakc', 'praep']):
                continue
            original = form + 'ń'
            proved = original in PREPOSITION_N_DOCUMENTED
            inherited = {field: '|'.join(sorted({label for item in (preposition, pronoun)
                                                for label in item[field].split('|') if label}))
                         for field in ('names', 'qualifiers')}
            results.append({
                'rule_id': 'preposition-n-source-v1', 'status': 'candidate_not_qualified',
                'original': original, 'lemma_id': pronoun['lemma_id'], 'expanded_tag': tag,
                'preposition_expanded_tag': prep_tag, **inherited,
                'components': [{'kind': 'source_interpretation', 'interpretation': dict(item)}
                               for item in (preposition, pronoun)],
                'linguistic_evidence': {
                    'rule_id': 'preposition-n-whole-form-proof-v1',
                    'status': 'accept' if proved else 'unresolved',
                    'message': 'Cała forma dosłownie wskazana w §9.1 SGJP; inne warunki oceniane osobno.'
                               if proved else 'Cała forma poza enumeracją §9.1 SGJP; dowód nadal wymagany.',
                    'evidence': ['config/generator/constructions.json',
                                 'https://sgjp.pl/static/pdf/Podstawy_teoretyczne_SGJP.pdf'],
                },
                'fulfilled_component_requirements': ['pisane_łącznie_z_przyimkiem'],
                'evidence': ['docs/generator/konstrukcje.md', 'config/generator/constructions.json'],
            })
    return results



SPELLING_VARIANT_RULE = 'documented-spelling-variant-v1'
SPELLING_SOURCE_SHA = '3b2ee079143bc95186370fd528735779c4ba62f4ce14e30cf6622ceb566e9810'
SPELLING_DOCUMENT_SHA = '87daaddd86911370d4df3c1e5769028e8fa9087e052c8954b70ec173ada2d72e'


def spelling_variant_candidates(source):
    """Dwa literalne przykłady normy, dokładny rekord; żadnej reguły lower."""
    _validate_source(source)
    identities = {('Angol','Angol',9040,'pot.,etn.'):'angol',
                  ('Jugol','Jugol',358226,''):'jugol'}
    target=identities.get((source['original'],source['lemma_id'],source['first_source_row'],source['qualifiers']))
    if (target is None or source['source_id']!='sgjp-20260823'
            or source.get('source_sha256')!=SPELLING_SOURCE_SHA
            or source['raw_tag']!='subst:sg:nom:m1' or source['names']!='nazwa_pospolita'):
        return []
    trace={'source_original':source['original'],'target_original':target,
        'use_id':'rjp-informal-ethnic-'+target+'-v1','coverage':'documented_use_only',
        'document_sha256':SPELLING_DOCUMENT_SHA,'norm_effective_from':'2026-01-01',
        'locator':'https://rjp.pan.pl/app/uploads/2025/11/2-zalacznik-do-komunikatu-11-25-wersja-jednolita.pdf#page=43; §8.1.2 pkt4 uwaga'}
    return [{'rule_id':SPELLING_VARIANT_RULE,'status':'candidate_not_qualified',
        'original':target,'lemma_id':source['lemma_id'],'expanded_tag':source['raw_tag'],
        'names':source['names'],'qualifiers':source['qualifiers'],
        'components':[{'kind':'source_interpretation','interpretation':dict(source)}],
        'orthographic_variant':trace,
        'linguistic_evidence':{'rule_id':'orthography-attested-lowercase-2026-v1','status':'accept',
            'message':'Jawny przykład normy2026 potwierdza mały zapis tego użycia; inne warunki językowe i growe osobno.',
            'evidence':[trace['locator'],'config/generator/orthography.json']},
        'evidence':['config/generator/orthography.json',trace['locator']]}]


def checked_spelling_variants(db):
    """Przed oceną sprawdź źródło, payload i rzeczywiste relacje składników."""
    import json
    import hashlib
    from .canonical import dumps
    if not db.execute("select 1 from sqlite_master where name='derivation_candidate'").fetchone():return
    for row in db.execute('select * from derivation_candidate where rule_id=?',(SPELLING_VARIANT_RULE,)):
        try:
            value=json.loads(row[8]);parts=value['components']
            if len(parts)!=1 or parts[0]['kind']!='source_interpretation':
                raise ValueError('składnik')
            ref=parts[0]['interpretation']
            raw=db.execute("""select i.source_id,i.first_row,f.original,l.lemma_id,i.tag,i.names,i.qualifiers,s.metadata
                from interpretation i join surface_form f on f.id=i.form_id
                join lexeme l on l.id=i.lexeme_id join source_artifact s on s.source_id=i.source_id
                where i.source_id=? and i.first_row=? and f.original=? and l.lemma_id=?""",
                (ref['source_id'],ref['first_source_row'],ref['original'],ref['lemma_id'])).fetchone()
            if raw is None:raise ValueError('źródło')
            source=dict(zip(SOURCE_FIELDS,raw[:7]));source['source_sha256']=json.loads(raw[7]).get('sha256')
            candidates=spelling_variant_candidates(source)
            if len(candidates)!=1 or value!=candidates[0]:raise ValueError('dowód/mapowanie')
            c=candidates[0];encoded=dumps(c);key=hashlib.sha256(encoded.encode()).hexdigest()
            expected=(key,c['rule_id'],c['original'],c['original'],c['lemma_id'],c['expanded_tag'],c['names'],c['qualifiers'],encoded)
            if row!=expected:raise ValueError('klucz/pola')
            components=db.execute('select position,kind,source_id,source_row from derivation_component where candidate_key=? order by position',(key,)).fetchall()
            if components!=[(0,'source_interpretation',source['source_id'],source['first_source_row'])]:
                raise ValueError('relacje składników')
        except (KeyError,ValueError,TypeError,AttributeError) as error:
            raise GeneratorError('Niespójny kandydat udokumentowanej pisowni; wymagany nowy build',4) from error

def materialize_confirmed_candidates(db, batch_size=10000):
    """Zapisz potwierdzony podzbiór bez dopuszczenia lub pełnego statusu etapu.

    Kandydat i jego składniki zapisują się razem; porcje mogą pozostać po awarii.
    Klucz treści zachowuje alternatywne ślady, także dla istniejącego napisu.
    """
    import hashlib
    from .canonical import dumps

    if type(batch_size) is not int or not 1 <= batch_size <= 10000:
        raise GeneratorError('Porcja konstrukcji musi mieć od 1 do 10 000 kandydatów', 2)
    select = '''select i.source_id,i.first_row,f.original,l.lemma_id,i.tag,i.names,i.qualifiers
        from interpretation i join surface_form f on f.id=i.form_id join lexeme l on l.id=i.lexeme_id'''
    new_count, pending, source_count = 0, 0, 0

    def save(candidate):
        nonlocal new_count, pending
        payload = dumps(candidate)
        key = hashlib.sha256(payload.encode('utf-8')).hexdigest()
        nfc = unicodedata.normalize('NFC', candidate['original'])
        game_key = unicodedata.normalize('NFC', nfc.lower())
        inserted = db.execute('''insert or ignore into derivation_candidate
            (candidate_key,rule_id,original,game_key,lemma_id,expanded_tag,names,qualifiers,payload)
            values (?,?,?,?,?,?,?,?,?)''',
            (key, candidate['rule_id'], candidate['original'], game_key, candidate['lemma_id'],
             candidate['expanded_tag'], candidate['names'], candidate['qualifiers'], payload)).rowcount
        new_count += inserted
        for position, component in enumerate(candidate['components']):
            source = component.get('interpretation')
            db.execute('''insert or ignore into derivation_component
                (candidate_key,position,kind,source_id,source_row) values (?,?,?,?,?)''',
                (key, position, component['kind'], source['source_id'] if source else None,
                 source['first_source_row'] if source else None))
        pending += 1
        if pending >= batch_size:
            db.commit()
            pending = 0

    for row in db.execute(select + " where i.tag like 'impt:%' order by i.source_id,i.first_row"):
        source_count += 1
        source=dict(zip(SOURCE_FIELDS,row))
        for candidate in impt_particle_candidates(source)+impt_double_particle_candidates(source):
            save(candidate)
    operators = [dict(zip(SOURCE_FIELDS,row)) for row in db.execute(
        select + " where f.original='by' and i.tag in ('part','comp') order by i.source_id,i.first_row")]
    endings = [dict(zip(SOURCE_FIELDS,row)) for row in db.execute(
        select + " where i.tag like 'aglt:%:nwok' order by i.source_id,i.first_row")]
    for operator in operators:
        for ending in endings:
            if operator['source_id'] == ending['source_id']:
                for candidate in by_aglt_candidates(operator, ending):
                    save(candidate)
    mobile_hosts = [dict(zip(SOURCE_FIELDS,row)) for row in db.execute(
        select + " where i.tag in ('comp','part') order by i.source_id,i.first_row")]
    for host in mobile_hosts:
        for ending in endings:
            for candidate in mobile_by_aglt_candidates(host, ending):
                save(candidate)
    all_endings = [dict(zip(SOURCE_FIELDS,row)) for row in db.execute(
        select + " where i.tag like 'aglt:%' order by i.source_id,i.first_row")]
    lemmas = sorted({key[0] for key in MOBILE_AGLT_HOSTS} | {'ja','ty','my','wy','wszystek'})
    placeholders = ','.join('?' for _ in lemmas)
    source_hosts = [dict(zip(SOURCE_FIELDS,row)) for row in db.execute(
        select + f" where l.lemma_base in ({placeholders}) order by i.source_id,i.first_row",lemmas)]
    for host in source_hosts:
        for ending in all_endings:
            for candidate in mobile_aglt_candidates(host,ending):
                save(candidate)
            for candidate in personal_aglt_candidates(host,ending):
                save(candidate)
    for host in source_hosts:
        for operator in operators:
            for ending in [None]+endings:
                for candidate in mobile_by_sequence_candidates(host,operator,ending):
                    save(candidate)
    prepositions = [dict(zip(SOURCE_FIELDS,row)) for row in db.execute(
        select + " where i.tag like 'prep:%' order by i.source_id,i.first_row")]
    pronouns = [dict(zip(SOURCE_FIELDS,row)) for row in db.execute(
        select + " where f.original='ń' and i.tag like 'ppron3:%' order by i.source_id,i.first_row")]
    for preposition in prepositions:
        for pronoun in pronouns:
            for candidate in preposition_n_candidates(preposition, pronoun):
                save(candidate)
    import json
    hashes={sid:json.loads(metadata).get('sha256') for sid,metadata in db.execute('select source_id,metadata from source_artifact')}
    for row in db.execute(select + " where l.source_id='sgjp-20260823' and l.lemma_id in ('Angol','Jugol') order by i.source_id,i.first_row"):
        source=dict(zip(SOURCE_FIELDS,row));source['source_sha256']=hashes[source['source_id']]
        for candidate in spelling_variant_candidates(source):save(candidate)
    db.commit()
    checked_spelling_variants(db)
    by_rule = dict(db.execute('select rule_id,count(*) from derivation_candidate group by rule_id order by rule_id'))
    from .reports import construction_scope_report
    return {'schema_version': 1, 'release_scope':construction_scope_report(db),
            'scope': 'confirmed_subset_candidates_not_full_constructions',
            'full_constructions_pending': True, 'impt_source_interpretations': source_count,
            'operator_source_interpretations': len(operators), 'aglt_source_interpretations': len(endings),
            'new_candidates': new_count, 'candidates': sum(by_rule.values()), 'by_rule': by_rule,
            'components': db.execute('select count(*) from derivation_component').fetchone()[0],
            'notice': 'Kandydaci zachowują ślady; nie są decyzjami językowymi ani dopuszczeniem do gry. '
                      'Brak pełnej macierzy nadal blokuje ukończenie etapu konstrukcji.'}
