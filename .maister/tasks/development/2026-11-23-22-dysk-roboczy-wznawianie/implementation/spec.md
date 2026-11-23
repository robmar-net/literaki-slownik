# Specyfikacja: build na T7 z wznawianiem (#22)

## TL;DR
Para A/B buduje się na T7: każdy przebieg to katalog na T7 i symlink `data/work/<przebieg>`. Brak dysku daje kod 75, a nadzorca sam robi `build --resume`.
Wznowienie zaczyna od pierwszego niegotowego etapu, w raportach od pierwszego raportu bez znacznika. Wynik ma być taki sam jak ze świeżego buildu (te same `canonical-index`, `logical-content`, `lists/*.txt`).
Po `verify` skrypt `promote_run.py` kopiuje A na dysk wewnętrzny (sha256 i tryb), podmienia symlink atomowo, kasuje B i kopię A na T7. `export` odmawia przebiegu na T7.
`clean_work.py` domyślnie tylko wypisuje. Stare wydania kasuje tylko z listą zaakceptowaną przez właściciela; „bieżące na serwerze” ustala sam z `NOTICE` serwera.
Kod: stdlib, testy `unittest` bez USB i bez prawdziwego buildu słownika. Jednorazowy pomiar `fullfsync` na T7 jest częścią wdrożenia.

## Key Decisions
- Wznowienie od pierwszego etapu, który nie jest `complete`; każdy dalszy etap liczy się od nowa. Tylko tak wynik nie zależy od tego, które etapy były `pending`.
- Ponowne wykonanie etapu przed `reports` kasuje `reports/.done/`, bo znaczniki wiążą się z bazą sprzed resetu.
- `new_candidates`, `new_analyses`, `new_decisions` zostają w wartościach funkcji (testy idempotencji), ale build usuwa je z raportów kanonicznych. To najmniejsza zmiana, która odcina K8 od historii.
- „Wolumen roboczy” = punkt montowania ścieżki ma znacznik `.literaki-work-volume`. Jawny `--work-root` zawsze wymaga znacznika. Bez `--work-root` ścieżka na punkcie montowania repo to dysk wewnętrzny (testy i stare przebiegi działają bez zmian).
- `--resume` najpierw sprawdza dysk (symlink, cel, G1 → 75), dopiero potem czyta manifest. Manifest leży na T7, więc odwrotna kolejność dałaby 4 zamiast 75.
- Wznowienie z niegotowym `preflight` zaczyna przebieg od nowa w tym samym katalogu (kasuje bazę). Dzięki temu nadzorca nie staje po zniknięciu dysku w pierwszych sekundach.
- Promocja nie zmienia manifestu przebiegu, więc pieczęć `verify` zostaje ważna. Ślad promocji to `promotion.json` w katalogu przebiegu. Leży poza pieczęcią i poza `canonical-index`, a test to potwierdza.
- Promocja jest „automatyczna” jako jedno polecenie po `verify` (bez pytania o B). `verify` sam niczego nie kopiuje i zostaje komendą tylko do odbioru.
- Podmiana symlinku na katalog jednym `renamex_np(RENAME_SWAP)`. `export.py` już woła `renamex_np` przez `ctypes`.
- „Bieżące na serwerze” ustala sam skrypt (decyzja właściciela). Wydanie jest bieżące, gdy sha256 jego `release-manifest.json` albo któregokolwiek pliku z jego `files` występuje w `origin/main:NOTICE` repo serwera. `NOTICE` podaje głównie hashe list. Brak repo albo `NOTICE` → wszystkie wydania potrzebne.
- Próg miejsca to 50 GB na proces przy starcie i 100 GB na wolumenie przy starcie pary (A+B na jednym T7).
- Tryb `fullfsync` wybiera jednorazowy pomiar na T7 w trakcie wdrożenia, według reguły ≤5% → 4B, inaczej 4C. Wynik trafia do ADR-020 i do stałej w kodzie.
- Lokalne ADR-001..008 trafiają do repo jako ADR-014..021. ADR-014 opisuje nowy układ.

## Open Questions / Risks
- Odbudowa tabel importu może w teorii zmienić `rowid`. Ryzyko jest niskie: `logical-content` łączy po kluczach trwałych, a SQLite po DELETE wszystkich wierszy numeruje od 1. Plan awaryjny (nowy plik bazy od `preflight`) zostaje w ADR-016.
- Promocja kopiuje ~22 GB na dysk wewnętrzny. Miejsce jest sprawdzane (kod 78).
- Po skasowaniu B ponowny `verify` A (np. nowy przegląd K7) wymaga nowej pary.
- Zniknięcie T7 przerywa A i B naraz. Wspólny błąd wznowienia wykryje tylko test z R6, para go nie wykryje.
- „Bieżące na serwerze” zależy od lokalnego `origin/main` serwera (bez `fetch`). Nieaktualny checkout może nie znać nowszego wydania. Chroni wtedy reguła „ostatnie w rodzinie” i osobna zgoda właściciela.
- Restart nadzorcy po restarcie maszyny jest ręczny. LaunchAgent jest poza zakresem.

## Cel
Build pary trwa ~13 h i nie może przepadać przez kilkusekundowe zniknięcie T7 ani przez restart. Strata ma wynosić najwyżej bieżący etap albo bieżący raport, bez zmiany wyniku i kontraktu K1–K10.

## Historie użytkownika
- Jako operator uruchamiam `build_pair.sh <nazwa>` i rano mam parę gotową do przeglądu, nawet gdy T7 zniknął w nocy.
- Jako operator po restarcie maszyny uruchamiam nadzorcę z `--run-dir` i tracę tylko bieżący etap.
- Jako właściciel mam jedną kopię zachowanego wydania na dysku wewnętrznym (backup), a na T7 tylko rzeczy odtwarzalne.
- Jako właściciel decyduję, które stare wydania znikają. Skrypt nigdy nie kasuje ich sam.

