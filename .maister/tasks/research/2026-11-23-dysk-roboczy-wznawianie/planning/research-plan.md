# Plan badania: dysk roboczy i wznawianie buildu

## TL;DR
Badanie techniczne: analiza kodu (stan buildu, ścieżki) + praktyki zewnętrzne (SQLite przy utracie urządzenia, wznawianie potoków, wykrywanie odmontowania na macOS).
3 zbieracze: `codebase-build`, `codebase-paths`, `external`. Tylko odczyt: bez buildów, bez usuwania i przenoszenia plików.
Wynik: mapa etapów (czas, rozmiar, gdzie trwały stan), 2–4 warianty lokalizacji i 2–4 wznawiania z kosztem i ryzykiem, rekomendacja z kolejnością kroków.

## Key Decisions
- **Typ: technical (z elementem literatury).** Odpowiedź leży głównie w kodzie i logach; zewnętrzne źródła tylko do zachowania SQLite/macOS i wzorców checkpointów.
- **3 zbieracze, nie 4.** Konfiguracja (`config/generator/*.json`, `.gitignore`) wchodzi do `codebase-paths`; mniej nakładania.
- **Punkt wyjścia wznawiania: istniejący mechanizm.** `run.py` już zapisuje status etapów w `manifest.json` (`STAGES`, `set_stage`), a `scripts/resume_reports.py` wznawia tylko `reports`. Badamy uogólnienie, nie projekt od zera.
- **Pomiary tylko z istniejących artefaktów** (`manifest.json` → `stages.*.updated`, `*.err` z `/usr/bin/time -l`, `performance.json`, `du`/`ls -l`).

## Open Questions / Risks
- `lists-v32-*-a` ma etapy rozciągnięte na 4 dni (decisions 2026-11-04 → 2026-11-07), a `.out.json`/`.err` są puste: prawdopodobnie przebieg wznawiany. Trzeba to ustalić z logów/historii zadań, zanim użyjemy go jako miary czasu.
- Zapis `manifest.json` przez `write_json`: nie wiadomo, czy jest atomowy (tmp + rename + fsync). Do sprawdzenia w `canonical.py`.
- `database.py` nie ustawia `journal_mode` ani `synchronous` (domyślnie DELETE/FULL). Wpływ na odporność i czas do zmierzenia w literaturze, nie budową.
- Przyczyna znikania `/Volumes/Data` nieznana; `pmset disksleep` = 0 już teraz, więc trop uśpienia dysku jest słabszy (zasilanie/kabel/hub USB).
- K8 (`code_identity`) hashuje `*.py` pakietu i stan git: zmiana ścieżek w kodzie zmienia tożsamość kodu, symlink nie.

## 1. Przegląd
**Pytanie:** jak trzymać `data/work/*/build.sqlite` (~21 GB/przebieg, para A/B ~44 GB, ~14 h) na `/Volumes/Data` (USB, APFS, znika) i jak wznawiać przerwany build bez pracy od zera.

**Podpytania:**
1. Lokalizacja: konfiguracja ścieżki vs symlink `data/work` vs zmienna środowiskowa; co się psuje (kod, testy, skrypty, runbooki, skill `zgloszenia-slow`, `explain`); jak wykryć brak dysku od razu (zamiast pustego katalogu w `/Volumes`).
2. Wznawianie: od którego etapu/części; checkpoint w `manifest.json` vs baza per etap; atomowe zapisy; kontrola spójności po wznowieniu (`PRAGMA integrity_check`, hash).
3. Powtarzalność: K1–K10 w `verify.py`, `--peer-run` A/B, hashe w manifeście, K8 czysty kod, ścieżki zapisane w manifeście.

**Zakres:** jak w briefie. Poza: polityka słownika, nowe buildy, CI.

## 2. Metodologia
- **Główna:** czytanie kodu i śledzenie przepływu stanu (`build.py` → `run.py`/`database.py` → `verify.py`/`export.py`/`explain.py`), inwentaryzacja ścieżek (`grep`), odczyt metadanych przebiegów.
- **Pomocnicza:** dokumentacja SQLite (atomic commit, WAL, `synchronous`, „How to corrupt”), dokumentacja Apple (`diskutil`, `pmset`, DiskArbitration), wzorce checkpointów potoków.
- **Rama analizy:** (a) komponenty i trwały stan per etap; (b) koszt powtórzenia etapu (czas, rozmiar); (c) wpływ wariantu na każdy czytnik ścieżki; (d) wpływ na K1–K10; (e) macierz wariant × koszt zmiany × ryzyko.
- **Fallback:** gdy logi nie dają czasu etapu, użyć `stages.*.updated` z manifestów kilku przebiegów (v27–v32, pary a/b) i `performance.json`.

