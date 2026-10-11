# Odbiór POP/POP0 (pop-v2, metoda ADR-007 rew. 4)

## TL;DR
Pakiet `pop-v2` spełnia D-1…D-7. Przegląd 423 próbek: 416 trafnych, 4 pojedyncze słowa (granica, lemat `krocie`), 0 wad klasy; straż częstych form 0 braków. Zastępuje wycofane pop-v1. Zatwierdził właściciel 2026-10-11.

## Key Decisions
- Cztery rewizje metody (ADR-007 rew. 2–4): NKJP wspólny z nazwą własną pomijany, miara log-ipm, dolne ograniczenie dla brakującego źródła, granica nie dzieli bloków, przycinanie słabych członków grup z wariantami lematu razem, straż częstych form.

## Open Questions / Risks
- Ranking z korpusów słabo widzi słowa potoczne (D7). Przy granicy POP zdarzają się archaizmy i przymiotniki od małych miejscowości (`przestanek`, `strzeleński`).
- POP ⊆ LL-PL STANDARD. Podłączenie do gry to osobna praca.

| kryterium | wynik |
|---|---|
| D-1 dwa przebiegi | `diff -r` identyczne (`data/work/pop-v2-20261011-194738-a`, `-b`) |
| D-2 baza i LL-PL bez zmian | hash bazy `85b23ca5cfaae273ec869f84fab643a87685c455606d8b21df4aec918f3a338c`; hashe `manifest.json`, `lists/`, `reports/` przebiegu i release-manifest v29 przed = po |
| D-3 kontrola pakietu | `scripts/check_pop_package.py` = 0 |
| D-4 przegląd | 416 correct / 4 incorrect / 3 unknown; `verification/pop-v2-review.json` |
| D-5 kontrola z przeglądem | `check_pop_package.py --review` = 0 |
| D-6 pomiar | ponowny pomiar `data/work/pop-measure-20261011-194738-v2` po zmianie kodu rankingu |
| D-7 ten dokument | — |

| | POP | POP0 |
|---|---:|---:|
| leksemy | 53 002 | 13 896 |
| jednostki | 45 137 | 11 638 |
| formy | 1 227 250 | 388 509 |
| sha256 listy (rozpakowanej) | `d846b7f0ec03b9da2b3ce39cdcdee1efac5fc8d683e0d1caf0d770cd544aebd7` | `594a3bd67a426ec3a71dc55c483b91815f765c67291f27c89f335568098e276e` |

release-manifest sha256: `2a4bcc78d049f555c61be9d0ce89c7c26d896225d8d35aeb5eead0c72504e8e8`. Kod: tree_sha256 `c2f8fa14191b9e7968b18cee3788ddda1d60306b9eb81aea60718d93a667de0c`.
