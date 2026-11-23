# Kontrola kompletności: #22 (build na T7 z wznawianiem)

## TL;DR
Wynik: **passed_with_issues**. Plan jest wykonany w 100%: 95 kroków i 14 grup, wszystkie odhaczone w `.md` i `.html`. Kod i testy są dla każdej grupy. R1–R13 mają kod i testy o nazwach z kolumny „Test” w spec. Standardy są zachowane. Są 1 ostrzeżenie i 5 uwag (info). Żadna nie blokuje.

## Key Decisions
- Liczę 95 kroków `N.M`. Wiersze `N.0` to nagłówki grup: razem 109 pól `[x]`, 0 `[ ]`.
- Standardy: repo nie ma `.maister/docs/standards/`. Jako standardy biorę `AGENTS.md`, kontrakt `docs/generator/cli.md` i listę z sekcji „Standards Compliance” w planie.
- Zasada wiki z `AGENTS.md` nie dotyczy #22. Kryteria, wersje list, źródła ani wydania się nie zmieniają.

## Open Questions / Risks
- `FULLFSYNC_MODE` nie jest walidowana. `database.py:37` sprawdza `== 'build'`, a `build.py:40` sprawdza `== 'stage_boundaries'`. Literówka w stałej wyłączy więc `fullfsync` w etapie i synchronizację na granicach, bez żadnego błędu. Ryzyko jest małe, bo to stała w kodzie.

## 1. Plan
| Grupa | Kroki | Dowód w kodzie (wybrane) |
|---|---|---|
| 1 | 3/3 | `.gitignore` `/logs`, `tests/test_gitignore.py` |
| 2 | 7/7 | `canonical.py` `write_bytes`, `set_replace_guard`; `tests/test_durable_write.py` |
| 3 | 9/9 | `scripts/measure_fullfsync.py`, `verification/fullfsync-measurement.json`, ADR-020 |
| 4 | 8/8 | `volume.py`: `mount_point`, `check_fresh`, `check_resume`, `find_by_marker`, `activate`, `check_target` |
| 5 | 9/9 | `run.py` `build_attempts`, `close_attempt`; `tests/test_exit_codes.py`, `tests/test_run_layout.py` |
| 6 | 8/8 | `build.py` `STAGE_RUNNERS`, `reports/.done`; `links.py` z dwoma DROP |
| 7 | 7/7 | `build.py` `reset_stage`, `resume`, `restart_in_place`; 19 punktów przerwania w `test_resume_equivalence.py` |
| 8 | 4/4 | `database.py` `FULLFSYNC_MODES`, `build.py` `stage_durable` |
| 9 | 9/9 | `scripts/build_supervised.py`, `build_pair.sh`, `resume_reports.py` (nakładka) |
| 10 | 9/9 | `scripts/promote_run.py` (S0–S4), `export.py` odmawia 5 na T7 |
| 11 | 6/6 | `scripts/clean_work.py`, 9 testów |
| 12 | 5/5 | `verify.py:34` `build_history`, `export.py:172` |
| 13 | 6/6 | ADR-014..021, `cli.md`, runbook, `INDEX.md` |
| 14 | 5/5 | 2 testy styku, pełny zestaw 676 + 5 OK (wg work-log) |

Kontrole repo z kroku 14.5 powtórzone: brak UUID i `/Users/` w zmienionych plikach i w artefaktach zadania, brak `.github/`, `config/` bez zmian.

## 2. Standardy
| Standard | Dotyczy? | Wynik |
|---|---|---|
| `AGENTS.md`: po polsku, zwięźle | tak | spełniony (ADR, cli.md, runbook, komentarze) |
| `AGENTS.md`: bez sekretów, repo publiczne (bez UUID i ścieżek domowych) | tak | spełniony (grep czysty, `test_cli_docs` pilnuje ADR) |
| `AGENTS.md`: artefakty Maister w `.maister/`, dane robocze w `.gitignore` | tak | spełniony (`/logs`, `/data/work/`) |
| `AGENTS.md`: zmiana składu słownika po rozmowie z użytkownikiem | tak | nic się nie zmienia (`config/` bez zmian) |
| `AGENTS.md`: aktualizacja wiki | nie | brak zmian kryteriów, list i wydań |
| `cli.md`: JSON na stdout, błędy na stderr, kody jako kontrakt | tak | spełniony (nowe skrypty używają `json.dumps` i `sys.stderr`, kody 75–78 opisane) |
| stdlib, `unittest`, `GeneratorError(message, code)` | tak | spełniony |
| Bez CI (tylko self-hosted) | tak | spełniony (brak `.github/`) |

## 3. Dokumentacja
- Work-log ma 14 wpisów grup z datą, plikami, testami i mutacjami, plus wpis końcowy (95/95, 676 + 5).
- Spec R1–R13 pokrywa się z kodem. Dwa odstępstwa na ostrzejszą stronę, oba opisane: resztka startu (`run.py:42`, `cli.md:56`) i czysty `git` przy `--resume` (ADR-016:18).
- R13: `cli.md` opisuje `--resume`, `--work-root`, 75–78, nowe skrypty i kody `resume_reports.py` (`cli.md:99`). `INDEX.md` ma wpisy ADR-014..021 i zadania.

## Uwagi
| # | Waga | Miejsce | Opis | Do poprawy |
|---|---|---|---|---|
| 1 | warning | `implementation/work-log.md` | Sekcja „Standards Reading Log / Loaded Per Group” to wciąż szablon. Standardy wymienia tylko wpis grupy 1. | tak |
| 2 | info | `literaki_slownik/database.py:11-12,37`, `build.py:40` | `FULLFSYNC_MODE` bez walidacji względem `FULLFSYNC_MODES` (zob. ryzyka) | tak |
| 3 | info | `database.py:7`, `scripts/promote_run.py:75,80,212` | Prywatne `canonical._full_sync` i `_sync_directory` używane poza modułem. Work-log oddał to do przeglądu, sprawa otwarta. | tak |
| 4 | info | `implementation-plan.md`, „Standards Compliance” | Plan powołuje się na `.maister/docs/standards/`, a ten katalog nie istnieje | tak |
| 5 | info | `work-log.md`, wpis grupy 12 | „wynik niżej w commit” bez liczby testów powtórki | tak |
| 6 | info | `tests/test_clean_work.py` | Nazwy testów po polsku, w pozostałych modułach po angielsku | tak |

Poza zakresem: 5 `ResourceWarning` w testach sprzed #22 (`test_links_structures`, `test_round5_zds`, `test_sjp_extra`).
