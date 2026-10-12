# STANDARD i POP: wynik celowanego audytu — runda 4

## TL;DR
Osobny przegląd potwierdza zakres **2382 form ze 110 rodzin**; skład propozycji pozostaje bez zmian.
Wszystkie **2430 ubytków POP** wynikają z granicy obecnego rankingu przy niezmienionych miarach tracących członków.
`Dekagram` był w POP0 dzięki wspólnej grupie i wyjątkowi dla jej najmocniejszego członka; cofnięcie `dag` usuwa tę podstawę.
Z 12 wątpliwych zapisów **8 kwalifikuje się do osobnej decyzji o cofnięciu obecnych analiz**, a **4 wymagają wstrzymania**. Bez wdrożenia.

## Key Decisions
- Użytkownik przyjął rundę 3 jako podstawę decyzji i zlecił zalecany audyt. Nie zatwierdził paczki do wydania, cofnięć ani zmiany metody.
- Zachowujemy zasadę współczesnego znaczenia i odpowiadającej mu współczesnej odmiany. Pozostałe kryteria STANDARD nadal obowiązują.
- Pierwotne wyniki rundy 3 pozostają historią. Ten raport doprecyzowuje przyczyny i dowody; nie zmienia produkcji.

## Open Questions / Risks
- Ocena językowa ma średnią pewność. Osobni agenci używają tego samego modelu i częściowo tych samych źródeł; to nie niezależna ekspertyza ludzka.
- Dowód napisu nie zawsze dowodzi analizy przyjętej przez generator. Nowy sens może wymagać innego leksemu lub źródła.
- Parametry POP realizują ograniczony ranking, nie gwarancję zachowania każdego wcześniej przyjętego słowa.

## 1. Zakres i metoda

[Plan](../planning/round4-plan.md) obejmuje trzy zamknięte tory: wszystkie 110 rodzin propozycji, 12 wskazanych przyjęć i pełne wyjaśnienie zmian POP.
Koordynator odtworzył listy i przeprowadził kontrole przyczynowe. Osobni recenzenci ocenili rodziny, obecne przyjęcia oraz kod i interpretację pomiarów POP.
To celowany przegląd dowodów, nie losowa próba ani pomiar błędu populacyjnego.

Podstawa liczb pozostaje ta sama: **LL-PL v29**, przypięte dane i metoda `pop-v2`. Baza została otwarta tylko do odczytu.
Całe zbiory POP/POP0 oraz delty dodatków i izolowanego cofnięcia `dag` są identyczne z wynikami rundy 3.
Źródła i pokrycie: [rejestr](../planning/sources.md), [walidacja POP](../analysis/findings/round4/pop-validation.json).

## 2. Paczka 2382 form po osobnym przeglądzie

Wynik: **110/110 rodzin potwierdzonych w proponowanym zakresie; 0 form do wycofania lub zawężenia**.
Przeczytano ponownie 324 surowe konkordancje dla 109 rodzin; `surdut` sprawdzono przez WSJP.
Osobny parser sprawdził 199 pełnych tabel SGJP i ich hashe, wszystkie 7192 wskazane analizy oraz 15 621 odwołań do form.
To kontrola zgodności z materiałem źródłowym, nie dodatkowe 15 621 niezależnych poświadczeń językowych.
Pełne oceny każdej rodziny: [raport recenzenta](../analysis/findings/round4/family-review.md), [macierz 110 ocen](../analysis/findings/round4/family-review.json).

Przegląd znalazł słabsze uzasadnienia i uzupełnił je:

