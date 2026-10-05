# Dokumentacja projektu

## TL;DR
Audyt i projekt pierwszego generatora są zakończone oraz zatwierdzone.
Specyfikacja v3 jest materiałem wejściowym użytkownika, nie raportem wyników.

## Key Decisions
- Dokumenty i proces Maister są wersjonowane w tym repozytorium.
- Zasady językowe i publikacji opisuje `../../AGENTS.md`.

## Dokumenty
- [Specyfikacja v3](../../docs/literaki-niezalezne-slowniki-prompt-v3.md) — rozdział 15 wyznacza bieżący zakres.
- [Prosty język i minimum leksykalne](../../docs/literaki-prosty-jezyk-minimum-leksykalne-kierunki.md) — publiczna notatka użytkownika v1.0, 2026-10-04, skopiowana bez zmian z Downloads; przyszłe słowniki znajomości. Opisane zewnętrzne dane nie są zatwierdzone, pozostają BLOCKED i nie zmieniają bieżącego zakresu.
- [Zasady pracy](../../AGENTS.md).

- [Raport końcowy i przekazanie](../tasks/research/2026-10-04-audyt-zrodel-polskich-slownikow/outputs/research-handoff.md).
- [Implementacja generatora — zakres i luki](../tasks/development/2026-10-04-generator-broad-standard/analysis/gap-analysis.md) — aktywne zadanie development.
- [Specyfikacja generatora](../tasks/development/2026-10-04-generator-broad-standard/implementation/spec.md) — zatwierdzona przez użytkownika.
- [Plan implementacji generatora](../tasks/development/2026-10-04-generator-broad-standard/implementation/implementation-plan.md) — zatwierdzony, G1/G2 wykonane, G3/G4/G5/G6 częściowe.
- [Etykiety generatora](../../docs/generator/etykiety.md) — pełna inwentaryzacja i otwarte kwestie semantyki.
- [Konstrukcje i fleksja](../../docs/generator/konstrukcje.md) — dowody, kontrola nadgeneracji, macierz klas.
- [Ortografia](../../docs/generator/ortografia.md) — rozdzielenie języka, gry i profilu.
- [Mapowanie KWJP](../../docs/generator/mapowanie-kwjp.md) — pełny wynik lemma-all i kontrakt powiązań.
- [Decyzja o dodatkowych wejściach](../tasks/development/2026-10-04-generator-broad-standard/analysis/evidence/source-extension-decision.md) — bramka rozszerzenia dowodów, bez zmiany reguł gry.

- [Bieżące CLI generatora](../../docs/generator/cli.md) — import i diagnostyczne explain; pełna polityka, konstrukcje i wydanie pozostają nieukończone.
- [Dobór próbek jakości](../../docs/generator/jakosc.md) — mechanika quality-v1 i szablon przeglądu; integracja z pełnymi raportami pozostaje nieukończona.
- [Sprostowanie polityki źródeł](../tasks/development/2026-10-04-generator-broad-standard/analysis/evidence/source-policy-clarification.md) — brak automatycznego przejęcia ograniczeń źródeł SJP.pl; decyzje zmieniające skład list omawiamy przed wdrożeniem.

- [Raport wpływu filtrów](../../docs/generator/raporty.md) — strumieniowe efekty samodzielne/kolejne/łączne; bez deklaracji pełnego wydania.

- [Odroczenie źródeł społecznościowych](../tasks/development/2026-10-04-generator-broad-standard/analysis/evidence/wiktionary-attestation-decision.md) — decyzja użytkownika: Wikisłownik i podobne źródła dopiero później; obecne dane bez ich użycia.

- [Ocena niepoprawności SGJP](../tasks/development/2026-10-04-generator-broad-standard/analysis/evidence/incorrect-forms-decision.md) — zatwierdzone A i wdrożony filtr konkretnych interpretacji, odrębny od niezalecania.

- [Wymagania kontekstu](../tasks/development/2026-10-04-generator-broad-standard/analysis/evidence/context-restrictions-decision.md) — zatwierdzone A, 11 etykiet i pełny runtime warunku kontekstu.

