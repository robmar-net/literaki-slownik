# Warianty rozwiązania: słowniki tematyczne

## TL;DR
Przejrzeliśmy 6 obszarów decyzji, w każdym 3–5 wariantów (razem 22).
Polecamy: listę warstwową (rdzeń SGJP, potem Słowosieć A z częściami i miejscami) z oceną próby. Temat opisuje jeden plik konfiguracji w repozytorium.
Jednostką jest leksem SGJP, a formy bierzemy z bazy. Homonimy oznaczamy, nie usuwamy. Wszystkie tematy idą w jednym pakiecie „TEMATY” na wzór POP00.
Kolejność: matematyka (pilotaż), potem morze, na końcu rolnictwo po pomiarze nowych korzeni. IATE to opcjonalna warstwa później. LLM odkładamy, bo to wydatek i wymaga dwóch potwierdzeń.
Pewność: średnia. Trafność i pokrycie ocenił jeden oceniający.

## Key Decisions
- **Cel: lista warstwowa** (T1 rdzeń SGJP, T2 Słowosieć A + części/miejsca, T3 uzupełnienia). Dzięki warstwom ten sam pakiet obsłuży wąski rdzeń terminów i pełny temat.
- **Źródła teraz: SGJP + Słowosieć 4.5 (A + rel. 25, 27).** Skojarzeń (rel. 108, 146) nie bierzemy, bo połowa to szum. IATE i LLM to osobne, późniejsze decyzje.
- **Temat = plik konfiguracji** (atomy SGJP, korzenie z id synsetu, wykluczenia, jawne dodatki z bazy). Plik wersjonujemy i zmieniamy przez przegląd.
- **Leksem SGJP jako jednostka; formy ∩ STANDARD.** Każdy wpis ma zapisane źródło. Gdy lemat ma znaczenia spoza tematu, wpis dostaje flagę `wieloznaczny`.
- **Jeden pakiet „TEMATY”** w stylu POP00 (`method.json`, `LIMITATIONS.md`, `ATTRIBUTIONS.md` z notą plWordNet). Przed wydaniem trzeba rozstrzygnąć licencję Słowosieci 4.5.
- **ADR przed wdrożeniem.** Dotyczy metod spoza Zadania E (SGJP, Słowosieć). Zapisuje też statusy metod: E1 słaba, E2 zablokowana, E3 odroczona.

## Open Questions / Risks
- **Licencja Słowosieci 4.5.** Link w repozytorium zwraca 404, nota mówi „4.2 © 2020”, a w zipie nie ma LICENSE. To blokuje wydanie, ale nie budowę roboczą. Decyzja użytkownika nr 1 z raportu.
- **Jeden oceniający.** Korzenie, lista 107 słów i ocena prób pochodzą od agenta. Proponujemy, by operator został drugim oceniającym na małej próbie.
- **Rolnictwo 40%.** Brakuje czynności i budynków (`orka`, `obora`, `ciągnik`). Nowych korzeni jeszcze nie zmierzono. Jeśli nie pomogą, zostaje LLM (wydatek) albo ręczne dodatki.
- **Wynik zależy od korzeni i wydania** (matematyka A: 558 lematów w 4.2, 431 w 4.5). Trzeba przypiąć wydanie i zapisać korzenie.
- **Granice tematu** to decyzja redakcyjna, np. rośliny egzotyczne pod `roślina uprawna`.
- **Do czego służy lista?** Prompt v3 mówi o dodatku do wiedzy bota. Wiki jest dla odwiedzających. Od odbiorcy zależy, czy wydanie publiczne jest potrzebne od razu.

## Problem Reframing

### Research Question
Czy możemy zbudować listy tematyczne (marynistyka, rolnictwo, matematyka, potem inne) jako podzbiory słownika projektu i z czego?
Odpowiedź z badania: tak dla matematyki (86% pokrycia) i morza (78%). Rolnictwo tylko częściowo (40%).

### How Might We
1. Jak sprawić, by lista tematyczna była trafna, a zarazem zawierała słowa podstawowe, a nie tylko terminy fachowe?
2. Jak połączyć źródła tak, by zysk w pokryciu nie zalał listy szumem?
3. Jak opisać temat, żeby wynik dało się odtworzyć i poprawić bez kodu?
4. Jak zachować regułę „temat ⊆ słownik przy stole” i uczciwie oznaczyć wieloznaczność?
5. Jak wydać listy zgodnie z licencjami (nota plWordNet, atrybucja IATE)?
6. Jak kolejnością tematów obniżyć ryzyko i koszt?

