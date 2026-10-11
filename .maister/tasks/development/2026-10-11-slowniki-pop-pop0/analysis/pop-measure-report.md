# Pomiar POP i POP0 — etap A

Raport tylko do odczytu. NKJP wyłącznie jako rangi, percentyle i udziały (C14). Przykłady w tabelach to **ilustracja**, nie próba losowa. Próba losowa jest w sekcji „Próbki”.

## TL;DR
- Baza bez zmian: hash przed = po (`85b23ca5cfaa…`).
- Wariant bazowy: D5 `e-common`, D3 KWJP+NKJP (F, waga 0,5), D4 `strip-edges-keep-dot`, POP = 40 000 leksemów, POP0 = 5 000.
- POP bazowy: 40 000 leksemów, 902 062 form STANDARD, pokrycie kwjp-all 89,8%, kwjp-standard 98,3%.
- Sufit pokrycia (wszystkie leksemy): kwjp-all 91,1%.
- D5d łączy łańcuchowo: największa grupa 112 leksemów; `e-common`: 22.
- NKJP ściśle jednoznaczne (D5c) przypisuje 45,3% masy dopasowanej; d 93,9%; `e-common` 72,6%.
- Reguła D4 `strip-edges-keep-dot`: dopasowane 87,1% tokenów NKJP.

## Podstawa

| pole | wartość |
|---|---|
| leksemy z formą w STANDARD | 236 595 |
| w tym nazwy własne | 23 670 |
| w tym potoczne (`pot.`) | 2 410 |
| formy STANDARD | 3 090 194 |
| leksemy KWJP (EXACT) / grupy AMBIGUOUS | 70 771 / 11 834 |
| options_sha256 | `6092c6a75711d9ed…` |
| code_identity | `81a5f82ae66f9457…` |

## D1 — mianownik pokrycia

| mianownik | masa KWJP | POP bazowy | sufit (wszystkie leksemy) |
|---|---|---|---|
| kwjp-all | 81 664 894 | 89,8% | 91,1% |
| kwjp-exact | 76 386 837 | 93,0% | 93,9% |
| kwjp-standard | 74 540 021 | 98,3% | 99,8% |

Masa KWJP: EXACT 76 386 837, AMBIGUOUS 3 468 121, UNMATCHED 1 809 936.

**Zalecenie D1:** progi liczyć w `kwjp-standard`; w raporcie zawsze też `kwjp-all`. Cel „98–99% tekstu” w `kwjp-all` jest nieosiągalny (sufit 91,1%).

## D2 — formy listy

POP bazowy (40 000 leksemów). STANDARD: 3 090 194 form, z leksemem (reguła i): 3 004 843.

| wariant | formy | zmiana vs pełna | usunięte wg klasy | udział masy NKJP usuniętych |
|---|---|---|---|---|
| pełna odmiana | 902 062 | −0 / +0 | — | 0,00% |
| bez wołacza | 896 926 | −5 136 / +0 | voc 5 136 | 0,02% |
| bez rozkaźnika | 876 199 | −25 863 / +0 | impt 25 863 | 0,17% |
| bez imiesłowów | 710 550 | −191 512 / +0 | participle 191 512 | 1,98% |
| bez os. 1/2 | 691 412 | −210 650 / +0 | person-1-2 210 650 | 2,28% |
| bez czterech klas | 494 764 | −407 298 / +0 | impt 25 866, participle 191 512, person-1-2 210 650, voc 5 139 | 4,28% |
| bez konstrukcji | 868 567 | −33 495 / +0 | — | 0,00% |
| reguła (ii) | 897 671 | −4 391 / +0 | — | 0,31% |

**Zalecenie D2:** pełna odmiana, konstrukcje: tak, reguła (i). Wykluczenia klas tną formy, które gracz zna z tekstu; reguła (ii) kosztuje kilkanaście minut na każdy `pop` (czas tutaj: 907,3 s).

## D3 — miara i wagi

| miara | leksemy | formy | pokrycie kwjp-all | kwjp-exact | kwjp-standard | Spearman vs bazowa | top 5 000 wspólne | top 40 000 wspólne | POP Jaccard |
|---|---|---|---|---|---|---|---|---|---|
| KWJP+NKJP F, waga 0,5 | 40 000 | 902 062 | 89,8% | 93,0% | 98,3% | 1,0000 | 100,0% | 100,0% | 100,0% |
| KWJP+NKJP F, waga 0,75 | 40 000 | 895 081 | 89,9% | 93,1% | 98,5% | 0,9878 | 96,7% | 94,7% | 93,3% |
| KWJP+NKJP F, waga 0,25 | 40 000 | 912 358 | 89,5% | 92,7% | 98,0% | 0,9905 | 96,4% | 94,2% | 93,2% |
| sama KWJP: F | 40 000 | 889 849 | 90,0% | 93,3% | 98,6% | 0,9705 | 92,7% | 86,8% | 89,6% |
| sama KWJP: ARF | 40 000 | 837 012 | 90,0% | 93,2% | 98,6% | 0,9561 | 86,3% | 86,0% | 86,0% |
| sama KWJP: 1-DP | 40 000 | 869 552 | 89,9% | 93,1% | 98,5% | 0,9355 | 81,7% | 84,5% | 84,0% |
| sama KWJP: gatunki | 40 000 | 728 111 | 62,3% | 64,2% | 68,3% | 0,3212 | 6,5% | 78,9% | 50,0% |

Pewność dopasowania (jednostki wszystkie / w POP): AMBIGUOUS 1 216 / 751, EXACT 51 611 / 25 571, NKJP_ONLY 38 447 / 1 176, NONE 128 504 / 0.

**Zalecenie D3:** KWJP+NKJP z percentyli, F, waga 0,5. Sama KWJP (F) zostaje ścieżką wycofania NKJP (ADR-006); różnicę pokazują kolumny Spearman i Jaccard.

## D4 — czyszczenie NKJP

| reguła | id | dopasowane tokeny | kolizje | masa scalona | D5c przypisane |
|---|---|---|---|---|---|
| full-nfc | `nkjp-clean-full-nfc-v1` | 77,7% | 0 | 0,00% | 44,4% |
| strip-edges | `nkjp-clean-strip-edges-v1` | 93,7% | 636 328 | 16,06% | 45,5% |
| strip-edges-keep-dot | `nkjp-clean-strip-edges-keep-dot-v1` | 87,1% | 548 375 | 9,39% | 45,3% |

