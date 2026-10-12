# Runda 5 — niezależna kontrola pomiaru POP

## TL;DR

Potwierdzono skład wariantów, przycinanie i wyniki obu populacji STANDARD. Kontrola używa własnych algorytmów na zapisanym grafie oraz niezależnego SQL dla oryginalnych wierszy KWJP. Nie przebudowuje grafu ani morfologii. Dwie naprawy diagnostyki dyspersji były konieczne; wynik sprzed napraw jest nieważny. Ten audyt potwierdza pomiar, nie wybiera progu POP.

## Key Decisions

- **Dowód:** zgodność 10 limitów liczby i 6 progów punktacji w każdej populacji; pełne formy, hashe i oba mianowniki sprawdzone dla pięciu głównych wariantów oraz 11 wariantów diagnostycznych.
- **Dowód:** dyspersja korzysta z OR oryginalnych wierszy KWJP, których kandydaci mają tę samą podstawę lematu. ARF i F pochodzą z jednego wiersza; singletony mają własny dowód. Siatka 25 pól oraz próbka 300 podstaw są odtworzone.
- **Rekomendacja:** użyć poprawionych pomiarów do decyzji po ocenie jakości próbki. Nie uznawać pokrycia tokenów, wartości 0,05 ani samego przejścia testów za uzasadnienie docelowego progu.

## Open Questions / Risks

- Niezależność zaczyna się od cache grafu i form. Budowa grafu, wyliczone miary oraz przypisanie źródeł nie zostały ponownie odtworzone z całości surowych danych.
- `unknown` oznacza brak oryginalnego wiersza spełniającego warunek wspólnej podstawy kandydatów. Nie dowodzi nieobecności słowa w KWJP. Zachowanie takich pozycji jest jawnym fallbackiem, nie dowodem rozproszenia.
- Grupowanie po podstawie nie rozstrzyga znaczeń homonimów. Próba jest warstwowa i oparta na baseline; bez wag nie daje odsetka błędów całego słownika. Warianty diagnostyczne nie stanowią zatwierdzonej specyfikacji POP.

## Wyniki odtworzenia

Stan źródeł odczytany 2026-10-12. W tabeli: leksemy po przycięciu / unikalne formy. Szczegółowe hashe, liczniki i zakres kontroli: [raport JSON](measurement-review.json). Wyniki źródłowe: [baseline](baseline-measurements.json), [proposal](proposal-measurements.json).

| Wariant | Obecny STANDARD | Proponowany STANDARD |
|---|---:|---:|
| Limit 60k | 53 002 / 1 227 250 | 52 921 / 1 227 192 |
| Limit 70k | 63 015 / 1 424 934 | 63 047 / 1 427 316 |
| Limit 80k | 72 997 / 1 636 683 | 73 029 / 1 639 065 |
| Stały próg z baseline 60k | 53 002 / 1 227 250 | 53 033 / 1 229 622 |
| Stały próg 0,05 | 63 851 / 1 443 064 | 63 883 / 1 445 446 |

Baseline 60k odtwarza dokładnie opublikowany POP, a zapisany POP0 jest zgodny z plikiem wydania. Proponowany STANDARD to baseline powiększony dokładnie o 2382 formy z rundy 3; delta POP 60k również jest identyczna z [pomiarem rundy 3](../round3/pop-impact.json). Dla pięciu głównych wariantów odtworzono liczbę dodatków i ubytków oraz pełne listy ubytków w [porównaniu populacji](standard-sensitivity.json).

Limit liczby działa **przed przycięciem**, zachowuje całe bloki remisów i może zatrzymać się poniżej limitu. Warianty `count` stosują obecną rangę własną; warianty `score` porównują własną miarę ze stałym progiem i zachowują istniejące wyjątki najmocniejszego członka oraz grup bez rozdzielnego dowodu. `score-0.05` oznacza próg `log10(0,05)`, nie punktację liczbową ≥ 0,05. To jawne, różne warianty badawcze. Źródło: [kod pomiaru](../../round5_measure.py), funkcje `run_scenario`, `value_prune`.

Pokrycie też jest zgodne. `kwjp-all` ma stały mianownik **81 664 894**, a `kwjp-standard` odpowiednio **74 540 021** i **74 542 063**. Ten drugi zmienia się ze STANDARD. Baseline 60k/70k/80k daje 98,5951% / 98,6458% / 98,6600% względem `kwjp-standard`, ale 89,9931% / 90,0395% / 90,0523% względem `kwjp-all`. Niejednoznaczny wiersz jest pokryty dopiero po wybraniu wszystkich kandydatów. Pokrycie tokenów nie mierzy znajomości słów ani jakości każdego dodanego leksemu. Źródła: oba pliki pomiarów i [metodologia](methodology-sources.md).

## Dyspersja, próbkowanie i historia napraw

