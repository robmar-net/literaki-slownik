# Ortografia i dopuszczalność gry

## TL;DR
Norma pisowni, reguła gry i profil płytek są osobnymi ocenami.
Zachowujemy źródłowy zapis; normalizacja nie jest świadectwem dopuszczalności.
Nie zmieniamy zasad działającej gry.

## Key Decisions
- BROAD i STANDARD mają wspólny filtr growy oraz odrębny zakres językowy.
- NFC/lower służy wyszukiwaniu i agregacji; nie usuwa obowiązkowej wielkiej litery.
- Nie przepisujemy dawnej formy na nową i nie tworzymy nowych leksemów przez dopisanie `nie`.

## Open Questions / Risks
- Zgodność wszystkich kwalifikatorów historycznej pisowni pozostaje nieukończona.
- Odczyt ZDS nie jest zgodą na automatyczne przyjęcie wszystkich aktualnych wymagań źródłowych jako nowej polityki projektu.

[Zasady RJP](https://rjp.pan.pl/app/uploads/2025/11/2-zalacznik-do-komunikatu-11-25-wersja-jednolita.pdf), §4.4.4, §4.5 i §4.6, rozróżniają kontrakcje, pisownię operatora warunkowego i partykuły. Podwojenie partykuły może być zgodne z pisownią, a mimo to wykluczone growo. Przy winien/powinien operator warunkowy zapisuje się osobno. Nie dopisujemy sklejonych form do generatora.

[ZDS](https://sjp.pl/sl/dp.phtml) przeczytano na wyraźne zlecenie jako referencję reguł, bez list słów i benchmarku. Ogranicza klasy i krotność dołączeń oraz wymaga opracowania słownikowego całych kontrakcji przyimkowych. Ma także osobne wymagania dotyczące źródeł haseł. Nie wolno zastąpić ich częstością korpusową ani samym wynikiem analizatora. Zakres wiążący w projekcie wymaga uzgodnienia z dokumentacją gry i zatwierdzonym G1/N1/C1; witryna nie jest automatyczną aktualizacją zasad.

Alfabet 32 liter i długość 2–15 pozostają w `config/generator/profile.json`. Oryginały spoza profilu pozostają w bazie. Próba PCV może jednocześnie naruszać pisownię grową i alfabet; obie przyczyny muszą pozostać widoczne.

## Zatwierdzona norma 2026

Wdrożono A dla normy 2026: dokładne analizy comp jeśliby/jeżeliby i ich składniki konstrukcyjne mają odrzucenie STANDARD; BROAD nie wyklucza przez samą dawną pisownię. Nie usunięto wpisów i nie zmieniono reguł gry. Dodano kandydatów mobilnych końcówek dla trzech pozostałych zamkniętych klas, z kontrolą lematu, POS, wokaliczności, źródła i śladów. Odmienne formy niezgodne z wariantem źródłowej klasy wymagają dalszej oceny; pełna macierz i kwalifikacja nadal otwarte.

## Adnotacja akcent i klasy źródłowe gry — bieżący przyrost

Zatwierdzone A dla adnotacji akcent wdrożono bez zmiany dawności: BROAD nie wyklucza przez brak objaśnienia, STANDARD odrzuca dwie analizy daw.,rzad.,akcent. Pełny raport 7 458 520 analiz zachowuje 26 nieobjaśnionych oznaczeń w 1910 analizach. Dodano diagnostyczne warunki klas źródłowych gry: nazwy, brev, niesamodzielne segmenty oraz odrębną ocenę całości konstrukcji. Nowa zamknięta klasa ja/ty/my/wy/wszyscy zachowuje sześć kandydatów i growe odrzucenie tych analiz, bez usuwania homonimów. Pozostałe mobilne hosty i sekwencje by oceniono zgodnie z zachowanymi wyłączeniami gry; byle ma udokumentowany wyjątek. Pełna kwalifikacja i wydanie nadal nieukończone.

[Przegląd i dowody](../../.maister/tasks/development/2026-10-04-generator-broad-standard/analysis/evidence/accent-and-source-game-review.md).

## Wspólna norma growa2026 — zatwierdzone A

Obowiązkową wielką literę oceniamy według normy2026 w obu wariantach, również dla dawnych zapisów zachowanych językowo w BROAD. Pierwszy udokumentowany podzbiór: warszawianin, warszawiak, krakowiak:Sm1, subst:m1/depr:m2. STANDARD odrzuca dawny lowercase językowo; BROAD zachowuje go jako niewykluczający przez samą historię, lecz ta interpretacja odpada growo. Wpisy pozostają w bazie. Krakowiak:Sm2 jako taniec oceniany osobno. Nie wyznaczamy klasy po sufiksie/m1; pełna inwentaryzacja wymaga dalszych danych i dowodów. [Rozstrzygnięcie](../../.maister/tasks/development/2026-10-04-generator-broad-standard/analysis/evidence/game-capitalization-norm-decision.md); [runtime](../../.maister/tasks/development/2026-10-04-generator-broad-standard/analysis/evidence/capital-double-review.md).

## Dalszy przegląd mieszkańców i etnonimów

RJP §8.1.2 pkt3 obejmuje także wsie, osiedla i dzielnice. Odrębna uwaga pkt4 dopuszcza małą literę dla jawnych nieoficjalnych nazw etnicznych; nie rozszerzamy tego na wszystkie nazwy. SGJP nie ma małych angol/jugol, ma tylko dokładne Angol/Jugol. Projekt osobnych kandydatów pisowni czeka na decyzję; źródłowych zapisów nie zmieniono. Pełny raport83 ID z etn. nie jest kompletną klasą mieszkańców — dwie wskazane nazwy kobiet nie mają etn. Brak nowych aktywnych filtrów.
