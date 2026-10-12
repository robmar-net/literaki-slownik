# Ślepa ocena jakości B — 150 haseł POP

## TL;DR

Oceniono wszystkie 150 haseł bez odczytu rankingu, progów ani przynależności. Wynik jest oceną językową przydatności do szerokiego POP, nie badaniem znajomości słów przez graczy i nie audytem legalności STANDARD.

**ograniczone: 82**, **ogólne: 54**, **błędne_dopasowanie: 1**, **marginalne: 3**, **niepewne: 10**.

Pobrane konkordancje: **644**. Faktycznie przeczytane i adnotowane: **316**, z 220 dokumentów. Hasła z 0 wyników live: **35**. Dla 17 haseł dołączono właściwe zewnętrzne źródło pierwotne.

## Key Decisions

- Oddzielono klasę hasła od zgodności pojedynczego kontekstu. Nazwisko przy pilarz, pomylenie repertorium/repetytorium i uszkodzone zauważa przy zaważać nie przekreślają prawidłowych użyć.
- mszyć ma dwa odczytane wyniki, oba najprawdopodobniej uszkodzone ruszył w relacjach piłkarskich. Duża grupa z msza nie naprawia tego dowodu.
- Nie utożsamiono braku wiersza publikacyjnego z brakiem użycia. pomiaukiwać, odbąknąć, odmoczyć, podrzemać i dotaszczyć mają własne poprawne konteksty.
- Terminy i lokalne przymiotniki otrzymały ograniczone, co nie jest decyzją o ich wykluczeniu. Źródła zewnętrzne potwierdziły m.in. wiroid, wiwera, profitka, strzępiak i pasywizacja mimo 0 live.
- Wstrzymano ocenę niektórych leksemów i mapowań jako niepewne. Dotyczy to m.in. troszka, kaktusowaty, nabieracz i minirobota.
- Daty nowych wydań nie legalizują dowodu o współczesności starych cytatów. Marginalne dla siejba, ruptura i odwłóczyć opiera się również na jawnej kwalifikacji WSJP, nie tylko małej liczbie trafień.

## Open Questions / Risks

- Kategorie na granicy rejestru ogólnego i książkowego wymagają porównania niezależnych ocen. Przykłady: nieoczywistość, jedyność, bezgłos, rozminowywać, mauretański.
- troszka miesza różne funkcje składniowe; kaktusowaty ma tylko konteksty rodziny kaktusowatych. Nie przenosić częstości powiązanej jednostki na cały paradygmat.
- pilarz i kaletnik mają dowód dla nazw osób, nie wszystkich homonimów obecnych w próbce; gul ma różne części mowy i dwa mniej jasne konteksty.
- wywiadowczyni w próbie live dotyczy tylko pszczół. To dodatni wąski sens, nie dowód powszechności nazwy kobiety.
- szampiter ma historyczne znaczenie szampan i regionalne szampon; kikować ma co najmniej dwa różne środowiskowe znaczenia. Potrzebne zachowanie podziału sensów.
- Niska pewność i niepewne oznaczają luki danych. Nie wolno w analizie progu zamienić ich automatycznie na negatywne oceny.
- Pierwszych 10 trafień bywa skupionych w jednym autorze/źródle. Ocena do trzech dokumentów i rozszerzenia spornych przypadków nie tworzą losowej próby języka ani ankiety graczy.
- Źródła historyczne dowodzą istnienia słowa, a nie jego aktualnego szerokiego obiegu. Brak kontekstu nie dowodzi nieistnienia.

Utrwalenie ślepej oceny (UTC): 2026-10-12T10:38:14.379552+00:00. Żadnych zmian produkcyjnych ani decyzji o progach.

## Metoda i zakres

Ręczna ocena 150 haseł. Do 3 kontekstów z różnych dokumentów spośród pierwszych 10; dla 10 spornych haseł przeczytano wszystkie dostępne pierwsze 10. Dodatkowe kwerendy źródeł pierwotnych dla wybranych niejasności. Klasy są oceną badacza, nie badaniem znajomości graczy.

Klasa ogólne obejmuje także codzienne zdrobnienia i przejrzyste derywaty. Oceny bez pozytywnego kontekstu mają przeważnie niską pewność. Klasa ograniczone oznacza węższy rejestr/temat, a nie rzadkość zmierzoną w całej populacji. Ogólne nie znaczy znane wszystkim; ograniczone nie znaczy nieprzydatne do gry.

Przy każdym haśle JSON zachowuje oryginalne wiersze KWJP osobno (F, ARF, POS), grupę i status własnego rekordu. Nie sumowano ARF ani nie stosowano ukrytego progu. Licznik live jest tylko wynikiem zgłoszonym przez wyszukiwarkę.

Dokładne przeczytane konteksty identyfikuje [quality-b.json](quality-b.json): hit_index_zero_based, document_id i sentence, z oceną zgodności sensu, URL i hashem odpowiedzi. Nie zapisano tekstów konkordancji. Skrypt [round5_quality_b.py](../../round5_quality_b.py) odtwarza artefakty z utrwalonych ręcznych adnotacji.

## Oceny wszystkich haseł

