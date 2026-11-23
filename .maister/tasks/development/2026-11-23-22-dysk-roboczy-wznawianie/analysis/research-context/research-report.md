# Raport: dysk roboczy na /Volumes/Data i wznawianie buildu

Typ: badanie techniczne · Data: 2026-11-23 · Wykonawca: research-synthesizer (maister) · Kod: `literaki-slownik` @ `b31246e7`

## TL;DR
Buduj na dysku wewnętrznym, a na T7 trzymaj tylko gotowe przebiegi. Każde zniknięcie T7, nawet na 3 s, zabija trwający build. Na dysku wewnętrznym jest 193 GB wolnego miejsca, para A/B zajmuje ~44 GB.
Niezależnie od dysku dodaj wznawianie per etap w tej samej bazie i znaczniki per raport. Dziś restart w dowolnym etapie przed `reports` kosztuje do ~13 h.
Od razu popraw `.gitignore` (`/data/work`, `/cache` bez ukośnika) i dodaj strażnik montowania: `ismount` + znacznik z UUID wolumenu, a przy braku dysku przerwij build.

## Key Decisions
- **Lokalizacja: L3, hybryda.** Build wewnątrz, archiwum na `/Volumes/Data`. USB nie bierze udziału w 13-h zapisie, kod się nie zmienia, K1–K10 też nie.
- **Wznawianie: (a), etapy w jednej bazie.** Połowa etapów jest już idempotentna. Daje ochronę przed restartem i kill, nie tylko przed USB.
- **Migawka (b) tylko przy budowie na USB.** Najlepiej przez backup API, a nie `VACUUM INTO`, bo backup kopiuje strony 1:1.
- **ATTACH per etap (c) odrzucony na teraz.** Łamie FK, `logical_content_report` i `database_sha256`.
- **Symlink L1 jako zapas.** Tylko gdy zabraknie miejsca wewnątrz, z poprawką `.gitignore`, strażnikiem i `fullfsync=ON`.

## Open Questions / Risks
- **Piny POP/POP00/TEMATY.** Pliki `config/generator/{pop-sources,pop-sources-v29,pop00-sources,tematy-sources}.json` wskazują usunięty `lists-v31-20261012-162111-a`. Do decyzji właściciela: przepiąć na v32-a albo przebudować v31.
- **Wynik wznowionego buildu.** Nie wiadomo, czy wznowiony build da ten sam `logical_content` co świeży (rowid po `DELETE` i ponownym imporcie). Przed parą A/B potrzebny jest test.
- **Czas `decisions`.** Normalny czas tego etapu nie jest znany (w v32 trwał 61 h, to anomalia).
- **Time Machine.** Nie sprawdzono, czy kopiuje `data/work` z dysku wewnętrznego na ten sam T7.
- **Przyczyna zniknięć T7.** Jest nieznana: zasilanie, kabel albo firmware FXI72P2Q. Przy budowie na USB to ryzyko zostaje.
- **Prywatność.** Repo jest publiczne. UUID wolumenu ma być tylko w znaczniku na samym wolumenie, nigdy w kodzie ani w konfiguracji.

## Spis treści
1. Streszczenie · 2. Cele · 3. Metoda · 4. Ustalenia · 5. Analiza · 6. Lokalizacja: warianty · 7. Wznawianie: warianty · 8. Wnioski · 9. Rekomendacja · 10. Dodatki

## 1. Streszczenie
Badanie objęło miejsce przechowywania plików generatora i wznawianie przerwanego buildu. Źródła to kod (`build.py`, `run.py`, `database.py`, `verify.py`, `export.py`, `explain.py`, skrypty), metadane przebiegów (manifesty, `.err` z `/usr/bin/time`, `performance.json`, PRAGMA w trybie `ro`) oraz dokumentacja SQLite i Apple.

Najważniejsze ustalenie: build to jeden proces z 7 etapami na jednej bazie 22 GB. Zniknięcie dysku kończy proces błędem `SQLITE_IOERR`, a katalogu przebiegu nie da się użyć ponownie. Dlatego dziś awaria oznacza pracę od zera. Wyjątek to `reports`, które da się wznowić w całości.

## 2. Cele
- Gdzie trzymać duże pliki, żeby kod, testy, runbooki i `explain` działały, a brak dysku był wykrywany od razu.
- Jak wznawiać od ostatniego ukończonego etapu albo raportu.
- Jak zachować K1–K10, parę A/B i pieczęci.

