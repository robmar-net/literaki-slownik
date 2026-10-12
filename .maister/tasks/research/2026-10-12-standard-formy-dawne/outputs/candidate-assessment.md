# STANDARD: konkretni kandydaci i wpływ na POP — runda 3

## TL;DR
Propozycja badawcza obejmuje **2382 nowe formy ze 110 rodzin**: 997 z wcześniejszych 3364 kandydatów i 1385 spoza tej paczki.
Sprawdzono wszystkie 290 obecnych przyjęć zależnych od wyjątku; dla 12 wybrane konteksty nie uzasadniają przyjętej analizy.
Ponowne przeliczenie daje STANDARD +2382, POP **+2372 i −2430**, POP0 +481. Sam wzrost STANDARD może więc zmniejszyć POP.
Rekomendacja: omówić tę konkretną paczkę i skutki rankingu; cofanie obecnych przyjęć rozpatrzyć osobno. To nadal research, bez wdrożenia.

## Key Decisions
- Przyjęta wcześniej zasada znaczenia i współczesnej odmiany pozostaje podstawą. Nie dobrano nowego progu frekwencji.
- Każdy dodatek ma wskazaną analizę, rodzinę, dowód znaczenia i zakres odmiany. Nie odblokowujemy całych dawnych etykiet ani całej paczki 3364.
- Pozostałe kryteria STANDARD obowiązują. Książkowość i rzadkość same nie wykluczają słowa.
- Główny pomiar zachowuje obecne przyjęcia. Osobny wariant cofnięcia 12 napisów służy wyłącznie zbadaniu wrażliwości.
- [Wcześniejszy research i uzgodnienie kierunku](research-report.md) pozostają zapisane. Kod produkcyjny, listy, polityka i wydanie nie zostały zmienione.

## Open Questions / Risks
- To szczegółowa propozycja do przeglądu przez właściciela, nie zatwierdzona paczka wydania. Ocena semantyki pochodzi od jednego badacza.
- 2367 z wcześniejszych 3364 napisów nie trafiło do propozycji. Nie oznacza to ich zbiorowego odrzucenia ani zakończenia pełnej ekspertyzy znaczeń.
- Reguła POP zależy od składu STANDARD, homonimów, limitu leksemów i całych bloków remisów. Zmiany trzeba oceniać na obu listach, nie tylko liczyć dodatki.
- Czytnik SGJP i współczesne słowniki nie mają jeszcze zatwierdzonego mapowania do produkcyjnego wejścia. Ten research go nie wdraża.

## 1. Pytanie, metoda i rzeczywiste pokrycie

Po zaakceptowaniu kierunku użytkownik polecił przejść do oceny kandydatów i pomiaru wpływu. Pytanie brzmi: **co konkretnie można uzasadnić według tej zasady i co zmieniłoby się w STANDARD, POP oraz POP0?** [Plan zapisany przed wynikami](../planning/candidate-assessment-plan.md).

| Tor | Wykonano | Granica wniosku |
|---|---|---|
| Dawna paczka | Macierz 404 grup / 3364 unikalnych napisów; sprawdzenie identyfikacji i kwalifikatorów SGJP oraz powiązanie z dostępnymi dowodami | Pełny spis ocen zakresu, nie pełna ekspertyza wszystkich znaczeń |
| Szczegółowe rodziny | 125 rekordów: 112 z potwierdzonym współczesnym zakresem, 1 ograniczony do konstrukcji, 12 wstrzymanych | 110 rodzin wnosi nowe napisy; 3 potwierdzone nie wymagają dodatków |
| Obecny wyjątek | Wszystkie 290 napisów zależnych od wyjątku oraz ich przyjęte analizy | Nie tylko poprzednia próbka 40 |
| Wyszukiwarka KWJP | 309 zapytań: 290 przyjęć i 19 uzupełnień; 730 ocenionych konkordancji | Pierwsze dwa różne dokumenty w pierwszych 10 wynikach; 16 trudnych przypadków rozszerzono do wszystkich 10 |
| SGJP | 501 wyszukań haseł, bez błędów końcowych; 207 pełnych tabel dla rodzin rozpatrywanych do propozycji | Bieżący czytnik służy badaniu odmiany, nie aktualizacji snapshotu |
| Wcześniejsze dowody | Ponownie wykorzystano 257 zapytań, 643 konkordancje i 107 fragmentów publicznego KWJP½M z rundy 2 | Zbiory mogą się pokrywać; nie sumujemy ich jako niezależnych obserwacji |
| Słowniki i źródła pierwotne | Wcześniejsze kontrole WSJP i nowsze teksty; uzupełnienia znaczeń, liczby gramatycznej i konfliktów rejestru | Zależność fleksji WSJP od SGJP oraz anotacji korpusowej pozostaje jawna |
| Pomiar | Dokładne odtworzenie bazowych POP/POP0, następnie pełny ranking i skład list w dwóch scenariuszach | Symulacja obecnej metody, bez zmiany jej parametrów |

