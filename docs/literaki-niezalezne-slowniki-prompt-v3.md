# Słowniki języka polskiego dla Literaki Lounge — specyfikacja projektu v3

Wersja: 3.0  
Data: 2026-10-04  
Status: specyfikacja robocza przygotowana do publikacji.  
Charakter dokumentu: cele, wymagania i instrukcje wykonawcze projektu.  
Opracowanie: z pomocą AI; uwzględnia przegląd i przyjęte decyzje projektowe.

Dokument opisuje planowane prace. Wyniki pomiarów, potwierdzenie pochodzenia danych i ustalenia dotyczące licencji będą przedstawiane w osobnych, wersjonowanych raportach. Niniejsza specyfikacja nie jest raportem z zakończonego audytu ani opinią prawną.

Nazwy instytucji, słowników, korpusów i narzędzi służą identyfikacji źródeł oraz metod. Ich przywołanie nie oznacza patronatu, autoryzacji ani zatwierdzenia projektu przez te podmioty. Dobór źródeł, filtry i nazwy wynikowych wariantów są decyzjami projektu Literaki Lounge. Atrybucje dla wykorzystanych zasobów należy zachować zgodnie z ich warunkami.

Sformułowania nakazujące lub wyłączające określone działania opisują wymagania wykonawcze **tego projektu**. Wyłączenie źródła ze względu na przyjętą metodę nie jest oceną jego jakości ani stwierdzeniem, że inni nie mogą z niego korzystać. Warunki wykorzystania każdego zasobu rozpatruje się odrębnie.

## 1. Cel projektu i bieżący zakres wykonania

Zaprojektuj odtwarzalny proces budowy słowników języka polskiego dla Literaki Lounge z udokumentowanych źródeł i reguł. Założeniem konstrukcji jest niewykorzystywanie danych SJP.pl ani OSPS jako materiału wejściowego do generowania słowników. SJP.pl przewidziano jako późniejszy punkt odniesienia w porównaniu; OSPS pozostaje poza zakresem prac. Dokładne znaczenie tego rozdzielenia określa rozdział 3.

Projekt ma cztery powiązane cele:

1. Zbudować kilka dużych słowników dopuszczalności słów, z których po ocenie będzie można wybrać jeden lub dwa do zastąpienia dotychczasowej listy SJP.pl w Literaki Lounge.
2. Porównać zamrożonych kandydatów z konkretnym wydaniem listy SJP.pl, aby opisać różnice pokrycia i skutki dla gry. Podobieństwo do SJP.pl nie jest jedynym ani nadrzędnym kryterium wyboru.
3. Zbudować mniejsze słowniki codziennej polszczyzny o różnych rozmiarach, przeznaczone dla narzędzi ułatwiających grę i botów o ograniczonej znajomości słów.
4. Przygotować słowniki tematyczne pozwalające modelować zainteresowania i specjalizacje botów.

**Pierwsze wykonanie tej specyfikacji obejmuje wyłącznie etap opisany w rozdziale 15: audyt źródeł, analizę danych i projekt filtrów.** Pozostałe rozdziały określają wymagania dla całego projektu. Na tym etapie nie buduj kompletu końcowych słowników ani nie wykonuj benchmarku SJP.pl.

## 2. Uzgodnione zasady projektu

### 2.1. Dopuszczalność słowa a znajomość słowa

Rozdziel dwa rodzaje słowników:

- **Słownik dopuszczalności** określa, czy daną formę można ułożyć przy stole.
- **Słownik znajomości** określa, które dopuszczalne słowa zna dany bot albo pokazuje dane narzędzie pomocnicze.

Każdy słownik znajomości musi być podzbiorem konkretnego, wersjonowanego słownika dopuszczalności. Rzadkość słowa może ograniczać wiedzę bota, lecz sama w sobie nie jest powodem wykluczenia go z szerokiego słownika gry.

Znajomość słowa nie oznacza znalezienia najlepszego ruchu. Parametry słownika i parametry strategii oraz przeszukiwania ruchów opisuj oddzielnie. Projekt nie wymaga teraz implementacji nowego silnika gry ani przebudowy botów.

### 2.2. Pełna poprawna fleksja

Duży słownik dopuszcza pełną poprawną odmianę zakwalifikowanych leksemów, w granicach polityki danego wariantu oraz reguł gry. Nie wymagaj, aby każda forma fleksyjna była osobno poświadczona w korpusie.

„Pełna” oznacza wszystkie dopuszczalne formy wynikające z danych i reguł fleksyjnych przyjętych w projekcie, a nie wszystkie ciągi rozpoznawane przez analizator. Odrzucona interpretacja lub historyczny wariant formy nie wraca do STANDARD tylko dlatego, że pozostałe formy tego leksemu są współczesne.

Potwierdzenie konkretnej formy zachowaj jako odrębny wariant eksperymentalny i sygnał przy tworzeniu słowników znajomości.

### 2.3. Zakres STANDARD

STANDARD ma obejmować współczesną polszczyznę, również rzadką, nieformalną i specjalistyczną. Zachowuj co do zasady:

- potocyzmy;
- wulgaryzmy;
- regionalizmy;
- terminologię fachową i naukową;
- słowa rzadkie.

Ograniczaj przede wszystkim jednoznacznie przestarzałe słownictwo i historyczne warianty pisowni, jeśli oznaczenia źródłowe pozwalają je wiarygodnie rozpoznać. Nie utożsamiaj rzadkości, regionalności ani specjalistyczności z przestarzałością. Brak kwalifikatora nie stanowi dowodu współczesności; zachowaj informację o ograniczeniach klasyfikacji.

### 2.4. Granica między fleksją a słowotwórstwem

Podstawą wszystkich początkowych dużych wariantów, także BROAD, są **leksemy udokumentowane w danych SGJP udostępnionych z Morfeuszem oraz ich poprawne formy fleksyjne**.

Nie rozszerzaj automatycznie zasobu leksemów przez produktywne dodawanie prefiksów, składanie członów lub inne reguły słowotwórcze. Samo rozpoznanie konstrukcji przez analizator nie wystarcza do przyjęcia jej do słownika.

Nie odrzucaj jednak istniejącego leksemu tylko dlatego, że ma budowę prefiksalną lub złożoną. Decydujące jest jego udokumentowanie w dopuszczonym źródle.

Rozszerzenia słowotwórcze można później zbadać jako osobny eksperyment, z jawnymi regułami i oceną przykładów. Nie są częścią pierwszego generatora.

## 3. Rozdzielenie źródeł konstrukcyjnych i porównawczych

