"""Potwierdzone warunki i profil; pełna polityka językowa nadal nieukończona."""
import unicodedata
from .inputs import GeneratorError

ALPHABET = 'aąbcćdeęfghijklłmnńoóprsśtuwyzźż'
VERSION = 'diagnostic-approved-conditions-v22'
UNEXPLAINED_ACCENT_LABELS = frozenset({'daw.,rzad.,akcent'})
UNEXPLAINED_FIRST_RELEASE_LABELS = frozenset({
    'astrol.', 'astrol.,ekon.', 'astron.', 'astron.,handl.', 'biblt.',
    'char.,fot.', 'char.,gry', 'etn.', 'fot.', 'gry', 'gry,zool.',
    'gwar.,etn.', 'hom.,fot.', 'hom.,gry', 'kolej.', 'podniosłe',
    'pot.,etn.', 'pot.,gry', 'pot.,slang', 'rzad.,etn.', 'rzad.,fot.',
    'rzad.,slang', 'slang', 'slang,wulg.', 'spoż.',
})


def unexplained_label_checks(qualifiers):
    """Zatwierdzone odstępstwo od wymogu objaśnienia, bez zgadywania semantyki."""
    return [{'rule_id': 'linguistic-unexplained-label-first-release-v1',
             'status': 'accept', 'source_label': label, 'gloss_status': 'unestablished',
             'message': 'Oznaczenie zachowane: objaśnienie nieustalone. Sam brak objaśnienia nie wyklucza w pierwszym wydaniu; inne kryteria osobno.',
             'evidence': ['config/generator/policy.json',
                          '.maister/tasks/development/2026-10-04-generator-broad-standard/analysis/evidence/unexplained-labels-first-release-decision.md']}
            for label in sorted(set(qualifiers.split('|')) & UNEXPLAINED_FIRST_RELEASE_LABELS)]
def accent_gloss_checks(qualifiers):
    """Zachowaj nieobjaśnioną adnotację; dawność oceniana odrębnie."""
    return [{'rule_id':'linguistic-accent-gloss-first-release-v1',
             'status':'accept', 'source_label':label, 'gloss_status':'unestablished',
             'message':'Adnotacja akcent zachowana: objaśnienie nieustalone. Sam brak objaśnienia nie wyklucza w pierwszym wydaniu; dawność i inne kryteria osobno.',
             'evidence':['config/generator/policy.json',
                         '.maister/tasks/development/2026-10-04-generator-broad-standard/analysis/evidence/accent-gloss-first-release-decision.md']}
            for label in sorted(set(qualifiers.split('|')) & UNEXPLAINED_ACCENT_LABELS)]


FIRST_RELEASE_CONTRACTIONS = frozenset('bezeń dlań doń nadeń nań odeń oń podeń poń przedeń przezeń spodeń spozań sprzedeń weń zań zeń znadeń'.split())
DEFERRED_CONTRACTIONS = frozenset('kołoń pozań zzań ponadeń popodeń poprzezeń sponadeń spopodeń'.split())
KNOWN_NAME_LABELS = frozenset({
    'człon_nazwiska', 'człon_nazwiska_(herb)', 'człon_nazwy_firmy',
    'człon_nazwy_geograficznej', 'człon_nazwy_instytucji', 'człon_nazwy_organizacji',
    'człon_nazwy_własnej', 'człon_nazwy_święta', 'człon_przydomka', 'człon_pseudonimu',
    'człon_tytułu', 'imię', 'marka', 'nazwa_członka_rodu', 'nazwa_firmy',
    'nazwa_geograficzna', 'nazwa_instytucji', 'nazwa_języka_programowania',
    'nazwa_kroju_pisma', 'nazwa_oprogramowania', 'nazwa_organizacji', 'nazwa_pospolita',
    'nazwa_własna', 'nazwa_własna_astronomiczna', 'nazwa_własna_budowli',
    'nazwa_własna_osoby', 'nazwa_własna_środka_lokomocji', 'nazwa_święta', 'nazwisko',
    'nazwisko_(odmężowskie)', 'nazwisko_(odojcowskie)', 'patronimicum', 'przydomek',
    'pseudonim', 'tytuł',
})
BOUND_FORM_CLASSES = frozenset({'adja', 'pacta', 'numcomp', 'aglt'})
CONFIRMED_CONSTRUCTOR_RULES = frozenset({
    'documented-spelling-variant-v1', 'impt-single-particle-v1', 'impt-double-particle-v1', 'by-aglt-nwok-v1', 'preposition-n-source-v1',
    'mobile-by-host-aglt-v1', 'mobile-source-host-aglt-v1', 'mobile-host-by-sequence-v1', 'personal-host-aglt-v1',
})

# Pełne identyfikatory rozdzielają mieszkańca od tanecznego homonimu m2.
# Podzbiór dowodowy; nie rozpoznajemy mieszkańców po sufiksie ani samym m1.
# Runda 1 (2026-10-08): dosłowne przykłady RJP §8.1.2 pkt 3 jako dowód klasy.
MANDATORY_CAPITAL_2026_LEMMAS = frozenset({'warszawianin','warszawiak','krakowiak:Sm1',
    'krakowianin','krakus','kresowianin','rzymianin','sądeczanin','zatorzanin'})

# Decyzja warunkowa właściciela (runda 1): wycofanie to zmiana na 'reject' i nowy build.
ADJP_GAME_STATUS = 'accept'


RESIDENT_RELATION_SOURCES = {6309663: ('warszawiance', 'subst:sg:dat.loc:f'),
 6309664: ('warszawianek', 'subst:pl:gen:f'),
 6309665: ('warszawianka', 'subst:sg:nom:f'),
 6309666: ('warszawiankach', 'subst:pl:loc:f'),
 6309667: ('warszawiankami', 'subst:pl:inst:f'),
 6309668: ('warszawianki', 'subst:pl:nom.acc.voc:f'),
 6309669: ('warszawianki', 'subst:sg:gen:f'),
 6309670: ('warszawianko', 'subst:sg:voc:f'),
 6309671: ('warszawiankom', 'subst:pl:dat:f'),
 6309672: ('warszawianką', 'subst:sg:inst:f'),
 6309673: ('warszawiankę', 'subst:sg:acc:f')}
