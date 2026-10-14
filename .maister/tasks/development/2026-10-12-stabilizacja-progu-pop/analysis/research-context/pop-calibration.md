# Granica POP: limit liczby a siła dowodów

## TL;DR

Limit 60 tys. nie jest ustaloną granicą między słowami zwykłymi a resztą. Większy limit dodaje również sensowne słowa.
Samo podniesienie do 70 lub 80 tys. nie rozwiązuje problemu: zwykłe słowa pozostają niżej, a słabe dopasowania trafiają wyżej.
Stały próg punktacji usuwa konkurencję o miejsca w zbadanej zmianie STANDARD, ale nadal wymaga kalibracji i jawnej obsługi braków danych.
Wyniki są materiałem do decyzji. Nie zmieniono produkcyjnego POP, STANDARD, konfiguracji ani wydania.

## Key Decisions

- **Korekta rekomendacji z rundy 4:** poprawność algorytmu nie uzasadnia zachowania limitu 60k. Wycofuję zalecenie, aby samo odtworzenie ubytków zamykało rozmowę o granicy POP.
- **Rekomendacja metodologiczna:** skład powinien wynikać z jawnych wymagań dowodowych. Rozmiar jest wynikiem i miarą kosztu, a nie samodzielnym dowodem popularności.
- **Bez wyboru magicznej liczby:** 60 025 usuwa konkretny ubytek przez dopasowanie do bloku remisów; 70k, 80k i próg 0,05 również nie są potwierdzoną granicą znajomości słów. Dodatki do STANDARD, cofnięcia i zmiana POP pozostają odrębnymi, niezatwierdzonymi decyzjami.

## Open Questions / Risks

- Trzeba rozstrzygnąć zakres POP: szeroki współczesny zasób obejmujący słowa książkowe, szkolne i dziedzinowe czy węższy zasób ogólnego użytku. Klasa „ograniczone” w badaniu nie oznacza odrzucenia.
- Korpus mierzy użycie w swoich tekstach, nie znajomość słowa przez gracza. Brak w opublikowanej tabeli nie oznacza braku współczesnego użycia. Oceny językowe mają średnią pewność; osobne tory tego samego modelu i punktowe źródła nie zastępują reprezentatywnego badania ludzi.
- Stały próg nie gwarantuje niezmienności przy nowych źródłach, zmianie grupowania, mapowania i znaczeń. Zachowane wyjątki grupowe też wymagają jawności.

## Pytanie i zakres

Czy podniesienie limitu poprawia POP i czy lepiej wyznaczać jego skład minimalną siłą dowodów użycia? Badanie wykonano na obecnym `pop-v2`, osobno dla obecnego STANDARD i propozycji **+2382 form** z rundy 3. Nie dołączono osobnej propozycji cofnięć z rundy 4. POP0 nie był przedmiotem nowej kalibracji.

Pierwotne porównanie 60k/80k używało percentyli i `available-only`. Obecna metoda używa log-ipm, przycinania członków, grup wariantów i innych reguł braków. Historia zawiera wcześniejsze przeglądy próbek, lecz stare porównanie limitów nie rozstrzyga dzisiejszej granicy. Źródła i historia: [przegląd metodologii](../analysis/findings/round5/methodology-sources.md), [ADR-007](../../../../../docs/adr/ADR-007-metoda-pop-v1.md).

## Metoda i źródła

- **27 wariantów × 2 STANDARD:** 10 limitów liczby, 6 stałych progów punktacji, 8 filtrów dyspersji na liście 80k i 3 absolutne kryteria KWJP. Dodatkowo siatka 25 kombinacji ARF/ilorazu dla obu populacji.
- **300 różnych podstaw lematu:** po 40 z sześciu kolejnych pasm 40–100k; po 20 rozbieżności punktacji, rozbieżności dyspersji i nazwanych kontroli. Dobór hashujący ze stałym ziarnem; kontrole analizowane osobno.
- Dwa tory oceniały po 150 haseł bez znajomości pasma, progu ani przynależności. Koordynator ocenił 30 powtórnie; częściowe obserwacje torów były mu znane, więc nie jest to całkowicie niezależna ślepa replikacja.
- **300 zapytań KWJP, 1342 pobrane konkordancje, 0 błędów końcowego dostępu.** Liczba pobranych wyników różni się od liczby przeczytanych. Odczyt ograniczono zwykle do trzech różnych dokumentów; sporne przypadki rozszerzono.
- Pokryto pięć kategorii: kod, decyzje projektu, konfigurację/testy, przypięte dane i źródła pierwotne. Zewnętrzne podstawy obejmują dokumentację korpusów, publikacje metodologiczne, słowniki i teksty dziedzinowe.

