# Ścieżki `data/work`, `cache/`, przebiegi: inwentarz i wpływ przeniesienia

## TL;DR
- Kod generatora nie ma na sztywno `data/work`: każde polecenie bierze `--run-dir` (cli.py:25–47). Wejścia rozwiązuje względem katalogu manifestu źródeł (`config/generator/`), nie względem przebiegu (inputs.py:33, 80–83).
- Manifest przebiegu zapisuje **ścieżki bezwzględne** wejść (`inputs.manifest_path`, `artifacts[].resolved_path`) i eksportu (`export.output_dir`). K1–K10 i K8 porównują **hashe i treść**, a nie ścieżki przebiegu. Przeniesienie katalogu przebiegu lub symlink `data/work` nie psuje verify, export ani explain. Przeniesienie **repo** psuje (K1, export, explain liczą od zapisanego `manifest_path`).
- Na sztywno `../../data/work/...` są piny w `config/generator/{pop-sources,pop-sources-v29,pop00-sources,tematy-sources}.json`. Działają tylko przez symlink albo przez ścieżkę względną; same zmienna środowiskowa lub flaga ich nie przekierują.
- Groźny przypadek: `.gitignore` ma `/data/work/` z ukośnikiem, a ten wzorzec nie pasuje do symlinku. Symlink `data/work` pokaże się jako nieśledzony i może trafić do publicznego repo.
- Zniknięcie dysku daje głośny błąd w verify, explain, export i `build_pair.sh`. Po cichu zawiodą: bezwzględny katalog roboczy na pustym punkcie montowania (`mkdir(parents=True)` utworzy drzewo na dysku wewnętrznym) i zapis statusu `failed`, który przy błędzie I/O jest połykany.

## Key Decisions
- „Ścieżka zapisana” i „ścieżka porównywana” to dwie różne rzeczy. Rozstrzyga ta druga: porównania idą po hashach (reports.py:79–123, verify.py:416–462, export.py:58–100).
- Symlink oceniam na poziomie katalogu (`data/work` → wolumen). Symlinki do pojedynczych plików w przebiegu są celowo odrzucane (reports.py:103, verify.py:540, 549, export.py:95).
- Zachowanie `pathlib.mkdir` przy wiszącym symlinku wywnioskowałem z semantyki CPythona. Nie testowałem go, bo zakaz `ln` i operacji zapisu.

## Open Questions / Risks
- **R1 (.gitignore, wysokie):** `/data/work/` i `/cache/` (.gitignore:2–5) pasują tylko do katalogów, a git nie traktuje symlinku jak katalogu. Symlink `data/work` → `/Volumes/Data/...` wymaga wpisu bez ukośnika (`/data/work`). Bez tego `git add -A` doda symlink z prywatną ścieżką do publicznego repo. Wniosek z dokumentacji gitignore, nie pomiar.
- **R2 (cichy zapis na dysk wewnętrzny):** przy wariancie env/flagi z bezwzględnym katalogiem roboczym `create_run` robi `mkdir(parents=True)` (run.py:43). Jeśli `/Volumes/Data` zostanie jako pusty, zapisywalny katalog (np. resztka przy montowaniu jako „Data 1”), build zacznie pisać ~21 GB na dysk systemowy bez błędu. Dziś `/Volumes/Data` ma właściciela użytkownika (noowners), więc zapis byłby możliwy, gdyby katalog został.
- **R3 (mylący komunikat):** przy wiszącym symlinku `data/work` rodzic się nie tworzy (EEXIST na symlinku, `is_dir()`=False), a `create_run` zamienia `FileExistsError` na „Katalog przebiegu już istnieje; wybierz nowy” (run.py:44–45). Błąd jest głośny, ale opisuje złą przyczynę (wniosek).
- **R4:** przy błędzie I/O w trakcie buildu `set_stage(...,'failed')` może się nie udać, a `except OSError: pass` (build.py:249–253) to połyka. Manifest zostaje na `running`. verify i tak odmówi (verify.py:592–598), ale `.err` i `.out.json` leżą obok przebiegu na tym samym dysku (build_pair.sh:12–15) i giną razem z nim.
- **R5:** piny pop, pop00 i tematy wskazują `lists-v31-20261012-162111-a`, którego już nie ma (zostały tylko `.out.json`/`.err`). Te konfiguracje nie działają niezależnie od przeniesienia, z głośnym błędem „Brak zwykłego pliku” (inputs.py:34–35).
- `write_json` robi `fsync` pliku i `os.replace` (canonical.py:33–44), ale bez `F_FULLFSYNC` i bez fsync katalogu. Na USB to temat dla `external`.

## Inwentarz

