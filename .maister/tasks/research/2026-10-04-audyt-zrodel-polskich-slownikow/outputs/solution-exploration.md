# Warianty pierwszego generatora — materiał do decyzji

Data: 2026-10-04. Faza: porównanie rozwiązań po zatwierdzonym audycie. **Użytkownik wybrał G1 (odpowiedź A na D1): BROAD i STANDARD z pełną dopuszczalną fleksją, wyjaśnieniami i dowodami KWJP.** **D2=A/N1: pierwszy wynik SGJP/KWJP, NKJP później po wyjaśnieniu warunków.** **D3=A/C1: udokumentowane konstrukcje istniejących leksemów w głównych kandydatach po kontroli klas.** Konwergencja zakresu zakończona; propozycje techniczne podlegają zatwierdzeniu projektu. Zgoda „tak i tak” włączyła porównanie i projekt, nie implementację.

## TL;DR

Wybrany pierwszy wynik to dwa kandydaty: BROAD i STANDARD, z pełną dopuszczalną fleksją, dowodami KWJP oraz wyjaśnieniami decyzji. Lokalny, odtwarzalny proces pozostaje rekomendacją techniczną do projektu. Najpierw trzeba udowodnić reguły istotne dla kompletności i rozstrzygnąć rzeczywiste wybory zakresu. Słowniki znajomości, tematy i benchmark pozostają późniejszymi etapami.

Nie wybrano wcześniejszego pilota jako wyniku końcowego ani czterech wariantów w pierwszym wydaniu. Pilot może być etapem prac; warianty ATTESTED pozostają odroczone.

NKJP pozostaje BLOCKED we wszystkich opcjach. Brak dowodów dotyczących licencji lub znaczenia oznaczeń nie jest kwestią gustu do rozstrzygnięcia głosowaniem. Można wybrać kolejność prac i sposób prezentowania niewiedzy.

## Key Decisions

**Już obowiązujące wymagania:** §2 i §6 [specyfikacji v3](../../../../../docs/literaki-niezalezne-slowniki-prompt-v3.md): pełna dopuszczalna fleksja, oddzielenie dopuszczalności od znajomości, współczesny i szeroki STANDARD, brak produktywnego tworzenia nowych leksemów, kwalifikacja jednej interpretacji przed agregacją form. Nie pytamy o nie ponownie.

**D1 zatwierdzona — G1:** dwa pełne kandydaty BROAD i STANDARD, wyjaśnienia i dowody KWJP; kontrola kompletności przed odbiorem. Oznaczenie INCOMPLETE nie spełnia kryterium wyniku końcowego.

**D2 zatwierdzona — N1:** pierwszy wynik korzysta z SGJP/KWJP; NKJP pozostaje wymaganiem pełnego projektu i dołączy po wyjaśnieniu warunków w nowym wydaniu.

**D3 zatwierdzona — C1:** konstrukcje istniejących leksemów należą do BROAD/STANDARD po kontroli reguł każdej klasy. Lista konkretnych reguł nadal wymaga dowodów. Q2 jest konsekwencją G1: niepełny pilot nie zastępuje odbioru. F1 i O2/O3 pozostają propozycjami technicznymi projektu.

**Rekomendacje techniczne do późniejszego projektu:** lokalne polecenia i jedna relacyjna baza, zachowane rekordy źródłowe i manifesty, brak API i usług. SQLite jest hipotezą startową, nie wynikiem testu wydajności. [Model procesu](../analysis/findings/model-procesu.md).

## Open Questions / Risks

- Przyjęto C1; [uzupełnienie](../analysis/findings/construction-scope.md) rozdziela dowody klas od wyboru zakresu.
- Wykonawcza macierz klas i kompletność ich reguł pozostają do udowodnienia; pełna fleksja jest obowiązkowa.
- Nie mamy jeszcze podziału wszystkich nietypowych zapisów na zwykłe wyrazy, skrótowce, nazwy i symbole ani dowodu semantyki mieszanych kwalifikatorów. Rozstrzygnięcie wymaga dalszych przykładów i źródeł, nie automatycznego `lower()`.
- Nie wykazano kompletności wszystkich klas odmiany. Wstrzymanie dowolnej wymaganej klasy daje wynik niepełny; nie może realizować obietnicy końcowej pełnej fleksji.
- NKJP nie bierze udziału w generowaniu. Nieustalone pozostają też część historii anotacji KWJP i jakość przyszłych rankingów znajomości.