| Hasło | Klasa | Pewność | Odczyt live: konteksty / dokumenty | Uzasadnienie |
|---|---|---|---:|---|
| przedryndać | ograniczone | średnia | 0 / 0 | WSJP potwierdza ekspresywne przejechanie trasy i telefonowanie; brak live kontekstu nie unieważnia słowa. Rejestr potoczny, nienacechowane użycie ogólne nieudokumentowane tutaj. |
| dekagram | ogólne | wysoka | 3 / 3 | Zwykła miara masy w opisach ilości; osobny rzeczownik ma 24 wystąpienia w tabeli. Skróty tworzą odrębną warstwę 61, której nie wolno utożsamiać z częstością pełnego wyrazu. |
| pomiaukiwać | ogólne | wysoka | 3 / 3 | Trzy nowe narracje opisują wydawanie odgłosów przez koty. Zwykły opis czynności, mimo braku opublikowanego własnego wiersza. |
| margarynowy | ogólne | średnia | 1 / 1 | Przymiotnik od codziennego produktu; kontekst części przedsiębiorstwa związanej z margaryną potwierdza sens. Jedna próbka ogranicza pewność zasięgu. |
| mszyć | błędne_dopasowanie | wysoka | 2 / 2 | Oba trafienia mają postać mszył tam, gdzie relacja piłkarska wymaga ruszył. Duża grupa z msza nie jest dowodem żywotności czasownika mszyć. |
| transkrypcyjny | ograniczone | wysoka | 1 / 1 | Kontekst metod zapisu badań potwierdza termin zawodowy/naukowy, nie zwykły szeroki opis. |
| odbąknąć | ogólne | wysoka | 3 / 3 | W trzech dialogach oznacza krótką niechętną odpowiedź. Ekspresywny, lecz zwykły czasownik codziennej komunikacji. |
| hoja | ograniczone | wysoka | 2 / 2 | Dwa dokumenty dotyczą rośliny ozdobnej; właściwe użycia nazwy ogrodniczej. Nie są dowodem nazw własnych mimo flagi źródła. |
| podminować | ogólne | wysoka | 3 / 3 | Przenośne destabilizowanie i zdenerwowanie człowieka są czytelne w różnych tekstach; nie ogranicza się do saperstwa. |
| biseks | ograniczone | wysoka | 3 / 3 | Trzy polskie użycia nazwy osoby biseksualnej; skrócona potoczna nazwa, nie błąd ani archaizm. |
| pilarz | ogólne | średnia | 10 / 3 | Osiem z pierwszych dziesięciu trafień wspiera nazwę zawodu, dwa dotyczą nazwiska. To wsparcie pilarz:Sm1; homonim pilarz:Sm2 pozostaje niepotwierdzony. |
| fermentownia | ograniczone | niska | 0 / 0 | Budowa nazwy wskazuje pomieszczenie lub dział procesu fermentacji, więc zastosowanie branżowe. To wstępna ocena semantyczna; 0 live i brak wiersza nie ustalają faktycznego zasięgu. |
| nieruchawość | ogólne | wysoka | 3 / 3 | Trzy teksty używają zwykłej nazwy cechy małej ruchliwości; nie trzeba specjalistycznej dziedziny, aby uzasadnić jej przydatność. |
| wirusowość | ograniczone | średnia | 1 / 1 | Jedyny kontekst dotyczy szybkiego rozpowszechniania informacji w sieci. Potwierdza termin komunikacji medialnej, nie całą potencjalną wieloznaczność. |
| zgorzknialec | ogólne | niska | 0 / 0 | Przejrzysta nazwa osoby zgorzkniałej nadaje się do zwykłego opisu człowieka. Ocena językowa bez znalezionego live użycia; brak nie jest dowodem nieistnienia. |
| niebieskawo | ogólne | wysoka | 3 / 3 | Trzy teksty opisują barwę światła lub zmiany skórnej. Samodzielny przysłówek, a nie tylko człon złożenia. |
| obrączkować | ograniczone | wysoka | 3 / 3 | Znakowanie zwierząt ma wąską praktykę przyrodniczą; jeden kontekst przenosi czynność na zakuwanie człowieka. Sens zgodny, nie sam dźwięk napisu. |
| siejba | marginalne | wysoka | 9 / 4 | WSJP: dawne określenie siewu. Osiem z dziewięciu kontekstów to poezja/przytoczenia, jeden to współczesna stylizowana powieść. Nie jest to brak użyć, lecz wyraźne ograniczenie chronologiczno-stylistyczne. |
| amperomierz | ograniczone | wysoka | 1 / 1 | Właściwa nazwa przyrządu w obwodzie elektrycznym. Termin szkolny/techniczny może należeć do szerokiego POP mimo tej klasy. |
| kurara | ograniczone | wysoka | 3 / 3 | Trzy konteksty dotyczą trucizny, także w porównaniu. Nazwa specjalnego desygnatu obecna w prozie, nie przypadkowy ciąg liter. |
| pedancik | ogólne | niska | 0 / 0 | Regularne ekspresywne zdrobnienie nazwy osoby pedantycznej. Ocena przydatności opiera się na budowie i rozumieniu, bo live nie dostarczył kontekstu. |
| niemelodyjny | ogólne | niska | 0 / 0 | Zwykłe przeczące określenie braku melodyjności. Brak kontekstu pozostawia otwarty zasięg użycia, nie czyni słowa marginalnym. |
| portowiec | ogólne | wysoka | 3 / 3 | Trzy użycia nazwy pracownika portu w tekstach o życiu i pracy ludzi. Bez pomylenia z nazwą drużyny. |
| ryba | ogólne | wysoka | 3 / 3 | Zwykły rzeczownik o zwierzęciu i żywności oraz utrwalona przenośnia o ważnych osobach; dowód zgodny. |
| siedmiogodzinny | ogólne | wysoka | 3 / 3 | Przejrzyste określenie czasu rozmowy, spektaklu i płaczu; różne zwykłe sytuacje, nie termin. |
| wywiadowczyni | ograniczone | średnia | 1 / 1 | Wszystkie dostępne trafienia pochodzą z jednego artykułu pszczelarskiego o pszczołach rozpoznających miejsca. Nie potwierdza to szerokiego użycia nazwy kobiety działającej w wywiadzie. |
| spotwornieć | ogólne | wysoka | 3 / 3 | Trzy odrębne teksty opisują przerażającą zmianę rzeczy, organu lub rynku pracy. Grupa ze spotwornić nie zastępuje własnego dowodu. |
| pozakomórkowy | ograniczone | wysoka | 1 / 1 | Kontekst macierzy poza komórką potwierdza termin biologiczny/medyczny. |
| kikować | ograniczone | wysoka | 1 / 1 | Kontekst podziału łupu wskazuje obserwowanie/stanie na czatach. Pierwotne opracowanie UJK potwierdza także nowe użycie internetowe usuwania z gry/grupy; nie należy ich zlewać. |
| marudnie | ogólne | średnia | 1 / 1 | Przysłówek zwykłej cechy sposobu działania, w poetyckim opisie budzenia. Jeden literacki kontekst nie mierzy znajomości słowa. |
| limfocytowy | ograniczone | wysoka | 3 / 3 | Trzy konteksty dotyczą nazwy białaczki. Precyzyjny termin medyczny, również używany w prasie ogólnej. |
| niebotyczność | ograniczone | średnia | 1 / 1 | Jedyne użycie to abstrakcyjny, podniosły opis wszechrzeczy. Potwierdzony rzeczownik, lecz dowód ma wyraźny rejestr literacki. |
| kozeta | niepewne | niska | 0 / 0 | Dawny słownik Arcta potwierdza nazwę mebla. Nie znaleziono live kontekstu i nie rozstrzygnięto współczesnego zakresu wobec kozetka oraz homonimicznej nazwy osoby. |
| bezgłos | ograniczone | wysoka | 3 / 3 | Trzy poprawne użycia oznaczają ciszę/brak głosu w opisach literackich i eseistycznych; rejestr książkowy. |
| chłoporobotnik | ograniczone | wysoka | 3 / 3 | Współczesne teksty opisują określoną grupę społeczno-zawodową, często historycznie. Termin społeczny nie staje się nieistniejący wskutek historycznego desygnatu. |
| żelatynowy | ogólne | średnia | 3 / 3 | Zwykły przymiotnik materiałowy, poświadczony przy kapsułkach i folii oraz przedsiębiorcy. Specjalność przedmiotów nie zmienia każdego użycia w osobny termin. |
| repetytorium | ogólne | wysoka | 9 / 8 | Prawidłowe użycia szkolne i powtórzeniowe obok trzech najpewniej błędnych zapisów repertorium w kancelarii/tłumaczeniach. Słowo pozostaje ogólne, dowód wymaga odszumienia. |
| konklawista | ograniczone | średnia | 0 / 0 | Autorski tekst Przewodnika Katolickiego używa nazwy uczestnika konklawe, choć live daje 0. Termin religijno-historyczny, nie ocena wieku samego wyrazu. |
| ścieżyna | ograniczone | średnia | 3 / 3 | Dwa pierwsze dokumenty zawierają literackie przytoczenia, trzeci bieżący opis drogi u Wilka. Zdrobnienie o rejestrze książkowym, nie błędne dopasowanie. |
| wypełzły | ograniczone | średnia | 2 / 1 | Dwa cytowane opisy oczu/brwi odpowiadają przymiotnikowi wyblakły. Wąski literacki dowód; nie wspiera go automatycznie częsty czasownik wypełznąć. |
| nieczłowieczy | ograniczone | wysoka | 3 / 3 | Trzy użycia podniosłe lub literackie, w tym poetycki cytat. Znaczenie jest czytelne, ale nie neutralny codzienny rejestr. |
| lobować | ograniczone | wysoka | 3 / 3 | Wszystkie wybrane konteksty opisują sportowe zagranie piłki nad przeciwnikiem. Nie mylić z lobbować. |
| koniunktiwus | ograniczone | średnia | 2 / 1 | Dwa konteksty jednego reportażu przywołują formę koniunktiwu, z czego jeden żartobliwie. Termin gramatyczny; dowód lemmatyzacji nie wyznacza zasięgu ogólnego. |
| rowerzystka | ogólne | wysoka | 3 / 3 | Zwykła nazwa osoby jadącej rowerem, poświadczona w trzech sytuacjach życia codziennego. |
| opierdzielać | ograniczone | wysoka | 3 / 3 | Trzy konteksty potwierdzają wyraźnie potoczny/wulgarny rejestr reprymendy i innego działania. Ograniczenie rejestrem nie oznacza automatycznego wykluczenia. |
| hetmanić | ograniczone | średnia | 2 / 2 | Jeden kontekst literackiego przytoczenia i drugi współczesnej historiozoficznej narracji opisują przewodzenie. Grupa z hetman nie dowodzi szerokiej częstości czasownika. |
| harmonogramować | ograniczone | niska | 0 / 0 | Semantycznie czasownik planowania prac według harmonogramu, o profilu zawodowym. 0 live; ocena wstępna, nie zmierzona częstość. |
| szyfonowy | ogólne | wysoka | 3 / 3 | Różne teksty opisują zwykłe przedmioty wykonane z tkaniny: sztandar, pelerynę, kokardę. Nie wymaga specjalnego kontekstu fachowego. |
| odmoczyć | ogólne | wysoka | 3 / 3 | Trzy konteksty zwykłej czynności moczenia ciała lub przedmiotów. Brak opublikowanego wiersza nie oznacza braku użycia. |
| wiroid | ograniczone | wysoka | 0 / 0 | ZPE i PIORiN potwierdzają rzeczywistą nazwę biologicznego czynnika chorób roślin. Live 0 przy pozytywnym źródle dziedzinowym. |
| dupowaty | ograniczone | wysoka | 2 / 2 | Dwa dokumenty używają obraźliwego potocznego określenia niezaradności/poddańczości. Rejestr ograniczony, dowód właściwy. |
| naskubać | ogólne | niska | 0 / 0 | Przejrzysty czasownik zebrania przez skubanie; proponowana klasa ogólna jest oceną językową, nie wynikiem pomiaru znajomości. Live 0. |
| ujeździć | ograniczone | wysoka | 3 / 3 | Dwa użycia dotyczą przysposobienia zwierzęcia do jazdy, trzecie formy nieujeżdżony. Własne poświadczenia istnieją; dziedzina jeździecka. |
| podrzemać | ogólne | wysoka | 3 / 3 | Trzy zwykłe konteksty krótkiego odpoczynku/snu; produktywne codzienne użycie czasownika. |
| wiwera | ograniczone | wysoka | 0 / 0 | WSJP potwierdza nazwę zoologiczną i przytacza użycie prasowe z 2020 r. Live 0 nie uprawnia do marginalizacji. |
| jedyność | ograniczone | wysoka | 3 / 3 | Trzy abstrakcyjne użycia eseistyczne/literackie; prawidłowa nazwa cechy, wyraźnie książkowa. |
| szampiter | ograniczone | średnia | 0 / 0 | Opracowanie językoznawcze dokumentuje dawną żartobliwą nazwę szampana, a słownik powiatu poznańskiego regionalne szampon. Potrzebne rozdzielenie znaczeń; live 0 nie uzasadnia automatycznego odrzucenia obu. |
| poszeregować | ogólne | średnia | 2 / 2 | Dwa konteksty układania myśli i materiałów według cech; zwykła zrozumiała czynność, bez wymaganego żargonu. |
| koronawirus | ogólne | wysoka | 3 / 3 | W trzech tekstach ogólnych opisuje pandemię i codzienne ograniczenia. Pochodzenie biologiczne nie ogranicza jego współczesnego rejestru do biologów. |
| okruchowy | ograniczone | niska | 0 / 0 | Przymiotnik o prawdopodobnym zastosowaniu materiałowym/geologicznym; bez live kontekstu zasięg pozostaje słabo rozpoznany. Nie przypisuję marginalności za sam brak. |
| deminutywny | ograniczone | wysoka | 7 / 1 | Wszystkie siedem trafień pochodzi z jednego tekstu językoznawczego: pięć przymiotników i dwa człony adja. Właściwy termin, lecz nie siedem niezależnych świadectw. |
| anyżowy | ogólne | wysoka | 3 / 3 | Trzy konteksty smaków cukierków i napojów; zwykły przymiotnik kulinarny. |
| ćwierćnuta | ograniczone | średnia | 1 / 1 | Kontekst metaforyczny zachowuje znaczenie muzycznej wartości nuty. Termin szkolny może być przydatny w szerokim POP. |
| niecelność | ogólne | średnia | 1 / 1 | Zwykła nazwa braku celności w narracji. Jedno poświadczenie nie wystarcza do pomiaru rozpowszechnienia, lecz nie wskazuje dziedziny specjalnej. |
| zaważać | ogólne | wysoka | 3 / 3 | Dwa z trzech kontekstów poprawnie opisują wpływ na życie/decyzję. Trzeci to zapewne uszkodzone zauważa; nie wolno liczyć go jako poprawnego użycia. |
| podjarać | ograniczone | wysoka | 3 / 3 | Trzy konteksty ekscytacji, w tym reportaż i popularyzacja nauki. Potoczne znaczenie żywe, niezależne od dosłownego rozpalania. |
| niereligijny | ogólne | wysoka | 3 / 3 | Zwykły przymiotnik opisujący przyczyny, ideologię i wierzenia; różne konteksty społeczne. |
| gatunkować | ograniczone | niska | 0 / 0 | Czasownik klasyfikowania według gatunku/klasy ma profil zawodowy. Brak live pozostawia użycie bez potwierdzenia w tej próbie. |
| dotaszczyć | ogólne | wysoka | 3 / 3 | Trzy narracje opisują przemieszczenie człowieka lub zakupów z wysiłkiem; zwykły czasownik. |
| dolomitowy | ograniczone | wysoka | 2 / 2 | Dwa konteksty dotyczą skały i pyłu w badaniu technicznym. Właściwy przymiotnik mineralogiczny/materiałowy. |
| bezołowiówka | ogólne | wysoka | 2 / 2 | Dwa teksty prasowe o cenie i zużyciu paliwa potwierdzają codzienną potoczną nazwę benzyny bezołowiowej; bez wąskiego żargonu grupy. |
| mirakl | ograniczone | wysoka | 2 / 2 | Dwa teksty dotyczą historycznego gatunku widowiska i inspiracji muzycznej. Żywy termin historii kultury, nie dowód archaizacji narracji. |
| rozplatać | ogólne | wysoka | 3 / 3 | Literalne rozplatanie włosów i metafory wyjaśniania związków/zdarzeń; zwykłe użycie w różnych tekstach. |
| lunonauta | ograniczone | średnia | 0 / 0 | Autorski artykuł Uranii używa nazwy uczestnika wyprawy księżycowej; 0 live nie oznacza nieistnienia. Wąski termin astronautyczny. |
| roztrzepotać | ograniczone | średnia | 3 / 3 | Trzy obrazowe użycia imiesłowu przy skrzydłach, sercu i dłoniach. Rejestr literacki; nie dowód wszystkich form czasownika. |
| kooperatyzm | ograniczone | wysoka | 3 / 3 | Trzy teksty o współdziałaniu/spółdzielczości i ideach społecznych. Prawidłowy termin społeczno-ekonomiczny. |
| sansara | ograniczone | wysoka | 2 / 2 | Dwa teksty objaśniają religijny cykl narodzin i śmierci. Dodatni dowód specjalnego słownictwa religijnego. |
| ławkowiec | ograniczone | średnia | 1 / 1 | Kontekst pracy malarskiej zestawia duże narzędzia z cienkimi; odpowiada nazwie pędzla. Jeden literacki przykład, specjalne narzędzie. |
| rozminowywać | ogólne | wysoka | 3 / 3 | Dwa dosłowne opisy usuwania min oraz metafora likwidowania napięcia społecznego. Czasownik wykracza poza instrukcję zawodową. |
| omnipotentny | ograniczone | wysoka | 3 / 3 | Trzy książkowe użycia wszechmocy w krytyce i eseistyce. Sens zgodny, ograniczenie rejestrem erudycyjnym. |
| cieszanowski | ograniczone | wysoka | 1 / 1 | Kontekst sceny wydarzenia w Cieszanowie; lokalny przymiotnik, nie przypadkowe nazwisko. |
| antykorowski | ograniczone | wysoka | 1 / 1 | Kontekst ulotek skierowanych przeciw KOR; wąska historia polityczna. Prawidłowy przymiotnik od nazwy organizacji. |
| modularność | ograniczone | wysoka | 2 / 2 | Dwa własne użycia w piśmie Programista opisują budowę oprogramowania. Termin techniczny; brak wiersza publikacyjnego nie usuwa pozytywnego dowodu. |
| dekstran | ograniczone | wysoka | 1 / 1 | Jedyny kontekst dotyczy środka podawanego w szpitalu. Termin farmaceutyczny, poprawnie rozpoznany semantycznie. |
| młociński | ograniczone | wysoka | 3 / 3 | Trzy dokumenty opisują park/las związany z Młocinami; nazewnictwo lokalne. Wielka litera w nazwie obiektu nie czyni automatycznie dowodu bezwartościowym. |
| nieoczywistość | ogólne | średnia | 3 / 3 | Zrozumiała ogólna cecha braku oczywistości; próbka skupiona w krytyce literackiej, ale znaczenie nie jest terminem tej dziedziny. |
| malinówka | ogólne | wysoka | 3 / 3 | Poprawne użycia domowej nalewki i odmiany jabłek. Wieloznaczność nie jest sama w sobie błędem dopasowania. |
| superstrat | ograniczone | średnia | 0 / 0 | WSJP przy haśle substrat cytuje rzeczywiste użycie superstrat w opisie relacji języków. Termin językoznawczy, mimo 0 live. |
| profitka | ograniczone | wysoka | 0 / 0 | Autorski katalog Muzeum Kresów używa nazwy części lichtarza. Rzeczywisty termin muzealny, nie dowód ogólnego użycia; live 0. |
| subtropikalny | ogólne | wysoka | 3 / 3 | Trzy opisy podróżnicze klimatu, lasu i przyrody; przymiotnik geograficzny używany poza specjalistycznym wywodem. |
| szambiarka | ogólne | wysoka | 3 / 3 | Trzy codzienne/podróżnicze konteksty pojazdu asenizacyjnego; zwykła nazwa pojazdu i usługi. |
| przebiśnieg | ogólne | wysoka | 3 / 3 | Literalne kwiaty oraz czytelna przenośnia; zwykła nazwa przyrodnicza w różnych tekstach. |
| kocborowski | ograniczone | niska | 0 / 0 | Budowa wskazuje lokalny przymiotnik od nazwy miejsca. Bez live nie potwierdzono konkretnej podstawy i zasięgu; klasyfikacja prowizoryczna. |
| wyiskrzyć | ograniczone | średnia | 1 / 1 | Jedno świadome obrazowe użycie w powieści. Potwierdza formę literacką, nie samodzielnie szeroką produktywność. |
| strzępiak | ograniczone | wysoka | 0 / 0 | Oficjalny wykaz grzybów parku narodowego podaje kilka nazw gatunków. Termin przyrodniczy z pozytywnym źródłem mimo 0 live. |
| dejman | ograniczone | średnia | 1 / 1 | Dwa trafienia z jednych wspomnień marynarza; przeczytany kontekst ludzi szykujących się do zejścia wskazuje nazewnictwo załogi. Dokładnej definicji funkcji nie dopowiadam. |
| metkownica | ogólne | średnia | 1 / 1 | Nazwa ręcznego urządzenia do metkowania, w kontekście techniki druku. Przedmiot codziennego handlu, nie wyjątkowy termin naukowy. |
| krwawica | ogólne | wysoka | 3 / 3 | Trzy teksty używają ekspresywnej nazwy ciężko wypracowanych środków; współczesny sens ogólny. |
| laminarny | ograniczone | wysoka | 3 / 3 | Właściwe użycia przy komorze, skrzydle i wentylacji. Termin techniczny utrzymuje sens także w metaforze literackiej. |
| paranormalność | ograniczone | średnia | 3 / 3 | Trzy konteksty dyskusji o nadnaturalnych zjawiskach; abstrakcyjny termin tego obszaru. Nie oceniam prawdziwości opisywanych zjawisk. |
| przerąbywać | ogólne | średnia | 1 / 1 | Poprawny kontekst rąbania bala siekierą; zwykła czynność manualna, mimo małej próby. |
| szałaputka | niepewne | niska | 0 / 0 | Brak live oraz brak trafnego pierwotnego wyniku w celowanej kwerendzie WSJP. Nie przesądzam wieku ani zasięgu samej nazwy osoby. |
| rajszewski | ograniczone | niska | 0 / 0 | Przymiotnik o strukturze lokalnej nazwy relacyjnej. Bez kontekstu nie potwierdzono dokładnej podstawy i obiegu; wstępna kategoria lokalna. |
| osjakowski | ograniczone | niska | 0 / 0 | Przymiotnik o strukturze lokalnej nazwy relacyjnej. Live 0; ocena lokalnego zakresu jest wstępna, bez utożsamienia braku z marginalnością. |
| gul | ogólne | średnia | 10 / 4 | Występuje jako odgłos/przywołanie ptaka oraz potoczne określenie uczucia w gardle. Dwa dalsze trafienia są mniej jasne; miary interj nie wystarczają dla każdego homonimu rzeczownikowego. |
| kapralina | niepewne | niska | 0 / 0 | Live 0 i brak właściwego wyniku celowanej kwerendy WSJP. Nie rozstrzygnięto między dawną nazwą a ewentualnym nowym użyciem; brak nie stanowi werdyktu. |
| ruptura | marginalne | wysoka | 7 / 4 | WSJP oznacza nazwę przepukliny jako przestarzałą. Z siedmiu trafień jeden cytat jest hiszpański, sześć odnosi się do choroby w narracji historycznej/stylizowanej. |
| aroniowy | ogólne | wysoka | 3 / 3 | Przymiotnik produktu spożywczego, poświadczony przy przetworach i napojach; dwie próbki branżowe nie czynią sensu wyłącznie fachowym. |
| fraszkopis | ograniczone | średnia | 1 / 1 | Kontekst osoby piszącej fraszki w czasopiśmie literackim; książkowa nazwa twórcy, nie błąd. |
| zaciemnienie | ogólne | wysoka | 3 / 3 | Dwa abstrakcyjne użycia utrudnienia rozumienia oraz dosłowne nocne zaciemnienie. Własny rzeczownik ma dowód niezależny od dużej rodziny czasowników. |
| odwłóczyć | marginalne | wysoka | 1 / 1 | Właściwy cytat dawnej wypowiedzi o odłożeniu operacji; WSJP ma przest. Sama data wydania biografii nie dowodzi neutralnego współczesnego użycia. |
| manipuł | niepewne | niska | 0 / 0 | Live 0; nie ustalono w tej kwerendzie, które znaczenie i jaki współczesny obieg mają być oceniane. Potrzebne źródło znaczeniowe przed oceną POP. |
| niezwłoczność | ograniczone | wysoka | 3 / 3 | Dwa teksty prawno-urzędowe i jeden reportaż odnoszący się do procedury. Poprawna abstrakcyjna nazwa właściwości, dominujący rejestr formalny. |
| wykrzyknikowy | ograniczone | średnia | 1 / 1 | Kontekst krytyki stylistycznej potwierdza określenie językoznawcze. Jeden dokument, nie szeroki przekrój użycia. |
| paleozoik | ograniczone | średnia | 1 / 1 | Metafora warstw terenu opiera się na poprawnym terminie geologicznym. Termin szkolny może być odpowiedni dla szerokiego POP. |
| kokotek | ograniczone | średnia | 1 / 1 | Kontekst śląskich potraw wskazuje regionalną nazwę kulinarną/zwierzęcia. Nie jest dowodem znaczeń powiązanej kokotki; precyzyjne mapowanie pozostaje ograniczone. |
| nepotyczny | ogólne | wysoka | 3 / 3 | Trzy użycia w krytyce układów, struktur i działalności publicznej. Zrozumiały przymiotnik ogólnego dyskursu społecznego. |
| lektorium | ograniczone | wysoka | 3 / 3 | Dwa konteksty czytelni i jeden przestrzeni kościelnej; termin instytucjonalny, znaczenia trzeba rozdzielić przed przenoszeniem miar. |
| biochemicznie | ograniczone | wysoka | 3 / 3 | Trzy właściwe opisy działania organizmu; termin sposobu/zakresu wyjaśnienia biologiczno-chemicznego. |
| bojownica | ograniczone | wysoka | 0 / 0 | WSJP potwierdza książkową nazwę kobiety walczącej o idee. Własnego live użycia brak; miary grupy z bojownik nie są zastępczym poświadczeniem tej formy. |
| proweniencyjny | ograniczone | wysoka | 3 / 3 | Trzy konteksty badania pochodzenia dzieł i zbiorów; termin muzealnictwa/historii sztuki. |
| kaletnik | ogólne | średnia | 3 / 3 | Trzy właściwe użycia zawodu/usługi, w tym współczesnej naprawy. Potwierdzają kaletnik:Sm1; homonim kaletnik:Sm3 pozostaje bez dowodu. |
| posuć | niepewne | niska | 0 / 0 | Brak live i brak trafnego wyniku celowanej kwerendy WSJP. Nie wyprowadzam marginalności ani znaczenia ze współczesnego posypać przez samą analogię. |
| cegłówka | ogólne | wysoka | 3 / 3 | Trzy zwykłe opisy cegły, także metaforyczne; potoczny rzeczownik o szerokim zastosowaniu. |
| zniczek | ogólne | niska | 0 / 0 | Regularne zdrobnienie codziennej nazwy przedmiotu. Ocena semantyczna bez znalezionego kontekstu; nie badano rozpoznawalności graczy. |
| tomahawk | ograniczone | wysoka | 3 / 3 | Trzy poprawne nazwy broni w opisach/rzeźbie i prozie. Termin kulturowy używany współcześnie, bez dowodu archaizacji samego wyrazu. |
| mauretański | ograniczone | wysoka | 2 / 2 | Dwa dokumenty o historii i architekturze Maurów; poprawny przymiotnik kulturowo-historyczny, nie ogólna codzienna relacja. |
| elementarność | ograniczone | średnia | 3 / 3 | Trzy użycia abstrakcyjne w krytyce i filozofii; sens zgodny, rejestr erudycyjny. Nie marginalizować z powodu samej rzadkości. |
| pracodawczy | ograniczone | średnia | 1 / 1 | Poprawny kontekst inicjatyw zatrudnieniowych; profil instytucjonalny. Jedno użycie, brak podstaw do pewnej oceny szerokiego obiegu. |
| pozlepiać | ogólne | wysoka | 3 / 3 | Trzy użycia rzeczy złączonych w całość lub chaotycznie sklejonego dzieła; zwykła czynność i przenośnia. |
| nabieracz | niepewne | niska | 0 / 0 | Dwa homonimy o różnym rodzaju, lecz brak live kontekstu. Nie ustalono, czy dowód ma dotyczyć osoby, narzędzia czy innego sensu. |
| kanalikowy | ograniczone | niska | 0 / 0 | Relacyjny przymiotnik od kanalika ma prawdopodobnie profil techniczny/anatomiczny. Brak kontekstu pozostawia dokładny sens otwarty. |
| terminarzyk | ogólne | niska | 0 / 0 | Przejrzyste zdrobnienie terminarza, nazwy codziennego przedmiotu. Propozycja semantyczna bez potwierdzenia live; nie wniosek o częstości. |
| troszka | niepewne | średnia | 8 / 8 | Osiem wyników miesza rzeczownikową małą ilość, przysłówkowe troszkę, regionalne troszka i po troszku. Potrzebne rozdzielenie jednostek; nie przenosić powszechności troszkę na każdy rzeczownikowy paradygmat. |
| kaktusowaty | niepewne | średnia | 2 / 2 | Oba wyniki odnoszą się do rodziny kaktusowatych, nie jasno do przymiotnika podobny do kaktusa. Znaczenie botaniczne jest rzeczywiste, lecz przejście od kaktusowate do badanego przymiotnika niezamknięte. |
| staniczek | ogólne | wysoka | 3 / 3 | Zdrobnienie zwykłej części odzieży w wypowiedziach i reportażu; jeden cytat piosenki nie wyczerpuje dowodu. |
| płomiennowłosy | ograniczone | średnia | 2 / 2 | Dwa obrazowe opisy osoby o rudych włosach, w reportażu i grze. Rejestr literacki/ekspresywny, bez błędu analizy. |
| judaszowski | ograniczone | niska | 0 / 0 | Przymiotnik o możliwej biblijnej/przenośnej funkcji, ale live 0. Ocena rejestru wstępna; brakuje odczytanego kontekstu dla konkretnego sensu. |
| balneator | niepewne | niska | 0 / 0 | Live 0; wyszukiwanie przyniosło łacińskie nazewnictwo zawodu, które nie potwierdza współczesnego polskiego użycia. Potrzebne właściwe źródło językowe. |
| minirobota | niepewne | niska | 0 / 0 | Brak live i brak właściwego wyniku WSJP. Sam prefiks mini- nie wystarcza do ustalenia znaczenia ani zasięgu całego hasła. |
| zabawność | ogólne | średnia | 3 / 3 | Prawidłowa ogólna nazwa cechy, choć trzy wybrane teksty są literackie. Nie jest to automatycznie termin literaturoznawczy. |
| symplifikować | ograniczone | wysoka | 1 / 1 | Jedyny kontekst socjologiczno-filozoficzny potwierdza erudycyjny czasownik upraszczania. |
| dorozumieć | ograniczone | wysoka | 3 / 3 | Trzy właściwe użycia rozumienia przez wnioskowanie, w esejach i prozie. Rejestr książkowy; nie wyłącznie cytat historyczny. |
| medresa | ograniczone | wysoka | 3 / 3 | Trzy właściwe użycia szkoły muzułmańskiej w reportażach; termin kulturowy. Podobne serie wydawnicze nie są trzema niezależnymi badaniami znajomości. |
| kuracjuszka | ogólne | wysoka | 3 / 3 | Zwykła nazwa uczestniczki kuracji/sanatorium; trzy odmienne bieżące sytuacje i dialog. |
| kodeina | ograniczone | wysoka | 3 / 3 | Trzy trafienia dotyczą substancji/leku, w tym tekst historyczny i cytat artystyczny. Poprawny termin farmaceutyczny; korpusowy przekrój nie mierzy znajomości ogólnej. |
| planistyka | ograniczone | wysoka | 3 / 3 | Poprawne użycia w planowaniu, urbanistyce i ekonomii, także wyliczenie w powieści. Termin dziedzinowy, nie błąd dopasowania. |
| pęca | ograniczone | niska | 0 / 0 | Pierwotne opracowanie słownictwa potwierdza nazwę elementu wyposażenia ptaka łowczego. Brak live pozostawia otwarty dzisiejszy obieg i stosunek do pęc; termin sokolniczy, nie automatycznie martwy. |
| domcio | ogólne | średnia | 2 / 2 | Dwa poprawne współczesne konteksty zdrobniałej nazwy domu. Ekspresywność rodzinna/żartobliwa nie jest tu wąskim żargonem. |
| pasywizacja | ograniczone | wysoka | 0 / 0 | Aktualny opis zajęć UW używa terminu operacji składniowej. Mocne właściwe źródło specjalistyczne mimo 0 live. |

