# Plan implementacji: słowniki POP i POP0 (#3)

Podstawa: `implementation/spec.md` (rew. 2), `verification/spec-audit.md`.

## TL;DR
- 17 grup, 90 kroków. Etapy A (grupy 1–7) i B (8–10) są rozpisane w całości. C, D i E (11–17) to zarys, **do doprecyzowania po B5**.
- Kolejność: piny → ładowanie KWJP/SGJP → NKJP → rangi i opcje → skrypt pomiaru → pomiar na v29 → **STOP: właściciel** → ADR-007 → `pop.json` → **STOP: bramka B5** → C → D (**STOP: przegląd**) → E.
- Równolegle: grupa 5 (`quality.py`) z grupami 1–4; grupy 13 i 14 po 12. Reszta jest szeregowa, bo dzieli `pop.py` i `tests/test_pop.py`.
- Testy: 2–8 na grupę z kodem, razem ok. 55–78.

## Key Decisions
- Kod ładowania danych, rang i opcji jest w `literaki_slownik/pop.py`. Skrypt pomiaru go importuje, więc A i C liczą tym samym kodem (D-6).
- Czasy reguł przynależności (A9) trafiają do osobnego `timing.json`. `measure.json` jest bez czasów, więc dwa przebiegi dają te same bajty (A3).
- Testy `pop-quality-v1` są w nowym pliku `tests/test_pop_quality.py`. `tests/test_quality.py` zostaje bez zmian.
- Fikstura POP (`tests/pop_helpers.py`) ma własne SGJP. `release_helpers.SGJP` i testy LL-PL się nie zmieniają.
- Grupy bez kodu (7, 8, 10, 16, 17) nie mają testów. Zamiast nich mają kontrole: hashe, `cmp`, `curl -fI`.

## Open Questions / Risks
- Bramki właściciela: po grupie 7 (D1–D8), po grupie 10 (B5) i w grupie 16 (przegląd). Wykonawca **zatrzymuje się** w każdej i nie zaczyna następnej grupy bez odpowiedzi.
- Grupy 11–17 zależą od wyborów D1–D8. Ich kroki i testy przepisze grupa 10.
- Liczby z audytu (14 s odczytu, 350 MB, 14 s hasha) mogły się zestarzeć. Grupa 7 mierzy je od nowa.
- Druga reguła przynależności (D2c) czyta `analysis` (17,5 mln) i `variant_decision` (35 mln). Czas nieznany do grupy 7.
- Grupy 2–4 dzielą `pop.py`, więc idą po kolei. To wydłuża etap A.
- Nowy `pop.py` i zmiana `quality.py` zmieniają `code_identity`. Ma to znaczenie tylko dla przyszłej weryfikacji LL-PL.

## Overview
Total Steps: 90
Task Groups: 17 (A: 1–7, B: 8–10, C: 11–15, D: 16, E: 17)
Expected Tests: ok. 55–78 (A+B: 42, C: do 26, przegląd: do 10)

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

- [ ] 8.0 Zapis decyzji (B2, B4)
  - [ ] 8.1 Sprawdź, że ADR-007 jest wolny (`docs/adr/`, gałęzie lokalne)
  - [ ] 8.2 `docs/adr/ADR-007-metoda-pop-v1.md`: status, data, wybór per D1–D8 z liczbami z raportu A, odrzucone opcje, warunek rewizji, wycofanie NKJP (D3 = sama KWJP), link do `config/generator/pop.json`
  - [ ] 8.3 `ATTRIBUTIONS.md`: opis zmian NKJP wg D4 (reguła i jej identyfikator)
  - [ ] 8.4 Właściciel akceptuje ADR; status „zaakceptowana” z datą

**Acceptance Criteria:**
- ADR-007 zaakceptowany; `ATTRIBUTIONS.md` zgodny z D4

### Task Group 9: `pop.json` i walidator konfiguracji
**Dependencies:** 8
**Files to Modify:** config/generator/pop.json, literaki_slownik/pop.py, tests/test_pop.py
**Estimated Steps:** 5

