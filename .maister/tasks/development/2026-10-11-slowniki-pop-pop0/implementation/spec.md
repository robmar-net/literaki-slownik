# Specyfikacja: słowniki POP i POP0 (#3)

> **Uwaga (2026-10-11):** metoda zmieniła się po przeglądach i weryfikacji (ADR-007 rew. 2–4, metoda `pop-v2`): log-ipm, `prune-weak-members-v2`, D8 `lower-bound-kwjp-absent`, straż częstych form, warunki list jak LL-PL. Gdzie ta specyfikacja mówi inaczej (percentyle F, `available-only`, liczby D-6), obowiązuje ADR-007 rew. 4 i `config/generator/pop.json`.


Rewizja 3 (2026-10-11), bramka B5. Opcje wybrane w [ADR-007](../../../../../docs/adr/ADR-007-metoda-pop-v1.md) zamiast list opcji. Rew. 2: po audycie `verification/spec-audit.md`.

## TL;DR
- POP i POP0 to dwie stałe listy popularnych słów. POP0 ⊆ POP ⊆ STANDARD z LL-PL v29.
- Metoda `pop-v1` jest wybrana (ADR-007, D1–D9) i zapisana w `config/generator/pop.json`.
- POP = 60 000 leksemów, POP0 = 20 000, pełna odmiana. Miara: percentyle KWJP i NKJP, F, waga 0,5. Nazwy własne poza rankingiem.
- Etapy A i B są zrobione (grupy 1–9). Zostają: C polecenie `pop` → D odbiór z przeglądem właściciela → E wydanie `pop-v1` i wiki.
- Wydanie tylko po zatwierdzonym przeglądzie próbek, sprawdzonym skryptem. Integracja z serwerem gry jest poza zakresem.

## Key Decisions
- D1–D9 przyjęte w ADR-007 przez agenta z upoważnienia właściciela (2026-10-11: „podnieść oba limity; POP mocno, POP0 trochę; decyzje podejmij sam”). Odwracalne.
- D2 = pełna odmiana. To zmiana wobec wcześniejszej odpowiedzi właściciela „typowe formy” (`analysis/clarifications.md`). Powód: bez czterech klas form jest o 45% mniej, a słownik stołu wymaga pełnej odmiany (§2.2).
- `pop` przyjmuje tylko wartości ADR-007. Jedyny wyjątek: D3 = sama KWJP (F), ścieżka wycofania NKJP (ADR-006).
- Nowy moduł `literaki_slownik/pop.py` i podkomenda `pop`. LL-PL (`sources.json`, `inputs.py`, `decisions.VARIANTS`) bez zmian.
- Własny manifest `config/generator/pop-sources.json` z pinami v29 (baza 85b23ca5…, release-manifest 54705743…, STANDARD a432c7c5…, NKJP 73af4909…).
- Klucz leksemu = `(source_id, lemma_id)`.
- Pakiet ma status `BUILT`. Wydanie wymaga `pop-v1-review.json` ze statusem `REVIEWED`, związanego hashami z pakietem. Sprawdza to `scripts/check_pop_package.py`.
- Pakiet nie ma pliku NKJP ani liczb NKJP per forma lub leksem. NKJP tylko jako ranga lub percentyl (ADR-006).
- Podstawa D-6: `code_identity` pomiaru = `tree_sha256` 81a5f82a… (commit 7133fbe). Zmiana kodu rankingu w C → ponowny pomiar.

## Open Questions / Risks
- Liczby dla 60 000 pochodzą z sondy w dodatku raportu, nie z `measure.json`. Dla POP0 = 20 000 nie ma liczby z pomiaru. D-6 porównuje POP z sondą, POP0 zapisuje jako nowy wynik.
- Pełna odmiana: bot zna każdą formę leksemu z POP, także rzadkie (wołacz, imiesłowy). Ocena w przeglądzie D-4.
- `e-common` nadal łączy zwykłe homonimy (`nie`/`on`/`jeść`, największa grupa 22). POP „zna” oba leksemy `zamek`. F nie jest kopiowane.
- Miara zależy od NKJP (ADR-006). Ścieżka wycofania (sama KWJP) musi działać bez NKJP (C19).
- `kot` (ranga 9 128) musi być w POP0. Brak = błąd `pop` i powrót do D6.
- Serwer gra na `pl-sjp-20260820`. Bot z POP ⊆ STANDARD przy stole SJP może zagrać słowo spoza SJP. Mówią o tym wiki i LIMITATIONS.
- KWJP dzieli formy przeszłe (`zrobił`+`em`). To brak, nie zero.

