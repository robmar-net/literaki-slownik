# Alternatywy: jak wychwytywać nowe, popularne słowa

Data: 2026-11-03 · Podstawa: `analysis/synthesis.md`, `outputs/research-report.md` · Pewność: średnia-wysoka

## TL;DR
- Sześć obszarów decyzji, po 3–4 alternatywy. Kolejność od bazowego: D1 → D2 → D3 → D4 → P1 → D5.
- Rekomendacja: **D1** suplement v2 słowo po słowie (próba: antyszczepionkowiec); **D2** podbić SGJP do 20261018 od razu; **D3** nowy ADR rozszerza ADR-006 o NKJP w metodzie, tylko poza buildem; **D4** ParlaMint-PL 5.0 + Leipzig news, tylko poza buildem; **P1** przegląd przy każdym nowym eksporcie SGJP, z kartą kandydata; **D5** wulwę odłożyć i mierzyć w każdym przeglądzie.
- Nic tu nie zmienia list. Każdy wpis to osobna decyzja użytkownika.

## Kluczowe decyzje
- **D1: suplement v2, słowo po słowie** — jedyna droga do słowa spoza SGJP; uchyla wariant A tylko dla wskazanych słów.
- **D2: SGJP 20261018 teraz** — +2 lematy (`muralista`, `muralistka`), bez zmiany polityki i licencji.
- **D3: NKJP w metodzie przez nowy ADR, poza buildem** — daje metodzie podstawę formalną; NKJP nie trafia do list.
- **D4: ParlaMint + Leipzig tylko jako narzędzie i liczby w karcie** — czysta licencja, bez zmiany kodu buildu.
- **P1: przegląd przy nowym eksporcie SGJP** — rytm wyznacza źródło leksemów, nie kalendarz.
- **D5: wulwa odłożona z pomiarem** — dziś brak dowodu w dopuszczonych źródłach; wraca w każdym przeglądzie.

## Otwarte pytania i ryzyka
- **D1:** ręczna fleksja to decyzja redakcyjna. Błąd wzoru daje złe formy na liście.
- **D1:** kod przyjmuje najwyżej 1 suplement. Suplement v2 musi zastąpić v1 w tym samym slocie albo wymaga zmiany kodu (do projektu rozwiązania).
- **D3:** trafność ok. 65% oceniał jeden agent. Miara g jest zgrubna (2 313 lematów z SGJP też przechodzi progi).
- **D4:** ParlaMint kończy się w 06.2022, Leipzig nie ma lat 2019–2020 i 2025. Słowa z lat 2023–2026 będą słabo widoczne.
- **D4:** Leipzig wolno brać tylko z plików do pobrania (CC BY 4.0). Strona i API mają CC BY-NC.
- **D5:** użytkownik może chcieć wulwę mimo słabego dowodu. Wtedy działa D5-A, ale tylko po D1-A.

---

## 1. Problem

### Pytanie badawcze
Czy istnieją dobre, naukowe, wiarygodne źródła słów nowych w polszczyźnie, ale popularnych (np. „wulwa”), i jak literaki-slownik może je systematycznie wychwytywać?

### Co ustaliło badanie (skrót)
- Źródło leksemów to tylko SGJP + `sgjp-supplement.tab`. SGJP rośnie wolno (F1).
- OJ UW i WSJP PAN są rzetelne, ale bez licencji danych: tylko dowód ręczny (F2, F3).
- Metoda progowa NKJP → KWJP (2011–2020): 374 kandydatów, ok. 65% trafnych (F10).
- Po 2020: ParlaMint-PL 5.0 i Leipzig news mają CC BY 4.0. FineWeb-2 i HPLT licencjonują tylko opakowanie (F7, F8).
- Wulwy nie ma w żadnym dopuszczonym źródle (§8 raportu).

### Pytania „Jak moglibyśmy…”
1. Jak wpuścić pojedyncze dobrze udokumentowane słowo spoza SGJP, nie otwierając zasobu dla korpusów? (D1)
2. Jak tanio wziąć to, co SGJP już dodał? (D2)
3. Jak dać metodzie wykrywania podstawę formalną? (D3)
4. Jak zobaczyć słowa po 2020 roku bez ryzyka licencji? (D4)
5. Jak sprawić, by przegląd kandydatów był regularny i powtarzalny? (P1)
6. Co zrobić ze słowem, które ktoś zna, a źródła go nie mają? (D5)