Wszystkie pięć wymaganych kategorii zbadano: kod, dokumentację, konfiguracje/testy, przypięte dane i źródła pierwotne. Rozwinięcie i adresy: [rejestr źródeł](../planning/sources.md). Surowe teksty i pobrane odpowiedzi pozostają w ignorowanym cache. Publiczne pliki zawierają własne notatki, identyfikatory, bibliografię, metryki, hashe i analizowane formy.

## 2. Co dokładnie proponujemy

**2382 dodatkowe napisy** mają łącznie **7192 wskazane analizy**, które w bazie v29 odrzucono wyłącznie za dawność. Niezależny od skryptu propozycji odczyt SQL sprawdził każdą z tych analiz. Żadna pozostała odmowa nie jest omijana. [Lista i zakresy rodzin](../analysis/findings/round3/proposal.json), [dowód każdej analizy](../analysis/findings/round3/proposal-proof.json), [walidacja](../analysis/findings/round3/validation.json).

| Rodzina | Nowe napisy | Zakres uzasadnienia |
|---|---:|---|
| sołtyska | 10 | Kobieta pełniąca urząd; współczesne reportaże i prasa, rozdzielenie od dawnej żony sołtysa |
| niezbędnik | 10 | Narzędzie, wyposażenie i przenośny zbiór potrzebnych informacji |
| desperacja | 8 | Współczesna odmiana; bez `desperacyj` |
| ekscytacja | 6 | Uzupełnienie rozciętej odmiany, m.in. `ekscytacją` |
| sztaluga | 5 | Żywa liczba pojedyncza i regularna odmiana |
| szuwar | 4 | Roślinność nadwodna; liczba pojedyncza nie jest sama w sobie dawna |
| przechwałka | 5 | Przechwalanie się, bez przenoszenia dowodu z dawnego znaczenia pogróżki |
| pryncypium | 4 | Obie liczby, w tym rzadziej używana pojedyncza |
| aktuariusz | 11 | Współczesny zawód związany z ubezpieczeniami |
| edukować | 100 | Odpowiednia odmiana czasownika oraz już udokumentowane konstrukcje |
| moderować | 68 | Czasownik i właściwe imiesłowy; nie dawny samodzielny przymiotnik `moderowany` |
| wynegocjować | 48 | Czasownik, imiesłów i odsłownik w znaczeniu osiągnięcia ustaleń |

To przykłady, nie kryterium doboru paczki. Pełne [125 ocen rodzin](../analysis/findings/round3/family-decisions.json) obejmuje także rejestr książkowy i język fachowy. Współczesne użycie ma pochodzić z różnych tekstów; nie wymagamy osobnej frekwencji każdego rzadkiego przypadku gramatycznego.

Z poprzedniej paczki pochodzi **997 form**, a **1385** pojawia się dopiero po kontroli rodzin poza progiem lemma+POS≥30. Para lemma+POS dzieli m.in. formy osobowe, imiesłowy i odsłowniki. Nie opisuje całego leksemu. Dlatego przyjęcie samych 3364 kandydatów jednocześnie dodawałoby rzeczy nieuzasadnione i pomijało poprawnie umotywowaną odmianę.

W macierzy 404 grup jest **95 z konkretnym dodatkiem**, **3 z jawnym konfliktem/wstrzymaniem** oraz **306 bez dostatecznego ustalenia zakresu**. Te ostatnie nadal mają identyfikację źródła, wskazane dostępne konteksty i status każdego napisu. To rozpoznana kolejka dalszej oceny, nie 306 dowiedzionych archaizmów. [Pełna macierz](../analysis/findings/round3/candidate-matrix.json).

## 3. Jak ograniczono przenoszenie dowodu

Analiza łączy ręcznie wskazane znaczenie z konkretnym artykułem czytnika. Przechodzi po powiązaniach odmiany, np. do imiesłowu lub stopnia wyższego. Dodatkowa dawna etykieta formy lub osobno oznaczonego wariantu zatrzymuje przeniesienie. Nie przechodzimy do dowolnych wyrazów podobnych ani do innego aspektu czasownika.

