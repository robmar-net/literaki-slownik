# Ocena kandydatów według przyjętego kierunku — runda 3

## TL;DR
Użytkownik polecił przejść do oceny kandydatów i pomiaru wpływu po przyjęciu zasady znaczenia i współczesnej odmiany.
Sprawdzimy pełną populację 404 grup / 3364 form, wcześniejsze kontrole oraz 290 obecnych przyjęć zależnych od wyjątku.
Wynikiem będą jawne oceny zakresu dowodu, konkretna propozycja dodatków i symulacja STANDARD oraz POP/POP0.
Brak dowodu pozostaje nierozstrzygnięciem. Liczba kandydatów nie stanie się liczbą zaakceptowanych słów.

## Key Decisions
- Kontynuacja researchu, bez zmiany generatora, polityki, produkcyjnych wejść i wydań. Odpowiedź „ok, idzmy” autoryzuje ten następny krok.
- Zasada przyjęta wcześniej pozostaje punktem odniesienia; dokładna procedura dowodowa jest propozycją badawczą do oceny, nie zatwierdzoną regułą wykonawczą.
- Nie ograniczamy odmiany progiem frekwencji ani progiem dla konkretnej części mowy. Potwierdzone rodziny sprawdzamy również poza wcześniejszym scenariuszem lemma≥30.
- Zachowujemy poprzednie pomiary i decyzję użytkownika; nowa faza ma osobną bramkę oceny wyników.

## Open Questions / Risks
- Brak pełnych danych semantycznych w przypiętym eksporcie. Odczyt czytnika służy analizie i nie staje się nowym wejściem produkcyjnym.
- Przykłady autorskie i kwalifikator słownika mogą się różnić. Taki konflikt ujawniamy zamiast samodzielnie rozstrzygać granicę archaizacji.
- POP może zmienić również dobór leksemów i progi rankingu. Samo przecięcie dodatków z dawnym rankingiem nie jest pełnym pomiarem.

## Pytanie i odbiorca
Które dodatki można konkretnie uzasadnić przyjętą zasadą, które wymagają węższego zakresu lub dalszej decyzji, oraz jak proponowany zakres wpłynie na listy? Odbiorcą jest właściciel podejmujący decyzję o ewentualnym wdrożeniu.

## Metoda i obowiązkowe pokrycie
- Kod: odczyt obecnej kwalifikacji i budowy POP, w tym reguły przenoszenia form, doboru jednostek i przycinania homonimów.
- Dokumentacja: uzgodniony kierunek, istniejące reguły STANDARD, ADR-007 i ograniczenia źródeł.
- Konfiguracje i testy: piny v29 / pop-v2, kontrola składania list i istniejących testów związanych z użytymi funkcjami.
- Dane: pełna macierz 404 grup, wszystkie 290 zależnych przyjęć, wcześniejsze 257 zapytań i 107 fragmentów; rozszerzenie potwierdzonych rodzin na wszystkie kandydackie analizy dawności bez progu lemma/POS.
- Źródła pierwotne: ponowne użycie udokumentowanych odczytów SGJP/WSJP/KWJP i celowe uzupełnienie brakujących dowodów znaczenia lub odmiany. Pełne teksty tylko w ignorowanym cache.

## Rozdział ocen
Każda grupa otrzyma odsyłacze do dostępnych dowodów i jeden z wyników: konkretny zakres do propozycji, zakres ograniczony, konflikt wymagający decyzji albo brak wystarczającego dowodu. Ocena dotyczy wskazanych analiz i form, nie całego napisu we wszystkich znaczeniach.

Propozycja wymaga rozpoznanego współczesnego znaczenia, użyć autorskich w różnych tekstach oraz ustalonego współczesnego zakresu odmiany. Brak dawności w WSJP pomaga rozstrzygać konflikt z etykietą SGJP; zależność źródeł pozostaje jawna. Formy z dodatkową dawną końcówką lub ograniczeniem konstrukcji nie przechodzą razem z całą rodziną. Rzadkiej regularnej odmiany nie wymagamy w osobnych konkordancjach. Wątpliwe pochodne i rozbieżne warianty pozostają oddzielnie.

## Pomiar i walidacja
- Baza v29 tylko do odczytu; pełna lista proponowanych form, identyfikator leksemu, zakres, dowody i powód każdej decyzji w artefaktach.
- Osobno przyrost z dawnej populacji 3364 i dodatki spoza niej. Pozostałe odmowy nadal obowiązują.
- Kontrola wszystkich 290 przyjęć: powiązanie z analizą i dostępnym dowodem; brak dowodu nie oznacza automatycznego usunięcia.
- Odtworzenie bazowego POP/POP0, następnie ponowne przeliczenie rankingu i list dla symulowanego STANDARD. Raport także o ewentualnych ubytkach, nowych jednostkach i straży częstych form.
- Kontrola sum, rozłączności statusów, źródeł i zgodności bazowych wyników z opublikowanym pakietem. Jawne ograniczenia badania.

## Warunek zakończenia
Każdy rekord zakresu ma wynik i uzasadnienie, konkretna propozycja ma dowód znaczenia i odmiany, pomiar obejmuje STANDARD i POP/POP0, a raport ujawnia nierozstrzygnięcia. Publikujemy komentarz i przedstawiamy wyniki użytkownikowi do decyzji. Nie udajemy pełnego audytu wszystkich 389160 potencjalnych dodatków ani reprezentatywnego odsetka błędów.
