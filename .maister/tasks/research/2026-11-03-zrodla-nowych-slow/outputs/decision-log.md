# Decyzje: wychwytywanie nowych słów

Data: 2026-11-03 · Zgłoszenie: #16 · Podstawa: `solution-exploration.md`, wybory D1–D5 i P1 w `orchestrator-state.yml`, pomiar `analysis/findings/korpusy-04-zysk.md`.

## TL;DR
- Pięć szkiców ADR: **ADR-014 … ADR-018**. Numery są wolne w `docs/adr/` (ostatni: ADR-013). Do potwierdzenia przy wdrożeniu.
- Najważniejsze: **ADR-016**. Suplement v2 zastępuje v1 w tym samym slocie, więc limit „najwyżej 1 suplement” w kodzie zostaje bez zmian.
- **ADR-017** rozstrzyga pytanie o kandydatów tylko z PPC. Drugi korpus nie jest wymagany, bo wtedy tracimy ok. 60–70 słów wartych gry (np. patostreaming). Pełne karty dostają tylko grupy z ≥ 5 użyciami w posiedzeniach plenarnych: 73 grupy, trafność 34%. Reszta trafia na listę skróconą (10%) albo zostaje odłożona (leki i angielskie, 0%).
- Korpusy i NKJP służą tylko do wykrywania i liczb w karcie. Do list słowo wchodzi wyłącznie decyzją użytkownika, przez suplement.

## Kluczowe decyzje
- ADR-014: NKJP 1grams także do miary wzrostu, poza buildem.
- ADR-015: PPC, ParlaMint-PL 5.0 i Leipzig news tylko do wykrywania. Osobny manifest, nie `sources.json`.
- ADR-016: suplement v2 w miejscu v1, słowo po słowie, fleksja według wzoru leksemu SGJP.
- ADR-017: PPC-only w trzech warstwach (plenarna, skrócona, odłożona), bez wymogu drugiego korpusu.
- ADR-018: przegląd kwartalny z odświeżeniem PPC; pierwsza paczka w częściach.

## Otwarte pytania i ryzyka
- Numery ADR mogą się zmienić, jeśli inna praca zajmie 014–018 wcześniej.
- Trafność w ADR-017 opiera się na ocenach agenta (100 + 100 grup, bez konkordancji). Pierwsza część przeglądu użytkownika ją zweryfikuje.
- Suplement łączy dwie role (uzupełnienie eksportu i nowe leksemy). Nagłówek pliku musi to mówić.

---

## ADR-014: NKJP 1grams także do miary wzrostu, poza buildem

### Status
Proponowana (wybór użytkownika D3-A, 2026-11-03). Rozszerza zakres [ADR-006](../../../../../docs/adr/ADR-006-nkjp-cc-by-bez-wersji.md).

### Kontekst
ADR-006 dopuszcza NKJP 1grams tylko do miar POP i POP0. Metoda progowa NKJP → KWJP potrzebuje NKJP jako bazy „przed 2011”. Daje 374 kandydatów z lat 2011–2020, ok. 65% trafnych. Bez decyzji metoda nie ma podstawy formalnej.

### Czynniki decyzji
- Podstawa formalna dla metody, która już działa (5 z 5 kontroli celu).
- Bez nowej licencji: CC BY jest przyjęte w ADR-006.
- Nic nie trafia do list automatycznie (§4.4 specyfikacji v3).

### Rozważane opcje
1. Nowy ADR: NKJP także do miary wzrostu g, tylko poza buildem.
2. Bez NKJP: kandydat = częsty w KWJP i brak w SGJP (lista luk, nie nowych słów).
3. Baza czasu tylko z jednego korpusu po 2015 (ParlaMint, PPC).

### Wynik decyzji
Wybrana opcja 1. Daje jedyną miarę wzrostu dla lat 2011–2020. Opcja 3 nie widzi tych lat. Wchodzi więc obok, w ADR-015, a nie zamiast.

