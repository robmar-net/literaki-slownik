# Miejsce zmiany dawności w pipeline — materiał do omówienia

## TL;DR
Zmiana należy do etapu `decisions`: oceny wieku konkretnej analizy przed agregacją do listy STANDARD.
Trwałym wejściem powinien być wersjonowany rejestr własnych ocen, przypięty do źródeł i dokładnych analiz.
SQLite oraz listy są odtwarzanym wynikiem; POP/POP0 przelicza się potem z nowego STANDARD i nowej bazy.
Obecny research to symulacja; produkcyjnego rejestru i obsługi nowego warunku jeszcze nie ma.

## Key Decisions
- Użytkownik pyta o miejsce zmiany, trwałość, powtarzalność, dokumentację i wpływ. To wyjaśnienie propozycji, bez zatwierdzenia wdrożenia.
- Zalecenie: nowy dowód rozstrzyga wyłącznie warunek wieku we wskazanej analizie; inne kryteria pozostają oceniane razem z nią.
- Zalecenie dla pierwszego zakresu: 2382 dodatki; osiem cofnięć i cztery wstrzymania to osobne decyzje.

## Open Questions / Risks
- Mapowanie 7192 sprawdzonych pozycji analiz z researchu na dokładne rekordy i konstrukcje produkcyjne wymaga implementacji oraz kontroli kompletności.
- Nowy snapshot SGJP może zmienić identyfikatory i zakres odmiany. Stara decyzja nie powinna automatycznie przejść na inny rekord.
- Dotychczasowy wyjątek oparty na liczniku KWJP pozostaje, jeśli zatwierdzimy tylko dodatki. Taka paczka nie usuwa całego ryzyka transferu dowodu między homonimami.
- Akceptacja rotacji POP i sposób wdrożenia nadal są otwarte.

## Zakres i metoda

Odczyt istniejącego kodu, konfiguracji, schematu, testów i wyników rund 3–4. Bez zmiany plików aplikacyjnych, bazy, list ani wiki. Analizę i syntezę wykonano w jednym kontekście: to wąska kontrola integracji, bez delegacji. Poniżej rozdzielono fakty i zalecenia.

## Obecny przebieg — ustalenia z kodu

1. `inspect_sources()` sprawdza źródła oraz hashe konfiguracji: [inputs.py](../../../../../literaki_slownik/inputs.py), linie 43–103.
2. `build()` importuje SGJP/KWJP i tworzy kandydatów konstrukcji. Następnie uruchamia etap `decisions`: [build.py](../../../../../literaki_slownik/build.py), linie 90–157.
3. `materialize_assessments()` rozwija analizy źródłowe, przetwarza istniejące konstrukcje i wywołuje wspólną ocenę: [decisions.py](../../../../../literaki_slownik/decisions.py), linie 255–365.
4. `assess_diagnostic()` składa warunki językowe, gry, profilu i zakresu. W STANDARD wywołuje `contemporary_use_override()`: ten obecnie znosi odmowę za dawność przy co najmniej 30 użyciach zapisu w nieliterackim KWJP. Nie sprawdza tożsamości znaczenia: [decisions.py](../../../../../literaki_slownik/decisions.py), linie 38–63; [policy.py](../../../../../literaki_slownik/policy.py), linie 90–91, 1059–1114.
5. `save()` zapisuje analizy i decyzje; powody są kanonicznym JSON-em identyfikowanym przez SHA-256. `write_lists()` wybiera zapisy z przynajmniej jedną w całości przyjętą analizą: [decisions.py](../../../../../literaki_slownik/decisions.py), linie 291–313; [build.py](../../../../../literaki_slownik/build.py), linie 74–86.
6. Weryfikacja i eksport poprzedzają osobne budowanie pakietu POP. `_build_pop()` korzysta z przypiętej bazy i STANDARD, liczy grupy, miary, próg i przycinanie: [pop.py](../../../../../literaki_slownik/pop.py), linie 1558–1598. Nie tworzy oceny współczesności STANDARD.

## Zalecane miejsce i zakres zmiany

Nowy dowód wieku należy do wspólnej ścieżki `assess_diagnostic()` / `contemporary_use_override()`, wywoływanej przez etap `decisions`. Loader i walidator rejestru byłyby podłączone w `build()` i `materialize_assessments()`. `explain` musi korzystać z tych samych danych i znaczenia reguły.