- [ ] 9.0 Konfiguracja metody `pop-v1` (B3, C3)
  - [ ] 9.1 Napisz 6 testów
    - `config/generator/pop.json` z repo przechodzi
    - nieznany klucz → kod 2
    - opcja D spoza zamkniętej listy → kod 2
    - liczba złego typu (`bool`, `float` zamiast `int`) albo spoza zakresu → kod 2
    - D3 = „sama KWJP” zawsze przyjmowane
    - `sampling` inne niż `pop-quality-v1` → kod 2
  - [ ] 9.2 `pop.json`: `version: pop-v1`, `adr: ADR-007`, opcje D1–D8, progi, wagi, `sampling`
  - [ ] 9.3 `load_config(path)` w `pop.py`: zamknięte listy opcji (te z raportu A), typy przez `type(x) is int`, zakresy
  - [ ] 9.4 ADR-007 i `pop.json` wskazują się nawzajem
  - [ ] 9.5 Uruchom tylko testy z 9.1

**Acceptance Criteria:**
- 6 testów z 9.1 przechodzi; `pop.json` przechodzi walidator

### Task Group 10: Bramka B5 — spec rew. 3 i plan C
**Dependencies:** 9
**Files to Modify:** .maister/tasks/development/2026-10-11-slowniki-pop-pop0/implementation/spec.md, .maister/tasks/development/2026-10-11-slowniki-pop-pop0/implementation/implementation-plan.md, .maister/tasks/development/2026-10-11-slowniki-pop-pop0/implementation/implementation-plan.html
**Estimated Steps:** 4

- [ ] 10.0 Bramka B→C (B5)
  - [ ] 10.1 Spec rew. 3: wybrane opcje zamiast list; usunąć niewybrane ścieżki (zostaje D3 = sama KWJP)
  - [ ] 10.2 Rozpisz grupy 11–17: kroki, testy, pliki
  - [ ] 10.3 Zanotuj `code_identity` z `measure.json`; jeśli kod rankingu zmieni się w C, D-6 wymaga ponownego pomiaru
  - [ ] 10.4 **STOP.** Właściciel zatwierdza spec rew. 3 i plan C. Bez tego grupa 11 nie startuje

**Acceptance Criteria:**
- spec rew. 3 i plan C zatwierdzone przez właściciela

### Etap C — polecenie `pop` (do doprecyzowania po B5)

### Task Group 11: Polecenie `pop` — rdzeń
**Dependencies:** 10
**Files to Modify:** literaki_slownik/pop.py, literaki_slownik/cli.py, tests/test_pop.py
**Estimated Steps:** 5

- [ ] 11.0 Budowa list POP i POP0 (C1–C10, C14, C15)
  - [ ] 11.1 Napisz do 8 testów: POP0 ⊆ POP ⊆ STANDARD; naruszenie → 4; D5 bez kopiowania F; brak ≠ 0 (statusy KWJP/NKJP); forma konstrukcji z leksemem składnika; hash bazy po ≠ przed → 5 i pusty `--output-dir`; CLI kody 2/3/4/5 (subprocess)
  - [ ] 11.2 `build_pop(...)`: przepływ ze spec na funkcjach grup 1–4 i `load_config`
  - [ ] 11.3 Podkomenda `pop` w `cli.py`: leniwy import, `_finish`, `--json`
  - [ ] 11.4 Czas na v29 ≤ 10 min (C15)
  - [ ] 11.5 Uruchom tylko testy z 11.1

**Acceptance Criteria:**
- testy z 11.1 przechodzą; `pop` na v29 ≤ 10 min

### Task Group 12: Pakiet POP
**Dependencies:** 11
**Files to Modify:** literaki_slownik/pop.py, tests/test_pop.py
**Estimated Steps:** 6

- [ ] 12.0 Pakiet `BUILT` (C11–C13, C17, C18)
  - [ ] 12.1 Napisz do 7 testów: dwa przebiegi równe bajtowo (z gzip); gzip `mtime=0`, pusta nazwa, poziom 9; manifest `status: BUILT`, bez czasów i ścieżek bezwzględnych; pliki 0444, istniejący katalog → 4; skan pakietu bez liczb NKJP (C14); próbki `pop-quality-v1` i `review_template` z hashem raportu rang; `ATTRIBUTIONS.md`/`LIMITATIONS.md`/`TERMS.md` obecne
  - [ ] 12.2 `POP.txt.gz`, `POP0.txt.gz`, `reports/` (pokrycie, rangi, wrażliwość wag, próbki, szablon przeglądu), `SHA256SUMS`
  - [ ] 12.3 `release-manifest.json` (C12)
  - [ ] 12.4 Trzy pliki md z `pop-sources.json` i ADR-007 (wzór `verify.py:468-520`)
  - [ ] 12.5 Staging + `export.rename_noreplace`, pliki 0444
  - [ ] 12.6 Uruchom tylko testy z 12.1