RESIDENT_RELATION_EVIDENCE = [{'artifact_id': 'resident-relations-own-review',
  'sha256': 'ad37b2f97b253b8fc6de11ae8e043868b12fe1e653ea1cd196ee06db4a221789',
  'locator': 'resident-relations-observation.json; Warszawa#7791 → warszawianka#61637, odwrotna '
             'relacja do miejscowości; dokładne source_records',
  'status': 'ALLOWED',
  'role': 'own_documentary_review'},
 {'artifact_id': 'rjp-2026-resident-norm-own-review',
  'sha256': '87daaddd86911370d4df3c1e5769028e8fa9087e052c8954b70ec173ada2d72e',
  'locator': 'https://rjp.pan.pl/app/uploads/2025/11/2-zalacznik-do-komunikatu-11-25-wersja-jednolita.pdf#page=43; '
             '§8.1.2 pkt3',
  'status': 'ALLOWED',
  'role': 'own_documentary_review'}]
RESIDENT_RELATION_CONDITIONS = frozenset({'game-documented-resident-capital-v1','orthography-documented-resident-capital-2026-v1'})


def resident_use_checks(review, variant=None):
    """Dowód tylko zamkniętego użycia, nigdy całego źródłowego ID/pozostałości."""
    if not review:return []
    s=review.get('source',{})
    if (s.get('source_id')!='sgjp-20260823'
            or s.get('source_sha256')!='3b2ee079143bc95186370fd528735779c4ba62f4ce14e30cf6622ceb566e9810'
            or s.get('lemma_id')!='warszawianka' or s.get('names')!='nazwa_pospolita'
            or s.get('qualifiers')!=''
            or RESIDENT_RELATION_SOURCES.get(s.get('first_source_row'))!=(s.get('original'),s.get('raw_tag'))
            or review.get('use_id')!=f"sgjp-relation-warszawianka-{s.get('first_source_row')}-v1"
            or review.get('coverage')!='documented_use_only'
            or review.get('evidence')!=RESIDENT_RELATION_EVIDENCE
            or frozenset(review.get('documented_conditions',[]))!=RESIDENT_RELATION_CONDITIONS):
        return []
    common={'scope':'documented_use_only','source_lemma_id':s['lemma_id'],
            'semantic_class':'resident_of_locality','norm_effective_from':2026,
            'evidence':review['evidence']}
    if variant is None:
        return [dict(common,rule_id='game-documented-resident-capital-v1',status='reject',
            message='To udokumentowane użycie nazwy mieszkanki wymaga wielkiej litery według normy2026; obowiązujące wyłączenie growe, inne użycia osobno.')]
    return [dict(common,rule_id='orthography-documented-resident-capital-2026-v1',
        status='reject' if variant=='standard' else 'accept',
        message=('Małoliterowy zapis tego użycia nie odpowiada normie2026 STANDARD.' if variant=='standard' else
                 'BROAD nie wyklucza językowo udokumentowanego dawnego zapisu; gra i inne warunki osobno.'))]


def documented_name_checks(source):
    """Zamknięte mapowanie dokumentacji do dokładnego przypiętego rekordu."""
    if (source.get('source_id') != 'sgjp-20260823'
            or source.get('source_sha256') != '3b2ee079143bc95186370fd528735779c4ba62f4ce14e30cf6622ceb566e9810'
            or source.get('raw_tag') != 'frag' or source.get('names') != ''
            or source.get('qualifiers') != ''
            or (source.get('original'), source.get('lemma_id'), source.get('first_source_row'))
               not in {('de','de:F',1463128), ('ibn','ibn',1960055)}):
        return []
    return [{'rule_id':'game-documented-surname-component-v1','status':'reject',
             'source_lemma_id':source['lemma_id'],
             'documented_name_class':'człon_nazwiska',
             'source_identity':{k:source[k] for k in ('source_id','source_sha256','first_source_row',
                                                    'original','lemma_id','raw_tag','names','qualifiers')},
             'message':'Dokumentacja autorów SGJP wskazuje tę dokładnie przypisaną analizę jako człon nazwiska; istniejące wyłączenie growe, wpis i inne homonimy zachowane.',
             'evidence':['https://sgjp.pl/static/pdf/Podstawy_teoretyczne_SGJP.pdf#page=138',
                         '.maister/tasks/development/2026-10-04-generator-broad-standard/analysis/evidence/documented-name-class-proof-decision.md']}]


def mandatory_capital_checks(source):
    lemma=source.get('lemma_id')
    tag=source['raw_tag'].split(':')
    if (lemma not in MANDATORY_CAPITAL_2026_LEMMAS or len(tag)!=4
            or not ((tag[0]=='subst' and tag[-1]=='m1') or (tag[0]=='depr' and tag[-1]=='m2'))):
        return []
    return [{'rule_id':'game-mandatory-capital-2026-v1','status':'reject',
             'source_lemma_id':lemma,'norm_effective_from':'2026-01-01',
             'message':'Ta interpretacja nazwy mieszkańca wymaga wielkiej litery według normy2026, również przy dawnym zapisie w BROAD; inne homonimy osobno.',
             'evidence':['config/generator/orthography.json',
                         '.maister/tasks/development/2026-10-04-generator-broad-standard/analysis/evidence/capitalization-source-cases.json',
                         '.maister/tasks/development/2026-10-04-generator-broad-standard/analysis/evidence/game-capitalization-norm-decision.md',
                         'https://rjp.pan.pl/app/uploads/2025/11/2-zalacznik-do-komunikatu-11-25-wersja-jednolita.pdf#page=43']}]


