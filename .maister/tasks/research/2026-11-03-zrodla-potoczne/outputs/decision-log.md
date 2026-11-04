# Decyzje: źródła potoczne i świadome zmiany językowe

Data: 2026-11-04 · Zgłoszenie: #16 · Podstawa: `solution-exploration.md`, `orchestrator-state.yml` (phase-4, decision_areas) · Rozszerza szkice ADR-014–018 z [2026-11-03-zrodla-nowych-slow](../../2026-11-03-zrodla-nowych-slow/outputs/decision-log.md)

## TL;DR
- Pięć szkiców: **ADR-019 … ADR-023**, numery do potwierdzenia przy wdrożeniu. Ostatni ADR w `docs/adr/` to ADR-013. Szkice z #16 (014–018) jeszcze nie są w repo.
- Najważniejszy: **ADR-019**. Do repo idą tylko fakty, a opt-out sprawdzamy na hostach wszystkich trafień kandydata. Na nim stoją ADR-020 i ADR-021.
- **ADR-021** idzie za wyborem użytkownika (Z1), a nie za rekomendacją badania (Z2). Hasło DS wystarcza. Słowo tylko z zaimki.pl potrzebuje jednego dowodu użycia.
- Każde słowo wchodzi do list tylko decyzją użytkownika przez suplement v2 (ADR-016).

## Kluczowe decyzje
- ADR-019: polityka TDM, opt-out i publikacji (1A).
- ADR-020: warstwa potoczna, CC tylko potwierdza (4A).
- ADR-021: typ „zmiana świadoma” (Z1) i rola zaimki.pl (2A).
- ADR-022: feminatywy i neutratywy w partiach (3C).
- ADR-023: rodziny pisowni i homografy (5A).

## Otwarte pytania / ryzyka
- Numery przesuną się, jeśli ADR z #16 dostaną inne numery albo inna praca zajmie 019–023.
- Ocena prawna w ADR-019 to odczyt zbieracza, nie porada prawna (ccrawl-01).
- ADR-021 przyjmuje ryzyko słów bez zmierzonego użycia (metoda-02 § 2).
- `Content-Signal: ai-train=no`: flaga hosta czy wykluczenie? Propozycja w ADR-019: flaga. Potwierdza użytkownik.

---

<a id="adr-019"></a>
## ADR-019: Polityka TDM, opt-out i publikacji

### Status
Proponowana (wybór użytkownika 1A, 2026-11-04). Numer do potwierdzenia przy wdrożeniu.

### Kontekst
Najmocniejszy sygnał potoczny dają źródła bez licencji tekstu: napisy i sieć (synthesis W1). FineWeb-2 i HPLT mają licencję opakowania (ODC-By, CC0), ale nie tekstu (ccrawl-01). Art. 26³ pozwala liczyć lokalnie, jeśli właściciel nie zastrzegł TDM. Dziś 34 ze 100 największych hostów próbki blokuje CCBot (37,6% ich dokumentów), a 8 z 200 ma jawny tekst o TDM (ccrawl-04). Kontekst albo cytat byłby już utworem (art. 29, 34, 35).

### Czynniki decyzji
- Zgodność z art. 26³ i z decyzją z 2026-11-04 (BAN-PL wycofany, bez cytatów z tekstów bez licencji).
- Liczby w karcie muszą być już po filtrze.
- Mały koszt: rzadkie słowa mają kilka dokumentów (wulwa 2 + 2, ccrawl-02).

### Rozważane opcje
1. **1A:** fakty publiczne, opt-out na hostach wszystkich trafień kandydata.
2. 1B: lista blokad dla całej próbki (ok. 10⁵ zapytań, 332 317 hostów; ccrawl-04).
3. 1C: lista dużych hostów plus sprawdzanie hostów trafień.
4. 1D: bez liczb, tylko znacznik „potwierdzone w sieci”.