## Cel
Dać botom i ewentualnej opcji stołu dwie odtwarzalne listy słów znanych z tekstów, wybrane miarą z korpusów i przyjęte przez właściciela.

## Historie użytkownika
- Jako właściciel chcę raportu z liczbami i przykładami, żeby wybrać metodę i progi na danych, nie na opisach.
- Jako twórca botów chcę listy POP i POP0 z hashami i manifestem, żeby bot znał tylko popularne słowa.
- Jako właściciel chcę zapytać o słowo i usłyszeć, czemu jest albo go nie ma w POP/POP0.
- Jako odwiedzający wiki chcę wiedzieć, czym są POP i POP0, ile mają słów i skąd je pobrać.

## Metoda `pop-v1` (ADR-007)

| # | decyzja | wybór | pole `pop.json` | liczba z raportu |
|---|---|---|---|---|
| D1 | mianownik pokrycia | `kwjp-standard`; raporty też `kwjp-all` | `d1` | sufit `kwjp-all` 91,1% |
| D2 | formy | pełna odmiana, konstrukcje tak, reguła (i) | `d2` = `{classes: [], constructions: yes, membership: i}` | reguła (i) 10,5 s, (ii) 907 s |
| D3 | miara | KWJP+NKJP z percentyli, F, waga 0,5 | `d3` | 98,3% przy 40 000; sama KWJP: Spearman 0,9705 |
| D4 | czyszczenie NKJP | `strip-edges-keep-dot` (`nkjp-clean-strip-edges-keep-dot-v1`) | `d4` | 87,1% tokenów, 9,39% masy scalonej |
| D5 | homonimy | `e-common`: grupa homonimów bez nazw własnych | `d5` | NKJP przypisane 72,6%, grupa ≤ 22 |
| D6 | progi | POP 60 000, POP0 20 000 leksemów (liczba) | `d6` | 60 000 → 45 229 jednostek, 1 328 263 form, 98,5% |
| D7 | luka potoczna | przyjęta, opis w LIMITATIONS | `d7` = `accepted` | 597 z 2 410 potocznych w POP 40 000 |
| D8 | braki danych | pełny → poza listą; częściowy → `available-only` z flagą | `d8` | 128 504 jednostek bez danych |
| D9 | nazwy własne | poza rankingiem; ich formy tylko przez zwykłe leksemy | `proper_names_in_ranking: false` | — |
| — | warunek D6 | `kot` w POP0 | `must_include_pop0: ["kot"]` | ranga 9 128 |

Ścieżka wycofania NKJP: `d3 = {source: kwjp, field: F}`, `d4 = null`.

Reguły wspólne:
- Agregacja wierszy KWJP jednego leksemu: F sumowane. Nigdy suma ARF/1-DP ani suma całości z podkorpusami (§8.1).
- Grupa homonimów (`e-common`): union-find po grupach AMBIGUOUS KWJP i po zbiorach właścicieli form NKJP. Łączy tylko zbiory, w których każdy właściciel jest zwykłym leksemem z formą w STANDARD. F zostaje przy grupie; nie dzielimy go i nie kopiujemy.
- Właściciele formy NKJP liczeni wobec wszystkich leksemów SGJP (`sgjp-20260823`, `sgjp-supplement-v1`, z nazwami własnymi i analizami odrzuconymi). Zbiór z nazwą własną nie tworzy grupy; jego F zostaje nieprzypisane.
- Brak w KWJP = `ABSENT_OR_BELOW_PUBLICATION_THRESHOLD`, w NKJP = `NOT_IN_PUBLISHED_LIST`. Statusy osobno per źródło, nigdy ranga 0.

## Wymagania

