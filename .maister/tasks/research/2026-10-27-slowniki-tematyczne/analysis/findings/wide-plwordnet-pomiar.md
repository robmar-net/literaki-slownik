# Słowosieć 4.5: pomiar trzech tematów

## TL;DR
Drzewo Słowosieci (hiponimia, części, skojarzenia) daje dużo więcej słów tematu niż kwalifikatory SGJP. Pokrycie oczywistych słów: morze 59%, rolnictwo 40%, matematyka 86%. W SGJP było 27%, 0% i 23%.
Trafność zależy od głębokości. Samo drzewo hiponimii: morze 23/30, rolnictwo 14/30, matematyka 23/30 trafnych. Dodatki z części i skojarzeń są słabsze: 16/30, 8/30 i 10/30.
Domeny tematyczne Princeton WordNet po mapowaniu są prawie bezużyteczne dla morza i rolnictwa (0–11% pokrycia). Dla matematyki działają, ale są szumne.
SGJP i Słowosieć prawie się nie pokrywają (morze 30%, rolnictwo 14% lematów SGJP). Razem dają pokrycie: morze 78%, rolnictwo 40%, matematyka 86%.

## Key Decisions
- Korzenie wybrałem z góry, przed testem pokrycia (lista niżej). Pod test ich nie stroiłem. Mogłoby to zawyżyć pokrycie.
- Jednostka to lemat Słowosieci (`lexicalunit.lemma`, `pos` 1–4). Słowo „do gry” to lemat jednowyrazowy z samych małych liter polskich (`^[a-ząćęłńóśźż]+$`). „W BROAD” znaczy, że lemat jest w `data/work/release-LL-PL-v30/LL-PL-BROAD.txt` (v31; zob. `local-data-sgjp-dziedziny.md`).
- Trafność oceniam na poziomie lematu, nie znaczenia. `pole`, `para` i `rząd` mają sens matematyczny, ale jako słowa z listy liczę je jako wątpliwe.
- Wyniki główne podaję dla 4.5. Wyniki 4.2 podaję dla porównania, bo jego drzewo matematyczne jest inne.

## Open Questions / Risks
- Próby i test pokrycia ocenił jeden oceniający, czyli ja. Lista słów do testu pochodzi z rundy 1 i też ma jednego autora. Pewność wartości: niska do średniej.
- Wynik zależy od wyboru korzeni. Inny zestaw (np. `zwierzę hodowlane` zamiast `zwierzę gospodarskie`, które daje 980 lematów) zmieni liczby.
- Wieloznaczność: lemat wchodzi do tematu przez jedno znaczenie (`kot` jako mała kotwica, `kiosk` w okręcie podwodnym, `orka` jako ssak). Na liście słów tego nie widać.
- Czynności rolnicze leżą w drzewie poza tematem: `orać` < `obrabiać`, `orka` < `harówka`, `obora` < `budynek inwentarski` < `pomieszczenie, w którym żyją zwierzęta`. Rolnictwo wymaga innych korzeni albo innej metody.
- Między 4.2 a 4.5 drzewo matematyczne się zmieniło. Podejście A zmalało z 558 do 431 lematów, a `równanie` wypadło z tematu. Wyniki zależą więc od wydania.

## Metoda
Skrypty: `/private/tmp/claude-501/-Users-robmar-Projects-Literaki/7eed58b5-7e1f-4a3f-8359-d9bc24330c2b/scratchpad/plwn/`
- `to_sqlite.py`: zrzut MySQL → SQLite.
- `lib.py`: domknięcia relacji. Baza w zmiennej `PLWN_DB`.
- `measure.py`: zbiory A/C/B1/B2 i przecięcia → `summary-45.json`, `summary-42.json`.
- `cover_sample.py`: test pokrycia i próby po 30 lematów (`random.Random(20261027)`) → `samples-45.txt`, `samples-42.txt`.
- Uruchomienie: `PLWN_DB=…/plwn45.sqlite python3 -I measure.py && … cover_sample.py`.

Podejścia:
- **A**: hiponimy korzeni (rel. 11, domknięcie).
- **C**: A plus części i miejsca z A (rel. 25, 27) z ich hiponimami, plus jeden krok fuzzynimii i określnika (rel. 108, 146).
- **B1**: członkowie domen tematycznych PWN (rel. 183), przeniesieni do plWN przez synonimię międzyjęzykową (208/209, 3005/3006, 228/229).
- **B2**: B1 plus hiponimy PWN członków (rel. 171), plus hiponimy plWN podpięte pod nie (rel. 210), z domknięciem w plWN.