## Wymagania i kryteria akceptacji

Każdy test jest hermetyczny: `tempfile`, podstawione `os.path.ismount`, `os.stat`/`os.statvfs`, `fcntl.fcntl`, `subprocess`. Fikstury pochodzą z `tests/helpers.py` i `tests/release_helpers.py`.

| ID | Wymaganie | Kryteria akceptacji | Test |
|---|---|---|---|
| R1 | Układ: `data/work` zostaje katalogiem; nowy przebieg = katalog `<korzeń T7>/<nazwa>` + symlink `data/work/<nazwa>` | `build --work-root W`: strażnik na W (znacznik wymagany, inaczej 76), `mkdir W/<nazwa>` (`parents=False`), manifest i `reports/` w środku, na końcu symlink. Jeśli `W/<nazwa>` istnieje bez symlinku, nie ma w nim `build.sqlite`, a jego manifest ma wszystkie etapy `pending`, to jest resztka nieudanego startu: build ją kasuje i zaczyna od nowa. Inaczej 4. Bez T7 nic nie powstaje na dysku systemowym. `.gitignore`: dodać `/logs` (wpis `/data/work/` już obejmuje symlinki w środku) | podstawiony brak montowania → 75 i brak nowych plików w `data/work`; W bez znacznika na dysku repo → 76; resztka startu → build przechodzi; `git check-ignore` w repo tymczasowym dla symlinku `data/work/x` i `logs/x` |
| R2 | Strażnik wolumenu G1/G2/G3 + miejsce; `scripts/init_work_volume.py` | Tabela „Strażnik” niżej. `init_work_volume.py <korzeń>` zapisuje znacznik (UUID z `diskutil info -plist`, losowy `marker_id`). Odmawia, gdy znacznik istnieje albo korzeń leży na dysku repo | brak montowania → 75; inny `marker_id` → 76; zmiana `st_dev` → 75; wolne <50 GB → 78; ścieżka wewnętrzna bez znacznika i bez `--work-root` → przepuszcza; init drugi raz → odmowa |
| R3 | Trwały zapis: `write_json`, nowy `write_bytes`; `write_lists` przez `write_bytes` | Kolejność: tmp w tym samym katalogu → zapis → `F_FULLFSYNC` (gdy `fcntl` go nie ma albo zwraca błąd: `os.fsync`) → G3 → `os.replace` → fsync katalogu. Błąd sprzątania tmp w `finally` nie zasłania pierwotnego błędu | mock wywołań: kolejność; fallback na `fsync`; przerwanie przed `replace` zostawia stary plik; `unlink` rzucający OSError nie zmienia typu pierwotnego wyjątku |
| R4 | Klasyfikator błędów | Tabela „Kody wyjścia”. `connect`: rollback i `close` w `try`, ich błąd jest pomijany. Nieudany zapis `failed` nie zmienia kodu | wstrzyknięty `sqlite3.OperationalError('disk I/O error')`: strażnik upadły → 75, zdrowy → 4; `SQLITE_FULL`/`ENOSPC` → 78; `SQLITE_CORRUPT` → 77; CLI `build` zwraca te kody |
| R5 | `build --resume --manifest M --run-dir R` | Kolejność w sekcji „Wznowienie”: najpierw dysk (75), potem manifest (4), readiness (5), G2 (76), miejsce (78), kod (4), wejścia (3), `quick_check` (77). Potem `running` → `failed`, otwarta próba → `interrupted`, reset i etapy | po jednej odmowie na każdą kontrolę; wiszący symlink → 75, nie 4; `running` po `os._exit` w procesie potomnym kończy się `failed`; podwójne przerwanie i drugie `--resume` dają wynik świeżego |
| R6 | „Wznowiony = świeży” (cztery poprawki niżej) | Przerwanie na każdej granicy etapu, w środku `import_kwjp`, `constructions`, `links` i między każdą parą raportów. Po `--resume` pliki `reports/canonical-index.json`, `reports/logical-content.json`, `lists/*.txt` są bajtowo równe świeżemu buildowi. Para wznowiony + świeży przechodzi K8 | harness parametryzowany punktem przerwania; para → `verify` VERIFIED (fikstura `complete_pair`) |
| R7 | Znaczniki raportów `reports/.done/<raport>.json` | Pola: `sha256`, `bytes`, `tree_sha256`, `manifest_sha256` (wejść). Zapis: raport, potem znacznik. Raport jest pomijany tylko wtedy, gdy wszystkie pola zgadzają się z plikiem i bieżącym kodem. Przy pominięciu `unresolved` czytany z `reports/unresolved.json`. Świeży build też pisze znaczniki. `canonical_index` ich nie obejmuje | zły hash znacznika → raport liczony od nowa; `unresolved` z pliku daje te same bajty raportów zależnych; `.done` poza `canonical-index` |
| R8 | SQLite, pomiar i wybór trybu | `connect` dla bazy zapisywalnej: `journal_mode=DELETE`, `synchronous=FULL`. Build: tryb `fullfsync` według stałej (sekcja „Trwałość”). `scripts/measure_fullfsync.py` pisze JSON. Wdrożenie obejmuje jeden pomiar na T7, wpis w ADR-020 i ustawienie stałej | PRAGMA odczytane w trakcie etapu i na granicy mają oczekiwane wartości w obu trybach; skrypt na `tmp` daje JSON z obydwoma wariantami i `overhead_pct` przy `--reference-run` |
| R9 | Nadzorca `scripts/build_supervised.py` | Sekcja „Nadzorca” | podstawiony build i zegar (bez czekania): 75,75,0 → 0; 75×4 → 75 po 3 wznowieniach; 75 przed powstaniem przebiegu → świeży build, nie `--resume`; 4 → stop; 77 → stop; G1 bez G2 → 76; wolumen pod inną ścieżką → 76 od razu; czekanie > limitu → 75; SIGINT → 130 bez wznowienia |
| R10 | Promocja `scripts/promote_run.py` i odmowa `export` | Sekcja „Promocja” | A nie VERIFIED → 5; zmiana pliku na T7 po verify → 5; różny sha256/tryb kopii → 4 i nic nie skasowane; zniknięcie T7 w trakcie kopii → 75, staging zostaje; przerwanie w każdym stanie i ponowne wywołanie kończy promocję; ponowne wywołanie po `export` kasuje kopię T7; `export` symlinku/ścieżki na T7 → 5; `export` po promocji przechodzi `changes_since_verify` mimo `promotion.json` |
| R11 | Sprzątanie `scripts/clean_work.py` | Sekcja „Sprzątanie” | drzewo z każdą klasą: lista bez zmian na dysku; `--apply` kasuje tylko klasy T7; katalog `VERIFIED`/`FROZEN` bez symlinku nigdy nie jest kasowany; katalog z rekordu promocji też nie; wydanie przypięte / bieżące / ostatnie w rodzinie nigdy nie jest kandydatem; fikstura `NOTICE` w prawdziwym kształcie (hashe list w osobnych liniach) w tymczasowym repo git: wydanie z hashem pliku listy w `NOTICE` → potrzebne; brak repo lub `NOTICE` → zero kandydatów i komunikat; `--delete-releases` z nazwą potrzebną → odmowa całości |
| R12 | Historia prób w `verify` i `export` | `verify` (JSON i tekst) pokazuje skrót `build_history`. `export` kopiuje go do `release-manifest.json` → `source_run.build_history`. Zmiana `build_attempts` po verify → export odmawia (5) | wznowiony przebieg: skrót w obu miejscach; ręczna zmiana historii po verify → kod 5 |
| R13 | Dokumentacja | `docs/generator/cli.md`: `--resume`, `--work-root`, kody 75–78, nowe skrypty, nowe kody `resume_reports.py`. Runbook: przebieg pracy z T7. ADR-014..021 w `docs/adr/` (mapa niżej). Wpisy w `.maister/docs/INDEX.md` | grep w testach dokumentacji: kody 75–78 i nazwy skryptów obecne w `cli.md` |

