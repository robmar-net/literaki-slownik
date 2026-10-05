# CLI generatora — bieżący stan

## TL;DR
Działają inspect-sources, build importu i diagnostyczne explain. Pełny generator nadal jest w implementacji.
Explain czyta bazę bez zmian i pokazuje wszystkie źródłowe interpretacje.
Nieaktywna polityka językowa daje unresolved; diagnostyka nie nadaje końcowego członkostwa w liście.

## Key Decisions
- Python 3.11+ i biblioteka standardowa; uruchomienie z katalogu repo.
- Źródła podajemy lokalnie przez jawny manifest. CLI niczego nie pobiera.
- Oryginał, język, reguły gry, profil i końcowa lista są rozdzielone. Korpus nie dopuszcza słowa do gry.

## Open Questions / Risks
- Konstrukcje i pełna polityka wymagają domknięcia G3/G4. Verify/export oraz pełny odbiór nie są jeszcze gotowe.
- Bieżące explain ocenia źródłowe interpretacje oraz odtwarza kandydatów dwóch potwierdzonych klas. Brak w imporcie SGJP nie jest oceną wszystkich możliwych konstrukcji.
- Brak powiązań w starszej bazie nie oznacza braku korpusowego ani F=0.

## Komendy dostępne

```sh
python3 -m literaki_slownik --help
python3 -m literaki_slownik inspect-sources --manifest config/generator/sources.json --json
python3 -m literaki_slownik build --manifest config/generator/sources.json --run-dir data/work/import-new --json
python3 -m literaki_slownik explain --run-dir data/work/import-new --word PCV
python3 -m literaki_slownik explain --run-dir data/work/import-new --word DNA --variant broad --json
```

Build odmawia istniejącego katalogu. Aktualnie wykonuje preflight i importy; pozostawia INCOMPLETE oraz jawnie pending dla dalszych etapów. Użyj nowego katalogu przy ponowieniu. Nie modyfikuj historycznego audytu.

Explain nie skraca odpowiedzi JSON: pokazuje wszystkie oryginały, pełne ID homonimów, surowe tagi i ich rozwinięcia, nazwy/kwalifikatory, źródła i pierwszy wiersz interpretacji. Duplikaty pozostają w raw tabeli; pierwszy wiersz nie jest listą wszystkich powtórzeń. Tekst zawiera powody ocen na osobnych poziomach. NFC/lower służy wyszukiwaniu; PCV nie staje się dopuszczalne przez zapytanie pcv.

## Jak czytać wynik

- source_presence=present: znaleziono wpis w bazie, także przy growym odrzuceniu.
- source_presence=absent: brak w kompletnym imporcie SGJP; pełne konstrukcje pozostają nieocenione.
- not_observed_in_incomplete_import: brak w odczytanej części; awaria/running/pending importu nie dowodzi braku w źródle.
- assessment.language: polityka językowa jeszcze nieaktywna, unresolved.
- assessment.game: potwierdzony zakaz wielkich liter oceniany osobno; inne warunki pozostają unresolved.
- assessment.profile: kanoniczny PL v1, 32 litery i 2–15 znaków; źródłowy zapis pozostaje zachowany, nie usuwamy znaków.
- source_aggregation: wynik tylko znalezionych źródłowych analiz; nie przenosi warunków między homonimami.
- list_membership: w obecnej diagnostyce zawsze unresolved. Nie jest listą wydania ani obietnicą końcowej kwalifikacji.

Jeżeli baza ma relacje evidence_link/evidence_candidate, explain pokazuje powiązane obserwacje i wszystkich kandydatów. F i inne miary pozostają przy jednostce/opublikowanej liście, raz na rekord. Powiązanie lemma czytać nie dowodzi częstości pełnej formy czytałem. sense_identity_confirmed pozostaje false. W starszej bazie bez relacji links_available=false; nie uruchamiamy budowania powiązań podczas odczytu.

## Kody i kontrola

JSON: jeden obiekt UTF-8 na stdout, błędy na stderr. Kod 0 oznacza poprawną diagnostykę także dla reject/unresolved/absent. Kod 2: błędne argumenty/schemat, 3: niedopuszczone wejście/hash, 4: błąd operacyjny/odczytu, 130: przerwanie. Kody wydania 5 zostają w kontrakcie przyszłego verify/export; nie dodano obejścia wydania.

```sh
python3 -m unittest discover -s tests -p 'test_*.py'
python3 -m unittest discover -s scripts -p 'test_audit_sgjp.py'
```

[Rzeczywista próba explain](../../.maister/tasks/development/2026-10-04-generator-broad-standard/analysis/evidence/diagnostic-explain-runtime.json) obejmuje osiem zapytań do pełnej bazy z technicznymi powiązaniami KWJP. Hashe bazy i manifestu przed/po odczycie są identyczne. To sprawdzenie mechaniki, bez odbioru G8/K7.

## Potwierdzone warunki w diagnostyce

Explain w wersji `diagnostic-approved-conditions-v2` pokazuje zatwierdzone A dla `niezal.`: samo niezalecanie nie odrzuca w obu wariantach. Obok tej pozytywnej oceny pojedynczego warunku nadal pokazuje nierozstrzygnięcie pełnej polityki. Nie jest to werdykt dopuszczalności całego słowa. Odczyt istniejącego importu pokazuje warunki bieżącej wersji kodu, nie ukończony historyczny build decyzji.

Explain w wersji `diagnostic-approved-conditions-v3` pokazuje również zatwierdzone warunki wieku: dodatkowa dawność/archaiczność może dać językowe reject w STANDARD mimo niewiadomych innych warunków. BROAD pozostawia samą dawność niewykluczającą. List_membership pozostaje unresolved, ponieważ nie zbudowano wszystkich konstrukcji i pełnych decyzji.

Wersja `diagnostic-approved-conditions-v4` dodaje jawny niewykluczający warunek zakresu użycia dla 15 sprawdzonych etykiet potoczności/regionalności/gwarowości/wulgarności/rzadkości. Nieznane mieszanki pozostają do oceny; całe członkostwo nadal unresolved. W kolejnej wersji v5 niepopr. wdrożono zgodnie z zatwierdzonym A.

Wersja `diagnostic-approved-conditions-v5` pokazuje reject językowy dla 27 etykiet jawnej niepoprawności w obu wariantach. Source_presence pozostaje present, a pozostałe analizy zachowane. List_membership nadal unresolved ze względu na brak pełnych konstrukcji i decyzji.

## Diagnostyczni kandydaci konstrukcji

Wersja `diagnostic-approved-conditions-v6` dodaje 357 etykiet opisowych. `derivations` pokazuje także znane klasy rozkaźnik + jedna partykuła i by + nwok aglt, z pełnymi składnikami oraz przyczynami ocen. Odczyt nie zapisuje kandydatów do bazy, nie nadaje pełnego dopuszczenia i nie uruchamia kompletnego build. JSON nie ucina wyników. Tekst pokazuje wiersze źródeł i odziedziczone ograniczenia; source_presence nadal oznacza obecność bezpośredniego wpisu. Powiązań KWJP kandydatów nie zbudowano, nie przypisujemy im F z segmentów.
