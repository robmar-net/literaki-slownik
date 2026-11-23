# ADR-018: kody wyjścia 75–78

**Status:** zaakceptowana 2026-11-23 (decyzja agenta). Zadanie #22.

## TL;DR
Nowe kody: 75 dysk roboczy zniknął, 76 zły wolumen, 77 uszkodzona baza, 78 brak miejsca.
Tylko 75 oznacza „czekaj i wznów” (ADR-019). Pozostałe kody (0, 2, 3, 4, 5, 130) bez zmian.

## Kontekst
Wcześniej każdy `OSError` i `sqlite3.Error` kończył się kodem 4, tak jak błąd danych, a `sqlite3.Error`
poza buildem dawał traceback i kod 1. Nadzorca musi odróżnić zniknięcie dysku od błędu, którego ponawianie
nic nie da. Tekst błędu nie jest kontraktem, kod wyjścia jest.

## Decyzje
- Po `sqlite3.Error`/`OSError` build robi `ROLLBACK` (błąd pomijany), zamyka połączenie i pyta strażnika.
  Strażnik nie przechodzi: 75 albo 76. Przechodzi: `SQLITE_FULL`/`ENOSPC`/`EDQUOT` → 78,
  `SQLITE_CORRUPT`/`SQLITE_NOTADB` → 77, reszta → 4.
- 77 także po `quick_check` ≠ `ok` przy `--resume`. 78 także przy progach miejsca na starcie i w promocji.
- `cli.py` łapie `sqlite3.Error` → 4.
- Kontrakt obejmuje `build`, `build --resume`, `build_supervised.py`, `build_pair.sh`, `promote_run.py`,
  `init_work_volume.py` i `resume_reports.py`. Opis: `docs/generator/cli.md`, „Kody i kontrola”.
- Wartości 75–78 to kody `sysexits` (`EX_TEMPFAIL` … `EX_CONFIG`), bez kolizji z obecnymi.

Odrzucone: jeden kod błędu i parsowanie stderr w nadzorcy.

### Poprawki po weryfikacji #22
- Na przebiegu z `work_volume` błąd urządzenia (`SQLITE_IOERR`, `SQLITE_CANTOPEN`,
  `EIO`, `ENXIO`, `ENODEV`, `ENOENT`, `EROFS`) daje 75 także przy zdrowym strażniku. T7 mógł wrócić, zanim
  klasyfikator go sprawdził, a G3 nie widzi powrotu z tym samym `st_dev`. `st_ino` nie pomaga: APFS trzyma
  numery i-węzłów na dysku. Na dysku wewnętrznym ten sam błąd daje 4. Fałszywe 75 kosztuje jeden etap,
  bo wznowienie jest idempotentne, a nadzorca ma limit 3 wznowień.
- Build i `--resume` biorą blokadę `.<nazwa>.build.lock` obok symlinku przebiegu; zajęta → 4 przed zmianą.
- Korzeń przebiegów na dysku repo daje 76 we wszystkich miejscach (`volume.check_work_root`).

## Otwarte pytania / ryzyka
- Inny błąd I/O w chwili zniknięcia dysku zostanie uznany za 75. Limit wznowień (ADR-019) ogranicza skutek.
