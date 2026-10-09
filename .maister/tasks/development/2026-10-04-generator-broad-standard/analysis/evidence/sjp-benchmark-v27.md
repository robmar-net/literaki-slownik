# Porównanie z SJP.pl: v27

## TL;DR
Po rundach 4 i 5 znamy w tekstach tyle samo słów co SJP.pl. Różnych słów SJP.pl brakuje nam nadal około 611 tys., prawie wyłącznie rzadkich.

Metoda i zakres jak w [v25](sjp-benchmark-v25.md). Ten sam skrypt i ta sama lista SJP.pl.

| miara | BROAD v25 | BROAD v27 | STANDARD v25 | STANDARD v27 | SJP.pl |
|---|---:|---:|---:|---:|---:|
| słowa | 3 469 938 | 3 479 827 | 3 081 120 | 3 090 887 | 3 239 694 |
| różne słowa SJP.pl, które mamy | 80,9% | 81,1% | 77,8% | 78,1% | — |
| wystąpienia słów w tekstach KWJP, które znamy | 93,0% | **95,4%** | 92,8% | **95,3%** | 95,4% |

## Wnioski
- Wzrost pokrycia tekstów to prawie w całości `się` i `siebie` (uzupełnienie SGJP).
- Krótkie słowa: 2 litery: 23 tylko w SJP.pl, 10 tylko u nas (v25: 18); 3 litery: 247 i 153 (v25: 176).
- Skróty jako rzeczowniki (`nr`, `dr`, `pkt`) zniknęły z naszych nadwyżek.

## Otwarte
- **Marki małą literą** (`ford`, `toyota`, `audi`, `facebook`, `warszawa` jako samochód) jeszcze przechodzą. ZDS 01/2026 ich nie dopuszcza. SGJP oznacza je jako `nazwa_pospolita`, bez śladu marki.
- Kryterium „w tekstach zwykle wielką literą” nie nadaje się do ich wykrycia: łapie też zwykłe słowa (`bóg`, `polak`, `francuz` jako klucz). Potrzebna zamknięta lista ręczna.
- Luki źródła: przymiotniki z przedrostkiem (`antydumpingowy`), pospolite homonimy nazw własnych (`janusz`, `kraków` od „krak”).

Listy: sha256 BROAD `7a0da133…`, STANDARD `b378b81c…`, build `lists-v27-20261008-150154-a` (wszystkie etapy `complete`, coverage COMPLETE, 13,5 h).
