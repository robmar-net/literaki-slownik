# Work Log

## 2026-11-23T11:04:42Z - Implementation Started

**Total Steps**: 95
**Task Groups**: 1–14 (fale: {1,2,3} → 4 → 5 → {6,10} → 7 → {8,9,11,12} → 13 → 14)

## Standards Reading Log

### Loaded Per Group
Repo nie ma `.maister/docs/standards/`; standardami są `AGENTS.md` repo, kontrakt `docs/generator/cli.md` i lista „Standards Compliance” planu.
- **Wszystkie grupy:** `AGENTS.md` (polski, brak sekretów/UUID/ścieżek domowych, skład słownika bez zmian, brak CI), stdlib + `unittest`.
- **Grupy 5–9, 11 (kody, CLI):** `docs/generator/cli.md` — JSON na stdout, błędy na stderr, kody wyjścia jako kontrakt.
- **Grupy 2, 6, 10 (zapis, baza):** ADR-020 (fullfsync), `canonical.write_bytes` jako wzorzec zapisu trwałego.
- **Grupa 13 (docs):** format ADR repo, `.maister/docs/INDEX.md`.
- **Grupa 14 (testy):** konwencje istniejących testów, test styku przez obie strony.

## 2026-11-23T11:05:57Z - Group 1 Complete
**Steps**: 1.1–1.3. **Tests**: tests.test_gitignore 2/2. **Files**: .gitignore (/logs), tests/test_gitignore.py.
**Standards**: plan Standards Compliance, AGENTS.md; discovered: GIT_* env stripped in test git calls.

## 2026-11-23T11:07:28Z - Group 2 Complete
**Steps**: 2.1–2.7. **Tests**: test_durable_write+test_build 18/18; regresja lifecycle/reports/export/cli 34/34. Mutacja except OSError → czerwony, przywrócone.
**Files**: canonical.py (write_bytes, F_FULLFSYNC z fallbackiem, fsync katalogu też F_FULLFSYNC, set_replace_guard), build.py (write_lists), tests/test_durable_write.py.
**Notes**: hak G3 przez canonical.set_replace_guard(fn) dla grupy 4.

## 2026-11-23T11:11:11Z - Group 4 Complete
**Steps**: 4.1–4.8. **Tests**: test_volume+test_durable_write 14/14; mutacja check_target → czerwony.
**Files**: literaki_slownik/volume.py, scripts/init_work_volume.py, tests/test_volume.py (canonical.py bez zmian).
**Operator (orkiestrator, decyzja właściciela)**: utworzony katalog roboczy na T7 (`<wolumen>/literaki-slownik/work`) i znacznik `.literaki-work-volume` w korzeniu wolumenu (init_work_volume.py, rc=0). UUID tylko w znaczniku.
**Notes**: kolejność resume i wpięcie check_fresh/activate dla grup 5 i 7 w raporcie grupy.

## 2026-11-23T11:19:23Z - Group 3 Complete
**Steps**: 3.1–3.9. **Tests**: test_measure_fullfsync+test_database 7/7.
**Pomiar T7**: commit OFF 4,14 ms, ON 17,57 ms; 3 051 commitów buildu v32 → narzut 0,0876% → **4B, FULLFSYNC_MODE='build'** (ADR-020). quick_check v32 (22 GB, ro, immutable) ok w 486 s; sha256/mtime bazy bez zmian. Katalog pomiaru usunięty.
**Files**: scripts/measure_fullfsync.py, tests/test_measure_fullfsync.py, database.py (stałe), docs/adr/ADR-020-fullfsync.md, verification/fullfsync-measurement.json.

## 2026-11-23T11:33:05Z - Group 5 Complete
**Steps**: 5.1–5.9. **Tests**: 13 modułów, 119/119 (74 s).
**Files**: run.py (create_run z work_root, pola manifestu, close_attempt, reguła resztek startu — ostrzejsza niż spec), build.py (check_fresh/activate/deactivate, exit_code), cli.py (--work-root, sqlite3.Error→4), database.py (tolerancja rollback/close), explain.py (stages = statusy), tests/test_run.py, tests/layout_helpers.py (nowy, poza listą), tests/test_run_layout.py, tests/test_exit_codes.py.
**Notes**: ResourceWarning z tests/test_durable_write.py:121 (grupa 2) — do domknięcia w grupie 14.