### 3.1. Znaczenie niezależności w tym projekcie

Niezależność jest wymaganiem dotyczącym wejść i decyzji konstrukcyjnych, którego spełnienie trzeba udokumentować. Docelowy zbiór powinien dać się odtworzyć z przyjętych źródeł i reguł bez dostępu do SJP.pl, jego list różnic ani OSPS. Publikowanie zapewnień o konkretnym wydaniu wymaga wskazania zakresu weryfikacji i pozostających ograniczeń.

W ramach tego projektu nie wykorzystuj SJP.pl do pozyskiwania leksemów, form, reguł, wyjątków, list wykluczeń ani do doboru progów pod zgodność z SJP.pl. Nie używaj go także do rankingów znajomości ani klasyfikacji tematycznej.

SJP.pl wykorzystaj dopiero po zbudowaniu i zamrożeniu kandydatów, wyłącznie do benchmarku, analizy różnic i wyboru spośród wcześniej przygotowanych wariantów, z uwzględnieniem warunków użytego wydania. To ograniczenie metodologiczne projektu, a nie ogólne stwierdzenie o uprawnieniach do korzystania z SJP.pl.

OSPS pozostaje poza zakresem pozyskiwania danych, konstrukcji i ewaluacji. Nie pobieraj, nie scrapuj, nie odpytuj ani nie importuj jego danych na potrzeby tego projektu. Ta decyzja nie wymaga formułowania ocen warunków dostępu do OSPS.

Ze względu na przyjęty zakres źródeł nie używaj PoliMorfa ani innych zasobów o udokumentowanym pochodzeniu od SJP.pl jako wejść konstrukcyjnych. Dokumentacja projektu PoliMorf opisuje połączenie SGJP i Morfologika; dokumentacja Morfeusza wskazuje także udział materiału SJP.pl w tym wariancie. Podstawę tej decyzji odnotuj z odwołaniem do dokumentacji źródłowej, bez wnioskowania o jakości lub dopuszczalności innych zastosowań PoliMorfa.

W konfiguracji Morfeusza jawnie wybierz SGJP; zapisz identyfikator faktycznie załadowanego słownika. Nie polegaj wyłącznie na nazwie biblioteki lub ustawieniu domyślnym.

Pochodzenie wejść i decyzji opisuj w granicach dostępnych dowodów. Wymaganie projektowe nie stanowi zapewnienia o całej historii źródeł, narzędzi ani danych treningowych zewnętrznych modeli. Znane zależności pośrednie, w tym narzędzia użyte do anotacji korpusów i klasyfikacji tematycznej, opisz wraz z ich rolą. Obszary bez wystarczających informacji oznacz jako nieustalone. Nie wnioskuj o braku zależności wyłącznie z braku informacji o niej.

### 3.2. Zamrożenie i późniejsze poprawki

Przed benchmarkiem utrwal wersje źródeł, kodu, konfiguracji, kandydatów i ich sumy kontrolne. Moduł budujący słowniki nie może wczytywać danych benchmarku ani jego list różnic.

W tym samym przebiegu nie zmieniaj kandydatów na podstawie wyników porównania. Można wybrać jeden lub dwa spośród zamrożonych wariantów.

Benchmark może ujawnić ogólny błąd generatora, np. pominięcie klasy odmiany. Jego naprawa w następnej wersji jest dopuszczalna, jeżeli:

- ma uzasadnienie w źródłach przyjętych do konstrukcji lub w specyfikacji, niezależne od samej obecności słowa w SJP.pl;
- dotyczy ogólnej reguły, a nie dopisania słów z listy różnic;
- ma opis przyczyny, przykłady i weryfikację poprawki;
- prowadzi do nowego, jawnie oznaczonego wydania.

Nie kopiuj brakujących słów i nie dobieraj progów w celu maksymalizacji zgodności z SJP.pl. W raporcie odróżniaj pierwsze porównanie od kolejnych iteracji po poznaniu wyników.

## 4. Źródła i audyt licencji

Podane niżej informacje odsyłają do deklaracji publikowanych przez źródła i stanowią punkt wyjścia do audytu. Potwierdź warunki oraz ich zakres dla konkretnego artefaktu i wersji przed jego włączeniem do procesu. Nie utożsamiaj licencji programu, eksportu danych i całej witryny.

W rejestrze rozróżniaj wyłączenie z zakresu projektu, nieustalone warunki użycia oraz niedostępność techniczną. Statusy `ALLOWED` i `BLOCKED` opisują decyzję o wykorzystaniu w tym procesie. `BLOCKED` nie jest stwierdzeniem bezprawności korzystania ze źródła przez inne podmioty.

### 4.1. SGJP dystrybuowany z Morfeuszem 2

Użyj aktualnego oficjalnego tekstowego eksportu danych fleksyjnych SGJP przeznaczonego dla Morfeusza 2, po weryfikacji warunków konkretnej dystrybucji. Oficjalna strona licencyjna Morfeusza wskazuje BSD 2-Clause dla programu wraz z zawartymi danymi językowymi; zakres tej deklaracji dla użytych plików należy udokumentować w audycie.

To podstawowe źródło leksemów, form, interpretacji gramatycznych, oznaczeń nazw własnych oraz dostępnych kwalifikatorów. Jeżeli potrzebne są dodatkowe oficjalne pliki reguł segmentacji lub fleksji, audytuj i wersjonuj je osobno.

Deklarację odnoszącą się do eksportu stosuj wyłącznie w potwierdzonym zakresie. Warunki wykorzystania pełnej internetowej bazy SGJP ustala się odrębnie.

### 4.2. KWJP100

Użyj publicznych list frekwencyjnych oraz n-gramów KWJP100 po weryfikacji wybranego wydania. README repozytorium `ipipan/kwjp100-varia` deklaruje CC BY 4.0 dla zamieszczonych w nim zasobów. Zachowaj tę deklarację wraz z odniesieniem do wersji repozytorium.

Zachowaj, zależnie od dostępności w danym pliku:

- F, IPM, ARF, 1-DP i rangę;
- dane dla form oraz lematów, w tym POS tam, gdzie istnieje;
- rozróżnienie list uwzględniających i nieuwzględniających wielkości liter;
- częstości i inne dostępne miary w podkorpusach fiction/fact/press;
- parametry selekcji oraz próg publikacji wpisów.

