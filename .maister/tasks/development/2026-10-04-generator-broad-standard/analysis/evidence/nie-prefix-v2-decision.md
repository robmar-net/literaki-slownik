# Konstrukcja nie- v2: bez zaimków i nieodmiennych (#5)

## TL;DR
`nie-prefix-degree-v1` tworzyła słowa od zaimków i przymiotników nieodmiennych (`nieta`, `nieżaden`, `niewideo`). Reguła `nie-prefix-degree-v2` je pomija. Na danych v29 z list wypada 346 słów BROAD i 336 STANDARD. Zmiana wejdzie przy następnym buildzie list. Decyzja jest odwracalna.

## Problem
SGJP oznacza tagiem `adj`/`adv` także zaimki przymiotne (`ten`, `nasz`, `żaden`) i słowa nieodmienne (`wideo`, `super`, `fair`). ZDS §5 i pisownia 2026 każą pisać `nie` łącznie z przymiotnikiem i przysłówkiem odprzymiotnikowym. Z zaimkiem i słowem nieodmiennym piszemy osobno: „nie ta”, „nie tak”, „nie fair”. Źródło: strona wiki „Słowa spoza SJP.pl” (2026-10-12).

## Reguła v2
- **Zaimki:** zamknięty zbiór `NIE_PRONOMINAL_LEMMAS` w `literaki_slownik/constructions.py`, porównywany po bazie lematu:
  - zaimki przymiotne: wskazujące, pytające, nieokreślone, ogólne, przeczące, dzierżawcze;
  - przysłówki zaimkowe ze stopniem w SGJP: `tak`, `jak`, `siak`, `owak`, `samo`, …
- **Nieodmienne:** `nie_indeclinable_lemmas(db)`, czyli lemat `adj` z jedną formą przy wielu tagach. Wylicza się z danych SGJP, bez ręcznej listy; dziś 95 lematów. Ta sama baza wyklucza przysłówek z tej pary (`super:D`). Pojedynczy wiersz nie wystarcza, bo niepełny leksem nie dowodzi nieodmienności.
- **Bez zmian:** przymiotniki odmienne w każdym stopniu (`nietani`, `niedroższy`) i przymiotniki liczebnikowe (`niepierwszy`). Liczebnikowe to osobna kwestia, nie badana.

## Pomiar (v29, przebieg `lists-v30-20261010-165826-a`, tylko odczyt)
| | BROAD | STANDARD |
|---|---:|---:|
| słowa, które wypadną | 346 | 336 |
| w tym od zaimków | 275 | 268 |
| w tym od nieodmiennych | 71 | 68 |
| wystąpienia w KWJP, razem | 263 | 263 |

- Każde słowo z listy, które ma kandydata odrzuconego przez v2, nie ma innego źródła, więc wypada.
- Wystąpienia w KWJP mają tylko `nieta` (211), `nietę` (20), `nietą` (16), `nieto` (11) i `niewideo` (5). To zapewne „nie ta” zapisane łącznie.
- Przejrzałem pełną listę: same zaimki i nieodmienne. Hasła SGJP z własnym wpisem, np. `nieswój`, zostają.

## Status
Kod i testy: `tests/test_round5_zds.py`. Listy, wydanie i wiki zmienią się przy następnym buildzie, razem z innymi zmianami (decyzja właściciela, 2026-10-12).
