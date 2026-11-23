# Etapy buildu: co czytają i piszą, gdzie trwały stan, czasy (codebase-build)

## TL;DR
- Build to jeden proces z 7 etapami na jednej bazie `build.sqlite` (journal `delete`, `synchronous=FULL`, bez WAL). Stan etapów trzyma `manifest.json`, zapisywany atomowo, a stan danych sama baza. Katalogu przebiegu nie da się użyć ponownie (`run.py:42-45`).
- Żaden etap poza `reports` nie ma wznawiania. `constructions` i `decisions` są z założenia idempotentne (`insert or ignore`). `import_*` i `links` po przerwaniu zostawiają dane, przez które ponowienie się wywróci (`INSERT` przy PK, `create table`).
- Czas: około 12,5–13,8 h na przebieg, z czego `reports` zajmuje ~8–8,5 h (65%) i nie pisze do bazy. Najtańszy duży zysk to checkpoint per raport. Rozmiar: około 21,3 GB tworzą importy, konstrukcje i decyzje, a `links` ~0,76 GB.
- ATTACH per etap rozbija trzy kontrakty: FK między plikami (SQLite ich nie obsługuje), `logical_content_report` (czyta tylko `main.sqlite_master`) oraz `database_sha256` jednego pliku (verify/export).

## Key Decisions
- Za źródło czasów v32 brałem znaczniki `stages.*.updated` w manifeście i mtime plików, bo `.out.json`/`.err` v32 mają 0 B. Za źródło czasów etapów v27–v31 brałem tylko sumy z `/usr/bin/time`, bo katalogi tych przebiegów usunięto i nie ma ich `performance.json`.
- Rozmiar per etap oszacowałem z `rootpage` tabel `links` (`freelist_count=0`). Nie użyłem `dbstat`, bo wymaga pełnego skanu.

## Open Questions / Risks
- `decisions` w v32-a trwał ~61 h (2026-11-04 18:23 → 2026-11-07 07:38 UTC), a cały v31 tylko 13,8 h. Przyczyna jest nieznana: uśpienie maszyny, konkurencja A/B albo dysk. Work-log podaje tylko „etap reports dokończony po restarcie maszyny” (`.maister/tasks/development/2026-11-04-16-sgjp-20261018/work-log.md:21`). Nie traktować tego jako miary.
- `import_kwjp` w v32 trwał 2 h 25 min. Brak porównania z v31, bo nie ma jego `performance.json`.
- `write_json` robi `fsync` pliku, ale nie katalogu i nie `F_FULLFSYNC` (`canonical.py:40-41`). Na macOS i USB przy utracie zasilania rename może nie przetrwać (kategoria external).
- `write_lists` pisze `lists/*.txt` nieatomowo (`build.py:85`, `write_bytes`).
- `resume_reports.py` otwiera bazę w trybie `rw`, a nie `ro` (`scripts/resume_reports.py:59`), choć raporty nie piszą do bazy.

## Etapy (kolejność `run.py:9`, wykonanie `build.py:92-248`)