Korzenie (id synsetu: nazwa):
- Morze: 7354 `statek 1`, 2149 `okręt 1`, 4511 `łódź 2`, 6214 `marynarz 1`, 13299/417999 `żeglarz 2/1`, 14136 `żegluga 1`, 14515 `żeglarstwo 1`. Domeny PWN: seafaring, navigation, ship, boat, sailing vessel, sailing, water travel, shipbuilding, shipping, maritime law, fishing.
- Rolnictwo: 4721 `roślina uprawna 1`, 4624 `zboże 1`, 25882 `maszyna rolnicza 1`, 14426 `narzędzie rolnicze 1`, 45566 `zwierzę gospodarskie 1`, 15900 `nawóz 1`, 5990 `rolnik 1`, 249040 `uprawa 2`, 2916/71969 `rolnictwo 1/2`. Domeny PWN: farming, animal husbandry, gardening, forestry, livestock.
- Matematyka: 8086 `pojęcie matematyczne 1`, 46351 `obiekt matematyczny 1`, 48390 `figura geometryczna 1`, 20685 `liczba 2`, 885 `funkcja 3`, 8076 `działanie matematyczne 1`, 13154 `matematyk 1`, 8122 `matematyka 1`. Domeny PWN: mathematics, geometry, arithmetic, algebra, matrix algebra.

## W1. Rozmiar tematu (4.5) — **pewność: wysoka** (liczby), zależą od korzeni
| Temat | Podejście | Synsety | Lematy | Do gry | W BROAD | Lematy SGJP z etykietą tematu w zbiorze |
|---|---|---:|---:|---:|---:|---:|
| Morze | A | 403 | 505 | 317 | 263 | 28/254 (11%) |
| Morze | C | 792 | 1011 | 568 | 489 | 75/254 (30%) |
| Morze | B1 | 31 | 42 | 35 | 32 | 6/254 (2%) |
| Morze | B2 | 68 | 90 | 69 | 62 | 12/254 (5%) |
| Rolnictwo | A | 992 | 1568 | 577 | 498 | 12/96 (12%) |
| Rolnictwo | C | 1398 | 1965 | 877 | 759 | 13/96 (14%) |
| Rolnictwo | B1 | 22 | 33 | 32 | 32 | 1/96 (1%) |
| Rolnictwo | B2 | 99 | 122 | 116 | 114 | 1/96 (1%) |
| Matematyka | A | 841 | 996 | 431 | 355 | 41/62 (66%) |
| Matematyka | C | 1076 | 1273 | 589 | 505 | 44/62 (71%) |
| Matematyka | B1 | 130 | 175 | 119 | 113 | 4/62 (6%) |
| Matematyka | B2 | 1832 | 2128 | 897 | 782 | 38/62 (61%) |

- Nowe słowa wobec SGJP (do gry, spoza etykiet tematu) w C: morze 493, rolnictwo 864, matematyka 545.
- Dla porównania 4.2: morze C 566 do gry, rolnictwo C 914, matematyka A 558, C 751, B2 791 (`summary-42.json`).
- Domeny PWN mają niewielu członków: morze 96 synsetów PWN, rolnictwo 40, matematyka 194. Mapowanie na plWN gubi większość z nich.

## W2. Pokrycie oczywistych słów (te same 107 słów co w rundzie 1) — **pewność: średnia**
Wszystkie 107 słów są w Słowosieci 4.5. Liczę, czy lemat jest w zbiorze.

| Temat | A | C | B1 | B2 | SGJP (runda 1) | SGJP ∪ C |
|---|---:|---:|---:|---:|---:|---:|
| Morze (37) | 9 (24%) | 22 (59%) | 0 | 1 (3%) | 10 (27%) | 29 (78%) |
| Rolnictwo (35) | 13 (37%) | 14 (40%) | 2 (6%) | 4 (11%) | 0 | 14 (40%) |
| Matematyka (35) | 25 (71%) | 30 (86%) | 5 (14%) | 26 (74%) | 8 (23%) | 30 (86%) |

- Morze, brak w C: `kil`, `rufa`, `burta`, `sztorm`, `bandera`, `reja`, `rybak`, `halsować`, `falochron`, `nabrzeże`, `kuk`, `bakburta`, `sterburta`, `achtersztag`, `trał`. Siedem z nich ma etykietę w SGJP.
- Rolnictwo, brak w C: `orka`, `siew`, `żniwa`, `snop`, `stóg`, `obora`, `chlew`, `ciągnik`, `opryskiwacz`, `siano`, `ul`, `pasieka`, `bronować`, `orać`, `siać`, `kosić`, `ugór`, `zagon`, `miedza`, `ściernisko`, `kośnik`.
- Matematyka, brak w C: `pochodna`, `równanie`, `średnica`, `parabola`, `hiperbola`. W 4.2 brakowało 4 słów: `równanie` wtedy było w temacie.
- Przyczyna braków: słowa leżą w innych gałęziach drzewa. Przykłady: `ciągnik` < `pojazd mechaniczny`; `siano` < `karma` < `jedzenie`; `sztorm` < `wiatr`; `rybak` < `człowiek ze względu na swoje zajęcie`; `parabola` < `stożkowa` < `owal` < `figura geometryczna 2` (kształt, nie pojęcie). Według mnie dokładanie korzeni pomoże, ale to praca ręczna dla każdego tematu.

