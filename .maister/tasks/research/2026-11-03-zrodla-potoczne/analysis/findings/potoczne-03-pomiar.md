# potoczne-03: pomiar kontroli w źródłach potocznych

## TL;DR
- **Napisy OpenSubtitles z filmów 2022–2023** (62,6 mln słów) mają **wszystkie 7 kontroli**, w potocznym znaczeniu: wulwa 7, ghosting 11, cringe 10, boomer 90, hejt 64, lockdown 169, antyszczepionkowiec 12. To jedyne zmierzone źródło, w którym wszystkie cztery kontrole celu występują w dobrym znaczeniu.
- **BAN-PL (Wykop)**: najwyższe ipm słów internetowych (cringe 5,6; boomer 5,6), ale 0 dla wulwy i ghostingu. Kontrole dodatnie są wysokie (hejt 43,5 ipm), więc te zera coś znaczą. Korpus jest jednak mały (0,7 mln słów).
- **Fora (kafeteria.pl)**: 416 mln słów, ale treść jest głównie starsza. Boomer to tu prawie wyłącznie guma do żucia, ghosting to zjawisko w obrazie kina IMAX. Wulwa: 3 trafienia świadomego użycia.
- **Strony dyskusji plwiki**: wulwa 7 (wątek z 2023 r. w „Dyskusja:Wargi sromowe”), cringe 2, ghosting 0. Kontrole dodatnie wysokie (hejt 121).
- Wynik z prefiksu pliku mono OpenSubtitles (235 mln słów, prawdopodobnie stare filmy): hejt 0, lockdown 0. To pokazuje, że **podział w czasie jest konieczny**. Liczba z całego zbioru bez dat rozmywa nowe słowa.

## Kluczowe decyzje
- Formy: dokładne paradygmaty z `kontrole.json`, token po tokenie. Mała litera, Wielka i WERSALIKI liczone osobno. Jednostka (zdanie, wpis, strona) jest pomijana jako angielska, gdy ma ≥2 angielskie słowa stop i więcej angielskich niż polskich. W plwiki próg jest inny: ≥5 słów stop i >10% segmentu.
- OpenSubtitles: plik mono nie ma dat, a jego początek to starsze filmy. Pobrałem więc zakresem `Range` tylko człony `pl/2022/` i `pl/2023/` z `xml/pl.zip`. Ich położenie odczytałem z katalogu centralnego ZIP.
- Strony dyskusji plwiki: rok komentarza biorę z najbliższego następnego podpisu „HH:MM, D mmm RRRR (CET)”. Artykuły (ns 0) liczę osobno, jako tło.

## Otwarte pytania i ryzyka
- **Duplikaty w OpenSubtitles**: OPUS trzyma kilka wersji napisów do jednego filmu. Przykład: „Motorem tej rewolucji jest wulwa.” występuje dwa razy. Liczby zdań zawyżają liczbę niezależnych użyć. Przed użyciem w karcie trzeba policzyć **filmy** (IMDb ID z nazwy pliku), nie zdania.
- Napisy to tłumaczenia (głównie z angielskiego). „Ghosting” i „cringe” mogą być kalką tłumacza, a nie polszczyzną użytkowników. Jako dowód „słowo w obiegu” są słabsze niż Wykop.
- Pomiary są częściowe, bo maszyna była mocno obciążona (load avg 35–73):
  - kafeteria: 1,18 z 8,79 GB (13%); serwer zerwał połączenie;
  - plwiki: 1,91 z 3,54 GB bz2 (54%); dumps.wikimedia.org ucinał połączenia w 5 z 7 części;
  - OpenSubtitles 2022–2023: pełne, 15 503 człony.
- Plwiki, artykuły: „wulwa” ma 158 trafień, głównie w artykułach zoologicznych (narząd dwuparców i pająków). Nie świadczy to o świadomej zmianie. Wyjątek: „Srom” („rzadziej wulwa”).
- Rok z podpisu w plwiki bywa mylący (archiwa, komentarze bez podpisu). To przybliżenie.

## Wyniki (mała/Wielka/WERSALIKI; ipm = trafienia PL na mln słów; „en” = pominięte jako tekst angielski)

