# Wdrożenie zatwierdzonego progu wieku STANDARD

## TL;DR
A wdrożone jako diagnostic-approved-conditions-v20, konfiguracja v17. Brak wykluczającego oznaczenia przechodzi tylko warunek wieku z age_basis=source_classification i age_certainty=not_independently_established. Nie jest dowodem współczesności ani pełną kwalifikacją.

## Key Decisions
- Jawne daw./przest./arch. i mieszane wyłączenia nadal odrzucają STANDARD; BROAD bez nowego warunku wieku.
- Warunek wieku nie objaśnia nieznanego kwalifikatora. Nie dodano go do approved_qualifier_checks; pokrycie nie ukrywa pozostałych luk.
- Reguły gry, niepoprawność, pisownia, próg leksykalny i pozostałość znaczeń nadal odrębne.

## Kontrole
Test-first: trzy nowe testy wieku, red ImportError → green. Zaktualizowano test współdzielenia payloadów: BROAD i STANDARD mają teraz dwa różne payloady zamiast jednego; każdy nadal jest współdzielony między słowami. Raport niewiadomych otrzymał osobny test red KeyError → green. Końcowo 208/208 generatora, 5/5 audytu, diff check i preflight 14 źródeł / 12 konfiguracji OK.

[Runtime](age-baseline-runtime.json), [skrypt](age-baseline-runtime-probe.py): dwie niezależne projekcje wszystkich homonimów sześciu udokumentowanych użyć, 10 kompaktowych rekordów i rozwinięć, 6 użyć + 6 pozostałości, 16 analiz / 32 decyzje. Treść logiczna i próbki identyczne, ponowienie 0 nowych analiz, FK/integrity OK. 24 explain readonly i źródło bez zmian. Nie jest to pełny przebieg v20.

## Open Questions / Risks
G3/G4/G6 pozostają częściowe, 8/36 głównych kroków. Ogólne niewiadome polityki i metadanych gry pozostają aktywne; nie można ogłosić pełnego wydania. Wcześniejszy dowód leksykalny był zatwierdzony tylko dla BROAD; rozszerzenie na STANDARD wymaga decyzji.
