# Wspólny dowód leksykalny — wdrożenie A

## TL;DR
A wdrożone jako diagnostic-approved-conditions-v21 / approved-conditions-v18. Ten sam dokładnie udokumentowany dowód użycia przechodzi warunek leksykalny BROAD i STANDARD. Pozostałe warunki i nierozpoznane znaczenia zachowane; pełne wydanie nadal otwarte.

## Key Decisions
- Wiek, niepoprawność, norma 2026, gra, profil i zakres są nadal odrębnymi warunkami. Kroćset zachowuje reject STANDARD za dawność mimo dodatniego dowodu leksykalnego.
- Rejestr sześciu dokładnych użyć i strażniki źródła/dokumentu bez rozszerzenia. Pozostałość nie przejmuje dowodu użycia.
- Czytnik ocenia zapisany warunek według wersji utrwalonej analizy: v16–v20 zachowują wcześniejszy próg BROAD-only, v21 wymaga wspólnego dowodu. Starsza baza nie jest przeliczana lub modyfikowana. Zmiana danych nadal wymaga nowego build.

## Open Questions / Risks
G3/G4/G6 nadal częściowe, 8/36 głównych kroków. Brakujące warunki i pełna macierz nie zostały zamknięte; nie powstały finalne listy. Następny próg dotyczy roli ręcznie sprawdzonych opisów/przykładów oficjalnego czytnika, bez importu jego metadanych.

## Dowody i kontrole
Test-first: zmienione dwa wcześniejsze testy wariantów i nowy test kroćset/nieznanego wariantu — red 3 błędy → green 6/6. Historyczny odczyt: red GeneratorError dla v20 → green; ten sam historyczny payload podszywający się pod v21 nadal odrzucany. Cały generator 210/210, audyt 5/5, bez ostrzeżeń.

[Runtime](shared-lexical-proof-runtime.json), [odtwarzanie](shared-lexical-proof-runtime-probe.py): dwie nowe niezależne projekcje całej populacji homonimów sześciu użyć, 10 kompaktowych rekordów / 10 rozwinięć, 6 użyć + 6 pozostałości, 16 analiz / 32 decyzje. Identyczna logiczna treść i próbki, ponowienie 0 nowych analiz, FK/integrity OK; 24 explain readonly, źródło bez zmian. Członkostwo nie zmienia się: pięć kluczy unresolved, kroćset reject STANDARD. To nie jest pełny build ani pomiar przyszłej delty list.

Dwa rzeczywiste starsze przebiegi v19/v20 odczytane readonly i z niezmienionym SHA bazy, nadal lexical STANDARD unresolved. Próg v21 nie jest narzucany historycznej bazie. Konfiguracje i źródła przechodzą preflight; techniczna zmiana wersji nie aktywuje niepełnej polityki.
