# G5 — przegląd kompletności powiązań KWJP

## TL;DR
Powiązano wszystkie 5 066 341 jednostek z 13 list (2 940 333 krawędzie, w tym 301 do kandydatów konstrukcji). Niezależna weryfikacja SQL: 0 braków, 0 nadmiarów, 0 jednostek bez powiązania, 0 niespójnych statusów, 0 naruszeń FK.
Etap `links` pozostaje `pending`: bramka wymaga `constructions=complete`, a ten etap jest otwarty. Build zwraca INCOMPLETE.
Dopasowanie strukturalne nie dowodzi sensu ani dopuszczalności. F jest przypisywane raz, do jednostki korpusu.

## Key Decisions
- `pos-map.json` (`pos-map-v1`) jest wczytywany z manifestu i walidowany. Przyjmowany jest tylko wtedy, gdy deklaruje `sense_identity_confirmed=false` i `allocate_frequency_to_candidates=false`, ma rozłączne zbiory kwjp_only i sgjp_only, a cele mieszczą się w klasach SGJP. Klasy kwjp_only i sgjp_only nie dostają aliasów.
- UNMATCHED ma jawny powód: `NO_POS`, `POS_OUTSIDE_EXPLICIT_MAP` albo `NO_STRUCTURAL_CANDIDATE`. AMBIGUOUS nie wybiera sensu i nie dzieli F.
- Etap `links=complete` ustawia wyłącznie `link_stage_gate`. Wymaga zer we wszystkich licznikach `verify_link_completeness` (oczekiwany zbiór krawędzi odtworzony niezależnie od `create_links`) oraz zakończonego etapu constructions. W przeciwnym razie częściowy zbiór kandydatów fałszywie wyglądałby na pełny.
- `word_availability`: statusy są liczone per lista i gatunek, z mianownikiem (próg i liczba jednostek) właściwym dla danej listy. Homograf konstrukcji dostaje NOT_IN_PUBLISHED_LIST zamiast statusu progowego. To ostrożny wybór: opublikowany segment nie jest całą formą. NKJP ma status UNAVAILABLE. Częstości segmentowanych form nie rekonstruujemy.

## Open Questions / Risks
- Decyzja potrzebna: semantyka klas KWJP `xxs` (9 887 jednostek UNMATCHED w lemma-all), `xxx` (4 048), `brev`/`sym`/`dig`/`interp`/`romandig`/`siebie`, a także ewentualne aliasy dla `cond`/`pacta`. Dziś te jednostki nie mają powiązań. Nie wpływa to na skład list.
- Decyzja potrzebna: czy homograf konstrukcji spoza listy (doń, jeśliby) ma pokazywać status progowy zamiast NOT_IN_PUBLISHED_LIST. Zmiana dotyczy tylko prezentacji dowodu.
- Ryzyko: F segmentu może być zaniżone dla homografów konstrukcji spoza bieżących klas (miałem = miał+em). Raport podaje to jako `tokenization_caveat`, bez korekty.
- `word_availability` nie jest jeszcze podpięte do `explain` (G6). Próbka jakości powiązań (`quality.sample_corpus_links`) i odbiór należą do G6/G8.

## Zakres i wejście
Wejściem była kopia `data/work/import-20261004-1302/build.sqlite`, otwarta przez `mode=ro` i skopiowana mechanizmem sqlite backup do `data/work/g5-20261005-225423`. Hashe artefaktów są identyczne z `config/generator/sources.json`. Bieżący zbiór kandydatów konstrukcji został zmaterializowany: 125 362 kandydatów, 282 112 składników. Polityka, kryteria i skład list nie zostały zmienione.

## Wyniki per lista (wybrane)
| Lista | Jednostki | EXACT | AMBIGUOUS | UNMATCHED | Krawędzie do form / leksemów / konstrukcji |
|---|---:|---:|---:|---:|---|
| 2grams-lemma-all | 1 627 126 | — | — | — | NOT_APPLICABLE, 0 krawędzi |
| lemma-all | 184 917 | 108 854 | 12 453 | 63 610 | 134 636 krawędzi do 95 173 leksemów (maks. 4 kandydatów na jednostkę) |
| lemma-fakt | 164 651 | 103 503 | 10 064 | 51 084 | 124 418 krawędzi do leksemów |
| lemma-fikcja | 134 453 | 93 960 | 7 082 | 33 411 | 108 789 krawędzi do leksemów |
| lemma-publicystyka | 157 968 | 99 234 | 11 742 | 46 992 | 123 576 krawędzi do leksemów |
| orth-all | 419 961 | 314 910 | 20 | 105 031 | 314 925 do form, 34 do konstrukcji |
| orth_lc-all | 360 472 | 280 983 | 33 805 | 45 684 | 348 603 do form, 45 do konstrukcji |

UNMATCHED w lemma-all według POS: subst 40 210, xxs 9 887, adj 5 192, xxx 4 048, brev 1 137. Pełny podział, sumy F per status i pozostałe listy znajdują się w [g5-links-completion.json](g5-links-completion.json).

Konstrukcje: 45 z 125 362 kandydatów ma krawędź korpusową (krawędź oznacza dokładny napis orth/orth_lc). Brak krawędzi nie znaczy, że częstość wynosi zero.

## Próbki dostępności
- kot: F=6756 występuje raz, przy rekordzie lematu. Ten rekord wskazuje dwóch kandydatów, kot:Sm1 i kot:Sm2. F nie jest mnożone.
- rok w fikcji: Rok:Sf i Rok:Sm1 mają status NOT_IN_PUBLISHED_LIST. rok:Sm3~lata i rok:Sm3~roki mają status OBSERVED i dzielą jeden rekord F=40 881.
- doń, jeśliby, czytajże, abyśmy: konstrukcje mają status NOT_IN_PUBLISHED_LIST z powodem segmentacji.
- Leksem jeśliby (comp) w lemma-all ma status ABSENT_OR_BELOW_PUBLICATION_THRESHOLD.
- Zapytanie o jedno słowo trwa od 0,3 do 15 ms po wymuszeniu kolejności złączenia od indeksu celu (`CROSS JOIN`).

## Wydajność (macOS)
Kopia: 11,1 s. Konstrukcje: 35,0 s. Powiązania: 159,4 s. Raport: 64,5 s. Weryfikacja: 31,2 s. FK: 23,4 s. Łącznie ok. 351 s. Szczytowe RSS: 1 344 192 512 B.

## Hash i odtworzenie
SHA-256 kanonicznego `links.json` (postać build, bez pól diagnostycznych skryptu): `49306c4746bcccd6a9e2d74e84aefc20c0d21f2fca92de2fa42259091f956d87`. SHA-256 pełnego wyjścia skryptu, z polami diagnostycznymi: `4699dc8b1d04bb9c128a801cf036bde3ed5268d826ceb5dedfa41c02e30008ea`.

```
PYTHONPATH=. python3 tmp/g5_full_links.py data/work/import-20261004-1302/build.sqlite data/work/g5-NOWY
PYTHONPATH=. python3 tmp/g5_samples.py data/work/g5-NOWY
```
Skrypty leżą w ignorowanym katalogu `tmp/`. Są cienką nakładką na `links.create_links`, `link_report(details=True)`, `verify_link_completeness`, `link_stage_gate` i `word_availability`. Tę samą ścieżkę przechodzi build w etapie links.
