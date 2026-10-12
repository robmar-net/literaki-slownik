"""Utrwalenie ślepych ocen badacza B; nie jest automatycznym klasyfikatorem.

Czyta wyłącznie próbkę blind-b i pobrane dla niej konteksty. Nie odczytuje
rankingu, progów, przynależności ani ocen drugiego badacza. Konteksty pozostają
w ignorowanym cache; raport zawiera własne adnotacje i metadane.
"""
import hashlib
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

TASK = Path(__file__).resolve().parents[1]
ROOT = TASK.parents[3]
OUT = TASK / 'analysis/findings/round5'
INPUT = OUT / 'sample-blind-b.json'
CONTEXTS = ROOT / 'tmp/research-issue4/round5/contexts-b-raw.json'

# Ręczne oceny po lekturze. G=ogólne, O=ograniczone, M=marginalne,
# B=błędne dopasowanie dowodu, N=niepewne. Pewność dotyczy oceny klasy,
# nie odsetka graczy znających słowo.
ASSESSMENTS = '''przedryndać|O|średnia|WSJP potwierdza ekspresywne przejechanie trasy i telefonowanie; brak live kontekstu nie unieważnia słowa. Rejestr potoczny, nienacechowane użycie ogólne nieudokumentowane tutaj.
dekagram|G|wysoka|Zwykła miara masy w opisach ilości; osobny rzeczownik ma 24 wystąpienia w tabeli. Skróty tworzą odrębną warstwę 61, której nie wolno utożsamiać z częstością pełnego wyrazu.
pomiaukiwać|G|wysoka|Trzy nowe narracje opisują wydawanie odgłosów przez koty. Zwykły opis czynności, mimo braku opublikowanego własnego wiersza.
margarynowy|G|średnia|Przymiotnik od codziennego produktu; kontekst części przedsiębiorstwa związanej z margaryną potwierdza sens. Jedna próbka ogranicza pewność zasięgu.
mszyć|B|wysoka|Oba trafienia mają postać mszył tam, gdzie relacja piłkarska wymaga ruszył. Duża grupa z msza nie jest dowodem żywotności czasownika mszyć.
transkrypcyjny|O|wysoka|Kontekst metod zapisu badań potwierdza termin zawodowy/naukowy, nie zwykły szeroki opis.
odbąknąć|G|wysoka|W trzech dialogach oznacza krótką niechętną odpowiedź. Ekspresywny, lecz zwykły czasownik codziennej komunikacji.
hoja|O|wysoka|Dwa dokumenty dotyczą rośliny ozdobnej; właściwe użycia nazwy ogrodniczej. Nie są dowodem nazw własnych mimo flagi źródła.
podminować|G|wysoka|Przenośne destabilizowanie i zdenerwowanie człowieka są czytelne w różnych tekstach; nie ogranicza się do saperstwa.
biseks|O|wysoka|Trzy polskie użycia nazwy osoby biseksualnej; skrócona potoczna nazwa, nie błąd ani archaizm.
pilarz|G|średnia|Osiem z pierwszych dziesięciu trafień wspiera nazwę zawodu, dwa dotyczą nazwiska. To wsparcie pilarz:Sm1; homonim pilarz:Sm2 pozostaje niepotwierdzony.
fermentownia|O|niska|Budowa nazwy wskazuje pomieszczenie lub dział procesu fermentacji, więc zastosowanie branżowe. To wstępna ocena semantyczna; 0 live i brak wiersza nie ustalają faktycznego zasięgu.
nieruchawość|G|wysoka|Trzy teksty używają zwykłej nazwy cechy małej ruchliwości; nie trzeba specjalistycznej dziedziny, aby uzasadnić jej przydatność.
wirusowość|O|średnia|Jedyny kontekst dotyczy szybkiego rozpowszechniania informacji w sieci. Potwierdza termin komunikacji medialnej, nie całą potencjalną wieloznaczność.
zgorzknialec|G|niska|Przejrzysta nazwa osoby zgorzkniałej nadaje się do zwykłego opisu człowieka. Ocena językowa bez znalezionego live użycia; brak nie jest dowodem nieistnienia.
niebieskawo|G|wysoka|Trzy teksty opisują barwę światła lub zmiany skórnej. Samodzielny przysłówek, a nie tylko człon złożenia.
obrączkować|O|wysoka|Znakowanie zwierząt ma wąską praktykę przyrodniczą; jeden kontekst przenosi czynność na zakuwanie człowieka. Sens zgodny, nie sam dźwięk napisu.
siejba|M|wysoka|WSJP: dawne określenie siewu. Osiem z dziewięciu kontekstów to poezja/przytoczenia, jeden to współczesna stylizowana powieść. Nie jest to brak użyć, lecz wyraźne ograniczenie chronologiczno-stylistyczne.
amperomierz|O|wysoka|Właściwa nazwa przyrządu w obwodzie elektrycznym. Termin szkolny/techniczny może należeć do szerokiego POP mimo tej klasy.
kurara|O|wysoka|Trzy konteksty dotyczą trucizny, także w porównaniu. Nazwa specjalnego desygnatu obecna w prozie, nie przypadkowy ciąg liter.
pedancik|G|niska|Regularne ekspresywne zdrobnienie nazwy osoby pedantycznej. Ocena przydatności opiera się na budowie i rozumieniu, bo live nie dostarczył kontekstu.
niemelodyjny|G|niska|Zwykłe przeczące określenie braku melodyjności. Brak kontekstu pozostawia otwarty zasięg użycia, nie czyni słowa marginalnym.
portowiec|G|wysoka|Trzy użycia nazwy pracownika portu w tekstach o życiu i pracy ludzi. Bez pomylenia z nazwą drużyny.
ryba|G|wysoka|Zwykły rzeczownik o zwierzęciu i żywności oraz utrwalona przenośnia o ważnych osobach; dowód zgodny.
siedmiogodzinny|G|wysoka|Przejrzyste określenie czasu rozmowy, spektaklu i płaczu; różne zwykłe sytuacje, nie termin.
wywiadowczyni|O|średnia|Wszystkie dostępne trafienia pochodzą z jednego artykułu pszczelarskiego o pszczołach rozpoznających miejsca. Nie potwierdza to szerokiego użycia nazwy kobiety działającej w wywiadzie.
spotwornieć|G|wysoka|Trzy odrębne teksty opisują przerażającą zmianę rzeczy, organu lub rynku pracy. Grupa ze spotwornić nie zastępuje własnego dowodu.
pozakomórkowy|O|wysoka|Kontekst macierzy poza komórką potwierdza termin biologiczny/medyczny.
kikować|O|wysoka|Kontekst podziału łupu wskazuje obserwowanie/stanie na czatach. Pierwotne opracowanie UJK potwierdza także nowe użycie internetowe usuwania z gry/grupy; nie należy ich zlewać.
marudnie|G|średnia|Przysłówek zwykłej cechy sposobu działania, w poetyckim opisie budzenia. Jeden literacki kontekst nie mierzy znajomości słowa.
limfocytowy|O|wysoka|Trzy konteksty dotyczą nazwy białaczki. Precyzyjny termin medyczny, również używany w prasie ogólnej.
niebotyczność|O|średnia|Jedyne użycie to abstrakcyjny, podniosły opis wszechrzeczy. Potwierdzony rzeczownik, lecz dowód ma wyraźny rejestr literacki.
kozeta|N|niska|Dawny słownik Arcta potwierdza nazwę mebla. Nie znaleziono live kontekstu i nie rozstrzygnięto współczesnego zakresu wobec kozetka oraz homonimicznej nazwy osoby.
bezgłos|O|wysoka|Trzy poprawne użycia oznaczają ciszę/brak głosu w opisach literackich i eseistycznych; rejestr książkowy.
chłoporobotnik|O|wysoka|Współczesne teksty opisują określoną grupę społeczno-zawodową, często historycznie. Termin społeczny nie staje się nieistniejący wskutek historycznego desygnatu.
żelatynowy|G|średnia|Zwykły przymiotnik materiałowy, poświadczony przy kapsułkach i folii oraz przedsiębiorcy. Specjalność przedmiotów nie zmienia każdego użycia w osobny termin.
repetytorium|G|wysoka|Prawidłowe użycia szkolne i powtórzeniowe obok trzech najpewniej błędnych zapisów repertorium w kancelarii/tłumaczeniach. Słowo pozostaje ogólne, dowód wymaga odszumienia.
konklawista|O|średnia|Autorski tekst Przewodnika Katolickiego używa nazwy uczestnika konklawe, choć live daje 0. Termin religijno-historyczny, nie ocena wieku samego wyrazu.
ścieżyna|O|średnia|Dwa pierwsze dokumenty zawierają literackie przytoczenia, trzeci bieżący opis drogi u Wilka. Zdrobnienie o rejestrze książkowym, nie błędne dopasowanie.
wypełzły|O|średnia|Dwa cytowane opisy oczu/brwi odpowiadają przymiotnikowi wyblakły. Wąski literacki dowód; nie wspiera go automatycznie częsty czasownik wypełznąć.
nieczłowieczy|O|wysoka|Trzy użycia podniosłe lub literackie, w tym poetycki cytat. Znaczenie jest czytelne, ale nie neutralny codzienny rejestr.
lobować|O|wysoka|Wszystkie wybrane konteksty opisują sportowe zagranie piłki nad przeciwnikiem. Nie mylić z lobbować.
koniunktiwus|O|średnia|Dwa konteksty jednego reportażu przywołują formę koniunktiwu, z czego jeden żartobliwie. Termin gramatyczny; dowód lemmatyzacji nie wyznacza zasięgu ogólnego.
rowerzystka|G|wysoka|Zwykła nazwa osoby jadącej rowerem, poświadczona w trzech sytuacjach życia codziennego.
opierdzielać|O|wysoka|Trzy konteksty potwierdzają wyraźnie potoczny/wulgarny rejestr reprymendy i innego działania. Ograniczenie rejestrem nie oznacza automatycznego wykluczenia.
hetmanić|O|średnia|Jeden kontekst literackiego przytoczenia i drugi współczesnej historiozoficznej narracji opisują przewodzenie. Grupa z hetman nie dowodzi szerokiej częstości czasownika.
harmonogramować|O|niska|Semantycznie czasownik planowania prac według harmonogramu, o profilu zawodowym. 0 live; ocena wstępna, nie zmierzona częstość.
szyfonowy|G|wysoka|Różne teksty opisują zwykłe przedmioty wykonane z tkaniny: sztandar, pelerynę, kokardę. Nie wymaga specjalnego kontekstu fachowego.
odmoczyć|G|wysoka|Trzy konteksty zwykłej czynności moczenia ciała lub przedmiotów. Brak opublikowanego wiersza nie oznacza braku użycia.
wiroid|O|wysoka|ZPE i PIORiN potwierdzają rzeczywistą nazwę biologicznego czynnika chorób roślin. Live 0 przy pozytywnym źródle dziedzinowym.
dupowaty|O|wysoka|Dwa dokumenty używają obraźliwego potocznego określenia niezaradności/poddańczości. Rejestr ograniczony, dowód właściwy.
naskubać|G|niska|Przejrzysty czasownik zebrania przez skubanie; proponowana klasa ogólna jest oceną językową, nie wynikiem pomiaru znajomości. Live 0.
ujeździć|O|wysoka|Dwa użycia dotyczą przysposobienia zwierzęcia do jazdy, trzecie formy nieujeżdżony. Własne poświadczenia istnieją; dziedzina jeździecka.
podrzemać|G|wysoka|Trzy zwykłe konteksty krótkiego odpoczynku/snu; produktywne codzienne użycie czasownika.
wiwera|O|wysoka|WSJP potwierdza nazwę zoologiczną i przytacza użycie prasowe z 2020 r. Live 0 nie uprawnia do marginalizacji.
jedyność|O|wysoka|Trzy abstrakcyjne użycia eseistyczne/literackie; prawidłowa nazwa cechy, wyraźnie książkowa.
szampiter|O|średnia|Opracowanie językoznawcze dokumentuje dawną żartobliwą nazwę szampana, a słownik powiatu poznańskiego regionalne szampon. Potrzebne rozdzielenie znaczeń; live 0 nie uzasadnia automatycznego odrzucenia obu.
poszeregować|G|średnia|Dwa konteksty układania myśli i materiałów według cech; zwykła zrozumiała czynność, bez wymaganego żargonu.
koronawirus|G|wysoka|W trzech tekstach ogólnych opisuje pandemię i codzienne ograniczenia. Pochodzenie biologiczne nie ogranicza jego współczesnego rejestru do biologów.
okruchowy|O|niska|Przymiotnik o prawdopodobnym zastosowaniu materiałowym/geologicznym; bez live kontekstu zasięg pozostaje słabo rozpoznany. Nie przypisuję marginalności za sam brak.
deminutywny|O|wysoka|Wszystkie siedem trafień pochodzi z jednego tekstu językoznawczego: pięć przymiotników i dwa człony adja. Właściwy termin, lecz nie siedem niezależnych świadectw.
anyżowy|G|wysoka|Trzy konteksty smaków cukierków i napojów; zwykły przymiotnik kulinarny.
ćwierćnuta|O|średnia|Kontekst metaforyczny zachowuje znaczenie muzycznej wartości nuty. Termin szkolny może być przydatny w szerokim POP.
niecelność|G|średnia|Zwykła nazwa braku celności w narracji. Jedno poświadczenie nie wystarcza do pomiaru rozpowszechnienia, lecz nie wskazuje dziedziny specjalnej.
zaważać|G|wysoka|Dwa z trzech kontekstów poprawnie opisują wpływ na życie/decyzję. Trzeci to zapewne uszkodzone zauważa; nie wolno liczyć go jako poprawnego użycia.
podjarać|O|wysoka|Trzy konteksty ekscytacji, w tym reportaż i popularyzacja nauki. Potoczne znaczenie żywe, niezależne od dosłownego rozpalania.
niereligijny|G|wysoka|Zwykły przymiotnik opisujący przyczyny, ideologię i wierzenia; różne konteksty społeczne.
gatunkować|O|niska|Czasownik klasyfikowania według gatunku/klasy ma profil zawodowy. Brak live pozostawia użycie bez potwierdzenia w tej próbie.
dotaszczyć|G|wysoka|Trzy narracje opisują przemieszczenie człowieka lub zakupów z wysiłkiem; zwykły czasownik.
dolomitowy|O|wysoka|Dwa konteksty dotyczą skały i pyłu w badaniu technicznym. Właściwy przymiotnik mineralogiczny/materiałowy.
bezołowiówka|G|wysoka|Dwa teksty prasowe o cenie i zużyciu paliwa potwierdzają codzienną potoczną nazwę benzyny bezołowiowej; bez wąskiego żargonu grupy.
mirakl|O|wysoka|Dwa teksty dotyczą historycznego gatunku widowiska i inspiracji muzycznej. Żywy termin historii kultury, nie dowód archaizacji narracji.
rozplatać|G|wysoka|Literalne rozplatanie włosów i metafory wyjaśniania związków/zdarzeń; zwykłe użycie w różnych tekstach.
lunonauta|O|średnia|Autorski artykuł Uranii używa nazwy uczestnika wyprawy księżycowej; 0 live nie oznacza nieistnienia. Wąski termin astronautyczny.
roztrzepotać|O|średnia|Trzy obrazowe użycia imiesłowu przy skrzydłach, sercu i dłoniach. Rejestr literacki; nie dowód wszystkich form czasownika.
kooperatyzm|O|wysoka|Trzy teksty o współdziałaniu/spółdzielczości i ideach społecznych. Prawidłowy termin społeczno-ekonomiczny.
sansara|O|wysoka|Dwa teksty objaśniają religijny cykl narodzin i śmierci. Dodatni dowód specjalnego słownictwa religijnego.
ławkowiec|O|średnia|Kontekst pracy malarskiej zestawia duże narzędzia z cienkimi; odpowiada nazwie pędzla. Jeden literacki przykład, specjalne narzędzie.
rozminowywać|G|wysoka|Dwa dosłowne opisy usuwania min oraz metafora likwidowania napięcia społecznego. Czasownik wykracza poza instrukcję zawodową.
omnipotentny|O|wysoka|Trzy książkowe użycia wszechmocy w krytyce i eseistyce. Sens zgodny, ograniczenie rejestrem erudycyjnym.
cieszanowski|O|wysoka|Kontekst sceny wydarzenia w Cieszanowie; lokalny przymiotnik, nie przypadkowe nazwisko.
antykorowski|O|wysoka|Kontekst ulotek skierowanych przeciw KOR; wąska historia polityczna. Prawidłowy przymiotnik od nazwy organizacji.
modularność|O|wysoka|Dwa własne użycia w piśmie Programista opisują budowę oprogramowania. Termin techniczny; brak wiersza publikacyjnego nie usuwa pozytywnego dowodu.
dekstran|O|wysoka|Jedyny kontekst dotyczy środka podawanego w szpitalu. Termin farmaceutyczny, poprawnie rozpoznany semantycznie.
młociński|O|wysoka|Trzy dokumenty opisują park/las związany z Młocinami; nazewnictwo lokalne. Wielka litera w nazwie obiektu nie czyni automatycznie dowodu bezwartościowym.
nieoczywistość|G|średnia|Zrozumiała ogólna cecha braku oczywistości; próbka skupiona w krytyce literackiej, ale znaczenie nie jest terminem tej dziedziny.
malinówka|G|wysoka|Poprawne użycia domowej nalewki i odmiany jabłek. Wieloznaczność nie jest sama w sobie błędem dopasowania.
superstrat|O|średnia|WSJP przy haśle substrat cytuje rzeczywiste użycie superstrat w opisie relacji języków. Termin językoznawczy, mimo 0 live.
profitka|O|wysoka|Autorski katalog Muzeum Kresów używa nazwy części lichtarza. Rzeczywisty termin muzealny, nie dowód ogólnego użycia; live 0.
subtropikalny|G|wysoka|Trzy opisy podróżnicze klimatu, lasu i przyrody; przymiotnik geograficzny używany poza specjalistycznym wywodem.
szambiarka|G|wysoka|Trzy codzienne/podróżnicze konteksty pojazdu asenizacyjnego; zwykła nazwa pojazdu i usługi.
przebiśnieg|G|wysoka|Literalne kwiaty oraz czytelna przenośnia; zwykła nazwa przyrodnicza w różnych tekstach.
kocborowski|O|niska|Budowa wskazuje lokalny przymiotnik od nazwy miejsca. Bez live nie potwierdzono konkretnej podstawy i zasięgu; klasyfikacja prowizoryczna.
wyiskrzyć|O|średnia|Jedno świadome obrazowe użycie w powieści. Potwierdza formę literacką, nie samodzielnie szeroką produktywność.
strzępiak|O|wysoka|Oficjalny wykaz grzybów parku narodowego podaje kilka nazw gatunków. Termin przyrodniczy z pozytywnym źródłem mimo 0 live.
dejman|O|średnia|Dwa trafienia z jednych wspomnień marynarza; przeczytany kontekst ludzi szykujących się do zejścia wskazuje nazewnictwo załogi. Dokładnej definicji funkcji nie dopowiadam.
metkownica|G|średnia|Nazwa ręcznego urządzenia do metkowania, w kontekście techniki druku. Przedmiot codziennego handlu, nie wyjątkowy termin naukowy.
krwawica|G|wysoka|Trzy teksty używają ekspresywnej nazwy ciężko wypracowanych środków; współczesny sens ogólny.
laminarny|O|wysoka|Właściwe użycia przy komorze, skrzydle i wentylacji. Termin techniczny utrzymuje sens także w metaforze literackiej.
paranormalność|O|średnia|Trzy konteksty dyskusji o nadnaturalnych zjawiskach; abstrakcyjny termin tego obszaru. Nie oceniam prawdziwości opisywanych zjawisk.
przerąbywać|G|średnia|Poprawny kontekst rąbania bala siekierą; zwykła czynność manualna, mimo małej próby.
szałaputka|N|niska|Brak live oraz brak trafnego pierwotnego wyniku w celowanej kwerendzie WSJP. Nie przesądzam wieku ani zasięgu samej nazwy osoby.
rajszewski|O|niska|Przymiotnik o strukturze lokalnej nazwy relacyjnej. Bez kontekstu nie potwierdzono dokładnej podstawy i obiegu; wstępna kategoria lokalna.
osjakowski|O|niska|Przymiotnik o strukturze lokalnej nazwy relacyjnej. Live 0; ocena lokalnego zakresu jest wstępna, bez utożsamienia braku z marginalnością.
gul|G|średnia|Występuje jako odgłos/przywołanie ptaka oraz potoczne określenie uczucia w gardle. Dwa dalsze trafienia są mniej jasne; miary interj nie wystarczają dla każdego homonimu rzeczownikowego.
kapralina|N|niska|Live 0 i brak właściwego wyniku celowanej kwerendy WSJP. Nie rozstrzygnięto między dawną nazwą a ewentualnym nowym użyciem; brak nie stanowi werdyktu.
ruptura|M|wysoka|WSJP oznacza nazwę przepukliny jako przestarzałą. Z siedmiu trafień jeden cytat jest hiszpański, sześć odnosi się do choroby w narracji historycznej/stylizowanej.
aroniowy|G|wysoka|Przymiotnik produktu spożywczego, poświadczony przy przetworach i napojach; dwie próbki branżowe nie czynią sensu wyłącznie fachowym.
fraszkopis|O|średnia|Kontekst osoby piszącej fraszki w czasopiśmie literackim; książkowa nazwa twórcy, nie błąd.
zaciemnienie|G|wysoka|Dwa abstrakcyjne użycia utrudnienia rozumienia oraz dosłowne nocne zaciemnienie. Własny rzeczownik ma dowód niezależny od dużej rodziny czasowników.
odwłóczyć|M|wysoka|Właściwy cytat dawnej wypowiedzi o odłożeniu operacji; WSJP ma przest. Sama data wydania biografii nie dowodzi neutralnego współczesnego użycia.
manipuł|N|niska|Live 0; nie ustalono w tej kwerendzie, które znaczenie i jaki współczesny obieg mają być oceniane. Potrzebne źródło znaczeniowe przed oceną POP.
niezwłoczność|O|wysoka|Dwa teksty prawno-urzędowe i jeden reportaż odnoszący się do procedury. Poprawna abstrakcyjna nazwa właściwości, dominujący rejestr formalny.
wykrzyknikowy|O|średnia|Kontekst krytyki stylistycznej potwierdza określenie językoznawcze. Jeden dokument, nie szeroki przekrój użycia.
paleozoik|O|średnia|Metafora warstw terenu opiera się na poprawnym terminie geologicznym. Termin szkolny może być odpowiedni dla szerokiego POP.
kokotek|O|średnia|Kontekst śląskich potraw wskazuje regionalną nazwę kulinarną/zwierzęcia. Nie jest dowodem znaczeń powiązanej kokotki; precyzyjne mapowanie pozostaje ograniczone.
nepotyczny|G|wysoka|Trzy użycia w krytyce układów, struktur i działalności publicznej. Zrozumiały przymiotnik ogólnego dyskursu społecznego.
lektorium|O|wysoka|Dwa konteksty czytelni i jeden przestrzeni kościelnej; termin instytucjonalny, znaczenia trzeba rozdzielić przed przenoszeniem miar.
biochemicznie|O|wysoka|Trzy właściwe opisy działania organizmu; termin sposobu/zakresu wyjaśnienia biologiczno-chemicznego.
bojownica|O|wysoka|WSJP potwierdza książkową nazwę kobiety walczącej o idee. Własnego live użycia brak; miary grupy z bojownik nie są zastępczym poświadczeniem tej formy.
proweniencyjny|O|wysoka|Trzy konteksty badania pochodzenia dzieł i zbiorów; termin muzealnictwa/historii sztuki.
kaletnik|G|średnia|Trzy właściwe użycia zawodu/usługi, w tym współczesnej naprawy. Potwierdzają kaletnik:Sm1; homonim kaletnik:Sm3 pozostaje bez dowodu.
posuć|N|niska|Brak live i brak trafnego wyniku celowanej kwerendy WSJP. Nie wyprowadzam marginalności ani znaczenia ze współczesnego posypać przez samą analogię.
cegłówka|G|wysoka|Trzy zwykłe opisy cegły, także metaforyczne; potoczny rzeczownik o szerokim zastosowaniu.
zniczek|G|niska|Regularne zdrobnienie codziennej nazwy przedmiotu. Ocena semantyczna bez znalezionego kontekstu; nie badano rozpoznawalności graczy.
tomahawk|O|wysoka|Trzy poprawne nazwy broni w opisach/rzeźbie i prozie. Termin kulturowy używany współcześnie, bez dowodu archaizacji samego wyrazu.
mauretański|O|wysoka|Dwa dokumenty o historii i architekturze Maurów; poprawny przymiotnik kulturowo-historyczny, nie ogólna codzienna relacja.
elementarność|O|średnia|Trzy użycia abstrakcyjne w krytyce i filozofii; sens zgodny, rejestr erudycyjny. Nie marginalizować z powodu samej rzadkości.
pracodawczy|O|średnia|Poprawny kontekst inicjatyw zatrudnieniowych; profil instytucjonalny. Jedno użycie, brak podstaw do pewnej oceny szerokiego obiegu.
pozlepiać|G|wysoka|Trzy użycia rzeczy złączonych w całość lub chaotycznie sklejonego dzieła; zwykła czynność i przenośnia.
nabieracz|N|niska|Dwa homonimy o różnym rodzaju, lecz brak live kontekstu. Nie ustalono, czy dowód ma dotyczyć osoby, narzędzia czy innego sensu.
kanalikowy|O|niska|Relacyjny przymiotnik od kanalika ma prawdopodobnie profil techniczny/anatomiczny. Brak kontekstu pozostawia dokładny sens otwarty.
terminarzyk|G|niska|Przejrzyste zdrobnienie terminarza, nazwy codziennego przedmiotu. Propozycja semantyczna bez potwierdzenia live; nie wniosek o częstości.
troszka|N|średnia|Osiem wyników miesza rzeczownikową małą ilość, przysłówkowe troszkę, regionalne troszka i po troszku. Potrzebne rozdzielenie jednostek; nie przenosić powszechności troszkę na każdy rzeczownikowy paradygmat.
kaktusowaty|N|średnia|Oba wyniki odnoszą się do rodziny kaktusowatych, nie jasno do przymiotnika podobny do kaktusa. Znaczenie botaniczne jest rzeczywiste, lecz przejście od kaktusowate do badanego przymiotnika niezamknięte.
staniczek|G|wysoka|Zdrobnienie zwykłej części odzieży w wypowiedziach i reportażu; jeden cytat piosenki nie wyczerpuje dowodu.
płomiennowłosy|O|średnia|Dwa obrazowe opisy osoby o rudych włosach, w reportażu i grze. Rejestr literacki/ekspresywny, bez błędu analizy.
judaszowski|O|niska|Przymiotnik o możliwej biblijnej/przenośnej funkcji, ale live 0. Ocena rejestru wstępna; brakuje odczytanego kontekstu dla konkretnego sensu.
balneator|N|niska|Live 0; wyszukiwanie przyniosło łacińskie nazewnictwo zawodu, które nie potwierdza współczesnego polskiego użycia. Potrzebne właściwe źródło językowe.
minirobota|N|niska|Brak live i brak właściwego wyniku WSJP. Sam prefiks mini- nie wystarcza do ustalenia znaczenia ani zasięgu całego hasła.
zabawność|G|średnia|Prawidłowa ogólna nazwa cechy, choć trzy wybrane teksty są literackie. Nie jest to automatycznie termin literaturoznawczy.
symplifikować|O|wysoka|Jedyny kontekst socjologiczno-filozoficzny potwierdza erudycyjny czasownik upraszczania.
dorozumieć|O|wysoka|Trzy właściwe użycia rozumienia przez wnioskowanie, w esejach i prozie. Rejestr książkowy; nie wyłącznie cytat historyczny.
medresa|O|wysoka|Trzy właściwe użycia szkoły muzułmańskiej w reportażach; termin kulturowy. Podobne serie wydawnicze nie są trzema niezależnymi badaniami znajomości.
kuracjuszka|G|wysoka|Zwykła nazwa uczestniczki kuracji/sanatorium; trzy odmienne bieżące sytuacje i dialog.
kodeina|O|wysoka|Trzy trafienia dotyczą substancji/leku, w tym tekst historyczny i cytat artystyczny. Poprawny termin farmaceutyczny; korpusowy przekrój nie mierzy znajomości ogólnej.
planistyka|O|wysoka|Poprawne użycia w planowaniu, urbanistyce i ekonomii, także wyliczenie w powieści. Termin dziedzinowy, nie błąd dopasowania.
pęca|O|niska|Pierwotne opracowanie słownictwa potwierdza nazwę elementu wyposażenia ptaka łowczego. Brak live pozostawia otwarty dzisiejszy obieg i stosunek do pęc; termin sokolniczy, nie automatycznie martwy.
domcio|G|średnia|Dwa poprawne współczesne konteksty zdrobniałej nazwy domu. Ekspresywność rodzinna/żartobliwa nie jest tu wąskim żargonem.
pasywizacja|O|wysoka|Aktualny opis zajęć UW używa terminu operacji składniowej. Mocne właściwe źródło specjalistyczne mimo 0 live.'''

