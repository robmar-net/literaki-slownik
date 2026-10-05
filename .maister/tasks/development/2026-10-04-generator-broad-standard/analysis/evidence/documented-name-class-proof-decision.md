# Dowód klasy konkretnego członu nazwiska

## TL;DR
Użytkownik zatwierdził A — próg dowodu: czy jednoznaczny opis konkretnej formy przez autorów SGJP wystarcza do uzupełnienia brakującej klasy? Dokumentacja opisuje de i ibn jako człony nazwisk. Propozycja dotyczy tylko dokładnych analiz frag, nie całych napisów.

## Key Decisions
- Zatwierdzone A: opis autorów dotyczący konkretnej formy wystarcza do sklasyfikowania tej analizy jako członu nazwiska po ręcznym sprawdzeniu tożsamości. Stosujemy istniejące wyłączenie growe nazw; nie dodajemy reguły zakazującej kontekstu.
- Niewybrane B: wymagamy dodatkowego niezależnego dowodu; do tego czasu brakująca klasyfikacja pozostaje unresolved.
- Pierwszy zakres wdrożenia po A: tylko źródłowe de:F/frag oraz ibn/frag z przypiętego eksportu, zgodne z §7.12 dokumentacji. Nie aktywujemy kopii glos ani internetowej bazy metadanych. Pozostałe rekordy wymagają osobnej kontroli dowodów/mapowania i warunków źródeł.

## Open Questions / Risks
- Decyzja A zatwierdzona 2026-10-05T14:57:35Z; dokładny filtr wdrożony. Pełna macierz nadal otwarta.
- Dokumentacja nie jest kompletnym wykazem znaczeń. Odmowa może dotyczyć wyłącznie jednoznacznie przypisanej klasy; nie rozciągamy przykładu na niezweryfikowane ID lub inne homonimy.
- Publiczny odczyt internetowy pomógł przeglądowi, ale nie znosi nieustalonych warunków maszynowego użycia metadanych. Ten przyrost może oprzeć się na już audytowanej dokumentacji PDF i własnym mapowaniu, bez nowego wejścia.

## Dowód i przewidywany wpływ

[SGJP §7.12, s.138](https://sgjp.pl/static/pdf/Podstawy_teoretyczne_SGJP.pdf#page=138) jednoznacznie wskazuje de i ibn w funkcji członów nazwisk. Przypięte formy to de:F/frag/wiersz1463128 i ibn/frag/wiersz1960055, oba bez etykiety nazwy. Niezależny de:S/wiersz1463129 jest rzeczownikiem pospolitym. [Rejestr źródłowy](pan-semantic-cases.json); [adnotacje dokumentacji](pan-semantic-document-review.json).

A doda dwie odmowy growe w każdym wariancie. De:S nie otrzyma odmowy od tego warunku; ibn nie ma drugiej źródłowej analizy tego napisu w przypiętym eksporcie. Potencjalna strata klucza przez ten warunek wynosi więc jeden, ale nie jest to delta finalnej listy: pełna polityka pozostaje nierozstrzygnięta. Wpisy słownikowe zachowane. B nie doda tych odmów i pozostawi brak klasyfikacji.

## Powód pytania

[AGENTS.md](../../../../../AGENTS.md): „Decyzje zmieniające skład słownika lub kryteria dopuszczalności omawiamy z użytkownikiem przed ich wdrożeniem”. Ustalenie, jaki dowód pozwala uzupełnić brakującą klasyfikację grową, dotyczy tego wymogu. Nie zmieniamy zasad gry.

## Wdrożenie

Zatwierdzone A: jednoznaczny opis konkretnej formy przez autorów SGJP i ręcznie zweryfikowana tożsamość wystarczają do uzupełnienia klasy członu nazwiska. Wdrożono tylko de:F/frag i ibn/frag, ze strażnikami hasha, źródła, wiersza i pięciu pól. Wpisy i de:S zachowane; reguły gry niezmienione, metadane online nieaktywne.

Runtime v14 wymaga nowego build, nie przepisuje starych zapisanych ocen. Strażnik dodatkowo sprawdza SHA256 eksportu 3b2ee079143bc95186370fd528735779c4ba62f4ce14e30cf6622ceb566e9810. Źródłowe pięć pól pozostaje bez zmian; dokumentacyjna klasyfikacja jest odrębnym powodem growym. Nowych danych leksykalnych ani kopii glos nie dodano.
