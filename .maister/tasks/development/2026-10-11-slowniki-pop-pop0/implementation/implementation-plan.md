# Plan implementacji: słowniki POP i POP0 (#3)

> **Uwaga (2026-10-11):** metoda zmieniła się po przeglądach i weryfikacji (ADR-007 rew. 2–4, metoda `pop-v2`): log-ipm, `prune-weak-members-v2`, D8 `lower-bound-kwjp-absent`, straż częstych form, warunki list jak LL-PL. Gdzie ta specyfikacja mówi inaczej (percentyle F, `available-only`, liczby D-6), obowiązuje ADR-007 rew. 4 i `config/generator/pop.json`.


Podstawa: `implementation/spec.md` (rew. 3, 47 wymagań), `docs/adr/ADR-007-metoda-pop-v1.md`, `config/generator/pop.json`. Plan C, D, E rozpisany w grupie 10 (B5).

## TL;DR
- 17 grup, 102 kroki. A (1–7) i B (8–9) zrobione. Grupa 10 czeka na zatwierdzenie właściciela (10.4).
- Dalej: `pop` rdzeń (11) → pakiet (12) → `explain_pop` (13) ‖ skrypt kontroli (14) → przegląd testów (15) → odbiór na v29 (16, **STOP: przegląd**) → wydanie `pop-v1` i wiki (17).
- `pop` przyjmuje tylko wartości ADR-007 i wycofanie NKJP. Nowy kod poniżej sekcji konfiguracji `pop.py`; kod rankingu bez zmian (D-6).
- Testy: 45 są; C dodaje 27; przegląd do 10. Razem ok. 72–82.

## Key Decisions
- Kod `pop` dopisany na końcu `pop.py`, pod sekcją konfiguracji. Funkcje rankingu (linie przed `# --- Konfiguracja`) i `database.py` bez zmian. Wtedy pomiar A jest podstawą D-6 bez ponownego liczenia.
- Złożenie `pop` wg `scripts/measure_pop.py` (`_load`, `_d5_option('e-common')`, `_select`, `_forms`). Bez `load_forms_accepted` i `load_form_classes`: D2 nie ma klas ani reguły (ii).
- `load_config` zawężone do ADR-007 (C3). Testy grupy 9, które przyjmują inne opcje (waga 1, wycofanie z `d4` ≠ `null`), odwrócone.
- Raporty pakietu: `reports/thresholds.json`, `reports/units.json`, `reports/sample.json`, `reports/review-template.json`. „Indeks POP” = `reports/units.json`; jego hash idzie do `review_template` jako `canonical_index_sha256`.
- Wypełniony przegląd `pop-v1-review.json` jest poza pakietem. Pakiet ma tylko szablon `UNREVIEWED`, więc `SHA256SUMS` się nie zmienia.
- `check_pop_package.py` dostaje `--standard <lists/standard.txt>`. STANDARD nie jest w pakiecie; hash pliku sprawdzany z pinem w manifeście.
- Kontrola „bez liczb NKJP”: klucze z `nkjp` w raportach tylko z listy dozwolonej (`nkjp_rank`, `nkjp_percentile`, `nkjp_status`); brak pliku z surowym NKJP.
- Assety Release wg wzoru `llpl-v29`: listy `.txt.gz`, `pop-v1-pakiet.tar.gz`, `SHA256SUMS`, plus `pop-v1-review.json`.

## Open Questions / Risks
- Bramki właściciela: 10.4 (spec rew. 3 i ten plan) i 16.8 (przegląd próbek). Wykonawca zatrzymuje się w każdej.
- Fikstura ma małe progi. Liczby 60 000/20 000 widać dopiero na v29 (11.7, 16.6).
- Zmiana kodu rankingu w C → ponowny pomiar A (ok. 5 min, bez reguły (ii)) przed porównaniem D-6.
- POP0 = 20 000 nie ma liczby z pomiaru. D-6 tylko ją zapisuje.
- RSS ok. 3,6 GB na przebieg. Dwa przebiegi `pop` po kolei, nie równolegle.
- `tar` assetu nie musi być bajtowo powtarzalny. Treść wiąże `SHA256SUMS` pakietu.

## Overview
Total Steps: 102
Task Groups: 17 (A: 1–7, B: 8–10, C: 11–15, D: 16, E: 17)
Expected Tests: ok. 72–82 (A+B: 45 istniejących, C: 27 nowych, przegląd: do 10)

Zasady dla każdej grupy:
- Nigdy nie pisać do `data/work/lists-v30-20261010-165826-a` ani do `data/work/release-LL-PL-v29`. Baza tylko `mode=ro`.
- `config/generator/sources.json`, `literaki_slownik/inputs.py`, `decisions.VARIANTS` i testy LL-PL bez zmian.
- Docstringi i komunikaty po polsku. JSON przez `canonical.write_json`. Błędy przez `GeneratorError` (2 argumenty/konfiguracja, 3 źródło/hash, 4 integralność/katalog istnieje, 5 gotowość).
- KWJP zbiorczo per `source_id` / zakres `evidence_id`. Bez `LEFT JOIN evidence_candidate` bez kierunku. Sortowanie i agregacja w Pythonie.

## Implementation Steps

### Etap A — pomiar

### Task Group 1: Manifest POP, piny i fikstura
**Dependencies:** None
**Files to Modify:** config/generator/pop-sources.json, literaki_slownik/pop.py, tests/pop_helpers.py, tests/test_pop.py
**Estimated Steps:** 5

