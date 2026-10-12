#!/usr/bin/env python3
"""Utrwala ręczne, ślepe oceny A; nie odczytuje projektu próby ani rankingu.

Surowe konkordancje zostają w ignorowanym tmp. Ten skrypt nie klasyfikuje
automatycznie: NOTES i OVERRIDES to notatki reviewera po lekturze dowodów.
"""
import hashlib
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]
TASK = Path(__file__).resolve().parent.parent
INPUT = TASK / 'analysis/findings/round5/sample-blind-a.json'
CACHE = ROOT / 'tmp/research-issue4/round5/contexts-a-raw.json'
OUT = TASK / 'analysis/findings/round5'

# hasło | klasa | pewność | odczytany zakres znaczenia | uzasadnienie oceny
NOTES = """
alogiczność|R|średnia|brak logicznego związku|Abstrakcyjna ocena w krytyce i refleksji literackiej; rejestr książkowy.
pies|C|wysoka|zwierzę domowe|Zwykłe słowo ogólne. Odczyt dotyczy zwierzęcia, nie całej grupy z homonimem osobowym i derywatami.
absolutysta|R|wysoka|zwolennik bezwzględnych zasad|Użycia filozoficzne oraz przenośne; termin i rejestr intelektualny.
lnica|R|wysoka|roślina Linaria|Ogród Botaniczny UW potwierdza nazwę rośliny. Brak live nie oznacza dawności; zakres botaniczny.
katechumenat|R|wysoka|przygotowanie do chrztu|Współczesny termin religijny, potwierdzony w różnych tekstach.
partykuła|R|wysoka|część mowy|Termin językoznawczy, także szkolny; przydatność w POP nie jest przez tę klasę rozstrzygnięta.
nienudny|C|wysoka|niebędący nudnym|Przejrzyste zaprzeczenie używane w zwykłych ocenach jedzenia, lektury i życia.
miodokwiat|R|wysoka|roślina storczykowata|WSJP definiuje nazwę botaniczną; zero live nie jest dowodem nieistnienia ani archaiczności.
szybkościomierz|C|wysoka|miernik prędkości pojazdu|Zrozumiała nazwa urządzenia w zwykłych opisach pojazdów.
zabobonnie|C|średnia|w sposób przesądny|Zwyczajny przysłówek oceniający zachowanie lub poglądy; brak wąskiej specjalizacji.
demistyfikować|R|wysoka|ujawniać złudzenie lub ideologiczne pozory|Konteksty krytyki, teorii i publicystyki wskazują rejestr książkowy.
ostojowy|R|średnia|stanowiący ostoję przyrody|Pierwotne opracowanie Lasów Państwowych potwierdza sens przyrodniczy; nie rozszerzam na inne sensy.
pyrex|R|średnia|rodzaj szkła|Materiały dydaktyczne AGH potwierdzają użycie nazwy materiału; geneza od marki wymaga ostrożności, bez rozstrzygania STANDARD.
nieuprzejmość|C|wysoka|brak uprzejmości|Zwykła nazwa zachowania w kontaktach międzyludzkich.
treściwie|C|wysoka|zwięźle i rzeczowo|Zwykły sposób mówienia lub pisania, różne konteksty.
jednogłowy|R|średnia|mający jedną głowę|Oba konteksty dotyczą orła heraldycznego. Przejrzystość budowy nie dowodzi szerokiego użycia.
kamieniować|C|wysoka|obrzucać kamieniami|Historyczne cytaty współistnieją z opisem współczesnych postaw; zwykły czasownik czynności.
idolatria|R|wysoka|ubóstwianie|Termin religijny i filozoficzny; odczytane konteksty są zgodne.
opieszale|C|wysoka|powoli i bez potrzebnej sprawności|Zwykła ocena działania ludzi i instytucji.
speleologia|R|wysoka|badanie jaskiń|Nazwa dyscypliny i zainteresowania; specjalizacja nie oznacza automatycznego odrzucenia z POP.
obznajmiać|M|średnia|zaznajamiać|Jedyny live to przytoczenie dawnej wypowiedzi. Słownikowy opis rodziny potwierdza przestarzałość i książkowość.
wylosowywać|C|średnia|dokonywać kolejnych losowań|Przejrzysty czasownik poświadczony w zwykłym kontekście egzaminu; mała liczba wyników nie zmienia sensu.
regnowski|R|wysoka|związany z Regnowem|Dokument własny gminy zawiera przymiotnik geograficzny; zakres lokalny.
skarlić|R|średnia|doprowadzić do utraty znaczenia lub wartości|Odczytano wszystkie dziewięć wyników, wyłącznie rzeczownikowe formy skarlenie. Kontekst mediów daje sens sprawczy, pozostałe często nie rozstrzygają skarlić/skarleć.
włochatość|C|średnia|cecha pokrycia włosami|Przejrzysta nazwa cechy fizycznej, także w opisie artystycznym.
ostawiać|M|średnia|pozostawiać|Cztery konteksty obejmują gwarę, archaizację i dwa zapisy nieodróżnialne od ubytku litery w zostawiać.
trzciański|R|wysoka|związany z Trzcianą|Własna publikacja gminy poświadcza lokalny przymiotnik; nie jest to wyraz nieistniejący.
zmiennocieplny|R|wysoka|mający temperaturę zależną od otoczenia|Termin biologiczny o szerokim zastosowaniu edukacyjnym, poświadczony o zwierzętach.
pensja|C|wysoka|wynagrodzenie za pracę|Zwykłe współczesne znaczenie płacy; dawny sens szkoły nie został tu oceniony.
lokajski|R|średnia|związany z lokajem lub służalczy|Użycie opisowe i książkowa przenośnia; ograniczony rejestr, bez podstaw do uznania za nieistniejące.
uwodornić|R|wysoka|poddać uwodornieniu|Jedno jednoznaczne użycie procesu chemicznego.
socjolekt|R|wysoka|odmiana języka grupy społecznej|Termin językoznawczy, potwierdzony w dwóch dokumentach.
kardamon|C|wysoka|przyprawa|Zwykłe nazwanie składnika jedzenia i napojów, obecne w różnych kontekstach.
prześmiardły|R|średnia|przeniknięty złym zapachem|Ekspresywna forma w prozie i opisie spektaklu TVP; dowód nie uzasadnia automatycznego uznania za martwą.
grzbiecisty|R|średnia|o wyraźnym grzbiecie nosa|Live dotyczy przymiotnika opisującego nos. Rzeczownik grzbiecista w grupie nie jest dowodem tego samego leksemu.
powroźniczy|R|wysoka|związany z wyrobem sznurów|Termin rzemieślniczy, potwierdzony poza nazwą własną firmy.
żółtobiały|C|średnia|barwa pośrednia między żółtą a białą|Przejrzysty przymiotnik barwy w zwykłym opisie przedmiotu; nie rozstrzygam ortografii innych znaczeń.
beletryzować|R|wysoka|nadawać cechy beletrystyki|Termin twórczości literackiej, nie archaizm tylko dlatego, że część tekstów mówi o przeszłości.
zdeprymować|C|wysoka|wprawić w zakłopotanie lub przygnębienie|Zwykły współczesny opis reakcji emocjonalnej w kilku utworach.
czapczyna|M|średnia|ekspresywnie o czapce|Jedyny kontekst to dawniej brzmiące przytoczenie; obecny materiał wskazuje marginalny ekspresywizm, nie brak legalności.
wtrząchnąć|C|wysoka|zjeść z apetytem|Zwykły potoczny czasownik, zgodne konteksty jedzenia i kalorii.
trójszereg|R|wysoka|szyk trzech szeregów|Akt policji definiuje termin musztry. Potwierdzenie spoza live wyklucza wniosek o nieistnieniu.
alienować|R|wysoka|wyobcowywać|Książkowy i socjologiczny zakres użyć; brak dowodu błędnego dopasowania.
psinka|C|wysoka|pieszczotliwie o psie|Zwykłe zdrobnienie w relacji o zwierzęciu domowym.
prawowierność|R|wysoka|zgodność z doktryną religijną|Odczytane konteksty religijne i historyczne; ograniczenie dziedzinowe.
kurczęcy|C|średnia|związany z kurczęciem|Opis mięsa i metafora budowy ciała; zwykły, choć mniej centralny przymiotnik.
kruszonka|C|wysoka|sypka warstwa na wypiekach|Użycia kulinarne i przenośne potwierdzają słowo zwykłego użytku.
kaflarnia|R|wysoka|zakład wytwarzający kafle|Nazwa zakładu rzemieślniczego; opisy dawnych fabryk same nie czynią wyrazu archaizmem.
nadprzestrzenny|R|wysoka|związany z nadprzestrzenią|Kontekst fantastyki naukowej; wyspecjalizowana konwencja.
cyborium|R|wysoka|element architektury lub naczynie liturgiczne|Konteksty ujawniają dwa sensy związane z kościołem; obydwa specjalistyczne.
kot|C|wysoka|zwierzę i frazeologia|Zwykłe słowo; odróżniono nazwę tytułu, idiom i dosłowne użycie. Nie potwierdzono wszystkich homonimów grupy.
pięciobój|R|wysoka|dyscyplina sportowa|Termin sportowy używany w publicznych opisach zawodów; klasa nie przesądza usunięcia z szerokiego POP.
śniedź|C|wysoka|nalot na metalu|Zwykła nazwa widocznej substancji w opisach przedmiotów, także literackich.
kolesiowatość|U|niska|zakres nieustalony|Brak live i brak użytecznego wyniku dodatkowej kwerendy. Budowa słowa i notowanie NKJP nie wystarczają do oceny rejestru.
rozkazująco|C|wysoka|tonem polecenia|Samodzielny przysłówek w zwykłych opisach mowy; nie przenoszę tej oceny na całą grupę czasowników.
ardeński|R|wysoka|związany z Ardenami|Geograficzny przymiotnik, także w nazwie rasy konia i zawodów kolarskich.
spotowy|R|wysoka|dotyczący bieżącego rynku dostaw|Pierwsze dziesięć trafień pochodzi z jednego dokumentu o energii; nie potwierdzają znaczenia reklamowego.
makiawelski|R|średnia|cynicznie dążący do celu|WSJP wymienia dokładne hasło jako synonim w książkowym polu znaczeniowym; brak własnego kontekstu live.
poprzekształcać|C|średnia|przekształcić wiele elementów|WSJP poświadcza zwykły dystrybutywny czasownik na przykładzie równań; zero live nie uzasadnia marginalności.
asystentura|R|wysoka|praca lub stanowisko asystenta|Akademicka nazwa funkcji; poświadczona w relacjach zawodowych.
obskurność|C|średnia|zaniedbany i nieprzyjemny wygląd|Przejrzysta nazwa cechy wnętrza w opisie filmu; brak wąskiego terminu.
chichotliwy|C|średnia|skłonny do chichotu lub go wyrażający|Ekspresywny, lecz zwykły przymiotnik; kilka zgodnych opisów śmiechu i reakcji.
uherski|X|wysoka|człon czeskiej nazwy miejscowej|Jedyny live to Uherský Brod w spolszczonej odmianie, oznaczony placeName_settlement. To nie dowód samodzielnego polskiego przymiotnika pospolitego.
autogen|R|średnia|spawanie lub palnik acetylenowy|Producent urządzeń i ogłoszenie pracodawcy potwierdzają współczesny żargon spawalniczy.
sczerstwieć|C|wysoka|utracić świeżość, przenośnie stwardnieć|Live zawiera przenośnie, a WSJP potwierdza zwykły sens dotyczący pieczywa.
kondygnacyjny|R|średnia|związany z kondygnacjami|Jedno samodzielne użycie architektoniczne; pozostałe cztery wyniki są członami zapisów liczbowych, co zawyża dowód samodzielnego hasła.
taternictwo|R|wysoka|wspinaczka tatrzańska|Termin dziedziny sportu i zainteresowania; zgodne konteksty wspinaczy.
kurant|R|średnia|melodia zegara lub mechanizm ją grający|Po odjęciu nazwy kawiarni pozostają zgodne użycia; brak potwierdzenia innych homonimów.
trójwładza|R|średnia|trzy równoległe ośrodki władzy|WSJP potwierdza współczesny termin polityczno-organizacyjny.
sekundant|R|wysoka|pomocnik uczestnika pojedynku|Odczytano znaczenie kodeksu honorowego; nie wnioskuję z niego o popularności pozostałych sensów.
hellenizacja|R|wysoka|przyjmowanie kultury greckiej|Termin historii kultury, używany współcześnie w opisach dawnych procesów.
kłopotliwie|C|wysoka|w sposób sprawiający kłopot|Zwykły przysłówek oceny, bez specjalistycznego znaczenia.
turkolog|R|wysoka|badacz języka i kultury tureckiej|Nazwa specjalizacji zawodowej; jednoznaczne konteksty osób.
sejsmograficzny|R|wysoka|związany z rejestrowaniem drgań|Techniczna podstawa i książkowe metafory; wszystkie odczytane użycia są zgodne.
witalista|R|wysoka|zwolennik lub reprezentant witalizmu|Termin filozoficzny i krytycznoliteracki.
hirudyna|R|wysoka|substancja ze śliny pijawek|Jednoznaczny termin biologiczno-medyczny, obecny też w tekstach popularnych.
dragować|R|wysoka|przesuwać się wskutek wleczenia kotwicy|Żargon żeglarski; w pierwszych dziesięciu tylko jeden dokument, nie dowód przekrojowego zasięgu.
slawistka|R|wysoka|kobieta zajmująca się slawistyką|Zwykła nazwa osoby w wyspecjalizowanej dziedzinie nauki.
eksplozywnie|R|średnia|gwałtownie, przez eksplozję|Własny opis Ogrodu Botanicznego UW potwierdza użycie o otwieraniu owocu; zakres terminologiczny.
sekserka|R|wysoka|osoba ustalająca płeć piskląt|Wywiad UWr i materiał ORE potwierdzają wyspecjalizowaną nazwę pracy.
omielić|U|niska|zakres nieustalony|Brak live; dodatkowe wyniki nie ustaliły relacji wariantu do omleć ani współczesnego zasięgu. Nie uznaję braku za nieistnienie.
mroczyć|R|wysoka|zaciemniać lub zakłócać świadomość|Po rozszerzeniu odczytu poza cytaty poetyckie są współczesne użycia; WSJP oznacza rejestr książkowy.
nargile|R|wysoka|fajka wodna|Nazwa przedmiotu z określonego kręgu kulturowego, poświadczona w relacjach podróżniczych.
kotwa|R|średnia|element kotwiczący i jego metafora|Techniczne użycie wspinaczkowe oraz przenośnie; nie utożsamiam dowodu z całą grupą kotew/kotwić.
urazówka|R|wysoka|oddział lub leczenie urazowe|Potoczny skrót środowiska medycznego, zrozumiały także w relacjach pacjentów.
mężobójczy|M|średnia|zabijający mężczyznę lub człowieka|Jedyny wynik to literacka archaizacja oskarżenia; brak podstaw do oceny jako zwykłego współczesnego słowa.
powschodzić|U|niska|wzejść o wielu roślinach|Jedyny kontekst jest cytatem biblijnym. Budowa jest przejrzysta, ale ten dowód nie rozstrzyga współczesnego zwykłego zasięgu.
zaropiały|C|wysoka|wypełniony ropą|Zwykły opis objawu fizycznego i metafora; kilka różnych dokumentów.
emblemacik|C|średnia|mały emblemat|Tekst uczennic z 1999/2000 potwierdza przejrzyste zdrobnienie. Brak live ogranicza pewność o dzisiejszym zasięgu.
wyzyskiwaczka|C|średnia|kobieta wyzyskująca innych|Przejrzysta nazwa osoby; współczesna rozprawa UAM potwierdza zgodny sens poza live.
rozpadlisko|C|średnia|głęboka rozpadlina terenu|Zwykły opis zagrożenia na polach i przy budynkach, bez konieczności fachowego znaczenia.
uziemienie|C|wysoka|instalacja ochronna lub ograniczenie ruchu|Po odczycie wszystkich ośmiu wyników potwierdzone znaczenie elektryczne i zwykłe przenośnie.
kraulowy|R|wysoka|związany z kraulem|Relacja własna szkoły z zawodów oraz instrukcja pływania potwierdzają przymiotnik sportowy.
bladozielony|C|wysoka|jasny odcień zieleni|Zwykły przymiotnik koloru, także kreatywna przenośnia.
przegrywarka|R|średnia|urządzenie do przegrywania nagrań|Badanie językoznawcze z 2003 r. potwierdza nazwę sprzętu; obecny zasięg nie wynika z tego historycznego potwierdzenia.
kakałko|C|wysoka|pieszczotliwie o kakao|Zwykłe potoczne nazwanie napoju lub produktu, dwa zgodne konteksty.
podróba|C|wysoka|imitacja lub falsyfikat|Zwykłe potoczne słowo, kilka dziedzin użycia; bez przenoszenia oceny na pełną rodzinę czasownika.
świderek|C|wysoka|spiralny produkt spożywczy|Zwykła nazwa kształtu i produktu: lody, makaron, wypiek; dowody nie obejmują wszystkich sensów.
zabajkalski|R|wysoka|związany z Zabajkalem|Przymiotnik geograficzny, również w nazwach jednostek administracyjnych i wojskowych.
mikrokomputer|R|wysoka|mały komputer|Termin informatyczny; obok historii techniki odczytano współczesne zastosowanie artystyczne.
bednia|M|średnia|naczynie z klepek|Opracowanie dialektologiczne omawia wyraz jako składnik gwary. Nie znaleziono dowodu zwykłego współczesnego użycia.
generatywność|R|wysoka|cecha generatywna w psychologii i teorii|Publikacje badaczy potwierdzają żywy, wyspecjalizowany termin mimo zera live.
bezecny|R|średnia|haniebny lub nieprzyzwoity|Książkowy ekspresywizm; są użycia współczesne, nie tylko stary cytat.
sztuczydło|R|średnia|pogardliwie o utworze scenicznym|Ekspresywne słowo krytyki teatralnej; dwa konteksty o sztuce.
omlecik|C|wysoka|mały omlet|Dwa zwykłe użycia kulinarne, obok jednego literackiego tytułu lub żartu.
toponim|R|wysoka|nazwa geograficzna|Termin onomastyczny, zgodne konteksty naukowe i eseistyczne.
shaker|R|średnia|naczynie do mieszania drinków|Termin barmański, poświadczony w przepisach; pierwsze dziesięć trafień to jeden dokument.
nori|R|średnia|wodorosty spożywcze|Nazwa składnika kuchni japońskiej, poświadczona w recepturze i relacjach.
psychoonkologia|R|wysoka|psychologiczne aspekty choroby nowotworowej|Specjalizacja kliniczna; nazwy instytucji uzupełnia samodzielne użycie nazwy dyscypliny.
czarnoksięstwo|R|średnia|praktyki magiczne|Słowo religii, historii wierzeń i literatury; konteksty nie dowodzą zaniku leksemu.
praojcowski|R|średnia|związany z przodkami|WSJP potwierdza sens; odczytane poświadczenia mają styl historyczny i podniosły.
kaszany|C|średnia|związany z kaszą|WSJP potwierdza współczesny przymiotnik kulinarny, odrębny od rzeczownika kaszana.
piszczałkowy|R|wysoka|związany z piszczałkami instrumentu|Techniczne opisy organów i instrumentów ludowych.
szczeniackość|C|średnia|niedojrzałość zachowania|Przejrzysta nazwa zwykłej cechy; jedno zgodne użycie nie mierzy rozpowszechnienia.
genotypowy|R|wysoka|związany z genotypem|Dokumenty naukowe potwierdzają termin genetyczny; nie wystarczy popularność grupowego genotyp.
glikoliza|R|wysoka|proces biochemiczny|Jednoznaczny termin biochemii. Ocena dotyczy zgodności słowa, nie poprawności naukowej całego zdania.
kalorycznie|C|wysoka|z dużą ilością kalorii|Zwykła ocena jedzenia i diety w kilku tekstach.
pozawracać|U|niska|zakres nieustalony|Brak live, dodatkowa kwerenda nie dostarczyła użycia. Przejrzysta budowa nie zastępuje dowodu zasięgu.
komercyjność|C|średnia|nastawienie na sprzedaż i zysk|Zwykła abstrakcyjna cecha ocenianego utworu; tylko jeden dokument ogranicza pewność.
wiecznotrwały|R|średnia|trwający bez końca|Podniosły i literacki przymiotnik, także ironiczna innowacja o tworzywie sztucznym.
standaryzacyjny|R|wysoka|związany ze standaryzacją|Termin organizacyjno-techniczny w różnych dziedzinach.
geometrycznie|C|wysoka|według geometrycznego układu|Zwykły przysłówek opisu kształtu, zastosowany także do fryzury i planowania.
litologia|R|wysoka|skład i opis skał|Baza własna PIG potwierdza żywy termin geologiczny.
makabrycznie|C|wysoka|w sposób przerażający lub drastyczny|Zwykły przysłówek ekspresywny w kilku różnych tekstach.
kociarstwo|C|średnia|zbiorowo o kotach|WSJP potwierdza potoczne znaczenie zwierzęce. Nie utożsamiam go z pogardliwym żargonem wojskowym.
kluchowaty|C|średnia|mający konsystencję kluch lub ociężały|Zwykły potoczny opis jedzenia oraz przenośnia, bez oznak koniecznej archaizacji.
wypaleniskowy|R|wysoka|związany z rolnictwem wypaleniskowym|Opracowanie naukowe poświadcza techniczny opis systemu upraw; dawny referent nie oznacza martwego terminu.
przetrzepać|C|wysoka|pobić, przeszukać lub dotkliwie osłabić|Zwykłe potoczne użycia w kilku znaczeniach, zgodne z czasownikiem.
astronautyczny|R|wysoka|związany z lotami kosmicznymi|Przymiotnik dziedzinowy, używany także w publicystyce i przenośniach.
dias|M|wysoka|dawne określenie diabła|Cztery z pięciu wyników są obcojęzyczne; jeden jest archaizowanym przytoczeniem. Słownik staropolski potwierdza dawny sens.
weselisko|C|wysoka|ekspresywnie o weselu|Zwykła potoczna nazwa hucznego wesela; nie tylko odniesienia do dawnych obyczajów.
ketoza|R|wysoka|termin chemiczny lub metaboliczny|ZPE i NCEŻ potwierdzają oba zakresy. Brak live nie podważa aktualności terminu.
deklamatorski|R|wysoka|związany z deklamacją|Termin artystyczny i krytycznoliteracki; zgodne konteksty.
półomdlenie|C|średnia|stan bliski omdleniu|Przejrzysty opis samopoczucia w dwóch utworach, bez oznaki specjalistycznego terminu.
retortowy|R|wysoka|związany z urządzeniem retortowym|Jedyny kontekst dotyczy kotłów; techniczny przymiotnik, nie dowód innych sensów.
wędrowniczka|C|wysoka|kobieta wędrująca|Zwykła nazwa osoby, obok metafory o kartce. Męski homonim grupy nie został oceniony.
podbieg|R|wysoka|bieg pod górę lub odcinek takiego biegu|Żargon treningu biegowego, szerzej używany przez amatorów.
auszpik|R|średnia|potrawa w galarecie|Nazwa kulinarna w opisach wykwintnego menu; starsza kuchnia nie przesądza nieaktualności wyrazu.
krótkofalarstwo|R|wysoka|amatorska łączność radiowa|Nazwa współczesnego hobby; oba konteksty zapraszają do tej aktywności.
wołowaty|R|średnia|ociężały i powolny|Ekspresywna przenośnia w ocenie samochodu; ograniczony rejestr, lecz rzeczywiste użycie współczesne.
propedeutyczny|R|wysoka|wprowadzający do dalszej nauki|Termin dydaktyczny, także w formacji seminaryjnej i krytyce przekładu.
kontrapost|R|wysoka|układ postaci ze szczególnym rozłożeniem ciężaru|Termin historii sztuki rozszerzany na zwykły opis sylwetki.
zesypać|U|niska|zakres nieustalony|Notowanie morfologiczne nie rozstrzyga relacji do zsypać; nie uzyskano kontekstu pozwalającego ocenić współczesny zasięg.
porcik|C|wysoka|mały port|Zwykłe zdrobnienie w relacjach podróżniczych, trzy różne dokumenty.
sabejczyk|R|średnia|wyznawca religii sabejskiej|Publikacja UG potwierdza małoliterową nazwę wyznawcy. Grupa zawiera też wielkoliterową nazwę ludu, której nie wolno z nią utożsamiać.
pozapoetycki|R|wysoka|pozostający poza poezją|Termin opisu literatury i języka, trzy zgodne konteksty krytyczne.
nieporęczny|C|wysoka|niewygodny w użyciu|Zwykły przymiotnik; odczytane przenośnie dotyczą języka, bez potrzeby wąskiego rejestru.
etnometodologia|R|wysoka|nurt badania codziennych praktyk społecznych|Aktualny sylabus UJ potwierdza termin socjologiczny.
prawostronność|R|średnia|dominacja prawej strony|Materiały ORE i AWF potwierdzają termin lateralizacji; nie rozszerzam dowodu na wszystkie inne znaczenia.
argonowy|R|wysoka|związany z argonem|Techniczny przymiotnik poświadczony przy rodzaju lasera.
"""

