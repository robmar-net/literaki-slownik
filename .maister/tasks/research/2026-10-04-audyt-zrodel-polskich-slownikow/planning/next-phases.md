# Dalsze fazy po zatwierdzeniu audytu

## TL;DR
Użytkownik zatwierdził przejście dalej po raporcie słowami „idzmy dalej”.
Faza badawcza jest zakończona; jej artefakty i sumy kontrolne zweryfikowano przy wznowieniu.
Rekomendujemy porównanie wariantów, a następnie projekt pierwszego generatora.
Włączenie każdej z tych dwóch opcjonalnych faz wymaga osobnej decyzji w procesie Maister.

## Key Decisions
- Akceptacja audytu potwierdza podstawę dalszych decyzji, nie zatwierdza automatycznie wszystkich scenariuszy filtrów.
- Nie powtarzamy pomiarów ani uzgodnień rozdziału 2 specyfikacji bez nowego powodu.
- Raport i manifest zachowują postać zamrożonego materiału z commita `6137e23`; aktualny status zatwierdzenia zapisują stan zadania i dziennik.

## Open Questions / Risks
- Czy włączyć porównanie wariantów (brainstorming i późniejszy wybór)? Rekomendacja: tak.
- Czy włączyć projekt wysokiego poziomu po rozstrzygnięciu potrzebnych decyzji? Rekomendacja: tak.
- NKJP pozostaje BLOCKED do konstrukcji do czasu uzyskania dowodów dotyczących warunków; wybór dalszej ścieżki nie znosi tej blokady.

## 1. Porównanie wariantów i wybór — rekomendowane

Audyt ujawnił kilka obszarów, w których istnieją różne sposoby postępowania. Porównanie powinno dotyczyć wyłącznie tych nowych niejednoznaczności:

| Obszar | Dlaczego potrzebne jest porównanie | Dowód |
|---|---|---|
| Formy złożone z segmentów | Pełne formy osobowe już istnieją, ale konstrukcje typu `bym`, `przezeń`, `czytajże` wymagają odrębnego rozpatrzenia; swobodne składanie nadgeneruje | [Reguły SGJP](../analysis/findings/sgjp-rules.md) |
| Kwalifikatory i skrótowce | Przesiew policzył wpływ ostrożnego wariantu, lecz nie rozstrzygnął semantyki mieszanych etykiet i całej polityki pisowni | [Raport](../outputs/research-report.md) |
| Kolejność prac przy blokadzie NKJP | Potrzebna jest jasna zależność między wyjaśnieniem warunków a możliwością przygotowania części generatora na SGJP/KWJP | [Audyt NKJP](../analysis/findings/nkjp-audit.md) |
| Zakres pierwszego generatora | Należy odróżnić pierwszy sprawdzalny proces importu i kwalifikowania od późniejszych modeli znajomości, tematów i benchmarku | [Model procesu](../analysis/findings/model-procesu.md) |

Wynik: `outputs/solution-exploration.md` z porównaniem istotnie różnych podejść, ograniczeniami i rekomendacją. Potem osobne, sekwencyjne decyzje użytkownika tylko tam, gdzie pozostaje rzeczywisty wybór. Nie przyjmujemy żadnego wariantu przez sam fakt uruchomienia tej fazy.

Pominięcie jest możliwe: audyt staje się materiałem do kolejnego zadania, a powyższe decyzje pozostają jawnie otwarte. Nie wolno po pominięciu traktować ich jako rozstrzygniętych.

## 2. Projekt pierwszego generatora — rekomendowany

Audyt dostarczył szkic modelu danych, lecz jeszcze nie kompletny projekt przepływu od pobrania źródła do wyjaśnialnego, odtwarzalnego wydania. Projekt powinien doprecyzować:

- granice pobierania i importu, dozwolone role źródeł oraz blokowanie niedopuszczonych wejść;
- bazę form i interpretacji, decyzje filtrów, powiązania korpusowe i zapytanie o przyczynę przyjęcia/odrzucenia;
- przebieg lokalnych poleceń, manifesty, walidację, powtarzalność i obsługę nieudanego przebiegu;
- kryteria zakończenia pierwszej implementacji, pakiet atrybucji i sposób publikowania wyników;
- odroczenie modeli znajomości, tematów i benchmarku do właściwych etapów.

Wynik: `outputs/high-level-design.md` oraz `outputs/decision-log.md`, oparte na dowodach i rozstrzygniętych wariantach. Projekt ma własną bramkę zatwierdzenia. Nie oznacza uruchomienia implementacji, zmiany słownika działającej gry ani rozpoczęcia benchmarku.

Pominięcie jest możliwe: przekazujemy audyt i ewentualnie wybrane warianty do późniejszego zadania projektowego/implementacyjnego. Pozostają brakujące kontrakty przepływu i obsługi błędów.

## Decyzje do zapisania niezależnie

1. Porównanie wariantów: **tak (rekomendowane)** / nie.
2. Projekt wysokiego poziomu: **tak (rekomendowane)** / nie.

Można wybrać każdą kombinację. Obie decyzje dotyczą dalszych faz badawczo-projektowych; implementacja pozostaje osobnym zadaniem.
