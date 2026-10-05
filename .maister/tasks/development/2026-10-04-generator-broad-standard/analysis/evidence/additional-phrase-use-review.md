# Dalsze jawnie udokumentowane użycia SGJP

## TL;DR
Wdrożono ten sam zatwierdzony próg dodatniego dowodu leksykalnego BROAD dla pięciu kolejnych dokładnych użyć. Pełna kwalifikacja, STANDARD i pozostałość zachowane jako odrębne oceny. Runtime v19, konfiguracja v16; pełna macierz nadal otwarta.

## Key Decisions
- Dwójnasób, trójnasób, kroćset, roścież i ziem: wyłącznie dokładne przykłady autorów, nie automatyczne rozszerzenie klasy ani korzystanie z WSJP.
- Ponownie przeczytano całe właściwe fragmenty [SGJP](https://sgjp.pl/static/pdf/Podstawy_teoretyczne_SGJP.pdf): §1.4 s.19 (roścież/ziem), §7.7.2 s.134 (dwójnasób/trójnasób), §7.12 s.137–138 (kroćset). SHA przypiętego PDF:3e3d104b1a210e0097c511b36f1440de539413ec64079fba505c47c3bf7684ca; SHA eksportu:3b2ee079143bc95186370fd528735779c4ba62f4ce14e30cf6622ceb566e9810. Własne mapowanie pięciu pól i wierszy z wcześniejszej adnotacji PAN potwierdzone w bazie G2.
- Nie dodano wykluczenia wieku z opisu całej klasy dwójnasób/trójnasób: wcześniejsze A nadal wiąże. Kroćset ma jawne daw. i nadal odpada ze STANDARD, także w pozostałości.
- Dowód leksykalny nie przechodzi na pozostałość ani rzeczownikowe homonimy ziemia/Ziemia. Warunek BROAD accept nie oznacza akceptacji całej analizy.

## Open Questions / Risks
Pełne mapowanie wszystkich frag, ortografii i warunków growych pozostaje otwarte. Źródłowy opis przestarzałej klasy nie zastępuje rozstrzygnięcia konkretnego znaczenia; źródła społecznościowe, WSJP i benchmark nadal nie są wejściami.

## Kontrole
Trzy nowe regresje: pięć dokładnych użyć z pozostałością; zły dokument/useID odmawia przed zapisem; usunięcie dodatniego powodu ze spójnego payloadu z przeliczonym hashem odmawia odczytu. Zamknięty rejestr zawiera sześć przypadków wraz z wcześniejszym wznak. Końcowo204/204 testów generatora +5/5 audytu bez ostrzeżeń, preflight14źródeł/12konfiguracji OK.

Test-first red: dwa nieudokumentowane mapowania; test negatywny dokumentu już poprawnie odmawiał. Po wdrożeniu poprawiono oczekiwanie fikstury kroćset STANDARD (już istniejący reject) oraz kolejność zamykania SQLite/przed usunięciem katalogu testowego. Green16focused i cała suita204. Ochronę czytnika rozszerzono także na istniejący wznak.

[Runtime](additional-phrase-runtime.json): dwie nowe niezależne projekcje pełnego źródła ze wszystkimi homonimami wskazanych kluczy:9rekordów/9rozwinięć/14analiz/28ocen;5użyć/5pozostałości. Powtórny zapis0nowych analiz, logiczna treść/próbki zgodne, FK/integrityOK,20readonly explain bez zmian baz, źródłowa baza niezmieniona. To nie pełne build G8 ani finalna delta list.

Odtwarzanie: PYTHONPATH=. python3 .maister/tasks/development/2026-10-04-generator-broad-standard/analysis/evidence/additional-phrase-runtime-probe.py --source-run data/work/import-20261004-1302 --output tmp/additional-phrase-runtime.json. Powstają nowe katalogi, wcześniejsze projekcje pozostają.
