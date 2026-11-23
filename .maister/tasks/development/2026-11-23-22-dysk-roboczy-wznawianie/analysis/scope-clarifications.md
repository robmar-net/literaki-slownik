# Decyzje zakresu (faza 2)

## TL;DR
Build w całości na T7. Po udanym `verify` B jest kasowane automatycznie, A kopiowane (z hashami) na dysk wewnętrzny, gdzie robi się `export`; kopia A na T7 znika.
Na dysku wewnętrznym (backup) zostaje jedna kopia tego, co zachowujemy. Skrypt sprzątania kasuje śmieci; stare wydania tylko po „tak” właściciela dla konkretnej listy.

## Key Decisions
- D1 (właściciel): zapieczętowana baza zamrożonego przebiegu na dysku wewnętrznym — pieczęć wydania w backupie, verify/export bez T7.
- D2 (właściciel, zastępuje migrację): bez migracji dzisiejszego `data/work`. Zamiast niej `scripts/clean_work.py`: domyślnie lista; kasuje sam nieudane i porzucone przebiegi oraz B po udanym verify; stare wydania (bez pinu w `config/generator/*-sources.json`, nie bieżące na serwerze, nie ostatnie w rodzinie) tylko po zgodzie właściciela na listę.
- D3 (właściciel): promocja automatyczna — po udanym `verify` A: kopia na dysk wewnętrzny z kontrolą sha256 i trybu, potem usunięcie B i kopii A z T7. `export` odmawia przebiegu na wolumenie zewnętrznym.
- Układ (ADR-014, technicznie): `data/work` zostaje katalogiem wewnętrznym; nowy przebieg to symlink `data/work/<przebieg>` → T7; po promocji symlink zastąpiony prawdziwym katalogiem. Piny i ścieżki bez zmian.
- Historia prób w polu `build_attempts` na poziomie głównym manifestu (nie myli się z `verification/attempt-NNNN`).

## Open Questions / Risks
- „Bieżące wydanie na serwerze” trzeba ustalić bez sekretów (np. z konfiguracji repo serwera albo publicznej listy leksykonów).
- Kasowanie B zaraz po verify A: jeśli A trzeba będzie ponownie weryfikować (np. nowy przegląd K7), partnera już nie ma — wtedy potrzebny nowy build pary.
