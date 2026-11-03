# Raport: źródła nowych, popularnych słów

Typ: mieszany (literatura + technika) · Data: 2026-11-03 · Wykonawca: agent research-synthesizer (maister)
Podstawa: 10 plików ustaleń w `analysis/findings/`, synteza w `analysis/synthesis.md`.

## TL;DR
- Naukowe źródła nowych słów istnieją. Najlepsze to **Obserwatorium Językowe UW** i **WSJP PAN**. Żadne nie ma jednak licencji danych, więc może być tylko **dowodem ręcznym**, a nie źródłem leksemów.
- Źródłem leksemów zostaje SGJP. Rośnie on wolno: eksport 20261018 dodaje 2 lematy.
- Wychwytywanie da się zrobić metodą progową: korpus z datami, lista kandydatów, decyzja użytkownika, suplement v2. Dziś działa na latach 2011–2020 (374 kandydatów, ok. 65% trafnych). Dla lat po 2020 kandydatami na korpus są **ParlaMint-PL 5.0** i **Leipzig news** (CC BY 4.0).
- **Wulwy nie ma w żadnym dopuszczonym źródle.** Można ją dodać tylko suplementem v2, decyzją użytkownika, przy słabym dowodzie.

## Kluczowe decyzje (do podjęcia przez użytkownika)
1. **Czy dopuścić leksemy spoza SGJP przez suplement v2** (uchylenie wariantu A dla pojedynczych słów). Przykład pierwszego słowa: antyszczepionkowiec. Alternatywa: czekać na SGJP. Wpływ: każde słowo wymaga ręcznego paradygmatu i pliku dowodów.
2. **Czy podbić SGJP do 20261018.** Zysk: `muralista`, `muralistka`. Licencja się nie zmienia, polityka też nie.
3. **Czy rozszerzyć ADR-006 o użycie NKJP w metodzie wykrywania.** Dziś ADR-006 obejmuje tylko POP i POP0.
4. **Jaki korpus ma dawać dowód po 2020 roku:** ParlaMint-PL 5.0 i Leipzig news (czysta licencja, małe), FineWeb-2 lub HPLT (duże, licencja tekstu nieustalona), czy żaden.
5. **Co z wulwą:** dodać wyjątkiem przez suplement v2, odłożyć do ponownego pomiaru albo odrzucić z zapisem „luka źródła”.

## Otwarte pytania i ryzyka
- **Licencja tekstu w FineWeb-2 i HPLT.** Licencjonują one tylko opakowanie („We do not own any of the text”). Pochodna lista słów może naruszać prawa autorów stron.
- **Leipzig ma dwie licencje.** Strona i API: CC BY-NC. Korpusy do pobrania: CC BY 4.0. Wolno używać tylko plików do pobrania.
- **Trafność metody (65%)** oceniał jeden agent, bez konkordancji. Miara wzrostu g jest zgrubna.
- **Szum:** błędne lematy KWJP, nazwy własne (boomer w HPLT), angielskie frazy (Anti-ghosting), znaczenia specjalistyczne (wulwa w zoologii).
- **Skażenie SJP.pl** w korpusach sieciowych jest małe (1/36 574 dokumentów w FineWeb-2) i da się je wykluczyć po URL. Kopie na innych domenach mogą jednak przejść filtr.

---

## Spis treści
1. Streszczenie
2. Cel i zakres
3. Metodologia
4. Ustalenia
5. Analiza
6. Wnioski
7. Rekomendacje i decyzje
8. Przypadek „wulwa”
9. Załączniki

## 1. Streszczenie
Badanie sprawdziło 26 źródeł w dwóch grupach: 11 słowników i rejestrów oraz 15 korpusów i list. Sprawdziło też zasady i kod projektu. Każde źródło zmierzono na 9 słowach kontrolnych. Cztery z nich są w SGJP, pięć nie.

Wynik ma trzy części. Po pierwsze, rejestry naukowe istnieją, ale nie mają licencji danych. Po drugie, korpusy z czystą licencją i datami istnieją, ale są małe albo jednorodne. Po trzecie, metoda progowa działa, ale dziś tylko na latach 2011–2020. Głównym ograniczeniem nie jest technika, tylko polityka: wariant A i zasada §2.4/§4.4 (leksemy tylko z SGJP).