| Rodzina | Ustalenie | Skutek dla propozycji |
|---|---|---|
| `utytułować` | Same użycia przymiotnika były za słabą podstawą całego czasownika. Odczytano bezpośrednie użycia czasownikowe w [Gazecie Uniwersyteckiej UŚ, 2005](https://gazeta.us.edu.pl/node/225861) i [sprawozdaniu szkoły za 2023](https://zss-szamotuly.pl/osiagniecia/). Siedem dodatkowych sond KWJP dało zero. | 69 form pozostaje; uzasadnienie uzupełnione |
| `szewron` | Trzy podobne teksty o logo nie są trzema mocnymi niezależnymi dowodami. [WSJP: naszywka](https://wsjp.pl/haslo/podglad/110989/szewron/5262617/naszywka) potwierdza pospolite znaczenie i zgodną odmianę. | 10 form pozostaje; uzasadnienie skorygowane |
| `odstawka` | Dodatek to tylko `odstawce`; `odstawkę` było przyjęte wcześniej. | Bez rozszerzenia na pełny paradygmat |
| `szacowny` | SGJP podaje stopień wyższy bez dodatkowej dawności; odczytane znaczenie WSJP pokazuje stopień równy. Brak tabeli nie jest jawnym zakazem stopniowania. | 22 formy pozostają; rozbieżność i średnia pewność jawne |

Przegląd potwierdza konkretną paczkę. Nie rozstrzyga wszystkich znaczeń tych rodzin ani pozostałych 2367 wcześniejszych kandydatów.

## 3. Dlaczego POP traci 2430 form

| Mechanizm | Członkowie rankingu | Ubytki form |
|---|---:|---:|
| Cały blok jednakowej miary przestaje mieścić się w limicie | 111 w 108 jednostkach | 2422 |
| Własna miara `wypełzły` przestaje mieścić się w tym samym progu | 1 | 8 |
| Razem, kategorie rozłączne | 112 | **2430** |

Jednostki i miary pierwszej grupy pozostają identyczne. Miara własna `wypełzły` też się nie zmienia: ranga przechodzi z 45030 na 45060, a nowy próg wynosi 45059.
To ten sam poziom punktacji co w utraconym bloku. Po dodatkach zostaje 91 miejsc, a cały następny blok potrzebuje 116 leksemów.

Każda utracona forma jest przypisana do przyczyny w [pełnym pomiarze](../analysis/findings/round4/pop-losses.json).
Odczyt kodu, [ADR-007](../../../../../docs/adr/ADR-007-metoda-pop-v1.md) i testów potwierdza zgodność z obecną metodą: limit liczy leksemy przed przycinaniem, remis wchodzi cały albo wcale.
Nie wykazano błędu implementacji. Utrata miejsca w POP nie oznacza utraty poprawności ani spadku zmierzonej częstości.

**Rekomenduję zachować limity 60 000/20 000 i pełne bloki remisów.** Podniesienie limitu lub trwała unia ze starą listą tylko dla tej paczki zmieniłyby kryterium pod pożądany wynik.
Ocena, czy taka rotacja jest akceptowalna dla użytkowników, pozostaje decyzją o metodzie POP.

## 4. Co naprawdę dzieje się z `dag` i `dekagram`

W danych `dag` jest wspólnym zapisem dla `daga` i `dekagram`. To jedyna forma utrzymująca `daga` w populacji rankingu.
Wspólna forma w NKJP łączy te leksemy w grupę o randze 10311, mieszczącej się w POP0.

Sam `dekagram` ma własną rangę **21474**, poniżej granicy POP0 **11638**. Zostaje dzięki wyjątkowi dla najmocniejszego członka wybranej grupy.
Po cofnięciu `dag` grupa się rozpada. `Dekagram` ma tę samą własną miarę **0,017383523**, teraz jako samodzielna jednostka o randze **21476**. Pozostaje w POP i STANDARD, traci 10 form w POP0.

To skutek utraty wsparcia grupy, nie pogorszenia własnego dowodu `dekagram`.
Nazwa statusu `PROPER_SHARED` jest tu myląca: kod używa jej również dla zwykłego leksemu spoza dopuszczonej populacji, nie tylko nazwy własnej.

Kontrole przyczynowe:

- Usunięcie samego `dag` przy zachowanej bazowej populacji rankingu usuwa z obu list wyłącznie `dag`.
- Sama punktacja KWJP przy zachowanych grupach NKJP: `dekagram` jest poza POP0 już przed cofnięciem.
- Pełne wyłączenie NKJP również z budowania grup: ten sam wniosek. To oddzielna kontrola, nie to samo co zmiana wyłącznie punktacji.

[Ślady i kontrole](../analysis/findings/round4/dag-mechanism.json), [niezależny przegląd mechanizmu](../analysis/findings/round4/pop-method-review.md).
Nie rekomenduję wyjątku utrzymującego akurat `dekagram`. Ewentualna zmiana zasad grupowania wymagałaby oceny całej populacji; ten przypadek sam jej nie uzasadnia.

## 5. Dwanaście obecnych przyjęć

Przeczytano i oceniono **771 konkordancji dokładnych zapisów**, w tym 120 znanych z rundy 3 i 651 dodatkowych, oraz **25 kontekstów z 7 uzupełniających zapytań fleksyjnych**.
Dobór: pierwsze 50 i ostatnia strona; przy najwyżej 100 wynikach cała odpowiedź. To nadal dobór celowy, nie pełny przegląd większych wyników.
Każdy wiersz ma identyfikator i ocenę. Sprawdzono też wszystkie **30 obecnie przyjętych analiz** tych 12 zapisów oraz źródła słownikowe i teksty autorskie.
[Macierz analiz i notatek](../analysis/findings/round4/current-twelve.json), [raport](../analysis/findings/round4/current-twelve.md).

| Zapis | Wynik badawczy | Dlaczego |
|---|---|---|
| `bad`, `dag`, `dyr`, `reż`, `sie`, `sui`, `wiosenno`, `świąteczno` | **24 konkretne analizy do osobnej decyzji o cofnięciu** | Rozszerzone dowody nadal dotyczą innych zastosowań: obcego języka, skrótów, innej fleksji lub członów złożeń. Nie potwierdzają przyjętych analiz. |
| `sek` | **Wstrzymać** — 2 analizy | [WSJP](https://wsjp.pl/haslo/podglad/119510/sek) opisuje właściwą nazwę wina bez kwalifikatora dawności, choć przykład pochodzi z 1958. Konflikt z SGJP wymaga rozstrzygnięcia; skróty sekund nadal nie są dowodem tego rzeczownika. |
| `um` | **Wstrzymać** — 2 analizy | Znaleziono 16 właściwych kontekstów: 9 użyć przedmiotowych/relacjonowanych i 7 metajęzykowych. Wszystkie pochodzą od jednego autora, Mariusza Wilka, świadomie przywracającego dawne słowo. To spór o granicę archaizowania, nie brak polskiego użycia. |
| `moko` | **Wstrzymać** — 1 analiza | Żywa nazwa tatuażu maoryskiego ma poświadczenia, ale nie dowodzi przyjętego wołacza od `moka` — kawy. Wymaga osobnej ścieżki leksykalnej. 99 trafień KWJP pochodzi z dwóch mocno zależnych tekstów. |
| `tem` | **Wstrzymać** — 1 analiza | Termin bizantyński ma użycia w [ZPE](https://zpe.gov.pl/a/przeczytaj/DaOziCkqx) i [artykule Kiriła Marinowa, tom 2019](https://pressto.amu.edu.pl/index.php/bp/article/view/20525). Nie ustalono zgodności znaczenia i rodzaju z dawnym `tema/f` w bazie. |

**Nie rekomenduję cofnięcia całej dwunastki.** Nowe dowody zmieniają ocenę czterech przypadków. Dla pozostałych ośmiu rekomendacja dotyczy wskazanych analiz, nie twierdzenia o nieistnieniu słowa lub zakazu każdej możliwej ścieżki.
Na przykład łacińskie `sui` w polskim tekście nie potwierdza odmiany dawnego `suja`; ewentualne dopuszczenie takiego komponentu wymagałoby własnej podstawy.
Nie włączamy nowych pełnych paradygmatów `moko` ani `tem` na podstawie samych zapisów.

Źródło Khan Academy dla `temą` jest pomocniczym tropem z indeksu wyszukiwarki: pełnego tekstu nie udało się odczytać, data przekładu nie jest ustalona.
Nie stanowi samodzielnego rozstrzygnięcia. Szkolny PDF z `daga` też nie został uznany za zweryfikowane współczesne poświadczenie.

## 6. Wpływ i rekomendacja

Ponieważ przegląd nie zmienił zbioru 2382 dodatków, główny wynik pozostaje taki jak w rundzie 3:

| Lista | Dodatki | Ubytki | Zmiana netto |
|---|---:|---:|---:|
| STANDARD | 2382 | 0 | +2382 |
| POP | 2372 | 2430 | −58 |
| POP0 | 481 | 0 | +481 |

Obecne przyjęcia są w tym scenariuszu zachowane. Kontrole pierwszych 20 000 częstych form dla POP i 5000 dla POP0 nadal nie wykazują braków.
Nie oznacza to automatycznie braku dotkliwych zmian poza tym zakresem.

Rekomenduję przyjąć tę paczkę jako wynik badania do osobnej decyzji wdrożeniowej, przy zachowaniu obecnej metody POP.
Implementacja nadal wymaga uzgodnionego mapowania dowodu znaczenia i odmiany do przypiętych analiz oraz sposobu utrzymania tych decyzji.
Oceny cofnięć powinny stanowić osobną decyzję. Nie rekomenduję kolejnego ogólnego poszerzania próbki.

### Osobna wrażliwość: dodatki i cofnięcie wskazanych 8 zapisów

Policzono również skutki ewentualnego cofnięcia 24 wskazanych analiz, które są jedynymi przyjętymi ścieżkami dla ośmiu zapisów.
To kontrolny scenariusz, nie zatwierdzenie cofnięć. Cztery wstrzymania pozostają bez zmian.

| Lista | Dodatki | Ubytki | Zmiana netto | Liczba form po zmianie |
|---|---:|---:|---:|---:|
| STANDARD | 2382 | 8 | +2374 | 3 092 568 |
| POP | 2372 | 2437 | −65 | 1 227 185 |
| POP0 | 481 | 14 | +467 | 388 976 |

POP0 traci `dag`, `reż`, `wiosenno`, `świąteczno` oraz 10 form `dekagram`.
W POP dodatkowe 7 ubytków to wskazane cofnięcia poza `bad`, którego już wcześniej nie było w POP.
Obie kontrole częstych form przechodzą. [Pełny pomiar z hashem ocen i 24 kluczami analiz](../analysis/findings/round4/eight-sensitivity.json).
Wariant cofnięcia 12 z rundy 3 pozostaje wyłącznie historyczną analizą wrażliwości; nie jest aktualną propozycją po nowych dowodach.

## 7. Walidacja i ograniczenia

Koordynator uruchomił 11 istniejących testów, recenzent POP 25. Wszystkie przeszły; zbiory częściowo się pokrywają, więc nie sumujemy ich do 36 różnych testów.
Sprawdzono dokładne zbiory list, pełne przypisanie ubytków i zgodność kodu z ADR. W przeglądzie wykryto i poprawiono nieprecyzyjny zakres jednej kontroli KWJP; oba warianty są jawnie zapisane.

Pewność pomiarów i przyczyn jest wysoka dla przypiętego wejścia. Pewność ocen językowych pozostaje średnia.
Niezależny kontekst recenzji ogranicza powtarzanie założeń, ale nie zapewnia niezależności modeli, źródeł ani anotacji korpusowej.
Data dokumentu/edycji 2021–2022 nie dowodzi daty powstania tekstu. Celowe przeglądy nie estymują błędu w całym słowniku.

Skrypty badawcze: `analysis/round4_pop.py`, `analysis/round4_family_review.py`, `analysis/round4_twelve.py`.
Kontrola kompletności: `analysis/round4_validate.py`; [wynik](../analysis/findings/round4/validation.json).
`round4_pop.py` odtwarza bazę, przyczyny ubytków i kontrole; tryb `sensitivity_eight` liczy osobno wariant 8 cofnięć.
Surowe odpowiedzi i korpusy pozostają w ignorowanym `tmp/research-issue4/`; publiczne artefakty zawierają własne oceny, identyfikatory, hashe, metryki i odsyłacze.
Nie zmieniono kodu produkcyjnego, reguł, list, wydania ani wiki.