### Etap A — pomiar (zrobione, grupy 1–7)
| id | wymaganie |
|---|---|
| A1 | `scripts/measure_pop.py` sprawdza piny z `pop-sources.json` i hash bazy przed i po. |
| A2 | Wynik w nowym `data/work/pop-measure-<stempel>/`; istniejący katalog → kod 4. |
| A3 | `measure.json` kanoniczny, z `code_identity` i `options_sha256`; dwa przebiegi równe bajtowo (b = c). |
| A4 | Raport `report.md`, kopia `analysis/pop-measure-report.md`, z dodatkiem o progach i decyzjach. |
| A5 | Tabele opcji D1–D8 z liczbami i przykładami; dla D5 top 50 wierszy AMBIGUOUS. |
| A6 | Luka potoczna: różnica percentyli NKJP–KWJP, kwalifikator `pot.`. |
| A7 | Próbki graniczne `pop-quality-v1`, 30 na warstwę, ocena wstępna agenta. |
| A8 | Wydajność: KWJP zbiorczo, bez dużych sortowań w SQLite (pomiar 261 s, RSS 3,6 GB). |
| A9 | Formy konstrukcji (85 351) i czas reguł przynależności. |
| A10 | NKJP w raporcie tylko jako rangi, percentyle i udziały (C14). |

### Etap B — decyzje (zrobione, grupy 8–10)
| id | wymaganie |
|---|---|
| B1 | Decyzje D1–D9 po raporcie A; właściciel delegował je agentowi (2026-10-11). |
| B2 | `docs/adr/ADR-007-metoda-pop-v1.md`: status, wybór, odrzucone opcje, rewizja, wycofanie NKJP. |
| B3 | `config/generator/pop.json` (`pop-v1`) i `pop.load_config`; ADR i konfiguracja wskazują się nawzajem. |
| B4 | `ATTRIBUTIONS.md`: zmiany NKJP wg D4. |
| B5 | Bramka B→C: ta rewizja spec i plan C. Właściciel zatwierdza; bez tego grupa 11 nie startuje. |