def source_game_checks(source, candidate=None):
    """Ocena klas zapisu; kandydat pochodzi wyłącznie z zamkniętego konstruktora.

    Tag składnika nie oznacza klasy kompletnej rekonstrukcji. Frag/adjp
    nie są automatycznie wykluczane przez wymaganie kontekstu.
    """
    labels = set(source['names'].split('|')) - {''}
    unknown = sorted(labels - KNOWN_NAME_LABELS)
    proper = sorted(labels & (KNOWN_NAME_LABELS - {'nazwa_pospolita'}))
    mixed = bool(proper and 'nazwa_pospolita' in labels)
    result = [{'rule_id':'game-source-name-labels-v1',
               'status':'unresolved' if unknown else 'accept', 'unknown_labels':unknown,
               'message':'Nieznane oznaczenia nazwy wymagają oceny.' if unknown else
                         'Źródłowe oznaczenia nazw rozpoznane; inne warunki osobno.',
               'evidence':['config/generator/categories.json', 'https://sgjp.pl/instrukcja/']}]
    result.append({'rule_id':'game-proper-name-class-v1',
                   'status':'unresolved' if mixed else 'reject' if proper else 'accept',
                   'proper_name_labels':proper, 'mixed_common_name':mixed,
                   'message':'Mieszana klasyfikacja pospolita/własna wymaga oceny tej analizy; nie tworzymy alternatywnych sensów.' if mixed else
                             'Ta analiza jest źródłowo sklasyfikowana jako nazwa własna lub jej człon.' if proper else
                             'Brak źródłowego oznaczenia nazwy własnej; inne warunki osobno.',
                   'evidence':['config/generator/categories.json', 'https://sgjp.pl/instrukcja/']})
    pos = source['raw_tag'].split(':',1)[0]
    if candidate is not None:
        confirmed = candidate['rule_id'] in CONFIRMED_CONSTRUCTOR_RULES
        result.append({'rule_id':'game-construction-whole-unit-v1',
                       'status':'accept' if confirmed else 'unresolved',
                       'constructor_rule_id':candidate['rule_id'],
                       'message':'Potwierdzony konstruktor: oceniamy całość, nie samodzielność końcówki; pozostałe warunki osobno.' if confirmed else
                                 'Nieznany konstruktor wymaga oceny samodzielności całości.',
                       'evidence':['config/generator/constructions.json']})
        if candidate['rule_id']=='impt-double-particle-v1':
            result.append({'rule_id':'game-double-particle-v1','status':'reject',
                           'message':'Ta analiza zawiera dwa dołączenia partykuły że/ż; zachowane reguły gry wykluczają ją, niezależne homonimy osobno.',
                           'evidence':['config/generator/constructions.json','docs/generator/konstrukcje.md']})
        elif candidate['rule_id']=='personal-host-aglt-v1':
            result.append({'rule_id':'game-personal-host-aglt-v1','status':'reject',
                           'message':'Końcówka czasownikowa dołączona do zaimka lub przymiotnika: ta konstrukcyjna analiza jest wyłączona przez zachowane reguły gry; homonimy osobno.',
                           'evidence':['config/generator/constructions.json','docs/generator/konstrukcje.md']})
        elif candidate['rule_id'] in {'mobile-source-host-aglt-v1','mobile-host-by-sequence-v1'}:
            host = candidate['components'][0]['interpretation']
            permitted = (candidate['rule_id']=='mobile-source-host-aglt-v1'
                         and host['original']=='byle' and host['lemma_id'].split(':',1)[0]=='byle'
                         and host['raw_tag']=='comp')
            result.append({'rule_id':'game-mobile-host-composition-v1',
                           'status':'accept' if permitted else 'reject',
                           'message':'Udokumentowany wyjątek byle + końcówka osobowa; pozostałe kryteria osobno.' if permitted else
                                     'Ta źródłowa konstrukcja mobilnej końcówki lub trybu przypuszczającego z nieczasownikowym hostem jest wyłączona przez zachowane reguły gry; homonimy osobno.',
                           'evidence':['config/generator/constructions.json','docs/generator/konstrukcje.md']})
    elif pos == 'brev':
        result.append({'rule_id':'game-abbreviation-v1', 'status':'reject',
                       'message':'Źródłowa analiza jest skrótem; nie utożsamiamy skrótu ze skrótowcem rzeczownikowym.',
                       'evidence':['config/generator/categories.json', 'docs/generator/ortografia.md']})
    elif pos == 'adjp':
        result.append({'rule_id':'game-adjp-graphic-word-v1', 'status':ADJP_GAME_STATUS,
                       'provisional':True, 'source_class':pos,
                       'message':'Forma przyimkowa (po polsku) jest osobnym wyrazem graficznym według RJP §4.4; '
                                 'dopuszczona warunkowo decyzją właściciela, oznaczona do ewentualnego wycofania.'
                                 if ADJP_GAME_STATUS=='accept' else
                                 'Forma przyimkowa wycofana decyzją właściciela jako niesamodzielny wyraz w grze.',
                       'evidence':['.maister/tasks/development/2026-10-04-generator-broad-standard/analysis/evidence/owner-decisions-round1-decision.md', 'https://rjp.pan.pl/app/uploads/2025/11/2-zalacznik-do-komunikatu-11-25-wersja-jednolita.pdf']})
    elif pos in BOUND_FORM_CLASSES or 'pisane_łącznie_z_przyimkiem' in source['qualifiers'].split('|'):
        result.append({'rule_id':'game-dependent-segment-v1', 'status':'reject',
                       'source_class':pos,
                       'message':'Źródłowa analiza jest niesamodzielnym składnikiem; może uczestniczyć w potwierdzonej pełnej konstrukcji.',
                       'evidence':['config/generator/categories.json', 'docs/generator/konstrukcje.md']})
    if candidate is None:
        result+=mandatory_capital_checks(source)
        result+=documented_name_checks(source)
    return result


def release_scope_checks(candidate=None):
    """Zakres wydania dotyczy śladu konstrukcji; nie błędności ani całego napisu."""
    status, message = 'accept', 'Analiza nie jest wyłączona przez ograniczenie zakresu kontrakcji; inne warunki osobno.'
    if candidate is not None and candidate['rule_id']=='preposition-n-source-v1':
        original = candidate['original']
        if original in DEFERRED_CONTRACTIONS:
            status, message = 'reject', 'Kandydat poza zakresem pierwszego wydania; zachowany diagnostycznie, bez uznania formy za błędną.'
        elif original not in FIRST_RELEASE_CONTRACTIONS:
            status, message = 'unresolved', 'Nieznany zakres kontrakcji: wymagana ocena, bez automatycznego wyłączenia.'
    return [{'rule_id':'first-release-contraction-scope-v1', 'status':status,
             'message':message, 'evidence':['config/generator/constructions.json',
             '.maister/tasks/development/2026-10-04-generator-broad-standard/analysis/evidence/remaining-contractions-scope-decision.md']}]


