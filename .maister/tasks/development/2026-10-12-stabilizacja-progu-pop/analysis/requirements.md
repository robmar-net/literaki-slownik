# Wymagania: STANDARD #4 i tymczasowy POP #6

## TL;DR

Zatwierdzone 2382 formy mają wejść do STANDARD przez wersjonowaną, edytowalną konfigurację dokładnych analiz.
POP ma używać stałej punktacji dzisiejszego cięcia oraz punktacji własnej członków grup; POP0 zachowuje dotychczasową metodę.
Nowe przebiegi i listy muszą być odtwarzalne, kontrolowane pełnym diffem i opisane w dokumentacji oraz wiki.
Docelowa granica POP, osiem cofnięć, wydanie i integracja z grą pozostają oddzielne.

## Key Decisions

- Zakres zatwierdził właściciel 2026-10-12: 2382 dodatki zgodne z badawczymi JSON-ami, trwały pipeline, dokumentacja wiki, tymczasowa stabilizacja POP.
- Edytowalność oznacza zmianę jawnego JSON-a i nowy build z pinem hasha; nie poprawkę gotowej listy lub starej bazy.
- Własny dowód współczesnego znaczenia podważa wyłącznie historyczną odmowę wskazanej analizy; pozostałe warunki nadal obowiązują.

## Open Questions / Risks

- Rzeczywiste wyniki mogą odbiegać od symulacji, jeżeli build użyje innych bajtów wejściowych lub zmienionej polityki. Każdą rozbieżność trzeba wyjaśnić przed uznaniem wyniku.
- Pełne dwa buildy są kosztowne. Samo przejście testów jednostkowych nie wystarczy do stwierdzenia, że 2382 formy weszły do nowego STANDARD.

## Wymagania funkcjonalne

1. Konfiguracja produkcyjna wskazuje dokładnie 2382 formy i 7192 udokumentowanych analiz `(forma, leksem, rozwinięty tag, rodzaj źródła lub konstrukcji)`. Każdy wpis ma odniesienie do ocenionej rodziny i badawczego dowodu. Wstrzymane formy i osiem cofnięć są wyłączone.
2. Manifest `sources.json` przypina SHA256 tej konfiguracji. Build odmawia brakującego pliku, niezgodnego hasha, błędnego schematu, duplikatu, niedopasowanej lub nadmiarowej analizy. W przebiegu zostają metryki wykorzystania konfiguracji.
3. Tylko w STANDARD i tylko dla wskazanej analizy reguła o współczesnym użyciu zastępuje odmowę dawności. Inne odmowy językowe, warunki gry, profil i zakres wydania nie są omijane. BROAD i historyczne wejścia nie zmieniają znaczenia.
4. `explain` i zapisane oceny wskazują zastosowany wyjątek, dowód oraz wersję polityki. Niezależne homonimy i nieobjęte formy zachowują dotychczasowe powody.
5. Konfiguracja POP ma nową wersję metody. POP wybiera grupy z wynikiem `≥ −1,042878629` i przycina członków według ich własnego wyniku z zachowaniem dwóch dotychczasowych wyjątków. Remisy na progu wchodzą razem. POP0 nadal stosuje limit 20 000 i własną rangę.
6. Raport progu i `explain pop` pokazują właściwy rodzaj granicy. Generator odmawia naruszenia `POP0 ⊆ POP ⊆ STANDARD`, straży częstych form, pinów lub niezgodności danych.
7. Na przypiętej bazie bez dodatków nowy POP ma dokładnie ten sam zbiór 1 227 250 form co `pop-v2`; po dodatkach oczekiwane są STANDARD 3 092 576 form, POP +2372/0 i POP0 +481 w zbadanym scenariuszu. Wyniki są warunkami porównania, nie gwarancją dla innych źródeł.
8. Dokumentacja w repo i wiki opisują nowy wyjątek STANDARD, tymczasowy próg POP, status starego wydania i otwartą potrzebę powrotu do merytorycznej granicy. Wiki nie pokazuje nowych liczb jako wydanych przed wydaniem.

## Weryfikacja i odbiór

- Testy konfiguracji i dokładnego dopasowania analiz, w tym wstrzymania, homonimów, konstrukcji i innych odmów.
- Testy progu na remisach, brakach punktacji, członkach grup, POP0 oraz raportach i diagnostyce.
- Dwa nowe buildy z identycznych pinów, niezależny verify/export, zgodne hashe list, pełny diff wobec bazowych wydań, kontrola 2382/7192 oraz dodatnich i ujemnych przykładów z `validation.json`.
- Przegląd próbek jakości i straż częstych form; każdy inny ubytek niż osobno oczekiwany wymaga analizy.

## Poza zakresem

- Osiem cofnięć z oddzielnego audytu; nowe źródła lub progi automatycznej frekwencji; kalibracja docelowej granicy POP; zmiana POP0; wdrożenie list do serwera gry; automatyczne wydanie GitHub Release.