### Konsekwencje
#### Dobre
- Lista 374 staje się formalnym strumieniem kandydatów.
- Atrybucja jak w ADR-006, bez nowych warunków.
- Build i `sources.json` bez zmian. Wpis `unavailable: NKJP` w manifeście buildu zostaje, bo build NKJP nie używa.

#### Złe
- Miara g jest zgrubna: porównuje lemat KWJP z formą podstawową NKJP. Te same progi przechodzi 2 313 lematów już obecnych w SGJP.
- NKJP i KWJP się nie zmieniają, więc ten strumień daje kandydatów raz. W kolejnych kwartałach tylko odejmujemy rozstrzygnięte.

---

## ADR-015: PPC, ParlaMint-PL 5.0 i Leipzig news tylko do wykrywania

### Status
Proponowana (wybór użytkownika D4-A, 2026-11-03).

### Kontekst
Po 2020 roku NKJP → KWJP nic nie widzi. Pomiar `korpusy-04-zysk.md`: PPC (316 mln słów, do 2026-10-16) daje 702 nowe grupy form spoza SGJP i spoza listy 374. Leipzig daje 154, a ParlaMint 15. Łącznie jest to 875 grup, w tym ok. 300 słów wartych gry. Kod buildu przyjmuje tylko 6 rodzajów artefaktów i dokładnie 14 + suplement.

### Czynniki decyzji
- Czysta licencja liczb pochodnych.
- Bez zmiany kodu buildu.
- Odtwarzalność: każdy plik przypięty przez sha256.
- Dane surowe (16 GB) nie mogą trafić do Git.

### Rozważane opcje
1. Trzy korpusy tylko poza buildem: wykrywanie i liczby w karcie.
2. Korpusy w buildzie jako `corpus_evidence` (nowy rodzaj artefaktu).
3. FineWeb-2 lub HPLT (duże, ale licencja tekstu nieustalona).
4. Żaden korpus; po 2020 tylko dowód ręczny (OJ UW, WSJP).

### Wynik decyzji
Wybrana opcja 1, bo daje lata 2020–2026 bez zmiany kodu i bez ryzyka licencji. Szczegóły:
- **Osobny manifest wykrywania**, nie `sources.json`. Każdy wpis ma url, wersję, `retrieved_at`, sha256, licencję, zakres i atrybucję. Ten manifest obejmuje też NKJP (ADR-014), KWJP i SGJP jako punkt odniesienia.
- **PPC dopisany do źródeł projektu**: `ATTRIBUTIONS.md` (dane: domena publiczna, anotacja CC BY) i wiersz w tabeli źródeł na wiki `Home` z opisem „tylko do wykrywania nowych słów”.
- **Leipzig tylko z plików do pobrania** (CC BY 4.0). Strona i API mają CC BY-NC, więc ich nie używamy.
- **Co wolno w repo:** manifest, skrypty, zliczenia pochodne dla kandydatów (lemat, liczby rocznie, g, liczba dokumentów), do 2 krótkich przykładów zdań na kandydata z atrybucją. **Czego nie wolno:** surowych plików, pełnych list frekwencyjnych, długich fragmentów tekstu.

### Konsekwencje
#### Dobre
- Widać słowa z lat 2023–2026, czego nie ma żaden inny korpus (PPC: 518 nowych grup w tym okresie).
- Build, testy buildu i `inputs.py` bez zmian.

#### Złe
- PPC jest zaszumiony: 15,6% słów znanych z SGJP też przechodzi kryterium „nowe”. Stąd ADR-017.
- Słowa potoczne i internetowe (boomer, ghosting, cringe, wulwa) nie wyjdą w żadnym z trzech korpusów. To osobne badanie (D5).
- ParlaMint kończy się w VI 2022. Leipzig nie ma lat 2019–2020 ani 2025.
- 16 GB danych na dysku (dziś 34 GB wolnego).

---

## ADR-016: Suplement v2 słowo po słowie, w miejscu v1

### Status
Proponowana (wybór użytkownika D1-A, 2026-11-03). Uchyla wariant A z `source-extension-decision.md` tylko dla słów, które użytkownik zatwierdzi.

