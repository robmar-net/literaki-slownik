# ADR-019: nadzorca buildu wznawia tylko po kodzie 75

**Status:** zaakceptowana 2026-11-23 (decyzja agenta). Zadanie #22.

## TL;DR
`scripts/build_supervised.py` uruchamia build, a po kodzie 75 czeka na dysk i robi `build --resume`.
Najwyżej 3 wznowienia i 30 min czekania na raz. Każdy inny kod kończy pracę. `build_pair.sh` uruchamia
dwóch nadzorców pod `caffeinate -dimsu`.

## Kontekst
T7 zniknął raz w nocy. Bez nadzorcy strata obejmuje czas do chwili, gdy ktoś to zauważy. Nowy proces ma
świeże deskryptory, a SQLite przy otwarciu sam cofa hot journal. Pętla w `sh` byłaby nietestowalna.

## Decyzje
- Przed każdym procesem: przebieg istnieje i manifest czytelny → `build --resume`; przebiegu nie ma →
  świeży `build --work-root W`; symlink jest, a dysku brak → czekanie.
- Po 75 co `--poll-seconds` (5) sprawdza G1+G2, najdłużej `--wait-minutes` (30). Limit `--max-resumes` (3).
  Wyczerpany limit albo czas: 75. Inny znacznik albo wolumen pod inną ścieżką: 76 od razu.
- SIGINT: przekazany do buildu, kod 130. SIGTERM i SIGHUP: przekazane, kod buildu, bez wznowienia.
- Nadzorca nie dotyka plików przebiegu (`-journal` zostaje).
- Logi na dysku wewnętrznym: `logs/<nazwa>.out.json`, `logs/<nazwa>.err`, `logs/<nazwa>.supervisor.log`.
  Przez cały czas trzyma `flock` na `logs/<nazwa>.lock`; drugi nadzorca tego przebiegu dostaje 4.
  Po tej blokadzie `clean_work.py` rozpoznaje żywy przebieg.
- Ręczne `build --resume` zostaje trybem bazowym.

Odrzucone: tylko ręczne wznawianie; pętla w `build_pair.sh`.

### Poprawki po weryfikacji #22
- `marker_id` nadzorca zapamiętuje przed pierwszym procesem i odświeża po każdym
  udanym odczycie; po 75 nie spada do „nieznany”, więc wolumen pod inną ścieżką daje 76 od razu.
- Watchdog bez postępu: `--stall-minutes` (domyślnie 120, 0 wyłącza). Postęp to zmiana mtime manifestu, bazy,
  journala i raportów albo wzrost czasu CPU buildu (raport `unresolved` liczy ~4 h bez zapisu plików).
  Po limicie: zdarzenie `stalled`, SIGTERM, po 60 s SIGKILL; strażnik zawodzi → 75 (wznowienie), zły
  wolumen → 76, zdrowy → 4. Proces w nieprzerywalnym I/O może przeżyć SIGKILL; wtedy trzyma blokadę buildu
  i wznowienie kończy się kodem 4 (stop bez szkody).
- Sygnał przed `Popen` nie uruchamia nowego buildu, a sygnał między `Popen` a przypisaniem dziecka trafia do
  dziecka. Pod `nohup` SIGHUP zostaje ignorowany; runbook uruchamia parę przez `nohup … & disown`.
- Drugi z rzędu kod 75 w tym samym etapie, gdy sonda jest od razu zdrowa, kończy nadzorcę kodem 4 (zdarzenie `repeated-75-healthy`): to błąd kodu albo I/O niezwiązane z dyskiem, a nie zanik T7. Jedno takie 75 nadal wznawia (szybki powrót T7).

## Otwarte pytania / ryzyka
- Po restarcie maszyny nadzorcę uruchamia się ręcznie (z tym samym `--run-dir`). LaunchAgent poza zakresem.
- Przy częstych zniknięciach limit 3 wznowień się wyczerpie: 75 i decyzja człowieka.
