# Decyzje zakresu — #12

## TL;DR
Operator (2026-10-29T01:20:39Z): R2 tylko T2 (+T3 medycyna), ok. 300 słów. Agent ocenia z szerokimi granicami, próg zgodności 0,80. Usuwanie pojedynczych lematów dodajemy teraz. Progi takie jak przy morzu. Zmierzony szum wycinamy przed budową. Listy słów oczywistych operator przegląda przed budową. IATE 2841 jako T3 tylko w medycynie. Dodatki D dopiero po ocenie.

## Kluczowe decyzje
| Temat | Decyzja operatora |
|---|---|
| Rozmiar R2 | operator: 30 słów T2 na temat + 30 T3 w medycynie (~300); T1 ocenia tylko agent |
| Ocena agenta | instrukcja z szerokimi granicami (clarifications.md); próg zgodności 0,80 bez zmian |
| Wykluczenia lematów | implementujemy teraz (`wykluczenia` niepuste dozwolone, stosowane w budowie) |
| Progi | takie same jak dla morza |
| Szum zwierzęta/medycyna | wycinamy zmierzone poddrzewa przed budową (zwierzęta: 6047 człowiek 1, 78303 hominid 1, poddrzewa części ciała z rel. 25; medycyna: organy roślin pod 2180/5999); resztę mierzy R2 |
| Słowa oczywiste | ok. 35 na temat; agent pisze, operator przegląda jedną stronę przed budową; potem bez zmian |
| IATE | T3 = 2841 tylko w medycynie; reszta bez T3 |
| Dodatki D | nie w v1; po wspólnej ocenie |
| Faza 5 | tak |

Decyzje techniczne (nasze, do ADR-012): jeden pakiet na temat; T3 opcjonalne; `t3_tak` „nie dotyczy” bez T3; znaczniki śródlądowe tylko morze; `dodatki` poziom wyżej; metoda `tematy-v1`; regresja morze-v2 bajtowa (poza hashem pliku tematu); strona zbiorcza R2 z linkami do 9 stron.

## Otwarte pytania
- Przy R2 tylko T2 trzeba zmienić próbę operatora (`operator_per_stratum` per warstwa) i kryterium t1_tak (tylko agent).

## Zmiana metody R2 (operator, 2026-10-29, po stronach R2)

- Operator przejrzał 9 stron, ale nie zaznaczał ocen: „nie jestem tu nijak lepszy od Ciebie, ja muszę użyć wyszukiwarki do większości z tych terminów, to nie ma wielkiego sensu”. W muzyce nie był pewien około połowy terminów.
- Jedyna uwaga: „cytoplazma” nie pasuje do kuchni (agent też ocenił „nie”). Reszta: „albo ok, albo nie umiem ocenić”.
- **Decyzja (AskUserQuestion): trafność T2 i T3 w bramce liczymy z ocen agenta.** Kryterium zgodności operator–agent: nie dotyczy. Zmianę zapisujemy w ADR-012.
