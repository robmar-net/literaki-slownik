# Warstwy quality-v1 — wdrożenie i pomiary

## TL;DR
Build zapisuje próbki analiz, słów i powiązań z pełnymi danymi wybranych jednostek.
Wszystkie13 list KWJP:5066341 jednostek,270 wybranych; powtórzenie identyczne.
Historyczna projekcja219713 analiz:641 słów/1124 analizy, identyczne dwa dobory.
Próbki i przegląd pozostają UNREVIEWED; pełny odbiór G8 jest otwarty.

## Key Decisions
- Seed/encoding/limit30 quality-v1 bez zmian. Jednostka słowna zawiera wszystkie swoje analizy i oba warianty; jednostka korpusowa ma F raz oraz wszystkie strukturalne kandydatury.
- Warstwy: krótkie, pełne ID homonimów, historia, udokumentowane etykiety tematyczne, nazwa/pospolity kandydat, każda obecnie potwierdzona konstrukcja, źródłowe klasy POS, oba warianty filter_changed/unresolved; metody/statusy linków.
- Definicje tematów quality-words są własnym przeglądem dotychczasowych etykiet, służą wyłącznie doborowi próby. Nie są filtrami dopuszczalności ani dowodem wszystkich specjalistycznych znaczeń.
- Szablon review dołącza całą wybraną jednostkę, odrzuca brak/duplikat/obcą jednostkę. Ocena nadal pusta, hash próbki wiążący.

## Open Questions / Risks
- Przynależność do próby nie jest rozstrzygnięciem znaczenia ani kontrolą jego poprawności.
- Brak źródłowej klasy w historycznej projekcji oraz pusty konstruktor mają EMPTY_NOT_COVERAGE. Pełna macierz i rzeczywisty przegląd wszystkich wybranych jednostek nadal wymagane.
- G6.3 pozostaje częściowe do pełnego pokrycia macierzy; główne checkboxy8/36 bez zmian.

## Pomiary

[Linki](quality-links-runtime.json): pełna historyczna populacja13list/2940032krawędzie,16warstw (także zera),270jednostek. Pierwszy poprawiony dobór 33.098s; dwa identyczne wyniki, hash DB bez zmian i total_changes0.

[Słowa](quality-words-runtime.json): wszystkie zapisane analizy historycznej projekcji219713/213636kluczy. Dobór 18.054s;641słów/1124analizy, powtórzenie identyczne, baza niezmieniona. Brak kompletu nowej polityki w tej historycznej bazie jest jawny.

Pierwszy pomiar linków przerwano SIGINT po wykryciu planu SCAN l/SCAN c LEFT-JOIN, powtarzającego skan milionów krawędzi. Poprawa: dwa uporządkowane strumienie liczebności i UNION ALL korzystający z istniejących indeksów częściowych. Znaczenie kontroli zachowane; regresja1000jednostek ma budżet2mln instrukcji SQLite, bez kruchego limitu czasu. Obsługa starszej bazy bez candidate_key sprawdzona na pełnych danych. Nie zmieniono indeksów/schematu ani historycznych baz.

Test-first:3testy linków,2testy słów,regresja kosztu i pełne dane review. Integracja build sprawdzona na przypiętych konfiguracjach. Duże próbki z surowymi jednostkami pozostają poza Git; publiczne podsumowania wiążą je SHA.