## 1. Punkty wyjścia i kryteria

Materiałem są zatwierdzony [raport](research-report.md), [synteza](../analysis/synthesis.md), dowody [SGJP](../analysis/findings/sgjp-rules.md), [KWJP](../analysis/findings/kwjp-findings.md), [NKJP](../analysis/findings/nkjp-audit.md) i [zakres dalszych faz](../planning/next-phases.md). Pierwotne porównanie nie obejmowało nowych pomiarów. W konwergencji dodano [uzupełnienie bibliograficzne konstrukcji](../analysis/findings/construction-scope.md); pomiarów scenariuszy nie zmieniano. Oceny poniżej są rekomendacjami projektowymi, nie pomiarami.

Pytania otwierające alternatywy:

1. Jak uzyskać pierwszy użyteczny wynik bez obiecywania nieudowodnionej kompletności?
2. Jak zachować pełne rodziny fleksyjne, nie dopisując wszystkiego, co rozpozna analizator?
3. Jak zachować informację o niepewności bez arbitralnego kwalifikowania słów?
4. Jak oddzielić ortografię i kategorię wyrazu od technicznego klucza gry?
5. Jak kontynuować pracę przy blokadzie jednego źródła, nie omijając tej blokady?

Ocena używa pięciu kryteriów: **prostota** utrzymania, **pokrycie** wymagań, jakość **dowodów**, **powtarzalność** oraz przydatność do **późniejszego benchmarku**. Brak wymaganych dowodów eliminuje twierdzenie o gotowości niezależnie od pozostałych zalet.

## 2. Podejścia globalne: pierwszy wynik

| Opcja | Pierwszy wynik | Argument za | Koszt i ograniczenie |
|---|---|---|---|
| **G1 — dwa kandydaty z wyjaśnieniami** | BROAD i STANDARD z pełną dopuszczalną fleksją zakwalifikowanych leksemów, po kontroli przyjętych klas; import KWJP i powiązania dowodów; manifest, eksport i wyjaśnienie słowa | Bezpośrednio sprawdza podstawę przyszłego zamiennika słownika, zachowując mały zakres | Nie można ogłosić kompletności przed kontrolą fleksji i rozstrzygnięciem wymaganych klas; brak gotowych ATTESTED |
| **G2 — pilot techniczny przed kandydatami** | Import, baza, decyzje dla rozstrzygniętych rekordów, raport niewiedzy i techniczny eksport z oznaczeniem `INCOMPLETE` | Najszybszy sposób sprawdzenia modelu, kosztu obliczeń i wyjaśnień bez czekania na wszystkie dowody | Nie realizuje obietnicy pełnych słowników. Nie jest końcowym BROAD/STANDARD ani podstawą wyboru słownika do gry; wymaga następnego etapu |
| **G3 — cztery warianty w pierwszym wydaniu** | G1 oraz ATTESTED-LEXEME i eksperymentalny ATTESTED-FORM, oparte na wybranej bazie i KWJP | Od razu pozwala ocenić skutki poświadczeń i niepełnych rodzin wariantu FORM | Więcej mapowań, progów i próbek do oceny; niejednoznaczność leksemów komplikuje pierwsze zakończenie; nadal bez znajomości i tematów |

| Kryterium | G1 | G2 | G3 |
|---|---|---|---|
| Prostota | Dwie polityki, jeden proces | Najmniejszy zakres bieżący, dwa etapy odbioru | Najwięcej zależności i konfiguracji |
| Pokrycie | Pełna baza dopuszczalności w przyjętym zakresie | Jawnie częściowe | Baza oraz dwa eksperymenty korpusowe |
| Dowody | Wymaga domknięcia wymaganych klas | Umożliwia pracę mimo braków, lecz ich nie rozstrzyga | Wymaga dodatkowo obronionych kryteriów poświadczenia |
| Powtarzalność | Manifesty, deterministyczne eksporty | Także manifesty; obowiązkowy rejestr pominięć | Jak G1 oraz wersje mapowań i progów |
| Późniejszy benchmark | Dwa zamrożone warianty po odbiorze | Dopiero po uzupełnieniu; pilot nie zastępuje kandydatów | Cztery zamrożone warianty po odbiorze |

