# Raport: słowniki tematyczne — czy i z czego je zbudujemy?

Typ: mieszany (pomiar danych + kod i dokumenty + źródła w sieci). Rundy: 1 (dane projektu i PAN), 2 (poszerzenie, wybór użytkownika). Data: 2026-10-27. Wykonawca: agent research (maister).

## TL;DR
Tak dla matematyki i morza, częściowo dla rolnictwa. Żadne jedno źródło nie wystarcza.
Etykiety SGJP dają trafny, wąski rdzeń (254 / 96 / 62 leksemy). Drzewa Słowosieci 4.5 od ręcznie wybranych korzeni dają największy przyrost.
Pokrycie słów oczywistych: SGJP 27 / 0 / 23%, Słowosieć 59 / 40 / 86%, razem 78 / 40 / 86% (morze / rolnictwo / matematyka).
IATE to dobre otwarte uzupełnienie. Korpusy PAN, n-gramy KWJP i rodziny słowotwórcze dają mało. AGROVOC zablokowany, Wikisłownik odroczony.
Rolnictwu brakuje czynności i budynków; pomóc mogą nowe korzenie albo LLM (bez wyceny). Pewność ogólna: średnia.

## Key Decisions
- Odpowiedź: listy tematyczne są możliwe, ale tylko z kilku źródeł naraz i z ręcznym przeglądem próby.
- Kombinację niżej (§7) podajemy jako opcję. Wybór należy do użytkownika.
- Etykiety SGJP, Słowosieć i IATE to metody spoza trzech metod Zadania E (prompt v3). Każda wymaga ADR.
- Metoda E2 (korpus dziedzinowy) nie ma korpusu spełniającego warunki. Prompt v3 każe ją wtedy oznaczyć jako zablokowaną.
- Metody E1 (n-gramy KWJP) i rodzin słowotwórczych nie polecamy jako głównych: pilotaż dał głównie szum.

## Open Questions / Risks
- Jeden oceniający. Trafność prób, lista 107 słów testowych i korzenie Słowosieci pochodzą od jednej osoby. Wartości mają pewność niską do średniej.
- Licencja Słowosieci: link licencji w repozytorium zwraca 404; nota mówi „plWordNet 4.2 © 2020”, dane to 4.5; zip nie ma pliku LICENSE.
- Wynik Słowosieci zależy od korzeni i wydania (matematyka A: 558 lematów w 4.2, 431 w 4.5).
- LLM: brak ceny i warunków dostawcy. To wydatek — wymaga dwóch potwierdzeń.
- Wieloznaczność: każde źródło przypisuje temat lematowi przez jedno znaczenie (`kot`, `kiosk`, `orka`, `pole`).

## Spis treści
1. Podsumowanie
2. Cel i zakres
3. Metoda
4. Wyniki rundy 1
5. Wyniki rundy 2
6. Porównanie źródeł
7. Opcja: proponowana kombinacja
8. Co wymaga ADR
9. Decyzje użytkownika
10. Analiza (wzorce, SWOT)
11. Odpowiedź i wnioski
12. Załączniki

## 1. Podsumowanie
Runda 1 sprawdziła dane projektu i zasoby PAN. Jedynym źródłem dziedziny okazały się etykiety SGJP: trafne, ale na 1,2% leksemów i bez słów podstawowych.
Runda 2 poszerzyła poszukiwania: Słowosieć (pobrana i zmierzona), metody Zadania E (pilotaż E1, opis E3), rodziny słowotwórcze, KWJP½M, NKJP 1M oraz źródła zewnętrzne (IATE, AGROVOC, EuroVoc, Wikisłownik, Wikidata).
Wynik: Słowosieć daje najwięcej słów podstawowych. Razem z SGJP pokrywa matematykę (86%) i morze (78%). Rolnictwo zostaje na 40%.

## 2. Cel i zakres
**Pytanie (po obu rundach):** czy da się zbudować listy tematyczne (marynistyka, rolnictwo, matematyka) i z czego?

**Podpytania:** które źródła mają temat słowa; ile słów dają i jak trafnie; jakie pokrycie słów oczywistych; na jakiej licencji; jakim nakładem; czego wymaga projekt (ADR, decyzje).

