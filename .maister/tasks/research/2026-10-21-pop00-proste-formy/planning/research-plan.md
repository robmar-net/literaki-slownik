# Plan badania POP00

## TL;DR
Pięć kategorii źródeł rozliczamy osobno.
Najpierw metoda POP0 i dane, potem pomiar czułości progów i synteza.
Progi w pilotażu są sondami, nie wybraną polityką słownika.

## Key Decisions
- Źródła: kod, dokumentacja i historia, konfiguracja/testy, przypięte dane, literatura pierwotna.
- Pomiar: POP0 pop-v3 przecięty z formami KWJP orth-all; progi IPM 0,1 / 0,5 / 1 / 2 / 5.
- Kontrole: tokenizacja, wielkość liter, brak wiersza, rozkład długości, zwykłe odmiany.
- Nie pobieramy list zablokowanych przez wcześniejszy audyt. Literatura służy metodologii.

## Open Questions / Risks
- Korpus ma inny rozkład rejestrów niż rozmowa i gra.
- Tokenizacja może ukrywać całe słowo jako kilka segmentów.
- Homonimy: częstość zapisu nie dowodzi częstości każdej interpretacji.

## Strategia i kryteria zakończenia
1. Audyt pop.py, ADR-007/008, konfiguracji, testów i wydania; agent tylko odczytu.
2. Poprzednie badania prostego języka i problemów doboru POP; issue #6.
3. Pomiar odtwarzalnym skryptem: hashe wejść, liczby, pokrycie masy korpusowej,
   przykłady i rozkład długości; osobna kontrola leksemów i tokenizacji.
4. Co najmniej dwa źródła zewnętrzne: oficjalne KWJP i badania rozpoznawania słów.
5. Synteza: wykonalność, ryzyka, alternatywy, brakujące dowody i propozycja badania graczy.
Kończymy po rozliczeniu wszystkich kategorii i wyjaśnieniu sprzeczności istotnych dla wniosku.
Nie wymagamy w tym rozpoznaniu pełnego badania ludzi ani symulacji partii: to dalsza walidacja,
nie wolno więc deklarować poprawy naturalności lub grywalności jako zmierzonego efektu.

## Pytania
- Czy POP0 wybiera leksemy czy także konkretne formy?
- Czy samo usunięcie klas gramatycznych zachowuje zwyczajny język?
- Ile form usuwa próg powierzchniowy i jakie formy usuwa błędnie?
- Czy inny korpus lepiej mierzy znajomość, a jego dane są dostępne na potrzebnych warunkach?
- Czy cel wymaga listy, czy raczej doboru naturalnych ruchów bota?