- [x] 1.0 Manifest POP i sprawdzanie pinów (A1, część C2)
  - [x] 1.1 Napisz 6 testów w `tests/test_pop.py`
    - poprawny manifest na fiksturze: zwraca ścieżki i hash bazy
    - zły pin bazy → kod 3
    - `run-dir/manifest.json` `export.release_manifest_sha256` ≠ hash `--release-dir/release-manifest.json` → kod 3
    - zły hash `lists/standard.txt` albo NKJP → kod 3
    - przebieg bez `readiness: FROZEN` → kod 5
    - wejście inne niż KWJP/NKJP (np. `sjp`) albo nieznany klucz → kod 2
  - [x] 1.2 Fikstura `tests/pop_helpers.py`
    - przebieg FROZEN i pakiet z `release_helpers` (`complete_pair` + verify/export z `allow_test_fixture`, wzór `tests/test_export.py`)
    - własne SGJP i KWJP (wzór `tests/test_build.py` `manifest`): `zamek:a/b`, `rok` z dwoma leksemami, `lata`/`lato`, `Polska` (nazwa własna) i `polski`, interpretacja z `pot.`, konstrukcja (`nie-` + przymiotnik), `ul`
    - mały `1grams.gz` (wzór `tests/test_kwjp.py`) z `ul.`, `ul`, `ok.`, `polska`, `lata`
    - `pop-sources.json` przypięty do fikstury
  - [x] 1.3 `config/generator/pop-sources.json`
    - `version: pop-sources-v1`; pełne hashe: baza (z `manifest.json` przebiegu), `release-manifest.json` v29, `lists/standard.txt`, `cache/nkjp/1grams.gz`
    - wejścia tylko `kwjp` (z bazy) i `nkjp_1gram`; ścieżka pakietu LL-PL v29
  - [x] 1.4 `literaki_slownik/pop.py`
    - `load_sources(path)`: ścisły walidator kluczy i rodzajów wejść (kod 2)
    - `check_inputs(sources, run_dir, release_dir)`: FROZEN (5), piny (3); reuse `inputs.checked_file`, `canonical.sha256`
    - `database_sha256(path)`: strumień po 1 MB
    - `read_standard(path)` → `frozenset` kluczy
  - [x] 1.5 Uruchom tylko testy z 1.1

**Acceptance Criteria:**
- 6 testów z 1.1 przechodzi
- `pop-sources.json` ma pełne hashe zgodne z danymi na dysku

### Task Group 2: Ładowanie KWJP i SGJP z bazy
**Dependencies:** 1
**Files to Modify:** literaki_slownik/pop.py, tests/pop_helpers.py, tests/test_pop.py
**Estimated Steps:** 7

- [x] 2.0 Dane leksemów i form z bazy tylko do odczytu (A6, A8, A9)
  - [x] 2.1 Napisz 7 testów
    - klucz leksemu to `(source_id, lemma_id)`, nie `lexeme.id`
    - kilka wierszy KWJP jednego leksemu: F sumowane; ARF, 1-DP i gatunki z wiersza o największym F (remis: klucz wiersza)
    - wiersz AMBIGUOUS `zamek` daje grupę `zamek:a/b`; F przy grupie, członkowie bez własnego F
    - formy leksemu tylko z kluczy STANDARD
    - forma konstrukcji trafia do leksemu składnika przez `derivation_candidate.lemma_id` + `source_id`
    - leksem potoczny = `pot.` w dowolnej interpretacji
    - hash bazy przed = po (wzór `tests/test_explain.py:22`)
  - [x] 2.2 `load_kwjp(db, source_id)`
    - zakres `evidence_id` per `source_id`, potem `evidence_link` i `evidence_candidate` w tym zakresie; łączenie w Pythonie
    - lemma-all i gatunki (fikcja, fakt, publicystyka); statusy EXACT/AMBIGUOUS/UNMATCHED; miary z `kwjp.METRICS`
  - [x] 2.3 `load_lexemes(db)`: `lexeme.id` → klucz, źródło, POS, kwalifikatory (`pot.`), nazwa własna
  - [x] 2.4 `load_forms(db, standard)`: leksem → `game_key` przez `interpretation` → `surface_form`
    - reguła (i): forma ∈ STANDARD i jest formą leksemu
    - reguła (ii): analiza tego leksemu przyjęta w STANDARD (`analysis` + `variant_decision`); osobna funkcja, żeby zmierzyć jej czas
  - [x] 2.5 `load_constructions(db, standard)`: `derivation_candidate` bez `interpretation_id` → leksem składnika; liczniki: jeden / żaden / kilka (A9)
  - [x] 2.6 `kwjp_measures(rows)`: agregacja wierszy leksemu wg reguł wspólnych; grupy homonimów jako osobne jednostki; nigdy suma ARF/1-DP ani korpusu z podkorpusami
  - [x] 2.7 Uruchom tylko testy z 2.1

**Acceptance Criteria:**
- 7 testów z 2.1 przechodzi
- żadne zapytanie nie używa `LEFT JOIN evidence_candidate` ani `ORDER BY` na tekście

### Task Group 3: NKJP — czytanie, czyszczenie, jednoznaczność
**Dependencies:** 1
**Files to Modify:** literaki_slownik/pop.py, tests/test_pop.py
**Estimated Steps:** 6

