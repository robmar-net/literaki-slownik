# Specyfikacja: słowniki POP i POP0 (#3)

Rewizja 2 (2026-10-11), po audycie `verification/spec-audit.md` (M1–M6, m1–m14).

## TL;DR
- POP i POP0 to dwie stałe listy popularnych słów. Obie są podzbiorami STANDARD z LL-PL v29: POP0 ⊆ POP ⊆ STANDARD.
- Źródła: tylko KWJP (z zamrożonej bazy v29) i NKJP `1grams.gz`. Krok jest pochodny i tylko do odczytu.
- Pięć etapów: A pomiar → B decyzje (ADR) → bramka „rewizja spec + plan C” → C polecenie `pop` → D odbiór → E wydanie `pop-v1` i wiki.
- Metoda i progi (D1–D8) czekają na raport A. Raport mierzy pełne listy opcji, w tym grupę homonimów (`rok`, `dzień`).
- Wydanie wymaga zatwierdzonego przeglądu próbek, sprawdzonego skryptem. Integracja z serwerem gry jest poza zakresem.

## Key Decisions
- Nowy moduł `literaki_slownik/pop.py` i podkomenda `pop`. LL-PL (`sources.json`, `inputs.py`, `decisions.VARIANTS`) zostaje nietknięty.
- Własny manifest `config/generator/pop-sources.json` z pinami v29 (baza 85b23ca5…, release-manifest 54705743…, STANDARD a432c7c5…, NKJP 73af4909…) i ścieżką pakietu LL-PL v29.
- Metoda w `config/generator/pop.json` ze ścisłym walidatorem: opcje D1–D8 z zamkniętej listy, liczby z typem i zakresem.
- Wszystkie decyzje D1–D8 w jednym ADR-007, odwracalnym.
- Klucz leksemu = `(source_id, lemma_id)`. `lexeme.id` to liczba z importu i nie jest stabilna.
- Jednoznaczność formy NKJP liczona wobec wszystkich leksemów SGJP (oba źródła, nazwy własne, analizy odrzucone), nie tylko STANDARD.
- Próbki: `quality._config` przyjmuje drugą zamkniętą konfigurację `pop-quality-v1`. Bez własnego samplera.
- Hash bazy (14 s) liczony w każdym `pop`, przed i po. Wynik trafia do manifestu pakietu.
- Pakiet ma status `BUILT`. Wydanie wymaga osobnego pliku `pop-v1-review.json` ze statusem `REVIEWED`, związanego hashami z pakietem. Sprawdza to `scripts/check_pop_package.py`.
- `explain` dla POP to osobna ścieżka `explain_pop`. `pop` nie trafia do `VARIANTS`.
- Pakiet nie ma pliku NKJP ani liczb NKJP per forma lub leksem. NKJP tylko jako ranga lub percentyl (ADR-006).
- SJP.pl nie jest użyty w `pop-v1` ani jako miara. Wejścia to tylko KWJP i NKJP.

## Open Questions / Risks
- D1–D8 nierozstrzygnięte do raportu A. Ryzyko: progi źle dobrane → boty grają nieznanymi słowami albo zbyt ubogo.
- Cel „98–99% tekstu” jest nieosiągalny wobec wszystkich tokenów KWJP (sufit 93,5%). D1 musi wybrać mianownik.
- Grupa homonimów jako jednostka (D5) sprawia, że POP „zna” oba leksemy `rok`. F nie jest kopiowane, ale skład jest szerszy. Decyduje właściciel.
- POP jako słownik stołu z D2 = „formy typowe” stoi w napięciu ze spec v3 §2.2 (pełna odmiana). D2 dotyczy `pop-v1` dla botów. Opcję stołu rozstrzyga zadanie integracji z serwerem.
- Serwer gra na `pl-sjp-20260820`. Bot z POP ⊆ STANDARD przy stole SJP może zagrać słowo spoza SJP. Mówią o tym wiki i LIMITATIONS.
- KWJP dzieli formy przeszłe (`zrobił`+`em`). Na poziomie form to brak, nie zero.
- Reguła „analiza tego leksemu przyjęta w STANDARD” (D2) wymaga `analysis` (17,5 mln) i `variant_decision` (35 mln). Czas mierzy etap A.
- Nowy plik `.py` i zmiana `quality.py` zmieniają `code_identity` (tree_sha256). Dotyczy tylko przyszłej weryfikacji LL-PL.