CLASS = {'G':'ogólne','O':'ograniczone','M':'marginalne','B':'błędne_dopasowanie','N':'niepewne'}
# Dodatkowo przeczytano wszystkie dostępne z pierwszej dziesiątki tych haseł.
EXPANDED = {'pilarz','siejba','repetytorium','wypełzły','koniunktiwus',
            'deminutywny','gul','ruptura','troszka','kaktusowaty'}

EXTERNAL = {
 'przedryndać': [('https://wsjp.pl/haslo/podglad/111647/przedryndac/5263631/500-km','WSJP: właściwe hasło i przykłady przejechania trasy; nie wyniki KWJP live.')],
 'kikować': [('https://obserwatorium-mlodziezy.ujk.edu.pl/jednostki/kikowac/','Opracowanie UJK rozróżnia obserwowanie i nowe znaczenie usuwania z gry/grupy.')],
 'kozeta': [('https://pl.wikisource.org/wiki/M._Arcta_S%C5%82ownik_ilustrowany_j%C4%99zyka_polskiego/K_%28ca%C5%82o%C5%9B%C4%87%29','Historyczny słownik Arcta: nazwa mebla; nie dowód aktualnego obiegu.')],
 'wiwera': [('https://wsjp.pl/haslo/podglad/117600/wiwera','WSJP: zoologiczna nazwa i cytat prasowy 2020.')],
 'szampiter': [('https://www.poradnikjezykowy.uw.edu.pl/wydania/poradnik_jezykowy.796.2022.07.3-U.Sokolska.pdf','Autorska analiza języka Boya, s.45: szampiter jako szampan; materiał historyczny.'),('https://smakipowiatupoznanskiego.pl/slownik-gwary-poznanskiej/','Słownik regionalny powiatu: szampiter jako szampon. Osobna ścieżka znaczeniowa.')],
 'profitka': [('https://muzeumkresow.eu/eksponat/lichtarz-3/','Autorski opis eksponatu: część lichtarza; poświadczenie użycia muzealnego.')],
 'pęca': [('https://repozytorium.amu.edu.pl/bitstream/10593/464/2/S%C5%81OWNIK.pdf','Opracowanie leksykalne UAM: wyposażenie ptaka łowczego; zestawienie historycznych rejestracji, nie pomiar współczesnego zasięgu.')],
 'bojownica': [('https://wsjp.pl/haslo/podglad/129634/bojownica','WSJP: książkowa nazwa kobiety walczącej o idee, niezależna od bojownik.')],
 'siejba': [('https://wsjp.pl/haslo/podglad/119994/siejba','WSJP kwalifikuje nazwę siewu jako dawną.')],
 'odwłóczyć': [('https://wsjp.pl/haslo/podglad/124654/odwloczyc','WSJP kwalifikuje czasownik odsunięcia w czasie jako przestarzały.')],
 'ruptura': [('https://wsjp.pl/haslo/podglad/50305/ruptura','WSJP: przestarzała nazwa przepukliny.')],
 'konklawista': [('https://www.przewodnik-katolicki.pl/Archiwum/2004/Przewodnik-Katolicki-48-2004/Historia/Jak-wybierano-papiezy','Autorski artykuł Małgorzaty Jańczak używa nazwy uczestnika konklawe; historyczny temat nie przesądza wieku wyrazu.')],
 'superstrat': [('https://wsjp.pl/haslo/podglad/20796/substrat/5157958/w-jezykoznawstwie','WSJP cytuje superstrat przy opisie relacji języków; nie jest to odrębne hasło superstrat.')],
 'pasywizacja': [('https://informatorects.uw.edu.pl/pl/courses/view?prz_kod=3301-ZJ-WM-JF003','Autorski opis zajęć UW, cykle 2025Z/2026Z, potwierdza termin składniowy.')],
 'wiroid': [('https://zpe.gov.pl/a/przeczytaj/DQN7i4ibO','Materiał dydaktyczny ZPE o wiroidach.'),('https://www.gov.pl/web/piorin/regulowane-agrofagi-niekwarantannowe-dla-unii','PIORiN: nazwy wiroidów w wykazie agrofagów; badamy użycie słowa, nie przepisy.')],
 'strzępiak': [('https://pnbt.gov.pl/pliki-do-pobrania/otworz/a7b93254-3b32-4d4e-b9a5-c6641d00d381.pdf','Oficjalny wykaz grzybów PN Bory Tucholskie, pozycje 215–224: nazwy gatunków.')],
 'lunonauta': [('https://www.urania.edu.pl/zasoby/ksiezyc-ludzie-i-slowa.html','Autorski artykuł Uranii używa nazwy uczestnika wyprawy księżycowej.')],
}

