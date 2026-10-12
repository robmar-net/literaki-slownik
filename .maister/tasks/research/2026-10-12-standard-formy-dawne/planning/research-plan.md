# Plan researchu

## TL;DR
Pięć kategorii dowodów łączy diagnozę kodu, miary korpusowe i ocenę ryzyka.
Pomiary obejmą cały zbiór odmów za dawność, niezależnie od SJP.pl.
Próbka słów nie będzie udawać reprezentatywnego badania znaczeń.

## Key Decisions
- Scenariusze zamrażamy przed odczytem wyników: próg formy 5, 10, 20, 30; cały KWJP ≥30; dowód lemat+POS w fakt/publicystyka ≥30 i ≥100; wariant z rozproszeniem DP_norm ≤0,9. Są to sondy wrażliwości, nie wybrane reguły.
- Jednostka skutku: nowy unikalny napis w STANDARD z co najmniej jedną spójną analizą; pozostałe odmowy pozostają.
- NKJP: pomocnicza triangulacja na istniejących dozwolonych danych, bez aktywacji w STANDARD.

## Open Questions / Risks
- Próg publikacji wynosi 5 w całym KWJP; gatunkowe wartości 1–4 są publikowane. Brak wiersza nie jest dowodem nieistnienia słowa.
- Lematyzacja i homonimia mogą przypisać dowód do niewłaściwego leksemu.
- Częstotliwość nie rozróżnia żywego użycia od cytatu, stylizacji i wzmianki.

## Kroki
1. Kod: źródła → nonfiction_frequencies → override → ocena interpretacji → agregacja słowa; test granicy 29/30 i wielkiej litery.
2. Dokumentacja i konfiguracje: runda 4/7, ADR-006/007, manifesty, metoda POP, status wydania.
3. Dane: odczyt bazy wydania; osobny skrypt i metryki; weryfikacja hashy; lista przyczyn odmów przykładów; zakres całej populacji.
4. Źródła pierwotne: SGJP — znaczenie etykiet; KWJP — gatunki, zakres lat, miary i ograniczenia; NKJP — pochodzenie i warunki; WSJP PAN — kontrola znaczeń w próbce.
5. Próbka: wszystkie przykłady ticketu, słowa o dużym efekcie i deterministyczna próbka nowych lematów. Jawna ocena: zwykłe użycie / nacechowane żywe / dawne lub stylizacyjne / nierozstrzygnięte. Odrębnie kontrola dostępnych kontekstów.
6. Synteza: liczby, kontrprzykłady, pewność, braki i rekomendacja do rozmowy. Publikacja komentarza jest zlecona przez użytkownika. Bramka akceptacji researchu pozostaje otwarta.

## Walidacja i warunek zatrzymania
Wszystkie pięć kategorii sprawdzone albo niedostępność udokumentowana. Różnice przeliczone z utrwalonych decyzji i kontrolnych ocen kodu. Istotne sprzeczności jawne; konkretna rekomendacja nie wymaga udawania kompletnego audytu znaczeń. Jeśli wynik zależy od nieweryfikowalnego znaczenia, wskazujemy wymagany dalszy audyt.

## Dodatkowa sonda po próbce
Pierwsza próbka ujawniła archaiczne odmiany zwykłych słów. Dodano kontrolę lemma+POS NF≥30 bez dosłownego składnika arch. (skrypt followup.py), z osobną próbką 30 grup. Nie dobierano wariantu do SJP.pl. Sonda dyspersji oznacza co najmniej jeden gatunek nieliteracki z F≥30 i DP_norm≤0,9, nie sumę lub średnią DP.
