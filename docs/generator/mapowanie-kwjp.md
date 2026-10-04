# Powiązania KWJP

## TL;DR
Pełne mapowanie lemma-all sprawdzono i niezależnie odtworzono.
Dopasowanie strukturalne nie potwierdza sensu ani dopuszczalności w grze.
Moduł links ma testy; nie jest jeszcze włączony do pełnego przebiegu build.

## Key Decisions
- NFC, zachowanie wielkości liter, lemma_base + identyczny POS; pełny lemma_id zostaje.
- F i pozostałe miary są przechowywane raz przy jednostce/listach korpusu. Kandydaci wskazują ten rekord.
- Bigramów nie sklejamy w częstość całego słowa; braków nie imputujemy.

## Open Questions / Risks
- Zgodność napisu i POS nie dowodzi zgodności znaczenia. Listy nie zawierają flagi zgadywania taggera.
- Nie ustalono szczegółowej semantyki części klas spoza SGJP; ich status pozostaje UNMATCHED, bez aliasu.
- G5 pozostaje częściowa: pełne powiązania wszystkich list i integracja build są przed nami.

SGJP ma 34 klasy, KWJP lemma 39; 32 wspólne nazwy mają jawne mapowanie w `config/generator/pos-map.json`. Pozostałe KWJP `dig,interp,romandig,siebie,sym,xxs,xxx` pozostają niedopasowane. SGJP `cond,pacta` nie otrzymują wymyślonych aliasów.

| Wynik dla 184 917 jednostek lemma-all | Liczba |
|---|---:|
| jeden kandydat lemma/POS | 108 854 |
| wielu kandydatów | 12 453 |
| brak dopasowania | 63 610 |

Przykłady z SGJP/KWJP: zamek i rok mają wiele pełnych ID; polski/A i polski/S pozostają odrębne. Dwie nie-NFC jednostki nie dopasowały się również po NFC. Nie usuwamy diakrytyków. Pełny raport jest w `analysis/evidence/kwjp-mapping.json` aktywnego zadania.

[Instrukcja KWJP](https://kwjp.pl/manual) wskazuje [dokumentację Korpusomatu](https://korpusomat.readthedocs.io/pl/latest/mtas.html), która wyjaśnia segmentację i anotację Morfeusz/Concraft, w tym analizę odgadniętą dla słów nieznanych. Rozdzielenie segmentów uniemożliwia wnioskowanie o nieobecności pełnej formy wyłącznie z list orth. Zgodność POS jest mapowaniem strukturalnym, nie rozpoznaniem sensu.

[Opis list](https://kwjp.pl/lists/doc/about/) podaje globalny próg publikacji F≥5. Gatunkowe F=1–4 są prawidłowe; brak w gatunku nie dowodzi F<5. Miary i mianowniki pozostają odrębne. Parser zachowuje nazwę CSV Dice bez zmiany nazwy ani wartości.

Odtworzenie: `python3 scripts/probe_generator_evidence.py --database PATH --mode kwjp`. Cztery testy `tests.test_links` obejmują homonimię, case/NFC/POS, formy/orth_lc/bigramy, brak versus zero oraz jednorazowe F z relacjami FK. Test-first: brak modułu → 4/4 green; cała suita 25/25.