SPECIAL = {
 ('dekagram',3):('powiązane_inna_forma','Skrót dkg odnosi się do tej samej jednostki, lecz nie jest pełną formą rzeczownika.'),
 ('mszyć',0):('niezgodne','W relacji piłkarskiej prawdopodobnie uszkodzony zapis ruszył; nie dowód mszyć.'),
 ('mszyć',1):('niezgodne','W relacji piłkarskiej prawdopodobnie uszkodzony zapis ruszył; nie dowód mszyć.'),
 ('pilarz',8):('niezgodne','Nazwisko piłkarza, nie zawód ani inny rzeczownik pospolity.'),
 ('pilarz',9):('niezgodne','Nazwisko piłkarza, nie zawód ani inny rzeczownik pospolity.'),
 ('repetytorium',2):('niezgodne','Rejestr notarialny: najprawdopodobniej błędny zapis repertorium.'),
 ('repetytorium',5):('niezgodne','Rejestr kancelarii: najprawdopodobniej błędny zapis repertorium.'),
 ('repetytorium',8):('niezgodne','Rejestr czynności tłumacza: najprawdopodobniej repertorium.'),
 ('zaważać',1):('niezgodne','Wprowadzenie wypowiedzi urzędnika wygląda na uszkodzone zauważa.'),
 ('deminutywny',0):('powiązane_inna_forma','Niesamodzielny człon złożenia deminutywno-, nie samodzielny przymiotnik.'),
 ('deminutywny',2):('powiązane_inna_forma','Niesamodzielny człon złożenia deminutywno-, nie samodzielny przymiotnik.'),
 ('gul',3):('zgodne_inny_homonim','Potoczny rzeczownik o odczuciu w gardle, nie wykrzyknik.'),
 ('gul',8):('niepewne','Potoczne użycie wymaga szerszego kontekstu; tag interj nie rozstrzyga sensu.'),
 ('gul',9):('niepewne','Potoczna nominalizacja/ocena; tag m1 nie rozstrzyga mapowania rekordu.'),
 ('ruptura',0):('niezgodne','Cytat hiszpański, nie polska nazwa przepukliny.'),
 ('troszka',0):('niepewne','Związek po troszku; nie potwierdza automatycznie pełnego paradygmatu troszka/f.'),
 ('troszka',1):('niepewne','Ilościowe troszkę; granica rzeczownik/przysłówek/kwantyfikator wymaga rozdzielenia.'),
 ('troszka',2):('niezgodne','W cytacie dawnej poezji funkcja przysłówkowa; nie dowód badanego rzeczownika.'),
 ('troszka',3):('niezgodne','Regionalny przysłówek, nie dowód badanego rzeczownika.'),
 ('troszka',4):('niezgodne','Stopień zmiany: funkcja przysłówkowa, nie rzeczownikowa ilość.'),
 ('troszka',5):('zgodne','Mała ilość uczucia w dopełniaczu; najmocniejsze rzeczownikowe dopasowanie.'),
 ('troszka',6):('niepewne','Forma troszku nie rozstrzyga zgodności z żeńskim paradygmatem próbki.'),
 ('troszka',7):('niepewne','Ilościowe troszkę piwa, samo nie rozstrzyga modelu jednostki.'),
 ('kaktusowaty',0):('niepewne','Odniesienie do rodziny roślin; możliwa nominalizacja kaktusowate, nie swobodny przymiotnik.'),
 ('kaktusowaty',1):('niepewne','Rodzina botaniczna kaktusowate; semantycznie pokrewne, mapowanie leksemu nierozstrzygnięte.'),
}