Największe kolizje (ilustracja; bez liczb, liczby tylko w `measure.json`):

- `strip-edges`: `się` ← `się,`/`się.`, `r` ← `r.`/`r.,`, `to` ← `to,`/`to.`, `art` ← `art.`/`(art.`, `tak` ← `tak,`/`tak.`, `tym` ← `tym,`/`tym.`, `nie` ← `nie,`/`nie.`, `zł` ← `zł.`/`zł,`, `roku` ← `roku.`/`roku,`, `w` ← `w.`/`(w`
- `strip-edges-keep-dot`: `się` ← `się,`/`się:`, `to` ← `to,`/`to:`, `tym` ← `tym,`/`tym:`, `tak` ← `tak,`/`tak?`, `tego` ← `tego,`/`tego?`, `nie` ← `nie,`/`"nie`, `w` ← `(w`/`"w`, `wiem` ← `wiem,`/`wiem?`, `powiedzieć` ← `powiedzieć,`/`powiedzieć:`, `roku` ← `roku,`/`roku?`

**Zalecenie D4:** `strip-edges-keep-dot` — zdejmuje cudzysłowy i nawiasy, ale nie skleja skrótów z kropką (`ul.`, `r.`, `art.`), które dominują kolizje `strip-edges`.

## D5 — homonimy

| opcja | leksemy | formy | pokrycie kwjp-all | kwjp-exact | kwjp-standard | KWJP przypisane | NKJP przypisane | grupy | największa |
|---|---|---|---|---|---|---|---|---|---|
| a: brak F przy niejednoznaczności | 40 000 | 1 026 659 | 87,3% | 93,4% | 95,7% | 87,8% | 23,4% | 0 | 1 |
| b: F kopiowane z flagą (tylko porównanie) | 40 000 | 782 324 | 90,1% | 92,9% | 98,7% | 91,3% | 93,9% | 0 | 1 |
| c: tylko formy jednoznaczne | 40 000 | 1 031 598 | 87,6% | 93,3% | 95,9% | 87,8% | 45,3% | 0 | 1 |
| d: grupa homonimów (wszyscy właściciele) | 40 000 | 616 005 | 90,1% | 92,7% | 97,7% | 92,2% | 93,9% | 18 457 | 112 |
| e dosłowne: łączy tylko leksemy z formą w STANDARD | 40 000 | 617 873 | 89,0% | 91,8% | 97,5% | 91,1% | 89,0% | 18 288 | 102 |
| e bez nazw własnych | 40 000 | 902 062 | 89,8% | 93,0% | 98,3% | 90,6% | 72,6% | 11 377 | 22 |

Los słów (ilustracja): ranga jednostki, liczba leksemów w jednostce, czy w POP.