### Zależności
```
D1 (polityka wejścia) ──┬──> D5 (wulwa: A wymaga D1-A)
                        └──> P1 (bez D1-A karta kończy się raportem luki)
D3 (NKJP w metodzie) ───┐
D4 (korpus po 2020) ────┴──> P1 (co liczymy w karcie) ──> D5 (pomiar przy przeglądzie)
D2 (SGJP 20261018) — niezależna
```

---

## 2. Alternatywy

### D1. Jak dopuścić leksem spoza SGJP (bazowa)

**D1-A. Suplement v2, słowo po słowie** ⭐
Użytkownik decyduje o każdym słowie osobno. Słowo dostaje wiersze z pełną fleksją według wzoru podobnego leksemu SGJP, plik dowodów i nowy nagłówek suplementu. Dalej przechodzi te same filtry co leksem z SGJP.
- Plusy: pełna kontrola; mały koszt na słowo; zgodne z zasadą „decyzja użytkownika z przykładami”.
- Minusy: uchyla wariant A (dla wskazanych słów); ręczna fleksja; potrzebny nowy nagłówek i może zmiana limitu suplementów.
- Kiedy: gdy są słowa z silnym dowodem, jak antyszczepionkowiec (OJ UW + WSJP + KWJP 34 + ParlaMint 93, ok. 12 form).
- Dowód: F2, F3, F11; `projekt-zasady-zrodel.md` droga B.

**D1-B. Suplement v2, ale tylko do szerokiej listy (BROAD)**
Jak A, ale słowo spoza SGJP nie wchodzi do STANDARD. STANDARD zostaje „czystym SGJP”.
- Plusy: ostrożniej; STANDARD bez zmian w zasadach źródeł.
- Minusy: nowy wyjątek w filtrach; słowo popularne (np. antyszczepionkowiec) brakuje tam, gdzie gracz go oczekuje.
- Kiedy: gdy użytkownik chce próby bez ruszania głównej listy.
- Dowód: F11 (wariant A), zasada „nie zmieniamy reguł gry”.

**D1-C. Czekać na SGJP; tylko raport „luka źródła”**
Nic nie dodajemy. Kandydaci trafiają do raportu luk i wracają przy nowym eksporcie.
- Plusy: zero ryzyka redakcyjnego; nic nie zmienia polityki.
- Minusy: SGJP dodał 2 lematy w 2 miesiące; antyszczepionkowca nie ma od lat. Nowe słowa praktycznie nie wejdą.
- Kiedy: gdy użytkownik woli spójność źródła od aktualności.
- Dowód: F1.

**D1-D. Automatyczny wpis po progu korpusowym**
Kandydat, który przejdzie progi i ma potwierdzenie w Słowosieci, wchodzi bez decyzji.
- Plusy: skaluje się.
- Minusy: sprzeczne z §2.4/§4.4 („korpusy nie mogą automatycznie rozszerzać”); 35% szumu; fleksję i tak trzeba ustalić ręcznie.
- Kiedy: praktycznie nigdy przy obecnych zasadach. Pokazane dla porównania.
- Dowód: F10, F11.

### D2. SGJP 20261018 (niezależna)

**D2-A. Podbić teraz, osobno** ⭐
Nowy eksport, nowy build, aktualizacja wiki.
- Plusy: bez ryzyka; licencja (BSD-2) i polityka bez zmian; +`muralista`, `muralistka` z formami.
- Minusy: cały cykl buildu i wiki dla 2 lematów.
- Dowód: F1 (sha256 `346bd7bc…5be`, 348 420 lematów).

**D2-B. Podbić razem z pierwszym suplementem v2**
Jeden build, jedna zmiana wiki.
- Plusy: mniej cykli.
- Minusy: wiąże pewną zmianę z niepewną decyzją D1; trudniej ocenić wpływ każdej osobno.

**D2-C. Zostać przy 20260823 do większej różnicy**
- Plusy: zero pracy teraz.
- Minusy: lista świadomie starsza od źródła; przy rzadkich eksportach różnica rośnie wolno.

### D3. NKJP w metodzie wykrywania a ADR-006

**D3-A. Nowy ADR: NKJP jako baza „przed 2011” w metodzie, poza buildem** ⭐
ADR rozszerza dozwolone użycie NKJP (dziś POP, POP0) o liczenie wzrostu g. Wynik to lista kandydatów, nie wpis do list.
- Plusy: metoda już działa (5 z 5 kontroli celu); dane są w repo; NKJP ma już CC BY (ADR-006).
- Minusy: g jest zgrubne (lemat KWJP vs forma NKJP); trzeba utrzymać próg i filtry szumu.
- Dowód: F9, F10; NeoN (F5) ma podobne progi.

