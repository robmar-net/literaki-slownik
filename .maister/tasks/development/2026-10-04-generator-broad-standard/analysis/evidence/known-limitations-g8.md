# Znane ograniczenia (G8, K5)

## Wniosek
Trzy reguły zostawiają część analiz bez rozstrzygnięcia. Nie zmienia to żadnego słowa na listach: każdą taką analizę inna reguła i tak odrzuca. Decyzja agenta, 2026-10-09, odwracalna.

## Miara
Raport `reports/unresolved.json` z buildu v28 (`lists-v28-20261009-101041-a`):
- słowa nierozstrzygnięte: 0 w BROAD i 0 w STANDARD;
- analizy nierozstrzygnięte w ocenie końcowej: 0;
- przy każdej regule poniżej: `word_keys_by_membership.unresolved = 0`, a wszystkie jej analizy mają końcowe odrzucenie.

`verify` liczy to samo dla nowego przebiegu. Jeśli któraś reguła zmieni choć jedno słowo, odbiór K5 się zatrzyma, mimo tego wpisu.

## Reguły

| reguła | warstwa | co zostaje otwarte | analizy / słowa | słowa: przyjęte inną analizą / odrzucone |
|---|---|---|---|---|
| `game-proper-name-class-v1` | game | SGJP daje tej samej analizie oznaczenie nazwy własnej i pospolitej | 476 / 269 | 184/85 (BROAD), 163/106 (STANDARD) |
| `linguistic-unknown-qualifier-v1` | language | kwalifikator bez zatwierdzonego warunku | 6 / 1 | 0/1 |
| `preposition-n-whole-form-proof-v1` | language | forma przyimek+`ń` spoza wyliczenia §9.1 SGJP | 24 / 8 | 0/8 |

## Wycofanie
Usunąć wpisy z `config/generator/release.json` (`known_limitations`). `verify` zatrzyma wtedy odbiór na K5.
