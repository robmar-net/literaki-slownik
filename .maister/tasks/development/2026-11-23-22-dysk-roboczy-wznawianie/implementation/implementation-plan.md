# Plan implementacji: build na T7 z wznawianiem (#22)

## TL;DR
14 grup, 95 kroków, ok. 76–86 testów. Każda grupa zaczyna od testów i kończy się uruchomieniem tylko swoich testów. Pełny zestaw idzie raz, w grupie 14.
Fala 1 (równolegle): `.gitignore` (1), trwały zapis (2), skrypt i pomiar `fullfsync` na T7 (3). Potem łańcuch: strażnik (4) → układ i kody (5) → etapy (6) → `--resume` (7).
Promocja (10) rusza po 5, równolegle z 7. Po 7: `fullfsync` w buildzie (8), nadzorca (9), sprzątanie (11), historia (12), też równolegle. Na końcu dokumentacja (13) i pełny zestaw (14).
Pomiar w grupie 3 uruchamia tylko `measure_fullfsync.py`, nigdy `build`. Wynik trafia do ADR-020 i do stałej `FULLFSYNC_MODE`.

## Key Decisions
- Fala 1 to trzy osobne grupy o rozłącznych plikach. Mogą iść równolegle.
- Pomiar idzie w grupie 3, przed kodem trybu `fullfsync` (grupa 8). Grupa 8 tylko czyta gotową stałą, więc wybór 4B/4C nie czeka na resztę.
- Spec ma 13 wymagań, więc plan ma 13 grup i grupę testów. Daje to więcej testów niż typowe 16–34. Limit 2–8 na grupę obowiązuje.
- `explain` (tylko statusy etapów) idzie w grupie 5 razem z nowymi polami manifestu, bo tam powstaje ryzyko dla K7.
- Grupy 6 i 7 dzielą `build.py`, więc idą po kolejności. Grupa 6 przy weryfikacji uruchamia też `test_build`, `test_reports` i `test_lifecycle`, bo przebudowuje `build()`.
- Grupa 10 (promocja) zależy tylko od 4 i 5, więc może iść równolegle z 6–7. `export.py` zmienia też grupa 12, dlatego 12 czeka na 10.

## Open Questions / Risks
- Pomiar wymaga zamontowanego T7. Gdy dysku brak, grupa 3 staje na kroku 3.7. Nie mierzy niczego na dysku wewnętrznym, a `FULLFSYNC_MODE` zostaje `build`.
- `quick_check` przebiegu referencyjnego czyta ~21 GB z dysku wewnętrznego. To kilka minut, uruchamiane w tle.
- Wspólne pliki: `build.py` (2, 5, 6, 7, 8), `database.py` (3, 5, 8), `canonical.py` (2, 4), `cli.py` (5, 7), `export.py` (10, 12). Zależności je serializują.
- Harness R6 (grupa 7) to najdroższy test zestawu. Ma wiele punktów przerwania na fiksturze, więc trzeba pilnować czasu (`subTest`, jedna fikstura).
- `.maister/tasks` leży w publicznym repo, więc wynik pomiaru zapisuje się bez ścieżek i UUID.
- Narzędzie `TaskCreate` nie było dostępne. Postęp śledzą checkboxy w tym pliku i znaczniki w HTML.

## Overview
Total Steps: 95
Task Groups: 14
Expected Tests: ~76 w grupach 1–13 (2–8 na grupę) + do 10 w grupie 14

## Implementation Steps

### Task Group 1: `.gitignore` i katalog logów
**Dependencies:** None
**Files to Modify:** `.gitignore`, `tests/test_gitignore.py`
**Estimated Steps:** 3

- [x] 1.0 Ignorowanie symlinków przebiegów i logów
  - [x] 1.1 Napisać 2 testy w `tests/test_gitignore.py`
    - Tymczasowe repo git z kopią `.gitignore`: `git check-ignore` łapie symlink `data/work/x` i plik `logs/x.out.json`.
    - Plik kodu (`literaki_slownik/x.py`) nie jest ignorowany.
  - [x] 1.2 Dodać `/logs` do `.gitignore`, bez końcowego ukośnika, z komentarzem po polsku. Wpis `/data/work/` zostaje.
  - [x] 1.3 Uruchomić tylko testy z 1.1

**Acceptance Criteria:**
- Oba testy przechodzą. Symlinki w `data/work` i pliki w `logs/` są ignorowane (R1, L2).

### Task Group 2: Trwały zapis plików (R3)
**Dependencies:** None
**Files to Modify:** `literaki_slownik/canonical.py`, `literaki_slownik/build.py`, `tests/test_durable_write.py`
**Estimated Steps:** 7

