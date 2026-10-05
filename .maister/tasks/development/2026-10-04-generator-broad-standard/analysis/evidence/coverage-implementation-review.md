# Diagnostyczny raport pokrycia klas

## TL;DR
Nowe build zapisują reports/coverage.json i wiążą go w indeksie kanonicznym. Raport rozlicza obserwowane klasy źródła/konstruktorów oraz zapisane oceny; INCOMPLETE pozostaje.

## Key Decisions
- Liczymy kompaktowe interpretacje i rozwinięcia tagów oddzielnie. Udokumentowane użycia nie zwiększają populacji źródłowej; pokrycie ocen źródła liczymy przez source_expansion + unresolved_remainder.
- Pusta klasa konstruktora nie dowodzi pokrycia. Nieznane konstruktory są jawne. Inwentaryzacja klasy nie dowodzi jej kwalifikacji semantycznej.
- Starszy import bez tabel ocen obsługiwany readonly: wszystkie rozwinięcia nieocenione. Częściowy schemat ocen lub konstrukcji odmawia raportu; baz nie migrujemy.
- COMPLETE_TECHNICAL_NOT_QUALIFICATION mówi tylko o zapisaniu ocen całej obserwowanej populacji źródła, nie o rozstrzygnięciu niewiadomych lub gotowości wydania.

## Open Questions / Risks
Pełna macierz semantyczna, przegląd jakości, finalne listy i wiązanie verify nadal otwarte. Indeks pozostaje diagnostyczny.

## Kontrole
Dwie regresje red→green i integracja build: rozdzielenie źródła/użyć, brakujące oceny, deterministyczny raport, indeks wiąże coverage, starszy schemat i odmowa częściowego schematu. Wcześniejszy runtime ujawnił brak tabel derivation_candidate w G2; obsłużono zgodność bez modyfikowania danych.

[Runtime readonly](coverage-runtime.json): pełny G2 7 458 520 kompaktowych interpretacji, 34 klasy, 17 234 910 rozwinięć bez utrwalonych ocen. Obie projekcje mieszkańca:22/28 źródłowych i42analizy, pokrycie źródła28/28 w obu wariantach. Dwa raporty każdej bazy identyczne; wszystkie hashe baz niezmienione. To nie dwa pełne build G8.

Odtwarzanie: PYTHONPATH=. python3 .maister/tasks/development/2026-10-04-generator-broad-standard/analysis/evidence/coverage-runtime-probe.py --run data/work/import-20261004-1302 --run data/work/resident-use-20261005-174732-a --run data/work/resident-use-20261005-174732-b --output tmp/coverage-runtime.json.
