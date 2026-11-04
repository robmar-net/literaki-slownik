# #16 etap A: SGJP 20261018

## TL;DR
- Nowy eksport różni się od 20260823 jednym blokiem 23 wierszy (`muralista`, `muralistka`) od wiersza 2512694; nic nie usunięto ani nie zmieniono.
- `scripts/rebase_sgjp_pin.py` przepiął konfiguracje: 7343 rekordy sprawdzone w nowym eksporcie, 0 niezgodnych, 132 klucze konstrukcji przeliczone z payloadu przebiegu `lists-v31-20261012-162111-a`.
- Kod, testy, manifest, `ATTRIBUTIONS.md`, dokumentacja przepięte. Testy: 560 + 5 OK, nowe 3 OK.

## Kluczowe decyzje
- Wersja polityki zostaje `approved-conditions-v30`: reguły się nie zmieniły, zmienił się tylko eksport (odstępstwo od planu, który zakładał v31).
- Id reguły `sgjp-20260823-winien-person-erratum-v1` zostaje: erratum dotyczy tych samych rekordów (wiąże je sha i formy).
- `use_id` relacji `warszawianka` zawiera numer wiersza, więc zmienia się z wierszem (+23).
- `evidence.json` dalej cytuje źródła Morfeusza 20260823 (`segmenty.dat`): to inny artefakt niż eksport.

## Otwarte pytania
- Wydanie: v31 osobno czy razem z suplementem v2 (pytanie po buildzie).

## Przebieg
- 2026-11-04: pobranie, sha `346bd7bc…e5be` zgodny; audyt `analysis/sgjp-stats.json` (7458543 rekordy); nagłówek licencji identyczny bajtowo.