# Dosłowne leksemy potwierdzone pełnym odczytem SGJP i poradą UŁ/RJP2026.
ORTHOGRAPHY_2026_CONJUNCTIONS = frozenset({'jeśliby','jeżeliby'})
# Runda 1: zapis łączny SGJP spoza otwartej listy RJP §4.5 pkt 1c (,,np.'').
SGJP_SINGLE_WORD_BY = {'bodajby':'part','niechby':'part','kieby':'comp','jeźliby':'comp'}


def orthography_checks(source, variant):
    """Ocena konkretnej źródłowej analizy; nie ogólna reguła końcowych liter."""
    if variant not in {'broad','standard'}:
        raise GeneratorError('Wariant musi być broad lub standard', 2)
    capital=mandatory_capital_checks(source)
    if capital and source['original'].islower():
        return [{**capital[0],'rule_id':'orthography-2026-resident-capital-v1',
                 'status':'reject' if variant=='standard' else 'accept',
                 'message':'Źródłowy dawny zapis małoliterowy nie odpowiada normie2026 wymaganej w STANDARD.' if variant=='standard' else
                           'Udokumentowany dawny zapis niewykluczający językowo w BROAD; obowiązkowa wielka litera w grze oceniana osobno.'}]
    lemma = source['lemma_id']
    if SGJP_SINGLE_WORD_BY.get(lemma) == source['raw_tag'] and source['original'] == lemma:
        return [{'rule_id':'orthography-sgjp-single-word-by-v1','status':'accept','source_lemma_id':lemma,
                 'message':'Zapis łączny według SGJP; otwarta lista RJP §4.5 pkt 1c go nie wyklucza (decyzja właściciela). Wiek i gra osobno.',
                 'evidence':['.maister/tasks/development/2026-10-04-generator-broad-standard/analysis/evidence/owner-decisions-round1-decision.md', 'https://rjp.pan.pl/app/uploads/2025/11/2-zalacznik-do-komunikatu-11-25-wersja-jednolita.pdf']}]
    if (lemma not in ORTHOGRAPHY_2026_CONJUNCTIONS or source['raw_tag'] != 'comp'
            or source['original'] != lemma):
        return []
    return [{'rule_id':'orthography-2026-conjunction-by-v1',
             'status':'reject' if variant == 'standard' else 'accept',
             'source_lemma_id':lemma, 'norm_effective_from':'2026-01-01',
             'message':'Norma 2026 wymaga pisowni rozdzielnej; ta analiza odpada ze STANDARD.'
                       if variant == 'standard' else
                       'Udokumentowany dawny zapis nie wyklucza sam w BROAD; reguły gry i inne warunki osobno.',
             'evidence':['config/generator/orthography.json',
                         '.maister/tasks/development/2026-10-04-generator-broad-standard/analysis/evidence/orthography-2026-decision.md',
                         'https://www.poradnia-jezykowa.uni.lodz.pl/szczegoly/pisownia-spojnikow-jesli-jezeli-z-czastka-by']}]


CONTEXT_REQUIREMENTS = {
    'daw.,z_D.': 'adjective_genitive',
    'daw._dziś_gwar.,z_D.': 'adjective_genitive',
    'fraz.': 'phraseological_usage',
    'fraz.,rzad.': 'phraseological_usage',
    'gwar.,z_D.': 'adjective_genitive',
    'książk.,z_D.': 'adjective_genitive',
    'po_liczebniku': 'after_numeral',
    'pot.,po_liczebniku': 'after_numeral',
    'pot.,z_D.': 'adjective_genitive',
    'przest.,z_D.': 'adjective_genitive',
    'z_D.': 'adjective_genitive',
}


def context_checks(qualifiers):
    """Zachowaj wymaganie użycia; samo w sobie nie odrzuca poprawnej formy."""
    descriptions = {
        'adjective_genitive': 'Określenie przymiotnikowe w dopełniaczu.',
        'phraseological_usage': 'Użycie frazeologiczne.',
        'after_numeral': 'Użycie po liczebniku.',
    }
    return [{'rule_id': 'linguistic-context-non-excluding-v1',
             'status': 'accept', 'source_label': label,
             'required_context': CONTEXT_REQUIREMENTS[label],
             'message': descriptions[CONTEXT_REQUIREMENTS[label]] +
                        ' Samo wymaganie kontekstu nie wyklucza; inne ograniczenia oceniane osobno.',
             'evidence': ['config/generator/policy.json',
                          '.maister/tasks/development/2026-10-04-generator-broad-standard/analysis/evidence/context-restrictions-decision.md']}
            for label in sorted(set(qualifiers.split('|')) & CONTEXT_REQUIREMENTS.keys())]


def approved_qualifier_checks(qualifiers, variant):
    """Zatwierdzone warunki kwalifikatorów; inne warstwy nadal osobno."""
    return (history_checks(qualifiers, variant) + disrecommended_checks(qualifiers)
            + usage_checks(qualifiers) + incorrect_checks(qualifiers)
            + descriptive_checks(qualifiers) + context_checks(qualifiers)
            + unexplained_label_checks(qualifiers) + accent_gloss_checks(qualifiers))