**Istotne ograniczenie:** dokumentacja list KWJP podaje próg co najmniej pięciu wystąpień w całym korpusie. Potwierdź ten próg dla użytego wydania. Brak wpisu na takiej liście nie oznacza F = 0. Autorzy dokumentacji wskazują automatyczną lematyzację i anotację jako możliwe źródło błędów; uwzględnij to ograniczenie w ocenie dopasowań.

Nie zakładaj, że listy form i lematów mają tę samą strukturę albo że wszystkie miary są dostępne na każdym poziomie.

### 4.3. NKJP n-grams

Użyj przede wszystkim unigramów z 300-milionowego zrównoważonego podkorpusu NKJP jako dodatkowego źródła informacji o użyciu form.

Wskazana w rozdziale 16 strona dystrybucji zawiera deklarację „CC-BY” bez numeru wersji w tej informacji. Ustal szczegóły dla wybranego artefaktu na podstawie dystrybucji lub oficjalnej dokumentacji; nie dopisuj samodzielnie wersji licencji. Jeżeli warunki wymagane do planowanego użycia pozostają nieustalone, wstrzymaj wykorzystanie tego artefaktu w generowaniu danych i oznacz go jako BLOCKED z odpowiednią przyczyną. Audyt pozostałych źródeł może być kontynuowany.

Dokumentacja opisuje unigram jako ciąg znaków niebędących białymi znakami, sprowadzony do małych liter. Zweryfikuj rzeczywistą tokenizację, obsługę interpunkcji i strukturę plików. Nie zakładaj zgodności jeden do jednego z formami SGJP lub KWJP.

Częstość napisu w tych danych nie rozstrzyga, czy występował on jako rzeczownik pospolity, nazwa własna czy inna interpretacja. Nie określaj tego poświadczenia jako statystycznie niezależnego bez zbadania nakładania się materiału korpusów.

### 4.4. Źródła opcjonalne i granice zakresu

- NKJP ręcznie anotowany 1M: opcjonalnie, po weryfikacji konkretnego wydania i licencji.
- PL196x: opcjonalnie, po weryfikacji licencji; materiał pomocniczy/historyczny, nie samodzielna miara współczesności.
- PoliMorf: poza zakresem konstrukcji zgodnie z rozdziałem 3.1. Ewentualne późniejsze porównanie wymaga osobnego oznaczenia pochodzenia i weryfikacji warunków użycia; nie jest wymagane.
- WSJP PAN i pełna internetowa baza SGJP: nie są wejściami w podstawowym wariancie projektu. Ewentualne hurtowe pozyskanie wymaga wcześniejszego ustalenia uprawnień obejmujących zamierzone użycie; brak takiego ustalenia w tej specyfikacji nie jest oceną ogólnych warunków dostępności tych zasobów.
- Korpusy tematyczne: wyłącznie po audycie warunków pozyskania i wykorzystania.

Korpusy mogą dostarczać dowodów użycia, rankingów i kontekstów tematycznych. Nie mogą automatycznie rozszerzać początkowego zasobu leksemów poza dane SGJP przyjęte do konstrukcji w tym projekcie.

### 4.5. Rejestr źródeł

Dla każdego artefaktu zapisz przynajmniej:

```text
SOURCE_ID
SOURCE_NAME
ARTIFACT_NAME
VERSION / RELEASE_DATE / COMMIT
DOWNLOAD_URL
RETRIEVED_AT
SHA256
OWNER / AUTHORS
LICENSE_NAME
LICENSE_VERSION
LICENSE_URL
LICENSE_EVIDENCE
LICENSE_SCOPE
USED_FOR
ATTRIBUTION_REQUIRED
ATTRIBUTION_TEXT
KNOWN_DERIVATION / ANNOTATION_DEPENDENCIES
STATUS: ALLOWED | BLOCKED
BLOCK_REASON
NOTES
```

Zachowaj dostępne zawiadomienia o prawach, teksty licencji i wymagane atrybucje. Wygeneruj zestaw informacji dołączanych do wynikowych danych, odpowiedni do faktycznie użytych źródeł. Warunki udostępnienia dokumentacji projektu, kodu, bazy, eksportów i raportów ustalaj osobno, z uwzględnieniem obowiązków wynikających z użytych materiałów.

Publikacja tej specyfikacji nie nadaje uprawnień do zasobów zewnętrznych ani nie określa automatycznie licencji przyszłych wyników. Nie przypisuj projektowi wyłącznych praw do materiału pochodzącego ze źródeł zewnętrznych.

W tym procesie nieustalone warunki lub zakres wykorzystania oznaczają BLOCKED: artefakt nie bierze udziału w generowaniu danych do czasu wyjaśnienia. Nie traktuj samej możliwości przeglądania strony jako potwierdzenia uprawnień do planowanego pozyskania i udostępniania danych.

## 5. Zadanie A — struktura SGJP i przejście od segmentów do słów

Najpierw zbadaj dokładny format aktualnego eksportu. Dokumentacja Morfeusza rozróżnia segmenty, interpretacje i reguły ich łączenia. Nie zakładaj, że eksport jednej kolumny daje kompletną listę samodzielnych słów.

Udokumentuj:

- kolumny, nagłówki, kodowanie i separatory;
- identyfikatory leksemów, oznaczenia homonimii oraz tagi gramatyczne;
- klasyfikację nazw własnych;
- kwalifikatory i poziom ich przypisania: leksem, forma, interpretacja;
- warianty pisowni i wielkość liter;
- skróty, skrótowce, symbole i zapisy liczbowe;
- aglutynację, segmenty zależne i reguły łączenia;
- formy wielowyrazowe, formy z łącznikiem oraz inne znaki specjalne;
- zakres pełnych form zapisanych bezpośrednio i tych wymagających odtworzenia.

Odpowiedz na cztery pytania:

1. Które wpisy reprezentują pełne słowa nadające się do dalszej oceny growej?
2. Jakie pełne formy fleksyjne trzeba odtworzyć z segmentów lub reguł i na jakiej podstawie?
3. Które operacje są fleksją udokumentowanych leksemów, a które tworzą nowe leksemy i pozostają wyłączone?
4. Jak sprawdzić kompletność i uniknąć zarówno dopuszczenia niesamodzielnego segmentu, jak i utraty poprawnej formy?

Dla form rekonstruowanych zachowaj leksem źródłowy, składniki, identyfikator reguły i wersję generatora. Nie traktuj samego pozytywnego wyniku analizy morfologicznej jako wystarczającego dowodu dopuszczalności.

Pokaż statystyki surowych danych przed zastosowaniem filtrów. Rozróżniaj liczbę rekordów, interpretacji, leksemów i unikalnych zapisów form.

