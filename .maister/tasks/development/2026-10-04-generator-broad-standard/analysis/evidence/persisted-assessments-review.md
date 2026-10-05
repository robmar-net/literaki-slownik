# Utrwalone analizy i pełne powody ocen

## TL;DR
Nowe build utrwalają każde rozwinięcie źródłowego tagu oraz każdą konstrukcję, z dwiema osobnymi ocenami wariantów. Jest to diagnostyka, nie pełna kwalifikacja ani wydanie. Generator147/147 i audyt5/5 przeszły.

## Key Decisions
- Schema2 dodaje analysis, variant_decision i decision_payload. Każda analiza wskazuje przez FK dokładną interpretację albo konstrukcję; surowe rekordy i homonimy zostają.
- Powody ocen przechowujemy jako wspólne kanoniczne dokumenty JSON identyfikowane SHA256. Profil oryginalnej formy pozostaje przy analizie. Współdzielenie identycznych dokumentów nie łączy sensów ani statusów między homonimami.
- Build zapisuje reports/decisions.json. Explain JSON udostępnia persisted_analyses, odróżniając zapisany wynik z wersją od bieżącej diagnostyki. Stare bazy pozostają czytelne, bez migracji.
- Odmienna wersja lub wynik istniejącej oceny wymaga nowego build. Sprawdzenie hashy powodów działa również podczas odczytu. Logical-content obejmuje nowe relacje z kluczami treści zamiast technicznych ID.
- Status decisions pozostaje pending: pełna macierz językowa/growa jeszcze nieaktywna. Każdy znany warunek i pozostałe nierozstrzygnięcia są zachowane; nie zamieniamy unresolved na accept.

## Dowody
[Runtime](persisted-assessment-runtime.json): wszystkie615 interpretacji wejściowych bieżących konstruktorów poza impt,850 rozwinięć źródłowych i776 konstrukcji; razem1626 analiz i3252 oceny.72 różne dokumenty powodów, pełne przykłady jam/bym/doń. Ponowienie:0 nowych analiz/ocen i identyczny logical-content. FK/integrity OK; baza źródłowa tylko do odczytu.67,724s obejmuje także wybór projekcji i konstrukcje, nie jest pomiarem czasu pełnego build.

Test-first: brak materialize_assessments → implementacja; brak ocen w build → integracja; brak persisted_analyses → explain; wspólne powody/profile i odmowa uszkodzonego dokumentu → naprawa. Testy kontrolują osobne rozwinięcia, przeciwne homonimy, idempotencję, zmianę polityki, checksum i stabilność logical-content po zmianie ID.147/147 całej suity oraz5/5 historycznego audytu przeszły.

## Open Questions / Risks
Pełne G3–G9, dwa pełne build, verify/export i canonical maister-verify nieukończone;8/36 checkboxów bez zmian. Koszt zapisu17mln rozwinięć źródłowych wymaga pomiaru G8. Projekcja nie zastępuje pełnego odbioru. Dalsza [decyzja o odniesieniu normy growej](game-capitalization-norm-decision.md) wymaga odpowiedzi przed nowym filtrem.