### Kontekst
Leksem wchodzi do list tylko z SGJP albo z suplementu. `inputs.py` w trybie produkcyjnym wymaga: 1 SGJP, 13 list KWJP i **najwyżej 1** `lexical_supplement`. Dziś suplement v1 ma 4 wiersze (się, siebie, sobie, sobą). Jego nagłówek uzasadnia wpis brakiem w eksporcie TSV, co nie pasuje do nowych słów. Czytnik SGJP nie dopuszcza komentarzy poza nagłówkiem.

### Czynniki decyzji
- Bez zmiany kodu i limitu, który chroni manifest.
- Każde słowo osobno, z dowodem i decyzją użytkownika.
- Pełna i poprawna fleksja (§2.2).
- Łatwe wycofanie.

### Rozważane opcje
1. **v2 zastępuje v1 w tym samym slocie**: jeden plik, nowy `DICT-ID`, nowy `source_id`, rosnąca lista `evidence`.
2. Drugi plik suplementu i zmiana limitu w `inputs.py` na ≤ 2 (kod i testy).
3. Nowe źródło leksykalne (nowy `kind`, importer, ADR licencji).

### Wynik decyzji
Wybrana opcja 1. Limit jest strażnikiem, a nie przeszkodą: jeden plik to jeden audyt. Dowody dla każdego słowa mieszczą się w istniejącym polu `evidence`, gdzie kod sprawdza sha256 każdego pliku. Szczegóły:
- **Wersja przy każdej zmianie pliku:** v2, v3… Nowy sha256, wszystkie 6 liczników `expected_counts` liczone od nowa, `duplicates` = 0.
- **Nagłówek** opisuje dwie części (uzupełnienie eksportu i leksemy spoza SGJP decyzją użytkownika) i wskazuje rejestr decyzji. Wiersze danych są bez komentarzy.
- **Fleksja według wzoru:** dla każdego słowa wskazujemy leksem SGJP z tą samą klasą i odmianą (np. `związkowiec` dla `antyszczepionkowiec`, m1). Formy powstają przez podmianę tematu w paradygmacie wzoru. Użytkownik widzi pełną listę form w karcie przed decyzją.
- **Kwalifikatory puste:** słowo przechodzi te same filtry co leksem SGJP i trafia do STANDARD i BROAD.
- **Nakładanie z SGJP:** przy każdym nowym eksporcie SGJP usuwamy z suplementu leksemy, które SGJP już ma.
- **Zmiana testu, nie kodu:** test rundy 4 sprawdza dziś dokładnie 4 wiersze. Ma sprawdzać, że te 4 wiersze są w pliku.
- **Wycofanie:** usunąć wiersze, nowa wersja, build.

### Konsekwencje
#### Dobre
- `inputs.py` i `build.py` bez zmian.
- Każde słowo ma ślad: karta, decyzja, plik dowodów z sha256.

#### Złe
- Nazwa `sgjp-supplement` obejmuje teraz także słowa spoza SGJP. Wyjaśnia to nagłówek i wiki.
- Fleksja z wzoru to decyzja redakcyjna. Zły wzór daje złe formy na liście.
- Każda paczka oznacza nową wersję pliku, nowy build i aktualizację wiki.

---

## ADR-017: Kandydaci tylko z PPC

### Status
Proponowana (do zatwierdzenia przez użytkownika; pytanie z uwag do D4).

### Kontekst
W puli 875 grup jest 545 grup, które przechodzą kryterium tylko w PPC. PPC jest zaszumiony. 15,6% słów znanych z SGJP też przechodzi w nim kryterium „nowe”, bo zmienia się skład korpusu (po 2020 przeważają interpelacje) i zdarzają się tematyczne wybuchy (nazwy leków w interpelacjach). Użytkownik zapytał, czy takie słowa wymagają potwierdzenia w drugim korpusie albo wzrostu liczonego tylko w posiedzeniach plenarnych.

