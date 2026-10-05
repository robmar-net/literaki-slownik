# Dobór próbek do kontroli jakości

## TL;DR
Moduł `literaki_slownik.quality` realizuje zatwierdzony dobór quality-v1.
Wybiera do 30 różnych jednostek na warstwę, zachowując populacje i nakładanie prób.
Próbka i szablon przeglądu mają status UNREVIEWED; nie nadają VERIFIED.
Integracja z pełnymi raportami i decyzjami generatora pozostaje do wykonania.

## Key Decisions
- SHA256 liczony z kanonicznego JSON `[seed,warstwa,klucz]`, UTF-8 bez spacji. Przy remisie rozstrzyga klucz.
- Wejście każdej warstwy jest posortowanym strumieniem stabilnych kluczy. Duplikaty liczymy raz; niesortowane wejście jest błędem.
- Pamięć wyboru ograniczamy do 30 jednostek na warstwę, zamiast przechowywać pełne populacje w Pythonie.
- Pusta warstwa ma EMPTY_NOT_COVERAGE. Wybrane jednostki mają SAMPLED_NOT_VERIFIED.

## Open Questions / Risks
- Moduł nie określa przynależności słów do warstw ani nie rozstrzyga dopuszczalności. Warstwy zależą od pełnych analiz i raportów.
- Szablon wiąże przegląd hashami z próbką, indeksem kanonicznym i dowodami. Weryfikacja wypełnionego przeglądu będzie częścią G7.
- Próba nie jest statystyczną gwarancją bezbłędności i nie zastępuje kontroli kompletności macierzy.

## Kontrakt i sprawdzenie

`sample_strata(strata, config)` przyjmuje mapę identyfikatorów warstw do posortowanych strumieni kluczy. Klucz musi identyfikować jednostkę merytoryczną; jednostki korpusowe i słowa powinny mieć odrębne przestrzenie nazw. W raporcie są wielkości populacji, prób, hashe wybranych kluczy, liczba unikalnych jednostek i lista przecięć prób.

`review_template(sample, canonical_index_sha256=..., evidence_sha256=...)` tworzy pozycje z pustą oceną, recenzentem i uzasadnieniem źródłowym. Nie przypisuje poprawności domyślnie ani nie zawiera jeszcze pełnych analiz; te musi dostarczyć etap raportowania.

Konfiguracja `config/generator/quality.json` jest zamknięta dla zatwierdzonej quality-v1. Inna wersja, seed, limit lub kodowanie wymaga jawnej aktualizacji kontraktu.

Testy: `python3 -m unittest tests.test_quality`. Obejmują znany hash UTF-8, wybór najmniejszych hashy, limit, powtórzenia, remisy, puste grupy, przecięcia, błędne wejścia i powiązanie przeglądu z hashami.

Diagnostyczne użycie na rzeczywistych powiązaniach lemma-all zapisano w [quality-runtime.json](../../.maister/tasks/development/2026-10-04-generator-broad-standard/analysis/evidence/quality-runtime.json). Nie jest to pełny odbiór G8.

## Diagnostyczne próbki utrwalonych analiz

sample_persisted_analyses dobiera do30 stabilnych kluczy na rodzaj analizy (źródłowe rozwinięcie/konstrukcja/użycie/pozostałość) oraz status każdego wariantu. Dołącza rekord źródłowy i wszystkie warstwy obu wariantów. Build z przypiętym quality zapisuje reports/quality-analyses.json. Wynik UNREVIEWED, full_quality_matrix_pending: nie zastępuje wymaganych warstw słownych/konstrukcyjnych i metod linków pełnego odbioru. Próbka podaje także puste warstwy jako EMPTY_NOT_COVERAGE.