### Etap C — polecenie `pop`
| id | wymaganie |
|---|---|
| C1 | `python3 -m literaki_slownik pop --manifest config/generator/pop-sources.json --config config/generator/pop.json --run-dir <przebieg v29> --release-dir <pakiet LL-PL v29> --output-dir <nowy> [--json]`. Leniwy import, kody 2/3/4/5 jak reszta CLI. |
| C2 | Wejścia przez `pop.check_inputs`: run-dir `FROZEN` (inaczej kod 5), piny release-manifestu, `standard.txt`, bazy i NKJP (niezgodność → kod 3). Inne źródło niż KWJP/NKJP → kod 2. |
| C3 | Konfiguracja przez `pop.load_config`, zawężone do wartości ADR-007: D1, D2, D4, D5, D7, D8, D9 dokładnie jak w tabeli metody; D6 `count`, POP0 < POP; D3 = KWJP+NKJP F albo sama KWJP F z `d4 = null`. Inna wartość (np. `d5 = d`, reguła (ii), klasy D2) → kod 2. |
| C4 | Baza tylko `mode=ro`. Hash bazy przed i po; różnica → kod 5, nic w `--output-dir`. Zero zapisów w run-dir i release-dir. |
| C5 | Jednostki: `pop.units(..., 'e', relevant, nkjp, owners, eligible=relevant − nazwy własne)`. Ranking tylko ze zwykłych leksemów z formą w STANDARD (D9): nazwa własna nie ma rangi i nie liczy się do progu. Ranga: klucz `(-miara, klucz jednostki)` (`pop.rank_units`). |
| C6 | Miara (`pop.measure`): `0,5 × percentyl KWJP F + 0,5 × percentyl NKJP`. Brak częściowy: percentyl dostępnego źródła, flaga `single_source:<źródło>`. Brak pełny: status `NO_DATA`, jednostka poza listami. Statusy per źródło wg §8.2. |
| C7 | Grupa dzieli rangę, nie F. Nigdy nie kopiujemy ani nie dzielimy F jednej formy/lematu na kilka leksemów. |
| C8 | NKJP: strumień gz, NFC, małe litery, reguła `nkjp-clean-strip-edges-keep-dot-v1`, agregacja po `game_key` (`pop.read_nkjp`). F trafia do jednostki tylko ze zbioru właścicieli, który `e-common` przypisuje. |
| C9 | Formy: pełna odmiana. Formy leksemu z reguły (i) (`pop.load_forms`) plus formy konstrukcji (`pop.load_constructions`) jego składnika. Bez wykluczeń klas. Tylko klucze z `lists/standard.txt`. POP0 ⊆ POP ⊆ STANDARD sprawdzane przed zapisem; naruszenie → kod 4. |
| C10 | Progi (`pop.threshold`): prefiks rang, jednostka w całości albo wcale; POP ≤ 60 000 leksemów, POP0 ≤ 20 000. Każde słowo z `must_include_pop0` (`kot`) musi być w POP0; brak → kod 4, nic nie zapisane. Raport progów: ranga graniczna, jednostki, leksemy, formy, pokrycie `kwjp-standard` i `kwjp-all`. |
| C11 | Pakiet: `POP.txt.gz`, `POP0.txt.gz` (posortowane `game_key`, `\n`; gzip `mtime=0`, pusta nazwa, poziom 9), `reports/` (progi i pokrycie, rangi jednostek z miarami, statusami i flagami, próbki, szablon przeglądu), `release-manifest.json`, `ATTRIBUTIONS.md`, `LIMITATIONS.md`, `TERMS.md`, `SHA256SUMS`. |
| C12 | Manifest pakietu: `status: BUILT`; hashe wejść, w tym zmierzony hash bazy; `code_identity`; hash `pop.json`; `ADR-007`; `must_include_pop0` (dla D-3); id reguły NKJP (albo brak przy samej KWJP); hashe wyjść. Bez czasów i ścieżek bezwzględnych. |
| C13 | Zapis do stagingu, potem `export.rename_noreplace`; pliki 0444. Katalog istnieje → kod 4. |
| C14 | Bez surowego NKJP i bez liczb NKJP per forma lub leksem w pakiecie i w `explain`. NKJP tylko jako ranga/percentyl. |
| C15 | Czas na v29: ≤ 10 min na tym Macu (pomiar A z wszystkimi opcjami: 261 s). |
| C16 | `explain --variant pop\|pop0 --pop-dir <pakiet> --run-dir <v29> --word <słowo>` przez `explain_pop`; `decisions.VARIANTS` bez zmian. Wynik: czy w STANDARD; leksemy słowa; per jednostka ranga, miara, statusy, flagi, próg. Powód: `IN_POP0`, `IN_POP`, `BELOW_THRESHOLD`, `NO_DATA`, `PROPER_NAME_ONLY`, `NOT_IN_STANDARD`. Piny pakietu ≠ run-dir → kod 3. |
| C17 | Próbki: `quality` z `pop-quality-v1` (seed `literaki-slownik-pop-v1`, 30 na warstwę, z `pop.json` → `sampling`). Warstwy: granica POP wewnątrz/zewnątrz, granica POP0 wewnątrz/zewnątrz, braki danych, rozbieżność KWJP–NKJP, grupy homonimów, części mowy, krótkie/długie słowa. `review_template` dostaje hash raportu rang jednostek. |
| C18 | `ATTRIBUTIONS.md`, `LIMITATIONS.md`, `TERMS.md` z `pop-sources.json` i ADR-007. TERMS: listy CC BY (formy z SGJP, wybór miarą z KWJP i NKJP wg ADR-006), kod BSD-2-Clause. |
| C19 | Wycofanie NKJP: z `d3 = {kwjp, F}`, `d4 = null` polecenie `pop` nie czyta `1grams.gz`, a pakiet nie wymienia NKJP w atrybucjach ani w manifeście. |

