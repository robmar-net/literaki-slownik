# Domknięcia mechaniki i pozostałe luki semantyczne

## TL;DR
Sprawdzono wszystkie 70 zamkniętych definicji hostów w przypiętym segmenty.dat i wykonano konstruktor dla każdego ich źródłowego zakresu. Rejestry nie mają braków ani dodatków. Potwierdzono odrębne, niezmienione przyczyny odrzucenia 295 mieszanych nazw oraz dwóch rekordów ń. Pełna kwalifikacja znaczeń i ortografii nadal otwarta.

## Key Decisions
- Domknięta jest macierz źródłowych hostów czterech klas; nie pełna kwalifikacja wszystkich kandydatów. Nie zmieniono żadnej reguły generowania ani gry.
- 70 definicji obejmuje 17 z_aglt_by (by obsługiwane osobną klasą, pozostałe 16), 53 pozostałe hosty oraz 47 hostów sekwencji by. Porównanie zbiorów z kodem jest dokładne; zero brakujących/nadmiarowych definicji. Źródłowe powtórzenie czyż zachowuje obie lokalizacje, nie mnoży definicji.
- Każda definicja ma rzeczywiste źródłowe rekordy i co najmniej jednego kandydata. Sprawdzono wspólne źródło składników, dziedziczenie wszystkich etykiet, warianty i adnotacje odmienionego hosta. Nie włączono permissive ani dopasowania przez sufiks.

## Open Questions / Risks
Pełne 34 klasy źródłowe, semantyka kwalifikacji i norma wymagają dalszego domknięcia. Publiczny czytnik ma dokładniejsze opisy, ale jego metadane nie są zatwierdzonym wejściem maszynowym. Brak odsyłacza nie dowodzi braku znaczenia mieszkańca; brak kwalifikatora nie dowodzi współczesności. Nie oznaczono G3 lub G4 jako complete.

## Dowód braku wpływu dwóch szczególnych niewiadomych
295 kompaktowych interpretacji mieszających nazwę pospolitą i własną ma niezależny game-required-uppercase-v1=reject. Niewiadoma klasy pozostaje zachowana; jej usunięcie lub rozstrzygnięcie nie zmieni końcowej oceny tych analiz. Nie jest to odrzucenie innych homonimów całego słowa.

Jedyny niepowiązany dosłowny kwalifikator pisane_łącznie_z_przyimkiem dotyczy dwóch rekordów ń/on:S, wiersze 4212679 i 4212680: razem sześć rozwinięć. Oba mają game-dependent-segment-v1 i profile-pl-length-v1=reject. Długość jednego znaku wyklucza sam napis niezależnie od innych interpretacji. Nie udajemy objaśnienia kwalifikatora; brak pełnej glosy sam nie zmienia listy w tym zakresie. Potwierdzone całe kontrakcje nadal oceniane odrębnie.

## Zakres frag
147 kompaktowych rekordów: 41 ma niezależną odmowę istniejących warunków w BROAD, 62 w STANDARD; odpowiednio 106 i 85 nie ma takiej odmowy. To projekcja źródłowych warunków bez przypisywania własnych dokumentacyjnych użyć do całego ID; nie liczba słów do dopuszczenia ani kompletna ocena pozostałości. Nie przejmujemy odmowy lub akceptacji jednego użycia przez inne znaczenia.

## Odtwarzanie
[Runtime](remaining-matrix-runtime.json), [skrypt](remaining-matrix-probe.py) czytają wyłącznie pełny G2 i przypięty segmenty.dat SHA 73fca7c4cd5a1cd0db5cd6367b098ec96a6fb01481a0eb441f3b24aa9ca4521c. Dwa raporty identyczne, SHA bazy przed/po niezmienny, total_changes=0. Wynik nie zastępuje pełnych dwóch build K8 ani językowego odbioru G8.