- [x] 2.0 `write_json` i `write_bytes` trwałe na zewnętrznym dysku
  - [x] 2.1 Napisać 5 testów w `tests/test_durable_write.py`
    - Kolejność wywołań (mock): tmp w tym samym katalogu → zapis → `fcntl(F_FULLFSYNC)` → hook → `os.replace` → fsync katalogu.
    - Fallback na `os.fsync`, gdy `fcntl` nie ma `F_FULLFSYNC` albo zwraca błąd.
    - Przerwanie przed `replace` zostawia stary plik i nie zostawia tmp.
    - `unlink` rzucający `OSError` nie zmienia typu pierwotnego wyjątku.
    - `write_lists` pisze przez `write_bytes` i daje te same bajty list.
  - [x] 2.2 Wspólna funkcja zapisu trwałego dla bajtów, z kolejnością z R3
  - [x] 2.3 Hook przed `os.replace`: `set_replace_guard(fn)`, domyślnie brak. Podłącza go grupa 4.
  - [x] 2.4 `write_json` serializuje jak dziś (te same bajty) i woła wspólną funkcję. Dodać `write_bytes(path, data)`.
  - [x] 2.5 Sprzątanie tmp w `finally` w `try/except OSError`, żeby pierwotny błąd poleciał dalej
  - [x] 2.6 `build.write_lists` przez `write_bytes`. Nazwy i bajty plików list bez zmian.
  - [x] 2.7 Uruchomić tylko testy z 2.1

**Acceptance Criteria:**
- 5 testów przechodzi. Bajty `write_json` są takie jak przed zmianą.

### Task Group 3: Skrypt pomiaru i jednorazowy pomiar `fullfsync` na T7 (R8, ADR-020)
**Dependencies:** None
**Files to Modify:** `scripts/measure_fullfsync.py`, `tests/test_measure_fullfsync.py`, `literaki_slownik/database.py`, `docs/adr/ADR-020-fullfsync.md`, `.maister/tasks/development/2026-11-23-22-dysk-roboczy-wznawianie/verification/fullfsync-measurement.json`
**Estimated Steps:** 9

- [x] 3.0 Pomiar narzutu `fullfsync` i wybór 4B/4C
  - [x] 3.1 Napisać 5 testów w `tests/test_measure_fullfsync.py` (na `tempfile`)
    - JSON ma oba warianty (`fullfsync_off`, `fullfsync_on`: mediana czasu commitu, liczba commitów próby).
    - `--reference-run` (fikstura z `reports/import-counts.json` i `reports/decisions.json`) daje `build_commits`, `overhead_pct` według wzoru ze spec i `choice`.
    - `--quick-check` podaje wynik i czas na kopii fikstury, otwartej tylko do odczytu.
    - Wynik nie zawiera ścieżek absolutnych. Katalog `--dir` znika na końcu.
    - Istniejący `--dir` → odmowa, nic nie skasowane.
  - [x] 3.2 `scripts/measure_fullfsync.py` (stdlib, bez importu buildu słownika)
    - Tworzy `--dir` (`parents=False`) i w nim tymczasową bazę: `journal_mode=DELETE`, `synchronous=FULL`.
    - Mierzy serie commitów z partią wierszy przy `fullfsync=OFF` i `ON`, naprzemiennie, kilka powtórzeń, mediana.
  - [x] 3.3 Liczba commitów buildu: rekordy referencyjnego przebiegu / 10 000 w górę plus commity etapów
    - `overhead_pct = (ON − OFF) × commity / 46 800 × 100`.
    - `choice`: `build` przy ≤ 5%, inaczej `stage_boundaries`.
  - [x] 3.4 `--quick-check DB`: `PRAGMA quick_check` przez URI `mode=ro`, wynik i czas
  - [x] 3.5 W `database.py`: stała `FULLFSYNC_MODE = 'build'` i krotka dozwolonych wartości. Zachowanie bez zmian, stałą czyta dopiero grupa 8.
  - [x] 3.6 Uruchomić tylko testy z 3.1. Muszą przejść przed 3.7.
  - [x] 3.7 Jednorazowy pomiar na T7. Uruchamia tylko ten skrypt, bez `build` i bez zmian w przebiegach.
    - Sprawdzić, czy `/Volumes/Data` jest punktem montowania i ma wolne miejsce. Gdy nie, przerwać i zgłosić, bez zastępstwa na dysku wewnętrznym.
    - Uruchomić w tle: `python3 scripts/measure_fullfsync.py --dir /Volumes/Data/.measure-<stempel> --reference-run data/work/<ostatni FROZEN> --quick-check data/work/<ostatni FROZEN>/build.sqlite`. Dziś ostatni `FROZEN` to `lists-v32-20261104-161601-a`.
    - Na końcu sprawdzić, czy katalog `.measure-<stempel>` zniknął.
  - [x] 3.8 Zapisać JSON wyniku do `verification/fullfsync-measurement.json` w katalogu zadania (bez ścieżek i UUID). Ustawić `FULLFSYNC_MODE` według reguły.
  - [x] 3.9 Napisać `docs/adr/ADR-020-fullfsync.md` po polsku, bez ścieżek i UUID
    - Liczby: czasy ON i OFF, commity, `overhead_pct`, czas `quick_check`, data pomiaru.
    - Wybór 4B/4C.
    - `F_FULLFSYNC` i fsync katalogu w zapisie plików, `quick_check` przy wznowieniu.
    - Zakazy: WAL, `journal_mode=OFF/MEMORY`, `synchronous<FULL`.