## 2. Cel i zakres
**Pytanie:** czy istnieją dobre, naukowe i wiarygodne źródła słów, które są w polszczyźnie od niedawna, ale są popularne, i jak literaki-slownik może je systematycznie wychwytywać?

**Podpytania:** kto rejestruje neologizmy; które korpusy mają lata 2015+ i daty; czy pochodną listę wolno opublikować; wynik kontroli; jak źródło wchodzi do `sources.json`; jaka metoda i progi.

**Poza zakresem:** SJP.pl (nie jest źródłem), Wikisłownik (odroczony decyzją użytkownika z 2026-10-04), kontakt z autorami i innymi grupami (źródła wymagające formularza, konta albo maila są BLOCKED), zmiany w listach.

## 3. Metodologia
- **Trzy kategorie zbierania:** `neolog` (rejestry i słowniki, 4 pliki), `korpusy` (korpusy z datami, 3 pliki), `projekt` (zasady repo, kontrole lokalne, metoda progowa, 3 pliki).
- **Kontrole:** hejt, lockdown, covidowy, influencerka (w SGJP); antyszczepionkowiec, boomer, ghosting, cringe, wulwa (spoza SGJP). Każde „brak” ma kontrolę dodatnią w tym samym źródle.
- **Dane:** strony i licencje (cytaty z URL, odczyt 2026-11-03), pobrania w scratchpadzie (SGJP 20261018, ParlaMint-PL, LCC 2024, próbki FineWeb-2 i HPLT), lokalne `cache/` (SGJP 20260823, KWJP100, NKJP 1grams, Słowosieć 4.5).
- **Ocena źródła:** `ALLOWED` / `ALLOWED-kandydat` / `do decyzji` / `tylko dowód ręczny` / `BLOCKED`.

## 4. Ustalenia

### Trzy role źródeł
| Rola | Co robi | Dziś w projekcie |
|---|---|---|
| **(a) źródło leksemów** | tworzy leksemy z fleksją w generatorze | SGJP 20260823 + `sgjp-supplement.tab` (4 formy zaimka zwrotnego) |
| **(b) dowód użycia** (`corpus_evidence`) | liczby z korpusu, nie tworzą leksemów | 13 artefaktów KWJP100 (CC BY 4.0, próg 5) |
| **(c) dowód ręczny** | link i data odczytu w karcie kandydata | nic formalnie; tu: OJ UW, WSJP, PWN, plebiscyty |

Poprawka planu: `sources.json` ma **13 artefaktów KWJP** (4 `kwjp_lemma`, 4 `kwjp_orth`, 4 `kwjp_orth_lc`, 1 `kwjp_bigram`). Liczba 15 obejmuje też SGJP i suplement.

### F1. SGJP rośnie wolno — pewność wysoka
Eksport 20261018 (BSD-2-Clause, sha256 `346bd7bc…5be`) ma 348 420 lematów. Względem 20260823 to +2 (`muralista`, `muralistka`). Między czerwcem a sierpniem przybyło 137 lematów, alfabetycznie (C–D). To przegląd słownika, a nie rejestr neologizmów. Kontrole są bez zmian. *Źródło: `neolog-slowniki.md` §1.*

### F2. OJ UW to najlepszy rejestr, ale bez licencji — pewność wysoka
Słownik ma 2756 haseł. Ostatnie hasło pochodzi z 2026-10-30, a w 2026 roku przybyło 280 haseł. Kryterium to „co najmniej 10 poświadczeń w co najmniej 5 tekstach po 2003” i brak w 8 słownikach sprzed 2003. Regulamin, § 7: treści „są przedmiotem praw autorskich”. Licencji danych i eksportu brak. Kontrole: jest lockdown i antyszczepionkowiec; hejt trafił do negatywnej weryfikacji („za stary”); `cringe-owy` jest tylko jako przymiotnik. Wulwy, ghostingu i boomera nie ma. Ocena: **tylko dowód ręczny**. *Źródło: `neolog-ojuw.md`.*

### F3. WSJP PAN ma luki SGJP, bez licencji — pewność wysoka
WSJP ma 100 tys. haseł (01.2026). Ma **antyszczepionkowca** (pot.) i **boomera** (pokolenie wyżu, pogard.). Nie ma ghostingu, cringe ani wulwy. Licencji brak, jest tylko „Copyright© IJP PAN”. Ocena: **tylko dowód ręczny** (spec §4.4). *Źródło: `neolog-slowniki.md` §2.*

