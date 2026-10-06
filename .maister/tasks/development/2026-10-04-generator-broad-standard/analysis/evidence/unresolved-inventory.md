## TL;DR
Pełny, odtwarzalny inwentarz niewiadomych obejmuje 7 458 520 rekordów SGJP i 125 362 kandydatów konstrukcji (17 360 294 analiz na wariant). Polityka v21 nie została zmieniona.
Słowa zależne od merytorycznej niewiadomej: BROAD 46 802, STANDARD 46 406; unia bez podwójnego liczenia: 46 877. Ponad 83% tej liczby to przesiew `-anin/-anka`, a 16% to `adjp`.
Formalna warstwa semantyki złożonych kwalifikatorów obejmuje dodatkowo 635 937 słów BROAD i 258 653 słowa STANDARD. Wszystkie etykiety mają już zatwierdzone warunki.
Bez nowych źródeł decyzją właściciela można rozstrzygnąć: adjp, by, przykłady RJP, warstwę kwalifikatorów i część frag. Przesiewu mieszkańców nie da się rozstrzygnąć per słowo; możliwa jest tylko decyzja klasowa.
Dwa pełne przebiegi dały identyczny wynik (SHA 13497395…d451), a bazy pozostały niezmienione. Nowy build measure nie skończył etapu decisions, więc wynik pochodzi z symulacji `assess_diagnostic`.

## Key Decisions
- **Źródło liczb.** Liczby pochodzą z symulacji tej samej ścieżki co `materialize_assessments`, czyli `assess_diagnostic` z przeglądami użyć `checked_use_reviews`. Symulację uruchomiono na pełnym G2 i kandydatach G5. Nic nie zapisano i nie aktywowano żadnych nowych dowodów.
- **Placeholdery.** Dwa stałe placeholdery (`linguistic-policy-not-active-v1`, `game-metadata-not-complete-v1`) są w każdej analizie. Liczymy je osobno jako „warstwę aktywacji”, a nie jako kategorię informacji.
- **Kategorie danych.** Kategorie danych (frag, adjp, mieszkańcy, by, pozostałość użyć) to populacje do decyzji, a nie nowe klasyfikatory polityki. W kodzie v21 jedyną niewiadomą merytoryczną poza placeholderami jest `semantic-use-qualification-pending-v1`. Pozostałe kategorie wynikają z macierzy speców §6 i z pozycji pending w `coverage.json`.
- **Agregacja słów** jest zgodna z `aggregate`:
  - słowo, którego wszystkie analizy mają niezależną odmowę, nie jest zależne;
  - słowo z analizą wolną od kategorii merytorycznych też nie jest zależne;
  - słowo jest zależne od X, gdy żadna analiza nie jest wolna, a któraś nieodrzucona analiza ma X;
  - „jedyna” oznacza, że X jest jedyną kategorią merytoryczną słowa.
- **Wszystkie opcje są wyłącznie materiałem do decyzji.** Niczego nie wdrożono.

## Open Questions / Risks
- **Populacja mieszkańców jest niekompletna i zanieczyszczona.**
  - Przesiew obejmuje tylko `-anin` (m1) i odpowiadające mu `-anka` (f). Pomija `-ak`, `-czyk`, `-ec`, `-ita` itd. (np. warszawiak, bawarczyk), więc 39 095 to dolna granica.
  - Jednocześnie przesiew zawiera słowa niebędące mieszkańcami: chrześcijanin, mieszczanin, ziemianin, dworzanin, parafianin, poganin, luteranin, mahometanin, purytanin.
  - Pięciopolowy eksport nie zawiera relacji mieszkaniec–miejscowość. Wcześniejszy przegląd ustalił, że brak odsyłacza nie dowodzi braku znaczenia mieszkańca.