**Acceptance Criteria:**
- 5 testów przechodzi.
- Pomiar wykonany na T7, bez buildu słownika. Katalog pomiaru skasowany.
- ADR-020 zawiera zmierzony narzut i wybrany tryb. `FULLFSYNC_MODE` ma ten sam tryb.

### Task Group 4: Strażnik wolumenu i znacznik (R2)
**Dependencies:** 2
**Files to Modify:** `literaki_slownik/volume.py`, `scripts/init_work_volume.py`, `literaki_slownik/canonical.py`, `tests/test_volume.py`
**Estimated Steps:** 8

- [x] 4.0 Moduł `volume.py` i `init_work_volume.py`
  - [x] 4.1 Napisać 8 testów w `tests/test_volume.py` (podstawione `os.path.ismount`, `os.stat`, `os.statvfs`, `subprocess`)
    - Brak montowania → 75. Inny `marker_id` → 76. Zmiana `st_dev` (G3) → 75. Wolne < 50 GB → 78.
    - Ścieżka wewnętrzna bez znacznika i bez `--work-root` → przepuszcza (`work_volume` null).
    - `--work-root` bez znacznika na dysku repo → 76. Zewnętrzny wolumen bez znacznika → 76.
    - `init_work_volume.py` drugi raz → odmowa. Korzeń na dysku repo → odmowa.
    - `find_by_marker` znajduje znacznik pod inną ścieżką (np. `<nazwa> 1`).
    - Hook zapisu: cel w aktywnym przebiegu ze zmienionym `st_dev` → 75, a stary plik zostaje.
  - [x] 4.2 `mount_point(path)`: najbliższy przodek po `realpath`, dla którego `ismount` jest prawdą. Do tego punkt montowania repo.
  - [x] 4.3 Znacznik `.literaki-work-volume` i kontrole według tabeli „Strażnik”: start świeży (z `--work-root` i bez) oraz `--resume`/nadzorca. Błędy jako `GeneratorError(…, 75|76|78)`.
  - [x] 4.4 Miejsce przez `os.statvfs`: próg 50 GB na proces, stała 100 GB dla pary (dla `build_pair.sh`)
  - [x] 4.5 G3: `activate(run_dir)` zapamiętuje `realpath` i `st_dev`; `check_active()` i `check_target(path)` (tylko cele w aktywnym przebiegu). Podłączyć przez `canonical.set_replace_guard`.
  - [x] 4.6 `find_by_marker(marker_id)` przegląda punkty montowania w `/Volumes`
  - [x] 4.7 `scripts/init_work_volume.py <korzeń>`
    - UUID z `diskutil info -plist` (`plistlib`), losowy `marker_id` (`secrets`), zapis przez `write_json`.
    - Odmowa, gdy znacznik istnieje albo korzeń leży na dysku repo.
    - stdout: JSON tylko z `marker_id`.
  - [x] 4.8 Uruchomić tylko testy z 4.1

**Acceptance Criteria:**
- 8 testów przechodzi. Kody zgodne z tabelą „Strażnik”.
- UUID wolumenu jest tylko w znaczniku, nigdy w stdout ani w manifeście.

### Task Group 5: Układ przebiegu, pola manifestu i kody wyjścia (R1, R4)
**Dependencies:** 4
**Files to Modify:** `literaki_slownik/run.py`, `literaki_slownik/build.py`, `literaki_slownik/cli.py`, `literaki_slownik/database.py`, `literaki_slownik/explain.py`, `tests/test_run.py`, `tests/test_run_layout.py`, `tests/test_exit_codes.py`
**Estimated Steps:** 9

