# Raport wpływu filtrów

## TL;DR
`literaki_slownik.reports.filter_impact` liczy samodzielne, kolejne i łączne efekty filtrów.
Oddziela odrzucone analizy od kluczy słów pozbawionych wszystkich analiz.
Przetwarza posortowane grupy strumieniowo; nie sumuje nakładających się strat.
Dotyczy dostarczonych analiz, nie domniemanej kompletności wydania.

## Key Decisions
- Klucz odpada dopiero po odrzuceniu wszystkich jego analiz. Jedna poprawna analiza może zachować napis.
- Efekt kolejny przypisujemy w jawnie podanej kolejności; wcześniej odrzucone jednostki nie są liczone ponownie jako nowe.
- Nieznane warunki pozostają unresolved, a nie reject.
- Raport odmawia pominięcia reguły, która odrzuciła którąkolwiek analizę; odmawia też statusów sprzecznych z warunkami.

## Open Questions / Risks
- Pełna integracja z build i wszystkimi konstrukcjami pozostaje do wykonania.
- Pusta populacja ma EMPTY_NOT_COVERAGE, a obecność raportu nie nadaje VERIFIED.
- Liczniki podanych analiz nie obejmują niezbudowanych interpretacji i nie są końcową deltą list BROAD/STANDARD.

## Kontrakt

`filter_impact(groups, variant, rule_order)` przyjmuje iterator grup `{key, analyses}` w rosnącej kolejności kluczy. Każda grupa musi być niepusta, unikalna i zawierać wyłącznie analizy własnego klucza. Format analizy odpowiada `assess_analysis`.

Raport podaje: mianowniki kluczy i analiz, samodzielne odrzucenia, nowe i skumulowane odrzucenia po każdym filtrze, efekt łączny oraz rozkład accept/reject/unresolved dostarczonych analiz po agregacji do kluczy. To rozkład ocen podanych analiz; nie jest deklaracją gotowości listy wydania.

Testy: `python3 -m unittest tests.test_reports`. Pokrywają nakładanie filtrów, usuwanie różnych homonimów przez różne reguły, zmianę kolejności, niewiadome, puste grupy, błędne statusy i niepełną listę filtrów.

[Diagnostyczny runtime](../../.maister/tasks/development/2026-10-04-generator-broad-standard/analysis/evidence/filter-report-runtime.json) obejmuje osiem rzeczywistych kluczy i 15 interpretacji. Znane warunki wielkiej litery i profilu są w jawnej kolejności obok filtra wieku; nie pomijamy ich w raporcie.

## Pokrycie warunków kwalifikatorów

`qualifier_coverage(fields)` przyjmuje unikalne pary (pełne pole kwalifikatorów, dodatnia liczba kompaktowych interpretacji). Używamy inwentaryzacji po deduplikacji, nie surowych wierszy i nie rozwiniętych tagów. Duplikaty pól i błędne liczniki są odrzucane. Raport jest deterministyczny niezależnie od kolejności wejścia.

`labels` zachowuje dokładne etykiety, liczniki i warunki obu wariantów. `fields` wiąże je z pełnymi polami; `unmapped_labels` pokazuje etykiety bez żadnego znanego warunku. `full_qualification_pending` zawsze true: dodatnia ocena jednego warunku nie oznacza akceptacji całej analizy. Brak warunku i brak kwalifikatora nie są automatycznym accept. Przecinek pozostaje częścią etykiety; powtórzona etykieta w polu nie podwaja licznika. Liczniki etykiet i kategorii mogą się nakładać.

Nowe build zapisują reports/qualifier-conditions.json, zachowując INCOMPLETE i reports pending. Istniejący przebieg można zbadać bez modyfikacji:

```sh
python3 scripts/probe_generator_evidence.py --mode qualifier-conditions --database PATH/build.sqlite
```

[Pełny przegląd i wyniki](../../.maister/tasks/development/2026-10-04-generator-broad-standard/analysis/evidence/qualifier-coverage-review.md): 26 etykiet bez warunku, 1 910 interpretacji, dwa identyczne raporty. Nie jest to delta list ani pełny odbiór.

## Logiczna treść bieżącej bazy

