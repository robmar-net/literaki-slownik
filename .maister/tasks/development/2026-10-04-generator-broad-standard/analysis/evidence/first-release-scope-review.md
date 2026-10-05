# Zakres pierwszego wydania i źródłowe sekwencje by

## TL;DR
A zatwierdzone i wdrożone: zakres kontrakcji pierwszego wydania obejmuje 18 poświadczonych form (57 analiz), osiem innych (24 analizy) pozostaje diagnostycznie poza zakresem. Ocena językowa niewiadoma nie została zmieniona na błędność. Nowa warstwa release_scope jest oddzielna od języka, gry i profilu; członkostwo jest oceniane dla pojedynczej analizy, więc homonimy nie są tracone. Nie zmieniono kluczy ani treści utrwalonych kandydatów. Dodano zamknięte źródłowe sekwencje host+partykułowe by+(opcjonalna końcówka nwok), z pełnymi 2/3 składnikami i odrębną oceną pisowni normy2026.

## Key Decisions
- Osiem konstrukcji poza zakresem to wyłączenie śladów w pierwszym wydaniu, nie czarna lista napisów ani odmowa poprawności językowej.
- Release_scope jest dodatkowym warunkiem członkostwa, z osobną widoczną przyczyną w explain. Domyślna obecność w zakresie nie rozstrzyga poprawności/growego dopuszczenia.
- Nie zmieniamy payloadów kandydatów przy zmianie zakresu: można ponownie ocenić istniejący ślad bez utraty kandydatów i pochodzenia.
- Nieznana nowa kontrakcja pozostaje unresolved w zakresie; nie uzyskuje domyślnego excluded ani accepted.
- Źródłowa klasa by to partykuła. Analiza spójnikowego by nie jest dołączana jako ten operator. Z_aglt_nwok2 nie pozwala dołączać by.
- Norma2026 odrzuca tę konkretną składaną analizę w STANDARD; niezależne źródłowe wyrazy i inne analizy mają odrębne oceny. W BROAD sama udokumentowana dawna konstrukcja nie wyklucza.

## Open Questions / Risks
- Pełna polityka kategorii i kwalifikatorów, raporty/verify/export oraz dwa pełne przebiegi nadal wymagają domknięcia.
- Dodatnia ocena pojedynczego warunku nie jest accept dla całej analizy lub listy.
- Zawężenie jednej klasy nie wyłącza innych wymaganych części planu.

## Test-first i rzeczywiste dane

Trzy testy zakresu miały rzeczywisty red: brak argumentu scope_checks, brak reguły release_scope_checks i brak warstwy w explain. Test integracji sprawdza także raport build (kandydat wewnątrz i poza zakresem) oraz homonim. Dwa testy sekwencji by miały red: brak konstruktora i brak osiągalnej rekonstrukcji w explain; po implementacji green.

[Runtime zakresu](first-release-scope-runtime.json) odczytuje pełną projekcję klasy przyimkowej readonly: 57 analiz w zakresie, 24 poza zakresem, osiem napisów, zero nieznanego zakresu; dwa raporty identyczne, total_changes=0. Czternaście rzeczywistych zapytań pełnego G2 zachowuje dowody i wpisy, rozdziela język od zakresu oraz pokazuje nowe sekwencje by. To nie pełny wynik G8 ani wydanie.
