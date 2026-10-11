# CLI generatora — bieżący stan

## TL;DR
Działają inspect-sources, build importu, diagnostyczne explain, verify/export (G7) oraz `pop` (listy POP/POP0, ADR-007). Pełny generator nadal jest w implementacji.
Explain czyta bazę bez zmian i pokazuje wszystkie źródłowe interpretacje.
Nieaktywna polityka językowa daje unresolved; diagnostyka nie nadaje końcowego członkostwa w liście.

## Key Decisions
- Python 3.11+ i biblioteka standardowa; uruchomienie z katalogu repo.
- Źródła podajemy lokalnie przez jawny manifest. CLI niczego nie pobiera.
- Oryginał, język, reguły gry, profil i końcowa lista są rozdzielone. Korpus nie dopuszcza słowa do gry.

## Open Questions / Risks
- Verify przyjmuje tylko przebieg ze wszystkimi etapami complete. Pierwsze wydanie: LL-PL v29 (VERIFIED, export FROZEN, 2026-10-11).
- Bieżące explain ocenia źródłowe interpretacje oraz odtwarza kandydatów dwóch potwierdzonych klas. Brak w imporcie SGJP nie jest oceną wszystkich możliwych konstrukcji.
- Brak powiązań w starszej bazie nie oznacza braku korpusowego ani F=0.

## Komendy dostępne

```sh
python3 -m literaki_slownik --help
python3 -m literaki_slownik inspect-sources --manifest config/generator/sources.json --json
python3 -m literaki_slownik build --manifest config/generator/sources.json --run-dir data/work/import-new --json
python3 -m literaki_slownik explain --run-dir data/work/import-new --word PCV
python3 -m literaki_slownik explain --run-dir data/work/import-new --word DNA --variant broad --json
python3 -m literaki_slownik verify --run-dir data/work/run-a --peer-run data/work/run-b --review sciezka/quality-review.json --json
python3 -m literaki_slownik export --run-dir data/work/run-a --output-dir data/work/pakiet-nowy --json
```

