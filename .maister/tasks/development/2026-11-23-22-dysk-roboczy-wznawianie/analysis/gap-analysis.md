# Analiza luk: #22 — dysk roboczy na T7 i wznawianie budowy

## TL;DR
Z projektu (12 kroków) w kodzie nie ma nic: brak `--resume`, strażnika, kodów 75–78, trwałego zapisu, nadzorcy i pomiaru. Do tego cztery zagrożenia „wznowiony ≠ świeży” trzeba naprawić przed `--resume`.
Nowa zasada właściciela (na T7 tylko to, co odtwarzalne) unieważnia ADR-001 w obecnym kształcie: symlink całego `data/work` wyniósłby na niebackupowany dysk 57 pakietów wydań, przeglądy i weryfikacje. T7 dzieli kontener APFS z dyskiem Time Machine, więc to, co na nim leży, nie ma kopii.
Inwentarz: z 25 GB w `data/work` odtwarzalny „ciężar” to praktycznie jeden plik, `build.sqlite` zamrożonego v32 (21 GB). Reszta (~4 GB) jest nieodtwarzalna albo za mała, żeby ją przenosić.
Rekomendacja: `data/work` zostaje prawdziwym katalogiem wewnętrznym, nowe przebiegi to symlinki per przebieg na T7, a przed `verify` przebieg wraca na dysk wewnętrzny (promocja z kontrolą hashy).

## Key Decisions
- **Układ katalogów zmieniony z 1A na symlink per przebieg + promocja przed `verify`** (decyzja techniczna, nowy ADR-014 zastępuje lokalny ADR-001). Powód: piny `../../data/work/release-*`, `pop-v3-…-a`, `pop00-…-r2-a` muszą wskazywać dysk wewnętrzny. Przepinanie ich zmieniłoby `*-sources.json` i hashe wejść starych buildów. Ścieżki w pinach i runbookach się nie zmieniają.
- **Granica odtwarzalności = `verify`.** Wszystko, co powstaje do końca `build` (baza, `-journal`, `lists/`, `reports/`, `reports/.done/`, manifest bez `verification`), jest odtwarzalne i może leżeć na T7. Od `verify` powstają `verification/attempt-NNNN`, pieczęć i pakiet `export`. To jest nieodtwarzalne, więc musi być już na dysku wewnętrznym.
- **Pozycje niepewne zostają wewnątrz:** `plwordnet/` (1,3 GB), `nkjp-1m/` (0,2 GB) i `cache/` (870 MB). Da się je odtworzyć tylko wtedy, gdy źródło w sieci nadal istnieje, a są małe. To ostrożne odczytanie zasady właściciela.
- **Pomiary i dowody zostają wewnątrz:** `pop-measure-*`, `fala-1-*-czasy`, `timing.json` (czasy są nieodtwarzalne) i 27 niedokończonych przebiegów eksperymentalnych z 2026-10-05 (dowody decyzji o zakresie). Do tego `*-review.json` i 33 logi `.out.json`/`.err`.
- **Skrypt migracji klasyfikuje i odmawia** (krok 0, nowy). Bez listy ręcznej: reguły po zawartości katalogu (np. `release-manifest.json`, `verification/`, `*-review.json`, stan manifestu). Domyślnie tryb `--dry-run`. Ta sama klasyfikacja służy później promocji.
- Decyzje z fazy 1 bez zmian: `attempts[]` na poziomie głównym manifestu, ADR od ADR-014, liczniki `new_*` ze stanu bazy, `explain` zwraca z etapów tylko `.status`.

## Open Questions / Risks
- **Zamrożona baza v32 (21 GB) jest odtwarzalna tylko co do treści.** Nowy build da ten sam `logical_content`, ale bajty `build.sqlite` nie są gwarantowane. Weryfikacja pieczętuje `database_sha256`, więc po utracie T7 tej pieczęci nie da się odtworzyć. To decyzja właściciela (D1).
- **Wartość migracji istniejących danych jest mała.** Po klasyfikacji na T7 może trafić tylko baza v32 (zależy od D1). Główny zysk z T7 to przyszłe buildy (~22 GB na stronę, para ~44 GB). Na dysku wewnętrznym jest wolne 195 GB.
- **Promocja przed `verify` kosztuje** kopię ~22 GB na stronę na dysk wewnętrzny (minuty I/O) i miejsce wewnątrz dla każdego zachowanego wydania. Przy wariancie D1 = T7 pakiet wydania i tak zostaje wewnątrz, a baza zostaje na T7 jako symlink w katalogu przebiegu.
- Wolumen T7 jest montowany z `noowners`. Bity trybu (read-only `build.sqlite` po `export`) się zachowują, ale właściciel pliku nie. Skrypt kopiujący sprawdza tryb i sha256 po kopii.
- Manifest v32 zapisuje absolutny `export.output_dir` (ścieżka domowa). Dziś to bez wpływu (gitignored), ale nie wolno go kopiować do artefaktów zadania.
- Piny POP/POP00/TEMATY wskazują usunięty `lists-v31-…-a` (`lists-v30-…-a` też nie istnieje). Tego zadania to nie dotyczy, osobna decyzja właściciela (bez zmian od researchu).
- Zniknięcie T7 przerywa A i B naraz. Błąd wznowienia wspólny dla obu stron wykryje tylko test „wznowiony = świeży”.

