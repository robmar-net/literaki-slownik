# ADR-008: Metoda `pop-v3` — stałe progi punktacji POP i POP0

**Status:** zaakceptowana 2026-10-12 (decyzja właściciela, tymczasowa). Częściowo zastępuje [ADR-007](ADR-007-metoda-pop-v1.md): zmienia tylko D6 i porównanie w D5 dla POP i POP0.
Docelowe granice POP i POP0: [#6](https://github.com/robmar-net/literaki-slownik/issues/6).

## Kontekst
W `pop-v2` POP to 60 000 leksemów jednostek przed przycięciem. Gdy STANDARD rośnie, nowe słowa zajmują miejsca:
dodatki z #4 wypchnęłyby 2 430 form POP o niezmienionych dowodach.
Badanie: [kalibracja POP](../../.maister/tasks/development/2026-10-12-stabilizacja-progu-pop/analysis/research-context/pop-calibration.md).
Stały próg dzisiejszego cięcia odtwarza bazowy POP (1 227 250 form) i po dodatkach daje +2 372/0.
POP0 ma ten sam problem (2026-10-13): na nowym STANDARD (#4/#5) POP0 ma dokładnie 20 000 leksemów przed
przycięciem, bez zapasu; jeden leksem więcej wyrzuciłby cały blok remisu. Właściciel: 20 000 to przypadkowy
próg, POP0 dostaje tę samą korektę od razu (zmiana niewydanego `pop-v3`, bez nowej wersji).

## Decyzje
D1–D5, D7–D9 jak w ADR-007 (rew. 4). Zmiany:

**D6. POP: punktacja ≥ −1,042878629; POP0: punktacja ≥ 0,57370099.**
Lista bierze każdą jednostkę rankingu z miarą D3 (średnia log-ipm) nie mniejszą od swojego progu, z remisem
na granicy. Jednostka bez miary nie wchodzi. Liczba leksemów jest wynikiem, nie limitem.
Wartości to miary ostatnich jednostek cięć `pop-v2` (60 000 i 20 000 leksemów) na wydanych wejściach
(`pop-sources-v29.json`, `pop-v2.json`), w pełnej precyzji miary (9 miejsc po przecinku): zamrożone stałe,
nie granice znajomości słów. Na granicy POP0 nie ma remisu: ostatnia jednostka ma punktację sama, następny blok
(8 jednostek, 10 leksemów) ma 0,573686024.

**D5: własna punktacja zamiast własnej rangi.** Członek grupy zostaje na liście, gdy własna miara ≥ próg tej
listy. Wyjątki bez zmian: najmocniejszy członek (największa własna miara), grupa bez rozdzielnych dowodów,
warianty jednego lematu razem.

**POP0 ⊆ POP.** Konfiguracja wymaga progu POP0 ≥ progu POP (inaczej kod 2), więc jednostki i członkowie POP0
są w POP. Budowa sprawdza to także jawnie; naruszenie (jednostki albo leksemy) = kod 4.

Konfiguracja: [`config/generator/pop.json`](../../config/generator/pop.json) (`pop-v3`).
`pop-v2` zostaje odtwarzalne: [`config/generator/pop-v2.json`](../../config/generator/pop-v2.json) to bajtowa kopia
konfiguracji wydanego pakietu (SHA256 `affcfab8…9a60`). Walidacja wymaga pary rodzajów progu danej wersji
(`pop-v2`: liczba/liczba, `pop-v3`: punktacja/punktacja) i skończonej liczby.

Raporty: `thresholds.json` podaje `by`, `score` albo `limit`, ostatnią rangę, jednostki, leksemy, pokrycie
i `provisional` (link do #6) dla obu list. Pakiet nie podaje miar jednostek (C14); członek grupy ma tylko
`member_meets_score` (lista → tak/nie). `explain --variant pop|pop0` pokazuje próg punktacji listy.

Odrzucone: limit 60 025 (dopasowanie do jednej paczki); limit 70/80 tys. (przesuwa konkurencję o miejsca);
progi 0,075/0,05/0,025 (poszerzają POP bez kalibracji; decyzja w #6).

## Ograniczenia
- Stałe są w skali D3 (KWJP+NKJP log-ipm, waga 0,5). Wycofanie NKJP (ADR-006) zmienia skalę: wymaga nowej stałej
  i nowej wersji metody; `pop-v3` przyjmuje tylko tę D3.
- Stałe nie gwarantują braku ubytków przy zmianie źródeł, mapowania lub grup.
- Wyjątki grupowe zostają; nie każdy leksem ma własny mocny dowód.
- Wartości pochodzą z historycznych cięć, nie z oceny ludzi.

## Rewizja
Nowe granice POP i POP0 ustala #6. Zmiana progu to nowa wersja metody i nowy ADR.
