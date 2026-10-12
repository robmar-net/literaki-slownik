# STANDARD: formy dawne i słowa żywe — research #4

## TL;DR
Problem istnieje, ale nie wynika z pominięcia publicystyki: próg 30 działa na dokładną formę, nie leksem.
Samo obniżenie progu lub przejście na leksem daje wyraźne błędy i nie rozwiązuje całego problemu.
Rekomendacja do rozmowy: oddzielić współczesność znaczenia od współczesności formy odmiany.
Badanie zakończono; zatwierdzenie wniosków i wybór kryteriów pozostają u właściciela.

## Key Decisions
- Wykonano tylko research. Nie zmieniono reguł, konfiguracji, list, wydania ani wiki.
- Wszystkie scenariusze są dodatkowymi wyjątkami: zachowują obecne przyjęcia i inne odmowy.
- SJP.pl służy wyłącznie jako końcowa miara; nie wybiera kandydatów, progów ani próbki.

## Open Questions / Risks
- Czy STANDARD ma obejmować żywe słowa książkowe i nazwy dawnych przedmiotów?
- Jak dopuścić współczesną odmianę leksemu bez archaicznych form i obcych znaczeń?
- Miara lemma+POS, nawet z rozproszeniem, nie rozpoznaje znaczenia; nie jest gotową polityką.

## Pytanie, metoda i zakres
Dlaczego reguła dawności odrzuca zwykłe dziś słowa i jaka niezależna miara mogłaby ją poprawić? Prześledzono kod, testy, decyzje i konfiguracje. Zbadano cały zbiór analiz zamrożonego wydania, dla których jedyną przeszkodą pozostaje dawność; przeliczono unikalne nowe napisy. Potem porównano je z top 2000 braków SJP. Przejrzano deterministyczną próbkę 40 grup lematowych, kolejną próbkę 30 grup po wykryciu ryzyka oraz publiczne konteksty KWJP½M. Oficjalną dokumentację sprawdzono 2026-10-12.

Baza: `data/work/lists-v30-20261010-165826-a` użyta w wydaniu **LL-PL v29**, polityka `approved-conditions-v29`, STANDARD **3 090 194** form. W nazwach lokalnego buildu, pakietu i polityki występują różne numery; nie są zamienne. SHA256 bazy `85b23ca5…3a338c`, listy `a432c7c5…19d877` zgadzają się z przypiętym manifestem POP. Pełne dane i identyfikatory: [measurements.json](../analysis/findings/measurements.json).

## 1. Przyczyna
[decisions.py:19](../../../../../literaki_slownik/decisions.py) sumuje **orth**, małe litery, **fakt + publicystyka**. [policy.py:1086](../../../../../literaki_slownik/policy.py) przy ≥30 zastępuje tylko odmowę dawności. Reguła dotyczy dokładnej formy, a nie całej odmiany. Runda 7 chroni przed dowodem typu „Ali” → dawny spójnik ali. [Diagnoza kodu](../analysis/findings/code-and-policy.md).

