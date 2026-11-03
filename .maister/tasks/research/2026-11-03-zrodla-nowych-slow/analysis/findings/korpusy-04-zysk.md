# korpusy: zysk z ParlaMint-PL, Leipzig news PL i PPC

## TL;DR
- **Najwięcej daje PPC.** Ma teksty do **2026-10-16**, 316 mln słów z lat 2015–2026, i da się go pobrać bez konta. Sam w sobie jest jednak bardzo zaszumiony.
- Po filtrach i z kryterium wzrostu zostaje łącznie **875 grup form** (przybliżonych leksemów) o n ≥ 20, które są nowe po 2019 roku, nie ma ich w SGJP 20261018 ani na liście 374. 811 z nich ma w KWJP F < 20. Prawie cały zysk to więc realny przyrost wobec metody NKJP→KWJP: wspólnych z listą 374 jest tylko 28.
- Słów wartych gry jest około **300 (pewnie 250–400)**. To wynik ręcznej oceny 100 kandydatów: 34% w próbce losowej, 70% wśród kandydatów obecnych w ≥ 2 korpusach, ok. 18% wśród kandydatów tylko z PPC.
- Kontrole: lockdown, covidowy i pandemia przechodzą wszędzie. Antyszczepionkowiec przechodzi w ParlaMint i PPC, influencerka tylko w Leipzig. **Boomer, ghosting, cringe i wulwa nie wychodzą nigdzie** (w każdym korpusie jest ich 0–23 wystąpień). Te trzy korpusy ich nie złapią.
- ParlaMint wnosi mało, bo kończy się w VI 2022 i ma 36 mln słów: 16 nowych grup przy n ≥ 20. Leipzig daje 154, głównie słownictwo wojny i mediów.

## Kluczowe decyzje
- **Jednostka to grupa form, nie lemat.** Lematyzator stanza w ParlaMint i PPC zostawia nieznane słowo jako lemat = forma (np. `lockdownu` → lemat `lockdownu`). Lematy spoza SGJP są więc w praktyce formami. Grupuję je przez ucięcie końcówki fleksyjnej (`covidowych`, `covidowe` → `covidow`). To przybliżenie: część leksemów się rozpada (`ługańsk` / `ługański`), więc liczby grup są zawyżone o ok. 10%.
- **Wzrost:** g = (ipm po) / (ipm przed), z +0,5 do liczby wystąpień i z normalizacją przez medianę dla słów z SGJP. Przedziały: ParlaMint i PPC 2015–2019 → 2020+, Leipzig 2018 → 2021–2024. „Nowe” znaczy: g ≥ 5, po ≥ 10, obecne w ≥ 3 latach okresu „po” (w ParlaMint we wszystkich trzech).
- **Filtry szumu:** tylko litery polskie, długość ≥ 3, większość użyć małą literą i nie PROPN, nie angielskie słowo bez polskiej odmiany, nie literówka (1 edycja od formy SGJP ≥ 10× częstszej), nie ucięta forma (`wiadczeniu` ← `świadczeniu`), nie etykieta domeny (`tvnmeteo.pl`), nie pojedynczy fragment będący prefiksem lub sufiksem formy SGJP (`ewid`, `techn`, `ązku`). Ostatni filtr zabiera też trochę prawdziwych słów (np. `pełnoletniość`).
- Leipzig ma tylko formy. Forma obecna w SGJP oznacza słowo znane. Formy grupuję tak samo jak lematy.

## Otwarte pytania
- Czy przymiotniki od nazw miejsc (`ługański`, `biełgorodzki`, `mariupolski`) wchodzą do gry? W Leipzig to ok. 25% „nowych”.
- Czy nazwy leków i terminy fachowe z interpelacji (trastuzumab, pertuzumab, ogólnospławny) w ogóle rozważamy? W PPC to ok. 30% puli.
- Miara wzrostu w PPC jest słaba: 15,6% słów znanych z SGJP też ją przechodzi (zob. kalibrację). Przed listą do decyzji trzeba albo liczyć wzrost tylko w posiedzeniach plenarnych, albo wymagać ≥ 2 korpusów.
- Licencja PPC: dane to domena publiczna, anotacja CC BY. Dla pochodnej listy słów wystarczy podanie źródła. Brakuje decyzji, czy wpisujemy PPC do `sources.json`.

