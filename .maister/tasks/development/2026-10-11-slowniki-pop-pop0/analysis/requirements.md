# Wymagania: POP i POP0

## TL;DR
Dwa słowniki popularnych słów, podzbiory STANDARD z LL-PL v29, budowane szybkim krokiem tylko do odczytu z KWJP i NKJP. Najpierw skrypt pomiarowy i decyzje właściciela, potem polecenie `pop`, odbiór i wydanie `pop-v1`.

## Key Decisions
- POP: leksemy z typowymi formami; rozmiar wg pokrycia tekstów; kandydat na słownik gry (opcja stołu) i słownik botów.
- POP0: o rząd wielkości mniejszy; słownik słabszych botów.
- Źródła: tylko KWJP (z `build.sqlite` zamrożonego przebiegu) i NKJP 1grams (ADR-006). SJP.pl tylko jako miara.
- Dwie stałe listy, bez skali ciągłej. Pakiet osobny, wydanie jak LL-PL; integracja z serwerem poza zakresem.
- Bez nowego pełnego buildu: krok pochodny nad zamrożonym LL-PL v29, przypięty jego hashami.

## Open Questions / Risks
- D1–D8 do decyzji po raporcie pomiaru (zob. scope-clarifications.md).

## Opis początkowy
GitHub #3. POP: bardzo szeroki, kandydat na słownik gry dla graczy, którzy chcą normalnej rozgrywki bez nieznanych słów, i na słownik botów, żeby układały znane słowa. POP0: bardzo ograniczony, dla słabszych botów, żeby naturalnie grały gorzej.

## Pytania i odpowiedzi (właściciel, 2026-10-11)
| pytanie | odpowiedź |
|---|---|
| Jednostka | leksem z typowymi formami |
| Rozmiar POP | wg pokrycia tekstów |
| Potoczne | tylko korpusy; zmierzyć lukę (różnica rang NKJP–KWJP, kwalifikator „pot.” z SGJP, przykłady) |
| Zakres | pomiar → decyzje → implementacja → odbiór → wydanie, jedno zadanie |
| Warianty form | zmierzyć „typowe formy” i „pełna odmiana”, wybór po pomiarze |
| Przegląd próbek | 30 na warstwę, stały seed; agent ocenia, właściciel zatwierdza |
| Pakiet | osobny, GitHub Release `pop-v1`; integracja z grą poza zakresem |
| Budowa | z zamrożonego LL-PL v29, nowe polecenie `pop`, minuty |
| Poziomy | dwie stałe listy |

## Wymagania funkcjonalne
1. Skrypt pomiarowy tylko do odczytu (`scripts/measure_pop.py`): przypina bazę hashami; raport D1–D8 z tabelami i próbkami granicznymi; wynik w nowym `data/work/pop-measure-*`.
2. Raport dla właściciela po polsku; decyzje zapisane jako odwracalne ADR.
3. Polecenie `pop` (moduł `literaki_slownik/pop.py`): własny manifest (`config/generator/pop-sources.json`), przypięta konfiguracja progów, nowy katalog wyjściowy; listy POP i POP0, raporty z miarami i hashami, próbki jakości (własna konfiguracja, nie quality-v1).
4. `explain` dla POP/POP0: dlaczego słowo jest albo go nie ma (ranga, miary, status danych).
5. Odbiór: POP0 ⊆ POP ⊆ STANDARD; dwa niezależne przebiegi identyczne; baza LL-PL niezmieniona; brak danych ≠ 0; brak kopiowania frekwencji między homonimami; przegląd próbek zatwierdzony przez właściciela.
6. Wydanie `pop-v1`: listy `.txt.gz`, pakiet z raportami, SHA256SUMS, ATTRIBUTIONS (KWJP + NKJP wg ADR-006), LIMITATIONS; bez surowego NKJP.
7. Wiki: strony `Slownik-POP`, `Slownik-POP0`, wiersze w Home i _Sidebar, Historia zmian; zaznaczyć, że POP ⊆ LL-PL STANDARD, nie ⊆ SJP.

## Kod do ponownego użycia
`scripts/benchmark_sjp.py` (przepływ), `database.connect(readonly=True)`, `canonical.{dumps,write_json,sha256,load_json}`, `inputs.checked_file`, `GeneratorError`, `run.code_identity`, `export.rename_noreplace`, `quality.sample_strata`/`review_template`, `kwjp.rows`, parser z `scripts/audit_nkjp.py`, fikstury `tests/helpers.py`, `tests/release_helpers.py`, `tests/test_kwjp.py`.

## Zasoby wizualne
Brak (bez UI).

## Granice
- Poza zakresem: integracja z serwerem i botami, słowniki branżowe, nowy build LL-PL, zmiana `sources.json`/`inputs.py` LL-PL.
- Nie używamy list zewnętrznych (Jasnopis, Logios, Zgółkowa, Kurzowa, PSONI, SJP.pl jako wejście).

## Uwagi techniczne
- Nie pisać do zamrożonego przebiegu. Ładować `corpus_evidence` per `source_id`; unikać złączeń bez kierunku (`LEFT JOIN evidence_candidate` >10 min) i sortowania dużego tekstu w SQLite.
- KWJP dzieli formy przeszłe (`zrobił+em`): brak w orth ≠ 0. NKJP: brak progu, interpunkcja doklejona, kolizje typu `ul.`→`ul`.
- Pokrycie: sufit 93,5% wobec wszystkich tokenów KWJP; raportować kilka mianowników.
