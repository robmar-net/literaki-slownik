# Analiza kodu: słowniki POP i POP0

**Data**: 2026-10-11
**Zadanie**: robmar-net/literaki-slownik#3. Dwa słowniki popularnych słów.
**Opis**: POP (szeroki; kandydat na słownik gry bez nieznanych słów i na słownik botów) i POP0 (o rząd wielkości mniejszy, dla słabszych botów). Oba to podzbiory STANDARD z wydania LL-PL v29 (zamrożony przebieg `data/work/lists-v30-20261010-165826-a`). Źródła: frekwencja KWJP i 1-gramy NKJP (ADR-006). Najpierw pomiary i decyzje właściciela, potem kod.
**Analizator**: codebase-analyzer (3 agenty Explore: odkrywanie plików + analiza kodu, kontekst, wzorce)

---

## TL;DR

- Kodu popularności nie ma. POP to **nowy krok pochodny**, tylko do odczytu, nad zamrożonym przebiegiem v29.
- Wejście LL-PL (`sources.json`, `inputs.py`) zostaje bez zmian. POP dostaje własny manifest i własny katalog wyjściowy.
- Dane są gotowe: KWJP już w `build.sqlite` (powiązania z leksemami i formami), NKJP to 1 plik gz (5,36 mln wierszy).
- Wzorzec: `scripts/benchmark_sjp.py` (przepływ danych) + `canonical`, `inputs.checked_file`, `export.rename_noreplace`, `quality.sample_strata` (rygor).
- Blokuje nas 6 decyzji właściciela (jednostka, miara, progi, czyszczenie NKJP, potoczność, użycie w grze). Bez nich nie ma specyfikacji.

## Kluczowe decyzje

| Decyzja | Uzasadnienie |
|---|---|
| Nowy moduł `literaki_slownik/pop.py` i podkomenda CLI `pop` | Wzorzec CLI już jest (5 podkomend, leniwy import, kody wyjścia). |
| Własny manifest, np. `config/generator/pop-sources.json` | `inputs.py` wymaga dokładnie 14 artefaktów LL-PL. Dodanie NKJP zmieniłoby tożsamość LL-PL. |
| Bazę wskazują hashe zamrożonego przebiegu, nie `inspect_sources()` | Bieżący `sources.json` (c4bafe…86) różni się od wejścia przebiegu (26e407…7d, git 415e087). |
| STANDARD czytamy z `lists/standard.txt`, sprawdzony hashem | Plik jest bajtowo równy `LL-PL-STANDARD.txt` (3 090 194 słów). Sortowanie w Pythonie, nie w SQLite. |
| Baza tylko `mode=ro` (opcjonalnie `immutable=1`) | DELETE journal; tabele tymczasowe trafiają do bazy temp. `explain` już tak robi. |
| Wynik w nowym katalogu, nigdy w przebiegu | `lists/` i `reports/` przebiegu są nadal zapisywalne. Zapis tam łamie pieczęć. |
| KWJP: jedno zapytanie strumieniowe na `source_id` | 360–420 tys. wierszy na źródło, tanio. Zapytanie na słowo to antywzorzec. |
| Raporty kanoniczne (`canonical.write_json`), bez czasów i ścieżek | Dwa przebiegi muszą dać te same bajty. |
| Testy LL-PL zostają bez zmian | 5 testów oczekuje NKJP w `unavailable`. |

## Otwarte pytania i ryzyka

**Do decyzji właściciela (przed specyfikacją):**

| # | Pytanie | Co mówi dokumentacja |
|---|---|---|
| Q1 | Jednostka: leksem, forma czy hybryda? | Spec v3 §9.1–9.3. Leksem daje wszystkie formy. Raportować liczbę leksemów i form. |
| Q2 | Miara popularności i wagi | §9.4: rangi, percentyle, logi. Nie sumować surowych ARF/1-DP. Wagi uzasadnić. Analiza wrażliwości. |
| Q3 | Rozmiar POP i POP0 | Punkty startowe 5k/10k/20k/40k/80k leksemów, „do oceny". POP0 ≈ POP/10. |
| Q4 | Reguła czyszczenia NKJP | **Sprzeczność**: `nkjp-audit.md` mówi „łącz po pełnym ciągu NFC, nie usuwaj interpunkcji". ADR-006 i ATTRIBUTIONS mówią „interpunkcja usunięta". Usuwanie scala liczby (`kot.` → `kot`). Potrzebna wersjonowana reguła. |
| Q5 | Potoczność | KWJP nie ma mowy ani mediów społecznościowych. NKJP częściowo to wyrównuje. Czy to wystarczy? |
| Q6 | Użycie w grze | POP jako słownik gry „bez nieznanych słów"? Wtedy brak w POP odrzuca ruch. To decyzja o regułach. |
| Q7 | Homonimy w KWJP | 12 453 lematów ma kilku kandydatów (zamek, rok). Czy przypisać F wszystkim, żadnemu, czy oznaczyć? Spec zabrania dzielenia i kopiowania F. |