- **Macierz klas i ortografii nie ma per-słownej populacji.** `full_category_and_orthography_matrix` i `documented_game_conditions_without_sjp_editorial_source_policy` mają w `coverage.json` status pending. Nie mają jednak kodu ani danych, które wskazywałyby konkretne analizy. Inwentarz pokazuje tylko rozkład klas analiz „czystych”, które zależą od tej decyzji.
- **Build measure nie został porównany.** Build `data/work/measure-20261005-223725-a` (PID 95197) o 01:33 miał etapy constructions/decisions/links/reports w stanie pending. Nie przerywano go. Porównanie z jego `reports/unresolved.json` pozostaje do wykonania po zakończeniu.
- **KWJP to tylko wskazówka.** Obecność słowa w KWJP (orth) nie dowodzi poprawności ani zapisu małą literą; listy `orth_lc` gubią wielkość liter. Liczby KWJP podano tylko jako wskazówkę do ewentualnych przeglądów.

## Tabela kategorii

Kolumny „słowa zal.” podają słowa z wynikiem zależnym od kategorii, a w nawiasie słowa, dla których jest to jedyna kategoria. Analizy i rekordy kompaktowe są liczone tylko wśród nieodrzuconych.

| Kategoria | Status | Kompakt. B/S | Analizy B/S | Słowa zal. BROAD | Słowa zal. STANDARD | Bez nowych źródeł? |
|---|---|---|---|---|---|---|
| R1 przesiew mieszkańców `-anin/-anka` | unresolved; brak dowodu klasy | 42 863 / 42 675 | 58 846 / 58 578 | 39 095 (39 095) | 38 997 (38 997) | tylko decyzja klasowa |
| R2 przykłady mieszkańców z RJP §8.1.2 pkt 3 | konflikt SGJP (mała) z RJP 2026 (wielka) | 83 / 83 | 116 / 116 | 70 (70) | 70 (70) | tak |
| A adjp (`po polsku`) | unresolved: samodzielność segmentu | 8 306 / 8 015 | 8 306 / 8 015 | 7 556 (7 556) | 7 269 (7 269) | tak (reguła gry) |
| F frag | unresolved: brak znaczenia lub użycia | 106 / 85 | 112 / 90 | 67 (62) | 57 (53) | częściowo |
| B `-by` spoza listy RJP 4.5 | unresolved: status jednego wyrazu | 4 / 3 | 4 / 3 | 4 (4) | 3 (3) | tak |
| U pozostałość udokumentowanych użyć | unresolved: inne znaczenia ID | 19 / 18 | 22 / 21 | 15 (10) | 14 (10) | częściowo |
| P `semantic-use-qualification-pending-v1` | unresolved (kod v21) | 6 / 5 | 6 / 5 | 4 (0) | 3 (0) | częściowo |
| kod: contraction-scope, whole-unit, source-name-labels, proper-name-class, inne | brak nieodrzuconych | 0 | 0 | 0 | 0 | — |
| **Suma merytoryczna (unia kategorii)** | | | | **46 802** | **46 406** | unia B∪S **46 877**, B∩S 46 331 |
| Q formalna semantyka złożonych kwalifikatorów | pending w `coverage.json` | 884 768 / 359 949 | 2 061 404 / 821 360 | 635 937 | 258 653 | tak (zamknięcie pending) |
| Warstwa aktywacji (2 placeholdery) | unresolved w każdej analizie | — | 12 208 543 / 10 956 624 | 3 508 109 | 3 119 229 | po rozstrzygnięciu powyższych i verify |

**Kategorie bez wpływu na listy** (każda ma niezależną odmowę i jest zachowana w diagnostyce):

| Kategoria | Liczebność | Wynik |
|---|---|---|
| mieszane nazwy pospolite i własne | 295 kompaktowych | game-required-uppercase-v1=reject |
| `pisane_łącznie_z_przyimkiem` (ń/on:S, wiersze 4212679–80) | 2 kompaktowe / 6 rozwinięć | odmowa: segment zależny i długość |
| odroczone kontrakcje `-ń` | 8 form / 24 analizy | odmowa: zakres pierwszego wydania |
| brev | 449 | reject |
| etn. | 83 lematy / 967 interpretacji (wielka litera) | reject przez wielką literę |
| 1 910 nieobjaśnionych etykiet | — | wymóg glosy zwolniony decyzją użytkownika |

Stany słów (poza unią kategorii merytorycznych):