| forma | leksemy | a | b | c | d | e-literal | e-common |
|---|---|---|---|---|---|---|---|
| `nie` | 4 | nie:C: r 184, 1 leks., POP; nie:I: r 20 203, 1 leks., POP; nie:T: r 8, 1 leks., POP (+1) | nie:C: r 105, 1 leks., POP; nie:I: r 12 481, 1 leks., POP; nie:T: r 8, 1 leks., POP (+1) | nie:C: r 180, 1 leks., POP; nie:I: r 20 243, 1 leks., POP; nie:T: r 8, 1 leks., POP (+1) | nie:C: r 1, 18 leks., POP; nie:I: r 1, 18 leks., POP; nie:T: r 1, 18 leks., POP (+1) | nie:C: r 1, 17 leks., POP; nie:I: r 1, 17 leks., POP; nie:T: r 1, 17 leks., POP (+1) | nie:C: r 1, 15 leks., POP; nie:I: r 1, 15 leks., POP; nie:T: r 1, 15 leks., POP (+1) |
| `to` | 6 | ten: r 11, 1 leks., POP; to:C: r 4 407, 1 leks., POP; to:M: r 91, 1 leks., POP (+3) | ten: r 7, 1 leks., POP; to:C: r 2 655, 1 leks., POP; to:M: r 47, 1 leks., POP (+3) | ten: r 7, 1 leks., POP; to:C: r 4 410, 1 leks., POP; to:M: r 87, 1 leks., POP (+3) | ten: r 4, 20 leks., POP; to:C: r 4, 20 leks., POP; to:M: r 4, 20 leks., POP (+3) | ten: r 3, 17 leks., POP; to:C: r 3, 17 leks., POP; to:M: r 3, 17 leks., POP (+3) | ten: r 3, 11 leks., POP; to:C: r 3, 11 leks., POP; to:M: r 3, 11 leks., POP (+3) |
| `być` | 4 | Być:Sf: r —, 1 leks.; Być:Sm1: r —, 1 leks.; bycie: r 16 338, 1 leks., POP (+1) | Być:Sf: r 49 137, 1 leks.; Być:Sm1: r 49 133, 1 leks.; bycie: r 10 132, 1 leks., POP (+1) | Być:Sf: r —, 1 leks.; Być:Sm1: r —, 1 leks.; bycie: r 16 317, 1 leks., POP (+1) | Być:Sf: r 3, 48 leks., POP; Być:Sm1: r 3, 48 leks., POP; bycie: r 3, 48 leks., POP (+1) | Być:Sf: r 2, 21 leks., POP; Być:Sm1: r 2, 21 leks., POP; bycie: r 2, 21 leks., POP (+1) | Być:Sf: r —, 1 leks.; Być:Sm1: r —, 1 leks.; bycie: r 15 318, 1 leks., POP (+1) |
| `rok` | 4 | Rok:Sf: r —, 1 leks.; Rok:Sm1: r —, 1 leks.; rok:Sm3~lata: r —, 1 leks. (+1) | Rok:Sf: r 28 185, 1 leks., POP; Rok:Sm1: r 27 875, 1 leks., POP; rok:Sm3~lata: r 25, 1 leks., POP (+1) | Rok:Sf: r —, 1 leks.; Rok:Sm1: r 35 122, 1 leks., POP; rok:Sm3~lata: r —, 1 leks. (+1) | Rok:Sf: r 20, 14 leks., POP; Rok:Sm1: r 20, 14 leks., POP; rok:Sm3~lata: r 20, 14 leks., POP (+1) | Rok:Sf: r 18, 13 leks., POP; Rok:Sm1: r 18, 13 leks., POP; rok:Sm3~lata: r 18, 13 leks., POP (+1) | Rok:Sf: r —, 1 leks.; Rok:Sm1: r 33 010, 1 leks.; rok:Sm3~lata: r 25, 2 leks., POP (+1) |
| `raz` | 2 | raz:Sm3~a~u: r —, 1 leks.; raz:Sm3~u: r —, 1 leks. | raz:Sm3~a~u: r 60, 1 leks., POP; raz:Sm3~u: r 61, 1 leks., POP | raz:Sm3~a~u: r 15 582, 1 leks., POP; raz:Sm3~u: r —, 1 leks. | raz:Sm3~a~u: r 50, 4 leks., POP; raz:Sm3~u: r 50, 4 leks., POP | raz:Sm3~a~u: r 46, 4 leks., POP; raz:Sm3~u: r 46, 4 leks., POP | raz:Sm3~a~u: r 42, 4 leks., POP; raz:Sm3~u: r 42, 4 leks., POP |
| `dzień` | 7 | Dzień:Sf: r —, 1 leks.; Dzień:Sm1: r —, 1 leks.; dzienia: r —, 1 leks. (+4) | Dzień:Sf: r 32 455, 1 leks., POP; Dzień:Sm1: r 32 454, 1 leks., POP; dzienia: r 474, 1 leks., POP (+4) | Dzień:Sf: r —, 1 leks.; Dzień:Sm1: r —, 1 leks.; dzienia: r —, 1 leks. (+4) | Dzień:Sf: r 59, 17 leks., POP; Dzień:Sm1: r 59, 17 leks., POP; dzienia: r 59, 17 leks., POP (+4) | Dzień:Sf: r 58, 11 leks., POP; Dzień:Sm1: r 58, 11 leks., POP; dzienia: r 58, 11 leks., POP (+4) | Dzień:Sf: r —, 1 leks.; Dzień:Sm1: r —, 1 leks.; dzienia: r —, 1 leks. (+4) |
| `lata` | 5 | Lata:Sf: r —, 1 leks.; Lata:Sm1: r —, 1 leks.; latać: r 3 885, 1 leks., POP (+2) | Lata:Sf: r 22 733, 1 leks., POP; Lata:Sm1: r 22 807, 1 leks., POP; latać: r 2 607, 1 leks., POP (+2) | Lata:Sf: r —, 1 leks.; Lata:Sm1: r —, 1 leks.; latać: r 3 168, 1 leks., POP (+2) | Lata:Sf: r 20, 14 leks., POP; Lata:Sm1: r 20, 14 leks., POP; latać: r 20, 14 leks., POP (+2) | Lata:Sf: r 18, 13 leks., POP; Lata:Sm1: r 18, 13 leks., POP; latać: r 18, 13 leks., POP (+2) | Lata:Sf: r —, 1 leks.; Lata:Sm1: r —, 1 leks.; latać: r 3 193, 2 leks., POP (+2) |
| `lato` | 5 | Lata:Sf: r —, 1 leks.; Lata:Sm1: r —, 1 leks.; Lato:Sf: r —, 1 leks. (+2) | Lata:Sf: r 22 733, 1 leks., POP; Lata:Sm1: r 22 807, 1 leks., POP; Lato:Sf: r 15 387, 1 leks., POP (+2) | Lata:Sf: r —, 1 leks.; Lata:Sm1: r —, 1 leks.; Lato:Sf: r —, 1 leks. (+2) | Lata:Sf: r 20, 14 leks., POP; Lata:Sm1: r 20, 14 leks., POP; Lato:Sf: r 20, 14 leks., POP (+2) | Lata:Sf: r 18, 13 leks., POP; Lata:Sm1: r 18, 13 leks., POP; Lato:Sf: r 18, 13 leks., POP (+2) | Lata:Sf: r —, 1 leks.; Lata:Sm1: r —, 1 leks.; Lato:Sf: r —, 1 leks. (+2) |
| `polska` | 3 | Polska:Sf~ej: r —, 1 leks.; Polska:Sf~i: r —, 1 leks.; polski:A: r 81, 1 leks., POP | Polska:Sf~ej: r 104, 1 leks., POP; Polska:Sf~i: r 96, 1 leks., POP; polski:A: r 69, 1 leks., POP | Polska:Sf~ej: r —, 1 leks.; Polska:Sf~i: r 70, 1 leks., POP; polski:A: r 1 324, 1 leks., POP | Polska:Sf~ej: r 33, 7 leks., POP; Polska:Sf~i: r 33, 7 leks., POP; polski:A: r 33, 7 leks., POP | Polska:Sf~ej: r 30, 7 leks., POP; Polska:Sf~i: r 30, 7 leks., POP; polski:A: r 30, 7 leks., POP | Polska:Sf~ej: r —, 1 leks.; Polska:Sf~i: r 115, 1 leks., POP; polski:A: r 1 477, 1 leks., POP |
| `polski` | 4 | Polska:Sf~i: r —, 1 leks.; Polski: r 41 587, 1 leks.; polski:A: r 81, 1 leks., POP (+1) | Polska:Sf~i: r 96, 1 leks., POP; Polski: r 24 619, 1 leks., POP; polski:A: r 69, 1 leks., POP (+1) | Polska:Sf~i: r 70, 1 leks., POP; Polski: r 42 035, 1 leks.; polski:A: r 1 324, 1 leks., POP (+1) | Polska:Sf~i: r 33, 7 leks., POP; Polski: r 33, 7 leks., POP; polski:A: r 33, 7 leks., POP (+1) | Polska:Sf~i: r 30, 7 leks., POP; Polski: r 30, 7 leks., POP; polski:A: r 30, 7 leks., POP (+1) | Polska:Sf~i: r 115, 1 leks., POP; Polski: r 38 732, 1 leks.; polski:A: r 1 477, 1 leks., POP (+1) |
| `zamek` | 3 | Zamek: r 45 956, 1 leks.; zamek:Sm3~a: r —, 1 leks.; zamek:Sm3~u: r —, 1 leks. | Zamek: r 27 996, 1 leks., POP; zamek:Sm3~a: r 2 381, 1 leks., POP; zamek:Sm3~u: r 2 414, 1 leks., POP | Zamek: r 46 703, 1 leks.; zamek:Sm3~a: r 10 420, 1 leks., POP; zamek:Sm3~u: r —, 1 leks. | Zamek: r 1 483, 4 leks., POP; zamek:Sm3~a: r 1 483, 4 leks., POP; zamek:Sm3~u: r 1 483, 4 leks., POP | Zamek: r 1 484, 4 leks., POP; zamek:Sm3~a: r 1 484, 4 leks., POP; zamek:Sm3~u: r 1 484, 4 leks., POP | Zamek: r 43 050, 1 leks.; zamek:Sm3~a: r 6 229, 2 leks., POP; zamek:Sm3~u: r 6 229, 2 leks., POP |

