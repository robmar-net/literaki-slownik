# projekt: 9 kontroli w lokalnych źródłach

## TL;DR
- SGJP 20260823 ma 4 kontrole dodatnie (hejt, lockdown, covidowy, influencerka) i nie ma 5 pozostałych. Potwierdza to tabelę z planu.
- KWJP (2011–2020) widzi tylko słowa z tej dekady: antyszczepionkowiec 34, boomer 5, a ghosting, cringe i wulwa mają <5. Słowa po 2020 roku są poza zasięgiem lokalnych danych.
- NKJP (teksty do 2010) ma przy kontrolach dodatnich 0–2 wystąpienia. Daje więc oś czasu: „przed 2011” wobec „2011–2020”.
- Słowosieć 4.5 ma po polsku hejt, influencerkę i **antyszczepionkowca**, czyli lukę SGJP. Lockdown, boomer i cringe ma tylko jako jednostki angielskie.

## Kluczowe decyzje
- Unigramy NKJP mają doklejoną interpunkcję (`wulwa,`, `boomer.`). Liczę po obcięciu znaków `.,;:!?()[]{}"'„”“«»…-–—/*`. Bez tego „wulwa” daje 0 zamiast 2, a „srom” 59 zamiast 110.
- Formy słów spoza SGJP biorę z ręcznego paradygmatu, opisanego w skrypcie. Formy słów z SGJP biorę z eksportu.

## Otwarte pytania
- 10 wystąpień „boomer” w NKJP (do 2010) to najpewniej angielskie *baby boomer* albo nazwy. Lokalne 1grams nie mają kontekstu, więc tego nie sprawdzę.
- Daty wejścia kontroli do SGJP są lokalnie nieznane, bo mamy jeden eksport. Kalibracji „przed wejściem do SGJP” nie da się zrobić na tych danych (zob. `projekt-metoda.md`).

## Pomiar
Odczyt 2026-11-03. Skrypty: `/private/tmp/claude-501/-Users-robmar-Projects-Literaki/3ae5c44e-c8df-4ef9-924a-bcb0e5eaf7f8/scratchpad/nowe-slowa/kontrole.py`, wynik w `…/nowe-slowa/kontrole.json` (pełna ścieżka jak wyżej).
Okresy: KWJP 2011–2020 (`cache/kwjp/overview.html`: „comprises texts written between 2011 and 2020”), NKJP do 2010 (tamże: „only contains texts up to 2010”). Rozmiary: KWJP100 81 664 894 tokenów (`sources.json: denominator`), NKJP 1grams 246 153 378.

| Słowo | SGJP | KWJP lemat all (F / 1-DP) | fakt / fikcja / publ. | KWJP orth_lc all (suma form) | KWJP 2-gramy (wiersze) | NKJP 1grams (formy) | Słowosieć 4.5 (PL) |
|---|---|---|---|---|---|---|---|
| hejt | jest (subst, interj) | 366 / 0,083 | 92 / 8 / 266 | 361 | 20 | 2 | jest (4 LU) |
| lockdown | jest | 241 / 0,029 | 37 / 8 / 196 | 244 | 20 | 0 | brak (tylko EN, pos 6) |
| covidowy | jest (adj) | 116 / 0,012 | 6 / 4 / 106 | 120 | 10 | 0 | brak |
| influencerka | jest | 24 / 0,008 | 3 / 3 / 18 | 16 | 0 | 0 | jest |
| antyszczepionkowiec | **brak** | 34 / 0,015 | 7 / 2 / 25 | 36 (‑cy 12, ‑ców 19, ‑com 5) | 0 | 0 (`antyszczepionkowe` 1) | **jest** (+ `antyszczepionkowy`) |
| boomer | brak (jest `bumer` m3) | 5 / 0,002 | 3 / – / 2 | 0 (każda forma <5) | 0 | 10 (boomer 8) | brak (tylko EN, pos 6) |
| ghosting | brak | <5 | – | 0 | 0 | 1 | brak |
| cringe | brak | <5 | – | 0 | 0 | 0 | brak (tylko EN, pos 5) |
| wulwa | brak (tylko nazwisko `Wulw`) | <5 | – | 0 | 0 | 6 (wulw 4, wulwa 2; nazwisko wg badania wulwy) | brak (jest `wulwodynia`) |

**Kontrole dodatnie przy każdym „brak”:**
| Słowo | SGJP | KWJP lemat | NKJP | Słowosieć |
|---|---|---|---|---|
| srom | jest | 92 | 110 | jest |
| pandemia | jest | 2 985 | 193 | jest |
| hejter | jest | 127 | 1 | jest |
| bumer | jest | <5 | 17 | jest |

- Każde źródło ma dodatnie trafienia, więc zera są zmierzone, a nie skutkiem złego odczytu.
- Prefiksy w SGJP: `antyszczepion*`, `boomer*`, `ghosting*`, `cring*` i `krindż*` mają 0 lematów. `wulw*` daje tylko `Wulw`. `covid*` daje 5 lematów (COVID-19, covid, covidowo, covidowość, covidowy).
- Na liście lematów KWJP `koronawirus` ma 4 730, `koronawirusowy` 60, `antyszczepionkowy` 37, a `influencer` 42.

## Co z tego wynika dla metody
1. KWJP plus NKJP to jedyna lokalna para z osią czasu: do 2010 i 2011–2020. Wszystkie 4 kontrole „w SGJP” i antyszczepionkowiec mają w NKJP 0–2, a w KWJP F ≥ 24. To wyraźny sygnał wzrostu.
2. Boomer, ghosting, cringe i wulwa są poniżej progu KWJP. Żaden lokalny korpus ich nie złapie. Do tego potrzebny jest korpus z tekstami po 2020 roku (kategoria `korpusy`).
3. Słowosieć daje niezależne potwierdzenie dla luki SGJP (antyszczepionkowiec). Nie ma jednak lockdownu ani covidowego, więc może tylko wspierać wynik, a nie być warunkiem.