## 1. PPC: co to jest (odczyt 2026-11-03)
- Pobieranie bez konta: `https://kdp.ipipan.waw.pl/static/ppcdump-tei/<kadencja>-tei.zip` (link ze strony `clip.ipipan.waw.pl/PPC`). Repozytorium git na `git.nlp.ipipan.waw.pl` nie obsługuje częściowego klonu. Płytki klon się zrywa.
- Pobrałem trzy kadencje, razem 11,4 GB: 2015-2019 (3,79 GB, sha256 `e1b62b56…2052`), 2019-2023 (4,92 GB, `fe1a95be…a2f2`), 2023-2027 (2,70 GB, `d556a686…3ccd`).
- Format: katalog na dokument z `header.xml` (data), `text_structure.xml` (TEI) i `anno.ccl.gz` (CCL, stanza: orth, lemma, upos, xpos; anotacja z 2026-10-19).
- Zakres: posiedzenia Sejmu i Senatu, komisje, interpelacje i zapytania. Najnowsze daty: interpelacje 2026-10-16, Sejm 2026-10-09, Senat 2026-10-13.
- Anotacja nie obejmuje wszystkiego. W 2015-2019 ma ją 49 256 z 96 799 dokumentów (brak zo/zp, część ip). W 2023-2027 nie ma jej 3 950 z 5 537 komisji Sejmu. Liczę tylko dokumenty z anotacją.

Słowa (bez interpunkcji) w dokumentach z anotacją, w mln:

| 2015* | 2016 | 2017 | 2018 | 2019 | 2020 | 2021 | 2022 | 2023 | 2024 | 2025 | 2026 (do X) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 2,7 | 28,5 | 29,4 | 26,6 | 16,8 | 39,6 | 43,8 | 31,0 | 25,6 | 22,6 | 25,8 | 23,6 |

\* tylko XI–XII 2015 (kadencji 2011-2015 nie pobierałem).

Dla porównania: ParlaMint-PL 5.0 .ana ma 36,1 mln słów w latach 2015-11 – 2022-06, a Leipzig news ma 12,5–13,7 mln słów na rocznik (2018, 2021–2024).

## 2–4. Zysk (grupy form spoza SGJP 20261018, po filtrach, w ≥ 2 dokumentach)

| Korpus | słowa | grupy n ≥ 5 | grupy n ≥ 20 | nowe n ≥ 20 | nowe, poza 374 | …i KWJP F < 20 | nowe n ≥ 5, poza 374 |
|---|---|---|---|---|---|---|---|
| ParlaMint-PL 5.0 | 36,1 mln | 781 | 193 | 16 | 15 | 9 | 35 |
| Leipzig news PL | 66,3 mln | 2 692 | 737 | 167 | 154 | 131 | 278 |
| PPC 2015–2026 | 316,0 mln | 8 073 | 3 025 | 716 | 702 | 666 | 1 334 |
| **Łącznie (suma n)** | 418 mln | 9 942 | 3 611 | **903** | **875** | **811** | **1 582** |

- Przed filtrami (klucze lemat/forma, n ≥ 5, ≥ 2 dok., spoza SGJP) jest: ParlaMint 6 923, PPC 183 078, Leipzig 44 974. Odpadają głównie znaki spoza alfabetu (PPC 139 891), wielka litera (PPC 30 088, Leipzig 30 574) i literówki (PPC 2 175, Leipzig 2 834).
- PPC z samych lat 2023–2026 (wobec 2015–2019) daje 518 nowych grup przy n ≥ 20. Tego okresu nie ma żaden inny korpus.
- Skąd się biorą nowe grupy n ≥ 20 spoza listy 374: tylko PPC 545, tylko Leipzig 87, PPC + Leipzig 167, wszystkie trzy 52, PPC + ParlaMint 12, Leipzig + ParlaMint 12.
- **Przyrost wobec NKJP→KWJP:** z 903 nowych tylko 28 jest na liście 374. 811 nie ma w KWJP nawet z F ≥ 20, więc metoda KWJP ich nie widzi.