- [x] 5.0 `build --work-root`, symlink przebiegu i klasyfikator błędów
  - [x] 5.1 Napisać 8 testów w `tests/test_run_layout.py` i `tests/test_exit_codes.py`
    - `build --work-root W` (podstawiony znacznik): katalog `W/<nazwa>`, symlink `data/work/<nazwa>` na końcu, `work_volume.marker_id`, jedna próba w `build_attempts`, `resume` = `{false, 0}`.
    - Brak montowania → 75 i brak nowych plików w `data/work`.
    - Resztka startu (bez symlinku, bez `build.sqlite`, wszystkie etapy `pending`) → build przechodzi. Inna zawartość → 4.
    - Wstrzyknięty `sqlite3.OperationalError('disk I/O error')`: strażnik upadły → 75, zdrowy → 4.
    - `SQLITE_FULL` i `ENOSPC` → 78. `SQLITE_CORRUPT` → 77.
    - Rollback rzucający w `connect` i nieudany zapis `failed` nie zmieniają kodu.
    - CLI `build` zwraca te kody. Goły `sqlite3.Error` w `cli.py` → 4, nie traceback.
    - `explain` zwraca `stages` jako `{"<etap>": "<status>"}`.
  - [x] 5.2 `run.create_run`: `mkdir(parents=False)`, wariant z `work_root` (sprzątanie resztki startu, symlink po manifeście i `reports/`), pola `work_volume`, `build_attempts`, `resume`. Poprawić `tests/test_run.py`.
  - [x] 5.3 Zamykanie próby (`ended`, `last_stage`, `outcome`, `exit_code`). Błąd zamknięcia jest pomijany.
  - [x] 5.4 `cli build --work-root`. Bez niego jak dziś (dysk wewnętrzny, `work_volume` null). Po `create_run` `volume.activate`.
  - [x] 5.5 Klasyfikator w `except` w `build.py`: rollback (błąd pomijany) → `close` → strażnik (75/76) → `sqlite_errorcode`/`errno` (78/77) → 4. `GeneratorError` i `KeyboardInterrupt` jak dziś.
  - [x] 5.6 `database.connect`: rollback i `close` w `try`, ich błąd pomijany
  - [x] 5.7 `cli.py`: `except sqlite3.Error` → 4. Kody 75–78 przez `GeneratorError.code`.
  - [x] 5.8 `explain`: `stages` tylko ze statusami. K7 nie zależy od historii.
  - [x] 5.9 Uruchomić testy z 5.1 i `tests/test_run.py`

**Acceptance Criteria:**
- 8 testów i `test_run.py` przechodzą.
- Kody zgodne z tabelą „Kody wyjścia”. Bez T7 nic nie powstaje na dysku systemowym.

### Task Group 6: Pętla etapów, cztery poprawki i znaczniki raportów (R6 część, R7)
**Dependencies:** 5
**Files to Modify:** `literaki_slownik/build.py`, `literaki_slownik/links.py`, `tests/test_stage_loop.py`, `tests/test_report_markers.py`
**Estimated Steps:** 8

- [x] 6.0 `build()` jako pętla etapów według `STAGES`
  - [x] 6.1 Napisać 7 testów w `tests/test_stage_loop.py` i `tests/test_report_markers.py`
    - `construction-candidates.json` bez `new_candidates`, `decisions.json` bez `new_analyses`/`new_decisions`. Funkcje `materialize_*` dalej je zwracają.
    - `import-counts.json` liczony z bazy ma te same metryki co dziś na fiksturze.
    - `inventory.json`, `qualifier-conditions.json` i `import-counts.json` istnieją przed `import_kwjp: complete`.
    - `links`: `running` na starcie, drugi `create_links` na tej samej bazie nie pada, `pending` z `reason`, gdy etap jest niekompletny.
    - `preflight: complete` dopiero po commicie `source_artifact`.
    - Znacznik ze złym hashem → raport liczony od nowa. `unresolved` z pliku daje te same bajty raportów zależnych.
    - `.done/` nie wchodzi do `canonical-index`.
  - [x] 6.2 Podział `build()` na funkcje etapów i jedna pętla od wskazanego etapu. Świeży build zaczyna od `preflight`.
  - [x] 6.3 Poprawka 1: usunięcie `new_*` z raportów kanonicznych przed zapisem
  - [x] 6.4 Poprawki 2 i 3: `import-counts.json` z bazy. Trzy pliki zapisywane na końcu `import_kwjp`, przed `complete`.
  - [x] 6.5 Poprawka 4 (`links`): `set_stage(running)`, osobne `DROP TABLE IF EXISTS evidence_candidate`, potem `evidence_link`. Na końcu `complete` albo `pending` z `reason`.
  - [x] 6.6 `preflight: complete` po utworzeniu bazy i commicie `source_artifact`
  - [x] 6.7 Znaczniki `reports/.done/<raport>.json`
    - Pola: `sha256`, `bytes`, `tree_sha256`, `manifest_sha256`. Najpierw raport, potem znacznik.
    - Raport jest pomijany tylko przy pełnej zgodności. Przy pominięciu `unresolved` czytany z `reports/unresolved.json`.
    - Świeży build też pisze znaczniki.
  - [x] 6.8 Uruchomić testy z 6.1 oraz `tests/test_build.py`, `tests/test_reports.py`, `tests/test_lifecycle.py` (regresja podziału)

**Acceptance Criteria:**
- 7 nowych testów i trzy istniejące moduły przechodzą.
- Świeży build daje te same `canonical-index`, `logical-content` i `lists/*.txt` co przed podziałem.

