# Prosty język i minimum leksykalne — kierunki dalszych badań dla Literaki Lounge

Wersja: 1.0  
Data: 2026-10-04  
Status: publiczna notatka rozpoznawcza; opisane zasoby nie są zatwierdzonymi wejściami do budowy słowników.  
Opracowanie: z pomocą AI.

## 1. Podsumowanie i decyzja na obecny etap

Badania nad prostym językiem, słownictwem podstawowym oraz oceną trudności tekstu są wartościowym kierunkiem dla rozwoju mniejszych słowników Literaki Lounge. Mogą pomóc w projektowaniu botów o ograniczonym zasobie słownictwa, podpowiedzi opartych na codziennej polszczyźnie oraz profili tematycznych.

**Na razie nie włączamy opisanych poniżej zewnętrznych list słów, baz objaśnień ani danych leksykalnych narzędzi do procesu budowy słowników. W ramach tego rozpoznania nie potwierdziliśmy licencji lub innych warunków obejmujących planowane pozyskanie, przetwarzanie i udostępnianie tych danych lub wyników opartych na nich.**

Jest to decyzja dotycząca zakresu naszego projektu. Nie oznacza, że zasoby nie mają żadnej licencji, że uzyskanie odpowiednich uprawnień jest niemożliwe ani że inne sposoby ich wykorzystania są niedopuszczalne. Notatka nie dokumentuje odmowy udzielenia licencji przez żadnego z wymienionych autorów lub dostawców.

Zachowujemy te kierunki jako inspirację metodologiczną i temat do ewentualnego ponownego rozpoznania. Nie uzależniamy od nich realizacji obecnego etapu projektu.

## 2. Co obejmuje ten kierunek

Określenie „język uproszczony” prowadzi do kilku powiązanych, lecz odmiennych zagadnień.

**Prosty język — plain language.** Dotyczy zrozumiałej komunikacji: doboru słownictwa, budowy zdań i organizacji informacji. Nie jest po prostu zamkniętą listą wyrazów, z których wolno korzystać. Dobór słów zależy również od odbiorcy i celu wypowiedzi. [1]

**Język łatwy do czytania i rozumienia — ETR, easy-to-read.** To odrębne podejście do dostępności informacji, rozwijane przede wszystkim z myślą o dorosłych osobach z niepełnosprawnością intelektualną. Obejmuje także sposób prezentacji treści, na przykład ilustracje i układ tekstu. Nie należy utożsamiać go z dowolnym tekstem napisanym prostym językiem. [1]

**Słownictwo podstawowe i minimum leksykalne.** To kierunek związany z doborem zasobu przydatnego w podstawowej komunikacji i nauczaniu języka. Istnieją konkretne słowniki, których opisy wskazują zarówno selekcję słownictwa, jak i uporządkowanie tematyczne lub pojęciowe. [5][6]

Z punktu widzenia Literaki Lounge najbliższy celowi jest trzeci kierunek, uzupełniony badaniami nad powszechnością i znajomością słów. Jest to ocena przydatności dla naszego projektu, a nie klasyfikacja jakości tych podejść.

## 3. Zidentyfikowane zasoby i narzędzia

### 3.1. Jasnopis: listy słów uwzględniane przy ocenie trudności

Instrukcja Jasnopisu opisuje wyjątki od kwalifikowania wyrazów jako trudnych. Obejmują one 5000 wyrazów najczęściej występujących w polskich tekstach oraz wyrazy o wysokim „prawdopodobieństwie subiektywnym”, z odwołaniem do pracy J. Imiołczyka z 1987 roku. Są to składniki określonej metody oceny tekstu, nie uniwersalna definicja znajomości słowa. [2]

**Znaczenie dla projektu:** interesująca jest możliwość zestawienia częstości korpusowej z innym kryterium wyróżniania słów uznawanych w danej metodzie za łatwe. Ewentualne wykorzystanie wymagałoby poznania dokładnego pochodzenia list, jednostek opisu, wersji i sposobu ich doboru.

**Stan rozpoznania:** nie potwierdzono publicznego eksportu tych list wraz z licencją obejmującą planowane zastosowanie. Regulamin Jasnopisu opisuje korzystanie z aplikacji, zawiera ograniczenie automatycznego odpytywania i wskazuje potrzebę kontaktu przy innym niż opisane wykorzystaniu API. Nie traktujemy dostępu do aplikacji jako uprawnienia do pozyskania jej zaplecza leksykalnego. [3]

### 3.2. Logios: kilka zakresów słownictwa częstego

W publicznym opisie parametrów aplikacji Logios Redaktor występują wskaźniki **Top 100, Top 1000, Top 3000 oraz Top 2000 NET**. Ostatni z nich odnosi się do najczęstszych wyrazów w internecie. Aplikacja rozróżnia także słowa długie oraz słowa określane jako długie i rzadkie. [4]