# Tylko źródła rzeczywiście odczytane przez narzędzie web; zakres jest jawny.
SOURCES = {
 'lnica': [('https://www.ogrod.uw.edu.pl/en/baza-wiedzy/lnica-pospolita-2/', 'Ogród Botaniczny UW: Lnica pospolita', 'web_open', 'opis rośliny, linie 10–25')],
 'miodokwiat': [('https://wsjp.pl/haslo/podglad/66821/miodokwiat', 'WSJP: miodokwiat', 'web_search_extract', 'definicja botaniczna i nota o użyciu; ponowny open nie zwrócił strony')],
 'ostojowy': [('https://bip2.lasy.gov.pl/pl/bip/px_dg~rdlp_torun~pop_bydgoszcz.pdf', 'RDLP Toruń: program ochrony przyrody', 'web_search_extract', 's. 128, przymiotnik przy charakterze siedliska')],
 'pyrex': [('https://home.agh.edu.pl/~kakol/efizyka/w20/main20c.html', 'AGH: Kondensator z dielektrykiem', 'web_search_extract', 'nazwa rodzaju szkła w tabeli')],
 'obznajmiać': [('https://dobryslownik.pl/slowo/obznajomi%C4%87/33126/', 'Dobry słownik: obznajomić', 'web_search_extract', 'kwalifikacja przestarzałe/książkowe oraz dokładny odpowiednik niedokonany')],
 'regnowski': [('https://archiwum.bip.ugregnow.pl/PDF/GMINNA_STRATEGIA_ROZWIAZYWANIA_.PDF', 'Gmina Regnów: strategia społeczna', 'web_search_extract', 'fragment o ziemi regnowskiej, nie nazwisku')],
 'trzciański': [('https://trzciana.pl/30-lat-od-reaktywacji-gminy-trzciana', 'Gmina Trzciana: 30 lat od reaktywacji', 'web_open_find', 'tekst z 1.12.2024, akapit o frakcji trzciańskiej')],
 'prześmiardły': [('https://teatrtv.vod.tvp.pl/85912644/kalkwerk', 'TVP: Kalkwerk', 'web_search_extract', 'opis stanu bohatera spektaklu; nie datowanie powstania leksemu')],
 'grzbiecisty': [('https://wsjp.pl/haslo/podglad/110139/grzbiecista', 'WSJP: grzbiecista', 'web_search_extract', 'odrębny rzeczownik sportowy; źródło ostrzeżenia o grupowaniu, nie potwierdzenie przymiotnika')],
 'trójszereg': [('https://edziennik.policja.gov.pl/DU_KGP/2013/18/oryginal/Zalacznik.pdf', 'Policja: regulamin musztry', 'web_search_extract', 'punkt 77, definicja szyku')],
 'makiawelski': [('https://wsjp.pl/haslo/podglad/101329/makiaweliczny/5246953/wladca', 'WSJP: makiaweliczny — władca', 'web_search_extract_and_open', 'kwalifikator książkowy i relacja synonimii z dokładnym hasłem makiawelski')],
 'poprzekształcać': [('https://wsjp.pl/haslo/podglad/48872/poprzeksztalcac/5148079', 'WSJP: poprzekształcać — równania', 'web_search_extract', 'definicja, przykłady z NKJP i odmiana; dwie próby open nie zwróciły strony')],
 'autogen': [('https://eckert.com.pl/kompendium/zasada-dzialania-oraz-zastosowanie-palnika-acetylenowo-tlenowego-w-przemysle.html', 'Eckert: palnik acetylenowo-tlenowy', 'web_open_find', 'akapit o nazwie autogen, linie 53–57')],
 'sczerstwieć': [('https://wsjp.pl/haslo/podglad/107945/sczerstwiec/5257825/o-pieczywie', 'WSJP: sczerstwieć — o pieczywie', 'web_search_extract', 'definicja i przykłady zwykłego użycia')],
 'trójwładza': [('https://wsjp.pl/haslo/podglad/79912/trojwladza', 'WSJP: trójwładza', 'web_open', 'definicja i przykłady z różnych zakresów instytucjonalnych')],
 'eksplozywnie': [('https://www.ogrod.uw.edu.pl/en/baza-wiedzy/niecierpek-gruczolowaty-3/', 'Ogród Botaniczny UW: Niecierpek gruczołowaty', 'web_search_extract', 'własny opis otwierania owocu')],
 'sekserka': [('https://uwr.edu.pl/naukowcy/czym-sie-zajmujemy/beata-czyz-wszyscy-jestesmy-hipokrytami/', 'UWr: wywiad z Beatą Czyż', 'web_search_extract', 'wyjaśnienie roli osoby sprawdzającej płeć pisklęcia')],
 'mroczyć': [('https://wsjp.pl/haslo/podglad/82166/mroczyc/5204078/umysl', 'WSJP: mroczyć — umysł', 'web_search_extract', 'kwalifikacja książkowa, definicja i współczesne przykłady')],
 'emblemacik': [('https://jubileusz.grabski.edu.pl/zycie-szkoly/gazetka-szkolna', 'Zespół Szkół im. Grabskiego: Gazetka szkolna', 'web_open_find', 'Kleks 1999/2000, tekst o identyfikatorze, linie 814–837')],
 'wyzyskiwaczka': [('https://bip.amu.edu.pl/__data/assets/pdf_file/0026/655181/Wiejaczka-Elzbieta_Rozprawa-doktorska.pdf', 'UAM: rozprawa Elżbiety Wiejaczki', 'web_search_extract', 'fragment współczesnej rozprawy z nazwą kobiety wyzyskującej, w cytowanym opisie')],
 'kraulowy': [('https://www.spr3bielany.edu.pl/2010/04/11/bielanska-liga-plywacka/', 'SP nr 3: Bielańska Liga Pływacka', 'web_search_extract', 'własna relacja z zawodów z 2011 r.; nazwa stylu')],
 'przegrywarka': [('https://repozytorium.uwb.edu.pl/jspui/bitstream/11320/9554/1/BAJ_3_2003_B_Nowowiejski_rec_I_Bajerowa_Zarys_historii_jezyka_polskiego_1939-2000.pdf', 'B. Nowowiejski: recenzja z własnymi przykładami słowotwórczymi', 'web_search_extract', 's. 279, przykład nazwy urządzenia dodany przez autora recenzji')],
 'bednia': [('https://ruj.uj.edu.pl/server/api/core/bitstreams/cfde60f4-ead3-4068-8f82-adefe0bfcadf/content', 'LingVaria 2020 nr 2: analiza słowotwórstwa gwarowego', 'web_search_extract', 'omówienie bedni w materiale słownika gwary orawskiej')],
 'generatywność': [('https://czasopisma.uksw.edu.pl/fp/article/view/1339', 'K. Biel: Generatywność i jej przejawy w readaptacji społecznej skazanych', 'web_search_extract', 'abstrakt publikacji z 2017 r., definicja dziedzinowa')],
 'praojcowski': [('https://wsjp.pl/haslo/podglad/97838/praojcowski', 'WSJP: praojcowski', 'web_search_extract', 'definicja i przykłady; późniejszy open nie zwrócił strony')],
 'kaszany': [('https://wsjp.pl/haslo/podglad/100304/kaszany', 'WSJP: kaszany', 'web_search_extract_and_open', 'definicja, kulinarne przykłady i odróżnienie od rzeczownika kaszana')],
 'genotypowy': [('https://agro.icm.edu.pl/agro/element/bwmeta1.element.agro-article-83824604-5c3f-49b0-baf0-ade52f984926/c/3-9.PDF', 'Genetica Polonica 35A, 1994', 'web_search_extract', 'zastosowanie dokładnego przymiotnika w tekście naukowym')],
 'litologia': [('https://geostanowiska.pgi.gov.pl/515', 'PIG: Warstwy zakopiańskie w potoku Białym', 'web_search_extract', 'opis własny geostanowiska, pole litologia')],
 'kociarstwo': [('https://wsjp.pl/haslo/podglad/49410/kociarstwo/5148943/zwierzeta', 'WSJP: kociarstwo — zwierzęta', 'web_search_extract_and_open', 'potoczne znaczenie zbiorowe; odróżnione od sensu wojskowego')],
 'wypaleniskowy': [('https://ruj.uj.edu.pl/server/api/core/bitstreams/616c9d42-4ea9-4427-ae77-e90d7299f76a/content', 'Prace Geograficzne, zeszyt 123', 'web_search_extract', 'użycie o systemie upraw w badaniu przekształceń środowiska')],
 'dias': [('https://pjs.ijp.pan.pl/Sstp/Supl.pdf', 'IJP PAN: Słownik staropolski, suplement', 'web_search_extract', 's. 12, hasło Dias/Dyjas i dawny sens diabeł')],
 'ketoza': [('https://zpe.gov.pl/a/nazewnictwo-i-wzory-cukrow/DDMNQHFFB', 'ZPE: nazewnictwo i wzory cukrów', 'web_search_extract', 'sens chemiczny'), ('https://ncez.pzh.gov.pl/zdrowe-odchudzanie/dieta-ketogeniczna-w-swietle-badan-naukowych/', 'NCEŻ: Dieta ketogeniczna w świetle badań naukowych', 'web_search_extract', 'akapit o sensie metabolicznym; bez formułowania porad zdrowotnych')],
 'sabejczyk': [('https://czasopisma.bg.ug.edu.pl/index.php/cywilizacja/article/download/9434/8469/13383', 'R. Ożarowski: opis społeczności Iraku', 'web_search_extract', 's. 190, sabejczycy jako nazwa wyznawców; odrębne od etnonimu Sabejczycy')],
 'etnometodologia': [('https://sylabus.uj.edu.pl/pl/document/3783e5b3-400d-4c2e-8f21-459a22066d5f.pdf', 'UJ: sylabus Etnometodologia', 'web_search_extract', 'karta przedmiotu, cykl 2024/25 i cele kształcenia')],
 'prawostronność': [('https://ore.edu.pl/wp-content/uploads/phocadownload/6latek/przed_progiem_01_07_13.pdf', 'ORE: Przed progiem', 'web_search_extract', 'fragment o lateralizacji i dominacji strony ciała')],
}

