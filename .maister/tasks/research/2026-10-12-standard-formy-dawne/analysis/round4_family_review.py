"""Osobny przegląd rodzin: surowy cache jest ignorowany, raport nie zawiera cytatów."""
import ast
import hashlib
import html
import json
import re
import sys
import urllib.parse
import urllib.request
from html.parser import HTMLParser
from collections import Counter
from pathlib import Path

TASK = Path(__file__).resolve().parents[1]
ROOT = TASK.parents[3]
CACHE = ROOT / 'tmp/research-issue4'
EXTRA = CACHE / 'round4-family'
OUT = TASK / 'analysis/findings/round4'


def read(path):
    return json.loads(path.read_text())


def fetch():
    # Parser wyłącznie transportowy, bez przejmowania ocen pierwszego badacza.
    tree = ast.parse((TASK / 'analysis/kwjp_live_probe.py').read_text())
    namespace = {'re': re, 'html': html}
    exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n, ast.FunctionDef)
                                 and n.name in ('plain', 'parse')], type_ignores=[]),
                 '<kwjp-parser>', 'exec'), namespace)
    EXTRA.mkdir(parents=True, exist_ok=True)
    results = []
    for word in ['utytułować', 'utytułował', 'utytułowała', 'utytułowali',
                 'utytułuje', 'utytułowanie', 'utytułowano']:
        url = 'https://kwjp.pl/query_corpus/21/?' + urllib.parse.urlencode({
            'query': '[orth="' + word + '"]', 'per_page': '10', 'chosen_corpora': 'balanced'})
        path = EXTRA / (word + '.html')
        if not path.exists():
            with urllib.request.urlopen(url, timeout=45) as response:
                path.write_bytes(response.read())
        total, rows = namespace['parse'](path.read_text())
        assert total is not None, word
        result = {'word': word, 'url': url, 'total': total,
                  'sha256': hashlib.sha256(path.read_bytes()).hexdigest(), 'rows': rows}
        results.append(result)
        print(word, total, flush=True)
        for row in rows:
            print(row['document_id'], row['date'], row['left'], row['word'], row['right'], flush=True)
    (EXTRA / 'kwjp-extra.json').write_text(json.dumps(results, ensure_ascii=False, indent=2) + '\n')


SOURCES = {
    'utytulowac-school': 'https://zss-szamotuly.pl/osiagniecia/',
    'utytulowac-university': 'https://gazeta.us.edu.pl/node/225861',
    'utytulowac-sgjp': 'https://sgjp.pl/edycja/ajax/inflection-tables/?lexeme_id=258968&variant=1',
    'dwoic-wsjp': 'https://wsjp.pl/haslo/podglad/82235/dwoic-sie',
    'nascie-wsjp': 'https://wsjp.pl/haslo/podglad/112096/nascie',
    'szewron-wsjp': 'https://wsjp.pl/haslo/podglad/110989/szewron/5262617/naszywka',
    'surdut-wsjp': 'https://wsjp.pl/haslo/podglad/71964/surdut/5193113/marynarka',
    'solenny-wsjp': 'https://wsjp.pl/haslo/podglad/86912/solenny/5215913/obietnica',
    'zasadny-wsjp': 'https://wsjp.pl/haslo/podglad/85607/zasadny',
    'rozgorzec-wsjp': 'https://wsjp.pl/haslo/podglad/105235/rozgorzec/5251162/swiatlo',
}


def fetch_sources():
    EXTRA.mkdir(parents=True, exist_ok=True)
    results = []
    for key, url in SOURCES.items():
        path = EXTRA / (key + '.html')
        try:
            if not path.exists():
                with urllib.request.urlopen(url, timeout=45) as response:
                    path.write_bytes(response.read())
            results.append({'id': key, 'url': url, 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()})
            print(key, path.stat().st_size, flush=True)
        except Exception as error:
            results.append({'id': key, 'url': url, 'error': str(error)})
            print(key, 'ERROR', str(error), flush=True)
    (EXTRA / 'sources.json').write_text(json.dumps(results, ensure_ascii=False, indent=2) + '\n')


