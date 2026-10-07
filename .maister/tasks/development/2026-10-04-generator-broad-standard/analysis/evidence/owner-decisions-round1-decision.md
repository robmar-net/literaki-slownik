# Decyzje właściciela, runda 1: R2, adjp, `-by`, etykiety złożone

## TL;DR
Właściciel rozstrzygnął 2026-10-08 cztery kategorie z [inwentarza niewiadomych](unresolved-inventory.md), wszystkie na przypiętych SGJP i RJP, bez nowych źródeł.
- Etykiety złożone to koniunkcja warunków składowych.
- Formy adjp (`polsku`) są dopuszczone warunkowo, z oznaczeniem.
- Cztery formy `-by` zapisane łącznie w SGJP są dopuszczone.
- Sześć dosłownych przykładów mieszkańców z RJP wymaga wielkiej litery.

Polityka: `diagnostic-approved-conditions-v22`. Przesiew mieszkańców R1, frag oraz U/P pozostają otwarte na kolejne rundy.

## Key Decisions
- **Q — etykiety złożone.** Warunek etykiety złożonej (np. `archit.,hist.`) to koniunkcja warunków jej składników. Kod już tak liczył, więc decyzja tylko zamyka pending `all_compound_qualifier_semantics_and_variant_policy`. Listy się nie zmieniają. Wpis w `coverage.json`: `compound_qualifier_conjunction_user_approved`.
- **A — adjp, warunkowo.** Forma przyimkowa przymiotnika (`po polsku` → `polsku`) jest osobnym wyrazem graficznym według RJP §4.4 pkt 1, więc zostaje dopuszczona w grze. Na prośbę właściciela jest oznaczona do ewentualnego wycofania:
  - reguła `game-adjp-graphic-word-v1` ma pole `provisional: true` i widać ją w explain każdej analizy adjp;
  - wycofanie to zmiana `ADJP_GAME_STATUS` w `literaki_slownik/policy.py` z `accept` na `reject` i nowy build; tę ścieżkę pokrywa test;
  - słowa dotknięte decyzją można wskazać po `rule_id` w decyzjach bazy.
  Wpis: `adjp_graphic_word_provisional_user_approved`.
- **B — `-by` jako jeden wyraz.** `bodajby` (part), `niechby` (part), `kieby` (comp) i `jeźliby` (comp) przyjmujemy w zapisie łącznym SGJP. Lista RJP §4.5 pkt 1c zaczyna się od „np.”, więc ich nie wyklucza. Reguła: `orthography-sgjp-single-word-by-v1`, accept w obu wariantach. Wiek i gra są oceniane osobno: `jeźliby` (`daw.`) nadal odpada ze STANDARD przez wiek. Norma 2026 dla `jeśliby`/`jeżeliby` jest bez zmian. Wpis: `by_single_word_sgjp_user_approved`.
- **R2 — dosłowne przykłady RJP.** Dosłowny przykład w RJP 2026 §8.1.2 pkt 3 (s. 43) wystarcza jako dowód klasy „nazwa mieszkańca” dla pełnego lematu SGJP. Do `MANDATORY_CAPITAL_2026_LEMMAS` dopisano `krakowianin`, `krakus`, `kresowianin`, `rzymianin`, `sądeczanin` i `zatorzanin`. Obowiązuje istniejąca reguła: odmowa w grze; STANDARD odrzuca zapis małą literą, BROAD go zachowuje. Wpis: `rjp_literal_resident_examples_capital_user_approved`.
  - `bawarka` (`kulin.`, napój) nie jest objęta decyzją.
  - Formy żeńskie (`krakowianka`, `rzymianka`, `krakuska`) również nie; należą do R1 lub pozostają bez dowodu.
  - Nazwisko `Krakus` oraz lematy `Rzymianin`/`Sądeczanin` (wielka litera w SGJP) nie są objęte decyzją.

## Open Questions / Risks
- `rzymianin` i `krakus` mogą mieć w SGJP pod tym samym ID inne znaczenie. Pięciopolowy eksport tego nie pokazuje. Właściciel przyjął to ryzyko.
- adjp to decyzja warunkowa. Przed wydaniem (G8) właściciel może ją wycofać jedną zmianą.
- Pozostają otwarte:
  - R1 — przesiew `-anin/-anka`; możliwa tylko decyzja klasowa;
  - F — frag;
  - U/P — pozostałość udokumentowanych użyć;
  - pending `full_category_and_orthography_matrix` i `documented_game_conditions_without_sjp_editorial_source_policy`.

## Dowody
- RJP, Zasady pisowni i interpunkcji polskiej, wersja jednolita 11-2025 (sha 87daaddd…d72e): §4.4 pkt 1, §4.5 pkt 1c–d, §8.1.2 pkt 3 (s. 43).
- Przypięty SGJP `sgjp-20260823`. Wiersze przykładów są w [inwentarzu](unresolved-inventory.md).
- Testy: `tests/test_owner_decisions_round1.py` (5 testów). Mutacje 4/4 czerwone: usunięcie lematów R2, zmiana statusu adjp na reject, usunięcie znacznika, wyłączenie reguły `-by`.

## Pomiar po rundzie 1
Sonda `scripts/probe_unresolved_inventory.py` (sha 0950507b…b987) liczy teraz adjp, `-by` i Q jako rozstrzygnięte (`OWNER_RESOLVED`), a bawarkę jako niebędącą mieszkanką. Uruchomiono ją na tych samych bazach co inwentarz i na polityce v22. Bazy pozostały niezmienione (`readonly_unchanged=true`). Czas 486 s, RSS 1,4 GB, wynik sha 59ba28e8…b987.

| Miara | BROAD przed | BROAD po | STANDARD przed | STANDARD po |
|---|---:|---:|---:|---:|
| słowa zależne od kategorii merytorycznej | 46 802 | 39 172 | 46 406 | 39 064 |
| z warstwą formalną Q | 682 739 | 39 172 | 305 059 | 39 064 |
| definitywna odmowa | 1 548 874 | 1 548 934 | 1 937 754 | 1 937 814 |
| czyste (tylko placeholdery) | 2 825 370 | 3 468 877 | 2 814 170 | 3 080 105 |

Unia BROAD∪STANDARD słów zależnych: 46 877 → 39 245.

Pozostałe kategorie:

| Kategoria | BROAD | STANDARD |
|---|---|---|
| R1 przesiew `-anin/-anka` | 39 095 | 38 997 |
| F frag | 67 (62 jedyne) | 57 (53) |
| U pozostałość użyć | 15 (10) | 14 (10) |
| P kod `semantic-use-qualification-pending-v1` | 4 | 3 |

R2 dało +60 odmów w każdym wariancie (6 lematów × 10 słów). Bawarka przechodzi do słów czystych.
