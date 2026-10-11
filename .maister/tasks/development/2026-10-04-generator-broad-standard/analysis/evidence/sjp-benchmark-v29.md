# Porównanie z SJP.pl: v29

## TL;DR
Rundy 6 i 7 usunęły marki i dawne formy, które wchodziły do STANDARD dzięki nazwom własnym. Pokrycie SJP.pl prawie się nie zmieniło. W tekstach STANDARD zna o 0,06 pp mniej, bo te formy liczyły się dzięki wystąpieniom typu „Nowak”.

Metoda i zakres jak w [v25](sjp-benchmark-v25.md). Ten sam skrypt i ta sama lista SJP.pl.

| miara | BROAD v27 | BROAD v29 | STANDARD v27 | STANDARD v29 | SJP.pl |
|---|---:|---:|---:|---:|---:|
| słowa | 3 479 827 | 3 479 364 | 3 090 887 | 3 090 194 | 3 239 694 |
| różne słowa SJP.pl, które mamy | 81,13% | 81,13% | 78,08% | 78,07% | — |
| wystąpienia słów w tekstach KWJP, które znamy | 95,36% | 95,28% | 95,31% | 95,17% | 95,38% |

Miara tekstów liczy formy po zamianie na małe litery, więc „Ford” liczy się jak `ford`. Spadek po usunięciu marek i nazw jest skutkiem zasad gry, nie regresją.

## Zmiany
- v28 (runda 6): −463 słowa w obu listach, marki z zamkniętej listy (`toyota`, `ford`, `warszawa` jako samochód).
- v29 (runda 7): −230 słów w STANDARD, BROAD bez zmian (`nowak`, `amerykanie`, `ali`, `aukcyjny`).
- Krótkie słowa: 2 litery: 23 tylko w SJP.pl, 10 tylko u nas (bez zmian); 3 litery: 247 i 152 (v27: 153).

## Otwarte
- Luki źródła: przymiotniki z przedrostkiem (`antydumpingowy`), pospolite homonimy nazw własnych (`janusz`, `kraków` od „krak”).
- Wyjątek współczesnego użycia mierzy formę, nie znaczenie (`sek` z „sek.”).

Listy: sha256 BROAD `9be96245…`, STANDARD `a432c7c5…`, build `lists-v30-20261010-165826-a` (wszystkie etapy `complete`, coverage COMPLETE, 12,6 h; build kontrolny `-b` identyczny).