## 6. Reguły kwalifikowania i normalizacji

### 6.1. Filtruj interpretacje, a następnie agreguj formy

Jedna pisownia może mieć wiele interpretacji. Forma trafia do danego słownika, jeżeli **istnieje co najmniej jedna interpretacja spełniająca łącznie wszystkie warunki tego wariantu**.

Nie wystarczy, że każdy warunek jest spełniony przez inną interpretację. Nie odrzucaj też całego napisu wyłącznie dlatego, że jedna z interpretacji jest wykluczona.

Przykład ilustrujący zasadę: odrzucenie imienia „Róża” nie może usuwać pospolitego rzeczownika „róża”. Analogicznie postępuj z kwalifikatorami, skrótami i homonimią. Przykłady raportowane jako wyniki audytu muszą pochodzić z rzeczywiście przebadanej wersji danych.

### 6.2. Polityka znaków i długości

Oddziel zachowanie oryginalnego zapisu od klucza używanego przez grę:

- zachowuj oryginalną formę, lemat i wielkość liter;
- stosuj jawną normalizację Unicode, domyślnie NFC;
- oceniaj status nazwy własnej i wymagania pisowni przed sprowadzeniem do klucza bez rozróżniania wielkości liter;
- zachowuj polskie znaki diakrytyczne;
- nie twórz słów przez usuwanie łączników, spacji, apostrofów czy innych znaków;
- nie traktuj kropki wymaganej w skrócie jako zbędnego ozdobnika.

Alfabet gry, reprezentację blanków, minimalną i maksymalną długość oraz przyjętą politykę ortograficzną zapisz jako konfigurację. Ustal je na podstawie dostępnej specyfikacji Literaki Lounge; jeśli jej brakuje, wskaż brak w raporcie, zamiast przedstawiać domysł jako obowiązującą regułę.

Nie usuwaj potrzebnych danych z bazy źródłowej tylko dlatego, że dany napis nie mieści się w docelowej planszy. Ograniczenia gry mogą być filtrami eksportu.

### 6.3. Kategorie wymagające jawnych decyzji

Wykluczaj interpretacje będące nazwami własnymi, skrótami, symbolami, zapisami cyfrowymi, elementami technicznymi lub niedopuszczalnymi segmentami. Nie usuwaj automatycznie zapisanych słownie liczebników, takich jak „dwa” i „sto”.

Nie stosuj jednego mechanicznego filtra do skrótów, skrótowców oraz zleksykalizowanych wyrazów o takim pochodzeniu. Najpierw ustal, jak reprezentuje je źródło, i pokaż skutki proponowanej reguły.

Brak jednoznacznej klasyfikacji oznacz jako przypadek nierozstrzygnięty w audycie. Nie ukrywaj go pod etykietą „inne”. Nie rozszerzaj reguł samodzielnie o oceny obyczajowe, stylistyczne lub intuicyjną „dziwność” słowa.

## 7. Zadanie B — kandydaci na duże słowniki

Zbuduj w późniejszym etapie następującą rodzinę kandydatów. Przed generowaniem końcowych list określ konfigurację każdego wariantu.

Prefiks `LL-PL-` oznacza wariant projektu Literaki Lounge dla języka polskiego. Jest roboczym identyfikatorem technicznym. W dalszej treści dopuszcza się skróty BROAD, STANDARD i ATTESTED wyłącznie w znaczeniu z poniższej tabeli.

| Identyfikator | Znaczenie w projekcie |
| --- | --- |
| `LL-PL-BROAD` | szeroki zbiór z udokumentowanych leksemów i ich dopuszczalnej fleksji |
| `LL-PL-STANDARD` | podzbiór BROAD według przyjętej polityki współczesności |
| `LL-PL-ATTESTED-LEXEME` | wariant wymagający poświadczenia leksemu |
| `LL-PL-ATTESTED-FORM` | eksperymentalny wariant wymagający poświadczenia konkretnej formy |

Określenie STANDARD nazywa politykę tego projektu. Nie oznacza instytucjonalnego zatwierdzenia, certyfikacji ani ustanowienia normy językowej.

### 7.1. LL-PL-BROAD

Możliwie szeroki słownik oparty na udokumentowanych leksemach SGJP oraz ich dopuszczalnej fleksji, z filtrami technicznymi i growymi z rozdziału 6.

Nie wykluczaj automatycznie archaizmów, regionalizmów, potocyzmów, wulgaryzmów, terminów naukowych i fachowych ani słów rzadkich. Warianty historyczne zachowuj tylko w zakresie zgodnym z jawną polityką BROAD i ograniczeniami znaków gry; nie przyjmuj dowolnej historycznej pisowni rozpoznawanej przez analizator.

Nie wymagaj potwierdzenia korpusowego.

### 7.2. LL-PL-STANDARD

Podzbiór LL-PL-BROAD realizujący uzgodniony zakres współczesnej polszczyzny z rozdziału 2.3. Zachowaj pełną dopuszczalną fleksję zakwalifikowanych leksemów.

Przed zastosowaniem kwalifikatorów pokaż:

- ich rzeczywistą listę i znaczenie;
- liczbę objętych interpretacji, form i leksemów;
- nakładanie się kategorii;
- przykłady interpretacji odrzuconych i form, które mimo tego pozostają dzięki innej poprawnej interpretacji;
- przypadki, w których kwalifikator nie pozwala na pewną decyzję.

Nie przedstawiaj STANDARD jako doskonałego rozpoznania współczesności. Udokumentuj ograniczenia pokrycia kwalifikatorami.

### 7.3. LL-PL-ATTESTED-LEXEME

Kandydat na duży słownik ograniczony do leksemów z potwierdzeniem użycia. Zaczyna od jawnie wskazanego BROAD lub STANDARD. Dopuszcza wszystkie formy tego leksemu przyjęte w wybranej bazie, bez osobnego wymagania poświadczenia każdej z nich.

Poświadczenie musi mieć określony poziom pewności przypisania do leksemu. Sam fakt występowania wspólnego napisu nie może automatycznie potwierdzać wszystkich jego homonimów. Zachowaj informację, czy potwierdzenie pochodzi z dopasowanego lematu i POS, jednoznacznej formy czy dopasowania niejednoznacznego.

Przetestuj kilka kryteriów siły poświadczenia; słabe dopasowania przedstaw osobno. Nie utożsamiaj poświadczenia samego lematu jako napisu z rozpoznaniem właściwego leksemu.

### 7.4. LL-PL-ATTESTED-FORM

