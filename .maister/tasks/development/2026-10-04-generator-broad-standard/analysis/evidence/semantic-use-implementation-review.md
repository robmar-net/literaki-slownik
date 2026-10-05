# Udokumentowane użycia — wdrożenie i kontrola

## TL;DR
Zatwierdzone A wdrożono jako własne adnotacje dokładnego rekordu, osobne spójne oceny użyć i niewiadomą pozostałość.
Nowe build v15 czytają przypięty przegląd, a explain/raporty/próbka zachowują oba warianty i źródło.
Dwa niezależne przebiegi projekcji147 kluczy frag z homonimami są logicznie identyczne; źródłowa baza bez zmian.
Pełna polityka, macierz i wydanie pozostają nieukończone.

## Key Decisions
- Źródłowe dane i schemat2 bez migracji. Własny przegląd jest osobnym source_artifact, ze stabilnym SHA256; ślad użycia należy do hashowanego payloadu i klucza analizy. Zmiana/pominięcie przeglądu wymaga nowego build.
- use_id, source_id, SHA eksportu, pierwsza źródłowa lokalizacja, pełny ID i pięć pól są obowiązkowe. Walidacja poprzedza zapisy. Dowody mają własną rolę own_documentary_review, hash i lokalizator; BLOCKED, nieznana rola, duplikaty i inne pola/snapshot odmawiają zapisu.
- Format1 ma documented_use_only: nie pozwala zadeklarować pełnej kwalifikacji bez dowodu. Obsługa kompletności poszczególnych warunków nadal wymaga domkniętej macierzy G3. Nie ma pola wstrzykującego arbitralne accept/reject. Cała ocena użycia zachowuje język/gra/profil/zakres.
- Warunki dokumentacyjne są przypinane do konkretnego użycia; validator wymaga zamkniętego ID istniejącej reguły, dokładnego źródłowego przypadku i właściwego dokumentu. Dowód użycia nie propaguje warunku na nierozpoznane możliwości. Fizyczny zapis/profil i pozostałe warunki źródłowe nadal obowiązują.
- Pierwsze2 adnotacje to wcześniej zatwierdzone de:F/frag i ibn/frag; bez importu glos/metadanych czytnika. Inne własne obserwacje nadal nie są aktywnymi wejściami kwalifikacji. Również don nie otrzymał domniemanych znaczeń.

## Open Questions / Risks
- Brak kompletnych ocen pozytywnych językowych/growych oraz mapowania pozostałych użyć; następny wybór dotyczy dodatniego dowodu językowego, nie modelu reprezentacji.
- quality-analyses obejmuje rodzaje utrwalonych analiz i statusy wariantów; nie zastępuje wszystkich wymaganych warstw słownych/linków quality-v1. Próbka UNREVIEWED, full_quality_matrix_pending.
- Jawna pozostałość może mieć odmowę niezależną od znaczenia, np. przez alfabet lub fizyczny zapis wielką literą. Brak poznanych znaczeń sam nie jest odmową. Unknown w którejkolwiek warstwie pozostaje widoczny także pod znanym reject.
- G3/G4/G6 częściowe, G7–G9 i obowiązkowy wybór weryfikacji w fazie10 nadal przed nami;8/36 głównych kroków, bez deklaracji wydania.

## Interfejs i jednostki

Konfiguracja semantic-uses w sources.json ma zwykły przypięty path/sha256; build czyta ją dopiero po preflight. Własna konfiguracja config/generator/semantic-uses.json zawiera dwie dokładne adnotacje. `materialize_assessments(db, use_reviews=...)` waliduje całość, utrwala przegląd i odmawia jego zmiany w istniejącym zapisie. Rekordów źródłowych nie zastępuje rekordami użyć.

Report decisions podaje source_rows, source_compact_interpretations, source_tag_expansions, documented_use_analyses, remainder_analyses i całkowite source_analyses. Pozostałość zajmuje miejsce źródłowego rozwinięcia; analiza każdego udokumentowanego użycia jest dodatkowa. Liczba rozwinięć tagów nie jest liczbą znaczeń.

Explain pokazuje semantic_analyses i ich dowody; źródłowy rekord jest oceniany bez nieudowodnionego przenoszenia warunków użycia, a source_aggregation ma jawny basis persisted_source_expansions_and_use_alternatives. Odczyt utrwalonych ocen i raporty odmawiają braku pozostałości, niewłaściwego klucza/śladu/wersji źródła i błędnego metadokumentu także przy poprawnie przeliczonym hashu sfałszowanego JSON. Starsze bazy bez przeglądu pozostają czytelne.

Raporty unknown/filter podają semantic_analysis_kinds, osobno konstrukcje, zwykłe rozwinięcia, użycia i pozostałości. Nowe build z przypiętym quality tworzy reports/quality-analyses.json: do30 jednostek na diagnostyczną warstwę, źródło i komplet warstw obu wariantów. Próbka nie jest automatycznym odbiorem.

## Rzeczywisty przebieg

[Runtime](semantic-use-runtime.json) obejmuje wszystkie147 zaplanowanych kluczy frag i zachowane źródłowe homonimy:295 kompaktowych interpretacji /295 reprezentatywnych surowych rekordów projekcji,540 rozwinięć tagów,2 dodatkowe analizy użyć,2 pozostałości w miejsce istniejących rozwinięć,542 analizy i1084 oceny wariantów. To projekcja, nie pełny build7,46mln rekordów ani pełna populacja znaczeń.

Wykonano baseline bez adnotacji oraz dwa niezależne nowe zapisy z tymi samymi adnotacjami. Powtórzenie każdej materializacji0 nowych analiz/ocen, FK/integrity OK. Dwa zapisy mają identyczne logical-content i próbki; hash oryginalnej bazy bez zmian. Osiem readonly explain pokazuje użycie i pozostałość.

W pierwszym roboczym przebiegu pozostałość błędnie odziedziczyła dawną rekordową odmowę nazwiska. Test-first wykazał ten brak rozdzielenia; poprawiono zgodnie z A. Końcowy ibn ma odmowę udokumentowanego użycia i nierozstrzygniętą pozostałość: diagnostyczne słowo zmienia reject→unresolved w obu wariantach. De pozostaje unresolved przez zachowane niezależne homonimy. Nie jest to dopuszczenie ibn do listy ani zmiana reguły gry. Poprzednich baz nie zmieniono; robocze przebiegi zachowane.

## Kontrole

7 nowych testów: początkowe3 TypeError→green; wejście build brak adnotacji0→1 red→green; próbka ImportError→green; zakres dokumentacyjny TypeError→green; brak pozostałości/obcy ślad przy poprawnym hashu nie odmawiał red→green. Dwa błędy porządku sprzątania fikstury SQLite skorygowano przez commit danych testowych przed usunięciem folderu. Brakujący import load_json poprawiono przed green. Dodatkowe kontrole jakości w istniejącym teście build i niedopuszczonych warunków green, bez dopisywania fikcyjnego red.

Całość179/179 generator +5/5 audytu. Preflight14 źródeł i11 konfiguracji OK. Kontrole są weryfikacją przyrostu G4/G6, nie kanoniczną fazą11 Maister ani zamknięciem pozostałych kroków.

Diagnostyczna próbka rzeczywista: 140 unikalnych jednostek;2 użycia i2 pozostałości, powtarzalna, nadal UNREVIEWED.