## Explored Alternatives

### D1. Cel listy

**D1-A. Rdzeń terminów (wąski)**
Tylko leksemy z etykietą dziedziny SGJP. Lista krótka i fachowa.
- Plusy: trafność 29/27/30 na 30. Dane i kod już są. Licencja BSD-2.
- Minusy: pokrycie słów oczywistych 27/0/23%. Brak `kotwica`, `pług`, `sinus`. Rolnictwo bez słów podstawowych.
- Najlepszy, gdy: bot ma być „fachowcem”, a nie „miłośnikiem tematu”.
- Dowód: raport W2–W5; WSJP *Zasady* s. 37, 47 (kwalifikator = termin).

**D1-B. Pełny temat (jedna płaska lista)**
Słowa podstawowe i terminy razem, bez rozróżnienia.
- Plusy: najprostszy odbiór. Jedna liczba na temat.
- Minusy: miesza trafność 30/30 z 14/30 (rolnictwo A). Odbiorca nie może zawęzić listy. Każda poprawka zmienia całość.
- Najlepszy, gdy: odbiorcą jest człowiek, który przegląda listę.
- Dowód: W13, W14.

**D1-C. Warstwy (T1 / T2 / T3)** — *polecany*
T1: etykiety SGJP. T2: Słowosieć A + części i miejsca. T3: uzupełnienia (później IATE, jawne dodatki). Każdy wpis ma warstwę i źródło.
- Plusy: zawiera A i B (T1 to rdzeń, T1–T3 to pełny temat). Trafność widać osobno dla każdej warstwy. Pasuje do zasady promptu v3: zapisuj wynik i niepewność.
- Minusy: więcej pól w pakiecie i trzeba wyjaśnić warstwy na wiki.
- Najlepszy, gdy: nie wiemy jeszcze, kto i jak użyje list.
- Dowód: tabela źródło × cechy w syntezie §7; prompt v3 §10 („różne wyniki”, „niepewność”).

**D1-D. Wynik ciągły na leksem (0–3)**
Każdy leksem bazy dostaje wynik przynależności. Próg wybiera odbiorca, podobnie jak `vocabulary_level` w prompcie v3.
- Plusy: najbardziej elastyczny. Naturalny format dla LLM (E3).
- Minusy: źródła słownikowe dają tylko „tak/nie”, więc wynik byłby udawany. Bez LLM nie ma czym go policzyć.
- Najlepszy, gdy: zapadnie decyzja o LLM.
- Dowód: W20, `wide-metody-llm.md`.

### D2. Kombinacja źródeł

**D2-A. Tylko SGJP**
- Plusy: zero nowych źródeł i zero nowych licencji. Kilka dni pracy.
- Minusy: 254/96/62 leksemy. Rolnictwo 0% pokrycia.
- Dowód: W2, W4.

**D2-B. SGJP + Słowosieć 4.5 A + części i miejsca (rel. 25, 27)** — *polecany*
- Plusy: najlepszy zmierzony przyrost przy dobrej trafności (A: 23/14/23 na 30). Części są lepsze od skojarzeń. Dane leżą lokalnie. 85–88% nowych słów jest w BROAD v31.
- Minusy: nowa licencja z niejasną wersją. Korzenie wybiera się ręcznie. Rolnictwo dalej słabe.
- Dowód: W11–W14; `wide-plwordnet-pomiar.md`.

**D2-C. Jak B + słowa pojedyncze z IATE**
- Plusy: czysta licencja z atrybucją. Dodaje terminy morskie (`cuma`, `kilson`, `szpigat`).
- Minusy: tylko 7–21% haseł to pojedyncze słowa. Rolnictwo jest szumne (`fosfina`, `ebola`), a matematyka uboga (≥87 haseł). Trafności i pokrycia nie zmierzono. Potrzebne konto EU Login albo stary TBX z 2019.
- Dowód: W15.