**Rekomendacja: G1.** G2 pozostaje rozsądnym kamieniem milowym wewnątrz realizacji G1, ale nie zastępuje jego kryteriów końcowych. G3 ma sens, gdy priorytetem jest szybkie porównanie wpływu korpusów, a użytkownik akceptuje szerszy pierwszy etap. Modele znajomości, tematy, integracja gry i sam benchmark są odroczone we wszystkich trzech opcjach.

## 3. Konstrukcje z segmentów: dwie odrębne osie

### 3.1. Jak osiągnąć pokrycie bez nadgeneracji

Audyt wykazał pełne `czytałem/czytałbym` w eksporcie i nadmiar 120 trójek w kontrolnym mechanicznym składaniu. `bym/byśmy/przezeń/czytajże` nie znaleziono jako pełnych rekordów w badanej próbce; są to osobne przypadki konstrukcji, nie dowód braku całej fleksji. [Dowody i zakres kontroli](../analysis/findings/sgjp-rules.md).

| Opcja | Metoda | Korzyść | Koszt/ryzyko |
|---|---|---|---|
| **F1 — eksport i mała lista zatwierdzonych reguł** | Pełne formy z eksportu; każda potrzebna rekonstrukcja ma dowód, składniki, zakres, dodatnie i ujemne przykłady | Najprostsze wyjaśnienie pochodzenia, kontrola defektywności | Wymaga inwentaryzacji klas; lista reguł sama nie dowodzi kompletności |
| **F2 — generator oparty na ograniczonym silniku Morfeusza** | Przypięty SGJP i reguły, wyłącznie zatwierdzony podzbiór przejść; wynik z pełnym śladem interpretacji | Wspólna reprezentacja skomplikowanych konstrukcji i narzędzie kontroli reguł | Więcej kodu integracji; trzeba udowodnić brak ścieżek słowotwórczych, a pozytywna analiza nadal nie wystarcza |
| **F3 — najpierw zamknięta macierz klas i kontrola referencyjna** | Przed modułem rekonstrukcji udokumentować oczekiwania dla wszystkich klas, osobno wykonać kontrolne wyliczenia, dopiero potem dobrać reguły | Najmocniejsza podstawa obietnicy kompletności i przyszłych aktualizacji | Najwolniejszy pierwszy eksport; wymaga większego nakładu eksperckiego przed implementacją |

**Rekomendacja: F1 z macierzą pokrycia jako kryterium odbioru**, bez wymogu budowania drugiego kompletnego generatora z F3. Ani filtrowanie POS w ciemno, ani wszystkie ścieżki analizatora nie są dopuszczalną alternatywą. Tymczasowe odroczenie klasy jest możliwe tylko przy oznaczeniu niepełności, jak G2.

### 3.2. Jaki zakres mają mieć konstrukcje wieloleksemowe

To wybór produktu odrębny od implementacji F1–F3. Żaden wariant nie znosi zakazu tworzenia nowych leksemów ani wymogu pełnej fleksji. Przed ostatecznym wyborem należy przedstawić rozdzielone klasy z przykładami, dowodem samodzielnej pisowni i kwalifikacją ortograficzną.

| Opcja | Zakres | Obrona wariantu | Konsekwencja |
|---|---|---|---|
| **C1 — włączyć udokumentowane klasy samodzielnych zapisów** | Kontrolowane konstrukcje istniejących leksemów należą do kandydatów po potwierdzeniu reguł i pisowni | Użytkownik gry widzi całe poprawne słowo; nie powinien odczuwać przypadkowego podziału źródła na segmenty | Większa praca nad regułami; nie wolno rozciągnąć zgody na wszystkie konstrukcje analizatora |
| **C2 — osobny eksperyment konstrukcyjny** | Podstawowi kandydaci i osobny zbiór rozszerzony o potwierdzone konstrukcje; żaden nowy leksem | Pozwala ocenić zmianę zakresu przed włączeniem do bazy gry | Więcej wariantów i jawna informacja o pominiętych klasach; nie może ukrywać braków wymaganej fleksji w bazie |
| **C3 — wstrzymać zamrożenie do pełnego przeglądu klas** | Najpierw dowody i lista wymaganych konstrukcji, potem jeden spójny zakres kandydatów | Unika publikacji kilku konkurencyjnych definicji tego, co generator obejmuje | Odkłada pierwszy kandydat; prace nad importem i bazą mogą trwać |