Wdrożono A dla25dosłownych oznaczeń bez pełnego objaśnienia: source_label zachowany, gloss_status=unestablished, inne kryteria osobno. Pełny runtime:1908kompaktowych analiz, dwa identyczne raporty, sześć readonly explain; wielka litera Abchaz nadal odrzuca growo. Dodano logical-content bieżącego schematu do build:10zamkniętych relacji, klucze źródłowe zamiast ID, wykrywanie nowych tabel/kolumn i niespójnych FK. Testy potwierdzają identyczność po zmianie ID i zmianę hasha po modyfikacji powiązań/kwalifikatorów. To nie pełny indeks kanoniczny ani odbiór G8.

reports/logical-content.json jest diagnostyczną kontrolą bieżącego schematu; po utrwaleniu decyzji kwalifikacji kontrakt musi zostać rozszerzony. Zmiana kodu lub schematu wymaga nowego build, wcześniejszych baz nie migrujemy.

## Niewiadome zapisanych ocen

Nowe build tworzą reports/unresolved.json: osobno liczby analiz i kluczy słów w BROAD/STANDARD, status członkostwa i niewiadome w każdej warstwie. Znana odmowa nie usuwa niewiadomych; wspólne payloady nie zaniżają liczby analiz, a powtórzony check nie zawyża liczby dotkniętych analiz. Wynik słowa zachowuje dopuszczony homonim. Raport odmawia niepełnego zapisu lub niezgodnych hashy/statusów. To diagnostyka, INCOMPLETE i pełne reports pending; nie nadaje VERIFIED. [Przegląd i runtime](../../.maister/tasks/development/2026-10-04-generator-broad-standard/analysis/evidence/unresolved-report-review.md).

## Wpływ filtrów z zapisanych ocen

Nowe build zapisuje `reports/filter-impact.json`: samodzielne, kolejne i łączne odmowy, dla wszystkich utrwalonych analiz każdego wariantu. Kolejność ID reguł jest leksykograficzna i jawnie diagnostyczna, nie ustala pierwszeństwa reguł językowych. Odmowa analizy nie usuwa słowa z dodatnim lub nierozstrzygniętym homonimem. Unknown nie jest odmową. Przed raportem wymagane jest pełne pokrycie zapisanych ocen obu wariantów, zgodność statusów i hashy powodów; uszkodzenie odmawia raportu. Oznaczenie zakresu pozostaje `all_persisted_assessments_not_full_release`, bez promocji do VERIFIED.

## Udokumentowane użycia i pozostałość

Nowe build v15 czytają przypięte `semantic-uses` i rozliczają source_rows / source_compact_interpretations / source_tag_expansions oddzielnie od documented_use_analyses i remainder_analyses. Unknown/filter podają semantic_analysis_kinds. Dowód użycia nie przechodzi na pozostałość; odczyt odmawia zgubionej analizy lub fałszywego śladu także z przeliczonym hashem. Przy przypiętym quality powstaje reports/quality-analyses.json, z pełnym źródłem i warstwami obu wariantów. To diagnostyczne warstwy utrwalonych analiz, nie pełna macierz quality-v1; UNREVIEWED i INCOMPLETE pozostają. [Przegląd](../../.maister/tasks/development/2026-10-04-generator-broad-standard/analysis/evidence/semantic-use-implementation-review.md).

## Diagnostyczny indeks kanoniczny

Build zapisuje reports/canonical-index.json: hashe/rozmiary ustalonego zestawu raportów, przyszłych list oraz hashe źródeł/dowodów/konfiguracji. Czasy, ścieżki i fizyczna baza wyłączone; jej treść logiczna wiązana przez logical-content. Indeks ma INCOMPLETE i jawne missing, nie jest verify. [Kontrola](../../.maister/tasks/development/2026-10-04-generator-broad-standard/analysis/evidence/canonical-index-implementation-review.md).

## Raport pokrycia klas

Build zapisuje reports/coverage.json: kompaktowe interpretacje i rozwinięcia według POS, obserwowane/nieobserwowane klasy konstruktorów, zapisane analizy oraz brakujące oceny źródła. Udokumentowane użycie nie powiększa liczby źródłowych form. COMPLETE_TECHNICAL_NOT_QUALIFICATION opisuje tylko pokrycie zapisanych ocen; INCOMPLETE i pełna macierz semantyczna nadal otwarte. Starszy import bez ocen pozostaje readonly i ma wszystkie rozwinięcia nieocenione; częściowy schemat odmawia raportu. [Kontrole](../../.maister/tasks/development/2026-10-04-generator-broad-standard/analysis/evidence/coverage-implementation-review.md).