## Dodatkowe źródła pierwotne

- **przedryndać** — [WSJP: właściwe hasło i przykłady przejechania trasy; nie wyniki KWJP live.](https://wsjp.pl/haslo/podglad/111647/przedryndac/5263631/500-km)
- **siejba** — [WSJP kwalifikuje nazwę siewu jako dawną.](https://wsjp.pl/haslo/podglad/119994/siejba)
- **kikować** — [Opracowanie UJK rozróżnia obserwowanie i nowe znaczenie usuwania z gry/grupy.](https://obserwatorium-mlodziezy.ujk.edu.pl/jednostki/kikowac/)
- **kozeta** — [Historyczny słownik Arcta: nazwa mebla; nie dowód aktualnego obiegu.](https://pl.wikisource.org/wiki/M._Arcta_S%C5%82ownik_ilustrowany_j%C4%99zyka_polskiego/K_%28ca%C5%82o%C5%9B%C4%87%29)
- **konklawista** — [Autorski artykuł Małgorzaty Jańczak używa nazwy uczestnika konklawe; historyczny temat nie przesądza wieku wyrazu.](https://www.przewodnik-katolicki.pl/Archiwum/2004/Przewodnik-Katolicki-48-2004/Historia/Jak-wybierano-papiezy)
- **wiroid** — [Materiał dydaktyczny ZPE o wiroidach.](https://zpe.gov.pl/a/przeczytaj/DQN7i4ibO)
- **wiroid** — [PIORiN: nazwy wiroidów w wykazie agrofagów; badamy użycie słowa, nie przepisy.](https://www.gov.pl/web/piorin/regulowane-agrofagi-niekwarantannowe-dla-unii)
- **wiwera** — [WSJP: zoologiczna nazwa i cytat prasowy 2020.](https://wsjp.pl/haslo/podglad/117600/wiwera)
- **szampiter** — [Autorska analiza języka Boya, s.45: szampiter jako szampan; materiał historyczny.](https://www.poradnikjezykowy.uw.edu.pl/wydania/poradnik_jezykowy.796.2022.07.3-U.Sokolska.pdf)
- **szampiter** — [Słownik regionalny powiatu: szampiter jako szampon. Osobna ścieżka znaczeniowa.](https://smakipowiatupoznanskiego.pl/slownik-gwary-poznanskiej/)
- **lunonauta** — [Autorski artykuł Uranii używa nazwy uczestnika wyprawy księżycowej.](https://www.urania.edu.pl/zasoby/ksiezyc-ludzie-i-slowa.html)
- **superstrat** — [WSJP cytuje superstrat przy opisie relacji języków; nie jest to odrębne hasło superstrat.](https://wsjp.pl/haslo/podglad/20796/substrat/5157958/w-jezykoznawstwie)
- **profitka** — [Autorski opis eksponatu: część lichtarza; poświadczenie użycia muzealnego.](https://muzeumkresow.eu/eksponat/lichtarz-3/)
- **strzępiak** — [Oficjalny wykaz grzybów PN Bory Tucholskie, pozycje 215–224: nazwy gatunków.](https://pnbt.gov.pl/pliki-do-pobrania/otworz/a7b93254-3b32-4d4e-b9a5-c6641d00d381.pdf)
- **ruptura** — [WSJP: przestarzała nazwa przepukliny.](https://wsjp.pl/haslo/podglad/50305/ruptura)
- **odwłóczyć** — [WSJP kwalifikuje czasownik odsunięcia w czasie jako przestarzały.](https://wsjp.pl/haslo/podglad/124654/odwloczyc)
- **bojownica** — [WSJP: książkowa nazwa kobiety walczącej o idee, niezależna od bojownik.](https://wsjp.pl/haslo/podglad/129634/bojownica)
- **pęca** — [Opracowanie leksykalne UAM: wyposażenie ptaka łowczego; zestawienie historycznych rejestracji, nie pomiar współczesnego zasięgu.](https://repozytorium.amu.edu.pl/bitstream/10593/464/2/S%C5%81OWNIK.pdf)
- **pasywizacja** — [Autorski opis zajęć UW, cykle 2025Z/2026Z, potwierdza termin składniowy.](https://informatorects.uw.edu.pl/pl/courses/view?prz_kod=3301-ZJ-WM-JF003)

Daty dostępu: 12.10.2026. Odczyt zewnętrzny obejmował treść hasła albo indeksowany fragment źródła, nie cały każdy dokument PDF. Wyników SJP.pl nie używano jako normy ani przesłanki klasy.