## Cel
Dać botom i ewentualnej opcji stołu dwie odtwarzalne listy słów znanych z tekstów, wybrane miarą z korpusów i przyjęte przez właściciela.

## Historie użytkownika
- Jako właściciel chcę raportu z liczbami i przykładami, żeby wybrać metodę i progi na danych, nie na opisach.
- Jako twórca botów chcę listy POP i POP0 z hashami i manifestem, żeby bot znał tylko popularne słowa.
- Jako właściciel chcę zapytać o słowo i usłyszeć, czemu jest albo go nie ma w POP/POP0.
- Jako odwiedzający wiki chcę wiedzieć, czym są POP i POP0, ile mają słów i skąd je pobrać.

## Wymagania

### Etap A — pomiar (tylko odczyt)
| id | wymaganie |
|---|---|
| A1 | Skrypt `scripts/measure_pop.py` sprawdza piny z `pop-sources.json`, w tym hash bazy przed i po. Różnica = błąd. |
| A2 | Wynik w nowym katalogu `data/work/pop-measure-<stempel>/`. Nic nie trafia do zamrożonego przebiegu ani pakietu v29. Katalog istnieje → kod 4. |
| A3 | `measure.json` kanoniczny (`canonical.write_json`), bez czasów i ścieżek. Zawiera `code_identity` i hash `pop.json`/opcji. Dwa przebiegi dają te same bajty. |
| A4 | Raport po polsku `report.md` dla właściciela, kopia w `analysis/pop-measure-report.md` zadania. Tabele, przykłady, zalecenie przy każdej decyzji. |
| A5 | Raport pokazuje dla D1–D8 opcje z liczbami (tabela niżej). Każda opcja: liczba leksemów, liczba form STANDARD, pokrycie, przykłady. Dla D5: top 50 wierszy AMBIGUOUS wg F i ich los w każdej opcji. |
| A6 | Luka potoczna: różnica rang NKJP–KWJP; leksem potoczny = token `pot.` w dowolnej interpretacji leksemu (`interpretation.qualifiers`); udział i przykłady przy kandydatach D6. |
| A7 | Próbki graniczne: 30 na warstwę, `quality.sample_strata` z konfiguracją `pop-quality-v1` (C17). Agent wstępnie ocenia. Przykłady w tabelach raportu są oznaczone jako ilustracje, nie próba losowa. |
| A8 | Wydajność: KWJP ładowany zbiorczo per `source_id` / zakres `evidence_id`; bez `LEFT JOIN evidence_candidate`; bez dużych sortowań w SQLite. |
| A9 | Formy z konstrukcji: liczba form STANDARD tylko z `derivation_candidate` (305 107 kandydatów bez `interpretation_id`, np. `zróbże`, `nienajlepszy`); ile mapuje się na dokładnie jeden leksem składnika, ile na żaden lub kilka; czas obu reguł przynależności z D2. |
| A10 | Miary NKJP w raporcie tylko jako rangi i percentyle, także dla leksemu z jedną formą (C14). Liczby NKJP per forma tylko w `measure.json` w katalogu roboczym, nie w kopii raportu w zadaniu. |

Co pomiar pokazuje dla każdej decyzji:

| # | Decyzja | Opcje do zmierzenia |
|---|---|---|
| D1 | Mianownik pokrycia | wszystkie tokeny KWJP; masa EXACT; masa leksemów z formą w STANDARD |
| D2 | Formy listy | (a) klasy znaczników: pełna odmiana vs wykluczenie (wołacz, rozkaźnik, imiesłowy, os. 1/2 i inne), udział masy i liczba form na klasę; (b) formy konstrukcji leksemu: tak/nie; (c) przynależność formy: „forma ∈ STANDARD i jest formą leksemu” vs „analiza tego leksemu przyjęta w STANDARD” (§2.2) |
| D3 | Miara i wagi | miara KWJP: F, ARF, 1-DP, liczba gatunków z obecnością (fikcja, fakt, publicystyka), pewność dopasowania (EXACT / grupa AMBIGUOUS / tylko NKJP); sama KWJP; KWJP + NKJP jako rangi/percentyle, kilka wag; Spearman i nakładanie top-N; wrażliwość progu na wagi |
| D4 | Czyszczenie NKJP | pełny napis NFC; zdjęcie interpunkcji z brzegów; zdjęcie bez kropki; lista kolizji (`ul.`→`ul`, `ok.`→`ok`) |
| D5 | Homonimy | (a) brak F; (b) F z flagą niejednoznaczności; (c) tylko formy jednoznaczne; (d) grupa homonimów jako jednostka: F przy grupie, wszyscy członkowie dzielą rangę, grupa wchodzi w całości albo wcale. Masa i przykłady (`rok`, `raz`, `dzień`, `lata`/`lato`, `polska`/`polski`) |
| D6 | Progi POP i POP0 | leksemy i formy dla 5k/10k/20k/40k/80k i dla celów pokrycia; próbki przy granicach |
| D7 | Luka potoczna | akceptacja luki w `pop-v1`: tak / osobne zadanie. Miara: ile leksemów potocznych wypada przy kandydatach D6 |
| D8 | Braki danych | (a) brak w obu źródłach: liczba i mapa na statusy §8.2; (b) brak częściowy: tylko dostępne źródło / dolna granica rangi z flagą / wykluczenie; wrażliwość progów D6 na regułę |

Reguły wspólne dla opcji:
- Agregacja wierszy KWJP jednego leksemu (10 510 leksemów ma kilka wierszy lemma): F sumowane; ARF, 1-DP i gatunki z wiersza o największym F (remis: klucz wiersza) albo tylko w raporcie. Nigdy suma ARF/1-DP ani suma całego korpusu z podkorpusami (§8.1).
- Grupa homonimów = zbiór kandydatów jednego wiersza AMBIGUOUS KWJP. F zostaje przy grupie. Nie dzielimy go i nie kopiujemy na członków jako osobnych F.
- Forma NKJP jest jednoznaczna, gdy jej `game_key` należy do dokładnie jednego leksemu wśród wszystkich leksemów SGJP (`sgjp-20260823`, `sgjp-supplement-v1`, z nazwami własnymi i analizami odrzuconymi). `polska` nie jest jednoznaczna, więc nie daje F przymiotnikowi `polski`.
- Brak w KWJP = `ABSENT_OR_BELOW_PUBLICATION_THRESHOLD` (lista „all” ma próg F ≥ 5). Brak w NKJP = `NOT_IN_PUBLISHED_LIST` (lista ma też F = 1). Statusy osobno per źródło, nigdy ranga 0.

### Etap B — decyzje właściciela
| id | wymaganie |
|---|---|
| B1 | Właściciel wybiera D1–D8 po raporcie A. Pytanie zawiera opcje, liczby, przykłady i zalecenie. |
| B2 | Decyzje zapisane w `docs/adr/ADR-007-metoda-pop-v1.md`: status, data, wybór per D, odrzucone opcje, warunek rewizji, ścieżka wycofania NKJP (D3 = sama KWJP). Odwracalne. Numer sprawdzony przed zapisem. |
| B3 | Wartości wpisane do `config/generator/pop.json` (wersja `pop-v1`). ADR i konfiguracja wskazują się nawzajem. |
| B4 | `ATTRIBUTIONS.md`: opis zmian NKJP zgodny z D4. |
| B5 | Bramka B→C: rewizja spec (rew. 3) z wybranymi opcjami i plan etapu C. Bez niej C nie startuje. |

