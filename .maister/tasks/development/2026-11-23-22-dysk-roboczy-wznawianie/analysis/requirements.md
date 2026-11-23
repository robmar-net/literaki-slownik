# Wymagania (faza 5)

## TL;DR
Build pary A/B w całości na T7, odporny na zniknięcie dysku: kod 75, nadzorca wznawia `build --resume` per etap i per raport, wynik = świeży build.
Po verify: promocja A na dysk wewnętrzny (sha256), skasowanie B, export wewnątrz. `clean_work.py` sprząta; stare wydania tylko po zgodzie.

## Key Decisions
- Przebieg pracy (właściciel): `build_pair.sh <nazwa>` → 2 nadzorców pod `caffeinate -dimsu` na T7 → przegląd K7 przez sesję → `verify` → automatyczna promocja A + kasowanie B → `export` na dysku wewnętrznym.
- `scripts/resume_reports.py` zostaje jako nakładka na `build --resume`; `build_pair.sh`: logi do `logs/` (dysk wewnętrzny), start przez nadzorcę.
- Brak makiet/UI.

## Opis początkowy
Wdrożenie projektu z badania `research/2026-11-23-dysk-roboczy-wznawianie` (#22), z korektami z faz 1–2 (`analysis/clarifications.md`, `analysis/scope-clarifications.md`).

## Wymagania funkcjonalne
1. Układ: `data/work` zostaje katalogiem wewnętrznym; nowy przebieg tworzony jako katalog na wolumenie roboczym T7 i symlink `data/work/<przebieg>`. Brak wolumenu ⇒ żaden plik przebiegu nie powstaje na dysku systemowym. `.gitignore`: `/data/work`, `/cache`, `/logs` bez ukośnika.
2. Strażnik wolumenu G1 `ismount` punktu montowania, G2 znacznik `.literaki-work-volume` (`marker_id` w manifeście; UUID tylko na wolumenie), G3 `st_dev` bez zmian przed etapem i przed `os.replace`; wolne miejsce ≥50 GB na stronę. `scripts/init_work_volume.py` zakłada znacznik.
3. Trwały zapis: `write_json` i nowy `write_bytes` — tmp w tym samym katalogu, `F_FULLFSYNC` (fallback `fsync`), `os.replace`, fsync katalogu; sprzątanie w `finally` nie maskuje błędu. `write_lists` atomowo.
4. Klasyfikator błędów: `sqlite3.Error`/`OSError` ⇒ ROLLBACK (tolerowany), zamknięcie, ponowny strażnik; brak dysku 75, zły wolumen 76, `quick_check`≠ok 77, brak miejsca 78, reszta 4.
5. `build --resume --manifest M --run-dir R`: walidacja `tree_sha256`/`git_dirty`, `inputs.manifest_sha256`, `marker_id`, nie VERIFIED/FROZEN; `quick_check`; `running`→`failed`; pomijanie `complete`; odbudowa etapów nieidempotentnych (import: DELETE w kolejności FK łącznie z wierszem `own-semantic-use-review-v1`; links: DROP IF EXISTS); `build_attempts` na poziomie głównym manifestu.
6. Wznowiony = świeży: usunąć zależność od przebiegu w `new_candidates`, `new_analyses`, `new_decisions`; `import-counts.json` z bazy; `inventory.json` i `qualifier-conditions.json` w obrębie etapu; `links` ustawia `running`; `explain` zwraca z etapów tylko status (K7).
7. Raporty: znaczniki `reports/.done/<raport>.json` (sha256, bytes, tree_sha256, manifest_sha256); przy wznowieniu pomijane, `unresolved` wczytywany z pliku.
8. SQLite: jawnie `journal_mode=DELETE`, `synchronous=FULL`; `fullfsync` wg pomiaru (≤5% ⇒ cały build, inaczej granice etapów); `scripts/measure_fullfsync.py` (JSON).
9. Nadzorca `scripts/build_supervised.py`: po 75 czeka na G1+G2 co 5 s do 30 min, `--resume`, maks. 3 próby; 76/77/78/4 stop; log do `logs/`.
10. Promocja `scripts/promote_run.py`: wymaga VERIFIED A; kopiuje A na dysk wewnętrzny z kontrolą sha256 i trybu plików, podmienia symlink na katalog, kasuje kopię A i B na T7. `export` odmawia przebiegu na wolumenie zewnętrznym.
11. Sprzątanie `scripts/clean_work.py`: domyślnie lista; `--apply` kasuje nieudane/porzucone przebiegi i osierocone katalogi na T7; stare wydania (bez pinu w `config/generator/*-sources.json`, nie bieżące na serwerze, nie ostatnie w rodzinie) tylko z osobną flagą po zgodzie właściciela na konkretną listę.
12. `verify` wypisuje historię prób; `export` przenosi skrót `build_history` do `source_run` w `release-manifest.json` (bez komunikatów i ścieżek).
13. Dokumentacja: `docs/generator/cli.md` (resume, kody 75–78, skrypty), runbook, ADR-014+ w `docs/adr/`.

## Ponowne użycie
- Kontrole z `scripts/resume_reports.py:44-52` → wspólna walidacja wznowienia.
- Wzorce testów przerwań: `tests/test_lifecycle.py:50-84`, `tests/test_build.py:151,201`; fikstury `tests/helpers.py`, `tests/release_helpers.py` (uwaga: `complete_run` nadpisuje etapy).

## Zakres
Poza zakresem: prawdziwe buildy słowników (pierwsza para na T7 to osobna decyzja właściciela), zmiany polityki i składu, piny POP/POP00/TEMATY, migracja dzisiejszego `data/work`, cięcie etapów od środka (2C), migawki (3C), CI (tylko lokalnie; nigdy runnery GitHuba).

## Uwagi techniczne
Python stdlib, `python3 -m unittest discover -s tests -p 'test_*.py'`. Repo publiczne: brak UUID i ścieżek domowych. Prawdziwy USB nie jest używany w testach (podstawiane `ismount`/`stat`/`fcntl`); pomiar `measure_fullfsync.py` na T7 jednorazowo.