Top 50 wierszy AMBIGUOUS KWJP wg F i ich los (ranga jednostki pierwszego członka):

| lemat KWJP | F | kandydaci | a | b | c | d | e-literal | e-common |
|---|---|---|---|---|---|---|---|---|
| `rok` | 315 221 | 2 | r —, 1 leks. | r 25, 1 leks., POP | r —, 1 leks. | r 20, 14 leks., POP | r 18, 13 leks., POP | r 25, 2 leks., POP |
| `raz` | 124 639 | 2 | r —, 1 leks. | r 60, 1 leks., POP | r 15 582, 1 leks., POP | r 50, 4 leks., POP | r 46, 4 leks., POP | r 42, 4 leks., POP |
| `dzień` | 110 040 | 2 | r —, 1 leks. | r 265, 1 leks., POP | r —, 1 leks. | r 59, 17 leks., POP | r 58, 11 leks., POP | r 55, 6 leks., POP |
| `Polska` | 89 502 | 2 | r —, 1 leks. | r 104, 1 leks., POP | r —, 1 leks. | r 33, 7 leks., POP | r 30, 7 leks., POP | r —, 1 leks. |
| `stać` | 81 179 | 2 | r —, 1 leks. | r 99, 1 leks., POP | r 1 218, 1 leks., POP | r 31, 50 leks., POP | r 28, 46 leks., POP | r 59, 12 leks., POP |
| `wiele` | 80 820 | 2 | r —, 1 leks. | r 112, 1 leks., POP | r 2 446, 1 leks., POP | r 89, 11 leks., POP | r 84, 11 leks., POP | r 1 426, 2 leks., POP |
| `oko` | 61 242 | 2 | r —, 1 leks. | r 235, 1 leks., POP | r 1 148, 1 leks., POP | r 145, 12 leks., POP | r 140, 12 leks., POP | r 474, 2 leks., POP |
| `ktoś` | 55 549 | 2 | r —, 1 leks. | r 202, 1 leks., POP | r 315, 1 leks., POP | r 144, 2 leks., POP | r 141, 2 leks., POP | r 120, 2 leks., POP |
| `państwo` | 49 902 | 2 | r —, 1 leks. | r 198, 1 leks., POP | r —, 1 leks. | r 136, 2 leks., POP | r 133, 2 leks., POP | r 117, 2 leks., POP |
| `należeć` | 42 944 | 2 | r —, 1 leks. | r 181, 1 leks., POP | r 11 577, 1 leks., POP | r 138, 7 leks., POP | r 135, 7 leks., POP | r 123, 7 leks., POP |
| `przypadek` | 41 326 | 2 | r —, 1 leks. | r 231, 1 leks., POP | r 64 445, 1 leks. | r 157, 4 leks., POP | r 153, 4 leks., POP | r 136, 4 leks., POP |
| `Warszawa` | 34 641 | 2 | — | — | — | — | — | — |
| `powód` | 31 818 | 2 | r —, 1 leks. | r 643, 1 leks., POP | r 4 556, 1 leks., POP | r 205, 9 leks., POP | r 204, 9 leks., POP | r 180, 7 leks., POP |
| `rząd` | 31 671 | 2 | r —, 1 leks. | r 285, 1 leks., POP | r 359, 1 leks., POP | r 192, 10 leks., POP | r 191, 10 leks., POP | r 328, 4 leks., POP |
| `prezydent` | 28 703 | 2 | r —, 1 leks. | r 729, 1 leks., POP | r —, 1 leks. | r 291, 2 leks., POP | r 293, 2 leks., POP | r 254, 2 leks., POP |
| `co` | 28 403 | 2 | r —, 1 leks. | r 191, 1 leks., POP | r —, 1 leks. | r 15, 10 leks., POP | r 13, 10 leks., POP | r 12, 10 leks., POP |
| `Polak` | 26 337 | 3 | r —, 1 leks. | r 2 225, 1 leks., POP | r —, 1 leks. | r 361, 5 leks., POP | r 363, 5 leks., POP | r —, 1 leks. |
| `tysiąc` | 24 911 | 2 | r —, 1 leks. | r 404, 1 leks., POP | r —, 1 leks. | r 321, 7 leks., POP | r 322, 7 leks., POP | r 370, 2 leks., POP |
| `ile` | 24 586 | 2 | r —, 1 leks. | r 430, 1 leks., POP | r 2 065, 1 leks., POP | r 331, 10 leks., POP | r 331, 10 leks., POP | r 292, 5 leks., POP |
| `dostać` | 24 373 | 2 | r —, 1 leks. | r 492, 1 leks., POP | r 1 590, 1 leks., POP | r 365, 3 leks., POP | r 365, 3 leks., POP | r 316, 3 leks., POP |
| `stawać` | 21 831 | 2 | r —, 1 leks. | r 632, 1 leks., POP | r 3 783, 1 leks., POP | r 346, 22 leks., POP | r 348, 22 leks., POP | r 403, 9 leks., POP |
| `Jan` | 21 569 | 2 | — | — | — | r 278, 27 leks., POP | — | — |
| `tyle` | 20 826 | 2 | r —, 1 leks. | r 434, 1 leks., POP | r 14 610, 1 leks., POP | r 188, 20 leks., POP | r 185, 19 leks., POP | r 7 305, 2 leks., POP |
| `minister` | 19 707 | 2 | r —, 1 leks. | r 612, 1 leks., POP | r —, 1 leks. | r 337, 4 leks., POP | r 338, 4 leks., POP | r 303, 4 leks., POP |
| `prezes` | 18 463 | 2 | r —, 1 leks. | r 663, 1 leks., POP | r —, 1 leks. | r 422, 4 leks., POP | r 422, 4 leks., POP | r 366, 4 leks., POP |
| `członek` | 18 435 | 3 | r —, 1 leks. | r 506, 1 leks., POP | r —, 1 leks. | r 433, 5 leks., POP | r 436, 5 leks., POP | r 1 052, 3 leks., POP |
| `dyrektor` | 17 717 | 2 | r —, 1 leks. | r 712, 1 leks., POP | r —, 1 leks. | r 448, 4 leks., POP | r 451, 4 leks., POP | r 398, 4 leks., POP |
| `wolny` | 16 858 | 2 | r —, 1 leks. | r 598, 1 leks., POP | r 76 697, 1 leks. | r 319, 13 leks., POP | r 321, 13 leks., POP | r 551, 7 leks., POP |
| `pies` | 16 496 | 2 | r —, 1 leks. | r 1 015, 1 leks., POP | r 60 113, 1 leks. | r 670, 7 leks., POP | r 668, 7 leks., POP | r 587, 6 leks., POP |
| `Piotr` | 16 134 | 2 | — | — | — | r 554, 9 leks., POP | — | — |
| `pozwalać` | 15 055 | 2 | r —, 1 leks. | r 714, 1 leks., POP | r 2 398, 1 leks., POP | r 539, 2 leks., POP | r 540, 2 leks., POP | r 482, 2 leks., POP |
| `kupić` | 14 772 | 2 | r —, 1 leks. | r 860, 1 leks., POP | r 67 805, 1 leks. | r 557, 9 leks., POP | r 556, 9 leks., POP | r 561, 3 leks., POP |
| `wychodzić` | 14 693 | 2 | r —, 1 leks. | r 931, 1 leks., POP | r 3 739, 1 leks., POP | r 681, 6 leks., POP | r 679, 6 leks., POP | r 593, 6 leks., POP |
| `typ` | 14 327 | 2 | r —, 1 leks. | r 1 675, 1 leks., POP | r —, 1 leks. | r 440, 6 leks., POP | r 440, 6 leks., POP | r 423, 4 leks., POP |
| `pozostawać` | 14 005 | 2 | r —, 1 leks. | r 899, 1 leks., POP | r 4 224, 1 leks., POP | r 673, 2 leks., POP | r 671, 2 leks., POP | r 594, 2 leks., POP |
| `przestać` | 13 749 | 2 | r —, 1 leks. | r 1 181, 1 leks., POP | r 5 693, 1 leks., POP | r 832, 4 leks., POP | r 830, 4 leks., POP | r 729, 4 leks., POP |
| `klient` | 13 656 | 2 | r —, 1 leks. | r 713, 1 leks., POP | r 1 234, 1 leks., POP | r 592, 2 leks., POP | r 591, 2 leks., POP | r 539, 2 leks., POP |
| `model` | 12 092 | 2 | r —, 1 leks. | r 1 299, 1 leks., POP | r —, 1 leks. | r 910, 5 leks., POP | r 909, 5 leks., POP | r 993, 2 leks., POP |
| `czerwiec` | 11 994 | 2 | r —, 1 leks. | r 1 000, 1 leks., POP | r —, 1 leks. | r 750, 5 leks., POP | r 751, 5 leks., POP | r 1 003, 2 leks., POP |
| `posiadać` | 11 837 | 2 | r —, 1 leks. | r 701, 1 leks., POP | r 2 727, 1 leks., POP | r 535, 8 leks., POP | r 536, 8 leks., POP | r 490, 5 leks., POP |
| `Adam` | 11 800 | 2 | — | — | — | r 791, 8 leks., POP | — | — |
| `Marek` | 11 737 | 2 | r —, 1 leks. | r 1 019, 1 leks., POP | r —, 1 leks. | r 218, 19 leks., POP | r 215, 19 leks., POP | r —, 1 leks. |
| `profesor` | 11 674 | 2 | r —, 1 leks. | r 1 757, 1 leks., POP | r —, 1 leks. | r 917, 2 leks., POP | r 913, 2 leks., POP | r 816, 2 leks., POP |
| `metr` | 11 641 | 3 | r —, 1 leks. | r 1 239, 1 leks., POP | r 80 801, 1 leks. | r 807, 7 leks., POP | r 806, 7 leks., POP | r 702, 7 leks., POP |
| `premier` | 10 929 | 2 | r —, 1 leks. | r 1 597, 1 leks., POP | r —, 1 leks. | r 627, 5 leks., POP | r 628, 5 leks., POP | r 563, 5 leks., POP |
| `sen` | 10 782 | 2 | r —, 1 leks. | r 2 699, 1 leks., POP | r —, 1 leks. | r 737, 22 leks., POP | r 737, 18 leks., POP | r 922, 9 leks., POP |
| `Krzysztof` | 10 602 | 2 | — | — | — | — | — | — |
| `Tomasz` | 10 557 | 2 | — | — | — | r 833, 6 leks., POP | — | — |
| `dochodzić` | 10 020 | 2 | r —, 1 leks. | r 1 245, 1 leks., POP | r 8 075, 1 leks., POP | r 878, 5 leks., POP | r 874, 5 leks., POP | r 778, 5 leks., POP |
| `Jerzy` | 9 847 | 2 | — | — | — | r 743, 8 leks., POP | — | — |

