# Adnotacja akcent — wymóg objaśnienia w pierwszym wydaniu

## TL;DR
Zatwierdzone A: dwa kompaktowe źródłowe rekordy z daw.,rzad.,akcent: dwomakroć / dwakroć:N i trzemakroć / trzykroć:N. Dawność jest rozstrzygnięta; dokładna treść adnotacji akcent nadal nie została ustalona. Poprzedni wyjątek25dosłownych etykiet nie obejmował tej etykiety.

## Key Decisions
- Użytkownik zatwierdził A; wdrożono zamknięty wyjątek dla daw.,rzad.,akcent. STANDARD odrzuca te konkretne analizy za dawność niezależnie od dalszej decyzji.
- A: zachować adnotację z nieustalonym objaśnieniem; jego brak sam nie wyklucza w BROAD, wszystkie inne kryteria obowiązują. Jawne rozszerzenie wyjątku wymagania, nie zgadywanie znaczenia.
- B: przed pełnym wydaniem BROAD ustalić objaśnienie, unresolved pozostaje do zdobycia dowodu.

## Open Questions / Risks
- Objaśnienie nadal nieustalone; zatwierdzenie nie zastępuje jego ustalenia. Źródłowe oznaczenie nie może zostać po cichu zamienione na akcentowaną formę albo wymaganie kontekstu.
- Reguły gry, inne unknown i pozostałe K1–K10 nie są przez A domknięte.

## Dowody

Readonly G2: dwomakroć, lemat dwakroć:N; trzemakroć, lemat trzykroć:N; oba tag num:pl:inst:m1.m2.m3.f.n:congr, puste pole nazw i dokładne kwalifikatory daw.,rzad.,akcent. Źródłowe pola zachowane. Aktualne metadane interfejsu SGJP mają kwalifikator formy akcent (ID3927), ale nie objaśniają jego skutku. Dokumentacja SGJP o wymowie/akcentowaniu nie dowodzi, że ta konkretna adnotacja ma wyłącznie efekt opisowy.

Sprawdzono pinned tmp/lane-qualifiers/leksemy.html (metryka w config/generator/evidence.json), całą tabelę [oznaczeń SGJP](https://sgjp.pl/oznaczenia/), [instrukcję](https://sgjp.pl/instrukcja/) i [Podstawy SGJP](https://sgjp.pl/static/pdf/Podstawy_teoretyczne_SGJP.pdf). Wyszukiwania dokładnych form nie przyniosły źródłowego objaśnienia akcent; wyników SJP nie użyto jako danych ani dowodu dopuszczalności. Nie dodano nowego artefaktu leksykalnego.

## Wdrożenie zatwierdzonego A

Reguła `linguistic-accent-gloss-first-release-v1` zachowuje dokładną adnotację i `gloss_status=unestablished`. [Pełny runtime](accent-game-runtime.json) potwierdza językowe unresolved w BROAD i reject za dawność w STANDARD, bez zmiany źródła. Inne kryteria pozostają obowiązkowe.
