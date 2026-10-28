# Log decyzji: słowniki tematyczne

## TL;DR
10 decyzji, wszystkie przyjęte (wybory użytkownika z fazy 4 i jego wymogi: pokrycie z POP/POP00 oraz diagnostyka BROAD/STANDARD).
Najważniejsze: lista warstwowa T1/T2/T3 (ADR-001), metody spoza Zadania E ze statusami E1/E2/E3 (ADR-002), nowe źródła Słowosieć 4.5 i IATE 2019 z notami (ADR-003, ADR-004), raport pokrycia z POP i POP00 z diagnostyką kandydatów wobec BROAD i STANDARD (ADR-009).
Numery tu są lokalne dla tego badania. W repozytorium proponujemy dwa pliki: **repo ADR-010** „metoda tematy-v1” (ADR-001, 002, 005–010) i **repo ADR-011** „źródła Słowosieć 4.5 i IATE” (ADR-003, 004).
Progi bramki (ADR-010) są propozycją do zatwierdzenia przez operatora.

## Key Decisions
- Warstwy zamiast jednej listy; każdy wpis ma warstwę i źródło.
- E1 słaba, E2 zablokowana, E3 odroczona; zamiast nich SGJP + Słowosieć + IATE.
- Słowosieć: tylko listy lematów, nota i zastrzeżenie plWordNet, bez surowego zrzutu.
- IATE: pełny TBX 2019, bez EU Login, atrybucja „Download IATE, European Union, 2019”.
- Leksem SGJP jako jednostka, formy ∩ STANDARD, flaga `wieloznaczny`.
- Pokrycie z POP i POP00: liczba główna w leksemach, druga w formach, razem i na warstwę.
- Diagnostyka: kandydaci ∩ BROAD i ∩ STANDARD przed filtrem, bez progu; lista wydana zostaje ∩ STANDARD.

## Open Questions / Risks
- Licencja Słowosieci 4.5 przyjęta mimo noty „4.2 © 2020” i linku 404 (ADR-003).
- Trafność IATE i T2 bez skojarzeń nie są zmierzone; pilotaż to sprawdzi (ADR-010).
- Pokrycie z POP00 w leksemach równa się pokryciu z POP0 (ADR-009).
- Kandydat bez leksemu SGJP nie ma form; liczymy go osobno w lematach (ADR-009).

---

<a id="adr-001"></a>
## ADR-001: Lista warstwowa T1/T2/T3

### Status
Accepted (wybór użytkownika D1, 2026-10-27)

### Context
Źródła różnią się trafnością i zasięgiem. Etykiety SGJP są trafne (29–30/30), ale wąskie (pokrycie 27/0/23%). Słowosieć daje słowa podstawowe przy trafności ~23/30. Nie wiemy jeszcze, czy bot chce wąskiego rdzenia, czy pełnego tematu.

### Decision Drivers
- Trafność widoczna osobno dla każdego źródła.
- Odbiorca może odciąć słabszą część bez nowej budowy.
- Prompt v3: zapisuj wynik i niepewność.

### Considered Options
1. D1-A: tylko rdzeń SGJP.
2. D1-B: jedna płaska lista.
3. D1-C: warstwy T1 SGJP, T2 Słowosieć, T3 IATE i jawne dodatki.
4. D1-D: wynik ciągły 0–3 na leksem.

### Decision Outcome
Chosen option: 3 (D1-C), bo zawiera rdzeń i pełny temat w jednym pliku, a trafność każdej warstwy jest mierzona osobno. Wpis z kilku warstw dostaje najniższą (T1 < T2 < T3) i listę wszystkich źródeł; warstwy są rozłączne.

### Consequences
#### Good
- T1 to rdzeń terminów; T1–T3 to pełny temat.
- Nowe źródło (np. LLM po decyzji) dochodzi jako warstwa, bez zmiany formatu.
#### Bad
- Więcej pól w pakiecie; warstwy trzeba wyjaśnić na wiki.
- Wynik ciągły (D1-D) odłożony, bo bez LLM byłby udawany.

---

<a id="adr-002"></a>
## ADR-002: Metody spoza Zadania E i statusy E1/E2/E3

### Status
Accepted