**D2-D. Jak B + LLM jako oceniający (E3)**
- Plusy: jedyna metoda, która sięga poza wybrane drzewa (`orka`, `obora`). Ocenia całą bazę (212 728 leksemów). Mieści się w prompcie v3.
- Minusy: koszt nieznany (~1,7 mln tokenów wejścia i ~1,3 mln wyjścia na temat, ×3 przebiegi). Warunki wyniku u dostawcy niesprawdzone. Wymaga dwóch potwierdzeń. Model o otwartych wagach na Macu to wariant bez opłat, ale licencję wag trzeba sprawdzić.
- Dowód: W20.

**D2-E. Słowosieć zbiór C (z skojarzeniami)**
- Plusy: najwyższe pokrycie (59/40/86%).
- Minusy: dodatki C − A są w połowie szumem (16/8/10 trafnych na 30: `kot`, `nowomowa`, `szeryf`). Wymaga dużo więcej przeglądu.
- Dowód: W14.

### D3. Jak definiujemy i utrzymujemy temat

**D3-A. Plik konfiguracji tematu** — *polecany*
Jeden plik na temat w repozytorium: atomy SGJP, korzenie Słowosieci (id synsetu i nazwa), dozwolone relacje, wykluczenia (leksemy lub poddrzewa) i jawne dodatki. Dodatki muszą być w bazie. Zmiana pliku to nowa wersja tematu.
- Plusy: wynik da się odtworzyć. Nowy temat to nowy plik bez kodu. Wykluczenia usuwają znany szum (`monstera`). Jawne dodatki łatają rolnictwo (`orka`, `obora`). Prompt v3 dopuszcza „jawnie podaną listę użytkownika”.
- Minusy: korzenie wciąż wybiera człowiek. Długie listy wykluczeń mogą ukryć słabość źródła.
- Dowód: „temat leży w wielu gałęziach” (synteza §3); wzór konfiguracji POP00 (ADR-009).

**D3-B. Lista ręczna po jednorazowym generowaniu**
Generujemy raz, a potem źródłem prawdy jest plik słów, który redagujemy ręcznie.
- Plusy: pełna kontrola nad każdym słowem.
- Minusy: nowa baza albo wydanie Słowosieci nie przechodzi automatycznie. Odtwarzalność ginie. Przy 600–900 słowach na temat to dużo pracy.
- Dowód: W12 (rozmiary tematów).

**D3-C. Korzenie wybierane automatycznie**
Na przykład z domen PWN po mapowaniu (B1/B2) albo od synsetu nazwy tematu.
- Plusy: brak ręcznej pracy i łatwe skalowanie na nowe tematy.
- Minusy: zmierzone B1/B2 dają 0–11% dla morza i rolnictwa. Temat leży w wielu gałęziach.
- Dowód: W13.

**Przegląd (dotyczy każdego wariantu):**
- R1: tylko agent, próba 50–100 na temat. Tanio, ale z jednym oceniającym.
- R2 *(polecany)*: agent ocenia próbę 50 na warstwę, a operator ocenia 30 z niej jako drugi oceniający. Zapisujemy zgodność. Operator gra w Literaki, więc dobrze ocenia słowa.
- R3: pełny przegląd każdego słowa. Najdokładniejszy, ale przy 600–900 słowach na temat za drogi.

### D4. Jednostka, przecięcie z bazą, homonimy

**D4-A. Leksem SGJP; formy ∩ STANDARD** — *polecany*
Lemat ze Słowosieci mapujemy na leksemy SGJP (lemat i część mowy). Formy bierzemy z bazy STANDARD. Odbiorca może zawęzić wynik do POP/POP0/POP00 przez przecięcie.
- Plusy: zgodne z promptem v3 („najpierw leksemy, potem formy”, „podzbiór słownika przy stole”). Jedna lista na temat.
- Minusy: dla bazy BROAD odbiorca musi przeciąć sam albo trzeba drugi plik.
- Dowód: prompt v3 §10; synteza §5.

**D4-B. Osobna lista na każdą bazę (BROAD, STANDARD, POP0)**
- Plusy: gotowe do użycia bez przecinania.
- Minusy: trzy razy więcej plików i liczb na wiki. Ryzyko rozjazdu przy nowym buildzie.

**D4-C. Same lematy, bez form**
- Plusy: najmniejszy plik, czytelny dla człowieka.
- Minusy: bot gra formami, więc i tak musi je rozwinąć. Gubimy związek z leksemem SGJP przy homonimach.