- [x] 3.0 NKJP jako ranga leksemu bez kopiowania F (A10, D4, D5)
  - [x] 3.1 Napisz 6 testów
    - parser `r" *([0-9]+) (.+)\n"` na małym gz; NFC, małe litery, suma po `game_key`
    - trzy reguły czyszczenia: `full-nfc`, `strip-edges`, `strip-edges-keep-dot`; `ul.` i `ok.` w każdej
    - lista kolizji (`ul.`→`ul`, `ok.`→`ok`) z masą obu stron
    - `polska` nie jest jednoznaczna (nazwa własna + przymiotnik) i nie daje F `polski`
    - `lata` (`rok` i `lato`) nie daje F żadnemu leksemowi
    - forma bez wiersza NKJP ma status `NOT_IN_PUBLISHED_LIST`, nigdy 0
  - [x] 3.2 `read_nkjp(path, rule)`: strumień gzip, identyfikator reguły z wersją; suma całości w strumieniu; w pamięci tylko klucze form SGJP
  - [x] 3.3 `nkjp_collisions(...)`: napisy scalane przez regułę, top wg masy
  - [x] 3.4 `form_owners(db)`: `game_key` → klucze leksemów wśród wszystkich leksemów SGJP (`sgjp-20260823`, `sgjp-supplement-v1`, z nazwami własnymi i analizami odrzuconymi); zbiorczo
  - [x] 3.5 `nkjp_lexeme_ranks(...)`: F tylko z formy jednoznacznej; na wyjściu ranga i percentyl, także dla leksemu z jedną formą
  - [x] 3.6 Uruchom tylko testy z 3.1

**Acceptance Criteria:**
- 6 testów z 3.1 przechodzi
- funkcje publiczne zwracają NKJP leksemu tylko jako rangę/percentyl

### Task Group 4: Rangi, pokrycie i opcje D1–D8
**Dependencies:** 2, 3
**Files to Modify:** literaki_slownik/pop.py, tests/test_pop.py
**Estimated Steps:** 7

- [x] 4.0 Wspólne funkcje rankingu dla pomiaru i `pop`
  - [x] 4.1 Napisz 8 testów
    - ranga deterministyczna, klucz `(-miara, klucz jednostki)`, remis rozstrzyga klucz
    - percentyle na małym przykładzie
    - brak pełny i częściowy: osobne statusy KWJP i NKJP, nigdy ranga 0; trzy reguły D8b
    - D5d: grupa `rok` dzieli rangę i wchodzi w całości albo wcale
    - pokrycie w trzech mianownikach D1
    - próg po liczbie jednostek i po celu pokrycia (D6)
    - filtr klas znaczników D2a (wołacz, rozkaźnik, imiesłowy, os. 1/2)
    - Spearman i nakładanie top-N; kombinacja KWJP+NKJP tylko z rang/percentyli, z wagą
  - [x] 4.2 `units(..., d5)`: jednostki dla opcji D5 a–d
  - [x] 4.3 `measure(..., d3, d8)`: sama KWJP (F, ARF, 1-DP, gatunki) albo KWJP+NKJP z wagą; reguła braku częściowego
  - [x] 4.4 `rank_units`, `percentiles`, `coverage(..., d1)`, `threshold(..., d6)`
  - [x] 4.5 `forms_for(units, d2)`: klasy znaczników, konstrukcje tak/nie, reguła przynależności (i)/(ii)
  - [x] 4.6 `spearman`, `top_overlap`
  - [x] 4.7 Uruchom tylko testy z 4.1

**Acceptance Criteria:**
- 8 testów z 4.1 przechodzi
- żadna funkcja nie zwraca 0 w miejsce braku danych

### Task Group 5: Konfiguracja próbek `pop-quality-v1`
**Dependencies:** None
**Files to Modify:** literaki_slownik/quality.py, tests/test_pop_quality.py
**Estimated Steps:** 3

- [x] 5.0 Druga zamknięta konfiguracja w `quality._config` (A7, C17)
  - [x] 5.1 Napisz 3 testy w `tests/test_pop_quality.py`
    - `pop-quality-v1` (seed `literaki-slownik-pop-v1`, 30, `ENCODING`) przyjęte; dwa wywołania `sample_strata` równe
    - inna wartość (wersja, seed, rozmiar, kodowanie, `bool` jako rozmiar) → kod 2
    - mieszanka: wersja `quality-v1` z seedem POP → kod 2
  - [x] 5.2 `_config`: zamknięta mapa `wersja → seed` z dwiema parami; reszta warunków bez zmian
  - [x] 5.3 Uruchom testy z 5.1 i `tests.test_quality` (plik bez zmian)

**Acceptance Criteria:**
- 3 nowe testy i wszystkie `tests.test_quality` przechodzą

### Task Group 6: Skrypt pomiaru `scripts/measure_pop.py`
**Dependencies:** 4, 5
**Files to Modify:** scripts/measure_pop.py, tests/test_measure_pop.py
**Estimated Steps:** 7

