# Kontrakcje, mobilne zakończenia i ślady korpusowe

## TL;DR
Wdrożono zatwierdzone A: dokumentacja SGJP potwierdza całe18kontrakcji.
Pełny przegląd klasy dał57analiz z dowodem i24z nierozstrzygniętym dowodem; nie są to końcowe listy.
Dodano64kandydatów zamkniętej klasy16hostów z_aglt_by oraz powiązania całych konstrukcji z KWJP.
Siedem errat winien jest widocznych w explain, bez zmiany surowych rekordów.

## Key Decisions
- Przyimek i ń muszą pochodzić z jednego eksportu, uzgodnić gen/acc i mieć udokumentowaną postać. Ń to on:S, sg, m1/m2/m3, ter, nakc, praep. Nie doklejamy ń do dowolnego przyimka.
- Status accept w linguistic_evidence dotyczy tylko dowodu całego napisu. Kandydat pozostaje candidate_not_qualified; język/gra/profil/lista wymagają innych warunków. Źródłowe pisane_łącznie_z_przyimkiem jest zachowane, fulfilled_component_requirements opisuje jego spełnienie przez konstrukcję.
- Osiem form poza enumeracją SGJP pozostaje unresolved, z pełnymi składnikami; nie uruchomiono akceptacji przez analogię ani automatycznej odmowy. Pełne wydanie pozostaje zablokowane do rozstrzygnięcia dowodów.
- Z_aglt_by to zamknięte lemma+POS z przypiętego segmenty.dat:13comp i3part, łącznie16hostów, cztery niewokaliczne końcówki. Samo zakończenie by nie wystarcza; niby nie jest hostem. Niezależne partykułowe aby:T nie staje się spójnikowym aby:M. By samo zachowuje wcześniejszy konstruktor bez dublowania.
- Evidence_candidate może wskazywać dokładnie jeden leksem, bezpośrednią formę lub candidate_key konstrukcji. F pozostaje wyłącznie w corpus_evidence. Lemma korzenia i bigram segmentów nie dowodzą F całej nowej formy.
- Indeks game_key zawęża dopasowanie konstrukcji, a orth sprawdza następnie dokładną NFC i wielkość liter; nie wykonujemy skanowania wszystkich kandydatów dla każdej jednostki KWJP.
- Explain odczytuje też wcześniejszy schemat evidence_candidate, bez migracji lub zmian starej bazy.
- Errata osoby winien dotyczy siedmiu sprawdzonych (lemma_id,forma,surowy_tag) w źródle o konkretnym SHA256. Nie jest regułą endswith ani poprawką importu. Raw_tag i jego rozwinięcia pozostają widoczne obok corrected_tag i corrected_expanded_tags.

## Open Questions / Risks
- Pozostałe grupy hostów mobilnych, pełna semantyka kwalifikatorów/kategorii i historyczna pisownia nadal wymagają domknięcia. Nie oznaczono G3/G4/G5/G6 jako complete.
- Pełna kwalifikacja nadal nieaktywna. Wszystkie końcowe oceny członkostwa pozostają unresolved, także dla potwierdzonego dowodu konstrukcji.
- Zmiana relacji evidence_candidate dotyczy nowych baz, schemat generatora nie był jeszcze wydany. Readonly starych przebiegów jest sprawdzony.
- Próby runtime to projekcje wymaganych klas, nie dwa pełne odtworzenia G8. Wyszukiwanie ośmiu pozostałych form nie dostarczyło potwierdzonego polskiego opracowania; wyniki słowackie i niepowiązane nie są dowodem polskiej konstrukcji.

## Dowody i runtime

[Przyimki](preposition-runtime.json):169źródłowychinterpretacji(prep,ń,doń) wybranych z pełnego G2 readonly;81kandydatów i162składniki.57analiz/18napisów ma dowód,24analizy/8napisów pozostają unresolved. Powtórzenie zachowuje klucze i nie dopisuje kandydatów, FK/integrityOK.45,218s obejmuje projekcję, dwa materializowania i kontrole. W rzeczywistym explain doń zachowuje donia oraz3analizy kontrakcji; zań ma6analiz dla dwóch przypadków. Nadń nie jest generowane. Stare powiązania zamek czytelne:20obserwacji, żadnej pewnej tożsamości sensu.

[Hosty by](mobile-by-runtime.json):280źródłowychinterpretacji wszystkichcomp/part/aglt z G2 readonly;64nowe kandydaty16właściwychhostów, plus8wcześniejszychby. Powtórzenie bez dopisania,144składniki,FK/integrityOK.40,497s obejmuje projekcję/dwaprzebiegi/kontrole. Abyśmy,gdybym,obyś,kiebyście zachowują właściweanalizy i etykiety; nibym,nibyśmy,byem bezkandydata. Pełny zakres pozostałych mobilnych hostów nie jest zastąpiony tą grupą.

[Erraty](winien-explain-runtime.json):wszystkie7rzeczywistych zapytań do pełnego G2 readonly dają raw_tag sec i osobną erratę pri, także w tekście; nie dopisano napisów ani zmodyfikowano źródła.

Źródła pierwotne:[SGJP](https://sgjp.pl/static/pdf/Podstawy_teoretyczne_SGJP.pdf) §6.4.1,6.6.1,7.3,7.5,7.8,9.1; przypięty segmenty.dat143–147,760–777,822,1896–1905. Metryki/hash w config/generator/evidence.json. Brak nowych źródeł leksykalnych, aktywacji WSJP lub Wikisłownika i brak kopiowania reguł SJP.pl.

## Test-first i regresje
Trzy testy kontrakcji: red brak funkcji → green. Test explain: red brak konstrukcji → green; test persistence dodany jako kontrola integracji po konstruktorze (już green, nie deklarujemy red). Test linków całej konstrukcji: red UNMATCHED → AMBIGUOUS, następnie green; test explain korpusu: red brakobserwacji → właściwyORTH,F=5bezLEMMA,F=99. Test mobilnej klasy: red brak funkcji → green; test explain: red brakśladu → green. Dwa testy errat: red brakfunkcji → green. Ostatni zestaw focused52/52; pełna suita uruchomiona przy końcu przyrostu, rezultat zapisany w work-log.