Źródłowy kwalifikator `daw.` lub `przest.` zostaje zapisany. Nowa reguła zapisuje, dlaczego udokumentowane współczesne znaczenie i wskazana odmiana pozwalają spełnić warunek wieku w tej analizie. Pozostałe odmowy — pisownia, wielka litera, skrót, profil gry, dawna końcówka poza zakresem dowodu — zachowują działanie.

Zalecany zakres jest jawny: dopuszczenie wskazanych analiz źródłowych oraz wskazanych, już istniejących analiz konstrukcyjnych. Dowód leksemu nie daje automatycznej akceptacji wszystkich homonimów, wariantów i przyszłych konstrukcji. Tworzenie kandydatów konstrukcji pozostaje wcześniejszym etapem; zmienia się ich kwalifikacja, jeśli objęto je dowodem.

## Trwałość: wejście w repozytorium i wynik w bazie

Proponowany nowy plik `config/generator/standard-age-evidence.json` (jeszcze nie istnieje) powinien zawierać własne, zatwierdzone oceny. Nazwa i schemat są propozycją do specyfikacji.

Każda ocena powinna mieć:

- stały identyfikator, opis współczesnego znaczenia, zakres odmiany i jawne wyłączenia;
- źródła dowodu: identyfikatory, lokalizatory, daty dostępu, hashe własnych notatek/artefaktów oraz odsyłacz do zatwierdzonej decyzji;
- dokładne cele: hash snapshotu, `source_id`, rekord źródłowy, leksem, zapis, tag oraz właściwe rozwinięcia; dla konstrukcji także `candidate_key`, regułę i składniki;
- wersję schematu oraz reguły interpretującej dowód.

Sam `analysis_key` jest użytecznym identyfikatorem kontrolnym, ale nie zastępuje przypięcia snapshotu, znaczenia i pełnej tożsamości źródłowej. Trzeba rozliczyć wszystkie wpisy: brak celu, rozbieżny tag/hash, konflikt albo niejednoznaczne mapowanie powinny zatrzymywać nowy build, zamiast cicho pomijać ocenę.

Manifest `sources.json` przypina rejestr i potrzebne artefakty dowodowe hashem. Build korzysta z tych plików lokalnie. Dostęp do aktualnej strony słownika, wyszukiwarki, agenta albo cache `tmp/` nie jest zależnością produkcyjnego odtwarzania. Publikowany rejestr zawiera własne oceny i odsyłacze; surowe korpusy nie są do niego kopiowane.

W bazie powinien pozostać pełny zastosowany rejestr lub jego odtwarzalna projekcja wraz z hashem oraz ślad przy każdej ocenie. Istniejące `source_artifact`, `analysis`, `decision_payload` i `variant_decision` dają wzorzec; dokładną reprezentację trzeba potwierdzić w specyfikacji. Baza jest wynikiem, który można odbudować od zera z wejść.

Nie wystarczy dopisać pliku do `configurations`: obecne `inspect_sources()` sprawdzi jego hash, ale nowa reguła i walidacja mapowania muszą rzeczywiście go odczytać oraz użyć.

## Wzorce do wykorzystania i ich granice

`semantic-uses.json` oraz `checked_use_reviews()` już przypinają własne przeglądy do pełnego rekordu i hashów źródła, zachowują ślad, wykrywają zmieniony przegląd oraz sprawdzają spójność odczytu. To dobry wzorzec walidacji i trwałości.

Obecny format obsługuje jednak zamknięty zakres dowodów użyć, nazw i warunku leksykalnego. Nie zawiera ogólnego dowodu współczesności z zakresem fleksji. Nie można potraktować tego jako działającej obsługi nowych 110 rodzin bez zmiany schematu i kodu. Osobny rejestr wieku unika przypisania nowej treści do innego istniejącego warunku.

`materialize_assessments()` już odmawia nadpisania ocen przy zmianie wersji polityki, przeglądu lub treści powodów. Nowy zakres powinien zachować ten kontrakt: nowa wersja polityki, nowy katalog przebiegu, stary build i wydanie zachowane.

`explain.py` ma zarówno ponowną ocenę bieżącym kodem, jak i odczyt utrwalonych analiz. Dla nowej reguły trzeba zapewnić ich zgodność; dla historycznego przebiegu wynik zapisany z dawną polityką nie może zostać zastąpiony dzisiejszym rejestrem.

## Powtarzalność i wymagane sprawdzenia

Istniejące `create_run()` zapisuje manifest wejść, commit i hash kodu. `verify._check_reproduction()` porównuje niezależny drugi build: ten sam kod, ten sam manifest i tę samą treść kanoniczną. To właściwy mechanizm dla nowego zakresu.