| Etap | Czyta | Pisze (baza) | Pisze (pliki) | Commit | Ponowienie / wznowienie | v32-a czas |
|---|---|---|---|---|---|---|
| `create_run` | `sources.json` (`inspect_sources`, hash wszystkich wejść) | — | `manifest.json`, `reports/` | — | odmowa, gdy katalog istnieje (`run.py:42-45`) | — |
| `preflight` | — | `source_artifact` (`build.py:103-106`) + schemat (`database.py:21-22`) | manifest | 1 commit | — | 3 s |
| `import_sgjp` | `cache/sgjp/*.tab.gz`, suplement | `sgjp_record` porcjami; potem `lexeme`, `surface_form` (`INSERT OR IGNORE`), `interpretation` jednym INSERT…SELECT (`build.py:28-49`) | — | co 10 000 wierszy (`build.py:21-25`); agregaty 1 commit (`build.py:49`) | **nie**: zwykły `INSERT` przy PK; częściowe porcje zostają | 17 min 27 s |
| `import_kwjp` | `cache/kwjp/*.csv.gz` | `corpus_evidence` (`build.py:59-73`) | po etapie: `import-counts.json`, `inventory.json`, `qualifier-conditions.json` (`build.py:122-127`) | co 10 000 | **nie** (UNIQUE `source_id,row_number`) | 2 h 24 min |
| `constructions` | `interpretation`+`surface_form`+`lexeme` | `derivation_candidate`, `derivation_component` (`constructions.py:501-598`) | `construction-candidates.json` | co 10 000 kandydatów (`constructions.py:536`) | **tak, z założenia**: `insert or ignore`, klucz = sha payloadu; docstring: „porcje mogą pozostać po awarii” (`constructions.py:504`) | ~24,5 min |
| `decisions` | konfiguracje `semantic-uses`, wyjątki dawności, wykluczenia (`build.py:141-168`) | `analysis`, `decision_payload`, `variant_decision` (`decisions.py:309-315`) | `decisions.json`; `lists/{broad,standard}.txt` (`build.py:76-89`) | co porcję (`decisions.py:315`) | **tak, z założenia**: `insert or ignore`; odmowa przy innej `policy_version`, innym przeglądzie użyć albo zmienionym payloadzie (`decisions.py:281-293`) | ~61 h (anomalia) + `write_lists` ~1 h 56 min |
| `links` | `corpus_evidence`, `lexeme`, `surface_form`, `derivation_candidate`; tabela `temp.link_lemma_pos` w RAM (`links.py:45-53`) | `evidence_link`, `evidence_candidate` + 6 indeksów (`links.py:130-165`) | `links.json` (`build.py:197`) | **1 transakcja** na cały etap (`build.py:191`); INSERT wiersz po wierszu | **nie**: `create table` bez `IF NOT EXISTS`; po przerwaniu (rollback) można ponowić | ~26 min (zapis do bazy kończy się 09:52 UTC) |
| `reports` | cała baza, **tylko odczyt** (mtime `build.sqlite` = koniec `links`, 2026-11-07T10:52+01) | — | 7–9 JSON-ów (`build.py:201-235`), na końcu `performance.json`, `canonical-index.json` (`build.py:240-244`) | — | **tak, w całości**: `scripts/resume_reports.py` (wymaga `complete` do `links`, `reports` w stanie `running`/`failed`, tego samego `tree_sha256` i `manifest_sha256`: `:46-54`). Nie ma checkpointu per raport | 8,54 h (wznowienie) |

Czasy raportów v32-a (`reports/performance.json`): `unresolved` 14 857 s (4,1 h), `quality_analyses` 5180 s, `logical_content` 4564 s, `filter_impact` 3789 s, `quality_words` 2013 s, `quality_links` 302 s, `coverage` 34 s; szczyt RSS 8,99 GB. `unresolved` przekazuje wynik w pamięci do `filter_impact`, `quality_*` i `coverage` (`build.py:204-232`). Żeby wznowić od środka, trzeba by wczytać `unresolved.json` z pliku.

## Czasy i rozmiary całości (logi `data/work/*.err`, `/usr/bin/time -l`)

| Przebieg | real | max RSS | Uwagi |
|---|---|---|---|
| v24-a | 13 861 s | 1,26 GB | błąd w reports („Nie można odczytać pełnych ocen…”) |
| v27-a | 48 667 s (13,5 h) | 1,20 GB | complete |
| v28-a | 41 821 s | 1,18 GB | „command terminated abnormally”, `.out.json` 0 B |
| v29-a | 34 832 s (9,7 h) | 1,50 GB | complete |
| v30-a / b (równolegle) | 45 528 / 45 545 s (12,6 h) | 1,20 / 1,16 GB | „ok. 12,5 h, w tym reports ~8 h” (`.maister/tasks/development/2026-10-12-stabilizacja-progu-pop/implementation/work-log.md:27`) |
| v31-a / b (kolejno) | 49 552 / 46 337 s (13,8 / 12,9 h) | 1,18 / 1,14 GB | przed cache 4 GB (`bb01f15`, 2026-10-13) |
| v32-a / b | — (0 B) | 8,99 GB (perf.) | przerwany restartem; reports wznowione |
| verify v31 / v32 | 26 211 s / 20 765 s (5,8 h) | 1,37 / 7,05 GB | `integrity_check` + `logical_content` A i B + sha256 bazy |
| export v31b (z v32-a) | 11,5 s | 0,13 GB | sha256 22 GB bazy (`export.py:82`) |

Baza v32-a: 22 035 492 864 B, `page_size` 4096, `page_count` 5 379 759, `freelist_count` 0, `journal_mode=delete`, `synchronous=2`, `user_version=2`, `auto_vacuum=0` (PRAGMA tylko do odczytu). `evidence_link` ma rootpage 5 194 303, więc wszystko przed `links` to ~21,28 GB, a `links` ~0,76 GB. Pozostałe pliki przebiegu: `lists/` 83 MB, `reports/` ~66 MB (`quality-words.json` 61 MB), `verification/` 146 MB.

