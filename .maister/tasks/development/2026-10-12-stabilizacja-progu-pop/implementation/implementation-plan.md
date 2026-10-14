# Plan implementacji: 2382 formy STANDARD i stabilizacja POP

## TL;DR

Najpierw przypinamy dokładne decyzje z badania do wersjonowanego JSON-a i włączamy je w zapis ocen STANDARD.
Następnie zmieniamy selekcję POP oraz przycinanie członków; POP0 pozostaje przy dotychczasowym limicie.
Pełne nowe buildy, porównanie wszystkich form, przegląd próbek i wiki zamykają pracę nad kodem i kryterium.
Docelowa granica POP, osiem cofnięć, wydanie GitHub Release i gra pozostają poza zakresem.

## Key Decisions

- Zadanie wykonujemy sekwencyjnie: grupy dzielą `explain.py`, manifesty i raporty; równoległe zapisy groziłyby niespójnym wynikiem.
- Produkcyjny JSON powstanie z badawczych `proposal-proof.json` i `family-decisions.json` po jednoznacznym powiązaniu z przypiętą bazą. Później jest zwykłym, edytowalnym wejściem pipeline.
- Każda grupa zaczyna się od testu/kontraktu, potem implementacji i lokalnego sprawdzenia. Pełny build czeka na skompletowany kod i testy.
- Wiki pokaże prawdziwy status nowych list: robocze po buildzie, wydane dopiero po osobnej decyzji o publikacji.

## Open Questions / Risks

- Przebieg pełnego LL-PL jest kosztowny, a `verify` wymaga przeglądu próbek K9. Wynik buildu i czas pracy trzeba zmierzyć, nie zakładać z symulacji.
- Dopuszczenie nowej konfiguracji nie może nadpisać zamrożonego v30; wszystkie katalogi wynikowe będą nowe.
- Rozbieżność pełnego diffu, brak straży lub dodatkowy ubytek wymaga zatrzymania i analizy, nie korekty wartości progu pod oczekiwany wynik.

## Zależności i własność plików

`G0 → G1 → G2 → G3 → G4 → G5`. Grupy są sekwencyjne. Koordynator jest właścicielem stanu Maister, planu, dashboardu i dziennika. Brak równoległych piszących agentów.

| Grupa | Zakres | Pliki główne | Warunki |
| --- | --- | --- | --- |
| G0 | Dane decyzji i preflight | `config/generator/standard-age-exceptions.json`, `scripts/check_standard_age_exceptions.py` lub równoważny walidator, `config/generator/sources.json`, testy walidatora | S1, część S2 |
| G1 | Oceny STANDARD | `literaki_slownik/decisions.py`, `policy.py`, `build.py`, `explain.py`, `config/generator/policy.json`, ewentualnie nowy moduł walidacji, `tests/test_standard_age_exceptions.py`, istniejące testy decyzji | S1–S3 |
| G2 | Metoda POP | `literaki_slownik/pop.py`, `explain.py`, `config/generator/pop.json`, `tests/test_pop.py`, `tests/test_pop_v2.py`, `tests/pop_helpers.py`, nowy ADR | P1–P3 |
| G3 | Odbiór na pełnych danych | nowe katalogi `data/work/`, raporty `verification/`, manifesty wejść POP, skrypt porównania zbiorów | S2–S3, P1–P3, R1 |
| G4 | Dokumentacja i wiki | `docs/generator/cli.md`, `docs/generator/etykiety.md`, `docs/runbook-wiki.md`, wiki `Slownik-STANDARD.md`, `Slownik-POP.md`, `Slownik-POP0.md`, `Historia-zmian.md`, ewentualnie `Home.md` | D1 |
| G5 | Kontrola końcowa i przekazanie | raport weryfikacji, stan Maister, komentarze #4/#6, PR | wszystkie |

## G0 — trwały JSON decyzji

- [x] **0.1** Utrwalić identyczność wejść badania: hash zamrożonej bazy, SGJP, badawczych JSON-ów, 2382 napisów i 7192 trójek. Sprawdzić bez modyfikacji bazy, że każda trójka ma jedną analizę; ponowić wynik audytu `{1: 7192}`.
- [x] **0.2** Napisać test walidatora: poprawny przypadek oraz zły hash źródła, duplikat, brak rekordu, zły tag, obcy lemat, forma poza zakresem i konstrukcja bez właściwego klucza mają dawać odmowę bez częściowego dopuszczenia.
- [x] **0.3** Przenieść zatwierdzony zakres do `config/generator/standard-age-exceptions.json`: uporządkowane 2382 przypadki / 7192 dokładnych analiz, dowód rodziny, hash źródła i proveniencja badania. Wstrzymane rodziny oraz osiem cofnięć nie wchodzą.
- [x] **0.4** Dodać referencję `configurations.standard-age-exceptions` z SHA256 do `sources.json`. Walidator i `inspect-sources` muszą wykryć zmianę bez aktualizacji hasha.
- [x] **0.5** Uruchomić testy nowego walidatora i `tests/test_inputs.py`; zachować wynik w work log.