DESCRIPTIVE_LABELS = frozenset({
    'anat.',
    'anat.,muz.,techn.',
    'anat.,techn.',
    'anat.,zool.',
    'antr.',
    'archeol.',
    'archit.',
    'archit.,bud.',
    'archit.,hist.',
    'archit.,rel.',
    'archit.,techn.',
    'bank.',
    'bibl.',
    'biochem.',
    'biochem.,farm.',
    'biol.',
    'biol.,chem.',
    'biol.,fiz.,miner.,techn.',
    'biol.,kulin.',
    'biol.,med.',
    'biol.,zool.',
    'bot.',
    'bot.,chem.',
    'bot.,geol.',
    'bot.,hist.',
    'bot.,kulin.',
    'bot.,med.',
    'bot.,miner.',
    'bot.,ogr.',
    'bot.,włók.',
    'bot.,zool.',
    'bud.',
    'bud.,hist.',
    'bud.,techn.',
    'char.',
    'char.,anat.',
    'char.,archit.',
    'char.,biol.',
    'char.,bot.',
    'char.,bot.,kulin.',
    'char.,bud.',
    'char.,chor.',
    'char.,hist.',
    'char.,kulin.',
    'char.,lit.',
    'char.,meteor.',
    'char.,mit.',
    'char.,mors.,żegl.',
    'char.,muz.',
    'char.,muz.,teatr.',
    'char.,praw.',
    'char.,techn.',
    'char.,zool.',
    'char.,łow.',
    'char.,żegl.',
    'chem.',
    'chem.,farm.',
    'chem.,fiz.',
    'chem.,fiz.,muz.',
    'chem.,ogr.',
    'chem.,wojsk.',
    'chor.',
    'chor.,lit.',
    'chor.,muz.',
    'druk.',
    'druk.,hist.',
    'edyt.',
    'ekon.',
    'ekon.,praw.',
    'elektr.',
    'elektr.,komp.',
    'erud.',
    'etnolog.',
    'euf.',
    'euf.,rzad.',
    'farm.',
    'film.',
    'filoz.',
    'filoz.,rel.',
    'fiz.',
    'fiz.,mat.',
    'fiz.,techn.',
    'form.',
    'genet.',
    'geogr.',
    'geogr.,geol.',
    'geol.',
    'geol.,komp.',
    'geol.,med.',
    'gwar.,archit.',
    'gwar.,char.',
    'gwar.,hom.',
    'gwar.,pot.,żart.',
    'gwar.,rzad.,archit.',
    'gwar.,rzad.,hom.',
    'gwar.,łow.',
    'gwar.,środ.',
    'górn.',
    'górn.,rzem.',
    'górn.,techn.',
    'handl.',
    'hip.',
    'hist.',
    'hist.,lit.',
    'hist.,mit.',
    'hist.,monet.',
    'hist.,mors.',
    'hist.,poligr.',
    'hist.,polit.',
    'hist.,roln.',
    'hist.,sport.',
    'hist.,techn.',
    'hist.,wojsk.',
    'hom.',
    'hom.,anat.',
    'hom.,archit.',
    'hom.,biol.',
    'hom.,bot.',
    'hom.,bot.,kulin.',
    'hom.,bud.',
    'hom.,chem.',
    'hom.,chem.,fiz.',
    'hom.,chor.',
    'hom.,edyt.',
    'hom.,ekon.',
    'hom.,fiz.',
    'hom.,geol.',
    'hom.,hist.',
    'hom.,hydrol.',
    'hom.,jęz.',
    'hom.,komp.',
    'hom.,kulin.',
    'hom.,lit.',
    'hom.,mat.',
    'hom.,med.',
    'hom.,meteor.',
    'hom.,mit.',
    'hom.,mors.',
    'hom.,mors.,żegl.',
    'hom.,mot.',
    'hom.,muz.',
    'hom.,muz.,teatr.',
    'hom.,paleont.',
    'hom.,praw.',
    'hom.,psych.',
    'hom.,rel.',
    'hom.,sport.',
    'hom.,techn.',
    'hom.,term.',
    'hom.,wojsk.',
    'hom.,zool.',
    'hom.,łow.',
    'hom.,żegl.',
    'hydrol.',
    'indyw.',
    'indyw.,char.',
    'indyw.,hom.',
    'indyw.,rzad.',
    'indyw.,rzad.,hom.',
    'indyw.,żart.',
    'iron.',
    'iron.,char.',
    'iron.,książk.',
    'iron.,pogard.',
    'iron.,pot.',
    'iron.,pot.,żart.',
    'iron.,rzad.',
    'iron.,rzad.,hom.',
    'iron.,żart.',
    'iron.,żart.,hom.',
    'jęz.',
    'jęz.,komp.',
    'jęz.,lit.',
    'jęz.,mat.',
    'karc.',
    'komp.',
    'komp.,lit.',
    'komp.,mat.,techn.',
    'komp.,muz.',
    'komp.,psych.',
    'książk.',
    'książk.,hom.',
    'książk.,poet.',
    'książk.,pogard.',
    'książk.,rzad.',
    'książk.,żart.',
    'książk.,żart.,hom.',
    'kulin.',
    'kulin.,mikol.',
    'kulin.,sport.',
    'kulin.,zool.',
    'lekcew.',
    'lekcew.,pot.',
    'lekcew.,pot.,rzad.',
    'lekcew.,wulg.',
    'leśn.',
    'leśn.,ogr.',
    'lit.',
    'lit.,muz.',
    'lotn.',
    'mat.',
    'mat.,muz.',
    'med.',
    'med.,praw.',
    'med.,psych.',
    'med.,wet.',
    'med.,zool.',
    'meteor.',
    'mikol.',
    'mikol.,zool.',
    'miner.',
    'mit.',
    'monet.',
    'mors.',
    'mors.,wojsk.',
    'mors.,żegl.',
    'mot.',
    'muz.',
    'muz.,teatr.',
    'muz.,techn.',
    'num.',
    'ogr.',
    'paleont.',
    'plast.',
    'poet.',
    'poet.,rzad.',
    'pogard.',
    'pogard.,pot.',
    'pogard.,pot.,char.',
    'pogard.,pot.,hom.',
    'pogard.,pot.,rzad.',
    'pogard.,rzad.',
    'pogard.,wulg.',
    'pogard.,żart.',
    'poligr.',
    'polit.',
    'pot.,anat.',
    'pot.,bot.',
    'pot.,bot.,geol.',
    'pot.,bot.,kulin.',
    'pot.,char.',
    'pot.,hist.',
    'pot.,hom.',
    'pot.,karc.',
    'pot.,komp.',
    'pot.,kulin.',
    'pot.,monet.',
    'pot.,mors.',
    'pot.,mors.,wojsk.',
    'pot.,muz.',
    'pot.,num.',
    'pot.,rub.',
    'pot.,rzad.,karc.',
    'pot.,sport.',
    'pot.,szkol.',
    'pot.,wojsk.',
    'pot.,zool.',
    'pot.,środ.',
    'pot.,środ.,char.',
    'pot.,środ.,hom.',
    'pot.,żart.',
    'pot.,żart.,char.',
    'pot.,żart.,hom.',
    'pot.,żegl.',
    'praw.',
    'przen.',
    'przen.,hom.',
    'przen.,rzad.,wulg.',
    'psych.',
    'pszcz.',
    'reg.,bud.',
    'reg.,char.',
    'reg.,hist.',
    'reg.,hom.',
    'reg.,kulin.',
    'reg.,rzad.,zool.',
    'reg.,zool.',
    'reg.,łow.',
    'rel.',
    'roln.',
    'roln.,techn.',
    'rub.',
    'rub.,rzad.',
    'rub.,żart.',
    'ryb.',
    'ryb.,techn.',
    'rzad.,anat.',
    'rzad.,biol.',
    'rzad.,bot.',
    'rzad.,char.',
    'rzad.,chem.',
    'rzad.,elektr.',
    'rzad.,etnolog.',
    'rzad.,geogr.',
    'rzad.,hist.',
    'rzad.,hom.',
    'rzad.,hom.,term.',
    'rzad.,kulin.',
    'rzad.,kulin.,sport.',
    'rzad.,lit.',
    'rzad.,lotn.',
    'rzad.,mat.',
    'rzad.,med.',
    'rzad.,med.,wet.',
    'rzad.,meteor.',
    'rzad.,mikol.',
    'rzad.,muz.',
    'rzad.,num.',
    'rzad.,ogr.',
    'rzad.,rel.',
    'rzad.,roln.',
    'rzad.,ryb.,techn.',
    'rzad.,rzem.',
    'rzad.,sport.',
    'rzad.,szt.,włók.',
    'rzad.,techn.',
    'rzad.,term.',
    'rzad.,wojsk.',
    'rzad.,zool.',
    'rzad.,łow.',
    'rzad.,łow.,zool.',
    'rzad.,łow.,zootechn.',
    'rzad.,środ.',
    'rzad.,środ.,łow.',
    'rzad.,żart.',
    'rzad.,żegl.',
    'rzem.',
    'sport.',
    'sport.,zool.',
    'sport.,żegl.',
    'szach.',
    'szkol.',
    'szt.',
    'teatr.',
    'techn.',
    'term.',
    'wet.',
    'wet.,zool.',
    'wojsk.',
    'wulg.,char.',
    'wulg.,hom.',
    'włók.',
    'włók.,zool.',
    'zool.',
    'zootechn.',
    'łow.',
    'łow.,zool.',
    'łow.,zootechn.',
    'łow.,żegl.',
    'środ.',
    'środ.,char.',
    'środ.,hom.',
    'środ.,sport.',
    'środ.,łow.',
    'żart.',
    'żart.,hom.',
    'żegl.',
})