**Homonimy (podwybór):**
- H1 *(polecany)*: oznaczamy. Wpis z lematem, który ma w Słowosieci znaczenia spoza drzewa tematu, dostaje flagę `wieloznaczny` i zapisane znaczenie źródłowe. Przegląd może go wykluczyć. Prompt v3 wymaga, by uwzględniać wieloznaczność.
- H2: usuwamy wszystkie wieloznaczne. Lista robi się czysta, ale tracimy `pole`, `liczba`, `orka`.
- H3: lista na poziomie znaczeń. Najdokładniejsza, ale bot gra napisem, nie znaczeniem. Poza zakresem.

### D5. Pakiet i publikacja

**D5-A. Jeden pakiet „TEMATY” z plikiem na temat** — *polecany*
Wzór POP00: osobna podkomenda obok `pop`/`pop00`, wspólny `method.json` z wersją metody i wydaniem Słowosieci, a do tego `LIMITATIONS.md` i `ATTRIBUTIONS.md` (nota plWordNet, później atrybucja IATE). W pakiecie jest plik na temat i manifest z liczbami.
- Plusy: jedna metoda, jedna nota i jedna strona wiki `Slownik-TEMATY`. Nowy temat dochodzi jako nowy plik.
- Minusy: zmiana jednego tematu wymaga nowej wersji całego pakietu.
- Dowód: ADR-009; runbook wiki („nowy rodzaj słownika = nowa strona”).

**D5-B. Osobny pakiet na każdy temat**
- Plusy: tematy mają niezależne wersje i wydania.
- Minusy: noty licencyjne i metoda powielone w każdym pakiecie. Na wiki N stron.

**D5-C. Tylko artefakt roboczy, bez wydania**
Listy zostają w `data/work`, a korzystają z nich tylko boty.
- Plusy: omija blokadę licencji Słowosieci. Najszybsze.
- Minusy: wbrew zasadzie wiki z AGENTS.md (praca bez wiki jest nieskończona). Odbiorca nie ma stabilnej wersji.

**Wspólne warunki:** nie publikujemy surowego zrzutu Słowosieci (są w nim nazwiska redaktorów i log IP), tylko listy lematów. Stronę wiki „W przygotowaniu” zakładamy na starcie prac.

### D6. Pierwsze tematy i kolejność

**D6-A. Matematyka → morze → rolnictwo, z bramką po pilotażu** — *polecany*
Matematyka ma najwyższe pokrycie (86%), więc najtaniej sprawdza całą ścieżkę: konfigurację, mapowanie, przegląd i pakiet. Morze (78%) idzie jako drugie. Rolnictwo dopiero po pomiarze nowych korzeni (czynności, budynki).
- Plusy: najmniejsze ryzyko, bo błąd metody wychodzi na najczystszym temacie.
- Minusy: najbardziej „życiowy” temat dla graczy przychodzi ostatni.

**D6-B. Wszystkie trzy naraz**
- Plusy: jedno wydanie i jeden przegląd.
- Minusy: rolnictwo (40%) blokuje albo obniża jakość całego wydania.

**D6-C. Najpierw morze**
- Plusy: największy rdzeń SGJP (254) i najbogatszy temat dla bota „żeglarza”.
- Minusy: pokrycie 78% i więcej szumu niż w matematyce, więc ścieżka sprawdzana jest w trudniejszych warunkach.

**D6-D. Jeden temat i stop do decyzji**
- Plusy: najmniej pracy przed oceną przydatności.
- Minusy: wolniej. Ścieżka, którą już przyjęliśmy, i tak obejmuje A po bramce.

## Trade-Off Analysis

Skala: W = wysoko (korzystnie), Ś = średnio, N = nisko (niekorzystnie). Przy ryzyku W oznacza niskie ryzyko.