## G1 — decyzje STANDARD z danych

- [x] **1.1** Testy najpierw: pojedynczy dopuszczony zapis, współczesne znaczenie innego homonimu, dawny wariant formy, konstrukcja z istniejących składników, inna odmowa gry/języka, BROAD bez zmiany. Testy powinny wykazać brak obsługi JSON-a przed zmianą kodu.
- [x] **1.2** Wczytać przypięty JSON w fazie `decisions`, zwalidować pełny zestaw kluczy i przekazać mapę dokładnych analiz do `materialize_assessments()` oraz `assess_diagnostic()`.
- [x] **1.3** Zastąpić tylko historyczny reject dla właściwej analizy STANDARD jawnie nazwaną regułą; zachować inne checks, semantyczną pozostałość, status BROAD, konstrukcje oraz wyliczanie członkostwa z bazy. Podnieść wersję polityki.
- [x] **1.4** Zakończyć fazę tylko, gdy każda pozycja JSON-a została użyta dokładnie raz i wyniki 2382/7192 są rozliczone. Zapisane oceny, raport decyzji, manifest i `explain` mają pokazywać tę samą podstawę. Stary przebieg odczytuje swoją zapisaną ocenę.
- [x] **1.5** Uruchomić skupione testy `tests/test_standard_age_exceptions.py`, `tests/test_decisions.py`, `tests/test_semantic_uses.py`, `tests/test_age_baseline.py`, `tests/test_inputs.py`, testy `explain`.

## G2 — stały próg POP

- [x] **2.1** Testy najpierw: próg włącznie z remisem, brak punktacji, własna punktacja członków, wyjątek najmocniejszego, grupa bez rozdzielnych danych, mieszana konfiguracja i odmowa przy naruszeniu podzbioru. Dodać test raportu i `explain pop`.
- [x] **2.2** Dodać `score` dla POP do `threshold()` i ścieżkę przycinania własną punktacją do `prune_members()`, zachowując obecną ścieżkę `count` dla POP0 i starej metody.
- [x] **2.3** Wersjonować konfigurację jako `pop-v3` z `score ≥ −1.042878629`; walidacja `pop-v2` nadal dopuszcza stary, przypięty układ. Raport, `LIMITATIONS.md`, pakiet i `explain pop` pokazują rodzaj progu oraz jego tymczasowy charakter.
- [x] **2.4** Dodać nowy ADR metody i linki; nie przepisywać historycznej decyzji ADR-007. Uruchomić skupione testy `test_pop.py`, `test_pop_v2.py`, `test_check_pop_package.py`.

## G3 — pełne zbiory i odbiór

- [x] **3.1** Przed pełnym buildem uruchomić pełny zestaw testów lokalnych oraz kontrolę pinów i czystości kodu. Zacommitować kod, bo `verify` wymaga zgodnego `code_identity` bez dirty w pakiecie.
- [x] **3.2** Z tych samych przypiętych wejść wykonać dwa nowe przebiegi LL-PL w oddzielnych katalogach. Porównać kanoniczne raporty, dokładny zbiór STANDARD z bazą v30: +2382/0, odpowiednie ślady 7192 ocen i 11 dodatnich oraz 11 ujemnych kontroli. BROAD bez nieplanowanych zmian.
- [x] **3.3** Wygenerować i ocenić próbki jakości nowego przebiegu. Do K9 przygotować przegląd związany hashami; brak zatwierdzonego przeglądu oznacza brak `verify/export` i brak twierdzenia o wydanej liście.
- [x] **3.4** Po K9 uruchomić `verify` na dwóch przebiegach, następnie `export` do nowego katalogu. Sprawdzić status FROZEN, piny i brak zmian starych przebiegów. Aktualizować `config/generator/pop-sources.json` wyłącznie na hash nowego, zweryfikowanego STANDARD.
- [x] **3.5** Zbudować bazowy POP nową metodą na starym, przypiętym STANDARD przy użyciu osobnego historycznego manifestu wejść; porównać dokładny zbiór z wydanym `pop-v2`. Dopiero potem przepiąć roboczy `config/generator/pop-sources.json` na hash nowego, zweryfikowanego STANDARD i wykonać dwa nowe przebiegi POP. Oczekiwane: POP +2372/0, POP0 +481/0, zero braków straży, podzbiory oraz zgodne deterministyczne hashe i niezależny `scripts/check_pop_package.py`.
- [x] **3.6** Zapisać liczniki, hashe, wejścia, pełne delty i ograniczenia w `verification/implementation-verification.md`. Rozbieżność badać przed dalszym krokiem; nie zmieniać progu pod wynik.