Ostateczne napisy muszą już istnieć w przypiętych analizach przechodzących wszystkie kryteria poza dawnością. Nie tworzymy własnych form na podstawie podobieństwa. Negatywne imiesłowy/odsłowniki i stopień najwyższy są wiązane z odpowiednią formą dodatnią albo stopniem wyższym na podstawie istniejącego tagu. Konstrukcje generatora wymagają sprawdzenia zapisanych składników i już obowiązującej reguły. Uwaga składniowa `z D.` przy liczebniku `naście` nie jest częścią napisu do gry.

| Przypadek | Wynik oceny |
|---|---|
| desperacja → desperacyj; atencja → atencyj | Współczesne znaczenie nie znosi osobnej dawnej końcówki |
| dokumenta, klasztora, zasłonionemu, mielszy | Nie trafiają do propozycji; popularność formy podstawowej nie wystarcza |
| wywrzeć wpływ → wywre | Odrębny leksem i odmiana; brak przeniesienia |
| na umór → umorach; na odstawkę → odstawek | Zachowany zwrot nie daje pełnej swobodnej odmiany; dla odstawka proponowane jest tylko dodatkowe `odstawce` |
| moderowana / utytułowane | Współczesny imiesłów nie dowodzi samodzielnych dawnych rzeczowników/przymiotników o tym samym napisie |
| spękany | Wstrzymane mapowanie do badanego czasownika; czytnik nie łączy go z jego imiesłowem |
| zafrasować | WSJP również wskazuje przestarzałość; potrzebne rozstrzygnięcie granicy rejestru |

