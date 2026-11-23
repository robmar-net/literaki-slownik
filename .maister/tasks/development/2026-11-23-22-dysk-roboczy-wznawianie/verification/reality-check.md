# Kontrola rzeczywistości #22 (build na T7 z wznawianiem)

## TL;DR
**Status: ⚠️ Issues Found — GO na pierwszą parę na T7, z zastrzeżeniami.** Kod rozwiązuje problem właściciela:
zniknięcie T7 kończy build kodem 75, nadzorca czeka i wznawia od bieżącego etapu albo raportu, a nie od zera.
Duże pliki (baza ~22 GB, journal) są na T7, `temp_store=MEMORY`, na dysk wewnętrzny trafia jedna kopia A po verify.
Sprzątanie nic nie kasuje bez `--apply`, a wydań bez listy właściciela.
Krytycznych luk brak: 0 critical, 3 warning, 5 info. Testy celowane (10 modułów: resume, równoważność, nadzorca, promocja, sprzątanie, wolumen, kody, pętla etapów, znaczniki, układ): 64/64 OK w 266 s.
Największa luka: nic z tego nie było sprawdzone na prawdziwym odłączeniu USB. Testy podstawiają `ismount`/`stat`
i zakładają, że dysku nadal nie ma, gdy klasyfikator sprawdza błąd.

## Key Decisions
- Ocena wg celu „para buildów ~13 h na T7 nie zaczyna od zera”, nie wg doskonałości kodu.
- Luki z audytu spec (H1–H3, M1–M8) sprawdziłem w kodzie: wszystkie są obsłużone (H1: `check_mounted` przed
  odczytem manifestu, `build.py` `resume`; H2: `clean_work` porównuje hashe plików z `NOTICE`, dry-run widzi 50 hashy
  i trzyma `pop-v2`; H3: stany S0–S4 w `promote_run.py`; M1: `rename_swap`; M5: świeży build po 75 bez przebiegu).
- Nie powtarzam W1/W2 z `production-readiness-report.md` (SIGHUP przy zamknięciu terminala; czas pary na T7
  niezmierzony), tylko je potwierdzam.

## Open Questions / Risks
- Czy `st_dev` po ponownym podłączeniu T7 naprawdę się zmienia? ADR-015 to zakłada, nikt tego nie zmierzył (R1).
- Czy macOS przy zanikającym USB zwraca błąd I/O, czy proces wisi w stanie `U`? Nadzorca nie ma watchdoga (R2).

## Rzeczywistość vs deklaracje

| Deklaracja | Rzeczywistość | Dowód |
|---|---|---|
| Brak dysku → 75, nadzorca wznawia | Tak, gdy dysku nadal nie ma przy klasyfikacji | `build.exit_code`, `test_disk_lost_in_a_stage_is_75_then_supervisor_resumes_to_a_complete_run` |
| Wznowiony = świeży | Tak, 19 punktów przerwania, para wznowiony+świeży → VERIFIED | `tests/test_resume_equivalence.py` |
| Strata ≤ bieżący etap/raport | Tak, ale etap lub raport trwa godziny | v32-a: `diagnostic_unresolved` 14 857 s (~4,1 h) |
| Duże pliki na T7 | Tak: baza i journal obok siebie, `temp_store=MEMORY` | `database.py:43` |
| Jedna kopia na dysku wewnętrznym | Tak, po `promote_run.py`: A wewnątrz, B i kopia A na T7 skasowane | `promote_run.py` `_finish` |
| Promocja „automatyczna” | Łańcuch `verify && promote_run` w runbooku, nie wywołanie z `verify` | runbook §5 krok 5 |
| Sprzątanie bez zgody nie kasuje wydań | Tak: dry-run kod 0, 26 kandydatów (0,42 GB), nic nie skasowane | `clean_work.py` bez `--apply` |
| fullfsync ≤ 5% | 0,09% z pomiaru commitów na T7, nie z pełnego buildu | `verification/fullfsync-measurement.json` |

## Luki

### Warning
**R1. Szybki powrót T7 przed klasyfikacją daje 4 zamiast 75 i nadzorca się zatrzymuje.**
- `exit_code` przy `OSError`/`sqlite3.Error` pyta strażnika (G3 `st_dev`, G1, G2). Gdy wszystkie przechodzą, zwraca 4.
  Test `test_disk_io_error_is_75_when_guard_fails_and_4_when_healthy` utrwala to zachowanie.