## Summary
- **Poziom ryzyka**: średnio-wysoki (kontrakt manifestu: pieczęć, K7, K8, export; I/O zależne od platformy; dane bez kopii na T7).
- **Nakład**: wysoki (ok. 12 plików kodu, 4 nowe skrypty, 7+ modułów testów).
- **Wykryte cechy**: modifies_existing_code, creates_new_entities, involves_data_operations.

## Task Characteristics
- Has reproducible defect: nie (zniknięcie T7 to warunek środowiska, nie błąd w kodzie; `create_run` odmawia istniejącego katalogu zgodnie z projektem)
- Modifies existing code: tak
- Creates new entities: tak (strażnik, nadzorca, pomiar, init wolumenu, migracja/promocja)
- Involves data operations: tak (manifest, sqlite, journal, `.done`, logi, migracja)
- UI heavy: nie (tylko CLI)

## Inwentarz `data/` (zmierzony 2026-11-23)

| Grupa | Wpisy | Rozmiar | Klasa | Miejsce |
|---|---|---|---|---|
| `lists-v32-…-a/build.sqlite` (FROZEN, read-only) | 1 plik | 21 GB | odtwarzalna treść, pieczęć nie | **D1** |
| `lists-v32-…-a`: `manifest.json`, `verification/` (146 MB), `reports/` (63 MB), `lists/` (83 MB) | 1 | 0,3 GB | nieodtwarzalne (pieczęć, dowód wydania) | wewnątrz |
| Pakiety z `release-manifest.json` (`release-LL-PL-v29..v31`, `pop*`, `pop00*`, `tematy*`) | 57 | 1,7 GB | nieodtwarzalne; część przypięta | wewnątrz |
| Przebiegi eksperymentalne 2026-10-05 (`*-scope`, `*-use`, `*-constructions`, …), stan niedokończony | 27 | <1 GB | dowody decyzji | wewnątrz |
| `pop-measure-*`, `fala-1-*-czasy`, `tematy-wydanie`, `tematy-v2-release` | 9 | mało | pomiary i wydania | wewnątrz |
| `plwordnet/` (sqlite), `nkjp-1m/` (pobrane) | 2 | 1,5 GB | zależne od źródła w sieci | wewnątrz |
| Luźne pliki: 33 logi `.out.json`/`.err`, `pop-v1/v2-review.json`, `fala-1-*.log` | 37 | mało | nieodtwarzalne | wewnątrz (logi docelowo `logs/`) |
| `cache/` (poza `data/`) | — | 870 MB | pobrane wejścia | wewnątrz |

W `data/` jest tylko `work/`. W całym `data/work` nie ma symlinków ani twardych dowiązań, a read-only jest 1006 plików (bazy i pakiety po `export`). Wszystko leży dziś na dysku wewnętrznym, który Time Machine obejmuje.

## Gaps Identified

### Missing Features (wszystko nowe)
- **Krok 0 — klasyfikacja i migracja** (`scripts/migrate_work.py`): inwentarz z klasą każdego wpisu i pliku, `--dry-run` domyślnie, odmowa dla klasy nieodtwarzalnej, kopia z sha256 i trybem, na końcu symlink w miejscu oryginału. Usunięcie oryginału tylko osobną komendą po zgodzie właściciela.
- **Promocja przebiegu** (`scripts/promote_run.py` albo krok w nadzorcy/`verify`): kopia przebiegu z T7 do `data/work/<run>` z kontrolą hashy, podmiana symlinku na katalog, odmowa `verify` na wolumenie zewnętrznym. Projekt tego nie przewiduje, to luka po nowej zasadzie.
- **Strażnik G1–G3** + `scripts/init_work_volume.py`. Brak w kodzie, `create_run` robi `mkdir(parents=True)` (`run.py:40-51`).
- **Klasyfikator i kody 75–78.** Dziś `build.py:249-258` zamienia wszystko na 4. `cli.py` i `docs/generator/cli.md` znają tylko 0, 2, 3, 4, 5, 130.
- **`build --resume`**, `attempts[]`, `PRAGMA quick_check`, znaczniki `reports/.done/`.
- **Nadzorca** `scripts/build_supervised.py` pod `caffeinate -dimsu`.
- **Pomiar** `scripts/measure_fullfsync.py` (warunek decyzji 4B/4C).
- **`build_history`** w `verify` i `export`.