### Kod (`literaki_slownik/`)
| Miejsce | Co | Wpływ symlinku `data/work` | Wpływ env/flagi (root poza repo) |
|---|---|---|---|
| cli.py:25,28,36,41,47 | `--run-dir` wymagane (pop: opcjonalne) | brak | brak: wystarczy podać ścieżkę |
| run.py:40–51 | `create_run`: `mkdir(parents=True, exist_ok=False)` | wiszący symlink → mylący błąd (R3) | pusty punkt montowania → cichy zapis (R2) |
| run.py:16–37 | `code_identity`: hash `*.py` i `schema.sql`, `git status -- literaki_slownik` z `cwd=package.parent` | brak (dane poza pakietem) | brak |
| inputs.py:33,42,83,102 | wejścia `(manifest.parent / path).resolve()`, zapis `resolved_path`, `manifest_path` bezwzględnie | brak | brak; symlink `cache/` zapisze docelową ścieżkę `/Volumes/...` w manifeście i w bazie |
| build.py:102,246 | `run/'build.sqlite'`, wynik `run.resolve()` | brak | brak |
| database.py:10–12 | `Path.resolve().as_uri()?mode=ro/rw/rwc` | brak; `ro`/`rw` na brakującym pliku daje błąd | jw. |
| reports.py:87,103 | `canonical_index`: `root=resolve()`, odrzuca symlink pliku i plik poza root | symlink katalogu nadrzędnego OK; symlink `reports/` lub `lists/` → błąd | brak |
| reports.py:321–329 | logical-content pomija `path`, `resolved_path`, `retrieved_at` | brak | brak |
| verify.py:88,149 | K10 i K1 czytają `inputs.manifest_path` (bezwzględny) | brak | brak; przeniesienie repo → K1 i K10 fail |
| verify.py:417 | K8: `run.resolve() == peer.resolve()` | podanie A przez symlink i przez ścieżkę docelową zostanie wykryte | brak |
| verify.py:599–604 | `verification/attempt-NNNN` względnie do przebiegu | brak | brak |
| export.py:63–67,141,169 | pieczęć: `manifest_core_sha256` (obejmuje `inputs` ze ścieżkami bezwzględnymi), `run_name=resolve().name`, `output_dir` bezwzględnie | brak; nazwa przebiegu bez zmian | nie przepisywać `inputs` w manifeście, bo złamie to pieczęć |
| export.py:125 | staging `mkdtemp(dir=target.parent)` | rodzic musi istnieć → głośny błąd | jw. |
| explain.py:49,267 | piny z `manifest_path`; wynik zawiera `sources` (metadane z `resolved_path`) i `stages` (czasy) | brak | po przeniesieniu repo pin → `pinned_file_unavailable` (degradacja, nie błąd) |
| pop.py:91–95 | `base['run_dir']` względem pliku pop-sources, nadpisywalne `--run-dir` | działa | trzeba podać `--run-dir`/`--release-dir` |
| pop00.py:389–394 | `base_run` = sha256 `run/manifest.json` | brak | brak (hash bajtów) |
| rule_docs.py:89 | tekst `--run-dir <przebieg>` | — | — |

### Konfiguracja
- `config/generator/sources.json`: `../../cache/...` (np. :12, :79), `../../config/...`, `../../.maister/...`, wszystko względem `config/generator/`. Działa przez symlink `cache/`; przeniesienie wymaga symlinku albo zmiany pinów, a zmiana pinów zmienia `manifest_sha256` (K1, K8 peer).
- `config/generator/evidence.json:15–121`: `cache/...` i `tmp/...` (względem innej bazy; poza buildem).
- `pop-sources.json:7–8`, `pop-sources-v29.json:7–8`: `run_dir`/`release_dir` = `../../data/work/...`.
- `pop00-sources.json:6–18` (4 piny) i `tematy-sources.json:6–30` (7 pinów) na `../../data/work/...`. Hashe pinów nie zależą od ścieżki, więc symlink wystarczy.
- `.gitignore:2–5`: `/cache/ /tmp/ /data/raw/ /data/work/`, patrz R1. `data/raw/` nie istnieje.

