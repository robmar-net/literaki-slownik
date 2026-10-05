# Norma wielkiej litery i podwojona partykuła

## TL;DR
Zatwierdzone A wdrożono w normie growej, zachowując odrębność języka i gry. Podwojona partykuła otrzymała pełny ślad konstrukcyjny oraz growe odrzucenie. Rzeczywisty runtime i151 testów generatora oraz5 audytu przeszły. Pełne wydanie nadal nieukończone.

## Key Decisions
- game-mandatory-capital-2026-v1 odnosi się do normy2026 w BROAD i STANDARD. Zamknięty podzbiór obejmuje pełne ID warszawianin, warszawiak, krakowiak:Sm1 oraz subst:m1/depr:m2. Nie zgadujemy po sufiksie ani samym m1 i nie przepisywaliśmy form źródłowych.
- Warstwa językowa zachowuje udokumentowany małoliterowy zapis w BROAD i odrzuca go w STANDARD. Poprawny wielkoliterowy zapis nie ma odrzucenia językowego przez ten warunek; growy zakaz pozostaje osobno.
- krakowiak:Sm2 (taniec, m2/chor.) ma niezależne źródłowe analizy. Odrzucenie mieszkańca nie jest odrzuceniem całego klucza słowa.
- impt-double-particle-v1 ma wyłącznie źródłową regułę sg/sec + że + ż. Każde rozwinięcie perf/imperf zachowuje surową analizę, jej pełne ID i kwalifikatory oraz dwie oddzielne partykuły. Nie wywołujemy konstruktora rekursywnie i nie mnożymy dołączeń do zgadywanych hostów.
- Dowód językowy pochodzi z segmenty.dat334–340. game-double-particle-v1 odrzuca ten ślad zgodnie z zachowanym §5 reguł gry. Istniejące homonimy nadal oceniamy osobno. Wszystkie nowe build i explain obsługują tę samą klasę, z trwałymi FK i hashami.
- Wersja diagnostyczna policyv13, constructions-discovery-v6, orthography-discovery-v3. Rehash konfiguracji w sources.json; wcześniejsze runtime/DB nie zmienione. To nie pełna aktywacja G3/G4.

## Open Questions / Risks
- Trzy leksemy nie zamykają klasy nazw mieszkańców. Pełny eksport pięciopolowy nie opisuje znaczeń pozwalających wyznaczyć kompletną klasę po normie2026.
- Pełna inwentaryzacja frag:147 analiz,109 małoliterowych i38 z wielką literą. Sam tag nie dowodzi, które są niesamodzielnym członem obcego zwrotu; nie odrzucamy całej klasy przez kontekst.
- G3–G9 i pełne verify/export/G8 nieukończone,8/36 kroków bez zmian. Techniczna projekcja nie zastępuje dwóch pełnych build ani przeglądu jakościowego.
- [Przygotowane zapytanie do SGJP](sgjp-semantic-metadata-request.md) dotyczy istnienia odpowiednich klasyfikacji i warunków ich udostępnienia. Nie wysłano wiadomości ani nie aktywowano nowych danych.

## Dowody i weryfikacja
[Runtime](capital-double-runtime.json):93 284 kompaktowe interpretacje wejściowe,94 353 rozwinięcia źródłowe,125 360 kandydatów i282 110 składników.219 713 analiz/439 426 ocen,588 wspólnych dokumentów powodów. Powtórzenie obu materializacji bez nowych rekordów, identical logical-content, FK/integrityOK;258,018s łącznie z projekcją, konstrukcjami, ocenami i powtórzeniami. Baza źródłowa tylko odczytywana, nie cały build G8.

[Kontrola warunków](capital-double-conditions.json): po51 growo odrzuconych analiz mieszkańców i31 146 analiz podwojonej partykuły w każdym wariancie.14 analiz tańca bez odrzucenia przez te warunki; w pełnej diagnostyce pozostają unresolved. Nie są to delty finalnych list.

Test-first: normy wielkiej litery ImportError → policy → green; przypadek poprawnego uppercase miał błędne reject → ograniczono językowy warunek dawnej pisowni do lowercase. Podwojona partykuła ImportError → konstruktor/gamecheck → green. Build/explain ValueError(brak śladu) → integracja → green. Dotychczasowe testy podzbioru dopasowano do dodatkowych kandydatów, zachowując kontrolę FK, komponentów, śladów alternatywnych i częściowego zapisu po awarii. Nie załagodzono wyłączeń gry. Rozdzielenie homonimów, trwały zapis i readonly sprawdzone w JSON.151/151 całej suity i5/5 historycznego audytu OK, preflight14/14wejść+10konfiguracji.

## Źródła pierwotne i role
[RJP §8.1.2 pkt3](https://rjp.pan.pl/app/uploads/2025/11/2-zalacznik-do-komunikatu-11-25-wersja-jednolita.pdf#page=43), przypięty dokument normy; Morfeusz20260823/input/segmenty.dat334–340, hash w config/generator/evidence.json; [reguły gry §5](https://sjp.pl/sl/dp.phtml), wyłącznie odczyt reguł, bez list/werdyktów i redakcyjnych ograniczeń źródeł.

[Autorzy SGJP](https://sgjp.pl/o-slowniku/) opisują charakter gramatyczny słownika i zasadniczy brak znaczeń, podają kontakt oraz informują o dodaniu nazw miejscowości i derywowanych nazw mieszkańców wIVwydaniu. Nie wynika z tego dostępność konkretnego maszynowego pola ani licencja na internetową bazę. [Katalog pobrań Morfeusza](https://download.sgjp.pl/morfeusz/) w odczycie2026-10-05 wskazuje current=20260823; nie znaleziono nowszego publicznego eksportu rozwiązującego rozbieżność. To nowe obserwacje dokumentacji, bez zmiany przypiętych wejść.