## Kalibracja miary wzrostu
Odsetek słów **znanych z SGJP** (n ≥ 20, ≥ 2 dok.), które przechodzą kryterium „nowe”, czyli fałszywe alarmy:

| Kryterium | ParlaMint | Leipzig | PPC |
|---|---|---|---|
| g ≥ 5 | 3,4% | 5,8% | 22,1% |
| **g ≥ 5, ≥ 3 lata „po” (przyjęte)** | **2,7%** | **4,5%** | **15,6%** |
| g ≥ 10, ≥ 3 lata | 1,5% | 3,4% | 10,4% |
| g ≥ 20, ≥ 3 lata | 0,8% | 1,7% | 6,5% |

- Każdy próg powyżej 5 gubi kontrole: antyszczepionkowiec ma w PPC g = 8,8. Influencerka ma w Leipzig 13,0.
- W PPC zmienia się skład korpusu: przed 2020 przeważają komisje, po 2020 interpelacje, a w 2015–2019 połowa interpelacji nie ma anotacji. Do tego dochodzą tematyczne wybuchy (`nefrektomia`, nazwy miejscowości). Z 3 025 grup PPC fałszywych „nowych” może być ok. 470, czyli dużą część z 716.

## 5. Kontrole
Wystąpienia rocznie (formy z ręcznego paradygmatu; Leipzig tylko małą literą). Werdykt dla kryterium „nowe”: ✓ łapie, ✗ nie łapie.

| Słowo | ParlaMint 2015–19 / 2020 / 21 / 22 | PPC 2015–19 / 2020 / 21 / 22 / 23 / 24 / 25 / 26 | Leipzig 2018 / 21 / 22 / 23 / 24 | Werdykt (PM / PPC / LCC) |
|---|---|---|---|---|
| hejt (stare, kontrola ujemna) | 123 / 61 / 26 / 17 | 241 / 179 / 83 / 98 / 145 / 295 / 340 / 196 | 157 / 161 / 114 / 158 / 177 | ✗ ✗ ✗ (poprawnie, g 1,8 / 2,4 / 0,9) |
| lockdown | 0 / 108 / 170 / 28 | 0 / 631 / 576 / 146 / 61 / 38 / 22 / 10 | 0 / 936 / 211 / 37 / 31 | ✓ ✓ ✓ |
| covidowy | 0 / 146 / 150 / 42 | 0 / 746 / 1751 / 1051 / 302 / 140 / 71 / 51 | 0 / 1114 / 404 / 90 / 28 | ✓ ✓ ✓ |
| influencerka | 0 / 0 / 1 / 0 | 0 / 0 / 1 / 1 / 1 / 3 / 4 / 2 | 4 / 35 / 41 / 95 / 88 | ✗ ✗ ✓ |
| antyszczepionkowiec | 3 / 5 / 75 / 4 | 8 / 9 / 90 / 22 / 14 / 14 / 10 / 11 | 36 / 144 / 39 / 12 / 5 | ✓ ✓ ✗ (było już w 2018) |
| boomer | 0 | 0 | 1 / 1 / 5 / 8 / 5 | ✗ ✗ ✗ |
| ghosting | 0 | 0 | 2 / 0 / 0 / 0 / 1 | ✗ ✗ ✗ |
| cringe (+ krindż) | 0 | 0 … 2026: 1 | 0 / 2 / 4 / 3 / 4 | ✗ ✗ ✗ |
| wulwa | 0 | 0 | 0 | ✗ ✗ ✗ |
| *kontrola dodatnia:* pandemia | 1 / 1851 / 2243 / 616 | 21 / 19932 / 13806 / 6380 / 1819 / 1255 / 895 / 441 | 13 / 8347 / 2894 / 1143 / 798 | ✓ ✓ ✓ |
| *kontrola dodatnia:* hejter | 17 / 6 / 6 / 7 | 25 / 9 / 10 / 22 / 20 / 54 / 27 / 24 | 49 / 21 / 20 / 32 / 31 | ✗ ✗ ✗ (stare, poprawnie) |

- Każde „0” ma w tym samym korpusie kontrolę dodatnią: hejt ma 227 / 1 577 / 767 wystąpień.
- Boomer, ghosting, cringe i wulwa to język potoczny i internetowy. W stenogramach i wiadomościach prawie ich nie ma. Te trzy korpusy ich nie złapią.