### F4. PWN i Słowosieć 5.0 są BLOCKED — pewność wysoka
Regulamin PWN pozwala „jedynie w zakresie własnego użytku osobistego”. Pełne zrzuty Słowosieci 5.0 są udostępniane „po weryfikacji zgłoszenia”, czyli przez formularz. Słowosieć 4.5 zostaje według ADR-011. *Źródło: `neolog-slowniki.md` §3–4.*

### F5. NeoN (IPI PAN, 2025) to metoda bez danych — pewność wysoka
Artykuł ma licencję CC BY 4.0 (arXiv:2505.15426). Progi: DF > 5 dokumentów, ≥ 5 wystąpień małą literą, ≥ 5 nie jako nazwa własna, długość 3–20, odległość edycyjna > 0,5. Lejek: 200 696 → 1056. Precyzja 0,917 po filtrze LLM, recall 0,699. Kodu i listy nie udostępniono. Ocena: **punkt odniesienia dla metody**. *Źródło: `neolog-inne.md` §5.*

### F6. Plebiscyty dają sygnał popularności, bez danych — pewność średnia
Młodzieżowe Słowo Roku (PWN, od 2016) i Słowo Roku (UW i FJP) mają po 15–21 słów rocznie. Cringe był w finale MSR 2024. Licencji brak, a lista MSR jest znana tylko z prasy. Ocena: **tylko dowód ręczny**. *Źródło: `neolog-inne.md` §1–2.*

### F7. Dowód użycia po 2020: ParlaMint-PL 5.0 i Leipzig news — pewność wysoka
| | ParlaMint-PL 5.0 | Leipzig `pol_news_*` |
|---|---|---|
| Licencja | CC BY 4.0 (całość) | CC BY 4.0 (pliki do pobrania); strona i API CC BY-NC |
| Okres | 2015-11-12 – 2022-06-30 | 2018, 2021–2024 |
| Rozmiar | 37,0 mln słów | ~15,7 mln tokenów na rocznik |
| Daty | dzienne | rocznik |
| Ryzyko SJP.pl | brak | 0 z 179 903 URL-i |
| Ograniczenia | jeden rejestr (polityka) | tylko formy, zdania przetasowane, brak 2019–2020 i 2025 |

Ocena obu: **ALLOWED-kandydat `corpus_evidence`**. ParlaMint dobrze pokazuje datę wejścia słowa: lockdown i covidowy mają 0 do 2019 roku, potem 111–176 rocznie; antyszczepionkowiec ma 78 w 2021. *Źródło: `korpusy-01`, `korpusy-02`, `korpusy-03`.*

### F8. FineWeb-2 i HPLT: najlepsze technicznie, licencja do decyzji — pewność wysoka
Oba mają dziesiątki miliardów słów, a przy każdym dokumencie datę i URL. Domenę `sjp.pl` da się wykluczyć: w próbkach było 1/36 574 i 0/21 656 dokumentów. Licencja obejmuje tylko opakowanie (ODC-By, CC0), a tekst należy do autorów stron. Ocena: **do decyzji**. OSCAR i CulturaX wymagają konta, a MADLAD-400 ma sprzeczną licencję i brak URL, więc wszystkie trzy są **BLOCKED**. CC-100 ma licencję „unknown”. Google Books Ngram nie ma polskiego. *Źródło: `korpusy-01`, `korpusy-03`.*

### F9. KWJP to lata 2011–2020, NKJP do 2010 — pewność wysoka
„Przed KWJP” oznacza więc słowa po 2020 roku. Nowszych list niż commit `26d82bd8` nie ma. *Źródło: `korpusy-01` (10), `projekt-kontrole-lokalne`.*

### F10. Metoda progowa NKJP → KWJP działa — pewność średnia
Progi: **F ≥ 20, 1-DP ≥ 0,005, ≥ 2 z 3 gatunków KWJP, wzrost g ≥ 10.** Łapią 5 z 5 kontroli celu: hejt, lockdown, covidowy, influencerkę i antyszczepionkowca. Odrzucają `srom` (g = 1,8). Lista wynosi 530 lematów, po filtrach szumu 374, a z potwierdzeniem w Słowosieci 125. Trafność w próbce 60: ok. 65%; z Słowosiecią 23/24, bez niej 16/36. Nie łapie wulwy, ghostingu, cringe ani boomera (KWJP F ≤ 5). Progów pod nie nie strojono. **Użycie NKJP wykracza poza ADR-006 (POP, POP0) i wymaga decyzji.** *Źródło: `projekt-metoda.md`.*

