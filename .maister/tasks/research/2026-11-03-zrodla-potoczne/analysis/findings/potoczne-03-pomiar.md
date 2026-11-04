# potoczne-03: pomiar kontroli w źródłach potocznych

## TL;DR
- **Napisy OpenSubtitles z filmów 2022–2023** (62,6 mln słów) mają **wszystkie 7 kontroli**, w potocznym znaczeniu: wulwa 7, ghosting 11, cringe 10, boomer 90, hejt 64, lockdown 169, antyszczepionkowiec 12. To jedyne zmierzone źródło, w którym wszystkie cztery kontrole celu występują w dobrym znaczeniu.
- BAN-PL wycofany decyzją użytkownika 2026-11-04 (autorzy chronią archiwa hasłem przed automatycznym zbieraniem); liczby usunięte.
- **Fora (kafeteria.pl)**: 416 mln słów, ale treść jest głównie starsza. Boomer to tu prawie wyłącznie guma do żucia, ghosting to zjawisko w obrazie kina IMAX. Wulwa: 3 trafienia świadomego użycia.
- **Strony dyskusji plwiki**: wulwa 7 (wątek z 2023 r. w „Dyskusja:Wargi sromowe”), cringe 2, ghosting 0. Kontrole dodatnie wysokie (hejt 121).
- Wynik z prefiksu pliku mono OpenSubtitles (235 mln słów, prawdopodobnie stare filmy): hejt 0, lockdown 0. To pokazuje, że **podział w czasie jest konieczny**. Liczba z całego zbioru bez dat rozmywa nowe słowa.

## Kluczowe decyzje
- Formy: dokładne paradygmaty z `kontrole.json`, token po tokenie. Mała litera, Wielka i WERSALIKI liczone osobno. Jednostka (zdanie, wpis, strona) jest pomijana jako angielska, gdy ma ≥2 angielskie słowa stop i więcej angielskich niż polskich. W plwiki próg jest inny: ≥5 słów stop i >10% segmentu.
- OpenSubtitles: plik mono nie ma dat, a jego początek to starsze filmy. Pobrałem więc zakresem `Range` tylko człony `pl/2022/` i `pl/2023/` z `xml/pl.zip`. Ich położenie odczytałem z katalogu centralnego ZIP.
- Strony dyskusji plwiki: rok komentarza biorę z najbliższego następnego podpisu „HH:MM, D mmm RRRR (CET)”. Artykuły (ns 0) liczę osobno, jako tło.

## Otwarte pytania i ryzyka
- **Duplikaty w OpenSubtitles**: OPUS trzyma kilka wersji napisów do jednego filmu. Przykład: jedno zdanie z wulwą (film 2022–2023) występuje dwa razy. Liczby zdań zawyżają liczbę niezależnych użyć. Przed użyciem w karcie trzeba policzyć **filmy** (IMDb ID z nazwy pliku), nie zdania.
- Napisy to tłumaczenia (głównie z angielskiego). „Ghosting” i „cringe” mogą być kalką tłumacza, a nie polszczyzną użytkowników. Jako dowód „słowo w obiegu” są słabsze niż tekst pisany przez polskich użytkowników.
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
| OpenSubtitles mono, prefiks 477 MB gz (19,5%) | 235,3 mln | 0 | 0 | 0 | 5/782/3 (imię postaci) | **0** | **0** | **0** |
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
- Fora SpeakLeash: brak dat.

## Konteksty (opis własny; dosłowne cytaty tylko z plwiki, CC BY-SA 4.0)
- wulwa, napisy (filmy 2022–2023): bohaterka poprawia wulgarną nazwę narządu na „wulwa”; w innym zdaniu bohaterka opisuje oglądanie własnej wulwy. Znaczenie anatomiczne, świadome.
- wulwa, kafeteria.pl (rok wpisu nieznany): wpis poprawia „wagina” na „wulwa” jako nazwę właściwą.
- wulwa, plwiki (Dyskusja:Wargi sromowe, 2023, CC BY-SA 4.0, autorzy wg historii strony): „…reprezentacji różnorodnego wyglądu wulwy w encyklopediach i podręcznikach…”
- ghosting, napisy (2022–2023): postać prosi drugą, by przestała ją ignorować („ghosting” jako rzeczownik w bierniku); w innym zdaniu „ekspertka od ghostingu” jako określenie osoby.
- cringe, napisy (2022–2023): wykrzyknienie oceniające sytuację jako żenującą. plwiki (CC BY-SA 4.0): „no sorry totalny cringe”.
- boomer, napisy (2022–2023): znana riposta wobec starszej osoby, w znaczeniu pokoleniowym.

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
- SHA-1 części plwiki: w `dumpstatus.json` zrzutu 20261101. Części były ucięte, więc sumy nie dotyczą przeczytanego prefiksu.
- Na dysku zostały małe pobrania: `dane/male` (parquet, PolEval, Common Voice), `dane/wyniki/opensubs-trafienia.txt` (linie z trafieniami). Hook zablokował mi kasowanie (`rm`), więc trzeba je skasować ręcznie. Dużych plików nie ma, bo wszystko szło strumieniowo.
