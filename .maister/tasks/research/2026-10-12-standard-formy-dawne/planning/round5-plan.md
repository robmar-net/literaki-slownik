# Kalibracja POP — plan rundy 5

## TL;DR
Badamy, czy podnieść limit POP i czy zastąpić go progiem siły dowodów użycia.
Porównujemy tę samą metodę na obecnym STANDARD i propozycji +2382 form.
Wyniki mają uzasadnić decyzję; nic nie zmieniamy w produkcji.

## Key Decisions
- Zlecenie użytkownika: „zrob teraz to badanie”. Publikacja wyników w komentarzu #4 pozostaje autoryzowana.
- Przypięte wejścia LL-PL v29, KWJP, NKJP i pop-v2. POP0 20k jako kontrola, bez nowej kalibracji POP0.
- Oddzielamy pomiar składu, ocenę językową i rekomendację. Zachowujemy historię wcześniejszych wyników.

## Open Questions / Risks
- Nie mamy reprezentatywnych ocen znajomości słów przez graczy. Częstość, rozproszenie i ocena badacza są wskaźnikami.
- Grupy homonimów, najsilniejsi członkowie i braki danych mogą przepuszczać słabe dowody niezależnie od limitu.
- Dobór kontekstów z wyszukiwarki jest celowy. Ręczne oceny mają średnią pewność.

## Pytanie i sukces
Czy obecna granica odcina wartościowe słowa, jaką cenę ma jej przesunięcie i czy próg dowodowy poprawia jakość oraz stabilność? Wynik obejmuje rozmiary, pokrycie po przycinaniu, delty, przykłady dobrych i słabych dodatków, lukę poza listą oraz rekomendację z warunkami. Nie szukamy liczby, która tylko przywróci wskazane wcześniej przykłady.

## Plan pomiarów
- Odtworzyć dokładnie opublikowane POP/POP0 i deltę +2382 STANDARD; zweryfikować przypięcie danych i brak zapisu do bazy.
- Limity POP: 40k/50k do diagnostyki wewnętrznej; 60k, 60025 jako kontrola bloku, 65k, 70k, 75k, 80k, 90k, 100k. Dwa warianty STANDARD. Pełne remisy i obecne przycinanie członków bez zmian.
- Próg wartości obecnej mieszanej miary: równoważniki 0,1; 0,075; 0,05; 0,025; 0,01 na milion oraz wartość graniczna bazowego 60k. Nie nazywać tej mieszanki literalną częstością w jednym korpusie. Próg stosowany do grup i własnych miar członków, z jawnie zachowanymi wyjątkami obecnej metody; dodatkowo porównać odpowiednik obecnego przycinania rangowego, jeśli granica wpada między miary.
- Rozproszenie: opisać F, ARF/F, 1-DP i obecność w trzech gatunkach; nie sumować miar rozproszenia i nie traktować gatunków jak liczby dokumentów. Po inspekcji dostępności określić mały, jawny wariant kontrolny własnego dowodu KWJP przed oceną próbek; brak miary nie oznacza zera.
- Każdy wynik: wybrane jednostki, leksemy przed/po przycinaniu, pełne formy i hash, pokrycie KWJP-standard/all, liczba słów korzystających z wyjątków i braków źródeł, zmiana po dodatkach STANDARD. Dane NKJP wyłącznie jako agregaty, rangi/statusy i wyniki własnych obliczeń.

## Próba jakości
Ustalone przed pomiarem: po 40 różnych podstaw lematu w przedziałach 40–50k, 50–60k, 60–70k, 70–80k, 80–90k i 90–100k; łącznie 240. Dobór deterministyczny przez SHA-256 seeda `issue4-round5-pop-boundary-v1`, warstwy i podstawy lematu. Maksymalnie 40 dodatkowych rozbieżności między metodami oraz 20 kontroli wskazanych wcześniej; oznaczone oddzielnie, bez mieszania z próbą.