### Etap D — odbiór
| id | wymaganie |
|---|---|
| D-1 | Dwa niezależne przebiegi `pop` do dwóch katalogów. `SHA256SUMS` i wszystkie pliki równe bajtowo. |
| D-2 | Hash bazy v29 przed i po obu przebiegach = 85b23ca5…; release-manifest v29, `lists/`, `manifest.json` i `reports/` przebiegu bez zmian. |
| D-3 | `scripts/check_pop_package.py --pop-dir <pakiet> [--review <plik>]`, bez importu `pop.py`: `SHA256SUMS` zgodne; POP0 ⊆ POP ⊆ STANDARD na plikach; słowa z `must_include_pop0` manifestu (`kot`) w POP0; brak surowego NKJP i liczb NKJP. |
| D-4 | Bramka przeglądu: agent ocenia każdą pozycję próbek, właściciel zatwierdza. Wynik `pop-v1-review.json`: status `REVIEWED`, `sample_sha256` próbki, hash `SHA256SUMS` pakietu. Bez zatwierdzenia właściciela nie ma etapu E. |
| D-5 | `check_pop_package.py --review` zwraca 0 tylko przy `REVIEWED`, każdej pozycji ocenionej i zgodnych hashach. Inaczej kod 4. |
| D-6 | Podstawa: `measure.json` z `data/work/pop-measure-20261011-154857-b`, `code_identity` = commit `db15d829…` (dirty), `tree_sha256` `81a5f82ae66f9457…` = pakiet z commitu 7133fbe. Grupa 9 dodała tylko sekcję konfiguracji. Gdy C zmieni kod rankingu (`pop.py` przed sekcją konfiguracji lub `database.py`), najpierw ponowny pomiar A na kodzie pakietu: liczby bazowe = raport A (POP 40 000: 902 062 form, 98,3%). Zawsze: POP pakietu = sonda z dodatku (45 229 jednostek, 1 328 263 formy, 98,5% `kwjp-standard`); liczby POP0 zapisane. |
| D-7 | Wynik w `verification/pop-acceptance.md`: hashe, liczby, `code_identity`, wynik przeglądu, wynik D-3/D-5. |

### Etap E — wydanie i wiki
| id | wymaganie |
|---|---|
| E1 | Bramka wydania: GitHub Release `pop-v1` tylko po `check_pop_package.py --review` = 0. Assety: pliki z C11 i `pop-v1-review.json`. Notatka: liczby, hashe, podstawa LL-PL v29, ADR-007, ograniczenia. |
| E2 | Atrybucja: SGJP i KWJP jak w LL-PL, NKJP wg ADR-006 (twórca, tytuł, URL, „CC BY, wersja nieokreślona”, zmiany wg D4, brak poparcia). |
| E3 | `LIMITATIONS.md`: POP ⊆ STANDARD, nie ⊆ SJP; miara użycia ≠ znajomość; pełna odmiana; luka potoczna (D7); nazwy własne poza rankingiem (D9); grupy homonimów `e-common`; segmentacja KWJP. |
| E4 | Wiki wg `docs/runbook-wiki.md`: `Slownik-POP` i `Slownik-POP0` z liczbami z pakietu, metodą z ADR-007 i linkiem do Release; usunąć „W przygotowaniu” w `Slownik-POP`, `Slownik-POP0`, `Home`, `_Sidebar`, `Slownik-STANDARD`; wiersz w `Historia-zmian`. Bez tez o znajomości słów ponad przegląd. |
| E5 | Dokumenty: `docs/generator/cli.md` (`pop`, `explain` dla POP), `docs/generator/jakosc.md` (`pop-quality-v1`), `docs/runbook-wiki.md`, `docs/plan-dalszych-prac-runbook.md:51` (usunąć „NKJP BLOCKED”). |
| E6 | `curl -fI` na każdy asset Release i strony wiki zwraca 200. |

## Kryteria odbioru etapów
| etap | gotowe, gdy |
|---|---|
| A | zrobione: b = c bajtowo; hash bazy bez zmian; raport z D1–D8, A9, próbkami i dodatkiem |
| B | ADR-007 zaakceptowany; `pop.json` przechodzi `load_config`; `ATTRIBUTIONS.md` wg D4; spec rew. 3 i plan C zatwierdzone przez właściciela |
| C | `tests/test_pop.py` i pełny zestaw zielone; `pop` na v29 ≤ 10 min; `kot` w POP0 |
| D | D-1…D-7 spełnione; właściciel zatwierdził przegląd |
| E | Release `pop-v1` po D-5; wiki wypchnięte; E6 zielone; commit i push repo |

## Komponenty do ponownego użycia

