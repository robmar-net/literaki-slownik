# Zakres badania

## TL;DR
Celem jest decyzja o wykonalności pierwszego generatora.
Odbiorcą jest zespół projektu oraz czytelnik publicznego repozytorium.
Wynikiem będzie audyt źródeł, pomiary i projekt; nie końcowy słownik.

## Key Decisions
- Zakres wyznacza rozdział 15 specyfikacji v3.
- Odróżniamy pomiar, interpretację, rekomendację i niewykonane badanie.

## Open Questions / Risks
- Statusy licencyjne i możliwości rekonstrukcji fleksji wymagają sprawdzenia dla konkretnych plików.

## Pytanie i zakres
Czy konkretne wydania SGJP/Morfeusza, KWJP100 i unigramów NKJP pozwalają odtworzyć słowniki zgodnie ze specyfikacją v3 i wyjaśniać każdą decyzję?

Obejmujemy wszystkie 10 punktów rozdziału 15. Źródła wybieramy z oficjalnych dystrybucji dostępnych podczas wykonania. Materiały opcjonalne (NKJP1M, PL196x, WSJP, korpusy dziedzinowe) nie są wymagane w tym etapie. Dokumentację PoliMorfa czytamy wyłącznie dla pochodzenia.

Wyłączone: pobieranie SJP.pl, OSPS w każdej roli, produkcyjne listy, benchmark i zmiany aplikacji. Nie pytamy ponownie o zasady z rozdziału 2.

## Sukces
Każdy punkt rozdziału 15 ma wynik z dowodem albo zaobserwowaną blokadę, jej wpływ i następny krok. Udostępnione skrypty pozwalają odtworzyć pomiary z wejść wskazanych checksumami. Nie zastępujemy braków szacunkami.