### Etap C — polecenie `pop`
| id | wymaganie |
|---|---|
| C1 | `python3 -m literaki_slownik pop --manifest config/generator/pop-sources.json --config config/generator/pop.json --run-dir <przebieg v29> --release-dir <pakiet LL-PL v29> --output-dir <nowy> [--json]`. Leniwy import, kody 2/3/4/5 jak reszta CLI. |
| C2 | Walidator manifestu: `run-dir/manifest.json` ma `readiness: FROZEN` (inaczej kod 5) i `export.release_manifest_sha256` = pin. `--release-dir/release-manifest.json` ma ten sam hash. `run-dir/lists/standard.txt`, baza i NKJP zgodne z pinami. Niezgodność → kod 3. Manifest wymienia tylko wejścia KWJP i NKJP (oraz bazę/STANDARD); inne źródło → kod 2. |
| C3 | Walidator konfiguracji: znane klucze; opcje D1–D8 z zamkniętej listy; liczby (progi, wagi, limity) z typem i zakresem; nieznany klucz, opcja lub zła liczba → kod 2. D3 = „sama KWJP” jest zawsze przyjmowane (wycofanie NKJP wg ADR-006). |
| C4 | Baza tylko `mode=ro`. Hash bazy przed i po każdym `pop`; różnica → kod 5, nic nie trafia do `--output-dir`. Zero zapisów w run-dir i release-dir. |
| C5 | Jednostka: leksem, klucz `(source_id, lemma_id)`, albo grupa homonimów wg D5. Ranga deterministyczna, klucz `(-miara, klucz jednostki)`. Miara wg D3 z rang/percentyli; agregacja wierszy KWJP wg reguł wspólnych; bez sumowania ARF/1-DP i całości z podkorpusami (§8.1). |
| C6 | Brak danych ≠ 0. Każda jednostka ma status per źródło (§8.2: `OBSERVED`, `ABSENT_OR_BELOW_PUBLICATION_THRESHOLD`, `NOT_IN_PUBLISHED_LIST`, `UNMATCHED`, `NOT_APPLICABLE`, `UNAVAILABLE`). Brak pełny i częściowy wg D8. |
| C7 | Homonimy wg D5. Nigdy nie kopiujemy ani nie dzielimy F jednej formy/lematu na kilka leksemów. Grupa dzieli rangę, nie F. |
| C8 | NKJP: strumień gz, NFC, małe litery, reguła czyszczenia D4 z identyfikatorem wersji, agregacja po `game_key`. F trafia do leksemu tylko z formy jednoznacznej wobec wszystkich leksemów SGJP. |
| C9 | Formy listy: formy jednostki z `lists/standard.txt` (sprawdzony hashem), zawężone wg D2 (klasy, konstrukcje, reguła przynależności). Forma konstrukcji należy do leksemu przez `derivation_candidate.lemma_id` i `source_id` składnika; wchodzi do POP tylko razem z tym leksemem. Wynik POP0 ⊆ POP ⊆ STANDARD, sprawdzany przed zapisem; naruszenie → kod 4. |
| C10 | Progi POP i POP0 wg D6. Raport podaje wynikowy próg rangi, liczbę leksemów, liczbę form, pokrycie w każdym mianowniku z D1. |
| C11 | Pakiet: `POP.txt.gz`, `POP0.txt.gz` (posortowane `game_key`, `\n`; gzip z `mtime=0`, pustą nazwą pliku, poziomem 9), `reports/` (pokrycie, rangi jednostek z miarami i statusami, wrażliwość wag, próbki, szablon przeglądu), `release-manifest.json`, `ATTRIBUTIONS.md`, `LIMITATIONS.md`, `TERMS.md`, `SHA256SUMS`. |
| C12 | Manifest pakietu: `status: BUILT`; hashe wszystkich wejść, w tym zmierzony hash bazy; `code_identity`; hash konfiguracji; identyfikator ADR-007; wersja reguły NKJP; hashe wyjść. Bez czasów i ścieżek bezwzględnych. |
| C13 | Zapis do stagingu, potem `export.rename_noreplace` na `--output-dir`; pliki 0444. Katalog istnieje → kod 4. |
| C14 | Bez surowego NKJP i bez liczb NKJP per forma lub per leksem w pakiecie i w `explain`. NKJP tylko jako ranga/percentyl, także dla leksemu z jedną formą. |
| C15 | Czas na prawdziwych danych: ≤ 10 min na tym Macu (odczyt 14 s + 2 × hash 14 s zmierzone w audycie). |
| C16 | `explain --variant pop\|pop0 --pop-dir <pakiet> --run-dir <v29> --word <słowo>` przez osobną funkcję `explain_pop`; `choices` w CLI rozszerzone, `decisions.VARIANTS` bez zmian. Wynik: czy w STANDARD; leksemy słowa; per jednostka ranga, miary, statusy, próg; powód (`IN_POP0`, `IN_POP`, `BELOW_THRESHOLD`, `NO_DATA`, `FORM_NOT_TYPICAL`, `NOT_IN_STANDARD`). Piny pakietu ≠ run-dir → kod 3. |
| C17 | Próbki: `quality._config` przyjmuje zamkniętą konfigurację `pop-quality-v1` (seed `literaki-slownik-pop-v1`, 30, to samo kodowanie) obok `quality-v1`; obie bez innych wartości. Konfiguracja w `pop.json` pod kluczem `sampling`. Warstwy: granica POP wewnątrz/na zewnątrz, granica POP0 wewnątrz/na zewnątrz, braki danych, rozbieżność KWJP–NKJP, grupy homonimów, części mowy, krótkie/długie słowa. `review_template` dostaje jako `canonical_index_sha256` hash raportu rang jednostek pakietu (indeks POP). |
| C18 | `ATTRIBUTIONS.md`, `LIMITATIONS.md`, `TERMS.md` generowane z `pop-sources.json` i ADR-007. TERMS: warunki list (formy z SGJP, wybór miarą z KWJP i NKJP, CC BY wg ADR-006) i kodu (BSD-2-Clause). |

