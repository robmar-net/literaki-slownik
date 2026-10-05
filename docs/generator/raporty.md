# Raport wpływu filtrów

## TL;DR
`literaki_slownik.reports.filter_impact` liczy samodzielne, kolejne i łączne efekty filtrów.
Oddziela odrzucone analizy od kluczy słów pozbawionych wszystkich analiz.
Przetwarza posortowane grupy strumieniowo; nie sumuje nakładających się strat.
Dotyczy dostarczonych analiz, nie domniemanej kompletności wydania.

## Key Decisions
- Klucz odpada dopiero po odrzuceniu wszystkich jego analiz. Jedna poprawna analiza może zachować napis.
- Efekt kolejny przypisujemy w jawnie podanej kolejności; wcześniej odrzucone jednostki nie są liczone ponownie jako nowe.
- Nieznane warunki pozostają unresolved, a nie reject.
- Raport odmawia pominięcia reguły, która odrzuciła którąkolwiek analizę; odmawia też statusów sprzecznych z warunkami.

## Open Questions / Risks
- Pełna integracja z build i wszystkimi konstrukcjami pozostaje do wykonania.
- Pusta populacja ma EMPTY_NOT_COVERAGE, a obecność raportu nie nadaje VERIFIED.
- Liczniki podanych analiz nie obejmują niezbudowanych interpretacji i nie są końcową deltą list BROAD/STANDARD.

## Kontrakt

`filter_impact(groups, variant, rule_order)` przyjmuje iterator grup `{key, analyses}` w rosnącej kolejności kluczy. Każda grupa musi być niepusta, unikalna i zawierać wyłącznie analizy własnego klucza. Format analizy odpowiada `assess_analysis`.

Raport podaje: mianowniki kluczy i analiz, samodzielne odrzucenia, nowe i skumulowane odrzucenia po każdym filtrze, efekt łączny oraz rozkład accept/reject/unresolved dostarczonych analiz po agregacji do kluczy. To rozkład ocen podanych analiz; nie jest deklaracją gotowości listy wydania.

Testy: `python3 -m unittest tests.test_reports`. Pokrywają nakładanie filtrów, usuwanie różnych homonimów przez różne reguły, zmianę kolejności, niewiadome, puste grupy, błędne statusy i niepełną listę filtrów.

[Diagnostyczny runtime](../../.maister/tasks/development/2026-10-04-generator-broad-standard/analysis/evidence/filter-report-runtime.json) obejmuje osiem rzeczywistych kluczy i 15 interpretacji. Znane warunki wielkiej litery i profilu są w jawnej kolejności obok filtra wieku; nie pomijamy ich w raporcie.

## Pokrycie warunków kwalifikatorów

`qualifier_coverage(fields)` przyjmuje unikalne pary (pełne pole kwalifikatorów, dodatnia liczba kompaktowych interpretacji). Używamy inwentaryzacji po deduplikacji, nie surowych wierszy i nie rozwiniętych tagów. Duplikaty pól i błędne liczniki są odrzucane. Raport jest deterministyczny niezależnie od kolejności wejścia.

`labels` zachowuje dokładne etykiety, liczniki i warunki obu wariantów. `fields` wiąże je z pełnymi polami; `unmapped_labels` pokazuje etykiety bez żadnego znanego warunku. `full_qualification_pending` zawsze true: dodatnia ocena jednego warunku nie oznacza akceptacji całej analizy. Brak warunku i brak kwalifikatora nie są automatycznym accept. Przecinek pozostaje częścią etykiety; powtórzona etykieta w polu nie podwaja licznika. Liczniki etykiet i kategorii mogą się nakładać.

Nowe build zapisują reports/qualifier-conditions.json, zachowując INCOMPLETE i reports pending. Istniejący przebieg można zbadać bez modyfikacji:

```sh
python3 scripts/probe_generator_evidence.py --mode qualifier-conditions --database PATH/build.sqlite
```

[Pełny przegląd i wyniki](../../.maister/tasks/development/2026-10-04-generator-broad-standard/analysis/evidence/qualifier-coverage-review.md): 26 etykiet bez warunku, 1 910 interpretacji, dwa identyczne raporty. Nie jest to delta list ani pełny odbiór.

## Logiczna treść bieżącej bazy

Wdrożono A dla25dosłownych oznaczeń bez pełnego objaśnienia: source_label zachowany, gloss_status=unestablished, inne kryteria osobno. Pełny runtime:1908kompaktowych analiz, dwa identyczne raporty, sześć readonly explain; wielka litera Abchaz nadal odrzuca growo. Dodano logical-content bieżącego schematu do build:10zamkniętych relacji, klucze źródłowe zamiast ID, wykrywanie nowych tabel/kolumn i niespójnych FK. Testy potwierdzają identyczność po zmianie ID i zmianę hasha po modyfikacji powiązań/kwalifikatorów. To nie pełny indeks kanoniczny ani odbiór G8.

reports/logical-content.json jest diagnostyczną kontrolą bieżącego schematu; po utrwaleniu decyzji kwalifikacji kontrakt musi zostać rozszerzony. Zmiana kodu lub schematu wymaga nowego build, wcześniejszych baz nie migrujemy.

## Niewiadome zapisanych ocen

Nowe build tworzą reports/unresolved.json: osobno liczby analiz i kluczy słów w BROAD/STANDARD, status członkostwa i niewiadome w każdej warstwie. Znana odmowa nie usuwa niewiadomych; wspólne payloady nie zaniżają liczby analiz, a powtórzony check nie zawyża liczby dotkniętych analiz. Wynik słowa zachowuje dopuszczony homonim. Raport odmawia niepełnego zapisu lub niezgodnych hashy/statusów. To diagnostyka, INCOMPLETE i pełne reports pending; nie nadaje VERIFIED. [Przegląd i runtime](../../.maister/tasks/development/2026-10-04-generator-broad-standard/analysis/evidence/unresolved-report-review.md).

## Wpływ filtrów z zapisanych ocen

Nowe build zapisuje `reports/filter-impact.json`: samodzielne, kolejne i łączne odmowy, dla wszystkich utrwalonych analiz każdego wariantu. Kolejność ID reguł jest leksykograficzna i jawnie diagnostyczna, nie ustala pierwszeństwa reguł językowych. Odmowa analizy nie usuwa słowa z dodatnim lub nierozstrzygniętym homonimem. Unknown nie jest odmową. Przed raportem wymagane jest pełne pokrycie zapisanych ocen obu wariantów, zgodność statusów i hashy powodów; uszkodzenie odmawia raportu. Oznaczenie zakresu pozostaje `all_persisted_assessments_not_full_release`, bez promocji do VERIFIED.