## W3. Trafność (próba 30 lematów do gry, 4.5) — **pewność: średnia** (jeden oceniający)
| Temat | Zbiór | Trafne | Wątpliwe | Błędne | Przykłady |
|---|---|---:|---:|---:|---|
| Morze | A | 23 | 7 | 0 | trafne: `flueta`, `bosman`, `welbot`, `sejner`; wątpliwe: `kanu`, `piroga`, `handlowiec` |
| Morze | C − A | 16 | 12 | 2 | trafne: `bramsel`, `falszkil`, `genua`, `odcumowywać`; wątpliwe: `kot`, `kiosk`, `peryskop`; błędne: `silnik`, `dwubieg` |
| Rolnictwo | A | 14 | 14 | 2 | trafne: `płaskurka`, `saradela`, `kopaczka`, `supertomasyna`; wątpliwe: `pizang`, `chardonnay`, `yerba`; błędne: `przebiśnieg`, `monstera` |
| Rolnictwo | C − A | 8 | 11 | 11 | trafne: `lemiesz`, `dymka`, `łąkarstwo`; błędne: `nowomowa`, `tabakiera`, `opium` |
| Matematyka | A | 23 | 6 | 1 | trafne: `cosec`, `ostrosłup`, `kwartyl`, `transformata`; wątpliwe: `pięćsetka`, `entropia`; błędne: `izentropa` |
| Matematyka | C − A | 10 | 8 | 12 | błędne: `szeryf`, `eksport`, `zarobek`, `kosmologia` |
| Matematyka | B2 − A | 10 | 13 | 7 | wątpliwe: `piętnastokrotny`, `grupa`; błędne: `oko`, `lupa`, `firmament` |

- Ta sama próba na 4.2 (`samples-42.txt`): morze A 27/3/0, C − A 18/9/3; rolnictwo A 18/11/1, C − A 7/10/13; matematyka A 13/10/7, C − A 5/5/20, B2 − A 7/11/12. W 4.2 drzewo `pojęcie matematyczne` ciągnęło szum (`firmament`, `niedopłata`, `stan`, `dryf`).
- Kryterium ma rolnictwo wątpliwe dla roślin egzotycznych i ozdobnych pod `roślina uprawna` (`pomelo`, `monstera`). To decyzja redakcyjna: czy „roślina uprawna” to temat rolniczy.
- Wzór: A jest dość trafne. Dodatki C są w połowie szumem, bo fuzzynimia i określnik łączą luźno. Części (rel. 25, 27) są lepsze od skojarzeń (rel. 108).

## W4. Porównanie z SGJP i z BROAD — **pewność: wysoka**
- Słowosieć i SGJP opisują różne warstwy. SGJP ma terminy olinowania i manewrów (`achtersztag`, `halsować`). Słowosieć ma typy statków, części i słowa podstawowe (`kotwica`, `maszt`, `żagiel`, `pokład`). Z 254 leksemów morskich SGJP tylko 75 jest w C.
- Matematyka się pokrywa: 44 z 62 leksemów `mat.` w C. Słowosieć dodaje 545 nowych lematów do gry.
- 85–88% lematów do gry z C jest w BROAD v31 (morze 489/568, rolnictwo 759/877, matematyka 505/589). Poza BROAD zostaje 79, 118 i 84 lematów. To rzadkie terminy i nazwy obce (`dhow`, `drakar`, `daikon`, `basmati`) oraz skróty (`cos`, `ctg`, `arctg`). Takich słów lista i tak nie przyjmie.

## Wniosek
Słowosieć to najlepsze z dotąd zbadanych otwartych źródeł tematu dla morza i matematyki. Daje setki słów, w tym słowa podstawowe. Wymaga jednak ręcznego wyboru korzeni i przeglądu, bo nie ma etykiet dziedzin. Dla rolnictwa daje rośliny, zwierzęta i narzędzia, ale gubi czynności i budynki. Najlepsza kombinacja to SGJP (rdzeń) plus drzewo A Słowosieci z wybranymi częściami. To opcja do decyzji użytkownika. Potrzebny byłby ADR, bo to metoda spoza trzech metod Zadania E.