def descriptive_checks(qualifiers):
    """Sama dziedzina, styl lub oznaczenie wariantu nie wyklucza.

    Zamknięta mapa całych etykiet. Nie przenosi efektu na nieznaną
    mieszaną etykietę i nie zastępuje oceny składni lub całej analizy.
    """
    return [{'rule_id': 'linguistic-descriptive-non-excluding-v1',
             'status': 'accept', 'source_label': label,
             'message': 'Sama dziedzina, stylistyka lub opis wariantu formy nie wyklucza; pozostałe warunki oceniane osobno.',
             'evidence': ['config/generator/policy.json', 'docs/generator/etykiety.md',
                          'https://sgjp.pl/oznaczenia/', 'https://sgjp.pl/instrukcja/']}
            for label in sorted(set(qualifiers.split('|')) & DESCRIPTIVE_LABELS)]


INCORRECT_LABELS = frozenset({
    'daw.,niepopr.',
    'indyw.,niepopr.',
    'książk.,niepopr.',
    'książk.,niepopr.,pogard.',
    'niepopr.',
    'niepopr.,astron.',
    'niepopr.,biol.',
    'niepopr.,biol.,zool.',
    'niepopr.,filoz.',
    'niepopr.,fiz.',
    'niepopr.,genet.',
    'niepopr.,jęz.',
    'niepopr.,jęz.,lit.',
    'niepopr.,lit.',
    'niepopr.,med.',
    'niepopr.,muz.',
    'niepopr.,polit.',
    'niepopr.,pot.',
    'niepopr.,pot.,żart.',
    'niepopr.,przest.',
    'niepopr.,rel.',
    'niepopr.,rzad.',
    'niepopr.,rzad.,arch.,char.',
    'niepopr.,rzad.,hom.',
    'niepopr.,sport.',
    'niepopr.,szt.',
    'niepopr.,wulg.',
})


def incorrect_checks(qualifiers):
    """Jawna niepoprawność konkretnej analizy, bez usunięcia wpisu/homonimów."""
    return [{'rule_id': 'linguistic-incorrect-form-v1',
             'status': 'reject', 'source_label': label,
             'message': 'SGJP oznacza tę interpretację jako niepoprawną; odrzucenie w BROAD i STANDARD.',
             'evidence': ['config/generator/policy.json',
                          '.maister/tasks/development/2026-10-04-generator-broad-standard/analysis/evidence/incorrect-forms-decision.md']}
            for label in sorted(set(qualifiers.split('|')) & INCORRECT_LABELS)]


USAGE_LABELS = frozenset({
    'gwar.', 'gwar.,pot.', 'gwar.,rzad.', 'pot.', 'pot.,reg.',
    'pot.,reg.,rzad.', 'pot.,rzad.', 'pot.,rzad.,wulg.', 'pot.,wulg.',
    'reg.', 'reg.,rzad.', 'reg.,wulg.', 'rzad.', 'rzad.,wulg.', 'wulg.',
})


def usage_checks(qualifiers):
    """Zatwierdzony niewykluczający zakres użycia, bez pełnego werdyktu.

    Zamknięte dosłowne etykiety; nie rozbijamy przecinków w runtime.
    Mieszanki z ograniczeniami spoza tej mapy wymagają osobnej oceny.
    """
    return [{'rule_id': 'linguistic-informal-rare-non-excluding-v1',
             'status': 'accept', 'source_label': label,
             'message': 'Sama potoczność, wulgarność, regionalność, gwarowość lub rzadkość nie wyklucza; inne warunki oceniane osobno.',
             'evidence': ['docs/literaki-niezalezne-slowniki-prompt-v3.md',
                          'config/generator/policy.json', 'https://sgjp.pl/oznaczenia/']}
            for label in sorted(set(qualifiers.split('|')) & USAGE_LABELS)]