### Context
Prompt v3 (Zadanie E) każe przetestować trzy metody: n-gramy KWJP (E1), korpus dziedzinowy z keyness (E2), LLM jako oceniający (E3). Badanie zrobiło pilotaż E1 i opis E3. Nie znalazło korpusu dla E2. Etykiety SGJP, drzewa Słowosieci i IATE są poza listą Zadania E.

### Decision Drivers
- Prompt v3: metodę bez korpusu oznacz jako zablokowaną lub odroczoną.
- Raportuj jakość próbek, nie tylko liczbę etykiet.
- Zakaz wydatków bez dwóch potwierdzeń.

### Considered Options
1. Trzymać się tylko E1–E3.
2. Metody spoza listy z ADR i zapisanymi statusami E1–E3.
3. Odłożyć tematy do decyzji o LLM.

### Decision Outcome
Chosen option: 2, bo E1 dała głównie szum (odzysk 9/3/3 słów testowych), E2 nie ma korpusu, a E3 to wydatek bez ceny. Statusy: **E1 — słaba** (wynik pilotażu), **E2 — zablokowana** (brak korpusu spełniającego warunki; KWJP½M i NKJP 1M za małe), **E3 — odroczona** (dwa potwierdzenia kosztu). Rodziny słowotwórcze: słabe, nie wdrażamy.

### Consequences
#### Good
- Metoda ma podstawę w pomiarze, a odejście od promptu jest jawne.
- E3 można włączyć później jako warstwę.
#### Bad
- Słowa poza drzewami (np. `orka`, `obora`) wymagają ręcznych dodatków.

---

<a id="adr-003"></a>
## ADR-003: Słowosieć 4.5 jako źródło T2

### Status
Accepted (licencję przyjął użytkownik, D2)

### Context
Słowosieć daje największy przyrost słów podstawowych (morze C 59%, matematyka 86%). Licencja plWordNet pozwala rozpowszechniać pochodne z notą copyright i zastrzeżeniem. Link licencji w repozytorium CLARIN-PL zwraca 404, nota na stronie mówi „plWordNet 4.2 © 2020”, zip 4.5 nie ma LICENSE. Zrzut 4.5 zawiera nazwiska redaktorów (`owner`) i log IP.

### Decision Drivers
- Pokrycie słów podstawowych.
- Warunki licencji i ochrona danych osobowych w zrzucie.
- Odtwarzalność (wynik zależy od wydania: matematyka A 558 w 4.2, 431 w 4.5).

### Considered Options
1. Słowosieć 4.5: hiponimia (rel. 11) + części i miejsca (rel. 25, 27).
2. Jak 1 + skojarzenia (rel. 108, 146).
3. Domeny Princeton WordNet po mapowaniu (B1/B2).
4. Bez Słowosieci.

### Decision Outcome
Chosen option: 1, bo skojarzenia są w połowie szumem (C − A 16/8/10 na 30), a domeny PWN dają 0–11% dla morza. Warunki: wydanie 4.5 przypięte hashem zipa i bazy SQLite; nota i zastrzeżenie plWordNet w `ATTRIBUTIONS.md`; publikujemy tylko lematy; surowego zrzutu, tabel `owner` i logu IP nie kopiujemy do pakietu ani repozytorium; bez nazwy Politechniki Wrocławskiej w reklamie. Niejasność wersji licencji idzie do `LIMITATIONS.md`.

### Consequences
#### Good
- Słowa podstawowe (`kotwica`, `maszt`, `żagiel`) w temacie.
#### Bad
- Ryzyko licencyjne zostaje (wersja noty).
- Korzenie wybiera człowiek; wynik zależy od korzeni.

---

<a id="adr-004"></a>
## ADR-004: IATE pełny TBX 2019 jako źródło T3

### Status
Accepted (wybór użytkownika D2)

### Context
Licencja pliku pobrania IATE pozwala kopiować i przerabiać, także komercyjnie, z atrybucją. Plik z filtrami wymaga konta EU Login. Stary pełny TBX (`IATE_download.zip`, 112,8 MB, 30.09.2019) jest bez logowania. Słowa pojedyncze to 7–21% haseł.

### Decision Drivers
- Zakaz kontaktu i zakładania kont u autorów źródeł.
- Terminy morskie (`cuma`, `kilson`, `szpigat`) brakujące w innych źródłach.