Konflikt `zafrasować` pokazuje ograniczenie samego wieku tekstu: współczesny autor może świadomie używać starego słowa. Nie rozstrzygnięto tu zbiorowo statusu takich przypadków. [WSJP: zafrasować](https://wsjp.pl/haslo/podglad/88943/zafrasowac).

Z drugiej strony adnotacja „zwykle” nie oznacza zakazu drugiej liczby. WSJP podaje oba paradygmaty dla [pryncypium](https://wsjp.pl/haslo/podglad/87307/pryncypium), [szuwar](https://wsjp.pl/haslo/podglad/72148/szuwar), [gawiedź](https://wsjp.pl/haslo/podglad/75561/gawiedz) i [jagnięcina](https://wsjp.pl/haslo/podglad/57581/jagniecina/5160693/mieso). To wspiera rzadką regularną odmianę. Dawny przedmiot również nie oznacza dawnej nazwy: [surdut — marynarka](https://wsjp.pl/haslo/podglad/71964/surdut/5193113/marynarka) ma opis bez kwalifikatora dawności i współczesną odmianę.

## 4. Kontrola wszystkich 290 obecnych przyjęć

| Ocena wybranych kontekstów | Napisy |
|---|---:|
| Autorskie użycie w dzisiejszej narracji | 181 |
| Nierozstrzygnięty zakres lub rejestr | 50 |
| Ograniczona konstrukcja | 34 |
| Wybrane konteksty nie wspierają przyjętej analizy | 12 |
| Tylko jeden dokument w sondzie | 3 |
| Mieszane dowody wymagające rozdziału analiz | 10 |
| Razem | **290** |

Kategorie opisują wynik kontroli dowodu, nie gotowe decyzje zachować/usunąć. [Każdy napis i jego przyjęte analizy](../analysis/findings/round3/current-review.json).

Dla **bad, dag, dyr, reż, sek, sie, sui, um, moko, wiosenno, świąteczno, tem** przeczytano po 10 kontekstów. Nie znaleziono w nich dowodu analiz, dzięki którym napisy weszły do STANDARD. To m.in. skróty, obcy język, literówki lub człony złożeń. Nie twierdzimy, że zbadano wszystkie trafienia ani dowiedziono nieistnienia tych słów.

Ważne różnice:
- `dag` występuje jako jednostka masy; baza przyjmuje dawną odmianę `daga`. `reż` występuje jako skrót reżysera, lecz przyjęta jest dawna nazwa żyta.
- `moko` występuje w opisie maoryskich tatuaży; to nie dowód wołacza od `moka`. Nowe znaczenie wymaga właściwego przypisania.
- `premium` jest żywe, lecz współczesny modyfikator jakości nie dowodzi dawnego rzeczownika ani `premiów`.
- `ludzko` ma zarówno fragmenty złożeń, jak i samodzielne współczesne użycia. Nie należy usuwać całego napisu przez część błędnych trafień.
- `łże` ma żywe użycie czasownikowe; nie jest to dowód dawnego rzeczownika `łeż`.

Nie ma podstaw do mechanicznego wyłączenia całego dotychczasowego wyjątku. Jednocześnie jego uzasadnienie wymaga kontroli nie tylko przy nowych słowach. [730 notatek i odsyłacze do konkretnych wierszy](../analysis/findings/round3/context-review.json).

## 5. Rzeczywisty wpływ na listy

Baza: **LL-PL v29**, STANDARD 3 090 194; lokalny numer buildu `v30` nie jest numerem wydania. Bazowe POP i POP0 odtworzono jako dokładnie te same zbiory co opublikowane w `pop-v2-20261011-194738-b`. Potem przeliczono jednostki, ranking, próg remisów, przycinanie członków grup i formy. [Odtworzenie bazy](../analysis/findings/round3/pop-baseline.json), [pełne delty](../analysis/findings/round3/pop-impact.json).

| Lista | Przed | Dodatki | Ubytki | Po | Zmiana netto |
|---|---:|---:|---:|---:|---:|
| STANDARD | 3 090 194 | 2382 | 0 | 3 092 576 | +2382 |
| POP | 1 227 250 | 2372 | 2430 | 1 227 192 | **−58** |
| POP0 | 388 509 | 481 | 0 | 388 990 | +481 |

Ubytki POP pozostają w STANDARD. Przykłady: `cowboy`, `barion`, `kifoza`, `wakuola`, `anyżowy` i formy ich odmiany. Dziesięć dodatków rodziny `pojazdowy` nie wchodzi do POP. Wszystkie nowe formy POP/POP0 w tym scenariuszu pochodzą z nowych dodatków STANDARD.

**Dlaczego POP maleje?** Obowiązuje limit 60 000 leksemów i zakaz dzielenia bloków o tej samej mierze. Zmiana populacji i grup homonimów przesuwa granicę. Przed zmianą wybrano 59 991 leksemów przed przycinaniem; następny blok miał 60. Po zmianie wybrano 59 909, a następny blok liczy 116 i nie mieści się w pozostałych 91 miejscach. Liczba wybranych jednostek spada z 45 137 do 45 059. To skutek obecnej metody, a nie dowód zmiany poprawności słów. Reguły: [ADR-007](../../../../../docs/adr/ADR-007-metoda-pop-v1.md), funkcje `threshold` i `prune_members` w `literaki_slownik/pop.py`.

W obu listach nadal przechodzą obowiązujące kontrole częstych form: 20 000 dla POP i 5000 dla POP0, bez braków. To istotna kontrola, ale nie dowód braku dotkliwych zmian poniżej tych zakresów.

### Wariant wrażliwości: cofnięcie 12 wątpliwie uzasadnionych przyjęć

Osobno policzono tę samą paczkę dodatków po usunięciu wymienionych 12 napisów. **To nie rekomendacja automatycznego usunięcia.** [Założenie](../analysis/findings/round3/sensitivity-proposal.json), [wynik](../analysis/findings/round3/sensitivity-pop-impact.json).

| Lista | Dodatki | Ubytki | Po | Netto wobec wydania |
|---|---:|---:|---:|---:|
| STANDARD | 2382 | 12 | 3 092 564 | +2370 |
| POP | 2372 | 2440 | 1 227 182 | −68 |
| POP0 | 481 | 15 | 388 975 | +466 |

POP0 traci 5 cofanych napisów oraz 10 form `dekagram`: `dekagram`, `dekagrama`, `dekagramach`, `dekagramami`, `dekagramem`, `dekagramie`, `dekagramom`, `dekagramowi`, `dekagramy`, `dekagramów`. To dodatkowy skutek zmiany rankingu i grup po cofnięciu `dag`; poprawność i obecność tych form w STANDARD nie zmieniają się. Pozostałe kontrole częstych form nadal przechodzą. Sam komunikat „minus 12” byłby więc mylący.

Izolowana [kontrola cofnięcia wyłącznie dag](../analysis/findings/round3/dag-control.json), bez dodatków i pozostałych cofnięć, potwierdza ten związek: POP traci tylko `dag`, a POP0 także wszystkie 10 wymienionych form `dekagram`.

## 6. Walidacja, pewność i ograniczenia

Weryfikacja obejmuje wszystkie 2382 dodatki i 7192 analizy w bazie otwartej tylko do odczytu, kompletność macierzy 404/3364 i kontroli 290, kontrolne formy dodatnie i ujemne oraz sumy delty POP. Pełny hash bazy po symulacji jest identyczny: `85b23ca5cfaae273ec869f84fab643a87685c455606d8b21df4aec918f3a338c`. [Wynik walidacji](../analysis/findings/round3/validation.json).

Przeszły też 3 istniejące testy POP dotyczące całych bloków remisów, przycinania słabego członka homonimów i zachowania masy grupy. HTML sprawdzono strukturalnie wraz z odsyłaczami; nie deklarujemy wizualnego podglądu w niedostępnej przeglądarce.

Pewność jest **wysoka dla pomiarów na przypiętych danych** i wykazanych pomyłek w przenoszeniu dowodu. Jest **średnia dla ręcznego rozstrzygnięcia znaczenia i rejestru całej propozycji**. Nie znamy odsetka błędów w całej populacji ani w pozostałych 2367 kandydatach. Nie było niezależnego drugiego anotatora. Celowo dobrane pierwsze konteksty nie są losową próbą, a różne identyfikatory dokumentów nie gwarantują niezależności redakcyjnej.

KWJP nadal opisuje teksty z lat 2011–2020. Nowsza data wydania w metryce nie dowodzi powstania tekstu po 2020. Punktowe źródła z lat 2024–2025 pochodzą z poprzedniej rundy; kontrola z 2026 nie czyni całego korpusu korpusem współczesnej mowy. SGJP, WSJP i automatyczna anotacja KWJP są częściowo zależne. Z tego powodu nie traktujemy ich jako trzech niezależnych głosów.

Odtwarzanie: `round3_sources.py`, `round3_kwjp.py`, `round3_annotate.py`, `round3_assess.py`, `round3_pop.py bootstrap/measure`, `round3_validate.py` w katalogu `analysis/`. Pliki decyzji rodzin są ręcznie przygotowanym wejściem badawczym. Pomiar wariantu używa `measure sensitivity-proposal.json sensitivity-pop-impact.json`. `bootstrap` wymaga dużych przypiętych danych; cache NKJP pozostaje lokalny. Adresy i hashe odpowiedzi są w manifestach [SGJP](../analysis/findings/round3/sgjp-manifest.json), [pełnych tabel](../analysis/findings/round3/full-tables-manifest.json) i [KWJP](../analysis/findings/round3/kwjp-manifest.json).

## 7. Co radzę po tej rundzie

**Kontynuacja:** użytkownik przyjął wyniki tej rundy jako podstawę decyzji i zlecił celowany audyt. [Runda 4](targeted-audit.md) potwierdza paczkę, rozlicza wszystkie ubytki POP i rozdziela wcześniejsze 12 przypadków na 8 do osobnej decyzji o cofnięciu oraz 4 wstrzymania. Poniżej zachowano pierwotną rekomendację rundy 3. Wdrożenie nadal niezatwierdzone.

Materiał wystarcza do konkretnej rozmowy o zmianie. **Rekomenduję przyjąć 2382 formy jako paczkę do przeglądu i omówienia**, bez automatycznego zatwierdzania jej do wydania. Ma jawne zakresy dowodu i ujawniony wpływ na wszystkie listy. Przed wdrożeniem trzeba uzgodnić, czy akceptujemy wynikające z obecnego rankingu ubytki POP; same dodatki STANDARD nie opisują całości skutku.

Cofanie istniejących przyjęć należy rozpatrzyć osobno: najpierw właściwa analiza i możliwość innego żywego znaczenia, potem wpływ na POP. Dwunastka stanowi konkretną listę problemów z dowodem, a nie gotową czarną listę. Pozostałe 2367 form kierujemy do dalszej, celowanej oceny; nie blokujemy całej poprawy do czasu wyczerpania wszystkich możliwych przypadków.

Nie rekomenduję następnej losowej próby ani strojenia progu do uzyskania pożądanej liczby. Dalsze zbieranie ma sens dla wskazanej granicy: dawne użycie autorskie, zwrot utrwalony, samodzielny przymiotnik wobec imiesłowu lub konkretne mapowanie znaczeń. Bramką tej rundy jest przyjęcie wyników jako podstawy rozmowy albo wskazanie takiej grupy do pogłębienia. Zgoda na research nie jest zgodą na implementację.