| Stan słowa | BROAD | STANDARD |
|---|---|---|
| definitywna odmowa | 1 548 874 | 1 937 754 |
| czyste, zależne tylko od placeholderów | 2 825 370 | 2 814 170 |

Na wariant jest 5 056 983 kluczy.

## R1 — przesiew nazw mieszkańców `-anin/-anka`

1. **Status i kryterium.**
   - Status: unresolved / dowód klasy niedostępny.
   - RJP 2026 §8.1.2 pkt 3 (s. 43) wymaga wielkiej litery dla nazw mieszkańców. SGJP zapisuje je małą literą jako `nazwa_pospolita`, bo stosuje wcześniejszą normę.
   - Kryterium: forma i lemat małą literą, klasa subst/depr, oraz:
     - lemat kończący się na `anin`, w analizie m1 (2 103 lematy), albo
     - lemat `…anka`, utworzony z takiego lematu, w analizie f (2 051 lematów).
   - Z kryterium wyłączono lematy rozstrzygnięte w polityce (`MANDATORY_CAPITAL_2026_LEMMAS`, warszawianka) oraz R2.
   - Ograniczenia populacji: niepełność (inne sufiksy) oraz fałszywe trafienia (np. chrześcijanin, mieszczanin, ziemianin, poganin); szczegóły w Open Questions.
2. **Liczebność.**
   - BROAD: 42 863 kompaktowe, 58 846 analiz, 39 095 słów zależnych (wszystkie jedyne).
   - STANDARD: 42 675 kompaktowych, 58 578 analiz, 38 997 słów.
   - Homonim z czystą analizą zwalnia słowo, np. `krakowian` (m3, wiersz 2229539) jest czysty mimo analizy dopełniacza `krakowianin`.
   - W KWJP orth występuje 539 z 39 095 słów.
3. **Czego brakuje.** Brakuje informacji, czy konkretne pełne ID SGJP ma znaczenie „mieszkaniec miejscowości lub regionu”. Ta informacja decyduje między wielką literą wymaganą (reject w grze) a pospolitym zapisem małą literą (accept).
   - Eksport ma tylko pięć pól i nie zawiera relacji `substhab`/`habsubst`.
   - Publiczny czytnik je zawiera, ale właściciel odłożył go jako wejście.
   - KWJP nie rozróżnia znaczeń.
   - W przypiętych źródłach nie ma drogi per słowo. Możliwe jest tylko dopasowanie heurystyczne (stem → toponim `nazwa_geograficzna` w SGJP). Byłoby to nowe kryterium „przez sufiks”, wcześniej świadomie niewłączone.
4. **Przykłady.**

   | Wiersz | Forma | Lemat | Tag | Kwalif. | Uwaga |
   |---|---|---|---|---|---|
   | sgjp-20260823 1079744 | abramowian | abramowianin | subst:pl:gen:m1 | — | |
   | 2120117 | kisieliczanin | kisieliczanin | subst:sg:nom:m1 | — | |
   | 2229577 | krakowianka | krakowianka | subst:sg:nom:f | — | |
   | 1377204 | chrześcijanin | chrześcijanin | subst:sg:nom:m1 | — | fałszywe trafienie |
   | 2448296 | mieszczanin | mieszczanin | subst:sg:nom:m1 | — | fałszywe trafienie |

5. **Opcje.** Zob. sekcję „Opcje decyzji dla właściciela”: R1-A, R1-B, R1-C.

## R2 — przykłady mieszkańców wymienione dosłownie w RJP

1. **Status i kryterium.**
   - Status: konflikt — SGJP zapisuje małą literą, RJP 2026 wielką.
   - Kryterium: 24 przykłady z RJP §8.1.2 pkt 3, zapisane małą literą i wyszukane jako lematy SGJP (m1 lub f, depr).
   - Wyłączono lematy już rozstrzygnięte: warszawianin, warszawiak, krakowiak:Sm1. Krakowiak:Sm2 to taniec (m2), więc jest poza kryterium.
   - W SGJP występuje małą literą 7 lematów: bawarka, krakowianin, krakus, kresowianin, rzymianin, sądeczanin, zatorzanin.