### Etap D — odbiór
| id | wymaganie |
|---|---|
| D-1 | Dwa niezależne przebiegi `pop` do dwóch katalogów. `SHA256SUMS` i wszystkie pliki równe bajtowo. |
| D-2 | Hash bazy v29 przed i po obu przebiegach równy 85b23ca5…; release-manifest v29, `lists/`, `manifest.json` i `reports/` przebiegu bez zmian (hashe przed i po). |
| D-3 | `scripts/check_pop_package.py --pop-dir <pakiet> [--review <plik>]`, bez importu `pop.py`: `SHA256SUMS` zgodne; POP0 ⊆ POP ⊆ STANDARD na plikach; brak surowego NKJP i liczb NKJP (skan pakietu). |
| D-4 | Przegląd próbek: agent ocenia każdą pozycję, właściciel zatwierdza. Wynik `pop-v1-review.json` ze statusem `REVIEWED`, `sample_sha256` próbki i hashem `SHA256SUMS` pakietu. |
| D-5 | `check_pop_package.py --review` zwraca 0 tylko, gdy przegląd ma status `REVIEWED`, każdą pozycję ocenioną, `sample_sha256` = próbka pakietu i hash `SHA256SUMS` = pakiet. Inaczej kod 4. |
| D-6 | Liczby pakietu (leksemy, formy, pokrycie) = liczby raportu A dla wybranych opcji. Gdy `code_identity` w `measure.json` ≠ w manifeście pakietu, najpierw ponowny pomiar A na kodzie pakietu. |
| D-7 | Wynik odbioru w `verification/pop-acceptance.md` zadania: hashe, liczby, wynik przeglądu, wynik D-3/D-5. |

