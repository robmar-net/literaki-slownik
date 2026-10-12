# Luki i zakres: tymczasowa stabilizacja POP (#6)

## TL;DR

Obecny limit 60 000 wypycha 2430 dotychczasowych form POP w badanej propozycji +2382 STANDARD.
Stały próg dzisiejszego cięcia wraz z przycinaniem według własnej punktacji daje w tej symulacji identyczny POP bazowy oraz +2372/0 po dodatkach.
POP0 może zachować metodę i skład; trzeba jawnie sprawdzić zawieranie POP0 w POP.
Zakres dodatków STANDARD z #4 oraz cofnięć wymaga oddzielnego rozstrzygnięcia; docelowa granica popularności pozostaje otwarta.

## Key Decisions

- Tymczasowy cel: stabilność składu POP względem zajmowania miejsc przez nowe leksemy. Stały próg pochodzi z obecnego cięcia, nie z nowej definicji popularności.
- Zmiana selekcji POP nie zmienia oceny językowej STANDARD, źródeł, miary D3, grup D5 ani progów POP0.
- Nowa metoda ma być wersjonowana, jawna w raporcie i odtwarzalna z pinów wejść oraz hashów.

## Open Questions / Risks

- Czy pilne poprawki w tym kroku obejmują zatwierdzenie +2382 form w STANDARD z #4? Pytanie zostało skierowane do właściciela. Osiem cofnięć badano oddzielnie i nie należy ich domniemywać.
- Jeśli zmiana źródeł lub grupowania złamie `POP0 ⊆ POP`, generator ma przerwać budowę, a nie ukryć naruszenie.
- Próg nie rozstrzyga słów z własnym współczesnym użyciem, których obecna miara nie promuje. Powrót do merytorycznej granicy jest osobnym otwartym punktem #6.

## Stan obecny i pożądany

| Obszar | Teraz | Cel tymczasowy |
| --- | --- | --- |
| Wybór jednostek POP | Prefiks rankingu do 60 000 leksemów przed przycięciem | Wynik punktowy co najmniej stała wartość z dzisiejszego cięcia |
| Członkowie grup POP | Własna ranga nie większa niż ranga progu; wyjątki głowy i braku osobnego dowodu | Własna punktacja co najmniej próg; te same wyjątki |
| POP0 | Limit 20 000 i przycinanie własną rangą | Bez zmiany |
| STANDARD | Wydany v29 | Osobne rozstrzygnięcie #4 |
| Pakiet i diagnostyka | `pop-v2`, limit liczbowy | Nowa wersja metody, raport progu, trafne wyjaśnienie wyboru |

## Punkty integracji i pełny obieg

Operator uruchamia `pop` na zamrożonym przebiegu LL-PL i przypiętym STANDARD. Konfiguracja przechodzi walidację; jednostki i członkowie otrzymują punktację; generator wybiera, sprawdza warunki, zapisuje pakiet i raport. Operator porównuje pełne listy oraz próbkę, weryfikuje pakiet niezależnym skryptem i aktualizuje ADR, CLI oraz wiki. Wydanie i użycie przez grę pozostają osobnym krokiem. Diagnostyka `explain` ma uzasadniać wynik według nowej metody, bez pokazywania mylącej granicy rangi dla POP.

## Charakterystyka

- has_reproducible_defect: false — to świadoma zmiana metody, nie izolowana usterka.
- modifies_existing: true; new_capability: false; data_operations: true (nowy pakiet, bez modyfikacji wejść).
- ui_heavy: false; risk_level: high (skład słownika i wersjonowanie).
- TDD red: pomijamy, bo nie naprawiamy pojedynczego reprodukowalnego defektu; plan powinien zawierać testy przed kodem.
- UI mockups i E2E przeglądarkowe: nie dotyczą generatora CLI; weryfikacja dotyczy pełnych zbiorów i pakietu.

## Decyzja zakresu

Rekomendowany zakres po potwierdzeniu: w jednym kroku wdrożyć stały próg POP oraz zatwierdzone dodatki STANDARD, osobno zostawiając osiem cofnięć. Umożliwi to sprawdzenie dokładnego wyniku +2372/0 na rzeczywistym buildzie. Alternatywa: wdrożyć najpierw wyłącznie POP; porównanie +2382 pozostanie wtedy symulacją. Nie rozszerzać tego kroku na docelową kalibrację progu ani wydanie.
