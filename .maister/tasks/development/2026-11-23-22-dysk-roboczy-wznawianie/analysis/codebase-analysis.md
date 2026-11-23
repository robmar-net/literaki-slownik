# Raport analizy kodu

**Data**: 2026-11-23
**Zadanie**: #22: dysk roboczy na T7 i wznawianie budowy
**Opis**: Wdrożenie projektu z `analysis/research-context/high-level-design.md`: symlink `data/work` na dysk zewnętrzny (T7), strażnik wolumenu (G1 ismount, G2 znacznik, G3 st_dev), trwały zapis (F_FULLFSYNC i fsync katalogu), klasyfikator błędów na kody 75–78, `build --resume` per etap z `attempts[]` i `PRAGMA quick_check`, znaczniki per raport `reports/.done/`, nadzorca, pomiar fullfsync, historia w verify/export.
**Analizator**: codebase-analyzer (2 agenty Explore: Code Analysis, Context Discovery)

---

## TL;DR
- `build()` to jedna funkcja (`build.py:92-258`) bez punktów wznowienia. `create_run` odmawia przy istniejącym katalogu, a `set_stage` nadpisuje cały słownik etapu.
- Cztery zachowania psują zasadę „wznowiony = świeży” albo wywracają wznowienie. Bez ich naprawy K8 odrzuci wznowiony przebieg, a etap links padnie.
- Projekt wymaga trzech poprawek: `attempts[]` na poziomie głównym manifestu, ADR-y od numeru ADR-014 i odcięcie K7 od zmian w `stages`.
- Zapis nie jest trwały na zewnętrznym dysku: `write_json` robi samo `fsync`, bez F_FULLFSYNC i bez fsync katalogu; SQLite nie ma jawnych PRAGMA.
- Złożoność: duża (ok. 12 plików kodu i 7+ modułów testów). Ryzyko: średnio-wysokie.

## Key Decisions
- **`attempts[]` na poziomie głównym manifestu, nie w `stages`.** `set_stage` (`run.py:62`) zastępuje cały słownik etapu, a `complete_run` w testach (`tests/release_helpers.py:143`) też go nadpisuje. `manifest_core_sha256` (`verify.py:28-31`) i tak pieczętuje nowe klucze główne (zgodnie z ADR-008).
- **Numeracja ADR od ADR-014.** Lokalny dziennik decyzji projektu ma ADR-001..008. Ich nazwy kolidują z repozytoryjnymi ADR-006/007/008, a `docs/adr/` kończy się na ADR-013. Przy przenoszeniu do repo trzeba je przenumerować na ADR-014 i dalej.
- **K7 nie może widzieć `attempts`.** `explain.py:267` zwraca cały słownik `stages`, a K7 haszuje wynik explain (`verify.py:358-373`, `release_helpers.py:171-172`). Każda zmiana w `stages` po wznowieniu zmienia hasz przeglądu. Stąd decyzja o kluczu głównym, a `explain` nie powinien zwracać nic poza `.status` etapów. Trzeba to przypiąć testem.
- **Etapy jako funkcje według `STAGES`.** `build()` trzeba podzielić na funkcje kluczowane listą `run.py:9`, pomijane, gdy etap ma status `complete`. Nie warto dopisywać warunków do obecnego bloku.
- **Klasyfikator w istniejącym `except` (`build.py:249-258`).** `cli.py` nie potrzebuje nowej gałęzi, bo kod przechodzi przez `GeneratorError.code`.
- **`scripts/resume_reports.py` zostaje cienką nakładką** na nową pętlę raportów. Dziś duplikuje `build.py:201-235` i nie ma testów.