**W zakresie:** runda 1 — SGJP, Morfeusz, KWJP100, NKJP, WSJP, inne zasoby IPI PAN; runda 2 — Słowosieć 4.2/4.5, metody E1 i E3, rodziny SGJP, KWJP½M, NKJP 1M, IATE, AGROVOC, EuroVoc, Wikisłownik (tylko opis), Wikidata, Wikipedia, GEMET, GUS.
**Poza zakresem:** wdrożenie, zmiana reguł gry, kontakt z autorami (stąd bez Słowosieci 5.0 i tokenu API IATE), wywołania płatnych API, użycie danych Wikisłownika.

## 3. Metoda
- **Jednostka:** leksem SGJP (runda 1) lub lemat Słowosieci (runda 2). „Do gry” = jeden wyraz z małych liter polskich.
- **Test pokrycia:** te same 107 słów oczywistych w obu rundach (37 morze, 35 rolnictwo, 35 matematyka). W E1 i rodzinach bez słów będących zalążkami (28 / 35 / 27).
- **Trafność:** próby po 30 (ziarno 20261027), ocena trafne / wątpliwe / błędne, jeden oceniający.
- **Słowosieć:** zrzuty 4.2 i 4.5 z CLARIN-PL → SQLite. Podejścia: A (hiponimia od korzeni), C (A + części, miejsca, skojarzenia), B1/B2 (domeny Princeton WordNet po mapowaniu). Korzenie wybrane przed testem, bez strojenia.
- **E1:** bigramy lematów KWJP100 (lokalnie), ranking G², warianty min1/min2 i kontekstowy (PPMI).
- **E3:** tylko opis i szacunek tokenów; bez wywołań.
- **Źródła zewnętrzne:** strony, pojedyncze zapytania API, nagłówki HTTP; bez pobierania całych zbiorów.
- **Dane surowe:** `data/work/plwordnet/`, `data/work/kwjp-half-m/`, `data/work/nkjp-1m/` (gitignore). Skrypty w scratchpadzie sesji (`plwn/`, `metody/`, `pan2/`).
- **Rama:** tabela źródło × (pokrycie, nowe słowa, trafność, licencja, nakład).

## 4. Wyniki rundy 1 (skrót)

| # | Wynik | Pewność |
|---|---|---|
| W1 | SGJP ma etykiety dziedzin (pole 5 eksportu, 73 atomy); to cecha leksemu (≥90% form w 4032 z 4472 leksemów) | wysoka |
| W2 | Zasięg: 4472 z 387 398 leksemów (1,2%). Morze 254, rolnictwo 96, matematyka 62 leksemy; prawie wszystkie w BROAD/STANDARD v31 | wysoka |
| W3 | Trafność: 29/30, 27/30, 30/30 | średnia |
| W4 | Pokrycie słów oczywistych: 27% / 0% / 23% (brak `kotwica`, `pług`, `sinus`) | średnia |
| W5 | Kwalifikator oznacza termin, nie temat (WSJP *Zasady* s. 37, 47) | wysoka |
| W6 | Korpusy PAN nie oznaczają dziedziny słowa | wysoka |
| W7 | WSJP ma temat każdego znaczenia, ale bez licencji, eksportu i API | wysoka |
| W8 | Inne zasoby IPI PAN (SEJFEK, ELRC) nie pasują do 3 tematów | średnia |
| W9 | Kod: brak indeksu tematów; są wzorce (`quality.py:278`, `pop.py:162-185`, POP00) | wysoka |
| W10 | Prompt v3, Zadanie E: trzy metody (n-gramy KWJP, korpus dziedzinowy, LLM jako oceniający) | wysoka |

Szczegóły: `analysis/findings/local-data-*.md`, `code-docs-*.md`, `pan-resources-*.md`.

## 5. Wyniki rundy 2

### W11. Słowosieć: licencja pozwala na listy pochodne — **pewność: wysoka** (treść), **średnia** (wersja)
Licencja wzorowana na Princeton WordNet: wolno używać, zmieniać i rozpowszechniać, także komercyjnie. Warunek: nota copyright i zastrzeżenie przy każdej kopii. Nie wolno używać nazwy Politechniki Wrocławskiej w reklamie.
Publiczne wydania: 4.2 i 4.5 (CLARIN-PL, handle 11321/891 i 11321/834). Wydanie 5.0 tylko przez formularz — odpada.
Ryzyka: link licencji w repozytorium zwraca 404; nota na slowosiec.pl dotyczy 4.2; w zipach brak LICENSE. Zrzut 4.5 zawiera nazwiska redaktorów i log IP — surowego zrzutu nie publikujemy, tylko listy lematów.
Źródło: `wide-plwordnet-licencja-i-dane.md`; https://slowosiec.pl/pl/about (2026-10-27).