## 2026-11-23T11:44:11Z - Group 6 Complete
**Steps**: 6.1–6.8. **Tests**: 15 modułów, 147/147 (184 s).
**Porównanie z HEAD** (te same wejścia): logical-content.json i lists/*.txt identyczne bajtowo; różnią się tylko construction-candidates.json i decisions.json (usunięte new_*) i ich hashe w canonical-index — zamierzone.
**Files**: build.py (pętla etapów STAGE_RUNNERS, run_build/stage_context/record_failure, metryki z bazy, znaczniki .done), links.py (dwa DROP), tests/test_stage_loop.py, tests/test_report_markers.py.
**Notes**: constructions z full_constructions_pending kończy pending (dziś flaga zawsze False). Docstring create_links → grupa 13.

## 2026-11-23T11:47:53Z - Group 10 Complete
**Steps**: 10.1–10.9. **Tests**: promote_run+export+lifecycle+verify 41/41. Mutacje: warunek indeksu B i odmowa export → czerwone; os.path.exists w _guard nieobjęty (nadmiarowy).
**Files**: scripts/promote_run.py (S0–S4, lock, log, staging, rename_swap), export.py (rename_swap, on_work_volume → 5), tests/test_promote_run.py.
**Notes**: --peer opcjonalny; używa prywatnych canonical._full_sync/_sync_directory (do rozważenia w przeglądzie).

## 2026-11-23T11:54:55Z - Group 7 Complete
**Steps**: 7.1–7.7. **Tests**: 10 modułów, 60/60; harness 19 punktów przerwania (błąd I/O i os._exit), podwójne przerwanie, para wznowiony+świeży → VERIFIED. Mutacje reset_stage i restart_in_place → czerwone.
**Files**: build.py (reset_stage, guarded_build, resume, restart_in_place), run.py (first_incomplete, check_identity, begin_resume), cli.py (--resume), tests/test_resume.py, tests/test_resume_equivalence.py.
**Notes**: check_identity wymaga git_dirty is False (ostrzej niż stary resume_reports). Grupa 8: F_FULLFSYNC po reset_stage.

## 2026-11-23T11:55:18Z - Group 11 Complete
**Steps**: 11.1–11.6. **Tests**: test_clean_work 8/8; 8 mutacji → czerwone, przywrócone.
**Dry-run na repo**: NOTICE dostępny (50 hashy); 26 kandydatów wydań (~0,42 GB): pop-v1, v1r2, v1r3; tematy v1 (7 tematów + tematy-v1); tematy-matematyka-v2, tematy-medycyna-v2 (a/b). Potrzebne: LL-PL v29/v30/v31, pop-v2/v3, pop00, tematy v2/v3, tematy-wydanie-20261029. Nic nie skasowane.
**Notes**: pop00-v1-* remisują wersją → zawsze zostają (bezpieczna strona).

## 2026-11-23T11:59:43Z - Group 9 Complete
**Steps**: 9.1–9.9. **Tests**: test_build_supervised+test_resume_reports 15/15.
**Files**: scripts/build_supervised.py (nowy), scripts/build_pair.sh (LITERAKI_WORK_ROOT, 100 GB, logs/, caffeinate -dimsu), scripts/resume_reports.py (nakładka), tests/test_build_supervised.py, tests/test_resume_reports.py.
**Notes**: drugi nadzorca na tej samej blokadzie → 4; /usr/bin/time -l usunięte (peak_rss w performance.json).

## 2026-11-23T12:00:14Z - Group 8 Complete
**Steps**: 8.1–8.4. **Tests**: 28/28 + 20/20 sąsiednie; mutacja kolejności stage_durable → czerwony.
**Files**: database.py (connect build=True: DELETE/FULL/fullfsync ON; full_sync(db)), build.py (stage_durable na granicach etapów i po reset_stage), tests/test_durability_modes.py.
**Notes**: database.py używa prywatnego canonical._full_sync — do przeglądu; brak walidacji wartości FULLFSYNC_MODE.

## 2026-11-23T12:06:42Z - Group 12 Complete
**Steps**: 12.1–12.5. **Tests**: test_build_history 3/3; powtórka 6 modułów po fali (verify, export, lifecycle, promote_run, resume_equivalence, build_history) — wynik niżej w commit.
**Files**: verify.py (build_history, sekcja „Historia buildu”), export.py (source_run.build_history), tests/test_build_history.py.

## 2026-11-23T12:12:30Z - Group 13 Complete
**Steps**: 13.1–13.6. **Tests**: test_cli_docs+test_rule_docs 8/8.
**Files**: docs/adr/ADR-014..019, 021 (nowe), ADR-020 (uzupełnienie), docs/generator/cli.md, docs/plan-dalszych-prac-runbook.md, .maister/docs/INDEX.md, tests/test_cli_docs.py.

## 2026-11-23T12:42:07Z - Group 14 Complete
**Steps**: 14.1–14.5. **Tests**: +2 testy styku (promocja→clean_work, nadzorca + prawdziwe cli.main; obie mutacje czerwone), poprawka ResourceWarning w test_durable_write.
**Pełne zestawy**: tests 676/676 OK (392 s); scripts/test_audit_sgjp 5/5 OK. Sonda wycieków stanu globalnego: 0. Grep UUID/ścieżek: czysto (usunięta stara ścieżka domowa z runbooka, linia 108). .github/workflows brak; config/ bez zmian.
**Notes**: 5 ResourceWarning w testach sprzed #22 (test_links_structures, test_round5_zds, test_sjp_extra) — poza zakresem.

## 2026-11-23T12:42:07Z - Implementation Complete
**Total Steps**: 95/95. **Test Suite**: 676 + 5 OK. Commity: b53a6d4 … (grupy 1–14).

## 2026-11-23T16:33:06Z - Poprawki po weryfikacji (ostrzeżenia 1–12)
Decyzje właściciela: poprawić 1–12; klasa 6 nie kasuje kompletnego przebiegu czekającego na verify.
Zmiany: I/O na wolumenie → 75; blokada buildu `.<nazwa>.build.lock` obok symlinku; nadzorca pamięta marker_id; kasowanie przez `.<nazwa>.deleting` (wznawialne); watchdog `--stall-minutes` (mtime + czas CPU); jedna `volume.check_work_root`; walidacja FULLFSYNC_MODE; `workfs.py` i publiczne helpery canonical; runbook z `nohup … & disown`.
**Testy**: 694/694 OK (431 s) + 5/5 scripts. Każda zmiana zachowania: test czerwony → zielony.

## 2026-11-23T16:55:16Z - Poprawki po ponownym przeglądzie (N1–N8)
`repeated-75-healthy` (drugie zdrowe 75 w etapie → 4), `cputime-unknown`, `--resume` przez ścieżkę T7 → 4, `.deleting` nie jest wydaniem, lista skasowanych w JSON błędu, `age_days` dla klasy 3. **Testy**: 715/715 OK (415 s) + 5/5.
