# Decyzje właściciela, runda 2: frag, pozostałość użyć, przesiew mieszkańców R1

## TL;DR
Właściciel rozstrzygnął 2026-10-08 ostatnie trzy kategorie merytoryczne z [inwentarza niewiadomych](unresolved-inventory.md):
- frag są dopuszczone warunkowo, z oznaczeniem, tak jak adjp;
- sprawdzone użycia wyczerpują swoje pełne ID SGJP;
- przesiew `-anin/-anka` to nazwy mieszkańców (wielka litera, odmowa w grze), z wyjątkiem [76 zaakceptowanych nie-mieszkańców](r1-non-resident-exceptions.md).

Polityka: `diagnostic-approved-conditions-v23`. Runda 1: [owner-decisions-round1-decision.md](owner-decisions-round1-decision.md).

## Key Decisions
- **F — frag, warunkowo.** Fragment frazy (`wznak`, `bezcen`, `wte`) jest osobnym wyrazem graficznym, więc zostaje dopuszczony w grze.
  - Reguła `game-frag-graphic-word-v1` ma `provisional: true`.
  - Wycofanie to zmiana `FRAG_GAME_STATUS` w `literaki_slownik/policy.py` na `reject` i nowy build.
  - Udokumentowane człony nazwisk (`ibn`, `de`) i wpisy z wielkiej litery nadal odpadają przez osobne reguły.
  - Wpis w `coverage.json`: `frag_graphic_word_provisional_user_approved`.
- **U/P — użycia wyczerpują ID.** Dla 19 interpretacji z przeglądem użyć (`config/generator/semantic-uses.json`):
  - pozostałość pełnego ID dostaje `semantic-remainder-exhausted-v1` = reject, więc nie daje osobnej analizy;
  - samo użycie dostaje `semantic-use-qualification-closed-v1` = accept (zamiast `semantic-use-qualification-pending-v1` = unresolved);
  - gra, wiek i pisownia są nadal oceniane osobno, więc warszawianka odpada w grze przez wielką literę, a dwójnasób, trójnasób, kroćset i wznak idą za decyzją o frag;
  - niezależne homonimy nie są objęte decyzją;
  - wpis: `documented_uses_exhaust_reviewed_ids_user_approved`.
- **R1 — decyzja klasowa.** Zamknięty przesiew z przypiętego SGJP zapisano w `literaki_slownik/resident_screen.py`:
  - 2 103 lematy `-anin` małą literą (analizy m1 i depr);
  - 2 051 istniejących lematów żeńskich `-anka` (analizy f).
  - Reguła `game-resident-screen-capital-2026-v1` daje reject w grze. Ortografia jest jak przy pozostałych mieszkańcach: STANDARD odrzuca zapis małą literą, BROAD go zachowuje.
  - Nie są objęte: 76 wyjątków (lemat męski i jego `-anka`), zapis wielką literą, inne rodzaje (np. `mezanin` m3) i lematy już rozstrzygnięte w `MANDATORY_CAPITAL_2026_LEMMAS`.
  - Wpis: `resident_screen_class_capital_with_76_exceptions_user_approved`.
  - Wyjątki wybrano ręcznie spośród wszystkich 2 103 lematów. Pomocniczo użyto dopasowania do toponimów SGJP (`scripts/probe_resident_toponyms.py`).
  - 12 niepewnych lematów, np. `nowomieszczanin`, `kartuzianin`, `górzanin`, pozostaje decyzją właściciela w przesiewie.

## Open Questions / Risks
- **R1 przyjmuje znane ograniczenie.** Przesiew nie obejmuje innych sufiksów mieszkańców (`-ak`, `-czyk`, `-ec`, `-ita`, np. warszawiak jest osobno). Te słowa przechodzą jak zwykłe rzeczowniki, choć część z nich RJP 2026 każe pisać wielką literą. To dolna granica, nie pełna klasa.
- **Ryzyka per słowo:**
  - pod lematem z przesiewu może kryć się także inne znaczenie (np. `zagórzanin`), a wtedy słowo odpada niesłusznie;
  - lista 76 wyjątków może być niepełna.
- **adjp i frag są warunkowe.** Przed wydaniem (G8) można je wycofać jedną zmianą.
- **Pozostają do zamknięcia** pending w `coverage.json`: `full_category_and_orthography_matrix` i `documented_game_conditions_without_sjp_editorial_source_policy`. Nie mają populacji per słowo; wymagają przeglądu macierzy klas.

## Dowody i testy
- RJP 2026 §8.1.2 pkt 3 (s. 43), §4.4 pkt 1; przypięty SGJP `sgjp-20260823`.
- Testy: `tests/test_owner_decisions_round2.py` (7 testów, red → green). Cztery testy dotychczasowych użyć odwrócono zgodnie z decyzją: pozostałość unresolved → reject z nową regułą. Niezależne homonimy pozostały bez zmian.
- Mutacje 10/10 czerwone (5 dla frag/U/P, 5 dla R1), pliki przywrócone (`cmp`).
- Suita 259/259 + audit 5/5.

## Pomiar po rundzie 2
Sonda `scripts/probe_unresolved_inventory.py` (sha 7dac4a30…b9d8) działała na tych samych bazach co inwentarz, na polityce v23, w trybie tylko do odczytu (`readonly_unchanged=true`). Czas 581 s, RSS 1,3 GB, wynik sha 743512c6…9023.

| Miara | BROAD po r. 1 | BROAD po r. 2 | STANDARD po r. 1 | STANDARD po r. 2 |
|---|---:|---:|---:|---:|
| słowa zależne od kategorii merytorycznej | 39 172 | **0** | 39 064 | **0** |
| definitywna odmowa | 1 548 934 | 1 587 045 | 1 937 814 | 1 975 863 |
| czyste (tylko placeholdery) | 3 468 877 | 3 469 938 | 3 080 105 | 3 081 120 |

Bilans:
- BROAD: 39 172 = 38 111 nowych odmów + 1 061 nowych słów czystych.
- STANDARD: 39 064 = 38 049 + 1 015.
- W obu wariantach odmowy + czyste = 5 056 983 kluczy, czyli wszystkie.

Unia słów zależnych BROAD∪STANDARD: 0 (przed rundami było 46 877). Wszystkie słowa zależą teraz tylko od dwóch placeholderów aktywacji (`linguistic-policy-not-active-v1`, `game-metadata-not-complete-v1`) i od dwóch pending macierzy w `coverage.json`.
