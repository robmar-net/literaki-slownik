# ADR-008: Metoda `pop-v3` — stały próg punktacji POP

**Status:** zaakceptowana 2026-10-12 (decyzja właściciela, tymczasowa). Częściowo zastępuje [ADR-007](ADR-007-metoda-pop-v1.md): zmienia tylko D6 dla POP i porównanie w D5 dla POP.
Docelowa granica POP: [#6](https://github.com/robmar-net/literaki-slownik/issues/6).

## Kontekst
W `pop-v2` POP to 60 000 leksemów jednostek przed przycięciem. Gdy STANDARD rośnie, nowe słowa zajmują miejsca:
dodatki z #4 wypchnęłyby 2 430 form POP o niezmienionych dowodach.
Badanie: [kalibracja POP](../../.maister/tasks/development/2026-10-12-stabilizacja-progu-pop/analysis/research-context/pop-calibration.md).
Stały próg dzisiejszego cięcia odtwarza bazowy POP (1 227 250 form) i po dodatkach daje +2 372/0.

## Decyzje
D1–D5, D7–D9 jak w ADR-007 (rew. 4). Zmiany:

**D6. POP: punktacja ≥ −1,042878629; POP0: 20 000 leksemów.**
POP bierze każdą jednostkę rankingu z miarą D3 (średnia log-ipm) nie mniejszą od progu, z remisem na granicy.
Jednostka bez miary nie wchodzi. Liczba leksemów jest wynikiem, nie limitem.
Wartość to miara ostatniej jednostki POP `pop-v2` na STANDARD v29: zamrożona stała, nie granica znajomości słów.
POP0 bez zmian (limit liczby, blok remisu w całości albo wcale).

**D5 dla POP: własna punktacja zamiast własnej rangi.** Członek grupy zostaje w POP, gdy własna miara ≥ próg.
Wyjątki bez zmian: najmocniejszy członek (największa własna miara), grupa bez rozdzielnych dowodów, warianty
jednego lematu razem. POP0 dalej porównuje własną rangę z granicą POP0.

**POP0 ⊆ POP sprawdza budowa.** Progi są w różnych miarach, więc konfiguracja tego nie gwarantuje.
Naruszenie (jednostki albo leksemy) = kod 4.

Konfiguracja: [`config/generator/pop.json`](../../config/generator/pop.json) (`pop-v3`).
`pop-v2` zostaje odtwarzalne: [`config/generator/pop-v2.json`](../../config/generator/pop-v2.json) to bajtowa kopia
konfiguracji wydanego pakietu (SHA256 `affcfab8…9a60`). Walidacja wymaga pary rodzajów progu danej wersji
(`pop-v2`: liczba/liczba, `pop-v3`: punktacja/liczba) i skończonej liczby.

Raporty: `thresholds.json` podaje `by`, `score` albo `limit`, ostatnią rangę, jednostki, leksemy, pokrycie
i `provisional` (link do #6). Pakiet nie podaje miar jednostek (C14); członek grupy ma tylko
`member_meets_score` (tak/nie). `explain --variant pop` pokazuje próg punktacji, `pop0` — limit i rangę.

Odrzucone: limit 60 025 (dopasowanie do jednej paczki); limit 70/80 tys. (przesuwa konkurencję o miejsca);
progi 0,075/0,05/0,025 (poszerzają POP bez kalibracji; decyzja w #6).

## Ograniczenia
- Stała jest w skali D3 (KWJP+NKJP log-ipm, waga 0,5). Wycofanie NKJP (ADR-006) zmienia skalę: wymaga nowej stałej
  i nowej wersji metody; `pop-v3` przyjmuje tylko tę D3.
- Stała nie gwarantuje braku ubytków przy zmianie źródeł, mapowania lub grup.
- Wyjątki grupowe zostają; nie każdy leksem ma własny mocny dowód.
- Wartość pochodzi z historycznego cięcia, nie z oceny ludzi.

## Rewizja
Nową granicę ustala #6. Zmiana progu to nowa wersja metody i nowy ADR.
