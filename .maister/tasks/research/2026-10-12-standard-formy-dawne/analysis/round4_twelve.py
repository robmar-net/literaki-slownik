"""Odtwarzalna, tylko odczytowa kwerenda 12 zapisów. Surowe teksty tylko w cache.

Uruchomienie: python3 <ten plik> fetch | supplement | sources | inventory
Oceny językowe w findings/round4/current-twelve.json są pracą badacza,
nie wynikiem automatycznego klasyfikatora.
"""
import ast
import concurrent.futures
from collections import Counter
from datetime import datetime, timezone
import hashlib
import html
import json
import math
import re
import subprocess
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

TASK = Path(__file__).resolve().parents[1]
ROOT = TASK.parents[3]
CACHE = ROOT / 'tmp/research-issue4/round4-twelve'
WORDS = 'bad dag dyr reż sek sie sui um moko wiosenno świąteczno tem'.split()
tree = ast.parse((TASK / 'analysis/kwjp_live_probe.py').read_text())
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n, ast.FunctionDef)
    and n.name in ('plain', 'parse')], type_ignores=[]), '<KWJP parser>', 'exec'))

def query(word, page=1):
    url = f'https://kwjp.pl/query_corpus/21/{str(page)+"/" if page > 1 else ""}?'
    url += urllib.parse.urlencode({'query': f'[orth="{word}"]', 'per_page': 50,
                                  'chosen_corpora': 'balanced'})
    path = CACHE / f'{word}-{page}.html'
    if not path.exists():
        with urllib.request.urlopen(url, timeout=60) as response:
            body = response.read()
        total, rows = parse(body.decode())
        if total is None:
            raise ValueError(f'Nie rozpoznano wyniku {word}/{page}')
        path.write_bytes(body)
        time.sleep(.15)
    body = path.read_bytes()
    total, rows = parse(body.decode())
    assert total is not None, (word, page)
    return {'word': word, 'page': page, 'url': url, 'total': total,
            'sha256': hashlib.sha256(body).hexdigest(), 'rows': rows}

def fetch():
    CACHE.mkdir(parents=True, exist_ok=True)
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
        first = list(pool.map(query, WORDS))
    result = list(first)
    # Pełne wyniki dla <=100 trafień, dla pozostałych pierwsza i ostatnia strona.
    for record in first:
        if record['total'] > 50:
            result.append(query(record['word'], math.ceil(record['total'] / 50)))
    (CACHE / 'kwjp-raw.json').write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n')
    print('Pobrano strony:', len(result), 'wiersze:', sum(len(r['rows']) for r in result))

def inventory():
    raw = json.loads((CACHE / 'kwjp-raw.json').read_text())
    for word in WORDS:
        records = [r for r in raw if r['word'] == word]
        print(word, records[0]['total'], sum(len(r['rows']) for r in records),
              len({row['document_id'] for r in records for row in r['rows']}))

def supplement():
    patterns = ['badu|badzie|badem|badów', 'daga|dagę|dagą|dagi|dagami',
                'rży|rżą|rżami|rżach', 'seku|sekiem|seków|sekami',
                'suje|sują|suję|suja', 'tema|temy|temą|temami',
                'moka|mokę|moką|moki']
    result = []
    for pattern in patterns:
        record = query(pattern)
        result.append(record)
        print(pattern, record['total'], len(record['rows']), flush=True)
    (CACHE / 'kwjp-supplement-raw.json').write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n')

def sources():
    import importlib.util
    spec = importlib.util.spec_from_file_location("source_reader", TASK / "analysis/round3_sources.py")
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    m.TMP = CACHE
    result = []
    for word in WORDS:
        manifest, details = m.fetch(word)
        result.append({"manifest": manifest, "details": details})
        print(word, [(a["id"], a["entry"]) for a in manifest["articles"]], flush=True)
    (CACHE / "sgjp-raw.json").write_text(json.dumps(result, ensure_ascii=False, indent=2)+"\n")

