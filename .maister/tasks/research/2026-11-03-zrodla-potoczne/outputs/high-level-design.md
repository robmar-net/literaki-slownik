# Projekt: źródła potoczne i świadome zmiany językowe

Data: 2026-11-04 · Zgłoszenie: #16 · Wybory: 1A, 2A (Z1) + zaimki.pl, 3C, 4A, 5A · Rozszerza: [projekt nowych słów](../../2026-11-03-zrodla-nowych-slow/outputs/high-level-design.md) · Decyzje: [decision-log.md](decision-log.md)

## TL;DR
- **Sieć i napisy potwierdzają słowo z kolejki, nie wykrywają go.** Kolejkę tworzą detektory: zgłoszenia, napisy (lokalnie), nowe hasła Dobrego Słownika (DS), tezaurus DS, zaimki.pl, plebiscyty.
- **Do repo idą tylko fakty:** liczby, lata, liczba hostów, data, URL i własny opis. Tekst nie idzie nigdy. Opt-out sprawdzamy na hostach wszystkich trafień kandydata, w dniu pomiaru i ponownie przed wpisem.
- **Zmiana świadoma:** hasło DS wystarcza (Z1). Słowo znane tylko z zaimki.pl potrzebuje jednego niezależnego dowodu użycia. Feminatywy i neutratywy idą w partiach, werdykt dla każdego słowa. Pierwsza partia: 122.
- **Każda pisownia ma osobny werdykt** we wspólnej karcie rodziny.
- Projekt dokłada kontenery do potoku z #16. Build, suplement v2 i decyzja słowo po słowie zostają bez zmian.

