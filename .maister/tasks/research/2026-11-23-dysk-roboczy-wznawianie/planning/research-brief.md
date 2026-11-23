# Brief: duże pliki robocze na /Volumes/Data i wznawianie buildu

## TL;DR
Badamy przeniesienie dużych plików generatora (build.sqlite ~21 GB na przebieg, para A/B ~44 GB, build ~14 h) z `data/work/` w repo na zewnętrzny dysk `/Volumes/Data` (USB, APFS, 1 TB wolne), który czasem znika. Szukamy rozwiązania, w którym zniknięcie dysku nie oznacza budowy od zera.

## Pytanie badawcze
1. Gdzie i jak trzymać duże pliki poza repo (konfiguracja ścieżki, symlink, zmienna środowiskowa), żeby kod, testy, runbooki i `explain` działały, a brak dysku był wykrywany od razu, a nie jako cichy błąd?
2. Jak zmienić build, żeby przerwany przebieg (utrata dysku, restart, kill) dało się wznowić od ostatniego ukończonego etapu lub części: checkpointy etapów, podział bazy na pliki per etap/część, atomowe zapisy, weryfikacja spójności po wznowieniu?
3. Jak to pogodzić z wymogami powtarzalności (verify K1–K10, para A/B, manifest z hashami, K8 czysty kod)?

## Typ
Technical (analiza kodu + praktyki zewnętrzne: SQLite na dyskach zewnętrznych, odporność na odłączenie).

## Zakres
- W zakresie: `literaki_slownik/build.py`, `run.py`, `database.py`, `schema.sql`, `verify.py`, `export.py`, `explain.py`, `scripts/build_pair.sh`, runbooki (`docs/plan-dalszych-prac-runbook.md`), `.gitignore`, `cache/`; zachowanie SQLite (WAL, journal, fsync) przy utracie urządzenia; macOS: montowanie USB, `diskutil`, uśpienie dysku.
- Poza zakresem: zmiana polityki słownika, nowe buildy teraz, CI.
- Ograniczenia: bez CI na runnerach GitHuba; repo publiczne (żadnych prywatnych ścieżek z danymi osobistymi poza nazwą wolumenu); niczego nie usuwamy ani nie budujemy w ramach badania.

## Kryteria sukcesu
- Mapa etapów buildu z czasem i rozmiarem każdego (z logów `.out.json`/`.err` i manifestów) i miejscem, gdzie stan jest trwale zapisany.
- Ocena 2–4 wariantów lokalizacji i 2–4 wariantów wznawiania, z kosztem zmiany i ryzykiem.
- Rekomendacja z kolejnością kroków.

## Kontekst
- `/Volumes/Data`: USB, APFS, SSD, 3.6 TB, 1 TB wolne; znika czasem (przyczyna nieznana).
- Dziś: `data/work/` w `.gitignore`; zostaje 1 przebieg (`lists-v32-20261104-161601-a`, 21 GB) do `explain`.
- Utworzono: 2026-11-23T04:15:20Z