**D3-B. Bez NKJP: kandydat = częsty w KWJP i brak w SGJP**
Bez miary wzrostu. Lista „luk SGJP”, nie „nowych słów”.
- Plusy: nie trzeba ADR.
- Minusy: miesza stare luki z nowymi; więcej szumu; nie odpowiada na pytanie o „nowe”.
- Dowód: F10 (bez g próg przepuszcza dużo więcej lematów).

**D3-C. Baza czasu z jednego korpusu (np. ParlaMint 2015–2019 vs 2020–2022)**
Ten sam tager w obu okresach, więc g uczciwsze.
- Plusy: lepsza miara; bez NKJP.
- Minusy: jeden rejestr (polityka); mało tekstu; zależy od D4; nie widzi lat 2011–2014.
- Dowód: F7 (lockdown 0 do 2019, potem 111–176 rocznie).

### D4. Korpus po 2020 i jego miejsce

**D4-A. ParlaMint-PL 5.0 + Leipzig news, tylko poza buildem** ⭐
Służą do szukania kandydatów i do liczb w karcie (z atrybucją CC BY). Build się nie zmienia.
- Plusy: czysta licencja; daty; brak zmian kodu; widzi lockdown, covidowy, antyszczepionkowca (78 w 2021).
- Minusy: ParlaMint kończy się w 06.2022 i jest jednym rejestrem; Leipzig ma tylko formy i luki w latach.
- Dowód: F7; W6.

**D4-B. ParlaMint + Leipzig w buildzie jako `corpus_evidence`**
Nowy rodzaj artefaktu obok KWJP.
- Plusy: liczby po 2020 dostępne dla filtrów i raportów.
- Minusy: zmiana kodu (`14 + supplements`, `KINDS`), testów i ADR; korpusy są za małe na progi przy rzadkich słowach.
- Dowód: F11.

**D4-C. FineWeb-2 lub HPLT (po decyzji o licencji tekstu)**
- Plusy: ogromne, z datą i URL; widzą też rzadkie słowa (ghosting, cringe).
- Minusy: licencja obejmuje tylko opakowanie („We do not own any of the text”); szum (boomer w HPLT); pobranie ≫ 2 GB; kopie SJP.pl na innych domenach.
- Dowód: F8; W2, W5.

**D4-D. Żaden korpus; po 2020 tylko dowód ręczny (OJ UW, WSJP)**
- Plusy: nic nowego do utrzymania.
- Minusy: brak systematyczności; OJ UW ma inne kryterium „nowego” (hejt za stary); brak liczb.
- Dowód: F2, W4.

### P1. Proces: rytm przeglądu i karta kandydata (z syntezy)

**P1-A. Przegląd przy każdym nowym eksporcie SGJP** ⭐
Nowy eksport → odfiltruj kandydatów, którzy weszli do SGJP → policz resztę → karty dla top-N → decyzja użytkownika.
- Plusy: rytm wyznacza źródło leksemów; od razu widać, co SGJP „załatwił” sam.
- Minusy: nieregularny (zależy od PAN).

**P1-B. Kwartalnie, z kalendarza**
- Plusy: przewidywalnie.
- Minusy: często bez nowych danych (KWJP się nie zmienia, ParlaMint też nie).

**P1-C. Przy nowym korpusie (nowy rocznik Leipzig, nowa wersja ParlaMint)**
- Plusy: przegląd tylko, gdy są nowe liczby.
- Minusy: rzadko; słowa z SGJP mogą czekać.

**P1-D. Tylko na żądanie**
- Plusy: zero stałego kosztu.
- Minusy: brak systematyczności, czyli brak odpowiedzi na drugą część pytania.

**Karta kandydata (wspólna dla A–D):** lemat, klasa, liczby (KWJP F i gatunki, NKJP, g, ParlaMint rocznie, Leipzig rocznie), Słowosieć tak/nie, 2–3 przykłady z korpusu z dozwoloną licencją, linki OJ UW/WSJP z datą odczytu, typ szumu (błędny lemat, nazwa, angielski, termin), proponowany wzór fleksji z SGJP, przewidywana liczba form, werdykt: dodać / odrzucić / odłożyć.

### D5. Wulwa (zależy od D1 i P1)