## 6. Ocena ręczna
Oceniałem sam lemat z liczbami i formami, bez konkordancji. Klasy:
- **A**: polski leksem warty gry;
- **B**: prawdziwy, ale fachowy albo nie nowy;
- **E**: przymiotnik od nazwy miejsca;
- **C**: nazwa leku lub łacina;
- **D**: szum.

| Próbka (pula n ≥ 20, nowe, poza 374) | A | B | E | C | D |
|---|---|---|---|---|---|
| losowa 50 (seed 1103) | 17 (34%) | 13 | 2 | 11 | 7 |
| – w niej tylko PPC (33) | 6 (18%) | 11 | 0 | 10 | 6 |
| – w ≥ 2 korpusach (11) | 8 (73%) | 2 | 0 | 0 | 1 |
| – tylko Leipzig (6) | 3 | 0 | 2 | 1 | 0 |
| losowa 30 z ≥ 2 korpusów (seed 1104) | 21 (70%) | 6 | 0 | 1 | 2 |
| losowa 20 tylko z Leipzig (seed 1105) | 10 (50%) | 1 | 5 | 0 | 4 |

- **Szacunek A w puli 875:** PPC-only 545 × 18% ≈ 100, ≥ 2 korpusy 243 × 71% ≈ 170, Leipzig-only 87 × 50% ≈ 45. Razem **≈ 315**. Po odjęciu ok. 10% rozbitych grup zostaje ≈ 280. Przedział jest szeroki (250–400), bo próbka PPC-only liczyła tylko 33.
- Szum D to: fragmenty i skróty (`międzynar`, `zzd`), błędne lematy (`sprzyć`, `niepełnosprawa`), angielskie ciągi (`adults`, `ecommerce`, `affaires`) i nazwy (`mobywatel`, `etoll`).
- Część klasy A to stare luki SGJP, a nie słowa nowe (jednocyfrowy, bezobsługowy, inwerter, cyberprzestępczość). Do słownika nadają się tak samo.

**Najlepsze przykłady** (wystąpienia; w nawiasie: przed 2020 → po; PM = ParlaMint, LCC = Leipzig):

| Grupa | PPC | LCC | PM | KWJP F |
|---|---|---|---|---|
| antyinflacyjny | 1 589 (0→1 589) | 328 (0→328) | 191 (0→191) | 8 |
| ekoschemat | 1 787 (0→1 787) | 106 (0→106) | – | 0 |
| respiratorowy | 1 228 (0→1 228) | 111 (0→111) | 18 | 11 |
| kryptoaktywa | 1 764 (15→1 749) | 10 | – | 0 |
| patostreaming | 558 (8→550) | – | – | 0 |
| pełnoskalowy | 526 (9→517) | 274 (0→274) | – | 0 |
| neosędzia | 498 (0→498) | 75 (0→75) | 28 | 13 |
| wyszczepić | 504 (4→500) | 7 | 13 | 0 |
| wagnerowiec | – | 490 (1→489) | – | 0 |
| pocovidowy | 366 (0→366) | 137 (0→137) | 6 | 0 |
| antydronowy | 362 (1→361) | 5 | – | 0 |
| paralimpijski | 311 (3→308) | 22 | – | 0 |
| armatohaubica | 199 (9→190) | 246 (6→240) | – | 13 |
| antycovidowy | 221 (0→221) | 59 (0→59) | 20 | 8 |
| pulsoksymetr | 210 (3→207) | 70 | – | 58 |
| babciowe / babciowy | 193 (0→193) | 153 (0→153) | – | 0 |
| deepfake | 190 (0→190) | 43 (0→43) | – | 0 |
| pumptrack | 183 (0→183) | 111 | – | 8 |
| jednodawkowy | 179 (0→179) | 179 (1→178) | – | 0 |
| zeroemisyjność | 179 (1→178) | 10 | – | 0 |
| neuroróżnorodny | 157 (0→157, od 2024) | 7 | – | 0 |
| popandemiczny | 127 (0→127) | 45 (0→45) | 13 | 0 |
| eurokołchoz | 121 (1→120) | 21 | 13 | 0 |
| gigafabryka | 115 (0→115) | 5 | – | 0 |
| chatbot | 81 (1→80) | 127 (4→123) | – | 6 |
| multiwersum | – | 101 (0→101) | – | 0 |
| soundbar | – | 85 (2→83) | – | 0 |
| showrunner | – | 80 (2→78) | – | 0 |
| stablecoin | 56 (0→56) | – | – | 0 |
| wymazówka | 35 (0→35) | – | – | 12 |

