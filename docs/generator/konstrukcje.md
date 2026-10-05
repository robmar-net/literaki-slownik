# Kontrola fleksji i konstrukcji

## TL;DR
Nadgeneracja historycznej próby została wyjaśniona, nie dopisujemy 120 form.
Siedem niespójnych tagów winien nie oznacza brakujących napisów.
Macierz rozdziela poprawność językową, dopuszczalność gry i kompletność dowodów.

## Key Decisions
- Pełne rekordy źródłowe są preferowane; surowych tagów nie poprawiamy w importerze.
- Przy konstrukcji zachowujemy wszystkie składniki i ich kwalifikację. Odrzucenie jednej analizy nie usuwa homonimów.
- Nie uruchamiamy trybu permissive ani produktywnego tworzenia nowych leksemów.

## Open Questions / Risks
- Zatwierdzone A: dosłowna enumeracja18kontrakcji w SGJP wystarcza jako dowód językowy;8pozostałych wymaga dalszego dowodu. Sama reguła składania ich nie potwierdza.
- Warunki konstrukcji odnosimy do udokumentowanych zasad gry, bez automatycznego przejmowania redakcyjnej polityki źródeł SJP.pl. Zob. [sprostowanie](../../.maister/tasks/development/2026-10-04-generator-broad-standard/analysis/evidence/source-policy-clarification.md). Nie aktualizujemy reguł gry przez odczyt bieżącej witryny.
- Lista hostów mobilnych zakończeń wymaga dowodu morfemu, nie tylko końcowych liter.