**Ryzyka:**

- Brak ≠ 0. Słowo bez danych ma status (np. `ABSENT_OR_BELOW_PUBLICATION_THRESHOLD`), nie zero. POP0 musi zdefiniować to jawnie.
- KWJP dzieli `czytałem` na `czytał`+`em`. Listy form nie mają takich form. Poziom form zaniża ich popularność.
- NKJP: brak POS i lematu, małe litery (scala nazwy własne i pospolite), nieznany ekstraktor i wersja. Nie jest niezależnym dowodem od KWJP.
- `quality.py` przyjmuje tylko `quality-v1`. Próbki graniczne POP potrzebują własnej konfiguracji i walidatora.
- Nowy plik `.py` zmienia `code_identity` (tree_sha256). Ma to znaczenie tylko dla przyszłej weryfikacji LL-PL.
- Hash bazy 22 GB trwa minuty. Lepiej jako osobna flaga, nie domyślnie.
- Nieaktualne wzmianki „NKJP BLOCKED": `docs/plan-dalszych-prac-runbook.md:51`, `sources.json` `unavailable`, `tests/helpers.py`. Poprawiać tylko w ramach POP lub przy następnym LL-PL.
- Wiki: `README.md:21` i `docs/runbook-wiki.md:28` wymagają nowych stron o słownikach popularnych.

---

## Podsumowanie

Repo buduje i zamraża słowniki dopuszczalności (LL-PL). Słowników znajomości nie ma. Wszystkie potrzebne dane leżą w zamrożonej bazie v29 (KWJP z powiązaniami) i w `cache/nkjp/1grams.gz`. Zadanie to nowy, deterministyczny krok tylko do odczytu, z własnym manifestem, zamrożeniem i atrybucją.

---

## Pliki

### Główne

| Plik | Linie | Rola dla POP |
|---|---|---|
| `literaki_slownik/links.py` | 415 | Powiązania KWJP → leksem/forma. `word_availability` (351–415): statusy dostępności. Kierunek złączenia: linia 358. |
| `literaki_slownik/database.py` | 26 | `connect(readonly=True)`: `mode=ro`, cache 64 MB, funkcje SQL `nfc()`, `game_key()`. |
| `literaki_slownik/kwjp.py` | 48 | `rows(path, kind)`, `METRICS` (freq, ipm, ARF, DP, DP_norm, 1-DP, total_freq). |
| `literaki_slownik/export.py` | 174 | Zamrożenie: `rename_noreplace`, pliki 0444, `changes_since_verify`. Wzór dla wydania POP. |
| `literaki_slownik/canonical.py` | 44 | `dumps`, `load_json` (odrzuca duplikaty kluczy i NaN), `sha256`, atomowy `write_json`. |
| `literaki_slownik/inputs.py` | 107 | `GeneratorError(message, code, source, row)`, `checked_file`. LL-PL wymaga 14 artefaktów: nie ruszać. |
| `literaki_slownik/quality.py` | 337 | `sample_strata`: próbki deterministyczne (seed, 30). Konfiguracja przypięta do `quality-v1`. |
| `literaki_slownik/cli.py` | 90 | 5 podkomend, kody wyjścia 2/3/4/5, `--json`. Tu dojdzie `pop`. |
| `scripts/benchmark_sjp.py` | 206 | Najlepszy szablon pomiaru nad zamrożonym przebiegiem. |
| `docs/adr/ADR-006-nkjp-cc-by-bez-wersji.md` | 28 | Licencja NKJP, tylko `1grams.gz`, tylko POP/POP0, bez redystrybucji surowych danych. |

### Pomocnicze

