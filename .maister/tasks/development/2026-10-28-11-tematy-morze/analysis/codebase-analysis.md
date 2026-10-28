# Raport analizy kodu

**Data**: 2026-10-28
**Zadanie**: #11 — pilotaż słownika tematycznego „morze” (pakiet TEMATY)
**Opis**: nowa wsadowa, deterministyczna podkomenda generatora według wzoru POP00 (#10); warstwy T1 (etykiety SGJP), T2 (Słowosieć 4.5), T3 (IATE TBX 2019, dziedzina 4821); plik konfiguracji tematu; raport przecięć z POP/POP00 (leksemy i formy, na warstwę); diagnostyka kandydatów wobec BROAD/STANDARD z przykładami odrzuconych; surowe pobrania poza Git z przypiętym SHA-256; kontrola pokrycia T2 i tego, czy IATE 4821 wciąga żeglugę śródlądową.
**Analizator**: codebase-analyzer (3 agenty Explore: File Discovery, Code Analysis, Pattern Mining)

---

## TL;DR

- TEMATY to nowa funkcja, ale wzór już jest: POP00 (`pop00.py`, 416 linii) plus podkomenda w `cli.py`, checker w `scripts/`, ADR, testy unittest.
- Słowosieć 4.5 leży już lokalnie (`data/work/plwordnet/`, SHA-256 znany). IATE nie ma nigdzie, trzeba je pobrać.
- W SGJP nie ma etykiety `mar.`. Morze to `mors.`, `żegl.`, `ryb.` i ich złożenia. Research: 254 leksemy, 246 w STANDARD v31.
- Brak API „leksemy po etykiecie”: T1 to nowy pełny skan `interpretation` (~7,46 mln wierszy) z cache po `(tag, names, qualifiers)`.
- Złożoność: umiarkowana. Ryzyko: średnie, głównie przez nowe źródła (licencje, pobranie, pokrycie T2/T3), nie przez kod.

## Kluczowe decyzje

- Nowy moduł `literaki_slownik/tematy.py` i podkomenda `tematy` na wzór `pop00` — POP00 to najbliższy, sprawdzony wzorzec (manifest + config + nowy katalog wyjściowy + koperta `--json`).
- Osobny manifest źródeł `config/generator/tematy-sources.json` w stylu `pop00-sources.json` (ścieżka + SHA-256), nie rozszerzanie `sources.json` — `KINDS` w `inputs.py` jest zamknięte (sgjp/kwjp).
- Pobieranie to osobny krok (`curl -fL` + SHA-256, wzór `scripts/audit_kwjp.py --fetch`). Budowanie nie używa sieci.
- Tożsamość leksemu `lemma_id@source_id`; T2/T3 mapują lemat na leksem przez `lexeme.lemma_base`. Nie używać `.bin` z morph-index (brak id leksemów).
- Etykiety T1 dzielić najpierw po `|`, potem po `,` — dokładnie tak, jak robi to `pop.load_lexemes` (`names` po `|`, `qualifiers` po `,`); porównywać całe etykiety (np. `mors.`), nie podciągi.
- Konfiguracja tematu walidowana przez zbiór kluczy i typy, z odrzuceniem nieznanych pól. Nie powielać sztywnego słownika z `pop00.load_config` — nie skaluje się na ~10 tematów.
- Następny ADR projektu to ADR-010. Lokalne numery ADR z researchu (001–010) kolidują, trzeba je przemapować.

## Otwarte pytania / ryzyka

- Ścieżka plików tematów: `config/generator/tematy/<temat>.json` czy jeden plik. Nowa konwencja, do decyzji.
- Lista etykiet T1: pewne `mors.`, `mors.,wojsk.`, `mors.,żegl.`, `żegl.`, `ryb.`, `ryb.,techn.`. Wątpliwe `geogr.` (163), `meteor.` (737) — raczej poza „morzem”, ale to decyzja zakresu.
- `ryb.` (516 interpretacji) obejmuje też rybactwo śródlądowe. Ten sam problem co przy IATE 4821 i żegludze śródlądowej.
- Pokrycie T2: domknięcie po relacjach 11, 25, 27 z wykluczeniami poddrzew jeszcze niezmierzone; ryzyko dryfu w ogólne słownictwo.
- IATE: adres pobrania, licencja i rozmiar TBX 2019 niesprawdzone na dysku. Trzeba zmierzyć udział terminów śródlądowych w 4821.
- Licencja Słowosieci: tabeli właściciela i logu IP nie wolno kopiować. Pochodna SQLite musi je pomijać.
- Błąd z POP00 (f33fe05): `confirm_unchanged` musi ponownie hashować każdy przeczytany plik, także pliki w pakietach POP/POP00.
- Koszt: dwukrotne SHA-256 bazy `build.sqlite` (22 GB) dominuje czas. Spodziewane minuty, nie sekundy.
- Repo rośnie od 9-tysięcznych JSON-ów przeglądu commitowanych dwa razy w POP00. Dla TEMATY trzymać je poza Git lub raz.

---

## Podsumowanie

Pakiet to czysta biblioteka standardowa Pythona (~9,4 tys. linii), testy w `unittest`. POP00 dał gotowy szkielet: weryfikacja wejść po SHA-256, odczyt SQLite tylko do odczytu, deterministyczny zapis pakietu, niezależny checker, dwa identyczne buildy a/b. TEMATY dokłada trzy nowe źródła i raport przecięć, ale nie zmienia istniejących ścieżek.

---

## Pliki

### Główne

**literaki_slownik/pop00.py** (416 linii)
- Wzorzec całej podkomendy: `load_config`, `load_sources`, `check_inputs`, `read_words`, `read_analyses`, `_write_package`, `confirm_unchanged`, `build_package`, `explain_pop00`.
- Do skopiowania struktury; część funkcji do wydzielenia jako wspólne.

**literaki_slownik/cli.py** (160 linii)
- Rejestracja podkomend w `main()` (13–105), parser POP00 51–55, dispatch 93–95, `_finish` ~142, `explain --variant` 28–33, 63–67.
- Tu dochodzi `tematy` (i ewentualnie wariant w `explain`).

**literaki_slownik/pop.py** (2033 linii)
- `load_lexemes` (162, podział etykiet 170–180), `load_forms` (287), `load_constructions` (315), `_label` (1762), `_write_gzip` (1767), `_attributions`/`_terms` (1828, 1926).
- Źródło form STANDARD i tożsamości leksemu. `_write_gzip` jest prywatne — upublicznić.

**literaki_slownik/inputs.py** (107 linii)
- `checked_file`, `inspect_sources`; `GeneratorError(msg, code)`.

**config/generator/pop00.json** (11), **pop00-sources.json** (26)
- Wzór dla `tematy.json`, `tematy-sources.json` i pliku tematu.

**scripts/check_pop00_package.py** (319 linii)
- Wzór niezależnego checkera (`Refused(code)`, `require`, `digest`, `--review`); nie importuje pakietu.

### Powiązane

- **literaki_slownik/canonical.py** (44): `dumps`, `load_json` (odrzuca duplikaty kluczy i NaN), strumieniowe `sha256`, atomowe `write_json`.
- **literaki_slownik/quality.py**: `sample_strata` (41), `review_template` (84), `SEEDS` — dopisać `tematy-quality-v1`.
- **literaki_slownik/run.py**: `code_identity()` (16).
- **literaki_slownik/export.py**: `rename_noreplace` (33).
- **literaki_slownik/sgjp.py** (60), **schema.sql** (81): kolumna `interpretation.qualifiers` (tekst dosłowny).
- **literaki_slownik/policy.py** (1193): `descriptive_checks` (797) — porównania całych etykiet.
- **config/generator/qualifiers.json** (3170): dosłowne etykiety; separator `|` (3119).
- **config/generator/evidence.json** (130), **sources.json** (861): model pochodzenia źródła (pola wymagane).
- **scripts/audit_kwjp.py** (~136–180): wzór pobierania przez `curl` w podprocesie.
- **docs/adr/ADR-009-pop00-v1.md** (46): format ADR.
- **docs/generator/**: `cli.md` (205), `raporty.md` (83), `jakosc.md` (57), `etykiety.md` (94), `publikacja.md` (77); `docs/runbook-wiki.md` (72); `ATTRIBUTIONS.md`.

### Dane (poza Git)

- BROAD/STANDARD: `data/work/lists-v31-20261012-162111-a/` (`lists/broad.txt`, `lists/standard.txt`, `build.sqlite`, `manifest.json`).
- POP/POP0: `data/work/pop-v3-20261014-022011-a/` (`POP.txt.gz`, `POP0.txt.gz`, `reports/units.json`).
- POP00: `data/work/pop00-v1-20261021-r2-a/` i `-b` (`POP00.txt.gz`, `release-manifest.json`).
- Słowosieć: `data/work/plwordnet/wordnet_work_4_5.zip` (465 563 957 B, sha256 `30edc5f85c06408d372a897f1d1ff3d03fa939b8680b176c1f97351f4a72dcbc`), `plwn45.sqlite` (pochodna).
- SGJP surowy: `cache/sgjp/sgjp-20260823.tab.gz`.
- IATE: brak. Docelowo `cache/iate/`; Słowosieć docelowo `cache/plwordnet/`.

---

## Obecne działanie

### Przepływ POP00 (wzór)

1. `load_sources` czyta manifest wejść i odrzuca nieznane klucze.
2. `check_inputs` (145–181) hashuje każde wejście, wymaga stanu `FROZEN`, sprawdza manifest POP (kind, method, package_id, status) i hashe bazy oraz STANDARD.
3. `read_words` (107): lista kanoniczna (posortowana, unikalna, NFC, małe litery, długość 2–15).
4. `read_analyses` (184–207): SQLite tylko do odczytu, klucz `lemma_id@source_id`, zapytania porcjami po 400.
5. `_write_package` (288–328): `.txt.gz`, `method.json`, `reports/*.json`, `ATTRIBUTIONS/TERMS/LIMITATIONS`, `release-manifest.json`, `SHA256SUMS`.
6. `build_package` (337–376): staging w `mkdtemp` obok celu, `chmod 0444`, `rename_noreplace`; `confirm_unchanged` (331) na końcu.

### Determinizm

Wszystko sortowane; `canonical.dumps`; gzip z `mtime=0`, bez nazwy, poziom 9; próbki seedowane hashem; `code_identity()` w manifeście. Dwa buildy a/b dają identyczne hashe.

### Konwencje CLI

`--manifest` (przypięcia) i `--config` (metoda) wymagane; `--output-dir` nowy, rodzic istnieje, bez nadpisywania; koperta `--json` `{schema_version:1, command, status, diagnostics, result}`; komunikaty po polsku. Kody wyjścia: 2 argumenty/konfiguracja, 3 przypięcia/brak pliku, 4 dane/nadpisanie, 5 stan.

### Etykiety SGJP

Morze: `mors.` (1619 interpretacji), `mors.,wojsk.` (22), `mors.,żegl.` (56), `żegl.`, `ryb.` (516), `ryb.,techn.`. Pola przechowywane w całości; przecinek bywa częścią etykiety.

---

## Zależności

### Od czego zależy TEMATY

- `build.sqlite` (v31): leksemy, interpretacje, formy.
- `lists/broad.txt`, `lists/standard.txt`: diagnostyka kandydatów.
- Pakiety POP/POP0/POP00: przecięcia (leksemy przez `units.json`, formy przez `.txt.gz`).
- Słowosieć 4.5 (SQLite pochodna), IATE TBX 2019.
- `canonical`, `inputs`, `quality`, `run`, `export`, `pop`.

### Kto zależy

Nikt — nowa funkcja. Dotykane wspólne miejsca: `cli.py` (rejestracja), `quality.SEEDS`, ewentualnie upublicznienie `pop._write_gzip`, `tests/test_documented_names.py` (nazwy w dokumentacji).

**Liczba konsumentów**: 0 nowych; ~3 wspólne punkty styku.
**Zasięg wpływu**: niski.

---

## Testy

### Pliki

- `tests/test_pop00.py` (53), `test_pop00_package.py` (75), `test_check_pop00_package.py` (70), `test_explain_pop00.py` (34), `pop00_helpers.py` (85) — wzór dla `test_tematy*.py` i `tematy_helpers.py`.
- `tests/test_cli.py`, `test_documented_names.py`, `helpers.py`, `pop_helpers.py`, `release_helpers.py`.

Uruchomienie: `python3 -m unittest discover -s tests -p 'test_*.py'` oraz `python3 -m unittest discover -s scripts -p 'test_audit_sgjp.py'`.

### Ocena

- Wzorzec testów POP00 dobry: małe bazy w helperach, test pakietu, test checkera, test `explain`.
- Luki do pokrycia w TEMATY: podział etykiet `|`/`,`, mapowanie lematu na wiele leksemów (homonimy), nieznane pola konfiguracji tematu, zmiana pliku w trakcie budowy (re-hash pakietów wejściowych), parser TBX, domknięcie Słowosieci.

---

## Wzorce kodu

- **Pliki**: `literaki_slownik/<nazwa>.py`, `config/generator/<nazwa>.json` + `<nazwa>-sources.json`, `scripts/check_<nazwa>_package.py`.
- **Wersje**: `tematy-v1`, `tematy-sources-v1`, `tematy-quality-v1`, seed `literaki-slownik-tematy-v1`.
- **Styl**: funkcje modułowe, bez klas; leniwy import w dispatchu CLI; polskie komunikaty.
- **Commity**: `feat(tematy): … (#11)`.
- **Wiki**: strona `Slownik-TEMATY` w „Strony”, na start „W przygotowaniu”, Home, `_Sidebar`; liczby z manifestu; commit `wiki: … (vNN)`.

---

## Ocena złożoności

| Czynnik | Wartość | Poziom |
|--------|-------|-------|
| Pliki | ~12–15 nowych lub zmienionych (moduł, CLI, 3 configi, checker, 4–5 testów, ADR, docs) | Wysoki |
| Zależności | ~7 modułów pakietu + 3 nowe źródła | Średni |
| Konsumenci | 0 nowych | Niski |
| Testy | wzorzec dobry, nowe testy od zera | Średni |

### Ogółem: umiarkowana

Kod powtarza znany wzór. Trudność leży w danych: parsowanie TBX, domknięcie Słowosieci, mapowanie lematów na leksemy, decyzje zakresu tematu.

---

## Kluczowe ustalenia

### Mocne strony
- Gotowy, przetestowany szkielet POP00 i niezależny checker.
- Słowosieć 4.5 już pobrana i przypięta.
- Dojrzały model pochodzenia źródła (`sources.json`, `evidence.json`).

### Obawy
- Brak IATE na dysku i brak sprawdzonej licencji/URL.
- Sztywna walidacja konfiguracji w POP00 nie nadaje się do skalowania.
- Prywatny import `_write_gzip` między modułami.
- Stałe w kodzie (próg ipm, teksty TERMS/LIMITATIONS inline).
- Data pobrania brana z `mtime` — zawodna.

### Szanse
- Wydzielić wspólne kroki pakowania (staging, SHA256SUMS, manifest) zamiast trzeciej kopii.
- Plik tematu jako dane — kolejne tematy bez zmian kodu.

---

## Ocena wpływu

- **Zmiany główne**: nowy `literaki_slownik/tematy.py`; `cli.py`; `config/generator/tematy.json`, `tematy-sources.json`, plik(i) tematu; `scripts/check_tematy_package.py`; skrypt pobrania.
- **Zmiany powiązane**: `quality.SEEDS`, `pop._write_gzip` (upublicznienie), `ATTRIBUTIONS.md`, `docs/adr/ADR-010-*.md`, `docs/generator/cli.md`, `raporty.md`, `jakosc.md`, `etykiety.md`.
- **Testy**: nowe `tests/test_tematy*.py`, `tematy_helpers.py`; `test_documented_names.py` może wymagać aktualizacji.

### Ryzyko: średnie

Kod izolowany, brak konsumentów. Ryzyko wynika z nowych źródeł: licencje (Słowosieć, IATE), poprawność pobrania, jakość T2/T3 (dryf, żegluga śródlądowa), oraz z błędu re-hashowania znanego z POP00.

---

## Rekomendacje

1. **Pobranie najpierw.** Skrypt w `scripts/` pobiera IATE TBX do pliku tymczasowego, liczy SHA-256, zmienia nazwę i zapisuje URL, czas UTC, rozmiar i hash do manifestu źródeł. Słowosieć tylko przypiąć (hash już znany). Surowe pliki w `cache/iate/`, `cache/plwordnet/`.
2. **Pochodna Słowosieci bez danych osobowych.** SQLite dla buildu bez tabeli właściciela i logu IP; hash pochodnej przypięty osobno.
3. **Moduł `tematy.py`.**
   - `load_config`: walidacja kluczy i typów, odrzucenie nieznanych.
   - `check_inputs`: jak POP00 + pakiet POP00 (`pop00-v1-20261021-r2-a/release-manifest.json`), Słowosieć, IATE, plik tematu.
   - T1: jeden skan `interpretation`, cache po `(tag, names, qualifiers)`, dopasowanie całych etykiet z pliku tematu.
   - T2: synsety-zarodki z pliku tematu, domknięcie po relacjach 11, 25, 27, wykluczenia poddrzew; lemat → `lexeme.lemma_base`.
   - T3: jednowyrazowe polskie terminy IATE z dziedziny 4821; lemat → leksem.
   - Warstwa leksemu = najniższa z T1<T2<T3; flaga `wieloznaczny` przy wielu leksemach na lemat.
   - Diagnostyka przed przecięciem ze STANDARD: kody `BRAK_LEKSEMU`, `POZA_BROAD`, `POZA_STANDARD`, z przykładami (deterministyczny wybór).
   - Przecięcia z POP/POP0 (leksemy, `units.json`) i POP/POP00 (formy, `.txt.gz`), osobno na warstwę.
   - `confirm_unchanged` hashuje każdy przeczytany plik, także w pakietach wejściowych.
4. **Pakiet.** `<ID>.tsv.gz`, `<ID>.txt.gz`, `tematy/<id>.json`, `method.json`, `reports/summary.json`, `ATTRIBUTIONS` (SGJP + plWordNet + IATE), `TERMS`, `LIMITATIONS`, `release-manifest.json`, `SHA256SUMS`. Teksty licencyjne z plików, nie z kodu.
5. **Kontrole jakości dla pilotażu.** Zmierzyć pokrycie T2 (ile leksemów T1 łapie T2 i odwrotnie) i udział terminów śródlądowych w IATE 4821; wynik w raporcie i w ADR-010.
6. **Testy i checker.** Testy na małych bazach jak w POP00; `scripts/check_tematy_package.py` bez importu pakietu; akceptacja: dwa czyste, identyczne buildy a/b, checker PASS, pełny przegląd próbki.
7. **Bez sieci w buildzie.** Pobranie i build to osobne kroki.

---

## Następne kroki

Uruchomić gap-analyzer: porównać ten stan z wymaganiami #11 i rozstrzygnąć otwarte decyzje zakresu (lista etykiet T1, wykluczenia T2, filtr śródlądowy dla T3, ścieżka plików tematu) przed specyfikacją.