### ADR w repo (z lokalnego rejestru decyzji)

| Repo | Lokalny | Treść |
|---|---|---|
| ADR-014 | ADR-001 (zmieniony) | układ: `data/work` wewnątrz, symlink per przebieg na T7, granica odtwarzalności na `verify`, promocja (D1, D3), `export` tylko wewnątrz, `clean_work.py` (D2) |
| ADR-015 | ADR-002 | strażnik G1/G2/G3, znacznik, UUID tylko na wolumenie, progi miejsca |
| ADR-016 | ADR-003 | `build --resume` od pierwszego niegotowego etapu, kolejność kontroli, reset tabel, plan awaryjny |
| ADR-017 | ADR-004 | znaczniki `reports/.done/`, `unresolved` z pliku |
| ADR-018 | ADR-005 | kody 75–78 |
| ADR-019 | ADR-006 | nadzorca wznawia tylko po 75 |
| ADR-020 | ADR-007 | `fullfsync` 4B/4C: wynik pomiaru na T7 i wybór; `F_FULLFSYNC`, `quick_check` |
| ADR-021 | ADR-008 | `build_attempts`/`resume` na poziomie głównym, pod pieczęcią, poza K8; `explain` tylko status; test „wznowiony = świeży” |

## Strażnik wolumenu

Nowy moduł `literaki_slownik/volume.py`. Punkt montowania to najbliższy przodek ścieżki po `realpath`, dla którego `os.path.ismount` jest prawdą.

| Sytuacja | Świeży build z `--work-root W` | Świeży build bez `--work-root` | `--resume`, nadzorca (oczekiwany `marker_id`) |
|---|---|---|---|
| W albo cel symlinku przebiegu nie istnieje | 75 | — | 75 |
| punkt montowania = punkt montowania repo | 76 (W bez znacznika na dysku systemowym, wbrew R1) | przepuszcza (`work_volume` = null) | 75, gdy przebieg to symlink (wolumen niezamontowany, np. pusty katalog w `/Volumes`); przepuszcza, gdy przebieg wewnętrzny i manifest ma `work_volume` null |
| inny punkt montowania, brak znacznika | 76 | 76 | 76 |
| znacznik jest, `marker_id` inny | — (przyjmuje znaleziony) | — | 76 |
| znacznik zgodny | OK | OK | OK |
| `st_dev` katalogu przebiegu inny niż zapamiętany w procesie (G3) | 75 | 75 | 75 |
| wolne miejsce < 50 GB (start buildu lub wznowienia, tylko wolumen roboczy) | 78 | — | 78 |

- G3 jest sprawdzany przed każdym etapem i przed `os.replace` w zapisie trwałym, gdy cel leży w aktywnym przebiegu procesu.
- `build_pair.sh` przed startem wymaga ≥ 100 GB wolnego na W (dwie strony po ~22 GB plus journal i zapas). Przy braku kończy kodem 78.
- Znacznik `.literaki-work-volume` w korzeniu wolumenu zawiera UUID z `diskutil` i `marker_id`. Do repo i manifestu trafia tylko `marker_id`.
- Wolumen pod inną ścieżką: gdy G1 nie przechodzi, `volume.find_by_marker(marker_id)` przegląda punkty montowania w `/Volumes`. Jeśli znajdzie znacznik o tym `marker_id` pod inną ścieżką (np. `<nazwa> 1`), nadzorca kończy od razu kodem 76 i podaje ścieżkę. Symlinków nie przepina sam. SQLite tego nie wymaga, bo hot journal leży obok bazy.

