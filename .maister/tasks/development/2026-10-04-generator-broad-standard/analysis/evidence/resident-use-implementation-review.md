# Jawna relacja mieszkańca — wdrożenie

## TL;DR
Zatwierdzone A wdrożono w runtime v18 dla udokumentowanego użycia warszawianka i całego jego źródłowego paradygmatu. Pozostałość i geograficzny homonim zachowane. To fragment G3/G4/G6, bez pełnego wydania.

## Key Decisions
- 11 dokładnych rekordów SGJP, 14 rozwinięć; dowód własnej obserwacji i normy2026 przypięte hashami. Metadane online nie stały się wejściem maszynowym.
- Growy obowiązek wielkiej litery odrzuca tylko sprawdzone użycie. STANDARD odrzuca dawny małoliterowy zapis; BROAD nie wyklucza przez ten warunek językowy, inne warunki nadal obowiązują.
- Nie dodano warszawianka do globalnego zbioru leksemów mieszkańców. Nieznana pozostałość i inne znaczenia nie przejmują reguły.
- Kontrola przed zapisem odmawia zmienionych pól/wierszy/hashów/dowodów/warunków. Czytnik odmawia także usunięcia reguły z poprawnie przeliczonym hashem i spójnymi statusami.

## Open Questions / Risks
Pełna populacja mieszkańców i mapowanie znaczeń nadal otwarte. Brak odsyłacza nie dowodzi nieprzynależności do klasy. Pełna macierz kwalifikacji, G7/G8/G9 i obowiązkowa bramka phase10 pozostają do wykonania. Nie deklarujemy delty finalnych list.

## Kontrole
Cztery regresje red→green: całe paradygmaty i homonimy; błędne przypięcia; explain/próbka; spójna podmiana payloadu. Explain tekstowy pokazuje pełne powody warstw udokumentowanego użycia.

[Rzeczywisty runtime](resident-use-runtime.json): dwie niezależne nowe projekcje wszystkich pasujących homonimów, 22 kompaktowe rekordy, 28 rozwinięć źródła, 14 użyć i 14 pozostałości, 42 analizy/84 oceny. Powtórny zapis: zero nowych analiz; logiczna treść i próbki identyczne; FK/integrity OK. 40 odczytów explain bez zmian baz; oryginalna baza G2 niezmieniona. Każdy z10 kluczy słów pozostaje unresolved przez nierozpoznane możliwości.

Odtwarzanie: PYTHONPATH=. python3 .maister/tasks/development/2026-10-04-generator-broad-standard/analysis/evidence/resident-use-runtime-probe.py --source-run data/work/import-20261004-1302 --output tmp/resident-use-runtime.json. Skrypt tworzy nowe projekcje; nie nadpisuje poprzednich.

Końcowo 201/201 testów generatora +5/5 audytu, bez ostrzeżeń; preflight14 źródeł/12 konfiguracji OK, git diff --check OK. Naprawiono domknięcie SQLite w istniejącym teście raportu kwalifikatorów (ResourceWarning wcześniejszego biegu).