**Rekomendacja kierunkowa: C1**, ale zatwierdzenie wykonawczej listy klas dopiero po ich przeglądzie. Nie należy prosić użytkownika o jedną zbiorczą odpowiedź dla `by`, przyimek+`ń` i rozkaźnik+partykuła, jeżeli dowody ujawnią różne zasady pisowni. C2 nie jest furtką do stałego pomijania pełnej fleksji obiecanej w §2.2.

## 4. Mieszane kwalifikatory: postępowanie z niewiedzą

W `daw.|górn.` techniczny separator nie rozstrzyga semantyki. Brak kwalifikatora nie dowodzi współczesności. `hist.` nie jest automatycznie przestarzałością. Jedna prawidłowa interpretacja może zachować napis pomimo odrzucenia innej. [Dowody parsera i ograniczenia](../analysis/findings/sgjp-rules.md), [pomiary scenariuszy](research-report.md).

Przykłady z utrwalonego pomiaru: `bonowali` od `bonować` ma `daw.|górn.`, a `burtowali` od `burtować` — `daw.|żegl.`. Nie zakładamy ani „zawsze dawne”, ani „wystarczy kwalifikator fachowy, żeby przyjąć”. Podobny problem dotyczy pola nazw: `AI` występuje z `nazwa_pospolita|nazwa_firmy`; sama obecność pierwszej etykiety nie wyjaśnia sposobu przypisania kwalifikacji do interpretacji. [Zapisane statystyki i przykłady](../analysis/findings/sgjp-stats.json).

W każdej opcji baza ma wynik `accept/reject/unresolved`; nie wolno nazwać braku dowodu pewnym odrzuceniem ani przyjęciem. Różny jest **warunek publikacji**, a nie domyślne znaczenie etykiet.

| Opcja | Postępowanie | Argument za | Ograniczenie |
|---|---|---|---|
| **Q1 — częściowy eksport i jawna kolejka** | Eksport obejmuje wyłącznie interpretacje rozstrzygnięte; osobny raport pokazuje potencjalnie utracone formy | Pozwala wcześnie sprawdzić proces i koszt ostrożności | Wynik częściowy, nie dowód pełnego pokrycia; `unresolved` musi być widoczne w wyjaśnieniu |
| **Q2 — bramka przed zamrożeniem** | Zamrożenie pełnego kandydata wymaga rozstrzygnięcia istotnych klas; baza i raporty powstają wcześniej | Spójne z obietnicą pokrycia, nie redukuje zasobu ukrytym filtrem | Termin zależy od dostępności dowodów; można zakończyć jedynie pilot |
| **Q3 — dwa diagnostyczne scenariusze graniczne** | Osobno policzyć wynik potwierdzony i hipotetyczny zasięg wpływu przypadków nierozstrzygniętych | Pozwala określić wagę problemu przed kosztownym wyjaśnianiem | Górny scenariusz nie jest słownikiem poprawnych słów; dochodzi raportowanie, bez rozwiązania semantyki |

**Rekomendacja: Q2 dla końca G1; Q1 podczas prac, Q3 tylko gdy mierzalny wpływ pomoże ustalić kolejność wyjaśnień.** Nie zgadujemy semantyki dla terminowego wydania. Ogólnej decyzji użytkownika wymaga zgoda na wcześniejszy wynik częściowy, a nie sposób rozumienia nieudokumentowanego separatora.

## 5. Wielkie litery, skróty i skrótowce

Wykluczenie nazw własnych, skrótów i symboli jest ustalone. Zleksykalizowane wyrazy o pochodzeniu skrótowym wymagają odrębnej kwalifikacji. Wielka litera sama nie koduje kategorii semantycznej; mała litera w KWJP również nie dowodzi pospolitości. `lower()` tworzy techniczny klucz **po** kwalifikacji i nie nadaje słowu dopuszczalności. [Specyfikacja §6](../../../../../docs/literaki-niezalezne-slowniki-prompt-v3.md), [KWJP: Róża/róża](../analysis/findings/kwjp-findings.md).