### F11. Kod i polityka blokują nowe leksemy — pewność wysoka
- §2.4 i §4.4 specyfikacji v3: leksemy tylko z SGJP, a korpusy „nie mogą automatycznie rozszerzać” zasobu.
- Wariant A (`.maister/tasks/development/2026-10-04-generator-broad-standard/analysis/evidence/source-extension-decision.md`): „Nie rozszerzać zasobu leksemów”.
- `inputs.py`: w trybie produkcyjnym `len(artifacts) == 14 + supplements` i `supplements ≤ 1`. Nowego korpusu ani drugiego suplementu nie da się dodać bez zmiany kodu.
- Nagłówek suplementu v1 („brak w eksporcie TSV, obecne w opisie SGJP”) nie pasuje do neologizmów. Potrzebna jest więc wersja v2.

*Źródło: `projekt-zasady-zrodel.md`.*

### Tabela kontroli (skrót)
| Słowo | SGJP | OJ UW | WSJP | KWJP lemat | NKJP | ParlaMint | LCC 2024 | FineWeb-2 próbka (dok.) | HPLT próbka (dok.) |
|---|---|---|---|---|---|---|---|---|---|
| hejt | + | NW (za stary) | + | 366 | 2 | 366 | 294 | 123 | 42 |
| lockdown | + | + | + | 241 | 0 | 316 | 31 | 63 | 35 |
| covidowy | + | − (stara +) | + | 116 | 0 | 349 | 28 | 39 | 19 |
| influencerka | + | − (stara +) | − | 24 | 0 | 1 | 96 | 15 | 11 |
| antyszczepionkowiec | − | + | + | 34 | 0 | 93 | 8 | 11 | 4 |
| boomer | − (`bumer`) | − | + | 5 | 10 (EN?) | 0 | 10 | 11 | 70 ⚠ |
| ghosting | − | − | − | <5 | 1 | 0 | 3 | 3 (1 szum) | 1 |
| cringe | − | `cringe-owy` | − | <5 | 0 | 0 | 2 | 0 | 2 |
| wulwa | − | − | − | <5 | 2 (nazwisko) | 0 | 0 | 2 | 3 |

### Podsumowanie ustaleń
| # | Ustalenie | Kategoria | Pewność |
|---|---|---|---|
| F1 | SGJP 20261018: +2 lematy | neolog | wysoka |
| F2 | OJ UW: najlepszy rejestr, bez licencji, kryterium „po 2003” | neolog | wysoka |
| F3 | WSJP: ma antyszczepionkowca i boomera, bez licencji | neolog | wysoka |
| F4 | PWN, Słowosieć 5.0: BLOCKED | neolog | wysoka |
| F5 | NeoN: metoda, bez danych | neolog | wysoka |
| F6 | Plebiscyty: sygnał, bez danych | neolog | średnia |
| F7 | ParlaMint-PL 5.0, Leipzig news: kandydaci `corpus_evidence` | korpusy | wysoka |
| F8 | FineWeb-2, HPLT: licencja tekstu do decyzji | korpusy | wysoka |
| F9 | KWJP 2011–2020, NKJP do 2010 | korpusy/projekt | wysoka |
| F10 | Metoda progowa: 374 kandydatów, ~65% | projekt | średnia |
| F11 | Polityka i kod blokują leksemy spoza SGJP | projekt | wysoka |

## 5. Analiza

### Wzorce
- **W1. Świeżość i licencja wykluczają się.** Źródła, które szybko notują nowe słowa (OJ UW, WSJP, MSR, MoncoPL), nie mają licencji. Źródła z licencją (SGJP, KWJP) są wolne albo stare.
- **W2. Licencja opakowania to nie licencja tekstu** (FineWeb-2, HPLT, OSCAR).
- **W3. Bramka dostępu oznacza BLOCKED** (Słowosieć 5.0, OSCAR, CulturaX).
- **W4. Trzy różne definicje „nowego”:** OJ UW (po 2003), NeoN (poza NKJP i KWJP), projekt (poza SGJP). Hejt jest „stary” dla OJ UW i „nowy” dla nas.
- **W5. Szum ma stałe typy:** błędny lemat, nazwa własna, fraza angielska, znaczenie specjalistyczne.
- **W6. Rejestr korpusu decyduje o tym, co widać.** ParlaMint ma covid, ale nie influencerkę. Prasa ma influencerkę.