## G4 — trwała dokumentacja i wiki

- [x] **4.1** Uzupełnić dokumentację wyjątku STANDARD: jak edytować JSON, przypiąć hash, uruchomić nowy build, sprawdzić dokładne dopasowanie i dlaczego nie wystarczy dopisać formy do gotowej listy.
- [x] **4.2** Zaktualizować opis POP, CLI i ADR; oznaczyć stałą jako tymczasową i podlinkować otwarty #6. W `docs/runbook-wiki.md` dopisać sposób opisu nowej metody.
- [x] **4.3** W klonie wiki zaktualizować STANDARD, POP, POP0 i `Historia-zmian` na podstawie rzeczywistych manifestów. `Home` tylko jeżeli zmienia się opis/stany. Zachować stare wydane liczby i linki, gdy nowe listy są jedynie robocze. Przykłady sprawdzić w listach.
- [x] **4.4** Sprawdzić linki, hashe, liczby, stan git wiki i długość stron; commit/push wiki według runbooka. Nie publikować nowego wydania bez osobnej decyzji.

## G5 — weryfikacja i przekazanie

- [~] **5.1** POMINIĘTE (decyzja właściciela 2026-10-14: bez przeglądów agentów, od razu PR).** Uruchomić kanoniczną weryfikację Maister, przegląd poprawności i realności, sprawdzić kompletność S1–D1 i czystość repo. Po istotnej poprawce odświeżyć raport.
- [x] **5.2** Uaktualnić #4 i #6 wynikami, ograniczeniami oraz linkami do konfiguracji, ADR i wiki. #6 zostawić otwarty dla merytorycznej granicy POP; #4 rozliczyć tylko w zakresie zatwierdzonych dodatków.
- [x] **5.3** Commit/push repo oraz PR z finalnym opisem zachowania i walidacji. Nie uruchamiać CI na runnerach GitHub-hosted. Decyzja o wydaniu i integracji z grą pozostaje oddzielna.

## Komendy kontrolne

```sh
python3 -m unittest tests.test_inputs tests.test_decisions tests.test_semantic_uses tests.test_age_baseline tests.test_pop tests.test_pop_v2 tests.test_check_pop_package
python3 -m unittest discover -s tests -p 'test_*.py'
python3 -m literaki_slownik inspect-sources --manifest config/generator/sources.json --json
python3 -m literaki_slownik build --manifest config/generator/sources.json --run-dir <nowy-a> --json
python3 -m literaki_slownik build --manifest config/generator/sources.json --run-dir <nowy-b> --json
python3 -m literaki_slownik verify --run-dir <nowy-a> --peer-run <nowy-b> --review <oceniony-przeglad> --json
python3 -m literaki_slownik export --run-dir <nowy-a> --output-dir <nowy-pakiet> --json
python3 -m literaki_slownik pop --manifest config/generator/pop-sources.json --config config/generator/pop.json --output-dir <nowy-pop-a> --json
python3 scripts/check_pop_package.py --pop-dir <nowy-pop-a> --standard <nowy-a>/lists/standard.txt
```

## Wycofanie

Nie kasować ani nie modyfikować historycznych katalogów i wydań. Na niepowodzeniu zostawić poprzednie manifesty jako operacyjny punkt odniesienia, oznaczyć nowy przebieg jako nieprzyjęty i poprawić kod/JSON w nowej rewizji. Każdy ponowny build używa nowego katalogu. Cofnięcie opublikowanego wydania lub zmian wiki wymaga odrębnej decyzji właściciela.

## Status planu

Plan opublikowano w [komentarzu #4](https://github.com/robmar-net/literaki-slownik/issues/4#issuecomment-6125514977) 2026-10-12T13:44:55Z. Właściciel wykona implementację osobno. Wszystkie kroki G0–G5 pozostają niewykonane.
