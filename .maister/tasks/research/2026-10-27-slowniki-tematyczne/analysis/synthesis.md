# Synteza: słowniki tematyczne (runda 1 + runda 2)

## TL;DR
Tak, da się zbudować listy tematyczne, ale tylko z kilku źródeł naraz i z ręcznym przeglądem.
Rdzeń: etykiety SGJP (trafne, wąskie: 254 / 96 / 62 leksemy). Największy przyrost: drzewa hiponimii Słowosieci 4.5 od ręcznie wybranych korzeni.
Pokrycie słów oczywistych: SGJP 27% / 0% / 23%; Słowosieć (zbiór C) 59% / 40% / 86%; razem 78% / 40% / 86% (morze / rolnictwo / matematyka).
IATE to dobre otwarte uzupełnienie. N-gramy KWJP, rodziny SGJP, KWJP½M i NKJP 1M dają mało. AGROVOC zablokowany, Wikisłownik odroczony.
Rolnictwo wciąż słabe (czynności, budynki). Tam pomóc może tylko więcej korzeni albo LLM — bez wyceny i bez decyzji.

## Key Decisions
- Odpowiedź na pytanie: matematykę i morze zbudujemy (SGJP + Słowosieć, opcjonalnie IATE). Rolnictwo tylko częściowo.
- Proponowana kombinacja to opcja, nie decyzja. Wybiera użytkownik.
- Słowosieć, IATE i etykiety SGJP to metody spoza trzech metod Zadania E (prompt v3, w. 408–426). Każda wymaga ADR.
- Metoda E2 (korpus dziedzinowy) nie ma korpusu spełniającego warunki. Według promptu v3 oznaczamy ją jako zablokowaną.
- Metoda E1 (n-gramy KWJP) po pilotażu jest słaba. Nie polecamy jej jako głównej.

## Open Questions / Risks
- Jeden oceniający: wszystkie próby trafności, lista 107 słów testowych i wybór korzeni pochodzą od jednej osoby (agenta). Wartości mają pewność niską do średniej.
- Licencja Słowosieci: link w repozytorium zwraca 404; nota na stronie mówi „plWordNet 4.2 © 2020”, a dane to 4.5; w zipie brak pliku LICENSE.
- Wynik Słowosieci zależy od korzeni i wydania (matematyka A: 558 lematów w 4.2, 431 w 4.5; `równanie` wypadło).
- LLM: koszt niewyceniony, warunki wyniku u dostawcy niesprawdzone. Wymaga dwóch potwierdzeń (wydatek).
- Wieloznaczność: lemat wchodzi do tematu przez jedno znaczenie (`kot`, `kiosk`, `orka`, `pole`) w każdym źródle.

## 1. Pytanie
Po rundzie 1: czy dane projektu albo zasoby PAN mają dziedzinę słowa? (Odpowiedź: tylko etykiety SGJP, wąskie.)
Po rundzie 2 (poszerzenie, wybór użytkownika): czy da się zbudować listy tematyczne (morze, rolnictwo, matematyka) i z czego?

## 2. Analiza krzyżowa

### Potwierdzone w kilku źródłach
| Ustalenie | Źródła | Pewność |
|---|---|---|
| SGJP ma etykiety dziedzin; 4472 z 387 398 leksemów (1,2%) | pomiar eksportu; `qualifiers.json`; `label-coverage.json`; `build.sqlite` v31 | wysoka |
| Etykieta = termin fachowy, nie temat | pomiar pokrycia SGJP; WSJP *Zasady* s. 37, 47; brak rdzenia SGJP w tekstach tematu KWJP½M i NKJP 1M | wysoka |
| Korpusy PAN nie dadzą podkorpusu tematycznego | runda 1 (dokumentacja); runda 2: KWJP½M ma `meta_topic` tylko dla 777 książek (temat: 1466 / 881 / 400 słów); NKJP 1M bez UKD/BN (3889 nagłówków, sprawdzone dwa razy) | wysoka |
| Słowosieć i SGJP opisują różne warstwy | tylko 75 z 254 leksemów morskich SGJP w C; Słowosieć ma `kotwica`, `maszt`, SGJP ma `achtersztag`, `halsować` | wysoka |
| Słowa podstawowe tematu są w tekstach tematu, nie w etykietach | KWJP½M (`pszczół`, `pasieka`, `jachtów`, `regat`); test pokrycia SGJP 0% dla rolnictwa | średnia |
| Metody „z tekstu” (E1, rodziny) poszerzają w dół, nie w bok | E1: top 50 to kolokacje; rodziny: odzysk 0–1 słowa na temat | średnia |