Odtwarzalność oznacza identyczne listy i kanoniczną treść ocen dla tych samych wejść. Daty uruchomienia i techniczny układ pliku SQLite nie muszą być identyczne bajtowo.

Przed uznaniem wdrożenia za gotowe trzeba sprawdzić:

- pełne mapowanie zatwierdzonego rejestru; brak dowodów przeniesionych na homonim lub dawną końcówkę;
- pozytywne i negatywne przypadki, m.in. `desperacja` / `desperacyj`, odrębne analizy `dag`, dowody konstrukcji oraz zachowanie innych odmów;
- zgodność build ↔ `explain`, zachowanie historycznych przebiegów, odmowę przy zmienionych hashach i niepasujących celach;
- dwa świeże buildy i zgodność ich kanonicznych wyników;
- dokładny zbiór dodatków/ubytków wobec symulacji oraz kontrolę BROAD, POP/POP0 i częstych form.

Powiązane istniejące testy: `test_round4_sjp_fixes.py`, `test_round5_zds.py`, `test_decisions.py`, `test_semantic_uses.py`, `test_verify.py`, `test_pop.py`. W tym odczycie nie uruchamiano testów: nie zmieniono implementacji.

## Dokumentacja i utrzymanie

1. Nowy ADR opisujący zasadę dowodu współczesności, zakres fleksji, pierwszeństwo ocen, pozostawienie lub późniejszą zmianę wyjątku KWJP oraz zachowanie po zmianie źródła.
2. Dokumentacja generatora: opis rejestru, tworzenia i kontroli wpisu, budowania oraz diagnostyki `explain`; aktualizacja opisu filtra dawności.
3. Raport zmiany: dokładne analizy i formy, delta wszystkich list, wersje kodu/polityki/źródeł, wyniki powtarzalności, manifest wydania.
4. Przy wdrożeniu zmieniającym kryteria/listy: wiki STANDARD, POP/POP0, liczby i historia zgodnie z [runbookiem](../../../../../docs/runbook-wiki.md). W samym researchu wiki pozostaje bez zmian.

Przyszłe nowe przypadki wymagają nowej własnej oceny i zatwierdzenia. Aktualizacja SGJP wymaga porównania i ponownego przypięcia; kod nie powinien uznawać starej kwalifikacji za dowód dla dowolnego przyszłego rekordu o tym samym napisie. Cofnięcie decyzji jest nową wersją rejestru i nowym buildem, z zachowaniem historii.

## Wpływ i granice obecnych liczb

| Obszar | Oczekiwany wpływ zakresu samych dodatków |
|---|---|
| Źródłowy SGJP i korpusy | Te same przypięte dane; dochodzi własny rejestr dowodów |
| BROAD | Skład bez zmiany; wymaga kontroli pełnego przebiegu |
| STANDARD | +2382, −0 na badanej bazie |
| POP | +2372, −2430; metoda pozostaje ta sama |
| POP0 | +481, −0 |
| Diagnostyka i manifesty | Nowy powód, identyfikatory dowodów, wersja polityki i hashe |
| Osiem cofnięć / cztery wstrzymania | Poza pierwszym zakresem dodatków |

[Symulacja](round3_pop.py) tworzy w pamięci `standard ∪ additions − removals` i ponownie liczy POP z istniejącej bazy. [Kontrola analiz](round3_validate.py) potwierdza odrzucenie wskazanych analiz wyłącznie za wiek. Nie jest to pełny build nowej polityki. Dokładny zbiór 2382 form oraz policzone delty są oczekiwanym wynikiem odbioru dla przypiętej bazy, który trzeba potwierdzić produkcyjnym przebiegiem.

Nie zbadano w tym odczycie sposobu pobierania nowych wydań przez aplikację. Zmiana generatora, publikacja pakietu i użycie pakietu w aplikacji pozostają rozdzielnymi działaniami.

## Wynik analizy

- `status`: completed_read_only
- `summary`: miejsce integracji ustalone; istnieją wzorce trwałych ocen i powtarzalności, obsługa nowego dowodu wieku pozostaje propozycją
- `files_found`: build.py, decisions.py, policy.py, inputs.py, schema.sql, run.py, explain.py, verify.py, export.py, pop.py, sources.json, semantic-uses.json, testy i artefakty researchu
- `complexity`: umiarkowana integracja; duże wymagania wobec mapowania danych i pełnego odbioru
- `risk_level`: podwyższony wpływ na skład słowników; bez zmian produkcyjnych w tej analizie
