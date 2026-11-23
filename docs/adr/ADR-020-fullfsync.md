# ADR-020: `fullfsync` przez cały build (4B)

**Status:** zaakceptowana 2026-11-23 (decyzja agenta według reguły ze spec #22).

## TL;DR
Pomiar na T7 dał narzut `fullfsync=ON` **0,09%** czasu buildu, przy progu 5%. Wybór: **4B**,
`FULLFSYNC_MODE = 'build'` w `literaki_slownik/database.py`, czyli `PRAGMA fullfsync=ON` przez cały build.

## Kontekst
Build idzie na zewnętrznym dysku USB (T7) i ma przetrwać odłączenie dysku i utratę zasilania.
Na macOS `fsync` nie opróżnia cache dysku. Robi to dopiero `F_FULLFSYNC`, a w SQLite `PRAGMA fullfsync=ON`.
Spec #22 daje dwa tryby i regułę wyboru:
- `build` (4B): `fullfsync=ON` przez cały build, gdy narzut ≤ 5%;
- `stage_boundaries` (4C): `OFF` w etapie i `F_FULLFSYNC` pliku bazy na granicy etapu, gdy narzut > 5%.

Wzór: `overhead_pct = (czas commitu ON − OFF) × commity buildu / 46 800 s × 100`.

## Pomiar (2026-11-23)
`scripts/measure_fullfsync.py` na T7 (APFS, USB), w nowym katalogu tymczasowym, skasowanym na końcu.
Bez buildu słownika. Baza testowa: `journal_mode=DELETE`, `synchronous=FULL`, commit co 10 000 wierszy,
próby OFF i ON naprzemiennie, 5 powtórzeń po 200 commitów. SQLite 3.54.1.

| Wielkość | Wartość |
|---|---|
| mediana commitu, `fullfsync=OFF` | 4,14 ms (1 000 commitów) |
| mediana commitu, `fullfsync=ON` | 17,57 ms (1 000 commitów) |
| różnica na commit | 13,43 ms |
| commity buildu (przebieg `lists-v32-20261104-161601-a`) | 3 051 = 3 044 partii + 7 etapów |
| rekordy: import / analizy | 12 524 888 / 17 828 737 |
| narzut | 41 s na 46 800 s = **0,09%** |
| `quick_check` tej bazy (22 GB, tylko odczyt) | `ok`, 486 s |

Liczbę commitów skrypt liczy z `reports/import-counts.json` i `reports/decisions.json`: każde źródło
i każdy rodzaj analiz to partie po 10 000, w górę. Pełny wynik:
[fullfsync-measurement.json](../../.maister/tasks/development/2026-11-23-22-dysk-roboczy-wznawianie/verification/fullfsync-measurement.json).

## Decyzje
- **4B: `fullfsync=ON` przez cały build.** Narzut jest ok. 57 razy mniejszy od progu. Margines pokrywa
  różnicę między małą bazą testową a bazą 22 GB, w której commit pisze więcej stron.
- **Zapis plików** (`write_json`, `write_bytes`): tmp w tym samym katalogu, `F_FULLFSYNC` pliku
  (fallback `os.fsync`), `os.replace`, fsync katalogu.
- **Wznowienie** sprawdza bazę przez `PRAGMA quick_check`; wynik inny niż `ok` daje kod 77.
  Na bazie 22 GB to ok. 8 minut.
- **Zakazy:** WAL, `journal_mode=OFF` i `MEMORY`, `synchronous` poniżej `FULL`.

Odrzucone: 4C. Daje mniejszy zysk niż 0,1% czasu, a dokłada fsync na granicach etapów i okno,
w którym dane etapu nie są jeszcze trwałe.

## Wdrożenie w buildzie (#22, grupa 8)
- `database.connect`: każde połączenie zapisywalne ma `journal_mode=DELETE` i `synchronous=FULL`.
  Z `build=True` i `FULLFSYNC_MODE = 'build'` też `fullfsync=ON` i `checkpoint_fullfsync=ON`.
  Połączenie tylko do odczytu nic nie ustawia.
- `stage_durable` na końcu każdego etapu i po resecie `--resume`: commit przed plikami etapu i manifestem.
  W trybie `stage_boundaries` dodatkowo `F_FULLFSYNC` pliku bazy (`database.full_sync`). Kod obu trybów
  zostaje, więc inny dysk roboczy może przejść na 4C zmianą stałej.
- 4C zostaje celowo jako tryb zapasowy (przegląd #22): pomiar objął opóźnienie commitu, a nie pełny build na T7,
  i ponowny pomiar może przekroczyć próg 5%. `database.connect(build=True)` sprawdza `FULLFSYNC_MODE`
  względem `FULLFSYNC_MODES`; literówka w stałej daje `GeneratorError` z kodem 4, zanim build otworzy bazę.

## Otwarte pytania / ryzyka
- Pomiar dotyczy jednego dysku (T7). Inny dysk roboczy wymaga nowego pomiaru tym samym skryptem.
- 486 s `quick_check` zmierzono na dysku wewnętrznym. Na T7 może trwać dłużej.
