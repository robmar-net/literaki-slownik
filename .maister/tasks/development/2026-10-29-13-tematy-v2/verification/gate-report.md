# Bramka v2 (#13)

## TL;DR
Sześć tematów przechodzi wszystkie progi (pogoda, muzyka, sport, kuchnia oraz bez zmian rośliny i zwierzęta). Trzy nie przechodzą jednego progu: grzyby i matematyka `t2_tak`, medycyna `t1_tak`. Wszystkie braki to oceny „niepewne”, nie „nie”: `t2_nie` jest spełnione wszędzie. **Decyzja operatora (2026-10-29): dalej wszystkie 10.** Bez wydania.

## Kluczowe decyzje
- R2 z ocen agenta, tak jak w #12. Oceny z #12 przenosimy, gdy klucz i `selected_unit` są identyczne. Nowych pozycji jest 33 (`przeniesienie-ocen.json`).
- Progi bez zmian (`config/generator/tematy.json`).

## Otwarte pytania
- Rozstrzygnięte: grzyby, matematyka i medycyna idą „dalej” mimo progu, bo agent jest surowszy od operatora (morze: agent T2 21/50, operator 30/30). Pryzma i reeksport wykluczymy w matematyce przy następnej wersji.

## Wyniki (pakiety `-v2-20261029-a`, `zestawienie-v2.json`)

| Temat | Wpisy v1 → v2 | Słowa oczywiste | T1 tak | T2 tak | T2 nie | Bramka |
|---|---|---|---|---|---|---|
| grzyby | 207 → 211 | 21/34 → 30/34 | 1 | 23/50 → **24/50** | 0 | popraw |
| pogoda | 232 → 239 | 23/36 → 30/36 | 24/25 | 41/50 | 0 | dalej |
| matematyka | 475 → 469 | 4/5 | 49/50 | 29/50 → **32/50** | 3/25 → 1/25 | popraw |
| muzyka | 1063 → 1060 | 28/37 | 47/50 | 16/25 → 17/25 | 0 | dalej |
| sport | 794 → 808 | 20/36 → 34/36 | 24/25 | 22/25 | 0 | dalej |
| kuchnia | 1818 → 1815 | 31/37 | 1 | 9/10 | 0 | dalej |
| medycyna | 3246 → 2896 | 32/39 → 31/39 | 21/25 → **43/50** | 41/50 | 1/25 | popraw |

Progi: słowa oczywiste ≥ 0,70; T1 ≥ 0,90; T2 tak ≥ 2/3, nie ≤ 0,10.

## Co zostaje poniżej progu
- **grzyby, T2:** 26 × „niepewne”, 0 × „nie”. Głównie rzadkie nazwy grzybów i terminy mykologiczne (np. łysak, zębak, przetrwalnik, zoospora). Do progu brakuje 10 „tak”.
- **matematyka, T2:** 16 × „niepewne”, 2 × „nie” (pryzma, reeksport). Wśród „niepewne” są terminy geometrii i astronomii (azymut, loksodroma, ekliptyka). Brakuje 2 „tak”.
- **medycyna, T1:** 7 × „niepewne”, 0 × „nie” (np. afekt, cyklotymik, zoofilia; atomy `psych.` i `med.`). Do 0,90 brakuje 2 „tak”. W v1 było 21/25, więc ten próg nie przechodził już wtedy; bramka #12 dotyczyła T3.
- Medycyna straciła jedno słowo oczywiste, które było tylko w T3.

Morze w zestawieniu ma werdykt „popraw” z ocen agenta. Na bramce #12 operator dał „dalej” (swoje oceny 30/30), więc bez zmian.
