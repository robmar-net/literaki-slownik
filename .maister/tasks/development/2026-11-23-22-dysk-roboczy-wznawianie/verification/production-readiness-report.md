# Gotowość do pierwszej pary A/B na T7 (#22)

**Data:** 2026-11-23 · **Zakres:** `git diff aa50eca..HEAD` w `literaki-slownik` · **Cel:** pierwsza prawdziwa para
`LITERAKI_WORK_ROOT=<wolumen>/literaki-slownik/work scripts/build_pair.sh <nazwa>` → `verify` → `promote_run.py` → `export`
na dysku wewnętrznym. **Status:** z zastrzeżeniami.

## TL;DR
- **Werdykt: GO z zastrzeżeniami.** Blokerów brak: 0 critical, 2 warning, 6 info.
- Kod, kody wyjścia, strażnik wolumenu, wznawianie i dokumentacja są spójne. Testy: 676 OK (pełny zestaw, 585 s, uruchomione ponownie przy tej ocenie).
- Stan T7 (tylko `ls`/`df`/`stat`): APFS po USB, ok. 1,0 TB wolne (próg pary 100 GB); znacznik w korzeniu wolumenu jest
  (121 B, tryb 0600); `literaki-slownik/work` istnieje i jest pusty. Dysk wewnętrzny: ok. 187 GiB wolne (promocja A ≈ 24 GB).
  RAM 36 GB (para ≈ 12 GB).
- Przed startem: uruchomić parę **odpięcie od terminala** (`nohup … & disown`) i tak samo nadzorcę po restarcie, pod
  `caffeinate -dimsu` (W1). Czas pary na T7 jest niezmierzony (W2).

## Key Decisions
- Ocena wg celu „production” = jedna para buildów operatora, nie usługa sieciowa. Kategorie HTTP (health check, CORS,
  rate limiting, HTTPS, Sentry, metryki) nie dotyczą lokalnego wsadowego CLI; zastępują je: kody wyjścia, logi w `logs/`,
  historia prób w manifeście, strażnik G1–G3 i progi miejsca.
- Znacznika nie czytałem; sprawdziłem tylko jego obecność, rozmiar i tryb. Na T7 niczego nie zapisałem, buildu nie
  uruchamiałem.
- Zamiar „SIGHUP kończy bez wznowienia” (ADR-019) uznaję za poprawny; ryzyko leży w sposobie uruchomienia (W1), nie w kodzie.

## Open Questions / Risks
- **W1 (warning, odporność): SIGHUP przy zamknięciu terminala albo sesji kończy parę bez wznowienia.** `build_pair.sh`
  i krok 4 runbooka („po restarcie”) uruchamiają nadzorców na pierwszym planie. Nadzorca instaluje własny handler SIGHUP,
  przekazuje sygnał buildowi i kończy pracę jego kodem (129), bez `--resume`. Sam `nohup` tego nie zmienia, bo handler
  Pythona nadpisuje `SIG_IGN`; potrzebne jest odpięcie od terminala (`& disown` albo `setsid`). Krok 4 nie ma też
  `caffeinate -dimsu`, więc wznowiona strona może zasnąć z maszyną. Naprawa (doc): w runbooku i `cli.md`
  `nohup caffeinate -dimsu scripts/build_pair.sh … > logs/pair.log 2>&1 & disown` oraz to samo dla
  `build_supervised.py` po restarcie. Fixable: tak.
- **W2 (warning, wydajność): czas pary na T7 niezmierzony.** „Ok. 13 h” pochodzi z buildów na dysku wewnętrznym.
  Pomiar ADR-020 objął tylko opóźnienie commitu (narzut `fullfsync` 0,09%), nie losowe odczyty bazy 22 GB po USB
  przy dwóch buildach na jednym dysku. Czas może być wyraźnie dłuższy. Bez wpływu na poprawność. Mitygacja: w pierwszej
  parze odczytać czasy etapów z `reports/performance.json` i `logs/*.supervisor.log` i poprawić runbook. Fixable: nie.
- **I1 (info):** `quick_check` przy wznowieniu zmierzony na dysku wewnętrznym (486 s); na T7 może trwać dłużej (ADR-020 to
  zapisuje).