## Open Questions / Risks
- **Cztery zagrożenia dla zasady „wznowiony ≠ świeży”** (szczegóły w sekcji Key Findings). Każde wymaga zmiany kodu przed `--resume`.
- Wpis `source_artifact` `own-semantic-use-review-v1` dodawany przez decisions (`decisions.py:356`) trzeba kasować przy resecie decisions i wcześniejszych etapów. Inaczej preflight źle policzy `source_artifact`.
- Zapis do `stages`/`attempts` po verify zmienia `manifest_core_sha256`, więc export odmówi z kodem 5 (`export.py:63`). Wznowienie po VERIFIED/FROZEN musi być zabronione. `set_stage` już tego pilnuje (`run.py:60`).
- Nazwa `verification/attempt-NNNN` (`verify.py:565-576`) może się mylić z `attempts[]` budowy. Pole i katalog warto nazwać rozróżnialnie, np. `build_attempts`.
- `scripts/build_pair.sh:15` zapisuje logi (`.out.json`, `.err`) na dysku roboczym. Znikną razem z dyskiem, więc logi nadzorcy muszą trafiać na dysk wewnętrzny (np. `logs/`, którego dziś brak także w `.gitignore`).
- `.gitignore` ma `/data/work/` z ukośnikiem. Wzorzec obejmuje tylko katalogi, więc symlink `data/work` wyjdzie jako nieśledzony. Potrzebny wpis bez ukośnika i test `git check-ignore`.
- Bramka K8 sprawdza u partnera tylko `.status` etapów (`verify.py:441-452`). Brakuje testu „wznowiony + świeży partner → VERIFIED”.
- Brak testów kodów wyjścia `build` w CLI, mapowania `sqlite3.Error`/`OSError` na 4 i połykania błędu `set_stage(failed)` (`build.py:252`).

---

## Summary

Kod budowy jest liniowy i zakłada jeden nieprzerwany przebieg. Mechanizmy potrzebne do wznowienia są częściowo gotowe: atomowy `write_json`, `insert or ignore` w constructions/decisions, porównanie istniejących wierszy w decisions, kontrole w `resume_reports.py:44-52`. Główna praca to podział `build()` na etapy, idempotencja importów i links, liczniki niezależne od wznowienia, trwały zapis oraz strażnik i klasyfikator w jednym miejscu.

---

## Files Identified

### Primary Files

**`literaki_slownik/build.py`** (258 linii)
- Cały przebieg budowy, commity (`:24`, `:49`, `:106`, `:191`) i obsługa wyjątków `:249-258`.
- Tu trafiają: podział na etapy, klasyfikator, wywołanie strażnika, znaczniki `.done`.

**`literaki_slownik/run.py`** (63 linie)
- `STAGES` `:9`, `code_identity` `:16-37`, `create_run` `:40-51` (`exist_ok=False`, kod 4), `set_stage` `:54-63` (zastępuje słownik etapu).
- Tu trafiają: wariant otwarcia istniejącego przebiegu, `attempts[]`, ewentualnie kontrola strażnika przed zapisem.

**`literaki_slownik/canonical.py`** (44 linie)
- `write_json` `:33-44`: mkstemp, fsync `:40`, replace. Brakuje F_FULLFSYNC i fsync katalogu. Sprzątanie w `finally` (`:43-44`) może rzucić OSError i zasłonić pierwotny błąd.

**`literaki_slownik/database.py`** (29 linii)
- `connect` `:8-29`: PRAGMA `:14-18`, schema `:22`, commit/rollback `:24-26`. Rollback może rzucić na zniknięty dysk. Nie ustawia jawnie `journal_mode`, `synchronous` ani `fullfsync`.

**`literaki_slownik/links.py`** (415 linii)
- `create_links` `:130-165`: `CREATE TABLE` bez `IF NOT EXISTS` (`:132`), więc drugi przebieg pada. `executescript` commituje przed DDL.

**`literaki_slownik/verify.py`** (638 linii)
- Pieczęć `manifest_core_sha256` `:28-31`, K8 `:416-465`, bramka etapów `:590-595`, historia `:612-616`/`:633-638`.

**`literaki_slownik/export.py`** (174 linie)
- `changes_since_verify` `:58-99`, `release-manifest.json` `:135-151`. Historię budowy (`build_history`) najlepiej dopisać w `source_run` obok `code` (`:145`).