def selected_indices(case):
    if case['lemma'] in EXPANDED:
        return list(range(len(case['rows'])))
    seen=set(); selected=[]
    for i,row in enumerate(case['rows']):
        if row['document_id'] in seen: continue
        seen.add(row['document_id']); selected.append(i)
        if len(selected)==3: break
    return selected

def context_note(lemma, i, row):
    if (lemma,i) in SPECIAL: return SPECIAL[(lemma,i)]
    if lemma=='siejba':
        return ('zgodne_stylizacja','Współczesna obrazowa narracja powieściowa.') if i==7 else ('zgodne_cytat','Właściwy leksem w poetyckim przytoczeniu; data dokumentu nie jest datą powstania cytatu.')
    if lemma=='wypełzły': return ('zgodne_cytat','Właściwy przymiotnik w cytowanym opisie literackim; nie czas przeszły wypełznąć.')
    if lemma=='ścieżyna' and i in (0,1): return ('zgodne_cytat','Właściwy leksem w literackim przytoczeniu.')
    if lemma=='odwłóczyć': return ('zgodne_cytat','Cytowana dawna wypowiedź; nie nowa kreacja z daty wydania biografii.')
    if lemma=='pilarz': return ('zgodne','Zawód pracownika ścinającego drzewa: pilarz:Sm1; nie dowód homonimu Sm2.')
    if lemma=='kaletnik': return ('zgodne','Zawód/usługa: kaletnik:Sm1; nie dowód homonimu Sm3.')
    if lemma=='wywiadowczyni': return ('zgodne_wąski_sens','Nazwa pszczoły rozpoznającej miejsce; zakres nazwy kobiety niepotwierdzony.')
    if lemma=='gul': return ('zgodne','Dźwiękonaśladowanie/przywołanie ptaka, ścieżka wykrzyknikowa.')
    if lemma=='ruptura': return ('zgodne_stylizacja','Polska nazwa choroby w narracji historycznej/stylizowanej; błędny tag nazwy własnej nie zmienia sensu.')
    return ('zgodne','Odczytany kontekst odpowiada sensowi opisanemu w uzasadnieniu; nie przesądza innych homonimów ani całego paradygmatu.')

