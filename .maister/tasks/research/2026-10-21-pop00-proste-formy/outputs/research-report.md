# POP00 — słowa i odmiany znajome zwykłemu graczowi

## TL;DR
Pomysł jest wykonalny, ale sam próg częstości form usuwa także codzienny język.
Rekomenduję POP00 oparty na leksemach POP0, zwykłej odmianie i dowodach dla form nietypowych.
Częstość powinna wspierać wybór; nie zastępuje oceny rozpoznawalności przez graczy.
Zakończono rozpoznanie i pomiar progów; trwa bramka odbioru, nie zatwierdzono polityki ani wydania.

## Key Decisions
- Punkt odniesienia: wydane pop-v3, 388 763 formy i 13 896 leksemów POP0.
- Wyniki progów są eksperymentem; nie wybrano docelowej liczebności ani progu POP00.
- Zalecenie dotyczy słownika znajomości. Użycie go jako zasad stołu wymaga osobnej decyzji.

## Open Questions / Risks
- Co dokładnie uznamy za zwykłą odmianę, a co za formę wymagającą osobnego dowodu?
- POP0 samo pomija pewne zwykłe słowa. Ograniczenie form nie naprawi wyboru leksemów.
- Brak ocen graczy i symulacji: nie znamy jeszcze wpływu na naturalność ruchów i grywalność.

## 1. Pytanie, metoda i pokrycie
Celem jest język osoby grającej bez treningu słownikowego: słowa, które rozpoznaje,
oraz odmiany brzmiące naturalnie. Nie utożsamiamy tego z krótkimi słowami, wiekiem,
wykształceniem ani formalnym standardem prostego języka.

Przeczytano kod selekcji, konfigurację, odpowiednie testy, ADR, wcześniejsze badania
i aktualny stan issue #6. Wykonano pomiar na wydanym POP0 i przypiętych CSV KWJP.
Porównano dokumentację korpusu, badania rozpoznawania słów i definicję prostego języka.
Wszystkie pięć kategorii planu zbadano; ograniczenia dostępu opisano w
[dowodach zewnętrznych](../analysis/findings/external-evidence.md).

