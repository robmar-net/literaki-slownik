# Warianty rozwiązań: słowa potoczne i świadome zmiany językowe

Zadanie: `2026-11-03-zrodla-potoczne` (#16) · Data: 2026-11-04 · Pewność rekomendacji: średnia

## TL;DR
- **Wniosek: sieć i napisy tylko potwierdzają słowo z kolejki, nie wykrywają go.** Do repo idą liczby, URL, data i własny opis. Tekst nie idzie nigdy.
- 5 obszarów, 19 wariantów. Rekomendacja: **1A + 2B + 3C + 4A + 5A**.
- 1A: liczymy lokalnie, publikujemy fakty. Opt-out sprawdzamy na hostach trafień kandydata, w dniu pomiaru.
- 2B: Z2 z obecnymi progami, ustalonymi **przed** pomiarem kandydatów, jednymi dla każdego słowa tego typu. DS daje dowód ręczny, tezaurus DS jest tylko sygnałem.
- 3C: feminatywy przeglądamy w partiach, ale werdykt zapada dla każdego słowa osobno. Słowo bez użycia odpada.
- 4A: progi v2 na start, B7 tymczasowo. CC tylko potwierdza, na próbce 1–2 mld słów, z ręcznym filtrem znaczeń.
- 5A: każda pisownia ma osobny werdykt, a karta jest wspólna. `cringe` dostaje oba tagi.

## Kluczowe decyzje
- **1A.** Liczby, lata i liczba hostów z CC, a przy dokumentach dowodowych tylko URL, data i własny opis. Napisy działają tylko jako lokalny detektor; w karcie podajemy liczbę filmów i link. Fora SpeakLeash i źródła NC odkładamy. Powód: art. 26³ i decyzja z 2026-11-04 (ccrawl-01, ccrawl-04, potoczne-02).
- **2B.** Z2 = DS + jeden z warunków (a) ≥3 użycia w korpusie z licencją, (b) ≥5 hostów i ≥10 trafień, (c) publikacja redagowana. Progów nie stroimy pod wulwę (metoda-02).
- **3C.** Partie z puli DS ∩ zaimki.pl (122 formy, swiadoma-04). Dla podklasy (a) obowiązuje ten sam warunek użycia co w Z2. Forma, którą znamy tylko z list, odpada.
- **4A.** Kolejka powstaje z detektorów: zgłoszeń ręcznych, napisów, nowych haseł DS i plebiscytów. CC liczy tylko kandydatów. Wykrywanie w CC odpada, bo potocznych jest tam ok. 4% (ccrawl-03).
- **5A.** Osobny werdykt dla każdej pisowni (R1 w metoda-04). Pole „nowe formy w grze” informuje użytkownika, ale progu nie zmienia.

## Otwarte pytania / ryzyka
- Ocena prawna to odczyt zbieracza, a nie porada prawna. Nie wiadomo, czy art. 26³ liczy stan opt-out z dnia crawla, czy z dnia naszego pobrania. Przyjmujemy dzień pobrania (ccrawl-04).
- Wulwa nie spełnia Z2(b): ma 6 trafień, a próg to 10 (ccrawl-02). Zostaje warunek (c), ale tekstów cytowanych w DS nikt nie przeczytał. Jeśli (c) odpadnie, wulwa czeka, a progu nie obniżamy.
- Czy podklasa (b) mieści się w zasadach dopuszczalności Kurnika? To decyzja użytkownika (swiadoma-05).
- Liczby z sieci są wstępne. Policzono je przed filtrem opt-out, a ghosting na 4 formach zamiast 9 (synthesis S2, S4).
- `krindż` i `bumer` nie mają pomiaru w sieci. Jest tylko Leipzig: krindż 4 trafienia (metoda-05).

---

## Problem
### Pytanie badawcze
Skąd literaki-slownik ma brać wiarygodne dowody na słowa potoczne, internetowe i świadome zmiany językowe, których nie widać w PPC, ParlaMint i Leipzig (planning/research-brief.md)?

### Pytania „jak moglibyśmy” (HMW)
1. Jak liczyć źródła bez licencji tekstu, nie publikując tekstu i szanując opt-out?
2. Jak dopuścić rzadkie słowa celowe, nie wpuszczając słów bez użycia i nie biorąc strony w sporach?
3. Jak obsłużyć dużą pulę feminatywów, nie wpuszczając form tylko ze wzoru?
4. Jak zbudować potok potoczny, który odróżnia potoczność od spamu i innych znaczeń?
5. Jak decydować o pisowniach i homografach, gdy w grze zmieniają one bardzo różną liczbę form?

Punkty stałe (nie podważamy): suplement v2 w miejscu v1, SGJP 20261018 osobno, miara g poza buildem w nowym ADR, PPC + ParlaMint + Leipzig poza buildem, rytm kwartalny z PPC, karta kandydata i decyzja użytkownika przed wejściem do list (badanie `2026-11-03-zrodla-nowych-slow`, phase_4_decisions). BAN-PL jest wycofany. Cytaty z tekstów bez licencji nie trafiają do repo. Historii Git nie przepisujemy.

---

## Obszar 1. Polityka prawna źródeł bez licencji tekstu (D1, D3, D12)

### 1A. Fakty publiczne, opt-out na hostach trafień kandydata (rekomendacja)
Liczymy lokalnie (art. 26³ ust. 1) tylko dla kandydatów z kolejki i kasujemy dane po pomiarze (ust. 3). Przed zapisem liczb sprawdzamy opt-out na hostach **wszystkich** dokumentów z trafieniem, nie tylko dokumentów dowodowych. Sprawdzamy robots.txt (CCBot albo `*`), jawny tekst o TDM, TDMRep, a regulamin czytamy ręcznie przy dokumentach dowodowych. Hosty z zastrzeżeniem odrzucamy. W karcie zostają liczby, lata, liczba hostów, data sprawdzenia oraz URL i data z własnym opisem.
- **Plusy:** mało zapytań, bo rzadkie słowa mają kilka dokumentów (wulwa 2+2 dok., ccrawl-02). Liczby w karcie są już po filtrze. Wszystko mieści się w decyzji z 2026-11-04.
- **Minusy:** z samego repo nie da się sprawdzić kontekstu. Lista nie nadaje się do wykrywania (pełnego skanu).
- **Kiedy najlepsza:** CC tylko potwierdza (4A).
- **Dowody:** ccrawl-01 (tabela czynności), ccrawl-04 („lżejsza ścieżka”), F3, F4.

### 1B. Lista blokad dla całej próbki przed każdym liczeniem
Robimy jednorazową listę hostów z zastrzeżeniem dla całej próbki (ok. 10⁵ zapytań, ccrawl-04) i wykluczamy ich dokumenty z każdego liczenia. Publikujemy to samo co w 1A.
- **Plusy:** wszystkie liczby są czyste, także w skanie wykrywającym.
- **Minusy:** praca na dużą skalę. Lista starzeje się, bo opt-out rośnie po crawlu (W8). Próbka ma 332 317 hostów (ccrawl-04).
- **Kiedy najlepsza:** gdy CC ma też wykrywać (4B).
- **Dowody:** ccrawl-04, W8.

### 1C. Lista blokad dla dużych hostów i sprawdzanie hostów trafień
Blokujemy z góry hosty z czołówki (100 największych ma 11,0% dokumentów, 34 z nich blokuje CCBot; ccrawl-04), a resztę sprawdzamy jak w 1A.
- **Plusy:** tanio odcina dużą część zastrzeżonego tekstu, zanim cokolwiek policzymy.
- **Minusy:** to dwa mechanizmy zamiast jednego. Przy kandydatach daje mało ponad 1A.
- **Kiedy najlepsza:** gdy liczymy wielu kandydatów naraz.
- **Dowody:** ccrawl-04.

### 1D. Bez liczb: tylko znacznik „potwierdzone w sieci”
Z CC i napisów publikujemy tylko tak lub nie oraz datę.
- **Plusy:** najmniejsze ryzyko prawne.
- **Minusy:** traci się progi B6/B7, Z2(b) i kalibrację. Karty nie da się porównać między słowami.
- **Kiedy najlepsza:** gdyby publikacja liczb z TDM okazała się zakazana.
- **Dowody:** ccrawl-01 (liczby to „niskie ryzyko”, nie zero).

**Wspólne dla wszystkich wariantów:**
- OpenSubtitles służy tylko jako detektor lokalny; w karcie liczba filmów (IMDb ID) i link (D1, potoczne-03).
- Fora SpeakLeash mają „conditional license” i słaby sygnał, więc je odkładamy (potoczne-02).
- Źródła NC odkładamy (D12).
- Moment zastrzeżenia: stan w dniu pomiaru, zapisany w karcie. Przed wpisem w przeglądzie kwartalnym sprawdzamy go ponownie (ccrawl-04).

**Rekomendacja: 1A.** Pasuje do 4A i daje liczby po filtrze bez skanu całej próbki.

---

## Obszar 2. Próg dowodu dla typu „zmiana świadoma” (D4, D5, D6)

### 2A. Z1: wystarczy dowód ręczny z DS
- **Plusy:** proste. Wulwa przechodzi od razu.
- **Minusy:** jedno źródło decyduje. Lista może dostać słowa bez użycia. Łatwiej o zarzut stronniczości.
- **Dowody:** metoda-02 § 2.

### 2B. Z2 z obecnymi warunkami, ustalonymi z góry (rekomendacja)
Dowód ręczny (DS: URL, data, id i własny opis) plus jeden warunek: (a) ≥3 użycia w korpusie z licencją, (b) ≥5 niezależnych hostów i ≥10 trafień po B1–B5 i po opt-out albo (c) publikacja redagowana. Wartości zatwierdzamy, **zanim** zmierzymy 8 kandydatów (swiadoma-04). Hosty DS i podobnych słowników wyklucza B8.
- **Plusy:** słowo opisuje użycie. Próg jest niski, ale niezależny. Próg ustalony przed pomiarem chroni neutralność.
- **Minusy:** trzeba mierzyć każdego kandydata. Wulwa zależy dziś od (c), czyli od lektury, której nie zrobiono (I1).
- **Dowody:** metoda-02, ccrawl-02 (wulwa: 6 hostów, 6 trafień), swiadoma-01.

### 2C. Z2 z niższym warunkiem (b): ≥5 hostów, bez progu trafień
- **Plusy:** wulwa przechodzi bez warunku (c).
- **Minusy:** próg ustawiony pod jedno słowo. Wygląda na branie strony i podważa neutralność. Pięć hostów to mało przy spamie (ccrawl-03).
- **Dowody:** ccrawl-02, metoda-02 (ryzyko polityczne).

### 2D. Z3: progi potoczne B1–B7
- **Plusy:** jeden mechanizm.
- **Minusy:** wycina cel. Wulwa ma 0,006–0,016 ipm wobec ≥0,05 (I1).
- **Dowody:** ccrawl-02, metoda-01.

**Role źródeł (w każdym wariancie):**

| Źródło | Rola | Do repo |
|---|---|---|
| DS (prawa zastrzeżone) | dowód ręczny | URL, data, id, własny opis |
| tezaurus DS (GPL/LGPL) | sygnał lokalny do kolejki, bez importu (D5) | „jest w tezaurusie DS vX” + SHA256 |
| zaimki.pl (OQL v1.4) | nie używać w repo (D6) | nic |
| RJP | reguła klasy, nie dowód słowa | URL przy klasie |

**Neutralność:**
- Jeden próg dla każdego słowa tego typu, niezależnie od środowiska, z którego słowo pochodzi.
- Karta opisuje użycie i normę, bez ocen.
- Podklasy (c), czyli form normatywnych bez użycia, nie dodajemy.

**Rekomendacja: 2B.** Jeśli (c) nie potwierdzi wulwy, wulwa czeka na kolejny kwartał. Progu nie zmieniamy.

---

## Obszar 3. Feminatywy i formy systemowe (D11)

### 3A. Słowo po słowie, z kolejki jak każde inne
- **Plusy:** to dokładnie D1-A i tak działa SGJP (muralistka w 20261018, swiadoma-04).
- **Minusy:** pula jest duża (644 hasła feminatywopodobne w DS spoza SGJP, swiadoma-01), więc praca idzie wolno.
- **Dowody:** swiadoma-05 S3.

### 3B. Hurtem według wzoru RJP dla zawodów z SGJP
- **Plusy:** szybko. Ma uzasadnienie w regule RJP 2019.
- **Minusy:** do listy wchodzą formy bez użycia (angelolożka; 270 form na `-lożka` w tezaurusie, swiadoma-04). Łamie D1-A.
- **Dowody:** swiadoma-04, W6.

### 3C. Partie z wspólną kartą, osobny werdykt i próg użycia (rekomendacja)
Pulę DS ∩ zaimki.pl (122 formy, swiadoma-04) przeglądamy w partiach. Każde słowo musi spełnić ten sam warunek użycia co w Z2. Forma, którą widać tylko w listach (tezaurus, DS, zaimki.pl), dostaje flagę `tylko-wzór` i odpada.
- **Plusy:** tempo większe niż w 3A, a zasada pozostaje słowo po słowie. Jeden próg dla (a) i (b).
- **Minusy:** każde słowo wymaga pomiaru. Część zgodna z regułą RJP odpadnie z braku użycia.
- **Dowody:** swiadoma-04, swiadoma-05, I5.

### 3D. Tylko feminatywy zgłoszone ręcznie, bez przeglądu puli
- **Plusy:** najmniej pracy.
- **Minusy:** pomija najmocniejszą pulę. Wynik zależy od tego, kto zgłasza.
- **Dowody:** I5.

**Jak odsiać formy ze wzoru (dla 3A i 3C):**
- Lista (tezaurus, zaimki.pl) to tylko detektor.
- Dowód użycia musi pochodzić spoza hostów B8.
- Kontrolą dodatnią jest psycholożka (swiadoma-05).
- Przy formach, które SGJP częściowo już ma, karta pokazuje tylko nowe formy (ministra: 4 nowe z 10, swiadoma-04).

**Rekomendacja: 3C.** Pasuje do rekomendacji D11 („słowo po słowie”) i do 2B.

---

## Obszar 4. Potok potoczny (D9)

### 4A. CC potwierdza, progi v2, B7 tymczasowy (rekomendacja)
- **Kolejka:** zgłoszenia ręczne, napisy (lokalnie), nowe hasła DS spoza SGJP (931 z id ≥226000, swiadoma-01) i plebiscyty.
- **Pomiar:** CC na próbce 1–2 mld słów po opt-out (1A), z formami z pełnego wzoru (ghosting 9).
- **Filtr znaczeń:** ręczna ocena lokalnych kontekstów (ghosting w znaczeniu relacyjnym tylko w 2/27, ccrawl-02).
- **Progi:** v2 B1–B6. B7 tymczasowo: ≥20 trafień i ≥0,05 ipm.
- **Plusy:** wykorzystuje to, w czym CC jest dobre (I3). Szum zostaje w lokalnej ocenie, a nie na liście.
- **Minusy:** potok zależy od jakości kolejki. Ręczna ocena znaczeń kosztuje czas.
- **Dowody:** ccrawl-02, ccrawl-03, metoda-05 (37/43 i 0/20 przy v2).

### 4B. CC także wykrywa, z automatycznym filtrem spamu
- **Plusy:** znajduje słowa, których nikt nie zgłosił.
- **Minusy:** potocznych jest ok. 4%, a spamu i zlepków ok. 40% (ccrawl-03). Filtra spamu nie ma. Wymaga 1B.
- **Dowody:** ccrawl-03, W7.

### 4C. Najpierw kalibracja na sieci, potem karty
Do czasu próbki 1–2 mld słów po opt-out i ponownego ustalenia B3–B7 na celach nie wydajemy żadnej karty potocznej.
- **Plusy:** progi są pewniejsze. Listy kalibracyjne są dziś małe (37/43, Wilson ok. 73–93%, metoda-05).
- **Minusy:** opóźnienie. Kalibracji i tak nie da się zrobić bez kandydatów.
- **Dowody:** metoda-05, ccrawl-02.

### 4D. Progi v1 (ostrzejsze)
- **Plusy:** mniej fałszywych alarmów.
- **Minusy:** wycina prawdziwe zapożyczenia (v1: 26/43, metoda-05), w tym boomer.
- **Dowody:** metoda-05.

**Co zrobić w każdym wariancie:**
- przeliczyć ghosting z 9 formami;
- ujednolicić filtr angielski B4;
- spisać jedną tabelę progów hostów (B6 ≥10, Z2(b) ≥5; synthesis S2, S6, S7).

**Rekomendacja: 4A.** Kalibrację z 4C robimy na pierwszych kartach i nie blokujemy nią kolejki.

---

## Obszar 5. Pisownie i homografy (D7, D8)

### 5A. Karta wspólna, osobny werdykt dla każdej pisowni (rekomendacja)
`boomer` i `bumer` oraz `cringe` i `krindż` mają jedną kartę rodziny i osobne bramki oraz werdykty (R1). Pisownia niegrywalna (`cringe’owy`) liczy się tylko jako dowód, że leksem żyje (R3). Spolszczeń z reguły nie tworzymy.
- **Plusy:** zgodne z SGJP (spoiler/spojler, metoda-04). Każda pisownia ma własny dowód.
- **Minusy:** więcej pomiarów (krindż i bumer bez pomiaru w sieci).
- **Dowody:** metoda-04 § 3.

### 5B. Jeden werdykt dla całej rodziny pisowni
- **Plusy:** jedna decyzja zamiast kilku.
- **Minusy:** wpuszcza pisownię bez użycia, a SGJP tak nie robi.
- **Dowody:** metoda-04.

### 5C. Werdykt ważony wpływem na grę
Przy małym wpływie (`bumer` m1 daje 1 nową formę, `boomer` 11; metoda-04) stosujemy uproszczony przegląd.
- **Plusy:** szybciej przy homografach.
- **Minusy:** obniża dowód zależnie od liczby form. Z czasem to rozmywa zasady.
- **Dowody:** metoda-03, metoda-04, I4.

**Rodzaj `cringe` (D7):** dwa tagi: przymiotnik nieodmienny (jak `cool`) i rzeczownik n (jak `selfie`). Alternatywy: tylko adj albo tylko n. W grze to w każdym przypadku 1 forma (metoda-04), więc tagi wpływają na opis, nie na grę.

**„Nowe formy w grze”:** pole tylko informuje. Użytkownik widzi, że decyzja o `bumer` zmienia 1 formę, ale próg dowodu jest ten sam.

**Rekomendacja: 5A** i dwa tagi dla `cringe`.

---

## Analiza kompromisów (5 perspektyw)
Skala: W = wysoka (dobrze), Ś = średnia, N = niska. Przy ryzyku W oznacza **niskie** ryzyko.

| Wariant | Wykonalność | Wpływ na grę i użytkownika | Prostota | Ryzyko (W = małe) | Skala |
|---|---|---|---|---|---|
| **1A** | W | Ś | W | W | Ś |
| 1B | Ś | Ś | N | W | W |
| 1C | Ś | Ś | Ś | W | Ś |
| 1D | W | N | W | W | N |
| 2A | W | Ś | W | N | W |
| **2B** | Ś | W | Ś | W | Ś |
| 2C | Ś | Ś | Ś | N | Ś |
| 2D | W | N | W | Ś | W |
| 3A | W | Ś | W | W | N |
| 3B | W | Ś | W | N | W |
| **3C** | Ś | W | Ś | W | Ś |
| 3D | W | N | W | Ś | N |
| **4A** | Ś | W | Ś | W | Ś |
| 4B | N | Ś | N | N | W |
| 4C | Ś | N | Ś | W | Ś |
| 4D | W | N | W | Ś | Ś |
| **5A** | Ś | W | Ś | W | Ś |
| 5B | W | Ś | W | N | Ś |
| 5C | W | Ś | Ś | N | Ś |

Główny kompromis: rekomendowane warianty płacą prostotą i skalą (więcej ręcznej pracy na słowo) za mniejsze ryzyko prawne i za neutralność.

## Preferencje użytkownika
- 2026-11-04: BAN-PL wycofany. Cytatów z tekstów bez licencji nie ma w repo, są tylko URL, data i własny opis. Historii Git nie przepisujemy.
- Z badania #16: decyzja słowo po słowie (D1-A). Wulwa to istotna zmiana językowa, choć nie mieści się w prostych regułach (D5). Terminy fachowe dopuszczamy tylko wtedy, gdy weszły do języka potocznego.
- Stałe zasady: SJP.pl nie jest źródłem. Wikisłownik odroczony. Nie kontaktujemy autorów zasobów.

## Rekomendowane podejście
**„Potwierdzanie, nie wykrywanie”: 1A + 2B + 3C + 4A + 5A.**
- **Uzasadnienie:** każde słowo trafia do kolejki z detektora, a dowód dostaje z pomiaru lokalnego i z faktów, które wolno publikować. Jedna tabela progów obejmuje oba typy dowodu. Werdykt zawsze zapada dla jednego słowa.
- **Akceptowane koszty:** dużo ręcznej pracy na słowo. Brak automatycznego wykrywania. Kontekstu nie da się sprawdzić z samego repo.
- **Założenia (jeśli są fałszywe, rekomendacja się zmienia):**
  1. Publikacja liczb i URL z TDM ma niskie ryzyko. Jeśli nie, przechodzimy na 1D.
  2. Próbka 1–2 mld słów da karty dla kontroli (ccrawl-02, ekstrapolacja).
  3. Kolejka z detektorów wystarcza. Jeśli ważne słowa wciąż umykają, wracamy do 4B z 1B.
  4. Typ „zmiana świadoma” obejmuje kilka–kilkanaście leksemów na kwartał (metoda-02).
- **Pewność:** średnia.

## Dlaczego nie inne
- **1B:** koszt pełnej listy ma sens tylko przy wykrywaniu.
- **1C:** przy kandydatach daje mało ponad 1A.
- **1D:** traci progi i kalibrację.
- **2A:** dopuszcza słowa bez użycia.
- **2C:** próg ustawiony pod jedno słowo psuje neutralność.
- **2D:** wycina cel typu.
- **3A:** zgodne z zasadami, ale wolniejsze niż 3C bez zysku dowodowego.
- **3B:** wpuszcza formy ze wzoru.
- **3D:** pomija najmocniejszą pulę.
- **4B:** ok. 4% trafień potocznych i brak filtra spamu.
- **4C:** blokuje kolejkę, a kalibracja i tak potrzebuje kandydatów.
- **4D:** wycina prawdziwe zapożyczenia.
- **5B:** wpuszcza pisownię bez użycia.
- **5C:** obniża dowód zależnie od liczby form.

## Odroczone pomysły
| Pomysł | Klasa | Dlaczego później |
|---|---|---|
| Automatyczny filtr spamu na poziomie dokumentu w CC | stretch | potrzebny tylko dla 4B (ccrawl-03) |
| Pełna lista blokad dla próbki (1B) | stretch | gdy CC zacznie wykrywać |
| Źródła NC (Spokes, hate_speech_pl) i fora SpeakLeash | stretch | stare, mało trafień, licencja do oceny (D12, potoczne-02) |
| Wikisłownik | poza zakresem | odroczony decyzją |
| Formy czasownika w rodzaju niebinarnym | poza zakresem | to zmiana fleksji SGJP, nie nowy leksem (metoda-02) |
| Szkice ADR: warstwa potoczna, typ „zmiana świadoma”, polityka TDM | stretch | dla solution-designer (raport § 9) |
