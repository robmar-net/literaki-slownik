# Odbiór pełnych danych: LL-PL v30 (roboczy) i POP pop-v3

## TL;DR
STANDARD +2382 (dokładnie wyjątki #4) −336 (#5); BROAD −346 (#5). Dwa przebiegi LL-PL dają bajtowo te same listy; `verify` = VERIFIED; `export` FROZEN.
POP i POP0 (pop-v3, oba progi score, tymczasowe — #6): dwa przebiegi identyczne; na starym STANDARD bajtowo równe wydanemu pop-v2; straż 0 braków; checker OK.
Nic nie wydano. Wydanie i gra: osobna decyzja.

## LL-PL

| | v30 przebieg (wydanie llpl-v29) | v31 przebieg (pakiet LL-PL v30) | + | − |
|---|---:|---:|---:|---:|
| STANDARD | 3 090 194 | 3 092 240 | 2382 (#4) | 336 (#5) |
| BROAD | 3 479 364 | 3 479 018 | 0 | 346 (#5) |

- Przebiegi: A `lists-v31-20261012-162111-a` (13,8 h), B `lists-v31-20261013-060725-b` (12,9 h); kod `0560f20` (`tree_sha256 f71d223d…`).
- `reports/decisions.json`: 7192/7192 dopasowanych, 0 niewykorzystanych, 2382 słowa (7060 źródłowych, 132 konstrukcje).
- Ubytki: same formy `nie…` od zaimków i nieodmiennych; liczby równe pomiarowi #5.
- K9: `quality-review-v31.json`, 1876 pozycji, 0 błędnych, 23 niepewne; dodatkowo 40 dodatków #4 i 20 ubytków #5 — trafne.
- `verify --run-dir A --peer-run B`: VERIFIED, K1–K10 pass (7,3 h).
- `export` → `data/work/release-LL-PL-v30`: release-manifest `cdc59511…`, STANDARD `dab4f3bc…`, baza A `4b0d17c6…`.

## POP / POP0 (`pop-v3`, `data/work/pop-v3-20261014-022011-{a,b,base29}`)

| | pop-v2 | pop-v3 | + (#4) | − (#5) | leksemy | pokrycie KWJP (słowa STANDARD) |
|---|---:|---:|---:|---:|---:|---:|
| POP (score ≥ −1,042878629) | 1 227 250 | 1 229 303 | 2372 | 319 | 53 033 | 98,6% |
| POP0 (score ≥ 0,57370099) | 388 509 | 388 763 | 481 | 227 | 13 896 | 94,6% |

- a = b bajtowo (POP `e360ba56…`, POP0 `34be65fa…`).
- `base29` (nowy kod na starym STANDARD) = wydany pop-v2 bajtowo (`0ef37e78…`, `e91eb7e5…`).
- Straż: 20 000 / 5 000 najczęstszych form KWJP — 0 braków. `POP0 ⊆ POP ⊆ STANDARD`; `check_pop_package.py` OK dla a, b i base29.
- 10 dodatków #4 poza POP: odmiana `pojazdowy` (zgodnie z badaniem).

## Odstępstwa i ograniczenia
- POP0 również stały próg (decyzja właściciela 2026-10-13, #6); plan przewidywał limit 20 000. Na v30 wynik identyczny z limitem.
- Zamrożony v30 nietknięty (mtime `build.sqlite` 1791660525). Stare przebiegi v25–v29 usunięte za zgodą właściciela (dysk).