### Kluczowe spostrzeżenia
1. **Wykrywanie i wejście do list to dwa różne problemy.** Wykrywanie da się zrobić na korpusach. Wejście wymaga źródła z fleksją i licencją, a takiego poza SGJP nie ma.
2. **Pierwszym ograniczeniem jest polityka.** Nawet najlepszy dowód nie doda słowa, dopóki obowiązuje wariant A.
3. **Antyszczepionkowiec to naturalny pierwszy przypadek.** Ma wszystkie trzy rodzaje dowodu.
4. **Po 2020 roku metoda jest ślepa** bez nowego korpusu.
5. **Wulwa nie jest jeszcze mierzalnie popularna.** Ma kilka dokumentów sieciowych i 0 w korpusach z czystą licencją.

### SWOT metody wykrywania
| Mocne | Słabe |
|---|---|
| skalibrowana na kontrolach; zgodna z NeoN; dane już w repo; wynik to lista, a nie wpis | tylko lata 2011–2020; g zgrubne; 35% szumu; trafność oceniona przez jednego agenta |
| **Szanse** | **Zagrożenia** |
| ParlaMint i Leipzig dają oś czasu po 2020; Słowosieć porządkuje listę; OJ UW i WSJP jako dowód ręczny | NKJP poza ADR-006; licencja FineWeb-2 i HPLT; ręczna fleksja w suplemencie (decyzja redakcyjna); skażenie kopiami SJP.pl |

## 6. Wnioski
1. **Odpowiedź na pytanie:** tak, wiarygodne naukowe źródła istnieją (OJ UW, WSJP PAN; NeoN jako metoda). Żadne nie może być źródłem leksemów, bo brak licencji danych. Mogą być dowodem ręcznym. — pewność **wysoka**.
2. **Systematyczne wychwytywanie** jest możliwe jako proces: korpus z datami, progi, karta kandydata, decyzja użytkownika, suplement v2. Dla lat 2011–2020 jest gotowe, a dla lat po 2020 wymaga nowego korpusu. — pewność **średnia-wysoka**.
3. **Bez decyzji użytkownika nic się nie zmienia.** Zmiana wymaga uchylenia wariantu A, rozszerzenia ADR-006 i zmiany kodu dla nowego korpusu. — pewność **wysoka**.

Dodatkowo metoda ujawnia starsze luki SGJP (neoliberalny, prorosyjski, postsowiecki, performans, superbohater, kryptowaluta). Część z nich znana jest od rundy 4. Formacje z `anty-` i `post-` wymagają osobnej decyzji (§2.4).

**Pewność ogólna: średnia-wysoka.** Krajobraz źródeł i licencje mają pewność wysoką, metoda i próbki sieciowe średnią.

## 7. Rekomendacje i decyzje
Każdą zmianę składu list przedstawiamy użytkownikowi z przykładami, alternatywami i wpływem. Niżej są propozycje, a nie rozstrzygnięcia.

| # | Decyzja | Przykład | Alternatywy | Wpływ | Wysiłek |
|---|---|---|---|---|---|
| D1 | Dopuścić leksemy spoza SGJP przez suplement v2 | antyszczepionkowiec (OJ UW + WSJP + KWJP 34 + ParlaMint 93), boomer (WSJP + KWJP 5) | (a) tak, słowo po słowie; (b) nie, czekać na SGJP; (c) tylko raport „luka źródła” | uchyla wariant A; ręczna fleksja; wpis do STANDARD i BROAD; zmiana wiki | mały na słowo |
| D2 | Podbić SGJP do 20261018 | `muralista`, `muralistka` | zostać przy 20260823 | +2 lematy, bez zmiany polityki | mały |
| D3 | Rozszerzyć ADR-006 o NKJP w metodzie | lista 374 kandydatów 2011–2020 | nie używać NKJP; czekać na drugi okres z jednym tagerem | podstawa formalna metody; NKJP nadal poza buildem | mały (ADR) |
| D4 | Korpus „po 2020” | ParlaMint-PL 5.0 + Leipzig news | FineWeb-2/HPLT po decyzji o licencji; żaden | tylko poza buildem: brak zmian kodu; w buildzie: nowy `kind`, zmiana `14 + supplements`, ADR | średni–duży |
| D5 | Rytm przeglądu | przy każdym eksporcie SGJP lub raz na kwartał | tylko przy nowym KWJP | regularna karta kandydatów | mały |