## Kody wyjścia

Kontrakt dla `build`, `build --resume`, nadzorcy i nowych skryptów.

| Kod | Znaczenie | Nadzorca |
|---|---|---|
| 0 | proces skończył się bez błędu (etapy mogą być `pending`, jak dziś) | koniec |
| 2 | błąd argumentów | stop |
| 3 | błąd wejść: manifest, hash, także `inputs.manifest_sha256` inny niż przy buildzie | stop |
| 4 | błąd buildu: dane, kod, inna tożsamość kodu przy `--resume`, brak przebiegu albo nieczytelny manifest przy zdrowym dysku, inny `sqlite3.Error`/`OSError`, błąd kopii przy promocji | stop |
| 5 | przebieg `VERIFIED`/`FROZEN`; promocja lub export odmawia (pieczęć, wolumen) | stop |
| 75 | dysk roboczy zniknął: po błędzie I/O strażnik nie przechodzi (G1/G3) albo brak dysku przy starcie `--resume`/promocji; nadzorca: wyczerpany limit albo czas | czekaj i wznów, maks. 3 wznowienia |
| 76 | zły wolumen: inny znacznik, zewnętrzny wolumen bez znacznika, `--work-root` bez znacznika, wolumen zamontowany pod inną ścieżką | stop |
| 77 | `quick_check` ≠ `ok` albo `SQLITE_CORRUPT`/`SQLITE_NOTADB` | stop, decyzja człowieka |
| 78 | brak miejsca: `SQLITE_FULL`, `ENOSPC`, `EDQUOT`, progi startu, promocja bez miejsca | stop |
| 130 | SIGINT | stop |

Klasyfikacja `sqlite3.Error`/`OSError` w `build`: rollback (błąd pomijany) → zamknięcie → strażnik. Gdy strażnik nie przechodzi, kod to 75 albo 76. Gdy przechodzi: `SQLITE_FULL`/`ENOSPC`/`EDQUOT` → 78, `SQLITE_CORRUPT`/`SQLITE_NOTADB` → 77, reszta → 4. `GeneratorError` i `KeyboardInterrupt` działają jak dziś. `cli.py` łapie dodatkowo `sqlite3.Error` → 4 (dziś kończy się tracebackiem z kodem 1).

## Manifest przebiegu: nowe pola

| Pole (poziom główny) | Kształt | Kto pisze |
|---|---|---|
| `work_volume` | `{"marker_id": "<losowy>"}` albo `null` (dysk wewnętrzny) | `create_run` |
| `build_attempts` | lista `{"attempt": n, "started", "ended" \| null, "first_stage", "last_stage", "outcome", "exit_code"}`; `outcome` ∈ `complete`, `incomplete` (są etapy `pending`), `interrupted`, `failed` | `create_run` i `--resume` otwierają, koniec procesu zamyka; gdy zamknięcie się nie uda, `--resume` ustawia `interrupted` |
| `resume` | `{"resumed": bool, "count": n}` | `create_run` (`false`, 0), `--resume` (+1) |

- Bez komunikatów błędów i ścieżek. Świeże buildy A i B mają ten sam kształt pól.
- `set_stage` dalej zastępuje słownik etapu. Historia nie leży w `stages`.
- Pieczęć: `SEAL_EXCLUDED` się nie zmienia, więc `manifest_core_sha256` obejmuje nowe pola. Zmiana po verify blokuje export (5).
- K8 bez zmian: porównuje `tree_sha256`, `canonical-index`, `logical-content`, a nie manifest.
- `explain` zwraca z `stages` tylko `{"<etap>": "<status>"}`, więc K7 nie zależy od historii ani od znaczników czasu. Żaden obecny test nie czyta `stages` z wyniku `explain`.
- Skrót `build_history` (verify, export): `{"resumed", "attempts", "outcomes": [...], "exit_codes": [...], "resumed_from": [etapy]}`.

## Wznowienie

### Kolejność kontroli `--resume`
1. `os.path.lexists(R)`: brak → 4 („brak przebiegu”).
2. `R` jest symlinkiem, a jego cel nie istnieje → 75.
3. G1: punkt montowania celu = punkt montowania repo przy przebiegu-symlinku → 75.
4. Odczyt `manifest.json`: brak albo nieczytelny → najpierw ponowny G1 (75, gdy dysk zniknął), inaczej 4.
5. `readiness` `VERIFIED`/`FROZEN` → 5.
6. G2: `marker_id` znacznika ≠ `work_volume.marker_id` (albo manifest ma null, a przebieg leży na wolumenie roboczym) → 76.
7. Miejsce ≥ 50 GB na wolumenie roboczym → inaczej 78.
8. `tree_sha256` równy i `git_dirty` false → inaczej 4.
9. `inspect_sources(M)`: `manifest_sha256` równy `inputs.manifest_sha256` → inaczej 3.
10. `preflight` niegotowy (albo brak kompletu `source_artifact`): kasowanie `build.sqlite`, `-journal`, zawartości `reports/` i `lists/`, potem przebieg od `preflight` w tym samym katalogu.
11. Otwarcie bazy, `PRAGMA quick_check` = `ok` → inaczej 77.
12. Każdy `running` zmienia się w `failed`, otwarta próba dostaje `interrupted`, dopisuje się nowa próba, potem reset i etapy.