# Kontrola dostępu po utrwaleniu pierwszych ocen. Nie zmienia macierzy ocen.
# Każdy wpis odpowiada kolejno adresom SOURCES[lemma]. Nie kopiuje treści źródła.
OPEN_AUDIT = {
 'lnica': [('read_fragment', 'Otwarta treść: opis rośliny, linie 10–25.')],
 'miodokwiat': [('failed', 'Dwie próby open dokładnego URL: Internal Error; ostatnia 12.10.2026. Definicję odczytano tylko jako indeksowany fragment wyniku.')],
 'ostojowy': [('failed', 'Open dokładnego PDF: Failed to fetch / Error fetching. Odczytano tylko indeksowany fragment s. 128.')],
 'pyrex': [('read_fragment', 'Otwarta treść: tabela 20.1, wiersz rodzaju szkła, linie 14–25.')],
 'obznajmiać': [('failed', 'Open dokładnego hasła obznajomić: Cache miss. Kwalifikator oraz odpowiednik niedokonany odczytano tylko w indeksowanym fragmencie.')],
 'regnowski': [('read_fragment', 'Otwarty PDF: s. 10, linie 297–307; lokalny przymiotnik w opisie historii gminy.')],
 'trzciański': [('read_fragment', 'Otwarta treść: artykuł z 1.12.2024, linie 78–103, akapit o frakcji trzciańskiej.')],
 'prześmiardły': [('empty_body', 'Open dokładnego URL TVP zwrócił tytuł i jedną pustą linię bez opisu spektaklu. Opis przeczytano tylko w indeksowanym fragmencie.')],
 'grzbiecisty': [('read_fragment', 'Otwarta treść: hasło rzeczownikowe grzbiecista, definicja i odmiana, linie 4–77. Nie jest to dowód przymiotnika grzbiecisty.')],
 'trójszereg': [('failed', 'Open dokładnego PDF Policji: Internal Error, bez treści. Definicję punktu 77 odczytano tylko jako indeksowany fragment.')],
 'makiawelski': [('read_fragment', 'Otwarta treść: hasło makiaweliczny, linie 9–39; kwalifikator książkowy dotyczy tego hasła, a dokładne makiawelski jest wskazanym synonimem. Dowód pośredni.')],
 'poprzekształcać': [('failed', 'Open URL bazowego: Cache miss; dwie próby URL znaczenia: Internal Error. Definicję, przykłady i odmianę odczytano tylko w indeksowanym fragmencie.')],
 'autogen': [('read_fragment', 'Otwarta treść producenta: akapit o nazwie autogen, linie 53–57.')],
 'sczerstwieć': [('read_fragment', 'Otwarta treść: definicja znaczenia o pieczywie, połączenia i przykłady, linie 1–27.')],
 'trójwładza': [('read_fragment', 'Otwarta treść: definicja i przykłady z różnych zakresów instytucjonalnych, linie 4–47.')],
 'eksplozywnie': [('read_fragment', 'Otwarta treść Ogrodu UW: opis owocu niecierpka, linie 38–46.')],
 'sekserka': [('read_fragment', 'Otwarta treść wywiadu UWr: opis zawodu i czynności, linie 157–160.')],
 'mroczyć': [('read_fragment', 'Otwarta treść: znaczenie umysł, kwalifikator książkowy, definicja i przykłady, linie 6–28.')],
 'emblemacik': [('read_fragment', 'Otwarta treść szkolnej gazety: Kleks 1999/2000, tekst o identyfikatorze, linie 814–837.')],
 'wyzyskiwaczka': [('read_fragment', 'Otwarty PDF: s. 117, linie 3707–3714; dokładna forma w tłumaczonym cytacie w rozprawie. Nie jest to niezależny pomiar popularności.')],
 'kraulowy': [('failed', 'Open dokładnego URL szkolnej relacji: Internal Error, bez treści. Odczytano tylko indeksowany fragment relacji z zawodów 2011 r.')],
 'przegrywarka': [('read_fragment', 'Otwarty PDF: s. 279, linie 124–133; własne przykłady słowotwórcze autora recenzji z 2003 r.')],
 'bednia': [('failed', 'Open dokładnego URL repozytorium UJ: Internal Error, bez treści. Odczytano tylko indeksowany fragment analizy materiału gwarowego.')],
 'generatywność': [('failed', 'Open dokładnego URL artykułu UKSW: Internal Error, bez treści. Odczytano tylko indeksowany abstrakt publikacji z 2017 r.')],
 'praojcowski': [('failed', 'Dwie próby open dokładnego hasła WSJP: Internal Error, bez treści. Definicję i przykłady odczytano tylko jako indeksowany fragment.')],
 'kaszany': [('read_fragment', 'Otwarta treść: definicja, związek z kaszą spożywczą i przykłady kulinarne, linie 4–29.')],
 'genotypowy': [('failed', 'Open dokładnego PDF AGRO: Internal Error, bez treści. Odczytano tylko indeksowany fragment tekstu Genetica Polonica 35A, 1994.')],
 'litologia': [('read_fragment', 'Otwarta karta PIG: pole litologia oraz opis geostanowiska, linie 61–72.')],
 'kociarstwo': [('read_fragment', 'Otwarta treść: potoczny sens zbiorowy zwierząt, definicja i przykłady, linie 6–23.')],
 'wypaleniskowy': [('failed', 'Open dokładnego URL repozytorium UJ: URL is not accessible via this tool. Odczytano tylko indeksowany fragment opisu systemu upraw.')],
 'dias': [('failed', 'Open dokładnego PDF IJP PAN: HTTP 502 Bad Gateway. Odczytano tylko indeksowany fragment hasła Dias/Dyjas, s. 12.')],
 'ketoza': [('read_fragment', 'Otwarta treść ZPE: podział monosacharydów i ketozy, linie 19–35.'), ('read_fragment', 'Otwarta treść NCEŻ: sekcja Czym jest ketoza?, linie 65–68. Wyłącznie rozróżnienie znaczeń, bez porad zdrowotnych.')],
 'sabejczyk': [('read_fragment', 'Otwarty PDF: s. 190, linie 189–201; sabejczycy jako określenie wspólnoty religijnej Mandejczyków.')],
 'etnometodologia': [('read_fragment', 'Otwarty PDF: s. 1–2, nazwa przedmiotu, cykl 2024/25 oraz cele kształcenia, linie 1–77.')],
 'prawostronność': [('read_fragment', 'Otwarty PDF: s. 46, linie 1322–1330 oraz słowniczek s. 69, linie 1927–1929; znaczenie lateralizacji.')],
}
FIRST_JSON_SHA256 = '4637c012da04f6c639fdf383c2cc822b1453ec5aeec90735195447edb491aaad'
FIRST_CREATED_AT = '2026-10-12T10:46:08.068074+00:00'
FROZEN_ASSESSMENT_SHA256 = 'c655914d7f9d0f43b90803a62124d9cf28a38c49e6255e3a0d30aef52f7735fa'