- [x] 6.0 Pomiar tylko do odczytu z raportem dla właściciela (A1–A10)
  - [x] 6.1 Napisz 6 testów dymnych na fiksturze
    - dwa przebiegi do dwóch katalogów → `measure.json` równy bajtowo
    - istniejący katalog wyjściowy → kod 4
    - zły pin → kod 3, nic nie zapisane
    - hash bazy przed = po
    - `report.md` ma sekcje D1–D8, A9 i próbki
    - `report.md` nie ma liczb NKJP per forma (skan: tylko rangi/percentyle)
  - [x] 6.2 Argumenty: `--sources`, `--run-dir`, `--release-dir`, `--output-dir`; `main()` zwraca kod, `GeneratorError` → kod i komunikat; bez `SystemExit` w funkcjach
  - [x] 6.3 Przepływ: `check_inputs` → hash bazy → grupy 2–3 → opcje D1–D8 (grupa 4) → próbki `pop-quality-v1` → hash bazy; różnica → kod 5, nic nie zapisane
    - warstwy próbek: granica POP wewn./zewn. i POP0 wewn./zewn. przy kandydatach D6, braki danych, rozbieżność KWJP–NKJP, grupy homonimów, części mowy, krótkie/długie słowa
  - [x] 6.4 `measure.json`: kanoniczny, `code_identity`, hash `pop-sources.json` i listy opcji, bez czasów i ścieżek; liczby NKJP per forma tylko tu. Czasy (A9, D2c) w osobnym `timing.json`
  - [x] 6.5 `report.md` po polsku
    - TL;DR; tabela na każdą D1–D8: opcja, leksemy, formy STANDARD, pokrycie, przykłady oznaczone „ilustracja”; zalecenie przy każdej
    - D5: top 50 AMBIGUOUS wg F i ich los w każdej opcji (`rok`, `raz`, `dzień`, `lata`/`lato`, `polska`/`polski`)
    - A6 luka potoczna; A9 formy konstrukcji i czas obu reguł; próbki graniczne
  - [x] 6.6 Zapis do stagingu obok celu, potem `export.rename_noreplace`
  - [x] 6.7 Uruchom tylko testy z 6.1

**Acceptance Criteria:**
- 6 testów z 6.1 przechodzi
- skrypt nie pisze poza nowym katalogiem wyjściowym

### Task Group 7: Pomiar na v29 i raport dla właściciela
**Dependencies:** 6
**Files to Modify:** data/work/pop-measure-<stempel>/ (poza gitem), .maister/tasks/development/2026-10-11-slowniki-pop-pop0/analysis/pop-measure-report.md
**Estimated Steps:** 6

- [x] 7.0 Prawdziwy pomiar i pytanie do właściciela (kryteria etapu A)
  - [x] 7.1 Przed: `df` (miejsce na dysku); zapisz hashe `manifest.json`, `lists/`, `reports/` przebiegu i `release-manifest.json` v29
  - [x] 7.2 Dwa przebiegi do dwóch katalogów `data/work/pop-measure-<stempel>-a|b`; `cmp` obu `measure.json`; zapisz czas i RSS
  - [x] 7.3 Hash bazy = pin `85b23ca5…`; hashe z 7.1 bez zmian
  - [x] 7.4 Agent wstępnie ocenia próbki graniczne; ocena w raporcie, osobno od ilustracji
  - [x] 7.5 Kopia raportu do `analysis/pop-measure-report.md` bez liczb NKJP per forma; commit i push repo
  - [x] 7.6 **STOP.** Pytanie do właściciela (B1): dla każdej D1–D8 opcje, liczby, przykłady, zalecenie. Nie zaczynaj grupy 8 bez odpowiedzi

**Acceptance Criteria:**
- dwa `measure.json` równe bajtowo; hash bazy bez zmian
- raport ma tabelę dla każdej D1–D8, pomiar A9 i próbki
- właściciel odpowiedział na D1–D8

### Etap B — decyzje

### Task Group 8: ADR-007 i atrybucja NKJP
**Dependencies:** 7 (i odpowiedź właściciela)
**Files to Modify:** docs/adr/ADR-007-metoda-pop-v1.md, ATTRIBUTIONS.md
**Estimated Steps:** 4

- [x] 8.0 Zapis decyzji (B2, B4)
  - [x] 8.1 Sprawdź, że ADR-007 jest wolny (`docs/adr/`, gałęzie lokalne)
  - [x] 8.2 `docs/adr/ADR-007-metoda-pop-v1.md`: status, data, wybór per D1–D8 z liczbami z raportu A, odrzucone opcje, warunek rewizji, wycofanie NKJP (D3 = sama KWJP), link do `config/generator/pop.json`
  - [x] 8.3 `ATTRIBUTIONS.md`: opis zmian NKJP wg D4 (reguła i jej identyfikator)
  - [x] 8.4 Właściciel akceptuje ADR; status „zaakceptowana” z datą

**Acceptance Criteria:**
- ADR-007 zaakceptowany; `ATTRIBUTIONS.md` zgodny z D4

### Task Group 9: `pop.json` i walidator konfiguracji
**Dependencies:** 8
**Files to Modify:** config/generator/pop.json, literaki_slownik/pop.py, tests/test_pop.py
**Estimated Steps:** 5

- [x] 9.0 Konfiguracja metody `pop-v1` (B3, C3)
  - [x] 9.1 Napisz 6 testów
    - `config/generator/pop.json` z repo przechodzi
    - nieznany klucz → kod 2
    - opcja D spoza zamkniętej listy → kod 2
    - liczba złego typu (`bool`, `float` zamiast `int`) albo spoza zakresu → kod 2
    - D3 = „sama KWJP” zawsze przyjmowane
    - `sampling` inne niż `pop-quality-v1` → kod 2
  - [x] 9.2 `pop.json`: `version: pop-v1`, `adr: ADR-007`, opcje D1–D8, progi, wagi, `sampling`
  - [x] 9.3 `load_config(path)` w `pop.py`: zamknięte listy opcji (te z raportu A), typy przez `type(x) is int`, zakresy
  - [x] 9.4 ADR-007 i `pop.json` wskazują się nawzajem
  - [x] 9.5 Uruchom tylko testy z 9.1

**Acceptance Criteria:**
- 6 testów z 9.1 przechodzi; `pop.json` przechodzi walidator

