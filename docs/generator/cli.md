# CLI generatora — bieżący stan

## TL;DR
Działają inspect-sources, build importu, diagnostyczne explain, verify/export (G7) oraz `pop` (listy POP/POP0, metoda `pop-v3`, ADR-008). Pełny generator nadal jest w implementacji.
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

Dwa przebiegi do `verify` uruchamia równolegle `scripts/build_pair.sh PREFIKS`.

Verify i export opisuje [publikacja.md](publikacja.md#verify-i-export--wdrożenie-g7).

Wyjątki dawności STANDARD (#4): edycja JSON-a, pin, build i kontrola — [wyjatki-dawnosci-standard.md](wyjatki-dawnosci-standard.md).

## POP i POP0 (`pop`)

Metoda bieżąca: `pop-v3` ([ADR-008](../adr/ADR-008-pop-v3-staly-prog.md)), `config/generator/pop.json`.
POP = jednostki z punktacją ≥ −1,042878629 (remis wchodzi, brak punktacji nie). Liczba leksemów jest wynikiem, nie limitem.
POP0 = jednostki z punktacją ≥ 0,57370099 (ta sama reguła). Oba progi są **tymczasowe**: to cięcia wydanego pop-v2
(60 000 i 20 000 leksemów), nie zmierzone granice popularności. Docelowe progi: [#6](https://github.com/robmar-net/literaki-slownik/issues/6).
Pozostałe decyzje: [ADR-007](../adr/ADR-007-metoda-pop-v1.md) rew. 4. NKJP jako CC BY: [ADR-006](../adr/ADR-006-nkjp-cc-by-bez-wersji.md).

```sh
python3 -m literaki_slownik pop --manifest config/generator/pop-sources.json \
  --config config/generator/pop.json --output-dir data/work/pop-nowy [--run-dir <przebieg>] [--release-dir <pakiet LL-PL>] [--json]
```

Odtworzenie wydanego `pop-v2` (limit 60 000 leksemów POP, metoda historyczna):

```sh
python3 -m literaki_slownik pop --manifest config/generator/pop-sources-v29.json \
  --config config/generator/pop-v2.json --output-dir data/work/pop-v2-odtworzenie
```

`pop-v2.json` to bajtowa kopia konfiguracji wydanego pakietu. `pop-sources-v29.json` przypina STANDARD v29.
`--config` jest wymagany. Walidacja przyjmuje tylko parę progów danej wersji: `pop-v2` liczba/liczba, `pop-v3` punktacja/liczba.

- `--run-dir` i `--release-dir` domyślnie z manifestu. Przebieg musi być FROZEN, hashe zgodne z pinami.
- `--output-dir` musi nie istnieć; katalog nadrzędny musi istnieć. `pop` nigdy nie nadpisuje.
- `--output-dir` w przebiegu albo w pakiecie LL-PL: kod 2, zanim cokolwiek się liczy.
- Kody: 0 pakiet zbudowany; 2 argumenty, manifest lub `pop.json` spoza ADR-007/ADR-008; 3 pin lub brak wejścia; 4 błąd danych (też SQLite, brak klucza, zły kształt, wiersz NKJP z CRLF), istniejący cel, naruszone `POP0 ⊆ POP ⊆ STANDARD` (sprawdzane jawnie; `pop.json` z progiem POP0 < próg POP = kod 2), słowo z `must_include_pop0` poza POP0 albo częsta forma poza listą (straż `frequent_guard`); 5 przebieg nie FROZEN albo baza zmieniła się w trakcie.

Pakiet (status `BUILT`, pliki 0444):

| plik | treść |
|---|---|
| `POP.txt.gz`, `POP0.txt.gz` | listy form, gzip bez nazwy, `mtime=0` |
| `reports/units.json` | jednostki: ranga i percentyl, bez wartości NKJP |
| `reports/thresholds.json` | progi: `by` (`score` albo `count`), `score` z `provisional` (link #6) albo `limit`, ostatnia ranga, leksemy, formy, przycięcia, straż częstych form |
| `reports/sample.json`, `reports/review-template.json` | próbka `pop-quality-v1` i pusty szablon przeglądu |
| `ATTRIBUTIONS.md`, `LIMITATIONS.md`, `TERMS.md` | atrybucje, ograniczenia, warunki |
| `release-manifest.json`, `SHA256SUMS` | tożsamość wejść i kodu, hashe plików |

Wyjaśnienie słowa w pakiecie:

```sh
python3 -m literaki_slownik explain --run-dir <przebieg> --word kot --variant pop --pop-dir <pakiet> [--json]
```

`--variant pop|pop0` wymaga `--pop-dir` (inaczej kod 2). Powody: `IN_POP0`, `IN_POP`, `BELOW_THRESHOLD` (poniżej progu), `NOT_IN_STANDARD` (spoza STANDARD), `PROPER_NAME_ONLY` (tylko nazwa własna), `PRUNED_WEAK_MEMBER` (jednostka na liście, własny leksem poniżej progu; w `pop-v3` — własna punktacja, `member_meets_score` per lista), `NO_DATA` (brak danych o użyciu).
`pop` pokazuje próg punktacji i jego tymczasowość, `pop0` — limit i rangę.

Kontrola niezależna od kodu budowy (tylko biblioteka standardowa):

```sh
python3 scripts/check_pop_package.py --pop-dir <pakiet> --standard <przebieg>/lists/standard.txt [--review pop-v1-review.json]
```

Sprawdza `SHA256SUMS`, manifest, `POP0 ⊆ POP ⊆ STANDARD`, brak surowego NKJP; z `--review` także przegląd. Kody: 0 zgodne, 2 argumenty, 3 `--standard` ≠ pin, 4 naruszenia (lista na stderr).

Pomiar przed decyzją o progach (tylko odczyt): `python3 scripts/measure_pop.py --output-dir data/work/pop-measure-<stempel> [--sources] [--run-dir] [--release-dir] [--with-membership-ii]`. Wynik: `measure.json`, `timing.json`, `report.md`. Kody: 2 argumenty, 3 piny, 4 katalog istnieje, 5 baza zmieniona lub przebieg nie FROZEN.

Build odmawia istniejącego katalogu. Aktualnie wykonuje preflight i importy; pozostawia INCOMPLETE oraz jawnie pending dla dalszych etapów. Użyj nowego katalogu przy ponowieniu. Nie modyfikuj historycznego audytu.

Explain nie skraca odpowiedzi JSON: pokazuje wszystkie oryginały, pełne ID homonimów, surowe tagi i ich rozwinięcia, nazwy/kwalifikatory, źródła i pierwszy wiersz interpretacji. Duplikaty pozostają w raw tabeli; pierwszy wiersz nie jest listą wszystkich powtórzeń. Tekst zawiera powody ocen na osobnych poziomach. NFC/lower służy wyszukiwaniu; PCV nie staje się dopuszczalne przez zapytanie pcv.

## POP00 (`pop00`)

Metoda `pop00-v1`: [ADR-009](../adr/ADR-009-pop00-v1.md). Dziedziczy leksemy POP0 pop-v3,
chroni zwykłą odmianę i wymaga 0,1 IPM dla wybranych grup. Nijaka pierwsza/druga osoba odpada
jako analiza; inny zachowany homonim może zachować napis. Nie zmienia słownika stołu.

```sh
python3 -m literaki_slownik pop00 --manifest config/generator/pop00-sources.json \
  --config config/generator/pop00.json --output-dir data/work/pop00-nowy --json
python3 -m literaki_slownik explain --run-dir <zamrożony-przebieg> \
  --word zrobiłem --variant pop00 --pop00-dir data/work/pop00-nowy --json
python3 scripts/check_pop00_package.py --pop00-dir data/work/pop00-nowy \
  --manifest config/generator/pop00-sources.json --config config/generator/pop00.json \
  [--review <przegląd.json>]
```

Manifest przypina pakiet POP0, manifest FROZEN, bazę, STANDARD i dokładny KWJP orth/all.
Hashe wejść są sprawdzane przed i po budowie. Cel musi być nowym katalogiem poza wejściami.
Kod 2: argumenty/metoda/cel w wejściach; 3: brak lub niezgodny pin; 4: dane, nieznany tag,
niepełne pokrycie, utrata leksemu albo istniejący cel; 5: przebieg nie FROZEN lub zmiana wejść.

Pakiet BUILT: `POP00.txt.gz`, `method.json`, `reports/decisions.json`, `summary.json`,
`sample.json`, `review-template.json`, manifest, sumy oraz atrybucje, warunki i ograniczenia.
Wszystkie raporty wymienione po `decisions.json` są również w `reports/`.
Pliki są tylko do odczytu; gzip nie ma nazwy ani czasu. BUILT nie oznacza automatycznego odbioru.

Diagnostyka pokazuje IN_POP00, FORM_FILTERED albo NOT_IN_POP0, źródłowy tag, leksem,
identyfikator analizy, grupę filtra i dowód użycia. NO_PUBLISHED_EVIDENCE nie jest częstością zero.
Kontroler jest niezależny od buildera; odtwarza decyzje z bazy, a nie tylko sprawdza sumy.
Przegląd musi obejmować całą próbkę, odpowiadać sumom pakietu i nie mieć nierozstrzygniętych pozycji.

## TEMATY (`tematy`)

Metoda `tematy-v2`: [ADR-012](../adr/ADR-012-tematy-fala-1.md) (warstwy z [ADR-010](../adr/ADR-010-tematy-v1.md)),
źródła: [ADR-011](../adr/ADR-011-zrodla-slowosiec-iate.md). Pilotaż #11 (`morze`), fala 1 #12 (9 tematów).
Lista to leksemy SGJP ∩ STANDARD w rozłącznych warstwach: T1 etykiety SGJP, T2 Słowosieć 4.5,
T3 IATE 2019 (opcjonalne), D ręczne dodatki z pliku tematu. Nie zmienia słownika stołu.
Temat to plik `config/generator/tematy/<id>.json`; `<id>` to jego `id` (np. `morze`), `<ID>` to `id` wielkimi
literami (`MORZE`).

Źródła pobieramy osobno, z siecią. Budowa sieci nie używa.

```sh
python3 scripts/fetch_tematy_sources.py iate        # → cache/iate/IATE_download.zip (tylko tematy z t3)
python3 scripts/fetch_tematy_sources.py plwordnet   # → cache/plwordnet/wordnet_work_4_5.zip
python3 -I scripts/build_plwordnet_db.py --zip cache/plwordnet/wordnet_work_4_5.zip \
  --output cache/plwordnet/plwn45-tematy.sqlite
python3 -m literaki_slownik tematy --manifest config/generator/tematy-sources.json \
  --config config/generator/tematy.json --topic config/generator/tematy/<id>.json \
  --output-dir data/work/tematy-<wersja tematu>-YYYYMMDD-a [--json]
python3 scripts/check_tematy_package.py --package-dir data/work/tematy-<wersja tematu>-YYYYMMDD-a \
  --manifest config/generator/tematy-sources.json --config config/generator/tematy.json \
  [--review review.json]                            # niezależny checker
python3 scripts/tematy_review.py strona --package-dir data/work/tematy-<wersja tematu>-YYYYMMDD-a \
  --review review.json --output r2.html             # strona przeglądu R2
python3 scripts/tematy_review.py zapisz --package-dir data/work/tematy-<wersja tematu>-YYYYMMDD-a \
  --review review.json --oceny operator.json|- [--reviewer operator]   # oceny operatora
```

- `fetch_tematy_sources.py`: `curl -fL` do pliku tymczasowego, potem przeniesienie bez nadpisania.
  Wypisuje rekord JSON (`url`, `retrieved_at`, `sha256`, `bytes`, `path`; dla IATE też
  `last_modified` i `member`). Zip Słowosieci musi mieć przypięty hash. Kod 1: błąd pobrania lub hasha.
- `build_plwordnet_db.py`: pochodna SQLite ze zrzutu w zipie. Tylko tabele i kolumny z listy
  dozwolonych, bez danych redaktorów; relacje `valid=1`; tabela `meta` wiąże ją z zipem.
  Dwa uruchomienia dają ten sam plik. Kod 1: cel istnieje, błąd zrzutu albo nazw relacji.
- `tematy`: `--manifest` przypina wejścia (`tematy-sources.json`), `--config` metodę
  (`tematy.json`), `--topic` temat (`tematy/<id>.json`), `--output-dir` nowy katalog poza wejściami.
  Nazwa pakietu: `data/work/tematy-<wersja tematu>-YYYYMMDD-{a,b}`, np. `tematy-grzyby-v1-20261029-a`.
  Temat bez `t3` nie czyta IATE; IATE nie trafia wtedy do tekstów ani do `inputs` manifestu.
  Każdy czytany plik trafia do rejestru z hashem; przed przeniesieniem budowa hashuje go ponownie.
  Kody: 0 pakiet BUILT; 2 konfiguracja, nieznane pole albo cel w wejściach; 3 brak lub niezgodny pin
  (także manifest wydania, POP, POP00, `meta` pochodnej); 4 dane albo istniejący cel;
  5 przebieg nie FROZEN albo zmiana wejścia w trakcie budowy.
- `check_tematy_package.py`: nie importuje `literaki_slownik`. Sprawdza sumy, manifest,
  `<ID>.txt` ⊆ STANDARD, TSV wobec TXT, rozłączne warstwy, warstwę D wobec dodatków tematu,
  brak wykluczonych par w TSV, przecięcia z POP i POP00. Zna tylko `tematy-v2`; starsze pakiety
  sprawdza checker z commitu `a633136`.
  Z `--review` liczy trafność, zgodność, kappę, test słów oczywistych i werdykt ([jakosc.md](jakosc.md#próbki-tematy-tematy-quality-v1)).
- `tematy_review.py`: `strona` robi stronę HTML z pozycjami operatora (bez ocen agenta; odmawia bez
  hasha ocen agenta); `zapisz` łączy JSON operatora z plikiem przeglądu i sprawdza klucze i hashe.

Pakiet BUILT (13 plików, tylko do odczytu): `<ID>.txt.gz`, `<ID>.tsv.gz`, `tematy/<id>.json`,
`method.json`, `reports/{summary.json,raport.md,sample.json,review-template.json}`,
`ATTRIBUTIONS.md`, `LIMITATIONS.md`, `TERMS.md`, `release-manifest.json`, `SHA256SUMS`.
Opis plików: [raporty.md](raporty.md#raporty-tematy). `explain` nie ma wariantu tematy.

## Indeks morfologii SGJP (`morph-index`)

Dla serwera Literaki (#1862): forma BROAD → analizy z eksportu SGJP (lemat, tag, kwalifikatory). Uruchamiany ręcznie; wynik trafia do `lexicons/sgjpindex/` w repo serwera.

```sh
python3 -m literaki_slownik morph-index --broad <LL-PL-BROAD.txt.gz> --sgjp cache/sgjp/sgjp-20260823.tab.gz \
  --broad-lexicon-id pl-broad-20261011 --broad-dawg-sha256 <hex z lexicons/pl-broad-20261011.sha256> --out <plik>.bin [--json]
```

- Wypisuje: formy z analizą, liczby reguł, list i końcówek, bajty, bajty po `gzip -9`, SHA-256.
- Format v1 (little-endian): `LLMI`, `u32` wersja 1, sześć pól nagłówka (id leksykonu, SHA-256 `.dawg`, SHA-256 listy BROAD po rozpakowaniu, nazwa eksportu SGJP, jego SHA-256, `literaki-slownik <commit>`), sześć długości sekcji `u32` i sekcje: końcówki lematów, tagi, kwalifikatory, reguły po 9 B, listy reguł, formy w blokach po 32.
- Lista reguł formy zachowuje kolejność wierszy eksportu. Listy są numerowane od najczęstszej; remis rozstrzyga pierwsze wystąpienie.
- Formy spoza SGJP nie mają wpisu. Wynik jest deterministyczny.
- Przebudowa w serwerze jednym poleceniem: `scripts/rebuild-sgjp-index <katalog literaki-slownik> --broad <LL-PL-BROAD.txt.gz> --sgjp <sgjp-….tab.gz>` (#1862). Robi dwa przebiegi, porównuje je i podmienia plik w `lexicons/sgjpindex/`.
- Kody: 2 zły argument (np. `--broad-dawg-sha256` to nie 64 małe znaki hex); 4 błąd danych albo istniejący `--out`.

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