# Wszystkie wiersze poniższych haseł rzeczywiście odczytano dodatkowo.
EXPANDED = {'skarlić', 'ostawiać', 'uherski', 'kondygnacyjny', 'mroczyć', 'uziemienie', 'dias'}
# W innych przypadkach faktycznie przeczytano pierwszy wiersz każdego z maks. 3
# różnych dokumentów, wybranych spośród pierwszych 10 odpowiedzi.
OVERRIDES = {
 ('pies', 0): ('zgodne', 'Zwierzę; nie dowód homonimu osobowego ani derywatów grupy.'),
 ('skarlić', 0): ('niepewne', 'Gerundium; sam kontekst nie rozstrzyga sprawczego skarlić i niesprawczego skarleć.'),
 ('skarlić', 1): ('niepewne', 'Gerundium w opisie zmiany stanu; źródłowej podstawy nie rozstrzygnięto.'),
 ('skarlić', 2): ('niepewne', 'Gerundium przy degradacji; niepełny dowód czasownika sprawczego.'),
 ('skarlić', 3): ('zgodne', 'Sprawczy sens ograniczenia znaczenia mediów; forma rzeczownikowa czasownika.'),
 ('skarlić', 4): ('niepewne', 'Gerundium; proces lub działanie sprawcze nie są tu rozdzielone.'),
 ('skarlić', 5): ('niepewne', 'Samodzielny rzeczownikowy opis degradacji; podstawa czasownikowa niejednoznaczna.'),
 ('skarlić', 6): ('niepewne', 'Gerundium przy utracie prestiżu, możliwa zmiana stanu.'),
 ('skarlić', 7): ('niepewne', 'Adnotacja subst przy lemacie czasownika; kontekst nie identyfikuje podstawy.'),
 ('skarlić', 8): ('niepewne', 'Gerundium przy moralnej degradacji; niepełne rozróżnienie podstawy.'),
 ('ostawiać', 0): ('niepewne', 'Zapis może reprezentować wariant lub błąd zamiast zostawiać.'),
 ('ostawiać', 1): ('niepewne', 'Zapis może reprezentować stylizację lub ubytek litery w zostawiać.'),
 ('ostawiać', 2): ('zgodne_stylizacja', 'Wyraźnie gwarowy otaczający tekst.'),
 ('ostawiać', 3): ('zgodne_stylizacja', 'Archaizowany dialog w konwencji fantasy.'),
 ('powroźniczy', 0): ('ograniczone_nazwa', 'Człon nazwy firmy; sam nie dowodzi swobodnego użycia.'),
 ('kot', 0): ('ograniczone_tytul', 'Tytuł książki, z leksykalnym znaczeniem zwierzęcym.'),
 ('kot', 2): ('zgodne_frazeologia', 'Frazeologizm; nie odrębny homonim osobowy.'),
 ('uherski', 0): ('niezgodne', 'Człon nazwy Uherský Brod; adnotacja ne/placeName_settlement potwierdza nazwę własną.'),
 ('kondygnacyjny', 1): ('czesciowe_segmentacja', 'Człon przymiotnika z zapisem liczbowym; brak samodzielnego użycia.'),
 ('kondygnacyjny', 2): ('czesciowe_segmentacja', 'Oddzielony od liczby człon złożenia; niepełny dowód samodzielnego hasła.'),
 ('kondygnacyjny', 3): ('czesciowe_segmentacja', 'Oddzielony od liczby człon złożenia.'),
 ('kondygnacyjny', 4): ('czesciowe_segmentacja', 'Oddzielony od liczby człon złożenia, ten sam dokument i zdanie co poprzedni.'),
 ('kurant', 0): ('ograniczone_nazwa', 'Nazwa kawiarni; pozostałe konteksty dają samodzielne użycie.'),
 ('mroczyć', 0): ('zgodne_cytat', 'Poetyckie przytoczenie; nie dowód bieżącej mowy.'),
 ('mroczyć', 1): ('zgodne_cytat', 'Poetyckie przytoczenie.'),
 ('mroczyć', 3): ('zgodne_cytat', 'Przytoczenie poetyckie.'),
 ('mroczyć', 4): ('zgodne_cytat', 'Przytoczenie poetyckie.'),
 ('mroczyć', 7): ('ograniczone_tytul', 'Powtarzany tytuł utworu.'),
 ('mroczyć', 8): ('ograniczone_tytul', 'Powtarzany tytuł tego samego utworu.'),
 ('mroczyć', 9): ('ograniczone_tytul', 'Powtarzany tytuł tego samego utworu.'),
 ('mężobójczy', 0): ('zgodne_stylizacja', 'Literacka archaizacja; nie samoistny dowód zwykłego rejestru.'),
 ('powschodzić', 0): ('zgodne_cytat', 'Cytat biblijny, sens kiełkowania.'),
 ('uziemienie', 0): ('niepewne', 'Wąska konkordancja nie wystarcza do ustalenia dokładnego sensu organizowanego uziemienia.'),
 ('uziemienie', 1): ('zgodne_metafora', 'Przenośnia w wywodzie literackim.'),
 ('uziemienie', 2): ('zgodne', 'Zwykłe ograniczenie możliwości poruszania się.'),
 ('uziemienie', 3): ('zgodne', 'Znaczenie elektrycznej instalacji ochronnej.'),
 ('uziemienie', 4): ('zgodne_metafora', 'Kontakt ciała z podłożem w opisie tańca.'),
 ('uziemienie', 5): ('zgodne', 'Element wyposażenia ochronnego urządzenia.'),
 ('uziemienie', 6): ('zgodne', 'Przenośnie o wymuszonym bezruchu.'),
 ('uziemienie', 7): ('zgodne', 'Unieruchomienie w podróży lotniczej.'),
 ('omlecik', 1): ('ograniczone_tytul', 'Żartobliwe nazwanie utworu; nie dowód potrawy.'),
 ('psychoonkologia', 0): ('ograniczone_nazwa', 'Nazwa fundacji, zawierająca nazwę dyscypliny.'),
 ('psychoonkologia', 3): ('ograniczone_nazwa', 'Nazwa poradni, zawierająca nazwę dyscypliny.'),
 ('dias', 0): ('niezgodne', 'Portugalski wyraz w tytule; adnotacja xxx/ne_foreign.'),
 ('dias', 1): ('niezgodne', 'Portugalski wyraz w tytule; adnotacja xxx/ne_foreign.'),
 ('dias', 2): ('niezgodne', 'Obcojęzyczny tytuł książki; nie polski rzeczownik.'),
 ('dias', 3): ('zgodne_stylizacja', 'Archaizowane przytoczenie z sensem diabła; nie dowód bieżącej zwykłej mowy.'),
 ('dias', 4): ('niezgodne', 'Hiszpańskie powitanie; adnotacja xxx/ne_foreign.'),
 ('wędrowniczka', 1): ('zgodne_metafora', 'Przenośne użycie nazwy wędrującej osoby o kartce.'),
}