- [Pełne pokrycie warunków kwalifikatorów](../tasks/development/2026-10-04-generator-broad-standard/analysis/evidence/qualifier-coverage-review.md) — raport nowych build, ekspozycja luk i granice częściowej oceny.

- [Utrwalanie konstrukcji](../tasks/development/2026-10-04-generator-broad-standard/analysis/evidence/persisted-constructions-review.md) — dwa potwierdzone rodzaje, rozliczenie klas i zgodność wcześniejszych baz.

- [KWJP w build](../tasks/development/2026-10-04-generator-broad-standard/analysis/evidence/build-links-integration-review.md) — relacje bezpośrednie; pełny etap pending.
- [Dowody kontrakcji](../tasks/development/2026-10-04-generator-broad-standard/analysis/evidence/contraction-proof-decision.md) — konieczna decyzja użytkownika przed nowym warunkiem.

- [Kontrakcje, mobilne by i korpus](../tasks/development/2026-10-04-generator-broad-standard/analysis/evidence/constructions-links-review.md) — wdrożoneA,57/24analizy przyimkowe,64mobilne by,7errat winien; pełny zakres nadal otwarty.

- [Warunki publikacji](../../docs/generator/publikacja.md) — zatwierdzony wariant A, zakres własnych materiałów i atrybucje źródeł.

- [Norma 2026 a nieoznaczone dawne zapisy](../tasks/development/2026-10-04-generator-broad-standard/analysis/evidence/orthography-2026-decision.md) — konieczny wybór przed aktywacją kwalifikacji.

- [Norma i mobilne klasy](../tasks/development/2026-10-04-generator-broad-standard/analysis/evidence/norm-mobile-review.md) — wdrożenie A, rzeczywiste kontrolne przebiegi i ograniczenia.
- [Zakres niepoświadczonych kontrakcji](../tasks/development/2026-10-04-generator-broad-standard/analysis/evidence/remaining-contractions-scope-decision.md) — zatwierdzone A: 18 form w pierwszym wydaniu, osiem zachowanych poza zakresem, odwracalna osobna warstwa oceny.

- [Kontrola zakresu i sekwencji by](../tasks/development/2026-10-04-generator-broad-standard/analysis/evidence/first-release-scope-review.md) — 127/127 testów generatora, powtarzalny runtime 770 kandydatów poza impt; pełny etap nadal otwarty.
- [Oznaczenia bez pełnego objaśnienia](../tasks/development/2026-10-04-generator-broad-standard/analysis/evidence/unexplained-labels-first-release-decision.md) — zatwierdzone A i wdrożone; objaśnienia nadal nieustalone, 1908 analiz źródłowych, inne kryteria obowiązują.

- [A25 i logiczna treść](../tasks/development/2026-10-04-generator-broad-standard/analysis/evidence/unexplained-and-logical-content-review.md) — 134/134 testów, pełne pokrycie i diagnostyczny hash bieżących relacji.
- [Adnotacja akcent](../tasks/development/2026-10-04-generator-broad-standard/analysis/evidence/accent-gloss-first-release-decision.md) — zatwierdzone A, zachowana adnotacja i osobne odrzucenie STANDARD za dawność.

- [Akcent i klasy źródłowe gry](../tasks/development/2026-10-04-generator-broad-standard/analysis/evidence/accent-and-source-game-review.md) — 142 testy, pełny runtime klas i sześć konstrukcji osobowych bez utraty homonimów.

- [Utrwalone analizy i powody ocen](../tasks/development/2026-10-04-generator-broad-standard/analysis/evidence/persisted-assessments-review.md) — schema2, idempotencja, pełne rozwinięcia, bez ukończonego wydania.
- [Norma odniesienia wielkiej litery w grze](../tasks/development/2026-10-04-generator-broad-standard/analysis/evidence/game-capitalization-norm-decision.md) — wymagana decyzja przed filtrem dawnych zapisów BROAD.
