# Kontrola kompletności: POP/POP0 (#3)

## TL;DR
- Wynik: **passed_with_issues**. 0 krytycznych, 3 ostrzeżenia, 4 informacje.
- Plan: 17/17 grup, 102/102 kroki `[x]`. Kod jest dla każdej grupy.
- Standardy: zgodne. Wiki, Release, ADR i dokumenty zaktualizowane.
- Główna luka: spec rew. 3 opisuje metodę sprzed rew. 2 i 3 ADR-007 (stare liczby i opcje D3, D5, D8).

## Key Decisions
- Zmiany metody po przeglądach (ADR-007 rew. 2, 3) uznaję za udokumentowane: ADR, work-log, `pop-acceptance.md`, `pop.json`. Brak ich tylko w spec i planie.
- Zmiana kodu rankingu w C (`measure_floors` l. 735, `prune_members` l. 1040 nad znacznikiem konfiguracji l. 1190) jest dozwolona przez 16.2: ponowny pomiar `data/work/pop-measure-20261011-175938-r3` istnieje.
- „POP = sonda (45 229 / 1 328 263)” z 11.7 i 16.6 nie jest spełnione dosłownie. Rozbieżność wynika ze zmiany metody zatwierdzonej przez właściciela, nie z błędu.

## Open Questions / Risks
- Kto czyta spec, dostaje złą miarę (percentyle F, `available-only`, `e-common` bez przycinania) i złe liczby POP.
- `.maister/docs/INDEX.md` nie wskazuje ADR-006, ADR-007 ani tego zadania.

## 1. Plan
| miara | wynik |
|---|---|
| kroki | 102/102 (119 `[x]` z nagłówkami x.0), 0 `[ ]` |
| kod | `pop.py`: `load_sources` 70, `check_inputs` 90, `load_kwjp` 196, `read_nkjp` 361, `units` 540, `measure` 742, `threshold` 869, `load_config` 1300, `build_pop` 1419, `_write_gzip` 1543; `explain.py`: `explain_pop` 342; `cli.py`: `pop`, `--variant pop/pop0`, `--pop-dir`; `quality.SEEDS`; `scripts/measure_pop.py`, `scripts/check_pop_package.py` (tylko stdlib) |
| konfiguracja | `pop.json` = ADR-007 rew. 3 (`log-ipm`, `prune-weak-members`, `lower-bound-absent`) |
| testy | 6 plików testów POP są; work-log: 372 OK |
| dane | `data/work/pop-v1r3-…-a/-b`, pakiet z `LIMITATIONS.md` (C19 opisane) |
| wydanie | Release `pop-v1`: 5 assetów wg 17.2 |

## 2. Standardy
| standard | dotyczy | wynik |
|---|---|---|
| AGENTS.md: polski, zwięźle | tak | spełnione |
| AGENTS.md: decyzje o składzie z właścicielem | tak | delegacja zapisana w ADR-007; przegląd zatwierdzony |
| AGENTS.md: wiki w tej samej pracy | tak | 6 stron, bez „przygotowaniu”, wypchnięte (`master...origin/master`) |
| `docs/runbook-wiki.md` | tak | liczby z manifestu, sha256, link Release i ADR; w tabelach zwykłe linki (`[[a|b]]` w `Home.md` tylko poza tabelami, l. 20, 41) |
| ADR-006 (NKJP) | tak | `ATTRIBUTIONS.md` l. 61–75; pakiet bez surowego NKJP |
| ADR-007 | tak | `pop.json` ↔ ADR wskazują się nawzajem |
| `jakosc.md`, `publikacja.md` | tak | `pop-quality-v1` opisane; TERMS w pakiecie |
| prosty język §4–5 | tak | brak list zewnętrznych |
| `.maister/docs/INDEX.md` | tak | nieaktualny (zob. ostrzeżenie 3) |

## 3. Dokumentacja
| artefakt | wynik |
|---|---|
| work-log | 16 wpisów z czasem, każda grupa, iteracje 2 i 3, wpis końcowy |
| ADR-007 | rew. 2 i 3 z liczbami i przykładami |
| `pop-acceptance.md` | D-1…D-7, hashe, liczby, `tree_sha256` |
| docs | `cli.md`, `jakosc.md`, `runbook-wiki.md`, `plan-dalszych-prac-runbook.md` zaktualizowane |
| spec rew. 3 | nieaktualny wobec ADR rew. 2/3 |

## Problemy
| # | waga | miejsce | opis | do poprawy |
|---|---|---|---|---|
| 1 | ostrzeżenie | `implementation/spec.md` l. 9, 47–52, 120, 221 | TL;DR i tabela metody: percentyle F, `e-common`, `available-only`; kryterium „POP = 45 229 / 1 328 263”. ADR i pakiet: log-ipm, `prune-weak-members`, `lower-bound-absent`, POP 51 805 leks. / 1 219 614 form | tak: dopisać rew. 4 albo notę „metoda wg ADR-007 rew. 3” i nowe liczby |
| 2 | ostrzeżenie | `implementation/implementation-plan.md` l. 6–9, 12, 438–444 | TL;DR „grupa 10 czeka”, kolejność bez „zrobione” dla 10–17; „kod rankingu bez zmian” nieprawdziwe po rew. 2/3 | tak: odświeżyć TL;DR i kolejność, dopisać notę o iteracjach |
| 3 | ostrzeżenie | `.maister/docs/INDEX.md` | brak ADR-006, ADR-007 i zadania POP | tak: dodać 2–3 linki |
| 4 | informacja | `work-log.md` l. 5, 8–11 | „Total Steps: 90” (plan: 102); „Standards Reading Log” pusty; grupy 6–17 bez wiersza standardów | tak |
| 5 | informacja | `pop-acceptance.md` D-6 | brak liczb z ponownego pomiaru r3 (tylko ścieżka) | tak |
| 6 | informacja | `orchestrator-state.yml` | niezacommitowany; reszta wypchnięta | tak |
| 7 | informacja | 11.7, 16.6 | „POP = sonda” niespełnione dosłownie; przyczyna udokumentowana (ADR rew. 2/3) | nie (decyzja) |
