# Oznaczenia SGJP bez pełnego objaśnienia — decyzja pierwszego wydania

## TL;DR

Pending: nie wdrożono zmiany kryterium. Pełny raport źródła obejmuje 605 dosłownych etykiet. Dla poniższych 25 oznaczeń nie ustalono dotąd pełnego, źródłowego objaśnienia. Dotyczą 1908 kompaktowych analiz źródłowych; to ekspozycja, nie liczba słów dopuszczonych do gry ani delta list.

## Wariant A — rekomendacja

Jawnie zmienić wymaganie pierwszego wydania dla zamkniętej listy poniżej: zachować oryginalne oznaczenie i informację „objaśnienie nieustalone”; sam brak jego objaśnienia nie wyklucza ani nie blokuje tej analizy. To odstępstwo od wymogu pełnego objaśnienia, nie dowód ustalenia semantyki.

Pozostałe warunki nadal obowiązują: jawna niepoprawność, dawność w STANDARD, samodzielność, klasa/nazwa, pisownia, reguły gry i profil. Brak objaśnienia etykiety nie daje automatycznego accept całej analizie. Znane warunki pozostałych składników nie mogą zostać pominięte. Nie dotyczy to nowych nieznanych etykiet, innych otwartych warunków ani `pisane_łącznie_z_przyimkiem` (osobna analiza niesamodzielnego składnika).

Wpisy oraz ślady pozostają w bazie. Późniejsze objaśnienie może zmienić ocenę w nowej wersji; nie podmieniamy zamrożonych list.

## Wariant B

Zachować pełne objaśnienie tych oznaczeń jako warunek pierwszego wydania. Do czasu zdobycia dowodów pozostają unresolved. Można kontynuować niezależne prace techniczne, lecz brak dowodu nie staje się ani automatyczną odmową językową, ani powodem uznania całego etapu za ukończony.

## Przykłady i granice dowodu

- `ciemni` / `ciemnia` z `fot.`: kandydat do zachowania mimo nieustalonego objaśnienia tego dokładnego skrótu; inne warunki osobno.
- `Abchaz` z `etn.`: pole nazwy pospolitej nie zwalnia z reguły obowiązkowej wielkiej litery. A nie dopuszcza tego zapisu do gry.
- `zagore` / `zagorzeć` z `podniosłe`: zachowujemy etykietę, a ocenę historii i poprawności przeprowadzamy osobno.
- `biblt.` w analizach `informatorium` nie otrzymuje domyślnego rozwinięcia „biblijne”. Nie zgadujemy skrótów z podobieństwa.

Aktualna [tabela oznaczeń SGJP](https://sgjp.pl/oznaczenia/) zawiera m.in. inne zapisy `fotogr.`, `astr.`, `etnon.`. Nie jest to samo w sobie dowodem tożsamości wszystkich etykiet w przypiętym eksporcie. W źródłowym `segmenty.dat` definicja `etnonimy subst:% labels=etn.%` (wiersz 672) daje związek `etn.` z etnonimami; nie utożsamiamy go z dziedziną etnologiczną ani nie deklarujemy pełnego objaśnienia wszystkich mieszanek.

Źródła liczb i przykładów: [pełne pokrycie](qualifier-condition-coverage.json) i [rzeczywisty odczyt](qualifier-coverage-runtime.json). Jednostki są kompaktowymi analizami importu, przed rozwinięciem tagów. Liczniki etykiet mogą się nakładać; 1908 policzono przez unię pól, nie sumę wierszy tabeli.

| Dosłowna etykieta | Analizy źródłowe | Przykład / pełny lemat / wiersz źródła |
|---|---:|---|
| `astrol.` | 11 | ascendencie / ascendent:Sm3 / wiersz 1160749 |
| `astrol.,ekon.` | 11 | descendencie / descendent:Sm3 / wiersz 1493865 |
| `astron.` | 192 | azymucie / azymut / wiersz 1180041 |
| `astron.,handl.` | 130 | nietranzytowana / tranzytować / wiersz 6015533 |
| `biblt.` | 11 | informatoria / informatorium / wiersz 1979651 |
| `char.,fot.` | 1 | ciemń / ciemnia / wiersz 1394448 |
| `char.,gry` | 1 | kręgielń / kręgielnia / wiersz 2263668 |
| `etn.` | 929 | Abchaz / Abchaz / wiersz 412 |
| `fot.` | 162 | ciemni / ciemnia / wiersz 1394438 |
| `gry` | 122 | banko / banko / wiersz 1196912 |
| `gry,zool.` | 11 | skoczek / skoczek:Sm2 / wiersz 5660547 |
| `gwar.,etn.` | 12 | Rusnacy / Rusnak:Sm1~cy / wiersz 788692 |
| `hom.,fot.` | 1 | ciemni / ciemnia / wiersz 1394437 |
| `hom.,gry` | 1 | kręgielni / kręgielnia / wiersz 2263657 |
| `kolej.` | 11 | ukres / ukres / wiersz 6137816 |
| `podniosłe` | 15 | zagore / zagorzeć / wiersz 6862210 |
| `pot.,etn.` | 13 | Angol / Angol / wiersz 9040 |
| `pot.,gry` | 11 | kręgiel / kręgiel / wiersz 2263614 |
| `pot.,slang` | 11 | dziuniek / dziuńka / wiersz 1677701 |
| `rzad.,etn.` | 1 | strzygoniów / strzygoń / wiersz 5831016 |
| `rzad.,fot.` | 1 | samowyzwalaczów / samowyzwalacz / wiersz 5578473 |
| `rzad.,slang` | 13 | flimon / flimon / wiersz 1778429 |
| `slang` | 79 | cwel / cwel / wiersz 1416492 |
| `slang,wulg.` | 26 | ciul / ciul:Sm2 / wiersz 1403986 |
| `spoż.` | 132 | jeliciarce / jeliciarka / wiersz 2034337 |

## Status

Decyzja oczekuje na odpowiedź użytkownika. Nie aktywowano nowej reguły ani wyłączenia wymogu. G3–G6 pozostają częściowe, a G7–G9 niewykonane. Wybór A nie domyka pozostałych wymagań K1–K10.
