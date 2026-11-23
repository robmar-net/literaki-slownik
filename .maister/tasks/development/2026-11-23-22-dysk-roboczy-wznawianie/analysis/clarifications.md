# Wyjaśnienia (faza 1)

## TL;DR
Na T7 przenosimy tylko to, co umiemy odtworzyć (kosztem czasu); rzeczy nieodtwarzalne zostają na dysku wewnętrznym objętym backupem. Kopiowanie z kontrolą hashy, stary katalog usuwamy dopiero po zgodzie właściciela.
Decyzje techniczne podjąłem sam (ADR w projekcie): `attempts[]` na poziomie głównym manifestu, ADR od ADR-014, liczniki `new_*` zamienione na niezmienne przy wznowieniu, `explain` zwraca z etapów tylko status.

## Key Decisions
- Przeniesienie `data/work` na T7 — decyzja właściciela (2026-11-23). Usunięcie starego katalogu tylko po osobnej zgodzie.
- **Backup (właściciel, 2026-11-23):** na T7 trafia tylko to, co da się odtworzyć kosztem czasu (bazy przebiegów, listy, raporty z buildu). To, czego nie da się odtworzyć (np. przeglądy, pakiety wydań, decyzje i ich dowody), zostaje na dysku wewnętrznym objętym backupem. Skrypt migracji musi klasyfikować każdy wpis i odmawiać przeniesienia nieodtwarzalnego.
- `attempts[]` na poziomie głównym manifestu — `set_stage` i `complete_run` nadpisują wpis etapu.
- Numeracja ADR od ADR-014 — `docs/adr/` kończy się na 013.
- Pola `new_candidates`, `new_analyses`, `new_decisions` liczone ze stanu bazy albo usunięte — inaczej K8 rozróżni wznowiony od świeżego.
- `explain` zwraca z `stages` tylko `.status` — odcina K7 od historii prób.

## Open Questions / Risks
- Trzeba ustalić, które pliki przebiegu są nieodtwarzalne (np. `review`, `verification/`, pakiety `export`) i gdzie zostają, skoro przebieg na T7 się do nich odwołuje.
- Przeniesienie zamrożonych przebiegów: `export` robi `chmod` read-only na `build.sqlite`; kopia musi zachować uprawnienia i hashe, a piny `../../data/work` muszą dalej działać przez symlink.