| Wariant | Wykonalność | Wpływ na odbiorcę | Prostota | Ryzyko | Skalowalność |
|---|---|---|---|---|---|
| D1-A rdzeń | W | N | W | W | Ś |
| D1-B pełny płaski | W | Ś | W | Ś | N |
| **D1-C warstwy** | W | W | Ś | W | W |
| D1-D wynik ciągły | N (bez LLM) | W | N | N | W |
| D2-A SGJP | W | N | W | W | N |
| **D2-B + Słowosieć A/części** | W | W | Ś | Ś (licencja) | Ś (korzenie ręczne) |
| D2-C + IATE | Ś (EU Login) | Ś | N | Ś | Ś |
| D2-D + LLM | Ś | W? (nie zmierzono) | N | N (koszt, warunki) | W |
| D2-E Słowosieć C | W | N (szum) | N | Ś | Ś |
| **D3-A plik tematu** | W | W | W | W | W |
| D3-B lista ręczna | W | Ś | Ś | Ś | N |
| D3-C korzenie auto | Ś | N | W | N | W |
| **D4-A leksem ∩ STANDARD** | W | W | W | W | W |
| D4-B lista na bazę | W | W | N | Ś | N |
| D4-C same lematy | W | N | W | Ś | Ś |
| **D5-A pakiet TEMATY** | W | W | W | Ś (licencja) | W |
| D5-B pakiet na temat | W | Ś | N | Ś | Ś |
| D5-C bez wydania | W | N | W | Ś (sprzeczne z AGENTS) | N |
| **D6-A kolejno z bramką** | W | Ś | W | W | W |
| D6-B naraz | Ś | Ś | Ś | N | Ś |
| D6-C morze pierwsze | W | W | W | Ś | W |
| D6-D jeden i stop | W | N | W | W | N |

Główne napięcia:
- **Pokrycie a trafność.** Każda warstwa dokłada słowa i obniża trafność (30 → 23 → 16 na 30). Warstwy (D1-C) nie każą wybierać jednego punktu.
- **Rolnictwo a koszt.** Tylko LLM albo ręczna praca (korzenie, dodatki) domyka luki. Ręczna praca jest tańsza i najpierw trzeba ją zmierzyć.
- **Szybkość a licencja.** Wydanie czeka na decyzję o licencji Słowosieci. Budowa robocza może ruszyć od razu.

## User Preferences
W tym kroku nie było dialogu z użytkownikiem. Obowiązują ograniczenia projektu:
- Wydatki (LLM, płatne API) wymagają dwóch potwierdzeń.
- Nie kontaktujemy autorów (stąd brak Słowosieci 5.0 i tokenu API IATE).
- Wikisłownik jest odroczony, dopóki użytkownik go nie otworzy.
- Temat to podzbiór słownika przy stole. LLM nie dodaje słów i nie rozstrzyga o dopuszczalności (prompt v3).
- Zmiany kryteriów i nowe słowniki aktualizują wiki w tej samej pracy.
- Decyzje słownikowe są delegowane i odwracalne, ale skład listy pokazujemy użytkownikowi z przykładami.

## Recommended Approach
**Lista warstwowa z SGJP i Słowosieci, opisana plikiem tematu, wydana jako pakiet „TEMATY”, tematy kolejno od matematyki.**

Składniki: D1-C + D2-B + D3-A z przeglądem R2 + D4-A z H1 + D5-A + D6-A.

**Uzasadnienie.** To jedyne zestawienie, które daje 86% i 78% pokrycia matematyki i morza bez nowych kosztów i bez szumu skojarzeń. Wynik da się odtworzyć z pliku i ADR. Warstwy zostawiają miejsce na IATE i LLM, nie zmieniając formatu.

**Co oddajemy:**
- rolnictwo zostaje niepełne do czasu pomiaru nowych korzeni;
- ok. 1/4 wpisów T2 będzie wątpliwa, a przegląd jest tylko próbkowy;
- wydanie publiczne czeka na decyzję o licencji Słowosieci 4.5.

**Założenia (jeśli są fałszywe, zmienia się rekomendacja):**
1. Tekst licencji ze slowosiec.pl obejmuje dane 4.5. Jeśli nie, zostaje D5-C (bez wydania) albo D2-A.
2. Odbiorca (bot) umie korzystać z warstw albo bierze T1–T2 razem.
3. Mapowanie lematów Słowosieci na leksemy SGJP gubi mało słów, bo 85–88% jest w BROAD v31.
4. Drugi oceniający (operator) potwierdzi trafność T2 mniej więcej na poziomie 23/30. Jeśli wyjdzie dużo niżej, T2 trzeba zawęzić (mniej relacji, więcej wykluczeń).
5. Nowe korzenie podniosą rolnictwo wyraźnie ponad 40%. Jeśli nie, pytamy o LLM (dwa potwierdzenia) albo zostaje rolnictwo bez czynności.

**Pewność: średnia.** Liczby źródeł są pewne. Trafność i pokrycie oparte są na małych próbach jednego oceniającego.

