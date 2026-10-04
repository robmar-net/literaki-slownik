# PoliMorf — podstawa wyłączenia z wejść konstrukcyjnych

## TL;DR

Wyłączenie PoliMorfa wynika z §3.1 przyjętej specyfikacji i dokumentowanego pochodzenia. Nie pobrano danych PoliMorfa, Morfologika, SJP.pl ani OSPS. Badanie ograniczono do oficjalnej dokumentacji.

## Key Decisions

- Dane PoliMorfa mają w tym procesie status **BLOCKED / PROJECT_EXCLUDED_DERIVATION**. Powodem jest zakres metodologiczny projektu, a nie niejasność licencji czy ocena jakości.
- Dokumentacja ma status `ALLOWED` wyłącznie jako źródło bibliograficzne ustaleń. Jej kopie pozostają w cache; nie publikujemy pełnych dokumentów.
- Jawny wybór SGJP oraz identyfikator faktycznie załadowanego słownika są konieczne. Sama nazwa „Morfeusz” nie identyfikuje wejść.

## Open Questions / Risks

Zbadane opisy wystarczają do uzasadnienia wyłączenia PoliMorfa. Nie są audytem całej historii SGJP, wszystkich narzędzi anotacji ani ich zależności. Nie dowodzą całkowitego braku pośrednich zależności od innych zasobów w całym przyszłym procesie.

## Dowody pierwotne

1. [Oficjalna strona PoliMorf](https://zil.ipipan.waw.pl/PoliMorf), ostatnia edycja 09.12.2015, opisuje wynik standaryzacji i połączenia Morfeusz SGJP oraz Morfologika. Dla źródeł i wynikowego zasobu deklaruje BSD 2-Clause. Strona wskazuje wydanie 0.6.7, którego danych nie pobierano. Opis Morfologika wskazuje wcześniejszy słownik ispell/hunspell jako podstawę wzbogaconą o informację morfologiczną.
2. [Marcin Woliński, „Morfeusz 2. Dokumentacja techniczna i użytkowa”, 22.01.2026](https://download.sgjp.pl/morfeusz/Morfeusz2.pdf), strona 2, wyraźnie rozróżnia SGJP oraz Polimorf i wskazuje łączenie SGJP z materiałem SJP.pl w tym drugim wariancie. To bezpośredni dowód dla zakresu ustalonego w specyfikacji; nie trzeba pobierać list słownikowych, aby uzasadnić decyzję.

Na stronie PoliMorf wymieniono publikację: Woliński, Miłkowski, Ogrodniczuk, Przepiórkowski i Szałkiewicz, *PoliMorf: A (not so) new open morphological dictionary for Polish*, LREC 2012, s. 860–864. Raport opiera konkretne ustalenia na dwóch odczytanych źródłach powyżej, nie przedstawia tej publikacji jako dodatkowo przeczytanej.

## Metryki i dostępność

Pobrano wyłącznie stronę HTML oraz PDF dokumentacji do `cache/nkjp/`. Rejestr wraz z SHA256: [polimorf-sources.json](polimorf-sources.json). Strona i PDF były dostępne; curl zakończył się sukcesem. Próbny adres `https://morfeusz.sgjp.pl/doc/about/pl` nie był dostępny w narzędziu WWW; aktualny oficjalny PDF zapewnił wymagany dowód. Nie stanowi to blokady kategorii źródeł.

SHA256 HTML: `7bbd9be0b866bbe2cb14d6a442ee10e702c626d0f2064f6170eac1ed94595910`.
SHA256 PDF: `5571ddb62c0e19668919151bc89637b9fb0a80ffd6665f2d4d1ff3cde756d3cd`.

Nie obliczano statystyk zasobu i nie oceniano jego rekordów. Warunki poszczególnych plików danych nie były audytowane; przytoczenie deklaracji BSD nie oznacza zakończenia takiego audytu.