**`scripts/resume_reports.py`** (108 linii)
- Wznawia tylko raporty. Duplikuje `build.py:201-235` i nie ma testów.

### Related Files

**`literaki_slownik/cli.py`** (186 linii): parser `build` `:23-26`, kody wyjścia `:117-127`. Trzeba dodać `--resume`.
**`literaki_slownik/reports.py`** (554 linie): `canonical_index` `:79` z jawną listą `:91-95`, więc `.done/` nie wejdzie do K8.
**`literaki_slownik/explain.py`** (549 linii): `:187-188` czyta `import_sgjp.status`, `:267` zwraca całe `stages` (sprzężenie z K7).
**`literaki_slownik/constructions.py`**: `new_candidates` `:607`, `insert or ignore` `:520,530`, commity `:536,598`.
**`literaki_slownik/decisions.py`**: `new_analyses`/`new_decisions` `:432`, `insert or ignore` `:312-314`, porównanie istniejących `:298,334-336,347-349`, `source_artifact` `:356`.
**`literaki_slownik/inputs.py`**: `GeneratorError(message, code=3, …)` `:7-13`.
**`scripts/build_pair.sh`** (22 linie): dwa równoległe buildy, bez caffeinate i nadzorcy, logi na dysku roboczym.
**`docs/generator/cli.md`**: komendy `:18-41`, kody `:222-229` (dziś 0, 2, 3, 4, 5, 130).
**`docs/generator/publikacja.md:55`**, **`docs/adr/`** (ADR-006..013), **`.gitignore`**.

---

## Current Functionality

### Kluczowe funkcje

- **`build()`**: `inspect_sources` → `create_run` → preflight `complete` (`:101`), zanim powstanie baza (`:102`) → import sgjp/kwjp (`:107-121`) → luźne raporty `inventory.json`, `qualifier-conditions.json` (`:122-127`) → constructions (`:129-136`) → decisions z `write_lists` (`:137-179`) → links bez statusu `running` (`:182-200`) → reports (`:201-235`) → ponowne sprawdzenie manifestu (`:237-239`) → `performance.json`, `canonical-index.json` poza blokiem `with` (`:243-244`).
- **`flush()`** `:21-25`: `executemany` i commit co 10 000 wierszy.
- **`import_sgjp`** `:28-56`: zwykłe INSERT-y w partiach, tabele pochodne, jeden commit `:49`. Awaria zostawia zacommitowane partie `sgjp_record` bez tabel pochodnych.
- **`write_lists`** `:76-89`: `Path.write_bytes` (`:85`), nieatomowy i bez fsync.
- **Obsługa wyjątków** `:249-258`: łapie `BaseException`, próbuje `set_stage(failed)` i ignoruje OSError. Przepuszcza KeyboardInterrupt i GeneratorError, a OSError, `sqlite3.Error` i ValueError zamienia na GeneratorError z kodem 4.

### Przepływ danych

Źródła (`config/generator/sources.json`) → `build.sqlite` (12 tabel schematu, `user_version=2`, oraz tabele links tworzone w trakcie) → raporty JSON w `reports/` → `canonical-index.json` (K8). Manifest `manifest.json` zbiera stan etapów, `verify` go pieczętuje, `export` zamraża.

### Idempotencja obecnych etapów

| Etap | Zachowanie przy powtórce | Potrzebne |
|---|---|---|
| preflight | INSERT na PK → IntegrityError | sprawdzić kompletność, pominąć |
| import_sgjp | partie zostają, UNIQUE → IntegrityError | DELETE tabel etapu i późniejszych |
| import_kwjp | UNIQUE na `corpus_evidence` | DELETE tabel links, potem `corpus_evidence` |
| constructions | `insert or ignore`, działa | stały licznik zamiast `new_candidates` |
| decisions | `insert or ignore` z porównaniem wierszy, działa | stałe liczniki, atomowy `write_lists` |
| links | `CREATE TABLE` → „already exists” | `DROP TABLE IF EXISTS`, status `running` |
| reports | nadpisywanie plików | znaczniki `.done` per raport |