### Skrypty
- `scripts/build_pair.sh:7,12–15`: `cd` do repo, `run="data/work/$1-$stamp-$side"`, `.out.json`/`.err` obok przebiegu. Przy braku dysku przekierowanie zawodzi, build nie startuje, `rc=1` (głośno). Ścieżki dziś stałe, bez env.
- `scripts/resume_reports.py:5,43,55,101`: `--run-dir`, piny względem `--manifest`.
- Stałe ścieżki: `probe_resident_toponyms.py:7` (`data/work/import-20261004-1302`), `pilot_links.py:22,41` (`ROOT/cache/...`), `audit_kwjp.py:22` (`ROOT/cache/kwjp`), `audit_sgjp.py:25–26` (`mkdir cache`, temp w `cache`), `fetch_tematy_sources.py:29–30` (domyślne cele w `cache/`). Przez symlink `cache/` działają; przy env trzeba je zmienić.
- Tylko w docstringach: `measure_pop.py:5`, `rebase_sgjp_pin.py:5–7`, `build_plwordnet_db.py:5–6`.

### Testy
- Hermetyczne: `tmp_path`/`TemporaryDirectory` (155 wystąpień). Nie zależą od `data/work` ani `cache/`. Wyjątki czytają repo: `test_rebase_sgjp_pin.py:46` (`config/generator/sources.json`), `test_round4_sjp_fixes.py:38` (asercja pinu `../../config/...`). Testy symlinków: `test_reports.py:102`, `test_check_pop00_package.py:68`.
- Przeniesienie lub symlink nie wpływa na testy. Zmiana pinów `../../cache` w `sources.json` może wymagać poprawek w tych dwóch testach.

### Dokumentacja i skill
- `docs/plan-dalszych-prac-runbook.md:141,146,178,184`, `docs/runbook-zgloszenia.md:17,19,35,36`, `docs/generator/cli.md:23–27,53–172` (21 trafień), `docs/generator/wyjatki-dawnosci-standard.md:64`, `docs/odtwarzanie-audytu.md:5–63`, ADR-011:37–149, ADR-012:24,126,130, ADR-013:44,51, `mapowanie-kwjp.md:55`. Wszędzie są ścieżki względne `data/work/...`/`cache/...`, które zostają poprawne przy symlinku. Przy env/flagi trzeba je przepisać.
- `.claude/skills/zgloszenia-slow/SKILL.md`: żadnych ścieżek `data/work` ani `cache` (sprawdzone pełnym odczytem). Odsyła do `docs/runbook-zgloszenia.md` i wspomina `tmp/`.

## K1–K10 / K8 a ścieżki
- **K1** (verify.py:140–157): `inspect_sources(inputs['manifest_path'])` ponownie hashuje wejścia i porównuje `manifest_sha256` i `manifest`. Ścieżka przebiegu nie gra roli. Zapisany `manifest_path` jest bezwzględny, więc przeniesienie repo albo worktree = fail.
- **K7** (verify.py:357–374): hash wyniku `explain` z przeglądu. Wynik zawiera `stages.*.updated` i `sources[].resolved_path`, więc z natury jest związany z jednym przebiegiem. Ścieżka katalogu przebiegu do niego nie wchodzi.
- **K8** (verify.py:416–462): `tree_sha256` (nazwy i bajty plików pakietu), `git_dirty` tylko dla `literaki_slownik`, `canonical-index` (ścieżki względne, `excluded: local_paths, timestamps`, reports.py:119–121), logical-content bez ścieżek. Różne lokalizacje A i B (np. A wewnątrz, B na `/Volumes`) nie zmieniają wyniku. To samo dotyczy różnego położenia `cache/`, bo provenance ma tylko hashe.
- **Export i pieczęć** (export.py:58–100): `manifest_core_sha256` obejmuje `inputs` ze ścieżkami bezwzględnymi, ale tylko je porównuje. Ponowne przeliczenie nie zależy od miejsca przebiegu. Ręczna „migracja” ścieżek w manifeście złamie pieczęć.
- Dziś zapisane (v32-a): `manifest_path=<repo>/config/generator/sources.json`, `resolved_path` w `.../cache/...`, `export.output_dir=.../data/work/release-LL-PL-v31`. Pakiet wydania zapisuje tylko `run_name` (export.py:141).

## Zniknięcie dysku: co jest głośne, co ciche
| Sytuacja | Zachowanie |
|---|---|
| verify/explain/export na brakującym przebiegu | głośno: brak `manifest.json` (verify.py:584–587, explain.py:184–186, 277) |
| SQLite `ro`/`rw` na brakującym pliku | głośno: `unable to open` (database.py:11–12) |
| `build_pair.sh`, wiszący symlink | głośno: redirect zawodzi, `rc=1` |
| `build` przez wiszący symlink | głośno, ale mylący komunikat (R3) |
| `build` z bezwzględnym rootem na pustym, zapisywalnym `/Volumes/Data` | **po cichu** (R2) |
| utrata dysku w trakcie buildu | status `failed` może się nie zapisać (R4) |
| `cache/` jako symlink na zniknięty dysk | głośno: `Brak zwykłego pliku` w preflight lub K1 |