class SourceParser(HTMLParser):
    """Osobny parser spanów i ich najbliższego li; bez importu czytnika rundy3."""
    def __init__(self, source):
        super().__init__(convert_charrefs=True)
        self.stack = []
        self.records = []
        self.feed(source)

    def handle_starttag(self, tag, attrs):
        if tag in {'br', 'img', 'input', 'meta', 'hr', 'link', 'wbr'}:
            return
        self.stack.append({'tag': tag, 'classes': dict(attrs).get('class', '').split(),
                           'text': [], 'forms': [], 'qualifiers': []})

    def handle_data(self, data):
        for node in self.stack:
            node['text'].append(data)

    def handle_endtag(self, tag):
        matches = [i for i, node in enumerate(self.stack) if node['tag'] == tag]
        if not matches:
            return
        node = self.stack[matches[-1]]
        self.stack = self.stack[:matches[-1]]
        value = re.sub(r'\s+', ' ', ''.join(node['text'])).strip()
        if value and ('form' in node['classes'] or 'qualifiers' in node['classes']):
            for ancestor in reversed(self.stack):
                if ancestor['tag'] == 'li':
                    ancestor['forms' if 'form' in node['classes'] else 'qualifiers'].append(value)
                    break
        if tag == 'li':
            for form in node['forms']:
                self.records.append({'word': form, 'qualifiers': node['qualifiers']})