### Task Group 7: `build --resume`, reset i harness „wznowiony = świeży” (R5, R6)
**Dependencies:** 6
**Files to Modify:** `literaki_slownik/build.py`, `literaki_slownik/run.py`, `literaki_slownik/cli.py`, `tests/test_resume.py`, `tests/test_resume_equivalence.py`
**Estimated Steps:** 7

- [x] 7.0 Wznowienie od pierwszego niegotowego etapu
  - [x] 7.1 Napisać 8 testów w `tests/test_resume.py` i `tests/test_resume_equivalence.py`
    - Po jednej odmowie na każdą kontrolę (`subTest`): brak przebiegu 4, wiszący symlink 75 (nie 4), G1 75, nieczytelny manifest 4, `VERIFIED` 5, G2 76, miejsce 78, kod 4, wejścia 3, `quick_check` 77.
    - `running` po `os._exit` w procesie potomnym → `failed`. Otwarta próba → `interrupted`, `resume.count` + 1.
    - Niegotowy `preflight` → przebieg od nowa w tym samym katalogu.
    - Reset każdego etapu według tabeli: tabele, wiersz `own-semantic-use-review-v1`, `.done/` skasowane po etapie przed `reports`.
    - Harness: przerwanie na każdej granicy etapu, w środku `import_kwjp`, `constructions`, `links` i między każdą parą raportów. Po `--resume` pliki są bajtowo równe świeżemu buildowi.
    - Podwójne przerwanie i drugie `--resume` dają wynik świeżego.
    - Para wznowiony + świeży → `verify` VERIFIED (`complete_pair`).
  - [x] 7.2 `cli build --resume --manifest M --run-dir R`
  - [x] 7.3 Kontrole w kolejności 1–11 ze spec. Przenieść kontrole z `scripts/resume_reports.py:44-52` do wspólnej walidacji.
  - [x] 7.4 Krok 12: `running` → `failed`, otwarta próba `interrupted`, nowa próba, `resume` + 1
  - [x] 7.5 Reset w jednej transakcji, z commitem i pełnym flushem przed `set_stage(running)`. DROP dziecka przed rodzicem, DROP przed DELETE.
  - [x] 7.6 Harness w testach: wyjątek wstrzykiwany w podstawioną funkcję etapu albo raportu, jedna fikstura, punkty przez `subTest`
  - [x] 7.7 Uruchomić tylko testy z 7.1

**Acceptance Criteria:**
- 8 testów przechodzi. Każdy punkt przerwania daje bajtowo ten sam wynik co świeży build.
- Para wznowiony + świeży przechodzi K8.

### Task Group 8: SQLite PRAGMA i tryb `fullfsync` w buildzie (R8)
**Dependencies:** 3, 7
**Files to Modify:** `literaki_slownik/database.py`, `literaki_slownik/build.py`, `tests/test_durability_modes.py`
**Estimated Steps:** 4

- [x] 8.0 Trwałość bazy według wyniku pomiaru
  - [x] 8.1 Napisać 4 testy w `tests/test_durability_modes.py`
    - Zapisywalny `connect` → `journal_mode=delete`, `synchronous=2` (FULL). `readonly` bez zmian.
    - Tryb `build`: `fullfsync=1` w trakcie etapu i na granicy.
    - Tryb `stage_boundaries`: `fullfsync=0` w etapie. Na końcu `F_FULLFSYNC` na `build.sqlite` (mock), potem pliki etapu, potem manifest `complete`.
  - [x] 8.2 `connect` dla bazy zapisywalnej: `journal_mode=DELETE`, `synchronous=FULL`
  - [x] 8.3 Pętla etapów stosuje `FULLFSYNC_MODE` z grupy 3. Kolejność zawsze: dane trwale → pliki etapu → manifest.
  - [x] 8.4 Uruchomić tylko testy z 8.1

**Acceptance Criteria:**
- 4 testy przechodzą w obu trybach. Żadnego WAL ani `synchronous<FULL`.

### Task Group 9: Nadzorca, `build_pair.sh` i nakładka `resume_reports.py` (R9)
**Dependencies:** 1, 4, 7
**Files to Modify:** `scripts/build_supervised.py`, `scripts/build_pair.sh`, `scripts/resume_reports.py`, `tests/test_build_supervised.py`, `tests/test_resume_reports.py`
**Estimated Steps:** 9