DISRECOMMENDED_LABELS = frozenset({
    'niezal.', 'daw.,niezal.', 'niezal.,przest.', 'niezal.,rzad.', 'niezal.,pot.',
})


HISTORICAL_LABELS = frozenset({
    "arch.,char.",
    "arch.,char.,biol.",
    "arch.,char.,bot.",
    "arch.,char.,bud.",
    "arch.,char.,chem.",
    "arch.,char.,chem.,fiz.",
    "arch.,char.,chor.",
    "arch.,char.,edyt.",
    "arch.,char.,ekon.",
    "arch.,char.,fiz.",
    "arch.,char.,geol.",
    "arch.,char.,hist.",
    "arch.,char.,hydrol.",
    "arch.,char.,jęz.",
    "arch.,char.,komp.",
    "arch.,char.,kulin.",
    "arch.,char.,lit.",
    "arch.,char.,mat.",
    "arch.,char.,med.",
    "arch.,char.,meteor.",
    "arch.,char.,mit.",
    "arch.,char.,mors.",
    "arch.,char.,mot.",
    "arch.,char.,muz.",
    "arch.,char.,paleont.",
    "arch.,char.,praw.",
    "arch.,char.,psych.",
    "arch.,char.,rel.",
    "arch.,char.,sport.",
    "arch.,char.,techn.",
    "arch.,char.,term.",
    "arch.,char.,wojsk.",
    "arch.,char.,zool.",
    "arch.,char.,żegl.",
    "arch._(tylko_po_\"ku\")",
    "daw.",
    "daw.,anat.",
    "daw.,arch.,char.",
    "daw.,arch.,char.,rel.",
    "daw.,bot.",
    "daw.,bud.",
    "daw.,char.",
    "daw.,char.,karc.",
    "daw.,chem.,fiz.",
    "daw.,daw._dziś_gwar.",
    "daw.,daw._dziś_gwar.,rzad.",
    "daw.,etn.",
    "daw.,flis.",
    "daw.,gry",
    "daw.,gwar.",
    "daw.,górn.",
    "daw.,hist.",
    "daw.,hom.",
    "daw.,hom.,karc.",
    "daw.,hom.,rel.",
    "daw.,indyw.",
    "daw.,iron.",
    "daw.,jęz.",
    "daw.,karc.",
    "daw.,kulin.",
    "daw.,mat.",
    "daw.,meteor.",
    "daw.,mikol.",
    "daw.,monet.",
    "daw.,niepopr.",
    "daw.,niezal.",
    "daw.,num.",
    "daw.,pogard.",
    "daw.,pot.",
    "daw.,praw.",
    "daw.,przest.",
    "daw.,przest.,rzad.",
    "daw.,pszcz.",
    "daw.,reg.",
    "daw.,reg.,char.",
    "daw.,reg.,hom.",
    "daw.,rel.",
    "daw.,rzad.",
    "daw.,rzad.,akcent",
    "daw.,rzad.,anat.",
    "daw.,rzad.,char.",
    "daw.,rzad.,hist.",
    "daw.,rzad.,hom.",
    "daw.,rzad.,jęz.",
    "daw.,rzad.,term.",
    "daw.,rzad.,zool.",
    "daw.,sport.",
    "daw.,techn.",
    "daw.,wojsk.",
    "daw.,wulg.",
    "daw.,z_D.",
    "daw.,zool.",
    "daw.,łow.",
    "daw.,środ.",
    "daw.,żart.",
    "daw.,żegl.",
    "gwar.,przest.",
    "gwar.,rzad.,arch.,char.",
    "indyw.,arch.,char.",
    "iron.,przest.",
    "iron.,żart.,arch.,char.",
    "książk.,arch.,char.",
    "książk.,przest.",
    "książk.,żart.,arch.,char.",
    "niepopr.,przest.",
    "niepopr.,rzad.,arch.,char.",
    "niezal.,przest.",
    "pogard.,pot.,arch.,char.",
    "pogard.,przest.",
    "pot.,arch.,char.",
    "pot.,przest.",
    "pot.,przest.,char.",
    "pot.,przest.,hom.",
    "przen.,arch.,char.",
    "przest.",
    "przest.,anat.",
    "przest.,arch.,char.",
    "przest.,arch.,char.,lit.",
    "przest.,char.",
    "przest.,druk.",
    "przest.,fiz.",
    "przest.,gry",
    "przest.,hip.",
    "przest.,hist.",
    "przest.,hom.",
    "przest.,hom.,lit.",
    "przest.,jęz.",
    "przest.,karc.",
    "przest.,leśn.",
    "przest.,lit.",
    "przest.,mat.",
    "przest.,med.",
    "przest.,monet.",
    "przest.,muz.",
    "przest.,paleont.",
    "przest.,podniosłe",
    "przest.,przest._dziś_książk.",
    "przest.,reg.",
    "przest.,roln.",
    "przest.,rzad.",
    "przest.,rzad.,hom.",
    "przest.,rzad.,techn.",
    "przest.,rzad.,żart.",
    "przest.,sport.",
    "przest.,szkol.",
    "przest.,szt.",
    "przest.,teatr.",
    "przest.,techn.",
    "przest.,wojsk.",
    "przest.,wulg.",
    "przest.,z_D.",
    "przest.,zool.",
    "przest.,łow.",
    "przest.,środ.",
    "przest.,żart.",
    "przest.,żegl.",
    "przest._dziś_książk.,arch.,char.",
    "rzad.,arch.,char.",
    "rzad.,arch.,char.,term.",
    "żart.,arch.,char.",
})
CURRENT_USAGE_LABELS = frozenset({
    "daw.,daw._dziś_gwar.",
    "daw.,daw._dziś_gwar.,rzad.",
    "daw._dziś_fraz.",
    "daw._dziś_gwar.",
    "daw._dziś_gwar.,rzad.",
    "daw._dziś_gwar.,z_D.",
    "daw._dziś_rzad.",
    "daw._dziś_środ.",
    "pogard.,przest._dziś_książk.",
    "przest.,przest._dziś_książk.",
    "przest._dziś_gwar.",
    "przest._dziś_książk.",
    "przest._dziś_książk.,arch.,char.",
    "przest._dziś_książk.,hom.",
    "przest._dziś_książk.,rzad.",
    "przest._dziś_książk.,żart.",
})


