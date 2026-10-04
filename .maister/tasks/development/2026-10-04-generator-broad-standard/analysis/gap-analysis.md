# Zakres implementacji i luki do domknięcia

## TL;DR

Zakres zachowuje zatwierdzony cel G1: pełne BROAD i STANDARD, nie pilot jako wynik końcowy.
Implementacja obejmuje lokalne CLI, SQLite, źródła, kwalifikację, konstrukcje, KWJP, explain, verify i export.
Do prac trzeba włączyć uzupełnienie dowodów językowych i macierzy kompletności, nie tylko kod.
Znane niewiadome wpływające na skład list blokują końcowe wydanie zgodnie z K4/K5.

## Key Decisions

- G1/N1/C1 i Python/SQLite są już zatwierdzone; nie otwieramy tych wyborów ponownie.
- Istniejące pomiary pozostają dowodami audytu, a nowe przebiegi mają własne katalogi i manifesty.
- Zgoda „wykonaj implementacje tej fazy” upoważnia do nowego zadania development. Jego wymagane bramki dotyczą konkretnej specyfikacji i planu.

## Open Questions / Risks

- Brak finalnej semantyki wszystkich mieszanych etykiet i kategorii skrótowców; nie rozstrzygamy tego arbitralnym filtrem.
- Nie wykazano pełnej macierzy fleksji/konstrukcji ani ich ograniczeń i dziedziczenia kwalifikacji.
- Własne warunki publikacji oraz rzeczywiste koszty pełnego przebiegu muszą być ustalone przed wydaniem.

## 1. Stan obecny i oczekiwany

Obecnie operator może odtworzyć audyt, ale nie ma narzędzia budującego wyjaśnialny, kontrolowany pakiet kandydatów. Oczekiwany przebieg: kontrola jawnych wejść → import → rekonstrukcje/ocena → powiązania korpusowe → verify → export. Explain jest dostępny dla wskazanej bazy i wersji polityki.

| Obszar | Luka wykonawcza | Zakres tej implementacji |
|---|---|---|
| Wejścia | Audyt ma rejestry, brak wspólnej kontroli generatora | Manifest, status/rola/hash, zawiadomienia; odmowa źródła BLOCKED lub benchmark |
| Import i dane | Brak bazy i wspólnych parserów | SQLite, oryginalne zapisy, numery rekordów, pełne ID, walidacja i rozliczenie importu |
| Reguły | Przesiew audytu nie jest normą | Wersjonowany rejestr reguł z dowodami; accept/reject/unresolved dla spójnych analiz |
| Konstrukcje | C1 zatwierdzone, warunki klas niekompletne | Macierz klas, zweryfikowane reguły, ślady składników, brak nadgeneracji i nowych leksemów |
| KWJP | Pilot nie pokrywa całego mapowania | Pełny import jawnie wskazanych list, mapowanie z niepewnością, statusy braków i zachowane miary |
| Operator | Brak dostępnego CLI i explain | inspect-sources, build, explain, verify, export; czytelne komunikaty i JSON |
| Wydanie | Brak kontrolowanego odbioru | K1–K10, dwa odtworzenia, pakiet list/raportów/atrybucji, ochrona wcześniejszych wydań |

## 2. Wymagane zadania dowodowe

| Zadanie | Dowód już istniejący | Co trzeba domknąć |
|---|---|---|
| Semantyka pól nazw/kwalifikatorów | Parser dzieli kwalifikatory po kresce; surowe pola i przykłady w sgjp-rules/stats | Znaczenie alternatyw i parowania, wszystkie rzeczywiście występujące kombinacje wpływające na decyzje |
| Kategorie skrótowców | brev odrębne; subst/nazwa_pospolita może występować przy wielkich literach | Udokumentowane klasy i przykłady, m.in. PCR/PCV; zmierzony wpływ, bez mechanicznego lower jako dowodu |
| Pełna fleksja | Pełne praet/cond, kontrola 896 798 trójek | Pozostałe klasy, winien, defektywność oraz wyjaśnienie 120 nadmiarowych trójek kontroli |
| Konstrukcje | RJP/SGJP i kod reguł dla bym, przyimek+ń, rozkaźnik+partykuła | Warunki liczby/przypadku/wokaliczności, podwojenia i mobilne końcówki; pełne dziedziczenie analiz |
| Ortografia | NFC/profil PL i celowane dowody pisowni | Macierz współczesnego STANDARD i historycznych form BROAD; ograniczenia by/nie bez swobodnej derywacji |
| Dopasowania KWJP | Formaty, progi, miary i przykłady zgodne/niejednoznaczne | Pełne mapowanie POS/metod, z góry ustalona próba jakości i ocena wyników |

Są to obowiązkowe części realizacji K1–K10. Nie wolno zmniejszyć końcowego zakresu przez oznaczenie klas jako „później”. Mechanizm unresolved pozwala prowadzić prace techniczne, ale nie usuwa blokady pełnego wydania. Nowe rzeczywiste decyzje polityki będą przedstawiane na źródłowych przykładach; znaczenie faktów ustalamy z dowodów.

## 3. Persona, dostęp i cykl danych

Operator uruchamia CLI w lokalnym repo: wybiera jawny manifest i nowy katalog, kontroluje błędy, pyta explain, przegląda raport jakości i przygotowuje pakiet. Nie ma logowania ani nawigacji aplikacyjnej; dostęp do komend zastępuje UI. Wszystkie moduły muszą być osiągalne z CLI, a manifest musi wskazywać pliki wynikowe i ich wersje.

Wejścia są niezmienne i ignorowane przez Git; w repo pozostają konfiguracje, reguły, dowody, kod i raporty procesu. Nowy przebieg nie nadpisuje poprzedniego. Przerwanie nie daje statusu complete. Pobranie i import są rozdzielone. Dane źródłowe nie są kodem do wykonania. Publikacja pakietu i bazy ma osobno sprawdzone warunki.

## 4. Warunki brzegowe i wyłączenia

NKJP pozostaje UNAVAILABLE/BLOCKED i wymaganiem późniejszego pełnego projektu. Poza tą implementacją pozostają ATTESTED, modele znajomości/tematyczne, benchmark i integracja działającej gry. Nie zmieniamy pierwotnej kopii promptu ani zamrożonych wyników research.

Nie ma reprodukowalnego defektu aplikacji ani ciężkiego UI: TDD red dla bugfix i makiety nie są aktywowane. Implementacja nowej funkcjonalności nadal wymaga testów przed kodem w grupach planu. Audyt specyfikacji jest zalecany ze względu na integralność i niejednoznaczność reguł. Weryfikacja runtime będzie dotyczyć CLI oraz rzeczywistych przebiegów danych.

## 5. Bramka zakresu

Rekomendacja: przejść do specyfikacji i planu z całym powyższym zakresem, włączając zadania dowodowe oraz pełne kryteria K1–K10. Nie proponujemy ponownego wyboru G1/N1/C1 ani pilota zamiast końcowego wyniku. Alternatywa: użytkownik wskazuje korektę zakresu przed uszczegółowieniem.

Charakterystyka: `new_capability=true`, `modifies_existing=true` (dokumentacja/organizacja repo), `data_operations=true`, `ui_heavy=false`, `has_reproducible_defect=false`, `risk_level=high`.