**Znaczenie dla projektu:** jest to trop do badań nad kilkoma zakresami słownictwa, zamiast jednym podziałem na „łatwe” i „trudne”. Sama liczba w nazwie wskaźnika nie określa jednak poziomu bota ani kompetencji człowieka.

**Stan rozpoznania:** nie potwierdzono eksportu list oraz warunków pozwalających wykorzystać je w naszej bazie. Opis wskaźnika nie wystarcza do ustalenia dokładnej zawartości, pochodzenia i licencji danych, na których został oparty.

### 3.3. Halina Zgółkowa: „Słownik minimum języka polskiego”

Opis wydawcy wskazuje dobór haseł z wykorzystaniem pól tematycznych i zastosowanie słownika w nauczaniu polszczyzny. To kierunek szerszy niż mechaniczne wybranie początku listy frekwencyjnej. [5]

**Znaczenie dla projektu:** warto rozważać nie tylko częstość wyrazów, ale także pokrycie codziennych obszarów komunikacji. Dla naszego modelu mogłoby to oznaczać sprawdzanie, czy mniejszy słownik nie pomija całych grup przydatnych pojęć.

**Stan rozpoznania:** zidentyfikowano publikację i opis jej założeń, ale nie potwierdzono licencji na import listy haseł, przypisań tematycznych lub innych danych do redystrybuowanej bazy projektu. Zakupu egzemplarza nie uznajemy w naszym audycie za potwierdzenie takich uprawnień.

### 3.4. Zofia Kurzowa: słownik podstawowy z indeksem pojęciowym

„Ilustrowany słownik podstawowy języka polskiego wraz z indeksem pojęciowym wyrazów i ich znaczeń” obejmuje według opisu wydawcy około 5000 jednostek przydatnych w codziennym i oficjalnym porozumiewaniu się. Zawiera także indeks pojęciowy. [6]

**Znaczenie dla projektu:** połączenie podstawowego zasobu z organizacją pojęciową jest interesujące zarówno dla stopniowania wiedzy botów, jak i dla późniejszego rozwijania specjalizacji tematycznych.

**Stan rozpoznania:** nie potwierdzono otwartego zbioru danych ani licencji obejmującej planowany import i udostępnianie listy lub jej opracowania. Opis publikacji jest punktem odniesienia do dalszych badań, nie zgodą na przejęcie jej zawartości.

### 3.5. PSONI: „Słownik trudnych słów”

Serwis udostępnia trudne słowa wraz z wyjaśnieniami ich znaczeń. Nie jest to lista wyrazów prostych ani gotowy zestaw podstawowego słownictwa. [7]

**Znaczenie dla projektu:** kierunek jest bliższy projektowaniu przystępnych objaśnień dla graczy niż wybieraniu słów znanych początkującemu botowi. Nie należy uznawać hasła za podstawowe tylko dlatego, że jego znaczenie zostało objaśnione w dostępny sposób.

**Stan rozpoznania:** nie potwierdzono warunków pozwalających na hurtowe przejęcie haseł i objaśnień do projektu.

## 4. Jakie pomysły warto zachować

Poniższe punkty są propozycjami dla Literaki Lounge, a nie wynikami przeprowadzonego eksperymentu.

**Rozdzielenie częstości, znajomości i trudności.** Ranking korpusowy opisuje użycie w określonym materiale. W naszym modelu nie powinien samodzielnie rozstrzygać, że słowo jest znane wszystkim graczom. Analogicznie nie zamieniamy oceny trudności całego tekstu w ocenę wiedzy bota.

**Pokrycie codziennych tematów.** Przy ocenie mniejszych słowników warto badać, czy reprezentują różne obszary codziennej komunikacji. Można zaprojektować własne kryteria takiego przeglądu bez przejmowania gotowych przypisań tematycznych z opisanych publikacji.

**Kilka zakresów wiedzy.** Zamiast jednego słownika „prostego” można badać kilka zagnieżdżonych poziomów. Ich liczebności i użyteczność powinny wynikać z naszych danych i testów, a nie z automatycznego przeniesienia progów innego narzędzia.

**Osobna warstwa objaśnień.** To, które słowo bot zna, oraz to, jak wyjaśnić jego znaczenie graczowi, są różnymi zadaniami. Ewentualny zbiór objaśnień wymagałby osobnego ustalenia źródeł, uprawnień i jakości.

Te kierunki dotyczą przede wszystkim **słowników znajomości**. Nie zmieniają zasad kwalifikowania form do dużego słownika dopuszczalności. Zachowujemy rozdzielenie przyjęte w specyfikacji projektu v3: słownik bota pozostaje podzbiorem słownika obowiązującego przy stole.

Poziomom botów nie przypisujemy diagnoz, stopni niepełnosprawności ani automatycznych odpowiedników wieku lub wykształcenia. Interesuje nas model zasobu słów w grze, nie ocena osób korzystających z określonego standardu komunikacji.

