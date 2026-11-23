# ADR-016: `build --resume` od pierwszego niegotowego etapu w tej samej bazie

**Status:** zaakceptowana 2026-11-23 (decyzja agenta). Zadanie #22.

## TL;DR
`build --resume --manifest M --run-dir R` wznawia przebieg w tym samym katalogu i tej samej bazie.
Zaczyna od pierwszego etapu, który nie jest `complete`; ten i każdy dalszy liczy się od nowa.
Strata po awarii to bieżący etap (w `reports` bieżący raport, ADR-017). Wynik jest taki sam jak ze świeżego
buildu (ADR-021).

## Kontekst
Wcześniej build odmawiał istniejącego katalogu, a wznawiało się tylko całe `reports`
(`scripts/resume_reports.py`). `constructions` i `decisions` są idempotentne (`insert or ignore`),
`import_*` i `links` nie były. Plik bazy per etap z `ATTACH` łamie klucze obce i pieczęć.

## Decyzje
- **Kolejność kontroli:** 1 brak `R` → 4; 2 symlink bez celu → 75; 3 G1 → 75; 4 manifest nieczytelny →
  ponowny G1 (75), inaczej 4; 5 `VERIFIED`/`FROZEN` → 5; 6 G2 → 76; 7 miejsce → 78; 8 `tree_sha256` i czysty
  kod → 4; 9 `manifest_sha256` wejść → 3; 10 niegotowy `preflight` → przebieg od zera w tym samym katalogu;
  11 `PRAGMA quick_check` ≠ `ok` → 77; 12 `running` → `failed`, nowa próba, reset, etapy.
  Dysk przed manifestem, bo manifest leży na T7: odwrotnie zamiast 75 byłoby 4.
- **Reset:** `import_sgjp`/`import_kwjp` usuwają `evidence_candidate` i `evidence_link` (`DROP`) i czyszczą
  tabele etapu i dalszych (`DELETE`, dziecko przed rodzicem). `constructions`, `decisions`: tylko oba `DROP`.
  `links` przy każdym uruchomieniu usuwa i tworzy swoje tabele. Reset w jednej transakcji przed `running`.
  Gdy w próbie wykonał się etap przed `reports`, `reports/.done/` znika.
- Świeży build i `--resume` idą tą samą pętlą etapów. Wynik JSON ma `resumed_from` (pierwszy etap próby).
- `--resume` nie przyjmuje `--work-root` (kod 2): przebieg ma już katalog.
- `resume_reports.py` to nakładka: stare kontrole (2 przebieg nie czeka na raporty, 4 inny kod), potem
  `build --resume` i jego kod.

Odrzucone: cięcie etapów od środka, plik bazy per etap z `ATTACH`, migawka bazy po etapie.

## Otwarte pytania / ryzyka
- Przerwa w środku etapu kosztuje cały etap (import do ok. 2,4 h).
- Po `DELETE` plik bazy ma inne bajty niż świeży; K8 porównuje treść, więc to dopuszczalne.
- Plan awaryjny, gdyby test „wznowiony = świeży” pokazał różnicę po odbudowie importu: wznowienie
  z etapu importu w nowym pliku bazy od `preflight`. Dziś test przechodzi.