Poza zakresem: polityka słownika, nowe buildy, CI.

## 3. Metoda
- 3 zbieracze: `codebase-build`, `codebase-paths`, `external`. Tylko odczyt, bez buildów i bez zapisu do bazy.
- Źródła: ~15 modułów i skryptów, 6 konfiguracji, ~12 dokumentów i ADR, 147 pozycji w `data/work`, ~20 stron dokumentacji SQLite, Apple, Pythona i raportów o T7.
- Rama oceny: trwały stan per etap, koszt powtórzenia, wpływ na każdego czytelnika ścieżki, wpływ na K1–K10, macierz wariant × koszt × ryzyko.

## 4. Ustalenia

| # | Ustalenie | Kategoria | Pewność | Źródła |
|---|---|---|---|---|
| F1 | Build: 7 etapów, jedna baza (`journal_mode=delete`, `synchronous=FULL`, bez `fullfsync`) | architektura | wysoka | 2 |
| F2 | Katalogu przebiegu nie da się użyć ponownie; status po awarii zostaje `running`, a `failed` jest połykany | wznawianie | wysoka | 2 |
| F3 | Czas ~13 h, z tego `reports` 8–8,5 h (65%), `unresolved` 4,1 h; importy 2,7 h | koszt | wysoka | 3 |
| F4 | Idempotentne: `constructions`, `decisions`. Nieidempotentne: `import_*` (zwykły INSERT przy PK), `links` (`create table`) | wznawianie | wysoka | 1 (kod) |
| F5 | Kod bierze `--run-dir`; na sztywno `data/work` jest tylko w `build_pair.sh` i w 4 konfiguracjach z pinami | ścieżki | wysoka | 1 |
| F6 | K1–K10/K8 porównują hashe i treść; przeniesienie katalogu przebiegu jest bezpieczne, przeniesienie repo nie | powtarzalność | wysoka | 1 |
| F7 | `.gitignore` `/data/work/` nie pasuje do symlinku (R1) | bezpieczeństwo repo | wysoka | 2 |
| F8 | Zniknięcie urządzenia → `SQLITE_IOERR_*`; hot journal cofa transakcję, o ile leży obok bazy pod tą samą ścieżką | SQLite | wysoka (dok.), średnia (T7) | 3 |
| F9 | macOS `fsync` nie opróżnia cache dysku; robi to `F_FULLFSYNC`/`PRAGMA fullfsync` (domyślnie off); USB może kłamać | SQLite/macOS | średnia | 3 |
| F10 | `/Volumes` = `root:wheel 755`, więc proces użytkownika nie utworzy sobowtóra; ryzyko zostaje przy `sudo`/`Data 1` | macOS | średnia | 2 |
| F11 | T7 Shield 4 TB: jedno zniknięcie w 7 dniach (2026-11-20 02:32:18, 3 s, bez snu); ten sam kontener APFS ma Time Machine | środowisko | wysoka (pomiar) | 1 |
| F12 | ATTACH łamie FK między plikami, `logical_content_report` (tylko `main`), `database_sha256` | architektura | wysoka | 2 |
| F13 | Piny POP/POP00/TEMATY wskazują usunięty `lists-v31-20261012-162111-a` | konfiguracja | wysoka | 1 |

Szczegóły i cytaty plik:linia: `analysis/findings/codebase-build-stages.md`, `codebase-paths-inventory.md`, `external-sqlite-macos.md`.

### Mapa etapów (v32-a)
| Etap | Czas | Zapis do bazy | Wznawialny dziś | Co trzeba zmienić |
|---|---|---|---|---|
| preflight | 3 s | schemat, `source_artifact` | — | nic |
| import_sgjp | 17 min | `sgjp_record`… (~część 21,3 GB) | nie | obciąć tabele i powtórzyć |
| import_kwjp | 2 h 24 min | `corpus_evidence` | nie | obciąć i powtórzyć |
| constructions | ~25 min | `derivation_*` | tak (`insert or ignore`) | nic |
| decisions | ? (61 h anomalia) | `analysis`, `decision_*`, `variant_decision` | tak | nic; `lists/*.txt` zapisywać atomowo |
| links | ~26 min | `evidence_*` (~0,76 GB), 1 transakcja | po rollbacku tak, ale `create table` | `DROP … IF EXISTS` |
| reports | 8,5 h | nic (tylko odczyt) | w całości (`resume_reports.py`) | znaczniki per raport, `unresolved.json` z pliku |