## 5. Granice wykorzystania na obecnym etapie

Dla opisanych zasobów przyjmujemy projektowy status **BLOCKED — nieustalone warunki planowanego użycia danych**. Dotyczy on konkretnych list i baz, które chcielibyśmy pozyskać, a nie całych dziedzin badań ani wszelkiego korzystania z wymienionych usług.

Na tym etapie:

- nie importujemy ich list haseł, rankingów, kwalifikacji ani objaśnień do bazy projektu; nie używamy ich również jako zbiorów wzorcowych do kalibracji modeli znajomości;
- nie odtwarzamy zaplecza leksykalnego usług przez masowe zapytania ani nie traktujemy pośredniego przepisania danych przez model AI jako zastępstwa za ustalenie uprawnień;
- zachowujemy opisy i odnośniki bibliograficzne oraz możemy rozważać ogólne pomysły metodologiczne, wyraźnie oddzielając je od przejęcia danych.

Ewentualny powrót do konkretnego źródła wymagałby wskazania artefaktu i wersji, ustalenia pochodzenia danych oraz udokumentowania warunków obejmujących zamierzone czynności: pozyskanie, przetwarzanie, włączenie do projektu i odpowiedni zakres publikacji wyników. Osobno należy sprawdzić obowiązki atrybucji i zgodność z zasadami doboru źródeł w specyfikacji v3.

Nie zakładamy, że brak otwartego eksportu wyklucza indywidualne uzgodnienie warunków. Nie zakładamy też, że samo uzyskanie dostępu technicznego rozstrzyga warunki wykorzystania.

## 6. Zakres ustaleń i źródła

Notatka opiera się na publicznych instrukcjach, opisach funkcji, informacjach wydawcy i stronie słownika. Nie obejmuje analizy pełnej zawartości książek, eksportów wewnętrznych list ani kompletnego audytu licencyjnego. Potencjalne zastosowania w grze są propozycjami projektu.

Stan rozpoznania: **4 października 2026 r.** Informacje o dostępności i warunkach wykorzystania należy ponownie sprawdzić przed jakąkolwiek decyzją o włączeniu danych.

[1] [Jasnopis — Prosty język](https://jasnopis.pl/prosty-jezyk/). Charakterystyka prostego języka i odróżnienie go od ETR.

[2] [Jasnopis — Instrukcja](https://www.jasnopis.pl/instrukcja/). Opis kryteriów trudności słów, listy 5000 wyrazów i odwołanie do prawdopodobieństwa subiektywnego.

[3] [Jasnopis — Regulamin](https://jasnopis.pl/regulamin/). Warunki korzystania z aplikacji i ograniczenia dotyczące automatycznego odpytywania oraz API.

[4] [Logios Redaktor — konfiguracja parametrów](https://redaktor.logios.dev/config/). Opis wskaźników Top 100, Top 1000, Top 3000 i Top 2000 NET; część interfejsu jest ładowana dynamicznie.

[5] [Universitas — Halina Zgółkowa, „Słownik minimum języka polskiego”](https://www.universitas.com.pl/pl/ksiazki/2-slownik-minimum-jezyka-polskiego.html). Opis publikacji i doboru haseł według pól tematycznych.

[6] [Universitas — Zofia Kurzowa, „Ilustrowany słownik podstawowy języka polskiego wraz z indeksem pojęciowym wyrazów i ich znaczeń”](https://www.universitas.com.pl/en/books/47-ilustrowany-slownik-podstawowy-jezyka-polskiego-wraz-z-indeksem-pojeciowym-wyrazow-i-ich-znaczen.html). Opis zakresu publikacji i indeksu pojęciowego.

[7] [PSONI — Słownik trudnych słów](https://slownik.psoni.org.pl/). Internetowy słownik objaśnień.

Powiązany dokument projektu: „Słowniki języka polskiego dla Literaki Lounge — specyfikacja projektu v3”, w szczególności rozdziały 2.1, 4, 9 i 10. Niniejsza notatka go nie zmienia.

Nazwy autorów, instytucji, publikacji i narzędzi służą identyfikacji źródeł. Ich wymienienie nie oznacza współpracy, patronatu ani zatwierdzenia projektu przez te podmioty. Notatka nie jest opinią prawną, nie przypisuje projektowi praw do materiałów zewnętrznych i nie nadaje uprawnień do ich wykorzystania.

## 7. Wniosek końcowy

**Prosty język, minimum leksykalne i badania nad znajomością słów pozostają ważnym kierunkiem dla Literaki Lounge. Opisane zasoby zachowujemy w dokumentacji jako tropy do dalszych badań, ale na razie nie wykorzystujemy ich danych do budowy słowników ani profili botów, ponieważ nie potwierdziliśmy warunków licencyjnych obejmujących takie zastosowanie.**
