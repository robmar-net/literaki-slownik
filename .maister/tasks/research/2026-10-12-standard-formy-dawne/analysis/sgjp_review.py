"""Manifest odczytanych stron SGJP i własne obserwacje; bez redystrybucji tabel."""
import hashlib
import json
import urllib.parse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]
TASK = Path(__file__).resolve().parents[1]
TMP = ROOT/'tmp/research-issue4'
OUT = TASK/'analysis/findings/round2'
DATA = '''
akcesorium|23062|Nagłówek daw.; pełna liczba pojedyncza i mnoga. Istnienie tabeli nie dowodzi współczesności lp.
atencja|18022|Nagłówek przest.; atencyj osobno char. arch. Rozdzielone poziomy kwalifikacji.
bakier|73621|Daw., flis.; nota ogranicza dzisiejsze użycie do na bakier, choć tabela jest pełna.
cugiel|26165|Przest., objaśnienie odsyła do cugle; pełna lp. nie rozstrzyga dzisiejszego ograniczenia liczby.
desperacja|27040|Przest. w nagłówku, desperacyj char. arch. w tabeli. Wysoka pozycja częstości nie usuwa kwalifikatora.
dinozaur|4078|Przest. i paleont. w nagłówku; rodzaj m2. Nie należy interpretować wieku zwierzęcia jako wieku jego nazwy.
dokument|3202|Leksem bez dawności w nagłówku; dokumenta jako dawny wariant liczby mnogiej.
familia|29801|Przest. w nagłówku; familij ma oddzielne char. arch.
generyczny|108785|Przest. w nagłówku, zwykła tabela przymiotnika; sprzeczność z żywymi znaczeniami wymaga dowodu semantycznego.
industrialny|111758|Przest. w nagłówku mimo współczesnych użyć; czytnik potwierdza, że to nie tylko błąd odczytu eksportu.
kajet|35106|Przest. w nagłówku, pełna odmiana; WSJP także oznacza dawność.
klasztor|3048|Klasztora ma daw. przy konkretnej formie, klasztoru bez tego oznaczenia.
kursor|39051,39052,66898|Trzy leksemy: posłaniec m1 daw., koń m2 daw., znak ekranowy m3. Kursorzy należy do osobowego posłańca.
manowiec|40850|Daw.; objaśnienie manowce i pełna lp. Nie dowodzi współczesności manowca.
metr|1773,66941,83455|Jednostka długości, nauczyciel m1 przest. i metrum. Metrowie należy do nauczyciela.
miałki|122041|Brak dawności nagłówka; odsyłacz do mielszy. Sam odsyłacz nie rozstrzyga dzisiejszej kwalifikacji stopnia wyższego.
niezbędnik|113|Daw. w nagłówku i pełna odmiana; współczesne konteksty wskazują narzędzie/zestaw.
osiem|90127|Ośm ma daw. przy wariancie. Duża frekwencja osiem nie jest dowodem wariantu ośm.
otyły|13161,129567|Osobno rzeczownik i przymiotnik; odsyłacz do otylszy. Nie oceniono wieku stopnia wyższego na podstawie samego rodzica.
podorędzie|48994|Daw. i pełna odmiana, bez dowodu użycia wszystkich form w obecnym języku.
porachunek|49760|Przest., glosa rachunek; trzeba oddzielić od dzisiejszych porachunków w sensie konfliktu.
powijak|50112|Przest.; nazwa płótna i pełna lp. WSJP opisuje również ten przedmiot, osobno od figuratywnych powijaków.
preferować|260027|Przest. w nagłówku; odsyłacze do imiesłowów i odsłownika. Potwierdza rzeczywistą etykietę źródła.
przechwałka|50988|Daw. nad kilkoma znaczeniami: groźba/obraza oraz przechwalanie. Nie dowodzi dawności każdego znaczenia.
przyjaźny|138049|Dawny wariant pisowni z ź; nie mylić ze współczesnym przyjazny.
radośny|139132|Dawny wariant pisowni z ś; nie mylić ze współczesnym radosny.
rozpuk|54175|Daw.; nota wskazuje współczesne do rozpuku. Pełna tabela nie uzasadnia rozpukowi.
siedem|90154|Siedm ma daw. przy wariancie; siedem nie ma tego oznaczenia.
sołtyska|56579|Przest. w nagłówku; czytnik nie rozdziela tu współczesnej pani sołtys od dawnej żony sołtysa tak jak WSJP.
sztaluga|58772|Daw. i glosa sztalugi; współczesną lp. potwierdzają WSJP i niezależny odczyt kontekstu.
szuwar|58909|Przest. i glosa szuwary; WSJP wskazuje zwykle liczbę mnogą, co nie oznacza wyłącznie mnogiej.
ukradek|61025|Daw.; nota ogranicza dzisiejsze użycie do ukradkiem i z ukradka mimo pełnej tabeli.
umór|61110|Daw.; nota wskazuje na umór. Poprawia wcześniejsze mylne do umoru; brak dowodu umorach.
wolontariacki|1005298|Daw. w nagłówku; WSJP i teksty XXI wieku dokumentują żywe znaczenie.
wynegocjować|257540|Przest. w nagłówku; bieżąca etykieta źródła, nie wyłącznie pomyłka parsera eksportu.
wywrzeć|268872,268873|Dwa czasowniki: dawny nieprzechodni o wygotowaniu (wywre, wywrzał) i przechodni o wpływie (wywrze, wywarł). Konkretne potwierdzenie błędu przenoszenia frekwencji między homonimami.
wyłącznie|171781,1200244|Osobno przysłówek odprzymiotnikowy z odsyłaczem do wyłączniej oraz nieodmienna partykuła. Nie przenosić popularności partykuły na stopniowanie przysłówka.
zapęd|64500|Daw.; glosa pęd/impet i pełna odmiana. Oddzielić to znaczenie od współczesnych zapędów.
zarośle|64527|Przest.; glosa zarośla i tabela lp. WSJP obecne zarośla opisuje jako pluralia tantum.
zasłonić|271105|Nagłówek bez dawności; zasłoniono, zasłonienie, zasłonieni oznaczone przest. przy wariantach, inne formy bez tej etykiety.
'''
records=[]
for line in DATA.strip().splitlines():
    word,ids,note=line.split('|',2)
    qp={'sort_rules':['a_fronte'],'filter':{},'visible_vocabs':['SGJP','miejscowości','nazwiska'],'reader':True}
    url='https://sgjp.pl/edycja/ajax/search-by-form/?'+urllib.parse.urlencode({'exponent':word,'query_params':json.dumps(qp,ensure_ascii=False,separators=(',',':')),'columns':'["entry","abbr_pos","genders"]'})
    search=TMP/f'sgjp-{word}-search.json'
    rows=[]
    for id in ids.split(','):
        path=TMP/f'sgjp-{id}-tables.json'
        rows.append({'id':int(id),'url':f'https://sgjp.pl/edycja/ajax/inflection-tables/?lexeme_id={id}&variant=0','response_sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
    records.append({'word':word,'search_url':url,'search_response_sha256':hashlib.sha256(search.read_bytes()).hexdigest(),'articles':rows,'observation':note})
assert len(records)==40
assert sum(len(x['articles']) for x in records)==47
(OUT/'sgjp-review.json').write_text(json.dumps({'accessed':'2026-10-12','queries':40,'articles':47,'method':'Celowa kontrola publicznego czytnika: nagłówek, kwalifikatory przy formach, glosy i ograniczenia. Własne notatki, nie nowe dane generatora. Baza online nie musi odpowiadać eksportowi 20260823. Przegląd nie ustala pochodzenia wszystkich kwalifikatorów.','cases':records},ensure_ascii=False,indent=2)+'\n')
print('SGJP: 40 zapytań, 47 artykułów, manifest SHA256')
