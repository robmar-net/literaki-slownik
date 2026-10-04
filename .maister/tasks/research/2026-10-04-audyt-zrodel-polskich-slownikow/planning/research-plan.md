# Plan i metodologia audytu

## TL;DR
Zbadamy trzy rodziny źródeł oraz konfigurację gry.
Dokumentację skonfrontujemy z rzeczywistą strukturą i zawartością plików.
Obliczenia mają wyjaśnione jednostki i deterministyczne wyniki.

## Key Decisions
- Zakres wyznacza rozdział 15 specyfikacji v3.
- Odróżniamy pomiar, interpretację, rekomendację i niewykonane badanie.

## Open Questions / Risks
- Statusy licencyjne i możliwości rekonstrukcji fleksji wymagają sprawdzenia dla konkretnych plików.

## Kolejność
1. Dokumentacja, licencje i pochodzenie konkretnych artefaktów; blokada niejasnych wejść.
2. Pobranie do ignorowanego cache, wersje, SHA256 i metadane w rejestrze.
3. Pełne statystyki tekstowego SGJP; kwalifikatory, tagi, homonimy, segmenty.
4. Struktura KWJP/NKJP oraz ograniczony, jawnie dobrany pilotaż dopasowań.
5. Niezależny i sekwencyjny wpływ filtrów BROAD/STANDARD; jawne przypadki nierozstrzygnięte.
6. Synteza wszystkich 10 wymagań, model danych, manifest, ograniczenia i następny etap.

## Walidacja
Pomiary obejmują cały wybrany eksport SGJP. Liczba linii nie zastępuje liczby interpretacji ani leksemów; tagi alternatywne liczymy osobno z definicją. Kontrolujemy homonimy, zachowanie polskich znaków, brak sumowania dowodów korpusowych i relację STANDARD ⊆ BROAD. Przykłady ilustracyjne oznaczamy; nie udajemy próby reprezentatywnej. Duże surowe wejścia nie trafiają do Git.

## Granice zbierania
Obowiązkowo wszystkie punkty startowe rozdziału 16 (bez przeglądarki list jeśli jej dokumentacja i dane zapewniają pełne pokrycie; sama strona będzie sprawdzona). Co najwyżej trzy próby w niedostępnej kategorii, z alternatywnym oficjalnym adresem jeśli istnieje. Sukcesy zachowujemy. Nie kończymy kategorii z powodu samej czasochłonności. Zakończenie zbierania dopiero przy pokryciu źródeł lub udokumentowanej niedostępności.

## Przegląd
Po raporcie obowiązkowa bramka zatwierdzenia badania ze skilla maister-research. Dalsze generowanie rozwiązań i projekt wysokiego poziomu ocenimy oddzielnie; wymagany szkic modelu i filtrów jest już częścią audytu.
