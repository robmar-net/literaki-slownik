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