**Zalecenie D5:** `e-common` — grupa homonimów bez nazw własnych. Nie kopiuje F, przypisuje 72,6% masy NKJP (c: 45,3%), a największa grupa ma 22 leksemów (d: 112).

## D6 — progi POP i POP0

| próg | leksemy | jednostki | ranga graniczna | formy | pokrycie kwjp-all | kwjp-exact | kwjp-standard |
|---|---|---|---|---|---|---|---|
| 5 000 leksemów | 5 000 | 2 191 | 2 191 | 99 181 | 72,0% | 74,7% | 78,9% |
| 10 000 leksemów | 9 999 | 5 026 | 5 026 | 215 040 | 80,5% | 83,5% | 88,2% |
| 20 000 leksemów | 20 000 | 11 644 | 11 644 | 454 198 | 86,4% | 89,6% | 94,7% |
| 40 000 leksemów | 40 000 | 27 498 | 27 498 | 902 062 | 89,8% | 93,0% | 98,3% |
| 80 000 leksemów | 80 000 | 64 077 | 64 077 | 1 664 269 | 90,6% | 93,9% | 99,2% |
| pokrycie 80% (kwjp-standard) | 5 378 | 2 388 | 2 388 | 107 802 | 73,0% | 75,7% | 80,0% |
| pokrycie 90% (kwjp-standard) | 11 842 | 6 150 | 6 150 | 258 998 | 82,1% | 85,2% | 90,0% |
| pokrycie 95% (kwjp-standard) | 20 809 | 12 226 | 12 226 | 473 956 | 86,7% | 89,9% | 95,0% |
| pokrycie 98% (kwjp-standard) | 36 885 | 24 847 | 24 847 | 839 060 | 89,5% | 92,7% | 98,0% |