| Źródło | Słowa | wulwa | ghosting | cringe | boomer | hejt (+) | lockdown (+) | antyszczep. (+) |
|---|---|---|---|---|---|---|---|---|
| OpenSubtitles xml 2022–2023 | 62,6 mln | 7/0/0 · 0,11 | 10/1/0 · 0,18 | 7/2/1 · 0,16 | 65/24/1 · 1,44 | 57/6/1 · 1,02 | 130/27/12 · 2,70 | 12/0/0 · 0,19 |
| OpenSubtitles mono, prefiks 477 MB gz (19,5%) | 235,3 mln | 0 | 0 | 0 | 5/782/3 (postać „kapitan Boomer”) | **0** | **0** | **0** |
| BAN-PL_1 (Wykop 2019–2023) | 0,71 mln | 0 | 0 | 4/0/0 · 5,6 | 3/1/0 · 5,6 | 31/0/0 · 43,5 | 22/0/0 · 30,9 | 12/2/0 · 19,7 |
| SpeakLeash kafeteria (13%) | 415,7 mln | 3/0/0 · 0,007 | 3/0/0 (znaczenie techniczne) | 0 (en 3) | 8/4/1 (guma) · en 2 | 63/6/2 · 0,17 | 5/1/0 · en 5 | 4/0/0 · 0,01 |
| plwiki, dyskusje (54%) | 182,2 mln | 5/2/0 · 0,04 | 0 | 2/0/0 · 0,01 | 22/4/0 (głównie okręty) | 115/5/1 · 0,66 | 26/6/0 · en 2 | 29/30/0 · 0,32 |
| plwiki, artykuły (tło, 54%) | 566,2 mln | 124/34/0 (zoologia) | 3/3/0 | 9/11/1 (tytuły ang.) | 27/193/0 (nazwiska) | 147/56/6 | 200/247/2 | 39/9/0 |
| PolEval 2019 (tweety) | 0,15 mln | 0 | 0 | 2/0/0 · 13,4 | 0 | 5/1/0 · 40,2 | 0 (sprzed 2020) | 0 |
| hate_speech_pl | 0,48 mln | 0 | 0 | 0 | 1 („boomery” = okręty) | **0** | **0** | **0** |
| PolEmo 2.0 | 0,90 mln | 0 | 0 | 0 | 0 | 1/0/0 | **0** | **0** |
| Common Voice PL (sentence-collector) | 0,16 mln | 0 | 0 | 0 | 0 | **0** | **0** | **0** |

Zera bez wniosku: wiersze, w których kontrole dodatnie (+) też są zerowe (pogrubione), nie mówią nic o kontrolach celu. Są to: hate_speech_pl, PolEmo, Common Voice i prefiks mono OpenSubtitles. Powód to wiek tekstu albo rozmiar.

## Podział w czasie
- **OpenSubtitles (rok filmu)**: z 357 327 plików 41 515 (11,6%) pochodzi z lat 2019+. W tym 2022: 9 020, 2023: 6 482. Lata 2022 i 2023 dają tę samą rangę kontroli, np. lockdown 106/63, boomer 50/40, cringe 4/6.
- **plwiki, dyskusje (rok podpisu)**:
  - wulwa: 2023: 5 (pozostałe bez roku);
  - cringe: 2021: 1, 2023: 1;
  - hejt: od 2010, z rosnącym trendem (2023: 26, 2024: 40);
  - lockdown: 2020–2025;
  - antyszczepionkowiec: szczyt w 2021 r. (32).
- BAN-PL: tylko okres zbioru (2019–06.2023, klasa neutralna 2021–2023). Fora SpeakLeash: brak dat.

## Konteksty (lokalnie; nie do repo poza tymi krótkimi cytatami)
- wulwa, napisy 2022–2023: „To nie piczka, tylko wulwa!”, „Raz nawet kucnęłam nad lustrem i podziwiałam moją wulwę.”
- wulwa, kafeteria: „Wagina to pochwa. wulwa! To jest poprawna nazwa.”
- wulwa, plwiki (Dyskusja:Wargi sromowe, 2023): „…reprezentacji różnorodnego wyglądu wulwy w encyklopediach i podręcznikach…”
- ghosting, napisy: „Przestać robić mi ghosting.”, „Ekspertka od ghostingu.”
- cringe, BAN-PL: „cringe jak skurwysyn”; napisy: „Co za cringe.”; plwiki: „no sorry totalny cringe”.
- boomer, BAN-PL: „Wiem, że zaraz mnie boomerzy zminusują”; napisy: „Ok, boomer.”

## Dane, sumy i sprzątanie
- Skrypty: `scratchpad/potoczne/potoczne/scripts/`:
  - `licz.py` i `licz_szybki.py` (formy z `kontrole.json`, odsiew angielskiego);
  - `plwiki.py`, `scal-plwiki.py`;
  - `zipcd.py`, `zipspan.py`, `zipstream.py` (ZIP przez Range).
  
  Skopiowane `scan.py`, `scanjsonl.py`, `ctx.py` zostały niezmienione.
- Wyniki JSON: `scratchpad/potoczne/potoczne/dane/wyniki/`.
- Transfer łącznie ok. 4,9 GB, wszystko strumieniowo, bez zapisu na dysk:
  - OpenSubtitles mono 1,22 GB (dwa przerwane podejścia);
  - xml 2022–2023: 589 559 027 B;
  - kafeteria: 1 175 141 669 B;
  - plwiki: 1 910 898 412 B;
  - małe zbiory < 20 MB.
- SHA-1 BAN-PL: `80c4a3db…` (BAN-PL_1.zip), `2a5607fc…` (BAN-PL_2.zip). SHA-1 części plwiki: w `dumpstatus.json` zrzutu 20261101. Części były ucięte, więc sumy nie dotyczą przeczytanego prefiksu.
- Na dysku zostało ok. 32 MB małych pobrań: `dane/banpl` (CSV, 14 MB), `dane/male` (parquet, PolEval, Common Voice), `dane/wyniki/opensubs-trafienia.txt` (linie z trafieniami). Hook zablokował mi kasowanie (`rm`), więc trzeba je skasować ręcznie. Dużych plików nie ma, bo wszystko szło strumieniowo.