2. **Liczebność.**
   - 83 kompaktowe i 116 analiz na wariant; 70 słów BROAD i 70 STANDARD, wszystkie z jedyną kategorią.
   - Z tego bawarka (10 słów) ma kwalifikator `kulin.` (napój), więc nie jest nazwą mieszkanki. Pozostałe 6 lematów daje 60 słów.
3. **Czego brakuje.** Brakuje tylko decyzji, czy dosłowny przykład RJP dla tego samego napisu wystarcza jako dowód klasy pełnego ID SGJP.
   - Droga w przypiętych źródłach: RJP PDF (sha 87daaddd…d72e), s. 43, oraz kwalifikator SGJP `kulin.` jako rozróżnienie znaczenia bawarki.
   - Ryzyko dla rzymianin i krakus: SGJP może opisywać pod tym samym ID inne znaczenie (np. potoczne). Eksport tego nie pokazuje.
4. **Przykłady.**

   | Wiersz | Forma | Lemat | Tag | Kwalif. |
   |---|---|---|---|---|
   | 5549367 | rzymianin | rzymianin | subst:sg:nom:m1 | — |
   | 2229681 | krakus | krakus | subst:sg:nom:m1 | — |
   | 2237776 | kresowianin | kresowianin | subst:sg:nom:m1 | — |
   | 5944839 | sądeczanin | sądeczanin | subst:sg:nom:m1 | — |
   | 1206021 | bawarka | bawarka | subst:sg:nom:f | kulin. |

## A — adjp (forma przyimkowa przymiotnika)

1. **Status i kryterium.**
   - Status: unresolved — samodzielność segmentu w grze.
   - Kryterium: klasa źródłowa `adjp`. Ma 8 606 kompaktowych rekordów; 300 w BROAD i 591 w STANDARD ma niezależną odmowę.
   - Populacja jest kompletna, bo klasa jest jawna w tagu.
2. **Liczebność.**
   - BROAD: 8 306 analiz, 7 556 słów (wszystkie jedyne).
   - STANDARD: 8 015 analiz, 7 269 słów.
   - W KWJP orth występuje 181 z 7 556 słów.
3. **Czego brakuje.** Forma występuje wyłącznie po przyimku `po` (`po polsku`). RJP §4.4 pkt 1 każe pisać wyrażenia przyimkowe rozdzielnie, więc ortograficznie „polsku” jest osobnym wyrazem. Brakuje decyzji reguły gry, czy taki niesamodzielny wyraz graficzny jest dopuszczalny.
   - Ta decyzja jest analogiczna do istniejącej `game-dependent-segment-v1`, którą zastosowano do `ń`.
   - Dane są kompletne w eksporcie SGJP i RJP. Nowy dowód nie jest potrzebny.
4. **Przykłady** (wszystkie bez kwalifikatora):

   | Wiersz | Forma | Lemat | Tag |
   |---|---|---|---|
   | 4618674 | polsku | polski:A | adjp:dat |
   | 1077532 | abakańsku | abakański | adjp:dat |
   | 1077676 | abchasku | abchaski | adjp:dat |
   | 1078441 | abisyńsku | abisyński | adjp:dat |

## F — frag (fragment frazy)

1. **Status i kryterium.**
   - Status: unresolved — brak znaczenia lub użycia; 14 rekordów ma dowód użycia.
   - Kryterium: klasa źródłowa `frag`, 147 kompaktowych rekordów (109 małą, 38 wielką literą). Niezależną odmowę ma 41 w BROAD i 62 w STANDARD.
   - Populacja jest kompletna (jawna klasa). Odczyt czytnika obejmował wszystkie 147, ale nie jest aktywnym wejściem.
2. **Liczebność.**
   - BROAD: 106 kompaktowych, 112 analiz, 67 słów (62 jedyne).
   - STANDARD: 85 kompaktowych, 90 analiz, 57 słów (53 jedyne).
   - Nakładają się z U/P: dwójnasób, trójnasób, kroćset, wznak, ibn.
   - 36 z 67 słów ma jakąkolwiek jednostkę KWJP.