def history_checks(qualifiers, variant):
    """Tylko wiek formy według zamkniętego rejestru dosłownych etykiet.

    Nie rozbijamy przecinków na sensy i nie stosujemy substring na nowych
    etykietach. Dodatkowe daw./przest. nie znika przez obecność dziś.
    Pozytywna ocena tego warunku nie zatwierdza całej analizy.
    """
    if variant not in {'broad', 'standard'}:
        raise GeneratorError('Nieznany wariant słownika', 2)
    result = []
    for label in sorted(set(qualifiers.split('|'))):
        if label in CURRENT_USAGE_LABELS:
            result.append({'rule_id': 'linguistic-current-usage-non-excluding-v1',
                           'status': 'accept', 'source_label': label,
                           'message': 'Wskazane współczesne użycie nie wyklucza; dodatkowe ograniczenia oceniane osobno.',
                           'evidence': ['config/generator/policy.json', 'docs/generator/etykiety.md']})
        if label in HISTORICAL_LABELS:
            result.append({'rule_id': 'linguistic-historical-form-v1',
                           'status': 'reject' if variant == 'standard' else 'accept',
                           'source_label': label,
                           'message': 'Oznaczenie dawności wyklucza tę analizę ze STANDARD, także przy dziś.'
                                      if variant == 'standard' else 'Sama dawność nie wyklucza z BROAD.',
                           'evidence': ['config/generator/policy.json',
                                        '.maister/tasks/development/2026-10-04-generator-broad-standard/analysis/evidence/mixed-history-decision.md']})
    return result


def standard_age_baseline_checks(qualifiers, variant):
    """Zatwierdzony próg wieku; nie ustala pełnej poprawności ani współczesności."""
    if variant not in {'broad','standard'}:
        raise GeneratorError('Nieznany wariant słownika',2)
    if variant=='broad' or any(c['status']=='reject' for c in history_checks(qualifiers,variant)):
        return []
    return [{'rule_id':'linguistic-standard-age-baseline-v1','status':'accept',
        'age_basis':'source_classification','age_certainty':'not_independently_established',
        'scope':'age_condition_only','source_qualifiers':qualifiers,
        'message':'Brak wykluczającego oznaczenia wieku nie blokuje tego warunku STANDARD. Współczesność nie została niezależnie ustalona; inne warunki i konkretne dowody osobno.',
        'evidence':['config/generator/policy.json',
                    '.maister/tasks/development/2026-10-04-generator-broad-standard/analysis/evidence/standard-age-baseline-decision.md']}]


def disrecommended_checks(qualifiers):
    """Tylko warunek niezalecania, nie ocena całego kwalifikatora/analizy.

    Zamknięta lista dosłownych etykiet z audytu. Przecinka nie traktujemy
    jako separatora sensów; pozostałe składniki etykiety oceniamy osobno.
    Nieznane etykiety nadal wymagają oceny w pełnej polityce.
    """
    return [{'rule_id': 'linguistic-disrecommended-non-excluding-v1',
             'status': 'accept', 'source_label': label,
             'message': 'Samo niezalecanie nie wyklucza w BROAD ani STANDARD; pozostałe warunki oceniane osobno.',
             'evidence': ['config/generator/policy.json',
                          '.maister/tasks/development/2026-10-04-generator-broad-standard/analysis/evidence/disrecommended-decision.md']}
            for label in sorted(set(qualifiers.split('|')) & DISRECOMMENDED_LABELS)]


def spelling_checks(original):
    """Ocena źródłowego zapisu, zanim powstanie małoliterowy klucz."""
    uppercase = any(character.isupper() for character in unicodedata.normalize('NFC', original))
    return [{'rule_id': 'game-required-uppercase-v1',
             'status': 'reject' if uppercase else 'accept',
             'message': 'Źródłowy zapis wymaga wielkich liter.' if uppercase else
                        'Źródłowy zapis nie zawiera wielkich liter; pozostałe reguły oceniane osobno.',
             'evidence': ['docs/generator/ortografia.md']}]


def assess_profile(original):
    nfc = unicodedata.normalize('NFC', original)
    key = unicodedata.normalize('NFC', nfc.lower())
    invalid = sorted(set(key) - set(ALPHABET))
    checks = [
        {'rule_id': 'profile-pl-alphabet-v1', 'status': 'reject' if invalid else 'accept',
         'message': 'Znaki poza alfabetem płytek.' if invalid else 'Alfabet płytek zgodny.',
         'evidence': ['config/generator/profile.json']},
        {'rule_id': 'profile-pl-length-v1', 'status': 'accept' if 2 <= len(key) <= 15 else 'reject',
         'message': 'Wymagana długość 2–15 znaków po NFC/lower.',
         'evidence': ['config/generator/profile.json']},
    ]
    return {'status': 'reject' if any(c['status'] == 'reject' for c in checks) else 'accept',
            'version': 'pl-v1', 'original': original, 'nfc': nfc, 'game_key': key,
            'length': len(key), 'invalid_characters': invalid, 'checks': checks}


def construction_orthography_checks(candidate, variant):
    if candidate is None or candidate['rule_id']!='mobile-host-by-sequence-v1':
        return []
    if variant not in {'broad','standard'}:
        raise GeneratorError('Wariant musi być broad lub standard',2)
    return [{'rule_id':'orthography-2026-host-by-sequence-v1',
             'status':'reject' if variant=='standard' else 'accept',
             'norm_effective_from':'2026-01-01',
             'message':'Ta konstrukcja wymaga rozdzielnej pisowni by według normy2026; odrębne źródłowe wyrazy oceniane osobno.'
                       if variant=='standard' else 'Udokumentowana źródłowa konstrukcja historyczna; sama pisownia nie wyklucza w BROAD. Inne warunki osobno.',
             'evidence':['config/generator/orthography.json',
              'https://rjp.pan.pl/app/uploads/2025/11/2-zalacznik-do-komunikatu-11-25-wersja-jednolita.pdf'] }]