## Kluczowe decyzje
- Polityka TDM, opt-out i publikacji (1A) — [ADR-019](decision-log.md#adr-019).
- Warstwa potoczna: CC tylko potwierdza, progi v2, B7 tymczasowy (4A) — [ADR-020](decision-log.md#adr-020).
- Typ „zmiana świadoma”: Z1 z hasłem DS; zaimki.pl jako detektor plus jeden dowód użycia (2A) — [ADR-021](decision-log.md#adr-021).
- Feminatywy i neutratywy w partiach, flaga `tylko-wzór` (3C) — [ADR-022](decision-log.md#adr-022).
- Rodzina pisowni: karta wspólna, werdykty osobne (5A) — [ADR-023](decision-log.md#adr-023).
- Numery ADR-019+ do potwierdzenia przy wdrożeniu. Zależą od numerów ADR-014–018 z #16.

## Otwarte pytania / ryzyka
- **Ocena prawna to odczyt zbieracza, nie porada prawna** (ccrawl-01). Nie wiadomo, czy art. 26³ liczy opt-out z dnia crawla, czy z dnia pobrania. Przyjmujemy dzień pobrania (ccrawl-04).
- **`Content-Signal: ai-train=no`** (12/100 dużych hostów, ccrawl-04) dotyczy treningu AI, nie każdego TDM. Nie ma go na liście z 1A. Propozycja: zapisać jako flagę hosta, nie wykluczać. Potwierdza użytkownik.
- **Z1 wpuszcza słowa bez zmierzonego użycia**, jeśli mają hasło DS (metoda-02). Użytkownik przyjął to ryzyko. Karta pokazuje liczby, jeśli są, ale nie stawia progu.
- **Lista lematów z zaimki.pl w repo.** Partia 122 to przecięcie z tezaurusem DS (GPL/LGPL), więc każdy lemat ma wolne źródło. Słowo tylko z zaimki.pl trafia do repo pojedynczo, z własnym dowodem.
- **Neutratywy:** suplement wymaga wzoru fleksji SGJP (ADR-016). Gdy nie ma pasującego wzoru, słowo czeka.
- **Czy podklasa (b) mieści się w zasadach dopuszczalności Kurnika:** decyzja użytkownika (swiadoma-05).
- **Liczby z sieci są wstępne:** policzone przed filtrem opt-out, ghosting z 4 form zamiast 9 (synthesis S2, S4).
- **Dysk:** próbka 1–2 mld słów to kilkanaście–kilkadziesiąt GB (ccrawl-02: 662,7 mln słów ≈ 8,9 GB pobrań). Liczymy plik po pliku i kasujemy go zaraz po liczeniu.

---

## Opis
**Problem.** Korpusy z #16 (PPC, ParlaMint, Leipzig) nie widzą słów potocznych ani świadomych zmian. Wulwa, ghosting, cringe i boomer mają w nich 0–6 trafień (metoda-05). Źródła z najmocniejszym sygnałem (napisy, sieć) nie mają licencji tekstu (synthesis W1).

**Rozwiązanie.** Do kolejki z #16 dochodzą **detektory lokalne**. Kandydat z kolejki dostaje **pomiar potwierdzający** w Common Crawl (FineWeb-2/HPLT) na próbce 1–2 mld słów, po **filtrze opt-out**. Słowa świadomej zmiany dostają **dowód ręczny** z DS. Wynik trafia do **rozszerzonej karty kandydata**. Dalej działa droga z #16: decyzja użytkownika, wzór fleksji SGJP, suplement v2, build, wiki.

**Kluczowe decyzje:**
- **Potwierdzanie, nie wykrywanie.** W CC tylko ok. 4% nowych grup to słowa potoczne (ccrawl-03).
- **Fakty zamiast tekstu.** Liczby i URL to wynik TDM. Kontekst byłby cytatem (ccrawl-01).
- **Dwa typy dowodu, dwie reguły.** `potoczne`: bramki B1–B8. `zmiana_swiadoma`: hasło DS albo jeden dowód użycia.
- **Werdykt zawsze dla jednego słowa i jednej pisowni.** Partia i rodzina dzielą tylko kartę.

## Architektura

### Kontekst (C4, poziom 1)
```
                       zgłoszenie, werdykt (słowo po słowie)
   [Użytkownik] <------------------------------------------+
        |  ^                                               |
  karty |  | dowód ręczny (URL, data, własny opis)         |
        v  |                                               |
 +-------------------------------+   listy (Release)   [Gracz /
 |  literaki-slownik             |-------------------> odwiedzający
 |  wykrywanie + build (z #16)   |   liczby, źródła     wiki]
 |  + detektory, pomiar CC,      |-----> [Wiki projektu] ---^
 |    filtr opt-out              |
 +-------------------------------+
    ^ HTTPS, lokalnie   ^ HTTPS, lokalnie    ^ HTTPS (robots.txt,
    | (TDM, art. 26³)   | (detektory)        |  tdmrep, regulamin)
 [FineWeb-2 / HPLT]  [OpenSubtitles, DS:    [hosty trafień
  (opakowanie ODC-By  mapa witryny,          kandydata]
   / CC0; tekst bez   tezaurus DS, zaimki.pl,
   licencji)          plebiscyty]
```
- Strzałki w górę to dane do liczenia lokalnego. Nic z tych źródeł nie idzie do repo poza faktami.
- SJP.pl nie jest źródłem. Wikisłownik jest odroczony. Nie kontaktujemy autorów zasobów.

### Kontenery (C4, poziom 2)
```
 DETEKTORY (lokalnie, poza Git)            POMIAR (lokalnie, poza Git, taskpolicy -b, python -I)
 +----------------------------+            +--------------------------------------------+
 | zgłoszenia ręczne          |            | Pomiar CC: próbka 1-2 mld słów,            |
 | napisy: liczba filmów      |            | formy z wzoru, bramki B1-B8, lata, hosty   |
 | DS: nowe hasła (mapa)      |            +---------------------+----------------------+
 | tezaurus DS (sha256)       |                      | hosty trafień
 | zaimki.pl (lokalnie)       |                      v
 | plebiscyty (ręcznie)       |            +--------------------------------------------+
 +-------------+--------------+            | Filtr opt-out: robots CCBot/*, tekst TDM,  |
               | lemat + źródło            | TDMRep; regulamin ręcznie; data stanu      |
               v                           +---------------------+----------------------+
 +----------------------------+                      | trafienia z czystych hostów
 | Kolejka (z #16) + strumień |------ kandydat ----->v
 | potoczne / zmiana_swiadoma |            +--------------------------------------------+
 +----------------------------+            | Ocena znaczeń (ręcznie, konteksty lokalne) |
               ^                           | wynik: n z m w znaczeniu; potem kasowanie  |
               | odejmuje rozstrzygnięte   +---------------------+----------------------+
 +----------------------------+                      | liczby
 | Rejestr decyzji (z #16)    |                      v
 | + typ dowodu, tylko-wzór,  |<--- werdykt --- +--------------------------------+
 |   data opt-out             |                 | Karta kandydata (rozszerzona)  |<-- Dowód ręczny:
 +-------------+--------------+                 | karta rodziny / karta partii   |    DS, plwiki,
               | dodać                          +--------------------------------+    RJP (klasa)
               v
 +--------------------------------------------------------------+
 | Z #16, bez zmian: wzór fleksji SGJP -> suplement v2 -> build  |
 | -> benchmark -> wiki                                          |
 +--------------------------------------------------------------+
```
- **Detektory** dają tylko lemat i nazwę źródła. Nie dają dowodu.
- **Pomiar CC** działa tylko dla kandydatów z kolejki. Nie skanuje próbki w poszukiwaniu nowych słów.
- **Filtr opt-out** stoi przed każdą liczbą, która trafia do karty.
- **Decyzja** to jedyne przejście do buildu, jak w #16.

## Komponenty

| Komponent | Cel | Zadania | Interfejs | Zależy od |
|---|---|---|---|---|
| **Detektory lokalne** | Zasilić kolejkę słowami spoza korpusów #16 | napisy OpenSubtitles: liczba filmów (IMDb ID), nie zdań; DS: nowe hasła z mapy witryny (id, `lastmod`); tezaurus DS: obecność + sha256 pliku; zaimki.pl: feminatywy i neutratywy spoza SGJP; plebiscyty i zgłoszenia ręcznie | lemat + detektor → kolejka | manifest wykrywania (#16) |
| **Kolejka** (rozszerzona) | Kolejność przeglądu | strumień `potoczne` lub `zmiana_swiadoma`; partie (3C); rodziny pisowni (5A); odjęcie rejestru i SGJP jak w #16 | kandydat → pomiar albo karta | rejestr, ADR-017/018 |
| **Pomiar CC** | Potwierdzić użycie kandydata | próbka FineWeb-2/HPLT 1–2 mld słów; wszystkie formy z wzoru (ghosting: 9); B1–B8 v2; lata i hosty; plik po pliku, kasowanie po liczeniu | lista form → trafienia (host, rok, URL) lokalnie | wzór fleksji (#16), tabela progów |
| **Filtr opt-out** | Liczyć tylko to, co wolno (art. 26³) | hosty **wszystkich** trafień; robots.txt (`CCBot` albo `*`), jawny tekst TDM, TDMRep; regulamin ręcznie przy dokumentach dowodowych; data stanu; drugie sprawdzenie przed wpisem | hosty → hosty dozwolone + data | sieć (tylko ten krok i pobieranie) |
| **Ocena znaczeń** | Odsiać inne znaczenia | ręczna ocena kontekstów lokalnych (ghosting relacyjny tylko w 2/27 i 5/45, ccrawl-02); wynik liczbowy; kasowanie kontekstów po ocenie | trafienia → n z m w znaczeniu | pomiar CC |
| **Dowód ręczny** | Udokumentować źródło redagowane | DS: URL, data, id, własny opis; plwiki dyskusje: liczby i link; RJP: reguła klasy, URL przy klasie; publikacja: DOI lub URL | wpis w karcie | użytkownik / agent |
| **Karta kandydata** (rozszerzona) | Wszystko do decyzji | nowe pola (tabela niżej); karta rodziny pisowni; karta partii | kandydat → karta w repo | karta z #16 |
| **Rejestr decyzji** (rozszerzony) | Pamięć między kwartałami | pola: typ dowodu, flaga `tylko-wzór`, data stanu opt-out; reguła powrotu z ADR-018 | werdykt → rejestr | rejestr z #16 |
| **Tabela progów** | Jedno miejsce dla wszystkich progów | B1–B8 v2, B7 tymczasowy, B6 hosty, reguła jednego dowodu dla zaimki.pl, jedna definicja B4 | czytana przez pomiar i kartę | ADR-020 |

### Nowe pola karty

| Pole | Wartości / treść | Przykład |
|---|---|---|
| typ dowodu | `korpus`, `potoczne`, `zmiana_swiadoma`, `reczny` (może być kilka) | wulwa: `zmiana_swiadoma` |
| detektor | skąd słowo w kolejce | ghosting: napisy |
| rodzina pisowni | pisownie z osobnym dowodem i werdyktem; zapisy niegrywalne jako dowód życia | boomer / bumer |
| homograf | forma już w SGJP jako inny leksem | bumer m3 (10 form) |
| nowe formy w grze | formy po odjęciu SGJP, osobno STANDARD i BROAD; tylko informacja | boomer +11, bumer m1 +1 |
| lejek | trafienia: surowe → B3 → B4 → B5 → B6 → po opt-out → po ocenie znaczeń | — |
| stan opt-out | data sprawdzenia, liczba hostów sprawdzonych i odrzuconych, data drugiego sprawdzenia | — |
| napisy | liczba filmów + link do opensubtitles.org | — |
| dowód ręczny | źródło, URL, data odczytu, id, własny opis | DS wulwa, id 226245 |
| flaga `tylko-wzór` | forma znana tylko z list | — |
| tagi | klasy i rodzaj; dla `cringe` dwa | adj nieodm. + subst n |

## Przepływ kwartalny
Rytm i kroki z #16 (ADR-018) zostają. Dochodzą kroki oznaczone ★.

```
1. Pobierz (z #16) + ★ detektory lokalne
2. Nowy SGJP? osobny bump (z #16)
3. ★ Kolejka: strumień, partia, rodzina pisowni
4. ★ Pomiar CC dla kandydatów -> ★ filtr opt-out (stan z dnia pomiaru)
   -> ★ ocena znaczeń -> kasowanie danych
5. ★ Dowód ręczny (DS, plwiki, RJP)
6. Karty (część ok. 50; partia ma jedną kartę z wierszem na słowo)
7. Decyzja użytkownika, osobno dla każdego słowa i pisowni
8. ★ Drugie sprawdzenie opt-out dla słów "dodać" -> suplement vN, build
9. Wiki + commit
```
- Krok 4 przeliczamy tylko przy nowej wersji próbki CC albo dla nowych kandydatów.
- Krok 8: jeśli host dowodu dodał zastrzeżenie, liczbę przeliczamy bez niego. Gdy próg spadnie poniżej wymaganego, słowo wraca do kolejki.

## Przepływ danych

| Dane | Gdzie powstają | Gdzie leżą | Do repo? |
|---|---|---|---|
| shardy FineWeb-2/HPLT | pobranie | `cache/`, kasowane po liczeniu pliku | nie |
| trafienia (host, rok, URL) i konteksty | pomiar CC | `data/work/`, kasowane po ocenie znaczeń | nie |
| liczby, lata, liczba hostów, ipm, lejek | pomiar + filtr | karta | **tak** |
| URL + data + własny opis dokumentu dowodowego | ręcznie | karta | **tak** (po opt-out) |
| zdania z napisów | detektor | lokalnie, kasowane | nie; w karcie liczba filmów + link |
| hasła DS, mapa witryny | detektor | lokalnie | nie; URL, data, id, opis |
| tezaurus DS | detektor | `cache/` | nie; „jest w tezaurusie DS vX” + sha256 |
| dane zaimki.pl | detektor | lokalnie | nie; URL, data, opis przy słowie |
| werdykt, typ dowodu, flagi | użytkownik | rejestr | **tak** |

## Granice prawne

| Czynność | Podstawa | Zasada |
|---|---|---|
| liczenie form w CC | art. 26³ ust. 1 | tylko lokalnie, tylko hosty bez zastrzeżenia |
| przechowywanie danych | art. 26³ ust. 3 | tak długo, jak trwa pomiar; potem kasujemy |
| publikacja liczb, lat, liczby hostów | wynik TDM, nie utwór (ccrawl-01) | tak, z datą stanu opt-out |
| URL + data + własny opis | fakt | tak, po opt-out hosta i lekturze regulaminu |
| kontekst, cytat, próbka | art. 29, 34, 35 | **nie** z tekstów bez licencji |
| napisy | brak licencji tekstu | tylko detektor; w karcie liczba filmów + link |
| DS (prawa zastrzeżone) | — | dowód ręczny, bez kopiowania haseł |
| tezaurus DS (GPL-2.0+ / LGPL 2.1) | — | sygnał lokalny, bez importu |
| zaimki.pl (OQL v1.4) | niezgodna z CC BY 4.0 list | detektor lokalny, bez importu |
| plwiki dyskusje (CC BY-SA 4.0) | licencja | liczby i link; cytat z atrybucją tylko wyjątkowo |
| fora SpeakLeash, źródła NC | — | odłożone |

Projekt nie jest organizacją badawczą (art. 26²), więc działa na art. 26³. Zastrzeżenie umowne wiąże (ccrawl-01).

## Punkty integracji
- **Manifest wykrywania (ADR-015 z #16):** nowe wpisy FineWeb-2, HPLT, OpenSubtitles, tezaurus DS, mapa witryny DS, zaimki.pl. Każdy ma osobno licencję tekstu i opakowania oraz zakres: „tylko liczenie lokalne” albo „liczby do publikacji”.
- **Wzór fleksji (ADR-016):** daje listę form do pomiaru. Bez wzoru nie ma pomiaru B5a.
- **Rejestr i kolejka (ADR-017/018):** wspólne dla wszystkich strumieni. Słowo odrzucone w jednym strumieniu nie wraca z drugiego bez nowego dowodu.
- **Suplement v2 i build:** bez zmian. Kwalifikator pusty. Typ dowodu jest w rejestrze, nie w suplemencie.
- **Sieć:** HTTPS tylko przy pobieraniu i przy sprawdzaniu opt-out. Bez formularzy, kont i maili.
- **`ATTRIBUTIONS.md`:** FineWeb-2 (ODC-By, ccrawl-01) i HPLT (CC0), gdy pierwsze liczby trafią do repo. plwiki (CC BY-SA), gdy pojawi się cytat.

## Wdrożenie: kroki i zależności

| # | Krok | Zależy od |
|---|---|---|
| 0 | Skasować małe pobrania z badania (`dane/male`, plik trafień w napisach; potoczne-03) | — |
| 1 | Wdrożyć #16: manifest (ADR-015), suplement v2 i wzór fleksji (ADR-016), kolejka i rejestr (ADR-017/018), karta | — |
| 2 | ADR-019–023 do `docs/adr/` z ostatecznymi numerami; wpisy w `.maister/docs/INDEX.md` | 1 (numery ADR #16) |
| 3 | Tabela progów: B1–B8 v2, B7 tymczasowy, jedna definicja B4, reguła jednego dowodu | 2 |
| 4 | Wpisy manifestu dla nowych źródeł | 1 |
| 5 | Filtr opt-out: sprawdzanie hostów trafień, zapis stanu i daty | 4 |
| 6 | Pomiar CC na próbce 1–2 mld słów, plik po pliku, z kasowaniem | 3, 4, 5, wzór fleksji z 1 |
| 7 | Kontrole: ghosting z 9 formami; hejt, lockdown, antyszczepionkowiec jako kontrola dodatnia liczenia (lockdown 0 przed 2020) | 6 |
| 8 | Detektory lokalne: napisy (liczba filmów), mapa DS, tezaurus DS, zaimki.pl | 4 |
| 9 | Rozszerzyć kartę (nowe pola, karta rodziny, karta partii) i rejestr | 1 |
| 10 | Pierwsze karty: wulwa (próba Z1), rodziny boomer/bumer i cringe/krindż, ghosting | 6–9 |
| 11 | Partia 122 (zaimki.pl ∩ tezaurus DS) | 8, 9 |
| 12 | Kalibracja B3–B7 na pierwszych kartach (nie blokuje kolejki) | 10 |
| 13 | Wiki, `ATTRIBUTIONS.md`, `docs/runbook-wiki.md` | 10 (pierwsze liczby w repo) |

## Wpływ na wiki
Zasada repo: zmiana źródeł lub kryteriów aktualizuje wiki w tej samej pracy. Strony z #16 dostają dopiski.

| Strona | Kiedy | Co zmienić |
|---|---|---|
| `Home` | przy pierwszej karcie potocznej | tabela źródeł: FineWeb-2/HPLT „tylko liczby w kartach, po filtrze opt-out”; DS „tylko dowód ręczny (link)”; OpenSubtitles „tylko lokalne wykrywanie” |
| `Slownik-STANDARD`, `Slownik-BROAD` | przy pierwszym „dodać” z nowego strumienia | słowa potoczne i świadome zmiany wchodzą tak samo: decyzją, przez suplement; przykład |
| `Nowe-slowa` (nowa z #16) | przy pierwszej karcie | **nowa sekcja „Źródła potoczne i świadome zmiany”:** detektory; zasada „potwierdzanie, nie wykrywanie”; co publikujemy (fakty, bez tekstu); opt-out; dwa typy dowodu; partie feminatywów i neutratywów; rodziny pisowni; czego nie używamy (SJP.pl, Wikisłownik odroczony) |
| `_Sidebar` | razem z `Nowe-slowa` | link do sekcji |
| `Historia-zmian` | przy każdym buildzie z nową wersją suplementu | wiersz z liczbą słów z każdego typu dowodu |
| `Porownanie-z-SJP.pl` | po buildzie | nowy benchmark (tylko porównanie) |
| `Slownik-POP`, `POP0`, `POP00`, `TEMATY` | bez zmian | — |

## Decyzje projektowe

| ADR | Decyzja | Odrzucone |
|---|---|---|
| [ADR-019](decision-log.md#adr-019) | fakty publiczne; opt-out na hostach wszystkich trafień kandydata (1A) | lista blokad całej próbki (1B); lista dużych hostów (1C); tylko znacznik (1D) |
| [ADR-020](decision-log.md#adr-020) | CC tylko potwierdza; progi v2; B7 tymczasowy (4A) | CC wykrywa (4B); najpierw kalibracja (4C); progi v1 (4D) |
| [ADR-021](decision-log.md#adr-021) | Z1 z hasłem DS; zaimki.pl + jeden dowód użycia (2A) | Z2 (2B); Z2 z niższym progiem (2C); Z3 (2D) |
| [ADR-022](decision-log.md#adr-022) | partie, werdykt na słowo, `tylko-wzór` odpada (3C) | słowo po słowie bez partii (3A); hurt (3B); tylko zgłoszenia (3D) |
| [ADR-023](decision-log.md#adr-023) | rodzina pisowni: karta wspólna, werdykty osobne (5A) | jeden werdykt (5B); werdykt ważony grą (5C) |

## Przykłady

**1. Wulwa (zmiana świadoma, Z1).**
Mamy: hasło DS id 226245, dodane I–II 2024 (swiadoma-01); brak w SGJP 20261018; w CC 3 + 3 trafienia, 0,006–0,016 ipm (ccrawl-02).
Gdy kandydat przejdzie z kolejki do karty,
wtedy karta ma typ `zmiana_swiadoma` i dowód DS (URL, data, id, własny opis). Pomiar CC nie jest wymagany. Jeśli jest, karta pokazuje liczby po opt-out, bez progu. Użytkownik wybiera wzór fleksji (rzeczownik żeński na `-wa`) i wydaje werdykt.

**2. Ghosting (potoczne, napisy → CC).**
Mamy: 10 trafień w napisach 2022–2023 (potoczne-03); w CC znaczenie relacyjne tylko w 2/27 i 5/45 kontekstów (ccrawl-02).
Gdy pomiar policzy 9 form wzoru `ranking`, przefiltruje hosty z zastrzeżeniem i oceni znaczenia,
wtedy karta pokazuje lejek do „po ocenie znaczeń” i liczbę filmów z linkiem. Jeśli po ocenie zostaje < 20 trafień albo < 0,05 ipm, B7 nie jest spełnione, a słowo trafia na listę skróconą.

**3. Rodzina boomer / bumer.**
Mamy: `boomer` +11 form, `bumer` m1 +1 (`bumerzy`), `bumer` m3 już w SGJP (metoda-04); `bumer` bez pomiaru w sieci.
Gdy rodzina dostaje kartę,
wtedy każda pisownia ma własny lejek i werdykt. `bumer` bez dowodu użycia czeka. Próg dowodu jest ten sam, mimo że gra zyskuje tylko 1 formę.

**4. Partia 122 (feminatywy).**
Mamy: 122 formy w zaimki.pl i w tezaurusie DS, bez SGJP (swiadoma-04), np. chirurżka, kardiolożka.
Gdy partia dostaje wspólną kartę (reguła RJP dla klasy, opis źródeł),
wtedy każde słowo ma wiersz: hasło DS → przechodzi jak Z1; brak hasła DS → potrzebny jeden niezależny dowód użycia; brak obu → flaga `tylko-wzór`, werdykt „odrzucić”. Rejestr pozwala wrócić z nowym dowodem.

**5. Host dodał zastrzeżenie przed wpisem.**
Gdy drugie sprawdzenie opt-out (krok 8) znajdzie nową blokadę `CCBot` na hoście trafienia,
wtedy liczby przeliczamy bez tego hosta i zapisujemy nową datę. Jeśli warunek przestaje być spełniony, słowo wraca do kolejki.

## Poza zakresem
- Wykrywanie nowych słów w CC i filtr spamu (4B), lista blokad całej próbki (1B).
- Fora SpeakLeash i źródła NC (Spokes, hate_speech_pl).
- Import danych zaimki.pl i tezaurusa DS.
- Sondy `essa`, `zoomer`, `dziaders` (odroczone w fazie 4).
- Formy czasownika w rodzaju niebinarnym (zmiana fleksji SGJP, nie nowy leksem; metoda-02).
- Własne spolszczenia pisowni.
- Wikisłownik (odroczony), SJP.pl (nie jest źródłem), kontakt z autorami.
- Przepisywanie historii Git.
- Konkretne pliki, polecenia i testy: to specyfikacja wdrożenia.

## Kryteria sukcesu
- Każda liczba z CC w karcie ma datę stanu opt-out. Żadne trafienie z hosta z zastrzeżeniem nie jest w niej policzone.
- W repo nie ma tekstu z napisów, CC, DS ani zaimki.pl: tylko liczby, URL, daty, id i własny opis.
- Dane z pomiaru są skasowane po ocenie znaczeń. Na dysku nie zostaje żaden shard.
- Kontrole dodatnie (hejt, lockdown, antyszczepionkowiec) mają trafienia po opt-out, a lockdown ma 0 przed 2020.
- Każde słowo partii 122 i każda pisownia rodziny ma osobny werdykt w rejestrze. Żadne słowo z flagą `tylko-wzór` nie trafia do suplementu.
- Build z nowymi słowami przechodzi bez zmiany kodu (suplement v2, ADR-016).