### W12. Słowosieć nie ma dziedzin, ale drzewo daje temat — **pewność: wysoka**
Pole `domain` to 54 klasy ogólne (`artefact`, `plant`), rejestr `specj.` nie mówi, jaka dziedzina. Temat daje drzewo hiponimii od ręcznie wybranych korzeni (np. `statek 1`, `zboże 1`, `pojęcie matematyczne 1`), plus części i miejsca.

| Temat | Podejście | Lematy do gry | W BROAD v31 | Nowe wobec SGJP | Lematy SGJP w zbiorze |
|---|---|---:|---:|---:|---:|
| Morze | A | 317 | 263 | — | 28/254 |
| Morze | C | 568 | 489 | 493 | 75/254 |
| Rolnictwo | A | 577 | 498 | — | 12/96 |
| Rolnictwo | C | 877 | 759 | 864 | 13/96 |
| Matematyka | A | 431 | 355 | — | 41/62 |
| Matematyka | C | 589 | 505 | 545 | 44/62 |

### W13. Pokrycie słów oczywistych rośnie najbardziej — **pewność: średnia**
| Temat | SGJP | Słowosieć A | Słowosieć C | SGJP ∪ C |
|---|---:|---:|---:|---:|
| Morze (37) | 27% | 24% | 59% | **78%** |
| Rolnictwo (35) | 0% | 37% | 40% | **40%** |
| Matematyka (35) | 23% | 71% | 86% | **86%** |

Braki: morze `rufa`, `burta`, `sztorm`, `rybak`; rolnictwo `orka`, `siew`, `żniwa`, `obora`, `ciągnik`, `ul`, `orać`; matematyka `pochodna`, `równanie`, `parabola`. Przyczyna: słowa leżą w innych gałęziach (`ciągnik` < `pojazd mechaniczny`, `sztorm` < `wiatr`).
Domeny Princeton WordNet po mapowaniu (B1/B2) są prawie bezużyteczne dla morza i rolnictwa (0–11%).

### W14. Trafność Słowosieci zależy od głębokości — **pewność: średnia** (jeden oceniający)
| Temat | A trafne / 30 | C − A trafne / 30 | Przykład szumu |
|---|---:|---:|---|
| Morze | 23 | 16 | `silnik`, `kot` |
| Rolnictwo | 14 | 8 | `monstera`, `nowomowa`, `opium` |
| Matematyka | 23 | 10 | `szeryf`, `eksport` |

Części i miejsca (rel. 25, 27) są lepsze od skojarzeń (rel. 108, 146). Rolnictwo A ma wiele wątpliwych roślin egzotycznych pod `roślina uprawna` — to decyzja redakcyjna.

### W15. IATE — dobre uzupełnienie — **pewność: wysoka** (licencja), **średnia** (liczby)
Licencja pliku pobrania: wolno kopiować, rozpowszechniać i przerabiać, także komercyjnie, z atrybucją „Download IATE, European Union, [rok]”. Nie dotyczy wyszukiwarki ani API.
Dostęp: plik z filtrami wymaga konta EU Login; stary pełny TBX z 2019 r. jest bez logowania (112,8 MB).

| Temat | Hasła PL (dolna granica) | Słowa pojedyncze w próbie | Przykłady |
|---|---:|---:|---|
| Morze | ≥1155 | 7,9% | `cuma`, `kilson`, `szpigat`, `żaglowiec` |
| Rolnictwo (z rybołówstwem i leśnictwem) | ≥13 784 | 20,7% | `karp`, `indyk`, ale też `fosfina`, `ebola` |
| Matematyka | ≥87 | 6,6% | `iloraz`, `mianownik`, `rzędna` |

Terminy głównie wielowyrazowe i urzędowe. Trafności i pokrycia na liście 107 słów nie mierzono.

### W16. Inne źródła zewnętrzne — **pewność: średnia do wysokiej**
- **AGROVOC:** 34 780 + 8808 polskich etykiet. Prawa do treści PL „rests with the institutions that authored it”; autora nie ustalono. **Zablokowany.**
- **EuroVoc:** licencja czysta (decyzja 2011/833/UE). Słów pojedynczych: morze 8, rolnictwo 65 (+93 żywność), matematyka 1. Za mały na listę; nadaje się na zalążek lub test.
- **Wikisłownik:** kwalifikator przy znaczeniu (lepiej niż SGJP); `{{żegl}}` 1856, `{{roln}}` 2333 stron (wszystkie języki); CC BY-SA 4.0. **Odroczony** decyzją użytkownika.
- **Wikidata Lexemes:** CC0, ale 1 polski leksem z dziedziną. Dziś bezużyteczne.
- **Wikipedia, GEMET, GUS, akty prawne:** marginalne. Otwartego polskiego słownika żeglarskiego, rolniczego ani matematycznego nie znaleziono.