### Etap E — wydanie i wiki
| id | wymaganie |
|---|---|
| E1 | GitHub Release `pop-v1`: pliki pakietu z C11 i osobny asset `pop-v1-review.json`. Przed `gh release create` musi przejść `check_pop_package.py --review` (kod 0); inaczej brak wydania. Notatka: liczby, hashe, podstawa (LL-PL v29), ADR-007, ograniczenia. |
| E2 | Atrybucja: SGJP i KWJP jak w LL-PL, NKJP wg ADR-006 (twórca, tytuł, URL, „CC BY, wersja nieokreślona”, zmiany, brak poparcia). |
| E3 | `LIMITATIONS.md`: POP ⊆ LL-PL STANDARD, nie ⊆ SJP; miara użycia ≠ znajomość; luka potoczna; segmentacja KWJP; grupy homonimów (jeśli D5 = d). |
| E4 | Wiki wg `docs/runbook-wiki.md`. Wstępne strony `Slownik-POP` i `Slownik-POP0` już są, bez tezy o „przeciętnym graczu” i bez przesądzania form. Etap E: liczby z pakietu, metoda z ADR-007, link do Release; usunąć „W przygotowaniu” w `Slownik-POP`, `Slownik-POP0`, `Home`, `_Sidebar`, `Slownik-STANDARD`; wiersz w `Historia-zmian`. Bez tez o znajomości słów bez przeglądu. |
| E5 | Dokumenty: `docs/generator/cli.md` (polecenie `pop`, warianty `explain`), `docs/generator/jakosc.md` (kontrakt `pop-quality-v1`), `docs/runbook-wiki.md`, `docs/plan-dalszych-prac-runbook.md:51` (usunąć „NKJP BLOCKED”). |
| E6 | Linki: `curl -fI` na każdy asset Release i na strony wiki zwraca 200. |

## Kryteria odbioru etapów
| etap | gotowe, gdy |
|---|---|
| A | dwa przebiegi skryptu dają ten sam `measure.json`; hash bazy bez zmian; raport ma tabelę dla każdej z D1–D8, pomiar A9 i próbki |
| B | ADR-007 zaakceptowany przez właściciela; `pop.json` przechodzi walidator; `ATTRIBUTIONS.md` zgodny z D4; spec rew. 3 i plan C gotowe (B5) |
| C | testy `tests/test_pop.py` zielone; pełny zestaw testów zielony; `pop` na v29 ≤ 10 min |
| D | D-1…D-7 spełnione; właściciel zatwierdził przegląd |
| E | Release `pop-v1` opublikowany po D-5; wiki wypchnięte; E6 zielone; commit i push repo |

## Komponenty do ponownego użycia

### Istniejący kod
| plik | co daje |
|---|---|
| `scripts/benchmark_sjp.py` | przepływ pomiaru nad zamrożonym przebiegiem (bez jego wad: czas w wyniku, `SystemExit`, nieatomowy zapis) |
| `scripts/audit_nkjp.py` | parser `1grams.gz` (`r" *([0-9]+) (.+)\n"`) |
| `literaki_slownik/database.py` `connect(readonly=True)` | połączenie ro, `game_key()`, `nfc()` |
| `literaki_slownik/canonical.py` | `dumps`, `load_json`, `sha256`, `write_json` |
| `literaki_slownik/inputs.py` | `checked_file`, `GeneratorError` |
| `literaki_slownik/run.py` | `code_identity` |
| `literaki_slownik/export.py` | `rename_noreplace`, `READ_ONLY`, `write_release_manifest` |
| `literaki_slownik/quality.py` | `sample_strata`, `review_template`, `sampling_digest`; `_config` rozszerzony o `pop-quality-v1` |
| `literaki_slownik/verify.py:468-520` | wzór `_markdown_attributions/limitations/terms` dla C18 |
| `literaki_slownik/kwjp.py` | `METRICS` (freq, ARF, DP, 1-DP, total_freq) |
| `literaki_slownik/decisions.py` | `nonfiction_frequencies` (jeśli D3 użyje gatunków) |
| `literaki_slownik/explain.py` | dostęp ro do FROZEN, formatowanie; nowa funkcja `explain_pop` obok |
| `literaki_slownik/cli.py` | subparser, `_finish`, kody wyjścia |
| `data/work/release-LL-PL-v29/` | `release-manifest.json` (pin, `--release-dir`); układ pakietu |
| `tests/release_helpers.py`, `tests/helpers.py` | fikstura SGJP (`kot`, `zamek:a/b`), `complete_run`, `make_review` |
| `tests/test_kwjp.py` | helper gz CSV — ten sam wzór dla małego `1grams.gz` |
| `tests/test_explain.py:22,36` | wzór „hash bazy bez zmian po kroku ro” |