### Reset

Wznowienie zaczyna od pierwszego etapu z `STAGES`, który nie jest `complete`. Ten etap i wszystkie dalsze liczą się od nowa.

| Pierwszy niegotowy etap | Reset przed startem (w tej kolejności) |
|---|---|
| `preflight` | krok 10 wyżej |
| `import_sgjp` | `DROP TABLE IF EXISTS evidence_candidate`; `DROP TABLE IF EXISTS evidence_link` (osobne polecenia, dziecko przed rodzicem); DELETE: `variant_decision`, `decision_payload`, `analysis`, `derivation_component`, `derivation_candidate`, `interpretation`, `lexeme`, `surface_form`, `sgjp_record`, `corpus_evidence`; wiersz `source_artifact` `own-semantic-use-review-v1` |
| `import_kwjp` | oba DROP jak wyżej; DELETE tabel decisions/constructions w tej samej kolejności, potem `corpus_evidence`; wiersz przeglądu użyć |
| `constructions`, `decisions` | oba DROP; bez DELETE: `constructions` ma `insert or ignore` po kluczu sha256 treści, a `decisions` ma `insert or ignore` z porównaniem wierszy |
| `links` | oba DROP (indeksy znikają razem z tabelą) |
| `reports` | znaczniki `.done` według R7 |

- Gdy w tej próbie wykonał się jakikolwiek etap przed `reports`, `reports/.done/` jest kasowane przed `reports`.
- Reset idzie w jednej transakcji. Commit z pełnym flushem jest przed `set_stage(running)`.
- `build()` dzieli się na funkcje etapów według `STAGES`. Świeży build i `--resume` idą tą samą pętlą.

### Cztery poprawki „wznowiony = świeży”
1. `construction-candidates.json` bez `new_candidates`, `decisions.json` bez `new_analyses`/`new_decisions`. Build usuwa te pola przed zapisem, a funkcje `materialize_*` zwracają je dalej.
2. `import-counts.json` liczony z bazy po etapach importu (te same metryki co dziś), a nie ze słownika w pamięci.
3. `inventory.json`, `qualifier-conditions.json` i `import-counts.json` zapisywane na końcu `import_kwjp`, przed `set_stage(complete)`.
4. `links`: `set_stage(links, running)` na starcie i DROP przed `create_links`. Na końcu `complete`, gdy `stage_completion.complete`. W przeciwnym razie `pending` z `reason` (dziś etap zostawał bez zmiany statusu).

Dodatkowo `preflight` dostaje `complete` dopiero po utworzeniu bazy i commicie `source_artifact`, a `write_lists` zapisuje atomowo.

## Trwałość i `fullfsync`

| Tryb (stała w `database.py`) | Działanie | Kiedy |
|---|---|---|
| `build` (4B) | `PRAGMA fullfsync=ON` przez cały build | pomiar ≤ 5% |
| `stage_boundaries` (4C) | `fullfsync=OFF` w etapie; na końcu etapu, po ostatnim commicie, `F_FULLFSYNC` na pliku `build.sqlite`, potem pliki etapu, potem manifest | pomiar > 5% |

- Pomiar w trakcie wdrożenia (T7 jest zamontowany): `scripts/measure_fullfsync.py --dir <korzeń T7>/.measure-<stempel> --reference-run data/work/<ostatni zamrożony przebieg> [--quick-check <jego build.sqlite>]`. Tylko tymczasowa baza testowa na T7, bez buildu słownika. Katalog pomiaru jest kasowany na końcu.
- Reguła: `overhead_pct = (czas commitu ON − OFF) × liczba commitów buildu / 46 800 s × 100`. Liczbę commitów skrypt liczy z `reports/import-counts.json` i `reports/decisions.json` przebiegu referencyjnego (rekordy / 10 000, w górę) i dolicza commity etapów.
- ADR-020 zapisuje liczby (bez ścieżek i UUID), wybór i czas `quick_check`. Stała w kodzie dostaje wybraną wartość. Do czasu pomiaru domyślna jest `build`.
- Kolejność zawsze: dane etapu trwale → pliki etapu → manifest `complete`.
- Nigdy WAL, `journal_mode=OFF/MEMORY` ani `synchronous<FULL`.

## Nadzorca

`scripts/build_supervised.py --manifest M --run-dir R [--work-root W] [--max-resumes 3] [--wait-minutes 30] [--poll-seconds 5]`

- Wybór polecenia przed każdym procesem: `os.path.lexists(R)` i manifest czytelny → `build --resume`; `R` nie istnieje → `build --work-root W` (świeży, także po 75 sprzed `create_run`); symlink jest, a dysku brak → czekanie.
- `marker_id` nadzorca zna z manifestu albo, przy świeżym starcie, ze znacznika `W`.
- Po 75: co `poll` sekund G1+G2. Gdy OK → nowy proces. G1 bez zgodnego G2 → 76 od razu. Wolumen o tym `marker_id` pod inną ścieżką → 76 od razu, z tą ścieżką w logu. Po `wait` minutach → 75. Każde ponowienie po 75 liczy się do limitu 3.
- Inne kody kończą pracę z tym kodem. SIGINT przekazuje procesowi potomnemu i kończy 130. SIGTERM i SIGHUP też przekazuje i kończy kodem procesu potomnego, bez wznowienia (`running` naprawi następne `--resume`).
- Nie dotyka plików przebiegu (`-journal` zostaje).
- Logi leżą na dysku wewnętrznym: `logs/<nazwa>.out.json` (stdout każdej próby, dopisywany), `logs/<nazwa>.err`, `logs/<nazwa>.supervisor.log` (jedna linia JSON na zdarzenie). Przez cały czas pracy nadzorca trzyma blokadę `flock` na `logs/<nazwa>.lock`.
- Testowalność: logika w funkcji z wstrzykiwanym uruchamianiem buildu, `sleep` i zegarem. CLI tylko ją opakowuje.
- `scripts/build_pair.sh <nazwa>`:
  - wymaga `LITERAKI_WORK_ROOT`, inaczej kończy kodem 2;
  - sprawdza czysty kod jak dziś i ≥ 100 GB na W (inaczej 78);
  - robi `mkdir -p logs` i uruchamia dwóch nadzorców pod `caffeinate -dimsu`;
  - ścieżki `data/work/<nazwa>-<stempel>-<a|b>` się nie zmieniają.