**D5-A. Dodać teraz wyjątkiem**
Suplement v2, fleksja według wzoru `wagina` (ok. 10 form: wulwa, wulwy, wulwie, wulwę, wulwą, wulwo, wulw, wulwom, wulwami, wulwach).
- Plusy: spełnia wprost prośbę z pytania.
- Minusy: wymaga D1-A; dowód słaby (0 w korpusach z czystą licencją, kilka dokumentów sieciowych); tworzy precedens słowa bez dowodu.

**D5-B. Odłożyć i mierzyć w każdym przeglądzie** ⭐
Warunek wejścia: pojawi się w SGJP, OJ UW lub WSJP albo przejdzie progi w korpusie z dozwoloną licencją.
- Plusy: spójne z zasadą dowodu; mały koszt; łatwo zmienić decyzję później.
- Minusy: słowo czeka, może długo.

**D5-C. Odrzucić z zapisem „luka źródła”**
- Plusy: sprawa zamknięta.
- Minusy: trzeba będzie ją otwierać, gdy słowo się upowszechni; P1-B i tak by je mierzył.

---

## 3. Analiza kompromisów

Skala: **W** wysoka, **Ś** średnia, **N** niska. Dla ryzyka **N** jest dobre.

| Alt. | Wykonalność | Wpływ na graczy | Prostota | Ryzyko | Skalowalność |
|---|---|---|---|---|---|
| D1-A | W | W (słowa, których gracze używają) | Ś | Ś (fleksja ręczna) | Ś (ręcznie, słowo po słowie) |
| D1-B | Ś | Ś | N (nowy wyjątek filtrów) | N | Ś |
| D1-C | W | N | W | N | N (SGJP +2/2 mies.) |
| D1-D | Ś | Ś | Ś | W (35% szumu, sprzeczne z §2.4) | W |
| D2-A | W | N (+2 lematy) | W | N | — |
| D2-B | W | N | Ś | Ś (wiąże z D1) | — |
| D2-C | W | N | W | N | N |
| D3-A | W | Ś (pośrednio) | W | N | Ś (tylko 2011–2020) |
| D3-B | W | N | W | Ś (więcej szumu) | Ś |
| D3-C | Ś | Ś | Ś | Ś (mały korpus) | Ś |
| D4-A | W | Ś | W | N | Ś (do 2024, luki lat) |
| D4-B | Ś | Ś | N | Ś (kod, ADR) | Ś |
| D4-C | N | W | N | W (licencja tekstu) | W |
| D4-D | W | N | W | N | N |
| P1-A | W | Ś | W | N | W |
| P1-B | W | Ś | W | N | Ś (puste przebiegi) |
| P1-C | W | N | W | N | Ś |
| P1-D | W | N | W | Ś (brak rytmu) | N |
| D5-A | Ś (po D1-A) | Ś | Ś | Ś (precedens) | — |
| D5-B | W | N teraz | W | N | — |
| D5-C | W | N | W | N | — |

Wniosek z macierzy: zwycięzcy mają niskie ryzyko i nie zmieniają kodu buildu. Jedyną zmianą polityki jest D1-A, i to wąską (per słowo).

### Przykłady i wpływ na listy (decyzja użytkownika)
| Decyzja | Przykład | Wpływ |
|---|---|---|
| D1-A | antyszczepionkowiec | +1 leksem, ok. 12 form; STANDARD i BROAD wg zwykłych filtrów |
| D1-A (dalsze) | boomer | słaby dowód (WSJP, KWJP 5); SGJP ma `bumer`, więc najpierw pytanie o wariant pisowni |
| D1-A (z metody) | neoliberalny, prorosyjski, postsowiecki, performans, superbohater, kryptowaluta | każde osobno; formacje `anty-` i `post-` wymagają osobnej decyzji (§2.4) |
| D2-A | muralista, muralistka | +2 leksemy z formami |
| D3-A + D4-A | 374 kandydatów (125 z Słowosiecią, 23/24 trafnych) | lista do przeglądu, nie do list; ok. 240 prawdziwych leksemów do oceny |
| D5-A | wulwa | +1 leksem, ok. 10 form |

---

## 4. Preferencje użytkownika (z zasad projektu)
- Zmiany składu list decyduje użytkownik; pokazujemy przykłady i wpływ.
- Leksemy tylko z SGJP (§2.4/§4.4, wariant A), dopóki użytkownik tego nie zmieni.
- SJP.pl nie jest źródłem. Wikisłownik odroczony.
- Żadnego kontaktu z autorami zasobów ani innymi grupami. Źródła z formularzem, kontem albo mailem odpadają.
- Reguł gry (Kurnik + ZDS) nie zmieniamy.
- Każda zmiana źródeł lub list aktualizuje wiki.