| Plik | Linie | Związek |
|---|---|---|
| `literaki_slownik/explain.py` | 276 | Czyta przebiegi FROZEN tylko do odczytu. Wzór dostępu. |
| `literaki_slownik/decisions.py` | 439 | `nonfiction_frequencies` (19–35): KWJP orth fakt+publicystyka. Do ponownego użycia. |
| `literaki_slownik/run.py` | 63 | `code_identity`, `now()`, `create_run` (kod 4), `set_stage` blokuje VERIFIED/FROZEN (kod 5). |
| `literaki_slownik/reports.py` | 554 | `canonical_index` (79): jawna lista plików → {sha256, bytes}. |
| `literaki_slownik/verify.py` | 638 | Pieczęć (579–631). |
| `literaki_slownik/build.py` | 233 | Etapy budowy LL-PL. Tylko kontekst. |
| `literaki_slownik/schema.sql` | – | Indeks `evidence_unit(unit_1, unit_2, pos)` (38). |
| `config/generator/sources.json` | – | Manifest LL-PL. NKJP w `unavailable`. Nie zmieniać. |
| `ATTRIBUTIONS.md` | – | Tekst atrybucji NKJP (61–73). |
| `scripts/audit_nkjp.py`, `scripts/audit_kwjp.py` | – | Parsowanie NKJP (`r" *([0-9]+) (.+)\n"`) i KWJP. |
| `docs/literaki-niezalezne-slowniki-prompt-v3.md` | – | Wymagania: §2.1, §7.3–7.4, §8, §9.1–9.5. |
| `docs/literaki-prosty-jezyk-minimum-leksykalne-kierunki.md` | – | Zakazane zasoby i pomysły metodologiczne (§4). |
| `docs/plan-dalszych-prac-runbook.md` | – | §4.B, §4.D. Linia 51 nieaktualna. |

---

## Obecny stan

### Baza (zamrożony przebieg v29)

| Element | Wartość |
|---|---|
| Przebieg | `data/work/lists-v30-20261010-165826-a`, kod 105a99b (czysty) |
| `build.sqlite` | 22 GB, `journal_mode=delete`, `database_sha256` 85b23ca5…8c |
| Wydanie | `data/work/release-LL-PL-v29/`, `release-manifest.json` sha 54705743… |
| STANDARD | 3 090 194 słów, sha a432c7c5… |
| BROAD | 3 479 364 słów |
| Manifest wejścia przebiegu | 26e407…7d (git 415e087), ≠ bieżący c4bafe…86 |

### Tabele potrzebne POP

| Tabela | Wiersze | Uwagi |
|---|---|---|
| `corpus_evidence` | 5 066 341 | KWJP; indeks `evidence_unit`, autoindeks `UNIQUE(source_id,row_number)`. Brak indeksu po freq. |
| `evidence_link` | – | metoda, status (UNMATCHED/AMBIGUOUS/EXACT_CANDIDATE), `sense_identity_confirmed=0`. |
| `evidence_candidate` | – | dokładnie jedno z: `lexeme_id`, `form_id`, `candidate_key`. |
| `interpretation` | – | form_id → lexeme_id, tag. |
| `surface_form` | – | `original`, `nfc`, `game_key`, `length`. |
| `lexeme` | – | `lemma_id`, `lemma_base`. |
| `variant_decision` | 35 080 090 | Nie potrzebna do POP. |

### Źródła frekwencji

| Źródło | Wiersze | Uwagi |
|---|---|---|
| KWJP lemma (all/fakt/fikcja/publ.) | 184 917 / 164 651 / 134 453 / 157 968 | (lemat, POS), 39 POS; suma all ≈ 81,7 mln |
| KWJP orth | 419 961 / 384 453 / 331 568 / 366 287 | forma z wielkością liter |
| KWJP orth_lc | 360 472 / 331 932 / 287 133 / 315 420 | forma małymi literami |
| NKJP 1grams.gz | 5 364 398 | suma 246 153 378; F=1: 2 989 804; tylko alfabet PL: 1 368 033; z interpunkcją: 3 892 305 |

KWJP: próg `total_freq ≥ 5` na liście „all”. Listy gatunkowe mają F=1–4: nie filtrować ponownie. Brak w gatunku ≠ 0. Korpus 2011–2020: fikcja 30%, fakt 35%, publicystyka 35%.

Mapowanie lematów KWJP: 108 854 jednoznacznych, 12 453 wieloznacznych, 63 610 bez dopasowania.

### Przepływ danych (proponowany)

```
release-manifest v29 + lists/standard.txt (hash) ──┐
build.sqlite (ro) ─ KWJP per source_id ────────────┼─> agregacja po game_key / leksemie
cache/nkjp/1grams.gz (hash) ─ strumień, czyszczenie┘    (tylko STANDARD)
        └─> ranga / percentyl ─> progi ─> pop.txt ⊇ pop0.txt
                                       └─> raporty, próbki, release-manifest POP (atrybucja NKJP)
```