CLASSES = {'C': 'ogólne', 'R': 'ograniczone', 'M': 'marginalne', 'X': 'błędne_dopasowanie', 'U': 'niepewne'}

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    inputs = json.loads(INPUT.read_text())['cases']
    raw = {x['id']: x for x in json.loads(CACHE.read_text())}
    notes = {}
    for line in NOTES.strip().splitlines():
        lemma, cat, conf, sense, reason = line.split('|')
        assert lemma not in notes
        notes[lemma] = (CLASSES[cat], conf, sense, reason)
    assert len(notes) == len(inputs) == 150
    assert set(notes) == {x['lemma'] for x in inputs}
    output = []
    source_audit = []
    for case in inputs:
        r = raw[case['id']]
        assert r['lemma'] == case['lemma'] and r['status'] == 'read'
        cls, conf, sense, reason = notes[case['lemma']]
        selected, seen = [], set()
        for index, row in enumerate(r['rows'][:10]):
            if case['lemma'] in EXPANDED or (row['document_id'] not in seen and len(seen) < 3):
                selected.append((index, row))
                seen.add(row['document_id'])
        contexts = []
        for index, row in selected:
            match, note = OVERRIDES.get((case['lemma'], index), ('zgodne', f'Odczyt zgodny z zakresem: {sense}.'))
            contexts.append({'row_index': index, 'document_id': row['document_id'], 'sentence': row['sentence'], 'document_date': row['date'], 'sense_match': match, 'note': note})
        refs = [{'url': a, 'title': b, 'access': c, 'read_scope': d, 'accessed': '2026-10-12'} for a,b,c,d in SOURCES.get(case['lemma'], [])]
        audited_refs = []
        sources = SOURCES.get(case['lemma'], [])
        audit = OPEN_AUDIT.get(case['lemma'], [])
        assert len(sources) == len(audit)
        for (url, title, initial_access, initial_scope), (status, scope) in zip(sources, audit):
            audited_refs.append({'url': url, 'title': title,
                'access': 'web_open_fragment' if status == 'read_fragment' else 'web_search_extract_open_failed',
                'read_scope': scope, 'accessed': '2026-10-12',
                'first_assessment_access': initial_access, 'first_assessment_read_scope': initial_scope,
                'open_attempt': {'date': '2026-10-12', 'url': url, 'status': status, 'result': scope},
                'local_cache': False})
        if audited_refs:
            source_audit.append({'id': case['id'], 'lemma': case['lemma'], 'sources': audited_refs})
        output.append({
            'id': case['id'], 'lemma': case['lemma'], 'class': cls, 'confidence': conf,
            'sense_reviewed': sense, 'reason': reason,
            'input_evidence_refs': [{'key': e['key'], 'pos': e['pos'], 'group_members': e['group_members'], 'kwjp_own_status': e['kwjp_own']['status'], 'kwjp_own_row': e['kwjp_own']['row'], 'kwjp_group_row': e['kwjp_group']['row'], 'nkjp_own_status': e['nkjp_own_status']} for e in case['evidence']],
            'original_kwjp_rows': case['original_kwjp_rows'],
            'kwjp_live': {'query_url': r['url'], 'response_sha256': r['response_sha256'], 'access_status': r['status'], 'search_reported_total': r['total'], 'reported_total_is_exact_frequency': False, 'returned_rows': len(r['rows']), 'read_context_count': len(contexts), 'read_distinct_documents': len(seen), 'contexts': contexts, 'zero_result_is_nonexistence': False},
            'external_sources': refs,
            'evidence_limit': 'Przeczytano wyłącznie wskazane konkordancje i fragmenty źródeł; ocena nie obejmuje automatycznie wszystkich sensów ani członków grupy.',
        })
    counts = Counter(x['class'] for x in output)
    frozen_core = [{k: x[k] for k in ['id', 'lemma', 'class', 'confidence', 'sense_reviewed', 'reason', 'kwjp_live']} for x in output]
    core_sha = hashlib.sha256(json.dumps(frozen_core, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
    assert core_sha == FROZEN_ASSESSMENT_SHA256, 'Macierz pierwszych ocen musi pozostać zamrożona.'
    summary = {'cases': len(output), 'classes': dict(counts), 'live_contexts_read': sum(x['kwjp_live']['read_context_count'] for x in output), 'cases_with_live_context_read': sum(bool(x['kwjp_live']['contexts']) for x in output), 'zero_live_results': sum(x['kwjp_live']['returned_rows'] == 0 for x in output), 'live_access_errors': 0, 'cases_with_external_source': sum(bool(x['external_sources']) for x in output)}
    access_counts = dict(Counter(s['access'] for x in source_audit for s in x['sources']))
    doc = {
        'reviewer': '/root/family_review', 'round': 5, 'lane': 'A',
        'assessment_frozen_before_unblinding': True, 'created_at': FIRST_CREATED_AT,
        'input': {'path': str(INPUT.relative_to(ROOT)), 'sha256': sha(INPUT)},
        'private_context_cache': {'path': str(CACHE.relative_to(ROOT)), 'sha256': sha(CACHE)},
        'method': [
            'Pierwsze oceny utrwalone przed odczytem sample-design, measurements, rankingu, membership i ocen innych reviewerów.',
            'Ocenia osobny reviewer-agent; nie jest to niezależność statystyczna, ekspert ludzki ani badanie znajomości słów przez graczy.',
            'W każdym haśle przeczytano pierwszy kontekst z maksymalnie trzech różnych dokumentów wśród pierwszych dziesięciu wyników; siedem oznaczonych haseł rozszerzono do wszystkich zwróconych wierszy.',
            'Wybrane teksty są celowo dobranymi dowodami. Nie są losową próbą kontekstów; kolejność wyników może nadreprezentować książki.',
            'Klasy opisują ocenę przydatności leksykalnej dla szerokiego POP. Ograniczone oznacza termin, rejestr książkowy lub zakres lokalny, nie automatyczne wykluczenie.',
            'Zwykłe produktywne derywaty i kolokwializmy mogą być ogólne. Nazwa procesu historycznego może pozostawać współczesnym terminem.',
            'Brak live to odpowiedź read z zerem wyników, nigdy samodzielny dowód nieistnienia, dawności ani braku znajomości.',
            'Total live jest liczbą zgłoszoną przez wyszukiwarkę, nie dokładną częstością. Oryginalne wiersze KWJP zachowano bez agregowania F i ARF.',
            'Data dokumentu pochodzi z metadanych; może oznaczać wydanie wcześniejszego tekstu, zwłaszcza w cytatach.',
            'Źródła web odczytano jako wskazane fragmenty wyników lub stron. Nie pobierano ich do lokalnego cache; nie deklaruje się pełnej lektury publikacji.',
            'Artefakt zawiera własne oceny, metryki i identyfikatory; nie zawiera surowych konkordancji ani cytatów korpusu.',
        ],
        'summary': summary, 'cases': output,
    }
    first_bytes = (json.dumps(doc, ensure_ascii=False, indent=2) + '\n').encode()
    assert hashlib.sha256(first_bytes).hexdigest() == FIRST_JSON_SHA256
    (OUT / 'quality-a.json').write_bytes(first_bytes)
    access_doc = {
        'reviewer': '/root/family_review', 'round': 5, 'lane': 'A',
        'created_at': datetime.now(timezone.utc).isoformat(),
        'frozen_matrix': {'path': 'quality-a.json', 'first_sha256': FIRST_JSON_SHA256, 'current_sha256': sha(OUT / 'quality-a.json'), 'assessment_sha256': core_sha, 'unchanged': True},
        'scope': 'Po utrwaleniu ocen podjęto próbę otwarcia każdego uzupełniającego źródła. Zapis rozdziela otwarty właściwy fragment i sam indeksowany fragment po nieudanym open. Bez lokalnego cache i bez deklaracji pełnej lektury publikacji. Klasy, pewności, uzasadnienia i 316 konkordancji bez zmian; nadal bez rankingu ani ocen innych reviewerów.',
        'summary': {'cases': len(source_audit), 'source_urls': sum(len(x['sources']) for x in source_audit), 'access': access_counts},
        'cases': source_audit,
    }
    (OUT / 'quality-a-source-access.json').write_text(json.dumps(access_doc, ensure_ascii=False, indent=2) + '\n')
    lines = ['# Runda 5 — ślepa ocena leksykalna A', '', '## TL;DR', '',
        f'Oceniono wszystkie 150 haseł przed ujawnieniem rang i składu POP. Odczytano {summary["live_contexts_read"]} konkordancji dla {summary["cases_with_live_context_read"]} haseł; {summary["zero_live_results"]} zapytań zwróciło zero wyników, bez błędów dostępu. Źródła pierwotne uzupełniły {summary["cases_with_external_source"]} ocen.', '',
        ' | '.join(f'{k}: **{v}**' for k,v in counts.items()) + '.', '',
        '## Key Decisions', '',
        '- Oceniono słowo i odczytany sens, bez automatycznego przenoszenia frekwencji rodziny na jej członków. Klasa „ograniczone” nie jest decyzją o wykluczeniu z POP.',
        '- „Uherski”: jedyne trafienie jest członem nazwy miejscowej. „Dias”: cztery trafienia obcojęzyczne i jedno archaizowane. „Kondygnacyjny”: cztery z pięciu trafień to segmenty złożeń z liczbą.',
        '- „Skarlić”: wszystkie dziewięć trafień ma formę rzeczownikową; większość nie rozstrzyga podstawy skarlić/skarleć. Jedno daje sens sprawczy. To słaby dowód popularności pełnego czasownika.',
        '- Brak live nie obniżał automatycznie oceny: źródła potwierdzają m.in. kaszany, poprzekształcać i kociarstwo oraz terminy lnica, litologia, autogen i sekserka.',
        '- Do trzech różnych dokumentów na hasło wybrano spośród pierwszych dziesięciu. Dodatkowo przeczytano wszystkie dostępne wiersze siedmiu spornych haseł. JSON podaje każdy przeczytany dokument, sentence, ocenę zgodności i hash odpowiedzi.', '',
        '## Open Questions / Risks', '',
        '- Niepewne: ' + ', '.join(x['lemma'] for x in output if x['class'] == 'niepewne') + '. Nie są automatycznie odrzucone.',
        '- To przegląd przez osobnego agenta, nie badanie rozpoznawalności wśród graczy ani niezależna ekspertyza człowieka. Granica ogólne/ograniczone jest oceną redakcyjną.',
        '- Pierwsze wyniki wyszukiwarki nadreprezentują niektóre dokumenty. Odczyt obejmuje wybrane konkordancje, nie całe utwory. Daty wydań nie gwarantują współczesności cytowanej wypowiedzi.',
        '- Liczby total live nie są dokładnymi F. Oryginalne metryki KWJP i członków grup zachowano osobno. Żadnego rankingu ani progu POP tu nie oceniono.',
        '- Podjęto próbę otwarcia wszystkich 36 adresów uzupełniających: ' + str(access_counts.get('web_open_fragment', 0)) + ' dało odczyt właściwego fragmentu, a ' + str(access_counts.get('web_search_extract_open_failed', 0)) + ' pozostało wyłącznie indeksowanym fragmentem po błędzie lub pustej odpowiedzi. [Audyt dostępu](quality-a-source-access.json) podaje każdy wynik; samego snippetu nie uznano za otwarcie tekstu.',
        '- Oceny zamrożono przed tym audytem dostępu. Hash pierwszego JSON: `' + FIRST_JSON_SHA256 + '`. Kontrola skrótu osobno potwierdza brak zmian 150 ocen i zakresu KWJP.', '',
        '| Hasło | Ocena | Pewność | KWJP: odczyt / dokumenty | Uzasadnienie |', '|---|---|---|---:|---|']
    for x in output:
        k = x['kwjp_live']
        refs = ' '.join(f'[{s["title"]}]({s["url"]})' for s in x['external_sources'])
        reason = x['reason'] + (f' {refs}' if refs else '')
        lines.append(f'| [{x["lemma"]}]({k["query_url"]}) | {x["class"]} | {x["confidence"]} | {k["read_context_count"]} / {k["read_distinct_documents"]} | {reason} |')
    lines += ['', 'Pełne identyfikatory i zakres odczytu: [quality-a.json](quality-a.json). Surowe konteksty pozostają w ignorowanym cache.']
    (OUT / 'quality-a.md').write_text('\n'.join(lines) + '\n')
    print(json.dumps(summary, ensure_ascii=False))
    print('quality-a.json sha256:', sha(OUT / 'quality-a.json'))

if __name__ == '__main__':
    main()