### Considered Options
1. Pełny TBX 2019 bez logowania.
2. Aktualny plik z filtrami (EU Login).
3. API IATE (token = kontakt).
4. Bez IATE.

### Decision Outcome
Chosen option: 1, bo jest jedyną drogą bez konta i kontaktu. Bierzemy polskie terminy jednowyrazowe typu „term” z kodów dziedzin w konfiguracji tematu (np. 4821), z filtrem niezawodności (propozycja ≥ 3). Atrybucja: „Download IATE, European Union, 2019”. Plik przypięty SHA-256 w manifeście źródeł.

### Consequences
#### Good
- Czysta licencja; terminy fachowe w T3.
#### Bad
- Dane sprzed 7 lat; trafność niezmierzona.
- Dziedzina 4821 obejmuje żeglugę śródlądową; może wymagać wykluczeń.

---

<a id="adr-005"></a>
## ADR-005: Temat = plik konfiguracji; przegląd R2

### Status
Accepted (wybór użytkownika D3)

### Context
Temat leży w wielu gałęziach drzewa (`sztorm` < `wiatr`, `ciągnik` < `pojazd mechaniczny`). Korzenie trzeba wybrać ręcznie. Ocena trafności w badaniu pochodziła od jednego oceniającego.

### Decision Drivers
- Odtwarzalność i nowy temat bez kodu.
- Drugi oceniający przy rozsądnym nakładzie.

### Considered Options
1. D3-A: plik konfiguracji na temat (atomy, korzenie z id i nazwą, relacje, wykluczenia, dodatki, kody IATE).
2. D3-B: lista ręczna po jednorazowym generowaniu.
3. D3-C: korzenie automatyczne.
Przegląd: R1 (tylko agent), R2 (agent 50 na warstwę, operator 30 z nich), R3 (pełny).

### Decision Outcome
Chosen option: 1 z przeglądem R2, bo wynik da się odtworzyć, a operator gra w Literaki i dobrze ocenia słowa. Nieznane pole, zła relacja albo nazwa synsetu niezgodna z id to błąd budowy. Dodatki muszą być w bazie. Poprawki idą przez konfigurację, nie przez ręczną edycję listy. Próby są deterministyczne (ziarno w `method.json`). Zapisujemy trafność obu oceniających i zgodność.

### Consequences
#### Good
- Zmiana tematu jest widoczna w historii pliku.
- Ocena ma drugiego oceniającego.
#### Bad
- Długie listy wykluczeń mogą ukryć słabość źródła; raport podaje ich liczbę.
- Przegląd jest próbkowy (ok. 1/4 T2 może być wątpliwa).

---

<a id="adr-006"></a>
## ADR-006: Jednostka: leksem SGJP; formy ∩ STANDARD

### Status
Accepted (wybór użytkownika D4)

### Context
Prompt v3: klasyfikuj leksemy, potem dołącz formy; temat musi być podzbiorem słownika przy stole. Słowosieć i IATE dają lematy, nie leksemy SGJP. 85–88% nowych lematów Słowosieci jest w BROAD v31.

### Decision Drivers
- Temat ⊆ STANDARD.
- Jedna lista na temat.

### Considered Options
1. D4-A: leksem SGJP, formy ∩ STANDARD.
2. D4-B: osobna lista na każdą bazę.
3. D4-C: same lematy.

### Decision Outcome
Chosen option: 1. Lemat + część mowy mapujemy na leksemy SGJP z przebiegu v31 FROZEN. Kandydat bez leksemu w bazie odpada z powodem w raporcie. Kwalifikatory SGJP dzielimy najpierw po `|`, potem po `,` (obecne ładowanie leksemów POP dzieli tylko po `,`). Odbiorca sam przecina z POP/POP0/POP00.

### Consequences
#### Good
- Zgodne z promptem v3; temat nigdy nie rozszerza dopuszczalności.
#### Bad
- Dla BROAD odbiorca musi przeciąć sam.
- Mapowanie lematu na kilka leksemów SGJP tworzy homonimy (ADR-007).

---

<a id="adr-007"></a>
## ADR-007: Reguła `wieloznaczny`

### Status
Accepted (wybór użytkownika H1)

### Context
Każde źródło przypisuje temat lematowi przez jedno znaczenie (`kiosk`, `kot`, `pole`, `orka`). Bot gra napisem, nie znaczeniem. Prompt v3: etykieta tematyczna nie oznacza, że każde użycie słowa dotyczy tematu.

