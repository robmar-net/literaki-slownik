# Formy oznaczone jako niepoprawne — decyzja przed filtrem

## TL;DR
SGJP odróżnia niepopr. od niezal.; nie przenosimy decyzji o niezalecaniu na niepoprawność.
Użytkownik zatwierdził A: jawna ocena niepoprawności SGJP odrzuca konkretną interpretację w obu wariantach.
Filtr niepopr. wdrożono dla 27 sprawdzonych dosłownych etykiet. Wszystkie źródłowe wpisy pozostają w bazie i explain.

## Key Decisions
- Oceniana jest konkretna interpretacja, nie cały leksem ani wszystkie homonimy napisu.
- Potoczność, wulgarność, regionalność, gwarowość i rzadkość same nie odrzucają — to zatwierdzony zakres, wdrożony dla 15 dosłownych etykiet.
- Nie korzystamy z Wikisłownika ani podobnych źródeł; ich użycie użytkownik odłożył.

## Open Questions / Risks
- Rozstrzygnięte A: jawna, sprawdzona etykieta wystarcza do odrzucenia konkretnej interpretacji; pełne listy nadal wymagają pozostałych warunków.
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

## Zatwierdzenie A i wykonanie

`incorrect_checks` korzysta z zamkniętej mapy 27 dosłownych etykiet, bez substring runtime i bez przenoszenia oceny niezal. Niepoprawność jest odrębną przyczyną reject w BROAD i STANDARD; nie usuwa wpisu ani poprawnego homonimu.

[Runtime po wdrożeniu](incorrect-runtime.json): wszystkie 7 458 520 rekordów rozliczone, 3 156 analiz niepoprawnych. Dla 1 714 objętych kluczy wczytano wszystkie 3 303 importowane analizy. Sam filtr odrzuca komplet analiz 1 618 kluczy; 96 kluczy ma inne analizy, bez automatycznej obietnicy accept. Łącznie ze znanymi warunkami gry/profilu odrzucony komplet dotyczy 1 625 kluczy tej populacji. Nie jest to delta końcowego wydania; konstrukcje i pełna polityka nadal nieukończone. Odczyt readonly, 9,223 s, total_changes=0.