### W17. Metoda E1 (n-gramy KWJP100) jest słaba — **pewność: średnia**
Odzysk słów testowych w całej liście kandydatów: morze 9/28, rolnictwo 3/35, matematyka 3/27. Precyzja top 50: 5–7, 8–10, 1–2 na 50.
Przyczyna: sąsiad w bigramie to kolokacja (`pole karne`, `liczba zgonów`, `Morze Bałtyckie`). Rdzeń SGJP prawie nie występuje w korpusie. Wariant kontekstowy (PPMI) jest gorszy.

### W18. Rodziny słowotwórcze nie dodają słów podstawowych — **pewność: średnia**
Eksport SGJP nie ma odsyłaczy słowotwórczych (tylko imiesłowy, odsłowniki, stopień wyższy). Morfeusz też nie. Miara zastępcza (wspólny początek lematu): odzysk 0–1 słowa na temat; precyzja ~1/30, ~2/30, ~11/30. Daje pochodne terminów (`dwumianowy`), nie temat.

### W19. KWJP½M i NKJP 1M nie dają podkorpusu tematycznego — **pewność: wysoka**
- KWJP½M: `meta_topic` tylko w 777 książkach (głównie gatunki). Teksty tematu: morze 1466, rolnictwo 881, matematyka 400 słów na 513 tys. Rdzeń SGJP: 5 / 0 / 0 trafień. Słowa tematu bez etykiety są (`pszczół`, `pasieka`, `jachtów`, `regat`) — to wspiera ideę E2, ale nie ten korpus.
- NKJP 1M (v1.2): 3889 nagłówków bez UKD i haseł BN; tylko typ i kanał. Teksty tematu po tytule: 1464 / 1345 / 40 słów, głównie ustawy. Rdzeń SGJP: 0 trafień jednoznacznych. Licencja: nkjp.pl CC BY 4.0, README CC BY 3.0 PL.

### W20. LLM (E3) — jedyny pełny przegląd bazy, bez wyceny — **pewność: niska** (bez wywołań)
Ocena 0–3 każdego leksemu z bazy (LLM nie dodaje słów; prompt v3, w. 418–422). Do oceny 212 728 leksemów z formą w STANDARD v31 (56 354 w KWJP100).
Szacunek na temat: ~1,7 mln tokenów wejścia i ~1,3 mln wyjścia (całość) albo ~0,45 / ~0,34 mln (tylko KWJP100). ×3 przebiegi dla niepewności. Ceny niesprawdzone.
Jako jedyna metoda może sięgnąć po słowa poza wybranymi drzewami (np. `orka`, `obora`) — nie zmierzono. Ryzyka: warunki wyniku u dostawcy, powtarzalność, wieloznaczność, stronniczość. Alternatywa: model o otwartych wagach na Macu (licencja wag do sprawdzenia).

## 6. Porównanie źródeł

| Źródło / metoda | Pokrycie (morze / roln. / mat.) | Precyzja (próba 30) | Licencja | Nakład | Ocena |
|---|---|---|---|---|---|
| Etykiety SGJP | 27 / 0 / 23% | 29 / 27 / 30 | BSD-2 | mały | **rdzeń** |
| Słowosieć 4.5, A | 24 / 37 / 71% | 23 / 14 / 23 | plWordNet + nota | średni | **główne poszerzenie** |
| Słowosieć 4.5, C | 59 / 40 / 86% | C − A: 16 / 8 / 10 | j.w. | średni + przegląd | części tak, skojarzenia nie |
| SGJP ∪ Słowosieć C | 78 / 40 / 86% | — | j.w. | — | najlepsze zmierzone |
| IATE (plik pobrania) | nie mierzono | nie mierzono | wolne, z atrybucją | średni (EU Login) | **uzupełnienie** |
| EuroVoc | nie mierzono | — | atrybucja UE | mały | za mały |
| AGROVOC | nie mierzono | — | PL niejasna | — | zablokowany |
| E1: bigramy KWJP | 9/28, 3/35, 3/27 słów | top 50: 5–7 / 8–10 / 1–2 na 50 | CC BY 4.0 | mały | słabe |
| Rodziny SGJP | 0–1 słowo | ~1 / ~2 / ~11 | BSD-2 | mały | słabe |
| KWJP½M / NKJP 1M | teksty 400–1466 słów | — | CC BY | mały | brak tematu, za małe |
| E3: LLM | nie mierzono | nie mierzono | warunki dostawcy | średni–duży, koszt nieznany | do decyzji |
| Wikisłownik | nie mierzono | — | CC BY-SA 4.0 | średni | odroczony |
| Wikidata Lexemes | ~0 | — | CC0 | — | bezużyteczne dziś |
| WSJP | — | — | brak | — | tylko ręczny wgląd |