**Acceptance Criteria:**
- testy z 12.1 przechodzą

### Task Group 13: `explain_pop`
**Dependencies:** 12
**Files to Modify:** literaki_slownik/explain.py, literaki_slownik/cli.py, tests/test_explain_pop.py
**Estimated Steps:** 4

- [ ] 13.0 Wyjaśnienie słowa w POP/POP0 (C16)
  - [ ] 13.1 Napisz 5 testów: powody `IN_POP0`, `IN_POP`, `BELOW_THRESHOLD`, `NO_DATA`, `FORM_NOT_TYPICAL`, `NOT_IN_STANDARD`; piny pakietu ≠ run-dir → 3; brak liczb NKJP w wyniku; `decisions.VARIANTS` bez zmian; CLI `--variant pop|pop0 --pop-dir`
  - [ ] 13.2 `explain_pop(...)` obok `explain`
  - [ ] 13.3 CLI: `choices` rozszerzone, `--pop-dir`
  - [ ] 13.4 Uruchom tylko testy z 13.1

**Acceptance Criteria:**
- testy z 13.1 przechodzą

### Task Group 14: `scripts/check_pop_package.py`
**Dependencies:** 12
**Files to Modify:** scripts/check_pop_package.py, tests/test_check_pop_package.py
**Estimated Steps:** 3

- [ ] 14.0 Niezależna kontrola pakietu i przeglądu (D-3, D-5)
  - [ ] 14.1 Napisz 6 testów: poprawny pakiet → 0; zmieniony plik → 4; naruszenie podzbiorów → 4; liczba NKJP w pakiecie → 4; przegląd `UNREVIEWED`, pozycja bez oceny, inny `sample_sha256` albo inny hash `SHA256SUMS` → 4; skrypt nie importuje `pop.py`
  - [ ] 14.2 Skrypt tylko na stdlib
  - [ ] 14.3 Uruchom tylko testy z 14.1

**Acceptance Criteria:**
- testy z 14.1 przechodzą

### Task Group 15: Przegląd testów i luki
**Dependencies:** 11, 12, 13, 14
**Files to Modify:** tests/test_pop.py, tests/test_measure_pop.py, tests/test_explain_pop.py, tests/test_check_pop_package.py
**Estimated Steps:** 4

- [ ] 15.0 Przegląd testów POP
  - [ ] 15.1 Przejrzyj testy grup 1–14 (ok. 58–68)
  - [ ] 15.2 Znajdź luki tylko dla POP (tabela ograniczeń spec)
  - [ ] 15.3 Dopisz do 10 testów
  - [ ] 15.4 Testy POP, potem raz pełny zestaw `python3 -m unittest discover -s tests -p 'test_*.py'`

**Acceptance Criteria:**
- testy POP i pełny zestaw zielone; najwyżej 10 nowych testów

### Etap D — odbiór (do doprecyzowania po B5)

### Task Group 16: Odbiór pakietu
**Dependencies:** 15
**Files to Modify:** .maister/tasks/development/2026-10-11-slowniki-pop-pop0/verification/pop-acceptance.md, data/work/pop-v1-*/ (poza gitem)
**Estimated Steps:** 8

- [ ] 16.0 Odbiór D-1…D-7
  - [ ] 16.1 Hashe bazy, `manifest.json`, `lists/`, `reports/` przebiegu i release-manifest v29 przed
  - [ ] 16.2 Dwa przebiegi `pop` do dwóch katalogów; wszystkie pliki równe bajtowo (D-1)
  - [ ] 16.3 Hashe z 16.1 po; baza = `85b23ca5…` (D-2)
  - [ ] 16.4 `check_pop_package.py --pop-dir` = 0 (D-3)
  - [ ] 16.5 Liczby pakietu = raport A; inny `code_identity` → najpierw ponowny pomiar A (D-6)
  - [ ] 16.6 Agent ocenia każdą pozycję próbki → `pop-v1-review.json`. **STOP:** właściciel zatwierdza, status `REVIEWED` (D-4)
  - [ ] 16.7 `check_pop_package.py --review` = 0 (D-5)
  - [ ] 16.8 `verification/pop-acceptance.md`: hashe, liczby, przegląd, D-3/D-5 (D-7)

**Acceptance Criteria:**
- D-1…D-7 spełnione; właściciel zatwierdził przegląd

### Etap E — wydanie i wiki (do doprecyzowania po B5)