Dokładny [plan](../planning/round5-plan.md), [dobór próby](../analysis/findings/round5/sample-design.json), [manifest kontekstów](../analysis/findings/round5/context-manifest.json), [rejestr źródeł](../planning/sources.md). Własne oceny i identyfikatory publikujemy; pełne teksty korpusów i surowy NKJP pozostają poza repozytorium. Nie importowano list znajomości słów ani zasobów o nierozstrzygniętej dopuszczalności.

KWJP opisuje redagowaną polszczyznę pisaną 2011–2020, z udziałami 35% publicystyki, 35% faktu i 30% fikcji. Tabela ogólna publikuje jednostki od F≥5. To istotne ograniczenie dla słów potocznych i rzadkich. [Opis KWJP](https://kwjp.pl/overview), [dokumentacja list](https://kwjp.pl/lists/doc/about/). Literatura uzasadnia rozróżnienie częstości, rozproszenia i znajomości; nie dostarcza polskiej granicy 70k, ARF=3 lub 0,05. [Adelman i in.](https://wrap.warwick.ac.uk/399/1/WRAP_Adelman_cdps4.pdf), [Gries](https://stgries.info/research/2020_STG_Dispersion_PHCL.pdf). Dla Brysbaerta i Hlaváčovej wykorzystano tylko dostępne abstrakty; zakres dostępu zapisano w przeglądzie źródeł.

## Co daje większy limit

Limit liczy leksemy **przed przycięciem**. Cały blok remisów wchodzi albo odpada; stąd np. limit 60k daje 53 002 zachowane leksemy. Formy obejmują ich pełną dopuszczoną odmianę.

| Limit | Leksemy po przycięciu | Formy obecnego STANDARD | Przyrost form względem 60k | Pokrycie KWJP–STANDARD |
|---|---:|---:|---:|---:|
| 40k | 32 259 | 837 241 | −390 009 | 97,9934% |
| 50k | 42 473 | 1 038 227 | −189 023 | 98,4303% |
| 60k | 53 002 | 1 227 250 | 0 | 98,5951% |
| 65k | 58 086 | 1 325 930 | +98 680 | 98,6273% |
| 70k | 63 015 | 1 424 934 | +197 684 | 98,6458% |
| 75k | 67 321 | 1 516 043 | +288 793 | 98,6539% |
| 80k | 72 997 | 1 636 683 | +409 433 | 98,6600% |
| 90k | 79 852 | 1 777 209 | +549 959 | 98,6638% |
| 100k | 85 669 | 1 895 041 | +667 791 | 98,6654% |

Źródło: [pełne pomiary baseline](../analysis/findings/round5/baseline-measurements.json). Mianownik KWJP–STANDARD wynosi 74 540 021. Drugi, stały mianownik KWJP–all wynosi 81 664 894; dla 60/70/80k pokrycie wynosi odpowiednio **89,9931% / 90,0395% / 90,0523%**. Nie jest nim nominalne 100 mln słów korpusu. Przy proponowanym STANDARD pierwszy mianownik rośnie do 74 542 063.

Zysk 70k→80k to **211 749 form i 0,0142 punktu procentowego** pokrycia KWJP–STANDARD. Mały przyrost pokrycia nie dowodzi małej wartości słów: częste jednostki dominują w tej metryce. To pomiar dopasowania do korpusu użytego także do rankingu, a nie niezależny test trafności POP.

## Skąd pochodzą dowody na kolejnych pasmach

Pasmo to nowe podstawy lematu między zbiorami po przycięciu. Nie jest różnicą liczby leksemów. „Własny KWJP” oznacza oryginalny wiersz, którego wszyscy kandydaci mają tę samą podstawę; nie potwierdza automatycznie sensu.

| Pasmo | Nowe podstawy | Bez własnego wiersza KWJP | Odsetek | Mediana sumy F własnych wierszy, gdy istnieją |
|---|---:|---:|---:|---:|
| 40–50k | 9 930 | 110 | 1,11% | 30 |
| 50–60k | 10 295 | 1 450 | 14,08% | 12 |
| 60–70k | 9 837 | 4 981 | 50,64% | 7 |
| 70–80k | 9 881 | 8 409 | 85,10% | 6 |
| 80–90k | 6 814 | 6 398 | 93,89% | 6 |
| 90–100k | 5 784 | 5 596 | 96,75% | 6 |

Źródło: [pełne profile pasm](../analysis/findings/round5/band-profiles.json), potwierdzone własnym SQL recenzenta. Dalej wybór coraz mocniej zależy od NKJP i reguł braków. **To nie jest odsetek złych słów.** Brak publikacji może wynikać z progu F, segmentacji, mapowania lub niejednoznaczności. Z drugiej strony starszy NKJP nie zawsze świadczy o dzisiejszym użyciu.

## Ocena językowa próbki

Łącznie utrwalono **104 oceny „ogólne”, 170 „ograniczone”, 9 „marginalne”, 2 „błędne dopasowanie” i 15 „niepewne”**. To nie są automatyczne przyjęcia i odrzucenia. „Ograniczone” obejmuje m.in. terminy szkolne, zawody, hobby, słowa książkowe i rejestr potoczny. Nie wolno traktować 170 takich ocen jako błędów POP.

| Pasmo: po 40 haseł | Ogólne | Ograniczone | Marginalne | Błędny dowód | Niepewne | Zerowe wyniki live |
|---|---:|---:|---:|---:|---:|---:|
| 40–50k | 23 | 17 | 0 | 0 | 0 | 0 |
| 50–60k | 18 | 22 | 0 | 0 | 0 | 2 |
| 60–70k | 9 | 28 | 2 | 0 | 1 | 2 |
| 70–80k | 10 | 28 | 0 | 1 | 1 | 5 |
| 80–90k | 10 | 21 | 3 | 1 | 5 | 20 |
| 90–100k | 8 | 24 | 2 | 0 | 6 | 27 |

Widać zmianę proporcji względem wewnętrznych pasm, lecz **nie ma skoku jakości uzasadniającego dokładnie 70k albo 80k**. Ostatnie pasma mają więcej luk i niskiej pewności. Z 10 ogólnych w paśmie 80–90k siedem ma odczytane konkordancje; z ośmiu w 90–100k tylko trzy. Pozostałe oceny opierają się na źródłach uzupełniających albo jawnie wstępnej interpretacji budowy słowa.

W osobnych 20 rozbieżnościach punktacji było 6 ogólnych, 12 ograniczonych, 1 marginalne i 1 niepewne. W 20 rozbieżnościach dyspersji: 8 ogólnych, 11 ograniczonych i 1 niepewne. W 20 nazwanych kontrolach: 12 ogólnych, 7 ograniczonych i 1 marginalne. To próby celowe; nie wolno zsumowanego odsetka przenosić na cały POP. Również po 40 z pasma nie daje precyzyjnej estymacji błędu całej populacji.

Przeczytano i adnotowano **632 wyniki**: 622 różne pary hasło–zdanie i 621 różnych zdań z **386 dokumentów**. Różnica wynika z kilku trafień w tym samym zdaniu. Pełna pierwsza strona zawierała 1342 wyniki; nie twierdzimy, że przeczytano każdy. 68 zapytań dało zero wyników. **29 ocen ma niską pewność** — pozostają widoczne zamiast udawać rozstrzygnięcie.

| Przykład | Ocena i odczytany dowód | Limit 70k | Limit 80k | Stały próg 0,05 |
|---|---|---:|---:|---:|
| pomiaukiwać, podrzemać, szambiarka | Ogólne; zwykłe czynności i pojazd/usługa w różnych tekstach | tak | tak | tak |
| aroniowy, nepotyczny | Ogólne; produkty spożywcze i dyskurs społeczny | nie | tak | nie |
| odbąknąć, bezołowiówka | Ogólne; trzy zwykłe odpowiedzi w dialogach oraz dwa artykuły o paliwie | nie | nie | nie |
| ćwierćnuta | Ograniczone: termin szkolny, który może być właściwy dla szerokiego POP | tak | tak | tak |
| siejba | Marginalne: przestarzała nazwa, głównie cytaty i stylizacja | tak | tak | tak |
| uherski | Jedyny live to czeska nazwa Uherský Brod; zły dowód na polski przymiotnik pospolity | nie | tak | nie |

Obecność oznacza co najmniej jeden wybrany leksem tej podstawy w baseline, a nie zatwierdzenie wszystkich sensów. Źródła przykładów, dokładne identyfikatory zdań i ocen: [tor A](../analysis/findings/round5/quality-a.json), [tor B](../analysis/findings/round5/quality-b.json); przypisanie do wariantów: [macierz](../analysis/findings/round5/sample-membership.json). Błędny dowód nie oznacza, że słowo nie istnieje. Przykłady pokazują ograniczenia zarówno zwiększenia limitu, jak i samego progu punktacji.

Kontrola 30 powtórnych ocen dała **22 zgodne klasy i 8 różnic**. Pięć różnic dotyczy dodatkowych źródeł dla przedryndać, lnicy, miodokwiatu, ostojowego i pyrexu. Pozostałe to granica ogólne/branżowe przy pilarzu oraz wstępne oceny fermentowni i zgorzknialca bez znalezionego kontekstu. Zachowano obie oceny. To jawna miara rozbieżności tego przeglądu, nie współczynnik wiarygodności eksperckiego badania. [Agregacja i różnice](../analysis/findings/round5/quality-summary.json).

**Klasy i poziomy pewności są historią zamrożonego pierwszego przeglądu.** Późniejsza kontrola źródeł B odczytała właściwe fragmenty 17 z 19 adresów; własne hasła przedryndać i bojownica pozostały niedostępne po ponowieniach. Wysoka pewność pierwotnej oceny bojownicy nie oznacza więc zakończonej weryfikacji źródłowej. Znaczenie telefoniczne przedryndać ma osobny odczytany dowód synonimii. Wycofano też przeniesienie kwalifikatora żartobliwości z czasownika szampitrować na rzeczownik szampiter. [Korekty i ograniczenia B](../analysis/findings/round5/quality-b-post-freeze.md). Nie zmieniono wstecz macierzy; tych przypadków nie użyto do wyboru progu.

Tor A podjął próby otwarcia wszystkich 36 uzupełniających adresów: **23 właściwe fragmenty odczytane, 13 ograniczeń dostępu** z zapisanym błędem lub pustą odpowiedzią. Dotyczy to m.in. miodokwiatu, ostojowego i poprzekształcać; ich uzupełnienia pozostają indeksowanymi fragmentami. Zamrożona pewność nie usuwa tych ograniczeń. [Audyt A](../analysis/findings/round5/quality-a-source-access.json). Łącznie uzupełniano 52 hasła, a 40 z 55 wskazanych źródeł sprawdzono przez odczyt właściwego fragmentu. Główne kontrprzykłady w tabeli opierają się na odczytanych konkordancjach; kwalifikator siejby dodatkowo potwierdzono w otwartym WSJP.

## Stały próg a konkurencja o miejsca

Porównanie stosuje tę samą wartość progu do obu STANDARD. Zmienia też przycinanie członków: porównuje własną **punktację zamiast własnej rangi**. Zachowuje istniejące wyjątki najmocniejszego członka oraz grup bez rozdzielnego dowodu. Nie jest czystym kryterium „każdy leksem ma własny mocny dowód”.

| Wariant | Obecny POP: formy | POP przy +2382 STANDARD | Dodatki / ubytki po zmianie STANDARD |
|---|---:|---:|---:|
| Limit 60k | 1 227 250 | 1 227 192 | +2372 / −2430 |
| Limit 60 025 | 1 227 250 | 1 229 622 | +2372 / 0 |
| Limit 70k | 1 424 934 | 1 427 316 | +2382 / 0 |
| Limit 80k | 1 636 683 | 1 639 065 | +2382 / 0 |
| Stały próg dzisiejszego 60k | 1 227 250 | 1 229 622 | +2372 / 0 |
| Stały próg 0,075 | 1 287 853 | 1 290 225 | +2372 / 0 |
| Stały próg 0,05 | 1 443 064 | 1 445 446 | +2382 / 0 |
| Stały próg 0,025 | 1 776 311 | 1 778 693 | +2382 / 0 |

Źródła: [porównanie STANDARD](../analysis/findings/round5/standard-sensitivity.json), [pełne proposal](../analysis/findings/round5/proposal-measurements.json). Próg dzisiejszego 60k to **score ≥ −1,042878629**. Oznaczenie 0,05 znaczy **score ≥ log10(0,05)**, nie score ≥ 0,05 i nie dosłowną częstość każdego słowa w jednym korpusie. Obecna miara ma różne podstawy dla obu źródeł, pojedynczego źródła i braków.

**Wniosek:** stabilizację można oddzielić od poszerzenia. Stała wartość obecnego cięcia odtwarza dzisiejszy POP dokładnie, a po badanych dodatkach nie usuwa innych słów. To uzasadnienie mechanizmu przeciw konkurencji o miejsca, nie dowód trafności historycznego cięcia. Większy limit tylko przesuwa miejsce przyszłej konkurencji. Przy zmianie grafu lub źródeł także stały próg może powodować ubytki.

## Czy dyspersja daje lepsze kryterium

Dyspersję badano na **oryginalnym wierszu KWJP**, z ARF i F tego samego wiersza. Wiele wierszy jednej podstawy łączy warunek OR. Nie dzielono najlepszego ARF przez sumę F grupy ani nie przenoszono dowodu na inną podstawę.

| Diagnostyka na obecnym STANDARD | Leksemy | Formy | Pokrycie KWJP–STANDARD | Braki w straży 20k częstych form |
|---|---:|---:|---:|---:|
| 80k, ARF≥3, ARF/F≥0,1; wymaga własnego KWJP | 55 677 | 1 257 654 | 98,6302% | 0 |
| To samo, zachowuje brak własnego KWJP | 70 873 | 1 603 293 | 98,6302% | 0 |
| 80k, ARF≥3, ARF/F≥0,3; wymaga własnego KWJP | 54 225 | 1 244 311 | 97,4834% | 332 |
| Własne F≥10, ARF≥3, ARF/F≥0,1; bez limitu liczby | 49 184 | 1 122 691 | 98,5650% | 1 |

Pierwsze dwa warianty mają identyczne pokrycie, lecz różnią się o **345 639 form**. Polityka braków jest więc ważną decyzją ukrytą przed samym pokryciem. Wariant bez fallbacku usuwa także słowa z poprawnymi żywymi kontekstami. Straż jest kontrolą regresji, nie pełną oceną sensu; nie każdy jej wpis jest bezsporny.

Próg ilorazu 0,3 odrzuca m.in. **ty, mama, ksiądz**. Nie ma podstaw do jego przyjęcia. Z kolei przy F=5–9 nawet bardzo skupione wystąpienia mogą mieć ARF/F>0,1; sam iloraz nie wystarczy. Wszystkie 25 pól i 11 pełnych wariantów są w [siatce](../analysis/findings/round5/baseline-dispersion-grid.json) i [pomiarach](../analysis/findings/round5/baseline-measurements.json). Rozproszenie jest użyteczną składową dowodu, nie gotowym automatycznym rozstrzygnięciem.

## Weryfikacja i odtwarzanie

Baseline 60k odtworzono jako **dokładnie ten sam zbiór form** co opublikowany POP. Osobny skrypt odtworzył cięcia wszystkich limitów i progów, warianty dyspersji, dobór próby oraz główne pełne zbiory form i pokrycie. Recenzent korzystał z zapisanego grafu i morfologii; nie przebudował ich od surowych danych. Wykonał również 25 istniejących testów POP, wszystkie poprawne. [Zakres niezależnej kontroli](../analysis/findings/round5/measurement-review.md).

W pierwszej sondzie badawczej naprawiono pomijanie dowodów jednostek jednoelementowych i łączenie ARF/F z różnych agregacji. Wadliwy wynik wycofano, diagnostykę i próbkę przeliczono przed oceną. Później poprawiono wyłącznie opisowy licznik braków w trzech wariantach. Te poprawki nie dotyczyły produkcji ani głównego porównania limitów. Historia i hashe są jawne w [manifeście](../analysis/findings/round5/input-manifest.json).

Trwały zapis obejmuje plan, skrypty, przypięcie źródeł, hashe wejść, pełne pomiary, dobór próby, oceny i źródła, stan Maister oraz komentarz do ticketu. Odtworzenie wymaga tych samych lokalnych wejść zgodnie z konfiguracją źródeł; surowych korpusów nie zastępuje sam raport.

Sekwencja pomiaru: `analysis/round3_pop.py bootstrap` przygotowuje cache wejść; `analysis/round5_measure.py` liczy oba scenariusze i próbkę; następnie `analysis/round5_measure.py repair_diagnostics` zapisuje także znaczniki korekty wymagane przez historyczny audyt; `analysis/round5_profiles.py` zapisuje profile; `analysis/round5_independent_check.py` odtwarza pomiar innym kodem. Każdą podaną ścieżkę poprzedza `.maister/tasks/research/2026-10-12-standard-formy-dawne/`; polecenia uruchamia się przez `python3` z katalogu repo. Najbezpieczniej odtwarzać w osobnej kopii przypiętego commita, aby zachować opublikowane pomiary i daty. Zapytania i identyfikatory kontekstów są odtwarzalne przez `analysis/round5_contexts.py`, lecz żywa wyszukiwarka może się zmienić. Oceny językowe to utrwalona interpretacja, a nie deterministyczna prawda o znajomości.

Zmiana produkcyjna, jeśli zostanie uzgodniona, wymagałaby osobno wersjonowanej polityki POP, dokumentacji decyzji i pomiaru skutków wydania. Sam raport ani komentarz nie zmieniają pipeline. To badanie dotyczy wyboru POP po STANDARD; nie zmienia dopuszczalności słów ani zasad gry.

## Rekomendacja do rozmowy

**Nie zalecam teraz zamiany 60k na 80k jako rzekomo merytorycznego rozwiązania.** Badanie potwierdza sens poszerzenia o część niżej ocenionych słów, ale nie potwierdza jednej docelowej liczby. Próg 0,05 ma tę samą słabość: jest mierzalny i powtarzalny, lecz pomija np. odbąknąć, a przyjmuje siejbę. Samo przemianowanie limitu na próg nie rozwiązuje semantyki.

Zalecam przyjąć kierunek: **jawne wymagania dowodowe, rozmiar wynikowy, osobna ocena braków i nieprzypisywalnych znaczeń**. Dla celu szerokiego POP nie wykluczałbym całych klas terminów, słów książkowych czy regularnych derywatów tylko dlatego, że mają mało KWJP. Własne współczesne użycia i zgodność znaczenia muszą mieć odrębną wagę od rankingu grupy. To rekomendacja do uzgodnienia, jeszcze nie kompletna reguła automatyczna ani projekt wdrożenia.

Jeśli osobno chcemy usunąć wypychanie słów przy tej paczce STANDARD, **stały próg obecnego cięcia jest wariantem o najmniejszej zmianie składu**: baseline bez zmian, po dodatkach +2372 i zero ubytków. Może być punktem odniesienia dla stabilizacji, ale zachowuje ograniczenia dzisiejszej granicy i wyjątków. Limit 60 025 jest wyłącznie doraźnym dopasowaniem do tej paczki; nie rekomenduję go jako nowej zasady.

**Pewność:** wysoka dla wielkości zbiorów, mechanizmu limitu i skutków zbadanych wariantów; średnia dla rejestru i zgodności znaczeń; brak pomiaru rozpoznawalności słów przez graczy. **Nie potrzeba teraz kolejnego przypadkowego poszerzania próbki.** Najpierw należy uzgodnić zakres POP i akceptowane rodzaje dowodów. Następne badanie, jeśli będzie potrzebne, powinno sprawdzać konkretną uzgodnioną regułę na odłożonej próbie, a nie szukać liczby pasującej do poznanych przykładów.