**Pomiar (2026-11-03).** PPC przeliczony ponownie z podziałem na kategorie: posiedzenia, komisje, interpelacje. Agent ocenił 100 losowych grup PPC-only i wszystkie 78 grup z sygnałem plenarnym. Klasa A to słowo warte gry. Oceny są bez konkordancji. Kalibracja: w posiedzeniach plenarnych kryterium „nowe” przechodzi **5,4%** słów znanych z SGJP (21 968 słów), a w całym PPC **15,6%**. Sygnał plenarny jest więc uczciwszy.

| Reguła dla 545 grup PPC-only | zostaje | trafność (A) | słów A (szac.) | traci słowa A, np. |
|---|---|---|---|---|
| bez reguły | 545 | 13% (13/100) | ≈ 70 | — |
| wymagaj 2. korpusu | 0 | — | 0 | wszystkie: patostreaming, neuroróżnorodność, praworządnościowy, starolas, targetować, wyszczepiać |
| wzrost tylko w plenarnych: g ≥ 5, ≥ 10 po, ≥ 3 lata | 33 | 42% (14/33) | 14 | 11 z 25: starolas, darknet, stablecoin, małpkowy |
| wzrost tylko w plenarnych: g ≥ 5, ≥ 5 po, ≥ 2 lata | 60 | 37% (22/60) | 22 | wyszczepiać, biorezonans, półautomatycznie |
| **≥ 5 użyć po 2019 w plenarnych, bez flagi lek/angielski** | **73** | **34% (25/73)** | **25** | — (w tej warstwie) |
| (dla porównania, część reszty) ≥ 2 kategorie PPC bez sygnału plenarnego | 116 | 13% (2/15) | ≈ 15 | — |
| reszta bez flagi | 365 | 10% (6/60) | ≈ 37 | streamować, wymazówka, tutoriał, mikroelektrownia |
| z flagą lek/angielski (także 5 z sygnałem plenarnym) | 107 | 0% (0/33) | ≈ 0 | — |

Dla porównania: grupy z ≥ 2 korpusów mają 70% (21/30), a Leipzig-only 50% (10/20).

### Czynniki decyzji
- Nie tracić prawdziwych słów, których nie ma w innych korpusach (patostreaming: PPC 558, Leipzig 0).
- Nie marnować czasu użytkownika na pulę o trafności 5–10%.
- Prosta reguła, którą da się powtórzyć co kwartał.

### Rozważane opcje
1. Wymagać drugiego korpusu (odrzucić PPC-only).
2. Liczyć wzrost tylko w posiedzeniach plenarnych (P2 albo P3 z tabeli).
3. **Warstwy bez odcinania:** sygnał plenarny ustala kolejność i rodzaj przeglądu.
4. Bez reguły: wszystkie 545 jako pełne karty.

### Wynik decyzji
Wybrana opcja 3. Drugi korpus nie jest wymagany, bo opcja 1 traci ok. 60–70 słów wartych gry. Reguła:
- **Warstwa plenarna** (73 grupy, ok. 34%): co najmniej 5 użyć po 2019 w posiedzeniach plenarnych i brak flagi „lek” lub „angielski”. Dostaje pełne karty po grupach z ≥ 2 korpusów i po Leipzig-only.
- **Warstwa skrócona** (365 grup, ok. 10%): reszta bez flagi. Użytkownik dostaje listę lematów z liczbami i zaznacza słowa warte karty. Kartę dostają tylko zaznaczone.
- **Warstwa odłożona** (107 grup, 0 z 33 ocenionych): flaga „lek” lub „angielski”. Bez karty, tylko w raporcie kwartału. Wraca, gdy słowo pojawi się w drugim korpusie, bo to znak, że weszło do języka potocznego (uwaga użytkownika o lekach i terminach).
- Wzrost w plenarnych (g ≥ 5) pokazujemy w karcie jako liczbę, ale nie odcinamy nim kandydatów.

### Konsekwencje
#### Dobre
- Zostają słowa tylko z PPC: patostreaming, neuroróżnorodność, praworządnościowy, wyszczepiać, receptomat.
- Pełne karty dostaje ok. 400 grup z trafnością ≥ 34%, a nie 875 z trafnością 35%.