# Własne oceny po odczycie konkordancji i tabel, a nie skopiowane decyzje rundy 3.
NOTES = '''admirator|Zwolennik i wielbiciel osób; użycie autorskie w biografii i publicystyce. Pełna odmiana m1.
adwersarz|Przeciwnik w sporze politycznym i artystycznym. Rzadkie adwersarzów ma jawne podparcie fleksyjne.
aktuariusz|Osoba wykonująca współczesny zawód ubezpieczeniowy; brak potrzeby ratowania dawnego znaczenia urzędnika.
atencja|Względy, szacunek lub uwaga w narracji współczesnej. Bez archaicznego atencyj.
aukcja|Sprzedaż licytacyjna, także internetowa; odmiana rzeczownika, bez aukcyj.
aukcyjny|Związek z domami i portalami aukcyjnymi; wszystkie rodzaje przymiotnika.
bębniarz|Wykonawca muzyki, nie dawny urząd. Bębniarzów rzadkie, ale nieoznaczone jako dawne.
denominacja|Współczesne nazwy wyznań oraz przeliczenia waluty; wspólna odmiana bez denominacyj.
desperacja|Stan psychiczny w autorskiej narracji; liczba mnoga nie jest zakazana. Bez desperacyj.
diariusz|Nazwa typu zapisu i dzieła w krytyce literackiej; opis dawnych dzienników nie datuje samego wyrazu.
dinozaur|Konkordancje zawierają metafory osób. WSJP osobno potwierdza zwierzę i odmianę m2, potrzebną dla tej analizy.
domniemywać|Autorskie wnioskowanie. Przechodniość i powiązane imiesłowy/odsłownik udokumentowane w SGJP.
donacja|Część przykładów opisuje dawne nadania; darowizna dla instytucji daje odrębny żywy zakres. Bez donacyj.
doradztwo|Doradzanie inwestycyjne i repertuarowe. Pełna odmiana obejmuje również rzadką liczbę mnogą.
dostawczy|Samochód przeznaczony do dostaw; regularna odmiana przymiotnika.
dwoić|Zachować zakres dwoić się: podwajanie i frazeologizm. WSJP potwierdza odsłownik i czynny imiesłów. Bierny pozostaje wyłączony.
dyktat|Narzucona wola, także w sztuce i polityce; pełna odmiana m3.
edukować|Czynność kształcenia i uświadamiania z wyrażonym obiektem; uzasadniony czynny i bierny zakres czasownika.
ekscytacja|Stan emocjonalny i poznawczy. Regularna odmiana bez ekscytacyj.
eksplikacja|Wyjaśnianie w filozofii i krytyce; specjalistyczność nie jest dawnością. Bez eksplikacyj.
estyma|Szacunek w autorskim komentarzu. Pełny paradygmat nie wymaga osobnego poświadczenia każdego przypadka.
ewangelizować|Współczesna czynność religijna z obiektem; pełna odmiana i powiązane formy czasownikowe.
familia|Rodzina, także w żywej narracji pierwszoosobowej; książkowe nacechowanie, bez familij.
fantazmat|Pojęcie w rozważaniach o sztuce i polityce. Zbieżna odmiana rzeczownika m3.
feta|Uroczyste świętowanie. Oceniono ten zakres, nie ser lub narkotyk.
finalny|Końcowy rezultat i etap; właściwe współczesne znaczenie przymiotnika.
forpoczta|Przenośny zwiastun lub grupa poprzedzająca; współczesny komentarz, pełna odmiana rzeczownika.
garsoniera|Niewielkie mieszkanie, także dzisiejsze; dawne realia jednego przykładu nie ograniczają pozostałych.
gawiedź|Zbiorowość ludzi oceniana przez autora. SGJP podaje obie liczby; rzadkość mnogiej nie jest powodem wyłączenia.
gehenna|Ciężkie przeżycia, także biurokratyczne; żywa metafora, regularna odmiana.
generyczny|Ogólny typ programistyczny i schematyczna muzyka; współczesne znaczenia fachowe/metaforyczne.
harcówka|Pomieszczenie harcerzy używane współcześnie. Nie należy utożsamiać z dawnym znaczeniem związanym z harcem.
hospicjum|Instytucja opieki; liczba mnoga hospicja i formy zależne odpowiadają temu samemu znaczeniu.
industrialny|Przemysłowy charakter miejsca lub zjawiska; dawność opisywanego miasta nie zmienia rejestru autora.
instrumentarium|Zestaw narzędzi, także abstrakcyjnych. Odmiana liczby mnogiej jest właściwa temu zakresowi.
insurekcyjny|Związany z tradycją i ideą powstańczą w dzisiejszym wywodzie. Nazwa dawnego zjawiska pozostaje żywa.
jagnięcina|Mięso w kontekście jedzenia. Obie liczby w tabeli; brak podstaw do zakazania rzadkich form mnogich.
komercja|Działalność podporządkowana zarobkowi; zwykłe autorskie użycie. Bez komercyj.
konfuzja|Zakłopotanie i dezorientacja we współczesnym opisie. Bez konfuzyj.
konkludować|Formułować wniosek w wypowiedzi; zakres czynny i odsłownik. Dodatkowo przestarzały bierny nie został przyjęty.
konsens|Porozumienie, także gospodarcze i etyczne. Nie wymaga ograniczenia do jednej stałej frazy.
konsultor|Współczesna funkcja doradcza w Kościele, dwa odrębne dokumenty. Pełna odmiana m1.
kurort|Miejscowość wypoczynkowa; użycie autorskie w wielu opisach, zwykła odmiana.
marnotrawny|Nie tylko fraza biblijna: metafora pamięci daje samodzielny przymiotnik. Odmiana zgodna, bez rozszerzania na rzeczownik.
mezalians|Niedopasowany związek; SGJP podaje obie formy mnogie mezaliansy/mezalianse bez odrębnej dawności.
mikrob|Drobnoustrój w opisie biologicznym oraz metafora; odmiana m2 odpowiada pierwszemu zakresowi.
moderować|Kierowanie dyskusją i regulowanie oddziaływania; konstrukcje bierne mają wyrażonych sprawców. Bez dawnego samodzielnego przymiotnika.
mokradło|Teren podmokły: poetycki pierwszy przykład nie jest jedynym; kolejne są narracyjne. Liczba pojedyncza ma bezpośredni dowód.
napitek|Napój w autorskim komentarzu, także żartobliwym; nie tylko cytowanie Zagłoby.
naście|Przybliżona liczba 11–19. WSJP potwierdza cały zakres siedmiu form, także naścioro i naściorga.
negocjator|Osoba prowadząca negocjacje; dzisiejsze i historyczne referenty, ta sama współczesna nazwa.
niezbędnik|Zestaw przyborów lub pomocniczych materiałów. Nie wyprowadza się dowodu z nazwy własnej.
nominować|Wskazać kandydata lub nadać stanowisko. Dwuwartościowy aspekt jest jawny w SGJP; formy nie są dobierane z innego czasownika.
obligować|Nakładać obowiązek, z wyrażonym obiektem i podstawą zobowiązania; pełny zakres czasownikowy.
odpad|Pozostałość produkcji, w tym melasa i muł. Użycie pojedyncze jest autentyczne, nie tylko wygenerowane z odpady.
odstawka|Propozycja pozostaje ograniczona: nowa forma to tylko odstawce. Konteksty nie uzasadniają włączenia całej odmiany.
okazjonalny|Sporadyczny lub związany z okazją; odmiana przymiotnika, bez automatycznego ratowania osobno oznaczonego przysłówka.
podołek|Część ubrania lub miejsce na kolanach; żywe opisy i poradnik, mimo uwagi narratora o nieznanym słowie.
pojazdowy|Związany z pojazdami: mechanika i technika. Termin fachowy o regularnej odmianie.
postura|Budowa ciała i pozycja; poprawne użycia autorskie. Rodzaj żeński i przypadki pozostają zgodne.
powiadać|Mówić lub głosić, także z podmiotem nieosobowym. SGJP wiąże czynny, bierny i odsłownik; pełna regularna odmiana.
preferować|Przedkładać coś nad coś innego. Konteksty bierne wyraźnie łączą obiekt i podmiot preferencji.
prezydencja|Sprawowanie przewodnictwa w UE; współczesne znaczenie instytucjonalne, bez prezydencyj.
prokreacja|Rozmnażanie i jego funkcja. Nie ograniczać przypadków lub liczby z powodu abstrakcyjności; bez prokreacyj.
proweniencja|Pochodzenie osób, postaci lub idei; żywy rejestr książkowy. Bez proweniencyj.
pryncypium|Zasada; SGJP podaje pojedyncze pryncypium mimo przewagi mnogiej w kontekstach. Nie wprowadzać progu dla każdej formy.
przechwałka|Przechwalanie się w dialogu współczesnej prozy. Nie ratować w ten sposób odrębnego dawnego znaczenia pogróżki.
przytulisko|Miejsce schronienia, także przenośne. Nacechowanie cudzysłowem pierwszych przykładów nie wyczerpuje zakresu.
przywdziać|Założyć strój, także współczesną koszulkę reprezentacji; odsłownik zachowuje dopełnienie. Pełna przechodnia odmiana.
przywdziewać|Nakładać strój lub metaforyczną maskę; aktualne użycie autorskie, nie tylko stylizowany cytat.
przywództwo|Kierowanie grupą i jego model. Odmiana abstrakcyjnego rzeczownika, również mnoga.
rarytas|Rzadki ceniony przedmiot lub przysmak. Co najmniej jeden przykład jest cytatem, ale są też własne wypowiedzi autorów.
reintegracja|Ponowne połączenie obszaru lub grupy; termin współczesnej polityki. Bez reintegracyj.
resentyment|Utrwalona niechęć i uraza w krytyce; nie wymaga uznania rejestru za potoczny.
rozbój|Przestępstwo w autorskim wywodzie. Rozboi ma niezal., które zgodnie z zatwierdzoną polityką samo nie wyklucza.
rozgorzeć|Rozpocząć się z siłą lub rozbłysnąć. Warianty podniosłe nie są etykietowane jako dawne formy; WSJP potwierdza równoległą odmianę.
schadzka|Umówione spotkanie miłosne; współczesna nazwa w opisie, nie tylko cytat historyczny.
siedzisko|Element mebla lub pojazdu; właściwe rzeczownikowe znaczenie i obie liczby.
skarbówka|Potoczna nazwa organu podatkowego; konteksty instytucjonalne, właściwa odmiana żeńska.
sklepikarz|Osoba sprzedająca w sklepie; współczesny wywód. Rzadkie sklepikarzów nie ma dodatkowej dawności.
solenny|Uroczysty lub stanowczo obiecany. Stopniowanie osobno potwierdzone w WSJP; regularne formy porównawcze pozostają w zakresie.
sołtyska|Kobieta pełniąca urząd, potwierdzona wprost w niezależnych opisach. Nie tylko dawna żona sołtysa.
spożytkować|Wykorzystać środki, pieniądze lub zasób; przechodni czasownik z obiektem.
surdut|WSJP potwierdza nazwę ubioru i pełną odmianę. Dawny strój nie jest dowodem dawności nazwy.
suwenir|Pamiątka z podróży w autorskim opisie, nie tylko cytat lub historyczny prezent.
szacowny|Godny szacunku, czasem ironicznie. SGJP ma nieoznaczony jako dawny stopień wyższy; WSJP dla jubilata pokazuje tylko równy, co nie jest jawnym zakazem stopniowania.
szata|Strój lub zewnętrzna postać; nie tylko szata graficzna. Dodawane szato/szatą należą do właściwego paradygmatu.
szewron|Trzy pierwsze korpusowe teksty motoryzacyjne są bardzo podobne. Uzupełnienie WSJP potwierdza pospolity rzeczownik naszywka i całą odmianę, niezależnie od logo.
sztaluga|Stojak malarski w liczbie pojedynczej; bezpośrednie użycia w kilku utworach.
szuwar|Pierwsza sonda ma jeden dokument. WSJP uzupełnia nazwę zbiorowiska i pojedyncze szuwarem; zwykle mnoga nie znaczy tylko mnoga.
szwaczka|Osoba szyjąca; autorskie opisy zawodu, poprawna odmiana żeńska.
ubezpieczyciel|Podmiot udzielający ubezpieczenia; pojedyncze ubezpieczycielu jest regularnym przypadkiem tej samej nazwy.
ubogacić|Wzbogacić duchowo lub o nowe właściwości; są użycia autorskie poza cytatem religijnym.
uniwersum|Wyodrębniony świat i zbiór wyobrażeń; liczba mnoga odpowiada temu samemu znaczeniu.
upakować|Umieścić ciasno wiele elementów; konteksty bierne dotyczą wykonanej czynności, nie innego samodzielnego leksemu.
utytułować|Pierwotne konteksty potwierdzały głównie przymiotnik. Uzupełniono autorskie użycia czasownika utytułowała (UŚ, 2005) i utytułował (szkoła, 2023); nie rozszerzać na dawne rzeczowniki utytułowany/utytułowana.
uzurpacja|Nieuprawnione roszczenie lub przywłaszczenie; żywe użycie autorskie. Bez uzurpacyj.
warzyć|Produkcja piwa i miodu pitnego daje żywy przechodni zakres. Dawne gotowanie jadła nie jest podstawą rozszerzenia.
widomy|Dający się rozpoznać znak lub dowód. Nie przenosić tej oceny na dodatkowo przestarzałe widomie.
wojaż|Podróż w aktualnej narracji; nacechowanie książkowe lub żartobliwe nie oznacza dawności.
wolontariacki|Związany z pracą ochotniczą; właściwy przymiotnik. Wolontariacku dotyczy dopuszczonej konstrukcji po..., nie swobodnego przysłówka.
wybranka|Wybrana ukochana osoba lub metaforyczna wspólnota; regularne przypadki, nie archaiczna końcówka.
wyedukować|Doprowadzić do zdobycia wiedzy; formy bierne zachowują znaczenie rezultatu kształcenia.
wynegocjować|Uzyskać w negocjacjach; odsłownik z właściwym dopełnieniem i pełna przechodnia odmiana.
władny|Mający uprawnienie lub możność zrobienia czegoś. Ograniczenie składniowe nie wyłącza regularnej odmiany rodzajów.
zagościć|Pojawić się na pewien czas, także przenośnie; zakres nieprzechodni i odsłownik, bez strony biernej.
zagustować|Zacząć coś lubić; nieprzechodnia konstrukcja z w..., pełna odmiana i odsłownik.
zasadny|Mający uzasadnienie. WSJP osobno potwierdza stopień zasadniejszy; rzadkie rodzaje nie są zakazane.
zaszaleć|Pozwolić sobie na nadmiar lub przyjemność; współczesne użycie, nieprzechodnia odmiana i odsłownik.
zbój|Rabuś albo żartobliwe określenie osoby; występuje poza dawnym cytatem. Pełna odmiana m1.
'''


