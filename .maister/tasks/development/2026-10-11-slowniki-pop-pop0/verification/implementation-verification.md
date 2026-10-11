# Weryfikacja implementacji POP/POP0

## TL;DR
❌ **Nie zaliczona.** Mechanika działa (plan 102/102, testy 372 OK, pakiet odtwarzalny, atrybucje kompletne), ale treść `pop-v1` ma wadę High: przycinanie wariantów leksemu wyrzuca częste słowa (`pies`, `przypadek`, `padł`; `raz` poza POP0).
Problemy: 1 krytyczny, 9 ostrzeżeń, ok. 20 informacyjnych. Wydanie `pop-v1` wycofane (pre-release + ostrzeżenie, wiki), właściciel: naprawić i wydać pop-v2.

## Open Questions / Risks
- Formy nijakie 1./2. osoby (`przeczytałobym`, `-łoś`): 42 214 w POP, 13 807 w POP0 — rzadkie; decyzja o klasie form.
- Rozmiary po przycięciu: POP 51 805, POP0 13 181 leksemów; po naprawie G1 się zmienią.

## Wyniki
| sprawdzenie | wynik | najważniejsze |
|---|---|---|
| kompletność | ⚠️ | plan 102/102; spec i plan nie opisują rew. 2–3; INDEX.md bez ADR-006/007 |
| testy | ✅ (z implementacji) | 372 OK |
| przegląd kodu | ⚠️ 0/2/8 | W1 `pop --output-dir` wewnątrz przebiegu FROZEN nie jest odrzucany; W2 błędy SQLite/KeyError → traceback zamiast kodu 4 |
| pragmatyczny | ⚠️ 0/3/4 | podwójne zawężanie konfiguracji; martwa gałąź `members: all`; spec nieaktualna |
| gotowość wydania | ⚠️ GO z uwagami | „nie jest wydaniem” w LIMITATIONS; `SHA256SUMS` z plikami spoza zasobów |
| realność | ❌ | G1 High: brak częstych słów; G2: próbka bez warstwy „częste poza listą”; G3 rzadkie formy `-łoby-`; G4 rozmiary; G6 zdanie o serwerze nieaktualne (#1836) |
| licencja (właściciel) | do poprawy | `TERMS.md` POP: „wybór i układ CC BY 4.0” niezgodne z decyzją A → jak LL-PL |

## Do naprawy (pop-v2)
1. **Krytyczne:** warianty jednego lematu liczyć razem przy przycinaniu (G1) + twarda kontrola: top-N form KWJP w STANDARD (bez nazw własnych) muszą być w POP/POP0 + warstwa przeglądu „częste poza listą” (G2).
2. TERMS jak LL-PL (właściciel, 2026-10-11).
3. W1 blokada wyjścia w przebiegu/pakiecie; W2 mapowanie błędów na kod 4.
4. LIMITATIONS: bez „nie jest wydaniem”, aktualne zdanie o serwerze; `SHA256SUMS` wydania tylko dla zasobów (listy rozpakowane osobno).
5. Spec rew. 4, plan, INDEX.md, work-log.

Raporty: `completeness-check.md`, `code-review-report.md`, `pragmatic-review.md`, `production-readiness-report.md`, `reality-check.md`.