#### Złe
- Oceny pochodzą od agenta. Warstwę plenarną oceniono w całości (78), ale resztę tylko na próbce (60 + 33). Przedziały są szerokie.
- Ok. 37 słów wartych gry zostaje w warstwie skróconej. Wyjdą tylko wtedy, gdy użytkownik przejrzy listę.
- Liczenie PPC musi zapisywać kategorię dokumentu (posiedzenia, komisje, interpelacje).
- Pliki pomiaru są w scratchpadzie sesji, poza repo: `/private/tmp/claude-501/-Users-robmar-Projects-Literaki/3ae5c44e-c8df-4ef9-924a-bcb0e5eaf7f8/scratchpad/nowe-slowa/projekt/` (`ppc_cat.py`, `plenarne.py`, `reguly.py`, `plenarne.json`, `oceny.json`, `oceny-p1.json`). Przy wdrożeniu trzeba je odtworzyć skryptem w repo.

---

## ADR-018: Przegląd kwartalny i pierwsza paczka w częściach

### Status
Proponowana (wybór użytkownika P1-B, 2026-11-03).

### Kontekst
PPC dostaje nowe teksty i anotację co kilka tygodni (ostatnia anotacja 2026-10-19). SGJP wydaje eksporty nieregularnie. Pierwsza pula to 875 grup z korpusów i 374 z NKJP → KWJP. Główny koszt to ręczny przegląd, nie obliczenia.

### Czynniki decyzji
- Przewidywalny rytm.
- Mały koszt jednej sesji przeglądu.
- Decyzje nie wracają bez nowego dowodu.

### Rozważane opcje
1. Przy każdym nowym eksporcie SGJP.
2. Kwartalnie, razem z odświeżeniem PPC.
3. Przy nowym korpusie (nowy rocznik Leipzig, nowa wersja ParlaMint).
4. Tylko na żądanie.

### Wynik decyzji
Wybrana opcja 2, bo PPC to jedyne źródło, które rośnie co kwartał. Szczegóły:
- **Kwartał:** pobierz bieżącą kadencję PPC, sprawdź nowy eksport SGJP, nowy rocznik Leipzig i nową wersję ParlaMint. Przelicz tylko to, co się zmieniło.
- **Rejestr decyzji** w repo: lemat (grupa form), werdykt (dodać / odrzucić / odłożyć), data, powód, plik decyzji. Odrzucony wraca tylko wtedy, gdy jego liczba wystąpień wzrośnie co najmniej trzykrotnie albo pojawi się w nowym źródle. Odłożony wraca w następnym kwartale.
- **Pierwsza paczka (~300 słów wartych gry) w częściach po ok. 50 kart.** Kolejność według ADR-017: próba na jednym słowie (antyszczepionkowiec), potem grupy z ≥ 2 korpusów (243, ok. 5 części), Leipzig-only (87, 2 części), warstwa plenarna PPC (73, 2 części), a na końcu lista skrócona PPC (365 lematów, bez kart). Lista 374 (NKJP → KWJP) to osobny strumień, ok. 8 części, od drugiego kwartału.
- **Kryteria oceny w karcie** (uwagi użytkownika): przymiotniki od nazw miejsc są dopuszczalne (RJP 2026, s. 51: pisze się je małą literą; potwierdzenie użytkownika przy pierwszym takim słowie); nazwy leków i terminy fachowe tylko wtedy, gdy weszły do języka potocznego.
- **SGJP podbijamy osobno** (D2-A), przed pierwszą częścią, a potem zawsze przed przeglądem, gdy jest nowy eksport.

### Konsekwencje
#### Dobre
- Jedna sesja to ok. 50 kart, czyli godzina pracy użytkownika.
- Rejestr zapobiega powtarzaniu tych samych decyzji.

#### Złe
- Kwartał bez nowego słowa wartego gry jest możliwy. Wtedy wynik to raport bez zmiany list.
- Każda część z werdyktem „dodać” to nowy build i aktualizacja wiki.