### Incomplete Features
- `write_json` (`canonical.py:33-44`): `fsync` jest, ale bez F_FULLFSYNC i bez fsync katalogu. Sprzątanie w `finally` może zasłonić pierwotny błąd.
- `write_lists` (`build.py:76-89`): `write_bytes`, nieatomowy i bez fsync.
- `connect` (`database.py`): brak jawnych `journal_mode`, `synchronous` i `fullfsync`. Rollback może rzucić przy zniknięciu dysku.
- `scripts/resume_reports.py`: wznawia tylko całe `reports`, duplikuje `build.py:201-235`, bez testów.
- `build_pair.sh`: logi na dysku roboczym, brak nadzorcy i `caffeinate`, brak tworzenia symlinku per przebieg.
- `.gitignore`: `/data/work/` (tylko katalog) i brak `/logs`. Po zmianie układu symlink per przebieg leży wewnątrz ignorowanego katalogu, ale wpis bez ukośnika i test `git check-ignore` zostają (na wypadek symlinku w innym miejscu).

### Behavioral Changes Needed (cztery zagrożenia „wznowiony ≠ świeży”)
1. `new_candidates` (`constructions.py:607`) i `new_analyses`/`new_decisions` (`decisions.py:432`) liczyć ze stanu bazy.
2. `import-counts.json` przeliczać z bazy, nie z pamięci (`build.py:99,116`).
3. `inventory.json` i `qualifier-conditions.json` przenieść do etapu (`build.py:122-127`).
4. `links.py:132`: `DROP TABLE IF EXISTS` przed `CREATE`, links ze statusem `running`.
Do tego: kasowanie wiersza `source_artifact` z decisions (`decisions.py:356`) przy resecie, preflight `complete` dopiero po utworzeniu bazy (`build.py:101-102`), `explain.py:267` zwraca tylko `.status` (K7).

## Ścieżka operatora

| Krok | Dziś | Po zmianie | Ocena |
|---|---|---|---|
| Start pary | `build_pair.sh`, przebieg w `data/work/<run>` (dysk wewnętrzny) | `build_pair.sh` → 2 nadzorców; `data/work/<run>` to symlink na T7; logi w `logs/` | ✅ te same ścieżki |
| Zniknięcie T7 | traceback/kod 4, przebieg stracony, logi na T7 | kod 75, nadzorca czeka ≤30 min i sam robi `--resume` | ✅ |
| Restart maszyny | ręczne `resume_reports.py` (tylko w `reports`) | operator uruchamia `build_supervised.py --run-dir …` | ✅, ale wymaga wpisu w runbooku |
| Weryfikacja | `verify` w miejscu | najpierw promocja na dysk wewnętrzny, potem `verify`/`export`; `verify` odmawia na T7 | ⚠️ nowy krok; automatycznie w nadzorcy po kodzie 0, żeby nie był ręczny |
| Wydanie | `export` do `data/work/release-*` | bez zmian (wewnątrz) | ✅ |

Wykrywalność dla operatora (CLI): 6/10 dziś (`resume_reports.py` znany tylko z runbooka), 8/10 po zmianie, jeśli `docs/generator/cli.md` i runbook opiszą nadzorcę i kody.

## Cykl życia danych

| Obiekt | Tworzy | Czyta | Zmienia | Usuwa | Luka |
|---|---|---|---|---|---|
| `manifest.json` | `create_run` | verify, export, explain, resume_reports | `set_stage` (zastępuje słownik) | — | brak `attempts[]`, `resume`, `work_volume.marker_id`; brak otwarcia istniejącego przebiegu |
| `build.sqlite` + `-journal` | `connect` | wszystkie etapy, verify | etapy | — | brak `quick_check`, `fullfsync`; reset tabel import/links |
| `reports/.done/*.json` | — | — | — | — | całość brak |
| `lists/*.txt` | `write_lists` | verify, export | — | — | zapis nieatomowy |
| `verification/attempt-NNNN` | verify | export | — | — | musi powstać na dysku wewnętrznym (promocja) |
| logi `.out.json`/`.err`, `supervisor.log` | `build_pair.sh` (na T7) | operator | — | — | przenieść do `logs/` wewnątrz |
| znacznik `.literaki-work-volume` | — | — | — | — | całość brak (init) |
| kopie migracji | — | — | — | — | skrypt brak; usuwanie oryginałów tylko po zgodzie |