To obecnie przede wszystkim luka dowodowa. Trzy metody jej usunięcia:

| Opcja | Metoda | Argument za | Koszt |
|---|---|---|---|
| **O1 — ręczny przegląd wszystkich przypadków spornych** | Każdy przypadek otrzymuje źródło, kategorię i uzasadnienie; decyzje wersjonowane | Najłatwiej wyjaśnić pojedynczy trudny przypadek bez upraszczającej reguły | Koszt aktualizacji i ryzyko niespójnego oceniania; wielkość pracy trzeba zmierzyć |
| **O2 — reguły dla potwierdzonych klas i kolejka reszty** | Udokumentowane klasy obsługiwane jednakowo; przypadki bez dowodu pozostają nierozstrzygnięte | Dobry kompromis odtwarzalności i pracy ręcznej | Reguła nie może być tylko testem wielkiej litery; kolejka może blokować pełny wynik |
| **O3 — najpierw rozszerzony audyt oznaczeń źródła** | Przed wyborem filtra uzyskać mapowanie kategorii i reprezentacji z dokumentacji lub oficjalnego wyjaśnienia | Najlepsza podstawa trwałej automatyzacji zamiast listy wyjątków | Zależność od dostępności źródła; nie gwarantuje usunięcia wszystkich niejednoznaczności |

**Rekomendacja: O2, z O3 dla reguł, których znaczenia nie potwierdzono.** O1 może uzupełniać udokumentowane wyjątki niezależne od przyszłego benchmarku. Nie ma jeszcze podstaw do pytania „dopuszczamy wszystkie wielkie litery?” ani do filtra „wykluczamy wszystkie skrótowce”.

Jeżeli po rozdzieleniu kategorii pozostanie rzeczywisty wybór growej polityki pisowni, przedstawimy go osobno na zweryfikowanych przykładach. Decyzja użytkownika nie zastępuje dowodu, do której kategorii dany rekord należy. Liczebności scenariusza `wielka_litera_do_oceny` z audytu nie są liczbą skrótowców.

## 6. NKJP: harmonogram, nie uchylenie blokady

Dokładny artefakt ma status BLOCKED do konstrukcji i dopasowań. Wymaga oficjalnego doprecyzowania warunków; techniczna dostępność tego nie zmienia. [Audyt NKJP](../analysis/findings/nkjp-audit.md).

| Opcja | Kolejność | Argument za | Koszt |
|---|---|---|---|
| **N1 — pierwszy wynik SGJP/KWJP, NKJP później** | Projektować pierwszy generator na dopuszczonych wejściach; NKJP `UNAVAILABLE` z powodem | Nie blokuje podstawy dopuszczalności; uczciwe jawne ograniczenie korpusów | Nie daje jeszcze wariantów wymagających potwierdzenia w obu korpusach |
| **N2 — rozwijać SGJP/KWJP, wstrzymać wydanie do NKJP** | Prace techniczne idą dalej; publikacja docelowego wydania czeka na wyjaśnienie i osobny odbiór importu | Jedno pełniejsze pierwsze wydanie i mniej przejściowych wariantów | Termin wydania zależy od zewnętrznego dowodu |
| **N3 — najpierw wyjaśnić NKJP, potem implementacja** | Po projekcie priorytetem jest uzupełnienie dowodów przed kodem | Racjonalne przy małym zespole, który nie chce utrzymywać przejściowego zakresu | Opóźnia także prace niezależne od NKJP, bez pewności daty rozwiązania |

**Rekomendacja: N1.** Późniejsze odblokowanie oznacza nowy manifest i jawne wydanie. Żaden wariant nie pozwala korzystać z danych wcześniej. N1 może być zatwierdzone niezależnie od G1–G3; wybór szerszego pierwszego generatora nie musi uzależniać terminu od zablokowanego źródła. NKJP pozostaje wymaganiem pełnego zakresu projektu, z jawnym statusem blokady; N1 odracza jego udział, nie usuwa tego wymagania. Kontakt z autorami wymaga osobnego polecenia wysłania wiadomości; teraz dokumentujemy potrzebny dowód.

## 7. Granica projektu i następna decyzja