### Sprzeczności wyjaśnione
- **„Tylko LLM sięga po słowa podstawowe”.** Plik `wide-metody-llm.md` mówi to o trzech metodach Zadania E. Słowosieć też je daje (`kotwica`, `maszt`, `żagiel`, `pokład` są w C). Poprawne ujęcie: LLM to jedyna metoda, która może sięgnąć po słowa leżące poza wybranymi drzewami (np. `orka`, `siew`, `obora`). Nie zmierzono tego.
- **Pokrycie Słowosieci 59 / 40 / 86%** dotyczy zbioru C (z częściami i skojarzeniami). Sam zbiór A (hiponimia) daje 24 / 37 / 71%. Dodatki C − A są w połowie szumem (trafne 16 / 8 / 10 na 30). Przyrost pokrycia kosztuje trafność.
- **Licencja NKJP 1M.** Strona nkjp.pl: CC BY 4.0; README w archiwum: CC BY 3.0 PL. Obie to CC BY; różni się wersja. Dla obecnego wyniku bez znaczenia, bo korpus nie wchodzi do list.
- **Licencja Słowosieci.** Stopka slowosiec.pl: CC BY-SA 4.0; repozytorium: licencja „plWordNet”. Interpretacja: stopka dotyczy serwisu, nie bazy. Pewność średnia.

### Pewność
- Wysoka: liczniki SGJP i Słowosieci (dla danych korzeni), brak tematu w korpusach PAN, treść licencji IATE, EuroVoc, Słowosieci.
- Średnia: trafność wszystkich prób (n=30, jeden oceniający); pokrycie (107 słów jednego autora); liczby IATE (dolne granice, próby 86–300 haseł).
- Niska: rozmiar pełnego tematu; skuteczność LLM (bez wywołań); użyteczność AGROVOC (licencja).

## 3. Wzorce

| Wzorzec | Opis | Dowód | Ocena |
|---|---|---|---|
| Etykieta = termin fachowy | SGJP, IATE, EuroVoc oznaczają terminy wąskie lub urzędowe | SGJP pokrycie 27/0/23%; IATE 7–21% słów pojedynczych | stały w źródłach słownikowych i terminologicznych |
| Drzewo pojęć łapie słowa podstawowe | hiponimia od korzenia daje typy, części, nazwy ogólne | Słowosieć A/C | działa dla rzeczowników; gubi czynności i budynki |
| Temat leży w wielu gałęziach | `ciągnik` < `pojazd mechaniczny`; `siano` < `karma`; `sztorm` < `wiatr`; `parabola` < `owal` | `wide-plwordnet-pomiar.md` W2 | każdy temat wymaga ręcznego doboru korzeni |
| Sąsiad w tekście ≠ słowo tematu | bigramy dają kolokacje (`pole karne`, `liczba zgonów`) | E1 top 50: 5–10/50 ściśle, matematyka 1–2/50 | stały; wieloznaczne zalążki dominują |
| Metadane opisują tekst, nie słowo | `meta_topic`, `catRef`, UKD/BN | KWJP½M, NKJP 1M | stały we wszystkich korpusach PAN |
| Licencja rośnie odwrotnie do jakości | WSJP (najlepszy) bez licencji; AGROVOC-PL niejasny; Wikisłownik CC BY-SA; Wikidata CC0 pusta | runda 1 i 2 | stały — źródła czyste są małe lub terminologiczne |
| Wieloznaczność per lemat | każde źródło przypisuje temat lematowi przez jedno znaczenie | `kot`, `kiosk`, `orka`, `pole`, `liczba` | wymaga przeglądu i zapisu niepewności (prompt v3) |

