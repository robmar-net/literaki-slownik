# Dziennik pracy #14

## TL;DR
Przed wydaniem TEMATY: matematyka i medycyna v3, jedna seria budów 10 tematów. Bez wydania. Plan: [plan.md](plan.md).

## Kluczowe decyzje
- Medycyna: atomy T1 bez zmian, 5 wykluczeń z `psych.` (operator, 2026-10-29).
- Pakiety w `data/work/tematy-wydanie-<data>/`, bo nazwy z tą datą już istnieją.

## Otwarte pytania
- Wydanie: osobna decyzja operatora. Pakiety `-a` w `gate-report.md`.

## Wpisy
- 2026-10-29T14:52:00Z — start, [#14](https://github.com/robmar-net/literaki-slownik/issues/14). Dependabot: brak otwartych PR-ów (Literaki-server, literaki-slownik).
- 2026-10-29T14:52:00Z — krok 1: matematyka v3 (+pryzma, reeksport), medycyna v3 (+walidować, logizować, apercypować, rozhamować jako `inf`; dezindywiduacja). Test `test_tematy_fala`: red, potem green; pełny zestaw OK.
- 2026-10-29T15:23:27Z — krok 2: 20 budów z HEAD `c563c33` w `data/work/tematy-wydanie-20261029/`: a = b, checker pass, jeden `git_commit` w 20 manifestach. 8 tematów bez zmiany składu jest bajtowo jak poprzednie pakiety, poza `release-manifest.json` i `SHA256SUMS`. Matematyka 467 wpisów, medycyna 2 891; brak 7 wykluczonych lematów w TSV.
- 2026-10-29T15:23:27Z — krok 3: `przepnij.py` przepiął przeglądy 8 tematów (morze z ocenami operatora z #12), checker `--review` exit 0. Medycyna: 100/100 ocen przeniesionych. Matematyka: 98 przeniesionych, 2 nowe (centyl, wierzchołek) do oceny agenta.
- 2026-10-29T15:26:07Z — krok 3–4: matematyka: agent ocenił 2 nowe pozycje (2 × „tak”); checker `--review` exit 0 dla matematyki i medycyny. `zestawienie-wydanie.json`, `gate-report.md` z sha256 manifestów. Matematyka v3 przechodzi wszystkie progi.
- 2026-10-29T15:26:07Z — krok 5–6: ADR-013 („Przed wydaniem”), INDEX.md, wiki `a7dc527`. Pełny zestaw testów OK.

## Standards Compliance Checklist (wynik)
- [x] Polski, zwięźle, z TL;DR / Kluczowe decyzje / Otwarte pytania (gate-report, work-log).
- [x] Zmiana składu zatwierdzona przez operatora (AskUserQuestion: medycyna, 5 wykluczeń; matematyka z bramki #13).
- [x] Bez nazw innych gier słownych.
- [x] Pakiety w `data/work` poza Git; piny wejść bez zmian.
- [x] Decyzja w ADR-013 i INDEX.md.
- [x] Wiki według runbooka, nadal „W przygotowaniu”.
- [x] Próba R2 `tematy-quality-v1`, progi bez zmian.
- [x] Nazwy pakietów `tematy-<wersja>-YYYYMMDD-{a,b}` (w katalogu serii `tematy-wydanie-20261029/`).
- [x] Commit i push po zapisach w `.maister/tasks`.
- [x] Bez CI na runnerach GitHuba.