### Decision Drivers
- Nie wycinać słów centralnych (`pole`, `liczba`).
- Uczciwy zapis niepewności.

### Considered Options
1. H1: oznaczyć flagą i zapisać znaczenie źródłowe.
2. H2: usunąć wszystkie wieloznaczne.
3. H3: lista na poziomie znaczeń.

### Decision Outcome
Chosen option: 1. Wpis dostaje `wieloznaczny = tak`, gdy (a) jego lemat ma w Słowosieci jednostkę w synsecie spoza domknięcia tematu albo (b) lemat i część mowy wskazują więcej niż jeden leksem SGJP. `nie`, gdy lemat jest w Słowosieci i wszystkie jego znaczenia leżą w temacie. `brak danych`, gdy lematu nie ma w Słowosieci (często T1 i T3). Znaczenie źródłowe: id i nazwa synsetu (T2), atom SGJP (T1), id hasła i kod dziedziny IATE (T3). Przegląd może wykluczyć wpis przez konfigurację.

### Consequences
#### Good
- Słowa centralne zostają; odbiorca może je odfiltrować flagą.
#### Bad
- Wiele wpisów T1/T3 będzie miało „brak danych”.
- Flaga nie mówi, które znaczenie jest częstsze.

---

<a id="adr-008"></a>
## ADR-008: Jeden pakiet TEMATY i jedna strona wiki

### Status
Accepted (wybór użytkownika D5)

### Context
Wzór POP00: osobna podkomenda, konfiguracja, pakiet z `method.json`, `LIMITATIONS.md`, `ATTRIBUTIONS.md` i manifestem z hashami. AGENTS.md: praca bez wiki jest nieskończona; nowy słownik dostaje stronę „W przygotowaniu” na starcie.

### Decision Drivers
- Jedna metoda i jedna nota licencyjna dla wszystkich tematów.
- Zasada wiki.

### Considered Options
1. D5-A: jeden pakiet TEMATY, plik na temat.
2. D5-B: pakiet na temat.
3. D5-C: tylko artefakt roboczy.

### Decision Outcome
Chosen option: 1. Podkomenda obok `pop` i `pop00`; pakiet w nowym katalogu, bez nadpisywania; manifest z liczbami i hashami; stany BUILT i REVIEWED. Strona wiki `Slownik-TEMATY` powstaje „W przygotowaniu” na starcie prac.

### Consequences
#### Good
- Nowy temat to nowy plik w pakiecie i wiersz na wiki.
#### Bad
- Zmiana jednego tematu daje nową wersję całego pakietu.

---

<a id="adr-009"></a>
## ADR-009: Raport pokrycia z POP i POP00; diagnostyka BROAD i STANDARD

### Status
Accepted (dwa wymogi użytkownika, 2026-10-27)

### Context
Użytkownik chce wiedzieć, ile każdego tematu jest w POP i POP00, czyli jak bardzo jest „grywalny” dla bota na mniejszym słowniku. D4 zostaje: pliki tematu nie są przecinane z POP. POP i POP0 wybierają leksemy (`reports/units.json` pakietu pop-v3). POP00 dziedziczy leksemy POP0, każdy zachowuje formę, i ogranicza tylko formy (ADR-009 projektu). Drugi wymóg: słowo spoza STANDARD (albo BROAD) jest na końcu bezużyteczne, więc chcemy wiedzieć, ilu kandydatów źródła odpada.

### Decision Drivers
- Tania, czytelna miara przydatności tematu i każdej warstwy.
- Jednostka zgodna ze sposobem budowy POP.
- Odtwarzalność (wersje POP, POP00, BROAD i STANDARD przypięte).
- Miara przed filtrem, bo po ∩ STANDARD udział STANDARD to zawsze 100%.

### Considered Options
1. Udział w leksemach jako liczba główna, formy obok.
2. Udział w formach jako liczba główna.
3. Osobne pliki tematu ∩ POP / ∩ POP00 (D4-B).
4. Dla BROAD/STANDARD: miara po filtrze (trywialna) albo przed filtrem (diagnostyczna).