## 4. Kluczowe wnioski

1. **Słowosieć to największy przyrost.** Nowe słowa do gry spoza etykiet SGJP (C): morze 493, rolnictwo 864, matematyka 545. 85–88% z nich jest w BROAD v31. Licencja pozwala na listy pochodne z notą. Pewność: wysoka (liczby), średnia (trafność).
2. **SGJP + Słowosieć wystarczy dla matematyki i prawie dla morza.** Pokrycie 86% i 78%. Rolnictwo stoi na 40%: brak `orka`, `siew`, `żniwa`, `obora`, `ciągnik`, `ul`. Pewność: średnia.
3. **Zbiór A jest dość trafny, dodatki C nie.** A: 23 / 14 / 23 trafnych na 30. C − A: 16 / 8 / 10. Części (rel. 25, 27) są lepsze od skojarzeń (rel. 108, 146). Pewność: średnia.
4. **IATE uzupełnia terminy, nie temat.** Czysta licencja pliku pobrania. Słowa pojedyncze to 8% (morze), 21% (rolnictwo), 7% (matematyka). Matematyka uboga (≥87 haseł). Rolnictwo szumne (gatunki ryb, środki chemiczne). Pewność: średnia.
5. **Metody z danych PAN są słabe.** E1 (bigramy KWJP): odzysk 9 / 3 / 3 słów testowych, top 50 głównie szum. Rodziny SGJP: 0–1 słowo, eksport nie ma odsyłaczy. KWJP½M i NKJP 1M: teksty tematu mają 400–1466 słów. Pewność: średnia do wysokiej.
6. **Rolnictwo wymaga osobnego kroku.** Czynności i budynki leżą w drzewie poza tematem. Opcje: więcej korzeni (`obrabiać ziemię`, budynki inwentarskie), IATE, LLM. Żadnej nie zmierzono dla tych braków. Pewność: średnia.
7. **LLM jest jedyną metodą „pełnego przeglądu” bazy.** 212 728 leksemów STANDARD; ~1,7 mln tokenów wejścia i ~1,3 mln wyjścia na temat (szacunek, bez ceny). Pewność: niska (bez pomiaru).

## 5. Relacje i przepływ danych
```
SGJP (BSD-2, lokalnie) ── etykiety dziedzin ──┐
Słowosieć 4.5 (licencja plWordNet) ── drzewa od korzeni (A + części) ──┤
IATE plik pobrania (atrybucja UE) ── słowa pojedyncze z dziedziny ──────┼─► kandydaci (lematy)
[opcja] LLM ── ocena 0–3 leksemów z bazy ───────────────────────────────┘
      ─► mapowanie na leksemy SGJP ─► ∩ STANDARD (podzbiór bazy) ─► przegląd ręczny próby
      ─► pakiet tematyczny jak POP00 (method.json, LIMITATIONS.md, ATTRIBUTIONS.md)
KWJP100 / NKJP ─► tylko ranking frekwencji (bez tematu)
WSJP ─► tylko ręczny wgląd w próbkę
```
Punkt wpięcia w kodzie: obok `pop`/`pop00` (`cli.py:44-55`); `quality.py:278` już dzieli etykiety na atomy; `pop.load_lexemes` trzeba poprawić o podział po `|`.

## 6. Luki
- Brak drugiego oceniającego i niezależnej listy słów testowych.
- Pokrycia IATE, EuroVoc i AGROVOC na liście 107 słów nie mierzono.
- Trafności słów pojedynczych IATE nie oceniono na próbie; są tylko przykłady.
- LLM nie wywołano; brak ceny, brak próby jakości.
- Rolnictwo: nie sprawdzono dodatkowych korzeni Słowosieci dla czynności i budynków.
- Nie sprawdzono, czy dump Kuźni z tabelą `odsylacze` jest publiczny.
- 3/4-gramy KWJP (26,5 MB, 9,4 MB) nie pobrane; szersze okno może trochę pomóc E1.
- Słowosieć 5.0 niedostępna (formularz = kontakt z autorami, zakazany).