Poziom form: `orth_lc` / `orth` (all + gatunki) po `game_key`.
Poziom leksemów: `evidence_candidate.lexeme_id` → `interpretation` → `surface_form.game_key` (EXACT i AMBIGUOUS, bez dzielenia F).

---

## Zależności

### Z czego POP korzysta

| Moduł | Po co |
|---|---|
| `canonical` | JSON kanoniczny, hash, zapis atomowy |
| `inputs` | `checked_file`, `GeneratorError` |
| `database` | połączenie ro, `game_key()` |
| `run` | `code_identity`, `create_run` |
| `export` | `rename_noreplace`, `changes_since_verify` |
| `quality` | `sample_strata` (z nową konfiguracją) |
| `decisions` | `nonfiction_frequencies` (opcjonalnie) |
| `kwjp` | `METRICS` |

### Kto zależy od POP

Nikt w repo. Przyszli odbiorcy: boty i ewentualny słownik gry w `Literaki-server`.

**Liczba odbiorców**: 0 w repo.
**Zasięg wpływu**: niski dla LL-PL (nic się nie zmienia), średni na przyszłość (POP może sterować grą).

---

## Testy

| Plik | Co daje POP |
|---|---|
| `tests/helpers.py` | `fixture_manifest`, `rewrite`. Twardo: NKJP `unavailable` BLOCKED. |
| `tests/release_helpers.py` | fikstura SGJP (kot, kotek, zamek:a/b), `complete_run`, `complete_pair`, `make_review`, `tree_hashes`. |
| `tests/test_kwjp.py` | helper `source()` pisze gz CSV. Ten sam wzór dla małego `1grams.gz`. |
| `tests/test_explain.py:22,36` | wzór: hash bazy bez zmian po kroku ro. |
| `tests/test_export.py`, `tests/test_verify.py` | wzór zamrożenia. |
| `tests/test_links.py` | homonimia, wielkość liter, NFC, POS, brak vs zero. |
| `tests/test_cli.py` | CLI przez subprocess, status JSON. |
| `tests/test_quality.py` | wzór testu determinizmu. |

Testy oczekujące NKJP w `unavailable`: `test_build.py:71`, `test_explain.py:399`, `test_links.py:88,100,192`, `test_export.py:67`. Zostają.

Polecenie: `python3 -m unittest discover -s tests -p 'test_*.py'`.

**Luki**: brak testów popularności (kodu też brak). Do napisania: POP0 ⊆ POP ⊆ STANDARD, dwa przebiegi równe, przebieg bazowy niezmieniony, brak ≠ 0, czyszczenie NKJP, homonimy bez kopiowania F.

---

## Wzorce kodu

| Obszar | Konwencja |
|---|---|
| Docstringi | po polsku; zakres i czego kod nie robi |
| Błędy | `GeneratorError`; kody 2 argumenty/konfiguracja, 3 źródło/hash, 4 integralność/IO/katalog istnieje, 5 gotowość, 130 przerwanie |
| CLI | subparser, pomoc po polsku, `--run-dir`/`--output-dir`/`--json`, leniwy import, `_finish` |
| Listy | posortowane `game_key`, UTF-8, każda linia z `\n`; nazwy `pop.txt`, `pop0.txt` |
| Raporty | kebab-case `.json`, `write_json`, `schema_version`, `scope`, sha256 wejść, `code_identity` |
| Konfiguracja | przypięta, z wersją, ścisły walidator |
| Rangi | deterministyczne: klucz `(-freq, key)` |
| Hashowana treść | bez czasów i ścieżek |
| Styl | funkcyjny, moduły bez klas, SQLite + Python |

**Antywzorce do uniknięcia**: zapytanie na słowo; złączenie bez kierunku (bez `CROSS JOIN`); duże sortowanie w temp SQLite; `json.loads` na wiersz; zapis do zamrożonego przebiegu; niekanoniczny JSON; brak jako zero; cicha zmiana konfiguracji próbek. Słabe punkty `benchmark_sjp.py`: własny sha256, `indent=1` nieatomowo, czas w hashowanym wyniku, `SystemExit`.

---

## Ocena złożoności

| Czynnik | Wartość | Poziom |
|---|---|---|
| Pliki | 1 nowy moduł + CLI + manifest + konfiguracja + testy (~5–7) | Średni |
| Zależności | 8 modułów wewnętrznych | Średni |
| Odbiorcy | 0 w repo | Niski |
| Testy | wzorce gotowe, testów POP brak | Średni |

