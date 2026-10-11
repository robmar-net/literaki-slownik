# Odbiór POP/POP0 (pop-v1, metoda ADR-007 rew. 3)

## TL;DR
Pakiet `pop-v1` spełnia D-1…D-7. Przegląd 420 próbek: 414 trafnych, 3 sporne słowa przy granicy, 0 wad metody. Zatwierdził właściciel 2026-10-11.

## Key Decisions
- Trzy iteracje metody po przeglądach (ADR-007 rew. 2 i 3): NKJP wspólny z nazwą własną pomijany, miara log-ipm, dolne ograniczenie dla brakującego źródła, granica nie dzieli bloków, przycinanie słabych członków grup.

## Open Questions / Risks
- Ranking z korpusów słabo widzi słowa potoczne (D7). Przy granicy POP zdarzają się archaizmy i przymiotniki od małych miejscowości (`przestanek`, `strzeleński`).
- Serwer gra dziś na SJP.pl. POP ⊆ LL-PL STANDARD, nie ⊆ SJP.pl.

| kryterium | wynik |
|---|---|
| D-1 dwa przebiegi | `diff -r` identyczne (`data/work/pop-v1r3-20261011-175938-a`, `-b`) |
| D-2 baza i LL-PL bez zmian | hash bazy `85b23ca5cfaae273ec869f84fab643a87685c455606d8b21df4aec918f3a338c`; hashe `manifest.json`, `lists/`, `reports/` przebiegu i release-manifest v29 przed = po |
| D-3 kontrola pakietu | `scripts/check_pop_package.py` = 0 |
| D-4 przegląd | 414 correct / 3 incorrect / 3 unknown; `verification/pop-v1-review.json` |
| D-5 kontrola z przeglądem | `check_pop_package.py --review` = 0 |
| D-6 pomiar | ponowny pomiar `data/work/pop-measure-20261011-175938-r3` po zmianie kodu rankingu |
| D-7 ten dokument | — |

| | POP | POP0 |
|---|---:|---:|
| leksemy | 51 805 | 13 181 |
| jednostki | 45 056 | 11 633 |
| formy | 1 219 614 | 380 489 |
| sha256 listy (rozpakowanej) | `504725ab8c52e449c9c5109b1a4450f91c33b440c28573f45fb633d70d910139` | `6fde7b6a1d27787efec75730568f32781433165bcb7a2ddba0f505b7c580d966` |

release-manifest sha256: `f1552d2bf4de62f245c1e2e437f62144689446ba39602ea7e3096a93fbce826f`. Kod: tree_sha256 `85334f3561ab781bbe3021239a0fe568fe3cc62abf54376c62578e1afc0cb939`.