- `scripts/resume_reports.py` staje się nakładką: te same kontrole co dziś (`:44-52`), potem `build --resume`. Kod wyjścia przekazuje dalej (dziś 0/2, odtąd kontrakt z tabeli; opis w `cli.md`).

## Promocja

`scripts/promote_run.py --run-dir data/work/<A> --peer data/work/<B>` uruchamiane od razu po udanym `verify` (runbook: `verify … && promote_run.py …`). Przez cały czas trzyma blokadę `logs/<A>.promote.lock`. Staging ma stałą nazwę `data/work/.<A>.promote`.

Rekord `promotion.json` w katalogu przebiegu (tylko w kopii wewnętrznej) ma pola: `t7_path` (realpath kopii A na T7), `peer_link`, `peer_path` (realpath B), `marker_id`, `started`, `completed` (null albo czas). Nie jest częścią manifestu ani `canonical-index`. `changes_since_verify` go nie czyta, bo sprawdza tylko rdzeń manifestu, wejścia, pliki kanoniczne, `build.sqlite` i pliki próby verify. Test potwierdza, że export przechodzi.

| Stan na dysku | Akcja | Kod przy błędzie |
|---|---|---|
| S0: `data/work/<A>` to symlink, brak stagingu | kontrole: A `VERIFIED` (5); `changes_since_verify(A)` puste (5); cel na wolumenie roboczym ze zgodnym `marker_id` (75/76); wolne wewnątrz ≥ rozmiar A × 1,1 (78); dalej jak S1 | 5, 75, 76, 78 |
| S1: symlink + staging (pełny albo częściowy) | kasowanie stagingu i kopia od zera: tylko zwykłe pliki i katalogi (symlink albo plik specjalny w A → 4); każdy plik zapisem trwałym, z tym samym trybem (`S_IMODE`) i `mtime`; potem porównanie sha256 i trybu każdego pliku z T7; zapis `promotion.json`; `changes_since_verify(staging)` puste | różnica → 4; błąd I/O → strażnik: 75/76, inaczej 4; staging zostaje |
| S1 → S2 | `renamex_np(staging, data/work/<A>, RENAME_SWAP)`; po zamianie staging to dawny symlink, więc `unlink`; fsync `data/work` | błąd zamiany → 4, nic się nie zmienia |
| S2/S3: `data/work/<A>` to katalog z `promotion.json`, `completed` = null | A może być `VERIFIED` albo `FROZEN` (dozwolone po exporcie); strażnik dla `t7_path` (brak dysku → 75); kasowanie B, gdy `peer_link` dalej wskazuje `peer_path`, B jest `INCOMPLETE`, a sha256 jego `reports/canonical-index.json` równa się `canonical_index_sha256` z pieczęci A (inaczej B zostaje, wpis w logu); kasowanie kopii A pod `t7_path` po sprawdzeniu, że to nie jest katalog wewnętrzny; `completed` ustawione | 75, 76 |
| S4: `completed` ustawione | nic, kod 0 | — |

- Zdarzenia trafiają do `logs/<A>.promote.log`.
- Manifest A się nie zmienia.
- Kody: 0, 2, 4, 5, 75, 76, 78.
- `export` (`export.py`) odmawia kodem 5, gdy `run_dir` jest symlinkiem albo leży na wolumenie roboczym: „przebieg na T7; najpierw promote_run.py”.

## Sprzątanie

`scripts/clean_work.py [--work-root W] [--apply] [--server-repo ŚCIEŻKA] [--server-current NAZWA]... [--delete-releases PLIK]`

Domyślnie tylko lista (JSON na stdout: wpis, klasa, rozmiar, powód). Bez `--apply` nic nie jest kasowane.

Klasy według pierwszeństwa. Wygrywa pierwsza pasująca.

| # | Klasa | Gdzie | `--apply` |
|---|---|---|---|
| 1 | manifest `VERIFIED`/`FROZEN` (z symlinkiem albo bez) | T7 | nigdy (czeka na promocję) |
| 2 | promocja w toku: trzymana `logs/<x>.promote.lock`, staging `.<x>.promote`, albo ścieżka jest `t7_path`/`peer_path` w `promotion.json` z `completed` = null | T7 | nigdy |
| 3 | przebieg w toku: trzymana `logs/<x>.lock` albo manifest lub katalog zmieniany < 24 h | T7 | nigdy |
| 4 | nieznana zawartość: brak manifestu i nie jest resztką startu z R1 | T7 | nigdy (tylko lista) |
| 5 | osierocony: brak symlinku w `data/work`, manifest `INCOMPLETE` albo resztka startu, ≥ 24 h | T7 | kasuje |
| 6 | nieukończony: `INCOMPLETE`, symlink jest, ≥ 24 h | T7 (+ symlink) | kasuje |
| 7 | promowany przebieg, wydania, dowody, przeglądy, pomiary, przebiegi eksperymentalne, staging, logi | dysk wewnętrzny | nigdy (tylko lista) |
| 8 | stare wydanie (kandydat) | dysk wewnętrzny | tylko z `--delete-releases` |

