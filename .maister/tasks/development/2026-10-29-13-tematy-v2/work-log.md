# Dziennik pracy #13

## TL;DR
v2 siedmiu tematów z bramki #12. Plan zatwierdzony przez operatora: [plan.md](plan.md).

## Kluczowe decyzje
- Wykluczenie jest bezwzględne: obejmuje też dodatki D (ADR-013).
- Oceny R2 agenta z #12 przenosimy dla tych samych kluczy; agent ocenia tylko nowe pozycje.

## Otwarte pytania
- Bramka v2 po zestawieniu (operator).

## Wpisy
- 2026-10-29T13:51:31Z — start. Dependabot: brak otwartych PR-ów (Literaki-server, literaki-slownik).
- 2026-10-29T13:51:31Z — krok 1: `1498e3a` wykluczenie a D (test red → green). Krok 2: `eed1569` checker (teksty, summary) i wczesna walidacja odcinków. Pełny zestaw testów OK.
- 2026-10-29T13:51:31Z — krok 3: pliki 7 tematów v2, `tests/test_tematy_fala.py`. Skrypty budowy: kopie z #12 (`buduj_v2.sh`, `verify_real.py` z pustym `Z_T3`).
- 2026-10-29T14:11:26Z — krok 4: 14 budów (HEAD `a56b815`), a = b i checker pass dla wszystkich 7 tematów. Kontrola medycyny zgłosiła fałszywy alarm: słowo „IATE” w `uwagi` kopii pliku tematu. `verify_real.py` pomija teraz plik tematu; po powtórzeniu kontroli medycyna jest zgodna. Słowa oczywiste: grzyby 30/34, pogoda 30/36, sport 34/36, matematyka 28/35, muzyka 28/37, kuchnia 31/37, medycyna 31/39. Liczby w `verify-<id>.json`.
- 2026-10-29T14:11:26Z — krok 5: przeniesione oceny z #12 (`przenies_oceny.py`): 33 pozycje do oceny (grzyby 5, matematyka 6, muzyka 3, kuchnia 3, medycyna 16; pogoda i sport 0). Medycyna: 10 pozycji ze zmienionymi źródłami (bez T3), 6 nowych.