**W zakresie teraz:** porównanie, rozstrzygnięcia polityki i projekt generatora. **Późniejsza implementacja:** import, baza, reguły, eksport, wyjaśnienia i kontrole; wymaga osobnego zadania. **Późniejsze osobne etapy:** modele znajomości, tematy, benchmark po zamrożeniu i integracja gry. Nie dobieramy progów pod benchmark i nie pozyskujemy jego danych.

Proponowana kolejność rozmowy:

1. **Pierwszy wynik: G1/G2/G3.** To określa, co projekt ma uznawać za skończone.
2. **Harmonogram NKJP: N1/N2/N3.** Osobna krótka decyzja o zależności wydania; nie o warunkach użycia.
3. **Zakres konstrukcji C1/C2/C3**, po doprecyzowaniu klas i ich dowodów. Implementacyjne F1–F3 są rekomendacją projektu, nie koniecznie osobną rundą pytań.
4. **Akceptacja lub brak akceptacji częściowego wyniku przy nierozstrzygniętych klasach.** Q2 wynika z celu pełnego G1; nie potrzeba ponownego pytania, jeżeli użytkownik już wybrał bramkę kompletności. Semantykę kwalifikatorów i kategorie skrótowców ustalamy z dowodów; pytanie normatywne dopiero wtedy, gdy po audycie rzeczywiście pozostanie wybór.
5. Zatwierdzenie projektu wysokiego poziomu obejmującego rozstrzygnięte osie, otwarte zależności i kryteria odbioru. Nie przedstawiać nieudowodnionych reguł jako gotowych do implementacji.

**Historia D1 — pytanie rozstrzygnięte odpowiedzią A:**

> Co uznajemy za pierwszy docelowy wynik generatora? **A — dwa wyjaśnialne kandydaty BROAD i STANDARD, z pełną dopuszczalną fleksją zakwalifikowanych leksemów i dowodami KWJP (rekomenduję); B — wcześniejszy pilot techniczny, jawnie niepełny; C — od razu te dwa oraz ATTESTED-LEXEME i ATTESTED-FORM.** NKJP i zakres konstrukcji rozstrzygniemy osobno; ta odpowiedź nie zatwierdza reguł językowych.

**Rozstrzygnięcie D1: A / G1.** Zaakceptowany koszt: końcowi kandydaci wymagają kontroli pełnej dopuszczalnej fleksji i rozstrzygnięcia istotnych klas. Pilot nie zastępuje odbioru, ATTESTED odroczone. Pozostałe rekomendacje nie są automatycznie zatwierdzone.

**Historia D2 — rozstrzygnięta A / N1:** Czy pierwszy wynik ma czekać na wyjaśnienie warunków NKJP? A / N1: SGJP i KWJP najpierw, NKJP później (rekomendacja); B / N2: prace SGJP/KWJP mogą trwać, ale wydanie czeka; C / N3: wyjaśnienie NKJP przed implementacją. Wszystkie opcje zachowują blokadę użycia oraz NKJP jako wymaganie pełnego projektu.


**Historia D3 — rozstrzygnięta A / C1:** Czy udokumentowane konstrukcje istniejących leksemów, takie jak przyimek z `-ń` i rozkaźnik z partykułą, uwzględniamy w głównych kandydatach? A/C1: tak, po kontroli każdej klasy (rekomendacja); B/C2: osobne rozszerzenie; C/C3: decyzja po pełnej macierzy klas. [Dowody, granice i konsekwencje](../analysis/findings/construction-scope.md). Wymagana fleksja, w tym kontrola `bym/byśmy`, nie podlega ponownemu głosowaniu.

## 8. Wynik konwergencji

Użytkownik kolejno wybrał G1, N1 i C1. Odrzucono pilot jako wynik końcowy, cztery warianty w pierwszym wydaniu, oczekiwanie na NKJP i osobne rozszerzenie konstrukcyjne. Zachowano wymóg kontroli kompletności.

Nie pytamy o znaczenie nierozstrzygniętych kwalifikatorów: wymaga dowodów. Jeśli badanie ujawni nowy wybór normatywny, należy wrócić z konkretnymi przykładami. Techniczne F1 i O2/O3 zostaną ocenione w projekcie; nie są osobno zatwierdzoną polityką.