**Zalecenie D6:** wstępnie POP = 40 000 leksemów (98,3% kwjp-standard), POP0 = 5 000 (78,9%). Ostatecznie po ocenie próbek granicznych.

## D7 — luka potoczna (A6)

Leksemy potoczne z formą w STANDARD: 2 410. Mediana różnicy percentyli NKJP − KWJP: potoczne 19,90 (n = 1 145), pozostałe 18,07 (n = 45 371).

| próg | potoczne w POP | potoczne poza |
|---|---|---|
| 5 000 leksemów | 40 | 2 370 |
| 10 000 leksemów | 73 | 2 337 |
| 20 000 leksemów | 181 | 2 229 |
| 40 000 leksemów | 597 | 1 813 |
| 80 000 leksemów | 1 671 | 739 |

Potoczne poza POP bazowym, wg rangi NKJP (ilustracja):

| jednostka | ranga NKJP | ranga KWJP | ranga bazowa |
|---|---|---|---|
| Francuz:Sm1~i+francuz:Sm1+francuz:Sm2+francuz:Sm2.m3 | 4 355 | 41 076 | 28 223 |
| trefl+treflowy | 9 938 | 44 502 | 33 942 |
| rand+random | 16 348 | 45 511 | 38 781 |
| admin | 16 757 | 39 178 | 33 024 |
| desktop | 17 438 | 46 074 | 40 041 |
| gimbus:Sm1+gimbus:Sm2.m3 | 18 180 | 34 536 | 29 852 |
| ping | 18 884 | 40 799 | 35 652 |
| emka | 19 231 | 46 130 | 41 251 |
| forumowicz | 19 605 | 32 191 | 28 671 |
| papcio+papeć | 20 104 | 37 730 | 33 561 |
| draft | 20 211 | 32 479 | 29 210 |
| manatki | 20 877 | 31 129 | 28 455 |
| pudłować | 20 981 | 31 470 | 28 777 |
| pokurcz:Sm1+pokurcz:Sm2+pokurcze+pokurczyć | 22 390 | 29 093 | 27 633 |
| wsio | 22 475 | 39 056 | 36 110 |

**Zalecenie D7:** przyjąć lukę w `pop-v1` i opisać ją w LIMITATIONS; dodatki potoczne to osobne zadanie.

## D8 — braki danych

Brak pełny (bez KWJP i NKJP): 128 504 jednostek. Statusy KWJP/NKJP (§8.2):

| KWJP / NKJP | jednostki |
|---|---|
| ABSENT_OR_BELOW_PUBLICATION_THRESHOLD/NOT_IN_PUBLISHED_LIST | 107 072 |
| ABSENT_OR_BELOW_PUBLICATION_THRESHOLD/OBSERVED | 37 440 |
| ABSENT_OR_BELOW_PUBLICATION_THRESHOLD/UNMATCHED | 15 126 |
| OBSERVED/NOT_IN_PUBLISHED_LIST | 314 |
| OBSERVED/OBSERVED | 46 516 |
| OBSERVED/UNMATCHED | 5 997 |
| UNMATCHED/NOT_IN_PUBLISHED_LIST | 14 |
| UNMATCHED/OBSERVED | 1 007 |
| UNMATCHED/UNMATCHED | 6 292 |

| brak częściowy | leksemy | formy | pokrycie kwjp-all | kwjp-exact | kwjp-standard | braki częściowe | POP Jaccard vs available-only |
|---|---|---|---|---|---|---|---|
| available-only | 40 000 | 902 062 | 89,8% | 93,0% | 98,3% | 44 758 | 100,0% |
| lower-bound | 40 000 | 940 145 | 82,0% | 85,3% | 89,9% | 44 758 | 83,5% |
| exclude | 40 000 | 940 145 | 82,0% | 85,3% | 89,9% | 44 758 | 83,5% |

**Zalecenie D8:** brak pełny poza listą; brak częściowy `available-only` (percentyl dostępnego źródła, z flagą). Wrażliwość pokazuje kolumna Jaccard.

## A9 — formy konstrukcji i czas reguł

Formy STANDARD tylko z konstrukcji: 85 351. Jeden leksem składnika: 83 586, żaden: 0, kilka: 1 765.

- kilka (ilustracja): `bluźnijcież`, `bluźnijmyż`, `bluźnijże`, `bodźcież`, `bodźmyż`, `bodźże`, `breszcież`, `breszmyż`, `breszże`, `brzęczcież`

Czas reguły (i): 10,5 s. Czas reguły (ii): 907,3 s.

| reguła | leksemy | pary leksem–forma | tylko w tej regule |
|---|---|---|---|
| (i) | 236 595 | 3 276 831 | 164 409 |
| (ii) | 210 405 | 3 112 422 | 0 |

Pozostałe etapy: constructions 7,7 s, d1 0,4 s, d2 4,0 s, d3 10,6 s, d6 2,3 s, d7 1,0 s, d8 4,7 s, form_classes 24,1 s, form_owners 10,9 s, kwjp 5,7 s, kwjp_measures 1,6 s, lexemes 11,8 s, membership_i 10,5 s, membership_ii 907,3 s, nkjp_full-nfc 5,7 s, nkjp_strip-edges 10,5 s, nkjp_strip-edges-keep-dot 10,8 s, samples 3,2 s, standard 0,8 s, units_a 5,8 s, units_b 6,2 s, units_c 5,8 s, units_d 5,7 s, units_e-common 5,8 s, units_e-literal 5,6 s.

## Próbki (A7)

