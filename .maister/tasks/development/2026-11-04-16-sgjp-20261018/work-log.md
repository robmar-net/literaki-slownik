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
- 2026-11-08: przegląd K9 `verification/quality-review-v32.json` dla `lists-v32-20261104-161601-a` (1876 pozycji). Przeniesione bez zmian z v31: 763 (jednostka identyczna poza przypięciem SGJP). Ocenione na nowo: 1113 — 924 z przesuniętym wierszem SGJP (+23; każdy cytowany rekord sprawdzony w eksporcie 20261018), 180 nowych analiz (próba wylosowana na nowo, bo klucze analiz zależą od id źródła) i 9 dawnych „niepewne” rozstrzygniętych dowodem z SGJP (bob, jugol, 7 linków UNMATCHED).
- Wynik: błędnych 0, niepewnych 14 (jeśliby/jeżeliby ×5, ponadeń, popodeń, poprzezeń, sponadeń, spopodeń, zzań, sek, spełna, toć — jak w v31), żadna pozycja nie wpływa na listy ani linki. Warstwa uzupełniająca: 21 nowych form muralista/muralistka, wszystkie poprawne (accept w BROAD i STANDARD).
- 2026-11-08: etap reports dokończony po restarcie maszyny (`scripts/resume_reports.py`, A i B, ~8,5 h, oba complete).
- 2026-11-09: `verify` A/B + `quality-review-v32.json`: **VERIFIED**, K1–K10 pass (5,8 h, szczyt RSS 7,1 GB). BROAD 3 479 039, STANDARD 3 092 261; 15 plików kanonicznych identycznych z B. Export i wydanie czekają na decyzję operatora.