def artifact():
    """Zapis ręcznych ocen. Nie klasyfikuje automatycznie nowych konkordancji.

    Indeksy odnoszą się wyłącznie do zahaszowanych stron z tej sesji. Każdy
    wiersz tych stron badacz przeczytał; poniżej koduje jego własne adnotacje.
    Surowy kontekst ani automatyczna interpretacja korpusu nie opuszczają cache.
    """
    raw = json.loads((CACHE / 'kwjp-raw.json').read_text())
    extra = json.loads((CACHE / 'kwjp-supplement-raw.json').read_text())
    analyses = json.loads((CACHE / 'all-analyses.json').read_text())
    source_records = json.loads((CACHE / 'sgjp-raw.json').read_text())
    urls = {
        'wsjp_bad': 'https://wsjp.pl/haslo/podglad/126382/bad',
        'wsjp_sek': 'https://wsjp.pl/haslo/podglad/119510/sek',
        'wsjp_rez': 'https://wsjp.pl/haslo/podglad/117368/rez',
        'wsjp_dyr_abbr': 'https://wsjp.pl/haslo/podglad/8216/dyr/967433',
        'wsjp_rez_abbr': 'https://wsjp.pl/haslo/podglad/8593/rez/1034181',
        'wsjp_sek_abbr': 'https://wsjp.pl/haslo/podglad/8823/sek/1867234',
        'wsjp_mokka': 'https://wsjp.pl/haslo/podglad/81308/mokka/5202356/napoj',
        'wilk': 'https://nowynapis.eu/tygodnik/nr-80/artykul/listy-z-procidy-6-konspira',
        'moko_madej': 'https://niezmywalnatozsamosc.blogspot.com/2011/11/?m=0',
        'moko_author': 'https://niezmywalnatozsamosc.blogspot.com/p/kontakt.html?m=0',
        'tem_zpe': 'https://zpe.gov.pl/a/przeczytaj/DaOziCkqx',
        'tem_marinow': 'https://pressto.amu.edu.pl/index.php/bp/article/view/20525',
        'tem_marinow_pdf': 'https://pressto.amu.edu.pl/index.php/bp/article/download/20525/20906',
        'tem_khan': 'https://pl.khanacademy.org/humanities/world-history/medieval-times/a/the-rise-of-the-byzantine-empire',
        'sgjp_intro': 'https://sgjp.pl/static/pdf/Wst%C4%99p%20do%20II%20wydania%20SGJP.pdf?1458313456=',
        'daga_historical': 'https://literat.ug.edu.pl/glogers/0007.htm',
        'daga_student_unresolved': 'https://spwolborz.edu.pl/witryna/kola_zainteresowan/infa/woj.pdf',
        'wiosenno_historical': 'https://wip.pbp.poznan.pl/7175277/Wiosenno',
    }
    # Kolejność: decyzja dla obecnej ścieżki; typ nowego dowodu; dowód dodatni;
    # dowód ujemny/nieadekwatny; alternatywna ścieżka; granica decyzji; źródła.
    configurations = {
      'bad': ('kwalifikuje do cofnięcia po decyzji', 'brak_nowego_dowodu_właściwej_analizy',
        'SGJP i WSJP potwierdzają rzeczownik oznaczający uzdrowisko; WSJP ma kwalifikator przest. i przykłady z lat 1974–1986.',
        '53/53 konteksty nie dotyczą uzdrowiska. Są to cytaty angielskie, tytuły oraz składniki wyrażeń bad boy, bad trip, terminów technicznych. Suplement badu/badzie/badem/badów: 0.',
        'Element angielski w polskim wyrażeniu nie potwierdza rzeczownika bad. Ewentualne wyrażenie lub nieodmienny przymiotnik wymaga osobnej podstawy leksykalnej.',
        'Nie stwierdzono nieistnienia współczesnego użycia uzdrowiskowego. Proponowane cofnięcie dotyczy wyłącznie obecnych 2 analiz rzeczownika.', ['wsjp_bad']),
      'dag': ('kwalifikuje do cofnięcia po decyzji', 'brak_nowego_dowodu_właściwej_analizy',
        'SGJP potwierdza D. lm. od daga (daw.); historyczne źródło Glogera identyfikuje broń.',
        '55/55 przejrzanych wystąpień to jednostka masy. Nie potwierdzają daga. Suplement daga/dagę/dagą/dagi/dagami: 0.',
        'Broń historyczna może mieć żywą nazwę. Wyszukiwanie dało dawny słownik, obcojęzyczne opisy oraz niezweryfikowany chronologicznie szkolny PDF z nazwą własną i objaśnieniem daga; nie jest to zamknięte wykluczenie terminologii.',
        'Cofnięcie jednej obecnej analizy wymaga decyzji; kwalifikator i brak potwierdzenia nie są dowodem nieistnienia. Nie dopuszczać skrótu dag jako substytutu tej analizy.', ['daga_historical', 'daga_student_unresolved']),
      'dyr': ('kwalifikuje do cofnięcia po decyzji', 'brak_nowego_dowodu_właściwej_analizy',
        'SGJP opisuje archaiczny wykrzyknik dźwiękonaśladowczy, przest.; WSJP potwierdza odrębną ścieżkę skrótową.',
        '59/59 wystąpień to skróty dyrektor/dyrygent, w tym zapis z rozwinięciem w nawiasie. Brak potwierdzenia wykrzyknika.',
        'Nazwisko Dyra i skrót dyrektor są już oddzielnymi odrzuconymi analizami; nie mogą ratować wykrzyknika.',
        'Cofnięcie dotyczyłoby tylko dyr/interj; nie oceniano pełnej populacji wykrzykników ani każdego regionalnego użycia.', ['wsjp_dyr_abbr']),
      'reż': ('kwalifikuje do cofnięcia po decyzji', 'brak_nowego_dowodu_właściwej_analizy',
        'SGJP i WSJP potwierdzają nazwę żyta, daw. WSJP cytuje tekst z 1977 r. o dawnych Słowianach.',
        '100/100 przejrzanych wystąpień dotyczy reżyserii/reżyserowania. Suplement 11 form rży dotyczy wyłącznie czasownika rżeć.',
        'Skrót reż. ma inną analizę. Możliwość żywego regionalnego rzeczownika żyto nie została wyczerpująco zbadana.',
        'Cofnięcie dotyczyłoby M./B. lp. rzeczownika, nie wszelkich zapisów reż. Liczba 1000 jest licznikiem interfejsu, a nie gwarantowaną pełną liczebnością.', ['wsjp_rez', 'wsjp_rez_abbr']),
      'sek': ('wstrzymać', 'błędny_poprzedni_dowód_nowy_właściwy_leksykograficzny',
        'WSJP opisuje rzeczownik oznaczający słodkie wino dawniej produkowane w Hiszpanii, bez kwalifikatora chronologicznego; ostatnia wskazana aktualizacja 23.01.2025. To właściwy leksem, a nie sekunda.',
        '53/53 konteksty nie dotyczą wina: 50 sekund, 1 skrót sekretarza, 2 urwane słowa seks. Suplement seku/sekiem/seków/sekami: 0. Przykład WSJP pochodzi z 1958 r.',
        'Zbadać współczesną terminologię winiarską i konflikt SGJP daw. / WSJP bez kwalifikatora; sam historyczny produkt nie czyni nazwy archaizmem.',
        'Nie przyjmować automatycznie całego paradygmatu na podstawie braku kwalifikatora WSJP; także nie cofać automatycznie 2 obecnych analiz.', ['wsjp_sek', 'wsjp_sek_abbr']),
      'sie': ('kwalifikuje do cofnięcia po decyzji', 'brak_nowego_dowodu_właściwej_analizy',
        'SGJP potwierdza dawne si:A oraz ograniczone współczesne związki ni to ni sio, Do siego roku; nie są one użyciem mnogiego sie.',
        '68/68 wystąpień należy do innych zjawisk: się bez diakrytyku, odmiana regionalna/stylizacja, niemiecki zaimek, adresy URL. Żaden nie realizuje przyjętych 12 analiz przymiotnikowych.',
        'Regionalne sie odpowiadające się wymagałoby własnego rekordu i oceny regionalnego źródła; nie jest dowodem odmiany si:A.',
        'Cofnięcie 12 analiz si:A dla sie; nie odrzucenie wszystkich regionalizmów ani innych form tego leksemu.', []),
      'sui': ('kwalifikuje do cofnięcia po decyzji', 'błędny_poprzedni_dowód_inna_jednostka_do_odrębnej_oceny',
        '47/47 wyników wyjaśnia współczesną obecność napisu; 46 to składniki łacińskich połączeń (również we współczesnej polskiej narracji), 1 tytuł oksytański.',
        'Żaden nie jest fleksją suja = kuksaniec. Suplement suja/suję/sują/suje: 1 rozbicie pasuje i 2 cytaty perskie.',
        'Możliwa osobna ścieżka komponentu sui generis/sui iuris po przyjęciu kryteriów projektu. Wstęp SGJP II wyraźnie wyłącza sui generis ze swojego zakresu; to opis źródła, nie wiążąca norma projektu.',
        'Cofnięcie dotyczyłoby 4 analiz suja. Nie oznacza tezy, że sam napis nie ma współczesnej funkcji lub nigdy nie może wejść inną ścieżką.', ['sgjp_intro']),
      'um': ('wstrzymać', 'błędny_poprzedni_dowód_nowy_właściwy_użyciowy_granica_stylizacji',
        'Po pierwszych 10 trafieniach znaleziono 16 właściwych polskich kontekstów u Mariusza Wilka: 9 użyć przedmiotowych odnoszących się do umysłu i 7 metajęzykowych (nie są to niezależne akty współczesnej kreacji). Dwa dokumenty: Dom włóczęgi (2014), Dziennik północny. Lotem gęsi (metadane KWJP 2021).',
        '29/45 wystąpień jest obcojęzycznych. Wszystkie 16 właściwych pochodzi od jednego autora, który świadomie przywraca zapomniane słowo. Esej Wilka z 17.12.2020 potwierdza tę strategię.',
        'To właściwy rzeczownik, nie skrót UM. Otwarte pozostaje, czy świadome autorskie archaizowanie spełnia definicję współczesnej formy Standard.',
        'Wstrzymać zarówno cofnięcie, jak i rozszerzenie. Materiał uzasadnia dyskusję M./B. lp.; nie daje automatycznej akceptacji całego paradygmatu.', ['wilk']),
      'moko': ('wstrzymać', 'błędny_poprzedni_dowód_nowe_znaczenie_wymaga_innego_rekordu',
        '99/99 kontekstów dotyczy tatuażu maoryskiego, jako rzeczownik lub składnik ta moko; dwa dokumenty o dużej zależności tekstowej. Niezależny materiał autorski kuratora wystawy z 04.11.2011 także używa rzeczownika moko.',
        'Brak wsparcia dla obecnego wołacza moka = kawa. WSJP ma mokka z podwójnym k. Suplement moka wykrywa rytuał darów (3) i zaparzacz (2), nie wołacz dawnej kawy.',
        'Zbadać osobny leksem moko w znaczeniu tatuażu: źródło leksykalne, rodzaj i nieodmienność. Nie kopiować 99 wystąpień jako 99 niezależnych świadectw.',
        'Stara analiza moka/voc jest niepoparta zebranym materiałem. Wstrzymać usunięcie napisu do rozstrzygnięcia nowej ścieżki; nie tworzyć jej pełnego paradygmatu na podstawie intuicji.', ['moko_madej', 'moko_author', 'wsjp_mokka']),
      'wiosenno': ('kwalifikuje do cofnięcia po decyzji', 'brak_nowego_dowodu_właściwej_analizy',
        'SGJP rozróżnia przestarzały przysłówek i współczesny człon przymiotnikowy adja od wiosenny.',
        '37/37 trafień to człony złożeń, nie swobodny przysłówek. Udostępniany dziś wiersz Jasieńskiego Wiosenno jest dziełem autora z lat 1901–1938, a nie nowym użyciem z daty indeksowania strony.',
        'Nie mylić członu wiosenno- z samodzielnym adv. Nowe użycie poetyckie mogłoby wymagać osobnej oceny stylizacji, lecz nie zostało znalezione.',
        'Cofnąć po decyzji wyłącznie wiosenno/adv:pos; adja pozostaje odrębną odrzuconą ścieżką.', ['wiosenno_historical']),
      'świąteczno': ('kwalifikuje do cofnięcia po decyzji', 'brak_nowego_dowodu_właściwej_analizy',
        'SGJP rozróżnia dawny przysłówek i współczesny człon przymiotnikowy adja od świąteczny.',
        '69/69 wystąpień to człony złożeń, nie swobodny przysłówek; również urwany zapis przed dalszym członem nie jest samodzielnym użyciem.',
        'Nie przenosić częstości świąteczno- na świąteczno/adv. Brak poświadczenia w tej próbie nie dowodzi niemożliwości użycia poetyckiego.',
        'Cofnąć po decyzji wyłącznie świąteczno/adv:pos; adja pozostaje odrębną odrzuconą ścieżką.', []),
      'tem': ('wstrzymać', 'błędny_poprzedni_dowód_nowe_znaczenie_mapowanie_nierozstrzygnięte',
        'Nowa właściwa ścieżka semantyczna: bizantyński okręg administracyjny. ZPE ma D. lm. tem w bieżącej narracji edukacyjnej. Kirił Marinow, tom 2019, publikacja 24.01.2020, używa tem zarówno w D. lm., jak i jako męskiego M./B. lp. Tekst Khan Academy ma też narzędnik temą (nieustalona data polskiego przekładu).',
        '86/86 przejrzanych KWJP nie jest obecną analizą tema/f/D.lm.: dawna lub stylizowana forma zaimka, obcy cytat, fragmenty wyrazów, błędy. Suplement tema: 3 cytaty obce i 3 rozbite wyrazy.',
        'Należy rozdzielić tema/f w dawnym sensie temat od współczesnego terminu historycznego tema/f lub tem/m3. Poświadczenie napisu oraz odmiany temą nie identyfikuje automatycznie znaczenia rekordu SGJP 59605; możliwy nowy leksem/sens.',
        'Nie usuwać napisu przed decyzją o terminie historycznym, lecz nie uznawać starej analizy za uratowaną. Brak podstaw do przeniesienia pełnego paradygmatu; osobna identyfikacja leksemu, rodzaju, sensu i źródła.', ['tem_zpe', 'tem_marinow', 'tem_marinow_pdf', 'tem_khan']),
    }
    classes = {
        'english_component': 'Angielski element/cytat/tytuł; nie rzeczownik uzdrowiskowy bad.',
        'mass_symbol': 'Jednostka masy; nie fleksja daga.',
        'abbreviation_directing': 'Skrót funkcji/instytucji związanej z kierowaniem; nie wykrzyknik dyr.',
        'abbreviation_film': 'Skrót reżyserii/reżysera; nie rzeczownik oznaczający żyto.',
        'abbreviation_seconds': 'Skrót sekundy; nie wino.',
        'abbreviation_secretary': 'Skrót sekretarza; nie wino.',
        'truncated_sex': 'Urwany wyraz seks; nie wino.',
        'reflexive_variant': 'Zapis się bez diakrytyku lub w stylizacji; nie zaimek przymiotny si:A.',
        'reflexive_regional': 'Regionalny/stylizowany odpowiednik się; nie si:A.',
        'url_fragment': 'Część adresu internetowego; nie analizowany leksem.',
        'german_pronoun': 'Niemiecki zaimek; nie polskie si:A.',
        'latin_phrase': 'Część łacińskiego połączenia użytego/cytowanego w polskim tekście; nie suja.',
        'occitan_title': 'Tytuł oksytański; nie suja.',
        'foreign_um': 'Wyraz obcojęzyczny/cytat/tytuł; nie polski rzeczownik um.',
        'um_authored': 'Użycie przedmiotowe właściwego rzeczownika um w narracji/relacji/przytoczeniu; korpus nie rozstrzyga sam daty stworzenia takiego użycia.',
        'um_metalinguistic': 'Właściwy polski leksem um, lecz użycie metajęzykowe.',
        'tattoo_moko': 'Tatuaż maoryski, również ta moko; nie wołacz od kawy moka.',
        'compound_part': 'Niesamodzielny człon złożenia; nie przyjęty przysłówek.',
        'tem_pronoun': 'Dawna/stylizowana forma zaimka ten/tym; nie rzeczownik tema.',
        'tem_foreign': 'Obcojęzyczny cytat; nie polska tema.',
        'tem_fragment_or_error': 'Fragment wyrazu, błąd lub uszkodzenie tekstu; nie udokumentowany rzeczownik tema.',
        'tem_abbreviation': 'Skrót temperatury w kontekście pogody; nie rzeczownik tema.',
        'verb_rzec': 'Forma czasownika rżeć; nie fleksja rzeczownika reż.',
        'suja_fragment': 'Druga część podzielonego pasuje; nie suja.',
        'suja_foreign': 'Cytat perski; nie suja.',
        'tema_foreign': 'Cytat portugalski lub hiszpański; nie polska tema.',
        'tema_fragment': 'Fragment temat/tematyka po rozbiciu zapisu.',
        'moka_ritual': 'Nazwa rytuału/wymiany darów; nie kawa.',
        'moka_device': 'Nazwa typu zaparzacza; nie wołacz nazwy kawy.',
    }
    def classify(w, i):
        base = {'bad':'english_component','dag':'mass_symbol','dyr':'abbreviation_directing',
                'reż':'abbreviation_film','moko':'tattoo_moko','wiosenno':'compound_part','świąteczno':'compound_part'}
        if w in base: return base[w]
        if w=='sek': return 'truncated_sex' if i in (8,9) else 'abbreviation_secretary' if i==10 else 'abbreviation_seconds'
        if w=='sie':
            if i in (2,23,29,30,31,32,33): return 'german_pronoun'
            if i in (5,6,38,39,40,41,42,43): return 'url_fragment'
            if i in (7,44,45,864,865,866): return 'reflexive_regional'
            return 'reflexive_variant'
        if w=='sui': return 'occitan_title' if i==12 else 'latin_phrase'
        if w=='um':
            if i in (14,15,16,17,24,25,26,29,32): return 'um_authored'
            if i in (18,19,27,28,30,31,33): return 'um_metalinguistic'
            return 'foreign_um'
        if w=='tem':
            if i==0: return 'tem_foreign'
            if i in (155,163,165,168,169,170,181): return 'tem_fragment_or_error'
            if i==182: return 'tem_abbreviation'
            return 'tem_pronoun'
        if w.startswith('rży|'): return 'verb_rzec'
        if w.startswith('suje|'): return 'suja_fragment' if i==0 else 'suja_foreign'
        if w.startswith('tema|'): return 'tema_foreign' if i<3 else 'tema_fragment'
        if w.startswith('moka|'): return 'moka_ritual' if i<3 else 'moka_device'
        raise ValueError((w,i))
    documents = {}
    def reviewed(record):
        result = []
        for i,row in enumerate(record['rows'], start=(record['page']-1)*50):
            documents[row['document_id']] = {'date_as_reported':row['date'],'metadata':row['metadata']}
            result.append({'hit_index_zero_based':i, 'document_id':row['document_id'],
                           'sentence':row['sentence'], 'manual_class':classify(record['word'],i)})
        return {k:record[k] for k in ('word','page','url','total','sha256')} | {'downloaded':len(result),'read_and_assessed':len(result),'annotations':result}
    pages = [reviewed(r) for r in raw]
    extra_pages = [reviewed(r) for r in extra]
    cases=[]
    for w in WORDS:
        cfg=configurations[w]
        accepted=[{'analysis_key':a[1], 'lemma':a[2], 'tag':a[3], 'qualifiers':a[4], 'assessment_key':a[6]} for a in analyses[w] if a[5]=='accept']
        other=[{'analysis_key':a[1], 'lemma':a[2], 'tag':a[3], 'qualifiers':a[4], 'status':a[5]} for a in analyses[w] if a[5]!='accept']
        selected=[p for p in pages if p['word']==w]
        annotations=[a for p in selected for a in p['annotations']]
        source=next(s['manifest'] for s in source_records if s['manifest']['word']==w)
        cases.append({'word':w,'decision':cfg[0],'evidence_category':cfg[1],
                      'accepted_analyses':accepted,'other_baseline_analyses':other,
                      'positive_evidence':cfg[2],'negative_or_wrong_evidence':cfg[3],
                      'alternative_analysis':cfg[4],'decision_boundary':cfg[5],
                      'external_source_ids':cfg[6], 'sgjp_current':source,
                      'kwjp_displayed_total':selected[0]['total'],'kwjp_downloaded':len(annotations),
                      'kwjp_read_and_assessed':len(annotations),
                      'kwjp_documents':len({a['document_id'] for a in annotations}),
                      'kwjp_classes':dict(Counter(a['manual_class'] for a in annotations))})
    result={'schema_version':1,'created_at_utc':datetime.now(timezone.utc).isoformat(),
            'scope':'Research only; brak zmian danych/ocen produkcyjnych. Propozycje wymagają decyzji operatora.',
            'baseline':'data/work/lists-v30-20261010-165826-a/build.sqlite',
            'method':{'selection':'KWJP, zbiór balanced/21, dokładny orth małymi literami. Pierwsze 50 i ostatnia strona po 50. Dla <=100 pełna odpowiedź. Suplement 7 grup innych form, pierwsze 50 (żadna grupa nie przekroczyła 50). Dobór celowy, bez estymacji populacji.',
                      'downloaded_exact':sum(p['downloaded'] for p in pages),
                      'read_and_assessed_exact':sum(p['read_and_assessed'] for p in pages),
                      'overlap_round3_first10':120,'additional_exact_rows_beyond_round3':651,
                      'downloaded_supplement':sum(p['downloaded'] for p in extra_pages),
                      'read_and_assessed_supplement':sum(p['read_and_assessed'] for p in extra_pages),
                      'independence':'Wiersze nie są niezależnymi świadectwami. um: 1 autor/2 dokumenty. moko: 2 dokumenty z dużym pokryciem tekstu. Ręczna ocena kontekstu ma pierwszeństwo przed automatycznym tagiem KWJP.',
                      'limitations':['Małe litery i wybrane warianty nie obejmują wszystkich zapisów ani całych paradygmatów.',
                                     'Licznik 1000 reż może być limitem interfejsu.',
                                     'Brak w ograniczonej kwerendzie nie dowodzi nieistnienia formy.',
                                     'Daty dokumentów KWJP są metadanymi, nie gwarantują daty stworzenia słów; Lotem gęsi raportowane jako 2021.',
                                     'Cytat dawny w nowym wydaniu nie jest współczesnym autorskim użyciem.',
                                     'Khan Academy: dopasowanie odmiany widoczne w indeksie wyszukiwarki; open zwróciło pustą stronę, data przekładu nieustalona. Dowód pomocniczy.',
                                     'Szkolny PDF daga to niezweryfikowany trop; nie policzony jako dodatnie poświadczenie współczesnego użycia.']},
            'summary':{'spellings':len(cases),'accepted_analyses':sum(len(c['accepted_analyses']) for c in cases),
                       'decisions':dict(Counter(c['decision'] for c in cases)),
                       'analyses_by_decision':dict(sum((Counter({c['decision']:len(c['accepted_analyses'])}) for c in cases),Counter()))},
            'cases':cases,'class_legend':classes,'pages':pages,'supplement_pages':extra_pages,
            'documents':documents,'external_sources':[{ 'id':k,'url':v,'accessed':'2026-10-12'} for k,v in urls.items()],
            'publication':'Wyłącznie własne parafrazy, oceny i metadane. Surowe odpowiedzi oraz teksty KWJP pozostają w ignorowanym tmp/research-issue4/round4-twelve/.'}
    assert result['summary']['accepted_analyses']==30
    assert result['method']['read_and_assessed_exact']==771
    assert result['method']['read_and_assessed_supplement']==25
    out=TASK/'analysis/findings/round4'
    out.mkdir(parents=True,exist_ok=True)
    (out/'current-twelve.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(result['summary'],ensure_ascii=False))

if __name__ == '__main__':
    {'fetch': fetch, 'inventory': inventory, 'supplement': supplement, 'sources': sources, 'artifact': artifact}[sys.argv[1]]()