### Istniejący kod
| plik | co daje |
|---|---|
| `literaki_slownik/pop.py` (grupy 1–4, 9) | `load_sources`, `check_inputs`, `database_sha256`, `read_standard`, `load_lexemes`, `load_kwjp_lists`, `kwjp_measures`, `load_forms`, `load_constructions`, `read_nkjp`, `form_owners`, `nkjp_lexeme_ranks`, `units`, `measure`, `rank_units`, `percentiles`, `member_ranks`, `coverage`, `threshold`, `forms_for`, `load_config` |
| `scripts/measure_pop.py` | ponowny pomiar dla D-6; wzór złożenia `e-common` z `eligible` |
| `literaki_slownik/quality.py` | `sample_strata`, `review_template`, `sampling_digest`; `pop-quality-v1` (grupa 5) |
| `literaki_slownik/database.py` | `connect(readonly=True)`, `game_key()`, `nfc()` |
| `literaki_slownik/canonical.py` | `dumps`, `load_json`, `sha256`, `write_json` |
| `literaki_slownik/inputs.py` | `checked_file`, `GeneratorError` |
| `literaki_slownik/run.py` | `code_identity` |
| `literaki_slownik/export.py` | `rename_noreplace`, `READ_ONLY`, `write_release_manifest` |
| `literaki_slownik/verify.py:468-520` | wzór `_markdown_attributions/limitations/terms` dla C18 |
| `literaki_slownik/explain.py` | dostęp ro do FROZEN, formatowanie; `explain_pop` obok |
| `literaki_slownik/cli.py` | subparser, `_finish`, kody wyjścia |
| `data/work/release-LL-PL-v29/` | `release-manifest.json` (pin); układ pakietu |
| `tests/pop_helpers.py`, `tests/release_helpers.py`, `tests/helpers.py` | fikstura SGJP (`kot`, `zamek:a/b`), NKJP, `complete_run`, `make_review` |
| `tests/test_explain.py:22,36` | wzór „hash bazy bez zmian po kroku ro” |

### Nowe i dlaczego
| plik | dlaczego |
|---|---|
| polecenie `pop` w `pop.py` + `cli.py` | brak budowy pakietu; funkcje rankingu już są, brakuje złożenia, progów, zapisu i kontroli |
| `explain_pop` w `explain.py` | `explain` zna tylko warianty LL-PL |
| `scripts/check_pop_package.py` | niezależna kontrola pakietu i przeglądu (D-3, D-5); nie importuje `pop.py` |
| testy w `tests/test_pop.py` i `tests/test_check_pop_package.py` | brak testów budowy i kontroli |

Bez nowych klas, bez skali ciągłej, bez losowej wiedzy, bez własnego samplera. Kod niewybranych opcji zostaje w `pop.py` tylko dla pomiaru; `pop` go nie wywołuje.

## Podejście techniczne
- Przepływ `pop`: piny i hash bazy → `load_config` → STANDARD → leksemy, KWJP, właściciele form → NKJP (pomijane przy samej KWJP) → jednostki `e-common` bez nazw własnych → miara → rangi → progi → `kot` w POP0 → formy (reguła (i) + konstrukcje) → kontrola podzbiorów → hash bazy → staging → pakiet.
- Sortowanie i agregacja w Pythonie, nie w SQLite temp.
- Nowy kod `pop` dopisany poniżej sekcji konfiguracji `pop.py`, żeby nie zmieniać kodu rankingu (D-6).

## Wskazówki do implementacji

### Testy
- 2–8 testów na grupę kroków; weryfikacja grupy uruchamia tylko nowe testy.
- Kluczowe przypadki: POP0 ⊆ POP ⊆ STANDARD; dwa przebiegi równe bajtowo (z gzip); hash bazy bez zmian; brak ≠ 0 (pełny poza listą, częściowy z flagą `single_source`); `zamek:a/b` bez kopiowania F, grupa wchodzi w całości; nazwa własna bez rangi, jej forma wchodzi przez zwykły leksem; forma konstrukcji wchodzi z leksemem składnika; `ul.` nie skleja się z `ul`; brak `kot` w POP0 → kod 4; `pop.json` z opcją spoza ADR-007 → kod 2; sama KWJP przechodzi i nie czyta NKJP; zły pin → kod 3; nie-FROZEN → kod 5; istniejący katalog → kod 4; skan pakietu bez liczb NKJP; przegląd UNREVIEWED lub z innym hashem → kod 4; `explain_pop` z każdym powodem.
- Testy grupy 9 przyjmujące opcje spoza ADR-007 odwrócić po zawężeniu (C3).
- `quality-v1` i testy LL-PL bez zmian.
- Polecenie: `python3 -m unittest discover -s tests -p 'test_*.py'`.