### Task Group 10: Bramka B5 — spec rew. 3 i plan C
**Dependencies:** 9
**Files to Modify:** .maister/tasks/development/2026-10-11-slowniki-pop-pop0/implementation/spec.md, .maister/tasks/development/2026-10-11-slowniki-pop-pop0/implementation/implementation-plan.md, .maister/tasks/development/2026-10-11-slowniki-pop-pop0/implementation/implementation-plan.html
**Estimated Steps:** 4

- [x] 10.0 Bramka B→C (B5)
  - [x] 10.1 Spec rew. 3: wybrane opcje zamiast list; usunąć niewybrane ścieżki (zostaje D3 = sama KWJP)
  - [x] 10.2 Rozpisz grupy 11–17: kroki, testy, pliki
  - [x] 10.3 Zanotuj `code_identity` z `measure.json`; jeśli kod rankingu zmieni się w C, D-6 wymaga ponownego pomiaru
    - podstawa: `data/work/pop-measure-20261011-154857-b/measure.json`, `tree_sha256` `81a5f82ae66f9457…` (commit `db15d829…`, dirty = kod z 7133fbe)
    - nowy kod `pop` tylko poniżej sekcji konfiguracji `pop.py` (`# --- Konfiguracja metody`)
    - kontrola: `git diff 7133fbe -- literaki_slownik/database.py` puste i `pop.py` do znacznika konfiguracji równy 7133fbe; inaczej ponowny pomiar A (16.2)
  - [x] 10.4 **STOP.** Właściciel zatwierdza spec rew. 3 i plan C. Bez tego grupa 11 nie startuje

**Acceptance Criteria:**
- spec rew. 3 i plan C zatwierdzone przez właściciela

### Etap C — polecenie `pop`

### Task Group 11: Polecenie `pop` — rdzeń
**Dependencies:** 10
**Files to Modify:** literaki_slownik/pop.py, literaki_slownik/cli.py, tests/pop_helpers.py, tests/test_pop.py
**Estimated Steps:** 8

- [x] 11.0 Listy POP i POP0 w pamięci (C1–C10, C14, C15, C19)
  - [x] 11.1 Napisz 8 testów w `tests/test_pop.py`
    - `load_config` zawężone: `d5 = d`, klasy D2, reguła (ii), `d1 = kwjp-all`, inna reguła D4, waga ≠ 0,5, `d6` przez `coverage`, D9 `true`, wycofanie z `d4` ≠ `null` → kod 2; `pop.json` z repo i wycofanie z `d4 = null` przechodzą
    - POP0 ⊆ POP ⊆ STANDARD; `zamek:a/b` wchodzi w całości albo wcale; F grupy nie trafia do członków
    - `Polska` bez rangi i poza progiem; forma `polska` wchodzi przez `polski`
    - brak pełny → `NO_DATA`, poza listami; częściowy → flaga `single_source:<źródło>`; nigdy ranga 0
    - forma konstrukcji wchodzi z leksemem składnika; `ul.` nie skleja się z `ul`
    - brak słowa z `must_include_pop0` w POP0 → kod 4
    - sama KWJP (`d3 = {kwjp, F}`, `d4 = null`): `1grams.gz` nie jest otwierany; wynik bez pól NKJP (C19)
    - hash bazy przed = po; inny hash po (podmieniony `database_sha256`) → kod 5; CLI (subprocess) zły `pop.json` → 2, zły pin → 3, przebieg nie-FROZEN → 5
  - [x] 11.2 `tests/pop_helpers.py`: `pop_config(tmp, pop, pop0)` z małymi progami; NKJP fikstury z `kot` i liczbami o rzadkich ciągach cyfr (np. `7340919`) dla skanu C14; `kot` w POP0 przy progach fikstury
  - [x] 11.3 Zawęź `load_config` (C3): wartości ADR-007 jako stałe w sekcji konfiguracji; D3 = KWJP+NKJP F z wagą 0,5 albo sama KWJP F z `d4 = null`; D6 tylko `count`, POP0 < POP. Odwróć testy grupy 9: „waga 1 w zakresie” i wycofanie z `d4` ≠ `null`
  - [x] 11.4 `build_pop(sources, config, run_dir, release_dir)` pod sekcją konfiguracji
    - `check_inputs` → hash bazy → `read_standard` → `load_lexemes`, `load_kwjp_lists`, `kwjp_measures`, `form_owners`, `load_forms` (reguła (i)), `load_constructions`
    - `read_nkjp(path, d4)` tylko przy KWJP+NKJP
    - `units(kwjp, 'e', relevant, nkjp, owners, eligible=relevant − proper)`; `relevant` = leksemy z formą w STANDARD
    - `measure(result, d3, d8)` → `rank_units` → `threshold` osobno dla `d6.pop` i `d6.pop0`
    - `must_include_pop0` w POP0 (brak → 4) → `forms_for(members, d2, forms, constructions)` → kontrola podzbiorów (→ 4) → hash bazy po (różny → 5)
    - funkcji rankingu nie zmieniać; wzór złożenia: `scripts/measure_pop.py`
  - [x] 11.5 Wynik w pamięci: posortowane klucze POP i POP0; wiersze jednostek (ranga, miara, percentyle KWJP/NKJP, statusy per źródło, flagi, członkowie); raport progów (ranga graniczna, jednostki, leksemy, formy, pokrycie `kwjp-standard` i `kwjp-all`)
  - [x] 11.6 Podkomenda `pop` w `cli.py` (C1): `--manifest`, `--config`, `--run-dir`, `--release-dir`, `--output-dir`, `--json`; leniwy import, `_finish`. W tej grupie liczy i wypisuje podsumowanie; zapis pakietu w grupie 12
  - [x] 11.7 Na v29 (bez zapisu): czas ≤ 10 min (C15); POP = sonda (45 229 jednostek, 1 328 263 formy, 98,5%); `kot` w POP0; wynik i czas do `work-log.md`. Kontrola D-6 z 10.3
  - [x] 11.8 Uruchom tylko testy z 11.1 i odwrócone testy grupy 9