### Task Group 17: Wydanie `pop-v1` i wiki
**Dependencies:** 16
**Files to Modify:** docs/generator/cli.md, docs/generator/jakosc.md, docs/runbook-wiki.md, docs/plan-dalszych-prac-runbook.md, wiki: Slownik-POP, Slownik-POP0, Home, _Sidebar, Slownik-STANDARD, Historia-zmian
**Estimated Steps:** 6

- [ ] 17.0 Wydanie i dokumentacja (E1–E6)
  - [ ] 17.1 Tuż przed wydaniem `check_pop_package.py --review` = 0; inaczej brak wydania
  - [ ] 17.2 `gh release create pop-v1`: pliki C11, osobny asset `pop-v1-review.json`; notatka: liczby, hashe, LL-PL v29, ADR-007, ograniczenia, atrybucja NKJP (E1–E3)
  - [ ] 17.3 Dokumenty (E5): `cli.md`, `jakosc.md`, `runbook-wiki.md`, `plan-dalszych-prac-runbook.md:51` bez „NKJP BLOCKED”
  - [ ] 17.4 Wiki wg `docs/runbook-wiki.md` (E4): liczby z pakietu, metoda z ADR-007, link do Release; bez „W przygotowaniu”; wiersz w `Historia-zmian`; bez tez o znajomości słów
  - [ ] 17.5 `curl -fI` na każdy asset i stronę wiki → 200 (E6)
  - [ ] 17.6 Commit i push repo oraz wiki

**Acceptance Criteria:**
- Release `pop-v1` po D-5; wiki wypchnięte; E6 zielone

## Execution Order

1. Grupa 1: Manifest i piny (5 kroków)
2. Grupa 5: `pop-quality-v1` (3 kroki; równolegle z 1–4)
3. Grupa 2: KWJP i SGJP (7 kroków, po 1)
4. Grupa 3: NKJP (6 kroków, po 1; po 2, bo ten sam plik)
5. Grupa 4: Rangi i opcje (7 kroków, po 2, 3)
6. Grupa 6: Skrypt pomiaru (7 kroków, po 4, 5)
7. Grupa 7: Pomiar na v29 (6 kroków, po 6) — **STOP: właściciel D1–D8**
8. Grupa 8: ADR-007 (4 kroki, po 7)
9. Grupa 9: `pop.json` (5 kroków, po 8)
10. Grupa 10: Bramka B5 (4 kroki, po 9) — **STOP: właściciel**
11. Grupa 11: `pop` rdzeń (5 kroków, po 10)
12. Grupa 12: Pakiet (6 kroków, po 11)
13. Grupy 13 i 14 równolegle (4 i 3 kroki, po 12)
14. Grupa 15: Przegląd testów (4 kroki, po 11–14)
15. Grupa 16: Odbiór (8 kroków, po 15) — **STOP: przegląd właściciela**
16. Grupa 17: Wydanie i wiki (6 kroków, po 16)

## Standards Compliance

Zgodnie z `.maister/docs/INDEX.md` i `docs/`:
- `AGENTS.md`: po polsku, zwięźle; decyzje o składzie słownika z właścicielem; wiki w tej samej pracy
- `docs/literaki-niezalezne-slowniki-prompt-v3.md` §2.1, §2.2, §8.1, §8.2, §9.1, §9.4, §13
- `docs/adr/ADR-006-nkjp-cc-by-bez-wersji.md`: atrybucja, bez surowego NKJP, wycofanie NKJP
- `docs/generator/jakosc.md` (kontrakt próbek), `docs/generator/publikacja.md` (licencje, układ pakietu), `docs/runbook-wiki.md`
- `docs/literaki-prosty-jezyk-minimum-leksykalne-kierunki.md` §4–5: bez list zewnętrznych

## Notes

- Test najpierw: każda grupa z kodem zaczyna od 2–8 testów.
- Po grupie uruchamiaj tylko jej testy. Pełny zestaw raz, w grupie 15.
- Zaznaczaj kroki po wykonaniu.
- Najpierw ponowne użycie: `canonical`, `inputs.checked_file`, `export.rename_noreplace`, `quality.sample_strata`/`review_template`, `run.code_identity`, `kwjp.METRICS`, parser z `scripts/audit_nkjp.py`, fikstury `tests/release_helpers.py`.
- Bramki właściciela (grupy 7, 10, 16) zatrzymują wykonawcę. Etap C nie startuje przed B5.
