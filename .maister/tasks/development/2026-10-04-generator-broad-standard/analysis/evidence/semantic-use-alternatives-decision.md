# Kilka udokumentowanych użyć jednego rekordu źródłowego

## TL;DR
Pełny przegląd147 przypadków frag ujawnił konkretną niejednoznaczność mapowania: don ma dwa publiczne artykuły, a w przypiętym eksporcie jeden rekord. Proponujemy własną, dowodową warstwę alternatywnych użyć powiązaną z niezmienionym rekordem. To wymaga decyzji przed zmianą modelu kwalifikacji; nie jest nową regułą gry.

## Key Decisions
- Proponowane A: jedno źródłowe pięciopolowe rozpoznanie może mieć kilka osobno udokumentowanych użyć. Każde oceniane spójnie językowo/growo/profilowo; nie łączymy warunku językowego jednego użycia z klasyfikacją grową innego.
- B: utrzymujemy jeden wynik dla całego źródłowego rekordu; niejednoznaczne mapowania pozostają unresolved do znalezienia bogatszego, zgodnego i dopuszczonego źródła. Nie oznaczamy ich jako błędnych i nie omijamy blokady wydania.
- Nie tworzymy nowych słów ani źródłowych leksemów. Zachowujemy source_id, hash eksportu, pełny ID, wiersze, pięć pól, wszystkie homonimy i wcześniejsze oceny.
- Sam dostęp do publicznego czytnika nie aktywuje internetowej bazy metadanych. Przegląd referencyjny pozostaje osobnym artefaktem własnych obserwacji; aktualny zbiór148 artykułów nie jest wejściem polityki ani słownikiem znaczeń.

## Open Questions / Risks
- Pending: czy zatwierdzić A i zmienić model ocen przed dalszą kwalifikacją?
- Opis użycia nie dowodzi kompletnej semantyki. Dla nieprzejrzanych możliwości pozostaje jawna nierozstrzygnięta alternatywa; nie odrzucamy ich przez brak dowodu.
- Nadal otwarte: dokładna zgodność internetowych opisów ze snapshotem, nazwy mieszkańców, granica pożyczki/cytatu i pełna macierz normy2026. Ta decyzja nie rozstrzyga tych luk ani dopuszczalności don/sir/session.

## Konkretny przypadek

Przypięty rekord don/frag, bez nazwy i kwalifikatora, wiersz1554730, odpowiada kandydatom z dwóch publicznych artykułów:

- [don, artykuł91612](https://sgjp.pl/leksemy/#91612/don): użycie wykrzyknikowe w din don;
- [don, artykuł1003284](https://sgjp.pl/leksemy/#1003284/don): przedimek przed imieniem, np. don Juan.

Nie przyjmujemy, że przedimek sam stanowi nazwę własną, ani że wyrażenie jest obcym cytatem wyłącznie przez pochodzenie. To dwie odrębne obserwacje wymagające własnej kwalifikacji. Jednoznaczne mapowanie pisownia+frag nie wybiera między nimi.

Dodatkowo opisy na koń i wyjść za mąż znajdują się przy artykułach rzeczownikowych. Zachowujemy rozróżnienie koń:F i mąż:F względem rzeczownikowych homonimów — internetowe ID artykułu nadrzędnego nie zastępuje źródłowego ID fragmentu. [Pełny audyt](sgjp-full-frag-reader-coverage.json).

[Dokumentacja SGJP §2.1, s.21](https://sgjp.pl/static/pdf/Podstawy_teoretyczne_SGJP.pdf#page=21) już potwierdza, że tożsamość leksemu nie jest identyfikatorem pojedynczego znaczenia. Wybór sposobu reprezentacji tego faktu w generatorze pozostaje naszym zadaniem.

## Projekt A do wdrożenia po zatwierdzeniu

1. Własna adnotacja ma stabilny use_id, dokładną tożsamość źródłowego rekordu, hash eksportu i dowód konkretnego użycia. Numer internetowy jest odsyłaczem, nie kluczem źródłowym.
2. Dowód ma zakres documented_use_only. Osobno zapisujemy coverage: czy rozpoznano tylko użycia, czy udowodniono kompletność klasy istotnej dla danego warunku. Brak dowodu kompletności nie staje się domyślnym complete.
3. Przed kwalifikacją walidujemy mapowanie, pochodzenie/warunki dowodu, spójność i konflikty. Odrzucamy nieprzypiętą adnotację, duplikat use_id, inne pola, inny snapshot i próbę importu BLOCKED.
4. Oceny użyć zachowują ślad do tej samej surowej interpretacji. Każda ma pełny komplet warstw i osobne przyczyny. Użycie może dostarczyć dodatniej analizy tylko po spełnieniu wszystkich wymaganych kryteriów; internetowa etykieta nie jest takim wynikiem.
5. Jeśli nie pokryto wszystkich istotnych możliwości, zachowujemy dodatkową nierozstrzygniętą analizę. Dowód pojedynczego użycia nie wyłącza pozostałych. Agregacja słowa pozostaje istniejącą zasadą: accept, jeśli istnieje spójna zaakceptowana analiza; w przeciwnym razie unresolved, jeśli pozostała niewiadoma; reject tylko przy samych odmowach.
6. Explain, raporty niewiadomych/filtrów i próbka pokazują zarówno źródłowy rekord, jak i użycia. Liczba rekordów źródłowych, rozwinięć tagów i analiz użyć jest rozliczana osobno. Nowa wersja polityki i nowy build, bez nadpisywania wcześniejszych baz.

## Wpływ i powód bramki

Bieżący przegląd zmienił0 reguł i0 ocen. Bezpośredni przypadek projektu to1 źródłowy rekord don i2 kandydackie opisy, nie nowa lista dopuszczonych słów. Finalnej delty nie da się uczciwie obliczyć przed dokładnym mapowaniem i kwalifikacją.

[AGENTS.md](../../../../../AGENTS.md) wymaga omówienia decyzji zmieniających kryteria lub skład słownika. Executor Maister nakazuje: „Ask the user before changing scope” oraz zatrzymanie dla zmiany architektury poza zatwierdzonym planem. A zmienia jednostkę oceniania, więc nie wdrażamy tej części automatycznie. Rekomendujemy A: pozwala zachować różnice bez wymyślania znaczeń i bez zbiorczego odrzucania napisu.