Eksperymentalny podzbiór BROAD lub STANDARD wymagający potwierdzenia konkretnej formy. Może zawierać niepełne rodziny fleksyjne. Raportuj tę właściwość jawnie; nie przedstawiaj jej jako błędu form niepoświadczonych.

Wariant jest przydatny do porównań i budowy słowników znajomości. Nie traktuj go domyślnie jako preferowanego zamiennika pełnego dużego słownika.

### 7.5. Eksperymenty z progami

Dla obu wariantów ATTESTED rozważ, stosownie do dostępnego poziomu danych:

- obecność w opublikowanej liście KWJP lub NKJP;
- próg F, ARF lub 1-DP;
- obecność w co najmniej dwóch podkorpusach KWJP;
- potwierdzenie w obu zasobach.

„Obecność w KWJP” oznacza obecność w użytej liście z jej progiem publikacji, a nie dowolne pojedyncze wystąpienie w całym korpusie.

Dobieraj punkty cięcia na podstawie rozkładów i próbek jakościowych, przed benchmarkiem SJP.pl. Porównaj wpływ progów na liczebność, kompletność fleksji i strukturę słownictwa. Nie twórz bez uzasadnienia pełnego iloczynu wszystkich kombinacji parametrów.

## 8. Zadanie C — wspólny model danych

Zaprojektuj bazę główną jako model leksemów, form, interpretacji, poświadczeń i decyzji. Końcowe pliki słów mają być eksportami z tej bazy, nie jedyną postacią wiedzy projektu.

Proponowane jednostki logiczne:

| Jednostka | Minimalna zawartość |
| --- | --- |
| SourceArtifact | wersja źródła, adres, checksum, licencja i rola |
| Lexeme | identyfikator źródłowy, lemat, oznaczenia homonimii, odniesienie do wydania |
| SurfaceForm | zapis oryginalny, zapis znormalizowany, klucz growy, długość |
| Interpretation | forma, leksem, POS, morfologia, kwalifikatory, status nazwy własnej |
| Derivation | forma odtworzona, składniki, reguła fleksyjna, wersja generatora |
| CorpusEvidence | zasób, jednostka, rodzaj listy, miary, podkorpus, status dostępności |
| EvidenceLink | powiązanie poświadczenia z formą lub leksemem, metoda i niejednoznaczność |
| VariantDecision | wariant, interpretacja/forma, wynik, przyczyny i wersja reguł |
| KnowledgeScore | model powszechności, poziom jednostki, wynik, wersja konfiguracji |
| TopicScore | leksem, temat, wynik, metoda, dowody i wersja |
| BuildManifest | źródła, konfiguracja, kod, seed, identyfikatory i sumy wyników |

Nie wymagaj konkretnego silnika bazy bez uzasadnienia. Wybierz prostą reprezentację odpowiednią do rzeczywistych rozmiarów i relacji.

### 8.1. Łączenie źródeł

Nie usuwaj oznaczeń homonimii z kluczy leksemów. Przygotuj jawne mapowanie konwencji lematów i tagów SGJP/KWJP. Sam napis lematu nie gwarantuje tożsamości jednostki.

Nie przypisuj całej częstości jednej formy każdemu pasującemu leksemowi. Jeżeli nie da się jej rozdzielić, zachowaj ją na poziomie formy lub jako niejednoznaczne poświadczenie. Nie twórz sztucznej precyzji.

Nie sumuj bez uzasadnienia ARF, 1-DP ani rang. Nie sumuj częstości całego korpusu z częstościami jego podkorpusów. Dla każdej agregacji określ jednostkę, mianownik i sposób obsługi nakładania się danych.

### 8.2. Braki danych

Wartość liczbowa i status dostępności są odrębnymi polami. Rozróżniaj co najmniej:

- `OBSERVED`: opublikowana wartość, również rzeczywiste zero, jeśli źródło je podaje;
- `ABSENT_OR_BELOW_PUBLICATION_THRESHOLD`: brak wpisu na liście z dolnym progiem publikacji, gdy jednostka mieści się w jej zakresie;
- `NOT_IN_PUBLISHED_LIST`: brak wpisu przy innym lub nieustalonym mechanizmie selekcji;
- `UNMATCHED`: nie udało się wiarygodnie połączyć jednostek źródeł;
- `NOT_APPLICABLE`: miara nie dotyczy danej jednostki;
- `UNAVAILABLE`: danych nie pozyskano lub źródło jest zablokowane.

Brak wpisu może wynikać również z tokenizacji, zakresu listy lub błędu anotacji. Nie deklaruj, że znasz rzeczywistą częstość 0–4, jeżeli nie zapewniono porównywalności jednostki.

Nie zamieniaj automatycznie braków na zera. W rankingach opisz sposób postępowania z brakami i przeprowadź ocenę wrażliwości na przyjętą metodę.

## 9. Zadanie D — słowniki codziennej polszczyzny

Celem jest użyteczny model zasobu słów, a nie pomiar rzeczywistej kompetencji konkretnej osoby. Liczby leksemów nie przekładają się automatycznie na wiek, wykształcenie ani poziom językowy.

Buduj słowniki na wybranej, wersjonowanej bazie dopuszczalności. Zbadaj trzy modele:

### 9.1. LEXEME

Uszereguj leksemy według powszechności. Dla wybranego leksemu bot zna jego formy dopuszczone w bazie. Rozróżniaj leksem od samego napisu lematu i zachowuj ograniczenia jakości mapowania korpusowego.

Zbadaj jako punkty startowe top 5k, 10k, 20k, 40k i 80k leksemów. Dostosuj zakres do liczby dostępnych, wiarygodnie ocenionych jednostek. Dla każdego progu raportuj zarówno liczbę leksemów, jak i liczbę unikalnych form.

### 9.2. FORM

Uszereguj konkretne formy. Model ma symulować bardzo ograniczony zasób wiedzy, który nie obejmuje automatycznie całej odmiany znanych słów. Wyraźnie raportuj niepełność rodzin fleksyjnych.

### 9.3. HYBRID

Połącz powszechność leksemu z powszechnością jego konkretnych form. Opisz, które formy wynikają z poznania leksemu, a które wymagają dodatkowego progu. Nie wprowadzaj ukrytych wyjątków służących poprawianiu wyników gry.

### 9.4. COMMONNESS i jego ocena

Zaproponuj funkcję lub niewielką rodzinę funkcji COMMONNESS wykorzystujących:

- częstość i ARF;
- 1-DP;
- obecność w różnych gatunkach KWJP;
- pomocnicze potwierdzenie NKJP;
- poziom pewności dopasowania i dostępność danych.