## 7. Synteza wg ramy: źródło × cechy

| Źródło / metoda | Pokrycie (morze / roln. / mat.) | Nowe słowa | Trafność (próba 30) | Licencja | Nakład | Ocena |
|---|---|---|---|---|---|---|
| Etykiety SGJP | 27 / 0 / 23% | 254 / 96 / 62 leksemy | 29 / 27 / 30 | BSD-2 | mały (dane i kod są) | rdzeń |
| Słowosieć 4.5, A | 24 / 37 / 71% | 317 / 577 / 431 do gry | 23 / 14 / 23 | plWordNet (nota) | średni (korzenie, przegląd) | główne poszerzenie |
| Słowosieć 4.5, C | 59 / 40 / 86% | 568 / 877 / 589 do gry | C − A: 16 / 8 / 10 | j.w. | średni + więcej przeglądu | tylko części, bez skojarzeń |
| SGJP ∪ Słowosieć C | 78 / 40 / 86% | — | — | j.w. | — | najlepsze zmierzone |
| Słowosieć, domeny PWN (B1/B2) | 0–3 / 6–11 / 14–74% | małe | mat. B2 − A: 10 | j.w. | średni | słabe |
| IATE (plik pobrania) | nie mierzono | morze ≥1155, roln. ≥13 784, mat. ≥87 haseł; słowa pojedyncze 8 / 21 / 7% | nie mierzono | wolne użycie z atrybucją | średni (EU Login, filtr, mapowanie) | uzupełnienie |
| EuroVoc | nie mierzono | 8 / 65(+93 żywność) / 1 słów pojedynczych | — | atrybucja UE | mały | za mały |
| AGROVOC | nie mierzono | 34 780 + 8808 etykiet PL | — | PL niejasna | — | zablokowany |
| E1: bigramy KWJP | 9 / 3 / 3 słów testowych (całość) | <1000 kandydatów | top 50: 5–7 / 8–10 / 1–2 na 50 | CC BY 4.0 | mały | słabe |
| Rodziny SGJP (zastępczo) | 0–1 słowo | 118–411 | ~1 / ~2 / ~11 | BSD-2 | mały | słabe; tylko pochodne |
| KWJP½M `meta_topic` | — | teksty 1466 / 881 / 400 słów | — | CC BY 4.0 | mały | za mały |
| NKJP 1M | — | teksty 1464 / 1345 / 40 słów | — | CC BY (4.0 lub 3.0 PL) | mały | brak tematu |
| E3: LLM | nie mierzono | ocenia całą bazę (212 728) | nie mierzono | warunki dostawcy | średni–duży, koszt nieznany | jedyne pełne, do decyzji |
| Wikisłownik | nie mierzono | `{{żegl}}` 1856, `{{roln}}` 2333 stron (wszystkie języki) | — | CC BY-SA 4.0 | średni | odroczony |
| Wikidata Lexemes | — | 1 polski leksem z P9488 | — | CC0 | — | dziś bezużyteczne |
| WSJP | — | >160 tys. znaczeń z tematem | — | brak | — | tylko ręczny wgląd |

## 8. Wnioski
- **Główny:** listy tematyczne da się zbudować dla matematyki i morza z SGJP + Słowosieci (zbiór A plus części), z ręcznym przeglądem. Rolnictwo wymaga dodatkowych korzeni, IATE albo LLM.
- **Poboczne:** dane PAN (KWJP, NKJP) nie dają tematu; nadają się tylko do rangowania frekwencją. E2 jest zablokowana. E1 i rodziny słowotwórcze nie są warte wdrożenia jako metody główne.
- **Opcja (nie decyzja):** SGJP ∪ Słowosieć A + części (rel. 25, 27), ∩ STANDARD, przegląd próby; IATE (słowa pojedyncze) dla morza i po filtrze dla rolnictwa; LLM tylko po decyzji o koszcie. Kolejność: matematyka, morze, rolnictwo.
- **Wymaga ADR:** każda metoda spoza listy Zadania E (etykiety SGJP, Słowosieć, IATE) oraz oznaczenie E2 jako zablokowanej.