### Wynik decyzji
Wybrana opcja 1, bo daje liczby po filtrze bez skanu całej próbki i pasuje do ADR-020. Szczegóły:
- **Do repo:** liczby, lata, liczba hostów, ipm, lejek, data stanu opt-out, URL i data dokumentu dowodowego z własnym opisem.
- **Nigdy do repo:** kontekst, cytat, próbka z tekstu bez licencji.
- **Zastrzeżenie** to: robots.txt blokujący `CCBot` albo `*`, jawny tekst o TDM, TDMRep. Regulamin czytamy ręcznie przy dokumentach dowodowych. `Content-Signal: ai-train=no` zapisujemy jako flagę hosta (propozycja, do potwierdzenia).
- **Zakres:** hosty wszystkich trafień kandydata, nie tylko dokumentów dowodowych.
- **Czas:** stan w dniu pomiaru, zapisany w karcie. Drugie sprawdzenie przed wpisem do suplementu.
- **Dane:** liczymy lokalnie, plik po pliku. Kasujemy po pomiarze i ocenie znaczeń (art. 26³ ust. 3).
- **Napisy OpenSubtitles:** tylko detektor lokalny. W karcie liczba filmów (IMDb ID) i link.
- **Odłożone:** fora SpeakLeash („conditional license”) i źródła NC.

### Konsekwencje
#### Dobre
- Każda opublikowana liczba ma datę stanu opt-out.
- Repo nie zawiera tekstu z żadnego źródła bez licencji.

#### Złe
- Kontekstu nie da się sprawdzić z samego repo. Zostaje URL i własny opis.
- Lista nie nadaje się do wykrywania w CC (to wymagałoby 1B).
- Przy każdym nowym pomiarze dane trzeba pobrać ponownie.
- Moment zastrzeżenia (crawl czy nasze pobranie) jest niepewny. Przyjęto dzień pobrania (ccrawl-04).

---

<a id="adr-020"></a>
## ADR-020: Warstwa potoczna — CC tylko potwierdza

### Status
Proponowana (wybór użytkownika 4A, 2026-11-04). Numer do potwierdzenia przy wdrożeniu.

### Kontekst
Wśród nowych grup form w CC tylko ok. 4% to słowa potoczne, 45% to terminy, a 25% spam (ccrawl-03). Filtra spamu nie ma. Dla kandydata z kolejki CC daje jednak dość trafień: ekstrapolacja na całe zbiory to setki–tysiące trafień kontroli (ccrawl-02). Słowa angielskie mają szum znaczeniowy (ghosting relacyjny tylko w 2/27 i 5/45 kontekstów, ccrawl-02). Progi v2 na Leipzig: 37/43 zapożyczeń i 0/20 słów angielskich (metoda-05).

### Czynniki decyzji
- Użyć CC tam, gdzie działa (potwierdzenie, synthesis I3).
- Szum ma zostać w ocenie lokalnej, nie na liście.
- Prosta, powtarzalna reguła co kwartał.

### Rozważane opcje
1. **4A:** CC potwierdza kandydatów z kolejki, progi v2, B7 tymczasowy.
2. 4B: CC także wykrywa, z filtrem spamu (wymaga 1B).
3. 4C: najpierw kalibracja na sieci, potem karty.
4. 4D: progi v1 (26/43 zapożyczeń, metoda-05).

### Wynik decyzji
Wybrana opcja 1. Szczegóły:
- **Kolejka:** zgłoszenia ręczne, napisy (lokalnie), nowe hasła DS spoza SGJP (931 z id ≥ 226000, swiadoma-01), plebiscyty.
- **Pomiar:** próbka FineWeb-2/HPLT 1–2 mld słów po opt-out (ADR-019). Wszystkie formy z wzoru fleksji (ghosting: 9, metoda-04).
- **Progi:** v2 B1–B6. B7 tymczasowo ≥ 20 trafień i ≥ 0,05 ipm.
- **Znaczenia:** ręczna ocena kontekstów lokalnych. Do karty idzie tylko wynik „n z m”.
- **Porządki przed pierwszą kartą:** przeliczyć ghosting z 9 formami; jedna definicja B4 (dziś trzy różne, synthesis S6); jedna tabela progów hostów (synthesis S7).
- **Kalibracja** B3–B7 na pierwszych kartach, bez blokowania kolejki.
- Typ dowodu `potoczne`, kwalifikator w suplemencie pusty (ADR-016).

### Konsekwencje
#### Dobre
- Na listę nie wchodzi spam ani terminy z sieci.
- Progi są znane przed pomiarem i takie same dla każdego słowa.

