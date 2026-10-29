# Dziennik pracy #13

## TL;DR
v2 siedmiu tematów z bramki #12. Plan zatwierdzony przez operatora: [plan.md](plan.md).

## Kluczowe decyzje
- Wykluczenie jest bezwzględne: obejmuje też dodatki D (ADR-013).
- Oceny R2 agenta z #12 przenosimy dla tych samych kluczy; agent ocenia tylko nowe pozycje.

## Otwarte pytania
- Brak w #13. Na wydanie czekają: pryzma i reeksport w matematyce, atomy T1 medycyny, jedna przebudowa wszystkich 10 tematów (ADR-013).

## Wpisy
- 2026-10-29T13:51:31Z — start. Dependabot: brak otwartych PR-ów (Literaki-server, literaki-slownik).
- 2026-10-29T13:51:31Z — krok 1: `1498e3a` wykluczenie a D (test red → green). Krok 2: `eed1569` checker (teksty, summary) i wczesna walidacja odcinków. Pełny zestaw testów OK.
- 2026-10-29T13:51:31Z — krok 3: pliki 7 tematów v2, `tests/test_tematy_fala.py`. Skrypty budowy: kopie z #12 (`buduj_v2.sh`, `verify_real.py` z pustym `Z_T3`).
- 2026-10-29T14:11:26Z — krok 4: 14 budów (HEAD `a56b815`), a = b i checker pass dla wszystkich 7 tematów. Kontrola medycyny zgłosiła fałszywy alarm: słowo „IATE” w `uwagi` kopii pliku tematu. `verify_real.py` pomija teraz plik tematu; po powtórzeniu kontroli medycyna jest zgodna. Słowa oczywiste: grzyby 30/34, pogoda 30/36, sport 34/36, matematyka 28/35, muzyka 28/37, kuchnia 31/37, medycyna 31/39. Liczby w `verify-<id>.json`.
- 2026-10-29T14:11:26Z — krok 5: przeniesione oceny z #12 (`przenies_oceny.py`): 33 pozycje do oceny (grzyby 5, matematyka 6, muzyka 3, kuchnia 3, medycyna 16; pogoda i sport 0). Medycyna: 10 pozycji ze zmienionymi źródłami (bez T3), 6 nowych.
- 2026-10-29T14:22:29Z — krok 5–6: 33 oceny agenta (5 sesji, po jednej na temat), checker `--review` exit 0 dla 7 tematów, `zestawienie-v2.json`, `gate-report.md`. Bramka (AskUserQuestion): operator wybrał „Dalej wszystkie” — grzyby (T2 24/50), matematyka (T2 32/50) i medycyna (T1 43/50) idą dalej mimo progu.
- 2026-10-29T14:22:29Z — krok 7: ADR-013, ADR-012 (odsyłacz), INDEX.md, cli.md, jakosc.md, runbook-wiki.md; wiki `bb68b05` (TEMATY v2, Historia zmian, Home).
- 2026-10-29T14:22:29Z — krok 8: pełny zestaw testów: 560 OK. Regresja morza na nowym kodzie (`data/work/tematy-morze-v2-20261029-r13`): wszystkie pliki bajtowo jak w #12, poza `release-manifest.json` (`code_identity`) i `SHA256SUMS`.

## Standards Compliance Checklist (wynik)
- [x] Teksty po polsku, zwięźle, z TL;DR / Kluczowe decyzje / Otwarte pytania (ADR-013, gate-report, work-log).
- [x] Skład słownika pokazany operatorowi przed wdrożeniem (tabela w zatwierdzonym planie).
- [x] Bez nazw innych gier słownych (sprawdzony diff wiki).
- [x] Pakiety w `data/work` poza Git; piny w `tematy-sources.json` bez zmian.
- [x] Decyzja techniczna w ADR-013 i INDEX.md.
- [x] Wiki według runbooka; „W przygotowaniu”, bez wydania.
- [x] Próba R2 `tematy-quality-v1`, D poza próbą, progi bez zmian.
- [x] Kody wyjścia zgodne z cli.md (kod 4 dla dodatku z wykluczeniem; opisany).
- [x] Commit i push po zapisach w `.maister/tasks`.
- [x] Bez kontaktu z autorami zasobów.
- [x] Bez CI na runnerach GitHuba (repo bez workflow; nic nie dodano).