## 5. Analiza

**Wzorce:** jedna baza jako cały stan, manifest jako dziennik etapów (zapis atomowy, ale bez fsync katalogu), idempotencja przez `insert or ignore`, wznawianie ad hoc tylko dla `reports`, pieczęć hashem całego pliku, logi obok przebiegu (giną z dyskiem).

**Kluczowe wnioski:**
1. **Przerwa 3 s kosztuje tyle co 3 h.** Po ponownym montowaniu deskryptory procesu są martwe. Liczy się tylko trwały stan i to, czy da się z niego ruszyć.
2. **Build wewnątrz usuwa problem USB całkowicie** i nie wymaga zmian w kodzie ani w kontraktach K.
3. **Znaczniki per raport dają największy zysk na godzinę pracy:** 65% czasu buildu, najgorsza strata spada z 8,5 h do 4,1 h.
4. **Hot journal to jedyna ochrona bazy na USB.** Nie wolno go ruszać i trzeba otwierać bazę tą samą ścieżką.

**SWOT (stan obecny)**
| Mocne | Słabe |
|---|---|
| manifest z etapami; idempotentne `constructions`/`decisions`; kontrakty K niezależne od ścieżki przebiegu | brak ponownego użycia katalogu; `reports` wznawiane tylko w całości; brak strażnika montowania; `.gitignore` nie łapie symlinku |
| **Szanse** | **Zagrożenia** |
| 193 GB wewnątrz mieści parę; `resume_reports.py` jako wzór uogólnienia | T7 znika bez ostrzeżenia; mostek USB może kłamać o `fsync`; Time Machine na tym samym dysku |

## 6. Lokalizacja: warianty

| Wariant | Jak | Koszt zmiany | Ryzyko | K1–K10 |
|---|---|---|---|---|
| **L1 symlink** | `data/work` → `/Volumes/Data/literaki-slownik/work` | ~0 kodu; `.gitignore` | build na USB (każde zniknięcie zabija przebieg); wiszący symlink daje mylący błąd „katalog już istnieje” (R3); wyciek ścieżki przy złym `.gitignore` (R1) | bez zmian; piny `../../data/work` działają |
| **L2 korzeń z env/flagi** | `LITERAKI_WORK_ROOT` w `build_pair.sh`, `--run-dir` z niego | mały kod, ~20 miejsc w runbookach i `docs/generator/cli.md` | piny w 4 konfiguracjach nie podążą; cichy zapis na dysk systemowy przy pustym punkcie montowania (R2) | bez zmian; zmiana pinów → nowy `manifest_sha256` |
| **L3 hybryda (zalecana)** | build w `data/work` wewnątrz; po `verify`/`export` skrypt archiwizuje na `/Volumes/Data/literaki-slownik/archive/<przebieg>` (kopia → sha256 → usunięcie źródła); `explain --run-dir` z archiwum | mały (skrypt + runbook) | wewnątrz jedna para naraz; ewentualna kopia `data/work` przez Time Machine | bez zmian (porównania po hashach) |

**Poprawka `.gitignore` (R1), we wszystkich wariantach:** zamienić `/data/work/` → `/data/work` i `/cache/` → `/cache`. Wzorzec bez ukośnika pasuje i do katalogu, i do symlinku. Sprawdzić: `git check-ignore -v data/work`.

**Strażnik montowania** (zawsze, gdy ścieżka leży pod `/Volumes`):
- Na wolumenie leży plik `/Volumes/Data/.literaki-work-volume` z UUID odczytanym raz z `diskutil info -plist /Volumes/Data` (`VolumeUUID`).
- Przed startem, przed każdym etapem i przed każdym `os.replace` sprawdzaj:
  - `os.path.ismount('/Volumes/Data')`;
  - czy znacznik istnieje i jego UUID zgadza się z bieżącym `diskutil`;
  - czy `os.stat(run_dir).st_dev` jest takie samo jak na starcie.
- Jeśli coś się nie zgadza, kończ z jasnym komunikatem („brak wolumenu Data”). Nie twórz katalogu i nie używaj `mkdir -p` od `/Volumes`.
- W `build_pair.sh`: ta sama kontrola przed startem oraz sprawdzenie wolnego miejsca (≥ 2×22 GB na stronę).

