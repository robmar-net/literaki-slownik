# Audyt specyfikacji generatora

## TL;DR

Werdykt: passed_with_issues — brak blokad przygotowania planu, trzy doprecyzowania techniczne.
Wymagania R01–R12 i odbiór K1–K10 są osiągalne przez opisany przebieg CLI.
Nie zmieniono zatwierdzonej specyfikacji ani kodu podczas audytu.
Nierozstrzygnięte reguły językowe pozostają obowiązkowymi zadaniami, nie wyłączeniami zakresu.

## Key Decisions

- Plan musi zawierać dowody językowe, przegląd jakości oraz dwa pełne przebiegi, oprócz kodu.
- Doprecyzowania I1–I3 mają być jawnie włączone do planu do zatwierdzenia; nie zmieniają G1/N1/C1.
- Brak zainstalowanego specjalisty: audyt wykonany przez koordynatora według maister-reviews-spec-audit.

## Open Questions / Risks

- Semantyka etykiet, kompletność klas i warunki publikacji pozostają blokadami pełnego wydania do czasu domknięcia dowodów.
- Wykonalność budżetów pamięci/czasu potwierdzi rzeczywisty pomiar; nie ma dziś dowodu osiągnięcia limitów.

## Materiał i metoda

Przeczytano pełną [specyfikację](../implementation/spec.md), [wymagania](../analysis/requirements.md), analizy [kodu](../analysis/codebase-analysis.md) i [luk](../analysis/gap-analysis.md), zatwierdzony projekt oraz reguły AGENTS. Zweryfikowano docelowe przepływy względem skryptów audytu, zwłaszcza testów homonimii i pilota KWJP: statyczne ścieżki wyjściowe nie nadają się do nowego build, a kandydat lemma/POS nie jest pewnym przypisaniem sensu.

Nie ma lokalnych standardów ani szablonów specialist agents; brak potwierdzony rg w poprzedniej fazie. Audyt jest oceną dokumentów, bez uruchamiania pełnego importu lub zmiany istniejących wyników.

## Sprawdzone obszary

| Obszar | Sekcje specyfikacji | Ocena |
|---|---|---|
| Problem, role, granice | §1–2 | Jasne; lokalny operator/recenzent, bez usługi |
| Wejścia, izolacja, uprawnienia | §3–4 | Jawne artefakty/role/hash; BLOCKED i benchmark odrzucone |
| Reguły, fleksja, konstrukcje | §5–6 | Pełny zakres i dowody; nieznane klasy nie mogą być pominięte |
| KWJP i braki | §7 | Jednostki i miary odrębne, brak kopiowania F i imputacji zera |
| Osiągalność zachowania | §8 | Każda funkcja dostępna przez komendę i pełny przebieg |
| Błędy i lifecycle | §9 | Etapy a gotowość osobno; przerwanie nie udaje sukcesu |
| Powtarzalność i przegląd | §10 | Próbka określona przed pomiarem, kanoniczne wyniki i dwa build |
| Testowalny odbiór | §11 | Każde K wskazuje dowód automatyczny lub przeglądowy |
| Dokumentacja, rollout, rollback | §12 | Instrukcja i nowe wydania; bez wdrożenia do gry i nadpisywania |

## Doprecyzowania do planu

| ID / poziom | Miejsce i wpływ | Dokładne rozstrzygnięcie wykonawcze |
|---|---|---|
| I1 / info | §8, §11, K10: verify poprzedza fizyczny pakiet export | Verify ocenia przygotowane listy/raporty/atrybucje i plan pakietu w katalogu roboczym; export materializuje te same zweryfikowane bajty i hashe. Test odrzuca rozbieżność. Nie ma wymogu istniejącego zamrożonego pakietu przed verify. |
| I2 / info | §10, K8: trzeba jednoznacznie wskazać, co podlega porównaniu | Plik canonical-index.json wylicza hashe list roboczych i raportów merytorycznych. Czas, RSS, ścieżki lokalne, logi, verdict i fizyczna baza są poza porównaniem. Dane językowe, decyzje, pochodzenie, linki i dobór próbki są w porównaniu. |
| I3 / info | §10, K9: łączenie seed/warstwa/klucz może być niejednoznaczne | Haszować UTF-8 kanonicznej tablicy JSON [seed, warstwa, klucz], bez spacji; remis SHA256 rozstrzyga kanoniczny klucz. Zachować tę metodę w quality-v1 i testach. |

I1–I3 uszczegóławiają istniejące kontrakty; nie wymagają rezygnacji z kryterium ani nowego źródła. Wprowadzenie innej definicji kompletności, pominięcie klasy lub nadanie unknown akceptacji byłoby zmianą materialną wymagającą decyzji użytkownika.

## Werdykt i minimum przed wykonaniem

`passed_with_issues`: critical=0, warning=0, info=3. Można przygotować plan, który zawiera I1–I3 oraz pokrycie R/K, pliki, odpowiedzialność, test-first i dowody. Jego zatwierdzenie jest wymagane przed implementacją. Ten audyt nie potwierdza gotowości reguł językowych ani ukończenia generatora.