## 7. Koszt odświeżenia
| Źródło | Pobranie | Liczenie (`taskpolicy -b`, Mac pod obciążeniem) | Jak często |
|---|---|---|---|
| PPC, tylko kadencja 2023-2027 | 2,7 GB (rośnie) | ok. 20 min, 6 procesów | co kwartał; plik ma nową anotację (2026-10-19) |
| PPC, wszystkie trzy kadencje | 11,4 GB | ok. 40 min | raz, jako baza 2015–2019 |
| ParlaMint-PL .ana | 2,3 GB | ok. 40 min, 1 proces | rzadko: 5.0 z 2025-07 sięga 2022-06 |
| Leipzig, nowy rocznik | ok. 200 MB | ok. 5 min na rocznik | raz w roku; `pol_news_2025` jeszcze nie ma |
- Miejsce: dane 16 GB (PPC 11 GB, ParlaMint 2,2 GB, Leipzig 3,0 GB), zliczenia 0,35 GB. Na dysku jest dziś 35 GB wolnego.
- Główny koszt to przegląd ręczny, nie obliczenia. 875 kandydatów przy precyzji ok. 35% to kilka godzin pracy. Najtańsza kolejność: najpierw 243 grupy z ≥ 2 korpusów (ok. 70% trafień), potem Leipzig-only, a PPC-only na końcu albo z dodatkowym filtrem.

## Pewność i luki
- **Pewność średnia** dla liczb zysku i **niska–średnia** dla szacunku słów wartych gry (jeden oceniający, bez konkordancji, 100 ocen).
- Grupowanie przez ucinanie końcówek jest zgrubne. Liczby grup to przybliżenie liczby leksemów (ok. ±10%).
- Wzrost w PPC zależy od składu korpusu (fałszywe alarmy 15,6%). Liczby „nowe” w PPC są zawyżone.
- Brak anotacji w części PPC 2015–2019 i części komisji 2023–2027.
- Leipzig: część zdań ma zepsute kodowanie (`£atwiej`). Filtr form uciętych usuwa większość skutków, ale nie wszystkie (`stwa`).
- Dokumenty dla ParlaMint i PPC zliczam jako sumę po upos, więc to górna granica. Na próg ≥ 2 dok. ma to mały wpływ.
- Nie sprawdzałem kandydatów w SGJP ręcznie, opieram się na eksporcie 20261018 (lematy i formy).

## Pliki (scratchpad, poza repo)
`/private/tmp/claude-501/-Users-robmar-Projects-Literaki/3ae5c44e-c8df-4ef9-924a-bcb0e5eaf7f8/scratchpad/nowe-slowa/zysk/`:
- skrypty: `scripts/pm_count.py`, `scripts/ppc_count.py`, `scripts/lcc_count.py`, `scripts/analiza.py`, `scripts/zysk2.py` (grupy, tabele, próbki), `scripts/kalibracja.py`, `scripts/kontrole2.py`, `scripts/kontrole_g.py`, `scripts/k374.py`, `scripts/wspolne.py`, `scripts/paradygmaty.py`;
- wyniki: `zysk2.json` (tabele, cała pula n ≥ 20 w `pula20`, próbki), `kalibracja.json`, `kontrole2.json`, `kontrole-zysk.json`, `kontrole-g.json`, `k374.json`;
- zliczenia: `pm.pkl`, `ppc-*.pkl`, `lcc.pkl`, `analiza.pkl`;
- dane: `../dl-ppc/`, `../dl-parlamint-ana/` (`ParlaMint-PL.ana.tgz`, sha256 `246407ad…d398`), `../dl-lcc/` (sha256 roczników w logu pobierania).
- `zysk.json` i `zysk-summary.json` to pierwsza wersja bez grupowania form. Nie cytuję ich.