### Zgodność ze standardami
- `AGENTS.md`: po polsku, zwięźle; decyzje o składzie słownika z właścicielem (tu delegowane, zapisane w ADR-007); wiki w tej samej pracy.
- Spec v3 (`docs/literaki-niezalezne-slowniki-prompt-v3.md`): §2.1, §2.2 (pełna odmiana dla stołu), §8.1, §8.2, §9.1, §9.4, §13.
- ADR-006: atrybucja NKJP, bez surowego pliku, wycofanie = pakiet bez NKJP (C19).
- ADR-007: metoda `pop-v1`; każda zmiana to nowa wersja w `pop.json`.
- `docs/generator/publikacja.md`: BSD-2-Clause kod, CC BY 4.0 raporty; układ pakietu.
- `docs/generator/jakosc.md`: `sample_strata`, `review_template`, UNREVIEWED do zatwierdzenia.
- `docs/literaki-prosty-jezyk-minimum-leksykalne-kierunki.md` §4–5: bez list zewnętrznych; bez poziomów wg wieku lub wykształcenia.

## Ograniczenia (twarde)
| ograniczenie | sprawdza |
|---|---|
| tylko KWJP i NKJP jako wejście; SJP.pl nieużywany | C2, manifest POP |
| bez list zewnętrznych (Jasnopis, Logios, Zgółkowa, Kurzowa, PSONI, OSPS, PoliMorf, Wikisłownik) | manifest POP |
| tylko metoda ADR-007 (plus wycofanie NKJP) | C3, test |
| brak danych ≠ 0 | C6, test |
| bez kopiowania F między homonimami | C7, C8, test |
| POP0 ⊆ POP ⊆ STANDARD; `kot` w POP0 | C9, C10, D-3 |
| odtwarzalność bajtowa | D-1, test |
| zamrożony przebieg i baza bez zmian | C4, D-2, test |
| bez surowego NKJP i liczb NKJP w pakiecie | C14, D-3, test |
| wydanie tylko po zatwierdzonym przeglądzie | D-4, D-5, E1 |

## Poza zakresem
- Integracja z `Literaki-server`, botami i opcją stołu.
- Nowy build LL-PL; zmiany `sources.json`, `inputs.py`, testów LL-PL.
- Inne opcje D1–D9 w `pop` (np. typowe formy, reguła (ii), `d`); zmiana metody to nowa wersja i ADR.
- Skala ciągła `vocabulary_level`, losowa wiedza botów, model FORM i HYBRID.
- Miara POP względem SJP.pl; słowniki tematyczne; ręczne dodatki potoczne (D7: osobne zadanie).
- Zmiana listy `familiar/` na serwerze.

## Kryteria sukcesu
| miara | cel |
|---|---|
| podzbiory | POP0 ⊆ POP ⊆ STANDARD, 0 wyjątków; `kot` w POP0 |
| rozmiar POP | ≤ 60 000 leksemów; = sonda: 45 229 jednostek, 1 328 263 formy, 98,5% `kwjp-standard` |
| rozmiar POP0 | ≤ 20 000 leksemów; liczby zapisane w D-7 |
| powtarzalność | 2 przebiegi, 100% plików równych bajtowo |
| baza v29 | hash przed = po = 85b23ca5… |
| czas `pop` | ≤ 10 min |
| przegląd | 30 pozycji na warstwę, ocena agenta, zatwierdzenie właściciela, `--review` = 0 |
| wydanie | Release `pop-v1` z SHA256SUMS, przeglądem i atrybucją NKJP |
| wiki | strony POP/POP0 z liczbami, bez „W przygotowaniu” |

## Założenia
- Przebieg `data/work/lists-v30-20261010-165826-a` (FROZEN), pakiet `data/work/release-LL-PL-v29` i `cache/nkjp/1grams.gz` są lokalnie i zgodne z pinami (sprawdzone w grupie 1).
- Kod rankingu w HEAD (487402c) = kod pomiaru (7133fbe); grupa 9 dodała tylko sekcję konfiguracji (sprawdzone `git diff`).