- **I2 (info):** strażnik porównuje tylko `marker_id`; `volume_uuid` ze znacznika nie jest porównywany z `diskutil`.
  Klon wolumenu ze znacznikiem przeszedłby G2. Ryzyko małe (jeden dysk).
- **I3 (info):** `--resume` i `verify` wymagają niezmienionego i zacommitowanego `literaki_slownik/` w tym checkoucie
  przez cały build (kod 4). Zmiany generatora w tym czasie robić w osobnym worktree.
- **I4 (info):** w `build_pair.sh` kolizja nazwy strony `b` (exit 2) zostawia działającego nadzorcę strony `a`.
  Przy stemplu z sekundami prawie niemożliwe.
- **I5 (info):** `logs/<nazwa>.supervisor.log` ma zdarzenia JSON nadzorcy i, na końcu, jego stdout
  (`{"run_dir","exit_code"}`) w innym kształcie. Oba to poprawny JSON w osobnych liniach (O_APPEND), czytelne.
- **I6 (info):** `FULLFSYNC_MODE` bez walidacji względem `FULLFSYNC_MODES` (za completeness-check); `shutil.rmtree(onerror=)`
  w `promote_run.py` i `clean_work.py` jest przestarzałe od Pythona 3.12 (działa na 3.15.2).

## Przegląd kategorii

| Kategoria | Ocena | Stan |
|---|---|---|
| Konfiguracja | 95% | `LITERAKI_WORK_ROOT` wymagany (2), sprawdzany przed startem: istnienie (75), znacznik (76), ≥ 100 GB (78); build sprawdza ≥ 50 GB na proces |
| Logi i obserwowalność | 85% | `logs/` na dysku wewnętrznym (ignorowany przez git): `.supervisor.log` (JSON na zdarzenie), `.out.json`, `.err`, `.promote.log`; `build_attempts` w manifeście i w `verify`/`release-manifest.json`; brak powiadomienia o końcu |
| Odporność | 85% | kody 75–78 z klasyfikatora po błędzie I/O; nadzorca wznawia tylko po 75 (3×, 30 min); `begin_resume` zamyka próbę jako `interrupted`; `quick_check` → 77; hot journal cofa SQLite; trwały zapis (F_FULLFSYNC, replace, sync katalogu); W1 |
| Wydajność i zasoby | 80% | miejsce i RAM z zapasem; `fullfsync` 0,09%; W2 |
| Bezpieczeństwo danych | 95% | UUID tylko w znaczniku; logi i manifest mają losowy `marker_id`; promocja kasuje B tylko `INCOMPLETE` ze zgodnym `canonical-index`; `export` na T7 → 5; `clean_work.py` domyślnie tylko lista |
| Wdrożenie i dokumentacja | 90% | `cli.md` (tabela kodów), runbook §5 kroki 1–7, ADR-014..021; brak migracji danych (stare przebiegi bez zmian); W1 dotyczy kroków 2 i 4 |

**Gotowość łącznie: ok. 88%. Ryzyko wdrożenia: niskie** (zła ścieżka kończy się kodem, a nie utratą danych; wydanie
powstaje tylko po `verify` i promocji).

## Restart maszyny — przebieg
Proces ginie; `logs/<nazwa>.lock` znika razem z nim. Po zalogowaniu i zamontowaniu T7 ręcznie, osobno dla stron:
`build_supervised.py --run-dir data/work/<przebieg>` → `build --resume`: etap `running` → `failed`, otwarta próba →
`interrupted`, `quick_check`, praca od pierwszego niegotowego etapu. Gdy T7 jeszcze się nie zamontował, nadzorca czeka
do 30 min. Gdy wróci pod inną ścieżką (np. `Data 1`), kończy 76 (decyzja człowieka; symlinki są bezwzględne).

## Następne kroki
1. Uruchomić parę odpiętą od terminala i pod `caffeinate` (W1); poprawić te dwa polecenia w runbooku i `cli.md`.
2. W trakcie śledzić `logs/<przebieg>.supervisor.log`; nie zmieniać `literaki_slownik/` w tym checkoucie (I3).
3. Po parze zapisać zmierzony czas na T7 w runbooku (W2).
4. Dalej wg runbooka: przegląd K7 → `verify … && promote_run.py --peer` → `export` na dysku wewnętrznym.