- [x] 9.0 Czekanie na dysk i wznawianie tylko po 75
  - [x] 9.1 Napisać 8 testów w `tests/test_build_supervised.py` i `tests/test_resume_reports.py` (podstawiony build, `sleep` i zegar)
    - 75, 75, 0 → 0. 75 × 4 → 75 po 3 wznowieniach.
    - 75 przed powstaniem przebiegu → świeży build, nie `--resume`.
    - 4 → stop. 77 → stop.
    - G1 bez G2 → 76. Wolumen pod inną ścieżką → 76 od razu. Czekanie dłuższe niż limit → 75.
    - SIGINT → 130 bez wznowienia.
    - `build_pair.sh` bez `LITERAKI_WORK_ROOT` → 2.
    - `resume_reports.py` przekazuje kod `build --resume`.
  - [x] 9.2 Funkcja `supervise(...)` z wstrzykiwanym uruchamianiem buildu, `sleep`, zegarem i sondą wolumenu. Wybór polecenia: `lexists` i czytelny manifest.
  - [x] 9.3 Po 75: co `poll` sekund G1+G2 i `find_by_marker`. Limit `wait` minut, maks. 3 wznowienia.
  - [x] 9.4 Sygnały: SIGINT do dziecka i 130. SIGTERM/SIGHUP do dziecka i kod dziecka, bez wznowienia.
  - [x] 9.5 Logi w `logs/` na dysku wewnętrznym
    - `<nazwa>.out.json` (dopisywany), `<nazwa>.err`, `<nazwa>.supervisor.log` (linia JSON na zdarzenie).
    - `flock` na `logs/<nazwa>.lock` przez cały czas pracy. Plików przebiegu nie dotyka.
  - [x] 9.6 CLI `main()` opakowuje `supervise` (argumenty ze spec)
  - [x] 9.7 `build_pair.sh`
    - Wymaga `LITERAKI_WORK_ROOT` (inaczej 2), czystego kodu i ≥ 100 GB na W (inaczej 78).
    - `mkdir -p logs`, dwóch nadzorców pod `caffeinate -dimsu`. Ścieżki `data/work/<nazwa>-<stempel>-<a|b>` bez zmian.
  - [x] 9.8 `resume_reports.py` jako nakładka: dzisiejsze kontrole, potem `build --resume`, kod wyjścia dalej
  - [x] 9.9 Uruchomić tylko testy z 9.1

**Acceptance Criteria:**
- 8 testów przechodzi bez czekania w czasie rzeczywistym. Ponawiany jest tylko kod 75.

### Task Group 10: Promocja i odmowa `export` na T7 (R10)
**Dependencies:** 4, 5
**Files to Modify:** `scripts/promote_run.py`, `literaki_slownik/export.py`, `tests/test_promote_run.py`
**Estimated Steps:** 9

- [x] 10.0 `promote_run.py` ze stanami S0–S4
  - [x] 10.1 Napisać 8 testów w `tests/test_promote_run.py` („T7” = katalog tymczasowy z podstawionym `ismount`, fikstura `complete_pair`)
    - A nie `VERIFIED` → 5. Zmiana pliku na T7 po verify → 5.
    - Różny sha256 albo tryb kopii → 4 i nic nie skasowane.
    - Zniknięcie T7 w trakcie kopii → 75, staging zostaje.
    - Przerwanie w każdym stanie S0–S3 i ponowne wywołanie kończy promocję (`subTest`).
    - Ponowne wywołanie po `export` kasuje kopię na T7.
    - B kasowany tylko, gdy jest `INCOMPLETE` i zgadza się `canonical_index_sha256`. Inaczej zostaje.
    - `export` symlinku albo ścieżki na wolumenie roboczym → 5.
    - `export` po promocji przechodzi `changes_since_verify` mimo `promotion.json`. `promotion.json` jest poza pieczęcią i poza `canonical-index`.
  - [x] 10.2 Rozpoznanie stanu S0–S4. Blokada `logs/<A>.promote.lock`.
  - [x] 10.3 S0: `VERIFIED` (5), `changes_since_verify` puste (5), wolumen i `marker_id` (75/76), miejsce wewnątrz ≥ rozmiar × 1,1 (78)
  - [x] 10.4 S1: staging `data/work/.<A>.promote` od zera
    - Tylko zwykłe pliki i katalogi; symlink albo plik specjalny → 4.
    - Zapis trwały, ten sam tryb i `mtime`. Potem porównanie sha256 i trybu z T7.
    - `promotion.json`, a na końcu `changes_since_verify(staging)` puste.
  - [x] 10.5 S1 → S2: `renamex_np(RENAME_SWAP)` według wzoru `rename_noreplace`, `unlink` dawnego symlinku, fsync `data/work`
  - [x] 10.6 S2/S3
    - Strażnik dla `t7_path`.
    - Kasowanie B według warunków. Kasowanie kopii A, gdy nie jest katalogiem wewnętrznym.
    - Ustawienie `completed`.
  - [x] 10.7 Błąd I/O → strażnik (75/76), inaczej 4. Zdarzenia w `logs/<A>.promote.log`. Manifest A bez zmian.
  - [x] 10.8 `export.py`: odmowa 5 dla symlinku albo ścieżki na wolumenie roboczym („przebieg na T7; najpierw promote_run.py”)
  - [x] 10.9 Uruchomić tylko testy z 10.1