Niezależne złączenie SQLite odnalazło **121 308** oryginalnych wierszy, których kandydaci mają jedną podstawę lematu. Z tych wierszy odtworzono wszystkie składy 8 filtrów na 80k, 3 absolutnych wariantów F/ARF oraz 25 pól siatki w każdej populacji. Przykład baseline: ARF ≥ 3 i ARF/F ≥ 0,1 daje **55 677 leksemów / 1 257 654 formy**; zachowanie 15 196 pozycji `unknown` daje **70 873 / 1 603 293**. To wpływ odmiennej polityki braków danych.

Naprawiono dwa błędy pierwszego pomiaru:

1. Dowód singletonu był szukany wyłącznie w podjednostkach grupy. Trafiał do `unknown` mimo własnego KWJP. Obecny kod próbki korzysta również z własnej jednostki singletonu; potwierdzono **261** takich wpisów dowodowych.
2. ARF bywał brany z najlepszego wiersza, a F z agregacji. Ich iloraz nie opisywał jednego rekordu. Obecne sondy stosują OR oryginalnych wierszy i dzielą ARF przez F tego samego rekordu, bez przenoszenia na inne podstawy.

Pierwotne **17 894 leksemy / 391 166 form / 9168 braków częstych form** nie służą do oceny metody dyspersji. Historia korekty jest zapisana jako `diagnostic_correction`, a moment ukończenia w `diagnostics_corrected_at` w [manifeście](input-manifest.json).

Dodatkowo wykryto i sprawdzono naprawę błędu raportowania: trzy absolutne warianty KWJP miały `unknown_lexemes = 0`, bo nie przekazano zbioru do funkcji zapisującej wynik. Prawidłowa liczba w całej ich populacji to **154 307 dla baseline i 154 310 dla proposal**. Korekta z 10:31:12 UTC nie zmienia wybranych leksemów, form ani pokrycia. Hash końcowego skryptu odpowiada manifestowi; raport JSON zachowuje hashe pełnego odtworzenia i osobno późniejszej kontroli metadanych.

Odtworzono dobór wszystkich 300 podstaw z ziarna i funkcji hashującej, wielkości populacji warstw oraz dowody oryginalnych wierszy. Próbkę rozbieżności dyspersji wygenerowano po korekcie. Źródła: [schemat próby](sample-design.json), [próbka](sample-blind.json), [niezależny skrypt](../../round5_independent_check.py).

## Profile pasm

Osobny odczyt SQL i własne liczenie potwierdziły wszystkie sześć pasm w [band-profiles.json](band-profiles.json), w tym liczniki grup. Pasmo oznacza **nowe podstawy lematu pojawiające się między zbiorami po przycięciu**, nie różnicę liczby leksemów ani jednostek rankingu. Bez własnego oryginalnego wiersza jest **4981 / 9837 (50,6354%)** podstaw pasma 60–70k oraz **8409 / 9881 (85,1027%)** pasma 70–80k. To zmiana dostępności rodzaju dowodu, nie automatyczny werdykt jakości.

Mediana `own_F_sum` sumuje różne oryginalne wiersze tej samej podstawy i uwzględnia wyłącznie podstawy z takim dowodem. ARF i ARF/F pochodzą z pojedynczego wiersza o najwyższym **F** (remis rozstrzyga numer wiersza), nie z maksimum ani sumy ARF. Liczniki statusów, flag i gatunków dotyczą wybranych grup: jedna podstawa może wystąpić w kilku grupach. Nie należy interpretować ich jako liczby własnych wierszy KWJP. Źródło: [skrypt profili](../../round5_profiles.py).

## Zakres techniczny i testy

[Niezależny skrypt](../../round5_independent_check.py) nie importuje `pop.py` ani skryptu pomiarowego. Własnymi funkcjami odtwarza cięcia, rangi własne do przycinania, sumę form, SHA256 i pokrycie. Oryginalne wiersze pobiera własnym SQL przez połączenie tylko do odczytu. Rozmiar i czas modyfikacji bazy pozostały niezmienione. SHA256 całej bazy pochodzi z manifestu koordynatora; w tej kontroli nie haszowano ponownie 22 GB.

Kod zapisuje dla NKJP statusy, flagi i zagregowane wyniki. Odczyt ścieżek zapisu i skan publicznych JSON rundy 5 nie wykazały surowego NKJP F. Cache zawierający dane wejściowe pozostaje w ignorowanym `tmp/`.

Jednorazowo wykonano **25 testów, wszystkie PASS**: `PopRankingTests`, `PopPruneTests`, `VariantPoolTests`, `SharedDominantTests`, `AsymmetricBoundTests`, `NkjpOutdatedTests` z [test_pop.py](../../../../../../../tests/test_pop.py) oraz [test_pop_v2.py](../../../../../../../tests/test_pop_v2.py). Testy produkcyjne wspierają interpretację istniejącego mechanizmu; poprawność skryptu badawczego sprawdza osobne odtworzenie opisane wyżej.

Źródła interpretacji mechanizmu: [ADR-007](../../../../../../../docs/adr/ADR-007-metoda-pop-v1.md), [mapowanie KWJP](../../../../../../../docs/generator/mapowanie-kwjp.md) oraz [audyt rundy 4](../round4/pop-method-review.md). Nie wdrożono zmiany progu, reguł ani list.