**Acceptance Criteria:**
- 8 testów z 11.1 przechodzi
- `pop` na v29 ≤ 10 min; POP zgodne z sondą; `kot` w POP0
- `pop.py` przed sekcją konfiguracji i `database.py` równe 7133fbe

### Task Group 12: Pakiet POP `BUILT`
**Dependencies:** 11
**Files to Modify:** literaki_slownik/pop.py, literaki_slownik/cli.py, tests/pop_helpers.py, tests/test_pop.py
**Estimated Steps:** 8

- [x] 12.0 Zapis pakietu (C11–C13, C17, C18)
  - [x] 12.1 Napisz 7 testów
    - dwa przebiegi do dwóch katalogów: wszystkie pliki równe bajtowo; gzip: `mtime=0`, pusta nazwa, poziom 9; treść = posortowane `game_key` z `\n`
    - układ: `POP.txt.gz`, `POP0.txt.gz`, `reports/` (4 pliki), `release-manifest.json`, `ATTRIBUTIONS.md`, `LIMITATIONS.md`, `TERMS.md`, `SHA256SUMS`; `SHA256SUMS` obejmuje wszystko poza sobą
    - manifest: `status: BUILT`, hashe wejść (z hashem bazy), `code_identity`, hash `pop.json`, ADR-007, `must_include_pop0`, id reguły NKJP, hashe wyjść; bez czasów i ścieżek bezwzględnych
    - pliki 0444; istniejący `--output-dir` → 4 i bez zmian; błąd w trakcie → brak celu
    - skan pakietu: żadnej liczby NKJP z fikstury (rzadkie ciągi z 11.2) i brak surowego NKJP; klucze `nkjp*` tylko z listy dozwolonej (C14)
    - próbki `pop-quality-v1` z warstwami C17; `review-template.json` `UNREVIEWED`, `canonical_index_sha256` = hash `reports/units.json`
    - `ATTRIBUTIONS.md` z NKJP wg ADR-006 (twórca, URL, „CC BY, wersja nieokreślona”, reguła D4); sama KWJP → bez NKJP w atrybucjach i manifeście (C19); TERMS: CC BY i BSD-2-Clause
  - [x] 12.2 `tests/pop_helpers.py`: `pop_package(tmp)` buduje pakiet fikstury dla grup 13–14
  - [x] 12.3 `_write_gzip(path, keys)`: `gzip.GzipFile(filename='', mtime=0, compresslevel=9)`; `POP.txt.gz`, `POP0.txt.gz`
  - [x] 12.4 `reports/`: `thresholds.json` (C10), `units.json` (rangi, miary, percentyle, statusy, flagi; bez F NKJP), `sample.json` (`quality.sample_strata`, `sampling` z `pop.json`; warstwy: granica POP wewn./zewn., granica POP0 wewn./zewn., braki danych, rozbieżność KWJP–NKJP, grupy homonimów, części mowy, krótkie/długie), `review-template.json` (`quality.review_template`, `evidence_sha256` = hashe list i `thresholds.json`)
  - [x] 12.5 `ATTRIBUTIONS.md`, `LIMITATIONS.md` (punkty E3), `TERMS.md` z `pop-sources.json` i ADR-007 (wzór `verify.py:468-520`)
  - [x] 12.6 `release-manifest.json` (C12) przez `canonical`; potem `SHA256SUMS` (`<sha256>  <ścieżka>`, posortowane)
  - [x] 12.7 Staging obok celu → `export.rename_noreplace`; pliki 0444; cel istnieje → 4. `cli pop` zapisuje pakiet i wypisuje ścieżkę oraz liczby
  - [x] 12.8 Uruchom tylko testy z 12.1

**Acceptance Criteria:**
- 7 testów z 12.1 przechodzi
- pakiet fikstury powtarzalny bajtowo, bez liczb NKJP

### Task Group 13: `explain_pop`
**Dependencies:** 12
**Files to Modify:** literaki_slownik/explain.py, literaki_slownik/cli.py, tests/test_explain_pop.py
**Estimated Steps:** 5

- [x] 13.0 Wyjaśnienie słowa w POP/POP0 (C16)
  - [x] 13.1 Napisz 5 testów w `tests/test_explain_pop.py` (pakiet z `pop_package`)
    - każdy powód: `IN_POP0`, `IN_POP`, `BELOW_THRESHOLD`, `NO_DATA`, `PROPER_NAME_ONLY`, `NOT_IN_STANDARD`
    - wynik: czy w STANDARD, leksemy, per jednostka ranga, miara, statusy, flagi, próg; bez liczb NKJP
    - piny pakietu ≠ run-dir (hash bazy, release-manifest) → kod 3
    - hash bazy przed = po; `decisions.VARIANTS` bez zmian
    - CLI `explain --variant pop0 --pop-dir … --word kot` (tekst i `--json`); `--variant pop` bez `--pop-dir` → kod 2
  - [x] 13.2 `explain_pop(pop_dir, run_dir, word, variant)` w `explain.py`: piny z `release-manifest.json` pakietu; leksemy słowa z bazy ro; wiersze z `reports/units.json` i `thresholds.json`
  - [x] 13.3 Format tekstowy obok `format_explanation`
  - [x] 13.4 CLI: `choices` + `pop`, `pop0`; `--pop-dir`; brak przy POP → 2
  - [x] 13.5 Uruchom tylko testy z 13.1