- Wydanie to katalog z `release-manifest.json`, szukany w `data/work` do głębokości 2 (np. `tematy-wydanie-…/<pakiet>/`). Razem z nim idzie jego przebieg `FROZEN` (`source_run.run_name`), jeśli ten nie jest potrzebny innemu wydaniu.
- Rodzina to nazwa do pierwszego `-v<cyfry>`. Wersja to krotka liczb po `v`, np. `v1r2` → (1, 2). Wpis, którego nie da się rozpoznać, dostaje klasę 7.
- Wydanie potrzebne (nigdy kandydat), gdy spełnia choć jedno:
  - ścieżka wydania albo jego przebiegu (`run_dir`, `release_dir`, `path` i katalog nadrzędny pliku) występuje w którymkolwiek `config/generator/*-sources.json`;
  - jest bieżące na serwerze: sha256 jego `release-manifest.json` albo któregokolwiek pliku z jego `files` (listy `.txt`, `.txt.gz`) jest wśród 64-znakowych hashy w `git -C <server-repo> show origin/main:NOTICE`. `--server-repo` domyślnie `../server` (repo robmar-net/Literaki-server); tylko odczyt, bez `fetch`, bez sieci i sekretów. Katalog `lexicons/` (`pl-*-RRRRMMDD.dawg`) trafia do listy tylko jako kontekst;
  - brak checkoutu serwera, `origin/main` albo `NOTICE`, lub `NOTICE` bez żadnego hasha → wszystkie wydania potrzebne i zero kandydatów; wynik mówi to wprost (`server_notice: unavailable` i powód);
  - nazwa albo `package_id` jest na liście `--server-current` (ręczny dodatek do `NOTICE`, nie zamiennik);
  - jest ostatnie w rodzinie (najwyższa wersja; przy remisie najpóźniejsze `frozen_at`).
- `--delete-releases PLIK` to plik z dokładnymi nazwami zaakceptowanymi przez właściciela. Wymaga `--apply`. Nazwa spoza kandydatów → odmowa całości (4), nic nie skasowane. Przed kasowaniem `chmod u+w` (pliki read-only po `export`).
- Kody: 0, 2 (argumenty), 4 (odmowa).

## Ponowne użycie

### Istniejący kod
- `literaki_slownik/canonical.py` `write_json` jest bazą trwałego zapisu; `write_bytes` dzieli z nim jedną funkcję.
- `literaki_slownik/run.py` `STAGES`, `code_identity`, `set_stage` dają pętlę etapów i kontrolę tożsamości przy `--resume`. Blokada po verify (`:60`) już jest.
- `scripts/resume_reports.py:44-52`: kontrole tożsamości kodu i wejść przechodzą do wspólnej walidacji `--resume`.
- `literaki_slownik/export.py` `changes_since_verify` sprawdza pieczęć w promocji (na A i na stagingu przed zamianą).
- `literaki_slownik/export.py` `rename_noreplace` (`renamex_np` przez `ctypes`), `READ_ONLY` i wzorzec stagingu to wzór dla `RENAME_SWAP` w promocji.
- `literaki_slownik/reports.py` `canonical_index` ma jawną listę, więc `.done/` i `promotion.json` nie wchodzą do K8.
- `literaki_slownik/verify.py` `manifest_core_sha256` i `SEAL_EXCLUDED` zostają bez zmian, a pieczęć obejmuje nowe pola.
- `constructions.py`/`decisions.py` `insert or ignore` (klucz z treści, w decisions z porównaniem wierszy) daje idempotencję bez zmian.
- Testy:
  - `tests/test_lifecycle.py:50-84` (przerwanie i `running`);
  - `tests/test_build.py:151,201` (awaria po partii);
  - `tests/helpers.py` `fixture_manifest`;
  - `tests/release_helpers.py` `complete_pair`/`complete_run`; `complete_run` nadpisuje `stages`, ale nie rusza pól głównych.

### Nowe elementy
- `literaki_slownik/volume.py`: strażnik, klasyfikacja wolumenu i `find_by_marker`. Dziś nie ma nic podobnego, a potrzebują go `build`, `export`, nadzorca, promocja i sprzątanie.
- `scripts/init_work_volume.py`: jednorazowe założenie znacznika.
- `scripts/build_supervised.py`: pętla czekania i wznawiania. W `build_pair.sh` (sh) byłaby nietestowalna.
- `scripts/measure_fullfsync.py`: dane do wyboru 4B/4C.
- `scripts/promote_run.py`, `scripts/clean_work.py`: nowe operacje na danych wymagane przez D2/D3.

## Podejście techniczne
- Kolejność grup:
  1. `.gitignore`, trwały zapis, skrypt pomiaru i pomiar na T7 (niezależne od siebie);
  2. strażnik, klasyfikator i kody;
  3. podział `build()`, cztery poprawki, `--resume`, `.done`, harness;
  4. `fullfsync` według wyniku pomiaru (ADR-020);
  5. nadzorca, `build_pair.sh`, nakładka;
  6. promocja, odmowa `export`, sprzątanie;
  7. historia w `verify`/`export`;
  8. dokumentacja i ADR.
- Każda zmiana w `literaki_slownik/` zmienia `tree_sha256`. Para A/B buduje się z jednego commitu.
- Strażnik działa w procesie: zapamiętuje aktywny przebieg i `st_dev`. `write_json` pyta go tylko o cele w tym przebiegu.

## Wskazówki implementacyjne