Proponowana kolejność: D2 (bez ryzyka), potem D3 i D1 na jednym słowie (antyszczepionkowiec) jako próba, potem D4.

## 8. Przypadek „wulwa”
**Stan na 2026-11-03:**
- (a) źródło leksemów: brak. SGJP 20261018 ma tylko nazwisko `Wulw`.
- (b) dowód użycia: brak w korpusach z czystą licencją (KWJP <5, ParlaMint 0, LCC 2024 0). W próbkach sieciowych są 2 dokumenty FineWeb-2 (2020, 2022) i 3 dokumenty HPLT, a licencja tych źródeł jest do decyzji. W Wikipedii słowo występuje głównie jako termin zoologiczny. NKJP ma 2 wystąpienia, najpewniej nazwisko.
- (c) dowód ręczny: brak w OJ UW (także w negatywnej weryfikacji), WSJP, PWN i Miejskim. Słowosieć 4.5 ma tylko `wulwodynię`.

**Co dziś da się zrobić:** dodać ją przez **suplement v2**, wyłącznie decyzją użytkownika jako świadomy wyjątek: wiersze z pełną fleksją według wzoru `wagina` (to decyzja redakcyjna), nowy nagłówek, plik dowodów. Metoda progowa jej nie zaproponuje, a dowód jest dziś słaby.

**Opcje dla użytkownika:**
1. Dodać teraz wyjątkiem (suplement v2, wzór `wagina`).
2. Odłożyć i mierzyć przy każdym przeglądzie: OJ UW, nowy SGJP, Leipzig 2025, gdy się ukaże.
3. Odrzucić z zapisem „luka źródła” (jak w rundzie 4).

Pewność: **wysoka** co do braku w źródłach dopuszczonych, **średnia** co do popularności w sieci (małe próbki).

## 9. Załączniki

### A. Źródła (26 + lokalne)
- **neolog (11):** OJ UW (nowa i stara witryna), SGJP 20261018, WSJP PAN, PWN, Słowosieć 5.0, Młodzieżowe Słowo Roku, Słowo Roku UW/FJP, RJP PAN, Miejski Słownik Slangu (kontrola), NeoN.
- **korpusy (15):** ParlaMint-PL 5.0, Leipzig news, FineWeb-2, HPLT, MADLAD-400, OSCAR, CulturaX, CC-100, MoncoPL, KWJP100, Wikipedia i Wikinews, PPC, Spokes, Google Books Ngram, n-gramy CC.
- **lokalne:** `cache/sgjp/sgjp-20260823.tab.gz`, `cache/kwjp/*`, `cache/nkjp/1grams.gz`, `cache/plwordnet/` (4.5), `config/generator/sources.json`, `literaki_slownik/inputs.py`, spec v3, ADR-006, ADR-011.
- **Wyłączone:** SJP.pl, PoliMorf, Wikisłownik (odroczony 2026-10-04).

### B. Luki
- brak historii dat haseł SGJP (kalibracji „przed wejściem do SGJP” nie da się zrobić);
- ParlaMint liczony na formach, a nie lematach;
- próbki sieciowe <0,03% korpusu;
- okres PPC po 2018, licencja Spokes, dostępność MoncoPL;
- licencja OJ UW i WSJP do ustalenia tylko kontaktem (zabronionym).

### C. Pliki
- Ustalenia: `analysis/findings/neolog-00-przeglad.md`, `neolog-ojuw.md`, `neolog-slowniki.md`, `neolog-inne.md`, `korpusy-01-przeglad.md`, `korpusy-02-kontrole.md`, `korpusy-03-licencje.md`, `projekt-zasady-zrodel.md`, `projekt-kontrole-lokalne.md`, `projekt-metoda.md`.
- Pomiary (scratchpad, poza repo): `/private/tmp/claude-501/-Users-robmar-Projects-Literaki/3ae5c44e-c8df-4ef9-924a-bcb0e5eaf7f8/scratchpad/nowe-slowa/` (`kalibracja2.py/json`, `kalibracja3.py/json`, `kontrole.py/json`, pobrania z sha256).
- Poprzednie badanie: `.maister/tasks/research/2026-11-03-wulwa-brak-w-zrodlach/outputs/research-report.md`.