Kod bazowy: `4f74b42fb4b6d3c256e079f30eebc6cac8d782a9`, zgodny z remote main odczytanym 2026-10-21.
Hash POP0 odpowiada assetowi [wydania pop-v3](https://github.com/robmar-net/literaki-slownik/releases/tag/pop-v3).
To rozpoznanie możliwości, nie walidacja gotowego słownika.

## 2. Co dzisiaj robi POP0
Wybór dotyczy leksemów, po czym przejmowana jest pełna odmiana i konstrukcje w STANDARD.
Nie ma filtra popularności każdego napisu. Próg wyboru leksemów odtwarza dawny limit,
nie wynik badań znajomości. Wyjątki homonimiczne dodatkowo sprawiają, że nie każdy leksem
ma własny silny dowód. [Kod i historia](../analysis/findings/code-and-history.md).

To wyjaśnia, dlaczego znajomy czasownik może wnosić do POP0 nietypową formę.
W rzeczywistym pakiecie są zarówno `zrobiłem`, jak i `remontowałoś` oraz `przeczytałobym`.
Wszystkie trzy mają analizy SGJP; poprawność i znajomość to różne kryteria.

## 3. Pomiar: samo cięcie częstością
Dokładny zapis małymi literami z KWJP orth/all; IPM = wystąpienia na milion tokenów.
Brak wiersza traktujemy jako brak dowodu, choć w poniższym naiwnym filtrze powoduje odrzucenie.
Progi odnoszą się do opublikowanego IPM zaokrąglonego do dwóch miejsc.

| Wariant | Formy | Udział form POP0 | Zachowana masa obserwowanych użyć POP0 |
|---|---:|---:|---:|
| Pełny POP0 | 388 763 | 100% | 100% |
| Dowolny opublikowany wiersz | 138 981 | 35,75% | 100% |
| IPM ≥ 0,1 | 125 769 | 32,35% | 99,87% |
| IPM ≥ 0,5 | 75 278 | 19,36% | 98,17% |
| IPM ≥ 1 | 53 443 | 13,75% | 96,05% |
| IPM ≥ 2 | 34 101 | 8,77% | 92,33% |
| IPM ≥ 5 | 16 586 | 4,27% | 84,89% |

Ostatnia kolumna liczy tylko opublikowane małoliterowe tokeny KWJP należące do POP0.
**96,05% nie oznacza 96% języka, znajomości, ruchów ani partii.** Względem całej opublikowanej
małoliterowej listy orth/all wariant IPM ≥ 1 ma 82,06%, a bazowy POP0 85,43%.
To także inny mianownik niż publikowane dla POP0 pokrycie leksemowe 94,6%.

Źródło: [odtwarzalny skrypt](../analysis/measure_forms.py),
[pełny wynik i hashe](../analysis/evidence/form-measurement.json).

### Dlaczego wysoki procent pokrycia myli
- 249 782 form POP0 nie ma dokładnego wiersza w liście KWJP. Część jest rzadka,
  część ukrywa tokenizacja. KWJP publikuje tylko jednostki z co najmniej pięcioma wystąpieniami
  w całym korpusie. [Dokumentacja KWJP](https://kwjp.pl/lists/doc/about/).
- `zrobiłem`, `zrobiłam`, `byłem`, `byłam`, `zrobiliśmy` nie mają wiersza w badanej liście,
  chociaż są w POP0. Kod projektu dokumentuje segmentację `zrobił` + `em`.
  [Pomiar](../analysis/evidence/form-measurement.json), `literaki_slownik/pop.py:1903–1904`.
- Dużo masy daje niewiele bardzo częstych form. Zachowanie tej masy nie chroni
  rzadziej używanego, lecz oczywistego narzędnika, wołacza czy rozkaźnika.

### Sprawdzone przykłady
| Forma | IPM orth/all | Co zrobi próg 1 |
|---|---:|---|
| kotem | 4,49 | zostawi |
| kotach | 0,86 | odrzuci |
| czytaj | 5,45 | zostawi |
| czytajcie | 0,37 | odrzuci |
| czytając | 9,24 | zostawi |
| miłymi | 0,58 | odrzuci |
| miłemu | 0,19 | odrzuci |
| zrobiłem | brak wiersza | odrzuci |
| remontowałoś | brak wiersza | odrzuci |
| przeczytałobym | brak wiersza | odrzuci |

Wszystkie formy tej tabeli są w POP0. Ocena „zwykła/nietypowa” jest hipotezą językową do oceny
przez ludzi; obecność, IPM i wynik filtra są pomiarem.

Próg 1 usuwa też wszystkie formy **661 z 13 896 leksemów (4,76%)**, m.in. `aktualizować`,
`anulować`, `aksamitny`, `aha`. Konstrukcje nie ratują tych leksemów.
Nie spełnia więc dosłownego warunku „te same leksemy”.
[Pomiar leksemów](../analysis/evidence/lexeme-measurement.json).

### Kontrole czułości
Warunek IPM ≥ 1 w całym KWJP **lub w fikcji** daje 59 954 formy zamiast 53 443:
ratuje np. `kotach` (fikcja 1,46), lecz nadal nie rozwiązuje segmentacji ani `miłemu`.
Fikcja jest tylko przybliżeniem mniej formalnego rejestru, nie korpusem rozmów.
Złożenie wielkich i małych liter daje 141 400 poświadczonych form zamiast 138 981,
ale zaciera pochodzenie od nazw własnych. Nie przyjęto tego jako automatycznej korekty.

Próg 1 redukuje zasób 2–3-literowy z 676 do 454, a 7-literowy z 25 777 do 8 033.
To sygnał potrzeby testów gry, nie zmierzony spadek wyników. Dane długości są w wyniku skryptu.

## 4. Czy wystarczy usunąć trudne odmiany?
**Nie usuwałbym całych kategorii:** pierwszej/drugiej osoby, wołacza, rozkaźnika ani wszystkich
imiesłowów. Wyrzucimy wtedy codzienny język, np. `czytam`, `czytasz`, `czytaj`, `czytając`.
Historyczny eksperyment już ujawnił koszt takich cięć, ale dotyczył innego POP.
[Historia](../analysis/findings/code-and-history.md).

Sensowniejsze jest badanie węższych klas, np. nijakiej pierwszej/drugiej osoby
(`remontowałoś`, `przeczytałobym`) i rzadkich wariantów końcówek.
W POP0 14 010 form ma przynajmniej jedną analizę rodzaju nijakiego i osoby pierwszej/drugiej.
**Nie jest to liczba do prostego odjęcia:** alternatywna analiza może uzasadniać zachowanie napisu.
[Pomiar morfologii](../analysis/evidence/lexeme-measurement.json).

Obecny helper wykluczania klas przepuszcza konstrukcje poza filtrem. Trzeba objąć nimi także
konstrukcje i zachować alternatywne dopuszczone interpretacje. To znana granica istniejącego
narzędzia, nie powód, by uznać taki filtr za gotowy. [Audyt kodu](../analysis/findings/code-and-history.md).

## 5. Porównanie możliwych dróg
To rekomendacje wynikające z rozpoznania; formalny wybór rozwiązania pozostaje przed nami.

| Droga | Zaleta | Główne ryzyko | Ocena |
|---|---|---|---|
| Twardy próg częstości każdej formy | prosty, mała lista, łatwo mierzyć | segmentacja, dziurawe odmiany i utrata leksemów | dobry wariant kontrolny, słaby produkt samodzielnie |
| Pełny POP0 minus wąskie nietypowe formy | zachowuje produktywną odmianę | zostawia rzadkie formy i dziedziczy słabe leksemy POP0 | bezpieczniejszy pierwszy kandydat |
| Częste formy + zwykła odmiana; nietypowe wymagają mocniejszego dowodu | łączy znajomość podstawy z naturalną fleksją | trzeba określić klasy i skalibrować wyjątki | rekomendowany kierunek POP00 |
| Preferowanie znajomych ruchów bota bez nowego walidatora | może osiągnąć cel widoczny w grze | nie daje samodzielnej listy, wymaga oceny wszystkich słów ruchu | alternatywa, jeśli celem jest zachowanie bota |

Rekomendowany wariant to: **te same leksemy jako punkt wyjścia, zwykłe odmiany chronione,
forma nietypowa bez automatycznego biletu za popularny leksem**. Nie proponuję gwarantowania
kilku najczęstszych form na leksem: rzadki leksem dostałby wtedy sztuczny przywilej,
a normalna odmiana nadal mogłaby być niepełna.

Jeśli celem jest bot, miarę znajomości warto stosować do wszystkich słów powstających w ruchu,
w tym krzyżówek. Wybór łatwego słowa głównego nie gwarantuje łatwego całego ruchu.
To zalecenie projektowe, nie wynik testu silnika w tym badaniu.

## 6. Co można zrobić lepiej niż tylko obcinać POP0
Oddzielić trzy osie: **znajomość leksemu, naturalność formy, łatwość znalezienia ruchu**.
Gracz może rozumieć słowo, a nie wymyślić go z siedmiu liter. Mała lista nie jest samodzielnym
modelem początkującego gracza.

Samo dziedziczenie leksemów POP0 ma sufit: `nieładnie` ma w KWJP IPM 1,57, ale nie ma go w POP0;
`siedmioletni` także jest poza POP0. To sprawdzone przykłady ograniczenia zakresu, nie propozycja
automatycznego dodania tych haseł. Zwykłość leksemów powinna być osobnym audytem,
powiązanym z otwartą kalibracją [#6](https://github.com/robmar-net/literaki-slownik/issues/6).

Badania [SUBTLEX-PL](https://biblio.ugent.be/publication/5878584) uzasadniają porównywanie
częstości z różnych rejestrów. Ewentualne dane napisowe mogą pomóc, ale wymagają audytu
wersji i warunków; nie są konieczne do pierwszego kandydata na obecnych danych.
Definicja [prostego języka](https://jasnopis.pl/prosty-jezyk/) dotyczy całych komunikatów.
Tutaj trafniejsze określenie celu to „znajome słowa i naturalne odmiany”.

## 7. Zalecany następny eksperyment
Po odbiorze rozpoznania warto porównać trzy kandydaty: samą częstość jako kontrolę,
POP0 minus wąskie nietypowe formy oraz wariant łączący częstość i ochronę zwykłej odmiany.
Nie wybierać teraz wielkości „50 tys.” ani „100 tys.” tylko dlatego, że wygląda wygodnie.

1. Ustalić zasady zwykłej odmiany na konkretnych rodzinach; obsłużyć segmentację.
2. Przygotować zrównoważoną próbę zachowanych i odrzuconych form: długości, części mowy,
   częstości, konstrukcje, homonimy, codzienne dziedziny. Obecne przykłady pozostają zestawem diagnostycznym.
3. Zebrać niezależne oceny: „znam słowo”, „ta odmiana brzmi zwyczajnie”, „zdziwiłaby mnie w grze”.
   Operator może zrobić pilot; twierdzenie o graczach wymaga grupy docelowej.
4. Zamrozić reguły, a później ocenić osobny zbiór, nie użyty do ich wyboru.
5. Zmierzyć ruchy na tych samych pozycjach/rękach: odsetek niezrozumiałych słów,
   liczbę dostępnych ruchów, wymiany, długości i straty punktowe. Nie optymalizować tylko zwycięstw.
6. Zachować `POP00 ⊆ POP0 ⊆ STANDARD`, jeśli decyzja pozostawi obecne leksemy jako granicę.
   Rozszerzenie o codzienne leksemy spoza POP0 to odrębna, jawna decyzja.

To plan dalszej walidacji, nie wykonane badanie ludzi ani gotowa specyfikacja implementacji.

## 8. Pewność, luki i bramka
**Wysoka pewność:** stan POP0, mechanika generatora, liczby progów, wskazane fałszywe odrzucenia.
**Średnia:** przewaga proponowanego połączenia morfologii i użycia jako kierunku badawczego.
**Nieustalone:** najlepsze reguły, docelowy rozmiar, ocena ludzi i efekt w partiach.

Więcej masowych progów na tych samych CSV nie usunie błędu tokenizacji ani nie zmierzy znajomości.
Warto przejść do porównania konkretnych wariantów i próby jakości; nie ma jeszcze podstaw do wydania.

**Bramka research-foundation:** przyjąć wyniki rozpoznania albo wskazać, co pogłębić.
Burza pomysłów i projekt wysokopoziomowy pozostają osobnymi decyzjami kolejnego etapu.

## Źródła i odtworzenie
Rejestr: [sources.md](../planning/sources.md). Kod/historia i literatura: dwa pliki w
`analysis/findings/`; wyniki i hashe w `analysis/evidence/`.
Uruchom z dowolnego katalogu: `python3 <katalog-zadania>/analysis/measure_forms.py`
oraz `python3 <katalog-zadania>/analysis/measure_lexemes.py` przy dostępnych lokalnych wejściach.

Atrybucje danych: SGJP/Morfeusz, snapshot 20260823; KWJP100, IPI PAN,
[repozytorium źródłowe](https://github.com/ipipan/kwjp100-varia), CC BY 4.0.
Utworzono agregaty i mały zestaw przykładów, nie zmieniano danych wejściowych.
Wybór leksemów odziedziczony z POP0 korzysta też z NKJP; pełne warunki i autorzy w
[ATTRIBUTIONS.md](../../../../../ATTRIBUTIONS.md) i pakiecie pop-v3.
Żaden z autorów źródeł nie jest wskazywany jako popierający rekomendację.