**Acceptance Criteria:**
- 8 testów przechodzi. Promocję da się wznowić z każdego stanu.
- `export` z T7 jest niemożliwy. Pieczęć `verify` zostaje ważna po promocji.

### Task Group 11: Sprzątanie `clean_work.py` (R11)
**Dependencies:** 4, 10
**Files to Modify:** `scripts/clean_work.py`, `tests/test_clean_work.py`
**Estimated Steps:** 6

- [x] 11.0 Lista domyślnie, kasowanie tylko klas T7 i zaakceptowanych wydań
  - [x] 11.1 Napisać 8 testów w `tests/test_clean_work.py`
    - Drzewo z każdą klasą: bez `--apply` na dysku nic się nie zmienia. `--apply` kasuje tylko klasy 5–6.
    - `VERIFIED`/`FROZEN` bez symlinku nigdy nie jest kasowany. Katalog z rekordu promocji też nie.
    - Wydanie przypięte, bieżące albo ostatnie w rodzinie nigdy nie jest kandydatem.
    - `NOTICE` w prawdziwym kształcie w tymczasowym repo git z `refs/remotes/origin/main`: hash pliku listy → wydanie potrzebne.
    - Brak repo albo `NOTICE` → zero kandydatów i `server_notice: unavailable` z powodem.
    - `--delete-releases` z nazwą potrzebną → odmowa całości (4). Nazwa kandydata → skasowane po `chmod u+w`.
  - [x] 11.2 Klasy 1–8 według pierwszeństwa. Trzymane blokady wykrywa `flock(LOCK_NB)`, próg wieku to 24 h.
  - [x] 11.3 Wydania do głębokości 2. Rodzina do `-v<cyfry>`, wersja jako krotka (`v1r2` → (1, 2)), nierozpoznane → klasa 7. Razem z wydaniem idzie jego przebieg `FROZEN`.
  - [x] 11.4 Wydania potrzebne
    - Piny w `config/generator/*-sources.json`.
    - `NOTICE` przez `git -C <server-repo> show origin/main:NOTICE`, bez `fetch` i bez sieci.
    - `--server-current` i reguła „ostatnie w rodzinie”.
  - [x] 11.5 Wyjście JSON (wpis, klasa, rozmiar, powód), `--apply`, `--delete-releases PLIK` (wymaga `--apply`). Kody 0, 2, 4.
  - [x] 11.6 Uruchomić tylko testy z 11.1

**Acceptance Criteria:**
- 8 testów przechodzi. Bez zgody właściciela nic nieodtwarzalnego nie znika.

### Task Group 12: Historia prób w `verify` i `export` (R12)
**Dependencies:** 7, 10
**Files to Modify:** `literaki_slownik/verify.py`, `literaki_slownik/export.py`, `tests/test_build_history.py`
**Estimated Steps:** 5

- [ ] 12.0 Skrót `build_history`
  - [ ] 12.1 Napisać 3 testy w `tests/test_build_history.py`
    - Wznowiony przebieg: skrót w `verify` (JSON i tekst).
    - Skrót w `release-manifest.json` → `source_run.build_history`.
    - Ręczna zmiana `build_attempts` po verify → `export` kończy się kodem 5.
  - [ ] 12.2 Funkcja skrótu: `resumed`, `attempts`, `outcomes`, `exit_codes`, `resumed_from`
  - [ ] 12.3 `verify`: skrót w wyniku JSON i tekstowym. `SEAL_EXCLUDED` bez zmian.
  - [ ] 12.4 `export`: `source_run.build_history`
  - [ ] 12.5 Uruchomić tylko testy z 12.1

**Acceptance Criteria:**
- 3 testy przechodzą. K8 bez zmian.

### Task Group 13: Dokumentacja i ADR (R13)
**Dependencies:** 3, 8, 9, 10, 11, 12
**Files to Modify:** `docs/adr/ADR-014-*.md` … `docs/adr/ADR-021-*.md` (020 tylko uzupełnienie), `docs/generator/cli.md`, `docs/plan-dalszych-prac-runbook.md`, `.maister/docs/INDEX.md`, `tests/test_cli_docs.py`
**Estimated Steps:** 6

