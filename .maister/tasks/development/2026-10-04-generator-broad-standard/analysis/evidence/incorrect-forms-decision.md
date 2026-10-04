# Formy oznaczone jako niepoprawne — decyzja przed filtrem

## TL;DR
SGJP odróżnia niepopr. od niezal.; nie przenosimy decyzji o niezalecaniu na niepoprawność.
Zatwierdzony zakres obejmuje poprawne formy fleksyjne; otwarty wybór dotyczy sposobu wykorzystania jawnej oceny SGJP.
Filtr niepopr. nie został wdrożony. Wszystkie źródłowe wpisy pozostają w bazie i explain.

## Key Decisions
- Oceniana jest konkretna interpretacja, nie cały leksem ani wszystkie homonimy napisu.
- Potoczność, wulgarność, regionalność, gwarowość i rzadkość same nie odrzucają — to zatwierdzony zakres, wdrożony dla 15 dosłownych etykiet.
- Nie korzystamy z Wikisłownika ani podobnych źródeł; ich użycie użytkownik odłożył.

## Open Questions / Risks
- Czy jawne niepopr. w przypiętym SGJP wystarcza do odrzucenia tej interpretacji, czy wymagamy indywidualnego rozpatrzenia?
- Liczby ekspozycji nie są liczbą usuniętych słów; inne analizy napisu mogą pozostać dopuszczalne.
- Nieznane złożone etykiety nie mogą odziedziczyć odmowy przez luźny substring.

## Dowody i rzeczywisty przykład
[Oznaczenia SGJP](https://sgjp.pl/oznaczenia/) rozróżniają niepopr. (ocena niepoprawności) oraz niezal. (niezalecanie). Zatwierdzony prompt, §2.2–2.4, wymaga poprawnej fleksji, a nie wszystkich ciągów analizatora.

W SGJP 20260823 `abolicjoniźmie` dla leksemu `abolicjonizm` ma niepopr. w miejscowniku i wołaczu. `abolicjonizmie` tego samego leksemu ma te same przypadki bez tego oznaczenia. `kakaa` ma niezal., objęte osobną, już zatwierdzoną regułą niewykluczającą. To przykłady z przypiętych danych; brak etykiety nie dowodzi kompletnej kwalifikacji.

[Pełny przegląd](usage-incorrect-runtime.json) rozlicza 7 458 520 rekordów i 615 pól kwalifikatorów. Niepopr. występuje w 3 156 rekordach, 1 714 oryginalnych formach i 1 398 pełnych identyfikatorach leksemów. Zatwierdzone 15 niewykluczających etykiet zakresu użycia daje 288 034 rekordy ekspozycji. Są to rekordy kompaktowe, bez twierdzenia o utracie końcowych list.

## Warianty
**A — rekomendowany:** jawne niepopr. na sprawdzonej dosłownej etykiecie SGJP odrzuca tę interpretację w BROAD i STANDARD. Wpis zostaje w bazie; inna poprawna analiza tego napisu jest oceniana niezależnie. To wykonanie wymogu poprawnej fleksji na podstawie oceny przyjętego źródła.

**B:** samo niepopr. nie uruchamia automatycznej odmowy; każda taka interpretacja wymaga indywidualnego rozpatrzenia. Do czasu rozstrzygnięcia pozostaje unresolved, bez automatycznej akceptacji. Daje dodatkowy przegląd wiarygodności oceny źródła, ale wymaga większej pracy i nadal blokuje pełne wydanie przy istotnych niewiadomych.

Zasady gry i inne warunki nie zmieniają się w obu wariantach. Nie wprowadzamy listy niepoprawnych form dopuszczonych do gry.