---

## 5. Rekomendacja

**Zestaw: D1-A + D2-A + D3-A + D4-A + P1-A + D5-B.**

Kolejność wdrażania: D2-A (bez ryzyka) → D3-A (ADR) → D1-A na jednym słowie (antyszczepionkowiec) jako próba → D4-A → P1-A jako stały rytm → D5-B w pierwszym przeglądzie.

**Dlaczego:** rozdziela wykrywanie od wejścia do list. Wykrywanie jest systematyczne i poza buildem (D3, D4, P1). Wejście jest ręczne i wąskie (D1). Jedyna zmiana polityki dotyczy pojedynczych słów z dowodem.

**Kompromisy, które przyjmujemy:**
- ręczna fleksja i ręczny przegląd: wolno, ale bezpiecznie;
- słaba widoczność lat 2023–2026 (ParlaMint do 06.2022, Leipzig do 2024);
- rzadkie słowa (ghosting, cringe, wulwa) nie wejdą szybko.

**Założenia (jeśli są fałszywe, rekomendacja się zmienia):**
1. Użytkownik zgodzi się uchylić wariant A dla pojedynczych słów. Jeśli nie: D1-C, a reszta zostaje jako raport luk.
2. Wzór fleksji z podobnego leksemu SGJP wystarczy dla większości kandydatów.
3. CC BY 4.0 ParlaMint i Leipzig pozwala na liczby i krótkie przykłady w karcie z atrybucją.
4. SGJP dalej będzie publikował eksporty co kilka miesięcy (rytm P1-A).
5. Trafność ok. 65% utrzyma się przy ocenie użytkownika. Jeśli spadnie, trzeba ostrzejszych progów (np. F ≥ 30: 246 kandydatów).

**Pewność:** średnia-wysoka. Wysoka dla D2, D3, D4 (licencje i dane sprawdzone). Średnia dla D1 i P1 (koszt ręczny nieznany do pierwszej próby).

## 6. Dlaczego nie inne
- **D1-B:** dodaje nowy wyjątek w filtrach, a popularne słowo i tak powinno być w STANDARD. Dobre jako wariant ostrożny, gdyby użytkownik chciał.
- **D1-C:** SGJP nie nadąża; pytanie o systematyczne wychwytywanie zostaje bez odpowiedzi.
- **D1-D:** łamie §2.4/§4.4 i decyzję per słowo; 35% szumu.
- **D2-B:** wiąże pewną zmianę z niepewną.
- **D2-C:** świadomie starsza lista bez zysku.
- **D3-B:** nie odróżnia nowego od starego.
- **D3-C:** dobra miara, ale za mały i jednorodny korpus jako jedyna baza; można dodać później jako kontrolę.
- **D4-B:** zmiana kodu bez potrzeby, póki liczby służą tylko karcie.
- **D4-C:** licencja tekstu nieustalona i nie da się jej ustalić bez kontaktu.
- **D4-D:** brak liczb i rytmu.
- **P1-B, P1-C:** puste albo zbyt rzadkie przeglądy. **P1-D:** brak systematyczności.
- **D5-A:** słowo bez dowodu w dopuszczonych źródłach; precedens. Dostępne, jeśli użytkownik tak zdecyduje (wymaga D1-A).
- **D5-C:** zamyka sprawę, którą i tak trzeba będzie mierzyć.

## 7. Odłożone pomysły
- **Licencja tekstu FineWeb-2 i HPLT** — do osobnej decyzji użytkownika; bez niej D4-C zablokowane.
- **Uczciwa miara g** (lematy w obu okresach jednym tagerem) — poprawi trafność; poza zakresem tej decyzji.
- **Filtr typu NeoN** (wielka litera, nazwa własna, odległość edycyjna) jako dodatkowe sito szumu.
- **Wariant pisowni boomer/bumer** — osobne pytanie o warianty pisowni.
- **Reforma pisowni RJP od 2026** — może zmienić formy w listach; osobny temat.
- **Leipzig 2025** — sprawdzić w przeglądzie, gdy wyjdzie.
- **Starsze luki SGJP z metody** (neoliberalny, kryptowaluta…) — to nie neologizmy po 2020; mogą iść tą samą drogą D1-A, ale osobną partią.