## 3. Źródła
Pełna lista: `planning/sources.md`.

## 4. Fazy
1. **Odkrycie:** lista przebiegów w `data/work/`, rozmiary (`ls -l`, bez `du` całego dysku jeśli wolne), pliki per przebieg; `grep` po `data/work`, `cache/`, `run_dir`, `--run-dir`, `/Volumes`.
2. **Czytanie:** `build.py`, `run.py`, `database.py`, `schema.sql`, `canonical.py` (`write_json`), `verify.py` (K1–K10), `export.py`, `explain.py`, `scripts/resume_reports.py`, `scripts/build_pair.sh`.
3. **Pogłębienie:** które tabele pisze który etap (granice etapów w `schema.sql`), co etap czyta z poprzednich, gdzie są `commit()`; czy etap jest idempotentny; co trzyma ścieżki absolutne/względne w manifeście; zachowanie SQLite przy zniknięciu urządzenia w trakcie zapisu.
4. **Weryfikacja:** krzyżowo czasy z `.err` (`real`) vs `stages.*.updated`; testy (`tests/test_lifecycle.py`, `test_verify.py`, `test_build.py`) potwierdzają semantykę statusów; każde twierdzenie z plikiem i linią.

## Gathering Strategy

### Instances: 3

| # | Category ID | Focus Area | Tools | Output Prefix |
|---|------------|------------|-------|---------------|
| 1 | codebase-build | Etapy buildu, trwały stan (manifest, baza, raporty), rozwiązywanie `run-dir`/`cache`, co czytają `verify`/`explain`/`export`, czasy i rozmiary z `data/work/*.out.json`, `*.err`, manifestów, `performance.json`; istniejące wznawianie (`resume_reports.py`) | Read, Grep, Bash (tylko odczyt: `ls -l`, `stat`, `python3 -c` na JSON) | codebase-build |
| 2 | codebase-paths | Każde zakodowane `data/work`/`cache/` w kodzie, testach, skryptach, docs, runbookach, `.claude/skills`, `config/`; wpływ ścieżki konfigurowalnej/env/symlinku; K1–K10 i K8: ścieżki i hashe w manifeście, `code_identity` | Read, Grep, Bash (tylko odczyt) | codebase-paths |
| 3 | external | SQLite przy utracie urządzenia (rollback journal vs WAL, `synchronous`, fsync/`F_FULLFSYNC` na macOS, ryzyko korupcji), wzorce checkpoint/resume (plik per etap, atomic rename, wyjścia adresowane treścią, `ATTACH`), macOS: zniknięcie punktu montowania vs pusty katalog, `diskutil`, `pmset disksleep`, wykrywanie (`os.path.ismount`, `st_dev`, plik-znacznik z UUID wolumenu) | WebSearch, WebFetch, Bash (`diskutil info`, `pmset -g`, `mount` — tylko odczyt) | external |

### Rationale
Brief dzieli się naturalnie na: jak build trzyma stan (wznawianie), gdzie są ścieżki (lokalizacja + powtarzalność) i jak zachowuje się platforma (SQLite/macOS). Konfiguracja jest mała i dotyczy głównie ścieżek, więc trafia do #2. Więcej zbieraczy dublowałoby czytanie tych samych 6 plików.

**Wspólne zakazy dla wszystkich:** bez `build`, `verify`, `export`, testów piszących do `data/work`; bez `rm`/`mv`/`chmod`; bez otwierania `build.sqlite` w trybie zapisu (jeśli w ogóle: `mode=ro`, i tylko `PRAGMA page_count/page_size`, nie `integrity_check` na 21 GB). Wyniki do `analysis/findings/<prefix>-*.md`, po polsku, z cytatem plik:linia.

## 5. Kryteria sukcesu
- Tabela etapów (`preflight` … `reports`): czas, przyrost bazy/plików, gdzie trwały stan, czy idempotentny, koszt powtórzenia.
- Pełna lista miejsc ze ścieżką `data/work`/`cache` z oceną wpływu każdego wariantu lokalizacji.
- Opis zachowania SQLite i macOS przy zniknięciu dysku, poparty źródłami (URL).
- 2–4 warianty lokalizacji i 2–4 warianty wznawiania z kosztem zmiany i ryzykiem; zgodność z K1–K10 i parą A/B.
- Rekomendacja z kolejnością kroków.

## 6. Oczekiwane wyniki
- `outputs/research-report.md`: mapa etapów, warianty, rekomendacja.
- Szkic zmian (bez implementacji): ścieżka robocza (np. zmienna/konfiguracja + kontrola wolumenu), wznawianie etapów (`build --resume`), aktualizacja runbooków.
