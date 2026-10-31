# Przegląd wykrzykników SGJP w STANDARD (#15)

## TL;DR
- W STANDARD v31 jest 441 form, które SGJP podaje jako wykrzykniki.
  - **A, 191 form:** forma jest na liście SJP.pl albo ma wyraźne użycie w KWJP.
  - **B, 62 formy:** kandydaci.
  - **C, 188 form:** forma ma w SGJP także inną klasę, więc przegląd jej nie zmienia.
- Większość kandydatów B to rzadkie, prawdziwe polskie wyrazy dźwiękonaśladowcze i gwarowe: bz, ham, ura, tpru, dalbóg i podobne.
  - sjp.pl często je opisuje, ale jako „niedopuszczalne w grach”. Tej polityki SJP.pl nie przejmujemy.
- Polskiego znaczenia nie znalazłem w żadnym słowniku tylko dla dwóch form: **up** i **ou**.
  - Obie mają w KWJP przewagę oznaczeń obcych: up 115 wobec 7, ou 21 wobec 0.
- Rekomendacja: wykluczyć tylko up i ou, listą dokładnych analiz. Reszta zostaje.

## Key Decisions
- SJP.pl i Wikisłownik są tylko miarą do wskazania kandydatów. Nie są podstawą decyzji.
- Lista nie zmienia się w tym zgłoszeniu.

## Open Questions & Risks
- Decyzja należy do operatora (warianty niżej).
- Kandydatów B sprawdziłem w sjp.pl i Wikisłowniku tylko na próbce 16 form.

## Metoda
- Skrypt: `tmp/interj-review.py`, uruchomiony na przebiegu `data/work/lists-v31-20261012-162111-a`. SGJP: `sgjp-20260823`.
- Lista SJP.pl to zrzut `pl-sjp-20260820.dawg`: 3 240 471 słów, sha256 `2a593404…70b8`, zgodny z runbookiem.
- Reguła B: formy nie ma na liście SJP.pl, a jednocześnie w KWJP `interj` < 10 albo oznaczeń obcych (`xxs` + `xxx`) jest więcej niż `interj`.
- Asercje w skrypcie:
  - A + B + C = 441;
  - up trafia do B;
  - hej i ach trafiają do A;
  - grupa C nie jest pusta.

## Kandydaci B (62), od najczęstszych w KWJP (małe litery)
up, bz, ou, din, ham, wej, bac, ura, hum, ałła, dendele, dziu, brrum, bęk, csyt, cupu, dalbóg, dażbóg, dbrum, dobrydzień, drdr, dziń, fiku, glu, gluk, hap, hałła, hrym, hup, huź, huźha, kiw, kukuk, malu, miku, mojaśty, pluś, prastu, prastum, prrru, prru, pru, pry, pstręk, pyf, pyrg, rrrum, rrum, skik, szastum, szmyrk, terefere, tfy, tprr, tpru, tssyt, tst, wciurności, wiu, wiśt, wont, zerk

## Próbka 16 kandydatów
| forma | KWJP interj / obce / wszystkie | sjp.pl | Wikisłownik |
|---|---|---|---|
| up | 7 / 115 / 434 | tylko skrót UP | tylko angielskie |
| ou | 0 / 21 / 33 | brak hasła | brak polskiego |
| bz | 0 / 0 / 261 | jest: odgłos bzyczenia | — |
| din | 0 / 0 / 25 | tylko skrót DIN | — |
| ham | 0 / 0 / 23 | jest: łakome chwycenie ustami | — |
| wej | 0 / 0 / 17 | tylko w wu-wej, gwarowe | — |
| ura | 0 / 0 / 15 | jest: dawne „hura” | — |
| terefere | 0 / 0 / 0 | brak | brak |
| dalbóg | 0 / 0 / 0 | brak | brak |
| tpru | 0 / 0 / 0 | brak | brak |
| dobrydzień | 0 / 0 / 0 | brak | brak |
| mojaśty | 0 / 0 / 0 | — | brak (SGJP: gwar.) |

W wierszach terefere, dalbóg, tpru i dobrydzień wszystkie trzy liczby KWJP są zerowe.
To znane polskie wyrazy z SGJP; ich brak w KWJP wynika z rzadkości. Formy gwarowe przechodzą
do STANDARD zgodnie z zatwierdzoną polityką (`docs/generator/etykiety.md`: gwarowość nie
wyklucza). Spośród 441 form 124 nie występują w KWJP ani razu.

## Warianty
1. **Wykluczyć up i ou** listą dokładnych analiz (plik w kształcie `standard-age-exceptions.json`).
   - Dowód niezależny od SJP.pl: brak polskiego znaczenia i przewaga oznaczeń obcych w KWJP.
   - Ubytek: 2 formy. *Rekomendowany.*
2. **Zostawić wszystko.** SGJP jest zatwierdzonym źródłem, a up i ou są nieszkodliwe.
3. **Wykluczyć całe B (62).**
   - Usunęłoby prawdziwe wyrazy (bz, ham, ura) tylko dlatego, że brak ich na liście SJP.pl.
   - To byłoby przejęcie polityki SJP.pl, sprzeczne z AGENTS.md. Odradzam.

Prosta reguła „obce > interj” nie nadaje się do automatu: w grupie A trafia też w au, hoc,
kaput, pull i salam.

## Dalej (po decyzji)
Nowa wersja reguły albo pliku, nowy build, wydanie i wiki. To osobny krok.