Kompletność: 0 z 8 nowych obiektów i operacji istnieje. Osieroconych operacji nie ma, bo każdy nowy zapis ma czytelnika w projekcie. Jedynym kandydatem był `attempts[]`, ale czytają go `verify` i `export` (krok 10).

## Kroki wdrożenia: stan

| # | Krok | Stan | Uwaga |
|---|---|---|---|
| 0 | Klasyfikacja i migracja `data/work` (nowy) | brak | test na drzewie tymczasowym: odmowa dla pakietu, `verification/`, review; kopia z sha256 i trybem |
| 1 | `.gitignore`, logi do `logs/` | brak | — |
| 2 | `measure_fullfsync.py` + pomiar | brak | pomiar na T7 to nie build, wolno go zrobić |
| 3 | Trwały zapis | częściowo (`fsync`) | — |
| 4 | Strażnik + init | brak | — |
| 5 | Klasyfikator 75–78 | brak | — |
| 6 | `--resume` + 4 zagrożenia + harness | brak | największy krok |
| 7 | `.done` + nakładka `resume_reports.py` | brak | — |
| 8 | `fullfsync` 4B/4C | brak | zależy od 2 |
| 9 | Nadzorca + `build_pair.sh` + promocja | brak | promocja dodana |
| 10 | historia w verify/export | brak | — |
| 11 | Dokumentacja, ADR-014+ | brak | — |
| 12 | Znacznik na T7, pierwsza para A/B | poza wdrożeniem | build tylko po zgodzie właściciela |

## Issues Requiring Decisions

### Critical
1. **D1 — gdzie leży zapieczętowana baza zamrożonego przebiegu** (v32 dziś, każdy następny po `verify`).
   - A: na dysku wewnętrznym (cały przebieg wewnątrz). Migracja istniejących danych nie przenosi wtedy prawie nic.
   - B: na T7, z symlinkiem `build.sqlite` w wewnętrznym katalogu przebiegu. Zwalnia 21 GB wewnątrz, ale po utracie T7 pieczęci `database_sha256` nie da się odtworzyć (treść tak, kosztem ~13 h), a `verify`/`export` takiego przebiegu wymagają T7.
   - Rekomendacja: **A**. Na dysku wewnętrznym jest 195 GB wolne, a pieczęć to dowód wydania. Starsze bazy można później usuwać osobnymi decyzjami.

### Important
1. **D2 — zakres migracji istniejących danych.** Po klasyfikacji (przy D1 = A) nic nie jest warte przeniesienia: reszta to pakiety, dowody, pomiary albo małe pozycje zależne od źródeł w sieci.
   - A: zbudować skrypt (klasyfikacja i odmowa), uruchomić go w `--dry-run`, przenieść tylko to, co sklasyfikuje jako odtwarzalne. Przy D1 = A to zero albo prawie zero.
   - B: pominąć migrację i używać T7 tylko dla nowych przebiegów.
   - Domyślnie: **A**. Właściciel zlecił migrację, a ta sama klasyfikacja służy promocji. Skrypt pokaże inwentarz do akceptacji.
2. **D3 — promocja przed `verify` (nowy krok w przepływie).** Weryfikacja i wydanie tylko na dysku wewnętrznym, a kopia przebiegu (~22 GB na stronę) wykonuje się automatycznie po udanym buildzie.
   - Opcje: automatycznie w nadzorcy po kodzie 0 / ręcznie przed `verify`.
   - Domyślnie: **automatycznie**. Właściciel woli automatyzację, a `verify` i tak odmawia na wolumenie zewnętrznym.

## Recommendations
- Najpierw krok 0 (inwentarz w `--dry-run`) i krok 2 (pomiar). Oba nie są buildem i dają dane do D1/D2 oraz 4B/4C.
- Cztery zagrożenia naprawić jako pierwszą grupę kroku 6, z testem „przerwany + wznowiony = świeży” na każdej granicy etapu.
- ADR-014: układ per przebieg + granica odtwarzalności na `verify`. Lokalny ADR-001..008 przenumerować na ADR-014 i dalej.
- Klasyfikacja w skrypcie jako reguły po zawartości, z testem na drzewie z każdą klasą. Bez ręcznej listy wpisów.

## Risk Assessment
- **Complexity Risk**: wysokie. Podział `build()`, reset tabel, kolejność trwałego zapisu.
- **Integration Risk**: średnie. Pieczęć, K7 i K8 zależą od kształtu manifestu (ok. 18 plików czyta `stages`).
- **Regression Risk**: średnie. Testy `release_helpers.complete_run` nadpisują etapy. Nie ma testów kodów wyjścia CLI.
- **Data Risk**: wysokie przy migracji. Read-only pliki, `noowners` na T7, brak kopii na T7. Kopia z sha256, a usuwanie oryginałów tylko po osobnej zgodzie.