def review():
    prior = TASK / 'analysis/findings/round3'
    proposal = read(prior / 'proposal.json')
    families = [row for row in proposal['family_results'] if row['new_words']]
    original = {row['lemma_id']: row for row in read(prior / 'family-decisions.json')}
    notes = dict(line.split('|', 1) for line in NOTES.strip().splitlines())
    assert set(notes) == {row['lemma_id'] for row in families} and len(notes) == 110
    raw = {row['word']: row for name in ['kwjp-live-raw.json', 'round3-kwjp-raw.json']
           for row in read(CACHE / name)}
    manifests = {row['id']: row for row in read(prior / 'full-tables-manifest.json')['articles']}
    table_data = read(CACHE / 'round3-full-tables.json')
    needed = sorted({aid for row in families for aid in row['reader_articles_traversed']})
    parsed, sources = {}, []
    for aid in needed:
        path = CACHE / f'sgjp-{aid}-variant1.json'
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        assert digest == manifests[aid]['sha256'], aid
        records = SourceParser(read(path)['html']).records
        parsed[aid] = records
        # Porównanie osobnego parsera z wcześniejszym cache po każdej formie i kwalifikatorze.
        assert Counter((r['word'], tuple(r['qualifiers'])) for r in records) == Counter(
            (r['word'], tuple(r['qualifiers'])) for r in table_data[str(aid)]['forms']), aid
        sources.append({'article_id': aid, 'url': manifests[aid]['url'], 'sha256': digest})

    proof = read(prior / 'proposal-proof.json')['cases']
    age = re.compile(r'\b(?:daw|przest|arch)\.')
    checks = Counter()

    def check_proof(item, roots):
        if item['method'] == 'existing_qualified_construction':
            assert item['components']
            for part in item['components']:
                check_proof(part, roots)
            checks['existing_construction'] += 1
            return
        assert item['source']
        for source in item['source']:
            aid = source['article_id']
            candidates = [r for r in parsed[aid] if r['word'] == source['reader_text']]
            assert candidates, (aid, item)
            assert any(r['qualifiers'] == source['qualifiers'] for r in candidates)
            assert not age.search(' '.join(source['qualifiers'])), source
            if aid not in roots:
                assert not age.search(' '.join(table_data[str(aid)]['headers'])), source
            normalized = re.sub(r'\s+(?:\(z D\.\)|z D\.)$', '', source['reader_text'])
            assert normalized == item['word'], (normalized, item['word'])
            checks['source_references'] += 1
        checks[item['method']] += 1

    for row in proof:
        for analysis in row['analyses']:
            rule = original[analysis['lemma_id']]
            check_proof(analysis['proof'], set(rule['article_ids']))
            assert analysis['tag'].split(':')[0] not in rule.get('exclude_pos', [])
            if isinstance(rule['scope'], list):
                assert row['word'] in rule['scope']
            checks['analyses'] += 1

    cases = []
    for family in families:
        lid = family['lemma_id']
        selected, seen = [], set()
        for word in original[lid]['reviewed_words']:
            for row in raw.get(word, {}).get('rows', []):
                if row['document_id'] in seen:
                    continue
                seen.add(row['document_id'])
                path = CACHE / 'kwjp-live' / (word + '.html')
                selected.append({'word': word, 'document_id': row['document_id'],
                                 'sentence_id': row['sentence'], 'url': raw[word]['url'],
                                 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()})
                if len(selected) == 3:
                    break
            if len(selected) == 3:
                break
        cases.append({'lemma_id': lid, 'result': 'potwierdzona', 'proposed_count': len(family['new_words']),
                      'proposed_words': family['new_words'], 'affected_count': 0, 'affected_words': [],
                      'scope_note': notes[lid], 'confidence': 'medium', 'reviewed_contexts': selected,
                      'reviewed_article_ids': family['reader_articles_traversed']})
    assert len({w for case in cases for w in case['proposed_words']}) == 2382
    extra_sources = read(EXTRA / 'sources.json')
    fresh = SourceParser(read(EXTRA / 'utytulowac-sgjp.html')['html']).records
    assert Counter((r['word'], tuple(r['qualifiers'])) for r in fresh) == Counter(
        (r['word'], tuple(r['qualifiers'])) for r in parsed[258968])
    # Błędy pobrania lokalnego nie unieważniają odczytu tej samej strony narzędziem web.
    web_sources = [
        {'id': key, 'url': SOURCES[key], 'access_method': 'web.run', 'read': True}
        for key in ['utytulowac-school', 'dwoic-wsjp', 'nascie-wsjp', 'szewron-wsjp',
                    'surdut-wsjp', 'solenny-wsjp', 'zasadny-wsjp', 'rozgorzec-wsjp']]
    web_sources += [
        {'id': 'szacowny-wsjp', 'url': 'https://wsjp.pl/haslo/podglad/32129/szacowny/4202582/jubilat', 'access_method': 'web.run', 'read': True},
        {'id': 'szuwar-wsjp', 'url': 'https://wsjp.pl/haslo/podglad/72148/szuwar', 'access_method': 'web.run', 'read': True},
        {'id': 'dinozaur-wsjp', 'url': 'https://wsjp.pl/haslo/podglad/31984/dinozaur/3919032/zwierze', 'access_method': 'web.run', 'read': True}]
    supplementary = [{k: v for k, v in row.items() if k != 'rows'} for row in read(EXTRA / 'kwjp-extra.json')]
    result = {
        'research_only': True, 'implementation_approved': False, 'reviewed_on': '2026-10-12',
        'reviewer': 'Osobny agent recenzujący; ten sam model i częściowo te same źródła. Nie jest to drugi anotator ludzki ani niezależna próba statystyczna.',
        'coverage': {'families': len(cases), 'proposed_words': 2382,
                     'reviewed_kwjp_contexts': sum(len(c['reviewed_contexts']) for c in cases),
                     'families_with_kwjp_contexts': sum(bool(c['reviewed_contexts']) for c in cases),
                     'raw_sgjp_tables_parsed_and_hash_verified': len(needed),
                     'morphology_checks': dict(checks),
                     'supplementary_kwjp_queries': len(supplementary),
                     'live_utytulowac_table_matches_cached_forms_and_qualifiers': True,
                     'result_counts': dict(Counter(c['result'] for c in cases)),
                     'affected_words': 0},
        'method': [
            'Ponowny odczyt surowych kontekstów: pierwsze trzy różne identyfikatory dokumentu w dostępnych zapytaniach danej rodziny; mniej, jeśli więcej nie było. Surdut: słownik WSJP zamiast KWJP.',
            'Ręczna ocena znaczenia i funkcji gramatycznej wszystkich 110 rodzin; osobne notatki na rodzinę. Tabela nie dowodzi osobnego użycia każdej z 2382 form.',
            'Osobny parser pełnych surowych tabel SGJP; porównanie kompletu form i kwalifikatorów, hashów i wszystkich 7192 analiz propozycji. Nie uruchamiano generatora ani nie zmieniano bazy.',
            'Nie kopiowano ocen pierwszego badacza. Jego lista wskazała przedmiot kontroli i istniejące zapytania, więc dobór źródeł nie jest ślepy ani losowy.',
            'Dodatkowy odczyt WSJP dla granic znaczeń/odmiany oraz bezpośrednie sondy KWJP i autorskie teksty dla utytułować.'],
        'findings': [
            {'id': 'utytulowac-gap-resolved', 'affected_family': 'utytułować', 'scope_words': 69,
             'conclusion': 'Nie wystarcza samo utytułowane; pierwotne uzasadnienie było za szerokie. Nowe bezpośrednie użycia czasownika w UŚ (2005) i sprawozdaniu szkoły (2023) domykają tę lukę w przyjętym kierunku oceny. Siedem zerowych sond KWJP nie dowodzi nieistnienia czasownika.'},
            {'id': 'szewron-dependent-texts', 'affected_family': 'szewron', 'scope_words': 10,
             'conclusion': 'Trzy podobne opisy logo nie są mocnym dowodem trzech niezależnych użyć. WSJP potwierdza pospolite znaczenie naszywki i pełną zgodną odmianę; propozycję można zachować z poprawionym uzasadnieniem.'},
            {'id': 'odstawka-report-precision', 'affected_family': 'odstawka', 'scope_words': 1,
             'conclusion': 'Propozycja dodaje odstawce; odstawkę jest wcześniej przyjęte. Nie należy opisywać obu jako już przyjętych ani rozszerzać na cały paradygmat.'},
            {'id': 'szacowny-dictionary-scope', 'affected_family': 'szacowny', 'scope_words': 22,
             'conclusion': 'SGJP podaje regularny stopień wyższy bez etykiety dawności; WSJP w odczytanym znaczeniu pokazuje tylko równy. Brak tabeli nie jest jawnym zakazem; pozostaje średnia pewność semantyczna.'}],
        'limitations': [
            'Osobny reviewer-agent ogranicza bezkrytyczne powtórzenie oceny, ale dzieli model oraz większość materiału z pierwszym badaczem.',
            'Pierwsze konkordancje to próbka celowa. Nie oszacowano błędu populacyjnego ani odsetka archaizmów.',
            'Metryki 2021/2022 w cache są datami dokumentów/wydań; nie ustalono z nich późniejszej daty powstania tekstu.',
            'Potwierdzenie obejmuje proponowane formy i wskazane znaczenia, nie wszystkie znaczenia rodzin ani pozostałych 2367 kandydatów.',
            'Brak kwalifikatora przy wariancie nie jest samodzielnym dowodem współczesności; ocenę oparto także na kontekstach i relacji fleksyjnej.'],
        'input_sha256': {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest()
                         for path in [prior / 'proposal.json', prior / 'proposal-proof.json',
                                      prior / 'family-decisions.json', CACHE / 'kwjp-live-raw.json',
                                      CACHE / 'round3-kwjp-raw.json']},
        'sgjp_sources': sources, 'extra_source_downloads': extra_sources,
        'source_access_note': 'Skrypt sources wykonano dwukrotnie z require_escalated. DNS szkoły i HTTP403 WSJP powtórzyły się; UŚ i SGJP pobrano. Odczyty web.run pozostają osobnymi dowodami, nie są przedstawiane jako lokalnie zachowane odpowiedzi HTTP.',
        'web_sources': web_sources, 'supplementary_kwjp': supplementary, 'families': cases,
    }
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / 'family-review.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(result['coverage'], ensure_ascii=False, indent=2))


if __name__ == '__main__':
    if sys.argv[1:] == ['fetch']:
        fetch()
    elif sys.argv[1:] == ['sources']:
        fetch_sources()
    elif sys.argv[1:] == ['review']:
        review()