### Decision Outcome
Chosen option: 1, bo POP/POP0 i Zadanie E działają na leksemach, a udział w formach zależy od wielkości paradygmatu (czasownik waży kilka razy więcej niż rzeczownik). Dla każdego tematu, całości i warstw T1/T2/T3 (rozłącznych) podajemy: |temat|, |temat ∩ POP|, |temat ∩ POP00| oraz udziały |temat ∩ X| / |temat|, w leksemach i w formach. Leksem w POP00 = członek POP0. Forma w POP/POP00 = napis na liście form pakietu. Miejsca: manifest (`counts.<temat>.overlap`), raport podsumowania, strona wiki (tabela na temat), raport bramki. Manifest źródeł przypina SHA-256 manifestu pop-v3 (`4acb7014…1d58`) i pop00-v1; pakiet TEMATY je powtarza.

**Diagnostyka BROAD i STANDARD (opcja 4, przed filtrem).** Na zbiorze kandydatów po mapowaniu, przed ∩ STANDARD, dla każdego tematu, razem i T1/T2/T3: |kandydaci|, |∩ BROAD|, |∩ STANDARD| i udziały, w leksemach (liczba główna) i formach. Leksem jest w X, gdy ma formę na liście X. Odrzuceni: liczba i do 10 przykładów na powód i warstwę (`BRAK_LEKSEMU` w lematach, poza udziałami; `POZA_BROAD`; `POZA_STANDARD`). Miejsca: `reports/summary.json`, raport bramki, jedno zdanie na wiki. Bez progu. Manifest źródeł przypina przebieg v31 i listy BROAD i STANDARD (`dab4f3bc…fa7d`) hashami. Lista wydana zostaje ∩ STANDARD.

### Consequences
#### Good
- Operator widzi od razu, która warstwa jest grywalna.
- Bez nowych plików list; D4 bez zmian.
- Widać, które źródło i warstwa marnują najwięcej kandydatów (np. IATE spoza BROAD).
#### Bad
- Udział POP00 w leksemach równa się udziałowi POP0; informację niesie liczba w formach. Trzeba to napisać na wiki.
- Nowe wydanie POP, POP00 albo przebiegu bazy zmienia liczby; wymaga nowej budowy pakietu.
- `BRAK_LEKSEMU` liczony w lematach nie sumuje się z leksemami; raport musi to pokazać osobno.

---

<a id="adr-010"></a>
## ADR-010: Pilotaż morze i bramka

### Status
Accepted (wybór użytkownika D6; progi to propozycja)

### Context
Morze ćwiczy wszystkie trzy warstwy, także IATE (≥1155 haseł PL, kod 4821). Ma największy rdzeń SGJP z pierwszych tematów (254 leksemy) i pokrycie 78% w badaniu (SGJP ∪ Słowosieć C). Matematyka nie ćwiczy dobrze IATE (≥87 haseł).

### Decision Drivers
- Sprawdzić całą ścieżkę na jednym temacie przed falą.
- Jasne kryteria „dalej / popraw / stop”.

### Considered Options
1. Matematyka najpierw (D6-A).
2. Morze najpierw, potem bramka (D6-C).
3. Wszystkie naraz.

### Decision Outcome
Chosen option: 2, bo tylko morze sprawdza T3. Proponowane progi bramki: pokrycie 37 słów oczywistych ≥ 70%; trafność operatora T1 ≥ 27/30, T2 ≥ 20/30 (≤ 3 błędne), T3 ≥ 20/30; zgodność agent–operator ≥ 80%; dwie budowy z identycznymi hashami; noty obecne, brak danych redaktorów i IP. Raportujemy bez progu: pokrycie z POP i POP00, diagnostykę kandydatów wobec BROAD i STANDARD przed filtrem (ADR-009) i udział `wieloznaczny` z przykładami. Po bramce operator zatwierdza ok. 10 tematów (propozycja: zwierzęta, rośliny, morze, medycyna i ciało, muzyka, kuchnia, sport, matematyka, pogoda, grzyby; rolnictwo po lepszych korzeniach).

### Consequences
#### Good
- Błąd metody wychodzi na jednym temacie.
- IATE sprawdzone od razu.
#### Bad
- Morze ma więcej szumu niż matematyka; pilotaż jest trudniejszy.
- Progi pochodzą z pomiaru jednego oceniającego; mogą wymagać korekty.
