# Dobór próbek do kontroli jakości

## TL;DR
Moduł `literaki_slownik.quality` realizuje zatwierdzony dobór quality-v1.
Wybiera do 30 różnych jednostek na warstwę, zachowując populacje i nakładanie prób.
Próbka i szablon przeglądu mają status UNREVIEWED; nie nadają VERIFIED.
Nowe build zapisują trzy diagnostyczne próbki; pełna macierz i odbiór pozostają do wykonania.

## Key Decisions
- SHA256 liczony z kanonicznego JSON `[seed,warstwa,klucz]`, UTF-8 bez spacji. Przy remisie rozstrzyga klucz.
- Wejście każdej warstwy jest posortowanym strumieniem stabilnych kluczy. Duplikaty liczymy raz; niesortowane wejście jest błędem.
- Pamięć wyboru ograniczamy do 30 jednostek na warstwę, zamiast przechowywać pełne populacje w Pythonie.
- Pusta warstwa ma EMPTY_NOT_COVERAGE. Wybrane jednostki mają SAMPLED_NOT_VERIFIED.

## Open Questions / Risks
- Dobór warstw opiera się na utrwalonych analizach i etykietach; nie rozstrzyga dopuszczalności. Pełne pokrycie klas zależy od domknięcia macierzy.
- Szablon wiąże przegląd hashami z próbką, indeksem kanonicznym i dowodami. Weryfikacja wypełnionego przeglądu będzie częścią G7.
- Próba nie jest statystyczną gwarancją bezbłędności i nie zastępuje kontroli kompletności macierzy.

## Kontrakt i sprawdzenie

`sample_strata(strata, config)` przyjmuje mapę identyfikatorów warstw do posortowanych strumieni kluczy. Klucz musi identyfikować jednostkę merytoryczną; jednostki korpusowe i słowa powinny mieć odrębne przestrzenie nazw. W raporcie są wielkości populacji, prób, hashe wybranych kluczy, liczba unikalnych jednostek i lista przecięć prób.

`review_template(sample, canonical_index_sha256=..., evidence_sha256=...)` tworzy pozycje z pustą oceną, recenzentem i uzasadnieniem źródłowym. Nie przypisuje poprawności domyślnie. Jeśli próbka zawiera items, dołącza pełne jednostki do selected_unit i wymaga zgodnego pokrycia bez duplikatów.

Konfiguracja `config/generator/quality.json` jest zamknięta dla zatwierdzonej quality-v1. Druga zamknięta konfiguracja to `pop-quality-v1` (POP, niżej). Inna wersja, seed, limit lub kodowanie wymaga jawnej aktualizacji kontraktu.

Testy: `python3 -m unittest tests.test_quality`. Obejmują znany hash UTF-8, wybór najmniejszych hashy, limit, powtórzenia, remisy, puste grupy, przecięcia, błędne wejścia i powiązanie przeglądu z hashami.

Diagnostyczne użycie na rzeczywistych powiązaniach lemma-all zapisano w [quality-runtime.json](../../.maister/tasks/development/2026-10-04-generator-broad-standard/analysis/evidence/quality-runtime.json). Nie jest to pełny odbiór G8.

## Diagnostyczne próbki utrwalonych analiz

sample_persisted_analyses dobiera do30 stabilnych kluczy na rodzaj analizy (źródłowe rozwinięcie/konstrukcja/użycie/pozostałość) oraz status każdego wariantu. Dołącza rekord źródłowy i wszystkie warstwy obu wariantów. Build z przypiętym quality zapisuje reports/quality-analyses.json. Wynik UNREVIEWED, full_quality_matrix_pending: nie zastępuje wymaganych warstw słownych/konstrukcyjnych i metod linków pełnego odbioru. Próbka podaje także puste warstwy jako EMPTY_NOT_COVERAGE.

## Próbki słów i powiązań

`sample_word_analyses` dobiera całe klucze słowne; dołącza wszystkie analizy i obie oceny, ślady konstrukcji i źródła. Definicje tematów w przypiętym quality-words służą wyłącznie próbkowaniu. `sample_corpus_links` rozlicza każdą jednostkę KWJP i jej kandydatury, F tylko raz. Build zapisuje quality-words.json i quality-links.json. UNREVIEWED i EMPTY_NOT_COVERAGE pozostają wiążące. [Pomiary i granice](../../.maister/tasks/development/2026-10-04-generator-broad-standard/analysis/evidence/quality-strata-implementation-review.md).

## Próbki POP (`pop-quality-v1`)