`pop-quality-v1`, seed `literaki-slownik-pop-v1`, 30 na warstwę, status `UNREVIEWED`. Ocena wstępna agenta: grupa 7.

| warstwa | populacja | próbka |
|---|---|---|
| braki-danych | 175 256 | 30 |
| formy-dlugie | 371 351 | 30 |
| formy-krotkie | 1 100 | 30 |
| grupy-homonimow | 28 194 | 30 |
| pop-granica-wewnatrz | 589 | 30 |
| pop-granica-zewnatrz | 589 | 30 |
| pop0-granica-wewnatrz | 924 | 30 |
| pop0-granica-zewnatrz | 950 | 30 |
| pos-adj | 8 951 | 30 |
| pos-adv | 3 086 | 30 |
| pos-other | 670 | 30 |
| pos-subst | 18 217 | 30 |
| pos-verb | 9 076 | 30 |
| rozbieznosc-kwjp-nkjp | 1 967 | 30 |

- `braki-danych`: `wykłośność`, `kahalny`, `społecznikarski`, `kresowiacki`, `Mącze`, `cytomegalowirus`, `klister`, `egzempt`, `czortowskość`, `togijski`, `dannicko`, `liścisko`, `niegórnolotność`, `niebiofilność`, `niekantabryjsko`, `entomogamia`, `oprzyrządowywać`, `samowzmocnienie`, `niesynogarliczy`, `Ławice`, `Swatek:Sf`, `niekordobański`, `niewolframowość`, `nieokrutność`, `Drapińska`, `budapeszteńsko`, `penetrometr`, `biokatalizator`, `Żarowska`, `Płotka:Sf`
- `formy-dlugie`: `dorzucałyśmy`, `niewynalezionym`, `niezgrubianych`, `dyskredytować`, `niezakatrupień`, `uszczypliwość`, `niegnuśnieniach`, `zagnieździwszy`, `finansujecie`, `przetestował`, `niezaparkowania`, `niezamazywanemu`, `amputowałbym`, `chuliganiącemu`, `prześwitując`, `pozytywniałby`, `deprawowaniu`, `niefrasobliwość`, `zatroszczyłaby`, `zwiększeniami`, `niedyktowanie`, `nieupłynnionym`, `zaprzysięgnijmy`, `konkurowałoś`, `złowieszczemu`, `nieścierającej`, `łzawilibyśmy`, `nielansowana`, `wpatrzałyście`, `potraktowałobyś`
- `formy-krotkie`: `pup`, `sil`, `bit`, `elf`, `rżę`, `dym`, `suń`, `nam`, `pun`, `jar`, `ulg`, `acz`, `juk`, `dną`, `wie`, `luk`, `ani`, `lad`, `baź`, `cer`, `kią`, `hak`, `nań`, `as`, `ze`, `bań`, `ról`, `nys`, `par`, `ryś`
- `grupy-homonimow`: `stoczyć`, `zniczowy`, `ocierniony`, `spryciula:Sf`, `złościć`, `zblazowanie`, `spożyć`, `wyrypać`, `cesarstwo:Sn_ncol`, `gromowy`, `roztleć`, `wślizgać:Vi`, `przyciszyć`, `bruzdkowanie`, `rozwojowo`, `garnizonowy:A`, `niezasłużenie`, `znękany`, `pigularz`, `dławisz`, `zmylić`, `równouprawnienie`, `kawał:Sm3~u`, `zaniedbany`, `jaja`, `kwaterunkowy`, `zjędrnić`, `szampańskie`, `pozajelitowy`, `smok:Sm3`
- `pop-granica-wewnatrz`: `międzywale`, `sianowski`, `konspiracyjnie`, `odźwiernia`, `konkretyzować`, `adwentystyczny`, `rozbawiać`, `kastowy`, `skalar:Sm3`, `wyczołgać`, `rozpłaszczyć`, `sygnet`, `alzacki`, `naszczekiwać`, `podnóżek:Sm1`, `zwiadowczy`, `antycypacja`, `inseminacja`, `spedycja`, `jon`, `filomata`, `Bednarski`, `mieszek`, `rozgonić`, `cielisty`, `chrypka`, `tinta`, `demaskacja`, `trumienka`, `błogostan`
- `pop-granica-zewnatrz`: `zlinczować`, `tent`, `chartumski`, `kardamon`, `zaczerniać`, `superman`, `rozzuchwalić`, `słowiańszczyzna`, `niesolidność`, `zapowietrzony`, `pręcik`, `aprecjacja`, `rowerzystka`, `inkorporacja`, `zdemobilizować`, `zalękniony`, `Konda`, `rozmarzać`, `dekolonizacja`, `kpiarski`, `endemiczny`, `harcować`, `łapówkarstwo`, `wdeptać`, `runa`, `zaczernić`, `Nawarra`, `Wlazły:Sm1`, `medycznie`, `matematyczka`
- `pop0-granica-wewnatrz`: `maszyna`, `dysponowany`, `ukończyć`, `infrastruktura`, `medalowy`, `oddechowy`, `objawowy`, `odezwać`, `urlopowo`, `unikat:Sm1`, `chęć`, `boisko`, `rozwinięty`, `mijać`, `pomnik`, `malowanie`, `umierać`, `magazyn`, `klasyczny`, `Chrystus`, `przyjemny`, `posługiwać`, `wyłączenie`, `postrzegać`, `obchodzić`, `użytek`, `mieszkaniowy`, `zrealizowanie`, `głąb:Sm2.m3`, `stolikowy`
- `pop0-granica-zewnatrz`: `energetyczny`, `regulowanie`, `osłabiały`, `nieprotestujący`, `zaliczyć`, `eksportowo`, `turystyczny`, `pościelić`, `przewodnik:Sm2`, `pensja`, `przewodnik:Sm1`, `oszczędności`, `ryba`, `zakochany:S`, `domyślać`, `odmiennie`, `dziesiątkowy`, `operacyjny`, `wymożenie`, `psychiczna`, `lekarsko`, `Mikołaj`, `rozegrany`, `przełom`, `przypuszczać`, `pośrednictwo`, `obrazić`, `zasiąg`, `wada`, `siódmy:S`
- `pos-adj`: `groźny`, `niewart`, `moralizatorski`, `znużony`, `życiowy`, `bankowy`, `prostolinijny`, `ekstatyczny`, `trzeci:A`, `luby:A`, `opatrunkowy`, `zakryty`, `milicyjny`, `serowy`, `niski`, `interpersonalny`, `iloczynowy`, `nowosądecki`, `strzelający:A`, `żołnierski`, `wielkoduszny`, `połamany`, `kaloryczny`, `płciowy`, `pracujący:A`, `prawny`, `bliskowschodni`, `poglądowy`, `rozwijalny`, `wieczorowy`
- `pos-adv`: `niewygodno`, `umiejętnie`, `bystro`, `śmierdząco`, `stylistycznie`, `urągająco`, `niebezpieczno`, `solidarnie`, `pękato`, `ślepo`, `narodowościowo`, `tym:D`, `diametralnie`, `łudząco`, `fiołkowo`, `grzecznie`, `małostkowo`, `nierozerwanie`, `krwawie`, `lwio`, `miałko`, `asortymentowo`, `wybaczająco`, `podle:D`, `niegdyś`, `osobniczo`, `poprzednio`, `naprzeciwko:D`, `jednogłośnie`, `kołysząco`
- `pos-other`: `żeby:M`, `jednakże:C`, `prócz`, `odnośnie`, `cztery`, `otóż`, `la:P`, `hop:I`, `kilkadziesiąt`, `pełno:N`, `czuć:V`, `generał`, `gdyby:M`, `porucznik`, `znowu`, `wśród`, `mniej`, `odpierdol`, `tak:T`, `abo:T`, `ha:I`, `trzysta`, `bądź:C`, `osiemnaście`, `ni:C`, `dalibóg:T`, `zza`, `zaprawdę`, `naokół:P`, `alias:C`
- `pos-subst`: `stawiennictwo`, `Jankes`, `wynalezienie`, `uciążliwość`, `oświetlenie`, `najdroższy`, `kondolencja`, `przesłuchanie`, `mig:Sm3`, `rzemieślnik`, `targan`, `bachor`, `przejażdżka`, `arbuz`, `musza`, `kibel`, `golf:Sm3~a~u`, `posługa`, `kupka`, `pula`, `potępiona`, `dobroczynność`, `ceregiele`, `zuchwałość`, `laurka`, `powinowata`, `nadczłowiek`, `wyrost`, `pracujący:S`, `legitymacja`
- `pos-verb`: `odpowiedzieć`, `zatroszczyć`, `wytłoczyć`, `uwielbić`, `biedzić`, `utwardzić`, `zaczadzić`, `niwelować`, `podzwaniać`, `ucywilizować`, `umocnić`, `obyć`, `spacyfikować`, `zarwać`, `transportować`, `zgrzać`, `dźwignąć`, `elektryzować`, `zamruczeć`, `aranżować`, `nachodzić:Vp`, `rozsądzić`, `opóźnić`, `wpierdolić`, `odczekać`, `zalegalizować`, `przybierać`, `zbutwieć`, `opatrzyć`, `nadjeżdżać`
- `rozbieznosc-kwjp-nkjp`: `hakować`, `rozhukać`, `motolotnia`, `numerolog`, `wólczański`, `koagulacja`, `nok`, `muszkatela`, `Pan`, `cham`, `sunna`, `narzędziowy`, `migdał`, `maleńki`, `babiogórski`, `tuberoza`, `teina`, `czyliż`, `kapciuszek`, `fazowy`, `jang`, `mazowiecko`, `stargać`, `oprotestowywać`, `konosament`, `posłuszny`, `strążysko:S`, `nałapać`, `gabinecik`, `rozkolportować`