## Fleksja
[Teoria SGJP](https://sgjp.pl/static/pdf/Podstawy_teoretyczne_SGJP.pdf), §6.6.2, opisuje ograniczone paradygmaty czasowników niewłaściwych. Pełny odczyt 30 leksemów wykazał po pięć analiz, bez osobowych form 1./2. osoby. Mechaniczna próba dopisała po cztery nieuprawnione trójki: razem 120. Dane i pełne paradygmaty są w `analysis/evidence/closure-*.json` aktywnego zadania; koordynator porównał wszystkie 150 rekordów z bazą.

W siedmiu leksemach winien źródłowe formy z zakończeniem `-śmy` mają tag `sec`. Tabele SGJP §6.6.1 i §6.4.1 potwierdzają osobę pierwszą. Kontrola daje 105 oczekiwanych i 105 źródłowych osobowych trójek, z siedmioma różnicami tagów po obu stronach. Wpływ na obecność napisów: zero. Explain pokazuje surowy tag i osobną jawną erratę, przypiętą do SHA256 źródła; nie ukrywa poprawki w imporcie.

## Macierz konstrukcji
Warunki techniczne opierają się na przypiętym `segmenty.dat` Morfeusza 20260823; rejestr dowodów zawiera hash.

| Klasa | Kontrola źródłowa | Status |
|---|---|---|
| operator by + aglt | właściwy składnik, osoba/liczba, nwok | potwierdzona klasa, cztery kombinacje |
| rozkaźnik + partykuła | osobowy impt, zakończenie i wokaliczność | 92 622 interpretacje; zero wyjątków zakończeń |
| przyimek + ń | dozwolony wariant, przecięcie gen/acc | 27 analiz / 26 napisów; growe poświadczenia niekompletne |
| podwojona partykuła | oddzielna analiza konstrukcji | językowo możliwa; growo wykluczona |
| mobilne zakończenie | konkretna klasa hosta i morfem | macierz hostów nieukończona; brak automatycznej reguły endswith |
| inne produktywne ścieżki | tworzenie nowych leksemów / permissive | poza zatwierdzonym zakresem |

Przypadki rozdzielające pochodzą z danych SGJP: `jam` ma niezależną analizę od jama i frag; `żeż` jest także rozkaźnikiem od żec; `doń` także formą od donia. Nie odrzucamy całego napisu przez niedopuszczalną analizę konstrukcyjną. Przesiew hostów zwrócił `niby`, choć nie dowodzi on dołączalnego morfemu. Nie generujemy mechanicznie `nibym`.

## Zaimplementowane konstruktory

`literaki_slownik.constructions` tworzy kandydatów dla rozkaźnika z jedną partykułą i źródłowego `by` (comp/part) z czterema końcówkami aglt nwok. Każdy wynik zachowuje pełne składniki, ID homonimów i źródłowe kwalifikatory. Pierwotny podzbiór obejmował tylko jedną partykułę; poniżej opisano nową odrębną klasę podwojenia. Nie zgadujemy hosta po końcowych literach. Nieznana klasa lub niezgodne zakończenie daje błąd pokrycia. Kandydaci są utrwalani przez build; pełna kwalifikacja do list nadal wymaga domknięcia.

Pełny runtime: 92 622 źródłowe rekordy impt → 93 438 rozwiniętych analiz, 91 104 różne napisy; 4 100 napisów odpada już w profilu alfabetu/długości. To nie końcowa delta listy. Dwa źródłowe by × cztery aglt dają osiem analiz czterech napisów. [Raport](../../.maister/tasks/development/2026-10-04-generator-broad-standard/analysis/evidence/approved-rules-runtime.json).

## Źródła społecznościowe — bieżąca faza

Wikisłownik i podobne źródła społecznościowe odkładamy na później. W bieżącej fazie nie używamy ich do budowy słownika ani rozstrzygania dopuszczalności. Zachowujemy przypięte dane SGJP i KWJP oraz ich odrębne role; KWJP nie jest dowodem poprawności konstrukcji. Brakujące poświadczenia pozostają unresolved — nie oznaczają odrzucenia formy i nie pozwalają deklarować pełnego wydania. Dotychczasowe audyty pozostają materiałem historycznym, bez aktywacji ich danych.

## Konstrukcje w explain

Explain odtwarza tylko potwierdzone klasy na podstawie pełnych interpretacji w istniejącym imporcie. Sufiks zapytania służy odnalezieniu możliwego źródłowego rozkaźnika; konstruktor musi potwierdzić klasę, zakończenie i dokładny wynik. By + aglt wymaga dokładnego by oraz właściwej nwok końcówki. Nie tworzy nibym; czytajżeż wymaga odrębnej, zamkniętej klasy źródłowego podwojenia opisanej poniżej.

Pole derivations zawiera regułę, rozwinięty tag, pełne składniki i etykiety oraz diagnostyczną ocenę obu wariantów. Source_presence i source_aggregation nadal dotyczą tylko bezpośredniego importu SGJP; brak bezpośredniego wpisu nie zaprzecza istnieniu kandydata. Kandydat pozostaje candidate_not_qualified, list_membership unresolved. Pełna macierz i końcowe decyzje pozostają otwarte; zapis dwóch klas w build dodano w kolejnym kroku.

Warunek kontekstu A nie obejmuje `pisane_łącznie_z_przyimkiem`: źródłowe ń pozostaje niesamodzielnym składnikiem. Nie zezwala na automatyczne tworzenie niepoświadczonych kontrakcji.

## Zapis potwierdzonych kandydatów w bazie

Nowe build utrwalają impt + jedną partykułę oraz źródłowe by + nwok aglt. Tabela `derivation_candidate` przechowuje oryginał, klucz wyszukiwania, pełny lemat, rozwinięty tag, etykiety i kanoniczny JSON śladu. `candidate_key` jest SHA256 tego JSON; nie zależy od technicznego ID wiersza SQLite. Inne analizy, tagi lub składniki zachowują odrębne ślady nawet wtedy, gdy wynikowy napis jest taki sam.

Tabela `derivation_component` wiąże każdy składnik źródłowy kluczem obcym z surowym rekordem SGJP. Partykuła gramatyczna ma jawny kind i nie udaje wpisu słownikowego. Kandydat i jego składniki zapisują się w jednej porcji; po błędzie mogą pozostać wcześniejsze porcje, lecz etap jest failed, a gotowość INCOMPLETE. Ponowne wyliczenie tego samego zestawu nie dubluje śladów. Nie dubluje też ani nie usuwa bezpośrednich wpisów w interpretation.

Kandydaci mają wyłącznie `candidate_not_qualified`. W `reports/construction-candidates.json` znajduje się rozliczenie potwierdzonego podzbioru. Pełny etap constructions pozostaje pending, ponieważ inne klasy i kwalifikacja nadal wymagają wykonania.

Explain nadal odtwarza potwierdzone konstrukcje z rzeczywistych składników, a `persisted_candidate_key` wskazuje odpowiadający im zapis, jeśli istnieje. Dla starych baz bez tych tabel pole jest null; odczyt nie wymaga migracji ani modyfikacji wcześniejszego przebiegu. To odnośnik do śladu, nie finalna ocena dopuszczalności.

## Zatwierdzony dowód kontrakcji i zamknięta grupa hostów by

Wdrożono zatwierdzone A: 57 rozwiniętych analiz 18 dosłownie wskazanych form SGJP ma dowód językowy; 24 analizy ośmiu pozostałych form pozostają nierozstrzygnięte. Build i explain zapisują pełne składniki i zachowują homonimy. Zamknięta grupa 16 hostów z_aglt_by daje 64 kandydatów zgodnych z klasą źródłową. KWJP orth/orth_lc wiąże całe konstrukcje przez candidate_key, bez dziedziczenia częstości rdzenia. Explain czyta starsze bazy. Siedem errat winien jest adnotacją zależną od hasha źródła. Pełna polityka, pozostałe klasy i wydanie nadal wymagają ukończenia.

[Przegląd i rzeczywiste liczebności](../../.maister/tasks/development/2026-10-04-generator-broad-standard/analysis/evidence/constructions-links-review.md). Pełny zakres pozostałych mobilnych hostów i dowodów pozostaje obowiązkowy.

## Pozostałe zamknięte klasy mobilnych końcówek

Wdrożono A dla normy 2026: dokładne analizy comp jeśliby/jeżeliby i ich składniki konstrukcyjne mają odrzucenie STANDARD; BROAD nie wyklucza przez samą dawną pisownię. Nie usunięto wpisów i nie zmieniono reguł gry. Dodano kandydatów mobilnych końcówek dla trzech pozostałych zamkniętych klas, z kontrolą lematu, POS, wokaliczności, źródła i śladów. Odmienne formy niezgodne z wariantem źródłowej klasy wymagają dalszej oceny; pełna macierz i kwalifikacja nadal otwarte. Źródło: [Teoria SGJP](https://sgjp.pl/static/pdf/Podstawy_teoretyczne_SGJP.pdf), §6.4.1.

## Rozbieżności przy odmiennych hostach

Rzeczywista kontrola nowych mobilnych klas: 312 kandydatów i 624 składniki, identyczny digest przy powtórzeniu, FK/integrity OK. Osiem różnic wariantu klasy i odmienionej formy rozstrzygnięto przez SGJP §6.4.1; adnotacja zachowuje oba warianty. Generator 122/122, audyt 5/5. Wymagana decyzja o zakresie ośmiu niepoświadczonych kontrakcji pozostaje pending; brak wyłączenia przed odpowiedzią.

## Zatwierdzony zakres pierwszego wydania

A zatwierdzone i wdrożone: zakres kontrakcji pierwszego wydania obejmuje 18 poświadczonych form (57 analiz), osiem innych (24 analizy) pozostaje diagnostycznie poza zakresem. Ocena językowa niewiadoma nie została zmieniona na błędność. Nowa warstwa release_scope jest oddzielna od języka, gry i profilu; członkostwo jest oceniane dla pojedynczej analizy, więc homonimy nie są tracone. Nie zmieniono kluczy ani treści utrwalonych kandydatów. Dodano zamknięte źródłowe sekwencje host+partykułowe by+(opcjonalna końcówka nwok), z pełnymi 2/3 składnikami i odrębną oceną pisowni normy2026.

## Adnotacja akcent i klasy źródłowe gry — bieżący przyrost

Zatwierdzone A dla adnotacji akcent wdrożono bez zmiany dawności: BROAD nie wyklucza przez brak objaśnienia, STANDARD odrzuca dwie analizy daw.,rzad.,akcent. Pełny raport 7 458 520 analiz zachowuje 26 nieobjaśnionych oznaczeń w 1910 analizach. Dodano diagnostyczne warunki klas źródłowych gry: nazwy, brev, niesamodzielne segmenty oraz odrębną ocenę całości konstrukcji. Nowa zamknięta klasa ja/ty/my/wy/wszyscy zachowuje sześć kandydatów i growe odrzucenie tych analiz, bez usuwania homonimów. Pozostałe mobilne hosty i sekwencje by oceniono zgodnie z zachowanymi wyłączeniami gry; byle ma udokumentowany wyjątek. Pełna kwalifikacja i wydanie nadal nieukończone.

[Przegląd i dowody](../../.maister/tasks/development/2026-10-04-generator-broad-standard/analysis/evidence/accent-and-source-game-review.md).

## Podwojona partykuła — pełna klasa źródłowa sg

Build i explain obsługują impt-double-particle-v1: tylko źródłowy impt:sg:sec:perf/imperf, zgodna spółgłoska, +że+ż. To formalna reguła segmenty.dat334–340, z trzema uporządkowanymi składnikami. Nazwy/kwalifikatory/ID zachowane.31 146 kandydatów z pełnych źródłowych rozkaźników, każdy z odrębnym game-double-particle-v1=reject. Nie generujemy dalszych podwojeń ani plural+żeż. Jedno źródło perf.imperf daje osobne ślady. Dotyczy analizy konstrukcji, nie wszystkich słów kończących się na żeż ani niezależnych homonimów. [Dowody i runtime](../../.maister/tasks/development/2026-10-04-generator-broad-standard/analysis/evidence/capital-double-review.md). Pełna polityka pozostałych klas nadal nieukończona.