### Testy
- 2–8 testów na grupę kroków. Weryfikacja grupy uruchamia tylko jej nowe testy. Pełny zestaw idzie raz, na końcu: `python3 -m unittest discover -s tests -p 'test_*.py'`.
- Bez prawdziwego USB i bez prawdziwego buildu słownika, tylko fikstury. Przerwania przez wstrzyknięty wyjątek i `os._exit` w procesie potomnym.
- Do aktualizacji: `tests/test_run.py` (`parents=False`) i testy `explain`, jeśli któryś zacznie czytać `stages`.
- Tylko lokalnie. Repo nie ma CI i nie dostaje workflow na runnerach GitHuba.

### Zgodność ze standardami
- `AGENTS.md`: po polsku, zwięźle. Repo jest publiczne, więc w kodzie, testach, dokumentach i artefaktach nie ma UUID wolumenu ani ścieżek z katalogu domowego (`marker_id` jest losowy).
- `docs/generator/cli.md`: JSON na stdout, błędy na stderr, kody jako kontrakt.
- Python stdlib, `unittest`, styl funkcyjny, `GeneratorError(message, code)`.
- Bez zmian w składzie słownika, polityce i pinach.

## Poza zakresem
- Prawdziwe buildy słownika. Pierwsza para na T7 to osobna decyzja właściciela.
- Migracja dzisiejszego `data/work` (zastępuje ją `clean_work.py`).
- Zmiany polityki i składu list; piny POP/POP00/TEMATY (martwy cel `lists-v31-…-a`).
- Cięcie etapów od środka (2C), migawki bazy (3C), reguła świeżego partnera (5C), WAL, ATTACH.
- Automatyczne przepinanie symlinków po zamontowaniu pod inną ścieżką; LaunchAgent nadzorcy.
- Przyczyna zniknięć T7 (kabel, firmware, Spotlight, Time Machine).
- CI. Jeśli kiedyś powstanie, to tylko self-hosted.

## Kryteria sukcesu
1. Zniknięcie T7 w dowolnym etapie daje kod 75 w ciągu sekund, a na dysku systemowym nie powstaje żaden plik przebiegu.
2. Nadzorca sam wznawia pracę po powrocie dysku. Strata ≤ bieżący etap albo raport.
3. Test „wznowiony = świeży” przechodzi dla każdego punktu przerwania, a para wznowiony + świeży → VERIFIED.
4. K1–K10 bez zmian. Historia prób jest widoczna w `verify` i w `release-manifest.json`.
5. Inne błędy nie są ponawiane. Uszkodzona baza zatrzymuje pracę kodem 77.
6. Po promocji wydanie i zapieczętowana baza leżą wyłącznie na dysku wewnętrznym, a `export` z T7 jest niemożliwy.
7. `clean_work.py` bez zgody właściciela nie usuwa niczego nieodtwarzalnego. Wydanie wysłane na serwer nigdy nie jest kandydatem.
8. W repo nie ma UUID ani ścieżek domowych. `git check-ignore` łapie symlinki w `data/work` i `logs/`.
9. ADR-020 zawiera zmierzony narzut i wybrany tryb.

## Rozwiązanie uwag audytu

Źródło: `../verification/spec-audit.md`.

| ID | Zmiana |
|---|---|
| H1 | „Kolejność kontroli `--resume`”: najpierw `lexists`, cel, G1 (75), potem manifest (4), potem G2 (76). Nadzorca używa `lexists` (M5) |
| H2 | Reguła „bieżące na serwerze” porównuje sha256 `release-manifest.json` i każdego pliku z `files` z hashami w `NOTICE`. Fail-safe bez zmian. Fikstura w prawdziwym kształcie |
| H3 | Tabela stanów S0–S4 promocji: 75 przy zniknięciu T7, staging zawsze od zera, `changes_since_verify` na stagingu przed zamianą, `promotion.json` z `t7_path`, praca także po `export` |
| M1 | Zamiana `renamex_np(RENAME_SWAP)` zamiast `unlink` + `rename` |
| M2 | Klasy sprzątania z pierwszeństwem: `VERIFIED`/`FROZEN` i promocja w toku nigdy; osierocony tylko `INCOMPLETE`/resztka startu, ≥ 24 h |
| M3 | Dwa osobne `DROP`, najpierw `evidence_candidate`; w wierszach importu DROP przed DELETE |
| M4 | `links` kończy `pending` z `reason`, gdy `stage_completion.complete` = false |
| M5 | Nadzorca: `lexists` i 75 przed `create_run` → świeży build; build sprząta resztkę startu (R1); niegotowy `preflight` przy `--resume` zaczyna od nowa |
| M6 | 50 GB na proces, 100 GB na wolumen przy starcie pary |
| M7 | Jawny `--work-root` bez znacznika → 76 |
| M8 | `find_by_marker`: wolumen pod inną ścieżką → 76 od razu, bez 30 min czekania |
| L1 | Inne `inputs.manifest_sha256` → 3 |
| L2 | `.gitignore`: tylko dodać `/logs`; test `check-ignore` dla `data/work/x` |
| L3 | Opis idempotencji `constructions` poprawiony (klucz z treści) |
| L4 | Ryzyko `rowid` obniżone, plan awaryjny zostaje |
| L5 | Zapis o `test_explain.py:370` poprawiony |
| L6 | Wydania zagnieżdżone (głębokość 2), wersje `v1r2`, nieznane → „nigdy” |
| L7 | Pomiar `fullfsync` w zakresie wdrożenia; SIGTERM/SIGHUP opisane; LaunchAgent poza zakresem |
| L8 | Nowe kody `resume_reports.py` w `cli.md` (R13) |
| L9 | Nadzorca z wstrzykiwanym buildem, `sleep` i zegarem |