## Aktualizacja v20

unresolved_report dodaje word_keys_by_membership (accept/reject/unresolved) każdej reguły: wynik całego słowa po wszystkich homonimach. To współwystępowanie, nie przyczynowa delta po usunięciu reguły. Historyczne bazy zachowują własne wcześniejsze oceny.

## Raporty POP00

`reports/decisions.json` rozlicza każdy napis POP0: wynik, dowód KWJP i wszystkie
interpretacje wybranych leksemów, w tym konstrukcje. Identyfikatory źródłowe są niezależne
od technicznych ID SQLite. Przy kilku analizach jedna zachowana wystarcza do zachowania napisu.
`reports/summary.json` pokazuje formy, straty, zachowane leksemy, długości i nakładające się grupy.
Pokrycie ma dwa jawne mianowniki: opublikowane małoliterowe tokeny KWJP orth/all należące do POP0
oraz wszystkie opublikowane małoliterowe tokeny tej listy. Nie jest miarą znajomości ani grywalności.
Nieobecność w KWJP ma NO_PUBLISHED_EVIDENCE, bez imputacji zera. Brak analizy albo utrata
całego leksemu jest błędem budowy. Szczegóły polityki: [ADR-009](../adr/ADR-009-pop00-v1.md).

## Raporty TEMATY

Metoda `tematy-v1`, [ADR-010](../adr/ADR-010-tematy-v1.md). Pliki pakietu:
- `MORZE.txt.gz`: formy tematu ∩ STANDARD, posortowane, gzip bez nazwy i czasu.
- `MORZE.tsv.gz`: wiersz na leksem; kolumny `klucz`, `lemat`, `czesci_mowy`, `warstwa`, `zrodla`,
  `znaczenie`, `wieloznaczny`, `formy` (liczba form). Warstwa to najniższa z T1 < T2 < T3, źródła to wszystkie.
- `tematy/morze.json`, `method.json`: kopia tematu i metody.
- `reports/summary.json` i `reports/raport.md` (te same liczby, tekst dla człowieka).
- `reports/sample.json`, `reports/review-template.json`: próba R2 ([jakosc.md](jakosc.md#próbki-tematy-tematy-quality-v1)).
- `ATTRIBUTIONS.md` (plik pakietu POP plus Słowosieć i IATE), `LIMITATIONS.md`, `TERMS.md`.
- `release-manifest.json` (`literaki-tematy-manifest`, `status: BUILT`, `counts.morze`, `overlap`, `files`) i `SHA256SUMS`.

Pola `summary.json`:
- `liczby`: kandydaci, wpisy, formy, `warstwy` T1/T2/T3.
- `przeciecia`: `leksemy` i `formy`, dla T1, T2, T3 i `razem`: `temat`, `pop` i `pop00` (`liczba`, `procent`
  względem tematu). Leksem w POP00 = członek POP0; forma = napis z `POP.txt.gz` albo `POP00.txt.gz`.
- `diagnostyka`: przed ∩ STANDARD; kandydaci, ∩ BROAD, ∩ STANDARD i udziały, na warstwę, w leksemach i formach.
- `odrzucone`: `BRAK_LEKSEMU` (z podliczbą `ger`), `NIE_JEDNO_SLOWO`, `POZA_BROAD`, `POZA_STANDARD`;
  liczba i do 10 przykładów na powód i warstwę.
- `t1`, `t2`, `t3`: atomy SGJP; synsety, sztuczne, jednostki, lematy; liczby haseł IATE według typu i powody odrzuceń.
- `wieloznaczny`: `tak`/`nie`/`brak_danych`, liczba, procent, 10 przykładów.
- `slowa_oczywiste`: test 37 słów; do progu idzie `razem`, `T1` i `T1_T2` są diagnostyką.
- `srodladowe`: żegluga śródlądowa w T3 (`kandydaci_t3` główna miara, `wpisy_t3` dodatkowo).
- `werdykt`: `automatyczny` (`dalej` albo `popraw`), `niespelnione`, `czeka_na_ocene`. „stop” wybiera tylko operator.

Procenty liczymy z dokładnych ułamków (jedno miejsce); pusty mianownik daje `null`.