### Nowe pliki i dlaczego
| plik | dlaczego nowy |
|---|---|
| `scripts/measure_pop.py` | brak pomiaru popularności; benchmark SJP mierzy co innego |
| `scripts/check_pop_package.py` | niezależna kontrola pakietu i przeglądu (D-3, D-5); musi nie zależeć od `pop.py` |
| `literaki_slownik/pop.py` | brak kodu popularności; jeden moduł funkcyjny jak reszta |
| `config/generator/pop-sources.json` | `inputs.py` wymaga dokładnie 14 artefaktów LL-PL; NKJP zmieniłby tożsamość LL-PL |
| `config/generator/pop.json` | `quality.json` jest zamknięty dla `quality-v1`; metoda POP potrzebuje własnych, wersjonowanych wartości |
| `docs/adr/ADR-007-metoda-pop-v1.md` | zapis decyzji D1–D8 |
| `tests/test_pop.py` | brak testów popularności |

Bez nowych klas, bez skali ciągłej `vocabulary_level`, bez losowego komponentu wiedzy, bez własnego samplera.

## Podejście techniczne
- Przepływ: piny i hash bazy → STANDARD z `lists/standard.txt` → KWJP per `source_id` z bazy ro → NKJP strumieniem → jednostki (leksem lub grupa) → miary → rangi → progi → formy → kontrola podzbiorów → hash bazy → pakiet.
- Leksem ↔ formy: `evidence_candidate.lexeme_id` → `interpretation` → `surface_form.game_key`; konstrukcje przez `derivation_candidate.lemma_id` + `source_id` składnika → klucz leksemu. Tylko klucze STANDARD, reguła przynależności wg D2.
- Sortowanie i agregacja w Pythonie, nie w SQLite temp.
- Parametry zależne od D1–D8 są polami `pop.json`. Kod obsługuje opcje wybrane w ADR-007, opcje porównywane w raporcie i zawsze D3 = „sama KWJP”. Walidator odrzuca resztę.
- Pomiar i `pop` dzielą funkcje ładowania danych z `pop.py` (skrypt importuje moduł). `code_identity` w obu wynikach pozwala to sprawdzić (D-6).

## Wskazówki do implementacji

### Testy
- 2–8 testów na grupę kroków; weryfikacja grupy uruchamia tylko nowe testy.
- Grupy: walidacja manifestu i konfiguracji; ranking, agregacja wierszy i podzbiory; NKJP (czyszczenie, kolizje, jednoznaczność) i homonimy; formy konstrukcji; determinizm i baza bez zmian; próbki `pop-quality-v1` i `check_pop_package.py`; `explain` dla POP; skrypt pomiaru (dym na fiksturze).
- Kluczowe przypadki: POP0 ⊆ POP ⊆ STANDARD; dwa przebiegi równe bajtowo (z gzip); hash bazy bez zmian; brak ≠ 0 (pełny i częściowy, osobne statusy KWJP/NKJP); `zamek:a/b` bez kopiowania F; grupa homonimów wchodzi w całości; forma NKJP wspólna z nazwą własną nie daje F; forma konstrukcji wchodzi z leksemem składnika; `ul.`→`ul` wg D4; zła konfiguracja lub liczba spoza zakresu → kod 2; manifest z wejściem innym niż KWJP/NKJP → kod 2; zły pin → kod 3; nie-FROZEN → kod 5; istniejący katalog → kod 4; skan pakietu bez liczb NKJP (C14); D3 = sama KWJP przechodzi walidator; przegląd UNREVIEWED lub z innym hashem → kod 4.
- `quality-v1` dalej przyjmowane bez zmian; testy `tests.test_quality` bez zmian, plus 1–2 testy na `pop-quality-v1`.
- Testy LL-PL bez zmian (5 testów oczekuje NKJP w `unavailable`).
- Polecenie: `python3 -m unittest discover -s tests -p 'test_*.py'`.

