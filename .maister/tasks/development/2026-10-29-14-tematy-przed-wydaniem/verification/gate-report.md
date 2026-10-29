# Seria przed wydaniem (#14)

## TL;DR
Wszystkie 10 tematów zbudowano z jednego commita `c563c33`. Każdy temat ma dwie budowy (20 pakietów); obie są bajtowo identyczne i przechodzą checker. Przeglądy R2 przepięto na nowe pakiety, checker `--review` daje exit 0. Matematyka v3 przechodzi teraz wszystkie progi. Pakiety `-a` są gotowe do wydania. Wydanie to osobna decyzja.

## Kluczowe decyzje
- Matematyka v3: bez pryzma i reeksport.
- Medycyna v3: atomy T1 bez zmian, bez 5 słów z `psych.` (operator).
- Grzyby (T2 24/50), medycyna (T1 43/50) i morze idą dalej decyzją operatora z bramek #12 i #13.

## Otwarte pytania
- Kiedy wydanie (Release, link pobrania, zdjęcie „W przygotowaniu” na wiki).

## Pakiety (`data/work/tematy-wydanie-20261029/…-a`)

| Temat | Wersja | Wpisy | Formy | Słowa oczywiste | T1 tak | T2 tak | T2 nie | sha256 `release-manifest.json` |
|---|---|---|---|---|---|---|---|---|
| grzyby | grzyby-v2 | 211 | 1848 | 15/17 | 1 | 12/25 | 0 | `08c21aa966301bb4…` |
| pogoda | pogoda-v2 | 239 | 2191 | 5/6 | 24/25 | 41/50 | 0 | `dc7cea76aaa486b1…` |
| matematyka | matematyka-v3 | 467 | 4248 | 4/5 | 49/50 | 17/25 | 0 | `c1e726e68befb1e3…` |
| muzyka | muzyka-v2 | 1060 | 9158 | 28/37 | 47/50 | 17/25 | 0 | `ac5eafa0ec11d7b2…` |
| sport | sport-v2 | 808 | 8021 | 17/18 | 24/25 | 22/25 | 0 | `e67b8ecb02ad60da…` |
| kuchnia | kuchnia-v2 | 1815 | 16064 | 31/37 | 1 | 9/10 | 0 | `87cebffb3862cb6d…` |
| rosliny | rosliny-v1 | 2371 | 22244 | 1 | 47/50 | 19/25 | 0 | `296cbf78b70353c9…` |
| zwierzeta | zwierzeta-v1 | 2765 | 23880 | 1 | 1 | 43/50 | 0 | `349335480eb03765…` |
| medycyna | medycyna-v3 | 2891 | 26383 | 31/39 | 43/50 | 41/50 | 1/25 | `a63f05c710d96c7c…` |
| morze | morze-v2 | 970 | 11035 | 1 | 23/25 | 21/50 | 23/50 | `963022f0eb81ae09…` |

Progi liczone z ocen agenta. W morzu operator ocenił T2 i T3: 30/30 i 27/27 „tak” (#11, #12).
