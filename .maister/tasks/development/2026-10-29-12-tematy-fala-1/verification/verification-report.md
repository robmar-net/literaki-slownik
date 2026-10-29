# Weryfikacja #12 (TEMATY, fala 1)

## TL;DR
- Zakres wybrany przez operatora: przegląd kodu i kompletność.
- Kompletność: **passed_with_issues** — 7 pozycji w dokumentach, wszystkie poprawione w tym commicie.
- Przegląd kodu: brak krytycznych. Nic nie wpływa na 10 zbudowanych pakietów: a/b identyczne dla wszystkich 10, checker niezależny od generatora.
- 2 uwagi niskie i uwagi informacyjne przechodzą do v2 (niżej).
- Pełny zestaw testów: 555 + 5 OK (grupa 19).

## Kluczowe decyzje
- Bramka (operator, 2026-10-29): dalej — kuchnia, rośliny, zwierzęta, morze; popraw — grzyby, pogoda, sport, matematyka, muzyka, medycyna. Bez wydania; v2 poza #12 ([gate-report.md](gate-report.md), [ADR-012](../../../../../docs/adr/ADR-012-tematy-fala-1.md#zmiana-metody-r2-2026-10-29)).
- Uwag z przeglądu nie poprawiamy w #12: nie zmieniają zbudowanych pakietów, a dotyczą budów v2.

## Otwarte pytania
- **Wykluczenia a dodatki D** (niska). Generator `_exclude` (`literaki_slownik/tematy.py` ~672–691) usuwa tylko leksemy T1–T3. Checker `exclusions` (`scripts/check_tematy_package.py` ~231–240) odrzuca każdy wiersz TSV, także D, z wykluczoną klasą. Ustalić semantykę przed v2 grzybów (dodatki i wykluczenia naraz).
- **Checker nie sprawdza tekstów pakietu niezależnie** (niska): resztki `<!--` i `@@SRODLADOWE@@`, atrybucja IATE bez `t3`. Nie sprawdza też pól `summary.json`: `t3`, `srodladowe`, `nie_dotyczy`.
- **Walidacja odcinków tekstów** (info) działa dopiero przy zapisie pakietu. Mogłaby zaraz po `load_topic`.
- **KeyError zamiast kodu wyjścia** (info) przy brakujących polach w checkerze (~238, ~680).
- **Licencja plWordNet** (info): cytat w `config/generator/tematy-teksty/ATTRIBUTIONS-tematy.md` kończy się bez kropki. Sprzed #12; porównać z oryginałem.

## Kompletność — poprawione dokumenty
1. ADR-012, „Zmiana metody R2” i TL;DR: decyzje operatora (4 dalej / 6 popraw) zamiast „decyzje jeszcze nie zapadły”; „Otwarte na v2”.
2. `gate-report.md`: TL;DR, Kluczowe decyzje i Otwarte pytania zgodne z tabelą decyzji.
3. `spec.md`, „Zmiany po audycie”: operator nie ocenił R2, trafność z ocen agenta.
4. `.maister/docs/INDEX.md`: wpis ADR-012 o ocenach agenta w fali 1.
5. `work-log.md`: liczba kroków 127 (121 [x], 6 [~]).
6. `scope-clarifications.md`: `tematy-v1` → potem `tematy-v2` (ADR-012).
7. Ten raport.