- Martwy deskryptor po ponownym montowaniu daje błąd I/O przy następnej operacji. Jeśli T7 wrócił wcześniej
  (zniknięcie „na sekundy”, a proces akurat liczył w RAM), to G1 i G2 przechodzą. G3 łapie to tylko wtedy, gdy macOS
  nadał wolumenowi inne `st_dev`. Numer `diskN` jest zwykle używany ponownie, więc `st_dev` może być taki sam.
  Tego nie zmierzono.
- Skutek: build stoi do chwili, gdy ktoś zauważy. Danych nie traci, ręczne `build --resume` działa.
- Poprawka: w klasyfikatorze, dla przebiegu z `work_volume`, traktować `SQLITE_IOERR`/`EIO`/`ENXIO` jako 75
  (wznowienie jest idempotentne i ograniczone do 3 prób). Druga możliwość: porównać `st_ino` bazy z `fstat`
  otwartego deskryptora.

**R2. Brak watchdoga na zawieszony build.** Jeśli I/O na zanikającym USB zablokuje proces zamiast zwrócić błąd,
`child.wait()` w nadzorcy czeka bez końca. Nikt nie dostaje kodu ani wpisu w logu. Do zmierzenia przy pierwszym
prawdziwym zdarzeniu. Ewentualna poprawka: limit czasu bez postępu (np. brak zmiany `manifest.json`/journal przez N min).

**R3. Całość nie była uruchomiona na prawdziwym sprzęcie.** Nie było buildu na T7 (czas pary nieznany, W2 w
production-readiness) ani prawdziwego odłączenia USB. To poza zakresem z decyzji właściciela, ale pierwsza para
jest w praktyce testem akceptacyjnym. Proponuję jednorazowo odłączyć T7 w trakcie krótkiego etapu i sprawdzić
w `logs/<przebieg>.supervisor.log`, że jest `exit 75` → `wait` → `start --resume`.

### Info
- **I1.** Wznawianie działa per etap i per raport, a nie od miejsca przerwania. Najdłuższe jednostki trwają godziny
  (`unresolved` ~4,1 h). Wymaganie „nie od zera” jest spełnione. Zysk zależy od chwili zniknięcia dysku.
- **I2.** Limit 3 wznowień liczy się na cały przebieg (~13 h). Przy jednym zniknięciu na noc wystarcza.
- **I3.** `build_pair.sh` kieruje stdout nadzorcy do `logs/<nazwa>.supervisor.log`, a nadzorca pisze tam też
  zdarzenia JSON. Ostatnia linia ma inny kształt (`run_dir`, `exit_code`). To nie szkodzi, ale czytelnik logu musi to
  uwzględnić.
- **I4.** Dysk wewnętrzny: `clean_work` tylko wypisuje (klasa 7). Dziś `data/work` ma 25 GB, z czego 22,3 GB to
  `lists-v32-…-a` (FROZEN, źródło bieżącego wydania), więc śmieci wewnątrz prawie nie ma. Zgodne z D2.
- **I5.** Kasowanie B zaraz po promocji: ponowny `verify` A wymaga nowej pary. Ryzyko znane i przyjęte (scope D3).

## Kompletność funkcjonalna
Około 90%. Ścieżki „brak dysku”, „zły dysk”, „brak miejsca”, „uszkodzona baza”, przerwana promocja i sprzątanie
mają kod i testy. Brakuje odporności na wyścig z R1, watchdoga z R2 i dowodu na prawdziwym sprzęcie (R3).

## Plan działań
| # | Zadanie | Kryterium | Priorytet | Wysiłek |
|---|---|---|---|---|
| 1 | Błąd I/O na przebiegu z `work_volume` → 75 (R1) | test: zdrowy strażnik + `disk I/O error` na T7 → 75, nadzorca wznawia | High | 1–2 h |
| 2 | Uruchamiać parę przez `nohup … & disown` (W1 z production-readiness) | para przeżywa zamknięcie terminala | High | 10 min |
| 3 | Próba odłączenia T7 przy pierwszej parze (R3) | w logu nadzorcy `75 → wait → --resume → 0` | Medium | 15 min nadzoru |
| 4 | Watchdog bez postępu (R2), jeśli zdarzy się zawieszenie | wpis w logu i kod 75 po N min bez postępu | Medium | 2–3 h |

## Decyzja
**GO** na pierwszą parę na T7. Najgorszy przypadek to zatrzymanie z ręcznym `--resume` (R1, R2), nie utrata danych
ani zapis na dysk wewnętrzny. Pozycję 1 warto zrobić przed parą, bo usuwa najbardziej prawdopodobną drogę,
którą nadzorca nie zadziała dokładnie w scenariuszu „dysk znika na sekundy”.
