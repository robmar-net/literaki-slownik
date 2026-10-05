# Oznaczenia bez objaśnień i logiczna treść bazy

## TL;DR
Wdrożono A dla25dosłownych oznaczeń bez pełnego objaśnienia: source_label zachowany, gloss_status=unestablished, inne kryteria osobno. Pełny runtime:1908kompaktowych analiz, dwa identyczne raporty, sześć readonly explain; wielka litera Abchaz nadal odrzuca growo. Dodano logical-content bieżącego schematu do build:10zamkniętych relacji, klucze źródłowe zamiast ID, wykrywanie nowych tabel/kolumn i niespójnych FK. Testy potwierdzają identyczność po zmianie ID i zmianę hasha po modyfikacji powiązań/kwalifikatorów. To nie pełny indeks kanoniczny ani odbiór G8.

## Key Decisions
- Nie udajemy, że poznaliśmy znaczenia oznaczeń: to zatwierdzony wyjątek wymagania pierwszego wydania.
- Hash logiczny obejmuje wszystkie tabele i kolumny bieżącego schematu. Każda nowa relacja wymaga jawnego rozszerzenia kontraktu; nie zostanie pominięta.
- Techniczne ID zostają zastąpione tożsamością źródła/wiersza/lematu/zapisu/kandydata. Wyłączone są tylko deklarowane lokalizatory źródeł i czas ich pozyskania.
- Nowy raport nie kończy etapu reports ani nie promuje INCOMPLETE do VERIFIED.

## Open Questions / Risks
- Pełna kwalifikacja, utrwalone decyzje, cały indeks kanoniczny i pełne G8 pozostają niewykonane.
- Adnotacja akcent nie należała do listy25; dwa źródłowe rekordy wymagają osobnego rozstrzygnięcia wymogu, zachowując już zatwierdzoną dawność.

## Dowody

- [Pełne pokrycie po A](unexplained-labels-condition-coverage.json) i [runtime](unexplained-labels-runtime.json); wcześniejszych raportów nie nadpisano.
- [Readonly hash rzeczywistej projekcji](logical-content-projection-runtime.json):770kandydatów i1784składniki, identyczny raport dwa razy, zero zapisów. To pełne wejście wdrożonych konstruktorów poza impt, nie pełny słownik.
- Test-first4warunki/raport/explain i3logical-content: rzeczywiste błędy braku funkcji/rejestru/pliku raportu → green. Pierwsza fikstura testu linków nie zawierała KWJP; dodano własny rekord i relację, aby kontrola zmiany informacji o linku dotyczyła istniejących danych.
- Generator134/134 i baseline audytu5/5 przeszły. Preflight14/14artefaktów i10konfiguracji poprawny; po zmianach metadanych powtarzamy preflight.

## Kodowanie logical-content

Każda logiczna relacja ma oddzielny licznik i SHA256 strumienia uporządkowanych tablic JSON (UTF-8, LF, sortowanie kluczy obiektów). Zbiorczy SHA256 wiąże nazwy tabel, liczby wierszy i hashe. Źródłowe duplikaty pozostają osobnymi wierszami; oryginały, surowe tagi, kwalifikatory, payloady kandydatów i wartości miar pozostają uwzględnione. Metadane licencji/hash/wersji/URL i hashe dowodów są uwzględnione. Dokładna lista wyłączonych lokalizatorów jest w raporcie. Nie hashujemy fizycznych bajtów SQLite jako testu równoważności.