Bezpieczna kolejność DELETE: evidence_candidate, evidence_link, variant_decision, decision_payload, analysis, derivation_component, derivation_candidate, interpretation, lexeme, surface_form, sgjp_record, corpus_evidence. Do tego wiersz `source_artifact` z decisions.

---

## Dependencies

### Imports
- `sqlite3` (Python 3.15.2: `sqlite_errorcode`/`sqlite_errorname` są dostępne), `os`, `hashlib`, `tempfile`, `pathlib`, `subprocess` (git w `code_identity`).
- Wewnętrzne: `run`, `database`, `canonical`, `inputs`, `constructions`, `decisions`, `links`, `reports`, `quality`.

### Consumers stanu etapów manifestu
- **`run.py:50,62`**: tworzy i zapisuje etapy.
- **`build.py:194,245-248`**: status constructions, readiness.
- **`verify.py:445,590-592`**: bramka etapów i partner K8.
- **`explain.py:187-188,267`**: status importu, całe `stages` w wyniku (wpływa na K7).
- **`scripts/resume_reports.py:45-48,100-103`**.
- Testy: `test_build.py`, `test_run.py:18`, `test_lifecycle.py:63-65,78`, `test_verify.py:248`, `test_explain.py:370`, `test_standard_age_exceptions.py:418`, `test_standard_exclusions.py:275`, `release_helpers.py:143`, minimalne manifesty w `test_documented_names.py:68`, `test_spelling_variants.py:83`, `test_semantic_uses.py:100`, `test_resident_uses.py:42`.

**Consumer Count**: ok. 6 modułów kodu i 12 plików testów.
**Impact Scope**: wysoki. Kształt manifestu czyta verify, export, explain i testy.

---

## Test Coverage

### Test Files
- **`tests/test_build.py`**: awaria po zacommitowanej partii `:151`, awaria constructions zachowuje import `:201`.
- **`tests/test_lifecycle.py`**: awaria `import_kwjp` → `failed` `:50-73`, ręczny `running` → verify odmawia `:75`, pełny dysk (OSError 28) przy exporcie `:84`, `:100`.
- **`tests/test_run.py`**, **`tests/test_database.py`**, **`tests/test_cli.py`** (tylko inspect-sources 0/3 i argparse 2, `:10-30`).
- **`tests/test_verify.py`**, **`tests/test_export.py`**: odmowa fixture z kodem 5 (`:69`, `:125`), K8 nie porównuje `created` ani `performance.json` (`test_verify.py:114`).
- Pomocnicze: `tests/helpers.py` (`fixture_manifest`, `rewrite`), `tests/release_helpers.py` (`complete_run` nadpisuje etapy, `complete_pair` z dwoma prawdziwymi buildami w 0,29 s).

### Coverage Assessment
- **Liczba testów**: 46 w sześciu modułach (13,4 s), 63 pliki `test_*.py`, stdlib `unittest`.
- **Luki**: brak testów dla `--resume`, `.done`, `attempts`, kodów 75–78, strażnika, `quick_check` i fullfsync. Bez testów są też: kody wyjścia `build` w CLI, mapowanie `sqlite3.Error`/OSError na 4, połykanie błędu `set_stage(failed)`, `resume_reports.py`, `build_pair.sh`, `git check-ignore` dla symlinku i para „wznowiony + świeży” → VERIFIED. Prawdziwy build fixture nigdy sam nie dochodzi do kompletu etapów.
- Testy dokumentacji: tylko `tests/test_rule_docs.py:13`. Żaden test nie pilnuje `cli.md`.

---

## Coding Patterns

- **Nazwy**: funkcje i moduły `snake_case`, etapy jako napisy z `STAGES`, raporty `kebab-case.json`.
- **Styl**: funkcyjny, moduły bez klas, błędy jako `GeneratorError(message, code)` z `.diagnostic()`.
- **Stan**: manifest JSON zapisywany przez `write_json`. SQLite przez menedżer kontekstu `connect`.
- **Kody wyjścia**: wszystkie przez `GeneratorError.code` w `cli.py:117-120`.