3. **Czego brakuje.** Brakuje frazy, w której fragment występuje, oraz rozstrzygnięcia, czy sam fragment jest wyrazem dopuszczalnym w grze.
   - RJP §4.4 pkt 1 (UWAGA) dosłownie podaje zapis `wte i wewte`. To przypięty dowód, że wte i wewte są osobnymi wyrazami graficznymi.
   - Dla pozostałych frazy nie ma w eksporcie (tylko w odłożonym czytniku). KWJP bigramy mogą pokazać kolokację, ale nie dowodzą poprawności.
4. **Przykłady.**

   | Wiersz | Forma | Tag | Kwalif. |
   |---|---|---|---|
   | 6465979 | wte | frag | pot. |
   | 6339103 | wewte | frag | pot. |
   | 1186786 | bajduś | frag | — |
   | 1221841 | bezcen | frag | — |
   | 1960055 | ibn | frag | — |

## B — `-by` spoza listy RJP 4.5

1. **Status i kryterium.**
   - Status: unresolved — status odrębnego wyrazu.
   - Kryterium: comp/conj/part/qub/adv z lematem kończącym się na `by`, spoza listy RJP §4.5 pkt 1c–d oraz spoza zakodowanych jeśliby/jeżeliby.
   - Populacja jest pełna dla tego kryterium.
2. **Liczebność.**
   - BROAD: 4 kompaktowe, 4 analizy, 4 słowa: bodajby, jeźliby, kieby, niechby.
   - STANDARD: 3 słowa; jeźliby (`daw.`) jest odrzucone.
3. **Czego brakuje.** Lista RJP 4.5 pkt 1c zaczyna się od „np.”, więc jest otwarta. Według §4.6 pkt 2 „bodaj” i „niech” pisze się rozdzielnie jako partykuły. Formy z `-by` nie są tam jednak wymienione.
   - SGJP podaje je jako jeden segment.
   - Droga w przypiętych źródłach: decyzja interpretacyjna RJP + SGJP; nowych danych nie ma.
4. **Przykłady.**

   | Wiersz | Forma | Tag | Kwalif. |
   |---|---|---|---|
   | 1271504 | bodajby | part | — |
   | 2828906 | niechby | part | — |
   | 2109581 | kieby | comp | gwar. |
   | 2037652 | jeźliby | comp | daw. |

## U i P — pozostałość i domknięcie udokumentowanych użyć

1. **Status i kryterium.** Status: unresolved.
   - Rekordy z przeglądem w `config/generator/semantic-uses.json` (19 interpretacji, 22 użycia) mają dwie niewiadome:
     - U — pozostałość pełnego ID poza sprawdzonym użyciem;
     - P — kod v21 `semantic-use-qualification-pending-v1` dla samego użycia.
2. **Liczebność.**
   - U: BROAD 19 kompaktowych, 22 analizy, 15 słów (10 jedynych, wszystkie to formy warszawianka); STANDARD 18/21/14 (10).
   - P: BROAD 6 analiz, 4 słowa (dwójnasób, kroćset, trójnasób, wznak); STANDARD 5 analiz, 3 słowa. P nigdy nie jest jedyną kategorią, bo te słowa są też w F i U.
3. **Czego brakuje.**
   - U: brakuje pewności, że pełne ID nie ma innych znaczeń. Eksport tego nie rozróżnia, a czytnik jest odłożony.
   - P: brakuje domknięcia pozostałych warunków gry dla użycia ograniczonego do frazy.
   - Jedyną drogą jest decyzja reguły. Nowe dane nie są dostępne.
4. **Przykłady.**

   | Wiersz | Forma | Lemat | Tag | Użycie / uwaga |
   |---|---|---|---|---|
   | 6309665 | warszawianka | — | subst:sg:nom:f | U |
   | 1647764 | dwójnasób | — | frag | sgjp-authors-phrase-dwojnasob-v1 |
   | 6770165 | wznak | — | frag | sgjp-authors-phrase-wznak-v1 |
   | 2244647 | kroćset | — | frag | daw. |
   | 5520636 | roścież | roścież:F | frag | nie blokuje: inny homonim czysty |

## Q — formalna semantyka złożonych kwalifikatorów

