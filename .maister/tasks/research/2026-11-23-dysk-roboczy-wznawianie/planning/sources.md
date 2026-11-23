# Źródła badania

## TL;DR
Źródła istnieją i zostały sprawdzone (2026-11-23). Kod: 6 modułów (~1,8 tys. wierszy) + `run.py`, `canonical.py`, `resume_reports.py`, `build_pair.sh`. Dane: `data/work/` (147 pozycji, jeden przebieg z bazą 22,0 GB). Zewnętrzne: dokumentacja SQLite i Apple.

## Open Questions / Risks
- `lists-v32-20261104-161601-a.out.json` i `.err` mają 0 B; czasy v32 tylko z `manifest.json`. Pełne `.err` (z `/usr/bin/time -l`) mają v27, v29, v30 a/b, v31 a/b (np. v31-a: `49551.59 real` ≈ 13,8 h, RSS 1,18 GB).

## Kod (kategoria codebase-build)
- `literaki_slownik/build.py` (258 w.) — kolejność etapów, `flush`/`commit`, `set_stage`, `performance`.
- `literaki_slownik/run.py` (63 w.) — `STAGES` (`preflight, import_sgjp, import_kwjp, constructions, decisions, links, reports`), `create_run` (odmowa przy istniejącym katalogu), `set_stage`, `code_identity` (K8).
- `literaki_slownik/database.py` (29 w.) — `connect`: `cache_size` 4 GB, `temp_store=MEMORY`; brak `journal_mode`/`synchronous`.
- `literaki_slownik/schema.sql` (81 w.) — tabele; przypisanie do etapów.
- `literaki_slownik/canonical.py` — `write_json`/`load_json` (atomowość zapisu manifestu).
- `literaki_slownik/verify.py` (638 w.) — K1–K10, `--peer-run`, katalog `verification/attempt-NNNN`.
- `literaki_slownik/export.py` (174 w.), `literaki_slownik/explain.py` (549 w.) — co czytają z przebiegu.
- `literaki_slownik/cli.py`, `literaki_slownik/reports.py` — opcje `--run-dir`, ścieżki raportów.
- `scripts/resume_reports.py` — istniejące wznawianie etapu `reports` (#16).
- `scripts/build_pair.sh` — para A/B, `data/work/PREFIKS-STAMP-{a,b}`, `.out.json`/`.err`, odmowa przy dirty (K8).

## Dane przebiegów (tylko odczyt)
- `data/work/lists-v32-20261104-161601-a/` — `build.sqlite` (22 035 492 864 B, r--r--r--), `manifest.json` (`readiness: FROZEN`, `stages.*.updated`, `export`, `verification`), `lists/`, `reports/`, `verification/attempt-0001/`.
- `data/work/lists-v{24,25,27,28,29,30,31,32}-*-{a,b}.{out.json,err}` — wyniki `build --json` i `/usr/bin/time -l`.
- `data/work/{export,verify}-v31*.{out.json,err}`, `verify-v32.*` — czasy verify/export.
- Pozostałe katalogi (`pop-*`, `tematy-*`, `release-LL-PL-v*`, `fala-1-*`) — kontekst innych czytników `data/work`.

## Ścieżki i powtarzalność (kategoria codebase-paths)
Pliki z trafieniem `data/work`/`cache/`/`run_dir`/`--run-dir` (grep 2026-11-23):
- Kod: `literaki_slownik/{build,cli,export,verify,explain,reports,pop,pop00,rule_docs}.py`.
- Skrypty: `scripts/{build_pair.sh,resume_reports.py,measure_pop.py,benchmark_sjp.py,sjp_missing_top.py,sjp_extra_top.py,pilot_links.py,rebase_sgjp_pin.py,fetch_tematy_sources.py,build_plwordnet_db.py,audit_kwjp.py,probe_resident_toponyms.py}`.
- Testy: `tests/{test_lifecycle,test_verify,test_explain,test_explain_pop,test_explain_pop00,test_pop,test_export,test_measure_pop}.py`, `tests/{pop_helpers,tematy_helpers}.py`.
- Konfiguracja: `config/generator/{sources,evidence,pop-sources,pop-sources-v29,pop00-sources,tematy-sources}.json`, `.gitignore` (`/cache/`, `/data/work/`, `/tmp/`, `/data/raw/`).
- Dokumentacja: `docs/plan-dalszych-prac-runbook.md`, `docs/generator/{cli,publikacja,reguly,mapowanie-kwjp,wyjatki-dawnosci-standard}.md`, `docs/{runbook-wiki,runbook-zgloszenia,odtwarzanie-audytu}.md`, `docs/adr/ADR-01{1,2,3}-*.md`.
- Skill: `.claude/skills/zgloszenia-slow/` (sprawdzić ręcznie; pierwszy grep nic nie zwrócił — potwierdzić innym wzorcem).
- `cache/` (870 MB: `plwordnet` 562 MB, `iate` 108 MB, `kwjp` 85 MB, `sgjp` 81 MB, `nkjp` 22 MB) — mały, może zostać na dysku wewnętrznym.
- `AGENTS.md`, `README.md` — reguły repo (repo publiczne: bez prywatnych ścieżek).

## Środowisko (odczyt)
- `mount`: `/dev/disk10s2 on /Volumes/Data (apfs, local, nodev, nosuid, journaled, noowners)`.
- `diskutil info /Volumes/Data`: USB, External, SSD, Removable Media: Fixed.
- `pmset -g`: `disksleep 0`.
- `/Volumes/Data` zawiera `.DocumentRevisions-V100-bad-1` (ślad wcześniejszego problemu wolumenu — do odnotowania).

## Zewnętrzne (kategoria external)
- SQLite: https://www.sqlite.org/atomiccommit.html, https://www.sqlite.org/wal.html, https://www.sqlite.org/howtocorrupt.html, https://www.sqlite.org/pragma.html#pragma_synchronous, https://www.sqlite.org/pragma.html#pragma_fullfsync, https://www.sqlite.org/lang_attach.html, https://www.sqlite.org/backup.html, https://www.sqlite.org/lang_vacuum.html (`VACUUM INTO`).
- Python: https://docs.python.org/3/library/os.html#os.replace, `os.path.ismount`, `os.fsync`; `fcntl.F_FULLFSYNC` (macOS).
- Apple: `man diskutil`, `man pmset`, `man fsync` (F_FULLFSYNC), DiskArbitration (https://developer.apple.com/documentation/diskarbitration); zachowanie `/Volumes/<nazwa>` po odłączeniu (pusty katalog / `Data 1`).
- Wzorce: checkpointy etapów w narzędziach potokowych (Make/Snakemake/DVC: wyjście per etap, rename atomowy, hash wejść).