**Wymaga ADR przed wdrożeniem:** metoda tematyczna (SGJP + Słowosieć, warstwy, plik tematu), nowe źródło Słowosieć 4.5 z notą, statusy E1/E2/E3 i reguła flagi `wieloznaczny`.

## Why Not Others
- **D1-A rdzeń:** rolnictwo miałoby 0% słów oczywistych, a morze bez `kotwica` nie jest tematem. Rdzeń zostaje jako T1.
- **D1-B płaska lista:** odbiorca nie może odciąć warstwy słabszej trafności.
- **D1-D wynik ciągły:** bez LLM nie ma czym go policzyć uczciwie. Wrócimy do niego, jeśli zapadnie decyzja o E3.
- **D2-A tylko SGJP:** za mało słów (62 dla matematyki), a w rolnictwie brak słów podstawowych.
- **D2-C IATE teraz:** nie ma pomiaru trafności ani pokrycia, trzeba konta albo starego TBX, a słów pojedynczych jest mało. Warto później jako T3 dla morza.
- **D2-D LLM teraz:** to wydatek bez ceny i bez próby jakości. Najpierw sprawdzimy tańszą drogę (korzenie).
- **D2-E Słowosieć C:** połowa dodatków to szum. Lepiej wziąć same części i miejsca.
- **D3-B lista ręczna:** traci odtwarzalność, a nie przejdzie na nową bazę ani nowe wydanie.
- **D3-C korzenie automatyczne:** zmierzone domeny PWN dają 0–11%.
- **D4-B lista na bazę:** potraja pliki dla zysku, który odbiorca uzyska jednym przecięciem.
- **D4-C same lematy:** bot gra formami, więc i tak trzeba by je rozwinąć.
- **H2 usuwanie homonimów:** wycina słowa centralne (`pole`, `liczba`).
- **D5-B pakiet na temat:** powiela noty i metodę bez potrzeby.
- **D5-C bez wydania:** łamie zasadę wiki. Zostaje tylko jako plan awaryjny przy złej licencji.
- **D6-B naraz:** rolnictwo zablokowałoby lub osłabiło całość.
- **D6-C morze pierwsze:** dobry temat, ale ścieżkę taniej sprawdzić na czystszej matematyce. Różnica jest mała, więc wybór można odwrócić.
- **D6-D jeden i stop:** bramka po pilotażu w D6-A daje to samo.

## Zakres (trzy strefy)

| Strefa | Co |
|---|---|
| **W zakresie** | trzy tematy; SGJP + Słowosieć 4.5 (A + części/miejsca); plik tematu; przegląd próby; leksem ∩ STANDARD; flaga `wieloznaczny`; pakiet TEMATY; ADR; strona wiki |
| **Rozszerzenie (można odłożyć)** | warstwa IATE (T3) dla morza; nowe korzenie i jawne dodatki dla rolnictwa; drugi oceniający; kolejne tematy z promptu v3 (kulinaria, sport, muzyka, kolej…) tą samą metodą |
| **Poza zakresem** | Wikisłownik (odroczony); AGROVOC (zablokowany); Słowosieć 5.0 (kontakt z autorami); terminy wielowyrazowe; listy na poziomie znaczeń; zmiana reguł gry; użycie list w botach serwera Literaki (osobne repozytorium) |

## Deferred Ideas
- **LLM jako oceniający (E3)**, także model o otwartych wagach na Macu. Powód odłożenia: koszt i warunki wyniku. Wrócić, gdy rolnictwo po nowych korzeniach nadal będzie słabe. Dwa potwierdzenia.
- **Ranking frekwencji wewnątrz tematu (KWJP100).** Pozwoliłby botowi znać najpierw częste słowa tematu. Łączy się z poziomami wiedzy bota z promptu v3. Na razie to decyzja odbiorcy.
- **Integracja z botami Literaki** (temat jako dodatek do wiedzy bota). To osobne zadanie w repozytorium serwera.
- **Dump Kuźni z odsyłaczami słowotwórczymi.** Nie wiadomo, czy jest publiczny. Mógłby dodać pochodne terminów.
- **3/4-gramy KWJP.** Mogą trochę poprawić E1, ale E1 jest słaba.
- **EuroVoc jako zalążek lub zestaw testowy.** Jest za mały na listę, ale ma czystą licencję.
- **Niezależna lista słów testowych** od operatora, do ponownego pomiaru pokrycia.