---

## Complexity Assessment

| Czynnik | Wartość | Poziom |
|---|---|---|
| Rozmiar plików | `build.py` 258, `verify.py` 638, łącznie ~2500 linii w zasięgu | Średni |
| Zależności | ok. 10 modułów wewnętrznych i stdlib | Wysoki |
| Konsumenci | ok. 18 plików (kod i testy) czytających `stages` | Wysoki |
| Pokrycie testami | build/lifecycle częściowe, wznawianie brak | Niskie–średnie |

### Ogólnie: złożone

Zmiana dotyka kontraktu manifestu (pieczęć, K7, K8, export) i semantyki każdego etapu. Wymaga też niskopoziomowego I/O (F_FULLFSYNC, st_dev) na macOS.

---

## Key Findings

### Cztery zagrożenia dla zasady „wznowiony ≠ świeży”

1. **Liczniki „wstawione w tym przebiegu”.** `construction-candidates.json` ma `new_candidates` (`constructions.py:607`), a `decisions.json` ma `new_analyses`/`new_decisions` (`decisions.py:432`). Po wznowieniu wartości są mniejsze, a oba pliki są w `canonical_index`, więc K8 wykaże różnicę. **Poprawka:** liczyć stan bazy (`SELECT count(*)`) albo usunąć te pola z raportów kanonicznych.
2. **`import-counts.json` z pamięci.** Słownik `counts` (`build.py:99,116`) traci liczby sgjp, gdy import_sgjp zostaje pominięty. Ten sam problem ma `performance.json`, ale jest wyłączony z indeksu. **Poprawka:** przeliczać liczniki z bazy albo zapisywać je w etapie i czytać przy pominięciu.
3. **Luźne raporty między etapami.** `inventory.json` i `qualifier-conditions.json` powstają w `build.py:122-127`, po zakończeniu import_kwjp, a przed constructions. Awaria w tym miejscu zostawia je niezapisane, a wznowienie je pomija. **Poprawka:** przenieść je do etapu (koniec import_kwjp albo początek constructions) z własnym znacznikiem.
4. **Tabele links bez idempotencji.** `CREATE TABLE` (`links.py:132`) przy powtórce pada z „already exists”. `executescript` commituje DDL, nawet gdy INSERT-y (commit dopiero `build.py:191`) przepadły. **Poprawka:** `DROP TABLE IF EXISTS` przed utworzeniem i status `running` dla links.

### Poprawki projektu wynikające z analizy
- `attempts[]` na poziomie głównym (powód: `set_stage` i `complete_run` nadpisują etap). Pieczęć i tak je obejmuje.
- ADR-y projektu od ADR-014 (kolizja z repozytoryjnymi ADR-006/007/008).
- Odcięcie K7: `explain` nie może zwracać nic z etapów poza `.status`, inaczej wznowienie zmieni hasz przeglądu. Potrzebny test przypinający.

### Strengths
- Atomowy `write_json` w jednym miejscu, więc trwałość da się dodać centralnie.
- Constructions i decisions są już idempotentne (`insert or ignore`, porównanie wierszy, odmowa z kodem 4 przy różnicy).
- `canonical_index` ma jawną listę plików, więc `.done/` nie wycieknie do K8.
- `resume_reports.py:44-52` ma gotowe kontrole tożsamości kodu i wejść.

### Concerns
- Preflight dostaje `complete` przed utworzeniem bazy (`build.py:101-102`).
- Rollback i sprzątanie w `finally` mogą zasłonić pierwotny błąd zniknięcia dysku.
- `sqlite3.Error` nie jest łapany w CLI. Jeśli ominie `build`, kończy się tracebackiem z kodem 1.