Natomiast [wiki braków SJP](https://github.com/robmar-net/literaki-slownik/wiki/Brakujace-slowa-SJP.pl) pokazuje **orth_lc / all**: także fikcję i zapis wielką literą. To inne liczby.

| Forma | Liczba z miary wiki | Małe litery: fakt + publicystyka | Lemma+POS: fakt + publicystyka |
|---|---:|---:|---:|
| desperacja | 67 | 28 | 233 |
| ekscytacją | 71 | 21 | 219 |
| niezbędnik | 80 | 17 | 88 |
| familia | 95 | 19 | 170 |
| odzienie | 81 | 28 | 63 |
| surdut | 82 | 19 | 58 |
| aliści | 65 | 12 | 31 |
| jakoż | 61 | 7 | 41 |
| iże | 102 | 0 | 1 |

Przykład niespójnej odmiany: `desperacji` jest w STANDARD (166 wystąpień nieliterackich), ale `desperacja` nie; `ekscytacja` jest (42), ale `ekscytacją` nie. To zachowanie zgodne z obecną regułą, nie błąd sumowania.

615/2000 z ticketu potwierdzono. Jest to **liczba napisów z dawną analizą w próbce braków**, a nie liczba błędów. Wymienienie „nazwy własnej + dawności” może łączyć powody z różnych homonimów.

## 2. Ile doszłoby do STANDARD
Wyniki dokładne dla poniższych symulacji na przypiętej bazie. To nie build ani prognoza zatwierdzonego wydania. Wszystkie inne warunki pozostają, a nowy wyjątek jest dodany do obecnego. Jednostka: unikalna forma do gry, nie leksem.

| Dodatkowe złagodzenie | Nowe formy | Odzysk z top 2000 braków SJP |
|---|---:|---:|
| Obecny próg 30 — kontrola | 0 | 0 |
| Dokładna forma: nieliterackie ≥20 | 131 | 130 |
| Dokładna forma: nieliterackie ≥10 | 487 | 323 |
| Dokładna forma: nieliterackie ≥5 | 1193 | 405 |
| Dokładna forma: cały KWJP ≥30 | 150 | 149 |
| Lemma+POS: nieliterackie ≥30 | 4559 | 307 |
| Lemma+POS: nieliterackie ≥100 | 2150 | 126 |
| Lemma+POS: gatunek nieliteracki ≥30 i DP_norm≤0,9 | 1793 | 89 |
| Lemma+POS ≥30, ale zachować blokadę arch. | 3364 | 307 |
| Całkowicie zdjąć tylko odmowę dawności | 389160 | 615 |

Próg 20 nadal pomija `niezbędnik` i `familia`, a wpuszcza `nazad` i `trzykroć`. Cały KWJP wpuszcza `iże`: 100 małoliterowych wystąpień w fikcji, brak opublikowanego małoliterowego wystąpienia w fakt/publicystyka. Próg lemma ≥100 nadal pomija `niezbędnik` i nie chroni dawnych odmian. Dyspersja ogranicza skupiska, ale wpuszcza `desperacyj`; nie zastępuje oceny znaczenia ani formy.

## 3. Ile w tym archaizmów: wynik próbki
W wariancie lemma ≥30 **35 z 40 wylosowanych grup daje wyłącznie formę oznaczoną przez SGJP jako arch.**, np. `technologij`, `infolinij`, `telekomunikacyj`. W 76 dodatkach tej próbki 36 ma jawne arch. (dodatkowo `familij`). To źródłowa klasyfikacja i kontrola form, nie niezależna ekspertyza całej populacji; nie przeliczamy tego odsetka na 4559 dodatków.

W całej tej symulacji aż **3779/4559** nowych form nie ma opublikowanego małoliterowego wiersza orth/all. Brak wiersza nie oznacza nieistnienia formy, ale pokazuje, jak dużo przyjęć wynika wyłącznie z przeniesienia dowodu leksemu.

Zachowanie blokady arch. zatrzymuje 1195 dodatków. Pozostałe 3364 nadal obejmują np. `ośm`, `niewiela`, `wywre` oraz wymagające rozdzielenia homonimów `metrowie` i `kursorzy`. Nie można jednak odrzucać wszystkich takich przykładów mechanicznie: [WSJP dokumentuje kalkulatorzy w żywym znaczeniu osoby](https://wsjp.pl/haslo/podglad/18446/kalkulator/1895592/bezwzgledny).

Pełne 70 grup, sposób losowania, oceny i zastrzeżenia: [przegląd próbek](../analysis/findings/sample-review.md).

## 4. Co znaczy niezależny dowód współczesności
[KWJP](https://kwjp.pl/overview) opisuje piśmiennictwo 2011–2020. [Miary list](https://kwjp.pl/lists/doc/about/) pozwalają badać częstość i rozproszenie, ale anotacja jest automatyczna. Lemma+POS może łączyć różne znaczenia; licznik nie rozróżnia cytatu i użycia. Dane gatunkowe 1–4 są poprawne — próg publikacji 5 dotyczy całego korpusu.

Przegląd 5500 plików KWJP½M dał 12 właściwych kontekstów rodzin przykładów ticketu: są żywe `desperacji` i `ekscytację`, stylizowane `iże`, a także `jakoż` w dawnym języku wewnątrz książki zaklasyfikowanej jako fakt. Próbka sugeruje cytat, lecz pełnego pochodzenia tego fragmentu nie ustalono. `Niezbędnik` wielką literą w odsyłaczu nie dowodzi zwykłego rzeczownika. Metryczki i własne oceny: [context-review.json](../analysis/findings/context-review.json).

Źródła słownikowe ujawniają różnicę między rejestrem a dawnością: [desperacja](https://wsjp.pl/haslo/podglad/47650/desperacja/5147287/rozpacz) i [familia](https://wsjp.pl/haslo/podglad/12840/familia/5180478/wielodzietna) są w WSJP książkowe; [odzienie](https://wsjp.pl/haslo/podglad/89359/odzienie) — przestarzałe; [surdut](https://wsjp.pl/haslo/podglad/71964/surdut/5193113/marynarka) opisuje dawny przedmiot. To nie są równoważne przesłanki odrzucenia.

[NKJP 1-gramy](https://zil.ipipan.waw.pl/NKJPNGrams) są starsze, małoliterowe, bez kontekstu i rozdziału znaczeń. Po istniejącym czyszczeniu mają `jakoż` 413, `aliści` 268, `desperacja` 121: nie należy z tego robić skali współczesności. [ADR-006](../../../../../docs/adr/ADR-006-nkjp-cc-by-bez-wersji.md) dopuszcza dane do POP/POP0; użycie ich do kwalifikacji STANDARD wymaga osobnej decyzji o zakresie.

„Niezależne” oznacza tu niezależność od SJP.pl. KWJP używa SGJP w anotacji, a WSJP często cytuje NKJP; tych źródeł nie należy liczyć jako całkowicie niezależnych głosów. [Szczegóły i źródła](../analysis/findings/external-evidence.md).

## 5. Wniosek i rekomendacja do decyzji
**Nie rekomenduję obecnie żadnego z prostych progów jako samodzielnej reguły produkcyjnej.** Dane wystarczają do odrzucenia automatycznego przejścia na leksem i do potwierdzenia wad obecnej miary. Nie wystarczają do uczciwego ogłoszenia, że wszystkie 3364 dodatki są dobre.

Rekomenduję kryterium dwuczęściowe: dodatni dowód współczesnego znaczenia/leksemu oraz osobną kontrolę współczesnej formy. Częstość, publicystyka i rozproszenie mogą wyłaniać kandydatów. Ostateczny dowód powinien rozdzielać homonimy i nie przenosić się na dawną odmianę. Dopuszczenie książkowości lub nazw dawnych przedmiotów jest decyzją o charakterze STANDARD.

Alternatywy do rozmowy: zachować obecną regułę (znane braki zostaną), obniżyć próg (mała i policzalna zmiana, ale także archaizmy), albo opracować kontrolę leksemu i formy (najlepiej odpowiada problemowi, wymaga dodatkowej pracy dowodowej). Ostatni kierunek jest rekomendacją, nie zatwierdzoną decyzją.

Po ustaleniu znaczenia „słowo żywe” warto pogłębić ocenę konkretnych kandydatów, szczególnie homonimów i odmiany. Dalsze dowolne obniżanie progów ma mniejszą wartość. POP/POP0 wymagają osobnego ponownego pomiaru po zmianie STANDARD: limity i ranking mogą zmienić skład, więc nie dodajemy mechanicznie powyższych przyrostów do ich liczebności.

## Pokrycie, pewność i odtwarzanie
Wszystkie pięć zaplanowanych kategorii sprawdzono: kod; decyzje/dokumentacja; konfiguracja/testy; przypięte dane; zewnętrzne źródła pierwotne. [Rejestr](../planning/sources.md). Nie kontaktowano się z autorami danych. Nie importowano nowego źródła.

**Wysoka pewność**: przyczyna, różnica miar, skutki dokładnie opisanych sond. **Średnia**: interpretacja małej próbki i zalecany kierunek. **Nieustalone**: udział rzeczywistych archaizmów w całej nowej populacji, rozdział wszystkich znaczeń, użycie po 2020.

Odtwarzanie z katalogu repo: `python3 .maister/tasks/research/2026-10-12-standard-formy-dawne/analysis/measure.py`, następnie `analysis/followup.py` i `analysis/evidence_probe.py` z tego samego katalogu zadania. Wymagają lokalnej przypiętej bazy, cache KWJP/NKJP i benchmarku; nie pobierają nowych danych. Baza otwierana `mode=ro`, a probe nie zmienia list. Hashe zweryfikowano, kontrola obecnego progu dała 0 zmian; istniejące 6 testów reguły przeszło. Kontrolne zapytania dla przykładów odtworzyły frekwencje i statusy ([walidacja](../analysis/findings/validation.json)).
