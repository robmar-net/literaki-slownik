# Research Maister: STANDARD i formy dawne

## TL;DR
Problem jest potwierdzony. Publicystyka już jest uwzględniona; wyjątek wymaga jednak 30 wystąpień dokładnej formy, nie całego leksemu.
Proste przejście na częstość leksemu przywróci zwykłe słowa, ale także wiele archaicznych odmian.
Rekomenduję rozdzielić ocenę współczesnego znaczenia i współczesnej formy. Decyzji o nowej regule jeszcze nie podjęto.

## Key Decisions
- Zgodnie ze zleceniem: tylko research. Bez zmian kodu generatora, polityki, list, wydania i wiki.
- SJP.pl był wyłącznie miarą. Kandydatów i próbki wybrano z pełnych danych SGJP/KWJP.

## Open Questions / Risks
- Czy STANDARD ma obejmować żywe słowa książkowe i nazwy dawnych przedmiotów?
- Jak przywracać odmianę bez dopuszczania archaicznych form i podbierania częstości innym znaczeniom?

### Dlaczego te słowa odpadają
Wyjątek z rundy 7 liczy `orth`, wyłącznie zapis małymi literami, **fakt + publicystyka**. Wiki pokazuje `orth_lc / all`: także fikcję i zapis wielką literą.

| Forma | Liczba z miary wiki | Liczba używana przez wyjątek |
|---|---:|---:|
| desperacja | 67 | 28 |
| ekscytacją | 71 | 21 |
| niezbędnik | 80 | 17 |
| familia | 95 | 19 |
| odzienie | 81 | 28 |
| surdut | 82 | 19 |

`desperacji` jest w STANDARD (166), ale `desperacja` nie. `ekscytacja` jest (42), ale `ekscytacją` nie. To skutek reguły działającej osobno na każdą formę. [Kod i diagnoza](https://github.com/robmar-net/literaki-slownik/blob/58396d7a967236de9f479250aff8802dbc078f0b/.maister/tasks/research/2026-10-12-standard-formy-dawne/analysis/findings/code-and-policy.md).

615/2000 potwierdziło się. To liczba napisów z dawną analizą, **nie liczba błędów do automatycznego poprawienia**. Powód „nazwa własna + forma dawna” może łączyć odmowy różnych homonimów.

### Ile doszłoby
Pomiar na zamrożonej bazie wydania LL-PL v29, STANDARD 3 090 194 form. Wszystkie poniższe scenariusze **poszerzają obecny wyjątek**, zachowują dotychczasowe przyjęcia i wszystkie inne odmowy. Jednostka: unikalna forma do gry.

| Dodatkowy wyjątek | Nowe formy STANDARD | Odzysk z top 2000 braków SJP |
|---|---:|---:|
| Dokładna forma, fakt+publicystyka ≥20 | 131 | 130 |
| Dokładna forma, fakt+publicystyka ≥10 | 487 | 323 |
| Dokładna forma, cały KWJP ≥30 | 150 | 149 |
| Lemma+POS, fakt+publicystyka ≥30 | 4559 | 307 |
| Lemma+POS, fakt+publicystyka ≥100 | 2150 | 126 |
| Lemma+POS, gatunek nieliteracki ≥30 i DP_norm≤0,9 | 1793 | 89 |
| Lemma+POS ≥30, ale zachować blokadę arch. | 3364 | 307 |
| Usunąć samą odmowę dawności | 389160 | 615 |

Próg 20 nadal pomija `niezbędnik` i `familia`, a wpuszcza `nazad` i `trzykroć`. Cały KWJP wpuszcza `iże` dzięki beletrystyce. Podwyższenie progu leksemu lub dodanie dyspersji nadal wpuszcza `desperacyj`. [Pomiary i odtwarzalne skrypty](https://github.com/robmar-net/literaki-slownik/tree/58396d7a967236de9f479250aff8802dbc078f0b/.maister/tasks/research/2026-10-12-standard-formy-dawne/analysis).

### Co pokazały próbki
W deterministycznej próbce wariantu lemma ≥30 **35/40 grup lematowych daje wyłącznie formy oznaczone w SGJP jako arch.**: np. `technologij`, `infolinij`, `telekomunikacyj`. W 76 nowych formach tej próbki 36 ma jawne arch. To klasyfikacja źródłowa; nie jest niezależną ekspertyzą całej populacji i nie ekstrapoluję jej na 4559 dodatków.

Blokada arch. zatrzymuje 1195 form. Przegląd dalszych 30 grup nadal ujawnia `ośm`, `niewiela`, `wywre` i ryzyko pomieszania znaczeń przy `metrowie`/`kursorzy`. Z drugiej strony [WSJP potwierdza żywe kalkulatorzy jako określenie osób](https://wsjp.pl/haslo/podglad/18446/kalkulator/1895592/bezwzgledny): także odrzucanie musi opierać się na dowodzie. [Pełny przegląd próbek](https://github.com/robmar-net/literaki-slownik/blob/58396d7a967236de9f479250aff8802dbc078f0b/.maister/tasks/research/2026-10-12-standard-formy-dawne/analysis/findings/sample-review.md).

Przejrzałem też 5500 plików publicznej próbki KWJP½M, uzyskując 12 właściwych kontekstów rodzin przykładów. Są żywe użycia `desperacji` i `ekscytację`, stylizowane `iże`, a także dawny język z `jakoż` w książce z gatunku fakt. Sam gatunek nie usuwa stylizacji i cytatów.

### Wniosek do rozmowy
**Nie rekomenduję wdrażania teraz żadnego prostego progu.** Rekomenduję dodatni dowód współczesnego znaczenia/leksemu oraz osobną kontrolę współczesnej odmiany. KWJP i rozproszenie mogą wyłaniać kandydatów; nie mogą same przenosić dowodu na wszystkie homonimy i dawne formy.

Książkowość i dawność nie są tym samym: WSJP opisuje [desperację](https://wsjp.pl/haslo/podglad/47650/desperacja/5147287/rozpacz) i [familię](https://wsjp.pl/haslo/podglad/12840/familia/5180478/wielodzietna) jako książkowe, [odzienie](https://wsjp.pl/haslo/podglad/89359/odzienie) jako przestarzałe. [Surdut](https://wsjp.pl/haslo/podglad/71964/surdut/5193113/marynarka) to nazwa dawnego przedmiotu. Granica między tymi przypadkami jest decyzją o charakterze STANDARD.

NKJP jest pomocniczy: starszy, bez wielkości liter, znaczeń i dat przy 1-gramach. W pomiarze `jakoż` ma 413, `aliści` 268, `desperacja` 121 — to nie skala współczesności. ADR-006 dotyczy POP/POP0; aktywacja NKJP w kwalifikacji STANDARD wymaga osobnego uzgodnienia zakresu.

**Pewność:** wysoka dla przyczyny i liczb opisanych sond; średnia dla ocen próbki. Nie ustalono udziału rzeczywistych archaizmów w całym przyroście ani użycia po 2020 (koniec zakresu KWJP). Przed wdrożeniem potrzebny jest dalszy audyt kandydatów według uzgodnionego kryterium. Zmiana STANDARD wymaga też nowego pomiaru POP/POP0 — nie znamy jeszcze ich nowych liczebności.

[Pełny raport, źródła i ograniczenia](https://github.com/robmar-net/literaki-slownik/blob/58396d7a967236de9f479250aff8802dbc078f0b/.maister/tasks/research/2026-10-12-standard-formy-dawne/outputs/research-report.md). Research wykonany pluginem Maister; wyniki czekają na omówienie z właścicielem.