## 7. Opcja: proponowana kombinacja (nie decyzja)

1. **Rdzeń:** leksemy z etykietą SGJP (`mors.`, `żegl.`, `ryb.`; `roln.`, `ogr.`, `zootechn.`, `pszcz.`, `leśn.`; `mat.`).
2. **Poszerzenie:** Słowosieć 4.5, zbiór A od korzeni z §5 plus części i miejsca (rel. 25, 27). Bez skojarzeń (rel. 108, 146) i bez domen PWN.
3. **Uzupełnienie:** słowa pojedyncze z IATE (plik pobrania) dla morza; dla rolnictwa po filtrze (bez gatunków łacińsko-polskich i chemii).
4. **Filtr:** mapowanie na leksemy SGJP, przecięcie ze STANDARD (temat to podzbiór bazy, prompt v3).
5. **Przegląd:** próba 50–100 na temat, najlepiej dwóch oceniających. Zapis niepewności przy słowach wieloznacznych.
6. **Pakiet:** wzór POP00 (osobna podkomenda, `method.json`, `LIMITATIONS.md`, noty w `ATTRIBUTIONS.md`).
7. **Kolejność:** matematyka (najtańsza, 86%), morze (78%), rolnictwo (40%; wymaga nowych korzeni dla czynności i budynków albo LLM).

Oczekiwany rozmiar (do gry, przed przeglądem): morze ok. 570–800, rolnictwo ok. 880–970, matematyka ok. 590–650 lematów (C + rdzeń SGJP; pewność niska).

## 8. Co wymaga ADR
- **Metoda spoza Zadania E.** Prompt v3 wymienia trzy metody. Etykiety SGJP, drzewa Słowosieci i IATE są poza nimi. Potrzebny ADR z uzasadnieniem i wynikami pilotażu.
- **Nowe źródła:** Słowosieć (licencja plWordNet, nota, wersja 4.5) i IATE (atrybucja, plik pobrania, data). Zapis warunków jak w audycie źródeł.
- **Status metod E:** E1 — wynik pilotażu (słaba); E2 — zablokowana (brak korpusu dziedzinowego spełniającego warunki); E3 — odroczona do decyzji o koszcie.
- **Reguła wieloznaczności:** jak oznaczać lemat, który wpada do tematu przez jedno znaczenie.

## 9. Decyzje użytkownika
1. **Licencja Słowosieci.** Czy przyjmujemy tekst ze slowosiec.pl (nota „4.2 © 2020”) jako licencję danych 4.5, mimo linku 404 i braku LICENSE w zipie?
2. **LLM.** Czy używamy? Jaki dostawca lub model o otwartych wagach? Jaki budżet? To wydatek: zasada dwóch potwierdzeń. Ceny i warunki wyniku trzeba odczytać w dniu decyzji.
3. **IATE.** Czy zakładamy konto EU Login (plik z filtrami, aktualny), czy bierzemy stary pełny TBX z 2019 r.?
4. **NKJP 1M.** Która wersja licencji (CC BY 4.0 czy 3.0 PL)? Potrzebne tylko, jeśli korpus wejdzie do pakietu; dziś nie wchodzi.
5. **Wikisłownik.** Czy odroczenie zostaje? Ma kwalifikatory przy znaczeniu, ale CC BY-SA 4.0 może objąć wydaną listę.
6. **Cel listy.** Czy wystarczy „rdzeń terminów” (SGJP), czy chcemy pełny temat ze słowami podstawowymi? Od tego zależy, czy Słowosieć i LLM są potrzebne.
7. **Granice tematu.** Np. czy rośliny egzotyczne i ozdobne pod `roślina uprawna` należą do rolnictwa.

## 10. Analiza

