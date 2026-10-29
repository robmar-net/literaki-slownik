# Dziennik pracy #14

## TL;DR
Przed wydaniem TEMATY: matematyka i medycyna v3, jedna seria budów 10 tematów. Bez wydania. Plan: [plan.md](plan.md).

## Kluczowe decyzje
- Medycyna: atomy T1 bez zmian, 5 wykluczeń z `psych.` (operator, 2026-10-29).
- Pakiety w `data/work/tematy-wydanie-<data>/`, bo nazwy z tą datą już istnieją.

## Otwarte pytania
- Wydanie: osobna decyzja.

## Wpisy
- 2026-10-29T14:52:00Z — start, [#14](https://github.com/robmar-net/literaki-slownik/issues/14). Dependabot: brak otwartych PR-ów (Literaki-server, literaki-slownik).
- 2026-10-29T14:52:00Z — krok 1: matematyka v3 (+pryzma, reeksport), medycyna v3 (+walidować, logizować, apercypować, rozhamować jako `inf`; dezindywiduacja). Test `test_tematy_fala`: red, potem green; pełny zestaw OK.
- 2026-10-29T15:23:27Z — krok 2: 20 budów z HEAD `c563c33` w `data/work/tematy-wydanie-20261029/`: a = b, checker pass, jeden `git_commit` w 20 manifestach. 8 tematów bez zmiany składu jest bajtowo jak poprzednie pakiety, poza `release-manifest.json` i `SHA256SUMS`. Matematyka 467 wpisów, medycyna 2 891; brak 7 wykluczonych lematów w TSV.
- 2026-10-29T15:23:27Z — krok 3: `przepnij.py` przepiął przeglądy 8 tematów (morze z ocenami operatora z #12), checker `--review` exit 0. Medycyna: 100/100 ocen przeniesionych. Matematyka: 98 przeniesionych, 2 nowe (centyl, wierzchołek) do oceny agenta.