1. **Status i kryterium.**
   - Status: pending (`all_compound_qualifier_semantics_and_variant_policy`).
   - Kryterium: nieodrzucona analiza z niepustym polem kwalifikatorów.
   - Wszystkie etykiety mają zatwierdzony warunek: 604 z 605 zmapowane, a jedna, `pisane_łącznie_z_przyimkiem`, ma niezależną odmowę.
2. **Liczebność.**
   - BROAD: 884 768 kompaktowych, 2 061 404 analizy, 635 937 słów.
   - STANDARD: 359 949 kompaktowych, 821 360 analiz, 258 653 słowa.
   - Liczone są tylko słowa bez analizy wolnej od kwalifikatorów.
3. **Czego brakuje.** Brakuje formalnego potwierdzenia, że warunek etykiety złożonej to koniunkcja warunków składowych, oraz zasad dla wariantów. Kod już tak liczy.
   - Droga w przypiętych źródłach: istniejące decyzje rejestrów etykiet. Nowe źródło nie jest potrzebne.
4. **Przykłady.**

   | Wiersz | Forma | Lemat | Tag | Kwalif. | Zależność |
   |---|---|---|---|---|---|
   | 1077569 | abaci | abat | subst:pl:nom:m1 | daw. | tylko BROAD |
   | 1077547 | abakus | — | subst:sg:nom:m3 | archit.,hist. | — |
   | 1077548 | abakusa | — | subst:sg:gen:m3 | archit.,hist. | — |

## Warstwa aktywacji i macierz klas

- **Zakres.** Każda nieodrzucona analiza ma 2 placeholdery, więc warstwa obejmuje wszystkie słowa z nieodrzuconą analizą: 3 508 109 BROAD i 3 119 229 STANDARD.
- **Czego brakuje.** Nie brakuje informacji: to przełącznik aktywacji polityki i metadanych gry po domknięciu kategorii i verify.
- **Analizy czyste według klasy** (BROAD), czyli populacja, której dotyczy pending `full_category_and_orthography_matrix`:

  | Klasa | Analizy | Klasa | Analizy |
  |---|---|---|---|
  | adj | 3 645 123 | adv | 24 923 |
  | ppas | 2 009 654 | depr | 23 058 |
  | subst | 1 168 281 | inf | 22 891 |
  | pact | 1 054 172 | imps | 22 490 |
  | praet | 846 682 | pant | 11 519 |
  | cond | 516 696 | pcon | 10 244 |
  | ger | 423 552 | num | 3 164 |
  | fin | 137 290 | konstrukcje impt-single | 89 293 |
  | impt | 69 935 | | |

  Małe klasy: interj 355, winien 280, ppron3 234, ppron12 155, part 147, prep 122, comp 46, conj 32, pred 25, adjc 11, bedzie 6.
- **Bez osobnej populacji.** Kod nie wskazuje w nich żadnej analizy unresolved. Nie zidentyfikowano też osobnej populacji dla pending `documented_game_conditions_without_sjp_editorial_source_policy`. Liczb słów nie podano, żeby nie przypisywać im danych bez podstawy.

## Opcje decyzji dla właściciela (bez wdrożenia)

Wpływ podano jako zmianę liczby słów zależnych BROAD/STANDARD. „Wyłączenie” oznacza odmowę słowa w pierwszym wydaniu z jawnym raportem „nieudowodnione”. Słowa z czystym homonimem pozostają bez zmian.

- **Wszystkie kategorie, A (domyślne):** utrzymać unresolved. Blokada wydania: 46 877 słów w unii; z warstwą Q blokada nadal trwa.
- **R1 przesiew mieszkańców:**
  - B: wyłączyć cały przesiew z pierwszego wydania. Około −39 095/−38 997 słów zależnych, które wypadają z list. Wypadną też fałszywe trafienia (chrześcijanin, mieszczanin…).
  - C: przyjąć zapis SGJP (`nazwa_pospolita`, mała litera) jako operacyjną klasyfikację z raportem ograniczenia, podobnie jak próg wieku A. Około −39 095/−38 997 słów zależnych, które wchodzą na listy. Ryzyko: małe litery w nazwach, które RJP 2026 każe pisać wielką.
  - D: B lub C plus ręczna zamknięta lista wyjątków dla oczywistych nie-mieszkańców (chrześcijanin…). Wymaga nowego przeglądu.