### Ogólnie: umiarkowana

Kod jest prosty. Trudność leży w metodzie (miara, homonimy, czyszczenie NKJP, progi) i w rygorze (determinizm, pieczęć, atrybucja).

---

## Wnioski

### Mocne strony
- KWJP jest już powiązany z leksemami i formami, ze statusami dopasowania.
- Gotowe narzędzia: kanoniczny JSON, zapis atomowy, zamrożenie, próbki deterministyczne.
- Dostęp ro do zamrożonego przebiegu już działa (`explain`).
- Audyty KWJP i NKJP są zrobione; liczby są znane.

### Obawy
- Sprzeczność w regule czyszczenia NKJP (Q4).
- Homonimy: 12 453 lematów KWJP bez rozstrzygnięcia.
- Segmentacja KWJP zaniża formy z aglutynantem.
- Brak danych potocznych.
- Dryf manifestu: bieżący `sources.json` ≠ wejście przebiegu.

### Szanse
- `nonfiction_frequencies` i `word_availability` do ponownego użycia.
- `sample_strata` pasuje do próbek granicznych (`pop:boundary_in`, `pop:boundary_out`, `pop0:zero_freq`).
- Całość liczy się w minutach.

---

## Wpływ

- **Nowe pliki**: `literaki_slownik/pop.py`, `config/generator/pop-sources.json`, konfiguracja progów i próbek POP, `tests/test_pop.py`.
- **Zmiany**: `literaki_slownik/cli.py` (podkomenda `pop`), `ATTRIBUTIONS.md` (jeśli trzeba), dokumentacja, wiki.
- **Bez zmian**: `sources.json`, `inputs.py`, `build.py`, testy LL-PL, zamrożony przebieg.

### Ryzyko: nisko-średnie

LL-PL zostaje nietknięte, więc ryzyko regresji jest niskie. Ryzyko merytoryczne jest średnie: złe decyzje o mierze i progach dają słowniki, które boty i gra mogą użyć źle.

---

## Rekomendacje

Nowa funkcja (brak implementacji).

1. **Najpierw pomiary, potem decyzje.** Skrypt pomiarowy ro (wzór `benchmark_sjp.py`) dla właściciela:
   - liczba leksemów i form STANDARD przy progach 5k/10k/20k/40k/80k (KWJP lemma, orth_lc, NKJP);
   - pokrycie: ile słów STANDARD ma dane w każdym źródle;
   - zgodność rang KWJP i NKJP;
   - wpływ czyszczenia NKJP: pełny NFC vs usunięta interpunkcja;
   - próbki przy progach (stały seed).
2. **Decyzje właściciela Q1–Q7.** Zapisać jako ADR, odwracalne (reguła: decyzje słownikowe są delegowane, ale z dowodami).
3. **Implementacja** po decyzjach:
   - manifest POP z pinami bazy (`release_manifest_sha256`, `database_sha256`, sha STANDARD), artefakt NKJP (`kind: nkjp_1gram`, sha 73af4909…3dc9), progi, warunki wydania, atrybucje;
   - KWJP: zapytanie strumieniowe na `source_id`; NKJP: strumień gz, NFC, małe litery, wersjonowana reguła czyszczenia, agregacja po `game_key`, tylko STANDARD;
   - rangi i percentyle, nie sumy surowych liczb; wagi uzasadnione; analiza wrażliwości;
   - asercje: POP0 ⊆ POP ⊆ STANDARD; brak ≠ 0;
   - zamrożenie jak `export.py`; `release-manifest` POP wskazuje LL-PL v29; atrybucja NKJP; bez surowego NKJP w paczce;
   - test: dwa przebiegi dają te same bajty; hash bazy bez zmian.
4. **Zakazy**: bez Jasnopisu, Logiosu, Zgółkowej, Kurzowej, PSONI, SJP.pl, OSPS, PoliMorfu, Wikisłownika; bez strojenia pod SJP.pl; bez mapowania poziomów botów na wiek lub wykształcenie; bez twierdzeń o „przeciętnym człowieku” bez przejrzanej próbki.
5. **Dokumentacja**: strony wiki o słownikach popularnych; poprawka nieaktualnych „NKJP BLOCKED” tylko tam, gdzie dotyczy POP.

---

## Następne kroki

Uruchomić gap-analyzer. Wejście: ten raport i pytania Q1–Q7. Zaplanować pomiary z punktu 1 przed specyfikacją.