- Konfiguracja: `sampling` w `config/generator/pop.json`. Seed `literaki-slownik-pop-v1`, 30 na warstwę, to samo kodowanie co quality-v1.
- Klucze: leksemy (`lemma_id@source_id`) albo formy.
- Warstwy: `pop-granica-wewnatrz`, `pop-granica-zewnatrz`, `pop0-granica-wewnatrz`, `pop0-granica-zewnatrz`, `braki-danych`, `rozbieznosc-korpusow`, `grupy-homonimow`, `pos-<POS>`, `czeste-poza-lista` (formy z 50 000 najczęstszych form KWJP `orth` (all, tylko zapis małymi literami) ze STANDARD, z leksemem w rankingu, których nie ma w POP), `formy-krotkie`, `formy-dlugie`. Pusta warstwa: `EMPTY_NOT_COVERAGE`.
- `pop` zapisuje `reports/sample.json` i `reports/review-template.json` (UNREVIEWED).
- Przegląd: status `REVIEWED`, każda pozycja oceniona, hashe próbki, indeksu jednostek, dowodów i `sha256sums_sha256` (SHA256 pliku `SHA256SUMS` pakietu). Sprawdza go `scripts/check_pop_package.py --review` ([cli.md](cli.md#pop-i-pop0-pop)).
- Przegląd wydania `pop-v1-review.json` jest assetem [Release pop-v1](https://github.com/robmar-net/literaki-slownik/releases/tag/pop-v1).

## Próbki POP00 (`pop00-quality-v1`)

Seed `literaki-slownik-pop00-v1`, po 30 pozycji na warstwę, ten sam algorytm SHA256.
Warstwy rozdzielają każdą przyczynę zachowania/odrzucenia, próg 0,08–0,12 IPM,
brak publikowanego dowodu, konstrukcje, długości i alternatywne analizy.
Przykłady diagnostyczne zatwierdzonego planu są wyłączone z populacji niezależnej próby.
Puste warstwy pozostają EMPTY_NOT_COVERAGE. Automatyczna próbka ma UNREVIEWED.
`scripts/check_pop00_package.py --review` sprawdza pełną próbkę, powody z bazy i hashe przeglądu.
Przegląd technicznej zgodności z polityką nie dowodzi rozpoznawalności przez graczy.

## Próbki TEMATY (`tematy-quality-v1`)

- Seed `literaki-slownik-tematy-v1`, ten sam algorytm SHA256. Warstwy: T1, T2, T3; klucze to leksemy. Warstwy D (dodatki ręczne) próba nie losuje.
- Próba agenta: `min(50, N)` na warstwę (`quality.sample_strata`). Operator: pierwsze `min(30, N)`
  z próby agenta w kolejności rangi (`operator_per_stratum` w `tematy.json`), tylko w warstwach
  z `operator_warstwy` (metoda `tematy-v2`: `["T2", "T3"]`, [ADR-012](../adr/ADR-012-tematy-fala-1.md)).
  Mała warstwa: cała.
- Skala: tak / nie / niepewne. Trafność warstwy = „tak” / N, gdzie N to rzeczywista liczba ocen.
  „niepewne” nie jest ani „tak”, ani „nie”.
- Progi (udziały, dokładne ułamki): test słów oczywistych ≥ 0,70 (wynik całości); T1 „tak” ≥ 0,90;
  T2 „tak” ≥ 2/3 i „nie” ≤ 0,10; T3 „tak” ≥ 2/3; zgodność ≥ 0,80.
- Zgodność: odsetek identycznych ocen na pozycjach ocenionych przez obu. Kappa Cohena na tych samych
  pozycjach, 3 kategorie.
- Kolejność: agent ocenia wszystkie pozycje, hash jego ocen trafia do pliku przeglądu przed stroną
  operatora. Strona nie pokazuje ocen agenta.
- Źródło ocen progu: warstwa z `operator_warstwy` liczy się z ocen operatora (bez nich „czeka”), pozostałe
  (w `tematy-v2`: T1) z ocen agenta. Zgodność liczymy na pozycjach ocenionych przez obu.
- `nie_dotyczy`: `t3_tak` tematu bez `t3`. Nie blokuje „dalej”.
- Budowa daje tylko werdykt `dalej` albo `popraw` z testu słów oczywistych; reszta czeka na przegląd.
  `scripts/check_tematy_package.py --review` liczy werdykt z ocen ([cli.md](cli.md#tematy-tematy)).
- **Fala 1 (#12): bramka z ocen agenta.** Operator nie ocenił R2 (decyzja 2026-10-29, ADR-012
  „Zmiana metody R2”). Na bramce T2 i T3 liczyliśmy z ocen agenta, z tymi samymi progami; zgodność
  „nie dotyczy”. To sposób użycia, nie zmiana kodu: checker dalej czeka na oceny operatora. Wynik bramki
  liczy skrypt zadania `analysis/zestawienie_fali.py` funkcją `verdict` checkera. Agent ocenia surowiej
  niż operator (morze: T2 21/50 wobec 30/30).