**Acceptance Criteria:**
- 5 testów z 13.1 przechodzi; `explain` LL-PL bez zmian

### Task Group 14: `scripts/check_pop_package.py`
**Dependencies:** 12
**Files to Modify:** scripts/check_pop_package.py, tests/test_check_pop_package.py
**Estimated Steps:** 6

- [x] 14.0 Niezależna kontrola pakietu i przeglądu (D-3, D-5)
  - [x] 14.1 Napisz 7 testów w `tests/test_check_pop_package.py` (pakiet z `pop_package`)
    - poprawny pakiet → 0
    - zmieniony, brakujący albo dodatkowy plik → 4
    - słowo POP0 spoza POP, słowo POP spoza STANDARD, brak `kot` w POP0 → 4
    - klucz `nkjp*` spoza listy dozwolonej albo plik surowego NKJP → 4
    - przegląd: `UNREVIEWED`, pozycja bez oceny, inny `sample_sha256`, inny hash `SHA256SUMS` → 4; `REVIEWED` kompletny → 0
    - zły argument → 2; hash `--standard` ≠ pin w manifeście → 3
    - skrypt nie importuje `pop` ani `literaki_slownik` (skan AST)
  - [x] 14.2 `SHA256SUMS` i hashe wyjść manifestu; zbiór plików dokładnie jak w `SHA256SUMS`
  - [x] 14.3 Podzbiory na plikach (gzip), `--standard` z pinem, `must_include_pop0` z manifestu
  - [x] 14.4 Skan NKJP: klucze JSON w `reports/`, nazwy plików
  - [x] 14.5 `--review <plik>`: status, każda ocena, `sample_sha256` = hash `reports/sample.json`, hash `SHA256SUMS`. Tylko stdlib; `main()` zwraca kod
  - [x] 14.6 Uruchom tylko testy z 14.1

**Acceptance Criteria:**
- 7 testów z 14.1 przechodzi; skrypt tylko na stdlib

### Task Group 15: Przegląd testów i luki
**Dependencies:** 11, 12, 13, 14
**Files to Modify:** tests/test_pop.py, tests/test_explain_pop.py, tests/test_check_pop_package.py
**Estimated Steps:** 4

- [x] 15.0 Przegląd testów POP
  - [x] 15.1 Przejrzyj testy grup 1–14 (ok. 72)
  - [x] 15.2 Luki tylko dla POP wg tabeli ograniczeń spec i „Kluczowe przypadki” (np. wycofanie NKJP end-to-end, `ul.`/`ul` w pakiecie)
  - [x] 15.3 Dopisz do 10 testów
  - [x] 15.4 Testy POP, potem raz pełny zestaw `python3 -m unittest discover -s tests -p 'test_*.py'`

**Acceptance Criteria:**
- testy POP i pełny zestaw zielone; najwyżej 10 nowych testów

### Etap D — odbiór

### Task Group 16: Odbiór pakietu na v29
**Dependencies:** 15
**Files to Modify:** .maister/tasks/development/2026-10-11-slowniki-pop-pop0/verification/pop-acceptance.md, .maister/tasks/development/2026-10-11-slowniki-pop-pop0/verification/pop-v1-review.json, data/work/pop-v1-<stempel>-a|b/ (poza gitem), data/work/pop-v1-review.json (poza gitem)
**Estimated Steps:** 10

- [x] 16.0 Odbiór D-1…D-7
  - [x] 16.1 `df`; hashe przed: baza, `manifest.json`, `lists/`, `reports/` przebiegu, `release-manifest.json` v29
  - [x] 16.2 D-6: kontrola z 10.3. Kod rankingu zmieniony → ponowny `scripts/measure_pop.py` do nowego katalogu; ten `measure.json` jest podstawą
  - [x] 16.3 Dwa przebiegi `pop` po kolei do `data/work/pop-v1-<stempel>-a` i `-b`; czas i RSS; `diff -r` i `cmp SHA256SUMS` (D-1)
  - [x] 16.4 Hashe z 16.1 po; baza = `85b23ca5…` (D-2)
  - [x] 16.5 `check_pop_package.py --pop-dir …-a --standard <v29>/lists/standard.txt` = 0 (D-3)
  - [x] 16.6 Liczby: POP = sonda (45 229 jednostek, 1 328 263 formy, 98,5% `kwjp-standard`); POP0 zapisane; `kot` w POP0 (ranga ok. 9 128). Rozbieżność → STOP i przyczyna, bez poprawiania liczb
  - [x] 16.7 Agent ocenia każdą pozycję `reports/review-template.json` (ocena, uzasadnienie, `reviewer: agent`) → szkic `data/work/pop-v1-review.json`; podsumowanie per warstwa dla właściciela
  - [x] 16.8 **STOP.** Właściciel zatwierdza przegląd; wtedy status `REVIEWED`. Bez tego brak grupy 17 (D-4)
  - [x] 16.9 `check_pop_package.py --review data/work/pop-v1-review.json` = 0 (D-5); kopia do `verification/pop-v1-review.json`
  - [x] 16.10 `verification/pop-acceptance.md` (D-7): hashe, liczby, `code_identity`, wynik przeglądu, wyjście D-3/D-5; commit i push repo

**Acceptance Criteria:**
- D-1…D-7 spełnione; właściciel zatwierdził przegląd

### Etap E — wydanie i wiki