#### Złe
- Potok jest tak dobry jak kolejka. Słowo, którego nikt nie zgłosi i żaden detektor nie złapie, nie wyjdzie.
- Ręczna ocena znaczeń kosztuje czas.
- Listy kalibracyjne są małe (37/43 to Wilson ok. 73–93%, metoda-05).

---

<a id="adr-021"></a>
## ADR-021: Typ „zmiana świadoma” (Z1) i rola zaimki.pl

### Status
Proponowana (wybór użytkownika 2A i decyzja o zaimki.pl, 2026-11-04). Badanie rekomendowało Z2 (2B); użytkownik wybrał Z1. Numer do potwierdzenia przy wdrożeniu.

### Kontekst
Słowa świadomej zmiany są rzadkie z definicji. Wulwa ma w CC 0,006–0,016 ipm (ccrawl-02), więc progi potoczne by ją wycięły. DS ma redagowane hasło wulwy (id 226245, dodane I–II 2024; swiadoma-01), ale wszystkie prawa zastrzeżone. zaimki.pl ma 2439 feminatywów spoza SGJP, z czego tylko 8 ma podane źródła (raport § 4.4). Licencja OQL v1.4 nie zgadza się z CC BY 4.0 list.

### Czynniki decyzji
- Wulwa to istotna zmiana językowa (D5 z #16).
- Prosta reguła, ta sama dla każdego słowa tego typu.
- Żadnych danych z OQL ani z DS w repo.

### Rozważane opcje
1. **Z1 (2A):** dowód ręczny z DS wystarcza.
2. Z2 (2B): dowód ręczny plus jeden warunek użycia: ≥ 3 w korpusie z licencją, ≥ 5 hostów i ≥ 10 trafień albo publikacja redagowana.
3. Z2 z niższym progiem hostów (2C).
4. Z3: progi potoczne B1–B7 (2D).

### Wynik decyzji
Wybrana opcja 1 (decyzja użytkownika). Szczegóły:
- **Hasło DS** wystarcza dla typu `zmiana_swiadoma`. W karcie: URL, data odczytu, id, własny opis.
- **Tezaurus DS:** tylko sygnał lokalny. W repo „jest w tezaurusie DS vX” i sha256 pliku. Bez importu.
- **zaimki.pl:** detektor. Feminatywy i neutratywy wchodzą do kolejki. W karcie URL, data, własny opis. Bez importu danych.
- **Słowo tylko z zaimki.pl** (bez hasła DS) potrzebuje **jednego niezależnego dowodu użycia**: korpus z licencją, trafienie w CC na hoście bez zastrzeżenia i spoza B8, publikacja redagowana albo dyskusja plwiki. Zapis: URL, data, własny opis.
- **Neutratywów nie odrzucamy z góry.** Przechodzą tę samą regułę i muszą mieć wzór fleksji SGJP (ADR-016).
- **RJP** to reguła klasy (URL przy klasie), nie dowód słowa.
- Karta opisuje użycie i normę, bez ocen. Pomiar CC jest opcjonalny i nie stawia progu.

### Konsekwencje
#### Dobre
- Wulwa ma pełną drogę dowodu bez czekania na pomiar ani lekturę publikacji.
- Jedna prosta reguła dla każdego słowa z hasłem DS.

#### Złe
- Jedno źródło decyduje o dowodzie. Lista może dostać słowa bez zmierzonego użycia (metoda-02 § 2).
- Łatwiej o zarzut stronniczości. Ochroną jest ta sama reguła dla każdego słowa i opis bez ocen.
- Gdy DS zmieni lub usunie hasło, dowód trzeba odnowić w kolejnym kwartale.

---

<a id="adr-022"></a>
## ADR-022: Feminatywy i neutratywy w partiach

### Status
Proponowana (wybór użytkownika 3C, 2026-11-04). Numer do potwierdzenia przy wdrożeniu.

### Kontekst
Pula jest duża: 644 hasła feminatywopodobne w DS spoza SGJP (swiadoma-01), 270 form na `-lożka` w tezaurusie DS (swiadoma-04). Część to formy ze wzoru bez użycia (synthesis W6). SGJP dodaje feminatywy pojedynczo (muralistka w 20261018, swiadoma-04). Część wspólna zaimki.pl i tezaurusa DS spoza SGJP to 122 formy (swiadoma-04).

### Czynniki decyzji
- Zasada słowo po słowie (D1-A z #16).
- Tempo większe niż karta na słowo.
- Żadna forma tylko ze wzoru nie wchodzi na listę.

### Rozważane opcje
1. 3A: słowo po słowie, każde z osobną kartą.
2. 3B: hurtem według wzoru RJP.
3. **3C:** partie ze wspólną kartą, werdykt dla każdego słowa.
4. 3D: tylko zgłoszenia ręczne.

### Wynik decyzji
Wybrana opcja 3. Szczegóły:
- **Pierwsza partia:** 122 formy (zaimki.pl ∩ tezaurus DS, bez SGJP). Obejmuje feminatywy i neutratywy.
- **Karta partii:** wspólna część (reguła RJP dla klasy, opis źródeł, wzór fleksji klasy) i jeden wiersz na słowo z dowodem i werdyktem.
- **Reguła wiersza (ADR-021):** hasło DS → przechodzi; bez hasła DS → jeden niezależny dowód użycia; bez obu → flaga `tylko-wzór`, odpada.
- **Formy częściowo w SGJP:** karta pokazuje tylko nowe formy (ministra: 4 nowe z 10; swiadoma-04).
- **Kontrola dodatnia:** psycholożka (jest w SGJP; swiadoma-05).
- Odrzucona forma wraca tylko z nowym dowodem (reguła z ADR-018).

### Konsekwencje
#### Dobre
- Szybciej niż karta na słowo, a werdykt dalej dotyczy jednego słowa.
- Forma ze wzoru bez dowodu nie wchodzi.

#### Złe
- Część form zgodnych z regułą RJP odpadnie z braku dowodu.
- Długa partia to długa sesja. Można ją podzielić na części, jak w ADR-018.

---

<a id="adr-023"></a>
## ADR-023: Rodziny pisowni i homografy

### Status
Proponowana (wybór użytkownika 5A, 2026-11-04). Numer do potwierdzenia przy wdrożeniu.

### Kontekst
SGJP przyjmuje obie pisownie, gdy obie są w użyciu (spoiler/spojler, mail/mejl; metoda-04). Pisownie różnie zmieniają grę: `boomer` dodaje 11 form, a `bumer` m1 tylko 1, bo `bumer` m3 już jest w SGJP (metoda-04). Zapisy z apostrofem, myślnikiem albo q/v/x odpadają na alfabecie gry (`cringe’owy`). `krindż` ma tylko 4 trafienia w Leipzig (metoda-05).

### Czynniki decyzji
- Każda pisownia na liście ma własny dowód.
- Próg nie zależy od liczby form w grze.
- Zgodność z praktyką SGJP.

### Rozważane opcje
1. **5A:** karta wspólna, osobny dowód i werdykt każdej pisowni.
2. 5B: jeden werdykt dla rodziny.
3. 5C: werdykt ważony wpływem na grę.

### Wynik decyzji
Wybrana opcja 1. Szczegóły:
- **Karta rodziny:** pisownie obok siebie, każda z własnym lejkiem i werdyktem.
- **Formy niegrywalne** (`cringe’owy`) liczą się tylko jako dowód, że leksem żyje. Nie wchodzą na listę.
- **Bez własnych spolszczeń.** Pisownia wchodzi tylko z własnym dowodem użycia.
- **Homograf:** pole pokazuje leksem SGJP o tej samej formie. „Nowe formy w grze” liczy formy po odjęciu SGJP. Pole tylko informuje, progu nie zmienia.
- **`cringe`:** dwa tagi, przymiotnik nieodmienny (jak `cool`) i rzeczownik n (jak `selfie`). W grze to 1 forma.

### Konsekwencje
#### Dobre
- Na liście nie ma pisowni bez użycia.
- Użytkownik widzi realny wpływ decyzji na grę.

#### Złe
- Więcej pomiarów: `krindż` i `bumer` nie mają jeszcze pomiaru w sieci.
- Pisownia z małym wpływem (1 forma) wymaga tego samego dowodu co pisownia z 11 formami.
