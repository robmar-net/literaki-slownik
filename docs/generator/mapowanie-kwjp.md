# Powiązania KWJP

## TL;DR
Pełne mapowanie lemma-all sprawdzono i niezależnie odtworzono.
Dopasowanie strukturalne nie potwierdza sensu ani dopuszczalności w grze.
Moduł links działa w build dla bezpośrednich form/leksemów; pełne powiązania konstrukcji nadal wymagają wykonania.

## Key Decisions
- NFC, zachowanie wielkości liter, lemma_base + identyczny POS; pełny lemma_id zostaje.
- F i pozostałe miary są przechowywane raz przy jednostce/listach korpusu. Kandydaci wskazują ten rekord.
- Bigramów nie sklejamy w częstość całego słowa; braków nie imputujemy.

## Open Questions / Risks
- Zgodność napisu i POS nie dowodzi zgodności znaczenia. Listy nie zawierają flagi zgadywania taggera.
- Nie ustalono szczegółowej semantyki części klas spoza SGJP; ich status pozostaje UNMATCHED, bez aliasu.
- G5 pozostaje częściowa: bezpośrednie powiązania są zintegrowane, pełne relacje konstrukcji i odbiór pozostają przed nami.

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

## Pełny przebieg techniczny powiązań
Na nowej kopii diagnostycznej powiązano wszystkie 5 066 341 jednostek z 13 list, tworząc 2 940 032 krawędzie kandydatów. Kontrola FK przeszła. Czas powiązań: 114,10 s; szczyt RSS: 117 948 416 B na macOS. To samodzielna kontrola techniczna bez konstrukcji, końcowej polityki ani odbioru G8.

[Raport mianowników](../../.maister/tasks/development/2026-10-04-generator-broad-standard/analysis/evidence/full-links-report.json) rozdziela każdą listę/gatunek, liczbę opublikowanych jednostek, sumę F, statusy dopasowań i krawędzie. Wszystkie opublikowane rekordy mają obserwację korpusową również przy UNMATCHED; dopasowanie i dostępność miary to różne własności. `link_report` odmawia raportu kompletności, gdy brakuje choć jednego powiązania. [Koszt przebiegu](../../.maister/tasks/development/2026-10-04-generator-broad-standard/analysis/evidence/full-links-performance.json).

## Integracja diagnostyczna z build

Komenda build tworzy bezpośrednie powiązania wszystkich zaimportowanych jednostek KWJP i reports/links.json; F pozostaje przy jednostce korpusu. Raport wskazuje osobno listy/gatunki i źródła niedostępne. Pełne powiązania konstrukcji nadal otwarte: links pozostaje pending, a wynik INCOMPLETE. Błąd zapisu powiązań oznacza links failed, zachowując zakończone importy. Testy generatora 106/106 i audytu 5/5 przeszły.

## Całe formy konstrukcji

Nowe relacje wskazują candidate_key przez FK tylko dla dopasowania całego napisu orth/orth_lc. Częstość korzenia nie przechodzi na konstrukcję; F nie jest powielane za homonimami lub śladami. Explain zachowuje zgodność wcześniejszych baz. Pełny etap links nadal wymaga pozostałych klas i odbioru.