def main():
    sample=json.loads(INPUT.read_text()); live=json.loads(CONTEXTS.read_text())
    raw={c['id']:c for c in live}
    manual=[line.split('|',3) for line in ASSESSMENTS.splitlines()]
    assert len(manual)==150==len(sample['cases'])
    cases=[]; documents={}
    for initial, rating in zip(sample['cases'],manual):
        lemma,cl,confidence,reason=rating
        assert lemma==initial['lemma'], (lemma,initial['lemma'])
        c=raw[initial['id']]; read=[]
        for i in selected_indices(c):
            r=c['rows'][i]; alignment,note=context_note(lemma,i,r)
            documents[r['document_id']]={'metadata':r['metadata'],'date_as_reported':r['date']}
            read.append({'hit_index_zero_based':i,'document_id':r['document_id'],
                         'sentence':r['sentence'],'surface':r['word'],
                         'alignment':alignment,'note':note,'url':c['url']})
        keys=[e['key'] for e in initial['evidence']]
        groups=[e['group_members'] for e in initial['evidence']]
        group_mismatch=any(set(g)!={e['key'][1]} for e,g in zip(initial['evidence'],groups))
        qstatus='read_zero_results' if c['total']==0 else 'read_positive_results'
        sources=[{'kind':'KWJP_live','url':c['url'],'query':c['query'],'status':qstatus,
                  'response_sha256':c['response_sha256']}]
        sources += [{'kind':'pierwotne_źródło_zewnętrzne','url':url,'note':note,'accessed':'2026-10-12',
                     'read_scope':'Odczyt treści hasła lub indeksowanego fragmentu strony/opracowania; bez tezy o przeczytaniu całego dokumentu.'}
                    for url,note in EXTERNAL.get(lemma,[])]
        cases.append({'id':initial['id'],'lemma':lemma,'class':CLASS[cl],'confidence':confidence,
          'rationale':reason,'assessed_scope':'Przydatność znaczenia/leksemu do szerokiego POP; nie legalność STANDARD ani znajomość wśród graczy.',
          'source_keys':keys,'group_members':groups,'original_kwjp_rows':initial['original_kwjp_rows'],
          'own_source_statuses':[{'key':e['key'],'kwjp':e['kwjp_own']['status'],'nkjp':e['nkjp_own_status']} for e in initial['evidence']],
          'metric_scope_note': 'Grupa zawiera inne leksemy; jej miara nie zastępuje własnego dowodu.' if group_mismatch else 'Nie przyjmowano rangi ani progu. Oryginalne wiersze F/ARF/POS zachowano osobno.',
          'live_reported_hits':c['total'],'live_reported_hits_note':'Wynik zgłoszony przez wyszukiwarkę, możliwy limit; nie zastępuje F z przypiętej tabeli.',
          'downloaded_contexts':len(c['rows']),'read_contexts_count':len(read),
          'read_documents_count':len({r['document_id'] for r in read}),
          'read_contexts':read,'sources':sources,
          'coverage_gap':'Brak odczytanych konkordancji live; klasa jest oceną semantyczną wspartą źródłem zewnętrznym, jeżeli je wskazano.' if not read else 'Pierwszych 10 wyników; wybrane dokumenty nie stanowią reprezentatywnej próby użyć ani odbiorców.'})
    now=datetime.now(timezone.utc).isoformat()
    result={'schema_version':1,'reviewer':'B','blind_assessment_frozen_at_utc':now,
      'blinding':'Nie odczytano sample-design.json, measurements, rankingu, membership ani ocen koordynatora/drugiego badacza przed utrwaleniem ocen.',
      'input_sha256':hashlib.sha256(INPUT.read_bytes()).hexdigest(),
      'contexts_input_sha256':hashlib.sha256(CONTEXTS.read_bytes()).hexdigest(),
      'method':'Ręczna ocena 150 haseł. Do 3 kontekstów z różnych dokumentów spośród pierwszych 10; dla 10 spornych haseł przeczytano wszystkie dostępne pierwsze 10. Dodatkowe kwerendy źródeł pierwotnych dla wybranych niejasności. Klasy są oceną badacza, nie badaniem znajomości graczy.',
      'class_definitions':{'ogólne':'Zwykłe współczesne słowo ogólnego użytku, także przejrzyste codzienne derywaty. Część ocen bez live ma niską pewność.',
        'ograniczone':'Termin, specjalny rejestr lub lokalny przymiotnik. Nie oznacza automatycznego wykluczenia z szerokiego POP.',
        'marginalne':'Dawne lub bardzo osobliwe użycie na podstawie dodatnich przesłanek o charakterze słowa, nie samego braku korpusowego.',
        'błędne_dopasowanie':'Konkretny znaleziony dowód dotyczy czegoś innego; nie teza, że leksem nie istnieje.',
        'niepewne':'Materiał nie rozstrzyga sensu, mapowania lub zakresu; nie wolno włączać do negatywów.'},
      'summary':{'cases':len(cases),'classes':dict(Counter(c['class'] for c in cases)),
        'confidence':dict(Counter(c['confidence'] for c in cases)),
        'downloaded_contexts':sum(c['downloaded_contexts'] for c in cases),
        'read_contexts':sum(c['read_contexts_count'] for c in cases),
        'distinct_documents_read':len(documents),'zero_live_cases':sum(c['live_reported_hits']==0 for c in cases),
        'external_source_cases':len(EXTERNAL)},
      'cases':cases,'documents':documents,
      'limits':['Ocena jakości nie jest oceną znanego progu; rangi i przynależność pozostają ukryte.',
        'Brak w publikowanym wykazie i 0 live nie oznaczają nieistnienia ani marginalności.',
        'Wynik 1000 jest traktowany jako możliwy limit wyszukiwarki.',
        'Data wydania/przechowywania tekstu nie gwarantuje daty stworzenia cytatu; metadane obejmują także 2021/2022.',
        'Kategorie ogólne/ograniczone są oceną językową badacza; nie przeprowadzono badania graczy.',
        'Mieszany materiał oznaczano przy konkretnym kontekście, nie przez odrzucenie całego hasła.',
        'Nie publikowano surowych konkordancji. Zachowano wyłącznie własne uzasadnienia i metadane.']}
    (OUT/'quality-b.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(result['summary'],ensure_ascii=False))
    render(result)

def render(d):
    s=d['summary']
    lines=['# Ślepa ocena jakości B — 150 haseł POP','', '## TL;DR','',
      'Oceniono wszystkie 150 haseł bez odczytu rankingu, progów ani przynależności. Wynik jest oceną językową przydatności do szerokiego POP, nie badaniem znajomości słów przez graczy i nie audytem legalności STANDARD.','',
      ', '.join(f'**{k}: {v}**' for k,v in s['classes'].items())+'.','',
      f"Pobrane konkordancje: **{s['downloaded_contexts']}**. Faktycznie przeczytane i adnotowane: **{s['read_contexts']}**, z {s['distinct_documents_read']} dokumentów. Hasła z 0 wyników live: **{s['zero_live_cases']}**. Dla {s['external_source_cases']} haseł dołączono właściwe zewnętrzne źródło pierwotne.",'',
      '## Key Decisions','',
      '- Oddzielono klasę hasła od zgodności pojedynczego kontekstu. Nazwisko przy pilarz, pomylenie repertorium/repetytorium i uszkodzone zauważa przy zaważać nie przekreślają prawidłowych użyć.',
      '- mszyć ma dwa odczytane wyniki, oba najprawdopodobniej uszkodzone ruszył w relacjach piłkarskich. Duża grupa z msza nie naprawia tego dowodu.',
      '- Nie utożsamiono braku wiersza publikacyjnego z brakiem użycia. pomiaukiwać, odbąknąć, odmoczyć, podrzemać i dotaszczyć mają własne poprawne konteksty.',
      '- Terminy i lokalne przymiotniki otrzymały ograniczone, co nie jest decyzją o ich wykluczeniu. Źródła zewnętrzne potwierdziły m.in. wiroid, wiwera, profitka, strzępiak i pasywizacja mimo 0 live.',
      '- Wstrzymano ocenę niektórych leksemów i mapowań jako niepewne. Dotyczy to m.in. troszka, kaktusowaty, nabieracz i minirobota.',
      '- Daty nowych wydań nie legalizują dowodu o współczesności starych cytatów. Marginalne dla siejba, ruptura i odwłóczyć opiera się również na jawnej kwalifikacji WSJP, nie tylko małej liczbie trafień.','',
      '## Metoda i zakres','',d['method'],'',
      'Klasa ogólne obejmuje także codzienne zdrobnienia i przejrzyste derywaty. Oceny bez pozytywnego kontekstu mają przeważnie niską pewność. Klasa ograniczone oznacza węższy rejestr/temat, a nie rzadkość zmierzoną w całej populacji. Ogólne nie znaczy znane wszystkim; ograniczone nie znaczy nieprzydatne do gry.','',
      'Przy każdym haśle JSON zachowuje oryginalne wiersze KWJP osobno (F, ARF, POS), grupę i status własnego rekordu. Nie sumowano ARF ani nie stosowano ukrytego progu. Licznik live jest tylko wynikiem zgłoszonym przez wyszukiwarkę.','',
      'Dokładne przeczytane konteksty identyfikuje [quality-b.json](quality-b.json): hit_index_zero_based, document_id i sentence, z oceną zgodności sensu, URL i hashem odpowiedzi. Nie zapisano tekstów konkordancji. Skrypt [round5_quality_b.py](../../round5_quality_b.py) odtwarza artefakty z utrwalonych ręcznych adnotacji.','',
      '## Oceny wszystkich haseł','',
      '| Hasło | Klasa | Pewność | Odczyt live: konteksty / dokumenty | Uzasadnienie |',
      '|---|---|---|---:|---|']
    for c in d['cases']:
        lines.append(f"| {c['lemma']} | {c['class']} | {c['confidence']} | {c['read_contexts_count']} / {c['read_documents_count']} | {c['rationale']} |")
    lines += ['', '## Dodatkowe źródła pierwotne', '']
    for c in d['cases']:
        for e in c['sources'][1:]: lines.append(f"- **{c['lemma']}** — [{e['note']}]({e['url']})")
    lines += ['', 'Daty dostępu: 12.10.2026. Odczyt zewnętrzny obejmował treść hasła albo indeksowany fragment źródła, nie cały każdy dokument PDF. Wyników SJP.pl nie używano jako normy ani przesłanki klasy.', '',
      '## Open Questions / Risks','',
      '- Kategorie na granicy rejestru ogólnego i książkowego wymagają porównania niezależnych ocen. Przykłady: nieoczywistość, jedyność, bezgłos, rozminowywać, mauretański.',
      '- troszka miesza różne funkcje składniowe; kaktusowaty ma tylko konteksty rodziny kaktusowatych. Nie przenosić częstości powiązanej jednostki na cały paradygmat.',
      '- pilarz i kaletnik mają dowód dla nazw osób, nie wszystkich homonimów obecnych w próbce; gul ma różne części mowy i dwa mniej jasne konteksty.',
      '- wywiadowczyni w próbie live dotyczy tylko pszczół. To dodatni wąski sens, nie dowód powszechności nazwy kobiety.',
      '- szampiter ma historyczne znaczenie szampan i regionalne szampon; kikować ma co najmniej dwa różne środowiskowe znaczenia. Potrzebne zachowanie podziału sensów.',
      '- Niska pewność i niepewne oznaczają luki danych. Nie wolno w analizie progu zamienić ich automatycznie na negatywne oceny.',
      '- Pierwszych 10 trafień bywa skupionych w jednym autorze/źródle. Ocena do trzech dokumentów i rozszerzenia spornych przypadków nie tworzą losowej próby języka ani ankiety graczy.',
      '- Źródła historyczne dowodzą istnienia słowa, a nie jego aktualnego szerokiego obiegu. Brak kontekstu nie dowodzi nieistnienia.','',
      f"Utrwalenie ślepej oceny (UTC): {d['blind_assessment_frozen_at_utc']}. Żadnych zmian produkcyjnych ani decyzji o progach."]
    (OUT/'quality-b.md').write_text('\n'.join(lines)+'\n')

if __name__=='__main__': main()