## Trwały stan i jego zapis
- `manifest.json`: statusy etapów (`pending/running/complete/failed`, `updated`), `code` (K8), `inputs` z `resolved_path`, `verification`, `export` (`run.py:47-63`). `set_stage` odmawia, gdy przebieg jest `VERIFIED` albo `FROZEN` (`run.py:59-60`). Po `kill -9` albo utracie dysku etap zostaje `running` (`build.py:250-253`).
- `canonical.write_json`: `mkstemp` w tym samym katalogu, `fsync`, `os.replace` (`canonical.py:33-44`). Zapis atomowy wobec procesu, ale bez fsync katalogu i bez `F_FULLFSYNC`.
- Baza: `connect()` ustawia tylko `foreign_keys=ON`, `cache_size=-4194304` (4 GB) i `temp_store=MEMORY` (`database.py:14-18`). Nie ustawia `journal_mode`, `synchronous` ani `fullfsync`. Na wyjściu z kontekstu robi commit, a przy wyjątku rollback (`database.py:24-27`).
- `performance` istnieje tylko w pamięci aż do `build.py:243`. Po awarii czasy wcześniejszych etapów przepadają (`resume_reports.py:56`).

## Rozwiązywanie ścieżek
- `--run-dir` jest wymagany i liczony względem cwd (`cli.py:25,28,36,41`, `build.py:96`). `connect` przechodzi na ścieżkę absolutną (`database.py:10`). `build_pair.sh` zawsze używa `data/work/$1-$stamp-$side` i kładzie logi `.out.json`/`.err` obok katalogu (`scripts/build_pair.sh:12-15`).
- Wejścia (`cache/`): ścieżki względem katalogu manifestu, np. `../../cache/sgjp/…` (`config/generator/sources.json`), `(base/path).resolve()` + sha256 (`inputs.py:33-37`). Symlink jest akceptowany, bo działa `resolve()`. Absolutny `resolved_path` trafia do manifestu i `source_artifact.metadata`, ale `logical_content` go pomija (`reports.py:318-321`).
- `canonical_index` odrzuca symlink i ścieżkę spoza przebiegu dla `lists/` i `reports/` (`reports.py:104-105`). Pomija `build.sqlite`, `manifest.json` i `performance.json` (`reports.py:121`).

## Czytelnicy przebiegu
- `verify`: `build.sqlite` `ro` (`verify.py:206,380`), `integrity_check` + `foreign_key_check` + `logical_content` (`verify.py:377-392`), sha256 całego pliku jako pieczęć (`verify.py:619,628`). Tworzy `verification/attempt-NNNN` (`verify.py:565-574`).
- `export`: ponownie liczy sha256 `build.sqlite` (`export.py:82`). Na końcu robi `chmod` bazy do trybu tylko do odczytu i ustawia `FROZEN` (`export.py:168-172`).
- `explain`: `ro` (`explain.py:193,461`), czyta `analysis`, `interpretation`, `surface_form`, `lexeme`, `derivation_*`, `evidence_*`, `corpus_evidence`.

## Które tabele mogłyby iść do osobnych plików (ATTACH)

| Plik etapu | Tabele | FK do innego pliku |
|---|---|---|
| import | `source_artifact`, `sgjp_record`, `lexeme`, `surface_form`, `interpretation`, `corpus_evidence` | — |
| constructions | `derivation_candidate`, `derivation_component` | `derivation_component` → `sgjp_record` (`schema.sql:51`) |
| decisions | `analysis`, `decision_payload`, `variant_decision` | `analysis` → `interpretation`, `derivation_candidate` (`schema.sql:57-58`) |
| links | `evidence_link`, `evidence_candidate` | → `corpus_evidence`, `lexeme`, `surface_form`, `derivation_candidate` (`links.py:134-142`) |

Przeszkody:
1. SQLite nie pozwala na FK między schematami. Trzeba by usunąć te FK albo sprawdzać je jawnie.
2. `logical_content_report` czyta `sqlite_master` tylko z `main` i ma zamknięty zestaw tabel (`reports.py:295-307`).
3. `database_sha256` dotyczy jednego pliku (`verify.py:619`, `export.py:82`), a `explain` i `verify` otwierają jeden plik.
4. Wszystkie zapytania są bez prefiksu schematu. Działają przez ATTACH, dopóki nazwy tabel się nie powtarzają.

Najprostszy podział jest naturalny: `links` (~0,76 GB) i `decisions` piszą tylko nowe tabele, a importy są największe i najtańsze w czasie (~2,7 h w v32). Podział **etapów czasowo kosztownych** (`reports`) nie wymaga ATTACH, bo `reports` nie pisze do bazy.