### Opportunities
- Jeden moduł strażnika (G1–G3) wołany przed `create_run`, na starcie wznowienia, w `except` i w `set_stage`.
- Wspólny atomowy zapis bajtów dla `write_json` i `write_lists`.

---

## Impact Assessment

- **Główne zmiany**: `build.py`, `run.py`, `canonical.py`, `database.py`, `links.py`, `cli.py`, nowy moduł strażnika (i klasyfikatora).
- **Powiązane**: `constructions.py`, `decisions.py`, `explain.py`, `verify.py` (historia), `export.py` (`build_history`), `scripts/resume_reports.py`, `scripts/build_pair.sh` (nadzorca, caffeinate, logi poza T7), `.gitignore`, `docs/generator/cli.md` (kody 75–78, `--resume`), `docs/adr/ADR-014+`.
- **Testy**: nowe testy wznowienia per etap, klasyfikatora, strażnika, `.done`, K7/K8 dla pary wznowiony+świeży i kodów wyjścia CLI. Do tego aktualizacja `release_helpers.complete_run`, żeby nie kasowała `attempts`.

### Risk Level: średnio-wysokie

Wysoki fan-out kształtu manifestu, wpływ na pieczęć i dwa kryteria weryfikacji (K7, K8). Do tego I/O zależne od platformy, którego testy w CI nie odtworzą (zniknięcie dysku trzeba symulować).

---

## Recommendations

Modyfikacja istniejącego kodu i nowe możliwości:

1. **Najpierw naprawić cztery zagrożenia** (liczniki, `import-counts`, luźne raporty, links DDL) jako osobną grupę z testem „przebieg przerwany i wznowiony daje `canonical-index.json` identyczny ze świeżym”.
2. **Podzielić `build()`** na funkcje etapów według `STAGES`. Wznowienie robi wariant `create_run` bez `mkdir`, który sprawdza `tree_sha256`, `git_dirty`, `inputs.manifest_sha256`, znacznik wolumenu oraz brak VERIFIED/FROZEN. Potem `connect(create=False)` i `PRAGMA quick_check` (wynik ≠ `ok` → 77). Etap `running` z poprzedniej próby trzeba zamknąć jako `failed` z wynikiem `interrupted` i zresetować jego tabele i tabele późniejszych etapów.
3. **`attempts[]` na poziomie głównym**: dopisywać przy `create_run` i wejściu wznowienia, zamykać w `except` i po sukcesie.
4. **Trwałość**: w `write_json` F_FULLFSYNC przez `fcntl` z fallbackiem na `fsync`, fsync katalogu po `replace` i sprzątanie połykające OSError. Wspólny zapis atomowy także dla `write_lists`. W `connect` jawnie `journal_mode=DELETE`, `synchronous=FULL`, `fullfsync`/`checkpoint_fullfsync`, z pomiarem kosztu.
5. **Klasyfikator w `build.py:249-258`**: `sqlite_errorname` IOERR/CANTOPEN → decyzja strażnika (75 albo 4), FULL → 78, NOTADB/CORRUPT → 77. Errno ENOSPC/EDQUOT → 78, EIO/ENXIO/ENODEV/ENOENT/EROFS → strażnik. Nieudany rollback i nieudany `set_stage(failed)` nie mogą zasłonić klasy błędu.
6. **Znaczniki `.done`** wokół każdego `write_json` raportu (`build.py:205,208,216,219,226,229,233`). Przy pominięciu `unresolved` wczytywać z `reports/unresolved.json`. `resume_reports.py` przerobić na nakładkę.
7. **Testy przypinające**: K7 bez zmian po wznowieniu, para wznowiony+świeży → VERIFIED, `git check-ignore data/work` dla symlinku, kody wyjścia `build` w CLI.

---

## Next Steps

Uruchomić gap-analyzer na tym raporcie i `high-level-design.md`. Do projektu trzeba wnieść trzy poprawki (`attempts[]` na poziomie głównym, ADR-014+, odcięcie K7) i cztery zagrożenia jako wymagania specyfikacji.