## 7. Wznawianie: warianty

**Co robi SQLite przy zniknięciu USB w trakcie zapisu.** Proces dostaje `SQLITE_IOERR_WRITE`, `_READ` albo `_FSYNC`. Trzeba wtedy zrobić `ROLLBACK`, zamknąć połączenie i poczekać na ponowne zamontowanie. Przy ponownym otwarciu hot journal (`build.sqlite-journal`) cofa przerwaną transakcję. Warunek: journal leży obok bazy i baza jest otwierana tą samą ścieżką co w chwili awarii. Journala nie wolno usuwać, przenosić ani kopiować bazy bez niego. Na macOS `fsync` nie opróżnia cache dysku, a `PRAGMA fullfsync=ON` (`F_FULLFSYNC`) tak. Nie wiadomo jednak, czy mostek T7 to przekazuje dalej. Dlatego po wznowieniu trzeba sprawdzić bazę (`PRAGMA quick_check`).

| Wariant | Opis | Przetrwa 3 s USB | Strata na awarię | Zmiana kodu | K1–K10 / A-B | Miejsce |
|---|---|---|---|---|---|---|
| dziś | — | nie | do ~13 h (w `reports` do 8,5 h) | — | — | 22 GB |
| **(a) etapy w jednej bazie** | `build --resume`: zgoda na istniejący katalog z tym samym `tree_sha256`/`manifest_sha256`; `running` przy starcie → `failed`; `import_*`: obciąć tabele etapu i powtórzyć; `links`: `DROP … IF EXISTS`; `reports`: znacznik `reports/.done/<raport>.json` z sha256 wyniku, `unresolved` czytany z pliku; czasy etapów zapisywane w manifeście; `quick_check` po wznowieniu | tak, jeśli journal cofnie (średnia) | bieżący etap: ≤2,4 h import, ~25 min konstrukcje/links, `decisions` ?, ≤4,1 h raport | średnia (~200–400 linii + testy) | K8: nowa tożsamość kodu raz, A i B budowane tym samym kodem; potrzebny test „wznowiony = świeży” (`logical_content`) | 22 GB |
| **(b) migawka po długim etapie** | po `import_kwjp` i `decisions`: backup API → `checkpoint.sqlite.tmp` → fsync → `os.replace` → znacznik z sha256; wznowienie = przywrócenie migawki i ruszenie od następnego etapu | tak, chroni też przed korupcją | jak (a) + czas migawki (niezmierzony) | (a) bez idempotencji importów + ~100 linii | backup API zachowuje strony; `VACUUM INTO` może zmienić rowid (tabele bez `INTEGER PRIMARY KEY`) | +22 GB/stronę (+44 GB/parę) |
| **(c) plik per etap + ATTACH** | `import.sqlite`, `constructions.sqlite`…, czytane `ATTACH … mode=ro` | tak, pliki niezmienne | jak (a) | duża + ADR | łamie FK (SQLite nie ma FK między plikami), `logical_content_report` (tylko `main`), `database_sha256` jednego pliku; `explain`/`verify` otwierają jeden plik | ~22 GB |
| **(d) build wewnątrz, potem przenieś** | = L3 | tak, USB nie bierze udziału | 0 od USB; inne awarie jak dziś (albo jak w (a)) | ~0 | bez zmian | 44 GB/parę wewnątrz z 193 GB |

## 8. Wnioski
- **Odpowiedź na pytanie 1 (gdzie), pewność wysoka.** Duże pliki trzymaj na T7, ale buduj na dysku wewnętrznym (L3). Jeśli build ma iść na T7, użyj L1 + `.gitignore` + strażnika. L2 nie daje nic ponad L1, a psuje piny i runbooki.
- **Odpowiedź na pytanie 2 (jak wznawiać), pewność wysoka co do kształtu, średnia co do identyczności wyniku.** Wariant (a) ze znacznikami per raport. (b) tylko przy budowie na USB.
- **Odpowiedź na pytanie 3 (powtarzalność), pewność wysoka.** L1 i L3 nie zmieniają K1–K10. Zmiana z (a) zmienia raz tożsamość kodu (K8), co jest normalne. Trzeba udowodnić testem, że wznowiony przebieg daje ten sam `logical_content` co świeży.
- **Ustalenia poboczne:**
  - logi `.out.json`/`.err` giną razem z dyskiem;
  - `write_lists` nie jest atomowy;
  - `resume_reports.py` otwiera bazę `rw`;
  - `write_json` nie robi fsync katalogu.

