# Synteza rozpoznania POP00

## TL;DR
Selekcja form jest wykonalna na istniejących danych.
Próg powierzchniowy bez obsługi fleksji i segmentacji usuwa naturalne słowa.
Najlepszy kierunek do sprawdzenia łączy leksemy POP0, zwykłą odmianę i ostrożność wobec nietypowych form.

## Key Decisions
- Zakończono zbieranie dowodów; operator zaakceptował rozpoznanie 2026-10-21 („ok”).
- Nie przyjęto progu ani reguł POP00, nie zmieniono wydanych list.
- Burza pomysłów i projekt pozostają osobnymi opcjami po bramce.

## Open Questions / Risks
- Nie ma reprezentatywnego pomiaru znajomości ani pomiaru grywalności.
- Zachowanie wszystkich leksemów nie wynika z samego filtra form: przy IPM ≥ 1 ginie 661 leksemów.
- Pełna odmiana wszystkich leksemów odtworzyłaby część problemu dzisiejszego POP0.

## Łańcuch wnioskowania
1. Kod i konfiguracja wybierają leksemy, a nie częstość każdej formy.
2. Pomiary potwierdzają ogromną redukcję przez próg, ale też fałszywe odrzucenia.
3. Segmentacja wyjaśnia część braków; próg publikacji i rejestr wyjaśniają inne luki.
4. Nie wolno utożsamiać braku obserwacji z brakiem znajomości.
5. Wąskie reguły morfologiczne i własny pomiar ocen pozwolą sprawdzić naturalność.

## Zgodność i sprzeczności źródeł
Pakiet i kod zgadzają się co do aktualnych liczb i pełnej odmiany.
Starsze README/indeks mówią o nieukończonym generatorze lub dawnym limicie;
wydanie i ADR-008 są nowszym dowodem. Historyczny pomiar szerokich klas nie jest pomiarem POP0.
Wyniki korpusowe nie przeczą znajomości zwykłych odmian: mierzą inne zjawisko.

Pewność wysoka dla mechaniki i liczb, średnia dla rekomendowanego kierunku,
nieustalona dla efektu u graczy. Dalsze badanie powinno dodać nowe rodzaje dowodów,
nie tylko więcej progów tego samego korpusu.

Pełne liczby, cytowania, alternatywy i plan walidacji: [raport](../outputs/research-report.md).