- [ ] 13.0 Opis nowego przebiegu pracy
  - [ ] 13.1 Napisać 2 testy w `tests/test_cli_docs.py`
    - `cli.md` zawiera kody 75, 76, 77, 78, `--resume`, `--work-root` i nazwy pięciu nowych skryptów.
    - ADR-014..021 istnieją i nie mają UUID ani ścieżek domowych.
  - [ ] 13.2 ADR-014..019 i ADR-021 według mapy ze spec i `decision-log.md`. Po polsku, zwięźle. ADR-020 uzupełnić tylko o to, co zmieniła grupa 8.
  - [ ] 13.3 `docs/generator/cli.md`
    - `build --resume`, `--work-root`, kody 75–78.
    - `build_supervised.py`, `promote_run.py`, `clean_work.py`, `init_work_volume.py`, `measure_fullfsync.py`.
    - Nowe kody `resume_reports.py`.
  - [ ] 13.4 Runbook (`docs/plan-dalszych-prac-runbook.md`, sekcja „Nowy przebieg i awaria”)
    - Raz `init_work_volume.py`, potem `build_pair.sh` z `LITERAKI_WORK_ROOT`.
    - Nadzorca po restarcie, `verify … && promote_run.py …`, `clean_work.py` jako lista.
  - [ ] 13.5 `.maister/docs/INDEX.md`: wpisy ADR-014..021 i zadania #22
  - [ ] 13.6 Uruchomić tylko testy z 13.1

**Acceptance Criteria:**
- 2 testy przechodzą. Dokumenty opisują wszystkie nowe polecenia i kody.

### Task Group 14: Przegląd testów, luki i pełny zestaw
**Dependencies:** 1–13
**Files to Modify:** `tests/test_*.py` (tylko dopiski luk, maks. 10 testów)
**Estimated Steps:** 5

- [ ] 14.0 Przegląd i uzupełnienie luk
  - [ ] 14.1 Przejrzeć testy z grup 1–13 (~76)
  - [ ] 14.2 Znaleźć luki tylko w zakresie #22, np. kody end-to-end przez CLI, promocja + `clean_work.py` na jednym drzewie
  - [ ] 14.3 Dopisać najwyżej 10 testów
  - [ ] 14.4 Uruchomić pełny zestaw: `python3 -m unittest discover -s tests -p 'test_*.py'` i `python3 -m unittest discover -s scripts -p 'test_audit_sgjp.py'`. Sprawdzić linię wyniku, nie tylko kod wyjścia.
  - [ ] 14.5 Kontrole repo
    - grep UUID (8-4-4-4-12) i ścieżek domowych w zmienionych plikach i w artefaktach zadania.
    - Brak `.github/workflows`.
    - `git status` bez plików z `data/work/` i `logs/`.
    - `git diff --stat config/` puste (skład słownika bez zmian).

**Acceptance Criteria:**
- Oba pełne zestawy przechodzą. Dodano najwyżej 10 testów.
- Brak UUID i ścieżek domowych. Skład słownika bez zmian.

## Execution Order

1. Fala 1, równolegle:
   - Group 1: `.gitignore` (3 kroki)
   - Group 2: trwały zapis (7 kroków)
   - Group 3: pomiar `fullfsync` (9 kroków)
2. Group 4: strażnik (8 kroków), po 2
3. Group 5: układ i kody (9 kroków), po 4
4. Równolegle:
   - Group 6: etapy (8 kroków), po 5
   - Group 10: promocja (9 kroków), po 4 i 5
5. Group 7: `--resume` (7 kroków), po 6
6. Równolegle:
   - Group 8: `fullfsync` w buildzie (4 kroki), po 3 i 7
   - Group 9: nadzorca (9 kroków), po 1, 4 i 7
   - Group 11: sprzątanie (6 kroków), po 4 i 10
   - Group 12: historia (5 kroków), po 7 i 10
7. Group 13: dokumentacja (6 kroków), po 3, 8, 9, 10, 11 i 12
8. Group 14: pełny zestaw (5 kroków), po wszystkich

## Standards Compliance

Standardy z `.maister/docs/standards/` i `AGENTS.md` repo:
- Treści po polsku, zwięźle. W kodzie, testach i dokumentach nie ma UUID ani ścieżek domowych.
- Python stdlib, `unittest`, styl funkcyjny, `GeneratorError(message, code)`.
- `docs/generator/cli.md`: JSON na stdout, błędy na stderr, kody jako kontrakt.
- Skład słownika, polityka i piny bez zmian. Prawdziwy build słownika nie jest uruchamiany.
- Bez CI. Gdyby kiedyś powstał workflow, to tylko na runnerze self-hosted.
- Implementerzy nie commitują. Commituje orkiestrator.

## Notes

- Test-driven: każda grupa zaczyna od 2–8 testów.
- Po każdej grupie uruchamia się tylko jej nowe testy. Wyjątki: grupa 5 uruchamia też `test_run.py`, a grupa 6 trzy moduły regresji.
- Testy są hermetyczne: `tempfile` i podstawione `ismount`, `stat`, `statvfs`, `fcntl`, `subprocess`. Bez USB.
- Każda zmiana w `literaki_slownik/` zmienia `tree_sha256`. Para A/B buduje się z jednego commitu (poza zakresem zadania).
- Wykonane kroki odhacza się tutaj i w `implementation-plan.html`.