Verify i export opisuje [publikacja.md](publikacja.md#verify-i-export--wdrożenie-g7).

## POP i POP0 (`pop`)

Metoda `pop-v2`: [ADR-007](../adr/ADR-007-metoda-pop-v1.md) rew. 4. NKJP jako CC BY: [ADR-006](../adr/ADR-006-nkjp-cc-by-bez-wersji.md).

```sh
python3 -m literaki_slownik pop --manifest config/generator/pop-sources.json \
  --config config/generator/pop.json --output-dir data/work/pop-nowy [--run-dir <v29>] [--release-dir <LL-PL v29>] [--json]
```

- `--run-dir` i `--release-dir` domyślnie z manifestu. Przebieg musi być FROZEN, hashe zgodne z pinami.
- `--output-dir` musi nie istnieć; katalog nadrzędny musi istnieć. `pop` nigdy nie nadpisuje.
- `--output-dir` w przebiegu albo w pakiecie LL-PL: kod 2, zanim cokolwiek się liczy.
- Kody: 0 pakiet zbudowany; 2 argumenty, manifest lub `pop.json` spoza ADR-007; 3 pin lub brak wejścia; 4 błąd danych (też SQLite, brak klucza, zły kształt, wiersz NKJP z CRLF), istniejący cel, naruszone `POP0 ⊆ POP ⊆ STANDARD`, słowo z `must_include_pop0` poza POP0 albo częsta forma poza listą (straż `frequent_guard`); 5 przebieg nie FROZEN albo baza zmieniła się w trakcie.

Pakiet (status `BUILT`, pliki 0444):

| plik | treść |
|---|---|
| `POP.txt.gz`, `POP0.txt.gz` | listy form, gzip bez nazwy, `mtime=0` |
| `reports/units.json` | jednostki: ranga i percentyl, bez wartości NKJP |
| `reports/thresholds.json` | progi: leksemy, formy, przycięcia, straż częstych form |
| `reports/sample.json`, `reports/review-template.json` | próbka `pop-quality-v1` i pusty szablon przeglądu |
| `ATTRIBUTIONS.md`, `LIMITATIONS.md`, `TERMS.md` | atrybucje, ograniczenia, warunki |
| `release-manifest.json`, `SHA256SUMS` | tożsamość wejść i kodu, hashe plików |

Wyjaśnienie słowa w pakiecie:

```sh
python3 -m literaki_slownik explain --run-dir <v29> --word kot --variant pop --pop-dir <pakiet> [--json]
```

`--variant pop|pop0` wymaga `--pop-dir` (inaczej kod 2). Powody: `IN_POP0`, `IN_POP`, `BELOW_THRESHOLD` (poniżej progu), `NOT_IN_STANDARD` (spoza STANDARD), `PROPER_NAME_ONLY` (tylko nazwa własna), `PRUNED_WEAK_MEMBER` (jednostka na liście, własny leksem poniżej progu), `NO_DATA` (brak danych o użyciu).

Kontrola niezależna od kodu budowy (tylko biblioteka standardowa):

```sh
python3 scripts/check_pop_package.py --pop-dir <pakiet> --standard <v29>/lists/standard.txt [--review pop-v1-review.json]
```

Sprawdza `SHA256SUMS`, manifest, `POP0 ⊆ POP ⊆ STANDARD`, brak surowego NKJP; z `--review` także przegląd. Kody: 0 zgodne, 2 argumenty, 3 `--standard` ≠ pin, 4 naruszenia (lista na stderr).

Pomiar przed decyzją o progach (tylko odczyt): `python3 scripts/measure_pop.py --output-dir data/work/pop-measure-<stempel> [--sources] [--run-dir] [--release-dir] [--with-membership-ii]`. Wynik: `measure.json`, `timing.json`, `report.md`. Kody: 2 argumenty, 3 piny, 4 katalog istnieje, 5 baza zmieniona lub przebieg nie FROZEN.

Build odmawia istniejącego katalogu. Aktualnie wykonuje preflight i importy; pozostawia INCOMPLETE oraz jawnie pending dla dalszych etapów. Użyj nowego katalogu przy ponowieniu. Nie modyfikuj historycznego audytu.

Explain nie skraca odpowiedzi JSON: pokazuje wszystkie oryginały, pełne ID homonimów, surowe tagi i ich rozwinięcia, nazwy/kwalifikatory, źródła i pierwszy wiersz interpretacji. Duplikaty pozostają w raw tabeli; pierwszy wiersz nie jest listą wszystkich powtórzeń. Tekst zawiera powody ocen na osobnych poziomach. NFC/lower służy wyszukiwaniu; PCV nie staje się dopuszczalne przez zapytanie pcv.

## Jak czytać wynik

- source_presence=present: znaleziono wpis w bazie, także przy growym odrzuceniu.
- source_presence=absent: brak w kompletnym imporcie SGJP; pełne konstrukcje pozostają nieocenione.
- not_observed_in_incomplete_import: brak w odczytanej części; awaria/running/pending importu nie dowodzi braku w źródle.
- assessment.language: polityka językowa jeszcze nieaktywna, unresolved.
- assessment.game: potwierdzony zakaz wielkich liter oceniany osobno; inne warunki pozostają unresolved.
- assessment.profile: kanoniczny PL v1, 32 litery i 2–15 znaków; źródłowy zapis pozostaje zachowany, nie usuwamy znaków.
- source_aggregation: wynik tylko znalezionych źródłowych analiz; nie przenosi warunków między homonimami.
- list_membership: w obecnej diagnostyce zawsze unresolved. Nie jest listą wydania ani obietnicą końcowej kwalifikacji.

Jeżeli baza ma relacje evidence_link/evidence_candidate, explain pokazuje powiązane obserwacje i wszystkich kandydatów. F i inne miary pozostają przy jednostce/opublikowanej liście, raz na rekord. Powiązanie lemma czytać nie dowodzi częstości pełnej formy czytałem. sense_identity_confirmed pozostaje false. W starszej bazie bez relacji links_available=false; nie uruchamiamy budowania powiązań podczas odczytu.

## Kody i kontrola

JSON: jeden obiekt UTF-8 na stdout, błędy na stderr. Kod 0 oznacza poprawną diagnostykę także dla reject/unresolved/absent. Kod 2: błędne argumenty/schemat, 3: niedopuszczone wejście/hash, 4: błąd operacyjny/odczytu, 130: przerwanie. Kod 5: verify odmówił VERIFIED (JSON `status: refused`, wynik per K) albo export odmówił. Publiczne CLI nie ma obejścia ani trybu fikstury.

```sh
python3 -m unittest discover -s tests -p 'test_*.py'
python3 -m unittest discover -s scripts -p 'test_audit_sgjp.py'
```

[Rzeczywista próba explain](../../.maister/tasks/development/2026-10-04-generator-broad-standard/analysis/evidence/diagnostic-explain-runtime.json) obejmuje osiem zapytań do pełnej bazy z technicznymi powiązaniami KWJP. Hashe bazy i manifestu przed/po odczycie są identyczne. To sprawdzenie mechaniki, bez odbioru G8/K7.

## Potwierdzone warunki w diagnostyce

Explain w wersji `diagnostic-approved-conditions-v2` pokazuje zatwierdzone A dla `niezal.`: samo niezalecanie nie odrzuca w obu wariantach. Obok tej pozytywnej oceny pojedynczego warunku nadal pokazuje nierozstrzygnięcie pełnej polityki. Nie jest to werdykt dopuszczalności całego słowa. Odczyt istniejącego importu pokazuje warunki bieżącej wersji kodu, nie ukończony historyczny build decyzji.

Explain w wersji `diagnostic-approved-conditions-v3` pokazuje również zatwierdzone warunki wieku: dodatkowa dawność/archaiczność może dać językowe reject w STANDARD mimo niewiadomych innych warunków. BROAD pozostawia samą dawność niewykluczającą. List_membership pozostaje unresolved, ponieważ nie zbudowano wszystkich konstrukcji i pełnych decyzji.

Wersja `diagnostic-approved-conditions-v4` dodaje jawny niewykluczający warunek zakresu użycia dla 15 sprawdzonych etykiet potoczności/regionalności/gwarowości/wulgarności/rzadkości. Nieznane mieszanki pozostają do oceny; całe członkostwo nadal unresolved. W kolejnej wersji v5 niepopr. wdrożono zgodnie z zatwierdzonym A.

Wersja `diagnostic-approved-conditions-v5` pokazuje reject językowy dla 27 etykiet jawnej niepoprawności w obu wariantach. Source_presence pozostaje present, a pozostałe analizy zachowane. List_membership nadal unresolved ze względu na brak pełnych konstrukcji i decyzji.

## Diagnostyczni kandydaci konstrukcji

Wersja `diagnostic-approved-conditions-v6` dodaje 357 etykiet opisowych. `derivations` pokazuje także znane klasy rozkaźnik + jedna partykuła i by + nwok aglt, z pełnymi składnikami oraz przyczynami ocen. Odczyt nie zapisuje kandydatów do bazy, nie nadaje pełnego dopuszczenia i nie uruchamia kompletnego build. JSON nie ucina wyników. Tekst pokazuje wiersze źródeł i odziedziczone ograniczenia; source_presence nadal oznacza obecność bezpośredniego wpisu. Powiązań KWJP kandydatów nie zbudowano, nie przypisujemy im F z segmentów.

Wersja `diagnostic-approved-conditions-v7` dodaje zatwierdzony warunek kontekstu dla 11 etykiet. JSON zachowuje `source_label` i `required_context`; tekst pokazuje wymaganie. Status accept dotyczy tylko tego warunku. Pełna ocena językowa i list_membership mogą pozostać unresolved, a znana odmowa nadal ma pierwszeństwo.

Nowe `build` zapisują także `reports/qualifier-conditions.json`: znane warunki i nierozpoznane etykiety. Raport pozostaje częściowy; nie zmienia gotowości INCOMPLETE ani statusu reports pending. Szczegóły w [raportach](raporty.md).

Nowe `build` utrwalają również potwierdzone dwa rodzaje kandydatów konstrukcji i zapisują `reports/construction-candidates.json`. `explain` pokazuje `persisted_candidate_key` oraz zapisany ślad w tekście; dla wcześniejszych baz jest null. Pełny etap constructions pozostaje pending; nie oznacza to kompletnej kwalifikacji lub wydania.

## Utrwalone oceny diagnostyczne (schema2)

Nowy build zapisuje każde rozwinięcie tagu i każdą konstrukcję do analysis, po dwie variant_decision, i pełne współdzielone powody decision_payload identyfikowane SHA256. reports/decisions.json rozlicza pokrycie. Explain JSON udostępnia persisted_analyses z wersją zapisu, kompletną oceną i indywidualnym profilem. Bieżące analyses/derivations pozostają diagnostyką aktualnego kodu, więc wersje należy czytać osobno. Stara baza bez tabel ocen daje pustą persisted_analyses, bez zapisu lub migracji. Zmieniona wersja/treść wymaga nowego build; uszkodzony hash powodów jest błędem odczytu. decisions nadal pending, list_membership unresolved, INCOMPLETE; pełne verify/export niegotowe.

## Diagnostyka policyv13

Nowa wersja pokazuje udokumentowany podzbiór obowiązkowej wielkiej litery według normy2026, osobno od historycznej oceny językowej, oraz źródłowy konstruktor impt_sg+że+ż z growym reject. Explain dla krakowiak zachowuje oba pełne ID; idźżeż pokazuje źródłowy rozkaźnik i dwie oddzielne partykuły. Bieżąca ocena policyv13 i wcześniejszy zapis ocen mają własne wersje, bez nadpisywania starych build. List_membership i pełna gotowość nadal nieukończone.

## Udokumentowane użycia — diagnostyka v15

Build opcjonalnie odczytuje konfigurację semantic-uses przypiętą path/sha256 w configurations manifestu wejść. Jej schema_version1 zawiera reviews: dokładny source, stabilny use_id, własny opis, evidence oraz coverage documented_use_only. documented_conditions wiąże istniejące warunki dokumentacyjne z tym użyciem i wymaga właściwego hasha dowodu. Brak przypięcia lub inna tożsamość odmawia zapisu, a zmiana przeglądu wymaga nowego katalogu. Domyślny manifest ma2 wcześniej zatwierdzone użycia de:F/ibn; czytnik internetowy nie stał się wejściem.

Explain tekst/JSON pokazuje semantic_analyses z pełnymi śladami i niewiadomą pozostałością. Source_aggregation ma jawny basis; nie jest akceptacją do listy. Starsze zapisane oceny pozostają czytelne bez migracji. [Wdrożenie i granice](../../.maister/tasks/development/2026-10-04-generator-broad-standard/analysis/evidence/semantic-use-implementation-review.md).

## Dodatni dowód konkretnego użycia

W v16 lexical_proof w przypiętym własnym przeglądzie dotyczy wyłącznie zatwierdzonego użycia wznak/frag. Explain pokazuje accept tego warunku BROAD i unknown STANDARD; inne warunki oraz nierozpoznana pozostałość zachowane. Nie jest to końcowe dopuszczenie do listy. Zmiana konfiguracji wymaga nowego build.