Preferuj percentyle, rangi i transformacje logarytmiczne zamiast sumowania surowych miar o nieporównywalnej skali. Uzasadnij wagi i sprawdź ich wrażliwość. Nie traktuj skorelowanych miar jako niezależnych dowodów. Podaj osobno wyniki dla lematów/leksemów i form.

Częstość oraz dyspersja są wskaźnikami użycia, nie bezpośrednim dowodem powszechnej znajomości. Opisz gatunki, okresy i odmiany języka reprezentowane przez korpusy oraz możliwe braki pokrycia codziennej komunikacji.

Przygotuj próbki do przeglądu jakościowego dla każdego modelu i poziomu: krótkie i długie słowa, różne części mowy, pozycje blisko progów, przypadki rozbieżności miar oraz słowa bez części danych. Wielkość próbek i sposób losowania ustal jawnie.

Oddziel przykłady wybrane do ilustracji od losowej próby oceny. Bez przeglądu nie deklaruj, że poziom odpowiada „przeciętnemu człowiekowi”.

### 9.5. Poziomy i trwałość wiedzy

Rozważ `vocabulary_level = 0.0 ... 1.0` oraz eksport kilku poziomów statycznych.

Dla tej samej osobowości, konfiguracji i wydania bazy wyższy poziom powinien rozszerzać zasób niższego poziomu. Nie musi to obowiązywać przy porównaniu dwóch różnych osobowości lub wydań źródeł.

Losowy komponent wiedzy może pozwalać znać część słów rzadszych mimo nieznajomości niektórych częstszych, ale:

- losowanie musi być odtwarzalne;
- zasób wiedzy jest trwały dla danej konfiguracji bota;
- nie losuj znajomości każdego słowa od nowa przy każdym ruchu;
- zachowaj zagnieżdżenie poziomów przy stałym seedzie;
- utrwal seed, wersję modelu i sposób przypisania słów.

## 10. Zadanie E — słowniki tematyczne

Buduj podzbiory wybranego słownika dopuszczalności, np. dla kulinariów, żywności, marynistyki, matematyki, sportu, medycyny, botaniki, muzyki, informatyki i kolei.

Klasyfikuj przede wszystkim leksemy, następnie dołączaj ich dopuszczalne formy. Zasób tematyczny może być dodatkiem do podstawowej wiedzy bota. Po scaleniu nadal musi być podzbiorem słownika obowiązującego przy stole.

Przetestuj na ograniczonym pilotażu trzy metody:

1. Słowa zalążkowe i ich sąsiedztwo w n-gramach KWJP.
2. Porównanie częstości w korpusie dziedzinowym przyjętym po weryfikacji źródła z korpusem odniesienia, z miarą keyness lub log-odds.
3. Klasyfikator semantyczny lub LLM jako pomocniczy scorer istniejących leksemów.

Słowa zalążkowe pochodzą z bazy przyjętej w projekcie lub jawnie podanej listy użytkownika; same nie rozszerzają dopuszczalności. LLM nie dostarcza nowych słów ani poprawnych form i nie rozstrzyga o ich dopuszczeniu do gry. Klasyfikuje wyłącznie istniejące jednostki.

Jeden leksem może należeć do wielu tematów z różnymi wynikami. Zachowaj model, prompt, konfigurację, wynik i niepewność klasyfikacji LLM; korzystaj z zapisanych wyników dla odtwarzalności. Uwzględnij wieloznaczność: etykieta tematyczna nie oznacza, że każde użycie słowa dotyczy danego tematu.

Przed pozyskaniem korpusu dziedzinowego sprawdź warunki jego użycia. Preferencją projektu są CC0, materiały o potwierdzonym statusie domeny publicznej, CC BY oraz materiały własne/użytkownika z odpowiednimi uprawnieniami. Materiały CC BY-SA utrzymuj osobno do czasu ustalenia obowiązków dla konkretnego sposobu wykorzystania. Do procesu włączaj wyłącznie źródła, dla których udokumentowano warunki planowanego pozyskania i udostępniania danych.

Jeżeli nie ma dostępnego korpusu spełniającego warunki metody 2, oznacz metodę jako zablokowaną lub odroczoną. Materiał zastępczy wymaga tej samej weryfikacji źródła. Raportuj jakość próbek tematycznych, nie tylko liczbę przypisanych etykiet.

## 11. Zadanie F — benchmark SJP.pl

Uruchom dopiero po ukończeniu i zamrożeniu kandydatów. Pobierz oficjalną listę grową SJP.pl, potwierdzając aktualną licencję konkretnego wydania oraz warunki przechowywania i publikowania wyników. Zapisz źródło, datę, wersję i checksum.

Nie korzystaj z OSPS. Nie modyfikuj kandydatów w tym przebiegu.

### 11.1. Porównywalność

Porównuj zbiory unikalnych kluczy growych po zastosowaniu tej samej jawnej polityki znaków, wielkości liter i długości. Raportuj liczebności zarówno przed ograniczeniami wspólnego zakresu, jak i po nich.

Odróżniaj różnice leksykalne od różnic wynikających z formatu, normalizacji, długości lub polityki pisowni. Nie usuwaj znaków w celu sztucznego zwiększenia zgodności.

### 11.2. Metryki

Dla każdego kandydata A policz:

- `|A|`, `|SJP|`, `|A ∩ SJP|`, `|A − SJP|`, `|SJP − A|`;
- Jaccard: `|A ∩ SJP| / |A ∪ SJP|`;
- pokrycie SJP: `|A ∩ SJP| / |SJP|`;
- udział form A obecnych w SJP: `|A ∩ SJP| / |A|`.

Podaj mianowniki i obsługę pustych zbiorów. Metryki opisują relacje między badanymi zbiorami. Nie interpretuj ich samodzielnie jako miary poprawności językowej lub ogólnej jakości. W tym badaniu lista SJP.pl pełni rolę punktu odniesienia; różnica między zbiorami wymaga wyjaśnienia z uwzględnieniem ich zakresu, wersji i reguł kwalifikowania.

Nie nazywaj `A − SJP` ani `SJP − A` błędami.

Przy publikowaniu porównania podawaj daty i wersje obu zbiorów, metodę normalizacji, zakres długości, definicje metryk oraz ograniczenia analizy. Oddziel ustalenia o konkretnych rekordach od ocen całych zasobów. Nie wyprowadzaj ogólnych twierdzeń o autorach, jakości lub przewadze jednego słownika wyłącznie z liczby różnic. Przykłady i listy różnic udostępniaj w zakresie wynikającym ze zweryfikowanych warunków użytych materiałów.