### Task Group 17: Wydanie `pop-v1`, dokumenty i wiki
**Dependencies:** 16
**Files to Modify:** docs/generator/cli.md, docs/generator/jakosc.md, docs/runbook-wiki.md, docs/plan-dalszych-prac-runbook.md, ../wiki-literaki-slownik/Slownik-POP.md, ../wiki-literaki-slownik/Slownik-POP0.md, ../wiki-literaki-slownik/Home.md, ../wiki-literaki-slownik/_Sidebar.md, ../wiki-literaki-slownik/Slownik-STANDARD.md, ../wiki-literaki-slownik/Historia-zmian.md
**Estimated Steps:** 7

- [x] 17.0 Wydanie i dokumentacja (E1–E6)
  - [x] 17.1 Tuż przed wydaniem `check_pop_package.py --pop-dir … --standard … --review …` = 0; inaczej brak wydania (E1)
  - [x] 17.2 `gh release create pop-v1` wg wzoru `llpl-v29`: `POP.txt.gz`, `POP0.txt.gz`, `pop-v1-pakiet.tar.gz`, `SHA256SUMS`, `pop-v1-review.json`. Notatka: liczby z `reports/thresholds.json`, hashe, podstawa `llpl-v29`, ADR-007, ograniczenia, atrybucja NKJP wg ADR-006 (E1–E3)
  - [x] 17.3 Dokumenty (E5): `cli.md` (`pop`, `explain --variant pop|pop0 --pop-dir`), `jakosc.md` (`pop-quality-v1`), `runbook-wiki.md` (strony POP/POP0, skąd liczby), `plan-dalszych-prac-runbook.md` (l. 45: komenda `pop`; l. 51: bez „NKJP BLOCKED”, odesłanie do ADR-006/007)
  - [x] 17.4 Wiki wg `docs/runbook-wiki.md`: `git -C ~/Projects/Literaki/wiki-literaki-slownik pull --ff-only`; `Slownik-POP` i `Slownik-POP0`: zamiast „**W przygotowaniu.**” stan (słowa, leksemy, `pop-v1`, link do Release, sha256), tabela filtrów z przykładem słowa, link do ADR-007; bez tez o znajomości słów
  - [x] 17.5 Usuń „w przygotowaniu” z `Home` (wiersze POP/POP0: liczba i link), `_Sidebar`, `Slownik-STANDARD`; wiersz w `Historia-zmian`. W tabelach `[POP](Slownik-POP)`, nie `[[a|b]]`. `grep -ri przygotowaniu` w wiki = pusto
  - [x] 17.6 `curl -fIL` na każdy asset Release i każdą zmienioną stronę wiki → 200 (E6)
  - [x] 17.7 Commit i push repo `literaki-slownik` oraz wiki

**Acceptance Criteria:**
- Release `pop-v1` po D-5; wiki bez „w przygotowaniu”, wypchnięte; E6 zielone

## Execution Order

1. Grupa 1: Manifest i piny (5 kroków) — zrobione
2. Grupa 5: `pop-quality-v1` (3 kroki) — zrobione
3. Grupy 2, 3, 4: KWJP/SGJP, NKJP, rangi (7, 6, 7 kroków) — zrobione
4. Grupa 6: Skrypt pomiaru (7 kroków) — zrobione
5. Grupa 7: Pomiar na v29 (6 kroków) — zrobione
6. Grupy 8, 9: ADR-007, `pop.json` (4, 5 kroków) — zrobione
7. Grupa 10: Bramka B5 (4 kroki, po 9) — **STOP: właściciel (10.4)**
8. Grupa 11: `pop` rdzeń (8 kroków, po 10)
9. Grupa 12: Pakiet (8 kroków, po 11)
10. Grupy 13 i 14 równolegle (5 i 6 kroków, po 12; wspólnych plików brak)
11. Grupa 15: Przegląd testów (4 kroki, po 11–14)
12. Grupa 16: Odbiór na v29 (10 kroków, po 15) — **STOP: przegląd właściciela (16.8)**
13. Grupa 17: Wydanie i wiki (7 kroków, po 16)

## Standards Compliance

Zgodnie z `.maister/docs/INDEX.md` i `docs/`:
- `AGENTS.md`: po polsku, zwięźle; decyzje o składzie słownika z właścicielem (D1–D9 delegowane, ADR-007); wiki w tej samej pracy
- `docs/literaki-niezalezne-slowniki-prompt-v3.md` §2.1, §2.2, §8.1, §8.2, §9.1, §9.4, §13
- `docs/adr/ADR-006-nkjp-cc-by-bez-wersji.md`: atrybucja, bez surowego NKJP, wycofanie NKJP
- `docs/adr/ADR-007-metoda-pop-v1.md`: tylko metoda `pop-v1`; zmiana = nowa wersja
- `docs/generator/jakosc.md` (kontrakt próbek), `docs/generator/publikacja.md` (licencje, układ pakietu), `docs/runbook-wiki.md`
- `docs/literaki-prosty-jezyk-minimum-leksykalne-kierunki.md` §4–5: bez list zewnętrznych

## Notes

- Test najpierw: każda grupa z kodem zaczyna od 2–8 testów.
- Po grupie uruchamiaj tylko jej testy. Pełny zestaw raz, w grupie 15.
- Zaznaczaj kroki po wykonaniu.
- Najpierw ponowne użycie: funkcje `pop.py` z grup 1–4 i 9, złożenie z `scripts/measure_pop.py`, `quality.sample_strata`/`review_template`, `canonical`, `export.rename_noreplace`, `run.code_identity`, wzór `verify.py:468-520`, fikstury `tests/pop_helpers.py`.
- Bramki właściciela (10.4, 16.8) zatrzymują wykonawcę.