## Dodatek (2026-10-11): progi po ocenie próbek i decyzje

Ocena wstępna agenta (krok 7.4), próbki graniczne przy POP 40k / POP0 5k:
- za granicą POP0 są słowa bardzo znane (`ryba`, `pensja`, `wada`, `turystyczny`): 5 000 leksemów to tylko 2 191 jednostek;
- za granicą POP też znane (`kardamon`, `rowerzystka`, `matematyczka`, `pręcik`, `zlinczować`);
- nazwy własne (`Bednarski`, `Mikołaj`, `Nawarra`) zajmują miejsca w rankingu.

Właściciel: „podnieść oba limity; POP mocno, POP0 trochę; decyzje podejmij sam” (2026-10-11).

Sonda progów bez nazw własnych w rankingu (`e-common`, bazowe D1–D4, D8; scratchpad `probe_thresholds.py`):

| próg (leksemy) | jednostki | formy | pokrycie kwjp-standard | tuż za granicą (ilustracja) |
|---|---:|---:|---:|---|
| 10 000 | 5 008 | 215 618 | 88,0% | benzyna, bagażnik, biodro, ramka, rezerwa |
| 15 000 | 8 160 | 336 496 | 92,1% | wiza, młyn, ginekolog, lenistwo, bańka |
| 40 000 | 27 369 | 916 244 | 97,9% | gimnastyczka, paralotnia, halogen, biosfera, bat |
| 60 000 | 45 229 | 1 328 263 | 98,5% | tomahawk, psinka, podjarać, shaker, mikrokomputer |
| 80 000 | 63 905 | 1 719 657 | 98,6% | wewnątrz już: ruptura, dejman, dragować, dudarz |

Rangi jednostek (bez nazw własnych): dom 76, pies 581, fajny 1 985, ryba 2 443, pensja 2 558, kot 9 128, spoko 9 912, kardamon 26 901.

Decyzje (agent z upoważnienia właściciela, odwracalne; zapis w ADR-007):
- D1 `kwjp-standard`, w raportach też `kwjp-all`.
- D2 pełna odmiana, konstrukcje tak, reguła (i). Zmiana wobec „typowych form”: wykluczenia klas tną formy znane z tekstu (bez czterech klas −45% form), a słownik stołu wymaga pełnej odmiany (§2.2).
- D3 KWJP+NKJP z percentyli, F, waga 0,5; sama KWJP jako ścieżka wycofania.
- D4 `strip-edges-keep-dot`.
- D5 `e-common`.
- D6 POP = 60 000 leksemów, POP0 = 20 000 (`kot` musi być w POP0).
- D7 luka potoczna przyjęta, opis w LIMITATIONS.
- D8 brak pełny poza listą; częściowy `available-only`.
- D9 (nowa) nazwy własne nie biorą udziału w rankingu; ich formy wchodzą tylko przez zwykłe leksemy.