Ocena: zastosowanie ogólne, termin/rejestr ograniczony, marginalne lub niejasne, błąd przypisania/odmiany, niepewne. Klasa nie jest automatycznym wyrokiem dopuszczenia. Własna miara, źródła i homonimia widoczne; decyzja wariantu i przedział zostają ukryte w pierwszym przeglądzie. Dla co najmniej 10 pozycji z każdej warstwy oraz przypadków spornych odczytać konteksty lub źródło słownikowe. Dwa rozłączne przeglądy oraz kontrola co najmniej 30 wspólnych pozycji; to ten sam model, nie niezależni ludzie. Wyniki warstw opisujemy osobno, bez nieuzasadnionej estymacji całej populacji.

## Źródła i walidacja
Pięć wymaganych kategorii: kod `pop.py`/`kwjp.py`; ADR/spec/historia wyboru; konfiguracja i istniejące testy; przypięte dane i pełne zbiory; pierwotna dokumentacja KWJP/NKJP, badania metodologiczne i odczyty kontekstów. Materiały poprzednich rund są odczytane i zachowane; nie pobieramy ich ponownie bez potrzeby. Brak `.maister/docs/standards` oraz `.codex/agents` potwierdzono odczytem katalogów. Plan i synteza inline; niezależny tor źródeł i późniejszy przegląd próbek wg reguł delegacji Maister, z rozłącznymi plikami.

Kontrole: zgodność bazowych list, monotoniczność przy podnoszeniu limitu na stałej populacji, identyczne wartości po ponownym wyborze, pełna delta dwóch STANDARD, ponowne hashe wejść, niezależna kontrola progów i próbki. Kryterium zakończenia: wszystkie warianty policzone i zweryfikowane, każda pozycja próby oceniona, wszystkie wymagane kategorie źródeł pokryte lub udokumentowany faktyczny brak dostępu; niepewne przypadki jawne.

## Wyniki i bramka
Nowy raport `outputs/pop-calibration.md` + HTML; skrypty i manifesty pod `analysis/`; wyniki pod `analysis/findings/round5/`. Komentarz do #4 po weryfikacji. Następnie omówienie rekomendacji z użytkownikiem, bez automatycznej zmiany konfiguracji, ADR, list, wydania lub wiki.


## Doprecyzowanie sond rozproszenia przed oceną próby

Odczyt metodologii wskazał dwa błędy pierwszej sondy: singleton bez podjednostki został potraktowany jak brak danych, a ARF jednego wiersza dzielono przez sumę F agregatu. Pierwsze wyniki unieważniono i zachowano lokalnie. Korekta używa wszystkich oryginalnych wierszy KWJP, bez transferu między różnymi podstawami lematu; wystarcza jeden zgodny wiersz. ARF i F pochodzą zawsze z tego samego rekordu. Poprawione pomiary niezależnie odtworzono.

Dokładne warianty: filtr na 80k z ARF≥3/10 oraz ARF/F≥0,1/0,3, każdy w wersji wymagającej KWJP i zachowującej brakujące dane według bazowego 80k. Ponadto trzy progi własnego KWJP bez limitu liczby: F≥10 i ARF≥3; F≥20 i ARF≥5; F≥50 i ARF≥10, zawsze ARF/F≥0,1. Pełne rozmiary/hashe i oba mianowniki. Siatka wrażliwości ARF∈{1,1;2;3;5;10}, ARF/F∈{0;0,01;0,03;0,1;0,3}: liczniki członków i braków, bez dodatkowej selekcji zwycięzcy. Te progi są eksperymentami, nie wartościami wyznaczonymi przez literaturę.

Próba 300 została wygenerowana ponownie po korekcie; pierwsze oceny rozpoczęto dopiero na poprawionej wersji. Konteksty pobrano dla całej próby, nie tylko planowanego minimum 60 haseł:300 odczytów i 1342 konkordancje. Każdy recenzent czyta do 3 różnych dokumentów na hasło oraz poszerza sporne przypadki. Brak trafień pozostaje jawnym ograniczeniem. Wynik live równy 1000 zapisujemy jako liczbę zgłoszoną przez wyszukiwarkę, nie częstość z przypiętego korpusu.