### Zgodność ze standardami
- `AGENTS.md`: po polsku, zwięźle; decyzje o składzie słownika z właścicielem, z przykładami i alternatywami; wiki w tej samej pracy.
- Spec v3 (`docs/literaki-niezalezne-slowniki-prompt-v3.md`): §2.1 (znajomość ⊆ dopuszczalność), §2.2 (odrzucona interpretacja nie wraca), §8.1 (bez kopiowania F, bez sumowania ARF/1-DP), §8.2 (statusy braków, wrażliwość), §9.1 (leksem, liczby leksemów i form), §9.4 (F, ARF, 1-DP, gatunki, pewność, rangi/percentyle, wagi, próbki), §13 (odtwarzalność, wyjaśnialność).
- ADR-006: atrybucja NKJP, bez redystrybucji surowego pliku, wycofanie = pakiet bez NKJP.
- `docs/generator/publikacja.md`: BSD-2-Clause kod, CC BY 4.0 raporty; układ pakietu.
- `docs/generator/jakosc.md`: kontrakt `sample_strata` i `review_template`, status UNREVIEWED do zatwierdzenia; jawna zmiana kontraktu dla `pop-quality-v1`.
- `docs/literaki-prosty-jezyk-minimum-leksykalne-kierunki.md` §4–5: bez zewnętrznych list; bez przypisywania poziomów do wieku lub wykształcenia.

## Ograniczenia (twarde)
| ograniczenie | sprawdza |
|---|---|
| tylko KWJP i NKJP jako wejście | walidator manifestu (C2), test |
| SJP.pl nieużywany w `pop-v1` | manifest POP, przegląd kodu |
| bez list zewnętrznych (Jasnopis, Logios, Zgółkowa, Kurzowa, PSONI, OSPS, PoliMorf, Wikisłownik) | manifest POP |
| brak danych ≠ 0 | test C6 |
| bez kopiowania F między homonimami | test C7, C8 |
| POP0 ⊆ POP ⊆ STANDARD | `pop` przed zapisem, D-3 |
| odtwarzalność bajtowa | D-1, test |
| zamrożony przebieg i baza bez zmian | A1, C4, D-2, test |
| atrybucja wg ADR-006 | C18, E2 |
| bez surowego NKJP i liczb NKJP w pakiecie | C14, D-3, test |
| wydanie tylko po zatwierdzonym przeglądzie | D-5, E1 |

## Poza zakresem
- Integracja z `Literaki-server`, botami i opcją stołu (tam też rozstrzygnięcie §2.2 dla stołu).
- Nowy build LL-PL; zmiany `sources.json`, `inputs.py`, testów LL-PL.
- Skala ciągła `vocabulary_level`, losowa wiedza botów, model FORM i HYBRID jako osobne listy.
- Miara POP względem SJP.pl.
- Słowniki tematyczne.
- Ręczne dodatki słów potocznych.
- Zmiana listy `familiar/` na serwerze.

## Kryteria sukcesu
| miara | cel |
|---|---|
| podzbiory | POP0 ⊆ POP ⊆ STANDARD, 0 wyjątków |
| powtarzalność | 2 przebiegi, 100% plików równych bajtowo |
| baza v29 | hash przed = po = 85b23ca5… w każdym `pop` i w D-2 |
| czas `pop` | ≤ 10 min |
| rozmiar POP0 | ok. rząd wielkości mniejszy niż POP (wg D6) |
| przegląd | 30 pozycji na warstwę, ocena agenta, zatwierdzenie właściciela, `check_pop_package.py --review` = 0 |
| wydanie | Release `pop-v1` z SHA256SUMS, przeglądem i atrybucją NKJP |
| wiki | strony POP/POP0 z liczbami, bez „W przygotowaniu”; Home, _Sidebar, Slownik-STANDARD, Historia-zmian |

## Założenia
- Zamrożony przebieg `data/work/lists-v30-20261010-165826-a` (FROZEN), pakiet `data/work/release-LL-PL-v29` i `cache/nkjp/1grams.gz` są lokalnie i zgodne z pinami (sprawdzone w audycie).
- Kwalifikator „pot.” jest czytelny z `interpretation.qualifiers` (62 090 interpretacji, sprawdzone).
- Numer ADR-007 jest wolny (dziś tylko ADR-006); sprawdzić przed zapisem.