- **R2 przykłady RJP:**
  - B: przykład RJP jako dowód klasy → reject 6 lematów (60 słów).
  - Bawarka `kulin.` → czyste (10 słów wchodzi).
  - Wpływ: −70/−70 słów zależnych.
- **A adjp:**
  - B: niesamodzielny wyraz graficzny → reject. −7 556/−7 269 słów, które wypadają.
  - C: osobny wyraz graficzny według RJP §4.4 → accept. Tyle samo słów wchodzi.
- **F frag:**
  - B: wyłączyć wszystkie frag bez dowodu. −67/−57 słów zależnych; zostają tylko formy z czystymi homonimami.
  - C: dopuścić wte/wewte (RJP) oraz udokumentowane użycia, resztę wyłączyć. Około +2 do +5 wchodzi, reszta wypada.
  - D: dopuścić wszystkie frag jako wyrazy graficzne.
- **B `-by`:**
  - B: wyłączyć 4/3 słowa.
  - C: przyjąć SGJP jako jeden wyraz (+4/+3).
- **U/P:**
  - B: przyjąć, że sprawdzone użycie wyczerpuje pełne ID, i domknąć warunki frazy. Dotyczy 15/14 słów, z których 10 to warszawianka (reject przez wielką literę).
  - C: wyłączyć pozostałość.
- **Q:**
  - B: zamknąć pending jako koniunkcję warunków składowych, zgodnie z kodem. 635 937/258 653 słów przestaje zależeć od tej warstwy; lista się nie zmienia.
  - A: utrzymać pending, czyli blokować wszystkie te słowa.

**Podsumowanie.**
- Słowa zależne od dowolnej niewiadomej merytorycznej: BROAD 46 802, STANDARD 46 406, unia 46 877, przecięcie 46 331.
- Z formalną warstwą Q zależnych jest 682 739 słów BROAD i 305 059 STANDARD.
- Rozstrzygalne bez nowych źródeł (decyzją reguły lub interpretacji na przypiętych SGJP/RJP): A, B, R2, Q oraz część F i P/U. Razem około 7 630/7 342 słów, plus cała warstwa formalna Q.
- R1 można domknąć tylko decyzją klasową (B/C), a nie dowodem per słowo.

## Odtwarzanie

Komenda; każdy przebieg trwał ok. 527 s, a oba uruchomiono równolegle, N=1,2:

```
python3 scripts/probe_unresolved_inventory.py \
  --database data/work/import-20261004-1302/build.sqlite \
  --candidates-database data/work/g5-20261005-225423/build.sqlite \
  --lists-dir tmp/unresolved-inventory/runN-lists > tmp/unresolved-inventory/runN.json
```

| Pozycja | SHA-256 |
|---|---|
| skrypt | 9773513b4dce7d7393c628d7994918c8d9e8f9648a6ef945c687d65242365db5 |
| G2 przed i po | e0371fdf8b4be3187c864a2f2dcb5544d8445d99f79dbbe24c04bbaa5007f35e |
| G5 przed i po | 0dc53d2c37e3dadbc16177512495ae3985eea9173a67546d7490f319cb1bf2e7 |
| run1.json = run2.json | 13497395aebeac153511fd6b7a2720aa51a7d2f6ad93ae339893e1ac812ad451 |

- Obie bazy otwierano wyłącznie w trybie `mode=ro`; `readonly_unchanged=true`.
- Katalogi list są identyczne (`diff -r`). Pełne listy słów leżą w `tmp/unresolved-inventory/run1-lists/`; SHA-256 każdego pliku zapisano w [JSON](unresolved-inventory.json).
- Teksty RJP odczytano z przypiętego PDF (sha 87daaddd…d72e) ekstraktorem `tmp/unresolved-inventory/rjp_text.py`. Litera „ó” renderuje się w nim jako „?”.
- Liczby KWJP pochodzą z readonly zapytań do `corpus_evidence` w G2.