### 11.3. Analiza różnic

Dla `A − SJP` pokaż dostępne miary KWJP i NKJP, lematy, POS, kwalifikatory, długość oraz pochodzenie i przyczynę przyjęcia. Wyróżnij najczęstsze i najbardziej rozpowszechnione słowa nieobecne w SJP.

Dla `SJP − A` sprawdź dostępne poświadczenia korpusowe i możliwe przyczyny braku: brak leksemu w źródle, filtr polityki, wariant pisowni, brak odtworzenia formy, niejednoznaczne dopasowanie lub przyczyna nieustalona. Hipotezy oznaczaj jako hipotezy. Analiza tej grupy nie może stać się kanałem dopisywania słów do generatora.

Podaj statystyki dla długości 2, 3, 4, 5, 6, 7 i 8+, z dodatkowymi przedziałami, jeżeli wymagają tego limity gry. Formy poza zakresem gry raportuj osobno.

Zbadaj rodziny fleksyjne, grupy anagramów, rozkład częstości form dodanych i utraconych oraz kompletność odmiany. Poświadczeń niejednoznacznych nie przedstawiaj jako rozstrzygniętych.

### 11.4. Wpływ na grę

W późniejszym etapie porównuj możliwości układania słów na wspólnym zestawie stojaków, z tym samym rozkładem płytek, zasadami blanków i seedem. Raportuj m.in. liczbę dostępnych słów, brak dostępnych słów oraz możliwości wykorzystania wszystkich siedmiu płytek.

Jeżeli dostępny jest silnik i reprezentatywne pozycje planszy, porównaj także ruchy dopuszczalne według reguł gry i punktację w tych samych pozycjach. Sam test anagramów ze stojaka nie mierzy całego wpływu na rozgrywkę. Opisz pochodzenie pozycji i możliwe uprzedzenie próby, np. gdy pochodzą z partii rozegranych na SJP.

Nie wymyślaj wyników symulacji. Jeśli infrastruktura nie jest dostępna, dostarcz specyfikację eksperymentu i oznacz pomiar jako niewykonany.

## 12. Zadanie G — wybór docelowych słowników

Porównaj kandydatów według:

- udokumentowania pochodzenia wejść i zgodności decyzji z zasadami rozdzielenia źródeł z rozdziału 3;
- jasności licencji i obowiązków atrybucji;
- jakości oraz aktualności danych;
- pokrycia współczesnej polszczyzny;
- potencjalnych artefaktów i nierozstrzygniętych przypadków;
- kompletności dopuszczalnej fleksji;
- łatwości wyjaśnienia decyzji i aktualizacji;
- konsekwencji dla gry;
- wyników benchmarku SJP.pl.

Nie wybieraj wariantu docelowego wyłącznie przez największą liczebność lub podobieństwo do SJP.pl. Pokaż tabelę kompromisów w odniesieniu do zastosowań Literaki Lounge. Możliwym wynikiem jest pozostawienie dwóch wariantów: szerokiego i współczesnego STANDARD.

Przedstaw rekomendację wraz z dowodami i ograniczeniami. Samo przygotowanie danych nie oznacza automatycznej zmiany słownika w działającym Literaki Lounge.

## 13. Odtwarzalność i wyjaśnialność

Każde wydanie ma umożliwiać odtworzenie wyników z tych samych wejść i konfiguracji:

- dokładne wersje źródeł, licencji i kodu;
- konfiguracja filtrów, progów, normalizacji i eksportu;
- seedy oraz zapisane wyniki klasyfikacji niedeterministycznej;
- deterministyczna deduplikacja i kolejność eksportu;
- sumy kontrolne wejść i wyników;
- dziennik zmian względem poprzedniego wydania.

Dla zapytania o słowo system powinien potrafić wyjaśnić, jakie interpretacje znaleziono, które przyjęto/odrzucono, z jakich powodów i do których wariantów forma należy. Brak słowa w źródle odróżniaj od odrzucenia przez filtr.

Zachowuj źródłowe dane i archiwizuj materiały w zakresie dozwolonym przez ich licencje. Nie wymagaj redystrybucji surowych wejść, jeśli warunki tego nie dopuszczają.

## 14. Kryteria jakości i zakończenia etapów

Dla każdego filtra raportuj wpływ zastosowanego samodzielnie, wpływ w ustalonej kolejności oraz wynik łączny. Rozróżniaj usunięte interpretacje i faktycznie utracone unikalne formy; nie sumuj bezkrytycznie nakładających się kategorii.

Przygotuj kontrole najważniejszych własności:

- STANDARD jest podzbiorem BROAD;
- wariant ATTESTED jest podzbiorem wskazanej bazy;
- słowniki znajomości i tematyczne nie dopuszczają form spoza przypisanej bazy;
- zaakceptowana forma ma co najmniej jedną interpretację spełniającą wszystkie warunki;
- homonimia i nazwy własne nie powodują usunięcia poprawnej interpretacji pospolitej;
- normalizacja nie tworzy wyrazów przez usuwanie znaków;
- brak korpusowy nie został bezpodstawnie zamieniony na zero;
- jedna częstość nie została wielokrotnie doliczona różnym interpretacjom;
- odtworzone formy mają podstawę i ślad reguły;
- generowanie nie korzysta z wejść benchmarku;
- poziomy wiedzy są odtwarzalne i zagnieżdżone zgodnie z rozdziałem 9.5.

Próbki jakościowe powinny obejmować m.in. krótkie słowa, homonimy, formy historyczne, słowa fachowe, nazwy własne pokrywające się z pospolitymi oraz formy rekonstruowane. Nie oceniaj jakości wyłącznie przez podobieństwo do SJP.pl.

Przy każdym wyniku rozróżniaj: zmierzone dane, wynik zastosowanej reguły, hipotezę, rekomendację i niewykonany eksperyment. Nie przedstawiaj samych planów jako gotowego generatora.

## 15. Pierwszy etap — wykonaj teraz tylko audyt

Wykonaj:

1. Audyt oficjalnych plików źródłowych SGJP dla Morfeusza oraz ewentualnych niezbędnych reguł.
2. Audyt list KWJP100 i unigramów NKJP: licencje, dostępność, wersje, format, tokenizacja, progi publikacji i reprezentowane jednostki.
3. Rejestr dokładnych źródeł i sum kontrolnych; status ALLOWED/BLOCKED z uzasadnieniem.
4. Analizę struktury plików pozyskanych w zakresie ustalonych uprawnień, bez przyjmowania założeń na podstawie nazw kolumn.
5. Statystyki SGJP: rekordy, interpretacje, leksemy, unikalne formy, POS, kwalifikatory, nazwy własne, długości i znaki.
6. Analizę rozróżnienia pełnych słów i segmentów oraz plan uzyskania kompletnej fleksji bez produktywnego tworzenia nowych leksemów.
7. Projekt filtrów BROAD i STANDARD, z rzeczywistymi przykładami i policzonym wpływem filtrów, jeśli dane pozwalają go już ustalić.
8. Pilotaż dopasowania źródeł: przykłady zgodnych, niejednoznacznych i niedopasowanych lematów/form oraz zasady obsługi braków.
9. Projekt modelu danych i manifestu odtwarzalności.
10. Listę ograniczeń, blokad i zaleceń do implementacji pierwszego generatora, zgodnych z wymaganiami tej specyfikacji.

Na tym etapie dozwolone są skrypty audytowe i próbne obliczenia niezbędne do uzyskania statystyk. Nie przedstawiaj ich jako ukończonych słowników produkcyjnych.

**Nie pobieraj jeszcze SJP.pl, nie uruchamiaj benchmarku ani nie korzystaj z OSPS.**

Zakończ etap raportem Markdown zawierającym:

- krótką ocenę wykonalności;
- tabelę źródeł, wersji, licencji i statusów;
- opis formatów i ograniczeń danych;
- rzeczywiście obliczone statystyki z definicją jednostek;
- tabelę filtrów z uzasadnieniami, przykładami i skutkami;
- plan obsługi fleksji, segmentów i homonimii;
- projekt połączenia z korpusami, z obsługą progów i braków;
- projekt bazy i odtwarzalnego procesu;
- nierozstrzygnięte kwestie wymagające dowodów lub decyzji;
- konkretny zakres następnego etapu.

Etap jest zakończony, gdy każda pozycja ma wynik albo jawny status niewykonania z konkretną przyczyną i opisem wpływu na dalsze prace. Nie uznawaj zablokowanego źródła za użyte i nie zastępuj brakujących statystyk szacunkami podanymi jako pomiar.

Nie pytaj ponownie o zasady już uzgodnione w rozdziale 2. Pytania ogranicz do rzeczywistych nowych niejednoznaczności ujawnionych przez dane.

## 16. Oficjalne punkty startowe do weryfikacji

Poniższe odnośniki prowadzą do dokumentacji i dystrybucji; przed użyciem ustal właściwe wersje artefaktów:

- [Morfeusz 2 — pobieranie](https://morfeusz.sgjp.pl/download/)
- [Morfeusz 2 — licencja programu i danych](https://morfeusz.sgjp.pl/doc/license/en)
- [Morfeusz 2 — dokumentacja techniczna i użytkowa](https://download.sgjp.pl/morfeusz/Morfeusz2.pdf)
- [KWJP100 — oficjalne repozytorium danych](https://github.com/ipipan/kwjp100-varia)
- [KWJP — dokumentacja list frekwencyjnych](https://kwjp.pl/lists/doc/about/)
- [KWJP — przeglądarka list](https://kwjp.pl/lists/)
- [NKJP — n-gramy z korpusu zrównoważonego](https://zil.ipipan.waw.pl/NKJPNGrams)
- [PoliMorf — opis pochodzenia i licencji zasobu](https://zil.ipipan.waw.pl/PoliMorf)

## 17. Historia zmian

### 17.1. Wersja 3 — redakcja do publikacji

1. Określono dokument jako roboczą specyfikację wymagań, oddzieloną od przyszłych raportów z audytu i wyników badań.
2. Doprecyzowano niezależność jako wymaganie dotyczące wejść i decyzji konstrukcyjnych, z obowiązkiem udokumentowania zakresu weryfikacji.
3. Wyraźnie oddzielono ograniczenia projektowe od ocen prawnych i ocen jakości zasobów zewnętrznych.
4. Wprowadzono identyfikatory `LL-PL-BROAD`, `LL-PL-STANDARD`, `LL-PL-ATTESTED-LEXEME` i `LL-PL-ATTESTED-FORM`.
5. Wyjaśniono rolę nazw instytucji i zasobów oraz projektowe znaczenie etykiety STANDARD.
6. Informacje licencyjne przedstawiono jako deklaracje źródeł wymagające weryfikacji dla konkretnych artefaktów; doprecyzowano znaczenie statusów ALLOWED/BLOCKED.
7. Zachowano neutralny opis porównania zbiorów oraz wymóg wyjaśniania różnic bez automatycznego uznawania ich za błędy.
8. Dodano informację o opracowaniu dokumentu z pomocą AI.
9. Zachowano wymagania techniczne i decyzje przyjęte w wersji 2, w tym pełną fleksję, zakres STANDARD, granicę słowotwórstwa i pierwszy etap ograniczony do audytu.

### 17.2. Wersja 2 — przegląd techniczny względem wersji 1

1. Rozdzielono dopuszczalność słów od modelowania znajomości słownictwa.
2. Uzgodniono pełną poprawną fleksję bez obowiązku korpusowego poświadczenia każdej formy.
3. Rozdzielono ATTESTED-LEXEME i eksperymentalny ATTESTED-FORM.
4. Uściślono STANDARD: pozostają potocyzmy, wulgaryzmy, regionalizmy i terminologia fachowa; ograniczenia dotyczą przede wszystkim jednoznacznej przestarzałości i historycznej pisowni.
5. Wyłączono produktywne tworzenie nieudokumentowanych leksemów z początkowych wariantów, także BROAD.
6. Dodano obsługę segmentów Morfeusza, rekonstrukcji form, homonimii i kwalifikowania na poziomie interpretacji.
7. Uwzględniono próg publikacji KWJP, różnice tokenizacji oraz niejednoznaczność poświadczeń i braków danych.
8. Rozwinięto model danych i zabezpieczenia przed wielokrotnym liczeniem częstości.
9. Dodano jakościową ocenę poziomów słowników oraz trwałość i zagnieżdżenie wiedzy botów.
10. Dopuszczono udokumentowane poprawki ogólnych błędów generatora w kolejnych wydaniach, bez przejmowania list słów z SJP.pl.
11. Doprecyzowano odtwarzalność, wyjaśnienia decyzji, warunki porównywalności benchmarku i kryteria zakończenia etapów.
12. Zachowano bieżący zakres: pierwszy etap kończy się audytem i projektem generatora, przed użyciem SJP.pl.