### Wzorce
- **Etykieta = termin.** SGJP, IATE, EuroVoc oznaczają terminy fachowe lub urzędowe, nie słowa podstawowe.
- **Drzewo pojęć łapie słowa podstawowe.** Słowosieć daje `kotwica`, `maszt`, `żagiel`; gubi czynności i budynki.
- **Temat leży w wielu gałęziach.** Każdy temat wymaga ręcznego doboru korzeni.
- **Sąsiad w tekście ≠ słowo tematu.** Bigramy dają kolokacje.
- **Metadane opisują tekst, nie słowo.** We wszystkich korpusach PAN.
- **Im lepsze dane, tym gorsza licencja.** WSJP bez licencji, AGROVOC-PL niejasny, Wikisłownik CC BY-SA; czyste źródła są małe (EuroVoc, Wikidata) lub terminologiczne (IATE).

### SWOT (kombinacja SGJP + Słowosieć + IATE)
| Mocne | Słabe |
|---|---|
| pokrycie 78% / 86% dla morza i matematyki; licencje pozwalają na listy pochodne; dane lokalne; wzór pakietu gotowy | rolnictwo 40%; ręczny dobór korzeni; przegląd szumu; jeden oceniający; temat per lemat, nie per znaczenie |
| **Szanse** | **Zagrożenia** |
| LLM lub nowe korzenie domkną rolnictwo; ta sama procedura dla innych tematów (kulinaria, muzyka); IATE dokłada terminy | niejasna wersja licencji Słowosieci; wynik zależy od wydania i korzeni; koszt LLM nieznany; homonimy w liście |

## 11. Odpowiedź i wnioski
**Bezpośrednia odpowiedź:** tak, listy tematyczne da się zbudować. Matematykę i morze — z etykiet SGJP i drzew Słowosieci 4.5 (pokrycie 86% i 78%), z ręcznym przeglądem; IATE może dołożyć terminy. Rolnictwo — tylko częściowo (40%); trzeba nowych korzeni, IATE po filtrze albo LLM.
Dane PAN (KWJP, NKJP) nie dają tematu. Metody E1 i rodziny słowotwórcze są słabe; E2 jest zablokowana.

**Pewność ogólna: średnia.** Liczby źródeł są pewne. Trafność i pokrycie ocenił jeden oceniający na małych próbach.

## 12. Załączniki

### Źródła
- Findings runda 1: `analysis/findings/local-data-sgjp-dziedziny.md`, `local-data-kwjp-nkjp.md`, `code-docs-kod-i-konfiguracja.md`, `code-docs-decyzje-i-dokumenty.md`, `code-docs-pomiary.md`, `pan-resources-slowniki.md`, `pan-resources-korpusy.md`.
- Findings runda 2: `wide-plwordnet-licencja-i-dane.md`, `wide-plwordnet-pomiar.md`, `wide-metody-zalazki-kwjp.md`, `wide-metody-rodziny-sgjp.md`, `wide-metody-llm.md`, `wide-pan-sprawdzenia-kwjp-half-m.md`, `wide-pan-sprawdzenia-nkjp-1m.md`, `wide-zewnetrzne-zrodla.md`.
- Dane lokalne: `cache/sgjp/sgjp-20260823.tab.gz`, `cache/kwjp/*`, `cache/nkjp/*`, `data/work/lists-v31-20261012-162111-a/build.sqlite`, `data/work/release-LL-PL-v30/`, `data/work/plwordnet/`, `data/work/kwjp-half-m/`, `data/work/nkjp-1m/`.
- Sieć (2026-10-27): https://sgjp.pl/oznaczenia/, https://pliki.wsjp.pl/zasady_opracowania_wsjp.pdf, https://slowosiec.pl/pl/about, https://clarin-pl.eu/dspace/handle/11321/834, https://clarin-pl.eu/dspace/handle/11321/891, https://iate.europa.eu/assets/i18n/en/static_pages/iate_dl_conditions.html, https://www.fao.org/agrovoc/maintenance, https://data.europa.eu/api/hub/search/datasets/eurovoc, https://github.com/ipipan/kwjp100-varia, https://nkjp.pl/index.php?page=14&lang=0.

### Luki
- Brak drugiego oceniającego i niezależnej listy słów testowych.
- Nie zmierzono pokrycia i trafności IATE, EuroVoc, AGROVOC na liście 107 słów.
- LLM bez wywołań i bez ceny.
- Rolnictwo: nie sprawdzono dodatkowych korzeni Słowosieci.
- Nie sprawdzono, czy dump Kuźni z odsyłaczami jest publiczny; 3/4-gramy KWJP nie pobrane.
- Słowosieć 5.0 niedostępna (formularz = kontakt z autorami).