## 9. Rekomendacja (kolejność)

| # | Krok | Priorytet | Nakład | Pewność | Uwagi |
|---|---|---|---|---|---|
| 1 | `.gitignore`: `/data/work`, `/cache` bez ukośnika; `git check-ignore -v` | wysoki | minuty | wysoka | chroni publiczne repo w każdym wariancie |
| 2 | Decyzja właściciela o pinach POP/POP00/TEMATY (przepiąć na v32-a albo przebudować v31) | wysoki | decyzja | wysoka | bez tego POP/POP00/TEMATY dają błąd „Brak zwykłego pliku” |
| 3 | L3: build wewnątrz; skrypt `scripts/archive_run.sh` (kopia na `/Volumes/Data/literaki-slownik/archive/`, porównanie sha256 `build.sqlite` z `export`, potem usunięcie źródła); przenieść obecny v32-a do archiwum; sprawdzić wykluczenie `data/work` z Time Machine | wysoki | mały | wysoka | zniknięcie T7 przestaje dotykać buildu |
| 4 | Strażnik montowania i miejsca w `build_pair.sh` i archiwizacji; logi `.err`/`.out.json` poza katalogiem na T7 | wysoki | mały | wysoka | fail-fast zamiast cichego zapisu |
| 5 | Znaczniki per raport w `reports` + `unresolved` z pliku; `resume_reports.py` w trybie `ro` | wysoki | mały–średni | wysoka | największy zysk: 65% czasu |
| 6 | `build --resume` (wariant a): ponowne użycie katalogu, `running`→`failed`, obcięcie importów, `DROP IF EXISTS` dla `links`, czasy etapów w manifeście, `quick_check`; test „wznowiony = świeży” | średni | średni | średnia | chroni przed restartem/kill (jak w v32) |
| 7 | Tylko jeśli build ma iść na T7: L1 + `PRAGMA fullfsync=ON` + migawka (b) przez backup API po `import_kwjp` i `decisions` | niski | średni | średnia | kosztuje +44 GB/parę i czas fsync |
| 8 | Łagodzenie T7: `caffeinate -dimsu` na czas buildu, Spotlight wyłączony dla wolumenu, bez backupu TM w trakcie, bezpośredni port i krótki kabel, sprawdzić firmware | niski | minuty | niska–średnia | przyczyna zniknięć nieznana |

Nie robić: ATTACH per etap (c) bez osobnego ADR; ręcznej „migracji” ścieżek w manifeście (łamie pieczęć); `mkdir -p` od `/Volumes`; uruchamiania buildu przez `sudo`. CI, jeśli kiedyś powstanie, tylko na runnerze self-hosted na Macu.

## 10. Dodatki

### Źródła
- Ustalenia: `analysis/findings/codebase-build-stages.md`, `analysis/findings/codebase-paths-inventory.md`, `analysis/findings/external-sqlite-macos.md`.
- Plan i lista źródeł: `planning/research-brief.md`, `planning/research-plan.md`, `planning/sources.md`.
- Zewnętrzne:
  - SQLite: https://www.sqlite.org/atomiccommit.html, https://www.sqlite.org/howtocorrupt.html, https://www.sqlite.org/rescode.html, https://www.sqlite.org/pragma.html, https://www.sqlite.org/wal.html, https://www.sqlite.org/lang_attach.html, https://www.sqlite.org/lang_vacuum.html, https://www.sqlite.org/backup.html;
  - Apple: `man 2 fsync`;
  - Python: dokumentacja `os.replace` i `os.path.ismount`;
  - sobowtóry w `/Volumes`: TidBITS;
  - firmware T7: wątki Apple i Samsung.

### Luki
- Normalny czas `decisions`; czasy etapów v27–v31.
- Czasy `quick_check`, kopii i backup API dla 21 GB na T7 (niezmierzone).
- Komunikat przy wiszącym symlinku (R3) wywnioskowany, nie sprawdzony.
- Przyczyna zniknięć T7; jedno zapytanie do logu z 7 dni.
- Time Machine a `data/work`.

### Szczegóły metody
- Pomiary tylko z istniejących artefaktów.
- PRAGMA w trybie `ro`, bez `integrity_check`.
- Bez buildów, bez `rm`/`mv`/`ln`.
